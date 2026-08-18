# Parent-Inherited Codex Subagent Routing Plan

## Status

- plan_version: 2
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: blocked_preflight
- plan_review_status: passed_after_one_bounded_repair
- implementation_review_status: pending
- implementation_verification_status: blocked
- execution_stop_reason: needs-design-decision
- recommended_next_phase: design-change
- next_entry: design-change

## Upstream Design

- design_ref: 2026-08-17-codex-native-binding-design.md
- design_version: sha256:b8d41cc09b9024c61b2a8d16d7961f75adb714c4147306d1abf3990e3384ad4b
- design_approval_status: approved
- architecture_decision_ref: CODEX-NATIVE-BIND-001
- boundary_decision_ref: CODEX-NATIVE-USER-ROUTE-002
- user_route_input_ref: 2026-08-18-codex-subagent-user-route-input.md
- user_route_input_version: sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df
- user_route_input_scope: Approved user-specific provider routing input. The implementation must
  verify this exact artifact version before NSR-040; reusable contracts and this portable plan refer
  to it without projecting its provider identifiers.
- boundary_decision_approval: The user explicitly approved this amendment on 2026-08-18:
  Codex-native subagents inherit the parent model and reasoning when no uplift is needed; user-level
  `~/.codex/AGENTS.md` owns model routing and role reasoning floors; role agent files pin neither
  model nor effort; the harness retains portable task difficulty and role eligibility but does not
  impose a physical explorer effort ceiling.
- superseded_design_scope: This amendment supersedes only the explorer effort pin and absolute
  low-cost ceiling in the approved design, the assumption that `[agents]` defaults are the normal
  fallback, and the requirement that semantic routing always emits both per-spawn values. It does
  not reopen the neutral envelope, backend, topology, isolation, recursion, or adjudication
  decisions in CODEX-NATIVE-BIND-001.

## Implementation Scope

- target_repository: market-csheng plus the explicitly listed user-owned Codex home files
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- provider_scope: Codex-native runtime binding only; Herdr allocation behavior is a compatibility
  oracle and is not changed in this milestone.
