# 決戦調査の BGM（第4.196版・まさちゃん 2026/11/18 15:09「BGMは、決戦調査用の闘いに合うBGMを作成して！」）
#   第4.198版（まさちゃん 21:37「BGMは、イントロだけでいいや！ ただイントロももう少し音暗くしてほしい！ 未来の崩壊した都市に合いそうな音楽がいい！」→ 聞く 用の ファイル → 21:45「いいね！これ入れて！」）：
#     前の 曲（32小節：A イントロ → B 金管の テーマ → C 声の 和音 → D）の イントロ だけを もとに、暗い 音で 作り直した 16小節（イントロの 形を 2回：2回目は 少し 厚く）
#   ぜんぶ 計算で 作る（録音・よその 曲・よその 音は 使わない）
#   python3 kisekae/cb_qbgm.py                 … ios/cb_assets/cb_qbgm.m4a（アプリに 入れる 形：ステレオ 44.1kHz・AAC）
#   python3 kisekae/cb_qbgm.py wav <出す wav>   … 聞いて・測って 確かめる 用（くり返す 1回り だけ）
#
#   曲：d moll（レ の 短調）・132 BPM（前の イントロと 同じ 速さ）・4/4・16小節（1回り 約29.1秒＝LOOP：cb/cb_app.js の BGMS.quest.len と 同じ）
#     イントロの 形（前の 曲の 1〜8小節）：太鼓の きざみ（1・2の裏・3・4拍）＋ 低い 音の 8分の きざみ（根・根・オクターブ上・根・根・根・5度・オクターブ上）＋ 16分の 分散
#     → 暗い 音に：太鼓は こわれた 工場の 鉄の 音（低い ドン ＋ 鉄の ひびき）・低い 弦 → 暗い シンセの ベース（フィルターが ゆっくり 開いて 閉じる）・
#        明るい 弦の 分散 → こもった ガラスの 音（1オクターブ 下・遠くで はねかえる こだま）・明るい シンバル → 吸いこむ 暗い 風の 音・
#        うしろに 低い うなり（こわれた 都市の 空気）・遠くの 鉄の きしみ・遠くの サイレン（1回り に 1回・小さく）
#     和音（もっと 暗く：明るい C を やめて、♭II の E♭ で「こわれた」感じ）：Dm｜B♭｜Gm｜A｜Dm｜B♭｜E♭｜A（2回）
#   くり返し：1回りより 長い 音の しっぽ（ひびき・こだま）は 頭へ 回す（つなぎ目で 音が とばない）。アプリ用の ファイルは 1回りの 前と うしろに PRE 秒（0.5秒）ずつ 同じ 音の つづき
#     → アプリは まん中の 1回り だけを くり返す（いつもの BGM と 同じ 形）
#   iPhone の スピーカーでも 聞こえる ように、低い 音は 倍音（100〜400Hz）を 残す・高い 音（6kHz〜）は へらして 暗く
import os, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
FILE = 'cb_qbgm.m4a'
SR = 44100
TAU = 2 * np.pi
BPM = 132
BEAT = 60.0 / BPM
BARS = 16
LOOP = BARS * 4 * BEAT          # 1回り（秒）＝ 16 * 4 * 60 / 132
PRE = 0.5
PEAK = 0.50
PHONE = 0.030                   # iPhone の スピーカーで 聞こえる 所（280Hz〜7kHz）の ふつうの 大きさ：前の 曲の イントロ 0.023・曲 ぜんたい 0.042 の あいだ（低い 音は スピーカーから 出ない ので こちらで そろえる）
RMS_MAX = 0.075                 # ぜんぶの 音の ふつうの 大きさの 上限（イヤホンで 大きく なりすぎない）
NL = int(round(LOOP * SR))
TAIL = int(5.0 * SR)            # 1回りの うしろに はみ出して よい 長さ（あとで 頭へ 回す）

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(n):
    """'D4' → 周波数"""
    nm, oc = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTE[nm] + 12 * (oc + 1) - 69) / 12)


