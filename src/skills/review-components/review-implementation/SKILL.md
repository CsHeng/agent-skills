---
name: review-implementation
description: "Read-only evaluator for one exact implementation diff and bounded brief. Return causally qualified candidate findings; direct review requests and all repair decisions belong to review-change and the implementing agent."
---

# Review Implementation

Review only the supplied objective, non-goals, acceptance criteria, exact changed files or diff, declared verification, and a small justified supporting-file set. Do not mutate files, delegate recursively, invoke another workflow, search for adjacent debt, or authorize repair.

A blocking candidate must be caused or newly activated by the current diff, violate a named requirement or oracle, have a concrete material consequence, carry sufficient evidence, and admit a smallest fix inside the approved scope. Moving or formatting unchanged code does not activate a pre-existing defect. Omit unrelated, future-phase, stylistic, speculative, and low-confidence observations.

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. The calling implementing agent independently adjudicates every candidate and owns any accepted repair.
