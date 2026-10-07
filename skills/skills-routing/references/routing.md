# Skill Selection

Use skills as the durable, agent-agnostic behavior surface. Express reusable behavior in an agent-agnostic skill rather than agent-specific rules. Keep AGENTS files as local constraints and thin indexes, not mandatory skill routers or long-form prompt packs.

## Contract Ownership

[Discovery Cases](routing.toml) supplies portable authoring guidance for discovery behavior, semantic trigger ownership, support routes, and composition. It does not define a lifecycle, mode, phase sequence, review gate, or protocol for another product to consume.

## Decision Rules

- Native description matching is the default discovery path.
- Match cases by the owner skill's frontmatter description and each case's negative boundaries; explicit-invocation cases keep positive overrides. Treat lexical hints as examples only; they are not a keyword router or a second owner map.
- An explicitly named or confidently matched skill runs directly without this skill-selection branch.
- An ambiguous multi-stage request or explicit skill-selection question uses this branch to select the smallest matching workflow skill.
- An unresolved simplification, language, tool, or oracle-method question uses its own reference in `skills-routing`; it does not require this skill-selection branch or a new primary workflow.
- The selected primary skill owns its semantic result. Session, discipline, policy, tool, and review-component skills contribute rendering, method, policy, tooling, or evidence.
- Review enters through `review-change`; `review-design`, `review-plan`, and `review-implementation` return candidate evidence only.
- Review is conditional: an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Standalone review does not synthesize earlier phases.
- One primary skill owns the response order and conclusion. `output-styles` supplies the shared rendering baseline, while other matching skills remain semantic overlays.

## External Skill Libraries

Treat third-party workflow libraries as independent collections. Before exposing overlapping skills in one discovery surface, check for ambiguous descriptions and duplicate public IDs. For description and invocation-surface tuning, read `references/skill-authoring.md` in `development-standards`.

Prefer a more specific skill when one applies. Use this branch only for an explicit skill-selection question or ambiguous multi-stage work.