CH = {'Dm': ['D', 'F', 'A'], 'Bb': ['Bb', 'D', 'F'], 'Gm': ['G', 'Bb', 'D'], 'A': ['A', 'C#', 'E'], 'Eb': ['Eb', 'G', 'Bb']}
PROG = ['Dm', 'Bb', 'Gm', 'A', 'Dm', 'Bb', 'Eb', 'A']


def tb(bar, beat=0.0):
    """小節（0から）と 拍（0〜）→ 秒"""
    return (bar * 4 + beat) * BEAT


def put(buf, x, at, pan=0.0, g=1.0):
    """buf（2×n）の at 秒に x を 置く（pan：−1 左〜＋1 右）"""
    i = int(round(at * SR)); n = min(len(x), buf.shape[1] - i)
    if n <= 0 or i < 0: return
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    buf[0, i:i + n] += x[:n] * g * l; buf[1, i:i + n] += x[:n] * g * r


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def saw(f, sec, cut=6000, ph=0.0):
    """のこぎり波（足し算で 作る：cut Hz より 上の 倍音は 入れない）"""
    t = t_(sec); y = np.zeros(len(t)); nh = max(1, min(80, int(cut / f)))
    for k in range(1, nh + 1):
        y += np.sin(TAU * f * k * t + ph * k) / k
    return y * (2 / np.pi)


def sq(f, sec, cut=3000, ph=0.0):
    """四角い 波（奇数の 倍音 だけ）"""
    t = t_(sec); y = np.zeros(len(t)); nh = max(1, min(40, int(cut / f)))
    for k in range(1, nh + 1, 2):
        y += np.sin(TAU * f * k * t + ph * k) / k
    return y * (4 / np.pi)


def lp(x, fc, order=2):
    return signal.lfilter(*signal.butter(order, min(0.99, fc / (SR / 2)), 'low'), x)


def bp(x, lo, hi, order=2):
    return signal.lfilter(*signal.butter(order, [lo / (SR / 2), min(0.99, hi / (SR / 2))], 'band'), x)


def adsr(n, a, d, s, r, sec):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((sec - t) / max(r, 1e-4), 0, 1)
    return e * rel


def svf(x, fc, q=0.7, band=False):
    """時間で かわる フィルター（fc＝Hz：数 か 配列）。band＝False：低い 音だけ 通す／True：fc の まわり だけ 通す。q＝山の 高さ（少し 鳴る）"""
    y = np.zeros_like(x); lo = bd = 0.0; damp = 1.0 / q
    f = 2 * np.sin(np.pi * np.clip(np.broadcast_to(fc, x.shape), 20, SR / 6) / SR)
    for i in range(len(x)):
        hi = x[i] - lo - damp * bd; bd += f[i] * hi; lo += f[i] * bd; y[i] = bd if band else lo
    return y


def svf_lp(x, fc, q=0.7):
    return svf(x, fc, q, False)


# ---------------- 打楽器（こわれた 工場の 音）----------------
def kick(rng, big=1.0):
    """低い ドン：音が 下がる 正弦波（倍音を 少し にごらせて iPhone でも 聞こえる 胴の 音）＋ 鉄の 皮の 雑音"""
    sec = 0.95; t = t_(sec)
    f = 52 + 95 * np.exp(-t * 24)
    ph = TAU * np.cumsum(f) / SR
    body = np.tanh(1.8 * (np.sin(ph) + 0.35 * np.sin(2.0 * ph) * np.exp(-t * 6))) * np.exp(-t * (4.2 / big))
    skin = bp(rng.standard_normal(len(t)), 120, 900) * np.exp(-t * 26) * 0.9
    return (body + skin) * np.minimum(1, t / 0.003)


