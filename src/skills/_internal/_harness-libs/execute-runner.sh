#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=skills/_harness-libs/artifact-dag.sh
source "$SCRIPT_DIR/artifact-dag.sh"
# shellcheck source=skills/_harness-libs/design-runner.sh
source "$SCRIPT_DIR/design-runner.sh"
# shellcheck source=skills/_harness-libs/plan-runner.sh
source "$SCRIPT_DIR/plan-runner.sh"
# shellcheck source=skills/_harness-libs/evaluation-gate.sh
source "$SCRIPT_DIR/evaluation-gate.sh"
# shellcheck source=skills/_harness-libs/recovery-routing.sh
source "$SCRIPT_DIR/recovery-routing.sh"
# shellcheck source=skills/_harness-libs/task-ledger.sh
source "$SCRIPT_DIR/task-ledger.sh"
# shellcheck source=skills/_harness-libs/phase-engine.sh
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
    --argjson effective_width "$effective_width" \
    --argjson binding_evidence "$binding_evidence_json" \
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
    | {
        outcome: $outcome,
        group_id: $group_id,
        model_policy: $model_policy,
        runtime_capacity: $runtime_capacity,
        plan_max_parallelism: $plan_max_parallelism,
        effective_width: $effective_width,
        stop_reason: (if $stop_reason == "" then null else $stop_reason end),
        failure_kind: (if $outcome == "parallel-conflict" then "parallel-conflict" else null end),
        recovery_phase: (if $outcome == "parallel-conflict" then "dependency-freeze" else null end),
        ready_frontier_task_ids: [$ready_frontier[] | .task_id],
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
        evidence: $binding_evidence
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
      model_policy: $model_policy,
      runtime_capacity: $runtime_capacity,
      plan_max_parallelism: $plan_max_parallelism,
      effective_width: 0,
      stop_reason: null,
      failure_kind: "parallel-conflict",
      recovery_phase: "dependency-freeze",
      ready_frontier_task_ids: [],
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

execution_ready_batch() {
  execution_runtime_binding "$@"
}

execution_controller_converge() {
  task_ledger_controller_converge "$@"
}

build_execution_result_json() {
  build_execution_result "$@"
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
