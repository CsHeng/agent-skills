---
name: use-coding-skills
description: "Use when the user asks how local coding skills should be selected, when an ambiguous multi-stage request needs routing, or when session, memory, or compact-handoff boundaries need guidance. Do not load for tasks that directly match another skill."
---

# Use Coding Skills

Optional routing and session-boundary guidance for local coding work. Keep this skill small: it assists ambiguous selection and handoff without becoming a mandatory entry or a replacement for directly matched skills.

## Session Contract

- Treat repository-owned docs, code, scripts, tests, and skills as durable truth.
- Treat agent memories, sessions, logs, caches, and generated summaries as recall or staging evidence.
- Keep scope bound to the named repository, product surface, or workflow.
- Treat explicit read-only wording literally.
- Match response language to user input language unless file conventions require otherwise.
- Prefer current local evidence and live runtime checks over stale memory when verification is cheap.
- Verify current external facts before relying on versions, project support, APIs, protocols, pricing, laws, or ecosystem state.
- Do not write agent-specific rules when a skill can express the behavior in an agent-agnostic way.

## Default Routing

Use these rules only after this skill has matched an explicit routing or ambiguous multi-stage request:

- Read `references/routing.toml` as declarative authoring guidance for discovery, semantic trigger cases, response composition, and support routes.
- Match cases by the owner skill's frontmatter description and each case's negative boundaries; explicit-invocation cases keep positive overrides. Treat lexical hints as examples only; they are not a keyword router or a second owner map.
- Let an explicitly named skill or confident direct workflow or policy match bypass this router.
- Route ambiguous multi-stage work through this skill, then select the smallest matching workflow skill.
- Keep exactly one primary response owner. Compose matching session, discipline, policy, tool, or review-component skills only as semantic overlays.
- Review requests enter through `review-change`; artifact-specific `review-*` skills are optional read-only evaluators, not top-level workflow owners.
- Review is conditional: use it for an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk judgment. Standalone review does not synthesize earlier phases.

## Compact Instructions

When compacting or handing off long conversations, preserve in priority order:

1. Architecture decisions and durable contracts.
2. Modified files and key changes.
3. Current verification status.
4. Open TODOs, recovery notes, and next gates.
5. Tool outputs only as pass/fail or the smallest required evidence.

## References

- Read `references/routing.toml` and `references/routing.md` when task routing or skill composition is ambiguous.
- Read `references/phase-boundary-decision-tree.md` when choosing how to preserve or discard context between completed coding phases.
- Read `references/memory-boundary.md` when a task touches memories, sessions, logs, generated summaries, or stale recalled facts.
- Read `references/preference-contract.md` when tuning session defaults, response style, or user preference capture.
