# CM第5弾のBGMと効果音（前置き3.2秒 → 題名 → ゆっくりの本編 → おわり → 注意書き）：150BPM・Aマイナー・60.4秒・48kHzステレオ → bgm5.wav
# 画面（cm5.html）と同じ時刻で鳴らす。前置きは派手に（いきなりドン・オーケストラのヒット・雷）、本編は控えめ（金の枠が出るところで小さなベル）
# 場面：前置き 0〜3.2・題名 3.2〜6.4・入力 6.4〜14.4・判定 14.4〜20.8・買い目編集 20.8〜27.2・自分のデータ 27.2〜33.6
#       自分だけのテンゲル 33.6〜38.4・買う馬／5重勝／収支 38.4〜45.6・おわり 45.6〜50.4・注意書き 50.4〜60.4
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000; DUR = 60.4; N = int(SR * DUR)
BEAT = 0.4; BAR = 1.6
rng = np.random.default_rng(20261012)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bgm5.wav')
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def hz(n):
    return 440.0 * 2 ** ((12 * (int(n[-1]) + 1) + NOTE[n[:-1]] - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def bus():
    return np.zeros((N, 2))


def stereo(x, pan=0.0):
    if x.ndim == 2:
        return x
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)


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


def square(f, n, ph0=0.0):
    return 0.5 * (saw(f, n, ph0) - saw(f, n, (ph0 + 0.5) % 1))


def svf_bp(x, fc, q):
    g = np.tan(np.pi * np.minimum(fc, SR * 0.45) / SR); k = 1 / q
    ic1 = ic2 = 0.0; out = np.empty_like(x)
    for i in range(len(x)):
        gi = g[i]; a1 = 1 / (1 + gi * (gi + k)); a2 = gi * a1; a3 = gi * a2
        v3 = x[i] - ic2; v1 = a1 * ic1 + a2 * v3; v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2; out[i] = v1
    return out


# ================= 音色 =================
def kick(big=False):
    n = int((0.9 if big else 0.36) * SR); t = tt(n)
    f = 48 + 135 * np.exp(-t / 0.028)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.3 if big else 0.13))
    click = filt(rng.standard_normal(n), 'highpass', 2000) * np.exp(-t / 0.002) * 0.45
    return ramp(np.tanh(2.2 * (body + click)) / np.tanh(2.2), 0.0005, 0.02)


def snare(v=1.0):
    n = int(0.25 * SR); t = tt(n)
    tone = (np.sin(2 * np.pi * 185 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)) * np.exp(-t / 0.045)
    nz = filt(rng.standard_normal(n), 'bandpass', [1200, 8000]) * np.exp(-t / 0.075)
    nz2 = filt(rng.standard_normal(n), 'bandpass', [1200, 8000]) * np.exp(-t / 0.075)
    return ramp(np.stack([0.55 * tone + 0.8 * nz, 0.55 * tone + 0.8 * nz2], 1) * v, 0.0005, 0.02)


def hat(open_=False, v=1.0):
    n = int((0.28 if open_ else 0.05) * SR); t = tt(n)
    y = filt(rng.standard_normal(n), 'highpass', 7500) * np.exp(-t / (0.09 if open_ else 0.012))
    return ramp(y * v, 0.0005, 0.01)


def crash(length=2.4, tau=0.8, rev=False):
    n = int(length * SR); t = tt(n); ys = []
    for _ in range(2):
        y = filt(rng.standard_normal(n), 'highpass', 4000) * 0.8
        for f in (3150, 4230, 5470, 6810, 8230, 9670):
            y += 0.06 * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
        ys.append(y * np.exp(-t / tau))
    y = np.stack(ys, 1)
    if rev:
        y = y[::-1]
    return ramp(y, 0.001 if not rev else 0.05, 0.05 if not rev else 0.004)


def boom(length=1.4, f0=34, f1=70, tau=0.45):
    n = int(length * SR); t = tt(n); f = f0 + f1 * np.exp(-t / 0.1)
    return ramp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau), 0.001, 0.05)


def supersaw(f, n, voices=7, spread=0.22, ph=None):
    y = np.zeros((n, 2))
    for i in range(voices):
        d = (i - (voices - 1) / 2) / ((voices - 1) / 2) * spread   # 半音単位
        pan = (i - (voices - 1) / 2) / ((voices - 1) / 2) * 0.8
        y += stereo(saw(f * 2 ** (d / 12), n, rng.uniform()), pan)
    return y / np.sqrt(voices)


