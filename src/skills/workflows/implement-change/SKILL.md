---
name: implement-change
description: "Implement an explicit bounded repository change or approved plan through mutation, verification, conditional review, accepted repair, and an evidence-backed outcome."
---

# Implement Change

Complete an explicit bounded repository change or an approved implementation plan while preserving its scope, authority, and acceptance evidence.

## Use This Skill When

- an explicit bounded user request or approved plan authorizes repository mutation
- implementation, verification, conditional review adjudication, and bounded repair need one semantic owner

Do not use it while scope, design, plan, prerequisites, or required authority remain unresolved, or when the request is only analysis, review, truth sync, or closure.

## Preconditions

- Confirm the authorized objective, any approved task order, allowed surfaces, declared verification, recovery policy, and known user changes.
- Treat commit, push, publication, deployment, destructive history changes, and external mutation as separate authority. Never infer them from approval to implement repository changes.
- Return `needs-authority`, `replan`, or `redesign` before performing work outside the approved boundary.

## Implement And Verify

1. Inspect the smallest current surface needed for the next ready task.
2. Prefer a narrow reproducer or red-green oracle for non-trivial behavior.
3. Make the smallest durable change within the approved scope and preserve unrelated user changes.
4. Complete all approved in-scope tasks whose dependencies can be satisfied; a task boundary is progress, not an automatic stopping point.
5. Check the actual changed surfaces against the plan.
6. Run the declared verification and any focused checks needed for the changed behavior.
7. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
8. When review is required, invoke one bounded `review-change` evaluation over the converged implementation diff and supply the objective, scope, changed files, declared oracles, and current verification evidence.
9. Adjudicate every material review candidate. Accept only findings causally tied to the current change and fixable inside the authorized scope.
10. If accepted findings exist, apply at most one focused same-slice repair and rerun the affected and declared verification without starting another review or an unbounded repair loop.

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

The reviewer is read-only. The implementing agent alone decides whether evidence supports a repair and owns any accepted repair. Severity or reviewer preference does not widen scope.

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
- `non-convergent`: the single focused repair did not converge
- `blocked`: required evidence or a prerequisite is unavailable

Return the outcome with changed files, verification evidence, the review decision and any resulting verdict or adjudication, repair evidence when applicable, and remaining uncertainty. Do not claim a write, install, deploy, commit, or push that was not actually performed.
