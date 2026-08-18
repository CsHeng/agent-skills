#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=plan-runner.sh
source "$HARNESS_LIB_ROOT/plan-runner.sh"

fail() {
  printf 'test-plan-runner: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"
  rg -n "$pattern" "$file_ref" >/dev/null || fail "$message"
}

replace_once() {
  local file_ref="$1"
  local old_line="$2"
  local new_line="$3"
  local replacement_file="${file_ref}.replacement"

  awk -v old_line="$old_line" -v new_line="$new_line" '
    BEGIN { replaced = 0 }
    !replaced && $0 == old_line {
      print new_line
      replaced = 1
      next
    }
    { print }
    END {
      if (!replaced) {
        exit 1
      }
    }
  ' "$file_ref" >"$replacement_file" || {
    rm -f -- "$replacement_file"
    fail "fixture line not found: $old_line"
  }
  mv -- "$replacement_file" "$file_ref"
}

replace_nth() {
  local file_ref="$1"
  local old_line="$2"
  local new_line="$3"
  local occurrence="$4"
  local replacement_file="${file_ref}.replacement"

  awk -v old_line="$old_line" -v new_line="$new_line" -v occurrence="$occurrence" '
    BEGIN { match_count = 0; replaced = 0 }
    $0 == old_line {
      match_count += 1
      if (match_count == occurrence) {
        print new_line
        replaced = 1
        next
      }
    }
    { print }
    END {
      if (!replaced) {
        exit 1
      }
    }
  ' "$file_ref" >"$replacement_file" || {
    rm -f -- "$replacement_file"
    fail "fixture occurrence not found: $old_line occurrence=$occurrence"
  }
  mv -- "$replacement_file" "$file_ref"
}

main() {
  local tmp_dir legacy_plan strict_plan guarded_plan invalid_rollback_plan partial_plan design_file
  local v2_plan invalid_version_plan invalid_profile_plan invalid_model_plan dependent_group_plan overlap_ref_plan overlap_lock_plan
  local read_only_plan invalid_shared_write_plan invalid_serial_worker_plan unknown_batch_plan mismatched_batch_plan invalid_convergence_plan
  local batch_catalog_fixture truth_design truth_scope_plan missing_truth_scope_plan invalid_truth_ref_plan invalid_docs_predicate_plan false_truth_scope_plan
  local external_target external_plan missing_external_policy_plan delegated_external_plan parallel_external_plan unlocked_external_plan unsafe_external_plan
  local -a fixture_batch_ids=()
  local plan_skill=""

  case "$SKILL_SURFACE" in
    generated) plan_skill="$GENERATED_SKILLS_ROOT/plan-change/SKILL.md" ;;
    source) plan_skill="$ROOT_DIR/src/skills/workflows/plan-change/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(default_plan_artifact_path "docs/plans/harness-kernel/2026-04-06-add-tier-entitlement-design.md")" == "docs/plans/harness-kernel/2026-04-06-add-tier-entitlement-plan.md" ]] \
    || fail "default plan path drifted"
  [[ "$(plan_entry_phase)" == "plan" ]] || fail "plan entry phase should be plan"

  tmp_dir="$(mktemp -d)"
  legacy_plan="$tmp_dir/legacy-plan.md"
  strict_plan="$tmp_dir/strict-plan.md"
  guarded_plan="$tmp_dir/guarded-plan.md"
  invalid_rollback_plan="$tmp_dir/invalid-rollback-plan.md"
  partial_plan="$tmp_dir/partial-plan.md"
  v2_plan="$tmp_dir/v2-plan.md"
  invalid_version_plan="$tmp_dir/invalid-version-plan.md"
  invalid_profile_plan="$tmp_dir/invalid-profile-plan.md"
  invalid_model_plan="$tmp_dir/invalid-model-plan.md"
  dependent_group_plan="$tmp_dir/dependent-group-plan.md"
  overlap_ref_plan="$tmp_dir/overlap-ref-plan.md"
  overlap_lock_plan="$tmp_dir/overlap-lock-plan.md"
  read_only_plan="$tmp_dir/read-only-plan.md"
  invalid_shared_write_plan="$tmp_dir/invalid-shared-write-plan.md"
  invalid_serial_worker_plan="$tmp_dir/invalid-serial-worker-plan.md"
  unknown_batch_plan="$tmp_dir/unknown-batch-plan.md"
  mismatched_batch_plan="$tmp_dir/mismatched-batch-plan.md"
  invalid_convergence_plan="$tmp_dir/invalid-convergence-plan.md"
  batch_catalog_fixture="$tmp_dir/batch-catalog.md"
  truth_design="$tmp_dir/truth-design.md"
  truth_scope_plan="$tmp_dir/truth-scope-plan.md"
  missing_truth_scope_plan="$tmp_dir/missing-truth-scope-plan.md"
  invalid_truth_ref_plan="$tmp_dir/invalid-truth-ref-plan.md"
  invalid_docs_predicate_plan="$tmp_dir/invalid-docs-predicate-plan.md"
  false_truth_scope_plan="$tmp_dir/false-truth-scope-plan.md"
  design_file="$tmp_dir/design.md"
  external_target="$tmp_dir/user-config.toml"
  external_plan="$tmp_dir/external-plan.md"
  missing_external_policy_plan="$tmp_dir/missing-external-policy-plan.md"
  delegated_external_plan="$tmp_dir/delegated-external-plan.md"
  parallel_external_plan="$tmp_dir/parallel-external-plan.md"
  unlocked_external_plan="$tmp_dir/unlocked-external-plan.md"
  unsafe_external_plan="$tmp_dir/unsafe-external-plan.md"
  printf 'model = "inherit"\n' >"$external_target"

  cat >"$design_file" <<'EOF'
