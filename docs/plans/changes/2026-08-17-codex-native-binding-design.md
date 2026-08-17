# Codex-Native Runtime Binding Backend And Neutral Controller Envelope Design

## Status

- design_version: 2
- decision_status: ready_for_approval
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and requested `plan-change` on 2026-08-17.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The harness separates portable plan topology from implementation-time actor and model binding, but today only two physical binding paths exist: the main agent executing serially in its own session, and the explicit Herdr terminal adapter. The controller binding envelope emitted by `execute-runner.sh` is shaped around Herdr concerns such as panes, leases, workspace identity, and terminal evidence, even though most of its content is backend-neutral provenance.

Codex CLI Multi-Agent V2 (v0.137.0+, verified against v0.147.0) now natively supports per-role model and reasoning routing: custom agent files under `.codex/agents/` or `~/.codex/agents/` pin `model`, `model_reasoning_effort`, `sandbox_mode`, and `developer_instructions` per role with the highest binding precedence, `[agents]` supplies session defaults and `max_concurrent_threads_per_session`, and the `spawn_agent` tool accepts per-spawn overrides when exposed. The primary user runs Codex CLI most of the time and wants delegated model routing to work natively there, without requiring a terminal multiplexer, while reusable plan and skill contracts stay provider-neutral.

Without this design, the semantic profiles that `plan-change` already records (`execution_profile`, `reasoning_profile`, roles derived from isolation and write refs) have no deterministic native Codex landing, and every non-Herdr delegation falls back to untyped prose guidance.

## Goals

- Add a `codex-native` runtime binding backend to `implement-change` that maps approved task roles (`worker`, `explorer`, `reviewer`) and semantic execution/reasoning profiles onto Codex custom agent files and native subagent spawning.
- Split the controller binding envelope into a backend-neutral core (controller identity, plan and ledger digests, task or review provenance, derived role, semantic profiles, touch set, isolation, resource locks, run nonce) plus per-backend extensions; the Herdr extension keeps its pane, lease, and workspace fields unchanged in behavior.
- Define repository-documented role agent file contracts for `worker`, `explorer`, and `reviewer` that encode the existing invariants natively: explorer effort low by default with medium ceiling, reviewer and explorer read-only sandbox, worker writes only in its assigned isolated worktree.
- Keep role agent files user-owned configuration: the runner validates their presence and declared invariants and returns a typed capability stop with the approved main fallback when they are missing or invalid; it does not silently create or rewrite user config.
- Preserve the main agent as sole adjudicator: delegated Codex subagents return bounded evidence to the controller; findings and claims still pass main-agent adjudication and oracle verification.
- Record codex-native physical bindings (selected agent file name, resolved model, reasoning effort, sandbox mode, thread identity when observable) as runtime evidence without changing approved task IDs, dependencies, topology, isolation, locks, touch sets, or oracles.
- Update the Herdr adapter decision horizon into a three-way comparison: codex-native backend versus Herdr adapter versus main-agent serial execution, judged on the existing three-trial evidence standard.

## Non-Goals

- No change to the sovereign lifecycle kernel, `phase_routes`, human approval gates, plan contract version 2 schema, or `plan-change` topology authority.
- No removal or demotion of the Herdr adapter in this milestone; it remains the explicit second backend for cross-CLI delegation (Grok Build), long command visibility, and terminal-lifecycle experiments.
- No provider model identifiers in plans, reusable skills, or the neutral envelope core; concrete models live only in user-owned Codex configuration and runtime binding evidence.
- No generic multi-backend registry, plugin loader, or Claude/Cursor native backend implementation in this milestone; a second native backend request is the extraction trigger for a shared interface.
- No reliance on subagent-to-subagent collaborative messaging: delegated actors must not message peers, recursively delegate, integrate peer work, adjudicate findings, repair, or advance lifecycle state.
- No unattended execution change and no new authority for delegated actors.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: false

## Boundaries

### Envelope Core And Backend Extensions

`execute-runner.sh controller-binding-envelope` gains an explicit `--backend` selector with `herdr` and `codex-native` values. The emitted envelope has:

