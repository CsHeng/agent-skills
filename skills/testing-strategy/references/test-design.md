# Test Design

Read this when writing new tests.

- Use Arrange-Act-Assert or an equally clear scenario structure.
- Name tests by behavior, condition, and outcome.
- Use table-driven examples for stable rule matrices.
- Use properties or fuzzing when invariants matter more than examples.
- Use characterization tests to investigate unknown consumer-relevant behavior before refactoring. Keep observations separate from required compatibility, and carry forward only what a consumer or explicit requirement depends on.
- Keep workflows focused on business sequences.
- Keep UI and E2E tests narrow and user-visible.
