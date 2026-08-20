+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-20-live-symlink-skill-management-design.md"
design_sha256 = "cfa8ccfdd4c9a742b2408136f5c14fe11a9eed84a5247146b01304346350dc4f"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["AGENTS.md", "README.md", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
default_runtime_model_policy = "semantic-routing"
parallel_execution_approved = false

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts/install-targets.toml", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = ["tests/test_install_target_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "LSM-010"
depends_on = []
verification_commands = ["uv run pytest tests/test_install_target_contracts.py -q"]
scope_slice = "Add a red-first install-contract oracle, then make live per-skill symlinks the recommended management mode while retaining optional plugin compatibility and compatible-but-non-recommended npx skills use."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["install-contract"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["The pre-change focused test fails because the contract does not yet declare live-symlink recommendation and compatibility-only plugin and npx policies.", "The updated contract names ~/.agents/skills child links, a local Git checkout, and git pull as the recommended local lifecycle.", "Both provider manifests and the sole root-flat materialization target remain unchanged, and the focused test passes."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts/install-targets.toml"]
test_file_refs = ["tests/test_install_target_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "LSM-020"
depends_on = ["LSM-010"]
verification_commands = ["rg -n -i 'live symlink|~/.agents/skills|npx skills|optional compatibility|git pull|duplicate' AGENTS.md README.md docs/architecture docs/changelog/design-decisions.md docs/quickstart.md", "git diff --check"]
scope_slice = "Synchronize stable repository guidance on authored and generated ownership, recommended local Git-plus-symlink management, optional plugins, non-recommended npx copy installation, duplicate discovery, and the ordered Grok-before-Claude machine cutover."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["stable-distribution-truth"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["README and quickstart lead with the live-symlink topology and present plugins and npx only as compatible alternatives.", "AI-facing and architecture truth no longer claim Claude and Codex plugins are the maintained primary entry surface.", "The durable decision log records why the 2026-08-07 native-plugin recommendation is superseded while preserving standalone resource closure and compatibility."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = []
external_impl_file_refs = []

[[tasks]]
task_id = "LSM-030"
depends_on = ["LSM-020"]
verification_commands = ["codex plugin list", "claude plugin list", "grok inspect --json", "find -L /Users/csheng/.claude/skills -mindepth 1 -maxdepth 1 -type d"]
scope_slice = "Capture a zero-duplicate Grok baseline and confirm Claude skill compatibility plus the coding plugin are disabled in Grok; then uninstall coding@csheng from Codex and Claude, add 39 non-conflicting Claude child symlinks to the same generated targets as ~/.agents/skills, and repeat the Grok and link-identity probes."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["user-skill-discovery", "claude-plugin-state", "codex-plugin-state"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Before any Claude link is added, Grok reports no duplicate skill names, resolved Claude skill compatibility is disabled, and the coding plugin is disabled.", "Claude Code and Codex no longer report coding@csheng as installed; unrelated plugins and both csheng marketplace registrations remain unchanged.", "Exactly 39 newly managed Claude coding links resolve to the same generated directories as their ~/.agents/skills counterparts and the pre-existing herdr link is preserved.", "After link creation, Grok still reports no duplicate names and no coding skill sourced from a Claude compatibility path."]
failure_policy = "guarded_rollback"
rollback_trigger = "The post-link Grok probe reports a duplicate name or a coding skill sourced from Claude compatibility that was absent from the captured pre-link baseline."
rollback_target = "Remove exactly the 39 Claude coding symlinks created by LSM-030 while preserving ~/.claude/skills/herdr, both plugin removals, all marketplace registrations, and Grok configuration."
rollback_verification = "Rerun the same Grok JSON probe and require the captured zero-duplicate baseline plus absence of Claude-sourced coding skills."

[tasks.scope]
impl_file_refs = []
test_file_refs = []
external_impl_file_refs = []

[[tasks]]
task_id = "LSM-040"
depends_on = ["LSM-030"]
verification_commands = ["bash scripts/check.sh", "claude plugin validate .", "uvx --with pyyaml python /Users/csheng/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .", "git diff --check"]
scope_slice = "Run aggregate repository validation, both retained plugin compatibility validators, exact local-state probes, and a bounded implementation review without installing copied skills, committing, pushing, or publishing."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["repository-acceptance", "user-skill-discovery"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Focused and aggregate contract, generated-surface, standalone-closure, Ruff, ty, pytest, Markdown, and plugin compatibility checks pass.", "The final diff is contained by the approved repository touch set and local state matches the approved Grok, Claude, Codex, and symlink invariants.", "No npx installation, third-party repository update, Grok configuration change, plugin version bump, commit, push, or publication occurs."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts/install-targets.toml", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = ["tests/test_install_target_contracts.py"]
external_impl_file_refs = []
+++
# Plan

## Implementation

Implement the approved live-symlink distribution decision as one serial unit. LSM-010 establishes an executable contract before prose changes. LSM-020 synchronizes durable repository guidance. LSM-030 treats Grok's zero-duplicate state as a hard precondition before changing Claude exposure, removes only the two explicitly named installed plugins, and performs one guarded Claude-link cutover. LSM-040 verifies both the recommended path and the retained compatibility surfaces.

The current-machine symlink and plugin operations are explicitly authorized local installation-state changes, not repository external-file edits and not use of the exact-existing-file broker. They cannot widen the repository touch set. Plugin marketplaces remain registered so optional compatibility can be re-enabled deliberately later.

## Work Package Readiness

- `milestone_objective`: make local Git clones plus live per-skill symlinks the recommended management topology, retain copy and plugin compatibility, remove active duplicate plugin exposure, and add Claude links only after Grok collision safety is proven.
- `non_goals`: no generated-skill content change, public-ID rename, plugin deletion, plugin version bump, marketplace removal, third-party clone update, npx execution, Grok configuration change, Ante or Pi adapter creation, unrelated Claude skill cleanup, commit, push, or publication.
- `future_phase`: add a repository-owned preview/apply symlink manager only if repeated manual link reconciliation becomes measurable maintenance cost.
- `decision_status`: `ready_for_review`.
- `oracle_strategy`: contract test, source-to-generated aggregate checks, plugin validators, exact symlink realpath comparison, and pre/post Grok resolved-state probes.
- `acceptance_oracles`: the exact task verification commands plus direct bounded design, plan, and implementation review.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: `2`, one focused contract/truth review and one final bounded implementation review.
- `subagent_ready`: `false`; the coupled local machine state and repository truth remain main-controller work.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0`; the user explicitly approved the recommended topology, both named plugin removals, and the Grok-gated Claude symlink addition on 2026-08-20.
- `runtime_contingencies`: `X1` stops before local mutation if Grok already has duplicate names or its resolved Claude/coding exclusions are absent; `X2` stops before link creation on any conflicting Claude path; `X3` executes the declared guarded rollback only for a new post-link Grok collision; `X4` stops on repository scope drift or an unrelated local plugin-state change.
- `planned_stop_points`: none when all preconditions and probes pass.
- `task_ordering_rationale`: encode and document the durable contract first, prove Grok isolation second, then remove plugin duplicates and expose Claude through links, and finally verify the converged repository and machine state.

Expected continuous range after approval: `E1 = LSM-010..LSM-040`.

## Recovery

`default_failure_policy: fix_forward`. Repair repository contract or prose at its owner and rerun the narrow oracle. Do not auto-reinstall plugins. LSM-030 alone carries the exact guarded rollback declared in its task metadata; it removes only links created by that task and never rewrites Grok configuration or unrelated Claude state.

## Truth Sync Handoff

`truth_sync_required: true`. Stable truth refs are the root README and AGENTS plus the declared quickstart, architecture, and decision-log files. Docs-governance predicate: `canonical-terminology-across-surfaces`. Truth sync must confirm that "recommended" consistently means live local Git checkout plus child symlinks, while "compatible" covers optional plugins and `npx skills` copy installation.

## Review Gate

- `required_entry`: `review-change`
- `review_component`: `review-plan`
- `actor_role`: `main`
- `review_depth`: `boundary`
- `review_status`: `passed`
- `candidate_findings`: none
- `review_evidence`: Direct bounded review was selected because delegation is disabled for this session and the plan is a small serial contract, documentation, and local-install-state change. The plan preserves source/generated ownership, makes Grok isolation a precondition, names exact local mutations, provides collision and conflict stops, and limits rollback to links created by the current task.
