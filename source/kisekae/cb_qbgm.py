# 決戦調査の BGM（第4.196版・まさちゃん 2026/11/18 15:09「BGMは、決戦調査用の闘いに合うBGMを作成して！」）
#   ぜんぶ 計算で 作る（録音・よその 曲・よその 音は 使わない）
#   python3 kisekae/cb_qbgm.py                 … ios/cb_assets/cb_qbgm.m4a（アプリに 入れる 形：ステレオ 44.1kHz・AAC）
#   python3 kisekae/cb_qbgm.py wav <出す wav>   … 聞いて・測って 確かめる 用（くり返す 1回り だけ）
#
#   曲：d moll（レ の 短調）・132 BPM・4/4・32小節（1回り 約58.2秒＝LOOP：cb/cb_app.js の BGMS.quest.len と 同じ）
#     A（1〜8小節）  ：太鼓 ＋ 低い 弦の きざみ（8分）＋ 弦の 速い 分散（16分）… 戦いの 前の 高まり
#     B（9〜16小節） ：金管の テーマ（勇ましい 旋律）＋ 小太鼓 ＋ シャカシャカ
#     C（17〜24小節）：テーマを 1オクターブ 上で（金管 ＋ 声の 和音）・シンバル … いちばん 盛り上がる
#     D（25〜32小節）：太鼓 と 声の 和音 だけに 落として → 小太鼓の ロールと 吸いこむ 音で 盛り上げて A へ もどる
#     和音：Dm｜B♭｜C｜A｜Dm｜B♭｜Gm｜A（A〜C）・B♭｜C｜Dm｜Dm｜B♭｜C｜A｜A（D）
#   楽器：太鼓（低い ドン：音が 下がる 正弦波 ＋ 皮の 雑音）・中太鼓・小太鼓（雑音 ＋ 胴の 音）・シャカシャカ（高い 雑音）・シンバル・
#         低い 弦／弦の 分散（のこぎり波を 3本 少し ずらして 重ねる・短く 切る）・金管（のこぎり波：立ち上がりで 明るく・ビブラート）・声の 和音（のこぎり波を 母音「あ」の ひびきに）
#   くり返し：1回りより 長い 音の しっぽ（シンバル・ひびき）は 頭へ 回す（つなぎ目で 音が とばない）。アプリ用の ファイルは 1回りの 前と うしろに PRE 秒（0.5秒）ずつ 同じ 音の つづき
#     → アプリは まん中の 1回り だけを くり返す（いつもの BGM と 同じ 形）
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
BARS = 32
LOOP = BARS * 4 * BEAT          # 1回り（秒）＝ 32 * 4 * 60 / 132
PRE = 0.5
PEAK = 0.50
RMS = 0.060                     # ふつうの 大きさ（いつもの BGM は 0.024 ぐらい：たたかいの 曲なので 少し 大きく・効果音が 聞こえる ぐらい）
NL = int(round(LOOP * SR))
TAIL = int(4.0 * SR)            # 1回りの うしろに はみ出して よい 長さ（あとで 頭へ 回す）

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(n):
    """'D4' → 周波数"""
    nm, oc = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTE[nm] + 12 * (oc + 1) - 69) / 12)


CH = {'Dm': ['D', 'F', 'A'], 'Bb': ['Bb', 'D', 'F'], 'C': ['C', 'E', 'G'], 'A': ['A', 'C#', 'E'], 'Gm': ['G', 'Bb', 'D']}
PROG_ABC = ['Dm', 'Bb', 'C', 'A', 'Dm', 'Bb', 'Gm', 'A']
PROG_D = ['Bb', 'C', 'Dm', 'Dm', 'Bb', 'C', 'A', 'A']


def chord_of(bar):
    return (PROG_D if bar >= 24 else PROG_ABC)[bar % 8]


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


def lp(x, fc, order=2):
    return signal.lfilter(*signal.butter(order, fc / (SR / 2), 'low'), x)


def bp(x, lo, hi, order=2):
    return signal.lfilter(*signal.butter(order, [lo / (SR / 2), min(0.99, hi / (SR / 2))], 'band'), x)


def adsr(n, a, d, s, r, sec):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((sec - t) / max(r, 1e-4), 0, 1)
    return e * rel


