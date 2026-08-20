+++
artifact_kind = "design"
contract_version = 3
approval_status = "approved"

[scope]
impl_file_refs = ["README.md", "contracts", "docs/architecture", "docs/changelog/design-decisions.md", "scripts", "skills", "src/runtime/harness", "src/skills"]
test_file_refs = ["src/runtime/harness/tests", "tests"]
external_impl_file_refs = []
+++
# Design

Classification record: request_kind = accepted post-cutover correctness repair for findings F1-F9; change_class = regulated lifecycle-kernel repair; design_strength = design-full; truth_impact = high; boundary_impact = high; recommended_next_phase = mandatory review-design followed by plan-change after approval. The user's instruction spanning 2026-08-19 and 2026-08-20 authorizes the controller to complete review-design and, if the reviewed boundary passes, continue directly into plan-change without a second intermediate prompt.

## Problem

The Python harness introduced by `42f06e1` does not yet preserve nine approved lifecycle invariants. Task compilation and runtime binding accept contradictory delegation, isolation, external-touch, and parallel metadata and do not own batch admission (F1). A generic `reviewed -> in-progress` transition can reuse evidence from the prior attempt (F2). Design truth impact is not machine-bound to plan truth-sync scope (F3). Request classification and lifecycle phase routing were deleted with their Shell owners without a Python replacement (F4). Ledger replacement can report failure after authority has already advanced (F5). Artifact initialization and later digest checks disagree on CRLF bytes (F6). Changed-path containment accepts unsafe lexical paths (F7). Bounded-review briefs do not preserve a no-symlink, immutable-file identity boundary (F8). Required Markdown sections are detected by substring instead of exact structural headings (F9).

The existing approved cutover design already requires Python ownership of parsing, validation, classification, phase rules, immutable task topology, evidence, recovery, truth sync, close, and atomic state. This repair does not change that authority. It supplies the missing executable contract and introduces an explicit next artifact and ledger version so strengthened admission rules do not silently reinterpret version-3 authority.

## Goals

- G1 (F1): make task and batch authority executable before binding by validating every cross-field invariant, compiling named batch records, admitting only dependency-ready conflict-free work within effective capacity, and deriving immutable batch provenance inside the ledger rather than trusting caller-provided mappings.
- G2 (F2): make rejected review the only repair-reopen path; increment the active attempt, retain bounded review history, and clear verification, accepted review, external evidence, and batch provenance before new work can converge.
- G3 (F3): machine-bind design truth impact, design truth-sync requirement, plan truth-sync requirement, and non-empty stable truth scope so medium or high truth impact cannot initialize a plan that bypasses truth sync.
- G4 (F4): restore deterministic request classification and phase-transition operations in the shared Python runtime from repository-owned lifecycle, workflow-mode, and routing contracts.
- G5 (F5): make ledger persistence distinguish safely restored failure from indeterminate durability; never return an ordinary retryable write failure after promotion unless the preceding ledger is durably restored.
- G6 (F6): hash exact artifact bytes once, decode those same bytes as strict UTF-8, preserve CRLF identity, and return typed invalid-encoding errors without a second read.
- G7 (F7): validate every changed path as a safe normalized repository-relative reference before touch-set containment.
- G8 (F8): bind bounded-review evidence through a regular non-symlink file descriptor and verify stable file identity plus SHA-256 before envelope emission.
- G9 (F9): validate exact required Markdown heading lines outside fenced code using one per-artifact-kind structural contract.

## Boundaries

### Architecture Decision HCR-001: Versioned Admission Instead Of In-Place Version-3 Drift

The chosen boundary introduces artifact contract version 4 and ledger version 4 for all newly initialized work. Version 4 adds machine fields for design truth impact and truth-sync requirement, top-level plan execution policy and named parallel-batch records, and ledger-owned admission provenance. Version-3 artifacts and ledgers remain readable only for immutable evidence, digest verification, and completion of truth-sync or close for work already converged before runtime refresh; the upgraded runtime rejects new version-3 ledger initialization, task mutation, repair, admission, and binding. The current repair itself is the final version-3 bootstrap execution and must initialize, execute, review, and converge with the pre-refresh installed runtime before the upgraded plugin is consumed.

The status quo is rejected because adding optional version-3 fields cannot distinguish old evidence from newly authored plans and leaves a downgrade path around F1 and F3. Mutating version-3 meaning in place is rejected because the same version would carry two admission contracts. A general schema framework or open-ended multi-version compatibility layer is rejected because only versions 3 and 4 are needed: post-refresh v3 permits immutable-evidence and digest reads plus truth-sync or close evaluation only for work already converged before refresh, while v4 is the sole authoring, initialization, task-mutation, admission, repair, and binding path.

