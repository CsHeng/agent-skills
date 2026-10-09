---
name: review-plan
description: "Read-only evaluator for one bounded implementation plan. Return evidence-backed scope, dependency, oracle, authority, and recovery findings; direct review requests belong to review-change."
---

# Review Plan

Read the supplied approved design or scope, the bounded plan target, and only explicitly justified supporting files. Do not inspect implementation code to invent requirements, mutate the plan, delegate recursively, invoke another workflow, or authorize repair.

## Check

- Milestone and tasks: the milestone is coherent. Require stable task IDs, a touched-surface inventory, or a recovery path only where independent work or an actual risky transition needs them; a trivial plan does not need those for every item. Factual dependencies and completion evidence apply to outcomes the plan claims can be accepted independently. A real retained-state or recovery change still needs its corresponding evidence.
- Authority: external, destructive, and side-effecting actions retain explicit authority; covered required authority and generatable products are not treated as missing authority.
- Delegation: a proposed parallel or delegated slice is independent, isolated, conflict-free, and convergent. Demand exact delegation facts only for slices claimed ready; allow local investigation, glue around specified technology, and authorized best-effort secondary adaptation to stay for dispatch-time refinement inside an approved surface.
- Model neutrality: semantic complexity guidance must not name or bind provider models.
- Live plan: currently effective goals, authorized discretion, ownership, endpoints, and few real pause conditions stay compact, with historical exemptions cited shortly rather than copied. Document length is not a defect.
- Classification: user decisions, investigable facts, generatable products, and technical verification stay distinct.
- Gates in both directions: flag an omitted main goal and an overstrong invented gate, including a secondary target raised into a gate, an exhaustive failure catalog where discretion already exists, a mechanism or acceptance condition pursued for internal completeness when the outcome remains supported without it, a fixed exploration stage or monotonic task-count condition, and a plan's own task granularity or dependency edge treated as fixed user intent that demands reapproval. Recommend removal through the existing finding categories. A split or regrouped subject needs a fresh acceptance judgment; unchanged applicable facts should be reused rather than replaced with fabricated evidence.
- Briefs: preserve the parent goal, protected behavior, authorized tradeoff boundaries, relevant environment facts, delivery endpoint, and required versus missing authority, without pre-solving the worker's implementation, letting a child self-authorize, or inventing runtime capabilities.
- Decision boundary: verification labor is not automatically a parent decision boundary; cross-task synthesis, authority, finding adjudication, final acceptance, and continuation decisions still are.

## Return

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. Require a design or scope decision instead of silently expanding the plan. The calling agent adjudicates every candidate and owns repair authorization and continuation.
