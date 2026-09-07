---
name: implement-change
description: "Implement an explicit bounded repository change or approved plan through mutation, verification, conditional review, accepted repair, and an evidence-backed outcome."
---

# Implement Change

Complete an explicit bounded repository change or an approved implementation plan while preserving its scope, authority, and acceptance evidence.

## Use This Skill When

- an explicit bounded user request or approved plan authorizes repository mutation
- implementation, verification, conditional review adjudication, and bounded repair need one semantic owner

Do not use it when a necessary scope, design, execution-order, prerequisite, or authority decision remains unresolved, or when the request is only analysis, review, truth sync, or closure. A separate design or plan artifact is not required for an otherwise sufficient bounded request; ordinary code investigation and local technical choices remain implementation work.

## Preconditions

- Confirm the authorized objective, any approved task order, repository ownership, allowed surfaces, protected behavior, acceptance evidence, applicable recovery policy, and known user changes. Use the approved plan when present; otherwise use the bounded request and applicable project contracts. Do not manufacture a plan, oracle-selection phase, delegation profiles, or review budget merely to begin local implementation.
- Inspect `git status --short` and preserve existing work. Default to the current checkout under Checkout And Concurrent Work below; dirty state alone is not a reason to create a worktree, clone, or branch.
- Treat commit, push, publication, deployment, destructive history changes, and external mutation as separate authority. Never infer them from approval to implement repository changes.
- Return `needs-authority`, `replan`, or `redesign` before performing work outside the approved boundary.

## Checkout And Concurrent Work

- Continue in the current checkout when the only uncommitted files are this task's design, plan, implementation, or evidence. Unrelated non-overlapping changes are also acceptable; preserve them and keep them outside this task's edits and any authorized commit. Committing task documents is optional and requires commit authority, not a prerequisite for implementation or a concurrency safeguard.
- If existing edits overlap the intended write set, inspect their content and ownership. Continue when they can safely be retained; otherwise resolve that specific conflict before writing. Do not reset, stash, overwrite, or isolate automatically merely to obtain a clean status.
- Prefer isolation only for a user request, an applicable repository rule, a required distinct branch state, a confirmed concurrent-write conflict, or overlapping state that cannot be safely preserved in place. When isolation is appropriate and authorized, use `git-worktrees` or another permitted mechanism and preserve uncommitted context explicitly; a new checkout does not inherit it. Isolation does not itself settle ownership or integration conflicts.
- Judge concurrency from the user's statement, already available host task evidence tied to the same checkout and writes, or unexpected changes observed during this task. Assess shared generated output, Git index/ref operations, and other shared resources as well as file overlap; multiple agents with disjoint safe operations do not automatically need worktrees. An agent process, dirty file, or recent modification timestamp alone is not proof of an active conflicting writer. Do not scan the whole workstation or build a coordination system to rule out hypothetical concurrency.
- Record the initial state, check the relevant current contents before edits, and reconcile the final diff against owned changes. If unexpected drift appears, pause affected writes and establish its source before proceeding; continue independent authorized work only when safe. These checks detect some conflicts, not mutual exclusion, and absence of visible activity does not prove there is no other writer.

## Implement And Verify

1. Inspect the smallest current surface needed for the next ready task. For bug fixes touching shared behavior:
   - Trace the reported symptom through the relevant entry point, shared function, and affected callers to the contract that owns the violated invariant.
   - Use symbol, reference, configuration, and test evidence as appropriate; account for public, generated, dynamic, or external callers when relevant. Text-search silence does not prove that all consumers are known. Keep inspection proportional to the proposed change rather than scanning the whole repository by default.
   - Choose a shared fix only when the affected callers share the invariant. Keep caller-specific product rules at their owning boundary and preserve intentionally different validation or error behavior; fewer guards or lines do not justify hoisting policy into a common helper.
   - If an unresolved caller contract prevents a safe bounded fix, state the evidence gap and use the existing `blocked`, `replan`, `redesign`, or `needs-authority` outcome that fits. Do not broaden the repair or turn it into a simplification audit.
