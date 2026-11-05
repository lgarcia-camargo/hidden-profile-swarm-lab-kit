# Who maintains this kit

This repository is the **public reproduction surface** for the Hidden Profile Lab program: pinned tasks, live swarm JSONL exports, and a no-network verifier (`scripts/verify_results.py`).

## Identity (GitHub-native)

- **Repository:** [lgarcia-camargo/hidden-profile-swarm-lab-kit](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit)
- **Owner profile:** [@lgarcia-camargo](https://github.com/lgarcia-camargo)
- **Contact:** open a [GitHub Issue](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/issues/new/choose) (use **Falsification report** if your numbers disagree with the pin) or comment on [Discussions](https://github.com/lgarcia-camargo/hidden-profile-swarm-lab-kit/discussions).

We do not publish personal email addresses in this kit. All triage happens in public GitHub threads so claims stay falsifiable.

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
