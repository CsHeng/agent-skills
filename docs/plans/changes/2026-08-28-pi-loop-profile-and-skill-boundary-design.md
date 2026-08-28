+++
artifact_kind = "design"
contract_version = 4
decision_id = "PI-LOOP-001"
approval_status = "approved"
decision_status = "approved_for_implementation"
review_verdict = "needs-fixes"
review_resolution = "resolved"
truth_impact = "high"
truth_sync_required = true
supersedes = ["PI-EXT-002:managed-workflow-runtime"]

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts", "docs/architecture", "scripts", "skills.index.json", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = ["/Users/csheng/workspace/playground/pi-extensions/AGENTS.md", "/Users/csheng/workspace/playground/pi-extensions/README.md", "/Users/csheng/workspace/playground/pi-extensions/docs/architecture", "/Users/csheng/workspace/playground/pi-extensions/extensions", "/Users/csheng/workspace/playground/pi-extensions/package.json", "/Users/csheng/workspace/playground/pi-extensions/scripts", "/Users/csheng/workspace/playground/pi-extensions/tests"]
+++
# Pi Loop Profile And Semantic Skill Boundary Design

## Decision State

- `decision_id`: `PI-LOOP-001`
- `design_depth`: `design-full`; the change removes a persisted workflow authority and reassigns ownership across two independently installed repositories.
- `decision_status`: `approved_for_implementation`; the one bounded design review is adjudicated, its accepted recovery-order finding is repaired, and the user approved the design together with its linked plan.
- `approval_status`: `approved` by the user's explicit 2026-08-28 `approve both and $coding:implement-change` instruction.
- `truth_impact`: `high` in both repositories because their current stable architecture and contracts assign lifecycle authority differently.

## Objective

Restore Pi as the coding agent rather than making it a protocol client for a second workflow engine. Keep reusable coding Skills semantic and provider-neutral. Limit Pi extensions to small, explicit changes to the existing Pi loop, beginning with a user-selected read-only planning profile.

The outcome must remove the failure-prone managed workflow while preserving the useful repository split established by `PI-EXT-002`: `market-csheng` owns portable Skills and `pi-extensions` owns Pi-specific extension code. No runtime, build, test, release, or configuration dependency may cross that repository boundary.

## Current Truth And Problem

Pi already supplies the agent loop, model turn, session, and base tool execution. The installed `workflow-harness` extension adds a second lifecycle above that loop: activation, frozen proposals, normalization, task graphs, stages, reviews, repair, replay, and settlement. Its custom `workflow_*` tools turn the model into a client of that protocol instead of allowing the active coding agent to understand the request, select semantic guidance, act, observe, and continue.

The two supplied Pi sessions demonstrate architectural failure rather than isolated validation defects:

- Session `01a04748-b0f9-7173-a25c-32584bea776d` repeatedly failed activation with `artifact is not a regular file` and stale Skill resolution. It issued eight activation calls but reached only one stage completion and one settlement.
- Session `01a04751-8262-7c36-b267-cada4070c107` failed activation provenance and stale-resolution checks, then rejected a submitted graph because normalization was not bound to the frozen proposal. Mutation was also denied for lack of a harness-admitted task attempt.
- `workflow_complete_stage` and `workflow_settle` terminate the current agent turn. The continuation handler covers selected child or review states, so an otherwise ordinary run can stop at a protocol boundary with unfinished user work.
- The extension has thousands of lines of task-specific state and validation, while its tests primarily exercise adapters and tool implementations. That evidence can prove transition code but cannot prove that the normal model loop reliably finishes user work.

The same pattern remains semantically encoded in `market-csheng`: lifecycle-owner metadata, workflow modes, fixed phase routes, automatic review requirements, approved-plan prerequisites, and a fixed workflow diagram. Although those contracts no longer execute a runtime, they still teach agents to reproduce the removed controller in prompt space.

## Boundary Model

Three concepts must remain distinct:

| Concept | State it may own | Legitimate examples | Owner |
| --- | --- | --- | --- |
| Agent loop | messages, tool calls, tool results, continuation, final answer | Pi's native read/act/observe loop | Pi core |
| Capability profile | a small tool/prompt/UI projection on that same loop | explicit plan/default profile | Pi extension |
| Workflow run | proposal identity, graph, stages, review/repair ledger, settlement | an explicit future orchestrator, if justified | separate product capability, not this milestone |

