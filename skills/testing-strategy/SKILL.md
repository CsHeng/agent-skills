---
name: testing-strategy
description: "Design or revise verification coverage, suite placement, fixtures, isolation, and execution lanes for an established oracle. Use for test-strategy decisions or suite audits; not merely to run existing checks or add routine tests under a settled strategy."
---

# Testing Strategy

## Purpose

Turn a selected executable oracle into the smallest concrete verification set that protects the user's intended outcome and actual consumer requirements. Existing tests and implementation behavior are evidence to assess, not requirements by themselves.

When supporting design, planning, simplification, implementation, or review, contribute only the testing decisions and evidence needed by that task. Its owner chooses the deliverable and presentation under `output-styles`; this skill and its references do not add a separate audit report or enlarge the requested scope.

Read only `references/oracle-selection.md` in `skills-routing` when the oracle method or protected behavior still needs a decision, not merely because the task involves architecture, planning, or TDD. Consume an established strategy directly. Running known checks or adding a routine regression test under that strategy does not require reopening strategy selection. For multi-client API contract ownership and layer decomposition decisions, use `api-contract-strategy`.

Do not measure maturity by test count or impose universal coverage percentages. Do not define effort by a fixed number of tests or hypotheses.

## Strategy Mapping

When selecting or auditing a strategy, use the relationships below to identify the decisions that matter. Explain relevant choices in the owning deliverable without filling a separate form. Routine tests under an established strategy consume it directly:

```text
boundary -> oracle -> fixture/environment -> owning suite -> CI/release lane -> diagnosis owner
```

1. Name the user outcome or consumer behavior being protected and its owner.
2. Carry forward the selected executable oracle and record the failure class it detects.
3. Choose the smallest realistic fixture and environment.
4. Place the check in the suite that owns diagnosis.
5. Assign fast, merge, release, or runtime execution.
6. Define what a failure means and who repairs it.

A missing verification layer is not repaired by duplicating lower-value unit tests.

Start acceptance from the critical consumer outcome and plausible failure modes, then choose the smallest real boundary that can prove each invariant. Keep a few risk-representative cross-boundary scenarios for behavior that isolated tests cannot see; use focused unit or integration checks for detailed logic and diagnosis. Neither an E2E-only rule nor a mandatory new test for every change protects an invariant by itself. A passing scenario with expected results invented from the same implementation is still a weak oracle.

## Classification Contract

When classifying or auditing existing checks, read [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md).

Distinguish these dimensions when they affect the decision rather than forcing one overloaded test label or requiring every field in the output:

- protected boundary and observable invariant
- primary evidence class
- real dependency and authority scope
- oracle type and independent source
- fast, merge, release, or runtime lane
- cross-cutting quality tags when relevant
- owning suite and failure diagnosis owner

Choose the primary evidence class from the highest real boundary exercised, not the framework, filename, directory, mock library, or test length. Evidence class and execution lane are separate decisions; security, compatibility, performance, and resilience are usually cross-cutting tags rather than universal hierarchy levels.

Use the smallest realistic boundary that can prove the invariant. Add higher-boundary evidence only when it proves behavior unavailable below, such as real serialization, persistence, provider interaction, a multi-operation workflow, UI behavior, or deployed conditions.

Test and file length are diagnostic signals, not verdicts. Assess the maintenance cost of setup, duplicated helpers, fixture copies, and extra processes as well as runtime cost. Split when one suite mixes protected boundaries, fixtures, authority levels, execution lanes, or diagnosis owners, or when failures cannot be localized. Keep cohesive table-driven matrices, parser cases, and reviewed golden contracts when their oracle remains independent and readable; sharing an expected fixture does not reduce coverage when several inputs intentionally produce the same result.

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

Critical paths may justify stronger gates than glue or generated code. Verify generated output through its real consumer and any declared reproducibility requirement rather than covering generated internals by hand. Keep dependency pins with their owner; tests should not copy the current selected version or checksum into a second source of truth.

## Red-Green Verification

