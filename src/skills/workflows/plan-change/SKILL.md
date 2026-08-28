---
name: plan-change
description: "Use after approved design or scope to create an execution-grade plan with task order, dependencies, verification, authority boundaries, and recovery policy."
---

# Plan Change

Turn an approved design or explicit bounded scope into an implementation plan another capable agent can follow.

## Use This Skill When

- an approved design or boundary decision needs ordered implementation work
- touched surfaces, dependencies, verification, authority, or recovery must be decided before mutation
- the work may benefit from explicitly independent task groups or delegated slices

Do not use it while design or approval is unresolved, to implement an existing plan, or for a standalone review request.

## Plan

1. Load the approved design or bounded scope and preserve its decisions.
2. Clear non-automatable prerequisites before presenting an execution-ready plan. Report unresolved account, login, access, credential, license, or physical prerequisites as `manual_checkpoint`; never hide them inside implementation tasks.
3. Split the work into stable task IDs with explicit factual dependencies, bounded objectives, touched files or surfaces, completion conditions, and concrete verification.
4. State required authority for external mutation, destructive actions, live cutovers, commits, publication, or deployment. Planning does not grant that authority.
5. Choose executable or substitute evidence for each task. Compose `executable-oracle-architecture-selector` when correctness needs an explicit oracle strategy, and `testing-strategy` when that strategy needs concrete test lanes.
6. State fix-forward or an explicitly guarded recovery policy for each risky task.
7. Identify parallel or delegable work only when dependencies are frozen, writes and shared resources do not conflict, isolation is safe, and convergence ownership is clear. Otherwise keep the plan serial.
8. Check work-package readiness and artifact coherence.
9. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
10. When review is required, invoke one bounded `review-change` evaluation before accepting the plan, adjudicate its read-only candidate findings here, and apply at most one focused in-scope repair before rechecking the affected evidence.

## Conditional Decisions

Use `language-decision-tree` only when a task creates or replaces a persisted project, service, tool, or automation boundary. Record the selected language and rationale only for affected tasks.

When the approved design contains an architecture decision, reference it and plan reversible implementation increments, ownership, oracles, and observable upgrade triggers. Do not rescore the design during planning. Return `needs_design_decision` if current evidence invalidates an approved design premise.

## Plan Guidance

An execution-grade plan should record:

- milestone objective, non-goals, and future phases
- task IDs, dependencies, scope slices, and touched surfaces
- completion conditions and verification commands or evidence
- explicit authority boundaries and prerequisite status
- serial order or safely independent named groups
- delegation eligibility and isolation expectations when useful
- recovery policy and any guarded rollback trigger
- truth-sync targets when stable truth will change
- review decision and, when review ran, its verdict and adjudication summary
- approval status and any remaining user decisions

Use semantic capability descriptions rather than provider names or exact model settings. A plan may describe task complexity or desired independence, but must not prescribe how a particular product schedules actors, binds models, records attempts, or resumes sessions.

## Decision States

- `ready_for_approval`: the plan and any required review evidence are complete
- `needs_design_decision`: the approved design is no longer sufficient
- `split_scope`: the milestone cannot remain one bounded execution package
- `manual_checkpoint`: a prerequisite or authority decision blocks readiness

Approval belongs to the user. Review success does not authorize implementation, and an implementation request does not retroactively approve an unresolved plan.