- a neutral core: controller identity, plan digest, ledger digest, `binding_kind` (`delegated-task`, `bounded-review`, `command-job`), selected immutable task projection or hashed review brief, derived role, semantic execution and reasoning profiles, isolation requirement, touch set, resource locks, batch provenance, model policy (`semantic-routing | inherit-main | runtime-default`), and a run nonce
- a backend extension object: Herdr keeps workspace/tab/pane/lease/capability-profile fields; codex-native carries the selected role agent file name, expected sandbox mode, the declared concurrency ceiling, and, when per-spawn values are supplied, the requested model, requested reasoning effort, and their resolution source as binding evidence

The core-plus-extension model is the internal construction shared by both backends, but the two backends emit different wire shapes. `--backend herdr` (and the flag-absent default) emits the current `schema_version: 1` envelope byte-compatibly through a compatibility projection from the internal model, so the existing Herdr adapter and its contract tests stay green without semantic edits. `--backend codex-native` emits the new `schema_version: 2` core-plus-extension shape. Migrating the Herdr wire shape to version 2 is an explicit upgrade trigger, not part of this milestone. The neutral core is the only part reusable contracts may reference.

`binding_kind: command-job` is valid only for the Herdr backend; `--backend codex-native` rejects it with a typed unsupported-combination stop because Codex subagents are agents, not command executors. Long local commands stay with the main controller or the Herdr adapter.

### Codex-Native Role Binding

Role derivation is unchanged and stays plan-driven: `reviewer` for a bounded review brief, `explorer` only for approved `fast`/`light`/`shared-read-only` tasks with no write refs, `worker` for everything else delegated.

Every codex-native binding, under every model policy, spawns through the validated role agent file so that sandbox mode and developer instructions are always enforced; model policies vary only the model and effort fields the file leaves unset. The documented role agent file contract is:

- `reviewer`: `sandbox_mode = "read-only"`, no `model` and no `model_reasoning_effort` pin, developer instructions restrict output to candidate findings against the provided brief and forbid repository-wide discovery, peer messaging, and recursive delegation
- `explorer`: `sandbox_mode = "read-only"`, no `model` pin, `model_reasoning_effort` pinned to `low` or `medium`; because a file-pinned value outranks per-spawn values, `[agents]` defaults, and parent inheritance in Codex resolution, the explorer ceiling is enforced mechanically by file precedence under every model policy. A file declaring `high` or above, a writable sandbox, or a missing effort pin for the explorer role is invalid and produces a typed capability stop, never a silent downgrade or promotion.
- `worker`: no `model` and no `model_reasoning_effort` pin; write scope is bounded to the assigned isolated worktree via the spawn working directory, and instructions require returning bounded diffs and evidence and forbid integration, adjudication, and continuation decisions

Per-spawn working-directory support is a required backend capability, not an assumption: the first worker binding in a session verifies that the spawned agent operates in the assigned worktree, an unsupported runtime returns a typed capability stop with the approved delegation fallback, and the controller's existing changed-path verification remains the post-hoc oracle in all cases.

Model policy mapping on top of the always-selected role file:

- `semantic-routing` (default): the controller supplies per-spawn `model` and `model_reasoning_effort` values mapped from the approved semantic profiles; they bind the fields the role file leaves unset
- `inherit-main`: no per-spawn values; unset fields resolve through parent inheritance
- `runtime-default`: no per-spawn values with `[agents]` defaults resolving unset fields

All three change only model and reasoning binding, never topology. Because ChatGPT-authenticated sessions handle per-spawn model overrides inconsistently, a semantic-routing spawn whose per-spawn values are rejected falls back to `[agents]` defaults and records that resolution source as binding evidence instead of failing the task.

File resolution follows Codex semantics: project `.codex/agents/` over `~/.codex/agents/`. Role agent files are user-owned runtime configuration and are not part of this repository's tracked plugin payload; this repository's own trials keep them at user level or untracked, while consumer repositories may commit their own project-scoped files at their discretion, outside this design's provider-neutrality constraint on reusable contracts.

### Concurrency And Recursion

Effective width remains the existing minimum rule; the codex-native backend additionally treats `agents.max_concurrent_threads_per_session` as its runtime capacity input. Recursion control is validated, not merely recorded: pre-emission validation requires the multi-agent feature to be enabled and, when `agents.max_depth` is configured, requires it to equal `1`, returning a typed capability stop otherwise. When `max_depth` is unconfigured, the runner records its absence as binding evidence and relies on the role-file instruction denial, which is documented as residual instruction-only enforcement. Collaborative peer messaging between spawned subagents is out of contract; the controller is the only integration point.

