<!-- Archived historical command wrapper; not an active plugin surface. -->
---
description: Compile an approved design into an execution-grade plan, run bounded agent-native review, and hold for human approval
argument-hint: "<approved-design-path> [--plan <path>]"
allowed-tools: ["Agent", "Read", "Glob", "Grep", "Bash", "Edit", "MultiEdit"]
---

Use `coding:plan-change`.

Validate the approved upstream design with `bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-change/scripts/harness/design-runner.sh"` and machine-check that its `approval_status: approved`. Write an execution-grade `plan_contract_version: 2` plan with strict task metadata, `Work Package Readiness`, `Execution Continuity`, `confirmation_clearance`, `continuous_after_plan_approval` when cleared, a `Recovery` section with `default_failure_policy: fix_forward`, review and human gates, and `approval_status: pending`. Each task declares `failure_policy: fix_forward | stop_and_diagnose | guarded_rollback` plus `parallel_group`, `parallel_policy: forbidden | allowed | required`, `delegation_policy: forbidden | allowed | preferred`, `execution_profile: deep | balanced | fast`, `reasoning_profile: deep | standard | light`, `isolation`, and `resource_locks`. Add a `Rollback` section only for guarded-rollback tasks with exact trigger, target, and verification. Use `coding:executable-oracle-architecture-selector` for non-trivial behavior. The readiness summary must expose `C0` when no confirmation remains. Validate the result with `bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-change/scripts/harness/plan-runner.sh"`.

Use `semantic-routing` as the default model policy for eligible delegated work and keep reusable plans free of concrete provider model identifiers. An execution-time `inherit-main` override changes worker model and reasoning binding only, never the approved dependencies or serial/parallel topology. Parallel groups require explicit human approval, dependency freeze, disjoint write and resource-lock sets, isolated worktrees for writes, an exact batch record whose `batch_id`, `tasks`, per-batch limit, and `convergence_task` match the task DAG, controller-owned convergence, evidence-bearing serial fallback for `allowed`, and a typed capacity stop for unavailable `required` work.

Run mandatory plan review through `coding:review-change`. Construct a bounded plan brief and prefer one reviewer subagent for non-trivial review; review directly when small or delegation is unavailable. The reviewer returns candidate findings only. The main agent adjudicates them and repairs only accepted current-milestone blockers.

After validation and review pass, report `C*`, `E*`, and `X*` execution readiness and stop at the explicit human approval gate. Only explicit approval changes `approval_status` to `approved` and allows `coding:implement-change`.
