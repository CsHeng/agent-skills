+++
artifact_kind = "close"
contract_version = 4
approval_status = "approved"
decision = "ready-for-close"
truth_sync_ref = "2026-08-23-routeros-scripting-guidelines-truth-sync.md"
truth_sync_sha256 = "adf92ea08da39caefb277db4532186b12a6ca3a78b46a9ed9c0458efd0211bf1"

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
+++
# Close

Close mode is `merge`: this gate judges the verified shared RouterOS scripting guideline ready for focused local commits and an ordinary push. The close gate itself performs neither action; the user separately authorized both subsequent phases.

## Decision

Both ledger tasks are converged and the ledger reports `lifecycle_state: task-complete`. The immutable execution result records passed review and verification, including the skill validator, generated parity, the aggregate repository check with 283 passing tests, and `git diff --check`. The exact truth-sync artifact is approved and evaluates to `ready-for-close`. The user explicitly invoked `close-change`; therefore the deterministic decision is `ready-for-close` in `merge` mode.
