#!/usr/bin/env python3
"""Run repository checks from a disposable, provider-isolated copy."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_NAMES = {
    ".git",
    ".dist",
    ".pi",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
EXCLUDED_PREFIXES = {"docs/plans", "integrations", "src/runtime"}


def include(relative: Path) -> bool:
    value = relative.as_posix()
    return not (set(relative.parts) & EXCLUDED_NAMES) and not any(
        value == prefix or value.startswith(prefix + "/")
        for prefix in EXCLUDED_PREFIXES
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


def run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    completed = subprocess.run(
        command, cwd=cwd, env=env, check=False, capture_output=True
    )
    if completed.returncode:
        raise RuntimeError(f"check failed: {command[0]} ({completed.returncode})")


def main() -> int:
    report: dict[str, object] = {
        "copy": "pending",
        "pi_blocked": False,
        "checks": "pending",
    }
    try:
        with tempfile.TemporaryDirectory(
            prefix="agent-skills-standalone-"
        ) as temporary:
            root = Path(temporary)
            checkout = root / "repo"
            checkout.mkdir()
            copy_repository(REPO_ROOT, checkout)
            report["copy"] = "pass"

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
