# Python Testing Examples

These examples use only the Python standard library, so they can be copied into a scratch directory and exercised with `uv run --no-project python -m unittest` or `python3 -m unittest`. They keep each test independent, gate on fixture readiness, release their own temporary directories and child processes, and report cleanup failures instead of hiding them.

## Runnable Example: Isolated, Readiness-Gated Suite

Save the fixture and the three Python files below in one directory.

### Fixture: `fixtures/catalog.json`

```json
{"widget": 5, "gadget": 3}
```

### Module under test: `catalog_store.py`

```python
"""Small stdlib-only store used by this testing example."""

from __future__ import annotations

import json
from pathlib import Path


class FixtureNotReadyError(RuntimeError):
    """Raised when a required fixture file or endpoint is not ready."""


class CleanupError(RuntimeError):
    """Raised when a task-owned resource was not released cleanly."""


def load_fixture(path: Path) -> dict[str, int]:
    """Read the shared seed catalog, failing fast with an explicit reason."""

    if not path.is_file():
        raise FixtureNotReadyError(
            f"fixture not ready: {path} is missing; "
            "set CATALOG_FIXTURE_DIR to a prepared fixture directory"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FixtureNotReadyError(
            f"fixture not ready: {path} is not valid JSON: {error}"
        ) from error
    return {str(key): int(value) for key, value in payload.items()}


class CatalogStore:
    """Persist catalog quantities in one JSON file under a data directory."""

    def __init__(self, data_dir: Path) -> None:
        self._path = Path(data_dir) / "catalog.json"

    def seed(self, quantities: dict[str, int]) -> None:
        """Write the starting contents for one test-owned data directory."""

        self._write(quantities)

    def add(self, sku: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        catalog = self._read()
        catalog[sku] = catalog.get(sku, 0) + quantity
        self._write(catalog)

    def quantity(self, sku: str) -> int:
        return self._read().get(sku, 0)

    def _read(self) -> dict[str, int]:
        if not self._path.exists():
            return {}
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        return {str(key): int(value) for key, value in payload.items()}

    def _write(self, catalog: dict[str, int]) -> None:
        self._path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
```

### Worker process: `heartbeat_worker.py`

```python
"""Task-owned worker used by the testing example; stdlib only."""

from __future__ import annotations

import signal
import sys
import time
from pathlib import Path


def main() -> int:
    data_dir = Path(sys.argv[1])
    if sys.argv[2] == "ignore-term":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    heartbeat = data_dir / "heartbeat"
    while True:
        heartbeat.write_text(str(time.monotonic()), encoding="utf-8")
        time.sleep(0.01)


if __name__ == "__main__":
    raise SystemExit(main())
```

### Suite: `test_catalog_store.py`

