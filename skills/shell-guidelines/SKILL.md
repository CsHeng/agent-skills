---
name: shell-guidelines
description: "Apply Shell policy to persisted scripts, CI or automation, constrained POSIX or BusyBox targets, non-trivial command fragments, and quoting, interpreter, portability, or safety reviews. Use as a conditional language overlay for the owning workflow; routine single-layer shell commands proceed directly."
---

# Shell Guidelines

Apply these rules to persisted or correctness-sensitive Shell: scripts (`.sh`, bash, zsh), CI and local automation, fragments whose quoting, expansion, interpreter, pipeline or failure behavior affects correctness, Shell for a constrained native runtime such as OpenWrt BusyBox ash or a target fixed to POSIX `sh`, Shell that must affect the invoking shell (sourced environments, profiles, launchers), and review or syntax audit of shell files. Ad hoc tool choice and command composition read `references/tool-selection.md` in `skills-routing`; language selection reads `references/language-selection.md` there.

## Progressive Disclosure

- Script structure, diagnostics and error-handling examples (the `ERR` trap, input validation): `references/script-patterns.md`
- A script targeting macOS or Homebrew `PATH`, needing Bash 4+, or an option behaving unexpectedly: `references/macos-homebrew.md`
- Read-only review checks: `references/review-checklist.md`

## Rules

### Interpreter

- Use `#!/bin/sh` and the ash/POSIX subset for BusyBox ash or a target contract fixed to POSIX `sh`; that constrained runtime keeps its native shell. Establish that constraint from the target contract. In POSIX `sh`, use `[ ]` and POSIX-compatible data structures.
- Use `#!/usr/bin/env bash` for CI and Linux bash, and `#!/usr/bin/env zsh` for zsh scripts. Keep zsh-only features in zsh scripts.
- Require Bash 4+ explicitly (shebang or runtime) or provide a compatibility fallback when a script uses `mapfile`/`readarray` or associative arrays; macOS `/bin/bash` is 3.2.

### Strict Mode And Failure

- Start Bash and zsh entrypoints with `set -euo pipefail`, and POSIX `sh` entrypoints with `set -eu` (portable POSIX `sh` uses `set -eu`).
- Give a Bash entrypoint with an `ERR` trap `set -Eeuo pipefail` and a minimal trap such as `trap 'echo "Error on line $LINENO" >&2' ERR`. In POSIX `sh`, check each command's status explicitly; the `ERR` trap is Bash and zsh only.
- Check the exit status of every external command, through `set -e` or an explicit test.
- Under `set -e`, increment counters with `((i+=1))` or `((++i))`; `((i++))` returns status 1 when the counter is 0.

### Inputs And Quoting

- Quote every variable expansion unless splitting or globbing is intended and documented.
- Validate the launcher's own inputs (argument presence and shape, environment variables it dereferences, paths it resolves) and reject unexpected values early. Domain parsing and state validation belong to the implementation the launcher starts.
- Treat user input as data: expand it quoted and pass it as arguments to a fixed command.
- Supply secrets and credentials through the environment or the project's secret mechanism.
- Use descriptive variable names such as `file_path` or `exit_status` in place of `path`, `status`, `pipestatus`, `argv`, `commands`, `functions`, `options` and `parameters` in any shell.
- Name script files in kebab-case: `my-script.sh`.

### Structure

- Keep scripts small and linear, with functions above the main flow, early returns, and each external mutation visible.
- Use an existing structured-data tool or a short embedded standard-library Python fragment when Shell parsing would be fragile; pass data separately from source through arguments, stdin or files. Choose a named script for readability; language selection follows the existing contract.
- Keep each reusable business rule in one implementation, in the language that owns it. A Shell entrypoint may locate and start a co-delivered implementation, and its normal delivery and update workflow stays intact.
- Keep an existing working Shell implementation, a simple script, a parent-shell effect, or a constrained native runtime in Shell. When parsing, state, recovery, concurrency or distribution cost makes it unreliable, read `references/language-selection.md` in `skills-routing` before proposing a rewrite.

### Temporary Files And Scope

- Create temporary files with `mktemp` or another native mechanism that respects `TMPDIR`, and clean only task-owned paths. Environment scope and temporary storage follow `development-standards`.
- Resolve script-owned resources from the script location or an explicit owning root, and keep them distinct from a CLI's intentionally caller-selected working directory.

## Checks

Run `shellcheck` for bash and sh where available, and the interpreter's syntax check (`bash -n`, `sh -n`, `zsh -n`):

```bash
bash -n path/to/script.sh
shellcheck path/to/script.sh
```

For generic error-handling patterns (resilience, resource management, monitoring), see `error-patterns`.
