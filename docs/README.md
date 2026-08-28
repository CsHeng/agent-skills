# Docs

This directory contains stable project truth plus stage artifacts retained for history.

## Stable Truth

- `quickstart.md` introduces installation and Skill selection.
- `architecture/workflow-orchestration.md` explains provider-neutral semantic workflow composition.
- `architecture/install-surface.md`, `invocation-contract.md`, and `maintenance-contract.md` define distribution and maintenance boundaries.
- `architecture/diagrams/` and `architecture/generated/` contain generated semantic views.
- `changelog/design-decisions.md` records current durable decisions and explicit supersessions.

## Stage Artifacts

Keep stage artifacts under `docs/plans/` when they matter for traceability. Default search tools avoid `docs/plans/` through `docs/.ignore`; use `rg --no-ignore` only when historical context is explicitly needed. Stage artifacts remain Git-tracked and never become stable truth automatically.
