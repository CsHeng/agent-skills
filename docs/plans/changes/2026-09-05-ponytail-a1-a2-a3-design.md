# Selective Ponytail Adoption Design: A1, A2, A3

## Status and authority

- Design depth: `design-lite`.
- Decision state: `ready_for_approval`; approval of the resulting design and plan remains pending.
- User-authorized scope: design and planning for the previously evaluated A1, A2, and A3 recommendations. The request explicitly permits planning after design; it does not authorize Skill implementation, installation, benchmark execution, or external mutation.
- Current repository basis: `bdf4e9c` (`fix(plan-change): require causal serial edges`); the working tree was clean before these stage artifacts were created.
- Truth impact: bounded semantic changes to three existing authored Skills and one new Skill-local reference.
- Boundary impact: no public ID, discovery, role, permission, dependency, runtime, or distribution architecture change.
- Independent design review: required because a reuse preference can override a contract, a shared-root fix can widen behavior, and evaluation guidance can accidentally introduce host mechanics or unsupported efficacy claims. One read-only evaluation and at most one focused in-scope repair are budgeted.
- Review status: `pass`. The independent read-only design evaluation returned no material candidate findings; the parent checked the result against A1-A3, S1-S8, and current ownership boundaries and accepted the verdict. No repair was required.
- Companion plan: [A1, A2, A3 implementation plan](2026-09-05-ponytail-a1-a2-a3-plan.md).

## Objective and current truth

Make three existing practices more actionable without importing Ponytail's persona, intensity levels, hooks, runtime state, or line-count optimization goal.

| Recommendation | Current owner and evidence | Bounded gap |
| --- | --- | --- |
| A1: look for existing capabilities before creating another implementation | `src/skills/policies/development-standards/SKILL.md`, especially Scoped Implementation and Dependency Selection, already prioritizes approved scope, repository conventions, durable maintenance, and safe dependency choices | The capability-search order is implicit rather than a short, explicit instruction |
| A2: examine relevant callers before fixing a shared function | `src/skills/workflows/implement-change/SKILL.md`, especially Implement And Verify, already requires a bounded reproducer, smallest durable change, declared verification, and scope preservation | The initial inspection does not explicitly connect a reported symptom to sibling callers, differing caller contracts, and the boundary that owns the violated invariant |
| A3: evaluate real agent behavior rather than prompt wording or advertised savings | `src/skills/disciplines/testing-strategy/SKILL.md`, especially Documentation And Markdown Verification and Fixtures And Environments, already supports consumer-behavior evaluations and explicit environment isolation | There is no focused reference for comparing an existing Skill bundle with a candidate change while controlling hidden instruction activation, acceptance oracles, and quantitative claims |

`docs/architecture/skill-composition.md` assigns the agent loop and session mechanics to the host and request interpretation, evidence judgment, and authority to the active agent. `docs/architecture/maintenance-contract.md` limits repository checks to distribution and maintenance properties rather than agent-behavior enforcement. Those boundaries remain unchanged.

## Chosen design

### A1: contract-aware capability search

Extend Dependency Selection in `development-standards` with a concise search heuristic. First understand the approved requirement and the relevant current implementation. Then look for a suitable repository-owned helper, type, or pattern; check standard-library and native-platform capabilities; check installed dependencies; only then consider a new implementation or dependency under the existing lifecycle-cost rules.

This is an order for finding candidates, not an unconditional ranking of solutions. Stop when a candidate satisfies the owned requirements, compatibility, trust, error, deployment, and maintenance constraints. A repository convention or installed dependency can be the correct choice even when a standard-library replacement exists. Reuse of a similar-looking helper is not justified when its semantics differ.

Preserve the existing exceptions for security-sensitive and non-trivial standards-based capabilities. Do not encourage custom cryptography, authentication protocols, complex parsers, or concurrency primitives merely to avoid a dependency. Do not add a one-line target, a file-count target, a new global audit, or an instruction to replace working approved dependencies.

Keep A1 with its existing policy owner. Do not duplicate the ladder in `implement-change`, language policies, the router, or architecture docs, and do not add a new semantic dependency to force universal activation.

### A2: caller-aware root-cause localization

Refine the initial inspection in Implement And Verify, applying the added guidance to bug fixes that touch shared behavior rather than every edit.

Trace the reported symptom to the relevant entry point, shared function, directly affected callers, and the contract that owns the violated invariant. Use repository-appropriate symbol, reference, configuration, and test evidence; a text search is a starting point, not proof that all callers have been found. Account for public, generated, dynamic, or external callers when that boundary is relevant. Keep the inspection proportional to the proposed change instead of requiring a whole-repository scan.

Fix a shared boundary only when the relevant callers share the invariant. A caller-specific product rule must stay at its owning boundary; do not move it into a common helper merely to reduce duplicated guards or diff size. Preserve intentionally different caller behavior.

Use a narrow reproducer and focused regression coverage for affected sibling paths and protected behavior as needed. Do not require one test per caller or prescribe a framework. If an unknown caller contract prevents a safe bounded change, state the evidence gap and use the existing `blocked`, `replan`, `redesign`, or `needs-authority` outcome that fits the actual problem. Do not infer absence of consumers, broaden the approved repair, or convert a bug fix into a simplification audit.

