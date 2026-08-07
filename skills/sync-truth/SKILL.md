---
name: sync-truth
description: "Use after verified behavior changes to update stable project truth docs, README/AGENTS boundaries, and durable operational facts."
---

# Sync Truth

Update stable truth after a truth-affecting change has evidence behind it.

## Use This Skill When

- a verified change has `truth_impact = true`
- stable docs or other long-lived truth need to reflect approved behavior
- the harness must update truth from execution evidence rather than rediscovery

## Do Not Use This Skill When

- the change has no real truth impact
- the request is only a read-only project explanation; use `analyze-project`
- the task is only implementation review or close without truth updates

## Bundled Runtime

Resolve the installed helper relative to this `SKILL.md` before changing into the target repository. `SKILL_ROOT` is explicitly assigned to the activated skill directory and is not expected from the host:

```bash
SKILL_ROOT="/absolute/path/to/sync-truth"
RUNNER="$(realpath "$SKILL_ROOT/scripts/harness/truth-sync-runner.sh")"
[[ -f "$RUNNER" ]] || exit 1
```

Use it to record the phase, derive a default artifact path, validate the artifact, and report the approval and gate states:

```bash
bash "$RUNNER" entry-phase
bash "$RUNNER" default-path "<topic>"
bash "$RUNNER" validate "<truth-sync-artifact>"
bash "$RUNNER" approval-status "<truth-sync-artifact>"
bash "$RUNNER" gate-result "<truth-sync-artifact>" "<review-status>" "<verify-status>"
```

## Artifact Contract

The truth-sync artifact contains `## Evidence`, `## Stable Truth Updates`, and `## Human Gate`.

- Evidence records `approved_design_ref`, `approved_plan_ref`, `review_gate_ref`, `verification_ref`, and `truth_sync_required: true`.
- Stable truth updates record `stable_truth_refs`, `stage_artifact_refs`, and `summary`. Stable refs point only at long-lived truth roots and never at `docs/plans/`.
- The human gate records `approval_required: true`, `approval_status: pending`, and `next_entry: close-change`.
- Keep approval pending until the user explicitly approves the truth sync. A passing review and verification gate plus approved truth sync is required before close; otherwise route to the machine-selected current entry.

## Workflow

1. Confirm that truth sync is required for the change.
2. Gather approved design, plan, review, and verification evidence.
3. Update stable truth artifacts with the minimum required changes.
4. Use lower-plane truth maintenance skills when the update touches their domain.
5. Stop for explicit human truth-sync approval before close.

## Operating Rules

- This is the top-level truth-sync gate.
- `analyze-project` remains the read-only truth query entry.
- `organize-docs` remains a lower-plane truth maintenance component.
- Truth sync does not rediscover the project from zero.
