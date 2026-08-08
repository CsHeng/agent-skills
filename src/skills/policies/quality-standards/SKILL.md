---
name: quality-standards
description: "Compatibility entry for explicitly named quality-standards requests; hand off repository-owned gates to development-standards."
---

# Quality Standards Compatibility

Use this skill only when the user explicitly names `quality-standards` or an existing thin host entry selects this public ID. It remains an explicit compatibility helper and owns no universal thresholds or independent report.

Route the request as follows:

- `development-standards` owns repository-specific maintainability and quality gate policy
- `testing-strategy` owns executable test evidence and CI verification lanes
- the matching language guideline owns linter, formatter, type-checker, and language test-runner configuration

Do not recreate generic complexity, maintainability-index, coverage, duplicate, or debt targets. Preserve this public ID until a separately approved compatibility migration removes it.
