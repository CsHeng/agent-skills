---
name: sync-truth
description: "Update stable project docs and durable operational facts to match already verified behavior when the user asks or an approved change includes it. Not for restructuring documentation ownership, layout, or search boundaries, which belongs to organize-docs, or for read-only explanation, which belongs to analyze-project."
---

# Sync Truth

Update long-lived project truth from verified change evidence.

## Use This Skill When

- a verified change has real truth impact and the user request or approved change scope authorizes the documentation mutation
- stable documentation or durable operational facts no longer match the implementation

Read-only project explanation goes to `analyze-project`, implementation review to `review-change`, closure without truth updates to `close-change`, and restructuring of documentation ownership, layout, or search boundaries to `organize-docs`.

## Workflow

1. Identify the smallest stable truth roots affected by verified behavior, separating long-lived truth from stage artifacts, generated output, and historical notes.
2. Start from the verified change evidence and update the stable facts that current implementation and verification support; keep stage artifacts as history.
3. Compose `organize-docs` when ownership, truth roots, search boundaries, stage placement, canonical terminology, or prose structure need adjustment, or when stable decision truth is created, promoted, superseded, compacted, or retired.
4. Verify links, commands, generated references, terminology, and repository documentation checks, then state the updated truth, its evidence, and any remaining mismatch.

## Rules

- Update facts from evidence, and record a goal, discretion, or boundary mismatch as a finding for the decision that owns it (`development-standards` Goals, Discretion, And Risk).
- Record external paths, secrets, settings contents, or transient machine state only when the user named them a durable public contract.
- Documentation authority covers documentation only.