- input_file_refs:
  - docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- truth_sync_reserved_refs: The stable docs and diagram paths above are in the immutable total touch
  set so `sync-truth` can operate after its separate human gate; NSR-010 through NSR-040 must not
  mutate them.
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/fixtures/codex-agents
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
- verification_commands:
  - `bash -n src/runtime/harness/execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `python3 -m unittest tests.test_skill_workflow_contracts tests.test_parallel_execution_contracts`
  - `python3 -m unittest tests.test_implement_change_via_herdr_contracts`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-design-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Make parent inheritance the normal Codex-native subagent baseline, move the
  user's concrete role routing and minimum reasoning policy into `~/.codex/AGENTS.md`, remove all
  model and effort pins from native role files, and keep the harness responsible only for portable
  task difficulty, role eligibility, topology, isolation, and effective binding evidence.
- non_goals:
  - Change lifecycle phases, approval gates, plan contract version 2, task DAG ownership,
    concurrency rules, isolation, worktree requirements, recursion limits, reviewer adjudication,
    or controller-owned repair.
  - Change Herdr's explicit Codex/Grok allocation profiles or wire schema; its existing tests remain
    unchanged compatibility evidence.
  - Put personal provider model identifiers or numeric role floors into reusable skills, neutral
    envelope fields, workflow plans for consumers, or generated plugin contracts. The only concrete
    personal routing text changed by this plan is the explicitly authorized user-owned
    `/Users/csheng/.codex/AGENTS.md`.
  - Create exact role pins or upper reasoning ceilings; automatically down-route a child below the
    parent profile for price or latency; make `AGENTS.md` a lifecycle or topology authority.
  - Commit, push, publish, install a plugin, mutate a provider, or run live Codex/Herdr subagent
    trials. A new Codex session is required for post-change runtime acceptance.
- future_phase:
  - Run one new-session reviewer, worker, and explorer trial and compare effective bindings with the
    parent profile and declared user floors.
  - Revisit Herdr allocation policy only if the user explicitly requests the same parent-baseline
    routing for that backend.
  - Introduce a machine-readable user-local floor contract only if real trials show that global
    `AGENTS.md` guidance plus binding evidence is not reliable enough.
- decision_status: ready_for_review
- oracle_strategy: Use contract and state-transition tests for Codex-native resolution precedence,
  legal override shapes, and required-uplift rejection; characterization tests to prove Herdr output
  and topology remain unchanged; configuration-conformance checks for the user-owned TOML and role
  files; deterministic generation/parity checks for source-owned skills and bundled runners; then
  defer stable docs, diagrams, and aggregate parity to the separately approved truth-sync gate.
- acceptance_oracles:
  - A valid reviewer, worker, or explorer role file contains `sandbox_mode` and non-empty
    `developer_instructions` but no `model` or `model_reasoning_effort`; every role pin returns the
    existing generic forbidden-pin typed stop before output mutation.
  - Explorer eligibility remains `fast`/`light`/`shared-read-only` with no write refs and main-owned
    synthesis, but no Codex-native validator, skill, or workflow contract treats that task metadata
    as a physical effort ceiling.
  - Codex-native semantic routing accepts an unchanged parent route with no per-spawn values, an
    effort-only uplift, or a model-plus-effort uplift; it rejects a model-only override so a changed
    model cannot silently fall to that model's default effort.
  - Simulated runtime rejection of either a required effort-only uplift or required
    model-plus-effort uplift returns `controller_binding_required_uplift_unsupported` before output
    mutation. It never retries without the required fields, falls back to `[agents]` defaults, or
    silently binds below the declared floor; the controller may use an already-approved main-agent
    fallback for the unchanged task or must return `manual-decision-required`.
  - Codex-native request and envelope validation accepts all runtime-supported current reasoning
    levels needed above the floor, including `max` and `ultra`, without introducing a role ceiling;
    unsupported model/effort combinations remain runtime capability failures rather than plan
    rewrites.
  - `inherit-main` still emits no per-spawn values. `runtime-default` records `[agents]` defaults
    when present and parent inheritance when both default keys are absent. Every policy preserves
    byte-stable task topology and safety metadata.
  - User config parses as TOML with `agents.default_subagent_model` and
    `agents.default_subagent_reasoning_effort` absent; all three user role files parse with no model
    or effort keys; `config.toml` remains mode `0600`.
  - User `AGENTS.md` defines the parent profile as the baseline, forbids cost-only down-routing,
    defines reviewer and worker reasoning floors at `high` and explorer at `medium`, permits any
    supported higher effort, and requires an explicit effort whenever a spawn changes model.
  - Herdr golden envelopes and `tests/test_implement_change_via_herdr_contracts.py` pass without
    semantic oracle changes; implementation-owned source generation is deterministic. Stable docs,
    diagrams, and aggregate checks are completed only after truth-sync approval.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Approved Architecture Decision

- architecture_decision_ref: CODEX-NATIVE-BIND-001
- boundary_decision_ref: CODEX-NATIVE-USER-ROUTE-002
- decision_fidelity: Keep the approved Codex-native backend and role authority boundaries. Change
  only physical routing ownership: the parent session is the default profile, the user-level host
  instruction supplies concrete model choices and minimum reasoning floors, role files supply
  sandbox and behavioral boundaries without model or effort pins, and portable harness metadata
  expresses task difficulty without a physical upper bound.
- reversible_increments:
  - NSR-010 changes deterministic native binding validation behind fixture-backed failing oracles
    while keeping Herdr output and neutral topology unchanged.
  - NSR-020 updates only source-owned semantic contracts after the runtime behavior is executable.
  - NSR-030 regenerates implementation-owned runtime projections and prepares, but does not apply,
    the stable-truth handoff.
  - NSR-040 applies the matching user-home policy only after repository and generated surfaces pass.
- upgrade_triggers:
  - Return `needs-design-decision` if parent-baseline routing requires changing task topology,
    lifecycle authority, role permissions, recursion, or the neutral envelope schema.
  - Return `needs-design-decision` if removing the portable explorer ceiling necessarily changes
    Herdr's accepted provider profiles in this milestone rather than leaving them backend-specific.
  - Return `needs-plan-change` if a machine-enforced personal floor requires a new tracked schema,
    parser, or user-config generator outside the declared touch set.
  - Return `manual-decision-required` if the current Codex runtime cannot express effort-only or
    model-plus-effort spawn overrides and no already-approved main-agent fallback can preserve the
    unchanged task contract.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1. NSR-010 through NSR-040 execute serially under the main controller;
  central harness sources, generated projections, stable truth, and user-home configuration make
  isolated delegated writes more costly than useful for this milestone.
- semantic_routing_contract: Start from the parent model and reasoning. Emit no override when that
  inherited profile satisfies the user route and task difficulty; emit an effort-only uplift when
  only reasoning must rise; emit model and effort together when the model must change. Never use a
  cost or latency preference to lower the child below the parent or a declared floor. If the runtime
  rejects a required uplift, return `controller_binding_required_uplift_unsupported`; never retry as
  `runtime-default` or with the required override fields removed.
- portable_plan_contract: `execution_profile` and `reasoning_profile` continue to express task
  difficulty only. They do not contain provider identifiers, select a physical effort, or cap a
  stronger inherited profile.
- worker_binding_policy: not applicable to implementation of this plan; every implementation task
  is main-owned.
- reviewer_binding_policy: Plan and implementation review use one bounded reviewer selected under
  the active user route; the reviewer returns candidates only and the main controller adjudicates.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes NSR-010 through NSR-040 as one continuous local implementation unit,
    including the exact repo-owned refs and the three explicitly listed files under
    `/Users/csheng/.codex`. It authorizes commenting out the two `[agents]` defaults, adding the
    user-level role routing policy, and removing the explorer effort pin. It does not authorize a
    commit, push, publication, plugin install, provider mutation, live subagent trial, or close.
- runtime_contingencies:
  - X1: If declared repo refs or the three user-home files contain unexplained overlapping user
    changes after execution begins, preserve them and return `blocked_source_baseline` before
    mutation.
  - X2: If Codex-native request validation cannot distinguish no override, effort-only uplift,
    model-plus-effort uplift, and invalid model-only override without changing the neutral envelope
    or topology, return `needs-design-decision` with the smallest failing fixture.
  - X3: If removing the portable explorer ceiling causes a required Herdr semantic or wire change,
    keep Herdr unchanged and return `needs-design-decision`; do not weaken Herdr regression oracles.
  - X4: If any user-home target becomes symlinked, externally managed, or changes ownership or mode
    before NSR-040, stop that task and report the actual source owner instead of editing the target.
  - X5: If focused or aggregate verification fails outside causal changed paths, diagnose and repair
    only accepted in-scope failures; do not relax role isolation, non-recursion, topology, or
    forbidden-pin assertions.
  - X6: If the active native runtime or spawn call rejects an effort-only or model-plus-effort uplift
    required by the user route, preserve the original task and return
    `controller_binding_required_uplift_unsupported`. Use main-agent execution only when its existing
    delegation fallback is already approved; otherwise return `manual-decision-required`. Do not
    retry through `[agents]` defaults or any lower child profile.
- planned_stop_points:
  - none inside NSR-010 through NSR-040; successful implementation and review route to the separate
    truth-sync approval gate. Runtime acceptance waits for a new Codex session.
- task_ordering_rationale: Establish failing native binding oracles before changing behavior; align
  portable skill contracts only after the runner accepts the new states; converge generated and
  runtime repository surfaces once; then update user-home files last so the currently loaded old
  explorer-pin contract is not invalidated before the new source and generated runtime are ready.
  Stable docs and diagrams remain untouched until implementation review passes and the user approves
  the separate truth-sync gate.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Record the initial Git status and hashes plus ownership and mode of each
  user-home target. Modify only declared refs and never discard unrelated user changes.
- oracle_boundary: Add new native binding cases before implementation. Do not weaken topology,
  sandbox, recursion, required-field, forbidden-pin, or Herdr compatibility assertions to obtain a
  pass.
- user_config_boundary: Preserve `config.toml` mode `0600`; inspect and report only the relevant
  keys and hashes, never unrelated configuration or credential values. Parse after every edit and
  fix forward inside the three authorized user-home files.
- generated_boundary: Edit `src/skills/` and `src/runtime/harness/` owners, then regenerate root-flat
  skills, bundled runners, and indexes during implementation. Regenerate diagrams only during the
  separately approved truth-sync phase. Never hand-edit generated projections.
- external_boundary: A new Codex thread, live subagent trial, commit, push, install, publication,
  provider action, truth sync, and close are distinct later gates, not recovery actions.
- guarded_rollback: none

## Task 1: Change Codex-native binding oracles and role-file validation

- task_id: NSR-010
- depends_on:
  - none
- scope_slice: Add failing Codex-native contract cases for pin-free role files, parent-baseline
  semantic routing, effort-only and model-plus-effort uplift, model-only rejection, accurate
  runtime-default fallback evidence, supported higher efforts, and rejected required-uplift
  capability responses; then update the deterministic runner and fixture matrix without changing
  neutral task topology or Herdr validation.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - tests/fixtures/codex-agents
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
- verification_scope:
  - Make the valid explorer fixture omit both model and effort and reject any model or effort pin
    for reviewer, worker, or explorer through the generic forbidden-pin typed stop.
  - Replace the explorer-ceiling and missing-explorer-pin cases with accepted no-pin, accepted
    high/max/ultra per-spawn effort, effort-only uplift, model-plus-effort uplift, and rejected
    model-only cases; prove typed stops occur before output mutation.
  - Cover runtime-default with fixture homes both with and without `[agents]` default keys and assert
    accurate `agents-defaults` versus `parent-inherit` resolution evidence.
  - Assert semantic routing with no uplift preserves parent inheritance and all accepted binding
    shapes preserve the same task projection, isolation, locks, and role file.
  - Simulate native rejection separately for effort-only and model-plus-effort uplift. Assert the
    typed `controller_binding_required_uplift_unsupported` result occurs before output mutation and
    that no retry changes the resolution source to `agents-defaults`, removes required fields, or
    binds a lower profile. Assert the existing delegation policy alone decides whether the unchanged
    task can return to the main controller or needs a manual decision.
  - Run Bash syntax, the focused execute-runner smoke test, topology contract tests, unchanged Herdr
    contract tests, and `git diff --check`.
- failing_oracle_first: Add the no-pin explorer success, semantic no-override success, effort-only
  success, max/ultra acceptance, model-only rejection, no-default runtime fallback, and both
  required-uplift rejection assertions before changing `execute-runner.sh`; each must fail against
  the current ceiling/pin/fallback contract.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - codex-native-binding-contract
  - codex-agent-fixtures
- task_review_depth: full
- done_when:
  - Every role fixture is pin-free when valid and every role pin has a distinct pre-emission
    forbidden-pin assertion.
  - Parent inheritance, effort-only uplift, model-plus-effort uplift, and model-only rejection are
    executable states with accurate resolution evidence.
  - Both required-uplift rejection shapes produce the typed stop without fallback, downgrade, retry,
    or output mutation.
  - Explorer can retain its factual role under any supported higher effort without changing its
    authority, isolation, or task metadata.
  - Herdr compatibility and topology invariance tests remain green without semantic oracle edits.
- failure_policy: fix_forward

## Task 2: Decouple portable task difficulty from physical subagent effort

- task_id: NSR-020
- depends_on:
  - NSR-010
- scope_slice: Update source-owned planning and implementation contracts so explorer eligibility
  remains a bounded factual, no-write, main-synthesis role while physical model and effort are
  selected from the parent baseline plus user runtime policy and task difficulty. Remove all
  portable low-cost ceilings and exact physical effort mappings for the Codex-native path.
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
- test_file_refs:
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
- verification_scope:
  - Preserve `fast`/`light`/`shared-read-only`/no-write explorer eligibility and main-owned
    synthesis while removing `role_cost`, default/max effort, rejected-effort, and file-pinned
    explorer ceiling claims from the reusable contract.
  - Record that parent profile is the physical baseline, role files may pin neither model nor
    effort, higher physical profiles do not widen explorer authority, and the host/user runtime
    policy owns concrete floor and uplift selection.
  - Define semantic routing as no override, effort-only uplift, or model-plus-effort uplift as
    needed; preserve `inherit-main` and `runtime-default` as portable policies with unchanged
    topology effects.
  - State that a rejected required semantic uplift is a typed capability stop and cannot be retried
    as `runtime-default`, with omitted fields, or below the user floor; only the task's pre-approved
    main fallback may preserve forward progress.
  - Run focused plan-runner and workflow contract tests plus `git diff --check`.
- failing_oracle_first: Change focused contract assertions first so the current absolute explorer
  cost fields, required effort pin, and always-explicit semantic routing fail before source prose
  and `workflow.toml` are updated.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - workflow-skill-contracts
  - runtime-binding-contract
- task_review_depth: deep
- done_when:
  - Portable task profiles still describe difficulty and authority but no longer cap physical
    effort or duplicate a personal model route.
  - Codex-native role-file and semantic-routing prose matches the executable NSR-010 contract.
  - Focused plan and workflow contract tests pass without provider identifiers in reusable source.
- failure_policy: fix_forward

## Task 3: Converge generated runtime surfaces and prepare truth-sync evidence

- task_id: NSR-030
- depends_on:
  - NSR-020
- scope_slice: Regenerate the implementation-owned skill index, root-flat skills, and bundled runners
  from source; run focused sovereign harness gates; collect the stale-truth and diagram deltas needed
  for the later truth-sync handoff without mutating stable docs, PlantUML views, or tracked SVGs.
- impl_file_refs:
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
- verification_scope:
  - Run the skill-index and root-flat generators, execute the six sovereign harness smoke tests, and
    confirm a second run produces no implementation-owned generated diff.
  - Record bounded stale-truth searches and expected diagram changes as truth-sync handoff evidence;
    do not edit `README.md`, stable architecture docs, diagram sources, or tracked SVGs in this task.
  - Confirm Herdr-specific constraints remain explicitly scoped and unchanged in generated runtime
    surfaces.
- failing_oracle_first: Skill generation check mode must fail against the pre-convergence generated
  skills and bundled runners, then pass after one source-owned regeneration. Stale docs/diagram
  evidence remains an expected truth-sync input, not an implementation failure to repair early.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-skill-surface
  - truth-sync-handoff-evidence
- task_review_depth: deep
- done_when:
  - Every implementation-owned generated skill and runner reproduces exactly from source and focused
    sovereign harness checks pass.
  - Stable docs and diagrams remain unmodified, with their required changes captured for truth sync.
  - Implementation evidence is ready for NSR-040, bounded implementation review, and the later
    truth-sync approval gate.
- failure_policy: fix_forward

## Task 4: Apply the user-level parent-baseline routing policy

- task_id: NSR-040
- depends_on:
  - NSR-030
- scope_slice: Update only the authorized user Codex home files: leave both `[agents]` default
  model/effort keys commented out so absent values inherit the parent, add the approved role model
  route and minimum reasoning floors to global `AGENTS.md`, and remove the explorer's effort pin
  and low-cost label while preserving all role sandboxes and behavioral restrictions.
- impl_file_refs:
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- input_file_refs:
  - docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md
- test_file_refs:
  - none
- verification_scope:
  - Before mutation, verify that the resolved input path matches
    `sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df`;
    otherwise return `blocked_source_baseline`. Copy its exact provider-specific role families into
    `AGENTS.md` without duplicating them in this portable plan. Preserve its reviewer and worker
    `high` minimums, explorer `medium` minimum, supported higher efforts, parent baseline, and
    permission for the main agent to choose among approved role families. State that these are
    floors, not pins or ceilings, and that cost/latency does not authorize down-routing below the
    parent.
  - Require an explicit effort whenever a spawn changes model; allow effort-only uplift when the
    model remains inherited; keep routing separate from lifecycle, task topology, and role
    authority. A rejected required uplift must stop with the typed capability result rather than
    falling back to `[agents]` defaults or retrying below the floor.
  - Parse `config.toml` and all three role files with Python `tomllib` without printing unrelated
    values. Assert both subagent default keys are absent and every role file lacks model and effort
    keys; verify reviewer/explorer remain read-only and worker remains workspace-write.
  - Preserve file ownership and modes, especially `config.toml` mode `0600`; record hashes of the
    five checked user files and state that a new Codex session is required for runtime acceptance.
- failing_oracle_first: Before editing, run the metadata-only conformance check and capture failures
  for configured `[agents]` defaults, the explorer effort pin, the low-cost explorer label, and the
  missing global route section; rerun the same check after the edits.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - user-codex-home-routing
- task_review_depth: focused
- done_when:
  - The immutable user-route input hash matches the approved version before any user-home mutation.
  - The two global subagent defaults are absent, so unoverridden child fields resolve to parent
    values.
  - The global route states the approved model choices and minimum-only reasoning floors, including
    the model-change-plus-effort rule and no cost-only down-routing.
  - Reviewer, worker, and explorer role files contain no model or effort pins and retain their
    sandbox and authority boundaries.
  - Metadata-only conformance passes with preserved ownership/modes and no secret-bearing output.
- failure_policy: fix_forward

## Truth Sync Handoff

- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- truth_sync_impl_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
- truth_sync_verification_commands:
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash scripts/check.sh`
  - `git diff --check`
