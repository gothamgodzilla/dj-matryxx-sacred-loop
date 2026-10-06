// Analyser-based energy-peak BPM estimator. No deps. Sacred-pause on silence.
window.DeskBPM = (() => {
  let last = 128;
  async function fromMic(onBpm) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const src = ctx.createMediaStreamSource(stream);
    const an = ctx.createAnalyser(); an.fftSize = 2048;
    src.connect(an);
    const buf = new Uint8Array(an.frequencyBinCount);
    let peaks = [];
    setInterval(() => {
      an.getByteTimeDomainData(buf);
      let e = 0;
      for (const v of buf) e += Math.abs(v - 128);
      e /= buf.length;
      const t = performance.now();
      if (e > 8) { peaks.push(t); if (peaks.length > 8) peaks.shift(); }
      if (peaks.length >= 4) {
        const d = (peaks[peaks.length - 1] - peaks[0]) / (peaks.length - 1);
        const bpm = Math.round(60000 / d);
        if (bpm >= 60 && bpm <= 200) { last = bpm; onBpm(bpm, "LIVE_RHYTHM"); return; }
      }
      onBpm(last, "SACRED_PAUSE (BPM_HOLD)");
    }, 500);
  }
  return { current: () => last, fromMic };
})();
