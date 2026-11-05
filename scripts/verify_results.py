#!/usr/bin/env python3
"""Verify pinned accuracy numbers from results.csv (no network, no LLM)."""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results.csv"
SUMMARY = ROOT / "summary.json"

# Headline claims reproduced from this kit (live track, 15-task pin).
EXPECTED = {
    ("live", "mesh"): (15, 15),
    ("live", "cot_partition", "hpl-09..15"): (0, 7),
}


def load_rows() -> list[dict]:
    with RESULTS.open(newline="") as f:
        return list(csv.DictReader(f))


def accuracy(rows: list[dict], track: str, regime: str, task_ids: set[str] | None = None) -> tuple[int, int]:
    correct = total = 0
    for r in rows:
        if r["track"] != track or r["regime"] != regime:
            continue
        if task_ids is not None and r["task_id"] not in task_ids:
            continue
        total += 1
        if r["correct"] in ("True", "true", "1"):
            correct += 1
    return correct, total


def main() -> int:
    if not RESULTS.is_file():
        print(f"missing {RESULTS}", file=sys.stderr)
        return 2
    rows = load_rows()
    ok = True

    c, t = accuracy(rows, "live", "mesh")
    exp_c_mesh, exp_t_mesh = EXPECTED[("live", "mesh")]
    print(f"live mesh: {c}/{t} (expected {exp_c_mesh}/{exp_t_mesh})")
    if (c, t) != (exp_c_mesh, exp_t_mesh):
        ok = False

    # task ids are full strings like hpl-09-datacenter-region
    task_ids_09_15 = {r["task_id"] for r in rows if r["task_id"].startswith("hpl-09") or r["task_id"].startswith("hpl-1")}
    task_ids_09_15 = {tid for tid in task_ids_09_15 if int(tid.split("-")[1]) >= 9}

    c, t = accuracy(rows, "live", "cot_partition", task_ids_09_15)
    exp_c, exp_t = EXPECTED[("live", "cot_partition", "hpl-09..15")]
    print(f"live cot_partition (hpl-09..15): {c}/{t} (expected {exp_c}/{exp_t})")
    if (c, t) != (exp_c, exp_t):
        ok = False

    if SUMMARY.is_file():
        summary = json.loads(SUMMARY.read_text())
        live_mesh = next(
            (g for g in summary.get("live", {}).get("regimes", []) if g["regime"] == "mesh"),
            None,
        )
        if live_mesh and live_mesh.get("correct") != exp_c_mesh:
            print("warning: summary.json live mesh count differs from CSV", file=sys.stderr)

    print("OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
