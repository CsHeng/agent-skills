---
name: design-change
description: "Resolve material design decisions or produce a requested change design. Use when goals, boundaries, ownership, compatibility, or acceptance need a decision; not to execute an already bounded change or approved plan."
---

# Design Change

Resolve the material change boundary that is still undecided, or document established decisions when the user requests a design artifact.

## Use This Skill When

- the user explicitly requests a design artifact
- a material decision about goals, non-goals, acceptance, ownership, compatibility, or recovery remains unresolved

Do not use it merely because a task mentions architecture or may touch stable truth. An authorized bounded change or approved plan can enter implementation directly; do not route it through this Skill to obtain a `no-design` credential. Code investigation, local technical choices, and already-authorized best-effort secondary adaptation do not automatically require a new design. Design does not need implementation-depth investigation or a catalog of every secondary feature that might later be adapted or omitted. If execution exposes one real boundary conflict, resolve that decision and return to the original task rather than restarting every phase. After the user answers the blocking question, resume the original authorized work; do not end on confirmation or a promise to continue. An explicit request to document settled design decisions still belongs here, but does not authorize subsequent implementation.

Do not use it for read-only project explanation or a standalone review request.

## Design

1. Establish the relevant current truth and the concrete problem.
2. For a design question that actually remains, classify truth and boundary impact and choose `no-design`, `design-lite`, or `design-full` without equating file count with risk. `no-design` is an available conclusion, not a credential every implementation must obtain from this Skill.
3. When a remaining goal, means, terminology, owner, hard-constraint, non-goal, acceptance, or authority mismatch actually blocks progress, read `references/goal-alignment.md` and clarify only what that decision needs. Distinguish binding main goals and hard constraints from replaceable means and authorized best-effort secondary work. Stop once the next authorized step can proceed, then resume the original authorized task.
4. Compare viable boundary choices only when the change creates or materially alters a persisted architecture boundary. Compose `architecture-patterns` for that decision.
5. Record the chosen scope, explicit non-goals, future phases, acceptance evidence, truth impact, recovery policy, implementation surface, and any authorized best-effort secondary discretion. Record those boundaries and that discretion; do not catalog every possible secondary failure or freeze glue around a specified library.
6. Produce a stable, reviewable design artifact when the chosen depth requires one.
7. Decide whether independent review is required by an explicit user request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment.
8. When review is required, request a bounded `review-change` evaluation and adjudicate its read-only candidate findings. Repair accepted defects within the confirmed design inputs and recheck affected evidence. Continue while there is an evidence-backed in-scope path; use targeted rereview when changes invalidate prior review evidence or an independent question remains. Do not impose a default repair count, reopen settled findings without new evidence, or change the confirmed goals to manufacture acceptance. Stop for a concrete unresolved decision, unavailable prerequisite, lack of a viable path, or an explicit invocation budget; report the reason and incomplete work. Once the requested artifact meets its requirements and no material issue remains, finish without redundant review.

## Decision States

- `ready_for_approval`: the design and any required review evidence are complete
- `needs_more_design`: a required design decision remains unresolved
- `split_scope`: the proposed milestone is not one coherent design surface
- `manual_checkpoint`: progress depends on a user or external decision; investigable facts and generatable products are not this state

Approval belongs to the user. Do not mark a design approved from review success alone, infer approval from a later implementation request, or continue into planning unless the request already authorizes that next step.

## Artifact Guidance

A design artifact should make these items easy to find:

- objective, current truth, hard constraints, and any authorized best-effort secondary space
- scope, non-goals, and future phases without requiring an exhaustive secondary-feature catalog
- chosen boundary and discarded material alternatives
- acceptance evidence and truth impact
- recovery policy and any exact approval-sensitive action
- review decision and, when review ran, its verdict and adjudication summary
- approval status

Keep the live artifact limited to currently effective goals, hard constraints, authorized discretion, ownership, acceptance, and real pause conditions. Distinguish user decisions from investigable facts, implementation products to generate, and executor means. Valuable historical revisions belong in stage records and may be cited shortly; do not copy old gate exemptions into the live design.

Use guarded rollback only when a concrete hazard makes it safer than forward repair and the trigger, target, and verification are explicit. Otherwise prefer fix-forward recovery.

Keep Markdown paragraphs and list items naturally unwrapped. When a document has several independent scopes, use stable unique labels rather than restarting ambiguous numbered lists.

When the user explicitly asks to grill, stress-test, harden, challenge, or interrogate a design or plan, read `references/stress-test-mode.md`. Ordinary bounded clarification does not enable that mode.
