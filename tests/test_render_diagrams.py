from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/render-diagrams.sh"
SOURCE = REPO_ROOT / "docs/architecture/diagrams/skill-composition.puml"
GENERATED = REPO_ROOT / "docs/architecture/generated/skill-composition.svg"


def resolve_plantuml() -> str | None:
    for key in ("RENDER_DIAGRAMS_PLANTUML", "PLANTUML"):
        value = os.environ.get(key)
        if value and Path(value).is_file():
            return value
    if shutil.which("mise"):
        completed = subprocess.run(
            ["mise", "which", "plantuml"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        if completed.returncode == 0:
            path = completed.stdout.strip()
            if path:
                return path
    return shutil.which("plantuml")


def plantuml_env() -> dict[str, str]:
    plantuml = resolve_plantuml()
    if not plantuml:
        raise unittest.SkipTest("PlantUML unavailable")
    return {
        "HOME": os.environ["HOME"],
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
        "PATH": os.environ["PATH"],
        "RENDER_DIAGRAMS_PLANTUML": plantuml,
    }


class RenderDiagramsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plantuml_env = plantuml_env()

    def run_script(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged = {**self.plantuml_env, **(env or {})}
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=merged,
        )

    def test_generation_uses_explicit_plantuml_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            diagram_dir = root / "docs/architecture/diagrams"
            generated_dir = root / "docs/architecture/generated"
            diagram_dir.mkdir(parents=True)
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(SOURCE, diagram_dir / "skill-composition.puml")
            shutil.copy2(SCRIPT, scripts_dir / "render-diagrams.sh")
            result = subprocess.run(
                ["bash", str(scripts_dir / "render-diagrams.sh")],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                env=self.plantuml_env,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            svg = generated_dir / "skill-composition.svg"
            self.assertTrue(svg.is_file())
            text = svg.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("<svg"))
            self.assertIn("plantuml", text.lower())

    def test_check_mode_is_non_mutating_when_fresh(self) -> None:
        before = GENERATED.read_bytes()
        result = self.run_script("--check")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, GENERATED.read_bytes())

    def test_check_mode_detects_stale_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            diagram_dir = root / "docs/architecture/diagrams"
            generated_dir = root / "docs/architecture/generated"
            diagram_dir.mkdir(parents=True)
            generated_dir.mkdir(parents=True)
            shutil.copy2(SOURCE, diagram_dir / "skill-composition.puml")
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(SCRIPT, scripts_dir / "render-diagrams.sh")
            (generated_dir / "skill-composition.svg").write_text(
                '<svg stale="1"></svg>',
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", str(scripts_dir / "render-diagrams.sh"), "--check"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                env=self.plantuml_env,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("stale or missing", result.stderr)

    def test_check_mode_does_not_create_missing_generated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            diagram_dir = root / "docs/architecture/diagrams"
            diagram_dir.mkdir(parents=True)
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(SOURCE, diagram_dir / "skill-composition.puml")
            shutil.copy2(SCRIPT, scripts_dir / "render-diagrams.sh")
            generated_dir = root / "docs/architecture/generated"
            self.assertFalse(generated_dir.exists())
            result = subprocess.run(
                ["bash", str(scripts_dir / "render-diagrams.sh"), "--check"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                env=self.plantuml_env,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(generated_dir.exists())

    def test_generation_failure_preserves_tracked_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            diagram_dir = root / "docs/architecture/diagrams"
            generated_dir = root / "docs/architecture/generated"
            diagram_dir.mkdir(parents=True)
            generated_dir.mkdir(parents=True)
            good = b"<svg preserved=\"1\"></svg>"
            (generated_dir / "skill-composition.svg").write_bytes(good)
            (diagram_dir / "skill-composition.puml").write_text("@startuml\nbroken syntax\n", encoding="utf-8")
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(SCRIPT, scripts_dir / "render-diagrams.sh")
            result = subprocess.run(
                ["bash", str(scripts_dir / "render-diagrams.sh")],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                env=self.plantuml_env,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(good, (generated_dir / "skill-composition.svg").read_bytes())

    def test_missing_tool_fails_without_placeholder(self) -> None:
        minimal_path = os.pathsep.join(part for part in ("/usr/bin", "/bin") if part)
        result = self.run_script(
            "--check",
            env={
                "PATH": minimal_path,
                "RENDER_DIAGRAMS_PLANTUML": "/nonexistent/plantuml",
                "PLANTUML": "/nonexistent/plantuml",
            },
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("PlantUML failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
