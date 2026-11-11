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

- Confirm the authorized objective, approved order, repository ownership, allowed surfaces, protected behavior, acceptance evidence, recovery policy, and known user changes from the approved plan when present, otherwise from the request and applicable project contracts.
- Inspect `git status --short` and preserve existing work.
- Treat task membership, authority, and capability as separate facts. Commit, push, publication, deployment, destructive history changes, and external mutation each need matching authority beyond implementation approval. Act on existing trusted permission for the same target and side effects; a design-only, source-only, or narrower request keeps its scope until the user adds delivery work. A push carries its entire outgoing history and the CI/CD it triggers.
- When an action would exceed a real goal, hard constraint, commitment, risk, or permission, obtain the narrow decision for that impact first and continue independent authorized work meanwhile.

## Execute The Settled Change

Implement the settled goals with the selected technology. Local investigation, glue, ordinary tests, same-task repair, and files the change causally requires are implementation work; an initial write inventory provides context. A `needs-decision` result describes an unresolved conflict for its owner.

Build a thin real path with useful local feedback first. For a replacement, follow `references/replacement-and-cutover.md` in `development-standards`: necessary prechecks, cutover, real-path verification, fix-forward repair. When supporting work grows while useful behavior stalls, reconsider the mechanism before assigning more workers or repairing every defect it creates; move non-prerequisite verification after cutover within existing authority. A known defect still gets a disposition against the actual outcome and risk.

## Goals And Discretion

Main goals, necessary conditions, user-fixed technical choices, exclusions, explicit user-fixed checks, and inviolable boundaries bind. Plan approval binds required outcome and boundary acceptance at the delivery endpoint; model-inferred task granularity, dependencies, ordering, guards, compatibility assumptions, and local proof methods stay revisable within that intent, and are corrected under existing approval when the required outcome and real boundaries hold. Authorized best-effort secondary work is adapted or omitted on evidence while the main goal continues, with the discretion and its effect recorded; a required result keeps its label and its oracle.

Investigate facts and generate execution products. After the user answers a blocking question, resume the original authorized work. When a later user instruction changes task authority, reconcile it with the current objective and endpoint and, where the record update is authorized, rewrite the authorization block as one current account as described in `plan-change`'s delivery reference.

Continue until the authorized outcome is delivered or a named boundary stops it; verification is complete when the evidence covers the changed behavior, affected consumers, and stated acceptance. Host interruption, user cancellation, and explicit invocation budgets end work as `blocked` with the remainder named.

During long tasks keep the objective, current result, remaining work, real blockers, and effective authority recoverable at milestones and handoffs. `plan.md` is an authorization, boundary, and handoff record; transient step tracking lives in working context or the host's passive task list, and `plan.md` changes only to reconcile an explicit authority, scope, or decision change or to record a handoff or terminal summary. Completion is the main agent's judgment from the actual result and evidence; acceptance, test, and review obligations come from the request and applicable policy.

## Checkout And Concurrent Work

- Continue in the current checkout when uncommitted files are this task's own material or unrelated non-overlapping changes; preserve the latter and keep them out of this task's edits and any authorized commit.
- When existing edits overlap the intended write set, inspect their content and ownership, continue when they can be retained safely, and otherwise resolve that specific conflict before writing. A reset, stash, or overwrite is a resolution only when its owner agrees.
- Judge concurrency from the user's statement, host task evidence tied to the same checkout, or unexpected changes observed during this task, covering shared generated output and Git index or ref operations as well as file overlap. When drift appears, read and reconcile it, then continue under the existing goals and authority. Host exact-write and candidate-apply checks stay binding; refresh or redispatch through the supported parent path.
- Read [Worktree Isolation](references/worktree-isolation.md) when this task needs its own Git worktree: an explicit request, an applicable repository rule, a required branch state, or a concrete conflict the current checkout cannot absorb. Host-managed isolation for delegated tasks follows the host procedure; Git mutation authority comes from the request and applicable policy.

## Implement And Verify

