# PowerShell Error Handling Examples

Read this when writing an advanced function that raises error records, or checking a native command's exit code. For generic resilience patterns, see `error-patterns`.

## Advanced Function

The function raises one terminating error and lets the caller decide how to report or recover; add `try/catch` at the boundary that owns recovery or context.

```powershell
function Get-ConfigValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$ConfigPath,

        [Parameter(Mandatory)]
        [string]$Key
    )

    if (-not (Test-Path -Path $ConfigPath)) {
        $PSCmdlet.ThrowTerminatingError(
            [System.Management.Automation.ErrorRecord]::new(
                [System.IO.FileNotFoundException]::new("Config file not found: $ConfigPath"),
                'ConfigFileNotFound',
                [System.Management.Automation.ErrorCategory]::ObjectNotFound,
                $ConfigPath
            )
        )
    }
    $config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
    return $config.$Key
}
```

## Native Command Exit Code

At script level, `throw` is the way to stop on a failed native command.

```powershell
& git status
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE"
}
```
