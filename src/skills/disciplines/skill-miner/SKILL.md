---
name: skill-miner
description: "Mine Codex/Claude/Grok sessions, memory files, and project context docs for repeated failures, workflow patterns, concrete skill improvement candidates, and memory cleanup after durable repo truth extraction."
---

# Skill Miner

Extract reusable skill improvements from agent history and project context without mutating the target repository by default.

Agent memory files are staging evidence, not long-term truth. Prefer extracting durable knowledge into repo code, repo docs, repo-local skills, or generic skills. After extraction, classify the corresponding memory entries as cleanup candidates instead of preserving them as the final source of truth.

## Scope

Default scope is the current Git repository. If no Git root exists, use the current working directory. Use all-history scope only when the user explicitly asks to search all local agent homes. When the user names additional agent homes, include those homes explicitly instead of assuming only the current host home.

Read these sources when available:
- Codex sessions: `~/.codex/sessions/**/*.jsonl`
- Codex memory: `~/.codex/memories/MEMORY.md`
- Claude sessions: `~/.claude/projects/**/*.jsonl`
- Claude memory: `~/.claude/projects/**/memory/*.md` and other `~/.claude/**/memory/*.md`
- Grok sessions: `~/.grok/sessions/<urlencoded-workspace>/prompt_history.jsonl` and per-session `events.jsonl`
- Project context docs: tracked `AGENTS.md` and `README.md` files under the target repo, plus an existing legacy `CLAUDE.md` as compatibility-migration evidence; symlinks that resolve to an already scanned document are deduplicated

Additional homes use the same directory shapes under their own Codex, Claude, or Grok home roots.

Do not decide what future agents should write into memory. Mine existing memory only to identify missing repo truth, missing skills, stale memory, and cleanup candidates.

## Workflow

1. Confirm the requested scope: current repo, named repo, or all local Codex/Claude/Grok history.
2. Stay read-only unless the user explicitly approves skill edits.
3. Run the bundled parser for structured signals instead of raw-scanning large JSONL files.
4. Separate evidence into:
   - command failures and tool errors
   - interrupted, compacted, or rolled-back turns
   - user corrections and scope rejections
   - approval-gate mistakes
   - memory-recorded failure patterns
   - project docs that are large, duplicated, or workflow-heavy enough to mine
5. Classify each candidate as:
   - update an existing generic skill
   - add a new generic skill
   - add or update a repo-local skill
   - add or update scoped repo docs or code truth
   - mark extracted memory for cleanup
   - do not promote
6. For memory-derived findings, decide whether the target repo already owns the durable truth. If yes, recommend removing or shrinking the memory entry after the repo update is verified.
7. Recommend concrete target files and validation commands.

## Parser

Use:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py --scope current --repo-root "$(git rev-parse --show-toplevel)"
```

For all local history:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py --scope all
```

For multiple local homes, repeat the home options:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py \
  --scope all \
  --codex-home ~/.codex \
  --codex-home /path/to/another/.codex \
  --claude-home ~/.claude \
  --claude-home /path/to/another/.claude \
  --grok-home ~/.grok \
  --grok-home /path/to/another/.grok
```

For machine-readable aggregation:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py \
  --scope all \
  --format json \
  --limit 0
```

For measuring whether an external skill bundle actually influenced sessions before retiring it:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py \
  --scope all \
  --skill-usage-only \
  --skill-usage-root /path/to/external-skill-bundle \
  --skill-usage-prefix external-skill-prefix \
  --skill-usage-before-date YYYY-MM-DD
```

For the current repository, keep all-agent history scope separate from the inventory boundary and supply the contract explicitly:

```bash
python3 /absolute/path/to/skills/skill-miner/scripts/extract-session-signals.py \
  --scope all \
  --skill-usage-only \
  --skill-usage-root /absolute/path/to/repo/skills \
  --skill-usage-prefix coding \
  --skill-usage-contract /absolute/path/to/repo/contracts/skills.toml \
  --format json \
  --limit 0
```

The script is read-only and accepts only named parameters. `--codex-home`, `--claude-home`, and `--grok-home` are repeatable; comma-separated values are also accepted. Default sources include `grok`. Grok workspace directories under `sessions/` are URL-encoded absolute paths; scope `current` matches those decoded paths to `--repo-root`.

Skill usage evidence is separated into explicit `$skill` user requests, assistant references, skill-file loads, and optional tool outputs. A model activation is only a heuristic summary: a skill load without an explicit user request in the same session is inferred activation, while raw records remain an upper bound rather than an exact invocation count. Installed flat paths resolve through exact current-inventory public ID directories; loads that cannot resolve to a current public ID are excluded instead of entering a repository-wide fallback bucket. Injected prompts, instruction blocks, available-skill inventories, and Claude tool-result wrappers do not count as user intent. `--skill-usage-contract` reports declared contract state, Codex source policy/defaults, and Claude frontmatter/default visibility as separate fields.

Raw examples are disabled by default. Set a positive `--limit` only when bounded session excerpts are required. Use `--skill-usage-include-output` only when tool output itself is evidence; it is off by default because directory listings and inventory dumps can inflate usage counts.

## Output Rules

- Lead with counts and strongest repeated patterns.
- Include project context signals by default when a repo root is available.
- Quote short user corrections only when they prove a workflow mistake.
- Treat search no-match exit codes as weak evidence unless followed by user correction.
- Do not promote repo-local facts into generic skills.
- Do not leave durable recommendations as `keep in memory only` when repo docs, repo-local skills, repo code, or generic skills can own them.
- For memory-derived findings, name both the durable target file and the source memory cleanup action.
- Do not claim a write, install, deploy, or commit happened unless the corresponding step completed.
- When the user requested analysis only, end with recommendations and do not edit files.

## Promotion Rules

Promote to a generic skill only when the pattern recurs across repositories or across task types. Promote to a repo-local skill when the pattern depends on repository topology, runtime inventory, local hostnames, or domain-specific operational truth. Promote stable operational facts to scoped repo docs or code-owned truth. Do not promote one-time runtime snapshots; use them only as evidence, and do not preserve them as durable memory unless no repo or skill surface can own them.

## Memory Cleanup

When memory entries have been extracted into durable repo truth:

- list the extracted memory entries or task groups as cleanup candidates
- cite the target repo files that now own the truth
- preserve only short pointers when useful for historical lookup
- never edit agent memory files directly unless the user explicitly requests memory maintenance through the active memory workflow

The preferred end state is repo-owned truth plus lean agent memory, not agent-specific memory as a parallel documentation system.
