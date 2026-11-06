# GitHub Pages path — PCE vs integrator disk

| Surface | Path |
|---------|------|
| **Live URL (after push)** | `https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/pce/index.html` |
| **Repo Pages file** | `docs/pce/index.html` |
| **Integrator markdown (source of truth text)** | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/contradiction-card-01-2026-11-06.md` |
| **Charter public mirror** | `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/public/index.html` |

Contradiction: markdown and JSON artifacts are produced on the bench-hour tree first; GitHub Pages only updates when `docs/pce/*` is committed to `hidden-profile-swarm-lab-kit` `main`. See `deploy-instructions.md`.
