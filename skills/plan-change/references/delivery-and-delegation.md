# Delivery And Delegation

Read this reference when a plan must record delivery endpoints, two-stage planning versus dispatch, cohesive worker slices, required versus missing authority, decision-versus-fact classification, compact live plan versus historical exemptions, same-task continuation without handles, or its implementation-approval summary. Ordinary local plans that do not claim those arrangements may skip it.

## Goal Gates And Planning Context

Keep four kinds of information distinct in the plan and approval summary:

- Goals, required acceptance, authority, and explicitly designated file/interface/order restrictions are binding. Changing them needs the corresponding owner decision.
- Observed touch files, baseline SHAs, inferred implementation details such as task granularity and dependency edges, and environment snapshots are planning context. Refresh them when facts change; do not promote them to immutable approval gates merely because the user approved the plan.
- Exact write sets, source identities, locks, and compare-and-apply preconditions required by an execution host are mechanical capabilities for that invocation. The parent may refine or redispatch inside existing authority, but an executor must not bypass these guards.
- Verification evidence describes a particular result or version. Drift may require selective invalidation and re-verification; that is not automatically a change to permission or goals.

When parallel work touches the same file, the implementation owner reads and preserves both changes, reconciles a compatible result, and verifies the affected integration. Plan for that convergence rather than treating any diff as a manual checkpoint. A real conflicting requirement, unresolved ownership, unsafe overwrite, or newly exceeded authority pauses the affected path; unrelated authorized work continues. Branch integration still respects applicable Git and protected-state permissions.

Model maintenance should track semantic progress and real remaining obligations, not force reapproval for each context refresh. A scope-contained repair loop belongs inside the current task; the task dependency DAG need not grow a new node for every failed check.

## Two-Stage Concretization

Planning records stable, acceptable behavior, non-goals, important reasons, external behavior, acceptance, delivery endpoints, real dependencies, state ownership, covered and missing authority, any authorized best-effort secondary space, and the space an executor may decide. Do not unconditionally freeze local variable names, helper structure, glue around a specified library, every command, or every failure branch. Do not pre-enumerate every secondary feature that the executor may adapt or omit under already authorized discretion.

At planning time, write known write surfaces, dependencies, and resources directly. Mark remaining local investigation as conditional delegation instead of inventing exact files. Ordinary implementation is not blocked by missing delegation metadata.

Before actual dispatch, the parent uses already known scope, inputs, initial write regions, environment, and the host contract. Necessary permission and input checks are not a new economic-research phase. Do not search, probe, estimate time, or call another model solely to decide whether delegation pays. With insufficient context, perform the next useful implementation action locally unless the user explicitly requires delegation. Do not finish the executor's investigation to fill filenames or reopen choices because its model changed.

A task already claimed delegation-ready must actually be ready. If approval explicitly fixed a file, interface, or ordering restriction, do not expand it; an observed inventory is not that restriction. If it approved only a module-level range, the parent may refine files and coordinate ownership inside that range. Reassigning in-range resources is usually the parent's job; only a change to a user-reserved decision rises to a human. Dispatch refinement is not scope expansion.

## Independent Work And Delivery Time

Record independence and join expectations during normal planning, not through a separate estimation exercise. Two substantive independent tasks may both go to children while the parent coordinates and waits; an asynchronous singleton may overlap other useful work. Neither parent busyness nor minimum batch size is a goal. Keep trivial or tightly coupled work local when already apparent, without numerical time, file-count, or task-count cutoffs.

A new main should receive goals, rationale, necessary inputs, initial write regions, protected boundaries, expected independent groups, and explicit integration/acceptance joins. Initial regions are refinable context, not a complete read set or user-approved file whitelist. Actual result scope and shared-resource conflicts still need reconciliation. Failed checks and same-task repair do not add new planning phases.

## Authority, Capability, And Delivery

Whether an action belongs to this task, whether matching authority exists, and whether current capability can perform it are three independent judgments. There is no default operational permission. Standing deploy permission does not turn a design-only or source-only task into deployment. A plan that mentions deploy does not grant deploy permission. Credentials are not permission.

