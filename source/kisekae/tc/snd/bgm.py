# 特別な フィールドの BGM（11/09 02:54 まさちゃん「幻の馬フィールドは、闇っぽいBGM・神様馬フィールドは、神っぽいBGM」）
#   ぜんぶ 計算で 作る（録音・素材は 使わない）・つなぎ目なく くり返せる 60秒（4拍子 16小節・64 BPM）
#   ・闇（幻の馬）：ニ短調。低い うなり（D）・くらい パッド（Dm → E♭ → B♭ → Asus4 → Dm）・ガラスの ような 鈴の 旋律（ときどき）
#                   ・高い 所の かすかな ゆらぎ・遠くの 低い ドーン・風
#   ・神（神様馬）：ハ長調。オーケストラ・教会（11/09 03:04）：パイプオルガン・合唱・弦・ホルン・教会の 鐘・ティンパニ（讃美歌の 進行・おわりは アーメン F→C）
#   トレーニングセンター＝落ち着ける 場所 → どちらも ゆっくり・やさしく・こわく しない
#   つなぎ目なし：ずっと 鳴る 音は ループの 長さで ちょうど 一周する 周波数・音の のこり と ひびき は 頭へ まわす（輪の ように）
#   python3 bgm.py <abyss|divine> <出す wav>              … 60秒の ループ（アプリ 用）
#   python3 bgm.py seq <出す wav> abyss:45 divine:45 …     … 動画の じゅんに（morning・evening・night は 場内の 環境音）
import math, os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
SR = amb.SR
BPM = 64; BEAT = 60 / BPM; BAR = 4 * BEAT; BARS = 16; LOOP = BARS * BAR          # 60.0 秒
N = int(round(LOOP * SR)); TAILN = int(8.0 * SR)
RMS_DB = -36.0          # ループ 全体の 大きさ（場内の 環境音 −43dB より 少し 大きい くらい：やさしく）
T = np.arange(N) / SR


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def per(f): return round(f * LOOP) / LOOP              # ループで ちょうど 一周する 周波数（ちがいは 0.01Hz 未満）


def env_ar(n, a, r):
    e = np.ones(n); ka = min(n, max(1, int(a * SR))); kr = min(n - ka, max(1, int(r * SR)))
    e[:ka] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ka)); e[n - kr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, kr))
    return e


class Stem:
    """音の 置き場（ループ ＋ のこり）。fold() で のこりを 頭へ まわす"""
    def __init__(self): self.b = np.zeros((2, N + TAILN))
    def put(self, x, at, pan=0.0):
        x = np.asarray(x); i = int(at * SR) % N
        st = np.stack([x * math.sqrt((1 - pan) / 2), x * math.sqrt((1 + pan) / 2)])
        while st.shape[1] > 0:
            m = min(st.shape[1], self.b.shape[1] - i); self.b[:, i:i + m] += st[:, :m]; st = st[:, m:]; i = 0
    def fold(self):
        y = self.b[:, :N].copy(); y[:, :TAILN] += self.b[:, N:]; return y


def cont(x, pan=0.0):
    """ずっと 鳴る 音（長さ N）→ ステレオ"""
    return np.stack([x * math.sqrt((1 - pan) / 2), x * math.sqrt((1 + pan) / 2)])


def circ_lp(x, fc, order=2):
    """輪の ように つながった 音に ローパス（頭と おしりを つないで かける）"""
    pad = 8192; y = amb.lp(np.concatenate([x[..., -pad:], x], -1), fc, order); return y[..., pad:]


def norm(x):
    """鳴って いる 所の 大きさ（RMS）を 1 に"""
    a = np.abs(x).max(0) if x.ndim == 2 else np.abs(x)
    act = a > 0.02 * a.max(); r = math.sqrt(float(np.mean((x[..., act] if x.ndim == 2 else x[act]) ** 2)))
    return x / max(r, 1e-12)


