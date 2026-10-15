---
name: implement-change
description: "Implement an explicit bounded repository change or approved plan through mutation, verification, conditional review, accepted repair, and an evidence-backed outcome."
---

# Implement Change

Complete the user's authorized outcome with the smallest durable change. Preserve required behavior and authority; use the plan to organize work without turning incidental methods, tests, or bookkeeping into additional requirements. Apply `development-standards` for necessity, compatibility, and proportionate evidence.

## Use This Skill When

- an explicit bounded user request or approved plan authorizes repository mutation
- implementation, verification, conditional review adjudication, and bounded repair need one semantic owner

Do not use it when a necessary scope, design, execution-order, prerequisite, or authority decision remains unresolved, or when the request is only analysis, review, truth sync, or closure. A separate design or plan artifact is not required for an otherwise sufficient bounded request; ordinary code investigation and local technical choices remain implementation work.

## Preconditions

- Confirm the authorized objective, any approved task order, repository ownership, allowed surfaces, protected behavior, acceptance evidence, applicable recovery policy, and known user changes. Use the approved plan when present; otherwise use the bounded request and applicable project contracts. Do not manufacture a plan, oracle-selection phase, delegation profiles, or review budget merely to begin local implementation.
- Inspect `git status --short` and preserve existing work. Default to the current checkout under Checkout And Concurrent Work below; dirty state alone is not a reason to create a worktree, clone, or branch.
- Treat task membership, authority, and capability as separate facts. Commit, push, publication, deployment, destructive history changes, and external mutation need matching authority, not merely implementation approval. Consume existing trusted permission for the same requested target and side effects without re-asking; standing permission does not add work to a design-only or otherwise narrower request. A push includes its entire outgoing history and triggered CI/CD, not just this task's tip commit.
- Report the specific owner decision needed before exceeding a real goal, hard constraint, or authority boundary. `replan` and `redesign` describe that unresolved conflict; they are not commands to activate upstream stages. Do not automatically call design, planning, or structural simplification to rejustify an approved implementation.

## One-Way Execution

Implement the settled goals and selected technology; do not automatically reopen design/plan or conduct an architecture replacement audit. Local investigation, glue, ordinary tests, same-task repair, and newly discovered in-goal files are implementation work. An initial write inventory is not a permanent approval whitelist. Coordinate actual ownership changes through the supported host path without renewed user approval when existing authority covers them. Only evidence of a real incompatible goal, hard constraint, or missing authority pauses the affected action for an owner decision; independent authorized work continues.

## Early Business Feedback

Use the current project environment to implement a thin real path from relevant input to useful output, with its local feedback loop. Resolve only the uncertainty or setup that actually blocks the next authorized step. Do not first build a complete fixture platform, probe framework, recovery rehearsal, or evidence pipeline when existing tools or a bounded local check suffice. Required pre-deployment checks can happen at the delivery join; safeguards against actual data loss or unauthorized effects must precede the affected operation.

When supporting work keeps growing while no business behavior has advanced, reconsider that branch rather than assigning more workers to harden it. Within existing authority, remove unnecessary mechanisms, defer non-prerequisite preparation, or use a direct existing capability, then continue the outcome. A working first slice is feedback, not permission to omit required remaining behavior or verification. Do not create a new timer, progress gate, or full redesign to make this correction.

## Goals, Discretion, And Continuation

Main goals, necessary conditions, user-fixed technical choices, and inviolable boundaries remain binding. Model-inferred task granularity, dependency edges, ordering, guards, compatibility assumptions, and verification methods remain revisable within that intent, including after general plan approval. Correct them without new approval when required outcomes and real boundaries stay intact. During long tasks and handoffs, retain the user's purpose and remaining outcomes rather than letting the growing task list replace them.

Already-authorized best-effort secondary work may be adapted or omitted based on evidence while the main goal continues. Do not self-grant that discretion, relabel a required result, or weaken an oracle to pass.

Investigate facts and generate execution products rather than asking for them, and after the user answers a blocking question, resume the original authorized work rather than terminating on confirmation.

When the user later adds explicit delivery authority such as `approved, include commit/push/deploy`, reconcile the currently effective objective, scope, and endpoint with the existing plan. Update the live plan, approval summary, and affected delivery dependencies when that write is authorized, then continue without asking permission merely to record the addition. Keep earlier reviewed revisions as provenance and do not leave contradictory live pending or excluded gates beside a top-level override.

