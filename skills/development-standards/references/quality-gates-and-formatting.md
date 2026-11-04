# Repository-Owned Quality Gates, Formatting, And CLI Conventions

Read this when selecting repository checks, proposing a new gate or metric, running a formatter, or writing a custom command-line interface.

## Quality Gates

- Select repository checks that cover the affected behavior and the actual delivery requirement; an available entrypoint is not a requirement to run every suite after each edit. In an authorized gate or suite simplification, keep checks for required behavior and remove the rest.
- Add a lint, complexity, duplication, coverage, or debt gate when it protects a named boundary and has a baseline, an accountable owner, a failure response, and an adoption or migration path. A metric is evidence for a goal; universal numeric thresholds across repositories or languages are not used.
- `testing-strategy` owns executable test evidence, suite boundaries, fixtures, and CI lanes; the matching language guideline owns concrete linter, formatter, type-checker, and test-runner configuration.
- Prefer trends and changed-code gates over arbitrary repository-wide targets when legacy baselines cannot satisfy a justified policy immediately.
- Record technical debt when its impact, scope, owner, priority, and retirement evidence are actionable.

## Formatting

- Follow the target repository's owned formatter and configuration, and run it on authorized changed files before final read-only checks. Column limits and pure-format lint gates come from that configuration, and strings, comments, and behavior stay as written when only line length is at issue.
- When the formatter cannot satisfy an existing explicit project hard rule, surface the configuration decision once rather than disabling the rule.
- Markdown prose is kept one paragraph per line under `organize-docs`.

## Custom CLI Conventions

- Follow repository-local command conventions first.
- Use descriptive long options for custom scripts; write and delete behavior takes an explicit option rather than a positional argument.
- Keep third-party CLI invocations in their native syntax.
- Give actionable validation errors and stable non-zero exits for invalid input.