def clank(rng, f0=210.0, g=1.0):
    """鉄の ひびき（倍音が そろわない 鉄の 板：こわれた ビルの 鉄骨）"""
    sec = 1.6; t = t_(sec); y = np.zeros(len(t))
    for k, (r, d, a) in enumerate(((1.0, 3.2, 1.0), (2.31, 4.5, 0.7), (3.87, 6.0, 0.45), (5.62, 8.0, 0.30), (7.15, 10.0, 0.18))):
        y += a * np.sin(TAU * f0 * r * t + rng.uniform(0, TAU)) * np.exp(-t * d)
    hit = bp(rng.standard_normal(len(t)), 400, 3000) * np.exp(-t * 60) * 0.5
    return lp((y + hit) * np.minimum(1, t / 0.002), 3500) * g


def low_tom(rng, f0=95):
    """低い 鉄の 太鼓（4小節ごとの おかず）"""
    sec = 0.6; t = t_(sec)
    f = f0 * (1 + 0.6 * np.exp(-t * 28))
    body = np.tanh(1.5 * np.sin(TAU * np.cumsum(f) / SR)) * np.exp(-t * 7.5)
    ring = np.sin(TAU * f0 * 2.7 * t) * np.exp(-t * 14) * 0.25
    skin = bp(rng.standard_normal(len(t)), 200, 1500) * np.exp(-t * 40) * 0.35
    return body + ring + skin


def snap(rng, g=1.0):
    """乾いた 打つ 音（2回目の 8小節の 2・4拍：こもった 手拍子）"""
    sec = 0.3; t = t_(sec); x = rng.standard_normal(len(t))
    e = np.exp(-t * 34) + 0.5 * np.exp(-np.maximum(0, t - 0.011) * 34) * (t > 0.011) + 0.3 * np.exp(-np.maximum(0, t - 0.022) * 30) * (t > 0.022)
    return bp(x, 700, 2600) * e * g


def tick(rng):
    """16分の 小さな 金属の きざみ（2回目の 8小節：遠くの 機械）"""
    sec = 0.05; t = t_(sec)
    return bp(rng.standard_normal(len(t)), 2500, 5500) * np.exp(-t * 90) * np.minimum(1, t / 0.002)


def swell(rng, sec):
    """吸いこむ 暗い 風（区切りの 前：明るい シンバルの かわり）"""
    t = t_(sec); x = rng.standard_normal(len(t)); r = (t / sec) ** 2.2
    fc = 300 + 1700 * r
    return svf_lp(x, fc, 1.4) * r * 0.9


def boom(rng):
    """区切りの 頭：低い ドーン（遠くの くずれる 音）"""
    sec = 3.0; t = t_(sec)
    f = 38 + 30 * np.exp(-t * 3)
    y = np.tanh(2.2 * np.sin(TAU * np.cumsum(f) / SR)) * np.exp(-t * 1.6)
    rum = lp(rng.standard_normal(len(t)), 260) * np.exp(-t * 1.2) * 0.8
    return (y + rum) * np.minimum(1, t / 0.01)


# ---------------- 音の ある 楽器 ----------------
def bass_note(f, sec, rng, cut):
    """暗い シンセの ベース：のこぎり波 2本（少し ずらす）＋ 1オクターブ 下の 四角 → 低い 音だけ 通す（cut：その 時の 開き）"""
    n = int(sec * SR)
    y = 0.6 * saw(f * 0.997, sec + 0.05, cut=2400, ph=rng.uniform(0, TAU)) + 0.6 * saw(f * 1.003, sec + 0.05, cut=2400, ph=rng.uniform(0, TAU)) + 0.45 * sq(f * 0.5, sec + 0.05, cut=900)
    y = y[:n]
    env = adsr(n, 0.004, 0.10, 0.55, 0.05, sec)
    fc = cut * (0.55 + 0.9 * np.exp(-np.arange(n) / SR * 18))          # 打った すぐ あとだけ 少し 開く
    return np.tanh(1.4 * svf_lp(y, fc, 1.6)) * env


def glass(f, sec, rng):
    """こもった ガラスの 音（16分の 分散：FM で 少し 金属っぽく・高い 音は けずる）"""
    n = int(sec * SR); t = np.arange(n) / SR
    mod = np.sin(TAU * f * 2.0 * t) * (1.6 * np.exp(-t * 22))
    y = np.sin(TAU * f * t + mod + rng.uniform(0, TAU)) * np.exp(-t * 9) * np.minimum(1, t / 0.003)
    return lp(y, 2200)


