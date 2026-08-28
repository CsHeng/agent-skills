---
name: design-change
description: "Use before implementation planning to classify change scope, truth impact, boundary impact, and the appropriate design depth."
---

# Design Change

Define an implementation-independent change boundary before planning.

## Use This Skill When

- the user wants to shape a concrete change before implementation
- the request may affect stable truth, public boundaries, architecture, or operating semantics
- goals, non-goals, acceptance conditions, ownership, or recovery need an explicit decision

Do not use it for read-only project explanation, an already approved design, implementation, or a standalone review request.

## Design

1. Establish the relevant current truth and the concrete problem.
2. Classify truth impact and boundary impact; choose `no-design`, `design-lite`, or `design-full` without equating file count with risk.
3. Run a bounded clarification loop when goals, terminology, owners, constraints, non-goals, or acceptance conditions are unresolved.
4. Compare viable boundary choices only when the change creates or materially alters a persisted architecture boundary. Compose `architecture-patterns` for that decision.
5. Record the chosen scope, explicit non-goals, future phases, acceptance evidence, truth impact, recovery policy, and implementation surface.
6. Produce a stable, reviewable design artifact when the chosen depth requires one.
7. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
8. When review is required, invoke one bounded `review-change` evaluation before accepting the design, adjudicate its read-only candidate findings here, and apply at most one focused in-scope repair before rechecking the affected evidence.

## Decision States

- `ready_for_approval`: the design and any required review evidence are complete
- `needs_more_design`: a required design decision remains unresolved
- `split_scope`: the proposed milestone is not one coherent design surface
- `manual_checkpoint`: progress depends on a user or external decision

Approval belongs to the user. Do not mark a design approved from review success alone, infer approval from a later implementation request, or continue into planning unless the request already authorizes that next step.

## Artifact Guidance

A design artifact should make these items easy to find:

- objective, current truth, and constraints
- scope, non-goals, and future phases
- chosen boundary and discarded material alternatives
- acceptance evidence and truth impact
- recovery policy and any exact approval-sensitive action
- review decision and, when review ran, its verdict and adjudication summary
- approval status

Use guarded rollback only when a concrete hazard makes it safer than forward repair and the trigger, target, and verification are explicit. Otherwise prefer fix-forward recovery.

Keep Markdown paragraphs and list items naturally unwrapped. When a document has several independent scopes, use stable unique labels rather than restarting ambiguous numbered lists.

When the user explicitly asks to grill, stress-test, harden, challenge, or interrogate a design or plan, read `references/stress-test-mode.md`.
