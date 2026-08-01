#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"

fail() {
  printf 'test-review-execute-command-control: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1" pattern="$2" message="$3"
  rg -n -- "$pattern" "$ROOT_DIR/$file_ref" >/dev/null || fail "$message"
}

main() {
  local implement_skill=""
  local workflow_contract=""
  case "$SKILL_SURFACE" in
    generated)
      implement_skill="skills/implement-change/SKILL.md"
      workflow_contract="skills/implement-change/references/workflow.toml"
      ;;
    source)
      implement_skill="src/skills/workflows/implement-change/SKILL.md"
      workflow_contract="src/skills/workflows/implement-change/references/workflow.toml"
      ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  assert_contains "commands/implement-change.md" 'execute-runner\.sh' "execute command should retain deterministic execution runner"
  assert_contains "commands/implement-change.md" 'approval_status:[[:space:]]*approved' "execute command should require plan approval"
  assert_contains "commands/implement-change.md" 'allowed_touch_set' "execute command should preserve touch-set enforcement"
  assert_contains "commands/implement-change.md" 'coding:review-change' "execute command should use top-level review semantics"
  assert_contains "$implement_skill" 'semantic-routing' "implementation skill should default eligible work to semantic routing"
  assert_contains "$implement_skill" 'inherit-main' "implementation skill should preserve inherit-main binding override"
  assert_contains "$workflow_contract" 'topology_owner = "plan-change"' "workflow should keep logical topology with planning"
  assert_contains "$workflow_contract" 'runtime_binding_owner = "implement-change"' "workflow should assign runtime binding to controller"
  assert_contains "$workflow_contract" 'delegated_recursion = false' "workflow should prevent recursive worker delegation"

  HARNESS_SKILL_SURFACE="$SKILL_SURFACE" bash "$ROOT_DIR/src/skills/_internal/_harness-libs/smoke-test/test-agent-native-review.sh"
}

main "$@"
