# Provider-Neutral Delegation Profiles Design

## Status

- design_version: 1
- change_class: B
- design_depth: design-lite
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved provider-neutral plan semantics, parent-owned translation, optional defaults, and independent Skill/runtime ownership on 2026-08-29.
- decision_state: approved
- review_status: passed
- recommended_next_phase: plan

## Objective

Make execution-grade plans reliably delegable when a user explicitly requests subagent-assisted implementation, especially for parallel and multi-repository work, without teaching Skills about Pi, an extension, a provider, a model, a scheduler, or a runtime protocol.

Plans should expose enough provider-neutral task semantics for any capable active agent to decide whether and how to delegate. A compatible host may translate those semantics into its own tool arguments, while an ordinary agent or a plan without the optional fields remains valid.

## Current truth and problem

`plan-change` already requires stable task IDs, dependencies, touched surfaces, verification, delegation eligibility, safe isolation, resource independence, and convergence ownership. It permits plans to describe task complexity or desired independence but intentionally forbids concrete model or product scheduling policy.

It does not currently name a canonical provider-neutral execution/reasoning vocabulary or require repository-root readiness when delegated implementation was explicitly requested. The active agent therefore must reconstruct those details from prose.

In the first production use of a bounded subagent runtime, a multi-repository plan was translated into one repository-rooted DAG. The runtime correctly rejected absolute sibling-repository paths, missing worker writes, write/scope mismatch, and unavailable staging parents before any child model call. The plan's semantic change scope was valid, but it lacked a sufficiently explicit physical delegation decomposition for the consuming agent.

This repository must repair the reusable planning semantics without importing the runtime's schema or turning plans into executable controller state.

## Selected boundary

The selected design is optional semantic task metadata owned by `plan-change` and interpreted by the active agent:

1. When the user explicitly requests delegated or subagent-assisted implementation, every task must state whether it is delegation-ready and why.
2. A delegation-ready task records provider-neutral execution intensity, reasoning intensity, repository ownership, write set, locks, isolation, and convergence responsibility.
3. The active agent may translate those semantics into any compatible host mechanism. The Skill neither names nor calls that mechanism.
4. The receiving runtime is free to ignore absent semantics, use defaults, or reject incompatible concrete arguments. It does not discover or parse the Skill.
5. Plans not requesting delegation may omit the optional profiles and remain execution-grade under existing guidance.

This is semantic interoperability, not an executable contract. There is no import, generated shared schema, runtime dependency, adapter package, capability discovery, or lifecycle handoff between repositories.

## Canonical semantic vocabulary

Delegable tasks use the established vocabulary already present in historical execution plans:

```text
execution_profile = fast | balanced | deep
reasoning_profile = light | standard | deep
```

The values describe desired execution behavior and reasoning effort, not concrete models, providers, prices, context windows, or thinking-level flags. No Skill assigns Sol, Terra, Luna, or any other model family to these values.

A plan may record the fields in its native Markdown or structured metadata style. Exact rendering is not a public runtime schema. The complete task proposition must preserve:

```text
task_id
depends_on
scope_slice
touched_surfaces
repository_owner
delegation_eligibility
parallel_group
execution_profile
reasoning_profile
isolation
resource_locks
write_set
verification
done_when
failure_policy
convergence_owner
```

Fields may be omitted when not applicable, but a task marked delegation-ready after an explicit delegated-implementation request must include execution profile, reasoning profile, isolation, repository ownership, locks, write set, and convergence owner.

Unknown or unsupported host mappings do not make the plan invalid. The active agent uses a compatible default or retains the task, while preserving authority and verification semantics.

## Repository-root readiness

A delegated writable task must belong to one repository root. Its write set is expressed relative to that repository and cannot include absolute sibling-repository paths, environment-variable pseudo-paths, or multiple Git roots.

For a multi-repository milestone, `plan-change` must choose one of these semantic decompositions:

- independent repository-owned tasks, each executable from its own repository context;
- parent-owned serial integration for cross-repository effects;
- an explicitly designed staging or external-mutation boundary with its own owner, cleanup, and verification.

The plan must not imply that one worker can mutate sibling repositories merely because the overall milestone spans them. It also must not prescribe a specific host's `cwd` flag, worktree path, snapshot implementation, or staging directory.

## Delegation readiness

When delegated implementation is explicitly requested, `subagent_ready: true` is justified only when:

- dependencies that define the task input are frozen;
- write sets are exact and do not conflict with potentially concurrent tasks;
- repository ownership and execution context are unambiguous;
- required parent directories or creation authority are identified;
- resource locks cover shared non-file state;
- isolation preserves relevant uncommitted context;
- task verification is executable or has explicit substitute evidence;
- the calling agent retains integration, verification judgment, review adjudication, repair decisions, continuation, and the final response;
- a serial fallback or typed capacity stop is stated where parallel capacity is not guaranteed.

