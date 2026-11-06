# Contradiction Card — serving notes

## Local paths (authoritative v1 build)

| Asset | Path |
|-------|------|
| Card UI | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html` |
| Incident JSON | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/incidents/PCE-2026-11-06-01.json` |
| USGS pairwise | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/data/usgs-pairwise-2026-11-06.json` |
| BLS pairwise | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/data/bls-pairwise-2026-11-06.json` |

## Local verify (static file)

```bash
curl -I "file:///Users/leon.garciacamargo/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html"
curl -I "file:///Users/leon.garciacamargo/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/incidents/pce-inc-2026-11-06-usgs-nc75462637.json"
```

Serve over HTTP for full fetch() behavior (browser file:// may block JSON):

```bash
cd ~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public && python3 -m http.server 8765
curl -I "http://127.0.0.1:8765/index.html"
curl -I "http://127.0.0.1:8765/incidents/pce-inc-2026-11-06-usgs-nc75462637.json"
```

## Target public URL (GitHub Pages mirror)

After `pce-deploy` copies this tree into `hidden-profile-swarm-lab-kit` docs root:

- **Card:** https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/index.html
- **Incident JSON:** https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/incidents/pce-inc-2026-11-06-usgs-nc75462637.json

Suggested deploy destination in repo: `analysis/hidden-profile-lab/public-kit/docs/pce/` (same relative layout as this `public/` folder).

## Chosen incident

`PCE-2026-11-06-01` / `nc75462637` — A1 from `contradiction-card-01-2026-11-06.md`. **Publish gated:** skeptic FAIL (`pce-usgs-nc75462637`, m-vtbcvjen) until PASS.

Handoff copy: `analysis/hidden-profile-lab/public-kit/docs/pce/`