2. Prefer a narrow reproducer or red-green oracle for non-trivial behavior. For shared-behavior fixes, select focused regression evidence for affected sibling paths and protected caller behavior as needed, without requiring one test per caller or prescribing a framework.
3. Make the smallest durable change within the approved scope and preserve unrelated user changes.
4. Complete all approved in-scope tasks whose dependencies can be satisfied; a task boundary is progress, not an automatic stopping point. When choosing a compatible delegation mechanism, preserve the approved repository owner, write set, resource locks, isolation, convergence owner, and optional execution and reasoning profiles. Submit ordinary independent slices as a flat batch. Encode a hard predecessor only when the approved implementation order requires it and no parent-owned synthesis, authority, verification, review adjudication, repair, or continuation decision occurs between the tasks.
5. Check the actual changed surfaces against the plan.
6. Remove abstractions, helpers, flags, and fallbacks this slice introduced that the approved behavior does not need. This is a same-slice cut, not a `code-simplification` audit and not a new task. If a cut needs a product tradeoff, stop and return `redesign` or `needs-authority`.
7. Run the declared verification and any focused checks needed for the changed behavior.
8. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
9. When review is required, request a bounded `review-change` evaluation over the current implementation diff with the objective, scope, changed files, declared oracles, and current verification evidence. Each invocation has one target; it does not consume a whole-change review allowance.
10. Adjudicate every material review candidate. Accept only findings causally tied to the current change and fixable inside the authorized scope.
11. For an in-scope verification failure or accepted finding, diagnose and repair against the same acceptance baseline, repeat the same-slice cut, and rerun affected and declared verification. Continue while there is an evidence-backed in-scope next step, without a default fixed repair count. Use targeted rereview when the repair invalidates prior review evidence, an independent question remains, or an applicable rule requires it. Do not automatically re-audit the whole repository after each edit.
12. Complete when the authorized objective, required verification, and material accepted findings are satisfied. Without new changes, failures, or unresolved risk, do not repeat checks or review merely to seek further confirmation.

Optional execution and reasoning profiles are semantic hints, not authority or provider bindings. Their absence or an unavailable host mapping does not block implementation: use a compatible default or retain the task in the active agent. When the user explicitly selects a concrete execution or reasoning route, preserve that choice through ephemeral task parameters when the compatible host supports them; the explicit user choice overrides semantic defaults for that invocation. Never mutate durable route configuration as a one-invocation workaround unless the user separately authorizes a persistent default change. Delegation does not transfer scope control, invocation judgment, verification, review adjudication, repair, continuation, or the final response.

Read `references/repair-loop.md` when verification or review produces an in-scope defect.

## Review Adjudication

Use one disposition for each material candidate:

- `accepted`
- `rejected_no_causal_link`
- `rejected_pre_existing`
- `rejected_out_of_scope`
- `rejected_insufficient_evidence`
- `deferred_followup`
- `needs_plan_change`

The reviewer is read-only. The implementing agent alone decides whether evidence supports a repair and owns any accepted repair. Severity or reviewer preference does not widen scope. Reuse prior dispositions only while their evidence applies to the current version; a different reviewer alone is not new evidence. Do not reopen a settled candidate without new evidence or overlook a new regression because an earlier version passed review.

## Acceptance Integrity

The approved objective, non-goals, dependencies, authority, protected contracts, and acceptance conditions remain the baseline throughout repair. Updating progress or adding execution evidence does not authorize rewriting these requirements to match the current implementation.

A mistaken test implementation may be corrected within authorized surfaces when an independent approved contract clearly establishes the right behavior; retain that evidence and apply the required review for oracle edits. Changing what counts as correct is a scope or design decision, not an implementation repair. Never weaken assertions, remove a failing requirement, or reduce the objective to manufacture a pass.

## Recovery

- `fix_forward` is the default: preserve evidence, diagnose the observed failure, repair within scope, and rerun the owning oracle.
- `stop_and_diagnose` preserves current state and stops further mutation.
- `guarded_rollback` requires an approved exact trigger, target, and rollback verification, plus evidence that rollback is safer than forward repair.

Never synthesize rollback, silently change task topology, or treat repeated failure as authority to redesign.

## Outcomes

- `pass`: implementation and required verification pass; no accepted finding from any required review remains
- `replan`: the approved scope, order, or verification is insufficient
- `redesign`: evidence invalidates an approved design boundary
- `needs-authority`: completion needs new user or external authority
- `guarded-rollback`: the approved rollback condition is met and its safe path is ready
- `non-convergent`: diagnosis yields no new evidence and no reasonable in-scope path remains; report what was tried, excluded, and still missing rather than a failure count
- `blocked`: required evidence or a prerequisite is unavailable, or work stopped on user cancellation or an explicit invocation time, call, or resource budget; name the actual reason and remaining work, not a claim that the objective is impossible

Return the outcome with changed files, verification evidence, the review decision and any resulting verdict or adjudication, repair evidence when applicable, and remaining uncertainty. Do not claim a write, install, deploy, commit, or push that was not actually performed.
