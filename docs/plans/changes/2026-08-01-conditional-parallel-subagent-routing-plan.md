# Conditional Parallel Subagent Routing Implementation Plan

## Upstream Design

- design_ref: 2026-08-01-conditional-parallel-subagent-routing-design.md
- design_version: 1

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: true
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/implement-change/references/repair-loop.md
  - src/skills/review-components/review-plan/SKILL.md
  - src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md
  - src/skills/_internal/_harness-libs/contracts.sh
  - src/skills/_internal/_harness-libs/artifact-dag.sh
  - src/skills/_internal/_harness-libs/plan-runner.sh
  - src/skills/_internal/_harness-libs/task-ledger.sh
  - src/skills/_internal/_harness-libs/execute-runner.sh
  - commands/plan-change.md
  - commands/implement-change.md
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
  - skills/implement-change/references/workflow.toml
  - skills/implement-change/references/repair-loop.md
  - skills/review-plan/SKILL.md
  - skills/executable-oracle-architecture-selector/SKILL.md
  - skills/_harness-libs/contracts.sh
  - skills/_harness-libs/artifact-dag.sh
  - skills/_harness-libs/plan-runner.sh
  - skills/_harness-libs/task-ledger.sh
  - skills/_harness-libs/execute-runner.sh
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-plan-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-task-ledger.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-execute-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-contracts.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-phase.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-recovery-routing.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-design-plan-command-control.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-sovereign-command-surface.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-artifact-dag.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-review-execute-command-control.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Capture a pre-mutation status and content-hash baseline for every pre-existing dirty path, including the unrelated `organize-docs` and `testing-strategy` work, and prove it is unchanged after convergence.
  - Record pre-change red evidence that the current plan parser accepts unknown scheduling metadata, the ledger exposes only one ready task, and the execution runner cannot materialize task-level runtime bindings.
  - Run the task-scoped Shell smoke tests and Python contract tests after each causal slice.
  - Run `bash -n` and ShellCheck on every changed Shell source and smoke test.
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py` only at controller-owned convergence.
  - Prove exact parity between every changed source skill or harness path and its generated root-flat counterpart.
  - Run the sovereign command-surface, design, plan, review, artifact-DAG, recovery, ledger, execution, and aggregate checks listed by `AGENTS.md`.
  - Run a bounded context-clean forward test for one approved two-task batch under both `semantic-routing` and `inherit-main` without changing the batch topology.
  - Route the exact implementation diff and evidence through bounded agent-native implementation review and leave no accepted finding unresolved.
  - Run `git diff --check` and compare the final changed-path set with the design and plan touch sets.

## Work Package Readiness

- milestone_objective: Make `plan-change` emit a portable, versioned conditional-parallel task DAG and make `implement-change` deterministically bind that unchanged DAG to main-agent or subagent actors, semantic execution profiles, available runtime capacity, isolated worktrees, convergence, and typed fallback or stop behavior.
- non_goals:
  - Modify `~/.codex/config.toml`, install a plugin, create user-global custom agents, or require a particular runtime concurrency ceiling.
  - Put GPT, Claude, Gemini, or any other vendor model identifier into reusable skills, runner schemas, generated surfaces, or stable architecture truth.
  - Add an external scheduler, a second lifecycle controller, recursive delegation, worker-owned integration, or worker-owned repair decisions.
  - Make all ready tasks parallel, allow concurrent writes in one checkout, or infer parallel approval from task count alone.
  - Change review candidate adjudication, truth-sync approval, close approval, commit, push, release, or installation policy.
  - Rewrite legacy plans merely to adopt the new contract.
- future_phase:
  - Use `sync-truth` after verified implementation to update `README.md`, `AGENTS.md`, `docs/architecture/workflow-orchestration.md`, `docs/architecture/maintenance-contract.md`, and `docs/changelog/design-decisions.md` from the final evidence, then stop for the required truth-sync approval.
  - Change user-global subagent defaults or concurrency only through a separately explicit user-authorized configuration action and verify them in a new Codex thread.
  - Consider wider batches, persistent worker pools, or provider-specific runtime adapters only after bounded execution evidence shows that two-way conflict-free batches are insufficient.
- decision_status: ready_for_review
- oracle_strategy: Use contract-model and state-transition tests for schema, ready-set, binding, fallback, isolation, and convergence behavior; use Shell smoke tests for the installed harness boundary; and use one context-clean agent forward test as substitute runtime evidence without asserting exact prose or concrete model names.
- acceptance_oracles:
  - A version-2 plan with an unknown policy, profile, group, dependency, isolation, or resource-lock state is rejected, while a legacy plan follows the documented compatibility path.
  - A deterministic ready-set function returns all dependency-satisfied tasks in stable plan order, and a batch selector admits only tasks in the approved named group with disjoint writes and resource locks.
  - The runtime-binding record preserves task IDs, dependencies, parallel groups, isolation, locks, and oracles across `semantic-routing`, `inherit-main`, and `runtime-default` model policies.
  - `parallel_policy: allowed` can record a conservative serial fallback, `parallel_policy: required` returns a typed capacity stop, and `delegation_policy: forbidden` cannot be relaxed by runtime preference.
  - Parallel write workers receive isolated worktrees derived from one dependency-frozen snapshot; only the main controller converges their bounded diffs and advances dependent tasks.
  - Source and generated surfaces are identical, all declared smoke and aggregate checks pass, and no reusable contract contains a concrete vendor model identifier.
  - A bounded implementation review passes or every accepted in-scope finding is repaired and reverified within two review batches.
  - Every pre-existing unrelated dirty path retains its baseline content and tracked or untracked status; no global config, commit, push, install, or remote state changes.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval of this plan authorizes CPR-010 through CPR-050 as one implementation unit, including the named P1 batch, two detached isolated worker worktrees, controller-owned patch convergence, bounded worker and reviewer subagents, and in-scope fix-forward repair; it does not authorize commits, pushes, plugin installation, user-global configuration writes, stable-truth approval, or close actions.
- runtime_contingencies:
  - X1: Stop and diagnose if any pre-existing unrelated dirty path changes content or status, or if a generator changes a path outside the approved touch set.
  - X2: Return `needs-plan-change` through dependency freeze if observed dependencies, write sets, resource locks, or convergence evidence invalidate P1's conflict-free claim.
  - X3: Record a serial fallback and continue when P1 remains `parallel_policy: allowed` but runtime capacity, subagent availability, or safe isolation is lower than planned; return a typed capacity stop only for future `parallel_policy: required` work.
  - X4: Return `needs-design-decision` if implementation would require concrete vendor model identifiers in reusable contracts, a provider-specific scheduler, or a second repair or integration owner.
  - X5: Stop and diagnose if aggregate or context-clean verification fails and the failure cannot be causally repaired inside the approved implementation and test surfaces.
- planned_stop_points:
  - none inside CPR-010 through CPR-050; successful implementation hands verified evidence to the separately approval-gated `sync-truth` phase.
- task_ordering_rationale: Freeze and test the portable plan schema first; execute the disjoint deterministic-runtime and workflow-contract slices as one conditional isolated batch; converge generated surfaces once; then run context-clean verification and controller-owned review before truth sync.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- topology_invariance: A model-policy override changes only actor model and reasoning binding; it cannot change task IDs, dependencies, parallel groups, batch limits, isolation, resource locks, touch sets, or acceptance oracles.
- semantic_profiles:
  - deep: use a runtime-available high-capability equivalent for architecture-sensitive or scheduler-state work.
  - balanced: use a runtime-available general implementation equivalent for bounded code and integration work.
  - fast: use a runtime-available efficient equivalent for mechanical contract, command, and documentation work.
- reasoning_profiles:
  - deep: reserve extended reasoning for cross-file invariants, conflicts, recovery, and adjudication.
  - standard: use normal implementation reasoning for bounded, explicit tasks.
  - light: use concise reasoning only for mechanical work with strong executable oracles.
- effective_concurrency: The controller uses the minimum of runtime capacity, user configuration, ready-task count, batch maximum, safe isolation width, disjoint write sets, and disjoint resource locks.
- user_runtime_boundary: External user preferences may provide a session ceiling and default subagent fallback, but this plan neither persists nor validates user-global configuration and never copies a concrete model identifier into repository truth.

## Parallel Batches

- batch_id: P1
- tasks:
  - CPR-020
  - CPR-030
- dependency_freeze: Both tasks depend only on completed CPR-010, have no dependency on each other, and receive the same content-addressed CPR-010 dependency snapshot.
- parallel_policy: allowed
- delegation_policy: preferred
- max_parallelism: 2
- isolation: isolated-worktree
- write_set_rule: CPR-020 owns deterministic scheduler and ledger scripts plus their smoke tests; CPR-030 owns workflow skills, references, command wrappers, and their contract tests. Their writable paths do not overlap.
- resource_lock_rule: `runtime-scheduler` and `workflow-contract` are distinct locks; neither worker may run generators, mutate generated root-flat files, edit stable truth, integrate the peer diff, or change user-global state.
- convergence_task: CPR-040
- fallback: If two safe worker slots or isolated worktrees are unavailable, execute CPR-020 then CPR-030 serially with the same task briefs, actors, touch sets, and oracles, and record why the approved parallel opportunity was not used.

## Task 1: Version and validate the portable plan contract

- task_id: CPR-010
- depends_on:
  - none
- scope_slice: Define the version-2 plan metadata, portable enums, validation rules, reviewer expectations, and oracle-selection guidance that make task topology, delegation eligibility, semantic profiles, isolation, and resource locks explicit while retaining a deliberate legacy-plan compatibility path.
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/review-components/review-plan/SKILL.md
  - src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md
  - src/skills/_internal/_harness-libs/contracts.sh
  - src/skills/_internal/_harness-libs/plan-runner.sh
  - commands/plan-change.md
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-plan-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-contracts.sh
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Before mutation, capture `git status --short` and content hashes for every pre-existing dirty path, and confirm current source/generated parity for those unrelated paths.
  - Add a red fixture proving current validation accepts at least one invalid version-2 enum or unsafe batch shape, then make it fail closed under the new contract.
  - Test all `parallel_policy`, `delegation_policy`, `execution_profile`, `reasoning_profile`, isolation, group, dependency, and resource-lock enums and cross-field rules.
  - Test that version-2 metadata is mandatory and strict while legacy plans take only the documented compatibility path.
  - Run `bash -n`, ShellCheck, `test-plan-runner.sh`, `test-kernel-contracts.sh`, and the focused Python contract test.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - plan-contract-schema
- task_review_depth: boundary
- done_when:
  - The portable enum and cross-field contract is defined once and reused by validation instead of being duplicated as prose-only advice.
  - New plans cannot omit or invent scheduling metadata, declare unsafe parallel membership, or use concrete vendor model identifiers as execution profiles.
  - Legacy plans remain readable and executable through an explicit compatibility mode with no silent reinterpretation as version 2.
  - Plan and plan-review skills assign logical DAG and recommendation ownership to `plan-change`, not to workers or runtime adapters.
  - The task-scoped red-green tests and Shell checks pass without changing any unrelated dirty path.
- failure_policy: fix_forward

## Task 2: Implement deterministic ready-batch and runtime binding mechanics

- task_id: CPR-020
- depends_on:
  - CPR-010
- scope_slice: Extend the artifact DAG, task ledger, and execution runner to return stable ready sets, select bounded conflict-free named batches, materialize actor and model-policy bindings, enforce isolation and resource locks, converge only through the controller, and emit typed fallback or conflict evidence.
- impl_file_refs:
  - src/skills/_internal/_harness-libs/artifact-dag.sh
  - src/skills/_internal/_harness-libs/task-ledger.sh
  - src/skills/_internal/_harness-libs/execute-runner.sh
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-task-ledger.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-execute-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-phase.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-recovery-routing.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-artifact-dag.sh
- verification_scope:
  - Preserve red evidence that the current ledger returns only the first ready task and the current runner recognizes only a plan-level parallel marker.
  - Test stable ready-set order, dependency completion, named-group membership, batch limits, write-set overlap, resource-lock overlap, read-only shared-checkout eligibility, and isolated-write requirements.
  - Test runtime binding for `semantic-routing`, `inherit-main`, and `runtime-default` while asserting byte-for-byte topology invariance in the approved task metadata.
  - Test `allowed` serial fallback, `required` capacity stop, forbidden delegation, `parallel-conflict` recovery routing, and controller-only convergence.
  - Run `bash -n`, ShellCheck, and all five task-scoped smoke tests inside the isolated worker worktree.
- executor_mode: subagent
- parallel_group: P1
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - runtime-scheduler
- task_review_depth: full
- done_when:
  - The ledger exposes all ready tasks deterministically and the batch selector returns only a safe subset authorized by P1.
  - Runtime binding records actor kind, model policy, semantic execution profile, reasoning profile, effective width, and fallback evidence without storing a concrete model identifier in the portable plan contract.
  - `inherit-main` changes binding only; it cannot collapse the two planned tasks into one, add dependencies, or relax isolation and locks.
  - Only the controller advances dependency state after validating actual changed paths, task oracles, and convergence evidence.
  - All task-scoped red-green tests pass and the worker writes only its declared paths.
- failure_policy: fix_forward

## Task 3: Evolve workflow guidance and command contracts

- task_id: CPR-030
- depends_on:
  - CPR-010
- scope_slice: Update `implement-change`, its workflow and repair references, and thin command surfaces so semantic routing and preferred subagent execution are the default for eligible tasks, `inherit-main` remains an execution-time binding override, and the main controller retains integration, review adjudication, repair, and continuation ownership.
- impl_file_refs:
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/implement-change/references/repair-loop.md
  - commands/implement-change.md
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-design-plan-command-control.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-sovereign-command-surface.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-review-execute-command-control.sh
  - tests/test_skill_workflow_contracts.py
- verification_scope:
  - Add contract-level red evidence for the missing planning-versus-runtime ownership split and the missing `inherit-main` topology-invariance rule.
  - Verify that preferred delegation remains conditional on readiness, policy, authority, isolation, locks, and runtime capacity rather than becoming unattended blanket parallelism.
  - Verify that workers cannot delegate recursively, widen touch sets, integrate peer work, adjudicate reviewer candidates, repair findings, or decide continuation.
  - Verify that custom role guidance leaves model selection unpinned so runtime semantic routing and `inherit-main` remain effective.
  - Run the four task-scoped smoke tests and the focused Python workflow-contract tests inside the isolated worker worktree.
- executor_mode: subagent
- parallel_group: P1
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - workflow-contract
- task_review_depth: boundary
- done_when:
  - `plan-change` remains the owner of logical topology and recommendations, while `implement-change` owns only runtime binding and physical execution.
  - Eligible tasks default to the approved delegation and semantic-routing advice, and an explicit `inherit-main` override preserves the same serial or parallel task topology.
  - Runtime capacity reduction is conservative and evidence-bearing; it never creates undeclared parallelism or authority.
  - Review, adjudication, repair, convergence, truth-sync routing, and close routing remain controller-owned and agent-native.
  - No reusable workflow or command contract pins a vendor model identifier, and all task-scoped tests pass.
- failure_policy: fix_forward

## Task 4: Converge generated surfaces and run integration oracles

- task_id: CPR-040
- depends_on:
  - CPR-020
  - CPR-030
- scope_slice: Have the main controller verify both worker diffs against their task briefs, apply only their bounded changes in deterministic order, regenerate the root-flat public surface once, and run the complete integration and repository checks.
- impl_file_refs:
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
  - skills/implement-change/references/workflow.toml
  - skills/implement-change/references/repair-loop.md
  - skills/review-plan/SKILL.md
  - skills/executable-oracle-architecture-selector/SKILL.md
  - skills/_harness-libs/contracts.sh
  - skills/_harness-libs/artifact-dag.sh
  - skills/_harness-libs/plan-runner.sh
  - skills/_harness-libs/task-ledger.sh
  - skills/_harness-libs/execute-runner.sh
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-plan-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-task-ledger.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-execute-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-contracts.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-phase.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-recovery-routing.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-design-plan-command-control.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-sovereign-command-surface.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-artifact-dag.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-review-execute-command-control.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Compare each worker's actual changed paths with its declared task refs and reject any peer, generated, stable-truth, global-config, or unrelated write before convergence.
  - Apply the CPR-020 and CPR-030 result patches over the common CPR-010 snapshot in stable task order and rerun their narrow tests after integration.
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py` exactly once from the converged controller checkout.
  - Require exact source/generated parity for every changed skill and `_harness-libs` path.
  - Run every sovereign harness smoke test required by `AGENTS.md`, the focused ledger and contract tests, `bash scripts/check.sh`, and `git diff --check`.
  - Compare final status and hashes against the pre-mutation unrelated-work baseline and compare all new changed paths with the approved touch set.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-root-flat
  - workflow-diagrams
