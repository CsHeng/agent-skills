+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "low"
truth_sync_required = false

[scope]
impl_file_refs = ["src/runtime/harness/artifacts.py", "src/runtime/harness/ledger.py", "skills"]
test_file_refs = ["src/runtime/harness/tests/test_v4_artifacts.py", "src/runtime/harness/tests/test_v4_ledger.py", "src/runtime/harness/tests/test_ledger.py", "tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []
+++
# Design

## Problem

The final bounded review of the approved HCR-001 implementation found five causally introduced contract violations after all aggregate checks passed: version-4 ledgers accept version-3 truth-sync or close artifacts, independent serial tasks can hold simultaneous active admissions, Windows drive-qualified repository references pass the portable path validator, pseudo-closing Markdown fences can expose headings that remain inside a real code block, and two pre-promotion ledger operations can leak raw operating-system errors instead of the typed durability result. The user reviewed that exact finding set and explicitly approved proceeding on 2026-08-20.

## Goals

- Enforce artifact/ledger version equality at truth-sync and close while retaining the already-converged version-3 compatibility tail.
- Make one ledger admission the exclusive active execution frontier unless all active peers entered through the same approved named-batch admission.
- Reject Windows drive-qualified repository references on every platform and recognize only syntactically valid Markdown closing fences.
- Bring parent creation and predecessor snapshot reads inside the typed pre-promotion ledger-write boundary.
- Refresh the six generated runtime bundles and prove the full repository acceptance surface again.

## Boundaries

This is a bounded follow-up inside approved architecture decision HCR-001. It changes no lifecycle owner, artifact or ledger version, task topology model, external-file authority, provider binding, stable documentation claim, public skill identity, or runtime bundle owner. All five repairs are fail-closed corrections to the already approved version-4 contract. Version 3 remains readable only for immutable evidence and digest verification plus truth-sync or close for work already converged before refresh. No external file, install, commit, push, publish, deploy, truth-sync approval, or close approval is authorized.

The design has low truth impact because stable documentation already states the intended behavior and requires no update when implementation is brought into conformance. The generated `skills/` tree remains a projection of authored runtime source and must be refreshed only through the repository generator. Recovery is fix-forward. Any new authority requirement, indeterminate ledger durability during execution, generated-tree replacement ambiguity, or finding outside these five contracts stops rather than widening this repair.
