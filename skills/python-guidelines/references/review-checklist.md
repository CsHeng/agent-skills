# Python Code Review Checklist

Apply these checks to the caller's bounded Python review target and its declared runtime. Read the target and relevant project configuration before choosing checks; do not execute application code just to inspect it.

This is a language overlay, not another review report. The primary reviewer owns severity order, required fields and the verdict. Return relevant evidence and unverified areas through that owner; do not add a second summary, raw tool transcript or fixed category order.

## Review Checks

- Resolve the Python version, owning project and dependency manifest. Use the toolchain and coding requirements in `python-guidelines`, not a separately maintained copy of those rules.
- Validate syntax with `ast.parse` or the target interpreter's syntax check. If using compilation, keep its bytecode outside the source tree; do not assume a missing interpreter or an unrun check passed.
- Run the project-pinned Ruff check. Formatter and safe-fix diagnostics belong to Ruff; name the applicable command and relevant diagnostic rather than hand-writing style, formatter or safe-fix patches.
- Run the appropriate type checker with the owning project's dependencies. Check type hints, unsafe defaults, exception boundaries, input validation and other applicable Python semantics.
- Inspect custom CLI argument definitions against the parameter rules below. Third-party tool invocations are outside that rule.
- Anchor material findings to location, evidence, impact and the smallest semantic correction. Candidate semantic diffs are optional, remain read-only, and must preserve valid Python and the authorized scope. The calling implementing agent adjudicates and applies repairs.

## Type-Check Dependencies

Use the nearest owning `pyproject.toml`, then `requirements*.txt`, rather than guessing imports or injecting individual packages until a command passes.

- For a `pyproject.toml` project, including a script project with `[tool.uv] package = false`, use its environment and `uv run ty check <target>`.
- For a requirements-based project, use `uvx --with-requirements <requirements.txt> ty check <target>`.
- If an import remains unresolved, check that the owning manifest declares the dependency before recommending code changes. A missing manifest is a finding or proposed repair, not permission for the read-only evaluator to create one.
- Use one-off `uvx --with <pkg>` only as a last-resort fallback and disclose that fallback and its limits.

Use the environment and cache isolation policy in `python-guidelines` when running these commands.

## Custom CLI Parameters

- Check `argparse.add_argument()` for single-letter aliases such as `add_argument("-x", "--xxx")` or `add_argument("-x")`.
- Require `ArgumentParser(add_help=False)` and an explicit `add_argument("--help", action="help")` so automatic `-h` does not reintroduce a short alias.
- Report a violated parameter rule with its location and effect. It contributes to the primary review; it does not require a separate parameter verdict or report section.
