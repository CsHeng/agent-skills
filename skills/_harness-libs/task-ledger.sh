#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=skills/_harness-libs/contracts.sh
source "$SCRIPT_DIR/contracts.sh"
# shellcheck source=skills/_harness-libs/plan-runner.sh
source "$SCRIPT_DIR/plan-runner.sh"

strip_wrapping_backticks() {
  sed -E 's/^`(.*)`$/\1/'
}

extract_task_list_field() {
  local plan_file="$1"
  local section="$2"
  local key="$3"

  awk -v section="$section" -v key="$key" '
    BEGIN {
      in_section = 0
      in_key = 0
    }
    $0 ~ "^##[[:space:]]+" section "[[:space:]]*$" {
      in_section = 1
      in_key = 0
      next
    }
    in_section && $0 ~ "^##[[:space:]]+" {
      exit
    }
    in_section && $0 ~ "^[[:space:]]*-[[:space:]]*" key ":[[:space:]]*$" {
      in_key = 1
      next
    }
    in_section && in_key && $0 ~ "^-[[:space:]]*[A-Za-z0-9_-]+:[[:space:]]*.*$" {
      in_key = 0
      next
    }
    in_section && in_key && $0 ~ "^-[[:space:]]*\\[[ xX]\\]" {
      in_key = 0
      next
    }
    in_section && in_key && $0 ~ "^[[:space:]]*-[[:space:]]+" {
      line = $0
      sub(/^[[:space:]]*-[[:space:]]+/, "", line)
      print line
      next
    }
  ' "$plan_file"
}

task_title_from_section() {
  local section="$1"
  printf '%s\n' "${section#Task [0-9]*: }"
}

task_depends_on_json() {
  local plan_file="$1"
  local section="$2"

  extract_task_list_field "$plan_file" "$section" "depends_on" \
    | awk 'NF > 0' \
    | jq -R . \
    | jq -s .
}

task_list_field_json() {
  local plan_file="$1"
  local section="$2"
  local key="$3"

  extract_task_list_field "$plan_file" "$section" "$key" \
    | awk 'NF > 0' \
    | strip_wrapping_backticks \
    | jq -R . \
    | jq -s .
}

task_is_dependency_free() {
  local depends_on_json="$1"

  jq -e '
    length == 0 or
    all(.[]; . == "root" or . == "none")
  ' <<<"$depends_on_json" >/dev/null
}

