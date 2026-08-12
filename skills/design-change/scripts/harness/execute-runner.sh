#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=artifact-dag.sh
source "$SCRIPT_DIR/artifact-dag.sh"
# shellcheck source=design-runner.sh
source "$SCRIPT_DIR/design-runner.sh"
# shellcheck source=plan-runner.sh
source "$SCRIPT_DIR/plan-runner.sh"
# shellcheck source=evaluation-gate.sh
source "$SCRIPT_DIR/evaluation-gate.sh"
# shellcheck source=recovery-routing.sh
source "$SCRIPT_DIR/recovery-routing.sh"
# shellcheck source=task-ledger.sh
source "$SCRIPT_DIR/task-ledger.sh"
# shellcheck source=phase-engine.sh
source "$SCRIPT_DIR/phase-engine.sh"

execute_entry_phase() {
  next_phase_for_entry "implement-change"
}

execution_plan_approval_status() {
  plan_approval_status "$1"
}

validate_execution_plan() {
  local plan_file="$1"
  local approval_status=""

  validate_execution_grade_plan_artifact "$plan_file" || return 1
  approval_status="$(execution_plan_approval_status "$plan_file")"

  [[ "$approval_status" == "approved" ]] || {
    printf 'plan artifact is not approved for execution: %s\n' "$approval_status" >&2
    return 1
  }
}

execution_plan_mode() {
  local plan_file="$1"

  [[ -f "$plan_file" ]] || {
    printf 'missing plan file: %s\n' "$plan_file" >&2
    return 1
  }

  if rg -n 'parallel_execution_approved:[[:space:]]*true' "$plan_file" >/dev/null; then
    printf 'parallel-approved\n'
    return
  fi

  printf 'serial-first\n'
}

execution_workspace_mode() {
  local repo_root=""
  local git_dir=""
  local common_dir=""
  local resolved_git_dir=""
  local resolved_common_dir=""

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  git_dir="$(git -C "$repo_root" rev-parse --git-dir 2>/dev/null || true)"
  common_dir="$(git -C "$repo_root" rev-parse --git-common-dir 2>/dev/null || true)"

  if [[ "$repo_root" == */.agents/worktrees/* ]]; then
    printf 'isolated-worktree\n'
    return
  fi

  if [[ -n "$git_dir" && -n "$common_dir" ]]; then
    if [[ "$git_dir" = /* ]]; then
      resolved_git_dir="$(realpath "$git_dir" 2>/dev/null || printf '%s' "$git_dir")"
    else
      resolved_git_dir="$(realpath "$repo_root/$git_dir" 2>/dev/null || printf '%s' "$git_dir")"
    fi
    if [[ "$common_dir" = /* ]]; then
      resolved_common_dir="$(realpath "$common_dir" 2>/dev/null || printf '%s' "$common_dir")"
    else
      resolved_common_dir="$(realpath "$repo_root/$common_dir" 2>/dev/null || printf '%s' "$common_dir")"
    fi
    if [[ "$resolved_git_dir" != "$resolved_common_dir" ]]; then
      printf 'isolated-worktree\n'
      return
    fi
  fi

  printf 'current-checkout\n'
}

execution_worktree_preflight_required() {
  local workspace_mode="$1"
  local decision_recorded="$2"

  is_valid_boolean_flag "$decision_recorded" || {
    printf 'invalid worktree decision flag: %s\n' "$decision_recorded" >&2
    return 1
  }

  case "$workspace_mode" in
    isolated-worktree) printf 'false\n' ;;
    current-checkout)
      if [[ "$decision_recorded" == "true" ]]; then
        printf 'false\n'
      else
        printf 'true\n'
      fi
      ;;
    *)
      printf 'invalid workspace mode: %s\n' "$workspace_mode" >&2
      return 1
      ;;
  esac
}

strip_wrapping_backticks() {
  sed -E 's/^`(.*)`$/\1/'
}

execution_verification_commands() {
  local plan_file="$1"

  validate_execution_plan "$plan_file" >/dev/null || return 1
  extract_markdown_list "$plan_file" "Implementation Scope" "verification_scope" \
    | awk 'NF > 0' \
    | strip_wrapping_backticks
}

resolve_execution_design_file() {
  local plan_file="$1"
  local repo_root=""
  local -a resolved=()

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  mapfile -t resolved < <(resolve_plan_design_ref "$repo_root" "$plan_file")
  [[ "${#resolved[@]}" -ge 1 ]] || return 1
  printf '%s\n' "${resolved[0]}"
}

execution_allowed_touch_set() {
  local plan_file="$1"
  local design_file=""

  validate_execution_plan "$plan_file" >/dev/null
  design_file="$(resolve_execution_design_file "$plan_file")"
  build_allowed_touch_set "$plan_file" "$design_file"
}

execution_truth_sync_required() {
  local plan_file="$1"
  local design_file=""
  local truth_impact=""

  validate_execution_plan "$plan_file" >/dev/null
  design_file="$(resolve_execution_design_file "$plan_file")"
  truth_impact="$(rg -o 'truth_impact:[[:space:]]*(low|medium|high)' "$design_file" | head -n 1 | sed -E 's/^truth_impact:[[:space:]]*//')"

  case "$truth_impact" in
    medium|high) printf 'true\n' ;;
    low) printf 'false\n' ;;
    *)
      printf 'missing or invalid truth_impact in design: %s\n' "$design_file" >&2
      return 1
      ;;
  esac
}

execution_task_catalog() {
  local plan_file="$1"

  validate_execution_plan "$plan_file" >/dev/null
  task_catalog_json "$plan_file"
}

execution_task_ledger() {
  local plan_file="$1"

  validate_execution_plan "$plan_file" >/dev/null
  task_ledger_json "$plan_file"
}

execution_next_ready_task() {
  local ledger_file="$1"
  task_ledger_next_ready_task_id "$ledger_file"
}

execution_ready_set() {
  local ledger_file="$1"
  task_ledger_ready_set_json "$ledger_file"
}

