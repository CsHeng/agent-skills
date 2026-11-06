---
name: skills-routing
description: "Select and compose skills when coding-task ownership is unclear or skill-selection guidance is requested. Also resolve open choices about simplification, implementation language, ad hoc tools, or verification methods, and guide session and recovery boundaries. Established workflows, settled methods, and routine commands proceed directly."
---

# Skills Routing

Resolve the question that is actually open. A request that explicitly names or confidently matches another skill goes directly to it; this skill is a method library and a tie-breaker, not a mandatory entry, lifecycle, or runtime dispatcher. Settled language and verification choices, routine commands, and ordinary cleanup stay with the current task.

## Read Only The Relevant Branch

A workflow may read a method reference directly without reselecting its primary skill.

| Open question | Read |
| --- | --- |
| Which skill owns an ambiguous request, or how should skills compose? | [Skill Selection](references/routing.md) and [Scope Contracts](references/routing.toml). |
| What unnecessary responsibility can disappear from code, tests, documents, or supporting mechanisms, or should a bespoke mechanism be replaced? | [Simplification](references/simplification.md). |
| Which language fits new persisted code or an authorized migration? | [Language Selection](references/language-selection.md). |
| Which ad hoc CLI or command composition fits a non-trivial task? | [Tool Selection](references/tool-selection.md); nested interpreters and mutation safety in [Ad Hoc Command Composition](references/adhoc-command-composition.md). |
| What executable evidence would establish the required outcome? | [Oracle Selection](references/oracle-selection.md). |
| How should recalled facts, compaction, or a handoff preserve the current task? | [Memory And Recovery](references/memory-boundary.md); [Phase Boundaries](references/phase-boundary-decision-tree.md) when choosing context transfer after a completed phase. |
| Does an ambiguity need clarification, or how does an explicit preference apply? | `references/goal-alignment.md` in `design-change`. |

## Keep The Current Owner And Authority

Reply composition follows `output-styles`; method references contribute decisions and evidence without an extra phase or approval gate. A simplification audit stays read-only, and bounded authorized application continues through `implement-change`. Recovery reconciles actual changes, the current goal and approval baseline, unadjudicated reports, and any still-valid executor; it neither restarts skill selection nor invents authority, and raw sessions are not a way around workspace or permission checks.