1. Inspect the smallest current surface needed for the next ready task. For a bug fix in shared behavior, trace the symptom through the entry point, shared function, and affected callers to the contract that owns the invariant, using symbol, reference, configuration, and test evidence; choose a shared fix when the affected callers share the invariant and keep caller-specific rules at their owning boundary. When an unresolved caller contract prevents a safe bounded fix, state the gap and return the fitting outcome.
2. Prefer a narrow reproducer or red-green oracle for non-trivial behavior, with focused regression evidence for affected sibling paths.
3. Make the smallest cohesive change that advances required behavior within the approved scope: least total responsibility and maintenance burden.
4. Complete all approved in-scope tasks whose dependencies can be satisfied; treat each task boundary as progress toward the outcome. Read [Delegated Execution](references/delegated-execution.md) before choosing delegation slices and when dispatching or continuing a worker, interpreting a result, or recovering a failed invocation.
5. Check changed surfaces against the user's goal, acceptance, authority, and fixed boundaries. Admit a discovered issue when the change caused it or it demonstrably blocks the authorized outcome; report unrelated existing failures separately. Reassess a growing mechanism before treating each resulting defect as a new goal.
6. When accepting a candidate or finishing a slice, keep each abstraction, guard, test, fixture, and document that names a behavior the outcome depends on, and fold or delete the rest, including ones a plan or review named. A requested broader audit uses `references/simplification.md` in `skills-routing`.
7. Run one verification strategy for the change. Required outcome acceptance, exclusions, and explicit user-fixed checks bind; choose the lowest-cost sufficient local proof for the actual diff from affected behavior, consumers, and uncertainty, and skip intermediate simulations a plan proposed when deterministic unit or schema checks plus authorized real-path verification already prove the boundary. Finish related edits before repeating checks that inform only the completed group. The main agent selects and times integration, E2E, and full-suite checks at useful joins, uses a full suite for relevant broad impact, an explicit delivery requirement, or uncertainty narrower evidence cannot resolve, and reuses applicable worker results.
8. Obtain independent review under the conditions `review-change` owns; when it runs, supply one bounded target with the objective, diff, and current evidence.
9. Adjudicate findings and repair accepted defects with [Focused Implementation Repair](references/repair-loop.md), rerunning the evidence the repair invalidated and retaining the rest.
10. Complete when the authorized objective, delivery endpoint, necessary verification, and accepted findings are satisfied. Report the delivered result, its evidence, authorized secondary tradeoffs, and any unverified remainder; missing downstream permission or capability blocks that step only.

## Delegation And Profiles

Optional execution and thinking profiles are provider-neutral hints; an absent or unmapped profile means a compatible default or keeping the task local. Use an execution preference alone when its host-selected thinking effort fits the task; add a thinking preference when the reasoning investment needs an independent adjustment. The host owns concrete model bindings and capability adaptation. An explicit user choice of model or thinking level is preserved through ephemeral task parameters for that invocation; durable route configuration changes only under separate authority. Delegation transfers bounded investigation, implementation, verification execution, diagnosis, and authorized repair labor; scope control, continuation decisions, cross-task synthesis, finding adjudication, final acceptance, and the final response stay with the parent. When no independent runnable work remains while workers run, end the turn and act on the completion notification.

## Recovery

- `fix-forward` is the default: preserve evidence, diagnose the observed failure, repair within scope, and rerun the owning oracle.
- `stop-and-diagnose` preserves current state and stops further mutation when continued mutation would compound uncertainty.
- `guarded-rollback` runs only under an approved exact trigger, target, and rollback verification, with evidence that rollback is safer than forward repair; repeated failure alone leaves the existing design and recovery decision in place.

## Outcomes

- `ready`: implementation and required verification pass and no accepted finding remains. Disclosed authorized secondary tradeoffs may remain when the main goal and approved acceptance hold; a requested production endpoint that was not performed is reported as not performed.
- `needs-decision`: qualified as `plan` when the approved scope, order, or verification is insufficient, `design` when evidence invalidates an approved design boundary, or `authority` when completion needs new user or external authority.
- `blocked`: required evidence, a prerequisite, or capability is unavailable, diagnosis yields no new evidence and no in-scope path remains, or work stopped on cancellation or an explicit budget. Name the actual reason, what was tried, and the remaining work.

Report what changed, the evidence, and material limits or unfinished work; include review or repair conclusions when they affect acceptance, and report only actions actually performed.
