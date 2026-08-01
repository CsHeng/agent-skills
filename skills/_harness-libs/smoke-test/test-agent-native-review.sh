#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"

fail() {
  printf 'test-agent-native-review: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1" pattern="$2" message="$3"
  rg -n -- "$pattern" "$ROOT_DIR/$file_ref" >/dev/null || fail "$message"
}

assert_absent() {
  local pattern="$1" message="$2"
  shift 2
  if rg -n -i -- "$pattern" "$@" >/dev/null; then
    fail "$message"
  fi
}

main() {
  local review_change=""
  local implement_change=""
  local review_implementation=""
  local review_components=""
  local command_root="$ROOT_DIR/commands"

  case "$SKILL_SURFACE" in
    generated)
      review_change="$ROOT_DIR/skills/review-change/SKILL.md"
      implement_change="$ROOT_DIR/skills/implement-change/SKILL.md"
      review_implementation="$ROOT_DIR/skills/review-implementation/SKILL.md"
      review_components="$ROOT_DIR/skills"
      ;;
    source)
      review_change="$ROOT_DIR/src/skills/workflows/review-change/SKILL.md"
      implement_change="$ROOT_DIR/src/skills/workflows/implement-change/SKILL.md"
      review_implementation="$ROOT_DIR/src/skills/review-components/review-implementation/SKILL.md"
      review_components="$ROOT_DIR/src/skills/review-components"
      ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  for causal_class in introduced_by_change regressed_by_change activated_by_change pre_existing unrelated; do
    rg -n -- "$causal_class" "$review_implementation" >/dev/null || fail "missing causal class: $causal_class"
  done

  for disposition in accepted rejected_no_causal_link rejected_pre_existing rejected_out_of_scope rejected_insufficient_evidence deferred_followup needs_plan_change; do
    rg -n -- "$disposition" "$review_change" >/dev/null || fail "missing main-agent disposition: $disposition"
  done

  assert_absent 'run-review\.sh|review-gate\.sh|review-runner\.sh|same-driver|cross-model|cross-provider|adversarial reviewer|codex exec|claude -p|gemini' \
    "active review surfaces must not invoke or select external reviewers" \
    "$review_change" "$implement_change" "$review_components" "$command_root/review-change.md" "$command_root/review-design.md" "$command_root/review-plan.md" "$command_root/review-implementation.md" "$command_root/implement-change.md"

  printf 'test-agent-native-review: PASS\n'
}

main "$@"
