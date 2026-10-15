# CM第7弾のBGMと効果音：150BPM・Aマイナー・89.6秒・48kHzステレオ → bgm7.wav
# 画面（cm7.html）と同じ時刻で鳴らす。音色・前置き・題名・ミックスは bgm6.py と同じ。ポイント（もらう・減る・解放）・単勝5連予想・サブスクの音を足した
# 場面：前置き 0〜3.2・題名 3.2〜6.4・1500Pプレゼント 6.4〜9.6・例の画面 9.6〜15.2・ポイントで読み取り 15.2〜23.2・判定 23.2〜29.6・買い目編集 29.6〜36.0
#       Pカスタム（サビ）36.0〜42.4・マザーデータ 42.4〜50.4・買う馬 50.4〜52.8・単勝5連予想 52.8〜60.8・収支 60.8〜63.2・サブスク 63.2〜71.2・おわり 71.2〜77.6・注意書き 77.6〜89.6
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000; DUR = 89.6; N = int(SR * DUR)
BEAT = 0.4; BAR = 1.6
rng = np.random.default_rng(20261012)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bgm7.wav')
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
seg(6.4, 8.0, 'F'); seg(8.0, 9.6, 'G')                                                                              # 1500Pプレゼント
seg(9.6, 11.2, 'Am'); seg(11.2, 12.8, 'F'); seg(12.8, 14.4, 'G'); seg(14.4, 15.2, 'E')                            # 例の画面
seg(15.2, 16.8, 'F'); seg(16.8, 18.4, 'G'); seg(18.4, 20.0, 'Em'); seg(20.0, 21.6, 'Am'); seg(21.6, 23.2, 'E')   # ポイントで読み取り
seg(23.2, 24.8, 'F'); seg(24.8, 26.4, 'G'); seg(26.4, 28.0, 'Em'); seg(28.0, 29.6, 'Am')                           # 1発でゾーンまで判定
seg(29.6, 31.2, 'Am'); seg(31.2, 32.8, 'F'); seg(32.8, 34.4, 'G'); seg(34.4, 36.0, 'E')                            # 買い目編集
seg(36.0, 36.8, 'F'); seg(36.8, 37.6, 'G'); seg(37.6, 38.4, 'Em'); seg(38.4, 39.2, 'Am'); seg(39.2, 40.0, 'F'); seg(40.0, 40.8, 'G')   # サビ（Pカスタム）
seg(40.8, 41.6, 'Am'); seg(41.6, 42.4, 'E')
seg(42.4, 44.0, 'F'); seg(44.0, 45.6, 'G'); seg(45.6, 47.2, 'Em'); seg(47.2, 48.8, 'Am'); seg(48.8, 50.4, 'G')   # マザーデータ
seg(50.4, 52.8, 'Am')                                                                                               # 買う馬
seg(52.8, 54.4, 'F'); seg(54.4, 56.0, 'G'); seg(56.0, 57.6, 'Em'); seg(57.6, 59.2, 'Am'); seg(59.2, 60.8, 'F')   # 単勝5連予想
seg(60.8, 63.2, 'G')                                                                                                # 収支
seg(63.2, 64.8, 'F'); seg(64.8, 66.4, 'G'); seg(66.4, 68.0, 'Em'); seg(68.0, 69.6, 'Am'); seg(69.6, 71.2, 'E')   # サブスク


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
groove(6.4, 9.6, g=0.9)                      # 1500Pプレゼント
groove(9.6, 15.2)                            # 例の画面
groove(15.2, 23.2)                           # ポイントで読み取り
groove(23.2, 29.6)                           # 判定
groove(29.6, 35.2)                           # 買い目編集
groove(35.2, 36.0, clap=False, offhat=False)  # サビ前
groove(36.0, 42.4)                           # Pカスタム（サビ）
groove(42.4, 50.4, offhat=False, g=0.9)      # マザーデータ
groove(50.4, 71.2)                           # 買う馬・単勝5連予想・収支・サブスク
for t0 in (9.2, 14.8, 22.8, 29.2, 42.0, 50.0, 52.4, 60.4, 62.8, 70.8):   # 場面の前のフィル
    for k in range(4):
        put(DR, t0 + 0.1 * k, snare(0.4 + 0.15 * k), 0.55, (-0.3, 0.3)[k % 2])
