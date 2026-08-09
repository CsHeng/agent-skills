#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=execute-runner.sh
source "$HARNESS_LIB_ROOT/execute-runner.sh"

fail() {
  printf 'test-execute-runner: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"
  rg -n -- "$pattern" "$file_ref" >/dev/null || fail "$message"
}

assert_json() {
  local json="$1"
  local expr="$2"
  local message="$3"

  if ! jq -e "$expr" <<<"$json" >/dev/null; then
    fail "$message"
  fi
}

main() {
  local tmp_dir design_file approved_plan pending_plan legacy_plan parallel_plan verdict ledger_file execution_result_json workspace_mode worktree_preflight
  local task_ledger_json=""
  local task_catalog_json=""
  local next_ready_task=""
  local binding_json=""
  local inherited_binding_json=""
  local topology_json=""
  local -a verification_commands allowed_touch_set
  local implement_skill=""

  case "$SKILL_SURFACE" in
    generated) implement_skill="$GENERATED_SKILLS_ROOT/implement-change/SKILL.md" ;;
    source) implement_skill="$ROOT_DIR/src/skills/workflows/implement-change/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(execute_entry_phase)" == "implement-serial" ]] || fail "execute entry phase should stay implement-serial"

  tmp_dir="$(mktemp -d)"
  design_file="$tmp_dir/design.md"
  approved_plan="$tmp_dir/approved-plan.md"
  pending_plan="$tmp_dir/pending-plan.md"
  legacy_plan="$tmp_dir/legacy-plan.md"
  parallel_plan="$tmp_dir/parallel-plan.md"

  cat >"$design_file" <<'EOF'
# Sample Design

## Status

Approved.

## Problem

Problem text.

## Goals

- Goal

## Non-Goals

- Non-goal

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: medium
- boundary_impact: low
- recommended_next_phase: plan

## Boundaries

- in_scope:
  - src/example.py
- out_of_scope:
  - src/other.py

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/example.py
  - src/helper.py
  - src/third.py
- test_file_refs:
  - tests/test_example.py
  - tests/test_helper.py
  - tests/test_third.py
EOF

  cat >"$approved_plan" <<'EOF'
# Approved Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-v1

## Implementation Scope

- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
  - `python -m pytest tests/test_example.py`

## Work Package Readiness

- milestone_objective: implement the approved example
- non_goals:
  - no production rollout
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: TDD for local behavior plus command verification
- acceptance_oracles:
  - `bash test.sh`
  - `python -m pytest tests/test_example.py`
- max_review_batches: 2
- subagent_ready: true

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: Implement Example

- task_id: task-1
- depends_on:
  - root
- scope_slice: core example implementation
- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
  - `python -m pytest tests/test_example.py`
- executor_mode: inline-serial
- task_review_depth: quick
- done_when:
  - implementation verification passes
- failure_policy: fix_forward
- [ ] Update `src/example.py`
- [ ] Run verification

## Recovery

- default_failure_policy: fix_forward
- backup_or_snapshot:
  - keep the pre-change data copy without automatic restore
EOF

  cat >"$pending_plan" <<'EOF'
# Pending Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-v1

## Implementation Scope

- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: implement the pending example
- non_goals:
  - no production rollout
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: TDD for local behavior plus command verification
- acceptance_oracles:
  - `bash test.sh`
- max_review_batches: 2
- subagent_ready: true

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: pending
- next_entry: implement-change

## Task 1: Implement Example

- task_id: task-1
- depends_on:
  - root
- scope_slice: pending example implementation
- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
- executor_mode: inline-serial
- task_review_depth: quick
- done_when:
  - verification passes
- failure_policy: fix_forward
- [ ] Update `src/example.py`

## Recovery

- default_failure_policy: fix_forward
EOF

  cat >"$legacy_plan" <<'EOF'
# Legacy Execution Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-v1

## Implementation Scope

- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: Legacy Example

- [ ] Step 1: Do work

## Rollback

- failure_kind: verification-failure
- rollback_entry: plan-change
EOF

  cat >"$parallel_plan" <<'EOF'
# Parallel Execution Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-08-01-v1

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: true
- truth_sync_required: true
- impl_file_refs:
  - src/example.py
  - src/helper.py
  - src/third.py
- test_file_refs:
  - tests/test_example.py
  - tests/test_helper.py
  - tests/test_third.py
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: bind a deterministic parallel batch
- non_goals:
  - no deployment
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: state-transition smoke tests
- acceptance_oracles:
  - `bash test.sh`
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: minimum of the plan and runtime limits

## Truth Sync Handoff

- stable_truth_refs:
  - src/example.py
- docs_governance_predicates:
  - none

## Parallel Batches

