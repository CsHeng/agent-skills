---
name: review-design
description: "Read-only evaluator for one bounded design brief. Return evidence-backed boundary findings; direct review requests belong to review-change, and final adjudication stays with the calling agent."
---

# Review Design

Evaluate only the design target and review scope supplied by the caller: the requested artifact or diff, its goals, non-goals, acceptance conditions, and explicitly justified supporting documents. Do not search the repository for additional requirements, mutate the design, delegate recursively, invoke another workflow, or authorize repair. Final adjudication, repair authorization, and continuation decisions stay with the calling agent; this evaluator only returns candidate findings.

For a whole-design target, defects anywhere in the supplied artifact are in scope, regardless of whether they predate the current change. For an explicitly diff-scoped target, a blocking candidate must be caused or newly activated by that diff; supporting context does not expand the target to unrelated pre-existing defects.

## Check

- Scope and ownership: confirm the design covers one bounded change surface with a named architecture owner, a sane dependency direction, and durable truth boundaries that do not silently move. Flag material rollout or recovery risk that the design does not own.
- Decisions versus means: distinguish the desired outcome and approved constraints from replaceable means. Judge whether a proposed mechanism or acceptance condition is necessary before improving its internal completeness, and recommend removal through the existing finding categories when the outcome remains supported without it. Flag a material unresolved decision, or an omitted main goal, necessary condition, specified technical choice, or inviolable boundary. Leave local choices an executor can investigate to that executor. A real retained-state or recovery boundary still needs its corresponding evidence; deployment wording alone does not require a restoration platform.
- Acceptance: check that acceptance conditions make downstream planning and verification possible, without inventing implementation-depth gates.
- Delivery intent: keep delivery intent, existing authority, and actual capability separate. Investigable facts and generatable products are not user decisions.
- Secondary space: when authorized best-effort secondary work exists, require it recorded without an exhaustive feature-failure catalog; absence of that catalog is not a defect. Flag overstrong commitments that would force item-by-item reapproval of secondary adaptations.
- Architecture tradeoff: when the design contains one, require causal demand and constraint evidence, a chosen owner, a practical oracle, a recovery boundary, and an observable reconsideration trigger; do not demand numeric scoring.

## Return

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. Omit unrelated, future-phase, speculative, and low-confidence observations unless a critical security or data-loss concern requires a manual decision.