A planning-only current activity is not a reason to exclude the useful delivery endpoint from a proposed plan. Applications and services consider commit, push, existing-environment deploy, and post-deploy verification; libraries, tools, and Skills use the relevant publish, install, or handoff endpoint. Record that endpoint so a later approval can cover it. Ask only about a real unresolved delivery decision, and respect an explicit source-only or design-only scope for the current request.

When the action is in this task and a trusted project convention or the current request already covers its goals and side effects, check remaining premises and consume that approval. Ask again only for a new goal, real side effect, or boundary conflict. An already approved same-goal deployment that lacks only a generated digest, binding, or similar execution product is not a new approval; generate, verify, and continue.

Record required authority and missing authority separately. Already covered required authority is not a `manual_checkpoint`. Investigable facts and implementation products the executor can generate are not missing authority. A capability gap blocks that step without blocking independently completable authorized work and without reporting local completion as end-to-end delivery.

If a secondary adaptation would change the main goal, or would make a later production action's commitments, risk, goals, or permissions exceed the approved boundary, pause only that affected action and obtain a narrow authorization before the impact. Independent, safe, authorized work continues. Do not reopen the whole design for an in-scope best-effort tradeoff, and do not disclose a newly material production risk only after going live.

When the task includes implementation and delivery, the plan states the delivery endpoint and the evidence that endpoint needs. `close-change` still owns later completion judgment. This skill does not rewrite live project permissions.

## Implementation-Approval Summary

End every plan intended for later implementation with a short, user-facing summary that makes the next decision explicit rather than leaving approval implied among tasks. Classify remaining items as a user decision, an investigable fact, an implementation product to generate, or technical verification. Only a true user or external decision belongs in Manual checkpoints. Use the smallest shape that can state currently effective goals, discretion, and real pause conditions:

- **Decision requested:** whether the user is being asked to authorize implementation now, or the plan is intentionally plan-only.
- **Approval scope:** the actions, targets, repositories, and side effects the user may approve together, including the exact objective, write or operational surfaces, delivery endpoints, and external effects. List commit, push, publication, deployment, destructive cleanup, configuration, installation, and live-data actions separately; omission means they are not approved.
- **Already covered:** trusted approval or project policy that already covers a listed action, with its source and matching target/side effects. Do not ask again for that same approval.
- **Agent-owned execution:** technical checks, investigable facts, and generatable products the agent must execute inside the authorized scope. Do not ask approval for these. Their results still have to be obtained; a new privilege, live side effect, or protected-state boundary remains a real checkpoint.
- **Manual checkpoints:** each currently unresolved authority, account, credential, access, license, physical prerequisite, or user decision; name the affected task, owner, and why it blocks. Do not disguise it as an implementation subtask.
- **Continuous-execution boundary:** after the user approves the stated scope and any named checkpoint, continue through ordinary in-scope investigation, dispatch refinement, worker execution, verification, review adjudication, and accepted repair without requesting serial approvals. After the user answers the unique blocker, resume the original authorized task rather than ending on confirmation. Pause only for a new goal, material side effect, protected-state risk, acceptance change, authority gap, or other decision explicitly retained by the user. Independent authorized work continues while only the affected production or protected-state action waits. This is the current scope's continuation rule, not a universal endless-execution engine.
- **Excluded actions:** state actions intentionally outside the request so a later host/tool step cannot infer them from implementation approval.

Do not force a user to approve implementation merely because they requested a plan. For a plan-only request, still name the useful delivery endpoint in the proposal, say that no implementation or delivery authority is requested, and name the exact later decision needed. Do not use this summary as a generic lifecycle gate, a task ledger, an approval ledger, a runtime schema, or an excuse to ask the user about local choices the executor can make. Keep historical exemptions and old reviewed revisions in stage records and cite them shortly as provenance; do not copy old gates into the live summary, and do not leave contradictory live pending or excluded gates beside a top-level override sentence. New evidence that changes the stated scope or boundary requires a new, narrow approval; a different model, reviewer, worker, authorized secondary adaptation, or normal repair iteration does not.

When the user later adds explicit delivery authority such as commit, push, or deploy, update the currently effective plan, this summary, and affected delivery dependencies to the new authorized objective, scope, and endpoint. Continue without asking permission merely to record that approval. Do not rewrite unrelated approved constraints, expand beyond the newly authorized target or scope, treat document annotation or review success as authority, or waive required verification.

