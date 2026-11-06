#!/usr/bin/env python3
"""
Supervised worker loop: ingest ledger, score every 15m, BLS wire-beater poll, Nostr on beat.
"""
from __future__ import annotations

import argparse
import logging
import os
import time

from primary_caller.beats import (
    maybe_publish_nostr_wire_beat,
    run_bls_watch_once,
    sync_beat_log_to_db,
)
from primary_caller.config import PUBLIC_KIT_ROOT
from primary_caller.db import utc_now_iso
from primary_caller.ledger import ingest_ledger
from primary_caller.scoring import persist_scores, score_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("primary-caller-worker")

DEFAULT_SCORE_INTERVAL_S = 15 * 60
DEFAULT_BLS_INTERVAL_S = 30


def tick(*, post_nostr: bool, bls_dry_run: bool) -> None:
    log.info("tick start %s", utc_now_iso())
    try:
        ingest_ledger()
    except FileNotFoundError as e:
        log.warning("ingest skipped: %s", e)

    try:
        scored = score_all()
        persist_scores(scored)
        log.info("scored %d predictions", len(scored))
    except Exception:
        log.exception("score failed")

    try:
        beat = run_bls_watch_once(dry_run=bls_dry_run, post_nostr=False)
        if beat and beat.get("event") == "bls_claims_detected" and post_nostr:
            maybe_publish_nostr_wire_beat()
        if beat:
            log.info("bls watch: %s", beat.get("event") or beat.get("status") or beat)
    except Exception:
        log.exception("bls watch failed")

    n = sync_beat_log_to_db()
    if n:
        log.info("synced %d beat events to db", n)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--score-interval",
        type=int,
        default=int(os.environ.get("WORKER_SCORE_INTERVAL_S", DEFAULT_SCORE_INTERVAL_S)),
        help="Seconds between score ticks (default 900)",
    )
    parser.add_argument(
        "--bls-interval",
        type=int,
        default=int(os.environ.get("WORKER_BLS_INTERVAL_S", DEFAULT_BLS_INTERVAL_S)),
        help="Seconds between BLS polls within a tick (worker runs BLS once per tick)",
    )
    parser.add_argument("--once", action="store_true", help="Single tick then exit")
    parser.add_argument(
        "--post-nostr",
        action="store_true",
        default=os.environ.get("NOSTR_NSEC", "").strip() != "",
        help="Publish Nostr on wire beat when NOSTR_NSEC set",
    )
    parser.add_argument(
        "--bls-dry-run",
        action="store_true",
        help="Use BLS fixture for beat detection (dev)",
    )
    args = parser.parse_args()

    log.info("worker cwd kit=%s", PUBLIC_KIT_ROOT)
    if args.once:
        tick(post_nostr=args.post_nostr, bls_dry_run=args.bls_dry_run)
        return

    while True:
        tick(post_nostr=args.post_nostr, bls_dry_run=args.bls_dry_run)
        time.sleep(max(60, args.score_interval))


if __name__ == "__main__":
    main()
