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

## Shared Runtime

Resolve both installed helpers relative to this `SKILL.md` before changing into the target repository. `SKILL_ROOT` is assigned by the agent to the activated skill directory; do not assume the host exported it:

```bash
SKILL_ROOT="/absolute/path/to/plan-change"
HARNESS_CLI="$(realpath "$SKILL_ROOT/scripts/harness/cli.py")"
[[ -f "$HARNESS_CLI" ]] || exit 1
```

Machine-check the upstream design before planning, then validate the plan and its approval state:

```bash
python3 "$HARNESS_CLI" design validate "<design-file>"
python3 "$HARNESS_CLI" plan validate "<plan-file>"
python3 "$HARNESS_CLI" plan compile "<plan-file>"
```

The plan starts with `approval_status: pending`; only explicit human approval changes it to `approved` and authorizes `implement-change`.

## Workflow

1. Load the approved design or boundary decision.
2. Run planning prerequisite clearance before drafting the implementation DAG.
3. If a non-automatable prerequisite is unresolved, return `manual_checkpoint` without producing an approval-ready plan.
4. Break the work into ordered tasks with explicit factual dependencies and stable task IDs.
5. Identify any remaining human confirmation, live-risk, destructive-write, external dependency, credential, or cutover uncertainty and resolve it before finalizing the plan whenever it does not depend on execution output.
6. Run work-package readiness before review.
7. Define touched files, executable oracles, verification commands, review depth, and failure policy for each task.
8. For each task, declare whether parallel execution and delegation are forbidden, allowed, or preferred/required as applicable; proactively name and dependency-freeze every safe parallel development group instead of leaving concurrency implicit.
9. Validate the plan artifact before review.
10. Route the artifact through mandatory plan review owned by `review-change` and bounded in-scope autofix when needed.
11. Hold the artifact at `approval_status: pending` until explicit human plan approval.
12. In the final planning summary, show whether execution can proceed continuously after approval or which confirmation IDs still need answers.
13. Stop after explicit human plan approval and hand off to `implement-change`.

## Planning Prerequisite Clearance

Clear non-automatable prerequisites before task decomposition. This entry gate covers external setup that the implementation depends on but the agent cannot safely complete within current authority, including account creation, interactive login or MFA enrollment, access grants, credential provisioning, subscription or license activation, and required physical actions.

- Report each unresolved prerequisite as a stable `C*` item with the exact human action and secret-safe completion evidence required.
- Return `decision_status: manual_checkpoint` and `execution_mode: not_ready`; do not draft or request approval for the implementation plan yet.
- Do not model these prerequisites as implementation DAG tasks, planned stop points, or runtime contingencies. They are planning-admission conditions, not unattended execution work.
- After the user completes them, verify the minimum safe evidence available, never record secret values, and restart planning from the now-cleared boundary.

If an external action can be automated safely inside already granted scope and authority, it may instead become a normal planned task with its own oracle. Lack of automation or authority must never be hidden as a mid-execution human gate.

## Implementation Language Decisions

Use `language-decision-tree` only when the approved scope introduces a new persisted project, tool, service, automation surface, or an approved implementation-language migration.

For each affected task, record enough decision metadata for implementation and review:

- `implementation_archetype`: for example `cli-tool`, `api-service`, `controller`, `batch-tool`, or `shell-orchestration`
- `implementation_language`: the selected language
- `language_rationale`: the distribution, ecosystem, runtime, ownership, or maintenance reason for the selection

Require these fields only when a task creates or replaces a persisted implementation boundary. Do not add placeholder language metadata to docs-only work, ordinary existing-language edits, generated-surface refreshes, or agent ad hoc commands.

## Explorer Eligibility

Use the explorer role only for pure repository search and factual confirmation. Explorer
eligibility is a portable no-write contract: such a task must have no implementation or test write refs, use `execution_profile: fast`, `reasoning_profile: light`, and `isolation: shared-read-only`; it may return bounded evidence and open questions but cannot edit, test-write, or make a design decision. A task that needs deeper synthesis, interpretation, or cross-file reasoning is a worker or main task, not an explorer, even when it does not write files.

Explorer authority is independent of physical model cost or reasoning effort. The parent session is the physical baseline, and user or host runtime policy may require a minimum uplift with no physical reasoning ceiling; a stronger binding never widens the explorer's read-only factual scope. Mixed search-and-judgment work must be decomposed into explicit explorer task IDs that return bounded facts and open questions, followed by a main-owned synthesis task. Do not let that synthesis task absorb otherwise independent fact-search slices. If the work needs interpretation or cross-file reasoning beyond the bounded facts, keep that reasoning in the synthesis task. Do not infer explorer eligibility from a model or provider name; record the semantic task profile in the approved plan and leave concrete binding to `implement-change`.

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

