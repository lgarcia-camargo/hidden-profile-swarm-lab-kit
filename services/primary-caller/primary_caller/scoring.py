from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any

from primary_caller.config import LEDGER_PATH, PUBLIC_KIT_ROOT
from primary_caller.db import connect, utc_now_iso
from primary_caller.status import raw_to_board


def _import_scorer():
    scripts = PUBLIC_KIT_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import score_open_ledger as sol  # type: ignore

    return sol


def score_all(now: datetime | None = None) -> list[dict[str, Any]]:
    sol = _import_scorer()
    now = now or datetime.now(timezone.utc)
    rows = sol.load_ledger(LEDGER_PATH)
    return [sol.score_row(r, now) for r in rows]


def persist_scores(scored: list[dict[str, Any]]) -> None:
    scored_at = utc_now_iso()
    with connect() as conn:
        bankroll_row = conn.execute(
            "SELECT value FROM meta WHERE key = 'paper_bankroll_usd'"
        ).fetchone()
        bankroll = float(bankroll_row["value"])
        total_pnl = 0.0

        for p in scored:
            pid = p["prediction_id"]
            raw = p.get("status", "PENDING")
            board = raw_to_board(raw)
            conn.execute(
                """
                INSERT INTO scores (
                    prediction_id, board_status, raw_status, detail,
                    primary_url_fetched, scored_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    board,
                    raw,
                    p.get("detail"),
                    p.get("primary_url_fetched"),
                    scored_at,
                ),
            )

            bet = conn.execute(
                "SELECT * FROM paper_bets WHERE prediction_id = ?", (pid,)
            ).fetchone()
            if bet and not bet["settled"] and board in ("PASS", "FAIL"):
                stake = float(bet["stake_usd"])
                pnl = stake if board == "PASS" else -stake
                conn.execute(
                    """
                    UPDATE paper_bets SET pnl_usd = ?, settled = 1, updated_at_utc = ?
                    WHERE prediction_id = ?
                    """,
                    (pnl, scored_at, pid),
                )
                total_pnl += pnl

        if total_pnl != 0:
            bankroll = round(bankroll + total_pnl, 2)
            conn.execute(
                "UPDATE meta SET value = ? WHERE key = 'paper_bankroll_usd'",
                (str(bankroll),),
            )


def latest_scores_by_prediction(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT s.* FROM scores s
        INNER JOIN (
            SELECT prediction_id, MAX(id) AS max_id FROM scores GROUP BY prediction_id
        ) t ON s.prediction_id = t.prediction_id AND s.id = t.max_id
        """
    ).fetchall()
    return {r["prediction_id"]: r for r in rows}
