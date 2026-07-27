---
name: shell-guidelines
description: "Apply Shell language policy to any Shell code, including persisted scripts, CI and local automation, ad hoc command fragments, or implementation reviews: safe variable names, target-matched interpreters, strict mode, quoting, portability, ShellCheck, and macOS/Homebrew behavior. Use as a language/tooling overlay alongside the primary workflow; do not take lifecycle ownership."
---

# Shell Guidelines

## Purpose

Define the Shell language-policy overlay for safe, portable, auditable Shell code. The primary workflow owns the task lifecycle, and `tool-decision-tree` owns ad hoc tool selection and command composition.

## Scope

In-scope:
- Shell fragments inside agent ad hoc commands
- Editing or creating shell scripts (`.sh`, bash/zsh scripts)
- CI and local automation scripts
- Code review and syntax audit for shell files

Out-of-scope:
- Agent ad hoc tool choice and command composition (see `tool-decision-tree` skill)
- Language selection (see `language-decision-tree` skill)
- Tool selection and progressive search workflow (see `tool-decision-tree` skill)

## Progressive Disclosure

- Script development patterns: `references/script-patterns.md`
- Code review DEPTH workflow and checklist: `references/review-checklist.md`

## Deterministic Steps

1. Choose the shell for the target environment
   - POSIX: `#!/bin/sh`
   - CI/Linux bash: `#!/usr/bin/env bash`
   - zsh scripts: `#!/usr/bin/env zsh`
   - macOS: `/bin/bash` is typically 3.2; if you rely on Bash 4+ features (e.g. `mapfile/readarray`, associative arrays), ensure Homebrew Bash is used via `PATH` or use the host-appropriate absolute shebang (`/opt/homebrew/bin/bash` on Apple Silicon, `/usr/local/bin/bash` on Intel) for internal scripts.
2. Enable strict mode for shell entrypoints
   - Use `set -euo pipefail` for Bash and zsh entrypoints.
   - Use `set -eu` for POSIX `sh` entrypoints because `pipefail` is not portable.
   - For Bash entrypoints that install an `ERR` trap, use `set -Eeuo pipefail` so the trap is inherited by functions, command substitutions, and subshells.
3. Quote and validate inputs
   - Quote all variable expansions unless intentionally relying on splitting/globbing.
   - Validate arguments count and basic shape before performing work.
   - Avoid `eval` and executing untrusted input.
4. Prefer simple, readable structure
   - Keep scripts small and linear where possible.
   - Put functions above the main execution flow.
   - Return early to reduce nesting.
5. Use linting and syntax checks
   - Run `shellcheck` for bash/sh where available.
   - Run interpreter syntax checks: `bash -n`, `sh -n`, `zsh -n`.

## Rules (Hard Constraints)

### Variable Naming
PROHIBITED: In any shell, declare or assign variables named `path`, `status`, `pipestatus`, `argv`, `commands`, `functions`, `options`, or `parameters`.

### Security
PROHIBITED: Use `eval` or `exec` with untrusted user input.
PROHIBITED: Hardcode secrets or credentials in shell scripts.
REQUIRED: Validate inputs before processing; reject unexpected values early.

### Error Handling
REQUIRED: Use strict mode for Bash and zsh entrypoints: `set -euo pipefail`.
REQUIRED: Use strict mode for POSIX `sh` entrypoints: `set -eu`.
PREFERRED: Under `set -e`, avoid `((i++))`/`((i--))` when counters can start at 0 (exit status becomes 1); prefer `((i+=1))` / `((++i))` for counters.
PROHIBITED: Ignore return codes from external commands.
PREFERRED: For Bash entrypoints, add a minimal failure trap for debugging context and enable errtrace so it propagates: `set -E; trap 'echo "Error on line $LINENO" >&2' ERR`.
PREFERRED: Do not emulate this pattern in POSIX `sh`; it has no portable `ERR` trap or errtrace equivalent.

