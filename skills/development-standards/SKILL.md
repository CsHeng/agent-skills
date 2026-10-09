---
name: development-standards
description: "Use during design, planning, implementation, and review as the shared baseline for necessary behavior, low maintenance cost, scoped changes, compatibility, dependencies, and proportionate verification. It does not own lifecycle routing or an independent report."
---

# Development Standards

Deliver the user's outcome with the least total implementation, testing, deployment, and maintenance burden over the intended lifetime. Start by deciding what is necessary. YAGNI comes before DRY: delete an unnecessary responsibility before extracting shared machinery, and reuse an existing adequate capability rather than generalizing a new framework. Durable does not mean speculative or maximally defensive.

Across languages, prefer suitable mature libraries and platform capabilities over building general-purpose machinery. Spend custom code on the business rules and necessary integration. Apparent simplicity in today's inputs is not evidence that a homegrown utility is cheaper to own.

Apply this baseline from the first design choice through planning, implementation, and review. Before adding or retaining a mechanism, compatibility promise, or verification gate, consider removing it. Name the required result or actual boundary that would fail without it, and the evidence for that claim. If the goal remains adequately supported without the mechanism, omit it. If that cannot yet be decided, use the cheapest targeted investigation that resolves the material uncertainty. This is a counterfactual engineering judgment, not an obligatory ablation experiment, scorecard, or checklist, and not a mandatory invocation of the simplification method in `skills-routing`. Preventing unnecessary work is preferable to building it and removing it later.

Keep the appropriate workflow as the primary owner; this overlay produces no independent report. Apply detailed implementation sections only when their boundary is relevant.

## Precedence And Composition

1. Follow the user's current goals, explicit choices, and real repository and safety boundaries. Designs and plans record those decisions; model-invented methods do not become user requirements merely through inclusion or general plan approval.
2. Apply this skill's necessity and maintenance baseline before choosing methods, breaking work into tasks, or defining verification.
3. Compose the matching language, security, error-handling, architecture, testing, or domain skill only when its boundary is active.
4. Let the lifecycle workflow own mutation, review, repair, continuation, and close decisions.

## Goals, Discretion, And Risk

- Deliver the main goal, its necessary conditions, user-fixed technical choices, and applicable inviolable boundaries.
- Judge supporting code, tests, documents, and tooling by how they serve that outcome. Task completion, language uniformity, line counts, and exhaustive equivalence are not substitute outcomes.
- Prefer direct behavior and existing capabilities. Add an abstraction, compatibility layer, guard, or gate only for a current need; hypothetical future consumers, concurrency, or accidental edits are not sufficient reasons.
- Authorized best-effort secondary outcomes may be substituted, degraded, or dropped during implementation. Record the discretion and its effect. The design does not need to enumerate every feature that might fail.
- Discretion comes from the current request, approved design, or applicable project convention. Do not grant it after the fact to pass review, silently weaken a required outcome, or drop a named secondary capability that the main goal actually depends on.
- Ordinary bugs, one failed attempt, or unknown feasibility do not by themselves make a requirement unsupported. Investigate enough to explain a tradeoff; do not exhaust every alternative.
- Calibrate protective effort to actual exposure, expected loss, and control cost; `security-guardrails` owns security-control calibration and `infrastructure-triage` owns operational recovery calibration. Do not require a scoring system or a zero-risk proof.
- Environment wording alone — remote hosts, multi-repository work, Ansible, deploy language — does not make the target production; use trusted project facts and the minimum check needed when the environment is unclear. Authorized rebuildable development state may be updated, rebuilt, or replaced with fix-forward recovery; protect unique data, credentials, shared hosts, and production commitments, and get narrow authorization before an action would exceed approved production goals, commitments, risk, or authority. In-scope adaptations and already-authorized deployments continue without renewed approval.

## Evidence Without Extra Machinery