The Python harness owns parsing, validation, state, and typed errors. Repository contracts remain the source for kernel membership, workflow modes, phase routes, evaluator selection, and trigger-case ownership. Generation copies the minimum normalized contract resources required by runtime classification into each of the six skill-local harness bundles, and parity tests prove those resources match their authored owners. This preserves standalone skill closure without hand-maintained Python rule tables.

The lifecycle-cost owner is this repository's harness and generator. The marginal cost is one explicit version transition, two bounded compatibility readers, small copied contract resources, and model tests. The benefit is removal of silent authority downgrade and restoration of the already-approved sovereign kernel. A future version increment is justified only by another persisted authority-shape change; ordinary validation additions remain within version 4.

Recovery boundary: do not modify an approved artifact or ledger digest in place. The bootstrap ledger remains owned by the pre-refresh installed runtime through completion. If it is lost or corrupted after mutation begins, stop with typed evidence and reconstruct from the dependency-frozen pre-change revision rather than weakening v4 admission or hard-coding a plan digest exception.

### D1: Artifact And Truth Contract

Version 4 design metadata contains `truth_impact = none | low | medium | high` and `truth_sync_required = true | false`. Version 4 plan metadata contains the matching truth-sync flag, stable truth refs, `default_runtime_model_policy`, `parallel_execution_approved`, and complete named batch records. Compilation rejects design/plan truth disagreement. `truth_sync_required = true` always requires at least one safe stable truth ref inside plan implementation scope and outside `docs/plans/`; `false` always requires an empty stable truth set. Medium or high truth impact must select `true`, while low or none may select either value subject to the same total scope-cardinality rule.

The parser reads each artifact once as bytes, hashes those exact bytes, decodes strict UTF-8, and parses one TOML front-matter block. Required human sections are exact ATX heading lines outside fenced code. Version 4 requires design `# Design`, `## Problem`, `## Goals`, and `## Boundaries`; plan `# Plan`, `## Implementation`, `## Work Package Readiness`, `## Execution Continuity`, `## Recovery`, and `## Truth Sync Handoff`; truth-sync `# Truth Sync`, `## Scope`, `## Evidence`, `## Stable Truth Updates`, and `## Human Gate`; close `# Close` and `## Decision`. Version-3 documents use the same structural heading matcher with their existing required-heading set, so valid historical artifacts remain readable while substring-only false positives are rejected.

### D2: Task, Batch, And Binding Authority

Version 4 compilation rejects incompatible task combinations before ledger initialization. External refs require main execution, forbidden delegation and parallelism, group `none`, controller checkout, and at least one resource lock. Delegated writers require isolated worktrees. Shared-read-only tasks have no write refs. Parallel `required` or `allowed` tasks name an approved group; forbidden tasks use group `none`. Named batch membership, convergence owner, maximum width, peer dependency freedom, disjoint write sets, and disjoint resource locks are compiled into the immutable projection. Guarded rollback fields are complete only when that policy is selected; fix-forward tasks carry no rollback authority.

The ledger admits a serial task or named batch only from the ready set. It evaluates dependency freeze, approved membership, resource and write conflicts, runtime capacity, and effective width, then creates immutable provenance. `allowed` work may serialize with recorded evidence; unavailable `required` capacity returns a typed stop. `execute bind` consumes ledger-derived admission identity and rejects caller substitution. No backend or model policy may rewrite topology, locks, isolation, touch sets, or oracles.

### D3: Attempt And Review Evidence

The generic transition table has no `reviewed -> in-progress` edge. Rejected `record_review` is the sole repair-reopen operation. It validates the review budget, closes the current attempt into immutable per-attempt history, increments `repair_attempts`, and clears only active-attempt eligibility pointers before requiring fresh verification and focused review. Each historical attempt retains or digest-references its verification, review decision, external chain, and batch provenance. An external repair extends the retained parent-linked applied chain from the preceding attempt rather than replacing it. Accepted review can move only to `reviewed` and then `converged`; historical evidence remains auditable but never satisfies eligibility for the new active attempt.

### D4: Persistence, Digest, Path, And Review-Brief Trust

Ledger writes stage and fsync the new file, preserve a same-directory recovery candidate for the preceding ledger when one exists, open the parent directory before promotion, atomically promote, and fsync the parent. A pre-promotion failure leaves the old ledger unchanged. A post-promotion failure attempts an idempotent restoration and directory durability barrier. Confirmed restoration returns `ledger-write-failed`; inability to prove either promoted or restored durability returns `ledger-durability-unknown`, retains recovery evidence, forbids blind retry, and routes to stop-and-diagnose. A missing preceding ledger follows the same distinction without inventing rollback state.

