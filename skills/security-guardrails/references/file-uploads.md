# File Uploads

Read this when the product accepts files.

- Cap size, enforced while receiving or reading bytes.
- Inspect content when the distinction between types matters; use client-supplied MIME types and extensions as untrusted metadata.
- Generate storage names independently of caller-supplied paths, and use exclusive creation when the intended behavior preserves existing files.
- Store outside the web root, or serve with non-executable permissions, when applicable.
