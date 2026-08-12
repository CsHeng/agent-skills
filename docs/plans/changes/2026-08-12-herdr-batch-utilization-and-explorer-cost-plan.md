# Herdr Batch Utilization And Explorer Cost Plan

## Status

- plan_version: 1
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: not_started
- plan_review_status: pass_after_one_bounded_repair
- recommended_next_phase: implement
- next_entry: implement-change-via-herdr

## Upstream Design

- design_ref: 2026-08-11-implement-change-via-herdr-design.md
- design_version: sha256:1e7d9b4e66d3716bb12d7b201bd73415e335510b627384cb0dda760981a889c6.
- design_approval_status: approved.
- architecture_decision_ref: HERDR-IMPL-001-explicit-runtime-adapter.
- approved_boundary_amendment: The user approved the 2026-08-12 post-trial correction after session
  `019ff433-a302-7150-878a-4df51290e109`: explorer reasoning is a fixed low-cost runtime class,
  not a relative downgrade from a worker; approved parallel batches must be able to occupy more than
  one Herdr agent pane under one controller; effective-width fallback must be explicit; pure search
  should be split from main-owned synthesis; agent startup needs a bounded shell-readiness gate; and
  controller-owned long-running verification commands may use ordinary owned Herdr panes.
- amendment_precedence: This approved follow-up boundary supersedes only the original design's
  relative explorer-effort rule and repository-single-run lease constraint. It preserves one
  `implement-change` controller, provider-neutral portable plans, controller-owned convergence and
  repair, run-owned Herdr resources, no unrelated pane mutation, and explicit user activation.

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: true
- truth_sync_required: true
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/tools/implement-change-via-herdr/SKILL.md
  - src/skills/tools/implement-change-via-herdr/references/runtime-contract.md
  - src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py
  - src/runtime/harness/execute-runner.sh
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills/plan-change/SKILL.md
  - skills/implement-change/SKILL.md
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
  - tests/fixtures/herdr
- verification_commands:
  - `python3 -m unittest tests.test_implement_change_via_herdr_contracts`
  - `uvx ruff check src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py tests/test_implement_change_via_herdr_contracts.py`
  - `UV_CACHE_DIR="$HOME/.cache/python/market-csheng-herdr" uv tool run ty check src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py`
  - `bash src/runtime/harness/smoke-test/test-execute-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-design-plan-skill-control.sh`
  - `bash src/runtime/harness/smoke-test/test-review-execute-skill-control.sh`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-design-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-agent-native-review.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash scripts/check.sh`
  - `uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Make the explicit Herdr adapter use approved agent capacity instead of
  silently serializing one-controller batches, keep explorers predictably cheap, improve startup
  reliability, and move long controller-owned verification processes out of the main pane without
  changing lifecycle authority or portable task topology.
- non_goals:
  - Add unattended execution, a second lifecycle controller, nested delegation, a generic terminal
    backend registry, tmux support, remote execution, provider actions, commit, push, deploy, plugin
    installation, or publication.
  - Put concrete provider models or reasoning-effort identifiers into portable plan task metadata.
  - Let an explorer synthesize design or implementation decisions, edit files, write tests, run a
    stateful mutation, adjudicate review, or continue the workflow.
  - Let a command pane invent a command, parse plan prose into shell, exceed controller authority,
    bypass task locks, mutate the ledger, or count terminal completion as oracle success.
  - Reuse, focus, rename, interrupt, or close a Herdr workspace, tab, pane, process, or agent not
    proven to be owned by the current controller run.
- future_phase:
  - Promote Herdr from an explicit overlay into ordinary `implement-change` routing only after three
    successful repository-local approved-plan trials cover at least two supported agent kinds and
    show lower coordination cost without recurring ownership or recovery ambiguity.
  - Add a second terminal backend only after a concrete backend proves equivalent readiness,
    lifecycle observation, ownership, and cleanup behavior.
  - Add richer scheduling heuristics only after run evidence shows the current explicit explorer
    decomposition and batch-capacity evidence remain insufficient.