- task_review_depth: full
- done_when:
  - Both worker slices converge without overlap, missing prerequisites, hidden peer dependencies, or worker-owned integration.
  - All generated root-flat files exactly match their source counterparts and no hand edit exists only in `skills/`.
  - All declared smoke, contract, aggregate, Shell, parity, diagram, and whitespace checks pass.
  - No generator or convergence step changes an unrelated path, including the pre-existing dirty `organize-docs` and `testing-strategy` work.
  - The converged implementation contains no concrete vendor model identifier in reusable contracts.
- failure_policy: stop_and_diagnose

## Task 5: Forward-test, review, and prepare truth-sync evidence

- task_id: CPR-050
- depends_on:
  - CPR-040
- scope_slice: Exercise the converged harness in a bounded context-clean scenario, review the exact implementation diff and evidence, repair only accepted same-slice findings, rerun affected verification, and prepare the verified handoff for `sync-truth`.
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/implement-change/references/repair-loop.md
  - src/skills/review-components/review-plan/SKILL.md
  - src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md
  - src/skills/_internal/_harness-libs/contracts.sh
  - src/skills/_internal/_harness-libs/artifact-dag.sh
  - src/skills/_internal/_harness-libs/plan-runner.sh
  - src/skills/_internal/_harness-libs/task-ledger.sh
  - src/skills/_internal/_harness-libs/execute-runner.sh
  - commands/plan-change.md
  - commands/implement-change.md
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
  - skills/implement-change/references/workflow.toml
  - skills/implement-change/references/repair-loop.md
  - skills/review-plan/SKILL.md
  - skills/executable-oracle-architecture-selector/SKILL.md
  - skills/_harness-libs/contracts.sh
  - skills/_harness-libs/artifact-dag.sh
  - skills/_harness-libs/plan-runner.sh
  - skills/_harness-libs/task-ledger.sh
  - skills/_harness-libs/execute-runner.sh
