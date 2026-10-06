# Python Tooling And Environments

Use this reference when configuring project tooling, running dependency-bearing one-offs, or diagnosing a test environment. The environment and toolchain policy remains in [Python Guidelines](../SKILL.md).

## Project Environments And Caches

Resolve the owning project and its existing storage convention. Select a project-specific external `UV_PROJECT_ENVIRONMENT` before using project commands; do not silently reuse an unrelated environment. In wrappers, choose an explicit namespace from the project/module identity rather than deriving it from the wrapper's path, so moving the wrapper does not change cache identity.

These are examples of external locations, not overrides of a project or host's declared root:

| Variable or setting | Example value | Responsibility |
| --- | --- | --- |
| `UV_PROJECT_ENVIRONMENT` | `$HOME/.cache/uv-projects/<namespace>` | The owning project's virtual environment, separate from its source tree. |
| `UV_CACHE_DIR` | `$HOME/.cache/uv` | uv's package/build cache; the default shared cache is suitable unless the environment requires another root. |
| `PYTHONDONTWRITEBYTECODE` | `1` | Primary suppression of `.pyc` generation. |
| `PYTHONPYCACHEPREFIX` | `$HOME/.cache/python/<namespace>` | Defensive redirect when a child process or command writes bytecode. |
| `RUFF_CACHE_DIR` | `$HOME/.cache/ruff/<namespace>` | Ruff's cache rather than `.ruff_cache` in the project. |
| pytest `cache_dir` | `$HOME/.cache/pytest/<namespace>` | Project-specific test state rather than `.pytest_cache` in the project. |

`uv venv` can honor `UV_PROJECT_ENVIRONMENT` at the project root; an explicit target is preferable when creating an environment from another directory. Check the installed uv's behavior when it matters. Existing virtual environments can be replaced by creation commands, so inspect ownership and compatibility before creating one; normal `uv run` or `uv sync` use is not a reason to recreate it. Keep one-shot environments task-owned and clean them up after verification.

For project-owned tooling, use the pinned tool from the owning environment. For a deliberately independent Ruff diagnostic with no project-pinned tool available, an explicit cache setup can accompany `uv tool run ruff`; do not present that fallback as the project's authoritative gate.

## pytest Setup

Use a namespaced external cache through the owning project's `pyproject.toml` or a command override:

```toml
[tool.pytest.ini_options]
cache_dir = "~/.cache/pytest/<namespace>"
```

```bash
uv run pytest -o "cache_dir=$HOME/.cache/pytest/<namespace>"
```

If using `PYTEST_ADDOPTS`, remember that it can override project options; do not share one pytest cache across projects, since state such as `--lf` can cross-contaminate results.

Before a test run, inspect the owning project's configuration and dependencies. Resolve whether configured `addopts` need plugins such as `pytest-cov`; do not assume a repository-root environment owns every subproject. Prefer the owning environment for project tests. A one-off `uvx --with pytest --with pytest-cov pytest ...` can support a narrow diagnostic; disabling addopts with `-o addopts=''` is also diagnostic, not a substitute for a required coverage or plugin-enabled gate.

## One-Off Dependencies

Plain `python3` may assume only the standard library. Do not rely on third-party packages being present in system Python or mise-managed Python, and do not install packages globally to make an agent command work.

- Run project-owned code through the owning project environment.
- For a one-off requiring packages, use `uvx --with <package> python3 ...` or `uv run --no-project --with <package> python3 ...`. These are not a reason to create an environment or metadata in the source project.
- For YAML one-offs, prefer `yq`; if Python is needed, use an explicit dependency such as `uvx --with pyyaml python3 ...`.
- For stdlib-only `uv run --no-project --script` entrypoints, omit the project environment setting unless that environment is actually needed. Still apply bytecode/cache isolation when importing repository files.

For non-trivial scratch logic, write a reviewable script in a task-owned external scratch location instead of nesting source inside shell quoting. Syntax-check it, pass needed dependencies explicitly and remove task-owned temporary material after use. Cache reuse does not grant permission to retain an entire one-shot environment indefinitely.

A project or one-off environment stored outside the tree still does not protect the checkout. Test runs, ad-hoc scripts, and coverage tooling can create untracked or ignored files under the project; inspect `git status --ignored` after verification and remove task-owned scratch and per-run state, without deleting another owner's retained cache.
