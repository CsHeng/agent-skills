# Docs Agent Notes

## Truth Boundary

- `docs/architecture/` and other stable `docs/` domains contain long-lived project truth.
- `docs/plans/` contains stage artifacts and history, not default current truth.
- `docs/architecture/workflow-orchestration.md` is the canonical semantic workflow view.
- `docs/architecture/diagrams/*.puml` and `docs/architecture/generated/*.svg` are generated from repository-owned semantic composition data; do not edit them by hand.
- `archived/` is inert history outside default documentation and Skill discovery.

## Search Policy

- Default stable search: `rg -n "pattern" docs`
- Explicit stage-history search: `rg --no-ignore -n "pattern" docs/plans`
- `docs/.ignore` affects search tools, not Git tracking. Keep valuable stage artifacts in Git.

Write stable truth from the current repository state. Preserve durable rationale, conditions, exceptions, and consequences, while leaving one-time migration narration in stage history.