def stab(notes, length=0.18, bright=3200, g=0.3):
    """オフビートのシンセのコード（ユーロビート風）"""
    n = int((length + 0.08) * SR); t = tt(n); y = np.zeros((n, 2))
    for nt in notes:
        y += supersaw(hz(nt), n, 5, 0.18)
    dark, br = filt(y, 'lowpass', 900), filt(y, 'lowpass', bright)
    fe = np.exp(-t / 0.07)[:, None]
    y = dark * (1 - fe) + br * fe
    env = np.interp(t, [0, 0.004, length, length + 0.08], [0, 1, 0.55, 0])[:, None]
    return y * env * g


def brass(notes, length=0.5, g=0.35, attack=0.012):
    """ブラス（ヒット・ファンファーレ）"""
    n = int((length + 0.25) * SR); t = tt(n); y = np.zeros((n, 2))
    for nt in notes:
        f = hz(nt) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.2, 0, 1))
        y += stereo(saw(f, n, rng.uniform()), rng.uniform(-0.5, 0.5)) + 0.5 * stereo(saw(f * 1.004, n, rng.uniform()), rng.uniform(-0.6, 0.6))
    dark, br = filt(y, 'lowpass', 700), filt(y, 'lowpass', 4200)
    fe = np.clip(np.interp(t, [0, attack + 0.02, 0.25, length], [0.2, 1, 0.65, 0.5]), 0, 1)[:, None]
    y = dark * (1 - fe) + br * fe
    env = np.interp(t, [0, attack, 0.12, length, length + 0.25], [0, 1, 0.8, 0.7, 0])[:, None]
    return y * env * g / max(1, len(notes)) ** 0.5


def orch_hit(notes, g=1.0):
    """オーケストラヒット：ブラス＋弦っぽい雑音＋ティンパニの低音"""
    n = int(1.2 * SR); t = tt(n)
    y = brass(notes, 0.18, 0.9, 0.003)[:n]
    if len(y) < n:
        y = np.vstack([y, np.zeros((n - len(y), 2))])
    nz = filt(rng.standard_normal((n, 2)), 'bandpass', [400, 5000]) * np.exp(-t / 0.06)[:, None] * 0.35
    low = stereo(np.sin(2 * np.pi * np.cumsum(hz(notes[0]) / 2 * (1 + 0.6 * np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.25)) * 0.5
    return ramp((y + nz + low) * g, 0.0008, 0.05)


def pluck(f, length=0.25, bright=2.4, tau=0.12):
    n = int(length * SR); t = tt(n); idx = bright * np.exp(-t / 0.04)
    return ramp(np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t / tau), 0.002, 0.03)


def bell(f, length=1.2, tau=0.4, idx=1.6):
    n = int(length * SR); t = tt(n); I = idx * np.exp(-t / 0.3)
    y = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t / tau)
    y += 0.25 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / (tau * 0.4))
    return ramp(y, 0.002, 0.06)


def lead_note(f, length, g=0.3):
    n = int((length + 0.12) * SR); t = tt(n)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.1) / 0.15, 0, 1)
    y = supersaw(f * vib, n, 7, 0.16) + 0.6 * stereo(square(f * vib, n))
    y = filt(y, 'lowpass', 5200)
    env = np.interp(t, [0, 0.006, 0.08, length, length + 0.12], [0, 1, 0.85, 0.8, 0])[:, None]
    return y * env * g


def bass_note(f, length=0.18):
    n = int((length + 0.02) * SR); t = tt(n)
    y = 0.6 * saw(f, n) + 0.4 * square(f, n)
    br, dk = filt(y, 'lowpass', 1600), filt(y, 'lowpass', 500)
    fe = np.exp(-t / 0.05); y = dk * (1 - fe) + br * fe
    y += 0.5 * np.sin(2 * np.pi * f * t) * (f < 120)
    env = np.interp(t, [0, 0.003, 0.05, length, length + 0.02], [0, 1, 0.8, 0.7, 0])
    return y * env


def whoosh(length=0.6, f0=450, f1=5500, peak=0.62, pan0=-0.8, pan1=0.8):
    n = int(length * SR); t = tt(n); u = t / length
    fc = np.where(u < peak, f0 * (f1 / f0) ** (u / peak), f1 * 0.35 ** ((u - peak) / (1 - peak)))
    y = svf_bp(rng.standard_normal(n), fc, 1.4)
    env = np.where(u < peak, (u / peak) ** 2, (1 - (u - peak) / (1 - peak)) ** 1.6)
    pan = pan0 + (pan1 - pan0) * u; a = (pan + 1) * np.pi / 4
    return ramp(np.stack([y * env * np.cos(a), y * env * np.sin(a)], 1) * np.sqrt(2), 0.005, 0.02)


