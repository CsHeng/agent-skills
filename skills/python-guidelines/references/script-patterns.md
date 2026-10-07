# Python Script and CLI Patterns

## Purpose

Build maintainable scripts and CLIs with clear IO, logging, and testability.

## Scope

- Script/CLI layout and invocation patterns
- Dependency management expectations (uv/uvx)
- Error handling and the implementation of task-relevant diagnostics

Use the owning project's environment and tooling policy in [Python Guidelines](../SKILL.md). Environment creation, caches and one-off dependencies are detailed in [Tooling And Environments](tooling-and-environments.md).

## Deterministic Steps

1. Decide interface:
   - module entrypoint: `python -m package.cli`
   - or executable script with `#!/usr/bin/env python3`
2. Define IO contract:
   - arguments, inputs, outputs, exit codes
3. Choose diagnostics for the actual consumer:
   - use `logging-standards` when selecting log events, fields, levels or routing
   - implement only the events needed for the task; do not add start/end or per-branch logs by default
4. Fail fast with actionable errors:
   - validate inputs before doing work
5. Add tests for behavior of core functions (not CLI plumbing).

## Diagnostics And Logging

For a small one-shot script, useful stderr diagnostics and an accurate exit code may be sufficient. Keep stdout for the promised result, preserve error propagation, and avoid logging the same failure at every layer.

For an operational tool that needs logs, use the project's logging mechanism and the event contract selected through `logging-standards`. Python's standard `logging` module can implement that contract; timestamps, field sets, correlation and retention are consumer decisions, not a universal script template. Keep sensitive values out of diagnostics.

## Checklist

- Follow the canonical type-hint requirements in [Python Guidelines](../SKILL.md), including parameters and return values
- `if __name__ == "__main__":` guard for executable scripts
- Short embedded Python is readable, uses an available runtime, and receives data separately from source; extract a named Python script when quoting or reuse warrants it, without treating embedding as a language-migration signal
- Clear exit codes (0 success, non-zero failure)
