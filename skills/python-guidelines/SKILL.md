---
name: python-guidelines
description: "Apply Python policy as a conditional overlay when writing or reviewing Python code, scripts, and services: uv, ruff, ty or mypy, pytest, packaging, CLI/service patterns, and controller or remote runtime contracts. Choosing Python for a new persisted component is language selection in skills-routing."
---

# Python Guidelines

Apply Python coding and tooling policy to Python files, scripts, CLIs, services and reviews. An unsettled language or ad hoc tool choice reads `references/language-selection.md` or `references/tool-selection.md` in `skills-routing`. A standard-library script that would acquire third-party runtime packages applies language selection before its environment expands.

## Toolchain And Environment

Apply the environment-scope rules in `development-standards`; these are the Python mappings.

- A Python project with managed dependencies uses `uv` for dependencies and tool execution, `pyproject.toml` for configuration, project-pinned Ruff for formatting and linting, and pytest for tests. Type-check with the checker the project configures (`mypy` or `pyright`), and with `ty` when the project declares none.
- A standard-library-only script or short embedded fragment runs directly on the available interpreter; keep inputs separate from source and honor the host's runtime contract.
- Resolve the nearest owning project, including in multi-project repositories, and run its commands with `uv run --project <project-root> ...` or from the owning project root.
- Point every project operation at the owning project's external `UV_PROJECT_ENVIRONMENT`, following the project or host's storage contract. The environment is project-scoped and reused across runs. Create it only when it is missing, and reuse a compatible existing one.
- Keep reusable caches and bytecode outside the source tree, distinct from the project environment, and give each owning project its own pytest `cache_dir`.

Read [Tooling And Environments](references/tooling-and-environments.md) for cache variables, pytest setup, one-off dependencies, and the post-verification check for untracked or ignored files.

Read [Controller And Remote Execution](references/controller-and-remote.md) when Python crosses a host or controller boundary, such as an Ansible module or a remote action.

## Coding Requirements

### Types And Constants

- Add type hints for all function parameters and return values. Use `X | None` when the runtime supports it, and `typing.Any` only for a hard constraint, with the reason documented.
- Replace magic numbers with named `UPPER_SNAKE_CASE` constants that include units where relevant, such as `TIMEOUT_SECONDS`.
- Default a mutable argument to `None` and build the value inside the function.

### Errors And Security

- Validate inputs early and raise actionable errors with context. Catch a specific exception type.
- Catch generic exceptions only at boundaries, with specific handling, structured logging and re-raise or wrapping. Error classification and recovery choices follow `error-patterns`.
- Define domain-specific exception classes inheriting from appropriate base classes, with useful context and without sensitive values in messages.
- Load secrets, credentials and configuration values from the environment or project configuration, and redact tokens, passwords and keys in logs.

### Formatting And Linting

- Use the owning project's pinned Ruff through `uv run ruff`, configured in `pyproject.toml`.
- Run `ruff check --fix --no-unsafe-fixes`, then `ruff format`, as separate commands; continue after exit 1 (residual diagnostics) and stop on any other non-zero exit. Resolve every final lint, format and type failure rather than suppressing it.
- Limit changes to authorized files, and let the formatter own line length.

### Tests And Documentation

- Use pytest by default, testing core behavior directly and keeping CLI plumbing thin. Cover happy and failure paths for critical logic.
- Use docstrings for public modules, classes and functions, in Google style for public APIs.

## Operational Commands (Examples)

Prefer the owning project's versioned command entrypoint. This Bash example runs from the owning project root with an existing uv lockfile; replace the placeholders with the project's declared environment and cache locations and the file list with the authorized files. The exports select an environment for use.

```bash
set -euo pipefail
# One project or subproject per environment; caches may be shared, per-project test state may not.
export UV_PROJECT_ENVIRONMENT="<project-env-root>/<project>"
export UV_CACHE_DIR="<cache-root>/uv"
export RUFF_CACHE_DIR="<cache-root>/ruff"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="<cache-root>/python"
files=(path/to/changed.py)

uv run --locked ruff check --fix --no-unsafe-fixes -- "${files[@]}" || {
  ruff_exit_code=$?
  [ "$ruff_exit_code" -eq 1 ] || exit "$ruff_exit_code"
}
uv run --locked ruff format -- "${files[@]}"
uv run --locked ruff check -- "${files[@]}"
uv run --locked ruff format --check -- "${files[@]}"
uv run --locked ty check .
uv run --locked pytest -q -o "cache_dir=<project-test-state-root>/<project>"
```

## Task-Specific References

- Read [Script And CLI Patterns](references/script-patterns.md) for interfaces, invocation and script structure.
- Read [Service Patterns](references/service-patterns.md) for Python service conventions.
- Read [Review Checks](references/review-checklist.md) for read-only language review evidence.
