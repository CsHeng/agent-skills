# Exact External File Touch Bootstrap Plan

## Status

- plan_version: 2
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: not_started
- plan_review_status: passed_after_one_bounded_repair
- implementation_review_status: pending
- implementation_verification_status: pending
- execution_stop_reason: none
- recommended_next_phase: implementation
- next_entry: implement-change

## Upstream Design

- design_ref: 2026-08-18-external-file-touch-set-design.md
- design_version: sha256:1022bd7d5852e50d269cb29f679257abc1141edf326b98378536291fda1dab96
- design_approval_status: approved
- architecture_decision_ref: EXACT-EXTERNAL-TOUCH-001

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- bootstrap_unit: E1 repository-only capability implementation; this plan declares no external implementation refs and authorizes no user-home mutation
- impl_file_refs:
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
  - src/runtime/harness/task-ledger.sh
  - src/runtime/harness/execute-runner.sh
  - src/runtime/harness/truth-sync-runner.sh
  - src/runtime/harness/external-touch-evidence.py
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/review-change/SKILL.md
  - src/skills/review-components/review-implementation/SKILL.md
  - src/skills/workflows/sync-truth/SKILL.md
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/review-change
  - skills/review-implementation
  - skills/sync-truth
  - skills/design-change/scripts/harness
  - skills/plan-change/scripts/harness
  - skills/implement-change/scripts/harness
  - skills/review-change/scripts/harness
  - skills/sync-truth/scripts/harness
  - skills/close-change/scripts/harness
- test_file_refs:
  - tests/test_external_touch_evidence.py
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-task-ledger.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/test_runtime_distribution_contracts.py
- verification_commands:
  - `python3 -m unittest tests.test_external_touch_evidence`
  - `python3 -m py_compile src/runtime/harness/external-touch-evidence.py tests/test_external_touch_evidence.py`
  - `bash -n src/runtime/harness/artifact-dag.sh`
  - `bash -n src/runtime/harness/plan-runner.sh`
  - `bash -n src/runtime/harness/task-ledger.sh`
  - `bash -n src/runtime/harness/execute-runner.sh`
  - `bash -n src/runtime/harness/truth-sync-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-task-ledger.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-truth-sync-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-close-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`
  - `python3 -m unittest tests.test_skill_workflow_contracts tests.test_parallel_execution_contracts tests.test_implement_change_via_herdr_contracts tests.test_runtime_distribution_contracts`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `bash scripts/check.sh`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Bootstrap the approved `exact-existing-files-v1` capability entirely inside the repository: add an exact external-ref contract, a standard-library filesystem evidence and compare-and-swap broker, ledger-rooted resumable intent chains, lifecycle evidence validation, portable workflow policy, stable truth, and deterministic generated bundles so a later separately approved E2 plan can safely govern the three user-owned routing files.
- non_goals:
  - Do not modify, create, delete, stage candidate content for, or otherwise mutate any file under `/Users/csheng/.codex`; this E1 plan contains no `external_impl_file_refs` field and invokes no external-write operation against user files.
  - Do not resume, reinterpret, or amend the blocked parent-inherited routing plan in place; do not change model routing, reasoning floors, role files, Codex defaults, or provider-specific user instructions.
  - Do not authorize directory or glob surfaces, relative or environment-expanded external refs, symlinks, hard links, new targets, caller-visible create/delete/rename, caller-selected metadata changes, delegated external writers, parallel external writers, hostile-concurrency guarantees, content backup, or automatic rollback.
  - Do not change lifecycle ownership, human gates, task topology semantics, Herdr wire behavior, provider neutrality, plugin metadata, installation state, commits, pushes, publication, or live agent sessions.
- future_phase:
  - E2 is a new separately reviewed and human-approved routing plan created only after E1 implementation, review, truth sync, and close converge; it may use the new external field for the exact design-approved user files.
  - Caller-visible create/delete/rename, directory authorization, delegated or parallel external writers, hostile-concurrency protection, and a generic versioned filesystem transaction schema remain new-design triggers.
  - Repeated unrelated demand may justify a generic external-touch schema only after the approved evidence threshold in the design is met.
