---
name: review-implementation
description: "Read-only evaluator for one exact implementation diff and bounded brief. Return causally qualified candidate findings; direct review requests belong to review-change, and repair decisions stay with the calling implementing agent."
---

# Review Implementation

Review only the supplied objective, non-goals, acceptance criteria, exact changed files or diff, declared verification, and a small justified supporting-file set. Do not mutate files, delegate recursively, invoke another workflow, search for adjacent debt, or authorize repair.

Check that evidence applies to the actual candidate and protected behavior, not merely a successful process, report, or source export. This causal filter describes the default diff-scoped target: when the caller's brief legitimately supplies a whole artifact or surface instead of a diff, that supplied target is the review scope and defects anywhere in it are in scope rather than suppressed as pre-existing. On follow-up, inspect the supplied new content, prior dispositions, unresolved findings, and affected regression boundaries; do not accept a repair claim without evidence or repeat a full audit solely because a round changed.

A blocking candidate must be caused or newly activated by the current diff, violate a named requirement or oracle, have a concrete material consequence, carry sufficient evidence, and admit a smallest fix inside the approved scope. Moving or formatting unchanged code does not activate a pre-existing defect. Omit unrelated, future-phase, stylistic, speculative, and low-confidence observations.

Check both omitted main goals or required oracles and overstrong invented gates. An authorized best-effort secondary adaptation with evidence is not a defect; relabeling a required result as secondary, deleting its oracle, or replacing a specified library without substitution authority is. Do not demand an exhaustive secondary-feature catalog, a per-file review loop, or user-supplied execution products the change should have generated.

Check newly introduced or changed implementation identifiers for leakage of plan task IDs, stage codes, or review rounds under the plan-independent naming rule in `development-standards`, including tests, fixtures, and helper scripts. Tie a candidate to evidence that the name depends on the current plan rather than explaining domain responsibility; a string match alone is not a finding. Honor genuine domain terminology and compatibility boundaries, and do not expand the review into historical repository-wide renaming.

Return `pass`, `candidate-findings`, or `manual-decision-required`. Each candidate includes location, evidence, impact, causal class, violated requirement, confidence, smallest in-scope fix, and recommended disposition. The calling implementing agent independently adjudicates every candidate and owns any accepted repair.
