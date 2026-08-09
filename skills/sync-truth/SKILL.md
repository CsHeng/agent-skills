---
name: sync-truth
description: "Use after verified behavior changes to update stable project truth docs, README/AGENTS boundaries, and durable operational facts."
---

# Sync Truth

Update stable truth after a truth-affecting change has evidence behind it. Mutation authority is either a direct explicit user request or a complete approved-plan controller context; neither path implies the other.

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
bash "$RUNNER" validate-against "<truth-sync-artifact>" "<approved-plan>" "<execution-result-json>"
bash "$RUNNER" approval-status "<truth-sync-artifact>"
bash "$RUNNER" mutation-authorization direct "<true|false>"
bash "$RUNNER" mutation-authorization controller "<approved-plan>" "<execution-result-json>"
bash "$RUNNER" docs-governance-decision "<approved-plan>" "<changed-stable-ref>"...
bash "$RUNNER" gate-result "<truth-sync-artifact>" "<approved-plan>" "<execution-result-json>"
```

## Artifact Contract

The truth-sync artifact contains `## Evidence`, `## Stable Truth Updates`, and `## Human Gate`.

- Evidence records `approved_design_ref`, `approved_plan_ref`, `review_gate_ref`, `verification_ref`, and `truth_sync_required: true`; every value must exactly match the approved plan and immutable execution result.
- Stable truth updates record `stable_truth_refs`, `stage_artifact_refs`, and `summary`. Stable refs point only at long-lived truth roots and never at `docs/plans/`.
- The human gate records `approval_required: true`, `approval_status: pending`, and `next_entry: close-change`.
- Keep approval pending until the user explicitly approves the truth sync. A passing review and verification gate plus approved truth sync is required before close; otherwise route to the machine-selected current entry.

## Workflow

1. Validate direct explicit-request authority or the complete approved-plan controller context.
2. Confirm from the approved plan and immutable execution result that truth sync is required, and reject missing, stale, or mismatched evidence.
3. Update stable truth artifacts with the minimum required changes.
4. Compose `organize-docs` only when a structured approved docs-governance predicate matches and every changed ref remains inside the stable truth touch set.
5. Stop for explicit human truth-sync approval before close.

## Operating Rules

- This is the top-level truth-sync gate.
- `analyze-project` remains the read-only truth query entry.
- `organize-docs` remains a lower-plane truth maintenance component.
- Markdown files do not activate `organize-docs` by suffix alone, and controller composition never widens the approved touch set.
- Truth sync does not rediscover the project from zero.
