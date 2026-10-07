# Test Layering And Suite Audit

## Purpose

Use this reference to classify an existing mixed test suite, decide whether a large or duplicated check is justified, and produce remediation guidance without treating test count or file length as quality. Keep the scope and deliverable selected by the calling task; using this method does not itself request a complete audit or a separate report.

The core chain is:

```text
protected boundary -> independent oracle -> real dependency and authority -> primary evidence class -> execution lane -> diagnosis owner
```

The result is not a universal pyramid. Contract, compatibility, security, performance, and runtime evidence answer different questions and do not form one mandatory linear stack.

## Contents

- [Classification Coordinates](#classification-coordinates)
- [Primary Evidence Classes](#primary-evidence-classes)
- [Smallest-Sufficient-Layer Rule](#smallest-sufficient-layer-rule)
- [Oracle Independence](#oracle-independence)
- [Suite Cohesion And Size](#suite-cohesion-and-size)
- [Subprocess Environment Isolation](#subprocess-environment-isolation)
- [Infrastructure Examples](#infrastructure-examples)
- [Audit Procedure](#audit-procedure)
- [Dispositions](#dispositions)
- [Audit Output](#audit-output)

## Classification Coordinates

Use these independent fields where needed to explain a suite's classification:

| Field | Question | Typical values |
| --- | --- | --- |
| Protected boundary | What observable invariant must remain true? | Function rule, rendered artifact, public schema, provider behavior, workflow outcome, user journey, deployed SLO |
| Primary evidence class | What is the highest real boundary this check exercises? | Static/documentation/generated, unit, component, integration, contract/conformance, workflow/system, UI/E2E, runtime |
| Dependency and authority scope | What real dependency or environment is required? | In-process, isolated local, cross-repository, deployed non-production, production-authorized |
| Oracle type and source | What independently says the result is correct? | Example, table, property, schema, compatibility base, scenario, model, reviewed golden, runtime objective |
| Execution lane | When is this evidence economical and authorized? | Fast, merge, release, runtime |
| Cross-cutting tags | Which quality attribute changes the setup or review risk? | Compatibility, security, performance, resilience, migration |
| Owner | Which suite owns diagnosis and who repairs failure? | Module, component, provider, consumer, workflow, platform, operations |

A check has one primary evidence class and one primary diagnosis owner. Add cross-cutting tags instead of inventing compound labels such as “security-performance-integration-E2E test.”

## Primary Evidence Classes

| Evidence class | Boundary actually exercised | Common oracle |
| --- | --- | --- |
| Static, documentation, or generated | Source form, structured metadata, links, schema, compilation, or source/generated projection | Parser, linter, schema, compiler, link checker, deterministic regeneration |
| Unit | One function, module, or rule in one process without meaningful real I/O | Examples, tables, properties |
| Component | One owned component through its public seam with outside dependencies replaced or isolated | Examples, component scenarios, embedded fixtures |
| Integration | Collaboration with a real database, process, service, provider SDK, filesystem boundary, or system tool | Real request/response, persisted state, process output |
| Contract or conformance | A producer-consumer, wire, persisted-format, generated-artifact, or cross-repository compatibility boundary | Schema, compatibility comparison, provider conformance, consumer adapter fixture |
| Workflow or system | A multi-operation business or control-plane sequence across components | Scenario, state transition, historical regression |
| UI or E2E | User-visible behavior that depends on the real browser, device, or application shell | Narrow user journey |
| Runtime | Behavior observable only after deployment or under production-authorized conditions | Synthetic probe, canary, SLO, runtime invariant |

Choose from the boundary actually exercised. A mocked HTTP client does not make a unit check an integration test, and invoking `pytest` does not make a cross-repository schema check a unit test. Contract evidence is not automatically more expensive than component evidence, and runtime evidence does not replace pre-merge correctness.

Performance, security, resilience, compatibility, and migration usually modify an evidence class rather than replace it. A property test over an authorization function may be a security-tagged unit test; a load scenario against a deployed service may be a performance-tagged runtime check.

## Smallest-Sufficient-Layer Rule

Start by naming the critical consumer outcome and credible ways it can fail. Then use the lowest realistic boundary that can prove each invariant, not the lowest boundary that can produce a green assertion. Keep a small set of risk-representative cross-boundary scenarios for the outcome itself; a trivial happy path chosen only for ease of passing is not sufficient evidence.

Promote or add evidence only when the higher boundary contributes information unavailable below:

- real serialization, protocol, or provider semantics
- persistence, transaction, filesystem, or process behavior
- producer-consumer compatibility
- multi-operation state transitions
- browser, device, kernel, network, scheduler, or controller behavior
- deployed configuration, traffic, recovery, or SLO conditions

Do not duplicate the same expectation at every layer. Let lower-boundary checks protect detailed rules and let higher-boundary checks assert the smallest cross-boundary outcome. Do not mock away the boundary named by the test.

## Oracle Independence

An oracle should be simpler, differently owned, or independently derived from the implementation.

Strong sources include:

- hand-selected domain examples whose expected result is obvious
- a schema, protocol, external standard, or compatibility base
- a property or model that is simpler than the implementation
- a consumer-owned adapter fixture or provider-owned conformance response
- a real consumer, compiler, parser, controller, or system tool
- a reviewed golden artifact when exact output is itself an external protocol, consumer contract, or explicit user requirement
- an explicitly approved runtime objective

Weak or tautological patterns include:

- deriving expected output with the same function or transformation being tested
- reproducing the source algorithm in test code
- asserting every manifest field by restating the manifest without a separately owned contract
- rendering and validating through the same untrusted helper while checking only existence
- snapshotting natural-language sentences, headings, keyword collections, or dependency versions copied from documentation
- freezing source layout, diagram content, fixture hashes, or incidental library behavior without a consumer requirement
- accepting any error, broad status range, or non-empty output when exact behavior matters

Use `replace` when the protected invariant is valuable but the current oracle is not independent. Use `delete` when no requirement supports the assertion or another owned oracle already proves the behavior at equal or stronger fidelity. A historical test or model-written plan does not turn an incidental implementation choice into required compatibility. Ordinary local evidence needs no separate source, fixture, or result hash to certify itself.

## Suite Cohesion And Size

There is no universal maximum file length, test length, test count, assertion count, or fixture size.

Large suites can be reasonable when they contain one cohesive rule matrix, parser or protocol corpus, one component boundary, or reviewed golden cases with localized failures. Long data is often clearer as a table or fixture than as many nearly identical functions. Assess whether each corpus distinction protects real behavior and whether setup or expected output is duplicated: several input encodings can share one expected output, and launcher tests can share a small helper when they exercise the same lifecycle. Avoid a new framework whose maintenance costs more than the duplication it removes.

Consider `split` when one file or test mixes any of:

- unrelated protected boundaries or business capabilities
- different repository, provider, consumer, or diagnosis owners
- cheap static checks with live or credentialed evidence
- fast, merge, release, and runtime lanes
- incompatible fixtures, setup lifecycles, or authority scopes
- several independent actions whose failures cannot be localized
- source-text policy snapshots beside executable behavior checks
- broad shared setup that turns one defect into many cascading failures

Length is a prompt to inspect cohesion, not a disposition. A 1,400-line focused CLI or parser suite may be healthier than a 200-line test that repeats implementation logic or mixes three owners.

For a single long test, prefer a readable scenario or table over an arbitrary one-assert rule. Split when it contains independent behaviors or diagnosis paths, not merely because it has many assertions.

## Subprocess Environment Isolation

Build subprocess environments from an empty mapping and add only the variables required by the scenario. Typical non-secret inputs include an explicit executable search path, a stable locale, a temporary home or cache, and the test-owned contract paths.

```python
env = {
    "PATH": os.environ["PATH"],
    "HOME": str(temp_home),
    "LC_ALL": "C",
    "APP_CONFIG": str(test_config),
}
subprocess.run(command, env=env, check=True)
```

Do not copy the complete developer or CI environment into a child process merely for convenience. Ambient credentials, agent sockets, cloud profiles, proxy settings, and unrelated feature flags can change behavior or appear in diagnostics.

Full environment inheritance is justified only when ambient-environment handling is the protected boundary. In that case:

- name the exception in the test
- remove sensitive and unrelated variables before launch
- use synthetic credential values when a credential-shaped input is required
- redact command output, exceptions, and captured artifacts
- prove cleanup and absence of unexpected inherited state

## Infrastructure Examples

### Terraform And Provider Graphs

Prefer formatting and validation, provider schemas, plan JSON invariants, address and migration contracts, and narrowly authorized provider integration. Avoid protecting behavior by matching arbitrary `.tf` prose or repeating the entire resource graph in Python assertions.

### Kubernetes And Generated Manifests

Prefer schema validation, deterministic rendering, policy or contract checks, real consumer parsing, and server-side dry-run when authority exists. Assert meaningful ownership, security, storage, identity, and rollout invariants rather than copying every YAML field into tests.

### Ansible, Shell, And Operations Wrappers

Use syntax checks, structured task parsing where syntax is the contract, isolated subprocess scenarios, fake tools outside the owned boundary, and narrowly authorized live acceptance. Do not freeze natural-language task names or inherit the full operator environment.

### Documentation And Skills

Code and observed runtime behavior establish implementation truth; documents and diagrams convey intent and explanation and should be synchronized after changes. Use applicable link, syntax, build, or generator checks for their tooling boundaries. Do not test document wording, headings, diagram nodes/edges, or preferred layout as production contracts, including when an LLM reads them. Test executable examples and real machine-consumed structured fields through the actual interface; do not invent such a field just to enforce an unnecessary documentation rule.

### Cross-Repository Contracts

Keep the canonical contract oracle with its owner and keep consumer assumptions with each consumer. A cross-repository check may verify reachability or compatibility, but it should not become one god suite that restates every repository's internal desired state and obscures diagnosis ownership.

## Audit Procedure

1. Establish whether the task needs a focused assessment or a complete audit of a named scope. Inspect the commands, tests, fixtures, generators, comparison bases, and runtime probes relevant to that scope and the decisions it needs.
2. Group checks with the same protected behavior and assessment. Examine individual tests when their recommendations, boundaries, lanes, or owners differ; a row per discovered entry point is not required.
3. Establish the user or consumer requirement behind the asserted invariant; do not assume the current test or a model-written plan makes it necessary.
4. Trace how expected results are derived and whether the oracle is independent.
5. Identify the real dependencies, authority, fixture lifecycle, lane, and diagnosis owner.
6. Apply the smallest-sufficient-layer rule and choose one primary disposition.
7. Record producer, consumer, shared-contract, write-set, and external dependencies separately from shared motivation.
8. Where a required behavior remains, verify its replacement or retained coverage before removing its old oracle. An unsupported constraint can be deleted without inventing a replacement test for it.

Sampling may support a focused recommendation, but it cannot support a claim that all tests were audited. For a requested complete audit, account for every entry point in the declared scope, grouped where the same assessment applies. An incomplete investigation remains explicitly partial; incidental discovery outside that scope does not enlarge it.

## Dispositions

| Disposition | Use when | Required evidence |
| --- | --- | --- |
| `keep` | The check protects a meaningful boundary with an independent oracle, fitting fixture, lane, and owner | Protected invariant and why the existing evidence is sufficient |
| `refactor` | The boundary and oracle are sound, but setup, naming, duplication, isolation, or readability impairs diagnosis | Smallest structural change that preserves the oracle |
| `replace` | The invariant matters, but the oracle is tautological, too weak, or at the wrong boundary | Replacement oracle and proof it covers the intended failure class |
| `delete` | No requirement supports the assertion, the check freezes prose or implementation detail, or an equal/stronger owner already proves it | Unsupported constraint or redundancy, with any actual required behavior still protected |
| `split` | One suite mixes boundaries, owners, fixtures, authority scopes, lanes, or independent failure domains | Proposed owning suites and the invariant transferred to each |
| `move-lane` | The evidence is sound but runs with the wrong cost, comparison base, environment, authority, or promotion effect | Target lane and its entry, authority, and failure-owner contract |

Choose a primary recommendation for each assessed suite or coherent group. Explain distinct outcomes of a split when they affect the decision.

## Audit Output

Follow the calling skill's deliverable and `output-styles`. For a standalone audit, lead with the supported recommendations, the suites or groups they concern, the behavior to preserve, and the evidence and limits behind the judgment. Include replacement coverage, placement, ownership, or coordination when the recommendation changes them. A table can help compare several suites; it is optional, and its columns follow the decision rather than a fixed field list.

When this analysis supports a design or plan, place the relevant conclusions there without an additional audit report. Distinguish facts, inferences, and unresolved evidence in whichever form is useful. A separate plan, approval, or coordination record follows the user's request and project policy, not this reference. State real producer-consumer and overlapping-write dependencies when they matter; common motivation or another plan's existence is not itself a dependency or a reason for a formal freeze.
