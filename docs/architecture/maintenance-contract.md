# Maintenance Contract

`src/skills/` is authored truth. `contracts/skills.toml` owns the 40 public IDs, source mapping, activation mode, default role, mutation guards, and semantic dependencies. The lifecycle, workflow-mode, and routing contracts are declarative authoring guidance only.

Generators produce `skills/`, `skills.index.json`, and architecture diagrams. Static checks validate parseability, inventory, discovery metadata, reference closure, generated parity, documentation, lint, types, and tests. They do not validate workflow artifacts or execute lifecycle behavior.
