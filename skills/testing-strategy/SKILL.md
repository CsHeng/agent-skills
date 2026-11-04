---
name: testing-strategy
description: "Design or revise verification coverage, suite placement, fixtures, isolation, and execution lanes for an established oracle. Use for test-strategy decisions or suite audits; not merely to run existing checks or add routine tests under a settled strategy."
---

# Testing Strategy

## Purpose

Turn a selected executable oracle into the smallest concrete verification set that protects the user's intended outcome and actual consumer requirements. Existing tests and implementation behavior are evidence to assess, not requirements by themselves.

When supporting design, planning, simplification, implementation, or review, contribute only the testing decisions and evidence that task needs.

Read `references/oracle-selection.md` in `skills-routing` when the oracle method or protected behavior still needs a decision. Under an established strategy, run known checks and add routine regression tests directly. For multi-client API contract ownership and layer decomposition, use `api-contract-strategy`.

Size verification by the protected boundary and its failure modes; add a numeric gate only under the conditions in the Coverage section of `references/ci-config.md`.

## Strategy Mapping

When selecting or auditing a strategy, use the relationships below to identify the decisions that matter, and explain the relevant choices in the owning deliverable:

```text
boundary -> oracle -> fixture/environment -> owning suite -> CI/release lane -> diagnosis owner
```

1. Name the user outcome or consumer behavior being protected and its owner.
2. Carry forward the selected executable oracle and record the failure class it detects.
3. Choose the smallest realistic fixture and environment.
4. Place the check in the suite that owns diagnosis.
5. Assign fast, merge, release, or runtime execution.
6. Define what a failure means and who repairs it.

Add a missing verification layer at the lowest boundary that can observe the failure.

Start acceptance from the critical consumer outcome and plausible failure modes, then choose the smallest real boundary that can prove each invariant. Keep a few risk-representative cross-boundary scenarios for behavior that isolated tests cannot see; use focused unit or integration checks for detailed logic and diagnosis. A passing scenario with expected results invented from the same implementation is a weak oracle. User-experience goals need corresponding scenarios, such as independent selection across business groups or a first-run initialization source; parser, existence, or golden checks cover other properties.

## Classification

When classifying or auditing existing checks, read [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md) for classification coordinates, evidence classes, the smallest-sufficient-layer rule, suite cohesion, dispositions, and the audit procedure.

Choose the primary evidence class from the highest real boundary the check exercises, and treat evidence class and execution lane as separate decisions. Add higher-boundary evidence when it proves behavior unavailable below, such as real serialization, persistence, provider interaction, a multi-operation workflow, UI behavior, or deployed conditions.

For API systems, keep schema compatibility and semantic compatibility separate: structural diffing cannot prove units, retry behavior, consistency, migration semantics, or status meaning.

## Red-Green Verification

- For behavior changes and bug fixes, identify the failing consumer outcome and an independent expected result, then write or identify a failing test or narrow reproducer before implementation when a correct seam exists. A post-change regression test is useful when it closes a real behavior gap.
- Confirm the oracle fails for the expected reason, not a typo or environment error.
- Implement the smallest change that makes the reproducer pass.
- Rerun the affected oracle after the repair and retain results that still cover unchanged behavior, inputs, and conditions.
- For config-only changes, use parser, schema, or real-consumer validation.
- For docs-only, generated, or exploratory changes, record the fitting lint, build, generation check, or manual evidence.
- When the user asks for TDD, test-first work, red-green-refactor, or vertical slices, read [TDD Vertical Slices](references/tdd-vertical-slices.md).

The main agent owns one verification strategy for the whole change; apply `development-standards` (Verification And Review) for timing, worker results, failure classification, and sufficiency.

## Documentation And Markdown Verification

When the change or audit touches Markdown, prompt or instruction files, or generated documentation, read [Documentation Verification](references/documentation-verification.md). Verify documentation through its real consumer: linter, link or build check, executable example, or schema check of a machine-read field.