for k in range(16):   # サビ前のロール
    put(DR, 35.2 + 0.05 * k, snare(0.25 + 0.05 * k), 0.6, (-0.25, 0.25)[k % 2])
put(FX, 35.2, riser(0.8, 300, 8000), 0.45)
put(DR, 36.0 - 1.2, crash(1.2, 0.4, rev=True), 0.4)

# ---- ベース（8分のオクターブ）とオフビートのコード ----
BRIGHT = lambda t: 36.0 <= t < 42.4 or 50.4 <= t < 71.2
for a, b, ch in PLAN:
    notes, root = CHORD[ch]; f = hz(root)
    k = 0; t = a
    while t < b - 1e-6:
        put(BS, t, bass_note(f * (2 if k % 2 else 1), 0.17), 0.5)
        if k % 2 == 1:
            put(CH, t, stab(notes, 0.16, 3600 if BRIGHT(t) else 2800), 0.55 if BRIGHT(t) else 0.45)
        k += 1; t += BEAT / 2
# マザーデータの場面：電子音のアルペジオ
ARPN = {'F': ['F5', 'A5', 'C6', 'A5'], 'G': ['G5', 'B5', 'D6', 'B5'], 'Em': ['E5', 'G5', 'B5', 'G5'], 'Am': ['A5', 'C6', 'E6', 'C6']}
t = 42.4
while t < 50.4 - 1e-6:
    ch = chord_at(t); seq = ARPN[ch]; i = int(round((t - 42.4) / 0.1))
    n = int(0.09 * SR); put(LD, t, ramp(filt(square(hz(seq[i % 4]), n), 'lowpass', 4000) * np.exp(-tt(n) / 0.05), 0.001, 0.01), 0.1, (-0.5, 0.5)[i % 2])
    t += 0.1
# パッド（サビと、買う馬〜サブスク）
for a, b, ch in PLAN:
    if 36.0 <= a < 42.4 or 50.4 <= a < 71.2:
        pad([n_ for n_ in CHORD[ch][0]] + [CHORD[ch][0][0][:-1] + str(int(CHORD[ch][0][0][-1]) + 1)], a, b - a, 0.14)

# ---- サビのメロディ（36.0〜40.8：F→G→Em→Am→F→G）と、しめ（40.8〜42.4：Am→E） ----
MEL = [('C6', 0, 2), ('A5', 2, 1), ('C6', 3, 1), ('D6', 4, 2), ('B5', 6, 1), ('D6', 7, 1),
       ('E6', 8, 1), ('D6', 9, 1), ('B5', 10, 1), ('G5', 11, 1), ('A5', 12, 3), ('E6', 15, 1),
       ('C6', 16, 1), ('A5', 17, 1), ('C6', 18, 1), ('F6', 19, 1), ('D6', 20, 1), ('B5', 21, 1), ('D6', 22, 1), ('G6', 23, 1),
       ('A6', 24, 2), ('E6', 26, 1), ('C6', 27, 1), ('B5', 28, 2), ('G#5', 30, 1), ('B5', 31, 1)]
for nt, s_, d in MEL:
    put(LD, 36.0 + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02), 0.5)
    put(SEND, 36.0 + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02), 0.25)
# 買う馬・単勝5連予想・収支：2.4秒の同じ形
RHY = [(0, 1), (1, 1), (2, 2), (4, 1), (5, 1), (6, 2), (8, 2), (10, 2)]
for base, ns in ((50.4, ['A5', 'C6', 'E6', 'D6', 'C6', 'B5', 'C6', 'E6']), (55.2, ['B5', 'D6', 'G6', 'F6', 'D6', 'B5', 'D6', 'G6']),
                 (57.6, ['A5', 'C6', 'E6', 'D6', 'C6', 'B5', 'C6', 'E6']), (60.8, ['B5', 'D6', 'G6', 'F6', 'D6', 'B5', 'D6', 'G6'])):
    for nt, (s_, d) in zip(ns, RHY):
        put(LD, base + 0.2 * s_, lead_note(hz(nt), 0.2 * d - 0.02, 0.24), 0.42)

