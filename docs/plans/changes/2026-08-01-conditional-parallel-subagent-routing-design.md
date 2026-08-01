# Conditional Parallel Subagent Routing Design

## Status

- design_version: 1
- approval_required: true
- approval_status: approved
- approval_basis: The user approved making `plan-change` own task decomposition, dependency and parallel eligibility, delegation eligibility, and vendor-neutral execution-profile advice; making `implement-change` own runtime actor and model binding; preserving conditional parallelism and controller ownership; and allowing an execution-time `inherit-main` model and reasoning override without changing the approved task topology.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The harness already declares `implement-parallel`, accepts a plan-level `parallel_execution_approved` marker, records task dependencies and an unconstrained `executor_mode`, and allows `implement-change` to spawn agents. It does not yet define a complete portable contract for named parallel batches, task-level delegation eligibility, semantic model and reasoning profiles, isolation and resource conflicts, effective runtime concurrency, or the user override that makes spawned workers inherit the main agent's model and reasoning settings.

As a result, `plan-change` can describe parallel intent but cannot prove that a batch is safe, while `implement-change` can delegate ad hoc but has no deterministic ready-batch or runtime-binding contract. Concrete GPT model identifiers also cannot become reusable skill truth because the plugin targets multiple agent runtimes and model families change independently of the workflow contract.

## Goals

- Make `plan-change` produce a versioned executable DAG that identifies named parallel groups, dependency freeze, delegation policy, semantic execution and reasoning profiles, isolation requirements, and shared resource locks per task.
- Make `implement-change` bind approved tasks to the main agent, subagents, worktrees, concrete available models, and an effective concurrency width at execution time without changing the approved DAG or safety constraints.
- Default eligible work to conditional subagent delegation and semantic model routing while preserving an explicit `inherit-main` model and reasoning override.
- Keep reusable skill and runner contracts vendor-neutral by using `deep`, `balanced`, and `fast` execution profiles plus semantic reasoning profiles rather than concrete model identifiers.
- Preserve serial execution for tasks whose dependency, write-set, shared-resource, live-state, authority, or convergence boundaries are not frozen.
- Add deterministic validation, ready-batch selection, conflict evidence, compatibility behavior for existing plans, and bounded forward tests.
- Keep `implement-change` as the only implementation controller and repair owner; delegated workers and reviewers cannot widen scope, integrate independently, delegate recursively, or decide continuation.

## Non-Goals

- Add a second lifecycle controller, external orchestration service, provider-specific agent manifest, or universal model registry.
- Store GPT, Claude, Gemini, or other vendor model identifiers in reusable skills, plan schema enums, runner contracts, or stable architecture truth.
- Modify `~/.codex/config.toml`, create user-global custom agents, or assume a configured concurrency ceiling is available in every runtime.
- Make every ready task parallel, permit concurrent writes in one checkout without proven isolation, or bypass human approval for a named parallel group.
- Change review candidate adjudication, repair ownership, failure-policy semantics, truth-sync ownership, or close gates.
- Require old approved plans to be rewritten before they remain executable through an explicit compatibility path.

## Change Classification

- request_kind: harness-parallel-execution-contract
- change_class: B
- design_strength: design-lite
- truth_impact: high
- boundary_impact: medium
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: true

## Boundaries

- `plan-change` owns logical task decomposition, stable task IDs, dependencies, named parallel groups, parallel and delegation policy, semantic execution and reasoning profiles, isolation, resource locks, executable oracles, failure policy, and human approval.
- `implement-change` owns physical runtime binding: actor selection, concrete model selection from available equivalents, effective concurrency, spawn and wait orchestration, worktree assignment, convergence, verification, and typed fallback or stop behavior.
- The approved plan is authoritative for topology and safety. Runtime binding may choose a more conservative path but may not introduce undeclared concurrency, delegation, touch surfaces, authority, or resource sharing.
- `inherit-main` means spawned workers inherit the main agent's model and reasoning settings; it does not mean that a declared parallel group becomes one inline main-agent task.
- `review-change` remains the review gate. Reviewers return candidate evidence only, and `implement-change` remains the final adjudicator and sole repair owner.
- Deterministic Shell helpers validate and materialize portable scheduling metadata but do not embed vendor model identifiers or invoke a provider-specific agent API.
- User-global Codex configuration remains an external runtime concern. The approved `max_concurrent_threads_per_session = 6`, Sol fallback, and medium subagent reasoning preference are not repository writes in this milestone.

## Approved Execution Contract

