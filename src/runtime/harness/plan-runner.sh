#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=artifact-dag.sh
source "$SCRIPT_DIR/artifact-dag.sh"
# shellcheck source=phase-engine.sh
source "$SCRIPT_DIR/phase-engine.sh"

default_plan_artifact_path() {
  local design_path="$1"
  local artifact_dir=""
  local base_name=""

  artifact_dir="$(dirname -- "$design_path")"
  base_name="$(basename -- "$design_path")"
  base_name="${base_name%-design.md}"
  base_name="${base_name%.md}"

  case "$artifact_dir" in
    docs/plans|docs/plans/*|*/docs/plans|*/docs/plans/*)
      printf '%s/%s-plan.md\n' "$artifact_dir" "$base_name"
      ;;
    *)
      printf 'docs/plans/changes/%s-plan.md\n' "$base_name"
      ;;
  esac
}

plan_entry_phase() {
  next_phase_for_entry "plan-change"
}

plan_task_metadata_mode() {
  case "${PLAN_RUNNER_TASK_METADATA_MODE:-compat}" in
    compat|strict) printf '%s\n' "${PLAN_RUNNER_TASK_METADATA_MODE:-compat}" ;;
    *)
      printf 'invalid PLAN_RUNNER_TASK_METADATA_MODE: %s\n' "${PLAN_RUNNER_TASK_METADATA_MODE:-}" >&2
      return 1
      ;;
  esac
}

validate_execution_grade_plan_artifact() {
  local plan_file="$1"

  (
    export PLAN_RUNNER_TASK_METADATA_MODE=strict
    validate_plan_artifact "$plan_file"
  )
}

list_plan_task_sections() {
  local plan_file="$1"

  awk '
    /^## Task [0-9]+:/ {
      sub(/^## /, "", $0)
      print $0
    }
  ' "$plan_file"
}

task_section_has_any_metadata() {
  local plan_file="$1"
  local section="$2"
  local key=""

  for key in \
    task_id \
    depends_on \
    scope_slice \
    impl_file_refs \
    external_impl_file_refs \
    test_file_refs \
    verification_scope \
    executor_mode \
    task_review_depth \
    done_when \
    failure_policy \
    parallel_group \
    parallel_policy \
    delegation_policy \
    execution_profile \
    reasoning_profile \
    isolation \
    resource_locks \
    rollback_trigger \
    rollback_target \
    rollback_verification \
    rollback_on_failure
  do
    if [[ -n "$(extract_markdown_scalar "$plan_file" "$section" "$key")" ]]; then
      return 0
    fi

    if [[ -n "$(extract_markdown_list "$plan_file" "$section" "$key" | awk 'NF > 0')" ]]; then
      return 0
    fi
  done

  return 1
}

plan_has_task_metadata() {
  local plan_file="$1"
  local section=""
  local -a task_sections=()

  mapfile -t task_sections < <(list_plan_task_sections "$plan_file")

  for section in "${task_sections[@]}"; do
    if task_section_has_any_metadata "$plan_file" "$section"; then
      return 0
    fi
  done

  return 1
}

plan_requires_readiness_contract() {
  local plan_file="$1"
  local mode=""

  mode="$(plan_task_metadata_mode)"
  [[ "$mode" == "strict" ]] || plan_has_task_metadata "$plan_file"
}

validate_plan_readiness_contract() {
  local plan_file="$1"
  local field=""
  local decision_status=""
  local max_review_batches=""
  local subagent_ready=""

  if ! plan_requires_readiness_contract "$plan_file"; then
    return 0
  fi

  rg -n '^## Work Package Readiness$' "$plan_file" >/dev/null || {
    printf 'plan artifact missing required section: ^## Work Package Readiness$\n' >&2
    return 1
  }

  for field in milestone_objective decision_status oracle_strategy max_review_batches subagent_ready; do
    [[ -n "$(extract_markdown_scalar "$plan_file" "Work Package Readiness" "$field")" ]] || {
      printf 'plan readiness missing required scalar field: %s\n' "$field" >&2
      return 1
    }
  done

  for field in non_goals future_phase acceptance_oracles; do
    [[ -n "$(extract_markdown_list "$plan_file" "Work Package Readiness" "$field" | awk 'NF > 0')" ]] || {
      printf 'plan readiness missing required list field: %s\n' "$field" >&2
      return 1
    }
  done

  decision_status="$(extract_markdown_scalar "$plan_file" "Work Package Readiness" "decision_status")"
  case "$decision_status" in
    ready_for_review|needs_design_decision|split_scope|manual_checkpoint) ;;
    *)
      printf 'plan readiness decision_status must be ready_for_review, needs_design_decision, split_scope, or manual_checkpoint\n' >&2
      return 1
      ;;
  esac

  max_review_batches="$(extract_markdown_scalar "$plan_file" "Work Package Readiness" "max_review_batches")"
  [[ "$max_review_batches" =~ ^[0-9]+$ && "$max_review_batches" -ge 1 && "$max_review_batches" -le 2 ]] || {
    printf 'plan readiness max_review_batches must be an integer between 1 and 2\n' >&2
    return 1
  }

  subagent_ready="$(extract_markdown_scalar "$plan_file" "Work Package Readiness" "subagent_ready")"
  case "$subagent_ready" in
    true|false) ;;
    *)
      printf 'plan readiness subagent_ready must be true or false\n' >&2
      return 1
      ;;
  esac
}

validate_task_scalar_field() {
  local plan_file="$1"
  local section="$2"
  local key="$3"
  local value=""

  value="$(extract_markdown_scalar "$plan_file" "$section" "$key")"
  [[ -n "$value" ]] || {
    printf 'plan task missing required scalar field (%s) in section: %s\n' "$key" "$section" >&2
    return 1
  }
}

validate_task_list_field() {
  local plan_file="$1"
  local section="$2"
  local key="$3"
  local value=""

  value="$(extract_markdown_list "$plan_file" "$section" "$key" | awk 'NF > 0')"
  [[ -n "$value" ]] || {
    printf 'plan task missing required list field (%s) in section: %s\n' "$key" "$section" >&2
    return 1
  }
}

normalize_plan_metadata_values() {
  sed -E 's/^`(.*)`$/\1/'
}

plan_contract_version() {
  local plan_file="$1"
  extract_markdown_scalar "$plan_file" "Implementation Scope" "plan_contract_version" \
    | normalize_plan_metadata_values
}

plan_uses_v2_contract() {
  local plan_file="$1"
  [[ "$(plan_contract_version "$plan_file")" == "2" ]]
}

plan_truth_sync_required() {
  local plan_file="$1"
  local required_value=""

  required_value="$(extract_markdown_scalar "$plan_file" "Implementation Scope" "truth_sync_required" | normalize_plan_metadata_values)"
  case "$required_value" in
    true|false) printf '%s\n' "$required_value" ;;
    "") printf 'false\n' ;;
    *)
      printf 'truth_sync_scope_required: truth_sync_required must be true or false\n' >&2
      return 1
      ;;
  esac
}

is_supported_plan_docs_governance_predicate() {
  case "$1" in
    none|readme-agents-claude-ownership|stable-truth-roots|decision-record-lifecycle|docs-search-boundaries|stage-artifact-placement|canonical-terminology-across-surfaces|markdown-prose-structure) return 0 ;;
    *) return 1 ;;
  esac
}

plan_design_truth_sync_required() {
  local plan_file="$1"
  local repo_root=""
  local design_file=""
  local truth_impact=""
  local -a resolved_design=()

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  mapfile -t resolved_design < <(resolve_plan_design_ref "$repo_root" "$plan_file" 2>/dev/null || true)
  [[ "${#resolved_design[@]}" -ge 1 ]] || {
    printf 'unknown\n'
    return
  }
  design_file="${resolved_design[0]}"
  [[ -f "$design_file" ]] || {
    printf 'unknown\n'
    return
  }
  truth_impact="$(awk '
    match($0, /truth_impact:[[:space:]]*(low|medium|high)/) {
      value = substr($0, RSTART, RLENGTH)
      sub(/^truth_impact:[[:space:]]*/, "", value)
      print value
      exit
    }
  ' "$design_file")"
  case "$truth_impact" in
    medium|high) printf 'true\n' ;;
    low) printf 'false\n' ;;
    *) printf 'unknown\n' ;;
  esac
}

