# Local Dependency Selection

Read this when choosing between an existing project capability, a mature community library or framework, and standard-library code during `design-change`, `implement-change`, or an authorized refactor. A runtime or delivery-boundary change belongs to language selection in `skills-routing`.

## Ownership And Default Preference

The user owns the business intent and any explicit technology constraint; the agent owns technical selection, implementation, and long-term repository maintenance. When the user specifies a framework, third-party library, or standard-library constraint, honor that choice. Otherwise, select the approach directly with seasoned engineering judgment and record the chosen library and its capability boundary in the design or change summary:

- **Default to a mature community library or framework for non-trivial general capabilities.** When a capability involves protocol rules, HTTP download/retry/resumption, structured CLI/config/schema binding, complex parsing, database migrations, or concurrency orchestration, stand on a battle-tested library or framework. Although an agent can generate custom standard-library infrastructure quickly, keeping bespoke mechanics and their edge-case test suites inside the repository taxes context tokens, review rounds, and maintenance across every future session. Accept bounded library-upgrade or future-replacement risk behind a clear local boundary in exchange for fast delivery and a small repository footprint.
- **Use the standard library directly for small, self-contained operations.** When the standard library covers the need in a short, straightforward call site without a custom state machine or mini-framework, write it directly instead of adding micro-dependencies that increase lockfile and supply-chain noise.
- **Define the capability boundary.** State which responsibilities the chosen library or framework owns and which thin domain rules and adapter glue remain in repository code, keeping the integration seam narrow enough that a future library upgrade or swap stays local.

## Selection And Maintenance Rules

- Check existing repository dependencies first and reuse an adequate capability already in the project before adding a second library for the same role; keep an approved suitable library even when a standard-library alternative exists.
- Judge candidates by required behavior, idiomatic ecosystem adoption, active maintenance, runtime and delivery fit, transitive surface, and license compatibility, with investigation proportionate to the change.
- Use a maintained implementation for cryptography, authentication protocols, parsers for complex standards, and concurrency primitives.
- Implement a general mechanism yourself only when available libraries fail a concrete requirement or impose a demonstrated disproportionate burden, and keep that custom mechanism narrow.
- In an authorized refactor, replace redundant custom file, path, parsing, transport, and serialization mechanics with mature libraries now available and retire their bespoke tests together while preserving domain tests, real consumer contracts, and data protections. Wrapping the same custom code behind a library-shaped interface keeps its maintenance burden.
