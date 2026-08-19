# Portable Plugin Surface

`src/skills/` is nested authored truth. `skills/` is the sole materialized root-flat 39-skill payload consumed by both maintained plugin manifests, direct Agent Skills discovery, and optional consumer-managed `npx skills` installation.

`src/runtime/harness/` is the single authored non-discoverable Python lifecycle runtime. Exactly `design-change`, `plan-change`, `implement-change`, `review-change`, `sync-truth`, and `close-change` declare `runtime_bundle = "harness"`; generation copies the production manifest into each owner at `scripts/harness/`. `analyze-project` remains lifecycle-owned and runtime-free.

Standalone distribution is closed at the skill directory. A selected lifecycle skill never depends on a repository sibling or a separately installed support skill. Destination, copy-versus-symlink mode, duplicate exposure, coexistence, update, and removal remain consumer-owned for optional `npx skills` use.

`.dist/` remains ignored and inert. Generation and validation neither read nor write provider-specific payloads there.

## Validation

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

Generation builds and validates a temporary sibling tree before atomically replacing `skills/`. The aggregate check verifies exact authored-to-generated parity, the six no-missing-or-extra production bundles, and copied skill execution from an unrelated temporary directory.
