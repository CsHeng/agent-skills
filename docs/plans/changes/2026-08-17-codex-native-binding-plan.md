# Codex-Native Runtime Binding Backend Plan

## Status

- plan_version: 2
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: complete
- plan_review_status: passed_after_one_bounded_repair
- implementation_review_status: passed_after_one_bounded_repair
- implementation_verification_status: passed
- execution_stop_reason: truth_sync_required
- recommended_next_phase: truth-sync
- next_entry: sync-truth

## Upstream Design

- design_ref: 2026-08-17-codex-native-binding-design.md
- design_version: sha256:b8d41cc09b9024c61b2a8d16d7961f75adb714c4147306d1abf3990e3384ad4b.
- design_approval_status: approved.
- architecture_decision_ref: CODEX-NATIVE-BIND-001.

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
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
- verification_commands:
  - `bash -n src/runtime/harness/execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `python3 -m unittest tests.test_implement_change_via_herdr_contracts`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash scripts/check.sh`
  - `uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Add a `codex-native` runtime binding backend to the deterministic
  execute-runner so approved task roles and semantic profiles land on Codex Multi-Agent V2 custom
  agent files natively, while the Herdr wire envelope stays byte-compatible through a projection
  from a new backend-neutral internal core, without changing lifecycle authority, plan topology,
  or provider neutrality of reusable contracts.
- non_goals:
  - Change the sovereign lifecycle kernel, `contracts/lifecycle.toml`, `phase_routes`, plan
    contract version 2 fields, or any human approval gate.
  - Remove, demote, or semantically edit the Herdr adapter or its Python contract tests; migrate
    the Herdr wire shape to `schema_version: 2` (explicit upgrade trigger, not this milestone).
  - Introduce provider model identifiers into plans, reusable skills, or the neutral envelope
    core; ship or track role agent files in the plugin payload; create or rewrite user-owned
    Codex configuration.
  - Build a generic multi-backend registry or a Claude/Cursor native backend; allow
    subagent-to-subagent messaging, recursive delegation, or delegated adjudication.
  - Run live Codex sessions in CI; the three-trial evaluation series is post-approval
    user-observed evidence, not a plan task.
- future_phase:
  - Extract a shared backend interface when a second native backend (Claude Task, Cursor
    subagents) is concretely requested.
  - Migrate envelope construction to Python if trial evidence shows envelope logic remains the
    dominant Bash complexity.
  - Migrate the Herdr wire shape to the `schema_version: 2` core-plus-extension envelope when a
    consumer needs neutral-core fields on the Herdr path.
  - Slim plan task metadata after the codex-native binding path proves itself in trials.
- decision_status: ready_for_review
- oracle_strategy: Use characterization oracles for Herdr compatibility (golden `schema_version: 1`
  envelopes captured from the pre-change runner across binding kinds and model policies, asserted
  byte-identical after the refactor, plus the unchanged Herdr Python contract suite); contract
  tests for the new codex-native emission (schema shape, role-file validation fixtures parsed with
  Python `tomllib` invoked from the smoke test, every typed rejection path, model-policy
  interaction, `max_depth`
  pre-emission validation, command-job rejection); and generation/parity oracles for skill, index,
  diagram, and bundled-runner surfaces.
- acceptance_oracles:
  - `controller-binding-envelope --backend herdr` and the flag-absent default emit envelopes
    byte-identical to captured pre-change golden output, and
    `tests/test_implement_change_via_herdr_contracts.py` passes without semantic edits.
  - `controller-binding-envelope --backend codex-native` emits a `schema_version: 2` neutral core
    plus codex extension containing the selected role agent file name, expected sandbox mode,
    declared concurrency ceiling, and per-spawn model/effort resolution evidence when supplied.
  - Each invalid role-file condition returns its own typed stop honoring the approved delegation
    fallback: missing file, unparsable file, parsable file omitting a required field (for example
    a reviewer or explorer file with no `sandbox_mode` key), forbidden model pin, explorer effort
    pin missing or above medium, writable reviewer or explorer sandbox, isolation conflict with
    the task.
  - All three model policies (`semantic-routing`, `inherit-main`, `runtime-default`) select the
    validated role agent file; no policy path emits a binding without it, and only model/effort
    resolution evidence differs between policies.
  - Pre-emission validation rejects emission with a typed capability stop when the multi-agent
    feature is disabled or a configured `agents.max_depth` differs from 1, and records an
    unconfigured `max_depth` as residual instruction-only enforcement evidence.
  - `binding_kind: command-job` with `--backend codex-native` returns a typed
    unsupported-combination stop; the worker per-spawn working-directory capability check has a
    typed stop path covered by fixtures.
  - Delegated writer envelopes still require an isolated worktree; reviewer and explorer
    envelopes carry no write refs; reusable skills, plans, and the neutral core contain no
    provider model identifiers and the repository tracks no role agent files.
  - Root-flat payload, skill index, diagrams, README, and
    `docs/architecture/workflow-orchestration.md` describe the same two-backend runtime binding
    boundary and reproduce exactly from source; aggregate `scripts/check.sh`, plugin validation,
    and `git diff --check` pass.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Approved Architecture Decision

- architecture_decision_ref: CODEX-NATIVE-BIND-001.
- decision_fidelity: Implement the smallest sufficient option: one codex-native backend that
  validates user-owned role agent files, emits the neutral envelope core with a thin codex
  extension, and lets Codex own spawned-thread lifecycle. Herdr remains the explicit second
  backend with an unchanged wire shape. No backend registry, no envelope schema language, no
  tracked role files.
- reversible_increments:
  - CNB-010 refactors envelope construction internally while proving byte-identical Herdr wire
    output; reverting it restores a single-shape emitter with no consumer impact.
  - CNB-020 adds the `--backend codex-native` branch, fixtures, and typed stops as a separable
    branch whose deletion leaves the neutral core and Herdr projection intact.
  - CNB-030 changes only skill prose and the workflow contract description of runtime backends.
  - CNB-040 regenerates deterministic surfaces and stable truth; regeneration is repeatable and
    hand edits are forbidden.
- upgrade_triggers:
  - Return `needs-design-decision` if Herdr byte-compatibility cannot be preserved by an internal
    projection and the wire shape itself must change in this milestone.
  - Return `needs-design-decision` if enforcing the explorer ceiling, read-only sandboxes, or
    non-recursion requires capabilities Codex file precedence and pre-emission validation cannot
    provide.
  - Return `needs-plan-change` if implementation requires touching `plan-change` topology
    authority, lifecycle contracts, or paths outside the declared touch set.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1. All four tasks execute serially by the main controller in the current
  checkout; no delegated writers, no parallel groups, no Herdr or Codex spawning during
  implementation. The codex-native backend is exercised only through deterministic fixtures and
  smoke tests in this plan; live spawning is post-approval trial evidence.
- oracle_note: Role agent file fixtures are validated by Python `tomllib` parsing invoked from the
  execute-runner smoke test, satisfying the design's repository-test parsing requirement without a
  live Codex session.
- worker_binding_policy: not applicable in this plan; executor_mode is main for every task.
- reviewer_binding_policy: Plan and implementation review use the standard bounded reviewer path
  with main-agent adjudication; reviewers return candidates only.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes CNB-010 through CNB-040 as one continuous local implementation unit:
    refactoring `execute-runner.sh` envelope construction, adding the codex-native backend branch
    and its typed stops, creating `tests/fixtures/codex-agents` fixtures, extending the
    execute-runner smoke test, updating implement-change and via-herdr skill prose and the
    workflow contract, updating stable architecture truth and README, and regenerating the skill
    index, root-flat payload, diagrams, and bundled runners. It does not authorize commit, push,
    install, publication, provider mutation, user-config writes, live Codex or Herdr spawning, or
    close.
- runtime_contingencies:
  - X1: If the repository contains unexplained overlapping user changes in declared refs,
    preserve them and return `blocked_source_baseline` before mutation.
  - X2: If golden-envelope comparison proves the Herdr wire shape cannot stay byte-identical
    through the internal projection, stop with the captured diff and return
    `needs-design-decision`; do not semantically edit the Herdr contract tests to make them pass.
  - X3: If focused or aggregate checks fail outside causal changed paths, stop and diagnose;
    repair only accepted in-scope failures and do not weaken typed-stop, byte-compatibility, or
    provider-neutrality oracles.
- planned_stop_points:
  - none inside CNB-010 through CNB-040; successful implementation and review route to the
    separate truth-sync approval gate.
- task_ordering_rationale: Prove the neutral core cannot break the existing Herdr consumer before
  adding any new backend behavior; add the codex-native branch and its full typed-stop fixture
  matrix against that stable core; only then update prose surfaces that describe the finished
  runtime behavior; converge generated surfaces and stable truth once at the end so regeneration
  runs against final sources.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Preserve the initial tracked and untracked baseline; mutate only declared
  impl and test refs; never discard or overwrite unrelated user changes.
- compatibility_boundary: The captured golden Herdr envelopes and the unchanged Python contract
  suite are the compatibility oracle; repairs restore projection output to byte equality rather
  than adjusting the oracle. Semantic edits to the Herdr contract tests are forbidden in this
  plan.
- config_boundary: The runner reads user-owned Codex configuration and role agent files but never
  creates, rewrites, or deletes them; fixture role files live only under
  `tests/fixtures/codex-agents`.
- generated_boundary: Regenerate from `src/skills/` and harness sources, compare deterministic
  outputs, and repair source or generator causes. Generated hand edits are forbidden.
- external_boundary: Commit, push, install, deploy, provider action, publication, and close are
  not recovery actions under this plan.
- guarded_rollback: none

## Task 1: Extract the neutral envelope core with a byte-compatible Herdr projection

- task_id: CNB-010
- depends_on:
  - none
- scope_slice: Restructure `controller-binding-envelope` in `execute-runner.sh` around an internal
  backend-neutral core (controller identity, plan and ledger digests, binding kind, immutable task
  projection or hashed review brief, derived role, semantic profiles, isolation, touch set,
  resource locks, batch provenance, model policy, run nonce) plus a backend extension object; add
  the `--backend` selector with `herdr` as the flag-absent default; project the Herdr backend to
  the current `schema_version: 1` wire shape byte-identically.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - tests/test_implement_change_via_herdr_contracts.py
- verification_scope:
  - Capture golden `schema_version: 1` envelopes from the pre-change runner across delegated-task,
    bounded-review, and command-job binding kinds and all three model policies; assert the
    refactored `--backend herdr` and flag-absent outputs are byte-identical to them.
  - Reject an unknown `--backend` value with a typed stop.
  - Run `bash -n`, the focused execute-runner smoke test, the unchanged Herdr Python contract
    suite, and `git diff --check`.
- failing_oracle_first: Add the golden-envelope byte-comparison cases and the unknown-backend
  rejection case to `test-execute-runner.sh` against captured pre-change output before
  restructuring envelope construction.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - runtime-binding-contract
- task_review_depth: deep
- done_when:
  - The internal core-plus-extension model is the single construction path and the Herdr wire
    output is proven byte-identical by golden comparison.
  - The Herdr contract suite passes without semantic edits.
  - No codex-native behavior is emitted yet; the selector exists with `herdr` default.
- failure_policy: fix_forward

## Task 2: Add the codex-native backend with role-file validation and typed stops

- task_id: CNB-020
- depends_on:
  - CNB-010
- scope_slice: Implement `--backend codex-native` emission of the `schema_version: 2` neutral core
  plus codex extension; add role agent file resolution (project `.codex/agents/` over
  `~/.codex/agents/`) and validation of the reviewer/explorer/worker contracts; add pre-emission
  validation of multi-agent enablement and `agents.max_depth`; add the worker per-spawn
  working-directory capability stop path and the codex-native command-job rejection; create the
  fixture set under `tests/fixtures/codex-agents`.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - tests/fixtures/codex-agents
- verification_scope:
  - Cover a valid reviewer/explorer/worker fixture trio: reviewer and explorer read-only with no
    model pin, explorer effort pinned to low or medium, worker with no model and no effort pin;
    assert emission succeeds and the extension records file name, sandbox mode, concurrency
    ceiling, and model/effort resolution source per policy.
  - Cover each distinct typed rejection with its own fixture or configuration: missing role file,
    unparsable TOML, parsable file omitting a required field (reviewer or explorer with no
    `sandbox_mode` key), forbidden model pin, explorer effort pin missing or above medium,
    writable reviewer or explorer sandbox, isolation conflict, multi-agent feature disabled,
    configured `max_depth` not equal to 1, command-job binding kind, and unsupported per-spawn
    working directory for a worker.
  - Parse every fixture role file with Python `tomllib` from the smoke test so validity and
    invalidity claims rest on real TOML parsing, not string matching.
  - Assert `semantic-routing` supplies per-spawn model/effort evidence, `inherit-main` and
    `runtime-default` supply none, and all three record the same selected role file; assert an
    unconfigured `max_depth` is recorded as residual instruction-only enforcement evidence.
  - Assert the neutral core carries no provider model identifiers and no fixture leaks into the
    tracked plugin payload.
  - Run `bash -n`, the focused execute-runner smoke test, and `git diff --check`.
- failing_oracle_first: Add the codex-native smoke cases and the full fixture matrix first; every
  typed-stop case must fail against the CNB-010 runner (which rejects the codex-native backend or
  lacks the validation) before the backend branch is implemented.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - runtime-binding-contract
  - codex-agent-fixtures
- task_review_depth: full
- done_when:
  - Every acceptance condition in the design that names a typed stop has a passing fixture-backed
    smoke case with a distinct stop identifier honoring the approved delegation fallback.
  - Valid trio emission produces the documented `schema_version: 2` shape under all three model
    policies.
  - Herdr golden comparisons from CNB-010 still pass unchanged.
- failure_policy: fix_forward

## Task 3: Describe the two-backend runtime binding in workflow skills

- task_id: CNB-030
- depends_on:
  - CNB-020
- scope_slice: Replace the Herdr-specific overlay framing in `implement-change/SKILL.md` with a
  runtime-backend section covering the neutral envelope core, the codex-native backend (role
  agent file contract, model-policy mapping, typed capability stops, main fallback, and the
  documented semantic-routing behavior that a rejected per-spawn override falls back to `[agents]`
  defaults with its resolution source recorded as binding evidence), and the
  Herdr backend as the explicit second path; update
  `src/skills/workflows/implement-change/references/workflow.toml` runtime-binding metadata
  accordingly; adjust `implement-change-via-herdr/SKILL.md` only where it describes the envelope
  it consumes, keeping its semantics intact.
- impl_file_refs:
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/tools/implement-change-via-herdr/SKILL.md
- test_file_refs:
  - none
- verification_scope:
  - Prose and contract state that every codex-native model policy spawns through the validated
    role agent file, that role files are user-owned and untracked, that command-job stays
    Herdr-or-main, and that `plan-change` topology authority is untouched.
  - No provider model identifier appears in any reusable skill or contract surface.
  - Run `python3 scripts/check-contracts.py` (via `bash scripts/check.sh` in CNB-040 for the
    aggregate; here the focused contract check) and `git diff --check`.
- failing_oracle_first: not applicable for prose-only refs; correctness is enforced by the
  contract checker, the CNB-040 generation parity oracles, and bounded review rather than a new
  phrase-level test.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - workflow-skill-contracts
- task_review_depth: focused
- done_when:
  - `implement-change` documents one neutral envelope core with two backends and unchanged
    lifecycle authority.
  - The via-herdr skill still describes exactly the envelope the runner emits for it.
  - Contract validation passes.
- failure_policy: fix_forward

## Task 4: Converge stable truth and generated surfaces

- task_id: CNB-040
- depends_on:
  - CNB-030
- scope_slice: Update `docs/architecture/workflow-orchestration.md` and `README.md` for the
  two-backend runtime binding boundary, including rewriting the recorded Herdr adapter decision
  horizon into the design's three-way comparison (codex-native backend versus Herdr adapter
  versus main-agent serial execution, judged on the existing three-trial evidence standard);
  regenerate the skill index, root-flat payload, PlantUML sources, tracked SVGs, and the six
  bundled execute-runner copies; run the aggregate and plugin gates from the integrated source.
- impl_file_refs:
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
  - none
- verification_scope:
  - Stable truth documents the neutral core, both backends, role-file ownership, typed stops,
    and the unchanged Herdr wire shape without duplicating runner internals, and records the
    delegation decision horizon as the three-way codex-native/Herdr/main-serial comparison
    instead of the previous Herdr-only horizon.
  - Regenerate all projections from source; generation check mode must pass with no residual
    diff and no hand edit.
  - Run the sovereign-surface, artifact-DAG, and recovery-routing smoke tests, aggregate
    `bash scripts/check.sh`, plugin validation, and `git diff --check`.
- failing_oracle_first: Generation check mode must fail against the pre-convergence generated
  skills, diagrams, and bundled runners before regeneration and pass without a second diff
  afterward.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: fast
- reasoning_profile: light
- isolation: controller-checkout
- resource_locks:
  - generated-skill-surface
  - workflow-diagrams
  - stable-architecture-truth
- task_review_depth: deep
- done_when:
  - Stable truth records the three-way codex-native/Herdr/main-serial delegation decision horizon
    in place of the previous Herdr-only horizon.
  - All root-flat, index, diagram, and bundled-runner projections reproduce exactly from source.
  - Aggregate and plugin gates pass; no path outside the approved touch set changes.
  - The controller records truth-sync readiness without installing, committing, or pushing.
- failure_policy: fix_forward

## Truth Sync Handoff

- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- handoff_scope: After implementation and bounded review pass, synchronize stable workflow truth
  for the backend-neutral envelope core, the codex-native binding backend with user-owned role
  agent files and typed capability stops, the byte-compatible Herdr wire projection, the
  three-way delegation decision horizon, and the unchanged lifecycle and adjudication authority.
  Generated diagrams remain subordinate projections and must be regenerated before truth sync.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_one_bounded_repair
- candidate_findings: The initial bounded review returned five candidates: one blocker (the typed
  rejection matrix omitted the design's distinct "omits a required field" stop), one major (no
  task owned the design-mandated three-way delegation decision horizon), and three minors (three
  design-declared smoke tests missing from top-level test refs, `tomllib` parsing softened to
  equivalent checks, and the semantic-routing per-spawn rejection fallback undocumented in any
  prose scope). Main adjudication accepted all five.
- review_evidence: Repairs added the omitted-required-field fixture and typed stop to CNB-020 and
  the acceptance oracles, assigned the three-way decision-horizon rewrite to CNB-040 scope,
  verification, done-when, and the truth-sync handoff, restored the three smoke tests to the
  declared test refs, required real Python `tomllib` parsing of fixture role files from the smoke
  test, and added the `[agents]`-defaults fallback documentation to CNB-030 scope. A focused
  verification review confirmed repairs one, three, four, and five and returned two narrow
  record-accuracy items on repair two (missing CNB-040 done-when condition and a premature
  verification claim in this record); both were repaired in the same slice and no task topology,
  oracle, touch-set, or authority regression was found.
- review_budget: One initial bounded review and one focused verification review were used. No
  further plan-review batch is authorized without new causal plan scope.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed plan and requested
  `implement-change` on 2026-08-17.
- next_entry: implement-change
