# Maintenance Contract

`src/skills/` and `src/runtime/harness/` are authored truth. `contracts/skills.toml` owns source mapping, exposure, activation mode, default role, mutation guards, runtime ownership, and linked runtime or routing contracts. `contracts/runtime-bundles.toml` owns the exact production runtime file set. `skills/` and `skills.index.json` are generated projections.

Edit authored sources and contracts, then regenerate all tracked projections:

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

The generator stages and validates the complete root-flat tree before atomic replacement and restores the immediately preceding tree if promotion fails. `scripts/check.sh` serially invokes root-flat parity, standalone install closure, contracts, index, diagrams, Ruff, ty, pytest, and Markdown once. It keeps `.dist/` ignored and untouched. The pre-commit hook enters the same non-mutating check.

Codex-native is the flag-absent runtime binding backend. `implement-change-via-herdr` remains an explicit lower-plane adapter. Lifecycle state, approved topology, repair, truth sync, and close authority stay with the sovereign workflow kernel.
