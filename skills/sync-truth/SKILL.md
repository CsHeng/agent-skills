---
name: sync-truth
description: "Update stable project docs and durable operational facts to match already verified behavior when the user asks or an approved change includes it. Not for restructuring documentation ownership, layout, or search boundaries, which belongs to organize-docs, or for read-only explanation, which belongs to analyze-project."
---

# Sync Truth

Update long-lived project truth from verified change evidence.

## Use This Skill When

- a verified change has real truth impact
- stable documentation or durable operational facts no longer match the implementation

Do not use it for read-only project explanation (`analyze-project`), a change with no truth impact, implementation review (`review-change`), closure without truth updates (`close-change`), or a requested restructuring of documentation ownership, layout, or search boundaries (`organize-docs`).

## Workflow

1. Confirm the user request or approved change scope authorizes the documentation mutation.
2. Identify the smallest stable truth roots affected by verified behavior.
3. Distinguish long-lived truth from stage artifacts, generated output, and historical notes.
4. Update only the stable facts supported by current implementation and verification evidence.
5. Compose `organize-docs` only when ownership, truth roots, search boundaries, stage placement, canonical terminology, or prose structure materially need adjustment.
6. Verify links, commands, generated references, terminology, and repository-specific documentation checks.
7. Report updated truth, evidence, and any remaining mismatch.

## Operating Rules

- `analyze-project` remains the read-only truth query entry.
- Truth sync does not rediscover the project from zero or reinterpret unverified implementation claims.
- Stage artifacts do not become stable truth merely because they are detailed.
- Verified evidence updates factual truth, but it does not by itself change goals, discretion, or boundaries: those change only through the user decision or approved change scope that owns them. Record a verified mismatch between effective goals and the implementation as a finding for that owning decision; do not self-authorize a goal, discretion, or boundary update from evidence. Superseded gates and exemption history stay in stage records rather than becoming a runtime contract.
- External paths, secrets, settings contents, or transient machine state do not enter stable project truth unless the user explicitly chose them as a durable public contract.
- Documentation scope never widens implementation authority.
