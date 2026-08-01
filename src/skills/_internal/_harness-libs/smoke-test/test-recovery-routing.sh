#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/skills/_harness-libs}"

# shellcheck source=skills/_harness-libs/recovery-routing.sh
source "$HARNESS_LIB_ROOT/recovery-routing.sh"

fail() {
  printf 'test-recovery-routing: %s\n' "$*" >&2
  exit 1
}

main() {
  [[ "$(recovery_route_for_failure "requirement-ambiguity")" == "clarify" ]] || fail "requirement ambiguity should route to clarify"
  [[ "$(recovery_route_for_failure "truth-conflict")" == "truth-scan" ]] || fail "truth conflict should route to truth-scan"
  [[ "$(recovery_route_for_failure "boundary-mismatch")" == "design-full" ]] || fail "proven boundary mismatch should route to design"
  [[ "$(recovery_route_for_failure "plan-incompleteness")" == "plan" ]] || fail "proven plan incompleteness should route to plan"
  [[ "$(recovery_route_for_failure "parallel-conflict")" == "dependency-freeze" ]] || fail "parallel conflict should route to dependency freeze"
  [[ "$(recovery_route_for_failure "verification-failure")" == "implement-serial" ]] || fail "verification failure should stay in implementation"
  [[ "$(recovery_route_for_failure "truth-sync-failure")" == "truth-sync" ]] || fail "truth-sync failure should stay in truth sync"

  [[ "$(resolve_recovery_route "verification-failure" 1)" == "implement-serial" ]] || fail "first verification failure should stay in implementation"
  [[ "$(resolve_recovery_route "verification-failure" 5)" == "implement-serial" ]] || fail "repeated verification failures must not widen the phase"
  [[ "$(resolve_recovery_route "plan-incompleteness" 5)" == "plan" ]] || fail "failure count must not turn plan evidence into redesign"
  [[ "$(resolve_recovery_route "boundary-mismatch" 5)" == "design-full" ]] || fail "proven boundary evidence should keep its design route"

  if resolve_recovery_route "verification-failure" 0 >/dev/null 2>&1; then
    fail "failure count 0 should be rejected"
  fi
}

main "$@"
