+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "high"
truth_sync_required = true

[scope]
impl_file_refs = [".pi/settings.json", "AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi", "scripts", "src/skills", "skills"]
test_file_refs = ["integrations/pi/tests", "tests"]
external_impl_file_refs = ["/home/csheng/.pi/agent/settings.json"]
+++
# Design

## Problem

The current Pi experiment changed the implementation language of the lifecycle controller without changing its architecture. A required `/csheng-run <mode> --auto ...` command still creates a separate workflow, selects a fixed phase sequence, injects phase-specific prompts, and treats public Skills as templates executed by that controller. Moving this loop from Skill-local Python and Shell into one TypeScript extension therefore produced a sidecar harness rather than making Pi itself the active host harness.

The installation boundary reinforces the mismatch. The workflow extension is loaded only by this repository's `.pi/settings.json`, so a normal Pi session in another repository receives the globally linked Skills but none of the mechanical state, ledger, gate, continuation, or progress behavior. The user must know an internal command, mode, and authorization marker to exercise the experiment, while ordinary natural-language and `/skill:<name>` use bypass the new mechanics.

If this shape continues, the repository will accumulate phase graphs, schemas, retries, ledgers, scheduling rules, and provider-specific invocation mechanics inside either Skills or a parallel controller. The Skills would become a Markdown-driven headless coding agent and Pi would remain only its model/tool transport. The required boundary is the inverse: portable Skills own engineering semantics and textual composition, while a globally installed Pi extension supplies host-native mechanics through Pi sessions, events, tools, follow-ups, and UI without introducing a second user workflow.

## Goals

- Make natural Pi requests and Pi-native `/skill:<name>` commands the only normal workflow entrypoints; no dedicated run command, mode argument, or auto marker is required.
- Preserve the sovereign semantic kernel: Skills and canonical contracts own request meaning, phase semantics, evidence meaning, review judgment, recovery choice, close judgment, and textual Skill-to-Skill handoffs.
- Make the Pi extension the active mechanical host for invocation state, request authority, task progress, ledger state, tool profiles, attempt budgets, artifact validation invocation, scheduling, branch replay, continuation, completion signaling, UI status, and telemetry.
- Translate a Skill-declared semantic handoff such as `design-change -> review-change(role=review-design)` into a validated Pi follow-up without making the Skill depend on Pi-specific commands or tool names.
- Install the Pi package globally for this validation machine so the same harness mechanics apply in arbitrary repositories while retaining exactly one global discovery path for each of the 40 portable Skills.
- Decompose the extension into behavior-bearing modules with explicit ownership while keeping one package and one in-process Pi runtime for the current single-agent scope.
- Keep generated Skills free of Skill-local lifecycle runtimes and reduce workflow Skill prose that encodes host state machines, detailed ledger mechanics, retries, scheduling, or provider behavior.
- Prove both sides of portability: extension-on execution gains native automation, while extension-off execution retains coherent Skill semantics and textual composition.

## Non-Goals

- No general cross-host orchestrator, cross-provider executor router, subagent scheduler, parallel writer runtime, Herdr control loop, or distributed durable service.
- No regulated, emergency, external-mutation, deployment, release, destructive-history, commit, push, publish, or secret-management workflow in the Pi lane.
- No independent lexical request classifier in the extension; native Skill description matching, explicit Skill invocation, and the portable routing contract remain semantic owners.
- No fork or patch of Pi core and no replacement of Pi's native agent loop, session store, tool execution, retry, compaction, or completion semantics.
- No deletion of the central Python artifact/ledger compatibility runtime in this milestone. It may validate durable artifact boundaries, but it cannot drive the Pi session loop or be invoked by a Skill as its controller.
- No attempt to remove all structure from Skills. A Skill may retain concise semantic evidence and durable artifact requirements; exact runtime schemas, transition enforcement, progress storage, and scheduling machinery do not belong in its operational prose.
- No public package release or compatibility promise for other machines before the local global-package path and disposable-repository probes pass.

