#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Checkout-specific mutable state stays outside the source tree and matches the mise
# context; shared uv/ruff caches keep their native defaults. The helper is the single
# source of truth for both this standalone entrypoint and mise `_.source`.
# shellcheck source=scripts/checkout-env.sh
source "$repo_root/scripts/checkout-env.sh"

check_python="${CHECK_PYTHON:-python3}"
check_uv="${CHECK_UV:-uv}"

run_gate() {
  local label="$1"
  shift
  printf 'check: %s\n' "$label" >&2
  "$@"
}

non_exec_shells="$(git ls-files -s -- '*.sh' | awk '$1 != "100755" { print $4 }')"
if [[ -n "$non_exec_shells" ]]; then
  echo "ERROR: tracked .sh files must be mode 100755 (git update-index --chmod=+x):" >&2
  printf '%s\n' "$non_exec_shells" >&2
  exit 1
fi

run_gate contract-package "$check_python" scripts/check-contracts.py
run_gate install-surface "$check_python" scripts/check-install-surface.py
run_gate diagrams bash scripts/render-diagrams.sh --check
run_gate ruff "$check_uv" run ruff check scripts/skill_portability.py scripts/check-install-surface.py
run_gate ty "$check_uv" run ty check scripts/skill_portability.py scripts/check-install-surface.py
run_gate pytest "$check_uv" run pytest -o "cache_dir=$PYTEST_CACHE_DIR"
markdown_args=(--root "$repo_root" --mode check --exclude archived)
run_gate markdown "$check_python" skills/organize-docs/scripts/normalize-markdown-prose.py "${markdown_args[@]}"
