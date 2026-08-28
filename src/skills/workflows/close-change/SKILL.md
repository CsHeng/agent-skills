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
4. Return `closed` only when all evidence required for the requested purpose is current and complete; otherwise name the smallest owning gap.

## Outcomes

- `closed`: the requested change boundary is complete
- `needs-implementation`: implementation or verification remains incomplete
- `needs-review`: a required bounded review is absent or unresolved
- `needs-truth-sync`: stable truth still needs an authorized update
- `needs-authority`: the requested close action needs user or external authority
- `blocked`: required evidence is unavailable

Closure is a semantic judgment, not permission to merge, release, delete, commit, push, publish, or deploy. Do not infer completion from partial checks, stale output, or delegated summaries, and do not reopen earlier phases unless current evidence identifies that specific gap.
