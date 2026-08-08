# Skill Activation And Trigger Ownership Design

## Status

Approved boundary version 1. This artifact records the repository boundary accepted when the user asked to plan the previously recommended sequence: repair measurement first, then make activation semantics authoritative, assign one owner per trigger case, consolidate overlapping skills without changing public IDs, narrow broad descriptions, and regenerate provider metadata plus architecture views.

## Problem

The repository currently has three partially independent views of whether a skill may be selected by a model: `contracts/skills.toml`, generated or copied provider metadata, and provider defaults. The views are not projected or reported from one authority. Most `agents/openai.yaml` files omit an invocation policy, Claude consumes the shared `SKILL.md` description surface without a repo-authored disable projection, and `skill-miner` currently infers model invocation from source frontmatter alone. The resulting report can classify almost the entire inventory as model-invoked even when the repository contract says otherwise.

Observed usage is also an upper bound rather than a reliable invocation count. Session histories contain explicit user mentions, assistant references, skill-file reads, injected inventory text, tool output, and Claude records whose outer `type: user` may wrap a tool result. Treating all such records as equivalent makes low-use and over-trigger conclusions unreliable.

The skill inventory also exposes overlapping descriptions without a machine-readable case owner. Broad selectors and policies can compete with direct workflow owners; review evaluators can appear as independent user intents; architecture, quality, resilience, logging, and security skills contain duplicated or stale boundaries. The generated `skill-planes` view explains macro lifecycle authority but does not show which skill owns a concrete trigger case.

## Goals

- Make current-repository skill usage measurable across Codex, Claude, and Grok histories from all repositories without treating external skill inventories as the subject of the audit.
- Separate declared activation, provider projection, observed explicit invocation, observed skill loading, assistant references, and inferred model activation.
- Establish one authored activation contract, deterministically project Codex `agents/openai.yaml` policy where the shared surface supports enforcement, and record Claude's description-and-routing fallback without claiming an unsupported metadata guarantee.
- Give every public skill a defined activation mode and give every semantic trigger case exactly one primary owner, with optional overlays, positive examples, negative examples, and non-authoritative lexical hints.
- Preserve one sovereign lifecycle owner per request while allowing domain and policy skills to compose as lower-plane support.
- Consolidate `clean-architecture`, `quality-standards`, and `security-logging` into durable owners while retaining their existing public IDs as explicit compatibility entries.
- Rewrite or narrow the descriptions and operating boundaries most likely to over-trigger, especially `tool-decision-tree`, `shell-guidelines`, session skills, review evaluators, resilience, logging, and cross-language policy.
- Preserve all current public IDs during this milestone and use display labels or descriptions, not public renames, for terminology improvement.
- Keep `skill-planes.puml` as the macro authority view and add a generated trigger-ownership view derived from machine contracts.

## Non-Goals

- No public skill ID rename, alias migration, compatibility deadline, or breaking removal in this milestone.
- No audit or redesign of third-party skill repositories; only current-repository skills are classified even when histories from all repositories are scanned.
- No keyword-only router, prompt classifier, embedding service, usage-ranking algorithm, or automatic deletion based on low observed counts.
- No claim that session logs prove every native model decision; inferred activation remains explicitly labeled heuristic evidence.
- No change to sovereign lifecycle phases, human approval gates, review budgets, repair ownership, execution topology, or close judgment.
- No user-global plugin, skill, agent-home, session, memory, or configuration mutation.
- No commit, push, release, plugin reinstall, or public version bump.
- No new implementation language or replacement of the existing Python, TOML, Markdown, Shell, and PlantUML boundaries.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- recommended_next_phase: plan
- truth_sync_required: true
- parallel_candidate: false

## Boundaries

- in_scope:
  - Repair `skill-miner` inventory and session-event classification and add fixture-backed confidence categories.
  - Add authoritative activation metadata to `contracts/skills.toml` and derive compatibility booleans and provider policies from it.
  - Extend the installed `routing.toml` contract with case-centered ownership and validate complete skill coverage plus one owner per case.
  - Preserve native description matching, direct-match bypass, one primary owner, and lower-plane overlay composition.
  - Convert three overlapping skills into explicit compatibility entries after moving unique durable guidance to named owners.
  - Rewrite the selected broad skill descriptions and stale guidance without changing lifecycle authority.
  - Generate the shared root-flat payload, target-specific validation surfaces, skill index, skill planes, trigger-ownership PlantUML, and SVGs from authored contracts.
  - Synchronize stable repository truth only after focused behavior and contract verification.
