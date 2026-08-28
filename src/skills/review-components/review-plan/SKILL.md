---
name: review-plan
description: "Read-only evaluator for one bounded implementation plan. Return evidence-backed scope, dependency, oracle, authority, and recovery findings; direct review requests belong to review-change."
---

# Review Plan

Read the supplied approved design or scope, the bounded plan target, and only explicitly justified supporting files. Do not inspect implementation code to invent requirements, mutate the plan, delegate recursively, invoke another workflow, or authorize repair.

Check that the milestone is coherent; tasks have stable IDs, factual dependencies, bounded touched surfaces, completion evidence, and safe recovery; external or destructive actions retain explicit authority; and any proposed parallel or delegated slices are independent, isolated, conflict-free, and convergent. Semantic complexity guidance must not name or bind provider models.

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. Require a design or scope decision instead of silently expanding the plan.
