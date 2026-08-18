# Parent-Inherited Codex Subagent Routing E2 Plan

## Status

- plan_version: 2
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: pending
- plan_review_status: passed_after_focused_repair
- implementation_review_status: pending
- implementation_verification_status: pending
- recommended_next_phase: implement
- next_entry: implement-change

## Upstream Design

- design_ref: 2026-08-18-parent-inherited-codex-subagent-routing-e2-design.md
- design_version: sha256:c5ca7faf092d67c2f0ad104d3f77ea7fe1363c8a5a5feca49d623f227e17707c
- design_approval_status: approved
- architecture_decision_ref: CODEX-NATIVE-BIND-001
- boundary_decision_ref: CODEX-NATIVE-USER-ROUTE-002
- user_route_input_ref: 2026-08-18-codex-subagent-user-route-input.md
- user_route_input_version: sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df

## Implementation Scope

- target_repository: market-csheng plus three exact user-owned Codex-home files
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- external_touch_policy: exact-existing-files-v1
- execution_continuity: continuous_after_plan_approval
- input_file_refs:
  - docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
- external_impl_file_refs:
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/fixtures/codex-agents
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
- verification_commands:
  - `bash -n src/runtime/harness/execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `python3 -m unittest tests.test_skill_workflow_contracts tests.test_parallel_execution_contracts`
  - `python3 -m unittest tests.test_implement_change_via_herdr_contracts`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash scripts/check.sh`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Replace Codex-native explorer ceilings and role pins with parent-baseline
  routing plus user-owned minimum reasoning floors, then apply the exact user-home policy through
  the E1 external broker.
- non_goals:
  - Change topology, lifecycle authority, role permissions, Herdr allocation, provider envelopes,
    plugin state, version metadata, commit, push, publication, or live runtime state.
  - Put provider identifiers or personal floor values in reusable repository truth.
- future_phase:
  - Start a new Codex session and perform reviewer, worker, and explorer runtime acceptance.
- decision_status: ready_for_review
- oracle_strategy: Add state-transition and role-file contract oracles first, preserve Herdr golden
  behavior, validate candidates structurally and secret-safely, regenerate projections, and run
  focused plus aggregate gates.
- acceptance_oracles:
  - All valid native role files are pin-free; inheritance, effort-only uplift, and
    model-plus-effort uplift are accepted while model-only input and silent downgrade are rejected.
  - Explorer role authority remains bounded without a physical reasoning ceiling; higher supported
    efforts including max and ultra are accepted.
  - The exact user-route input digest is preserved; only approved keys or the delimited routing
    block change in user files; all unrelated content and metadata remain unchanged.
  - Generated surfaces reproduce from source, Herdr compatibility stays green, stable truth is
    synchronized, and close evidence is complete.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1
- binding_contract: All implementation tasks are serial and main-owned. Portable execution and
  reasoning profiles express task difficulty only. Runtime physical selection starts from the
  parent profile; it emits no override, effort only, or model plus explicit effort as required.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Plan approval authorizes NSR-010 through NSR-040 plus bounded implementation review,
    including the exact three user-home files. Truth sync and close remain separate typed gates; the
    user's explicit `approve all` and `finally close-change` instructions may bind only after each
    required artifact or decision input has materialized and passed its own validation/review.
- runtime_contingencies:
  - X1: Stop before mutation on source, route-input digest, exact-path, ownership, mode, or baseline
    drift.
  - X2: Return `needs-design-decision` if the neutral envelope, topology, role authority, or Herdr
    contract must change.
  - X3: Return `controller_binding_required_uplift_unsupported` when a required native uplift is
    rejected; never retry through defaults or below the floor.
- planned_stop_points:
  - Stop at the truth-sync approval gate after implementation review passes.
  - Stop again at the close decision gate after approved truth sync and aggregate verification.
- task_ordering_rationale: Establish executable native oracles first, align source policy second,
  regenerate projections third, and mutate the user-owned runtime policy last through the broker.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Preserve unrelated user and repository changes; operate only on declared refs.
- oracle_boundary: Do not weaken topology, sandbox, recursion, forbidden-pin, Herdr, or
  unrelated-content preservation assertions.
- external_boundary: Use only prepared/applied E1 broker intents and stop on compare-and-swap drift.
- guarded_rollback: none

## Task 1: Change native binding oracles and validation

- task_id: NSR-010
- depends_on:
  - none