Repository paths pass the same safe-reference validator at artifact admission and changed-path assertion: no absolute path, empty segment, `.` or `..`, control character, backslash alias, glob, or directory-escape spelling. Review briefs are opened without following symlinks where the platform supports it; otherwise lstat/open/fstat identity checks reject symlink or replacement races. Only regular files are accepted, and hashing and reading use the validated descriptor.

### D5: Classification And Phase Contract

The runtime exposes complete request-classification and next-phase operations, not field-at-a-time getters. Classification consumes a typed request and the copied workflow-mode contract, rejects contradictory or unknown inputs, and returns one mode plus its initial phase and owner. Phase transition consumes the current mode, phase, approval/evidence state, and routing contract and returns one typed next phase or terminal stop. Failure recovery remains a separate evidence-class route and cannot widen merely from retry count.

Canonical repository contracts remain authored under `contracts/` and `src/skills/session/use-coding-skills/references/routing.toml`. The root-flat generator copies the minimum exact resources into runtime bundles; the runtime never reaches outside its installed skill directory in standalone mode. Tests compare the copied bytes or normalized projection with the authored contracts and exercise the same classification and phase matrices from source and copied installations.

### Implementation Surface

Authored runtime changes are limited to `src/runtime/harness/{artifacts,ledger,binding,cli}.py`, a small versioned contract loader/resource when required, and their focused tests. Distribution changes are limited to the runtime-bundle contract and root-flat generator/checker needed to copy canonical lifecycle resources. Workflow-skill changes update version-4 authoring, admission, execution, truth-sync, close, and review guidance. Stable truth changes update README, `docs/architecture/harness-state-machine.md`, `docs/architecture/workflow-orchestration.md`, and the design-decision changelog. Generated `skills/` changes are projections only.

Existing uncommitted external-touch cleanup remains a separate completed slice. This repair must preserve it byte-for-byte except where a later generated refresh mechanically incorporates both authored states. It must not restore the deleted one-shot external-touch path, retired checkers, fixtures, goldens, or vacuous test.

Non-goals: no S1-S6 follow-up simplification, no new third-party runtime dependency, no provider-specific model identifier in reusable plans, no external-file mutation, no plugin install or cache refresh, no commit, no push, no release, and no live Herdr/provider action. The change does not reopen the 39-skill surface, runtime-owner set, codex-native default, explicit Herdr adapter, or source/generated distribution boundary.

### Oracle Strategy

The selected oracle mix is model/state-transition tests plus contract/schema conformance, failing example tests for local parser and trust boundaries, deterministic fault injection for persistence, and characterization against the deleted Shell behavior and current stable contracts. The protected boundary is lifecycle authority, persisted artifact identity, and standalone runtime closure. Oracle ownership stays with `src/runtime/harness/tests` for module/state behavior and `tests/` for distribution, CLI, generated, and stable-contract behavior. No oracle may weaken an exact state, error code, permission set, digest, path, or approval requirement.

### Validation

Acceptance requires red-first reproductions for all F1-F9; version-4 valid/invalid artifact matrices; version-3 immutable-evidence and digest reads plus truth-sync or close evaluation only for work already converged before refresh; explicit rejection tests for version-3 initialization, task transition, verification, review, external evidence, repair, batch or serial admission, and binding; task cross-field and named-batch model tests covering ready order, conflicts, capacity, allowed serialization, required stop, immutable provenance, and backend invariance; repair-attempt evidence reset tests; truth-impact mismatch and empty-scope rejection; classification and phase characterization from copied canonical contracts; directory-open, directory-fsync, restoration, and indeterminate-durability fault injection; CRLF and invalid-UTF-8 byte identity; unsafe changed-path rejection; symlink and swap-race review-brief rejection; exact-heading and fenced-code negatives; standalone copied-skill closure; generated parity; Ruff, ty, pytest, aggregate check, both plugin validators, and `git diff --check`.

### Recovery Policy

Use fix-forward for repository edits and deterministic test failures. Use stop-and-diagnose only for an observed `ledger-durability-unknown`, lost bootstrap ledger, artifact digest drift, or generated-tree replacement ambiguity; preserve evidence and do not retry, restore, refresh digests, or widen authority automatically. The generated tree continues to use staged validation and atomic replacement. No task receives guarded rollback authority.