def riser(length, f0=250, f1=7000):
    n = int(length * SR); t = tt(n); u = t / length
    y = svf_bp(rng.standard_normal(n), f0 * (f1 / f0) ** u, 2.0) * 0.7
    y += 0.16 * np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2.5 * u)) / SR)
    return ramp(y * u ** 2, 0.01, 0.02)


def kyuin(length=0.55, f0=650, f1=2900):
    """スロットの『キュイン』っぽい上昇音（オリジナル）"""
    n = int((length + 0.45) * SR); t = tt(n); u = np.clip(t / length, 0, 1)
    f = f0 * (f1 / f0) ** (u ** 0.7) * (1 + 0.012 * np.sin(2 * np.pi * 14 * t) * (t > length))
    y = np.zeros((n, 2))
    for det, pan in ((0, 0), (0.006, -0.7), (-0.006, 0.7)):
        ph = 2 * np.pi * np.cumsum(f * (1 + det)) / SR
        y += stereo(np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * square(f * (1 + det), n), pan)
    env = np.interp(t, [0, 0.03, length, length + 0.45], [0, 1, 1, 0])[:, None]
    return ramp(y * env * 0.33, 0.002, 0.05)


def tap():
    n = int(0.08 * SR); t = tt(n)
    y = np.sin(2 * np.pi * 1900 * t) * np.exp(-t / 0.008) + 0.6 * np.sin(2 * np.pi * 640 * t) * np.exp(-t / 0.02)
    return ramp(y, 0.0005, 0.01)


def thunder(length=1.4):
    n = int(length * SR); t = tt(n)
    crack = filt(rng.standard_normal(n), 'highpass', 1500) * np.exp(-t / 0.05) * (1 + 0.8 * (rng.random(n) > 0.995))
    rumble = filt(rng.standard_normal(n), 'lowpass', 180) * np.exp(-t / 0.55) * 3.0
    return ramp(np.stack([crack + rumble, filt(rng.standard_normal(n), 'highpass', 1500) * np.exp(-t / 0.05) + rumble], 1) * 0.5, 0.001, 0.05)


def reel_tick():
    n = int(0.012 * SR); t = tt(n)
    return ramp(filt(rng.standard_normal(n), 'bandpass', [2000, 5000]) * np.exp(-t / 0.0025) + 0.4 * np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.003), 0.0002, 0.002)


def reel_stop():
    n = int(0.5 * SR); t = tt(n)
    thump = np.sin(2 * np.pi * np.cumsum(60 + 110 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.07)
    click = filt(rng.standard_normal(n), 'highpass', 2500) * np.exp(-t / 0.004) * 0.6
    ring = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1180, .25), (2330, .18), (3710, .12))) * np.exp(-t / 0.12)
    return ramp(thump + click + ring, 0.0005, 0.05)


def beep(f, length=0.03):
    n = int(length * SR)
    return ramp(square(f, n) * 0.6, 0.001, 0.006)


# ================= 曲の流れ =================
DR, BS, CH, LD, FX, SEND = bus(), bus(), bus(), bus(), bus(), bus()
kicks = []
CHORD = {  # 和音（オフビートの刻み・パッド用）と、ベースの根音
    'Am': (['A3', 'C4', 'E4'], 'A1'), 'F': (['F3', 'A3', 'C4'], 'F1'), 'G': (['G3', 'B3', 'D4'], 'G1'), 'Em': (['E3', 'G3', 'B3'], 'E1'),
    'E': (['E3', 'G#3', 'B3'], 'E1'), 'Dm': (['D3', 'F3', 'A3'], 'D2'), 'A': (['A3', 'C#4', 'E4'], 'A1'),
}
PLAN = []
def seg(t0, t1, ch):
    PLAN.append((t0, t1, ch))
