---
name: plan-change
description: "Use after approved design or scope to create execution-grade plans with task order, conditional parallel and delegation policy, semantic execution-profile advice, verification, and explicit recovery policy."
---

# Plan Change

Compile an approved change into an execution plan the harness can govern.

## Use This Skill When

- an approved design or explicit boundary decision needs an implementation plan
- the harness must define task order, write sets, or verification commands
- the change needs dependency freeze or an explicit recovery policy before execution

## Do Not Use This Skill When

- the request still needs change classification or design approval
- the user only wants code execution against an already approved plan
- the task is only review, truth sync, or close

## Bundled Runtime

Resolve both installed helpers relative to this `SKILL.md` before changing into the target repository. `SKILL_ROOT` is assigned by the agent to the activated skill directory; do not assume the host exported it:

```bash
SKILL_ROOT="/absolute/path/to/plan-change"
DESIGN_RUNNER="$(realpath "$SKILL_ROOT/scripts/harness/design-runner.sh")"
PLAN_RUNNER="$(realpath "$SKILL_ROOT/scripts/harness/plan-runner.sh")"
[[ -f "$DESIGN_RUNNER" && -f "$PLAN_RUNNER" ]] || exit 1
```

Machine-check the upstream design before planning, then validate the plan and its approval state:

```bash
bash "$DESIGN_RUNNER" validate "<design-file>"
[[ "$(bash "$DESIGN_RUNNER" approval-status "<design-file>")" == "approved" ]] || exit 1
bash "$PLAN_RUNNER" entry-phase
bash "$PLAN_RUNNER" default-path "<design-file>"
bash "$PLAN_RUNNER" validate "<plan-file>"
bash "$PLAN_RUNNER" approval-status "<plan-file>"
```

The plan starts with `approval_status: pending`; only explicit human approval changes it to `approved` and authorizes `implement-change`.

## Workflow

1. Load the approved design or boundary decision.
2. Break the work into ordered tasks with explicit dependencies and stable task IDs.
3. Identify any human confirmation, live-risk, destructive-write, external dependency, credential, or cutover uncertainty and try to resolve it before finalizing the plan.
4. Run work-package readiness before review.
5. Define touched files, executable oracles, verification commands, review depth, and failure policy for each task.
6. For each task, declare whether parallel execution and delegation are forbidden, allowed, or preferred/required as applicable; name and dependency-freeze every parallel group.
7. Validate the plan artifact before review.
8. Route the artifact through mandatory plan review owned by `review-change` and bounded in-scope autofix when needed.
9. Hold the artifact at `approval_status: pending` until explicit human plan approval.
10. In the final planning summary, show whether execution can proceed continuously after approval or which confirmation IDs still need answers.
11. Stop after explicit human plan approval and hand off to `implement-change`.

## Implementation Language Decisions

Use `language-decision-tree` only when the approved scope introduces a new persisted project, tool, service, automation surface, or an approved implementation-language migration.

For each affected task, record enough decision metadata for implementation and review:

- `implementation_archetype`: for example `cli-tool`, `api-service`, `controller`, `batch-tool`, or `shell-orchestration`
- `implementation_language`: the selected language
- `language_rationale`: the distribution, ecosystem, runtime, ownership, or maintenance reason for the selection

Require these fields only when a task creates or replaces a persisted implementation boundary. Do not add placeholder language metadata to docs-only work, ordinary existing-language edits, generated-surface refreshes, or agent ad hoc commands.

## Explorer Eligibility

Use the cheap explorer profile only for pure repository search and factual confirmation. Such a task
must have no implementation or test write refs, use `execution_profile: fast`,
`reasoning_profile: light`, and `isolation: shared-read-only`; it may return bounded evidence and open
questions but cannot edit, test-write, or make a design decision. A task that needs deeper synthesis,
interpretation, or cross-file reasoning is a worker or main task, not a cheap explorer, even when it
does not write files. Do not infer explorer eligibility from a model or provider name; record the
semantic profile in the approved plan and leave concrete binding to `implement-change`.

## Approved Architecture Decisions

When the upstream design contains an approved architecture decision, plan its implementation without rerunning selection. Record:

- `architecture_decision_ref`: the upstream `architecture_decision_id` or stable design section
- `reversible_increments`: ordered slices that buy information early and preserve a safe exit path
- `upgrade_triggers`: observable conditions that authorize deferred architecture supply or a return to design
- task-scoped implementation, oracle, rollout, recovery policy, ownership, and cleanup work for the chosen option

