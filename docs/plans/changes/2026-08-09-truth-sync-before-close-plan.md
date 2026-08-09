# Truth Sync Before Close Implementation Plan

## Upstream Design

- design_ref: 2026-08-09-truth-sync-before-close-design.md
- design_version: 1

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - contracts/skills.toml
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/sync-truth/SKILL.md
  - src/skills/workflows/close-change/SKILL.md
  - src/skills/disciplines/organize-docs/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
  - src/runtime/harness/execute-runner.sh
  - src/runtime/harness/evaluation-gate.sh
  - src/runtime/harness/truth-sync-runner.sh
  - src/runtime/harness/close-runner.sh
  - src/runtime/harness/phase-engine.sh
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/harness-state-machine.md
  - docs/architecture/maintenance-contract.md
  - docs/changelog/design-decisions.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills
  - skills.index.json
- test_file_refs:
  - scripts/check-contracts.py
  - scripts/generate-skills-index.py
  - scripts/flatten-skills.py
  - scripts/generate-workflow-diagrams.py
  - scripts/check.sh
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-kernel-phase.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
- verification_scope:
  - Preserve the pre-implementation status and content of every path outside the approved source, runtime, test, generated, and stable-truth surfaces.
  - Add deterministic red contract tests before changing plan validation, evidence binding, controller progression, docs-governance selection, or close behavior.
  - Reject missing or out-of-touch-set stable truth refs before execution and never infer a legacy missing declaration as `truth_sync_required: false`.
  - Derive close eligibility and exact artifact identity from the approved design, approved plan, immutable execution result, and approved truth-sync artifact; reject caller status overrides.
  - Keep direct explicit mutation and approved-controller mutation as distinct authorities, with conditional `organize-docs` constrained to the approved truth touch set.
  - Return a terminal closed result with no successful close self-route and keep merge, release, cleanup, commit, push, install, and deploy outside this judgment.
  - Regenerate all affected root-flat runtime bundles and architecture projections from source, then prove source/generated parity.
  - Run focused red-green tests, the sovereign harness smoke suite, aggregate validation, whitespace validation, bounded implementation review, and the required pre-close truth-sync gate.

## Work Package Readiness

- milestone_objective: Make a truth-affecting approved implementation advance through evidence-bound stable truth synchronization before close approval, keep docs organization conditional, and make successful close terminal.
- non_goals:
  - No new public lifecycle owner, closeout controller, provider command, background runner, recursive skill graph, or unattended execution mode.
  - No mutation inside `close-change` and no automatic merge, release, cleanup, commit, push, install, deploy, rollback, or destructive workspace action.
  - No default repository-wide `organize-docs` pass and no opportunistic Markdown normalization outside declared truth refs.
  - No change to implementation-review ownership, parallel execution, model routing, worker isolation, repair budgets, or recovery-policy semantics.
  - No compatibility path that treats caller booleans or a legacy artifact without stable truth scope as trustworthy lifecycle evidence.
- future_phase:
  - A separate external-action owner may be designed only if merge, release, or cleanup later needs durable execution state, resumability, and recovery semantics.
  - General stage-artifact migration, docs-layout cleanup, plugin installation, versioning, and distribution remain separately authorized work.
