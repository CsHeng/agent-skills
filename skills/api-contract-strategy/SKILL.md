---
name: api-contract-strategy
description: "Analyze and design API contract authoring, ownership, compatibility gates, provider conformance, consumer adapters, OpenAPI/Arazzo workflows, generated code and documentation, client lifecycle, and incremental legacy adoption. Use for HTTP providers with web, mobile, firmware, or multi-repository consumers when contract drift, duplicated DTOs, oversized OpenAPI files, manual API docs, Swagger annotations, CDC/Pact, Redocly/Respect, GUI collections, workflow tooling, or client generation decisions need clear boundaries."
---

# API Contract Strategy

## Purpose

Design the smallest sufficient contract and verification architecture for an API system: meaningful boundary evidence, clear ownership, deterministic compatibility, and low operational cost. Measure maturity by which boundaries have independent evidence and clear ownership.

## Scope

Read `references/oracle-selection.md` in `skills-routing` when the evidence strategy is unresolved. This Skill decomposes API ownership, compatibility, provider, consumer, workflow, and generation boundaries once a contract oracle exists, either a selected method or an existing OpenAPI/conformance setup.

## Decision Workflow

1. Map the provider, consumers, repository boundaries, release cadences, existing tests, current contract source, and duplicated representations.
2. Choose the maintained authoring source, domain split, bundle, generated projections, workflow specification, runner, and human documentation model using [structured contract stack](references/structured-contract-stack.md).
3. Classify existing evidence and decide which claims it supports using [verification layers](references/verification-layers.md).
4. Decide contract ownership, repository placement, workspace inputs, development generation, and release artifacts using [contract lifecycle](references/contract-lifecycle.md).
5. Identify the smallest missing verification layer and close that gap.
6. Select project-owned gates and tools using [tool selection](references/tool-selection.md); `testing-strategy` places the resulting suites, fixtures, and CI lanes.
7. Stage legacy adoption using [legacy adoption](references/legacy-adoption.md), preserving useful existing oracles.
8. Record rejected approaches and observable upgrade triggers.

Each reference holds the defaults, conditions, and upgrade triggers for its decision; read the one the decision touches.

## Output

Render only the decision-relevant conclusions. When the user explicitly requests a comprehensive assessment, cover current state, missing verification layers, target architecture and ownership, the incremental migration plan, tool choices with alternatives and operational cost, and rejected approaches with upgrade triggers.

## Guardrails

- Treat only deterministic validators and reviewable artifacts as contract authority.
- Apply `implement-change` Acceptance Integrity when implementation conflicts with a schema, fixture, assertion, or compatibility rule.
- Apply the demand test in `architecture-patterns` to operational infrastructure, and record its named owner and upgrade trigger.
