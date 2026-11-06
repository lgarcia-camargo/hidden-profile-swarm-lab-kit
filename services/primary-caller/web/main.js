const API =
  import.meta.env?.VITE_API_BASE ||
  (location.hostname === "127.0.0.1" || location.hostname === "localhost"
    ? "http://127.0.0.1:8787"
    : "");

function statusClass(s) {
  if (s === "PASS") return "pass";
  if (s === "FAIL") return "fail";
  return "pending";
}

async function fetchJson(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
}

function renderBoard(data) {
  document.getElementById("meta").innerHTML = `
    <span>Paper bankroll: <strong>$${data.paper_bankroll_usd.toLocaleString()}</strong></span>
    <span>Updated: ${data.generated_at_utc}</span>
  `;
  const el = document.getElementById("board");
  el.innerHTML = data.calls
    .map(
      (c) => `
    <article class="card ${statusClass(c.status)}">
      <div class="row">
        <span class="badge">${c.status}</span>
        <span class="cat">${c.category || ""}</span>
      </div>
      <h3>${c.prediction_id}</h3>
      <p>${c.claim}</p>
      <p class="detail">${c.detail}</p>
      <p class="stakes">Stake $${c.paper_stake_usd ?? "—"} · P&amp;L ${
        c.paper_pnl_usd != null ? c.paper_pnl_usd : "open"
      }</p>
      <p class="resolve">Resolve by ${c.resolve_by_utc}</p>
    </article>`
    )
    .join("");

  const beats = document.getElementById("beats");
  beats.innerHTML = (data.recent_beats || [])
    .map(
      (b) =>
        `<li><code>${b.event_type || "event"}</code> ${b.recorded_at_utc} — ${JSON.stringify(b.payload).slice(0, 120)}…</li>`
    )
    .join("");
}

async function refresh() {
  const [board, track] = await Promise.all([
    fetchJson("/v1/board"),
    fetchJson("/v1/track-record"),
  ]);
  renderBoard(board);
  document.getElementById("track").textContent = JSON.stringify(track, null, 2);
}

refresh().catch((e) => {
  document.getElementById("board").innerHTML = `<p class="error">API error: ${e.message}. Start API on 127.0.0.1:8787</p>`;
});

setInterval(() => refresh().catch(() => {}), 60_000);
