# Candidate Evidence

Use the required evidence below for every simplification candidate that might remove a concept, branch, adapter, layer, or durable state. Add the conditional evidence whenever its condition holds; it is then required, not optional. A candidate outside a boundary does not fill the conditional rows, but required causal, ownership, and reachability evidence is never dropped to shorten a record.

## Required Evidence

| Boundary | Questions | Strong evidence |
| --- | --- | --- |
| Identity and ownership | What stable candidate ID, class, exact scope, and current owner identify this cut? Is the removal unit a whole concept or an exact representation? | One bounded removal unit and accountable authored owner are traced across every generated, compatibility, or alternate form without conflating the concept with a representation. |
| Concept responsibility | What responsibility does the broader concept carry, and where else is that behavior implemented? | Entry points, call graph, state transitions, tests, contracts, and generated ownership establish the concept responsibility rather than inferring it from a representation. |
| Consumers and liveness | Which production, test, documentation, generated, dynamic-entrypoint, public API, persisted-data, wire-format, migration, compatibility, vendored, fixture, public-package, operator, plugin, or external-caller surfaces depend on it? What does that evidence establish about current reachability rather than owner intent? | Direct caller and service-reachability traces, dependency graphs, configuration inventories, protocol contracts, package manifests, fixtures, loaders, and repository history bound the liveness claim to searched surfaces. |
| Behavior loss | What observable behavior or guarantee would the cut remove? Does accepting that loss require a product decision? | Before-state behavior, negative guarantees, product ownership, and explicit decision authority are named. |
| Rationale and history | Why does the surface exist, and what evidence preserves or defeats that reason now? | Current stable truth, change history, compatibility policy, incidents, and owner evidence agree. |
| Change pressure | Is the apparent duplication temporary convergence, an active migration, or stable accidental complexity? | Recent history, open transition paths, owner statements in stable truth, and repeated change patterns. |
| Net reduction | After replacement glue, tests, documentation, generated artifacts, and dependency lifecycle are counted, is the system materially cheaper to maintain? | A bounded before-and-after ownership and maintenance inventory shows a net reduction. |
| Verification | What independent oracle could prove the smaller shape preserves behavior? | Existing contract, component, workflow, or runtime oracle with a clear diagnosis owner. |

## Conditional Evidence

| Boundary | Applies when | Questions | Strong evidence |
| --- | --- | --- | --- |
| Representation responsibility | the removal case materially depends on low or absent consumption | What does the exact representation contribute independently of the broader concept, and who owns each responsibility? | The exact representation's independent responsibility and ownership chain distinguish it from the broader concept. |
| Exact representation requirement | the removal case materially depends on low or absent consumption | Does current approved truth require the exact concept or representation, require only the broader concept, or require neither? | Stable ownership truth, current contracts, explicit deprecation or replacement, completed migration evidence, and accountable history distinguish a redundant representation from incomplete wiring or unresolved intent; search silence alone is not decisive. |
| Compatibility | the candidate touches a public, serialized, versioned, migrated, or retained-older-consumer surface | Is the surface public, serialized, versioned, migrated, or retained for older consumers? | Compatibility policy, deprecation state, release history, adapters, and fixture formats. |
| Durability | the candidate touches persisted data, retries, idempotency, audit trails, recovery, or restart behavior | Does it protect persisted data, retries, idempotency, audit trails, recovery, or restart behavior? | Storage schemas, migration paths, replay tests, failure-path tests, and operational procedures. |
| Trust | the candidate touches validation, authorization, isolation, redaction, provenance, or tamper evidence | Does it enforce validation, authorization, isolation, redaction, provenance, or tamper evidence? | Security contracts, negative tests, threat boundaries, and audit requirements. |

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

The following is an information checklist, not a required rendering template. Combine related facts in concise prose when that preserves the evidence; do not emit a separate label or empty section for every item. An explicit caller schema still applies. Establish which conditional boundaries the candidate touches before omitting their evidence; unresolved applicability is a limitation, not proof that a boundary is absent.

```text
Required for every candidate:
candidate ID:
candidate class:
exact scope:
removal level (concept or exact representation):
current owner:
location:
broader concept responsibility and owner:
complexity signal:
exact cut or collapse:
consumer evidence:
behavior or guarantees lost:
product decision required:
rationale and history evidence:
protected invariants:
net maintenance reduction:
confidence:
risk:
unresolved evidence:
smallest decisive oracle:
disposition:

Add only when the condition applies:
exact representation responsibility and owner (when the conditional gate applies):
liveness interpretation: confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence (when the conditional gate applies):
exact representation requirement evidence (when the conditional gate applies):
compatibility and durability evidence (required when the candidate touches that boundary):
trust and recovery evidence (required when the candidate touches that boundary):
```

If the user explicitly authorizes applying a candidate and its scope, protected behavior, and acceptance are sufficient, hand it to `implement-change`. Use `design-change` for a material unresolved tradeoff or a requested design artifact, not as a prerequisite for already settled implementation. The audit and its dispositions do not authorize mutation or choose the implementation plan.
