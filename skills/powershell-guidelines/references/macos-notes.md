# PowerShell On macOS And Cross-Platform Notes

Read this when a script authored on macOS targets Windows, or a case-sensitivity, line-ending or native-command portability question arises.

- PowerShell 7 on macOS installs through Homebrew (`brew install powershell`) and runs as `pwsh`.
- macOS [APFS](https://developer.apple.com/documentation/technologyoverviews/files-and-directories) is case-insensitive by default and also supports case-sensitive volumes. Check the target volume's behavior instead of inferring case sensitivity from the OS, and test path handling accordingly.
- macOS uses LF line endings; Windows expects CRLF for some tools. Use `.gitattributes` with `*.ps1 text eol=crlf` when targeting Windows.
- Use the `$HOME` automatic variable for portability; `$env:HOME` exists on macOS and `$env:USERPROFILE` on Windows.
- `grep`, `sed` and `awk` exist on macOS but not Windows; portable scripts use `Select-String`, `-replace` and `ForEach-Object`.
- Use `$env:PSModulePath` and `Join-Path` for portable module references.