Do not rescore or reopen the approved tradeoff merely because another pattern is available. If current repository or runtime evidence invalidates the approved demand, constraint, owner, hard requirement, or upgrade trigger, stop with `needs_design_decision` instead of silently changing the architecture inside the plan.

Require these fields only when the approved design carries architecture economics. Ordinary tasks inside an established boundary do not need placeholder decision metadata.

## Work-Package Readiness

Before review, the plan must prove that the current milestone is small enough to execute.

Record a `## Work Package Readiness` section with:
- `milestone_objective`
- `non_goals`
- `future_phase`
- `decision_status`: `ready_for_review`, `needs_design_decision`, `split_scope`, or `manual_checkpoint`
- `oracle_strategy`: selected with `executable-oracle-architecture-selector` when behavior, architecture, or runtime correctness is non-trivial
- `acceptance_oracles`: concrete tests, contracts, probes, dry-runs, manual evidence, or substitute verification
- `execution_continuity`: `continuous_after_plan_approval`, `pre_confirmation_required`, or `not_ready`
- `max_review_batches`: default `2`
- `subagent_ready`: `true` only when at least one declared delegated slice can execute without redefining scope, authority, topology, or oracles

If `decision_status` is not `ready_for_review`, stop and return that typed state instead of making the plan bigger.

If a task cannot declare an executable oracle or substitute verification, it is not ready for implementation unless the plan explicitly marks the task as docs-only, exploratory, or manual-evidence-only.

## Versioned Execution Contract

New execution plans use `plan_contract_version: 2`. Plans without a contract version remain on the deliberate legacy compatibility path; do not silently reinterpret them as version 2.

Truth-affecting version-2 plans also contain `## Truth Sync Handoff` with non-empty `stable_truth_refs` and `docs_governance_predicates`. Stable truth refs must be safe repository-relative paths inside the immutable implementation touch set and must not point into `docs/plans/`. Declare `none` when no docs-governance component is needed; otherwise use only the supported ownership, truth-root, search-boundary, stage-placement, canonical-terminology, or prose-structure predicates. Missing or invalid truth scope returns the typed `truth_sync_scope_required` planning state instead of allowing execution or widening scope.

The plan owns logical execution shape. In addition to the existing task metadata, every version-2 task declares:

- `parallel_group`: a stable named group or `none`
- `parallel_policy`: `forbidden | allowed | required`
- `delegation_policy`: `forbidden | allowed | preferred`
- `execution_profile`: `deep | balanced | fast`
- `reasoning_profile`: `deep | standard | light`
- `isolation`: `controller-checkout | isolated-worktree | shared-read-only`
- `resource_locks`: explicit shared-state locks or `none`

Use `parallel_execution_approved: true` only when the plan contains a named dependency-frozen parallel group. Every simultaneously eligible task in a group must have no direct or transitive dependency on a peer, disjoint writable file refs, disjoint resource locks, and an explicit batch limit. In `## Parallel Batches`, repeat one complete `batch_id` record per named group; its exact `tasks`, `max_parallelism`, optional policy summary, and `convergence_task` must agree with task metadata. Use `controller` as the convergence task only when convergence is owned directly by the harness rather than a later plan task. Parallel write tasks require `isolated-worktree`; `shared-read-only` is valid only when both implementation and test write refs are `none`, and any delegated writer requires an isolated worktree even when its task is serial.

Use semantic routing advice rather than provider model identifiers. `execution_profile` describes capability and cost; `reasoning_profile` describes reasoning intensity. The plan also declares a default runtime model policy from `semantic-routing | inherit-main | runtime-default`. `semantic-routing` is the default for eligible tasks. An execution-time `inherit-main` override changes worker model and reasoning binding only; it cannot rewrite task IDs, dependencies, serial/parallel topology, isolation, locks, touch sets, or oracles.

`implement-change` owns physical binding to the main agent or subagents, concrete available models, effective concurrency, worktrees, convergence, and recorded fallback. It may conservatively serialize `parallel_policy: allowed` work. It must return a typed capacity stop when `parallel_policy: required` cannot be honored. Workers never own integration, review adjudication, repair, or continuation.

## Execution Continuity

The goal of planning is to maximize uninterrupted execution after plan approval. Do not create stop gates as a default planning style.

