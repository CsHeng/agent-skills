---
name: docker-multiarch-build
description: "Use for multi-architecture Docker builds: buildx, amd64/arm64 images, Compose platform behavior, image validation, and cross-platform containers."
---

# Docker Multi-Architecture Build

Build production images that run on both amd64 and arm64, using buildx and multi-stage Dockerfiles.

## Steps

1. Use multi-stage builds so the runtime image holds no build toolchain.
2. Cross-compile compiled binaries (Go) with the `BUILDPLATFORM`, `TARGETOS` and `TARGETARCH` build args.
3. Run the container as a non-root user where possible; container hardening follows `security-guardrails`.
4. Validate per platform that the image starts and passes a simple health check (or document the health check as intentionally omitted). Load and run the native-platform image with `--load`; for the other platform, use a runtime already available and prefer cross-compilation over emulated builds.
5. Use `docker compose`, and write Compose files without a `version` field.
6. Run builder selection, local build and push as three separate steps; the commands are in `references/buildx-commands.md`, which applies whenever you run `docker buildx`.
