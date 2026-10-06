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
