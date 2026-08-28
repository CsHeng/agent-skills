# Install Surface

The portable install unit is one generated directory under `skills/<public-id>`. Each directory contains its own `SKILL.md`, projected provider metadata, and referenced resources. It does not resolve repository siblings or require executable workflow support.

The root-flat `skills/` tree is generated from `src/skills/` and checked for exact parity and reference closure. A local checkout with child symlinks is the recommended update path. Plugin manifests are optional packaging metadata and do not change Skill semantics.
