#!/usr/bin/env python3
"""Poll BLS primary URL; on change parse SA initial claims and append beat-log.jsonl."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BEAT_LOG = ROOT / "docs" / "data" / "beat-log.jsonl"
FIXTURE = ROOT / "fixtures" / "bls_claims_sample.html"
LEDGER = ROOT / "public-predictions" / "open-ledger-2026-11-05.jsonl"
PREDICTION_ID = "pred-bls-claims-2026-11-06"
CLAIMS_THRESHOLD = 225_000
DEFAULT_URL = "https://www.bls.gov/news.release/claims.nr0.htm"
USER_AGENT = "hidden-profile-swarm-lab-kit-wire-beater/1.0 (+public ledger monitor)"
WIRE_BEAT_SCRIPT = ROOT / "scripts" / "publish_wire_beat.py"
PAYLOAD_PATH = ROOT / "var" / "last-beat-payload.json"
API_BASE = __import__("os").environ.get("PRIMARY_CALLER_API", "http://127.0.0.1:8787")


def utc_now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def load_bls_primary_url() -> str:
    if not LEDGER.is_file():
        return DEFAULT_URL
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("prediction_id") == PREDICTION_ID:
            return row.get("verify", {}).get("primary") or DEFAULT_URL
    return DEFAULT_URL


def host_allowed(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host == "www.bls.gov" or host == "bls.gov" or host.endswith(".bls.gov")


def fetch_url(url: str, timeout: float = 45.0) -> tuple[bytes, dict[str, str]]:
    if not host_allowed(url):
        raise ValueError(f"URL not allowed: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return resp.read(), headers


def read_fixture(path: Path) -> tuple[bytes, dict[str, str]]:
    body = path.read_bytes()
    lm = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    return body, {"last-modified": lm, "etag": f'W/"fixture-{hashlib.sha256(body).hexdigest()[:16]}"'}


def parse_sa_initial_claims(text: str) -> int | None:
    nums = re.findall(r"initial claims[^0-9]{0,80}([\d,]+)", text, flags=re.IGNORECASE)
    if not nums:
        nums = re.findall(
            r"seasonally adjusted initial claims[^0-9]{0,40}([\d,]+)", text, re.I
        )
    if not nums:
        return None
    return int(nums[0].replace(",", ""))


def ledger_grade(sa_value: int | None) -> str | None:
    if sa_value is None:
        return None
    return "PASS" if sa_value > CLAIMS_THRESHOLD else "FAIL"


def ledger_status_for(sa_value: int | None) -> str:
    if sa_value is None:
        return "PENDING"
    return "TRUE" if sa_value > CLAIMS_THRESHOLD else "FALSE"


def build_wire_payload(
    *,
    sa_value: int | None,
    latency_ms: int,
    primary_url: str,
    content_hash: str,
    dry_run: bool,
    first_seen_utc: str,
) -> dict[str, Any]:
    return {
        "source": "bls",
        "sa_initial_claims": sa_value,
        "latency_ms": latency_ms,
        "primary_url": primary_url if not primary_url.startswith("fixture:") else DEFAULT_URL,
        "ledger_prediction_id": PREDICTION_ID,
        "ledger_status": ledger_status_for(sa_value),
        "threshold": CLAIMS_THRESHOLD,
        "page_fingerprint": content_hash,
        "dry_run": dry_run,
        "first_seen_utc": first_seen_utc,
    }


def post_beat_to_api(payload: dict[str, Any]) -> dict[str, Any] | None:
    body = json.dumps(
        {
            "source": payload["source"],
            "sa_initial_claims": payload["sa_initial_claims"],
            "latency_ms": payload["latency_ms"],
            "primary_url": payload["primary_url"],
            "ledger_prediction_id": payload["ledger_prediction_id"],
            "ledger_status": payload["ledger_status"],
            "threshold": payload["threshold"],
            "page_fingerprint": payload.get("page_fingerprint"),
            "dry_run": payload.get("dry_run", False),
            "first_seen_utc": payload.get("first_seen_utc"),
        }
    ).encode()
    req = urllib.request.Request(
        f"{API_BASE.rstrip('/')}/v1/beats",
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001 — monitor continues if API down
        return {"api_error": str(exc)}


def emit_wire_beat(payload: dict[str, Any], *, post_nostr: bool) -> None:
    PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAYLOAD_PATH.write_text(json.dumps(payload, indent=2))
    post_beat_to_api(payload)
    if not WIRE_BEAT_SCRIPT.is_file():
        return
    cmd = [sys.executable, str(WIRE_BEAT_SCRIPT), "--payload", str(PAYLOAD_PATH)]
    nsec = __import__("os").environ.get("NOSTR_NSEC", "").strip()
    if post_nostr and nsec and not payload.get("dry_run"):
        subprocess.run(cmd, cwd=str(ROOT), check=False)
    else:
        cmd.append("--artifacts-only")
        subprocess.run(cmd, cwd=str(ROOT), check=False)


def poll_once(
    *,
    url: str,
    dry_run: bool,
    state_path: Path,
    post_nostr: bool,
) -> dict[str, Any] | None:
    if dry_run:
        body, headers = read_fixture(FIXTURE)
        fetched_url = f"fixture:{FIXTURE.name}"
    else:
        body, headers = fetch_url(url)
        fetched_url = url

    content_hash = hashlib.sha256(body).hexdigest()
    state: dict[str, Any] = {}
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            state = {}

    etag = headers.get("etag")
    lm_raw = headers.get("last-modified") or headers.get("date")
    if not dry_run:
        unchanged = (
            state.get("content_hash") == content_hash
            and state.get("etag") == etag
            and state.get("last_modified") == lm_raw
        )
        if unchanged:
            return None

    first_seen_ms = utc_now_ms()
    ref_ms = first_seen_ms
    if lm_raw:
        try:
            ref_dt = datetime.strptime(lm_raw, "%a, %d %b %Y %H:%M:%S GMT").replace(
                tzinfo=timezone.utc
            )
            ref_ms = int(ref_dt.timestamp() * 1000)
        except ValueError:
            pass
    latency_ms = max(0, first_seen_ms - ref_ms)

    text = body.decode(errors="replace")
    sa_value = parse_sa_initial_claims(text)
    grade = ledger_grade(sa_value)

    first_seen_utc = datetime.fromtimestamp(
        first_seen_ms / 1000, tz=timezone.utc
    ).isoformat().replace("+00:00", "Z")
    if sa_value is None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                {
                    "content_hash": content_hash,
                    "etag": etag,
                    "last_modified": lm_raw,
                    "updated_utc": first_seen_utc,
                    "url": url,
                    "parse": "pending",
                },
                indent=2,
            )
        )
        return {
            "event": "bls_page_changed_unparsed",
            "primary_url": fetched_url,
            "content_hash": content_hash,
        }

    wire_payload = build_wire_payload(
        sa_value=sa_value,
        latency_ms=latency_ms,
        primary_url=fetched_url,
        content_hash=content_hash,
        dry_run=dry_run,
        first_seen_utc=first_seen_utc,
    )
    emit_wire_beat(wire_payload, post_nostr=post_nostr)
    record: dict[str, Any] = {
        "schema": "wire-beat/v1",
        "event": "bls_claims_detected",
        "prediction_id": PREDICTION_ID,
        "first_seen_utc": first_seen_utc,
        "first_seen_utc_ms": first_seen_ms,
        "first_seen_ms": first_seen_ms,
        "latency_ms": latency_ms,
        "sa_claims": sa_value,
        "sa_initial_claims": sa_value,
        "ledger_grade": grade,
        "ledger_status": wire_payload["ledger_status"],
        "ledger_rule": f"SA initial claims > {CLAIMS_THRESHOLD}",
        "primary_url": fetched_url,
        "content_hash": content_hash,
        "etag": etag,
        "last_modified": lm_raw,
        "dry_run": dry_run,
        "api_payload": wire_payload,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "content_hash": content_hash,
                "etag": etag,
                "last_modified": lm_raw,
                "updated_utc": record["first_seen_utc"],
                "url": url,
            },
            indent=2,
        )
    )
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch BLS claims release page")
    parser.add_argument("--url", default=None, help="Override primary URL")
    parser.add_argument("--dry-run", action="store_true", help="Use fixtures/bls_claims_sample.html")
    parser.add_argument("--once", action="store_true", help="Single poll then exit")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between polls")
    parser.add_argument(
        "--post-nostr",
        action="store_true",
        help="After detect, publish_wire_beat.py with NOSTR_NSEC (else artifacts-only)",
    )
    parser.add_argument(
        "--state-file",
        default=str(ROOT / "var" / "wire-beater-state.json"),
        help="Persist last content hash",
    )
    args = parser.parse_args()
    url = args.url or load_bls_primary_url()
    state_path = Path(args.state_file)

    while True:
        try:
            record = poll_once(
                url=url,
                dry_run=args.dry_run,
                state_path=state_path,
                post_nostr=args.post_nostr,
            )
            if record:
                print(json.dumps(record, indent=2))
            elif args.once:
                print(json.dumps({"status": "no_change", "url": url}))
        except urllib.error.HTTPError as e:
            err = {"error": "http", "code": e.code, "url": url}
            print(json.dumps(err), file=sys.stderr)
            if args.once:
                sys.exit(1)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"error": str(e), "url": url}), file=sys.stderr)
            if args.once:
                sys.exit(1)

        if args.once:
            break
        time.sleep(max(0.5, args.interval))


if __name__ == "__main__":
    main()