## Decision Discovery

- `milestone_objective`: replace the command-driven Pi sidecar controller with one globally installed modular Pi host adapter that transparently supplies harness mechanics to the existing Skill entry and composition model.
- `non_goals`: cross-host orchestration, parallel or delegated actors, regulated/external work, provider routing, publication, and deletion of the compatibility validator runtime.
- `unresolved_decisions`: none block planning; exact internal TypeScript type names and file splits may be adjusted during implementation only when the ownership and executable boundaries below remain unchanged.
- `shared_terms`: `semantic kernel` means portable Skills plus canonical semantic contracts; `host mechanics` means Pi-owned state, ledger, gates, scheduling, replay, and signaling; `semantic handoff` means one Skill requesting another public Skill and optional evaluator role; `host adapter` means the extension translating that request into Pi-native runtime behavior.
- `decision_status`: `approved_for_implementation`; the user explicitly approved this design together with its linked plan and invoked `implement-change` on 2026-08-27.

## Boundaries

### D1: Semantic Authority And Dependency Direction

Architecture decision `PI-HARNESS-003` supersedes the command-runner portion of `PI-HARNESS-002`. Public Skills remain the inward semantic policy. They define what a design, plan, implementation, review, truth sync, or close means and may state textual composition such as invoking `review-change` with the `review-design` evaluator role. The Pi adapter depends on the generated projection of those contracts and validates requested handoffs; Skills do not import Pi APIs, name Pi extension tools, or contain a fallback implementation of Pi's loop.

The extension must not maintain phase goals, engineering checklists, evaluator criteria, or a handwritten route table. Its transition runtime accepts a current invocation and a Skill-declared handoff, verifies that the owner, role, terminal intent, evidence class, and authority are permitted by the canonical projection, persists the mechanical result, and either schedules the next Pi turn or settles. Deleting the extension must remove automation, not the semantic intelligibility of the Skills.

### D2: Native Invocation Without A Parallel Entry

The global extension is dormant until ordinary Pi input activates a workflow owner. For explicit `/skill:<name>` input, Pi's `input` event exposes the raw Skill command before expansion and lets the adapter bind the invocation without changing the command. For natural-language input, Pi retains description-based Skill selection; the adapter supplies a small host protocol and refuses mutation until the agent has bound one top-level workflow owner. It may use observed Pi-native Skill expansion or a generic extension tool to bind the selected owner, but it must not keyword-route the user's request or manufacture a second semantic decision.

The original user turn records the requested terminal intent. A design-only request finishes after validated design review; a plan-only request finishes after validated plan review; an end-to-end implementation request may continue through the canonical phases permitted by its mode and authority. Internal `read_only`, `micro`, and `standard` profiles may remain mechanical policy inputs, but they are never required user syntax.

The extension exposes no required workflow command or startup flag. Optional diagnostics may report, stop, or inspect current state, but command discovery and documentation must make clear that normal use begins with natural language or `/skill:<name>`.

### D3: Semantic Handoff To Pi Follow-Up

Pi-specific handoff encoding belongs entirely to the extension. The adapter provides one small typed runtime boundary through which the active agent reports entry, completion, blockage, or a requested next Skill plus evaluator role and evidence references. Extension prompt guidelines describe this host protocol; reusable Skill prose describes only the semantic handoff. The adapter checks the request against the generated routing and lifecycle projection before calling `sendUserMessage()` with a Pi-native `/skill:<next-owner>` follow-up.

The handoff boundary must distinguish phase completion from final settlement. `agent_end` may schedule an already validated continuation, while `agent_settled` records externally observable completion only after retries, compaction, and queued follow-ups have drained. Free-form assistant prose never advances state. A stale owner, invalid evaluator role, changed terminal intent, missing approval evidence, or repeated repair returns a typed stop without inventing a route.

### D4: Pi-Native State, Ledger, Progress, And Replay

