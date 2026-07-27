# Shell Code Review Checklist

## Input

- Review target: caller-specified shell file path (required)
- Target shell: trusted shebang or caller-declared interpreter

## DEPTH Workflow

### D - Decomposition

- Objective: Complete read-only shell script audit
- Scope: Guidelines compliance, ShellCheck diagnostics, syntax validation
- Output: Evidence-backed findings with the smallest viable correction
- Reference: shell-guidelines SKILL.md

### E - Explicit Reasoning

- Findings: Line number, description, guideline section, explicit reasoning
- Recommendations: Name only the smallest change needed to resolve each finding
- Constraints: No stylistic changes, avoid false positives

### P - Parameters

- Strictness: Maximum compliance enforcement
- Findings: Conservative and rule-driven
- Determinism: Required output consistency
- Mutation: Prohibited; the lifecycle controller owns any repair

### T - Test Cases

- Failure Case: Missing fi, unquoted variables, prohibited variable names, or missing entrypoint strict mode -> report anchored findings
- Success Case: Proper structure, safe variable names, quoting, and target-appropriate entrypoint strict mode -> PASS status

### H - Heuristics

- Minimal Surface: Limit recommendations to necessary lines
- No Reformatting: Recommend preserving existing structure and logic
- Safe Output: Recommend changes that preserve valid shell code
- Deterministic Order: Shebang -> strict mode -> quoting -> variables -> traps -> flow

## Workflow

1. Target Validation: Read the script file without executing it
2. Interpreter Detection: Identify the shebang or caller-declared target and request context if neither exists
3. Syntax Validation: Run the resolved interpreter's syntax-only check
4. Static Analysis: For bash/sh files, execute ShellCheck with GCC format and pass `-s <bash|sh>` when the resolved shell came from caller context rather than a trusted shebang; for zsh, use `zsh -n` plus the manual guidelines audit
5. Guidelines Compliance: Check against shell scripting best practices
6. Violation Analysis: Categorize findings by severity and type
7. Report Compilation: Generate structured findings with actionable recommendations
8. Validation: Ensure every blocking finding is evidence-backed and the reviewer has not edited the implementation

## Output

- Summary: Pass/fail status with issue count
- Findings: Line-by-line evidence, impact, smallest viable correction, confidence, and scope classification
- Static Analysis: Relevant ShellCheck diagnostics for bash/sh, or the zsh manual-audit result
- Syntax Check: Interpreter validation results
- Verdict: Final PASS/FAIL determination