A mode is legitimate only when it changes the capabilities or instructions of the same loop. Once it owns task identity, graph admission, lifecycle transitions, review settlement, or terminal judgment, it is an orchestrator and must be named, entered, tested, and governed as such. Calling that state `managed mode` does not make it a mode.

## Decision

### D1: Preserve The Repository Split, Remove The Managed Workflow

`PI-EXT-002` remains authoritative for repository independence and is superseded only where it chose a Pi-owned managed workflow lifecycle. `pi-extensions` must remove the current `workflow-harness` package surface and its activation, proposal, graph, stage, review, repair, replay, settlement, dispatch, and tool-policy machinery.

The replacement is not a smaller workflow engine. It is one feature-specific `plan-mode` extension that changes the active tools, adds a short planning instruction, shows its active state, and restores the prior tool set on exit. It registers no model-facing workflow tools and owns no semantic work state.

### D2: Plan Mode Is An Explicit Capability Profile

The initial extension provides exactly two user-observable profiles:

- `default`: ordinary Pi behavior with the exact tool set that was active before plan mode.
- `plan`: the same Pi loop with Pi's exact built-in read-only tool set enabled, a short read-only planning instruction, and a visible status marker.

Entry and exit are explicit user actions. `/plan` enters the profile and `/default` exits it; an optional startup `--plan` flag may enter the same profile. Skill selection, prompt classification, plan-shaped prose, and model output must never enter or exit the profile automatically.

For the supported Pi version, the plan tool set is exactly `read`, `grep`, `find`, and `ls`, which Pi documents as built-in read-only tools. The profile deliberately excludes `bash`, `edit`, `write`, unknown tools, custom tools, and mixed-capability tools. It does not parse shell commands, predict side effects, or create a general permission engine. If a future Pi version does not expose the four declared tools, entry fails closed with a visible diagnostic instead of silently retaining a mutation-capable fallback.

On first entry, the extension records the exact prior active-tool list. Re-entering is idempotent and must not overwrite that snapshot. Exit restores that exact list rather than constructing a guessed default. Session persistence contains only the active profile and the saved tool list so a resumed session cannot silently regain mutation tools. It contains no request, proposal, task, stage, review, repair, attempt, or completion data.

The profile may inject one compact instruction before agent start: explore with available read-only tools, surface uncertainty, and return analysis or a plan without mutation. It must not prescribe artifact schemas, mandatory review, execution handoff, todo extraction, completion markers, or an automatic transition into implementation. It must not use `agent_end` to continue, terminate, or change profile.

### D3: The Active Coding Agent Owns Semantic Work

The active coding agent owns request interpretation, Skill selection, ordering, clarification, implementation decisions, verification depth, optional review, finding adjudication, repair, and the final response. These decisions remain part of the normal agent loop; they are not serialized into a host workflow graph.

`market-csheng` Skills provide reusable methods and constraints. A directly named or confidently matched Skill may run without a session router. An ambiguous multi-stage request may use `use-coding-skills`, but that router only selects one primary semantic response owner and optional overlays. It cannot manufacture phases, authority, review obligations, or host modes.

Formal artifacts remain useful when the user or task needs them, but their existence does not imply a universal lifecycle. `implement-change` may accept either an explicit bounded mutation request or an approved plan. `sync-truth`, `organize-docs`, and `close-change` apply only when their semantic trigger and authority match; they do not require a synthetic upstream plan merely to become callable.

A specialized delegated-mutation overlay such as `implement-change-via-herdr` may still require an approved bounded plan because the delegate must receive frozen scope rather than choose it. That local safety precondition does not make approved planning universal or turn the overlay into a lifecycle owner.

### D4: Review And Gates Are Conditional Decisions

Review is not an automatic phase or a fixed per-invocation child. The active coding agent invokes a bounded review when at least one of these conditions holds:

- the user explicitly requests review;
- a repository-owned or approved scope contract requires it;
- the risk, uncertainty, or evidence gap makes an independent read-only evaluation materially useful.

Review remains causality-bound and read-only, and the active coding agent adjudicates candidate findings. However, design, plan, and implementation Skills must not always invoke `review-change`, encode `reviews_per_invocation = 1`, or make review metadata a required artifact field when no review occurred. This design and its linked plan still receive one review each because the explicitly invoked current Skill contracts require it; that is migration evidence, not the target steady-state rule.

