# 馬カードバトルの BGM（第4.178版・まさちゃん 2026/11/16 14:43「テンゲルカードバトルにBGMをつける。(カーボーイの時代っぽい雰囲気、ゆったりバイオリンの音と、夜の虫の音で作成して)」）
#   ぜんぶ 計算で 作る（録音・よその 曲・よその 音は 使わない）：ふし・和音・リズムは 姫が 新しく 作った もの
#   python3 kisekae/cb_bgm.py                 … ios/cb_assets/cb_bgm.m4a（アプリに 入れる 形：ステレオ 44.1kHz・AAC）
#   python3 kisekae/cb_bgm.py wav <出す wav>   … 聞いて・測って 確かめる 用（くり返す 1回り だけ）
#
#   曲：ト長調・3拍子（ゆったりした ワルツ）・1分に 76拍・34小節（虫の 声 だけの 2小節 → A 8小節 → A' 8小節 → B 8小節 → A'' 8小節）＝ 1回り 約80.5秒（LOOP）
#     ・バイオリン（フィドル）の ような 音 2本：ふし（まん中より 少し 左）と、うしろで 2つの 音を のばす 2本目（右・小さく）
#       音の 作り方：弓で ひく 弦の ような ぎざぎざの 波（倍音を 40本 まで 足す）を、楽器の 胴の ひびき（280・460・560・1000・2600Hz あたりの 山）で 色づけ。
#       ビブラート（1秒に 5〜6回・のばす 音 だけ・おくれて かかる）で 倍音が ひびきの 山を 行き来する ＝ 弦らしい ゆれ。音の うつりは なめらかに（すべる）・弓の こすれる 音を 少し
#     ・夜の 虫の 声：コオロギ（コロコロ リー）・鈴虫（リーン）・遠くの 小さな 虫（リッ リッ）・木の 上の 細い 声。右にも 左にも いる。ふしが 休む 所でも 鳴いて いる
#     ・夜の 空気（とても 小さい 風の 音）
#   くり返し：1回り（LOOP 秒）は 頭と しっぽが つながる ように 作る（ひびきの のこり・虫の 声も ぐるっと 回す）。
#     アプリ用の ファイルは 1回りの 前と うしろに PRE 秒（0.5秒）ずつ 同じ 音の つづきを 入れる → アプリは まん中の 1回り だけを くり返す（cb/cb_app.js の BGM：つなぎ目で 音が とばない）
import os, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
FILE = 'cb_bgm.m4a'
SR = 44100
TAU = 2 * np.pi
BPM = 76; BEAT = 60.0 / BPM; BARS = 34
LOOP = BARS * 3 * BEAT          # 1回り（秒）：cb/cb_app.js の BGM.len と 同じ（34 * 3 * 60 / 76）
PRE = 0.5                       # アプリ用の ファイルの 前と うしろの つづき（秒）：cb/cb_app.js の BGM.pre と 同じ
PEAK = 0.50                     # ファイルの 山（アプリは BGM.vol 倍で 鳴らす）
NL = int(round(LOOP * SR))


def files():
    """アプリに 入れる 名前（build_ios.py・テストが 使う）"""
    return [FILE]


# ---------------- 音の 高さ ----------------
_SEMI = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    """'G4'・'F#4' → Hz（A4＝440）"""
    n = _SEMI[name[0]]; r = name[1:]
    if r[0] == '#': n += 1; r = r[1:]
    elif r[0] == 'b': n -= 1; r = r[1:]
    return 440.0 * 2 ** ((n - 9) / 12 + int(r) - 4)