### Skill And Prose Surface

`implement-change/SKILL.md` replaces its Herdr-specific overlay framing with a runtime-backend section describing the neutral envelope core plus the two current backends, keeping the Herdr overlay semantics intact. `implement-change-via-herdr` continues to consume controller envelopes, now reading the same core plus its Herdr extension. `plan-change` is untouched: semantic profiles and delegation policy already carry everything the new backend needs.

## Architecture Decision

- architecture_decision_id: CODEX-NATIVE-BIND-001
- decision_status: selected
- decision_horizon: Three repository-local delegated trials through the codex-native backend, compared against the existing Herdr trial series and main-agent serial execution on convergence quality, manual coordination cost, and recovery ambiguity.
- demand_evidence: The user's stated goal for delegation is model routing per role; Codex Multi-Agent V2 now provides native, officially documented per-role routing (custom agent files, `[agents]` defaults, spawn overrides) on the CLI the user runs most, removing the need for a terminal multiplexer in the common case.
- scarce_resource: Main-agent context, model spend, maintainer effort for orchestration code, and the reliability budget of Bash protocol surface.
- hard_requirements:
  - one `implement-change` lifecycle controller and unchanged approved plan topology
  - provider-neutral reusable contracts
  - read-only reviewer and explorer, isolated-worktree writers, no recursive delegation
  - evidence-based completion with main-agent adjudication
- options:
  - status quo: main-agent serial plus Herdr adapter only. Lowest new-code cost, but native Codex routing capability stays unused and every lightweight delegation pays Herdr's terminal-lifecycle complexity or falls back to prose.
  - smallest sufficient: one codex-native backend that validates user-owned role agent files, emits the neutral envelope core with a thin codex extension, and lets Codex own thread lifecycle. Selected: it reuses officially documented provider behavior instead of reimplementing lifecycle management, and shrinks rather than grows the Bash protocol surface.
  - structural investment: a generic backend registry with pluggable adapters and a formal envelope schema language. Deferred: only two backends exist, and the extraction trigger is a third concrete backend request.
- marginal_tradeoff: The backend adds envelope refactoring and role-file validation but removes the need for Herdr in the majority Codex-only case; net protocol surface shrinks because Herdr-specific fields leave the shared core.
- opportunity_cost: Work spent here defers plan-metadata slimming; that slimming is explicitly staged after this backend proves the binding path.
- owner_and_incentives: `plan-change` owns portable profiles, `implement-change` owns binding and validation, the user owns role agent files and model/cost choices in their own Codex config, and Codex owns spawned-thread lifecycle.
- comparative_advantage: Codex natively provides model routing, thread management, sandbox inheritance, and approval surfacing; the harness provides plan provenance, touch-set and oracle verification, adjudication, and typed stops. Neither duplicates the other.
- chosen_option: A codex-native binding backend plus a backend-neutral envelope core, with Herdr retained as the explicit second backend.
- upgrade_trigger:
  - a second native backend request (Claude Task, Cursor subagents) triggers extraction of a shared backend interface
  - repeated role-file validation failures across real runs trigger a repository-shipped role-file template install step gated by explicit user approval
  - trial evidence showing envelope logic remains the dominant complexity triggers the deferred Python migration of envelope construction and validation
  - a demonstrated consumer need for neutral-core fields on the Herdr path triggers migrating the Herdr wire shape from the byte-compatible `schema_version: 1` projection to the `schema_version: 2` core-plus-extension envelope together with its adapter and contract tests
- recovery_and_oracle: Removing the backend deletes the `--backend codex-native` branch, its role-file validation, and prose; the neutral core and Herdr extension remain. The boundary is protected by envelope schema tests, execute-runner smoke coverage, and the unchanged Herdr contract tests.

## Acceptance Conditions