- decision_status: ready_for_review
- oracle_strategy: Use model/state-transition tests for controller leases, concurrent run membership,
  readiness, command jobs, cleanup, and recovery; executable task-graph fixtures for batch selection,
  effective capacity, explicit serial fallback, and required-capacity stops; capability contract tests
  for fixed low-cost explorer bindings; fake-Herdr argv and lifecycle tests for deterministic coverage;
  then one bounded real-Herdr canary for simultaneous agents, command panes, reviewer startup, and
  exact cleanup.
- acceptance_oracles:
  - A pure fact-search task remains `fast` / `light` / `shared-read-only`, is split from any main-owned
    synthesis task, and binds under semantic routing to a low-cost explorer class with low as the
    default and medium as the maximum accepted effort; high and xhigh cannot be labeled explorer.
  - An explicit model policy that cannot supply the explorer cost ceiling returns a typed capability
    result or uses the already-approved main fallback; it never records a high-effort child as an
    explorer or compares explorer effort to a worker baseline.
  - An approved width-two batch produces binding evidence containing planned width, ready width,
    runtime capacity, effective width, selected task IDs, batch identity, and every limiting factor.
  - Allowed work that runs at width one records an exact `serial_fallback_reason`; required width that
    cannot be honored returns the existing typed capacity stop before Herdr allocation.
  - One controller, plan digest, workspace, repository identity, and approved batch may hold multiple
    live child run members concurrently; a second controller, mismatched plan or workspace, duplicate
    task attempt, unselected task, or excess width fails before resource allocation.
  - Each concurrent member retains independent state, nonce, task, pane, agent, evidence, recovery,
    and cleanup identity. Removing one member cannot release or close another member's resources;
    the controller lease releases only after the final owned live member is gone.
  - Agent startup waits for a verified available interactive shell with a bounded deadline and typed
    diagnostics, eliminating the observed immediate `agent_pane_busy` and non-available-shell race
    without retrying blindly or touching an unrelated pane.
  - A controller-issued command job uses an owned ordinary Herdr pane, exact controller-authored
    command text and cwd, declared timeout and task locks, bounded redacted output, exit evidence,
    and exact cleanup. It cannot select tasks, update the ledger, satisfy an oracle by claim, or
    interpolate prompt, agent output, or other untrusted fields into a shell command.
  - Fake-Herdr tests prove simultaneous agent and command membership, partial cleanup, controller
    crash/restart, stale-member diagnosis, mixed-resource protection, bounded waits, and secret-safe
    evidence deterministically.
  - A real-Herdr canary uses only run-owned background resources, observes two supported low-cost
    explorer processes alive at the same time with low as the default and medium as the ceiling,
    completes two ordinary command jobs, starts one read-only reviewer without a shell-readiness
    race, and leaves no owned residue or unrelated state change. Concrete agent kind, model, and
    effort remain runtime evidence.
  - Source skills, runtime scripts, root-flat generated skills, architecture truth, diagrams, tests,
    and plugin validation agree; no generated file is hand-edited and all focused and aggregate gates
    pass.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Approved Architecture Decision

- architecture_decision_ref: HERDR-IMPL-001-explicit-runtime-adapter with the approved 2026-08-12
  post-trial boundary amendment.
- decision_fidelity: Preserve one main `implement-change` controller and one explicit Herdr adapter.
  Replace the repository-single-run lease with a controller-scoped lease containing independently
  owned run members; keep portable explorer metadata semantic while enforcing a fixed low-cost
  physical binding at runtime; use explicit plan tasks to separate factual exploration from main
  synthesis; and add controller-owned command panes without granting them task authority.
