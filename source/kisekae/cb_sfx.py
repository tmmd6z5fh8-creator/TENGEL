# 馬カードバトルの 効果音（第4.176版）：ぜんぶ 計算で 作る（録音・よその 音は 使わない）
#   python3 kisekae/cb_sfx.py            … ios/cb_assets/cb_se_<名前>.m4a（アプリに 入れる 形：モノラル 44.1kHz・AAC 96kbps）
#   python3 kisekae/cb_sfx.py wav <出す フォルダ>   … wav（聞いて 確かめる 用）
#   音（cb/cb_app.js の SE と 同じ 名前）：
#     deal（配る：シャッ×5）・set（カードを 置く：トン）・flip（めくる：シュッ パッ）・win（ターンに 勝った：明るい 3つの 音）・lose（ターンに 負けた：下がる 2つの 音）・
#     even（かぶり・引き分け・同点：コン コン）・magic（効果：キラキラ 上がる）・tap（ボタン：チッ）・fanfare（対戦に 勝った：ファンファーレ）・over（対戦に 負けた：しずむ 音）・join（友だちと つながった：ピンポン）
#   大きさ（山）：アプリの ほかの 音（ピロン 0.23・デデーン 0.36）と ならぶ ぐらい（下の PEAK）
import os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
SR = 44100
NAMES = ['deal', 'set', 'flip', 'win', 'lose', 'even', 'magic', 'tap', 'fanfare', 'over', 'join']
PEAK = {'deal': 0.26, 'set': 0.30, 'flip': 0.27, 'win': 0.33, 'lose': 0.30, 'even': 0.30, 'magic': 0.27, 'tap': 0.16, 'fanfare': 0.40, 'over': 0.34, 'join': 0.30}


def files():
    """アプリに 入れる 音の 名前（build_ios.py・テストが 使う）"""
    return [f'cb_se_{n}.m4a' for n in NAMES]


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a, d, curve=4.0):
    """立ち上がり a 秒・そのあと 指数で 消える（n 点）"""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-curve * np.maximum(0, t - a) / max(d, 1e-4))


def band(x, lo, hi, order=2):
    sos = butter(order, [lo / (SR / 2), min(0.99, hi / (SR / 2))], btype='band', output='sos')
    return sosfilt(sos, x)


def low(x, hi, order=2):
    return sosfilt(butter(order, hi / (SR / 2), btype='low', output='sos'), x)


def put(buf, x, at):
    i = int(at * SR); n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n]


def bell(f, sec, parts=((1, 1.0), (2.0, 0.45), (3.01, 0.22), (4.2, 0.12)), decay=0.5):
    """鐘・グロッケンの ような 音：倍音ごとに 早く 消える"""
    t = t_(sec); y = np.zeros(len(t))
    for k, a in parts:
        y += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3.0 + 2.2 * k) / max(decay, 1e-3) * 0.5)
    return y * np.minimum(1, t / 0.004)


def brass(f, sec, bright=1.0):
    """金管の ような 音：のこぎり波を 低く こして、立ち上がりで 明るく"""
    t = t_(sec); y = np.zeros(len(t))
    for k in range(1, 13):
        y += np.sin(2 * np.pi * f * k * t + 0.3 * k) / k * np.exp(-0.18 * k / bright)
    e = np.minimum(1, t / 0.03) * np.minimum(1, (sec - t) / 0.08)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.2)
    return y * e * vib


def flick(rng, sec=0.07, lo=1800, hi=9000):
    """カードが こすれる 音（シャッ）"""
    n = int(sec * SR); x = band(rng.standard_normal(n), lo, hi)
    return x * env(n, 0.004, sec * 0.6, 5)


def snd_deal(rng):
    y = np.zeros(int(0.62 * SR))
    for i in range(5):
        put(y, flick(rng, 0.075, 1500 + 200 * i, 8000) * (0.8 + 0.2 * rng.random()), 0.02 + i * 0.105)
        put(y, 0.25 * low(rng.standard_normal(int(0.03 * SR)), 300) * env(int(0.03 * SR), 0.002, 0.02), 0.05 + i * 0.105)
    return y


def snd_set(rng):
    n = int(0.2 * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (150 * np.exp(-t * 18) + 70) * t) * env(n, 0.002, 0.09, 5)
    y = thud + 0.35 * band(rng.standard_normal(n), 900, 5000) * env(n, 0.002, 0.03, 5)
    return y


