# Barbie Pit × Sacred Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full-stack Barbie Pit live desk in sacred-loop skin: 4-trader sim driven by WebAudio BPM, 6-agent floor + 7-judge gate, 25SHA commits, Guinness SHA-256 plate, MATRYXX LLC branding.

**Architecture:** FastAPI sim backend (SQLite fictional ledger, single worker) + evolved single-page frontend (`index.html` + `assets/audio.js`, 5s poll). Cyclical floor loop; BPM sets personality weights and gas; Risk veto reverts.

**Tech Stack:** Python 3.12, FastAPI, uvicorn (workers 1), SQLite3 stdlib, pytest; vanilla JS + Tailwind CDN, WebAudio API; stdlib-only `smoke_desk.py`.

**Spec:** `dj-matryxx-sacred-loop/docs/superpowers/specs/2026-10-05-barbie-pit-sacred-loop-design.md`

## Global Constraints

- Operator MATRYXX LLC, Sheridan Wyoming; product Wingman.OS; components GANESH, LOGiX, MATRYXX (validation engine), Prince; company distinct from engine.
- No "Coexist LLC" / "Coexist Intelligence" strings anywhere.
- Fictional vessel ledger — not a brokerage, not a chain, not advice — persistent footer on UI and every export.
- 25SHA = `sha256(canonical_json).hexdigest()[:25].upper()`; Guinness = full SHA-256 of winner book.
- Gas = `12 + max(0, int((bpm - 100) * 0.8))` gwei; BPM loss holds last valid with `SACRED_PAUSE (BPM_HOLD)` label.
- DD at/over limit enforces sell-only halt; tick modes `1sec=1hr` / `1min=1hr`; SQLite single worker only.

## Review Focus

- BPM dropout mid-tick holds last BPM and labels sacred-pause instead of freezing or zeroing aggression.
- `?day=`-style bad frame/BPM input returns 422, never 500.
- FAILED/quota task marks run `failed` with reason instead of sticking in `submitted`.
- Guinness verify recomputes SHA-256 and matches stored plate hash exactly.
- Poll cache header `max-age=5` present on `/desk/today` for CDN correctness.

---

### Task 1: Sim core — personalities + BPM aggression

**Files:**
- Create: `dj-matryxx-sacred-loop/backend/app/sim.py`
- Test: `dj-matryxx-sacred-loop/backend/tests/test_sim.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `aggression_from_bpm(bpm: float | None, last: int) -> tuple[int, str, dict]` returning `(bpm_used, rhythm_label, weights)` where weights maps `0xVESP/0xKAEL/0xROOK/0xSABL` to floats summing to 1.0.

- [ ] **Step 1: Write the failing test**

```python
def test_aggression_bias_and_pause():
    from app.sim import aggression_from_bpm
    _, _, w_hi = aggression_from_bpm(165.0, 120)
    _, _, w_lo = aggression_from_bpm(100.0, 120)
    assert w_hi["0xROOK"] > w_hi["0xVESP"]
    assert w_lo["0xVESP"] >= w_hi["0xVESP"]
    bpm, label, _ = aggression_from_bpm(0.0, 128)
    assert (bpm, label) == (128, "SACRED_PAUSE (BPM_HOLD)")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_sim.py::test_aggression_bias_and_pause -v`
Expected: FAIL with "No module named app.sim" (or import error).

- [ ] **Step 3: Write minimal implementation**

```python
"""Personality weights from BPM. Rook likes speed, Vesper likes calm."""
BASE = {"0xVESP": 0.30, "0xKAEL": 0.25, "0xROOK": 0.25, "0xSABL": 0.20}

