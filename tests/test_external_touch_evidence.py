from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "src/runtime/harness/external-touch-evidence.py"
SHA256_ZERO = "0" * 64
SHA256_ONE = "1" * 64


def load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "external_touch_evidence", HELPER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load helper: {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExternalTouchBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.helper = load_helper()

    def test_capture_baseline_records_only_exact_file_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            target = fixture_root / "target.toml"
            target.write_text("enabled = true\n", encoding="utf-8")
            target.chmod(0o600)

            baseline = self.helper.capture_baseline(
                repo_root=REPO_ROOT,
                refs=[str(target)],
                run_id="run-1",
                task_id="EAT-TEST",
                design_sha256=SHA256_ZERO,
                plan_sha256=SHA256_ONE,
            )

            self.assertEqual(1, baseline["schema_version"])
            self.assertEqual("run-1", baseline["run_id"])
            self.assertEqual("EAT-TEST", baseline["task_id"])
            self.assertEqual([str(target)], [item["ref"] for item in baseline["refs"]])
            evidence = baseline["refs"][0]
            self.assertEqual("regular", evidence["file_type"])
            self.assertEqual("0600", evidence["mode"])
            self.assertEqual(os.getuid(), evidence["uid"])
            self.assertEqual(1, evidence["st_nlink"])
            self.assertEqual(target.stat().st_size, evidence["size"])
            self.assertEqual(64, len(evidence["sha256"]))
            self.assertNotIn("enabled = true", repr(baseline))

    def test_capture_baseline_rejects_symlink_hardlink_and_repository_overlap(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            symlink = fixture_root / "alias.toml"
            symlink.symlink_to(target)
            hardlink = fixture_root / "hardlink.toml"
            os.link(target, hardlink)

            for rejected_ref, expected_code in (
                (str(symlink), "external_touch_noncanonical_path"),
                (str(target), "external_touch_hardlink_rejected"),
                (
                    str((REPO_ROOT / "README.md").resolve()),
                    "external_touch_repository_overlap",
                ),
            ):
                with (
                    self.subTest(ref=rejected_ref),
                    self.assertRaises(self.helper.ExternalTouchError) as caught,
                ):
                    self.helper.capture_baseline(
                        repo_root=REPO_ROOT,
                        refs=[rejected_ref],
                        run_id="run-1",
                        task_id="EAT-TEST",
                        design_sha256=SHA256_ZERO,
                        plan_sha256=SHA256_ONE,
                    )
                self.assertEqual(expected_code, caught.exception.code)


class ExternalTouchMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.helper = load_helper()

    def _baseline(self, target: Path) -> dict[str, Any]:
        return self.helper.capture_baseline(
            repo_root=REPO_ROOT,
            refs=[str(target)],
            run_id="run-1",
            task_id="EAT-TEST",
            design_sha256=SHA256_ZERO,
            plan_sha256=SHA256_ONE,
        )

    def test_apply_and_repair_form_a_baseline_rooted_intent_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            run_dir = fixture_root / "run"
            run_dir.mkdir(mode=0o700)
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            target.chmod(0o600)
            baseline = self._baseline(target)
            original_inode = target.stat().st_ino

            first_source = fixture_root / "first.toml"
            first_source.write_text("value = 2\n", encoding="utf-8")
            first_stage = self.helper.stage_payload(
                run_dir=run_dir,
                intent_id="intent-1",
                source_file=first_source,
            )
            self.assertEqual("0600", first_stage["mode"])
            self.assertNotIn("value = 2", repr(first_stage))
            first_prepared = self.helper.prepare_intent(
                repo_root=REPO_ROOT,
                baseline=baseline,
                intents=[],
                ref=str(target),
                intent_id="intent-1",
                staged_payload=first_stage,
            )
            self.assertEqual(1, first_prepared["sequence"])
            self.assertEqual("prepared", first_prepared["state"])
            self.assertEqual(
                baseline["refs"][0]["sha256"], first_prepared["parent"]["sha256"]
            )

            first_applied = self.helper.apply_and_cleanup_intent(
                repo_root=REPO_ROOT, intent=first_prepared
            )
            self.assertEqual("applied", first_applied["state"])
            self.assertEqual("applied_now", first_applied["replay_state"])
            self.assertEqual("value = 2\n", target.read_text(encoding="utf-8"))
            self.assertNotEqual(original_inode, target.stat().st_ino)
            self.assertEqual("completed", first_applied["cleanup"]["state"])
            self.assertFalse(Path(first_stage["path"]).exists())

            second_source = fixture_root / "second.toml"
            second_source.write_text("value = 3\n", encoding="utf-8")
            second_stage = self.helper.stage_payload(
                run_dir=run_dir,
                intent_id="intent-2",
                source_file=second_source,
            )
            second_prepared = self.helper.prepare_intent(
                repo_root=REPO_ROOT,
                baseline=baseline,
                intents=[first_applied],
                ref=str(target),
                intent_id="intent-2",
                staged_payload=second_stage,
            )
            self.assertEqual(2, second_prepared["sequence"])
            self.assertEqual(
                first_applied["after"]["sha256"],
                second_prepared["parent"]["sha256"],
            )
            second_applied = self.helper.apply_and_cleanup_intent(
                repo_root=REPO_ROOT, intent=second_prepared
            )

            manifest = self.helper.compare_manifest(
                repo_root=REPO_ROOT,
                baseline=baseline,
                intents=[first_applied, second_applied],
            )
            result = manifest["refs"][0]
            self.assertTrue(result["changed"])
            self.assertEqual(2, result["applied_intent_count"])
            self.assertEqual("value = 3\n", target.read_text(encoding="utf-8"))
            self.assertNotIn("value = 3", repr(manifest))

    def test_apply_replays_exact_candidate_and_rejects_third_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            run_dir = fixture_root / "run"
            run_dir.mkdir(mode=0o700)
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            target.chmod(0o600)
            baseline = self._baseline(target)
            source = fixture_root / "candidate.toml"
            source.write_text("value = 2\n", encoding="utf-8")
            stage = self.helper.stage_payload(
                run_dir=run_dir, intent_id="intent-1", source_file=source
            )
            prepared = self.helper.prepare_intent(
                repo_root=REPO_ROOT,
                baseline=baseline,
                intents=[],
                ref=str(target),
                intent_id="intent-1",
                staged_payload=stage,
            )

            self.helper.apply_intent(repo_root=REPO_ROOT, intent=prepared)
            with mock.patch.object(
                self.helper, "_fsync_directory", wraps=self.helper._fsync_directory
            ) as fsync_directory:
                replayed = self.helper.apply_intent(
                    repo_root=REPO_ROOT, intent=prepared
                )
            self.assertEqual("already_applied", replayed["replay_state"])
            fsync_directory.assert_called_once_with(target.parent)

            target.write_text("value = 99\n", encoding="utf-8")
            with self.assertRaises(self.helper.ExternalTouchError) as caught:
                self.helper.apply_intent(repo_root=REPO_ROOT, intent=prepared)
            self.assertEqual("external_touch_baseline_drift", caught.exception.code)

    def test_prepare_rejects_noop_and_cleanup_refuses_ambiguous_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            run_dir = fixture_root / "run"
            run_dir.mkdir(mode=0o700)
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            target.chmod(0o600)
            baseline = self._baseline(target)
            source = fixture_root / "candidate.toml"
            source.write_text("value = 1\n", encoding="utf-8")
            stage = self.helper.stage_payload(
                run_dir=run_dir, intent_id="intent-1", source_file=source
            )
            with self.assertRaises(self.helper.ExternalTouchError) as caught:
                self.helper.prepare_intent(
                    repo_root=REPO_ROOT,
                    baseline=baseline,
                    intents=[],
                    ref=str(target),
                    intent_id="intent-1",
                    staged_payload=stage,
                )
            self.assertEqual("external_touch_noop_candidate", caught.exception.code)

            Path(stage["path"]).write_text("tampered\n", encoding="utf-8")
            prepared_like = {
                "state": "prepared",
                "candidate": stage,
                "broker_candidate_path": str(fixture_root / ".broker.tmp"),
            }
            with self.assertRaises(self.helper.ExternalTouchError) as cleanup_error:
                self.helper.cleanup_intent(intent=prepared_like, allow_prepared=True)
            self.assertEqual(
                "external_touch_cleanup_ambiguous", cleanup_error.exception.code
            )

    def test_staging_reservation_replays_and_cleanup_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            run_dir = fixture_root / "run"
            run_dir.mkdir(mode=0o700)
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            target.chmod(0o600)
            source = fixture_root / "candidate.toml"
            source.write_text("value = 2\n", encoding="utf-8")
            baseline = self._baseline(target)

            staging = self.helper.declare_intent(
                repo_root=REPO_ROOT,
                baseline=baseline,
                intents=[],
                ref=str(target),
                intent_id="intent-1",
                run_dir=run_dir,
                source_file=source,
            )
            self.assertEqual("staging", staging["state"])
            self.assertFalse(Path(staging["candidate"]["path"]).exists())
            staged_once = self.helper.stage_declared_payload(
                intent=staging, source_file=source
            )
            staged_replay = self.helper.stage_declared_payload(
                intent=staging, source_file=source
            )
            self.assertEqual(staged_once["sha256"], staged_replay["sha256"])
            prepared = self.helper.finalize_intent(
                intent=staging, staged_payload=staged_replay
            )
            applied = self.helper.apply_and_cleanup_intent(
                repo_root=REPO_ROOT, intent=prepared
            )
            self.assertEqual("completed", applied["cleanup"]["state"])
            self.assertFalse(Path(applied["candidate"]["path"]).exists())
            self.helper.validate_evidence_state(
                baseline=baseline,
                intents=[applied],
                expected_task_id="EAT-TEST",
                expected_run_id="run-1",
                expected_design_sha256=SHA256_ZERO,
                expected_plan_sha256=SHA256_ONE,
                expected_refs=[str(target)],
                require_applied=True,
                require_cleanup=True,
                check_cleanup_paths=True,
            )

            tampered = json.loads(json.dumps(applied))
            tampered["after"]["sha256"] = SHA256_ZERO
            with self.assertRaises(self.helper.ExternalTouchError):
                self.helper.validate_evidence_state(
                    baseline=baseline,
                    intents=[tampered],
                    expected_task_id="EAT-TEST",
                    expected_run_id="run-1",
                    expected_design_sha256=SHA256_ZERO,
                    expected_plan_sha256=SHA256_ONE,
                    expected_refs=[str(target)],
                    require_applied=True,
                    require_cleanup=True,
                    check_cleanup_paths=False,
                )

    def test_durable_state_replace_fsyncs_file_and_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            destination = fixture_root / "ledger.json"
            staged = fixture_root / ".ledger.next"
            destination.write_text("old\n", encoding="utf-8")
            staged.write_text("new\n", encoding="utf-8")
            with (
                mock.patch.object(
                    self.helper, "_fsync_file", wraps=self.helper._fsync_file
                ) as fsync_file,
                mock.patch.object(
                    self.helper,
                    "_fsync_directory",
                    wraps=self.helper._fsync_directory,
                ) as fsync_directory,
            ):
                self.helper.durable_replace_file(
                    staged_file=staged, destination_file=destination
                )
            fsync_file.assert_called_once_with(staged)
            fsync_directory.assert_called_once_with(fixture_root)
            self.assertEqual("new\n", destination.read_text(encoding="utf-8"))
            self.assertFalse(staged.exists())


class ExternalTouchCliTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = {
            "PATH": os.environ["PATH"],
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": "/tmp/market-csheng-eat-pycache",
        }
        return subprocess.run(
            [sys.executable, str(HELPER_PATH), *arguments],
            cwd=REPO_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_runs_baseline_stage_prepare_apply_compare_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir).resolve()
            run_dir = fixture_root / "run"
            run_dir.mkdir(mode=0o700)
            target = fixture_root / "target.toml"
            target.write_text("value = 1\n", encoding="utf-8")
            target.chmod(0o600)
            candidate = fixture_root / "candidate.toml"
            candidate.write_text("value = 2\n", encoding="utf-8")

            baseline_result = self._run(
                "baseline",
                "--repo-root",
                str(REPO_ROOT),
                "--run-id",
                "run-1",
                "--task-id",
                "EAT-TEST",
                "--design-sha256",
                SHA256_ZERO,
                "--plan-sha256",
                SHA256_ONE,
                "--ref",
                str(target),
            )
            self.assertEqual(0, baseline_result.returncode, baseline_result.stderr)
            baseline = json.loads(baseline_result.stdout)
            baseline_file = fixture_root / "baseline.json"
            baseline_file.write_text(json.dumps(baseline), encoding="utf-8")

            stage_result = self._run(
                "stage",
                "--run-dir",
                str(run_dir),
                "--intent-id",
                "intent-1",
                "--source-file",
                str(candidate),
            )
            self.assertEqual(0, stage_result.returncode, stage_result.stderr)
            stage_file = fixture_root / "stage.json"
            stage_file.write_text(stage_result.stdout, encoding="utf-8")
            intents_file = fixture_root / "intents.json"
            intents_file.write_text("[]", encoding="utf-8")

            prepare_result = self._run(
                "prepare",
                "--repo-root",
                str(REPO_ROOT),
                "--baseline-file",
                str(baseline_file),
                "--intents-file",
                str(intents_file),
                "--ref",
                str(target),
                "--intent-id",
                "intent-1",
                "--staged-file",
                str(stage_file),
            )
            self.assertEqual(0, prepare_result.returncode, prepare_result.stderr)
            intent_file = fixture_root / "intent.json"
            intent_file.write_text(prepare_result.stdout, encoding="utf-8")

            apply_result = self._run(
                "apply-and-cleanup",
                "--repo-root",
                str(REPO_ROOT),
                "--intent-file",
                str(intent_file),
            )
            self.assertEqual(0, apply_result.returncode, apply_result.stderr)
            applied = json.loads(apply_result.stdout)
            intent_file.write_text(apply_result.stdout, encoding="utf-8")
            intents_file.write_text(json.dumps([applied]), encoding="utf-8")

            compare_result = self._run(
                "compare",
                "--repo-root",
                str(REPO_ROOT),
                "--baseline-file",
                str(baseline_file),
                "--intents-file",
                str(intents_file),
            )
            self.assertEqual(0, compare_result.returncode, compare_result.stderr)
            self.assertTrue(json.loads(compare_result.stdout)["refs"][0]["changed"])

            cleanup_result = self._run("cleanup", "--intent-file", str(intent_file))
            self.assertEqual(0, cleanup_result.returncode, cleanup_result.stderr)
            for output in (
                baseline_result.stdout,
                stage_result.stdout,
                prepare_result.stdout,
                apply_result.stdout,
                compare_result.stdout,
                cleanup_result.stdout,
            ):
                self.assertNotIn("value = 2", output)

    def test_cli_reports_typed_error_without_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir).resolve() / "target.toml"
            target.write_text("super_secret = true\n", encoding="utf-8")
            hardlink = target.with_name("hardlink.toml")
            os.link(target, hardlink)
            result = self._run(
                "baseline",
                "--repo-root",
                str(REPO_ROOT),
                "--run-id",
                "run-1",
                "--task-id",
                "EAT-TEST",
                "--design-sha256",
                SHA256_ZERO,
                "--plan-sha256",
                SHA256_ONE,
                "--ref",
                str(target),
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("external_touch_hardlink_rejected", result.stderr)
            self.assertNotIn("super_secret", result.stderr)


if __name__ == "__main__":
    unittest.main()