### Portability
REQUIRED: If the target is POSIX `sh`, use only POSIX syntax (`[ ]`, no `[[ ]]`, no arrays).
PREFERRED: Do not assume macOS `/bin/bash` supports modern bash features; if you use bash-4+ features (e.g. `mapfile/readarray`, associative arrays), require bash 4+ explicitly (shebang/runtime) or provide a compatibility fallback.
PROHIBITED: Use zsh-only features in scripts intended for bash/sh environments.

### Data Handling
REQUIRED: Quote variables to prevent word splitting and glob expansion.
PROHIBITED: Implement multi-step structured data parsing in shell when a higher-level language is required by correctness/testability constraints (see the `language-decision-tree` skill).

### Persisted Script Escalation
PREFERRED: Revisit the implementation language through `language-decision-tree` when a persisted Shell script accumulates multi-step structured parsing, persistent state, complex retry or recovery, concurrency, multi-host distribution, embedded languages, or runtime and dependency management.
PREFERRED: Prefer Go for long-lived operational tooling when a single binary, cross-platform delivery, stable CLI contract, or reduced runtime state is a material benefit. This is a preference, not a mandatory replacement language; repository and ecosystem constraints still control the decision.
PROHIBITED: Split one reusable business rule across Shell and another implementation language.

### File Naming
REQUIRED: Name shell script files using hyphen style (kebab-case): `my-script.sh`, not `my_script.sh`

## macOS / Homebrew Notes (Agents + Non-Interactive)

- `#!/usr/bin/env bash` resolves via `PATH`; on macOS the default is often `/bin/bash` (3.2). If you need Bash 4+ features, require Homebrew Bash on `PATH` or use the host-appropriate absolute shebang (`/opt/homebrew/bin/bash` on Apple Silicon, `/usr/local/bin/bash` on Intel) for internal scripts.
- macOS login `zsh` runs `path_helper` (via `/etc/zprofile`), which can override PATH changes from `.zshenv`. For tasks explicitly testing `zsh -lc`, put the final Homebrew PATH setup in `.zprofile` after `path_helper`, using the host's `brew shellenv`.
- Homebrew `curl` is commonly keg-only; prefer `export PATH="$(brew --prefix curl)/bin:$PATH"` when you need modern curl/TLS features.
- Non-interactive bash sources `$BASH_ENV`; set it to a file that exports the PATH you expect (including Homebrew) if your automation runs `bash` non-interactively.
- Homebrew `*/libexec/gnubin` directories can replace macOS/BSD command semantics even when the host is macOS. Run `scripts/audit-homebrew-command-shadowing.py` when an option behaves unexpectedly or a script depends on a specific command dialect.
- Debug quickly: `command -v bash; /usr/bin/env bash --version | head -n1; type -a bash; command -v curl; curl --version | head -n1`.

### Homebrew Command Shadow Audit

The audit is read-only and emits deterministic JSON containing effective providers, duplicate providers, macOS system shadows, and gnubin-only commands:

```bash
python3 /absolute/path/to/skills/shell-guidelines/scripts/audit-homebrew-command-shadowing.py
```

Use `--path` for a synthetic or remote PATH snapshot, repeat `--system-dir` to replace the default macOS system directories, and add `--compact` for JSONL-oriented tooling.


## Operational Checks (Examples)

```bash
# Syntax
bash -n path/to/script.sh

# Lint
shellcheck path/to/script.sh
```

## Checklist

- Shell script files named with hyphen style (kebab-case): `my-script.sh`
- Correct shebang for target environment
- Strict mode enabled for Bash/zsh (`set -euo pipefail`) or POSIX `sh` (`set -eu`) entrypoints
- No declarations or assignments using prohibited Shell variable names
- No `eval`/unsafe execution of user input
- Variables quoted; inputs validated
- `shellcheck` clean (when available)

## Error Handling Examples

For generic error handling patterns (resilience, resource management, monitoring), see the `error-patterns` skill.

### Trap-Based Error Handler
```bash
#!/usr/bin/env bash
set -Eeuo pipefail

handle_error() {
    local exit_code=$?
    local line_number=$1
    echo "ERROR: Script failed on line $line_number with exit code $exit_code" >&2
    exit $exit_code
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