- out_of_scope:
  - Derive activation policy from frequency alone.
  - Add a second router or a second lifecycle authority.
  - Hand-edit generated `skills/`, PlantUML, SVG, or index outputs.
  - Preserve arbitrary fixed quality thresholds, one mandatory application log format, or stale references to nonexistent language skills.
  - Rename `error-patterns` or `logging-standards` public IDs; clearer display labels may be generated while compatibility is preserved.

## Architecture Decision

- architecture_decision_id: SAO-001-case-owned-skill-activation
- decision_status: selected
- decision_horizon: The current public-ID compatibility epoch, until measured trigger ambiguity or a provider capability change justifies a separately approved identity migration.
- current_demand: Maintainers need reliable current-skill usage evidence and deterministic discovery boundaries without making every visible skill compete as an independent intent.
- constrained_resource: Model discovery context and maintainer attention for keeping contracts, descriptions, provider metadata, generated views, and usage reports aligned.
- hard_requirements:
  - `src/skills/`, `contracts/skills.toml`, and the installed routing contract remain authored truth.
  - Generated surfaces are projections, never independent policy owners.
  - Exactly one primary owner exists for every semantic trigger case.
  - Lifecycle transitions remain owned only by the sovereign workflow kernel.
  - Public IDs remain unchanged in this milestone.
  - Raw session text and private paths are not committed as measurement artifacts.

### Selected Model

Each `[skills.<id>]` entry gains one authoritative `activation_mode` from `native`, `conditional`, `controller`, `explicit`, or `baseline` and one `default_role` from `primary`, `overlay`, `evaluator`, or `helper`. A skill may be a direct case owner and also appear as an overlay in another case; the case registry, rather than the default role alone, decides response ownership for a concrete request.

- `native`: native description matching may select the skill as a direct case owner.
- `conditional`: native matching may compose the skill only when the case predicate activates its domain, language, tooling, or policy boundary.
- `controller`: the skill is selected by a named workflow or routing edge and does not compete for an independent native user intent.
- `explicit`: the skill requires a user or thin host to name the public skill; it is not selected from a broad semantic match.
- `baseline`: the skill is composed by the shared response contract and never competes for primary intent ownership.

Provider behavior is capability-aware derived output, not a second policy source. A contract-level activation-mode projection table records that `native`, `conditional`, and `baseline` derive Codex `policy.allow_implicit_invocation: true`, while `controller` and `explicit` derive `false`; controller edges continue to name and load their evaluator explicitly. Repository generators and validators interpret that table through `scripts/skill_activation.py`. The independently installable `skill-miner` reads the supplied contract table directly when auditing this repository and falls back to observed provider metadata and defaults for bundles without that contract; it must not import a repository-only sibling module. Compatibility fields such as `implicit_invocation` may remain in `skills.index.json` only as generated derivations; they must not remain a second per-skill authored truth in `contracts/skills.toml`.

The tracked root-flat payload is shared by the retained Claude and Codex plugins. The current local Codex plugin validator rejects `disable-model-invocation: true` in `SKILL.md`, so this milestone must not inject that Claude-only disable flag into the shared frontmatter or pretend that Claude has the same enforceable boolean projection. Claude receives the narrowed descriptions, case registry, controller-only evaluator descriptions, optional-router boundary, and host-wrapper hints; `skill-miner` reports its effective default visibility separately from the desired contract. Splitting provider install roots is a future design decision, not a hidden implementation detail.

### Case Ownership Contract

`src/skills/session/use-coding-skills/references/routing.toml` remains the installed discovery authority and gains semantic trigger cases. Every case has a stable ID, exactly one `owner`, positive cases, negative cases, and zero or more overlays. Optional lexical hints illustrate user language but never replace semantic positive and negative boundaries.

Validation enforces:

- every `native` skill owns at least one case;
- every `conditional` skill owns a narrowly predicated case or appears as a case overlay;
- every `controller` skill is reachable from a workflow, phase, review-evaluator, or declared controller edge;
- every `explicit` skill has an explicit-entry case or a compatibility successor;
- the one `baseline` matches the composition rendering baseline;
- a compatibility helper has `superseded_by`, owns no native case, and remains explicitly addressable;
- every public skill is covered exactly through one or more declared roles without creating a second lifecycle owner;
- case owners, overlays, successors, and controller targets resolve to current public IDs.

### Initial Activation Assignment

The first migration uses architecture intent, not raw frequency, as the authority. Corrected usage data is evidence for description quality and future retirement decisions.