Live host state is stored as versioned Pi custom session entries and reconstructed only from the active session branch. It includes request identity, terminal intent, semantic owner and role, internal mode, authority source, active artifact references and digests, current task ID, dependency state, progress, attempts, accepted findings, pending handoff, tool profile, and terminal outcome. Pi session replacement, fork, resume, compaction, retry, and settlement events own the lifecycle of this state.

The Pi task ledger is a host projection of an approved plan, not a second planning authority. `plan-change` continues to own task IDs, dependencies, topology, touch sets, locks, oracles, recovery policy, and delegation/parallel permission. The extension validates or imports that projection at the artifact boundary, then owns runtime admission, current-task progress, attempt accounting, and continuation. Durable approved artifacts remain Git truth; Pi JSONL is the recoverable execution record for the active host session.

The central Python runtime may remain an out-of-process deterministic artifact compatibility validator until a later independent design justifies replacement. Pi invokes that boundary directly when durable artifact validation is needed; neither the model nor a Skill locates or executes a lifecycle CLI, and Python never polls or advances the Pi loop.

### D5: Authority And Tool Policy

The separate `--auto` marker is removed. Exact authority is supplied by the active Pi host profile and recorded with the invocation. The portable default remains phase-gated. On this explicitly authorized validation machine, the existing user-level Pi settings file carries a namespaced `codingHarness` object whose versioned `authorityProfile = "local-validation"` preauthorizes bounded repository-local `micro` and `standard` continuation while still respecting the user's terminal intent. An absent profile selects the portable phase-gated default, and an unknown or malformed profile fails closed. A generic implementation request alone does not silently rewrite portable approval semantics; persisted invocation state identifies the exact settings-backed authority source.

Before one workflow owner and authority are bound, write/edit and mutating shell operations fail closed with guidance to enter the appropriate workflow Skill; read-only discovery remains available. Once bound, active tools and `tool_call` preflight derive from the current semantic phase and approved touch set. Protected paths, external mutation, credential exposure, destructive history, commit, push, publish, deployment, unsupported modes, and work beyond the user's terminal intent remain blocked independently of local preauthorization.

### D6: Behavior-Bearing Extension Modules

The maintained package remains one Pi extension process but is decomposed by owned behavior rather than by pass-through layers:

- `skill-bridge`: explicit Skill input, natural-selection binding protocol, semantic handoff translation, and next-Skill expansion.
- `authority`: host-profile resolution, terminal-intent binding, and mutation admission evidence.
- `session-state`: versioned custom entries, branch replay, resume/fork/compaction boundaries, and terminal state.
- `task-ledger`: approved-plan projection, dependency readiness, current task, progress, attempt, and accepted-finding state.
- `transition-runtime`: mechanical validation of generated canonical routes, outcomes, repair budgets, and terminal conditions.
- `tool-gate`: active-tool profiles, touch-set enforcement, protected paths, and dangerous-command preflight.
- `continuation`: `agent_end`, follow-up scheduling, retry-safe pending state, and `agent_settled` signaling.
- `artifact-bridge`: deterministic validator invocation and digest-bound artifact references without owning artifact meaning.
- `ui-status` and `telemetry`: inspectable progress and sanitized observation data.
- `index.ts`: Pi event/tool registration and dependency wiring only.

Each module must carry behavior and a direct test seam. The implementation may combine modules whose deletion test proves they are pass-through wrappers, but it must not collapse semantic prompts, state, gates, continuation, and persistence back into one controller file.

### D7: Global Package And Discovery Boundary

The local `integrations/pi` package is installed through Pi's documented user-level package mechanism so its extension loads in every repository from `~/.pi/agent/settings.json`. The same existing file owns the namespaced machine-local `codingHarness` authority profile; the extension reads only that namespace, never provider credentials or model configuration. This repository's `.pi/settings.json` must not load the same extension again. The 40 Skills continue through one child symlink per public ID under `~/.agents/skills`; the Pi package exposes only the extension unless a later installation design replaces the symlink topology atomically.

