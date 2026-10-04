---
name: skill-miner
description: "Mine Codex/Claude/Grok/Pi sessions, memory files, and project context docs for repeated failures, workflow patterns, concrete skill improvement candidates, and memory cleanup after durable repo truth extraction."
---

# Skill Miner

Extract reusable skill improvements from agent history and project context without mutating the target repository by default.

Agent memory files are staging evidence, not long-term truth. Prefer extracting durable knowledge into repo code, repo docs, repo-local skills, or generic skills. After extraction, classify the corresponding memory entries as cleanup candidates instead of preserving them as the final source of truth.

Mining returns candidates with their source evidence. The user or calling agent adjudicates promotion and memory maintenance and authorizes any separate edit.

## Scope

Default scope is the current Git repository. If no Git root exists, use the current working directory. Use all-history scope only when the user explicitly asks to search all local agent homes. When the user names additional agent homes, include those homes explicitly instead of assuming only the current host home.

Read these sources when available:
- Codex sessions: `~/.codex/sessions/**/*.jsonl`
- Codex memory: `~/.codex/memories/MEMORY.md`
- Claude sessions: `~/.claude/projects/**/*.jsonl`
- Claude memory: `~/.claude/projects/**/memory/*.md` and other `~/.claude/**/memory/*.md`
- Grok sessions: `~/.grok/sessions/<urlencoded-workspace>/prompt_history.jsonl` and per-session `events.jsonl`
- Pi sessions: `~/.pi/agent/sessions/**/*.jsonl`
- Project context docs: tracked `AGENTS.md` and `README.md` files under the target repo; symlinks that resolve to an already scanned document are deduplicated

Additional homes use the same directory shapes under their own Codex, Claude, Grok, or Pi home roots. Pi scanning is read-only and limited to `sessions/**/*.jsonl`; do not read auth, settings, databases, other runtime stores, or subagent private state.

Do not decide what future agents should write into memory. Mine existing memory only to identify missing repo truth, missing skills, stale memory, and cleanup candidates.

## Workflow

1. Confirm the requested scope: current repo, named repo, or all local Codex/Claude/Grok/Pi history.
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

Resolve the skill directory from this file:

```bash
SKILL_DIR="$(cd "$(dirname "<path to this SKILL.md>")" && pwd)"
```

Run the bundled read-only parser for the current repository:

```bash
python3 "$SKILL_DIR/scripts/extract-session-signals.py" --scope current --repo-root "$(git rev-parse --show-toplevel)"
```

All-history scope is an explicit expansion beyond the default current repository; multiple homes, machine-readable aggregation, and skill-usage measurement each add inputs or interpretation without changing that history scope. Use [Parser Modes](references/parser-modes.md) when the task requires one of them.

The script is read-only and accepts only named parameters. `--codex-home`, `--claude-home`, `--grok-home`, and `--pi-home` are repeatable; comma-separated values are also accepted. Default sources include `grok` and `pi`. `--pi-home` defaults to `~/.pi/agent`. Grok workspace directories under `sessions/` are URL-encoded absolute paths; scope `current` matches those decoded paths to `--repo-root`. Default repository scope remains `current`; cross-repo Pi history still requires `--scope all`.

Interpret session evidence before treating it as intent:

- Pi v3 JSONL files are interpreted on the last determinable recorded `id`/`parentId` branch and that selection is reported rather than treated as the UI current branch. Exclusive branches are not concatenated. Mine raw tree messages, not compaction summaries or `retainedTail` copies. Version 1/2 and other unsupported or malformed files are disclosed as incomplete evidence, not counted as complete sessions. Do not follow `parentSession` outside the selected files; unrecognized forks are limitations, not unique-task claims. Strip injected `<skill ...>...</skill>` blocks and keep the remaining user tail as intent; skill injection is not an explicit user invocation. Count assistant `stop`, `toolUse`, `error`, `aborted`, and `length` separately from model-change events and from the assistant's actual model. Ordinary `stop` is not completion, premature stop, or missing approval; a later continue/approval prompt is only a candidate relationship.
- Raw examples are disabled by default. Set a positive `--limit` only when bounded session excerpts are required. Pi samples are categorical summaries and omit thinking, images, and raw tool payloads; treat any excerpt as potentially sensitive because sanitization is not a guarantee that arbitrary secrets are safe.

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
- Do not treat ordinary Pi `stop` as task success or as an approval-gate failure.
- Surface malformed, unsupported, or partial Pi evidence instead of reporting a silently complete count.

## Promotion Rules

Apply promotion only after ordinary mining surfaces a recurring pattern. Promote to a generic skill only when the pattern recurs across repositories or across task types. Promote to a repo-local skill when the pattern depends on repository topology, runtime inventory, local hostnames, or domain-specific operational truth. Promote stable operational facts to scoped repo docs or code-owned truth. Do not promote one-time runtime snapshots; use them only as evidence, and do not preserve them as durable memory unless no repo or skill surface can own them.

Promotion is a recommendation. Name the recurring source evidence for each candidate, and let the user or calling agent adjudicate promotion and authorize any skill edit; mining does not promote or edit by itself.

## Memory Cleanup

When memory entries have been extracted into durable repo truth:

- list the extracted memory entries or task groups as cleanup candidates
- cite the target repo files that now own the truth
- preserve only short pointers when useful for historical lookup
- never edit agent memory files directly unless the user explicitly requests memory maintenance through the active memory workflow

Cleanup entries are recommendations; the user or calling agent authorizes memory maintenance. The preferred end state is repo-owned truth plus lean agent memory, not agent-specific memory as a parallel documentation system.
