# Shell Script Development Patterns

## Purpose

Write safe, portable orchestration scripts that stay linear, visible, and subordinate to the persisted implementation they invoke.

## Scope

- Shell choice for persisted scripts
- Strict mode, quoting, error handling, portability, and basic logging
- Actual complexity or delivery costs that may justify a persisted language decision

Out-of-scope:

- Selecting the replacement language for a persisted tool; read `references/language-selection.md` in `skills-routing`
- Complex parsing, persistent state, or reusable business rules inside Shell

## Deterministic Rules

1. Choose Shell by target:
   - bash: bash-targeted local automation, CI, and Linux servers
   - zsh: zsh-targeted automation and configuration
   - sh: POSIX or minimal container environments
2. Use strict mode when supported:
   - bash/zsh: `set -euo pipefail`
   - sh: `set -eu`
3. Quote variables by default: `"${var}"`.
4. Keep orchestration linear and make each external mutation visible.
5. Revisit language selection only when actual parsing, state, recovery, concurrency, or distribution costs warrant it. An embedded language, script length, or accumulated state alone is not an escalation signal.
6. Use short embedded Python when it makes data handling clearer and its runtime is available. Keep quoting reviewable and pass data separately from source; extracting a named Python script for readability does not require a Go rewrite.
7. Preserve constrained native runtimes and parent-shell effects. Read `references/language-selection.md` in `skills-routing` for an authorized migration that may reduce total implementation, verification, deployment, and maintenance cost.
8. For one-shot remote actions, reuse the controller's built-in module, local rendering, thin transported Shell, or a short Python fragment on an existing runtime rather than creating a new product.
9. Name Shell script files using hyphen style: `my-script.sh`, not `my_script.sh`.

## Diagnostics And Logging

Send diagnostics to stderr and preserve stdout for the intended output. Keep error propagation and accurate exit status even when the script needs no logging framework.

Choose log events and their context through `logging-standards` when the task has an operational, diagnostic, security or audit consumer. Implement that contract with the project's existing mechanism; do not mandate `log_info`, `log_warn`, `log_error`, timestamps or one line format for every script.

A one-shot wrapper may need only an actionable failure message. A managed operational tool may need levels, structured fields and correlation; select those for its consumer, avoid duplicate error emission, and redact sensitive values.

## Checklist

- Shell script file uses kebab-case naming.
- Shebang matches the target environment.
- Strict mode matches the selected Shell.
- Variables are quoted unless splitting is intentional and documented.
- Inputs and mutation targets are validated.
- Language changes address actual complexity or cost within the authorized scope; embedded syntax alone has not become a rewrite requirement.
- `shellcheck` is clean when available.