- handoff_scope: After implementation and bounded review pass, synchronize stable truth for the
  parent-inherited Codex-native baseline, pin-free role files, user-owned concrete routing and
  reasoning floors, semantic task profiles without physical ceilings, accepted native override
  shapes, typed no-downgrade behavior when required uplift is unsupported, accurate resolution
  evidence, and unchanged topology, role authority, and Herdr boundary. Regenerate PlantUML and
  tracked SVG projections from the synchronized truth, then run the aggregate gate. User-home files
  are runtime configuration evidence, not repository stable truth.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_one_bounded_repair
- candidate_findings: The initial bounded review returned three high-confidence candidates. The main
  adjudication accepted all three: provider identifiers were duplicated into the portable plan;
  required-uplift rejection had no executable no-fallback oracle; and NSR-030 prematurely mixed
  stable-truth mutation into implementation before the separate truth-sync human gate. Focused
  verification returned one narrow record finding: the provider-neutral route decision ID was not a
  resolvable immutable execution input. Main adjudication accepted it.
- review_evidence: The initial repair referenced the approved user-owned route without embedding
  provider identifiers, added separate effort-only and model-plus-effort rejection oracles with a typed
  no-downgrade stop, and limits NSR-030 to implementation-owned generation plus truth-sync evidence.
  Stable docs, diagrams, aggregate generation, and `scripts/check.sh` are reserved for the explicit
  Truth Sync Handoff. Focused verification confirmed the no-fallback and truth-sync repairs, but found
  the provider-neutral route reference non-resolvable. The same-slice record repair added the
  immutable, user-approved input artifact and SHA-256 precondition for NSR-040; local inspection
  confirms no provider identifier entered this plan and no DAG, authority, oracle, or touch-set
  regression remains.
- review_budget: One initial bounded review and one focused verification review were used. The one
  causal same-slice record repair was applied; no further plan-review batch is authorized without new
  causal plan scope.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed plan and invoked
  `$coding:implement-change` on 2026-08-18.
- next_entry: implement-change

## Implementation Preflight

- attempted_on: 2026-08-18
- result: needs-design-decision
- typed_stop: controller_allowed_touch_set_external_ref_unsupported
- evidence: `execute-runner.sh allowed-touch-set` rejects the three absolute user-home refs before
  materializing the immutable execution touch set. The same comparison also proves that the approved
  upstream design surface does not contain the new plan-change source/projection refs or their four
  focused test refs.
- mutation_state: No repository source, generated runtime surface, or user-home configuration was
  changed. Only this stage artifact was updated to record the user's approval and failed preflight.
- required_decision: Either design an explicit external-side-effect contract for exact user-home refs,
  including immutable binding and changed-path evidence, or keep the artifact-DAG repository-only and
  split NSR-040 into a separately authorized host-configuration execution unit. The latter is the
  smallest durable option for this one user-owned routing policy.