seg(0.0, 1.2, 'Am'); seg(1.2, 1.6, 'F'); seg(1.6, 2.4, 'G'); seg(2.4, 3.2, 'E')                                   # 前置き
seg(4.8, 5.6, 'G'); seg(5.6, 6.4, 'E')                                                                              # 題名のあと
seg(6.4, 8.0, 'Am'); seg(8.0, 9.6, 'F'); seg(9.6, 11.2, 'G'); seg(11.2, 12.8, 'Em'); seg(12.8, 14.4, 'E')         # 入れるだけ
seg(14.4, 16.0, 'F'); seg(16.0, 17.6, 'G'); seg(17.6, 19.2, 'Em'); seg(19.2, 20.8, 'Am')                           # 1発でゾーンまで判定
seg(20.8, 22.4, 'Am'); seg(22.4, 24.0, 'F'); seg(24.0, 25.6, 'G'); seg(25.6, 27.2, 'Am')                           # 買い目編集
seg(27.2, 28.8, 'F'); seg(28.8, 30.4, 'G'); seg(30.4, 32.0, 'Em'); seg(32.0, 33.6, 'Am')                           # 自分のデータ
seg(33.6, 34.4, 'F'); seg(34.4, 35.2, 'G'); seg(35.2, 36.0, 'Em'); seg(36.0, 36.8, 'Am'); seg(36.8, 37.6, 'F'); seg(37.6, 38.4, 'G')   # サビ
seg(38.4, 40.8, 'Am'); seg(40.8, 43.2, 'F'); seg(43.2, 45.6, 'G')                                                   # 買う馬・5重勝・収支


def chord_at(t):
    for a, b, c in PLAN:
        if a <= t < b - 1e-9:
            return c
    return None


def pad(notes, t0, length, g=0.16):
    n = int((length + 0.4) * SR); tt_ = tt(n); y = np.zeros((n, 2))
    for nt in notes:
        y += supersaw(hz(nt), n, 7, 0.2)
    y = filt(y, 'lowpass', 2600) * np.interp(tt_, [0, 0.05, length, length + 0.4], [0, 1, 0.9, 0])[:, None]
    put(CH, t0, y, g)


def groove(t0, t1, hats16=True, kick_on=True, clap=True, offhat=True, g=1.0):
    nb = int(round((t1 - t0) / BEAT))
    for j in range(nb):
        tb = t0 + BEAT * j
        if kick_on:
            kicks.append(tb); put(DR, tb, kick(), 0.95 * g)
        if clap and j % 2 == 1:
            put(DR, tb, snare(), 0.75 * g); put(SEND, tb, snare(), 0.18)
        if offhat:
            put(DR, tb + BEAT / 2, hat(True, 0.9), 0.28 * g, 0.2)
        if hats16:
            for k, d in enumerate((0.0, 0.1, 0.3)):
                put(DR, tb + d, hat(v=0.6 if k else 0.8), 0.22 * g, (-0.3, 0.3, -0.2)[k])


def coin_jingle(t0, g=0.11, notes=('A5', 'C#6', 'E6', 'A6', 'C#7', 'E7', 'A7')):
    """金貨がこぼれる音（ベルの連打・オリジナル）"""
    for i, nt in enumerate(notes):
        put(FX, t0 + 0.045 * i + rng.uniform(0, 0.01), bell(hz(nt), 0.7, 0.2, 1.4), g * (0.8 + 0.4 * rng.random()), rng.uniform(-0.6, 0.6))


def whoosh_at(tc, length=0.55, g=0.32, **kw):
    put(FX, tc - 0.62 * length, whoosh(length, **kw), g)


# ---- 前置き（0〜3.2）：いきなりドン「オッズを入れるだけの」→ 1.2「全く新しい」→ 1.6「競馬アプリ!!」（派手に） ----
put(DR, 0.0, kick(True), 1.0); put(DR, 0.0, boom(1.6), 0.9); put(DR, 0.0, crash(2.6, 0.9), 0.55); put(FX, 0.0, thunder(1.4), 0.6)
put(FX, 0.0, orch_hit(['A2', 'E3', 'A3', 'C4', 'E4']), 0.9); put(SEND, 0.0, orch_hit(['A3', 'C4', 'E4', 'A4']), 0.3)
put(FX, 0.05, kyuin(0.45, 800, 3000), 0.4)
put(FX, 0.2, riser(1.0, 300, 6000), 0.3)
put(FX, 1.2, orch_hit(['F2', 'C3', 'F3', 'A3', 'C4']), 0.8); put(DR, 1.2, crash(1.4, 0.5), 0.4); put(DR, 1.2, kick(True), 0.8)
put(FX, 1.6, orch_hit(['G2', 'D3', 'G3', 'B3', 'D4', 'G4']), 0.95); put(SEND, 1.6, orch_hit(['G3', 'B3', 'D4', 'G4']), 0.3)
put(DR, 1.6, kick(True), 1.0); put(DR, 1.6, boom(1.4), 0.8); put(DR, 1.6, crash(2.2, 0.8), 0.5); put(FX, 1.58, thunder(1.2), 0.5)
put(FX, 1.6, brass(['G3', 'B3', 'D4', 'G4'], 0.7, 0.5), 0.8)
for i, nt in enumerate(['B5', 'D6', 'G6', 'B6']):
    put(FX, 1.75 + 0.06 * i, bell(hz(nt), 0.8, 0.25, 1.2), 0.08, (-0.4, 0.4)[i % 2])
