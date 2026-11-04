# Instruction Content

Use this reference when writing or revising a Skill's body, references, scripts, or assets.

## Write Rules As Decisions

- State each rule as a trigger and a decision: when this situation holds, do this. A reader should be able to act on the sentence without inferring what it forbids.
- Use at most one negated exclusion per rule, and only to separate a real confusable neighbor; name the receiver of the excluded case when one exists. A stack of "do not" sentences primes the behavior it names and reads as a checklist on instruction-literal models.
- Put examples of what not to do, counterexamples, and anti-pattern lists in a reference, with the body pointing to it.
- Give each doctrine one owning Skill or reference. Other Skills state at most one pointer sentence; they do not restate the rule, its exception list, or its rationale.
- A Skill's description already states that it is a conditional overlay or not a lifecycle owner; the body does not repeat that sentence.

## Progressive Disclosure

- Keep `SKILL.md` to admission, the decision steps, and pointers. Put the user's outcome, decision priorities, and essential boundaries first.
- Move narrow-trigger material into a reference and state its trigger in the body pointer: delegation, worktrees, long-task handoff, migration and replacement, compatibility, environment scope, temporary storage, dependency selection, naming, platform-specific notes, operational command examples, and extended checklists.
- When a reference exists, the body does not restate its content. When revising a Skill, reconcile the whole affected section and its composed Skills; replace conflicting guidance rather than appending another exception.
- Deterministic code goes in `scripts/`, reusable output assets in `assets/`.
- Follow `output-styles` for response composition. Describe decision-relevant content rather than fixed report templates; reserve mandatory formats for an explicit user request or an actual consuming interface.

## Status Vocabulary

All labels are kebab-case and shared across the collection; a Skill does not define a parallel set.

| Use | Labels |
| --- | --- |
| Workflow result (design, plan, implement, close) | `ready`; `needs-decision` qualified by `design`, `plan`, `authority` or `user`; `blocked` with the reason; `split-scope` |
| Recovery mode | `fix-forward`, `stop-and-diagnose`, `guarded-rollback` |
| Review verdict | `pass`, `needs-fixes`, `needs-decision`, `split-scope` |
| Caller disposition of a finding | accepted, rejected, deferred, escalated — plain words with a reason |
| Closure | `closed`, or `needs-` followed by the gap (`implementation`, `review`, `truth-sync`, `decision`) |

Uppercase modal labels, numbered gate taxonomies, and per-Skill enum lists are not used.

## Activated Instruction Content

- Keep distributed instructions focused on executable behavior, scope, authority, boundaries, and verification.
- Write every durable instruction as a proposition that can be resolved from the installed current state, independent of a review comment, authoring session, temporary branch, or unpublished draft.
- Preserve the subject, required action, conditions, ordering, modality, exceptions, ownership transfer, failure behavior, and consequences when simplifying instruction prose.
- Keep inspiration and provenance acknowledgements in the package root's human-facing documentation.
- Edit the authored owner directly. Where a repository generates provider projections, refresh them through its generator; directly authored metadata stays with its Skill.
- Review instruction meaning through realistic decisions; static distribution and link checks establish packaging hygiene, not the truth or effectiveness of the prose. Use a diagram for relationships or flow when it explains more clearly than repeated paragraphs.