def reverb(x, rt, mix, seed, lp):
    rng = np.random.default_rng(seed); n = int(rt * SR); y = x * (1 - 0.5 * mix)
    for c in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-6.9 * np.arange(n) / n); ir = amb.lp(ir, lp, 1); ir[:int(0.02 * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
        w = signal.fftconvolve(x[c], ir); out = w[:N].copy(); rest = w[N:]
        while len(rest): m = min(len(rest), N); out[:m] += rest[:m]; rest = rest[m:]          # ひびきの のこりは 頭へ（輪）
        y[c] += mix * out
    return y


def mix(stems, rt, wet, seed, lp):
    x = sum(10 ** (db / 20) * norm(s) for s, db in stems)
    x = reverb(x, rt, wet, seed, lp)
    x = amb.hp(np.concatenate([x[:, -8192:], x], 1), 28, 2)[:, 8192:]
    r = math.sqrt(float(np.mean(x ** 2))); x *= 10 ** (RMS_DB / 20) / max(r, 1e-12)
    pk = float(np.abs(x).max())
    if pk > 10 ** (-12 / 20): x *= 10 ** (-12 / 20) / pk                  # 山は −12dB まで
    return x


# ---------------- 闇（幻の馬） ----------------
def abyss():
    rng = np.random.default_rng(31)
    # 1. 低い うなり：D2 と A1（ゆっくり 大きく 小さく：ループで 2周）
    dr = np.sin(2 * np.pi * per(mtof(38)) * T) + 0.22 * np.sin(2 * np.pi * per(2 * mtof(38)) * T + 0.4) + 0.5 * np.sin(2 * np.pi * per(mtof(33)) * T)
    dr *= 0.7 + 0.3 * np.sin(2 * np.pi * 2 * T / LOOP)
    drone = cont(circ_lp(dr, 240), 0.0)
    # 2. くらい パッド：Dm → E♭ → B♭ → Asus4（4小節 ずつ）
    pad = Stem()
    for ci, ch in enumerate([[50, 53, 57], [51, 55, 58], [46, 50, 53], [45, 50, 52]]):
        n = int((4 * BAR + 3.0) * SR); tt = np.arange(n) / SR; x = np.zeros(n)
        for m in ch:
            for d in (-0.07, 0.0, 0.07):
                x += signal.sawtooth(2 * np.pi * mtof(m) * 2 ** (d / 12) * tt + rng.uniform(0, 6.28))
        cuts = [380, 560, 740, 920, 1100]; Y = np.stack([amb.lp(x, c, 2) for c in cuts])
        pos = (0.5 + 0.5 * np.sin(2 * np.pi * (tt + ci * 4 * BAR) / 20)) * (len(cuts) - 1)
        i0 = np.clip(np.floor(pos).astype(int), 0, len(cuts) - 2); fr = pos - i0; ar = np.arange(n)
        y = (Y[i0, ar] * (1 - fr) + Y[i0 + 1, ar] * fr) * env_ar(n, 2.8, 3.2)
        pad.put(y, ci * 4 * BAR, -0.15 + 0.3 * (ci % 2))
    # 3. ガラスの 鈴（ときどき）：A4 D5 F5 E5 ／ A4 D5 E♭5 D5
    bell = Stem()
    def gbell(f, dur=4.5):
        n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
        for r_, a_, d_ in ((1.0, 1.0, 2.6), (2.76, 0.32, 1.2), (5.4, 0.14, 0.6), (8.93, 0.05, 0.3)):
            y += a_ * np.sin(2 * np.pi * f * r_ * tt) * np.exp(-tt / d_)
        y[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR)); return amb.lp(y, 5000, 2)
    for bar, beat, m in [(0, 0, 69), (2, 1.5, 74), (4, 0, 77), (6, 2, 76), (8, 0, 69), (10, 1.5, 74), (12, 0, 75), (14, 2, 74)]:
        bell.put(gbell(mtof(m)), bar * BAR + beat * BEAT, rng.uniform(-0.4, 0.4))
    # 4. 高い 所の かすかな ゆらぎ（D6 と E♭6）
    shim = Stem()
    for bar in (4, 12):
        n = int(4 * BAR * SR); tt = np.arange(n) / SR
        shim.put((np.sin(2 * np.pi * mtof(86) * tt) + 0.8 * np.sin(2 * np.pi * mtof(87) * tt)) * env_ar(n, 5, 6), bar * BAR, 0.3 if bar == 4 else -0.3)
    # 5. 遠くの 低い ドーン（1小節目・9小節目）
    boom = Stem()
    for bar in (0, 8):
        n = int(5 * SR); tt = np.arange(n) / SR; f = 52 * np.exp(-tt / 2.5) + 36
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 1.8); y[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        boom.put(amb.lp(y, 180, 2), bar * BAR + 0.05)
    # 6. 風（とても 小さく）
    w = circ_lp(amb.bp(rng.normal(0, 1, N), 180, 700, 2), 900) * (0.55 + 0.45 * np.sin(2 * np.pi * 3 * T / LOOP + 1.0))
    wind = np.stack([w, np.roll(w, int(0.013 * SR))])
    return mix([(drone, -7), (pad.fold(), -3), (bell.fold(), -9), (shim.fold(), -24), (boom.fold(), -11), (wind, -25)], 3.8, 0.42, 7, 5000)


# ---------------- 神（神様馬） ----------------
FORM = [(850, 1.0, 110), (1220, 0.55, 120), (2810, 0.3, 180)]       # 「あー」の 声の 山（女声）


def choir(f, n, rng):
    """合唱の「あー」：のこぎり波 → 声の 山 3つ（帯の フィルター）・ゆらぎ（ビブラート）・3人"""
    tt = np.arange(n) / SR; y = np.zeros(n)
    for v in range(3):
        vib = 1 + 0.004 * np.sin(2 * np.pi * (5.0 + 0.4 * v) * tt + rng.uniform(0, 6.28)) + (v - 1) * 0.0025
        y += signal.sawtooth(2 * np.pi * np.cumsum(f * vib) / SR + rng.uniform(0, 6.28))
    out = np.zeros(n)
    for fc, a_, bw in FORM:
        b, a = signal.butter(2, [(fc - bw) / (SR / 2), (fc + bw) / (SR / 2)], 'band'); out += a_ * signal.lfilter(b, a, y)
    out += 0.25 * amb.lp(y, 500, 2)                                      # 声の 下の 方（あたたかさ）
    return amb.lp(out, 4500, 2)


def pluck(f, dur, rng):
    """ハープ：カープラス・ストロング（弦を はじく）"""
    n = int(dur * SR); L = max(2, int(round(SR / f))); ring = np.convolve(rng.uniform(-1, 1, L), [0.25, 0.5, 0.25], 'same'); out = np.empty(n); idx = 0      # はじめの 音を 少し まるく（やわらかい ハープ）
    for i in range(n):
        out[i] = ring[idx]; nx = idx + 1 if idx + 1 < L else 0; ring[idx] = 0.4985 * (ring[idx] + ring[nx]); idx = nx
    out[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return amb.lp(out, 5200, 2)


# 讃美歌の ような 進行（1小節 1和音）：[ベース, テノール, アルト, ソプラノ]・おわりは「アーメン」（F → C）
HYMN = [[36, 55, 60, 64], [33, 57, 60, 64], [29, 57, 60, 65], [31, 55, 59, 62],
        [40, 55, 60, 64], [41, 57, 60, 65], [38, 57, 62, 65], [31, 55, 59, 62],
        [33, 57, 60, 64], [40, 55, 59, 64], [41, 57, 60, 65], [40, 55, 60, 67],
        [38, 57, 60, 65], [31, 55, 59, 62], [29, 57, 60, 65], [36, 55, 60, 64]]
SWELL = [0.75, 0.75, 0.8, 0.8, 0.85, 0.9, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.15, 0.95, 0.85]        # だんだん 大きく → アーメンで 落ち着く


def organ(f, n, rng, stops=((1, 1.0), (2, 0.5), (3, 0.22), (4, 0.2), (5, 0.07), (6, 0.06), (8, 0.05))):
    """パイプオルガン：パイプの 音の 重ね（8'・4'・2 2/3'・2'…）・はじめに 小さな「シュッ」・ゆるい ゆれ（トレモロ）"""
    tt = np.arange(n) / SR; vib = 1 + 0.0012 * np.sin(2 * np.pi * 5.3 * tt + rng.uniform(0, 6.28))
    ph = 2 * np.pi * np.cumsum(f * vib) / SR; y = np.zeros(n)
    for h, a in stops:
        if f * h < 9000: y += a * np.sin(h * ph + rng.uniform(0, 6.28))
    ch = amb.bp(rng.normal(0, 1, n), min(f * 3, 6000), min(f * 6, 9000), 2) * np.exp(-tt / 0.05) * 0.15
    e = np.ones(n); ka = int(0.07 * SR); kr = int(0.25 * SR); e[:ka] = np.linspace(0, 1, ka); e[-kr:] *= np.linspace(1, 0, kr)
    return (y + ch) * e


def strings(f, n, rng, att=0.8, rel=1.2):
    """弦の 合奏：少し ずらした のこぎり波 5本・ビブラート・やわらかい ローパス"""
    tt = np.arange(n) / SR; y = np.zeros(n)
    for v in range(5):
        vib = 1 + 0.003 * np.sin(2 * np.pi * (5.2 + 0.3 * v) * tt + rng.uniform(0, 6.28)) + (v - 2) * 0.0018
        y += signal.sawtooth(2 * np.pi * np.cumsum(f * vib) / SR + rng.uniform(0, 6.28))
    return amb.lp(amb.lp(y, 2600, 2), 3200, 2) * env_ar(n, att, rel) / 5


def horn(f, n, rng):
    """やわらかい ホルン：音の 大きさ と いっしょに 明るく なる"""
    tt = np.arange(n) / SR; e = env_ar(n, 1.2, 1.5)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f * (1 + 0.002 * np.sin(2 * np.pi * 4.8 * tt))) / SR)
    cuts = [300, 550, 800, 1100]; Y = np.stack([amb.lp(y, c, 2) for c in cuts]); pos = e * (len(cuts) - 1)
    i0 = np.clip(np.floor(pos).astype(int), 0, len(cuts) - 2); fr = pos - i0; ar = np.arange(n)
    return (Y[i0, ar] * (1 - fr) + Y[i0 + 1, ar] * fr) * e