The extension resolves its generated contract and support files from its package location, never from the active project's current working directory. It treats the active repository as task data and must work in a disposable Git project outside this checkout with `--no-approve`, proving no hidden dependency on project-local settings or this repository's AGENTS file.

### D8: Skill Thinning And Portable Fallback

The seven semantic-kernel Skills retain concise phase meaning, durable evidence requirements, review ownership, and textual handoffs. Exact task-ledger fields, transition enums, retry loops, scheduling instructions, host state restoration, physical actor binding, and provider-specific mechanics move to canonical machine contracts or the Pi adapter. Fixed schemas that protect durable artifacts remain machine-owned contracts with short Skill-facing semantic summaries rather than copied procedural checklists.

An extension-off oracle loads the same generated Skills with Pi extensions disabled and verifies that an agent can still identify the requested owner, read its semantic responsibilities, and state the correct next Skill/evaluator handoff. This fallback is not expected to reproduce Pi's automatic state, gating, or continuation; it proves the Skills have not become a hidden Pi client or headless agent runtime.

### D9: Migration And Supersession

The existing `/csheng-run`, `--csheng-mode`, `--csheng-auto`, `workflow-command`, and phase-goal prompt path are experimental compatibility evidence only and are removed from the converged default surface. Pure low-level state validation, replay, tool-policy, contract-projection, and telemetry code may be retained only after being detached from the explicit runner and covered through the new module contracts.

The new native path is proven with deterministic tests and temporary `--extension` loading before the global package setting is changed. After global installation, the project-local extension entry is removed and a fresh disposable repository validates discovery, explicit Skill invocation, natural workflow entry, semantic review handoff, resume, terminal intent, and extension-off portability. No long-lived dual-controller mode is permitted.

## Architecture Economics

- `demand_evidence`: the current extension passes isolated workflows only through a special command and disappears outside this checkout, while the user requires ordinary Pi usage to receive native harness state and progress without turning Skills into a controller DSL.
- `scarce_resource`: one reliable owner for loop mechanics and state; maintaining the same controller semantics in Skill prose, Python compatibility code, and a TypeScript command runner consumes review attention and creates divergent authority.
- `status_quo`: retain the explicit TypeScript runner; rejected because it changes transport but preserves the sidecar-controller architecture and non-global user experience.
- `smallest_sufficient`: one globally installed, modular, in-process Pi host adapter that consumes canonical semantic projections and augments native Skill invocation; selected because Pi already supplies the required session and event primitives.
- `structural_investment`: build a provider-neutral host SDK or independent multi-agent orchestrator now; deferred because only one maintained Pi single-agent host is demanded and the portable semantic boundary already preserves a future extraction seam.
- `marginal_tradeoff`: binding mechanics to Pi public extension APIs adds provider-version maintenance, but it removes a user-visible parallel workflow and assigns state, tools, scheduling, and replay to the runtime with the lowest lifecycle cost.
- `opportunity_cost`: the refactor replaces some already passing prototype code and delays broader task use, but continuing the prototype would entrench the wrong dependency direction and make later Skill thinning more expensive.
- `owner_and_incentives`: `integrations/pi` owns Pi API behavior and local operational failures; contracts and authored Skills own portable semantics; the central Python runtime owns only deterministic compatibility boundaries; this repository owns cleanup of the retired runner surface.
- `comparative_advantage`: Pi natively exposes input interception, custom tools and entries, active-tool control, session branches, follow-ups, retry/compaction lifecycle, settlement, status UI, and packages, whereas Skills are best at concise reusable engineering intent.
- `chosen_option`: `PI-HARNESS-003`, the smallest sufficient modular Pi host adapter with no required workflow command.
- `upgrade_trigger`: require a shared provider-neutral mechanical SDK only when a second maintained host needs the same state and transition implementation; require a separate orchestrator only when approved multi-actor or cross-provider execution becomes current demand.
- `recovery_and_oracle`: test the adapter temporarily before global installation, retain `--no-extensions` as an operational bypass, preserve Git artifacts as durable truth, and require model/state, contract, component-event, global-discovery, live workflow, resume, and extension-off portability oracles.