- decision_status: ready_for_review
- oracle_strategy: Use TDD and table-driven unit tests for the Python path, identity, staging, broker, cleanup, and comparison boundary; contract tests for design-plan-task containment and main-only policy; model/state-transition tests for baseline-rooted prepared/applied intent chains, crash-window replay, convergence, and result binding; characterization and golden tests for plans without external refs, repository `allowed-touch-set`, task projections, and Herdr envelopes; and generation/parity checks for stable truth and all bundled harness surfaces.
- acceptance_oracles:
  - A legacy version-2 plan without external refs retains the same repository-only allowed touch set, immutable task projection, runner behavior, truth-sync route, close route, and byte-compatible Herdr envelopes.
  - A future plan can declare only exact design-approved existing regular files through `external_impl_file_refs` plus `external_touch_policy: exact-existing-files-v1`; absolute refs in repository fields, unsafe paths, design/task set mismatches, repository overlap, non-main actors, delegation, concurrency, missing locks, symlinks, and hard links fail with typed evidence before mutation.
  - Python unit tests prove canonical path and metadata capture, single-link enforcement, baseline-rooted immediate-parent comparison, private payload and sibling handling, atomic replacement and parent fsync, content-free JSON, cleanup ownership, one and multiple applied intents, and idempotent replay across pre-apply and post-replace crash windows.
  - Ledger and execute-runner tests prove immutable external task projection, baseline capture before mutation, persisted prepared state before broker apply, applied evidence afterward, contiguous parent-linked chains, convergence against the final after-state, separate `verified_external_changes`, exact `allowed_external_touch_refs`, and typed drift without silently refreshing a baseline.
  - Truth-sync and close tests accept only execution evidence bound to the approved design, plan, ledger, task IDs, and exact external set while leaving stable truth refs repository-relative and never rereading later-mutated external content.
  - Workflow tests require main-controller-only external tasks, broker-only mutation, metadata-only review briefs, controller-owned repair through a new chained intent, no delegated external fields, fix-forward recovery, and no provider identifiers in reusable contracts.
  - Source skills, indexes, diagrams, root-flat projections, and all six harness bundles regenerate deterministically; focused tests, aggregate `scripts/check.sh`, and `git diff --check` pass with no changed path outside this plan.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Approved Architecture Decision

- architecture_decision_ref: EXACT-EXTERNAL-TOUCH-001
- decision_fidelity: Implement only bootstrap unit E1 of the selected two-stage architecture. Preserve repository `allowed-touch-set` semantics and add a separate optional exact-existing-file channel backed by one Python standard-library helper, main-controller-only orchestration, immutable baseline evidence, baseline-rooted immediate-parent intent chains, and metadata-only lifecycle evidence. Do not materialize or execute routing unit E2 in this plan.
- reversible_increments:
  - EAT-010 establishes the isolated helper and its executable filesystem/security oracles without changing harness routing.
  - EAT-020 adds optional external-ref schema and validation while proving absent-field legacy compatibility; removing the optional branch restores the repository-only contract.
  - EAT-030 wires the helper into ledger and execution state behind the optional field; no E1 task itself declares or mutates an external target.
  - EAT-040 adds lifecycle and workflow consumers only after execution evidence is stable.
  - EAT-050 converges source-derived public skills, indexes, runtime bundles, and implementation verification; after bounded implementation review passes, the controller enters `sync-truth` to prepare stable truth and its dependent diagram projections before the human truth gate.
- upgrade_triggers:
  - Return `needs-design-decision` if implementation requires caller-visible target create/delete/rename, caller-selected chmod/chown, directory or glob authorization, symlink or hard-link allowance, delegated or parallel external writers, automatic rollback, or adversarial concurrent-writer guarantees.
  - Return `needs-design-decision` if exact-file safety cannot be implemented with a baseline-rooted broker and metadata-only evidence without storing raw external content in repository artifacts, task ledgers, results, reviews, or logs.
  - Return `needs-plan-change` if E1 requires a repository ref outside the approved design surface or any external file mutation, or if task topology, locks, or oracles must change.
  - Defer a generic versioned external-touch schema until at least three unrelated approved use cases establish demand.
