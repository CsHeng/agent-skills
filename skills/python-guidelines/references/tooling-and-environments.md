# Python Tooling And Environments

Use this reference when configuring project tooling, running dependency-bearing one-offs, or diagnosing a test environment. The environment and toolchain policy remains in [Python Guidelines](../SKILL.md).

## Project Environments And Caches

Resolve the owning project and its existing storage convention. Keep the project's mutable environment and per-project test state distinct from shareable caches, and choose paths from the project or host storage contract rather than one fixed global directory. `UV_PROJECT_ENVIRONMENT` names one project's or subproject's environment and is reused across runs, not recreated per task; the cache settings below may be shared. In wrappers, choose an explicit project identity rather than deriving it from the wrapper's path, so moving the wrapper does not change identity.

These are examples of the owning project or host's declared roots, not overrides of it:

| Variable or setting | Example value | Ownership and sharing |
| --- | --- | --- |
| `UV_PROJECT_ENVIRONMENT` | `<project-env-root>/<project>` | Mutable environment for one owning project or subproject; project-scoped, reused across runs, never shared between projects or replaced per task. |
| `UV_CACHE_DIR` | `<cache-root>/uv` | uv's package/build cache; shareable across projects and not the project environment. |
| `PYTHONDONTWRITEBYTECODE` | `1` | Suppresses `.pyc` generation; a flag, not a storage location. |
| `PYTHONPYCACHEPREFIX` | `<cache-root>/python` | Reusable bytecode cache redirect kept out of the source tree. |
| `RUFF_CACHE_DIR` | `<cache-root>/ruff` | Reusable lint cache; a shared external location is suitable unless the project requires isolation. |
| pytest `cache_dir` | `<project-test-state-root>/<project>` | Per-project mutable test state (`lastfailed`, `--lf`); give each project its own directory and do not treat it as a shared cache. |

`uv venv` can honor `UV_PROJECT_ENVIRONMENT` at the project root; an explicit target is preferable when creating an environment from another directory. Check the installed uv's behavior when it matters. Existing virtual environments can be replaced by creation commands, so inspect ownership and compatibility before creating one; normal `uv run` or `uv sync` use is not a reason to recreate a project environment. Only a genuinely one-shot throwaway environment is task-owned, and it is removed after verification.

For project-owned tooling, use the pinned tool from the owning environment. For a deliberately independent Ruff diagnostic with no project-pinned tool available, an explicit cache setup can accompany `uv tool run ruff`; do not present that fallback as the project's authoritative gate.

## pytest Setup

Use a per-project external test-state directory through the owning project's `pyproject.toml` or a command override. pytest's `cache_dir` holds mutable per-project state rather than a shared cache:

```toml
[tool.pytest.ini_options]
cache_dir = "<project-test-state-root>/<project>"
```

```bash
uv run pytest -o "cache_dir=<project-test-state-root>/<project>"
```

If using `PYTEST_ADDOPTS`, remember that it can override project options; do not share one pytest cache across projects, since state such as `--lf` can cross-contaminate results.

Before a test run, inspect the owning project's configuration and dependencies. Resolve whether configured `addopts` need plugins such as `pytest-cov`; do not assume a repository-root environment owns every subproject. Prefer the owning environment for project tests. A one-off `uvx --with pytest --with pytest-cov pytest ...` can support a narrow diagnostic; disabling addopts with `-o addopts=''` is also diagnostic, not a substitute for a required coverage or plugin-enabled gate.

## One-Off Dependencies

Plain `python3` may assume only the standard library. Do not rely on third-party packages being present in system Python or mise-managed Python, and do not install packages globally to make an agent command work.

- Run project-owned code through the owning project environment.
- For a one-off requiring packages, use `uvx --with <package> python3 ...` or `uv run --no-project --with <package> python3 ...`. These are not a reason to create an environment or metadata in the source project.
- For YAML one-offs, prefer `yq`; if Python is needed, use an explicit dependency such as `uvx --with pyyaml python3 ...`.
- Standard-library-only scripts and fragments may use an available `python3` directly without a virtual environment. If using `uv run --no-project --script`, omit the project environment setting unless it is needed. Apply bytecode/cache isolation when importing repository files.

For scratch logic whose quoting or size makes embedding hard to review, write a script in a task-owned external scratch location. A short `python -c` or quoted heredoc is valid when it remains clear and passes data separately from source. Syntax-check substantial scratch code, pass needed dependencies explicitly and remove task-owned temporary material after use. Cache reuse does not grant permission to retain an entire one-shot environment indefinitely.

A project or one-off environment stored outside the tree still does not protect the checkout. Test runs, ad-hoc scripts, and coverage tooling can create untracked or ignored files under the project; inspect `git status --ignored` after verification and remove task-owned scratch and per-run state, without deleting another owner's retained cache.