- Ordinary local development does not need hashes, checksums, digest manifests, provenance chains, or immutable receipts to establish consistency. Do not introduce them into implementation, tests, fixtures, designs, plans, or handoffs unless explicitly requested or necessary for an actual functional or trust boundary.
- Evidence needs relevant behavior, inputs, conditions, and an honest result. Read the current change and rerun affected checks when those facts change; do not require byte identity or replace hashes with mandatory revision bookkeeping.
- Existing cryptographic protocols, artifact integrity across a real trust boundary, and other current functional requirements can need digests. Their presence elsewhere, a mutable file, or a desire for stronger-looking proof does not justify another mechanism.
- When simplification is authorized, reassess inherited guards and their tests against current needs. A historical plan, test, or implementation is evidence of what exists, not proof it must continue to exist.

## Scoped Implementation

- Implement only requested behavior and approved supporting work.
- Keep changes tied to the requested outcome, necessary verification, and obsolete material created by this change; do not create a line-by-line traceability ledger.
- Do not refactor adjacent code, reformat unrelated files, remove pre-existing dead code, or add features that were not requested.
- Match established repository structure, naming, style, and ownership unless the approved change explicitly replaces them.
- Avoid single-use abstractions, speculative configuration, hypothetical extension points, and defensive branches for impossible states.
- Fail closed on errors that the main goal, a required contract, or a hard boundary depends on. A missing required case is an explicit failure, not a recovery.
- Do not add silent fallback, guessed defaults, or undeclared degraded success for required behavior. Authorized best-effort secondary degradation does not need every fallback named in the design.
- Do not swallow errors or keep a legacy path "just in case". Prefer a clean break over dual-running old and new behavior. Route classified fallback or degraded mode through `error-patterns` when that boundary is active.
- Remove imports, variables, helpers, configuration, and documentation made obsolete by the current change.
- Reuse genuinely shared behavior where it reduces maintenance. A little straightforward duplication can cost less than a new framework; do not generalize unnecessary guards or accidental compatibility merely to satisfy DRY.

## Durability And Temporary Mechanisms

- Prefer the smallest solution that can be maintained for the declared decision horizon without a known rewrite.
- A prototype or temporary mechanism is valid only when experimentation or staged migration is an approved goal.
- Give every temporary mechanism an owner, observable outcome, exit condition, and removal trigger.
- Do not call a known throwaway stopgap a durable implementation. Route a changed architecture boundary back to `design-change`.

## Compatibility And Migration

- Do not add or preserve compatibility behavior unless a current public or persisted contract, interoperability requirement, approved migration policy, or retained-state need requires it.
- Preserve required consumer behavior rather than every incidental property of the previous implementation. A library's default help wrapping, numeric representation, object identity, or undocumented parsing quirk is not automatically a public promise. Establish actual consumers and requirements before reproducing it in another language.
- Authorized disposable development state may rebuild or replace rather than preserve in-place compatibility.
- Retained existing data still needs corresponding migration evidence even when the runtime may be rebuilt.
- Distinguish internal implementation freedom from caller-visible APIs, stored data, wire formats, automation entry points, and generated compatibility surfaces.
- When compatibility is required, name its owner, supported versions, evidence, retirement condition, and migration path.
- Remove obsolete compatibility paths when their approved retirement condition is met; update affected producers, consumers, tests, generated surfaces, and stable docs together.

## Local Dependency Selection

This Skill owns the local implementation dependency decision, not the material open design choice or the architecture-boundary comparison; apply the shared reuse principle to the smallest owned behavior.

