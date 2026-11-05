---
name: Falsification report
description: You reproduced the kit and got different numbers than the pinned mesh/partition claims
title: "[falsify] "
labels: ["falsification", "needs-triage"]
assignees: []
---

## What you expected (from this repo's pin)

- Live **mesh**: 15/15 correct on `tasks.json`
- Live **cot_partition** on `hpl-09` … `hpl-15`: 0/7 correct

Reference: `python3 scripts/verify_results.py` on `main`.

## What you observed

| Regime | Your correct/total | Task subset (if not full pin) |
|--------|-------------------|-------------------------------|
| mesh | / | |
| cot_partition (or other) | / | |

Paste the exact `verify_results.py` output (or equivalent script output):

```
(paste here)
```

## Reproduction protocol

- [ ] Ran `scripts/verify_results.py` on a clean clone of this repo (no CSV edits)
- [ ] Re-ran **live swarm** coordination (Regime A mesh / partition) and appended to `results.csv`
- [ ] Offline replay / simulator harness
- [ ] Other (describe below)

**Environment**

- Date of run:
- Model IDs (if LLM involved):
- Swarm stack (if live): hosted swarmmy / other / N/A
- Git commit SHA of this kit:

## Artifacts

Attach or link:

- Diff of your `results.csv` vs `main` (or full file)
- Relevant JSONL under `runs/` if you regenerated live logs
- Any runner config that differs from `docs/methodology.md`

## Hypothesis (optional)

What might explain the mismatch? (protocol drift, task parsing, integrator not pooling clues, etc.)

---

Maintainers respond on this issue only. No direct email — see [PROFILE.md](../PROFILE.md).
