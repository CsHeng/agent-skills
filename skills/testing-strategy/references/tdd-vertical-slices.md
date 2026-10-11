# TDD Vertical Slices

Use this reference when the user asks for TDD, test-first work, red-green-refactor, or when a risky behavior change needs a narrow executable contract before implementation.

## Rules

- Apply TDD to required executable behavior, not documentation wording, diagram content, or incidental implementation choices. Use the documentation tooling guidance in `testing-strategy` for Markdown-only changes.
- Test observable behavior through the public interface, not private implementation shape.
- Derive the expected result from a consumer requirement, independent example, contract, or failure mode before writing the implementation; a test and code generated from the same guess can agree while both are wrong.
- Write one failing test or reproducer for one behavior, implement the smallest change to pass it, then repeat.
- Do not write a batch of imagined tests or build all supporting fixtures before code. Keep one real behavior, its minimal setup, implementation, and feedback together; reuse the existing test environment when it can exercise that behavior.
- Confirm the red state fails for the expected reason before implementing.
- Refactor after the current required behavior is green. If a failure exposes an unsupported test constraint, correct or remove that assertion within scope rather than adding product behavior merely to satisfy it.
- Keep tests resilient to internal refactors; a harmless rename or internal decomposition should not break behavior tests. Add a post-change regression test only when it closes an uncovered behavior gap; do not ban useful tests solely because implementation came first.

## Useful Feedback

Be able to explain the behavior exercised, why the red state failed, what made it pass, and which later changes require another check. Existing tests and command output can carry these facts; no per-slice receipt, separate record, or additional gate is required.

If no correct seam exists for a regression test, use the tightest adequate substitute and disclose its limits. Do not build a generic test harness solely to preserve a test-first ritual, and do not claim that substitute evidence covers behavior it never exercised.
