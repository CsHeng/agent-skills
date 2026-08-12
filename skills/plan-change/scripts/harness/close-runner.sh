#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=truth-sync-runner.sh
source "$SCRIPT_DIR/truth-sync-runner.sh"

is_valid_close_mode() {
  case "${1:-}" in
    merge|release|cleanup) return 0 ;;
    *) return 1 ;;
  esac
}

close_entry_phase() {
  next_phase_for_entry "close-change"
}

blocked_close_decision() {
  local close_mode="$1"
  local block_reason="$2"
  local next_entry="$3"

  jq -n \
    --arg close_mode "$close_mode" \
    --arg block_reason "$block_reason" \
    --arg next_entry "$next_entry" \
    '{
      close_mode: $close_mode,
      close_allowed: false,
      decision: "blocked",
      block_reason: $block_reason,
      terminal_state: null,
      next_entry: $next_entry
    }'
}

build_close_decision() {
  local close_mode="$1"
  local plan_file="$2"
  local execution_result_file="$3"
  local truth_artifact_file="${4:-}"
  local review_state=""
  local verify_state=""
  local truth_required=""
  local approval_state=""

  is_valid_close_mode "$close_mode" || {
    printf 'invalid close mode: %s\n' "$close_mode" >&2
    return 1
  }

  if ! validate_execution_plan "$plan_file" >/dev/null 2>&1; then
    blocked_close_decision "$close_mode" "approved-plan-invalid-or-truth-scope-missing" "plan-change"
    return
  fi
  if ! validate_execution_evidence_binding "$plan_file" "$execution_result_file" >/dev/null 2>&1; then
    blocked_close_decision "$close_mode" "execution-evidence-mismatch" "implement-change"
    return
  fi

  review_state="$(jq -r '.review_status' "$execution_result_file")"
  verify_state="$(jq -r '.verify_status' "$execution_result_file")"
  truth_required="$(jq -r '.truth_sync_required' "$execution_result_file")"

  if [[ "$truth_required" == "true" && "$(jq '.stable_truth_refs | length' "$execution_result_file")" -eq 0 ]]; then
    blocked_close_decision "$close_mode" "stable-truth-scope-required" "plan-change"
    return
  fi

  if [[ "$review_state" != "pass" ]]; then
    blocked_close_decision "$close_mode" "implementation-review-incomplete" "implement-change"
    return
  fi
  if [[ "$verify_state" != "pass" ]]; then
    blocked_close_decision "$close_mode" "implementation-verification-incomplete" "implement-change"
    return
  fi

  if [[ "$truth_required" == "true" ]]; then
    if [[ -z "$truth_artifact_file" || "$truth_artifact_file" == "none" ]]; then
      blocked_close_decision "$close_mode" "truth-sync-artifact-required" "sync-truth"
      return
    fi
    if ! validate_truth_sync_artifact_against_evidence "$truth_artifact_file" "$plan_file" "$execution_result_file" >/dev/null 2>&1; then
      blocked_close_decision "$close_mode" "truth-sync-evidence-mismatch" "sync-truth"
      return
    fi
    approval_state="$(truth_sync_approval_status "$truth_artifact_file")"
    if [[ "$approval_state" != "approved" ]]; then
      blocked_close_decision "$close_mode" "truth-sync-approval-pending" "sync-truth"
      return
    fi
  fi

  jq -n \
    --arg close_mode "$close_mode" \
    --argjson truth_sync_required "$truth_required" \
    '{
      close_mode: $close_mode,
      review_status: "pass",
      verify_status: "pass",
      truth_sync_required: $truth_sync_required,
      truth_sync_completed: $truth_sync_required,
      close_allowed: true,
      decision: "approved",
      block_reason: null,
      terminal_state: "closed",
      next_entry: null
    }'
}

validate_close_change() {
  local decision_json=""

  decision_json="$(build_close_decision "$@")"
  jq -e '.close_allowed == true and .terminal_state == "closed" and .next_entry == null' <<<"$decision_json" >/dev/null || {
    printf 'close gate blocked\n' >&2
    return 1
  }
}

usage() {
  cat <<'EOF'
Usage:
  close-runner.sh entry-phase
  close-runner.sh validate <merge|release|cleanup> <approved-plan> <execution-result-json> [truth-sync-artifact]
  close-runner.sh decision <merge|release|cleanup> <approved-plan> <execution-result-json> [truth-sync-artifact]
EOF
}

main() {
  local command_name="${1:-}"

  case "$command_name" in
    entry-phase)
      [[ $# -eq 1 ]] || { usage >&2; return 1; }
      close_entry_phase
      ;;
    validate)
      [[ $# -ge 4 && $# -le 5 ]] || { usage >&2; return 1; }
      validate_close_change "$2" "$3" "$4" "${5:-}"
      ;;
    decision)
      [[ $# -ge 4 && $# -le 5 ]] || { usage >&2; return 1; }
      build_close_decision "$2" "$3" "$4" "${5:-}"
      ;;
    *)
      usage >&2
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
