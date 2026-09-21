---
name: review-change
description: "Review one bounded design, plan, or implementation target; return evidence-backed candidate findings and one verdict without mutating the target or synthesizing missing lifecycle work."
---

# Review Change

Review exactly one supplied target and keep final repair judgment with the calling agent.

## Use This Skill When

- `design-change`, `plan-change`, or `implement-change` requests a bounded review of a current artifact or a targeted rereview of a repair
- the user directly asks to review a specific design, plan, diff, or implementation slice

A standalone review needs only a bounded target and review question. Do not require or create an upstream design, plan, implementation state, approval record, or lifecycle sequence merely because review was requested.

## Review Path

Review directly when the target is small or delegation is unavailable. For a non-trivial stable target, one independent reviewer may be useful when the active agent environment supports it.

If a relevant review Skill is currently discoverable, use it as the evaluator:

- design target: `review-design`
- plan target: `review-plan`
- implementation target: `review-implementation`

Otherwise perform the same bounded evidence-based review directly. Availability of those evaluator Skills is optional; do not assume a particular repository, provider, command name, or discovery mechanism.

An evaluator receives only the bounded brief, remains read-only, returns candidate findings, and must not delegate recursively, invoke another lifecycle phase, repair files, or widen scope. Read-only review does not grant command execution: any private verification must be supported and permitted by the host, preserve the reviewed source and protected state, and stay within the brief. Worker self-checking is not independent review.

One invocation returns one evaluation of its supplied target; this is not a limit on review calls for the whole change. The calling agent decides whether current evidence or an applicable rule needs another review. For rereview, focus on repairs, affected boundaries, and unresolved findings. Respect prior adjudications while their evidence remains valid; a new reviewer alone does not reopen a settled finding, and an old pass does not cover a new regression.

## Reviewer Continuity

For a justified follow-up on the same change, prefer the original reviewer when the host can safely continue its context, role, permissions, and current target. Supply the previous result reference, exact new candidate and delta, relevant evidence, parent dispositions, and remaining review question. Confirm the actual repair and affected regressions; neither a worker's claim nor the caller's wish to finish proves success.

The reviewer remains separate from the worker even across rounds. Do not rename a worker session to manufacture independence. A fresh view is useful for a changed material boundary, deficient prior coverage or judgment, or an explicit independent-review request, not as a fixed extra round. Respect route authority, and do not silently switch a selected model or reuse a session across repositories or roles. When valid continuation is unavailable, describe reconstruction or a new review honestly rather than claiming preserved native context.

## Bounded Brief

Include only what is needed to review the target:

- target class and objective
- goals, non-goals, acceptance criteria, and any authorized best-effort discretion supplied by the caller
- exact artifact, diff, or changed files and current candidate identity
- declared verification and evidence applicable to that candidate, including gaps or invalidated results
- allowed supporting files, each with a reason and a genuinely accessible source or bounded excerpt

Preserve the parent goal, protected behavior, authorized discretion, and important rationale without copying the entire conversation. A path outside the evaluator's readable snapshot is not supplied context. A commit identifier is not an accessible diff: provide the exact diff and necessary historical blobs, or confirm a supported bounded history-reading capability for that evaluator. Reading the working tree, reading Git history, and executing checks are different capabilities; a read-only role need not possess all three. Supply review rules inline or through explicitly accessible source files, not assumed access to the caller's home-directory Skills. On follow-up, explicitly deliver the changed artifact/delta or refresh the supported input; continuation alone does not update a captured snapshot. Preserve still-valid adjudications rather than rewriting the acceptance baseline. If a capability is unavailable, the parent may supply the missing material or review directly under existing authority, clearly naming the actual reviewer and input; do not silently switch to a writable role or another model. Execution success is not a review pass. Do not invent extra gates the supplied goals and acceptance do not require.

Stop with `manual-decision-required` when the target itself is missing or cannot be bounded. Do not reverse-engineer missing lifecycle artifacts.

## Candidate Findings

Each material candidate should include:

- concrete evidence and location
- causal connection to the reviewed target
- violated requirement or correctness risk
- consequence and confidence
- smallest in-scope repair, when one exists

Exclude pre-existing, unrelated, future-phase, speculative, and low-confidence observations from blocking findings. A critical out-of-scope security or data-loss risk may require a manual decision but never silently expands repair authority.

Check both omitted main goals or required results and overstrong invented gates. A secondary target wrongly raised into a gate, or an exhaustive secondary-feature catalog demanded where best-effort discretion already exists, is a defect. Using best-effort language to drop a required result, or deleting its oracle to manufacture a pass, is also a defect. An authorized secondary adaptation recorded with evidence is not automatically a finding. Security or oracle labels affect actual risk judgment; they do not create a fixed review count, per-file review loop, or evaluator repair right.

The calling agent adjudicates candidates as accepted, rejected, deferred, or requiring a plan/design decision. The reviewer never performs the repair and never decides lifecycle continuation.

## Verdicts

- `pass`: no material causally bound finding remains, including when authorized secondary tradeoffs are disclosed and the main goals still hold
- `needs-fixes`: one or more supported findings have an in-scope repair
- `manual-decision-required`: evidence or authority outside the review boundary is required
- `split-scope`: the supplied target cannot remain one bounded review surface
- `needs-design-decision`: architecture intent must change
- `needs-plan-change`: implementation scope or acceptance conditions are insufficient

Return one verdict with candidate findings and relevant verification gaps. Review and verification remain distinct evidence; neither invents the other.
