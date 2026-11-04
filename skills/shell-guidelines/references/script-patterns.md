# Shell Script Development Patterns

Write safe, portable orchestration scripts that stay linear, visible, and subordinate to the persisted implementation they invoke. The interpreter, strict-mode, quoting and structure rules are in `SKILL.md`; this reference adds diagnostics and examples.

## Choosing Shell By Target

- bash: bash-targeted local automation, CI, and Linux servers
- zsh: zsh-targeted automation and configuration
- sh: POSIX or minimal container environments

For a one-shot remote action, reuse the controller's built-in module, local rendering, thin transported Shell, or a short Python fragment on an existing runtime. `references/language-selection.md` in `skills-routing` owns the cost comparison for a persisted language change.

## Diagnostics And Logging

Send diagnostics to stderr and preserve stdout for the intended output. Keep error propagation and accurate exit status even when the script needs no logging framework.

Choose log events and their context through `logging-standards` when the task has an operational, diagnostic, security or audit consumer, and implement that contract with the project's existing mechanism. A one-shot wrapper may need only an actionable failure message. A managed operational tool may need levels, structured fields and correlation; select those for its consumer, emit each error once, and redact sensitive values.

## Error Handling Examples

Trigger: writing an `ERR` trap or an input-validation function.

### Trap-Based Error Handler

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

handle_error() {
    local exit_code=$?
    local line_number=$1
    echo "ERROR: Script failed on line $line_number with exit code $exit_code" >&2
    exit "$exit_code"
}

trap 'handle_error $LINENO' ERR
```

### Bash/zsh Input Validation Function

```bash
validate_input() {
    local input="$1"
    if [[ -z "$input" ]]; then
        echo "ERROR: Input parameter is required" >&2
        exit 1
    fi
}
```
