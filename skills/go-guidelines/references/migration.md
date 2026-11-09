# Go Migration Guidance

Read this when porting existing code, tests or a CLI from another language to Go. The decision whether to migrate, and how to weigh migration benefit against uniformity, belongs to `references/language-selection.md` in `skills-routing`; dependency selection follows `development-standards`.

## Design

- Design around business rules and actual consumer contracts, using Go's standard library and suitable maintained Go dependencies. Where the standard library has a gap, select an ecosystem implementation. Keep exact legacy serialization or parser behavior only for a real compatibility requirement.
- When Go remains the selected product language, choose between completing the current design, reusing a package, and replacing the flawed implementation. Evaluate Go suitability against business and consumer requirements.
- Inspect migration support code (file and path utilities, source-analysis adapters, type coercions) against the capabilities of existing Go packages and mature libraries. Trace real callers and protected domain behavior, and keep the business-specific glue outside the chosen capability’s ownership. A language prefix or utility filename prompts inspection; add a library when it removes a real responsibility at acceptable lifecycle cost.

## Tests

- Useful Python tests, fixture generators and independent verification tools can stay; their runtime and maintenance costs are separate from production delivery.
- Rework migration tests around business outcomes, real consumers, retained data and failure boundaries. Replace incidental formatting and library-equivalence assertions with meaningful scenarios, and keep required protocol bytes and data protection.

## CLI Parity

Preserve documented or relied-on arguments, outputs, exit behavior and state changes. Use the chosen parser's native behavior where consumers accept the native detail, such as abbreviations, diagnostic spelling or terminal-width wrapping.
