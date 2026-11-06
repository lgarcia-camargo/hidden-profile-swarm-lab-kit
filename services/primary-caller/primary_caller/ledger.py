from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from primary_caller.config import LEDGER_PATH, STAKE_FRACTION
from primary_caller.db import connect, utc_now_iso


def load_ledger_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def ingest_ledger(path: Path | None = None) -> dict[str, int]:
    ledger = path or LEDGER_PATH
    if not ledger.is_file():
        raise FileNotFoundError(f"Ledger not found: {ledger}")

    rows = load_ledger_jsonl(ledger)
    inserted = 0
    bets = 0
    now = utc_now_iso()

    with connect() as conn:
        bankroll = float(conn.execute(
            "SELECT value FROM meta WHERE key = 'paper_bankroll_usd'"
        ).fetchone()["value"])

        for row in rows:
            pid = row["prediction_id"]
            existing = conn.execute(
                "SELECT prediction_id FROM calls WHERE prediction_id = ?", (pid,)
            ).fetchone()
            if existing:
                continue
            conn.execute(
                """
                INSERT INTO calls (
                    prediction_id, registered_at_utc, resolve_by_utc, claim,
                    category, verify_json, ledger_json, ingested_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    row.get("registered_at_utc", ""),
                    row.get("resolve_by_utc", ""),
                    row.get("claim", ""),
                    row.get("category"),
                    json.dumps(row.get("verify") or {}),
                    json.dumps(row),
                    now,
                ),
            )
            inserted += 1

            bet_exists = conn.execute(
                "SELECT prediction_id FROM paper_bets WHERE prediction_id = ?", (pid,)
            ).fetchone()
            if not bet_exists:
                stake = round(bankroll * STAKE_FRACTION, 2)
                conn.execute(
                    """
                    INSERT INTO paper_bets (
                        prediction_id, stake_usd, bankroll_at_stake, pnl_usd,
                        settled, updated_at_utc
                    ) VALUES (?, ?, ?, NULL, 0, ?)
                    """,
                    (pid, stake, bankroll, now),
                )
                bets += 1

    return {"calls_inserted": inserted, "paper_bets_created": bets, "ledger": str(ledger)}
