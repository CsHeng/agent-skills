#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=execute-runner.sh
source "$SCRIPT_DIR/execute-runner.sh"

truth_sync_slugify_topic() {
  local topic="${1:-}"

  topic="$(printf '%s' "$topic" | tr '[:upper:]' '[:lower:]')"
  topic="$(printf '%s' "$topic" | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g')"
  [[ -n "$topic" ]] || topic="truth-sync"
  printf '%s\n' "$topic"
}

default_truth_sync_artifact_path() {
  local topic="$1"
  local artifact_date="${2:-$(date -u +%F)}"
  local slug=""

  slug="$(truth_sync_slugify_topic "$topic")"
  printf 'docs/plans/changes/%s-%s-truth-sync.md\n' "$artifact_date" "$slug"
}

truth_sync_entry_phase() {
  next_phase_for_entry "sync-truth"
}

truth_sync_approval_status() {
  local artifact_file="$1"

  [[ -f "$artifact_file" ]] || {
    printf 'missing truth-sync artifact: %s\n' "$artifact_file" >&2
    return 1
  }

  rg -o 'approval_status:[[:space:]]*(pending|approved)' "$artifact_file" \
    | head -n 1 \
    | sed -E 's/^approval_status:[[:space:]]*//'
}

truth_sync_artifact_scalar() {
  local artifact_file="$1"
  local section_name="$2"
  local field_name="$3"

  extract_markdown_scalar "$artifact_file" "$section_name" "$field_name" \
    | normalize_plan_metadata_values
}

