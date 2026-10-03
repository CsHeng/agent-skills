---
name: plan-change
description: "Create a requested implementation plan or resolve execution ordering, dependencies, coordination, verification, authority, or delivery endpoints for an authorized change. Not for executing an existing plan or a bounded change that needs no separate planning artifact."
---

# Plan Change

Turn an approved design or explicit bounded scope into a self-contained implementation plan a fresh main agent can follow. Optimize accepted end-to-end delivery within the quality, authority, and budget boundaries, not token count, dispatch count, or keeping the parent continuously coding.

## Use This Skill When

- the user requests an implementation plan based on settled design or bounded scope
- execution ordering, dependencies, coordination, verification, authority, delivery endpoints, or recovery arrangements genuinely need a planning decision

A bounded authorized change can enter implementation directly when those facts are already sufficient. Potential parallelism or ordinary local technical choices do not by themselves require a separate plan. When the user requests a plan artifact, document established decisions without reopening them or proceeding into implementation.

Do not use it while a necessary design decision or scope approval is unresolved, to execute an existing plan, or for a standalone review request.

## Plan

1. Load the approved design or bounded scope and preserve its decisions. Clear non-automatable prerequisites before presenting an execution-ready plan; report unresolved account, login, access, credential, license, or physical prerequisites as `manual_checkpoint` instead of hiding them inside implementation tasks.
2. Split the work into stable task IDs with explicit real dependencies, bounded objectives, ownership, completion conditions, and concrete verification. Treat binding user goals, acceptance, authority, and explicitly fixed restrictions as fixed; treat model-derived granularity, dependency edges, order, verification means, likely files, revisions, and environment snapshots as refinable planning context.
3. Judge task membership, covered versus missing authority, and current capability separately. Consume trusted approval that already covers the same goals and side effects; list only genuinely uncovered authority as `manual_checkpoint`, and never record investigable facts or generatable products as missing authority. Planning does not grant authority.
4. Name the useful delivery endpoint even when the current activity is planning-only; naming it is not operational permission, and an explicit source-only or design-only request stays inside its scope. Leave remaining local investigation, glue around specified technology, and already-authorized best-effort secondary adaptation to the executor instead of pre-enumerating every path or secondary failure.
5. Choose executable or substitute evidence for each task. Compose `executable-oracle-architecture-selector` when correctness needs an explicit oracle strategy, and `testing-strategy` when that strategy needs concrete test lanes.
6. State a fix-forward or explicitly guarded recovery policy for each risky task.
7. Identify cohesive delegable work from the investigation planning already needs, and record independent groups, shared resources, required predecessor inputs, initial write regions, and parent-owned integration joins.
   - A hard predecessor is eligible only for approved factual order with no intervening parent synthesis, authority, cross-task coordination, finding adjudication, final acceptance, or continuation decision.
   - Do not add a separate dispatch-economics or explorer-first phase, and do not prefill host or worker details. Narrative order alone is not a dependency, and unresolved independence stays conditional.
8. Check that the effective objective, authorized writes, protected behavior, factual dependencies, delivery endpoints, authorized discretion, and acceptance evidence are coherent; assess delegation readiness only for slices actually delegated or claimed delegation-ready.
9. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
10. When review is required, request a bounded `review-change` evaluation and adjudicate its read-only candidate findings.
    - Repair accepted defects inside the confirmed design and planning scope, and continue evidence-backed in-scope repair and affected verification without a default count limit.
    - Use targeted rereview when prior evidence becomes stale or an independent question remains.
    - Do not rewrite confirmed user goals, acceptance, or authority, erase a real unmet dependency, or weaken an oracle to make the plan pass.
    - Stop for a concrete decision or prerequisite gap, a lack of viable path, or an explicit invocation budget. Finish once the requested plan satisfies its requirements; further review is not a ritual.
11. Close every implementation-oriented plan with an explicit implementation-approval summary for the user.
    - Cover the actions, targets, repositories, and side effects the user may approve together; authority already covered; agent-owned checks and generatable products; and remaining real manual checkpoints and pause conditions.
    - Keep it to currently effective goals, discretion, and real pause conditions, and cite superseded exemptions shortly instead of copying old gates.
    - Do not hide a future approval request in task prose or ask again for ordinary in-scope execution choices after the stated scope is approved.

Read `references/delivery-and-delegation.md` when the plan must record delivery endpoints, plan-record contents, two-stage concretization, cohesive worker slices, required versus missing authority, decision-versus-fact classification, delegation readiness and profiles, same-task interaction without handles, or the implementation-approval summary. Ordinary local plans that do not claim those arrangements may omit it.

