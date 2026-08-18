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

assert_json_arg() {
  local json="$1"
  local arg_name="$2"
  local arg_value="$3"
  local expr="$4"
  local message="$5"

  if ! jq -e --arg "$arg_name" "$arg_value" "$expr" <<<"$json" >/dev/null; then
    fail "$message"
  fi
}

# Golden schema_version-1 wire shapes captured from the pre-refactor emitter.
# Placeholders are substituted with live fixture values before byte comparison.
GOLDEN_HERDR_DELEGATED_TEMPLATE='{"artifact_kind":"controller-binding-envelope","authority":{"adapter_capabilities":["consume-binding","manage-run-owned-terminal-resources","persist-adapter-state"],"denied_capabilities":["select-task","mutate-task-ledger","converge-task","invoke-review","adjudicate-findings","repair-implementation","derive-lifecycle-tail","claim-task-success"]},"batch_provenance":{"actor_capacity":3,"batch_id":"P1","batch_task_ids":["task-1","task-2","task-3"],"effective_width":2,"limiting_factors":["batch_limit"],"outcome":"bound","parallel_group":"P1","parallel_policy":"allowed","plan_max_parallelism":2,"planned_task_ids":["task-1","task-2","task-3"],"planned_width":2,"ready_frontier_task_ids":["task-1","task-2","task-3"],"ready_task_ids":["task-1","task-2","task-3"],"ready_width":3,"runtime_capacity":4,"selected_task_ids":["task-1","task-2"],"serial_fallback_reason":null,"stop_reason":null},"command_job":null,"controller":{"binding_kind":"delegated-task","controller_id":"controller-test","model_policy":"semantic-routing","run_id":"run-test-a1","run_nonce":"nonce-test-a1"},"physical_binding":{"agent_kind":"codex","agent_name":"worker-lynx-cb-ttask-1-a1","capability_profile":"delegated-local-writer","checkout_path":"__RAW_TMP__/.fixture-worker","control_plane_endpoint":"native://openai","credential_ref":"native-login/codex","model":"gpt-5.6-luna","pane_id":"pane-controller-test","permission_mode":"never","reasoning_effort":"high","sandbox_mode":"workspace-write","tab_id":"tab-controller-test","terminal_backend":"herdr","workspace_id":"workspace-test"},"provenance":{"batch":{"actor_capacity":3,"batch_id":"P1","batch_task_ids":["task-1","task-2","task-3"],"effective_width":2,"limiting_factors":["batch_limit"],"outcome":"bound","parallel_group":"P1","parallel_policy":"allowed","plan_max_parallelism":2,"planned_task_ids":["task-1","task-2","task-3"],"planned_width":2,"ready_frontier_task_ids":["task-1","task-2","task-3"],"ready_task_ids":["task-1","task-2","task-3"],"ready_width":3,"runtime_capacity":4,"selected_task_ids":["task-1","task-2"],"serial_fallback_reason":null,"stop_reason":null},"canonical_repository":"__REPO__","ledger_ref":"task-ledger.json","ledger_sha256":"__LEDGER_SHA__","plan_ref":"parallel-plan.md","plan_sha256":"__PLAN_SHA__","repository_revision":"__REV__"},"schema_version":1,"task":{"attempt":1,"convergence_required":true,"delegation_policy":"preferred","depends_on":["root"],"done_when":["example verification passes"],"execution_profile":"deep","executor_mode":"subagent","failure_policy":"fix_forward","impl_file_refs":["src/example.py"],"isolation":"isolated-worktree","oracle_refs":["bash test.sh"],"parallel_group":"P1","parallel_policy":"allowed","reasoning_profile":"deep","resource_locks":["example-state"],"rollback_target":"","rollback_trigger":[],"rollback_verification":[],"runtime_role":"worker","scope_slice":"example implementation","section":"Task 1: Example","start_state":"ready","status":"ready","task_id":"task-1","task_review_depth":"full","test_file_refs":["tests/test_example.py"],"title":"Example","touch_set":["src/example.py","tests/test_example.py"],"verification_commands":["bash test.sh"]}}'
GOLDEN_HERDR_COMMAND_TEMPLATE='{"artifact_kind":"controller-binding-envelope","authority":{"adapter_capabilities":["consume-binding","manage-run-owned-terminal-resources","persist-adapter-state"],"denied_capabilities":["select-task","mutate-task-ledger","converge-task","invoke-review","adjudicate-findings","repair-implementation","derive-lifecycle-tail","claim-task-success"]},"batch_provenance":{"actor_capacity":3,"batch_id":"P1","batch_task_ids":["task-1","task-2","task-3"],"effective_width":2,"limiting_factors":["batch_limit"],"outcome":"bound","parallel_group":"P1","parallel_policy":"allowed","plan_max_parallelism":2,"planned_task_ids":["task-1","task-2","task-3"],"planned_width":2,"ready_frontier_task_ids":["task-1","task-2","task-3"],"ready_task_ids":["task-1","task-2","task-3"],"ready_width":3,"runtime_capacity":4,"selected_task_ids":["task-1","task-2"],"serial_fallback_reason":null,"stop_reason":null},"command_job":{"argv":["bash","test.sh"],"command":"bash test.sh","cwd":"__REPO__","max_concurrency":1,"output_bound_bytes":8192,"provenance":{"kind":"task","task_id":"task-1"},"resource_locks":["example-state"],"timeout_seconds":60},"controller":{"binding_kind":"command-job","controller_id":"controller-test","model_policy":"semantic-routing","run_id":"command-run-a1","run_nonce":"nonce-test-a1"},"physical_binding":{"checkout_path":"__REPO__","pane_id":"pane-controller-test","tab_id":"tab-controller-test","terminal_backend":"herdr","workspace_id":"workspace-test"},"provenance":{"batch":{"actor_capacity":3,"batch_id":"P1","batch_task_ids":["task-1","task-2","task-3"],"effective_width":2,"limiting_factors":["batch_limit"],"outcome":"bound","parallel_group":"P1","parallel_policy":"allowed","plan_max_parallelism":2,"planned_task_ids":["task-1","task-2","task-3"],"planned_width":2,"ready_frontier_task_ids":["task-1","task-2","task-3"],"ready_task_ids":["task-1","task-2","task-3"],"ready_width":3,"runtime_capacity":4,"selected_task_ids":["task-1","task-2"],"serial_fallback_reason":null,"stop_reason":null},"canonical_repository":"__REPO__","ledger_ref":"task-ledger.json","ledger_sha256":"__LEDGER_SHA__","plan_ref":"parallel-plan.md","plan_sha256":"__PLAN_SHA__","repository_revision":"__REV__"},"schema_version":1,"task":{"attempt":1,"convergence_required":true,"delegation_policy":"preferred","depends_on":["root"],"done_when":["example verification passes"],"execution_profile":"deep","executor_mode":"subagent","failure_policy":"fix_forward","impl_file_refs":["src/example.py"],"isolation":"isolated-worktree","oracle_refs":["bash test.sh"],"parallel_group":"P1","parallel_policy":"allowed","reasoning_profile":"deep","resource_locks":["example-state"],"rollback_target":"","rollback_trigger":[],"rollback_verification":[],"runtime_role":"command-job","scope_slice":"example implementation","section":"Task 1: Example","start_state":"ready","status":"ready","task_id":"task-1","task_review_depth":"full","test_file_refs":["tests/test_example.py"],"title":"Example","touch_set":["src/example.py","tests/test_example.py"],"verification_commands":["bash test.sh"]}}'
GOLDEN_HERDR_REVIEW_TEMPLATE='{"artifact_kind":"controller-binding-envelope","authority":{"adapter_capabilities":["consume-binding","manage-run-owned-terminal-resources","persist-adapter-state"],"denied_capabilities":["select-task","mutate-task-ledger","converge-task","invoke-review","adjudicate-findings","repair-implementation","derive-lifecycle-tail","claim-task-success"]},"batch_provenance":null,"command_job":null,"controller":{"binding_kind":"bounded-review","controller_id":"controller-test","model_policy":"semantic-routing","run_id":"run-review-a1","run_nonce":"nonce-test-a1"},"physical_binding":{"agent_kind":"codex","agent_name":"reviewer-fox-78-timplem-a1","capability_profile":"delegated-read-only","checkout_path":"__REPO__","control_plane_endpoint":"native://openai","credential_ref":"native-login/codex","model":"gpt-5.6-sol","pane_id":"pane-controller-test","permission_mode":"never","reasoning_effort":"high","sandbox_mode":"read-only","tab_id":"tab-controller-test","terminal_backend":"herdr","workspace_id":"workspace-test"},"provenance":{"batch":null,"canonical_repository":"__REPO__","ledger_ref":"review-ready-ledger.json","ledger_sha256":"__REVIEW_LEDGER_SHA__","plan_ref":"parallel-plan.md","plan_sha256":"__PLAN_SHA__","repository_revision":"__REV__"},"schema_version":1,"task":{"attempt":1,"convergence_required":false,"delegation_policy":"preferred","depends_on":[],"done_when":["candidate findings returned to the main controller"],"execution_profile":"deep","executor_mode":"subagent","failure_policy":"stop-and-diagnose","impl_file_refs":[],"isolation":"shared-read-only","oracle_refs":["review-brief.md"],"parallel_group":"none","parallel_policy":"serial","reasoning_profile":"deep","resource_locks":["repository-review"],"review_brief_ref":"review-brief.md","review_brief_sha256":"__BRIEF_SHA__","rollback_target":"none","rollback_trigger":"none","rollback_verification":"none","runtime_role":"reviewer","scope_slice":"Review only the controller-issued bounded implementation brief","section":"Implementation Review","start_state":"ready","status":"ready","task_id":"implementation-review","task_review_depth":"implementation","test_file_refs":[],"title":"Bounded implementation review","touch_set":[],"verification_commands":["review-brief.md"]}}'

