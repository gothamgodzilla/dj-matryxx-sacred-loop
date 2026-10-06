/** Barbie Pit desk — polls /desk/today and renders Section 2 windows. */
window.BarbieDesk = (() => {
  const API = window.DESK_API_BASE || "http://127.0.0.1:8081";
  const feedRing = [];
  const FEED_MAX = 120;

  function el(id) {
    return document.getElementById(id);
  }

  function pushFeed(line) {
    feedRing.push(line);
    while (feedRing.length > FEED_MAX) feedRing.shift();
  }

  function formatFeedLine(ev) {
    const ts = new Date().toISOString().slice(11, 19);
    if (ev.kind === "repair") {
      return `[${ts}] REPAIR gen·${ev.depth || "?"} ${ev.phase} frame=${ev.frame} ${ev.msg || ""}`;
    }
    if (ev.kind === "telemetry") {
      return `[${ts}] TELEM ${ev.agent || "?"} frame=${ev.frame} ${ev.msg || ev.val || ""}`;
    }
    return `[${ts}] ${JSON.stringify(ev)}`;
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

  /** Live virtual screen: telemetry + recursive repair/regenerate learning feed. */
  function renderVirtualScreen(telemetryFeed, repairGeneration) {
    const screen = el("virtual-screen");
    const meta = el("virtual-screen-meta");
    if (!screen) return;

    if (telemetryFeed && telemetryFeed.length) {
      feedRing.length = 0;
      telemetryFeed.forEach((ev) => pushFeed(formatFeedLine(ev)));
    }

    if (meta) {
      meta.textContent =
        `repair_generation=${repairGeneration ?? 0} · feed_lines=${feedRing.length} · learn=recursive_self_repair→regenerate`;
    }

    screen.innerHTML = feedRing
      .map((line) => {
        const repair = line.includes("REPAIR");
        const telem = line.includes("TELEM");
        const cls = repair ? "text-amber-300" : telem ? "text-emerald-300/90" : "text-cyan-200/80";
        return `<div class="font-mono text-[11px] leading-relaxed ${cls}">${line}</div>`;
      })
      .join("");
    screen.scrollTop = screen.scrollHeight;
  }

  function ingestTickResult(tickJson) {
    if (!tickJson) return;
    (tickJson.repair || []).forEach((ev) => pushFeed(formatFeedLine({ ...ev, kind: "repair" })));
    if (tickJson.telemetry) {
      Object.entries(tickJson.telemetry).forEach(([agent, msg]) => {
        pushFeed(formatFeedLine({
          kind: "telemetry",
          frame: tickJson.frame,
          agent,
          msg,
          status: tickJson.status,
        }));
      });
    }
    const meta = el("virtual-screen-meta");
    if (meta) {
      meta.textContent =
        `repair_generation=${tickJson.repair_generation ?? 0} · feed_lines=${feedRing.length} · learn=recursive_self_repair→regenerate`;
    }
    const screen = el("virtual-screen");
    if (screen) {
      screen.innerHTML = feedRing
        .map((line) => {
          const repair = line.includes("REPAIR");
          const telem = line.includes("TELEM");
          const cls = repair ? "text-amber-300" : telem ? "text-emerald-300/90" : "text-cyan-200/80";
          return `<div class="font-mono text-[11px] leading-relaxed ${cls}">${line}</div>`;
        })
        .join("");
      screen.scrollTop = screen.scrollHeight;
    }
  }

  async function refresh() {
    try {
      const r = await fetch(API + "/desk/today");
      if (!r.ok) return;
      const d = await r.json();
      renderTraders(d.traders || []);
      renderBook(d.book || {}, d.frames || [], d.alerts || [], d.fills || []);
      renderFloor(d.floor || []);
      renderVirtualScreen(d.telemetry_feed || [], d.repair_generation);
      el("desk-status").textContent = `LIVE · 25SHA · regen ${d.repair_generation ?? 0}`;
      el("desk-status").className = "text-emerald-400 font-mono text-sm";
    } catch {
      el("desk-status").textContent = "OFFLINE · demo";
      el("desk-status").className = "text-amber-400 font-mono text-sm";
    }
  }

  return { refresh, ingestTickResult, API };
})();
