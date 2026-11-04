---
name: development-standards
description: "Use during design, planning, implementation, and review as the shared baseline for necessary behavior, low maintenance cost, scoped changes, compatibility, dependencies, and proportionate verification. It does not own lifecycle routing or an independent report."
---

# Development Standards

Deliver the user's outcome with the least total implementation, testing, deployment, and maintenance burden over the intended lifetime, counting the cost of delayed feedback and delivery. Decide what is necessary first: YAGNI before DRY, so an unnecessary responsibility is deleted before shared machinery is extracted, and an existing adequate capability is reused before a new framework is generalized. Durable means maintainable over the declared horizon, not maximally defensive.

This Skill is the baseline the lifecycle workflow applies from the first design choice through review. It produces no report of its own; the owning workflow keeps the response.

## The Necessity Test

Before adding or keeping a mechanism, compatibility promise, verification gate, guard, or task, name the required result or real boundary that fails without it and the evidence for that claim. When the goal stays adequately supported without it, omit it. When that cannot yet be decided, run the cheapest targeted investigation that resolves the uncertainty. This is an engineering judgment made in passing, not an ablation experiment, scorecard, or checklist.

Ask of a proposed constraint: if a capable implementer chose a different reasonable path that still met the user's goals and safety boundaries, would this constraint stop them? A constraint that would needs a concrete protected interest.

## Business Feedback Before Supporting Machinery

Build a thin real path from a relevant input to the required user-visible result, with only the setup and safeguards that this next step depends on. Checks required before delivery are prerequisites for delivery, not for starting. Protection goes before the operation that threatens protected state. When preparation grows without producing useful behavior or resolving a material uncertainty, simplify, defer, or remove that branch and return to the business path.

Spend judgment on the business rules that distinguish the product; keep simple use cases, generic support work, and local glue direct.

## Precedence

1. The user's current goals, explicit choices, and real repository and safety boundaries. Designs and plans record those decisions; a model-invented method becomes a requirement only when the user fixes it, not through inclusion or general plan approval.
2. This necessity and maintenance baseline, applied before methods, task splits, or verification are chosen.
3. The matching language, security, error-handling, architecture, testing, or domain Skill when its boundary is active.
4. The lifecycle workflow, which owns mutation, review, repair, continuation, and close.

## Goals, Discretion, And Risk

- Deliver the main goal, its necessary conditions, user-fixed technical choices, and applicable inviolable boundaries. Judge supporting code, tests, documents, and tooling by how they serve that outcome; task completion, language uniformity, line counts, and exhaustive equivalence are proxies, not outcomes.
- Add an abstraction, compatibility layer, guard, or gate for a current need. Hypothetical future consumers, hypothetical concurrency, or accidental edits are reasons to note, not to build.
- Authorized best-effort secondary outcomes may be substituted, degraded, or dropped during implementation; record the discretion and its effect. Discretion comes from the current request, approved design, or applicable project convention, and a required result keeps its oracle.
- Ordinary bugs, one failed attempt, or unknown feasibility leave a requirement supported; investigate enough to explain a tradeoff.
- Calibrate protective effort to actual exposure, expected loss, and control cost. `security-guardrails` owns security-control calibration; `infrastructure-triage` owns operational recovery calibration.
- Classify the environment from trusted project facts: a target that serves real users or holds retained data is production; otherwise treat it as rebuildable development state that may be updated, rebuilt, or replaced with fix-forward recovery. When the facts are unknown, check the smallest fact that decides it or ask one question. Remote hosts, Ansible, multi-repository work, and deploy wording are not classification facts. Unique data, credentials, shared hosts, and production commitments keep their protections in every class; an action that would exceed approved production goals, commitments, risk, or authority needs narrow authorization first, and in-scope adaptations and already-authorized deployments continue without it.
- Read [Replacement And Cutover](references/replacement-and-cutover.md) when a change replaces a running implementation, version, configuration, or service, or when a proving environment, dual-running period, or rollback path is being considered.

## Evidence Without Extra Machinery

Ordinary local development establishes consistency by reading the current change and rerunning affected checks when relevant facts change. Hashes, checksums, digest manifests, provenance chains, and immutable receipts belong to an actual functional or trust boundary: an existing cryptographic protocol, artifact integrity across a real trust boundary, or a current functional requirement. Evidence is judged by the behavior, inputs, and conditions it covers and an honest result. When simplification is authorized, inherited guards and their tests are reassessed against current needs; a historical plan, test, or implementation shows what exists, not what must continue.

## Scoped Implementation

