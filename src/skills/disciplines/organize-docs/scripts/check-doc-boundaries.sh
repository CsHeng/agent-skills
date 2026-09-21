#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DOCS_DIR="$ROOT_DIR/docs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR"

[[ -f "$DOCS_DIR/AGENTS.md" ]] || { echo "missing docs/AGENTS.md" >&2; exit 1; }
[[ -f "$DOCS_DIR/README.md" ]] || { echo "missing docs/README.md" >&2; exit 1; }

# A project may keep stage material with an external documentation owner.
# When a local stage tree exists, it must remain tracked and search-suppressed.
if [[ -d "$DOCS_DIR/plans" ]]; then
  [[ -f "$DOCS_DIR/.ignore" ]] || { echo "missing docs/.ignore" >&2; exit 1; }
  rg -qx 'plans/' "$DOCS_DIR/.ignore"
  if git check-ignore -q docs/plans/example.md; then
    echo "docs/plans should not be Git-ignored" >&2
    exit 1
  fi
  if rg --files docs | grep -q '^docs/plans/'; then
    echo "default docs file search unexpectedly listed stage artifacts" >&2
    exit 1
  fi
fi

NORMALIZER_ARGS=(--root "$ROOT_DIR" --mode check --exclude archived)
# Optional compatibility for projects that deliberately retain pinned originals.
if [[ -f "$ROOT_DIR/contracts/markdown-prose.toml" ]]; then
  NORMALIZER_ARGS+=(--immutable-manifest "$ROOT_DIR/contracts/markdown-prose.toml")
fi
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="$HOME/.cache/python/organize-docs" \
python3 "$SCRIPT_DIR/normalize-markdown-prose.py" "${NORMALIZER_ARGS[@]}"