- `contracts/lifecycle.toml`, `phase_routes`, plan contract version 2 fields, and all human gates are byte-for-byte unchanged.
- `controller-binding-envelope --backend herdr` and the flag-absent default emit the current `schema_version: 1` envelope byte-compatibly; the existing Herdr adapter contract tests pass without semantic edits.
- `controller-binding-envelope --backend codex-native` emits the `schema_version: 2` neutral core plus codex extension, and rejects emission when the selected role agent file is missing or unparsable, omits a required field, pins a model or effort where the contract forbids it, declares an invalid explorer effort pin, declares a writable reviewer/explorer sandbox, or conflicts with the task's isolation requirement; each rejection is a distinct typed stop honoring the approved delegation policy fallback.
- Every codex-native binding under every model policy selects the validated role agent file; no policy path spawns without it. The explorer effort ceiling is therefore enforced by the file pin plus Codex file precedence, which validation proves before emission.
- Pre-emission validation confirms the multi-agent feature is enabled and that a configured `agents.max_depth` equals `1`, returning a typed capability stop otherwise.
- `binding_kind: command-job` with `--backend codex-native` returns a typed unsupported-combination stop.
- A runtime that cannot honor the assigned per-spawn working directory for a worker returns a typed capability stop instead of binding a writer outside its isolated worktree.
- Reusable skills, plans, and the neutral envelope core contain no provider model identifiers; concrete models appear only in user-owned configuration and runtime binding evidence, and this repository tracks no role agent files in its plugin payload.
- Delegated writer envelopes require an isolated worktree exactly as today; reviewer and explorer envelopes carry no write refs.
- The generated root-flat payload, skill index, diagrams, README, and `docs/architecture/workflow-orchestration.md` agree on the two-backend runtime binding boundary.

## Validation

- Unit-test envelope core/extension construction and every typed rejection path in `execute-runner.sh`, including flag-absent default behavior and byte-compatibility of the `schema_version: 1` Herdr projection.
- Extend `test-execute-runner.sh` smoke coverage with codex-native envelope emission, role-file validation fixtures (valid trio, missing file, explorer missing or over-ceiling effort pin, forbidden model pin, writable reviewer), model-policy interaction cases, `max_depth` validation, and the codex-native command-job rejection.
- Keep `tests/test_implement_change_via_herdr_contracts.py` green without semantic edits as the Herdr-compatibility oracle.
- Validate role agent file fixtures with `tomllib` parsing in repository tests; do not test against a live Codex session in CI.
- Regenerate the skill index, root-flat payload, PlantUML sources, and tracked SVGs, then run `bash scripts/check.sh` and `git diff --check`.
- After implementation approval, run the three-trial evaluation series as user-observed evidence: one bounded review delegation, one explorer fact-finding slice, one isolated-worktree worker task, each through the codex-native backend in a real Codex session.

## Recovery

- Default fix-forward inside the approved touch set.
- A role-file validation failure at binding time is a typed capability stop with the task falling back to the main agent when delegation policy allows; it never mutates user configuration.
- Envelope refactoring regressions detected by Herdr contract tests roll forward by restoring extension field semantics; the neutral core schema is versioned from its first emission so consumers can reject unknown versions.
- Removing the codex-native backend is a reversible exit: delete the backend branch, its fixtures, and prose; no lifecycle, plan, or Herdr behavior depends on it.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_depth: boundary
- review_status: passed
- candidate_findings: 8 returned; 7 accepted and repaired, 1 rejected; focused verification passed with one minor sync repair (Herdr wire v2 migration added to upgrade triggers)
- review_evidence: A bounded delegated boundary review raised two blockers (model-policy paths bypassing role-file sandbox/recursion enforcement; Herdr byte-compatibility contradicting the envelope restructuring), three majors (`max_depth` recorded but not validated, unverified per-spawn working-directory capability, explorer ceiling unenforceable at bind time under `inherit-main`), and three minors. The main agent accepted and repaired seven findings: every model policy now spawns through the validated role file with model/effort fields unset except the explorer effort pin, whose file precedence enforces the ceiling mechanically; the Herdr wire shape stays `schema_version: 1` byte-compatible via a compatibility projection while codex-native emits `schema_version: 2`; `max_depth` and multi-agent enablement became pre-emission validation; worker working-directory support became a verified capability with a typed stop; codex-native `command-job` is a typed rejection; role agent files are declared outside this repository's tracked payload. The TOML-format concern was rejected with insufficient evidence because official Codex documentation defines custom agent files as standalone TOML.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and requested `plan-change` on 2026-08-17 after the delegated boundary review and focused verification passed.
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/tools/implement-change-via-herdr/SKILL.md
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/implement-change
  - skills/implement-change-via-herdr
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/codex-agents
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
