from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.environ.get("CODETRACE_DB_PATH", "backend/codetrace.db"))


def _connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE IF NOT EXISTS snippets (id TEXT PRIMARY KEY, code TEXT NOT NULL, created_at TEXT NOT NULL)")
    connection.commit()
    return connection


def create_snippet(code: str) -> dict:
    snippet_id = uuid.uuid4().hex[:12]
    created_at = datetime.now(timezone.utc)
    with _connection() as connection:
        connection.execute("INSERT INTO snippets (id, code, created_at) VALUES (?, ?, ?)", (snippet_id, code, created_at.isoformat()))
    return {"id": snippet_id, "code": code, "created_at": created_at}


def get_snippet(snippet_id: str) -> dict | None:
    with _connection() as connection:
        row = connection.execute("SELECT id, code, created_at FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "code": row["code"], "created_at": datetime.fromisoformat(row["created_at"])}

