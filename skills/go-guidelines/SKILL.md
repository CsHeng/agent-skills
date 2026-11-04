---
name: go-guidelines
description: "Apply Go-specific policy to existing or approved Go modules, CLI tools, API services, tests, and reviews: module hygiene, standard toolchain checks, explicit errors and context, purpose-specific architecture, and delivery. Use as a language overlay; do not own language selection or lifecycle control."
---

# Go Guidelines

Apply the shared baseline below, then load the reference that matches the archetype. An unfixed implementation-language decision uses `references/language-selection.md` in `skills-routing`; ad hoc command and tool choice uses `references/tool-selection.md` there; resilience and logging policy beyond Go-specific application belongs to `error-patterns` and `logging-standards`.

## Progressive Disclosure

- CLI tools and operator commands: `references/cli-tool-patterns.md`
- API and network services: `references/api-service-patterns.md`
- Producing, running, testing or delivering a Go artifact (build output, scratch, coverage or fuzz files, target-host delivery): `references/build-and-delivery.md`
- Porting existing code or tests from another language: `references/migration.md`
- Implementation review: `references/review-checklist.md`

Apply `api-service-patterns` to API or network services and `cli-tool-patterns` to CLIs; a library gets only the shared baseline. Load both profiles when one approved project owns both a CLI control surface and an API server.

## Shared Baseline

1. Use Go modules as the source of truth.
   - Keep `go.mod` and `go.sum` tracked and consistent.
   - Declare the minimum supported Go version in `go.mod`.
   - Run `go mod tidy` when imports or tool dependencies change, then review the module diff.
2. Use the standard toolchain first.
   - Format changed Go files with `gofmt` and the repository's configured formatting step.
   - Run `go test ./...` to compile packages and execute tests.
   - Run `go vet ./...` for suspicious constructs that compilation accepts.
   - Run project-owned analyzers such as Staticcheck or golangci-lint when configured.
3. Keep developer tools project-owned when reproducibility matters.
   - On Go 1.24 or newer, use a `go.mod` tool directive for versioned Go developer tools.
   - Use the repository's existing pre-1.24 mechanism when the module version requires it.
4. Handle errors explicitly.
   - Handle every returned error; discard one only when the API documents the result as irrelevant, and record that reason.
   - Add operation context with `fmt.Errorf("operation: %w", err)` when propagating an underlying error.
   - Define sentinel or custom error types when callers need stable programmatic classification through `errors.Is` or `errors.As`.
   - Log an error once, at the boundary that owns presentation or recovery.
5. Propagate cancellation and deadlines.
   - Accept `context.Context` as the first parameter for request-scoped, blocking, network, subprocess, or other IO-heavy work.
   - Pass the request context as an argument on each call.
6. Keep abstractions demand-driven.
   - Introduce an interface or layer when a second implementation, a fake, or an isolation need exists, and define it at the consuming boundary.
7. Test behavior at the narrowest useful boundary.
   - Use the standard `testing` package by default, with table-driven tests when they improve coverage and readability.
   - Use `httptest`, fakes, temporary directories, and injected IO in place of global process state when practical.

## Optional Checks

Use these when the project or risk profile calls for them:

- `go test -race ./...` for concurrent or shared-state code
- Staticcheck for low-noise semantic analysis
- `govulncheck ./...` for applications with third-party dependencies or release artifacts

Pin reproducible Go tools through the owning module.