# ---------------- 打楽器 ----------------
def taiko(rng, big=1.0):
    """太鼓：iPhone の スピーカーでも 聞こえる ように、低すぎる 音（〜60Hz）より 胴の ひびき（100〜300Hz）と 皮の 音を 大きく"""
    sec = 0.9; t = t_(sec)
    f = 64 + 80 * np.exp(-t * 20)
    ph = TAU * np.cumsum(f) / SR
    body = (0.7 * np.sin(ph) + 0.55 * np.sin(2.32 * ph) * np.exp(-t * 7) + 0.3 * np.sin(3.6 * ph) * np.exp(-t * 12)) * np.exp(-t * (4.6 / big))
    skin = bp(rng.standard_normal(len(t)), 150, 1600) * np.exp(-t * 30) * 0.9
    return (body + skin) * np.minimum(1, t / 0.002)


def tom(rng, f0=120):
    sec = 0.5; t = t_(sec)
    f = f0 * (1 + 0.5 * np.exp(-t * 30))
    body = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 9)
    skin = bp(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 45) * 0.4
    return body + skin


def snare(rng, g=1.0):
    sec = 0.35; t = t_(sec)
    nz = bp(rng.standard_normal(len(t)), 1500, 7500) * np.exp(-t * 18)
    body = np.sin(TAU * 196 * t) * np.exp(-t * 30) * 0.5
    return (nz + body) * g


def shaker(rng):
    sec = 0.08; t = t_(sec)
    return bp(rng.standard_normal(len(t)), 5000, 12000) * np.exp(-t * 60) * np.minimum(1, t / 0.006)


def crash(rng, sec=3.2):
    t = t_(sec); x = rng.standard_normal(len(t))
    y = bp(x, 3500, 12000) + 0.5 * bp(x, 7000, 15000)
    return y * np.exp(-t * 1.25) * np.minimum(1, t / 0.004)


def riser(rng, sec):
    """吸いこむ 音（雑音が だんだん 大きく 明るく）"""
    t = t_(sec); x = rng.standard_normal(len(t)); r = (t / sec) ** 2.4
    return lp(x, 900) * r * 0.6 + bp(x, 2000, 9000) * r ** 1.8 * 0.35


# ---------------- 音の ある 楽器 ----------------
def string_note(f, sec, rng, bright=3200):
    """弦（3本 少し ずらして 重ねた のこぎり波・短く）"""
    y = sum(saw(f * (1 + d), sec + 0.05, cut=bright * 1.6, ph=rng.uniform(0, TAU)) for d in (-0.0035, 0.0, 0.004)) / 3
    y = lp(y, bright)
    return y[:int(sec * SR)] * adsr(int(sec * SR), 0.008, 0.06, 0.35, 0.05, sec)


def bass_note(f, sec, rng):
    y = saw(f, sec + 0.05, cut=900, ph=rng.uniform(0, TAU)) + 0.4 * saw(f * 0.5, sec + 0.05, cut=500)
    y = lp(y, 520, 3)
    return y[:int(sec * SR)] * adsr(int(sec * SR), 0.006, 0.12, 0.6, 0.06, sec)


