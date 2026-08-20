+++
artifact_kind = "plan"
contract_version = 3
design_ref = "2026-08-20-harness-runtime-contract-repair-design.md"
design_sha256 = "d43af0d7df1f60dfedcb8cb7a4f9c91586ab15431db42a8cf04dc379bd641c1c"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["README.md", "docs/architecture", "docs/changelog/design-decisions.md"]

[scope]
impl_file_refs = ["README.md", "contracts", "docs/architecture", "docs/changelog/design-decisions.md", "scripts", "skills", "src/runtime/harness", "src/skills"]
test_file_refs = ["src/runtime/harness/tests", "tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-020"
depends_on = []
verification_commands = ["uv run pytest src/runtime/harness/tests/test_ledger.py src/runtime/harness/tests/test_v4_ledger.py -q", "uv run ruff check src/runtime/harness/ledger.py src/runtime/harness/tests/test_ledger.py src/runtime/harness/tests/test_v4_ledger.py", "uv run ty check src/runtime/harness"]
scope_slice = "Make the version-4 ledger the sole owner of ready-set admission, immutable serial or batch provenance, attempt-local eligibility, retained review and external evidence history, safe changed-path containment, typed durable-write outcomes, and strict version-3 mutation rejection; migrate the existing ledger tests without altering their pre-existing external-touch cleanup hunks."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["ledger-state-machine", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The retained HCR-010 red evidence and the new version-4 ledger red suite prove the v3 rejection and v4 state boundary before ledger implementation.", "test_ledger.py is migrated from mutable version-3 expectations to the strict read-only compatibility boundary while the baseline-captured external-touch helper changes remain byte-identical within that file.", "Admission tests cover dependency readiness, approved membership, resource and write conflicts, effective capacity, allowed serialization, required-capacity stop, immutable provenance, and caller invariance.", "Rejected review archives complete per-attempt verification, review, external chain, and provenance before clearing active eligibility; durability fault injection distinguishes confirmed restoration from ledger-durability-unknown."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/ledger.py"]
test_file_refs = ["src/runtime/harness/tests/test_ledger.py", "src/runtime/harness/tests/test_v4_ledger.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-030"
depends_on = ["HCR-020"]
verification_commands = ["uv run pytest src/runtime/harness/tests/test_binding.py src/runtime/harness/tests/test_cli_operations.py -q", "uv run ruff check src/runtime/harness/binding.py src/runtime/harness/cli.py src/runtime/harness/tests/test_binding.py src/runtime/harness/tests/test_cli_operations.py", "uv run ty check src/runtime/harness"]
scope_slice = "Bind execution only from ledger-derived version-4 admission and harden bounded-review brief reads to a regular non-symlink descriptor with stable identity and digest verification while enforcing the HCR-001 version gates at the CLI boundary."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["runtime-binding", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Red-first binding and CLI tests reproduce caller-substituted admission, symlink review briefs, file-swap races, and forbidden version-3 binding before implementation.", "Binding accepts only the active ledger-owned serial or named-batch admission identity and cannot rewrite task topology, locks, isolation, touch sets, or oracles.", "Review briefs are hashed and read from one validated regular-file descriptor; symlink, non-regular file, identity drift, content drift, and unsupported-platform fallback races return typed failures before envelope emission."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/binding.py", "src/runtime/harness/cli.py"]
test_file_refs = ["src/runtime/harness/tests/test_binding.py", "src/runtime/harness/tests/test_cli_operations.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-040"
depends_on = ["HCR-030"]
verification_commands = ["uv run pytest src/runtime/harness/tests/test_lifecycle.py src/runtime/harness/tests/test_cli_operations.py tests/test_runtime_distribution_contracts.py::RuntimeDistributionContractTests::test_runtime_bundles_project_canonical_lifecycle_resources -q", "uv run ruff check src/runtime/harness scripts/skill_distribution.py src/runtime/harness/tests/test_lifecycle.py src/runtime/harness/tests/test_cli_operations.py tests/test_runtime_distribution_contracts.py", "uv run ty check src/runtime/harness scripts/skill_distribution.py"]
scope_slice = "Restore complete deterministic request-classification and next-phase operations in Python from normalized projections of the canonical lifecycle, workflow-mode, and routing contracts and extend the runtime-bundle manifest and generator so all six standalone owners receive the minimum required resources."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["lifecycle-routing-contract", "distribution-generator", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Red-first characterization tests reproduce F4 by showing that the current Python runtime has no complete classification or phase-transition operation.", "The new lifecycle module rejects unknown or contradictory typed requests and returns one deterministic mode, initial phase, owner, next phase, or terminal stop from repository-owned contracts without a hand-maintained Python rule table.", "Source and copied-runtime tests exercise the same classification and phase matrices and prove every generated owner-local resource equals its canonical normalized projection; no standalone bundle reaches outside its installed skill directory."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts/runtime-bundles.toml", "scripts/skill_distribution.py", "src/runtime/harness/__init__.py", "src/runtime/harness/cli.py", "src/runtime/harness/lifecycle.py"]
test_file_refs = ["src/runtime/harness/tests/test_cli_operations.py", "src/runtime/harness/tests/test_lifecycle.py", "tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-050"
depends_on = ["HCR-040"]
verification_commands = ["python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/generate-workflow-diagrams.py", "uv run pytest src/runtime/harness/tests tests/test_runtime_distribution_contracts.py tests/test_skill_workflow_contracts.py tests/test_skill_routing_contracts.py tests/test_check_orchestration.py -q", "python3 scripts/flatten-skills.py --target root-flat --check", "python3 scripts/generate-skills-index.py --check", "python3 scripts/generate-workflow-diagrams.py --check"]
scope_slice = "Update stable runtime and workflow truth for artifact and ledger version 4, the strict version-3 compatibility boundary, restored classification and routing, and HCR-001; then regenerate the tracked root-flat skills and validate source-to-generated closure while preserving the separate external-touch cleanup."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["stable-docs", "lifecycle-skill-contract", "generated-skill-tree"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["README, the stable architecture domain, and the design-decision changelog describe version-4 authority, the exact version-3 compatibility boundary, lifecycle contract ownership, durability stops, and HCR-001 without promoting stage artifacts to stable truth.", "The six runtime-owning workflow skills author and consume the version-4 contract consistently and retain human approval, truth-sync, and close gates.", "Generated skills equal authored skill content plus the exact runtime-bundle manifest, including normalized lifecycle resources, with no missing, stale, or extra files.", "The pre-existing external-touch cleanup remains byte-identical except for the one mechanical generated refresh that combines its already-authored runtime state with this approved source state; no retired external-touch path, checker, fixture, golden, or vacuous test is restored."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["README.md", "docs/architecture", "docs/changelog/design-decisions.md", "skills", "src/skills/workflows/close-change/SKILL.md", "src/skills/workflows/design-change/SKILL.md", "src/skills/workflows/implement-change/SKILL.md", "src/skills/workflows/plan-change/SKILL.md", "src/skills/workflows/review-change/SKILL.md", "src/skills/workflows/sync-truth/SKILL.md"]
test_file_refs = ["src/runtime/harness/tests", "tests/test_check_orchestration.py", "tests/test_runtime_distribution_contracts.py", "tests/test_skill_routing_contracts.py", "tests/test_skill_workflow_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-060"
depends_on = ["HCR-050"]
verification_commands = ["bash scripts/check.sh", "claude plugin validate .", "uvx --with pyyaml python /Users/csheng/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .", "git diff --check"]
scope_slice = "Run the complete read-only local acceptance lane for the converged repair; any failure routes back to the owning prior task and cannot widen this verification task into a repair surface."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "shared-read-only"
resource_locks = ["repository-acceptance"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The aggregate contract, index, diagram, Ruff, ty, pytest, Markdown, runtime-bundle, and standalone-closure lanes pass from the converged tree.", "Both Claude and Codex plugin validators pass without installing, updating, publishing, committing, pushing, or closing the change.", "git diff --check passes and the final diff contains only the approved HCR repair plus the separately attributable pre-existing external-touch cleanup."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = []
test_file_refs = []
external_impl_file_refs = []
+++
# Plan

This resume plan is the minimal `needs-plan-change` repair discovered while executing HCR-020. The approved predecessor plan and frozen predecessor ledger retain HCR-010 green verification and converged artifact/compiler state. The separately hashed resume-evidence artifact retains the controller-observed HCR-010 and HCR-020 red results and the exact source identities at the typed stop. The predecessor entered HCR-020 and stopped before changing `ledger.py` because its task write set excluded the existing v3 mutation tests that must migrate for the approved strict compatibility boundary. This plan remains `approval_status = "pending"`; it does not reinterpret the predecessor approval.

## Predecessor Evidence

- `design_ref`: `docs/plans/changes/2026-08-20-harness-runtime-contract-repair-design.md`; `sha256`: `d43af0d7df1f60dfedcb8cb7a4f9c91586ab15431db42a8cf04dc379bd641c1c`.
- `predecessor_plan_ref`: `docs/plans/changes/2026-08-20-harness-runtime-contract-repair-plan.md`; `sha256`: `495f665c17df831d9b3a5239baa3127c393d3bef3b4e7725ee1f15cd0ed0a4ca`.
- `predecessor_ledger_ref`: `docs/plans/changes/2026-08-20-harness-runtime-contract-repair-ledger.json`; frozen `sha256`: `d7d4bb970e31840f095de24cb4039a8d47678a11cc61405f5e1c2dc4a187019c`.
- `preexisting_baseline_ref`: `docs/plans/changes/2026-08-20-harness-runtime-contract-repair-preexisting-baseline.json`; `sha256`: `764e623cf766ce7096fd498d3adef0581a377ab8ffc9c9155ccdb514f8a93b33`.
- `resume_evidence_ref`: `docs/plans/changes/2026-08-20-harness-runtime-contract-repair-resume-evidence.json`; `sha256`: `382d4dc513c33c6c8256ab665a0c126820777f32e0fda00918ef4056efc4752a`.
- `pre_initialization_oracle`: before initializing a resume ledger, verify all five digests; verify the predecessor ledger states HCR-010 `converged`, HCR-020 `in-progress`, and HCR-030 through HCR-060 `pending`; verify every HCR-010 implementation and test scope file, `ledger.py`, and both HCR-020 test files match the hashes in the resume-evidence artifact. Any mismatch returns X5 without ledger initialization or source mutation.

## Implementation

`plan_contract_version: 2`, `default_runtime_model_policy: semantic-routing`, and `parallel_execution_approved: false`. HCR-020 resumes from the accepted HCR-010 source state and adds only `src/runtime/harness/tests/test_ledger.py` to its writable test slice. It must preserve the baseline-captured external-touch helper hunks while replacing incompatible version-3 mutation expectations with strict read-only compatibility oracles. HCR-030 through HCR-060 are copied byte-for-byte from the predecessor task records; only removal of converged HCR-010, rebasing HCR-020 to no dependency inside this resume DAG, and the HCR-020 test-scope and migration-oracle repair differ from the predecessor task table.

## Work Package Readiness

- `milestone_objective`: resume the approved F1-F9 repair after correcting the one proven HCR-020 test ownership omission.
- `non_goals`: no change to HCR-001, HCR-010 implementation, F1-F9 scope, runtime topology, dependencies, stable truth scope, external files, installation, commit, push, release, truth-sync approval, or close approval.
- `future_phase`: S1-S6 simplification remains excluded.
- `decision_status`: `ready_for_review`; the live red-oracle conflict proves a plan touch-set omission, not a design change.
- `oracle_strategy`: retain the predecessor model/state, schema/contract, red-first, durability fault-injection, characterization, and generated-parity strategy; add only migration coverage for the existing version-3 ledger tests.
- `acceptance_oracles`: predecessor HCR-010 evidence plus the declared HCR-020 through HCR-060 commands and final aggregate validation.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: 2.
- `subagent_ready`: false.

## Architecture Decision HCR-001

`architecture_decision_ref: HCR-001 Versioned Admission Instead Of In-Place Version-3 Drift`. Reversible increments remain ledger, binding, lifecycle projection, stable/generated convergence, and read-only acceptance. The upgrade trigger remains another persisted authority-shape change. This resume plan changes no architecture demand, owner, boundary, or trigger.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0` — approval of this reviewed resume plan authorizes HCR-020 through HCR-060 with no additional confirmation.
- `runtime_contingencies`: retain X1 external-touch attribution drift, X2 loss or corruption of pre-refresh bootstrap evidence, X3 `ledger-durability-unknown`, and X4 generated-tree promotion ambiguity; X5 stops if the predecessor plan, ledger, HCR-010 source diff, or captured red evidence no longer matches the recorded SHA and task state.
- `planned_stop_points`: empty on the normal path; success stops at the separate truth-sync approval gate.
- `task_ordering_rationale`: migrate ledger tests and authority together, then bind only admitted work, restore lifecycle operations, converge stable/generated truth, and run aggregate acceptance.

## Recovery

`default_failure_policy: fix_forward`. Repair only inside the active task scope and rerun its narrow and invalidated dependent oracles. Do not rewrite or continue the predecessor ledger, weaken v3 rejection, hand-edit generated output, or use broad Git restoration. X1-X5 preserve evidence and stop rather than retry or roll back.

## Truth Sync Handoff

`truth_sync_required = true`; `stable_truth_refs = ["README.md", "docs/architecture", "docs/changelog/design-decisions.md"]`; `docs_governance_predicates = ["ownership", "truth-root", "canonical-terminology"]`. Verified implementation still routes continuously to a pending truth-sync artifact and explicit human truth approval.
