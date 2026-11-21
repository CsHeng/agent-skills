---
name: implement-change
description: "Implement an authorized bounded change—including multi-file, multi-repository, or operational updates under settled contracts—or an approved plan through mutation, proportionate verification, conditional review, and bounded repair. Undecided goals or boundaries belong to design-change; unresolved execution ordering or coordination belongs to plan-change."
---

# Implement Change

Complete the user's authorized outcome with the smallest durable change. The plan organizes the work; the user's goals, fixed choices, and real boundaries bind it. `development-standards` is the baseline for necessity and proportionate evidence.

## Use This Skill When

- an explicit bounded user request or approved plan authorizes repository mutation
- implementation, verification, conditional review adjudication, and bounded repair need one semantic owner

A bounded request is sufficient authorization for implementation. Undecided goals, boundaries, or acceptance go to `design-change`; unresolved ordering, cross-actor coordination, or authority gates go to `plan-change`.

## Preconditions

- Establish the objective and the boundaries that apply to this change from the approved plan when present, otherwise from the request and applicable project contracts: approved order, repository ownership, allowed surfaces, protected behavior, acceptance evidence, recovery policy, and known user changes. Resolve discoverable facts in the authorized workspace.
- Inspect `git status --short` and preserve existing work.
- Treat task membership, authority, and capability as separate facts. Commit, push, publication, deployment, destructive history changes, and mutation outside the task's authorized repositories and development environment each need matching authority beyond implementation approval; local reads, builds, tests, scratch files, and task-owned development services proceed without asking. Act on existing trusted permission for the same target and side effects; a design-only, source-only, or narrower request keeps its scope until the user adds delivery work. A push carries its entire outgoing history and the CI/CD it triggers.
- When an action would exceed a real goal, hard constraint, commitment, risk, or permission, obtain the narrow decision for that impact first and continue independent authorized work meanwhile.

## Execute The Settled Change

Implement the settled goals with the selected technology. Local investigation, glue, ordinary tests, same-task repair, and files the change causally requires are implementation work; an initial write inventory provides context. A `needs-decision` result describes an unresolved conflict for its owner.

Build a thin real path with useful local feedback first. For a replacement, follow `references/replacement-and-cutover.md` in `development-standards`: necessary prechecks, cutover, real-path verification, fix-forward repair. When supporting work grows while useful behavior stalls, reconsider the mechanism before assigning more workers or repairing every defect it creates; move non-prerequisite verification after cutover within existing authority. A known defect still gets a disposition against the actual outcome and risk.

## Goals And Discretion

Main goals, necessary conditions, user-fixed technical choices, exclusions, explicit user-fixed checks, and inviolable boundaries bind. Plan approval binds required outcome and boundary acceptance at the delivery endpoint; model-inferred task granularity, dependencies, ordering, guards, compatibility assumptions, and local proof methods stay revisable within that intent, and are corrected under existing approval when the required outcome and real boundaries hold. Authorized best-effort secondary work is adapted or omitted on evidence while the main goal continues, with the discretion and its effect recorded; a required result keeps its label and its oracle.

Investigate facts and generate execution products. After the user answers a blocking question, resume the original authorized work. When a later user instruction changes task authority, reconcile it with the current objective and endpoint and, where the record update is authorized, rewrite the authorization block as one current account as described in `plan-change`'s delivery reference.

Continue until every requested part of the authorized outcome is delivered or a named boundary stops it; verification is complete when the evidence covers the changed behavior, affected consumers, and stated acceptance. A status note, a completed milestone, a list of remaining work, or a recommendation on an open decision travels in the same turn with the next ready action (or with a supported worker-wait yield when only running workers remain), while work independent of a pending user answer continues. Before ending the task, compare the actual result and evidence against each part of the request so every requested item is accounted for. Host interruption, user cancellation, and explicit invocation budgets end work as `blocked` with the remainder named.

During long tasks keep the objective, current result, remaining work, real blockers, and effective authority recoverable at milestones and handoffs. `plan.md` is an authorization, boundary, and handoff record; transient step tracking lives in working context or the host's passive task list, and `plan.md` changes only to reconcile an explicit authority, scope, or decision change or to record a handoff or terminal summary. Completion is the main agent's judgment from the actual result and evidence; acceptance, test, and review obligations come from the request and applicable policy.

## Checkout And Concurrent Work

- Continue in the current checkout when uncommitted files are this task's own material or unrelated non-overlapping changes; preserve the latter and keep them out of this task's edits and any authorized commit.
- When existing edits overlap the intended write set, inspect their content and ownership, continue when they can be retained safely, and otherwise resolve that specific conflict before writing. A reset, stash, or overwrite is a resolution only when its owner agrees.
- Judge concurrency from the user's statement, host task evidence tied to the same checkout, or unexpected changes observed during this task, covering shared generated output and Git index or ref operations as well as file overlap. When drift appears, read and reconcile it, then continue under the existing goals, authority, and host access limits. When the host uses isolated candidates, observe its apply checks and reconcile or refresh through the supported path.
- Read [Worktree Isolation](references/worktree-isolation.md) when this task needs its own Git worktree: an explicit request, an applicable repository rule, a required branch state, or a concrete conflict the current checkout cannot absorb. Host-managed isolation for delegated tasks follows the host procedure; Git mutation authority comes from the request and applicable policy.

## Implement And Verify

