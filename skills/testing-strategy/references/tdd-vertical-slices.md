# TDD Vertical Slices

Use this reference when the user asks for TDD, test-first work, red-green-refactor, or when a risky behavior change needs a narrow executable contract before implementation.

## Rules

- Apply TDD to required executable behavior. Use the documentation tooling guidance in `testing-strategy` for Markdown-only changes.
- Test observable behavior through the public interface.
- Derive the expected result from a consumer requirement, independent example, contract, or failure mode before writing the implementation; a test and code generated from the same guess can agree while both are wrong.
- Write one failing test or reproducer for one behavior, implement the smallest change to pass it, then repeat.
- Keep one real behavior, its minimal setup, implementation, and feedback together; reuse the existing test environment when it can exercise that behavior.
- Confirm the red state fails for the expected reason before implementing.
- Refactor after the current required behavior is green. If a failure exposes an unsupported test constraint, correct or remove that assertion within scope.
- Keep tests resilient to internal refactors such as harmless renames or internal decomposition. Add a post-change regression test when it closes an uncovered behavior gap, including when implementation came first.

## Useful Feedback

Be able to explain the behavior exercised, why the red state failed, what made it pass, and which later changes require another check. Existing tests and command output can carry these facts; no per-slice receipt, separate record, or additional gate is required.

If no correct seam exists for a regression test, use the tightest adequate substitute and disclose its limits. Size the test harness to the behavior and limit evidence claims to what the substitute exercised.
