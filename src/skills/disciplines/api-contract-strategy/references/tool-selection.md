# Tool Selection

## Selection Record

For every selected tool, record:

- protected layer and failure class
- why the tool fits the repository toolchain
- project-owned invocation and version pin
- operational cost and required infrastructure
- alternative considered and material discard reason
- rejected defaults
- observable upgrade trigger

Prefer capabilities over brand names. Repositories should expose stable commands even if the underlying tool changes.

## Static OpenAPI Validation

Needed capabilities:

- parse and resolve references
- validate the chosen OpenAPI dialect
- lint naming, operation ids, examples, and security declarations
- provide deterministic nonzero exit status in CI

Possible tools include vacuum, Redocly, Spectral, and project-specific validators. Select one compatible with the existing toolchain and pin it.

Do not add a custom validator when a maintained project-owned CLI closes the same gap.

When one repository needs linting, reference resolution, deterministic bundling, Arazzo execution, and generated documentation, prefer the integrated Redocly CLI surface if its runtime and supported dialects fit. This does not require Redocly hosted services.

## Compatibility

Needed capabilities:

- compare explicit base and head contracts
- classify removed operations, required input, response narrowing, types, enums, status, and security changes
- configure severity for repository policy
- distinguish first introduction from missing evidence

Possible tools include oasdiff and equivalent structural diff engines. Schema compatibility still requires a semantic compatibility review owner.

## Provider Conformance

Prefer a library or runner that matches real protocol operations and validates actual requests and responses. Reuse the provider language and existing integration harness when practical.

Schemathesis or generative tools become attractive after a stable baseline exists and broad input exploration targets a named residual risk. They are not a prerequisite for basic conformance.

## Generated Client

Choose types before a full runtime client when the consumer already owns valuable policy. Pin the generator, commit or deterministically regenerate output, compile it, and fail stale-output checks.

Do not extensively test generated client internals. Test the generator/version contract and consumer-owned adapter behavior.

## Workflow Runner

Select an Arazzo-aware CLI/CI runner that links OpenAPI operations, verifies response status, schema, content type, and success criteria, accepts runtime inputs and server overrides, masks secrets, and returns deterministic exits. Prefer Redocly Respect when its supported Arazzo revision and the repository runtime fit; pin the Arazzo revision the selected runner can execute, because lint support for a newer revision is not execution support.

Retain an existing workflow runner when it already exercises the important scenario with lower operational cost. Workflow authoring, workflow count, and GUI or ad hoc interaction are owned by [Structured Contract Stack](structured-contract-stack.md).

## CDC / Pact

Do not automatically recommend Pact. The selection conditions and lifecycle cost are owned by [Legacy Adoption](legacy-adoption.md); price broker operation, provider states, publishing, version selection, and matrix growth before recommending it.

## Common Rejections

- independent contract repository without independent ownership
- hosted artifact or broker infrastructure for a small first-party team
- full generated SDK when type projection closes the drift
- UI tests for schema or serialization failures
- runtime probes as the first compatibility gate
- coverage thresholds without a protected boundary and diagnosis owner

Every rejected option should include an upgrade trigger rather than a permanent prohibition.
