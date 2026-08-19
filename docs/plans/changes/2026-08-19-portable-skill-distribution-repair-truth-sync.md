+++
artifact_kind = "truth-sync"
contract_version = 3
execution_result_ref = "2026-08-19-portable-skill-distribution-repair-execution-result.json"
execution_result_sha256 = "5cd510ec9d7eb1110499523dea9d48d7fdf7fb718b3f9df225117ccfbb510924"
ledger_ref = "2026-08-19-portable-skill-distribution-repair-ledger.json"
ledger_sha256 = "01a25fb58deb6e36242684d4b54929d1b7c350c8fbb2397679ce4ecbeb92b298"
approval_status = "pending"

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "docs/architecture", "docs/changelog/design-decisions.md"]
test_file_refs = []
external_impl_file_refs = []
+++
# Truth Sync

## Scope

Synchronize the stable repository truth for the nested authored skill tree, generated root-flat public projection, exact six skill-local Python runtime bundles, codex-native default backend, retired compatibility skills, thin serial validation, and immutable Markdown exception policy.

## Evidence

- approved_design_ref: `docs/plans/changes/2026-08-19-portable-skill-distribution-repair-design.md`
- approved_plan_ref: `docs/plans/changes/2026-08-19-portable-skill-distribution-repair-plan.md`
- review_gate_ref: `review:2eea25beed0fe6199e857a8d85358cb2dbfcc66aa90d1297f2205f089be7e83b:9494ac12ea83db8f52849ed0c7a50eb716b0098e91d0cbf86aef2e0fec239174:pdr-implementation-review-pass-20260819:pass`
- verification_ref: `verification:2eea25beed0fe6199e857a8d85358cb2dbfcc66aa90d1297f2205f089be7e83b:9494ac12ea83db8f52849ed0c7a50eb716b0098e91d0cbf86aef2e0fec239174:scripts-check-216-passed`
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs: `AGENTS.md`, `README.md`, `docs/architecture`, and `docs/changelog/design-decisions.md`
- stage_artifact_refs: the approved PDR design and plan, converged version-3 task ledger, immutable execution result, and this pending truth-sync artifact under `docs/plans/changes/`
- summary: Stable truth now records one nested authored tree, one generated root-flat public tree, generated skill-local runtime closure for six lifecycle owners, codex-native as the absent-flag default, explicit Herdr compatibility, serial aggregate validation, and zero mutable Markdown hard wraps.

## Human Gate

- approval_required: true
- approval_status: pending
- next_entry: close-change