If these facts are unavailable, the plan marks the task `subagent_ready: false` or keeps delegation conditional rather than inventing paths or runtime behavior.

## Skill responsibilities

### `plan-change`

`plan-change` owns the task semantics and readiness check. It must add the canonical profiles and single-repository write-boundary guidance without requiring a plan template, provider, runtime, or downstream Skill.

### `implement-change`

`implement-change` remains lifecycle owner for an approved implementation. When it chooses delegation and the plan carries semantic profiles, it preserves those hints for a compatible active host. It does not interpret model families, require delegation, or fail merely because no host mapping exists.

### Active agent and host

The active agent decides whether delegation is useful, translates optional semantics, invokes available tools, evaluates evidence, and retains all parent-owned decisions. The host owns concrete model binding, scheduling, process isolation, and tool execution.

No change is made to `may_spawn_agent` for `plan-change`; planning remains non-executing. `implement-change` already permits optional agent use and retains its current authority contract.

## Stable truth

`docs/architecture/skill-composition.md` should state that plans may carry optional provider-neutral delegation profiles and repository-root readiness, while excluded mechanics remain host-owned. It must not name a concrete consumer extension or provider model.

The authored source remains `src/skills/`. Generated `skills/` projections and indexes are refreshed through repository generators. No generated Skill file is edited directly.

## Alternatives

### Leave complexity as free prose

Rejected because the production failure demonstrates that free prose did not reliably preserve repository-root and route-intensity semantics through parent translation. A small canonical vocabulary improves interoperability without adding a controller.

### Publish the runtime tool schema from this repository

Rejected because it would make Skills depend on one host and would turn a provider-neutral plan into an adapter contract.

### Put model IDs into plan tasks

Rejected because model availability, authentication, cost, and naming belong to the runtime/user route boundary. Provider identifiers would make Skills non-portable.

### Require profiles on every plan

Rejected because many plans remain serial, directly implemented, or consumed by hosts without delegated execution. The fields are required only for tasks claimed ready under an explicit delegated-implementation request.

### Add a plan validator or workflow engine

Rejected because this repository owns semantic Skills, not persisted controller state, scheduling, attempts, or settlement. Existing source/generated parity and focused semantic checks remain sufficient.

## Scope

In scope:

- canonical `execution_profile` and `reasoning_profile` guidance;
- explicit delegation-readiness and single-repository write-boundary guidance;
- provider-neutral preservation guidance in `implement-change`;
- authored/generated Skill parity;
- stable skill-composition truth and focused tests that protect structured ownership boundaries.

Out of scope:

- Pi, extension, provider, or model references in maintained Skill truth;
- concrete model ranking, route resolution, scheduler limits, task process state, retries, or telemetry;
- a mandatory plan schema, parser, validator, controller, or ledger;
- changing review policy, implementation authority, or the active agent's final responsibility;
- external user configuration, package installation, commit, push, publication, or deployment.

## Acceptance evidence

- Authored `plan-change` guidance requires canonical profiles and repository-root readiness only under explicit delegated implementation.
- Authored `implement-change` preserves optional semantic hints without requiring delegation or naming a host.
- Provider/model identifiers remain absent from maintained Skill truth and generated projections.
- `plan-change` remains `may_spawn_agent = false`; `implement-change` retains its existing optional delegation authority.
- A focused semantic fixture demonstrates a single-repository ready task and a multi-repository task split without asserting exact natural-language prose.
- Generated root-flat Skills and indexes reproduce deterministically.
- `bash scripts/check.sh` and `git diff --check` pass.

## Recovery

Use fix-forward inside authored Skill truth, semantic tests, and generated projections. If implementation requires a shared executable schema, host adapter, concrete model policy, or plan parser, return `needs_design_decision` rather than expanding this boundary.

## Implementation surface

Expected authored and stable surfaces:

- `src/skills/workflows/plan-change/SKILL.md`
- `src/skills/workflows/implement-change/SKILL.md`
- an optional concise authored reference under `src/skills/workflows/plan-change/references/`
- `docs/architecture/skill-composition.md`
- focused semantic tests or fixtures

Expected generated surfaces:

- `skills/plan-change/`
- `skills/implement-change/`
- `skills.index.json`
- generated routing/diagram projections only when their source inputs change

No `pi-extensions` file is an implementation dependency of this design.

## Review decision

A bounded design review was required because the change adds durable cross-host semantic vocabulary and modifies when a plan may claim delegation readiness. Review was limited to this design, current authored `plan-change` and `implement-change`, Skill composition truth, contracts ownership, and generated-surface policy.

Direct `review-design` evaluation returned `pass`. The design preserves provider neutrality, keeps `plan-change` non-executing, leaves concrete binding and scheduling with the active host, requires repository-root and convergence evidence only when delegation readiness is claimed, and avoids a shared executable schema or controller. No material scope, ownership, portability, recovery, or generated-truth finding remains.
