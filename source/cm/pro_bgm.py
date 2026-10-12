# 前置き（15秒）の音：映画の予告編のような低い「ブォーン」・ピアノ・夜明けの盛り上がり → pro_bgm.wav
# 画面（pro.html）と同じ時刻で鳴らす。最後は光に飲みこまれて、本編（bgm2.wav）へそのままつながる
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000; DUR = 15.0; N = int(SR * DUR)
rng = np.random.default_rng(1012)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pro_bgm.wav')
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def hz(n):
    return 440.0 * 2 ** ((12 * (int(n[-1]) + 1) + NOTE[n[:-1]] - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def stereo(x, pan=0.0):
    if x.ndim == 2:
        return x
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)


def bus():
    return np.zeros((N, 2))


def put(b, t0, x, g=1.0, pan=0.0):
    x = stereo(x, pan); i0 = int(round(t0 * SR))
    if i0 < 0:
        x = x[-i0:]; i0 = 0
    n = min(len(x), N - i0)
    if n > 0:
        b[i0:i0 + n] += g * x[:n]


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x, axis=0)


def ramp(y, a=0.003, r=0.01):
    na, nr = max(1, int(a * SR)), max(1, int(r * SR)); y = y.copy()
    ea, er = np.linspace(0, 1, na), np.linspace(1, 0, nr)
    if y.ndim == 2:
        ea, er = ea[:, None], er[:, None]
    y[:na] *= ea; y[-nr:] *= er
    return y


def saw(f, n, ph0=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    dt = f / SR; ph = (ph0 + np.cumsum(dt) - dt[0]) % 1.0
    y = 2 * ph - 1
    m = ph < dt; x = ph[m] / dt[m]; y[m] -= x + x - x * x - 1
    m = ph > 1 - dt; x = (ph[m] - 1) / dt[m]; y[m] -= x * x + x + x + 1
    return y


def svf_bp(x, fc, q):
    g = np.tan(np.pi * np.minimum(fc, SR * 0.45) / SR); k = 1 / q
    ic1 = ic2 = 0.0; out = np.empty_like(x)
    for i in range(len(x)):
        gi = g[i]; a1 = 1 / (1 + gi * (gi + k)); a2 = gi * a1; a3 = gi * a2
        v3 = x[i] - ic2; v1 = a1 * ic1 + a2 * v3; v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2; out[i] = v1
    return out


# ================= 音色 =================
def braam(notes, length=3.2, g=1.0):
    """予告編の『ブォーン』：低いブラスの和音（暗い音から明るく開いて、ゆっくり消える）"""
    n = int(length * SR); t = tt(n); y = np.zeros((n, 2))
    for i, nt in enumerate(notes):
        f = hz(nt)
        for d, pan in ((-0.07, -0.6), (0.0, 0.0), (0.07, 0.6)):
            y += stereo(saw(f * 2 ** (d / 12), n, rng.uniform()), pan)
        if i == 0:
            y += stereo(np.sin(2 * np.pi * f * t)) * 1.5
    dark, br = filt(y, 'lowpass', 320), filt(y, 'lowpass', 2400)
    fe = np.interp(t, [0, 0.06, 0.35, 1.2, length], [0, 1, 0.75, 0.3, 0.1])[:, None]
    y = dark * (1 - fe) + br * fe
    y = np.tanh(y * 0.9) * 0.9
    env = np.interp(t, [0, 0.03, 0.5, length], [0, 1, 0.65, 0])[:, None] * np.exp(-t / 1.6)[:, None]
    return ramp(y * env * g / np.sqrt(len(notes)), 0.003, 0.2)


def piano(f, length=3.5, g=1.0):
    n = int(length * SR); t = tt(n); y = np.zeros(n)
    for k in range(1, 9):
        fk = k * f * np.sqrt(1 + 0.0004 * k * k)
        if fk > SR / 2.2:
            break
        y += (1 / k ** 1.25) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t / (2.4 / k ** 0.75))
    y += filt(rng.standard_normal(n), 'bandpass', [1500, 6000]) * np.exp(-t / 0.004) * 0.15
    y *= np.exp(-t / 1.8)
    return ramp(y * g * 0.5, 0.001, 0.15)


def boom(length=1.8, f0=30, f1=70, tau=0.6):
    n = int(length * SR); t = tt(n); f = f0 + f1 * np.exp(-t / 0.09)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    y += filt(rng.standard_normal(n), 'lowpass', 200) * np.exp(-t / 0.05) * 0.4
    return ramp(np.tanh(1.5 * y), 0.001, 0.08)


def crash(length=2.8, tau=1.0, rev=False):
    n = int(length * SR); t = tt(n); ys = []
    for _ in range(2):
        y = filt(rng.standard_normal(n), 'highpass', 3500) * 0.8
        for f in (3150, 4230, 5470, 6810, 8230, 9670):
            y += 0.05 * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
        ys.append(y * np.exp(-t / tau))
    y = np.stack(ys, 1)
    if rev:
        y = y[::-1]
    return ramp(y, 0.001 if not rev else 0.1, 0.1 if not rev else 0.004)