- decision_status: ready_for_review
- oracle_strategy: Characterization-first state-machine and artifact-contract TDD over structured runner inputs and outputs, followed by model-based transition checks, generated parity, aggregate repository validation, and bounded agent-native review; do not freeze natural-language Markdown wording as the behavioral oracle.
- acceptance_oracles:
  - Current code first produces narrow red evidence for caller-overridden close status, successful `close -> close`, absent required stable truth scope, incomplete controller mutation context, and unconditional or out-of-scope docs composition.
  - Version-2 plan validation requires non-empty stable truth refs for truth-affecting work, rejects stage-artifact refs and refs outside the immutable plan touch set, and preserves an explicit typed planning route for incomplete legacy inputs.
  - Execution evidence represents task completion, truth-sync pending, ready-for-close, and terminal closed states without conversation-memory claims.
  - Close rejects caller-supplied review, verification, truth requirement, completion, and artifact-identity overrides; only an exact approved evidence package can close.
  - Pending, missing, invalid, unapproved, or mismatched truth-sync evidence routes to its owning upstream phase, while an approved exact match yields `terminal_state: closed` and `next_entry: null` once.
  - Direct explicit truth/docs mutation and approved controller mutation both validate, while incomplete controller context, missing predicate evidence, and out-of-touch-set composition fail closed.
  - A simple stable-fact update leaves `organize-docs` inactive; each declared docs-governance predicate activates only the bounded lower-plane component.
  - Source workflow contracts, provider-neutral contracts, bundled runtime, root-flat projections, stable architecture truth, generated diagrams, and changelog converge on the same ownership and terminal semantics.
  - Focused tests, all required sovereign harness smoke tests, generators, `bash scripts/check.sh`, and `git diff --check` pass with no unrelated tracked drift.
  - Bounded implementation review leaves no accepted current-slice finding unresolved before automatic truth-sync preparation.
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

## Architecture Decision Handoff

- architecture_decision_ref: TSC-001-evidence-bound-pre-close-truth
- chosen_boundary: Preserve existing lifecycle owners; extend their typed handoffs so `implement-change` advances to required truth sync, `sync-truth` owns bounded mutation and approval, conditional `organize-docs` remains lower-plane, and `close-change` performs only evidence-bound terminal judgment.
- reversible_staging:
  - TSC-010 freezes the current defects as executable red evidence without changing behavior.
  - TSC-020 adds plan scope and evidence-identity contracts before any controller or close transition consumes them.
  - TSC-030 switches controller, truth, docs, and close behavior only after the new contracts exist.
  - TSC-040 regenerates and verifies the bounded projection before stable truth is prepared through the lifecycle gate.
- upgrade_trigger: Introduce a separately designed external-action owner only if merge, release, or cleanup execution requires durable state, resumability, and recovery semantics that cannot remain an explicit human action after close judgment.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Plan approval authorizes the complete serial red-green runtime and skill implementation, generated projection, declared verification, bounded implementation review, and preparation of the declared truth-sync update in the current checkout. It does not approve the resulting truth-sync artifact, close judgment, commit, push, plugin install, version bump, external distribution, merge, release, cleanup, or deploy.
- runtime_contingencies:
  - X1: Stop with `needs-design-decision` if the acyclic lifecycle can be preserved only by adding a public owner, introducing a close-to-truth back edge, or making `close-change` mutation-capable.
  - X2: Stop with `needs-plan-change` if required stable truth or conditional docs work cannot be bounded by the approved refs, immutable touch set, and structured predicate evidence.
  - X3: Stop with `manual-decision-required` if existing approved artifacts cannot be handled without trusting caller booleans or silently treating absent truth scope as completion.
  - X4: Stop and preserve evidence if a generator changes content outside the declared generated surfaces or validation fails for a cause that cannot be repaired inside the approved touch set.
- planned_stop_points:
  - TS1: After implementation review and verification pass, prepare the bounded truth-sync artifact with a pending approval state and stop for explicit human truth approval; close remains blocked until that gate is approved.
- task_ordering_rationale: Freeze observable failures first, establish plan and evidence contracts second, switch the controller and terminal transitions third, then regenerate, verify, and review the complete bounded implementation before the controller prepares stable truth.

## Task 1: Freeze the unsafe tail behavior as red executable contracts

- task_id: TSC-010
- depends_on:
  - none
- scope_slice: Extend focused harness smoke tests to reproduce caller-trusted close status, the successful close self-loop, absent truth-scope enforcement, incomplete controller authorization, evidence mismatches, and docs-governance overreach before implementation changes.
- impl_file_refs:
  - none
- test_file_refs:
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-kernel-phase.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
- verification_scope:
  - Record `git status --short` and preserve the approved design, this plan, and every unrelated working-tree path.
  - Add structured shell fixtures for an approved plan, immutable execution result, pending and approved truth artifacts, mismatched refs, direct mutation context, controller mutation context, and each docs-governance predicate.
  - Assert runner JSON fields, exact ref equality, touch-set containment, enum outcomes, and transition results rather than prose sentences or full Markdown snapshots.
  - Run the seven edited smoke tests and require red failures only at the newly specified missing contracts; syntax, fixture, import, path, and unrelated existing assertions must remain green.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - harness-tail-contract-tests
