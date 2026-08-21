+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "medium"
truth_sync_required = true

[scope]
impl_file_refs = ["docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "skills/implement-change/SKILL.md", "skills/implement-change/references/repair-loop.md", "skills/implement-change/references/workflow.toml", "skills/plan-change/SKILL.md", "src/skills/workflows/implement-change/SKILL.md", "src/skills/workflows/implement-change/references/repair-loop.md", "src/skills/workflows/implement-change/references/workflow.toml", "src/skills/workflows/plan-change/SKILL.md"]
test_file_refs = ["tests/test_parallel_execution_contracts.py", "tests/test_skill_workflow_contracts.py"]
external_impl_file_refs = []
+++
# Design

## Planning Prerequisite And Parallel Execution Contract

## Problem

Known non-automatable external prerequisites such as account creation, interactive login, MFA enrollment, access grants, or credential provisioning could remain inside an implementation plan and stop otherwise unattended work after execution had begun. Separately, an approved safe parallel batch could be serialized without requiring an observed limiting factor, leaving useful subagent development concurrency discretionary after the plan had already frozen a safe topology.

## Goals

- Make non-automatable external setup a planning-admission condition that must be cleared before task decomposition.
- Return `manual_checkpoint` and `not_ready` without an approval-ready implementation DAG while such a prerequisite remains unresolved.
- Require planning to surface eligible dependency-frozen development batches instead of leaving safe concurrency implicit.
- Require implementation to select the maximal safe ready width for an approved batch and permit allowed-work serialization only with exact limiting evidence.
- Preserve source-first authoring, generated root-flat parity, human plan approval, isolated delegated writes, disjoint write sets and locks, bounded batch width, controller convergence, and typed capacity stops.

## Boundaries

This change does not authorize the agent to create external accounts, complete interactive authentication, handle secret values, obtain access grants, or perform provider mutations without existing scope and authority. It does not treat DAG independence alone as sufficient parallel authority and does not remove named-batch approval, isolation, write-set, lock, capacity, or convergence requirements.

The task-policy vocabulary remains `forbidden | allowed | required`; no new parallel-policy enum is introduced. Runtime ledger and scheduler code already support approved batch admission and recorded serialization, so this slice changes the portable skill and structured workflow contract rather than replacing the runtime state machine.

The user directly authorized the bounded correction on 2026-08-21. This artifact records that existing authority and the verified implementation scope; it grants no new implementation, external, release, or deployment action.

## Acceptance

- `plan-change` rejects unresolved manual external setup before task decomposition and keeps it outside the implementation DAG, planned stops, and runtime contingencies.
- `plan-change` treats DAG independence as necessary but insufficient and proactively declares safe named development batches.
- `implement-change` selects the maximal safe ready width inside an approved group, records any allowed serial fallback reason, and retains a required-capacity typed stop.
- Structured contract tests protect the machine-readable prerequisite and parallel-selection fields without snapshotting natural-language policy text.
- Authored and generated skill surfaces remain equal under the repository generator and the aggregate repository check passes.

## Recovery

Use fix-forward inside the declared source, generated, test, and stable-truth refs. If validation exposes an incomplete invariant, repair the authored skill or structured workflow contract, regenerate the root-flat projection, and rerun the focused and aggregate checks. Do not weaken approval, isolation, touch-set, lock, or capacity safeguards to make the new policy pass.
