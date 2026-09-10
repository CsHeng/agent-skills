# Python Code Review Checklist

## Input

- Target file path: caller-specified (required)

## DEPTH Workflow

### D - Decomposition

- Objective: Complete Python semantic audit; send formatter and safe-fix diagnoses to Ruff
- Scope: Guidelines compliance, Ruff diagnostics, ty type checking, syntax validation
- Output: Structured semantic findings; no manual style patches
- Reference: python-guidelines SKILL.md

### E - Explicit Reasoning

- Findings: Line number, description, guideline section, explicit reasoning
- Patches: None for formatter or `ruff check --fix` diagnostics; semantic candidate diffs only when the calling agent may apply them
- Constraints: No stylistic changes, avoid false positives, evaluator stays read-only

### P - Parameters

- Strictness: Maximum compliance enforcement
- Fixes: Conservative, rule-driven semantic findings; tool-owned style stays with Ruff
- Determinism: Required output consistency
- Format: Semantic findings; no generated formatter or safe-fix patches

### T - Test Cases

- Failure Case: Syntax errors, type errors, missing type hints, argparse or security guideline violations -> semantic findings
- Tool-Owned Case: Formatter or safe-fix diagnostics -> name the Ruff command, do not write a style patch
- Success Case: Proper structure, type hints, clean imports -> PASS status

### H - Heuristics

- Minimal Surface: Report only necessary semantic lines
- No Reformatting: Do not hand-write line-length or formatter patches; preserve original structure and logic
- Safe Output: Candidate semantic diffs must remain valid Python
- Deterministic Order: Tool-owned Ruff -> type hints -> syntax -> types -> unused semantic code

## Workflow

1. File Validation: Read script and verify file exists and is readable
2. Python Version Detection: Identify Python version requirements
3. Syntax Validation: Run `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile <file>` or `ast.parse`
4. Static Analysis: Execute ruff check with structured output. Formatter and safe-fix diagnostics are tool-owned; do not convert them into manual patches
5. Type Checking: Execute `ty` with structured output using manifest-backed dependencies (nearest `pyproject.toml` / `requirements*.txt`). Prefer `uv run ty check <target>` for `pyproject.toml` projects (including script projects with `[tool.uv] package = false`), and `uvx --with-requirements <requirements.txt> ty check <target>` for requirements-based projects; avoid hardcoded one-off `uvx --with <single-package>` fixes
6. Guidelines Compliance: Check against Python scripting best practices
7. Parameter Style Validation: Check for short parameter aliases in argparse definitions
8. Violation Analysis: Categorize findings by severity and type; separate tool-owned style from semantic review
9. Finding Boundary: Do not generate formatter or safe-fix patches. Semantic repairs stay candidate findings for the calling agent; the evaluator remains read-only
10. Report Compilation: Generate structured findings with actionable recommendations
11. Validation: Ensure any semantic candidate diff would produce valid and safe Python code

## Type-Check Dependency Resolution (Required)

- Detect nearest dependency manifest(s): `pyproject.toml` first, then `requirements*.txt`.
- `pyproject.toml` project (preferred): run `uv run ty check <target>`. This includes script projects; adding a minimal `pyproject.toml` with `[tool.uv] package = false` is valid and preferred over ad-hoc package flags.
- `requirements*.txt` project: run manifest-backed `uvx`: `uvx --with-requirements <requirements.txt> ty check <target>`.
- If imports still fail, verify the manifest actually contains the missing dependency before suggesting code changes.
- Only use explicit one-off `uvx --with <pkg>` as a last-resort fallback, and report that it was a fallback.

## Parameter Style Validation

- Detection: Search for argparse.add_argument() calls with short parameter aliases or missing add_help=False
- Violation Pattern: add_argument("-x", "--xxx") or add_argument("-x") where x is a single letter
- Violation Pattern: ArgumentParser() without add_help=False (allows automatic -h)
- Compliant Pattern: ArgumentParser(add_help=False) with manual add_argument("--help", action="help")
- Scope: Custom CLI scripts only; third-party tool invocations are excluded
- Output: FAIL if short parameter aliases detected or add_help not disabled, PASS otherwise

## Output

- Summary: Pass/fail status with issue count
- Deviations: Line-by-line violations with guideline references
- Ruff Output: Raw static analysis results, with formatter/safe-fix items directed to project-pinned Ruff rather than a generated style patch
- Syntax Check: Python validation results
- Type Check: ty diagnostics results
- Parameter Style Check: PASS/FAIL with violation locations
- Auto-Fix Patch: None for formatter or safe-fix-owned diagnostics; semantic candidate diffs remain optional and read-only
- Verdict: Final PASS/FAIL determination
- Ownership: Evaluator is read-only; the calling agent adjudicates semantic findings