execution_batch_conflicts_json() {
  local ledger_file="$1"
  local group_id="$2"

  jq --arg group_id "$group_id" '
    def write_refs:
      ((.impl_file_refs // []) + (.test_file_refs // []))
      | map(select(. != "" and . != "none"));
    def refs_overlap($left; $right):
      ($left == $right) or
      ($left | startswith($right + "/")) or
      ($right | startswith($left + "/"));

    [.[] | select(.parallel_group == $group_id and .status != "done")] as $frontier
    | (
        [
            $frontier[]
            | select((write_refs | length) > 0 and .isolation != "isolated-worktree")
            | {
                kind: "isolation",
                task_id: .task_id,
                isolation: .isolation,
                requirement: "isolated-worktree"
              }
          ]
        + [
            range(0; $frontier | length) as $left_index
            | range($left_index + 1; $frontier | length) as $right_index
            | $frontier[$left_index] as $left
            | $frontier[$right_index] as $right
            | select(
                (($left.depends_on // []) | index($right.task_id)) != null or
                (($right.depends_on // []) | index($left.task_id)) != null
              )
            | {
                kind: "dependency",
                task_ids: [$left.task_id, $right.task_id]
              }
          ]
        + [
            range(0; $frontier | length) as $left_index
            | range($left_index + 1; $frontier | length) as $right_index
            | $frontier[$left_index] as $left
            | $frontier[$right_index] as $right
            | ($left | write_refs[]) as $left_ref
            | ($right | write_refs[]) as $right_ref
            | select(refs_overlap($left_ref; $right_ref))
            | {
                kind: "write-ref",
                task_ids: [$left.task_id, $right.task_id],
                left_ref: $left_ref,
                right_ref: $right_ref
              }
          ]
        + [
            range(0; $frontier | length) as $left_index
            | range($left_index + 1; $frontier | length) as $right_index
            | $frontier[$left_index] as $left
            | $frontier[$right_index] as $right
            | ($left.resource_locks // [])[] as $left_lock
            | ($right.resource_locks // [])[] as $right_lock
            | select($left_lock != "none" and $left_lock == $right_lock)
            | {
                kind: "resource-lock",
                task_ids: [$left.task_id, $right.task_id],
                resource_lock: $left_lock
              }
          ]
      )
  ' "$ledger_file"
}

execution_runtime_binding_from_validated_plan() {
  local plan_file="$1"
  local ledger_file="$2"
  local group_id="$3"
  local runtime_capacity="$4"
  local requested_model_policy="${5:-}"
  local default_model_policy=""
  local allowed_model_policy=""
  local plan_max_parallelism=""
  local group_task_count=""
  local frontier_count=""
  local non_ready_frontier_count=""
  local group_parallel_policy=""
  local actor_capacity=0
  local effective_width=0
  local binding_outcome=""
  local stop_reason_value=""
  local conflicts_json="[]"
  local binding_evidence_json="[]"
  local serial_fallback_reason_value=""
  local saw_requested_policy=false

  plan_uses_v2_contract "$plan_file" || {
    printf 'runtime binding requires a version-2 plan contract\n' >&2
    return 1
  }
  [[ "$runtime_capacity" =~ ^[1-9][0-9]*$ ]] || {
    printf 'runtime capacity must be a positive integer: %s\n' "$runtime_capacity" >&2
    return 1
  }
  plan_token_is_safe "$group_id" || {
    printf 'parallel group must be a portable token: %s\n' "$group_id" >&2
    return 1
  }

  default_model_policy="$(extract_markdown_scalar "$plan_file" "Runtime Binding" "default_model_policy" | normalize_plan_metadata_values)"
  if [[ -z "$requested_model_policy" ]]; then
    requested_model_policy="$default_model_policy"
  fi
  is_valid_model_policy "$requested_model_policy" || {
    printf 'invalid model policy: %s\n' "$requested_model_policy" >&2
    return 1
  }
  while IFS= read -r allowed_model_policy; do
    allowed_model_policy="$(printf '%s\n' "$allowed_model_policy" | normalize_plan_metadata_values)"
    if [[ "$allowed_model_policy" == "$requested_model_policy" ]]; then
      saw_requested_policy=true
      break
    fi
  done < <(extract_markdown_list "$plan_file" "Runtime Binding" "allowed_model_policies")
  [[ "$saw_requested_policy" == "true" ]] || {
    printf 'model policy is not allowed by the plan: %s\n' "$requested_model_policy" >&2
    return 1
  }

  plan_max_parallelism="$(parallel_batch_max_parallelism "$plan_file" "$group_id" | normalize_plan_metadata_values)"
  [[ "$plan_max_parallelism" =~ ^[0-9]+$ && "$plan_max_parallelism" -ge 2 ]] || {
    printf 'parallel group is not linked to a valid approved batch: %s\n' "$group_id" >&2
    return 1
  }
  group_task_count="$(jq --arg group_id "$group_id" '[.[] | select(.parallel_group == $group_id)] | length' "$ledger_file")"
  frontier_count="$(jq --arg group_id "$group_id" '[.[] | select(.parallel_group == $group_id and .status != "done")] | length' "$ledger_file")"
  non_ready_frontier_count="$(jq --arg group_id "$group_id" '[.[] | select(.parallel_group == $group_id and .status != "done" and .status != "ready")] | length' "$ledger_file")"
  group_parallel_policy="$(jq -r --arg group_id "$group_id" '[.[] | select(.parallel_group == $group_id) | .parallel_policy] | unique | if length == 1 then .[0] else "mixed" end' "$ledger_file")"
  actor_capacity="$(jq --arg group_id "$group_id" '
    def actor_kind:
      if .delegation_policy == "forbidden" then "main"
      elif .delegation_policy == "preferred" then "subagent"
      elif .executor_mode == "subagent" then "subagent"
      else "main"
      end;
    [.[] | select(.parallel_group == $group_id and .status == "ready")] as $ready
    | ([$ready[] | select(actor_kind == "subagent")] | length) +
      (if ([$ready[] | select(actor_kind == "main")] | length) > 0 then 1 else 0 end)
  ' "$ledger_file")"

  if [[ "$frontier_count" -eq 0 ]]; then
    printf 'parallel group has no remaining ready frontier: %s\n' "$group_id" >&2
    return 2
  fi
  if [[ "$non_ready_frontier_count" -gt 0 ]]; then
    printf 'parallel group is waiting for its complete ready frontier: %s\n' "$group_id" >&2
    return 2
  fi

  conflicts_json="$(execution_batch_conflicts_json "$ledger_file" "$group_id")"

  if [[ "$group_task_count" -lt 2 ]]; then
    conflicts_json="$(jq --arg group_id "$group_id" '. + [{kind: "group-membership", group_id: $group_id, requirement: "at-least-two-tasks"}]' <<<"$conflicts_json")"
  fi
  if [[ "$group_parallel_policy" != "allowed" && "$group_parallel_policy" != "required" ]]; then
    conflicts_json="$(jq --arg parallel_policy "$group_parallel_policy" '. + [{kind: "parallel-policy", parallel_policy: $parallel_policy}]' <<<"$conflicts_json")"
  fi
  if [[ "$(jq 'length' <<<"$conflicts_json")" -gt 0 ]]; then
    binding_outcome="parallel-conflict"
    binding_evidence_json="$conflicts_json"
  else
    effective_width="$frontier_count"
    if [[ "$effective_width" -gt "$plan_max_parallelism" ]]; then
      effective_width="$plan_max_parallelism"
    fi
    if [[ "$effective_width" -gt "$runtime_capacity" ]]; then
      effective_width="$runtime_capacity"
    fi
    if [[ "$effective_width" -gt "$actor_capacity" ]]; then
      effective_width="$actor_capacity"
    fi

    if [[ "$group_parallel_policy" == "required" && ( "$effective_width" -lt 2 || "$effective_width" -lt "$frontier_count" ) ]]; then
      binding_outcome="capacity-stop"
      stop_reason_value="parallel_capacity_required"
      binding_evidence_json="$(jq -n \
        --argjson runtime_capacity "$runtime_capacity" \
        --argjson plan_max_parallelism "$plan_max_parallelism" \
        --argjson ready_frontier_count "$frontier_count" \
        --argjson available_width "$effective_width" \
        --argjson actor_capacity "$actor_capacity" \
        '[{
          kind: "effective-capacity",
          runtime_capacity: $runtime_capacity,
          plan_max_parallelism: $plan_max_parallelism,
          ready_frontier_count: $ready_frontier_count,
          available_width: $available_width,
          actor_capacity: $actor_capacity
        }]')"
      effective_width=0
    elif [[ "$effective_width" -lt 2 ]]; then
      binding_outcome="serial-fallback"
      serial_fallback_reason_value="$(jq -r -n \
        --argjson ready_width "$frontier_count" \
        --argjson planned_width "$plan_max_parallelism" \
        --argjson runtime_capacity "$runtime_capacity" \
        --argjson actor_capacity "$actor_capacity" \
        '[
          (if $ready_width < 2 then "ready_frontier" else empty end),
          (if $planned_width < 2 then "batch_limit" else empty end),
          (if $runtime_capacity < 2 then "runtime_capacity" else empty end),
          (if $actor_capacity < 2 then "actor_capacity" else empty end)
        ] | join("+")')"
      [[ -n "$serial_fallback_reason_value" ]] || serial_fallback_reason_value="capacity"
      effective_width=1
      binding_evidence_json="$(jq -n \
        --argjson runtime_capacity "$runtime_capacity" \
        --argjson plan_max_parallelism "$plan_max_parallelism" \
        --argjson ready_frontier_count "$frontier_count" \
        --argjson actor_capacity "$actor_capacity" \
        '[{
          kind: "effective-capacity",
          runtime_capacity: $runtime_capacity,
          plan_max_parallelism: $plan_max_parallelism,
          ready_frontier_count: $ready_frontier_count,
          actor_capacity: $actor_capacity
        }]')"
    else
      binding_outcome="bound"
    fi
  fi

  jq \
    --arg group_id "$group_id" \
    --arg model_policy "$requested_model_policy" \
    --arg outcome "$binding_outcome" \
    --arg stop_reason "$stop_reason_value" \
    --argjson runtime_capacity "$runtime_capacity" \
    --argjson plan_max_parallelism "$plan_max_parallelism" \
    --argjson actor_capacity "$actor_capacity" \
    --argjson ready_width "$frontier_count" \
    --argjson effective_width "$effective_width" \
    --argjson binding_evidence "$binding_evidence_json" \
    --arg serial_fallback_reason "$serial_fallback_reason_value" \
    '
    def task_topology:
      {
        task_id,
        scope_slice,
        depends_on,
        parallel_group,
        parallel_policy,
        delegation_policy,
        execution_profile,
        reasoning_profile,
        isolation,
        resource_locks,
        impl_file_refs,
        test_file_refs,
        verification_commands,
        done_when,
        executor_mode
      };
    def actor_kind:
      if .delegation_policy == "forbidden" then "main"
      elif .delegation_policy == "preferred" then "subagent"
      elif .executor_mode == "subagent" then "subagent"
      else "main"
      end;
    def model_instruction:
      if $model_policy == "semantic-routing" then "bind-runtime-equivalent-for-execution-profile"
      elif $model_policy == "inherit-main" then "inherit-main-model"
      else "use-runtime-default-model"
      end;
    def reasoning_instruction:
      if $model_policy == "semantic-routing" then "bind-runtime-equivalent-for-reasoning-profile"
      elif $model_policy == "inherit-main" then "inherit-main-reasoning"
      else "use-runtime-default-reasoning"
      end;

    [.[] | select(.parallel_group == $group_id)] as $group_tasks
    | [$group_tasks[] | select(.status == "ready")] as $ready_frontier
    | (
        reduce $ready_frontier[] as $candidate (
          {tasks: [], main_count: 0};
          if (.tasks | length) >= $effective_width then
            .
          elif (($candidate | actor_kind) == "main" and .main_count >= 1) then
            .
          else
            .tasks += [$candidate]
            | if ($candidate | actor_kind) == "main" then .main_count += 1 else . end
          end
        )
        | .tasks
      ) as $selected
    | ([
        (if $ready_width < $plan_max_parallelism then "ready_frontier" else empty end),
        (if $plan_max_parallelism <= $ready_width and $plan_max_parallelism <= $runtime_capacity and $plan_max_parallelism <= $actor_capacity then "batch_limit" else empty end),
        (if $runtime_capacity <= $ready_width and $runtime_capacity <= $plan_max_parallelism and $runtime_capacity <= $actor_capacity then "runtime_capacity" else empty end),
        (if $actor_capacity <= $ready_width and $actor_capacity <= $plan_max_parallelism and $actor_capacity <= $runtime_capacity then "actor_capacity" else empty end)
      ]) as $limiting_factors
    | {
        outcome: $outcome,
        group_id: $group_id,
        batch_id: $group_id,
        approved_batch_id: $group_id,
        batch_identity: {
          batch_id: $group_id,
          parallel_group: $group_id,
          task_ids: [$group_tasks[] | .task_id],
          parallel_policy: ($group_tasks[0].parallel_policy // null)
        },
        model_policy: $model_policy,
        runtime_capacity: $runtime_capacity,
        actor_capacity: $actor_capacity,
        plan_max_parallelism: $plan_max_parallelism,
        planned_width: $plan_max_parallelism,
        ready_width: $ready_width,
        effective_width: $effective_width,
        stop_reason: (if $stop_reason == "" then null else $stop_reason end),
        serial_fallback_reason: (if $serial_fallback_reason == "" then null else $serial_fallback_reason end),
        limiting_factors: $limiting_factors,
        capacity_evidence: {
          batch_id: $group_id,
          planned_width: $plan_max_parallelism,
          plan_max_parallelism: $plan_max_parallelism,
          ready_width: $ready_width,
          runtime_capacity: $runtime_capacity,
          actor_capacity: $actor_capacity,
          effective_width: $effective_width,
          planned_task_ids: [$group_tasks[] | .task_id],
          ready_task_ids: [$ready_frontier[] | .task_id],
          ready_frontier_task_ids: [$ready_frontier[] | .task_id],
          selected_task_ids: [$selected[] | .task_id],
          limiting_factors: $limiting_factors,
          serial_fallback_reason: (if $serial_fallback_reason == "" then null else $serial_fallback_reason end)
        },
        failure_kind: (if $outcome == "parallel-conflict" then "parallel-conflict" else null end),
        recovery_phase: (if $outcome == "parallel-conflict" then "dependency-freeze" else null end),
        ready_frontier_task_ids: [$ready_frontier[] | .task_id],
        ready_task_ids: [$ready_frontier[] | .task_id],
        planned_task_ids: [$group_tasks[] | .task_id],
        selected_task_ids: [$selected[] | .task_id],
        task_topology: [$group_tasks[] | task_topology],
        bindings: [
          $selected[]
          | {
              task_id: .task_id,
              actor_kind: actor_kind,
              model_policy: $model_policy,
              model_instruction: model_instruction,
              execution_profile: .execution_profile,
              reasoning_profile: .reasoning_profile,
              reasoning_instruction: reasoning_instruction,
              isolation: .isolation
            }
        ],
        evidence: (
          if $outcome == "parallel-conflict" then
            $binding_evidence
          else
            $binding_evidence + [{
              kind: "effective-capacity",
              batch_id: $group_id,
              planned_width: $plan_max_parallelism,
              plan_max_parallelism: $plan_max_parallelism,
              ready_width: $ready_width,
              runtime_capacity: $runtime_capacity,
              actor_capacity: $actor_capacity,
              effective_width: $effective_width,
              planned_task_ids: [$group_tasks[] | .task_id],
              ready_task_ids: [$ready_frontier[] | .task_id],
              ready_frontier_task_ids: [$ready_frontier[] | .task_id],
              selected_task_ids: [$selected[] | .task_id],
              limiting_factors: $limiting_factors,
              serial_fallback_reason: (if $serial_fallback_reason == "" then null else $serial_fallback_reason end)
            }]
          end
        )
      }
    ' "$ledger_file"
}

execution_plan_ledger_drift_evidence_json() {
  local plan_file="$1"
  local ledger_file="$2"
  local catalog_json=""
  local approved_projection=""
  local observed_projection=""

  catalog_json="$(task_catalog_json "$plan_file")"
  approved_projection="$(jq -cS '
    [.[] | {
      section,
      title,
      task_id,
      scope_slice,
      depends_on,
      impl_file_refs,
      test_file_refs,
      verification_commands,
      executor_mode,
      parallel_group,
      parallel_policy,
      delegation_policy,
      execution_profile,
      reasoning_profile,
      isolation,
      resource_locks,
      convergence_required,
      task_review_depth,
      done_when,
      failure_policy,
      rollback_trigger,
      rollback_target,
      rollback_verification
    }]
  ' <<<"$catalog_json")"
  observed_projection="$(jq -cS '
    [.[] | {
      section,
      title,
      task_id,
      scope_slice,
      depends_on,
      impl_file_refs,
      test_file_refs,
      verification_commands,
      executor_mode,
      parallel_group,
      parallel_policy,
      delegation_policy,
      execution_profile,
      reasoning_profile,
      isolation,
      resource_locks,
      convergence_required,
      task_review_depth,
      done_when,
      failure_policy,
      rollback_trigger,
      rollback_target,
      rollback_verification
    }]
  ' "$ledger_file")"

  if [[ "$approved_projection" == "$observed_projection" ]]; then
    printf '[]\n'
    return
  fi

  jq -n \
    --argjson approved "$approved_projection" \
    --argjson observed "$observed_projection" \
    '[
      range(0; ([$approved | length, $observed | length] | max))
      | select($approved[.] != $observed[.])
      | {
          approved_task_id: ($approved[.].task_id // null),
          observed_task_id: ($observed[.].task_id // null)
        }
    ] as $differing_tasks
    | [{
        kind: "plan-ledger-drift",
        requirement: "ledger immutable task projection must match the approved plan",
        differing_tasks: $differing_tasks
      }]'
}

execution_plan_ledger_conflict_binding() {
  local plan_file="$1"
  local group_id="$2"
  local runtime_capacity="$3"
  local requested_model_policy="$4"
  local drift_evidence_json="$5"
  local catalog_json=""
  local default_model_policy=""
  local allowed_model_policy=""
  local plan_max_parallelism=""
  local saw_requested_policy=false

  [[ "$runtime_capacity" =~ ^[1-9][0-9]*$ ]] || {
    printf 'runtime capacity must be a positive integer: %s\n' "$runtime_capacity" >&2
    return 1
  }
  default_model_policy="$(extract_markdown_scalar "$plan_file" "Runtime Binding" "default_model_policy" | normalize_plan_metadata_values)"
  if [[ -z "$requested_model_policy" ]]; then
    requested_model_policy="$default_model_policy"
  fi
  is_valid_model_policy "$requested_model_policy" || {
    printf 'invalid model policy: %s\n' "$requested_model_policy" >&2
    return 1
  }
  while IFS= read -r allowed_model_policy; do
    allowed_model_policy="$(printf '%s\n' "$allowed_model_policy" | normalize_plan_metadata_values)"
    if [[ "$allowed_model_policy" == "$requested_model_policy" ]]; then
      saw_requested_policy=true
      break
    fi
  done < <(extract_markdown_list "$plan_file" "Runtime Binding" "allowed_model_policies")
  [[ "$saw_requested_policy" == "true" ]] || {
    printf 'model policy is not allowed by the plan: %s\n' "$requested_model_policy" >&2
    return 1
  }
  plan_max_parallelism="$(parallel_batch_max_parallelism "$plan_file" "$group_id" | normalize_plan_metadata_values)"
  [[ "$plan_max_parallelism" =~ ^[0-9]+$ && "$plan_max_parallelism" -ge 2 ]] || {
    printf 'parallel group is not linked to a valid approved batch: %s\n' "$group_id" >&2
    return 1
  }
  catalog_json="$(task_catalog_json "$plan_file")"

  jq -n \
    --arg group_id "$group_id" \
    --arg model_policy "$requested_model_policy" \
    --argjson runtime_capacity "$runtime_capacity" \
    --argjson plan_max_parallelism "$plan_max_parallelism" \
    --argjson task_catalog "$catalog_json" \
    --argjson drift_evidence "$drift_evidence_json" \
    '{
      outcome: "parallel-conflict",
      group_id: $group_id,
      batch_id: $group_id,
      approved_batch_id: $group_id,
      batch_identity: {
        batch_id: $group_id,
        parallel_group: $group_id,
        task_ids: [$task_catalog[] | select(.parallel_group == $group_id) | .task_id],
        parallel_policy: ([ $task_catalog[] | select(.parallel_group == $group_id) | .parallel_policy ] | unique | .[0] // null)
      },
      model_policy: $model_policy,
      runtime_capacity: $runtime_capacity,
      actor_capacity: 0,
      plan_max_parallelism: $plan_max_parallelism,
      planned_width: $plan_max_parallelism,
      ready_width: 0,
      effective_width: 0,
      stop_reason: null,
      serial_fallback_reason: null,
      limiting_factors: ["plan_ledger_drift"],
      capacity_evidence: {
        batch_id: $group_id,
        planned_width: $plan_max_parallelism,
        plan_max_parallelism: $plan_max_parallelism,
        ready_width: 0,
        runtime_capacity: $runtime_capacity,
        actor_capacity: 0,
        effective_width: 0,
        planned_task_ids: [$task_catalog[] | select(.parallel_group == $group_id) | .task_id],
        ready_task_ids: [],
        ready_frontier_task_ids: [],
        selected_task_ids: [],
        limiting_factors: ["plan_ledger_drift"],
        serial_fallback_reason: null
      },
      failure_kind: "parallel-conflict",
      recovery_phase: "dependency-freeze",
      ready_frontier_task_ids: [],
      ready_task_ids: [],
      planned_task_ids: [$task_catalog[] | select(.parallel_group == $group_id) | .task_id],
      selected_task_ids: [],
      task_topology: [
        $task_catalog[]
        | select(.parallel_group == $group_id)
        | {
            task_id,
            scope_slice,
            depends_on,
            parallel_group,
            parallel_policy,
            delegation_policy,
            execution_profile,
            reasoning_profile,
            isolation,
            resource_locks,
            impl_file_refs,
            test_file_refs,
            verification_commands,
            done_when,
            executor_mode
          }
      ],
      bindings: [],
      evidence: $drift_evidence
    }'
}

execution_runtime_binding() {
  local plan_file="$1"
  local ledger_file="$2"
  local group_id="$3"
  local runtime_capacity="$4"
  local requested_model_policy="${5:-}"
  local drift_evidence_json="[]"

  validate_execution_plan "$plan_file" >/dev/null || return 1
  drift_evidence_json="$(execution_plan_ledger_drift_evidence_json "$plan_file" "$ledger_file")"
  if [[ "$(jq 'length' <<<"$drift_evidence_json")" -gt 0 ]]; then
    execution_plan_ledger_conflict_binding \
      "$plan_file" \
      "$group_id" \
      "$runtime_capacity" \
      "$requested_model_policy" \
      "$drift_evidence_json"
    return
  fi
  execution_runtime_binding_from_validated_plan "$@"
}

execution_canonical_json_sha256() {
  local json_file="$1"

  [[ -f "$json_file" && ! -L "$json_file" ]] || {
    printf 'controller_binding_invalid: JSON input must be a regular non-symlink file: %s\n' "$json_file" >&2
    return 1
  }
  jq -cS . "$json_file" | shasum -a 256 | awk '{print $1}'
}

execution_herdr_agent_name() {
  local runtime_role="$1"
  local run_id="$2"
  local task_id="$3"
  local attempt="$4"
  local digest=""
  local animal_index=0
  local task_fragment=""
  local candidate=""
  local -a animal_names=(wolf owl fox otter badger lynx)

  case "$runtime_role" in
    reviewer|explorer|worker) ;;
    *)
      printf 'controller_binding_invalid: unsupported delegated role: %s\n' "$runtime_role" >&2
      return 1
      ;;
  esac
  [[ "$attempt" =~ ^[1-9][0-9]*$ ]] || {
    printf 'controller_binding_invalid: task attempt must be a positive integer\n' >&2
    return 1
  }

  digest="$(printf '%s' "$run_id:$task_id:$attempt" | shasum -a 256 | awk '{print $1}')"
  [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || {
    printf 'controller_binding_invalid: failed to derive agent identity\n' >&2
    return 1
  }
  animal_index=$((16#${digest:0:2} % ${#animal_names[@]}))
  task_fragment="$(
    printf '%s' "$task_id" \
      | tr '[:upper:]' '[:lower:]' \
      | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
  )"
  task_fragment="${task_fragment:0:6}"
  [[ -n "$task_fragment" ]] || task_fragment="task"
  candidate="$runtime_role-${animal_names[$animal_index]}-${digest:2:2}-t$task_fragment-a$attempt"
  candidate="${candidate:0:32}"
  candidate="$(printf '%s' "$candidate" | sed -E 's/-+$//')"
  [[ "$candidate" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$ ]] || {
    printf 'controller_binding_invalid: derived agent name is not valid\n' >&2
    return 1
  }
  printf '%s\n' "$candidate"
}

execution_git_common_directory() {
  local checkout_root="$1"
  local common_ref=""

  common_ref="$(git -C "$checkout_root" rev-parse --git-common-dir 2>/dev/null)" || return 1
  if [[ "$common_ref" = /* ]]; then
    realpath "$common_ref"
  else
    realpath "$checkout_root/$common_ref"
  fi
}

execution_git_directory() {
  local checkout_root="$1"
  local git_ref=""

  git_ref="$(git -C "$checkout_root" rev-parse --git-dir 2>/dev/null)" || return 1
  if [[ "$git_ref" = /* ]]; then
    realpath "$git_ref"
  else
    realpath "$checkout_root/$git_ref"
  fi
}

execution_controller_binding_envelope() {
  local plan_file="$1"
  local ledger_file="$2"
  local request_file="$3"
  local repo_root=""
  local repo_revision=""
  local repo_common_dir=""
  local plan_ref=""
  local ledger_ref=""
  local plan_digest=""
  local ledger_digest=""
  local expected_plan_digest=""
  local expected_ledger_digest=""
  local drift_evidence_json="[]"
  local controller_id=""
  local binding_kind=""
  local command_job_json="null"
  local command_cwd=""
  local command_locks_json="[]"
  local command_argv_json="[]"
  local run_id=""
  local run_nonce=""
  local task_id=""
  local attempt=""
  local model_policy=""
  local allowed_model_policy=""
  local saw_model_policy=false
  local task_count=0
  local task_json=""
  local task_state=""
  local expected_attempt=0
  local review_brief_path=""
  local review_brief_ref=""
  local review_brief_digest=""
  local expected_review_brief_digest=""
  local write_ref_count=0
  local runtime_role=""
  local requested_batch_id=""
  local requested_runtime_capacity=""
  local requested_batch_provenance_json="null"
  local canonical_batch_provenance_json="null"
  local runtime_batch_binding_json=""
  local batch_provenance_check_json=""
  local batch_group=""
  local capability_profile=""
  local sandbox_mode=""
  local agent_name=""
  local expected_agent_name=""
  local checkout_ref=""
  local checkout_root=""
  local checkout_common_dir=""
  local checkout_git_dir=""
  local physical_json=""
  local envelope_task_json=""
  local envelope_json=""
  local run_state_root=""
  local run_state_dir=""
  local output_file=""
  local temporary_file=""

  validate_execution_plan "$plan_file" >/dev/null || {
    printf 'controller_binding_unapproved: approved version-2 plan required\n' >&2
    return 1
  }
  plan_uses_v2_contract "$plan_file" || {
    printf 'controller_binding_invalid: version-2 plan contract required\n' >&2
    return 1
  }
  [[ -f "$ledger_file" && ! -L "$ledger_file" ]] || {
    printf 'controller_binding_invalid: ledger must be a regular non-symlink file\n' >&2
    return 1
  }
  [[ -f "$request_file" && ! -L "$request_file" ]] || {
    printf 'controller_binding_invalid: request must be a regular non-symlink file\n' >&2
    return 1
  }
  jq -e . "$ledger_file" >/dev/null || {
    printf 'controller_binding_invalid: ledger is not valid JSON\n' >&2
    return 1
  }
  jq -e '
    type == "object"
    and ((keys - [
      "attempt",
      "batch",
      "batch_id",
      "batch_provenance",
      "batch_runtime_capacity",
      "binding_kind",
      "command_job",
      "controller_id",
      "expected_ledger_sha256",
      "expected_plan_sha256",
      "model_policy",
      "physical_binding",
      "review_brief_path",
      "review_brief_sha256",
      "run_id",
      "run_nonce",
      "runtime_capacity",
      "schema_version",
      "task_id"
    ]) | length) == 0
    and (. as $request | all([
      "attempt",
      "binding_kind",
      "controller_id",
      "expected_ledger_sha256",
      "expected_plan_sha256",
      "model_policy",
      "physical_binding",
      "review_brief_path",
      "review_brief_sha256",
      "run_id",
      "run_nonce",
      "schema_version",
      "task_id"
    ][]; . as $key | $request | has($key) ))
    and .schema_version == 1
    and (.binding_kind == "delegated-task" or .binding_kind == "bounded-review" or .binding_kind == "command-job")
    and (.attempt | type == "number" and floor == . and . >= 1)
    and ([
      .controller_id,
      .binding_kind,
      .run_id,
      .run_nonce,
      .task_id,
      .model_policy,
      .expected_plan_sha256,
      .expected_ledger_sha256
    ] | all(.[]; type == "string" and length > 0 and (test("[[:cntrl:]]") | not)))
    and (
      if .binding_kind == "delegated-task" then
        .review_brief_path == "" and .review_brief_sha256 == ""
      elif .binding_kind == "bounded-review" then
        (.review_brief_path | type == "string" and length > 0 and startswith("/") and (test("[[:cntrl:]]") | not))
        and (.review_brief_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
      else
        .review_brief_path == "" and .review_brief_sha256 == ""
      end
    )
    and (.physical_binding | type == "object")
    and (
      if .binding_kind == "command-job" then
        (.physical_binding | keys) == ["checkout_path", "pane_id", "tab_id", "terminal_backend", "workspace_id"]
      else
        (.physical_binding | keys) == [
      "agent_kind",
      "agent_name",
      "capability_profile",
      "checkout_path",
      "control_plane_endpoint",
      "credential_ref",
      "model",
      "pane_id",
      "permission_mode",
      "reasoning_effort",
      "sandbox_mode",
      "tab_id",
      "terminal_backend",
      "workspace_id"
        ]
      end
    )
    and (.physical_binding | all(.[]; type == "string" and length > 0 and (test("[[:cntrl:]]") | not)))
    and (if .binding_kind == "command-job" then
      (.command_job | type == "object")
      and ((.command_job | keys) - ["argv", "command", "cwd", "max_concurrency", "output_bound_bytes", "provenance", "resource_locks", "timeout_seconds"] | length) == 0
      and (.command_job.cwd | type == "string" and startswith("/") and (test("[[:cntrl:]]") | not))
      and (.command_job.argv | type == "array" and length > 0 and all(.[]; type == "string" and length > 0 and length <= 32768 and (test("[[:cntrl:]`$;|&<>]") | not)))
      and ((.command_job.command // "") | type == "string" and (test("[`$;|&<>\n\r]") | not))
      and (.command_job.timeout_seconds | type == "number" and floor == . and . >= 1 and . <= 900)
      and (.command_job.max_concurrency | type == "number" and floor == . and . >= 1)
      and (.command_job.output_bound_bytes | type == "number" and floor == . and . >= 1 and . <= 65536)
      and (.command_job.resource_locks | type == "array" and length > 0 and all(.[]; type == "string" and length > 0 and . != "none" and (test("[[:cntrl:]]") | not)))
      and (.command_job.provenance | type == "object" and (.kind == "task" or .kind == "gate"))
    else true end)
    and ((.batch_id // "") | type == "string")
    and ((.batch_runtime_capacity // .runtime_capacity // null) == null or ((.batch_runtime_capacity // .runtime_capacity) | type == "number" and floor == . and . >= 1))
    and ((.batch_provenance // .batch // null) == null or ((.batch_provenance // .batch) | type == "object"))
  ' "$request_file" >/dev/null || {
    printf 'controller_binding_invalid: malformed or authority-expanding binding request\n' >&2
    return 1
  }

  binding_kind="$(jq -r '.binding_kind' "$request_file")"
  controller_id="$(jq -r '.controller_id' "$request_file")"
  run_id="$(jq -r '.run_id' "$request_file")"
  run_nonce="$(jq -r '.run_nonce' "$request_file")"
  task_id="$(jq -r '.task_id' "$request_file")"
  attempt="$(jq -r '.attempt' "$request_file")"
  model_policy="$(jq -r '.model_policy' "$request_file")"
  expected_plan_digest="$(jq -r '.expected_plan_sha256' "$request_file")"
  expected_ledger_digest="$(jq -r '.expected_ledger_sha256' "$request_file")"
  review_brief_path="$(jq -r '.review_brief_path' "$request_file")"
  expected_review_brief_digest="$(jq -r '.review_brief_sha256' "$request_file")"
  requested_batch_id="$(jq -r '.batch_id // .batch_provenance.batch_id // .batch.batch_id // empty' "$request_file")"
  requested_runtime_capacity="$(jq -r '.batch_runtime_capacity // .runtime_capacity // .batch_provenance.runtime_capacity // .batch.runtime_capacity // empty' "$request_file")"
  requested_batch_provenance_json="$(jq -c '.batch_provenance // .batch // null' "$request_file")"
  command_job_json="$(jq -c '.command_job // null' "$request_file")"

  plan_token_is_safe "$controller_id" && [[ "${#controller_id}" -le 128 ]] || {
    printf 'controller_binding_invalid: controller ID must be a bounded portable token\n' >&2
    return 1
  }
  plan_token_is_safe "$run_id" && [[ "${#run_id}" -le 128 ]] || {
    printf 'controller_binding_invalid: run ID must be a bounded portable token\n' >&2
    return 1
  }
  plan_token_is_safe "$run_nonce" && [[ "${#run_nonce}" -le 256 ]] || {
    printf 'controller_binding_required: controller nonce must be a bounded portable token\n' >&2
    return 1
  }
  plan_token_is_safe "$task_id" && [[ "${#task_id}" -le 128 ]] || {
    printf 'controller_binding_invalid: task ID must be a bounded portable token\n' >&2
    return 1
  }
  [[ "$expected_plan_digest" =~ ^[0-9a-f]{64}$ && "$expected_ledger_digest" =~ ^[0-9a-f]{64}$ ]] || {
    printf 'controller_binding_stale: expected digests must be lowercase SHA-256 values\n' >&2
    return 1
  }
  is_valid_model_policy "$model_policy" || {
    printf 'controller_binding_invalid: unsupported model policy: %s\n' "$model_policy" >&2
    return 1
  }
  while IFS= read -r allowed_model_policy; do
    allowed_model_policy="$(printf '%s\n' "$allowed_model_policy" | normalize_plan_metadata_values)"
    if [[ "$allowed_model_policy" == "$model_policy" ]]; then
      saw_model_policy=true
      break
    fi
  done < <(extract_markdown_list "$plan_file" "Runtime Binding" "allowed_model_policies")
  [[ "$saw_model_policy" == "true" ]] || {
    printf 'controller_binding_invalid: model policy is not allowed by the approved plan: %s\n' "$model_policy" >&2
    return 1
  }

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    printf 'controller_binding_invalid: controller is not inside a Git repository\n' >&2
    return 1
  }
  repo_root="$(realpath "$repo_root")"
  repo_revision="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null)" || {
    printf 'controller_binding_invalid: repository revision is unavailable\n' >&2
    return 1
  }
  repo_common_dir="$(execution_git_common_directory "$repo_root")" || {
    printf 'controller_binding_invalid: repository common directory is unavailable\n' >&2
    return 1
  }
  plan_ref="$(repo_relative_artifact_ref "$repo_root" "$plan_file")" || {
    printf 'controller_binding_invalid: plan must be inside the controller repository\n' >&2
    return 1
  }
  ledger_ref="$(execution_artifact_ref "$ledger_file")"
  plan_digest="$(harness_file_sha256 "$plan_file")"
  ledger_digest="$(execution_canonical_json_sha256 "$ledger_file")"
  [[ "$plan_digest" == "$expected_plan_digest" ]] || {
    printf 'controller_binding_stale: approved plan digest changed\n' >&2
    return 1
  }
  [[ "$ledger_digest" == "$expected_ledger_digest" ]] || {
    printf 'controller_binding_stale: task ledger digest changed\n' >&2
    return 1
  }
  drift_evidence_json="$(execution_plan_ledger_drift_evidence_json "$plan_file" "$ledger_file")"
  [[ "$(jq 'length' <<<"$drift_evidence_json")" -eq 0 ]] || {
    printf 'controller_binding_drift: ledger immutable task projection differs from approved plan\n' >&2
    return 1
  }

  if [[ "$binding_kind" == "command-job" ]]; then
    task_count="$(jq --arg task_id "$task_id" '[.[] | select(.task_id == $task_id)] | length' "$ledger_file")"
    [[ "$task_count" -eq 1 ]] || {
      printf 'controller_binding_task_unknown: command job task must resolve exactly once: %s\n' "$task_id" >&2
      return 1
    }
    task_json="$(jq -c --arg task_id "$task_id" '.[] | select(.task_id == $task_id)' "$ledger_file")"
    task_state="$(jq -r '.status' <<<"$task_json")"
    [[ "$task_state" == "ready" ]] || {
      printf 'controller_binding_task_not_ready: command job task is %s: %s\n' "$task_state" "$task_id" >&2
      return 1
    }
    expected_attempt="$(jq '(.attempt_count // 0) + 1' <<<"$task_json")"
    [[ "$attempt" -eq "$expected_attempt" ]] || {
      printf 'controller_binding_stale: command job task attempt must be %s: %s\n' "$expected_attempt" "$task_id" >&2
      return 1
    }
    command_cwd="$(jq -r '.cwd' <<<"$command_job_json")"
    [[ "$command_cwd" = /* && -d "$command_cwd" && ! -L "$command_cwd" ]] || {
      printf 'controller_binding_invalid: command cwd must be an existing non-symlink directory\n' >&2
      return 1
    }
    command_cwd="$(realpath "$command_cwd")"
    checkout_ref="$(jq -r '.physical_binding.checkout_path' "$request_file")"
    [[ "$command_cwd" == "$(realpath "$checkout_ref")" ]] || {
      printf 'controller_binding_cwd_mismatch: command cwd must exactly match checkout_path\n' >&2
      return 1
    }
    command_argv_json="$(jq -c '.argv' <<<"$command_job_json")"
    command_locks_json="$(jq -c '.resource_locks' <<<"$command_job_json")"
    jq -e --argjson locks "$command_locks_json" --argjson command_job "$command_job_json" '
      . as $task
      |
      (if $command_job.provenance.kind == "task" then
         (($locks | sort) == (($task.resource_locks // []) | sort))
         and ($command_job.max_concurrency == 1)
       else
         ($command_job.provenance.gate_id | type == "string" and length > 0 and (test("[[:cntrl:]]") | not))
         and ($locks | all(. as $lock | (($task.resource_locks // []) | index($lock)) != null))
         and ($command_job.max_concurrency <= (($task.resource_locks // []) | length))
       end)
      and ($locks | length > 0)
      and (.executor_mode == "main" or .executor_mode == "subagent")
      and (($command_job.provenance.kind // "") == "task" or ($command_job.provenance.kind // "") == "gate")
      and (($command_job.provenance.kind != "task") or ($command_job.provenance.task_id == .task_id))
    ' <<<"$task_json" >/dev/null || {
      printf 'controller_binding_invalid: command job locks or task provenance are not approved\n' >&2
      return 1
    }
    jq -e --argjson argv "$command_argv_json" --arg command_literal "$(jq -r '.command // empty' <<<"$command_job_json")" '
      ($argv | all(.[]; (test("[`$;|&<>\\n\\r]") | not)))
      and ($command_literal == "" or $command_literal == ($argv | join(" ")))
    ' <<<"$command_job_json" >/dev/null || {
      printf 'controller_binding_invalid: command job must use an exact literal argv without interpolation\n' >&2
      return 1
    }
    runtime_role="command-job"
    write_ref_count=0
    requested_batch_id="$(jq -r '.batch_id // .batch_provenance.batch_id // .batch.batch_id // empty' "$request_file")"
    requested_runtime_capacity="$(jq -r '.batch_runtime_capacity // .runtime_capacity // .batch_provenance.runtime_capacity // .batch.runtime_capacity // empty' "$request_file")"
    requested_batch_provenance_json="$(jq -c '.batch_provenance // .batch // null' "$request_file")"
    batch_group="$(jq -r '.parallel_group // "none"' <<<"$task_json")"
    if [[ "$batch_group" != "none" ]]; then
      [[ -n "$requested_batch_id" && "$requested_batch_id" == "$batch_group" ]] || {
        printf 'controller_binding_batch_mismatch: command job batch identity does not match selected task\n' >&2
        return 1
      }
      [[ "$requested_runtime_capacity" =~ ^[1-9][0-9]*$ ]] || {
        printf 'controller_binding_batch_required: command job requires runtime capacity evidence\n' >&2
        return 1
      }
      [[ "$(jq -r 'type' <<<"$requested_batch_provenance_json")" == "object" ]] || {
        printf 'controller_binding_batch_required: command job requires batch provenance\n' >&2
        return 1
      }
      runtime_batch_binding_json="$(execution_runtime_binding_from_validated_plan "$plan_file" "$ledger_file" "$batch_group" "$requested_runtime_capacity" "$model_policy")" || {
        printf 'controller_binding_batch_invalid: command job batch provenance could not be recomputed\n' >&2
        return 1
      }
      jq -e '.outcome == "bound" or .outcome == "serial-fallback"' <<<"$runtime_batch_binding_json" >/dev/null || {
        printf 'controller_binding_batch_invalid: command job selected batch is not allocatable\n' >&2
        return 1
      }
      canonical_batch_provenance_json="$(jq -cS '{
        batch_id,
        parallel_group: .batch_identity.parallel_group,
        parallel_policy: .batch_identity.parallel_policy,
        batch_task_ids: .batch_identity.task_ids,
        planned_task_ids: .batch_identity.task_ids,
        planned_width,
        plan_max_parallelism: .planned_width,
        ready_width,
        ready_task_ids: .ready_task_ids,
        ready_frontier_task_ids: .ready_task_ids,
        selected_task_ids,
        runtime_capacity,
        actor_capacity,
        effective_width,
        limiting_factors,
        serial_fallback_reason,
        outcome,
        stop_reason
      }' <<<"$runtime_batch_binding_json")"
      batch_provenance_check_json="$(jq -c \
        --arg task_id "$task_id" \
        --arg batch_id "$requested_batch_id" \
        --argjson expected "$canonical_batch_provenance_json" \
        --argjson supplied "$requested_batch_provenance_json" \
        '[
          ($expected.batch_id == $batch_id),
          (($expected.selected_task_ids | index($task_id)) != null),
          ($supplied.batch_id == $expected.batch_id),
          ($supplied.parallel_group == $expected.parallel_group),
          (($supplied.batch_task_ids // $supplied.task_ids) == $expected.batch_task_ids),
          (($supplied.planned_width // $supplied.plan_max_parallelism) == $expected.planned_width),
          ($supplied.ready_width == $expected.ready_width),
          (($supplied.ready_task_ids // $supplied.ready_frontier_task_ids) == $expected.ready_task_ids),
          ($supplied.selected_task_ids == $expected.selected_task_ids),
          ($supplied.runtime_capacity == $expected.runtime_capacity),
          ($supplied.actor_capacity == $expected.actor_capacity),
          ($supplied.effective_width == $expected.effective_width),
          ($supplied.limiting_factors == $expected.limiting_factors),
          ($supplied.serial_fallback_reason == $expected.serial_fallback_reason),
          ($supplied.outcome == $expected.outcome),
          ($supplied.stop_reason == $expected.stop_reason)
        ] as $checks | {valid: ($checks | all), checks: $checks}' <<<"$runtime_batch_binding_json")"
      [[ "$(jq -r '.valid' <<<"$batch_provenance_check_json")" == "true" ]] || {
        printf 'controller_binding_batch_forged: command job batch provenance is not controller-issued\n' >&2
        return 1
      }
    fi
  elif [[ "$binding_kind" == "bounded-review" ]]; then
    jq -e 'type == "array" and length > 0 and all(.[]; .status == "done")' "$ledger_file" >/dev/null || {
      printf 'controller_binding_task_not_ready: bounded review requires a fully converged ledger\n' >&2
      return 1
    }
    [[ -f "$review_brief_path" && ! -L "$review_brief_path" ]] || {
      printf 'controller_binding_invalid: review brief must be a regular non-symlink file\n' >&2
      return 1
    }
    review_brief_digest="$(harness_file_sha256 "$review_brief_path")"
    [[ "$review_brief_digest" == "$expected_review_brief_digest" ]] || {
      printf 'controller_binding_stale: bounded review brief digest changed\n' >&2
      return 1
    }
    review_brief_ref="$(execution_artifact_ref "$review_brief_path")"
    expected_attempt=1
    [[ "$attempt" -eq "$expected_attempt" ]] || {
      printf 'controller_binding_stale: bounded review attempt must be 1\n' >&2
      return 1
    }
    runtime_role="reviewer"
    write_ref_count=0
    task_json="$(jq -n -c \
      --arg task_id "$task_id" \
      --arg review_brief_ref "$review_brief_ref" \
      --arg review_brief_sha256 "$review_brief_digest" \
      '{
        section: "Implementation Review",
        title: "Bounded implementation review",
        task_id: $task_id,
        scope_slice: "Review only the controller-issued bounded implementation brief",
        depends_on: [],
        impl_file_refs: [],
        test_file_refs: [],
        verification_commands: [$review_brief_ref],
        executor_mode: "subagent",
        parallel_group: "none",
        parallel_policy: "serial",
        delegation_policy: "preferred",
        execution_profile: "deep",
        reasoning_profile: "deep",
        isolation: "shared-read-only",
        resource_locks: ["repository-review"],
        convergence_required: false,
        task_review_depth: "implementation",
        done_when: ["candidate findings returned to the main controller"],
        failure_policy: "stop-and-diagnose",
        rollback_trigger: "none",
        rollback_target: "none",
        rollback_verification: "none",
        status: "ready",
        attempt_count: 0,
        review_brief_ref: $review_brief_ref,
        review_brief_sha256: $review_brief_sha256
      }')"
  else
    task_count="$(jq --arg task_id "$task_id" '[.[] | select(.task_id == $task_id)] | length' "$ledger_file")"
    [[ "$task_count" -eq 1 ]] || {
      printf 'controller_binding_task_unknown: selected task must resolve exactly once: %s\n' "$task_id" >&2
      return 1
    }
    task_json="$(jq -c --arg task_id "$task_id" '.[] | select(.task_id == $task_id)' "$ledger_file")"
    task_state="$(jq -r '.status' <<<"$task_json")"
    [[ "$task_state" == "ready" ]] || {
      printf 'controller_binding_task_not_ready: selected task is %s: %s\n' "$task_state" "$task_id" >&2
      return 1
    }
    expected_attempt="$(jq '(.attempt_count // 0) + 1' <<<"$task_json")"
    [[ "$attempt" -eq "$expected_attempt" ]] || {
      printf 'controller_binding_stale: task attempt must be %s: %s\n' "$expected_attempt" "$task_id" >&2
      return 1
    }
    jq -e '.delegation_policy != "forbidden" and .executor_mode == "subagent"' <<<"$task_json" >/dev/null || {
      printf 'controller_binding_authority_denied: Herdr adapter accepts delegated tasks only: %s\n' "$task_id" >&2
      return 1
    }
    write_ref_count="$(jq '
      ((.impl_file_refs // []) + (.test_file_refs // []))
      | map(select(. != "" and . != "none"))
      | length
    ' <<<"$task_json")"
    if [[ "$write_ref_count" -eq 0 ]] \
      && jq -e '.execution_profile == "fast" and .reasoning_profile == "light" and .isolation == "shared-read-only"' <<<"$task_json" >/dev/null; then
      runtime_role="explorer"
    else
      runtime_role="worker"
    fi

    batch_group="$(jq -r '.parallel_group // "none"' <<<"$task_json")"
    if [[ "$batch_group" != "none" ]]; then
      [[ -n "$requested_batch_id" && "$requested_batch_id" == "$batch_group" ]] || {
        printf 'controller_binding_batch_mismatch: request batch identity does not match selected task\n' >&2
        return 1
      }
      [[ "$requested_runtime_capacity" =~ ^[1-9][0-9]*$ ]] || {
        printf 'controller_binding_batch_required: named parallel task requires runtime capacity evidence\n' >&2
        return 1
      }
      [[ "$(jq -r 'type' <<<"$requested_batch_provenance_json")" == "object" ]] || {
        printf 'controller_binding_batch_required: named parallel task requires batch provenance\n' >&2
        return 1
      }
      if ! runtime_batch_binding_json="$(execution_runtime_binding_from_validated_plan \
        "$plan_file" "$ledger_file" "$batch_group" "$requested_runtime_capacity" "$model_policy")"; then
        printf 'controller_binding_batch_invalid: runtime batch provenance could not be recomputed\n' >&2
        return 1
      fi
      jq -e '.outcome == "bound" or .outcome == "serial-fallback"' <<<"$runtime_batch_binding_json" >/dev/null || {
        printf 'controller_binding_batch_invalid: selected batch is not allocatable\n' >&2
        return 1
      }
      canonical_batch_provenance_json="$(jq -cS '
        {
          batch_id,
          parallel_group: .batch_identity.parallel_group,
          parallel_policy: .batch_identity.parallel_policy,
          batch_task_ids: .batch_identity.task_ids,
          planned_task_ids: .batch_identity.task_ids,
          planned_width,
          plan_max_parallelism: .planned_width,
          ready_width,
          ready_task_ids: .ready_task_ids,
          ready_frontier_task_ids: .ready_task_ids,
          selected_task_ids,
          runtime_capacity,
          actor_capacity,
          effective_width,
          limiting_factors,
          serial_fallback_reason,
          outcome,
          stop_reason
        }
      ' <<<"$runtime_batch_binding_json")"
      batch_provenance_check_json="$(jq -c \
        --arg task_id "$task_id" \
        --arg batch_id "$requested_batch_id" \
        --argjson expected "$canonical_batch_provenance_json" \
        --argjson supplied "$requested_batch_provenance_json" \
        '
          [
            ($expected.batch_id == $batch_id),
            (($expected.selected_task_ids | index($task_id)) != null),
            ($supplied.batch_id == $expected.batch_id),
            ($supplied.parallel_group == $expected.parallel_group),
            (($supplied.batch_task_ids // $supplied.task_ids) == $expected.batch_task_ids),
            (($supplied.planned_width // $supplied.plan_max_parallelism) == $expected.planned_width),
            ($supplied.ready_width == $expected.ready_width),
            (($supplied.ready_task_ids // $supplied.ready_frontier_task_ids) == $expected.ready_task_ids),
            ($supplied.selected_task_ids == $expected.selected_task_ids),
            ($supplied.runtime_capacity == $expected.runtime_capacity),
            ($supplied.actor_capacity == $expected.actor_capacity),
            ($supplied.effective_width == $expected.effective_width),
            ($supplied.limiting_factors == $expected.limiting_factors),
            ($supplied.serial_fallback_reason == $expected.serial_fallback_reason),
            ($supplied.outcome == $expected.outcome),
            ($supplied.stop_reason == $expected.stop_reason)
          ] as $checks
          | {valid: ($checks | all), checks: $checks}
        ' <<<"$runtime_batch_binding_json")"
      [[ "$(jq -r '.valid' <<<"$batch_provenance_check_json")" == "true" ]] || {
        printf 'controller_binding_batch_forged: request batch provenance is not controller-issued (%s)\n' "$batch_provenance_check_json" >&2
        return 1
      }
    fi
  fi

  physical_json="$(jq -c '.physical_binding' "$request_file")"
  checkout_ref="$(jq -r '.checkout_path' <<<"$physical_json")"
  if [[ "$binding_kind" != "command-job" ]]; then
    capability_profile="$(jq -r '.capability_profile' <<<"$physical_json")"
    sandbox_mode="$(jq -r '.sandbox_mode' <<<"$physical_json")"
    agent_name="$(jq -r '.agent_name' <<<"$physical_json")"
    jq -e --arg runtime_role "$runtime_role" --arg model_policy "$model_policy" '
    .terminal_backend == "herdr"
    and (.agent_kind == "codex" or .agent_kind == "grok")
    and (.permission_mode == "never" or .permission_mode == "always-approve")
    and (.sandbox_mode == "read-only" or .sandbox_mode == "workspace-write")
    and (.capability_profile == "delegated-read-only" or .capability_profile == "delegated-local-writer")
    and (.agent_name | test("^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$"))
    and (.checkout_path | startswith("/"))
    and (
      (.agent_kind == "codex"
        and (.model | test("^gpt-5\\.6(-(?:sol|terra|luna))?$"))
        and .control_plane_endpoint == "native://openai"
        and .credential_ref == "native-login/codex")
      or
      (.agent_kind == "grok"
        and (.model | test("^(grok-4\\.5|gpt-5\\.6(-(?:sol|terra|luna))?)$"))
        and .control_plane_endpoint == "native://grok"
        and .credential_ref == "native-login/grok")
    )
    and (.reasoning_effort == "low" or .reasoning_effort == "medium" or .reasoning_effort == "high" or .reasoning_effort == "xhigh")
    and (
      if .capability_profile == "delegated-read-only" then
        .permission_mode == "never" and .sandbox_mode == "read-only"
      else
        (.permission_mode == "never" or .permission_mode == "always-approve")
        and .sandbox_mode == "workspace-write"
      end
    )
    and (
      if $runtime_role == "reviewer" then
        .agent_kind == "codex"
        and (.model == "gpt-5.6" or .model == "gpt-5.6-sol")
        and (.reasoning_effort == "high" or .reasoning_effort == "xhigh")
      elif $runtime_role == "explorer" then
        (.reasoning_effort == "low" or .reasoning_effort == "medium")
        and (
          if $model_policy == "semantic-routing" then
            ((.agent_kind == "codex" and .model == "gpt-5.6-luna")
            or (.agent_kind == "grok" and .model == "grok-4.5"))
          else true
          end
        )
      else true
      end
    )
    ' <<<"$physical_json" >/dev/null || {
      printf 'controller_binding_invalid: unsupported physical binding\n' >&2
      return 1
    }
    expected_agent_name="$(execution_herdr_agent_name "$runtime_role" "$run_id" "$task_id" "$attempt")" || return 1
    [[ "$agent_name" == "$expected_agent_name" ]] || {
      printf 'controller_binding_invalid: agent name does not match deterministic task projection\n' >&2
      return 1
    }
  fi
  [[ -d "$checkout_ref" && ! -L "$checkout_ref" ]] || {
    printf 'controller_binding_invalid: checkout must be an existing non-symlink directory\n' >&2
    return 1
  }
  checkout_root="$(git -C "$checkout_ref" rev-parse --show-toplevel 2>/dev/null)" || {
    printf 'controller_binding_invalid: checkout is not a Git worktree\n' >&2
    return 1
  }
  checkout_root="$(realpath "$checkout_root")"
  checkout_common_dir="$(execution_git_common_directory "$checkout_root")" || {
    printf 'controller_binding_invalid: checkout common directory is unavailable\n' >&2
    return 1
  }
  [[ "$checkout_common_dir" == "$repo_common_dir" ]] || {
    printf 'controller_binding_repository_mismatch: checkout belongs to another repository\n' >&2
    return 1
  }
  if [[ "$binding_kind" == "command-job" ]]; then
    [[ "$checkout_ref" = /* && -d "$checkout_ref" && ! -L "$checkout_ref" ]] || {
      printf 'controller_binding_invalid: command checkout must be an existing non-symlink directory\n' >&2
      return 1
    }
  elif [[ "$write_ref_count" -gt 0 ]]; then
    [[ "$capability_profile" == "delegated-local-writer" && "$sandbox_mode" == "workspace-write" ]] || {
      printf 'controller_binding_capability_mismatch: writer requires delegated-local-writer and workspace-write\n' >&2
      return 1
    }
    jq -e '.isolation == "isolated-worktree"' <<<"$task_json" >/dev/null || {
      printf 'controller_binding_capability_mismatch: writer task requires isolated-worktree plan isolation\n' >&2
      return 1
    }
    checkout_git_dir="$(execution_git_directory "$checkout_root")" || {
      printf 'controller_binding_invalid: checkout Git directory is unavailable\n' >&2
      return 1
    }
    [[ "$checkout_root" != "$repo_root" && "$checkout_git_dir" != "$checkout_common_dir" ]] || {
      printf 'controller_binding_capability_mismatch: writer checkout must be an isolated worktree\n' >&2
      return 1
    }
  else
    [[ "$capability_profile" == "delegated-read-only" && "$sandbox_mode" == "read-only" ]] || {
      printf 'controller_binding_capability_mismatch: read-only task requires delegated-read-only and read-only sandbox\n' >&2
      return 1
    }
  fi

  envelope_task_json="$(jq -c \
    --arg runtime_role "$runtime_role" \
    --argjson attempt "$attempt" \
    '
    ({
      section,
      title,
      task_id,
      scope_slice,
      depends_on,
      impl_file_refs,
      test_file_refs,
      verification_commands,
      executor_mode,
      parallel_group,
      parallel_policy,
      delegation_policy,
      execution_profile,
      reasoning_profile,
      isolation,
      resource_locks,
      convergence_required,
      task_review_depth,
      done_when,
      failure_policy,
      rollback_trigger,
      rollback_target,
      rollback_verification,
      status,
      attempt: $attempt,
      runtime_role: $runtime_role,
      touch_set: (((.impl_file_refs // []) + (.test_file_refs // [])) | map(select(. != "" and . != "none")) | unique),
      oracle_refs: (.verification_commands // []),
      start_state: "ready"
    } + (if has("review_brief_ref") then {
      review_brief_ref,
      review_brief_sha256
    } else {} end))
    ' <<<"$task_json")"
  envelope_json="$(jq -n -cS \
    --arg binding_kind "$binding_kind" \
    --arg controller_id "$controller_id" \
    --arg run_id "$run_id" \
    --arg run_nonce "$run_nonce" \
    --arg model_policy "$model_policy" \
    --arg canonical_repository "$repo_root" \
    --arg repository_revision "$repo_revision" \
    --arg plan_ref "$plan_ref" \
    --arg plan_sha256 "$plan_digest" \
    --arg ledger_ref "$ledger_ref" \
    --arg ledger_sha256 "$ledger_digest" \
    --argjson batch_provenance "$canonical_batch_provenance_json" \
    --argjson task "$envelope_task_json" \
    --argjson command_job "$command_job_json" \
    --argjson physical_binding "$physical_json" \
    '{
      schema_version: 1,
      artifact_kind: "controller-binding-envelope",
      controller: {
        controller_id: $controller_id,
        binding_kind: $binding_kind,
        run_id: $run_id,
        run_nonce: $run_nonce,
        model_policy: $model_policy
      },
      provenance: {
        canonical_repository: $canonical_repository,
        repository_revision: $repository_revision,
        plan_ref: $plan_ref,
        plan_sha256: $plan_sha256,
        ledger_ref: $ledger_ref,
        ledger_sha256: $ledger_sha256,
        batch: $batch_provenance
      },
      batch_provenance: $batch_provenance,
      task: $task,
      command_job: (if $binding_kind == "command-job" then $command_job else null end),
      physical_binding: $physical_binding,
      authority: {
        adapter_capabilities: [
          "consume-binding",
          "manage-run-owned-terminal-resources",
          "persist-adapter-state"
        ],
        denied_capabilities: [
          "select-task",
          "mutate-task-ledger",
          "converge-task",
          "invoke-review",
          "adjudicate-findings",
          "repair-implementation",
          "derive-lifecycle-tail",
          "claim-task-success"
        ]
      }
    }')"
  jq -e '
    [paths(scalars) as $p | ($p[-1] | tostring)]
    | all(.[]; test("^(secret|token|password|api_key|prompt)$"; "i") | not)
  ' <<<"$envelope_json" >/dev/null || {
    printf 'controller_binding_invalid: envelope would persist forbidden secret or prompt fields\n' >&2
    return 1
  }

  run_state_root="$repo_root/.herdr-runs"
  run_state_dir="$run_state_root/$run_id"
  output_file="$run_state_dir/controller-binding.json"
  [[ ! -L "$run_state_root" && ( ! -e "$run_state_root" || -d "$run_state_root" ) ]] || {
    printf 'controller_binding_unsafe_output: run-state root is not a safe directory\n' >&2
    return 1
  }
  [[ ! -L "$run_state_dir" && ( ! -e "$run_state_dir" || -d "$run_state_dir" ) ]] || {
    printf 'controller_binding_unsafe_output: run directory is not a safe directory\n' >&2
    return 1
  }

  (
    umask 077
    mkdir -p -- "$run_state_dir"
    chmod 700 -- "$run_state_root" "$run_state_dir"
    temporary_file="$(mktemp "$run_state_dir/.controller-binding.XXXXXX")"
    if ! printf '%s\n' "$envelope_json" >"$temporary_file"; then
      rm -f -- "$temporary_file"
      return 1
    fi
    chmod 600 -- "$temporary_file"
    mv -f -- "$temporary_file" "$output_file"
  ) || {
    printf 'controller_binding_write_failed: failed to atomically materialize envelope\n' >&2
    return 1
  }

  printf '%s\n' "$output_file"
}

execution_ready_batch() {
  execution_runtime_binding "$@"
}

execution_controller_converge() {
  task_ledger_controller_converge "$@"
}

execution_artifact_ref() {
  local file_ref="$1"
  local repo_root=""
  local resolved_ref=""

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  resolved_ref="$(realpath "$file_ref")"
  case "$resolved_ref" in
    "$repo_root"/*) printf '%s\n' "${resolved_ref#"$repo_root"/}" ;;
    *) printf '%s\n' "$resolved_ref" ;;
  esac
}

execution_stable_truth_refs_json() {
  local plan_file="$1"

  extract_markdown_list "$plan_file" "Truth Sync Handoff" "stable_truth_refs" \
    | normalize_plan_metadata_values \
    | awk 'NF > 0' \
    | sort -u \
    | jq -R . \
    | jq -s .
}

execution_docs_governance_predicates_json() {
  local plan_file="$1"

  extract_markdown_list "$plan_file" "Truth Sync Handoff" "docs_governance_predicates" \
    | normalize_plan_metadata_values \
    | awk 'NF > 0' \
    | sort -u \
    | jq -R . \
    | jq -s .
}

build_execution_result_json() {
  local plan_file="$1"
  local ledger_file="$2"
  local review_state="$6"
  local verify_state="$7"
  local base_json=""
  local design_file=""
  local approved_plan_ref=""
  local approved_design_ref=""
  local plan_digest=""
  local design_digest=""
  local ledger_digest=""
  local truth_required=""
  local lifecycle_state=""
  local derived_stop_reason=""
  local derived_next_entry=""
  local derived_next_phase=""
  local derived_human_input=false
  local remaining_task_count=0
  local stable_truth_refs_json="[]"
  local allowed_touch_refs_json="[]"
  local docs_predicates_json="[]"
  local task_evidence_json="[]"
  local drift_evidence_json="[]"

  validate_execution_plan "$plan_file" >/dev/null || return 1
  [[ -f "$ledger_file" ]] || {
    printf 'missing execution ledger: %s\n' "$ledger_file" >&2
    return 1
  }
  drift_evidence_json="$(execution_plan_ledger_drift_evidence_json "$plan_file" "$ledger_file")"
  if [[ "$(jq 'length' <<<"$drift_evidence_json")" -gt 0 ]]; then
    printf 'execution ledger does not match the approved immutable task projection\n' >&2
    return 1
  fi

  base_json="$(build_execution_result "$@")"
  design_file="$(resolve_execution_design_file "$plan_file")"
  approved_plan_ref="$(execution_artifact_ref "$plan_file")"
  approved_design_ref="$(execution_artifact_ref "$design_file")"
  plan_digest="$(harness_file_sha256 "$plan_file")"
  design_digest="$(harness_file_sha256 "$design_file")"
  ledger_digest="$(jq -cS . "$ledger_file" | shasum -a 256 | awk '{print $1}')"
  truth_required="$(execution_truth_sync_required "$plan_file")"
  stable_truth_refs_json="$(execution_stable_truth_refs_json "$plan_file")"
  allowed_touch_refs_json="$(execution_allowed_touch_set "$plan_file" | jq -R . | jq -s 'sort')"
  docs_predicates_json="$(execution_docs_governance_predicates_json "$plan_file")"
  task_evidence_json="$(jq '.' "$ledger_file")"
  remaining_task_count="$(jq -r '.remaining_task_count' <<<"$base_json")"

  if [[ "$remaining_task_count" -eq 0 ]] && ! jq -e '
    all(.[];
      .status == "done" and
      (
        ((.convergence_required // false) == false) or
        (.convergence_verified == true and .oracles_verified == true and .integration_verified == true and .convergence_actor == "controller")
      )
    )
  ' "$ledger_file" >/dev/null; then
    printf 'completed execution evidence requires controller-converged task oracles and integration proof\n' >&2
    return 1
  fi

  if [[ "$remaining_task_count" -gt 0 ]]; then
    lifecycle_state="implementation-pending"
    derived_stop_reason="$(jq -r '.stop_reason' <<<"$base_json")"
    derived_next_entry="$(jq -r '.next_entry' <<<"$base_json")"
    derived_next_phase="$(jq -r '.next_phase' <<<"$base_json")"
    derived_human_input="$(jq -r '.human_input_required' <<<"$base_json")"
  elif [[ "$review_state" != "pass" ]]; then
    lifecycle_state="task-complete"
    derived_stop_reason="final_review_failed"
    derived_next_entry="implement-change"
    derived_next_phase="review"
  elif [[ "$verify_state" != "pass" ]]; then
    lifecycle_state="task-complete"
    derived_stop_reason="final_verification_failed"
    derived_next_entry="implement-change"
    derived_next_phase="verify"
  elif [[ "$truth_required" == "true" && "$(jq 'length' <<<"$stable_truth_refs_json")" -eq 0 ]]; then
    lifecycle_state="task-complete"
    derived_stop_reason="truth_sync_scope_required"
    derived_next_entry="plan-change"
    derived_next_phase="plan"
    derived_human_input=true
  elif [[ "$truth_required" == "true" ]]; then
    lifecycle_state="truth-sync-pending"
    derived_stop_reason="truth_sync_required"
    derived_next_entry="sync-truth"
    derived_next_phase="truth-sync"
  else
    lifecycle_state="ready-for-close"
    derived_stop_reason="ready_for_close"
    derived_next_entry="close-change"
    derived_next_phase="close"
    derived_human_input=true
  fi

  jq \
    --arg approved_plan_ref "$approved_plan_ref" \
    --arg approved_design_ref "$approved_design_ref" \
    --arg plan_sha256 "$plan_digest" \
    --arg design_sha256 "$design_digest" \
    --arg ledger_sha256 "$ledger_digest" \
    --arg review_gate_ref "review:$plan_digest:$ledger_digest:$review_state" \
    --arg verification_ref "verification:$plan_digest:$ledger_digest:$verify_state" \
    --arg lifecycle_state "$lifecycle_state" \
    --arg stop_reason "$derived_stop_reason" \
    --arg next_entry "$derived_next_entry" \
    --arg next_phase "$derived_next_phase" \
    --argjson human_input_required "$derived_human_input" \
    --argjson truth_sync_required "$truth_required" \
    --argjson stable_truth_refs "$stable_truth_refs_json" \
    --argjson allowed_touch_refs "$allowed_touch_refs_json" \
    --argjson docs_governance_predicates "$docs_predicates_json" \
    --argjson task_evidence "$task_evidence_json" \
    '. + {
      approved_plan_ref: $approved_plan_ref,
      approved_design_ref: $approved_design_ref,
      plan_sha256: $plan_sha256,
      design_sha256: $design_sha256,
      ledger_sha256: $ledger_sha256,
      review_gate_ref: $review_gate_ref,
      verification_ref: $verification_ref,
      truth_sync_required: $truth_sync_required,
      stable_truth_refs: $stable_truth_refs,
      allowed_touch_refs: $allowed_touch_refs,
      docs_governance_predicates: $docs_governance_predicates,
      task_evidence: $task_evidence,
      lifecycle_state: $lifecycle_state,
      stop_reason: $stop_reason,
      next_entry: $next_entry,
      next_phase: $next_phase,
      human_input_required: $human_input_required
    }' <<<"$base_json"
}

build_execute_gate_result() {
  local review_status="$1"
  local verify_status="$2"
  local truth_sync_required="$3"
  local truth_sync_completed="$4"

  build_evaluation_verdict "$review_status" "$verify_status" "$truth_sync_required" "$truth_sync_completed"
}

execute_recovery_route() {
  local failure_kind="$1"
  local failure_count="$2"

  resolve_recovery_route "$failure_kind" "$failure_count"
}

usage() {
  cat <<'EOF'
Usage:
  execute-runner.sh entry-phase
  execute-runner.sh approval-status <plan-file>
  execute-runner.sh validate <plan-file>
  execute-runner.sh mode <plan-file>
  execute-runner.sh workspace-mode
  execute-runner.sh worktree-preflight-required <current-checkout|isolated-worktree> <decision-recorded>
  execute-runner.sh verification-commands <plan-file>
  execute-runner.sh allowed-touch-set <plan-file>
  execute-runner.sh truth-sync-required <plan-file>
  execute-runner.sh task-catalog <plan-file>
  execute-runner.sh task-ledger <plan-file>
  execute-runner.sh next-ready-task <ledger-json>
  execute-runner.sh ready-set <ledger-json>
  execute-runner.sh ready-batch <plan-file> <ledger-json> <parallel-group> <runtime-capacity> [semantic-routing|inherit-main|runtime-default]
  execute-runner.sh runtime-binding <plan-file> <ledger-json> <parallel-group> <runtime-capacity> [semantic-routing|inherit-main|runtime-default]
  execute-runner.sh controller-binding-envelope <plan-file> <ledger-json> <request-json>
  execute-runner.sh controller-converge <plan-file> <ledger-json> <task-id> <controller> <oracles-passed> <integration-passed> [changed-path ...]
  execute-runner.sh execution-result <plan-path> <ledger-json> <current-phase> <active-task-id-or-empty> <stop-reason> <review-status> <verify-status> <next-entry> <next-phase> <human-input-required> [workspace-mode]
  execute-runner.sh gate-result <review-status> <verify-status> <truth-sync-required> <truth-sync-completed>
  execute-runner.sh recovery-route <failure-kind> <failure-count>
EOF
}

main() {
  local command="${1:-}"

  case "$command" in
    entry-phase)
      execute_entry_phase
      ;;
    approval-status)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_plan_approval_status "$2"
      ;;
    validate)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      validate_execution_plan "$2"
      ;;
    mode)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_plan_mode "$2"
      ;;
    workspace-mode)
      [[ $# -eq 1 ]] || { usage >&2; return 1; }
      execution_workspace_mode
      ;;
    worktree-preflight-required)
      [[ $# -eq 3 ]] || { usage >&2; return 1; }
      execution_worktree_preflight_required "$2" "$3"
      ;;
    verification-commands)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_verification_commands "$2"
      ;;
    allowed-touch-set)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_allowed_touch_set "$2"
      ;;
    truth-sync-required)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_truth_sync_required "$2"
      ;;
    task-catalog)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_task_catalog "$2"
      ;;
    task-ledger)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_task_ledger "$2"
      ;;
    next-ready-task)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_next_ready_task "$2"
      ;;
    ready-set)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      execution_ready_set "$2"
      ;;
    ready-batch)
      [[ $# -ge 5 && $# -le 6 ]] || { usage >&2; return 1; }
      execution_ready_batch "$2" "$3" "$4" "$5" "${6:-}"
      ;;
    runtime-binding)
      [[ $# -ge 5 && $# -le 6 ]] || { usage >&2; return 1; }
      execution_runtime_binding "$2" "$3" "$4" "$5" "${6:-}"
      ;;
    controller-binding-envelope)
      [[ $# -eq 4 ]] || { usage >&2; return 1; }
      execution_controller_binding_envelope "$2" "$3" "$4"
      ;;
    controller-converge)
      [[ $# -ge 7 ]] || { usage >&2; return 1; }
      execution_controller_converge "$2" "$3" "$4" "$5" "$6" "$7" "${@:8}"
      ;;
    execution-result)
      [[ $# -ge 11 ]] || { usage >&2; return 1; }
      build_execution_result_json "${@:2}"
      ;;
    gate-result)
      [[ $# -eq 5 ]] || { usage >&2; return 1; }
      build_execute_gate_result "$2" "$3" "$4" "$5"
      ;;
    recovery-route)
      [[ $# -eq 3 ]] || { usage >&2; return 1; }
      execute_recovery_route "$2" "$3"
      ;;
    *)
      usage >&2
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
