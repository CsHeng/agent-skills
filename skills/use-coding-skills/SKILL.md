---
name: use-coding-skills
description: "Use when the user asks how local coding skills should be selected, when an ambiguous multi-stage coding request needs explicit routing, when host-wrapper boundaries need clarification, or when session-boundary, memory-boundary, or compact handoff guidance is required. Do not load as a mandatory bootstrap for unrelated work or tasks that directly match a workflow or policy skill."
---

# Use Coding Skills

Optional routing and session-boundary guidance for local coding work. Keep this skill small: it assists ambiguous selection and handoff without becoming a mandatory entry or a replacement for directly matched skills.

## Session Contract

- Treat repository-owned docs, code, scripts, tests, and skills as durable truth.
- Treat agent memories, sessions, logs, caches, and generated summaries as recall or staging evidence.
- Keep scope bound to the named repo, runtime surface, host, or workflow.
- Treat explicit read-only wording literally.
- Match response language to user input language unless file conventions require otherwise.
- Prefer current local evidence and live runtime checks over stale memory when verification is cheap.
- Verify current external facts before relying on versions, project support, APIs, protocols, pricing, laws, or ecosystem state.
- Do not write agent-specific rules when a skill can express the behavior in an agent-agnostic way.

## Default Routing

Use these rules only after this skill has matched an explicit routing or ambiguous multi-stage request:

- Read `references/routing.toml` as the machine-readable discovery, semantic trigger-case, phase-to-owner, review-evaluator, support-route, composition, and host-wrapper contract.
- Match cases by their positive and negative semantic boundaries. Treat lexical hints as examples only; they are not a keyword router or a second owner map.
- Let an explicitly named skill or confident direct workflow or policy match bypass this router.
- Route ambiguous multi-stage work through this skill, then select the lifecycle mode before invoking a phase owner.
- Keep exactly one primary response or lifecycle owner. Compose matching session, discipline, policy, tool, or review-component skills only as lower-plane overlays.
- Route design, planning, execution, review, truth sync, and close through the workflow owners declared by the contract. Review requests enter through `review-change`; artifact-specific `review-*` skills are evaluators, not top-level gates.
- Keep host-level AGENTS files limited to user preferences, runtime constraints, and thin public-skill entry hints. Do not duplicate the phase graph, repair loop, review budgets, or typed exits outside the repo-owned contract.

## Compact Instructions

When compacting or handing off long conversations, preserve in priority order:

1. Architecture decisions and durable contracts.
2. Modified files and key changes.
3. Current verification status.
4. Open TODOs, recovery notes, and next gates.
5. Tool outputs only as pass/fail or the smallest required evidence.

## References

- Read `references/routing.toml` and `references/routing.md` when task routing, skill selection, lifecycle phase ownership, or host-wrapper scope is ambiguous.
- Read `references/phase-boundary-decision-tree.md` when choosing how to preserve or discard context between completed coding phases.
- Read `references/memory-boundary.md` when a task touches memories, sessions, logs, generated summaries, or stale recalled facts.
- Read `references/preference-contract.md` when tuning session defaults, response style, or user preference capture.
