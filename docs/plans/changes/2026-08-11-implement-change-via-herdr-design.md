# Implement Change via Herdr Runtime Adapter Design

## Status

- design_version: 2
- decision_status: ready_for_approval
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this design and requested `$coding:plan-change` on
  2026-08-11, then approved the exact two-path generated-surface amendment on 2026-08-12.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The current harness already separates portable plan topology from implementation-time actor and
model binding. It can select main or delegated actors, enforce isolated writer worktrees, converge
parallel batches, and route bounded review, but it does not provide a deterministic adapter for
running delegated coding-agent CLIs through Herdr tabs and panes.

The desired experiment uses one strong Codex main agent as implementation controller and final
judge, a strong independent Codex reviewer, and cheaper or faster coding-agent CLIs for bounded
worker and explorer tasks. Herdr should own terminal placement, process lifecycle, prompt delivery,
state observation, and owned-resource cleanup without becoming a second implementation controller.
The design also needs to coexist with unrelated work already running in Herdr.

## Goals

- Add an explicitly invoked `implement-change-via-herdr` public entry that composes the existing
  `implement-change` controller instead of creating another lifecycle owner.
- Preserve the approved plan as the sole source of task IDs, dependencies, serial or parallel
  shape, delegation policy, semantic execution and reasoning profiles, isolation, locks, touch
  sets, oracles, review depth, and failure policy.
- Make `implement-change` bind each selected actor at runtime to a concrete coding-agent CLI,
  model, reasoning effort, permission mode, worktree, and Herdr location.
- Use role-specific Herdr agents for `reviewer`, `worker`, and `explorer` work while the initiating
  main Codex agent remains the sole `orchestrator` and controller.
- Default pure search-and-confirmation exploration to `fast` execution and `light` reasoning, with
  the physical explorer binding one supported reasoning tier below the comparable worker default
  when the selected CLI exposes ordered effort levels.
- Record enough run state to resume, audit claims, verify touch sets and oracles, and clean up only
  tabs and panes created by the current run.
- Keep the first milestone small enough to validate with a fake Herdr CLI and then evaluate through
  a few user-run, repository-local tasks before generalizing the backend.

## Non-Goals

- Add `implement-change-via-herdr` to the sovereign lifecycle kernel, change
  `phase_routes.execute = implement-change`, or transfer repair, review adjudication, truth sync, or
  close authority out of `implement-change`.
- Launch or attach to Herdr from an external process when `HERDR_ENV=1` is absent. The first
  milestone must start from a main-agent pane already running inside Herdr.
- Treat Herdr as a generic `tmux` clone or implement a second terminal backend in this milestone.
- Store provider model identifiers, coding-agent CLI names, or permission flags in the approved
  plan schema or stable provider-neutral workflow contracts.
- Add a plan-level `work_role` field before real runs demonstrate that deterministic role derivation
  is ambiguous.
- Let delegated agents integrate peer work, widen scope, mutate external systems, push, deploy,
  adjudicate findings, repair outside their task slice, or decide continuation.
- Operate, rename, close, interrupt, or reuse panes and tabs that are not recorded as resources
  owned by the current adapter run.

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

### Lifecycle And Public Entry

`implement-change-via-herdr` is a user-facing parallel entry but a lower-plane runtime adapter. Its
manifest contract is:

```toml
[skills.implement-change-via-herdr]
source = "src/skills/tools/implement-change-via-herdr"
public_id = "implement-change-via-herdr"
category = "tool"
install = ["claude", "codex", "root-flat"]
lifecycle_owner = false
activation_mode = "explicit"
default_role = "overlay"
may_mutate_repo = true
may_spawn_agent = true
requires_explicit_user_request = true
requires_approved_plan = true
semantic_requires = ["implement-change"]
```

The skill owns one explicit routing case for requests that name
`$coding:implement-change-via-herdr` or explicitly ask to execute an approved plan through Herdr.
Ordinary approved-plan execution remains owned directly by `implement-change`. The adapter omits
`runtime_bundle`: repository validation reserves the shared harness bundle for lifecycle-owning
workflow skills. Its own deterministic scripts ship inside the tool skill, while the main agent
resolves and invokes the runner bundled with the activated `implement-change` skill.
Because the new explicit case is installed routing truth, `use-coding-skills.semantic_requires`
also gains `implement-change-via-herdr`; that discovery edge does not change lifecycle ownership.

