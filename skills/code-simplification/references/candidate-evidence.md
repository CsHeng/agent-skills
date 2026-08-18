# Candidate Evidence

Use this matrix for every simplification candidate that might remove a concept, branch, adapter, layer, or durable state.

## Evidence Matrix

| Boundary | Questions | Strong evidence |
| --- | --- | --- |
| Identity and ownership | What stable candidate ID, class, exact scope, and current owner identify this cut? | One bounded surface and accountable owner can be traced across authored and projected forms. |
| Responsibility | What behavior does the current code own? Where else is that behavior implemented? | Entry points, call graph, state transitions, tests, and generated ownership agree on one responsibility. |
| Consumers | Which production, test, documentation, generated, dynamic-entrypoint, public API, persisted-data, wire-format, migration, compatibility, vendored, fixture, public-package, operator, plugin, or external-caller surfaces depend on it? | Direct caller and service-reachability traces, dependency graphs, configuration inventories, protocol contracts, package manifests, fixtures, loaders, and repository history. |
| Behavior loss | What observable behavior or guarantee would the cut remove? Does accepting that loss require a product decision? | Before-state behavior, negative guarantees, product ownership, and explicit decision authority are named. |
| Rationale and history | Why does the surface exist, and what evidence preserves or defeats that reason now? | Current stable truth, change history, compatibility policy, incidents, and owner evidence agree. |
| Compatibility | Is the surface public, serialized, versioned, migrated, or retained for older consumers? | Compatibility policy, deprecation state, release history, adapters, and fixture formats. |
| Durability | Does it protect persisted data, retries, idempotency, audit trails, recovery, or restart behavior? | Storage schemas, migration paths, replay tests, failure-path tests, and operational procedures. |
| Trust | Does it enforce validation, authorization, isolation, redaction, provenance, or tamper evidence? | Security contracts, negative tests, threat boundaries, and audit requirements. |
| Change pressure | Is the apparent duplication temporary convergence, an active migration, or stable accidental complexity? | Recent history, open transition paths, owner statements in stable truth, and repeated change patterns. |
| Net reduction | After replacement glue, tests, documentation, generated artifacts, and dependency lifecycle are counted, is the system materially cheaper to maintain? | A bounded before-and-after ownership and maintenance inventory shows a net reduction. |
| Verification | What independent oracle could prove the smaller shape preserves behavior? | Existing contract, component, workflow, or runtime oracle with a clear diagnosis owner. |

## Decision Rules

- Use `recommend-design` only when all protected boundaries have affirmative evidence and a verification path.
- Use `reject` when the cut loses required behavior or has no net maintenance reduction.
- Use `defer-for-evidence` when one named dependency or migration decision blocks a safe conclusion.
- Use `no-safe-cut` when missing evidence cannot be obtained within the audit scope or the complexity carries required behavior.
- Do not infer safety from low line count, few visible callers, passing unit tests alone, or aesthetic preference.

## Candidate Record

```text
candidate ID:
candidate class:
exact scope:
current owner:
location:
current responsibility:
complexity signal:
exact cut or collapse:
consumer evidence:
behavior or guarantees lost:
product decision required:
rationale and history evidence:
protected invariants:
compatibility and durability evidence:
trust and recovery evidence:
net maintenance reduction:
confidence:
risk:
unresolved evidence:
smallest decisive oracle:
disposition:
```

If implementation is requested, hand the accepted candidate to `design-change`. This audit does not authorize mutation or choose the implementation plan.
