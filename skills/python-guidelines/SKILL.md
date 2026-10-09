---
name: python-guidelines
description: "Use for Python code, scripts, and services: uv, ruff, ty or mypy, pytest, packaging, CLI/service patterns, controller or remote runtime contracts, and review."
---

# Python Guidelines

Apply Python coding and tooling policy to Python files, scripts, CLIs, services and reviews. The primary workflow owns scope, mutation and delivery. For an unsettled language or ad hoc tool choice, read only `references/language-selection.md` or `references/tool-selection.md` in `skills-routing`, respectively.

Environment tooling below supports Python that is already justified; it does not justify selecting Python or adding dependencies. When a standard-library script would acquire third-party runtime packages, apply language selection before expanding its environment: the exception requires a business-matched capability or framework integration available only through Python. Keep that production decision separate from existing verification tooling.

## Toolchain And Environment

- For a Python project with managed dependencies, use `uv` for dependencies and tool execution, `pyproject.toml` for configuration, project-pinned Ruff for formatting and linting, and pytest for tests. Prefer `ty`; use mypy or pyright when the project requires it.
- A standard-library-only script or short embedded fragment may use an available interpreter directly. Do not create a project environment, package, or service merely to run it; keep inputs separate from source and honor the host's runtime contract.
- For code owned by a Python project, resolve the nearest owner, including in multi-project repositories. Run project commands through that environment with `uv run --project <project-root> ...` or from the owning project root.
- Set `UV_PROJECT_ENVIRONMENT` to an explicit, project-specific path outside the source tree, following the project or host's existing storage contract. Do not let project operations fall back to an in-tree `.venv`, or inherit another project's environment.
- Environment creation is separate from use. Create only a needed, task-owned environment; an explicit `uv venv "$UV_PROJECT_ENVIRONMENT"` target avoids working-directory ambiguity. Creation can replace an existing environment, so it is not a routine preflight before each check. Do not move, recreate or delete an existing environment merely to apply this guidance.
- Keep tool caches and bytecode outside the source tree. `UV_CACHE_DIR` controls uv's package/build cache, not the project environment. Use `PYTHONDONTWRITEBYTECODE=1` and a defensive `PYTHONPYCACHEPREFIX`; configure Ruff and pytest caches explicitly when the environment is unknown.
- Caches and environments outside the tree do not by themselves protect the checkout: coverage data, test writes, and ad-hoc scratch can still appear as untracked or ignored files. After verification, inspect `git status --ignored` for task-owned contamination and remove owned scratch and per-run state.

For cache configuration, one-off dependencies and pytest preflight, read [Tooling And Environments](references/tooling-and-environments.md). That reference supplies setup details, not a second environment policy.

## Controller And Remote Execution

A configuration-management controller's temporary module execution, such as the Python module Ansible writes and runs on a managed host, belongs to the controller. Preserve Python modules, plugins, and collections where the framework owns that ecosystem; do not vendor, reimplement, or treat framework execution as a language-migration target.

- For a one-shot remote action, reuse the controller's built-in modules, local rendering, thin transported Shell, or a short Python fragment on the existing target runtime. Select by clarity and actual dependency cost; do not create a package, service, or binary only to carry that invocation.
- For an approved Go replacement of a persistent remote tool, build on the controller or CI for the target OS and architecture and distribute the binary or image; do not compile on the managed target. A retained Python application may use its declared managed interpreter/environment or a prebuilt image. Do not introduce Python into an explicitly constrained native target.
- When Python crosses a host or controller boundary, state the runtime and output contract explicitly: interpreter and dependency source, invocation, stdout result, and exit behavior.

## Coding Requirements

### Types And Constants

- Add type hints for all function parameters and return values, not only public APIs. Prefer `X | None` when the runtime supports it. Use `typing.Any` only for a hard constraint and document why it is necessary.
- Replace magic numbers with named constants. Use `UPPER_SNAKE_CASE` and include units where relevant, such as `TIMEOUT_SECONDS`.
- Do not use mutable default arguments.

### Errors And Security

- Validate inputs early; catch specific exceptions and give actionable errors with context. Do not use bare `except:` in production code.
- Catch generic exceptions only at boundaries with specific handling, structured logging and re-raise or wrapping. Keep error classification and recovery choices with `error-patterns` when those decisions arise.
- Define domain-specific exception classes for domain errors, inheriting from appropriate base classes. Include useful context in exception messages without leaking sensitive values.
- Do not hardcode secrets, credentials or configuration values. Redact tokens, passwords and keys in logs.

### Formatting And Linting

- Use the owning project's pinned Ruff through `uv run ruff`, with configuration in `pyproject.toml`; do not replace it with an unpinned tool invocation.
- Keep safe fixes (`ruff check --fix --no-unsafe-fixes`) separate from formatting (`ruff format`). Do not enable unsafe fixes through flags or configuration.
- Do not chain `ruff check --fix && ruff format`: exit 1 means residual diagnostics and must not skip formatting. Continue after that exit, but stop on a tool error; keep every final lint, format and type failure unsuppressed.
- Limit changes to authorized files. Do not invent a numeric line-length gate that fights the formatter, or rewrite strings, comments or behavior only to satisfy pure line length.

### Tests And Documentation

- Use pytest by default, testing core behavior directly and keeping CLI plumbing thin. Cover happy and failure paths for critical logic.
- Choose the verification language independently of the production language. Retain useful Python tests and fixture generators for a Go or Shell product when their controller or CI runtime is affordable; removing Python from production targets does not require removing it from verification.
- Use docstrings for public modules, classes and functions. Prefer Google-style docstrings for public APIs, including usage expectations when they help maintainability.

## Operational Commands (Examples)

Prefer the owning project's versioned command entrypoint. This Bash example assumes an existing uv lockfile and runs from the owning project root; replace the namespace, storage paths and authorized file list with the project's values. The environment exports select an environment for use; they do not recreate it. Exit 1 from the initial fix pass does not make the final result acceptable, and other tool errors stop execution.

```bash
set -euo pipefail
export UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv-projects/<namespace>"
export RUFF_CACHE_DIR="$HOME/.cache/ruff/<namespace>"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$HOME/.cache/python/<namespace>"
files=(path/to/changed.py)

uv run --locked ruff check --fix --no-unsafe-fixes -- "${files[@]}" || {
  ruff_exit_code=$?
  [ "$ruff_exit_code" -eq 1 ] || exit "$ruff_exit_code"
}
uv run --locked ruff format -- "${files[@]}"
uv run --locked ruff check -- "${files[@]}"
uv run --locked ruff format --check -- "${files[@]}"
uv run --locked ty check .
uv run --locked pytest -q -o "cache_dir=$HOME/.cache/pytest/<namespace>"
```

## Task-Specific References

- Read [Script And CLI Patterns](references/script-patterns.md) for interfaces, invocation and script structure.
- Read [Service Patterns](references/service-patterns.md) for service boundaries and tests.
- Read [Review Checks](references/review-checklist.md) for read-only language review evidence. The calling review owner retains the report and verdict.
