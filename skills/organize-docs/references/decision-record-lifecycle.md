# Decision Record Lifecycle

Use this reference when creating, promoting, superseding, compacting, or retiring a durable decision record. An ordinary documentation update stays outside it.

## Disposition Matrix

| Current status | Future-value test | Disposition |
| --- | --- | --- |
| `proposed` | The decision is not implemented or rejected. | Keep it in the stage-artifact root. |
| `implemented` | Future maintainers need the boundary, rationale, consequences, compatibility obligation, or reconsideration trigger. | Promote or update the minimum durable explanation in the stable decision owner. Keep stage detail only when it adds useful context. |
| `implemented` | Only one-time execution mechanics remain. | Remove them from stable docs. Keep useful operational history in its owner, or delete it when it has no remaining value. |
| `rejected` | The alternative remains tempting, risky, or likely to recur. | Keep a concise stable negative guardrail with the rejection reason and an observable reconsideration trigger. |
| `rejected` | The alternative is obsolete and has ceased to prevent a plausible mistake. | Delete it. |
| `superseded` or removed | A newer owner covers the surviving behavior and material decision rationale. | Transfer any still-needed explanation or obligation, repair inbound links, then compact or delete the old entry. |
| `partially-superseded` | A public, persisted, wire, migration, compatibility, safety, or independently current negative decision survives. | Keep the old and new owners cross-linked and the supersession partial. |

## Stable Record Contract

A stable decision explains the current choice and why it matters. Include the following only where they help future decisions:

- the current decision and status
- the constraint it resolves
- material alternatives and discard reasons
- consequences and compatibility obligations
- ownership where clarification helps
- a meaningful reconsideration condition
- supersession links when another record shares or replaces authority

Migrate an older entry only when a real decision update touches it.

## Safety Rules

- Retention follows current value and explicit repository obligations. Authorized cleanup may delete worthless history directly; assess archive and deletion decisions by value and obligations.
- Preserve still-relevant rationale and obligations when compacting or retiring a stable record, and drop incidental execution detail.
- Repair inbound links before declaring full supersession.
- Keep partial supersession explicit when any independent obligation survives.

## Admission

Apply this lifecycle when authorized docs work, including a `sync-truth` handoff, creates, promotes, supersedes, compacts, or retires stable decision truth in declared stable refs. A simple stable fact update stays outside it; `docs/plans/` holds stage artifacts.