def church_bell(f, dur=7.0):
    """教会の 鐘：低い 音（ハム）・もとの 音・短三度・五度・上の 音（鐘らしい ずれた 響き）"""
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for r_, a_, d_ in ((0.5, 0.5, 5.0), (1.0, 1.0, 3.5), (1.183, 0.45, 2.6), (1.506, 0.35, 2.2), (2.0, 0.5, 1.8), (2.514, 0.18, 1.0), (2.662, 0.15, 0.9), (3.011, 0.12, 0.7), (4.166, 0.06, 0.4)):
        y += a_ * np.sin(2 * np.pi * f * r_ * tt + r_) * np.exp(-tt / d_)
    k = int(0.006 * SR); y[:k] *= np.linspace(0, 1, k)
    return amb.lp(y, 4500, 2)


def timpani_roll(f, dur, rng):
    """ティンパニの 小さな ロール（だんだん 大きく → 小さく）"""
    n = int(dur * SR); y = np.zeros(n); hit = int(0.6 * SR); th = np.arange(hit) / SR
    one = lambda a: (np.sin(2 * np.pi * np.cumsum(f * (1 + 0.04 * np.exp(-th / 0.05))) / SR) * np.exp(-th / 0.45) + amb.lp(rng.normal(0, 1, hit), 400, 2) * 0.25 * np.exp(-th / 0.06)) * a
    k = 0.0
    while k < dur - 0.3:
        a = math.sin(math.pi * k / dur) ** 1.5 * (0.8 + 0.2 * rng.uniform())
        i = int(k * SR); m = min(hit, n - i); y[i:i + m] += one(a)[:m]; k += 0.085
    return amb.lp(y, 700, 2)


