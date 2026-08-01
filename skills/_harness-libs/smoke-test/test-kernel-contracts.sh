#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/skills/_harness-libs}"

# shellcheck source=skills/_harness-libs/contracts.sh
source "$HARNESS_LIB_ROOT/contracts.sh"

fail() {
  printf 'test-kernel-contracts: %s\n' "$*" >&2
  exit 1
}

assert_eq() {
  local actual="$1"
  local expected="$2"
  local message="$3"

  [[ "$actual" == "$expected" ]] || fail "$message: expected=$expected actual=$actual"
}

assert_invalid() {
  local fn="$1"
  local value="$2"

  if "$fn" "$value"; then
    fail "$fn unexpectedly accepted $value"
  fi
}

assert_sequence() {
  local actual="$1"
  local expected="$2"
  local message="$3"

  [[ "$actual" == "$expected" ]] || fail "$message"
}

main() {
  local entries phases classes design_strengths verdicts artifact_classes failure_policies failure_kinds
  local plan_contract_versions parallel_policies delegation_policies execution_profiles reasoning_profiles
  local isolation_modes model_policies actor_kinds binding_outcomes execution_stop_reasons

  entries="$(printf '%s\n' "${HARNESS_ENTRIES[@]}")"
  phases="$(printf '%s\n' "${HARNESS_PHASES[@]}")"
  classes="$(printf '%s\n' "${HARNESS_CHANGE_CLASSES[@]}")"
  design_strengths="$(printf '%s\n' "${HARNESS_DESIGN_STRENGTHS[@]}")"
  verdicts="$(printf '%s\n' "${HARNESS_VERDICTS[@]}")"
  artifact_classes="$(printf '%s\n' "${HARNESS_ARTIFACT_CLASSES[@]}")"
  failure_policies="$(printf '%s\n' "${HARNESS_FAILURE_POLICIES[@]}")"
  plan_contract_versions="$(printf '%s\n' "${HARNESS_PLAN_CONTRACT_VERSIONS[@]}")"
  parallel_policies="$(printf '%s\n' "${HARNESS_PARALLEL_POLICIES[@]}")"
  delegation_policies="$(printf '%s\n' "${HARNESS_DELEGATION_POLICIES[@]}")"
  execution_profiles="$(printf '%s\n' "${HARNESS_EXECUTION_PROFILES[@]}")"
  reasoning_profiles="$(printf '%s\n' "${HARNESS_REASONING_PROFILES[@]}")"
  isolation_modes="$(printf '%s\n' "${HARNESS_ISOLATION_MODES[@]}")"
  model_policies="$(printf '%s\n' "${HARNESS_MODEL_POLICIES[@]}")"
  actor_kinds="$(printf '%s\n' "${HARNESS_ACTOR_KINDS[@]}")"
  binding_outcomes="$(printf '%s\n' "${HARNESS_RUNTIME_BINDING_OUTCOMES[@]}")"
  failure_kinds="$(printf '%s\n' "${HARNESS_FAILURE_KINDS[@]}")"
  execution_stop_reasons="$(printf '%s\n' "${HARNESS_EXECUTION_STOP_REASONS[@]}")"

  assert_sequence "$entries" "$(cat <<'EOF'
analyze-project
design-change
plan-change
implement-change
review-change
sync-truth
close-change
EOF
)" "entry order drifted"

  assert_sequence "$phases" "$(cat <<'EOF'
intake
truth-scan
clarify
design-lite
design-full
plan
dependency-freeze
implement-serial
implement-parallel
converge
review
verify
truth-sync
close
EOF
)" "phase order drifted"

  assert_sequence "$classes" "$(cat <<'EOF'
A
B
C
D
EOF
)" "change classes drifted"

  assert_sequence "$design_strengths" "$(cat <<'EOF'
no-design
design-lite
design-full
EOF
)" "design strengths drifted"

  assert_sequence "$verdicts" "$(cat <<'EOF'
pass
needs-fixes
guarded-rollback-required
manual-decision-required
EOF
)" "verdicts drifted"

  assert_sequence "$artifact_classes" "$(cat <<'EOF'
truth
design
plan
implementation
evaluation
history
EOF
)" "artifact classes drifted"

  assert_sequence "$failure_policies" "$(cat <<'EOF'
fix_forward
stop_and_diagnose
guarded_rollback
EOF
)" "failure policies drifted"

  assert_sequence "$plan_contract_versions" "2" "plan contract versions drifted"

  assert_sequence "$parallel_policies" "$(cat <<'EOF'
forbidden
allowed
required
EOF
)" "parallel policies drifted"

  assert_sequence "$delegation_policies" "$(cat <<'EOF'
forbidden
allowed
preferred
EOF
)" "delegation policies drifted"

  assert_sequence "$execution_profiles" "$(cat <<'EOF'
deep
balanced
fast
EOF
)" "execution profiles drifted"

  assert_sequence "$reasoning_profiles" "$(cat <<'EOF'
