# Maintenance Contract

`src/skills/` is authored truth. `contracts/skills.toml` owns the 40 public IDs, source mapping, activation mode, default role, mutation guards, and real semantic dependencies. The installed routing contract owns trigger cases, support routes, and response composition; it has no phase, mode, or gate authority.

Generators produce `skills/`, `skills.index.json`, and architecture diagrams. Static checks validate parseability, inventory, discovery metadata, reference closure, generated parity, documentation, lint, types, and tests. They do not validate workflow artifacts, enforce a lifecycle, or execute agent behavior.