Do not enter work-package readiness while planning prerequisite clearance is unresolved. `subagent_ready` can become `true` only after those prerequisites are cleared and the delegated slice can run without later human setup.

If a task cannot declare an executable oracle or substitute verification, it is not ready for implementation unless the plan explicitly marks the task as docs-only, exploratory, or manual-evidence-only.

## Versioned Execution Contract

New execution plans use artifact `contract_version = 4`. Version-3 plans are compatibility evidence only: they may be read and digest-verified, but the refreshed runtime cannot initialize, mutate, admit, repair, or bind execution from them. Do not silently reinterpret or upgrade a version-3 artifact.

Truth-affecting version-4 plans contain `## Truth Sync Handoff` with non-empty `stable_truth_refs` and the required truth-sync flag matching the approved design. Stable truth refs must be safe repository-relative paths inside the immutable implementation touch set and must not point into `docs/plans/`. Record any docs-governance predicates in the human plan body: declare `none` when no component is needed; otherwise use only the supported ownership, truth-root, search-boundary, stage-placement, canonical-terminology, or prose-structure predicates. Missing or invalid truth scope returns `truth-sync-scope-required` instead of allowing execution or widening scope.

The plan owns logical execution shape. Every version-4 task declares:

- `parallel_group`: a stable named group or `none`
- `parallel_policy`: `forbidden | allowed | required`
- `delegation_policy`: `forbidden | allowed | preferred`
- `execution_profile`: `deep | balanced | fast`
- `reasoning_profile`: `deep | standard | light`
- `isolation`: `controller-checkout | isolated-worktree | shared-read-only`
- `resource_locks`: explicit shared-state locks or `none`

Use `parallel_execution_approved: true` only when the plan contains a named dependency-frozen parallel group. Every simultaneously eligible task in a group must have no direct or transitive dependency on a peer, disjoint writable file refs, disjoint resource locks, and an explicit batch limit. In `## Parallel Batches`, repeat one complete `batch_id` record per named group; its exact `tasks`, `max_parallelism`, optional policy summary, and `convergence_task` must agree with task metadata. Use `controller` as the convergence task only when convergence is owned directly by the harness rather than a later plan task. Parallel write tasks require `isolated-worktree`; `shared-read-only` is valid only when both implementation and test write refs are `none`, and any delegated writer requires an isolated worktree even when its task is serial.

DAG independence is necessary but not sufficient for parallel development. When two or more ready development tasks are independent, delegable, isolated, conflict-free in writable refs and resource locks, and covered by a bounded named batch, plan them for active parallel execution. Keep them serial only for a concrete dependency, safety, isolation, convergence, or authority reason and record that reason in the plan.

Use semantic routing advice rather than provider model identifiers. `execution_profile` describes task capability and cost; `reasoning_profile` describes task reasoning intensity, not an exact physical effort or ceiling. The plan also declares a default runtime model policy from `semantic-routing | inherit-main | runtime-default`. `semantic-routing` starts from the parent profile and may emit no override, an effort-only uplift, or a model-plus-explicit-effort uplift according to user or host minimum policy. A required uplift that the runtime rejects is a typed no-downgrade stop, not permission to retry through defaults or below the minimum. `inherit-main` and `runtime-default` cannot rewrite task IDs, dependencies, serial/parallel topology, isolation, locks, touch sets, or oracles.

## Exact External Files

Keep `impl_file_refs` and `test_file_refs` repository-relative. When an approved design must update an existing file outside the repository, use the separate optional `external_impl_file_refs` list and declare `external_touch_policy: exact-existing-files-v1`; never place an absolute path in a repository ref field. Every external ref is one exact, existing, canonical regular file with no glob, directory, symlink, hard link, create, delete, chmod, chown, or caller-selected rename authority. Preserve exact design-to-plan-to-task containment and keep repository and external sets disjoint.

Any task with external refs must use `executor_mode: main`, `delegation_policy: forbidden`, `parallel_policy: forbidden`, `parallel_group: none`, `isolation: controller-checkout`, and at least one named resource lock. It cannot enter a parallel batch, delegated envelope, isolated worker, or command job. The first capability rollout is a repository-only bootstrap plan; only a later independently reviewed and approved plan may consume the newly generated external channel. This prevents a plan from authorizing a capability that does not exist at its own preflight.