def aggression_from_bpm(bpm, last):
    if bpm is None or bpm <= 0:
        return int(last), "SACRED_PAUSE (BPM_HOLD)", dict(BASE)
    b = int(bpm)
    rook_boost = max(-0.12, min(0.20, (b - 130) * 0.008))
    w = dict(BASE)
    w["0xROOK"] = round(w["0xROOK"] + rook_boost, 4)
    w["0xVESP"] = round(w["0xVESP"] - rook_boost / 2, 4)
    w["0xKAEL"] = round(1.0 - w["0xROOK"] - w["0xVESP"] - w["0xSABL"], 4)
    label = "LIVE_RHYTHM"
    return b, label, w
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_sim.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/backend/app/sim.py dj-matryxx-sacred-loop/backend/tests/test_sim.py
git commit -m "feat: bpm-driven personality weights with sacred-pause hold"
```

### Task 2: 25SHA cache + Guinness plate

**Files:**
- Create: `dj-matryxx-sacred-loop/backend/app/cache25.py`
- Create: `dj-matryxx-sacred-loop/backend/app/plate.py`
- Test: `dj-matryxx-sacred-loop/backend/tests/test_proof.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `state_root(payload: dict) -> str` (25SHA), `guinness_sha(payload: dict) -> str` (full SHA-256), `verify_plate(payload: dict, plate: str) -> bool`.

- [ ] **Step 1: Write the failing test**

```python
def test_roots_deterministic_and_verify():
    from app.cache25 import state_root
    from app.plate import guinness_sha, verify_plate
    p = {"frame": 5001, "bpm": 138}
    assert state_root(p) == state_root(p) and len(state_root(p)) == 25
    plate = guinness_sha(p)
    assert verify_plate(p, plate) is True
    assert verify_plate({"frame": 5002, "bpm": 138}, plate) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_proof.py -v`
Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

```python
# cache25.py
import hashlib, json
def state_root(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:25].upper()
```

```python
# plate.py
import hashlib, json
def guinness_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()
def verify_plate(payload, plate):
    return guinness_sha(payload) == plate
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_proof.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/backend/app/cache25.py dj-matryxx-sacred-loop/backend/app/plate.py dj-matryxx-sacred-loop/backend/tests/test_proof.py
git commit -m "feat: 25SHA state roots and Guinness plate verify"
```

### Task 3: Floor cycle + judges + store

**Files:**
- Create: `dj-matryxx-sacred-loop/backend/app/floor.py`
- Create: `dj-matryxx-sacred-loop/backend/app/judges.py`
- Create: `dj-matryxx-sacred-loop/backend/app/store.py`
- Test: `dj-matryxx-sacred-loop/backend/tests/test_desk.py`

**Interfaces:**
- Consumes: `aggression_from_bpm` (Task 1), `state_root/guinness_sha` (Task 2).
- Produces: `run_frame(store, frame: int, bpm_raw: float | None, cfg: dict) -> dict` with keys `frame,status,25sha,guinness_sha256,gas,rhythm,reason?`; statuses `0xCOMMITTED | 0xREVERT_RISK_EXCEEDED | 0xHALT_SELL_ONLY`. Store seeds 4 traders and exposes `traders()`.

- [ ] **Step 1: Write the failing test**

```python
def test_frame_commits_and_halts(tmp_path):
    from app.store import Store
    from app.floor import run_frame
    s = Store(str(tmp_path / "d.db"))
    ok = run_frame(s, 5001, 138.0, {"max_dd": 0.12, "seed": 1})
    assert ok["status"] in ("0xCOMMITTED", "0xREVERT_RISK_EXCEEDED")
    assert len(ok["25sha"]) == 25
    bad = run_frame(s, 5002, 0.0, {"max_dd": 0.12, "seed": 1})
    assert bad["rhythm"].startswith("SACRED_PAUSE")
    halt = run_frame(s, 5003, 138.0, {"max_dd": 0.0, "seed": 1})
    assert halt["status"] == "0xHALT_SELL_ONLY"
    assert [t["id"] for t in s.traders()] == ["0xVESP", "0xKAEL", "0xROOK", "0xSABL"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_desk.py -v`
Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

