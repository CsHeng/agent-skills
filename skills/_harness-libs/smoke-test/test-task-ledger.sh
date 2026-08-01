#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/skills/_harness-libs}"

# shellcheck source=skills/_harness-libs/task-ledger.sh
source "$HARNESS_LIB_ROOT/task-ledger.sh"

fail() {
  printf 'test-task-ledger: %s\n' "$*" >&2
  exit 1
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
  local tmp_dir design_file plan_file legacy_plan ledger_file result_json next_ready
  local ledger_json=""
  local updated_json=""

  tmp_dir="$(mktemp -d)"
  design_file="$tmp_dir/design.md"
  plan_file="$tmp_dir/plan.md"
  legacy_plan="$tmp_dir/legacy-plan.md"
  ledger_file="$tmp_dir/ledger.json"

  cat >"$design_file" <<'EOF'
# Sample Design

## Status

- approval_status: approved

## Problem

Problem.

## Goals

- Goal

## Non-Goals

- Non-goal

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: low
- boundary_impact: medium
- recommended_next_phase: plan

## Boundaries

- in_scope:
  - src/example

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/example
  - src/helper
  - src/followup
- test_file_refs:
  - tests/example
  - tests/helper
  - tests/followup
EOF

cat >"$plan_file" <<'EOF'
# Sample Task-Ledger Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-09-initial

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: true
- impl_file_refs:
  - src/example
  - src/helper
  - src/followup
- test_file_refs:
  - tests/example
  - tests/helper
  - tests/followup
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: build a task ledger for the example implementation
- non_goals:
  - no production rollout
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: TDD for local behavior plus command verification
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
- effective_concurrency: bounded by the approved batch and runtime capacity

## Parallel Batches

- batch_id: P1
- tasks:
  - task-1
  - task-2
- max_parallelism: 2
- convergence_task: controller

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: Core Example

- task_id: task-1
- depends_on:
  - root
- scope_slice: core example work
- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
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
  - example-core
- task_review_depth: quick
- done_when:
  - `bash test.sh` succeeds
- failure_policy: fix_forward
- [ ] Step 1: Implement core example

## Task 2: Independent Helper

- task_id: task-2
- depends_on:
  - root
- scope_slice: independent helper work
- impl_file_refs:
  - src/helper
- test_file_refs:
  - tests/helper
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
  - example-helper
- task_review_depth: quick
- done_when:
  - helper verification passes
- failure_policy: fix_forward
- [ ] Step 1: Implement helper

## Task 3: Dependent Follow-up

- task_id: task-3
- depends_on:
  - task-1
- scope_slice: dependent follow-up
- impl_file_refs:
  - src/followup
- test_file_refs:
  - tests/followup
- verification_scope:
  - `bash test.sh`
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - example-followup
- task_review_depth: quick
- done_when:
  - follow-up verification passes
- failure_policy: guarded_rollback
- rollback_trigger:
  - follow-up cutover loses the declared management path
- rollback_target: tested pre-change follow-up state
- rollback_verification:
  - follow-up management path passes after restore
- [ ] Step 1: Implement follow-up

## Recovery

- default_failure_policy: fix_forward

## Rollback

- guarded_task_ids:
  - task-3
EOF

  cat >"$legacy_plan" <<'EOF'
# Legacy Task-Ledger Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-09-initial

## Implementation Scope

- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
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

- failure_kind: plan-incompleteness
- rollback_entry: design-change
EOF

  ledger_json="$(task_ledger_json "$plan_file")"
  assert_json "$ledger_json" 'length == 3' "task ledger should include all tasks"
  assert_json "$ledger_json" '.[0].task_id == "task-1" and .[0].status == "ready"' "first task should start ready"
  assert_json "$ledger_json" '.[0].parallel_group == "P1" and .[0].parallel_policy == "allowed" and .[0].delegation_policy == "preferred"' "task ledger should preserve scheduling policy metadata"
  assert_json "$ledger_json" '.[0].execution_profile == "deep" and .[0].reasoning_profile == "deep" and .[0].isolation == "isolated-worktree"' "task ledger should preserve portable binding metadata"
  assert_json "$ledger_json" '.[0].resource_locks == ["example-core"]' "task ledger should preserve resource locks"
  assert_json "$ledger_json" '.[0].failure_policy == "fix_forward" and .[0].rollback_trigger == []' "fix-forward task should have no rollback metadata"
  assert_json "$ledger_json" '.[1].task_id == "task-2" and .[1].status == "ready"' "independent task should start ready"
  assert_json "$ledger_json" '.[2].task_id == "task-3" and .[2].status == "pending"' "dependent task should start pending"
  assert_json "$ledger_json" '.[2].failure_policy == "guarded_rollback" and (.[2].rollback_trigger | length) == 1 and .[2].rollback_target != "" and (.[2].rollback_verification | length) == 1' "guarded task should preserve exact rollback metadata"

  printf '%s\n' "$ledger_json" >"$ledger_file"
  next_ready="$(task_ledger_next_ready_task_id "$ledger_file")"
  [[ "$next_ready" == "task-1" ]] || fail "next ready task should be task-1"
  updated_json="$(task_ledger_ready_set_json "$ledger_file")"
  assert_json "$updated_json" 'map(.task_id) == ["task-1", "task-2"]' "ready set should preserve stable plan order"

  updated_json="$(task_ledger_set_status "$ledger_file" "task-1" "in_progress")"
  assert_json "$updated_json" '.[] | select(.task_id == "task-1") | .status == "in_progress"' "task-1 should enter in_progress"
  printf '%s\n' "$updated_json" >"$ledger_file"

  updated_json="$(task_ledger_set_status "$ledger_file" "task-1" "in_review")"
  assert_json "$updated_json" '.[] | select(.task_id == "task-1") | .status == "in_review"' "task-1 should enter in_review"
  printf '%s\n' "$updated_json" >"$ledger_file"

  if task_ledger_set_status "$ledger_file" "task-1" "done" >/dev/null 2>&1; then
    fail "version-2 task completion must require controller convergence"
  fi

  result_json="$(jq 'map(.convergence_required = false | if .task_id == "task-1" then .status = "done" else . end)' "$ledger_file")"
  result_json="$(task_ledger_refresh_ready_states <(printf '%s\n' "$result_json"))"
  assert_json "$result_json" '.[] | select(.task_id == "task-3") | .status == "ready"' "legacy completion should continue to unlock dependents"

  if task_ledger_controller_converge "$plan_file" "$ledger_file" "task-1" "worker" "true" "true" "src/example/main.sh" >/dev/null 2>&1; then
    fail "worker must not converge task results"
  fi
  updated_json="$(task_ledger_controller_converge "$plan_file" "$ledger_file" "task-1" "controller" "true" "true" "src/example/main.sh" "tests/example/main.sh")"
  assert_json "$updated_json" '.[] | select(.task_id == "task-1") | .status == "done" and .convergence_verified == true and .oracles_verified == true and .integration_verified == true and .convergence_actor == "controller"' "controller convergence should record evidence"
  assert_json "$updated_json" '.[] | select(.task_id == "task-3") | .status == "pending"' "partial parallel-group convergence must not advance dependents"
  printf '%s\n' "$updated_json" >"$ledger_file"

  updated_json="$(task_ledger_set_status "$ledger_file" "task-2" "in_progress")"
  printf '%s\n' "$updated_json" >"$ledger_file"
  updated_json="$(task_ledger_set_status "$ledger_file" "task-2" "in_review")"
  printf '%s\n' "$updated_json" >"$ledger_file"
  updated_json="$(task_ledger_controller_converge "$plan_file" "$ledger_file" "task-2" "controller" "true" "true" "src/helper/main.sh" "tests/helper/main.sh")"
  assert_json "$updated_json" '.[] | select(.task_id == "task-3") | .status == "ready"' "complete controller-verified parallel-group convergence should advance dependents"
  printf '%s\n' "$updated_json" >"$ledger_file"

  if task_ledger_json "$legacy_plan" >/dev/null 2>&1; then
    fail "legacy prose-only plan should not materialize a task ledger"
  fi

  result_json="$(build_execution_result "$plan_file" "$ledger_file" "implement-serial" "task-2" "task_blocked_requires_human" "pending" "pending" "implement-change" "implement-serial" "true" "current-checkout")"
  assert_json "$result_json" '.completed_task_count == 2' "execution result should report completed task count"
  assert_json "$result_json" '.remaining_task_count == 1' "execution result should report remaining task count"
  assert_json "$result_json" '.stop_reason == "task_blocked_requires_human"' "execution result should preserve stop reason"
  assert_json "$result_json" '.human_input_required == true' "execution result should preserve human-input flag"
}

main "$@"