- test_file_refs:
  - src/skills/_internal/_harness-libs/smoke-test/test-plan-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-task-ledger.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-execute-runner.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-contracts.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-kernel-phase.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-recovery-routing.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-design-plan-command-control.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-sovereign-command-surface.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-artifact-dag.sh
  - src/skills/_internal/_harness-libs/smoke-test/test-review-execute-command-control.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Start a context-clean bounded agent with only the approved design, plan, generated skills, task fixture, and runtime capabilities needed for the scenario; do not grant repository-wide discovery or mutation.
  - Demonstrate one two-task conflict-free batch under `semantic-routing`, repeat runtime binding with `inherit-main`, and prove identical task topology, isolated writes, controller convergence, and review ownership.
  - Demonstrate an `allowed` serial fallback, a `required` typed capacity stop, and a forbidden-delegation rejection using deterministic fixtures rather than relying on provider labels.
  - Route the exact diff, task oracles, changed-path proof, and forward-test evidence through `review-change` with `review-implementation`; adjudicate all candidates and allow at most two review batches.
  - Repair only accepted findings with qualifying change causality and approved-contract violation, then rerun affected tests plus final aggregate, parity, status, and whitespace checks.
  - Produce a truth-sync evidence summary that names only the stable truth refs approved by the design and leaves their mutation and approval to `sync-truth`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - implementation-review-gate
