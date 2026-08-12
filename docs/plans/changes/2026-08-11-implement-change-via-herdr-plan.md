# Implement Change via Herdr Runtime Adapter Plan

## Upstream Design

- design_ref: 2026-08-11-implement-change-via-herdr-design.md
- design_version: 2
- design_gate_status: approved
- design_gate_basis: The user explicitly approved the reviewed design and requested
  `$coding:plan-change` on 2026-08-11, then approved the exact two-path generated-surface amendment
  on 2026-08-12.

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - .gitignore
  - contracts/skills.toml
  - src/skills/session/use-coding-skills/references/routing.toml
  - src/skills/tools/implement-change-via-herdr
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/runtime/harness/execute-runner.sh
  - README.md
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills/implement-change-via-herdr
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
  - skills/use-coding-skills/references/routing.toml
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
  - skills.index.json
- test_file_refs:
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/herdr
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
- verification_scope:
  - `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng-herdr" python3 -m unittest tests.test_implement_change_via_herdr_contracts`
  - `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng-herdr" PYTEST_ADDOPTS="-o cache_dir=$HOME/.cache/pytest/market-csheng-herdr" uvx --with pytest pytest -q tests/test_implement_change_via_herdr_contracts.py`
  - `RUFF_CACHE_DIR="$HOME/.cache/ruff/market-csheng-herdr" uv tool run ruff check src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py tests/test_implement_change_via_herdr_contracts.py tests/fixtures/herdr/fake-herdr.py`
  - `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng-herdr" uv tool run ty check src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-design-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-design-plan-skill-control.sh`
  - `bash src/runtime/harness/smoke-test/test-agent-native-review.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-review-execute-skill-control.sh`
  - `bash scripts/check.sh`
  - `uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Add an explicit, lower-plane `implement-change-via-herdr` runtime adapter
  that lets the existing `implement-change` controller bind approved tasks to supported coding-agent
  CLIs inside run-owned Herdr resources, without changing lifecycle ownership, plan topology, or
  unrelated live Herdr state.
- non_goals:
  - Use the adapter being built to implement this plan, connect automated tests to live Herdr, or
    inspect, focus, rename, interrupt, reuse, or close any currently running Herdr resource.
  - Add a second lifecycle controller, change `phase_routes.execute`, move review adjudication or
    repair ownership out of `implement-change`, or add a new plan-level role field.
  - Persist concrete provider, model, reasoning-effort, permission, or credential choices in the
    portable plan contract or repository-wide defaults.
  - Add a generic terminal backend registry, tmux backend, dynamic provider plugin system, or
    unattended execution mode.
  - Install or update the plugin, start a new coding-agent session, commit, push, deploy, or perform
    any external action as part of implementation approval.
- future_phase:
  - After verified implementation, use `sync-truth` to update the declared stable truth refs and
    stop at its separate human approval gate.
  - After truth sync and an explicit installation/update authorization, install the refreshed local
    plugin and start the provider-appropriate fresh session needed to load it.
  - Forward-test from a newly selected disposable repository and Herdr context, then run two more
    repository-local approved plans across at least two supported agent kinds; do not reuse the
    currently active Herdr work as acceptance evidence.
  - Review the three forward-test records before promoting Herdr into `implement-change`, adding a
    role field, or extracting a second backend interface.
- decision_status: ready_for_review
- oracle_strategy: Use a model-based state-machine oracle for adapter transitions and leases, a
  fake-executable contract oracle for exact Herdr argv and responses, harness smoke tests for the
  controller-envelope and lifecycle boundary, and generated-surface parity plus aggregate checks
  for repository integration. Live Herdr is explicitly outside automated acceptance.
- acceptance_oracles:
  - Missing `HERDR_ENV=1`, missing CLI, caller-context mismatch, repository mismatch, unapproved
    plan, stale envelope, or unsupported capability profile returns a typed zero-mutation stop.
  - The runner-issued envelope binds the approved plan and ledger digests, immutable task
    projection, controller identity, physical binding, run nonce, touch set, and oracle refs; the
    adapter cannot select tasks, mutate the ledger, converge, review, repair, or derive a tail route.
  - The adapter reuses the initiating workspace, creates only one run-owned background tab and
    owned child panes with no focus change, persists every opaque ID before use, and never treats a
    display name as resource authority.
  - Explorer and reviewer bindings are read-only; writer bindings require an isolated worktree;
    task-tool network, undeclared credentials, remote actions, commit, push, deploy, and destructive
    actions remain denied independently from the coding agent's inference/auth control plane.
  - Agent startup uses argument vectors, bounded waits distinguish busy, idle, done, blocked,
    unknown, stalled, and timeout states, and completion claims remain untrusted until controller
    touch-set and oracle verification passes.
  - Atomic state and repository-scoped lease transitions cover active, cleanup-pending, released,
    restart, conflict, and evidence-based stale diagnosis without storing secrets, full prompts, or
    unbounded terminal output.
  - Cleanup re-enumerates owned resources, never closes a mixed-ownership tab, and releases the
    execution lease only after the run-owned live process and pane set reaches zero.
  - Both supported initial agent kinds and the relative fast/light explorer mapping are covered by
    fake bindings while concrete model choices remain runtime evidence rather than plan truth.
  - Source, contract, routing, generated root-flat payload, bundled harness copies, diagrams, skill
    index, and stable truth agree on one lower-plane adapter and one `implement-change` controller.
  - Every declared focused and aggregate check passes, no automated command reaches live Herdr, and
    no path outside the immutable touch set changes.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Approved Architecture Decision

- architecture_decision_ref: HERDR-IMPL-001-explicit-runtime-adapter
- decision_fidelity: Implement the approved smallest-sufficient option without rerunning selection:
  one explicit Herdr-only lower-plane adapter, one existing `implement-change` controller, no new
  plan role field, and no generic backend registry.
- reversible_increments:
  - HVR-010 adds only the controller provenance envelope and can be removed without changing the
    existing plan, ledger, execution, review, or close contract.
  - HVR-020 builds the adapter behind an unregistered explicit skill and fake-only tests, so no live
    runtime or ordinary execution path depends on it.
  - HVR-030 exposes only an explicit routing overlay; removing that contract entry leaves
    `phase_routes.execute = implement-change` and ordinary plan execution unchanged.
  - HVR-040 regenerates deterministic projections from source and can be reversed by removing the
    source overlay and regenerating again; generated files are never an independent authority.
  - HVR-050 adds no mutation and requires offline evidence before truth sync, installation, or any
    live forward trial.
- upgrade_triggers:
  - Consider promotion into `implement-change` only after three successful repository-local trials
    cover at least two supported agent kinds and the evidence shows lower coordination cost without
    recurring ownership or recovery ambiguity.
  - Add a plan-level role field only if repeated trial evidence shows explorer versus worker cannot
    be derived from isolation, write refs, execution profile, and reasoning profile.
  - Extract a generic backend interface only after a second concrete backend is requested and proves
    it can satisfy the agent-readiness, lifecycle-observation, ownership, and cleanup contract.
- decision_horizon: Preserve the explicit removable adapter through the three-trial evidence review;
  any earlier trigger that invalidates the approved demand, owner, hard requirement, or safe exit
  returns `needs-design-decision`.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval of this plan authorizes HVR-010 through HVR-050 as one serial implementation unit,
    including two bounded delegated writer tasks in isolated worktrees, controller-owned
    convergence, repository-local fake processes, generated-surface refresh, and in-scope
    fix-forward repair. It does not authorize live Herdr access, plugin installation/update, stable
    truth approval, commit, push, deploy, remote/provider action, or close.
- runtime_contingencies:
  - X1: Before mutation, capture the exact tracked and untracked baseline. Stop if any unrelated
    dirty path changes, or if a generator proposes a path outside the approved design and plan
    surfaces.
  - X2: Return `needs-design-decision` if a credible implementation requires a second lifecycle
    owner, plan-schema role field, generic backend framework, live-Herdr automated test, or a weaker
    ownership/capability boundary than the approved design.
  - X3: Stop before Herdr mutation if a developer or test accidentally resolves the real `herdr`
    executable; only the fixture executable and synthetic environment IDs are allowed in this plan.
  - X4: If the chosen coding-agent CLI cannot later enforce the declared control-plane/tool-plane
    capability profile, preserve the typed `delegated_capability_unavailable` result and main-agent
    fallback policy instead of weakening the profile or claiming live support.
  - X5: If skill scaffolding, generated projection, or plugin validation reveals a provider-specific
    metadata requirement outside the approved skill directory and generated surfaces, stop for a
    bounded plan or design decision rather than expanding silently.
  - X6: Stop and diagnose when focused or aggregate checks fail outside causal changed paths; repair
    only accepted in-scope failures and preserve evidence for an unresolved typed exit.
- planned_stop_points:
  - none inside HVR-010 through HVR-050; successful implementation enters bounded
    `review-change`, then hands verified evidence to the separately approval-gated `sync-truth`
    phase.
- task_ordering_rationale: Establish the controller-issued envelope before its consumer, implement
  and model-test the adapter before exposing it, add routing and workflow contracts only after the
  source skill exists, regenerate shared surfaces once under the controller, then run complete
  verification. There is no conflict-free dependency-frozen write batch worth approving in this
  bootstrap milestone.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- topology_invariance: Runtime actor, coding-agent CLI, model, reasoning effort, permission, and
  sandbox choices may instantiate the approved profiles but cannot change task IDs, dependencies,
  serial shape, delegation policy, isolation, locks, touch sets, oracles, or failure policy.
- semantic_profiles:
  - deep: Use a runtime-available high-capability equivalent for controller provenance, state-machine
    safety, leases, ownership, cleanup, and final adjudication.
  - balanced: Use a runtime-available general implementation equivalent for bounded source-contract
    and integration work with executable oracles.
  - fast: Use a runtime-available efficient equivalent only for deterministic generation or other
    mechanical work with strong parity checks.
- reasoning_profiles:
  - deep: Reserve extended reasoning for lifecycle boundaries, security/capability separation,
    recovery transitions, and review judgment.
  - standard: Use normal implementation reasoning for explicit, bounded contract edits.
  - light: Use concise reasoning for controller-owned generation whose outputs are deterministically
    checked.
- effective_concurrency: One task at a time. No named parallel batch is approved; delegated writer
  tasks remain serial and each starts from the controller-integrated result of its dependency.
- bootstrap_boundary: This plan cannot self-host through the adapter it creates. `implement-change`
  binds HVR-020 and HVR-030 through the currently available agent-native runtime, records their
  concrete actor/model choices at execution time, and does not access live Herdr.
- explorer_boundary: This DAG contains no pure search-and-confirmation slice, so it does not invent
  an explorer task. Future eligible explorer slices remain `fast` / `light` /
  `shared-read-only`; a search task needing synthesis is a worker or main task instead.

## Implementation Language

- selected_boundary: Keep `src/runtime/harness/execute-runner.sh` in Bash for its existing validated
  plan/ledger projection and JSON assembly boundary; implement the Herdr protocol, atomic run state,
  lease transitions, resource inventory, and safe subprocess argv handling in a Python 3
  standard-library script inside the new skill.
- ownership_seam: Bash validates the approved plan and ledger and materializes the immutable
  controller-issued binding envelope. Python validates and consumes that envelope and owns only
  adapter-local state and run-owned Herdr resources. Neither layer reimplements the other's
  business rules.
- language_rationale: The adapter is a persisted structured state machine with JSON, filesystem
  identity, atomic updates, bounded subprocess control, and recovery tests; Shell would make those
  invariants harder to test safely. Python is already the repository convention for stdlib-only
  deterministic tooling and ships without adding a runtime dependency.
- repository_tooling_fit: Follow the repository's existing `python3` plus `unittest` aggregate gate
  while also running focused pytest, Ruff, and ty through isolated `uv` tools with external caches.
  Do not add a repository-wide or public-skill `pyproject.toml` solely to migrate unrelated Python
  tooling inside this approved surface.
- skill_scaffold: Use the installed skill-creator `init_skill.py` for the initial source directory
  with `scripts` and `references`, then conform the generated files to this repository's
  `src/skills` contract and validate the completed source skill with the skill-creator validator.

## Task 1: Materialize the controller binding envelope

- task_id: HVR-010
- depends_on:
  - none
- scope_slice: Extend the existing execution runner with one deterministic, controller-owned
  operation that validates the approved plan and immutable ledger projection, selects only the
  controller-specified ready task, and atomically materializes a schema-versioned binding envelope
  for the adapter without granting adapter-side task selection or lifecycle authority.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
- verification_scope:
  - Add red fixtures for unapproved plans, plan-ledger drift, unknown or non-ready tasks, malformed
    physical bindings, stale digest inputs, unsafe output paths or permissions, and direct envelope
    forgery missing the controller nonce.
  - Assert the success envelope includes schema version, controller identity, canonical repository,
    plan and ledger digests, immutable task projection, touch set, oracle refs, physical binding,
    attempt, and nonce while excluding credentials and prompt content.
  - Prove that envelope generation cannot mutate the task ledger, choose a different task, run an
    agent, converge, review, repair, or derive a lifecycle tail.
  - Run `bash -n`, ShellCheck when available, and
    `bash src/runtime/harness/smoke-test/test-execute-runner.sh`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - controller-envelope
- task_review_depth: full
- done_when:
  - Exactly one runner operation emits an owner-only, atomically replaced, schema-versioned envelope
    from a validated approved task projection.
  - Every stale, ambiguous, unapproved, drifted, or authority-expanding input fails before adapter or
    repository mutation with actionable typed evidence.
  - The envelope is sufficient for adapter preflight but carries no lifecycle, review, convergence,
    repair, or tail-routing capability.
  - Focused Shell syntax, static analysis when available, and smoke tests pass.
- failure_policy: fix_forward

## Task 2: Build and model-test the Herdr adapter skill

- task_id: HVR-020
- depends_on:
  - HVR-010
- scope_slice: Scaffold the explicit tool skill, implement the Python adapter state machine and
  run-owned state/lease/resource protocol, add the precise ignored run-state root, and verify all
  behavior through a fake Herdr executable without contacting the live service.
- implementation_archetype: cli-tool
- implementation_language: Python 3 standard library
- language_rationale: A persisted JSON and filesystem state machine with atomic updates, subprocess
  argv safety, resource identity, bounded waits, and recovery transitions needs direct structured
  data and unit-test support while remaining dependency-free in every generated skill install.
- impl_file_refs:
  - .gitignore
  - src/skills/tools/implement-change-via-herdr/SKILL.md
  - src/skills/tools/implement-change-via-herdr/agents/openai.yaml
  - src/skills/tools/implement-change-via-herdr/references/runtime-contract.md
  - src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py
- test_file_refs:
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/herdr
- verification_scope:
  - Use the skill-creator scaffold and validator, then keep `SKILL.md` as the thin explicit workflow
    entry, `runtime-contract.md` as the detailed adapter boundary, and the Python script as the only
    deterministic Herdr state owner.
  - Drive the adapter with a fake executable that records exact argv and returns fixture JSON/state;
    fail the test if PATH resolves a non-fixture `herdr` binary or if any real Herdr socket/context is
    accessed.
  - Model preflight, allocate, start, prompt, wait, collect, controller-verification handoff, resume,
    and cleanup across happy, busy, blocked, unknown, stalled, timeout, malformed, and restart paths.
  - Cover caller-context pinning, no-focus allocation, role/name derivation and 32-character bounds,
    opaque-ID authority, safe argv startup, prompt single-submit, bounded evidence, and secret/prompt
    exclusion.
  - Cover read-only versus writer capability profiles, isolated-worktree enforcement, inference/auth
    control-plane allowance, task-tool network/credential/remote/commit/push/deploy denial, and
    always-approve confinement.
  - Cover repository-scoped lease conflict and stale diagnosis, active/cleanup-pending/released
    transitions, atomic state replacement, restart mismatches, mixed-tab cleanup, retained failure,
    clean-success release, and cleanup residue.
  - Run the focused unittest and pytest lanes, Ruff, ty, and the skill-creator validator with caches
    outside the repository.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - herdr-adapter-state-machine
- task_review_depth: full
- done_when:
  - The new skill is explicit, lower-plane, thin, and cannot run without a runner-issued envelope,
    approved caller context, `HERDR_ENV=1`, and an enforceable delegated capability profile.
  - Every Herdr mutation targets a freshly allocated manifest-owned opaque ID, records ownership
    before subsequent use, and cannot touch the initiating main pane or an unrelated resource.
  - State, lease, wait, resume, evidence, and cleanup transitions are deterministic, typed, bounded,
    restart-safe, and free of secrets, full prompts, and unbounded terminal output.
  - Fake-agent fixtures cover both initial supported agent kinds and semantic explorer downgrade
    behavior without persisting concrete model choices in portable plan truth.
  - Focused Python, skill, and fake-Herdr checks pass without resolving or controlling live Herdr.
- failure_policy: fix_forward

## Task 3: Expose the adapter without changing lifecycle ownership

- task_id: HVR-030
- depends_on:
  - HVR-020
- scope_slice: Register the explicit tool skill and its singular routing case, teach planning to
  recommend cheap pure explorers and implementation to own concrete physical binding, and protect
  the one-controller boundary through contract and sovereign-surface tests.
- impl_file_refs:
  - contracts/skills.toml
  - src/skills/session/use-coding-skills/references/routing.toml
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
- test_file_refs:
  - tests/test_implement_change_via_herdr_contracts.py
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
- verification_scope:
  - Add the exact manifest and installed semantic-requires edges from the approved design, with
    `lifecycle_owner = false`, explicit activation, overlay role, approved-plan requirement, and no
    shared runtime bundle.
  - Add one positive and negative semantic routing case for explicit via-Herdr execution; prove
    ordinary approved-plan execution still routes to `implement-change` and execute/verify phase
    routes remain unchanged.
  - Teach `plan-change` that only pure search and factual confirmation qualifies for
    `fast` / `light` / `shared-read-only`; deep synthesis never receives the cheap explorer default.
  - Teach `implement-change` to derive orchestrator/reviewer/explorer/worker roles, bind concrete CLI,
    model, effort, permission, sandbox, worktree, and Herdr evidence at runtime, and retain controller
    ownership of convergence, adjudication, repair, continuation, truth sync, and close.
  - Assert provider-neutral plan fields, topology invariance, `inherit-main` and `runtime-default`
    exceptions, no recursive delegation, no external authority, and no lifecycle-owner promotion.
  - Run the focused Python contract test and all four declared sovereign/control smoke tests.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: balanced
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - workflow-routing-contract
- task_review_depth: boundary
- done_when:
  - Direct explicit requests select the tool overlay plus `implement-change`, while ordinary execute
    requests and phase routes retain `implement-change` as their unique lifecycle owner.
  - Planning owns semantic difficulty and explorer eligibility; implementation owns only concrete
    runtime binding and cannot rewrite the approved DAG.
  - Reviewers remain candidate-only, explorers remain bounded read-only searchers, writers remain
    task-scoped isolated actors, and the main controller alone converges, adjudicates, repairs, and
    routes continuation.
  - Focused manifest, routing, workflow, review, and sovereign-surface checks pass.
- failure_policy: fix_forward

## Task 4: Converge generated and installed surfaces

- task_id: HVR-040
- depends_on:
  - HVR-030
- scope_slice: Have the main controller verify and integrate the two serial worker diffs, regenerate
  the skill index, root-flat public skill payload, bundled harness copies, PlantUML sources, and
  tracked SVGs exactly once, then prove deterministic source/generated parity.
- impl_file_refs:
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills/implement-change-via-herdr
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
  - skills/use-coding-skills/references/routing.toml
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
  - skills.index.json
- test_file_refs:
  - none
- verification_scope:
  - Compare HVR-020 and HVR-030 actual changed paths to their immutable refs before integration and
    reject any generated, stable-truth, peer-owned, global-config, or unrelated worker write.
  - Run `python3 scripts/generate-skills-index.py`,
    `python3 scripts/flatten-skills.py --target root-flat`, and
    `python3 scripts/generate-workflow-diagrams.py` only after both dependencies are integrated.
  - Prove source/root-flat parity for the new skill, both changed workflow skills, every generated
    harness copy, activation metadata, routing metadata, skill index, PlantUML, and SVG output.
  - Run the plugin validator because the new public skill includes generated Codex metadata.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: fast
- reasoning_profile: light
- isolation: controller-checkout
- resource_locks:
  - generated-surfaces
- task_review_depth: boundary
- done_when:
  - Both delegated diffs are within scope, independently verified, and integrated in dependency
    order by the main controller.
  - Every generated root-flat and diagram artifact matches its source and generator with no manual
    edit to generated files.
  - The new public skill has correct provider projection and no runtime bundle, while every existing
    lifecycle owner receives the refreshed execute runner bundle.
  - Generation and plugin validation pass without changing any path outside the approved set.
- failure_policy: fix_forward

## Task 5: Run complete offline acceptance

- task_id: HVR-050
- depends_on:
  - HVR-040
- scope_slice: Execute the complete fake-Herdr, harness, generated-surface, language, plugin, and
  aggregate repository oracles; audit the final touch set and evidence; and prepare the exact bounded
  implementation brief for `review-change` without accessing live Herdr.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Run every command in the global `verification_scope`, including focused unittest/pytest, Ruff,
    ty, required sovereign harness smoke tests, aggregate check, plugin validation, and diff check.
  - Confirm the fake executable was the only Herdr binary invoked and no live workspace, tab, pane,
    agent, socket, task, or terminal history was inspected or mutated.
  - Compare final changed paths and content hashes with the baseline, approved design surface, global
    plan touch set, and each task slice; prove every unrelated dirty path is unchanged.
  - Build the bounded review brief from the approved design and plan, exact implementation diff,
    declared oracles, task touch sets, and only justified direct dependencies.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - final-offline-acceptance
- task_review_depth: full
- done_when:
  - All focused and aggregate oracles pass from the controller checkout with caches outside the
    repository and no live Herdr access.
  - The final diff is confined to the approved design and plan surfaces, generated artifacts are
    current, and unrelated pre-existing state is byte-for-byte and status-for-status unchanged.
  - The review brief is bounded to this implementation and contains enough evidence for independent
    causality-bound review without repository-wide discovery.
  - Implementation is ready for mandatory `review-change`; it is not yet truth-synced, installed,
    committed, pushed, closed, or live-forward-tested.
- failure_policy: fix_forward

## Recovery

- default_failure_policy: fix_forward
- controller_policy:
  - Preserve failed or ambiguous adapter evidence and isolated worktrees; never integrate an
    unverified claim or a touch-set violation.
  - A failed delegated attempt may receive a fresh bounded attempt only after controller diagnosis;
    it cannot widen scope, change topology, or take review/repair authority.
  - Return `needs-plan-change` for invalid dependencies, touch sets, or test surfaces and
    `needs-design-decision` for a lifecycle, authority, capability, or backend-boundary change.
  - Do not silently fall back from an explicit future via-Herdr run to another terminal backend.
    During this bootstrap implementation, use only the current agent-native runtime declared by the
    plan's bootstrap boundary.
  - If an unexpected live Herdr interaction occurs, stop immediately, preserve evidence, and do not
    attempt cleanup against resources whose run ownership was never established.

## Truth Sync Handoff

- stable_truth_refs:
  - README.md
  - docs/architecture/workflow-orchestration.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- handoff_scope: After implementation and mandatory implementation review pass, update only the
  declared stable truth to describe the explicit lower-plane adapter, provider-neutral planning
  profiles, implementation-time physical binding, one-controller authority, fake-versus-live test
  boundary, and user-run trial horizon. Generated diagrams are refreshed during HVR-040 and must be
  verified, not hand-edited, during truth sync.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed
- candidate_findings: Two high-confidence plan-contract findings were accepted and repaired; none
  remain unresolved.
- review_evidence: The initial bounded review required explicit preservation of the approved
  architecture decision economics and task-local language metadata for HVR-020. The plan now maps
  HVR-010 through HVR-050 to reversible increments, preserves all three upgrade triggers and the
  three-trial horizon, and binds HVR-020 to the Python standard-library CLI boundary. Focused
  verification review passed without a same-slice regression. A user-authorized, bounded review of
  the 2026-08-12 two-path generated-surface amendment passed with no candidate findings.
- review_budget: Both planned batches were used: one initial bounded review and one focused
  verification review after accepted repairs. The 2026-08-12 manual decision authorized one
  additional scope-amendment review, which is now complete; no further plan-review batch is
  authorized without a new manual decision.
- review_brief: Review the approved design linkage, language seam, serial DAG, semantic profiles,
  delegation/isolation, immutable touch sets, executable oracles, no-live-Herdr boundary, recovery,
  truth-sync handoff, and lifecycle ownership. Do not reopen the approved architecture decision or
  perform repository-wide discovery.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved the reviewed plan and requested
  `$coding:implement-change` on 2026-08-11, then approved the exact two-path generated-surface
  touch-set repair and continuation on 2026-08-12.
- next_entry: implement-change
