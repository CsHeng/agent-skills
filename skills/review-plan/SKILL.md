---
name: review-plan
description: "Controller-selected plan evaluator for a bounded review brief. Return candidate DAG, scope, oracle, and recovery findings only; direct review intent belongs to review-change."
---

# Review Implementation Plan

Run only when `review-change` selects this evaluator for a plan review. Decide whether the supplied current-milestone plan can safely enter execution and return candidate findings; do not own direct review intent or future phases.

## Actor Contract

- Prefer a reviewer subagent for a non-trivial plan when the main agent can delegate.
- Permit direct main-agent review for small plans or when delegation is unavailable.
- The bounded review brief declares `actor_role: main | delegated`.
- A delegated reviewer must not delegate recursively, edit the plan, call lifecycle controllers, or authorize repairs.

## Bounded Review Brief

Require:

- plan path, current milestone objective, and exact changed plan sections or diff
- approved upstream `design_ref` and `design_version`
- approved scope, non-goals, future phase, and implementation surface
- task DAG and dependency state
- plan contract version, named parallel groups, batch limits, delegation policy, semantic execution and reasoning profiles, isolation, resource locks, and runtime model-policy options
- acceptance oracles, task failure policies, guarded-rollback metadata when present, and execution-continuity declarations
- the approved architecture decision reference, reversible staging, and upgrade triggers when the upstream design carries architecture economics
- explicitly allowed supporting files, each with a reason

Read the upstream design first, then the plan. Read no other files unless the brief names them or they are direct dependencies required to validate a changed plan claim. Do not inspect implementation code to invent plan requirements.

## Review Concerns

- one executable milestone objective with explicit non-goals
- scope contained by the approved design
- dependency-complete task order and ownership
- version-2 enum and cross-field validity, or an explicit legacy compatibility path
- dependency-frozen parallel groups with no peer dependency, writable-path overlap, shared resource lock, or unisolated concurrent write
- model-policy topology invariance: `semantic-routing`, `inherit-main`, and `runtime-default` may change runtime binding but not the approved DAG or safety boundary
- conservative capacity behavior: `allowed` work may serialize with evidence, while unavailable `required` work has a typed stop
- executable oracle or declared substitute for behavior-changing tasks
- recovery-policy and authority boundaries
- `Work Package Readiness` and `Execution Continuity` consistency
- fidelity to the approved architecture decision, including bounded reversible staging and preserved upgrade triggers

Do not rerun or rescore architecture selection. If the plan changes the approved demand, constraint, owner, hard requirement, chosen boundary, or upgrade trigger, return a design-decision candidate rather than treating the change as local plan repair.

Do not block on exact command flags, fixture contents, dashboard details, cleanup polish, or low-level decisions that can be made inside an approved task without changing its boundary.

## Candidate Finding Contract

Each material candidate includes:

- `location`, `evidence`, and concrete `impact`
- `causal_class`: `introduced_by_change | regressed_by_change | activated_by_change | pre_existing | unrelated`
- `violated_contract`: the exact approved design, readiness, DAG, oracle, recovery-policy, or continuity rule
- `confidence`: `high | medium | low`
- `smallest_fix`
- `recommended_disposition`

Only causally linked, high-confidence defects that prevent executing the current milestone are eligible blockers. Future-phase concerns, implementation-level hardening, pre-existing debt, unrelated observations, and low-confidence suggestions are non-blocking. If the plan requires a design, authority, or scope change, return a manual decision candidate instead of inventing a local repair.

Prefer PASS when the plan has a bounded executable DAG, sufficient oracles, correct ownership, safe declared concurrency, portable routing advice, a fix-forward or explicitly guarded recovery policy, and explicit execution continuity. Do not require concrete provider model identifiers, blanket parallelism, or rollback machinery for a `fix_forward` task.

## Output

Return:

- `verdict: pass | candidate-findings | manual-decision-required`
- `review_surface` with reasons for supporting files
- `candidate_findings`
- `pass_rationale` when passing

The main agent adjudicates candidate findings and owns any plan repair.