# ---------------- ふし（姫が 作った もの）：(音, 拍の 数[, しるし])。None＝休み。しるし：'b'＝弓を かえす（少し 切る）・'g'＝前に かざりの 音（1つ 上から すべる）----------------
#   和音：A   | G | G | C | G | Em | C | D | D |    A'  | G | G | C | G | Em | C | D | G |
#         B   | C | C | G | G | Am | D | G | D |    A'' | G | G | C | G | Em | C | D | G |
LEAD = [
    # はじめの 2小節：ふしは 休み（虫の 声と、2小節目から そっと 入る 2本目 だけ）
    (None, 6),
    # A
    ('B4', 2), ('D5', 1),            ('E5', 1.5), ('D5', 0.5), ('B4', 1, 'b'),      ('C5', 1), ('E5', 1), ('G5', 1),      ('D5', 2.6), (None, 0.4),
    ('E5', 1, 'g'), ('G5', 1), ('E5', 1),      ('C5', 2, 'b'), ('A4', 1),      ('B4', 1), ('A4', 1), ('F#4', 1),      ('A4', 2.4), (None, 0.6),
    # A'
    ('B4', 2), ('D5', 1),            ('E5', 1.5), ('D5', 0.5), ('B4', 1, 'b'),      ('C5', 1), ('E5', 1), ('G5', 1),      ('D5', 2), ('B4', 1, 'b'),
    ('E5', 2, 'g'), ('D5', 1),       ('C5', 1, 'b'), ('B4', 1), ('A4', 1),      ('A4', 2, 'b'), ('F#4', 1),      ('G4', 2.4), (None, 0.6),
    # B
    ('E5', 1), ('G5', 2),            ('E5', 1, 'b'), ('C5', 1), ('E5', 1),      ('D5', 2, 'b'), ('B4', 1),      ('G4', 1, 'b'), ('B4', 1), ('D5', 1),
    ('C5', 2, 'g'), ('E5', 1),       ('D5', 1, 'b'), ('C5', 1), ('A4', 1),      ('B4', 2, 'b'), ('G4', 1),      ('A4', 2.4), (None, 0.6),
    # A''
    ('B4', 2), ('D5', 1),            ('E5', 1.5), ('D5', 0.5), ('B4', 1, 'b'),      ('C5', 1), ('E5', 1), ('G5', 1),      ('G5', 2, 'b'), ('E5', 1),
    ('D5', 1, 'b'), ('E5', 1), ('D5', 1),      ('C5', 2, 'b'), ('A4', 1),      ('B4', 1), ('A4', 1.5), ('F#4', 0.5),      ('G4', 2.3), (None, 0.7),
]
# 2本目（うしろで のばす 2つの 音）：小節ごとに (下の 音, 上の 音)。None＝休み（ふしだけ）
PAD = [
    None, ('G3', 'D4'),
    ('G3', 'D4'), ('G3', 'D4'), ('G3', 'E4'), ('G3', 'D4'), ('G3', 'E4'), ('G3', 'E4'), ('A3', 'F#4'), ('A3', 'D4'),
    ('G3', 'D4'), ('G3', 'D4'), ('G3', 'E4'), ('G3', 'D4'), ('B3', 'E4'), ('C4', 'E4'), ('A3', 'F#4'), ('G3', 'D4'),
    ('C4', 'E4'), ('C4', 'G4'), ('B3', 'D4'), ('G3', 'D4'), ('A3', 'E4'), ('A3', 'F#4'), ('G3', 'D4'), ('A3', 'F#4'),
    ('G3', 'D4'), ('G3', 'D4'), ('G3', 'E4'), ('G3', 'D4'), ('B3', 'E4'), ('C4', 'E4'), ('A3', 'F#4'), ('G3', 'D4'),
]
# 小節ごとの 強弱（0〜1）：フレーズの 山へ 向かって ふくらみ、おわりで おさまる（ふし）／2本目は いつも ひかえめ（小節の まん中で 少し ふくらむ）
DYN = [0.0, 0.0,
       0.70, 0.78, 0.92, 0.84, 0.86, 0.80, 0.72, 0.62,
       0.72, 0.80, 0.94, 0.86, 0.90, 0.80, 0.70, 0.60,
       0.80, 0.90, 0.84, 0.76, 0.86, 0.80, 0.72, 0.62,
       0.74, 0.84, 0.98, 1.00, 0.88, 0.78, 0.68, 0.56]
assert abs(sum(n[1] for n in LEAD) - BARS * 3) < 1e-9, sum(n[1] for n in LEAD)
assert len(PAD) == BARS and len(DYN) == BARS


def dyn_line(vals, n):
    """小節ごとの 強弱を なめらかな 線（n サンプル）に"""
    bar = 3 * BEAT; t = np.arange(n) / SR / bar - 0.5
    v = np.asarray(list(vals) + [vals[0]], float)
    return np.interp(np.clip(t, 0, len(vals) - 0.001), np.arange(len(v)), v)


