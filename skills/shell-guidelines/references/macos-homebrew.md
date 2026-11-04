# Shell On macOS And Homebrew

Read this when a script targets macOS or a Homebrew `PATH`, needs Bash 4+, or an option behaves differently than expected.

- `#!/usr/bin/env bash` resolves through `PATH`, and macOS defaults to `/bin/bash` (3.2). For Bash 4+ features, put Homebrew Bash on `PATH` or use the host-appropriate absolute shebang for internal scripts: `/opt/homebrew/bin/bash` on Apple Silicon, `/usr/local/bin/bash` on Intel.
- macOS login `zsh` runs `path_helper` (via `/etc/zprofile`), which can override `PATH` changes from `.zshenv`. For tasks that test `zsh -lc`, put the final Homebrew `PATH` setup in `.zprofile` after `path_helper`, using the host's `brew shellenv`.
- Homebrew `curl` is commonly keg-only; use `export PATH="$(brew --prefix curl)/bin:$PATH"` for modern curl and TLS features.
- Non-interactive bash sources `$BASH_ENV`; point it at a file that exports the expected `PATH` (including Homebrew) when automation runs `bash` non-interactively.
- A resolved command's dialect can differ from the host OS when Homebrew `*/libexec/gnubin` directories shadow system commands. `references/tool-selection.md` in `skills-routing` covers ad hoc diagnostic handling. For persisted scripts that depend on a specific command dialect, run this skill's bundled `scripts/audit-homebrew-command-shadowing.py`.
- Quick diagnosis: `command -v bash; /usr/bin/env bash --version | head -n1; type -a bash; command -v curl; curl --version | head -n1`.

## Homebrew Command Shadow Audit

The audit is read-only and emits deterministic JSON containing effective providers, duplicate providers, macOS system shadows, and gnubin-only commands:

```bash
SKILL_DIR="$(cd "$(dirname "<path to this skill's SKILL.md>")" && pwd)"
python3 "$SKILL_DIR/scripts/audit-homebrew-command-shadowing.py"
```

Use `--path` for a synthetic or remote `PATH` snapshot, repeat `--system-dir` to replace the default macOS system directories, and add `--compact` for JSONL-oriented tooling.
