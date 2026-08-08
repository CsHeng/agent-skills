# Skill Activation And Trigger Ownership Truth Sync

## Evidence

- approved_design_ref: `docs/plans/changes/2026-08-07-skill-activation-and-trigger-ownership-design.md`
- approved_plan_ref: `docs/plans/changes/2026-08-07-skill-activation-and-trigger-ownership-plan.md`
- review_gate_ref: One bounded delegated implementation review found an out-of-touch-set `scripts/check-fixtures.py` change; the main agent accepted the finding, removed that script diff while retaining the migrated fixture contract under `tests/`, and one focused verification review passed. Final sanitized acceptance then exposed external loads entering a `(repo)` fallback bucket; the main agent accepted that current-slice defect, used the permitted additional repair attempt to add a regression fixture and require exact current public-ID resolution, and completed a bounded direct verification review with no unresolved finding.
- verification_ref: The skill-miner suite passed 8 tests; the repository suite passed 90 tests; `bash scripts/check.sh` passed all contract, generated-surface, fixture, Python, harness-smoke, and review-boundary checks; Claude strict validation, Codex plugin validation, PlantUML validation, docs-boundary validation, and `git diff --check` passed. The final sanitized all-repositories/current-inventory smoke reported 40 skills, 12,386 classified records across 2,023 sessions: 889 exact user requests, 3,462 assistant references, and 8,035 resolved skill loads. Its unique skill-session load upper bound was 4,220, split into 387 explicit-request-with-load and 3,833 heuristic-inferred cases; no unresolved `(repo)` bucket or raw example was emitted. Public skill IDs, install targets, lifecycle-owner fields, runtime pointers, routing pointers, and provider manifests are unchanged.
- truth_sync_required: true

## Stable Truth Updates

- stable_truth_refs:
  - `README.md`
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/architecture/invocation-contract.md`
  - `docs/architecture/workflow-orchestration.md`
  - `docs/architecture/diagrams/skill-trigger-ownership.puml`
  - `docs/architecture/generated/skill-trigger-ownership.svg`
- stage_artifact_refs:
  - `docs/plans/changes/2026-08-07-skill-activation-and-trigger-ownership-design.md`
  - `docs/plans/changes/2026-08-07-skill-activation-and-trigger-ownership-plan.md`
- summary: Stable truth now records contract-owned activation modes and default roles, capability-aware Codex policy projection, Claude effective visibility without a claimed unsupported switch, semantic positive and negative trigger-case ownership, non-authoritative lexical hints, explicit compatibility successors, conservative usage-measurement evidence classes, and the generated activation and trigger-ownership view. Public IDs and provider manifest identity remain unchanged.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: close-change