# Sample Design

## Implementation Surface

- impl_file_refs:
  - src/example
  - src/example-helper
  - src/converge
- external_impl_file_refs:
  - __EXTERNAL_TARGET__
- test_file_refs:
  - tests/example
  - tests/example-integration
  - tests/converge
EOF
  sed -i "s|__EXTERNAL_TARGET__|$external_target|" "$design_file"

  cat >"$batch_catalog_fixture" <<'EOF'
# Batch Catalog Fixture

## Parallel Batches

- batch_id: P1
- tasks:
  - task-a
  - task-b
- max_parallelism: 2
- convergence_task: controller

- batch_id: P2
- tasks:
  - task-c
  - task-d
- max_parallelism: 3
- convergence_task: merge-task
EOF

  cat >"$truth_design" <<'EOF'
# Truth Design Fixture

## Change Classification

- truth_impact: high
EOF

  cat >"$truth_scope_plan" <<'EOF'
# Truth Scope Fixture

## Upstream Design

- design_ref: truth-design.md
- design_version: 1

## Implementation Scope

- plan_contract_version: 2
- truth_sync_required: true
- impl_file_refs:
  - docs/architecture/runtime.md
- test_file_refs:
  - tests/runtime.sh

## Truth Sync Handoff

- stable_truth_refs:
  - docs/architecture/runtime.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
  - decision-record-lifecycle
EOF

  cp "$truth_scope_plan" "$missing_truth_scope_plan"
  sed -i '/^## Truth Sync Handoff$/,$d' "$missing_truth_scope_plan"

  cp "$truth_scope_plan" "$invalid_truth_ref_plan"
  replace_nth "$invalid_truth_ref_plan" '  - docs/architecture/runtime.md' '  - docs/plans/changes/runtime.md' 2

  cp "$truth_scope_plan" "$invalid_docs_predicate_plan"
  sed -i 's/canonical-terminology-across-surfaces/all-markdown/' "$invalid_docs_predicate_plan"

  cp "$truth_scope_plan" "$false_truth_scope_plan"
  sed -i 's/truth_sync_required: true/truth_sync_required: false/' "$false_truth_scope_plan"

  mapfile -t fixture_batch_ids < <(list_plan_parallel_batch_ids "$batch_catalog_fixture")
  [[ "${fixture_batch_ids[*]}" == "P1 P2" ]] || fail "parallel batch catalog should preserve repeated batch order"
  [[ "$(parallel_batch_max_parallelism "$batch_catalog_fixture" "P2")" == "3" ]] || fail "parallel batch catalog should resolve per-batch limits"
  [[ "$(extract_parallel_batch_list "$batch_catalog_fixture" "P2" "tasks" | paste -sd ' ' -)" == "task-c task-d" ]] || fail "parallel batch catalog should resolve exact per-batch members"

  cat >"$legacy_plan" <<'EOF'