When efficacy measurement is requested or a bounded risk judgment justifies it, use [Agent Skill Evaluation](references/agent-skill-evaluation.md) with the necessary execution authority and budget. For offline review of goal, risk, and discretion behavior, read [Goal And Risk Cases](references/goal-and-risk-cases.md).

## State, Recovery, And Proportionate Safeguards

When evidence for change-sensitive state is unresolved (retained-state migration, backup/restore behavior, rebuild-versus-replace for authorized disposable state, reuse of earlier evidence), read `references/oracle-selection.md` in `skills-routing`.

Tie each new hash, restore proof, replay mechanism, deployment rehearsal, or test gate to the affected behavior and a concrete failure mode, and use existing project evidence when sufficient (`development-standards`, Evidence Without Extra Machinery). Keep checksums, signatures, or exact bytes where a real artifact, protocol, cryptographic operation, or explicit user requirement depends on them.

Review the suite and instructions the bounded change touches.

## Oracle Integrity

- Protect the underlying requirement, not the existence of a test. Within authorized edits, remove or replace tests and agent-added guards that have no requirement or consumer basis, including incidental library behavior and arbitrary source or fixture bytes; an existing test, a passing review, or a model-written plan does not establish that basis. Exact wire bytes, cryptographic vectors, and explicitly required output remain valid oracles where they carry the contract. Revise an earlier model-declared test plan when the required outcome stays protected.
- Keep an oracle that protects a real requirement and make the implementation satisfy it (`implement-change`, Acceptance Integrity); removing a self-imposed constraint while preserving required behavior is a correction.
- Record the oracle type for non-trivial changes: example, scenario, contract, property, model, current-behavior snapshot, meta-oracle, or runtime oracle.
- Judge test additions and removals by the protection gained or lost and their maintenance cost.
- Make failures deterministic with readiness probes and exact assertions.
- Preserve exact negative and boundary behavior where it carries domain meaning.

## Fixtures And Environments

- Use deterministic fixtures with explicit setup and cleanup, and keep each test independent without shared mutable state.
- Reuse a fixture, expected output, or small helper when cases share the same meaning; keep case-specific semantics separate.
- Exercise the real owned boundary; mock only dependencies outside it.
- For ordinary trusted repository checks, reuse the project's working toolchain and test environment, and isolate or override databases, ports, caches, temporary files, and environment variables where concurrency, contamination, determinism, or protected-state exposure requires it.
- When untrusted execution, credential exposure, an environment-sensitive contract, or a hermetic-test policy applies, use a clean environment with an explicit allowlist (see Subprocess Environment Isolation in the layering reference and Deterministic Environment in `references/ci-config.md`).
- Keep unauthorized credentials and protected services out of test reach, and redact sensitive failure output.
- Use live credentials, production state, or hardware only when the user request or an approved plan covers them; default to local fixtures.

## Test Design

When writing new tests, read [Test Design](references/test-design.md).

## CI And Release Placement

When assigning lanes, read [Capability-Based CI](references/ci-config.md).

## Output Contract

When this skill owns the response, lead with the recommended testing decision and its basis. Include the protected behavior, oracle, placement, environment, commands, ownership, failure modes, and coordination where they affect that decision. Choose prose, a list, table, or diagram for clarity.

For an audit, state the scope actually examined and give supported recommendations to keep, refactor, replace, delete, split, or move checks to another lane. A requested complete audit accounts for every entry point in that scope; a focused assessment reports representative findings and their limits.

## References

- [Test Layering And Suite Audit](references/test-layering-and-suite-audit.md)
- [Documentation Verification](references/documentation-verification.md)
- [Test Design](references/test-design.md)
- [Python Testing Examples](references/examples-python.md)
- [Go Testing Examples](references/examples-go.md)
- [Capability-Based CI](references/ci-config.md)
- [TDD Vertical Slices](references/tdd-vertical-slices.md)
- [Agent Skill Evaluation](references/agent-skill-evaluation.md)
- [Goal And Risk Cases](references/goal-and-risk-cases.md)
