---
name: development-standards
description: "Use for cross-language implementation policy: the smallest durable change, request-scoped edits, compatibility and migration decisions, dependency selection, temporary mechanisms, maintainability, custom CLI conventions, and implementation review expectations."
---

# Development Standards

Choose the smallest durable implementation that satisfies the current approved requirements, contracts, and declared decision horizon. Durable does not mean speculative; do not buy flexibility, abstraction, compatibility, or operational surface without a current owner and need.

## Precedence And Composition

1. Follow repository-local policy and the approved design or plan first.
2. Apply this skill as the cross-language implementation baseline.
3. Compose the matching language, security, error-handling, architecture, testing, or domain skill only when its boundary is active.
4. Let the lifecycle workflow own mutation, review, repair, continuation, and close decisions.

## Scoped Implementation

- Implement only requested behavior and approved supporting work.
- Require every changed line to trace to the task slice, its executable oracle, or an orphan created by the same change.
- Do not refactor adjacent code, reformat unrelated files, remove pre-existing dead code, or add features that were not requested.
- Match established repository structure, naming, style, and ownership unless the approved change explicitly replaces them.
- Avoid single-use abstractions, speculative configuration, hypothetical extension points, and defensive branches for impossible states.
- Remove imports, variables, helpers, configuration, and documentation made obsolete by the current change.

## Durability And Temporary Mechanisms

- Prefer the smallest solution that can be maintained for the declared decision horizon without a known rewrite.
- A prototype or temporary mechanism is valid only when experimentation or staged migration is an approved goal.
- Give every temporary mechanism an owner, observable outcome, exit condition, and removal trigger.
- Do not call a known throwaway stopgap a durable implementation. Route a changed architecture boundary back to `design-change`.

## Compatibility And Migration

- Do not add or preserve compatibility behavior unless a current public or persisted contract, interoperability requirement, or approved migration policy requires it.
- Distinguish internal implementation freedom from caller-visible APIs, stored data, wire formats, automation entry points, and generated compatibility surfaces.
- When compatibility is required, name its owner, supported versions, evidence, retirement condition, and migration path.
- Remove obsolete compatibility paths when their approved retirement condition is met; update affected producers, consumers, tests, generated surfaces, and stable docs together.

## Dependency Selection

- Prefer an established, actively maintained library for non-trivial or security-sensitive capabilities when its total lifecycle cost is lower than a custom implementation.
- Compare correctness risk, maintenance activity, security response, transitive surface, update burden, license, runtime fit, and ecosystem ownership.
- Do not add a dependency for small transparent local logic whose implementation and verification are cheaper than the dependency lifecycle.
- Do not build custom cryptography, authentication protocols, parsers for complex standards, or concurrency primitives when a suitable maintained implementation exists.

## Maintainability

- Use names and module boundaries that reveal behavior and ownership.
- Keep functions and modules cohesive; split by responsibility, authority, state, or failure boundary rather than arbitrary line limits.
- Create interfaces for proven variation or caller-visible contracts, not hypothetical substitution.
- Comment why a non-obvious constraint exists; do not narrate obvious code.
- Validate external input at the owned boundary and handle failures that can occur under the declared runtime contract.
- Measure before optimizing and keep performance work tied to an observed bottleneck or explicit objective.

## Custom CLI Conventions

- Follow repository-local command conventions first.
- Prefer descriptive long options for custom scripts and avoid positional write or delete behavior.
- Keep third-party CLI invocations in their native syntax.
- Provide actionable validation errors and stable non-zero exits for invalid input.

## Verification And Review

- Define success criteria before implementation and select the smallest realistic oracle that proves the changed boundary.
- Reproduce bugs or establish equivalent before-state evidence when practical, then verify the narrow change and declared broader scope.
- Do not weaken tests, schemas, compatibility checks, security checks, or other oracles merely to make implementation pass.
- Review the approved diff, direct dependencies, and executable evidence. Pre-existing or unrelated debt does not expand the current task.

## Progressive Disclosure

- Local toolchain baseline: `references/toolchain-baseline.md`
- Skill descriptions, routers, and agent-agnostic workflow surfaces: `references/skill-authoring.md`

## Completion Check

- Current approved requirements and contracts are satisfied.
- The implementation is the smallest durable option for the declared horizon.
- Changed lines are request-traceable and unrelated work is untouched.
- Compatibility and dependencies have current owners and evidence where applicable.
- Temporary mechanisms have explicit exit conditions.
- Declared verification passes without weakening the oracle.
