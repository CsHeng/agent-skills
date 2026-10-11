# Oracle Selection

## Purpose

Choose or revise the executable feedback strategy when the evidence needed to verify a change is unresolved. An established contract, test strategy, or narrow reproducer may already answer that question; using TDD or running known checks alone does not require this reference.

Treat tests, contracts, properties, models, golden files, monitors, canaries, and synthetic probes as ways to observe the user's required outcomes and actual consumer contracts. Their presence does not independently establish what behavior must be preserved.

Documents and diagrams express intent or explain the implementation; code and observed runtime behavior establish what is implemented. Preserve explicit user requirements and synchronize explanatory material after changes, but select product oracles against the executable boundary rather than document wording, diagram content, or layout. Existing link, structure, and generator checks verify their own tooling boundary and do not prove the product works.

Core rule:

```text
intent / invariant -> executable oracle -> implementation -> observation -> oracle comparison -> regression guard
```

Do not rely on an agent's implicit understanding of the codebase as the maintenance boundary.

## Selection Questions

Use the questions that can change the current choice; do not fill a questionnaire when an existing check already supplies adequate evidence:

- What user outcome or actual consumer requirement makes this boundary worth protecting?
- Who owns the oracle?
- Is the behavior new, known, unstable, or legacy-current?
- Is the risk local, cross-service, stateful, security-sensitive, or production-only?
- Can the behavior be expressed as examples, contracts, properties, models, snapshots, or runtime SLOs?
- Is the agent allowed to change the oracle, or only the implementation?
- Does this change persist, migrate, or recover state, and does existing evidence still hold for the final candidate?
- Which user-visible outcome must hold, and would a parser, existence check, or golden file fail to prove it?
- Is an exact value or compatibility behavior required by a real consumer, protocol, cryptographic boundary, or explicit user constraint, or merely inherited from the current implementation or its tests?

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

Start with the cheapest relevant example, existing check, or real scenario that can expose the required failure. The methods below are alternatives or targeted additions, not bundles implied by a domain label. Add a model, property generator, fault-injection system, or new framework only when simpler evidence misses an important behavior and the extra setup and maintenance are worthwhile.

| Controlled behavior | Preferred method | Oracle type | Avoid when |
|---|---|---|---|
| Single function or module correctness | TDD | Example oracle | Interface is still volatile or code is trivial glue |
| Business acceptance behavior | BDD / ATDD | Scenario oracle | Testing low-level internals |
| Complex domain rules | Specification by Example + TDD | Example table + tests | No domain owner or rules are exploratory |
| Service-to-service compatibility | Contract testing | Contract oracle | Private unstable internal calls |
| Public API or schema compatibility | Contract / schema conformance | Contract oracle | Prototype schema is intentionally unstable |
| Large input space | Property-based testing / fuzzing | Property oracle | Invariant or generator is weak |
| Stateful workflow or protocol | Focused transition scenarios; model-based tests when combinations warrant them | Scenario or model oracle | A separate model adds no useful coverage over direct examples |
| Dependency-aware parallel execution | Targeted ordering, cancellation, conflict, or convergence scenarios; add a model only for uncovered combinations | Scenario, contract, or model oracle | A green happy path would be presented as proof of untested failure semantics |
| Legacy refactor safety | Characterization of consumer-relevant behavior | Current-behavior evidence | It would freeze known bugs or incidental implementation/library behavior as requirements |
| Test-suite strength | Mutation testing | Meta-oracle | Suite is slow, flaky, or low risk |
| Distributed resilience | Targeted dependency-failure checks; live fault injection or probes only for runtime-only claims | Scenario or runtime oracle | The claim can be tested more cheaply below, or live blast-radius controls are inadequate |
| Production-only regression | Canary / monitoring / SLO alerts | Runtime oracle | Used as a substitute for pre-merge correctness |
| Security boundary | Focused allowed/denied cases; add properties, fuzzing, or static analysis for the specific exposure | Example, property, or mixed oracle | Tooling adds no relevant protection or required assertions can be silently weakened |

## API Contract Decomposition

Select an executable oracle method here only when the evidence strategy is genuinely unresolved. An existing OpenAPI or conformance setup already establishes the method: consume it directly, and use `api-contract-strategy` to decide wire ownership, provider conformance, consumer adapters, workflow evidence, generation, and compatibility — including generated types versus SDK or adapter choices, which do not need a fresh selection pass.

When selection does happen here, this method supplies the oracle choice. `api-contract-strategy` does not rescore the method or own lifecycle execution.

## Feedback And Placement

For uncertain business behavior, prefer a thin real path and a relevant example over a complete assurance framework. An exploratory slice proves only what it exercises; complete required acceptance before delivery. For established behavior, consume current tests and add the focused missing scenario. For legacy changes, characterize consumer-relevant behavior without freezing incidental internals or historical bugs.

Choose an environment for the claim, not for a project label: a local deterministic scenario may prove a scheduler's cancellation rule; real deployment evidence is needed for behavior that depends on deployed conditions. Define what a live observation would establish before running it, and respect its actual authority and blast radius. Neither the word infrastructure nor the availability of fault injection schedules a production exercise.

Put a check before the operation whose risk or uncertainty it resolves. A required delivery check need not block starting independent local implementation. Repair only setup that the next useful check needs; reuse the project's existing tools instead of first building a generic fixture, probe, or result-recording platform. Protect actual retained-state transitions and required negative behavior throughout.

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

Reuse still-valid prior evidence. Re-verify combinations, state transitions, or checks that later edits invalidated, including changed data formats, recovery implementations, or runtime recovery conditions. Ordinary local results do not need source or test-file hashes, a receipt chain, or mandatory revision bookkeeping to establish applicability. Artifact integrity and exact-version reproduction remain appropriate when the protected behavior actually needs them. Refreshing a production backup is not by itself a reason to redo every recovery proof. Do not add a risk-scoring system, a fixed recovery-drill checklist, or a mandatory pre-work environment rehearsal. Do not measure oracle quality by test count, full matrix, or formality.

## Oracle Edit Judgment

Use the labels below to judge actual risk. They do not schedule a review round or a full matrix.

| Diff type | Concern to assess |
|---|---|
| implementation diff | Changed behavior and affected callers |
| test addition | Requirement or consumer basis, independent expected results, realistic fixtures, and maintenance cost |
| test deletion or assertion weakening | Loss of required coverage versus removal of an unsupported constraint, redundancy, or authorized adaptation |
| snapshot/golden update | Independent evidence for the new expected behavior |
| contract/model or business scenario change | Changed user commitments, compatibility, and state transitions |
| security oracle change | Actual exposure, exploitability, expected damage, and control cost |

First establish what requirement the assertion protects. Within authorized edits, an agent may remove its own unsupported tests, compatibility promises, or guards without treating them as immutable acceptance. An existing test or model-written plan is not enough to justify freezing code shape, document wording/layout, incidental library behavior, or fixture bytes. Preserve explicitly fixed requirements and actual consumer contracts.

Where the assertion does protect such a requirement, assess these changes for lost protection:

- exact assertion changed to existence-only assertion
- specific error changed to any error
- exact status changed to broad range
- exact permission set changed to partial containment
- schema version relaxed without compatibility rationale
- negative or boundary tests removed without equivalent protection for the required behavior
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

When oracle selection is the requested task, lead with the decision and render only the fields needed to justify or execute it. When design, planning, review, or implementation owns the response, contribute these results as a semantic overlay instead of emitting an independent oracle report.

Keep the answer concrete. Avoid generic coverage advice and empty template sections.