- task_review_depth: full
- done_when:
  - Context-clean evidence proves conditional parallel execution and model-policy topology invariance without a concrete vendor model assertion.
  - Review verdict is `pass`, or all accepted in-scope findings are repaired and focused verification passes within the declared review budget.
  - Final source/generated parity, aggregate checks, changed-path proof, and unrelated-work preservation checks pass after any repair.
  - The implementation result routes to `sync-truth` with verified evidence and no stable-truth file has been changed prematurely.
  - No commit, push, plugin installation, user-global configuration write, or close action occurs.
- failure_policy: fix_forward

## Truth Sync Handoff

- required_entry: sync-truth
- truth_sync_required: true
- stable_truth_refs:
  - README.md
  - AGENTS.md
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/maintenance-contract.md
  - docs/changelog/design-decisions.md
- handoff_condition: CPR-050 has passed with final implementation review, verification, changed-path evidence, and source/generated parity.
- approval_boundary: `sync-truth` creates and validates its own pending artifact from the observed implementation evidence and stops for explicit human truth-sync approval before `close-change`.

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- actor_role: delegated
- reviewer_profile: balanced execution with deep reasoning
- review_status: passed
- candidate_findings: none
- review_evidence: A bounded read-only reviewer confirmed design-to-plan ownership and topology fidelity; CPR-010 freezes the portable strict and legacy contract before P1; CPR-020 and CPR-030 have one common completed dependency, no interdependency, disjoint writes and locks, and isolated worktrees; CPR-040 alone converges and generates; semantic routing and `inherit-main` preserve topology; fallback, typed stops, dirty-work preservation, bounded review, repair, and truth-sync ownership are explicit.
- supporting_files:
  - 2026-08-01-conditional-parallel-subagent-routing-design.md: approved ownership, portable profile, safety, compatibility, fallback, and implementation-surface contract.
  - src/skills/workflows/plan-change/SKILL.md: current planning, readiness, continuity, and parallel-approval contract.
  - src/skills/workflows/implement-change/SKILL.md: current serial-first controller, review, repair, and continuation contract.
  - src/skills/_internal/_harness-libs/plan-runner.sh: current execution-grade plan validation boundary.
  - src/skills/_internal/_harness-libs/task-ledger.sh: current single-ready-task ledger behavior.
  - src/skills/_internal/_harness-libs/execute-runner.sh: current plan-level parallel marker and execution boundary.
  - AGENTS.md: source/generated truth, mandatory validation, review ownership, lifecycle approvals, and unrelated-work preservation rules.
