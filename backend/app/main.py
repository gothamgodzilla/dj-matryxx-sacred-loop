"""Desk API. Fictional vessel ledger — not a brokerage, not a chain, not advice."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .floor import run_frame
from .store import Store

app = FastAPI(title="Barbie Pit Desk", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TRADER_BIOS = {
    "0xVESP": "Says almost nothing. Watches the decoy print first. Fires once.",
    "0xKAEL": "Does not chase. Lets them overtrade the pink, then stamps the close.",
    "0xROOK": "First ping, first fill. Treats Barbie as a weapon. Speed is the personality.",
    "0xSABL": "Camp, precise, mean with a smile. SHA-256 or it did not happen.",
}


def _floor_feed(latest: dict | None) -> list[dict]:
    agents = [
        ("RESEARCHER", "live"),
        ("ANALYST", "live"),
        ("QUOTER", "live"),
        ("EXECUTOR", "live"),
        ("RISK", "veto" if latest and "REVERT" in latest.get("status", "") else "live"),
        ("OBSERVER", "live"),
    ]
    if not latest:
        return [{"agent": a, "state": s, "msg": "Awaiting first tick…"} for a, s in agents]
    f, bpm, gas, rhythm, st = (
        latest["frame"],
        latest["bpm"],
        latest["gas"],
        latest["rhythm"],
        latest["status"],
    )
    msgs = [
        f"Frame {f} · BPM {bpm} · {rhythm}",
        f"Fair value mid · gas {gas} gwei",
        "Risk sell-only" if "HALT" in st else "Ladder ask-side" if "REVERT" in st else "Two-sided quotes",
        f"Last status {st}",
        "Tighten limit · inventory skew" if "REVERT" in st else "Floor within band",
        f"25SHA {latest.get('25sha', '')[:12]}… · {st}",
    ]
    return [{"agent": a, "state": s, "msg": m} for (a, s), m in zip(agents, msgs)]
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
    rows = db.execute(
        "SELECT frame,status,root,plate,bpm,gas,rhythm FROM frames "
        "ORDER BY frame DESC LIMIT 30"
    ).fetchall()
    db.close()
    frames = [
            {
                "frame": r[0],
                "status": r[1],
                "25sha": r[2],
                "guinness_sha256": r[3],
                "bpm": r[4],
                "gas": r[5],
                "rhythm": r[6],
            }
            for r in rows
        ]
    traders = store().traders()
    for t in traders:
        t["bio"] = TRADER_BIOS.get(t["id"], "")
    latest = frames[0] if frames else None
    book_total = sum(t["book"] for t in traders)
    body = {
        "frames": frames,
        "traders": traders,
        "book": {
            "equity": book_total,
            "leading": traders[0]["name"] if traders else "—",
            "latest_frame": latest,
            "plate_hint": latest.get("guinness_sha256", "")[:16] if latest else None,
        },
        "floor": _floor_feed(latest),
        "fills": [
            {"frame": r[0], "status": r[1], "25sha": r[2], "bpm": r[4]}
            for r in rows
            if r[1] == "0xCOMMITTED"
        ],
        "alerts": [r[1] for r in rows if r[1] != "0xCOMMITTED"],
        "telemetry_feed": store().recent_telemetry(80),
        "repair_generation": store().get_meta("repair_generation", 0),
        "disclaimer": "Fictional vessel ledger — not a brokerage, not a chain, not advice.",
    }
    return JSONResponse(body, headers={"Cache-Control": "public, max-age=5"})


@app.get("/plate/current")
def plate():
    db = store()._db()
    r = db.execute(
        "SELECT plate FROM frames WHERE status='0xCOMMITTED' "
        "ORDER BY frame DESC LIMIT 1"
    ).fetchone()
    db.close()
    return {
        "guinness_sha256": r[0] if r else None,
        "disclaimer": "Fictional vessel ledger — not a brokerage, not a chain, not advice.",
    }
