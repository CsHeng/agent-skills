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

assert_not_contains() {
  local file_ref="$1" pattern="$2" message="$3"
  [[ "$file_ref" == /* ]] || file_ref="$ROOT_DIR/$file_ref"
  if rg -n -- "$pattern" "$file_ref" >/dev/null; then
    fail "$message"
  fi
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
  assert_contains "$implement_skill" 'lower-plane adapter' "Herdr must remain a lower-plane adapter"
  assert_contains "$implement_skill" 'physical bindings are runtime evidence' "provider bindings must remain runtime evidence"
  assert_contains "$implement_skill" 'runtime-default' "implementation skill should preserve runtime-default binding exception"
  assert_contains "$implement_skill" 'no implementation or test write refs' "implementation skill should require no-write explorer refs"
  assert_contains "$implement_skill" 'external authority' "Herdr must not grant external authority"
  assert_contains "$implement_skill" 'routes truth sync or close' "controller must retain truth-sync and close routing"
  assert_contains "$implement_skill" 'absolute low-cost explorer role' "implementation skill should keep explorer cost absolute"
  assert_contains "$implement_skill" 'explicit explorer task IDs' "implementation skill should preserve search task decomposition"
  assert_contains "$implement_skill" 'main-owned synthesis task' "implementation skill should keep synthesis main-owned"
  assert_contains "$implement_skill" 'low by default' "implementation skill should bind explorers to low effort by default"
  assert_contains "$implement_skill" 'medium as the ceiling' "implementation skill should cap explorer effort at medium"
  assert_contains "$implement_skill" '[Hh]igh/xhigh cannot be labeled explorer' "implementation skill should reject high and xhigh explorers"
  assert_not_contains "$implement_skill" 'relative.*downgrade|strict downgrade|one provider tier below|worker.?baseline' "implementation skill should not compare explorer cost to a worker"
  assert_not_contains "$implement_skill" 'high/xhigh.*(allowed|eligible|may use|can be)' "implementation skill should reject high and xhigh explorer allowance"
  assert_contains "$workflow_contract" 'topology_owner = "plan-change"' "workflow should keep logical topology with planning"
  assert_contains "$workflow_contract" 'runtime_binding_owner = "implement-change"' "workflow should assign runtime binding to controller"
  assert_contains "$workflow_contract" 'delegated_recursion = false' "workflow should prevent recursive worker delegation"
  assert_contains "$workflow_contract" 'role_cost = "absolute"' "workflow should encode absolute explorer cost"
  assert_contains "$workflow_contract" 'default_effort = "low"' "workflow should default explorer effort to low"
  assert_contains "$workflow_contract" 'max_effort = "medium"' "workflow should cap explorer effort at medium"
  assert_contains "$workflow_contract" 'semantic_routing_default_effort = "low"' "workflow should default semantic explorer effort to low"
  assert_contains "$workflow_contract" 'semantic_routing_max_effort = "medium"' "workflow should cap semantic explorer effort at medium"
  assert_contains "$workflow_contract" 'rejected_efforts = \["high", "xhigh"\]' "workflow should reject high and xhigh explorer effort"
  assert_contains "$workflow_contract" 'requires_explicit_search_synthesis_split = true' "workflow should require search and synthesis decomposition"

  HARNESS_SKILL_SURFACE="$SKILL_SURFACE" \
    HARNESS_GENERATED_SKILLS_ROOT="$GENERATED_SKILLS_ROOT" \
    bash "$ROOT_DIR/src/runtime/harness/smoke-test/test-agent-native-review.sh"
}

main "$@"
