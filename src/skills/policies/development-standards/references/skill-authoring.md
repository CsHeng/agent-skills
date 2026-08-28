# Skill Authoring

Use this reference when maintaining local skill inventories, descriptions, routers, or agent-agnostic workflow surfaces.

## Invocation Surface

- Model-invoked skills spend prompt context through their name and description every session. Use them only when the agent should route to the skill without the user naming it.
- User-invoked skills reduce prompt competition but require the user or a router skill to remember them.
- Keep overlapping third-party workflow libraries out of the default discovery surface unless their descriptions are curated and duplicate public IDs or ambiguous ownership are ruled out.
- Prefer a small router or wrapper for session defaults instead of exposing many broad workflow descriptions.

## Description Quality

- Put trigger conditions in the description, not only in the body.
- Keep descriptions specific enough to route but narrow enough not to steal unrelated tasks.
- Avoid duplicate synonyms that describe the same trigger branch.
- Mark retired, experimental, or user-only workflows so they do not compete with active model-routed skills.

## Progressive Disclosure

- Keep `SKILL.md` procedural and short.
- Move details into directly linked `references/`, deterministic code into `scripts/`, and reusable output assets into `assets/`.
- Do not duplicate the same rule across AGENTS files, command wrappers, and skill bodies; pick one durable owner and point to it.

## Activated Instruction Content

- Keep distributed instructions focused on executable behavior, scope, authority, boundaries, and verification.
- Write every durable instruction as a proposition that can be resolved from the installed current state. Do not depend on a review comment, authoring session, temporary branch name, or unpublished draft to complete its meaning.
- Preserve the subject, required action, conditions, ordering, modality, exceptions, ownership transfer, failure behavior, and consequences when simplifying instruction prose.
- Keep inspiration and provenance acknowledgements in the package root's human-facing documentation. Do not spend routine agent context on attribution that does not change runtime behavior.
- Edit the authored owner first, then refresh generated provider projections through the repository generator. Never repair generated copies by hand.
- When wording is model-visible or user-visible behavior, use a narrow structural, contract, snapshot, or runtime oracle owned by the affected surface.