task_catalog_json() {
  local plan_file="$1"
  local convergence_required=false
  local section=""
  local task_title=""
  local task_id=""
  local scope_slice=""
  local executor_mode=""
  local parallel_group=""
  local parallel_policy=""
  local delegation_policy=""
  local execution_profile=""
  local reasoning_profile=""
  local isolation_mode=""
  local task_review_depth=""
  local failure_policy=""
  local rollback_target=""
  local depends_on_json="[]"
  local impl_refs_json="[]"
  local test_refs_json="[]"
  local verification_json="[]"
  local done_when_json="[]"
  local rollback_trigger_json="[]"
  local rollback_verification_json="[]"
  local resource_locks_json="[]"

  validate_execution_grade_plan_artifact "$plan_file" >/dev/null || return 1
  if plan_uses_v2_contract "$plan_file"; then
    convergence_required=true
  fi

  while IFS= read -r section; do
    [[ -n "$section" ]] || continue
    task_title="$(task_title_from_section "$section")"
    task_id="$(extract_markdown_scalar "$plan_file" "$section" "task_id")"
    scope_slice="$(extract_markdown_scalar "$plan_file" "$section" "scope_slice")"
    executor_mode="$(extract_markdown_scalar "$plan_file" "$section" "executor_mode")"
    parallel_group="$(extract_markdown_scalar "$plan_file" "$section" "parallel_group" | strip_wrapping_backticks)"
    parallel_policy="$(extract_markdown_scalar "$plan_file" "$section" "parallel_policy" | strip_wrapping_backticks)"
    delegation_policy="$(extract_markdown_scalar "$plan_file" "$section" "delegation_policy" | strip_wrapping_backticks)"
    execution_profile="$(extract_markdown_scalar "$plan_file" "$section" "execution_profile" | strip_wrapping_backticks)"
    reasoning_profile="$(extract_markdown_scalar "$plan_file" "$section" "reasoning_profile" | strip_wrapping_backticks)"
    isolation_mode="$(extract_markdown_scalar "$plan_file" "$section" "isolation" | strip_wrapping_backticks)"
    task_review_depth="$(extract_markdown_scalar "$plan_file" "$section" "task_review_depth")"
    failure_policy="$(extract_markdown_scalar "$plan_file" "$section" "failure_policy")"
    rollback_target="$(extract_markdown_scalar "$plan_file" "$section" "rollback_target")"
    depends_on_json="$(task_depends_on_json "$plan_file" "$section")"
    impl_refs_json="$(task_list_field_json "$plan_file" "$section" "impl_file_refs")"
    test_refs_json="$(task_list_field_json "$plan_file" "$section" "test_file_refs")"
    verification_json="$(task_list_field_json "$plan_file" "$section" "verification_scope")"
    done_when_json="$(task_list_field_json "$plan_file" "$section" "done_when")"
    rollback_trigger_json="$(task_list_field_json "$plan_file" "$section" "rollback_trigger")"
    rollback_verification_json="$(task_list_field_json "$plan_file" "$section" "rollback_verification")"
    resource_locks_json="$(task_list_field_json "$plan_file" "$section" "resource_locks")"

    jq -n \
      --arg section "$section" \
      --arg task_title "$task_title" \
      --arg task_id "$task_id" \
      --arg scope_slice "$scope_slice" \
      --arg executor_mode "$executor_mode" \
      --arg parallel_group "$parallel_group" \
      --arg parallel_policy "$parallel_policy" \
      --arg delegation_policy "$delegation_policy" \
      --arg execution_profile "$execution_profile" \
      --arg reasoning_profile "$reasoning_profile" \
      --arg isolation "$isolation_mode" \
      --arg task_review_depth "$task_review_depth" \
      --arg failure_policy "$failure_policy" \
      --arg rollback_target "$rollback_target" \
      --argjson depends_on "$depends_on_json" \
      --argjson impl_file_refs "$impl_refs_json" \
      --argjson test_file_refs "$test_refs_json" \
      --argjson verification_commands "$verification_json" \
      --argjson done_when "$done_when_json" \
      --argjson rollback_trigger "$rollback_trigger_json" \
      --argjson rollback_verification "$rollback_verification_json" \
      --argjson resource_locks "$resource_locks_json" \
      --argjson convergence_required "$convergence_required" \
      '{
        section: $section,
        title: $task_title,
        task_id: $task_id,
        depends_on: $depends_on,
        scope_slice: $scope_slice,
        impl_file_refs: $impl_file_refs,
        test_file_refs: $test_file_refs,
        verification_commands: $verification_commands,
        executor_mode: $executor_mode,
        parallel_group: $parallel_group,
        parallel_policy: $parallel_policy,
        delegation_policy: $delegation_policy,
        execution_profile: $execution_profile,
        reasoning_profile: $reasoning_profile,
        isolation: $isolation,
        resource_locks: $resource_locks,
        convergence_required: $convergence_required,
        task_review_depth: $task_review_depth,
        done_when: $done_when,
        failure_policy: $failure_policy,
        rollback_trigger: $rollback_trigger,
        rollback_target: $rollback_target,
        rollback_verification: $rollback_verification
      }'
  done < <(list_plan_task_sections "$plan_file") | jq -s .
}

task_ledger_json() {
  local plan_file="$1"
  local catalog_json="[]"

  validate_execution_grade_plan_artifact "$plan_file" >/dev/null || return 1
  catalog_json="$(task_catalog_json "$plan_file")"

  jq '
    map(
      . as $task
      | $task + {
          status: (
            if (($task.depends_on | length) == 0) or
               ($task.depends_on | all(. == "root" or . == "none"))
            then "ready"
            else "pending"
            end
          ),
          attempt_count: 0,
          review_attempt_count: 0,
          failure_count: 0,
          last_failure_kind: "",
          active_impl_file_refs: $task.impl_file_refs,
          active_test_file_refs: $task.test_file_refs,
          started_at: null,
          completed_at: null,
          convergence_verified: false,
          convergence_actor: null,
          verified_changed_paths: [],
          oracles_verified: false,
          integration_verified: false,
          notes: ""
        }
    )
  ' <<<"$catalog_json"
}

