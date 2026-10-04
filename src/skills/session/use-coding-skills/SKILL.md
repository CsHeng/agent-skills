---
name: use-coding-skills
description: "Use when the user asks how local coding skills should be selected, when an ambiguous multi-stage request needs routing, or when session, memory, or compact-handoff boundaries need guidance. Do not load for tasks that directly match another skill."
---

# Use Coding Skills

Optional entry guidance for two conditional paths that stay separate: skill routing for an explicit routing question or ambiguous multi-stage request, and session or compact-handoff recovery. This skill is not a mandatory entry and does not replace a directly matched skill; each path is used only when its own question is active, and neither path requires the other.

## Routing Path

Use this path only for an explicit routing question or an ambiguous multi-stage request.

- Read `references/routing.md` for the selection contract and `references/routing.toml` for declarative discovery, semantic trigger cases, response composition, and support routes; this path loads routing material only.
- An explicitly named skill or confident direct workflow or policy match bypasses this skill and needs no routing lookup.
- Select the smallest matching workflow skill, keep exactly one primary response owner, and compose session, discipline, policy, tool, or review-component skills only as semantic overlays.
- Review requests enter through `review-change`; artifact-specific `review-*` skills are optional read-only evaluators, not top-level workflow owners. Review is conditional: an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Standalone review does not synthesize earlier phases.

## Session And Recovery Path

Use this path only when a task touches memories, sessions, logs, generated summaries, stale recalled facts, or recovery after compaction or handoff.

- Read `references/memory-boundary.md` for durable-truth order, memory verification, recovery evidence, and compact payload priority.
- Read `references/phase-boundary-decision-tree.md` when choosing how to carry context between completed coding phases; same-task follow-up is not a completed phase boundary.
- Read `references/preference-contract.md` for clarification, counsel versus execution, and boundaries on applying explicit user or project preferences.
- Recovery reconciles actual changes, the current goal and approval baseline, unadjudicated reports, and any still-valid executor before choosing continue or create. It does not restart skill selection, redispatch completed work, treat an unverified candidate as accepted, or invent approval.
- Persistent compaction and recovery preferences belong in harness-global instructions, not solely in a task-loaded Skill; project-owned design, plan, or approval summaries record task-specific decisions and still do not grant approval.
- Continuation depends on a real host resume path; do not claim host continuation is already supported, and do not read arbitrary historical JSONL or raw sessions to bypass host workspace and capability checks.
