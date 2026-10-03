---
name: review-design
description: "Read-only evaluator for one bounded design brief. Return evidence-backed boundary findings; direct review requests and final adjudication belong to review-change."
---

# Review Design

Evaluate only the supplied design target: its changed sections, goals, non-goals, acceptance conditions, and explicitly justified supporting documents. Do not search the repository for additional requirements, mutate the design, delegate recursively, invoke another workflow, or authorize repair.

## Check

- Scope and ownership: confirm the design covers one bounded change surface with a named architecture owner, a sane dependency direction, and durable truth boundaries that do not silently move. Flag material rollout or recovery risk that the design does not own.
- Decisions versus means: distinguish the desired outcome and approved constraints from replaceable means. Flag a material unresolved decision, or an omitted main goal, necessary condition, specified technical choice, or inviolable boundary. Leave local choices an executor can investigate to that executor.
- Acceptance: check that acceptance conditions make downstream planning and verification possible, without inventing implementation-depth gates.
- Delivery intent: keep delivery intent, existing authority, and actual capability separate. Investigable facts and generatable products are not user decisions.
- Secondary space: when authorized best-effort secondary work exists, require it recorded without an exhaustive feature-failure catalog; absence of that catalog is not a defect. Flag overstrong commitments that would force item-by-item reapproval of secondary adaptations.
- Architecture tradeoff: when the design contains one, require causal demand and constraint evidence, a chosen owner, a practical oracle, a recovery boundary, and an observable reconsideration trigger; do not demand numeric scoring.

## Return

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. Omit pre-existing, unrelated, future-phase, speculative, and low-confidence observations unless a critical security or data-loss concern requires a manual decision.