- reversible_increments:
  - HBU-010 changes only portable guidance and runtime role/cost policy; generated surfaces remain
    reproducible and the adapter protocol is unchanged until later tasks.
  - HBU-020 adds batch provenance and capacity/fallback evidence to the existing controller envelope
    while preserving current single-task bindings.
  - HBU-030 migrates lease state with schema-versioned fixtures and retains typed rejection of legacy,
    stale, foreign, or ambiguous state rather than silently adopting it.
  - HBU-040 adds command jobs as a separate controller-issued binding kind; removing that kind leaves
    delegated agent execution intact.
  - HBU-050 regenerates and documents the integrated contract only after focused behavior passes.
  - HBU-060 and HBU-070 are explicit no-write explorer canaries; HBU-080 performs final acceptance
    and review without installing, committing, pushing, or publishing.
- upgrade_triggers:
  - Return `needs-design-decision` if safe concurrent membership requires multiple lifecycle
    controllers, shared writable checkouts, weakened ownership proof, lease stealing, or agent-owned
    convergence.
  - Return `needs-design-decision` if command jobs require parsing arbitrary plan prose, persisting
    command secrets, or granting a pane more authority than the controller already holds.
  - Return `needs-plan-change` if live acceptance requires a new provider, unsupported model, external
    credential, repository write outside the touch set, or mutation of unrelated Herdr resources.
  - Add a plan-level role field only if repeated trial evidence shows explorer versus worker cannot
    be derived from isolation, write refs, execution profile, and reasoning profile.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 2 for the source-contract bootstrap batch and the required live-explorer
  canary batch. One controller may host up to the approved batch width of concurrently owned Herdr
  run members after HBU-030. Adapter mutation, generation, convergence, command-job acceptance,
  review, and truth preparation remain serial.
- explorer_binding_policy: Portable plans continue to say `fast` and `light`. Under semantic routing,
  a concrete explorer uses the lowest compatible low-cost model class, defaults to `low`, accepts
  `medium` only as the ceiling, and rejects `high` or `xhigh`. This is an absolute role invariant,
  not a comparison with a worker. An explicit policy that resolves above the ceiling cannot retain
  the child `explorer` role.
- worker_binding_policy: Worker capability follows the plan-owned execution and reasoning profiles;
  this change does not lower worker reasoning or force a provider.
- reviewer_binding_policy: Reviewer remains a read-only high-judgment actor and returns candidates
  only. The main controller adjudicates and repairs.
- bootstrap_boundary: HBU-010 and HBU-020 may run concurrently only when the currently installed
  runtime can honor width two safely. Because the existing Herdr lease is single-run, an allowed
  width-one bootstrap fallback is valid only when it is explicitly recorded; the new concurrency
  behavior is required by the HBU-060/HBU-070 canary batch after HBU-030 converges.

## Parallel Batches

- batch_id: HBU-source-contracts
- tasks:
  - HBU-010
  - HBU-020
- max_parallelism: 2
- parallel_policy: allowed
- delegation_policy: preferred
- isolation: isolated-worktree
- dependency_freeze: Both tasks start from the approved repository baseline, write disjoint source
  and test paths, hold disjoint locks, and do not depend on each other. HBU-010 owns workflow skills;
  HBU-020 owns the deterministic runner and its smoke test. Neither edits the adapter or generated
  surface.
- convergence_task: HBU-030
- fallback_policy: The existing adapter may serialize this bootstrap batch only with machine-readable
  planned/effective-width and exact fallback evidence. Serialization does not alter task scope,
  worktrees, locks, or oracles.

- batch_id: HBU-live-explorer-canary
- tasks:
  - HBU-060
  - HBU-070
- max_parallelism: 2
- parallel_policy: required
- delegation_policy: preferred
- isolation: shared-read-only
- dependency_freeze: Both explorers depend only on the integrated HBU-050 source, have no write refs,
  inspect disjoint factual surfaces, hold disjoint evidence locks, and return bounded evidence without
  synthesis. HBU-080 alone judges their results and concurrent-lifetime evidence.
