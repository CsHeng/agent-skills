---
name: review-implementation
description: "Controller-selected implementation evaluator for an exact task diff and bounded review brief. Return causality-qualified candidate findings only; direct review intent belongs to review-change, and lifecycle controllers own repair."
---

# Review Implementation

Run only when `review-change` or `implement-change` selects this evaluator with a bounded implementation brief. Judge the exact task diff and return candidate findings; do not own direct review intent, repair, or repository-wide audit.

## Actor Contract

- The main agent should prefer a reviewer subagent for non-trivial implementation review when delegation is available.
- The main agent may review directly for a small mechanical diff or when delegation is unavailable.
- The bounded review brief declares `actor_role: main | delegated`.
- A delegated reviewer must not delegate recursively, edit files, call lifecycle workflows, or authorize repair.

## Bounded Review Brief

Require:

- approved task-slice objective and non-goals
- acceptance criteria, invariants, and executable oracles
- exact changed files and diff for the task slice
- task-scoped tests and verification evidence
- approved touch set
- exact external refs and metadata-only root-before/final-after, ordered intent, preserved-mode/owner/identity, and redacted conformance evidence when the task used the external channel
- a small supporting-file allowlist, with one reason per file

Do not read a live external target, request raw external configuration or preimages, inspect staged payloads, or suggest a generic editor. External review is limited to the controller-supplied metadata-only evidence. The evaluator remains read-only; an accepted repair can only be adjudicated by the main controller and executed as the next parent-linked broker intent within the same exact ref set.

Review changed behavior and the supplied tests. Read an unchanged file only when it is a direct dependency of changed behavior and is necessary to decide whether the diff is correct. Record that reason in `review_surface`. Do not follow references recursively, inspect future plan tasks, or search the repository for adjacent debt.

## Causality

Classify every material candidate:

- `introduced_by_change`: the current diff creates the defect
- `regressed_by_change`: the current diff breaks previously correct behavior
- `activated_by_change`: the diff newly places pre-existing behavior on the approved active path
- `pre_existing`: the issue existed and the diff neither worsens nor activates it
- `unrelated`: the observation is not caused by the task slice

Only the first three classes are eligible for current repair. `activated_by_change` requires evidence that the diff newly executes, exposes, or relies on the behavior. Moving, renaming, formatting, archiving, or relabeling unchanged code does not itself activate pre-existing defects.

## Blocking Eligibility

A candidate is eligible to block only when it:

- is inside the bounded review surface
- has qualifying causality tied to a changed line or behavior
- violates a named task requirement, acceptance criterion, invariant, or oracle
- has a concrete material consequence
- has sufficient evidence and confidence
- has a smallest valid fix inside the approved task slice and touch set

Low-confidence findings never authorize automatic repair. Pre-existing, unrelated, future-phase, general-hardening, stylistic, and plan-expanding concerns are non-blocking and should normally be omitted. A critical incidental security or data-loss observation outside scope may be escalated to the main agent, but it must not be labeled current-scope repair.

Prefer PASS when the approved behavior and declared oracles are satisfied. Do not report possible issues merely to be defensive, and do not optimize for exhaustive finding discovery.

## Candidate Output

Return:

- `verdict: pass | candidate-findings | manual-decision-required`
- `review_surface`: every file read and why
- `candidate_findings`, each with `location`, `evidence`, `impact`, `causal_class`, `violated_contract`, `confidence`, `smallest_fix`, and `recommended_disposition`
- `pass_rationale` when passing

Candidate findings are advisory evidence. The main agent independently assigns their final disposition and only the lifecycle controller may repair accepted findings.