## Cohesive Slices

A worker slice may include investigation, implementation, direct tests, command feedback, and in-scope local repair. Do not split by one file per worker or by sending code and tests to different workers by default. The parent should not exhaust implementation detail and then hand off leftover typing.

Explorer work is for separately valuable or parallel facts. It is not a startup gate for every worker. The worker may investigate callers and implementation inside its slice.

Actively look for independent slices whose interfaces and inputs are stable and whose writes and shared resources do not conflict. Do not pad extra calls. A singleton offload is useful when the host and applicable call policy allow it; if the host is narrower, keep the work local, do not invent a second slice, and do not claim wall time will shrink. Shared skills cannot override a host's tighter singleton or delegation limit.

Shared interfaces, generators, lockfiles, registries, fixtures, ports, and external state need an explicit owner. Non-overlapping files do not prove independence. Only real dependencies create serial order; document chapter order does not.

For actual delegation, record repository ownership, an exclusive write set, resource locks, safe isolation, and convergence ownership with the active parent. The host owns its execution mechanisms; planning does not implement a lock or prescribe working-directory flags, snapshot paths, schedulers, or handles. Use the current checkout by default where safe and permitted; isolation needs a real policy or state reason, not delegation terminology alone.

## Parent Decisions Versus Labor

Parent-owned verification, repair, and continuation mean adjudication, authority, cross-task synthesis, and final acceptance. They do not mean every test, diagnosis, or repair command must run on the parent. Verification or repair labor may have factual dependencies but does not by itself require an intervening parent decision.

Keep a decision boundary where the parent must synthesize, authorize, coordinate across tasks, adjudicate findings, accept the result, or decide continuation. Compatible hosts may consume true dependencies that have no intermediate decision. Do not compile a plan into a static worker-to-reviewer-to-repair chain that bypasses that adjudication. Concrete DAGs, queues, and workspaces belong to the host.

## Same-Task Interaction

A cohesive task may include several parent-child exchanges. The plan may say that follow-up repair or directed rereview should prefer the same worker or reviewer while the parent keeps adjudication. Do not prefill child handles, candidate IDs, or session identifiers that do not exist yet. Host results and progress records hold those mappings during execution.

Do not add a runtime field, public continuation skill, or durable actor binding. If the current host cannot continue a child, say so at dispatch; do not write a fake ready handle into the plan.

## Readiness And Profiles

Local readiness is the ordinary check that objective, authorized writes, protected behavior, factual dependencies, delivery endpoints, and acceptance evidence are coherent. It does not require delegation profiles, parallel policy, exact dispatch paths, or a fixed review budget.

Assess delegation readiness only for slices actually delegated or claimed delegation-ready, using the existing semantic profiles and facts. Keep that vocabulary provider-neutral. Plans that do not claim delegation readiness may omit profiles. Claiming delegation-ready without those facts is fabrication, not planning.

## Examples

These examples are not template gates.

A module-level approved slice may be dispatched with host-exact files inside that module. An exact write set explicitly fixed as an approval boundary may not gain extra paths at dispatch; an incidental planning inventory may be refined within the approved slice. A design-only task stays design-only even when standing deploy permission exists. A planning-only request may still propose future commit, push, deploy, publish, install, or handoff endpoints without granting them. A delivery task with already covered commit, push, and deploy permission records those endpoints and consumes the permission instead of repeating the same approval. A delivery task that already has same-goal deploy approval and lacks only a new digest or binding generates that product, verifies, and continues. After an explicit later addition such as `approved, include commit/push/deploy`, the live plan and approval summary are reconciled to that authorized endpoint and superseded excluded gates move to provenance. A user-specified library with undecided glue leaves the glue to the executor. A best-effort secondary matcher that cannot be expressed is marked unsupported with evidence while the main path continues; the same matcher stays required when the user named it or the main goal depends on it. After the user answers the unique blocker, the same task resumes implementation rather than closing on a promise to continue. If a secondary tradeoff would change later production commitments or risk, independent local work continues and only the affected production action pauses for a narrow authorization. A cohesive parser-fix slice can locate implementation, edit approved files, run existing checks, and repair failures it caused, then return a candidate and evidence without changing a public schema. Two slices that still need an undecided shared schema are not independent.