def divine():
    """神様馬フィールド：オーケストラ・教会（11/09 03:04 まさちゃん「オーケストラっぽい、教会っぽいBGMにして！」）
    パイプオルガン（4声＋足の 低音）・合唱「あー」・弦（ソプラノの 1オクターブ 上 と 低音）・やわらかい ホルン（盛り上がる 所）
    ・教会の 鐘（1小節目・9小節目）・ティンパニの 小さな ロール（9小節目・13小節目）・大きな 聖堂の ひびき"""
    rng = np.random.default_rng(57)
    org, cho, strg, hrn, bel, tim = Stem(), Stem(), Stem(), Stem(), Stem(), Stem()
    for bi, (B, Tn, A, S) in enumerate(HYMN):
        st = bi * BAR; n = int((BAR + 0.35) * SR); w = SWELL[bi]
        x = organ(mtof(B), n, rng) * 0.9 + organ(mtof(Tn), n, rng) * 0.6 + organ(mtof(A), n, rng) * 0.6 + organ(mtof(S), n, rng) * 0.7
        if B >= 36: x += organ(mtof(B - 12), n, rng, ((1, 1.0), (2, 0.3), (3, 0.1))) * 0.6                # 足の 16'
        org.put(x, st)
        nn = int((BAR + 1.6) * SR)
        cx = sum(choir(mtof(m), nn, rng) for m in (Tn, A, S)) * env_ar(nn, 0.9, 1.4) * w
        cho.put(cx, st - 0.2, -0.15 + 0.3 * (bi % 2))
        sx = (strings(mtof(S + 12), nn, rng) * 0.8 + strings(mtof(B + 12 if B < 36 else B), nn, rng) * 0.6) * w
        strg.put(sx, st - 0.25, 0.2)
        if 8 <= bi <= 14:                                                                                    # 9〜15小節：ホルンが そっと 入る
            hrn.put((horn(mtof(A - 12), nn, rng) + horn(mtof(Tn - 12 + 12), nn, rng) * 0.7) * (w - 0.8), st - 0.2, -0.3)
    for bar in (0, 8):
        bel.put(church_bell(mtof(60)), bar * BAR + 0.02, 0.25)
    bel.put(church_bell(mtof(55)) * 0.6, 15 * BAR + 2 * BEAT, -0.25)
    for bar, f in ((8, mtof(45)), (12, mtof(38))):
        tim.put(timpani_roll(f, 2 * BEAT, rng), bar * BAR - 2 * BEAT, 0.0)
    return mix([(org.fold(), -1), (cho.fold(), -2), (strg.fold(), -5), (hrn.fold(), -10), (bel.fold(), -9), (tim.fold(), -15)], 6.0, 0.55, 9, 6500)


