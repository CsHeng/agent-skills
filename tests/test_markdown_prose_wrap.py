from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills/organize-docs/scripts/normalize-markdown-prose.py"
)
BOUNDARY_CHECKER = (
    REPO_ROOT
    / "src/skills/disciplines/organize-docs/scripts/check-doc-boundaries.sh"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "normalize_markdown_prose", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MarkdownProseWrapTests(unittest.TestCase):
    def test_unwraps_paragraph_and_list_item_continuations(self) -> None:
        module = load_module()
        source = """# Title

This is one natural
paragraph even when the second line starts uppercase.

- First list item
  continues here.
- Second list item.

1. Ordered item
   continues too.
"""
        expected = """# Title

This is one natural paragraph even when the second line starts uppercase.

- First list item continues here.
- Second list item.

1. Ordered item continues too.
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, expected)
        self.assertEqual(result.join_count, 3)

    def test_preserves_markdown_structures_and_explicit_breaks(self) -> None:
        module = load_module()
        source = """---
description: >
  Keep frontmatter
  exactly as written.
---

Setext heading
==============

| Name | Value |
| --- | --- |
| a | b |

```text
wrapped-looking
code stays
```

> ```text
> wrapped-looking
> quoted code stays
> ```

> # Quoted heading
>
> Quoted setext heading
> ---------------------
>
> | Name | Value |
> | --- | --- |
> | a | b |
>
> [quoted-ref]: https://example.com/
>
>     quoted indented
>     code stays

```markdown
Outer example.
```yaml
- nested
  code stays
```
```

Keep this explicit break.\x20\x20
Start a separate rendered line.

- Parent
   - Nested child
   - Another child

  - Keygen:
    ```bash
    echo code
    ```

    indented code stays

- confirmation:
  - id: C0
    question: keep this structured

> **Date:** 2026-01-01
> **Scope:** keep each field searchable
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, source)
        self.assertEqual(result.join_count, 0)

    def test_preserves_toml_frontmatter_blocks(self) -> None:
        module = load_module()
        source = '''+++
artifact_kind = "plan"
contract_version = 3

[[tasks]]
task_id = "PDR-010"
+++
# Plan

One paragraph
continues here.
'''

        result = module.transform_markdown(source)

        self.assertIn('[[tasks]]\ntask_id = "PDR-010"\n+++', result.text)
        self.assertIn("One paragraph continues here.", result.text)
        self.assertEqual(result.join_count, 1)

    def test_unwraps_blockquotes_and_cjk_without_inserting_cjk_space(self) -> None:
        module = load_module()
        source = """> This quoted paragraph
> continues here.

这是同一个
自然段。
"""
        expected = """> This quoted paragraph continues here.

这是同一个自然段。
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, expected)
        self.assertEqual(result.join_count, 2)

    def test_treats_unclosed_frontmatter_marker_as_thematic_break(self) -> None:
        module = load_module()
        source = """---
One wrapped
paragraph.
"""
        expected = """---
One wrapped paragraph.
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, expected)
        self.assertEqual(result.join_count, 1)

    def test_preserves_empty_metadata_fields_and_following_values(self) -> None:
        module = load_module()
        source = """task_id: `P01-platform-contracts`
depends_on:

- `P00-preflight`

Plan:
`docs/plans/example.md`

depends_on:
P01,P02
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, source)
        self.assertEqual(result.join_count, 0)

    def test_unwraps_semantic_looking_continuation_in_ordinary_list_item(self) -> None:
        module = load_module()
        source = """- Review that every stack is classified as one
  of: migrated target, approved holdback,
  or explicit defer.
"""
        expected = (
            "- Review that every stack is classified as one of: migrated target, "
            "approved holdback, or explicit defer.\n"
        )

        result = module.transform_markdown(source)

        self.assertEqual(result.text, expected)
        self.assertEqual(result.join_count, 2)

    def test_unwraps_empty_key_looking_prose_continuation(self) -> None:
        module = load_module()
        source = """Candidate creation is