pad(['A2', 'E3', 'A3', 'C4', 'E4'], 0.0, 1.2, 0.1)
for k in range(8):   # ティンパニのロール → 題名へ
    put(DR, 2.4 + 0.1 * k, boom(0.4, 60, 30, 0.12), 0.25 + 0.06 * k)
for k in range(8):
    put(DR, 2.8 + 0.05 * k, snare(0.4 + 0.07 * k), 0.55, (-0.25, 0.25)[k % 2])
put(FX, 2.4, riser(0.8, 300, 8000), 0.4); put(DR, 3.2 - 1.2, crash(1.2, 0.4, rev=True), 0.4)

# ---- 題名（3.2〜6.4）：エンブレム → テンゲルⅢ(3.6) → 競馬 判定アプリ(4.4) → 新登場(4.8) ----
put(FX, 3.12, thunder(1.6), 0.55)
put(DR, 3.2, kick(True), 1.0); put(DR, 3.2, boom(1.6), 0.9); put(DR, 3.2, crash(2.6, 0.9), 0.55)
put(FX, 3.2, orch_hit(['A2', 'E3', 'A3', 'C4', 'E4']), 0.9)
put(DR, 3.6, kick(), 0.9); put(FX, 3.6, orch_hit(['A3', 'C4', 'E4', 'A4']), 0.85); put(DR, 3.6, crash(1.2, 0.4), 0.3)
put(FX, 4.4, whoosh(0.4, pan0=-0.9, pan1=0.6), 0.4); put(FX, 4.4, brass(['F3', 'A3', 'C4', 'F4'], 0.3), 0.8)
put(FX, 4.8, brass(['G3', 'B3', 'D4', 'G4'], 0.3), 0.8); put(FX, 4.8, bell(hz('B6'), 0.8, 0.25, 1.0), 0.12); put(FX, 4.84, bell(hz('E7'), 0.8, 0.25, 1.0), 0.1)
pad(['A2', 'E3', 'A3', 'C4', 'E4'], 3.2, 1.6, 0.11)
for k in range(8):   # ティンパニのロール → 本編へ
    put(DR, 5.6 + 0.1 * k, boom(0.4, 60, 30, 0.12), 0.25 + 0.06 * k)
for k in range(4):
    put(DR, 6.0 + 0.1 * k, snare(0.5 + 0.12 * k), 0.6)
put(FX, 5.6, riser(0.8, 250, 7000), 0.35)

# ---- 本編のリズム ----
groove(0.4, 2.4)
groove(4.8, 6.4, clap=False, g=0.75)
groove(6.4, 14.4)
groove(14.4, 20.8)
groove(20.8, 27.2)
groove(27.2, 32.8, offhat=False, g=0.9)
groove(32.8, 33.6, clap=False, offhat=False)
groove(33.6, 45.6)
for t0 in (7.6, 14.0, 20.4, 26.8, 45.2):   # 場面の前のフィル
    for k in range(4):
        put(DR, t0 + 0.1 * k, snare(0.4 + 0.15 * k), 0.55, (-0.3, 0.3)[k % 2])
for k in range(16):   # サビ前のロール
    put(DR, 32.8 + 0.05 * k, snare(0.25 + 0.05 * k), 0.6, (-0.25, 0.25)[k % 2])
put(FX, 32.8, riser(0.8, 300, 8000), 0.45)
put(DR, 33.6 - 1.2, crash(1.2, 0.4, rev=True), 0.4)

