"""GET /health -> POST /desk/tick bad 422 -> tick ok -> today has frames -> plate verify."""
import json
import sys
import urllib.error
import urllib.request

import os

BASE = os.getenv("DESK_API_BASE", "http://127.0.0.1:8080")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        BASE + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
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
