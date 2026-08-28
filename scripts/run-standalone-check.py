#!/usr/bin/env python3
"""Run repository checks from a disposable, provider-isolated copy."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_NAMES = {".git", ".dist", ".pi", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
EXCLUDED_PREFIXES = {"docs/plans", "integrations", "src/runtime"}


def include(relative: Path) -> bool:
    value = relative.as_posix()
    return not (set(relative.parts) & EXCLUDED_NAMES) and not any(
        value == prefix or value.startswith(prefix + "/") for prefix in EXCLUDED_PREFIXES
    )


def copy_repository(source: Path, destination: Path) -> None:
    inventory = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=source,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for raw_relative in inventory:
        if not raw_relative:
            continue
        relative = Path(os.fsdecode(raw_relative))
        path = source / relative
        if not include(relative) or path.is_symlink() or not path.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def surface_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    completed = subprocess.run(command, cwd=cwd, env=env, check=False, capture_output=True)
    if completed.returncode:
        raise RuntimeError(f"check failed: {command[0]} ({completed.returncode})")


def main() -> int:
    report: dict[str, object] = {"copy": "pending", "pi_blocked": False, "checks": "pending"}
    try:
        with tempfile.TemporaryDirectory(prefix="agent-skills-standalone-") as temporary:
            root = Path(temporary)
            checkout = root / "repo"
            checkout.mkdir()
            copy_repository(REPO_ROOT, checkout)
            report["copy"] = "pass"
            report["surface_sha256"] = surface_digest(checkout)

            bin_dir = root / "bin"
            bin_dir.mkdir()
            pi = bin_dir / "pi"
            pi.write_text("#!/usr/bin/env sh\nexit 97\n", encoding="utf-8")
            pi.chmod(0o755)
            pi_config = root / "pi-config"
            pi_config.mkdir()
            isolated_home = root / "home"
            isolated_home.mkdir()
            isolated_tmp = root / "tmp"
            isolated_tmp.mkdir()
            env = {
                "HOME": str(isolated_home),
                "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                "TMPDIR": str(isolated_tmp),
                "XDG_CACHE_HOME": str(root / "cache"),
                "PI_CONFIG_DIR": str(pi_config),
                "PI_CODING_AGENT_DIR": str(pi_config),
                "STANDALONE_CHECK_ACTIVE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            blocked = subprocess.run(["pi", "--version"], env=env, check=False)
            report["pi_blocked"] = blocked.returncode == 97
            if not report["pi_blocked"]:
                raise RuntimeError("provider isolation failed")

            run(["git", "init", "-q"], checkout, env)
            run(["git", "add", "-A"], checkout, env)
            run([sys.executable, "scripts/generate-skills-index.py", "--check"], checkout, env)
            run([sys.executable, "scripts/flatten-skills.py", "--target", "root-flat", "--check"], checkout, env)
            run([sys.executable, "scripts/generate-workflow-diagrams.py", "--check"], checkout, env)
            run(["bash", "scripts/check.sh"], checkout, env)
            report["checks"] = "pass"
    except (OSError, RuntimeError) as exc:
        report["error"] = str(exc)
        print(json.dumps(report, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