Do not rewrite unrelated approved constraints, expand beyond the newly authorized target or scope, treat document annotation or review success as authority, or waive required verification. Naming a delivery endpoint or a planning-only proposal does not create operational permission; standing permission does not add delivery work to a narrower request, and an explicit source-only or design-only request stays inside its scope until the user explicitly adds the delivery work and matching authority.

A final-sounding response, a completed subtask, elapsed time, or the model's estimate of remaining context is not a stopping condition. Continue while an evidence-backed step can advance an authorized obligation, including independent work when another path is blocked.

Honor actual host interruption, user cancellation, and explicit invocation budgets, and report their uncompleted remainder as interrupted or blocked rather than success or proof that the goal is impossible. Do not invent a budget or require repeated checks merely to avoid stopping.

Credentials, tools, and review success are not operational permission; specified libraries bind and glue, helpers, and local algorithms stay with the implementer. Before an action would leave the approved boundary in goals, hard constraints, commitments, risk, or permissions, obtain narrow authorization for that impact, including before production or protected-state actions.

## Progress Through Long Tasks

Keep the objective, current result, remaining work, real blockers, and effective authority recoverable at useful milestones and handoffs. Use the conversation, existing project records, or available task tracking as appropriate to the task. Revise model-derived steps when a simpler route preserves the user's intent; continue useful authorized work until the requested outcome is delivered or a real boundary prevents it.

The main agent judges completion from the actual result and applicable evidence, independently of any task engine. Tracking helps retain context; its availability, fields, or completion status add no business acceptance, tests, or review requirements. Handle a tracking failure separately from the business work already performed.

## Checkout And Concurrent Work

- Continue in the current checkout when the only uncommitted files are this task's design, plan, implementation, or evidence. Unrelated non-overlapping changes are also acceptable; preserve them and keep them outside this task's edits and any authorized commit. Committing task documents is optional and requires commit authority, not a prerequisite or a concurrency safeguard.
- If existing edits overlap the intended write set, inspect their content and ownership. Continue when they can safely be retained; otherwise resolve that specific conflict before writing. Do not reset, stash, overwrite, or isolate automatically merely to obtain a clean status.
- Keep the parent in its current checkout unless a concrete reason requires otherwise.
   - Independently executing write tasks should use host-managed isolated workspaces that retain their separate results, and a task workspace should be reused across its worker/review/repair lifecycle.
   - Host-provided isolation does not itself invoke the separate `git-worktrees` Skill or grant new Git mutation authority. An explicitly requested worktree operation loads that Skill for its own creation, context-transfer, integration, and cleanup guidance; remember that a new checkout never inherits uncommitted context, and that isolation never settles semantic integration or shared-resource conflicts.
- Judge concurrency from the user's statement, already available host task evidence tied to the same checkout and writes, or unexpected changes observed during this task. Assess shared generated output, Git index/ref operations, and other shared resources as well as file overlap; multiple agents with disjoint safe operations do not automatically need worktrees. An agent process, dirty file, or recent modification timestamp alone is not proof of an active conflicting writer, and do not scan the whole workstation or build a coordination system to rule out hypothetical concurrency.
- Record the initial state, check the relevant current contents before edits, and reconcile the final diff against owned changes.
   - A plan's observed files and environment are context, not an immutable goal or permission boundary unless explicitly designated as one. Recording a revision is not a default prerequisite.
   - When drift appears, stop stale writes long enough to read and reconcile it, then continue under the existing goals and authority: preserve other work, merge compatible changes, and reverify affected behavior. Do not ask for new permission merely because a file or revision changed.
   - Pause only the affected path when ownership or a conflict cannot be resolved safely, or when an actual hard boundary changes.
   - Host exact-write capabilities and candidate apply checks remain binding: refresh or redispatch through the supported parent path, never bypass a conflict check. These checks detect some conflicts, not mutual exclusion, and absence of visible activity does not prove there is no other writer.

## Implement And Verify

