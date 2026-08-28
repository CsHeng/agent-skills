# Routing Reference

Use skills as the durable, agent-agnostic behavior surface. Keep AGENTS files as local constraints and thin indexes, not mandatory skill routers or long-form prompt packs.

## Contract Ownership

`references/routing.toml` is portable authoring guidance for discovery behavior, semantic trigger ownership, review evaluator selection, support routes, and composition. `contracts/lifecycle.toml` and `contracts/workflow-modes.toml` describe the collection's intended semantics; they are not a protocol that another product must consume or enforce.

## Decision Rules

- Native description matching is the default discovery path.
- An explicitly named or confidently matched skill bypasses `use-coding-skills`.
- An ambiguous multi-stage request or explicit routing question enters `use-coding-skills`, which selects the smallest matching workflow skill.
- Workflow skills own their own semantic results. Session, discipline, policy, tool, and review-component skills contribute rendering, method, policy, tooling, or evidence.
- Review enters through `review-change`; `review-design`, `review-plan`, and `review-implementation` return candidate evidence only.
- One primary skill owns the response order and conclusion. `output-styles` supplies the shared rendering baseline, while other matching skills remain semantic overlays.

## External Skill Libraries

Treat third-party workflow libraries as independent collections. Before exposing overlapping skills in one discovery surface, check for ambiguous descriptions and duplicate public IDs. For description and invocation-surface tuning, read `skills/development-standards/references/skill-authoring.md` from the repository root.

Prefer a more specific skill when one applies. Use this wrapper only for explicit routing, ambiguous multi-stage work, or session-boundary guidance.
