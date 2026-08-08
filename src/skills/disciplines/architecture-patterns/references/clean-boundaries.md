# Clean Boundaries

Use this reference when an architecture decision needs explicit layer responsibilities, dependency direction, interface placement, or cross-boundary tests. Apply it to the repository's actual modules rather than forcing the example layer names onto every system.

## Boundary Model

A common outer-to-inner arrangement is:

- handlers or adapters own transport parsing, protocol errors, and response formatting
- services or use cases own business rules, validation, and orchestration
- repositories and gateways own persistence and external IO
- domain models own entities, values, invariants, and domain behavior

Choose different names when the repository already has stable terms. The important property is ownership, not the number of layers.

## Dependency Direction

- Dependencies point toward stable domain behavior; inner policy does not import transport, persistence, or framework details.
- Cross-boundary calls use a caller-owned contract when an outward dependency would otherwise reverse dependency direction.
- Infrastructure implements the contract required by the inner caller.
- Constructor or explicit parameter injection makes required dependencies and lifetimes visible.
- Do not add pass-through layers or interfaces that isolate no real variation, ownership boundary, or caller-visible test contract.

## Interface Placement

Place an interface beside the behavior that consumes it when its purpose is to protect that caller from an outward dependency. Place a shared contract at a module boundary only when multiple callers genuinely own the same semantics. Keep persistence DTOs, transport schemas, and framework types out of domain behavior unless they are themselves the approved contract.

## Responsibility Checks

- Handlers stay thin and do not own business rules.
- Services do not depend on framework-specific request or persistence types.
- Repositories do not decide business policy.
- Domain models do not perform unowned IO.
- Mapping happens at the boundary that owns the external representation.

## Cross-Boundary Tests

- Test services or use cases behaviorally through fakes or in-memory implementations of caller-owned contracts.
- Test repositories and gateways against realistic integration boundaries.
- Keep handler tests focused on routing, parsing, authorization handoff, and serialization.
- Add contract or component tests where independently changing sides need the same executable boundary evidence.
- Avoid duplicating the same behavior assertion at every layer.

Treat these checks as architecture evidence. Concrete fixture, environment, and CI ownership remains with `testing-strategy`, while language-specific test tooling remains with the matching language guideline.
