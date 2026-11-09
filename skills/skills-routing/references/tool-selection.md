# Tool Selection

Read this when correctness, output volume, quoting, structure, or mutation risk makes an agent-side tool choice non-trivial. Routine `rg`, bounded file reads, and ordinary repository status checks need no selection pass. Nested interpreters, scratch scripts, and mutation safety are owned by [Ad Hoc Command Composition](adhoc-command-composition.md); persisted scripts are owned by `shell-guidelines`.

## Target Preflight

For an ambiguous multi-repository, runtime-specific, generated, ignored, or risky operation, identify the target before composing the command: `pwd`, `git rev-parse --show-toplevel`, and `test -e <target-path>`. When the current repository and read target are already unambiguous, start the command directly. Without a Git root, use path-scoped file checks. With several repositories or home directories in scope, record the active target path before drawing conclusions, and for runtime or host-specific work verify the active host and home context before importing assumptions from a previous incident. Before concluding a path is missing, check whether it is ignored, generated, mounted, or under a different home.

## Toolchain Preflight

Assume the preferred tools exist in the normal agent environment. Run `command -v <tool>` when a preferred tool fails with a not-found, PATH-like, or launcher error, when choosing a fallback after that failure, when diagnosing non-interactive, CI, or remote-shell PATH behavior, or when script logic must emit a deterministic missing-tool error.

Preferred tools with fallbacks:

- File discovery: `fd` → `find`
- Text search: `rg` → `grep`; lookaround or backreferences: `rg --pcre2` → a reviewable scratch script using the standard library
- Structural search or refactor: `ast-grep` → text search plus manual edit
- JSON extraction: `jq` → standard-library Python scratch script
- YAML validation or extraction: `yq` → `uvx --with pyyaml python3 <scratch-script>`

Plain `python3` fallbacks assume only the standard library; PyYAML, requests, pytest, and other third-party packages come through `uvx --with <package>`, with Python bytecode caches redirected when the script imports files from the target repository.

### macOS `stat` Dialect

Homebrew `gnubin` directories can shadow same-named commands under `/bin` and `/usr/bin`, so identify a command's dialect with `command -V`. When `stat` format semantics matter on macOS, call `/usr/bin/stat -f FORMAT -- <path>` for the BSD dialect or a verified GNU entry such as `gstat -c FORMAT -- <path>`. GNU `stat -f` requests file-system information and can emit plausible stdout while rejecting BSD operands, so a nonzero `stat` exit discards its stdout. Treat the first option or format error as a dialect mismatch: stop the batch, inspect `command -V stat`, select an explicit dialect, and validate on one representative target before continuing.

## Search And Output

Use bounded searches directly when the target is clear, scoping the directory and output (`head`, `sed -n`, targeted globs). For `rg`, exit code `1` is a no-match result. Before a broad replacement, preview representative matches and relevant exclusions, reusing the current diff or already-read files when they provide that evidence. Use a structured refactor when syntax matters and the tool fits; an ordinary bounded edit needs no new refactoring tool or scratch script. For large JSONL histories such as Codex or Claude sessions, prefer a bounded structured parser that filters injected system or skill text before treating matches as user intent.

## Long Execution

When the active tool can retain a long execution, use that path for the same execution: observation, waiting, extending a deadline, and cancellation are distinct operations, and reading output or releasing a wait leaves the execution running. If the active tool cannot retain the execution or wake the agent on completion, say so and keep the command on the supported foreground or bounded-wait path.
