#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! git check-ignore -q .dist/claude/skills; then
  echo "ERROR: .dist must remain ignored generated output" >&2
  exit 1
fi

if [[ -n "$(git ls-files -- .dist)" ]]; then
  echo "ERROR: .dist must not contain tracked files" >&2
  exit 1
fi

# Agents may exec skill/runtime shells directly; tracked .sh must keep git mode 100755.
non_exec_shells="$(git ls-files -s -- '*.sh' | awk '$1 != "100755" { print $4 }')"
if [[ -n "$non_exec_shells" ]]; then
  echo "ERROR: tracked .sh files must be mode 100755 (git update-index --chmod=+x):" >&2
  printf '%s\n' "$non_exec_shells" >&2
  exit 1
fi

install_surface_tmp="$(mktemp -d "${TMPDIR:-/tmp}/market-csheng-install-surfaces.XXXXXX")"
trap 'rm -rf "$install_surface_tmp"' EXIT

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/generate-skills-index.py --check

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/check-contracts.py

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/generate-workflow-diagrams.py --check

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/flatten-skills.py --target claude --dest "$install_surface_tmp/claude"

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/check-install-surface.py --target claude --dest "$install_surface_tmp/claude"

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/flatten-skills.py --target codex --dest "$install_surface_tmp/codex"

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/check-install-surface.py --target codex --dest "$install_surface_tmp/codex"

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/check-install-surface.py --target root-flat

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 scripts/check-fixtures.py

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/market-csheng" \
python3 -m unittest discover -s tests -p 'test_*.py'

for smoke_test in src/runtime/harness/smoke-test/test-*.sh; do
  bash "$smoke_test"
done

bash scripts/check-review-boundary.sh
