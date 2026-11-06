from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

from primary_caller.config import (
    BEAT_LOG,
    BLS_WATCH_SCRIPT,
    NOSTR_SCRIPT,
    PUBLIC_KIT_ROOT,
    WIRE_BEAT_SCRIPT,
)
from primary_caller.db import connect, utc_now_iso


def insert_beat_event(payload: dict[str, Any], *, event_type: str | None = None) -> int:
    """Insert one beat row (API / wire-beater monitor)."""
    line = json.dumps(payload, separators=(",", ":"))
    recorded = (
        payload.get("first_seen_utc")
        or payload.get("recorded_at_utc")
        or utc_now_iso()
    )
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO beat_events (event_type, prediction_id, payload_json, recorded_at_utc)
            VALUES (?, ?, ?, ?)
            """,
            (
                event_type or payload.get("event") or payload.get("source", "beat"),
                payload.get("prediction_id") or payload.get("ledger_prediction_id"),
                line,
                recorded,
            ),
        )
        return int(cur.lastrowid)


def sync_beat_log_to_db() -> int:
    if not BEAT_LOG.is_file():
        return 0
    inserted = 0
    with connect() as conn:
        existing_hashes = {
            r["payload_json"]
            for r in conn.execute("SELECT payload_json FROM beat_events").fetchall()
        }
        for line in BEAT_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if line in existing_hashes:
                continue
            payload = json.loads(line)
            conn.execute(
                """
                INSERT INTO beat_events (event_type, prediction_id, payload_json, recorded_at_utc)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.get("event"),
                    payload.get("prediction_id"),
                    line,
                    payload.get("first_seen_utc") or payload.get("armed_utc") or utc_now_iso(),
                ),
            )
            inserted += 1
            existing_hashes.add(line)
    return inserted


def run_bls_watch_once(*, dry_run: bool = False, post_nostr: bool = False):
    if not BLS_WATCH_SCRIPT.is_file():
        return {"error": "watch_bls_release.py missing"}

    cmd = [sys.executable, str(BLS_WATCH_SCRIPT), "--once"]
    if dry_run:
        cmd.append("--dry-run")
    if post_nostr:
        cmd.append("--post-nostr")

    proc = subprocess.run(
        cmd,
        cwd=str(PUBLIC_KIT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or proc.stderr or "").strip()
    if not out:
        return None
    try:
        return json.loads(out.splitlines()[-1])
    except json.JSONDecodeError:
        return {"raw": out, "returncode": proc.returncode}


def publish_wire_beat_payload(payload_path: Path, *, dry_run: bool = False) -> None:
    if not WIRE_BEAT_SCRIPT.is_file():
        return
    cmd = [sys.executable, str(WIRE_BEAT_SCRIPT), "--payload", str(payload_path)]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, cwd=str(PUBLIC_KIT_ROOT), check=False)


def maybe_publish_nostr_wire_beat(payload_path: Path | None = None) -> None:
    nsec = __import__("os").environ.get("NOSTR_NSEC", "").strip()
    if payload_path and payload_path.is_file() and WIRE_BEAT_SCRIPT.is_file():
        publish_wire_beat_payload(payload_path, dry_run=not bool(nsec))
        return
    if not nsec or not NOSTR_SCRIPT.is_file():
        return
    env = {**dict(__import__("os").environ), "NOSTR_MODE": "wire-beat"}
    subprocess.run(
        [sys.executable, str(NOSTR_SCRIPT)],
        cwd=str(PUBLIC_KIT_ROOT),
        env=env,
        check=False,
    )


def list_beats(conn: sqlite3.Connection, limit: int = 50) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, event_type, prediction_id, payload_json, recorded_at_utc
        FROM beat_events ORDER BY id DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "event_type": r["event_type"],
                "prediction_id": r["prediction_id"],
                "recorded_at_utc": r["recorded_at_utc"],
                "payload": json.loads(r["payload_json"]),
            }
        )
    return out