1. Inspect the smallest current surface needed for the next ready task. For a bug fix touching shared behavior:
   - Trace the symptom through the relevant entry point, shared function and affected callers to the contract that owns the violated invariant.
   - Use symbol, reference, configuration and test evidence as appropriate, including public, generated, dynamic or external callers. Text-search silence does not prove that all consumers are known. Keep inspection proportional rather than scanning the whole repository by default.
   - Choose a shared fix only when the affected callers share the invariant. Keep caller-specific product rules at their owning boundary and preserve intentionally different validation or error behavior; fewer guards or lines do not justify hoisting policy into a common helper.
   - If an unresolved caller contract prevents a safe bounded fix, state the evidence gap and use the `blocked`, `replan`, `redesign` or `needs-authority` outcome that fits. Do not broaden the repair into a simplification audit.
2. Prefer a narrow reproducer or red-green oracle for non-trivial behavior. For shared-behavior fixes, select focused regression evidence for affected sibling paths and protected caller behavior as needed, without requiring one test per caller or prescribing a framework.
3. Make the smallest cohesive change that advances required behavior within the approved scope, and preserve unrelated user changes. Smallest means the least total responsibility and maintenance burden, not the fewest edited lines or another patch around an unnecessary mechanism.
4. Complete all approved in-scope tasks whose dependencies can be satisfied; a task boundary is progress, not an automatic stopping point.
   - Dispatch substantive independent slices per Delegation And Profiles using the plan and already collected context. Spend no additional search, probe, model-call, or time-estimation budget deciding whether to delegate. If the available context is insufficient, implement the next useful step locally and leave naturally discovered independent work for later delegation.
   - Preserve repository ownership, shared resources, isolation, convergence ownership, and applicable profiles.
   - Encode a hard predecessor only for approved factual order with no intervening parent synthesis, authority, cross-task coordination, finding adjudication, final acceptance, or continuation decision. A verification command is not itself a parent decision.
5. Check the changed surfaces against the user's goal, acceptance, authority, and explicitly fixed boundaries. Admit discovered issues when they are caused by the change or demonstrably block the authorized outcome; report unrelated existing failures without absorbing their repair. Reassess a growing mechanism and its maintenance cost before treating every resulting defect as another goal. Preserve necessary correctness, safety, and retained-state protections while removing work the outcome does not need.
6. Remove unnecessary abstractions, guards, compatibility emulation, tests, fixtures, and documents introduced by this slice. Their appearance in a plan or review does not make them required. This is ordinary implementation cleanup; a broader requested audit uses only `references/simplification.md` in `skills-routing`. A real product tradeoff needs the corresponding owner decision, while removal of an unneeded method stays inside the current task.
7. Coordinate one verification strategy for the change. Select checks from affected behavior, consumers, and uncertainty; use local tests or compilation for useful feedback, and finish related edits before repeating checks that cannot inform intermediate work. The main agent selects and times integration, E2E, and full-suite checks at useful joins, delegating execution when helpful. Use a full suite for relevant broad impact, an explicit delivery requirement, or uncertainty narrower evidence cannot resolve. Reuse applicable worker results and verify uncovered combinations. Earlier model-declared breadth may be revised within the actual requirements.
8. Obtain independent review when explicitly requested, required by an applicable rule, or justified by concrete risk or uncertainty. Supply one bounded `review-change` target with the objective, diff, and current evidence; adjudicate material candidates under Review Adjudication.
9. Diagnose in-scope failures and repair accepted defects using [Focused Implementation Repair](references/repair-loop.md). Rerun evidence invalidated by the repair and cover any newly affected behavior; retain still-applicable results. Target rereview to a changed premise or unresolved independent question.
10. Complete when the authorized objective, delivery endpoint, necessary verification, and accepted findings are satisfied. Report the actual delivered result, applicable evidence, and any authorized secondary tradeoff or unverified remainder. Missing downstream permission or capability blocks that step, not independent work. Stop checking once sufficient evidence supports delivery; partial completion remains distinct from success.

## Delegation And Profiles

Optional execution and reasoning profiles are semantic hints, not authority or provider bindings. Their absence or an unavailable host mapping does not block implementation: use a compatible default or retain the task in the active agent. When the user explicitly selects a concrete execution or reasoning route, preserve that choice through ephemeral task parameters when the compatible host supports them; the explicit user choice overrides semantic defaults for that invocation. Never mutate durable route configuration as a one-invocation workaround unless the user separately authorizes a persistent default change.

Delegation does not transfer scope control, invocation and continuation decisions, cross-task synthesis, review adjudication, final acceptance, or the final response. It can transfer bounded investigation, implementation, verification execution, diagnosis, and authorized repair labor when the host and applicable policy permit them.

