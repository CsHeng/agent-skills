# Python Service Patterns

Read this when creating or changing a Python service. Service boundaries, layering and dependency direction follow `architecture-patterns`; apply its smallest-sufficient-structure rule to the service's actual size.

## Conventions

- Use the project's Python version (3.13+ for a new project), `uv` for dependencies, and Ruff for formatting and linting under `python-guidelines`.
- Keep the application entrypoint thin.
- Configure logging once at startup, with structured context fields.
- Add a minimal health endpoint.

## Testing

- Unit-test business rules directly.
- Add integration tests for persistence and external IO where fakes cannot protect the real boundary.