- scope_slice: Add failing pin-free role and parent-baseline routing cases, then update the native
  runner to accept no override, effort-only uplift, model-plus-effort uplift, and higher supported
  efforts while rejecting model-only input and unsupported required uplift without fallback.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- external_impl_file_refs:
  - none
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - tests/fixtures/codex-agents
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
- verification_scope:
  - Cover generic role-pin rejection, parent versus agents-default resolution evidence, max/ultra
    acceptance, model-only rejection, and both required-uplift rejection shapes before emission.
  - Prove topology, locks, isolation, and Herdr outputs remain unchanged.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - codex-native-binding-contract
- task_review_depth: full
- done_when:
  - Focused native binding and unchanged Herdr contract tests pass with pin-free valid fixtures.
- failure_policy: fix_forward

## Task 2: Decouple portable difficulty from physical effort

- task_id: NSR-020
- depends_on:
  - NSR-010
- scope_slice: Remove explorer physical cost ceilings and exact effort mappings from source-owned
  skills and workflow metadata while preserving factual read-only eligibility and main synthesis.
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
- external_impl_file_refs:
  - none
- test_file_refs:
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Assert parent baseline and three legal override shapes without provider identifiers or a role
    ceiling in reusable source.
  - Preserve explorer authority, topology, and portable difficulty metadata.
- failing_oracle_first: Update the focused skill/workflow contract assertions so the current
  low-cost ceiling and exact effort mapping fail before editing the three source-owned contracts.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - workflow-skill-contracts
- task_review_depth: deep
- done_when:
  - Focused plan and workflow contract tests pass with no native explorer physical ceiling.
- failure_policy: fix_forward

## Task 3: Regenerate implementation-owned surfaces

- task_id: NSR-030
- depends_on:
  - NSR-020
- scope_slice: Regenerate root-flat skills, indexes, and bundled execute runners from source, then
  run focused sovereign harness checks before any external mutation.
- impl_file_refs:
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
- external_impl_file_refs:
  - none
- test_file_refs:
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
- verification_scope:
  - Run both generators twice and prove the second run is deterministic.
  - Run all declared sovereign smoke tests and `git diff --check`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-skill-surface
- task_review_depth: deep
- done_when:
  - Generated source projections and all focused sovereign checks pass.
- failure_policy: fix_forward

## Task 4: Apply the user-level routing policy

- task_id: NSR-040
- depends_on:
  - NSR-030
- scope_slice: Through the exact-file broker, remove the two `[agents]` defaults, add one delimited
  global routing block, and remove explorer effort/low-cost pins while preserving unrelated content,
  ownership, mode, sandbox, and behavioral instructions.
- input_file_refs:
  - docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md
- user_route_input_version: sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df
- impl_file_refs:
  - none
- external_impl_file_refs:
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- test_file_refs:
  - none
- verification_scope:
  - Verify the exact route input ref and
    `sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df`
    before baseline capture; bind both values into candidate-validation evidence and final
    execution evidence while leaving the closed E1 prepared/applied intent schema unchanged.
  - Structurally prove only the two named default keys, explorer pin/description, and delimited
    routing block changed; parse all TOML and preserve `config.toml` mode `0600`.
  - Confirm reviewer, worker, and explorer role files remain pin-free with original sandboxes.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - user-codex-home-routing
- task_review_depth: focused
- done_when:
  - Metadata-only broker evidence retains the exact input ref/digest through convergence and
    secret-safe structural conformance passes for all exact refs.
- failure_policy: fix_forward

## Truth Sync Handoff

- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- truth_sync_impl_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
- truth_sync_verification_commands:
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash scripts/check.sh`
  - `git diff --check`
- handoff_scope: Synchronize stable provider-neutral truth for parent inheritance, pin-free role
  files, minimum-only user routing, legal uplift shapes, no silent downgrade, and unchanged topology,
  authority, and Herdr boundary; regenerate diagrams and SVGs from source.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_focused_repair
- review_evidence: The bounded reviewer found collapsed truth/close gates, missing route-digest propagation, premature implementation routing, and missing NSR-020 oracle ordering. Focused verification found one schema-expansion overreach. The accepted repairs restore separate gates, bind the exact route input before baseline and in final evidence without changing E1 intents, route through review until approval, and require failing workflow assertions before source edits. Main verification confirms validation and scope containment pass.
- review_budget: One bounded plan review and one focused verification review were consumed; the final same-slice schema correction was adjudicated and validated by the main controller.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user's explicit `approve all` instruction binds this reviewed plan on 2026-08-18.
- next_entry: implement-change
