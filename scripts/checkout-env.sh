#!/usr/bin/env bash
# Resolve checkout-specific, source-external state for this repository.
#
# Sourced by scripts/check.sh and evaluated by mise through `_.source`, so the
# independent check entrypoint and the mise context agree on the same mutable
# paths. Shared download caches keep native defaults; Ruff gets an external
# fallback when no user/global cache is configured.
set -euo pipefail

checkout_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cache_root=${XDG_CACHE_HOME:-${HOME:?HOME must be set}/.cache}
# Use a fixed-length identity: lossy path slugs can alias different checkouts.
if command -v sha256sum >/dev/null 2>&1; then
  checkout_key=$(printf '%s' "$checkout_root" | sha256sum)
else
  checkout_key=$(printf '%s' "$checkout_root" | shasum -a 256)
fi
checkout_key=${checkout_key%% *}

export PYTHONDONTWRITEBYTECODE=1
export UV_PROJECT_ENVIRONMENT="${cache_root}/uv-projects/agent-skills-${checkout_key}"
export PYTEST_CACHE_DIR="${cache_root}/pytest/agent-skills-${checkout_key}"
export RUFF_CACHE_DIR="${RUFF_CACHE_DIR:-${cache_root}/ruff}"
# Pytest does not read PYTEST_CACHE_DIR itself. Cover direct `uv run pytest`
# while preserving other caller options and quoting paths with spaces.
printf -v pytest_cache_option '%q' "cache_dir=$PYTEST_CACHE_DIR"
export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:-} -o $pytest_cache_option"
