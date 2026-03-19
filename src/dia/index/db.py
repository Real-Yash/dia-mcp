"""SQLite persistence for indexed UI/UX patterns."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

from dia.config import DB_PATH

_CREATE = """
CREATE TABLE IF NOT EXISTS patterns (
    id              TEXT PRIMARY KEY,
    url             TEXT NOT NULL,
    category        TEXT,
    app_name        TEXT,
    flow_name       TEXT,
    description     TEXT,
    screenshot_b64  TEXT,
    markdown        TEXT,
    branding        TEXT,
    metadata        TEXT,
    tags            TEXT,
    indexed_at      TEXT
)
"""


async def init() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE)
        await db.commit()


async def save_pattern(data: dict[str, Any]) -> str:
    pid = hashlib.md5(
        f"{data.get('url', '')}:{data.get('flow_name', '')}".encode()
    ).hexdigest()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO patterns
                (id, url, category, app_name, flow_name, description,
                 screenshot_b64, markdown, branding, metadata, tags, indexed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                pid,
                data.get("url", ""),
                data.get("category", ""),
                data.get("app_name", ""),
                data.get("flow_name", ""),
                data.get("description", ""),
                data.get("screenshot_b64", ""),
                data.get("markdown", ""),
                json.dumps(data.get("branding", {})),
                json.dumps(data.get("metadata", {})),
                json.dumps(data.get("tags", [])),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()
    return pid


async def search_patterns(
    *,
    query: str = "",
    category: str = "",
    tags: str = "",
    limit: int = 20,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []
    if query:
        q = f"%{query}%"
        conditions.append(
            "(description LIKE ? OR app_name LIKE ? OR flow_name LIKE ? OR markdown LIKE ?)"
        )
        params.extend([q, q, q, q])
    if category:
        conditions.append("category = ?")
        params.append(category)
    if tags:
        for t in tags.split(","):
            conditions.append("tags LIKE ?")
            params.append(f"%{t.strip()}%")

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM patterns WHERE {where} ORDER BY indexed_at DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await (await db.execute(sql, params)).fetchall()
        return [
            {
                "id": r["id"],
                "url": r["url"],
                "app_name": r["app_name"],
                "flow_name": r["flow_name"],
                "category": r["category"],
                "description": r["description"],
                "tags": json.loads(r["tags"] or "[]"),
                "indexed_at": r["indexed_at"],
                "has_screenshot": bool(r["screenshot_b64"]),
            }
            for r in rows
        ]
