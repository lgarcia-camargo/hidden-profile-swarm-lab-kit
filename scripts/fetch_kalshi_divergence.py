#!/usr/bin/env python3
"""Read-only Kalshi public API → kalshi-divergence.json (no trading)."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = Path(__file__).resolve().parents[1]
OUT_PATHS = [
    ROOT / "public-predictions" / "kalshi-divergence.json",
    ROOT / "docs" / "data" / "kalshi-divergence.json",
]


def fetch(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=45) as resp:
        return json.load(resp)


def mid_from_ob(ticker: str) -> float | None:
    try:
        ob = fetch(f"/markets/{ticker}/orderbook").get("orderbook_fp", {})
        yes = ob.get("yes_dollars") or []
        no = ob.get("no_dollars") or []
        best_yes = max((float(x[0]) for x in yes), default=0.0)
        best_no = max((float(x[0]) for x in no), default=0.0)
        if best_yes and best_no:
            return round((best_yes + (1.0 - best_no)) / 2.0, 4)
        if best_yes:
            return round(best_yes, 4)
        if best_no:
            return round(1.0 - best_no, 4)
    except OSError:
        pass
    return None


def kalshi_url(ticker: str, series_ticker: str | None) -> str:
    series = (series_ticker or ticker.split("-")[0]).lower()
    return f"https://kalshi.com/markets/{series}/{ticker.lower()}"


def market_bundle(ticker: str, match_note: str) -> dict:
    m = fetch(f"/markets/{ticker}")["market"]
    series = m.get("series_ticker") or m.get("event_ticker") or ticker.split("-")[0]
    return {
        "ticker": ticker,
        "kalshi_url": kalshi_url(ticker, series),
        "title": m.get("title"),
        "yes_sub_title": m.get("yes_sub_title"),
        "floor_strike": m.get("floor_strike"),
        "close_time_utc": m.get("close_time"),
        "yes_mid": mid_from_ob(ticker),
        "status": m.get("status"),
        "result": m.get("result") or None,
        "expiration_value": m.get("expiration_value"),
        "match_note": match_note,
    }


def build() -> dict:
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    specs = [
        {
            "prediction_id": "pred-bls-claims-2026-11-06",
            "ledger_boolean": "YES",
            "ledger_claim_summary": "SA initial jobless claims > 225,000 (Nov 6 BLS release)",
            "kalshi": market_bundle(
                "KXJOBLESSCLAIMS-26NOV12-215000",
                "Open macro proxy: >=215k for week ending Nov 7 (Nov 12 Kalshi window). "
                "No >225k strike on API; Nov 5 >=220k market finalized (189k). "
                "Ledger week ending Nov 1 — confirm against DOL/BLS headline.",
            ),
            "kalshi_reference_finalized": market_bundle(
                "KXJOBLESSCLAIMS-26NOV05-220000",
                "Prior Kalshi week ending Oct 31; settled before Nov 6 ledger resolve.",
            ),
        },
        {
            "prediction_id": "pred-usgs-m6-global-2026-11-12",
            "ledger_boolean": "YES",
            "ledger_claim_summary": "Any M>=6.0 in USGS feeds before Nov 12 23:59Z",
            "kalshi": market_bundle(
                "KXBIGGESTQUAKE-06NOV26-6.0",
                "Daily max magnitude market (Nov 6 UTC), not identical to cumulative USGS M6+ through Nov 12.",
            ),
        },
        {
            "prediction_id": "pred-usgs-45count-2026-11-07T22Z",
            "ledger_boolean": "YES",
            "ledger_claim_summary": "USGS 4.5_day feature count >= 8 at snapshot",
            "kalshi": None,
            "kalshi_match_note": "No Kalshi series maps to USGS GeoJSON feature count.",
        },
        {
            "prediction_id": "pred-usgs-new-m5-rof-48h",
            "ledger_boolean": "YES",
            "ledger_claim_summary": "New M>=5 Ring-of-Fire quake within 48h",
            "kalshi": market_bundle(
                "KXBIGGESTQUAKE-06NOV26-5.8",
                "Loose proxy: P(daily max M>=5.8 on Nov 6); not new-id RoF M5+.",
            ),
        },
        {
            "prediction_id": "pred-noaa-us-tsunami-fiji-m61-24h",
            "ledger_boolean": "YES",
            "ledger_claim_summary": "No US tsunami WARNING/ADVISORY for Fiji M6.1 origin",
            "kalshi": None,
            "kalshi_match_note": "No tsunami Kalshi contract on public API.",
        },
    ]

    pairs = []
    for spec in specs:
        kalshi = spec.get("kalshi")
        note = spec.get("kalshi_match_note")
        if kalshi and isinstance(kalshi, dict):
            note = note or kalshi.get("match_note")
        row = {
            "prediction_id": spec["prediction_id"],
            "ledger_boolean": spec["ledger_boolean"],
            "ledger_implied_yes_prob": 1.0,
            "ledger_claim_summary": spec["ledger_claim_summary"],
            "kalshi": kalshi,
            "kalshi_match_note": note,
        }
        if spec.get("kalshi_reference_finalized"):
            row["kalshi_reference_finalized"] = spec["kalshi_reference_finalized"]
        mid = kalshi.get("yes_mid") if kalshi else None
        row["divergence_from_ledger"] = round(abs(mid - 1.0), 4) if mid is not None else None
        pairs.append(row)

    return {
        "schema": "kalshi-ledger-divergence/v1",
        "disclaimer": "Research only — not investment advice. Read-only Kalshi public API; no trades; no wallet.",
        "api_base": BASE + "/",
        "fetched_at_utc": fetched,
        "ledger_pin": "https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/blob/main/public-predictions/open-ledger-2026-11-05.jsonl",
        "pages_url": "https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/kalshi-vs-ledger.html",
        "pairs": pairs,
    }


def main() -> None:
    doc = build()
    text = json.dumps(doc, indent=2) + "\n"
    for path in OUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