def drone(fs, sec, rng):
    """低い うなり（こわれた 都市の 空気）：少しずつ ずらした のこぎり波を ゆっくり 開く フィルターで"""
    n = int(sec * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f in fs:
        for d in (-0.006, -0.002, 0.003, 0.007):
            y += saw(f * (1 + d), sec, cut=1800, ph=rng.uniform(0, TAU))[:n]
    fc = 260 + 260 * (0.5 - 0.5 * np.cos(TAU * t / sec))
    return svf_lp(y / (4 * len(fs)), fc, 0.9) * adsr(n, 1.2, 1.0, 1.0, 1.2, sec)


def siren(sec):
    """遠くの サイレン（ゆっくり 上がって 下がる：小さく・遠く）"""
    t = t_(sec)
    f = 520 + 160 * (0.5 - 0.5 * np.cos(TAU * t / (sec / 2)))
    y = np.sin(TAU * np.cumsum(f) / SR) + 0.25 * np.sin(2 * TAU * np.cumsum(f) / SR)
    return lp(y, 1800) * np.sin(np.pi * t / sec) ** 2


def creak(rng, sec=1.4):
    """遠くの 鉄の きしみ（こすれる 音：細い 山が ゆれる）"""
    t = t_(sec); x = rng.standard_normal(len(t))
    f0 = 340 + 90 * np.sin(TAU * 0.7 * t + rng.uniform(0, TAU))
    y = svf(x, f0, 18.0, True)                                     # 細い 山が ゆれる（こすれて きしむ）
    return lp(y, 1500) * np.sin(np.pi * t / sec) ** 1.5 * 1.6


def wind(rng, sec):
    """こわれた 都市の 風（低い 雑音が ゆっくり ゆれる）"""
    t = t_(sec); x = rng.standard_normal(len(t))
    fc = 380 + 220 * np.sin(TAU * t / sec * 2 + 1.0) + 120 * np.sin(TAU * t / sec * 5)
    return svf_lp(x, fc, 1.1) * (0.6 + 0.4 * np.sin(TAU * t / sec * 3) ** 2)


# ---------------- 曲 ----------------
def render(parts=False):
    rng = np.random.default_rng(41198)
    L = NL + TAIL
    drums = np.zeros((2, L)); bass = np.zeros((2, L)); arp = np.zeros((2, L)); pad = np.zeros((2, L)); amb = np.zeros((2, L)); fx = np.zeros((2, L))
    for bar in range(BARS):
        ph2 = bar >= 8                                             # 2回目の 8小節（少し 厚く）
        ch = PROG[bar % 8]; r, th, fi = CH[ch]
        root2 = hz(r + '2')                                        # 前の イントロと 同じ 高さ（D2・B♭2・G2・A2・E♭2）
        fifth2 = root2 * 1.5
        # 太鼓：1・(2の裏)・3・4（前の イントロと 同じ きざみ）・3拍に 鉄の ひびき
        for b, g in ((0, 1.0), (1.5, 0.55), (2, 0.85), (3, 0.6)):
            put(drums, kick(rng, 1.0 if b in (0, 2) else 0.8), tb(bar, b), rng.uniform(-0.08, 0.08), g)
        put(drums, clank(rng, 196.0 if bar % 2 else 233.0, 0.30 if ph2 else 0.24), tb(bar, 2), 0.35 if bar % 2 else -0.35)
        if bar % 4 == 3:                                           # 4小節ごとの おかず（低い 鉄の 太鼓）
            for i, f0 in enumerate((128, 110, 96, 84)): put(drums, low_tom(rng, f0), tb(bar, 2 + i * 0.5), -0.35 + 0.23 * i, 0.55)
        if ph2:                                                    # 2回目：こもった 手拍子（2・4拍）・16分の 金属の きざみ
            for b in (1, 3): put(drums, snap(rng), tb(bar, b), 0.12, 0.30)
            for i in range(16): put(drums, tick(rng), tb(bar, i * 0.25), 0.4 if i % 2 else -0.4, 0.05 if i % 2 else 0.08)
        # 低い 8分の きざみ（前の イントロと 同じ 形）：フィルターは 8小節で ゆっくり 開いて 閉じる
        pat = [root2, root2, root2 * 2, root2, root2, root2, fifth2, root2 * 2]
        open_ = 0.5 - 0.5 * np.cos(TAU * ((bar % 8) + 0.5) / 8)
        for i, f in enumerate(pat):
            cut = 420 + 520 * open_ + (90 if ph2 else 0)
            put(bass, bass_note(f, BEAT * 0.46, rng, cut), tb(bar, i * 0.5), 0.0, 0.95 if i % 2 == 0 else 0.72)
        # 16分の 分散（前の イントロの 形を 1オクターブ 下・こもった ガラスの 音・こだま）
        tones = [hz(r + '4') / 2, hz(fi + '3') / 2, hz(th + '4') / 2, hz(fi + '3') / 2]      # 前の イントロの 分散を 1オクターブ 下
        tones = [f * 2 if f < 130 else f for f in tones]            # 低すぎる 音（〜130Hz）は もとの 高さ
        for i in range(16):
            f = tones[i % 4]; acc = 1.0 if i % 4 == 0 else 0.62
            put(arp, glass(f, BEAT * 0.5, rng), tb(bar, i * 0.25), -0.3 if i % 2 else 0.3, acc * (0.42 if ph2 else 0.36))
        # 低い うなり（2小節ごと：和音の 根と 5度）
        if bar % 2 == 0:
            rd = root2 / 2 if root2 >= 110 else root2               # 55〜110Hz
            put(pad, drone([rd, rd * 1.5, rd * 2], BEAT * 8.6, rng), tb(bar), 0.0, 1.0)
    # 区切り：頭に 低い ドーン・前に 吸いこむ 暗い 風
    put(fx, boom(rng), tb(0), 0.0, 0.55); put(fx, boom(rng), tb(8), 0.0, 0.40)
    put(fx, swell(rng, BEAT * 4), tb(7), 0.0, 0.30); put(fx, swell(rng, BEAT * 4), tb(15), 0.0, 0.36)
    # まわりの 音：風（ずっと）・遠くの きしみ・遠くの サイレン（1回りに 1回）
    w = wind(rng, LOOP + 1.0); put(amb, w, 0.0, -0.2, 0.22); put(amb, wind(rng, LOOP + 1.0), 0.0, 0.25, 0.18)
    for at, pn in ((tb(2, 1.0), -0.6), (tb(6, 2.5), 0.55), (tb(11, 0.5), -0.45), (tb(13, 3.0), 0.6)):
        put(amb, creak(rng, 1.2 + rng.uniform(0, 0.6)), at, pn, 0.16)
    put(amb, siren(BEAT * 16), tb(4), 0.5, 0.050)
    hp = lambda x, fc: np.stack([signal.lfilter(*signal.butter(2, fc / (SR / 2), 'high'), np.tile(x[c], 3))[L:2 * L] for c in range(2)])      # 低すぎる 音を へらす（くり返せる 形）
    fold = lambda x: x[:, :NL] + np.pad(x[:, NL:], ((0, 0), (0, NL - (L - NL))))
    ir = reverb_ir(198, rt=2.6, pre=0.03, dark=3800)
    dl = int(round(BEAT * 0.75 * SR))                              # こだま（付点 8分・左右 交互）

    def echo(x, fb=0.42, n=6):
        out = x.copy()
        for k in range(1, n + 1):
            sh = np.roll(x[::-1] if k % 2 else x, k * dl, axis=1) * (fb ** k)
            out += lp_st(sh, 1800)
        return out

    def wet(x, mix):
        out = np.zeros_like(x)
        for c in range(2):
            y = signal.fftconvolve(np.tile(x[c], 3), ir[c])[:3 * NL]
            out[c] = x[c] + mix * y[NL:2 * NL]
        return out
    pt = {'drums': wet(fold(hp(drums, 55)), 0.22), 'bass': wet(fold(hp(bass, 62)), 0.10), 'arp': wet(echo(fold(arp)), 0.40), 'pad': wet(fold(hp(pad, 60)), 0.30),
          'amb': wet(fold(amb), 0.55), 'fx': wet(fold(hp(fx, 30)), 0.35)}
    gain = {'drums': 0.62, 'bass': 0.46, 'arp': 0.55, 'pad': 0.42, 'amb': 0.45, 'fx': 0.45}
    mix = sum(pt[k] * gain[k] for k in pt); mix = mix - mix.mean(axis=1, keepdims=True)
    mix = lp_st(mix, 6500)                                          # 全体を 少し 暗く（高い 音を へらす：くり返せる 形で）
    mix = np.tanh(mix * 1.2) / 1.2                                  # 山を やわらかく そろえる
    g = min(PEAK / np.abs(mix).max(), PHONE / phone_rms(mix), RMS_MAX / np.sqrt(np.mean(mix ** 2)))      # スピーカーで 聞こえる 大きさを そろえる（山は PEAK・ぜんぶの 大きさは RMS_MAX を こえない）
    return (mix * g, {k: pt[k] * gain[k] * g for k in pt}) if parts else mix * g


def phone_rms(x):
    """iPhone の スピーカーで 聞こえる 所（280Hz〜7kHz）の ふつうの 大きさ"""
    b, a = signal.butter(4, [280 / (SR / 2), 7000 / (SR / 2)], 'band')
    y = signal.lfilter(b, a, np.tile(x.mean(axis=0), 2))[x.shape[1]:]
    return float(np.sqrt(np.mean(y ** 2)))


def lp_st(x, fc):
    """2ch に 低い 音だけ 通す フィルター（くり返せる 形：3回 ならべて まん中）"""
    n = x.shape[1]
    return np.stack([signal.lfilter(*signal.butter(2, fc / (SR / 2), 'low'), np.tile(x[c], 3))[n:2 * n] for c in range(2)])


def reverb_ir(seed, rt=1.7, pre=0.022, dark=5200):
    rng = np.random.default_rng(seed); n = int((rt * 1.15 + pre) * SR); t = np.arange(n) / SR
    ir = np.zeros((2, n))
    for ch in range(2):
        x = rng.standard_normal(n) * np.exp(-6.9 * np.maximum(0, t - pre) / rt) * (t >= pre)
        x = signal.lfilter(*signal.butter(1, dark / (SR / 2), 'low'), x)
        x = signal.lfilter(*signal.butter(1, 200 / (SR / 2), 'high'), x)
        ir[ch] = x / np.sqrt(np.sum(x ** 2))
    return ir


def with_margins(x):
    k = int(round(PRE * SR))
    return np.concatenate([x[:, -k:], x, x[:, :k]], axis=1)


def save_wav(x, path):
    wavfile.write(path, SR, (np.clip(x.T, -1, 1) * 32767).astype(np.int16))


def files():
    return [FILE]


if __name__ == '__main__':
    x = render()
    if len(sys.argv) > 2 and sys.argv[1] == 'wav':
        save_wav(x, sys.argv[2]); print('wav', sys.argv[2], round(x.shape[1] / SR, 3), '秒')
    else:
        os.makedirs(OUT, exist_ok=True); tmp = tempfile.mkdtemp(); w = os.path.join(tmp, 'cb_qbgm.wav'); o = os.path.join(OUT, FILE)
        save_wav(with_margins(x), w)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-ac', '2', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', o], check=True)
        print(f'できた：{FILE} {os.path.getsize(o)} B・1回り {LOOP:.3f}秒（前後に {PRE}秒ずつ）・山 {np.abs(x).max():.2f}・ふつうの 大きさ（RMS）{np.sqrt(np.mean(x ** 2)):.4f}・スピーカーで 聞こえる 所 {phone_rms(x):.4f} → {OUT}')
