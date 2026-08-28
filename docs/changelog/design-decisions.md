# Design Decisions

## 2026-08-28 — Portable Semantic Skills Only

### Decision

This repository owns 40 provider-neutral semantic Agent Skills, declarative authoring contracts, generated portable distribution, static conformance, stable documentation, and optional plugin manifests. It owns no workflow engine, artifact validator, task graph compiler, mutable execution ledger, provider adapter, actor or model binding, attempt scheduler, or replay protocol.

Formal `design-change`, `plan-change`, and `implement-change` each compose exactly one bounded `review-change` before accepting their semantic result. Informal work has no implied review. Standalone review starts from the supplied bounded target without synthesizing upstream phases. Review evaluators remain read-only; the calling agent adjudicates candidate findings and owns any accepted repair.

### Consequences

- Public Skill IDs remain stable and portable across compatible agent products.
- Mechanically enforced workflow behavior belongs outside this repository and is neither imported nor named as a dependency.
- Repository scripts validate only authored inventory, metadata, reference closure, generated parity, documentation, and ordinary code quality.
- Earlier runtime, provider-binding, and generated lifecycle decisions are superseded. Their historical detail remains in `docs/plans/` and `archived/`, outside current stable truth.

## 2026-08-20 — Live Child Links Are The Recommended Local Path

Use a local Git checkout plus one child symlink per public ID. Update the checkout with Git, regenerate its owned payload, and start a new agent session. Optional plugin or copied installations have separate update and removal lifecycles, and each tool should expose only one active path per public ID.

## 2026-08-07 — Generated Root-Flat Distribution

`src/skills/` is authored truth. `skills/` is the generated root-flat payload, and every public Skill must be self-contained under its own standard Agent Skills directory. Provider plugin manifests package that same payload without changing semantics.
