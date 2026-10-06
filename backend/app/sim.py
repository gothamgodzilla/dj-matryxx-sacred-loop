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
    return b, "LIVE_RHYTHM", w
