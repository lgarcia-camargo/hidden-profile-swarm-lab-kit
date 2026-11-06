#!/usr/bin/env python3
"""Publish the latest beat-log line to Nostr (wire-beat mode).

Uses NOSTR_NSEC like scripts/publish_nostr.py. Invoked by watch --post-nostr
or manually after a live detect.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "scripts" / "publish_nostr.py"


def main() -> None:
    env = {**os.environ, "NOSTR_MODE": "wire-beat"}
    rc = subprocess.run(
        [sys.executable, str(PUBLISH)],
        cwd=str(ROOT),
        env=env,
        check=False,
    ).returncode
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
