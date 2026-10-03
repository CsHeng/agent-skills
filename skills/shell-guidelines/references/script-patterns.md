# Shell Script Development Patterns

## Purpose

Write safe, portable orchestration scripts that stay linear, visible, and subordinate to the persisted implementation they invoke.

## Scope

- Shell choice for persisted scripts
- Strict mode, quoting, error handling, portability, and basic logging
- Capability signals that require a new persisted language decision

Out-of-scope:

- Selecting the replacement language for a persisted tool; use `language-decision-tree`
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
5. Route back to `language-decision-tree` when the script accumulates structured multi-step parsing, persistent state, complex retry or recovery, concurrency, multi-host distribution, embedded languages, or runtime and dependency management.
6. Prefer Go for a long-lived operational tool when static distribution, cross-platform delivery, or reduced runtime state materially improves the contract; do not treat this preference as a mandate.
7. Name Shell script files using hyphen style: `my-script.sh`, not `my_script.sh`.

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
- Complex persisted behavior has been routed back through `language-decision-tree`.
- `shellcheck` is clean when available.
