#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

fail() {
  printf 'test-sovereign-skill-surface: %s\n' "$*" >&2
  exit 1
}

main() {
  local skill="" skill_file="" skills_root="" via_herdr_skill=""
  local skill_names=(
    analyze-project
    design-change
    plan-change
    implement-change
    review-change
    sync-truth
    close-change
  )
  local runtime_owners=(
    design-change
    plan-change
    implement-change
    review-change
    sync-truth
    close-change
  )

  case "$SKILL_SURFACE" in
    generated)
      skills_root="$GENERATED_SKILLS_ROOT"
      via_herdr_skill="$skills_root/implement-change-via-herdr/SKILL.md"
      ;;
    source)
      skills_root="$ROOT_DIR/src/skills/workflows"
      via_herdr_skill="$ROOT_DIR/src/skills/tools/implement-change-via-herdr/SKILL.md"
      ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  for skill in "${skill_names[@]}"; do
    skill_file="$skills_root/$skill/SKILL.md"
    [[ -f "$skill_file" ]] || fail "missing sovereign skill: $skill_file"
    rg -n '^---$' "$skill_file" >/dev/null || fail "missing frontmatter in $skill"
    rg -n "^name: ${skill}$" "$skill_file" >/dev/null || fail "skill identity drifted: $skill"
  done

  [[ -f "$via_herdr_skill" ]] || fail "missing explicit Herdr overlay: $via_herdr_skill"
  rg -n 'lower-plane|implement-change controller' "$via_herdr_skill" >/dev/null \
    || fail "Herdr entry must remain a lower-plane controller overlay"
  rg -n 'sole `orchestrator`|main controller alone' "$skills_root/implement-change/SKILL.md" >/dev/null \
    || fail "implement-change must remain the sole controller"

  if [[ "$SKILL_SURFACE" == "generated" ]]; then
    for skill in "${runtime_owners[@]}"; do
      [[ -f "$skills_root/$skill/scripts/harness/contracts.sh" ]] \
        || fail "missing bundled runtime for $skill"
    done
  else
    [[ -f "$ROOT_DIR/src/runtime/harness/contracts.sh" ]] \
      || fail "missing authored harness runtime"
  fi

  if rg -n '\$\{?(PLUGIN_ROOT|CLAUDE_PLUGIN_ROOT)' "$skills_root" >/dev/null; then
    fail "portable skill surface must not depend on provider root variables"
  fi

  rg -n 'delegate recursively' "$skills_root/implement-change/SKILL.md" >/dev/null \
    || fail "implementation skill should preserve worker recursion boundary"
}

main "$@"
