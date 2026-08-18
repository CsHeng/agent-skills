# Docs Agent Notes

## Truth Boundary

- Treat `docs/` as the home of long-lived project truth unless a more specific local rule says otherwise.
- Treat `docs/architecture/workflow-orchestration.md` as the canonical prose view of workflow routing, DAG ownership, and repair convergence.
- Treat `docs/architecture/diagrams/*.puml` and `docs/architecture/generated/*.svg` as generated review surfaces. Change the owning routing, lifecycle, workflow-mode, skills, or controller-local contract and regenerate both with `python3 scripts/generate-workflow-diagrams.py` instead of editing them directly. The tracked SVGs are the human-facing rendering referenced by README and other prose docs.
- Treat `docs/plans/` as stage artifacts and history, not default current-state truth.
- Keep proposed decisions and one-time implementation mechanics in stage history. Promote implemented or recurring negative decisions only when future maintainers need their boundary, rationale, consequences, compatibility obligation, or reconsideration trigger.
- Before fully superseding, compacting, or retiring a stable decision, transfer every unique durable fact and repair inbound links. Keep partially superseded decisions cross-linked while any independent public, persisted, migration, compatibility, or safety obligation survives.
- Do not archive or delete tracked stage artifacts by age, count, or completion quota.
- Default docs searches should target stable truth docs first and avoid stage artifacts.
- Treat repository-level `archived/` content as inert history outside active plugin and docs discovery. Search it only when historical context is explicitly requested.

## Search Policy

- Default docs search: `rg -n "pattern" docs`
- Historical docs search in this repository: `rg --no-ignore -n "pattern" docs/plans`
- If `grep` is required, use `grep -R --exclude-dir=plans "pattern" docs`

## Git Note

- `docs/.ignore` affects search tools such as `rg`; it does not control Git tracking.
- Keep stage artifacts under `docs/` in Git when they matter for project history, decision traceability, or later dispute resolution.
- Search suppression for `docs/plans/` belongs in `docs/.ignore`, not in the repository root `.gitignore`.