### Plan And Runtime Binding

`plan-change` continues to own portable semantics:

- task DAG, named batch, dependency freeze, delegation policy, and batch limit
- `execution_profile: deep | balanced | fast`
- `reasoning_profile: deep | standard | light`
- isolation, writable refs, resource locks, oracles, review depth, and failure policy

Planning guidance should make pure repository search and factual confirmation a
`fast` / `light` / `shared-read-only` slice with no implementation or test write refs. A read-only
task that requires deep synthesis does not qualify for the cheap explorer default.

`implement-change` remains the physical binding owner. A Herdr binding record contains:

- plan digest, task ID, attempt, and derived runtime role
- terminal backend and concrete agent kind
- concrete model, reasoning effort, permission mode, sandbox mode, and delegated capability profile
- declared model-control-plane endpoint or broker plus a credential reference, never credential data
- Herdr workspace, tab, pane, and agent opaque IDs plus the human-readable agent name
- controller checkout or isolated worktree path
- approved task touch set, oracle refs, start state, terminal state, and collected evidence refs

The binding record is runtime evidence, not a plan amendment. Runtime mapping may be more
conservative than the approved plan but cannot raise concurrency, delegation, authority, or change
the task's semantic execution and reasoning profiles. Concrete provider effort is an explicit
mapping to those profiles, not a new source of task scope or authority.

### Runtime Roles

The first milestone derives roles without changing the plan schema:

- `orchestrator`: the initiating main agent that activated `implement-change`; it is never launched
  again in a Herdr child pane.
- `reviewer`: the actor selected by the `review-change` gate for a bounded read-only review brief.
- `explorer`: a delegated task only when it is `shared-read-only`, has no write refs, and is already
  approved as `fast` plus `light`.
- `worker`: every other delegated implementation task, including read-only work that needs more
  than search and factual confirmation.

Role derivation never downgrades an approved task profile. Repeated real-run ambiguity is an
upgrade trigger for a separately designed `work_role` plan field, not permission for the adapter to
guess.

The user's initial experimental preferences are run-scoped mappings, not repository defaults:

| Role | Semantic default | Initial physical preference | Authority |
|---|---|---|---|
| orchestrator | current main, deep judgment | Codex CLI with SOL, high or higher | lifecycle controller and final judge |
| reviewer | bounded review, deep judgment | Codex CLI with SOL, high or higher | candidate findings only |
| worker | plan-owned profile | Grok Build with Grok 4.5 high/medium, or Codex CLI with Luna xhigh when fast execution still needs standard/deep reasoning | assigned local task slice |
| explorer | fast/light | Under semantic routing, Codex CLI with Luna one compatible effort tier below the worker default, or Grok Build with Grok 4.5 medium | read-only search and confirmation |

Execution and reasoning are independent axes: a fast model may still be approved for standard or
deep reasoning. Under `semantic-routing`, an explorer uses the lowest available effort that maps to
`light` and preferably sits one provider tier below the comparable worker. If no such lower tier is
available, the controller chooses another compatible binding or records the conservative fallback;
it never relabels a non-light binding as light. An explicit `inherit-main` or `runtime-default`
policy takes precedence over the relative downgrade preference and records that choice without
changing the explorer's read-only role.

If an explorer cannot resolve a question through bounded search, it returns evidence and the open
question to the orchestrator. It does not silently increase scope, become a reviewer, or make a
design decision.

### Herdr Topology And Naming

The first milestone uses Herdr as an agent-aware terminal backend:

- workspace: reuse the initiating pane's current project workspace; do not create, rename, focus,
  close, or attach another workspace
- tab: create one run-owned background tab per approved plan execution attempt with `--no-focus`
- pane: create one run-owned pane per fixed role, task, and attempt, using the controller-provided
  checkout or worktree as its working directory
- agent: start exactly one supported interactive coding-agent process in each owned pane

