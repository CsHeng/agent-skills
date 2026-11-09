---
name: close-change
description: "Judge whether a verified change is ready for handoff, merge, release, or cleanup, or whether an explicitly guarded recovery action may proceed. Not for reporting an implementation run's own outcome, which implement-change owns, or for read-only branch facts, which analyze-project answers."
---

# Close Change

Decide whether a bounded change is complete for the requested close purpose.

## Use This Skill When

- implementation and required verification are complete
- the user wants an explicit handoff, merge, release, cleanup, or closure judgment

Discovering a missing review, truth sync, or authority at closure produces the matching `needs-` outcome. A standalone request to remove, prune, or repair a Git worktree uses `references/worktree-isolation.md` in `implement-change`.

## Closure Judgment

1. Confirm the requested close purpose and the evidence relevant to it.
2. Check implementation outcome, verification, the implementation review when one was required, accepted-repair evidence, truth-sync status, and any explicitly requested external action.
3. Separate completed work from actions not authorized or not performed (commit, push, publication, deployment, merge, destructive cleanup). Name the delivered version, any authorized secondary tradeoff with its reason and impact, and what was not verified.
4. Treat task membership, covered authority, and current capability as independent facts: an action outside this task stays out even under standing permission; an in-task action without covered authority returns `needs-decision`; authority without capability or evidence returns `blocked`. Consume already covered permission for the same target and side effects without re-asking, and pause only the increment whose goal, side effects, protected state, or permission changed.
5. Return `closed` only when all evidence required for the purpose is current for the specified version and endpoint; otherwise name the smallest owning gap. Allow `closed` with disclosed authorized secondary tradeoffs when the main goal and approved acceptance hold; an affected production action that was not performed leaves that endpoint incomplete.

Judge delivery by current evidence for the specified version at the requested endpoint. A push carries every still-unpushed commit and the CI/CD it triggers; name that gap when it is outside covered authority.

Account for active delegated work, unintegrated results, pending review or repair, and task workspaces still needed; mark owned execution resources as reclaimed, retained for a stated need, or unresolved. The implementation owner performs cleanup of resources it owns; closure gains no mutation authority over user branches or other workspaces.

## Outcomes

- `closed`: the requested change boundary is complete for the stated purpose
- `needs-implementation`: implementation or verification remains incomplete
- `needs-review`: a required bounded review is absent or unresolved
- `needs-truth-sync`: stable truth still needs an authorized update
- `needs-decision`: the requested close action needs user or external authority
- `blocked`: required evidence or capability is unavailable

Closure is a judgment; merging, releasing, deleting, committing, pushing, publishing, and deploying require their own covered authority.
