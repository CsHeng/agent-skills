+++
artifact_kind = "design"
contract_version = 3
approval_status = "approved"

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "pyproject.toml", "contracts", "docs/architecture", "docs/changelog/design-decisions.md", "hooks/pre-commit", "scripts", "skills", "skills.index.json", "src", "runtime"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []
+++
# Design

The user's 2026-08-19 instruction to implement this correction approves PDR-001 after the bounded design review findings were incorporated.

## Problem

HSC-050 incorrectly treated source-level sharing as sufficient for every distribution target. Native Claude and Codex plugins install the complete repository package, so lifecycle skills can reach a repository-level shared runtime, but `npx skills` and direct Agent Skills consumers install or expose one skill directory at a time. The current lifecycle skills therefore lose their executable runtime when installed independently.

The same cutover also removed the nested authored skill tree and its flat generated projection. That collapses two different responsibilities: maintainable source organization and compatibility with coding agents that require root-flat skill discovery.

The previous approved hybrid-distribution boundary used `src/skills/` as nested authored truth, generated root-flat `skills/` for provider and direct-agent discovery, and copied the single runtime source into every runner-owning generated skill. The current implementation and stable docs narrowed advisory `npx skills` support into instruction-only guidance, which was not the intended meaning of advisory ownership.

## Goals

- Restore one nested authored `src/skills/` tree and one generated root-flat `skills/` projection while retaining exactly 39 public skills and the three approved compatibility-skill retirements.
- Move the new Python lifecycle runtime to the single authored source `src/runtime/harness/` and materialize a production-only copy inside each of the six runner-owning generated skills.
- Make every independently installed lifecycle skill resolve its runtime only from its own skill directory.
- Retain codex-native as the flag-absent backend, explicit Herdr v1 projection, version-3 artifacts and ledger, complete external-evidence chain, approval and review gates, the thin aggregate checker, and the approved Markdown policy.
- Restore generator and install-surface parity checks without restoring field-at-a-time Shell parsing, copied authored truth, or repeated full validation.

## Boundaries

### Architecture Decision PDR-001

The chosen boundary is source sharing plus distribution closure. `src/skills/` and `src/runtime/harness/` are the only authored behavior sources. `skills/` is the sole materialized, tracked, root-flat compatibility projection. Each runtime-owning generated skill contains a generated `scripts/harness/` package copied from the single Python source and invokes `scripts/harness/cli.py` relative to its own skill root.

The status quo is rejected because repository-level `runtime/harness/` is outside the Agent Skills installation unit and breaks selected-skill installs. A separately published runtime package or runtime-support pseudo-skill is rejected because it introduces dependency installation, version coordination, network availability, and unsupported dependency discovery. Splitting the runtime into six hand-maintained implementations is rejected because it recreates multiple authorities.

The marginal cost is approximately six generated copies of the production Python package plus parity checks. The benefit is deterministic standalone closure across native plugins, `npx skills`, copy mode, symlink mode, and direct root-flat discovery. The generator owns materialization; maintainers edit only source and regenerate. The upgrade trigger for a separately versioned runtime is evidence that the generated package size or update cost materially harms supported installation, not source-code aesthetics.

### Distribution Contract

`npx skills` remains advisory only in destination, copy-versus-symlink, duplicate exposure, coexistence, update, and removal ownership. Advisory does not waive skill-local resource closure. The repository validates that every generated lifecycle skill contains the runtime files it references and works when copied away from the repository root.

Native Claude and Codex manifests both consume and validate the same tracked root-flat `skills/` projection. `root-flat` is the only generator target. Legacy Claude and Codex target names may be removed or retained only as non-materializing aliases to `root-flat`; neither generation nor validation reads or writes `.dist/claude` or `.dist/codex`. Agents that support nested source discovery may find `src/skills/`, but supported public consumption does not depend on recursive discovery.

The runtime-owner set is exactly `design-change`, `plan-change`, `implement-change`, `review-change`, `sync-truth`, and `close-change`, represented by `runtime_bundle = "harness"` in the skill contract. `analyze-project` remains a lifecycle owner but is runtime-free. For every skill, the generated tree equals its complete authored skill tree plus the specified provider-metadata projection; for the six runtime owners it additionally equals the production runtime manifest copied under `scripts/harness/`. The production runtime manifest contains the Python package files required for direct CLI execution and excludes tests, fixtures, caches, and development metadata. Generation and validation reject every missing, stale, or extra generated file.

### Implementation Surface

The repair restores the source and generator boundary around the already implemented Python runtime. It updates contracts, generator and checker code, lifecycle skill runtime paths, package tests, architecture truth, generated diagrams and index, and aggregate orchestration. It does not restore the retired Shell harness, the three compatibility skills, the three-run comparison gate, or `.dist/` as a tracked surface.

### Validation

Executable acceptance requires source-to-root-flat parity for all 39 skills, exact runtime-bundle parity for all six lifecycle owners, selected-skill copy tests from an unrelated temporary directory, native plugin validation, current `npx skills` discovery-shape characterization without performing a consumer installation, aggregate Python and contract tests, zero mutable Markdown hard wraps, and unchanged immutable exception digests.

### Recovery Policy

Use fix-forward repair inside this design scope. The current uncommitted flat tree and Python runtime are migration inputs, not rollback targets. Do not use a broad Git restore that would discard accepted Python runtime, codex-native, compatibility-retirement, checker, documentation, or Markdown changes. Whole-tree generation must build and validate a temporary sibling tree before atomically replacing `skills/`; if replacement fails, restore the immediately preceding generated tree. A failure-path oracle must prove that unsuccessful generation leaves the prior tree byte-for-byte intact.
