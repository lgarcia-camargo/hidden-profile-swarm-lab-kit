#!/usr/bin/env python3
"""Publish one Wire Beater Nostr note + update Pages data (beat log + status).

Wire-beater-lead monitor calls this on primary-page change with JSON payload.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from nostr_sdk import Client, EventBuilder, Keys, Kind, KindStandard, RelayUrl, init_logger, LogLevel

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
RECEIPT = "https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/predictions-live.html"
WIRE_PAGE = "https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/wire-beater.html"
CANONICAL_NPUB = "npub1re8upn82vffnqgqqhcxyuq8vuu26nfyh3jvx59x6lmf0390a9wssee0ppk"


def ledger_label(status: str) -> str:
    if status in ("TRUE", "PASS"):
        return "PASS"
    if status in ("FALSE", "FAIL"):
        return "FAIL"
    return "PENDING"


def format_note(p: dict) -> str:
    src = p.get("source", "BLS").upper()
    n = p.get("sa_initial_claims")
    num = f"{n:,}" if isinstance(n, int) else str(n)
    lat = p.get("latency_ms")
    lat_s = f"{lat / 1000:.1f}s" if isinstance(lat, (int, float)) else "n/a"
    pred = p.get("ledger_prediction_id", "pred-bls-claims-2026-11-06")
    grade = ledger_label(str(p.get("ledger_status", "PENDING")))
    primary = p.get("primary_url", "")
    thresh = p.get("threshold", 225_000)
    return (
        f"PRIMARY WIRE BEAT ({src}): SA initial claims {num} "
        f"(first seen +{lat_s} after primary page change). "
        f"Pre-reg {pred}: {grade} (threshold >{thresh:,}). "
        f"Primary: {primary} · Receipt: {RECEIPT} · Log: {WIRE_PAGE}"
    )


async def publish_nostr(nsec: str, text: str) -> str:
    init_logger(LogLevel.WARN)
    keys = Keys.parse(nsec)
    client = Client()
    for url in ("wss://nos.lol", "wss://relay.primal.net"):
        await client.add_relay(RelayUrl.parse(url))
    await asyncio.wait_for(client.connect(), timeout=20)
    event = EventBuilder(Kind.from_std(KindStandard.TEXT_NOTE), text).finalize(keys)
    await asyncio.wait_for(client.send_event(event), timeout=30)
    return event.id().to_hex()


def write_artifacts(p: dict, note_id: str, note_url: str) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {
        "recorded_at_utc": now,
        "canonical_npub": CANONICAL_NPUB,
        "nostr_note": note_url,
        "note_id": note_id,
        **p,
    }
    log_path = DATA / "beat-log.jsonl"
    with log_path.open("a") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")
    status = {
        "updated_at_utc": now,
        "phase": "beat" if p.get("sa_initial_claims") is not None else "waiting",
        "next_event": "bls_initial_claims_2026-11-06",
        "monitor_owner": "wire-beater-lead",
        "last_beat": row,
        "canonical_npub": CANONICAL_NPUB,
        "receipt_url": RECEIPT,
    }
    (DATA / "wire-beater-status.json").write_text(json.dumps(status, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", type=Path, help="JSON payload file from monitor")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raw = os.environ.get("WIRE_BEAT_JSON", "")
    if args.payload:
        payload = json.loads(args.payload.read_text())
    elif raw:
        payload = json.loads(raw)
    else:
        print("Provide --payload or WIRE_BEAT_JSON", file=sys.stderr)
        sys.exit(1)

    text = format_note(payload)
    print("NOTE:\n", text, sep="")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "note": text}, indent=2))
        return

    nsec = os.environ.get("NOSTR_NSEC", "").strip()
    if not nsec:
        print("NOSTR_NSEC missing", file=sys.stderr)
        sys.exit(1)
    note_id = asyncio.run(publish_nostr(nsec, text))
    note_url = f"https://njump.me/{note_id}"
    write_artifacts(payload, note_id, note_url)
    print(json.dumps({"note_url": note_url, "note_id": note_id}, indent=2))


if __name__ == "__main__":
    main()
