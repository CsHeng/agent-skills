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

## Shared Runtime

Resolve the installed helper relative to this `SKILL.md` before changing into the target repository. `SKILL_ROOT` is explicitly assigned to the activated skill directory and is not expected from the host:

```bash
SKILL_ROOT="/absolute/path/to/sync-truth"
HARNESS_CLI="$(realpath "$SKILL_ROOT/scripts/harness/cli.py")"
[[ -f "$HARNESS_CLI" ]] || exit 1
```

Use its `truth-sync` namespace for each complete validation or gate operation:

```bash
python3 "$HARNESS_CLI" truth-sync validate "<truth-sync-artifact>"
python3 "$HARNESS_CLI" truth-sync evaluate "<ledger-file>" "<truth-sync-artifact>"
```

## Artifact Contract

The truth-sync artifact contains `## Evidence`, `## Stable Truth Updates`, and `## Human Gate`.

- Evidence records `approved_design_ref`, `approved_plan_ref`, `review_gate_ref`, `verification_ref`, and `truth_sync_required: true`; every value must exactly match the approved plan and immutable execution result.
- Stable truth updates record `stable_truth_refs`, `stage_artifact_refs`, and `summary`. Stable refs point only at long-lived truth roots and never at `docs/plans/`.
- `stable_truth_refs` remain repository-relative even when implementation used exact external files. Validate `allowed_external_touch_refs` and metadata-only `verified_external_changes` against the approved plan and embedded task ledger; never copy external paths into stable truth scope.
- The human gate records `approval_required: true`, `approval_status: pending`, and `next_entry: close-change`.
- Keep approval pending until the user explicitly approves the truth sync. A passing review and verification gate plus approved truth sync is required before close; otherwise route to the machine-selected current entry.

## Workflow

1. Validate direct explicit-request authority or the complete approved-plan controller context.
2. Confirm from the approved plan and immutable execution result that truth sync is required, and reject missing, stale, or mismatched evidence. For external evidence, validate exact set, plan/design/task binding, contiguous parent-linked applied chains, and metadata-only manifests without rereading the current external file. Later legitimate user edits do not invalidate historical execution evidence.
3. Update stable truth artifacts with the minimum required changes.
4. Compose `organize-docs` only when a structured approved docs-governance predicate matches and every changed ref remains inside the stable truth touch set. Use `decision-record-lifecycle` only when the approved truth sync creates, promotes, supersedes, compacts, or retires stable decision truth; a simple stable fact update does not match it.
5. Stop for explicit human truth-sync approval before close.

## Operating Rules

- This is the top-level truth-sync gate.
- `analyze-project` remains the read-only truth query entry.
- `organize-docs` remains a lower-plane truth maintenance component.
- Markdown files do not activate `organize-docs` by suffix alone, and controller composition never widens the approved touch set.
- `decision-record-lifecycle` never promotes `docs/plans/` into stable truth and never authorizes quota-driven archive or deletion.
- Truth sync does not rediscover the project from zero.