- batch_id: P1
- tasks:
  - task-1
  - task-2
  - task-3
- max_parallelism: 2
- convergence_task: controller

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: Example

- task_id: task-1
- depends_on:
  - root
- scope_slice: example implementation
- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: P1
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - example-state
- task_review_depth: full
- done_when:
  - example verification passes
- failure_policy: fix_forward
- [ ] Implement example

## Task 2: Helper

- task_id: task-2
- depends_on:
  - root
- scope_slice: helper implementation
- impl_file_refs:
  - src/helper.py
- test_file_refs:
  - tests/test_helper.py
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: P1
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - helper-state
- task_review_depth: full
- done_when:
  - helper verification passes
- failure_policy: fix_forward
- [ ] Implement helper

## Task 3: Third Work Item

- task_id: task-3
- depends_on:
  - root
- scope_slice: third implementation slice
- impl_file_refs:
  - src/third.py
- test_file_refs:
  - tests/test_third.py
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: P1
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: balanced
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - third-state
- task_review_depth: full
- done_when:
  - third verification passes
- failure_policy: fix_forward
- [ ] Implement third work item

## Recovery

- default_failure_policy: fix_forward
EOF

  validate_execution_plan "$approved_plan"
  if validate_execution_plan "$pending_plan" >/dev/null 2>&1; then
    fail "pending plan should not pass execution validation"
  fi
  if validate_execution_plan "$legacy_plan" >/dev/null 2>&1; then
    fail "legacy prose-only plan should not pass execution validation"
  fi
  validate_execution_plan "$parallel_plan"

  [[ "$(execution_plan_approval_status "$approved_plan")" == "approved" ]] || fail "approved plan status should resolve"
  [[ "$(execution_plan_mode "$approved_plan")" == "serial-first" ]] || fail "execution should default to serial-first"
  [[ "$(execution_truth_sync_required "$approved_plan")" == "true" ]] || fail "medium truth impact should require truth sync"
  workspace_mode="$(execution_workspace_mode)"
  [[ "$workspace_mode" == "current-checkout" || "$workspace_mode" == "isolated-worktree" ]] || fail "workspace mode should be normalized"
  [[ "$(execution_worktree_preflight_required "isolated-worktree" "false")" == "false" ]] || fail "isolated worktree should skip preflight reminder"
  worktree_preflight="$(execution_worktree_preflight_required "current-checkout" "false")"
  [[ "$worktree_preflight" == "true" ]] || fail "current checkout should require worktree preflight reminder before execution starts"

  mapfile -t verification_commands < <(execution_verification_commands "$approved_plan")
  [[ "${#verification_commands[@]}" -eq 2 ]] || fail "verification commands should be extracted"
  [[ "${verification_commands[0]}" == "bash test.sh" ]] || fail "verification commands should strip markdown quoting"
  [[ "${verification_commands[1]}" == "python -m pytest tests/test_example.py" ]] || fail "verification commands should preserve command text"

  mapfile -t allowed_touch_set < <(execution_allowed_touch_set "$approved_plan")
  [[ "${#allowed_touch_set[@]}" -eq 2 ]] || fail "allowed touch set should come from approved plan"
  [[ " ${allowed_touch_set[*]} " == *" src/example.py "* ]] || fail "allowed touch set should include impl refs"
  [[ " ${allowed_touch_set[*]} " == *" tests/test_example.py "* ]] || fail "allowed touch set should include test refs"

  task_catalog_json="$(execution_task_catalog "$approved_plan")"
  assert_json "$task_catalog_json" 'length == 1 and .[0].task_id == "task-1"' "task catalog should materialize approved task metadata"
  assert_json "$task_catalog_json" '.[0].failure_policy == "fix_forward" and .[0].rollback_trigger == [] and .[0].rollback_target == ""' "task catalog should preserve fix-forward without rollback metadata"

  task_ledger_json="$(execution_task_ledger "$approved_plan")"
  assert_json "$task_ledger_json" 'length == 1 and .[0].status == "ready"' "task ledger should start ready for dependency-free root task"

  ledger_file="$tmp_dir/task-ledger.json"
  printf '%s\n' "$task_ledger_json" >"$ledger_file"
  next_ready_task="$(execution_next_ready_task "$ledger_file")"
  [[ "$next_ready_task" == "task-1" ]] || fail "next ready task should resolve from the task ledger"

  task_ledger_json="$(execution_task_ledger "$parallel_plan")"
  printf '%s\n' "$task_ledger_json" >"$ledger_file"
  assert_json "$(execution_ready_set "$ledger_file")" 'map(.task_id) == ["task-1", "task-2", "task-3"]' "ready-set API should return all ready tasks in plan order"

  binding_json="$(execution_runtime_binding "$parallel_plan" "$ledger_file" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "bound" and .effective_width == 2 and .selected_task_ids == ["task-1", "task-2"]' "semantic routing should bind the complete safe frontier"
  assert_json "$binding_json" '.bindings[0].actor_kind == "subagent" and .bindings[0].model_instruction == "bind-runtime-equivalent-for-execution-profile"' "preferred delegation should use portable semantic binding instructions"
  declare -F execution_ready_batch >/dev/null || fail "ready-batch API should be available"

  inherited_binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$ledger_file" "P1" 4 "inherit-main")"
  assert_json "$inherited_binding_json" '.bindings | all(.model_instruction == "inherit-main-model" and .reasoning_instruction == "inherit-main-reasoning")' "inherit-main should change binding instructions"
  topology_json="$(jq -cS '.task_topology' <<<"$binding_json")"
  [[ "$topology_json" == "$(jq -cS '.task_topology' <<<"$inherited_binding_json")" ]] || fail "inherit-main must preserve byte-stable task topology"

  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$ledger_file" "P1" 4 "runtime-default")"
  assert_json "$binding_json" '.bindings | all(.model_instruction == "use-runtime-default-model")' "runtime-default should emit a portable runtime-default instruction"

  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$ledger_file" "P1" 1 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "serial-fallback" and .effective_width == 1 and .stop_reason == null' "allowed work should serialize with capacity evidence"
  assert_json "$binding_json" '.evidence[0].kind == "effective-capacity" and .evidence[0].runtime_capacity == 1' "serial fallback should record explicit capacity evidence"

  jq 'map(.parallel_policy = "required")' "$ledger_file" >"$tmp_dir/required-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/required-ledger.json" "P1" 1 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "capacity-stop" and .stop_reason == "parallel_capacity_required" and .effective_width == 0 and .selected_task_ids == []' "required work should return the typed capacity stop without a partial binding"

  jq 'map(.parallel_policy = "required")' "$ledger_file" >"$tmp_dir/required-three-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/required-three-ledger.json" "P1" 2 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "capacity-stop" and .stop_reason == "parallel_capacity_required" and .effective_width == 0 and .selected_task_ids == [] and .evidence[0].available_width == 2' "required work must bind the complete remaining frontier at once"

  jq '.[0].delegation_policy = "forbidden" | .[0].executor_mode = "main"' "$ledger_file" >"$tmp_dir/forbidden-ledger.json"
  binding_json="$(execution_runtime_binding "$parallel_plan" "$tmp_dir/forbidden-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "parallel-conflict" and .failure_kind == "parallel-conflict" and .recovery_phase == "dependency-freeze" and (.evidence | any(.kind == "plan-ledger-drift"))' "public runtime binding should reject ledger topology drift from the approved plan"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/forbidden-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.bindings[0].actor_kind == "main"' "forbidden delegation must never be relaxed"

  jq 'map(.delegation_policy = "forbidden" | .executor_mode = "main")' "$ledger_file" >"$tmp_dir/main-only-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/main-only-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "serial-fallback" and .effective_width == 1 and .selected_task_ids == ["task-1"] and (.bindings | all(.actor_kind == "main")) and .evidence[0].actor_capacity == 1' "one controller actor cannot be counted as multiple parallel workers"

  jq 'map(.delegation_policy = "forbidden" | .executor_mode = "main" | .parallel_policy = "required")' "$ledger_file" >"$tmp_dir/required-main-only-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/required-main-only-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "capacity-stop" and .stop_reason == "parallel_capacity_required" and .effective_width == 0 and .selected_task_ids == [] and .evidence[0].actor_capacity == 1' "required parallel work must stop when compliant actor capacity is insufficient"

  jq '.[1].impl_file_refs = ["src/example.py"]' "$ledger_file" >"$tmp_dir/write-conflict-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/write-conflict-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "parallel-conflict" and .failure_kind == "parallel-conflict" and .recovery_phase == "dependency-freeze" and (.evidence | any(.kind == "write-ref"))' "overlapping write refs should return deterministic conflict evidence"

  jq '.[1].resource_locks = ["example-state"]' "$ledger_file" >"$tmp_dir/lock-conflict-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/lock-conflict-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "parallel-conflict" and (.evidence | any(.kind == "resource-lock"))' "overlapping resource locks should conflict"

  jq '.[1].depends_on = ["task-1"]' "$ledger_file" >"$tmp_dir/dependency-conflict-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/dependency-conflict-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "parallel-conflict" and (.evidence | any(.kind == "dependency"))' "dependencies inside a runtime frontier should conflict"

  jq '.[1].isolation = "controller-checkout"' "$ledger_file" >"$tmp_dir/isolation-conflict-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/isolation-conflict-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "parallel-conflict" and (.evidence | any(.kind == "isolation"))' "parallel writes without worktree isolation should conflict"

  jq 'map(.impl_file_refs = ["none"] | .test_file_refs = ["none"] | .isolation = "shared-read-only")' "$ledger_file" >"$tmp_dir/read-only-ledger.json"
  binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/read-only-ledger.json" "P1" 4 "semantic-routing")"
  assert_json "$binding_json" '.outcome == "bound" and (.evidence | all(.kind != "isolation"))' "read-only tasks may share a checkout"

  jq '.[1].status = "pending"' "$ledger_file" >"$tmp_dir/incomplete-frontier-ledger.json"
  if execution_runtime_binding_from_validated_plan "$parallel_plan" "$tmp_dir/incomplete-frontier-ledger.json" "P1" 4 "semantic-routing" >/dev/null 2>&1; then
    fail "binding should wait without conflict until the complete frontier is ready"
  fi

  printf '%s\n' "$(execution_task_ledger "$approved_plan")" >"$ledger_file"
  execution_result_json="$(build_execution_result_json "$approved_plan" "$ledger_file" "implement-serial" "task-1" "task_blocked_requires_human" "pending" "pending" "implement-change" "implement-serial" "true" "$workspace_mode")"
  assert_json "$execution_result_json" '.stop_reason == "task_blocked_requires_human"' "execution result should preserve deterministic stop reason"
  assert_json "$execution_result_json" '.remaining_task_count == 1 and .completed_task_count == 0' "execution result should count task ledger state"
  assert_json "$execution_result_json" '.approved_plan_ref | endswith("approved-plan.md")' "execution result should bind the approved plan identity"
  assert_json "$execution_result_json" '.approved_design_ref | endswith("design.md")' "execution result should bind the approved design identity"
  assert_json "$execution_result_json" '.plan_sha256 | length == 64' "execution result should bind immutable plan content"
  assert_json "$execution_result_json" '.design_sha256 | length == 64' "execution result should bind immutable design content"
  assert_json "$execution_result_json" '.ledger_sha256 | length == 64' "execution result should bind immutable task evidence"
  assert_json "$execution_result_json" '.task_evidence | length == 1 and .[0].task_id == "task-1"' "execution result should embed its immutable task projection"
  assert_json "$execution_result_json" '.review_gate_ref != null and .verification_ref != null' "execution result should expose deterministic review and verification refs"
  assert_json "$execution_result_json" '.lifecycle_state == "implementation-pending"' "incomplete execution should expose the pending implementation state explicitly"

  jq 'map(
    .status = "done"
    | .convergence_verified = true
    | .convergence_actor = "controller"
    | .oracles_verified = true
    | .integration_verified = true
  )' "$ledger_file" >"$tmp_dir/completed-ledger.json"
  execution_result_json="$(build_execution_result_json "$approved_plan" "$tmp_dir/completed-ledger.json" "verify" "" "truth_sync_required" "pass" "pass" "sync-truth" "truth-sync" "false" "$workspace_mode")"
  assert_json "$execution_result_json" '.truth_sync_required == true and .stable_truth_refs == []' "legacy truth-affecting evidence should expose its missing stable truth scope"
  assert_json "$execution_result_json" '.stop_reason == "truth_sync_scope_required" and .lifecycle_state == "task-complete" and .next_entry == "plan-change"' "missing legacy truth scope should return a typed planning stop"

  verdict="$(build_execute_gate_result "pass" "pass" "true" "false")"
  assert_json "$verdict" '.verdict == "pass"' "execute gate should preserve pass verdict"
  assert_json "$verdict" '.ready_for_close == false' "truth sync pending should block close"

  verdict="$(build_execute_gate_result "pass" "pass" "true" "true")"
  assert_json "$verdict" '.ready_for_close == true' "truth sync completion should unlock close"

  [[ "$(execute_recovery_route "verification-failure" 1)" == "implement-serial" ]] || fail "first verification failure should stay in implementation"
  [[ "$(execute_recovery_route "verification-failure" 5)" == "implement-serial" ]] || fail "repeated verification failures must not widen the phase"

  assert_contains "$implement_skill" 'scripts/harness/execute-runner\.sh' "implementation skill should use its bundled runner"
  assert_contains "$implement_skill" 'approval-status.*approved' "implementation skill should require approved plan"
  assert_contains "$implement_skill" 'verification_scope' "implementation skill should expose the verification scope field"
  assert_contains "$implement_skill" 'review-change' "implementation skill should route code review through top-level review semantics"
  assert_contains "$implement_skill" 'failure_policy' "implementation skill should follow the approved failure policy"
}

main "$@"
