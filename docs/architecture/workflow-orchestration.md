# Workflow Orchestration

This document is the canonical maintenance view of request discovery, workflow routing, lifecycle ownership, the installed implementation invocation DAG, and the controller-owned repair loop. It explains the contracts but does not replace them.

## Truth Precedence

When prose, diagrams, and runtime behavior disagree, resolve drift in this order:

1. `contracts/workflow-modes.toml` defines mode requirements and phase shape.
2. `contracts/lifecycle.toml` defines kernel membership and repository-wide defaults.
3. `contracts/skills.toml` defines skill exposure, activation modes, default roles, compatibility successors, permissions, provider projection capabilities, and installed contract pointers.
4. `src/skills/session/use-coding-skills/references/routing.toml` defines semantic trigger-case ownership, installed discovery behavior, phase-to-owner mapping, review evaluators, support routes, composition, and the host-wrapper boundary.
5. `src/skills/workflows/implement-change/references/workflow.toml` defines the invocation subgraph and repair metadata that must travel with the installed controller.
6. `src/skills/workflows/implement-change/references/repair-loop.md` explains the controller's repair semantics.
7. The PlantUML files in `diagrams/` and the rendered SVG files in `generated/` are generated views for humans and must not be edited by hand.

`docs/plans/` records design and implementation history. It is useful for rationale and dispute resolution but is not current runtime truth.

## Installed Surface

Claude Code and Codex retain their native plugin marketplaces and consume the same generated public `skills/` inventory. Other agents may consume that payload through optional, consumer-managed `npx skills` guidance. Lifecycle entry is through public skills and native description matching or a thin host mapping to those skills.

Activation intent is authored once in `contracts/skills.toml`. Generation projects Codex `policy.allow_implicit_invocation` from the contract-level mode table: `native`, `conditional`, and `baseline` allow implicit invocation, while `controller` and `explicit` do not. The shared `SKILL.md` payload remains provider-neutral. Claude's effective visibility is recorded as `default-visible`; the repository does not claim an unsupported per-skill Claude visibility switch.

Each runner-owning workflow carries its own generated `scripts/harness/` runtime bundle sourced from `src/runtime/harness/`. Runtime helpers are not separately discoverable skills, and workflow execution does not depend on a provider plugin root or a sibling support skill.

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

The semantic case registry gives each request case exactly one owner with positive and negative boundaries. Optional overlays add conditional policy or technique without becoming a second response owner. Lexical hints are non-authoritative examples and are never interpreted as a keyword router. The activation and trigger-ownership view ([rendered SVG](generated/skill-trigger-ownership.svg), [PlantUML source](diagrams/skill-trigger-ownership.puml)) shows activation modes, default roles, compatibility successors, case-owner and overlay edges, controller evaluators, phase-routed controllers, and the rendering baseline.

The selected lifecycle mode determines the phase sequence, while `routing.toml` maps each phase to one workflow owner. Review requests enter through `review-change`; `review-design`, `review-plan`, and `review-implementation` remain controller-selected artifact-specific read-only evaluators. The support-route table selects `output-styles`, tooling, implementation policy, language, infrastructure, documentation, and mining overlays without granting them lifecycle authority.

A host-level AGENTS file may supply user preferences, runtime constraints, and thin public-skill entry hints. It must not duplicate the phase graph, phase-to-owner mapping, repair states, review budgets, or typed exits. Those contracts travel with the repo-owned skill surface.

Design conditionally composes architecture selection without adding another controller. When a change creates or materially changes a persisted architecture boundary, `design-change` uses `architecture-patterns` to compare the status quo, the smallest sufficient option, and structural investment against current demand, constrained resources, ownership, lifecycle cost, and observable upgrade triggers. Detailed economics and pattern guidance remain on-demand references owned by the architecture skill. Ordinary changes inside an approved boundary do not need placeholder economics metadata.

When the user explicitly requests design stress testing, `design-change` asks the complete current decision frontier as one numbered round. Questions keep stable identifiers, recommendations, tradeoffs, and dependency order; discoverable facts remain the main agent's responsibility. After each reply, the frontier is recomputed until no decision-changing question remains, while an explicit user preference may retain one-question-at-a-time interaction.

At a completed phase boundary, `use-coding-skills` chooses the first applicable context operation in this order: continue with current context, discard irrelevant context whose durable result is already recorded, create a portable handoff, delegate only when the selected skill or approved policy already permits it, or compact as the fallback. This context decision is provider-neutral and does not grant lifecycle, delegation, parallelism, or shared-write authority.

Planning conditionally composes implementation policy without adding another controller. When an approved task introduces or replaces a persisted implementation boundary, `plan-change` uses `language-decision-tree` to record the implementation archetype, language, and rationale. Existing-language edits do not need placeholder decisions. Agent ad hoc command choice remains owned by `tool-decision-tree` and does not activate persisted implementation-language selection.

Planning also owns the portable execution topology. A version-2 plan records task dependencies, named parallel groups, delegation policy, semantic execution and reasoning profiles, isolation, write sets, resource locks, batch limits, and a convergence task. New metadata is strict and provider-neutral; legacy plans retain their documented serial compatibility path. A model or reasoning preference is therefore a recommendation attached to an unchanged task DAG, not permission to rewrite its serial or parallel shape.