validate_plan_truth_sync_contract() {
  local plan_file="$1"
  local truth_required=""
  local design_truth_required=""
  local truth_ref=""
  local predicate_id=""
  local saw_none=false
  local saw_governance=false
  local -a plan_surfaces=()
  local -a stable_truth_refs=()
  local -a docs_predicates=()

  plan_uses_v2_contract "$plan_file" || return 0
  truth_required="$(plan_truth_sync_required "$plan_file")" || return 1
  design_truth_required="$(plan_design_truth_sync_required "$plan_file")"
  if [[ "$design_truth_required" == "true" && "$truth_required" != "true" ]]; then
    printf 'truth_sync_scope_required: approved design truth impact requires truth_sync_required: true\n' >&2
    return 1
  fi
  [[ "$truth_required" == "true" ]] || return 0

  rg -n '^## Truth Sync Handoff$' "$plan_file" >/dev/null || {
    printf 'truth_sync_scope_required: truth-affecting version-2 plan requires a Truth Sync Handoff\n' >&2
    return 1
  }

  mapfile -t stable_truth_refs < <(extract_markdown_list "$plan_file" "Truth Sync Handoff" "stable_truth_refs" | normalize_plan_metadata_values | awk 'NF > 0')
  [[ "${#stable_truth_refs[@]}" -gt 0 ]] || {
    printf 'truth_sync_scope_required: stable_truth_refs must not be empty\n' >&2
    return 1
  }

  mapfile -t plan_surfaces < <({
    extract_markdown_list "$plan_file" "Implementation Scope" "impl_file_refs"
    extract_markdown_list "$plan_file" "Implementation Scope" "test_file_refs"
  } | normalize_plan_metadata_values | awk 'NF > 0' | sort -u)
  : "${plan_surfaces[*]}"

  for truth_ref in "${stable_truth_refs[@]}"; do
    declared_repo_path_ref_is_safe "$truth_ref" || {
      printf 'truth_sync_scope_required: unsafe stable truth ref: %s\n' "$truth_ref" >&2
      return 1
    }
    case "$truth_ref" in
      docs/plans/*|*/docs/plans/*)
        printf 'truth_sync_scope_required: stable truth ref must not use the stage artifact root: %s\n' "$truth_ref" >&2
        return 1
        ;;
    esac
    path_matches_any_surface plan_surfaces "$truth_ref" || {
      printf 'truth_sync_scope_required: stable truth ref is outside the immutable plan touch set: %s\n' "$truth_ref" >&2
      return 1
    }
  done

  mapfile -t docs_predicates < <(extract_markdown_list "$plan_file" "Truth Sync Handoff" "docs_governance_predicates" | normalize_plan_metadata_values | awk 'NF > 0')
  [[ "${#docs_predicates[@]}" -gt 0 ]] || {
    printf 'truth_sync_scope_required: docs_governance_predicates must declare none or a supported predicate\n' >&2
    return 1
  }

  for predicate_id in "${docs_predicates[@]}"; do
    is_supported_plan_docs_governance_predicate "$predicate_id" || {
      printf 'truth_sync_scope_required: unsupported docs governance predicate: %s\n' "$predicate_id" >&2
      return 1
    }
    if [[ "$predicate_id" == "none" ]]; then
      saw_none=true
    else
      saw_governance=true
    fi
  done
  if [[ "$saw_none" == "true" && "$saw_governance" == "true" ]]; then
    printf 'truth_sync_scope_required: none cannot be combined with docs governance predicates\n' >&2
    return 1
  fi
}

plan_token_is_safe() {
  local token="$1"
  [[ "$token" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]
}

plan_refs_overlap() {
  local left_ref="$1"
  local right_ref="$2"

  [[ -n "$left_ref" && -n "$right_ref" ]] || return 1
  [[ "$left_ref" != "none" && "$right_ref" != "none" ]] || return 1
  [[ "$left_ref" == "$right_ref" || "$left_ref" == "$right_ref"/* || "$right_ref" == "$left_ref"/* ]]
}

list_plan_parallel_batch_ids() {
  local plan_file="$1"

  awk '
    /^## Parallel Batches$/ {
      in_batches = 1
      next
    }
    in_batches && /^##[[:space:]]+/ {
      exit
    }
    in_batches && /^-[[:space:]]*batch_id:[[:space:]]*/ {
      value = $0
      sub(/^-[[:space:]]*batch_id:[[:space:]]*/, "", value)
      gsub(/^`|`$/, "", value)
      print value
    }
  ' "$plan_file"
}

extract_parallel_batch_scalar() {
  local plan_file="$1"
  local wanted_batch_id="$2"
  local key="$3"

  awk -v wanted_batch_id="$wanted_batch_id" -v key="$key" '
    /^## Parallel Batches$/ {
      in_batches = 1
      next
    }
    in_batches && /^##[[:space:]]+/ {
      exit
    }
    in_batches && /^-[[:space:]]*batch_id:[[:space:]]*/ {
      current_batch_id = $0
      sub(/^-[[:space:]]*batch_id:[[:space:]]*/, "", current_batch_id)
      gsub(/^`|`$/, "", current_batch_id)
      next
    }
    in_batches && current_batch_id == wanted_batch_id &&
      $0 ~ "^-[[:space:]]*" key ":[[:space:]]*" {
      value = $0
      sub(/^[^:]+:[[:space:]]*/, "", value)
      gsub(/^`|`$/, "", value)
      print value
      exit
    }
  ' "$plan_file"
}