The current main-agent pane is not renamed or repurposed. It receives only a logical orchestrator
handle in the run manifest. Child agent names are role-first, unique, and no longer than 32
characters:

```text
orchestrator-wolf-k7
reviewer-owl-k7-r1
explorer-fox-k7-t02-a1
worker-otter-k7-t03-a1
```

The animal is a stable mnemonic for the role, not a provider or capability marker. Short run,
task, review-round, and attempt suffixes prevent collisions. Names and labels are display handles;
Herdr's opaque workspace, tab, pane, and agent IDs remain authoritative.

Preflight captures `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`, and `HERDR_PANE_ID` from the initiating
pane, verifies that they resolve to the expected controller context, and binds them to the run
manifest. Every later operation uses `--current`, an explicit opaque ID, or a unique owned agent
name as appropriate. The adapter never relies on the UI-focused pane, and a caller-context or
workspace mismatch is a zero-mutation stop.

### Adapter Protocol And State

The deterministic adapter exposes a narrow internal command surface rather than a provider plugin
framework:

```text
preflight -> allocate -> start -> prompt -> wait -> collect
          -> controller-verify -> converge -> review -> cleanup
```

- `preflight` requires `HERDR_ENV=1`, the Herdr CLI, an approved plan, an exact caller context, a
  matching repository root, a compatible delegated capability profile, and a controller-issued
  binding envelope. Failure returns a typed zero-mutation stop.
- `allocate` creates only the owned background tab and child panes and records every returned ID
  before further work.
- `start` passes the concrete agent kind and model/reasoning/permission arguments as an argument
  vector; it never constructs a shell command from prompt or task content.
- `prompt` targets only a freshly started, non-working owned agent. It never submits into an
  already busy turn.
- `wait` always uses bounded timeouts and recognizes `idle`, `done`, `blocked`, `unknown`, prompt
  stall, and timeout as distinct observations.
- `collect` reads bounded terminal evidence and the agent's explicit completion claim. Raw terminal
  history and prompt bodies are not persisted by default.
- `controller-verify`, `converge`, and `review` are controller states, not Herdr adapter authority.
  An agent reaching `idle` or `done` is only a claim until changed paths, task oracles, and batch
  convergence pass.
- `cleanup` re-enumerates the owned tab and verifies workspace, tab, pane, and live-agent identity.
  It closes the tab only when every current pane and agent in it is manifest-owned. If any unowned
  or ambiguous resource is present, it closes only individually proven owned child panes and
  returns `cleanup_pending` without closing the tab.

The adapter does not accept a plan path and independently choose work. Before allocation,
`implement-change` uses its deterministic runner to validate the plan and ledger and materialize a
controller binding envelope containing controller identity, plan and ledger digests, the selected
immutable task projection, physical binding, capability profile, and a run nonce. Adapter mutation
commands require that envelope and reject direct or stale use with
`controller_binding_required`. This is a machine-checkable workflow provenance guard, not a
security boundary against the same local OS user. The envelope and nonce are stored with owner-only
permissions. The adapter cannot update the task ledger, converge work, invoke review, repair, or
derive a tail route.

Run state lives under `<repo-root>/.herdr-runs/<run-id>/` and is ignored through the precise
`/.herdr-runs/` rule. `state.json` is schema-versioned, atomically replaced under a single-writer
run lock, and binds the plan digest, repository revision, controller identity, physical bindings,
owned resource IDs, task attempts, observations, and evidence hashes. It must not persist secrets,
credentials, full prompts, or unbounded terminal output.

Preflight also acquires one repository-scoped via-Herdr execution lease, keyed from the canonical
Git common directory and bound to the controller context, plan digest, and run ID. A concurrent or
mismatched active lease returns `herdr_execution_conflict` before allocation. A possibly stale lease
is never stolen automatically: recovery must prove its bound processes and resources are absent or
perform explicit owned-resource cleanup before reclaiming it.

The persisted lease state is `active`, `cleanup-pending`, or `released`. Clean success atomically
marks it `released` only after all owned live agents, panes, and processes are closed. A retained
success or diagnosable failure keeps `cleanup-pending` while any run-owned live process or pane
remains. Explicit owned cleanup releases it after that live set reaches zero; a mixed tab that can no
longer be closed is recorded as cleanup residue but does not hold the execution lease once no
run-owned live process or pane remains. Restart and stale diagnosis read the persisted terminal
state before deciding whether a new run may acquire the lease.