- convergence_task: HBU-080
- fallback_policy: No serial fallback is allowed. Effective width below two returns
  `parallel_capacity_required` before live explorer allocation.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes HBU-010 through HBU-080 as one continuous local implementation unit,
    including the named width-two isolated bootstrap batch, the required width-two read-only explorer
    batch, fake Herdr processes, and one bounded live-Herdr
    canary that creates and cleans only run-owned background tabs, panes, agents, and command jobs in
    the current market-csheng workspace. It authorizes supported low-cost explorer inference within
    the low-default/medium-ceiling rule, plus one read-only reviewer. Concrete physical bindings are
    runtime evidence. It does not authorize touching unrelated
    Herdr state, plugin installation, commit, push, deploy, provider mutation, publication, or close.
- runtime_contingencies:
  - X1: If the repository or any declared worktree contains unexplained overlapping user changes,
    preserve them and return `blocked_source_baseline` before mutation or integration.
  - X2: If the current Herdr caller context cannot be proven, another controller owns the repository
    lease, or owned-resource identity becomes ambiguous, stop with typed evidence and do not reclaim,
    close, or reuse the resource.
  - X3: If a width-two required acceptance batch cannot observe two live owned members because Herdr
    lacks the necessary process or pane guarantees, preserve fake-test evidence and return
    `needs-design-decision` rather than claiming concurrency.
  - X4: If no supported explorer binding satisfies the low-default/medium-ceiling rule, return
    `delegated_capability_unavailable`; do not silently use high or xhigh under the explorer role.
  - X5: If command-pane safety requires untrusted interpolation, hidden credentials, undeclared locks,
    or a shell surface broader than controller authority, omit the command-job path and return
    `needs-design-decision`.
  - X6: If focused or aggregate checks fail outside causal changed paths, stop and diagnose; repair
    only accepted in-scope failures and do not weaken concurrency, ownership, readiness, or cost
    oracles.
- planned_stop_points:
  - none inside HBU-010 through HBU-080; successful implementation and review route to the separate
    truth-sync approval gate.
- task_ordering_rationale: Update portable role guidance and controller binding provenance first in
  a disjoint bootstrap batch; converge those contracts into the adapter's lease and readiness state
  machine; add command panes only after member ownership is safe; regenerate shared surfaces once;
  then require offline and live acceptance plus bounded review before truth synchronization.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Preserve the initial tracked and untracked baseline, isolate delegated writers,
  integrate only verified task diffs, and repair only within declared refs. Never discard or overwrite
  unrelated user changes.
- state_boundary: Persist schema-versioned controller and member ownership before fallible Herdr
  mutation. On failure, retain typed state and bounded evidence; cleanup only resources whose opaque
  IDs and controller/member identity are proven.
- lease_boundary: Never steal an active or ambiguous lease. A stale member can be removed only after
  proving its recorded agent, process, pane, and tab are absent or after explicit owned cleanup.
- live_boundary: A failed canary stops further live allocation, preserves bounded diagnostics, and
  cleans only proven run-owned resources. It never stops Herdr, closes the workspace, or touches an
  unrelated tab or pane.
- generated_boundary: Regenerate from `src/skills/` and harness sources, compare deterministic
  outputs, and repair source or generator causes. Generated hand edits are forbidden.
- external_boundary: Commit, push, install, deploy, provider action, publication, and close are not
  recovery actions under this plan.
- guarded_rollback: none

## Task 1: Define absolute explorer cost and search-synthesis decomposition

- task_id: HBU-010
- depends_on:
  - none
- scope_slice: Replace relative explorer-downgrade language with an absolute low-cost runtime
  invariant; require planners to split pure repository search and factual confirmation into explicit
  explorer tasks when the surrounding work also needs main-owned synthesis; preserve provider-neutral
  task metadata and controller-owned judgment.
