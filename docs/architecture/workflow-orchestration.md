# Workflow Orchestration

This document is the canonical maintenance view of request discovery, workflow routing, lifecycle ownership, the installed implementation invocation DAG, and the controller-owned repair loop. It explains the contracts but does not replace them.

## Truth Precedence

When prose, diagrams, and runtime behavior disagree, resolve drift in this order:

1. `contracts/workflow-modes.toml` defines mode requirements and phase shape.
2. `contracts/lifecycle.toml` defines kernel membership and repository-wide defaults.
3. `contracts/skills.toml` defines skill exposure, roles, permissions, and the installed runtime-contract pointer.
4. `src/skills/session/use-coding-skills/references/routing.toml` defines installed discovery behavior, phase-to-owner mapping, review evaluators, support routes, composition, and the host-wrapper boundary.
5. `src/skills/workflows/implement-change/references/workflow.toml` defines the invocation subgraph and repair metadata that must travel with the installed controller.
6. `src/skills/workflows/implement-change/references/repair-loop.md` explains the controller's repair semantics.
7. The PlantUML files in `diagrams/` and the rendered SVG files in `generated/` are generated views for humans and must not be edited by hand.

`docs/plans/` records design and implementation history. It is useful for rationale and dispute resolution but is not current runtime truth.

## Lifecycle Shape

Workflow mode selection precedes phase implementation. The selected mode determines which design, plan, review, truth-sync, recovery-policy, and evidence requirements apply.

- Read-only work routes to analysis without repository mutation.
- Micro changes use a bounded plan, execution, verification, and close path.
- Standard changes add design, review, and truth sync.
- Regulated changes require the full design, review, plan, implementation, truth-sync, and close gates plus an explicit recovery surface and fresh evidence. Classification alone never authorizes automatic rollback.
- Emergency work minimizes up-front ceremony but requires verification, post-hoc review, truth sync, and close.

Workflow skills own lifecycle transitions. Discipline, policy, tool, and review-component skills contribute methods or evidence without advancing lifecycle state.

## Request Discovery And Route Ownership

The harness routing sequence ([rendered SVG](generated/harness-routing-sequence.svg), [PlantUML source](diagrams/harness-routing-sequence.puml)) is generated from the installed routing contract plus the repository lifecycle and workflow-mode contracts. It shows the expected route from a user request through the optional host wrapper, native skill matching, optional ambiguity routing, lower-plane composition, mode selection, lifecycle gates, review evaluators, truth sync, and close.

Native description matching is the default discovery path. An explicitly named skill or confident direct workflow or policy match bypasses `use-coding-skills`; an ambiguous multi-stage request or explicit routing question enters it. `use-coding-skills` does not become a mandatory bootstrap or lifecycle controller.

The selected lifecycle mode determines the phase sequence, while `routing.toml` maps each phase to one workflow owner. Review requests enter through `review-change`; `review-design`, `review-plan`, and `review-implementation` remain artifact-specific read-only evaluators. The support-route table selects `output-styles`, tooling, implementation policy, language, infrastructure, documentation, and mining overlays without granting them lifecycle authority.

A host-level AGENTS file may supply user preferences, runtime constraints, and thin public-skill entry hints. It must not duplicate the phase graph, phase-to-owner mapping, repair states, review budgets, or typed exits. Those contracts travel with the repo-owned skill surface.

Design conditionally composes architecture selection without adding another controller. When a change creates or materially changes a persisted architecture boundary, `design-change` uses `architecture-patterns` to compare the status quo, the smallest sufficient option, and structural investment against current demand, constrained resources, ownership, lifecycle cost, and observable upgrade triggers. Detailed economics and pattern guidance remain on-demand references owned by the architecture skill. Ordinary changes inside an approved boundary do not need placeholder economics metadata.

Planning conditionally composes implementation policy without adding another controller. When an approved task introduces or replaces a persisted implementation boundary, `plan-change` uses `language-decision-tree` to record the implementation archetype, language, and rationale. Existing-language edits do not need placeholder decisions. Agent ad hoc command choice remains owned by `tool-decision-tree` and does not activate persisted implementation-language selection.

Planning also owns the portable execution topology. A version-2 plan records task dependencies, named parallel groups, delegation policy, semantic execution and reasoning profiles, isolation, write sets, resource locks, batch limits, and a convergence task. New metadata is strict and provider-neutral; legacy plans retain their documented serial compatibility path. A model or reasoning preference is therefore a recommendation attached to an unchanged task DAG, not permission to rewrite its serial or parallel shape.

When the approved design carries an architecture decision, `plan-change` references that decision and stages it as reversible increments with preserved upgrade triggers; it does not rescore the architecture tradeoff. `review-design` evaluates material demand-complexity and owner-cost fit at the design boundary, while `review-plan` evaluates fidelity and executable staging without reopening selection.

