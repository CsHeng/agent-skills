# Local Dependency Selection

Read this when choosing between an existing capability, a library, and custom code for one owned behavior. It covers the local implementation decision; a material open design choice belongs to `design-change`, and a runtime or delivery-boundary change belongs to language selection in `skills-routing`.

- Understand the business requirement, actual consumers, and relevant current code before choosing. Look for suitable project capabilities, standard-library or platform APIs, and mature ecosystem libraries before writing general-purpose code; evaluate a repository helper against the same current need.
- Prefer a suitable maintained library for a capability it already owns, in ordinary development, authorized repair, and migrations alike. Evaluate the lasting maintenance cost alongside the first patch.
- Judge suitability by required behavior, compatibility, runtime and delivery fit, maintenance and security response, transitive surface, licensing, and update cost. Choose an adequate existing capability with proportionate investigation, and keep an approved suitable library even when a standard-library alternative exists.
- Keep small domain rules and necessary adapters local when they fall outside a library's ownership. Implement a general mechanism yourself only when available capabilities fail a concrete requirement or impose a demonstrated disproportionate burden, and keep it narrow.
- When the appropriate library changes the runtime or delivery boundary, resolve that through language selection in `skills-routing`.
- In an authorized refactor, compare custom file, path, parsing, transport, and serialization code with the capabilities now available; replace redundant mechanics and retire their compatibility tests together while preserving domain tests, real consumer contracts, and data protections. Wrapping the same custom code behind a library-shaped interface keeps its maintenance responsibility.
- Use a maintained implementation for cryptography, authentication protocols, parsers for complex standards, and concurrency primitives.
- When the user or approved design specifies a library for a goal, that library is a boundary: choose glue, helpers, and local algorithms around it.
