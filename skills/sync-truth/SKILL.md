---
name: sync-truth
description: "Update stable project docs and durable operational facts to match already verified behavior, together with the user-fixed intent and rationale that explain it, when the user asks or an approved change includes it. Not for restructuring documentation ownership, layout, or search boundaries, which belongs to organize-docs, or for read-only explanation, which belongs to analyze-project."
---

# Sync Truth

Update long-lived project truth from verified change evidence, and keep the user's intent for that behavior where future maintainers will find it.

## Use This Skill When

- a verified change has real truth impact and the user request or approved change scope authorizes the documentation mutation
- stable documentation or durable operational facts no longer match the implementation
- a delivered change rests on user-fixed intent, preferences, or rejected alternatives that so far live only in a stage record or the conversation

Read-only project explanation goes to `analyze-project`, implementation review to `review-change`, closure without truth updates to `close-change`, and restructuring of documentation ownership, layout, or search boundaries to `organize-docs`.

## Workflow

1. Identify the smallest stable truth roots affected by verified behavior, separating long-lived truth from stage artifacts, generated output, and historical notes.
2. Start from the verified change evidence and update the stable facts that current implementation and verification support; keep stage artifacts as history.
3. Promote the durable intent behind that behavior to the same stable owner: the outcomes, preferences, and rationale the user fixed, and any rejected alternative that remains tempting, stated so a later change can tell when it is reopening a settled choice. Take it from the design's marked durable intent or, when no design exists, from the user's own statements in the conversation, and keep it distinct from agent-chosen means. A choice that binds several components or products becomes a decision record through `organize-docs`.
4. Compose `organize-docs` when ownership, truth roots, search boundaries, stage placement, canonical terminology, or prose structure need adjustment, or when stable decision truth is created, promoted, superseded, compacted, or retired.
5. Verify links, commands, generated references, terminology, and repository documentation checks, then state the updated truth, its evidence, and any remaining mismatch.

## Rules

- Update facts from evidence, and record a goal, discretion, or boundary mismatch as a finding for the decision that owns it (`development-standards` Goals, Discretion, And Risk).
- Promote only intent the user stated or approved; an inferred preference, a one-change execution detail, or a review exchange is not durable intent.
- Record external paths, secrets, settings contents, or transient machine state only when the user named them a durable public contract.
- Documentation authority covers documentation only.
