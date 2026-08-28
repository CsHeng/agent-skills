+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "high"
truth_sync_required = true

[scope]
impl_file_refs = [".pi", "AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi", "scripts", "skills.index.json", "src/runtime/harness", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = ["/home/csheng/workspace/pi-extensions", "/home/csheng/.pi/agent/settings.json"]
+++
# Design

## Problem

`agent-skills` currently combines a provider-agnostic collection of semantic Skills with a Pi-specific executable harness under `integrations/pi/` and a Python artifact/ledger runtime under `src/runtime/harness/`. That arrangement makes the repositories appear separable while preserving a hidden product relationship: Pi consumes generated lifecycle data and runtime behavior authored by the Skill repository, and the Skill repository describes Pi as its maintained host.

The required boundary is stronger. `pi-extensions` and `agent-skills` are unrelated repositories with unrelated release and behavior lifecycles. The Pi harness owns its entire workflow state machine and every enforceable host boundary. It must work when none of the `agent-skills` Skills exist. Installed Skills are optional semantic workers discovered at runtime through Pi's native Skill surface; they do not implement a Pi contract and the harness does not know their repository, IDs, output format, or lifecycle. `agent-skills` contains portable semantic instructions that may be used by Pi, Codex CLI, Claude, or another compatible consumer without assuming any harness.

## Goals

- Create `/home/csheng/workspace/pi-extensions` as an independent Pi package repository and make it the sole owner of the generic agent harness.
- Give the Pi harness its own provider-level workflow lifecycle: capture work, obtain or normalize a plan, admit a task graph, execute ready tasks, evaluate whether review is required, optionally invoke review, bound repair, verify, and settle.
- Make the harness discover currently available Skills from Pi at runtime and use their public names and descriptions as optional semantic capabilities. Do not require known Skill IDs, repositories, metadata extensions, artifact schemas, or lifecycle routes.
- When a user invokes any planning or implementation Skill, let that Skill do semantic work while the harness independently extracts or normalizes tasks, validates and persists the DAG, gates mutation, tracks attempts and evidence, and drives the run to a terminal state.
- When the harness has an explicit review requirement, prefer an appropriate currently discovered review Skill whose description matches the review intent; otherwise run a built-in generic review turn. Treat either result as untrusted semantic evidence admitted only through typed harness tools.
- Treat formal design, planning, and implementation stages as explicit review reasons: each completed formal stage automatically receives one bounded implicit review child. Ordinary pass-through work that never enters those stages is not reviewed automatically, and a standalone user-invoked review remains an independent bounded operation.
- Remove Pi integration and executable harness behavior from `agent-skills`. Retain only provider-neutral Skills and repository-internal declarative truth needed to author, route, validate, and distribute those Skills.
- Keep one Pi extension for the current atomic harness. Add another extension in `pi-extensions` only when it is independently useful, installable, configurable, testable, and removable without sharing the harness's private transaction state.
- Prove complete independence: each repository builds, tests, installs, and operates without the other repository present, and neither repository's acceptance suite mentions or locates the other.

## Non-Goals

- No contract bundle, adapter protocol, generated projection, shared schema package, submodule, symlink, sibling lookup, configured cross-repository path, compatibility fixture, or joint release gate between `pi-extensions` and `agent-skills`.
- No hardcoded assumptions in the Pi harness about `coding`, `design-change`, `plan-change`, `implement-change`, `review-change`, any artifact filename, or any Skill repository layout.
- No requirement that third-party Skills change their frontmatter, emit a harness-specific document, call a harness tool, or know that the Pi extension exists.
- No heuristic Markdown parser treated as authoritative. Free-form Skill output may be evidence for an agent-driven normalization step, but only a typed graph accepted by the harness becomes executable state.
- No universal review gate. Small, low-risk work with sufficient verification may proceed directly to settlement when no explicit request, admitted task policy, configured risk rule, or observed change fact requires review.
- No promise that a semantic Skill can enforce host boundaries by itself. Without a host harness, a Skill guides the active agent and relies on that host's normal permissions and workflow behavior.
- No remote repository creation, publication, registry release, commit, push, or provider/model configuration change in this milestone.

## Decision Discovery

- `milestone_objective`: split one coupled repository surface into two unrelated products: a generic Pi-native agent harness and a portable semantic Skill collection.
- `non_goals`: all cross-repository protocols and paths, known Skill identities, Skill-required harness metadata, degraded DAG or review enforcement, speculative extension splitting, and remote release work.
- `unresolved_decisions`: none block planning. Public package identity and remote hosting remain deferred because the initial milestone is a local independent repository and cut-over.
- `shared_terms`: `harness lifecycle` means Pi-owned capture, normalize, approve, execute, assess, verify, and settle states; `semantic worker` means any currently discovered Skill optionally selected for one harness intent; `task graph` means typed executable state owned only by the Pi harness; `child dispatch` means a harness-initiated bounded Skill call, including conditional review, that cannot re-enter root workflow admission; `unrelated repositories` means no runtime, build, test, configuration, documentation, or release edge in either direction.
- `decision_status`: `ready_for_plan`; implementation remains blocked on this design's approval gate.

## Boundaries

Architecture decision `PI-EXT-002` supersedes both `PI-HARNESS-003` and the contract-bundle proposal in `PI-EXT-001`. It removes the semantic-kernel/provider-host product relationship entirely.

### D1: Zero Cross-Repository Interface

`pi-extensions` does not consume an `agent-skills` contract, inspect its checkout, recognize its public IDs, run its scripts, or test against its artifacts. `agent-skills` does not expose a Pi adapter, harness ABI, Pi-specific projection, settings example, package path, or host conformance promise. The repositories may happen to be installed on the same machine because Pi and other agents discover Skills independently, but that is ordinary ambient composition rather than an integration.

The only interfaces used by the Pi harness are Pi's public extension APIs, Pi's currently discovered command metadata, the model/tool protocol, the current workspace, and harness-owned state. The only interface exposed by `agent-skills` is the standard Skill surface plus its human- and agent-readable semantic content.

### D2: Harness-Owned Lifecycle And State

The Pi extension owns a generic lifecycle independent of any Skill collection:

```text
pass-through
    │
    ▼
capture ─► normalize ─► approval ─► execute ─► assess ─► verify ─► settle
                                      │           ▲          │
                                      │           └─ repair ─┘
                                      └──── blocked/authority ─────────► settle
```

Planning, implementation, diagnosis, and review Skills are bounded child calls made by these states; they are not additional top-level phases. A policy checkpoint may call a review worker and use its typed result while remaining in `normalize` or `assess`. This prevents a Skill's own suggested lifecycle from growing or reversing the host state machine.

The harness records semantic stage roles independently of Skill identity. A formal managed change normally progresses through design, planning, and implementation roles when the user selects those capabilities; each role completion adds a stage-owned implicit review child before the result is admitted. Formality is a persisted root-admission decision, not a property of a Skill. Authorized origins are an explicit harness role request, an approved typed graph with a root formal-role declaration, or an observable root selection of a discovered Skill whose current description resolves through a typed result to design, planning, or implementation intent. The description may resolve the already-selected root capability, but a Skill name, task size, output text, worker result, or child dispatch cannot assign formality. An explicit single-task path may record `formalRole = none`, and ordinary pass-through has no formal role. The same synthetic Skill can therefore be used once as a formal root worker and once as a non-formal child without changing its content.

Each admitted formal role receives a stable `stageInstanceId` derived from the run, role, role ordinal, and frozen admission digest before worker dispatch. Its implicit review reason is keyed by that ID and consumed exactly once across retry, replay, resume, fork, and compaction. A lightweight request that stays in ordinary pass-through or uses a non-formal single-task path does not inherit those review calls merely because the extension is installed.

The harness persists request identity, workspace root, authority provenance, source-message digests, selected semantic workers, normalized task graph, task and attempt state, touch sets, locks, evidence, review findings, repair budget, verification results, and terminal outcome through Pi session entries. The state schema, transitions, replay rules, and migration policy live only in `pi-extensions`.

The initial activation contract is `skill-aware`: pass-through is the default for prompts that have not entered a managed workflow, and ordinary Pi behavior, including ordinary mutation, is unchanged there. A managed workflow starts only through an explicit harness command, admission of a typed task graph, or observable root selection of a discovered Skill that resolves to a managed design, planning, or implementation intent. Extension-originated child markers take precedence over capability text and can never activate another root or create a formal stage. Once capture starts, no worker receives a mutation-capable profile until a task has been admitted. The tool gate intercepts a managed worker's mutation-capable tool call before execution and redirects it into capture rather than applying it speculatively. Semantic classification may start capture or normalization, but it can never grant mutation authority or bypass approval. Disabling the extension restores Pi's ordinary tool behavior and removes all managed activation. A future global-guard mode is outside this milestone and cannot be inferred merely because the package is installed.

### D3: Native Skill Discovery Without Skill Assumptions

At each semantic dispatch, the extension snapshots Pi's current commands and considers only entries whose source is `skill`. It uses the public command name and description; it does not inspect repository identity or require extra frontmatter. Explicit `/skill:<name>` input is observable before expansion. Model-driven native selection is observable when a read call targets the exact `sourceInfo.path` supplied by Pi for a discovered Skill; the path is used only as an opaque correlation token and is never walked or interpreted as a repository layout. Explicit user selection wins when compatible with the current harness intent. Otherwise a bounded read-only capability-resolution turn receives the current intent and discovered name/description pairs and must select exactly one candidate or `none` through a typed tool.

Harness intents are provider-owned roles such as planning, implementation, review, diagnosis, or verification. They are not inferred from a fixed Skill name. A description such as “use when the user wants a code review” can make that Skill a review candidate regardless of its name or repository. Ambiguous selection does not silently choose by lexical score: the harness asks the user when the choice materially affects behavior, or uses its built-in generic worker when the role has a safe fallback.

To invoke a selected Skill, the extension uses Pi's native `/skill:<name>` expansion. The bounded work brief is injected separately as a harness-owned context message keyed by an opaque run or task ID, so arbitrary repository text is not interpolated into the command. Extension-injected Skill calls carry source and dispatch markers to prevent recursive activation loops. Discovery is refreshed after Pi reload; an active attempt retains the exact selected name and description snapshot for audit and replay.

### D4: Plan Capture And Task Extraction

A planning Skill may return prose, a file reference, a checklist, a table, structured frontmatter, or another format. The harness treats all of it as an untrusted plan proposal, freezes the relevant response and explicitly referenced workspace artifacts by digest, and starts a normalization turn. The normalization agent receives the frozen proposal plus the harness task-graph schema and must call a typed `submit_task_graph` tool. The planning Skill itself does not need to know or call that tool.

If an implementation Skill is selected with no active graph, the harness does not let the initial invocation mutate first and reconstruct a plan afterward. It captures the user request and any read-only exploration as the proposal, normalizes a one-task or multi-task graph, obtains required approval, and then re-invokes the selected Skill as the bounded worker. When the request cannot be normalized safely without design or planning judgment, the harness may discover a planning Skill or use its generic planner before returning to the held implementation intent; this is a forward child call inside `capture`, not a reverse transition initiated by the implementation Skill.

The harness-owned graph contains stable task IDs, descriptions, dependencies, declared write and read scopes, resource locks, execution isolation, completion evidence, executable verification, conditional review policy and rationale, and recovery policy. A small change may normalize to one task; a larger plan may normalize to a DAG. Missing safety-critical fields remain unresolved rather than being guessed into authority.

Before approval, the harness deterministically rejects duplicate IDs, missing dependencies, cycles, unreachable tasks, invalid statuses, contradictory isolation or write scopes, unsafe paths, conflicting resource locks, invalid parallel groups, unbounded attempts, and tasks without completion or verification evidence. A separate semantic plan check compares the frozen proposal to the normalized graph for omitted, invented, or reordered work. Structural validity does not prove semantic completeness; both gates must pass before execution.

### D5: DAG Execution And Mutation Boundary

Only the harness advances task state or grants a mutation-capable worker profile. It computes ready tasks from the admitted graph, defaults to serial execution, and allows parallel work only when the graph explicitly declares a bounded group with disjoint writes, resource locks, and approved isolation. Every worker receives one immutable task slice and may operate only inside its declared workspace and touch set.

Managed tool gating is defined by observable Pi tool calls and a harness-owned capability registry, not by hoped-for side effects. Known read-only tools remain available during capture and review. Known path-bearing mutation tools such as edit and write are admitted only after task approval and are checked before execution against the workspace and touch set. Unknown or mixed-capability tools are classified as mutating by default. In particular, unrestricted shell execution is blocked before admission and remains denied during managed work unless the exact task has an approved isolated executor. An exact user decision may instead authorize one named uncontained operation, but that call is recorded as an explicit suspension of path-containment guarantees and cannot come from a reusable profile or Skill output. Command-string heuristics and post-effect diffs may provide additional evidence but never satisfy a pre-effect containment claim.

An implementation Skill selected by the user or capability resolver acts as a semantic worker for the current task. If no matching implementation Skill is available, the current Pi agent receives a built-in generic implementation brief. Neither path can mark a task accepted directly. Workers report a typed result containing changed paths, evidence, verification output, residual risks, and requested outcome. The harness compares observed operations and repository diff to the declared slice, rejects scope escape, records an attempt, and evaluates the review policy before choosing review or direct verification.

Tool interception, protected paths, external effects, destructive Git operations, credential access, commit, push, publish, deployment, and terminal-state write denial are owned by the extension. Semantic worker instructions can narrow behavior but cannot expand host authority.

### D6: Conditional Review And Non-Reentrant Child Dispatch

Review is a conditional child operation, not a top-level harness phase or universal transition. It occurs only when the harness has a recorded reason: completion of a root-admitted formal design, planning, or implementation stage; an explicit user request; an admitted task-graph requirement; a matching machine-local risk policy; or observed facts such as scope divergence, sensitive boundary changes, failed-then-repaired verification, or an uncertain terminal claim. A formal-stage reason is keyed by its stable `stageInstanceId`, and retry or replay cannot enqueue it twice. The decision, target, and reason are persisted. Absence of a reason continues the current lifecycle directly; task size, Skill identity, and worker output alone never force review.

When review is required, the harness builds a bounded brief for the actual target, such as a normalized graph, task diff, verification failure, or terminal claim, then queries current Pi Skill discovery for review candidates by description. If the user already selected a compatible review Skill, use it; otherwise the capability resolver selects one candidate or `none` without hardcoded IDs. A selected Skill runs through its native command under a read-only tool profile; if no suitable Skill exists, the harness uses a built-in generic review prompt.

If an active semantic worker requests or attempts a review child as part of its own guidance, the harness intercepts that child dispatch before invocation and records a `worker-requested-review` reason. The worker never runs review inline. When that reason has the same frozen target and acceptance boundary as the formal-stage reason, the harness coalesces them into the one dispatch keyed by `stageInstanceId`, and its typed result satisfies both reasons. A different target remains a distinct bounded reason or is rejected as scope expansion. This is a generic child-dispatch rule and does not depend on a known review Skill, ID, or repository.

Every harness-initiated Skill call is a child dispatch with an expected typed result and an explicit non-reentry marker. Input emitted by that dispatch cannot start capture, normalization, planning, implementation, or another review workflow even when the selected Skill's own instructions mention those phases. A review child can only submit review findings; an implementation child can only submit the current task result; a normalization child can only submit a graph. Requests from a child to reverse into an upstream phase become bounded result content or a typed `needs-input` outcome, never a new state-machine entry.

A root user invocation whose resolved intent is standalone review does not synthesize design, planning, or implementation prerequisites. It creates one bounded review target, dispatches a matching discovered review Skill or the generic reviewer, returns the result, and settles. This manual path is separate from the implicit review children attached to formal managed stages.

The reviewer can only submit typed candidate findings with severity, confidence, causal scope, evidence, and affected paths. A review Skill cannot mutate the workspace, accept its own findings, advance the DAG, or grant another attempt. The harness adjudicates causally in-scope findings, permits a bounded repair when policy allows, and runs focused verification. It repeats review only when the recorded review policy or an accepted finding requires re-review; otherwise a successful focused verification may settle the repaired task.

### D7: Authority And Non-Overridable Safety Floor

Use a repository-neutral `workflowHarness` settings namespace containing only Pi-harness configuration such as activation, authority profile, attempt limits, protected paths, and UI preferences. It contains no Skill paths, Skill IDs, contract roots, or repository names. Discovered Skills are ambient Pi resources and do not alter authority.

The extension owns a non-overridable default safety floor for workspace containment, protected VCS and settings state, credentials, destructive operations, external writes, privileged operations, mixed or unknown tool capabilities, and authority provenance. Reusable profiles may authorize only capabilities whose boundary the harness can enforce. When Pi's observable API cannot establish a promised pre-effect boundary, the harness must deny the capability, require an approved isolation provider, or stop for exact user authorization that explicitly records which containment guarantee is being suspended for one operation; it cannot silently downgrade the promise to heuristic command inspection. Skill content, Skill description, planning output, reviewer output, and task normalization can never grant authority.

### D8: One Extension With Behavior-Bearing Modules

The initial `pi-extensions` repository exposes one `workflow-harness` extension. Capture, normalization, task graph, tool policy, worker dispatch, review, repair, replay, and settlement share one transactional ledger and must fail atomically. Splitting them into separately loaded extensions would create ordering, versioning, and partial-state failure modes without an independently useful capability.

Internally, the extension separates Pi adapter, command discovery, capability resolver, plan normalizer, graph validator, scheduler, policy gate, worker dispatcher, review dispatcher, session store, telemetry, and UI modules. A module becomes a second extension only when it has standalone user value, its own settings and state lifecycle, public Pi or namespaced event-bus boundaries, independent tests, and removal semantics that do not migrate or reinterpret `workflow-harness` state.

### D9: Standalone Pi Repository Shape

```text
pi-extensions/
├── AGENTS.md
├── README.md
├── package.json
├── extensions/
│   └── workflow-harness/
│       ├── index.ts
│       └── lib/
├── tests/
│   ├── fixtures/skills/
│   └── fixtures/workspaces/
└── scripts/
```

The root is a normal Pi package and initially exposes exactly one extension entry. Fixture Skills use unrelated synthetic names and varied descriptions and output styles. The repository and its default tests contain no `agent-skills`, `coding`, sovereign-kernel Skill ID, cross-repository contract, or Python runtime dependency.

### D10: Agent Skills Becomes Semantic-Only

Remove `integrations/pi/`, `scripts/generate-pi-contracts.py`, `src/runtime/harness/`, runtime bundle inventories, generated Skill-local harness payloads, executable artifact/ledger CLIs, Pi probes, Pi settings, and documentation that makes Pi a maintained host. Remove host-specific lifecycle, authority, attempt, continuation, replay, and tool-policy claims from portable Skills.

Retain provider-neutral Skill content and repository-internal declarative contracts only where they support Skill authoring, semantic routing, artifact guidance, distribution, or generated-surface consistency. Those contracts are private truth for `agent-skills`; no external harness is expected to consume them. Static repository checks may verify parseability, reference closure, generated Skill drift, and documentation consistency, but the repository has no executable workflow controller, live artifact admission engine, or mutable task ledger.

Skills may still instruct an agent how to analyze, design, plan, implement, review, synchronize truth, or close work and may define useful semantic output formats. They must remain coherent when used directly by Codex CLI, Pi without `workflow-harness`, or another Agent Skills consumer. They cannot claim that any host will enforce their preferred sequence or artifact format.

### D11: Migration And Cut-Over

First create and validate `pi-extensions` using synthetic Skills and frozen behavioral parity cases derived from the current harness guarantees, rewritten in generic terms. Reimplement artifact normalization, DAG enforcement, review dispatch, and ledger behavior in the extension without importing old Python code at runtime. Temporary-load the package through Pi and prove it with the `agent-skills` checkout unavailable.

Then change `/home/csheng/.pi/agent/settings.json` only to replace the old package path and migrate the harness's own settings namespace. Do not add an `agent-skills` path or Skill configuration. Pi's existing independent Skill discovery remains untouched. Ensure one harness instance and run every post-cutover activation, pass-through, graph, review-required, review-skipped, fallback, resume, and extension-off probe while the old source remains recoverable. Only after all probes pass may the old Pi and Python harness surfaces be removed from `agent-skills` and that repository's semantic and generated Skill truth be refreshed.

### D12: Verification Boundary

`pi-extensions` acceptance covers ordinary read and write pass-through outside managed workflows; pre-expansion explicit Skill capture; exact Pi-reported Skill-path correlation for model-driven selection; managed-worker write and edit interception before side effects; fail-closed denial of shell and unknown tools before admission; isolated mixed-tool execution after admission; one-operation uncontained authority with explicit guarantee-suspension evidence; explicit and discovered worker selection; Skill reload; free-form plan capture; typed graph normalization; omissions and inventions checks; graph cycle, readiness, lock, touch-set, and parallel checks; mutation gates; task attempts; one implicit review after each root-admitted formal design, planning, and implementation stage; direct verification for non-formal work without another review reason; standalone manual review without synthesized upstream stages; generic review fallback; non-reentrant child dispatch; repair budget; verification; replay; resume; settlement; and extension-off behavior. Paired acceptance cases run the same synthetic worker in formal-root and non-formal-child contexts, retry/replay cases prove `stageInstanceId` review deduplication, and a worker-requested-review case proves that the semantic request coalesces with the formal reason into one dispatch. All tests use synthetic Skills and disposable repositories.

`agent-skills` acceptance covers source and generated Skill closure, provider-neutral descriptions and instructions, repository-internal semantic contracts, docs, and optional provider plugin metadata. It runs with Pi and `pi-extensions` unavailable and contains no live harness execution tests.

There is deliberately no cross-repository composition test. Each product tests only its own public boundary: `pi-extensions` tests against arbitrary synthetic Skills exposed through Pi, while `agent-skills` tests conformance to the Agent Skills surface and its own authored truth.

## Architecture Economics

- `demand_evidence`: current code and settings prove that Pi mechanics, Python enforcement, and semantic Skills are coupled; the user requires a Pi harness that can orchestrate arbitrary discovered Skills and a Skill collection usable by unrelated hosts.
- `scarce_resource`: behavioral ownership and review attention are constrained. A host cannot safely enforce a DAG or review gate when another repository owns part of its runtime truth.
- `status_quo`: retain the current adapter and generated lifecycle projection; rejected because both products remain one distributed system disguised as two repositories.
- `contract_bundle`: make `agent-skills` publish a host-consumed bundle; rejected because it preserves an intentional product protocol and makes Pi behavior depend on one Skill collection's declarations.
- `smallest_sufficient`: one generic Pi harness with its own lifecycle and typed graph, dynamically using discovered Skills only as optional semantic workers; selected because it satisfies full independence while retaining deterministic host enforcement.
- `structural_investment`: multiple Pi extensions with a shared orchestration SDK; deferred because current capabilities share one ledger and atomic transition boundary and have no standalone installation demand.
- `marginal_tradeoff`: agent-driven normalization and description-based capability resolution cost extra turns and cannot prove semantic correctness alone, so the harness pairs them with frozen inputs, typed tools, deterministic graph checks, conditional risk-based review, and explicit authority. This cost buys compatibility with arbitrary unchanged Skills without charging every small change for a review turn.
- `opportunity_cost`: the migration replaces recently completed provider-specific work and requires a new generic test corpus, but retaining any shared contract would continue coupling every future Skill and harness change.
- `owner_and_incentives`: `pi-extensions` owns runtime correctness, safety, state, and operational failures; each Skill author owns only semantic guidance; the Pi operator owns installed resources and authority settings. No Skill repository can weaken the harness to make its own workflow pass.
- `comparative_advantage`: Pi's extension API is the lowest-cost owner for commands, events, tools, session state, follow-ups, and discovery; Agent Skills are the lowest-cost portable unit for semantic expertise.
- `chosen_option`: `PI-EXT-002`, one independent generic `workflow-harness` extension using arbitrary Pi-discovered Skills as untrusted optional semantic workers.
- `upgrade_trigger`: split another extension only after standalone demand and independent state exist; add a richer Pi-native capability metadata convention only as a Pi ecosystem feature with multiple unrelated producers, never as a private link to `agent-skills`.
- `recovery_and_oracle`: prove the new package with synthetic Skills before settings cut-over, preserve a secret-safe settings backup, keep the old implementation recoverable until generic parity passes, and prove both repositories while the other is unavailable.

## Implementation Surface

- New repository: `/home/csheng/workspace/pi-extensions` with its own Git metadata, Pi package manifest, one `workflow-harness` extension, harness-owned lifecycle and graph schemas, dynamic Skill discovery and invocation, generic fallback workers, tests, probes, and documentation.
- Existing repository: remove all Pi and executable harness surfaces; retain and refresh only provider-neutral Skills, internal semantic contracts, generators, docs, and optional consumer manifests.
- Machine-local settings: replace only the old Pi package entry and harness-owned configuration in `/home/csheng/.pi/agent/settings.json`; do not add any Skill repository path or relationship.

## Validation

- Validate and review this version-4 design before planning.
- Build a parity matrix from existing route, artifact, ledger, authority, continuation, tool-policy, and review guarantees, then express each case against synthetic Skills and harness-owned lifecycle state.
- In `pi-extensions`, run formatting, type checks, unit and component tests, package validation, temporary Pi load, synthetic planning/implementation/review Skill probes, generic fallback probes, disposable-repository workflow and replay probes, and forbidden-token/path scans proving no Skill-collection dependency.
- In `agent-skills`, regenerate only repository-owned outputs, run its aggregate static and semantic checks, validate affected optional plugin metadata, run `git diff --check`, and scan maintained source and docs for Pi-harness or executable-runtime residue.
- Prove each repository from an isolated copy or with the other checkout unavailable. Do not add a joint acceptance lane.
- After cut-over, verify one global harness package, unchanged independent Pi Skill discovery, unchanged provider/model settings, ordinary extension-off Skill use, one low-risk synthetic workflow that skips review, one policy-triggered workflow that invokes a discovered review Skill, and one required-review workflow that uses the generic fallback.

## Recovery Policy

Use fix-forward before cut-over. If generic parity or standalone checks fail, leave global Pi settings unchanged and repair only `pi-extensions`. After cut-over, failure of any required startup or behavioral probe triggers the same recovery: disable the new package or restore only the previous package entry and harness settings from a secret-safe structural backup, then verify Pi startup, ordinary pass-through, and extension-off behavior before continuing diagnosis. Keep the old implementation recoverable until every cut-over probe passes; never delete it as part of recovery. Do not restore a cross-repository adapter, add a shared contract, modify Skill discovery to force composition, delete either repository, publish, commit, or push to force convergence.

## Approval

Approved by the user on 2026-08-28 with the clarified review policy: formal design, planning, and implementation stages each imply one bounded review child; ordinary non-formal work does not; standalone review remains an independent manual path. The approved design may advance to `plan-change` after focused validation and design-review verification of this amendment.
