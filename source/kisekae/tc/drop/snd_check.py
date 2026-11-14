# 音を 数字で 確かめる（ピの 数・高さ・長さ・低い 音）
import sys, os
import numpy as np
from scipy.io import wavfile
from scipy import signal
D = sys.argv[1]


def onsets(x, sr, f1, f2, thr=0.25, gap=0.05):
    b, a = signal.butter(3, [f1 / (sr / 2), f2 / (sr / 2)], 'band')
    y = np.abs(signal.lfilter(b, a, x))
    w = int(0.004 * sr); e = np.convolve(y, np.ones(w) / w, 'same')
    e /= e.max() + 1e-12
    on = []; last = -9
    d = np.diff(e, prepend=0)
    for i in range(1, len(e)):
        if e[i] > thr and e[i - 1] <= thr and i / sr - last > gap:
            on.append(round(i / sr, 3)); last = i / sr
    return on, e


def peakf(x, sr, t0, t1, lo=300, hi=9000):
    s = x[int(t0 * sr):int(t1 * sr)]
    if len(s) < 256: return None
    S = np.abs(np.fft.rfft(s * np.hanning(len(s)))); f = np.fft.rfftfreq(len(s), 1 / sr)
    m = (f > lo) & (f < hi)
    return round(float(f[m][S[m].argmax()]), 1)


for nm in ('uma1', 'uma2', 'uma3', 'uma4', 'uma5', 'uma6'):
    sr, w = wavfile.read(os.path.join(D, f'tc_se_dp_{nm}.wav')); x = w.astype(np.float64).mean(1) / 32767
    on, e = onsets(x, sr, 1700, 3000)
    # ピの 高さ：それぞれの 出だしから 50ms
    fs = [peakf(x, sr, t + 0.005, t + 0.06, 1500, 3200) for t in on]
    # うしろの のこり（−30dB まで）
    env = np.abs(signal.hilbert(x)); pk = env.max(); tail = np.nonzero(env > pk * 10 ** (-30 / 20))[0][-1] / sr
    lowb, lowa = signal.butter(3, 200 / (sr / 2), 'low'); low = signal.lfilter(lowb, lowa, x)
    midb, mida = signal.butter(3, [200 / (sr / 2), 900 / (sr / 2)], 'band'); mid = signal.lfilter(midb, mida, x)
    rms = lambda v: float(np.sqrt((v ** 2).mean()))
    print(f'{nm}: len {len(x) / sr:.2f}s peak {np.abs(x).max():.2f} rms {rms(x):.3f} | high-band onsets {len(on)} at {on} freqs {fs} | −30dB at {tail:.2f}s | low(<200Hz) rms {rms(low):.3f} mid(200-900) rms {rms(mid):.3f}')
for nm in ('out', 'peg1', 'peg2', 'peg3', 'cup', 'miss', 'hold', 'open'):
    sr, w = wavfile.read(os.path.join(D, f'tc_se_dp_{nm}.wav')); x = w.astype(np.float64).mean(1) / 32767
    env = np.abs(signal.hilbert(x)); pk = env.max(); tail = np.nonzero(env > pk * 10 ** (-30 / 20))[0][-1] / sr
    print(f'{nm}: len {len(x) / sr:.2f}s peak {np.abs(x).max():.2f} peak freq {peakf(x, sr, 0, min(0.2, len(x) / sr))} −30dB at {tail:.2f}s')