write_codex_request() {
  local out_file="$1"
  local run_id="$2"
  local task_id="$3"
  local model_policy="$4"
  local requested_model="$5"
  local requested_effort="$6"
  local resolution_source="$7"
  local spawn_cwd_supported="$8"
  local checkout_path="$9"
  local plan_sha="${10}"
  local ledger_sha="${11}"
  local binding_kind="${12:-delegated-task}"
  local brief_path="${13:-}"
  local brief_sha="${14:-}"
  local required_uplift_supported="${15:-true}"
  local parent_reasoning_effort="${16:-medium}"
  local required_minimum_reasoning_effort="${17:-medium}"

  jq -n \
    --arg run_id "$run_id" \
    --arg task_id "$task_id" \
    --arg model_policy "$model_policy" \
    --arg requested_model "$requested_model" \
    --arg requested_effort "$requested_effort" \
    --arg resolution_source "$resolution_source" \
    --arg spawn_cwd_supported "$spawn_cwd_supported" \
    --arg checkout_path "$checkout_path" \
    --arg plan_sha "$plan_sha" \
    --arg ledger_sha "$ledger_sha" \
    --arg binding_kind "$binding_kind" \
    --arg brief_path "$brief_path" \
    --arg brief_sha "$brief_sha" \
    --arg required_uplift_supported "$required_uplift_supported" \
    --arg parent_reasoning_effort "$parent_reasoning_effort" \
    --arg required_minimum_reasoning_effort "$required_minimum_reasoning_effort" \
    '{
      schema_version: 1,
      binding_kind: $binding_kind,
      controller_id: "controller-test",
      run_id: $run_id,
      run_nonce: "nonce-codex-a1",
      task_id: $task_id,
      attempt: 1,
      model_policy: $model_policy,
      expected_plan_sha256: $plan_sha,
      expected_ledger_sha256: $ledger_sha,
      review_brief_path: $brief_path,
      review_brief_sha256: $brief_sha,
      physical_binding: {
        checkout_path: $checkout_path,
        parent_reasoning_effort: $parent_reasoning_effort,
        requested_model: $requested_model,
        requested_reasoning_effort: $requested_effort,
        required_minimum_reasoning_effort: $required_minimum_reasoning_effort,
        resolution_source: $resolution_source,
        spawn_cwd_supported: $spawn_cwd_supported,
        required_uplift_supported: $required_uplift_supported
      }
    }' >"$out_file"
}

render_golden_envelope() {
  local template="$1"
  local repo_realpath="$2"
  local raw_tmp="$3"
  local revision="$4"
  local plan_sha="$5"
  local ledger_sha="$6"
  local review_ledger_sha="${7:-}"
  local brief_sha="${8:-}"

  template="${template//__REPO__/$repo_realpath}"
  template="${template//__RAW_TMP__/$raw_tmp}"
  template="${template//__REV__/$revision}"
  template="${template//__PLAN_SHA__/$plan_sha}"
  template="${template//__LEDGER_SHA__/$ledger_sha}"
  template="${template//__REVIEW_LEDGER_SHA__/$review_ledger_sha}"
  template="${template//__BRIEF_SHA__/$brief_sha}"
  printf '%s\n' "$template"
}