- impl_file_refs:
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
- test_file_refs:
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
- verification_scope:
  - Prove an eligible explorer is exactly no-write `fast` / `light` / `shared-read-only`, returns only
    bounded facts and open questions, and cannot synthesize a decision or inherit implementation
    authority.
  - Prove mixed search-and-judgment work is represented as independent explorer task IDs followed by
    a main synthesis task rather than one coarse delegation-forbidden main task.
  - Prove runtime guidance uses low by default and medium as the ceiling for explorer child effort,
    rejects high/xhigh explorer classification, and contains no worker-relative downgrade rule.
  - Run the two focused skill-control smoke tests and `git diff --check`.
- failing_oracle_first: Add source-contract assertions that fail on `strict downgrade`,
  `one provider tier below`, worker-baseline comparison, high/xhigh explorer allowance, or guidance
  that lets a main synthesis task absorb otherwise independent fact-search slices.
- executor_mode: subagent
- parallel_group: HBU-source-contracts
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: balanced
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - workflow-skill-contracts
- task_review_depth: deep
- done_when:
  - Planning and implementation guidance agree on one absolute low-cost explorer class and explicit
    search-before-synthesis topology.
  - Portable plans still contain semantic profiles only; concrete provider mappings remain runtime
    evidence.
  - Focused smoke tests pass without weakening worker, reviewer, or controller authority.
- failure_policy: fix_forward

## Task 2: Make batch provenance and capacity fallback executable

- task_id: HBU-020
- depends_on:
  - none
- scope_slice: Extend deterministic runtime binding and controller envelopes with approved batch
  identity, selected task membership, planned and effective width, limiting factors, and explicit
  serialization evidence suitable for safe concurrent Herdr member admission.
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
- verification_scope:
  - Use executable DAG fixtures to cover width two, ready frontier width, actor capacity, batch limit,
    disjoint locks and writes, allowed width-one fallback, required-capacity stop, and topology parity
    under semantic routing and inherit-main.
  - Bind each selected task envelope to one immutable batch provenance record without allowing the
    adapter or request file to add a task, change width, or select a different group.
  - Emit exact limiting factors and `serial_fallback_reason` when allowed work runs at width one;
    preserve the existing typed `parallel_capacity_required` stop for required work.
  - Run `bash -n`, ShellCheck when available, the focused execute-runner smoke test, and
    `git diff --check`.
- failing_oracle_first: Add fixtures that fail when a width-two plan silently returns one binding,
  when the envelope lacks batch membership or capacity evidence, when a request forges a selected
  task, and when required width reaches Herdr allocation at capacity one.
- executor_mode: subagent
- parallel_group: HBU-source-contracts
- parallel_policy: allowed
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - runtime-binding-contract
- task_review_depth: deep
- done_when:
  - Runtime binding exposes enough immutable evidence for the adapter to admit exactly the approved
    concurrent members and explain every capacity reduction.
  - Allowed serialization is visible and required-capacity failure remains zero-mutation.
  - Focused runner checks pass with unchanged task IDs, topology, authority, and oracles.
- failure_policy: fix_forward

## Task 3: Admit concurrent controller-owned Herdr members and gate shell readiness

- task_id: HBU-030
- depends_on:
  - HBU-010
  - HBU-020
- scope_slice: Replace the repository-single-run lease with a controller-scoped, plan- and
  workspace-bound lease containing independent approved run members; enforce effective width and
  exact batch membership; add a bounded shell-readiness transition before agent startup; preserve
  per-member recovery, evidence, and cleanup ownership.
- implementation_archetype: cli-tool
- implementation_language: Python 3 standard library
- language_rationale: The existing adapter is a Python state machine with atomic JSON persistence,
  subprocess argv control, and fake-Herdr tests; extending that owner preserves one deterministic
  lease and lifecycle implementation without adding a dependency or parallel shell authority.
- impl_file_refs:
  - src/skills/tools/implement-change-via-herdr/SKILL.md
  - src/skills/tools/implement-change-via-herdr/references/runtime-contract.md
  - src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py
