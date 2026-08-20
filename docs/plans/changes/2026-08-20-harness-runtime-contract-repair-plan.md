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
task_id = "HCR-010"
depends_on = []
verification_commands = ["uv run pytest src/runtime/harness/tests/test_v3_artifacts.py src/runtime/harness/tests/test_v4_artifacts.py -q", "uv run ruff check src/runtime/harness/__init__.py src/runtime/harness/artifacts.py src/runtime/harness/tests/test_v3_artifacts.py src/runtime/harness/tests/test_v4_artifacts.py", "uv run ty check src/runtime/harness"]
scope_slice = "Introduce artifact contract version 4 with exact-byte parsing, exact structural headings, safe repository references, truth-impact coupling, and complete task and named-batch compilation while retaining the strictly bounded version-3 read and post-convergence completion path required by HCR-001."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["artifact-contract", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Red-first artifact tests reproduce F1, F3, F6, F7, and F9 before the runtime edit and their failing evidence is retained in the execution result.", "Version-4 design and plan matrices reject truth mismatch, invalid stable-truth cardinality, contradictory task metadata, incomplete or inconsistent named batches, unsafe paths, invalid UTF-8, substring headings, fenced-code headings, and exact-byte digest drift.", "Version-3 artifacts remain readable only for immutable evidence and digest checks plus truth-sync or close evaluation for work already converged before refresh; initialization, mutation, repair, admission, and binding are rejected by explicit tests."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/__init__.py", "src/runtime/harness/artifacts.py"]
test_file_refs = ["src/runtime/harness/tests/test_v3_artifacts.py", "src/runtime/harness/tests/test_v4_artifacts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "HCR-020"
depends_on = ["HCR-010"]
verification_commands = ["uv run pytest src/runtime/harness/tests/test_ledger.py src/runtime/harness/tests/test_v4_ledger.py -q", "uv run ruff check src/runtime/harness/ledger.py src/runtime/harness/tests/test_v4_ledger.py", "uv run ty check src/runtime/harness"]
scope_slice = "Make the version-4 ledger the sole owner of ready-set admission, immutable serial or batch provenance, attempt-local eligibility, retained review and external evidence history, safe changed-path containment, and typed durable-write outcomes."
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
done_when = ["Red-first version-4 ledger tests reproduce F1, F2, F5, and the changed-path half of F7 before implementation and retain their failing evidence without editing the external-touch cleanup already present in test_ledger.py.", "Admission model tests cover dependency readiness, approved membership, resource and write conflicts, effective width and capacity, allowed serialization, required-capacity stop, immutable provenance, and caller or backend invariance.", "Rejected review is the only repair-reopen path; every active-attempt eligibility pointer is cleared while immutable per-attempt verification, review, external chain, and batch provenance remain auditable and cannot satisfy the next attempt.", "Fault injection distinguishes pre-promotion failure, confirmed restoration, and ledger-durability-unknown after directory-open, promotion, directory-fsync, restoration, and restoration-fsync failures without blind retry or authority ambiguity."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["src/runtime/harness/ledger.py"]
test_file_refs = ["src/runtime/harness/tests/test_v4_ledger.py"]
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

This is the final version-3 bootstrap plan for the approved design `2026-08-20-harness-runtime-contract-repair-design.md` at SHA-256 `d43af0d7df1f60dfedcb8cb7a4f9c91586ab15431db42a8cf04dc379bd641c1c`. The user authorized mandatory review-design followed directly by plan-change; that authorization approved HCR-001 as the design boundary but does not approve implementation. This plan therefore remains `approval_status = "pending"` through machine validation and mandatory review-plan. `plan_contract_version: 2`, `default_runtime_model_policy: semantic-routing`, and `parallel_execution_approved: false` govern its portable execution shape without adding fields that the final version-3 bootstrap compiler cannot read.

## Implementation

Six controller-owned tasks execute serially from one dependency-frozen baseline. HCR-010 introduces the versioned artifact and compiler contract and covers F1 task and batch validation, F3 truth coupling, F6 byte identity, F7 safe repository references, and F9 exact headings. HCR-020 makes the ledger own admission, attempt history, safe changed-path assertion, and durable persistence for F1, F2, F5, and F7. HCR-030 binds only admitted work and hardens review-brief identity for F1 and F8. HCR-040 restores Python classification and next-phase operations from canonical contracts for F4. HCR-050 synchronizes stable truth, workflow authors, copied resources, and generated root-flat output. HCR-060 performs read-only aggregate acceptance.

Each behavior task records a failing focused oracle before changing authored runtime code. The controller repairs only inside that task's declared scope, reruns its narrow oracle, and advances the next dependency only after convergence. HCR-060 never absorbs a repair: a failure is attributed to HCR-010 through HCR-050 and fixed in that owning slice before aggregate acceptance is rerun. No task creates a new persisted implementation-language boundary; the approved design extends the existing Python harness and its existing Python distribution generator, so no language-decision metadata is needed.

The current working tree already contains the separately reviewed external-touch cleanup. Before HCR-010 mutates the repository, the controller records its exact path and digest baseline and checks the approved bootstrap design, this plan, and the final version-3 ledger with the pre-refresh installed runtime. HCR tasks compute their diff relative to that baseline. Only HCR-050 may mechanically refresh the six generated copies so both authored changes coexist; the controller must not restore or reinterpret any deleted external-touch surface.

## Work Package Readiness

- `milestone_objective`: restore the nine approved lifecycle invariants F1-F9 and leave one executable, versioned Python harness contract that cannot downgrade new work to version 3 after refresh.
- `non_goals`: no S1-S6 follow-up simplification; no new dependency, provider-specific model identifier, external-file mutation, plugin install or cache refresh, commit, push, release, truth-sync approval, close approval, live Herdr action, or change to the 39-skill and six-runtime-owner topology.
- `future_phase`: S1-S6 simplification candidates remain a separate post-repair audit only after version-4 correctness, generated closure, and stable truth converge; a general schema framework or version 5 requires a new persisted authority-shape trigger and a new design.
- `decision_status`: `ready_for_review`; HCR-001 is approved and no repository evidence invalidates its demand, constraint, owner, hard requirement, or upgrade trigger.
- `oracle_strategy`: model and state-transition testing for admission, attempts, and recovery; schema and contract conformance for artifacts, tasks, batches, and truth scope; test-first examples for digest, path, heading, and review-brief boundaries; deterministic fault injection for ledger durability; characterization against canonical lifecycle contracts and the retired Shell behavior; generated and standalone-closure parity for distribution.
- `acceptance_oracles`: red-first reproductions for F1-F9; valid and invalid version-4 matrices; explicit version-3 mutation and admission rejections; admission and repair state models; persistence fault injection; CRLF, invalid UTF-8, unsafe path, symlink, swap-race, exact-heading, and fenced-code negatives; source and copied classification matrices; generated parity; Ruff; ty; pytest; aggregate `scripts/check.sh`; both plugin validators; immutable Markdown; and `git diff --check`.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: 2, consisting of one bounded implementation review, one controller-owned batched repair if accepted findings exist, and one focused verification review.
- `subagent_ready`: false; all writable slices share one version transition, one dirty-tree attribution boundary, and one generated convergence point, so implementation remains main-executor serial work.

## Architecture Decision HCR-001

`architecture_decision_ref: HCR-001 Versioned Admission Instead Of In-Place Version-3 Drift`. The reversible increments are HCR-010 for parse and compile authority, HCR-020 for ledger state and durability, HCR-030 for runtime binding and review evidence, HCR-040 for classification and copied contract resources, HCR-050 for stable truth and generated convergence, and HCR-060 for read-only acceptance. Each increment has a narrow executable oracle and preserves a safe stop before the next authority layer consumes it.

The approved upgrade trigger is another persisted authority-shape change, not an ordinary validation addition. Evidence that canonical lifecycle contracts cannot be normalized into standalone bundles, that version-3 post-convergence truth-sync or close cannot be isolated from task mutation, or that the pre-refresh bootstrap ledger is unavailable before convergence returns `needs_design_decision`; it does not authorize an inline compatibility layer, plan digest exception, or provider-specific workaround.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0` — no confirmation remains beyond explicit approval of this reviewed plan. That approval authorizes HCR-010 through HCR-060 continuously inside their declared repository scopes; it does not authorize install, commit, push, release, truth-sync approval, or close approval.
- `runtime_contingencies`: `X1` stops before mutation if the separately attributable external-touch baseline has drifted since plan review or cannot be preserved through HCR diff attribution; `X2` stops and diagnoses if the pre-refresh installed runtime or final version-3 bootstrap ledger is lost, corrupted, or refreshed before this repair converges; `X3` stops mutation and preserves recovery evidence if live execution returns `ledger-durability-unknown`; `X4` stops HCR-050 and preserves both trees and all replacement evidence if generated-tree promotion or restoration leaves ownership ambiguous, with no retry, restore, or dependent execution until diagnosis proves one durable tree.
- `planned_stop_points`: empty on the normal path; successful HCR-060 stops only at the separate truth-sync human gate required by the high truth impact.
- `task_ordering_rationale`: establish the artifact and compiler boundary first, then make the ledger own valid state, bind only ledger-admitted work, restore contract-driven lifecycle operations, synchronize human and generated truth, and run full acceptance last. This order prevents downstream code from inventing authority that an upstream compiler or ledger has not yet made executable.

## Recovery

`default_failure_policy: fix_forward`. Ordinary compile, test, type, pre-promotion generation, parity, documentation, or plugin-validation failures are diagnosed and repaired inside the owning HCR task, followed by its focused oracle and every invalidated dependent oracle. Generated output is built and validated through the repository's staged root-flat workflow and is never hand-edited. Promotion or restoration ambiguity is X4, not an ordinary generation failure: HCR-050 preserves both candidate trees and replacement evidence and performs no retry or restoration until diagnosis proves the durable owner. No task has guarded rollback authority, and no broad Git restore may overwrite the external-touch baseline or user changes. X1, X2, X3, and X4 are evidence-preserving stop-and-diagnose contingencies, not retry or rollback hooks.

The bootstrap version-3 design, plan, and ledger remain under the pre-refresh installed runtime until implementation review converges. If their digest changes unexpectedly, stop and reconstruct evidence from the dependency-frozen pre-change revision rather than editing approved artifacts in place. The repository runtime may be refreshed or consumed only in a later separately authorized installation action.

## Truth Sync Handoff

`truth_sync_required = true`; `stable_truth_refs = ["README.md", "docs/architecture", "docs/changelog/design-decisions.md"]`. The stable updates record the version-4 artifact, admission, attempt, durability, trust, classification, and standalone-resource contract; the exact version-3 compatibility boundary; and HCR-001. `docs_governance_predicates = ["ownership", "truth-root", "canonical-terminology"]`: README remains the human overview, stable workflow truth stays under `docs/architecture`, the architecture decision is recorded in the changelog, and this stage plan remains non-canonical under `docs/plans/`. Truth sync and its approval occur only after verified implementation and mandatory implementation review.
