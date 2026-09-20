---
name: testing-strategy
description: "Design or revise verification coverage, suite placement, fixtures, isolation, and execution lanes for an established oracle. Use for test-strategy decisions or suite audits; not merely to run existing checks or add routine tests under a settled strategy."
---

# Testing Strategy

## Purpose

Turn a selected executable oracle into the smallest concrete verification set that protects the intended boundary.

Use `executable-oracle-architecture-selector` when the oracle method or protected behavior still needs a decision, not merely because the task involves architecture, planning, or TDD. Consume an established strategy directly. Running known checks or adding a routine regression test under that strategy does not require reopening strategy selection. For multi-client API contract ownership and layer decomposition decisions, use `api-contract-strategy`.

Do not measure maturity by test count or impose universal coverage percentages. Do not define effort by a fixed number of tests or hypotheses.

## Strategy Mapping

When this Skill is actively selecting or auditing a strategy, record the relevant mapping below. Routine tests under an established strategy consume it directly; they do not need a new strategy artifact:

```text
boundary -> oracle -> fixture/environment -> owning suite -> CI/release lane -> diagnosis owner
```

1. Name the behavior or system boundary and its owner.
2. Carry forward the selected executable oracle and record the failure class it detects.
3. Choose the smallest realistic fixture and environment.
4. Place the check in the suite that owns diagnosis.
5. Assign fast, merge, release, or runtime execution.
6. Define what a failure means and who repairs it.

A missing verification layer is not repaired by duplicating lower-value unit tests.

## Classification Contract

When classifying or auditing existing checks, read [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md).

Record orthogonal fields rather than forcing one overloaded test label:

- protected boundary and observable invariant
- primary evidence class
- real dependency and authority scope
- oracle type and independent source
- fast, merge, release, or runtime lane
- cross-cutting quality tags when relevant
- owning suite and failure diagnosis owner

Choose the primary evidence class from the highest real boundary exercised, not the framework, filename, directory, mock library, or test length. Evidence class and execution lane are separate decisions; security, compatibility, performance, and resilience are usually cross-cutting tags rather than universal hierarchy levels.

Use the smallest realistic boundary that can prove the invariant. Add higher-boundary evidence only when it proves behavior unavailable below, such as real serialization, persistence, provider interaction, a multi-operation workflow, UI behavior, or deployed conditions.

Test and file length are diagnostic signals, not verdicts. Split when one suite mixes protected boundaries, fixtures, authority levels, execution lanes, or diagnosis owners, or when failures cannot be localized. Keep cohesive table-driven matrices, parser cases, and reviewed golden contracts when their oracle remains independent and readable.

## Verification Placement

| Boundary | Typical oracle | Owning suite |
| --- | --- | --- |
| Function or module behavior | Examples, tables, properties | Unit or component |
| Internal component collaboration | Examples, fakes, real local dependency | Component or integration |
| Public wire shape | Schema and compatibility | Contract |
| Provider implementation | Real protocol request/response | Provider integration |
| Consumer assumptions | Mapping, serialization, adapter fixtures | Consumer adapter |
| Cross-operation business behavior | Scenarios | Workflow |
| Browser/app-owned behavior | User journey | UI / E2E |
| Load-sensitive behavior | Workload and threshold | Performance |
| Production-only behavior | SLO, canary, synthetic probe | Runtime |

For API systems, keep schema compatibility and semantic compatibility separate. Structural diffing cannot prove units, retry behavior, consistency, migration semantics, or status meaning.

## Coverage Policy

Treat line, branch, mutation, and scenario coverage as diagnostic evidence, not universal goals.

Add a numeric gate only when:

- it protects a named boundary or regression class
- the repository has a stable baseline
- the threshold has an owner and review rationale
- failure diagnosis is actionable
- raising the threshold will not incentivize low-semantic tests

Critical paths may justify stronger gates than glue or generated code. Generated internals usually need version pinning, deterministic generation, compilation, and boundary fixtures rather than handwritten coverage.

## Red-Green Verification

- For behavior changes and bug fixes, write or identify a failing test or narrow reproducer before implementation when a correct seam exists.
- Confirm the oracle fails for the expected reason, not a typo or environment error.
- A missing perfect agent-runnable reproducer does not freeze other authorized work; use the tightest available equivalent evidence and keep unblocked work moving.
- Implement the smallest change that makes the reproducer pass.
- Rerun the narrow oracle and declared verification scope before claiming success.
- For config-only changes, prefer parser, schema, or real-consumer validation.
- For docs-only, generated, or exploratory changes, record the fitting lint, build, generation check, or manual evidence.
- When the user asks for TDD, test-first work, red-green-refactor, or vertical slices, read [TDD Vertical Slices](references/tdd-vertical-slices.md).

## Documentation And Markdown Verification

Match documentation checks to the property that can actually fail:

- Human-authored prose: use review plus Markdown/prose linting, link checking, and documentation builds where applicable.
- Frontmatter, schemas, command identifiers, paths, and other machine-readable fields embedded in Markdown: parse and validate the structured field or stable identifier.
- Executable examples: compile or run the example through the real interface.
- Generated documentation: regenerate it and compare the owned source and generated surface.
- Prompt or instruction Markdown: test observable consumer behavior with an evaluation or integration scenario when that evidence is worth its cost; machine consumption alone does not make prose a unit-test interface.

When efficacy measurement is requested or a bounded risk judgment justifies it, use [Agent Skill Evaluation](references/agent-skill-evaluation.md) with the necessary execution authority and budget. Ordinary Skill editing does not require a live experiment, and maintenance checks do not establish behavioral or economic gains.