Record a `## Execution Continuity` section with:
- `execution_mode`: `continuous_after_plan_approval`, `pre_confirmation_required`, or `not_ready`
- `confirmation_clearance`: stable `C*` items for known human decisions, named parallel-batch approval, destructive writes, live cutovers, credential needs, or external dependencies
- `runtime_contingencies`: stable `X*` items only for observed conditions that block authorized or safe continuation, such as missing required authority or credentials, live state that invalidates the approved plan, loss of management connectivity, a routing or control-plane cycle, writer or quorum exclusivity risk, irreversible data-safety risk, or an explicitly declared guarded-rollback trigger; an ordinary verification failure is not itself a stop contingency
- `planned_stop_points`: should be empty for the normal case; non-empty only when a known issue cannot be safely pre-confirmed during planning
- `task_ordering_rationale`: explain why low-risk, no-confirmation tasks run before live, destructive, or high-risk tasks unless a risky task is a hard prerequisite

Each `confirmation_clearance` item should include:
- `id`: example `C1`
- `question`: the exact decision needed from the user
- `applies_to`: task IDs
- `resolution`: `pre_confirmed`, `needs_confirmation_before_execution`, or `deferred_not_in_scope`
- `default_if_unanswered`: normally `stop`

Known user decisions should be resolved during planning whenever possible. If a known decision remains `needs_confirmation_before_execution`, the plan is not fully continuous and the final planning summary must lead with that fact.

Use `runtime_contingencies` only for uncertainty that cannot be settled before execution. They are not routine human checkpoints.

## Failure Policy

Every new plan must include a `## Recovery` section with `default_failure_policy: fix_forward`. A backup, snapshot, retained source tree, previous release, HA peer, or VRRP failover path is recovery evidence; its existence does not authorize restoring old state.

Every task declares one `failure_policy`:

- `fix_forward`: default; diagnose, repair inside the approved touch set, rerun the narrow oracle, and continue toward cutover.
- `stop_and_diagnose`: preserve state and evidence, then stop mutation because continuing could compound an unresolved risk; do not restore old state automatically.
- `guarded_rollback`: use only when the task declares exact `rollback_trigger`, `rollback_target`, and `rollback_verification`, the trigger is observed, and restoring the target is tested and safer than forward repair.

Ordinary compile, test, probe, deploy-verification, or service-health failures do not justify guarded rollback by themselves. Do not add a `## Rollback` section unless at least one task uses `guarded_rollback`. When the user explicitly says no rollback or fix-forward, the plan must not contain rollback hooks, traps, restore steps, or rollback metadata.

## Planning Summary

When plan writing and mandatory plan review are complete, the response must include a concise execution-readiness summary before asking for approval:
- `C0`: no remaining confirmation needed; approval authorizes continuous execution
- or `C1`, `C2`, ...: exact confirmations still needed before execution
- `E1`, `E2`, ...: task ranges expected to run continuously
- `X1`, `X2`, ...: runtime contingencies that would stop execution only if triggered by observed evidence

Do not finish plan-change with only a generic approval request. The user must be able to see whether approving the plan will let `implement-change` run through the whole plan or where it will stop.

## Operating Rules

- This is a top-level harness entry.
- A prose status summary is not a valid plan artifact.
- New implementation plans should be execution-grade task catalogs, not prose-only checklists.
- Undeclared or unproven work remains serial. Eligible version-2 tasks follow their declared delegation and parallel policies after approval.
- Parallel work must be named, dependency-frozen, conflict-free, isolated when writable, and human-approved.
- Prefer pre-confirming known gates during planning over deferring them into execution.
- Plan approval should normally authorize the whole plan to run; unresolved confirmations are exceptions that must be clearly labeled.
- Mandatory review happens before the human approval gate.
- The upstream design should already be `approval_status: approved` before planning starts.
- Review and verification requirements must be part of the plan, not implied later.
- Behavior-changing tasks should declare the failing test, narrow reproducer, or substitute verification evidence expected before implementation.
- Plan writers must not absorb every possible reviewer concern into the current milestone. Put out-of-scope concerns into `future_phase` or stop with `split_scope` / `needs_design_decision`.
- Tasks implementing an approved architecture decision should use reversible increments and preserve its upgrade triggers instead of buying all deferred complexity immediately.
- Each new task should declare enough metadata for task-ledger execution, including `task_id`, `depends_on`, `scope_slice`, task-scoped file refs, `verification_scope`, `executor_mode`, version-2 parallel/delegation/profile/isolation/lock fields, `task_review_depth`, `done_when`, and `failure_policy`.
- Tasks that create or replace a persisted implementation boundary should also declare the conditional implementation-language decision described above.
- Task order should put low-risk, repo-local, reversible, and no-confirmation tasks before high-risk, live, destructive, or external-dependency tasks unless the risky task is a hard prerequisite.
- Legacy plans may remain readable in compatibility mode during transition, but new plans should not rely on that fallback.
