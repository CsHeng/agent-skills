# Exclusion Criteria

Read this when an untracked, tracked-generated or ambiguous file is present in the changes.

| Category | Examples | Action |
|----------|----------|--------|
| Secrets & credentials | API keys, tokens, passwords, .env files, private keys | Exclude, warn user; stop if tracked or staged |
| Foreign or unowned generated output | build/, dist/, *.pyc, __pycache__/, node_modules/, local caches and intermediate artifacts not intended as deliverables | Exclude; usually already matched by .gitignore |
| Intentional tracked generated deliverables | Committed generated mirrors, generated clients or docs, checked-in build outputs, and lock files that a source change in the same group requires | Include with the group whose source change produces or requires them |
| Large binaries | Images >1MB, compiled binaries, archives | Exclude, note reason |
| Temporary files | *.tmp, *.swp, *.log, .DS_Store | Exclude |
| IDE/editor config | .idea/, .vscode/settings.json (user-specific) | Exclude |
| Lock files with no source change | package-lock.json alone without package.json change | Exclude unless dependency intent is clear |

Apply judgment beyond these rules, reading file content when the filename alone is ambiguous: a `.json` file could be configuration (commit) or generated output (exclude).

"Generated" is a question of ownership and intent. A file the repository already tracks as a deliverable (a generated distribution mirror, a generated client or API document, a checked-in lock file, a build output the project commits on purpose) is committable and belongs to the group whose source change produced it. Foreign or unowned build output, caches, and ignored intermediates stay excluded. When it is unclear whether a tracked generated file is an intentional deliverable, check the repository's conventions and `.gitignore` first, and judge it by its role rather than its name or directory.

When uncertain, include the file if it is a normal source, config, test, docs, or lockfile change. When the uncertainty is whether a tracked or staged file should be versioned at all, stop and ask for human confirmation before committing.
