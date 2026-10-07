# Go Testing Examples

These examples use only the Go standard library, so they build and run offline with the `testing` package. The package gates the whole run on fixture readiness, gives every test its own `t.TempDir`, releases child processes through `t.Cleanup`, and returns explicit errors instead of ignoring them.

## Runnable Example: Readiness Gate, Isolation, And Cleanup

Save the module, the fixture, and the test file in one directory.

### Module: `go.mod`

```text
module example.com/catalog

go 1.24
```

### Fixture: `fixtures/catalog.json`

```json
{"widget": 5, "gadget": 3}
```

### Module under test: `catalog.go`

```go
// Package catalog is the stdlib-only subject used by this testing example.
package catalog

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// ErrFixtureNotReady reports that a required fixture file or endpoint is missing.
var ErrFixtureNotReady = errors.New("fixture not ready")

// ErrCleanup reports that a task-owned resource was not released cleanly.
var ErrCleanup = errors.New("cleanup failed")

// LoadFixture reads the shared seed catalog, failing with an explicit reason.
func LoadFixture(path string) (map[string]int, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("%w: %s is unreadable: %v", ErrFixtureNotReady, path, err)
	}
	catalog := make(map[string]int)
	if err := json.Unmarshal(data, &catalog); err != nil {
		return nil, fmt.Errorf("%w: %s is not valid JSON: %v", ErrFixtureNotReady, path, err)
	}
	return catalog, nil
}

// CatalogStore persists catalog quantities in one JSON file per data directory.
type CatalogStore struct {
	path string
}

// NewCatalogStore returns a store rooted at dataDir.
func NewCatalogStore(dataDir string) *CatalogStore {
	return &CatalogStore{path: filepath.Join(dataDir, "catalog.json")}
}

// Seed writes the starting contents for one test-owned data directory.
func (s *CatalogStore) Seed(catalog map[string]int) error {
	return s.write(catalog)
}

// Add accumulates quantity for one SKU.
func (s *CatalogStore) Add(sku string, quantity int) error {
	if quantity <= 0 {
		return fmt.Errorf("quantity must be positive, got %d", quantity)
	}
	catalog, err := s.read()
	if err != nil {
		return err
	}
	catalog[sku] += quantity
	return s.write(catalog)
}

// Quantity returns the stored quantity for one SKU.
func (s *CatalogStore) Quantity(sku string) (int, error) {
	catalog, err := s.read()
	if err != nil {
		return 0, err
	}
	return catalog[sku], nil
}

func (s *CatalogStore) read() (map[string]int, error) {
	data, err := os.ReadFile(s.path)
	if errors.Is(err, os.ErrNotExist) {
		return make(map[string]int), nil
	}
	if err != nil {
		return nil, fmt.Errorf("read catalog: %w", err)
	}
	catalog := make(map[string]int)
	if err := json.Unmarshal(data, &catalog); err != nil {
		return nil, fmt.Errorf("decode catalog: %w", err)
	}
	return catalog, nil
}

func (s *CatalogStore) write(catalog map[string]int) error {
	data, err := json.Marshal(catalog)
	if err != nil {
		return fmt.Errorf("encode catalog: %w", err)
	}
	return os.WriteFile(s.path, data, 0o600)
}
```

### Tests: `catalog_test.go`

