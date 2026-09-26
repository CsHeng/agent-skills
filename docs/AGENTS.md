# Product Documentation

`docs/architecture/`, `quickstart.md` and current product decisions own self-contained Skill use and maintenance truth. Generated `.puml` and `.svg` semantic views remain repository-owned; do not edit them by hand.

Shared boundaries and all new designs/plans belong to `$AGENT_ARCHITECTURE_DIR/docs/`; use its `plans/skills/` and `evaluations/skills/` domains for this product. Historical originals live in its `archived/agent-skills/` tree. Product checks must not require these external records or local `docs/plans` files.

Default search here covers product truth. Honor the architecture owner's search boundary when reading stage artifacts, using explicit paths and `rg --no-ignore`. Git tracking and search exclusion are distinct. Preserve product rationale, exceptions and compatibility obligations; do not copy the shared architecture explanation back into this tree.
