# PowerShell Operational Checks

Run these commands from a `pwsh` session. The parser snippet exits non-zero when the target file has parse errors, so an automated check must treat a non-zero exit as failure.

## Syntax Validation

```powershell
# Syntax validation (PowerShell parser); exits 1 when diagnostics are present.
$target = 'path/to/script.ps1'
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($target, [ref]$tokens, [ref]$errors) | Out-Null
if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_.Message }
    exit 1
}
Write-Output "Syntax OK: $target"
```

## Linting

```powershell
# PSScriptAnalyzer
Invoke-ScriptAnalyzer -Path 'path/to/script.ps1' -Severity Warning,Error
```

## Approved Verbs

```powershell
# Check approved verbs
Get-Verb | Sort-Object Verb
```
