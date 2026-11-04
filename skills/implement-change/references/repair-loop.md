# Focused Implementation Repair

Read this when verification exposes an in-scope defect or a bounded review returns causally supported findings. A repair is bounded by its objective, scope, authority, and acceptance evidence, not by a number of attempts.

## Adjudicate Findings First

The implementing parent decides each material candidate before any repair runs. Record the disposition as a plain word with its reason: accepted; rejected because there is no causal link to the change, the defect is pre-existing and does not block delivery, it is out of scope, or the evidence is insufficient; deferred to a named follow-up; or escalated as a design or plan decision. Severity and reviewer preference do not widen scope. A prior disposition stands while its evidence applies to the current version; a different reviewer alone is not new evidence, and an earlier pass does not cover a new regression.

Before treating an unavailable gate as a completion blocker, identify the approved outcome or changed behavior that needs it; prepare obtainable prerequisites within existing authority and keep genuine capability gaps visible. Required positive evidence stays required; a negative preflight does not satisfy it.

## Repair

1. Connect the failure to the authorized acceptance baseline. Admit it when evidence shows it blocks the authorized outcome or necessary correctness or safety within the chosen design and authority; thematic relevance, a red test, an accepted label, or a small diff alone is not that evidence. When the selected mechanism produces a growing repair stream, or review rounds keep finding defects inside supporting test, fixture, or simulation scaffolding, evaluate deleting or simplifying that mechanism before polishing it. A worker diagnoses and repairs ordinary local failures within its brief without returning each red-green iteration.
2. Diagnose the smallest supported cause. Combine accepted findings that share it, preserve unrelated user changes, and modify only authorized surfaces. For delegated follow-up, prefer the original valid worker through the host's continuation path; [Delegated Execution](delegated-execution.md) covers the incremental brief and capability failures.
3. Complete related repairs, remove mechanisms they made unnecessary, and rerun the checks the repair invalidated; add coverage for newly affected behavior and reuse unaffected results. Correct a mistaken or over-specified assertion from actual requirements and consumer evidence while keeping verification of the required outcome; a self-invented test or earlier model-declared check list is revisable, and a genuinely required result keeps its oracle.
4. Judge the current version with evidence that covers its actual candidate; a second or later failure is a reason to continue diagnosis, not to stop. Local check success does not settle parent acceptance.
5. Close a narrow deterministic repair on the caller's direct check of the diff (dead scaffolding deleted, a path, import, assertion, or schema field fixed) when it changes no broader design assumption. Request targeted rereview when the repair changes a premise the prior review relied on, an independent boundary question remains, or an applicable rule requires it, bounded to the repair and unresolved findings.
6. Complete when applicable evidence supports the authorized outcome and accepted findings are resolved. Disclose authorized secondary tradeoffs and unrelated existing failures separately; a broader suite's unrelated failure neither invalidates narrower evidence nor adds a goal.

## Stop For The Actual Blocker

- Contradictory acceptance, an invalid design premise, or a required scope or dependency change: preserve evidence and return `needs-decision` qualified as `plan` or `design`, leaving the approved baseline unchanged. Local difficulty, one failed attempt, or an authorized secondary omission is not that decision.
- Missing authority, input, or environment capability: return `needs-decision: authority` or `blocked` with the exact gap. Independently completable work proceeds; the whole task is not a pass. After the user answers, resume the original repair.
- Repeated diagnosis with no new evidence and no reasonable in-scope path: return `blocked`, stating what was tried, excluded, and still missing.
- User cancellation or an explicit invocation time, call, or resource budget: obey it and return `blocked` with current evidence and remaining work.

The reviewer stays read-only and never owns repair or continuation. Progress and evidence may be recorded; goals, non-goals, authority, dependencies, and acceptance change only through their owner. If a secondary adaptation would make a later production action exceed the approved boundary, pause that action and continue independent authorized repair.