def brass_note(f, sec, rng, bright=1.0):
    n = int(sec * SR); t = np.arange(n) / SR
    vib = 1 + 0.005 * np.sin(TAU * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    ph = TAU * np.cumsum(f * vib) / SR; y = np.zeros(n); nh = max(1, min(30, int(7000 / f)))
    env_b = 0.35 + 0.65 * np.exp(-t * 6)                     # 立ち上がりで 明るい
    for k in range(1, nh + 1):
        y += np.sin(k * ph + 0.2 * k) / k * np.exp(-k * (0.30 / bright) / (0.6 + env_b))
    return y * adsr(n, 0.035, 0.25, 0.75, 0.12, sec)


def choir(fs, sec, rng):
    """声の 和音（母音「あ」：のこぎり波 → 3つの ひびき）"""
    n = int(sec * SR); y = np.zeros(n)
    for f in fs:
        for d in (-0.004, 0.003):
            y += saw(f * (1 + d), sec, cut=5000, ph=rng.uniform(0, TAU))[:n]
    v = 0.0
    for fc, g in ((730, 1.0), (1090, 0.55), (2440, 0.25)):
        v = v + bp(y, fc * 0.82, fc * 1.18) * g
    return v * adsr(n, 0.45, 0.6, 0.85, 0.5, sec)


# ---------------- 曲 ----------------
MELODY = [  # B・C の テーマ（[(音, 拍の 長さ)] × 8小節）
    [('D4', 1.5), ('A4', 0.5), ('A4', 2.0)],
    [('Bb4', 1.0), ('A4', 1.0), ('G4', 1.0), ('F4', 1.0)],
    [('E4', 1.5), ('F4', 0.5), ('G4', 2.0)],
    [('A4', 3.0), ('E4', 0.5), ('C#5', 0.5)],
    [('D5', 1.5), ('C5', 0.5), ('A4', 2.0)],
    [('Bb4', 1.0), ('C5', 1.0), ('D5', 1.0), ('F5', 1.0)],
    [('G5', 1.5), ('F5', 0.5), ('E5', 1.0), ('D5', 1.0)],
    [('C#5', 2.0), ('E5', 1.0), ('A4', 1.0)]]


def up(n, k=1):
    return n[:-1] + str(int(n[-1]) + k)


def render(parts=False):
    rng = np.random.default_rng(41196)
    L = NL + TAIL
    drums = np.zeros((2, L)); low_s = np.zeros((2, L)); hi_s = np.zeros((2, L)); br = np.zeros((2, L)); vo = np.zeros((2, L)); fx = np.zeros((2, L))
    for bar in range(BARS):
        sec = bar // 8                                             # 0:A 1:B 2:C 3:D
        ch = chord_of(bar); r, th, fi = CH[ch]
        root2, fifth2 = hz(r + '2'), hz(fi + '2') if NOTE[fi] > NOTE[r] else hz(fi + '3')
        # 太鼓：1・(2の裏)・3・4 … D の さいごの 2小節は 連打
        for b, g in ((0, 1.0), (1.5, 0.55), (2, 0.85), (3, 0.6)):
            if sec == 3 and bar % 8 >= 6: continue
            put(drums, taiko(rng, 1.0 if b in (0, 2) else 0.8), tb(bar, b), rng.uniform(-0.1, 0.1), g * (0.9 if sec == 0 else 1.0))
        if sec == 3 and bar % 8 >= 6:
            k = bar % 8 - 6
            for i in range(8): put(drums, taiko(rng, 0.7), tb(bar, i * 0.5), rng.uniform(-0.2, 0.2), 0.45 + 0.07 * (i + 8 * k))
        if bar % 4 == 3 and sec != 3:                             # 4小節ごとの おかず（中太鼓）
            for i, f0 in enumerate((180, 150, 125, 105)): put(drums, tom(rng, f0), tb(bar, 2 + i * 0.5), -0.4 + 0.27 * i, 0.55)
        if sec in (1, 2):                                          # 小太鼓（2・4拍）・シャカシャカ（16分）
            for b in (1, 3): put(drums, snare(rng), tb(bar, b), 0.15, 0.42)
            for i in range(16): put(drums, shaker(rng), tb(bar, i * 0.25), 0.45, 0.10 if i % 2 else 0.16)
        if sec == 3 and bar % 8 >= 6:                              # 小太鼓の ロール（だんだん 大きく）
            k = bar % 8 - 6
            for i in range(16): put(drums, snare(rng, 0.6), tb(bar, i * 0.25), 0.1, 0.12 + 0.02 * (i + 16 * k))
        if bar % 8 == 0 and bar > 0 or bar == 0:                   # シンバル（区切りの 頭：A の 頭は 小さく）
            put(drums, crash(rng), tb(bar), -0.3, 0.30 if bar == 0 else 0.42)
            put(drums, crash(rng), tb(bar), 0.3, 0.30 if bar == 0 else 0.42)
        # 低い 弦（8分の きざみ）：D では 長く のばす
        if sec != 3:
            pat = [root2, root2, root2 * 2, root2, root2, root2, fifth2, root2 * 2]
            for i, f in enumerate(pat): put(low_s, bass_note(f, BEAT * 0.48, rng), tb(bar, i * 0.5), 0.0, 0.95 if i % 2 == 0 else 0.75)
        else:
            put(low_s, bass_note(root2, BEAT * 3.9, rng), tb(bar), 0.0, 0.5)
        # 弦の 分散（16分）：A・B・C（D は さいごの 2小節 だけ）
        if sec != 3 or bar % 8 >= 6:
            tones = [hz(r + '4'), hz(fi + '3'), hz(th + '4'), hz(fi + '3')]
            if sec == 2: tones = [up(r + '4'), r + '4', up(th + '4'), fi + '4']; tones = [hz(x) for x in tones]
            for i in range(16):
                f = tones[i % 4]; acc = 1.0 if i % 4 == 0 else 0.7
                put(hi_s, string_note(f, BEAT * 0.22, rng), tb(bar, i * 0.25), -0.35 if i % 2 else 0.35, acc * (0.55 if sec == 0 else 0.5))
        # 金管の テーマ（B：そのまま・C：1オクターブ 上 ＋ そのまま を うすく）
        if sec in (1, 2):
            at = 0.0
            for nn, d in MELODY[bar % 8]:
                f = hz(nn)
                put(br, brass_note(f, d * BEAT * 0.96, rng, 1.0), tb(bar, at), -0.1, 0.62 if sec == 1 else 0.40)
                if sec == 2: put(br, brass_note(f * 2, d * BEAT * 0.96, rng, 1.2), tb(bar, at), 0.12, 0.46)
                at += d
            if sec == 1: put(br, 0.5 * brass_note(hz(r + '3'), BEAT * 3.8, rng, 0.8), tb(bar), 0.3, 0.30)      # 下の 金管（和音の 根）
        # 声の 和音（C・D）
        if sec in (2, 3):
            fs = [hz(r + '3'), hz(th + ('4' if NOTE[th] < NOTE[r] else '3')), hz(fi + '3' if NOTE[fi] > NOTE[r] else fi + '4')]
            put(vo, choir(fs, BEAT * 4.3, rng), tb(bar), 0.0, 0.55 if sec == 3 else 0.42)
    # D の さいごに 吸いこむ 音（A の 頭へ）
    put(fx, riser(rng, BEAT * 8), tb(BARS - 2), 0.0, 0.35)
    hp = lambda x, fc: np.stack([signal.lfilter(*signal.butter(2, fc / (SR / 2), 'high'), np.tile(x[c], 3))[L:2 * L] for c in range(2)])      # 低すぎる 音を へらす（くり返せる 形）
    # ひびき（くり返せる 形：しっぽを 頭に 回してから、3回 ならべて ひびかせ まん中を 取る）
    fold = lambda x: x[:, :NL] + np.pad(x[:, NL:], ((0, 0), (0, NL - (L - NL))))
    ir = reverb_ir(196, rt=1.9, pre=0.025, dark=6000)
    def wet(x, mix):
        out = np.zeros_like(x)
        for c in range(2):
            y = signal.fftconvolve(np.tile(x[c], 3), ir[c])[:3 * NL]
            out[c] = x[c] + mix * y[NL:2 * NL]
        return out
    pt = {'drums': wet(fold(hp(drums, 75)), 0.16), 'low': wet(fold(hp(low_s, 55)), 0.12), 'hi': wet(fold(hi_s), 0.30), 'brass': wet(fold(br), 0.34), 'choir': wet(fold(vo), 0.45), 'fx': wet(fold(fx), 0.2)}
    gain = {'drums': 0.50, 'low': 0.40, 'hi': 0.90, 'brass': 0.62, 'choir': 0.36, 'fx': 0.5}
    mix = sum(pt[k] * gain[k] for k in pt); mix = mix - mix.mean(axis=1, keepdims=True)
    mix = np.tanh(mix * 1.2) / 1.2                                 # 山を やわらかく そろえる
    g = min(PEAK / np.abs(mix).max(), RMS / np.sqrt(np.mean(mix ** 2)))      # ふつうの 大きさ RMS（山は PEAK を こえない）
    return (mix * g, {k: pt[k] * gain[k] * g for k in pt}) if parts else mix * g


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
        print(f'できた：{FILE} {os.path.getsize(o)} B・1回り {LOOP:.3f}秒（前後に {PRE}秒ずつ）・山 {np.abs(x).max():.2f}・ふつうの 大きさ（RMS）{np.sqrt(np.mean(x ** 2)):.4f} → {OUT}')