deep
standard
light
EOF
)" "reasoning profiles drifted"

  assert_sequence "$isolation_modes" "$(cat <<'EOF'
controller-checkout
isolated-worktree
shared-read-only
EOF
)" "isolation modes drifted"

  assert_sequence "$model_policies" "$(cat <<'EOF'
semantic-routing
inherit-main
runtime-default
EOF
)" "model policies drifted"

  assert_sequence "$actor_kinds" "$(cat <<'EOF'
main
subagent
EOF
)" "actor kinds drifted"

  assert_sequence "$binding_outcomes" "$(cat <<'EOF'
bound
serial-fallback
capacity-stop
parallel-conflict
EOF
)" "runtime binding outcomes drifted"

  assert_sequence "$failure_kinds" "$(cat <<'EOF'
classification-failure
truth-conflict
requirement-ambiguity
boundary-mismatch
plan-incompleteness
dependency-churn
parallel-conflict
convergence-failure
review-blocking-failure
verification-failure
truth-sync-failure
EOF
)" "failure kinds drifted"

  is_valid_entry "analyze-project" || fail "analyze-project should be valid"
  is_valid_entry "close-change" || fail "close-change should be valid"
  assert_invalid is_valid_entry "smart-commit"

  is_valid_phase "truth-scan" || fail "truth-scan should be valid"
  is_valid_phase "implement-parallel" || fail "implement-parallel should remain a declared phase"
  assert_invalid is_valid_phase "implement"

  is_valid_change_class "A" || fail "A should be valid"
  is_valid_change_class "D" || fail "D should be valid"
  assert_invalid is_valid_change_class "Z"

  is_valid_design_strength "no-design" || fail "no-design should be valid"
  is_valid_design_strength "design-full" || fail "design-full should be valid"
  assert_invalid is_valid_design_strength "full-design"

  is_valid_verdict "pass" || fail "pass should be valid"
  is_valid_verdict "guarded-rollback-required" || fail "guarded-rollback-required should be valid"
  assert_invalid is_valid_verdict "ok"

  is_valid_artifact_class "truth" || fail "truth should be valid"
  is_valid_artifact_class "evaluation" || fail "evaluation should be valid"
  assert_invalid is_valid_artifact_class "code"

  is_valid_failure_policy "fix_forward" || fail "fix_forward should be valid"
  is_valid_failure_policy "guarded_rollback" || fail "guarded_rollback should be valid"
  assert_invalid is_valid_failure_policy "rollback_on_failure"

  is_valid_plan_contract_version "2" || fail "plan contract version 2 should be valid"
  assert_invalid is_valid_plan_contract_version "1"

  is_valid_parallel_policy "allowed" || fail "allowed parallel policy should be valid"
  is_valid_parallel_policy "required" || fail "required parallel policy should be valid"
  assert_invalid is_valid_parallel_policy "preferred"

  is_valid_delegation_policy "preferred" || fail "preferred delegation should be valid"
  assert_invalid is_valid_delegation_policy "required"

  is_valid_execution_profile "deep" || fail "deep execution profile should be valid"
  is_valid_execution_profile "fast" || fail "fast execution profile should be valid"
  assert_invalid is_valid_execution_profile "vendor-ultra"

  is_valid_reasoning_profile "standard" || fail "standard reasoning profile should be valid"
  assert_invalid is_valid_reasoning_profile "maximum"

  is_valid_isolation_mode "isolated-worktree" || fail "isolated-worktree should be valid"
  assert_invalid is_valid_isolation_mode "shared-write"

  is_valid_model_policy "semantic-routing" || fail "semantic-routing should be valid"
  is_valid_model_policy "inherit-main" || fail "inherit-main should be valid"
  assert_invalid is_valid_model_policy "pinned-provider"

  is_valid_actor_kind "subagent" || fail "subagent actor should be valid"
  assert_invalid is_valid_actor_kind "reviewer"

  is_valid_runtime_binding_outcome "serial-fallback" || fail "serial-fallback should be valid"
  assert_invalid is_valid_runtime_binding_outcome "silent-fallback"

  is_valid_failure_kind "classification-failure" || fail "classification-failure should be valid"
  is_valid_failure_kind "truth-sync-failure" || fail "truth-sync-failure should be valid"
  assert_invalid is_valid_failure_kind "git-conflict"

  assert_sequence "$execution_stop_reasons" "$(cat <<'EOF'
worktree_decision_required
task_blocked_requires_human
scope_violation_requires_replan
parallel_capacity_required
guarded_rollback_required
plan_incomplete
final_review_failed
final_verification_failed
truth_sync_required
ready_for_close
EOF
)" "execution stop reasons drifted"
  is_valid_execution_stop_reason "parallel_capacity_required" || fail "parallel capacity stop should be valid"

  assert_eq "$(harness_default_phase)" "intake" "default phase should stay intake"
}

main "$@"