validate_stable_truth_refs() {
  local artifact_file="$1"
  local truth_ref=""
  local -a stable_truth_refs=()

  mapfile -t stable_truth_refs < <(extract_markdown_list "$artifact_file" "Stable Truth Updates" "stable_truth_refs" | normalize_plan_metadata_values)
  [[ "${#stable_truth_refs[@]}" -gt 0 ]] || {
    printf 'truth-sync artifact requires at least one stable_truth_refs entry\n' >&2
    return 1
  }

  for truth_ref in "${stable_truth_refs[@]}"; do
    [[ -n "$truth_ref" ]] || continue
    declared_repo_path_ref_is_safe "$truth_ref" || {
      printf 'unsafe stable truth ref: %s\n' "$truth_ref" >&2
      return 1
    }
    case "$truth_ref" in
      docs/plans/*|*/docs/plans/*)
        printf 'stable truth ref must not point at stage artifact root: %s\n' "$truth_ref" >&2
        return 1
        ;;
    esac
  done
}

validate_truth_sync_artifact() {
  local artifact_file="$1"
  local required_pattern=""

  [[ -f "$artifact_file" ]] || {
    printf 'missing truth-sync artifact: %s\n' "$artifact_file" >&2
    return 1
  }

  for required_pattern in \
    '^# ' \
    '^## Evidence$' \
    '^## Stable Truth Updates$' \
    '^## Human Gate$'
  do
    rg -n "$required_pattern" "$artifact_file" >/dev/null || {
      printf 'truth-sync artifact missing required section: %s\n' "$required_pattern" >&2
      return 1
    }
  done

  for required_pattern in \
    'approved_design_ref:' \
    'approved_plan_ref:' \
    'review_gate_ref:' \
    'verification_ref:' \
    'truth_sync_required:' \
    'stable_truth_refs:' \
    'stage_artifact_refs:' \
    'summary:' \
    'approval_required:' \
    'approval_status:' \
    'next_entry:'
  do
    rg -n "$required_pattern" "$artifact_file" >/dev/null || {
      printf 'truth-sync artifact missing required field: %s\n' "$required_pattern" >&2
      return 1
    }
  done

  rg -n 'truth_sync_required:[[:space:]]*true' "$artifact_file" >/dev/null || {
    printf 'truth-sync artifact truth_sync_required must be true\n' >&2
    return 1
  }
  rg -n 'approval_required:[[:space:]]*true' "$artifact_file" >/dev/null || {
    printf 'truth-sync artifact approval_required must be true\n' >&2
    return 1
  }
  rg -n 'approval_status:[[:space:]]*(pending|approved)' "$artifact_file" >/dev/null || {
    printf 'truth-sync artifact approval_status must be pending or approved\n' >&2
    return 1
  }
  rg -n 'next_entry:[[:space:]]*close-change' "$artifact_file" >/dev/null || {
    printf 'truth-sync artifact next_entry must be close-change\n' >&2
    return 1
  }

  validate_stable_truth_refs "$artifact_file"
}

validate_external_execution_evidence_binding() {
  local execution_result_file="$1"
  local expected_external_refs_json="$2"
  local expected_plan_digest="$3"
  local expected_design_digest="$4"
  local task_id=""
  local run_id=""
  local task_temp_dir=""
  local -a helper_args=()
  local -a task_external_refs=()

  while IFS= read -r task_id; do
    [[ -n "$task_id" ]] || continue
    task_temp_dir="$(mktemp -d)"
    chmod 700 "$task_temp_dir"
    jq --arg task_id "$task_id" '.task_evidence[] | select(.task_id == $task_id) | .external_touch_baseline' "$execution_result_file" >"$task_temp_dir/baseline.json"
    jq --arg task_id "$task_id" '.task_evidence[] | select(.task_id == $task_id) | (.external_write_intents // [])' "$execution_result_file" >"$task_temp_dir/intents.json"
    run_id="$(jq -r '.run_id // empty' "$task_temp_dir/baseline.json")"
    mapfile -t task_external_refs < <(jq -r --arg task_id "$task_id" '.task_evidence[] | select(.task_id == $task_id) | (.external_impl_file_refs // [])[]' "$execution_result_file" | sort -u)
    helper_args=(
      python3 "$SCRIPT_DIR/external-touch-evidence.py" validate-state
      --baseline-file "$task_temp_dir/baseline.json"
      --intents-file "$task_temp_dir/intents.json"
      --expected-task-id "$task_id"
      --expected-run-id "$run_id"
      --expected-design-sha256 "$expected_design_digest"
      --expected-plan-sha256 "$expected_plan_digest"
      --require-applied
      --require-cleanup
    )
    local external_ref=""
    for external_ref in "${task_external_refs[@]}"; do
      helper_args+=(--expected-ref "$external_ref")
    done
    if ! "${helper_args[@]}" >/dev/null; then
      rm -rf -- "$task_temp_dir"
      printf 'external execution intent evidence is malformed or forked: %s\n' "$task_id" >&2
      return 1
    fi
    rm -rf -- "$task_temp_dir"
  done < <(jq -r '.task_evidence[] | select(((.external_impl_file_refs // []) | length) > 0) | .task_id' "$execution_result_file")

  jq -e \
    --argjson expected_external_refs "$expected_external_refs_json" \
    --arg expected_plan_digest "$expected_plan_digest" \
    --arg expected_design_digest "$expected_design_digest" \
    '
      def sha256: type == "string" and test("^[0-9a-f]{64}$");
      def file_evidence:
        type == "object" and
        (keys | sort) == (["file_type", "gid", "mode", "ref", "sha256", "size", "st_dev", "st_ino", "st_nlink", "uid"] | sort) and
        (.ref | type == "string" and startswith("/")) and
        (.sha256 | sha256) and (.size | type == "number") and
        .file_type == "regular" and (.mode | test("^[0-7]{4}$")) and
        ([.uid, .gid, .st_dev, .st_ino, .st_nlink] | all(type == "number")) and
        .st_nlink == 1;
      def private_candidate:
        type == "object" and
        (keys | sort) == (["gid", "mode", "path", "run_dir", "sha256", "size", "st_dev", "st_ino", "st_nlink", "uid"] | sort) and
        (.path | type == "string" and startswith("/")) and
        (.run_dir | type == "string" and startswith("/")) and
        (.sha256 | sha256) and (.size | type == "number") and
        .mode == "0600" and
        ([.uid, .gid, .st_dev, .st_ino, .st_nlink] | all(type == "number")) and
        .st_nlink == 1;
      def valid_chain($task; $baseline; $ref):
        ($baseline.refs | map(select(.ref == $ref)) | .[0]) as $root |
        ([$task.external_write_intents[] | select(.ref == $ref)] | sort_by(.sequence)) as $chain |
        ($chain | map(.sequence)) == [range(1; ($chain | length) + 1)] and
        all($chain[];
          .schema_version == 1 and .run_id == $baseline.run_id and .task_id == $task.task_id and
          (.intent_id | type == "string" and length > 0) and
          .root_baseline == $root and .state == "applied" and
          (.candidate | private_candidate) and (.after | file_evidence) and
          (.preserved_metadata | keys | sort) == (["file_type", "gid", "mode", "uid"] | sort) and
          .preserved_metadata.file_type == "regular" and
          (.broker_candidate_basename | type == "string") and
          (.broker_candidate_path | type == "string" and startswith("/")) and
          (.replay_state == "applied_now" or .replay_state == "already_applied")
        ) and
        all(range(0; ($chain | length));
          if . == 0 then $chain[.].parent == $root
          else $chain[.].parent == $chain[. - 1].after
          end
        );
      def valid_manifest_ref($task; $baseline; $manifest_ref):
        ($baseline.refs | map(select(.ref == $manifest_ref.ref)) | .[0]) as $root |
        ([$task.external_write_intents[] | select(.ref == $manifest_ref.ref)] | sort_by(.sequence)) as $chain |
        ($manifest_ref | keys | sort) == (["after", "applied_intent_count", "before", "changed", "ref"] | sort) and
        $manifest_ref.before == $root and
        $manifest_ref.applied_intent_count == ($chain | length) and
        $manifest_ref.after == (if ($chain | length) == 0 then $root else $chain[-1].after end) and
        $manifest_ref.changed == ($manifest_ref.after.sha256 != $root.sha256);
      def valid_external_task:
        . as $task |
        ((.external_impl_file_refs // []) | sort | unique) as $refs |
        if ($refs | length) == 0 then
          .external_touch_baseline == null and
          (.external_write_intents // []) == [] and
          .verified_external_changes == null
        else
          (.external_touch_baseline | type == "object") and
          (.external_touch_baseline.schema_version == 1) and
          (.external_touch_baseline.task_id == .task_id) and
          (.external_touch_baseline.plan_sha256 == $expected_plan_digest) and
          (.external_touch_baseline.design_sha256 == $expected_design_digest) and
          (.external_touch_baseline.run_id | type == "string" and length > 0) and
          ((.external_touch_baseline.refs | map(.ref) | sort) == $refs) and
          all(.external_touch_baseline.refs[]; file_evidence) and
          ((.external_write_intents // []) | type == "array") and
          all((.external_write_intents // [])[]; (.ref as $intent_ref | $refs | index($intent_ref)) != null) and
          all($refs[]; valid_chain($task; $task.external_touch_baseline; .)) and
          (.verified_external_changes | type == "object") and
          ((.verified_external_changes | keys | sort) == (["design_sha256", "plan_sha256", "refs", "run_id", "schema_version", "task_id"] | sort)) and
          (.verified_external_changes.schema_version == 1) and
          (.verified_external_changes.run_id == .external_touch_baseline.run_id) and
          (.verified_external_changes.task_id == .task_id) and
          (.verified_external_changes.plan_sha256 == $expected_plan_digest) and
          (.verified_external_changes.design_sha256 == $expected_design_digest) and
          ((.verified_external_changes.refs | map(.ref) | sort) == $refs) and
          all(.verified_external_changes.refs[]; valid_manifest_ref($task; $task.external_touch_baseline; .))
        end;

      ((.allowed_external_touch_refs // []) | sort | unique) == ($expected_external_refs | sort | unique) and
      ([.task_evidence[] | (.external_impl_file_refs // [])[]] | sort | unique) == ($expected_external_refs | sort | unique) and
      ([.task_evidence[] | (.external_write_intents // [])[] | .intent_id] | length) ==
        ([.task_evidence[] | (.external_write_intents // [])[] | .intent_id] | unique | length) and
      all(.task_evidence[]; valid_external_task) and
      (.verified_external_changes == [
        .task_evidence[]
        | select((.external_impl_file_refs // []) | length > 0)
        | {task_id, manifest: .verified_external_changes}
      ]) and
      ([
        [.task_evidence, .verified_external_changes]
        | ..
        | objects
        | keys[]
        | select(. == "content" or . == "raw_content" or . == "preimage")
      ] | length) == 0
    ' "$execution_result_file" >/dev/null || {
      printf 'external execution evidence does not match the approved metadata-only contract\n' >&2
      return 1
    }
}

validate_execution_evidence_binding() {
  local plan_file="$1"
  local execution_result_file="$2"
  local design_file=""
  local expected_plan_ref=""
  local expected_design_ref=""
  local expected_plan_digest=""
  local expected_design_digest=""
  local embedded_ledger_digest=""
  local embedded_drift_json="[]"
  local expected_truth_required=""
  local expected_stable_refs_json="[]"
  local expected_touch_refs_json="[]"
  local expected_external_refs_json="[]"
  local expected_docs_predicates_json="[]"

  validate_execution_plan "$plan_file" >/dev/null || return 1
  jq -e 'type == "object"' "$execution_result_file" >/dev/null 2>&1 || {
    printf 'invalid execution evidence json: %s\n' "$execution_result_file" >&2
    return 1
  }

  design_file="$(resolve_execution_design_file "$plan_file")"
  expected_plan_ref="$(execution_artifact_ref "$plan_file")"
  expected_design_ref="$(execution_artifact_ref "$design_file")"
  expected_plan_digest="$(harness_file_sha256 "$plan_file")"
  expected_design_digest="$(harness_file_sha256 "$design_file")"
  expected_truth_required="$(execution_truth_sync_required "$plan_file")"
  expected_stable_refs_json="$(execution_stable_truth_refs_json "$plan_file")"
  expected_touch_refs_json="$(execution_allowed_touch_set "$plan_file" | jq -R . | jq -s 'sort')"
  expected_external_refs_json="$(execution_allowed_external_touch_set "$plan_file" | jq -R . | jq -s 'map(select(length > 0)) | sort')"
  expected_docs_predicates_json="$(execution_docs_governance_predicates_json "$plan_file")"
  embedded_ledger_digest="$(jq -cS '.task_evidence' "$execution_result_file" | shasum -a 256 | awk '{print $1}')"
  embedded_drift_json="$(execution_plan_ledger_drift_evidence_json "$plan_file" <(jq '.task_evidence' "$execution_result_file"))"
  if [[ "$(jq 'length' <<<"$embedded_drift_json")" -gt 0 ]]; then
    printf 'embedded execution task evidence does not match the approved plan projection\n' >&2
    return 1
  fi
  validate_external_execution_evidence_binding \
    "$execution_result_file" \
    "$expected_external_refs_json" \
    "$expected_plan_digest" \
    "$expected_design_digest" || return 1

  jq -e \
    --arg expected_plan_ref "$expected_plan_ref" \
    --arg expected_design_ref "$expected_design_ref" \
    --arg expected_plan_digest "$expected_plan_digest" \
    --arg expected_design_digest "$expected_design_digest" \
    --arg embedded_ledger_digest "$embedded_ledger_digest" \
    --argjson expected_truth_required "$expected_truth_required" \
    --argjson expected_stable_refs "$expected_stable_refs_json" \
    --argjson expected_touch_refs "$expected_touch_refs_json" \
    --argjson expected_docs_predicates "$expected_docs_predicates_json" \
    '
      .execution_unit == "plan" and
      .approved_plan_ref == $expected_plan_ref and
      .approved_design_ref == $expected_design_ref and
      .plan_sha256 == $expected_plan_digest and
      .design_sha256 == $expected_design_digest and
      .ledger_sha256 == $embedded_ledger_digest and
      (.task_evidence | type == "array") and
      .total_task_count == (.task_evidence | length) and
      .completed_task_count == ([.task_evidence[] | select(.status == "done")] | length) and
      .remaining_task_count == ([.task_evidence[] | select(.status != "done")] | length) and
      (
        if .remaining_task_count == 0 then
          all(.task_evidence[];
            .status == "done" and
            (
              ((.convergence_required // false) == false) or
              (.convergence_verified == true and .oracles_verified == true and .integration_verified == true and .convergence_actor == "controller")
            )
          )
        else true
        end
      ) and
      .review_gate_ref == ("review:" + .plan_sha256 + ":" + .ledger_sha256 + ":" + .review_status) and
      .verification_ref == ("verification:" + .plan_sha256 + ":" + .ledger_sha256 + ":" + .verify_status) and
      .truth_sync_required == $expected_truth_required and
      ((.stable_truth_refs | sort) == ($expected_stable_refs | sort)) and
      ((.allowed_touch_refs | sort) == ($expected_touch_refs | sort)) and
      ((.docs_governance_predicates | sort) == ($expected_docs_predicates | sort)) and
      (
        if .remaining_task_count > 0 then .lifecycle_state == "implementation-pending"
        elif .review_status != "pass" or .verify_status != "pass" then .lifecycle_state == "task-complete"
        elif .truth_sync_required == true and (.stable_truth_refs | length) == 0 then .lifecycle_state == "task-complete"
        elif .truth_sync_required == true then .lifecycle_state == "truth-sync-pending"
        else .lifecycle_state == "ready-for-close"
        end
      )
    ' "$execution_result_file" >/dev/null || {
      printf 'execution evidence does not match the approved plan and immutable result contract\n' >&2
      return 1
    }
}

truth_sync_mutation_authorization() {
  local authority_kind="$1"
  shift || true
  local authorized=false
  local authority_label=""
  local reason=""

  case "$authority_kind" in
    direct)
      [[ $# -eq 1 ]] || return 1
      if [[ "$1" == "true" ]]; then
        authorized=true
        authority_label="direct-explicit-request"
        reason="explicit-user-request"
      elif [[ "$1" == "false" ]]; then
        authority_label="direct-request-missing"
        reason="explicit-user-request-required"
      else
        return 1
      fi
      ;;
    controller)
      [[ $# -eq 2 ]] || return 1
      authority_label="approved-plan-controller"
      if validate_execution_evidence_binding "$1" "$2" >/dev/null 2>&1 \
        && jq -e '.truth_sync_required == true and (.stable_truth_refs | length) > 0 and .review_status == "pass" and .verify_status == "pass" and .remaining_task_count == 0 and .lifecycle_state == "truth-sync-pending" and .next_entry == "sync-truth"' "$2" >/dev/null; then
        authorized=true
        reason="approved-plan-and-immutable-execution-evidence"
      else
        reason="complete-controller-context-required"
      fi
      ;;
    *) return 1 ;;
  esac

  jq -n \
    --arg authority "$authority_label" \
    --arg reason "$reason" \
    --argjson authorized "$authorized" \
    '{authority: $authority, authorized: $authorized, reason: $reason}'
}

truth_sync_docs_governance_decision() {
  local predicate_id="$1"
  shift || true
  local organize_docs_required=false
  local changed_refs_json="[]"
  local matched_predicates_json="[]"

  is_valid_docs_governance_predicate "$predicate_id" || return 1
  changed_refs_json="$(printf '%s\n' "$@" | awk 'NF > 0' | jq -R . | jq -s .)"
  if [[ "$predicate_id" != "none" ]]; then
    organize_docs_required=true
    matched_predicates_json="$(printf '%s\n' "$predicate_id" | jq -R . | jq -s .)"
  fi

  jq -n \
    --argjson organize_docs_required "$organize_docs_required" \
    --argjson matched_predicates "$matched_predicates_json" \
    --argjson changed_refs "$changed_refs_json" \
    '{
      organize_docs_required: $organize_docs_required,
      matched_predicates: $matched_predicates,
      changed_refs: $changed_refs
    }'
}

build_truth_sync_docs_governance_decision() {
  local plan_file="$1"
  shift || true
  local changed_ref=""
  local predicate_id=""
  local organize_docs_required=false
  local changed_refs_json="[]"
  local stable_truth_refs_json="[]"
  local matched_predicates_json="[]"
  local -a stable_truth_surfaces=()
  local -a matched_predicates=()

  validate_plan_truth_sync_contract "$plan_file" || return 1
  mapfile -t stable_truth_surfaces < <(extract_markdown_list "$plan_file" "Truth Sync Handoff" "stable_truth_refs" | normalize_plan_metadata_values | awk 'NF > 0')
  : "${stable_truth_surfaces[*]}"
  for changed_ref in "$@"; do
    declared_repo_path_ref_is_safe "$changed_ref" || return 1
    path_matches_any_surface stable_truth_surfaces "$changed_ref" || {
      printf 'docs composition ref is outside approved stable truth scope: %s\n' "$changed_ref" >&2
      return 1
    }
  done

  while IFS= read -r predicate_id; do
    [[ -n "$predicate_id" ]] || continue
    is_valid_docs_governance_predicate "$predicate_id" || return 1
    if [[ "$predicate_id" != "none" ]]; then
      organize_docs_required=true
      matched_predicates+=("$predicate_id")
    fi
  done < <(extract_markdown_list "$plan_file" "Truth Sync Handoff" "docs_governance_predicates" | normalize_plan_metadata_values)

  changed_refs_json="$(printf '%s\n' "$@" | awk 'NF > 0' | jq -R . | jq -s .)"
  stable_truth_refs_json="$(printf '%s\n' "${stable_truth_surfaces[@]}" | awk 'NF > 0' | jq -R . | jq -s 'sort')"
  matched_predicates_json="$(printf '%s\n' "${matched_predicates[@]:-}" | awk 'NF > 0' | jq -R . | jq -s 'sort')"
  jq -n \
    --argjson organize_docs_required "$organize_docs_required" \
    --argjson matched_predicates "$matched_predicates_json" \
    --argjson stable_truth_refs "$stable_truth_refs_json" \
    --argjson changed_refs "$changed_refs_json" \
    '{
      organize_docs_required: $organize_docs_required,
      matched_predicates: $matched_predicates,
      stable_truth_refs: $stable_truth_refs,
      changed_refs: $changed_refs
    }'
}

validate_truth_sync_artifact_against_evidence() {
  local artifact_file="$1"
  local plan_file="$2"
  local execution_result_file="$3"
  local expected_design_ref=""
  local expected_plan_ref=""
  local expected_review_ref=""
  local expected_verification_ref=""
  local observed_design_ref=""
  local observed_plan_ref=""
  local observed_review_ref=""
  local observed_verification_ref=""

  validate_truth_sync_artifact "$artifact_file" || return 1
  validate_execution_evidence_binding "$plan_file" "$execution_result_file" || return 1
  jq -e '.truth_sync_required == true and .remaining_task_count == 0 and .review_status == "pass" and .verify_status == "pass"' "$execution_result_file" >/dev/null || {
    printf 'truth-sync evidence requires completed passing implementation evidence\n' >&2
    return 1
  }

  expected_design_ref="$(jq -r '.approved_design_ref' "$execution_result_file")"
  expected_plan_ref="$(jq -r '.approved_plan_ref' "$execution_result_file")"
  expected_review_ref="$(jq -r '.review_gate_ref' "$execution_result_file")"
  expected_verification_ref="$(jq -r '.verification_ref' "$execution_result_file")"
  observed_design_ref="$(truth_sync_artifact_scalar "$artifact_file" "Evidence" "approved_design_ref")"
  observed_plan_ref="$(truth_sync_artifact_scalar "$artifact_file" "Evidence" "approved_plan_ref")"
  observed_review_ref="$(truth_sync_artifact_scalar "$artifact_file" "Evidence" "review_gate_ref")"
  observed_verification_ref="$(truth_sync_artifact_scalar "$artifact_file" "Evidence" "verification_ref")"

  exact_scalar_values_match "$expected_design_ref" "$observed_design_ref" || {
    printf 'truth-sync approved_design_ref mismatch\n' >&2
    return 1
  }
  exact_scalar_values_match "$expected_plan_ref" "$observed_plan_ref" || {
    printf 'truth-sync approved_plan_ref mismatch\n' >&2
    return 1
  }
  exact_scalar_values_match "$expected_review_ref" "$observed_review_ref" || {
    printf 'truth-sync review_gate_ref mismatch\n' >&2
    return 1
  }
  exact_scalar_values_match "$expected_verification_ref" "$observed_verification_ref" || {
    printf 'truth-sync verification_ref mismatch\n' >&2
    return 1
  }
  exact_ref_sets_match \
    <(jq -r '.stable_truth_refs[]' "$execution_result_file") \
    <(extract_markdown_list "$artifact_file" "Stable Truth Updates" "stable_truth_refs" | normalize_plan_metadata_values) || {
      printf 'truth-sync stable_truth_refs do not exactly match execution evidence\n' >&2
      return 1
    }

  extract_markdown_list "$artifact_file" "Stable Truth Updates" "stage_artifact_refs" \
    | normalize_plan_metadata_values \
    | rg -x --fixed-strings "$expected_design_ref" >/dev/null || {
      printf 'truth-sync stage_artifact_refs missing approved design\n' >&2
      return 1
    }
  extract_markdown_list "$artifact_file" "Stable Truth Updates" "stage_artifact_refs" \
    | normalize_plan_metadata_values \
    | rg -x --fixed-strings "$expected_plan_ref" >/dev/null || {
      printf 'truth-sync stage_artifact_refs missing approved plan\n' >&2
      return 1
    }
}

build_truth_sync_gate_result() {
  local artifact_file="$1"
  local plan_file="$2"
  local execution_result_file="$3"
  local approval_state=""
  local truth_sync_completed=false
  local gate_json=""
  local review_state=""
  local verify_state=""

  validate_truth_sync_artifact_against_evidence "$artifact_file" "$plan_file" "$execution_result_file"
  approval_state="$(truth_sync_approval_status "$artifact_file")"
  [[ "$approval_state" == "approved" ]] && truth_sync_completed=true
  review_state="$(jq -r '.review_status' "$execution_result_file")"
  verify_state="$(jq -r '.verify_status' "$execution_result_file")"
  gate_json="$(build_evaluation_verdict "$review_state" "$verify_state" "true" "$truth_sync_completed")"

  jq \
    --arg artifact_file "$artifact_file" \
    --arg approval_status "$approval_state" \
    '. + {
      artifact_file: $artifact_file,
      approval_status: $approval_status,
      next_entry: (if .ready_for_close then "close-change" else "sync-truth" end)
    }' <<<"$gate_json"
}

usage() {
  cat <<'EOF'
Usage:
  truth-sync-runner.sh default-path <topic> [date]
  truth-sync-runner.sh entry-phase
  truth-sync-runner.sh validate <truth-sync-artifact>
  truth-sync-runner.sh validate-against <truth-sync-artifact> <approved-plan> <execution-result-json>
  truth-sync-runner.sh approval-status <truth-sync-artifact>
  truth-sync-runner.sh mutation-authorization direct <explicit-user-request:true|false>
  truth-sync-runner.sh mutation-authorization controller <approved-plan> <execution-result-json>
  truth-sync-runner.sh docs-governance-decision <approved-plan> [changed-stable-ref ...]
  truth-sync-runner.sh gate-result <truth-sync-artifact> <approved-plan> <execution-result-json>
EOF
}

main() {
  local command_name="${1:-}"

  case "$command_name" in
    default-path)
      [[ $# -ge 2 ]] || { usage >&2; return 1; }
      default_truth_sync_artifact_path "$2" "${3:-}"
      ;;
    entry-phase)
      truth_sync_entry_phase
      ;;
    validate)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      validate_truth_sync_artifact "$2"
      ;;
    validate-against)
      [[ $# -eq 4 ]] || { usage >&2; return 1; }
      validate_truth_sync_artifact_against_evidence "$2" "$3" "$4"
      ;;
    approval-status)
      [[ $# -eq 2 ]] || { usage >&2; return 1; }
      truth_sync_approval_status "$2"
      ;;
    mutation-authorization)
      [[ $# -ge 3 ]] || { usage >&2; return 1; }
      truth_sync_mutation_authorization "$2" "${@:3}"
      ;;
    docs-governance-decision)
      [[ $# -ge 2 ]] || { usage >&2; return 1; }
      build_truth_sync_docs_governance_decision "$2" "${@:3}"
      ;;
    gate-result)
      [[ $# -eq 4 ]] || { usage >&2; return 1; }
      build_truth_sync_gate_result "$2" "$3" "$4"
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
