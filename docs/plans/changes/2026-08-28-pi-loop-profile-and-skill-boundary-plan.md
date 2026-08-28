+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-28-pi-loop-profile-and-skill-boundary-design.md"
design_sha256 = "0a80efc65b17674b25a4d18721db7f9b0e576ba798cf3ffa70e4126ea595ed67"
decision_id = "PI-LOOP-001"
approval_status = "approved"
decision_status = "approved_for_implementation"
review_verdict = "needs-fixes"
review_resolution = "resolved"
truth_sync_required = true
parallel_execution_approved = false

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts", "docs/architecture", "scripts", "skills.index.json", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = ["/Users/csheng/workspace/playground/pi-extensions/AGENTS.md", "/Users/csheng/workspace/playground/pi-extensions/README.md", "/Users/csheng/workspace/playground/pi-extensions/docs/architecture", "/Users/csheng/workspace/playground/pi-extensions/extensions", "/Users/csheng/workspace/playground/pi-extensions/package.json", "/Users/csheng/workspace/playground/pi-extensions/package-lock.json", "/Users/csheng/workspace/playground/pi-extensions/scripts", "/Users/csheng/workspace/playground/pi-extensions/tests"]

[[tasks]]
task_id = "PLP-100"
repository = "/Users/csheng/workspace/playground/pi-extensions"
depends_on = []
objective = "Add and prove a thin plan-mode extension without changing the installed package export or removing the current workflow harness."
verification_commands = ["npm run typecheck", "node --experimental-strip-types --test tests/plan-mode.test.ts", "bash scripts/run-temporary-plan-mode-probe.sh", "git diff --check -- extensions/plan-mode tests/plan-mode.test.ts scripts/run-temporary-plan-mode-probe.sh"]
done_when = ["The extension registers explicit /plan and /default commands plus the --plan startup flag.", "Plan profile sets the active tools to exactly read, grep, find, and ls; default restores the exact pre-entry list.", "Repeated entry does not overwrite the saved list, and session restore reapplies plan tools before another model turn.", "Persisted state contains only profile and toolsBeforePlan; the extension registers no model-facing tool and no agent_end continuation.", "The temporary RPC probe loads only the explicit extension path, observes its commands and state entries, and proves that --no-extensions without the explicit path exposes neither command."]
failure_policy = "fix_forward"

[tasks.scope]
impl_file_refs = ["extensions/plan-mode/index.ts", "scripts/run-temporary-plan-mode-probe.sh"]
test_file_refs = ["tests/plan-mode.test.ts"]
external_impl_file_refs = []

[[tasks]]
task_id = "PLP-200"
repository = "/Users/csheng/workspace/playground/market-csheng"
depends_on = []
objective = "Remove the prompt-space lifecycle controller from authored Skills and contracts while preserving semantic selection, distribution, and conditional review."
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/check-contracts.py", "python3 -m pytest tests/test_semantic_skill_contracts.py tests/test_skill_workflow_contracts.py tests/test_skill_routing_contracts.py tests/test_skill_activation_contracts.py tests/test_session_interaction_contracts.py -q", "git diff --check -- contracts scripts src/skills skills skills.index.json tests"]
done_when = ["contracts/lifecycle.toml and contracts/workflow-modes.toml no longer exist.", "contracts/skills.toml no longer carries lifecycle_owner, universal approved-plan prerequisites, or mandatory review composition.", "The explicit implement-change-via-herdr overlay retains its approved bounded-plan precondition because delegated mutation needs frozen scope; that specific guard is not treated as a universal lifecycle gate.", "The routing contract retains discovery, explicit direct-match bypass, semantic trigger cases, support routes, and one primary response owner but contains no gate policy, fixed phase routes, review evaluator route, or implicit review rule.", "design-change, plan-change, and implement-change describe review as conditional rather than exactly-once; implement-change accepts an explicit bounded mutation request or an approved plan.", "sync-truth and organize-docs rely on explicit request, evidence, and authority rather than a synthetic approved-plan prerequisite.", "activation_mode remains a static provider-discovery projection and is not renamed or described as runtime mode.", "Generated Skills and the index match authored source after the contract change."]
failure_policy = "fix_forward"

