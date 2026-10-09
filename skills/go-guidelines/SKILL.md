---
name: go-guidelines
description: "Apply Go-specific policy to existing or approved Go modules, CLI tools, API services, tests, and reviews: module hygiene, standard toolchain checks, explicit errors and context, purpose-specific architecture, and delivery. Use as a language overlay; do not own language selection or lifecycle control."
---

# Go Guidelines

## Purpose

Define the shared Go policy baseline, then load only the architecture reference that matches the implementation archetype. The primary workflow owns lifecycle order; an unfixed implementation-language decision uses only `references/language-selection.md` in `skills-routing`.

## Scope

In-scope:

- editing or creating approved Go code and modules
- Go CLI tools and API services
- Go tests, build configuration, and implementation review

Out-of-scope:

- choosing whether new persisted code should use Go; read `references/language-selection.md` in `skills-routing`
- ad hoc agent command and tool selection; read `references/tool-selection.md` in `skills-routing`
- generic resilience or logging policy beyond Go-specific application; see `error-patterns` and `logging-standards`

## Progressive Disclosure

- CLI tools and operator commands: `references/cli-tool-patterns.md`
- API and network services: `references/api-service-patterns.md`
- Implementation review workflow: `references/review-checklist.md`

Load both purpose profiles only when one approved project genuinely owns both a CLI control surface and an API server. Do not apply service layering to a small CLI or Cobra command structure to an API-only service.

## Shared Baseline

1. Use Go modules as the source of truth.
   - Commit consistent `go.mod` and `go.sum` files.
   - Declare the minimum supported Go version in `go.mod`.
   - Run `go mod tidy` when imports or tool dependencies change, then review the module diff.
2. Use the standard toolchain first.
   - Format changed Go files with `gofmt` and any already configured project formatting step. Do not invent a fixed-column wrapping rule, column linter, or extra formatter dependency.
   - Run `go test ./...` to compile packages and execute tests.
   - Run `go vet ./...` for suspicious constructs not rejected by compilation.
   - Run project-owned analyzers such as Staticcheck or golangci-lint when configured; do not introduce an aggregator only to satisfy this skill.
3. Keep developer tools project-owned when reproducibility matters.
   - On Go 1.24 or newer, prefer a `go.mod` tool directive for versioned Go developer tools.
   - Use the repository's existing pre-1.24 mechanism when the module version requires it.
4. Handle errors explicitly.
   - Do not ignore returned errors unless the API documents that the result is irrelevant and the reason is recorded.
   - Add operation context with `fmt.Errorf("operation: %w", err)` when propagating an underlying error.
   - Define sentinel or custom error types only when callers need stable programmatic classification through `errors.Is` or `errors.As`.
   - Log an error at the boundary that owns presentation or recovery; avoid logging and returning the same error at every layer.
5. Propagate cancellation and deadlines.
   - Accept `context.Context` as the first parameter for request-scoped, blocking, network, subprocess, or other IO-heavy work.
   - Do not store request contexts in long-lived structs.
6. Keep abstractions demand-driven.
   - Define small interfaces at the consuming boundary only when multiple implementations, fakes, or isolation requirements justify them.
   - Do not introduce interfaces, repositories, or layers solely because the code is written in Go.
   - In a migration, design around business rules and actual consumer contracts, using Go's standard library and suitable maintained Go dependencies. A standard-library gap is not a requirement to write a parser or emulate the prior language's library; select a suitable ecosystem implementation under `development-standards`. Keep exact legacy serialization or parser behavior only for a real compatibility requirement.
   - When Go remains the selected product language, choose whether to complete the current design, reuse a package or replace the flawed implementation. A literal port that recreates another language's runtime or libraries does not establish that Go is unsuitable.
   - Inspect custom file/path utilities, source-analysis adapters, type coercions and other migration support code against the capabilities of existing Go packages and suitable mature libraries. Trace real callers and protected domain behavior; keep only the business-specific glue the chosen capability does not own. A language prefix or utility filename prompts inspection, not automatic deletion, and adding a library is useful only when it removes a real responsibility at acceptable lifecycle cost.
7. Test behavior at the narrowest useful boundary.
   - Use the standard `testing` package by default for Go tests. Production Go does not require rewriting useful Python tests, fixture generators, or independent verification tools; their runtime and maintenance costs are separate from production delivery.
   - Rework migration tests around business outcomes, real consumers, retained data and failure boundaries. An old library or translated Python test is not an automatic oracle: replace incidental formatting and library-equivalence assertions with meaningful scenarios while retaining required protocol bytes and data protection.
   - Prefer table-driven tests when they improve coverage and readability.
   - Use `httptest`, fakes, temporary directories, and injected IO instead of global process state when practical.

## Build Output And Local State

- Direct `go run` is a development convenience for a host that owns the source and toolchain; it does not establish a consumer delivery contract. Choose the implementation and complete delivery boundary through `references/language-selection.md` in `skills-routing`.
- Use an explicit build when the consumer needs an artifact, a reusable executable, or startup/process behavior that `go run` does not provide. The Go driver adds overhead and does not guarantee the child program's exact exit status or signal behavior; verify those requirements before changing the invocation mechanism. When building, pass an explicit `-o` and use the repository's declared scratch or output directory, otherwise a unique task directory under `TMPDIR` (or `$HOME/tmp` for agent-owned ad hoc work when unset); do not leave the implicit `./<name>` binary in the checkout.
- A repository's declared scratch directory may be an ignored in-repo path such as `tmp/`, `dist/`, or `bin/`, or a directory outside the tree. Follow the repository's declaration rather than assuming an external-only location.
- Final output placement does not control Go's intermediate build files. Respect an explicit `GOTMPDIR`; otherwise Go uses the platform temporary directory, including `TMPDIR` on Unix. Ensure the effective development scratch root exists and is disk-backed for large builds. Do not conflate these temporary files with `GOCACHE` or `GOMODCACHE`, or override those caches merely to centralize scratch.
- `GOCACHE` and `GOMODCACHE` default outside the source tree, but that does not protect the checkout: test binaries, `-coverprofile` output, fuzz corpora, and explicit build outputs can still appear as untracked or ignored files. After verification, inspect ignored and untracked files as well as tracked diffs for task-owned contamination. Remove per-run scratch that is no longer needed; retain declared delivery artifacts or bounded caches according to their ownership contract, and do not delete another owner's data or cache.
- Build for the target `GOOS` and `GOARCH` on the controller or CI host and ship the binary or image. The managed execution target must not compile, download Go modules, or use `go run`; ordinary artifact/package installation is not runtime compilation.
- When an existing Shell entrypoint uses the binary, integrate both into the same declared delivery and update operation, including required assets. Verify that entrypoint in the delivered layout rather than assuming a backend build or test made the user's tool available.

## Optional Checks

Use these when the project or risk profile calls for them:

- `go test -race ./...` for concurrent or shared-state code
- Staticcheck for low-noise semantic analysis
- `govulncheck ./...` for applications with third-party dependencies or release artifacts
- golangci-lint when configured as the repository's analyzer aggregator

Pin reproducible Go tools through the owning module rather than assuming a workstation-global version.

## Checklist

- `go.mod` declares the supported Go baseline and `go.sum` is consistent
- changed Go files are `gofmt` clean
- `go test ./...` and `go vet ./...` pass
- project-configured analyzers pass when configured
- returned errors, cancellation, and resource cleanup are explicit
- tests cover the changed core behavior
- build, coverage, and test artifacts use the declared scratch and are cleaned up
- managed or production execution targets receive a prebuilt binary or image, not a compiler or `go run`
- the matching CLI or API purpose profile has been applied