The success default is `close-on-pass-retain-on-failure`; a run-scoped `retain_on_success` option is
allowed for the initial evaluation series. Blocked, unknown, stalled, timed-out, touch-violating,
or unverified agents remain available for diagnosis until an explicit owned-resource cleanup.

### Permissions And Mutation

CLI permission mode and sandbox mode are separate parts of the physical binding. The first
milestone separates the coding agent's control plane from task tool execution. The control plane
permits only the declared CLI's model-inference transport and its narrowly provisioned read-only
authentication handle; endpoint or broker identity and credential references are recorded without
storing credential values. That allowance is runtime plumbing, not permission for a task to invoke
arbitrary network or provider actions.

The task tool plane defines two enforceable delegated capability profiles:

- `delegated-read-only`: read access to the assigned checkout and bounded local inspection tools,
  with repository writes, task-tool network egress, undeclared credentials, SSH, provider actions,
  commit, push, deploy, and destructive actions denied
- `delegated-local-writer`: writes limited to the assigned isolated worktree plus bounded local
  subprocesses and tests, with task-tool network egress, undeclared home credentials, SSH, provider
  actions, commit, push, deploy, and destructive actions outside that worktree denied

Preflight must reject a coding-agent CLI and argument combination that cannot enforce the selected
control-plane/tool-plane separation and selected profile; the task stays with the main controller or
returns `delegated_capability_unavailable` according to its approved delegation policy. An
always-approve mode is valid only inside the enforced `delegated-local-writer` tool sandbox for a
task with an exact touch set and oracle. It changes interactive confirmation behavior only and
grants no additional lifecycle or external authority. Worktree isolation by itself is not a
capability sandbox. Reviewer and explorer actors always use `delegated-read-only`.

Delegated first-milestone actors are restricted to repository-local inspection, edits, and tests.
Any approved provider, deployment, remote, destructive, or externally visible action stays with the
main controller and follows its existing authority gates.

### Backend Boundary

The implementation should name a small agent-terminal adapter boundary but implement only Herdr.
Its required capabilities are owned tab/pane allocation, supported-agent startup, literal prompt
submission, agent-state wait, bounded output collection, and owned-resource cleanup. A future tmux
adapter is not equivalent unless it supplies credible agent readiness and lifecycle observation;
the interface must not be weakened to the lowest common terminal denominator.

No backend registry, dynamic plugin loader, or tmux implementation is justified in this milestone.
A second real backend request is the trigger to extract a reusable interface from observed Herdr
behavior.

## Architecture Decision

- architecture_decision_id: HERDR-IMPL-001-explicit-runtime-adapter
- decision_status: selected
- decision_horizon: Three user-run repository-local implementation trials covering at least two
  supported coding-agent kinds, followed by an evidence review.
- demand_evidence: The user wants to balance cost, speed, and quality by keeping a strong Codex main
  and reviewer while delegating bounded execution and search work to native coding-agent CLIs.
  Herdr already exposes agent-aware start, prompt, wait, read, tab, and pane operations needed for
  the experiment.
- scarce_resource: Main-agent context and attention, reviewer quality, execution latency, model
  spend, and maintainer effort for reliable orchestration and recovery.
- hard_requirements:
  - preserve one `implement-change` lifecycle controller and the approved plan topology
  - do not touch unrelated live Herdr resources
  - keep delegated writers isolated and external mutations controller-owned
  - make completion and cleanup evidence-based and resumable
- options:
  - status quo: Use only the current agent runtime's native subagents. This has the lowest
    maintenance cost but cannot exercise complementary coding-agent harnesses or expose their
    terminal lifecycle through Herdr.
  - smallest sufficient: Add one explicit lower-plane Herdr adapter that composes
    `implement-change`, carries its own deterministic resource-management script, and keeps model
    bindings run-scoped. Selected because it buys the experiment without changing the lifecycle
    kernel or plan schema.
  - structural investment: Generalize `implement-change` immediately into a pluggable multi-backend
    orchestrator with a model registry and new role schema. Deferred because one backend and no
    measured role ambiguity do not justify its implementation, migration, validation, and
    maintenance cost.
