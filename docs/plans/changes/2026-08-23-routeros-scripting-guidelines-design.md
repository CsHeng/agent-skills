+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "medium"
truth_sync_required = true

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
# Design

## RouterOS Scripting Guidelines

## Classification

- `request_kind`: `ordinary feature`.
- `change_class`: `standard`; the lifecycle classifier returned `mode = standard`, `initial_phase = analyze`, and `owner = analyze-project` for a repository-mutating ordinary feature.
- `design_strength`: `design-lite`; this adds a public policy surface inside the existing source/generated skill-distribution architecture without creating a new runtime or lifecycle boundary.
- `truth_impact`: `medium`; authored public skill identity, inventory count, and stable ownership documentation change.
- `boundary_impact`: `medium`; one new conditional overlay is added while lifecycle, activation, repository, consumer, and live-operation ownership remain unchanged.
- `recommended_next_phase`: `plan`, using the user's explicit instruction to produce the plan in the same turn for final review.

Architecture decision economics is not required because the change stays inside the established authored-source, generated-projection, and conditional-policy boundaries.

## Problem

RouterOS v7 scripting guidance currently lives in a broad personal `routeros-scripting` skill and a repository-local `routeros-rsc` skill that mixes language advice with extraction commands and homelab ownership. The generic guidance is not sourced from the current MikroTik developer manual, duplicates project-specific rules, and places syntax, execution context, permissions, convergence, and external I/O in one flat entrypoint. The shared `coding` collection has no conditional RouterOS language-policy overlay that another workflow can compose without inheriting a personal network-operations catchall.

The current `homelab-infra` evidence set contains 45 active or candidate non-archived `.rsc` files and 1,903 lines. Repeated patterns include local variables in 21 files, globals in 9, error handling in 5, external fetches in 4, control flow in 21, menu-object lookup in 22, explicit errors in 12, and logging in 25. These counts justify focused guidance on scopes, execution contexts, error behavior, stable lookup, convergence, permissions, and external I/O; they do not justify promoting homelab hostnames, manifest shapes, live execution commands, or local naming prohibitions into a generic skill.

## Goals

- Add public skill `routeros-scripting-guidelines` as a conditional policy overlay for writing, reviewing, and diagnosing RouterOS v7 script language and event-body behavior.
- Treat the current MikroTik scripting manual as the language authority and use repository `.rsc` patterns only to select which guidance deserves progressive disclosure.
- Keep `SKILL.md` concise and route substantial detail into `references/language-and-values.md`, `references/execution-contexts-and-permissions.md`, and `references/convergence-and-external-io.md`.
- State variable declaration and naming from the official language definition: ordinary unquoted names use letters and digits, other characters require quoting, names are case-sensitive, and built-in properties are reserved. Do not add a separate underscore prohibition or universal naming rule; camelCase may appear as an ordinary example without becoming a hard requirement.
- Keep repository ownership, desired-state manifests, extraction tools, device inventory, live audit, import, install, apply, and runtime diagnosis outside the generic language-policy owner.
- Publish the new authored skill through the repository's source-to-generated contract, root-flat projection, index, UI metadata, diagrams, current inventory counts, and aggregate validation.

## Non-goals

- No RouterOS CLI, REST API, WinBox, network-design, firewall-policy, VLAN, NAT, DHCP, routing, or live-device operations catchall.
- No copied mirror of the complete MikroTik manual, no exhaustive command catalog, and no speculative universal headers or backup/rollback requirements.
- No generic parser, formatter, linter, asset, template, or script until a repeated deterministic transformation proves one is useful.
- No standalone routing-exclusion chapter in `SKILL.md` and no compatibility alias for `routeros-scripting`.
- No personal-repository deletion, homelab repo-local skill retirement, consumer symlink mutation, plugin release, version bump, publication, or live RouterOS mutation in this repository plan.

## Boundaries

