# Focused Implementation Repair

Read this reference only when a bounded implementation review returns causally supported findings.

1. The implementing agent adjudicates every material candidate against the approved scope and current evidence.
2. Combine all accepted in-scope findings into one focused repair.
3. Diagnose the smallest common cause, preserve unrelated user changes, and mutate only approved surfaces.
4. Apply the same-slice cut from Implement And Verify before rerunning verification.
5. Rerun the affected checks and all verification declared by the approved plan.
6. Do not invoke another review. If verification still fails or the repair reveals insufficient scope, return `non-convergent`, `replan`, `redesign`, or `needs-authority` as appropriate.

The reviewer remains read-only. Severity and recommendation are evidence rather than repair authority. Pre-existing, unrelated, future-phase, speculative, and plan-expanding observations do not enter the repair.
