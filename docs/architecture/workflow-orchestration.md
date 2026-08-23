# Workflow Orchestration

This document is the canonical maintenance view of request discovery, workflow routing, lifecycle ownership, the installed implementation invocation DAG, and the controller-owned repair loop. It explains the contracts but does not replace them.

## Truth Precedence

When prose, diagrams, and runtime behavior disagree, resolve drift in this order:

1. `contracts/workflow-modes.toml` defines mode requirements and phase shape.
2. `contracts/lifecycle.toml` defines kernel membership and repository-wide defaults.
3. `contracts/skills.toml` defines skill exposure, activation modes, default roles, compatibility successors, permissions, provider projection capabilities, and installed contract pointers.
4. `skills/use-coding-skills/references/routing.toml` defines semantic trigger-case ownership, installed discovery behavior, phase-to-owner mapping, review evaluators, support routes, composition, and the host-wrapper boundary.
5. `skills/implement-change/references/workflow.toml` defines the invocation subgraph and repair metadata that must travel with the installed controller.
6. `contracts/runtime-bundles.toml` defines the exact skill-local Python files and normalized lifecycle resources installed with each runtime owner.
7. The PlantUML files in `diagrams/` and the rendered SVG files in `generated/` are generated views for humans and must not be edited by hand.

`docs/plans/` records design and implementation history. It is useful for rationale and dispute resolution but is not current runtime truth.

## Installed Surface

The recommended local surface is a Git checkout whose generated `skills/` directories are exposed through live child links under `~/.agents/skills`. Claude Code and Codex retain optional native plugin marketplaces, and `npx skills` remains a compatible but non-recommended copy path. Lifecycle entry is through portable public skill IDs and native description matching or a thin host mapping; distribution must not expose the same ID through multiple active discovery paths in one tool.

Activation intent is authored once in `contracts/skills.toml`. Generation projects Codex `policy.allow_implicit_invocation` from the contract-level mode table: `native`, `conditional`, and `baseline` allow implicit invocation, while `controller` and `explicit` do not. The shared `SKILL.md` payload remains provider-neutral. Claude's effective visibility is recorded as `default-visible`; the repository does not claim an unsupported per-skill Claude visibility switch.

The nested authored tree generates one root-flat 40-skill payload. Runtime helpers are not separately discoverable skills: one authored `src/runtime/harness/` package is materialized inside each of six runtime owners, so an installed lifecycle skill resolves its own `scripts/harness/cli.py` without a provider plugin root or sibling support skill.

## Lifecycle Shape

Workflow mode selection precedes phase implementation. The selected mode determines which design, plan, review, truth-sync, recovery-policy, and evidence requirements apply.

- Read-only work routes to analysis without repository mutation.
- Micro changes use a bounded plan, execution, verification, and close path.
- Standard changes add design, review, and truth sync.
- Regulated changes require the full design, review, plan, implementation, truth-sync, and close gates plus an explicit recovery surface and fresh evidence. Classification alone never authorizes automatic rollback.
- Emergency work minimizes up-front ceremony but requires verification, post-hoc review, truth sync, and close.

Workflow skills own lifecycle transitions. Discipline, policy, tool, and review-component skills contribute methods or evidence without advancing lifecycle state.

The skill-local Python runtime classifies one typed request and advances one typed phase transition from the normalized canonical contracts. Unknown signals, contradictory modes, incomplete phase evidence, and missing human approval produce typed stops. Regulated design and plan approval occurs after their mandatory review phase; modes without an explicit review phase retain the direct design or plan gate.

## Request Discovery And Route Ownership

The harness routing sequence ([rendered SVG](generated/harness-routing-sequence.svg), [PlantUML source](diagrams/harness-routing-sequence.puml)) is generated from the installed routing contract plus the repository lifecycle and workflow-mode contracts. It shows the expected route from a user request through the optional host wrapper, native skill matching, optional ambiguity routing, lower-plane composition, mode selection, lifecycle gates, review evaluators, truth sync, and close.