Human approval remains necessary only for decisions or actions that actually require it: unresolved product choice, destructive or external mutation, live cutover, commit, publication, deployment, or another authority boundary. Writing an artifact, completing a semantic phase, or selecting a Skill does not itself create a human gate.

### D5: Static Skill Metadata Must Not Resemble Runtime Control

Remove `contracts/lifecycle.toml`, `contracts/workflow-modes.toml`, lifecycle-owner flags, fixed phase routes, implicit review policy, and approved-plan prerequisites that encode a universal controller. Keep repository-owned contracts for Skill identity, generated distribution, semantic trigger cases, reference closure, and provider discovery projection.

`activation_mode` in `contracts/skills.toml` remains unchanged in this milestone. It is static distribution metadata used to project discovery/invocation availability, not a Pi runtime mode. Renaming it would create churn without correcting the boundary under discussion; stable docs and tests must make the distinction explicit.

## Ownership After The Change

| Concern | Owner | Explicitly not owned |
| --- | --- | --- |
| Turn continuation, tool execution, session lifecycle | Pi core | Skills and `plan-mode` |
| Plan/default tool projection, status, minimal profile persistence | `pi-extensions/plan-mode` | semantic task lifecycle |
| Request meaning, sequencing, evidence judgment, final answer | active coding agent | extension state machine |
| Reusable design, planning, implementation, review, policy, and testing guidance | `market-csheng` Skills | provider enforcement and scheduling |
| Approval and authority expansion | user | model output, Skill prose, or extension inference |

## Alternatives And Decision Economics

### A: Repair The Existing Managed Workflow

Rejected. It would fix stale resolution, directory normalization, and proposal binding while preserving the second controller that caused those errors. Every new task shape would continue to spend model context on protocol state and human attention on lifecycle review instead of user work.

### B: Keep Managed Mode But Make It Optional

Rejected for this milestone. Optional activation reduces blast radius but does not give the feature a coherent product boundary. A graph/review/replay/settlement engine remains an orchestrator even when entered explicitly, and current demand has not justified maintaining it.

### C: Build A Generic Profile Or Permission Framework

Deferred. The observed requirement is one plan profile. A framework would introduce configuration, policy composition, compatibility, and migration surfaces before a second stable profile exists.

### D: Thin Explicit Plan Profile Plus Semantic Skills

Selected. It uses Pi's existing loop and official extension mechanisms, makes the user-visible behavioral change reversible, removes protocol traffic from model context, and leaves review bandwidth for risk-bearing work. The scarce resources are model attention, human review attention, and confidence in completion; this option consumes the least of each while satisfying the observed need.

The opportunity cost of continuing the current harness is delayed coding usefulness: engineering effort goes to digests, provenance, graphs, review bookkeeping, replay, and settlement rather than better semantic guidance or actual task completion.

## Scope

### `pi-extensions`

- Add a thin `extensions/plan-mode/` implementation using Pi's public extension API.
- Replace the package export of `workflow-harness` with `plan-mode` only after the new profile passes a temporary-load probe, while retaining the old source as the exact rollback target.
- Run the installed-package probe against that export, restore the prior export if it fails, and remove the managed workflow source only after the installed probe passes.
- Remove workflow-specific tests, workflow probes, and dependencies that become unused after the successful installed cutover.
- Rewrite stable repository truth around loop-profile ownership and package independence.
- Retain focused tests for profile entry, read-only projection, exact restoration, resume behavior, and absence of workflow machinery.

### `market-csheng`

- Remove universal lifecycle/mode/gate contracts and simplify routing to semantic selection and composition.
- Remove universal mandatory-review and approved-plan requirements from authored Skills while retaining conditional review guidance and any narrowly justified frozen-scope precondition for explicit delegated mutation.
- Update validators, generators, tests, stable docs, and diagrams to assert the semantic-only boundary.
- Regenerate the tracked root-flat Skill payload and indexes from authored source.

## Non-Goals

