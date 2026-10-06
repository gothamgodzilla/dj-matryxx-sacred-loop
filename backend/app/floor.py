"""Cyclical 6-agent floor: RESEARCH→ANALYST→QUOTER→EXECUTOR→RISK→OBSERVER."""
import random

from .cache25 import state_root
from .plate import guinness_sha
from .sim import aggression_from_bpm

AGENTS = ["0xRESEARCH", "0xANALYST", "0xQUOTER", "0xEXECUTOR", "0xRISK", "0xOBSERVER"]


def run_frame(store, frame, bpm_raw, cfg):
    last = store.get_meta("last_bpm", 120)
    bpm, rhythm, weights = aggression_from_bpm(bpm_raw, last)
    store.set_meta("last_bpm", bpm)
    gas = 12 + max(0, int((bpm - 100) * 0.8))
    if cfg.get("drawdown", 0.04) >= cfg.get("max_dd", 0.12):
        return {
            "frame": frame,
            "status": "0xHALT_SELL_ONLY",
            "reason": "drawdown over limit",
            "gas": gas,
            "rhythm": rhythm,
        }
    rng = random.Random(cfg.get("seed", 2026) + frame)
    telemetry = {a: f"OK_{rng.randint(100, 999)}" for a in AGENTS}
    payload = {
        "frame": frame,
        "bpm": bpm,
        "gas": gas,
        "weights": weights,
        "telemetry": telemetry,
    }
    root, plate = state_root(payload), guinness_sha(payload)
    if rng.random() < 0.25:
        store.record(frame, "0xREVERT_RISK_EXCEEDED", root, plate, bpm, gas, rhythm)
        return {
            "frame": frame,
            "status": "0xREVERT_RISK_EXCEEDED",
            "25sha": root,
            "guinness_sha256": plate,
            "gas": gas,
            "rhythm": rhythm,
        }
    store.record(frame, "0xCOMMITTED", root, plate, bpm, gas, rhythm)
    return {
        "frame": frame,
        "status": "0xCOMMITTED",
        "25sha": root,
        "guinness_sha256": plate,
        "gas": gas,
        "rhythm": rhythm,
    }
