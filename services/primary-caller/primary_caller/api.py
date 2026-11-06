from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from primary_caller.config import PAPER_BANKROLL_USD, SERVICE_ROOT, STAKE_FRACTION
from primary_caller.db import connect, loads_json, utc_now_iso
from primary_caller.beats import insert_beat_event, list_beats
from primary_caller.ledger import ingest_ledger
from primary_caller.scoring import latest_scores_by_prediction, persist_scores, score_all

app = FastAPI(title="Primary Caller API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

WEB_DIR = SERVICE_ROOT / "web" / "dist"
if WEB_DIR.is_dir():
    app.mount("/app", StaticFiles(directory=str(WEB_DIR), html=True), name="app")


class BeatIn(BaseModel):
    source: str = "bls"
    sa_initial_claims: int
    latency_ms: float
    primary_url: str
    ledger_prediction_id: str = "pred-bls-claims-2026-11-06"
    ledger_status: str
    threshold: int = 225_000
    page_fingerprint: Optional[str] = None
    dry_run: bool = False
    first_seen_utc: Optional[str] = None


class CallIn(BaseModel):
    prediction_id: str
    registered_at_utc: str
    resolve_by_utc: str
    claim: str
    category: Optional[str] = None
    verify: dict = Field(default_factory=dict)
    falsifier: Optional[str] = None


@app.on_event("startup")
def startup() -> None:
    try:
        ingest_ledger()
    except FileNotFoundError:
        pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "primary-caller", "utc": utc_now_iso()}


@app.get("/v1/board")
def get_board() -> dict[str, Any]:
    with connect() as conn:
        calls = conn.execute(
            "SELECT * FROM calls ORDER BY resolve_by_utc ASC"
        ).fetchall()
        scores = latest_scores_by_prediction(conn)
        bets = {
            r["prediction_id"]: dict(r)
            for r in conn.execute("SELECT * FROM paper_bets").fetchall()
        }
        bankroll = float(
            conn.execute("SELECT value FROM meta WHERE key = 'paper_bankroll_usd'").fetchone()["value"]
        )

    items: list[dict[str, Any]] = []
    for c in calls:
        pid = c["prediction_id"]
        sc = scores.get(pid)
        bet = bets.get(pid)
        items.append(
            {
                "prediction_id": pid,
                "category": c["category"],
                "claim": c["claim"],
                "registered_at_utc": c["registered_at_utc"],
                "resolve_by_utc": c["resolve_by_utc"],
                "verify": loads_json(c["verify_json"]),
                "status": sc["board_status"] if sc else "PENDING",
                "detail": sc["detail"] if sc else "Not scored yet",
                "scored_at_utc": sc["scored_at_utc"] if sc else None,
                "paper_stake_usd": bet["stake_usd"] if bet else None,
                "paper_pnl_usd": bet["pnl_usd"] if bet else None,
                "paper_settled": bool(bet["settled"]) if bet else False,
            }
        )

    with connect() as conn2:
        beats = list_beats(conn2, limit=20)

    return {
        "generated_at_utc": utc_now_iso(),
        "paper_bankroll_usd": bankroll,
        "calls": items,
        "recent_beats": beats,
    }


@app.get("/v1/track-record")
def track_record() -> dict[str, Any]:
    with connect() as conn:
        bankroll = float(
            conn.execute("SELECT value FROM meta WHERE key = 'paper_bankroll_usd'").fetchone()["value"]
        )
        scores = latest_scores_by_prediction(conn)
        bets = conn.execute("SELECT * FROM paper_bets").fetchall()

    settled = [b for b in bets if b["settled"]]
    wins = sum(1 for b in settled if (b["pnl_usd"] or 0) > 0)
    losses = sum(1 for b in settled if (b["pnl_usd"] or 0) < 0)
    total_pnl = sum(float(b["pnl_usd"] or 0) for b in settled)
    open_stake = sum(float(b["stake_usd"]) for b in bets if not b["settled"])

    by_status = {"PASS": 0, "FAIL": 0, "PENDING": 0}
    for sc in scores.values():
        by_status[sc["board_status"]] = by_status.get(sc["board_status"], 0) + 1

    return {
        "generated_at_utc": utc_now_iso(),
        "paper_bankroll_usd": bankroll,
        "starting_bankroll_usd": PAPER_BANKROLL_USD,
        "stake_fraction": STAKE_FRACTION,
        "record": {"wins": wins, "losses": losses, "pending": by_status.get("PENDING", 0)},
        "total_settled_pnl_usd": round(total_pnl, 2),
        "open_stake_reserved_usd": round(open_stake, 2),
        "board_summary": by_status,
    }


@app.post("/v1/calls")
def post_call(body: CallIn) -> dict[str, Any]:
    """Internal: register a new call (append-only ledger file not updated in v0)."""
    row = body.model_dump()
    with connect() as conn:
        exists = conn.execute(
            "SELECT 1 FROM calls WHERE prediction_id = ?", (body.prediction_id,)
        ).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="prediction_id already exists")

        now = utc_now_iso()
        bankroll = float(
            conn.execute("SELECT value FROM meta WHERE key = 'paper_bankroll_usd'").fetchone()["value"]
        )
        stake = round(bankroll * 0.02, 2)
        conn.execute(
            """
            INSERT INTO calls (
                prediction_id, registered_at_utc, resolve_by_utc, claim,
                category, verify_json, ledger_json, ingested_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                body.prediction_id,
                body.registered_at_utc,
                body.resolve_by_utc,
                body.claim,
                body.category,
                json.dumps(body.verify),
                json.dumps(row),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO paper_bets (
                prediction_id, stake_usd, bankroll_at_stake, pnl_usd, settled, updated_at_utc
            ) VALUES (?, ?, ?, NULL, 0, ?)
            """,
            (body.prediction_id, stake, bankroll, now),
        )
    return {"ok": True, "prediction_id": body.prediction_id, "stake_usd": stake}


@app.post("/v1/beats")
def post_beat(body: BeatIn) -> dict[str, Any]:
    """Wire-beater monitor: append BeatEvent (source of truth for product board)."""
    payload = body.model_dump()
    payload["event"] = "bls_claims_detected"
    payload["prediction_id"] = body.ledger_prediction_id
    beat_id = insert_beat_event(payload)
    return {"ok": True, "beat_id": beat_id, "ledger_status": body.ledger_status}


@app.post("/v1/admin/ingest")
def admin_ingest() -> dict[str, Any]:
    return ingest_ledger()


@app.post("/v1/admin/score")
def admin_score() -> dict[str, Any]:
    scored = score_all()
    persist_scores(scored)
    return {"scored": len(scored), "at": utc_now_iso()}
