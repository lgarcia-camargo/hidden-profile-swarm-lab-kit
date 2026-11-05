# Hidden Profile Lab — task pack methodology

**Author:** hpl-task-pack (a-bqocr8mj) · **Parent:** hidden-profile-lab-runner (a-ibvos3i1) · **Channel:** `hidden-profile-lab`  
**Artifacts:** `tasks.json` (8 original HiddenBench-style tasks) · **Path:** `~/fleet-swarm/bench-hour/analysis/hidden-profile-lab/`

## Hidden Profile phenomenon

In social psychology, a **hidden profile** arises when group members each hold **partial, asymmetric information** and the **correct collective choice is not supported by any individual’s private evidence alone** (Stasser & Titus, 1985; Schulz-Hardt & Mojzisch, 2012). Groups often **over-discuss information that is already shared**, converge on a plausible but wrong option, and **fail to surface unique (unshared) facts**—a pattern called **shared information bias**. Li et al. formalize this for multi-agent LLMs as HiddenBench: shared cues frequently favor a **decoy option**, while decisive support for the optimum sits in **per-agent unshared clues** that must be pooled through communication (Li, Naito, & Shirado, 2025).

Our `tasks.json` follows that structure at the task level:

- **`question`** — scenario text visible to every role, including **misleading shared context** (decoy options that look attractive from public briefings).
- **`clues[]`** — each clue is visible to **exactly one** named role (`analyst-a`, …); no role receives another role’s clue in the hidden-profile condition.
- **`ground_truth`** — the unique correct answer string when **all** clues are integrated.
- **Hidden-profile check (design intent):** for each task, eliminating any one role’s clue leaves at least one decoy still plausible; only the **union** of clues identifies `ground_truth`.

This pack does **not** copy HiddenBench HF scenario text; scenarios are original to reduce pretraining leakage, matching HiddenBench Study 1 practice (Li et al., 2025, §4.1).

## Primary citations (≥3)

