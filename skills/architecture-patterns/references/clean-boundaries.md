# Clean Boundaries

Use this reference when an architecture decision needs explicit layer responsibilities, dependency direction, interface placement, or cross-boundary tests. Apply it to the repository's actual modules and terminology.

## Boundary Model

A common outer-to-inner arrangement is:

- handlers or adapters own transport parsing, protocol errors, and response formatting
- services or use cases own business rules, validation, and orchestration
- repositories and gateways own persistence and external IO
- domain models own entities, values, invariants, and domain behavior

Choose different names when the repository already has stable terms. Focus on ownership when choosing layers.

## Dependency Direction

- Dependencies point toward stable domain behavior; outer boundaries own transport, persistence, and framework details.
- Cross-boundary calls use a caller-owned contract when an outward dependency would otherwise reverse dependency direction.
- Infrastructure implements the contract required by the inner caller.
- Constructor or explicit parameter injection makes required dependencies and lifetimes visible.
- Add layers or interfaces that isolate real variation, an ownership boundary, or a caller-visible test contract.

## Interface Placement

Place an interface beside the behavior that consumes it when its purpose is to protect that caller from an outward dependency. Place a shared contract at a module boundary only when multiple callers genuinely own the same semantics. Keep persistence DTOs, transport schemas, and framework types out of domain behavior unless they are themselves the approved contract.

## Responsibility Checks

- Handlers stay thin; services or use cases own business rules.
- Services use contracts independent of framework-specific request or persistence types.
- Services or use cases own business policy; repositories own persistence.
- Repositories and gateways own external IO; domain models own domain behavior.
- Mapping happens at the boundary that owns the external representation.

## Cross-Boundary Tests

- Test services or use cases behaviorally through fakes or in-memory implementations of caller-owned contracts.
- Test repositories and gateways against realistic integration boundaries.
- Keep handler tests focused on routing, parsing, authorization handoff, and serialization.
- Add contract or component tests where independently changing sides need the same executable boundary evidence.
- Place each behavior assertion at the layer that provides its strongest relevant evidence.

Treat these checks as architecture evidence. Concrete fixture, environment, and CI ownership remains with `testing-strategy`, while language-specific test tooling remains with the matching language guideline.