task_ledger_next_ready_task_id() {
  local ledger_file="$1"

  jq -r '.[] | select(.status == "ready") | .task_id' "$ledger_file" | head -n 1
}

task_ledger_ready_set_json() {
  local ledger_file="$1"

  jq '[.[] | select(.status == "ready")]' "$ledger_file"
}

task_ledger_set_status() {
  local ledger_file="$1"
  local task_id="$2"
  local task_state="$3"
  local timestamp=""

  is_valid_task_status "$task_state" || {
    printf 'invalid task status: %s\n' "$task_state" >&2
    return 1
  }

  if [[ "$task_state" == "done" ]] && jq -e --arg task_id "$task_id" '.[] | select(.task_id == $task_id and .convergence_required == true)' "$ledger_file" >/dev/null; then
    printf 'version-2 task completion requires controller convergence: %s\n' "$task_id" >&2
    return 1
  fi

  timestamp="$(date -u +%FT%TZ)"

  jq \
    --arg task_id "$task_id" \
    --arg task_state "$task_state" \
    --arg timestamp "$timestamp" \
    '
    map(
      if .task_id == $task_id then
        .status = $task_state
        | .started_at = (
            if $task_state == "in_progress" and .started_at == null then
              $timestamp
            else
              .started_at
            end
          )
        | .completed_at = (
            if $task_state == "done" then
              $timestamp
            else
              .completed_at
            end
          )
      else
        .
      end
    )
    ' "$ledger_file"
}

