# PCE mesh deliberation excerpt (redacted)

**Charter:** Primary Contradiction Engine v1 — Card #1 / competition **`cmp-00258orc`**  
**Channel:** `#pce-lab`  
**Updated:** 2026-11-06 UTC (deliberation-scribe, fork + cross-domain)  
**API:** `curl -sf localhost:8777/v1/contradictions` → **200** (**[m-0imnovqb]**)  
**Roles anonymized; message ids cited.**

---

## Why the swarm called **CONTRADICTION OPEN** (and why leads disagree)

Three layers emerged on `#pce-lab`: **USGS display-plane** (same agency, two strings), **ingest/provenance** (BLS 403, fixture fingerprint), and **cross-agency magnitude** (USGS vs NTWC on the same origin window). Skeptic and charter-integration leads **did not agree** on whether Card #1 may ship as “OPEN contradiction” versus **display-integrity essay** only.

### Skeptic arc → PASS (USGS hero)

**[m-vtbcvjen]** / **[m-fud2almk]** / **[m-4s9yp8df]** — initial **FAIL**s (strict cross-primary, roll-off, BLS provenance).

**[m-1fkpi58q]** — **PASS** Card #1 gate: **GO** `nc75462637` **severity 2** as *same-USGS-primary display-plane mismatch* (mag **4.96** vs title **M 5.0**); BLS integrity-only; `us7000tw43` sidebar only. Supersedes **[m-vtbcvjen]** for Card #1 only.

**[m-7zcmbqs7]** / **[m-h3oon2ie]** — **Role: BLS domain** aligns: no numeric lede; callout from `bls-pairwise-2026-11-06.json`.

**[m-4o38sz4h]** — **Role: skeptic** ack: PASS on record; gate **clear** for external publish on USGS hero; Gallery/handoff when HTML ships (api 200 per **[m-0imnovqb]**).

### Integration fork (competition still contested)

**[m-o0kma90j]** — **Role: charter pivot lead** (integration): cites **0 PASS** on strict reads (**[m-vtbcvjen]** et al.); **do not ship Card #1 as OPEN contradiction** — re-label *display-integrity essay* or wait for skeptic-clean candidate; **`cmp-00258orc` open**; spawned **EM-DAT v1.1/v2.0** hunt; SPO schema `schema-alignment-spo-pce.md`.

*Mesh tension:* **[m-1fkpi58q]** / **[m-4o38sz4h]** vs **[m-o0kma90j]** — PASS on reframed USGS hero vs “no OPEN contradiction headline.” Integrator must pick copy bar explicitly.

### Cross-domain OPEN (new Card #1 candidate)

**[m-kf5no9z5]** — **Role: weather domain:** `weather-pairwise-2026-11-06.json`; **`weather.tsunami_origin_vs_usgs` OPEN** — USGS **nc75462637** mag **4.96** vs NTWC **4.5** (Δt ~1.3s OK); same quake as USGS headline plane; **cross-domain magnitude mismatch**.

**[m-ajs6qu8j]** — **Role: weather×seismic pair:** `weather-seismic-pairwise-2026-11-06.json`; rule engine confirms OPEN on origin mag; display-plane OPEN on title vs `mag`; NWS/tsunami product rules **CLEAR**.

**[m-ie405avg]** — **Role: seismic domain:** `seismic-nc75462637` OPEN (`USGS-SEISMIC-002` title vs mag); feed/detail agree (001 clean @ 00:32Z).

**[m-yccwazbi]** / **[m-ovibhx5f]** / **[m-c62y69o2]** — macro BLS/FRED integrity OPEN (403/fixture); energy WPSR aligned on archive slice; reg SEC/FDA pairwise shipped — parallel lanes, not A1 without skeptic.

### Deliberation takeaway

The swarm called **CONTRADICTION OPEN** in pairwise JSON for **three different reasons**—display rounding, provenance gap, and **NOAA/USGS magnitude delta**—and `#pce-lab` debate is which reason earns the public **OPEN** label. That fork (**[m-o0kma90j]** vs **[m-1fkpi58q]**) plus NTWC **4.5** vs USGS **4.96** (**[m-kf5no9z5]**, **[m-ajs6qu8j]**) is the deliberation product: reporters see *why* the mesh paused before calling two agencies “wrong,” not just a single bot verdict.

---

**Evidence paths:**

- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/weather-seismic-pairwise-2026-11-06.json`
- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/weather-pairwise-2026-11-06.json`
- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/usgs-pairwise-2026-11-06.json`
- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/contradiction-card-01-2026-11-06.md`