# ---------------- バイオリンの ような 音 ----------------
def smooth01(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def lp1(x, fc):
    b, a = signal.butter(1, fc / (SR / 2), 'low'); return signal.lfilter(b, a, x)


# 胴の ひびき（dB）：周波数の 表（対数の 目もり）を 作って おいて、倍音ごとに 引く
_FT = np.geomspace(60, 20000, 2048)


def _body_db(f):
    pk = [(275, 5.0, 0.11), (460, 7.0, 0.09), (560, 5.0, 0.08), (990, 3.5, 0.20), (1750, 1.5, 0.25), (2600, 5.5, 0.30), (3500, 2.0, 0.22)]      # (まん中 Hz, 山の 高さ dB, 幅 オクターブ)
    g = np.zeros_like(f)
    for fc, db, wd in pk:
        g += db * np.exp(-0.5 * (np.log2(f / fc) / wd) ** 2)
    g += -18.0 * np.maximum(0, np.log2(190.0 / f))      # 190Hz より 下は 出にくい
    g += -18.0 * np.maximum(0, np.log2(f / 3900.0))     # 3.9kHz より 上は なだらかに 落ちる
    return g


_BODY = 10 ** (_body_db(_FT) / 20)
_LOGFT = np.log(_FT)


def bowed(f0, amp, bright, seed):
    """周波数の 線 f0（Hz・1サンプルごと：ビブラート こみ）と 大きさ amp（0〜1）→ 弓で ひいた 弦の ような 音。bright＝明るさ（0〜1 の 線：大きい ほど 高い 倍音が 出る）"""
    n = len(f0); rng = np.random.default_rng(seed)
    ph = TAU * np.cumsum(f0) / SR
    y = np.zeros(n)
    fmax = float(f0.max()); kmax = int(min(40, np.floor(0.45 * SR / max(fmax, 1.0))))
    roll = 1.50 - 0.28 * bright                         # 倍音の へり方（大きい 音ほど 明るい：やわらかい 音に する ため 少し 多めに へらす）
    logf = np.log(np.maximum(f0, 30.0))
    for k in range(1, kmax + 1):
        g = np.interp(logf + np.log(k), _LOGFT, _BODY)  # その 倍音が いま いる 周波数での 胴の ひびき（ビブラートで ゆれる）
        y += np.sin(k * ph + 0.37 * k) * g / k ** roll * (0.92 if k % 2 == 0 else 1.0)
    y *= amp
    # 弓の こすれる 音（息の ような ざらつき）：大きさに ついて いく
    hiss = signal.lfilter(*signal.butter(2, [2200 / (SR / 2), 7000 / (SR / 2)], 'band'), rng.standard_normal(n))
    y += 0.022 * hiss * amp * (0.6 + 0.4 * bright)
    return y


def line(notes, seed, vib=0.0075, port=0.055, level=1.0, dyn=None, swell=0.0):
    """ふしを 1本の 線（周波数・大きさ）に して 音に する。くり返せる ように、おわりの のこり（すっと 消える ぶん）は 頭へ 回す"""
    rng = np.random.default_rng(seed)
    tail = int(0.5 * SR); n = NL + tail
    f = np.zeros(n); a = np.zeros(n); vd = np.zeros(n); br = np.zeros(n); dip = np.ones(n)
    t = 0.0; prev = None; items = list(notes)
    for j, it in enumerate(items):
        name, beats = it[0], it[1]; flag = it[2] if len(it) > 2 else ''
        d = beats * BEAT; i0 = int(round(t * SR)); i1 = int(round((t + d) * SR)); m = i1 - i0
        if name is not None:
            fz = hz(name); tt = np.arange(m) / SR
            f[i0:i1] = fz
            if 'g' in flag:                               # かざり：1つ 上の 音から すべり おりる（0.09秒）
                g = int(0.09 * SR); f[i0:i0 + g] = fz * 2 ** (2 / 12)
            # 大きさ：休みの あとは 0 から 立ち上がる（0.11秒）・つづけて ひく 音は 少し へこむ だけ → のばす 間に 少し ふくらむ
            e = smooth01(tt / 0.11) if prev is None else 0.80 + 0.20 * smooth01(tt / 0.06)
            e = e * (0.82 + 0.18 * smooth01(tt / max(0.35, d * 0.55)))
            a[i0:i1] = e
            if prev is not None and 'b' in flag:          # 弓を かえす：音の 頭で 少し へこませる
                w = int(0.06 * SR); x = np.arange(-w, w) / w; lo = max(0, i0 - w); hi_ = min(n, i0 + w)
                dip[lo:hi_] = np.minimum(dip[lo:hi_], 1 - 0.5 * np.exp(-4 * x[lo - (i0 - w):hi_ - (i0 - w)] ** 2))
            nxt = items[j + 1][0] if j + 1 < len(items) else None
            if nxt is None:                               # 休みの 前・さいごの 音：すっと 消える（0.16秒。高さは そのまま）
                r = min(int(0.16 * SR), n - i1)
                if r > 0: a[i1:i1 + r] = e[-1] * (0.5 + 0.5 * np.cos(np.pi * np.arange(r) / r))
            # ビブラートの 深さ：のばす 音 だけ・0.28秒 おくれて かかる
            vd[i0:i1] = vib * smooth01((tt - 0.28) / 0.35) * (1.0 if d >= 1.4 * BEAT else 0.55 if d >= 0.9 * BEAT else 0.0)
            br[i0:i1] = 0.45 + 0.25 * smooth01(tt / 0.4) + (0.12 if fz > 600 else 0.0)
            prev = name
        else:
            prev = None
        t += d
    # 休みの 所は 前の 音の 高さを のばして おく（消えて いく 間も 高さが とばない）
    idx = np.where(f > 0, np.arange(n), 0); np.maximum.accumulate(idx, out=idx); f = f[idx]
    f[f <= 0] = hz(next(it[0] for it in items if it[0] is not None))
    if dyn is not None: a = a * (0.35 + 0.65 * dyn_line(dyn, n))                # 小節ごとの 強弱
    if swell: a = a * (1 - swell + swell * np.sin(np.pi * np.clip(np.mod(np.arange(n) / SR / (3 * BEAT), 1.0), 0, 1)) ** 0.8)      # 小節の まん中で ふくらむ（2本目）
    a = lp1(a * dip, 45.0)
    # 高さ：音の うつりを すべらせる（port 秒ほど）
    fc = 2.2 / (TAU * port)
    f = np.exp(lp1(lp1(np.log(f), fc), fc))
    # ビブラート（速さは ゆっくり ゆらぐ）・高さの 小さな ゆらぎ
    rate = np.clip(5.5 + 5.0 * lp1(rng.standard_normal(n), 0.7), 4.9, 6.1)
    vph = TAU * np.cumsum(rate) / SR
    vd = lp1(vd, 6.0)
    jit = np.clip(0.055 * lp1(rng.standard_normal(n), 7.0), -0.003, 0.003)
    f = f * (1 + vd * np.sin(vph) + jit)
    a = a * (1 + 0.045 * (vd / max(vib, 1e-6)) * np.sin(vph + 0.6))               # ビブラートに 合わせて 大きさも 少し ゆれる
    a = a * (1 + 0.035 * np.clip(14 * lp1(rng.standard_normal(n), 11.0), -1, 1))  # 弓の 圧の 小さな むら
    y = bowed(f, np.clip(a, 0, None), np.clip(lp1(br, 8.0), 0, 1), seed + 1) * level
    out = y[:NL].copy(); out[:tail] += y[NL:]             # おわりの のこりを 頭へ
    return out


def pad_voice(seed):
    """2本目：小節ごとに 2つの 音を のばす（弱く・ビブラートは 浅く）。小節の かわり目は なめらかに つなぐ"""
    lo = [(p[0], 3, 'b') if p else (None, 3) for p in PAD]
    hi = [(p[1], 3, 'b') if p else (None, 3) for p in PAD]
    return line(lo, seed, vib=0.0035, port=0.09, level=0.55, swell=0.35), line(hi, seed + 7, vib=0.0040, port=0.09, level=0.5, swell=0.35)


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


def insects(seed):
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
        buf[0] += g * np.sqrt((1 - pan) / 2) * y; buf[1] += g * np.sqrt((1 + pan) / 2) * y
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


def render():
    """くり返す 1回り（ステレオ・2×NL）"""
    lead = line(LEAD, 1178, vib=0.0078, port=0.055, level=1.0, dyn=DYN)
    plo, phi = pad_voice(2178)
    # 2本目は ふしの うしろへ：小さく・高い 所を 少し 落とす
    plo = lp1(plo, 2600); phi = lp1(phi, 3000)
    mus = pan2(lead, -0.18) * 1.0 + pan2(plo, 0.30) * 0.30 + pan2(phi, 0.22) * 0.27
    mus = mus / (np.abs(mus).max() + 1e-9)
    mus = wet(mus, reverb_ir(77), 0.30)
    ins = wet(insects(4178), reverb_ir(78, rt=1.1), 0.10)
    air = night_air(5178)
    mus_rms = np.sqrt(np.mean(mus ** 2)); ins_rms = np.sqrt(np.mean(ins ** 2))
    mix = mus * (0.20 / mus_rms) + ins * (0.058 / ins_rms) + air * 3.0
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
        print(f'できた：{FILE} {os.path.getsize(o)} B・1回り {LOOP:.3f}秒（前後に {PRE}秒ずつ）・山 {np.abs(x).max():.2f}・ふつうの 大きさ（RMS）{np.sqrt(np.mean(x ** 2)):.3f} → {OUT}')