- test_file_refs:
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/herdr
- verification_scope:
  - Model controller lease acquisition, first and subsequent member admission, batch-width exhaustion,
    duplicate task attempts, foreign controller/plan/workspace/group rejection, independent member
    wait/collect, partial cleanup, final release, crash/restart, stale diagnosis, and mixed-resource
    protection.
  - Assert two approved members can remain live simultaneously and one cleanup cannot close, release,
    or alter the other member.
  - Poll only the allocated pane's process information until an available interactive shell is
    proven or a bounded typed deadline expires; then start the agent exactly once.
  - Preserve no-focus allocation, opaque-ID authority, exact native agent argv, bounded evidence,
    redaction, and rejection of legacy or malformed state.
  - Run focused unittest/pytest, Ruff, ty, skill validation, and `git diff --check`.
- failing_oracle_first: Add model fixtures reproducing repository-lease serialization, immediate
  `agent_pane_busy`, non-available-shell reviewer startup, partial-member cleanup, and a second
  controller collision before changing the state machine.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - herdr-controller-lease
  - herdr-member-state
- task_review_depth: full
- done_when:
  - One approved controller can use the plan's effective width without allowing another controller,
    unselected task, duplicate attempt, or excess member.
  - Shell readiness is a distinct bounded state with actionable evidence, and the observed startup
    races are covered by failing-then-passing fixtures.
  - Member recovery and cleanup remain exact, secret-safe, restart-safe, and independent.
- failure_policy: fix_forward

## Task 4: Add controller-owned ordinary command jobs

- task_id: HBU-040
- depends_on:
  - HBU-030
- scope_slice: Add a separate controller-issued command-job binding that runs long local verification
  commands in owned ordinary Herdr panes, records bounded process and exit evidence, observes task
  locks and capacity, and returns control to the main controller for oracle judgment.
- implementation_archetype: cli-tool
- implementation_language: Python 3 standard library
- language_rationale: Command jobs share the adapter's controller lease, member ownership, Herdr argv,
  wait, evidence, recovery, and cleanup machinery; keeping them in the existing Python state machine
  avoids an untracked shell runner and a second ownership implementation.
- impl_file_refs:
  - src/skills/tools/implement-change-via-herdr/SKILL.md
  - src/skills/tools/implement-change-via-herdr/references/runtime-contract.md
  - src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py
  - src/skills/workflows/implement-change/SKILL.md
  - src/runtime/harness/execute-runner.sh
- test_file_refs:
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/herdr
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
- verification_scope:
  - Require a controller-issued owner-only envelope with exact cwd, literal command, task or gate
    provenance, timeout, resource locks, output bound, and run nonce; reject task/agent content,
    newline/control injection, undeclared cwd, or an unbounded wait.
  - Use `pane run`, pane-specific process/output observation, bounded redacted collection, and owned
    cleanup without pretending Herdr provides agent lifecycle for an ordinary command.
  - Prove command exit is evidence only: the main controller still validates declared oracles,
    changed paths, convergence, review, repair, and continuation.
  - Cover two compatible command members concurrently, conflicting locks serially, timeout and
    nonzero exit, controller restart, partial cleanup, mixed pane protection, and secret exclusion.
  - Run focused unittest/pytest, Ruff, ty, skill-control smoke tests, and `git diff --check`.
- failing_oracle_first: Add red fixtures for command invention, untrusted interpolation, missing
  locks, foreign cwd, unbounded wait/output, ledger mutation, and treating exit zero as task success;
  add a positive fixture with two disjoint long-running commands alive concurrently.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: preferred
- execution_profile: balanced
- reasoning_profile: standard
- isolation: isolated-worktree
- resource_locks:
  - herdr-command-members
  - herdr-controller-lease
  - runtime-binding-contract
- task_review_depth: deep
- done_when:
  - Long local verification can leave the main pane while remaining controller-issued, lock-aware,
    bounded, observable, recoverable, and non-authoritative.
  - Command members coexist safely with agent members and cannot interpolate untrusted runtime data.
  - Focused adapter and workflow checks pass.
