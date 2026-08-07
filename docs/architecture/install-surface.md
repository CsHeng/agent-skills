# Install Surface

The source tree is structured for maintainability, while installed skill surfaces remain flat for agent compatibility.

## Surfaces

- `src/skills/`: source-of-truth tree grouped by category.
- `src/runtime/harness/`: non-discoverable deterministic runtime source and repository smoke tests.
- `contracts/skills.toml`: contract and exposure source.
- `skills/`: tracked generated root-flat compatibility surface. Current plugin manifests point directly here.
- `.dist/claude/skills/`: ignored, reproducible Claude-compatible flat surface generated on demand.
- `.dist/codex/skills/`: ignored, reproducible Codex-compatible flat surface generated on demand.

## Generation

Regenerate the tracked runtime surface with:

```bash
python3 scripts/flatten-skills.py --target root-flat
```

Generate ignored external surfaces only when needed:

```bash
python3 scripts/flatten-skills.py --target claude
python3 scripts/flatten-skills.py --target codex
```

External generated surfaces include `skills/.source-map.json`. The root-flat generated surface includes `.source-map.json` directly under the repository root `skills/` directory. `--target all` remains available for explicit release or packaging work, but normal repository maintenance only refreshes `root-flat`.

## Runtime Closure

Harness runtime is not an installable skill. Each runner-owning workflow declares `runtime_bundle = "harness"`; generation copies production files from `src/runtime/harness/` into that skill's `scripts/harness/` directory and excludes repository smoke tests and provider metadata.

Installed helpers locate sibling files from their own script directory. Portable skill prose uses skill-relative `scripts/...` paths and binds `SKILL_ROOT` only when it must resolve an installed helper before changing directories. There is no public runtime-support pseudo-skill and no universal provider-supplied `$PLUGIN_ROOT` contract.

## Distribution Ownership

Claude Code and Codex keep their maintained native plugin surfaces. The same generated `skills/` tree is the public payload that other coding agents may consume through optional `npx skills` guidance.

The repository validates payload shape, public identities, semantic requirements, and physical closure. It does not constrain or inspect the agent, scope, destination, copy/symlink mode, duplicate exposure, coexistence, update, removal, or cleanup choices made by an external consumer or the upstream CLI.

## Validation

Use:

```bash
bash scripts/check.sh
```

The check verifies manifest/source bijection, generated index freshness, semantic closure, owner-local runtime bundles, the tracked root-flat surface, temporary Claude and Codex install surfaces, command retirement, and retired review-routing references outside historical docs. It also rejects tracked `.dist/` files so a fresh clone remains sufficient for validation.