- native primary workflows: `analyze-project`, `design-change`, `plan-change`, `implement-change`, `review-change`.
- controller workflows: `sync-truth`, `close-change`.
- native session router: `use-coding-skills`, limited to routing questions, ambiguous multi-stage requests, and session-boundary work.
- baseline session overlay: `output-styles`.
- native domain owners: `organize-docs`, `api-contract-strategy`, `architecture-patterns`, `error-patterns`, `infrastructure-triage`, `testing-strategy`, `docker-multiarch-build`, `web-fetch`, `logging-standards`, `security-guardrails`, `sops-age-guardrails`, `smart-commit`.
- conditional overlays or narrowly predicated owners: `executable-oracle-architecture-selector`, `language-decision-tree`, `tool-decision-tree`, `development-standards`, `go-guidelines`, `lua-guidelines`, `powershell-guidelines`, `python-guidelines`, `shell-guidelines`.
- controller evaluators: `review-design`, `review-plan`, `review-implementation`.
- explicit tools: `skill-miner`, `codex-session-recovery`, `git-worktrees`, `smart-squash`.
- explicit compatibility helpers: `clean-architecture`, `quality-standards`, `security-logging`.

### Consolidation Ownership

- `architecture-patterns` owns architecture selection plus clean dependency and layer boundaries. `clean-architecture` becomes an explicit compatibility entry that points to the new architecture reference.
- `development-standards` owns cross-language maintainability and repository-specific quality-gate policy; `testing-strategy` and language overlays own their executable checks. `quality-standards` becomes an explicit compatibility entry and arbitrary universal thresholds are removed.
- `logging-standards` owns application, observability, security, and audit logging profiles while `security-guardrails` owns validation and exploit-prevention controls. `security-logging` becomes an explicit compatibility entry.
- `error-patterns` keeps its public ID but is rewritten around resilience, failure classification, cleanup, health evidence, and recovery-policy boundaries; its generated display label may become `Resilience and Recovery`.
- `logging-standards` keeps its public ID but is rewritten around goal-driven structured logging rather than one fixed timestamp or line format.

### Rejected Options

- status_quo: Keep booleans, copied provider defaults, and description-only matching. Rejected because the same skill has contradictory declared and effective exposure.
- keyword_router: Assign skills from one global trigger-word list. Rejected because words such as review, architecture, test, shell, and standards are context-dependent and would reproduce competition in a less transparent form.
- frequency_retirement: Disable or remove every low-count skill. Rejected because low counts may reflect broken measurement, missing provider projection, narrow but important safety policy, or controller-only ownership.
- immediate_public_rename: Rename resilience, logging, and compatibility skills now. Rejected because public IDs are installed contract surface and clearer display labels plus compatibility entries solve the current discovery problem without a breaking migration.
- planes_only: Add more categories to `skill-planes`. Rejected because planes explain authority level, not which skill owns a concrete request case.

### Reversible Increments And Upgrade Triggers

- reversible_increments:
  - Repair measurement without changing invocation policy.
  - Add activation semantics and projection while retaining all public IDs.
  - Add case ownership before moving overlapping guidance.
  - Convert overlaps into explicit compatibility entries only after successor content and reference checks pass.
  - Narrow remaining broad descriptions, then regenerate and synchronize truth.
- executable_oracle: Table-driven session fixtures, contract validation, generated metadata conformance, complete trigger-case coverage, compatibility-successor checks, generated diagram freshness, provider-native plugin validation, aggregate repository checks, and bounded review.
- recovery_boundary: Fix forward inside declared source, contracts, generators, tests, generated outputs, and stable docs. Preserve public IDs and stop before compatibility conversion if successor content or provider projection cannot be proven.
- upgrade_triggers:
  - Propose a public rename only after corrected multi-agent measurements show persistent ambiguity that display labels, activation modes, and compatibility entries cannot resolve, with a separately approved migration and compatibility window.
  - Revisit a classifier only if case ownership plus provider metadata still produces measurable, repeated cross-owner misrouting and the classifier has a named owner, deterministic evaluation set, and safe fallback.
  - Revisit provider-specific install roots only if corrected evidence shows that Claude's shared-surface default visibility still causes repeated owner collisions after descriptions and case routing are narrowed.
  - Return to design if Codex policy projection or explicit controller loading cannot preserve the selected controller-only and explicit-only boundaries on the installed surface.

## Acceptance Conditions

