# Decision Record Lifecycle

Use this reference when creating, promoting, superseding, compacting, or retiring a durable decision record. Do not turn an ordinary documentation update into a decision audit.

## Disposition Matrix

| Current status | Future-value test | Disposition |
| --- | --- | --- |
| Proposed | The decision is not implemented or rejected. | Keep it in the stage-artifact root. Do not promote or archive it to satisfy a quota. |
| Implemented | Future maintainers need the boundary, rationale, consequences, compatibility obligation, or reconsideration trigger. | Promote or update the minimum durable explanation in the stable decision owner. Keep stage detail only when it adds useful context. |
| Implemented | Only one-time execution mechanics remain. | Remove them from stable docs. Keep useful operational history in its owner or delete it during authorized cleanup when it has no remaining value. |
| Rejected | The alternative remains tempting, risky, or likely to recur. | Keep a concise stable negative guardrail with the rejection reason and an observable reconsideration trigger. |
| Rejected | The alternative is obsolete and no longer prevents a plausible mistake. | Do not promote it. Delete obsolete records within the authorized cleanup instead of archiving them by default. |
| Superseded or removed | A newer owner covers the surviving behavior and material decision rationale. | Transfer any still-needed explanation or obligation, repair inbound links, then compact or delete the old entry. |
| Partially superseded | A public, persisted, wire, migration, compatibility, safety, or independently current negative decision survives. | Keep the old and new owners cross-linked. Do not claim full supersession. |

## Stable Record Contract

A stable decision explains the current choice and why it matters. Include the following only where they help future decisions:

- the current decision and status
- the constraint it resolves
- material alternatives and discard reasons
- consequences and compatibility obligations
- ownership when it is not already clear
- a meaningful reconsideration condition
- supersession links when another record shares or replaces authority

Migrate an older entry only when a real decision update touches it. Do not rewrite the full decision log for conformity.

## Safety Rules

- Retention follows current value and explicit repository obligations, not tracked status alone. Authorized cleanup may delete worthless history without a separate archival or preservation ceremony.
- Preserve still-relevant rationale and obligations when compacting or retiring a stable record; do not preserve incidental execution detail solely because it is unique.
- Repair inbound links before declaring full supersession.
- Keep partial supersession explicit when any independent obligation survives.
- Never use record counts, age, or completion quotas as an archive or deletion rule.

## Truth-Sync Predicate

Use `decision-record-lifecycle` only when an authorized truth sync must create, promote, supersede, compact, or retire stable decision truth. It activates bounded `organize-docs` work only for declared stable refs. It does not apply to a simple stable fact update and never makes `docs/plans/` a stable-truth ref.