def snd_flip(rng):
    n = int(0.3 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # こす 高さが 上がって いく（シュッ）→ さいごに パッ
    y = np.zeros(n); seg = 512
    for i in range(0, n - seg, seg // 2):
        c = 700 + 5200 * (i / n) ** 1.3
        y[i:i + seg] += band(x[i:i + seg], c * 0.7, c * 1.5) * np.hanning(seg)
    y *= np.minimum(1, t / 0.02) * np.exp(-np.maximum(0, t - 0.17) * 30)
    put(y, 0.9 * band(rng.standard_normal(int(0.05 * SR)), 2500, 9000) * env(int(0.05 * SR), 0.001, 0.03, 5), 0.19)
    return y


def snd_win(rng):
    y = np.zeros(int(0.95 * SR))
    for i, f in enumerate((783.99, 987.77, 1174.66, 1567.98)):      # ソ・シ・レ・ソ（明るく 上がる）
        put(y, bell(f, 0.6, decay=0.55) * (0.8 if i < 3 else 1.0), i * 0.085)
    return y


def snd_lose(rng):
    y = np.zeros(int(0.8 * SR))
    for i, f in enumerate((392.0, 311.13)):                          # ソ → ミ♭（下がる）
        put(y, bell(f, 0.55, parts=((1, 1.0), (2.0, 0.3), (3.0, 0.1)), decay=0.7), i * 0.2)
    return low(y, 2600)


def snd_even(rng):
    y = np.zeros(int(0.5 * SR))
    for i in range(2):                                               # コン コン（木を たたく ような 同じ 高さ）
        n = int(0.16 * SR); t = np.arange(n) / SR
        k = np.sin(2 * np.pi * 520 * t) * env(n, 0.001, 0.06, 5) + 0.5 * np.sin(2 * np.pi * 1310 * t) * env(n, 0.001, 0.03, 5)
        put(y, k, 0.02 + i * 0.17)
    return y


def snd_magic(rng):
    y = np.zeros(int(0.8 * SR))
    notes = (1046.5, 1318.5, 1568.0, 2093.0, 2637.0, 3136.0)         # ド・ミ・ソ・ド・ミ・ソ（上へ）
    for i, f in enumerate(notes):
        put(y, bell(f, 0.45, parts=((1, 1.0), (2.0, 0.25), (3.0, 0.08)), decay=0.4) * (0.6 + 0.07 * i), i * 0.055)
    n = len(y); sh = band(rng.standard_normal(n), 6000, 12000) * env(n, 0.05, 0.5, 3) * 0.12
    return y + sh


def snd_tap(rng):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1900 * t) * env(n, 0.001, 0.02, 5) + 0.4 * band(rng.standard_normal(n), 3000, 9000) * env(n, 0.001, 0.008, 5)


def snd_fanfare(rng):
    y = np.zeros(int(1.75 * SR))
    seq = ((523.25, 0.0, 0.16), (659.25, 0.15, 0.16), (783.99, 0.30, 0.16), (1046.5, 0.45, 0.30), (783.99, 0.74, 0.14), (1046.5, 0.88, 0.80))      # ド ミ ソ ドー ソ ドーー
    for f, at, d in seq:
        put(y, brass(f, d + 0.06, 1.2), at)
        put(y, 0.5 * brass(f / 2, d + 0.06, 0.8), at)
    for f in (659.25, 783.99):                                       # さいごの 和音
        put(y, 0.55 * brass(f, 0.86, 1.0), 0.88)
    for i, f in enumerate((2093.0, 2637.0, 3136.0, 4186.0)):         # きらめき
        put(y, 0.22 * bell(f, 0.5, parts=((1, 1.0), (2.0, 0.2)), decay=0.4), 0.92 + i * 0.07)
    return low(y, 7000)


def snd_over(rng):
    y = np.zeros(int(1.3 * SR))
    for i, (f, d) in enumerate(((392.0, 0.3), (349.23, 0.3), (311.13, 0.3), (261.63, 0.7))):      # ソ ファ ミ♭ ドー（しずむ）
        put(y, bell(f, d + 0.25, parts=((1, 1.0), (2.0, 0.35), (3.0, 0.12)), decay=0.9), i * 0.2)
        put(y, 0.4 * bell(f / 2, d + 0.25, parts=((1, 1.0), (2.0, 0.2)), decay=0.9), i * 0.2)
    return low(y, 2400)


def snd_join(rng):
    y = np.zeros(int(0.75 * SR))
    put(y, bell(1318.5, 0.5, decay=0.6), 0.0)                        # ミ
    put(y, bell(1046.5, 0.6, decay=0.7), 0.16)                       # ド（ピン ポン）
    return y


def render():
    out = {}
    for i, name in enumerate(NAMES):
        y = globals()['snd_' + name](np.random.default_rng(1760 + i)).astype(np.float64)
        y = y - y.mean()
        y *= PEAK[name] / max(1e-9, float(np.abs(y).max()))
        nz = np.nonzero(np.abs(y) > 1e-4)[0]
        y = y[:min(len(y), nz[-1] + int(0.04 * SR))].copy()
        m = min(int(0.015 * SR), len(y)); y[-m:] *= np.linspace(1, 0, m)
        out[name] = y
    return out


if __name__ == '__main__':
    wav = len(sys.argv) > 1 and sys.argv[1] == 'wav'
    D = sys.argv[2] if wav and len(sys.argv) > 2 else OUT
    os.makedirs(D, exist_ok=True); tmp = tempfile.mkdtemp(); tot = 0
    for k, y in render().items():
        w = os.path.join(D if wav else tmp, f'cb_se_{k}.wav'); wavfile.write(w, SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
        o = w
        if not wav:
            o = os.path.join(D, f'cb_se_{k}.m4a')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-ac', '1', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', o], check=True)
        tot += os.path.getsize(o)
        print(k, round(len(y) / SR, 2), '秒', 'peak', round(float(np.abs(y).max()), 3), f'{os.path.getsize(o)} B', flush=True)
    print(f'できた：{len(NAMES)}こ・{tot / 1000:.1f}KB → {D}')
