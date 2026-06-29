from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
              task_id TEXT PRIMARY KEY,
              model TEXT,
              state TEXT,
              prompt TEXT,
              response_json TEXT,
              created_at TEXT,
              updated_at TEXT
            )
            """
        )
        db.commit()


def upsert_task(db_path: Path, task_id: str, *, model: str = "nano-banana-pro", state: str = "created", prompt: str = "", response: dict | None = None) -> None:
    init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(response or {}, ensure_ascii=False)
    with sqlite3.connect(db_path) as db:
        db.execute(
            """
            INSERT INTO tasks(task_id, model, state, prompt, response_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
              state=excluded.state,
              response_json=excluded.response_json,
              updated_at=excluded.updated_at
            """,
            (task_id, model, state, prompt, payload, now, now),
        )
        db.commit()


def slugify(value: str, fallback: str = "image") -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return value[:80] or fallback


def download_urls(urls: list[str], output_dir: Path, *, prefix: str = "result") -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for index, url in enumerate(urls, start=1):
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix or ".png"
        path = output_dir / f"{slugify(prefix)}-{index}{ext}"

        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
        paths.append(path)
    return paths
