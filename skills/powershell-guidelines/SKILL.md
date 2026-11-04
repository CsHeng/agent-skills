---
name: powershell-guidelines
description: "Apply PowerShell 7 policy as a conditional overlay when writing or reviewing PowerShell scripts, modules, and manifests: pwsh, PSScriptAnalyzer, strict mode, approved verbs, and cross-platform scripting. Code that must stay compatible with Windows PowerShell 5.1 gets no overlay from this policy, which also does not authorize upgrading it."
---

# PowerShell Guidelines

Apply PowerShell 7 standards for safe, portable, auditable automation to `.ps1`, `.psm1` and `.psd1` files, including scripts authored on macOS for Windows execution, and to their review and syntax audit. Language selection reads `references/language-selection.md` in `skills-routing`; ad hoc tool choice reads `references/tool-selection.md` there.

## Progressive Disclosure

- Parser, analyzer and approved-verb commands: `references/operational-checks.md`
- Authoring on macOS for Windows execution, or a case-sensitivity, line-ending or native-command portability question: `references/macos-notes.md`
- Writing an advanced function with error records, or checking a native command's exit code: `references/error-handling-examples.md`
- Read-only review checks: `references/review-checklist.md`

## Rules

### Script Header

- Start every script with `#Requires -Version 7.0`, adding `#Requires -Modules` for external module dependencies.
- Follow it with `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`. Use `'SilentlyContinue'` only inside a documented exception-handling block.

### Naming

- Name functions `Verb-Noun` with an approved verb (`Get-Verb` lists them).
- Use PascalCase for functions, parameters and script-scoped variables, and `$camelCase` for locals.
- Name script files in PascalCase: `Get-UserReport.ps1`.
- Write full cmdlet names in scripts (`Get-ChildItem`, not `ls`).
- Pass data through parameters and return values.

### Paths

- Build every path with `Join-Path` and `$PSScriptRoot`, and guard any platform-specific literal (such as `C:\...`) with a platform check.
- A single `[System.IO.Path]::Combine()` call may join three or more trusted literal segments in one expression, when no later segment is rooted (a rooted segment discards the earlier path).

### Inputs And Security

- Use `[CmdletBinding()]` for advanced functions and `[Parameter(Mandatory)]` for required inputs. Choose parameter types and validation attributes (`[ValidateSet()]`, `[ValidatePattern()]`, `[ValidateRange()]`) for the actual input constraints, and reject unexpected values early.
- Pass untrusted input as parameters or typed values.
- Supply secrets, credentials and API keys through the environment or a secret mechanism, and accept passwords as `[SecureString]` or credential objects.

### Errors

- Let failures propagate to the owning boundary. Add `try/catch` where recovery or context is needed, and `finally` where cleanup must run on success and failure. Include the operation attempted and relevant values in error messages.
- Use `$PSCmdlet.ThrowTerminatingError()` in advanced functions.
- Check `$LASTEXITCODE` after every native command.
- For generic error-handling patterns, see `error-patterns`.

## Checks

Run the parser check and `Invoke-ScriptAnalyzer` (Warning and Error severity) from `references/operational-checks.md`; the parser check exits non-zero when `Parser::ParseFile` reports diagnostics. Test scripts with `pwsh` on macOS before deploying to Windows.