Read `references/delegated-execution.md` when dispatching or continuing a worker, interpreting a delegated result, or recovering a failed invocation. A cohesive slice includes its local feedback loop; prefer the same valid worker for in-scope follow-up when the host supports continuation. A completed subset can be consumed and followed by nonconflicting work while other tasks are still running; when no independent runnable work remains, end the turn unfinished and rely on the supported completion notification rather than a default join of the whole submission. Keep trivial, tightly coupled, or unsupported work local rather than padding calls, and do not silently replace an explicitly required delegation method. Task tracking remains optional context and does not accept results, block execution, or replace parent verification.

## Review Adjudication

Use one disposition for each material candidate:

- `accepted`
- `rejected_no_causal_link`
- `rejected_pre_existing`
- `rejected_out_of_scope`
- `rejected_insufficient_evidence`
- `deferred_followup`
- `needs_plan_change`

The reviewer is read-only. The implementing parent adjudicates candidate findings and authorizes accepted repairs; a worker may execute the resulting bounded repair and its local checks, and routine worker diagnosis within its existing brief does not require parent approval for every red-green iteration. These detailed reason categories refine the broad caller dispositions — accepted, rejected with a reason, deferred, or escalated to a design or plan decision — used by other calling workflows for the same judgment; they are distinct from the evaluator's return category, from the reviewer's overall verdict, and from this workflow's own outcome labels, and no level converts automatically into another. Severity or reviewer preference does not widen scope. Reuse prior dispositions only while their evidence applies to the current version; a different reviewer alone is not new evidence. Do not reopen a settled candidate without new evidence or overlook a new regression because an earlier version passed review.

## Acceptance Integrity

The approved objective, non-goals, real unmet dependencies, authority, protected contracts, and acceptance conditions remain the baseline throughout repair; a model-inferred task split, dependency edge, or ordering may be corrected inside that baseline without overriding an explicitly user-fixed restriction. Updating progress or adding execution evidence does not authorize rewriting these requirements to match the current implementation. Distinguish a listed capability, permission to run its gate, and evidence required for this delivery: none implies the others.

Before treating an unavailable gate as a completion blocker, identify the approved outcome or changed behavior that needs it. Prepare obtainable prerequisites within existing authority, retain genuine required capability gaps, and never relabel required positive evidence as optional or satisfied by a negative preflight.

An authorized best-effort secondary adaptation recorded with evidence is an allowed result and does not rewrite the main-goal baseline. Treating a required result as optional, or deleting its oracle to manufacture a pass, remains forbidden, and ordinary failure or unknown feasibility is not itself proof that a required result is unsupported.

A mistaken or over-specified test may be corrected or removed within the authorized scope when the user's required behavior and consumer evidence establish what actually needs protection. Verify that behavior independently of the removed mechanism; do not preserve a self-invented requirement merely because its test fails. Changing a genuinely required result remains a scope or design decision, and deleting its oracle to manufacture a pass remains forbidden.

## Recovery

- `fix_forward` is the default: preserve evidence, diagnose the observed failure, repair within scope, and rerun the owning oracle.
- `stop_and_diagnose` preserves current state and stops further mutation.
- `guarded_rollback` requires an approved exact trigger, target, and rollback verification, plus evidence that rollback is safer than forward repair.

Never synthesize rollback or treat repeated failure as authority to redesign.

## Outcomes

- `pass`: implementation and required verification pass; no accepted finding from any required review remains. Disclosed authorized secondary tradeoffs may remain when the main goal and approved acceptance are met; do not also claim every secondary feature completed. A requested production endpoint that was not performed is not end-to-end success.
- `replan`: the approved scope, order, or verification is insufficient
- `redesign`: evidence invalidates an approved design boundary
- `needs-authority`: completion needs new user or external authority
- `guarded-rollback`: the approved rollback condition is met and its safe path is ready
- `non-convergent`: diagnosis yields no new evidence and no reasonable in-scope path remains; report what was tried, excluded, and still missing rather than a failure count
- `blocked`: required evidence or a prerequisite is unavailable, or work stopped on user cancellation or an explicit invocation time, call, or resource budget; name the actual reason and remaining work, not a claim that the objective is impossible

Explain what changed, the evidence supporting it, and material limits or unfinished work. Include review or repair conclusions when they affect acceptance. Report only actions actually performed; completion of the main goal does not imply every secondary feature was delivered.
