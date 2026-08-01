# Routing Reference

Use skills as the durable, agent-agnostic behavior surface. Keep AGENTS files as local constraints and thin indexes, not mandatory skill routers or long-form prompt packs.

## Contract Ownership

`references/routing.toml` is the installed machine-readable source for discovery behavior, lifecycle phase-to-owner mapping, review evaluator selection, support routes, composition, and the host-wrapper boundary. `contracts/lifecycle.toml` and `contracts/workflow-modes.toml` remain the repository-wide source for kernel membership, mode classification, and phase sequences.

The generated `docs/architecture/diagrams/harness-routing-sequence.puml` combines those contracts into the expected end-to-end route. It is a review view, not an independent source of truth.

## Decision Rules

- Native description matching is the default discovery path.
- An explicitly named or confidently matched skill bypasses `use-coding-skills`.
- An ambiguous multi-stage request or explicit routing question enters `use-coding-skills`, which selects the lifecycle mode before phase implementation.
- Workflow skills alone own lifecycle transitions. Session, discipline, policy, tool, and review-component skills contribute rendering, method, policy, tooling, or evidence without advancing lifecycle state.
- Review enters through `review-change`; `review-design`, `review-plan`, and `review-implementation` return candidate evidence only.
- One primary skill owns the response order and conclusion. `output-styles` supplies the shared rendering baseline, while other matching skills remain semantic overlays.

## Host Wrapper

A user-level or host-level AGENTS file may retain personal response preferences, local runtime constraints, and a thin hint to public skill IDs when deterministic entry is necessary. It must not become a parallel routing source or copy lifecycle phases, phase ownership, repair states, review budgets, or typed exits.

## External Skill Libraries

Keep third-party workflow libraries below the local harness plane by default. Before exposing them in the default discovery surface, measure actual usage with `skill-miner`, absorb durable behavior into repo-owned skills or references, and expose only curated user-invoked entries when they do not compete with local routing, approval gates, artifact ownership, or closeout rules. For description and invocation-surface tuning, read `skills/development-standards/references/skill-authoring.md` from the repository root.

Prefer a more specific skill when one applies. Use this wrapper only for explicit routing, ambiguous multi-stage work, or session-boundary guidance.
