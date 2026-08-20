+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-20-harness-final-review-followup-design.md"
design_sha256 = "3bde3ac9022ef290da032c9974e7194fdef276706ba81cdad94f011db26a4eb0"
approval_status = "approved"
truth_sync_required = false
stable_truth_refs = []
default_runtime_model_policy = "semantic-routing"
parallel_execution_approved = false

[scope]
impl_file_refs = ["src/runtime/harness/artifacts.py", "src/runtime/harness/ledger.py", "skills"]
test_file_refs = ["src/runtime/harness/tests/test_v4_artifacts.py", "src/runtime/harness/tests/test_v4_ledger.py", "src/runtime/harness/tests/test_ledger.py", "tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "FRF-010"
depends_on = []
verification_commands = ["uv run pytest src/runtime/harness/tests/test_v4_artifacts.py src/runtime/harness/tests/test_v4_ledger.py src/runtime/harness/tests/test_ledger.py -q", "uv run ruff check src/runtime/harness/artifacts.py src/runtime/harness/ledger.py src/runtime/harness/tests/test_v4_artifacts.py src/runtime/harness/tests/test_v4_ledger.py src/runtime/harness/tests/test_ledger.py", "uv run ty check src/runtime/harness"]
scope_slice = "Add red-first oracles for the five accepted final-review findings, then repair artifact path and fence validation plus ledger version matching, admission exclusivity, and typed pre-promotion write failures without changing HCR-001 authority."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["artifact-contract", "ledger-state-machine", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Red tests prove both cross-version mismatch directions for truth-sync and close: a version-4 ledger rejects version-3 artifacts and an already-converged version-3 ledger rejects version-4 artifacts, while same-version version-3 evidence retains only its approved compatibility tail.", "Red tests prove that a second independent serial admission is rejected while one task remains active and that approved named-batch peers still enter through one admission identity.", "Red tests prove that drive-qualified Windows repository references and pseudo-closing Markdown fences are rejected on every host platform.", "Fault injection proves parent-directory creation and predecessor snapshot failures return ledger-write-failed before promotion without changing prior authority.", "All focused runtime tests, Ruff, and ty pass and one bounded implementation review has no accepted finding remaining."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/artifacts.py", "src/runtime/harness/ledger.py"]
test_file_refs = ["src/runtime/harness/tests/test_v4_artifacts.py", "src/runtime/harness/tests/test_v4_ledger.py", "src/runtime/harness/tests/test_ledger.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "FRF-020"
depends_on = ["FRF-010"]
verification_commands = ["python3 scripts/flatten-skills.py --target root-flat", "uv run pytest tests/test_runtime_distribution_contracts.py -q", "python3 scripts/flatten-skills.py --target root-flat --check"]
scope_slice = "Refresh the six generated skill-local runtime bundles from the repaired authored Python source and prove exact manifest, lifecycle-resource, and standalone parity without editing generated files by hand."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["generated-skill-tree"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["All six runtime owners contain byte-identical repaired artifacts.py and ledger.py projections plus the unchanged declared runtime resources.", "The generated root-flat surface passes exact manifest, standalone closure, and freshness checks.", "The separate external-touch cleanup remains attributable and no retired checker, fixture, golden, or runtime path is restored."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["skills"]
test_file_refs = ["tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "FRF-030"
depends_on = ["FRF-020"]
verification_commands = ["bash scripts/check.sh", "claude plugin validate .", "uvx --with pyyaml python /Users/csheng/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .", "git diff --check"]
scope_slice = "Run full repository acceptance and a final bounded implementation review; any accepted same-contract repair remains limited to the declared follow-up runtime, test, and generated surface and must rerun all four acceptance commands."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["repository-acceptance", "artifact-contract", "ledger-state-machine", "generated-skill-tree"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The aggregate contract, generated, standalone, Ruff, ty, pytest, and Markdown lanes pass from the converged tree.", "Both plugin validators and git diff --check pass without install, commit, push, publish, deploy, truth-sync approval, or close approval.", "The final bounded review finds no remaining violation caused by the five accepted findings or their repairs, and the diff remains the approved HCR repair plus this follow-up and the separately attributable external-touch cleanup."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/artifacts.py", "src/runtime/harness/ledger.py", "skills"]
test_file_refs = ["src/runtime/harness/tests/test_v4_artifacts.py", "src/runtime/harness/tests/test_v4_ledger.py", "src/runtime/harness/tests/test_ledger.py", "tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []
+++
# Plan

## Implementation

This plan implements the five accepted findings from final review batch `hcr-060-final-review-20260820` without reopening architecture decision HCR-001. FRF-010 owns all authored runtime and oracle repair so version matching, admission exclusivity, portable path validation, structural fence parsing, and typed pre-promotion failures converge together. FRF-020 performs the only generated refresh. FRF-030 keeps the entire approved repair surface available for at most one accepted final-review repair while otherwise remaining an acceptance task. All work is repository-local, controller-owned, serial, and fix-forward.

Architecture decision reference: HCR-001 Versioned Admission Instead Of In-Place Version-3 Drift. Reversible increments are focused red oracles and runtime repair, generated refresh, then aggregate acceptance. The upgrade trigger remains another persisted authority-shape change; none of the five findings changes that shape.

## Work Package Readiness

- `milestone_objective`: close the five causality-confirmed final-review gaps and return the original HCR repair to a reviewable passing state.
- `non_goals`: no lifecycle redesign, version 5, external-file work, stable-doc rewrite, new dependency, provider-specific routing, plugin install, commit, push, publish, deploy, truth-sync approval, or close approval.
- `future_phase`: S1-S6 simplification work and unrelated code cleanup remain outside this follow-up.
- `decision_status`: `ready_for_review`.
- `oracle_strategy`: red-first example and state-transition tests, a bidirectional truth-sync/close artifact-ledger version mismatch matrix plus same-version version-3 tail coverage, portable path and structural Markdown negatives, deterministic pre-promotion fault injection, generated parity, and full aggregate acceptance.
- `acceptance_oracles`: the exact task verification commands plus bounded task review and final implementation review.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: `3`, one for authored runtime repair, one focused generated-parity review, and one final whole-slice review.
- `subagent_ready`: `false`; all mutation and repair stays with the main controller, while reviewer delegation remains read-only.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0`; no remaining confirmation is needed after explicit plan approval.
- `runtime_contingencies`: `X1` stops on `ledger-durability-unknown`; `X2` stops on generated-tree replacement ambiguity; `X3` stops if a finding needs authority outside the exact follow-up scope or changes HCR-001.
- `planned_stop_points`: none before the typed post-implementation close route.
- `task_ordering_rationale`: repair and prove authored authority first, refresh projections second, then run complete acceptance and final review over the converged tree.

Expected continuous range after approval: `E1 = FRF-010..FRF-030`.

## Recovery

`default_failure_policy: fix_forward`. Preserve failing oracle and review evidence, repair only inside the active task touch set, and rerun the narrow and declared checks. Do not synthesize rollback. An observed `ledger-durability-unknown`, artifact digest drift, generated replacement ambiguity, or required scope expansion stops with evidence and no blind retry.

## Truth Sync Handoff

`truth_sync_required: false`, `stable_truth_refs: []`, and docs-governance predicates: `none`. Existing stable truth already states the intended HCR-001 behavior; this follow-up brings runtime and generated projections into conformance without changing durable project claims. After successful implementation, the harness routes to close approval rather than truth sync.
