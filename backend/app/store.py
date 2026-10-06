"""Persistence. SQLite fictional ledger (frames, meta, traders). Single worker only."""
import json
import sqlite3
import time

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
        db.executescript(
            "CREATE TABLE IF NOT EXISTS frames(frame INTEGER PRIMARY KEY, status TEXT, "
            "root TEXT, plate TEXT, bpm INTEGER, gas INTEGER, rhythm TEXT); "
            "CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT); "
            "CREATE TABLE IF NOT EXISTS traders(id TEXT PRIMARY KEY, name TEXT, title TEXT, "
            "book INTEGER, cash INTEGER); "
            "CREATE TABLE IF NOT EXISTS telemetry_events("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, frame INTEGER, kind TEXT, "
            "agent TEXT, phase TEXT, payload TEXT);"
        )
        for t in TRADERS:
            db.execute("INSERT OR IGNORE INTO traders VALUES (?,?,?,?,?)", t)
        db.commit()
        db.close()

    def _db(self):
        return sqlite3.connect(self.path)

    def get_meta(self, k, default):
        db = self._db()
        r = db.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        db.close()
        return type(default)(r[0]) if r else default

    def set_meta(self, k, v):
        db = self._db()
        db.execute(
            "INSERT INTO meta VALUES (?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (k, str(v)),
        )
        db.commit()
        db.close()

    def record(self, frame, status, root, plate, bpm, gas, rhythm):
        db = self._db()
        db.execute(
            "INSERT OR REPLACE INTO frames VALUES (?,?,?,?,?,?,?)",
            (frame, status, root, plate, bpm, gas, rhythm),
        )
        db.commit()
        db.close()

    def log_telemetry(self, frame: int, events: list[dict]):
        now = time.time()
        db = self._db()
        for ev in events:
            db.execute(
                "INSERT INTO telemetry_events VALUES (NULL,?,?,?,?,?,?)",
                (
                    now,
                    frame,
                    ev.get("kind", "telemetry"),
                    ev.get("agent", ""),
                    ev.get("phase", ""),
                    json.dumps(ev, separators=(",", ":")),
                ),
            )
        db.commit()
        db.close()

    def recent_telemetry(self, limit: int = 80) -> list[dict]:
        db = self._db()
        rows = db.execute(
            "SELECT payload FROM telemetry_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        db.close()
        out = []
        for (raw,) in reversed(rows):
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return out

    def traders(self):
        db = self._db()
        rows = db.execute(
            "SELECT id,name,title,book,cash FROM traders ORDER BY book DESC"
        ).fetchall()
        db.close()
        return [
            {"id": r[0], "name": r[1], "title": r[2], "book": r[3], "cash": r[4]}
            for r in rows
        ]
