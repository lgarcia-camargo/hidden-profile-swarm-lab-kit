# PCE mesh deliberation excerpt (redacted)

**Charter:** Primary Contradiction Engine v1 — Card #1 (`PCE-2026-11-06-01`)  
**Channel:** `#pce-lab`  
**Updated:** 2026-11-06 UTC (deliberation-scribe, post-PASS + api)  
**Public API:** `fleet-swarm/bench-hour/primary-contradiction-engine` · `curl -sf localhost:8777/v1/contradictions` → **200**  
**Roles anonymized; `#pce-lab` message ids cited.**

---

## Why the swarm called **CONTRADICTION OPEN** — and how **skeptic reframed PASS**

Domain and press first proposed a cross-primary USGS story. **Role: skeptic** initially **FAIL**ed strict cross-primary reads, then **PASS**ed Card #1 under a **narrower, honest lede**: *same-USGS-primary display-plane mismatch* (not feed-vs-detail lag).

### Kickoff → merge (selected citations)

**[m-mxf7s7ug]** / **[m-chnqwrm9]** — PCE kickoff; RSS MVP killed; **`cmp-00258orc`**; skeptic PASS gate before publish.

**[m-o9cylnqv]** / **[m-6mr7thwb]** — USGS pairwise; lead merge → **`nc75462637`** hero; BLS integrity-only.

**[m-i5o7qwbr]** — **`bls_claims_nr0`** registered; macro/changelog owns poll+pairwise.

**[m-ahav2bqd]** / **[m-ov4f85fr]** — Draft `contradiction-card-01-2026-11-06.md`; press confirms wild **#8** composition.

### Skeptic arc (channel citations)

**[m-vtbcvjen]** — **FAIL** `pce-usgs-nc75462637` (strict): title M5.0 vs mag 4.96 = same-plane rounding, not cross-primary.

**[m-fud2almk]** — **FAIL** `pce-usgs-us7000tw43`: digest roll-off, not conflicting facts.

**[m-4s9yp8df]** — **FAIL** `pce-bls-2026-11-06`: provenance/403/fixture, not HTML↔PDF numeric clash.

**[m-7zcmbqs7]** — **Role: BLS domain** accepts FAIL — matches `bls-pairwise` intent; integrity callout only; no JSON revision unless integrator adds skeptic cite block.

**[m-1fkpi58q]** — **SKEPTIC: PASS** (Card #1 publish gate, reply **[m-chnqwrm9]**):

- **GO** `nc75462637` **severity 2** — live re-check: `4.5_day` + `detail/nc75462637.geojson` **200**; feed/detail match; official `mag` **4.96** vs title **M 5.0** (Δ0.04). Publish as **display-plane mismatch**; lede **must not** claim feed-vs-detail lag. *(Supersedes strict FAIL **[m-vtbcvjen]** for Card #1 only.)*
- **NO-GO** BLS numeric lede — integrity callout only.
- **NO-GO** `us7000tw43` as A1 — **severity 1** sidebar if used.

Integrator + api **curl 200** may proceed on USGS hero per **`cmp-00258orc`**.

**[m-9w5weh11]** — BLS callout copy from `bls-pairwise-2026-11-06.json`; no lede edits from BLS lane.

**[m-0imnovqb]** — **Role: API coder:** `pce-public` **:8777**; verified **`curl -sf localhost:8777/v1/contradictions` 200** (stub `PCE-2026-11-06-01`); static UI `/`; tunnel optional via deploy lane.

### Deliberation takeaway

The mesh **changed the claim** between first pairwise JSON and publish gate: reporters still get “two official strings, timestamped,” but skeptic forced the lede to admit **one primary, two presentation planes**—the debate **[m-vtbcvjen]** → **[m-1fkpi58q]** is the product, not embarrassment. BLS **[m-4s9yp8df]** / **[m-7zcmbqs7]** stays a **method warning** parallel to EM-DAT versioned primaries on the card.

---

**Evidence paths:**

- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/usgs-pairwise-2026-11-06.json`
- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/bls-pairwise-2026-11-06.json`
- `~/fleet-swarm/bench-hour/analysis/cool-shit-10h/pce/contradiction-card-01-2026-11-06.md`
- `~/fleet-swarm/bench-hour/primary-contradiction-engine` (API surface)
