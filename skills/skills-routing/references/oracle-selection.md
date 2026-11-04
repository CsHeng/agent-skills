# Oracle Selection

Read this when the executable evidence needed to verify a change is unresolved. An established contract, test strategy, or narrow reproducer already answers that question; running known checks or using TDD needs no selection pass.

Tests, contracts, properties, models, golden files, monitors, canaries, and synthetic probes are ways to observe the user's required outcomes and actual consumer contracts; their presence does not by itself establish what behavior must be preserved. Select product oracles against the executable boundary rather than document wording or diagram content (`development-standards` owns that distinction), and keep link, structure, and generator checks as evidence about their own tooling.

```text
intent / invariant -> executable oracle -> implementation -> observation -> oracle comparison -> regression guard
```

## Selection Questions

Use the questions that can change the current choice:

- What user outcome or actual consumer requirement makes this boundary worth protecting, and who owns the oracle?
- Is the behavior new, known, unstable, or legacy-current, and is the risk local, cross-service, stateful, security-sensitive, or production-only?
- Can the behavior be expressed as examples, contracts, properties, models, snapshots, or runtime SLOs?
- May the agent change the oracle, or only the implementation?
- Does the change persist, migrate, or recover state, and does existing evidence still hold for the final candidate?
- Is an exact value or compatibility behavior required by a real consumer, protocol, cryptographic boundary, or explicit user constraint, or merely inherited from the current implementation or its tests?

## Method Selector

Start with the cheapest relevant example, existing check, or real scenario that can expose the required failure. The methods below are alternatives or targeted additions; a model, property generator, fault-injection system, or new framework earns its place when simpler evidence misses an important behavior and the setup and maintenance are worthwhile.

| Controlled behavior | Preferred method | Oracle type | Weak fit when |
|---|---|---|---|
| Single function or module correctness | TDD | Example oracle | Interface is still volatile or code is trivial glue |
| Business acceptance behavior | BDD / ATDD | Scenario oracle | Testing low-level internals |
| Complex domain rules | Specification by Example + TDD | Example table + tests | No domain owner or rules are exploratory |
| Service-to-service compatibility | Contract testing | Contract oracle | Private unstable internal calls |
| Public API or schema compatibility | Contract / schema conformance | Contract oracle | Prototype schema is intentionally unstable |
| Large input space | Property-based testing / fuzzing | Property oracle | Invariant or generator is weak |
| Stateful workflow or protocol | Focused transition scenarios; model-based tests when combinations warrant them | Scenario or model oracle | A separate model adds no coverage over direct examples |
| Dependency-aware parallel execution | Targeted ordering, cancellation, conflict, or convergence scenarios | Scenario, contract, or model oracle | A green happy path would stand in for untested failure semantics |
| Legacy refactor safety | Characterization of consumer-relevant behavior | Current-behavior evidence | It would freeze known bugs or incidental library behavior |
| Test-suite strength | Mutation testing | Meta-oracle | Suite is slow, flaky, or low risk |
| Distributed resilience | Targeted dependency-failure checks; live fault injection only for runtime-only claims | Scenario or runtime oracle | The claim is testable more cheaply below, or blast-radius controls are inadequate |
| Production-only regression | Canary / monitoring / SLO alerts | Runtime oracle | Used instead of pre-merge correctness |
| Security boundary | Focused allowed/denied cases; properties, fuzzing, or static analysis for the specific exposure | Example, property, or mixed oracle | Tooling adds no relevant protection |

An existing OpenAPI or conformance setup already establishes the method; `api-contract-strategy` owns wire ownership, provider conformance, consumer adapters, generation, and compatibility.

## Feedback And Placement

For uncertain business behavior, prefer a thin real path and a relevant example over a complete assurance framework; an exploratory slice proves what it exercises, and required acceptance completes before delivery. For established behavior, consume current tests and add the focused missing scenario. For legacy changes, characterize consumer-relevant behavior.

Choose the environment for the claim: a local deterministic scenario may prove a scheduler's cancellation rule, while behavior that depends on deployed conditions needs deployment evidence. Define what a live observation would establish before running it and respect its authority and blast radius. Put a check before the operation whose risk it resolves; a required delivery check does not block independent local implementation. Repair only the setup the next useful check needs, reusing the project's existing tools.

When necessary evidence is missing or contradictory, name the unresolved oracle, contract, design, or authority decision and return it to the calling agent; a missing perfect reproducer leaves independent authorized work running on the best available before-state evidence.

## Change-Sensitive State Evidence

This section owns retained-state and recovery evidence reuse. Scale persistence and recovery evidence to this change, the value of the affected state, the blast radius, and whether prior evidence still applies to the final candidate; a stage label such as unreleased does not lower protection for unique or irreplaceable data.

- Ordinary logic that leaves persistence and recovery paths untouched needs its behavior checks, not a backup/restore drill.
- A new revision, repair, candidate digest, or template-only change leaves still-valid recovery evidence valid.
- A change that migrates retained state needs an oracle for upgrading representative pre-migration state, not only empty-store initialization, without touching live data.
- When backup/restore is itself the change, restore behavior is the product behavior under test.
- Authorized disposable development state may prove recovery by rebuild or replace; retained existing data still needs migration evidence.
- Re-verify the combinations, state transitions, or checks that later edits invalidated: changed data formats, recovery implementations, or runtime recovery conditions. Applicability is judged from the behavior, inputs, and conditions covered, without hashes or revision bookkeeping, and artifact integrity or exact-version reproduction applies where the protected behavior needs it.

## Oracle Edit Judgment

| Diff type | Concern to assess |
|---|---|
| implementation diff | Changed behavior and affected callers |
| test addition | Requirement or consumer basis, independent expected results, realistic fixtures, maintenance cost |
| test deletion or assertion weakening | Loss of required coverage versus removal of an unsupported constraint, redundancy, or authorized adaptation |
| snapshot or golden update | Independent evidence for the new expected behavior |
| contract, model, or business scenario change | Changed user commitments, compatibility, and state transitions |
| security oracle change | Actual exposure, exploitability, expected damage, control cost |

Establish first what requirement the assertion protects. Within authorized edits an agent may remove its own unsupported tests, compatibility promises, or guards; an existing test or model-written plan does not freeze code shape, document wording, incidental library behavior, or fixture bytes. Where the assertion protects a real requirement, assess these edits for lost protection: exact assertion to existence-only, specific error to any error, exact status to broad range, exact permission set to partial containment, schema version relaxed without compatibility rationale, negative or boundary tests removed without equivalent protection, snapshots bulk-updated without readable diff review, sleeps or retries added to hide flakiness, integration behavior mocked away to make CI pass. Authorized secondary-capability tradeoffs are recorded adapted results; a main-goal or hard-boundary oracle keeps its strength.

## Output

Lead with the recommended oracle strategy: protected boundary, behavior status, risk, oracle owner, selected methods with purpose and level, implementation order, concrete validation evidence, and oracle edits that need the calling agent's judgment. When design, planning, review, or implementation owns the response, contribute these as an overlay under `output-styles`.
