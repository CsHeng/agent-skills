+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-23-routeros-scripting-guidelines-design.md"
design_sha256 = "f20590e5d6722cf3b1e390208f945d68093467b10d79d24426f24b30f74aaf42"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = [
  "AGENTS.md",
  "README.md",
  "contracts/skills.toml",
  "docs/architecture/install-surface.md",
  "docs/architecture/invocation-contract.md",
  "docs/architecture/workflow-orchestration.md",
  "src/skills/policies/routeros-scripting-guidelines/SKILL.md",
  "src/skills/policies/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "src/skills/policies/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "src/skills/policies/routeros-scripting-guidelines/references/language-and-values.md",
  "src/skills/session/use-coding-skills/references/routing.toml",
]
default_runtime_model_policy = "semantic-routing"
parallel_execution_approved = false

[scope]
impl_file_refs = [
  "AGENTS.md",
  "README.md",
  "contracts/skills.toml",
  "docs/architecture/diagrams/skill-planes.puml",
  "docs/architecture/diagrams/skill-trigger-ownership.puml",
  "docs/architecture/generated/skill-planes.svg",
  "docs/architecture/generated/skill-trigger-ownership.svg",
  "docs/architecture/install-surface.md",
  "docs/architecture/invocation-contract.md",
  "docs/architecture/workflow-orchestration.md",
  "scripts/skill_distribution.py",
  "skills/.source-map.json",
  "skills.index.json",
  "skills/routeros-scripting-guidelines/SKILL.md",
  "skills/routeros-scripting-guidelines/agents/openai.yaml",
  "skills/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "skills/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "skills/routeros-scripting-guidelines/references/language-and-values.md",
  "skills/use-coding-skills/references/routing.toml",
  "src/skills/policies/routeros-scripting-guidelines/SKILL.md",
  "src/skills/policies/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "src/skills/policies/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "src/skills/policies/routeros-scripting-guidelines/references/language-and-values.md",
  "src/skills/session/use-coding-skills/references/routing.toml",
]
test_file_refs = ["tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "RSG-M010"
depends_on = []
verification_commands = [
  'uvx --with pyyaml python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" src/skills/policies/routeros-scripting-guidelines',
  "git diff --check",
]
scope_slice = "Author the conditional RouterOS scripting policy, three focused references, the minimal matching routing contract case, public skill contract, 40-skill inventory guards, and current stable documentation without adding a routing-exclusion section to the skill."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["skill-catalog-contract", "routeros-guideline-source"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = [
  "The authored SKILL.md is concise, identifies the official manual as authority, and links exactly the three planned references according to progressive disclosure.",
  "language-and-values.md follows the official declaration and naming rules without adding an underscore prohibition or mandatory naming style.",
  "Execution contexts, permission inheritance, dont-require-permissions risk, convergence, onerror, bounded retry, import dry-run, stable lookup, external I/O, and secret-safe logging are covered without homelab-specific facts or live mutation authority.",
  "contracts/skills.toml declares a conditional policy overlay, the routing contract case matches the skill's Use when boundary, and current inventory guards and stable docs describe 40 public skills.",
]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [
  "AGENTS.md",
  "README.md",
  "contracts/skills.toml",
  "docs/architecture/install-surface.md",
  "docs/architecture/invocation-contract.md",
  "docs/architecture/workflow-orchestration.md",
  "scripts/skill_distribution.py",
  "src/skills/policies/routeros-scripting-guidelines/SKILL.md",
  "src/skills/policies/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "src/skills/policies/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "src/skills/policies/routeros-scripting-guidelines/references/language-and-values.md",
  "src/skills/session/use-coding-skills/references/routing.toml",
]
test_file_refs = ["tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "RSG-M020"
depends_on = ["RSG-M010"]
verification_commands = [
  "python3 scripts/generate-skills-index.py",
  "python3 scripts/flatten-skills.py --target root-flat",
  "python3 scripts/generate-workflow-diagrams.py",
  "bash scripts/check.sh",
  "git diff --check",
]
scope_slice = "Regenerate the root-flat skill, UI metadata, index, and affected diagrams from authored truth, then verify source-generated equality and the complete repository contract."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["generated-skill-tree", "generated-workflow-diagrams"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = [
  "The generated root-flat skill and references equal the authored source and generated UI metadata allows implicit conditional discovery.",
  "skills.index.json reports 40 canonical skills and the skill-plane and trigger-ownership diagrams include the new conditional overlay and its declared routing case.",
  "The aggregate repository check and diff check pass with no unrelated generated drift.",
]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [
  "docs/architecture/diagrams/skill-planes.puml",
  "docs/architecture/diagrams/skill-trigger-ownership.puml",
  "docs/architecture/generated/skill-planes.svg",
  "docs/architecture/generated/skill-trigger-ownership.svg",
  "skills/.source-map.json",
  "skills.index.json",
  "skills/routeros-scripting-guidelines/SKILL.md",
  "skills/routeros-scripting-guidelines/agents/openai.yaml",
  "skills/routeros-scripting-guidelines/references/convergence-and-external-io.md",
  "skills/routeros-scripting-guidelines/references/execution-contexts-and-permissions.md",
  "skills/routeros-scripting-guidelines/references/language-and-values.md",
  "skills/use-coding-skills/references/routing.toml",
]
test_file_refs = []
external_impl_file_refs = []
+++
# Plan

## Implementation

Implement the shared repository slice in two serial source-generated tasks. `RSG-M010` authors the new public policy and all current inventory/truth changes; `RSG-M020` regenerates the portable projection and runs the complete repository gates. The source and generated tasks are deliberately serial because the second consumes the first and owns shared generated outputs.

The three-repository suite order is `RSG-M010..M020 -> RSP-P010 -> RSR-H010`. The personal and homelab plans may proceed only after `RSG-M020` passes. This creates the replacement before either duplicate owner is deleted while adding no compatibility alias or old-ID forwarding surface.

## Work Package Readiness

- `milestone_objective`: publish one source-first RouterOS v7 scripting policy overlay with focused official-manual-based references and complete generated distribution parity.
- `non_goals`: no live RouterOS operation, repository-specific extraction workflow, personal skill deletion, homelab skill deletion, compatibility alias, parser, formatter, asset, plugin release, version bump, install, publication, or provider-cache mutation.
- `future_phase`: execute the two sibling repository retirement plans, then optionally forward-test the new skill on realistic requests after the repository cutover.
- `decision_status`: `ready_for_review` under the user's explicit 2026-08-23 instruction to produce design and plan together for final review.
- `oracle_strategy`: official-source conformance review, skill quick validation, source-generated equality, structured distribution contracts, generated-diagram freshness, aggregate repository validation, and bounded artifact review.
- `acceptance_oracles`: the task commands, direct inspection of the frontmatter and three references, confirmation that the routing case matches the `Use when` boundary and no underscore prohibition exists, and direct main-agent review of the exact design and plan.
- `execution_continuity`: `continuous_after_plan_approval` for this repository slice.
- `max_review_batches`: `2`, one design/plan boundary review now and one focused implementation review only if execution later changes the approved surface.
- `subagent_ready`: `false`; the task graph contains one authored source slice followed by its coupled generated projection and the current session does not authorize delegation.

No implementation-language decision is required because this plan adds Markdown/TOML policy truth and existing generated artifacts, not a new executable boundary.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C0`; the user selected the three-repository split, official-source basis, variable naming treatment, no standalone routing section, and no-compatibility cutover.
- `runtime_contingencies`: `X1` stops before mutation if any approved market-csheng touch ref gains overlapping user changes or the canonical skill inventory changes after plan approval in a way that invalidates the 40-skill contract.
- `planned_stop_points`: none.
- `task_ordering_rationale`: author and validate source first, regenerate projections second, and require the shared replacement to pass before either sibling retirement plan deletes its old owner.

Expected continuous range after approval: `E1 = RSG-M010..RSG-M020`.

## Recovery

`default_failure_policy: fix_forward`. Repair only the declared authored source, contract, count guard, generated projection, test, diagram, or stable truth ref and rerun the narrow oracle followed by `bash scripts/check.sh`. Do not add an old-ID alias, copy personal guidance, weaken source-generated checks, or introduce rollback hooks.

## Truth Sync Handoff

`truth_sync_required: true`. Stable truth refs are the authored policy and references, `contracts/skills.toml`, and the current inventory/architecture documents declared in frontmatter. Docs-governance predicate: `canonical-terminology`; current skill-count and ownership language must consistently use the new public ID and 40-skill inventory without rewriting historical milestone evidence.

## Review Gate

- `required_entry`: `review-change`
- `review_component`: `review-plan`
- `actor_role`: `main`
- `review_depth`: `boundary`
- `review_status`: `passed`
- `candidate_findings`: none
- `review_evidence`: Direct review is appropriate because this turn may not delegate and the plan is a bounded source-generated policy addition. The plan preserves source ownership, progressive disclosure, official-source authority, the user's variable-name and routing-section corrections, exact generated parity, no-compatibility semantics, repository-local retirement boundaries, fix-forward recovery, and a fully serial dependency graph.
