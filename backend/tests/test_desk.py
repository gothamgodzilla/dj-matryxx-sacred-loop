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
