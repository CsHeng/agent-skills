# Structural Alternatives

Use for a requested reassessment of an owned architecture, replacement of a bespoke mechanism, or comparison of structural refactoring and rewriting. Bound the inquiry to the requested responsibility. Preserve required outcomes rather than every incidental property of the old implementation.

## Decision Evidence

Identify the responsibility currently owned, observable behavior, consumers, data and compatibility obligations, and the maintenance burden the user actually wants to reduce. Preserve the user's declared maintenance horizon and selected constraints; the current slice's line count is not the lifetime cost.

Compare continuing the current implementation, local simplification, and a concrete mature alternative. Check the project's existing facilities and primary documentation before declaring an alternative inadequate. Use targeted source or a bounded experiment only for a material unanswered question. Stop when the evidence supports a decision; do not exhaust the ecosystem or create a recurring scoring exercise.

Count migration, adapter glue, deployment and dependency ownership, licensing/platform constraints, verification, maintenance, and future extension costs. A larger one-time refactor or rewrite can be justified when it removes durable responsibilities; sunk cost is not a reason to retain the current implementation. Conversely, popularity or fewer local lines does not prove lower total ownership. User-stated expansion plans and established framework choices are valid inputs, not unsupported forecasts to discard.

For a new bespoke component, name the specific gap, reliability constraint, or integration/performance advantage. Lack of investigation is not evidence that mature options cannot work. Verification and recovery mechanisms must justify their own maintenance cost too; do not automatically recreate every historical defense in the replacement.

## Return And Stop

Return the bounded current responsibility, verified alternative capability and gaps, retained contracts, migration consequences, expected maintenance tradeoff, uncertainties, and whether a separate design decision is needed. Distinguish evidence from estimates. No worthwhile replacement is a valid result.

A recommendation may favor a substantial migration, but does not itself authorize mutation or create a mandatory plan. Continue into bounded implementation when the user's request already covers it; otherwise return the decision needed. Do not turn each implementation round into an architecture audit.
