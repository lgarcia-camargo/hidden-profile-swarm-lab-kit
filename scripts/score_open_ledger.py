#!/usr/bin/env python3
"""Score open prediction ledger lines against USGS / BLS / NOAA primary URLs only."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_DIR = ROOT / "public-predictions"

ALLOWED_HOST_SUFFIXES = (
    "earthquake.usgs.gov",
    "www.bls.gov",
    "bls.gov",
    "www.tsunami.gov",
    "tsunami.gov",
)

USER_AGENT = "hidden-profile-swarm-lab-kit-score/1.0 (+public ledger scorer)"


def parse_utc(iso: str) -> datetime:
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    return datetime.fromisoformat(iso).astimezone(timezone.utc)


def host_allowed(url: str) -> bool:
    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower()
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


def fetch_primary(url: str, timeout: float = 45.0) -> tuple[bytes, str]:
    if not host_allowed(url):
        raise ValueError(f"URL not an allowed primary source: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), url


def load_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def score_usgs_m6_global(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    resolve = parse_utc(row["resolve_by_utc"])
    primary = row["verify"]["primary"]
    body, fetched = fetch_primary(primary)
    data = json.loads(body.decode())
    features = data.get("features") or []
    resolve_ms = int(resolve.timestamp() * 1000)
    hit = [
        f
        for f in features
        if (f.get("properties") or {}).get("mag", 0) >= 6.0
        and (f.get("properties") or {}).get("time", 0) <= resolve_ms
    ]
    if hit:
        status = "TRUE"
        detail = f"{len(hit)} feature(s) with mag>=6.0, e.g. id={hit[0].get('id')}"
    elif now >= resolve:
        status = "FALSE"
        detail = "No M>=6.0 in feed through resolve_by"
    else:
        status = "PENDING"
        detail = "No M>=6.0 yet; resolve_by not reached"
    return {"status": status, "detail": detail, "primary_url_fetched": fetched}


def score_usgs_45count(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    resolve = parse_utc(row["resolve_by_utc"])
    if now < resolve:
        return {
            "status": "PENDING",
            "detail": f"Resolution snapshot at {row['resolve_by_utc']}",
            "primary_url_fetched": None,
        }
    body, fetched = fetch_primary(row["verify"]["primary"])
    data = json.loads(body.decode())
    count = len(data.get("features") or [])
    threshold = 8
    status = "TRUE" if count >= threshold else "FALSE"
    return {
        "status": status,
        "detail": f"feature_count={count} (need >={threshold})",
        "primary_url_fetched": fetched,
    }


def score_bls_claims(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    resolve = parse_utc(row["resolve_by_utc"])
    primary = row["verify"]["primary"]
    if now < resolve - __import__("datetime").timedelta(hours=12):
        # Release typically same calendar day as resolve; before that window → pending
        pass
    try:
        body, fetched = fetch_primary(primary)
    except urllib.error.HTTPError as e:
        return {
            "status": "PENDING" if now < resolve else "FALSE",
            "detail": f"BLS fetch HTTP {e.code}",
            "primary_url_fetched": primary,
        }
    text = body.decode(errors="replace")
    # SA initial claims headline patterns (release day may vary)
    nums = re.findall(
        r"initial claims[^0-9]{0,80}([\d,]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not nums:
        nums = re.findall(r"seasonally adjusted initial claims[^0-9]{0,40}([\d,]+)", text, re.I)
    if not nums:
        if now < resolve:
            return {
                "status": "PENDING",
                "detail": "Could not parse SA initial claims from BLS primary page yet",
                "primary_url_fetched": fetched,
            }
        return {
            "status": "FALSE",
            "detail": "No parseable SA initial claims on primary page at/after resolve",
            "primary_url_fetched": fetched,
        }
    value = int(nums[0].replace(",", ""))
    status = "TRUE" if value > 225_000 else "FALSE"
    if now < resolve and value <= 225_000:
        status = "PENDING"
        detail = f"Parsed claims={value}; awaiting official release window ({row['resolve_by_utc']})"
    else:
        detail = f"Parsed SA initial claims={value} (threshold >225,000)"
    return {"status": status, "detail": detail, "primary_url_fetched": fetched}


def in_ring_of_fire_band(lat: float, lon: float) -> bool:
    if lat < -60 or lat > 60:
        return False
    # 100°E–260°E (wraps through Pacific): lon >= 100 or lon <= -100
    if lon >= 100 or lon <= -100:
        return True
    return False


def baseline_id_set(row: dict[str, Any]) -> set[str]:
    verify = row.get("verify") or {}
    ids = row.get("baseline_ids") or verify.get("baseline_ids") or []
    return set(ids)


def score_usgs_new_m5_rof(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    resolve = parse_utc(row["resolve_by_utc"])
    baseline_ids = baseline_id_set(row)
    body, fetched = fetch_primary(row["verify"]["primary"])
    data = json.loads(body.decode())
    resolve_ms = int(resolve.timestamp() * 1000)
    for f in data.get("features") or []:
        props = f.get("properties") or {}
        mag = props.get("mag") or 0
        eid = f.get("id") or ""
        t = props.get("time") or 0
        if mag < 5.0 or eid in baseline_ids or t > resolve_ms:
            continue
        coords = (f.get("geometry") or {}).get("coordinates") or [0, 0]
        lon, lat = coords[0], coords[1]
        if in_ring_of_fire_band(lat, lon):
            return {
                "status": "TRUE",
                "detail": f"New M>={mag} id={eid} at lat={lat}, lon={lon}",
                "primary_url_fetched": fetched,
            }
    if now >= resolve:
        return {
            "status": "FALSE",
            "detail": "No qualifying new M>=5.0 in Ring-of-Fire band through resolve_by",
            "primary_url_fetched": fetched,
        }
    return {
        "status": "PENDING",
        "detail": "No qualifying new event yet; resolve_by not reached",
        "primary_url_fetched": fetched,
    }


def score_noaa_tsunami_fiji(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    resolve = parse_utc(row["resolve_by_utc"])
    primary = row["verify"]["primary"]
    body, fetched = fetch_primary(primary)
    text = body.decode(errors="replace").lower()
    us_regions = ("west coast", "alaska", "hawaii", "california", "oregon", "washington")
    alert_words = ("warning", "advisory")
    fiji_markers = ("fiji", "7000tw8r", "us7000tw8r", "m6.1")
    has_us_alert = any(r in text for r in us_regions) and any(a in text for a in alert_words)
    references_fiji = any(m in text for m in fiji_markers)
    if has_us_alert and references_fiji:
        return {
            "status": "FALSE",
            "detail": "Board text suggests US-coast warning/advisory tied to Fiji M6.1 window",
            "primary_url_fetched": fetched,
        }
    if now >= resolve:
        return {
            "status": "TRUE",
            "detail": "No US-coast warning/advisory for Fiji M6.1 through resolve fetch",
            "primary_url_fetched": fetched,
        }
    return {
        "status": "PENDING",
        "detail": "No disqualifying alert yet; awaiting resolve_by",
        "primary_url_fetched": fetched,
    }


SCORERS = {
    "pred-usgs-m6-global-2026-11-12": score_usgs_m6_global,
    "pred-usgs-45count-2026-11-07T22Z": score_usgs_45count,
    "pred-bls-claims-2026-11-06": score_bls_claims,
    "pred-usgs-new-m5-rof-48h": score_usgs_new_m5_rof,
    "pred-noaa-us-tsunami-fiji-m61-24h": score_noaa_tsunami_fiji,
}


def score_row(row: dict[str, Any], now: datetime) -> dict[str, Any]:
    pid = row["prediction_id"]
    scorer = SCORERS.get(pid)
    base = {
        "prediction_id": pid,
        "category": row.get("category"),
        "resolve_by_utc": row["resolve_by_utc"],
    }
    if scorer is None:
        base.update(
            {
                "status": "PENDING",
                "detail": "No scorer registered for this prediction_id",
                "primary_url_fetched": None,
            }
        )
        return base
    try:
        result = scorer(row, now)
    except Exception as e:  # noqa: BLE001 — public script surfaces fetch/parse errors
        base.update(
            {
                "status": "PENDING",
                "detail": f"score_error: {type(e).__name__}: {e}",
                "primary_url_fetched": row["verify"].get("primary"),
            }
        )
        return base
    base.update(result)
    return base


def default_ledger_path() -> Path:
    candidates = sorted(PREDICTIONS_DIR.glob("open-ledger-*.jsonl"))
    if not candidates:
        raise FileNotFoundError("No open-ledger-*.jsonl in public-predictions/")
    return candidates[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="Path to open-ledger JSONL (default: newest public-predictions/open-ledger-*.jsonl)",
    )
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="ISO UTC timestamp for scoring (default: now)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: public-predictions/scores-YYYY-MM-DD.json)",
    )
    args = parser.parse_args()
    ledger = args.ledger or default_ledger_path()
    now = parse_utc(args.as_of) if args.as_of else datetime.now(timezone.utc)
    out_date = now.strftime("%Y-%m-%d")
    output = args.output or (PREDICTIONS_DIR / f"scores-{out_date}.json")

    rows = load_ledger(ledger)
    scored = [score_row(r, now) for r in rows]
    payload = {
        "scored_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ledger_file": ledger.name,
        "ledger_path": str(ledger.relative_to(ROOT)),
        "predictions": scored,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    pages_latest = ROOT / "docs" / "data" / "latest-scores.json"
    pages_latest.parent.mkdir(parents=True, exist_ok=True)
    pages_latest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {output} and {pages_latest} ({len(scored)} predictions)")
    for p in scored:
        print(f"  {p['prediction_id']}: {p['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
