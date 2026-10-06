def test_aggression_bias_and_pause():
    from app.sim import aggression_from_bpm
    _, _, w_hi = aggression_from_bpm(165.0, 120)
    _, _, w_lo = aggression_from_bpm(100.0, 120)
    assert w_hi["0xROOK"] > w_hi["0xVESP"]
    assert w_lo["0xVESP"] >= w_hi["0xVESP"]
    bpm, label, _ = aggression_from_bpm(0.0, 128)
    assert (bpm, label) == (128, "SACRED_PAUSE (BPM_HOLD)")
