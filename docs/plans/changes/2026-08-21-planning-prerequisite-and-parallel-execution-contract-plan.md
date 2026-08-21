+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-21-planning-prerequisite-and-parallel-execution-contract-design.md"
design_sha256 = "43d004a729b38f79384dbc14e7ad48b6573a53e7d4eca333d1d8ae476aca1729"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md"]
default_runtime_model_policy = "semantic-routing"
parallel_execution_approved = false

[scope]
impl_file_refs = ["docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "skills/implement-change/SKILL.md", "skills/implement-change/references/repair-loop.md", "skills/implement-change/references/workflow.toml", "skills/plan-change/SKILL.md", "src/skills/workflows/implement-change/SKILL.md", "src/skills/workflows/implement-change/references/repair-loop.md", "src/skills/workflows/implement-change/references/workflow.toml", "src/skills/workflows/plan-change/SKILL.md"]
test_file_refs = ["tests/test_parallel_execution_contracts.py", "tests/test_skill_workflow_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "PPC-010"
depends_on = []
verification_commands = ["uv run pytest tests/test_parallel_execution_contracts.py tests/test_skill_workflow_contracts.py -q", "bash scripts/check.sh", "git diff --check"]
scope_slice = "Make manual external setup a pre-planning admission gate and make approved safe development batches use maximal available concurrency with evidenced serial fallback."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["workflow-skill-contract", "generated-skill-tree"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Planning returns manual_checkpoint and not_ready before task decomposition when required external setup cannot be automated inside existing authority.", "Eligible approved development batches select maximal safe ready width and allowed serialization requires exact limiting evidence.", "Structured contract tests, generated root-flat parity, aggregate validation, and bounded implementation review pass."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "skills/implement-change/SKILL.md", "skills/implement-change/references/repair-loop.md", "skills/implement-change/references/workflow.toml", "skills/plan-change/SKILL.md", "src/skills/workflows/implement-change/SKILL.md", "src/skills/workflows/implement-change/references/repair-loop.md", "src/skills/workflows/implement-change/references/workflow.toml", "src/skills/workflows/plan-change/SKILL.md"]
test_file_refs = ["tests/test_parallel_execution_contracts.py", "tests/test_skill_workflow_contracts.py"]
external_impl_file_refs = []
+++
# Plan

## Implementation

Treat the already-authorized correction as one bounded main-controller task because the authored skill files, generated projections, structured workflow contract, and contract tests form one atomic source-generated behavior change. Preserve the existing runtime state machine and human approval boundaries while making the model-visible policy unambiguous.

This artifact normalizes the user's direct correction request into the version-4 evidence package required for truth sync and close. It does not claim additional implementation authority or introduce work beyond the current diff.

## Work Package Readiness

- `milestone_objective`: front-load non-automatable external setup before implementation planning and actively use maximal safe concurrency inside approved development batches.
- `non_goals`: no external account or login action, secret handling, provider mutation, new parallel-policy enum, runtime scheduler rewrite, plugin reinstall, release version change, deployment, or publication.
- `future_phase`: add runtime observability only if real executions show that controllers misreport effective capacity despite the structured contract and ledger evidence.
- `decision_status`: `ready_for_review`.
- `oracle_strategy`: machine-readable TOML contract assertions, source-to-generated parity, focused workflow tests, aggregate repository validation, and bounded diff review.
- `acceptance_oracles`: the task verification commands and direct main-agent implementation review of the exact task diff.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: `2`, one initial bounded review and one focused verification review only if repair becomes necessary.
- `subagent_ready`: `false`; this is one coupled source-generated contract slice and the user did not request delegated execution.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0`; the user directly requested the correction and later explicitly approved truth sync, close, smart commit, and push.
- `runtime_contingencies`: `X1` stops on source-generated drift, contract-test failure, aggregate-check failure, or an unsafe tracked file discovered before commit.
- `planned_stop_points`: none.
- `task_ordering_rationale`: update authored owners first, refresh generated projections, verify the machine-readable contract and complete repository, then synchronize stable truth and close before commit and push.

Expected continuous range after approval: `E1 = PPC-010`.

## Recovery

`default_failure_policy: fix_forward`. Repair only the authored skill, structured contract, generated projection, tests, or stable truth inside the declared scope and rerun the narrow oracle followed by aggregate validation. Do not add automatic rollback or weaken existing parallel-safety and human-approval requirements.

## Truth Sync Handoff

`truth_sync_required: true`. Stable truth refs are `docs/architecture/workflow-orchestration.md` and `docs/changelog/design-decisions.md`. Docs-governance predicate: `none`; this change updates bounded current-state facts and records one durable decision without reorganizing truth roots, search boundaries, stage placement, canonical terminology, or prose structure.

## Review Gate

- `required_entry`: `review-change`
- `review_component`: `review-plan`
- `actor_role`: `main`
- `review_depth`: `boundary`
- `review_status`: `passed`
- `candidate_findings`: none
- `review_evidence`: Direct review was selected because the task is one small coupled contract slice and delegation was neither requested nor useful. The plan preserves the distinction between planning admission and implementation work, keeps DAG independence necessary but insufficient for concurrency, retains named-batch human approval and safety constraints, and declares exact source, generated, test, truth, verification, and recovery boundaries.
