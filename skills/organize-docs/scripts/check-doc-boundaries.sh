#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DOCS_DIR="$ROOT_DIR/docs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR"

[[ -f "$DOCS_DIR/.ignore" ]] || { echo "missing docs/.ignore" >&2; exit 1; }
rg -qx 'plans/' "$DOCS_DIR/.ignore"

[[ -f "$DOCS_DIR/AGENTS.md" ]] || { echo "missing docs/AGENTS.md" >&2; exit 1; }
[[ -f "$DOCS_DIR/README.md" ]] || { echo "missing docs/README.md" >&2; exit 1; }

rg -n "stable truth|stage artifacts|search tools|Git tracking|docs/.ignore" \
  "$DOCS_DIR/AGENTS.md" >/dev/null

rg -n "avoid \`docs/plans/\`|docs/plans|--no-ignore|Keep stage artifacts in Git" \
  "$DOCS_DIR/README.md" >/dev/null

if git check-ignore -q docs/plans/example.md; then
  echo "docs/plans should not be Git-ignored" >&2
  exit 1
fi

if rg --files docs | rg -q '^docs/plans/'; then
  echo "default docs file search unexpectedly listed stage artifacts" >&2
  exit 1
fi

rg --files --no-ignore docs | rg -q '^docs/plans/'

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/organize-docs" \
python3 "$SCRIPT_DIR/normalize-markdown-prose.py" \
  --root "$ROOT_DIR" \
  --mode check