[tasks.scope]
impl_file_refs = ["contracts/lifecycle.toml", "contracts/skills.toml", "contracts/workflow-modes.toml", "scripts/check-contracts.py", "scripts/generate-skills-index.py", "skills.index.json", "src/skills/session/use-coding-skills", "src/skills/workflows", "src/skills/disciplines/organize-docs", "skills"]
test_file_refs = ["tests/test_semantic_skill_contracts.py", "tests/test_skill_workflow_contracts.py", "tests/test_skill_routing_contracts.py", "tests/test_skill_activation_contracts.py", "tests/test_session_interaction_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PLP-210"
repository = "/Users/csheng/workspace/playground/market-csheng"
depends_on = ["PLP-200"]
objective = "Converge stable truth, diagrams, validators, and repository acceptance on semantic Skill composition rather than a sovereign workflow."
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/generate-workflow-diagrams.py", "python3 -m pytest tests/test_maintenance_guidance_contracts.py tests/test_skill_trigger_diagram.py tests/test_check_orchestration.py tests/test_standalone_check.py -q", "bash scripts/check.sh", "git diff --check"]
done_when = ["AGENTS.md and README.md assign semantic guidance to Skills and request-level judgment to the active coding agent without naming a sovereign kernel.", "Maintained architecture docs distinguish agent loop, capability profile, semantic Skill, and any separately designed future orchestrator.", "The fixed analyze-design-plan-implement-review-truth-close pipeline and its generated diagram are removed or replaced by non-sequential Skill-composition truth.", "Validators and tests assert structured semantic contracts and obsolete-control absence without pinning exact explanatory prose.", "The tracked diagrams, SVGs, root-flat Skills, and skills.index.json are current.", "The aggregate repository check passes without Pi, pi-extensions, user settings, or a workflow runtime."]
failure_policy = "fix_forward"

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture", "scripts/generate-workflow-diagrams.py", "scripts/check.sh", "skills.index.json", "skills"]
test_file_refs = ["tests/test_maintenance_guidance_contracts.py", "tests/test_skill_trigger_diagram.py", "tests/test_check_orchestration.py", "tests/test_standalone_check.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PLP-300"
repository = "/Users/csheng/workspace/playground/pi-extensions"
depends_on = ["PLP-100"]
objective = "Cut the live package export to the proven plan-mode extension and probe the installed surface while retaining the old harness as the exact rollback target."
verification_commands = ["node --experimental-strip-types --test tests/plan-mode.test.ts tests/package.test.ts tests/installed-probe.test.ts", "bash scripts/run-temporary-plan-mode-probe.sh", "bash scripts/run-installed-plan-mode-probe.sh", "pi list --no-approve", "git diff --check -- package.json scripts tests"]
done_when = ["package.json exports exactly extensions/plan-mode/index.ts and no workflow extension.", "The old extensions/workflow-harness tree and its old installed probe remain present throughout this task.", "The installed RPC probe observes exactly one /plan and one /default command, no workflow-harness command, and extension-off absence; package and component tests separately prove that the exported module registers no model-facing tool.", "The package remains the already registered local Pi package; no install, update, settings edit, or package-manager publication occurs."]
failure_policy = "guarded_rollback"
rollback_trigger = "The installed plan-mode probe fails after the package export is changed."
rollback_target = "Restore only package.json's extension export to ./extensions/workflow-harness/index.ts while the old source is still present; preserve plan-mode source and failing evidence."
rollback_verification = "Run bash scripts/run-installed-workflow-probe.sh and stop before PLP-310."

[tasks.scope]
impl_file_refs = ["package.json", "scripts/run-installed-plan-mode-probe.sh"]
test_file_refs = ["tests/package.test.ts", "tests/installed-probe.test.ts"]
external_impl_file_refs = []

[[tasks]]
task_id = "PLP-310"
repository = "/Users/csheng/workspace/playground/pi-extensions"
depends_on = ["PLP-300"]
objective = "After installed cutover evidence passes, retire the managed workflow implementation and converge the Pi package on one loop-profile extension."
verification_commands = ["npm install --package-lock-only --ignore-scripts --offline", "npm run check", "bash scripts/run-temporary-plan-mode-probe.sh", "bash scripts/run-installed-plan-mode-probe.sh", "if rg -n 'workflow_(activate|submit_graph|update_task|complete_stage|submit_review|adjudicate_review|complete_repair|settle)|extensions/workflow-harness' package.json extensions scripts; then exit 1; fi", "git diff --check"]
done_when = ["extensions/workflow-harness and every workflow-only test, fixture, probe, and settings-cutover script are removed.", "typebox and any other workflow-only dependency are removed from package.json and package-lock.json.", "AGENTS.md, README.md, package metadata, and maintained architecture describe only explicit loop-profile ownership and repository independence.", "The plan-mode implementation contains no task identity, graph, lifecycle phase, review, repair, replay, settlement, child dispatch, terminate result, or agent_end continuation.", "The complete Pi package check and both profile probes pass after old-source removal."]
failure_policy = "fix_forward"

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture", "extensions/workflow-harness", "package.json", "package-lock.json", "scripts", "extensions/plan-mode"]
test_file_refs = ["tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PLP-400"
repository = "both"
depends_on = ["PLP-210", "PLP-310"]
objective = "Collect independent final evidence from each repository and characterize removal of the three observed managed-workflow failure classes."
verification_commands = ["cd /Users/csheng/workspace/playground/market-csheng && bash scripts/check.sh && git diff --check", "cd /Users/csheng/workspace/playground/pi-extensions && npm run check && bash scripts/run-temporary-plan-mode-probe.sh && bash scripts/run-installed-plan-mode-probe.sh && pi list --no-approve && git diff --check"]
done_when = ["Each repository passes from its own root and its checks do not locate, import, or execute the other repository.", "Maintained market-csheng surfaces contain no host workflow mode, universal review count, fixed phase pipeline, or pi-extensions dependency.", "Maintained pi-extensions surfaces contain no workflow_* tool, activation provenance, proposal binding, graph admission, protocol settlement, or terminate-based continuation.", "The former directory/stale-activation, frozen-proposal binding, and premature protocol-stop paths are absent rather than retried or masked.", "No model-dependent exact-response assertion is used as acceptance evidence.", "Only the two pending design/plan artifacts and approved implementation touch sets are changed; no commit, push, publication, installation, settings mutation, or unrelated cleanup occurs."]
failure_policy = "fix_forward"

[tasks.scope]
impl_file_refs = []
test_file_refs = ["/Users/csheng/workspace/playground/market-csheng/tests", "/Users/csheng/workspace/playground/pi-extensions/tests"]
external_impl_file_refs = []
+++
# Pi Loop Profile And Semantic Skill Boundary Plan

## Readiness

- `architecture_decision`: `PI-LOOP-001`; preserve the independent repositories from `PI-EXT-002`, supersede only its managed-workflow runtime.
- `design_source`: `2026-08-28-pi-loop-profile-and-skill-boundary-design.md` at SHA-256 `0a80efc65b17674b25a4d18721db7f9b0e576ba798cf3ffa70e4126ea595ed67`.
- `scope_basis`: the user approved the design and this exact plan on 2026-08-28 and explicitly invoked `implement-change`, including the declared live export cutover and tracked harness removal.
- `milestone_objective`: replace the installed Pi workflow VM with one explicit read-only plan profile and remove the remaining prompt-space workflow controller from the semantic Skill repository.
- `non_goals`: orchestrator, autopilot, task graph, shell policy, generic permission framework, automatic review, model routing, subagent scheduling, settings edits, install/update, public Skill ID changes, plugin version changes, commit, push, publication, or deployment.
- `future_phase`: only the observable upgrade triggers in `PI-LOOP-001`; none are pre-authorized here.
- `decision_status`: `approved_for_implementation`; the one bounded plan review is adjudicated, its accepted oracle/scope findings are repaired, and the user has granted the plan's exact repository-local implementation authority.

The local prerequisites are currently observable: Pi `0.84.3`, Node `v26.7.0`, npm `11.19.0`, `jq`, Python, PlantUML, and GNU `realpath` are available. Before implementation, recheck both working trees. The design and plan files created by this design session are expected; any other overlapping change is a conflict stop, not permission to overwrite user work.

No account, credential, network, publication, or physical prerequisite blocks this plan. The Pi runtime probes use offline RPC command handling and do not call a model. `pi list --no-approve` is read-only and verifies the existing local package registration without changing settings.

## Execution Order And Ownership

Execute serially as `PLP-100 → PLP-200 → PLP-210 → PLP-300 → PLP-310 → PLP-400`. The dependency graph intentionally records that the initial Pi profile slice and market Skill slice are factually independent, but parallel execution is not approved: both involve generated or live-consumed surfaces, there is no latency requirement, and one controller should preserve the cutover and evidence boundary.

`subagent_ready = false`. No task needs a separate writer or reviewer. A single implementation owner works in one repository at a time, never treats the shared checkout as a multi-writer surface, and returns to the owning task if a verification failure needs repair.

Stable responsibility is:

| Work | Owner | Convergence evidence |
| --- | --- | --- |
| Thin plan profile and package cutover | `pi-extensions` implementation | component tests plus temporary and installed RPC probes |
| Semantic Skill and contract de-gating | `market-csheng` authored source | structured contract tests plus generated parity |
| Stable truth and diagrams | each owning repository | repository aggregate check |
| Cross-repository judgment | active implementation controller | two independent result summaries, never a shared runtime check |

## Oracle Strategy

The protected boundaries and evidence are deliberately smaller than the retired harness:

| Boundary | Primary oracle | Why |
| --- | --- | --- |
| Plan/default capability projection | component tests around a fake Pi extension API | deterministically observes exact tool sets, state, prompt marker, and idempotence |
| Session restore | component replay of the minimal custom entry | proves fail-closed profile recovery without a model call |
| Temporary and installed packaging | offline Pi RPC probes | proves actual command discovery, explicit command handling, package export, and extension-off behavior |
| Absence of workflow VM | source/package negative capability tests | the correct regression is deletion of the failing protocol paths |
| Semantic-only Skills | TOML/Markdown contract tests and source/generated parity | tests owned structure and boundaries without brittle prose matching |
| Repository acceptance | each repository's aggregate command | prevents a hidden cross-repository test or build dependency |

Do not recreate model-based end-to-end tests that wait for exact final prose. The reported early stops originated in explicit `terminate` and settlement protocol paths; their deletion plus ordinary Pi command/profile probes is the causal oracle. Property/model-state testing is not selected because no workflow state machine remains.

## Task Notes

### PLP-100: Shadow Plan Profile

Use Pi's public `registerCommand`, `registerFlag`, `getActiveTools`, `getAllTools`, `setActiveTools`, status, prompt-injection, and custom-entry/session events. Borrow only those capability-profile mechanics from Pi's installed example. Do not copy todo extraction, execution mode, `[DONE:n]`, widgets, shell command parsing, `agent_end`, or automatic implementation transition.

The implementation should remain one small module unless a helper is independently justified by focused tests. The fake API test owns exact behavior; the RPC probe owns real loader and command wiring. The package manifest remains untouched, so failure cannot affect the installed extension surface.

### PLP-200 And PLP-210: Semantic De-Gating

Remove redundant lifecycle ownership instead of renaming it. `category = "workflow"` may continue to describe a semantic workflow Skill, but it grants no top-level authority. Keep `activation_mode` because it projects provider discovery behavior rather than runtime state.

Make review guidance conditional on an explicit request, an applicable repository/approved-scope rule, or an evidence-backed risk judgment. Preserve `review-change` as a bounded read-only capability and keep evaluator Skills optional. Do not replace the removed fixed review count with a more elaborate scoring system.

Keep the explicit `implement-change-via-herdr` overlay plan-bound. Its approved bounded-plan precondition protects delegated mutation and does not force ordinary `implement-change`, truth sync, docs work, or other Skills through a universal lifecycle.

Rewrite routing around direct match, ambiguity resolution, one primary response owner, and optional semantic overlays. Remove the lifecycle table rather than replacing it with another universal sequence. Stable diagrams should show composition or ownership, not arrows that imply mandatory phase progression.

### PLP-300: Export-Only Cutover

This is the only guarded rollback task. It changes the live-consumed package export after the unexposed extension passes. The old source and old installed probe must remain byte-for-byte available during the new installed probe. A failure restores only the manifest export through an explicit patch and verifies the predecessor; it does not reset either repository or discard the new evidence.

No `pi install`, `pi update`, settings file edit, or package cache manipulation is needed because Pi already consumes this local package root. New Pi processes observe the manifest change; the current design session is not used as cutover evidence.

### PLP-310: Managed Workflow Retirement

Old source removal is authorized only after PLP-300 passes. Remove the implementation and tests instead of keeping compatibility shims, deprecated commands, inert adapters, or migration state. Historical stage documents, Git history, and the two supplied user session files remain untouched.

After old-source removal, recovery is fix-forward in `plan-mode`. The plan does not authorize reconstructing the retired workflow from Git or retaining a hidden fallback export.

### PLP-400: Independent Acceptance

Run both aggregate checks from their own roots and report results separately. A final diagnostic scan may prove obsolete control terms absent from maintained source, but structured tests and package probes remain the owning oracles. Stage artifacts are historical/planning evidence and are excluded from product-dependency scans.

## Authority And Stop Conditions

Planning grants no mutation authority. Human approval must name this exact plan and explicitly include the `PLP-300` live package-export cutover and the `PLP-310` repository-local removal of the obsolete tracked harness. That approval authorizes only additions, edits, generation, and tracked removals inside the declared scopes.

It does not authorize user settings changes, `pi install/update/remove`, dependency upgrades unrelated to removing unused workflow packages, mutation outside the two repositories, destructive Git history operations, commit, push, publication, release, deployment, or cleanup of unrelated files.

Stop with `needs_design_decision` if implementation evidence shows that plan/default cannot be expressed as a tool/prompt projection without task-semantic state, or that removing the market contracts breaks a public Skill identity or provider discovery surface. Stop with `manual_checkpoint` before mutation if either working tree contains an overlapping user change, the installed package no longer resolves to this `pi-extensions` root, a required local tool is missing, or the user does not explicitly approve the live export and tracked removal.

Ordinary focused test failures stay inside their owning task and use fix-forward repair. A scope-expanding repair, repeated cutover failure, settings dependency, cross-repository runtime edge, or need for model-dependent settlement is a stop rather than permission to rebuild the harness.

## Truth Sync

Truth sync is part of the owning implementation tasks, not a mandatory follow-on phase. Expected stable targets are:

- `market-csheng`: `AGENTS.md`, `README.md`, `contracts/skills.toml`, the installed routing contract, workflow Skill source, maintained architecture docs, and composition diagrams.
- `pi-extensions`: `AGENTS.md`, `README.md`, `package.json`, the maintained architecture document, extension source, probes, and tests.

Stage artifacts under `docs/plans/` remain subordinate evidence. They may name both repositories for this one migration but do not create a product dependency or become input to either repository's checks.

## Plan Review

- `review_scope`: one direct read-only review of this exact plan against `PI-LOOP-001`, current file surfaces, Pi's RPC observability, declared oracles, task dependencies, authority, and recovery. It excluded implementation-style preferences and unrelated pre-existing defects.
- `review_verdict`: `needs-fixes` with three high-confidence, in-scope candidates: RPC command discovery could not directly prove absence of LLM tools; a broad forbidden-word scan over docs/tests conflicted with structured boundary testing; and the plan did not distinguish the justified plan-bound Herdr delegation overlay from universal approved-plan gates. The lockfile command also lacked the promised offline constraint.
- `adjudication`: accepted and repaired as one focused plan batch. Tool absence now belongs to component/package source tests while RPC owns command/package wiring; the scan is limited to concrete retired identifiers in executable/package surfaces; `implement-change-via-herdr` explicitly retains its bounded-plan guard; and lockfile convergence is offline. A focused coherence recheck confirms the revised task oracles and scopes agree with the design. No second review was started and no material plan finding remains.

## Approval

The user approved this exact plan on 2026-08-28 through `approve both and $coding:implement-change`. That approval includes `PLP-300` package-export cutover and `PLP-310` tracked harness removal, but none of the separately excluded settings, install/update/remove, commit, push, publication, release, or deployment actions.
