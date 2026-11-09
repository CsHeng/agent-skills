# Parser Modes

These modes extend the current-repository parser invocation in `SKILL.md`. Resolve `SKILL_DIR` from that file first; every command here is read-only. Read only the mode the task requires.

Source-home selection (`--codex-home`, `--claude-home`, `--grok-home`, `--pi-home`), output format (`--format`), and history scope (`--scope`) are independent controls. Scope stays `current` unless `--scope all` is passed explicitly, and scope matching is identical across homes and output formats. Default sources include `grok` and `pi`, and `--pi-home` defaults to `~/.pi/agent`.

## Source Locations

Read these sources under each home when available; the default scope is still the current repository, and cross-repo Pi history needs `--scope all`.

- Codex sessions: `~/.codex/sessions/**/*.jsonl`
- Codex memory: `~/.codex/memories/MEMORY.md`
- Claude sessions: `~/.claude/projects/**/*.jsonl`
- Claude memory: `~/.claude/projects/**/memory/*.md` and other `~/.claude/**/memory/*.md`
- Grok sessions: `~/.grok/sessions/<urlencoded-workspace>/prompt_history.jsonl` and per-session `events.jsonl`; the workspace directories are URL-encoded absolute paths, and scope `current` matches the decoded paths to `--repo-root`
- Pi sessions: `~/.pi/agent/sessions/**/*.jsonl`
- Project context docs: tracked `AGENTS.md` and `README.md` files under the target repo; symlinks that resolve to an already scanned document are deduplicated

Additional homes use the same directory shapes under their own Codex, Claude, Grok, or Pi home roots.

## Pi Evidence Interpretation

Interpret session evidence before treating it as intent:

- Interpret Pi v3 JSONL files on the last determinable recorded `id`/`parentId` branch and report that selection; identify it separately from the UI current branch and keep exclusive branches separate.
- Mine raw tree messages as the evidence source.
- Disclose version 1/2 and other unsupported or malformed files as incomplete evidence, and surface partial Pi evidence in counts.
- Follow `parentSession` only within the selected files; report unrecognized forks as evidence limitations.
- Strip injected `<skill ...>...</skill>` blocks and keep the remaining user tail as intent; establish explicit user invocation from the user request.
- Count assistant `stop`, `toolUse`, `error`, `aborted`, and `length` separately from model-change events and from the assistant's actual model.
- Count assistant `stop` as a neutral event; treat a following continue or approval prompt only as a candidate relationship.
- Pi samples are categorical summaries that omit thinking, images, and raw tool payloads.

## All Local History

Expanding beyond the current repository is an explicit choice:

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" --scope all
```

## Multiple Local Homes

Repeat the home options for each additional Codex, Claude, Grok, or Pi home; comma-separated values are also accepted. Adding homes keeps the default current-repository scope; add `--scope all` only when the task also needs all-history coverage.

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" \
  --codex-home ~/.codex \
  --codex-home /path/to/another/.codex \
  --claude-home ~/.claude \
  --claude-home /path/to/another/.claude \
  --grok-home ~/.grok \
  --grok-home /path/to/another/.grok \
  --pi-home ~/.pi/agent \
  --pi-home /path/to/another/.pi/agent
```

## Machine-Readable Aggregation

`--format json` selects the output shape; scope and home options select their respective boundaries:

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" \
  --format json \
  --limit 0
```

## Skill Usage Measurement

For measuring whether an external skill bundle actually influenced sessions before retiring it:

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" \
  --scope all \
  --skill-usage-only \
  --skill-usage-root /path/to/external-skill-bundle \
  --skill-usage-prefix external-skill-prefix \
  --skill-usage-before-date YYYY-MM-DD
```

The `--scope all` there is a deliberate all-history choice for that measurement, independent of the skill-usage flags and output format.

For the current repository, keep explicit all-agent history scope separate from the inventory boundary and supply the contract explicitly:

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" \
  --scope all \
  --skill-usage-only \
  --skill-usage-root /absolute/path/to/repo/skills \
  --skill-usage-prefix coding \
  --skill-usage-contract /absolute/path/to/repo/contracts/skills.toml \
  --format json \
  --limit 0
```

Here too the history scope comes from the explicit `--scope all`.

Skill usage evidence is separated into explicit `$skill` user requests, assistant references, skill-file loads, and optional tool outputs. A model activation is a heuristic summary: a skill load without an explicit user request in the same session is inferred activation, while raw records supply an upper bound on invocation count. Installed flat paths resolve through exact current-inventory public ID directories; exclude loads that cannot resolve to a current public ID. Determine user intent from user requests after excluding injected prompts, instruction blocks, available-skill inventories, and Claude tool-result wrappers. `--skill-usage-contract` reports declared contract state, Codex source policy/defaults, and Claude frontmatter/default visibility as separate fields.

Skill output is not evidence by default. Use `--skill-usage-include-output` only when tool output itself is evidence; it is off by default because directory listings and inventory dumps can inflate usage counts. For Pi, skill-usage matching uses structured tool names and path-like arguments, and include-output remains subject to the sensitive-content boundary.
