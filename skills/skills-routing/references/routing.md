# Skill Selection

Use skills as the durable, agent-agnostic behavior surface. Express reusable behavior in an agent-agnostic skill rather than agent-specific rules. Keep AGENTS files as local constraints and thin indexes, not mandatory skill routers or long-form prompt packs.

## Contract Ownership

[Scope Contracts](routing.toml) groups neighboring skills into clusters. Each cluster names its members and the question that separates them, and each handoff names a situation, its single receiver, and the candidates that receiver replaces. A receiver or member is a public skill ID, `<id>:<reference>` for a method reference inside that skill, or `none` when general instructions and repository rules suffice without a skill from this collection; a separately installed skill whose description matches still applies. The registry does not define a lifecycle, mode, phase sequence, review gate, or protocol for another product to consume.

## Decision Rules

- Native description matching is the default discovery path.
- Match the request against skill descriptions first. When neighboring skills both seem to fit, answer their cluster's question and follow a handoff whose situation matches; a handoff to `none` means no skill from this collection is needed. A skill marked explicit loads only when the user names it or explicitly asks for its workflow.
- An explicitly named or confidently matched skill runs directly without this skill-selection branch.
- An ambiguous multi-stage request or explicit skill-selection question uses this branch to select the smallest matching workflow skill.
- An unresolved simplification, language, tool, or oracle-method question uses its own reference in `skills-routing`; it does not require this skill-selection branch or a new primary workflow.
- The selected primary skill owns its semantic result. Session, discipline, policy, tool, and review-component skills contribute rendering, method, policy, tooling, or evidence.
- Review enters through `review-change`; `review-design`, `review-plan`, and `review-implementation` return candidate evidence only.
- Review is conditional: an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Standalone review does not synthesize earlier phases.
- One primary skill owns the response order and conclusion. `output-styles` supplies the shared rendering baseline, while other matching skills remain semantic overlays.

## External Skill Libraries

Treat third-party workflow libraries as independent collections. Before exposing overlapping skills in one discovery surface, check for ambiguous descriptions and duplicate public IDs. For description and invocation-surface tuning, use `skill-authoring`.

Prefer a more specific skill when one applies. Use this branch only for an explicit skill-selection question or ambiguous multi-stage work.