- For behavior changes and bug fixes, first identify the failing consumer outcome and an independent expected result; write or identify a failing test or narrow reproducer before implementation when a correct seam exists. A post-change regression test is useful when it closes a real behavior gap, not just because code changed.
- Confirm the oracle fails for the expected reason, not a typo or environment error.
- A missing perfect agent-runnable reproducer does not freeze other authorized work; use the tightest available equivalent evidence and keep unblocked work moving.
- Implement the smallest change that makes the reproducer pass.
- Rerun the narrow oracle and declared verification scope before claiming success.
- For config-only changes, prefer parser, schema, or real-consumer validation.
- For docs-only, generated, or exploratory changes, record the fitting lint, build, generation check, or manual evidence.
- When the user asks for TDD, test-first work, red-green-refactor, or vertical slices, read [TDD Vertical Slices](references/tdd-vertical-slices.md).

## Documentation And Markdown Verification

Code and deployed observations establish implemented behavior; documents and diagrams describe human intent or explain that behavior. Update them when implementation changes, but do not make their prose or diagrams executable production truth. Explicit user requirements remain binding regardless of where they were recorded.

Use existing documentation tooling for the limited property it actually checks:

- Human-authored prose: use review plus Markdown/prose linting, link checking, and documentation builds where applicable.
- Frontmatter, schemas, command identifiers, paths, and other machine-readable fields embedded in Markdown: validate the structured field when an actual consumer or repository boundary depends on it; formatting preference alone does not make it a contract.
- Executable examples: compile or run the example through the real interface.
- Generated documentation and diagrams: regenerate with the owned tool and inspect the result. Existing generation/parity checks may verify the tool's operation; do not add snapshots of document or diagram content as a proxy for product behavior.
- Prompt or instruction Markdown: test observable consumer behavior with an evaluation or integration scenario when that evidence is worth its cost; machine consumption alone does not make prose a unit-test interface. An offline fixture can prove loading or workflow mechanics, not that a live model follows the instruction.

When efficacy measurement is requested or a bounded risk judgment justifies it, use [Agent Skill Evaluation](references/agent-skill-evaluation.md) with the necessary execution authority and budget. Ordinary Skill editing does not require a live experiment, and maintenance checks do not establish behavioral or economic gains.

For offline review of goal, risk, and discretion behavior, read [Goal And Risk Cases](references/goal-and-risk-cases.md). Those cases are optional comparison material, not unit tests, CI gates, or required live experiments.

Do not freeze natural-language sentences, keyword collections, headings, document layout, diagram nodes or edges, or their absence merely to encode intended meaning. Model visibility does not turn wording into a test interface. Moving an unnecessary prose assertion into a schema or another metadata file does not make it useful. When a real machine-consumed contract needs enforcement, validate its owned structured source or consuming behavior rather than duplicating documentation in test code.

When auditing an existing suite, classify relevant Markdown assertions by their consumer or protected boundary. Delete prose snapshots rather than weakening them to keyword checks. Retain applicable syntax, link, schema, executable-example, generated-surface, and consumer-behavior checks.

## State, Recovery, And Evidence Reuse

When evidence for change-sensitive state is unresolved — retained-state migration, backup/restore behavior, rebuild-versus-replace for authorized disposable state — read `references/oracle-selection.md` in `skills-routing`. Under an established strategy, reuse reliable evidence that still matches the final candidate: later edits that change covered behavior, fixtures, environments, or recovery and retained-state conditions invalidate the old result and need a fresh check of the affected path, while local greens never prove uncovered combinations or state transitions. Do not schedule a full backup/restore exercise for ordinary logic that leaves persistence and recovery paths untouched, and do not invent a scoring rubric or a standing drill catalog to force this scaling; unique or irreplaceable data keeps its protection regardless of project-stage labels, and applicable repository requirements still apply.

## Proportionate Safeguards

A new hash, restore proof, replay mechanism, deployment rehearsal, or test gate is additional functionality, not free safety. Tie it to the affected behavior and a concrete failure mode. Ordinary local verification does not need source, fixture, or result hashes to certify that the agent tested its own work, nor a replacement requirement to record Git identities everywhere. Use existing project evidence when sufficient. Preserve checksums, signatures, or exact bytes where a real artifact, protocol, cryptographic operation, or explicit user requirement depends on them; do not add an independent identity chain or full lifecycle drill solely because a slice, revision, or prose instruction changed.