# ---- ベース（8分のオクターブ）とオフビートのコード ----
for a, b, ch in PLAN:
    notes, root = CHORD[ch]; f = hz(root)
    k = 0; t = a
    while t < b - 1e-6:
        put(BS, t, bass_note(f * (2 if k % 2 else 1), 0.17), 0.5)
        if k % 2 == 1:
            put(CH, t, stab(notes, 0.16, 3600 if 33.6 <= t < 45.6 else 2800), 0.55 if 33.6 <= t < 45.6 else 0.45)
        k += 1; t += BEAT / 2
# データの場面：電子音のアルペジオ
ARPN = {'F': ['F5', 'A5', 'C6', 'A5'], 'G': ['G5', 'B5', 'D6', 'B5'], 'Em': ['E5', 'G5', 'B5', 'G5'], 'Am': ['A5', 'C6', 'E6', 'C6']}
t = 27.2
while t < 33.6 - 1e-6:
    ch = chord_at(t); seq = ARPN[ch]; i = int(round((t - 27.2) / 0.1))
    n = int(0.09 * SR); put(LD, t, ramp(filt(square(hz(seq[i % 4]), n), 'lowpass', 4000) * np.exp(-tt(n) / 0.05), 0.001, 0.01), 0.1, (-0.5, 0.5)[i % 2])
    t += 0.1
# パッド（サビと、買う馬・5重勝・収支）
for a, b, ch in PLAN:
    if 33.6 <= a < 45.6:
        pad([n_ for n_ in CHORD[ch][0]] + [CHORD[ch][0][0][:-1] + str(int(CHORD[ch][0][0][-1]) + 1)], a, b - a, 0.14)

# ---- サビのメロディ（33.6〜38.4）：F→G→Em→Am→F→G ----
MEL = [('C6', 0, 2), ('A5', 2, 1), ('C6', 3, 1), ('D6', 4, 2), ('B5', 6, 1), ('D6', 7, 1),
       ('E6', 8, 1), ('D6', 9, 1), ('B5', 10, 1), ('G5', 11, 1), ('A5', 12, 3), ('E6', 15, 1),
       ('C6', 16, 1), ('A5', 17, 1), ('C6', 18, 1), ('F6', 19, 1), ('D6', 20, 1), ('B5', 21, 1), ('D6', 22, 1), ('G6', 23, 1)]
for nt, s_, d in MEL:
    put(LD, 33.6 + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02), 0.5)
    put(SEND, 33.6 + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02), 0.25)
# 買う馬・5重勝・収支（38.4〜45.6）：1つ2.4秒ずつ同じ形
RHY = [(0, 1), (1, 1), (2, 2), (4, 1), (5, 1), (6, 2), (8, 2), (10, 2)]
for base, ns in ((38.4, ['A5', 'C6', 'E6', 'D6', 'C6', 'B5', 'C6', 'E6']), (40.8, ['A5', 'C6', 'F6', 'E6', 'C6', 'A5', 'C6', 'F6']), (43.2, ['B5', 'D6', 'G6', 'F6', 'D6', 'B5', 'D6', 'G6'])):
    for nt, (s_, d) in zip(ns, RHY):
        put(LD, base + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02, 0.24), 0.42)

# ---- ヒット（大きな文字が出るところ） ----
HITS = [(8.0, ['F2', 'C3', 'F3', 'A3', 'C4']), (15.2, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), (25.6, ['A2', 'E3', 'A3', 'C4', 'E4']), (27.6, ['F2', 'C3', 'F3', 'A3', 'C4']),
        (33.6, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), (34.0, ['F3', 'A3', 'C4', 'F4']), (34.4, ['G2', 'D3', 'G3', 'B3', 'D4', 'G4']),
        (38.4, ['A2', 'E3', 'A3', 'C4', 'E4']), (40.8, ['F2', 'C3', 'F3', 'A3', 'C4']), (43.2, ['G2', 'D3', 'G3', 'B3', 'D4'])]
for t0, nts in HITS:
    put(FX, t0, orch_hit(nts), 0.75); put(SEND, t0, orch_hit(nts), 0.2)
for t0 in (6.4, 14.4, 20.8, 27.2, 33.6, 38.4):
    put(DR, t0, crash(2.2, 0.75), 0.42)
put(DR, 33.6, boom(1.4), 0.7); put(DR, 15.2, boom(1.0), 0.5)
put(FX, 15.2, kyuin(0.55, 700, 3000), 0.5)   # 「1発でゾーンまで判定!!」
for i, nt in enumerate(['C6', 'F6', 'A6', 'C7']):
    put(FX, 15.35 + 0.06 * i, bell(hz(nt), 0.8, 0.25, 1.2), 0.08, (-0.4, 0.4)[i % 2])
