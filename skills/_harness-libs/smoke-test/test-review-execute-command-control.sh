#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

fail() {
  printf 'test-review-execute-command-control: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local path="$1" pattern="$2" message="$3"
  rg -n -- "$pattern" "$ROOT_DIR/$path" >/dev/null || fail "$message"
}

main() {
  assert_contains "commands/implement-change.md" 'execute-runner\.sh' "execute command should retain deterministic execution runner"
  assert_contains "commands/implement-change.md" 'approval_status:[[:space:]]*approved' "execute command should require plan approval"
  assert_contains "commands/implement-change.md" 'allowed_touch_set' "execute command should preserve touch-set enforcement"
  assert_contains "commands/implement-change.md" 'coding:review-change' "execute command should use top-level review semantics"

  bash "$ROOT_DIR/src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh"
}

main "$@"