# Legacy Sample Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-initial

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
- approval_status: pending
- next_entry: implement-change

## Task 1: Example

- [ ] Step 1: Do work
- [ ] Step 2: Run verification

## Rollback

- failure_kind: plan-incompleteness
- rollback_entry: design-change
EOF

  cat >"$strict_plan" <<'EOF'
# Strict Sample Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-initial

## Implementation Scope

- impl_file_refs:
  - src/example
  - src/example-helper
  - src/converge
- test_file_refs:
  - tests/example
  - tests/example-integration
  - tests/converge
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: validate the strict example flow
- non_goals:
  - no production rollout
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: TDD for local behavior plus integration smoke verification
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

## Task 1: Example Core

- task_id: task-1
- depends_on:
  - root
- scope_slice: core example flow
- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
- verification_scope:
  - `bash test.sh`
- executor_mode: inline-serial
- task_review_depth: quick
- done_when:
  - `bash test.sh` succeeds
- failure_policy: fix_forward
- [ ] Step 1: Do work

## Task 2: Example Integration

- task_id: task-2
- depends_on:
  - task-1
- scope_slice: integration follow-up
- impl_file_refs:
  - src/example-helper
- test_file_refs:
  - tests/example-integration
- verification_scope:
  - `bash test.sh`
- executor_mode: inline-serial
- task_review_depth: quick
- done_when:
  - helper and integration verification pass
- failure_policy: stop_and_diagnose
- [ ] Step 1: Extend the integration

## Recovery

- default_failure_policy: fix_forward
- backup_or_snapshot:
  - retain pre-change state as recovery evidence without automatic restore
EOF

  cat >"$v2_plan" <<'EOF'
# Version 2 Parallel Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-initial

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: true
- impl_file_refs:
  - src/example
  - src/example-helper
  - src/converge
- test_file_refs:
  - tests/example
  - tests/example-integration
  - tests/converge
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: validate one portable conditional-parallel batch
- non_goals:
  - no provider-specific model binding
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: model-based DAG and binding contract tests
- acceptance_oracles:
  - both dependency-free tasks pass independently
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: minimum of runtime capacity and safe ready tasks

## Parallel Batches

- batch_id: sample-parallel
- tasks:
  - parallel-core
  - parallel-integration
- parallel_policy: allowed
- max_parallelism: 2
- convergence_task: parallel-converge

## Task 1: Parallel Core

- task_id: parallel-core
- depends_on:
  - root
- scope_slice: first independent write slice
- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
- verification_scope:
  - `bash test-core.sh`
- executor_mode: subagent
- parallel_group: sample-parallel
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - core-contract
- task_review_depth: boundary
- done_when:
  - core verification passes
- failure_policy: fix_forward

## Task 2: Parallel Integration

- task_id: parallel-integration
- depends_on:
  - none
- scope_slice: second independent write slice
- impl_file_refs:
  - src/example-helper
- test_file_refs:
  - tests/example-integration
- verification_scope:
  - `bash test-integration.sh`
- executor_mode: subagent
- parallel_group: sample-parallel
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - integration-contract
- task_review_depth: focused
- done_when:
  - integration verification passes
- failure_policy: fix_forward

## Task 3: Parallel Convergence

- task_id: parallel-converge
- depends_on:
  - parallel-core
  - parallel-integration
- scope_slice: controller-owned batch convergence
- impl_file_refs:
  - src/converge
- test_file_refs:
  - tests/converge
