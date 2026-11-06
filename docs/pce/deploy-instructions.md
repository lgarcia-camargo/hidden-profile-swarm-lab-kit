# PCE Card #1 — GitHub Pages deploy

## Published URL (after push to `main`)

```
https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/index.html
```

Repo: [hidden-profile-swarm-lab-kit](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit)  
Pages root: **`docs/`** on branch **`main`** (GitHub Pages “Deploy from branch /docs”).

## Files to commit

From repository root:

| Path | Role |
|------|------|
| `docs/pce/index.html` | Public contradiction card (HTML) |
| `docs/pce/usgs-pairwise-2026-11-06.json` | Machine record |
| `docs/pce/bls-pairwise-2026-11-06.json` | BLS pairwise snapshot |
| `docs/index.html` | Optional: link to PCE from lab home |

Source integrator markdown (operator tree, not required on Pages):

`~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/contradiction-card-01-2026-11-06.md`

Mirror copy for charter bench:

`~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html`

## Operator push (local Mac)

```bash
cd /path/to/hidden-profile-swarm-lab-kit
git add docs/pce docs/index.html scripts/verify_pages.sh
git commit -m "Publish PCE Card #1 under docs/pce"
git push origin main
```

After push, CI workflow `verify-pages.yml` runs `scripts/verify_pages.sh` (includes `/pce/index.html`).

Manual check:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/index.html'
```

Expect `200` once Pages build completes (often 1–3 minutes).

## Hosted swarm (no git push)

Proof on operator disk:

```bash
cd ~/fleet-swarm/bench-hour/analysis/hidden-profile-lab/public-kit/docs
python3 -m http.server 8765
# other terminal:
curl -sS -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:8765/pce/index.html'
```

Expect `200`.

## Path contradiction note

- **GitHub Pages** serves only what is under `docs/` in the remote repo.
- **Integrator card** markdown lives under `bench-hour/analysis/cool-shit-10h/pce/` on the fleet disk until copied into `docs/pce/` and pushed.
- Until push, the public URL returns **404**; local `8765` proof is the verified deploy slice on hosted.
