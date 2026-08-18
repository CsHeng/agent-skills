# Decision Record Lifecycle

Use this reference when creating, promoting, superseding, compacting, or retiring a durable decision record. Do not turn an ordinary documentation update into a decision audit.

## Disposition Matrix

| Current status | Future-value test | Disposition |
| --- | --- | --- |
| Proposed | The decision is not implemented or rejected. | Keep it in the stage-artifact root. Do not promote or archive it to satisfy a quota. |
| Implemented | Future maintainers need the boundary, rationale, consequences, compatibility obligation, or reconsideration trigger. | Promote or update the minimum durable truth in the stable decision owner. Keep the stage artifact as historical evidence. |
| Implemented | Only one-time execution mechanics remain useful. | Leave the detail in stage history. Compact an existing stable record only after every unique durable fact has another current owner. |
| Rejected | The alternative remains tempting, risky, or likely to recur. | Keep a concise stable negative guardrail with the rejection reason and an observable reconsideration trigger. |
| Rejected | The alternative is obsolete and no longer prevents a plausible mistake. | Do not promote it. Retain an existing tracked stage artifact unless separately approved cleanup proves deletion is safe and useful. |
| Superseded or removed | A newer owner covers every surviving behavior and decision fact. | Transfer unique rationale, alternatives, consequences, verification gaps, compatibility facts, and reintroduction triggers; repair inbound links; then compact or retire the old stable entry. |
| Partially superseded | A public, persisted, wire, migration, compatibility, safety, or independently current negative decision survives. | Keep the old and new owners cross-linked. Do not claim full supersession. |

## Stable Record Contract

A new or materially updated stable decision records:

- the current decision and status
- the constraint it resolves
- material alternatives and discard reasons
- consequences and compatibility obligations
- the responsible owner
- an observable reconsideration trigger
- supersession links when another record shares or replaces authority

Migrate an older entry only when a real decision update touches it. Do not rewrite the full decision log for conformity.

## Safety Rules

- Preserve tracked stage history by default. Git history is not a substitute for the repository's explicit stage-artifact boundary.
- Transfer every unique durable fact before compacting or retiring a stable record.
- Repair inbound links before declaring full supersession.
- Keep partial supersession explicit when any independent obligation survives.
- Never use record counts, age, or completion quotas as an archive or deletion rule.

## Truth-Sync Predicate

Use `decision-record-lifecycle` only when an approved truth sync must create, promote, supersede, compact, or retire stable decision truth. It activates bounded `organize-docs` work only for declared stable refs. It does not apply to a simple stable fact update and never makes `docs/plans/` a stable-truth ref.
