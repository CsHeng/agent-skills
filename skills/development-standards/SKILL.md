---
name: development-standards
description: "Use as a conditional cross-language implementation overlay for smallest durable changes, request-scoped edits, compatibility, dependencies, temporary mechanisms, maintainability, and repository-owned quality gates. It does not own lifecycle routing or an independent report."
---

# Development Standards

Choose the smallest durable implementation that satisfies the current approved requirements, contracts, and declared decision horizon. Durable does not mean speculative; do not buy flexibility, abstraction, compatibility, or operational surface without a current owner and need.

This is a conditional implementation overlay. Do not select it as the primary owner for project analysis, design, planning, execution, or review.

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
- Fail closed on required errors. Do not add silent fallback, guessed defaults, or degraded success unless the approved design or a current caller contract names that behavior. A missing case is an explicit failure, not a recovery.
- Do not swallow errors or keep a legacy path "just in case". Prefer a clean break over dual-running old and new behavior. Route classified fallback or degraded mode through `error-patterns` when that boundary is active.
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

- Understand the approved requirement and relevant current code before choosing a solution. Search for a suitable repository-owned helper, type, or pattern; then standard-library and native-platform capabilities; then installed dependencies; only then consider a new implementation or dependency under the lifecycle-cost rules below.
- Treat this as a candidate-search order, not an unconditional solution ranking. Stop at a candidate that satisfies the owned behavior, compatibility, trust, error, deployment, and maintenance constraints. Do not reuse a similar-looking helper with different semantics or replace an approved dependency merely because a standard-library alternative exists; repository conventions and contracts take precedence over ladder position.
- Prefer an established, actively maintained library for non-trivial or security-sensitive capabilities when its total lifecycle cost is lower than a custom implementation.
- Compare correctness risk, maintenance activity, security response, transitive surface, update burden, license, runtime fit, and ecosystem ownership.
- Do not add a dependency for small transparent local logic whose implementation and verification are cheaper than the dependency lifecycle.
- Do not build custom cryptography, authentication protocols, parsers for complex standards, or concurrency primitives when a suitable maintained implementation exists.

## Maintainability

- Use names and module boundaries that reveal behavior and ownership.
- Keep functions and modules cohesive; split by responsibility, authority, state, or failure boundary rather than arbitrary line limits.
- Create interfaces for proven variation or caller-visible contracts, not hypothetical substitution.
- Comment why a non-obvious constraint exists; do not narrate obvious code, intermediate attempts, or session history. Apply the same rule to skill prose and `AGENTS.md`.
- Write persisted prose for the current repository state. A reader at current HEAD must be able to resolve its internal references and verify its claims without an authoring session, review thread, temporary branch, or uncommitted draft.
- Preserve complete propositions when editing comments, docstrings, prompts, diagnostics, help text, examples, configuration comments, and other durable prose: retain the actor, action, conditions, order, modality, negative guarantees, exceptions, ownership transfers, side effects, failure modes, and consequences that affect behavior.
- Remove review choreography, dead phase labels, reviewer arguments, and temporary change narration once they no longer explain the current state. Preserve exact durable issues, decisions, still-valid rejected alternatives, standards, and measured evidence at their repository-owned truth location.
- Treat model-visible and user-visible strings as behavior when wording affects routing, interpretation, diagnosis, safety, or compatibility. Protect such changes with the narrowest owned snapshot, contract, or runtime oracle; do not normalize prose repository-wide without an approved scope.
- Update authored sources before generated projections and regenerate through the repository-owned workflow.
- Validate external input at the owned boundary and handle failures that can occur under the declared runtime contract.
- Measure before optimizing and keep performance work tied to an observed bottleneck or explicit objective.

## Repository-Owned Quality Gates

- Follow quality gates already owned by the target repository, approved plan, CI contract, or release policy before introducing a new metric.
- Select a new lint, complexity, duplication, coverage, or debt gate only when it protects a named boundary, has a baseline, an accountable owner, a failure response, and an adoption or migration path.
- Do not impose universal numeric thresholds across repositories or languages. A metric is evidence for a goal, not the goal itself.
- Let `testing-strategy` own executable test evidence, suite boundaries, fixtures, and CI lanes. Let the matching language guideline own concrete linter, formatter, type-checker, and test-runner configuration.
- Treat trends and changed-code gates as preferable to arbitrary repository-wide targets when legacy baselines cannot satisfy a justified policy immediately.
- Record technical debt only when its impact, scope, owner, priority, and retirement evidence are actionable; do not create dashboards or recurring process by default.

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
