# 馬カードバトルの BGM：酒場の 夜（第4.179版・まさちゃん 2026/11/16 17:00「BGMにバイオリン消して、木がきしむ音、足跡を追加して！ 酒場っぽく後ろが、声とかでガヤガヤしてる感じも表現できたら入れてほしい！」）
#   第4.178版（14:43「カーボーイの時代っぽい雰囲気、ゆったりバイオリンの音と、夜の虫の音で作成して」）の バイオリンの 曲は git の 履歴に ある（バイオリンと うしろの 弦の 音は 消した）
#   ぜんぶ 計算で 作る（録音・よその 曲・よその 音は 使わない）
#   python3 kisekae/cb_bgm.py                 … ios/cb_assets/cb_bgm.m4a（アプリに 入れる 形：ステレオ 44.1kHz・AAC）
#   python3 kisekae/cb_bgm.py wav <出す wav>   … 聞いて・測って 確かめる 用（くり返す 1回り だけ）
#
#   場面：夜の 酒場の 前の 木の ポーチ（1回り 約80.5秒：前の 曲と 同じ 長さ＝LOOP）
#   まさちゃん 17:11「人の声ガヤガヤだけ消してみて！」→ VOICES＝False（話し声・笑い声は 入れない。グラスの チンは のこす：ドアが 開いて いる 間は 少し はっきり）。
#     ガヤガヤの 作り方（voice・crowd）は のこして ある：VOICES＝True に すると もどる
#     ・（VOICES＝True の とき だけ）酒場の 中の ガヤガヤ：16人の 話し声（声の もと＋口の 形の ひびき〈母音〉・1秒に 4〜6この 音節・高さが 上下・くじで えらぶ ので ことばには ならない）・ときどき 笑い声・グラスの チン。
#       部屋の ひびき → かべの むこうで こもる。スイングドアが 開いて いる 間 だけ 声が 少し 大きく・はっきり なる
#     ・足音：木の 床を ブーツで 歩く（かかと → つま先）＋ 拍車の チャリッ。左から 来て 酒場に 入る・出て きて 右へ 遠ざかる・右から 左へ 通りすぎる・右から 来て 入る
#     ・木の きしみ：歩く 足の 下の 床板・ゆりいす（行って 帰って）・スイングドア（ギィ…パタン パタン）
#     ・外の 夜：虫の 声（コオロギ・鈴虫 など：第4.178版と 同じ。ずっと 鳴る 細い 声は 小さく）・夜の 空気（とても 小さい 風の 音）
#   くり返し：1回り（LOOP 秒）は 頭と しっぽが つながる ように 作る（しっぽの 音・ひびきの のこりは 頭へ 回す）。
#     アプリ用の ファイルは 1回りの 前と うしろに PRE 秒（0.5秒）ずつ 同じ 音の つづきを 入れる → アプリは まん中の 1回り だけを くり返す（cb/cb_app.js の BGM：つなぎ目で 音が とばない）
import os, subprocess, sys, tempfile
import numpy as np
from scipy import signal, fft as sfft
from scipy.io import wavfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
FILE = 'cb_bgm.m4a'
SR = 44100
TAU = 2 * np.pi
LOOP = 34 * 3 * 60.0 / 76      # 1回り（秒）：cb/cb_app.js の BGM.len と 同じ（34 * 3 * 60 / 76：第4.178版の 曲の 長さ の まま）
PRE = 0.5                       # アプリ用の ファイルの 前と うしろの つづき（秒）：cb/cb_app.js の BGM.pre と 同じ
PEAK = 0.50                     # ファイルの 山（アプリは BGM.vol 倍で 鳴らす）
VOICES = False                  # 酒場の 中の 話し声（ガヤガヤ）を 入れるか（まさちゃん 17:11「人の声ガヤガヤだけ消してみて！」→ 入れない）
NL = int(round(LOOP * SR))


def files():
    """アプリに 入れる 名前（build_ios.py・テストが 使う）"""
    return [FILE]


# ---------------- 小さな 道具 ----------------
def lp1(x, fc):
    b, a = signal.butter(1, fc / (SR / 2), 'low'); return signal.lfilter(b, a, x)


