#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

fail() {
  printf 'test-review-execute-skill-control: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1" pattern="$2" message="$3"
  [[ "$file_ref" == /* ]] || file_ref="$ROOT_DIR/$file_ref"
  rg -n -- "$pattern" "$file_ref" >/dev/null || fail "$message"
}

main() {
  local implement_skill=""
  local workflow_contract=""
  case "$SKILL_SURFACE" in
    generated)
      implement_skill="$GENERATED_SKILLS_ROOT/implement-change/SKILL.md"
      workflow_contract="$GENERATED_SKILLS_ROOT/implement-change/references/workflow.toml"
      ;;
    source)
      implement_skill="src/skills/workflows/implement-change/SKILL.md"
      workflow_contract="src/skills/workflows/implement-change/references/workflow.toml"
      ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  assert_contains "$implement_skill" 'execute-runner\.sh' "implementation skill should retain deterministic execution runner"
  assert_contains "$implement_skill" 'approval-status.*approved' "implementation skill should require plan approval"
  assert_contains "$implement_skill" 'allowed_touch_set' "implementation skill should preserve touch-set enforcement"
  assert_contains "$implement_skill" 'review-change' "implementation skill should use top-level review semantics"
  assert_contains "$implement_skill" 'semantic-routing' "implementation skill should default eligible work to semantic routing"
  assert_contains "$implement_skill" 'inherit-main' "implementation skill should preserve inherit-main binding override"
  assert_contains "$workflow_contract" 'topology_owner = "plan-change"' "workflow should keep logical topology with planning"
  assert_contains "$workflow_contract" 'runtime_binding_owner = "implement-change"' "workflow should assign runtime binding to controller"
  assert_contains "$workflow_contract" 'delegated_recursion = false' "workflow should prevent recursive worker delegation"

  HARNESS_SKILL_SURFACE="$SKILL_SURFACE" \
    HARNESS_GENERATED_SKILLS_ROOT="$GENERATED_SKILLS_ROOT" \
    bash "$ROOT_DIR/src/runtime/harness/smoke-test/test-agent-native-review.sh"
}

main "$@"
