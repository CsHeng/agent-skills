#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

fail() {
  printf 'test-sovereign-command-surface: %s\n' "$*" >&2
  exit 1
}

assert_file() {
  local file_ref="$1"
  [[ -f "$ROOT_DIR/$file_ref" ]] || fail "missing file: $file_ref"
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"

  rg -n "$pattern" "$ROOT_DIR/$file_ref" >/dev/null || fail "$message"
}

main() {
  local command=""
  local command_names=(
    analyze-project
    design-change
    plan-change
    implement-change
    review-change
    sync-truth
    close-change
  )

  for command in "${command_names[@]}"; do
    assert_file "commands/${command}.md"
    assert_contains "commands/${command}.md" "^---$" "missing frontmatter in commands/${command}.md"
    assert_contains "commands/${command}.md" "coding:${command}" "command ${command} should invoke matching skill"
  done

  assert_contains "commands/implement-change.md" 'coding:implement-change' "implement command should route through sovereign controller"
  assert_contains "commands/implement-change.md" 'Workers cannot delegate recursively' "implement command should preserve worker boundary"

  if rg -n "[~]/.codex|/(home|Users)/[^/]+/.codex" "$ROOT_DIR/README.md" "$ROOT_DIR/AGENTS.md" "$ROOT_DIR/commands" >/dev/null; then
    fail "plugin command surface should not depend on ~/.codex paths"
  fi
}

main "$@"