task_ledger_refresh_ready_states() {
  local ledger_file="$1"

  jq '
    def is_converged_done:
      .status == "done" and
      (
        ((.convergence_required // false) == false) or
        (
          .convergence_verified == true and
          .oracles_verified == true and
          .integration_verified == true
        )
      );
    def completed_task_ids:
      . as $ledger
      | [
          $ledger[] as $task
          | select($task | is_converged_done)
          | select(
              (($task.convergence_required // false) == false) or
              (($task.parallel_group // "") == "") or
              (($task.parallel_group // "") == "none") or
              (
                [
                  $ledger[]
                  | select(.parallel_group == $task.parallel_group)
                ]
                | all(is_converged_done)
              )
            )
          | $task.task_id
        ];

    . as $ledger
    | completed_task_ids as $done
    | map(
        if .status == "pending" then
          if ((.depends_on | length) == 0) or
             (.depends_on | all(. as $dep | $dep == "root" or $dep == "none" or ($done | index($dep))))
          then
            .status = "ready"
          else
            .
          end
        else
          .
        end
      )
  ' "$ledger_file"
}

task_ledger_controller_converge() {
  local plan_file="$1"
  local ledger_file="$2"
  local task_id="$3"
  local convergence_actor="$4"
  local oracles_passed="$5"
  local integration_passed="$6"
  shift 6

  local timestamp=""
  local current_task_state=""
  local changed_refs_json="[]"
  local converged_json=""

  validate_execution_grade_plan_artifact "$plan_file" >/dev/null || return 1
  [[ "$convergence_actor" == "controller" ]] || {
    printf 'only the controller may converge task results: %s\n' "$task_id" >&2
    return 1
  }
  case "$oracles_passed:$integration_passed" in
    true:true) ;;
    *)
      printf 'task convergence requires passing task oracles and integration evidence: %s\n' "$task_id" >&2
      return 1
      ;;
  esac

  current_task_state="$(jq -r --arg task_id "$task_id" '.[] | select(.task_id == $task_id) | .status' "$ledger_file")"
  [[ "$current_task_state" == "in_review" ]] || {
    printf 'task must be in_review before controller convergence (%s): %s\n' "$task_id" "$current_task_state" >&2
    return 1
  }

  assert_task_change_boundary "$plan_file" "$task_id" "$@" || return 1
  changed_refs_json="$(printf '%s\n' "$@" | awk 'NF > 0' | jq -R . | jq -s .)"
  timestamp="$(date -u +%FT%TZ)"

  converged_json="$(jq \
    --arg task_id "$task_id" \
    --arg timestamp "$timestamp" \
    --argjson changed_refs "$changed_refs_json" \
    '
    map(
      if .task_id == $task_id then
        .status = "done"
        | .completed_at = $timestamp
        | .convergence_verified = true
        | .convergence_actor = "controller"
        | .verified_changed_paths = $changed_refs
        | .oracles_verified = true
        | .integration_verified = true
      else
        .
      end
    )
    ' "$ledger_file")"

  task_ledger_refresh_ready_states <(printf '%s\n' "$converged_json")
}

build_execution_result() {
  local plan_path="$1"
  local ledger_file="$2"
  local current_phase="$3"
  local active_task_id="$4"
  local stop_reason="$5"
  local review_status="$6"
  local verify_status="$7"
  local next_entry="$8"
  local next_phase="$9"
  local human_input_required="${10}"
  local workspace_mode="${11:-current-checkout}"

  is_valid_execution_stop_reason "$stop_reason" || {
    printf 'invalid execution stop reason: %s\n' "$stop_reason" >&2
    return 1
  }

  case "$human_input_required" in
    true|false) ;;
    *)
      printf 'invalid human_input_required flag: %s\n' "$human_input_required" >&2
      return 1
      ;;
  esac

  jq -n \
    --arg execution_unit "plan" \
    --arg plan_path "$plan_path" \
    --arg current_phase "$current_phase" \
    --arg active_task_id "$active_task_id" \
    --arg stop_reason "$stop_reason" \
    --arg review_status "$review_status" \
    --arg verify_status "$verify_status" \
    --arg next_entry "$next_entry" \
    --arg next_phase "$next_phase" \
    --arg workspace_mode "$workspace_mode" \
    --argjson human_input_required "$human_input_required" \
    --argjson completed_task_count "$(jq '[.[] | select(.status == "done")] | length' "$ledger_file")" \
    --argjson remaining_task_count "$(jq '[.[] | select(.status != "done")] | length' "$ledger_file")" \
    --argjson total_task_count "$(jq 'length' "$ledger_file")" \
    '{
      execution_unit: $execution_unit,
      plan_path: $plan_path,
      current_phase: $current_phase,
      active_task_id: (if $active_task_id == "" then null else $active_task_id end),
      completed_task_count: $completed_task_count,
      remaining_task_count: $remaining_task_count,
      total_task_count: $total_task_count,
      stop_reason: $stop_reason,
      review_status: $review_status,
      verify_status: $verify_status,
      next_entry: $next_entry,
      next_phase: $next_phase,
      human_input_required: $human_input_required,
      workspace_mode: $workspace_mode
    }'
}

usage() {
  cat <<'EOF'
Usage:
  task-ledger.sh catalog <plan-file>
  task-ledger.sh init <plan-file>
  task-ledger.sh next-ready <ledger-json>
  task-ledger.sh ready-set <ledger-json>
  task-ledger.sh set-status <ledger-json> <task-id> <status>
  task-ledger.sh refresh-ready <ledger-json>
  task-ledger.sh controller-converge <plan-file> <ledger-json> <task-id> <controller> <oracles-passed> <integration-passed> [changed-path ...]
  task-ledger.sh execution-result <plan-path> <ledger-json> <current-phase> <active-task-id-or-empty> <stop-reason> <review-status> <verify-status> <next-entry> <next-phase> <human-input-required> [workspace-mode]
EOF
}

main() {
  local command="${1:-}"

  case "$command" in
    catalog)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      task_catalog_json "$2"
      ;;
    init)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      task_ledger_json "$2"
      ;;
    next-ready)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      task_ledger_next_ready_task_id "$2"
      ;;
    ready-set)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      task_ledger_ready_set_json "$2"
      ;;
    set-status)
      [[ $# -eq 4 ]] || { usage >&2; return 1; }
      task_ledger_set_status "$2" "$3" "$4"
      ;;
    refresh-ready)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      task_ledger_refresh_ready_states "$2"
      ;;
    controller-converge)
      [[ $# -ge 7 ]] || { usage >&2; return 1; }
      task_ledger_controller_converge "$2" "$3" "$4" "$5" "$6" "$7" "${@:8}"
      ;;
    execution-result)
      [[ $# -ge 11 ]] || { usage >&2; return 1; }
      build_execution_result "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12:-current-checkout}"
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