extract_parallel_batch_list() {
  local plan_file="$1"
  local wanted_batch_id="$2"
  local key="$3"

  awk -v wanted_batch_id="$wanted_batch_id" -v key="$key" '
    /^## Parallel Batches$/ {
      in_batches = 1
      next
    }
    in_batches && /^##[[:space:]]+/ {
      exit
    }
    in_batches && /^-[[:space:]]*batch_id:[[:space:]]*/ {
      current_batch_id = $0
      sub(/^-[[:space:]]*batch_id:[[:space:]]*/, "", current_batch_id)
      gsub(/^`|`$/, "", current_batch_id)
      in_key = 0
      next
    }
    in_batches && current_batch_id == wanted_batch_id &&
      $0 ~ "^-[[:space:]]*" key ":[[:space:]]*$" {
      in_key = 1
      next
    }
    in_batches && in_key && /^-[[:space:]]*[A-Za-z0-9_-]+:[[:space:]]*/ {
      in_key = 0
    }
    in_batches && in_key && /^[[:space:]]+-[[:space:]]+/ {
      value = $0
      sub(/^[[:space:]]+-[[:space:]]+/, "", value)
      gsub(/^`|`$/, "", value)
      print value
    }
  ' "$plan_file"
}

parallel_batch_max_parallelism() {
  local plan_file="$1"
  local batch_id="$2"

  extract_parallel_batch_scalar "$plan_file" "$batch_id" "max_parallelism"
}

validate_v2_plan_header() {
  local plan_file="$1"
  local contract_version=""
  local parallel_approved=""
  local execution_continuity=""
  local default_model_policy=""
  local allowed_model_policy=""
  local batch_id=""
  local saw_default_model_policy=0

  contract_version="$(plan_contract_version "$plan_file")"
  if [[ -z "$contract_version" ]]; then
    return 0
  fi

  is_valid_plan_contract_version "$contract_version" || {
    printf 'plan contract version is unsupported: %s\n' "$contract_version" >&2
    return 1
  }

  parallel_approved="$(extract_markdown_scalar "$plan_file" "Implementation Scope" "parallel_execution_approved" | normalize_plan_metadata_values)"
  case "$parallel_approved" in
    true|false) ;;
    *)
      printf 'version-2 plan parallel_execution_approved must be true or false\n' >&2
      return 1
      ;;
  esac

  execution_continuity="$(extract_markdown_scalar "$plan_file" "Work Package Readiness" "execution_continuity" | normalize_plan_metadata_values)"
  case "$execution_continuity" in
    continuous_after_plan_approval|pre_confirmation_required|not_ready) ;;
    *)
      printf 'version-2 plan execution_continuity must be continuous_after_plan_approval, pre_confirmation_required, or not_ready\n' >&2
      return 1
      ;;
  esac

  rg -n '^## Runtime Binding$' "$plan_file" >/dev/null || {
    printf 'version-2 plan missing required section: ^## Runtime Binding$\n' >&2
    return 1
  }

  default_model_policy="$(extract_markdown_scalar "$plan_file" "Runtime Binding" "default_model_policy" | normalize_plan_metadata_values)"
  is_valid_model_policy "$default_model_policy" || {
    printf 'version-2 plan has invalid default_model_policy: %s\n' "$default_model_policy" >&2
    return 1
  }

  while IFS= read -r allowed_model_policy; do
    [[ -n "$allowed_model_policy" ]] || continue
    allowed_model_policy="$(printf '%s\n' "$allowed_model_policy" | normalize_plan_metadata_values)"
    is_valid_model_policy "$allowed_model_policy" || {
      printf 'version-2 plan has invalid allowed_model_policies entry: %s\n' "$allowed_model_policy" >&2
      return 1
    }
    if [[ "$allowed_model_policy" == "$default_model_policy" ]]; then
      saw_default_model_policy=1
    fi
  done < <(extract_markdown_list "$plan_file" "Runtime Binding" "allowed_model_policies")

  [[ "$saw_default_model_policy" -eq 1 ]] || {
    printf 'version-2 plan allowed_model_policies must include default_model_policy: %s\n' "$default_model_policy" >&2
    return 1
  }

  [[ -n "$(extract_markdown_scalar "$plan_file" "Runtime Binding" "effective_concurrency")" ]] || {
    printf 'version-2 plan Runtime Binding missing required scalar field: effective_concurrency\n' >&2
    return 1
  }

  if [[ "$parallel_approved" == "true" ]]; then
    rg -n '^## Parallel Batches$' "$plan_file" >/dev/null || {
      printf 'version-2 parallel plan missing required section: ^## Parallel Batches$\n' >&2
      return 1
    }
    batch_id="$(list_plan_parallel_batch_ids "$plan_file" | head -n 1)"
    [[ -n "$batch_id" ]] || {
      printf 'version-2 parallel plan must declare at least one batch_id\n' >&2
      return 1
    }
  fi
}

