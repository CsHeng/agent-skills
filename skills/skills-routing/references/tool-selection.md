# Tool Selection

## Purpose

Select and compose agent-side tools when correctness, output volume, quoting, structure, or mutation risk makes the choice non-trivial. Routine `rg`, bounded file reads, and ordinary repository status checks do not require this reference. This method does not choose the implementation language for persisted repository code and does not own the task lifecycle.

## Progressive Disclosure

- Ad hoc command composition and nested-interpreter boundaries: [Ad Hoc Command Composition](adhoc-command-composition.md).

## Target Preflight

For ambiguous multi-repository, runtime-specific, generated, ignored, or risky operations, identify the target before composing the command:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null || true
test -e <target-path>
```

Rules:
- Skip this preflight when the current repository and bounded read target are already unambiguous.
- If no Git root exists, do not treat `git status` failure as a task blocker; switch to path-scoped file checks.
- If multiple repositories or home directories are in scope, print or record the active target path before drawing conclusions.
- For runtime or host-specific work, verify the active host/home context before importing assumptions from a previous incident.
- For missing paths, first verify whether the path is ignored, generated, mounted, or under a different home before concluding it does not exist.

## Toolchain Preflight

Assume the preferred tools exist in the normal agent environment. Do not run ritual `command -v` checks before ordinary searches.

Use `command -v <tool>` only when:
- the preferred tool fails with `command not found`, a PATH-like error, or an unexpected launcher/runtime error
- choosing between an explicit fallback path after the preferred command fails
- diagnosing host-specific, non-interactive, CI, or remote-shell PATH behavior
- writing script logic that must emit a deterministic missing-tool error or report optional capability availability

### macOS `stat` Dialect

Homebrew `gnubin` directories can shadow same-named commands under `/bin` and `/usr/bin`; do not infer a command's dialect from the operating system or command name alone. Treat formatted `stat` output as the highest-risk case:

- Do not use bare `stat` when format semantics matter on macOS. Use `/usr/bin/stat -f FORMAT -- <path>` for the macOS/BSD dialect or a verified GNU entry such as `gstat -c FORMAT -- <path>`.
- GNU `stat -f` requests file-system information and can emit plausible stdout while rejecting BSD format operands. If `stat` exits nonzero, discard its stdout rather than treating partial output as file metadata.
- Treat the first option or format error as a dialect mismatch signal. Stop the batch, inspect `command -V stat`, select an explicit dialect, and validate the corrected command on one representative target before applying it to the remaining targets.

Persisted scripts are not an ad hoc command choice: `shell-guidelines` owns their PATH, shebang, and portability handling, including its gnubin shadow audit for scripts that depend on a specific command dialect.

Preferred tools with explicit fallbacks:
- File discovery: `fd` -> `find`
- Text search: `rg` -> `grep`
- Text search with lookaround/backreferences: `rg --pcre2` -> reviewable scratch script using the standard library
- Structural search/refactor: `ast-grep` -> "text search + manual edit"
- JSON extraction: `jq` -> standard-library Python scratch script
- YAML validation/extraction: `yq` -> `uvx --with pyyaml python3 <scratch-script>`

### Python Fallback Dependencies

Plain `python3` fallback commands may assume only the Python standard library. Do not assume PyYAML, requests, pytest, or other third-party packages exist in system Python or mise-managed Python. When procedural fallback logic is more than a simple expression, put it in a repo-external scratch script, review it, syntax-check it, and invoke it directly instead of nesting Python source inside a Shell command string. For one-off parsing that needs a third-party package, use `uvx --with <package> python3 <scratch-script>` and redirect Python bytecode caches when the script imports files from the target repository.

## Progressive Search Workflow

Use bounded searches directly when the target is clear. A separate count is useful only when result volume or a proposed broad edit needs sizing; it is not a prerequisite for every read or multi-file change. Scope the directory and output rather than enumerating the whole repository to prove it is searchable.

For `rg`, exit code `1` means no matches when the command otherwise ran successfully. Treat it as a no-match search result, not a tool failure.

Before a broad replacement, preview representative matches and relevant exclusions to confirm the intended transformation and authorized scope. Reuse the current diff or already-read files when they provide that evidence; do not repeat a ritual count/preview pass.

```bash
rg -n "pattern" . | head -n 50
rg -n --context 2 "pattern" path/to/dir | head -n 80
```

Use `rg --pcre2` before patterns with lookaround or backreferences. If PCRE2 is unavailable, switch to a small reviewable parser in a repo-external scratch file instead of repeatedly retrying invalid `rg` syntax or compressing procedural logic into nested quoting.

Use a structured refactor when syntax matters and the tool is suitable. An ordinary bounded edit does not require a new refactoring tool, scratch script, or separate plan. A count alone proves neither scope nor correctness; inspect the resulting change and run the checks that protect its behavior.

## Output Control

REQUIRED: Avoid dumping unbounded command output into the session.
PREFERRED: Use `head`, `sed -n`, targeted globs, and directory scoping.

## Structured History Search

For large JSONL histories such as Codex or Claude sessions, prefer a bounded structured parser over raw text search. Identify the relevant files, parse JSON records, and filter injected system/skill text before treating matches as user intent; count separately only when volume affects the approach.

## Long Execution

When the active tool can retain a long execution, use that path for the same execution. Observation, waiting for an event, extending a deadline, and cancellation are different operations. Reading output or releasing a wait does not cancel or relaunch the execution. A deadline change applies to that same execution. Cancellation is an explicit stop, not the end of a wait.

If the active tool cannot retain the execution or wake the agent when it finishes, say so. Do not detach it with `&`, `nohup`, a bare background process, or another unmanaged workaround. A command that must finish before a dependent step stays on the supported foreground or bounded-wait path.

## Safety

PROHIBITED: Run destructive operations (mass edits, deletes, resets) without matching authority and an understood, scoped impact. A sufficient current request or approved plan can supply that scope; do not manufacture another planning artifact. Preview uncertain broad effects before mutation.
PROHIBITED: Interpolate untrusted values into executable Shell, Python, or other source strings.
PREFERRED: Avoid nested interpreters and generated code strings when a direct tool, single-layer command, or reviewable scratch script can express the operation.