- marginal_tradeoff: A thin explicit skill, adapter state machine, fake CLI, and focused tests add
  enough deterministic behavior for safe trials; a generic backend framework would add recurring
  complexity before a second backend proves demand.
- opportunity_cost: The selected work consumes harness, review, documentation, and test capacity,
  but limits that cost by leaving the kernel, phase route, and plan contract version unchanged.
- owner_and_incentives: `plan-change` owns portable difficulty advice, `implement-change` owns
  authority and physical binding, the Herdr adapter owns only resources it creates, and the user
  owns run-scoped model/cost preferences. Each beneficiary therefore carries the corresponding
  decision and cleanup responsibility.
- comparative_advantage: Native coding-agent CLIs retain their own coding harnesses, Herdr supplies
  agent-aware terminal lifecycle and communication, and the existing controller supplies plan,
  review, verification, repair, truth-sync, and close semantics.
- chosen_option: An explicit `implement-change-via-herdr` tool overlay with one Herdr-only adapter
  and no new lifecycle or plan-schema authority.
- upgrade_trigger:
  - After three successful local trials across at least two agent kinds, consider making Herdr a
    first-class runtime backend inside `implement-change` only if the adapter reduces manual
    coordination without recurring ownership or recovery ambiguity.
  - Add a plan-level role field only if repeated trials cannot derive explorer versus worker from
    existing isolation, write-ref, execution-profile, and reasoning-profile metadata.
  - Extract a generic backend interface only when a second concrete backend is requested and can
    satisfy the agent-lifecycle capability contract.
- recovery_and_oracle: Remove or disable the explicit adapter without changing lifecycle routing;
  protect the boundary with fake-Herdr protocol tests, existing harness checks, and user-run local
  trials whose claims are independently verified by the main controller.

## Acceptance Conditions

- `contracts/lifecycle.toml` and `phase_routes.execute = implement-change` remain unchanged, while
  the new explicit skill resolves transitively to `implement-change` and cannot own repair.
- Invocation without `HERDR_ENV=1`, without an approved plan, or from a mismatched repository stops
  before any Herdr or repository mutation.
- Direct or stale adapter mutation without a runner-issued controller binding envelope stops before
  task selection, allocation, prompting, convergence, review, repair, or tail routing.
- The adapter reuses but never renames, focuses, closes, or repurposes the initiating workspace or
  main pane; it binds every operation to the captured caller context, and all created tabs and panes
  use `--no-focus` and are recorded before use.
- Plan fields remain provider-neutral. Every launched agent instead has a complete physical binding
  containing CLI, model, reasoning, permission, location, worktree, task, and attempt evidence.
- Pure explorer tasks are approved as `fast` / `light` / `shared-read-only` and launch read-only.
  Under semantic routing they use one lower compatible effort tier than the comparable worker
  default when possible; explicit `inherit-main` or `runtime-default` choices are recorded instead
  of being silently rewritten.
- Delegated writers cannot start without an isolated worktree; explorer and reviewer bindings
  cannot contain writable refs or write permissions. Unsupported capability profiles fail before
  launch, and always-approve cannot bypass the enforced sandbox.
- Fresh agent names follow the role-first, animal-mnemonic, unique, 32-character-bounded scheme.
- Busy, stalled, blocked, unknown, timed-out, and failed agents produce distinct bounded outcomes;
  no path blindly resends a prompt, closes an unowned pane, or interprets idle/done as passing.
- Controller verification rejects changed paths outside the task touch set and refuses convergence
  until task oracles and any batch integration oracle pass.
- Resume rejects plan-digest, repository-revision, resource-identity, or task-projection mismatch
  rather than attaching to an ambiguous prior run.
- Cleanup tests prove that only manifest-owned resources are closeable and that failure evidence is
  retained by default; a tab containing any unowned live resource is never closed.
