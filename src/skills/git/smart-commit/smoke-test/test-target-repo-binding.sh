#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_FILE="$SKILL_DIR/SKILL.md"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

assert_contains() {
  local file_path="$1"
  local expected="$2"
  if ! grep -Fq -- "$expected" "$file_path"; then
    fail "$file_path missing expected text: $expected"
  fi
}

main() {
  assert_contains "$SKILL_FILE" 'TARGET_REPO'
  assert_contains "$SKILL_FILE" 'git -C "$TARGET_REPO"'
  assert_contains "$SKILL_FILE" 'Never use the plugin repository as the implicit target repository'
}

main "$@"
