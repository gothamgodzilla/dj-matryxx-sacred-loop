def test_roots_deterministic_and_verify():
    from app.cache25 import state_root
    from app.plate import guinness_sha, verify_plate
    p = {"frame": 5001, "bpm": 138}
    assert state_root(p) == state_root(p) and len(state_root(p)) == 25
    plate = guinness_sha(p)
    assert verify_plate(p, plate) is True
    assert verify_plate({"frame": 5002, "bpm": 138}, plate) is False
