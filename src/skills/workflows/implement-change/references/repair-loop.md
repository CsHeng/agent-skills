# Focused Implementation Repair

Read this reference when verification exposes an in-scope defect or a bounded review returns causally supported findings. A repair is bounded by its objective, scope, authority, and acceptance evidence, not by a default number of attempts.

1. Establish the current failure and its connection to the authorized acceptance baseline. The implementing agent adjudicates every material review candidate; reviewer preference is not repair authority.
2. Diagnose the smallest supported cause. Combine related accepted findings when they share that cause, preserve unrelated user changes, and modify only authorized surfaces.
3. Apply the same-slice cut from Implement And Verify and rerun the affected checks and declared verification. Do not weaken the oracle to fit the repair. A mistaken test may be corrected only against independent approved contract evidence and within existing authority, retaining the rationale and required review.
4. Judge the current version. If a defect remains and evidence supports another in-scope step, continue diagnosis and repair. A second or later failure is not itself a stopping condition.
5. Request targeted rereview only when the repair changes evidence relied on by the prior review, an independent question remains, or an applicable rule requires it. Bound that invocation to the repair, affected boundaries, and unresolved findings. Reuse still-valid dispositions; do not reopen them without new evidence. A new regression cannot hide behind an old pass.
6. Complete when the authorized objective, required checks, and accepted findings are satisfied. With no new change, failure, or unresolved risk, do not repeat verification or review for its own sake.

Stop for the actual blocker:

- Contradictory acceptance, invalid design premises, or a required scope/dependency change: preserve evidence and return the appropriate `replan` or `redesign` decision, without rewriting the approved baseline.
- Missing authority, input, or environment capability: return `needs-authority` or `blocked` with the exact gap. Independently completable authorized work may proceed, but the whole task is not a pass.
- Repeated diagnosis with no new evidence and no reasonable in-scope path: return `non-convergent`, explaining excluded paths and missing evidence, not an attempt count.
- User cancellation or an explicit invocation time, call, or resource budget: obey the limit and report `blocked` with current evidence and remaining work. Budget exhaustion is neither success nor proof of an impossible objective.

The reviewer remains read-only and never owns repair or continuation. Pre-existing, unrelated, future-phase, speculative, and plan-expanding observations do not enter the repair. Progress and evidence may be recorded; goals, non-goals, authority, dependencies, and acceptance may not be silently changed.
