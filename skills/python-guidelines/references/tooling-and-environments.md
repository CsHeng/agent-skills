# Python Tooling And Environments

Use this reference when configuring project tooling, running dependency-bearing one-offs, or diagnosing a test environment. Policy is in [Python Guidelines](../SKILL.md); this reference carries details.

## Project Environments And Caches

Resolve the owning project and its existing storage convention. Keep the project's mutable environment and per-project test state distinct from shareable caches, and choose paths from the project or host storage contract. `UV_PROJECT_ENVIRONMENT` names one project's or subproject's environment and is reused across runs; the cache settings below may be shared. In wrappers, choose an explicit project identity that remains stable when the wrapper moves.

These examples illustrate the owning project or host's declared roots:

| Variable or setting | Example value | Ownership and sharing |
| --- | --- | --- |
| `UV_PROJECT_ENVIRONMENT` | `<project-env-root>/<project>` | Mutable environment for one owning project or subproject; dedicated to that project or subproject and reused across runs. |
| `UV_CACHE_DIR` | `<cache-root>/uv` | uv's package/build cache; shareable across projects; the project environment has its own location. |
| `PYTHONDONTWRITEBYTECODE` | `1` | Suppresses `.pyc` generation; a flag. |
| `PYTHONPYCACHEPREFIX` | `<cache-root>/python` | Reusable bytecode cache redirect kept out of the source tree. |
| `RUFF_CACHE_DIR` | `<cache-root>/ruff` | Reusable lint cache; a shared external location is suitable unless the project requires isolation. |
| pytest `cache_dir` | `<project-test-state-root>/<project>` | Per-project mutable test state (`lastfailed`, `--lf`); give each project its own directory. |

`uv venv` can honor `UV_PROJECT_ENVIRONMENT` at the project root; an explicit target is preferable when creating an environment from another directory. Check the installed uv's behavior when it matters. Creation commands can replace an existing virtual environment, so inspect ownership and compatibility before creating one; `uv run` and `uv sync` reuse the environment. Only a genuinely one-shot throwaway environment is task-owned, and it is removed after verification.

For project-owned tooling, use the pinned tool from the owning environment. For a deliberately independent Ruff diagnostic with no project-pinned tool available, an explicit cache setup can accompany `uv tool run ruff`; report that fallback as diagnostic and keep the project's pinned tool as the authoritative gate.

## pytest Setup

Use a per-project external test-state directory through the owning project's `pyproject.toml` or a command override. pytest's `cache_dir` holds mutable per-project state:

```toml
[tool.pytest.ini_options]
cache_dir = "<project-test-state-root>/<project>"
```

```bash
uv run pytest -o "cache_dir=<project-test-state-root>/<project>"
```

`PYTEST_ADDOPTS` can override project options. Each project keeps its own pytest cache, since state such as `--lf` can cross-contaminate results across projects.

Before a test run, inspect the owning project's configuration and dependencies. Resolve whether configured `addopts` need plugins such as `pytest-cov`, and identify each subproject's owning environment. Prefer the owning environment for project tests. A one-off `uvx --with pytest --with pytest-cov pytest ...` can support a narrow diagnostic; disabling addopts with `-o addopts=''` is also diagnostic; run any required coverage or plugin-enabled gate separately.

## One-Off Dependencies

Plain `python3` may assume only the standard library. Declare third-party packages through the owning environment or `uvx`, and keep system and mise-managed Python unmodified.

- Run project-owned code through the owning project environment.
- For a one-off requiring packages, use `uvx --with <package> python3 ...` or `uv run --no-project --with <package> python3 ...`. Keep the one-off environment and metadata outside the source project.
- For YAML one-offs, prefer `yq`; if Python is needed, use an explicit dependency such as `uvx --with pyyaml python3 ...`.
- Standard-library-only scripts and fragments may use an available `python3` directly without a virtual environment. If using `uv run --no-project --script`, omit the project environment setting unless it is needed. Apply bytecode/cache isolation when importing repository files.

For scratch logic whose quoting or size makes embedding hard to review, write a script in a task-owned external scratch location. A short `python -c` or quoted heredoc is valid when it remains clear and passes data separately from source. Syntax-check substantial scratch code, pass needed dependencies explicitly and remove task-owned temporary material after use. Remove the task-owned one-shot environment after verification while reusing eligible caches.

Protect the checkout even when a project or one-off environment is stored outside the tree. Test runs, ad-hoc scripts, and coverage tooling can create untracked or ignored files under the project; inspect `git status --ignored` after verification and remove task-owned scratch and per-run state while preserving another owner's retained cache.