The skill is a conditional language-policy overlay, not a lifecycle owner. A primary workflow retains authority over design, implementation, review, repository ownership, live mutations, and acceptance. The frontmatter `description` carries the user-facing positive `Use when` semantics. The repository routing contract receives the minimal matching trigger case required to project that same activation semantics; this is contract metadata, not a standalone routing-exclusion chapter in `SKILL.md`.

The current MikroTik [Scripting manual](https://manual.mikrotik.com/docs/developer-guides/scripting/) and its linked examples and tips are authoritative for syntax, scopes, types, variables, functions, errors, import behavior, and permission semantics. Supporting references summarize decision-relevant rules and link to the official pages rather than copying the manual. Repository examples are evidence that a topic is useful, never evidence that a homelab convention is universal.

The skill distinguishes script repository execution, direct CLI/import execution, and event contexts such as scheduler, Netwatch, PPP, and DHCP because caller permissions and built-in variables differ. It describes `dont-require-permissions` as a security-sensitive behavior to understand, not a default bypass. It treats `:onerror`, bounded `:retry`, `import ... verbose=yes dry-run`, stable object selection, read-before-write convergence, and secret-safe logging as tools whose exact failure policy remains owned by the calling task.

Adding one public ID changes the generated payload from 39 to 40 skills. Current-count guards and current-state documentation must move together with the contract; historical statements that intentionally describe an earlier 39-skill milestone need not be rewritten.

## Decision Discovery

- `milestone_objective`: establish one source-first generic RouterOS v7 scripting guideline with three focused references and generated distribution parity.
- `shared_terms`: `language authority` means the current official MikroTik scripting manual; `repository evidence` means non-archived `.rsc` usage used only for topic selection; `conditional overlay` means a non-lifecycle skill composed by the active primary workflow; `no compatibility` means no old public-ID alias or forwarding skill.
- `future_phase`: independently retire the personal skill and the homelab repo-local skill under their own repository plans, then consider behavioral forward-testing only after the new skill exists.
- `unresolved_decisions`: none.
- `decision_status`: `ready_for_plan` by the user's 2026-08-23 instruction to create design and plan together for final review.

## Implementation Surface

Authored truth is `contracts/skills.toml`, the new case in `src/skills/session/use-coding-skills/references/routing.toml`, and `src/skills/policies/routeros-scripting-guidelines/`. The entrypoint owns purpose, source precedence, the compact working method, and reference routing. The three references respectively own language/scopes/values, execution contexts/permissions, and convergence/error/external-I/O guidance. No `scripts/` or `assets/` directory is created.

Generated truth consists of the root-flat `skills/routeros-scripting-guidelines/` projection, generated UI metadata, `skills.index.json`, and the skill-plane and trigger-ownership diagrams. Current inventory counts and policy examples in AI-facing and human-facing stable documentation are updated without changing lifecycle or activation architecture.

## Validation

- Validate the new source skill with the bundled `skill-creator` quick validator and inspect that every reference is linked from `SKILL.md`.
- Parse `contracts/skills.toml`, verify the new skill is `category = "policy"`, `activation_mode = "conditional"`, `default_role = "overlay"`, and confirm its minimal routing case matches the frontmatter `Use when` boundary.
- Regenerate the skill index, root-flat payload, and workflow diagrams from authored sources.
- Run the focused distribution tests, `bash scripts/check.sh`, and `git diff --check`.
- Review the exact design and plan scopes through `review-change`; a manual content review checks source authority, variable-name wording, progressive disclosure, permissions semantics, and absence of homelab-specific facts.

## Recovery

Use fix-forward inside the declared source, contract, generated, test, and stable-documentation refs. If validation finds an incorrect rule, repair the authored source or contract, regenerate projections, and rerun the narrow and aggregate checks. Do not preserve the old personal skill as an alias, weaken source/generated parity, or add a broad compatibility route to make the new skill pass.