- failure_policy: fix_forward

## Task 5: Converge generated surfaces and stable architecture truth

- task_id: HBU-050
- depends_on:
  - HBU-040
- scope_slice: Integrate verified source changes, update stable workflow architecture, regenerate every
  root-flat skill and workflow diagram projection, and prove source/generated parity before live
  acceptance.
- impl_file_refs:
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills/plan-change
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
  - Document absolute explorer cost, explicit search/synthesis decomposition, planned-versus-effective
    capacity evidence, controller lease with concurrent members, shell readiness, command jobs, and
    unchanged lifecycle authority without duplicating detailed adapter state tables.
  - Regenerate the skill index, root-flat skills, PlantUML sources, and SVGs from source; compare all
    tracked projections and reject any generated hand edit or stale bundled runner.
  - Run source-map, sovereign-surface, diagram, docs-boundary, and `git diff --check` gates.
- failing_oracle_first: Generation/check mode must fail against the pre-convergence generated skills,
  diagrams, or bundled runners before regeneration and pass without a second diff afterward.
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
  - Stable architecture and source skills describe one controller, the fixed explorer cost class,
    concurrent owned members, readiness gate, and non-authoritative command jobs consistently.
  - All root-flat and diagram projections reproduce exactly from source.
  - No generated or stable path outside the approved touch set changes.
- failure_policy: fix_forward

## Task 6: Run the workflow-contract explorer canary

- task_id: HBU-060
- depends_on:
  - HBU-050
- scope_slice: In a run-owned Herdr agent pane, perform only bounded factual confirmation that the
  integrated planning and implementation skills define absolute low-cost explorer behavior,
  explicit fact-search decomposition, and unchanged main-owned synthesis and continuation.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Return exact file and line references for the explorer eligibility, low-default/medium-ceiling,
    search/synthesis split, and controller authority statements.
  - Record runtime binding and lifecycle timestamps sufficient for HBU-080 to verify this explorer
    overlapped with HBU-070, while returning no design or implementation judgment.
- failing_oracle_first: The binding must fail before allocation unless it is no-write `fast` /
  `light` / `shared-read-only`, uses a supported effort no higher than medium, and is selected in the
  required HBU-live-explorer-canary batch.
- executor_mode: subagent
- parallel_group: HBU-live-explorer-canary
- parallel_policy: required
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: light
- isolation: shared-read-only
- resource_locks:
  - live-explorer-workflow-evidence
- task_review_depth: focused
- done_when:
  - Bounded factual evidence identifies the integrated workflow contract without a source write,
    test write, synthesis decision, or authority claim.
  - Runtime evidence is sufficient for the controller to verify concurrent lifetime and exact owned
    cleanup.
- failure_policy: stop_and_diagnose

## Task 7: Run the adapter-contract explorer canary

- task_id: HBU-070
- depends_on:
  - HBU-050
- scope_slice: In a second concurrently owned Herdr agent pane, perform only bounded factual
  confirmation that the integrated adapter contract defines controller-scoped concurrent members,
  explicit capacity evidence, shell readiness, and non-authoritative ordinary command jobs.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Return exact file and line references for member admission, planned/effective width and fallback,
    readiness, command-job authority, and cleanup statements.
  - Record runtime binding and lifecycle timestamps sufficient for HBU-080 to verify this explorer
    overlapped with HBU-060, while returning no design or implementation judgment.
- failing_oracle_first: The binding must fail before allocation unless it is no-write `fast` /
  `light` / `shared-read-only`, uses a supported effort no higher than medium, and is selected in the
  required HBU-live-explorer-canary batch.
- executor_mode: subagent
- parallel_group: HBU-live-explorer-canary
- parallel_policy: required
- delegation_policy: preferred
- execution_profile: fast
- reasoning_profile: light
- isolation: shared-read-only
- resource_locks:
  - live-explorer-adapter-evidence
