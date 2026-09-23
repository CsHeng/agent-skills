# TDD Vertical Slices

Use this reference when the user asks for TDD, test-first work, red-green-refactor, or when a risky behavior change needs a narrow executable contract before implementation.

## Rules

- Apply TDD to executable behavior, not to natural-language wording in documentation. Use the documentation verification rules in `testing-strategy` for Markdown-only changes.
- Test observable behavior through the public interface, not private implementation shape.
- Derive the expected result from a consumer requirement, independent example, contract, or failure mode before writing the implementation; a test and code generated from the same guess can agree while both are wrong.
- Write one failing test or reproducer for one behavior, implement the smallest change to pass it, then repeat.
- Do not write a batch of imagined tests before code. That horizontal flow often locks in guessed structure instead of verified behavior.
- Confirm the red state fails for the expected reason before implementing.
- Refactor only after the current slice is green.
- Keep tests resilient to internal refactors; a harmless rename or internal decomposition should not break behavior tests. Add a post-change regression test only when it closes an uncovered behavior gap; do not ban useful tests solely because implementation came first.

## Slice Gate

For each slice, record:

- behavior being tested
- public interface or command exercised
- red command and failure reason
- minimal green change
- follow-up verification command

If no correct seam exists for a regression test, state that as the finding and use the tightest substitute verification command.