- cleanup_policy: Private controller payloads and broker sibling candidates exist only in test-owned temporary directories during E1 verification. Tests must prove applied and abandoned-run cleanup removes only ledger-bound artifacts whose identity and digest match and refuses ambiguous files.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1. EAT-010 through EAT-050 execute serially under the main controller in the current checkout. No worker, explorer, command job, Herdr pane, Codex-native subagent, isolated worktree, parallel group, or external writer is authorized by this plan.
- topology_invariance: Runtime model policy may affect only the main session's available model and reasoning context; it cannot change task IDs, dependencies, serial order, touch sets, resource locks, or executable oracles.
- worker_binding_policy: not applicable; every implementation task uses `executor_mode: main` and `delegation_policy: forbidden` because the bootstrap changes the shared control-plane contract and generated bundles.
- reviewer_binding_policy: Plan and implementation reviews use one bounded read-only reviewer when available; the reviewer receives only the approved artifact or exact implementation slice and returns candidates for main-agent adjudication.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes EAT-010 through EAT-050 as one continuous repository-local E1 implementation unit, including temporary-directory broker tests, source edits, focused and aggregate verification, deterministic implementation-surface regeneration, and bounded implementation review. After that review passes, the same approved controller context authorizes `sync-truth` to prepare only the declared stable truth and dependent diagram projections, then stop at their pending human gate. Approval does not authorize E2, any `/Users/csheng/.codex` write, live agent/provider action, plugin installation, commit, push, publication, approval of the prepared truth-sync artifact, or close approval.
- runtime_contingencies:
  - X1: If the initial worktree contains unexplained overlapping user changes in a declared E1 source, test, generated, or stable-truth ref, preserve them and return `blocked_source_baseline` before mutation.
  - X2: If same-filesystem atomic replacement, exact identity validation, or ledger-bound cleanup cannot satisfy the approved content-only boundary on supported local filesystems, preserve failing oracle evidence and return `needs-design-decision`; do not weaken path, symlink, hard-link, metadata, or content-redaction assertions.
  - X3: If absent-field plans, repository-only touch sets, task projections, Herdr envelopes, or lifecycle routes cannot remain compatible, stop with the narrow diff and return `needs-design-decision`; do not update characterization oracles to accept a semantic regression.
  - X4: If a focused or aggregate check fails outside causal changed paths, stop and diagnose; repair only accepted in-scope failures and do not widen the touch set, mutate external files, or hide failures with retries or relaxed assertions.
- planned_stop_points:
  - none inside EAT-010 through EAT-050; successful implementation and bounded review continue into controller-authorized truth preparation, then stop at the separate truth-sync approval gate. E2 remains unavailable until E1 truth sync and close complete.
- task_ordering_rationale: Establish the isolated filesystem oracle first, then add the optional artifact contract, bind controller state and execution, update lifecycle consumers, and regenerate source-derived public bundles only after source behavior converges. Perform bounded implementation review before `sync-truth` owns the stable documentation update and dependent diagram regeneration. This orders the most reversible and locally testable work before cross-cutting control-plane surfaces while preserving phase ownership.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Capture and preserve the initial tracked and untracked worktree baseline; mutate only task-declared repository refs and never discard, overwrite, or normalize unrelated user changes.
- external_boundary: E1 authorizes no external target. All helper mutation tests use fresh test-owned temporary files and assert cleanup; any attempted user-home or undeclared path access is a typed failure, not a recovery path.
- state_boundary: Preserve original baselines and prepared/applied intent evidence in failing fixtures; repair state-transition logic against the declared model and never silently recapture a baseline or synthesize an applied checkpoint.
- compatibility_boundary: Fix implementation to retain absent-field repository behavior and Herdr/task-projection characterization; do not weaken, delete, or bulk-update compatibility or security oracles.
- generated_boundary: During EAT-050, edit only source-owned skill/runtime files and regenerate root-flat skills, indexes, and all six runtime bundles. After implementation review, `sync-truth` owns stable docs plus any dependent diagram regeneration. Repair source or generator causes in the owning phase; never hand-edit generated output.
- external_actions_boundary: Commit, push, install, live agent execution, provider action, user-config mutation, E2 planning, truth-sync approval, and close are not recovery actions under this plan.
- guarded_rollback: none

## Task 1: Build the exact-file evidence and mutation helper from failing oracles

- task_id: EAT-010
- depends_on:
  - none
