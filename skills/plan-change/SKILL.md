---
name: plan-change
description: "Create a requested implementation plan or resolve execution ordering, dependencies, coordination, verification, authority, or delivery endpoints for an authorized change. Not for executing an existing plan or a bounded change that needs no separate planning artifact."
---

# Plan Change

Turn an approved design or explicit bounded scope into a self-contained implementation plan a fresh main agent can follow. Optimize accepted end-to-end delivery time within the quality, authority, and budget boundaries, not token count, dispatch count, or keeping the parent continuously coding.

## Use This Skill When

- the user requests an implementation plan based on settled design or bounded scope
- execution ordering, dependencies, coordination, verification, authority, delivery endpoints, or recovery arrangements genuinely need a planning decision

A bounded authorized change can enter implementation directly when those facts are already sufficient. Potential parallelism or ordinary local technical choices do not by themselves require a separate plan. When the user requests a plan artifact, document established decisions without reopening them or proceeding into implementation.

Do not use it while a necessary design decision or scope approval is unresolved, to execute an existing plan, or for a standalone review request.

## Plan

1. Load the approved design or bounded scope and preserve its decisions.
2. Clear non-automatable prerequisites before presenting an execution-ready plan. Report unresolved account, login, access, credential, license, or physical prerequisites as `manual_checkpoint`; never hide them inside implementation tasks.
3. Split the work into stable task IDs with explicit factual dependencies, bounded objectives, ownership, completion conditions, and concrete verification. Distinguish binding goals, acceptance, authority, and explicitly fixed restrictions from planning observations such as likely touch files, Git revisions, or environment snapshots. Record known surfaces and resources as refinable context unless they are intentionally hard boundaries; leave remaining local investigation, glue around specified technology, and already-authorized best-effort secondary adaptation to the executor instead of inventing exact paths or pre-enumerating every secondary failure. Ordinary implementation is not blocked by missing delegation metadata.
4. Separate whether an action belongs to this task, whether required authority is already covered or still missing, and whether current capability can perform it. Distinguish user decisions, investigable facts, implementation products to generate, and technical verification. State the useful delivery endpoint in a proposed plan even when the current activity is planning-only; current plan-only work is not a reason to exclude future delivery from the proposal. Naming that endpoint is not operational permission, and an explicit source-only or design-only request stays inside that scope. Consume already approved authority for the same goals and side effects after checking remaining premises; list only uncovered authority as `manual_checkpoint`. Do not list covered required authority, generatable products, or investigable facts as missing authority. Planning does not grant authority. Missing capability blocks that step without blocking independently completable authorized work or reporting local completion as end-to-end delivery.
5. Choose executable or substitute evidence for each task. Compose `executable-oracle-architecture-selector` when correctness needs an explicit oracle strategy, and `testing-strategy` when that strategy needs concrete test lanes.
6. State fix-forward or an explicitly guarded recovery policy for each risky task.
7. Use the investigation already needed for planning to identify cohesive delegable work, including local investigation, implementation, tests, and repair. Record expected independent groups, known shared resources, required predecessor inputs, initial write regions, and parent-owned integration joins. Independent writes need appropriately isolated workspaces; disjoint filenames alone do not prove independence. Do not separately estimate dispatch economics, pre-solve worker details, or require explorer-first investigation to fill the plan. Narrative order alone is not a dependency; unknown independence remains conditional.
8. Check that the currently effective objective, authorized writes, protected behavior, factual dependencies, delivery endpoints, authorized discretion, and acceptance evidence are sufficient and coherent. They may come from existing requests or contracts; local implementation does not require delegation profiles, parallel policy, exact dispatch paths, a fixed review budget, or a catalog of every secondary feature failure. Assess delegation readiness separately only for slices actually delegated or claimed delegation-ready.
9. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
10. When review is required, request a bounded `review-change` evaluation, adjudicate its read-only candidate findings, and repair accepted defects within the confirmed design and planning scope. Continue evidence-backed in-scope repair and affected verification without a default count limit. Use targeted rereview when prior evidence becomes stale or an independent question remains; do not reopen adjudicated findings without new evidence. Do not rewrite confirmed goals, dependencies, authority, or acceptance to make the plan pass. Stop for a concrete decision or prerequisite gap, lack of a viable path, or an explicit invocation budget, reporting the reason and incomplete work. Finish when the requested plan satisfies its requirements; further review is not a ritual.
11. Close every implementation-oriented plan with an explicit implementation-approval summary for the user. Distinguish (1) the actions, targets, repositories, and side effects the user may approve together, (2) authority already covered, (3) technical checks, investigable facts, and generatable products the agent must execute rather than ask approval for, and (4) remaining real manual checkpoints and pause conditions. Keep that summary to currently effective goals, discretion, and real pause conditions; cite historical exemptions shortly instead of copying old gates. Do not hide a future approval request in task prose or ask again for ordinary in-scope execution choices after the stated scope is approved.

Read `references/delivery-and-delegation.md` when the plan must record delivery endpoints, two-stage planning versus dispatch, cohesive worker slices, required versus missing authority, decision-versus-fact classification, compact live plan versus historical exemptions, same-task continuation without handles, or its implementation-approval summary. Ordinary local plans that do not claim those arrangements may omit it.