- Implement requested behavior, approved supporting work, necessary verification, and removal of material made obsolete by this change. Adjacent refactors, unrelated reformatting, pre-existing dead code, and unrequested features stay out.
- Match established repository structure, naming, style, and ownership unless the approved change replaces them.
- Fail closed on errors that the main goal, a required contract, or a hard boundary depends on; a missing required case is an explicit failure. Required behavior has no silent fallback, guessed default, or undeclared degraded success; classified fallback or degraded mode for a secondary outcome is designed through `error-patterns` when that boundary is active.
- Prefer a clean break over dual-running old and new behavior, and remove imports, variables, helpers, configuration, and documentation the change made obsolete.
- Reuse genuinely shared behavior where it reduces maintenance; a little straightforward duplication can cost less than a new framework.

## Durability And Experiments

Choose a solution that meets current commitments and can be maintained over the declared decision horizon. A bounded, disposable reproducer or local experiment inside authorized work is a normal implementation method with no separate phase or approval, subject to the real access, side-effect, and data boundaries. Learning evidence is distinct from delivered behavior: discard unsafe experimental shortcuts before delivery, and report what a prototype exercised rather than what it implies. A shipped temporary mechanism follows [Compatibility And Migration](references/compatibility-and-migration.md).

## Maintainability

- Use names and module boundaries that reveal behavior and ownership. Split by responsibility, authority, state, or failure boundary. Create interfaces for proven variation or caller-visible contracts.
- Name repository assets for stable domain concepts or verified behavior from the first write, in files, modules, functions, tests, fixtures, scripts, configuration keys, and environment variables; plan task IDs, stage codes, and review rounds stay in plans and progress records. Genuine domain phases and protocol terms are valid names, and existing compatibility-bound names change only under a scoped migration.
- Comment why a non-obvious constraint exists. Write persisted prose for the current repository state so a reader at `HEAD` can resolve its references and verify its claims; remove review choreography, dead phase labels, and change narration once they no longer explain the current state, and keep durable decisions, still-valid rejected alternatives, and measured evidence at their owned truth location.
- Code and observed execution establish implemented behavior; documents and diagrams express intent and explain it. Synchronize affected explanations after implementation and review their meaning directly rather than turning prose, headings, or diagram contents into tested interfaces. Actual protocol strings remain code contracts when consumers depend on them.
- Update authored sources before generated projections and regenerate through the repository-owned workflow.
- Validate external input at the owned boundary. Measure before optimizing and tie performance work to an observed bottleneck or explicit objective.

## Verification And Review

- Select evidence from the changed behavior, affected consumers, and real uncertainty. A non-executable change may need only inspection, syntax, link, or structural checks; a code edit alone creates no new test obligation, and parser or existence checks cannot establish a claimed user journey.
- Use narrow tests, compilation, or reproductions when they guide implementation, and finish related edits before repeating checks that cannot inform intermediate work. The main agent coordinates broader verification and reuses applicable results; a repair invalidates affected evidence, not every prior check.
- Reproduce bugs or establish equivalent before-state evidence when practical. Classify a failed check before repairing: change-induced defects and demonstrated delivery blockers stay in scope, unrelated existing failures are reported separately, and a missing perfect reproducer leaves independent authorized work running.
- Keep a required outcome and its oracle. When a mechanism is simplified or removed, recompute the verification the remaining outcome needs; tests that only preserved the removed mechanism or an incidental detail go with it when that simplification is in scope, and evidence for real retained-state or recovery boundaries stays. Authorized secondary tradeoffs are disclosed adapted results.
- Review the approved diff, direct dependencies, and executable evidence; pre-existing or unrelated debt stays outside the current task.

## References

- [Environment Scope And Temporary Storage](references/environment-and-storage.md): environment inputs, caches, and where disposable scratch lives.
- [Local Dependency Selection](references/dependency-selection.md): choosing between existing capability, library, and custom code.
- [Compatibility And Migration](references/compatibility-and-migration.md): public or persisted contracts, retained data, and shipped temporary mechanisms.
- [Replacement And Cutover](references/replacement-and-cutover.md): the single owner of cutover, proving-environment, and rollback doctrine.
- [Quality Gates, Formatting, And CLI Conventions](references/quality-gates-and-formatting.md): repository checks, new gates, formatters, and custom command-line interfaces.
- [Toolchain Baseline](references/toolchain-baseline.md): local toolchain defaults.
- Skill descriptions, admission boundaries, and instruction layout: `skill-authoring` and its `references/instruction-content.md`.
