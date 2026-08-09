#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=close-runner.sh
source "$HARNESS_LIB_ROOT/close-runner.sh"

TEST_CLOSE_TMP=""

fail() {
  printf 'test-close-runner: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"

  rg -n -- "$pattern" "$file_ref" >/dev/null || fail "$message"
}

assert_json() {
  local json_value="$1"
  local expression="$2"
  local message="$3"

  if ! jq -e "$expression" <<<"$json_value" >/dev/null; then
    fail "$message"
  fi
}

write_close_fixture() {
  local fixture_root="$1"

  cat >"$fixture_root/design.md" <<'EOF'
# Close Design

## Change Classification

- truth_impact: high

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - docs/architecture/runtime.md
- test_file_refs:
  - tests/runtime.sh
EOF

  cat >"$fixture_root/plan.md" <<'EOF'
# Close Plan

## Upstream Design

- design_ref: design.md
- design_version: 1

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - docs/architecture/runtime.md
- test_file_refs:
  - tests/runtime.sh
- verification_scope:
  - bash tests/runtime.sh

## Work Package Readiness

- milestone_objective: verify terminal close
- non_goals:
  - no external close action
- future_phase:
  - none
- decision_status: ready_for_review
- oracle_strategy: structured close contract tests
- acceptance_oracles:
  - exact evidence closes once
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
- effective_concurrency: 1

## Task 1: Close Contract

- task_id: close-task
- depends_on:
  - none
- scope_slice: verify terminal close
- impl_file_refs:
  - docs/architecture/runtime.md
- test_file_refs:
  - tests/runtime.sh
- verification_scope:
  - bash tests/runtime.sh
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - close-contract
- task_review_depth: focused
- done_when:
  - close evidence passes
- failure_policy: fix_forward

## Truth Sync Handoff

- required_entry: sync-truth
- stable_truth_refs:
  - docs/architecture/runtime.md
- docs_governance_predicates:
  - none

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
EOF
}

write_close_truth_artifact() {
  local artifact_file="$1"
  local approval_state="$2"
  local execution_result_file="$3"
  local approved_design_ref=""
  local approved_plan_ref=""
  local review_gate_ref=""
  local verification_ref=""

  approved_design_ref="$(jq -r '.approved_design_ref' "$execution_result_file")"
  approved_plan_ref="$(jq -r '.approved_plan_ref' "$execution_result_file")"
  review_gate_ref="$(jq -r '.review_gate_ref' "$execution_result_file")"
  verification_ref="$(jq -r '.verification_ref' "$execution_result_file")"

  cat >"$artifact_file" <<EOF
# Close Truth Sync

## Evidence

- approved_design_ref: $approved_design_ref
- approved_plan_ref: $approved_plan_ref
- review_gate_ref: $review_gate_ref
- verification_ref: $verification_ref
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs:
  - docs/architecture/runtime.md
- stage_artifact_refs:
  - $approved_design_ref
  - $approved_plan_ref
- summary: Bind stable truth before terminal close.

## Human Gate

- approval_required: true
- approval_status: $approval_state
- next_entry: close-change
EOF
}

