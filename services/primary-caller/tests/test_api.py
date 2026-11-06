from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
KIT = SERVICE_ROOT.parents[0]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    ledger = KIT / "public-predictions" / "open-ledger-2026-11-05.jsonl"
    monkeypatch.setenv("PRIMARY_CALLER_DB", str(db))
    monkeypatch.setenv("PRIMARY_CALLER_LEDGER", str(ledger))
    monkeypatch.setenv("PAPER_BANKROLL_USD", "10000")

    from primary_caller import config

    config.DB_PATH = db
    config.LEDGER_PATH = ledger

    from importlib import reload
    import primary_caller.api as api_mod

    reload(api_mod)
    with TestClient(api_mod.app) as c:
        c.post("/v1/admin/ingest")
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_board_after_startup(client):
    r = client.get("/v1/board")
    assert r.status_code == 200
    data = r.json()
    assert data["paper_bankroll_usd"] == 10000.0
    assert len(data["calls"]) == 5
    assert all("status" in c for c in data["calls"])


def test_track_record(client):
    r = client.get("/v1/track-record")
    assert r.status_code == 200
    data = r.json()
    assert data["stake_fraction"] == 0.02
    assert data["record"]["pending"] >= 0


def test_post_call_internal(client):
    body = {
        "prediction_id": "pred-test-internal",
        "registered_at_utc": "2026-11-06T00:00:00Z",
        "resolve_by_utc": "2026-11-07T00:00:00Z",
        "claim": "Test claim",
        "category": "test",
        "verify": {"primary": "https://example.com"},
    }
    r = client.post("/v1/calls", json=body)
    assert r.status_code == 200
    assert r.json()["stake_usd"] == 200.0
