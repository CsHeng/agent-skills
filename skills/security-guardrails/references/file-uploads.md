# File Uploads

Read this when the product accepts files.

- Cap size, enforced while receiving or reading bytes.
- Inspect content when the distinction between types matters; a client-supplied MIME type or extension alone is not an oracle.
- Generate storage names independently of caller-supplied paths, and use exclusive creation where overwriting is not intended.
- Store outside the web root, or serve with non-executable permissions, when applicable.
