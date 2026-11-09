# Toolchain Baseline

Use this as a local development baseline when the target repository's version policy permits it.

## Versions

- Python: 3.13+ with `X | None` union syntax.
- Go: 1.23+.
- Lua: 5.4+ with `luac -p` validation when applicable.
- PlantUML: 1.2025.9+ with `plantuml --check-syntax` validation.

## Environment

- Use `mise` for tool version management unless the target repository defines another owner. A user-global mise configuration may own reusable caches, tool versions, and developer preferences; project-owned or repository-local tool settings ensure correctness independently and take precedence.
- Use `uv` for Python package and environment workflows when it matches the repository standard.
- Assume plain `python3` has only the standard library for ad hoc fallback commands.
- Use `uvx --with <package> python3 ...` for one-off Python commands that require third-party packages outside a project environment.
- Use the current Docker Compose specification with an omitted `version` field.

## Shell Entry Points

- Prefer `#!/usr/bin/env bash` for CI or portable repository scripts.
- Prefer `#!/bin/zsh` only for local interactive macOS shell helpers.
- Keep third-party CLI flags in their native style.
- For custom scripts, use named long options for write/delete behavior and prefer them for other options.
