# Skill Composition

This repository defines portable semantic capabilities, not an agent loop or an orchestration runtime.

## Ownership

| Concern | Owner |
| --- | --- |
| Messages, model turns, tool execution, isolation mechanisms, continuation capability, and session lifecycle | compatible agent host |
| Request interpretation, Skill selection, sequencing, dispatch and continuation decisions, cross-task synthesis, authority judgment, optional review, adjudication, final acceptance, and response | active coding parent |
| Bounded investigation, implementation, verification execution, diagnosis, and authorized local repair | active agent or a worker within its actual host capability and task brief |
| Reusable analysis, design, planning, implementation, review, documentation, policy, testing, tool, and Git methods | the selected Skills |
| Mutation, destructive action, external effect, publication, and deployment authority | user and repository or environment policy |

One primary Skill owns the response order and conclusion. Matching session, discipline, policy, tool, or review-component Skills may contribute bounded semantic overlays. A directly named or confidently matched Skill runs without `use-coding-skills`; the router is only ambiguity and session-boundary guidance.

## Independent Capabilities

Analysis, design, planning, implementation, review, truth maintenance, and completion judgment are independently selectable capabilities. They do not form a mandatory sequence. An authorized bounded request with sufficient scope and acceptance can enter implementation directly; material unresolved design or execution-order decisions select design or planning when needed. An explicitly requested design or plan artifact remains a valid task without authorizing subsequent implementation. Ordinary code investigation, known checks, and TDD do not themselves require upstream artifacts or another oracle-selection decision.

Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Each `review-change` invocation receives one bounded target and may select an optional read-only evaluator. The active coding parent adjudicates candidate findings, authorizes repair, and decides any necessary targeted rereview; a worker may perform accepted repair and its local checks. Reviewer self-mutation remains forbidden, and worker self-checking is not independent review. A per-invocation boundary is not a whole-change review or repair count limit.

Repair follows the authorized objective, dependencies, scope, authority, and acceptance evidence. Continue with an evidence-backed in-scope path; stop for the actual decision, input, authority, diagnostic, cancellation, or explicit budget limit. Do not weaken acceptance or rewrite approved goals to fit the implementation. Finish when required evidence and accepted findings are satisfied rather than repeating checks without a new reason.

## Bounded Delegation And Continuity

Plans fix acceptable results, ownership, constraints, and factual dependencies without exhausting local implementation choices. Dispatch refines actual host-required files and inputs inside that approved boundary; exact approved writes do not silently expand. Cohesive worker slices can include investigation, implementation, tests, and local repair. Prefer useful independent parallel work without call quotas, explorer-first gates, or mandatory delegation of trivial work. Parent decision boundaries cannot be compiled into static reviewer-to-repair chains; a verification command alone is not such a decision.

A child returns a candidate and evidence, not business acceptance. Evidence applies to an identified candidate; reuse reliable applicable checks and verify changed combinations and missing acceptance. Successful startup, report delivery, source export, local tests, and final acceptance remain separate facts.

For the same task, prefer a valid original worker or reviewer when the host supports safe continuation. Reconcile current baseline, permissions, actual results, and executor state before follow-up or post-compaction creation. Worker and reviewer remain separate roles and contexts. A justified fresh review remains possible; a reconstructed context is not native-session continuity. These are portable methods, not a claim that any particular host supplies shell, persistent sessions, steering, or measured savings.

## Task And Delivery Authority

Task membership, existing authority, and current capability are independent. Consume trusted approval covering the requested target and actual side effects without repeating approval; standing permission does not widen a narrower request. Delivery evidence must match the intended version and endpoint, including the whole outgoing push history and its CI/CD effects. A downstream capability or authority gap does not erase independent authorized work or make local completion an end-to-end pass.

## Checkout Selection

The active implementing agent normally works in the current checkout while preserving task-local and unrelated user changes. Dirty state alone does not require isolation or a preliminary commit. Isolation is justified by an explicit request, an applicable repository rule, a distinct branch-state requirement, or a concrete conflict that cannot safely be handled in place.

Concurrency judgments use user statements, available task evidence tied to the checkout and writes, or observed unexpected drift, including shared generated output and Git index/ref operations. Process presence and file timestamps alone do not establish conflicting writers, and absence of visible activity does not prove exclusive access. Scope-aware pre-edit and final-diff checks are detection, not a prompt-based lock or a reason to build a workstation-wide coordinator.

## Excluded Mechanics

`contracts/skills.toml` and the installed routing reference support authoring, discovery projection, semantic dependencies, trigger cases, and response composition. They do not define a runtime mode, fixed phase graph, implicit review, task scheduler, attempt ledger, replay protocol, actor or model binding, or completion settlement.

Ordinary implementation readiness needs relevant objectives, allowed changes, protected behavior, and sufficient acceptance evidence, which may already exist in a bounded request or repository contract. It does not require delegation profiles, parallel policy, or a fixed review budget. Actual writable delegation additionally needs safe ownership, isolation, shared-resource handling, completion evidence, and calling-agent convergence.

Plans may still describe dependencies, safe isolation, verification, authority, and recovery because those facts make a bounded change executable. When delegated implementation is explicitly requested, they may also carry optional provider-neutral execution and reasoning profiles, one repository owner, repository-relative write sets, resource locks, isolation, and convergence ownership. These semantics remain guidance consumed and translated by the active coding agent rather than model bindings, host tool arguments, or state for a repository-owned controller.

Writable delegated slices belong to one repository root. Multi-repository plans split repository-owned writes or retain cross-repository integration in the active parent; they do not prescribe a host working directory, snapshot, worktree, staging path, scheduler, or concrete route.