validate_external_touch_contract() {
  local plan_file="$1"
  local external_touch_policy=""
  local design_link=""
  local design_file=""
  local section=""
  local task_id=""
  local task_external_refs=""
  local executor_mode=""
  local delegation_policy=""
  local parallel_policy=""
  local parallel_group=""
  local isolation_mode=""
  local resource_locks=""
  local plan_external_refs=""
  local -a task_sections=()

  plan_external_refs="$(
    extract_markdown_list "$plan_file" "Implementation Scope" "external_impl_file_refs" \
      | normalize_plan_metadata_values \
      | awk 'NF > 0 && $0 != "none"' \
      | sort -u
  )"
  external_touch_policy="$(
    extract_markdown_scalar "$plan_file" "Implementation Scope" "external_touch_policy" \
      | normalize_plan_metadata_values
  )"

  if [[ -z "$plan_external_refs" ]]; then
    [[ -z "$external_touch_policy" ]] || {
      printf 'external_touch_policy requires nonempty external_impl_file_refs\n' >&2
      return 1
    }
    return 0
  fi

  plan_uses_v2_contract "$plan_file" || {
    printf 'external_impl_file_refs require plan_contract_version 2\n' >&2
    return 1
  }
  [[ "$external_touch_policy" == "exact-existing-files-v1" ]] || {
    printf 'external_impl_file_refs require external_touch_policy: exact-existing-files-v1\n' >&2
    return 1
  }

  design_link="$(resolve_plan_design_ref "$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)" "$plan_file")" || return 1
  design_file="$(printf '%s\n' "$design_link" | sed -n '1p')"
  assert_plan_refs_within_design "$plan_file" "$design_file" || return 1

  mapfile -t task_sections < <(list_plan_task_sections "$plan_file")
  for section in "${task_sections[@]}"; do
    task_external_refs="$(
      extract_markdown_list "$plan_file" "$section" "external_impl_file_refs" \
        | normalize_plan_metadata_values \
        | awk 'NF > 0 && $0 != "none"' \
        | sort -u
    )"
    [[ -n "$task_external_refs" ]] || continue

    task_id="$(extract_markdown_scalar "$plan_file" "$section" "task_id" | normalize_plan_metadata_values)"
    build_task_allowed_external_touch_set "$plan_file" "$task_id" >/dev/null || return 1
    executor_mode="$(extract_markdown_scalar "$plan_file" "$section" "executor_mode" | normalize_plan_metadata_values)"
    delegation_policy="$(extract_markdown_scalar "$plan_file" "$section" "delegation_policy" | normalize_plan_metadata_values)"
    parallel_policy="$(extract_markdown_scalar "$plan_file" "$section" "parallel_policy" | normalize_plan_metadata_values)"
    parallel_group="$(extract_markdown_scalar "$plan_file" "$section" "parallel_group" | normalize_plan_metadata_values)"
    isolation_mode="$(extract_markdown_scalar "$plan_file" "$section" "isolation" | normalize_plan_metadata_values)"
    resource_locks="$(
      extract_markdown_list "$plan_file" "$section" "resource_locks" \
        | normalize_plan_metadata_values \
        | awk 'NF > 0 && $0 != "none"' \
        | sort -u
    )"

    [[ "$executor_mode" == "main" ]] || {
      printf 'external touch task must use executor_mode main: %s\n' "$task_id" >&2
      return 1
    }
    [[ "$delegation_policy" == "forbidden" ]] || {
      printf 'external touch task must forbid delegation: %s\n' "$task_id" >&2
      return 1
    }
    [[ "$parallel_policy" == "forbidden" && "$parallel_group" == "none" ]] || {
      printf 'external touch task must forbid parallel execution: %s\n' "$task_id" >&2
      return 1
    }
    [[ "$isolation_mode" == "controller-checkout" ]] || {
      printf 'external touch task must use controller-checkout isolation: %s\n' "$task_id" >&2
      return 1
    }
    [[ -n "$resource_locks" ]] || {
      printf 'external touch task requires a named resource lock: %s\n' "$task_id" >&2
      return 1
    }
  done
}

