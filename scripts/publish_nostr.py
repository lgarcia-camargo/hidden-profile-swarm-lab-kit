#!/usr/bin/env python3
"""Publish pre-register or outcome notes to Nostr (repo secret NOSTR_NSEC)."""
from __future__ import annotations

import asyncio
import json
import os
import sys

from nostr_sdk import Client, EventBuilder, Keys, Kind, KindStandard, RelayUrl, init_logger, LogLevel


RECEIPT = "https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/predictions-live.html"
KALSHI_PAGE = "https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/kalshi-vs-ledger.html"


def build_posts(mode: str) -> list[str]:
    if mode == "kalshi-divergence":
        return [
            f"MARKET vs LEDGER — read-only Kalshi mids vs our pre-registered YES calls (research, not advice). {KALSHI_PAGE}",
        ]
    if mode == "outcome":
        return [
            f"OUTCOME CHECK: grades vs USGS/BLS/NOAA primaries. Receipt: {RECEIPT}",
        ]
    return [
        f"PRE-REGISTER (before the news): 5 falsifiable calls graded on government primaries only. Receipt: {RECEIPT}",
        "1) M≥6 on USGS 4.5_day before Nov 12 23:59Z",
        "2) USGS M4.5+ count ≥8 @ Nov 7 22:00Z (baseline 6)",
        "3) BLS initial claims SA >225k Thu Nov 6 release",
        "4) New M≥5 Ring-of-Fire quake before Nov 7 21:55Z",
        "5) No US tsunami WARNING for Fiji M6.1 through Nov 6 21:55Z",
    ]


async def publish(nsec: str, texts: list[str]) -> dict:
    init_logger(LogLevel.WARN)
    keys = Keys.parse(nsec)
    client = Client()
    for url in ("wss://nos.lol", "wss://relay.primal.net", "wss://relay.snort.social"):
        try:
            await client.add_relay(RelayUrl.parse(url))
        except Exception:
            pass
    await asyncio.wait_for(client.connect(), timeout=20)
    note_urls: list[str] = []
    for text in texts:
        event = EventBuilder(Kind.from_std(KindStandard.TEXT_NOTE), text).finalize(keys)
        await asyncio.wait_for(client.send_event(event), timeout=30)
        note_urls.append(f"https://njump.me/{event.id().to_hex()}")
    npub = keys.public_key().to_bech32()
    return {"npub": npub, "profile": f"https://njump.me/{npub}", "notes": note_urls}


def main() -> None:
    nsec = os.environ.get("NOSTR_NSEC", "").strip()
    if not nsec:
        print("NOSTR_NSEC missing", file=sys.stderr)
        sys.exit(1)
    mode = os.environ.get("NOSTR_MODE", "preregister")
    result = asyncio.run(publish(nsec, build_posts(mode)))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
