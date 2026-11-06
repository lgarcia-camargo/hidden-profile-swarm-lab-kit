from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from primary_caller import config
from primary_caller.config import PAPER_BANKROLL_USD

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    prediction_id TEXT PRIMARY KEY,
    registered_at_utc TEXT NOT NULL,
    resolve_by_utc TEXT NOT NULL,
    claim TEXT NOT NULL,
    category TEXT,
    verify_json TEXT NOT NULL,
    ledger_json TEXT NOT NULL,
    ingested_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id TEXT NOT NULL,
    board_status TEXT NOT NULL,
    raw_status TEXT NOT NULL,
    detail TEXT,
    primary_url_fetched TEXT,
    scored_at_utc TEXT NOT NULL,
    UNIQUE(prediction_id, scored_at_utc)
);

CREATE TABLE IF NOT EXISTS paper_bets (
    prediction_id TEXT PRIMARY KEY,
    stake_usd REAL NOT NULL,
    bankroll_at_stake REAL NOT NULL,
    pnl_usd REAL,
    settled INTEGER NOT NULL DEFAULT 0,
    updated_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS beat_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    prediction_id TEXT,
    payload_json TEXT NOT NULL,
    recorded_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_db(path: Path | None = None) -> Path:
    db = path or config.DB_PATH
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA)
        row = conn.execute("SELECT value FROM meta WHERE key = ?", ("paper_bankroll_usd",)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                ("paper_bankroll_usd", str(PAPER_BANKROLL_USD)),
            )
        conn.commit()
    return db


@contextmanager
def connect(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = db_path or config.DB_PATH
    ensure_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_meta(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def loads_json(text: str | None) -> Any:
    if not text:
        return None
    return json.loads(text)