For offline review of goal, risk, and discretion behavior, read [Goal And Risk Cases](references/goal-and-risk-cases.md). Those cases are optional comparison material, not unit tests, CI gates, or required live experiments.

PROHIBITED: Add unit or contract tests that assert exact natural-language sentences, keyword collections, prose headings, or their absence in Markdown solely to freeze intended meaning.

PROHIBITED: Duplicate a Markdown policy sentence or rule list in test code.

REQUIRED: If a documentation rule must be machine-enforced, place the enforceable contract in a structured source of truth and generate the human-readable projection, or test the consuming behavior through its real interface.

When auditing an existing suite, find tests and checkers that read Markdown and classify every assertion. Delete prose snapshots rather than weakening them to smaller keyword checks. Retain syntax, link, schema, embedded machine-identifier, executable-example, generated-surface, and consumer-behavior checks.

## State, Recovery, And Evidence Reuse

Do not schedule a full backup/restore exercise for ordinary logic that leaves persistence and recovery paths untouched. A new revision, repair, candidate digest, or template-only change does not by itself invalidate still-valid recovery evidence. Unique or irreplaceable data keeps its protection regardless of project-stage labels; still obey applicable repository requirements.

Migration of retained state must exercise the upgrade of realistic existing state, not only empty-database initialization. Changes to backup or restore must verify restore behavior. Authorized disposable development state may prove recovery by rebuild or replace; do not force in-place upgrade for state that is approved to discard.

Reuse reliable evidence that still matches the final candidate. Later edits that change the covered behavior, fixture, environment, recovery implementation, or retained-state conditions invalidate the old result and need a fresh check of the affected path. Refreshing a production backup is not by itself a reason to redo every recovery proof. Local greens do not prove uncovered combinations or state transitions; those still need verification. Do not invent a scoring rubric or a standing drill catalog to force this scaling.

## Proportionate Safeguards

A new hash, restore proof, replay mechanism, deployment rehearsal, or test gate is additional functionality, not free safety. Tie it to the affected behavior and a concrete failure mode; prefer an existing Git/object identity or project primitive when it already provides the needed guarantee. Preserve real integrity and recovery requirements, but do not add an independent identity chain or full lifecycle drill solely because a slice, revision, or prose instruction changed.

Review only the relevant suite and instructions for a bounded change. Do not expand a local fix into a repository-wide test cleanup or prove instruction meaning with hardcoded prose keywords. Offline scenario review may expose contradictions, but does not establish improved model behavior or economic outcomes.

## Oracle Integrity

- Do not delete, weaken, or bulk-update a required oracle to make implementation pass. Authorized secondary tradeoffs are disclosed adapted results, not deleted assertions.
- Record the oracle type for non-trivial changes: example, scenario, contract, property, model, current-behavior snapshot, meta-oracle, or runtime oracle.
- Treat test deletion, assertion weakening, snapshot updates, contract changes, and security-oracle changes as elevated-risk diffs. Those labels inform risk judgment; they do not schedule a review round or a full matrix.
- Do not add sleeps, retries, broad status ranges, or existence-only assertions to hide deterministic failures.
- Preserve exact negative and boundary behavior where it carries domain meaning.

## Fixtures And Environments

- Prefer deterministic fixtures and explicit setup/cleanup.
- Exercise the real owned boundary; mock only dependencies outside that boundary.
- Keep each test independent and avoid shared mutable state.
- Use readiness checks instead of fixed sleeps.
- Isolate databases, ports, caches, temporary files, and environment variables.
- Build subprocess environments from an explicit allowlist starting with an empty mapping; add only required variables and use temporary homes or caches where needed.
- Inherit the ambient environment only when ambient-environment behavior is the named subject of the test; document the exception, exclude sensitive variables, and redact failure output.
- Do not require live credentials, production state, or hardware unless the owning plan explicitly authorizes that evidence.

## Test Design

- Use Arrange-Act-Assert or an equally clear scenario structure.
- Name tests by behavior, condition, and outcome.
- Prefer table-driven examples for stable rule matrices.
- Prefer properties or fuzzing when invariants matter more than examples.
- Prefer characterization tests for unknown legacy behavior before refactoring.
- Keep workflows focused on business sequences rather than endpoint catalogs.
- Keep UI/E2E narrow and user-visible.
- User-experience goals need corresponding scenarios, such as independent selection across business groups or a first-run initialization source. Parser, existence, or golden checks do not replace those behaviors.

## CI And Release Placement

Read [Capability-Based CI](references/ci-config.md) when assigning lanes.

Fast failures should precede expensive evidence. Keep commands project-owned and deterministic. Separate current-state validation from checks that require an explicit comparison base, deployment, hardware, or production authority.

## Output Contract

When this skill owns the response, lead with the recommended suite placement and commands. Include only:

- protected boundary and oracle
- fixture/environment and owning suite
- CI/release lane and diagnosis owner
- concrete verification order
- material discard reasons and failure modes

For an existing-suite audit, give every discovered suite an evidence-backed primary disposition: `keep`, `refactor`, `replace`, `delete`, `split`, or `move-lane`. Do not turn a shared motivation into an execution dependency; record cross-repository producer, consumer, ownership, and write-set dependencies separately.

When another lifecycle skill owns the response, contribute these results as a semantic overlay.

## References

- [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md)
- [Python Testing Examples](references/examples-python.md)
- [Go Testing Examples](references/examples-go.md)
- [Capability-Based CI](references/ci-config.md)
- [TDD Vertical Slices](references/tdd-vertical-slices.md)
- [Agent Skill Evaluation](references/agent-skill-evaluation.md)
- [Goal And Risk Cases](references/goal-and-risk-cases.md)
