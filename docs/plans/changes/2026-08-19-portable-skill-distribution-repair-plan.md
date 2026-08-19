+++
artifact_kind = "plan"
contract_version = 3
design_ref = "2026-08-19-portable-skill-distribution-repair-design.md"
design_sha256 = "2eea25beed0fe6199e857a8d85358cb2dbfcc66aa90d1297f2205f089be7e83b"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["AGENTS.md", "README.md", "docs/architecture", "docs/changelog/design-decisions.md"]

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "pyproject.toml", "contracts", "docs/architecture", "docs/changelog/design-decisions.md", "hooks/pre-commit", "scripts", "skills", "skills.index.json", "src", "runtime"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PDR-010"
depends_on = []
verification_commands = ["python3 src/runtime/harness/cli.py design validate docs/plans/changes/2026-08-19-portable-skill-distribution-repair-design.md", "python3 src/runtime/harness/cli.py plan validate docs/plans/changes/2026-08-19-portable-skill-distribution-repair-plan.md", "uv run pytest tests/test_runtime_distribution_contracts.py -k 'authored or source_runtime or retired'"]
scope_slice = "Restore nested authored skills and relocate the accepted Python harness to its authored source boundary without restoring retired Shell or compatibility surfaces."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["authored-skill-tree", "python-harness-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["All 39 retained flat skills have exactly one mapped authored source directory.", "The Python runtime imports and direct CLI execution work from src/runtime/harness.", "The three retired skill IDs and old Shell runtime remain absent."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["pyproject.toml", "src", "runtime", "skills"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PDR-020"
depends_on = ["PDR-010"]
verification_commands = ["python3 scripts/flatten-skills.py --target root-flat --check", "python3 scripts/check-install-surface.py", "python3 scripts/check-contracts.py", "uv run pytest tests/test_install_target_contracts.py tests/test_runtime_distribution_contracts.py -k 'generator or generated or runtime_bundle or failure_preserves'"]
scope_slice = "Restore one root-flat generator and contracts that derive the 39 public skills plus six exact skill-local Python runtime bundles from authored sources."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["distribution-generator", "skill-contract", "generated-skill-tree"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["root-flat is the sole materialization target and neither generator nor checker reads or writes .dist.", "Generated skills equal authored content, provider projection, and the exact production runtime manifest with no missing or extra files.", "A failed generation preserves the prior skills tree byte-for-byte."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts", "scripts/flatten-skills.py", "scripts/check-install-surface.py", "scripts/check-contracts.py", "scripts/skill_activation.py", "skills", "skills.index.json"]
test_file_refs = ["tests/test_install_target_contracts.py", "tests/test_runtime_distribution_contracts.py", "tests/test_skill_activation_contracts.py", "tests/test_skill_consolidation_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PDR-030"
depends_on = ["PDR-020"]
verification_commands = ["python3 scripts/generate-skills-index.py --check", "python3 scripts/generate-workflow-diagrams.py --check", "uv run pytest tests/test_check_orchestration.py tests/test_command_retirement_contracts.py tests/test_runtime_distribution_contracts.py", "python3 src/skills/disciplines/organize-docs/scripts/normalize-markdown-prose.py --root . --immutable-manifest contracts/markdown-prose.toml --mode check"]
scope_slice = "Converge skill-local runtime invocations, thin serial validation, generated views, and stable distribution truth on the restored source and root-flat boundary."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["lifecycle-skill-contract", "aggregate-check", "stable-docs"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Each runtime owner invokes only its own scripts/harness/cli.py and passes from an unrelated copied directory.", "The aggregate checker invokes each owned generator or checker once and one pytest lane.", "Index, diagrams, documentation, and Markdown oracles match the restored distribution contract."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture", "docs/changelog/design-decisions.md", "hooks/pre-commit", "scripts/check.sh", "scripts/generate-skills-index.py", "scripts/generate-workflow-diagrams.py", "src/skills", "skills", "skills.index.json"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PDR-040"
depends_on = ["PDR-030"]
verification_commands = ["bash scripts/check.sh", "claude plugin validate .", "uvx --with pyyaml python /Users/csheng/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .", "git diff --check"]
scope_slice = "Run bounded implementation review and final local acceptance for the corrected standalone distribution without installing, publishing, committing, or closing the change."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["repository-acceptance"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The accepted design, plan, generated closure, plugins, Python runtime, contracts, tests, and Markdown gates pass.", "No unauthorized external write or lifecycle action has occurred.", "Any accepted review finding is repaired and focused verification is rerun."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "pyproject.toml", "contracts", "docs/architecture", "docs/changelog/design-decisions.md", "hooks/pre-commit", "scripts", "skills", "skills.index.json", "src", "runtime"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []
+++
# Plan

The user's 2026-08-19 instruction to implement PDR-001 authorizes this exact serial correction after mandatory plan review. It also carries forward the previously approved development-tool cache prefixes under `~/.cache/uv/market-csheng-harness`, `~/.cache/uv-projects/market-csheng-harness`, `~/.cache/ruff/market-csheng-harness`, `~/.cache/python/market-csheng-harness`, and `~/.cache/pytest/market-csheng-harness`. It does not authorize any other external write, commit, push, plugin installation, publication, truth-sync approval, or close approval.

## Implementation

Use contract, characterization, and golden oracles for source-to-generated parity and standalone skill closure. Build every generated tree in a temporary sibling, validate it, and atomically replace the tracked root-flat tree only after success. Preserve the accepted Python runtime and current flat skill changes as migration inputs; do not recover by broadly restoring the pre-cutover Shell implementation.

The controller owns all four serial tasks in the current checkout because they mutate one coupled source, contract, generator, and generated-tree boundary. The review budget is one bounded design review, one bounded plan review, and one bounded implementation review with controller-owned repair.

## Work Package Readiness

- milestone objective: Restore nested authored skills and standalone generated lifecycle skills without undoing the accepted Python, codex-native, compatibility-retirement, checker, or Markdown work.
- non-goals: Restore the Shell harness, the three retired skill IDs, three-run user comparison, provider-specific `.dist` payloads, hand-maintained runtime copies, or a separately published runtime dependency; install plugins; commit; push; publish; approve truth sync; approve close.
- future phase: Consider a separately versioned runtime only if measured generated package size or update cost materially harms a supported installation path.
- architecture decision ref: PDR-001 source sharing plus distribution closure.
- decision status: ready_for_review.
- oracle strategy: Contract and golden parity for authored-to-generated skill trees, selected-skill copy characterization from an unrelated directory, failure injection for transactional whole-tree generation, and focused Python plus aggregate repository gates.
- acceptance oracles: Exactly 39 contract entries map to 39 nested authored directories and 39 root-flat generated directories; exactly six contract-declared owners receive no-missing-or-extra production Python runtime bundle; every copied owner CLI runs independently; `.dist` is untouched; failed generation preserves the preceding tree byte-for-byte; retired IDs and Shell runtime remain absent; the aggregate checker invokes each owner once; both plugin validators and immutable Markdown checks pass.
- maximum review batches: One bounded implementation review, one batched controller repair if needed, and one focused verification review.
- subagent ready: false; the coupled dirty-tree repair remains controller-owned and serial.

## Execution Continuity

- execution mode: continuous_after_plan_approval.
- confirmation clearance: C0 is satisfied by the user's 2026-08-19 implementation instruction for the exact repository touch set and five inherited tool-cache prefixes above.
- runtime contingencies: Stop with `blocked_source_baseline` for unexplained overlapping changes, `needs-design-decision` if standalone closure requires a dependency outside the skill directory, `needs-plan-change` for a path or external write outside the approved set, and `non-convergent` if one focused same-slice repair cannot satisfy transactional generation or closure oracles.
- planned stop points: None inside PDR-010 through PDR-040. Successful local acceptance stops at the separate truth-sync approval gate.
- task order rationale: Establish one authored tree and runtime first, then generate and validate the complete flat closure transactionally, then converge consumers and stable views, and finally run one aggregate acceptance and bounded implementation review.

## Reversible Increments And Upgrade Trigger

PDR-010 establishes the authored source boundary while preserving the current flat tree as migration input. PDR-020 builds and validates a complete temporary root-flat tree before the atomic swap. PDR-030 updates consumers and generated views against the valid new tree. PDR-040 performs local acceptance without installation or publication. Reconsider PDR-001 only when measured generated package size or update cost materially harms a supported installation path.

## Recovery

Fix forward is the default. Whole-tree generation stages and validates in a temporary sibling directory. Validation failure leaves the current `skills/` tree untouched. Replacement failure restores the immediately preceding tree before returning an error, and the focused failure-injection oracle compares that tree byte-for-byte. Do not use broad Git restore, regenerate `.dist`, restore retired compatibility IDs, or reintroduce the Shell harness as recovery.
