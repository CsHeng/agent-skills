# Candidate Evidence

Use this matrix for every simplification candidate that might remove a concept, branch, adapter, layer, or durable state.

## Evidence Matrix

| Boundary | Questions | Strong evidence |
| --- | --- | --- |
| Identity and ownership | What stable candidate ID, class, exact scope, and current owner identify this cut? Is the removal unit a whole concept or an exact representation? | One bounded removal unit and accountable authored owner are traced across every generated, compatibility, or alternate form without conflating the concept with a representation. |
| Responsibility | What responsibility does the broader concept carry? When the conditional gate applies, what does the exact representation contribute independently, and who owns each responsibility? Where else is either behavior implemented? | Entry points, call graph, state transitions, tests, contracts, and generated ownership distinguish the concept responsibility from the representation responsibility rather than inferring one from the other. |
| Consumers and liveness | Which production, test, documentation, generated, dynamic-entrypoint, public API, persisted-data, wire-format, migration, compatibility, vendored, fixture, public-package, operator, plugin, or external-caller surfaces depend on it? What does that evidence establish about current reachability rather than owner intent? | Direct caller and service-reachability traces, dependency graphs, configuration inventories, protocol contracts, package manifests, fixtures, loaders, and repository history bound the liveness claim to searched surfaces and distinguish consumption of the concept from consumption of each representation. |
| Exact representation requirement when non-consumption matters | If low or absent consumption materially supports the cut, does current approved truth require the exact concept or representation, require only the broader concept, or require neither? | Stable ownership truth, current contracts, explicit deprecation or replacement, completed migration evidence, and accountable history distinguish a redundant representation from incomplete wiring or unresolved intent; search silence alone is not decisive. |
| Behavior loss | What observable behavior or guarantee would the cut remove? Does accepting that loss require a product decision? | Before-state behavior, negative guarantees, product ownership, and explicit decision authority are named. |
| Rationale and history | Why does the surface exist, and what evidence preserves or defeats that reason now? | Current stable truth, change history, compatibility policy, incidents, and owner evidence agree. |
| Compatibility | Is the surface public, serialized, versioned, migrated, or retained for older consumers? | Compatibility policy, deprecation state, release history, adapters, and fixture formats. |
| Durability | Does it protect persisted data, retries, idempotency, audit trails, recovery, or restart behavior? | Storage schemas, migration paths, replay tests, failure-path tests, and operational procedures. |
| Trust | Does it enforce validation, authorization, isolation, redaction, provenance, or tamper evidence? | Security contracts, negative tests, threat boundaries, and audit requirements. |
| Change pressure | Is the apparent duplication temporary convergence, an active migration, or stable accidental complexity? | Recent history, open transition paths, owner statements in stable truth, and repeated change patterns. |
| Net reduction | After replacement glue, tests, documentation, generated artifacts, and dependency lifecycle are counted, is the system materially cheaper to maintain? | A bounded before-and-after ownership and maintenance inventory shows a net reduction. |
| Verification | What independent oracle could prove the smaller shape preserves behavior? | Existing contract, component, workflow, or runtime oracle with a clear diagnosis owner. |

## Conditional Intent-Evidence Gate

Apply this gate only when the removal case materially depends on low or absent consumption.

1. State whether the candidate removes the underlying concept or only an exact authored, generated, compatibility, serialized, or other representation. State the broader concept's responsibility and owner separately from the exact representation's independent responsibility and owner, and name all forms in that owned removal unit.
2. Interpret consumption as liveness evidence within the searched boundaries. Consumption of any representation may keep the concept live; it does not prove that every other representation is independently required. Low or absent consumption is not deletion proof. Classify that evidence explicitly as confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence.
3. Establish whether approved current truth requires the exact representation, requires only the broader concept, or provides no current requirement. If the exact representation is current canonical truth but has no consumer or enforcer, treat that as incomplete wiring and `reject` the cut without designing the repair. If exact ownership, requirement, canonical status, or external compatibility remains unresolved, use `defer-for-evidence`. Historical presence or a useful surrounding concept does not by itself protect every representation.
4. If a candidate combines independently removable concepts or representations with different owners, liveness, requirement evidence, boundaries, decisive oracles, or likely dispositions, split it and evaluate each part separately. Keep an authored source and mechanically generated projections together when they are one removal unit, but name each form and its ownership chain.

This gate refines evidence for the existing four dispositions; it creates no additional disposition. It does not apply when removal is justified independently of low or absent consumption, such as a proven behavior-preserving collapse of actively used duplication.

## Decision Rules

- Use `recommend-design` only when all protected boundaries have affirmative evidence and a verification path. When the gate applies, evidence must show that the broader concept remains correctly owned without the representation and no current contract requires that exact representation.
- Use `reject` when the cut loses required behavior, has no net maintenance reduction, or conflicts with evidence that the exact concept or representation remains owned or canonical.
- Use `defer-for-evidence` when one named dependency, migration decision, ownership fact, exact representation requirement, canonical-source question, or external compatibility fact blocks a safe conclusion.
- Use `no-safe-cut` when missing evidence cannot be obtained within the audit scope, concept and representation cannot be safely separated, or the complexity carries required behavior.
- Do not infer safety or intent from low line count, few visible callers, passing unit tests alone, search silence, or aesthetic preference.

## Candidate Record

```text
candidate ID:
candidate class:
exact scope:
removal level (concept or exact representation):
current owner and representation ownership chain:
location:
broader concept responsibility and owner:
exact representation responsibility and owner when the conditional gate applies:
complexity signal:
exact cut or collapse:
consumer evidence:
liveness interpretation (confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence when the conditional gate applies):
exact representation requirement evidence when the conditional gate applies:
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
