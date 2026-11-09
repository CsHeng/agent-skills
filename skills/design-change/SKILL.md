---
name: design-change
description: "Resolve material design decisions or produce a requested change design. Use when goals, boundaries, ownership, compatibility, or acceptance are undecided; settled changes—even across multiple files or repositories—go to implement-change, and open execution ordering or coordination goes to plan-change."
---

# Design Change

Resolve the decision needed to achieve the user's outcome with a maintainable solution, or document established decisions when a design artifact is requested. Judge options by useful behavior and the operating, deployment, and maintenance burden they leave behind, with `development-standards` as the baseline.

## Use This Skill When

- the user explicitly requests a design artifact
- a material decision about goals, non-goals, acceptance, ownership, compatibility, or recovery remains genuinely undecided

Resolve one newly exposed boundary conflict and return to the original task. A request to document settled decisions authorizes no implementation. When the outcome is settled and only the evidence that would prove it is open, use `references/oracle-selection.md` in `skills-routing`. When the user asks to grill, stress-test, harden, challenge, or interrogate a design or plan, read [Stress-Test Mode](references/stress-test-mode.md).

## Outcomes And Constraints

Start with the user's problem, the behavior that would resolve it, and the constraints that protect a real interest. Before proposing a mechanism, compatibility promise, or verification requirement, establish the current need and compare its total maintenance cost with a simpler way to meet it. Separate those requirements from the model's proposed means, and read [Goal Alignment](references/goal-alignment.md) when a goal-means mismatch, material tradeoff, acceptance ambiguity, authority gap, or clarification question needs resolution.

Design the target state. Replacement, cutover, dual-running, and rollback follow `references/replacement-and-cutover.md` in `development-standards`; a design-only request authorizes neither route's execution.

## Design

1. Establish enough current project truth to explain the problem and the useful delivery endpoint. Keep a design-only request design-only.
2. Choose the depth the decision needs; file count and document length do not set it, and a depth label is not a prerequisite for implementation.
3. Compare viable options against the outcome and maintenance burden, including keeping the current implementation or making a smaller change. Check existing project capabilities, host primitives, official tools, and mature implementations before proposing a durable general-purpose mechanism, and stop investigating when the choice is supported. Compose `architecture-patterns` for a material persisted architecture boundary.
4. State the chosen behavior, material reasons, protected boundaries, ownership, and the evidence that will distinguish success from failure. Describe compatibility or recovery machinery for an actual consumer, state transition, or failure. Leave replaceable implementation details open.
5. When an artifact is needed, make it reviewable at the level of the decision, in the project's document owner and conventions; a small design may be a few connected paragraphs.
6. Obtain a bounded `review-change` evaluation when explicitly requested, required by an applicable rule, or justified by concrete risk or uncertainty, supplying known facts and accessible sources; adjudicate findings and repair accepted defects. Review examines unnecessary mechanisms and gates as well as missing required behavior.
7. Recheck evidence affected by accepted changes and finish when the decision or artifact is supported and no material issue remains. In the closing response, distinguish a supported design from readiness to execute and name any material missing or unverified prerequisite.

## Artifact Guidance

Make the outcome, current truth, user-fixed constraints, chosen approach and rationale, ownership, necessary acceptance, and delivery endpoint easy to find; include non-goals, recovery, review conclusions, or unresolved approval where they help an executor. Mark the user-fixed intent that should outlive this change, such as durable outcomes, preferences, rationale, and still-tempting rejected alternatives, separately from one-change detail, so `sync-truth` can promote it to the stable owner at delivery. Preserve known facts that affect feasibility, protected boundaries, or necessary execution in the artifact or an accessible owner record, with safe input references in place of secret values and supplied facts distinct from assumptions. A source path, version, or short explanation locates supporting evidence. Use a diagram when relationships, ownership, or a state transition are clearer visually, and follow declared document ownership and `organize-docs` prose conventions.

## Authority And Outcomes

Design describes authority; it does not grant it. Commit, push, publication, installation, deployment, destructive cleanup, and external changes need matching user or project authority, consumed without re-asking when already granted for the same actions and targets. A settled framework choice or maintenance horizon is reconsidered only when new evidence identifies the material premise that changed; a requested broader simplification assessment uses `references/simplification.md` in `skills-routing`.

- `ready`: the requested design and any required review are complete; name an approval only when one is actually outstanding
- `needs-decision`: qualified as `design` when a material design decision remains unresolved, or `user` when a user or external decision blocks the affected action
- `split-scope`: the proposed milestone does not form a coherent change

An explicitly requested design ends at its requested endpoint. A decision made during already-authorized implementation returns to that work once resolved.