1. Inspect the smallest current surface needed for the next ready task. For a bug fix in shared behavior, trace the symptom through the entry point, shared function, and affected callers to the contract that owns the invariant, using symbol, reference, configuration, and test evidence; choose a shared fix when the affected callers share the invariant and keep caller-specific rules at their owning boundary. When an unresolved caller contract prevents a safe bounded fix, state the gap and return the fitting outcome.
2. For non-trivial behavior changes or bug fixes, use an existing check or narrow reproducer that exercises the affected contract and sibling paths (capturing before-state evidence when practical). Add a persisted regression test when requested, required by repository policy, or needed to catch a specific failure that existing checks miss.
3. Make the smallest cohesive change that advances required behavior within the approved scope: least total responsibility and maintenance burden.
4. Complete all approved in-scope tasks whose dependencies can be satisfied; treat each task boundary as progress toward the outcome. Read [Delegated Execution](references/delegated-execution.md) before choosing delegation slices and when dispatching or continuing a worker, interpreting a result, or recovering a failed invocation.
5. Check changed surfaces against the user's goal, acceptance, authority, and fixed boundaries. Admit a discovered issue when the change caused it or it demonstrably blocks the authorized outcome; report unrelated existing failures separately. Reassess a growing mechanism before treating each resulting defect as a new goal.
6. When assessing a delegated result or finishing a slice, review what this change added: keep each new abstraction, guard, test, fixture, and document that names a behavior the outcome depends on, and fold or delete the rest of the additions, including ones a plan or review named. Preserve unrelated existing material unless this change made it obsolete. A requested broader audit uses `references/simplification.md` in `skills-routing`.
7. Run one verification strategy for the change. Required outcome acceptance, exclusions, and explicit user-fixed checks bind; choose the lowest-cost sufficient local proof for the actual diff from affected behavior, consumers, and uncertainty, and skip intermediate simulations a plan proposed when deterministic unit or schema checks plus authorized real-path verification already prove the boundary. A check that failed to start or only parsed syntax leaves runtime behavior unverified; report what actually ran and the remaining behavioral gap. Finish related edits before repeating checks that inform only the completed group. The main agent selects and times integration, E2E, and full-suite checks at useful joins, uses a full suite for relevant broad impact, an explicit delivery requirement, or uncertainty narrower evidence cannot resolve, and reuses applicable worker results.
8. When a condition in `review-change` holds, obtain bounded review of one target with the objective, diff, and current evidence; otherwise rely on the verification from steps 5 and 7 and continue to step 10.
9. Adjudicate the findings you own and repair accepted defects with [Focused Implementation Repair](references/repair-loop.md), rerunning the evidence the repair invalidated and retaining the rest.
10. At completion, if this task used worktrees, [release them](references/worktree-isolation.md#clean-up-and-repair), including delegated ones, and verify removal or report what remains and why. Complete when the authorized objective, delivery endpoint, necessary verification, and accepted findings are satisfied. Report the delivered result, its evidence, authorized secondary tradeoffs, and any unverified remainder; missing downstream permission or capability blocks that step only.

## Delegation And Profiles

Optional execution and thinking profiles are provider-neutral hints; an absent or unmapped profile means a compatible default or keeping the task local. Use an execution preference alone when its host-selected thinking effort fits the task; add a thinking preference when the reasoning investment needs an independent adjustment. The host owns concrete model bindings and capability adaptation. An explicit user choice of model or thinking level is preserved through ephemeral task parameters for that invocation; durable route configuration changes only under separate authority. Delegation transfers bounded investigation, implementation, verification execution, diagnosis, and authorized repair labor; the main agent judges delegation costs, assigns work, tracks overall progress, and owns scope control, verification strategy, final acceptance, and the final response. When the host supports peer messaging or a shared workspace, use [Delegated Execution](references/delegated-execution.md) for peer coordination, in-brief repair, and escalation within those capabilities. When workers are running and no independent runnable work remains, wait or yield according to the host's completion mechanism as described in [Delegated Execution](references/delegated-execution.md).

## Recovery

- `fix-forward` is the default: preserve evidence, diagnose the observed failure, repair within scope, and rerun the owning oracle.
- `stop-and-diagnose` preserves current state and stops further mutation when continued mutation would compound uncertainty.
- `guarded-rollback` runs only under an approved exact trigger, target, and rollback verification, with evidence that rollback is safer than forward repair; repeated failure alone leaves the existing design and recovery decision in place.

## Outcomes

- `ready`: the authorized delivery endpoint is reached, required verification passes, and no accepted finding remains. Disclose authorized secondary tradeoffs when the main goal and approved acceptance hold. A source-only endpoint is ready on source evidence; when a requested delivery or production step still lacks authority or capability, report completed local work and return `needs-decision: authority` (when user or external permission is the gap) or `blocked` (when a prerequisite or capability is unavailable).
- `needs-decision`: qualified as `plan` when the approved scope, order, or verification is insufficient, `design` when evidence invalidates an approved design boundary, or `authority` when completion needs new user or external authority, after completing independent authorized work that can run meanwhile. Include the evidence, a recommendation, and what each answer changes.
- `blocked`: a required prerequisite, evidence source, or capability remains unavailable after diagnosing and working through ordinary obstacles (retrying a transient error or timeout, fixing a call, or using an available fallback tool or source), diagnosis yields no new evidence and no in-scope path remains, or work stopped on cancellation or an explicit budget. Name the actual reason, what was tried, and the remaining work.

Report what changed, the evidence, and material limits or unfinished work; include review or repair conclusions when they affect acceptance, and report only actions actually performed.