- scope_slice: Add the standard-library Python helper with deterministic `baseline`, `stage`, `prepare`, `apply`, `compare`, and ledger-bound cleanup operations. It must validate canonical exact existing regular files, reject repository overlap, symlinks and hard links, capture content-free identity metadata, stage controller payloads privately, create only broker-named sibling candidates, compare the opened target to the intent's immediate parent, preserve approved metadata, fsync candidate and parent, atomically replace the exact target, emit stable typed JSON, and support idempotent replay. E1 exercises it only against temporary fixtures.
- impl_file_refs:
  - src/runtime/harness/external-touch-evidence.py
- test_file_refs:
  - tests/test_external_touch_evidence.py
- verification_scope:
  - Cover valid regular files plus missing targets, directories, control/glob characters, non-canonical paths, final and ancestor symlinks, hard links, repository overlap, metadata access failure, content drift, identity drift, and deterministic ref ordering.
  - Cover private payload permissions, broker-generated sibling naming, `O_CREAT|O_EXCL` behavior, candidate hash verification, immediate-parent recheck, metadata preservation, atomic replacement, fsync calls, successful cleanup, crash-left candidate reuse or refusal, and ambiguous-artifact refusal.
  - Cover first and later parent transitions, candidate-equals-parent rejection, pre-apply replay, post-replace/pre-marker replay, conflicting third state, secret-free stdout/stderr/JSON, stable exit classes, and no shell command construction.
  - Run the focused unittest module, `py_compile`, and `git diff --check`.
- failing_oracle_first: Create `tests/test_external_touch_evidence.py` first and prove the path, identity, broker, chain, replay, cleanup, and redaction cases fail because the helper does not yet exist; implement only until that focused suite passes.
- implementation_archetype: deterministic exact-file compare-and-swap mutation and evidence helper
- implementation_language: Python 3 standard library
- language_rationale: The approved design assigns canonical path, file-descriptor identity, metadata, hashing, atomic replacement, fsync, typed JSON, and cleanup semantics to Python; introducing dependencies or reimplementing these rules in Bash would expand portability and quoting risk.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - external-touch-helper-contract
- task_review_depth: full
- done_when:
  - Every helper operation and typed error is covered by deterministic temporary-filesystem tests and emits no raw content.
  - Immediate-parent compare-and-swap, hard-link rejection, broker-only sibling mechanics, cleanup ownership, and crash replay satisfy the approved design.
  - No repository file other than the declared helper and test changes in this task.
- failure_policy: fix_forward

## Task 2: Add the optional external-ref artifact and plan contract

- task_id: EAT-020
- depends_on:
  - EAT-010
- scope_slice: Extend the artifact-DAG and plan validator with the optional `external_impl_file_refs` channel and required `external_touch_policy: exact-existing-files-v1` when non-empty. Preserve repository `impl_file_refs`, `test_file_refs`, and `allowed-touch-set` unchanged; enforce exact design-to-plan and plan-to-task set containment, no repository/external overlap, main-only serial actor metadata, non-empty locks, and absent-field normalization to an empty set. Expose validation needed for a future E2 plan without declaring an external ref in E1 itself.
- impl_file_refs:
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Add valid future-plan fixtures with exact design/plan/task external containment and invalid fixtures for absolute refs in repository fields, unsafe external syntax, missing or wrong policy, design mismatch, task widening, duplicate or overlapping surfaces, subagent or command-job actors, delegation, parallel policy, isolated-worktree execution, and missing locks.
  - Assert field absence preserves legacy validation and byte-identical sorted repository `allowed-touch-set` output; an empty external list behaves as absent.
  - Assert E1 itself validates with no external field and no operation unavailable at its preflight.
  - Run Bash syntax checks, artifact-DAG and plan-runner smoke tests, the parallel-contract module, and `git diff --check`.
- failing_oracle_first: Add dual-channel contract fixtures and the full invalid-policy matrix before parser changes; valid fixtures must initially fail for unsupported metadata while every existing repository-only fixture continues to pass.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - artifact-dag-plan-schema
- task_review_depth: deep
- done_when:
  - The optional external channel is exact, fail-closed, and actor-constrained without changing repository surfaces.
  - The current E1 plan and all legacy fixtures remain valid without an external field.
  - Future E2 plan/task widening or unsafe actor metadata fails before ledger creation.
- failure_policy: fix_forward