# ---------------- 夜の 虫 ----------------
def tone(f, amp, harm=(1.0, 0.035, 0.0)):
    f = np.asarray(f, np.float64); ph = TAU * np.cumsum(f) / SR; y = np.zeros(len(f))
    for k, h in enumerate(harm, 1):
        if h: y += h * np.sin(k * ph)
    return y * amp


def env_ar(n, att, rel):
    e = np.ones(n); a = max(1, min(int(att * SR), n // 2)); r = max(1, min(int(rel * SR), n - a))
    e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a)); e[n - r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return e


def korogi(rng, f0):
    """コオロギ「コロコロコロ リー」：細かい つぶの つながり → 少し のばす"""
    out = []; rate = rng.uniform(21, 27); npl = int(rng.uniform(0.5, 1.0) * rate)
    for i in range(npl):
        n = int(0.6 / rate * SR); t = np.linspace(0, 1, n)
        out += [tone(np.full(n, f0 * (1 + 0.008 * np.sin(i * 1.3))), np.sin(np.pi * t) ** 1.5 * (0.55 + 0.45 * min(1, (i + 1) / 4))), np.zeros(int(0.4 / rate * SR))]
    n = int(rng.uniform(0.28, 0.45) * SR); t = np.arange(n) / SR
    out.append(tone(np.full(n, f0 * 0.992), env_ar(n, 0.02, 0.14) * (0.75 + 0.25 * np.sin(TAU * 44 * t))))
    return np.concatenate(out)


def suzumushi(rng, f0):
    """鈴虫「リーン」：やわらかい つぶが 5〜8こ つながって 鈴の ように ひびく"""
    out = []; npl = int(rng.integers(5, 9))
    for i in range(npl):
        n = int(rng.uniform(0.050, 0.064) * SR); t = np.linspace(0, 1, n)
        f = f0 * (1 - 0.010 * i / npl) * (1 + 0.002 * np.sin(TAU * 3 * t))
        out += [tone(f, np.sin(np.pi * t) ** 0.8 * (0.6 + 0.4 * np.sin(np.pi * (i + 0.5) / npl)), (1.0, 0.03, 0.0)), np.zeros(int(0.005 * SR))]
    return np.concatenate(out)


def chirp3(rng, f0):
    """遠くの 小さな 虫「リッ リッ リッ」"""
    out = []
    for i in range(int(rng.integers(2, 5))):
        n = int(0.05 * SR); t = np.linspace(0, 1, n)
        out += [tone(np.full(n, f0), np.sin(np.pi * t) ** 1.2 * (0.75 + 0.25 * np.sin(TAU * 60 * t * 0.05))), np.zeros(int(rng.uniform(0.16, 0.22) * SR))]
    return np.concatenate(out)


def place(buf, y, at, pan, gain):
    """ステレオの 入れ物（2×NL）に 音を 置く。はみ出した ぶんは 頭へ 回す（くり返せる）"""
    i = int(at * SR) % NL; gl = gain * np.sqrt((1 - pan) / 2); gr = gain * np.sqrt((1 + pan) / 2)
    j = 0
    while j < len(y):
        m = min(len(y) - j, NL - i)
        buf[0, i:i + m] += gl * y[j:j + m]; buf[1, i:i + m] += gr * y[j:j + m]
        j += m; i = 0


def insects(seed, tree=1.0):
    """tree＝木の 上の 細い 声（ずっと 鳴って いる 高い 声）の 大きさ（第4.179版：酒場の 夜では 0.45）"""
    rng = np.random.default_rng(seed); buf = np.zeros((2, NL))
    # コオロギ 3びき（高さ・場所・間の ちがう）：2〜5秒に 1回
    for f0, pan, g, gap in ((4150, -0.65, 0.050, (2.4, 4.6)), (4480, 0.55, 0.042, (3.0, 5.6)), (3920, 0.15, 0.030, (4.5, 8.0))):
        t = rng.uniform(0.2, 2.0)
        while t < LOOP - 0.05:
            place(buf, lp1(korogi(rng, f0 * rng.uniform(0.992, 1.008)), 6500), t, pan, g * rng.uniform(0.75, 1.0)); t += rng.uniform(*gap)
    # 鈴虫 2ひき：リーン リーン（2〜3回 つづけて → 休む）
    for f0, pan, g in ((4320, 0.8, 0.045), (4610, -0.35, 0.036)):
        t = rng.uniform(1.0, 5.0)
        while t < LOOP - 0.05:
            for r in range(int(rng.integers(2, 4))):
                place(buf, suzumushi(rng, f0 * rng.uniform(0.996, 1.004)), t, pan, g * rng.uniform(0.8, 1.0)); t += rng.uniform(0.62, 0.78)
            t += rng.uniform(4.0, 8.5)
    # 遠くの 小さな 虫
    for f0, pan, g in ((5200, -0.9, 0.016), (5650, 0.9, 0.014)):
        t = rng.uniform(0.5, 3.0)
        while t < LOOP - 0.05:
            place(buf, chirp3(rng, f0), t, pan, g); t += rng.uniform(1.6, 3.4)
    # 木の 上の 細い 声（ずっと 鳴って いる・ゆっくり 大きく なったり 小さく なったり：1回りで もとに もどる）
    tt = np.arange(NL) / SR
    for f0, pan, g, cyc, ph in ((6350, -0.4, 0.0075, 3, 0.3), (6900, 0.5, 0.0060, 4, 1.9)):
        rate = 46.0
        pulse = lp1((np.mod(tt * rate, 1.0) < 0.5).astype(float), 160)
        sw = np.clip(0.55 + 0.45 * np.sin(TAU * cyc * tt / LOOP + ph), 0, 1)
        y = np.sin(TAU * f0 * tt) * pulse * sw
        buf[0] += tree * g * np.sqrt((1 - pan) / 2) * y; buf[1] += tree * g * np.sqrt((1 + pan) / 2) * y
    return buf


def night_air(seed):
    """夜の 空気：とても 小さい 風の 音（くり返せる：しっぽの つづきを 頭に 重ねて つなぐ・強弱は 1回りで もとに もどる 波）"""
    rng = np.random.default_rng(seed); out = np.zeros((2, NL)); tt = np.arange(NL) / SR; k = SR // 2
    fin = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    for ch in range(2):
        w = signal.lfilter(*signal.butter(2, [70 / (SR / 2), 520 / (SR / 2)], 'band'), rng.standard_normal(NL + 2 * k))[k:]      # はじめの k は フィルターの 立ち上がり（すてる）
        x = w[:NL].copy(); x[:k] = x[:k] * fin + w[NL:NL + k] * (1 - fin)       # 頭の k サンプル：しっぽの つづき（w[NL…]）から いまの 音へ うつる ＝ おわり → 頭が つながる
        g = 0.6 + 0.25 * np.sin(TAU * 2 * tt / LOOP + rng.uniform(0, TAU)) + 0.15 * np.sin(TAU * 5 * tt / LOOP + rng.uniform(0, TAU))
        out[ch] = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * g * 0.0045
    return out


# ---------------- ひびき（小さな 広間・外の 夜）----------------
def reverb_ir(seed, rt=1.7, pre=0.022):
    rng = np.random.default_rng(seed); n = int((rt * 1.15 + pre) * SR); t = np.arange(n) / SR
    ir = np.zeros((2, n))
    for ch in range(2):
        x = rng.standard_normal(n) * np.exp(-6.9 * np.maximum(0, t - pre) / rt) * (t >= pre)
        x = signal.lfilter(*signal.butter(1, 5200 / (SR / 2), 'low'), x)
        x = signal.lfilter(*signal.butter(1, 220 / (SR / 2), 'high'), x)
        for d, g in ((0.011, 0.5), (0.019, 0.38), (0.031, 0.3), (0.043, 0.22)):      # はじめの はね返り
            i = int((d + 0.003 * ch) * SR); x[i] += g * (1 if (ch + int(d * 1000)) % 2 else -1) * 6
        ir[ch] = x / np.sqrt(np.sum(x ** 2))
    return ir


def wet(st, ir, mix):
    """くり返せる ひびき：1回りを 3回 ならべて ひびかせ、まん中の 1回りを 取る（前の 回りの のこりが 頭に 入る）"""
    out = np.zeros_like(st)
    for ch in range(2):
        x = np.tile(st[ch], 3)
        y = signal.fftconvolve(x, ir[ch])[:len(x)]
        out[ch] = st[ch] + mix * y[NL:2 * NL]
    return out


def pan2(y, pan):
    return np.stack([y * np.sqrt((1 - pan) / 2), y * np.sqrt((1 + pan) / 2)])



# ---------------- 酒場の 夜の 音 ----------------
def fold(y):
    """1回りより 長い 音の しっぽを 頭に 重ねる（くり返して つながる）"""
    out = np.zeros(NL)
    for i in range(0, len(y), NL):
        seg = y[i:i + NL]; out[:len(seg)] += seg
    return out


def fold2(y):
    return np.stack([fold(y[0]), fold(y[1])])


# ---------------- ガヤガヤ（話し声）----------------
#   1人 ずつ：声帯の 音（のこぎり波を まるめた もの・高さが 上下する）＋ 息の 音 → 口の 形（母音の ひびき：F1〜F4）の フィルター。
#   音節（1秒に 4〜6こ）を つなげて 話す → 休む → 話す。母音・子音・高さは くじ（ことばには ならない）
VOW = {'a': (730, 1090, 2440), 'i': (300, 2200, 2950), 'u': (340, 1250, 2300), 'e': (480, 1850, 2550), 'o': (520, 900, 2450), 'x': (500, 1450, 2500)}
VK = list(VOW)
FR, HOP, NF = 1024, 256, 2048


def voice(rng, female, laughs=(), level=1.0):
    T = LOOP + 4.0; L = int(T * SR); nfr = L // HOP + 1
    f0b = rng.uniform(175, 245) if female else rng.uniform(88, 138)
    fsc = (1.16 if female else 1.0) * rng.uniform(0.96, 1.05)
    syl = []      # (t0, dur, vowel, cons, amp, f0a, f0b, laugh)
    t = rng.uniform(0.0, 4.0)
    while t < LOOP:
        ud = rng.uniform(0.7, 3.4); rate = rng.uniform(4.2, 6.2); ns = max(2, int(ud * rate))
        tt = t; pitch = f0b * rng.uniform(0.95, 1.12); fall = rng.uniform(0.75, 0.95); up = rng.random() < 0.25
        for k in range(ns):
            d = rng.uniform(0.11, 0.25) * (1.25 if k == ns - 1 else 1.0)
            prog = k / max(1, ns - 1)
            fa = pitch * (1 + (fall - 1) * prog) * rng.uniform(0.95, 1.06); fb = fa * rng.uniform(0.94, 1.04)
            if up and k == ns - 1: fb = fa * 1.25
            syl.append((tt, d, VOW[VK[rng.integers(0, 6)]], int(rng.choice([0, 1, 1, 2])), rng.uniform(0.55, 1.0) * (1.0 if k < ns - 1 else 0.75), fa, fb, 0))
            tt += d
        t = tt + rng.uniform(0.45, 4.2)
    for tl in laughs:      # 笑い声「ハハハハ」：高めの 声から 下がる・息が まじる
        syl = [s for s in syl if not (tl - 0.25 < s[0] < tl + 1.7)]
        n = int(rng.integers(4, 8)); tt = tl; f = f0b * rng.uniform(1.45, 1.7)
        for k in range(n):
            d = rng.uniform(0.12, 0.17); syl.append((tt, d, VOW['a'], 1, (1.0 - 0.09 * k) * 1.15, f, f * 0.93, 1)); f *= rng.uniform(0.92, 0.97); tt += d + rng.uniform(0.0, 0.03)
    syl.sort(key=lambda s: s[0])
    # コマ ごとの 決めごと
    amp = np.zeros(nfr); v = np.ones(nfr); f0 = np.full(nfr, f0b); F = np.tile(np.array(VOW['x'], float), (nfr, 1)); br = np.zeros(nfr)
    prev = VOW['x']
    for (t0, d, vw, cons, a, fa, fb, lg) in syl:
        i0 = int(t0 * SR / HOP); i1 = max(i0 + 1, int((t0 + d) * SR / HOP))
        if i0 >= nfr: break
        i1 = min(i1, nfr); u = (np.arange(i0, i1) - i0) / max(1, i1 - i0)
        c = (0.28 if lg else 0.22) if cons else 0.0
        e = np.clip(np.minimum(u / 0.15, 1.0), 0, 1) * np.where(u > 0.72, 0.35 + 0.65 * (1 - u) / 0.28, 1.0)
        amp[i0:i1] = np.maximum(amp[i0:i1], a * e)
        w = np.clip((u - c) / 0.4, 0, 1)[:, None]
        F[i0:i1] = np.array(prev, float)[None, :] * (1 - w) + np.array(vw, float)[None, :] * w
        if cons == 1: v[i0:i1] = np.where(u < c, 0.0, 1.0)
        elif cons == 2: amp[i0:i1] *= np.where(u < c, 0.55, 1.0); F[i0:i1, 0] = np.where(u < c, 260, F[i0:i1, 0])
        if lg: br[i0:i1] = 0.35
        f0[i0:i1] = fa + (fb - fa) * u
        prev = vw
    k3 = np.ones(3) / 3
    amp = np.convolve(amp, k3, 'same'); v = np.convolve(v, k3, 'same'); br = np.convolve(br, k3, 'same')
    # 1サンプル ずつの 音の もと
    tc = np.arange(nfr) * HOP; ts = np.arange(L)
    f0s = np.interp(ts, tc, f0) * (1 + 0.012 * np.sin(TAU * rng.uniform(4.5, 6.0) * ts / SR))
    ph = np.cumsum(f0s) / SR; saw = 2 * (ph % 1.0) - 1
    saw = signal.lfilter(*signal.butter(1, min(0.45, f0b * 1.6 / (SR / 2)), 'low'), saw) * 6
    vs = np.interp(ts, tc, v); bs = np.interp(ts, tc, br); am = np.interp(ts, tc, amp)
    nz = rng.standard_normal(L) * 0.55
    src = (saw * vs * (1 - bs) + nz * (1 - vs + bs * 0.8)) * am
    # 口の 形の フィルター（コマ ごと：窓を かけて 2048点で 計算 → 足し合わせる）
    fr = np.arange(NF // 2 + 1) * SR / NF
    out = np.zeros(L + NF)
    win = np.hanning(FR).astype(np.float32)
    for c0 in range(0, nfr, 2048):      # まとめて（メモリを ひかえめに）
        c1 = min(nfr, c0 + 2048); idx = np.arange(c0, c1)
        st = idx * HOP
        seg = np.zeros((c1 - c0, FR), np.float32)
        for j, s0 in enumerate(st):
            a = src[s0:s0 + FR]; seg[j, :len(a)] = a
        S = sfft.rfft(seg * win, n=NF, axis=1)
        Hm = np.ones((c1 - c0, len(fr)), np.float32)
        Fk = F[c0:c1] * fsc
        for k, (Fv, Bw) in enumerate(((Fk[:, 0], 90.0), (Fk[:, 1], 110.0), (Fk[:, 2], 150.0), (np.full(c1 - c0, 3400.0 * fsc), 220.0))):
            Fv = Fv[:, None].astype(np.float32)
            Hm *= 1.0 / np.sqrt((1 - (fr[None, :] / Fv) ** 2) ** 2 + (fr[None, :] * Bw / Fv ** 2) ** 2)
        y = sfft.irfft(S * Hm, n=NF, axis=1)
        for j, s0 in enumerate(st):
            out[s0:s0 + NF] += y[j]
    out = out[:L] / 2.0
    return fold(out) * level


def crowd(seed, n=16, laughs=None):
    """酒場の 中の ガヤガヤ（ステレオ・2×NL）。laughs＝{声の 番号: [笑う 時刻…]}"""
    rng = np.random.default_rng(seed); buf = np.zeros((2, NL)); laughs = laughs or {}
    for i in range(n):
        female = rng.random() < 0.3
        y = voice(np.random.default_rng(seed * 100 + i), female, laughs.get(i, ()), 1.0)
        y = y / (np.sqrt(np.mean(y ** 2)) + 1e-12) * rng.uniform(0.45, 1.0)
        pan = rng.uniform(-0.85, 0.85)
        buf[0] += y * np.sqrt((1 - pan) / 2); buf[1] += y * np.sqrt((1 + pan) / 2)
    return buf


# ---------------- 木の 音 ----------------
def modal_ir(freqs, decays, amps, dur=0.25, rng=None, spread=0.0):
    t = np.arange(int(dur * SR)) / SR; ir = np.zeros(len(t))
    for f, d, a in zip(freqs, decays, amps):
        if rng is not None and spread: f *= 1 + spread * rng.uniform(-1, 1)
        ir += a * np.sin(TAU * f * t + (rng.uniform(0, TAU) if rng is not None else 0)) * np.exp(-t / d)
    return ir


def creak(rng, dur, r0, r1, freqs, decays, amps, jitter=0.3, bump=0.3, a_env=None):
    """木が きしむ：こすれて 止まって を くり返す（1秒に r 回の こまかい「コッ」）→ 木の ひびき を 鳴らす"""
    n = int((dur + 0.1) * SR); imp = np.zeros(n); t = 0.0
    while t < dur:
        u = t / dur; r = r0 + (r1 - r0) * u + bump * (r0 + r1) / 2 * np.sin(np.pi * u)
        e = (np.sin(np.pi * u) ** 0.6) if a_env is None else a_env(u)
        imp[int(t * SR)] += e * rng.uniform(0.55, 1.0)
        t += (1.0 / r) * (1 + jitter * rng.uniform(-1, 1))
    ir = modal_ir(freqs, decays, amps, 0.12, rng, 0.04)
    y = signal.fftconvolve(imp, ir)[:n]
    return y


def floor_creak(rng, dur=None):
    return creak(rng, dur or rng.uniform(0.25, 0.6), rng.uniform(22, 30), rng.uniform(35, 48), [300, 610, 960, 1470, 2250], [0.022, 0.016, 0.012, 0.009, 0.006], [1.0, 0.75, 0.5, 0.32, 0.18])


def hinge_creak(rng, dur=None):
    return creak(rng, dur or rng.uniform(0.55, 0.85), rng.uniform(70, 95), rng.uniform(130, 170), [690, 1380, 2080, 3010], [0.018, 0.012, 0.009, 0.006], [1.0, 0.6, 0.4, 0.22], jitter=0.18, bump=0.2)


def chair_creak(rng, fwd):
    d = rng.uniform(0.32, 0.46)
    return creak(rng, d, *( (36, 54) if fwd else (52, 34) ), [420, 860, 1330, 1920], [0.02, 0.014, 0.01, 0.007], [1.0, 0.7, 0.45, 0.25], jitter=0.25, bump=0.15)


def knock(rng, freqs, decays, amps, exc_ms=4.0, dur=0.25):
    """木を たたく 音（短い 雑音で 木の ひびきを 鳴らす）"""
    ne = max(8, int(exc_ms / 1000 * SR)); exc = rng.standard_normal(ne) * np.exp(-np.arange(ne) / (ne / 3))
    return signal.fftconvolve(exc, modal_ir(freqs, decays, amps, dur, rng, 0.03))


def boot_step(rng, toe=False):
    """ブーツの 一歩：かかと（どん＋こつ）→ つま先（小さく）"""
    n = int(0.35 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    s = 0.45 if toe else 1.0
    ft = rng.uniform(92, 128)
    y += s * 0.9 * np.sin(TAU * ft * t) * np.exp(-t / 0.05) * (1 - np.exp(-t / 0.002))
    y += s * 0.35 * np.sin(TAU * ft * 2.2 * t) * np.exp(-t / 0.03)
    k = knock(rng, [360, 730, 1160, 1680, 2500], [0.045, 0.03, 0.022, 0.016, 0.01], [1.0, 0.85, 0.6, 0.4, 0.22], exc_ms=3.0 if not toe else 2.0, dur=0.2)
    y[:len(k)] += s * 0.55 * k[:n]
    c = rng.standard_normal(int(0.002 * SR)); c = signal.lfilter(*signal.butter(2, 3000 / (SR / 2), 'high'), c)
    y[:len(c)] += s * 0.25 * c
    return y


def spur(rng, a=1.0):
    """拍車の チャリッ（小さな 金具が 2〜3回 ふれる）"""
    n = int(0.4 * SR); y = np.zeros(n)
    base = rng.uniform(2900, 3500)
    for h in range(int(rng.integers(2, 4))):
        at = int(rng.uniform(0, 0.05) * SR); ir = modal_ir([base * r for r in (1.0, 1.47, 2.09, 2.76)], [0.075, 0.055, 0.04, 0.03], [1.0, 0.6, 0.4, 0.25], 0.3, rng, 0.02)
        ex = rng.standard_normal(40) * np.exp(-np.arange(40) / 8)
        z = signal.fftconvolve(ex, ir)[:n - at] * rng.uniform(0.4, 1.0)
        y[at:at + len(z)] += z
    return y * a


def walk(rng, buf, t0, steps, gap, pan0, pan1, g0, g1, creak_p=0.3, spurs=True):
    """木の 床の 上を 歩く（t0 から steps 歩・gap 秒 ごと。場所 pan0→pan1・大きさ g0→g1）"""
    t = t0
    for i in range(steps):
        u = i / max(1, steps - 1); pan = pan0 + (pan1 - pan0) * u; g = g0 + (g1 - g0) * u
        place(buf, boot_step(rng), t, pan, g)
        place(buf, boot_step(rng, True), t + rng.uniform(0.07, 0.11), pan, g)
        if spurs: place(buf, spur(rng), t + rng.uniform(0.01, 0.03), pan, g * 0.10)
        if rng.random() < creak_p: place(buf, floor_creak(rng), t + rng.uniform(0.03, 0.08), pan, g * 0.38)
        t += gap * rng.uniform(0.94, 1.06)
    return t


def door(rng, buf, t0, pan, g, flaps=3):
    """スイングドア：ギィ…（開く）→ パタン パタン（もどって ゆれる）"""
    place(buf, hinge_creak(rng), t0, pan, g * 0.30)
    tf = t0 + rng.uniform(1.6, 2.4); a = 1.0
    for k in range(flaps):
        place(buf, knock(rng, [170, 410, 880, 1500], [0.05, 0.035, 0.02, 0.012], [1.0, 0.7, 0.4, 0.2], exc_ms=6.0, dur=0.3), tf, pan + 0.05 * (k % 2), g * 0.45 * a)
        if k == 0: place(buf, hinge_creak(rng, 0.3), tf - 0.25, pan, g * 0.16)
        tf += rng.uniform(0.32, 0.42) * (0.85 ** k); a *= 0.55
    return tf


def glass(rng):
    """グラスの チン（2つの グラス）"""
    n = int(0.9 * SR); y = np.zeros(n)
    for j, f in enumerate((rng.uniform(1900, 2400), rng.uniform(2300, 2800))):
        ir = modal_ir([f * r for r in (1.0, 2.32, 4.25, 6.63)], [0.45, 0.28, 0.16, 0.09], [1.0, 0.45, 0.22, 0.1], 0.9, rng, 0.01)
        ex = rng.standard_normal(30) * np.exp(-np.arange(30) / 6)
        z = signal.fftconvolve(ex, ir)[:n]; y += z * (1.0 if j == 0 else 0.8)
    return y


# ---------------- 場面の 予定（秒）----------------
DOORS = [11.6, 27.0, 70.3]                                     # スイングドアが 開く 時刻
OPEN = [(11.6, 14.2), (27.0, 29.8), (70.3, 73.0)]             # ドアが 開いて いる 間（中の 声が 少し 大きく・はっきり）
LAUGH = {5: [12.4], 0: [43.8], 3: [44.1], 7: [44.35], 2: [71.1], 9: [71.35], 11: [58.6]}      # 笑う 人と 時刻（44秒 ごろ・71秒 ごろは 何人か いっしょに）
GLASS = [8.2, 13.1, 22.5, 33.9, 45.0, 56.7, 71.8, 78.4]       # グラスの チン


def loop_filt(x, fc, order=2):
    """くり返せる ローパス：3回 ならべて かけて まん中を 取る"""
    b, a = signal.butter(order, fc / (SR / 2), 'low')
    return np.stack([signal.lfilter(b, a, np.tile(x[c], 3))[NL:2 * NL] for c in range(2)])


def render(nv=16, voices=None):
    """くり返す 1回り（ステレオ・2×NL）。voices＝話し声（ガヤガヤ）を 入れるか（決めなければ VOICES）"""
    voices = VOICES if voices is None else voices
    rng = np.random.default_rng(31178)
    # 酒場の 中：（ガヤガヤ ＋ 笑い声）＋ グラス → 部屋の ひびき → かべの むこう（こもる）／ドアが 開いて いる 間は はっきり
    if voices: cr = crowd(9178, nv, LAUGH); crr = np.sqrt(np.mean(cr ** 2))
    else: cr = np.zeros((2, NL)); crr = 1.0
    for tg in GLASS:
        gz = glass(rng); place(cr, gz / np.abs(gz).max(), tg, rng.uniform(-0.6, 0.6), 1.3 * crr)
    cr = wet(cr, reverb_ir(81, rt=1.0, pre=0.012), 0.35)
    closed = loop_filt(cr, 1700); opened = loop_filt(cr, 4800) * 1.9
    tt = np.arange(NL) / SR; w = np.zeros(NL)
    for a, b in OPEN:
        for k in (-1, 0, 1):
            w = np.maximum(w, np.clip(np.minimum((tt - (a + k * LOOP)) / 0.35, ((b + k * LOOP) - tt) / 0.6), 0, 1))
    swell = 0.9 + 0.1 * np.sin(TAU * 3 * tt / LOOP + 0.7)
    inside = (closed * (1 - w) + opened * w) * swell
    # 外の ポーチ：足音・きしみ・ドア・ゆりいす
    fo = np.zeros((2, NL))
    walk(rng, fo, 5.0, 9, 0.66, -0.9, -0.08, 0.32, 0.9)                 # 左から 来て 酒場に 入る
    door(rng, fo, DOORS[0], 0.0, 0.85)
    door(rng, fo, DOORS[1], 0.05, 0.85)                                 # 出て くる
    walk(rng, fo, 28.3, 10, 0.68, 0.02, 0.85, 0.85, 0.28)               # 右へ 歩いて 遠ざかる
    place(fo, floor_creak(rng, 0.7), 36.5, 0.4, 0.35)
    te = walk(rng, fo, 47.0, 7, 0.7, 0.9, 0.05, 0.3, 0.85)              # 右から 左へ 通りすぎる
    walk(rng, fo, te, 7, 0.7, -0.05, -0.9, 0.85, 0.3)
    walk(rng, fo, 64.0, 9, 0.66, 0.85, 0.05, 0.28, 0.85)                # 右から 来て 入る
    door(rng, fo, DOORS[2], 0.0, 0.85)
    place(fo, floor_creak(rng, 0.5), 77.2, -0.3, 0.3)
    for (ta, tb, pan, g) in ((17.5, 40.0, -0.55, 0.55), (57.5, 69.0, 0.6, 0.42)):      # ゆりいす：ゆっくり ゆれる（行って 帰って）
        t = ta; fwd = True
        while t < tb:
            place(fo, chair_creak(rng, fwd), t, pan, g * rng.uniform(0.85, 1.0)); t += rng.uniform(0.85, 1.0); fwd = not fwd
    fo = wet(fo, reverb_ir(82, rt=0.55, pre=0.008), 0.18)
    ins = wet(insects(4178, tree=0.45), reverb_ir(78, rt=1.1), 0.10)
    air = night_air(5178)
    rms = lambda x: float(np.sqrt(np.mean(x ** 2)))
    k_in = 0.040 / rms(closed * swell) if voices else 0.040      # 話し声なし：グラスは 話し声 ありの ときと ほぼ 同じ 大きさ（話し声の RMS を 1 と した 時の 1.3倍 → 0.040 倍）
    mix = inside * k_in + ins * (0.020 / rms(ins)) + fo * (0.42 / np.abs(fo).max()) + air * 3.0
    mix = mix - mix.mean(axis=1, keepdims=True)
    return mix * (PEAK / np.abs(mix).max())


def with_margins(x):
    """アプリ用：1回りの 前と うしろに PRE 秒の つづき（前＝1回りの おわり・うしろ＝1回りの 頭）"""
    k = int(round(PRE * SR))
    return np.concatenate([x[:, -k:], x, x[:, :k]], axis=1)


def save_wav(x, path):
    wavfile.write(path, SR, (np.clip(x.T, -1, 1) * 32767).astype(np.int16))


if __name__ == '__main__':
    x = render()
    if len(sys.argv) > 2 and sys.argv[1] == 'wav':
        save_wav(x, sys.argv[2]); print('wav', sys.argv[2], round(x.shape[1] / SR, 3), '秒')
    else:
        os.makedirs(OUT, exist_ok=True); tmp = tempfile.mkdtemp(); w = os.path.join(tmp, 'cb_bgm.wav'); o = os.path.join(OUT, FILE)
        save_wav(with_margins(x), w)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-ac', '2', '-c:a', 'aac', '-b:a', '112k', '-movflags', '+faststart', o], check=True)
        print(f'できた：{FILE} {os.path.getsize(o)} B・1回り {LOOP:.3f}秒（前後に {PRE}秒ずつ）・山 {np.abs(x).max():.2f}・ふつうの 大きさ（RMS）{np.sqrt(np.mean(x ** 2)):.4f} → {OUT}')