Native description matching is the default discovery path. An explicitly named skill or confident direct workflow or policy match bypasses `use-coding-skills`; an ambiguous multi-stage request or explicit routing question enters it. `use-coding-skills` does not become a mandatory bootstrap or lifecycle controller.

The semantic case registry gives each request case exactly one owner. The owner skill's frontmatter description carries the positive boundary; each case declares negative boundaries, and explicit-invocation cases keep positive overrides. Optional overlays add conditional policy or technique without becoming a second response owner. Lexical hints are non-authoritative examples and are never interpreted as a keyword router. The activation and trigger-ownership view ([rendered SVG](generated/skill-trigger-ownership.svg), [PlantUML source](diagrams/skill-trigger-ownership.puml)) shows activation modes, default roles, compatibility successors, case-owner and overlay edges, controller evaluators, phase-routed controllers, and the rendering baseline.

The selected lifecycle mode determines the phase sequence, while `routing.toml` maps each phase to one workflow owner. Review requests enter through `review-change`; `review-design`, `review-plan`, and `review-implementation` remain controller-selected artifact-specific read-only evaluators. The support-route table selects `output-styles`, tooling, implementation policy, language, infrastructure, documentation, and mining overlays without granting them lifecycle authority.

A host-level AGENTS file may supply user preferences, runtime constraints, and thin public-skill entry hints. It must not duplicate the phase graph, phase-to-owner mapping, repair states, review budgets, or typed exits. Those contracts travel with the repo-owned skill surface.

Design conditionally composes architecture selection without adding another controller. When a change creates or materially changes a persisted architecture boundary, `design-change` uses `architecture-patterns` to compare the status quo, the smallest sufficient option, and structural investment against current demand, constrained resources, ownership, lifecycle cost, and observable upgrade triggers. Detailed economics and pattern guidance remain on-demand references owned by the architecture skill. Ordinary changes inside an approved boundary do not need placeholder economics metadata.

When the user explicitly requests design stress testing, `design-change` asks the complete current decision frontier as one numbered round. Questions keep stable identifiers, recommendations, tradeoffs, and dependency order; discoverable facts remain the main agent's responsibility. After each reply, the frontier is recomputed until no decision-changing question remains, while an explicit user preference may retain one-question-at-a-time interaction.

At a completed phase boundary, `use-coding-skills` chooses the first applicable context operation in this order: continue with current context, discard irrelevant context whose durable result is already recorded, create a portable handoff, delegate only when the selected skill or approved policy already permits it, or compact as the fallback. This context decision is provider-neutral and does not grant lifecycle, delegation, parallelism, or shared-write authority.

Planning conditionally composes implementation policy without adding another controller. When an approved task introduces or replaces a persisted implementation boundary, `plan-change` uses `language-decision-tree` to record the implementation archetype, language, and rationale. Existing-language edits do not need placeholder decisions. Agent ad hoc command choice remains owned by `tool-decision-tree` and does not activate persisted implementation-language selection.

Planning also owns the portable execution topology. A version-4 plan records task dependencies, named parallel groups, delegation policy, semantic execution and reasoning profiles, isolation, write sets, resource locks, batch limits, and convergence ownership. New metadata is strict and provider-neutral. A model or reasoning preference is therefore a recommendation attached to an unchanged task DAG, not permission to rewrite its serial or parallel shape.

Before task decomposition, planning clears every known non-automatable external prerequisite that the implementation needs but the agent cannot safely complete inside current authority. Account creation, interactive login or MFA enrollment, access grants, credential provisioning, subscription activation, and required physical actions are planning-admission conditions. An unresolved item returns `manual_checkpoint` with `execution_mode: not_ready`; it does not become an implementation task, planned stop, runtime contingency, or approval-ready DAG. After the user completes it, planning verifies only minimum secret-safe evidence and starts task decomposition from the cleared boundary.

Planning must also surface safe development concurrency instead of leaving it implicit. DAG independence is necessary but insufficient: a parallel group additionally requires explicit human approval, a dependency-frozen named batch, safe isolation, disjoint writable refs and resource locks, bounded width, and controller-owned convergence. When those conditions hold, the plan declares the group for active parallel execution; a concrete dependency, safety, isolation, convergence, or authority reason must justify keeping it serial.

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

