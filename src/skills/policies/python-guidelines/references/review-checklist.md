# Python Code Review Checklist

Apply these checks to the caller's bounded Python review target and its declared runtime. Read the target and relevant project configuration before choosing checks; do not execute application code just to inspect it.

This is a language overlay, not another review report. The primary reviewer owns severity order, required fields and the verdict. Return relevant evidence and unverified areas through that owner; do not add a second summary, raw tool transcript or fixed category order.

## Review Checks

- Resolve the Python version, owning project and dependency manifest. Use the toolchain and coding requirements in `python-guidelines`, not a separately maintained copy of those rules.
- Validate syntax with `ast.parse` or the target interpreter's syntax check. If using compilation, keep its bytecode outside the source tree; do not assume a missing interpreter or an unrun check passed.
- Run the project-pinned Ruff check. Formatter and safe-fix diagnostics belong to Ruff; name the applicable command and relevant diagnostic rather than hand-writing style, formatter or safe-fix patches.
- Run the appropriate type checker with the owning project's dependencies. Check type hints, unsafe defaults, exception boundaries, input validation and other applicable Python semantics.
- Inspect custom CLI argument definitions against the owning project's declared parameter rules below. Third-party tool invocations are outside that rule.
- Anchor material findings to location, evidence, impact and the smallest semantic correction. Candidate semantic diffs are optional, remain read-only, and must preserve valid Python and the authorized scope. The calling implementing agent adjudicates and applies repairs.

## Type-Check Dependencies

The owning project's configured checker is the authoritative baseline; review applies the same baseline as implementation and does not raise it. Resolve the nearest owning `pyproject.toml`, then `requirements*.txt`, and read its type-checker configuration before choosing a command, rather than guessing imports or injecting individual packages until a command passes.

- When the project configures mypy (`[tool.mypy]`, `mypy.ini`, a `setup.cfg` section, or an explicit mypy gate), run that configured mypy through the owning environment, such as `uv run mypy <target>`.
- When the project configures pyright (`[tool.pyright]` or `pyrightconfig.json`), run that configured pyright, such as `uv run pyright <target>`.
- When the project configures ty, or declares a type-checking gate that names ty, run `uv run ty check <target>`.
- When the project declares no type-checker configuration at all, the default is `ty`: `uv run ty check <target>` for a `pyproject.toml` project, or `uvx --with-requirements <requirements.txt> ty check <target>` for a requirements-based project, matching `python-guidelines`.
- Do not substitute a different checker, or add checks stricter than the project already declares, just because another tool is available; a stricter setting is an optional, non-blocking observation unless the owning project adopts it.
- If an import remains unresolved, check that the owning manifest declares the dependency before recommending code changes. A missing manifest is a finding or proposed repair, not permission for the read-only evaluator to create one.
- Use one-off `uvx --with <pkg>` only as a last-resort fallback and disclose that fallback and its limits.

Use the environment and cache isolation policy in `python-guidelines` when running these commands.

## Custom CLI Parameters

Apply the owning project's CLI convention; review must not introduce a stricter alias rule than the project declares.

- When the project declares a short-alias or help-flag convention, check `argparse.add_argument()` against that convention and report only a violated repository rule.
- An established alias already shipped by the tool, such as a documented `app ls` subcommand or an existing short flag, is that project's interface and is not a review finding; do not recommend removing it.
- The `ArgumentParser(add_help=False)` plus explicit `add_argument("--help", action="help")` pattern is one way to avoid an unintended automatic `-h`; mention it only as an optional, non-blocking observation when the project has no established help convention.
- Report a violated project-declared parameter rule with its location and effect. It contributes to the primary review; it does not require a separate parameter verdict or report section.