- Understand the business requirement, actual consumers and relevant current code before choosing a solution. Look for suitable project capabilities, standard-library or platform APIs, and mature ecosystem libraries before writing general-purpose code. A repository helper is a candidate, not a reason to preserve an unnecessary homegrown implementation.
- Prefer a suitable maintained library for a capability it already owns. "The current case is simple," fewer imports, avoiding all dependencies, familiarity or a shorter first patch do not by themselves justify recreating that capability. Apply this to ordinary development and authorized repair as well as migrations, across languages.
- Judge suitability by required behavior, compatibility, runtime and delivery fit, maintenance and security response, transitive surface, licensing and update cost. Choose an adequate existing capability without turning ordinary selection into an exhaustive dependency survey or scorecard. Do not replace an approved suitable library merely because a standard-library alternative exists.
- Keep small domain rules and necessary adapters local when a library does not own them. Implement a general mechanism yourself only when available capabilities fail a concrete requirement or impose a demonstrated disproportionate burden; keep the scope narrow. Neither line count nor a hypothetical dependency risk establishes that exception, and this guidance does not require a package for every trivial expression.
- Runtime and language constraints still apply. If the appropriate ecosystem library changes the runtime or delivery boundary, resolve that choice through language selection rather than silently adding an environment or rebuilding the library to preserve an earlier language assignment.
- In an authorized refactor, compare custom file/path utilities, parsers, transport, serialization and other support code with the capabilities now available. Replace redundant mechanics and retire their unsupported compatibility tests together; preserve domain tests, real consumer contracts and data protections. Renaming a helper or putting the same custom implementation behind a library-shaped interface does not reduce its maintenance responsibility.
- Do not build custom cryptography, authentication protocols, parsers for complex standards, or concurrency primitives when a suitable maintained implementation exists.
- When the user or approved design specifies a library for a goal, that library is a boundary. Choose glue, helpers, and local algorithms; do not swap the specified library from preference, and do not require the user to design each glue function.

## Maintainability

- Use names and module boundaries that reveal behavior and ownership.
- Keep functions and modules cohesive; split by responsibility, authority, state, or failure boundary rather than arbitrary line limits.
- Create interfaces for proven variation or caller-visible contracts, not hypothetical substitution.
- Comment why a non-obvious constraint exists; do not narrate obvious code, intermediate attempts, or session history. Apply the same rule to skill prose and `AGENTS.md`.
- Write persisted prose for the current repository state. A reader at current HEAD must be able to resolve its internal references and verify its claims without an authoring session, review thread, temporary branch, or uncommitted draft.
- Preserve complete propositions when editing comments, docstrings, prompts, diagnostics, help text, examples, configuration comments, and other durable prose: retain the actor, action, conditions, order, modality, negative guarantees, exceptions, ownership transfers, side effects, failure modes, and consequences that affect behavior.
- Remove review choreography, dead phase labels, reviewer arguments, and temporary change narration once they no longer explain the current state. Preserve exact durable issues, decisions, still-valid rejected alternatives, standards, and measured evidence at their repository-owned truth location.
- Code and observed execution establish implemented behavior; documents and diagrams express intent and explain it. Synchronize affected explanations after implementation. Review their meaning directly; do not turn prose, headings, diagram contents, or historical versions into tested interfaces. Actual protocol strings remain code contracts when consumers depend on them.
- Update authored sources before generated projections and regenerate through the repository-owned workflow.
- Validate external input at the owned boundary and handle failures that can occur under the declared runtime contract.
- Measure before optimizing and keep performance work tied to an observed bottleneck or explicit objective.

## Plan-Independent Naming

- Name repository implementation assets for stable domain concepts, responsibilities, or verified behavior from the first write, not the current plan's task IDs, stage codes, or review rounds. This includes files, directories, modules, functions, types, variables, tests, fixtures, helper scripts, build targets, configuration keys, and environment variables; calling repository code temporary does not exempt it.
- Keep plan identifiers in plans, progress records, and acceptance mappings rather than implementation names. One-shot experiments outside the repository may use them, but rename plan-derived implementation identifiers before promoting that code into the repository.
- Ask whether a name would still explain its responsibility if the current plan disappeared or its tasks were reordered. For example, prefer `autofallback_recovery_test.go` and `servingRecoveryBudget` over `g0_recovery_test.go` and `g0ServingRecoveryBudget`.
- Judge meaning, not spelling: genuine domain phases and protocol terms are valid names even when they resemble plan labels. Preserve existing compatibility-bound names unless a scoped migration is authorized; identify the compatibility reason rather than silently renaming an interface.
- Apply this rule to newly introduced or changed implementation names within the approved scope. It does not authorize repository-wide cleanup of historical names or a lexical ban on strings such as `g0` or `phase`.

## Temporary Storage

