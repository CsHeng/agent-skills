# Codex-Native Runtime Binding Truth Sync

## Evidence

- approved_design_ref: docs/plans/changes/2026-08-17-codex-native-binding-design.md
- approved_plan_ref: docs/plans/changes/2026-08-17-codex-native-binding-plan.md
- review_gate_ref: review:c7115414acbf07db3e9c3337ba9f5ca2feef31d2d612a444e69e3ed8777e2b7d:6e46d9267efb9550141a441dbeb7b1807893878a8fd68535ad3c71616dda7c15:pass
- verification_ref: verification:c7115414acbf07db3e9c3337ba9f5ca2feef31d2d612a444e69e3ed8777e2b7d:6e46d9267efb9550141a441dbeb7b1807893878a8fd68535ad3c71616dda7c15:pass
- truth_sync_required: true
- design_sha256: b8d41cc09b9024c61b2a8d16d7961f75adb714c4147306d1abf3990e3384ad4b
- plan_sha256: c7115414acbf07db3e9c3337ba9f5ca2feef31d2d612a444e69e3ed8777e2b7d
- ledger_sha256: 6e46d9267efb9550141a441dbeb7b1807893878a8fd68535ad3c71616dda7c15

## Stable Truth Updates

- stable_truth_refs:
  - docs/architecture/workflow-orchestration.md
  - README.md
- stage_artifact_refs:
  - docs/plans/changes/2026-08-17-codex-native-binding-design.md
  - docs/plans/changes/2026-08-17-codex-native-binding-plan.md
- summary: Stable workflow truth now documents the backend-neutral controller binding
  envelope core with two runtime binding backends: the codex-native backend
  (`schema_version: 2`, user-owned untracked role agent files with project-over-user
  precedence, pre-emission capability validation with distinct typed stops, all model
  policies spawning through the validated role file, command-job rejected, main-serial
  fallback) and the byte-compatible Herdr backend (`schema_version: 1` wire shape
  unchanged). The previous Herdr-only delegation decision horizon is rewritten as the
  three-way codex-native/Herdr/main-serial comparison on the existing three-trial
  user-run evidence standard. Lifecycle authority, plan topology ownership, adjudication,
  and provider neutrality of reusable contracts are unchanged. Generated diagrams,
  skill index, root-flat payload, and bundled runners were regenerated from source and
  are byte-identical projections.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved truth sync ("approve /sync-truth") on
  2026-08-17 after the deterministic execute gate returned review pass, verification
  pass, and truth-sync-pending.
- next_entry: close-change
