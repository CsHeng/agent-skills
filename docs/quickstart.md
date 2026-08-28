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

Select `design-change` when an unresolved persisted boundary needs a decision, `plan-change` when an accepted scope needs execution ordering and oracles, and `implement-change` when an explicit bounded mutation request or approved plan is ready. These capabilities may be used independently when their own preconditions are satisfied.

Invoke `review-change` for an explicit bounded review request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Review does not manufacture earlier work, and a review evaluator never owns repair.