# ---- ヒット（大きな文字が出るところ） ----
HITS = [(6.4, ['F2', 'C3', 'F3', 'A3', 'C4']), (7.2, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), (10.0, ['A2', 'E3', 'A3', 'C4', 'E4']), (15.6, ['F2', 'C3', 'F3', 'A3', 'C4']),
        (24.0, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), (34.4, ['E2', 'B2', 'E3', 'G#3', 'B3']),
        (36.0, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), (36.4, ['F3', 'A3', 'C4', 'F4']), (36.8, ['G2', 'D3', 'G3', 'B3', 'D4', 'G4']),
        (42.8, ['F2', 'C3', 'F3', 'A3', 'C4']), (50.4, ['A2', 'E3', 'A3', 'C4', 'E4']), (52.8, ['F2', 'C3', 'F3', 'A3', 'C4']), (60.8, ['G2', 'D3', 'G3', 'B3', 'D4']),
        (63.6, ['F2', 'C3', 'F3', 'A3', 'C4', 'F4'])]
for t0, nts in HITS:
    put(FX, t0, orch_hit(nts), 0.75); put(SEND, t0, orch_hit(nts), 0.2)
for t0 in (6.4, 9.6, 15.2, 23.2, 29.6, 36.0, 42.4, 50.4, 52.8, 60.8, 63.2):
    put(DR, t0, crash(2.2, 0.75), 0.42)
put(DR, 36.0, boom(1.4), 0.7); put(DR, 24.0, boom(1.0), 0.5)
put(FX, 24.0, kyuin(0.55, 700, 3000), 0.5)   # 「1発でゾーンまで判定!!」
for i, nt in enumerate(['C6', 'F6', 'A6', 'C7']):
    put(FX, 24.15 + 0.06 * i, bell(hz(nt), 0.8, 0.25, 1.2), 0.08, (-0.4, 0.4)[i % 2])
put(FX, 35.45, kyuin(0.55, 650, 2900), 0.55); put(FX, 36.0, kyuin(0.35, 1200, 3600), 0.35)

# ---- 1500Pプレゼント（6.4〜9.6）：コインが回って出る → 「1500P」でドン → 「プレゼント!!」 ----
put(FX, 6.45, kyuin(0.5, 700, 3200), 0.45); coin_jingle(6.6, 0.1)
put(DR, 7.2, kick(True), 1.0); put(DR, 7.2, boom(1.6), 0.85); put(DR, 7.2, crash(2.4, 0.9), 0.5); put(FX, 7.18, thunder(1.2), 0.4)
coin_jingle(7.2, 0.12); coin_jingle(7.25, 0.09, ('E6', 'A6', 'C#7', 'E7', 'A7', 'C#8'))
put(FX, 7.6, brass(['F3', 'A3', 'C4', 'F4'], 0.5, 0.5), 0.9); coin_jingle(7.62, 0.1)
for i in range(14):   # 降ってくる金貨の「チャリン」
    t0 = 7.9 + 0.11 * i + rng.uniform(0, 0.05)
    put(FX, t0, bell(hz(('A6', 'C#7', 'E7', 'A7')[i % 4]), 0.5, 0.15, 1.3), 0.05, rng.uniform(-0.7, 0.7))
put(FX, 8.8, riser(0.8, 300, 7000), 0.3)

