# Primary Caller v0

Product layer for the public prediction ledger: **FastAPI + SQLite** source of truth, **API-driven** live board, and a **supervised worker** for scoring + BLS wire-beater + optional Nostr.

Architecture: [primary-caller-product-architecture.md](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/blob/main/../../../../../cool-shit-10h/press/primary-caller-product-architecture.md) (bench-hour analysis).

## Quick start (Mac / local)

```bash
cd services/primary-caller
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# API on 127.0.0.1:8787
python3 main.py
```

In another terminal:

```bash
curl -s http://127.0.0.1:8787/v1/board | python3 -m json.tool
curl -s http://127.0.0.1:8787/v1/track-record | python3 -m json.tool
```

### Frontend (Vite)

```bash
cd web
npm install
npm run build
# Served at http://127.0.0.1:8787/app/ after build
```

Dev with proxy: `npm run dev` → http://localhost:5173

### Worker (15m score + BLS poll)

```bash
source .venv/bin/activate
export PYTHONPATH="$(pwd)"
python3 worker.py --once          # one tick
python3 worker.py                 # loop (900s default)
export NOSTR_NSEC='nsec1...'      # optional: post on wire beat
python3 worker.py --post-nostr
```

### Supervisor (launchd)

1. Copy `deploy/com.primary-caller.worker.plist` to `~/Library/LaunchAgents/`
2. Replace `WORKER_PATH`, `KIT_ROOT`, `SERVICE_ROOT` with absolute paths
3. `launchctl load ~/Library/LaunchAgents/com.primary-caller.worker.plist`

**nohup fallback:**

```bash
cd services/primary-caller
nohup python3 worker.py >> var/worker.log 2>&1 &
nohup python3 main.py >> var/api.log 2>&1 &
```

## Environment

| Variable | Default |
|----------|---------|
| `PRIMARY_CALLER_HOST` | `127.0.0.1` |
| `PRIMARY_CALLER_PORT` | `8787` |
| `PRIMARY_CALLER_DB` | `var/primary-caller.db` |
| `PRIMARY_CALLER_LEDGER` | `../../public-predictions/open-ledger-2026-11-05.jsonl` |
| `PAPER_BANKROLL_USD` | `10000` |
| `STAKE_FRACTION` | `0.02` |
| `NOSTR_NSEC` | (unset — wire beat publish skipped) |

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/v1/board` | Calls + PASS/PENDING/FAIL + paper stakes + recent beats |
| GET | `/v1/track-record` | Wins/losses, P&amp;L, bankroll |
| POST | `/v1/calls` | Internal register (creates paper stake) |
| POST | `/v1/admin/ingest` | Re-read open-ledger jsonl |
| POST | `/v1/admin/score` | Run scorer now |

Board status maps ledger scorer `TRUE`/`FALSE`/`PENDING` → **PASS** / **FAIL** / **PENDING**.

## Deploy (public URL)

Minimum bar (this v0): API on **127.0.0.1:8787** + static app at `/app/` + this README.

Optional:

- **Cloudflare Tunnel**: `cloudflared tunnel --url http://127.0.0.1:8787`
- **GitHub Pages**: embed iframe or link to tunneled API; set `VITE_API_BASE` at build time
- **Fly.io / Railway**: run `main.py` + worker as separate processes; mount persistent volume for SQLite

Legacy static site remains at [predictions-live.html](https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/predictions-live.html); this service replaces hand-edited live JSON for the product path.

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -q
```
