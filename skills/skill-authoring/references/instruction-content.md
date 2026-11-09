# Instruction Content

Use this reference when writing or revising a Skill's body, references, scripts, or assets, and when reviewing any model-facing instruction file such as `AGENTS.md`, a `README.md` an agent reads, or a prompt section.

## Write Rules As Decisions

- State each rule as a trigger and a decision: when this situation holds, do this. A reader acts on the sentence directly.
- Give each doctrine one owning Skill or reference. Other Skills state at most one pointer sentence to that owner.
- The description carries the overlay or lifecycle-owner statement once; the body starts at the method.

## Positive Register

Models learn from what the text names, so an instruction corpus states what the reader does, chooses, and owns. Every rule, description sentence, boundary line and `AGENTS.md` item takes the same form: the situation, then the action or the owner.

- A negative clause has one of two jobs. It excludes a case from this rule's scope and names where that case goes (a receiver Skill, another rule, the user), or it corrects a misreading observed in practice. Attach it after the positive statement it bounds, at most one per rule.
- A contrast whose second half is only a foil ("X, not Y", "is not a Z", "rather than W", "does not mean V") becomes the positive statement alone, or names the owner of the other half: "Role selects purpose and routing; access grants own permission."
- A negative whose excluded case nobody would choose is deleted. A stack of forbidden cases primes those cases and reads as a checklist on instruction-literal routes.
- Examples of what to avoid, counterexamples, and anti-pattern lists live in a reference, with the body pointing to it.

Review a file against this register by listing its negated sentences and classifying each as exclusion with receiver, observed-misreading correction, foil, or dead case; `skill-composition-evaluation` in the architecture workspace retains the scan method.

## Progressive Disclosure

- Keep `SKILL.md` to admission, the decision steps, and pointers. Put the user's outcome, decision priorities, and essential boundaries first.
- Move narrow-trigger material into a reference and state its trigger in the body pointer: delegation, worktrees, long-task handoff, migration and replacement, compatibility, environment scope, temporary storage, dependency selection, naming, platform-specific notes, operational command examples, and extended checklists.
- The body points to a reference and the reference holds the content. When revising a Skill, reconcile the whole affected section and its composed Skills, and replace conflicting guidance in place.
- Deterministic code goes in `scripts/`, reusable output assets in `assets/`.
- Follow `output-styles` for response composition. Describe decision-relevant content; a mandatory format follows an explicit user request or an actual consuming interface.

## Status Vocabulary

All labels are kebab-case and shared across the collection; these tables are the complete set.

| Use | Labels |
| --- | --- |
| Workflow result (design, plan, implement, close) | `ready`; `needs-decision` qualified by `design`, `plan`, `authority` or `user`; `blocked` with the reason; `split-scope` |
| Recovery mode | `fix-forward`, `stop-and-diagnose`, `guarded-rollback` |
| Review verdict | `pass`, `needs-fixes`, `needs-decision`, `split-scope` |
| Caller disposition of a finding | accepted, rejected, deferred, escalated — plain words with a reason |
| Closure | `closed`, or `needs-` followed by the gap (`implementation`, `review`, `truth-sync`, `decision`) |

## Activated Instruction Content

- Keep distributed instructions focused on executable behavior, scope, authority, boundaries, and verification.
- Write every durable instruction as a proposition that resolves from the installed current state, independent of a review comment, authoring session, temporary branch, or unpublished draft.
- Preserve the subject, required action, conditions, ordering, modality, exceptions, ownership transfer, failure behavior, and consequences when simplifying instruction prose.
- Keep inspiration and provenance acknowledgements in the package root's human-facing documentation.
- Edit the authored owner directly. Where a repository generates provider projections, refresh them through its generator; directly authored metadata stays with its Skill.
- Review instruction meaning through realistic decisions; static distribution and link checks cover packaging hygiene. Use a diagram for relationships or flow when it explains more clearly than repeated paragraphs.