def bell(f, length=3.0, tau=1.2, idx=1.2):
    n = int(length * SR); t = tt(n); I = idx * np.exp(-t / 0.4)
    y = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t / tau)
    return ramp(y, 0.002, 0.1)


def pad(notes, length, attack=0.4, release=0.8, cut=2600, g=0.2):
    n = int((length + release) * SR); t = tt(n); y = np.zeros((n, 2))
    for nt in notes:
        for i in range(5):
            d = (i - 2) / 2 * 0.12; pan = (i - 2) / 2 * 0.8
            y += stereo(saw(hz(nt) * 2 ** (d / 12), n, rng.uniform()), pan)
    y = filt(y, 'lowpass', cut)
    env = np.interp(t, [0, attack, length, length + release], [0, 1, 1, 0])[:, None]
    return y * env * g / np.sqrt(len(notes) * 5)


def whoosh(length=0.7, f0=300, f1=4500, peak=0.62, pan0=-0.7, pan1=0.7):
    n = int(length * SR); t = tt(n); u = t / length
    fc = np.where(u < peak, f0 * (f1 / f0) ** (u / peak), f1 * 0.3 ** ((u - peak) / (1 - peak)))
    y = svf_bp(rng.standard_normal(n), fc, 1.2)
    env = np.where(u < peak, (u / peak) ** 2, (1 - (u - peak) / (1 - peak)) ** 1.6)
    pan = pan0 + (pan1 - pan0) * u; a = (pan + 1) * np.pi / 4
    return ramp(np.stack([y * env * np.cos(a), y * env * np.sin(a)], 1) * np.sqrt(2), 0.005, 0.02)


def riser(length, f0=200, f1=6000):
    n = int(length * SR); t = tt(n); u = t / length
    y = svf_bp(rng.standard_normal(n), f0 * (f1 / f0) ** u, 1.8) * 0.7
    y += 0.2 * np.sin(2 * np.pi * np.cumsum(110 * 2 ** (3 * u)) / SR)
    return ramp(y * u ** 2.2, 0.01, 0.01)


def pluck(f, length=0.6, bright=1.4, tau=0.3):
    n = int(length * SR); t = tt(n); idx = bright * np.exp(-t / 0.05)
    return ramp(np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t / tau), 0.002, 0.04)


# ================= 流れ =================
LOW, MID, HI, FX, SEND = bus(), bus(), bus(), bus(), bus()
# 低いうなり（Am → 夜明けで C へ）
dr_n = int(12.4 * SR); t_ = tt(dr_n)
drone = np.sin(2 * np.pi * hz('A1') * t_) * 0.8 + filt(saw(hz('A1'), dr_n) + saw(hz('E2'), dr_n, .3) * .6, 'lowpass', 240) * 0.5
drone *= np.interp(t_, [0, 1.5, 5.3, 6.05, 6.25, 11.6, 12.4], [0, 1, 1, 0.15, 1, 1, 0]) * (1 + 0.15 * np.sin(2 * np.pi * 0.3 * t_))
put(LOW, 0.0, ramp(drone, 0.3, 0.3), 0.35)
air = filt(rng.standard_normal((N, 2)), 'bandpass', [3000, 9000]) * np.interp(tt(N), [0, 1, 14, 15], [0, 1, 1, .4])[:, None]
put(FX, 0.0, air, 0.012)
# 0.3〜0.5：小さな光 → 横に伸びる光
put(HI, 0.28, bell(hz('E6'), 2.5, 1.0, 0.8), 0.06, 0.3)
put(LOW, 0.5, boom(1.8), 0.55); put(FX, 0.5, crash(2.0, 0.7), 0.16); put(HI, 0.5, bell(hz('A6'), 3.0, 1.2, 1.4), 0.05, -0.3)
# 1：新しい競馬が、やってくる。
put(MID, 0.75, piano(hz('A4')), 0.5); put(SEND, 0.75, piano(hz('A4')), 0.35)
put(LOW, 1.4, braam(['A1', 'E2', 'A2']), 0.85); put(LOW, 1.4, boom(2.0, 28, 60, 0.7), 0.6); put(FX, 1.4, crash(2.6, 1.0), 0.12)
put(MID, 1.4, piano(hz('A3')), 0.4); put(MID, 1.4, piano(hz('E4')), 0.35); put(SEND, 1.4, braam(['A2', 'E3']), 0.25)
put(FX, 2.55 - 0.42, whoosh(0.7, pan0=-.6, pan1=.6), 0.16)
# 2：まったく新しい、競馬判定アプリ
put(MID, 3.05, piano(hz('E5')), 0.45); put(SEND, 3.05, piano(hz('E5')), 0.35)
put(LOW, 3.6, braam(['F1', 'C2', 'F2']), 0.8); put(LOW, 3.6, boom(1.8), 0.55); put(FX, 3.6, crash(2.2, 0.8), 0.12)
put(MID, 3.6, piano(hz('C5')), 0.35); put(MID, 3.6, piano(hz('A4')), 0.3)
put(FX, 4.85 - 0.42, whoosh(0.7, pan0=.6, pan1=-.6), 0.16)
# 3：ロゴ（ため → 一瞬の静けさ → ドン）
put(FX, 5.3, riser(0.82), 0.5); put(FX, 6.2 - 1.2, crash(1.2, 0.45, rev=True), 0.3)
put(LOW, 6.2, braam(['A1', 'E2', 'A2', 'C3', 'E3'], 4.0), 1.0); put(LOW, 6.2, boom(2.4, 26, 70, 0.9), 0.85)
put(FX, 6.2, crash(3.4, 1.4), 0.3); put(SEND, 6.2, braam(['A2', 'E3', 'A3']), 0.3)
for i, (nt, pn) in enumerate((('A6', -.4), ('E7', .4), ('B6', 0.))):
    put(HI, 6.25 + 0.06 * i, bell(hz(nt), 3.0, 1.3, 1.6), 0.05, pn)
