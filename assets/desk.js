/** Barbie Pit desk — polls /desk/today and renders Section 2 windows. */
window.BarbieDesk = (() => {
  const API = window.DESK_API_BASE || "http://127.0.0.1:8081";

  function el(id) {
    return document.getElementById(id);
  }

  function renderTraders(traders) {
    const root = el("leaderboard");
    if (!root) return;
    root.innerHTML = traders.map((t, i) => `
      <div class="holo rounded-2xl p-4 border border-pink-400/30 ${i === 0 ? 'ring-2 ring-pink-400/50' : ''}">
        <div class="text-xs text-pink-300/80">${i === 0 ? 'LEADING' : '#' + (i + 1)} · ${t.title}</div>
        <div class="text-lg font-bold text-white">${t.name}</div>
        <div class="text-3xl font-black text-[#D4AF37] tabular-nums">${t.book.toLocaleString()}</div>
        <div class="text-xs text-cyan-400/80 mt-1">cash ${t.cash.toLocaleString()}</div>
        <p class="text-xs text-white/60 mt-2 leading-snug">${t.bio || ''}</p>
      </div>`).join("");
  }

  function renderBook(book, frames, alerts, fills) {
    const lf = book.latest_frame;
    el("book-equity").textContent = book.equity?.toLocaleString() ?? "—";
    el("book-leading").textContent = book.leading ?? "—";
    if (lf) {
      el("book-meta").textContent =
        `Frame ${lf.frame} · ${lf.rhythm} · gas ${lf.gas} gwei · ${lf.status}`;
      el("book-25sha").textContent = lf["25sha"] || "—";
      el("bpm").textContent = lf.bpm ?? el("bpm").textContent;
    }
    el("book-alerts").innerHTML = (alerts.length ? alerts : ["Sell-only still in force. Do not reload."])
      .slice(0, 6).map(a => `<li class="text-pink-200/90 text-sm">${a}</li>`).join("");
    el("book-fills").innerHTML = (fills.length ? fills : [])
      .slice(0, 8).map(f => `<li class="text-cyan-200/90 text-sm font-mono">COMMIT frame ${f.frame} · 25SHA ${(f["25sha"]||'').slice(0,12)}…</li>`).join("")
      || '<li class="text-white/40 text-sm">No commits yet — tick running…</li>';
  }

  function renderFloor(floor) {
    el("floor-feed").innerHTML = floor.map(row => `
      <div class="flex gap-3 items-start border-b border-white/5 pb-2">
        <span class="text-xs font-mono w-24 shrink-0 ${row.state === 'veto' ? 'text-red-400' : 'text-emerald-400'}">${row.agent}</span>
        <span class="text-xs uppercase w-12 ${row.state === 'veto' ? 'text-red-300' : 'text-emerald-300'}">${row.state}</span>
        <span class="text-sm text-white/80 flex-1">${row.msg}</span>
      </div>`).join("");
  }

  async function refresh() {
    try {
      const r = await fetch(API + "/desk/today");
      if (!r.ok) return;
      const d = await r.json();
      renderTraders(d.traders || []);
      renderBook(d.book || {}, d.frames || [], d.alerts || [], d.fills || []);
      renderFloor(d.floor || []);
      el("desk-status").textContent = "LIVE · 25SHA";
      el("desk-status").className = "text-emerald-400 font-mono text-sm";
    } catch {
      el("desk-status").textContent = "OFFLINE · demo";
      el("desk-status").className = "text-amber-400 font-mono text-sm";
    }
  }

  return { refresh, API };
})();
