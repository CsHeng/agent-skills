# Structured Contract Stack

## Truth Roles

Keep one maintained source for each truth kind:

| Truth kind | Maintained source | Derived or executable surface |
| --- | --- | --- |
| HTTP operation and wire shape | OpenAPI root plus referenced fragments | Deterministic bundle, provider models, consumer types, fixtures, and generated HTML |
| Cross-operation outcome | Arazzo referencing stable OpenAPI operation IDs | Respect or another conforming CLI runner |
| Environment lifecycle | Existing project-owned lifecycle glue | Process, database, fixture, restart, readiness, and cleanup orchestration |
| Non-HTTP domain behavior | Owning code and stable domain docs | Focused tests and links |

Keep these roles non-overlapping. Arazzo defines sequencing, value chaining, runtime inputs, and success criteria; request and response schemas stay in OpenAPI.

## Authoring Source

Prefer OpenAPI-first when several provider or consumer languages, repositories, or agents need shared structured wire truth, compatibility must be reviewed before code drift, and generated provider boundary models are practical.

Prefer typed declarative code-first when one provider framework can export the complete OpenAPI contract deterministically from typed declarations. Reject the choice when manual repair is required or stale output cannot fail mechanically.

Use annotation- or comment-first generation only when annotations cover every operation and schema, the output is complete and deterministic, and missing or stale output fails a project-owned check.

For a legacy API, characterize registered routes and real protocol behavior, identify stable semantic truth, and adjudicate conflicts. Treat handwritten documentation and current implementation as equally unverified until adjudicated.

## Source Layout And Bundle

Keep one file for a genuinely small contract. When operation count, schema count, ownership, or merge contention makes that hostile to review, keep one thin root and split maintained source by stable API domain.

Provide one pinned project-owned command that resolves references, lints, and creates a deterministic bundle. Treat the bundle as generated:

- commit it with stale-output protection when portability, review, or agent context requires it
- otherwise write it to an ignored build root and regenerate it in every owning workflow

Edit the fragments and regenerate the bundle.

## Generated Projections

Generate only the provider and consumer wire boundary needed to remove duplication. Choose the projection size using Generated Client Scope in [Contract Lifecycle](contract-lifecycle.md). Keep domain models, persistence types, retry policy, UI state, and other non-wire behavior hand-written by default.

Generate human reference documentation from OpenAPI as the only API catalog.

## Workflows, Runner, And Lifecycle Glue

Use Arazzo for a small number of outcomes that require multiple operations, chained values, or state transitions. Keep workflow count proportional to business journeys, reference stable OpenAPI operation IDs, pass secrets as masked runtime inputs, and use synthetic examples.

Select a CLI/CI runner with the OpenAPI reference resolution, response verification, runtime input, server override, and deterministic exit capabilities described in [Tool Selection](tool-selection.md). Pin the executable revision; hosted services stay optional.

Retain Python or Shell only as lifecycle glue when it owns dynamic process, database, fixture, restart, readiness, or cleanup orchestration. After runner equivalence is proven, remove duplicated business HTTP steps from that glue.

## Human, Ad Hoc, And GUI Interaction

Use generated HTML for human review or external reference when a publication owner and audience exist. Agents can use the contract and generated artifacts directly.

Use Restish, curl, or a disposable single-operation Arazzo workflow for ad hoc exploration, and keep those artifacts uncommitted.

Add Bruno, Postman, Yaak, or another GUI collection only when a named GUI collaboration requirement justifies a generated or synchronized projection. Keep OpenAPI and Arazzo upstream as contract truth; treat the GUI collection as a projection.
