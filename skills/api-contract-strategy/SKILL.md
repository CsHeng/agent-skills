---
name: api-contract-strategy
description: "Analyze and design API contract authoring, ownership, compatibility gates, provider conformance, consumer adapters, OpenAPI/Arazzo workflows, generated code and documentation, client lifecycle, and incremental legacy adoption. Use for HTTP providers with web, mobile, firmware, or multi-repository consumers when contract drift, duplicated DTOs, oversized OpenAPI files, manual API docs, Swagger annotations, CDC/Pact, Redocly/Respect, GUI collections, workflow tooling, or client generation decisions need clear boundaries."
---

# API Contract Strategy

## Purpose

Design the smallest sufficient verification architecture for an API system.

Optimize for meaningful boundary evidence, clear ownership, deterministic compatibility, and low operational cost. Do not measure maturity by test count.

## Authority Boundaries

This is advisory guidance for the active workflow: it does not own lifecycle transitions, repository mutation, review, repair, or completion, and the owning workflow keeps action, continuation, and response ownership.

Keep adjacent authorities separate:

- Read only `references/oracle-selection.md` in `skills-routing` to select contract, example, scenario, property, model, characterization, meta, or runtime oracle methods when that evidence strategy is genuinely unresolved.
- `api-contract-strategy` decomposes API ownership, compatibility, provider, consumer, workflow, and generation boundaries once a contract oracle is established — a selected method or an existing OpenAPI/conformance setup already in place.
- `testing-strategy` turns the selected boundaries into concrete suites, fixtures, environments, CI lanes, and diagnosis ownership.
- `architecture-patterns` owns monorepo versus multi-repository structure, service boundaries, independent lifecycle choices, and their economics.

Do not emit a competing implementation plan when design, planning, or implementation owns the response.

## Decision Workflow

1. Map the provider, consumers, repository boundaries, release cadences, existing tests, current contract source, and duplicated representations.
2. Choose the maintained authoring source, domain split, bundle, generated projections, workflow specification, runner, and human documentation model using [structured contract stack](references/structured-contract-stack.md).
3. Classify existing evidence using [verification layers](references/verification-layers.md).
4. Decide contract ownership, repository placement, workspace inputs, development generation, and release artifacts using [contract lifecycle](references/contract-lifecycle.md).
5. Identify the smallest missing verification layer. Do not answer every gap with more unit tests.
6. Select project-owned gates and tools using [tool selection](references/tool-selection.md).
7. Stage legacy adoption using [legacy adoption](references/legacy-adoption.md). Preserve useful existing oracles.
8. Record rejected approaches and observable upgrade triggers.

## Selection Defaults

Start from these defaults. The owning reference holds the conditions, exceptions, and upgrade triggers that change them; read it when that decision is actually on the table.

- Keep a wire contract in the provider repository unless ownership or release lifecycle is genuinely independent ([contract lifecycle](references/contract-lifecycle.md)).
- Prefer OpenAPI-first when several languages or agents need shared wire truth and provider boundary generation is practical; choose code-first or annotation-first only under the complete deterministic export and stale-output conditions in [structured contract stack](references/structured-contract-stack.md).
- Keep one maintained root, split by stable API domain only under scale or ownership pressure, and treat bundles, generated boundary code, and human reference documentation as projections ([structured contract stack](references/structured-contract-stack.md)).
- Treat schema compatibility and semantic compatibility as distinct evidence, validate provider behavior through the real protocol boundary, keep consumer evidence consumer-owned, and keep UI and runtime probes narrow and orthogonal ([verification layers](references/verification-layers.md)).
- Use Arazzo for a small set of cross-operation business journeys and one pinned CLI/CI runner; do not automatically add Pact/CDC, a broker, an independent contract repository, full generated clients, hosted tooling, or a GUI collection ([tool selection](references/tool-selection.md), [legacy adoption](references/legacy-adoption.md)).
- Prefer explicit workspace inputs over inferred sibling paths ([contract lifecycle](references/contract-lifecycle.md)).
- Prefer simple local generation for small first-party teams, and add reproducible versioned artifacts only when release independence requires them ([contract lifecycle](references/contract-lifecycle.md)).

## Output Contract

Render only decision-relevant conclusions in ordinary conversation.

When the user explicitly requests a comprehensive assessment, preserve:

1. Current state analysis.
2. Missing verification layers.
3. Target architecture and ownership.
4. Incremental migration plan.
5. Tool choices, alternatives, and operational cost.
6. Rejected approaches and upgrade triggers.

A local compatibility, tooling, or migration question does not require this list; answer the decision at hand and name only the conditions that change it.

When another workflow owns the response, contribute these results as a semantic overlay rather than an independent report.

## Guardrails

- Do not let AI-generated prose become contract authority; require deterministic validators and reviewable artifacts.
- Do not relax a schema, fixture, assertion, or compatibility rule merely to make implementation pass.
- Do not claim semantic compatibility from schema diff alone.
- Do not claim provider conformance from handler-unit or service-unit tests that bypass the protocol boundary.
- Do not claim consumer conformance merely because generated code compiles.
- Do not duplicate OpenAPI with endpoint-by-endpoint workflow collections.
- Do not add operational infrastructure without current demand, a named owner, and an upgrade trigger.
