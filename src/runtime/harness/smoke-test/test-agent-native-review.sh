#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

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

  case "$SKILL_SURFACE" in
    generated)
      review_change="$GENERATED_SKILLS_ROOT/review-change/SKILL.md"
      implement_change="$GENERATED_SKILLS_ROOT/implement-change/SKILL.md"
      review_implementation="$GENERATED_SKILLS_ROOT/review-implementation/SKILL.md"
      review_components="$GENERATED_SKILLS_ROOT"
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

  rg -n -- 'candidate findings only' "$implement_change" >/dev/null \
    || fail "implementation controller must treat reviewer output as candidate findings only"
  rg -n -- 'must not delegate recursively' "$implement_change" >/dev/null \
    || fail "review and worker actors must not delegate recursively"
  rg -n -- 'main controller alone' "$implement_change" >/dev/null \
    || fail "implementation controller must retain convergence and repair authority"

  assert_absent 'run-review\.sh|review-gate\.sh|review-runner\.sh|same-driver|cross-model|cross-provider|adversarial reviewer|codex exec|claude -p|gemini' \
    "active review surfaces must not invoke or select external reviewers" \
    "$review_change" "$implement_change" "$review_components"

  printf 'test-agent-native-review: PASS\n'
}

main "$@"