- task_review_depth: focused
- done_when:
  - Each accepted design defect has at least one deterministic failing assertion and every fixture uses repository-local synthetic evidence.
  - The current false-positive close path and close self-loop are demonstrated without performing an external close action.
  - Red output is limited to missing approved behavior and no implementation, source skill, contract, generated, or stable-doc file changes in this task.
- failure_policy: fix_forward
- [ ] Add the focused structured fixtures and assertions.
- [ ] Run the changed tests red and record only the intended failures.

## Task 2: Add stable truth scope, mutation authority, and evidence identity contracts

- task_id: TSC-020
- depends_on:
  - TSC-010
- scope_slice: Make truth-affecting version-2 plans declare bounded stable truth refs and structured docs-governance predicates, distinguish direct from approved-controller mutation authority, and validate exact design, plan, review, verification, and truth identities.
- impl_file_refs:
  - contracts/skills.toml
  - src/skills/workflows/plan-change/SKILL.md
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
- test_file_refs:
  - scripts/check-contracts.py
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
- verification_scope:
  - Extend the skill exposure contract so `sync-truth` and conditional `organize-docs` retain direct explicit-request guards and separately accept a complete approved-plan controller context.
  - Require `Truth Sync Handoff` metadata for truth-affecting version-2 plans: at least one safe stable truth ref, refs contained by the immutable plan touch set, and only supported docs-governance predicate identifiers.
  - Return a typed `truth_sync_scope_required` planning state for missing or invalid legacy scope instead of inferring that truth sync is unnecessary or widening the touch set.
  - Add reusable artifact-DAG comparisons for exact approved design, plan, review, verification, stable truth refs, and allowed touch set; reject key presence without value equality.
  - Keep lifecycle ownership, public skill IDs, activation modes, provider projection, direct invocation behavior, and unrelated plan metadata unchanged.
  - Run the affected contract, plan-runner, and artifact-DAG smoke tests plus `python3 scripts/check-contracts.py` and `git diff --check`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - approved-plan-evidence-contract
- task_review_depth: full
- done_when:
  - A truth-affecting approved plan cannot validate without safe in-scope stable truth refs and supported predicate metadata.
  - Direct explicit mutation and controller mutation remain distinct, machine-checkable authorities; incomplete controller context fails closed.
  - Exact artifact identity checks reject every approved-design, plan, review, verification, stable-ref, or touch-set mismatch in the fixtures.
  - Focused TSC-020 tests pass while transition and close assertions intended for TSC-030 remain the only red evidence.
- failure_policy: fix_forward
- [ ] Implement version-2 stable truth scope and docs predicate validation.
- [ ] Implement dual mutation authority and exact artifact identity contracts.
- [ ] Run the focused contract layer green and preserve the remaining transition reds.

## Task 3: Implement continuous truth routing, conditional docs composition, and terminal close

- task_id: TSC-030
- depends_on:
  - TSC-020
- scope_slice: Bind the execution tail to approved evidence, advance required work into truth sync, invoke docs organization only for supported observed predicates inside the touch set, and replace close recursion with a terminal closed result.
- impl_file_refs:
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/sync-truth/SKILL.md
  - src/skills/workflows/close-change/SKILL.md
  - src/skills/disciplines/organize-docs/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/execute-runner.sh
  - src/runtime/harness/evaluation-gate.sh
  - src/runtime/harness/truth-sync-runner.sh
  - src/runtime/harness/close-runner.sh
  - src/runtime/harness/phase-engine.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-kernel-phase.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
