#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HARNESS_LIB_ROOT="${HARNESS_TEST_SURFACE:-$ROOT_DIR/skills/_harness-libs}"

# shellcheck source=skills/_harness-libs/artifact-dag.sh
source "$HARNESS_LIB_ROOT/artifact-dag.sh"

fail() {
  printf 'test-artifact-dag: %s\n' "$*" >&2
  exit 1
}

TEST_ARTIFACT_DAG_TMP=""

main() {
  local tmp design plan bad_plan resolved allowed
  tmp="$(mktemp -d)"
  TEST_ARTIFACT_DAG_TMP="$tmp"
  trap 'rm -rf -- "$TEST_ARTIFACT_DAG_TMP"' EXIT
  design="$tmp/design.md"
  plan="$tmp/plan.md"
  bad_plan="$tmp/bad-plan.md"

  cat >"$design" <<'EOF'
# Design

## Implementation Surface

- impl_file_refs:
  - src/app
- test_file_refs:
  - tests/app
EOF

  cat >"$plan" <<'EOF'
# Plan

## Upstream Design

- design_ref: design.md
- design_version: v1

## Implementation Scope

- impl_file_refs:
  - src/app/main.go
- test_file_refs:
  - tests/app/main_test.go

## Task 1: App

- task_id: app-task
- impl_file_refs:
  - src/app/main.go
- test_file_refs:
  - tests/app/main_test.go
EOF

  cat >"$bad_plan" <<'EOF'
# Bad Plan

## Upstream Design

- design_ref: design.md
- design_version: v1

## Implementation Scope

- impl_file_refs:
  - src/other/main.go
- test_file_refs:
  - tests/app/main_test.go
EOF

  harness_bash_version_supported 4 || fail "Bash 4 should be supported"
  harness_bash_version_supported 3 && fail "Bash 3 should be rejected"
  declared_repo_path_ref_is_safe "src/app" || fail "safe path rejected"
  declared_repo_path_ref_is_safe "../outside" && fail "parent traversal accepted"

  resolved="$(resolve_plan_design_ref "$tmp" "$plan")"
  [[ "$(printf '%s\n' "$resolved" | sed -n '1p')" == "$(realpath "$design")" ]] || fail "design path resolution mismatch"
  [[ "$(printf '%s\n' "$resolved" | sed -n '2p')" == "v1" ]] || fail "design version resolution mismatch"

  allowed="$(build_allowed_touch_set "$plan" "$design")"
  printf '%s\n' "$allowed" | rg -x 'src/app/main.go' >/dev/null || fail "implementation ref missing"
  printf '%s\n' "$allowed" | rg -x 'tests/app/main_test.go' >/dev/null || fail "test ref missing"
  build_allowed_touch_set "$bad_plan" "$design" >/dev/null 2>&1 && fail "out-of-design path accepted"

  allowed="$(build_task_allowed_touch_set "$plan" "app-task")"
  printf '%s\n' "$allowed" | rg -x 'src/app/main.go' >/dev/null || fail "task implementation ref missing"
  printf '%s\n' "$allowed" | rg -x 'tests/app/main_test.go' >/dev/null || fail "task test ref missing"
  assert_task_change_boundary "$plan" "app-task" "src/app/main.go" "tests/app/main_test.go" || fail "declared task changes should pass"
  assert_task_change_boundary "$plan" "app-task" "src/other.go" >/dev/null 2>&1 && fail "out-of-task change accepted"

  local -a surfaces=("src/app" "tests/app")
  : "${surfaces[*]}" # Also consumed through path_matches_any_surface's nameref.
  path_matches_any_surface surfaces "src/app/main.go" || fail "directory surface should include child"
  path_matches_any_surface surfaces "src/other/main.go" && fail "unrelated path matched surface"

  printf 'test-artifact-dag: PASS\n'
}

main "$@"