# ---- ポイント：減る音（−200P・−500P）・解放の音 ----
def pay_sfx(t0, g=1.0):   # 「ピロリン↓」＋小さなチャリン
    for i, nt in enumerate(('E6', 'C6', 'A5')):
        put(FX, t0 + 0.07 * i, bell(hz(nt), 0.6, 0.18, 1.1), 0.12 * g, (0.3, 0, -0.3)[i])
    coin_jingle(t0 + 0.02, 0.05 * g, ('A6', 'E7', 'A7'))


def open_sfx(t0, g=1.0):   # 「解放!!」：上がる音＋明るい和音
    put(FX, t0 - 0.05, kyuin(0.3, 900, 2600), 0.28 * g)
    for i, nt in enumerate(('A5', 'C#6', 'E6', 'A6', 'C#7')):
        put(FX, t0 + 0.05 * i, bell(hz(nt), 0.8, 0.25, 1.2), 0.09 * g, (-0.4, 0.4)[i % 2])


pay_sfx(16.5); pay_sfx(38.4); pay_sfx(39.6)
open_sfx(38.45); open_sfx(39.65)
# マザーデータの解放（44.0：−15,000P）は大きく
pay_sfx(44.0, 1.4); put(FX, 44.05, orch_hit(['G2', 'D3', 'G3', 'B3', 'D4', 'G4']), 0.6); put(DR, 44.05, boom(1.2), 0.5); open_sfx(44.1, 1.4); coin_jingle(44.15, 0.1)

# ---- 読み取り（16.1 吸い込まれる → 16.65〜17.75 読み取り中 → 17.9 自動で入った） ----
put(FX, 16.1, kyuin(0.36, 900, 2600), 0.2); put(FX, 16.48, bell(hz('A6'), 0.6, 0.18, 1.0), 0.08, 0.2)
t = 16.7; k = 0
while t < 17.75:
    put(FX, t, beep((1320, 1760, 1480, 1980)[k % 4], 0.03), 0.035, (-0.3, 0.3)[k % 2]); t += 0.1; k += 1
for i, nt in enumerate(['A5', 'C#6', 'E6', 'A6']):
    put(FX, 17.9 + 0.05 * i, bell(hz(nt), 0.9, 0.28, 1.2), 0.07, (-0.4, 0.4)[i % 2])
put(DR, 17.9, crash(1.6, 0.5), 0.22)
put(DR, 10.0, boom(1.0), 0.45)

# ---- 単勝5連予想：5つの画面が入るたびに「ピコン」（音が上がる）→ 合計 → ランダムのシャッフル ----
for i, nt in enumerate(('A5', 'C6', 'E6', 'A6', 'C7')):
    put(FX, 53.15 + 0.4 * i, bell(hz(nt), 0.7, 0.22, 1.2), 0.12, (-0.5, -0.25, 0, 0.25, 0.5)[i]); put(FX, 53.15 + 0.4 * i, tap(), 0.25)
for i, nt in enumerate(['A5', 'C#6', 'E6', 'A6']):
    put(FX, 55.2 + 0.05 * i, bell(hz(nt), 0.9, 0.28, 1.2), 0.07, (-0.4, 0.4)[i % 2])
t = 57.65; k = 0
while t < 57.95:
    put(FX, t, reel_tick(), 0.35, (-0.3, 0.3)[k % 2]); t += 0.03; k += 1
put(FX, 57.97, reel_stop(), 0.25)

# ---- データ上乗せ：カウンターの音と「＋走」 ----
t = 46.1; k = 0
while t < 47.4:
    put(FX, t, beep(1000 * 2 ** (k / 40)), 0.07, (-0.3, 0.3)[k % 2]); t += 0.04; k += 1
for t0 in (46.2, 46.5, 46.8, 47.1):
    put(FX, t0, bell(hz('E6'), 0.6, 0.18, 1.0), 0.12, -0.3); put(FX, t0 + 0.06, bell(hz('B6'), 0.7, 0.22, 1.0), 0.12, 0.3)

# ---- サブスク：金貨 ----
coin_jingle(63.25, 0.09); coin_jingle(63.6, 0.08)

