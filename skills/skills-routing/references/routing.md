# Skill Selection

Skills are the durable, agent-agnostic behavior surface. Reusable behavior lives in a skill rather than in agent-specific rules; AGENTS files stay local constraints and thin indexes.

## Contract Ownership

[Scope Contracts](routing.toml) groups neighboring skills into clusters. Each cluster names its members and the question that separates them, and each handoff names a situation, its single receiver, and the candidates that receiver replaces. A receiver is a public skill ID, `<id>:<reference>` for a method reference inside that skill, or `none` when general instructions and repository rules suffice; a separately installed skill whose description matches still applies. The registry defines no lifecycle, phase sequence, review gate, or protocol for another product.

## Decision Rules

- Match the request against skill descriptions first. When neighboring skills both seem to fit, answer their cluster's question and follow the matching handoff.
- A skill marked explicit loads only when the user names it or asks for its workflow.
- An ambiguous multi-stage request or explicit skill-selection question selects the smallest matching workflow skill. An unresolved simplification, language, tool, or oracle question uses its own reference here without a new primary workflow.
- The selected primary skill owns its semantic result; session, discipline, policy, tool, and review-component skills contribute rendering, method, policy, tooling, or evidence. Review enters through `review-change`, whose conditions it owns; `review-design`, `review-plan`, and `review-implementation` return candidate evidence only.

## External Skill Libraries

Treat third-party workflow libraries as independent collections. Before exposing overlapping skills in one discovery surface, check for ambiguous descriptions and duplicate public IDs; tune descriptions and invocation surfaces with `skill-authoring`.