- task_review_depth: focused
- done_when:
  - Bounded factual evidence identifies the integrated adapter contract without a source write,
    test write, synthesis decision, or authority claim.
  - Runtime evidence is sufficient for the controller to verify concurrent lifetime and exact owned
    cleanup.
- failure_policy: stop_and_diagnose

## Task 8: Run aggregate, command-job, cleanup, and review acceptance

- task_id: HBU-080
- depends_on:
  - HBU-060
  - HBU-070
- scope_slice: Judge the two explorer claims and concurrency evidence, run focused and aggregate
  offline gates, execute bounded ordinary command jobs, verify reviewer startup and exact cleanup,
  perform bounded implementation review, repair only accepted in-scope findings, and prepare the
  truth-sync handoff.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Prove HBU-060 and HBU-070 were both selected from the required batch, used supported low-cost
    bindings with no effort above medium, had overlapping live intervals, returned only bounded
    facts, and changed no repository path.
  - Run every declared focused test, all sovereign harness smoke tests, aggregate `scripts/check.sh`,
    plugin validation, and `git diff --check` from the integrated source.
  - Run two disjoint ordinary command jobs concurrently, verify exit/output evidence and controller
    oracle judgment, then start one bounded read-only reviewer after the shell-readiness gate.
  - Clean every canary-owned agent, pane, tab, process, member, and lease; compare before/after Herdr
    inventories and repository status to prove no unrelated resource or source changed.
  - Route the exact implementation diff and evidence through `review-change`; adjudicate candidates,
    permit at most two causal repair batches by reopening their causing task, rerun narrow and
    aggregate checks, and stop at truth-sync approval.
- failing_oracle_first: Acceptance must fail if effective width is one, either explorer binding exceeds
  medium, two member lifetimes do not overlap, the reviewer starts before shell readiness, a command
  job bypasses locks or controller judgment, any explorer writes, or any owned/foreign cleanup
  boundary is ambiguous.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - live-herdr-canary
  - aggregate-verification
  - implementation-review
- task_review_depth: full
- done_when:
  - Offline and real-Herdr oracles prove width-two agent use, fixed cheap explorer binding, reliable
    startup, command-job operation, exact cleanup, and unchanged controller authority.
  - All focused and aggregate repository gates pass with no accepted review finding remaining.
  - The controller records truth-sync readiness without installing, committing, pushing, deploying,
    publishing, or closing.
- failure_policy: stop_and_diagnose

## Truth Sync Handoff

- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
- docs_governance_predicates:
  - canonical-terminology-across-surfaces
- handoff_scope: After implementation, real-Herdr acceptance, and bounded review pass, synchronize
  stable workflow truth for the absolute low-cost explorer class, explicit fact-search decomposition,
  effective-capacity evidence, controller-scoped concurrent member lease, shell-readiness gate,
  controller-owned command jobs, and unchanged lifecycle authority. Generated diagrams remain
  subordinate projections and must be regenerated before truth sync.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_one_bounded_repair
- candidate_findings: The initial bounded review produced four accepted findings: the live canary
  lacked approved explorer task IDs, the generated touch set omitted the sync-truth runner bundle,
  concrete provider bindings leaked into portable canary approval, and two approved architecture
  upgrade triggers were incomplete. Main adjudication also accepted one touch-set omission for the
  command-job controller envelope. No candidate remains unresolved.
- review_evidence: Repairs added the required HBU-060/HBU-070 no-write explorer batch and main-owned
  HBU-080 judgment, added sync-truth and command-envelope runner refs, kept the canary provider-neutral,
  restored the three-trial/two-kind and role-ambiguity triggers, and routed repair through causal
  tasks. Focused verification review found no new DAG, oracle, authority, or touch-set conflict.
- review_budget: One initial bounded review and one focused verification review were used. No further
  plan-review batch is authorized without new causal plan scope.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed plan and requested
  `$coding:implement-change-via-herdr` on 2026-08-12.
- next_entry: implement-change-via-herdr
