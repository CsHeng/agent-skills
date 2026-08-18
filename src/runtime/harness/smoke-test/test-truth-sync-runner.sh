#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=truth-sync-runner.sh
source "$HARNESS_LIB_ROOT/truth-sync-runner.sh"

TEST_TRUTH_SYNC_TMP=""

fail() {
  printf 'test-truth-sync-runner: %s\n' "$*" >&2
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

write_tail_fixture() {
  local fixture_root="$1"
  local design_file="$fixture_root/design.md"
  local plan_file="$fixture_root/plan.md"

  cat >"$design_file" <<'EOF'
# Tail Design

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

  cat >"$plan_file" <<'EOF'
# Tail Plan

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

- milestone_objective: verify the evidence-bound tail
- non_goals:
  - no external close action
- future_phase:
  - none
- decision_status: ready_for_review
- oracle_strategy: structured harness contract tests
- acceptance_oracles:
  - tail evidence matches exactly
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
- effective_concurrency: 1

## Task 1: Tail Contract

- task_id: tail-task
- depends_on:
  - none
- scope_slice: verify tail evidence
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
  - tail-contract
- task_review_depth: focused
- done_when:
  - tail evidence passes
- failure_policy: fix_forward

## Truth Sync Handoff

- required_entry: sync-truth
- stable_truth_refs:
  - docs/architecture/runtime.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces

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

add_external_fixture_contract() {
  local fixture_root="$1"
  local external_ref="$2"
  local file_ref=""

  for file_ref in "$fixture_root/design.md" "$fixture_root/plan.md"; do
    awk -v external_ref="$external_ref" '
      /^-[[:space:]]*test_file_refs:/ {
        print "- external_impl_file_refs:"
        print "  - " external_ref
      }
      { print }
    ' "$file_ref" >"$file_ref.next"
    mv "$file_ref.next" "$file_ref"
  done
  sed -i '/^- parallel_execution_approved: false$/a\
- external_touch_policy: exact-existing-files-v1' "$fixture_root/plan.md"
}

write_truth_artifact() {
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
# Sample Truth Sync

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
- summary: Update stable harness tail truth.

## Human Gate

- approval_required: true
- approval_status: $approval_state
- next_entry: close-change
EOF
}

main() {
  local tmp_dir=""
  local plan_file=""
  local simple_plan_file=""
  local ledger_file=""
  local execution_result_file=""
  local tampered_execution_file=""
  local pending_artifact=""
  local approved_artifact=""
  local mismatched_artifact=""
  local invalid_artifact=""
  local gate_json=""
  local predicate_id=""
  local truth_skill=""
  local external_fixture external_target external_payload external_run_dir external_ledger external_execution

  case "$SKILL_SURFACE" in
    generated) truth_skill="$GENERATED_SKILLS_ROOT/sync-truth/SKILL.md" ;;
    source) truth_skill="$ROOT_DIR/src/skills/workflows/sync-truth/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(default_truth_sync_artifact_path "Harness Tail Gates" "2026-04-07")" == "docs/plans/changes/2026-04-07-harness-tail-gates-truth-sync.md" ]] \
    || fail "default truth-sync path drifted"
  [[ "$(truth_sync_entry_phase)" == "truth-sync" ]] || fail "truth-sync entry phase should be truth-sync"

  tmp_dir="$(realpath "$(mktemp -d)")"
  TEST_TRUTH_SYNC_TMP="$tmp_dir"
  trap 'rm -rf -- "$TEST_TRUTH_SYNC_TMP"' EXIT
  write_tail_fixture "$tmp_dir"
  plan_file="$tmp_dir/plan.md"
  simple_plan_file="$tmp_dir/simple-plan.md"
  ledger_file="$tmp_dir/ledger.json"
  execution_result_file="$tmp_dir/execution.json"
  tampered_execution_file="$tmp_dir/execution-tampered.json"
  pending_artifact="$tmp_dir/truth-sync-pending.md"
  approved_artifact="$tmp_dir/truth-sync-approved.md"
  mismatched_artifact="$tmp_dir/truth-sync-mismatch.md"
  invalid_artifact="$tmp_dir/truth-sync-invalid.md"
  external_fixture="$tmp_dir/external-fixture"
  external_target="$tmp_dir/user-config.toml"
  external_payload="$tmp_dir/payload.toml"
  external_run_dir="$tmp_dir/external-run"
  external_ledger="$tmp_dir/external-ledger.json"
  external_execution="$tmp_dir/external-execution.json"

  execution_task_ledger "$plan_file" | jq 'map(
    .status = "done"
    | .convergence_verified = true
    | .convergence_actor = "controller"
    | .oracles_verified = true
    | .integration_verified = true
  )' >"$ledger_file"
  build_execution_result_json "$plan_file" "$ledger_file" "verify" "" "truth_sync_required" "pass" "pass" "sync-truth" "truth-sync" "false" "current-checkout" >"$execution_result_file"
  assert_json "$(cat "$execution_result_file")" '.lifecycle_state == "truth-sync-pending" and .next_entry == "sync-truth"' "passing truth-affecting execution should route continuously to truth sync"

  write_truth_artifact "$pending_artifact" pending "$execution_result_file"
  write_truth_artifact "$approved_artifact" approved "$execution_result_file"
  cp "$pending_artifact" "$mismatched_artifact"
  sed -i 's/review:/review-mismatch:/' "$mismatched_artifact"
  cp "$pending_artifact" "$invalid_artifact"
  sed -i 's#docs/architecture/runtime.md#docs/plans/changes/runtime.md#' "$invalid_artifact"

  validate_truth_sync_artifact "$pending_artifact"
  validate_truth_sync_artifact_against_evidence "$pending_artifact" "$plan_file" "$execution_result_file"
  [[ "$(truth_sync_approval_status "$pending_artifact")" == "pending" ]] || fail "pending approval state should resolve"
  [[ "$(truth_sync_approval_status "$approved_artifact")" == "approved" ]] || fail "approved approval state should resolve"
  if validate_truth_sync_artifact "$invalid_artifact" >/dev/null 2>&1; then
    fail "stage artifact refs should be rejected from stable_truth_refs"
  fi
  if validate_truth_sync_artifact_against_evidence "$mismatched_artifact" "$plan_file" "$execution_result_file" >/dev/null 2>&1; then
    fail "mismatched review evidence should fail closed"
  fi

  mkdir "$external_fixture"
  mkdir -m 700 "$external_run_dir"
  printf 'model = "before"\n' >"$external_target"
  printf 'model = "after"\n' >"$external_payload"
  write_tail_fixture "$external_fixture"
  add_external_fixture_contract "$external_fixture" "$external_target"
  execution_task_ledger "$external_fixture/plan.md" | jq 'map(.status = "in_progress")' >"$external_ledger"
  execution_external_baseline "$external_fixture/plan.md" "$external_ledger" tail-task tail-run >"$tmp_dir/external-next.json"
  mv "$tmp_dir/external-next.json" "$external_ledger"
  execution_external_prepare "$external_fixture/plan.md" "$external_ledger" tail-task "$external_run_dir" "$external_target" tail-intent "$external_payload" >"$tmp_dir/external-next.json"
  mv "$tmp_dir/external-next.json" "$external_ledger"
  execution_external_apply "$external_fixture/plan.md" "$external_ledger" tail-task tail-intent >"$tmp_dir/external-next.json"
  mv "$tmp_dir/external-next.json" "$external_ledger"
  jq 'map(.status = "in_review")' "$external_ledger" >"$tmp_dir/external-next.json"
  mv "$tmp_dir/external-next.json" "$external_ledger"
  execution_controller_converge "$external_fixture/plan.md" "$external_ledger" tail-task controller true true >"$tmp_dir/external-next.json"
  mv "$tmp_dir/external-next.json" "$external_ledger"
  build_execution_result_json "$external_fixture/plan.md" "$external_ledger" verify "" truth_sync_required pass pass sync-truth truth-sync false current-checkout >"$external_execution"
  validate_execution_evidence_binding "$external_fixture/plan.md" "$external_execution"

  printf 'model = "later-user-edit"\n' >"$external_target"
  validate_execution_evidence_binding "$external_fixture/plan.md" "$external_execution" \
    || fail "historical external evidence should not reread or freeze the live target"
  jq '.allowed_external_touch_refs += ["/tmp/widened.toml"]' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "widened external touch evidence should fail closed"
  fi
  jq '.task_evidence[0].verified_external_changes.refs[0].content = "secret"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "content-bearing external evidence should fail closed"
  fi
  jq '.verified_external_changes[0].task_id = "other-task"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "mismatched external task evidence should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].ref = "/tmp/undeclared.toml"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "stray undeclared intent evidence should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents += [.task_evidence[0].external_write_intents[0]]' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "duplicate intent identity should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].after.sha256 = "0000000000000000000000000000000000000000000000000000000000000000"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "after evidence not bound to the candidate should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].after.ref = "/tmp/other.toml"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "after evidence not bound to the declared ref should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].after.mode = "0644"' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "after metadata not preserved from the parent should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].after.st_dev = (.task_evidence[0].external_write_intents[0].parent.st_dev + 1)' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "after device not bound to the parent filesystem should fail closed"
  fi
  jq '.task_evidence[0].external_write_intents[0].after.st_ino = .task_evidence[0].external_write_intents[0].parent.st_ino' "$external_execution" >"$tampered_execution_file"
  if validate_execution_evidence_binding "$external_fixture/plan.md" "$tampered_execution_file" >/dev/null 2>&1; then
    fail "after inode without an authorized transition should fail closed"
  fi
  execution_external_cleanup "$external_ledger" tail-task tail-intent >/dev/null

  gate_json="$(build_truth_sync_gate_result "$pending_artifact" "$plan_file" "$execution_result_file")"
  assert_json "$gate_json" '.verdict == "pass" and .truth_sync_completed == false and .lifecycle_state == "truth-sync-pending" and .next_entry == "sync-truth"' "pending truth approval should remain at truth sync"
  gate_json="$(build_truth_sync_gate_result "$approved_artifact" "$plan_file" "$execution_result_file")"
  assert_json "$gate_json" '.ready_for_close == true and .lifecycle_state == "ready-for-close" and .next_entry == "close-change"' "approved matching truth should become close-ready"

  gate_json="$(truth_sync_mutation_authorization direct true)"
  assert_json "$gate_json" '.authorized == true and .authority == "direct-explicit-request"' "direct explicit mutation should remain authorized"
  gate_json="$(truth_sync_mutation_authorization direct false)"
  assert_json "$gate_json" '.authorized == false' "implicit direct mutation should fail closed"
  gate_json="$(truth_sync_mutation_authorization controller "$plan_file" "$execution_result_file")"
  assert_json "$gate_json" '.authorized == true and .authority == "approved-plan-controller"' "complete controller context should authorize truth mutation"
  jq '.plan_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"' "$execution_result_file" >"$tampered_execution_file"
  gate_json="$(truth_sync_mutation_authorization controller "$plan_file" "$tampered_execution_file")"
  assert_json "$gate_json" '.authorized == false' "tampered controller evidence should fail closed"
  jq '.task_evidence[0].oracles_verified = false' "$execution_result_file" >"$tampered_execution_file"
  gate_json="$(truth_sync_mutation_authorization controller "$plan_file" "$tampered_execution_file")"
  assert_json "$gate_json" '.authorized == false' "tampered embedded task evidence should fail closed"

  gate_json="$(build_truth_sync_docs_governance_decision "$plan_file" docs/architecture/runtime.md)"
  assert_json "$gate_json" '.organize_docs_required == true and .matched_predicates == ["canonical-terminology-across-surfaces"]' "declared terminology alignment should activate bounded organize-docs"
  cp "$plan_file" "$simple_plan_file"
  sed -i 's/canonical-terminology-across-surfaces/none/' "$simple_plan_file"
  gate_json="$(build_truth_sync_docs_governance_decision "$simple_plan_file" docs/architecture/runtime.md)"
  assert_json "$gate_json" '.organize_docs_required == false and .matched_predicates == []' "simple stable fact updates should skip organize-docs"
  for predicate_id in \
    readme-agents-claude-ownership \
    stable-truth-roots \
    docs-search-boundaries \
    stage-artifact-placement \
    canonical-terminology-across-surfaces \
    markdown-prose-structure
  do
    gate_json="$(truth_sync_docs_governance_decision "$predicate_id" docs/architecture/runtime.md)"
    if ! jq -e --arg predicate_id "$predicate_id" '.organize_docs_required == true and .matched_predicates == [$predicate_id]' <<<"$gate_json" >/dev/null; then
      fail "each declared governance predicate should activate only its bounded docs component: $predicate_id"
    fi
  done
  if build_truth_sync_docs_governance_decision "$plan_file" README.md >/dev/null 2>&1; then
    fail "out-of-scope docs composition should fail closed"
  fi

  assert_contains "$truth_skill" 'scripts/harness/truth-sync-runner\.sh' "sync-truth skill should use its bundled runner"
  assert_contains "$truth_skill" 'validate-against' "sync-truth skill should bind its evidence package"
}

main "$@"
