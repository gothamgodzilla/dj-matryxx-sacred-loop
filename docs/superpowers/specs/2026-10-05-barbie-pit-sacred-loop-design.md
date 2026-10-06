# Barbie Pit × Sacred Loop — Full-Stack Design (2026-10-05)

## 0. Intent (agreed)
Replicate `bromance.grok.me` Barbie Pit LIVE DESK as a product using
`dj-matryxx-sacred-loop` tech + formula. Scope: full-stack (frontend
artifact + FastAPI sim + SQLite fictional ledger). Success = working
4-trader live desk with BPM-driven aggression, 25SHA commits, Guinness
SHA-256 plate, persistent fictional-ledger disclaimer.

Out of scope: real brokerage, real chain, real advice. All ledgers fictional.

## 1. Architecture (Approved)
- Frontend: evolved `index.html` → Barbie-Pit layout in sacred-loop skin
  (teal/cyan/purple/gold holographic). WebAudio BPM engine (mic/file).
  Aggression `= f(BPM)`: >140 Rook bias, <110 Vesper bias, dropout = sacred pause.
- Backend: FastAPI sim, tick modes `1sec=1hr / 1min=1hr`. SQLite fictional
  ledger (`books, fills, plates, journal`). Cyclical floor loop, never linear.
- Consensus: 6-agent floor `RESEARCH→ANALYST→QUOTER→EXECUTOR→RISK(veto)→OBSERVER`
  + 7-judge overlay for Guinness eligibility. 25SHA 25-char state root per
  commit, full SHA-256 for Guinness plate.
- Flow: `tick(BPM,frame) → weights → floor cycle → 7-judge gate → 25SHA
  cache check → COMMIT fills | VETO-revert`. SSE/poll to UI.

## 2. Components (Revised: 0x contract space)
- Agent contracts: `0xVESP` Vesperin Quell 43,155 / 35,289 quiet-sniper,
  `0xKAEL` Kaelith Voss 41,917 / 25,340 ice-closer, `0xROOK` Rook-Nine
  41,313 / 22,624 pink-sprinter, `0xSABL` Sable Quill 40,970 / 16,882 hash-bookie.
- Pool contracts: `MYTHOS / HELIX / FOX / SEAL` (+ WARDEN/DECOY/QUILL/ROOK9
  frame symbols as watchlist).
- YOUR FRAME: pairs, capital +5k/+25k, 1× wall, speed, skew 20/40/60,
  DD 5/12/20, pause/reset. WINDOW1 BOOK (equity/run-rate/clock/vol/mid/
  sell-only/veto/bps/spread/fees/toxic/volume + alerts + fills).
  WINDOW2 FLOOR (6-agent live feed).
- Backend modules: `sim.py` (personality weights), `floor.py` (6-agent cycle),
  `judges.py` (7-gate), `cache25.py` (25SHA `sha256(canonical)[:25].upper()`),
  `plate.py` (Guinness SHA-256), `store.py` (SQLite), `audio.js` (BPM isolated).
- Reference CLIs (provided): `chain_prompt.py` (address-space + gas `12+(BPM-100)*0.8`
  + 0xRISK approve/veto/custom-hex), `section3_flow_tests.py` (tick pipeline + recovery).

## 3. Flow / Errors / Tests (Provided impl accepted)
- Pipeline: BPM → weights → floor telemetry → `sha256(frame:bpm:gas:telemetry)`
  → 25SHA + Guinness SHA-256 → 7-judge (75% pass sim) → `0xCOMMITTED` |
  `0xREVERT_RISK_EXCEEDED` | `0xHALT_SELL_ONLY`.
- Recovery: BPM loss → hold `last_valid_bpm`, label `SACRED_PAUSE (BPM_HOLD)`;
  DD ≥ limit → `sell-only` halt; queue stall → park/resume next tick.
- Tests: deterministic seed (2026), 25SHA golden roots, veto path,
  Guinness verify (`recompute == stored`), disclaimer footer on every export.
- Legal: `Fictional vessel ledger — not a brokerage, not a chain, not advice.`
  Persistent footer + header. Yearly winner book SHA-256 struck on vessel
  Guinness plate. No ties.

## 4. Interfaces
- `GET /health`, `GET /desk/today` (leaderboard+book+floor), `GET /desk/fills`,
  `POST /desk/tick {frame,bpm,frame_cfg}` → `{status, 25sha, guinness_sha256, gas}`,
  `POST /desk/pause|reset`, `GET /plate/current` (Guinness hash).
- Frontend reads via poll (5s) → SSE upgrade later. Single worker with SQLite.

## 6. Branding
- Operator: MATRYXX LLC (Sheridan, Wyoming). Product: Wingman.OS.
- Components: GANESH, LOGiX, MATRYXX (validation engine), Prince.
- MATRYXX LLC (company) is distinct from MATRYXX (validation engine).
- “Coexist LLC” / “Coexist Intelligence” branding replaced with “MATRYXX LLC”.
- Copyright © 2026 MATRYXX LLC. Branding update only; no legal rename or asset transfer.

## 5. Self-review
- No TBD. No contradictions (6 floor + 7 judges = distinct layers).
- Scope is one product slice; artifact-first, backend second.
- Ambiguity resolved: BPM formula explicit, gas explicit, DD sell-only explicit.
