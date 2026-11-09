# PowerShell Code Review Checklist

Apply these checks to the caller's bounded PowerShell target. Read the script and project requirements before choosing checks, and inspect the implementation statically.

Contribute relevant evidence and verification gaps to the `review-change` caller.

## Review Checks

- Identify the declared runtime and applicable `#Requires -Version`; check the requirements owned by `powershell-guidelines`.
- Use `System.Management.Automation.Language.Parser.ParseFile` to validate syntax without running the script; a non-empty diagnostic set is invalid syntax. Preserve parser diagnostics that support a finding, and disclose unavailable or unrun validation.
- Run PSScriptAnalyzer with Warning and Error severity. Connect relevant diagnostics to the reviewed scope.
- Check `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`, approved verbs, explicit error handling and cross-platform path construction with `Join-Path`; `powershell-guidelines` states the narrow `[System.IO.Path]::Combine()` exception.
- Check for cmdlet aliases and global variables, including the `PSAvoidUsingCmdletAliases` and `PSAvoidGlobalVars` diagnostics.
- Inspect custom parameters against the rule below. Treat built-in cmdlet parameter names separately from custom aliases.
- Anchor material findings to their locations, evidence, impact and smallest viable correction. A candidate diff is optional and preserves valid PowerShell and the caller's scope.

## Custom Parameter Aliases

Check `[Alias()]` attributes for single-character aliases such as `[Alias('x')]`. Custom parameters follow the Custom CLI Conventions in `development-standards` (descriptive names); a single-character alias is a finding for the single review.

A clean parser or analyzer run covers syntax and analyzer rules; report semantic risks and checks that were not run even when no tool diagnostic remains.