## Task Granularity

Use independently verifiable outcomes and blocker boundaries as task boundaries:

- If one part can be accepted or blocked while another can still advance, make them independently trackable, and split local source work from externally gated verification when their prerequisites differ.
- Keep stable task IDs for independently deliverable owner packages. A stable ID preserves a still-identical obligation, not the initial decomposition: correcting a mistaken model-inferred split, merge, dependency edge, or order is an in-discretion representation refinement, not a goal change or a reason to re-request covered authority, while explicitly user-fixed restrictions still bind.
- Commands, file counts, and elapsed-time estimates are not task boundaries. An overall milestone may aggregate acceptance, but its grouping must not become a prerequisite for every local result or join.
- Record only the upstream outputs each consumer actually needs.

Assign each verification claim, its actual inputs, and its acceptance owner to the corresponding outcome:

- Separate shared-foundation proof, consumer-adoption proof, and whole-change joins when their prerequisites or acceptance differ. Do not make mutable consumer outputs inputs to foundation acceptance merely because one verification-matrix row groups their checks.
- Preserve any genuine compatibility dependency and its evidence. Otherwise verify the foundation against its owned inputs and fixtures, and place consumer checks with their owners or the relevant join.
- Check that a consumer-only change does not invalidate an independent foundation or sibling outcome.

## Conditional Decisions

Use `language-decision-tree` only when a task creates or replaces a persisted project, service, tool, or automation boundary. Record the selected language and rationale only for affected tasks.

When the approved design contains an architecture decision, reference it and plan reversible implementation increments, ownership, oracles, and observable upgrade triggers. Do not rescore the design during planning. Return `needs_design_decision` if current evidence invalidates an approved design premise.

Planning fixes acceptable behavior and ownership; dispatch refines host-required files and inputs inside the approved scope. Approving a plan does not turn every observed path or SHA into such a restriction, and in-scope local refinement or safely reconcilable parallel changes do not reopen the whole plan. Retain exact host capabilities and stale-candidate checks at the execution boundary.

When the user explicitly requests delegated or subagent-assisted implementation, read `references/delegation-profiles.toml`. Record each useful delegable slice's goal, known inputs, repository owner, initial write regions, shared-resource constraints, isolation and parent join, verification, and any applicable execution or reasoning profile. These are semantic expectations, not an executable dispatch schema or a complete file whitelist. Do not invent unknown paths or pre-investigate local implementation details to qualify a task; preserve explicit fixed restrictions and real host capability requirements, and keep materially unresolved independence conditional.

A writable delegated task belongs to one repository root. Split a multi-repository milestone into repository-owned writable slices, retain cross-repository integration in the active parent, or design an explicit external boundary with its own authority and cleanup. Do not imply that one worker can mutate sibling repositories, or prescribe a host-specific working-directory flag, snapshot, worktree, staging path, or scheduler.

`implement-change` owns any later projection of an approved factual predecessor into a compatible host mechanism. Do not compile a plan into a static worker-to-reviewer-to-repair chain that bypasses parent semantic adjudication.

## Document Ownership

Follow the project's declared design/plan owner, which may be a separate repository. Resolve owner-root variables before writing, include external document and product paths in the authorized write set, and keep the plan genuinely accessible to the executor. Invocation cwd is not a substitute for user authority. Do not copy an external plan into every product repository or make distributed Skills depend on a particular coordination checkout.

## Fresh-Main Handoff

Carry the effective goals, chosen design and rationale, required acceptance, covered authority, real dependencies, expected independent groups, and parent joins in the plan or accessible references. Do not rely on the prior conversation being present. Ensure uncommitted or out-of-checkout design/plan inputs are genuinely available to the executor; naming a path is not transmitting it. Keep the investigation transcript out unless a bounded piece is necessary.

At implementation time dispatch economics uses this plan and already collected context only. Do not budget a second search, probe, model call, or duration-estimation phase to decide whether to delegate. If evidence is insufficient, the main agent performs the next useful implementation action; independent work discovered naturally can be delegated later. An explicit required delegation method remains binding.

## Decision States

- `ready_for_approval`: the plan and any required review evidence are complete, and its implementation-approval summary names the exact decision the user can make
- `needs_design_decision`: the approved design is no longer sufficient
- `split_scope`: the milestone cannot remain one bounded execution package
- `manual_checkpoint`: a specific prerequisite or authority decision blocks the affected work; name it in the approval summary instead of hiding it in a later task

Approval belongs to the user. A plan's summary makes the next approval actionable but does not grant it; review success does not authorize implementation, and an implementation request does not retroactively approve an unresolved plan.