```go
package catalog

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"testing"
	"time"
)

var fixtureDir = envOr("CATALOG_FIXTURE_DIR", "fixtures")

func envOr(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

// TestMain gates the whole suite on fixture readiness and reports setup
// failures explicitly instead of letting every test fail obscurely.
func TestMain(m *testing.M) {
	if _, err := LoadFixture(filepath.Join(fixtureDir, "catalog.json")); err != nil {
		fmt.Fprintf(os.Stderr, "suite readiness failed: %v\n", err)
		os.Exit(1)
	}
	os.Exit(m.Run())
}

func newTestStore(t *testing.T) (*CatalogStore, map[string]int) {
	t.Helper()
	seed, err := LoadFixture(filepath.Join(fixtureDir, "catalog.json"))
	if err != nil {
		t.Fatalf("fixture not ready: %v", err)
	}
	// t.TempDir() is unique per test and removed by the testing package, so
	// repeated runs never inherit mutable state and a failed removal fails the test.
	store := NewCatalogStore(t.TempDir())
	if err := store.Seed(seed); err != nil {
		t.Fatalf("seed store: %v", err)
	}
	return store, seed
}

func TestStoreStartsFromFixture(t *testing.T) {
	store, seed := newTestStore(t)
	got, err := store.Quantity("widget")
	if err != nil {
		t.Fatalf("Quantity() error = %v", err)
	}
	if got != seed["widget"] {
		t.Fatalf("Quantity() = %d, want %d", got, seed["widget"])
	}
}

func TestStoreDoesNotLeakBetweenTests(t *testing.T) {
	store, _ := newTestStore(t)
	if err := store.Add("widget", 99); err != nil {
		t.Fatalf("Add() error = %v", err)
	}
}

func TestStoreAddAccumulatesWithinOneTest(t *testing.T) {
	store, seed := newTestStore(t)
	if err := store.Add("widget", 2); err != nil {
		t.Fatalf("Add() error = %v", err)
	}
	got, err := store.Quantity("widget")
	if err != nil {
		t.Fatalf("Quantity() error = %v", err)
	}
	if want := seed["widget"] + 2; got != want {
		t.Fatalf("Quantity() = %d, want %d", got, want)
	}
}

func TestInvalidQuantityIsRejected(t *testing.T) {
	store, _ := newTestStore(t)
	if err := store.Add("widget", 0); err == nil {
		t.Fatal("Add() error = nil, want rejection")
	}
}

func TestAddTableDriven(t *testing.T) {
	tests := []struct {
		name     string
		sku      string
		quantity int
	}{
		{name: "single add", sku: "widget", quantity: 1},
		{name: "bulk add", sku: "gadget", quantity: 4},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			store, seed := newTestStore(t)
			if err := store.Add(tt.sku, tt.quantity); err != nil {
				t.Fatalf("Add() error = %v", err)
			}
			got, err := store.Quantity(tt.sku)
			if err != nil {
				t.Fatalf("Quantity() error = %v", err)
			}
			if want := seed[tt.sku] + tt.quantity; got != want {
				t.Fatalf("Quantity() = %d, want %d", got, want)
			}
		})
	}
}

func BenchmarkAdd(b *testing.B) {
	seed, err := LoadFixture(filepath.Join(fixtureDir, "catalog.json"))
	if err != nil {
		b.Fatalf("fixture not ready: %v", err)
	}
	store := NewCatalogStore(b.TempDir())
	if err := store.Seed(seed); err != nil {
		b.Fatalf("seed store: %v", err)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if err := store.Add("widget", 1); err != nil {
			b.Fatalf("Add() error = %v", err)
		}
	}
}

func TestWorkerIsReadyAndReleased(t *testing.T) {
	dataDir := t.TempDir()
	ignore := os.Getenv("CATALOG_WORKER_IGNORES_INTERRUPT") == "1"
	cmd := startWorker(t, dataDir, ignore)
	t.Cleanup(func() {
		if err := stopWorker(cmd, 5*time.Second); err != nil {
			t.Errorf("worker cleanup: %v", err)
		}
	})
	if !waitForHeartbeat(dataDir, 5*time.Second) {
		t.Fatal("worker did not become ready within the readiness timeout")
	}
}

// TestHelperProcess runs as the task-owned worker when re-executed as a child.
func TestHelperProcess(t *testing.T) {
	if os.Getenv("GO_WANT_HELPER_PROCESS") != "1" {
		return
	}
	dataDir := os.Getenv("HELPER_DATA_DIR")
	heartbeat := filepath.Join(dataDir, "heartbeat")
	if os.Getenv("HELPER_IGNORE_INTERRUPT") == "1" {
		signal.Ignore(os.Interrupt)
	} else {
		stop := make(chan os.Signal, 1)
		signal.Notify(stop, os.Interrupt)
		go func() {
			<-stop
			os.Exit(0)
		}()
	}
	for {
		if err := os.WriteFile(heartbeat, []byte(time.Now().String()), 0o600); err != nil {
			fmt.Fprintf(os.Stderr, "heartbeat: %v\n", err)
			os.Exit(1)
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func boolToInt(value bool) string {
	if value {
		return "1"
	}
	return "0"
}

func startWorker(t *testing.T, dataDir string, ignoreInterrupt bool) *exec.Cmd {
	t.Helper()
	cmd := exec.Command(os.Args[0], "-test.run=TestHelperProcess")
	cmd.Stderr = os.Stderr
	// Subprocess environment allowlist: only the worker handshake variables.
	cmd.Env = []string{
		"GO_WANT_HELPER_PROCESS=1",
		"HELPER_DATA_DIR=" + dataDir,
		"HELPER_IGNORE_INTERRUPT=" + boolToInt(ignoreInterrupt),
		"CATALOG_FIXTURE_DIR=" + fixtureDir,
	}
	if err := cmd.Start(); err != nil {
		t.Fatalf("start worker: %v", err)
	}
	return cmd
}

// stopWorker terminates a task-owned worker and surfaces any ungraceful exit.
func stopWorker(cmd *exec.Cmd, timeout time.Duration) error {
	if cmd.Process == nil {
		return fmt.Errorf("%w: worker was never started", ErrCleanup)
	}
	done := make(chan error, 1)
	go func() { done <- cmd.Wait() }()
	if err := cmd.Process.Signal(os.Interrupt); err != nil {
		// The worker may already be gone; reap it, then still report the signal failure.
		if killErr := cmd.Process.Kill(); killErr != nil && !errors.Is(killErr, os.ErrProcessDone) {
			return fmt.Errorf("%w: signal worker: %v (kill also failed: %v)", ErrCleanup, err, killErr)
		}
		<-done
		return fmt.Errorf("%w: signal worker: %v", ErrCleanup, err)
	}
	select {
	case err := <-done:
		return err
	case <-time.After(timeout):
		if err := cmd.Process.Kill(); err != nil {
			return fmt.Errorf("%w: kill worker: %v", ErrCleanup, err)
		}
		<-done
		return fmt.Errorf("%w: worker ignored interrupt and was killed", ErrCleanup)
	}
}

func waitForHeartbeat(dataDir string, timeout time.Duration) bool {
	heartbeat := filepath.Join(dataDir, "heartbeat")
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		if _, err := os.Stat(heartbeat); err == nil {
			return true
		}
		time.Sleep(10 * time.Millisecond)
	}
	return false
}
```

