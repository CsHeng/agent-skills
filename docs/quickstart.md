# Quickstart

## Install From A Local Checkout

Generate the portable Skill tree, then expose one child link per public ID from `skills/<public-id>` into the compatible agent environment's standard Skill discovery directory. Keep one active discovery path per tool and public ID.

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
bash scripts/check.sh
```

Optional Claude and Codex plugin manifests are compatibility packaging surfaces. They are not required for a live-child-link installation and do not add workflow behavior.

## Choose A Skill

Use an explicitly named or confidently matched Skill directly. Use `use-coding-skills` only for ambiguous multi-stage requests or questions about Skill selection.

The usual formal flow is:

1. `design-change` defines the boundary and performs one bounded design review.
2. After user approval, `plan-change` creates an execution-grade plan and performs one bounded plan review.
3. After user approval, `implement-change` changes and verifies the repository, then performs one bounded implementation review.

Informal work does not inherit automatic review. A direct `review-change` request starts from one supplied bounded target and does not manufacture earlier phases.
