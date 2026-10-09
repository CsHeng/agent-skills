---
name: design-change
description: "Resolve material design decisions or produce a requested change design. Use when goals, boundaries, ownership, compatibility, or acceptance need a decision; not to execute an already bounded change or approved plan."
---

# Design Change

Resolve the decision needed to achieve the user's outcome with a maintainable solution, or document established decisions when a design artifact is requested. Judge options by useful behavior and the operating, deployment, and maintenance burden they leave behind.

## Use This Skill When

- the user explicitly requests a design artifact
- a material decision about goals, non-goals, acceptance, ownership, compatibility, or recovery remains unresolved

An authorized bounded change or approved plan can enter implementation directly. Code investigation, local technical choices, and in-scope simplification do not require a design phase or a `no-design` credential. Resolve one newly exposed boundary conflict and return to the original task; do not restart every phase or investigate every possible secondary feature.

A request to document settled design decisions does not authorize subsequent implementation. Read-only project explanation and standalone review use their own workflows.

## Outcomes And Constraints

Start with the user's problem, the behavior that would resolve it, and the constraints that protect a real interest. Before proposing a mechanism, compatibility promise, or verification requirement, establish the current need and compare its total maintenance cost with a simpler way to meet that need. Apply `development-standards` as the shared baseline; this is ordinary design judgment, not a separate simplification audit or form.

Separate those requirements from the model's proposed means. A guard, compatibility layer, checksum, receipt, task split, or verification method does not become an indispensable user requirement merely because the model wrote it into a design and received general approval. Preserve explicitly user-fixed choices, required behavior, applicable repository contracts, and actual safety and authority boundaries; revise derived mechanisms when a simpler approach still satisfies them. When a mechanism is simplified or removed, recompute the verification the remaining outcome needs; an old failure matrix does not transfer automatically. A real retained-state or recovery boundary still needs its corresponding evidence.

For a migration or replacement, compare the burden removed with the code, tests, dependencies, deployment steps, and maintenance introduced. Include retaining the current implementation or making a smaller change among viable options. Source-tree cleanliness, language consistency, and a completed inventory do not establish runtime or maintenance benefit. Keep performance claims tied to representative measurements; ordinary tests and documentation need not adopt the product's implementation language or runtime.

Read `references/goal-alignment.md` when an actual goal-means mismatch, material tradeoff, acceptance ambiguity, or authority gap needs resolution. Investigate accessible facts and leave local implementation choices with the executor. Ask the owner only for the decision that changes the outcome or a real boundary, then resume authorized work.

## Design

1. Establish enough current project truth to explain the problem and the useful delivery endpoint. Code describes implemented behavior; documents and diagrams describe human intent and may be out of date. Distinguish proposed delivery from the current request and matching permission; a design-only request remains design-only.
2. Choose the depth the decision needs: `no-design`, `design-lite`, or `design-full`. File count and documentation length do not establish risk, and these labels are not prerequisites for implementation.
3. Compare viable options against the outcome and maintenance burden. Check existing project capabilities, host primitives, official tools, and mature implementations before proposing a durable general-purpose mechanism; stop investigating when the choice is supported. Compose `architecture-patterns` only for a material persisted architecture boundary.
4. State the chosen behavior, material reasons, protected boundaries, ownership, and evidence that will distinguish success from failure. Describe compatibility or recovery machinery only for an actual consumer, state transition, or failure that requires it. Leave replaceable implementation details open.
5. When a design artifact is needed, make it reviewable at the same level as the decision. Use the project's document owner and conventions; a small design may be a few connected paragraphs.
6. Obtain independent review when explicitly requested, required by an applicable rule, or justified by concrete risk or uncertainty. Request a bounded `review-change` evaluation; the caller adjudicates findings and repairs accepted defects. Review must examine unnecessary mechanisms and gates as well as missing required behavior.
7. Recheck evidence affected by accepted changes. Finish when the requested decision or artifact is supported and no material issue remains. Do not add review rounds or broaden acceptance merely to seek more confidence. If a real decision or prerequisite still blocks progress, report that specific remainder and continue independent authorized work.

## Artifact Guidance

Make the outcome, current truth, user-fixed constraints, chosen approach and rationale, ownership, necessary acceptance, and useful delivery endpoint easy to find. Include non-goals, recovery, review conclusions, or unresolved approval only where they help a future executor act correctly. Do not turn this guidance into a mandatory form.

Keep the currently effective account separate from history. A source path, version, or short explanation is usually enough to locate supporting evidence; ordinary local designs do not need `design_sha256`, revision digests, baseline hashes, or a provenance chain. Retain an exact identity only where the actual interface or protected operation needs it. Judge evidence by the behavior, inputs, and conditions it covers, and refresh it when a relevant change invalidates that claim.

Use a diagram when relationships, ownership, or a state transition are clearer visually; let it replace repetitive prose. Keep meaningful explanations and exceptions beside it. Documents and diagrams are not proof of system behavior: test the implementation against the intended outcome, not document bytes, wording, or diagram contents. Implementation changes should be reflected in the existing human-facing explanation rather than enforced by new document tests.

Keep Markdown paragraphs and list items naturally unwrapped. Follow declared document ownership rather than copying a design into each affected repository.

## Authority And Completion

Design describes authority; it does not grant it. Commit, push, publication, installation, deployment, destructive cleanup, and external changes need matching user or project authority. Consume existing approval for the same actions and targets without asking again. A later instruction may authorize the next stage, but review success or a proposed endpoint cannot do so.

Use guarded rollback only when a concrete hazard makes it safer than forward repair and the trigger, target, and verification are understood. Do not create recovery machinery for hypothetical failures of ordinary reversible work.

- `ready_for_approval`: the requested design and any required review are complete; identify an approval only if one is actually outstanding
- `needs_more_design`: a material design decision remains unresolved
- `split_scope`: the proposed milestone does not form a coherent change
- `manual_checkpoint`: a user or external decision blocks the affected action; accessible facts and agent-generated products do not qualify

An explicitly requested design ends at its requested endpoint. A decision made during already-authorized implementation returns to that work once resolved. Do not end merely on confirmation or a promise to continue.

## Related Decisions

Honor explicit framework choices and maintenance horizons without adding speculative features. A settled choice is not automatically reconsidered during planning or implementation; new evidence must identify the material premise that changed. Ordinary subtraction within the current scope stays with the executor. When the user requests a broader simplification assessment, read only `references/simplification.md` in `skills-routing` to select the appropriate code, test, or documentation analysis; its conclusions do not themselves authorize implementation.

When the user explicitly asks to grill, stress-test, harden, challenge, or interrogate a design or plan, read `references/stress-test-mode.md`. Ordinary clarification does not enable that mode.
