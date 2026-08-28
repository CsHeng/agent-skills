#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

cache_root="${HOME:?HOME must be set}/.cache"
export UV_CACHE_DIR="$cache_root/uv/agent-skills"
export UV_PROJECT_ENVIRONMENT="$cache_root/uv-projects/agent-skills"
export RUFF_CACHE_DIR="$cache_root/ruff/agent-skills"
export PYTHONPYCACHEPREFIX="$cache_root/python/agent-skills"
export PYTEST_CACHE_DIR="$cache_root/pytest/agent-skills"
export PYTHONDONTWRITEBYTECODE=1

check_python="${CHECK_PYTHON:-python3}"
check_uv="${CHECK_UV:-uv}"

run_gate() {
  local label="$1"
  shift
  printf 'check: %s\n' "$label" >&2
  "$@"
}

if ! git check-ignore -q .dist/; then
  echo "ERROR: .dist must remain an ignored local output boundary" >&2
  exit 1
fi

if git ls-files --error-unmatch .dist >/dev/null 2>&1; then
  echo "ERROR: .dist must not contain tracked files" >&2
  exit 1
fi

non_exec_shells="$(git ls-files -s -- '*.sh' | awk '$1 != "100755" { print $4 }')"
if [[ -n "$non_exec_shells" ]]; then
  echo "ERROR: tracked .sh files must be mode 100755 (git update-index --chmod=+x):" >&2
  printf '%s\n' "$non_exec_shells" >&2
  exit 1
fi

run_gate contract-package "$check_python" scripts/check-contracts.py
run_gate generated-root-flat "$check_python" scripts/flatten-skills.py --target root-flat --check
run_gate install-surface "$check_python" scripts/check-install-surface.py
run_gate index "$check_python" scripts/generate-skills-index.py --check
run_gate diagrams "$check_python" scripts/generate-workflow-diagrams.py --check
run_gate ruff "$check_uv" run ruff check scripts/skill_distribution.py scripts/flatten-skills.py scripts/check-install-surface.py
run_gate ty "$check_uv" run ty check scripts/skill_distribution.py scripts/flatten-skills.py scripts/check-install-surface.py
run_gate pytest "$check_uv" run pytest -o "cache_dir=$PYTEST_CACHE_DIR"
markdown_args=(--root "$repo_root" --mode check)
if [[ "${STANDALONE_CHECK_ACTIVE:-0}" != "1" ]]; then
  markdown_args+=(--immutable-manifest contracts/markdown-prose.toml)
fi
run_gate markdown "$check_python" src/skills/disciplines/organize-docs/scripts/normalize-markdown-prose.py "${markdown_args[@]}"
