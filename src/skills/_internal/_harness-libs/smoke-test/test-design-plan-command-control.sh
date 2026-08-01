#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

fail() {
  printf 'test-design-plan-command-control: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"
  rg -n "$pattern" "$ROOT_DIR/$file_ref" >/dev/null || fail "$message"
}

main() {
  assert_contains "commands/design-change.md" 'design-runner\.sh' "design command should validate artifact before review"
  assert_contains "commands/design-change.md" 'coding:review-change' "design command should route through top-level review gate"
  assert_contains "commands/design-change.md" 'approval_status:[[:space:]]*pending|approval_status:[[:space:]]*approved' "design command should carry approval status gate"
  assert_contains "commands/design-change.md" 'coding:plan-change|next_entry: plan-change' "design command should hand off explicitly"

  assert_contains "commands/plan-change.md" 'plan-runner\.sh' "plan command should validate artifact before review"
  assert_contains "commands/plan-change.md" 'coding:review-change' "plan command should route through top-level review gate"
  assert_contains "commands/plan-change.md" 'approval-status|approval_status:[[:space:]]*approved' "plan command should machine-check approved upstream design"
  assert_contains "commands/plan-change.md" 'approval_status:[[:space:]]*pending|approval_status:[[:space:]]*approved' "plan command should carry approval status gate"
  assert_contains "commands/plan-change.md" 'coding:implement-change|next_entry: implement-change' "plan command should hand off explicitly"

  assert_contains "commands/plan-change.md" 'semantic-routing' "plan command should provide semantic routing advice"
  assert_contains "commands/plan-change.md" 'inherit-main' "plan command should preserve topology under inherit-main"
  assert_contains "commands/implement-change.md" 'logical topology' "implement command should leave logical topology to planning"
  assert_contains "commands/implement-change.md" 'runtime binding' "implement command should own runtime binding"
}

main "$@"
