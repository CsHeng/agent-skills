+++
artifact_kind = "plan"
contract_version = 3
design_ref = "2026-08-19-external-touch-single-pipeline-and-dead-lane-cleanup-design.md"
design_sha256 = "de4c42568dfb150b20e1f2af93546e41fd3ac44774f81f812b5c81d54bef3001"
approval_status = "approved"
truth_sync_required = false
stable_truth_refs = []

[scope]
impl_file_refs = ["scripts", "src/runtime/harness", "skills"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "ETC-010"
depends_on = []
verification_commands = ["! rg -l 'check-fixtures|check-review-boundary' --glob '!docs/plans/**' scripts tests src contracts docs README.md AGENTS.md hooks install.sh install-codex.sh", "uv run pytest tests/test_check_orchestration.py -q"]
scope_slice = "Delete the caller-less validation material left by 42f06e1: both retired checker scripts, the four orphaned request fixtures, and the four matching golden files."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "fast"
reasoning_profile = "light"
isolation = "controller-checkout"
resource_locks = ["dead-checker-lane"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["scripts/check-fixtures.py, scripts/check-review-boundary.sh, the four named tests/fixtures request JSONs, and all tests/golden/*.expected.json files are deleted with the empty tests/golden directory removed.", "No authored reference to either script remains outside docs/plans and repository history.", "tests/fixtures/codex-agents and tests/fixtures/herdr remain untouched because live Herdr contract tests consume them."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["scripts/check-fixtures.py", "scripts/check-review-boundary.sh"]
test_file_refs = ["tests/fixtures/read-only-request.json", "tests/fixtures/micro-doc-change.json", "tests/fixtures/regulated-infra-change.json", "tests/fixtures/implicit-smart-commit-request.json", "tests/golden"]
external_impl_file_refs = []

[[tasks]]
task_id = "ETC-020"
depends_on = []
verification_commands = ["! rg -n 'test_active_command_adapters_use_owner_local_runners' tests", "uv run pytest tests/test_command_retirement_contracts.py -q"]
scope_slice = "Remove the vacuous command-adapter test that early-returns on the missing commands/ directory and asserts deleted Shell runner scripts, keeping every live archive-inertness and retirement-disposition guard in the same file."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "fast"
reasoning_profile = "light"
isolation = "controller-checkout"
resource_locks = ["retirement-contract-tests"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["Only test_active_command_adapters_use_owner_local_runners is removed from tests/test_command_retirement_contracts.py.", "The remaining retirement and archive-inertness tests still pass."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = []
test_file_refs = ["tests/test_command_retirement_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "ETC-030"
depends_on = []
verification_commands = ["! rg -n 'def prepare_intent|add_parser\\(\"stage\"\\)|add_parser\\(\"prepare\"\\)' src/runtime/harness/external_touch.py", "uv run ruff check src/runtime/harness", "uv run ty check src/runtime/harness"]
scope_slice = "Collapse external-touch intent creation to the documented reservation chain: remove prepare_intent and the stage and prepare CLI subcommands from external_touch.py while keeping stage_payload as the internal materialization helper behind stage_declared_payload and keeping the staging candidate-schema branch in validate_evidence_state."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["prepare_intent, its CLI parser entries, and its dispatch branches no longer exist in src/runtime/harness/external_touch.py.", "stage_payload, declare_intent, stage_declared_payload, finalize_intent, apply, apply-and-cleanup, cleanup, compare, validate-state, durable-replace, and baseline operations are unchanged.", "The expected pre-repair evidence is the current one-shot-path tests failing against the edited runtime until ETC-040 lands."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/external_touch.py"]
test_file_refs = []
external_impl_file_refs = []

[[tasks]]
task_id = "ETC-040"
depends_on = ["ETC-030"]
verification_commands = ["uv run pytest tests/test_external_touch_evidence.py src/runtime/harness/tests -q", "! rg -n 'prepare_intent|\"stage\",|\"prepare\",' tests/test_external_touch_evidence.py src/runtime/harness/tests/test_ledger.py"]
scope_slice = "Rewrite the one-shot-path tests and the ledger external-evidence fixture helper onto the declare, stage-declared, finalize reservation chain while preserving every drift, replay, noop, ambiguous-cleanup, and secret-safety assertion."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["external-touch-tests"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["test_external_touch_evidence.py unit and CLI tests exercise baseline, declare, stage-declared replay, finalize, apply-and-cleanup, compare, and cleanup with the same negative-case coverage.", "src/runtime/harness/tests/test_ledger.py builds external evidence only through declare_intent, stage_declared_payload, and finalize_intent.", "No test or helper references prepare_intent or invokes the removed stage or prepare CLI operations."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = []
test_file_refs = ["tests/test_external_touch_evidence.py", "src/runtime/harness/tests/test_ledger.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "ETC-050"
depends_on = ["ETC-010", "ETC-020", "ETC-030", "ETC-040"]
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/generate-workflow-diagrams.py", "bash scripts/check.sh", "git diff --check"]
scope_slice = "Refresh the tracked generated root-flat payload so the six skill-local runtime bundles match the edited production runtime, then run the full aggregate acceptance lane."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["generated-skill-tree", "aggregate-check"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["The generated skills tree equals authored content plus the exact production runtime manifest with no missing, stale, or extra files.", "bash scripts/check.sh passes end to end, including bundle parity, contract, Ruff, ty, pytest, and Markdown lanes.", "skills.index.json and the workflow diagrams are byte-stable no-ops because skill metadata and routing contracts are untouched."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["skills"]
test_file_refs = []
external_impl_file_refs = []
+++
# Plan

Execution-grade serial task catalog for the approved design `2026-08-19-external-touch-single-pipeline-and-dead-lane-cleanup-design.md` (sha256 `de4c42568dfb150b20e1f2af93546e41fd3ac44774f81f812b5c81d54bef3001`, `approval_status: approved`, DEC-1 approved by the user on 2026-08-19). Five main-executor tasks run serially: two low-risk dead-material deletions first, then the runtime pipeline collapse, its test rewrite, and the generated-refresh plus aggregate acceptance lane last.

## Implementation

ETC-010 deletes the retired checker bodies and their orphaned fixture and golden files; ETC-020 removes the single vacuous command-adapter test; ETC-030 removes `prepare_intent` and the `stage` and `prepare` CLI subcommands from the authored runtime while preserving `stage_payload`, the documented reservation chain, and the `staging` candidate-schema branch of `validate_evidence_state`; ETC-040 rewrites the affected tests and the ledger fixture helper onto the `declare` → `stage-declared` → `finalize` chain with unchanged negative-case coverage; ETC-050 regenerates the tracked root-flat payload and runs the aggregate `check.sh` acceptance lane. Tasks ETC-010 through ETC-040 run in the controller checkout with disjoint file sets; ETC-050 integrates and converges the whole change. The plan stays inside the approved design scope: `scripts`, `src/runtime/harness`, and `skills` for implementation and `tests` plus `src/runtime/harness/tests` for tests. The index and workflow-diagram generators are re-run by ETC-050 for staleness safety but are expected byte-stable no-ops outside the declared touch set; any diff there indicates pre-existing generated drift and is handled fix-forward inside the aggregate lane, never by widening this plan's scope.

## Work Package Readiness

- `milestone_objective`: complete the 2026-08-19 simplification cleanup by deleting dead validation material, removing the vacuous retirement test, and collapsing external-touch intent creation to the single documented reservation chain.
- `non_goals`: no evidence-schema, ledger, wire-format, or stable-truth changes; no restoration of retired Shell harness, `commands/`, the review-language check lane, or retired skills; no refactor of deliberate task-shape projection (audit C4); no test-directory reorganization (audit C5); no version bump.
- `future_phase`: optional design-decisions changelog entry for DEC-1 and optional re-wiring of a retired-review-language guard are deliberately out of the approved design scope and excluded from this milestone.
- `decision_status`: `ready_for_review` (DEC-1 resolved by human design approval).
- `oracle_strategy`: existing executable oracles only — characterization via the current pytest suites (external-touch chain, ledger convergence, retirement contracts, check orchestration), static `rg` absence proofs for deleted surfaces, Ruff and ty on the authored runtime, and the aggregate `bash scripts/check.sh` lane including generated bundle parity; no new oracle class is required because behavior removal is fully observable through these existing oracles.
- `acceptance_oracles`: the five per-task `verification_commands` above plus the design's Validation section.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: 2.
- `subagent_ready`: false (all tasks are main-executor serial slices; no delegated slice would execute without redefining scope or authority).

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: none — DEC-1 was the only human decision and is already resolved by design approval; no destructive writes, external dependencies, credentials, live cutovers, or parallel-batch approvals exist in this plan.
- `runtime_contingencies`: none declared — an ordinary verification failure is fix-forward repair inside the approved touch set, not a stop contingency.
- `planned_stop_points`: empty.
- `task_ordering_rationale`: the two zero-risk dead-material deletions (ETC-010, ETC-020) run first; the only behavior-affecting edit (ETC-030) follows with its immediately dependent test rewrite (ETC-040); generated refresh and aggregate acceptance (ETC-050) run last as the integration convergence point, which is also the safe retry boundary if bundle regeneration fails.

## Recovery

`default_failure_policy: fix_forward` for every task: diagnose, repair inside the approved touch set, rerun the narrow task oracle, and continue toward aggregate acceptance. All edits are tracked-file deletions or rewrites recoverable through ordinary Git history; no persisted data, ledger file, or external file is touched, so no guarded-rollback trigger, target, or verification is declared. If bundle regeneration in ETC-050 fails, restore the immediately preceding generated tree and retry; never hand-edit generated `skills/` content.

## Truth Sync Handoff

`truth_sync_required = false` and `stable_truth_refs = []`: the approved design records truth impact as none required because stable truth already documents the single reservation chain and never documents any removed surface; `docs_governance_predicates = none`. The DEC-1 record lives in the approved design artifact under `docs/plans/`; an optional `docs/changelog/design-decisions.md` entry is future-phase work outside the approved design scope.