- verification_scope:
  - Make the execution result derive review, verification, truth requirement, plan identity, design identity, allowed truth refs, and current lifecycle state from the validated plan and converged ledger.
  - Route passing truth-affecting execution to controller-authorized `sync-truth` preparation without asking the user to invoke another skill; stop only at the pending truth artifact human gate.
  - Evaluate docs organization from supported structured predicates plus the bounded diff; a Markdown suffix alone is false, and every true result remains within the exact stable truth touch set.
  - Replace close-runner boolean inputs with approved plan, immutable execution result, and optional truth artifact evidence; treat caller hints as non-authoritative and fail mismatches closed.
  - Represent task-complete, truth-sync-pending, ready-for-close, and terminal-closed states explicitly; an approved close returns `terminal_state: closed` and JSON null `next_entry`.
  - Make the phase engine terminate after approved close and prove it cannot resolve `close` back to `close`.
  - Preserve the close mode as judgment metadata only and leave all actual merge, release, cleanup, commit, push, install, deploy, and rollback actions external.
  - Run all six focused smoke tests and `git diff --check` until the complete TSC-010 red set is green.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - harness-tail-state-machine
- task_review_depth: full
- done_when:
  - Required truth sync is a deterministic continuation after passing implementation review and verification, with one explicit pending human truth gate.
  - Simple stable-fact updates skip docs organization; supported governance predicates activate only bounded composition, and invalid context fails closed.
  - No caller-controlled status or mismatched artifact can authorize close.
  - One approved exact evidence package produces one terminal closed result with no successful self-route or repository mutation.
  - Every TSC-010 focused assertion passes.
- failure_policy: fix_forward
- [ ] Implement evidence-derived execution and truth continuation states.
- [ ] Implement conditional bounded docs composition and controller authorization.
- [ ] Implement artifact-bound terminal close and remove close recursion.
- [ ] Run the complete focused red-green suite.

## Task 4: Regenerate, validate, and review the bounded implementation

- task_id: TSC-040
- depends_on:
  - TSC-030
- scope_slice: Refresh every generated runtime and diagram projection owned by the changed sources, run the complete repository validation surface, and pass bounded implementation review before truth-sync preparation.
- impl_file_refs:
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills
  - skills.index.json
- test_file_refs:
  - scripts/generate-skills-index.py
  - scripts/flatten-skills.py
  - scripts/generate-workflow-diagrams.py
  - scripts/check.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-kernel-phase.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