## Implementation Surface

- `contracts/`, `scripts/generate-pi-contracts.py`, and `integrations/pi/generated/` expose the minimum canonical semantic ownership, route, evaluator, mode, and authority data needed by the adapter without phase-goal prose or a copied controller table.
- `integrations/pi/extensions/coding-harness/` becomes the modular global extension; the existing `csheng-workflow` directory is removed after any reusable low-level code is migrated.
- `integrations/pi/package.json`, the `codingHarness` namespace in global Pi settings, and project `.pi/settings.json` establish one global extension instance, one explicit local-validation authority source, and no duplicate project-local load. Package installation may reformat JSON, so preservation is judged by structural equality of all pre-existing non-package, non-harness settings rather than whole-file bytes.
- `integrations/pi/tests/` gains pure transition/ledger tests, fake-Pi component tests, package/discovery checks, authority and tool-gate tests, replay/resume tests, and negative tests for duplicate or invalid handoffs.
- `integrations/pi/scripts/` provides disposable repositories outside this checkout for explicit Skill, natural-language, resume, terminal-intent, and extension-off probes without hard-coding a provider identity or exposing credentials.
- The authored semantic-kernel Skills under `src/skills/`, their routing references and contracts, and generated root-flat `skills/` are thinned to semantic responsibility and textual composition while retaining durable artifact meaning.
- `AGENTS.md`, `README.md`, stable architecture documentation and diagrams, the Pi integration guide, and the Pi handoff replace the command-runner narrative with the native host-adapter boundary.

## Validation

- Validate the version-4 design and linked plan with the central artifact validator, then run bounded `review-design` and `review-plan` evaluation before the joint human gate.
- Use generated-contract parity and negative source checks to prove the extension contains no handwritten semantic route table, phase-goal checklist, required `/csheng-run`, or provider-specific execution identity.
- Use model/state-transition tests for Skill handoffs, terminal intent, approval evidence, task readiness, repair budget, invalid transitions, replay, and settlement.
- Use fake-Pi component tests for raw `/skill:*` input, natural owner binding, mutation-before-binding rejection, active-tool changes, custom-entry persistence, follow-up scheduling, resume/fork behavior, and `agent_settled` completion.
- Install the package globally only after temporary-load tests pass, then use Pi RPC from a disposable repository outside this checkout to prove one extension instance, 40 unique Skills, no required runner command, the exact `local-validation` authority source, and correct diagnostic availability. Compare a secret-safe structural digest of all pre-existing non-package, non-harness settings before and after installation so provider and model state cannot drift silently.
- Run one explicit `design-change` workflow that automatically reaches `review-change(role=review-design)` and stops at the requested design boundary, plus one natural bounded implementation workflow that reaches verification, review, truth sync when required, and close without a special entry command.
- Run the same semantic Skill request with extensions disabled and verify that the Skill remains understandable and names the same semantic handoff without attempting a Skill-local script.
- Regenerate the Pi projection, root-flat Skills, index, and diagrams; run all Pi tests, `bash scripts/check.sh`, `git diff --check`, and source scans for retired runner and Skill-local harness patterns.

## Recovery

Use fix-forward inside the approved repository and exact global-settings surfaces. Test through temporary extension loading before editing global Pi package settings. If the global adapter prevents Pi startup or cannot prove unique discovery, bypass it with Pi's no-extension mode or remove only the local package registration and `codingHarness` namespace while preserving every pre-existing setting and repository evidence; do not restore the command runner as a second authority. Stop on credential exposure, mutation before authority binding, state replay ambiguity, semantic-route drift, work outside the active repository or terminal intent, repeated repair, or Pi public-API incompatibility. No Git reset, commit, push, publication, or destructive source rollback is authorized.