- A repository-scoped execution lease prevents overlapping via-Herdr controllers, and stale leases
  require evidence-based diagnosis rather than automatic takeover. Clean success and explicit
  failure cleanup release the lease atomically only after no run-owned live process or pane remains.
- Source skills, routing, generated root-flat payload, skill index, diagrams, README, and stable
  workflow truth agree on the lower-plane adapter boundary.
- Automated implementation validation does not inspect or control the user's currently running
  Herdr tasks.

## Validation

- Build a fake `herdr` executable that records argv and returns fixture JSON or status transitions;
  automated tests must not connect to the live Herdr server.
- Cover missing `HERDR_ENV`, missing CLI, repository mismatch, approved-plan failure, no-focus
  allocation, caller-focus changes, role/name derivation, argument-safe startup, and exact binding
  persistence.
- Cover busy-before-prompt, prompt stall, blocked, unknown, timeout, agent completion claim without
  passing oracle, touch-set violation, worktree requirement, resume mismatch, and cleanup-owned-only.
- Cover direct or stale unbound adapter calls, concurrent controller leases, stale-lease diagnosis,
  clean-success release, retained-failure cleanup, restart, an unowned pane moved into the owned
  tab, unsupported sandbox/permission combinations, allowed per-agent-kind inference transport,
  denied task-tool network/credential/remote/commit/push attempts, and always-approve inside versus
  outside the enforced writer profile.
- Cover Codex and Grok agent-kind bindings plus the relative explorer reasoning downgrade without
  embedding those concrete model choices in the plan schema.
- Regenerate the skill index, root-flat payload, PlantUML sources, and tracked SVGs, then run
  `bash scripts/check.sh` and `git diff --check`.
- Run the repository-required sovereign surface, design runner, plan runner, design/plan control,
  agent-native review, artifact DAG, recovery routing, execute runner, and review/execute control
  smoke tests.
- Validate the Codex plugin surface when generated metadata changes.
- After implementation approval and installation, forward-test from a disposable repository inside
  a newly chosen Herdr context, then run two more repository-local approved plans. Treat those as
  user-observed experiment evidence, not as automated acceptance against the currently active
  Herdr workspace.

## Recovery

- Default to fix-forward inside the adapter, skill, tests, routing, generated surfaces, and stable
  docs declared by the approved plan.
- A failed agent start, prompt, wait, or claim creates a new attempt only after the controller has
  diagnosed the evidence; each attempt gets a fresh pane and agent name.
- A conflicting or stale repository lease stops before allocation. Reclaim it only after its bound
  Herdr resources and controller process are proven absent or an explicit owned cleanup completes.
- Release an active or cleanup-pending lease atomically after successful cleanup leaves no
  run-owned live process or pane. Preserve the terminal lease record for resume and audit instead
  of deleting its history.
- Do not kill, interrupt, reuse, or close an ambiguous resource. Retain it and return a typed stop
  when ownership or identity cannot be proven.
- Do not integrate a touch-set violation or unverified worker claim. Preserve the isolated
  worktree, retain evidence, and let `implement-change` decide bounded repair, replan, redesign, or
  new-authority routing.
- Herdr unavailability does not silently fall back to a different terminal backend for an explicit
  via-Herdr request. Allowed plan concurrency may still serialize according to the existing runner;
  unavailable required capacity returns its existing typed capacity stop.
- Removing the adapter skill, generated projection, explicit routing case, stable documentation,
  and ignored local run state is a reversible exit that leaves the lifecycle kernel and approved
  plan schema intact.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_depth: boundary
- review_status: passed
- candidate_findings: none unresolved
- review_evidence: A bounded delegated review raised eight boundary candidates. The main agent
  accepted and repaired all eight across delegated capability enforcement, agent control-plane
  separation, cleanup inventory, execution lease acquisition and release, semantic reasoning
  mapping, controller binding provenance, and caller-context pinning. Focused verification passed
  with no same-slice regression. A user-authorized, bounded generated-surface amendment review on
  2026-08-12 passed with no candidate findings.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved the reviewed design and requested
  `$coding:plan-change` on 2026-08-11, then approved the exact two-path generated-surface amendment
  on 2026-08-12.
- next_entry: plan-change

## Implementation Surface

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