main() {
  local tmp_dir design_file approved_plan pending_plan legacy_plan parallel_plan external_plan verdict ledger_file execution_result_json workspace_mode worktree_preflight
  local external_tmp external_target external_payload external_run_dir external_ledger
  local binding_request_file binding_envelope_file binding_plan_digest binding_ledger_digest binding_worker_dir
  local command_request_file command_envelope_file
  local golden_repo golden_revision golden_plan_sha golden_ledger_sha golden_expected backend_stop
  local golden_review_ledger_sha golden_brief_sha
  local codex_fixtures codex_home_valid codex_plan codex_plan_sha codex_ledger codex_ledger_sha
  local codex_done_ledger_sha codex_request codex_envelope_file codex_brief_sha codex_user_home role_fixture
  local binding_ledger_before binding_ledger_after binding_file_mode binding_dir_mode
  local task_ledger_json=""
  local task_catalog_json=""
  local next_ready_task=""
  local binding_json=""
  local batch_provenance_json=""
  local batch_binding_json=""
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
  external_tmp="$(realpath "$(mktemp -d)")"
  TEST_EXECUTE_TMP="$tmp_dir"
  TEST_EXECUTE_EXTERNAL_TMP="$external_tmp"
  trap 'rm -rf -- "$TEST_EXECUTE_TMP" "$TEST_EXECUTE_EXTERNAL_TMP"' EXIT
  design_file="$tmp_dir/design.md"
  approved_plan="$tmp_dir/approved-plan.md"
  pending_plan="$tmp_dir/pending-plan.md"
  legacy_plan="$tmp_dir/legacy-plan.md"
  parallel_plan="$tmp_dir/parallel-plan.md"
  external_plan="$tmp_dir/external-plan.md"
  external_target="$external_tmp/user-config.toml"
  external_payload="$external_tmp/payload.toml"
  external_run_dir="$external_tmp/run"
  external_ledger="$external_tmp/ledger.json"
  mkdir -m 700 "$external_run_dir"
  printf 'model = "before"\n' >"$external_target"
  printf 'model = "after"\n' >"$external_payload"

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
- external_impl_file_refs:
  - __EXTERNAL_TARGET__
- test_file_refs:
  - tests/test_example.py
  - tests/test_helper.py
  - tests/test_third.py
EOF
  sed -i "s|__EXTERNAL_TARGET__|$external_target|" "$design_file"

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

  cat >"$external_plan" <<'EOF'
# External Execution Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-08-18-v1

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- external_touch_policy: exact-existing-files-v1
- impl_file_refs:
  - src/example.py
- external_impl_file_refs:
  - __EXTERNAL_TARGET__
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: verify exact external execution evidence
- non_goals:
  - no delegated external writer
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: state-transition smoke tests
- acceptance_oracles:
  - exact baseline-rooted evidence converges
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: inherit-main
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1

## Truth Sync Handoff

- stable_truth_refs:
  - src/example.py
- docs_governance_predicates:
  - none

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: External Configuration

- task_id: external-task
- depends_on:
  - root
- scope_slice: exact external configuration update
- impl_file_refs:
  - src/example.py
- external_impl_file_refs:
  - __EXTERNAL_TARGET__
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - external-config
- task_review_depth: full
- done_when:
  - external evidence converges
- failure_policy: fix_forward

## Recovery

- default_failure_policy: fix_forward
EOF
  sed -i "s|__EXTERNAL_TARGET__|$external_target|g" "$external_plan"

  git -C "$tmp_dir" init -q
  git -C "$tmp_dir" add .
  git -C "$tmp_dir" \
    -c user.name="Harness Fixture" \
    -c user.email="harness@example.invalid" \
    commit -qm "fixture"
  binding_worker_dir="$tmp_dir/.fixture-worker"
  git -C "$tmp_dir" worktree add --detach "$binding_worker_dir" HEAD >/dev/null

  validate_execution_plan "$approved_plan"
  if validate_execution_plan "$pending_plan" >/dev/null 2>&1; then
    fail "pending plan should not pass execution validation"
  fi
  if validate_execution_plan "$legacy_plan" >/dev/null 2>&1; then
    fail "legacy prose-only plan should not pass execution validation"
  fi
  validate_execution_plan "$parallel_plan"
  validate_execution_plan "$external_plan"

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
  [[ "$(execution_allowed_external_touch_set "$external_plan")" == "$external_target" ]] || fail "allowed external touch set should remain separate and exact"

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
  assert_json "$binding_json" '.batch_id == "P1" and .planned_width == 2 and .ready_width == 3 and .runtime_capacity == 4 and .actor_capacity == 3 and .effective_width == 2' "parallel binding should expose immutable batch capacity evidence"
  assert_json "$binding_json" '.batch_identity.task_ids == ["task-1", "task-2", "task-3"] and .limiting_factors == ["batch_limit"] and .serial_fallback_reason == null' "parallel binding should expose batch identity and limiting factors"
  assert_json "$binding_json" 'any(.evidence[]; .kind == "effective-capacity" and .planned_width == 2 and .ready_width == 3 and .selected_task_ids == ["task-1", "task-2"])' "parallel binding evidence should be adapter-ready"
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
  assert_json "$binding_json" '.serial_fallback_reason == "runtime_capacity" and .limiting_factors == ["runtime_capacity"]' "allowed serialization should record the exact fallback reason"

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

  task_ledger_json="$(execution_task_ledger "$parallel_plan")"
  printf '%s\n' "$task_ledger_json" >"$ledger_file"
  binding_plan_digest="$(harness_file_sha256 "$parallel_plan")"
  binding_ledger_digest="$(jq -cS . "$ledger_file" | shasum -a 256 | awk '{print $1}')"
  batch_binding_json="$(execution_runtime_binding_from_validated_plan "$parallel_plan" "$ledger_file" "P1" 4 "semantic-routing")"
  batch_provenance_json="$(jq -cS '
    {
      batch_id,
      parallel_group: .batch_identity.parallel_group,
      parallel_policy: .batch_identity.parallel_policy,
      batch_task_ids: .batch_identity.task_ids,
      planned_width,
      ready_width,
      ready_task_ids: .ready_task_ids,
      selected_task_ids,
      runtime_capacity,
      actor_capacity,
      effective_width,
      limiting_factors,
      serial_fallback_reason,
      outcome,
      stop_reason
    }
  ' <<<"$batch_binding_json")"
  binding_request_file="$tmp_dir/controller-binding-request.json"
  jq -n \
    --arg plan_sha256 "$binding_plan_digest" \
    --arg ledger_sha256 "$binding_ledger_digest" \
    --arg batch_id "P1" \
    --argjson batch_runtime_capacity 4 \
    --argjson batch_provenance "$batch_provenance_json" \
    --arg checkout_path "$binding_worker_dir" \
    '{
      schema_version: 1,
      binding_kind: "delegated-task",
      controller_id: "controller-test",
      run_id: "run-test-a1",
      run_nonce: "nonce-test-a1",
      task_id: "task-1",
      attempt: 1,
      model_policy: "semantic-routing",
      expected_plan_sha256: $plan_sha256,
      expected_ledger_sha256: $ledger_sha256,
      batch_id: $batch_id,
      batch_runtime_capacity: $batch_runtime_capacity,
      batch_provenance: $batch_provenance,
      review_brief_path: "",
      review_brief_sha256: "",
      physical_binding: {
        terminal_backend: "herdr",
        agent_kind: "codex",
        model: "gpt-5.6-luna",
        reasoning_effort: "high",
        permission_mode: "never",
        sandbox_mode: "workspace-write",
        capability_profile: "delegated-local-writer",
        control_plane_endpoint: "native://openai",
        credential_ref: "native-login/codex",
        workspace_id: "workspace-test",
        tab_id: "tab-controller-test",
        pane_id: "pane-controller-test",
        agent_name: "worker-lynx-cb-ttask-1-a1",
        checkout_path: $checkout_path
      }
    }' >"$binding_request_file"

  [[ "$(execution_herdr_agent_name worker run-test-a1 task-1 1)" == "worker-lynx-cb-ttask-1-a1" ]] \
    || fail "controller and adapter must share the deterministic agent-name projection"

  jq 'del(.run_nonce) | .run_id = "missing-nonce"' "$binding_request_file" >"$tmp_dir/missing-nonce.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/missing-nonce.json") >/dev/null 2>&1; then
    fail "controller binding should reject a forged request without the controller nonce"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/missing-nonce" ]] || fail "missing nonce must fail before output mutation"

  jq '.run_id = "stale-plan" | .expected_plan_sha256 = ("0" * 64)' "$binding_request_file" >"$tmp_dir/stale-plan.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/stale-plan.json") >/dev/null 2>&1; then
    fail "controller binding should reject a stale plan digest"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/stale-plan" ]] || fail "stale plan digest must fail before output mutation"

  jq '.run_id = "stale-ledger" | .expected_ledger_sha256 = ("1" * 64)' "$binding_request_file" >"$tmp_dir/stale-ledger.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/stale-ledger.json") >/dev/null 2>&1; then
    fail "controller binding should reject a stale ledger digest"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/stale-ledger" ]] || fail "stale ledger digest must fail before output mutation"

  jq '.run_id = "unsafe-secret" | .physical_binding.api_key = "must-not-persist"' "$binding_request_file" >"$tmp_dir/unsafe-secret.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/unsafe-secret.json") >/dev/null 2>&1; then
    fail "controller binding should reject undeclared credential material"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/unsafe-secret" ]] || fail "credential material must fail before output mutation"

  jq '.run_id = "malformed-binding" | del(.physical_binding.sandbox_mode)' "$binding_request_file" >"$tmp_dir/malformed-binding.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/malformed-binding.json") >/dev/null 2>&1; then
    fail "controller binding should reject malformed physical binding data"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/malformed-binding" ]] || fail "malformed binding must fail before output mutation"

  jq '.physical_binding.agent_name = "worker-wolf-00-ttask-1-a1"' "$binding_request_file" >"$tmp_dir/mismatched-agent-name.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/mismatched-agent-name.json") >/dev/null 2>&1; then
    fail "controller binding should reject a non-deterministic agent name"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/run-test-a1" ]] || fail "agent-name mismatch must fail before output mutation"

  jq '.run_id = "../escape"' "$binding_request_file" >"$tmp_dir/unsafe-output.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/unsafe-output.json") >/dev/null 2>&1; then
    fail "controller binding should reject unsafe output paths"
  fi
  [[ ! -e "$tmp_dir/escape" ]] || fail "unsafe run ID must not escape the run-state root"

  jq '.run_id = "unknown-task" | .task_id = "task-unknown"' "$binding_request_file" >"$tmp_dir/unknown-task.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/unknown-task.json") >/dev/null 2>&1; then
    fail "controller binding should reject unknown tasks"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/unknown-task" ]] || fail "unknown task must fail before output mutation"

  jq '.[0].status = "pending"' "$ledger_file" >"$tmp_dir/non-ready-ledger.json"
  binding_ledger_digest="$(jq -cS . "$tmp_dir/non-ready-ledger.json" | shasum -a 256 | awk '{print $1}')"
  jq --arg ledger_sha256 "$binding_ledger_digest" '.run_id = "non-ready-task" | .expected_ledger_sha256 = $ledger_sha256' "$binding_request_file" >"$tmp_dir/non-ready-task.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$tmp_dir/non-ready-ledger.json" "$tmp_dir/non-ready-task.json") >/dev/null 2>&1; then
    fail "controller binding should reject a non-ready task"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/non-ready-task" ]] || fail "non-ready task must fail before output mutation"

  jq '.[0].scope_slice = "drifted task scope"' "$ledger_file" >"$tmp_dir/drifted-ledger.json"
  binding_ledger_digest="$(jq -cS . "$tmp_dir/drifted-ledger.json" | shasum -a 256 | awk '{print $1}')"
  jq --arg ledger_sha256 "$binding_ledger_digest" '.run_id = "drifted-ledger" | .expected_ledger_sha256 = $ledger_sha256' "$binding_request_file" >"$tmp_dir/drifted-request.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$tmp_dir/drifted-ledger.json" "$tmp_dir/drifted-request.json") >/dev/null 2>&1; then
    fail "controller binding should reject plan-ledger drift"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/drifted-ledger" ]] || fail "plan-ledger drift must fail before output mutation"

  binding_plan_digest="$(harness_file_sha256 "$pending_plan")"
  jq --arg plan_sha256 "$binding_plan_digest" '.run_id = "unapproved-plan" | .expected_plan_sha256 = $plan_sha256' "$binding_request_file" >"$tmp_dir/unapproved-request.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$pending_plan" "$ledger_file" "$tmp_dir/unapproved-request.json") >/dev/null 2>&1; then
    fail "controller binding should reject an unapproved plan"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/unapproved-plan" ]] || fail "unapproved plan must fail before output mutation"

  binding_ledger_before="$(harness_file_sha256 "$ledger_file")"
  binding_envelope_file="$(cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$binding_request_file")"
  binding_ledger_after="$(harness_file_sha256 "$ledger_file")"
  [[ "$binding_ledger_before" == "$binding_ledger_after" ]] || fail "controller binding must not mutate the task ledger"
  [[ "$binding_envelope_file" == "$(realpath "$tmp_dir")/.herdr-runs/run-test-a1/controller-binding.json" ]] || fail "controller binding should return the canonical envelope path"
  [[ -f "$binding_envelope_file" && ! -L "$binding_envelope_file" ]] || fail "controller binding should create a regular non-symlink envelope"
  binding_file_mode="$(stat -f '%Lp' "$binding_envelope_file" 2>/dev/null || stat -c '%a' "$binding_envelope_file")"
  binding_dir_mode="$(stat -f '%Lp' "$(dirname "$binding_envelope_file")" 2>/dev/null || stat -c '%a' "$(dirname "$binding_envelope_file")")"
  binding_file_mode="${binding_file_mode: -3}"
  binding_dir_mode="${binding_dir_mode: -3}"
  [[ "$binding_file_mode" == "600" ]] || fail "controller binding envelope should be owner-only"
  [[ "$binding_dir_mode" == "700" ]] || fail "controller binding run directory should be owner-only"
  assert_json "$(<"$binding_envelope_file")" '.schema_version == 1 and .artifact_kind == "controller-binding-envelope"' "controller binding should be schema-versioned"
  assert_json "$(<"$binding_envelope_file")" '.controller.controller_id == "controller-test" and .controller.run_id == "run-test-a1" and .controller.run_nonce == "nonce-test-a1"' "controller identity and nonce should be bound"
  assert_json "$(<"$binding_envelope_file")" '.provenance.plan_sha256 | length == 64' "controller binding should include the approved plan digest"
  assert_json "$(<"$binding_envelope_file")" '.provenance.ledger_sha256 | length == 64' "controller binding should include the canonical ledger digest"
  assert_json "$(<"$binding_envelope_file")" '.provenance.batch.batch_id == "P1" and .provenance.batch.selected_task_ids == ["task-1", "task-2"] and .provenance.batch.effective_width == 2' "controller binding should carry immutable batch provenance"
  assert_json "$(<"$binding_envelope_file")" '.batch_provenance == .provenance.batch and .batch_provenance.limiting_factors == ["batch_limit"]' "controller binding should expose complete capacity evidence"
  jq -e --arg repo_root "$(realpath "$tmp_dir")" '.provenance.canonical_repository == $repo_root' "$binding_envelope_file" >/dev/null || fail "controller binding should include the canonical repository"
  assert_json "$(<"$binding_envelope_file")" '.task.task_id == "task-1" and .task.status == "ready" and .task.attempt == 1 and .task.runtime_role == "worker"' "controller binding should preserve the selected ready task and derived role"
  assert_json "$(<"$binding_envelope_file")" '.task.touch_set == ["src/example.py", "tests/test_example.py"] and .task.oracle_refs == ["bash test.sh"]' "controller binding should include the immutable touch set and oracle refs"
  assert_json "$(<"$binding_envelope_file")" '.physical_binding.terminal_backend == "herdr" and .physical_binding.capability_profile == "delegated-local-writer"' "controller binding should preserve the validated physical binding"
  assert_json "$(<"$binding_envelope_file")" '.physical_binding.agent_name == "worker-lynx-cb-ttask-1-a1"' "controller binding should persist only the deterministic agent name"
  assert_json "$(<"$binding_envelope_file")" '.authority.adapter_capabilities == ["consume-binding", "manage-run-owned-terminal-resources", "persist-adapter-state"] and (.authority.denied_capabilities | index("mutate-task-ledger")) != null and (.authority.denied_capabilities | index("derive-lifecycle-tail")) != null' "controller binding should deny lifecycle authority"
  assert_json "$(<"$binding_envelope_file")" '[paths(scalars) as $p | getpath($p) | strings | test("must-not-persist|prompt"; "i")] | all(. == false)' "controller binding should exclude credential material and prompt content"

  golden_repo="$(realpath "$tmp_dir")"
  golden_revision="$(git -C "$tmp_dir" rev-parse HEAD)"
  golden_plan_sha="$(harness_file_sha256 "$parallel_plan")"
  golden_ledger_sha="$(jq -cS . "$ledger_file" | shasum -a 256 | awk '{print $1}')"
  golden_expected="$(render_golden_envelope "$GOLDEN_HERDR_DELEGATED_TEMPLATE" "$golden_repo" "$tmp_dir" "$golden_revision" "$golden_plan_sha" "$golden_ledger_sha")"
  [[ "$(<"$binding_envelope_file")" == "$golden_expected" ]] \
    || fail "flag-absent delegated envelope must stay byte-identical to the schema_version-1 golden"
  binding_envelope_file="$(cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$binding_request_file" herdr)"
  [[ "$(<"$binding_envelope_file")" == "$golden_expected" ]] \
    || fail "explicit --backend herdr delegated envelope must stay byte-identical to the schema_version-1 golden"
  backend_stop="$( (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$binding_request_file" tmux) 2>&1 >/dev/null )" \
    && fail "unknown runtime binding backend must be rejected"
  [[ "$backend_stop" == controller_binding_backend_unsupported:* ]] \
    || fail "unknown backend rejection must be the typed backend-unsupported stop"
  backend_stop="$( (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$binding_request_file" codex-native) 2>&1 >/dev/null )" \
    && fail "codex-native must reject a herdr-shaped physical binding request"
  [[ "$backend_stop" == controller_binding_invalid:* ]] \
    || fail "codex-native rejection of a herdr-shaped request must be the typed malformed-binding stop"
  binding_envelope_file="$(cd "$tmp_dir" && bash "$HARNESS_LIB_ROOT/execute-runner.sh" controller-binding-envelope "$parallel_plan" "$ledger_file" "$binding_request_file" --backend herdr)"
  [[ "$(<"$binding_envelope_file")" == "$golden_expected" ]] \
    || fail "CLI --backend herdr dispatch must emit the byte-identical schema_version-1 golden"
  if (cd "$tmp_dir" && bash "$HARNESS_LIB_ROOT/execute-runner.sh" controller-binding-envelope "$parallel_plan" "$ledger_file" "$binding_request_file" --wrong herdr) >/dev/null 2>&1; then
    fail "CLI dispatch must reject a malformed backend flag with usage"
  fi

  command_request_file="$tmp_dir/command-job-request.json"
  jq --arg cwd "$(realpath "$tmp_dir")" '
    .binding_kind = "command-job"
    | .run_id = "command-run-a1"
    | .physical_binding = {
        terminal_backend: "herdr",
        workspace_id: "workspace-test",
        tab_id: "tab-controller-test",
        pane_id: "pane-controller-test",
        checkout_path: $cwd
      }
    | .command_job = {
        cwd: $cwd,
        argv: ["bash", "test.sh"],
        command: "bash test.sh",
        timeout_seconds: 60,
        max_concurrency: 1,
        output_bound_bytes: 8192,
        resource_locks: ["example-state"],
        provenance: {kind: "task", task_id: "task-1"}
      }
  ' "$binding_request_file" >"$command_request_file"
  command_envelope_file="$(cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$command_request_file")"
  jq -e --arg cwd "$(realpath "$tmp_dir")" '.controller.binding_kind == "command-job" and .command_job.cwd == $cwd and .command_job.argv == ["bash", "test.sh"] and .command_job.resource_locks == ["example-state"]' "$command_envelope_file" >/dev/null || fail "command-job envelope should pin cwd, argv, and exact locks"
  jq -e '.authority.denied_capabilities | index("claim-task-success") != null' "$command_envelope_file" >/dev/null || fail "command-job envelope must deny task-success claims for adapter compatibility"
  HERDR_ENV=1 \
    HERDR_WORKSPACE_ID="workspace-test" \
    HERDR_TAB_ID="tab-controller-test" \
    HERDR_PANE_ID="pane-controller-test" \
    python3 "$ROOT_DIR/src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py" \
      preflight \
      --envelope "$command_envelope_file" \
      --herdr-executable "$ROOT_DIR/tests/fixtures/herdr/fake-herdr.py" \
      >/dev/null || fail "runner-issued command envelope must be accepted by the Herdr adapter"
  assert_json "$(<"$command_envelope_file")" '.physical_binding | keys == ["checkout_path", "pane_id", "tab_id", "terminal_backend", "workspace_id"]' "command-job envelope must not invent agent binding content"
  golden_expected="$(render_golden_envelope "$GOLDEN_HERDR_COMMAND_TEMPLATE" "$golden_repo" "$tmp_dir" "$golden_revision" "$golden_plan_sha" "$golden_ledger_sha")"
  [[ "$(<"$command_envelope_file")" == "$golden_expected" ]] \
    || fail "herdr command-job envelope must stay byte-identical to the schema_version-1 golden"
  if jq '.run_id = "command-injection" | .command_job.command = "bash test.sh; touch injected"' "$command_request_file" >"$tmp_dir/command-injection.json" \
    && (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/command-injection.json") >/dev/null 2>&1; then
    fail "command-job should reject shell interpolation"
  fi
  [[ ! -e "$tmp_dir/injected" ]] || fail "command-job rejection must not execute untrusted interpolation"
  if jq '.run_id = "command-foreign-cwd" | .command_job.cwd = "/tmp"' "$command_request_file" >"$tmp_dir/command-foreign-cwd.json" \
    && (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/command-foreign-cwd.json") >/dev/null 2>&1; then
    fail "command-job should reject foreign cwd"
  fi

  jq '.run_id = "forged-batch-membership" | .batch_provenance.selected_task_ids = ["task-1", "task-3"]' "$binding_request_file" >"$tmp_dir/forged-batch-membership.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/forged-batch-membership.json") >/dev/null 2>&1; then
    fail "controller binding should reject forged selected task membership"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/forged-batch-membership" ]] || fail "forged batch membership must fail before output mutation"

  jq '.run_id = "forged-effective-width" | .batch_provenance.effective_width = 1' "$binding_request_file" >"$tmp_dir/forged-effective-width.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/forged-effective-width.json") >/dev/null 2>&1; then
    fail "controller binding should reject forged effective width"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/forged-effective-width" ]] || fail "forged effective width must fail before output mutation"

  jq '.run_id = "forged-batch-identity" | .batch_id = "P2" | .batch_provenance.batch_id = "P2" | .batch_provenance.parallel_group = "P2"' "$binding_request_file" >"$tmp_dir/forged-batch-identity.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/forged-batch-identity.json") >/dev/null 2>&1; then
    fail "controller binding should reject forged batch identity"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/forged-batch-identity" ]] || fail "forged batch identity must fail before output mutation"

  jq '.run_id = "forged-unselected-task" | .task_id = "task-3"' "$binding_request_file" \
    | jq --arg agent_name "$(execution_herdr_agent_name worker forged-unselected-task task-3 1)" '.physical_binding.agent_name = $agent_name' \
    >"$tmp_dir/forged-unselected-task.json"
  if (cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$ledger_file" "$tmp_dir/forged-unselected-task.json") >/dev/null 2>&1; then
    fail "controller binding should reject an unselected task from the approved batch"
  fi
  [[ ! -e "$tmp_dir/.herdr-runs/forged-unselected-task" ]] || fail "unselected task must fail before output mutation"

  jq 'map(.status = "done" | .convergence_verified = true)' "$ledger_file" >"$tmp_dir/review-ready-ledger.json"
  printf '%s\n' 'Bounded implementation review fixture.' >"$tmp_dir/review-brief.md"
  chmod 600 "$tmp_dir/review-brief.md"
  binding_ledger_digest="$(jq -cS . "$tmp_dir/review-ready-ledger.json" | shasum -a 256 | awk '{print $1}')"
  review_brief_digest="$(harness_file_sha256 "$tmp_dir/review-brief.md")"
  reviewer_agent_name="$(execution_herdr_agent_name reviewer run-review-a1 implementation-review 1)"
  jq \
    --arg ledger_sha256 "$binding_ledger_digest" \
    --arg review_brief_path "$tmp_dir/review-brief.md" \
    --arg review_brief_sha256 "$review_brief_digest" \
    --arg agent_name "$reviewer_agent_name" \
    --arg checkout_path "$(realpath "$tmp_dir")" \
    '.binding_kind = "bounded-review"
      | .run_id = "run-review-a1"
      | .task_id = "implementation-review"
      | .expected_ledger_sha256 = $ledger_sha256
      | .review_brief_path = $review_brief_path
      | .review_brief_sha256 = $review_brief_sha256
      | .physical_binding.agent_name = $agent_name
      | .physical_binding.model = "gpt-5.6-sol"
      | .physical_binding.reasoning_effort = "high"
      | .physical_binding.sandbox_mode = "read-only"
      | .physical_binding.capability_profile = "delegated-read-only"
      | .physical_binding.checkout_path = $checkout_path' \
    "$binding_request_file" >"$tmp_dir/reviewer-binding-request.json"
  reviewer_envelope_file="$(cd "$tmp_dir" && execution_controller_binding_envelope "$parallel_plan" "$tmp_dir/review-ready-ledger.json" "$tmp_dir/reviewer-binding-request.json")"
  assert_json "$(<"$reviewer_envelope_file")" '.controller.binding_kind == "bounded-review" and .task.runtime_role == "reviewer" and .task.touch_set == [] and .task.review_brief_sha256 != null' "controller binding should issue a bounded reviewer envelope after convergence"
  golden_review_ledger_sha="$(jq -cS . "$tmp_dir/review-ready-ledger.json" | shasum -a 256 | awk '{print $1}')"
  golden_brief_sha="$(harness_file_sha256 "$tmp_dir/review-brief.md")"
  golden_expected="$(render_golden_envelope "$GOLDEN_HERDR_REVIEW_TEMPLATE" "$golden_repo" "$tmp_dir" "$golden_revision" "$golden_plan_sha" "$golden_ledger_sha" "$golden_review_ledger_sha" "$golden_brief_sha")"
  [[ "$(<"$reviewer_envelope_file")" == "$golden_expected" ]] \
    || fail "herdr bounded-review envelope must stay byte-identical to the schema_version-1 golden"

  # --- codex-native backend: role-file validation, typed stops, schema_version 2 emission ---

  codex_fixtures="$ROOT_DIR/tests/fixtures/codex-agents"
  codex_home_valid="$codex_fixtures/codex-home-valid"

  for role_fixture in "$codex_fixtures"/valid/agents/*.toml; do
    python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$role_fixture" \
      || fail "valid codex role fixture must parse with tomllib: $role_fixture"
  done
  for role_fixture in "$codex_fixtures"/invalid/*.toml; do
    if [[ "$role_fixture" == */unparsable.toml ]]; then
      if python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$role_fixture" 2>/dev/null; then
        fail "unparsable codex role fixture must fail tomllib parsing"
      fi
    else
      python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$role_fixture" \
        || fail "semantically invalid codex role fixture must still parse with tomllib: $role_fixture"
    fi
  done

  if compgen -G "$GENERATED_SKILLS_ROOT/*/agents/*.toml" >/dev/null 2>&1 \
    || compgen -G "$GENERATED_SKILLS_ROOT/.codex/agents/*.toml" >/dev/null 2>&1; then
    fail "tracked plugin payload must not ship role agent files"
  fi

  codex_plan="$tmp_dir/codex-plan.md"
  cat >"$codex_plan" <<'EOF'