`truth-sync evaluate` accepts a version-4 truth artifact whose approval status and execution-result and ledger digests are validated rather than caller booleans. `close-change` derives eligibility from a version-4 close artifact and its exact digest-linked approved truth artifact. Pending, missing, invalid, or mismatched evidence routes to its owning upstream phase. Successful judgment produces `terminal_state: closed` with `next_entry: null`; there is no successful `close-change` self-route.

## Optional Exact External Files

Repository writes and exact external-file writes are separate authorization channels. Repository `impl_file_refs`, `test_file_refs`, and the derived touch set retain relative-path semantics. A version-4 design, plan, and task declare `external_impl_file_refs` explicitly; the compiler derives a separate external touch set and requires exact design-to-plan-to-task containment. Repository-only work declares an empty external set.

## Versioned Runtime Authority

HCR-001 prevents an in-place reinterpretation of version-3 authority. All new design, plan, truth-sync, and close artifacts use contract version 4, and all new execution state uses ledger version 4. Version-4 compilation binds truth impact and scope, the complete task model, approved named batches, and runtime policy. The ledger then owns ready-set admission and immutable serial or batch provenance; caller and backend requests cannot substitute it.

Version-3 artifacts and ledgers remain readable only for immutable evidence, digest verification, and truth-sync or close evaluation for work already converged before refresh. Version-3 ledger initialization, task mutation, verification, review, repair, external evidence, admission, and binding are rejected. This compatibility boundary permits historical completion without leaving a downgrade path for new work.

Ledger writes use staged file durability, atomic promotion, and a parent-directory barrier. If a post-promotion failure is followed by proven durable restoration, the operation returns `ledger-write-failed`. If the runtime cannot prove either the promoted state or restored predecessor, it returns `ledger-durability-unknown`; the controller preserves evidence and stops instead of retrying, refreshing digests, or inventing rollback authority.

The channel is bootstrapped in two units. E1 is repository-only: it installs and verifies the contract, broker, state model, lifecycle validation, and generated bundles without naming or changing an external target. Only a later separately reviewed and approved E2 plan may consume that capability. An external task is always main-controller-owned, serial, non-delegated, bound to the controller checkout, and protected by named resource locks. It never enters a worker, explorer, command-job, parallel batch, or backend envelope.

The broker accepts only exact, canonical, existing, single-link regular files outside the repository. Before mutation, the controller binds the approved plan projection and captures one immutable metadata-only baseline. Each content change then advances a per-file chain through a durably persisted `staging` reservation, a validated `prepared` compare-and-swap intent, an `applied` after checkpoint, and completed cleanup of the exact ledger-bound private payload and sibling candidate. The first intent is rooted in the baseline; every repair intent names the preceding applied after-state as its immediate parent. File content never enters the ledger, review brief, execution result, truth-sync artifact, logs, or stable truth.

Apply or replay is valid only when the target matches the exact immediate parent or the already-applied candidate, including ref, digest, size, type, mode, owner, device, inode transition, and single-link evidence. Candidate and ledger files are fsynced before replacement, parent directories are fsynced afterward, and convergence requires the complete applied-and-cleaned chain plus current-state comparison. The execution result carries `allowed_external_touch_refs` and `verified_external_changes` separately from repository changed paths. Truth sync and close validate this historical metadata and its design/plan/task binding without rereading a live external target, so a later legitimate user edit does not rewrite execution history.

Recovery is fix-forward within the same exact ref set: replay the persisted staging or prepared checkpoint, record an already-applied candidate, or append the next parent-linked repair intent. A third state, plan-ledger drift, malformed or forked evidence, ambiguous private artifact, or incomplete cleanup stops with typed evidence; the controller never refreshes the baseline or synthesizes an applied marker. External file creation or deletion, directories or globs, symlinks or hard links, generic editors, caller-selected rename/chmod/chown, delegated or parallel mutation, raw-content evidence, and automatic rollback are explicit upgrade triggers requiring a new approved design and plan.