put(FX, 33.05, kyuin(0.55, 650, 2900), 0.55); put(FX, 33.6, kyuin(0.35, 1200, 3600), 0.35)

# ---- おわり（45.6〜50.4）：F → G → A（勝利の終わり方） ----
put(DR, 45.6, kick(True), 1.0); put(DR, 45.6, boom(1.6), 0.9); put(DR, 45.6, crash(2.6, 0.9), 0.55); put(FX, 45.56, thunder(1.4), 0.4)
put(FX, 45.6, orch_hit(['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), 0.9); put(FX, 45.6, brass(['F3', 'A3', 'C4', 'F4'], 0.34), 1.0)
put(DR, 46.0, kick(), 0.9); put(FX, 46.0, brass(['G3', 'B3', 'D4', 'G4'], 0.34), 1.0); put(FX, 46.0, orch_hit(['G2', 'D3', 'G3', 'B3']), 0.6)
put(DR, 46.4, kick(True), 1.0); put(DR, 46.4, crash(3.2, 1.2), 0.55); put(DR, 46.4, boom(1.8), 0.7)
put(FX, 46.4, brass(['A2', 'E3', 'A3', 'C#4', 'E4', 'A4'], 2.6, 0.55), 1.0); put(SEND, 46.4, brass(['A3', 'C#4', 'E4', 'A4'], 2.6, 0.4), 0.4)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 46.4, 3.6, 0.2)
for i, nt in enumerate(['A4', 'C#5', 'E5', 'A5', 'C#6', 'E6', 'A6']):
    put(LD, 46.5 + 0.07 * i, pluck(hz(nt), 0.5, 1.6, 0.25), 0.16, (-0.5, 0.5)[i % 2])
put(FX, 46.4, kyuin(0.4, 900, 3200), 0.45)
put(FX, 47.0, bell(hz('E6'), 2.2, 0.8, 2.0), 0.12, 0.3); put(FX, 47.03, bell(hz('A6'), 2.2, 0.8, 2.0), 0.1, -0.3)
for t0 in (45.6, 46.4):
    coin_jingle(t0, 0.08)

# ---- 50.4秒：注意書き → 50.4〜60.4は静かに（読む時間） ----
for k in range(12):
    put(DR, 49.8 + 0.05 * k, snare(0.3 + 0.05 * k), 0.5, (-0.25, 0.25)[k % 2])
put(FX, 49.6, riser(0.8, 300, 7000), 0.4); put(DR, 49.2, crash(1.2, 0.4, rev=True), 0.4)
put(DR, 50.4, kick(True), 0.85); put(DR, 50.4, boom(1.8), 0.7); put(DR, 50.4, crash(3.0, 1.1), 0.4); put(FX, 50.38, thunder(1.4), 0.35)
put(FX, 50.4, orch_hit(['A2', 'E3', 'A3', 'C#4', 'E4', 'A4']), 0.9); put(SEND, 50.4, orch_hit(['A3', 'C#4', 'E4', 'A4']), 0.3)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 50.5, 4.2, 0.1)
pad(['D3', 'F#3', 'A3', 'D4'], 54.8, 2.9, 0.09)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 57.8, 2.4, 0.09)
CALM = {50.5: ['A4', 'C#5', 'E5', 'A5'], 54.8: ['D5', 'F#5', 'A5', 'D6'], 57.8: ['A4', 'C#5', 'E5', 'A5']}
t = 50.9; k = 0
while t < 59.4:
    key = max(k_ for k_ in CALM if k_ <= t); seq = CALM[key]
    put(LD, t, pluck(hz(seq[k % 4]), 0.5, 1.4, 0.3), 0.055, (-0.5, 0.5)[k % 2]); t += 0.4; k += 1
for i in range(6):   # 注意書きが1つ出るたびに「ピン」
    put(FX, 50.8 + 0.5 * i, bell(hz('E6' if i % 2 == 0 else 'A6'), 0.8, 0.25, 1.0), 0.09, (-0.3, 0.3)[i % 2])

# ---- 効果音 ----
for tc, kw in ((6.4, {}), (14.4, {'pan0': .6, 'pan1': -.6}), (20.8, {'pan0': .7, 'pan1': -.7}), (25.7, {'pan0': .9, 'pan1': -.9}), (27.2, {}),
               (28.7, {'pan0': .5, 'pan1': -.5}), (32.0, {'pan0': .9, 'pan1': -.9}), (38.4, {}), (40.8, {'pan0': .7, 'pan1': -.7}), (43.2, {}), (45.6, {})):
    whoosh_at(tc, **kw)
