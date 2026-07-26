#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=skills/_harness-libs/contracts.sh
source "$SCRIPT_DIR/contracts.sh"

recovery_route_for_failure() {
  local failure_kind="$1"

  is_valid_failure_kind "$failure_kind" || return 1

  case "$failure_kind" in
    classification-failure|requirement-ambiguity) printf 'clarify\n' ;;
    truth-conflict) printf 'truth-scan\n' ;;
    boundary-mismatch) printf 'design-full\n' ;;
    plan-incompleteness) printf 'plan\n' ;;
    dependency-churn|parallel-conflict|convergence-failure) printf 'dependency-freeze\n' ;;
    review-blocking-failure|verification-failure) printf 'implement-serial\n' ;;
    truth-sync-failure) printf 'truth-sync\n' ;;
    *) return 1 ;;
  esac
}

resolve_recovery_route() {
  local failure_kind="$1"
  local failure_count="$2"

  [[ "$failure_count" =~ ^[1-9][0-9]*$ ]] || return 1

  # Retain the count for observability only. Repetition never proves that the
  # task graph or architecture boundary is wrong and must not widen the phase.
  recovery_route_for_failure "$failure_kind"
}