## Runtime Binding Backends

The controller's `execute bind` operation builds one backend-neutral core — controller identity and nonce, plan and ledger digests, binding kind, the immutable task projection or hashed review brief, derived runtime role, semantic profiles, isolation, touch set, resource locks, batch provenance, and model policy — and projects it onto a selected backend. Codex-native is the flag-absent `schema_version: 2` default; `--backend herdr` retains the explicit byte-compatible `schema_version: 1` wire shape. The neutral core is the only surface reusable contracts may reference; backend extensions record runtime evidence only, and no backend may rewrite the approved task topology, delegation policy, isolation, locks, touch sets, or oracles.

### Codex-Native Backend

The codex-native backend binds delegated reviewer, explorer, and worker actors through Codex Multi-Agent role agent files that are user-owned and never tracked in this repository. The runner resolves the project `.codex/agents/<role>.toml` ahead of the user-level agents directory, rejects symlinked project role files, and validates the selected file before any emission. Every role file pins neither model nor reasoning effort: reviewer and explorer files pin read-only sandboxes, while a worker file for a write task pins a workspace-write sandbox bounded by the per-spawn working directory of its assigned isolated worktree. A delegated task without write refs binds a read-only sandbox on the shared checkout.

The parent session is the codex-native physical baseline, while user or host instructions own concrete role families and minimum-only reasoning policy. `semantic-routing` emits no values when inheritance satisfies that policy, an effort-only uplift when the model remains valid, or model plus explicit effort when the model changes. `inherit-main` and `runtime-default` emit no per-spawn values; runtime-default evidence distinguishes configured `[agents]` defaults from parent inheritance when both defaults are absent. The codex extension binds the parent reasoning effort and active minimum, and validates every inherited, explicit, or default effective effort as monotonic against both. There is no portable role ceiling, and a stronger binding never expands explorer authority.

Pre-emission validation returns distinct typed capability stops instead of degraded bindings: multi-agent support disabled, a configured `agents.max_depth` other than 1 (an unconfigured depth is recorded as residual instruction-only enforcement evidence), missing, unparsable, or required-field-omitting role files, any model or effort pin, writable reviewer or explorer sandboxes, isolation conflicts, model-only overrides, reasoning below the parent or active minimum, unsupported required uplift, and missing per-spawn working-directory support for a delegated writer. A rejected required uplift never retries through `[agents]` defaults or below the minimum; it may use only an already-approved main-agent fallback for the unchanged task. `binding_kind=command-job` remains on the main controller or Herdr command-job path.

### Explicit Herdr Runtime Adapter

The Herdr path is selected only by an explicit `implement-change-via-herdr` request for an approved plan. It requires the initiating main agent to already be inside Herdr, reuses that pane's project workspace, and composes the existing `implement-change` controller. The controller emits a task- or review-specific binding envelope; the adapter consumes that envelope without reading the plan or mutating the task ledger.

Planning remains provider-neutral. A pure repository-search and factual-confirmation task qualifies as an `explorer` only when the approved metadata is `fast`, `light`, `shared-read-only`, and has no write refs. Explorer tasks are explicit independent task IDs that return bounded factual evidence to a main-agent synthesis task; they do not own inference or judgment. Runtime semantic routing gives this absolute cost class low reasoning by default and medium only as a ceiling. High and xhigh explorer reasoning are invalid rather than relative downgrades. Every delegated write task and every read-only task needing deeper synthesis is a `worker`. `semantic-routing`, `inherit-main`, and `runtime-default` may change physical model and reasoning selection, but never the approved DAG, isolation, authority, touch set, resource locks, or executable oracles.

Implementation-time binding records the coding-agent kind, concrete model and reasoning effort, permission and sandbox modes, native-login control-plane references, checkout or isolated worktree, and Herdr workspace, tab, pane, terminal, and optional agent-session identities. The first adapter supports Codex CLI and Grok Build CLI through separate exact native capability profiles. Reviewers and explorers are read-only, delegated writers require isolated worktrees, and nested agent delegation is disabled.

