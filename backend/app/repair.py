"""Recursive self-repair → verify → regenerate (cyclical, resumable)."""
REPAIR_PHASES = ("detect", "isolate", "patch", "verify", "regenerate", "rebind")


def needs_repair(status: str, rhythm: str) -> bool:
    return (
        "REVERT" in status
        or "HALT" in status
        or "SACRED" in rhythm
    )


def build_repair_events(frame: int, status: str, rhythm: str, root: str) -> list[dict]:
    if not needs_repair(status, rhythm):
        return []
    out = []
    for i, phase in enumerate(REPAIR_PHASES):
        out.append(
            {
                "kind": "repair",
                "frame": frame,
                "phase": phase,
                "depth": i + 1,
                "msg": f"recursive self-repair · {phase} · re-root {root[:12]}…",
            }
        )
    return out