# ---- おわり（71.2〜77.6）：F → G → A（勝利の終わり方）・紹介特典 ----
put(DR, 71.2, kick(True), 1.0); put(DR, 71.2, boom(1.6), 0.9); put(DR, 71.2, crash(2.6, 0.9), 0.55); put(FX, 71.16, thunder(1.4), 0.4)
put(FX, 71.2, orch_hit(['F2', 'C3', 'F3', 'A3', 'C4', 'F4']), 0.9); put(FX, 71.2, brass(['F3', 'A3', 'C4', 'F4'], 0.34), 1.0)
put(DR, 71.6, kick(), 0.9); put(FX, 71.6, brass(['G3', 'B3', 'D4', 'G4'], 0.34), 1.0); put(FX, 71.6, orch_hit(['G2', 'D3', 'G3', 'B3']), 0.6)
put(DR, 72.0, kick(True), 1.0); put(DR, 72.0, crash(3.2, 1.2), 0.55); put(DR, 72.0, boom(1.8), 0.7)
put(FX, 72.0, brass(['A2', 'E3', 'A3', 'C#4', 'E4', 'A4'], 2.6, 0.55), 1.0); put(SEND, 72.0, brass(['A3', 'C#4', 'E4', 'A4'], 2.6, 0.4), 0.4)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 72.0, 5.4, 0.2)
for i, nt in enumerate(['A4', 'C#5', 'E5', 'A5', 'C#6', 'E6', 'A6']):
    put(LD, 72.1 + 0.07 * i, pluck(hz(nt), 0.5, 1.6, 0.25), 0.16, (-0.5, 0.5)[i % 2])
put(FX, 72.0, kyuin(0.4, 900, 3200), 0.45)
put(FX, 72.6, bell(hz('E6'), 2.2, 0.8, 2.0), 0.12, 0.3); put(FX, 72.63, bell(hz('A6'), 2.2, 0.8, 2.0), 0.1, -0.3)
for t0 in (71.2, 72.0):
    coin_jingle(t0, 0.08)
coin_jingle(73.6, 0.1); put(FX, 73.6, bell(hz('C#7'), 1.2, 0.4, 1.4), 0.08)   # 紹介特典
t = 74.0; k = 0
while t < 77.2:   # しずかに続ける
    put(LD, t, pluck(hz(('A5', 'C#6', 'E6', 'C#6')[k % 4]), 0.5, 1.4, 0.3), 0.06, (-0.5, 0.5)[k % 2]); t += 0.4; k += 1

# ---- 77.6秒：注意書き → 77.6〜89.6は静かに（読む時間） ----
for k in range(12):
    put(DR, 77.0 + 0.05 * k, snare(0.3 + 0.05 * k), 0.5, (-0.25, 0.25)[k % 2])
put(FX, 76.8, riser(0.8, 300, 7000), 0.4); put(DR, 76.4, crash(1.2, 0.4, rev=True), 0.4)
put(DR, 77.6, kick(True), 0.85); put(DR, 77.6, boom(1.8), 0.7); put(DR, 77.6, crash(3.0, 1.1), 0.4); put(FX, 77.58, thunder(1.4), 0.35)
put(FX, 77.6, orch_hit(['A2', 'E3', 'A3', 'C#4', 'E4', 'A4']), 0.9); put(SEND, 77.6, orch_hit(['A3', 'C#4', 'E4', 'A4']), 0.3)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 77.7, 4.4, 0.1)
pad(['D3', 'F#3', 'A3', 'D4'], 82.2, 3.0, 0.09)
pad(['A2', 'E3', 'A3', 'C#4', 'E4'], 85.3, 4.3, 0.09)
CALM = {77.7: ['A4', 'C#5', 'E5', 'A5'], 82.2: ['D5', 'F#5', 'A5', 'D6'], 85.3: ['A4', 'C#5', 'E5', 'A5']}
t = 78.1; k = 0
while t < 88.6:
    key = max(k_ for k_ in CALM if k_ <= t); seq = CALM[key]
    put(LD, t, pluck(hz(seq[k % 4]), 0.5, 1.4, 0.3), 0.055, (-0.5, 0.5)[k % 2]); t += 0.4; k += 1
