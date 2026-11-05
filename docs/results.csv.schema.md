# results.csv schema (hidden-profile-lab)

**Path:** `~/fleet-swarm/bench-hour/analysis/hidden-profile-lab/results.csv`  
**Writer:** `build_gallery.py` (simulator rows from cool-shit aggregate JSON) + manual/runner append for live JSONL merges.

## Columns

| Column | Type | Values | Notes |
|--------|------|--------|-------|
| `track` | string | `simulator` \| `live` | Simulator = pinned-partition harness; live = swarm JSONL regimes |
| `task_id` | string | `hpl-01-…` … `hpl-15-…` | Must exist in pinned `tasks.json` (15-pack as of 2026-11-05) |
| `regime` | string | `mesh` \| `compete` \| `cot` \| `cot_partition` | Maps from regime A/B/C/C_partition logs |
| `correct` | bool | `True` / `False` | Final answer vs `ground_truth` (case-insensitive) |
| `tokens` | int | ≥0 | Harness estimate |
| `wall_ms` | int | ≥0 | Wall time ms |
| `mesh_posts_count` | int | ≥0 | Coordination posts; 0 for solo CoT |

## 15-pack expansion (hpl-09..15)

- **Pinned pack:** `tasks.json` task_count=15; extension source `tasks/hpl-09-15-extension.json`.
- **Live rows:** append only — do not remove hpl-01..08 historical rows.
- **Regime C** full-profile runs use schema `hidden-profile-lab/regime_c_run/v1` in `runs/regime_c.jsonl`.
- **Regime C_partition** optional per-task single-clue baseline (`regime_c_partition_run/v1`).
- **Runner manifest:** `lab-runner-manifest.json` (owner **a-ibvos3i1** for live mesh/compete on 09..15).

## Related

- `lab-runner-manifest.json` — canonical paths for runners  
- `task-pack-15-draft.md` — inventory + rubric  
- `CANONICAL.md` — harness vs live JSONL split  