## Task 3: Integrate baseline-rooted intent chains with controller execution

- task_id: EAT-030
- depends_on:
  - EAT-020
- scope_slice: Extend immutable task projection, dynamic ledger state, execute-runner operations, controller convergence, and execution-result construction for exact external refs. Capture the baseline before mutation; persist one prepared intent before each broker apply and its after-evidence immediately afterward; link later repair intents to the preceding after-state while retaining the immutable root; implement idempotent replay, separate verified external evidence, and `allowed-external-touch-set`; exclude external fields from delegated envelopes and preserve legacy and Herdr behavior.
- impl_file_refs:
  - src/runtime/harness/task-ledger.sh
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-task-ledger.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/test_implement_change_via_herdr_contracts.py
- verification_scope:
  - Exercise immutable external task projection, baseline capture binding to design/plan/run/task identity, exact sorted refs, initial and repeat capture, and rejection of missing, mismatched, or silently refreshed state.
  - Exercise one- and multi-intent chains with contiguous sequences, immediate-parent linkage, at most one prepared intent, applied evidence, empty-chain unchanged state, final state returning to baseline, fork/duplicate/missing sequence rejection, and current-state convergence.
  - Exercise interruption before sibling creation, after sibling creation, after replacement but before marker, and after marker but before cleanup; prove exact parent/candidate replay and typed drift for every third state.
  - Assert execution results carry `allowed_external_touch_refs` and metadata-only `verified_external_changes` separately from repository `verified_changed_paths`, and no delegated or Herdr envelope gains external paths or raw content.
  - Run Bash syntax checks, task-ledger, execute-runner, and recovery-routing smoke tests, the unchanged-behavior Herdr contract suite, the helper tests, and `git diff --check`.
- failing_oracle_first: Add task-ledger state-model and execute-runner fixtures for baseline ordering, prepared-before-apply, applied checkpoints, chain replay, convergence, typed drift, result binding, and absent-field compatibility before adding controller operations.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - task-ledger-external-state
  - execute-runner-external-broker
- task_review_depth: full
- done_when:
  - The controller can create and converge deterministic external evidence only through the broker and ordered ledger state.
  - Every crash window is replayable or returns typed drift without refreshing the root baseline or synthesizing evidence.
  - Repository-only execution, task topology, and Herdr wire behavior remain compatible.
- failure_policy: fix_forward

## Task 4: Carry external evidence through lifecycle and review contracts

- task_id: EAT-040
- depends_on:
  - EAT-030
- scope_slice: Update truth-sync execution-evidence validation and the plan, implementation, review, implementation-review, and truth-sync skill contracts for the optional external channel. Require exact-file main-only tasks, broker-only writes, metadata-only bounded review briefs, controller-owned repair through the next parent-linked intent, exact result binding, repository-only stable truth refs, and no reread of current external content during truth sync or close. Prove close behavior through shared artifact/result validation without adding a separate external writer or lifecycle authority.
- impl_file_refs:
  - src/runtime/harness/truth-sync-runner.sh
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/review-change/SKILL.md
  - src/skills/review-components/review-implementation/SKILL.md
  - src/skills/workflows/sync-truth/SKILL.md
- test_file_refs:
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - tests/test_skill_workflow_contracts.py
- verification_scope:
  - Truth-sync fixtures accept only exact external-set and metadata-evidence binding to approved design, plan, execution result, ledger, and task IDs; malformed, widened, content-bearing, or mismatched evidence fails without rereading a live target.
  - Close fixtures prove valid historical evidence remains valid after a simulated later external edit, while malformed or mismatched embedded evidence fails through shared validation.
  - Skill contract tests require the plan field semantics, E1/E2 bootstrap boundary, main-controller broker flow, chained repair, redacted review surface, truth-sync repository boundary, typed stops, and unchanged lifecycle ownership.
  - Provider identifiers, concrete model routes, raw external content, generic editor instructions, delegated external fields, and automatic rollback remain absent from reusable surfaces.
  - Run Bash syntax checks, truth-sync and close smoke tests, workflow contract tests, and `git diff --check`.
- failing_oracle_first: Add lifecycle evidence and workflow-contract assertions first; they must fail until truth-sync validation and all source skill consumers agree on the external channel and broker ownership.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - lifecycle-external-evidence-contract
  - workflow-skill-contracts