- New execution-grade plans declare a contract version so the runner can enforce the new task metadata while retaining a deliberate compatibility path for older plans.
- Each task declares `parallel_group`, `parallel_policy`, `delegation_policy`, `execution_profile`, `reasoning_profile`, `isolation`, and `resource_locks` in addition to the existing dependency, touch-set, oracle, review-depth, done, and failure-policy fields.
- `parallel_policy` is `forbidden`, `allowed`, or `required`. `required` is exceptional and produces a typed stop when the approved topology cannot be honored; `allowed` may degrade to serial with recorded evidence.
- `delegation_policy` is `forbidden`, `allowed`, or `preferred`. The runtime may choose the main agent for `allowed`, defaults to a subagent for `preferred`, and may never delegate `forbidden` work.
- `execution_profile` is `deep`, `balanced`, or `fast`. `reasoning_profile` is `deep`, `standard`, or `light`. Concrete model and effort selection belongs to the active runtime adapter.
- Runtime model policy is `semantic-routing` by default, with `inherit-main` and `runtime-default` as explicit alternatives. A user override changes model binding only and does not rewrite dependencies, parallel groups, isolation, resource locks, or acceptance oracles.
- Effective concurrency is bounded by the runtime capacity, user configuration, number of ready tasks, approved batch limit, isolation, write-set overlap, and resource locks.
- Parallel write tasks require isolated worktrees. Shared-checkout delegation is limited to read-only work unless the plan proves an equivalent isolation boundary.
- A batch converges through the main controller before dependents become ready. The controller verifies actual changed paths, task oracles, batch-level integration evidence, and ledger state before review and continuation.
- A dependency, touch-set, resource-lock, or convergence conflict records `parallel-conflict` evidence and returns to dependency freeze. It does not authorize scope expansion or automatic rollback.
- Custom agent role files should own instructions, sandbox, and tool boundaries without pinning a model when execution-time semantic routing and `inherit-main` must remain effective.

## Compatibility And Recovery Boundary

- Existing plans without the new contract version retain their current serial-first or explicitly marked parallel behavior through compatibility parsing.
- New plans use strict enum, group, dependency, isolation, resource-lock, and profile validation before review.
- A runtime that lacks subagents or a recommended model may serialize `parallel_policy: allowed` work or use the configured fallback while preserving the task contract. It must stop for `parallel_policy: required` when no equivalent execution boundary exists.
- Ordinary validation or worker failure remains `fix_forward` inside the approved task slice. Shared-state or integration ambiguity stops and diagnoses; guarded rollback remains unavailable unless a task separately declares its exact trigger, target, and verification.

## Acceptance Conditions

- A new plan contract can express logical topology, delegation eligibility, semantic execution and reasoning profiles, isolation, and resource locks without concrete vendor model identifiers.
- Plan validation rejects unknown policy/profile values, unnamed or unsafe parallel membership, dependencies inside one simultaneously scheduled frontier, overlapping write surfaces, and overlapping resource locks unless the group is serialized.
- The task ledger can return a deterministic ready set and bounded conflict-free batch instead of only the first ready task.
- The execution runner can materialize a runtime-binding record that distinguishes semantic routing, `inherit-main`, and runtime defaults while preserving the same approved parallel group.
- Tests prove that `parallel_policy: allowed` may fall back to serial, `parallel_policy: required` produces a typed capacity stop, and `delegation_policy: forbidden` cannot be relaxed by the runtime.
- Tests prove that old plans remain compatible and that new plans receive strict validation.
- Source skills, generated root-flat surfaces, commands, workflow documentation, and machine contracts agree on ownership and fallback semantics.
- A bounded context-clean forward test demonstrates one named independent batch, semantic routing, the `inherit-main` override, worktree isolation, convergence, and unchanged controller-owned review and repair.
- Aggregate validation, sovereign harness smoke tests, Bash syntax and lint checks, generated-source parity, workflow diagram checks, and `git diff --check` pass without modifying unrelated dirty work.
- User-global Codex configuration and concrete model availability remain outside the repository mutation surface.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- reviewer_profile: balanced execution with deep reasoning
- review_status: passed
- candidate_findings: none
- review_evidence: A bounded read-only reviewer confirmed that the design preserves one sovereign implementation controller, assigns logical topology to `plan-change` and runtime binding to `implement-change`, keeps parallel writes conditional on isolation and conflicts, provides conservative fallback and typed stops, retains legacy compatibility, and keeps reusable contracts vendor-neutral.

## Human Gate

- approval_basis: The user explicitly accepted conditional parallel execution, the `plan-change` versus `implement-change` ownership split, portable semantic model profiles, default subagent routing, the `inherit-main` override, and a user-owned concurrency and fallback configuration.
- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

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
  - README.md
  - AGENTS.md
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/maintenance-contract.md
  - docs/changelog/design-decisions.md
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
