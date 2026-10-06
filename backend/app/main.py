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
    rows = db.execute(
        "SELECT frame,status,root,plate,bpm,gas,rhythm FROM frames "
        "ORDER BY frame DESC LIMIT 30"
    ).fetchall()
    db.close()
    body = {
        "frames": [
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
        ],
        "traders": store().traders(),
        "fills": [
            {"frame": r[0], "status": r[1], "25sha": r[2], "bpm": r[4]}
            for r in rows
            if r[1] == "0xCOMMITTED"
        ],
        "alerts": [r[1] for r in rows if r[1] != "0xCOMMITTED"],
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
