# Contradiction Card #1 — serving (post weather hero ship)

## Card

- **ID:** `PCE-2026-11-06-01` / `pce-inc-2026-11-06-weather-t2ssp5`
- **Hero:** `weather.tsunami_origin_vs_usgs` — NTWC 4.5 vs USGS 4.96 (t2ssp5 / nc75462637)
- **Skeptic:** PASS `pce-weather-t2ssp5-mag` (m-20c4fllb)
- **Footnotes:** USGS display-plane (title vs mag), BLS integrity (`bls-pairwise`)

## Local paths

| Asset | Path |
|-------|------|
| UI | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html` |
| Incident | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/incidents/PCE-2026-11-06-01.json` |
| Pages mirror | `~/fleet-swarm/bench-hour/analysis/hidden-profile-lab/public-kit/docs/pce/` |

## Verify

```bash
curl -I "file:///Users/leon.garciacamargo/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html"
curl -I "file:///Users/leon.garciacamargo/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/incidents/PCE-2026-11-06-01.json"
# Mac API (when pce-public running):
curl -sf "http://127.0.0.1:8777/v1/contradictions"
curl -sf "http://127.0.0.1:8777/v1/contradictions/PCE-2026-11-06-01"
```

**Pages (after push):** https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/index.html