- pass_condition: The plan is an executable, dependency-frozen, vendor-neutral, conditionally parallel milestone whose P1 worker slices have disjoint writes and locks, whose runtime override cannot change topology, whose fallback and conflict exits are typed, and whose convergence, review, repair, and truth-sync ownership remain with the sovereign harness.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly replied `approve and $coding:implement-change`, accepting C0, the P1 conditional parallel batch, default `semantic-routing`, isolated worker worktrees, controller-owned convergence, and the declared recovery and stop boundaries.
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - Before any implementation mutation, the controller records Git status, content hashes, and source/generated parity for every pre-existing unrelated dirty path.
  - P1 workers use detached isolated worktrees seeded from one content-addressed CPR-010 dependency snapshot; they do not commit, integrate, generate public surfaces, or touch peer-owned files.
  - Worker results remain bounded patches until the controller verifies changed paths and narrow oracles, then applies them in stable task order and regenerates once.
  - An `allowed` parallel opportunity can safely serialize without changing the approved task contract; a proven conflict returns to dependency freeze instead of triggering automatic rollback.
  - Ordinary in-scope failures use fix-forward repair and narrow re-verification; shared-state ambiguity, unrelated drift, or non-causal aggregate failure stops mutation and preserves evidence.
  - No task uses guarded rollback, so this plan defines no rollback trigger, target, hook, or automatic restore path.