1. **HiddenBench / Hidden Profile formalization** — Yuxuan Li, Aoi Naito, Hirokazu Shirado, *HiddenBench: Assessing Collective Reasoning in Multi-Agent LLMs via Hidden Profile Tasks*, arXiv:2505.11556v2 (HTML: [https://arxiv.org/html/2505.11556v2](https://arxiv.org/html/2505.11556v2)). Defines shared vs unshared information, pre- vs post-discussion accuracy, and full-profile upper bound; reports multi-agent failure modes analogous to human groups.

2. **SILO-BENCH (communication–reasoning gap)** — ACL 2026 long paper, Anthology ID [2026.acl-long.1354](https://aclanthology.org/2026.acl-long.1354/) (*SILO-BENCH*). Benchmarks settings where agents must **coordinate partial observations**; success requires **communication that transfers private state**, not merely more reasoning steps in isolation. Our clue-per-role design is compatible with SILO-style **information siloing**, while task narratives remain decision-style (vendor/site/route) rather than digit-shard puzzles.

3. **MAD heterogeneity** — *Stop Overvaluing Multi-Agent Debate* (heterogeneous multi-agent debate as antidote to homogeneous debate failure), arXiv:2502.08788 ([https://arxiv.org/abs/2502.08788](https://arxiv.org/abs/2502.08788)). Shows **homogeneous** multi-agent debate can underperform strong single-agent baselines; **structured heterogeneity** (diverse roles, distinct evidence) improves integration. Maps directly to why **plurality over partial views** without private-fact pooling should fail hidden-profile tasks.

## Three evaluation regimes (swarmmy ↔ literature)

The hidden-profile-lab program compares **coordination topology** on identical tasks. Names below align with the cool-shit / channel lab (`mesh_integrator`, `competition_decide`, `cot_baseline`); literature anchors are in parentheses.

| Regime ID | Swarm protocol | Literature analogue | Expected behavior on hidden profile |
|-----------|----------------|---------------------|-----------------------------------|
| **`mesh_integrator`** (mesh) | Spawn one worker per role with **only that role’s clues**; discuss on `channel:hidden-profile-lab` (or mail an integrator); **one pooled decision** after private facts are shared. | Post-discussion hidden-profile condition with successful **information pooling** (HiddenBench §3); SILO-BENCH **communication closes the gap** when agents transmit siloed clues. | **Upper bound among multi-agent arms** if mesh actually surfaces all unshared clues (target: approach full-profile accuracy). |
| **`competition_decide`** (compete) | `competition_open` → agents **propose** from local views → `competition_decide` **plurality** without mandatory merge of private clue text. | **Homogeneous MAD**-like failure mode (arxiv:2502.08788): debate/plurality over **incomplete local posteriors**; resembles groups that **talk but do not integrate** unique evidence. | Often **below mesh**; may track **hidden-profile pre-discussion** accuracy or decoy shared in `question`. |
| **`cot_baseline`** (cot) | **Single agent** sees **`question` only** (shared misleading context), or optionally full clue union for **full-profile upper bound** in ablations. | HiddenBench **full-profile** vs **shared-only** baselines (Li et al., §3): full information upper bound; shared-only simulates **no private clue access**. | Shared-only: **poor** (decoy wins). Full-clue concat: **ceiling** for task difficulty check. |

### Diagnostic metrics (recommended)

- **Accuracy:** final answer equals `ground_truth` (case-insensitive string match).
- **Hidden-profile lift:** `acc_mesh − acc_compete` (integration gain over plurality).
- **CoT gap:** `acc_full_cot − acc_shared_cot` (value of private clues when pooled offline).
- **Communication cost:** mesh message count / tokens (regime A only), comparable to HiddenBench post-discussion rounds.

## Task inventory

| `id` | Roles | Clues | `ground_truth` |
|------|-------|-------|----------------|
| hpl-01-wildfire-evac | 3 | 3 | North Ridge Campground |
| hpl-02-clinical-trial-site | 4 | 4 | Site Gamma |
| hpl-03-satellite-downlink | 3 | 3 | Station Juliet |
| hpl-04-supply-chain-resin | 3 | 3 | Vendor Obsidian |
| hpl-05-university-supercomputer | 4 | 4 | Cluster Cirrus |
| hpl-06-restaurant-lease | 3 | 3 | Location Alley Lantern |
| hpl-07-cyber-insurance-carrier | 3 | 3 | Carrier Juniper |
| hpl-08-museum-loan-route | 4 | 4 | Route Rail |

**Total:** 8 tasks, 27 role-private clues (3–4 per task).

## How to run (downstream)

1. Load `tasks.json` and, for each task, inject per-role prompt: `question` + that role’s clue(s) only.
2. Run the three regimes on the same task order; log proposals, final answers, and message traces.
3. Compare accuracy and cost against HiddenBench-style references: shared-only baseline vs integrated mesh vs plurality competition.

## Limitations

- Tasks are **author-crafted**, not passed through HiddenBench automated difficulty filters (pre-discussion accuracy bands in Li et al., §3).
- **No shared fact array** in JSON (shared bias is prose in `question`); runners that need explicit `shared[]` tags can split question text or add a schema v2 field later.
- Hosted deploy runs measure **swarm coordination**, not a reproduction of HiddenBench’s 65-task LLM leaderboard.

## References (short)

- Li, Y., Naito, A., & Shirado, H. (2025). HiddenBench. arXiv:2505.11556v2.
- SILO-BENCH. ACL 2026 long. https://aclanthology.org/2026.acl-long.1354/
- Stop Overvaluing Multi-Agent Debate (heterogeneity). arXiv:2502.08788.
- Stasser, G., & Titus, W. (1985). Pooling of unshared information in group decision making. *Journal of Personality and Social Psychology*.
- Schulz-Hardt, S., & Mojzisch, A. (2012). Hidden profile research. In *Group discussion* research.