Keep this guidance in the existing inspection and verification flow without adding a lifecycle gate, new status vocabulary, mandatory evaluator, or cross-Skill dependency.

### A3: optional agent Skill evaluation reference

Add `src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md` and one conditional link from Documentation And Markdown Verification. The reference applies when a user requests efficacy measurement or a bounded risk judgment justifies evaluation and the necessary execution authority and budget exist. Ordinary Skill editing does not require running an experiment.

The reference should cover these decisions in provider-neutral prose:

- **Question and comparator:** state the claimed behavior change and owned acceptance criteria before comparing outputs. For an incremental Skill change, compare the current relevant Skill bundle at a pinned revision with the candidate bundle while keeping unrelated instructions constant. A no-Skill or terse-prose control is optional only when it answers a distinct question; it is not a substitute for the existing-bundle baseline.
- **Controlled execution:** keep the fixture revision, task, host and model configuration, tool and permission surface, budgets, and observable environment comparable. Separate runs with fresh task contexts and isolated writable state. Account for inherited repository and global instructions, plugins, hooks, memory, caches, sessions, and delegated-agent context where relevant. Do not globally disable or rewrite the user's settings to obtain isolation.
- **Activation evidence:** establish which intended instructions are active in each arm and whether a supposedly absent candidate can enter through another discovery or hook path. Use the host's observable configuration/context evidence and, where needed, a discriminating activation control. Record limitations when the host cannot expose the relevant state. Contaminated or materially unverified isolation does not support a causal savings claim; treat the run as invalid for that comparison or explicitly uncertain rather than silently counting it as clean.
- **Independent acceptance evidence:** judge the actual edited files or other owned deliverable through the task's real correctness, completeness, security, accessibility, compatibility, and regression oracles as applicable. Keep acceptance oracles independent of the candidate instructions and outputs. A shorter incomplete feature or weaker safety check is not a win, and necessary tests are not bloat. Reference good/bad cases can check that the oracle distinguishes a plausible shortcut from a valid result. An optional model judge is supporting evidence with a stated rubric and calibration limits, not a sole security oracle.
- **Bounded comparison:** choose a repeat and resource budget justified by the question before execution; preserve per-task observations, attempt counts, failures, timeouts, exclusions, and relevant variance. Do not retry until the desired result appears or silently remove failures from the denominator. No universal sample count, pass percentage, or automatic CI gate is introduced.
- **Claim discipline:** prioritize required behavior over size. Report code/dependency/maintenance-surface measures as contextual proxies and tokens, cost, and latency only when observed comparably. Separate measured observations from inference and judgment. Report observed numerators, denominators, models, tasks, revisions, and limitations rather than universal safety or benefit claims. Without an actual controlled comparator, do not invent a per-repository counterfactual saving.
- **Authority and data boundary:** the evaluator must have authority for the selected host, external model calls or cost, credentials, data exposure, repository writes, and cleanup before running. Use only approved task data and disposable state. The reference supplies a method, not an installer, benchmark runner, provider adapter, persistent result store, or permission grant.

A3's deliverable in this milestone is the guidance and its working Skill-local link, not a live experiment or a proven performance improvement. Keep local A1/A2 scenario examples in this design and plan as acceptance support; the reusable reference must remain useful without this repository, the Ponytail checkout, or stage artifacts.

## Non-goals and deferred work

- No new public Skills, frontmatter descriptions, routing cases, roles, permissions, or `semantic_requires` edges; preserve all 39 public IDs.
- No Ponytail persona, persistent intensity mode, automatic activation, subagent injection hook, statusline, user-settings integration, or shared mode flag.
- No runtime/controller, machine-readable evaluation contract, artifact validator, scheduler, mutable ledger, replay system, benchmark framework, fixture corpus, new dependency, or mandatory paid CI lane.
- No changes to `code-simplification`, `output-styles`, debt tracking, hook code, tests, generators, installer scripts, or plugin manifests.
- No shortest-diff mandate, unauthorized reduction of requested behavior, universal test-count limit, or claim that static checks prove agent adherence or measurable savings.
- A real cross-model or cross-host comparison, executable fixtures, evaluation runner, and measured benefit report are possible future work only under separately approved scope, execution authority, data handling, and budget. They are not unfinished tasks in this milestone.

## Alternatives and reasons

| Alternative | Decision and reason |
| --- | --- |
| Import Ponytail Skills and hooks as a new collection or integration | Reject: duplicates existing semantic owners and introduces host mechanics and state outside this repository's boundary |
| Add a new universal minimalism Skill or duplicate the ladder across workflow and policy Skills | Reject: fragments authority, expands discovery and dependencies, and adds instruction overhead without a new capability |
| Put the entire evaluation method in `testing-strategy/SKILL.md` | Reject: makes every testing invocation carry experiment guidance; use progressive disclosure instead |
| Implement a benchmark runner and freeze new policy sentences in tests | Reject: not needed for a semantic refinement; prose assertions do not prove consumer behavior and a runner is new implementation scope |
| Make no change because the general principles already exist | Reject for A1/A2's concrete inspection gaps and A3's instruction-contamination pitfall; retain existing boundaries rather than restating all existing policy |

