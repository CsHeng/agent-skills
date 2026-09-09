---
name: executable-oracle-architecture-selector
description: "Choose or revise executable evidence when how to verify a change is unresolved. Select oracle methods and protected boundaries; not to run known checks or implement tests under an established strategy."
---

# Executable Oracle Architecture Selector

## Purpose

Choose or revise the executable feedback strategy when the evidence needed to verify a change is unresolved. An established contract, test strategy, or narrow reproducer may already answer that question; using TDD or running known checks alone does not require this selector.

Treat tests, contracts, properties, models, golden files, monitors, canaries, and synthetic probes as executable oracles: durable constraints that define what behavior must hold.

Core rule:

```text
intent / invariant -> executable oracle -> implementation -> observation -> oracle comparison -> regression guard
```

Do not rely on an agent's implicit understanding of the codebase as the maintenance boundary.

## Selection Questions

Answer these before choosing a method:

- What system boundary is being protected?
- Who owns the oracle?
- Is the behavior new, known, unstable, or legacy-current?
- Is the risk local, cross-service, stateful, security-sensitive, or production-only?
- Can the behavior be expressed as examples, contracts, properties, models, snapshots, or runtime SLOs?
- Is the agent allowed to change the oracle, or only the implementation?
- Does this change persist, migrate, or recover state, and does existing evidence still hold for the final candidate?
- Which user-visible outcome must hold, and would a parser, existence check, or golden file fail to prove it?

Common boundaries:

- business behavior
- public API or service boundary
- core domain logic
- state machine or protocol
- legacy behavior
- test-suite quality
- runtime resilience
- security or permission boundary

## Method Selector

| Controlled behavior | Preferred method | Oracle type | Avoid when |
|---|---|---|---|
| Single function or module correctness | TDD | Example oracle | Interface is still volatile or code is trivial glue |
| Business acceptance behavior | BDD / ATDD | Scenario oracle | Testing low-level internals |
| Complex domain rules | Specification by Example + TDD | Example table + tests | No domain owner or rules are exploratory |
| Service-to-service compatibility | Contract testing | Contract oracle | Private unstable internal calls |
| Public API or schema compatibility | Contract / schema conformance | Contract oracle | Prototype schema is intentionally unstable |
| Large input space | Property-based testing / fuzzing | Property oracle | Invariant or generator is weak |
| Stateful workflow or protocol | Model-based tests + TDD | Model oracle | Model costs more than the system warrants |
| Dependency-aware parallel execution | Model/state-transition tests + contract tests | DAG, conflict, binding, and convergence oracle | Only happy-path completion is observable |
| Legacy refactor safety | Characterization / golden / approval tests | Current-behavior oracle | Current behavior is known wrong and should change now |
| Test-suite strength | Mutation testing | Meta-oracle | Suite is slow, flaky, or low risk |
| Distributed resilience | Fault injection / chaos / synthetic probes | Runtime oracle | Recovery and blast-radius controls are weak |
| Production-only regression | Canary / monitoring / SLO alerts | Runtime oracle | Used as a substitute for pre-merge correctness |
| Security boundary | TDD + properties + fuzz/static analysis | Mixed oracle | Required assertions can be silently weakened |

## API Contract Decomposition

For a public multi-client API, select the executable oracle method here first. When contract/schema conformance is selected, use `api-contract-strategy` to decompose wire ownership, provider conformance, consumer adapters, workflow evidence, generation, and compatibility lifecycle.

This selector retains authority over oracle-method selection. `api-contract-strategy` does not rescore the method or own lifecycle execution.

## Phase Defaults

Choose from these methods when they protect the current boundary at proportionate cost. A phase or infrastructure label does not require every method below.

Exploration or prototype:

- use smoke tests, typecheck/lint, minimal happy-path acceptance tests, small golden samples, and minimal public interface contracts
- avoid broad brittle tests over unstable internals

Stabilizing core semantics:

- require a failing test, executable oracle, or narrow reproducer before implementation for non-trivial behavior changes when a correct seam exists
- focus on state transitions, permission decisions, error semantics, idempotency, compatibility, and persisted formats

Mature or agent-assisted maintenance:

- use TDD/component tests for local changes, BDD/ATDD for critical business workflows, contract/schema checks for boundaries, mutation testing on critical diffs, and canaries/SLO validation for production-only behavior
- do not delete or weaken required oracles to make implementation pass; bulk snapshot updates need readable justification

Legacy or unknown behavior:

- pin current behavior first with characterization, golden, or approval tests
- refactor in small steps
- replace low-semantic snapshots with higher-semantic tests when stable seams emerge

Infrastructure or platform systems:

