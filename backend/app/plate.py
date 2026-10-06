import hashlib
import json


def guinness_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_plate(payload, plate):
    return guinness_sha(payload) == plate
