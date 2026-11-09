---
name: review-design
description: "Read-only evaluator for one bounded design brief. Return evidence-backed boundary findings; direct review requests belong to review-change, and final adjudication stays with the calling agent."
---

# Review Design

Evaluate only the supplied design target and brief under the finding rules, causal scope, and verdict in `review-change`. For a whole-design target, defects anywhere in the artifact are in scope; for a diff-scoped target, a blocking candidate is caused or newly activated by that diff.

## Design-Specific Checks

- Scope and ownership: one bounded change surface with a named owner, a sane dependency direction, and durable truth boundaries that stay put; flag material rollout or recovery risk outside the design's ownership.
- Decisions versus means: a material unresolved decision, or an omitted main goal, necessary condition, specified technical choice, or inviolable boundary. Local choices an executor can investigate stay with the executor.
- Acceptance and cutover: success is verifiable, with switching prerequisites limited to those needed for cutover; coexistence, qualification environments, rollback systems, and observation windows cite a concrete protected interest, per the replacement-and-cutover reference in `development-standards`.
- Delivery intent: delivery intent, existing authority, and actual capability stay separate; facts material to feasibility or protected boundaries are preserved in the design or an accessible owner record, with supplied facts distinct from assumptions.
- Secondary space: authorized best-effort secondary work is recorded at a useful level of detail; commitments that would force item-by-item reapproval are flagged.
- Architecture tradeoff: demand, constraints, ownership, and practical evidence support the choice; recovery or reconsideration detail appears where a concrete risk or unsettled premise needs it.