- verification_scope:
  - `bash test-converge.sh`
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - convergence-contract
- task_review_depth: boundary
- done_when:
  - batch convergence verification passes
- failure_policy: fix_forward

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: pending
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
EOF

  cat >"$partial_plan" <<'EOF'
# Partial Sample Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-initial

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
- approval_status: pending
- next_entry: implement-change

## Task 1: Partial

- task_id: task-1
- scope_slice: partial task metadata
- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
- verification_scope:
  - `bash test.sh`
- executor_mode: inline-serial
- task_review_depth: quick
- done_when:
  - `bash test.sh` succeeds
- failure_policy: fix_forward
- [ ] Step 1: Do work

## Recovery

- default_failure_policy: fix_forward
EOF

  cat >"$guarded_plan" <<'EOF'
# Guarded Network Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-04-06-initial

## Implementation Scope

- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: change a network control-plane boundary without losing management access
- non_goals:
  - no unrelated network redesign
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: pre-change reachability plus post-change management-path verification
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

## Task 1: Guard Management Connectivity

- task_id: task-network
- depends_on:
  - root
- scope_slice: network control-plane change
- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
- verification_scope:
  - `bash test.sh`
- executor_mode: inline-serial
- task_review_depth: boundary
- done_when:
  - management path and routing invariants pass
- failure_policy: guarded_rollback
- rollback_trigger:
  - management connectivity is lost immediately after the controlled apply
- rollback_target: tested pre-change network configuration
- rollback_verification:
  - management connectivity and routing invariants pass after restore
- [ ] Apply the bounded network change

## Recovery

- default_failure_policy: fix_forward

## Rollback

- guarded_task_ids:
  - task-network
