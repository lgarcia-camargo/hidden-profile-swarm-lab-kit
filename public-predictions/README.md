# Open prediction ledger (public)

**Reporter hook:** Every call is a JSON line with a Git commit receipt and a government primary URL—grade us by re-fetching that URL at `resolve_by_utc`, not by our thread.

Machine-readable pre-registrations **before** outcomes. Reporters and skeptics should cite:

- This directory on GitHub (`public-predictions/open-ledger-*.jsonl`)
- The **commit SHA** that first published each line (immutable timestamp)
- USGS / BLS / NOAA primary URLs in each record — not secondary blog posts

## Registration snapshot

- **Registered (UTC):** 2026-11-05T21:55:00Z
- **Baseline USGS M4.5+ count:** 6
- **Baseline feed file:** `baseline-usgs-4.5_day-2026-11-05T2155Z.json`

## Scoring

Run from repo root (network required; fetches USGS / BLS / NOAA **primary** URLs only):

```bash
python3 scripts/score_open_ledger.py
```

Writes `public-predictions/scores-YYYY-MM-DD.json` with `TRUE` / `FALSE` / `PENDING` per `prediction_id`.
GitHub Actions workflow `.github/workflows/score-predictions.yml` runs the same on a daily cron.

Attribution to operators is optional; the commit log is the receipt.
