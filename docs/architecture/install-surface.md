# Install Surface

The portable install unit is one generated directory under `skills/<public-id>`. Each directory contains its own `SKILL.md`, projected provider metadata, and referenced resources. It does not resolve repository siblings or require executable workflow support.

The root-flat `skills/` tree is generated from `src/skills/` and checked for exact parity and reference closure. A local checkout with child symlinks is the recommended update path. Plugin manifests are optional packaging metadata and do not change Skill semantics.

When an approved repository change includes its generated payload, regenerating files already exposed by existing child symlinks is part of that scoped mutation; link existence alone does not require a separate installation approval or isolated candidate. Validation by itself grants no mutation authority. Creating or changing discovery links, user settings, plugin installations, or external deployment behavior remains a separate authorized action. If regeneration has an unexpected external effect beyond the approved payload, resolve that specific boundary before proceeding.

Existing links make changed files available for subsequent reads; they do not prove a running session has refreshed cached descriptions or previously loaded instructions. Report actual generation and checking separately from any unperformed reload or behavioral observation.