## Conditional Decisions

Use `language-decision-tree` only when a task creates or replaces a persisted project, service, tool, or automation boundary. Record the selected language and rationale only for affected tasks.

When the approved design contains an architecture decision, reference it and plan reversible implementation increments, ownership, oracles, and observable upgrade triggers. Do not rescore the design during planning. Return `needs_design_decision` if current evidence invalidates an approved design premise.

Planning fixes acceptable behavior and ownership; dispatch refines host-required files and inputs inside the approved scope. Do not expand explicitly fixed file, interface, or ordering restrictions, invent readiness, or pre-solve the worker's implementation merely to fill filenames. Approving a plan does not turn every observed path or SHA into such a restriction. In-scope local refinement and safely reconcilable parallel changes do not reopen the whole plan; retain exact host capabilities and stale-candidate checks at the execution boundary.

When the user explicitly requests delegated or subagent-assisted implementation, read `references/delegation-profiles.toml`. For each useful delegable slice, record its goal, known inputs, repository owner, initial write regions, shared-resource constraints, isolation and parent join, verification, and any applicable execution/reasoning profile. These are semantic expectations, not an executable dispatch schema or a complete file whitelist. Do not invent unknown paths or pre-investigate local implementation details to qualify a task. Preserve explicit fixed restrictions and real host capability requirements; keep materially unresolved independence conditional.

A writable delegated task belongs to one repository root. Split a multi-repository milestone into repository-owned writable slices, retain cross-repository integration in the active parent, or design an explicit external boundary with its own authority and cleanup. Do not imply that one worker can mutate sibling repositories, and do not prescribe a host-specific working-directory flag, snapshot, worktree, staging path, or scheduler.

`implement-change` owns any later projection of an approved factual predecessor into a compatible host mechanism. A hard predecessor is eligible only when approved implementation order requires it and no parent-owned synthesis, authority, cross-task coordination, finding adjudication, final acceptance, or continuation decision occurs between the tasks. Verification or repair labor may have factual dependencies but does not by itself require an intervening parent decision. Do not compile a plan into a static worker-to-reviewer-to-repair chain that bypasses parent semantic adjudication.

## Fresh-Main Handoff

Carry the effective goals, chosen design and rationale, required acceptance, covered authority, real dependencies, expected independent groups, and parent joins in the plan or accessible references. Do not rely on the prior conversation being present. Ensure uncommitted or out-of-checkout design/plan inputs are genuinely available to the executor; naming a path is not transmitting it. Keep the investigation transcript out unless a bounded piece is necessary.

At implementation time dispatch economics uses this plan and already collected context only. Do not budget a second search, probe, model call, or duration-estimation phase to decide whether to delegate. If evidence is insufficient, the main agent performs the next useful implementation action; independent work discovered naturally can be delegated later. An explicit required delegation method remains binding.

## Plan Guidance

An execution-grade plan should record currently effective facts, not a copy of every superseded gate:

- milestone objective, non-goals, future phases, and authorized best-effort discretion when it exists
- task IDs, dependencies, scope slices, ownership, and known write surfaces
- completion conditions, delivery endpoints, and verification commands or evidence
- required authority, missing authority, and capability gaps as separate facts; investigable facts and generatable products are not missing authority
- serial order or safely independent named groups
- expected same-task parent-child interaction without prefilling handles that do not exist yet
- delegation eligibility, repository ownership, exact write set, resource locks, isolation, and convergence ownership when useful
- canonical execution and reasoning profiles for tasks claimed delegation-ready after an explicit delegated-implementation request
- recovery policy and any guarded rollback trigger
- truth-sync targets when stable truth will change
- review decision and, when review ran, its verdict and adjudication summary
- an implementation-approval summary: actions, targets, repositories, and side effects the user may approve together; already covered authority; agent-owned checks and generatable products; remaining real manual checkpoints and pause conditions; excluded actions; and reapproval triggers

Keep the live plan compact. Distinguish user decisions, investigable facts, implementation products to generate, technical verification, and already approved adaptations. New evidence updates the currently effective paragraphs; valuable history stays in stage records and is cited shortly. Document length is not a gate.

Use semantic capability descriptions rather than provider names or exact model settings. The optional execution and reasoning profiles express intent, not a route binding; a compatible active host may use a default or retain the task when no mapping exists. A later explicit user-selected execution or reasoning route is invocation authority rather than plan metadata and may be preserved through ephemeral compatible-host parameters without amending the plan. It never authorizes mutation of durable route configuration. Plans that do not claim delegation readiness may omit profiles. A plan must not prescribe how a particular product schedules actors, binds models, records attempts, or resumes sessions.

## Decision States

- `ready_for_approval`: the plan and any required review evidence are complete, and its implementation-approval summary names the exact decision the user can make
- `needs_design_decision`: the approved design is no longer sufficient
- `split_scope`: the milestone cannot remain one bounded execution package
- `manual_checkpoint`: a specific prerequisite or authority decision blocks the affected work; name it in the approval summary instead of hiding it in a later task

Approval belongs to the user. A plan's summary makes the next approval actionable but does not grant it; review success does not authorize implementation, and an implementation request does not retroactively approve an unresolved plan.