- Treat `TMPDIR` as the standard temporary-directory root consumed by `mktemp` and supporting tools, not as a new cache or artifact protocol. A development environment may set it per repository group to an absolute disk-backed path such as `$HOME/tmp/<group>` through mise; without a declared root, agent-owned ad hoc scratch falls back to `$HOME/tmp`. Create the root before use and use unique task directories beneath it.
- Honor explicit repository output locations and language/tool-specific directory settings. Python environments, Go build and module caches, and other reusable caches retain their own semantics; setting `TMPDIR` does not relocate them all. Setting only a final build output path does not relocate intermediate files either.
- Keep large clones, downloads, extraction, build intermediates, and test data on verified disk-backed storage rather than assuming a system temporary directory is safe: `/tmp` may be tmpfs and consume RAM. Portable project tools should respect `TMPDIR` through their native temporary-file API and may retain the platform default when it is unset; do not hardcode a developer's home path into runtime code or rewrite legitimate target-system `/tmp` paths.
- Keep task scratch, reusable caches, and retained evidence distinguishable beneath their declared roots. Clean only owned inactive scratch; do not delete a shared root or another running task's files. Environment changes affect newly launched consumers, not existing processes, and controller settings do not automatically propagate through SSH, sudo, containers, or services.

## Repository-Owned Quality Gates

- Run applicable repository checks. In an authorized gate or suite simplification, assess whether each check protects required behavior rather than treating its existence as a permanent requirement.
- Select a new lint, complexity, duplication, coverage, or debt gate only when it protects a named boundary, has a baseline, an accountable owner, a failure response, and an adoption or migration path.
- Do not impose universal numeric thresholds across repositories or languages. A metric is evidence for a goal, not the goal itself.
- Let `testing-strategy` own executable test evidence, suite boundaries, fixtures, and CI lanes. Let the matching language guideline own concrete linter, formatter, type-checker, and test-runner configuration.
- Treat trends and changed-code gates as preferable to arbitrary repository-wide targets when legacy baselines cannot satisfy a justified policy immediately.
- Record technical debt only when its impact, scope, owner, priority, and retirement evidence are actionable; do not create dashboards or recurring process by default.

## Formatting

- Follow the target repository's owned formatter and configuration. Do not invent numeric column limits or a conflicting pure-format lint gate.
- Run that formatter on authorized changed files before final read-only checks.
- Do not rewrite strings, comments, or behavior to satisfy pure line-length style.
- Do not silently disable an existing explicit project hard rule when the formatter cannot satisfy it; surface a configuration decision once.
- Markdown no-hard-wrap policy stays with `organize-docs`. Do not hard-wrap Markdown prose to a column width here.

## Custom CLI Conventions

- Follow repository-local command conventions first.
- Prefer descriptive long options for custom scripts and avoid positional write or delete behavior.
- Keep third-party CLI invocations in their native syntax.
- Provide actionable validation errors and stable non-zero exits for invalid input.

## Verification And Review

- Define success criteria before implementation and select the smallest realistic oracle that proves the changed user-visible boundary and hard constraints.
- Parser, existence, or golden checks do not replace user-goal scenarios that the change claims to satisfy.
- Reproduce bugs or establish equivalent before-state evidence when practical, then verify the narrow change and declared broader scope. A missing perfect reproducer does not freeze unrelated authorized work.
- Do not weaken a required outcome to make implementation pass. When a mechanism is simplified or removed, recompute the verification the remaining outcome needs; an old failure matrix does not transfer automatically. Correct or remove tests that only preserve an unnecessary mechanism or incidental detail when that simplification is in scope; keep evidence for the actual required behavior, including retained-state or recovery evidence when that boundary is real. Authorized secondary tradeoffs are disclosed adapted results, not hidden failures.
- Review the approved diff, direct dependencies, and executable evidence. Pre-existing or unrelated debt does not expand the current task.

## Progressive Disclosure

- Local toolchain baseline: `references/toolchain-baseline.md`
- Skill descriptions, routers, and agent-agnostic workflow surfaces: `references/skill-authoring.md`

## Completion Check

- Current approved requirements, main goal, and required contracts are satisfied.
- Authorized best-effort secondary tradeoffs are disclosed, with evidence, rather than silent.
- The implementation is the smallest durable option for the declared horizon.
- Changed lines are request-traceable and unrelated work is untouched.
- Compatibility and dependencies have current owners and evidence where applicable.
- Temporary mechanisms have explicit exit conditions.
- Declared verification passes without weakening a required oracle.
