---
name: docker-multiarch-build
description: "Use for multi-architecture Docker builds: buildx, amd64/arm64 images, Compose platform behavior, image validation, and cross-platform containers."
---

# Docker Multi-Architecture Build

## Purpose

Build production images that run on both amd64 and arm64, using buildx and multi-stage Dockerfiles.

## Deterministic Steps

1. Use multi-stage builds to keep runtime images small.
2. Use build args for platform-specific builds when compiling binaries (Go).
3. Prefer non-root runtime users where possible.
4. Validate the image starts and passes a simple health check per platform.
5. Use `docker compose` (not `docker-compose`) for Compose v2+ compatibility.
6. If using compose, omit the `version` field (Compose v2+ ignores it).

## Minimal Commands

These examples keep three decisions separate: choosing a builder, building images locally, and publishing them. Selecting a builder and pushing an image are side effects, so each is its own explicit step rather than part of a generic build.

### Choose A Builder

Builder creation is a deliberate, task-owned step; it must not silently replace another project's default builder. List builders first so the current default (marked `*`) is visible, then create a named builder without switching to it.

```bash
set -euo pipefail

# Show the current default builder (marked with *) before changing anything.
docker buildx ls

# Create a task-owned builder. This does not switch the current default.
if ! docker buildx create --name multiarch-local --driver docker-container; then
  echo "ERROR: buildx builder 'multiarch-local' was not created" >&2
  exit 1
fi
```

A `docker buildx create` failure is a real failure and must stay visible; do not append `|| true` or otherwise swallow its exit status. Scope later commands with `--builder multiarch-local` instead of `docker buildx use`, so other projects keep their default builder.
If you deliberately switch with `--use`, record the current default from `docker buildx ls` and restore it with `docker buildx use <original>` when done.

### Build Locally

Build both architectures to a local artifact; this step issues no push or publication, but it may still pull base or BuildKit images from their registries.

```bash
docker buildx build \
  --builder multiarch-local \
  --platform linux/amd64,linux/arm64 \
  -t repo/app:tag \
  --output type=oci,dest=repo-app-tag.tar \
  .
```

### Publish

Push only when the user explicitly authorizes publication of this image and tag, as a separate command from the local build above.

```bash
docker buildx build \
  --builder multiarch-local \
  --platform linux/amd64,linux/arm64 \
  -t repo/app:tag \
  --push \
  .
```

### Clean Up

Remove the builder this example created; it is task-owned and not shared with other projects.

```bash
docker buildx rm multiarch-local
```

## Checklist

- Multi-stage Dockerfile
- Runtime image does not include build toolchain
- Non-root user for runtime
- Health check exists (or documented as intentionally omitted)
