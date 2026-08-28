+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-27-pi-harness-offload-design.md"
design_sha256 = "d0c18217cde0c7b90e3d7df8c12d1642289e4b9c312734f546b1f0cf67a02581"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["AGENTS.md", "README.md", "docs/architecture/workflow-orchestration.md", "docs/architecture/install-surface.md", "docs/architecture/invocation-contract.md"]
default_runtime_model_policy = "inherit-main"
parallel_execution_approved = false

[scope]
impl_file_refs = [".pi/settings.json", "AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi", "scripts", "src/skills", "skills"]
test_file_refs = ["integrations/pi/tests", "tests"]
external_impl_file_refs = ["/home/csheng/.pi/agent/settings.json"]

[[tasks]]
task_id = "PIN-100"
depends_on = []
verification_commands = ["python3 scripts/generate-pi-contracts.py --check", "node --experimental-strip-types --test integrations/pi/tests/contracts.test.ts", "python3 -m pytest tests/test_skill_routing_contracts.py tests/test_check_orchestration.py -q", "git diff --check -- contracts scripts/generate-pi-contracts.py scripts/check.sh integrations/pi/generated tests/test_check_orchestration.py"]
scope_slice = "Project the minimum canonical lifecycle and routing facts needed by a Pi host adapter: semantic owners, legal handoffs, evaluator roles, modes, authority requirements, and terminal outcomes. Keep phase goals, engineering criteria, prompt prose, scheduling policy, and provider identity outside the projection."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["semantic-routing-contract", "pi-contract-projection"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The generated Pi projection is derived from canonical contracts and routing truth rather than a handwritten extension table.", "Every permitted owner-to-owner and review-evaluator handoff required by the semantic kernel is represented with an explicit terminal or continuation meaning.", "Unknown owners, stale contract versions, invalid evaluator roles, and incompatible approval evidence fail deterministically.", "The projection contains no copied phase goal, user-facing workflow command, provider name, model ID, or prompt-specific engineering checklist."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts/lifecycle.toml", "contracts/workflow-modes.toml", "scripts/generate-pi-contracts.py", "scripts/check.sh", "src/skills/session/use-coding-skills/references/routing.toml", "integrations/pi/generated/lifecycle-contracts.json"]
test_file_refs = ["integrations/pi/tests/contracts.test.ts", "tests/test_skill_routing_contracts.py", "tests/test_check_orchestration.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PIN-200"
depends_on = ["PIN-100"]
verification_commands = ["node --experimental-strip-types --test integrations/pi/tests/session-state.test.ts integrations/pi/tests/task-ledger.test.ts integrations/pi/tests/transition-runtime.test.ts integrations/pi/tests/artifact-bridge.test.ts", "git diff --check -- integrations/pi/extensions integrations/pi/tests"]
scope_slice = "Build the pure mechanical core behind explicit module boundaries: versioned active-branch session state, approved-plan task projection, dependency and attempt accounting, generated-contract transition validation, and deterministic artifact-validator invocation. Migrate reusable prototype code without binding Pi events yet."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["pi-session-state-schema", "pi-task-ledger-schema", "pi-transition-runtime", "pi-artifact-bridge"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Session state records request identity, terminal intent, semantic owner and role, authority source, artifact digests, task progress, attempts, accepted findings, pending handoff, tool profile, and terminal outcome with one versioned schema.", "Replay reconstructs only the active Pi branch and handles resume, fork, retry, compaction, malformed entries, and stale pending handoffs deterministically.", "The task ledger imports an approved plan topology without changing task IDs, dependencies, touch sets, locks, or oracles, and it admits only ready work.", "The transition runtime enforces generated legal routes, terminal intent, approval evidence, and one bounded same-slice repair without embedding semantic phase prompts.", "Python remains an out-of-process durable artifact compatibility boundary and cannot poll, schedule, or advance the Pi session loop."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["integrations/pi/extensions/csheng-workflow", "integrations/pi/extensions/coding-harness"]
test_file_refs = ["integrations/pi/tests/session-state.test.ts", "integrations/pi/tests/task-ledger.test.ts", "integrations/pi/tests/transition-runtime.test.ts", "integrations/pi/tests/artifact-bridge.test.ts"]
external_impl_file_refs = []

[[tasks]]
task_id = "PIN-300"
depends_on = ["PIN-200"]
verification_commands = ["node --experimental-strip-types --test integrations/pi/tests/skill-bridge.test.ts integrations/pi/tests/authority-profile.test.ts integrations/pi/tests/authority.test.ts integrations/pi/tests/tool-policy.test.ts integrations/pi/tests/extension-boundary.test.ts integrations/pi/tests/continuation.test.ts", "git diff --check -- integrations/pi/extensions integrations/pi/package.json integrations/pi/tests"]
scope_slice = "Bind the mechanical core to Pi's public extension lifecycle. Observe explicit Skill input, support natural owner binding without lexical routing, parse the versioned settings-backed host authority profile, record terminal intent and authority source, gate mutation before binding, translate validated semantic handoffs into native follow-ups, and settle only after queued work and retries drain."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["pi-public-event-binding", "pi-skill-bridge", "pi-tool-gate", "pi-continuation-runtime"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Natural Pi requests and native `/skill:<name>` commands enter the harness without a required runner command, mode argument, startup flag, or auto marker.", "Natural-language requests are bound by Pi-native Skill selection or an explicit generic host binding protocol, never by extension-owned keyword classification.", "The absent authority profile selects phase-gated behavior, the exact versioned `local-validation` profile permits bounded repository-local continuation, and malformed or unknown profile data fails closed without reading provider/model fields.", "A `design-change` completion may request `review-change` with role `review-design`; the adapter validates it and schedules the native follow-up while a design-only terminal intent stops after the reviewed design.", "Mutation fails closed before owner and authority binding, then derives active tools and preflight policy from the current phase, approved touch set, and protected-path rules.", "`agent_end` may stage a validated continuation, `agent_settled` alone records final completion, and replay cannot double-schedule a follow-up.", "The registered extension entrypoint only wires behavior-bearing modules and contains no `csheng-run`, `csheng-mode`, `csheng-auto`, fixed phase sequence, or phase-goal function."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["integrations/pi/extensions/coding-harness", "integrations/pi/package.json"]
test_file_refs = ["integrations/pi/tests/skill-bridge.test.ts", "integrations/pi/tests/authority-profile.test.ts", "integrations/pi/tests/authority.test.ts", "integrations/pi/tests/tool-policy.test.ts", "integrations/pi/tests/extension-boundary.test.ts", "integrations/pi/tests/continuation.test.ts"]
external_impl_file_refs = []

[[tasks]]
task_id = "PIN-400"
depends_on = ["PIN-300"]
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 -m pytest tests/test_skill_workflow_contracts.py tests/test_skill_routing_contracts.py tests/test_runtime_distribution_contracts.py tests/test_command_retirement_contracts.py tests/test_implement_change_via_herdr_contracts.py -q", "python3 scripts/check-contracts.py", "python3 scripts/check-install-surface.py", "git diff --check -- contracts scripts/check-contracts.py scripts/check-install-surface.py scripts/skill_distribution.py src/skills skills"]
scope_slice = "Thin the seven semantic-kernel Skills and their installed routing surface. Retain phase meaning, durable evidence, review ownership, recovery judgment, and textual Skill-to-Skill composition; remove host-loop state, exact ledger mechanics, actor scheduling, retry machinery, provider behavior, and Skill-local lifecycle runtime assumptions, then regenerate the 40-Skill payload."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["semantic-kernel-skills", "skill-routing-contract", "generated-skill-payload"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The seven top-level Skills remain coherent when the Pi extension is disabled and describe their semantic next owner or evaluator role in provider-neutral language.", "No Skill instructs the model to drive Pi tools, call an extension command, restore Pi state, schedule physical actors, or execute a Skill-local harness script.", "Durable artifact and evidence meaning remains owned by the appropriate Skill or canonical contract while live state, attempts, scheduling, and replay are absent from Skill prose.", "All 40 public IDs, activation metadata, standalone reference closure, and root-flat generation checks remain intact."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts/skills.toml", "contracts/runtime-bundles.toml", "scripts/check-contracts.py", "scripts/check-install-surface.py", "scripts/skill_distribution.py", "src/skills", "skills"]
test_file_refs = ["tests/test_skill_workflow_contracts.py", "tests/test_skill_routing_contracts.py", "tests/test_runtime_distribution_contracts.py", "tests/test_command_retirement_contracts.py", "tests/test_implement_change_via_herdr_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PIN-500"
depends_on = ["PIN-300", "PIN-400"]
verification_commands = ["npm --prefix integrations/pi test", "bash -n integrations/pi/scripts/run-native-discovery-probe.sh integrations/pi/scripts/run-native-workflow-probe.sh", "pi --version", "pi list --no-approve", "bash integrations/pi/scripts/run-native-discovery-probe.sh", "git diff --check -- .pi integrations/pi"]
scope_slice = "Prove the native adapter with temporary extension loading, then register the local Pi package once at user level, set the versioned `codingHarness.authorityProfile` to `local-validation`, retire the project-local duplicate load, and probe discovery plus bounded workflows from a disposable Git repository outside this checkout. Preserve every pre-existing global provider and model setting structurally without interpreting or emitting credential values."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["pi-package-install", "pi-global-settings", "pi-live-probe", "generated-skill-read"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Temporary-load tests pass before any user-level Pi setting changes.", "Pi user-level settings contain exactly one local package registration plus a versioned `codingHarness.authorityProfile = local-validation`, project `.pi/settings.json` does not load the same extension, and a secret-safe structural digest proves every pre-existing setting outside `packages` and `codingHarness` is unchanged.", "Each of the 40 global child symlinks resolves to this checkout's matching `skills/<public-id>` directory, no second configured Skill root exposes the same IDs, and a disposable repository outside this checkout loads exactly those 40 unique Skill commands plus one adapter instance without depending on project settings or this repository's AGENTS file.", "The disposable repository can inspect adapter status, enter through natural language or `/skill:<name>`, and observe the semantic review handoff under the recorded local-validation authority without invoking a `csheng-run` command or passing an auto flag.", "Probes redact secrets, use bounded repository-local mutations only, leave no tracked fixture outside the approved integration surface, and do not commit or push."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi/settings.json", "integrations/pi/package.json", "integrations/pi/README.md", "integrations/pi/scripts"]
test_file_refs = ["integrations/pi/tests/settings.test.ts", "integrations/pi/tests/package.test.ts", "integrations/pi/tests/authority-profile.test.ts", "integrations/pi/tests/native-entry.test.ts"]
external_impl_file_refs = ["/home/csheng/.pi/agent/settings.json"]

[[tasks]]
task_id = "PIN-600"
depends_on = ["PIN-500"]
verification_commands = ["python3 scripts/generate-pi-contracts.py", "python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/generate-workflow-diagrams.py", "bash scripts/check.sh", "bash integrations/pi/scripts/run-native-workflow-probe.sh", "git diff --check"]
scope_slice = "Synchronize stable project truth to PI-HARNESS-003, regenerate every owned projection and diagram, run aggregate acceptance, and collect converged live evidence for explicit design-only review, natural bounded implementation, resume, settlement, and extension-off semantic portability."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["stable-workflow-truth", "workflow-diagrams", "generated-skill-payload", "repository-acceptance", "pi-live-probe"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["AGENTS, README, stable architecture documents, diagrams, Pi integration guidance, and the Pi handoff consistently describe the native host adapter and no longer prescribe the command runner.", "The aggregate repository check, all Pi integration tests, generated-surface checks, Markdown rules, and `git diff --check` pass from one converged tree.", "An explicit design request reaches `review-change(role=review-design)` and settles at the design-only terminal boundary without human intervention inside the preauthorized run.", "A natural bounded implementation request follows the approved semantic lifecycle through verification, review, required truth sync, and close without a special workflow entry command.", "Resume evidence proves no duplicate task or handoff, and extension-off evidence proves the same Skills still identify their semantic owner and next review handoff without a Skill-local runtime.", "A bounded implementation review accepts no unresolved host-authority, state-replay, task-ledger, tool-gate, continuation, global-discovery, secret-handling, or semantic-drift finding; no commit, push, publish, or release occurs."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi/README.md"]
test_file_refs = ["integrations/pi/tests", "tests"]
external_impl_file_refs = []
+++
# Plan

## Implementation

Execute `PIN-100` through `PIN-600` serially after the joint design/plan approval. `PIN-100` establishes the canonical host projection, `PIN-200` builds pure mechanical state and transitions, `PIN-300` binds them to native Pi events and Skill handoffs, `PIN-400` thins the portable Skills, `PIN-500` proves and globally installs exactly one adapter instance, and `PIN-600` converges stable truth plus end-to-end evidence. Every task uses the controller checkout, and later slices consume contracts or runtime surfaces owned by earlier slices; no parallel batch or delegated writer is authorized.

Architecture decision reference: `PI-HARNESS-003`. This plan replaces the command-runner portion of `PI-HARNESS-002`; it does not preserve `/csheng-run` as a migration entry or compatibility controller. Reversible increments are canonical projection, pure mechanical core, Pi event binding, Skill thinning, temporary-load proof, user-level package plus namespaced authority-profile registration, and final truth convergence. The global setting is not touched until the same package has passed deterministic and temporary-load checks.

TypeScript is already fixed for the persisted Pi extension boundary because Pi's public extension API and session/event types are TypeScript-native; no language decision is reopened. Python remains fixed only for the existing deterministic artifact compatibility boundary. Small Bash probes may orchestrate documented Pi, Git, and `jq` commands but own no state machine, semantic route, retry loop, or persistent schema.

The linked design and this plan were jointly approved by the user on 2026-08-27 together with an explicit `implement-change` invocation. The approved continuous execution range is `PIN-100..PIN-600`.

## Work Package Readiness

- `milestone_objective`: replace the explicit Pi sidecar runner with one globally installed modular host adapter that adds native state, ledger, gates, progress, replay, and continuation to normal natural-language and `/skill:<name>` workflows while leaving semantic authority in portable Skills and canonical contracts and sourcing unattended local validation from one explicit settings-backed profile.
- `non_goals`: cross-host orchestration, multi-agent scheduling, parallel writers, provider/model routing, regulated or external mutation, deployment, release, commit, push, publication, Pi-core patches, and removal of the central artifact compatibility validator.
- `future_phase`: extract a provider-neutral mechanical SDK only after a second maintained host demonstrates the same runtime need; design a separate orchestrator only after approved multi-actor or cross-provider execution becomes current demand.
- `decision_status`: `approved_for_implementation`; no unresolved design choice blocks execution.
- `oracle_strategy`: model/state-transition tests for pure mechanics, generated-contract parity and negative tests, fake-Pi component tests for events and tools, temporary extension-load tests, global package/discovery RPC probes, bounded live synthetic workflows, resume/settlement probes, extension-off semantic fallback, and aggregate repository acceptance.
- `acceptance_oracles`: every task's exact verification commands and `done_when` predicates, followed by one causality-bounded implementation review with at most one focused same-slice repair per task.
- `execution_continuity`: `confirmed`; the user's joint approval authorizes the declared serial range and exact external settings surface.
- `max_review_batches`: `2`, comprising one direct boundary review of these design/plan artifacts before human approval and one implementation review over the converged task slices.
- `subagent_ready`: `false`; overlapping contracts, generated surfaces, host state schemas, and a single user-level Pi setting make a serial main-agent execution unit the smallest safe topology.

## Execution Continuity

- `execution_mode`: `confirmed_continuous`.
- `confirmation_clearance`: `C1` is `approved` and covers the exact approved design digest plus this plan, tasks `PIN-100..PIN-600`, repository-local mutation inside declared refs, bounded disposable-repository probes, and the exact user-level Pi settings file.
- `expected_continuous_range`: after `C1`, `E1 = PIN-100..PIN-600`; task boundaries are progress markers rather than implicit human gates, while terminal intent and any portable phase approval still follow the approved host authority recorded for the live probe.
- `runtime_contingencies`: `X1` stops if the canonical projection cannot express a required handoff without redefining Skill semantics; `X2` stops if Pi's public APIs cannot prove unique global loading or active-branch replay; `X3` stops if natural owner binding cannot fail closed before mutation without lexical routing; `X4` stops on credential exposure, provider-setting drift, mutation outside declared scope, semantic-route drift, repeated repair, or work beyond terminal intent.
- `planned_stop_points`: `C1` only. After approval, ordinary task completion does not stop the execution unit unless an `X*` contingency produces a typed blocked or needs-design exit.
- `task_ordering_rationale`: establish machine-readable semantic limits before mechanics, prove pure mechanics before Pi event binding, prove the native bridge before removing procedural Skill text, prove temporary loading before changing global settings, and synchronize stable truth only from converged runtime evidence.

## Recovery

`default_failure_policy: fix_forward`. Preserve the smallest failing state, repair only the causally owning task slice, rerun its focused oracle, and continue only after convergence. If `PIN-600` exposes a regression owned by an earlier completed task, keep convergence pending and reopen that exact owner for its one focused repair rather than widening `PIN-600`. A task's one accepted implementation finding may receive one focused same-slice repair; a repeated or plan-expanding defect triggers the matching `X*` stop instead of an unbounded loop.

Before user-level installation, run the adapter through temporary extension loading. If global registration prevents Pi startup or duplicates discovery, use Pi's no-extension mode or remove only this integration's exact package registration and `codingHarness` namespace from `/home/csheng/.pi/agent/settings.json`, preserving every pre-existing setting and repository evidence. Do not restore the command runner as a second authority, destructively reset the checkout, rewrite unrelated user changes, commit, push, publish, or release.

## Truth Sync Handoff

`truth_sync_required: true`. Stable truth targets are `AGENTS.md`, `README.md`, `docs/architecture/workflow-orchestration.md`, `docs/architecture/install-surface.md`, and `docs/architecture/invocation-contract.md`; the architecture diagrams and generated SVGs are subordinate generated truth refreshed from those contracts. The Pi integration guide and `docs/plans/2026-08-27-agent-skills-pi-handoff.md` are implementation and stage handoffs, not substitutes for stable truth.

Docs-governance predicates are `ownership`, `truth-root`, `canonical-terminology`, `search-boundary`, and `generated-subordination`. Truth sync must name `PI-HARNESS-003`, distinguish semantic kernel from host mechanics, document global package versus global Skill discovery as separate surfaces, retire the required runner syntax, and keep `docs/plans/` outside default stable-doc search.
