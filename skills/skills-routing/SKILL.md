---
name: skills-routing
description: "Select and compose skills when coding-task ownership is unclear or skill-selection guidance is requested. Also resolve open choices about simplification, implementation language, ad hoc tools, or verification methods, and guide session and recovery boundaries. Established workflows, settled methods, and routine commands proceed directly."
---

# Skills Routing

Resolve the question that is actually open. A request that explicitly names or confidently matches another skill goes directly to it; `skills-routing` is not a mandatory entry, a lifecycle, or a runtime/model dispatcher. Settled language and verification choices, routine commands, and ordinary cleanup stay with the current task.

## Read Only The Relevant Branch

Read the reference that answers the current question, not every branch. A workflow may read a method reference directly without reselecting its primary skill or loading skill-selection and session guidance.

| Open question | Read when needed |
| --- | --- |
| Which skill owns an ambiguous request, or how should skills compose? | [Skill Selection](references/routing.md) and [Discovery Cases](references/routing.toml). |
| What unnecessary responsibility can disappear from code, tests, documents, or supporting mechanisms? | [Simplification](references/simplification.md). |
| Which language fits new persisted code or an authorized migration? | [Language Selection](references/language-selection.md). |
| Which ad hoc CLI or command composition fits a non-trivial task? | [Tool Selection](references/tool-selection.md). |
| What executable evidence would establish the required outcome? | [Oracle Selection](references/oracle-selection.md). |
| How should recalled facts, compaction, or a handoff preserve the current task? | [Memory And Recovery](references/memory-boundary.md); [Phase Boundaries](references/phase-boundary-decision-tree.md) only when choosing context transfer after a completed phase. |
| Does an ambiguity require clarification, or how does an explicit preference apply? | [Interaction And Decision Boundaries](references/preference-contract.md). |

## Keep The Current Owner And Authority

Keep one primary response owner, using the composition guidance in `output-styles`. Method references contribute the decisions and evidence that owner needs; their output lists do not impose extra formats, broaden the requested investigation, or create a second report, mandatory phase, or approval gate. A simplification audit stays read-only; sufficiently bounded authorized application continues through `implement-change`. Review enters through `review-change` when requested or otherwise applicable.

Recovery reconciles actual changes, the current goal and approval baseline, unadjudicated reports, and any still-valid executor. It does not restart skill selection, redispatch completed work, accept an unverified candidate, or invent authority. Persistent recovery preferences remain harness-global; project records preserve task-specific decisions. Host capability governs continuation, and raw sessions are not a way around workspace or permission checks.