for tc in (9.5, 11.2, 12.8, 16.4):   # 画面を動かすところ（小さく）
    whoosh_at(tc, 0.4, 0.16)
for t0 in (22.0, 23.3, 28.6, 30.0, 39.55):
    put(FX, t0, tap(), 0.45)
for t0, nt in ((8.2, 'A5'), (9.9, 'C6'), (11.6, 'E6'), (13.3, 'A5'), (16.8, 'E6'), (18.05, 'A5'), (19.3, 'C6'), (24.6, 'C6'), (26.0, 'E6'),
               (27.7, 'E6'), (29.4, 'A5'), (32.4, 'C6'), (34.9, 'E6'), (36.5, 'A5'), (39.8, 'A5'), (41.15, 'C6'), (43.55, 'E6')):
    put(FX, t0, bell(hz(nt), 1.0, 0.3, 1.0), 0.13, 0.15)
# データ上乗せ：カウンターの音と「＋走」
t = 30.1; k = 0
while t < 31.4:
    put(FX, t, beep(1000 * 2 ** (k / 40)), 0.07, (-0.3, 0.3)[k % 2]); t += 0.04; k += 1
for t0 in (30.2, 30.5, 30.8, 31.1):
    put(FX, t0, bell(hz('E6'), 0.6, 0.18, 1.0), 0.12, -0.3); put(FX, t0 + 0.06, bell(hz('B6'), 0.7, 0.22, 1.0), 0.12, 0.3)

# ================= サイドチェイン・ミックス =================
def duck(depth, tau=0.09):
    g = np.ones(N)
    for tk in kicks:
        i0 = int(tk * SR); n = min(int(0.35 * SR), N - i0); t_ = tt(n)
        g[i0:i0 + n] = np.minimum(g[i0:i0 + n], 1 - depth * np.exp(-t_ / tau) * (1 - np.exp(-t_ / 0.003)))
    return g[:, None]


BS *= duck(0.6); CH *= duck(0.45); LD *= duck(0.2)
for b_, g_ in ((CH, 0.25), (LD, 0.3), (FX, 0.2)):
    SEND += b_ * g_
ir_n = int(1.6 * SR); t_ = tt(ir_n)
ir = rng.standard_normal((ir_n, 2)) * np.exp(-t_ / 0.42)[:, None]
ir = filt(ir, 'lowpass', 6000); ir[:int(0.012 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
wet = np.stack([fftconvolve(SEND[:, c], ir[:, c])[:N] for c in range(2)], 1)

parts = {'drums': DR * 0.7, 'bass': BS * 1.9, 'chords': CH * 1.6, 'lead': LD * 2.6, 'fx': FX * 0.9, 'reverb': wet * 0.35}
mix = sum(parts.values())
_m = slice(int(6.4 * SR), int(45.6 * SR)); _tot = np.sqrt(np.mean(mix[_m] ** 2))
_c = slice(int(33.6 * SR), int(38.4 * SR)); _ctot = np.sqrt(np.mean(mix[_c] ** 2))
for k_, v_ in parts.items():
    print(f'  {k_:7s} {20 * np.log10(np.sqrt(np.mean(v_[_m] ** 2)) / _tot + 1e-12):6.1f} dB   サビ {20 * np.log10(np.sqrt(np.mean(v_[_c] ** 2)) / _ctot + 1e-12):6.1f} dB')
mix = filt(mix, 'highpass', 30)
fade = np.ones(N); i0 = int(58.8 * SR); fade[i0:] = 0.5 * (1 + np.cos(np.pi * np.linspace(0, 1, N - i0)))
mix *= fade[:, None]
fi = int(0.01 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
rms = np.sqrt(np.mean(mix[_m] ** 2)); mix *= float(os.environ.get('RMS', '0.2')) / rms
mix = np.tanh(mix * 1.2) / 1.2
mix *= 0.89 / np.max(np.abs(mix))
mix *= 10 ** (float(os.environ.get('GAIN_DB', '-2.4')) / 20)
wavfile.write(OUT, SR, (mix * 32767).astype(np.int16))
print('ok', OUT, 'peak', round(float(np.max(np.abs(mix))), 3))
