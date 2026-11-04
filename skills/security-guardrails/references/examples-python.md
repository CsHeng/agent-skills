# Python Security Examples

These fragments illustrate effective controls. Copy only what the current boundary needs.

## Credential Access

Load secrets from the environment or the owned secret files, using the store the project already owns.

```python
import os

def database_password() -> str:
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise RuntimeError("DB_PASSWORD is required")
    return password
```

## Parameterized Queries

Bound parameters are the injection defense.

```python
import sqlite3

def find_user(conn: sqlite3.Connection, username: str):
    return conn.execute(
        "SELECT id, username FROM users WHERE username = ?",
        (username,),
    ).fetchone()
```

## Contextual Output Encoding

Encode for the output context.

```python
import html

def render_username(username: str) -> str:
    return "<span>" + html.escape(username, quote=True) + "</span>"
```

## Input Boundaries

Validate the fields the operation needs; this is a type and length rule.

```python
import re

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

def validate_username(username: str) -> str:
    if USERNAME_RE.fullmatch(username) is None:
        raise ValueError("username must be 3-30 ASCII letters, digits, or underscore")
    return username
```

## File Uploads

Follow `references/file-uploads.md`. A path-building fragment alone would prove neither the size limit nor safe storage; exercise both against real bytes.
