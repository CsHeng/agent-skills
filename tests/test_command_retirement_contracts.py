from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "check_contracts_command_retirement",
        REPO_ROOT / "scripts/check-contracts.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load scripts/check-contracts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract() -> dict[str, object]:
    with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
        return tomllib.load(handle)


class CommandRetirementContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_checker()

    def test_every_command_has_one_retirement_disposition(self) -> None:
        contract = load_contract()
        retirement = contract["command_retirement"]
        classified = {
            command
            for field in ("absorbed_by_skill", "thin_wrappers", "archive_only")
            for command in retirement[field]
        }
        active = {path.stem for path in (REPO_ROOT / "commands").glob("*.md")}
        archived = {
            path.stem for path in (REPO_ROOT / "archived/commands").glob("*.md")
        }

        self.assertEqual(classified, active | archived)
        self.assertFalse(active & archived)
        self.assertEqual(["check-secrets"], retirement["archive_only"])
        self.assertNotIn(
            "check-secrets",
            {entry["public_id"] for entry in contract["skills"].values()},
        )
        self.assertEqual(
            [],
            self.checker.validate_command_retirement_contract(contract, REPO_ROOT),
        )

    def test_command_archive_is_inert_and_search_suppressed(self) -> None:
        active_root = REPO_ROOT / "commands"
        archive_root = REPO_ROOT / "archived/commands"

        self.assertFalse(any(active_root.glob("*.md")))
        self.assertEqual(12, len(list(archive_root.glob("*.md"))))
        self.assertFalse(any(archive_root.rglob("SKILL.md")))
        self.assertFalse(any(path.is_symlink() for path in archive_root.rglob("*")))
        self.assertEqual(
            "commands/",
            (REPO_ROOT / "archived/.ignore").read_text(encoding="utf-8").strip(),
        )

    def test_provider_adapters_remain_active(self) -> None:
        retained_paths = (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".codex-plugin/plugin.json",
            ".codex-marketplace/.agents/plugins/marketplace.json",
            ".codex-marketplace/plugins/coding",
            "install.sh",
            "install-codex.sh",
            "scripts/install.sh",
            "hooks/post-edit-check.sh",
        )
        for relative_path in retained_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).exists())

    def test_active_truth_does_not_publish_retired_commands(self) -> None:
        active_truth = (
            "README.md",
            "AGENTS.md",
            "docs/quickstart.md",
            "docs/architecture/install-surface.md",
            "docs/architecture/maintenance-contract.md",
            "docs/architecture/workflow-orchestration.md",
        )
        retired_entries = tuple(
            f"`/{public_id}`"
            for public_id in (
                "analyze-project",
                "design-change",
                "plan-change",
                "implement-change",
                "review-change",
                "sync-truth",
                "close-change",
            )
        )
        for relative_path in active_truth:
            with self.subTest(path=relative_path):
                content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertNotIn("commands/", content)
                for retired_entry in retired_entries:
                    self.assertNotIn(retired_entry, content)

    def test_absorbed_workflows_own_their_runner_semantics(self) -> None:
        expected_runners = {
            "close-change": "close-runner.sh",
            "design-change": "design-runner.sh",
            "implement-change": "execute-runner.sh",
            "plan-change": "plan-runner.sh",
            "review-change": "design-runner.sh",
            "sync-truth": "truth-sync-runner.sh",
        }
        for public_id, runner in expected_runners.items():
            with self.subTest(skill=public_id):
                skill = (
                    REPO_ROOT
                    / "src/skills/workflows"
                    / public_id
                    / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(f"scripts/harness/{runner}", skill)

    def test_active_command_adapters_use_owner_local_runners(self) -> None:
        command_root = REPO_ROOT / "commands"
        if not command_root.is_dir():
            return

        expected_paths = {
            "close-change.md": "${CLAUDE_PLUGIN_ROOT}/skills/close-change/scripts/harness/close-runner.sh",
            "design-change.md": "${CLAUDE_PLUGIN_ROOT}/skills/design-change/scripts/harness/design-runner.sh",
            "implement-change.md": "${CLAUDE_PLUGIN_ROOT}/skills/implement-change/scripts/harness/execute-runner.sh",
            "plan-change.md": "${CLAUDE_PLUGIN_ROOT}/skills/plan-change/scripts/harness/plan-runner.sh",
            "sync-truth.md": "${CLAUDE_PLUGIN_ROOT}/skills/sync-truth/scripts/harness/truth-sync-runner.sh",
        }
        for command_name, runner_path in expected_paths.items():
            with self.subTest(command=command_name):
                command = (command_root / command_name).read_text(encoding="utf-8")
                self.assertIn(runner_path, command)
                self.assertNotIn("skills/_harness-libs", command)

    def test_command_adapter_runners_execute_from_unrelated_directory(self) -> None:
        runners = {
            "close-change": ("close-runner.sh", "close"),
            "design-change": ("design-runner.sh", "clarify"),
            "implement-change": ("execute-runner.sh", "implement-serial"),
            "plan-change": ("plan-runner.sh", "plan"),
            "sync-truth": ("truth-sync-runner.sh", "truth-sync"),
        }
        env = os.environ | {"CLAUDE_PLUGIN_ROOT": str(REPO_ROOT)}
        with tempfile.TemporaryDirectory() as unrelated_cwd:
            for public_id, (runner_name, expected_phase) in runners.items():
                with self.subTest(command=public_id):
                    runner = (
                        Path(env["CLAUDE_PLUGIN_ROOT"])
                        / "skills"
                        / public_id
                        / "scripts/harness"
                        / runner_name
                    )
                    result = subprocess.run(
                        ["bash", str(runner), "entry-phase"],
                        cwd=unrelated_cwd,
                        check=True,
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    self.assertEqual(expected_phase, result.stdout.strip())

    def test_smart_commit_already_owns_target_repository_binding(self) -> None:
        skill = (
            REPO_ROOT / "src/skills/git/smart-commit/SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn('TARGET_REPO="$(git -C "$INVOCATION_CWD"', skill)
        self.assertIn('git -C "$TARGET_REPO"', skill)


if __name__ == "__main__":
    unittest.main()
