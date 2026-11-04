# Buildx Commands

Read this when running `docker buildx`. Builder selection, local build and publication are three separate steps because each is a side effect.

## Choose A Builder

Builder creation is a task-owned step. List builders first so the current default (marked `*`) is visible, then reuse the task-owned builder or create it without switching the default.

```bash
set -euo pipefail

# Show the current default builder (marked with *) before changing anything.
docker buildx ls

# Reuse the task-owned builder when it exists; otherwise create it. Creation does not switch the default.
docker buildx inspect multiarch-local >/dev/null 2>&1 \
  || docker buildx create --name multiarch-local --driver docker-container
```

Let the `buildx create` exit status propagate. Scope later commands with `--builder multiarch-local` instead of `docker buildx use`, so other projects keep their default builder. When you switch deliberately with `--use`, record the current default from `docker buildx ls` and restore it with `docker buildx use <original>` when done.

## Build Locally

Build both architectures to a local artifact; this step issues no push or publication, though it may pull base or BuildKit images from their registries. The OCI tarball is an artifact, not a runnable image.

```bash
docker buildx build \
  --builder multiarch-local \
  --platform linux/amd64,linux/arm64 \
  -t repo/app:tag \
  --output type=oci,dest=repo-app-tag.tar \
  .
```

To validate the native platform, load a single-platform image and run it:

```bash
docker buildx build \
  --builder multiarch-local \
  --platform linux/amd64 \
  -t repo/app:tag-local \
  --load \
  .
```

Replace `linux/amd64` with the host's native platform.

## Publish

Publish as a separate command, after explicit user authorization for this image and tag.

```bash
docker buildx build \
  --builder multiarch-local \
  --platform linux/amd64,linux/arm64 \
  -t repo/app:tag \
  --push \
  .
```

## Clean Up

Remove the builder when this task created it and no other project uses it.

```bash
docker buildx rm multiarch-local
```
