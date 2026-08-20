# Portable Skill Surface

`src/skills/` is nested authored truth. `skills/` is the sole materialized root-flat 39-skill payload consumed by live Agent Skills discovery, both optional plugin manifests, and compatible consumer-managed `npx skills` installation.

`src/runtime/harness/` is the single authored non-discoverable Python lifecycle runtime. Exactly `design-change`, `plan-change`, `implement-change`, `review-change`, `sync-truth`, and `close-change` declare `runtime_bundle = "harness"`; generation copies the production manifest into each owner at `scripts/harness/`. `analyze-project` remains lifecycle-owned and runtime-free.

Standalone distribution is closed at the skill directory. A selected lifecycle skill never depends on a repository sibling or a separately installed support skill.

The recommended local topology keeps a Git checkout as the single physical payload and creates one child symlink per selected public ID under `~/.agents/skills/`. Updates use the checkout's Git remote and appear to compatible tools in new sessions. Third-party collections use their own local clones and the same live-link model. Provider-specific roots may link to those generated directories only after consumers that scan both roots pass duplicate-name probes. The invariant is one active discovery path per tool and public ID.

Claude Code and Codex plugin manifests remain optional compatibility. `npx skills` remains compatible but non-recommended because copied destinations create independent update, removal, cleanup, and duplicate-exposure state owned by the consumer and upstream CLI.

`.dist/` remains ignored and inert. Generation and validation neither read nor write provider-specific payloads there.

## Validation

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

Generation builds and validates a temporary sibling tree before atomically replacing `skills/`. The aggregate check verifies exact authored-to-generated parity, the six no-missing-or-extra production bundles, and copied skill execution from an unrelated temporary directory.
