+++
artifact_kind = "truth-sync"
contract_version = 4
execution_result_ref = "2026-08-23-routeros-scripting-guidelines-execution-result.json"
execution_result_sha256 = "5f855650f1af90aea88f68601d1367cb381209b33c8dae22e7ea4200ba4a53b3"
ledger_ref = "2026-08-23-routeros-scripting-guidelines-ledger.json"
ledger_sha256 = "ad7b026c544f63df347c52c309ec679a4a3d38b1db00ef778c2197b6f4c8ab15"
approval_status = "approved"

[scope]
impl_file_refs = [
  "AGENTS.md",
  "README.md",
  "contracts/skills.toml",
  "docs/architecture/install-surface.md",
  "docs/architecture/invocation-contract.md",
  "docs/architecture/workflow-orchestration.md",
  "src/skills/policies/routeros-scripting-guidelines/SKILL.md",
  "src/skills/policies/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "src/skills/policies/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "src/skills/policies/routeros-scripting-guidelines/references/language-and-values.md",
  "src/skills/session/use-coding-skills/references/routing.toml",
]
test_file_refs = []
external_impl_file_refs = []
+++
# Truth Sync

## Scope

Synchronize the shared skill catalog, activation contract, current inventory count, and RouterOS scripting policy truth with the verified generated 40-skill payload.

## Evidence

- approved_design_ref: `docs/plans/changes/2026-08-23-routeros-scripting-guidelines-design.md`
- approved_plan_ref: `docs/plans/changes/2026-08-23-routeros-scripting-guidelines-plan.md`
- review_gate_ref: `review:f20590e5d6722cf3b1e390208f945d68093467b10d79d24426f24b30f74aaf42:3bf4a11bb0140befda3885d592cb0de48287972160617b8d2a59394fe96f4c3b:RSG-M010-RSG-M020-main-review-pass:pass`
- verification_ref: `verification:f20590e5d6722cf3b1e390208f945d68093467b10d79d24426f24b30f74aaf42:3bf4a11bb0140befda3885d592cb0de48287972160617b8d2a59394fe96f4c3b:scripts-check-283-passed`
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs: the approved shared skill entrypoint and references, routing and distribution contracts, current inventory documentation, and architecture documentation listed in frontmatter
- stage_artifact_refs: this change's approved design and plan, converged task ledger, immutable execution result, and this pending truth-sync artifact under `docs/plans/changes/`
- summary: Shared truth now defines `routeros-scripting-guidelines` as a conditional RouterOS language overlay grounded in the official manual, publishes it through the 40-skill root-flat surface, and keeps live network authority with the active primary workflow.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved `coding:sync-truth` on 2026-08-23 for the complete three-repository cutover.
- next_entry: close-change
