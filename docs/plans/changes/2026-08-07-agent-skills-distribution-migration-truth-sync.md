# Agent Skills Distribution Migration Truth Sync

## Evidence

- approved_design_ref: `docs/plans/changes/2026-08-07-agent-skills-distribution-migration-design.md`
- approved_plan_ref: `docs/plans/changes/2026-08-07-agent-skills-distribution-migration-plan.md`
- review_gate_ref: bounded `review-change` implementation review passed on 2026-08-07 with no unresolved accepted finding
- verification_ref: generated index, root-flat skills, and diagrams are fresh; `bash scripts/check.sh`, all source-runtime smoke tests, Claude strict validation, Codex plugin validation, active-reference scans, `git diff --check`, and unrelated-working-directory owner-runner checks passed
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs:
  - `README.md`
  - `AGENTS.md`
  - `docs/AGENTS.md`
  - `docs/README.md`
  - `docs/quickstart.md`
  - `docs/architecture/harness-state-machine.md`
  - `docs/architecture/install-surface.md`
  - `docs/architecture/invocation-contract.md`
  - `docs/architecture/maintenance-contract.md`
  - `docs/architecture/workflow-orchestration.md`
  - `docs/changelog/design-decisions.md`
- stage_artifact_refs:
  - `docs/plans/changes/2026-08-07-agent-skills-distribution-migration-design.md`
  - `docs/plans/changes/2026-08-07-agent-skills-distribution-migration-plan.md`
- summary: Stable truth now records retained Claude Code and Codex plugin lanes, optional consumer-owned `npx skills` guidance with no repository restrictions, duplicate detection, or coexistence guarantee, unchanged public identities, owner-local harness runtime closure, retired active command wrappers, and the Superpowers acknowledgement.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: close-change