## Acceptance evidence

The implementing agent owns acceptance and any repair. Independent reviewers return candidates only. These scenarios guide semantic source review; they are not automated prompt-behavior test results or a new persisted fixture format.

| ID | Scenario | Required interpretation |
| --- | --- | --- |
| S1 | A repository helper or native capability already satisfies the approved task | Look before writing; reuse an appropriate owned capability without creating an unnecessary alternative |
| S2 | A standard-library replacement conflicts with the supported platform or approved dependency convention, or a short custom authentication implementation looks cheaper | Requirements and lifecycle/security constraints win over ladder position; preserve the suitable maintained solution |
| S3 | Two callers fail because the same shared invariant is violated | Localize the shared root, repair within scope, and select focused regression evidence for affected paths |
| S4 | Callers intentionally have different validation or error contracts, or a relevant dynamic/public caller is unresolved | Do not hoist caller-specific policy or assume search silence means safety; preserve differing behavior and expose any blocking evidence gap |
| S5 | The control arm receives the candidate through a global plugin or a child-agent injection path | Do not label the comparison isolated or report causal gains from it; repair isolation only within approved authority or report invalid/uncertain evidence |
| S6 | The candidate produces fewer lines by dropping a required behavior, accessibility condition, validation guard, or useful regression test | Fail the owned acceptance requirement; cost or size savings do not compensate for missing behavior |
| S7 | Results contain failures, timeouts, small samples, or incomparable billing/token observations | Report the full attempt accounting, comparability limits, and uncertainty; do not invent universal safety or counterfactual savings |
| S8 | The task authorizes documentation improvements but no external model run, configuration mutation, or data upload | Produce and verify guidance only; absence of a live trial does not block this milestone and does not prove efficacy |

Structural acceptance additionally requires exactly the intended authored and generated content changes, a valid relative link to the new reference, self-contained root-flat Skills, unchanged public metadata and architecture, and passing repository-owned checks. Semantic acceptance requires A1-A3 and their exceptions to coexist with current scope, dependency, error, and testing policies without weakening them.

## Truth ownership and implementation surface

The durable truth owners are the three existing authored Skills and the new reference under `testing-strategy`. The exact proposed authored write set is:

- `src/skills/policies/development-standards/SKILL.md`
- `src/skills/workflows/implement-change/SKILL.md`
- `src/skills/disciplines/testing-strategy/SKILL.md`
- `src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md` (new)

Generate the matching four files under root-flat `skills/`; never edit the projection directly. Run all repository-prescribed generators, but expect no content change to `skills.index.json`, architecture diagrams, `.source-map.json`, metadata, or other Skills because inventory, descriptions, sources, and composition are unchanged. Any unexpected generated change requires diagnosis, not automatic inclusion.

No stable architecture or root README/AGENTS update is needed because the existing semantic-only ownership and maintenance boundaries remain true. Keep this design and its plan in `docs/plans/changes/`, outside default stable-truth search.

## Verification, recovery, and approval

Use semantic source review against S1-S8 as substitute evidence for instruction meaning, plus existing executable contract, reference, portability, generation-parity, Markdown, lint, type, and test checks for the actual maintenance boundaries. Do not add exact-sentence, heading, keyword-presence, or keyword-absence tests. This verification can establish the authored/distributed guidance change; it cannot establish improved model behavior, security, cost, or speed.

Use `fix_forward` for bounded prose, link, or generation defects. Preserve existing work, fix only the owning source, regenerate, and rerun affected checks. Stop for a design or authority decision if correctness requires a new runtime, metadata contract, benchmark execution, broader caller policy, external mutation, or another Skill owner. No history rewrite or guarded rollback is justified by this documentation-only change.

The user's request authorizes creation of these design and plan artifacts only. Mark the pair `ready_for_approval` after bounded review and any accepted repair; approval and implementation authority remain with the user.

## External evidence provenance

External inspiration is pinned to Ponytail revision `974d940a1c5344210874150b98ff0d2c861fab6a`. It is comparative source evidence, not an implementation dependency or an authority source for local behavior.

- [Capability ladder and caller-aware fix rationale](https://github.com/DietrichGebert/ponytail/blob/974d940a1c5344210874150b98ff0d2c861fab6a/skills/ponytail/SKILL.md#L32-L54).
- [Documented global-hook contamination of the baseline](https://github.com/DietrichGebert/ponytail/blob/974d940a1c5344210874150b98ff0d2c861fab6a/benchmarks/results/2026-06-18-agentic.md#L40-L47).
- [Agentic evaluation method and its limitations](https://github.com/DietrichGebert/ponytail/blob/974d940a1c5344210874150b98ff0d2c861fab6a/benchmarks/agentic/README.md).

The assessment read source and tests without installing or executing Ponytail. Published benefit numbers are not adopted as acceptance targets.