# Codex Native Plan

## Upstream Design

- design_ref: design.md
- design_version: 2026-08-17-v1

## Implementation Scope

- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`

## Work Package Readiness

- milestone_objective: bind delegated tasks through the codex-native backend
- non_goals:
  - no deployment
- future_phase:
  - no follow-up phase
- decision_status: ready_for_review
- oracle_strategy: contract tests for envelope emission
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

## Review Gate

- required_entry: review-change
- required_mode: review-only

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Task 1: Codex Worker

- task_id: task-w
- depends_on:
  - root
- scope_slice: worker implementation slice
- impl_file_refs:
  - src/example.py
- test_file_refs:
  - tests/test_example.py
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - example-state
- task_review_depth: full
- done_when:
  - worker verification passes
- failure_policy: fix_forward
- [ ] Implement worker slice

## Task 2: Codex Explorer

- task_id: task-e
- depends_on:
  - root
- scope_slice: bounded factual confirmation slice
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: light
- isolation: shared-read-only
- resource_locks:
  - explorer-evidence
- task_review_depth: focused
- done_when:
  - bounded facts returned
- failure_policy: fix_forward
- [ ] Confirm facts

## Task 3: Codex Read-Only Deep

- task_id: task-r
- depends_on:
  - root
- scope_slice: deep read-only analysis slice
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - `bash test.sh`
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: shared-read-only
- resource_locks:
  - analysis-evidence
- task_review_depth: focused
- done_when:
  - bounded analysis returned
- failure_policy: fix_forward
- [ ] Analyze deeply

## Recovery

- default_failure_policy: fix_forward
EOF

  git -C "$tmp_dir" add codex-plan.md
  git -C "$tmp_dir" \
    -c user.name="Harness Fixture" \
    -c user.email="harness@example.invalid" \
    commit -qm "codex plan fixture"
  golden_revision="$(git -C "$tmp_dir" rev-parse HEAD)"

  mkdir -p "$tmp_dir/.codex/agents"
  cp "$codex_fixtures"/valid/agents/*.toml "$tmp_dir/.codex/agents/"

  codex_plan_sha="$(harness_file_sha256 "$codex_plan")"
  codex_ledger="$tmp_dir/codex-ledger.json"
  execution_task_ledger "$codex_plan" >"$codex_ledger"
  codex_ledger_sha="$(jq -cS . "$codex_ledger" | shasum -a 256 | awk '{print $1}')"
  jq 'map(.status = "done" | .convergence_verified = true)' "$codex_ledger" >"$tmp_dir/codex-done-ledger.json"
  codex_done_ledger_sha="$(jq -cS . "$tmp_dir/codex-done-ledger.json" | shasum -a 256 | awk '{print $1}')"

  run_codex_envelope() {
    local home_dir="$1"
    local ledger_ref="$2"
    local request_ref="$3"
    (cd "$tmp_dir" && CODEX_HOME="$home_dir" execution_controller_binding_envelope "$codex_plan" "$ledger_ref" "$request_ref" codex-native)
  }

  expect_codex_stop() {
    local home_dir="$1"
    local ledger_ref="$2"
    local request_ref="$3"
    local expected_prefix="$4"
    local message="$5"
    local stop_output=""

    stop_output="$(run_codex_envelope "$home_dir" "$ledger_ref" "$request_ref" 2>&1 >/dev/null)" \
      && fail "$message"
    [[ "$stop_output" == "$expected_prefix"* ]] || fail "$message (typed stop was: $stop_output)"
  }

  codex_request="$tmp_dir/codex-request.json"
  write_codex_request "$codex_request" codex-w1 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  binding_ledger_before="$(harness_file_sha256 "$codex_ledger")"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
  binding_ledger_after="$(harness_file_sha256 "$codex_ledger")"
  [[ "$binding_ledger_before" == "$binding_ledger_after" ]] || fail "codex-native binding must not mutate the task ledger"
  [[ "$codex_envelope_file" == "$(realpath "$tmp_dir")/.codex-native-runs/codex-w1/controller-binding.json" ]] \
    || fail "codex-native binding should return the canonical codex-native envelope path"
  assert_json "$(<"$codex_envelope_file")" '.schema_version == 2 and .artifact_kind == "controller-binding-envelope"' "codex-native envelope should be schema-version 2"
  assert_json "$(<"$codex_envelope_file")" '.core.controller.binding_kind == "delegated-task" and .core.controller.model_policy == "semantic-routing" and .core.task.task_id == "task-w" and .core.task.runtime_role == "worker"' "codex-native core should carry the neutral controller and task projection"
  assert_json "$(<"$codex_envelope_file")" '.core.provenance.plan_sha256 | length == 64' "codex-native core should bind the approved plan digest"
  assert_json "$(<"$codex_envelope_file")" '.backend.backend_kind == "codex-native"' "codex-native envelope should name its backend extension"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.role == "worker" and .backend.extension.role_agent_file == "worker.toml" and .backend.extension.role_agent_file_source == "project" and .backend.extension.expected_sandbox_mode == "workspace-write"' "codex-native extension should record the validated role agent file"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.concurrency_ceiling == 4 and .backend.extension.max_depth == 1 and .backend.extension.max_depth_enforcement == "validated"' "codex-native extension should record validated concurrency and recursion limits"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.requested_model == "example-model" and .backend.extension.requested_reasoning_effort == "high" and .backend.extension.resolution_source == "per-spawn" and .backend.extension.spawn_cwd_supported == true' "codex-native extension should record per-spawn resolution evidence"
  assert_json "$(<"$codex_envelope_file")" '[.core | .. | strings] | all(. != "example-model")' "the neutral envelope core must not carry provider model identifiers"
  assert_json "$(<"$codex_envelope_file")" '.core | has("physical_binding") | not' "the neutral envelope core must not embed backend physical bindings"

  codex_envelope_file="$(cd "$tmp_dir" && CODEX_HOME="$codex_home_valid" bash "$HARNESS_LIB_ROOT/execute-runner.sh" controller-binding-envelope "$codex_plan" "$codex_ledger" "$codex_request" --backend codex-native)"
  assert_json "$(<"$codex_envelope_file")" '.schema_version == 2 and .backend.backend_kind == "codex-native"' "CLI --backend codex-native dispatch should emit the schema-version 2 envelope"

  write_codex_request "$codex_request" codex-e1 task-e semantic-routing "" "" parent-inherit true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.core.task.runtime_role == "explorer" and .backend.extension.role_agent_file == "explorer.toml" and .backend.extension.expected_sandbox_mode == "read-only" and .backend.extension.requested_model == null and .backend.extension.requested_reasoning_effort == null and .backend.extension.resolution_source == "parent-inherit"' "codex-native explorer should inherit through the pin-free read-only explorer role file"

  write_codex_request "$codex_request" codex-e2 task-e semantic-routing "" high per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.requested_model == null and .backend.extension.requested_reasoning_effort == "high" and .backend.extension.resolution_source == "per-spawn"' "semantic routing should accept an effort-only uplift"

  for supported_effort in max ultra; do
    write_codex_request "$codex_request" "codex-e-$supported_effort" task-e semantic-routing example-model "$supported_effort" per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha"
    codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
    assert_json_arg "$(<"$codex_envelope_file")" effort "$supported_effort" '.backend.extension.requested_reasoning_effort == $effort' "semantic routing should accept supported effort above the role floor"
  done

  printf '%s\n' 'Bounded codex review brief.' >"$tmp_dir/codex-review-brief.md"
  chmod 600 "$tmp_dir/codex-review-brief.md"
  codex_brief_sha="$(harness_file_sha256 "$tmp_dir/codex-review-brief.md")"
  write_codex_request "$codex_request" codex-r1 implementation-review semantic-routing example-model high per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_done_ledger_sha" bounded-review "$tmp_dir/codex-review-brief.md" "$codex_brief_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$tmp_dir/codex-done-ledger.json" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.core.task.runtime_role == "reviewer" and .backend.extension.role_agent_file == "reviewer.toml" and .backend.extension.expected_sandbox_mode == "read-only" and .core.task.review_brief_sha256 != null' "codex-native bounded review should bind through the read-only reviewer role file"

  write_codex_request "$codex_request" codex-w2 task-w inherit-main "" "" parent-inherit true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.requested_model == null and .backend.extension.requested_reasoning_effort == null and .backend.extension.resolution_source == "parent-inherit" and .backend.extension.role_agent_file == "worker.toml"' "inherit-main must spawn through the same validated role file without per-spawn values"

  write_codex_request "$codex_request" codex-w3 task-w runtime-default "" "" parent-inherit true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_home_valid" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.resolution_source == "parent-inherit" and .backend.extension.role_agent_file == "worker.toml"' "runtime-default should record parent inheritance when both agents defaults are absent"

  write_codex_request "$codex_request" codex-w4 task-w runtime-default "" "" agents-defaults true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_fixtures/codex-home-defaults" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.resolution_source == "agents-defaults"' "runtime-default should record agents defaults when configured"

  write_codex_request "$codex_request" codex-w4-lower task-w runtime-default "" "" parent-inherit true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha" delegated-task "" "" true low high
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_required_uplift_below_floor:" "runtime-default without agents defaults must reject parent reasoning below the active minimum"

  write_codex_request "$codex_request" codex-nd1 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_fixtures/codex-home-no-depth" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.max_depth == null and .backend.extension.max_depth_enforcement == "instruction-only" and .backend.extension.concurrency_ceiling == null' "unconfigured max_depth must be recorded as residual instruction-only enforcement"

  write_codex_request "$codex_request" codex-s1 task-w semantic-routing example-model "" per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_model_policy_mismatch:" "semantic-routing model change without explicit effort must return the typed model-policy mismatch"

  write_codex_request "$codex_request" codex-s2 task-w inherit-main example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_model_policy_mismatch:" "inherit-main with per-spawn values must return the typed model-policy mismatch"

  write_codex_request "$codex_request" codex-s3 task-e semantic-routing "" high per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha" delegated-task "" "" false
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_required_uplift_unsupported:" "rejected effort-only uplift must stop without downgrade or output"

  write_codex_request "$codex_request" codex-s3-model task-e semantic-routing example-model high per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha" delegated-task "" "" false
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_required_uplift_unsupported:" "rejected model-plus-effort uplift must stop without downgrade or output"

  write_codex_request "$codex_request" codex-s3-lower task-e semantic-routing "" low per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha" delegated-task "" "" true high medium
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_required_uplift_below_floor:" "an effort-only request below the inherited parent must stop before output"

  write_codex_request "$codex_request" codex-s4 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_fixtures/codex-home-disabled" "$codex_ledger" "$codex_request" "controller_binding_multi_agent_disabled:" "a disabled multi-agent feature must return the typed capability stop"
  expect_codex_stop "$codex_fixtures/codex-home-bad-depth" "$codex_ledger" "$codex_request" "controller_binding_max_depth_invalid:" "a configured max_depth other than 1 must return the typed capability stop"
  expect_codex_stop "$codex_fixtures/codex-home-false-depth" "$codex_ledger" "$codex_request" "controller_binding_max_depth_invalid:" "a boolean max_depth must return the typed capability stop instead of instruction-only residual"

  write_codex_request "$codex_request" codex-s10 task-r semantic-routing example-model high per-spawn false "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_isolation_conflict:" "a zero-write delegated task must not bind a workspace-write role sandbox on the shared checkout"

  write_codex_request "$codex_request" codex-s5 task-w semantic-routing example-model high per-spawn false "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_spawn_cwd_unsupported:" "a delegated writer without per-spawn cwd support must return the typed capability stop"

  jq --arg cwd "$(realpath "$tmp_dir")" '
    .binding_kind = "command-job"
    | .run_id = "codex-s6"
    | .command_job = {
        cwd: $cwd,
        argv: ["bash", "test.sh"],
        timeout_seconds: 60,
        max_concurrency: 1,
        output_bound_bytes: 8192,
        resource_locks: ["example-state"],
        provenance: {kind: "task", task_id: "task-w"}
      }
  ' "$codex_request" >"$tmp_dir/codex-command-request.json"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$tmp_dir/codex-command-request.json" "controller_binding_unsupported_combination:" "command-job on the codex-native backend must return the typed unsupported-combination stop"

  write_codex_request "$codex_request" codex-s7 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  rm "$tmp_dir/.codex/agents/worker.toml"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_role_file_missing:" "a missing role agent file must return the typed missing stop"
  cp "$codex_fixtures/invalid/unparsable.toml" "$tmp_dir/.codex/agents/worker.toml"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_role_file_unparsable:" "an unparsable role agent file must return the typed unparsable stop"
  cp "$codex_fixtures/invalid/worker-read-only-sandbox.toml" "$tmp_dir/.codex/agents/worker.toml"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_isolation_conflict:" "a read-only worker sandbox must return the typed isolation conflict stop"
  cp "$codex_fixtures/invalid/worker-effort-pin.toml" "$tmp_dir/.codex/agents/worker.toml"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_role_file_forbidden_pin:" "a worker effort pin must return the typed forbidden-pin stop"
  cp "$codex_fixtures/valid/agents/worker.toml" "$tmp_dir/.codex/agents/worker.toml"

  write_codex_request "$codex_request" codex-s8 implementation-review semantic-routing example-model high per-spawn true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_done_ledger_sha" bounded-review "$tmp_dir/codex-review-brief.md" "$codex_brief_sha"
  cp "$codex_fixtures/invalid/reviewer-missing-sandbox.toml" "$tmp_dir/.codex/agents/reviewer.toml"
  expect_codex_stop "$codex_home_valid" "$tmp_dir/codex-done-ledger.json" "$codex_request" "controller_binding_role_file_missing_required_field:" "a parsable reviewer file omitting sandbox_mode must return the typed missing-required-field stop"
  cp "$codex_fixtures/invalid/reviewer-model-pin.toml" "$tmp_dir/.codex/agents/reviewer.toml"
  expect_codex_stop "$codex_home_valid" "$tmp_dir/codex-done-ledger.json" "$codex_request" "controller_binding_role_file_forbidden_pin:" "a reviewer model pin must return the typed forbidden-pin stop"
  cp "$codex_fixtures/invalid/reviewer-writable-sandbox.toml" "$tmp_dir/.codex/agents/reviewer.toml"
  expect_codex_stop "$codex_home_valid" "$tmp_dir/codex-done-ledger.json" "$codex_request" "controller_binding_role_file_sandbox_writable:" "a writable reviewer sandbox must return the typed writable-sandbox stop"
  cp "$codex_fixtures/valid/agents/reviewer.toml" "$tmp_dir/.codex/agents/reviewer.toml"

  write_codex_request "$codex_request" codex-s9 task-e semantic-routing "" "" parent-inherit true "$(realpath "$tmp_dir")" "$codex_plan_sha" "$codex_ledger_sha"
  cp "$codex_fixtures/invalid/explorer-effort-pin.toml" "$tmp_dir/.codex/agents/explorer.toml"
  expect_codex_stop "$codex_home_valid" "$codex_ledger" "$codex_request" "controller_binding_role_file_forbidden_pin:" "an explorer effort pin must return the generic typed forbidden-pin stop"
  cp "$codex_fixtures/valid/agents/explorer.toml" "$tmp_dir/.codex/agents/explorer.toml"

  codex_user_home="$tmp_dir/.fixture-codex-home"
  mkdir -p "$codex_user_home/agents"
  cp "$codex_home_valid/config.toml" "$codex_user_home/config.toml"
  cp "$codex_fixtures/valid/agents/worker.toml" "$codex_user_home/agents/worker.toml"
  rm "$tmp_dir/.codex/agents/worker.toml"
  write_codex_request "$codex_request" codex-u1 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_user_home" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.role_agent_file_source == "user"' "role file resolution must fall back to the user-level agents directory"
  ln -s "$codex_user_home/agents/worker.toml" "$tmp_dir/.codex/agents/worker.toml"
  write_codex_request "$codex_request" codex-u2 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  expect_codex_stop "$codex_user_home" "$codex_ledger" "$codex_request" "controller_binding_role_file_missing:" "a symlinked project role file must return the typed missing stop instead of silent user fallback"
  rm "$tmp_dir/.codex/agents/worker.toml"
  cp "$codex_fixtures/valid/agents/worker.toml" "$tmp_dir/.codex/agents/worker.toml"
  write_codex_request "$codex_request" codex-u3 task-w semantic-routing example-model high per-spawn true "$binding_worker_dir" "$codex_plan_sha" "$codex_ledger_sha"
  codex_envelope_file="$(run_codex_envelope "$codex_user_home" "$codex_ledger" "$codex_request")"
  assert_json "$(<"$codex_envelope_file")" '.backend.extension.role_agent_file_source == "project"' "a project role file must take precedence over a user-level role file"

  [[ ! -e "$tmp_dir/.codex-native-runs/codex-w4-lower" && ! -e "$tmp_dir/.codex-native-runs/codex-s1" && ! -e "$tmp_dir/.codex-native-runs/codex-s3" && ! -e "$tmp_dir/.codex-native-runs/codex-s3-model" && ! -e "$tmp_dir/.codex-native-runs/codex-s3-lower" && ! -e "$tmp_dir/.codex-native-runs/codex-s7" ]] \
    || fail "typed codex-native stops must fail before output mutation"

  declare -F execution_controller_binding_envelope >/dev/null || fail "controller-binding-envelope API should be available"

  printf '%s\n' "$(execution_task_ledger "$external_plan")" >"$external_ledger"
  jq 'map(.status = "in_progress")' "$external_ledger" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  execution_external_baseline "$external_plan" "$external_ledger" "external-task" "external-run-1" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  execution_external_prepare "$external_plan" "$external_ledger" "external-task" "$external_run_dir" "$external_target" "intent-1" "$external_payload" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  execution_external_apply "$external_plan" "$external_ledger" "external-task" "intent-1" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  jq 'map(.status = "in_review")' "$external_ledger" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  execution_controller_converge "$external_plan" "$external_ledger" "external-task" "controller" "true" "true" >"$external_tmp/ledger-next.json"
  mv "$external_tmp/ledger-next.json" "$external_ledger"
  execution_result_json="$(build_execution_result_json "$external_plan" "$external_ledger" "verify" "" "truth_sync_required" "pass" "pass" "sync-truth" "truth-sync" "false" "$workspace_mode")"
  assert_json_arg "$execution_result_json" ref "$external_target" '.allowed_external_touch_refs == [$ref]' "execution result should bind the exact external touch set"
  assert_json "$execution_result_json" '.verified_external_changes[0].task_id == "external-task" and .verified_external_changes[0].manifest.refs[0].changed == true' "execution result should expose metadata-only verified external changes separately"
  assert_json "$execution_result_json" '[.task_evidence[] | .verified_changed_paths[]?] | all(startswith("/") | not)' "repository changed-path evidence must not contain external refs"
  execution_external_cleanup "$external_ledger" "external-task" "intent-1" >/dev/null

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
