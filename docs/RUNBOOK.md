# Desk Runbook (Barbie Pit × Sacred Loop)

Operator: MATRYXX LLC, Sheridan Wyoming. Product: Wingman.OS.
Fictional vessel ledger — not a brokerage, not a chain, not advice.

## Deploy
- Image: `backend/Dockerfile` (single worker; SQLite requires `--workers 1`).
- Volume: `/data` persistent (`DATABASE_PATH=/data/desk.db` — frames are the ledger).
- Health: `GET /health` (Docker `HEALTHCHECK`, 30s).

## Operate
- Tick cadence: `1sec=1hr` (demo) or `1min=1hr` (wall) — frontend posts
  `/desk/tick {frame, bpm}` every 5s with `window.DeskBPM.current()`.
- BPM loss → sacred-pause hold (last BPM, labeled). No action needed.
- Drawdown at/over limit → `0xHALT_SELL_ONLY`; reduce exposure config, then resume ticks.
- Veto (`0xREVERT_RISK_EXCEEDED`) is normal (~25% sim); no action needed.

## Guinness plate
- Yearly winner book SHA-256 via `GET /plate/current`; rotation yearly.
- Verify: `guinness_sha(payload) == plate` (`backend/app/plate.py`).

## Release check
- `rg -i "coexist" index.html assets/ backend/` must print nothing (docs may
  reference the replaced names only to record the MATRYXX LLC replacement).
- `python smoke_desk.py` → `SMOKE OK` against local uvicorn before deploy.
