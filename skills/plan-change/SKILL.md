---
name: plan-change
description: "Create a requested implementation plan or resolve execution ordering, dependencies, coordination, and verification for an authorized change. Not for executing an existing plan or a bounded change that needs no separate planning artifact."
---

# Plan Change

Turn an approved design or explicit bounded scope into an implementation plan another capable agent can follow.

## Use This Skill When

- the user requests an implementation plan based on settled design or bounded scope
- execution ordering, dependencies, coordination, verification, authority, or recovery arrangements genuinely need a planning decision

A bounded authorized change can enter implementation directly when those facts are already sufficient. Potential parallelism or ordinary local technical choices do not by themselves require a separate plan. When the user requests a plan artifact, document established decisions without reopening them or proceeding into implementation.

Do not use it while a necessary design decision or scope approval is unresolved, to execute an existing plan, or for a standalone review request.

## Plan

1. Load the approved design or bounded scope and preserve its decisions.
2. Clear non-automatable prerequisites before presenting an execution-ready plan. Report unresolved account, login, access, credential, license, or physical prerequisites as `manual_checkpoint`; never hide them inside implementation tasks.
3. Split the work into stable task IDs with explicit factual dependencies, bounded objectives, touched files or surfaces, completion conditions, and concrete verification.
4. State required authority for external mutation, destructive actions, live cutovers, commits, publication, or deployment. Planning does not grant that authority.
5. Choose executable or substitute evidence for each task. Compose `executable-oracle-architecture-selector` when correctness needs an explicit oracle strategy, and `testing-strategy` when that strategy needs concrete test lanes.
6. State fix-forward or an explicitly guarded recovery policy for each risky task.
7. Identify parallel or delegable work only when dependencies are frozen, writes and shared resources do not conflict, isolation is safe, repository ownership is unambiguous, and convergence ownership is clear. Record factual predecessors without projecting them into a host task graph; ordinary delegated slices remain independent and flat. Every serial dependency between delegation-ready tasks must name the concrete predecessor artifact, shared resource, or parent-owned decision that requires the order; narrative order alone is not a dependency. Otherwise keep the plan serial.
8. Check that the objective, authorized writes, protected behavior, factual dependencies, and acceptance evidence are sufficient and coherent. They may come from existing requests or contracts; local implementation does not require delegation profiles, parallel policy, or a fixed review budget. Assess delegation readiness separately only for slices actually delegated or claimed delegation-ready.
9. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
10. When review is required, request a bounded `review-change` evaluation, adjudicate its read-only candidate findings, and repair accepted defects within the confirmed design and planning scope. Continue evidence-backed in-scope repair and affected verification without a default count limit. Use targeted rereview when prior evidence becomes stale or an independent question remains; do not reopen adjudicated findings without new evidence. Do not rewrite confirmed goals, dependencies, authority, or acceptance to make the plan pass. Stop for a concrete decision or prerequisite gap, lack of a viable path, or an explicit invocation budget, reporting the reason and incomplete work. Finish when the requested plan satisfies its requirements; further review is not a ritual.

## Conditional Decisions

Use `language-decision-tree` only when a task creates or replaces a persisted project, service, tool, or automation boundary. Record the selected language and rationale only for affected tasks.

When the approved design contains an architecture decision, reference it and plan reversible implementation increments, ownership, oracles, and observable upgrade triggers. Do not rescore the design during planning. Return `needs_design_decision` if current evidence invalidates an approved design premise.

When the user explicitly requests delegated or subagent-assisted implementation, read `references/delegation-profiles.toml`. For every task claimed ready for delegation, record one canonical execution profile, one canonical reasoning profile, one repository owner, an exact repository-relative write set, resource locks, isolation, convergence ownership, verification, completion evidence, and failure policy. Mark the task not ready or keep delegation conditional when those facts are unresolved.

A writable delegated task belongs to one repository root. Split a multi-repository milestone into repository-owned writable slices, retain cross-repository integration in the active parent, or design an explicit external boundary with its own authority and cleanup. Do not imply that one worker can mutate sibling repositories, and do not prescribe a host-specific working-directory flag, snapshot, worktree, staging path, or scheduler.

`implement-change` owns any later projection of an approved factual predecessor into a compatible host mechanism. A hard predecessor is eligible only when approved implementation order requires it and no parent-owned synthesis, authority, verification, review adjudication, repair, or continuation decision occurs between the tasks.

## Plan Guidance

An execution-grade plan should record:

- milestone objective, non-goals, and future phases
- task IDs, dependencies, scope slices, and touched surfaces
- completion conditions and verification commands or evidence
- explicit authority boundaries and prerequisite status
- serial order or safely independent named groups
- delegation eligibility, repository ownership, exact write set, resource locks, isolation, and convergence ownership when useful
- canonical execution and reasoning profiles for tasks claimed delegation-ready after an explicit delegated-implementation request
- recovery policy and any guarded rollback trigger
- truth-sync targets when stable truth will change
- review decision and, when review ran, its verdict and adjudication summary
- approval status and any remaining user decisions

Use semantic capability descriptions rather than provider names or exact model settings. The optional execution and reasoning profiles express intent, not a route binding; a compatible active host may use a default or retain the task when no mapping exists. A later explicit user-selected execution or reasoning route is invocation authority rather than plan metadata and may be preserved through ephemeral compatible-host parameters without amending the plan. It never authorizes mutation of durable route configuration. Plans that do not claim delegation readiness may omit profiles. A plan must not prescribe how a particular product schedules actors, binds models, records attempts, or resumes sessions.

## Decision States

- `ready_for_approval`: the plan and any required review evidence are complete
- `needs_design_decision`: the approved design is no longer sufficient
- `split_scope`: the milestone cannot remain one bounded execution package
- `manual_checkpoint`: a prerequisite or authority decision blocks readiness

Approval belongs to the user. Review success does not authorize implementation, and an implementation request does not retroactively approve an unresolved plan.