main() {
  local close_skill=""
  local tmp_dir=""
  local plan_file=""
  local ledger_file=""
  local execution_result_file=""
  local review_failure_file=""
  local low_truth_design_file=""
  local no_truth_plan_file=""
  local no_truth_execution_file=""
  local pending_artifact=""
  local approved_artifact=""
  local mismatched_artifact=""
  local decision_json=""

  case "$SKILL_SURFACE" in
    generated) close_skill="$GENERATED_SKILLS_ROOT/close-change/SKILL.md" ;;
    source) close_skill="$ROOT_DIR/src/skills/workflows/close-change/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(close_entry_phase)" == "close" ]] || fail "close entry phase should be close"
  is_valid_close_mode "merge" || fail "merge should be valid close mode"
  if is_valid_close_mode "destroy"; then
    fail "destroy should not be a valid close mode"
  fi

  tmp_dir="$(mktemp -d)"
  TEST_CLOSE_TMP="$tmp_dir"
  trap 'rm -rf -- "$TEST_CLOSE_TMP"' EXIT
  write_close_fixture "$tmp_dir"
  plan_file="$tmp_dir/plan.md"
  ledger_file="$tmp_dir/ledger.json"
  execution_result_file="$tmp_dir/execution.json"
  review_failure_file="$tmp_dir/execution-review-failure.json"
  low_truth_design_file="$tmp_dir/low-truth-design.md"
  no_truth_plan_file="$tmp_dir/no-truth-plan.md"
  no_truth_execution_file="$tmp_dir/no-truth-execution.json"
  pending_artifact="$tmp_dir/truth-pending.md"
  approved_artifact="$tmp_dir/truth-approved.md"
  mismatched_artifact="$tmp_dir/truth-mismatch.md"

  execution_task_ledger "$plan_file" | jq 'map(
    .status = "done"
    | .convergence_verified = true
    | .convergence_actor = "controller"
    | .oracles_verified = true
    | .integration_verified = true
  )' >"$ledger_file"
  build_execution_result_json "$plan_file" "$ledger_file" "verify" "" "truth_sync_required" "pass" "pass" "sync-truth" "truth-sync" "false" "current-checkout" >"$execution_result_file"
  write_close_truth_artifact "$pending_artifact" pending "$execution_result_file"
  write_close_truth_artifact "$approved_artifact" approved "$execution_result_file"
  cp "$approved_artifact" "$mismatched_artifact"
  sed -i 's/verification:/verification-mismatch:/' "$mismatched_artifact"

  decision_json="$(build_close_decision merge "$plan_file" "$execution_result_file")"
  assert_json "$decision_json" '.decision == "blocked" and .block_reason == "truth-sync-artifact-required" and .next_entry == "sync-truth"' "missing truth artifact should block close"
  decision_json="$(build_close_decision merge "$plan_file" "$execution_result_file" "$pending_artifact")"
  assert_json "$decision_json" '.decision == "blocked" and .block_reason == "truth-sync-approval-pending" and .next_entry == "sync-truth"' "pending truth approval should block close"
  decision_json="$(build_close_decision merge "$plan_file" "$execution_result_file" "$mismatched_artifact")"
  assert_json "$decision_json" '.decision == "blocked" and .block_reason == "truth-sync-evidence-mismatch" and .next_entry == "sync-truth"' "mismatched truth evidence should fail closed"

  decision_json="$(build_close_decision cleanup "$plan_file" "$execution_result_file" "$approved_artifact")"
  assert_json "$decision_json" '.decision == "approved" and .close_allowed == true and .terminal_state == "closed" and .next_entry == null' "approved exact evidence should produce one terminal close result"
  assert_json "$decision_json" '.close_mode == "cleanup" and .block_reason == null' "close mode should remain judgment metadata"
  validate_close_change cleanup "$plan_file" "$execution_result_file" "$approved_artifact"

  cp "$tmp_dir/design.md" "$low_truth_design_file"
  sed -i 's/truth_impact: high/truth_impact: low/' "$low_truth_design_file"
  cp "$plan_file" "$no_truth_plan_file"
  sed -i 's/design_ref: design.md/design_ref: low-truth-design.md/' "$no_truth_plan_file"
  sed -i 's/truth_sync_required: true/truth_sync_required: false/' "$no_truth_plan_file"
  build_execution_result_json "$no_truth_plan_file" "$ledger_file" "verify" "" "ready_for_close" "pass" "pass" "close-change" "close" "true" "current-checkout" >"$no_truth_execution_file"
  decision_json="$(build_close_decision cleanup "$no_truth_plan_file" "$no_truth_execution_file")"
  assert_json "$decision_json" '.decision == "approved" and .truth_sync_required == false and .terminal_state == "closed" and .next_entry == null' "derived no-truth evidence should close without a truth artifact"

  jq '.review_status = "needs-fixes" | .review_gate_ref = ("review:" + .plan_sha256 + ":" + .ledger_sha256 + ":needs-fixes") | .lifecycle_state = "task-complete"' "$execution_result_file" >"$review_failure_file"
  decision_json="$(build_close_decision release "$plan_file" "$review_failure_file" "$approved_artifact")"
  assert_json "$decision_json" '.decision == "blocked" and .block_reason == "implementation-review-incomplete" and .next_entry == "implement-change"' "review failure should return to implementation"

  decision_json="$(build_close_decision merge pass pass true true)"
  assert_json "$decision_json" '.decision == "blocked" and .close_allowed == false' "caller-supplied booleans must not approve close"

  assert_contains "$close_skill" 'scripts/harness/close-runner\.sh' "close skill should use its bundled runner"
  assert_contains "$close_skill" 'approved-plan.*execution-result-json' "close skill should require artifact-bound execution evidence"
}

main "$@"