- `skill-miner --scope all` can scan all configured agent histories while inventory and reporting remain limited to this repository's public skills.
- Measurement output distinguishes declared activation, projected provider visibility, explicit user invocation, skill load, assistant reference, tool output, and clearly labeled inferred model activation.
- Claude tool-result records wrapped with outer `type: user` do not count as explicit user invocations, and injected skill inventories do not count as usage.
- `contracts/skills.toml` is the only authored activation source; generated Codex `agents/openai.yaml` policy matches its derivation for every public skill, shared `SKILL.md` frontmatter remains provider-compatible, and Claude's non-enforceable default visibility is reported rather than concealed.
- Every current public skill has an activation mode and complete case coverage; every trigger case has exactly one owner and declared positive and negative boundaries.
- `review-implementation` and the other review evaluators no longer compete as native top-level intents.
- `clean-architecture`, `quality-standards`, and `security-logging` retain their IDs as explicit compatibility helpers and point to verified successor owners.
- Broad selectors and policies no longer claim routine search commands, every shell fragment, ordinary direct matches, or independent response schemas outside their case boundary.
- Existing public IDs, provider plugin manifests, lifecycle routes, approval gates, and controller repair semantics remain unchanged.
- `skill-planes` remains the macro plane view, and a generated trigger-ownership PlantUML plus SVG shows activation modes and case ownership without becoming a second contract.
- Required generators, focused tests, sovereign harness smoke tests, provider-native validators, `bash scripts/check.sh`, and `git diff --check` pass with no unrelated tracked drift.
- Bounded implementation review leaves no accepted current-slice finding unresolved, and stable truth stops at its explicit pending human gate.

## Validation

- Run table-driven `skill-miner` unit tests, including all-repository scope, current-inventory filtering, provider defaults, explicit versus inferred activation, Claude wrapped tool results, and injected metadata.
- Run activation and routing contract unit tests with invalid-mode, Codex projection drift, unsupported shared-frontmatter flags, duplicate-owner, missing-positive, missing-negative, uncovered-skill, invalid-overlay, invalid-successor, controller-reachability, and baseline-ownership fixtures.
- Generate Claude, Codex, and root-flat surfaces in isolated temporary directories; compare Codex policy with `contracts/skills.toml`, prove shared-frontmatter compatibility, and report effective Claude visibility separately.
- Regenerate `skills.index.json`, tracked root-flat skills, PlantUML, and SVG outputs from authored source.
- Run the repository aggregate check, sovereign harness surface and routing smoke tests, provider-native plugin validators, and Markdown whitespace validation.
- Perform one bounded implementation review plus one focused verification review when accepted findings require repair.

## Recovery

- Default to fix-forward inside the declared touch set.
- Do not roll back or delete public skills as a response to a failing fixture, stale generated output, or low measured count.
- Preserve the pre-implementation Git state and compare every final changed path with the approved surface.
- If provider capability evidence invalidates the selected activation model, stop with `needs-design-decision` before changing public exposure.
- If unique compatibility-skill behavior has no safe successor owner, stop with `needs-plan-change` before converting that skill to an explicit helper.

## Implementation Surface

- impl_file_refs:
  - AGENTS.md
  - README.md
  - contracts/skills.toml
  - docs/README.md
  - docs/architecture
  - docs/plans/changes/2026-08-07-skill-activation-and-trigger-ownership-truth-sync.md
  - scripts/check-contracts.py
  - scripts/check-install-surface.py
  - scripts/flatten-skills.py
  - scripts/generate-skills-index.py
  - scripts/generate-workflow-diagrams.py
  - scripts/skill_activation.py
  - skills
  - skills.index.json
  - src/skills/disciplines/api-contract-strategy
  - src/skills/disciplines/architecture-patterns
  - src/skills/disciplines/clean-architecture
  - src/skills/disciplines/error-patterns
  - src/skills/disciplines/executable-oracle-architecture-selector
  - src/skills/disciplines/infrastructure-triage
  - src/skills/disciplines/language-decision-tree
  - src/skills/disciplines/organize-docs
  - src/skills/disciplines/skill-miner
  - src/skills/disciplines/testing-strategy
  - src/skills/disciplines/tool-decision-tree
  - src/skills/git
  - src/skills/policies
  - src/skills/review-components
  - src/skills/session/output-styles
  - src/skills/session/use-coding-skills
  - src/skills/tools
  - src/skills/workflows
- test_file_refs:
  - scripts/check.sh
  - src/runtime/harness/smoke-test
  - src/skills/disciplines/skill-miner/tests
  - tests

## Human Gate

- approval_required: true
- approval_status: approved
- approval_evidence: The user explicitly requested `plan-change` using the previously recommended sequence and scope on 2026-08-07; this artifact records that accepted boundary without authorizing implementation.
- next_entry: plan-change
