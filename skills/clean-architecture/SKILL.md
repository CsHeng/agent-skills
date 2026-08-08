---
name: clean-architecture
description: "Compatibility entry for explicitly named clean-architecture requests; hand off architecture boundaries to architecture-patterns."
---

# Clean Architecture Compatibility

Use this skill only when the user explicitly names `clean-architecture` or an existing thin host entry selects this public ID. It is retained for compatibility and does not compete for native architecture requests.

The durable owner is `architecture-patterns`:

- read `architecture-patterns/references/clean-boundaries.md` for handlers, services, repositories, dependency direction, interface placement, and cross-boundary tests
- apply `architecture-patterns` as the response owner or lifecycle overlay
- compose `testing-strategy` only when concrete test layering or verification must be planned

Do not emit an independent checklist or report schema. Preserve this public ID until a separately approved compatibility migration removes it.
