#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../../.." && pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/src/runtime/harness}"
SKILL_SURFACE="${HARNESS_SKILL_SURFACE:-source}"
GENERATED_SKILLS_ROOT="${HARNESS_GENERATED_SKILLS_ROOT:-$ROOT_DIR/skills}"

# shellcheck source=design-runner.sh
source "$HARNESS_LIB_ROOT/design-runner.sh"

fail() {
  printf 'test-design-runner: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local path="$1"
  local pattern="$2"
  local message="$3"
  rg -n "$pattern" "$path" >/dev/null || fail "$message"
}

main() {
  local tmp_dir design_file design_skill

  case "$SKILL_SURFACE" in
    generated) design_skill="$GENERATED_SKILLS_ROOT/design-change/SKILL.md" ;;
    source) design_skill="$ROOT_DIR/src/skills/workflows/design-change/SKILL.md" ;;
    *) fail "HARNESS_SKILL_SURFACE must be generated or source" ;;
  esac

  [[ "$(default_design_artifact_path "Add Tier Entitlement" "2026-04-06")" == "docs/plans/changes/2026-04-06-add-tier-entitlement-design.md" ]] \
    || fail "default design path drifted"
  [[ "$(design_entry_phase)" == "clarify" ]] || fail "design entry phase should be clarify"

  tmp_dir="$(mktemp -d)"
  design_file="$tmp_dir/design.md"

  cat >"$design_file" <<'EOF'
# Sample Design

## Status

Proposed.

## Problem

Problem text.

## Goals

- Goal

## Non-Goals

- Non-goal

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: medium
- boundary_impact: low
- recommended_next_phase: design-lite

## Boundaries

- in_scope:
  - src/example
- out_of_scope:
  - src/other

## Human Gate

- approval_required: true
- approval_status: pending
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/example
- test_file_refs:
  - tests/example
EOF

  validate_design_artifact "$design_file"

  assert_contains "$design_skill" 'scripts/harness/design-runner\.sh' "design skill should use its bundled runner"
  assert_contains "$design_skill" 'review-change' "design skill should route through top-level review gate"
  assert_contains "$design_skill" 'approval_status:' "design skill should expose the approval status field"
  assert_contains "$design_skill" '^SKILL_ROOT=' "design skill should explicitly bind its installed root"
}

main "$@"
