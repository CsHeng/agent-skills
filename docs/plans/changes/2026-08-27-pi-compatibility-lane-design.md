+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "low"
truth_sync_required = false

[scope]
impl_file_refs = [".pi/settings.json", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []
+++
# Design

## Problem

The Pi handoff is still a proposed architecture and experiment, while this checkout has only read-only discovery evidence: Pi 0.84.2 can discover all 40 generated skills, but there is no maintained Pi integration lane, no deterministic session-state replay or telemetry test, and no configured Responses provider for the user's existing Ante gateway. The user explicitly authorized one uninterrupted P0-P4 experiment on this non-primary machine on 2026-08-27, including repository-local experimental changes, local Pi consumer configuration, API-backed smoke tests, and continuous execution without another design or plan gate as long as the work stays inside this boundary and nothing is pushed.

## Goals

- Establish the P0 baseline by correcting the handoff's stale 39-skill count and Markdown list defects, while retaining the legacy harness unchanged.
- Add an experimental `integrations/pi/` package that uses only Pi public extension APIs for status, completion notification, aggregate telemetry, and current-branch state replay.
- Add repository-local Pi settings that load exactly this extension and generated skill root, select the secret-safe `ante` Responses provider, and expose exactly the GPT-5.5/5.6 models advertised by that gateway on 2026-08-27.
- Prove P3 with deterministic unit tests plus no-model Pi discovery/RPC smoke tests, then enter P4 with bounded live model connectivity and read-only repository tasks.
- Keep prompts, tool inputs, tool outputs, API keys, and absolute session paths out of extension telemetry and tracked files.

## Non-Goals

- No `/mode`, tool-profile switch, mutation gate, protected-path policy, dangerous-bash approval, artifact bridge, task ledger, review/repair loop, micro workflow, standard workflow, subagent scheduler, Herdr integration, or router.
- No automatic model selection or model switching; the extension only makes an explicitly selected provider/model available.
- No project-trust decision and no `resources_discover` hook; Pi's built-in trust flow and one native skill discovery path remain authoritative.
- No regulated, external-mutation, auth-management, deployment, network-change, GitOps, or IaC workflow.
- No deletion, rewrite, or redistribution change to `src/runtime/harness`, runtime bundles, contracts, generated `skills/`, plugin manifests, or stable architecture documentation.
- No commit, push, publish, release, or claim that P4 comparative evidence is complete after only the initial field sample.

## Boundaries

Architecture decision `PI-COMPAT-001` selects one reversible repository-local TypeScript extension package. Repository and approved artifact truth remain in Git and the existing Python harness; Pi owns only its native loop plus session-local observation. The extension may append a versioned custom telemetry entry to the active Pi session and, only when `CSHENG_PI_TELEMETRY_DIR` is explicitly set, append a sanitized JSONL record below that exact directory. Replay must consume `ctx.sessionManager.getBranch()` supplied by the caller rather than all session entries.

The provider adapter reads the Ante base URL from the process environment and gives Pi the literal credential reference `$ANTE_API_KEY`; it never copies the credential into repository content, Pi auth state, telemetry, logs, or command output. The gateway catalog probe exposed `gpt-5.5`, `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`; public `gpt-5.5-pro` is deliberately absent because this key's gateway did not advertise it. GPT-5.6's unsuffixed alias is not duplicated because it routes to Sol. The adapter uses zero cost metadata because Ante pricing is not proven to match OpenAI list pricing.

Repository-local `.pi/settings.json` is the only Pi consumer configuration changed by this experiment. Its resource paths resolve from `.pi/` to `../integrations/pi/` and `../skills/`, it contains no credential value, and Pi's built-in project trust remains the only authority that activates it. The user's global `~/.pi/agent/settings.json`, `auth.json`, and model store remain unchanged. Field tasks run with `--approve`, an explicit read-only tool allowlist, and an explicit model so the observational extension cannot widen their authority.

## Architecture Economics

- `demand_evidence`: one expendable validation machine, one repository, one Pi session at a time, 40 already discoverable skills, and a need to observe five to ten low-risk tasks before investing in lifecycle migration.
- `scarce_resource`: reliable attribution between model quality, Pi mechanics, and Skill/extension responsibility; adding multiple control features now would destroy that attribution and increase Pi API-churn cost.
- `status_quo`: continue ad hoc `--skill` and model flags with no maintained observation lane; rejected because it cannot produce replay or telemetry evidence for P4.
- `smallest_sufficient`: one TypeScript package with provider registration, status, aggregate telemetry, current-branch replay, pure tests, and explicit CLI selection; selected because it provides the missing evidence without changing workflow authority.
- `structural_investment`: implement modes, gates, artifact bridge, micro/standard lifecycle, and review schema now; deferred because each depends on P4 evidence and introduces coupled authority changes.
- `marginal_tradeoff`: a few small modules and tests buy repeatable evidence; the next gate/lifecycle increment adds policy duplication and safety risk before observational value is known.
- `opportunity_cost`: every extra runtime feature delays the field trial and makes failures harder to attribute.
- `owner_and_incentives`: `integrations/pi/` owns Pi mechanics and cleanup; existing Skills/contracts own semantics; the user controls local installation and model choice; no future maintainer inherits an implicit migration commitment.
- `comparative_advantage`: TypeScript directly matches Pi's public extension and package surface, while the existing Python harness remains the lower-cost owner of deterministic artifact contracts.
- `chosen_option`: reversible observational adapter with explicit Ante Responses registration.
- `upgrade_trigger`: P4 produces at least five bounded task records with correct discovery, no secret leakage or unauthorized mutation, successful current-branch replay, and acceptable Pi upgrade maintenance; only then may a separately approved P5 gate/micro slice begin.
- `recovery_and_oracle`: run Pi with `--no-approve` or remove the experimental repository-local settings and integration diff to return immediately to the unchanged legacy lane; unit tests, Pi RPC discovery, provider catalog checks, live Responses smoke, read-only field-task oracles, and `bash scripts/check.sh` protect the boundary.

## Implementation Surface

- `.pi/settings.json`: trusted project-local selection of the one extension path, one skill root, Ante provider/model default, and the four model-cycle entries; no key or base URL is stored.
- `integrations/pi/package.json`: private experimental Pi package manifest and local test scripts.
- `integrations/pi/README.md`: exact ownership, installation, secret handling, model availability, telemetry schema, validation, and removal instructions.
- `integrations/pi/extensions/csheng-workflow/provider.ts`: pure Ante environment validation and static gateway-advertised model definitions.
- `integrations/pi/extensions/csheng-workflow/state.ts`: telemetry record schema, current-branch replay, run aggregation, and safe session reference handling.
- `integrations/pi/extensions/csheng-workflow/telemetry.ts`: opt-in sanitized JSONL persistence.
- `integrations/pi/extensions/csheng-workflow/index.ts`: public Pi hooks, status command, notification, session custom entries, and provider registration without tool mutation.
- `integrations/pi/scripts/run-field-probes.sh`: thin, strict-mode Bash orchestration for four model smokes and five read-only factual probes with exact output assertions; it owns no reusable workflow rule.
- `integrations/pi/tests/`: deterministic provider, state-replay, telemetry-redaction, and disk-writer tests.
- `docs/plans/2026-08-27-agent-skills-pi-handoff.md`: P0 factual and Markdown corrections only.

## Validation

- Validate and review this design and its execution plan before using the user's pre-confirmed approval.
- Run Node's TypeScript-stripping test runner over every integration test.
- Run `bash -n` and ShellCheck when available over the field runner.
- Load the extension in Pi RPC/offline/no-model mode and prove it registers without startup errors.
- Prove the generated skill root exposes exactly 40 unique skill commands through Pi RPC.
- With mise-provided Ante variables, list exactly the four gateway-advertised models and run one minimal Responses smoke per model without printing the key.
- Run at least five bounded read-only P4 probes with explicit tool and skill paths, store only aggregate telemetry, and evaluate their concrete output oracles.
- Run `git diff --check` and the repository aggregate check; no generated source refresh is expected because authored Skills/contracts/runtime are untouched.

## Recovery

Use fix-forward for repository implementation and test failures. The legacy harness remains untouched and is the safe fallback. A secret leak, an unexpected tracked-file mutation from Pi, a provider response incompatible with Pi's public Responses transport, state replay from outside the active branch, or a required authority expansion stops the experiment with evidence. `--no-approve` bypasses all project-local Pi configuration during diagnosis; no automatic rollback, commit, or push is authorized.
