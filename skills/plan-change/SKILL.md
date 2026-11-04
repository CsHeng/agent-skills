---
name: plan-change
description: "Create a requested or policy-required implementation plan, or resolve genuinely open execution ordering, cross-actor coordination, verification strategy, or authority gates. Execute approved plans and contract-conforming changes—even across multiple files or repositories—directly with implement-change; undecided goals or boundaries belong to design-change."
---

# Plan Change

Turn settled intent into a practical route to the user's outcome. A fresh executor should understand what success means, why the approach is worthwhile, what authority already exists, and what decisions remain open. `development-standards` applies from the first task: name the current need before adding a mechanism, compatibility obligation, verification lane, or task.

## Use This Skill When

- the user requests an implementation plan, or repository policy requires one for that change class
- execution ordering, cross-actor coordination, oracle strategy, authority gates, delivery endpoints, or recovery arrangements remain genuinely unresolved under existing contracts and runbooks

A plan artifact does not authorize implementation. An unresolved material design decision goes to `design-change`.

## Plan

1. Read the request, relevant design decisions, and enough implementation truth to identify the user-visible result. Preserve the user's goal, explicitly fixed choices, real acceptance, and safety and authority boundaries; treat model-derived guards, compatibility machinery, hashes, task splits, and verification routes as revisable means even when an approved document contains them.
2. Confirm the proposed work still serves that result and keep a simpler in-scope route available when it preserves the required behavior. For a migration or replacement, carry the operating, deployment, and maintenance rationale from the design; language selection in `skills-routing` owns the benefit judgment for a language or platform move.
3. Identify cohesive outcomes, real dependencies, owners, and how each result is checked. Put an early thin real business path first with only its genuine prerequisites ahead of it. Use task IDs when they help track independent work; a small change needs no task graph. Paths and names describe domain responsibility, not plan IDs.
4. Distinguish task membership, authority, and capability. Consume existing permission for the same goals, targets, and side effects. A true unresolved account, access, credential, license, physical, or owner decision blocks its affected action; discoverable facts and products the agent can generate remain implementation work.
5. State the useful delivery endpoint and any genuinely uncovered authority. An explicit source-only or design-only request stays within its scope.
6. Write verification at two levels: the required outcome and boundary acceptance fixed by the request, delivery endpoint, or real consumer and safety contracts; and candidate local proof methods (fast unit or schema checks, existing owner suites, optional reproducers) the implementer may revise. When deterministic unit or schema checks plus the authorized real-path check already cover a failure mode, no additional multi-process simulation, container rebuild, or duplicate cross-layer assertion is planned for it. Read `references/oracle-selection.md` in `skills-routing` when the oracle is unresolved and `testing-strategy` when coverage or execution lanes need design. When a mechanism is removed, recompute the checks the remaining outcome needs.
7. Plan recovery for actual risky transitions before the affected operation, normally fix-forward; `references/replacement-and-cutover.md` in `development-standards` owns the sequence. From known facts, make the first useful local action or parallel assignments decidable, as described in [Delivery And Delegation](references/delivery-and-delegation.md); later implementation adapts splits to actual state, and only a real goal or boundary conflict reopens planning.
8. Read the route for omitted outcomes, unnecessary mechanisms, and real blockers. Obtain a bounded `review-change` review when requested, required by an applicable rule, or justified by concrete risk or uncertainty, supplying known inputs and accessible sources; adjudicate findings and rereview only affected or still-uncertain decisions.
9. Finish when the plan explains a supported route and omitted known inputs are repaired. In the closing response, distinguish plan completion from execution readiness, name material missing or unverified prerequisites and their affected actions, and identify any decision still needed from the user alongside the authorized work that can continue.

## Task Boundaries And Evidence

Judge a proposed preparation task by the next result it enables or the concrete harm it prevents; otherwise move it to a later join, reuse an existing capability, or omit it. Split work where outcomes can be accepted or blocked independently; keep related implementation, tests, feedback, and repair together when they form one useful slice. Commands, files, time estimates, and review rounds are not tasks.

Task IDs preserve continuity, not the initial decomposition: the parent may correct model-inferred splits, merges, dependencies, or order within the user's goal and authority, while an explicitly user-fixed restriction binds. Reference settled architecture choices rather than rescoring them; evidence that invalidates a material premise returns `needs-decision: design`, and a simpler implementation of the same goal does not.

When delegated implementation is planned, record known inputs, repository owners, initial write regions, shared-resource constraints, verification, and any real integration join; `references/delegation-profiles.toml` holds the optional profile vocabulary, and concrete scheduling, workspaces, and route bindings belong to the host.

## Plan And Handoff

Use the project's declared document owner and make the plan and its necessary inputs accessible to the next executor, including uncommitted or out-of-checkout material. Keep a compact current account of the outcome, rationale, user-fixed constraints, covered authority, real dependencies, required acceptance versus candidate proof methods, ownership, and remaining decisions, with safe references in place of secret values; `development-standards` owns when exact identities or digests are needed. `plan.md` is an authorization, boundary, and handoff record that downstream implementation edits only for an explicit authority, scope, or decision change or a handoff or terminal summary. No particular headings, fields, or length are required.

## Outcomes

- `ready`: the requested plan and any required review are complete; name an approval only when one is actually outstanding
- `needs-decision`: qualified as `design` when a material goal or boundary is unresolved, or `user` when a specific user or external prerequisite blocks the affected action
- `split-scope`: the proposed milestone does not form a coherent execution package

A plan describes authority rather than granting it. A planning decision that arose during authorized work returns to that work once resolved.
