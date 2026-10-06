"""Cyclical 6-agent floor: RESEARCH→ANALYST→QUOTER→EXECUTOR→RISK→OBSERVER."""
import random

from .cache25 import state_root
from .plate import guinness_sha
from .repair import build_repair_events
from .sim import aggression_from_bpm

AGENTS = ["0xRESEARCH", "0xANALYST", "0xQUOTER", "0xEXECUTOR", "0xRISK", "0xOBSERVER"]


def run_frame(store, frame, bpm_raw, cfg):
    last = store.get_meta("last_bpm", 120)
    bpm, rhythm, weights = aggression_from_bpm(bpm_raw, last)
    store.set_meta("last_bpm", bpm)
    gas = 12 + max(0, int((bpm - 100) * 0.8))
    if cfg.get("drawdown", 0.04) >= cfg.get("max_dd", 0.12):
        status = "0xHALT_SELL_ONLY"
        repair_events = build_repair_events(frame, status, rhythm, "HALT")
        gen = store.get_meta("repair_generation", 0) + (1 if repair_events else 0)
        if repair_events:
            store.set_meta("repair_generation", gen)
        store.log_telemetry(
            frame,
            [{"kind": "telemetry", "frame": frame, "agent": "0xRISK", "msg": "DD breach"}]
            + repair_events,
        )
        return {
            "frame": frame,
            "status": status,
            "reason": "drawdown over limit",
            "gas": gas,
            "rhythm": rhythm,
            "telemetry": {},
            "repair": repair_events,
            "repair_generation": gen,
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
    status = "0xREVERT_RISK_EXCEEDED" if rng.random() < 0.25 else "0xCOMMITTED"
    store.record(frame, status, root, plate, bpm, gas, rhythm)
    telem_events = [
        {"kind": "telemetry", "frame": frame, "agent": a, "msg": v, "status": status}
        for a, v in telemetry.items()
    ]
    repair_events = build_repair_events(frame, status, rhythm, root)
    if repair_events:
        gen = store.get_meta("repair_generation", 0) + 1
        store.set_meta("repair_generation", gen)
    else:
        gen = store.get_meta("repair_generation", 0)
    store.log_telemetry(frame, telem_events + repair_events)
    return {
        "frame": frame,
        "status": status,
        "25sha": root,
        "guinness_sha256": plate,
        "gas": gas,
        "rhythm": rhythm,
        "telemetry": telemetry,
        "repair": repair_events,
        "repair_generation": gen,
    }