- verification_scope:
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py` in the repository-required order.
  - Require exact parity between every changed source skill or harness runtime file and each generated owner-local root-flat projection; never hand-edit generated `skills/` content.
  - Run the focused contract, phase, plan, artifact, execute, truth-sync, and close tests.
  - Run `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`, `bash src/runtime/harness/smoke-test/test-design-runner.sh`, `bash src/runtime/harness/smoke-test/test-plan-runner.sh`, `bash src/runtime/harness/smoke-test/test-design-plan-skill-control.sh`, `bash src/runtime/harness/smoke-test/test-agent-native-review.sh`, `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`, `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`, `bash src/runtime/harness/smoke-test/test-execute-runner.sh`, and `bash src/runtime/harness/smoke-test/test-review-execute-skill-control.sh`.
  - Run `bash scripts/check.sh` and `git diff --check`, then compare final changed paths against this approved touch set and preserve unrelated files.
  - Route the exact implementation diff, focused runner evidence, generated parity, touch-set proof, and justified direct dependencies through `review-change` with `review-implementation`; repair only accepted in-scope findings and rerun affected checks.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - generated-harness-tail-surface
- task_review_depth: full
- done_when:
  - All generated skill bundles, index metadata, PlantUML sources, and SVG renderings match their authoritative inputs with no hand edits.
  - Focused tests, sovereign harness smoke tests, aggregate validation, changed-path checks, and whitespace validation pass.
  - Bounded implementation review passes or every accepted current-slice finding is repaired and focused verification passes within the declared review budget.
  - Final execution evidence routes automatically to the declared truth-sync handoff, while prose stable truth remains reserved for that gate.
- failure_policy: fix_forward
- [ ] Regenerate root-flat and diagram projections from source.
- [ ] Run focused, sovereign, aggregate, parity, touch-set, and whitespace validation.
- [ ] Complete bounded implementation review and repair only accepted in-scope findings.

## Truth Sync Handoff

- required_entry: sync-truth
- truth_sync_required: true
- approved_design_ref: docs/plans/changes/2026-08-09-truth-sync-before-close-design.md
- approved_plan_ref: docs/plans/changes/2026-08-09-truth-sync-before-close-plan.md
- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/harness-state-machine.md
  - docs/architecture/maintenance-contract.md
  - docs/changelog/design-decisions.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- organize_docs_default: false
- organize_docs_decision: Activate the lower-plane component only for the declared cross-surface lifecycle terminology alignment in these four stable refs; do not scan, relocate, or normalize unrelated Markdown.
- stage_artifact_ref: docs/plans/changes/2026-08-09-truth-sync-before-close-truth-sync.md
- handoff_condition: TSC-040 has passed with converged task ledger, exact implementation diff, passing review and verification evidence, generated parity, and bounded stable truth refs.
- approval_boundary: The controller prepares and validates the minimum stable truth update and pending truth-sync artifact, then stops for explicit human approval. Only an approved exact artifact may enter `close-change`; one user message may approve it and request an explicit close mode when both are visible and unambiguous.

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- actor_role: delegated
- reviewer_profile: balanced execution with deep reasoning
- review_status: passed
- candidate_findings:
  - accepted: Reconcile the plan's generator and design-runner test refs with the approved design's key-for-key implementation surface so execution can construct its immutable allowed touch set.
- review_evidence: The initial delegated bounded review found one high-confidence design-to-plan surface classification defect: three generators were listed as design implementation refs while the plan used them as test refs, and `test-design-runner.sh` was absent from the design test surface. The finding was accepted and repaired by reclassifying the generators and adding the already-required runner under the design test refs without changing behavior or scope. Bash 4 validation then built the 41-ref allowed touch set successfully, and focused delegated verification returned `pass` with no remaining candidate finding or same-slice regression.
- supporting_files:
  - 2026-08-09-truth-sync-before-close-design.md: approved goals, non-goals, lifecycle ownership, authorization boundary, architecture decision, acceptance conditions, and implementation surface.
  - contracts/skills.toml: current direct mutation guards and lifecycle owner exposure that the plan must preserve while adding approved controller authority.
  - src/runtime/harness/plan-runner.sh: current version-2 plan and immutable touch-set validation boundary.
  - src/runtime/harness/artifact-dag.sh: current approved design-plan linkage and allowed-touch-set boundary.
  - src/runtime/harness/execute-runner.sh: current immutable plan projection and typed execution-result boundary.
  - src/runtime/harness/truth-sync-runner.sh: current truth artifact schema and human approval gate.
  - src/runtime/harness/close-runner.sh: current caller-boolean close interface and successful self-route being replaced.
  - src/runtime/harness/phase-engine.sh: current lifecycle sequence and `close -> close` transition being terminated.
  - AGENTS.md: source/generated ownership, serial-first execution, review budgets, truth boundary, mandatory validation, and human-sovereign gates.
- pass_condition: The plan remains one serial characterization-contract-transition-projection milestone faithful to TSC-001, with immutable evidence and touch sets, executable structured oracles, conditional docs governance, terminal close semantics, explicit truth and close approval boundaries, and fix-forward recovery.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed plan and invoked `implement-change` on 2026-08-09, accepting C0, serial execution, the declared truth-sync preparation boundary, and X1-X4 contingencies.
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - The controller records pre-implementation Git status and final changed-path evidence, and every planned mutation is repository-local and bounded by the approved touch set.
  - TSC-010 preserves deterministic failing evidence before behavior changes; TSC-020 and TSC-030 can be repaired independently through their focused runner tests before regeneration.
  - Generated root-flat files, PlantUML, SVG, and index metadata are reproducible from authoritative source and are regenerated rather than hand-repaired.
  - Automatic truth mutation is bounded by exact stable refs and remains recoverable before its separate human approval; close is read-only and terminal judgment performs no external action.
  - No task uses guarded rollback. Any design-boundary, plan-scope, legacy-evidence, or unrelated-generator contradiction stops with the declared typed contingency and preserves current evidence.