```python
"""Runnable suite: per-test isolation, readiness gating, surfaced cleanup."""

from __future__ import annotations

import http.server
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

from catalog_store import CatalogStore, CleanupError, load_fixture

FIXTURE_DIR = Path(os.environ.get("CATALOG_FIXTURE_DIR", "fixtures"))
IGNORE_SIGTERM = os.environ.get("CATALOG_WORKER_IGNORES_SIGTERM") == "1"


def start_worker(data_dir: Path, *, ignore_sigterm: bool = False) -> subprocess.Popen[bytes]:
    """Start a task-owned worker that updates a heartbeat file until stopped."""

    worker = Path(__file__).with_name("heartbeat_worker.py")
    mode = "ignore-term" if ignore_sigterm else "honor-term"
    # Subprocess environment allowlist: the worker needs no ambient variables.
    return subprocess.Popen(
        [sys.executable, str(worker), str(data_dir), mode],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env={},
    )


def stop_worker(process: subprocess.Popen[bytes], timeout: float = 5.0) -> None:
    """Terminate a task-owned worker; surface any ungraceful shutdown."""

    try:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=timeout)
                raise CleanupError(
                    f"worker pid {process.pid} ignored SIGTERM; "
                    "cleanup killed it and reported the failure"
                )
        elif process.returncode != 0:
            raise CleanupError(
                f"worker pid {process.pid} already exited with code "
                f"{process.returncode} before cleanup; the failure was not "
                "observed by the test"
            )
    finally:
        if process.stderr is not None:
            process.stderr.close()


def wait_for_heartbeat(data_dir: Path, timeout: float = 5.0) -> bool:
    """Readiness check: poll for the heartbeat instead of sleeping blindly."""

    heartbeat = data_dir / "heartbeat"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if heartbeat.exists():
            return True
        time.sleep(0.01)
    return False


class _HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path != "/health":
            self.send_error(404)
            return
        body = b'{"status": "ok"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        """Silence request logging so test output stays deterministic."""


class CatalogStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        # Readiness gate: fail fast with an explicit reason instead of a
        # confusing downstream error.
        self.fixture = load_fixture(FIXTURE_DIR / "catalog.json")
        # Isolation: every test gets its own temporary data directory, seeded
        # from the read-only fixture, so runs never inherit mutable state.
        self._temp_dir = tempfile.TemporaryDirectory(prefix="catalog-test-")
        self.addCleanup(self._release_temp_dir)
        self.data_dir = Path(self._temp_dir.name) / "data"
        self.data_dir.mkdir()
        self.store = CatalogStore(self.data_dir)
        self.store.seed(self.fixture)

    def _release_temp_dir(self) -> None:
        # cleanup() raises when the tree cannot be removed, so a failed cleanup
        # is reported instead of silently leaking the directory.
        self._temp_dir.cleanup()

    def test_seeded_quantity_is_visible(self) -> None:
        self.assertEqual(self.store.quantity("widget"), self.fixture["widget"])

    def test_add_accumulates_within_one_test(self) -> None:
        self.store.add("widget", 2)
        self.assertEqual(self.store.quantity("widget"), self.fixture["widget"] + 2)

    def test_each_test_starts_from_the_fixture(self) -> None:
        # Ordered after test_add_accumulates_within_one_test yet sees no residue.
        self.assertEqual(self.store.quantity("widget"), self.fixture["widget"])

    def test_invalid_quantity_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add("widget", 0)

    def test_table_driven_additions(self) -> None:
        cases = [("widget", 1), ("gadget", 4)]
        for sku, quantity in cases:
            with self.subTest(sku=sku, quantity=quantity):
                self.store.add(sku, quantity)
                self.assertEqual(
                    self.store.quantity(sku), self.fixture[sku] + quantity
                )

    def test_worker_is_ready_and_released(self) -> None:
        process = start_worker(self.data_dir, ignore_sigterm=IGNORE_SIGTERM)
        self.addCleanup(stop_worker, process)
        self.assertTrue(
            wait_for_heartbeat(self.data_dir),
            "worker did not become ready within the readiness timeout",
        )


class HealthEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _HealthHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/health"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5.0)
        if cls.thread.is_alive():
            raise CleanupError("health server thread did not stop within the timeout")

    def test_health_endpoint_becomes_ready(self) -> None:
        # Readiness check: poll the endpoint instead of sleeping a fixed time.
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(self.url, timeout=1.0) as response:
                    if response.status == 200:
                        return
            except OSError:
                time.sleep(0.05)
        self.fail("health endpoint did not become ready within the readiness timeout")


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

### Run recipe and expected outcome

Run from the directory holding the files:

```bash
CATALOG_FIXTURE_DIR="$PWD/fixtures" uv run --no-project python -m unittest -v
```

Every test builds its own `TemporaryDirectory`, seeds it from the read-only fixture, and releases it during cleanup, so running the same command twice produces the same passing result and leaves `fixtures/catalog.json` byte-identical. `test_each_test_starts_from_the_fixture` runs after a test that mutates the store and still observes the original value, which fails if any two tests share a data directory.

### Negative checks

Point the fixture directory at a nonexistent path to exercise the readiness gate, which fails before any test body runs and reports the missing path (no directory is allocated for this negative check):

```bash
CATALOG_FIXTURE_DIR="/nonexistent/catalog-fixtures" uv run --no-project python -m unittest
```

Set `CATALOG_WORKER_IGNORES_SIGTERM=1` to start the worker in its non-cooperative mode, where `stop_worker` kills the process and then raises `CleanupError` so unittest reports the cleanup failure instead of swallowing it:

```bash
CATALOG_WORKER_IGNORES_SIGTERM=1 uv run --no-project python -m unittest
```

## How The Suite Embodies The Rules

- Isolation: `setUp` creates a fresh `TemporaryDirectory` and a fresh `CatalogStore` per test, and `start_worker` passes an explicit empty environment, so mutable state and ambient variables never cross test or run boundaries.
- Readiness: `load_fixture` raises `FixtureNotReadyError` with the missing path, and `wait_for_heartbeat` plus the endpoint loop poll with a bounded deadline instead of sleeping blindly.
- Cleanup: `stop_worker` releases the child process and surfaces an ungraceful shutdown, `_release_temp_dir` lets `TemporaryDirectory.cleanup` raise, and `HealthEndpointTest.tearDownClass` shuts the server down and fails if its thread survives.
- Explicit error handling: fixture reads distinguish missing files from invalid JSON, invalid quantities raise `ValueError`, and worker start, signal, and kill errors are wrapped with the operation that failed.
