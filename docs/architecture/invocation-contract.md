# Invocation Contract

The authored skill exposure and activation contract is `contracts/skills.toml`. The installed semantic trigger-case registry is `src/skills/session/use-coding-skills/references/routing.toml`.

See `workflow-orchestration.md` for the canonical maintenance view and generated PlantUML views of harness routing, activation and trigger ownership, the implementation invocation DAG, and repair convergence.

## Categories

| Category | Purpose | Lifecycle Owner |
|---|---|---:|
| `workflow` | Top-level lifecycle authority | yes |
| `session` | Optional routing, session boundaries, and response style | no |
| `discipline` | Reusable engineering method | no |
| `policy` | Language, security, quality, and logging rules | no |
| `tool` | Narrow tool adapter or operational helper | no |
| `manual-tool` | Explicit user action only | no |
| `review-component` | Lower-plane review evaluator | no |

## Hard Rules

- Only workflow skills may set `lifecycle_owner = true`.
- Every public skill must declare one `activation_mode` and one `default_role` in `contracts/skills.toml`.
- Manual tools must use `activation_mode = "explicit"`.
- Mutation-capable skills must set either `requires_explicit_user_request = true` or `requires_approved_plan = true`.
- Non-discoverable runtime source must be bundled into each workflow that declares `runtime_bundle`; it is never emitted as a public skill.
- Direct and transitive `semantic_requires` entries must resolve to public skills, and the complete-inventory profile must remain closed.
- A skill with `runtime_contract` must keep that contract inside its source directory so generated install surfaces carry it with the skill.
- The one skill with `routing_contract` must be a non-lifecycle session skill and must keep that contract inside its source directory.
- Runtime invocation graphs must be acyclic, evaluators must not call lifecycle workflows, and an implementation repair graph must declare exactly one lifecycle-owning loop owner.

## Activation Modes And Roles

Activation modes describe the intended discovery boundary independently from provider capability:

| Mode | Intended boundary | Codex projection |
|---|---|---:|
| `native` | Owns a direct semantic request case | implicit allowed |
| `conditional` | Applies only when its predicate matches a primary request | implicit allowed |
| `controller` | Reached through an owning lifecycle or review controller | implicit disabled |
| `explicit` | Reached only through explicit selection or a compatibility handoff | implicit disabled |
| `baseline` | Composes after primary-owner selection | implicit allowed |

Default roles are `primary`, `overlay`, `evaluator`, and `helper`. The role is the normal composition posture; the case registry decides concrete request ownership, so a narrowly predicated conditional skill may own its matching case. A response has one primary owner; overlays contribute policy or evidence; evaluators return candidate evidence to a controller; helpers preserve an explicit compatibility entry and declare `superseded_by`.

`contracts/skills.toml` is the only authored activation authority. Do not restore per-skill `implicit_invocation` fields or hand-author `policy.allow_implicit_invocation` in source `agents/openai.yaml` files.

## Provider Projection

`scripts/skill_activation.py` interprets the contract-level activation-mode table for generators, validators, the index, and effective-provider-state reporting. `scripts/flatten-skills.py` deterministically projects `policy.allow_implicit_invocation` into every generated `agents/openai.yaml`: `true` for `native`, `conditional`, and `baseline`; `false` for `controller` and `explicit`.

The shared `SKILL.md` payload remains provider-neutral and must not use `disable-model-invocation: true`, which is incompatible with the retained Codex surface. Claude has no equivalent generated per-skill enforcement in this shared payload, so its effective state is reported separately as `default-visible`. Controller and explicit boundaries on Claude therefore remain semantic routing and workflow contracts rather than a claimed provider-level visibility switch.

`skills.index.json` exposes each skill's activation mode, default role, successor, derived Codex compatibility field, effective provider state, and trigger-case ownership. It is a generated inspection surface, not authored truth.

## Semantic Trigger Cases

Each `[[trigger_cases]]` entry in the installed routing contract has a stable case ID, exactly one owner, non-empty positive examples, non-empty negative examples, optional overlays, and optional lexical hints. Positive and negative examples define the semantic boundary. Lexical hints are inspection aids only and never become keyword routing logic.

Coverage is mode-aware: native skills own a case; conditional skills own a predicated case or compose as an overlay; controllers remain reachable through phase, review, or controller edges; explicit skills have an explicit case or a compatibility successor; the baseline matches `composition.rendering_baseline`. Lifecycle owners cannot become overlays, and controller evaluators or compatibility helpers cannot own native cases.

The current compatibility helpers are `clean-architecture` -> `architecture-patterns`, `quality-standards` -> `development-standards`, and `security-logging` -> `logging-standards`. Their public IDs remain installable for explicit handoff but do not compete for native matching.

## Usage Measurement Boundary

`skill-miner` can scan configured Codex, Claude, and Grok histories across repositories while restricting inventory to this repository through `--skill-usage-root` and `--skill-usage-contract`. It reports exact user `$skill` requests, assistant references, observed skill loads, and optional tool outputs as separate evidence classes. Installed flat paths resolve through known public IDs, and unresolved or external skill loads are excluded rather than assigned to a repository-wide bucket. A load without a matching explicit request is only `heuristic_inferred`; observed loads remain an upper bound rather than proof of model causality. Raw examples default to disabled and must be explicitly bounded with `--limit`.

## Exposure

Public skill IDs are generated from `contracts/skills.toml` into flat target surfaces. Do not add machine-readable contract metadata to `SKILL.md` frontmatter. Repo-global exposure metadata remains in `contracts/skills.toml`; install-required routing and runtime graph metadata lives in directly linked skill-local `references/` files.

Native description matching is the default discovery mechanism, but it is not a deterministic lifecycle gate. A host that must guarantee controller entry may keep a thin intent-to-skill mapping in its user-level agent bootstrap, for example:

- approved plan/design implementation -> `implement-change`
- implementation/code review -> `review-change`, which uses `review-implementation` plus matching policy overlays as bounded evaluators

The bootstrap must stop at public skill IDs. It must not duplicate workflow edges, repair states, round budgets, or exit rules; those travel with the installed controller under `implement-change/references/`.

## Output Composition

`output-styles` is the shared conversational rendering baseline. For every composed response, select one primary skill from the user's main intent to own the domain conclusion and concern order. Other matched skills contribute semantic overlays such as policy checks, evidence, risks, or stop states; they do not append independent report templates.

Fixed shapes remain valid for durable artifacts, machine-consumed schemas, and explicit user-requested formats. Internal analysis checklists do not automatically become response sections. For example, `analyze-project` evaluates truth roots, terminology, search boundaries, architecture, operations, status, and drift internally, but renders only relevant axes unless the user explicitly requests a full truth audit.

## Generated Architecture Views

`scripts/generate-workflow-diagrams.py` derives the full harness routing sequence from the installed routing contract plus lifecycle and mode contracts, the skill planes from the exposure contract, the activation and trigger-ownership view from the exposure and routing contracts, and the implementation DAG and repair loop from the installed controller contract. The generated files under `docs/architecture/diagrams/` and `docs/architecture/generated/` are review surfaces, not independent contract inputs.
