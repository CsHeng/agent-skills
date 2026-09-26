# Product Documentation

- [Quickstart](quickstart.md): installation and Skill selection.
- [Skill composition](architecture/skill-composition.md): portable semantic product contract.
- [Install surface](architecture/install-surface.md), [invocation](architecture/invocation-contract.md) and [maintenance](architecture/maintenance-contract.md): self-contained product boundaries.
- `architecture/diagrams/` and `architecture/generated/`: repository-owned generated semantic views.
- [Product decisions](changelog/design-decisions.md): durable product choices.

Shared architecture and vocabulary belong to `$AGENT_ARCHITECTURE_DIR/docs/architecture/`. New designs/plans, including Skills-only changes, belong to that owner's `docs/plans/skills/`; results belong to `docs/evaluations/skills/`; archived commands are under `archived/agent-skills/commands/`. Use the source roots from this repository's mise configuration rather than infer sibling paths. Use explicit paths and `rg --no-ignore` for stage/history searches there.

Those maintenance records do not become Skill dependencies. This product can be checked, installed and used without the architecture checkout, and does not require local stage artifacts or historical inventory.
