#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=close-runner.sh
source "$HARNESS_LIB_ROOT/close-runner.sh"

fail() {
  printf 'test-close-runner: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local path="$1"
  local pattern="$2"
  local message="$3"

  rg -n -- "$pattern" "$path" >/dev/null || fail "$message"
}

assert_json() {
  local json="$1"
  local expr="$2"
  local message="$3"

  if ! jq -e "$expr" <<<"$json" >/dev/null; then
    fail "$message"
  fi
}

main() {
  local close_skill decision_json

  case "$SKILL_SURFACE" in
    generated) close_skill="$GENERATED_SKILLS_ROOT/close-change/SKILL.md" ;;
    source) close_skill="$ROOT_DIR/src/skills/workflows/close-change/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(close_entry_phase)" == "close" ]] || fail "close entry phase should be close"
  is_valid_close_mode "merge" || fail "merge should be valid close mode"
  if is_valid_close_mode "destroy"; then
    fail "destroy should not be a valid close mode"
  fi

  decision_json="$(build_close_decision "merge" "pass" "pass" "true" "false")"
  assert_json "$decision_json" '.decision == "blocked"' "truth-sync pending should block close"
  assert_json "$decision_json" '.close_allowed == false' "truth-sync pending should not allow close"
  assert_json "$decision_json" '.next_entry == "sync-truth"' "truth-sync pending should route back to truth-sync"

  if validate_close_change "merge" "pass" "pass" "true" "false" >/dev/null 2>&1; then
    fail "close validation should fail when truth sync is pending"
  fi

  decision_json="$(build_close_decision "merge" "pass" "pass" "true" "true")"
  assert_json "$decision_json" '.decision == "approved"' "complete truth-sync should approve close decision"
  assert_json "$decision_json" '.close_allowed == true' "complete truth-sync should allow close"
  assert_json "$decision_json" '.next_entry == "close-change"' "complete truth-sync should stay at close"
  validate_close_change "merge" "pass" "pass" "true" "true"

  decision_json="$(build_close_decision "cleanup" "needs-fixes" "pass" "false" "false")"
  assert_json "$decision_json" '.decision == "blocked"' "review fixes should block close"
  assert_json "$decision_json" '.next_entry == "implement-change"' "review fixes should route back to execution"

  assert_contains "$close_skill" 'scripts/harness/close-runner\.sh' "close skill should use its bundled runner"
  assert_contains "$close_skill" 'review-status.*verify-status' "close skill should require review and verify status"
  assert_contains "$close_skill" 'truth-sync-required.*truth-sync-completed' "close skill should check truth sync completion"
}

main "$@"