guarded by:
"""
        expected = """Candidate creation is guarded by:
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, expected)
        self.assertEqual(result.join_count, 1)

    def test_preserves_empty_key_looking_label_after_list(self) -> None:
        module = load_module()
        source = """- Completed the stable truth sync.
Follow-up:

- Retire the old runtime.
"""

        result = module.transform_markdown(source)

        self.assertEqual(result.text, source)
        self.assertEqual(result.join_count, 0)

    def test_git_visible_scope_includes_untracked_and_skips_symlinks(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            tracked = root / "tracked.md"
            untracked = root / "untracked.md"
            ignored = root / "ignored.md"
            linked = root / "linked.md"
            tracked.write_text("Tracked.\n", encoding="utf-8")
            untracked.write_text("Untracked.\n", encoding="utf-8")
            ignored.write_text("Ignored.\n", encoding="utf-8")
            (root / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
            linked.symlink_to(tracked.name)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    "tracked.md",
                    "linked.md",
                    ".gitignore",
                ],
                check=True,
            )

            discovered = {
                candidate.relative_to(root.resolve())
                for candidate in module.discover_markdown_files(root)
            }

        self.assertEqual(discovered, {Path("tracked.md"), Path("untracked.md")})

    def test_cli_check_and_write_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            markdown_file = root / "README.md"
            markdown_file.write_text("One wrapped\nparagraph.\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)

            check_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--root",
                    str(root),
                    "--mode",
                    "check",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check_result.returncode, 1)
            self.assertIn("join_count=1", check_result.stdout)

            write_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--root",
                    str(root),
                    "--mode",
                    "write",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(write_result.returncode, 0, write_result.stderr)
            self.assertEqual(
                markdown_file.read_text(encoding="utf-8"),
                "One wrapped paragraph.\n",
            )

    def test_immutable_manifest_preserves_only_pinned_legacy_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            history = root / "docs/plans/history.md"
            history.parent.mkdir(parents=True)
            history.write_text("Legacy wrapped\nparagraph.\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text("Mutable wrapped\nparagraph.\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "docs/plans/history.md", "README.md"],
                check=True,
            )
            manifest = root / "immutable.toml"
            manifest.write_text(
                "version = 1\n\n[[exceptions]]\n"
                'path = "docs/plans/history.md"\n'
                f'sha256 = "{hashlib.sha256(history.read_bytes()).hexdigest()}"\n',
                encoding="utf-8",
            )

            write_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--root",
                    str(root),
                    "--immutable-manifest",
                    str(manifest),
                    "--mode",
                    "write",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(write_result.returncode, 0, write_result.stderr)
            self.assertEqual(history.read_text(encoding="utf-8"), "Legacy wrapped\nparagraph.\n")
            self.assertEqual(readme.read_text(encoding="utf-8"), "Mutable wrapped paragraph.\n")

            check_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--root",
                    str(root),
                    "--immutable-manifest",
                    str(manifest),
                    "--mode",
                    "check",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check_result.returncode, 0, check_result.stderr)
            self.assertIn("join_count=0", check_result.stdout)

    def test_immutable_manifest_rejects_unpinned_or_invalid_exceptions(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            history = root / "docs/plans/history.md"
            history.parent.mkdir(parents=True)
            history.write_text("Legacy wrapped\nparagraph.\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "docs/plans/history.md"], check=True)
            manifest = root / "immutable.toml"
            manifest.write_text(
                "version = 1\n\n[[exceptions]]\n"
                'path = "docs/plans/*.md"\n'
                'sha256 = "not-a-digest"\n',
                encoding="utf-8",
            )

            with self.assertRaises(module.MarkdownNormalizationError):
                module.load_immutable_manifest(root, manifest)

    def test_repository_boundary_checker_honors_immutable_manifest(self) -> None:
        if os.environ.get("STANDALONE_CHECK_ACTIVE") == "1":
            self.skipTest("stage history is intentionally absent from standalone copies")
        result = subprocess.run(
            ["bash", str(BOUNDARY_CHECKER)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("join_count=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