for i in range(7):   # 注意書きが1つ出るたびに「ピン」
    put(FX, 78.0 + 0.5 * i, bell(hz('E6' if i % 2 == 0 else 'A6'), 0.8, 0.25, 1.0), 0.09, (-0.3, 0.3)[i % 2])

# ---- 効果音 ----
for tc, kw in ((6.4, {}), (9.6, {'pan0': .6, 'pan1': -.6}), (15.2, {}), (23.2, {'pan0': .6, 'pan1': -.6}), (29.6, {'pan0': .7, 'pan1': -.7}), (34.5, {'pan0': .9, 'pan1': -.9}),
               (36.0, {}), (42.4, {'pan0': .5, 'pan1': -.5}), (48.0, {'pan0': .9, 'pan1': -.9}), (50.4, {}), (52.8, {'pan0': .7, 'pan1': -.7}), (60.8, {}), (63.2, {'pan0': .6, 'pan1': -.6}), (71.2, {})):
    whoosh_at(tc, **kw)
for tc in (10.5, 12.1, 13.7, 15.75, 18.0, 19.65, 21.45, 25.3, 44.9, 58.5, 65.35):   # 画面を動かすところ（小さく）
    whoosh_at(tc, 0.4, 0.16)
for t0 in (16.0, 30.8, 32.1, 37.7, 38.3, 39.05, 39.5, 43.8, 44.45, 46.0, 51.55, 57.6):
    put(FX, t0, tap(), 0.45)
for t0, nt in ((10.8, 'A5'), (10.95, 'C6'), (11.1, 'E6'), (12.05, 'C6'), (13.65, 'E6'), (16.7, 'E6'), (18.45, 'A5'), (20.0, 'C6'), (21.8, 'E6'),
               (25.6, 'E6'), (26.85, 'A5'), (28.1, 'C6'), (33.4, 'C6'), (34.8, 'E6'), (36.6, 'E6'), (40.6, 'A6'), (42.9, 'E6'), (45.3, 'A5'), (48.4, 'C6'),
               (50.75, 'A5'), (51.8, 'C6'), (55.4, 'E6'), (56.9, 'A5'), (58.9, 'C6'), (61.15, 'E6'), (63.8, 'A5'), (65.7, 'C6'), (67.7, 'E6'), (69.5, 'A6')):
    put(FX, t0, bell(hz(nt), 1.0, 0.3, 1.0), 0.13, 0.15)

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
_m = slice(int(6.4 * SR), int(71.2 * SR)); _tot = np.sqrt(np.mean(mix[_m] ** 2))
_c = slice(int(36.0 * SR), int(40.8 * SR)); _ctot = np.sqrt(np.mean(mix[_c] ** 2))
for k_, v_ in parts.items():
    print(f'  {k_:7s} {20 * np.log10(np.sqrt(np.mean(v_[_m] ** 2)) / _tot + 1e-12):6.1f} dB   サビ {20 * np.log10(np.sqrt(np.mean(v_[_c] ** 2)) / _ctot + 1e-12):6.1f} dB')
mix = filt(mix, 'highpass', 30)
fade = np.ones(N); i0 = int(88.0 * SR); fade[i0:] = 0.5 * (1 + np.cos(np.pi * np.linspace(0, 1, N - i0)))
mix *= fade[:, None]
fi = int(0.01 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
rms = np.sqrt(np.mean(mix[_m] ** 2)); mix *= float(os.environ.get('RMS', '0.2')) / rms
mix = np.tanh(mix * 1.2) / 1.2
mix *= 0.89 / np.max(np.abs(mix))
mix *= 10 ** (float(os.environ.get('GAIN_DB', '-2.4')) / 20)
wavfile.write(OUT, SR, (mix * 32767).astype(np.int16))
print('ok', OUT, 'peak', round(float(np.max(np.abs(mix))), 3))