`implement-change` owns physical binding to the main agent or subagents, concrete available models, effective concurrency, worktrees, convergence, and recorded fallback. For an approved batch, it selects the maximal safe ready set up to the approved and available width. It may serialize `parallel_policy: allowed` work only when an observed limiting factor reduces effective width and the exact reason is recorded. It must return a typed capacity stop when `parallel_policy: required` cannot be honored. Workers never own integration, review adjudication, repair, or continuation.

## Execution Continuity

The goal of planning is to maximize uninterrupted execution after plan approval. Do not create stop gates as a default planning style.

Record a `## Execution Continuity` section with:
- `execution_mode`: `continuous_after_plan_approval`, `pre_confirmation_required`, or `not_ready`
- `confirmation_clearance`: stable `C*` items for known human decisions, named parallel-batch approval, destructive writes, live cutovers, or output-dependent external decisions; planning prerequisites such as manual account, login, access, or credential setup must already be cleared
- `runtime_contingencies`: stable `X*` items only for observed conditions that block authorized or safe continuation, such as unexpected loss of previously cleared authority or credentials, live state that invalidates the approved plan, loss of management connectivity, a routing or control-plane cycle, writer or quorum exclusivity risk, irreversible data-safety risk, or an explicitly declared guarded-rollback trigger; an ordinary verification failure is not itself a stop contingency
- `planned_stop_points`: should be empty for the normal case; non-empty only when a human decision factually depends on execution output and cannot be moved before planning or after all autonomous work
- `task_ordering_rationale`: explain how factual dependencies were preserved, planning prerequisites were cleared before task decomposition, and any unavoidable output-dependent human action was placed after every independent autonomous task that can precede it

Each `confirmation_clearance` item should include:
- `id`: example `C1`
- `question`: the exact decision needed from the user
- `applies_to`: task IDs
- `resolution`: `pre_confirmed`, `needs_confirmation_before_execution`, or `deferred_not_in_scope`
- `default_if_unanswered`: normally `stop`

Known user decisions should be resolved during planning whenever possible. If a known decision remains `needs_confirmation_before_execution`, the plan is not fully continuous and the final planning summary must lead with that fact.

Do not use `pre_confirmation_required` to carry unresolved manual external setup into an otherwise approval-ready plan. Account creation, login or MFA setup, access grants, and credential provisioning that cannot be automated are planning-entry gates and must be completed before the implementation DAG is finalized. A human action that genuinely depends on an execution-produced artifact may remain a planned stop only when the plan places it as late as factual dependencies allow and schedules all independent autonomous work before it.

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
- Undeclared or unproven work remains serial. Eligible version-4 tasks follow their declared delegation and parallel policies after approval and only after ledger-owned admission.
- Parallel work must be named, dependency-frozen, conflict-free, isolated when writable, and human-approved.
- Planning must surface eligible parallel development groups proactively; once approved, `implement-change` should use their maximal safe ready width instead of choosing serial execution without a recorded limiter.
- Prefer pre-confirming known gates during planning over deferring them into execution.
- Clear non-automatable external setup before drafting the implementation DAG; never turn it into an unattended mid-plan stop.
- Plan approval should normally authorize the whole plan to run; unresolved confirmations are exceptions that must be clearly labeled.
- Mandatory review happens before the human approval gate.
- The upstream design should already be `approval_status: approved` before planning starts.
- Review and verification requirements must be part of the plan, not implied later.
- Behavior-changing tasks should declare the failing test, narrow reproducer, or substitute verification evidence expected before implementation.
- Plan writers must not absorb every possible reviewer concern into the current milestone. Put out-of-scope concerns into `future_phase` or stop with `split_scope` / `needs_design_decision`.
- Tasks implementing an approved architecture decision should use reversible increments and preserve its upgrade triggers instead of buying all deferred complexity immediately.
- Each new task declares the complete version-4 task-ledger metadata, including `task_id`, `depends_on`, `scope_slice`, task-scoped file refs, `verification_commands`, executor and parallel/delegation/profile/isolation/lock fields, convergence and review budgets, `task_review_depth`, `done_when`, `failure_policy`, and explicit rollback fields.
- External-file tasks additionally declare exact `external_impl_file_refs` and the main-only, serial, locked execution contract above; repository-only plans omit the field and retain legacy behavior.
- Tasks that create or replace a persisted implementation boundary should also declare the conditional implementation-language decision described above.
- Task order should put low-risk, repo-local, reversible, and no-confirmation tasks before high-risk, live, destructive, or external-dependency tasks unless the risky task is a hard prerequisite.
- Legacy plans may remain readable in compatibility mode during transition, but new plans should not rely on that fallback.