Review only the relevant suite and instructions for a bounded change. Do not expand a local fix into a repository-wide test cleanup or prove instruction meaning with hardcoded prose keywords. Offline scenario review may expose contradictions, but does not establish improved model behavior or economic outcomes.

## Oracle Integrity

- Protect the underlying requirement, not the existence of a test. Within authorized edits, remove or replace tests and agent-added guards that have no requirement or consumer basis, including incidental library behavior and arbitrary source or fixture bytes. An existing test, a passing review, or a model-written plan does not establish that basis. Exact wire bytes, cryptographic vectors, and explicitly required output remain valid oracles where they carry the contract.
- Do not delete, weaken, or bulk-update an oracle that protects a real requirement to make implementation pass. Removing a self-imposed constraint while preserving required behavior is not such weakening; authorized secondary tradeoffs remain disclosed adapted results.
- Record the oracle type for non-trivial changes: example, scenario, contract, property, model, current-behavior snapshot, meta-oracle, or runtime oracle.
- Judge test additions and removals by the protection gained or lost and their maintenance cost. Contract, snapshot, or security labels do not make every assertion necessary or schedule a review round or full matrix.
- Do not add sleeps, retries, broad status ranges, or existence-only assertions to hide deterministic failures.
- Preserve exact negative and boundary behavior where it carries domain meaning.

## Fixtures And Environments

- Prefer deterministic fixtures and explicit setup/cleanup.
- Reuse a fixture, expected output, or small helper when cases share the same meaning. Keep case-specific semantics separate and avoid a new test framework merely to deduplicate a few lines.
- Exercise the real owned boundary; mock only dependencies outside that boundary.
- Keep each test independent and avoid shared mutable state.
- Use readiness checks instead of fixed sleeps.
- Isolate databases, ports, caches, temporary files, and environment variables.
- Build subprocess environments from an explicit allowlist starting with an empty mapping; add only required variables and use temporary homes or caches where needed.
- Inherit the ambient environment only when ambient-environment behavior is the named subject of the test; document the exception, exclude sensitive variables, and redact failure output.
- Do not require live credentials, production state, or hardware unless the current change's explicit authorization — the user request or an approved plan — covers that evidence; a plan artifact is not the only authorization carrier, and ordinary local fixtures remain the default.

## Test Design

- Use Arrange-Act-Assert or an equally clear scenario structure.
- Name tests by behavior, condition, and outcome.
- Prefer table-driven examples for stable rule matrices.
- Prefer properties or fuzzing when invariants matter more than examples.
- Use characterization tests to investigate unknown consumer-relevant behavior before refactoring. Keep observations separate from required compatibility; do not permanently reproduce every parser quirk, library error, serialization detail, or historical bug just because the old program exhibited it.
- Keep workflows focused on business sequences rather than endpoint catalogs.
- Keep UI/E2E narrow and user-visible.
- User-experience goals need corresponding scenarios, such as independent selection across business groups or a first-run initialization source. Parser, existence, or golden checks do not replace those behaviors.

## CI And Release Placement

Read [Capability-Based CI](references/ci-config.md) when assigning lanes.

Fast failures should precede expensive evidence. Keep commands project-owned and deterministic. Separate current-state validation from checks that require an explicit comparison base, deployment, hardware, or production authority.

## Output Contract

When this skill owns the response, lead with the recommended testing decision and its basis. Include the protected behavior, oracle, placement, environment, commands, ownership, failure modes, and coordination only where they affect that decision or its execution. Choose prose, a list, table, or diagram for clarity; no fixed report shape is required.

For an audit, state the scope actually examined and give supported recommendations to keep, refactor, replace, delete, split, or move checks to another lane. A requested complete audit accounts for every entry point in that scope; a focused assessment may report representative findings and their limits without classifying every discovered suite. Shared motivation is not an execution dependency.

When another skill owns the response, integrate the relevant conclusions into its deliverable. Do not append this skill's output list as another report.

## References

- [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md)
- [Python Testing Examples](references/examples-python.md)
- [Go Testing Examples](references/examples-go.md)
- [Capability-Based CI](references/ci-config.md)
- [TDD Vertical Slices](references/tdd-vertical-slices.md)
- [Agent Skill Evaluation](references/agent-skill-evaluation.md)
- [Goal And Risk Cases](references/goal-and-risk-cases.md)