The initiating main agent remains the logical `orchestrator` and is never relaunched in a child pane. Managed child agents use the derived roles `reviewer`, `explorer`, or `worker`; their bounded display names are role-first with a stable animal mnemonic and task or attempt fragments. Opaque Herdr IDs, not names or UI focus, remain the ownership authority.

Each run creates only a no-focus background tab and its recorded panes in the caller workspace. Preflight pins the caller hierarchy and identity and admits the run into a controller-, plan-, workspace-, and batch-scoped lease. Compatible members may coexist only up to the controller-issued effective width and with disjoint resource locks. Allocation persists returned opaque resource IDs before fallible process inspection and requires a bounded stable-shell observation before starting an agent or command. Resume and cleanup revalidate the caller, lease owner, member, terminal, process argv, and available agent-session identity. Cleanup closes only resources owned by that member, retains ambiguous residue, and cannot close or release a sibling member.

Ordinary command jobs use the same controller-issued provenance and lease admission but are not agents. Their owner-only envelope fixes the checkout, literal argv, timeout, output bound, maximum concurrency, task-or-gate provenance, and resource locks while explicitly denying task selection, ledger mutation, review, repair, lifecycle, and task-success authority. Every command member counts against that validated capacity. The adapter sends one shell-safe command through positional `pane run`, records a unique process marker, waits for a unique completion marker with `pane wait-output`, and returns byte-bounded redacted output, process, and exit evidence. Exit zero is evidence only; the main controller still validates the declared oracle and converges the task.

Automated acceptance uses the repository's fake Herdr executable and must not connect to a live Herdr server. Live acceptance is a separately authorized user-run operation whose created resources must be recorded and cleaned without touching unrelated workspaces, tabs, or panes.

## Conditional Parallel Execution

Execution remains serial-first outside approved parallel groups. Inside an approved dependency-frozen batch, `implement-change` selects the maximal safe ready set up to the minimum of the approved maximum, ready frontier, runtime capacity, available actors, safe isolation width, and conflict-free writes and locks. Runtime binding records planned task IDs and width separately from the ready frontier, selected task IDs, runtime and actor capacity, effective width, exact limiting factors, and outcome.

Runtime binding supports `semantic-routing`, `inherit-main`, and `runtime-default`. Portable `deep`, `balanced`, or `fast` execution profiles and `deep`, `standard`, or `light` reasoning profiles describe task difficulty and eligibility, not exact physical effort or a ceiling. Codex-native semantic routing starts from the parent profile and applies only a required monotonic uplift; the explicit Herdr adapter retains its separate backend-specific allocation contract. No policy may change task IDs, dependencies, group membership, batch limits, isolation, touch sets, resource locks, or executable oracles. Reusable plans, skills, and stable truth do not store a user's provider model route.

Before selecting a batch, the public binding path compares the ledger's immutable task projection with the approved plan. Drift freezes dependencies and returns a typed parallel conflict with no selected task. An allowed batch may fall back to one task only when an observed runtime, actor, isolation, write-set, lock, or approved-width limiter reduces effective width to one, and it must record the exact `serial_fallback_reason`; serial-first posture alone is not a limiter. A required batch instead returns a typed capacity stop without allocating a member. Each controller envelope carries the recomputed immutable batch provenance, so runtime policy cannot silently change topology or claim unused parallel width.

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

The three retired compatibility aliases are absent. Their successor owners remain `architecture-patterns`, `development-standards`, and `logging-standards`.

## Maintenance

Regenerate the diagrams and their tracked SVG renderings after changing routing, lifecycle, workflow-mode, skills, or controller-local workflow contracts:

```bash
python3 scripts/generate-workflow-diagrams.py
```

SVG rendering requires `plantuml` on `PATH`. The optional pre-commit hook (`bash hooks/install-git-hooks.sh`) delegates to the strict aggregate check and never regenerates or stages files.

Validate that diagrams are current and syntactically valid:

```bash
python3 scripts/generate-workflow-diagrams.py --check
plantuml --check-syntax docs/architecture/diagrams
bash scripts/check.sh
```
