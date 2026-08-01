# Testing Strategy Layering And Suite Audit Design

## Status

- design_version: 1
- approval_required: true
- approval_status: approved
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The current `testing-strategy` skill names useful test categories and execution lanes, but it does not define a sufficiently deterministic classification procedure for auditing an existing mixed infrastructure suite. Without that procedure, an audit can mistake file length for poor test design, call every repository check a unit test, accept a test that reimplements the source as an independent oracle, or conflate the semantic level of evidence with when CI runs it.

The four homelab repositories contain legitimate large table-driven and component suites alongside a 6,608-line cross-repository contract module, natural-language prose snapshots, broad environment inheritance in subprocess tests, and suites that mix several diagnosis owners. The user approved correcting the environment boundary, removing prose snapshots, splitting the platform aggregate, and separating operations tests, but requested that the reusable testing guidance be corrected and reviewed before it is used to produce the repository-specific remediation guidance.

## Goals

- Make test classification depend on the protected boundary, real dependencies, authority, oracle, and diagnosis owner rather than framework, filename, or line count.
- Separate a test's primary evidence class from its execution lane and from cross-cutting quality attributes such as security, compatibility, performance, and resilience.
- Define the smallest-sufficient-layer rule: use the lowest realistic boundary that proves the invariant, and add higher-layer evidence only when it proves something unavailable below.
- Define an existing-suite audit contract with the dispositions `keep`, `refactor`, `replace`, `delete`, `split`, and `move-lane`.
- Make independent-oracle quality explicit so that tests do not merely repeat source logic, manifests, or natural-language policy.
- Require explicit environment allowlists for spawned processes by default, especially when the developer environment may contain credentials.
- Keep `SKILL.md` concise and place the detailed decision tree, matrices, examples, smells, exceptions, and audit output schema in a directly linked reference.
- Review and forward-test the revised skill before using it for the four-repository homelab audit.

## Non-Goals

- Modify tests, implementation, CI, or documentation in `homelab-infra`, `homelab-platform`, `homelab-operations`, or `homelab-dotfiles` during this milestone.
- Repair, preserve, or otherwise act on the known-bad token observed during the earlier operations test analysis.
- Declare a universal maximum file length, test length, test count, coverage percentage, or pyramid ratio.
- Force every verification activity into a single linear unit-to-E2E hierarchy.
- Add phrase assertions, keyword snapshots, or exact-heading tests for the revised skill prose.
- Create a new lifecycle skill, command, manifest entry, or public skill identifier.

## Change Classification

- request_kind: skill-guidance-change
- change_class: B
- design_strength: design-lite
- truth_impact: medium
- boundary_impact: medium
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: false

## Approved Behavior Contract

Every audited check is described with orthogonal fields instead of one overloaded label:

- Protected boundary: the invariant or observable behavior that must remain true.
- Primary evidence class: static/documentation/generated, unit, component, integration, contract/conformance, workflow/system, UI/E2E, or runtime.
- Dependency and authority scope: in-process, isolated local dependency, cross-repository input, deployed non-production system, or production-authorized observation.
- Oracle type: example, table, property, schema, compatibility comparison, scenario, model, current-behavior snapshot, meta-oracle, or runtime oracle.
- Execution lane: fast, merge, release, or runtime.
- Cross-cutting tags: compatibility, security, performance, resilience, migration, or another named quality attribute when relevant.
- Owning suite and diagnosis owner: one primary owner responsible for explaining and repairing the failure.

The primary evidence class is chosen by the highest real boundary exercised, not by the mocking library, test framework, directory, or command name. Contract, performance, security, and runtime evidence are not treated as interchangeable rungs in a universal pyramid.

File and test length are diagnostic signals only. A long table-driven suite, focused parser matrix, or readable golden fixture can remain cohesive; a module should be split when it mixes protected boundaries, fixtures, authority levels, execution lanes, or diagnosis owners, or when a failure cannot be localized without reading unrelated scenarios.

A test is not an independent oracle when it reproduces the source algorithm, restates an entire manifest field by field without a separately owned contract, or derives expected output from the same transformation under test. Prefer simpler domain examples, schemas, properties, models, real consumers, compatibility bases, or independently authored fixtures.

