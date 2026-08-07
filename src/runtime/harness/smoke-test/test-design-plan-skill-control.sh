#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

fail() {
  printf 'test-design-plan-skill-control: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local file_ref="$1"
  local pattern="$2"
  local message="$3"
  [[ "$file_ref" == /* ]] || file_ref="$ROOT_DIR/$file_ref"
  rg -n "$pattern" "$file_ref" >/dev/null || fail "$message"
}

main() {
  local design_skill plan_skill implement_skill
  case "$SKILL_SURFACE" in
    generated)
      design_skill="$GENERATED_SKILLS_ROOT/design-change/SKILL.md"
      plan_skill="$GENERATED_SKILLS_ROOT/plan-change/SKILL.md"
      implement_skill="$GENERATED_SKILLS_ROOT/implement-change/SKILL.md"
      ;;
    source)
      design_skill="src/skills/workflows/design-change/SKILL.md"
      plan_skill="src/skills/workflows/plan-change/SKILL.md"
      implement_skill="src/skills/workflows/implement-change/SKILL.md"
      ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  assert_contains "$design_skill" 'design-runner\.sh' "design skill should validate artifact before review"
  assert_contains "$design_skill" 'review-change' "design skill should route through top-level review gate"
  assert_contains "$design_skill" 'approval_status:[[:space:]]*pending|approval_status:[[:space:]]*approved' "design skill should carry approval status gate"
  assert_contains "$design_skill" 'plan-change|next_entry: plan-change' "design skill should hand off explicitly"

  assert_contains "$plan_skill" 'plan-runner\.sh' "plan skill should validate artifact before review"
  assert_contains "$plan_skill" 'review-change' "plan skill should route through top-level review gate"
  assert_contains "$plan_skill" 'approval-status.*approved' "plan skill should machine-check approved upstream design"
  assert_contains "$plan_skill" 'approval_status:[[:space:]]*pending|approval_status:[[:space:]]*approved' "plan skill should carry approval status gate"
  assert_contains "$plan_skill" 'implement-change|next_entry: implement-change' "plan skill should hand off explicitly"

  assert_contains "$plan_skill" 'semantic-routing' "plan skill should provide semantic routing advice"
  assert_contains "$plan_skill" 'inherit-main' "plan skill should preserve topology under inherit-main"
  assert_contains "$implement_skill" 'logical topology|task IDs, dependencies' "implementation skill should leave logical topology to planning"
  assert_contains "$implement_skill" 'runtime binding' "implementation skill should own runtime binding"
}

main "$@"
