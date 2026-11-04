# Parser Modes

These modes extend the current-repository parser invocation in `SKILL.md`. Resolve `SKILL_DIR` from that file first; every command here is read-only. Read only the mode the task requires.

Source-home selection (`--codex-home`, `--claude-home`, `--grok-home`, `--pi-home`), output format (`--format`), and history scope (`--scope`) are independent controls. Adding homes or selecting JSON output does not widen history scope; scope stays `current` unless `--scope all` is passed explicitly, and scope matching is identical in every output format. Default sources include `grok` and `pi`, and `--pi-home` defaults to `~/.pi/agent`.

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

- Interpret Pi v3 JSONL files on the last determinable recorded `id`/`parentId` branch and report that selection; it is not the UI current branch, and exclusive branches are not concatenated.
- Mine raw tree messages rather than compaction summaries or `retainedTail` copies.
- Disclose version 1/2 and other unsupported or malformed files as incomplete evidence rather than counting them as complete sessions, and surface partial Pi evidence instead of reporting a silently complete count.
- Follow `parentSession` only within the selected files; unrecognized forks are limitations, not unique-task claims.
- Strip injected `<skill ...>...</skill>` blocks and keep the remaining user tail as intent; skill injection is not an explicit user invocation.
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

`--format json` changes only the output shape; it does not change scope or the selected homes:

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

Here too the history scope comes from the explicit `--scope all`; the contract, prefix, and JSON flags do not affect it.

Skill usage evidence is separated into explicit `$skill` user requests, assistant references, skill-file loads, and optional tool outputs. A model activation is only a heuristic summary: a skill load without an explicit user request in the same session is inferred activation, while raw records remain an upper bound rather than an exact invocation count. Installed flat paths resolve through exact current-inventory public ID directories; loads that cannot resolve to a current public ID are excluded instead of entering a repository-wide fallback bucket. Injected prompts, instruction blocks, available-skill inventories, and Claude tool-result wrappers do not count as user intent. `--skill-usage-contract` reports declared contract state, Codex source policy/defaults, and Claude frontmatter/default visibility as separate fields.

Skill output is not evidence by default. Use `--skill-usage-include-output` only when tool output itself is evidence; it is off by default because directory listings and inventory dumps can inflate usage counts. For Pi, skill-usage matching uses structured tool names and path-like arguments rather than flattened payloads, and include-output still does not lift the sensitive-content boundary.
