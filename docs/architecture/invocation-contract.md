# Invocation Contract

`contracts/skills.toml` is the table-keyed source, exposure, activation, and runtime-ownership contract for the 40 public skills. `skills/use-coding-skills/references/routing.toml` owns installed semantic trigger cases, phase routes, evaluators, support routes, and composition.

Every skill declares one `activation_mode` and one `default_role`. The contract-level activation-mode projection derives Codex invocation metadata; individual skills do not author invocation policy. Runtime and routing references remain inside their canonical skill directories.

The authored runtime is non-discoverable at `src/runtime/harness/`. Generation copies its explicit production manifest into six runtime owners, and each installed lifecycle skill invokes only its own `scripts/harness/cli.py`. `implement-change` defaults to codex-native and keeps `implement-change-via-herdr` as an explicit adapter overlay.

Retired compatibility IDs are absent. Native and conditional owners use the routing contract; explicit skills require explicit cases; `output-styles` is the shared baseline overlay.
