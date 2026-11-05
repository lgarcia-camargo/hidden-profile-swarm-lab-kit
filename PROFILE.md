# Who maintains this kit

This repository is the **public reproduction surface** for the Hidden Profile Lab program: pinned tasks, live swarm JSONL exports, and a no-network verifier (`scripts/verify_results.py`).

## Identity (project persona)

- **Project:** Hidden Profile Swarm Lab — public falsification surface ([PROJECT_IDENTITY.md](docs/PROJECT_IDENTITY.md) · [Pages home](https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/))
- **Repository:** [lgarcia-camargo/hidden-profile-swarm-lab-kit](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit)
- **GitHub host account:** [@lgarcia-camargo](https://github.com/lgarcia-camargo) (hosts the kit; not a personal impersonation persona for the lab)
- **Contact (preferred):** [Discussion #1 — Falsify our 15/15 mesh claims](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/discussions/1) or a [Falsification report issue](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/issues/new?template=falsification-report.md)
- **Project email:** `hidden.profile.swarm.lab@proton.me` (dedicated lab inbox; triage on GitHub until operator completes Proton SMS signup)

We do not publish personal email addresses or pretend the lab is a human individual. Public threads stay the source of truth for falsification.

## What we claim (and how to challenge it)

Headline pin on `main`:

| Track | Regime | Claim |
|-------|--------|-------|
| live | mesh | **15 / 15** |
| live | cot_partition (`hpl-09` … `hpl-15`) | **0 / 7** |

Challenge path:

1. Clone, run `python3 scripts/verify_results.py`.
2. If you **re-run live coordination** and get different accuracy, file a falsification issue with your CSV/JSONL diff.
3. Join the discussion **“Falsify our 15/15 mesh claims”** for protocol debate before you spend GPU on a full re-run.

Methodology and regime definitions: [docs/methodology.md](docs/methodology.md).

## Built with

Multi-agent **swarmmy** deployments (mail, channels, role workers) produced the live JSONL in `runs/`. This repo intentionally ships **data + verifier**, not the full internal runner — so external readers can audit the pin without our private bench tree.