EOF

  cp "$strict_plan" "$invalid_rollback_plan"
  printf '\n## Rollback\n\n- guarded_task_ids:\n  - none\n' >>"$invalid_rollback_plan"

  cp "$v2_plan" "$invalid_version_plan"
  replace_once "$invalid_version_plan" '- plan_contract_version: 2' '- plan_contract_version: 99'

  cp "$v2_plan" "$invalid_profile_plan"
  replace_once "$invalid_profile_plan" '- execution_profile: deep' '- execution_profile: vendor-ultra'

  cp "$v2_plan" "$invalid_model_plan"
  replace_once "$invalid_model_plan" '- default_model_policy: semantic-routing' '- default_model_policy: provider-pinned'

  cp "$v2_plan" "$dependent_group_plan"
  replace_once "$dependent_group_plan" '  - none' '  - parallel-core'

  cp "$v2_plan" "$overlap_ref_plan"
  replace_nth "$overlap_ref_plan" '  - src/example-helper' '  - src/example' 2

  cp "$v2_plan" "$overlap_lock_plan"
  replace_once "$overlap_lock_plan" '  - integration-contract' '  - core-contract'

  cp "$v2_plan" "$read_only_plan"
  replace_nth "$read_only_plan" '  - src/example' '  - none' 2
  replace_nth "$read_only_plan" '  - tests/example' '  - none' 2
  replace_nth "$read_only_plan" '  - src/example-helper' '  - none' 2
  replace_nth "$read_only_plan" '  - tests/example-integration' '  - none' 2
  replace_once "$read_only_plan" '- isolation: isolated-worktree' '- isolation: shared-read-only'
  replace_once "$read_only_plan" '- isolation: isolated-worktree' '- isolation: shared-read-only'

  cp "$v2_plan" "$invalid_shared_write_plan"
  replace_once "$invalid_shared_write_plan" '- isolation: isolated-worktree' '- isolation: shared-read-only'

  cp "$v2_plan" "$invalid_serial_worker_plan"
  replace_once "$invalid_serial_worker_plan" '- executor_mode: main' '- executor_mode: subagent'
  replace_once "$invalid_serial_worker_plan" '- delegation_policy: forbidden' '- delegation_policy: preferred'

  cp "$v2_plan" "$unknown_batch_plan"
  replace_once "$unknown_batch_plan" '- batch_id: sample-parallel' '- batch_id: undeclared-batch'

  cp "$v2_plan" "$mismatched_batch_plan"
  replace_once "$mismatched_batch_plan" '  - parallel-integration' '  - parallel-converge'

  cp "$v2_plan" "$invalid_convergence_plan"
  replace_once "$invalid_convergence_plan" '- convergence_task: parallel-converge' '- convergence_task: parallel-core'

  cp "$v2_plan" "$external_plan"
  replace_once "$external_plan" '- parallel_execution_approved: true' $'- parallel_execution_approved: true\n- external_touch_policy: exact-existing-files-v1'
  replace_once "$external_plan" '- test_file_refs:' $'- external_impl_file_refs:\n  - __EXTERNAL_TARGET__\n- test_file_refs:'
  replace_nth "$external_plan" '- test_file_refs:' $'- external_impl_file_refs:\n  - __EXTERNAL_TARGET__\n- test_file_refs:' 4
  sed -i "s|__EXTERNAL_TARGET__|$external_target|g" "$external_plan"

  cp "$external_plan" "$missing_external_policy_plan"
  sed -i '/^- external_touch_policy: exact-existing-files-v1$/d' "$missing_external_policy_plan"

  cp "$external_plan" "$delegated_external_plan"
  replace_nth "$delegated_external_plan" '- executor_mode: main' '- executor_mode: subagent' 1

  cp "$external_plan" "$parallel_external_plan"
  replace_once "$parallel_external_plan" '- task_id: parallel-converge' '- task_id: external-converge'
  replace_nth "$parallel_external_plan" '- parallel_group: none' '- parallel_group: sample-parallel' 1
  replace_nth "$parallel_external_plan" '- parallel_policy: forbidden' '- parallel_policy: allowed' 1

  cp "$external_plan" "$unlocked_external_plan"
  replace_once "$unlocked_external_plan" '  - convergence-contract' '  - none'

  cp "$external_plan" "$unsafe_external_plan"
  sed -i "s|$external_target|relative/user-config.toml|g" "$unsafe_external_plan"

  validate_plan_artifact "$legacy_plan"
  validate_plan_artifact "$strict_plan"
  validate_plan_artifact "$v2_plan"
  validate_plan_artifact "$read_only_plan"
  validate_execution_grade_plan_artifact "$external_plan"
  validate_execution_grade_plan_artifact "$strict_plan"
  validate_execution_grade_plan_artifact "$v2_plan"
  validate_execution_grade_plan_artifact "$read_only_plan"
  validate_execution_grade_plan_artifact "$guarded_plan"
  [[ "$(plan_approval_status "$strict_plan")" == "pending" ]] || fail "plan approval status should resolve"
  [[ "$(plan_contract_version "$v2_plan")" == "2" ]] || fail "plan contract version should resolve"
  validate_plan_truth_sync_contract "$truth_scope_plan"
  if validate_plan_truth_sync_contract "$missing_truth_scope_plan" >/dev/null 2>&1; then
    fail "truth-affecting version-2 plans should require a truth-sync handoff"
  fi
  if validate_plan_truth_sync_contract "$invalid_truth_ref_plan" >/dev/null 2>&1; then
    fail "stable truth refs should reject stage artifacts"
  fi
  if validate_plan_truth_sync_contract "$invalid_docs_predicate_plan" >/dev/null 2>&1; then
    fail "unknown docs governance predicates should fail validation"
  fi
  if validate_plan_truth_sync_contract "$false_truth_scope_plan" >/dev/null 2>&1; then
    fail "a plan cannot override required design truth impact with false"
  fi

  if validate_plan_artifact "$partial_plan" >/dev/null 2>&1; then
    fail "partial task metadata should fail validation in compat mode once metadata appears"
  fi

  if (export PLAN_RUNNER_TASK_METADATA_MODE=strict; validate_plan_artifact "$legacy_plan") >/dev/null 2>&1; then
    fail "legacy prose-only plan should fail in strict task metadata mode"
  fi
  if validate_execution_grade_plan_artifact "$invalid_rollback_plan" >/dev/null 2>&1; then
    fail "fix-forward plan should reject generated rollback metadata"
  fi
  if validate_execution_grade_plan_artifact "$invalid_version_plan" >/dev/null 2>&1; then
    fail "unknown plan contract version should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$invalid_profile_plan" >/dev/null 2>&1; then
    fail "unknown execution profile should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$invalid_model_plan" >/dev/null 2>&1; then
    fail "provider-pinned model policy should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$dependent_group_plan" >/dev/null 2>&1; then
    fail "dependency inside one parallel group should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$overlap_ref_plan" >/dev/null 2>&1; then
    fail "overlapping parallel write refs should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$overlap_lock_plan" >/dev/null 2>&1; then
    fail "overlapping parallel resource locks should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$invalid_shared_write_plan" >/dev/null 2>&1; then
    fail "shared-read-only tasks with write refs should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$invalid_serial_worker_plan" >/dev/null 2>&1; then
    fail "delegated write tasks in the controller checkout should fail validation"
  fi
  if validate_execution_grade_plan_artifact "$unknown_batch_plan" >/dev/null 2>&1; then
    fail "batch IDs must match declared task parallel groups"
  fi
  if validate_execution_grade_plan_artifact "$mismatched_batch_plan" >/dev/null 2>&1; then
    fail "batch task lists must exactly match their task groups"
  fi
  if validate_execution_grade_plan_artifact "$invalid_convergence_plan" >/dev/null 2>&1; then
    fail "batch convergence tasks cannot be batch members"
  fi
  if validate_execution_grade_plan_artifact "$missing_external_policy_plan" >/dev/null 2>&1; then
    fail "external refs should require the exact external touch policy"
  fi
  if validate_execution_grade_plan_artifact "$delegated_external_plan" >/dev/null 2>&1; then
    fail "external tasks cannot be delegated"
  fi
  if validate_execution_grade_plan_artifact "$parallel_external_plan" >/dev/null 2>&1; then
    fail "external tasks cannot be parallelized"
  fi
  if validate_execution_grade_plan_artifact "$unlocked_external_plan" >/dev/null 2>&1; then
    fail "external tasks require a named resource lock"
  fi
  if validate_execution_grade_plan_artifact "$unsafe_external_plan" >/dev/null 2>&1; then
    fail "external refs must be exact absolute paths"
  fi

  assert_contains "$plan_skill" 'scripts/harness/plan-runner\.sh' "plan skill should use its bundled runner"
  assert_contains "$plan_skill" 'confirmation_clearance' "plan skill should require confirmation clearance"
  assert_contains "$plan_skill" 'continuous_after_plan_approval' "plan skill should state continuous execution mode"
  assert_contains "$plan_skill" 'default_failure_policy:[[:space:]]*fix_forward' "plan skill should default to fix-forward"
  assert_contains "$plan_skill" 'fix_forward' "plan skill should define fix-forward"
  assert_contains "$plan_skill" 'stop_and_diagnose' "plan skill should define stop-and-diagnose"
  assert_contains "$plan_skill" 'guarded_rollback' "plan skill should define guarded rollback"
  assert_contains "$plan_skill" 'executable-oracle-architecture-selector' "plan skill should route non-trivial behavior to oracle selection"
  assert_contains "$plan_skill" 'review-change' "plan skill should route through top-level review gate"
  assert_contains "$plan_skill" 'approval_status:' "plan skill should expose the approval status field"
  assert_contains "$plan_skill" 'plan_contract_version:[[:space:]]*2' "plan skill should require version-2 plans"
  assert_contains "$plan_skill" 'parallel_policy.*forbidden.*allowed.*required' "plan skill should define parallel policy"
  assert_contains "$plan_skill" 'delegation_policy.*forbidden.*allowed.*preferred' "plan skill should define delegation policy"
  assert_contains "$plan_skill" 'semantic-routing' "plan skill should default to semantic routing"
  assert_contains "$plan_skill" 'inherit-main' "plan skill should preserve the inherit-main override"
}

main "$@"
