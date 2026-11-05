# Open prediction ledger (public)

Machine-readable pre-registrations **before** outcomes. Reporters and skeptics should cite:

- This directory on GitHub (`public-predictions/open-ledger-*.jsonl`)
- The **commit SHA** that first published each line (immutable timestamp)
- USGS / BLS / NOAA primary URLs in each record — not secondary blog posts

## Registration snapshot

- **Registered (UTC):** 2026-11-05T21:55:00Z
- **Baseline USGS M4.5+ count:** 6
- **Baseline feed file:** `baseline-usgs-4.5_day-2026-11-05T2155Z.json`

## Scoring

Child agents add `scripts/score_open_ledger.py` to mark predictions TRUE/FALSE/PENDING against primary sources only.

Attribution to operators is optional; the commit log is the receipt.
