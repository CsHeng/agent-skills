#!/usr/bin/env bash
set -euo pipefail

echo "Installing coding@csheng plugin..."

usage() {
  cat <<'EOF'
Usage:
  ./install.sh [--scope user|project|local]

Defaults:
  --scope user

Notes:
  - When running as a Claude Code hook, CLAUDE_PROJECT_DIR points at the project root.
  - Project scope writes to: $CLAUDE_PROJECT_DIR/.claude/settings.json
  - Local scope writes to: $CLAUDE_PROJECT_DIR/.claude/settings.local.json
  - User scope writes to: $HOME/.claude/settings.json
EOF
}

SCOPE="user"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      shift
      SCOPE="${1:-}"
      shift || true
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      usage
      exit 2
      ;;
  esac
done

PLUGIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PLUGIN_DIR

SETTINGS_FILE=""
if [[ "$SCOPE" == "user" ]]; then
  SETTINGS_FILE="${CLAUDE_SETTINGS_FILE:-$HOME/.claude/settings.json}"
elif [[ "$SCOPE" == "project" ]]; then
  PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
  if [[ -z "$PROJECT_DIR" ]] && command -v git >/dev/null 2>&1; then
    PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  fi
  if [[ -z "$PROJECT_DIR" ]]; then
    echo "Project scope requires CLAUDE_PROJECT_DIR or a git worktree."
    exit 1
  fi
  SETTINGS_FILE="${CLAUDE_SETTINGS_FILE:-$PROJECT_DIR/.claude/settings.json}"
elif [[ "$SCOPE" == "local" ]]; then
  PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
  if [[ -z "$PROJECT_DIR" ]] && command -v git >/dev/null 2>&1; then
    PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  fi
  if [[ -z "$PROJECT_DIR" ]]; then
    echo "Local scope requires CLAUDE_PROJECT_DIR or a git worktree."
    exit 1
  fi
  SETTINGS_FILE="${CLAUDE_SETTINGS_FILE:-$PROJECT_DIR/.claude/settings.local.json}"
else
  echo "Invalid --scope: $SCOPE (expected: user|project|local)"
  exit 2
fi
readonly SETTINGS_FILE

if [[ ! -f "$SETTINGS_FILE" ]]; then
  mkdir -p "$(dirname -- "$SETTINGS_FILE")"
  printf '%s\n' '{}' > "$SETTINGS_FILE"
fi

if command -v jq >/dev/null 2>&1 && jq -e '.extraKnownMarketplaces["csheng"]' "$SETTINGS_FILE" >/dev/null 2>&1; then
    echo "Marketplace 'csheng' already configured"
else
    echo "Adding marketplace to settings.json..."

    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup.$(date +%s)"

    if command -v jq >/dev/null 2>&1; then
        tmp_file=$(mktemp)
        jq --arg path "$PLUGIN_DIR" \
            '.extraKnownMarketplaces["csheng"] = {"source": {"source": "directory", "path": $path}}' \
            "$SETTINGS_FILE" > "$tmp_file"
        mv "$tmp_file" "$SETTINGS_FILE"
        echo "Marketplace added successfully"
    else
        echo "jq not found. Install jq or manually add the marketplace:"
        echo ""
        echo "Add to $SETTINGS_FILE:"
        echo '{'
        echo '  "extraKnownMarketplaces": {'
        echo '    "csheng": {'
        echo '      "source": {'
        echo '        "source": "directory",'
        echo "        \"path\": \"${PLUGIN_DIR}\""
        echo '      }'
        echo '    }'
        echo '  }'
        echo '}'
        exit 1
    fi
fi

echo ""
echo "Plugin ready. Install it with:"
echo "   /plugin install coding@csheng"
echo ""
echo "Or for project-level installation (shared via git):"
echo "   /plugin install coding@csheng --scope project"