validate_v2_task_contracts() {
  local plan_file="$1"
  local parallel_approved=""
  local section=""
  local task_id=""
  local dependency_id=""
  local parallel_group=""
  local parallel_policy=""
  local delegation_policy=""
  local execution_profile=""
  local reasoning_profile=""
  local isolation_mode=""
  local executor_mode=""
  local resource_lock=""
  local task_write_refs=""
  local batch_id=""
  local batch_task_id=""
  local batch_task_key=""
  local batch_max_parallelism=""
  local batch_parallel_policy=""
  local batch_delegation_policy=""
  local batch_isolation_mode=""
  local convergence_task_id=""
  local convergence_member_id=""
  local left_task_id=""
  local right_task_id=""
  local left_ref=""
  local right_ref=""
  local left_lock=""
  local right_lock=""
  local current_node=""
  local ready_flag=""
  local progress_flag=""
  local group_name=""
  local group_task_count=0
  local unresolved_count=0
  local queue_index=0
  local left_index=0
  local right_index=0
  local batch_task_count=0
  local convergence_found=false
  local -a task_sections=()
  local -a task_ids=()
  local -a dependency_values=()
  local -a queue_nodes=()
  local -a group_names=()
  local -a batch_ids=()
  local -A section_by_task=()
  local -A dependencies_by_task=()
  local -A group_by_task=()
  local -A policy_by_task=()
  local -A delegation_by_task=()
  local -A isolation_by_task=()
  local -A writes_by_task=()
  local -A locks_by_task=()
  local -A group_counts=()
  local -A group_policy=()
  local -A seen_batch_ids=()
  local -A seen_batch_tasks=()
  local -A resolved_tasks=()
  local -A visited_nodes=()

  plan_uses_v2_contract "$plan_file" || return 0
  parallel_approved="$(extract_markdown_scalar "$plan_file" "Implementation Scope" "parallel_execution_approved" | normalize_plan_metadata_values)"
  mapfile -t task_sections < <(list_plan_task_sections "$plan_file")

  for section in "${task_sections[@]}"; do
    for task_id in parallel_group parallel_policy delegation_policy execution_profile reasoning_profile isolation; do
      validate_task_scalar_field "$plan_file" "$section" "$task_id" || return 1
    done
    validate_task_list_field "$plan_file" "$section" "resource_locks" || return 1

    task_id="$(extract_markdown_scalar "$plan_file" "$section" "task_id" | normalize_plan_metadata_values)"
    plan_token_is_safe "$task_id" || {
      printf 'version-2 plan task_id must be a portable token in section: %s\n' "$section" >&2
      return 1
    }
    case "$task_id" in
      none|root)
        printf 'version-2 plan task_id is reserved: %s\n' "$task_id" >&2
        return 1
        ;;
    esac
    [[ -z "${section_by_task[$task_id]+present}" ]] || {
      printf 'version-2 plan task_id must be unique: %s\n' "$task_id" >&2
      return 1
    }

    parallel_group="$(extract_markdown_scalar "$plan_file" "$section" "parallel_group" | normalize_plan_metadata_values)"
    parallel_policy="$(extract_markdown_scalar "$plan_file" "$section" "parallel_policy" | normalize_plan_metadata_values)"
    delegation_policy="$(extract_markdown_scalar "$plan_file" "$section" "delegation_policy" | normalize_plan_metadata_values)"
    execution_profile="$(extract_markdown_scalar "$plan_file" "$section" "execution_profile" | normalize_plan_metadata_values)"
    reasoning_profile="$(extract_markdown_scalar "$plan_file" "$section" "reasoning_profile" | normalize_plan_metadata_values)"
    isolation_mode="$(extract_markdown_scalar "$plan_file" "$section" "isolation" | normalize_plan_metadata_values)"
    executor_mode="$(extract_markdown_scalar "$plan_file" "$section" "executor_mode" | normalize_plan_metadata_values)"
    task_write_refs="$({
      extract_markdown_list "$plan_file" "$section" "impl_file_refs"
      extract_markdown_list "$plan_file" "$section" "test_file_refs"
    } | normalize_plan_metadata_values | awk 'NF > 0 && $0 != "none"' | sort -u)"

    plan_token_is_safe "$parallel_group" || {
      printf 'version-2 plan parallel_group must be a portable token in section: %s\n' "$section" >&2
      return 1
    }
    is_valid_parallel_policy "$parallel_policy" || {
      printf 'version-2 plan has invalid parallel_policy in section %s: %s\n' "$section" "$parallel_policy" >&2
      return 1
    }
    is_valid_delegation_policy "$delegation_policy" || {
      printf 'version-2 plan has invalid delegation_policy in section %s: %s\n' "$section" "$delegation_policy" >&2
      return 1
    }
    is_valid_execution_profile "$execution_profile" || {
      printf 'version-2 plan has invalid execution_profile in section %s: %s\n' "$section" "$execution_profile" >&2
      return 1
    }
    is_valid_reasoning_profile "$reasoning_profile" || {
      printf 'version-2 plan has invalid reasoning_profile in section %s: %s\n' "$section" "$reasoning_profile" >&2
      return 1
    }
    is_valid_isolation_mode "$isolation_mode" || {
      printf 'version-2 plan has invalid isolation in section %s: %s\n' "$section" "$isolation_mode" >&2
      return 1
    }
    is_valid_actor_kind "$executor_mode" || {
      printf 'version-2 plan executor_mode must be main or subagent in section %s: %s\n' "$section" "$executor_mode" >&2
      return 1
    }

    case "$parallel_policy" in
      forbidden)
        [[ "$parallel_group" == "none" ]] || {
          printf 'version-2 forbidden task must use parallel_group none: %s\n' "$task_id" >&2
          return 1
        }
        ;;
      allowed|required)
        [[ "$parallel_group" != "none" ]] || {
          printf 'version-2 parallel task must declare a named parallel_group: %s\n' "$task_id" >&2
          return 1
        }
        if [[ -n "$task_write_refs" && "$isolation_mode" != "isolated-worktree" ]]; then
          printf 'version-2 parallel write task must use isolated-worktree: %s\n' "$task_id" >&2
          return 1
        fi
        if [[ -z "$task_write_refs" && "$isolation_mode" != "isolated-worktree" && "$isolation_mode" != "shared-read-only" ]]; then
          printf 'version-2 parallel read-only task must use shared-read-only or isolated-worktree: %s\n' "$task_id" >&2
          return 1
        fi
        ;;
    esac

    if [[ "$isolation_mode" == "shared-read-only" && -n "$task_write_refs" ]]; then
      printf 'version-2 shared-read-only task cannot declare write refs: %s\n' "$task_id" >&2
      return 1
    fi
    if [[ "$executor_mode" == "subagent" && -n "$task_write_refs" && "$isolation_mode" != "isolated-worktree" ]]; then
      printf 'version-2 delegated write task must use isolated-worktree: %s\n' "$task_id" >&2
      return 1
    fi
    if [[ "$executor_mode" == "subagent" && -z "$task_write_refs" && "$isolation_mode" == "controller-checkout" ]]; then
      printf 'version-2 delegated read-only task must use shared-read-only or isolated-worktree: %s\n' "$task_id" >&2
      return 1
    fi

    if [[ "$delegation_policy" == "forbidden" && "$executor_mode" != "main" ]]; then
      printf 'version-2 delegation-forbidden task must use executor_mode main: %s\n' "$task_id" >&2
      return 1
    fi
    if [[ "$delegation_policy" == "preferred" && "$executor_mode" != "subagent" ]]; then
      printf 'version-2 delegation-preferred task must use executor_mode subagent: %s\n' "$task_id" >&2
      return 1
    fi

    while IFS= read -r resource_lock; do
      [[ -n "$resource_lock" ]] || continue
      resource_lock="$(printf '%s\n' "$resource_lock" | normalize_plan_metadata_values)"
      if [[ "$resource_lock" != "none" ]] && ! plan_token_is_safe "$resource_lock"; then
        printf 'version-2 plan resource lock must be a portable token in task %s: %s\n' "$task_id" "$resource_lock" >&2
        return 1
      fi
    done < <(extract_markdown_list "$plan_file" "$section" "resource_locks")

    task_ids+=("$task_id")
    section_by_task["$task_id"]="$section"
    dependencies_by_task["$task_id"]="$(extract_markdown_list "$plan_file" "$section" "depends_on" | normalize_plan_metadata_values | awk 'NF > 0')"
    group_by_task["$task_id"]="$parallel_group"
    policy_by_task["$task_id"]="$parallel_policy"
    delegation_by_task["$task_id"]="$delegation_policy"
    isolation_by_task["$task_id"]="$isolation_mode"
    writes_by_task["$task_id"]="$task_write_refs"
    locks_by_task["$task_id"]="$(extract_markdown_list "$plan_file" "$section" "resource_locks" | normalize_plan_metadata_values | awk 'NF > 0' | sort -u)"
  done

  for task_id in "${task_ids[@]}"; do
    mapfile -t dependency_values < <(printf '%s\n' "${dependencies_by_task[$task_id]}" | awk 'NF > 0')
    if [[ "${#dependency_values[@]}" -gt 1 ]]; then
      for dependency_id in "${dependency_values[@]}"; do
        case "$dependency_id" in
          none|root)
            printf 'version-2 task cannot mix %s with task dependencies: %s\n' "$dependency_id" "$task_id" >&2
            return 1
            ;;
        esac
      done
    fi
    for dependency_id in "${dependency_values[@]}"; do
      case "$dependency_id" in
        none|root) continue ;;
      esac
      [[ "$dependency_id" != "$task_id" ]] || {
        printf 'version-2 task cannot depend on itself: %s\n' "$task_id" >&2
        return 1
      }
      [[ -n "${section_by_task[$dependency_id]+present}" ]] || {
        printf 'version-2 task dependency is unknown (%s -> %s)\n' "$task_id" "$dependency_id" >&2
        return 1
      }
    done
  done

  unresolved_count="${#task_ids[@]}"
  while [[ "$unresolved_count" -gt 0 ]]; do
    progress_flag=false
    for task_id in "${task_ids[@]}"; do
      [[ -z "${resolved_tasks[$task_id]+present}" ]] || continue
      ready_flag=true
      while IFS= read -r dependency_id; do
        [[ -n "$dependency_id" ]] || continue
        case "$dependency_id" in
          none|root) continue ;;
        esac
        if [[ -z "${resolved_tasks[$dependency_id]+present}" ]]; then
          ready_flag=false
          break
        fi
      done <<<"${dependencies_by_task[$task_id]}"
      if [[ "$ready_flag" == "true" ]]; then
        resolved_tasks["$task_id"]=1
        unresolved_count=$((unresolved_count - 1))
        progress_flag=true
      fi
    done
    if [[ "$progress_flag" != "true" ]]; then
      printf 'version-2 task dependency graph contains a cycle\n' >&2
      return 1
    fi
  done

  for task_id in "${task_ids[@]}"; do
    group_name="${group_by_task[$task_id]}"
    [[ "$group_name" != "none" ]] || continue
    group_counts["$group_name"]=$(( ${group_counts[$group_name]:-0} + 1 ))
    if [[ -z "${group_policy[$group_name]+present}" ]]; then
      group_policy["$group_name"]="${policy_by_task[$task_id]}"
      group_names+=("$group_name")
    elif [[ "${group_policy[$group_name]}" != "${policy_by_task[$task_id]}" ]]; then
      printf 'version-2 parallel group must use one parallel_policy: %s\n' "$group_name" >&2
      return 1
    fi
  done

  if [[ "${#group_names[@]}" -gt 0 && "$parallel_approved" != "true" ]]; then
    printf 'version-2 named parallel groups require parallel_execution_approved: true\n' >&2
    return 1
  fi
  if [[ "${#group_names[@]}" -eq 0 && "$parallel_approved" == "true" ]]; then
    printf 'version-2 parallel_execution_approved is true but no named parallel group exists\n' >&2
    return 1
  fi
  for group_name in "${group_names[@]}"; do
    group_task_count="${group_counts[$group_name]}"
    [[ "$group_task_count" -ge 2 ]] || {
      printf 'version-2 parallel group must contain at least two tasks: %s\n' "$group_name" >&2
      return 1
    }
  done

  mapfile -t batch_ids < <(list_plan_parallel_batch_ids "$plan_file" | awk 'NF > 0')
  for batch_id in "${batch_ids[@]}"; do
    plan_token_is_safe "$batch_id" || {
      printf 'version-2 batch_id must be a portable token: %s\n' "$batch_id" >&2
      return 1
    }
    [[ -z "${seen_batch_ids[$batch_id]+present}" ]] || {
      printf 'version-2 batch_id must be unique: %s\n' "$batch_id" >&2
      return 1
    }
    seen_batch_ids["$batch_id"]=1
    [[ -n "${group_counts[$batch_id]+present}" ]] || {
      printf 'version-2 batch_id does not match a task parallel_group: %s\n' "$batch_id" >&2
      return 1
    }
  done
  [[ "${#batch_ids[@]}" -eq "${#group_names[@]}" ]] || {
    printf 'version-2 parallel batches must map one-to-one to named task groups\n' >&2
    return 1
  }

  for group_name in "${group_names[@]}"; do
    [[ -n "${seen_batch_ids[$group_name]+present}" ]] || {
      printf 'version-2 task parallel_group is missing a declared batch: %s\n' "$group_name" >&2
      return 1
    }

    batch_max_parallelism="$(parallel_batch_max_parallelism "$plan_file" "$group_name" | normalize_plan_metadata_values)"
    [[ "$batch_max_parallelism" =~ ^[0-9]+$ && "$batch_max_parallelism" -ge 2 ]] || {
      printf 'version-2 batch max_parallelism must be an integer of at least 2: %s\n' "$group_name" >&2
      return 1
    }

    batch_parallel_policy="$(extract_parallel_batch_scalar "$plan_file" "$group_name" "parallel_policy" | normalize_plan_metadata_values)"
    if [[ -n "$batch_parallel_policy" && "$batch_parallel_policy" != "${group_policy[$group_name]}" ]]; then
      printf 'version-2 batch parallel_policy must match its task group: %s\n' "$group_name" >&2
      return 1
    fi
    batch_delegation_policy="$(extract_parallel_batch_scalar "$plan_file" "$group_name" "delegation_policy" | normalize_plan_metadata_values)"
    if [[ -n "$batch_delegation_policy" ]]; then
      is_valid_delegation_policy "$batch_delegation_policy" || {
        printf 'version-2 batch has invalid delegation_policy: %s\n' "$group_name" >&2
        return 1
      }
      for task_id in "${task_ids[@]}"; do
        [[ "${group_by_task[$task_id]}" == "$group_name" ]] || continue
        [[ "${delegation_by_task[$task_id]}" == "$batch_delegation_policy" ]] || {
          printf 'version-2 batch delegation_policy summary must match every group task: %s\n' "$group_name" >&2
          return 1
        }
      done
    fi
    batch_isolation_mode="$(extract_parallel_batch_scalar "$plan_file" "$group_name" "isolation" | normalize_plan_metadata_values)"
    if [[ -n "$batch_isolation_mode" ]]; then
      is_valid_isolation_mode "$batch_isolation_mode" || {
        printf 'version-2 batch has invalid isolation summary: %s\n' "$group_name" >&2
        return 1
      }
      for task_id in "${task_ids[@]}"; do
        [[ "${group_by_task[$task_id]}" == "$group_name" ]] || continue
        [[ "${isolation_by_task[$task_id]}" == "$batch_isolation_mode" ]] || {
          printf 'version-2 batch isolation summary must match every group task: %s\n' "$group_name" >&2
          return 1
        }
      done
    fi

    batch_task_count=0
    while IFS= read -r batch_task_id; do
      [[ -n "$batch_task_id" ]] || continue
      batch_task_id="$(printf '%s\n' "$batch_task_id" | normalize_plan_metadata_values)"
      plan_token_is_safe "$batch_task_id" || {
        printf 'version-2 batch task must be a portable token (%s): %s\n' "$group_name" "$batch_task_id" >&2
        return 1
      }
      [[ -n "${section_by_task[$batch_task_id]+present}" ]] || {
        printf 'version-2 batch contains an unknown task (%s): %s\n' "$group_name" "$batch_task_id" >&2
        return 1
      }
      [[ "${group_by_task[$batch_task_id]}" == "$group_name" ]] || {
        printf 'version-2 batch task does not belong to its named group (%s): %s\n' "$group_name" "$batch_task_id" >&2
        return 1
      }
      batch_task_key="$group_name|$batch_task_id"
      [[ -z "${seen_batch_tasks[$batch_task_key]+present}" ]] || {
        printf 'version-2 batch task must be unique (%s): %s\n' "$group_name" "$batch_task_id" >&2
        return 1
      }
      seen_batch_tasks["$batch_task_key"]=1
      batch_task_count=$((batch_task_count + 1))
    done < <(extract_parallel_batch_list "$plan_file" "$group_name" "tasks")

    [[ "$batch_task_count" -eq "${group_counts[$group_name]}" ]] || {
      printf 'version-2 batch task list must exactly match its named group: %s\n' "$group_name" >&2
      return 1
    }
    for task_id in "${task_ids[@]}"; do
      [[ "${group_by_task[$task_id]}" == "$group_name" ]] || continue
      batch_task_key="$group_name|$task_id"
      [[ -n "${seen_batch_tasks[$batch_task_key]+present}" ]] || {
        printf 'version-2 batch is missing a group task (%s): %s\n' "$group_name" "$task_id" >&2
        return 1
      }
    done

    convergence_task_id="$(extract_parallel_batch_scalar "$plan_file" "$group_name" "convergence_task" | normalize_plan_metadata_values)"
    plan_token_is_safe "$convergence_task_id" || {
      printf 'version-2 batch must declare a portable convergence_task: %s\n' "$group_name" >&2
      return 1
    }
    if [[ "$convergence_task_id" != "controller" ]]; then
      [[ -n "${section_by_task[$convergence_task_id]+present}" ]] || {
        printf 'version-2 batch convergence_task is unknown (%s): %s\n' "$group_name" "$convergence_task_id" >&2
        return 1
      }
      [[ "${group_by_task[$convergence_task_id]}" != "$group_name" ]] || {
        printf 'version-2 batch convergence_task cannot be a batch member (%s): %s\n' "$group_name" "$convergence_task_id" >&2
        return 1
      }

      for convergence_member_id in "${task_ids[@]}"; do
        [[ "${group_by_task[$convergence_member_id]}" == "$group_name" ]] || continue
        queue_nodes=()
        visited_nodes=()
        convergence_found=false
        while IFS= read -r dependency_id; do
          [[ -n "$dependency_id" ]] || continue
          case "$dependency_id" in
            none|root) continue ;;
          esac
          queue_nodes+=("$dependency_id")
        done <<<"${dependencies_by_task[$convergence_task_id]}"
        queue_index=0
        while [[ "$queue_index" -lt "${#queue_nodes[@]}" ]]; do
          current_node="${queue_nodes[$queue_index]}"
          queue_index=$((queue_index + 1))
          [[ -z "${visited_nodes[$current_node]+present}" ]] || continue
          visited_nodes["$current_node"]=1
          if [[ "$current_node" == "$convergence_member_id" ]]; then
            convergence_found=true
            break
          fi
          while IFS= read -r dependency_id; do
            [[ -n "$dependency_id" ]] || continue
            case "$dependency_id" in
              none|root) continue ;;
            esac
            queue_nodes+=("$dependency_id")
          done <<<"${dependencies_by_task[$current_node]}"
        done
        [[ "$convergence_found" == "true" ]] || {
          printf 'version-2 convergence_task must depend on every batch member (%s): %s missing %s\n' "$group_name" "$convergence_task_id" "$convergence_member_id" >&2
          return 1
        }
      done
    fi
  done

  for task_id in "${task_ids[@]}"; do
    group_name="${group_by_task[$task_id]}"
    [[ "$group_name" != "none" ]] || continue
    queue_nodes=()
    visited_nodes=()
    while IFS= read -r dependency_id; do
      [[ -n "$dependency_id" ]] || continue
      case "$dependency_id" in
        none|root) continue ;;
      esac
      queue_nodes+=("$dependency_id")
    done <<<"${dependencies_by_task[$task_id]}"
    queue_index=0
    while [[ "$queue_index" -lt "${#queue_nodes[@]}" ]]; do
      current_node="${queue_nodes[$queue_index]}"
      queue_index=$((queue_index + 1))
      [[ -z "${visited_nodes[$current_node]+present}" ]] || continue
      visited_nodes["$current_node"]=1
      if [[ "${group_by_task[$current_node]}" == "$group_name" ]]; then
        printf 'version-2 parallel group contains a transitive dependency (%s -> %s): %s\n' "$task_id" "$current_node" "$group_name" >&2
        return 1
      fi
      while IFS= read -r dependency_id; do
        [[ -n "$dependency_id" ]] || continue
        case "$dependency_id" in
          none|root) continue ;;
        esac
        queue_nodes+=("$dependency_id")
      done <<<"${dependencies_by_task[$current_node]}"
    done
  done

  for ((left_index = 0; left_index < ${#task_ids[@]}; left_index += 1)); do
    left_task_id="${task_ids[$left_index]}"
    group_name="${group_by_task[$left_task_id]}"
    [[ "$group_name" != "none" ]] || continue
    for ((right_index = left_index + 1; right_index < ${#task_ids[@]}; right_index += 1)); do
      right_task_id="${task_ids[$right_index]}"
      [[ "${group_by_task[$right_task_id]}" == "$group_name" ]] || continue

      while IFS= read -r left_ref; do
        [[ -n "$left_ref" ]] || continue
        while IFS= read -r right_ref; do
          [[ -n "$right_ref" ]] || continue
          if plan_refs_overlap "$left_ref" "$right_ref"; then
            printf 'version-2 parallel tasks have overlapping write refs (%s, %s): %s <> %s\n' "$left_task_id" "$right_task_id" "$left_ref" "$right_ref" >&2
            return 1
          fi
        done <<<"${writes_by_task[$right_task_id]}"
      done <<<"${writes_by_task[$left_task_id]}"

      while IFS= read -r left_lock; do
        [[ -n "$left_lock" && "$left_lock" != "none" ]] || continue
        while IFS= read -r right_lock; do
          [[ -n "$right_lock" && "$right_lock" != "none" ]] || continue
          if [[ "$left_lock" == "$right_lock" ]]; then
            printf 'version-2 parallel tasks have overlapping resource locks (%s, %s): %s\n' "$left_task_id" "$right_task_id" "$left_lock" >&2
            return 1
          fi
        done <<<"${locks_by_task[$right_task_id]}"
      done <<<"${locks_by_task[$left_task_id]}"
    done
  done
}

validate_task_failure_policy() {
  local plan_file="$1"
  local section="$2"
  local mode="$3"
  local failure_policy=""
  local legacy_rollback=""
  local key=""
  local value=""

  failure_policy="$(extract_markdown_scalar "$plan_file" "$section" "failure_policy")"
  # Compatibility-only: execution-grade strict mode requires failure_policy.
  legacy_rollback="$(extract_markdown_scalar "$plan_file" "$section" "rollback_on_failure")"

  if [[ -z "$failure_policy" ]]; then
    if [[ "$mode" == "compat" && -n "$legacy_rollback" ]]; then
      return 0
    fi
    printf 'plan task missing required scalar field (failure_policy) in section: %s\n' "$section" >&2
    return 1
  fi

  is_valid_failure_policy "$failure_policy" || {
    printf 'plan task failure_policy must be fix_forward, stop_and_diagnose, or guarded_rollback in section: %s\n' "$section" >&2
    return 1
  }

  case "$failure_policy" in
    guarded_rollback)
      validate_task_list_field "$plan_file" "$section" "rollback_trigger" || return 1
      validate_task_scalar_field "$plan_file" "$section" "rollback_target" || return 1
      validate_task_list_field "$plan_file" "$section" "rollback_verification" || return 1
      ;;
    fix_forward|stop_and_diagnose)
      for key in rollback_trigger rollback_target rollback_verification; do
        value="$(extract_markdown_scalar "$plan_file" "$section" "$key")"
        if [[ -z "$value" ]]; then
          value="$(extract_markdown_list "$plan_file" "$section" "$key" | awk 'NF > 0')"
        fi
        if [[ -n "$value" ]]; then
          printf 'plan task %s must not declare %s in section: %s\n' "$failure_policy" "$key" "$section" >&2
          return 1
        fi
      done
      ;;
  esac
}

plan_uses_guarded_rollback() {
  local plan_file="$1"
  local section=""

  while IFS= read -r section; do
    [[ -n "$section" ]] || continue
    if [[ "$(extract_markdown_scalar "$plan_file" "$section" "failure_policy")" == "guarded_rollback" ]]; then
      return 0
    fi
  done < <(list_plan_task_sections "$plan_file")

  return 1
}

validate_plan_recovery_contract() {
  local plan_file="$1"
  local mode=""
  local default_failure_policy=""
  local has_recovery=0
  local has_rollback=0

  mode="$(plan_task_metadata_mode)"
  rg -n '^## Recovery$' "$plan_file" >/dev/null && has_recovery=1
  rg -n '^## Rollback$' "$plan_file" >/dev/null && has_rollback=1

  if [[ "$has_recovery" -eq 0 ]]; then
    if [[ "$mode" == "compat" && "$has_rollback" -eq 1 ]]; then
      return 0
    fi
    printf 'plan artifact missing required section: ^## Recovery$\n' >&2
    return 1
  fi

  default_failure_policy="$(extract_markdown_scalar "$plan_file" "Recovery" "default_failure_policy")"
  [[ "$default_failure_policy" == "fix_forward" ]] || {
    printf 'plan recovery default_failure_policy must be fix_forward\n' >&2
    return 1
  }

  if plan_uses_guarded_rollback "$plan_file"; then
    [[ "$has_rollback" -eq 1 ]] || {
      printf 'plan artifact with guarded_rollback tasks must include: ^## Rollback$\n' >&2
      return 1
    }
  elif [[ "$has_rollback" -eq 1 ]]; then
    printf 'plan artifact must not include a Rollback section without a guarded_rollback task\n' >&2
    return 1
  fi
}

validate_plan_task_contracts() {
  local plan_file="$1"
  local mode=""
  local section=""
  local saw_task_metadata=0
  local -a task_sections=()

  mode="$(plan_task_metadata_mode)"
  mapfile -t task_sections < <(list_plan_task_sections "$plan_file")
  [[ "${#task_sections[@]}" -gt 0 ]] || {
    printf 'plan artifact must contain at least one task section\n' >&2
    return 1
  }

  for section in "${task_sections[@]}"; do
    if task_section_has_any_metadata "$plan_file" "$section"; then
      saw_task_metadata=1
      break
    fi
  done

  if [[ "$mode" == "compat" && "$saw_task_metadata" -eq 0 ]]; then
    return 0
  fi

  for section in "${task_sections[@]}"; do
    validate_task_scalar_field "$plan_file" "$section" "task_id" || return 1
    validate_task_list_field "$plan_file" "$section" "depends_on" || return 1
    validate_task_scalar_field "$plan_file" "$section" "scope_slice" || return 1
    validate_task_list_field "$plan_file" "$section" "impl_file_refs" || return 1
    validate_task_list_field "$plan_file" "$section" "test_file_refs" || return 1
    validate_task_list_field "$plan_file" "$section" "verification_scope" || return 1
    validate_task_scalar_field "$plan_file" "$section" "executor_mode" || return 1
    validate_task_scalar_field "$plan_file" "$section" "task_review_depth" || return 1
    validate_task_list_field "$plan_file" "$section" "done_when" || return 1
    validate_task_failure_policy "$plan_file" "$section" "$mode" || return 1
  done
}

validate_plan_artifact() {
  local plan_file="$1"
  local pattern=""

  [[ -f "$plan_file" ]] || {
    printf 'missing plan file: %s\n' "$plan_file" >&2
    return 1
  }

  for pattern in \
    '^# ' \
    '^## Upstream Design$' \
    '^## Implementation Scope$' \
    '^## Review Gate$' \
    '^## Human Gate$' \
    '^## Task [0-9]+:'
  do
    rg -n "$pattern" "$plan_file" >/dev/null || {
      printf 'plan artifact missing required section: %s\n' "$pattern" >&2
      return 1
    }
  done

  for pattern in \
    'design_ref:' \
    'design_version:' \
    'impl_file_refs:' \
    'test_file_refs:' \
    'verification_scope:' \
    'required_entry:' \
    'approval_required:' \
    'approval_status:' \
    'next_entry:'
  do
    rg -n "$pattern" "$plan_file" >/dev/null || {
      printf 'plan artifact missing required field: %s\n' "$pattern" >&2
      return 1
    }
  done

  rg -n 'approval_status:[[:space:]]*(pending|approved)' "$plan_file" >/dev/null || {
    printf 'plan artifact approval_status must be pending or approved\n' >&2
    return 1
  }

  resolve_plan_design_ref "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" "$plan_file" >/dev/null || {
    printf 'plan artifact has invalid upstream design linkage\n' >&2
    return 1
  }

  local design_link=""
  local design_file=""
  design_link="$(resolve_plan_design_ref "$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)" "$plan_file")" || return 1
  design_file="$(printf '%s\n' "$design_link" | sed -n '1p')"
  assert_plan_refs_within_design "$plan_file" "$design_file" || return 1

  validate_v2_plan_header "$plan_file" || return 1
  validate_external_touch_contract "$plan_file" || return 1
  validate_plan_truth_sync_contract "$plan_file" || return 1
  validate_plan_task_contracts "$plan_file" || return 1
  validate_v2_task_contracts "$plan_file" || return 1
  validate_plan_readiness_contract "$plan_file" || return 1
  validate_plan_recovery_contract "$plan_file"
}

plan_approval_status() {
  local plan_file="$1"

  [[ -f "$plan_file" ]] || {
    printf 'missing plan file: %s\n' "$plan_file" >&2
    return 1
  }

  rg -o 'approval_status:[[:space:]]*(pending|approved)' "$plan_file" \
    | head -n 1 \
    | sed -E 's/^approval_status:[[:space:]]*//'
}

usage() {
  cat <<'EOF'
Usage:
  plan-runner.sh default-path <design-path>
  plan-runner.sh entry-phase
  plan-runner.sh validate <plan-file>
  plan-runner.sh approval-status <plan-file>
EOF
}

main() {
  local command="${1:-}"

  case "$command" in
    default-path)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      default_plan_artifact_path "$2"
      ;;
    entry-phase)
      plan_entry_phase
      ;;
    validate)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      validate_plan_artifact "$2"
      ;;
    approval-status)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      plan_approval_status "$2"
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
