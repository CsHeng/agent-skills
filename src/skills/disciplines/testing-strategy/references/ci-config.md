# Capability-Based CI

## Principle

Expose stable project-owned commands and map them to evidence lanes. Do not make a CI vendor, runner image, language version, service container, or coverage percentage the reusable strategy.

Evidence class answers what boundary is proved. Execution lane answers when the evidence is economical and authorized. Classify them separately.

## Contents

- [Lane Decision Record](#lane-decision-record)
- [Execution Lanes](#execution-lanes)
- [Capability Placement](#capability-placement)
- [Deterministic Environment](#deterministic-environment)
- [Gate Design](#gate-design)
- [Coverage](#coverage)

## Lane Decision Record

For every project-owned gate, record:

- command and protected boundary
- primary evidence class and oracle
- real dependencies and environment
- expected duration and resource cost
- required credentials, hardware, deployment, comparison base, or recovery authority
- failure diagnosis owner
- whether failure blocks merge, release, or runtime promotion
- typed fallback or stop when required external evidence is unavailable

Assign one primary lane. Repeating a cheap lower-lane gate later can add confidence, but repetition does not change its evidence class or ownership.

## Execution Lanes

### Fast

Run deterministic current-checkout evidence that needs no service startup, network authority, live credential, comparison base, or special hardware. Formatting, lint, type, schema, reference, generated-parity, compilation, and focused unit or component checks usually start here.

Fast means cheap and self-contained for the project; do not impose a universal time limit.

### Merge

Run evidence needed to decide whether a change may join the main line: isolated integration, contract or compatibility comparison, provider and consumer conformance, and critical workflow scenarios. Use explicit local services, synthetic credentials, temporary state, and a resolvable comparison base where required.

Current-state validation and base-versus-head compatibility are separate gates. A missing required base is a typed evidence failure, not permission to silently skip or compare against an arbitrary revision.

### Release

Run evidence over the actual release artifact, reproducible package, migration path, staging deployment, or explicitly allocated hardware. Release credentials and environments must be job-scoped and must not become ambient inputs to unrelated tests.

Use this lane when source-level evidence cannot prove artifact composition, packaging, upgrade, deployment, platform, or release-candidate behavior.

### Runtime

Run canaries, synthetic probes, SLO evaluation, and production-only invariants only with explicit deployment, observation, and recovery authority. Use least-privilege runtime credentials and bounded blast radius.

Runtime failure does not authorize rollback unless an approved plan declares the exact guarded trigger, target, and verification. Runtime evidence does not replace pre-merge correctness.

## Capability Placement

The table gives a typical earliest lane, not a mechanical mapping:

| Evidence capability | Typical earliest lane | Placement rule |
| --- | --- | --- |
| Static and current-state contract | Fast | Run formatting, lint, type, schema, references, generated output, and configuration before expensive evidence |
| Compatibility | Merge | Require an explicit base and distinguish first introduction from missing evidence |
| Provider integration | Merge | Exercise the real owned protocol boundary with isolated dependencies and cleanup |
| Consumer adapter | Fast or merge | Keep mapping and serialization local when possible; use merge when a real protocol, artifact, or provider is required |
| Workflow or system | Merge or release | Run critical multi-operation scenarios after cheaper provider and consumer failures are diagnosable |
| UI/E2E | Merge or release | Keep only user-visible journeys that cannot be proved below the UI |
| Performance or resilience | Release or runtime | Name the workload, environment, invariant, threshold rationale, blast radius, and owner |
| Runtime | Runtime | Require deployed-state and recovery authority |

Do not extensively retest generated internals. Protect the generator, deterministic artifact, compilation or parsing, and consumer-owned assumptions.

## Deterministic Environment

- pin project dependencies and generators
- use isolated temporary data
- build child-process environments from an empty mapping and an explicit allowlist
- use temporary homes, caches, ports, databases, and synthetic credentials
- opt into job credentials only for the gate that owns them
- inherit the ambient environment only when ambient behavior is the protected boundary, then remove sensitive variables and redact failures
- wait on readiness with a bounded probe
- capture diagnostic logs and artifacts
- clean up in success and failure paths
- avoid fixed sleeps and order-dependent state

Access to a developer shell, CI secret, cloud profile, agent socket, production credential, or management network does not make it an authorized test input.

## Gate Design

Run narrow affected gates during implementation and the declared aggregate gates before completion.

Order gates by diagnosis value and cost: deterministic static and local evidence first, isolated integration and compatibility next, release-artifact and workflow evidence after that, and runtime-authorized observation last. A higher lane must add evidence unavailable below rather than repeat the same assertion with more infrastructure.

## Coverage

If coverage is used, treat it as one signal. Set project-specific thresholds from risk and baseline, exclude generated or irrelevant code deliberately, and review threshold changes as oracle changes.

Do not create low-semantic tests merely to satisfy a percentage.
