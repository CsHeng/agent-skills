# PowerShell Code Review Checklist

Apply these checks to the caller's bounded PowerShell target. Read the script and project requirements before choosing checks; the evaluator does not edit or execute the implementation.

This is a language overlay. The primary reviewer owns findings, severity order, required fields and the verdict. Contribute relevant evidence and verification gaps, not a second summary, raw analyzer transcript or mandatory patch report.

## Review Checks

- Identify the declared runtime and applicable `#Requires -Version`; check the requirements owned by `powershell-guidelines`.
- Use `System.Management.Automation.Language.Parser.ParseFile` to validate syntax without running the script. Preserve parser diagnostics that support a finding, and disclose unavailable or unrun validation.
- Run PSScriptAnalyzer with Warning and Error severity. Connect relevant diagnostics to the reviewed scope instead of dumping all analyzer output.
- Check `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`, approved verbs, explicit error handling and cross-platform path construction with `Join-Path`.
- Check for cmdlet aliases and global variables, including the `PSAvoidUsingCmdletAliases` and `PSAvoidGlobalVars` diagnostics.
- Inspect custom parameters against the rule below. Built-in cmdlet parameter names are not custom aliases.
- Anchor material findings to their locations, evidence, impact and smallest viable correction. A candidate diff is optional and must preserve valid PowerShell and the caller's scope; the implementing agent owns adjudication and any mutation.

## Custom Parameter Aliases

Check `[Alias()]` attributes for single-character aliases such as `[Alias('x')]`. Use descriptive parameters without single-character aliases. A violation is evidence for the primary review, not a separate pass/fail report.

Do not reinterpret a clean parser or analyzer run as proof that all requested behavior is correct. Preserve semantic risks and checks that were not run even when no tool diagnostic remains.
