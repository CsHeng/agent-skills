# Skill Composition

This repository defines portable semantic capabilities, not an agent loop or an orchestration runtime.

## Ownership

| Concern | Owner |
| --- | --- |
| Messages, model turns, tool execution, continuation, and session lifecycle | compatible agent host |
| Request interpretation, Skill selection, sequencing, evidence judgment, optional review, adjudication, and final response | active coding agent |
| Reusable analysis, design, planning, implementation, review, documentation, policy, testing, tool, and Git methods | the selected Skills |
| Mutation, destructive action, external effect, publication, and deployment authority | user and repository or environment policy |

One primary Skill owns the response order and conclusion. Matching session, discipline, policy, tool, or review-component Skills may contribute bounded semantic overlays. A directly named or confidently matched Skill runs without `use-coding-skills`; the router is only ambiguity and session-boundary guidance.

## Independent Capabilities

Analysis, design, planning, implementation, review, truth maintenance, and completion judgment are independently selectable capabilities. They do not form a mandatory sequence. An explicit bounded mutation request may enter implementation directly, while unresolved architecture may require design and execution ordering may require a plan.

Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. `review-change` receives one bounded target and may select an optional read-only evaluator. The active coding agent adjudicates candidate findings and owns any repair.

## Excluded Mechanics

`contracts/skills.toml` and the installed routing reference support authoring, discovery projection, semantic dependencies, trigger cases, and response composition. They do not define a runtime mode, fixed phase graph, implicit review, task scheduler, attempt ledger, replay protocol, actor or model binding, or completion settlement.

Plans may still describe dependencies, safe isolation, verification, authority, and recovery because those facts make a bounded change executable. They remain guidance consumed by the active coding agent rather than state for a repository-owned controller.