- prefer contract/conformance tests, model/state-machine tests, fault injection, narrow local TDD, and runtime synthetic probes
- define the oracle before running live probes; a probe observes behavior, an oracle says whether it is acceptable

## Evidence Sufficiency And Delegation

Ordinary implementation needs the authorized objective and scope, allowed changes, protected behavior, and concrete acceptance evidence or a suitable substitute. These facts may already come from the bounded request, repository contracts, existing tests, or a reproducer; do not require a new plan or a work-package schema to restate them.

A missing perfect agent-runnable reproducer does not freeze unrelated authorized work. Use the best available before-state evidence and keep unblocked work moving; ask for access or instrumentation when that is the actual blocker.

When necessary evidence is missing or contradictory, name the actual unresolved oracle, contract, design, or authority decision and return it to the calling agent. Do not block local implementation or a TDD loop on delegation profiles, parallel policy, a maximum review budget, or a fixed hypothesis or test count.

Actual delegation additionally needs an accountable repository owner, bounded writes, safe isolation and shared-resource handling, completion evidence, and calling-agent convergence ownership. Let `plan-change` and `implement-change` consume those facts when delegating; profiles apply under their delegation-ready conditions, not as a local implementation gate. If safe delegation is unavailable, retain the work locally when the user's requirements and authority permit it; do not silently replace a required delegation method.

When the product being changed is itself an agent scheduler, model/state-transition and contract fixtures can protect dependency order, conflict exclusion, capacity, fallback behavior, and convergence. Test the actual owned scheduler interface and approved contract, not prose snapshots or provider names. An ordinary task using parallel assistance does not thereby require building a scheduler fixture.

## Change-Sensitive State Evidence

Scale persistence and recovery evidence to this change, the value of the affected state, the blast radius, and whether prior evidence still applies to the final candidate. A project stage label such as unreleased or non-commercial does not lower protection for unique or irreplaceable data. Follow applicable project requirements; do not skip them to save time.

Ordinary logic that does not touch persistence or recovery paths does not default to a full backup/restore drill. A new revision, repair, candidate digest, or template-only change does not by itself invalidate still-valid recovery evidence or require a restore drill. Necessary behavior checks still run.

When the change migrates retained state, select an oracle for upgrading representative pre-migration state, not only empty-store initialization; this does not require or authorize touching live data. When the change is backup/restore itself, restore behavior is the product behavior under test and needs corresponding evidence. Authorized disposable development state may prove recovery by rebuild or replace; do not force in-place upgrade for state that is approved to discard. Retained existing data still needs corresponding migration evidence.

Reuse still-valid prior evidence. Re-verify combinations, state transitions, or checks that later edits invalidated, including changed data formats, recovery implementations, or runtime recovery conditions. Refreshing a production backup is not by itself a reason to redo every recovery proof. Do not add a risk-scoring system, a fixed recovery-drill checklist, or a mandatory pre-work environment rehearsal. Do not measure oracle quality by test count, full matrix, or formality.

## Oracle Edit Judgment

Use the labels below to judge actual risk. They do not schedule a review round or a full matrix.

| Diff type | Concern to assess |
|---|---|
| implementation diff | Changed behavior and affected callers |
| test addition | Independent expected results and realistic fixtures |
| test deletion or assertion weakening | Loss of required coverage versus authorized retirement or adaptation |
| snapshot/golden update | Independent evidence for the new expected behavior |
| contract/model or business scenario change | Changed user commitments, compatibility, and state transitions |
| security oracle change | Actual exposure, exploitability, expected damage, and control cost |

Treat these as likely required-oracle weakening unless an independent contract authorizes the adaptation:

- exact assertion changed to existence-only assertion
- specific error changed to any error
- exact status changed to broad range
- exact permission set changed to partial containment
- schema version relaxed without compatibility rationale
- negative or boundary tests removed
- snapshots bulk-updated without readable diff review
- sleeps or retries added to hide flakiness
- integration behavior mocked away to make CI pass

Authorized secondary-capability tradeoffs are recorded adapted results with evidence. They do not justify deleting or relaxing a main-goal or hard-boundary oracle to make implementation pass. Parser, existence, or golden checks do not replace user-goal scenarios.

## Output Contract

Follow `output-styles` and preserve these semantic results:

- recommended oracle strategy and method mix
- protected boundary, behavior status, risk, and oracle owner
- selected methods, purpose, oracle level, and material discard reasons
- implementation order and concrete validation evidence
- oracle edits whose actual risk needs calling-agent judgment
- likely failure modes when they affect the decision

When this skill owns the response, lead with the decision and render only the fields needed to justify or execute it. When design, planning, review, or implementation owns the response, contribute these results as a semantic overlay instead of emitting an independent oracle report.

Keep the answer concrete. Avoid generic coverage advice and empty template sections.