- task_review_depth: deep
- done_when:
  - Plan, implementation, review, truth-sync, and close boundaries consume one consistent metadata-only external evidence contract.
  - Reviewers remain read-only and main-controller adjudication/repair remains distinct.
  - Stable truth scope remains repository-relative and historical evidence does not freeze user files forever.
- failure_policy: fix_forward

## Task 5: Converge generated implementation surfaces and verification evidence

- task_id: EAT-050
- depends_on:
  - EAT-040
- scope_slice: Regenerate the skill index, root-flat public skills, and all six complete harness bundles from the converged EAT-010 through EAT-040 source, then run the complete focused and aggregate implementation verification matrix. Do not edit stable docs or dependent diagram projections in this task; after bounded implementation review passes, hand those declared refs to controller-authorized `sync-truth`.
- impl_file_refs:
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/review-change
  - skills/review-implementation
  - skills/sync-truth
  - skills/design-change/scripts/harness
  - skills/plan-change/scripts/harness
  - skills/implement-change/scripts/harness
  - skills/review-change/scripts/harness
  - skills/sync-truth/scripts/harness
  - skills/close-change/scripts/harness
- test_file_refs:
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - tests/test_runtime_distribution_contracts.py
- verification_scope:
  - Regenerate source maps, index, root-flat skills, and every runner-owner bundle; prove the new helper and changed runtime files are distributed identically and no generated file was hand-edited.
  - Run every implementation-phase top-level verification command, `bash scripts/check.sh`, root-flat generation check mode, and `git diff --check`; inspect the final implementation changed-path set against EAT-010 through EAT-050.
  - Confirm `docs/architecture/workflow-orchestration.md`, `README.md`, and their diagram projections remain at the captured pre-implementation baseline until implementation review passes and `sync-truth` begins.
  - Confirm no `/Users/csheng/.codex` hash or metadata changed and no live Codex, Herdr, plugin, commit, push, or publication action occurred.
- failing_oracle_first: Before regeneration, generation/parity checks must report stale root-flat skills, indexes, or runtime bundles caused by the completed source changes; regenerate once from source and require check mode plus a second diff inspection to converge without residual drift.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-skill-surface
- task_review_depth: full
- done_when:
  - Source-derived public skills, indexes, and all runner bundles express the same approved E1 capability and E2 gate.
  - Every focused, aggregate, distribution, parity, and whitespace implementation oracle passes from the integrated source.
  - The controller records implementation evidence for bounded review while stable truth refs remain unchanged; after review passes it routes them to `sync-truth` without external configuration mutation, install, commit, or push.
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
- handoff_scope: Only after EAT-010 through EAT-050 converge and bounded implementation review passes, use the approved-controller `sync-truth` context to prepare the minimum stable repository truth for the exact-existing-file optional channel, two-unit E1/E2 bootstrap, main-controller compare-and-swap broker, baseline-rooted parent-linked intent chain, metadata-only lifecycle evidence, legacy compatibility, recovery policy, and upgrade triggers. Refresh dependent PlantUML and SVG projections in that phase, rerun the aggregate gate, create a pending truth-sync artifact, and stop for explicit human approval. User-home files and the concrete routing matrix remain outside repository stable truth; runtime bundles are implementation projections already converged in EAT-050.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_one_bounded_repair
- candidate_findings: The initial bounded plan review returned one blocker: EAT-050 assigned stable-truth mutation to an implementation task before bounded implementation review and the `sync-truth` owner. Main adjudication accepted the phase-ownership defect, while correcting the reviewer's narrower claim that human truth approval must precede candidate truth preparation; the approved-controller context authorizes preparation after implementation review and the human gate approves the resulting artifact before close.
- review_evidence: The repair limits EAT-050 to source-derived generated implementation surfaces and implementation verification, requires stable refs to remain unchanged through implementation review, and moves stable docs plus dependent diagram regeneration and aggregate revalidation into the explicit post-review Truth Sync Handoff. The focused reviewer returned `PASS: focused truth-ownership repair is complete with no repair-induced regression`.
- review_budget: One initial bounded plan review and one focused verification review were consumed. No further plan-review batch is authorized without a new causal plan scope.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed plan and requested `implement-change` on 2026-08-18.
- next_entry: implement-change
