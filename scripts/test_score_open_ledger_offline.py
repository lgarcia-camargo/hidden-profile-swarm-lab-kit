#!/usr/bin/env python3
"""Offline tests for score_open_ledger helpers (no network)."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "score_open_ledger",
    ROOT / "scripts" / "score_open_ledger.py",
)
score = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(score)


class ScoreOpenLedgerOffline(unittest.TestCase):
    def test_host_allowed_usgs_bls_noaa(self) -> None:
        self.assertTrue(score.host_allowed("https://earthquake.usgs.gov/foo"))
        self.assertTrue(score.host_allowed("https://www.bls.gov/news.release/empsit.toc.htm"))
        self.assertTrue(score.host_allowed("https://www.tsunami.gov/"))
        self.assertFalse(score.host_allowed("https://example.com/feed"))

    def test_baseline_ids_nested_under_verify(self) -> None:
        row = {
            "verify": {
                "baseline_ids": ["us7000tw8r", "nc75462637"],
            }
        }
        self.assertEqual(score.baseline_id_set(row), {"us7000tw8r", "nc75462637"})

    def test_ring_of_fire_band(self) -> None:
        self.assertTrue(score.in_ring_of_fire_band(49.0, 147.0))
        self.assertTrue(score.in_ring_of_fire_band(-21.0, -178.0))
        self.assertFalse(score.in_ring_of_fire_band(35.0, 77.0))
        self.assertFalse(score.in_ring_of_fire_band(70.0, 120.0))

    def test_usgs_45count_pending_before_resolve(self) -> None:
        row = {"resolve_by_utc": "2099-01-01T00:00:00Z", "verify": {"primary": "https://earthquake.usgs.gov/x"}}
        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        out = score.score_usgs_45count(row, now)
        self.assertEqual(out["status"], "PENDING")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
