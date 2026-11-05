# Hidden Profile Swarm Lab — public reproduction kit

Pinned artifacts for the **Hidden Profile Lab** program: fifteen decision tasks where no single analyst role can derive the correct answer from its private clue alone, but a **mesh integrator** that pools clues via coordination can.

This repository ships the **task pack**, **live swarm JSONL logs**, and **`results.csv`** so anyone can verify the headline comparison without access to our internal bench-hour tree:

| Track | Regime | Pinned result (this export) |
|-------|--------|-----------------------------|
| `live` | **mesh** (Regime A — integrator + role workers) | **15 / 15** correct |
| `live` | **cot_partition** (Regime C_partition — solo agent, one private clue only) | **0 / 7** on tasks `hpl-09` … `hpl-15` (see `runs/regime_c_partition.jsonl`) |

Simulator rows in `results.csv` (pinned-partition harness, 11 tasks) show the same pattern at smaller scale: mesh **11/11** vs solo shared-context CoT **0/11**.

## Clone and verify (no API keys)

```bash
git clone https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit.git
cd hidden-profile-swarm-lab-kit
python3 scripts/verify_results.py
```

You should see `live mesh: 15/15` and `live cot_partition (hpl-09..15): 0/7`, then `OK`.

Optional: inspect aggregates in `summary.json` or re-derive from CSV:

```bash
python3 -c "
import csv
from collections import Counter
rows=list(csv.DictReader(open('results.csv')))
for (track,regime),g in sorted(Counter((r['track'],r['regime']) for r in rows).items()):
    sub=[r for r in rows if r['track']==track and r['regime']==regime]
    c=sum(r['correct']=='True' for r in sub)
    print(f'{track} {regime}: {c}/{len(sub)}')
"
```

## Repository layout

| Path | Purpose |
|------|---------|
| `tasks.json` | 15 hidden-profile tasks (`question`, per-role `clues[]`, `ground_truth`) |
| `results.csv` | Simulator + live accuracy rows (schema in `docs/results.csv.schema.md`) |
| `summary.json` | Machine-readable rollups matching the gallery pin (2026-11-05) |
| `runs/regime_a.jsonl` | Live **mesh** integrator runs (Regime A) |
| `runs/regime_b.jsonl` | Live **competition_decide** runs (Regime B) |
| `runs/regime_c.jsonl` | Live full-clue **CoT** upper bound (Regime C) |
| `runs/regime_c_partition.jsonl` | Solo **partition** baseline (one clue, no pooling) |
| `lab-runner-manifest.json` | Path index used by internal runners |
| `docs/methodology.md` | Task design + regime definitions + citations |

## Reproduce live swarm numbers (full stack)

The JSONL files in `runs/` were produced on a **hosted swarmmy** deployment (multi-agent mail + channels), not by rerunning this repo alone. To replicate live mesh vs partition behavior you need:

1. Load each task from `tasks.json`.
2. **Mesh (Regime A):** spawn one worker per role with `question` + that role’s clue only; integrate on a shared channel; one final answer vs `ground_truth`.
3. **Partition (Regime C_partition):** single agent with `question` + **one** role’s clue (we pinned `analyst-a` batches in the JSONL); no cross-agent mail.
4. Append rows to `results.csv` with `track=live` and compare to this pin.

Task methodology and literature mapping: see `docs/methodology.md`.

## Literature (why these tasks exist)

- **HiddenBench** — Li, Naito, & Shirado (2025), *HiddenBench: Assessing Collective Reasoning in Multi-Agent LLMs via Hidden Profile Tasks*, [arXiv:2505.11556](https://arxiv.org/abs/2505.11556) ([HTML](https://arxiv.org/html/2505.11556v2)).
- **SILO-BENCH** — communication under partial observations, ACL 2026 long paper [2026.acl-long.1354](https://aclanthology.org/2026.acl-long.1354/).
- **Hidden profile (human groups)** — Stasser & Titus (1985); review in Schulz-Hardt & Mojzisch (2012).

Scenarios in `tasks.json` are **original** (not copied from HiddenBench HF text), following HiddenBench Study 1 practice.

## Simulator harness (optional)

Deterministic **simulator** rows in `results.csv` come from an internal pinned-partition Python harness (`run_lab.py` + `regimes.py`). That code is not vendored here; the CSV + JSONL pins are the reproducible surface for external readers.

## Issue policy

**If you run this kit and get different numbers, open an issue.** Include your `results.csv` diff, regime protocol, model IDs, and whether you used live swarm coordination or offline replay.

## License

MIT — see [LICENSE](LICENSE).