```python
# floor.py
import random
from .sim import aggression_from_bpm
from .cache25 import state_root
from .plate import guinness_sha

AGENTS = ["0xRESEARCH", "0xANALYST", "0xQUOTER", "0xEXECUTOR", "0xRISK", "0xOBSERVER"]

def run_frame(store, frame, bpm_raw, cfg):
    last = store.get_meta("last_bpm", 120)
    bpm, rhythm, weights = aggression_from_bpm(bpm_raw, last)
    store.set_meta("last_bpm", bpm)
    gas = 12 + max(0, int((bpm - 100) * 0.8))
    if cfg.get("drawdown", 0.04) >= cfg.get("max_dd", 0.12):
        return {"frame": frame, "status": "0xHALT_SELL_ONLY",
                "reason": "drawdown over limit", "gas": gas, "rhythm": rhythm}
    rng = random.Random(cfg.get("seed", 2026) + frame)
    telemetry = {a: f"OK_{rng.randint(100, 999)}" for a in AGENTS}
    payload = {"frame": frame, "bpm": bpm, "gas": gas, "weights": weights, "telemetry": telemetry}
    root, plate = state_root(payload), guinness_sha(payload)
    if rng.random() < 0.25:
        store.record(frame, "0xREVERT_RISK_EXCEEDED", root, plate, bpm, gas, rhythm)
        return {"frame": frame, "status": "0xREVERT_RISK_EXCEEDED",
                "25sha": root, "guinness_sha256": plate, "gas": gas, "rhythm": rhythm}
    store.record(frame, "0xCOMMITTED", root, plate, bpm, gas, rhythm)
    return {"frame": frame, "status": "0xCOMMITTED",
            "25sha": root, "guinness_sha256": plate, "gas": gas, "rhythm": rhythm}
```

