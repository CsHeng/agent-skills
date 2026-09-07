---
name: close-change
description: "Use after a verified change to judge closure readiness for handoff, merge, release, cleanup, or an explicitly guarded recovery action."
---

# Close Change

Decide whether a bounded change is complete for the requested close purpose.

## Use This Skill When

- implementation and required verification are complete
- the user wants an explicit handoff, merge, release, cleanup, or closure judgment

Do not use it while design, planning, implementation, review, required truth sync, or requested authorization is unresolved. A local status query or cleanup suggestion alone does not require this Skill.

## Closure Judgment

1. Confirm the requested close purpose and the evidence relevant to it.
2. Check implementation outcome, verification, the formal implementation review when one was required, accepted-repair evidence, truth-sync status, and any explicitly requested external action.
3. Separate completed work from actions that were not authorized or performed, such as commit, push, publication, deployment, merge, or destructive cleanup.
4. Treat task membership, covered authority, and current capability as independent facts; consume already covered permission for the same target and side effects, and do not invent extra authority at closure.
5. Return `closed` only when all evidence required for the requested purpose is current for the specified version and endpoint; otherwise name the smallest owning gap.

## Task, Authority, And Capability

Whether an action belongs to this task, whether matching authority already covers it, and whether the current host can perform it are independent judgments. Standing deploy permission does not convert a design-only request into implementation or deployment. A plan that names delivery does not grant delivery authority. Stored credentials are not authorization.

When the requested purpose includes a delivery action and a trusted project convention or the current request already covers that same target and its side effects, consume that coverage after remaining premises check out. Do not re-ask for the same approval. Pause only the increment whose goal, side effects, protected state, or permission actually changed.

Do not expand standing permissions into this task at closure, and do not cut short an already authorized delivery because a later checklist looks heavy. If the action is outside this task, leave it out even when standing permission exists. If it is in this task but uncovered, return `needs-authority`. If authority is present but capability or required evidence is unavailable, return `blocked` without reporting a local artifact as end-to-end complete.

## Delivery Endpoint Evidence

Judge delivery by current evidence for the specified version at the requested endpoint, not by local checks, a delegated summary, or an adjacent artifact. A push includes every still-unpushed commit that would travel with it and the CI/CD side effects that push would trigger; those belong to the operation boundary. Name that gap when the extra history or triggered pipeline is outside covered authority, rather than pushing a truncated subset or silently widening permission.

## Outcomes

- `closed`: the requested change boundary is complete
- `needs-implementation`: implementation or verification remains incomplete
- `needs-review`: a required bounded review is absent or unresolved
- `needs-truth-sync`: stable truth still needs an authorized update
- `needs-authority`: the requested close action needs user or external authority
- `blocked`: required evidence or capability is unavailable

Closure is a semantic judgment, not permission to merge, release, delete, commit, push, publish, or deploy. Do not infer completion from partial checks, stale output, or delegated summaries, and do not reopen earlier phases unless current evidence identifies that specific gap.
