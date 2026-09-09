# Python Security Examples

These fragments illustrate effective controls. They are not a service, rotation framework, or CI pipeline, and they do not restore absolute requirements from `SKILL.md`. Copy only what the current boundary needs.

## Credential Access

Load secrets from the environment or the owned secret files. Do not add an encryption library unless the project already owns that store.

```python
import os

def database_password() -> str:
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise RuntimeError("DB_PASSWORD is required")
    return password
```

## Parameterized Queries

Bound parameters are the injection defense. Do not filter SQL keywords.

```python
import sqlite3

def find_user(conn: sqlite3.Connection, username: str):
    return conn.execute(
        "SELECT id, username FROM users WHERE username = ?",
        (username,),
    ).fetchone()
```

## Contextual Output Encoding

Encode for the output context. Do not detect `<script>` tags as the XSS control.

```python
import html

def render_username(username: str) -> str:
    return "<span>" + html.escape(username, quote=True) + "</span>"
```

## Input Boundaries

Validate the fields the operation needs. This is a type and length rule, not an injection filter.

```python
import re

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

def validate_username(username: str) -> str:
    if USERNAME_RE.fullmatch(username) is None:
        raise ValueError("username must be 3-30 ASCII letters, digits, or underscore")
    return username
```

## File Uploads

Cap size, avoid caller-supplied paths, and inspect content when the product distinguishes types by bytes. Suffix checks are not a MIME oracle.

Enforce the size limit while receiving or reading bytes, generate storage names independently of caller paths, and use exclusive creation where overwriting is not intended. A path-building fragment alone would prove neither the size limit nor safe storage.