```python
# store.py (SQLite, same pattern as quantum-seas store)
import sqlite3

TRADERS = [
    ("0xVESP", "Vesperin Quell", "QUIET SNIPER", 43155, 35289),
    ("0xKAEL", "Kaelith Voss", "ICE CLOSER", 41917, 25340),
    ("0xROOK", "Rook-Nine", "PINK SPRINTER", 41313, 22624),
    ("0xSABL", "Sable Quill", "HASH BOOKIE", 40970, 16882),
]

class Store:
    def __init__(self, path="desk.db"):
        self.path = path
        db = sqlite3.connect(self.path)
        db.executescript("CREATE TABLE IF NOT EXISTS frames(frame INTEGER PRIMARY KEY, status TEXT, root TEXT, plate TEXT, bpm INTEGER, gas INTEGER, rhythm TEXT); CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT); CREATE TABLE IF NOT EXISTS traders(id TEXT PRIMARY KEY, name TEXT, title TEXT, book INTEGER, cash INTEGER);")
        for t in TRADERS:
            db.execute("INSERT OR IGNORE INTO traders VALUES (?,?,?,?,?)", t)
        db.commit(); db.close()
    def traders(self):
        db = self._db()
        rows = db.execute("SELECT id,name,title,book,cash FROM traders ORDER BY book DESC").fetchall()
        db.close()
        return [{"id": r[0], "name": r[1], "title": r[2], "book": r[3], "cash": r[4]} for r in rows]
```
    def _db(self):
        return sqlite3.connect(self.path)
    def get_meta(self, k, default):
        db = self._db()
        r = db.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        db.close()
        return type(default)(r[0]) if r else default
    def set_meta(self, k, v):
        db = self._db()
        db.execute("INSERT INTO meta VALUES (?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, str(v)))
        db.commit(); db.close()
    def record(self, frame, status, root, plate, bpm, gas, rhythm):
        db = self._db()
        db.execute("INSERT OR REPLACE INTO frames VALUES (?,?,?,?,?,?,?)", (frame, status, root, plate, bpm, gas, rhythm))
        db.commit(); db.close()
```

```python
# judges.py — 7-gate wrapper (Guinness eligibility: exactly the floor COMMIT + no DD breach)
def eligible(result):
    return result.get("status") == "0xCOMMITTED"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_desk.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/backend/app/floor.py dj-matryxx-sacred-loop/backend/app/judges.py dj-matryxx-sacred-loop/backend/app/store.py dj-matryxx-sacred-loop/backend/tests/test_desk.py
git commit -m "feat: floor cycle, 7-gate eligibility, sqlite ledger"
```

### Task 4: Desk API

**Files:**
- Create: `dj-matryxx-sacred-loop/backend/app/main.py`
- Create: `dj-matryxx-sacred-loop/backend/requirements.txt`
- Test: `dj-matryxx-sacred-loop/backend/tests/test_api.py`

**Interfaces:**
- Consumes: `run_frame` (Task 3), `verify_plate` (Task 2).
- Produces: HTTP `GET /health`, `GET /desk/today`, `POST /desk/tick`, `GET /plate/current`.

- [ ] **Step 1: Write the failing test**

```python
def test_tick_validation_and_today():
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    assert c.get("/health").json() == {"ok": True}
    assert c.post("/desk/tick", json={"frame": 1, "bpm": -5}).status_code == 422
    r = c.post("/desk/tick", json={"frame": 5001, "bpm": 138.0})
    assert r.json()["status"] in ("0xCOMMITTED", "0xREVERT_RISK_EXCEEDED")
    t = c.get("/desk/today")
    assert "max-age=5" in t.headers.get("cache-control", "")
    assert "disclaimer" in t.json()
    p = c.get("/plate/current")
    assert "guinness_sha256" in p.json()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_api.py -v`
Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

```python
"""Desk API. Fictional vessel ledger — not a brokerage, not a chain, not advice."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .floor import run_frame
from .store import Store

app = FastAPI(title="Barbie Pit Desk", version="0.1.0")
_store = None

def store():
    global _store
    if _store is None:
        _store = Store()
    return _store

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/desk/tick")
def tick(body: dict):
    try:
        frame = int(body.get("frame"))
        bpm = float(body.get("bpm"))
    except (TypeError, ValueError):
        raise HTTPException(422, "frame:int and bpm:number required")
    if bpm < 0 or bpm > 250:
        raise HTTPException(422, "bpm must be 0..250 (0 = sacred-pause hold)")
    return run_frame(store(), frame, bpm, {"max_dd": 0.12, "seed": 2026})

@app.get("/desk/today")
def today():
    db = store()._db()
    rows = db.execute("SELECT frame,status,root,plate,bpm,gas,rhythm FROM frames ORDER BY frame DESC LIMIT 30").fetchall()
    db.close()
    body = {"frames": [{"frame": r[0], "status": r[1], "25sha": r[2], "guinness_sha256": r[3], "bpm": r[4], "gas": r[5], "rhythm": r[6]} for r in rows],
            "traders": store().traders(),
            "fills": [{"frame": r[0], "status": r[1], "25sha": r[2], "bpm": r[4]} for r in rows if r[1] == "0xCOMMITTED"],
            "alerts": [r[1] for r in rows if r[1] != "0xCOMMITTED"],
            "disclaimer": "Fictional vessel ledger — not a brokerage, not a chain, not advice."}
    return JSONResponse(body, headers={"Cache-Control": "public, max-age=5"})

@app.get("/plate/current")
def plate():
    db = store()._db()
    r = db.execute("SELECT plate FROM frames WHERE status='0xCOMMITTED' ORDER BY frame DESC LIMIT 1").fetchone()
    db.close()
    return {"guinness_sha256": r[0] if r else None,
            "disclaimer": "Fictional vessel ledger — not a brokerage, not a chain, not advice."}
```

```text
# requirements.txt
fastapi>=0.115
uvicorn[standard]>=0.30
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/backend/app/main.py dj-matryxx-sacred-loop/backend/requirements.txt dj-matryxx-sacred-loop/backend/tests/test_api.py
git commit -m "feat: desk api with 422 validation and plate endpoint"
```

### Task 5: Frontend — artifact + audio + branding

**Files:**
- Modify: `dj-matryxx-sacred-loop/index.html` (leaderboard, frame controls, BOOK/FLOOR windows, poll, footer already present — extend with live data hooks)
- Create: `dj-matryxx-sacred-loop/assets/audio.js`
- Test: manual — `python -m http.server` + `smoke_desk.py` (Task 6); assert no "Coexist" strings: `rg -i coexist dj-matryxx-sacred-loop` returns nothing.

**Interfaces:**
- Consumes: `GET /desk/today`, `POST /desk/tick`, `GET /plate/current` (Task 4).
- Produces: live desk rendering; `window.DeskBPM.current()` used by tick sender.

- [ ] **Step 1: Write the failing check**

```bash
rg -i "coexist" dj-matryxx-sacred-loop && echo FOUND || echo CLEAN
test -f dj-matryxx-sacred-loop/assets/audio.js || echo MISSING_AUDIO
```

Expected: CLEAN + MISSING_AUDIO.

- [ ] **Step 2: Write `assets/audio.js` (WebAudio BPM estimator, isolated)**

```js
// Analyser-based energy-peak BPM estimator. No deps. Sacred-pause on silence.
window.DeskBPM = (() => {
  let last = 128;
  async function fromMic(onBpm) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const src = ctx.createMediaStreamSource(stream);
    const an = ctx.createAnalyser(); an.fftSize = 2048;
    src.connect(an);
    const buf = new Uint8Array(an.frequencyBinCount);
    let peaks = [];
    setInterval(() => {
      an.getByteTimeDomainData(buf);
      let e = 0;
      for (const v of buf) e += Math.abs(v - 128);
      e /= buf.length;
      const t = performance.now();
      if (e > 8) { peaks.push(t); if (peaks.length > 8) peaks.shift(); }
      if (peaks.length >= 4) {
        const d = (peaks[peaks.length - 1] - peaks[0]) / (peaks.length - 1);
        const bpm = Math.round(60000 / d);
        if (bpm >= 60 && bpm <= 200) { last = bpm; onBpm(bpm, "LIVE_RHYTHM"); return; }
      }
      onBpm(last, "SACRED_PAUSE (BPM_HOLD)");
    }, 500);
  }
  return { current: () => last, fromMic };
})();
```

- [ ] **Step 3: Hook `index.html` (poll + tick sender, keep existing skin)**

Add before `</body>`: script that every 5s GETs `/desk/today` into BOOK/FLOOR regions and POSTs `/desk/tick` with `window.DeskBPM.current()`. Keep MATRYXX LLC footer untouched.

- [ ] **Step 4: Verify**

Run: `rg -i "coexist" dj-matryxx-sacred-loop; echo "rg-exit:$?"` Expected: exit 1 (no matches). Load page, confirm footer shows MATRYXX LLC + disclaimer.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/index.html dj-matryxx-sacred-loop/assets/audio.js
git commit -m "feat: live desk hooks, webaudio bpm, matryxx footer"
```

### Task 6: Smoke + runbook + Dockerfile

**Files:**
- Create: `dj-matryxx-sacred-loop/backend/smoke_desk.py`
- Create: `dj-matryxx-sacred-loop/backend/Dockerfile`
- Create: `dj-matryxx-sacred-loop/docs/RUNBOOK.md`
- Test: run smoke against local uvicorn; expect `SMOKE OK`.

**Interfaces:**
- Consumes: Task 4 endpoints.
- Produces: deployable image (workers 1), runbook.

- [ ] **Step 1: Write failing check**

Run: `test -f dj-matryxx-sacred-loop/backend/smoke_desk.py || echo MISSING_SMOKE`
Expected: MISSING_SMOKE.

- [ ] **Step 2: Write `smoke_desk.py` (stdlib urllib only)**

```python
"""GET /health -> POST /desk/tick bad 422 -> tick ok -> today has frames -> plate verify."""
import json, sys, urllib.request, urllib.error
BASE = "http://127.0.0.1:8080"
def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, None
s, b = call("GET", "/health")
assert (s, b) == (200, {"ok": True}), (s, b)
s, _ = call("POST", "/desk/tick", {"frame": 1, "bpm": -5})
assert s == 422, s
s, b = call("POST", "/desk/tick", {"frame": 5001, "bpm": 138.0})
assert s == 200 and "25sha" in b, (s, b)
s, b = call("GET", "/desk/today")
assert s == 200 and b["frames"], (s, b)
print("SMOKE OK")
```

- [ ] **Step 3: Write `Dockerfile` + `RUNBOOK.md`**

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd -r app && mkdir -p /data && chown app /data
USER app
ENV DATABASE_PATH=/data/desk.db
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4).read()"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
```

Runbook: deploy (App Runner/ECS, `/data` volume), env (`DATABASE_PATH`), tick cadence per wall mode, DD response (sell-only), Guinness rotation yearly, re-verify `rg -i coexist` on release.

- [ ] **Step 4: Run smoke**

Run: `uvicorn app.main:app --port 8080 & sleep 3; python smoke_desk.py; kill %1`
Expected: `SMOKE OK`.

- [ ] **Step 5: Commit**

```bash
git add dj-matryxx-sacred-loop/backend/smoke_desk.py dj-matryxx-sacred-loop/backend/Dockerfile dj-matryxx-sacred-loop/docs/RUNBOOK.md
git commit -m "chore: desk smoke, docker single-worker, runbook"
```
