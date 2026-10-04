# Parser Modes

These modes extend the current-repository parser invocation in `SKILL.md`. Resolve `SKILL_DIR` from that file first; every command here is read-only. Read only the mode the task requires.

Source-home selection (`--codex-home`, `--claude-home`, `--grok-home`, `--pi-home`), output format (`--format`), and history scope (`--scope`) are independent controls. Adding homes or selecting JSON output does not widen history scope; scope stays `current` unless `--scope all` is passed explicitly, and scope matching is identical in every output format.

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
