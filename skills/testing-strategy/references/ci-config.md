# Capability-Based CI

## Principle

Expose stable project-owned commands and map them to evidence lanes, keeping the reusable strategy independent of CI vendor, runner image, language version, service container, and coverage percentage.

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
- the fallback, or a `blocked` result, when required external evidence is unavailable

Assign one primary lane. Repeating a cheap lower-lane gate later can add confidence, but repetition does not change its evidence class or ownership.

## Execution Lanes

### Fast

Run deterministic current-checkout evidence that needs no service startup, network authority, live credential, comparison base, or special hardware. Formatting, lint, type, schema, reference, generated-parity, compilation, and focused unit or component checks usually start here.

Fast means cheap and self-contained for the project.

### Merge

Run evidence needed to decide whether a change may join the main line: isolated integration, contract or compatibility comparison, provider and consumer conformance, and critical workflow scenarios. Use explicit local services, synthetic credentials, temporary state, and a resolvable comparison base where required.

Current-state validation and base-versus-head compatibility are separate gates. A missing required base is a `blocked` result; resolve the base or report the gap.

### Release

Run evidence over the actual release artifact, reproducible package, migration path, staging deployment, or explicitly allocated hardware. Scope release credentials and environments to the job that owns them.

Use this lane when source-level evidence cannot prove artifact composition, packaging, upgrade, deployment, platform, or release-candidate behavior.

### Runtime

Run canaries, synthetic probes, SLO evaluation, and production-only invariants only with explicit deployment, observation, and recovery authority. Use least-privilege runtime credentials and bounded blast radius.

Rollback after a runtime failure follows `implement-change` (Recovery). Pre-merge correctness is proved before merge.

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

For generated output, protect the generator, deterministic artifact, compilation or parsing, and consumer-owned assumptions, and verify it through its real consumer and any declared reproducibility requirement.

## Deterministic Environment

- pin project dependencies and generators
- use isolated temporary data
- for hermetic gates, build child-process environments from an empty mapping and an explicit allowlist
- use temporary homes, caches, ports, databases, and synthetic credentials
- opt into job credentials only for the gate that owns them
- inherit the ambient environment only when ambient behavior is the protected boundary, then remove sensitive variables and redact failures
- wait on readiness with a bounded probe
- capture diagnostic logs and artifacts
- clean up in success and failure paths
- avoid fixed sleeps and order-dependent state

A test input needs its own authorization; access to a developer shell, CI secret, cloud profile, agent socket, production credential, or management network does not supply it.

## Gate Design

Run narrow affected gates during implementation and, before completion, the aggregate gates that the change's impact or an explicit requirement calls for. Guard critical consumer paths with a few representative workflow or E2E scenarios rather than multiplying cheap assertions or covering every permutation through the most expensive lane. A required lane must fail or report unavailable when its prerequisite is missing; an optional local skip is not passing evidence for that lane.

Order gates by diagnosis value and cost: deterministic static and local evidence first, isolated integration and compatibility next, release-artifact and workflow evidence after that, and runtime-authorized observation last. A higher lane must add evidence unavailable below rather than repeat the same assertion with more infrastructure. For a consequential E2E, retain a bounded, redacted, repeatable proof appropriate to the boundary (such as the invocation, fixture identity and definitive output, or UI recording plus observable assertions). An artifact without an independently established expected result is not an oracle.

## Coverage

Treat line, branch, mutation, and scenario coverage as diagnostic evidence. Set project-specific thresholds from risk and baseline, exclude generated or irrelevant code deliberately, and review threshold changes as oracle changes.

Add a numeric gate when:

- it protects a named boundary or regression class
- the repository has a stable baseline
- the threshold has an owner and review rationale
- failure diagnosis is actionable
- raising the threshold will not incentivize low-semantic tests

Critical paths may justify stronger gates than glue or generated code. Keep dependency pins with their owner; tests reference the owner and carry no second copy of the selected version or checksum.
