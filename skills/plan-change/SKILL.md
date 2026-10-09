---
name: plan-change
description: "Create a requested implementation plan or resolve execution ordering, dependencies, coordination, verification, authority, or delivery endpoints for an authorized change. Not for executing an existing plan or a bounded change that needs no separate planning artifact."
---

# Plan Change

Turn settled intent into a practical route to the user's outcome. A fresh executor should understand what success means, why the approach is worthwhile, what authority already exists, and what decisions remain open. Completing the task list is not the outcome.

Apply `development-standards` from the start: before adding a mechanism, compatibility obligation, verification lane, or task, identify the current need and whether a simpler route reduces total maintenance burden. This judgment belongs in ordinary planning; it does not require invoking a simplification audit, filling a form, or waiting until implementation to remove unnecessary work.

## Use This Skill When

- the user requests an implementation plan based on settled design or bounded scope
- execution ordering, dependencies, coordination, verification, authority, delivery endpoints, or recovery arrangements genuinely need a planning decision

A bounded authorized change can enter implementation directly. Potential parallelism and ordinary local technical choices do not require a separate plan. A request for a plan artifact does not itself authorize implementation. An unresolved material design decision belongs with `design-change`; a standalone review uses `review-change`.

## Plan

1. Read the current request, relevant design decisions, and enough implementation truth to identify the user-visible result. Preserve the user's goal, explicitly fixed choices, real acceptance, and safety and authority boundaries. Treat model-derived guards, compatibility machinery, hashes, task splits, and verification routes as revisable means even when they appeared in an approved document.
2. Check that the proposed work still serves that result. For migration or replacement, retain the rationale about operating, deployment, and maintenance burden; do not use inventory closure, language uniformity, or test rewrites as proxies for benefit. Keep a simpler in-scope route available when it preserves the required behavior.
3. Identify cohesive outcomes, real dependencies, owners, and how each result will be checked. Use task IDs when they help track independent work; do not create a task graph merely to formalize a small change. Paths and names should describe domain responsibility, following `development-standards`, rather than encode plan IDs.
4. Distinguish task membership, authority, and capability. Consume existing permission for the same goals, targets, and side effects. A true unresolved account, access, credential, license, physical, or owner decision blocks its affected action; discoverable facts and products the agent can generate remain implementation work.
5. State the useful delivery endpoint and any genuinely uncovered authority. Planning may propose later delivery but cannot grant it, and an explicit source-only or design-only request stays within its current scope. Leave local investigation, glue, and authorized secondary adaptation to the executor.
6. Choose evidence that tests the required behavior under relevant inputs and conditions. Read only `references/oracle-selection.md` in `skills-routing` when that choice is unresolved, and use `testing-strategy` when concrete coverage or execution lanes need design. When a mechanism is simplified or removed, recompute the verification the remaining outcome needs; an old failure matrix does not transfer automatically. Reuse reliable applicable evidence instead of prescribing repeated proof after every source change. A real retained-state or recovery change still needs its corresponding evidence, and deployment wording alone does not add a restoration platform.
7. Plan recovery for actual risky transitions, normally fix-forward. Where independent work is useful, identify stable inputs, initial write regions, shared resources, and parent-owned integration and acceptance joins. Do not add explorer-first or dispatch-estimation stages, prefill host handles, or make narrative order a dependency.
8. Read through the proposed route for omitted outcomes, unnecessary mechanisms, and real blockers. Obtain bounded `review-change` review when requested, required by an applicable rule, or justified by concrete risk or uncertainty. The caller adjudicates findings and repairs accepted defects; rereview only affected or still-uncertain decisions.
9. Finish once the requested plan explains a supported route to the outcome. Identify any actual decision still needed from the user and the authorized work that can continue. Do not manufacture an implementation-approval request when the current task already provides that authority.

Read `references/delivery-and-delegation.md` when a plan needs delivery or approval detail, coordination of delegated slices, or a fresh-main handoff. Its guidance describes useful information, not a required document schema.

## Task Boundaries And Evidence

Split work where outcomes can be accepted or blocked independently, including local source work and externally gated verification with different prerequisites. Keep related implementation, tests, feedback, and repair together when they form one useful slice. Commands, files, elapsed-time estimates, and review rounds are not tasks by themselves.

Task IDs preserve continuity, not the initial decomposition. The parent may correct model-inferred splits, merges, dependencies, or order within the user's goal and authority. An explicitly user-fixed restriction still binds. Do not add a new node for each ordinary failed check or require full inventory completion when evidence supports a simpler route to the requested outcome.

Assign evidence to the result it actually proves. Separate foundation behavior, consumer adoption, and integrated delivery where their inputs differ. A consumer-only change does not invalidate an independent foundation or sibling result. Recheck changed behavior and affected combinations; a different file revision alone does not make unrelated evidence obsolete.

The implementation establishes actual system behavior; documents and diagrams express intent and explanation. Plan to update that explanation when implementation changes it. Verify the behavior the user requires, not document wording, diagram contents, or the plan's bookkeeping. Do not create tests that freeze those human-facing records.

## Conditional Decisions

Read only `references/language-selection.md` in `skills-routing` when a new persisted project, service, tool, or approved migration actually needs a language decision. Record the rationale where it matters; a product language does not dictate the language of its tests or tooling.

Reference settled architecture choices rather than rescoring them. Evidence that invalidates a material premise may require `needs_design_decision`; a simpler implementation of the same goal does not. Neither general plan approval nor a source snapshot makes every proposed precaution a fixed user choice.

When delegated implementation is requested or planned, read `references/delegation-profiles.toml` if semantic profiles are useful. Record known inputs, repository owner, initial write regions, shared-resource constraints, verification, and the parent join. Do not invent unknown paths or inspect implementation details solely to fill dispatch fields. Host-required exact capabilities remain binding at execution; they are not new human approval obligations.

A writable delegated task belongs to one repository root. The parent owns cross-repository integration, authority judgments, acceptance, and continuation. Keep genuine dependencies but do not compile them into an automatic worker-reviewer-repair chain that bypasses those decisions. Concrete scheduling, workspaces, and route bindings belong to the host; absent optional profile mappings do not block authorized work.

## Plan And Handoff

Use the project's declared document owner, resolving named roots before writing. Ensure the plan and its necessary inputs are accessible to the next executor, including uncommitted or out-of-checkout material. Do not duplicate it across repositories or make product execution depend on a coordination checkout.

Keep a compact current account of the outcome, rationale, user-fixed constraints, covered authority, real dependencies, relevant verification, ownership, and remaining decisions. Link useful historical context without repeating superseded gates. Ordinary local plans do not need mandatory Git identities, design or revision hashes, credentials, or receipt chains. Preserve exact identity requirements only for the interface or protected operation that actually consumes them.

Use a diagram where it makes relationships, sequence, or ownership clearer and removes repetitive prose. Keep reasons and exceptions in concise text; the diagram does not add executable gates. No particular headings, fields, or document length are required by this Skill.

## Decision States

- `ready_for_approval`: the requested plan and any required review are complete; name an approval only if one is outstanding
- `needs_design_decision`: a material goal or design boundary remains unresolved
- `split_scope`: the proposed milestone does not form a coherent execution package
- `manual_checkpoint`: a specific user or external prerequisite blocks the affected action

A plan describes authority rather than granting it. Review success does not authorize implementation; use the user's effective instructions and matching project permissions. When a planning decision arose during authorized work, resume that work once the decision is resolved.
