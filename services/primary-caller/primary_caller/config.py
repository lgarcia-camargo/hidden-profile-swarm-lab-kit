from __future__ import annotations

import os
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KIT_ROOT = SERVICE_ROOT.parents[0]

DEFAULT_LEDGER = (
    PUBLIC_KIT_ROOT / "public-predictions" / "open-ledger-2026-11-05.jsonl"
)
DEFAULT_DB = SERVICE_ROOT / "var" / "primary-caller.db"
DEFAULT_HOST = os.environ.get("PRIMARY_CALLER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("PRIMARY_CALLER_PORT", "8787"))

PAPER_BANKROLL_USD = float(os.environ.get("PAPER_BANKROLL_USD", "10000"))
STAKE_FRACTION = float(os.environ.get("STAKE_FRACTION", "0.02"))

LEDGER_PATH = Path(os.environ.get("PRIMARY_CALLER_LEDGER", str(DEFAULT_LEDGER)))
DB_PATH = Path(os.environ.get("PRIMARY_CALLER_DB", str(DEFAULT_DB)))

SCORE_SCRIPT = PUBLIC_KIT_ROOT / "scripts" / "score_open_ledger.py"
BLS_WATCH_SCRIPT = PUBLIC_KIT_ROOT / "scripts" / "watch_bls_release.py"
NOSTR_SCRIPT = PUBLIC_KIT_ROOT / "scripts" / "publish_nostr.py"
WIRE_BEAT_SCRIPT = PUBLIC_KIT_ROOT / "scripts" / "publish_wire_beat.py"
BEAT_LOG = PUBLIC_KIT_ROOT / "docs" / "data" / "beat-log.jsonl"
API_BASE = os.environ.get(
    "PRIMARY_CALLER_API", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"
)
