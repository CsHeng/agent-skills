---
name: skill-miner
description: "Explicitly selected mining of Codex/Claude/Grok/Pi sessions, memory files, and project context docs for repeated failures, workflow patterns, concrete skill improvement candidates, and memory cleanup candidates after durable repo truth extraction. Use only when the user names it or asks to mine history or memory; current-repository analysis belongs to analyze-project."
---

# Skill Miner

Extract reusable skill improvements from agent history and project context. Mining returns candidates with their source evidence; the user or calling agent adjudicates promotion and memory maintenance and authorizes any separate edit. Stay read-only unless the user explicitly approves skill edits, and with an analysis-only request end with recommendations.

Apply the Promotion Rule in `references/memory-boundary.md` of `skills-routing` for how agent memory relates to durable repo truth.

## Scope

Default scope is the current Git repository, or the current working directory when no Git root exists. Use all-history scope when the user explicitly asks to search all local agent homes, and include additional agent homes when the user names them. Sources are Codex, Claude, Grok, and Pi sessions and memory files, plus tracked `AGENTS.md` and `README.md` project context docs under the target repo.

Read [Parser Modes](references/parser-modes.md) for source locations when scope is all-history or multi-home, and for Pi evidence interpretation when Pi sessions are in scope. Pi scanning reads only `sessions/**/*.jsonl`; auth, settings, databases, other runtime stores, and subagent private state stay unread.

## Workflow

1. Confirm the requested scope: current repo, named repo, or all local Codex/Claude/Grok/Pi history.
2. Run the bundled parser for structured signals instead of raw-scanning large JSONL files.
3. Separate evidence into:
   - command failures and tool errors
   - interrupted, compacted, or rolled-back turns
   - user corrections and scope rejections
   - approval-gate mistakes
   - memory-recorded failure patterns
   - project docs that are large, duplicated, or workflow-heavy enough to mine
4. Classify each recurring candidate, naming its source evidence, as:
   - update an existing generic skill, or add a new one, when the pattern recurs across repositories or task types
   - add or update a repo-local skill when the pattern depends on repository topology, runtime inventory, local hostnames, or domain-specific operational truth
   - add or update scoped repo docs or code truth for stable operational facts
   - mark extracted memory for cleanup
   - do not promote, which covers one-time runtime snapshots that serve only as evidence
5. Name a repo doc, repo-local skill, code, or generic skill as the durable owner of each recommendation. Recommend concrete target files and validation commands.

## Memory

Mine existing memory to identify missing repo truth, missing skills, stale memory, and cleanup candidates. For each memory-derived finding, decide whether the target repo already owns the durable truth; if so, name the durable target file together with the source memory cleanup action, and recommend removing or shrinking the memory entry after the repo update is verified. List extracted memory entries or task groups as cleanup candidates, cite the repo files that now own the truth, and keep only short pointers when useful for historical lookup. Edit agent memory only on an explicit memory-maintenance request through the active memory workflow; cleanup entries are recommendations.

## Parser

Resolve the skill directory from this file and run the bundled read-only parser for the current repository:

```bash
SKILL_DIR="$(cd "$(dirname "<path to this SKILL.md>")" && pwd)"
python3 "$SKILL_DIR/scripts/extract-session-signals.py" --scope current --repo-root "$(git rev-parse --show-toplevel)"
```

The script accepts only named parameters, and the default scope stays `current`. Use [Parser Modes](references/parser-modes.md) when the task needs all-history scope, multiple homes, JSON output, or skill-usage measurement. Raw examples are off by default; set a positive `--limit` only when bounded session excerpts are required, and treat any excerpt as potentially sensitive because sanitization does not guarantee that arbitrary secrets are removed.

## Output Rules

- Lead with counts and the strongest repeated patterns, and include project context signals by default when a repo root is available.
- Quote short user corrections only when they prove a workflow mistake.
- Treat search no-match exit codes as weak evidence unless followed by user correction.
- Report only steps that completed.