### Run recipe and expected outcome

Run from the directory holding the files:

```bash
GOFLAGS=-mod=mod GOPROXY=off go test -count=1 ./...
GOFLAGS=-mod=mod GOPROXY=off go test -count=1 -bench BenchmarkAdd -benchtime 100x ./...
```

`newTestStore` calls `t.TempDir`, which returns a unique directory per test and removes it when the test ends, so running the same test command twice produces the same passing result and leaves `fixtures/catalog.json` byte-identical. `TestStoreDoesNotLeakBetweenTests` mutates its store before `TestStoreAddAccumulatesWithinOneTest` reads a freshly seeded one, which fails if any two tests share a data directory.

### Negative checks

Point the fixture directory at a nonexistent path to exercise the readiness gate in `TestMain`, which prints the missing path and exits non-zero before any test runs (no directory is allocated for this negative check):

```bash
CATALOG_FIXTURE_DIR="/nonexistent/catalog-fixtures" GOFLAGS=-mod=mod GOPROXY=off go test -count=1 ./...
```

Set `CATALOG_WORKER_IGNORES_INTERRUPT=1` to start the worker in its non-cooperative mode, where `stopWorker` kills the process and returns `ErrCleanup` so `t.Cleanup` records a visible test failure:

```bash
CATALOG_WORKER_IGNORES_INTERRUPT=1 GOFLAGS=-mod=mod GOPROXY=off go test -count=1 -run TestWorkerIsReadyAndReleased ./...
```

## How The Package Embodies The Rules

- Isolation: `newTestStore` and `TestWorkerIsReadyAndReleased` each call `t.TempDir`, and `startWorker` sets `cmd.Env` to an explicit allowlist, so mutable state and ambient variables never cross test or run boundaries.
- Readiness: `TestMain` fails the run with an explicit message when the fixture is missing, `newTestStore` returns `ErrFixtureNotReady`, and `waitForHeartbeat` polls with a bounded deadline instead of sleeping a fixed time.
- Cleanup: `t.Cleanup` stops the child process and reports any ungraceful exit, and the `testing` package removes each `t.TempDir` and fails the test if removal does not succeed.
- Explicit error handling: `LoadFixture` wraps `ErrFixtureNotReady`, `stopWorker` wraps `ErrCleanup` around signal and kill failures, and every ignored return value would instead be checked with `t.Fatalf` or returned to the caller.