When the approved design carries an architecture decision, `plan-change` references that decision and stages it as reversible increments with preserved upgrade triggers; it does not rescore the architecture tradeoff. `review-design` evaluates material demand-complexity and owner-cost fit at the design boundary, while `review-plan` evaluates fidelity and executable staging without reopening selection.

## Implementation Invocation DAG

The implementation invocation DAG ([rendered SVG](generated/implementation-invocation-dag.svg), [PlantUML source](diagrams/implementation-invocation-dag.puml)) is generated from the controller-local runtime contract.

The installed subgraph has one lifecycle controller:

- `implement-change` owns plan-bound execution, verification, repair convergence, truth-sync routing, and close routing.
- `implement-change-via-herdr` is an explicit lower-plane runtime adapter that can consume controller-issued task and review bindings; it never selects tasks, mutates the ledger, adjudicates findings, repairs implementation, or advances lifecycle state.
- `review-change` is the agent-native review gate: it constructs a bounded brief, chooses preferred subagent or direct main-agent review, and adjudicates candidate evidence.
- `review-implementation` is a read-only evaluator and returns candidate evidence only.
- `sync-truth` owns bounded stable-truth mutation and its human approval gate; controller entry requires the approved plan and immutable passing execution result.
- `organize-docs` composes below `sync-truth` only when the approved plan declares a supported docs-governance predicate, and it cannot widen the stable-truth touch set.
- `close-change` owns evidence-bound judgment after truth approval and returns the terminal `closed` state without mutating the repository or executing merge, release, cleanup, commit, push, install, or deploy actions.

Reverse calls from evaluators or gates into `implement-change` are forbidden. This keeps the public invocation graph acyclic while allowing the controller to own an internal repair state machine.

After every planned task is controller-converged and implementation review and verification pass, `implement-change` records an immutable execution result bound to the approved design and plan, the canonical task ledger, review and verification references, the allowed touch set, and the declared stable-truth refs. A truth-affecting result continues directly to controller-authorized `sync-truth` preparation and stops at the pending truth approval gate; it does not ask for close first. A non-truth-affecting result may advance directly to close approval.

`close-change` derives eligibility only from the approved plan, immutable execution result, and, when required, the exact approved truth-sync artifact. Pending, missing, invalid, or mismatched evidence routes to its owning upstream phase. Successful judgment produces `terminal_state: closed` with `next_entry: null`; there is no successful `close-change` self-route.

## Explicit Herdr Runtime Adapter

The Herdr path is selected only by an explicit `implement-change-via-herdr` request for an approved plan. It requires the initiating main agent to already be inside Herdr, reuses that pane's project workspace, and composes the existing `implement-change` controller. The controller emits a task- or review-specific binding envelope; the adapter consumes that envelope without reading the plan or mutating the task ledger.

Planning remains provider-neutral. A pure repository-search and factual-confirmation task qualifies as an `explorer` only when the approved metadata is `fast`, `light`, `shared-read-only`, and has no write refs. Every delegated write task and every read-only task needing deeper synthesis is a `worker`. `semantic-routing`, `inherit-main`, and `runtime-default` may change physical model and reasoning selection, but never the approved DAG, isolation, authority, touch set, resource locks, or executable oracles.

Implementation-time binding records the coding-agent kind, concrete model and reasoning effort, permission and sandbox modes, native-login control-plane references, checkout or isolated worktree, and Herdr workspace, tab, pane, terminal, and optional agent-session identities. The first adapter supports Codex CLI and Grok Build CLI through separate exact native capability profiles. Reviewers and explorers are read-only, delegated writers require isolated worktrees, and nested agent delegation is disabled.

The initiating main agent remains the logical `orchestrator` and is never relaunched in a child pane. Managed child agents use the derived roles `reviewer`, `explorer`, or `worker`; their bounded display names are role-first with a stable animal mnemonic and task or attempt fragments. Opaque Herdr IDs, not names or UI focus, remain the ownership authority.

Each run creates only a no-focus background tab and its recorded panes in the caller workspace. Preflight pins the caller hierarchy and identity and acquires one repository-scoped lease. Allocation persists returned opaque resource IDs before fallible process inspection; resume and cleanup revalidate the caller, lease owner, terminal, process argv, and available agent-session identity. Cleanup closes only resources whose ownership remains proven, retains ambiguous residue, and releases the lease only when the owned live set is gone.

Automated acceptance uses the repository's fake Herdr executable and must not connect to a live Herdr server. Live acceptance is a separately authorized user-run operation whose created resources must be recorded and cleaned without touching unrelated workspaces, tabs, or panes. The initial decision horizon is three repository-local trials across at least two supported agent kinds; only their evidence can justify first-class controller integration, a persisted plan role, or a generic second-backend interface.

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

Native matching can compose one primary workflow with matching policy overlays, such as `review-change` with `review-implementation` and `go-guidelines` for a Go implementation review. When a host needs deterministic entry, its thin mapping points only to public skill IDs or `use-coding-skills`; the installed routing and controller contracts remain authoritative.

Compatibility IDs remain explicit entry points only: `clean-architecture` hands off to `architecture-patterns`, `quality-standards` to `development-standards`, and `security-logging` to `logging-standards`. Public IDs remain stable while their successors own the durable guidance and native semantic cases.

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
