# Instruction Content

Use this reference when writing or revising a Skill's body, references, scripts, or assets.

## Progressive Disclosure

- Keep `SKILL.md` procedural and short.
- Put the user's outcome, decision priorities, and essential boundaries before detailed tactics. When revising a skill, reconcile the whole affected section and its composed skills; replace conflicting guidance rather than appending another exception at the end.
- Move details into directly linked `references/`, deterministic code into `scripts/`, and reusable output assets into `assets/`.
- Do not duplicate the same rule across AGENTS files, command wrappers, and skill bodies; pick one durable owner and point to it.
- Follow `output-styles` for response composition. Describe decision-relevant content rather than fixed report templates; a supporting skill and its references must fit the owning deliverable without adding separate reports or expanding the task to populate fields. Reserve mandatory formats for an explicit user request or an actual consuming interface.

## Activated Instruction Content

- Keep distributed instructions focused on executable behavior, scope, authority, boundaries, and verification.
- Write every durable instruction as a proposition that can be resolved from the installed current state. Do not depend on a review comment, authoring session, temporary branch name, or unpublished draft to complete its meaning.
- Preserve the subject, required action, conditions, ordering, modality, exceptions, ownership transfer, failure behavior, and consequences when simplifying instruction prose.
- Keep inspiration and provenance acknowledgements in the package root's human-facing documentation. Do not spend routine agent context on attribution that does not change runtime behavior.
- Edit the authored owner directly. Where a repository generates provider projections, refresh them through its generator instead of editing generated copies; directly authored metadata stays with its Skill.
- Review instruction meaning through realistic decisions when useful; do not test literal sentences, keyword presence, or document digests. Static distribution and link checks establish packaging hygiene, not the truth or effectiveness of the prose. Use diagrams for relationships or flow when they explain more clearly than repeated paragraphs, with short prose for rationale and exceptions.