put(MID, 6.25, pad(['A3', 'C4', 'E4', 'B4'], 1.9, 0.25, 0.6), 0.9)
put(MID, 6.95, piano(hz('C5'), 3.0, .8), 0.3); put(MID, 7.15, piano(hz('E5'), 3.0, .8), 0.25)
put(FX, 8.05 - 0.42, whoosh(0.7), 0.16)
# 4：競馬初心者から、熟練者まで。それぞれの、新しい競馬。
for t0, nt in ((8.5, 'A4'), (9.2, 'C5'), (10.0, 'E5')):
    put(MID, t0, piano(hz(nt)), 0.45); put(SEND, t0, piano(hz(nt)), 0.3)
    put(LOW, t0, boom(1.0, 40, 50, 0.25), 0.3)
put(MID, 10.0, pad(['F3', 'A3', 'C4', 'G4'], 0.5, 0.3, 0.3, 1800), 0.6)
put(LOW, 10.4, braam(['G1', 'D2', 'G2']), 0.8); put(LOW, 10.4, boom(1.8), 0.55); put(FX, 10.4, crash(2.4, 0.9), 0.13)
put(MID, 10.4, piano(hz('G4')), 0.35); put(MID, 10.4, piano(hz('D5')), 0.3)
put(FX, 11.55 - 0.42, whoosh(0.7, pan0=.6, pan1=-.6), 0.16)
# 5：新しい時代の、幕開け。（夜明け：C の和音が明るく広がる）
sw = pad(['C3', 'G3', 'C4', 'E4', 'G4', 'D5'], 3.0, 1.6, 0.05, 3200, 0.26)
put(MID, 12.0, sw, 1.0)
put(MID, 12.3, piano(hz('C5')), 0.45); put(SEND, 12.3, piano(hz('C5')), 0.3)
ARP = ['C5', 'E5', 'G5', 'C6', 'D6', 'E6', 'G6', 'C7']
k = 0; t0 = 12.4
while t0 < 14.7:
    u = (t0 - 12.4) / 2.3
    put(HI, t0, pluck(hz(ARP[k % 8]), 0.5, 1.2, 0.22), 0.04 + 0.08 * u, (-.5, .5)[k % 2]); k += 1; t0 += 0.13
put(LOW, 12.9, braam(['C2', 'G2', 'C3', 'E3'], 3.0), 0.95); put(LOW, 12.9, boom(2.0, 28, 70, 0.8), 0.75); put(FX, 12.9, crash(2.6, 1.1), 0.25)
for i, (nt, pn) in enumerate((('C7', -.4), ('G6', .4))):
    put(HI, 12.95 + 0.07 * i, bell(hz(nt), 2.5, 1.1, 1.4), 0.05, pn)
# 光に飲みこまれる（14.3〜15.0）
put(FX, 15.0 - 1.4, crash(1.4, 0.5, rev=True), 0.35)
sn = int(0.75 * SR); swell = filt(rng.standard_normal((sn, 2)), 'highpass', 800) * (np.linspace(0, 1, sn) ** 2.5)[:, None]
put(FX, 14.25, swell, 0.22)

# ================= ミックス =================
for b_, g_ in ((MID, 0.35), (HI, 0.5), (LOW, 0.08)):
    SEND += b_ * g_
ir_n = int(3.2 * SR); t_ = tt(ir_n)
ir = rng.standard_normal((ir_n, 2)) * np.exp(-t_ / 0.9)[:, None]
ir = filt(ir, 'lowpass', 6500); ir[:int(0.02 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
wet = np.stack([fftconvolve(SEND[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = LOW * 1.0 + MID * 1.0 + HI * 1.0 + FX * 1.0 + wet * 0.5
mix = filt(mix, 'highpass', 25)
fi = int(0.005 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.02 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.1) / 1.1
mix *= 0.89 / np.max(np.abs(mix))
mix *= 10 ** (float(os.environ.get('GAIN_DB', '-1.0')) / 20)
wavfile.write(OUT, SR, (mix * 32767).astype(np.int16))
print('ok', OUT, 'peak', round(float(np.max(np.abs(mix))), 3))