Human prose is protected by review, lint, links, builds, structured metadata validation, executable examples, generation parity, or observable consumer behavior. Exact natural-language sentences, keyword collections, and headings are not unit-test APIs.

Subprocess tests build an explicit environment allowlist from an empty mapping and add only required variables. Full environment inheritance is allowed only when ambient-environment behavior is the subject of the test, the exception is documented, sensitive variables are excluded, and failure output is redacted.

## Reference Shape

The source skill remains the compact normative entry point. A new `references/test-layering-and-suite-audit.md` owns the classification decision tree, evidence-class versus lane matrix, audit dispositions, suite-smell criteria, acceptable large-test cases, infrastructure examples, environment isolation rule, and review output schema.

The existing `references/ci-config.md` remains the owner of CI placement and is revised to map evidence to `fast`, `merge`, `release`, and `runtime` lanes with explicit environment and authority requirements. It must distinguish current-state validation from compatibility checks that require a base and from deployed checks that require runtime authority.

## Phase Boundary

This milestone changes and validates only `coding:testing-strategy`. After it passes deterministic validation and bounded review, a separate read-only phase will use the generated skill to inventory and classify all four homelab repositories, producing one shared audit and coordination ledger with evidence-backed `keep`, `refactor`, `replace`, `delete`, `split`, and `move-lane` recommendations.

The ledger must record each accepted change's owning repository, protected contract, producer and consumers, external dependencies, and whether it can execute independently. Common motivation is not an execution dependency.

Repository test edits require one repo-local `plan-change` artifact for each repository with accepted changes; a repository with no accepted change receives no empty plan. Each plan is independently approved and executed. Plans may be marked parallel-safe only after the shared ledger freezes their cross-repository dependencies and proves that they do not write the same contract or require another plan's output; otherwise they declare the exact inter-plan dependency.

The already accepted directions remain inputs to those later plans: correct operations subprocess environment handling with an allowlist, remove natural-language prose snapshots, split the platform cross-repository aggregate by owner and failure domain, and separate operations suites by boundary and lane. The known-bad token itself remains out of scope. Subagents may review or execute a dependency-frozen plan slice when that plan declares them ready, but delegation does not replace repo-local ownership or approval.

## Boundaries

- Source truth stays under `src/skills/disciplines/testing-strategy`; the root-flat `skills/testing-strategy` surface is generator-owned.
- `testing-strategy` owns concrete suite classification, placement, environment, lane, and failure diagnosis after oracle-method selection; `executable-oracle-architecture-selector` retains oracle-method authority.
- The new reference guides audit judgment but does not authorize repository mutation, test deletion, assertion weakening, or CI changes.
- Existing unrelated `organize-docs` work in `market-csheng` must remain byte-for-byte unchanged.
- No worktree, commit, push, installed global skill refresh, or homelab repository write is authorized by this design alone.

## Acceptance Conditions

- The revised skill defines the orthogonal classification fields and smallest-sufficient-layer rule without presenting a false universal hierarchy.
- The audit reference distinguishes legitimate long tests from mixed-owner god suites and defines actionable dispositions with required evidence.
- The guidance rejects source reimplementation, same-source tautologies, prose snapshots, and broad secret-bearing environment inheritance as weak or unsafe oracles.
- The CI reference maps evidence classes to execution lanes and authority boundaries without prescribing one vendor or universal numeric threshold.
- Source validation, deterministic generation, source/root-flat parity, aggregate repository checks, Markdown whitespace checks, a representative homelab forward-test, and bounded implementation review pass.
- No automated test is added solely to freeze the revised natural-language guidance.
- The next phase is a read-only four-repository audit and dependency ledger, followed by independently approved repo-local remediation plans only for repositories with accepted changes.

## Human Gate

- approval_basis: The user accepted the four concrete remediation directions, explicitly requested clearer layered behavior in `coding:testing-strategy`, agreed that the skill should be fixed and reviewed before auditing the repositories, and requested `coding:plan-change` first.
- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/skills/disciplines/testing-strategy/SKILL.md
  - src/skills/disciplines/testing-strategy/references/ci-config.md
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/SKILL.md
  - skills/testing-strategy/references/ci-config.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- test_file_refs:
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