## Implementation Invocation DAG

The implementation invocation DAG ([rendered SVG](generated/implementation-invocation-dag.svg), [PlantUML source](diagrams/implementation-invocation-dag.puml)) is generated from the controller-local runtime contract.

The installed subgraph has one lifecycle controller:

- `implement-change` owns plan-bound execution, verification, repair convergence, truth-sync routing, and close routing.
- `review-change` is the agent-native review gate: it constructs a bounded brief, chooses preferred subagent or direct main-agent review, and adjudicates candidate evidence.
- `review-implementation` is a read-only evaluator and returns candidate evidence only.
- `sync-truth` and `close-change` remain explicit downstream gates.

Reverse calls from evaluators or gates into `implement-change` are forbidden. This keeps the public invocation graph acyclic while allowing the controller to own an internal repair state machine.

## Conditional Parallel Execution

Execution remains serial-first. `implement-change` may bind more than one ready task only when the approved plan names a dependency-frozen batch, the human approval covers that batch, and its members have compatible dependencies, isolation, write sets, resource locks, and convergence ownership. Effective width is the minimum of the approved batch maximum, ready frontier, runtime capacity, available actors, safe isolation width, and conflict-free writes and locks.

Runtime binding supports `semantic-routing`, `inherit-main`, and `runtime-default`. Semantic routing maps portable `deep`, `balanced`, or `fast` execution profiles and `deep`, `standard`, or `light` reasoning profiles to runtime-available equivalents. `inherit-main` may reuse the main agent's model and reasoning choice, but no policy may change task IDs, dependencies, group membership, batch limits, isolation, touch sets, resource locks, or executable oracles. Reusable plans and skills do not store provider model identifiers.

Before selecting a batch, the public binding path compares the ledger's immutable task projection with the approved plan. Drift freezes dependencies and returns a typed parallel conflict with no selected task. An allowed batch may fall back to one task when effective capacity is one; a required batch instead returns a typed capacity stop.

Delegated writers use isolated worktrees derived from one dependency-frozen snapshot. A shared checkout is valid only for read-only work. Workers return bounded diffs and evidence; the main controller alone integrates them, verifies the complete group and its convergence evidence, and then unlocks external dependents.

## Repair Loop

The implementation repair loop ([rendered SVG](generated/implementation-repair-loop.svg), [PlantUML source](diagrams/implementation-repair-loop.puml)) is also generated from the installed controller contract.

The normal transition is:

```text
implement -> verify -> review -> classify -> diagnose -> repair -> verify
```

The main agent gives the reviewer only the approved task slice, exact diff, task tests, declared oracles, touch set, and justified supporting files. Findings require change causality and an explicit approved-contract violation. Severity or reviewer scope labels do not authorize repair.

The normal path is one initial bounded review, one batched repair of main-agent accepted findings, declared verification, and one focused verification review. Focused verification checks accepted findings and repair-introduced regressions; it does not reopen repository-wide discovery. At most one additional same-slice repair attempt is allowed for a proven incomplete or regressive repair.

`classify` produces one typed exit:

- `pass`: verification and review pass.
- `replan`: the approved plan or work-package order is insufficient.
- `redesign`: the architecture or boundary decision must change.
- `needs-authority`: completion requires new user authority or expanded scope.
- `guarded-rollback`: safe forward repair is unavailable and the approved task's exact rollback trigger, target, and verification are all satisfied.
- `non-convergent`: focused same-slice repair did not converge.

The recovery router maps evidence classes to the narrow owning phase. Failure count is retained only as diagnostic evidence and never widens implementation failure into dependency freeze, replan, or redesign. A plan route requires evidence that the task graph or touch set is insufficient; a design route requires evidence that the approved boundary is invalid.

Only `implement-change` mutates implementation state inside this loop. `review-implementation` never repairs, invokes a lifecycle workflow, delegates recursively, or decides continuation.

## Discovery And Bootstrap

Native matching can compose one primary workflow with matching policy overlays, such as `review-change` with `review-implementation` and `go-guidelines` for a Go implementation review. When a host needs deterministic entry, its thin wrapper points only to public skill IDs or `use-coding-skills`; the installed routing and controller contracts remain authoritative.

## Maintenance

Regenerate the diagrams and their tracked SVG renderings after changing routing, lifecycle, workflow-mode, skills, or controller-local workflow contracts:

```bash
python3 scripts/generate-workflow-diagrams.py
```

SVG rendering requires `plantuml` on `PATH`. The optional pre-commit hook (`bash hooks/install-git-hooks.sh`) regenerates and stages both automatically when diagram inputs are part of a commit.

Validate that diagrams are current and syntactically valid:

```bash
python3 scripts/generate-workflow-diagrams.py --check
plantuml --check-syntax docs/architecture/diagrams
bash scripts/check.sh
```
