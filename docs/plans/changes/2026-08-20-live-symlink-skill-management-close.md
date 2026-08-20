+++
artifact_kind = "close"
contract_version = 4
approval_status = "approved"
decision = "ready-for-close"
truth_sync_ref = "2026-08-20-live-symlink-skill-management-truth-sync.md"
truth_sync_sha256 = "c4e20d38da091fb44c98cc6430663e6c49a88938c55bf9999bb48c2ee67b95cb"

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts/install-targets.toml", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = ["tests/test_install_target_contracts.py"]
external_impl_file_refs = []
+++
# Close

Close mode is `release`: this gate judges the verified live-symlink management change ready for release. The gate itself performs no version bump, commit, push, publication, installation, or deployment action; the user explicitly authorized the version bump, focused commits, and push as subsequent release actions.

## Decision

All four ledger tasks are converged and the ledger reports `lifecycle_state: task-complete`. The immutable execution result records passed review and verification, and the current tree was revalidated after the final README topology refinement with `bash scripts/check.sh` (281 tests plus contract, generated-surface, index, diagram, Ruff, ty, and Markdown lanes), both plugin validators, and `git diff --check`. The exact truth-sync artifact is approved and evaluates to `ready-for-close`. The user explicitly invoked `close-change`, supplying the human close approval recorded above. The deterministic decision is `ready-for-close` in `release` mode.
