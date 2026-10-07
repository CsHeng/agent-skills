#!/usr/bin/env python3
"""Prove the bundled documentation layout checker rejects planted violations.

Each case builds a synthetic repository tree, writes a manifest, runs the
organize-docs skill's own layout checker, and asserts the expected rule fires.
The same fixtures prove that a declared exception is reported as exempt instead
of silently skipped, and that a clean declared tree passes. The checker is
skill-owned: these cases live with the skill and no consumer repository wires
the checker into its own tasks or tests.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "skills" / "organize-docs" / "scripts" / "check-documentation-layout.py"

BASE_MANIFEST: dict[str, object] = {
    "schema": "organize-docs/documentation-layout@1",
    "version": 1,
    "repository": "fixture",
    "documentationExtensions": [".md"],
    "classes": [
        {"name": "documentation-container"},
        {"name": "stable"},
        {"name": "staged-design"},
        {"name": "stage"},
        {"name": "archived"},
        {"name": "research-evidence"},
        {"name": "upstream-vendored"},
    ],
    "migrationManifestNames": ["migration-manifest.json"],
    "migrationManifestRoots": ["docs/plans"],
    "scannedRoots": ["docs"],
    "undeclaredRootDepth": 3,
    "requiredFiles": ["README.md", "docs/README.md"],
    "checks": [
        {"id": "G1", "capabilities": ["declared-roots"]},
        {
            "id": "G2",
            "capabilities": [
                "stage-shape",
                "archive-shape",
                "root-shape",
                "migration-conservation",
            ],
        },
        {"id": "G3", "capabilities": ["index-closure"]},
        {"id": "G4", "capabilities": ["link-resolution"]},
    ],
    "roots": [
        {
            "path": "docs",
            "class": "documentation-container",
            "containerRoot": True,
            "index": "README.md",
            "closure": False,
            "linkScope": "current",
        },
        {
            "path": "docs/architecture",
            "class": "stable",
            "index": "README.md",
            "closure": True,
            "linkScope": "current",
        },
        {
            "path": "docs/designs",
            "class": "staged-design",
            "index": "README.md",
            "closure": True,
            "linkScope": "current",
            "filePattern": "^\\d{4}-\\d{2}-\\d{2}-[a-z0-9][a-z0-9-]*\\.md$",
            "filePatternAllow": ["README.md"],
        },
        {
            "path": "docs/plans",
            "class": "stage",
            "index": "README.md",
            "closure": True,
            "closureIndexes": ["plan.md"],
            "linkScope": "staged",
            "frontmatterLinkFields": ["design_reference"],
        },
        {
            "path": "docs/archive",
            "class": "archived",
            "index": "README.md",
            "closure": True,
            "linkScope": "archived",
        },
        {
            "path": "research",
            "class": "research-evidence",
            "index": "README.md",
            "closure": False,
            "subdirectoryIndexes": {"maxDepth": 1, "index": "README.md"},
            "linkScope": "current",
        },
    ],
    "stage": {
        "root": "docs/plans",
        "domainSegment": True,
        "domains": ["coordination", "network"],
        "bundleParent": "changes",
        "planFile": "plan.md",
        "planPattern": "^[a-z0-9][a-z0-9-]*-plan\\.md$",
        "recordsDir": "records",
        "recordExtensions": [".json"],
        "bundleDirPattern": "^\\d{4}-\\d{2}-\\d{2}-[a-z0-9][a-z0-9-]*$",
        "optionalMembers": ["verification.md", "truth-sync.md", "close.md", "notes.md"],
        "flatFileExceptions": ["README.md"],
        "migrationManifest": "records/migration-manifest.json",
        "requireMigrationManifest": False,
        "linkExceptionBasis": "staged candidate work",
    },
    "archive": {
        "root": "docs/archive",
        "classSubroots": ["decisions", "designs"],
        "allowRootFiles": ["README.md"],
        "namingExceptions": [],
        "linkExceptions": [{"path": "docs/archive", "reason": "archived bodies are never rewritten"}],
        "unresolvedPointers": [
            {
                "from": "docs/archive/decisions/AD-DRONE-SAMPLE-900.md",
                "to": "docs/archive/decisions/missing.md",
                "reason": "archived body keeps its historical pointer; the owning index carries the replacement note",
            }
        ],
    },
    "exceptions": {
        "undeclaredDocumentationRoots": [],
        "closureExempt": [],
        "subdirectoryIndexExempt": [],
        "unresolvableLinks": [],
        "declaredPins": [],
        "retiredNames": [],
    },
}

CLEAN_TREE = {
    "README.md": "# Fixture\n",
    "docs/README.md": "# Documentation\n\n- [architecture](architecture/README.md)\n- [designs](designs/README.md)\n- [plans](plans/README.md)\n- [archive](archive/README.md)\n- [research](../research/README.md)\n",
    "docs/architecture/README.md": "# Architecture\n\n- [boundary](boundary.md)\n",
    "docs/architecture/boundary.md": "# Boundary\n",
    "docs/designs/README.md": "# Designs\n\n- [sample](2026-01-01-sample.md)\n",
    "docs/designs/2026-01-01-sample.md": "# Sample design\n",
    "docs/plans/README.md": "# Plans\n\n- [coordination](coordination/README.md)\n- [network](network/README.md)\n",
    "docs/plans/coordination/README.md": "# Coordination\n\n| Bundle | Status |\n| --- | --- |\n| [2026-01-01-sample](changes/2026-01-01-sample/plan.md) | retired |\n",
    "docs/plans/coordination/changes/2026-01-01-sample/plan.md": "# Sample plan\n\n- [result](records/execution-result.json)\n",
    "docs/plans/coordination/changes/2026-01-01-sample/records/execution-result.json": "{\"outcome\": \"pass\"}\n",
    "docs/plans/network/README.md": "# Network\n\nNo active bundle.\n",
    "docs/archive/README.md": "# Archive\n\n- [decisions](decisions/README.md)\n- [designs](designs/README.md)\n",
    "docs/archive/decisions/README.md": "# Archived decisions\n\n- [sample](AD-DRONE-SAMPLE-900.md)\n",
    "docs/archive/decisions/AD-DRONE-SAMPLE-900.md": "# Sample archived decision\n",
    "docs/archive/designs/README.md": "# Archived designs\n\n- [old](2025-01-01-old.md)\n",
    "docs/archive/designs/2025-01-01-old.md": "# Old design\n",
    "research/README.md": "# Research\n\n- [providers](providers/README.md)\n",
    "research/providers/README.md": "# Providers\n\n- [sample](sample.md)\n",
    "research/providers/sample.md": "# Sample evidence\n",
}


class GateFixture(unittest.TestCase):
    """Run the installed checker against synthetic trees."""

    def setUp(self) -> None:
        self.assertTrue(CHECKER.is_file(), f"missing checker {CHECKER}")
        self.workspace = Path(tempfile.mkdtemp(prefix="doc-layout-gates-"))
        self.addCleanup(shutil.rmtree, self.workspace, True)

    def build(self, extra: dict[str, str] | None = None, manifest_patch: dict | None = None) -> Path:
        tree = dict(CLEAN_TREE)
        tree.update(extra or {})
        root = self.workspace / f"tree-{len(list(self.workspace.iterdir()))}"
        (root / ".git").mkdir(parents=True, exist_ok=True)
        (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        for relative, body in tree.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        manifest = json.loads(json.dumps(BASE_MANIFEST))
        if manifest_patch:
            _deep_update(manifest, manifest_patch)
        manifest_path = root / "testing" / "documentation-layout.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return root

    def run_checker(self, root: Path) -> tuple[int, str]:
        result = subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                "--root",
                str(root),
                "--manifest",
                str(root / "testing" / "documentation-layout.json"),
                "--limit",
                "200",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout + result.stderr

    def assertRule(self, root: Path, rule: str) -> str:
        code, output = self.run_checker(root)
        self.assertEqual(code, 1, f"expected a violation for {rule}; output:\n{output}")
        self.assertIn(f"[{rule}]", output, f"expected rule {rule}; output:\n{output}")
        return output

    def assertExempt(self, root: Path, rule: str) -> str:
        code, output = self.run_checker(root)
        self.assertIn(rule, output, f"expected exempt rule {rule}; output:\n{output}")
        return output

    def test_clean_declared_tree_passes(self) -> None:
        root = self.build()
        code, output = self.run_checker(root)
        self.assertEqual(code, 0, f"clean fixture must pass; output:\n{output}")
        self.assertIn("documentation layout: pass", output)

    def test_g1_rejects_undeclared_material_class(self) -> None:
        root = self.build(
            manifest_patch={
                "roots": [
                    {
                        "path": "docs/architecture",
                        "class": "invented-class",
                        "index": "README.md",
                        "closure": True,
                        "linkScope": "current",
                    }
                ]
            }
        )
        # The patch replaces the whole roots list, so the remaining undeclared
        # roots also fire; the class rule is the one under test.
        self.assertRule(root, "undeclared-material-class")

    def test_g1_rejects_undeclared_markdown_root(self) -> None:
        root = self.build({"docs/extra/notes.md": "# Notes\n"})
        self.assertRule(root, "undeclared-documentation-root")

    def test_g1_rejects_missing_declared_index(self) -> None:
        root = self.build()
        (root / "docs" / "designs" / "README.md").unlink()
        self.assertRule(root, "declared-index-missing")

    def test_g1_rejects_missing_required_file(self) -> None:
        root = self.build()
        (root / "README.md").unlink()
        self.assertRule(root, "required-file-missing")

    def test_g2_rejects_machine_record_in_a_document_root(self) -> None:
        root = self.build(
            {"docs/plans/coordination/changes/2026-01-01-sample/approval.json": "{}\n"}
        )
        self.assertRule(root, "stage-record-placement")

    def test_g2_rejects_flat_stage_file(self) -> None:
        root = self.build({"docs/plans/loose-note.md": "# Loose\n"})
        self.assertRule(root, "stage-flat-file")

    def test_g2_rejects_design_body_inside_a_bundle(self) -> None:
        root = self.build(
            {"docs/plans/coordination/changes/2026-01-01-sample/design.md": "# Design\n"}
        )
        self.assertRule(root, "stage-undeclared-member")

    def test_g2_rejects_undeclared_domain(self) -> None:
        root = self.build({"docs/plans/commerce/README.md": "# Commerce\n"})
        self.assertRule(root, "stage-undeclared-domain")

    def test_g2_rejects_bundle_without_a_plan(self) -> None:
        root = self.build(
            {"docs/plans/network/changes/2026-02-02-orphan/notes.md": "# Notes\n"}
        )
        self.assertRule(root, "stage-bundle-plan-missing")

    def test_g2_rejects_misnamed_bundle(self) -> None:
        root = self.build(
            {"docs/plans/network/changes/sample/plan.md": "# Plan\n"}
        )
        self.assertRule(root, "stage-bundle-name")

    def test_g2_rejects_loose_archive_root_file(self) -> None:
        root = self.build({"docs/archive/loose.md": "# Loose archive file\n"})
        self.assertRule(root, "archive-loose-file")

    def test_g2_rejects_undeclared_archive_class(self) -> None:
        root = self.build({"docs/archive/first-party/README.md": "# First party\n"})
        self.assertRule(root, "archive-undeclared-class")

    def test_g2_rejects_design_outside_the_designs_pattern(self) -> None:
        root = self.build({"docs/designs/not-a-design.md": "# Misplaced\n"})
        self.assertRule(root, "root-file-pattern")

    def test_g2_rejects_surviving_migration_source(self) -> None:
        bundle = "docs/plans/coordination/changes/2026-01-01-sample"
        plan_body = CLEAN_TREE[f"{bundle}/plan.md"]
        root = self.build(
            {
                "docs/plans/changes/2026-01-01-sample-plan.md": plan_body,
                f"{bundle}/records/migration-manifest.json": json.dumps(
                    {
                        "moved": [
                            {
                                "from": "docs/plans/changes/2026-01-01-sample-plan.md",
                                "to": f"{bundle}/plan.md",
                            }
                        ]
                    }
                )
                + "\n",
            }
        )
        self.assertRule(root, "migration-source-survives")

    def test_g2_accepts_a_complete_migration_manifest(self) -> None:
        bundle = "docs/plans/coordination/changes/2026-01-01-sample"
        root = self.build(
            {
                f"{bundle}/records/migration-manifest.json": json.dumps(
                    {
                        "moved": [
                            {
                                "from": "docs/plans/changes/2026-01-01-sample-plan.md",
                                "to": f"{bundle}/plan.md",
                            }
                        ]
                    }
                )
                + "\n",
            }
        )
        index = root / "docs/plans/coordination/README.md"
        index.write_text(index.read_text() + "\n- [migration](changes/2026-01-01-sample/records/migration-manifest.json)\n")
        code, output = self.run_checker(root)
        self.assertEqual(code, 0, f"complete manifest must pass; output:\n{output}")
        self.assertIn("count migrationPairs: 1", output)

    def test_g3_migration_accounting_does_not_replace_index_links(self) -> None:
        bundle = "docs/plans/coordination/changes/2026-01-01-sample"
        record = f"{bundle}/records/orphan.json"
        root = self.build({
            record: "{}\n",
            f"{bundle}/records/migration-manifest.json": json.dumps({
                "moved": [{"from": "old.json", "to": record}]
            }) + "\n",
        })
        output = self.assertRule(root, "index-closure")
        self.assertIn(f"[index-closure] {record}", output)

    def test_g3_rejects_unreferenced_non_index_file(self) -> None:
        root = self.build({"docs/architecture/orphan.md": "# Orphan\n"})
        self.assertRule(root, "index-closure")

    def test_g3_rejects_missing_namespace_index(self) -> None:
        root = self.build({"research/gaps/evidence.md": "# Evidence\n"})
        self.assertRule(root, "namespace-index-missing")

    def test_g3_accepts_a_declared_closure_exception(self) -> None:
        root = self.build(
            {"docs/architecture/orphan.md": "# Orphan\n"},
            {
                "exceptions": {
                    "closureExempt": [
                        {"path": "docs/architecture/orphan.md", "reason": "diagram owned by a decision"}
                    ]
                }
            },
        )
        output = self.assertExempt(root, "index-closure-exempt")
        code, _ = self.run_checker(root)
        self.assertEqual(code, 0, f"declared closure exception must exempt; output:\n{output}")

    def test_g4_resolves_declared_frontmatter_paths_after_relocation(self) -> None:
        plan = "docs/plans/coordination/changes/2026-01-01-sample/plan.md"
        for value in (
            "../../../../designs/2026-01-01-sample.md",
            "'../../../../designs/2026-01-01-sample.md' # design binding",
            '"../../../../designs/2026-01-01-sample.md"',
        ):
            with self.subTest(value=value):
                root = self.build({plan: f"---\ndesign_reference: {value}\n---\n" + CLEAN_TREE[plan]})
                code, output = self.run_checker(root)
                self.assertEqual(code, 0, output)
        root = self.build({plan: "---\ndesign_reference: ../../../docs/designs/2026-01-01-sample.md\n---\n" + CLEAN_TREE[plan]})
        self.assertRule(root, "frontmatter-link-unresolved")

    def test_g4_rejects_unresolved_current_link(self) -> None:
        root = self.build(
            {"docs/architecture/boundary.md": "# Boundary\n\n- [missing](missing.md)\n"}
        )
        self.assertRule(root, "link-unresolved")

    def test_g4_exempts_a_declared_archived_pointer(self) -> None:
        root = self.build(
            {
                "docs/archive/decisions/AD-DRONE-SAMPLE-900.md": "# Sample archived decision\n\n- [missing](missing.md)\n"
            }
        )
        code, output = self.run_checker(root)
        self.assertEqual(code, 0, f"a declared archived pointer must exempt; output:\n{output}")
        self.assertIn("link-unresolved-archived", output)

    def test_g4_rejects_an_undeclared_archived_pointer(self) -> None:
        root = self.build(
            {
                "docs/archive/decisions/AD-DRONE-SAMPLE-900.md": "# Sample archived decision\n\n- [other](other.md)\n"
            }
        )
        self.assertRule(root, "link-unresolved-archived-undeclared")

    def test_g4_rejects_undeclared_sibling_pin(self) -> None:
        root = self.build(
            {"docs/architecture/boundary.md": "# Boundary\n\n- [sibling](../../../backend/docs/README.md)\n"}
        )
        self.assertRule(root, "link-escapes-root")

    def test_g4_exempts_a_declared_sibling_pin(self) -> None:
        root = self.build(
            {"docs/architecture/boundary.md": "# Boundary\n\n- [sibling](../../../backend/docs/README.md)\n"},
            {
                "exceptions": {
                    "declaredPins": [
                        {
                            "path": "docs/architecture/boundary.md",
                            "class": "contract-input",
                            "reason": "named by the accepting decision",
                        }
                    ]
                }
            },
        )
        code, output = self.run_checker(root)
        self.assertEqual(code, 0, f"declared pin must exempt; output:\n{output}")
        self.assertIn("link-escapes-root-declared", output)

    def test_g4_reports_staged_scope_separately(self) -> None:
        bundle = "docs/plans/coordination/changes/2026-01-01-sample"
        root = self.build(
            {
                f"{bundle}/plan.md": "# Sample plan\n\n- [result](records/execution-result.json)\n- [pending](../../../../architecture/documentation-layout.md)\n"
            }
        )
        code, output = self.run_checker(root)
        self.assertEqual(code, 0, f"staged scope must be reported, not failed; output:\n{output}")
        self.assertIn("link-unresolved-staged", output)

    def test_undeclared_exception_does_not_exempt(self) -> None:
        root = self.build(
            {"docs/architecture/orphan.md": "# Orphan\n"},
            {
                "exceptions": {
                    "closureExempt": [
                        {"path": "docs/architecture/other.md", "reason": "does not match the orphan"}
                    ]
                }
            },
        )
        self.assertRule(root, "index-closure")


def _deep_update(target: dict, patch: dict) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False, verbosity=2).result.wasSuccessful() else 1)
