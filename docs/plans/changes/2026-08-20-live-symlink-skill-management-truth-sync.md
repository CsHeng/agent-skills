+++
artifact_kind = "truth-sync"
contract_version = 4
execution_result_ref = "2026-08-20-live-symlink-skill-management-execution-result.json"
execution_result_sha256 = "95c9c7d2f75c4d83ce69bcbd7f5a5cac63bc3fea9cee4a8bfb5488d3e59fe6a1"
ledger_ref = "2026-08-20-live-symlink-skill-management-ledger.json"
ledger_sha256 = "2f0a6ed345cda48b4e7563a5db01cb12aff92fd1ca704890f29404985d9da2df"
approval_status = "approved"

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = []
external_impl_file_refs = []
+++
# Truth Sync

## Scope

Confirm that the stable repository truth consistently recommends local Git checkouts plus live per-skill symlinks, retains provider plugins and `npx skills` only as compatibility paths, and records the ordered Grok-before-Claude collision boundary.

## Evidence

- approved_design_ref: `docs/plans/changes/2026-08-20-live-symlink-skill-management-design.md`
- approved_plan_ref: `docs/plans/changes/2026-08-20-live-symlink-skill-management-plan.md`
- review_gate_ref: `review:cfa8ccfdd4c9a742b2408136f5c14fe11a9eed84a5247146b01304346350dc4f:b170e44b3868026974db11d1262dea35300558f467ca20650574d30c625e45e6:lsm-040-direct-review:pass`
- verification_ref: `verification:cfa8ccfdd4c9a742b2408136f5c14fe11a9eed84a5247146b01304346350dc4f:b170e44b3868026974db11d1262dea35300558f467ca20650574d30c625e45e6:scripts-check-281-passed`
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs: `AGENTS.md`, `README.md`, `docs/architecture/harness-state-machine.md`, `docs/architecture/install-surface.md`, `docs/architecture/workflow-orchestration.md`, `docs/changelog/design-decisions.md`, and `docs/quickstart.md`
- stage_artifact_refs: this change's approved design and plan, converged task ledger, immutable execution result, and this pending truth-sync artifact under `docs/plans/changes/`
- summary: Stable truth now makes the generated `skills/` payload plus live child symlinks the recommended local management topology, treats unqualified public IDs as portable identity, keeps plugins and copied `npx skills` installs compatible but non-recommended, and requires duplicate discovery to pass before adding provider-specific links.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: close-change
