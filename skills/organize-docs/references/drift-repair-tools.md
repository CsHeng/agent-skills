# Documentation Checks And Repair

Use these commands when the affected documentation boundaries need checking or when existing prose drift needs an authorized mechanical repair. They are not a routine restyling sequence for new or otherwise conforming prose.

Resolve the installed skill directory and target repository before running the selected check:

```bash
SKILL_DIR="$(cd "$(dirname "<path to this SKILL.md>")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
```

## Documentation Boundary Checks

When documentation truth boundaries change, run the bundled checker from the target repository:

```bash
cd "$REPO_ROOT"
bash "$SKILL_DIR/scripts/check-doc-boundaries.sh"
```

The checker also calls the bundled normalizer in `check` mode. Required boundary checks retain their declared scan scope; a smaller repair scope is not permission to hide findings or remove assertions.

For a repository with a machine-readable documentation manifest:

```bash
python3 "$SKILL_DIR/scripts/check-documentation-layout.py" --root "$REPO_ROOT" --manifest testing/documentation-layout.json
```

- The manifest declares roots and material classes, required indexes, stage and archive shapes, link scope, relocation manifests, and named exceptions. Use the repository's actual manifest path. Relocation checks verify old/new path relationships and created-file existence; they do not pin document contents.
- Capabilities are `declared-roots`, `stage-shape`, `archive-shape`, `root-shape`, `index-closure`, `link-resolution`, and `migration-conservation`; the manifest maps them to its gate identifiers.
- This check is advisory. Keep the manifest as declaration data, do not wire the checker into repository tasks, tests, or tool dependencies, and do not vendor a checker copy.
- Repair violations or declare a justified exception. Do not hide findings by narrowing the check. Unresolved links in archived and staged scopes are named exemptions; useful historical bodies need not be rewritten to satisfy a gate, and obsolete material may be removed within the authorized cleanup.
- Exit status is `0` on pass, `1` on undeclared violations, and `2` on an unusable manifest or missing checker.

## Repairing Existing Prose Wrapping

For a few affected lines, edit them directly. For a mechanical cleanup, use `scripts/normalize-markdown-prose.py` rather than writing a temporary parser. It scans Git-visible Markdown, including tracked and untracked files, while excluding ignored/cache material and symlinks.

Set the repair exclusions explicitly. The example below excludes only `archived`; add every unrelated file or subtree needed to bound the repair. Each `--exclude` is a literal repository-relative prefix, not a glob. If exclusions cannot safely express the authorized scope, make targeted edits instead.

```bash
REPAIR_SCOPE=(--exclude archived)
python3 "$SKILL_DIR/scripts/normalize-markdown-prose.py" --root "$REPO_ROOT" "${REPAIR_SCOPE[@]}" --mode count
python3 "$SKILL_DIR/scripts/normalize-markdown-prose.py" --root "$REPO_ROOT" "${REPAIR_SCOPE[@]}" --mode preview
```

`count` reports scope; `preview` shows bounded continuation pairs. Before writing, confirm that all affected files are authorized; raise the preview's `--limit` when needed to inspect the complete candidate set. Only then run the following commands with the same scope arguments:

```bash
python3 "$SKILL_DIR/scripts/normalize-markdown-prose.py" --root "$REPO_ROOT" "${REPAIR_SCOPE[@]}" --mode write
python3 "$SKILL_DIR/scripts/normalize-markdown-prose.py" --root "$REPO_ROOT" "${REPAIR_SCOPE[@]}" --mode check
```

`write` removes continuation newlines and aborts if non-whitespace prose content or Markdown structure changes. `check` detects remaining wrapped paragraphs, list items, or blockquotes. The normalizer preserves fenced and indented code, frontmatter, tables, headings, reference definitions, HTML-only lines, thematic breaks, and intentional hard breaks. If a joined line contains unrelated claims, split it into real paragraphs or list items at semantic boundaries, not at a fixed column width.

Use path exclusions to leave retained originals outside a mechanical prose repair. No content digest or immutable-document manifest is needed.
