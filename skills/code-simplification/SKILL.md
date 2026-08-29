---
name: code-simplification
description: "Use for read-only, evidence-first audits that identify behavior-preserving code simplifications from current repository truth, consumer evidence, compatibility history, and trust or durability boundaries. Do not use for applying refactors, ordinary implementation cleanup, performance-only tuning, or review limited to the current diff."
---

# Code Simplification

Identify code that can become smaller or clearer without changing owned behavior. Return audit evidence only; do not edit files, create a plan implicitly, or delegate the audit.

## Authority Boundary

- Keep the audit read-only. Do not mutate the repository, generate files, run destructive commands, or spawn another agent.
- Treat behavior, public contracts, compatibility, persisted data, security, auditability, and operational recovery as protected boundaries rather than removable complexity.
- Route requests to apply a candidate or accept a product tradeoff through `design-change`. Route review of an exact current diff through `review-change`.
- Do not turn ordinary task-local cleanup, performance work, or style preferences into a repository simplification audit.

## Workflow

1. Bound the audit to the requested repository, module, or subsystem and state what is outside scope.
2. Map the current behavior before proposing removal: entry points, consumers, data flow, failure handling, persisted state, public surfaces, and generated ownership.
3. Identify generated, vendored, migration, fixture, public-package, and dynamic-loader surfaces before classifying consumers. Trace evidence from current code, tests, repository history, configuration, callers, adapters, and stable documentation. Absence from one search is not proof that a boundary is unused.
4. Identify candidates where indirection, duplication, parallel paths, compatibility layers, or defensive state exceed current demonstrated needs. Bound each candidate as removal of a concept or of an exact representation; name the authored owner and any generated or compatibility forms.
5. Evaluate each candidate with [Candidate Evidence](references/candidate-evidence.md). When the case for removal materially depends on low or absent consumption, apply its intent-evidence gate; non-consumption alone does not show that an owner intends to retire the concept or representation. Preserve uncertainty explicitly; a valid audit may conclude `no-safe-cut`.
6. Split independently removable concepts or representations into separate candidates when their ownership, consumption, intent evidence, protected boundaries, decisive oracles, or dispositions differ. Keep an authored source and its mechanical projections together when they are one owned removal unit, while naming every form.
7. Report candidates and verification needs without changing code or promising that deletion is safe.

## Candidate Dispositions

- `recommend-design`: affirmative evidence supports the exact smaller shape, shows that a retained concept remains correctly owned without the representation when the intent-evidence gate applies, and names the verification required before implementation.
- `reject`: the proposed cut would remove required behavior, conflicts with evidence that the exact concept or representation remains owned or canonical, or costs more to maintain after replacement glue, tests, docs, and generated surfaces are counted.
- `defer-for-evidence`: one named consumer, compatibility promise, migration, exact-ownership question, representation requirement, or canonical-source question prevents a safe conclusion.
- `no-safe-cut`: evidence cannot be resolved within the audit scope, protected boundaries are coupled, or the apparent complexity carries required behavior.

Do not rank candidates by line count alone. Prefer high-confidence removal of an unnecessary concept over broad cosmetic churn.

## Output

For each material candidate, record:

- a stable candidate ID, candidate class, exact scope, removal level (`concept` or exact `representation`), and current owner
- broader concept responsibility and owner, plus the exact representation's independent responsibility and ownership chain when the intent-evidence gate applies
- complexity signal and the exact proposed cut or collapse, including authored, generated, and compatibility forms in the owned removal unit
- production, test, documentation, generated, dynamic-entrypoint, public API, persisted-data, wire-format, migration, and compatibility consumers as applicable
- liveness interpretation and, when low or absent consumption materially supports removal, an explicit classification as confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence, plus whether the exact representation is required
- observable behavior or guarantees lost by the cut and whether accepting that loss requires a product decision
- rationale and history evidence that protects, defeats, or preserves the current surface
- invariants and protected boundaries that must remain true
- compatibility, persistence, security, audit, and recovery impact
- net maintenance reduction after replacement glue, tests, documentation, generated artifacts, and dependency lifecycle are counted
- confidence, risk, and unresolved evidence
- disposition
- smallest decisive executable oracle or substitute verification required before implementation

Lead with the strongest candidates and keep each record concise. Keep `no-safe-cut` conclusions when they prevent unsafe deletion; do not manufacture a quota of findings.

## Operating Rules

- Prefer concrete repository evidence over generic simplicity principles.
- Preserve generated-source ownership: audit authored sources before generated projections, and do not mistake consumption of one representation for ownership or non-consumption of the underlying concept.
- Treat consumption as liveness evidence within the searched boundaries, not as owner intent. Active consumption can defeat an unused-code rationale; low or absent consumption cannot by itself authorize removal. Reconcile it with current exact ownership and requirement evidence rather than requiring a historical retirement declaration.
- Do not describe a compatibility path as dead merely because current first-party code does not call it.
- Do not remove validation, observability, recovery, or explicit failure handling unless equivalent owned behavior is proven elsewhere.
- Keep uncertainty and rejected candidates in the report when they explain why the current structure is justified.