def write(path, x):
    wavfile.write(path, SR, (np.clip(x.T, -1, 1) * 32767).astype(np.int16))


if __name__ == '__main__':
    if sys.argv[1] == 'seq':
        out = sys.argv[2]; SEQ = [(a.split(':')[0], float(a.split(':')[1])) for a in sys.argv[3:]]
        cache = {}; parts = []
        for i, (k, sec) in enumerate(SEQ):
            if k in ('abyss', 'divine'):
                if k not in cache: cache[k] = abyss() if k == 'abyss' else divine()
                L = cache[k]; reps = int(np.ceil(sec / LOOP)) + 1
                parts.append(np.tile(L, reps)[:, :int(sec * SR)].copy())
            else:
                parts.append(amb.scene(sec, k, 100 + i))
        x = int(.4 * SR)
        for i, p in enumerate(parts):
            if i > 0: p[:, :x] *= np.linspace(0, 1, x)
            if i < len(parts) - 1: p[:, -x:] *= np.linspace(1, 0, x)
        total = np.concatenate(parts, 1); write(out, total)
        print(out, round(total.shape[1] / SR, 1), '秒', 'peak', round(float(np.abs(total).max()), 3))
    else:
        k, out = sys.argv[1], sys.argv[2]
        x = abyss() if k == 'abyss' else divine(); write(out, x)
        print(out, round(x.shape[1] / SR, 1), '秒', 'rms', round(20 * math.log10(math.sqrt(float(np.mean(x ** 2)))), 1), 'dB', 'peak', round(20 * math.log10(float(np.abs(x).max())), 1), 'dB')
