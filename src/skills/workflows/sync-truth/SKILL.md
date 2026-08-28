---
name: sync-truth
description: "Use after verified behavior changes to update stable project truth, documentation boundaries, and durable operational facts."
---

# Sync Truth

Update long-lived project truth from verified change evidence.

## Use This Skill When

- a verified change has real truth impact
- stable documentation or durable operational facts no longer match the implementation

Do not use it for read-only project explanation, a change with no truth impact, implementation review, or closure without truth updates.

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
- External paths, secrets, settings contents, or transient machine state do not enter stable project truth unless the user explicitly chose them as a durable public contract.
- Documentation scope never widens implementation authority.