- No generic orchestrator, task graph, child-agent scheduler, autopilot, review ledger, replay, settlement, or workflow resumption.
- No shell allowlist, command parser, path-containment policy, or generic permission system inside plan mode.
- No automatic execution after planning and no plan todo extraction or completion markers.
- No change to Pi core, model selection, provider configuration, user settings, Skill installation, or live symlink topology.
- No change to the 40 public Skill IDs or their provider-neutral distribution surface.
- No plugin version bump, commit, push, publication, deployment, or deletion of inert historical stage artifacts.

## Future Upgrade Triggers

- Consider a generic permission-profile extension only after at least two independently useful profiles need the same mechanism and Pi core does not already own it.
- Consider bounded continuation assistance only if ordinary Pi runs still terminate prematurely after every harness `terminate` and settlement prompt has been removed, with reproducible session evidence showing a Pi-loop rather than task-specific failure.
- Consider an explicit `/orchestrate` product only after repeated real work requires dependency scheduling, isolated workers, resource locks, or durable restart/resume. It must be separately named, explicitly entered, removable, and independent of Skill selection.

These triggers are observations, not reserved implementation scope. Meeting one requires a new design decision.

## Acceptance Evidence

The design is satisfied only when implementation evidence proves all of the following:

- A temporary-loaded plan extension can enter plan profile, expose exactly `read`, `grep`, `find`, and `ls`, visibly report that profile, resume safely, and restore the exact previous tools on explicit exit.
- The installed package exposes no `workflow_*` tool or managed-workflow command and contains no runtime request, proposal, graph, stage, review, repair, replay, or settlement state.
- Plan profile never enables through Skill selection or model output, never calls `terminate`, and never uses `agent_end` to transition or continue work.
- Default profile and disabling the extension preserve ordinary Pi behavior.
- `market-csheng` contains no maintained universal lifecycle, workflow-mode, implicit-review, or approved-plan gate contract; its generated Skills match authored semantic source.
- Both repositories pass their own focused and aggregate checks without locating, importing, or testing the other repository.
- A regression characterization covers the three observed failure classes: directory/stale activation, proposal-binding rejection, and premature protocol termination. Success means those code paths no longer exist, not that new retries mask them.

Exact model prose is not an oracle. Component tests, negative capability checks, repository-static contract checks, and temporary/installed Pi probes own acceptance.

## Truth Impact, Authority, And Recovery

Stable truth changes in both repositories. In `market-csheng`, `AGENTS.md`, `README.md`, maintained architecture docs, routing contracts, Skill source, diagrams, generated payload, and related tests must converge. In `pi-extensions`, package metadata, `AGENTS.md`, `README.md`, maintained architecture, extension source, tests, and probes must converge.

Default recovery is fix-forward within the failing repository. The risky action is the live package export cutover in `pi-extensions`. Its order is fixed: first pass the new extension by explicit temporary load; then switch only the package export while retaining the old harness source; then run the installed-package probe; and only after that probe passes may implementation delete the old source. If the installed probe fails, restore only the previous export to the still-present old source, preserve the new source and failing evidence, and stop for a plan-level decision rather than rebuilding managed state. After the installed probe passes and old source is removed, subsequent failures are fixed forward in `plan-mode`; rollback to the removed workflow is no longer an authorized ordinary repair.

This design grants no implementation, deletion, user-settings, installation, commit, push, publication, or deployment authority. A later approval of the linked plan may authorize repository-local additions, edits, and removal of the obsolete managed workflow within its exact touch set. The live package-export cutover must be named in that approval; consumer settings remain out of scope.

## Design Review

- `review_scope`: one direct, read-only boundary review of this artifact against the cited current repository/session evidence, the current `workflow-harness` package surface, the current semantic Skill contracts, and Pi's installed plan-mode example. The review excluded implementation details, unrelated defects, and future orchestrator design.
- `review_verdict`: `needs-fixes` with one high-confidence candidate. The original cutover text allowed the old workflow source to be removed before the installed-package probe, while recovery depended on that source as the prior export target.
- `adjudication`: accepted and repaired in scope. The design now fixes the order as temporary-load proof, export-only cutover with old source retained, installed-package proof, then old-source removal. A focused recheck confirms that the rollback target exists for the only rollback window; no second review was started and no material design finding remains.

## Approval

The user approved this design together with its linked plan on 2026-08-28 and explicitly invoked `implement-change`. Implementation is authorized only within that plan's declared repositories, tasks, cutover, removal, verification, and recovery boundaries.
