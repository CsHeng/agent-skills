---
name: review-change
description: "Review one bounded design, plan, or implementation target; return evidence-backed candidate findings and one verdict without mutating the target or synthesizing missing lifecycle work."
---

# Review Change

Review exactly one supplied target and keep final repair judgment with the calling agent.

## Use This Skill When

- `design-change`, `plan-change`, or `implement-change` requests its single bounded review
- the user directly asks to review a specific design, plan, diff, or implementation slice

A standalone review needs only a bounded target and review question. Do not require or create an upstream design, plan, implementation state, approval record, or lifecycle sequence merely because review was requested.

## Review Path

Review directly when the target is small or delegation is unavailable. For a non-trivial stable target, one independent reviewer may be useful when the active agent environment supports it.

If a relevant review Skill is currently discoverable, use it as the evaluator:

- design target: `review-design`
- plan target: `review-plan`
- implementation target: `review-implementation`

Otherwise perform the same bounded evidence-based review directly. Availability of those evaluator Skills is optional; do not assume a particular repository, provider, command name, or discovery mechanism.

An evaluator receives only the bounded brief, remains read-only, returns candidate findings, and must not delegate recursively, invoke another lifecycle phase, repair files, or widen scope.

## Bounded Brief

Include only what is needed to review the target:

- target class and objective
- goals, non-goals, and acceptance criteria supplied by the caller
- exact artifact, diff, or changed files
- declared verification and current evidence
- allowed supporting files, each with a reason

Stop with `manual-decision-required` when the target itself is missing or cannot be bounded. Do not reverse-engineer missing lifecycle artifacts.

## Candidate Findings

Each material candidate should include:

- concrete evidence and location
- causal connection to the reviewed target
- violated requirement or correctness risk
- consequence and confidence
- smallest in-scope repair, when one exists

Exclude pre-existing, unrelated, future-phase, speculative, and low-confidence observations from blocking findings. A critical out-of-scope security or data-loss risk may require a manual decision but never silently expands repair authority.

The calling agent adjudicates candidates as accepted, rejected, deferred, or requiring a plan/design decision. The reviewer never performs the repair and never decides lifecycle continuation.

## Verdicts

- `pass`: no material causally bound finding remains
- `needs-fixes`: one or more supported findings have an in-scope repair
- `manual-decision-required`: evidence or authority outside the review boundary is required
- `split-scope`: the supplied target cannot remain one bounded review surface
- `needs-design-decision`: architecture intent must change
- `needs-plan-change`: implementation scope or acceptance conditions are insufficient

Return one verdict with candidate findings and relevant verification gaps. Review and verification remain distinct evidence; neither invents the other.
