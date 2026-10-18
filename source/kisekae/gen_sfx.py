"""的中ボタン・デカ的中ボタン・ど的中ボタン（フリーズ的中ボタン）の効果音。音は全部ここで合成する（録音や、ほかの音のデータは使わない）
   python3 gen_sfx.py <出力フォルダ>
   → sfx_hit_push.wav・sfx_hit.wav（的中）／sfx_big_push.wav・sfx_big.wav（デカ）／sfx_fz_push.wav・sfx_fz.wav（ど的中＝フリーズ）
     *_push＝PUSHが出たとき（当たりのお知らせ）。それ以外＝PUSHを押してから（0秒＝押した瞬間）。44.1kHz・16bit・ステレオ
     ＋ sfx_wave.json（音の大きさの形・1/50秒ごと。効果音のメモ Fx_Sound.dc.html の波形に使う。gen_fx.py と同じフォルダに置く）
   秒は見本の動き（gen_fx.py）に合わせる。フリーズは gen_fx.py の FZ_T（時刻）と GL_SCRIPT（バグるコマ）をそのまま読む
   乱数の種が決まっているので、何回作っても同じ音になる
   アプリ・見本に入れるとき（AAC 160kbps）：ffmpeg -i sfx_hit.wav -c:a aac -b:a 160k -movflags +faststart sfx_hit.m4a
   （見本のキャンバスは .m4a を受け付けないので、中身は同じで名前だけ .mp4 にして入れている）"""
import os, sys, ast, wave, json
import numpy as np
from scipy import signal

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))


def read_fx_times():
    """gen_fx.py から FZ_T と GL_SCRIPT を読む（見本の動きと音の時刻をそろえるため）"""
    tree = ast.parse(open(f'{HERE}/gen_fx.py', encoding='utf-8').read())
    fz = gl = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'FZ_T':
                fz = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            elif node.targets[0].id == 'GL_SCRIPT':
                gl = ast.literal_eval(node.value)
    return fz, gl


# ---------- 部品 ----------
def n_(d):
    return max(1, int(round(d * SR)))


def mtof(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def tl(n):
    return np.arange(n) / SR


def fade(x, a=.002, r=.012):
    x = np.array(x, dtype=float)
    na, nr = min(len(x), n_(a)), min(len(x), n_(r))
    if na > 1:
        x[:na] *= .5 - .5 * np.cos(np.linspace(0, np.pi, na))
    if nr > 1:
        x[-nr:] *= .5 + .5 * np.cos(np.linspace(0, np.pi, nr))
    return x


def env(n, a=.003, tau=.3, hold=0.0):
    """立ち上がり a 秒（直線）→ hold 秒そのまま → 指数で減る（tau 秒で 1/e）"""
    t = tl(n)
    e = np.exp(-np.maximum(t - a - hold, 0) / tau)
    return e * np.minimum(t / a, 1) if a > 0 else e


def phase(f, n):
    f = np.full(n, float(f)) if np.ndim(f) == 0 else np.asarray(f, dtype=float)[:n]
    return 2 * np.pi * np.cumsum(f) / SR


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def saw(f, n, dark=0.0, nh=40, odd=0.0):
    """倍音を足して作るのこぎり波（高い音でも折り返しノイズが出ない）。dark＝こもり具合（0＝明るい。時間で変えるとフィルターのように動く）。odd＞0で四角い音に近づく"""
    ph = phase(f, n)
    fmax = float(np.max(f)) if np.ndim(f) else float(f)
    kmax = max(1, min(nh, int(.45 * SR / max(fmax, 1.0))))
    dk = np.full(n, float(dark)) if np.ndim(dark) == 0 else np.asarray(dark, dtype=float)[:n]
    x = np.zeros(n)
    for k in range(1, kmax + 1):
        w = (1 + odd) if k % 2 else (1 - odd)
        x += w / k * np.exp(-(k - 1) * dk) * np.sin(k * ph)
    return x


def nsweep(d, f0, f1, bw, rng):
    """ザーッという音（ノイズ）の高さを f0 → f1 に動かす（ヒュー・シュワーン）。bw＝幅（オクターブ）"""
    n = n_(d)
    x = rng.standard_normal(n + 4096)
    f, tt, z = signal.stft(x, fs=SR, nperseg=1024, noverlap=768)
    fc = f0 * (f1 / f0) ** np.clip(tt / d, 0, 1)
    m = np.exp(-.5 * ((np.log2(np.maximum(f, 20))[:, None] - np.log2(fc)[None, :]) / bw) ** 2)
    _, y = signal.istft(z * m, fs=SR, nperseg=1024, noverlap=768)
    y = y[:n]
    return y / (np.std(y) + 1e-9)


# ---------- 楽器 ----------
def bell(f, d=1.0, ratio=3.5, idx=2.4, tau=.5, itau=.12, glock=.3):
    """キラーン・ピン：FMの鐘（高い音ほど変調を弱くして、耳に痛い音を出さない）"""
    n = n_(d)
    t = tl(n)
    idx = min(idx, max(.15, (16000 - f) / (f * ratio) - 1))
    i = idx * (.8 * np.exp(-t / itau) + .2 * np.exp(-t / tau))
    x = np.sin(2 * np.pi * f * t + i * np.sin(2 * np.pi * f * ratio * t))
    if glock and f * 2.76 < 16000:
        x = x + glock * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / (tau * .35))
    return fade(x * env(n, .0015, tau), .0015, .02)


def coin(f, rng, d=.5, bounce=True):
    """チャリン：金属のふぞろいな倍音＋当たる音（2回はねる）"""
    n = n_(d)
    t = tl(n)
    x = np.zeros(n)
    for r, a, tau in ((1, 1, .2), (1.47, .55, .11), (2.13, .4, .07), (2.76, .25, .05)):
        fr = f * r * (1 + rng.uniform(-.004, .004))
        if fr < 16000:
            x += a * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    x += .35 * hp(rng.standard_normal(n), 4000) * np.exp(-t / .002)
    if bounce:
        k = n_(rng.uniform(.035, .06))
        x[k:] += .4 * x[:n - k]
    return fade(x, .0008, .02)


def pop(f0=520, f1=260, d=.14, rng=None, noise=.25):
    """ポン（押した音）"""
    n = n_(d)
    t = tl(n)
    f = f1 + (f0 - f1) * np.exp(-t / .02)
    x = (np.sin(phase(f, n)) + .2 * np.sin(2 * phase(f, n))) * env(n, .001, .045)
    if noise:
        x += noise * bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t / .006)
    return fade(x, .0005, .02)


def kick(f0=150, f1=48, d=.5, drive=2.0, tau=.22, click=.3, rng=None):
    """ドン：音程が下がる低音＋少しひずませて、スマホのスピーカーでも聞こえるように"""
    n = n_(d)
    t = tl(n)
    f = f1 + (f0 - f1) * np.exp(-t / .035)
    x = np.tanh(drive * np.sin(phase(f, n)) * np.exp(-t / tau)) / np.tanh(drive)
    if click:
        x = x + click * hp(rng.standard_normal(n), 3000) * np.exp(-t / .003)
    return fade(x, .0005, .03)


def snare(rng, d=.25, tau=.07, tone=185):
    n = n_(d)
    t = tl(n)
    nz = bp(rng.standard_normal(n), 1200, 9000) * np.exp(-t / tau)
    tn = (.7 * np.sin(2 * np.pi * tone * t) + .35 * np.sin(2 * np.pi * tone * 1.72 * t)) * np.exp(-t / .045)
    return fade(.8 * nz + tn, .0005, .02)


def tom(f, rng, d=.32):
    n = n_(d)
    t = tl(n)
    x = np.sin(phase(f * (1 + .6 * np.exp(-t / .03)), n)) * np.exp(-t / .13)
    x = x + .25 * bp(rng.standard_normal(n), 300, 3000) * np.exp(-t / .02)
    return fade(np.tanh(1.6 * x) / np.tanh(1.6), .0005, .02)


def hat(rng, d=.06):
    n = n_(d)
    return fade(hp(rng.standard_normal(n), 7000) * np.exp(-tl(n) / .018), .0005, .01)


def crash(rng, d=2.0, tau=.65):
    """シャーン：金属の板（ふぞろいな四角い波を6つ重ねる）＋高いノイズ"""
    n = n_(d)
    t = tl(n)
    m = np.zeros(n)
    for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0):
        m += np.sign(np.sin(2 * np.pi * f * 1.6 * t + rng.uniform(0, 6.28)))
    m = hp(bp(m, 5500, 15000), 5000)
    nz = hp(rng.standard_normal(n), 5000)
    x = (.5 * m / 6 + .55 * nz) * np.exp(-t / tau) * np.minimum(t / .003, 1)
    return fade(x, .001, .15)


def pluck(m, d=.4, tau=.22, rng=None):
    """ピロ：すぐこもっていく明るいシンセ"""
    n = n_(d)
    t = tl(n)
    dk = .04 + .5 * (1 - np.exp(-t / .12))
    f = mtof(m)
    x = .6 * saw(f, n, dk) + .4 * saw(f * 1.003, n, dk, odd=.6)
    return fade(x * env(n, .002, tau), .002, .02)


def brass(m, d, rng, vib=True):
    """パーン：ブラス（3つの少しずれた音を重ねる・吹いた瞬間に明るくなる・あとで少しこもる・息の音）"""
    rel = .09
    n = n_(d + rel)
    t = tl(n)
    dk = .07 + .38 * np.exp(-t / .045) + .1 * (1 - np.exp(-t / .5))
    v = 1 + (.0045 * np.clip((t - .22) / .2, 0, 1) * np.sin(2 * np.pi * 5.6 * t) if vib else 0)
    x = np.zeros(n)
    for c in (-7, 0, 7):
        x += saw(mtof(m) * 2 ** (c / 1200) * v, n, dk, nh=36)
    a = np.minimum(t / .014, 1) * (1 + .3 * np.exp(-t / .06)) * np.clip((d + rel - t) / rel, 0, 1)
    breath = .25 * bp(rng.standard_normal(n), 1200, 3800) * np.exp(-t / .035)
    return fade(x / 3 * a + breath, .001, .02)


def stab(ms, d, rng, drive=1.8, sub=.5):
    """ジャン：パワーコードのシンセ（短い・ひずみ）"""
    n = n_(d)
    t = tl(n)
    dk = .03 + .32 * (1 - np.exp(-t / .1))
    x = np.zeros(n)
    for m in ms:
        for c in (-9, 9):
            x += saw(mtof(m) * 2 ** (c / 1200), n, dk, nh=32)
    x = x / (2 * len(ms))
    x = np.tanh(drive * x * env(n, .002, .17)) / np.tanh(drive)
    low = sub * np.sin(phase(mtof(min(ms) - 12), n)) * env(n, .002, .14)
    return fade(x + low, .001, .03)


def pad(ms, d, att=.2, rel=.4, dark=.33):
    """ふわーっと鳴る和音（ステレオに広げる）"""
    n = n_(d + rel)
    t = tl(n)
    a = np.minimum(t / att, 1) * np.clip((d + rel - t) / rel, 0, 1)
    out = np.zeros((n, 2))
    for i, m in enumerate(ms):
        for j, c in enumerate((-12, -4, 4, 12)):
            x = saw(mtof(m) * 2 ** (c / 1200), n, dark, nh=28) * a
            p = (j / 3 - .5) * .9 * (1 if i % 2 else -1)
            ang = (p + 1) * np.pi / 4
            out[:, 0] += x * np.cos(ang)
            out[:, 1] += x * np.sin(ang)
    return out / (len(ms) * 2.5)


def cuin(f0, f1, d, rise, rng):
    """キュイーン：すっと上がって、上でふるえる高い音（少しずつずらした3つ＋1オクターブ下）"""
    n = n_(d)
    t = tl(n)
    s = np.clip(t / rise, 0, 1)
    s = s * s * (3 - 2 * s)
    f = f0 * (f1 / f0) ** s
    vib = 1 + .011 * np.clip((t - rise) / .15, 0, 1) * np.sin(2 * np.pi * 6.5 * t)
    x = np.zeros(n)
    for c, a in ((-4, .5), (0, 1), (4, .5)):
        ph = phase(f * vib * 2 ** (c / 1200), n)
        x += a * (np.sin(ph) + .16 * np.sin(2 * ph))
    x += .25 * np.sin(phase(f * vib / 2, n))
    a = np.minimum(t / .012, 1) * np.where(t < rise + .22, 1, np.exp(-(t - rise - .22) / .3))
    return fade(x * a / 2.4, .002, .06)


def glitch(kind, d, rng):
    """バグる音：zip＝ジッ（荒いデジタルの粒）・buzz＝ブーッ（デジタルのうなり）・thud＝ブッ・tick＝チッ"""
    n = n_(d)
    t = tl(n)
    if kind == 'zip':
        h = int(rng.integers(12, 40))
        x = bp(np.repeat(rng.standard_normal(n // h + 1), h)[:n], 800, 7000)
    elif kind == 'buzz':
        f = rng.uniform(90, 420)
        x = lp(np.round((.6 * np.sign(np.sin(phase(f, n))) + .4 * np.sign(np.sin(phase(f * 2.01, n)))) * 4) / 4, 5000)
    elif kind == 'thud':
        x = lp(np.sign(np.sin(phase(rng.uniform(55, 90), n))) * np.exp(-t / .025), 1500)
    else:
        x = hp(rng.standard_normal(n), 3500) * np.exp(-t / .004)
    return fade(x, .001, .004)


def crackle(d, rate, rng):
    """ジジジ：静電気のパチパチ（短いノイズがばらばらに）"""
    n = n_(d)
    x = np.zeros(n)
    for _ in range(int(rng.poisson(rate * d))):
        i = int(rng.integers(0, max(1, n - 200)))
        k = int(rng.integers(20, 160))
        x[i:i + k] += rng.standard_normal(k)[:len(x[i:i + k])] * np.exp(-np.arange(k) / (k / 4))[:len(x[i:i + k])] * rng.uniform(.3, 1)
    return hp(x, 2500)


def crt_off(rng):
    """プチュン：「プ」（低いポン）＋「チュ」（高いノイズ）＋音程がいっきに下がる高い音（画面がつぶれる）＋「ン」（短いうなり）"""
    d = .45
    n = n_(d)
    t = tl(n)
    zip_ = np.sin(phase(380 + 6200 * np.exp(-t / .022), n)) * np.exp(-t / .06)
    chu = bp(rng.standard_normal(n), 2500, 9000) * np.exp(-np.maximum(t - .006, 0) / .018) * np.minimum(t / .006, 1)
    pu = np.sin(phase(70 + 160 * np.exp(-t / .02), n)) * np.exp(-t / .07)
    hum = (np.sin(phase(240, n)) + .4 * np.sin(phase(480, n))) * np.exp(-np.maximum(t - .03, 0) / .09) * np.minimum(t / .03, 1)
    click = hp(rng.standard_normal(n), 2000) * np.exp(-t / .0015)
    return fade(.5 * zip_ + .45 * chu + .7 * pu + .22 * hum + .45 * click, .0005, .05)


# ---------- まぜる ----------
class Mix:
    """音を時刻に置いて重ねる。rv＝残響に送る量・pan＝左右（-1 左〜1 右）"""

    def __init__(self, dur, seed):
        self.b = np.zeros((n_(dur), 2))
        self.r = np.zeros((n_(dur), 2))
        self.rng = np.random.default_rng(seed)

    def add(self, x, t, g=1.0, pan=0.0, rv=.2):
        x = np.asarray(x, dtype=float)
        if x.ndim == 1:
            p = pan if np.ndim(pan) == 0 else np.interp(np.arange(len(x)), np.linspace(0, len(x), len(pan)), pan)
            ang = (np.asarray(p) + 1) * np.pi / 4
            x = np.stack([x * np.cos(ang), x * np.sin(ang)], 1) * np.sqrt(2)
        i = n_(t) if t > 0 else 0
        j = min(len(self.b), i + len(x))
        if j > i:
            self.b[i:j] += g * x[:j - i]
            self.r[i:j] += g * rv * x[:j - i]

    def render(self, rt=1.5, damp=6500, target=-16.0, peak_db=-1.0):
        rng = np.random.default_rng(7)
        n = n_(rt * 1.3)
        t = tl(n)
        irs = []
        for _ in range(2):
            ir = lp(rng.standard_normal(n) * 10 ** (-3 * t / rt), damp, 1)
            ir = np.concatenate([np.zeros(n_(.015)), ir])
            irs.append(ir / np.sqrt((ir ** 2).sum()) * .5)
        wl = signal.fftconvolve(self.r[:, 0], irs[0])[:len(self.b)]
        wr = signal.fftconvolve(self.r[:, 1], irs[1])[:len(self.b)]
        x = master(self.b + np.stack([wl + .25 * wr, wr + .25 * wl], 1), peak_db)
        # 大きさをそろえる（LUFS）。ただし -1dB をこえるときは、こえない所まで
        g = min(10 ** ((target - lufs(x)) / 20), 10 ** (peak_db / 20) / (np.max(np.abs(x)) + 1e-12))
        return x * g


def biquad(kind, f0, q=.7071, gain_db=0.0):
    """RBJ のイコライザー（shelf_lo・shelf_hi・peak・hp）"""
    a_ = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    if kind == 'peak':
        b, a = [1 + al * a_, -2 * c, 1 - al * a_], [1 + al / a_, -2 * c, 1 - al / a_]
    elif kind == 'shelf_lo':
        sq = 2 * np.sqrt(a_) * al
        b = [a_ * ((a_ + 1) - (a_ - 1) * c + sq), 2 * a_ * ((a_ - 1) - (a_ + 1) * c), a_ * ((a_ + 1) - (a_ - 1) * c - sq)]
        a = [(a_ + 1) + (a_ - 1) * c + sq, -2 * ((a_ - 1) + (a_ + 1) * c), (a_ + 1) + (a_ - 1) * c - sq]
    elif kind == 'shelf_hi':
        sq = 2 * np.sqrt(a_) * al
        b = [a_ * ((a_ + 1) + (a_ - 1) * c + sq), -2 * a_ * ((a_ - 1) + (a_ + 1) * c), a_ * ((a_ + 1) + (a_ - 1) * c - sq)]
        a = [(a_ + 1) - (a_ - 1) * c + sq, 2 * ((a_ - 1) - (a_ + 1) * c), (a_ + 1) - (a_ - 1) * c - sq]
    else:
        b, a = [(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al]
    return np.array(b) / a[0], np.array(a) / a[0]


def lufs(x):
    """音の大きさ（ITU-R BS.1770 の LUFS：K特性・400msごと・-70と-10の門）"""
    y = x
    for kind, f0, q, g in (('shelf_hi', 1500, .7071, 4.0), ('hp', 38, .5, 0.0)):
        b, a = biquad(kind, f0, q, g)
        y = signal.lfilter(b, a, y, axis=0)
    blk, hop = n_(.4), n_(.1)
    z = np.array([np.mean(y[i:i + blk] ** 2, 0).sum() for i in range(0, max(1, len(y) - blk + 1), hop)])
    l = -.691 + 10 * np.log10(z + 1e-12)
    z = z[l > -70]
    if not len(z):
        return -70.0
    rel = -.691 + 10 * np.log10(z.mean()) - 10
    z = z[(-.691 + 10 * np.log10(z + 1e-12)) > rel]
    return float(-.691 + 10 * np.log10(z.mean()))


def master(x, peak_db=-1.0):
    """仕上げ：低すぎる音を切る → 低音を少し下げ、こもりを少し取り、輪郭を少し出す → まとめて少し圧縮（大きいところだけ下げる）→ 少しだけ丸める → いちばん大きい所を -1dB に"""
    x = np.stack([hp(x[:, c] - x[:, c].mean(), 30, 2) for c in range(2)], 1)
    for kind, f0, q, g in (('shelf_lo', 150, .7071, -3.0), ('peak', 320, 1.0, -2.0), ('peak', 2600, .9, 1.5)):
        b, a = biquad(kind, f0, q, g)
        x = signal.lfilter(b, a, x, axis=0)
    x = x / (np.max(np.abs(x)) + 1e-12)
    e = np.sqrt(np.maximum(lp(np.mean(x ** 2, 1), 15, 1), 1e-10))
    g = np.minimum(1.0, (.22 / e) ** (1 - 1 / 2.5))
    g = lp(np.concatenate([np.ones(2000), g]), 6, 1)[2000:]
    x = x * g[:, None]
    x = x / (np.max(np.abs(x)) + 1e-12)
    x = np.tanh(1.3 * x) / np.tanh(1.3)
    return x / (np.max(np.abs(x)) + 1e-12) * 10 ** (peak_db / 20)


def write_wav(path, x):
    y = np.clip(np.round(x * 32767), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())


def sparkle(mx, t0, dur, count, ms, g, rng, tau=(.12, .35)):
    """キラキラ：高い鐘の小さな音がばらばらに"""
    for _ in range(count):
        m = ms[int(rng.integers(0, len(ms)))]
        mx.add(bell(mtof(m), .6, idx=1.2, tau=rng.uniform(*tau), glock=.15), t0 + rng.uniform(0, dur), g * rng.uniform(.6, 1), rng.uniform(-.7, .7), rv=.35)


def coins(mx, t0, dur, count, g, rng, curve=1.6):
    """ジャラジャラ：コインがたくさん（はじめが多くて、だんだん少なく）"""
    for _ in range(count):
        mx.add(coin(rng.uniform(2800, 4600), rng, rng.uniform(.25, .45)), t0 + dur * rng.uniform(0, 1) ** curve, g * rng.uniform(.5, 1), rng.uniform(-.8, .8), rv=.25)


# ---------- 的中ボタン（ハ長調・明るく軽く） ----------
def sfx_hit_push():
    """PUSHが出たとき：ピロリン↑"""
    mx = Mix(1.4, 11)
    for i, m in enumerate((79, 84, 88)):          # G5 → C6 → E6
        mx.add(bell(mtof(m), 1.0, idx=2.0, tau=.32 + .1 * i), .075 * i, .5, (-.3, 0, .3)[i], rv=.3)
    sparkle(mx, .2, .35, 4, (96, 100, 103), .08, mx.rng)
    return mx.render(1.2, target=-17)


def sfx_hit():
    """押してから：0 ポン → .25〜.8 ヒュイーン（馬が上がる）→ .95「的中！」キラーン → 1.15・1.3 買い目でピン・ポン → 1.6 合計でチャリーン
       （的中の見本：馬 .3秒〜・「的中！」.95秒・買い目 1.15秒から .15秒ごと・合計は 1.15＋.15×3秒）"""
    mx = Mix(2.9, 12)
    r = mx.rng
    mx.add(pop(520, 260, rng=r), 0, .9, rv=.1)
    w = nsweep(.75, 380, 3200, .32, r) * np.sin(np.linspace(0, np.pi, n_(.75))) ** 2
    mx.add(w, .22, .14, np.linspace(-.3, .3, 8), rv=.25)
    mx.add(fade(np.sin(phase(np.geomspace(mtof(48), mtof(60), n_(.6)), n_(.6))) * np.sin(np.linspace(0, np.pi, n_(.6)))), .3, .1, rv=.2)
    # 「的中！」
    for i, m in enumerate((72, 76, 79, 84)):
        mx.add(pluck(m, .6, .26), .95, .16, (-.3, -.1, .1, .3)[i], rv=.25)
    for i, m in enumerate((84, 88, 91)):
        mx.add(bell(mtof(m), 1.2, idx=2.2, tau=.5), .95 + .02 * i, .2, (-.25, 0, .25)[i], rv=.35)
    mx.add(kick(160, 60, .35, 1.4, .12, .15, r), .95, .35, rv=.05)
    sparkle(mx, 1.0, .4, 6, (96, 98, 100, 103, 105), .07, r)
    mx.add(pad((60, 64, 67, 72), 1.1, .15, .5), .95, .5, rv=.3)
    # 買い目：ピン・ポン（E6・G6）→ 合計：チャリーン（C7＋コイン）
    for t, m in ((1.15, 88), (1.3, 91)):
        mx.add(bell(mtof(m), .7, idx=1.6, tau=.3), t, .22, rv=.3)
        mx.add(coin(3400, r, .3, False), t, .1, rv=.2)
    mx.add(bell(mtof(96), 1.2, idx=1.4, tau=.55), 1.6, .26, rv=.4)
    mx.add(bell(mtof(91), 1.2, idx=1.4, tau=.5), 1.6, .14, .2, rv=.4)
    mx.add(coin(3000, r, .5), 1.6, .32, -.15, rv=.25)
    mx.add(coin(4200, r, .45), 1.66, .24, .25, rv=.25)
    return mx.render(1.3, target=-16)


# ---------- デカ的中ボタン（ニ長調・大きく） ----------
def sfx_big_push():
    """PUSHが出たとき：キュイーン！"""
    mx = Mix(1.9, 21)
    mx.add(cuin(740, 2350, 1.3, .26, mx.rng), 0, .55, rv=.35)
    sparkle(mx, .22, .7, 8, (86, 90, 93, 98, 102), .07, mx.rng)
    return mx.render(1.5, target=-16)


def sfx_big():
    """押してから：0 ポン → .18 ドーン（白く光る）→ .25〜.75 シャララララ↑（虹の光）→ .85 光の中から馬 → 1.5「デカ的中!!」パーン
       → 1.85 パ（IV）→ 2.0 パ（V）→ 2.2 パーーン（I）＋合計でコイン（買い目 1.75・1.9）"""
    mx = Mix(3.8, 22)
    r = mx.rng
    mx.add(pop(440, 200, .16, r, .35), 0, .8, rv=.1)
    mx.add(kick(130, 42, .7, 2.5, .33, .3, r), .18, .9, rv=.12)
    mx.add(crash(r, 2.0, .6), .18, .2, -.5, rv=.2)
    mx.add(crash(r, 2.0, .6), .18, .2, .5, rv=.2)
    scale = (74, 76, 78, 79, 81, 83, 85, 86, 88, 90, 91, 93, 95, 97, 98)       # D5〜D7（ニ長調）
    for i, m in enumerate(scale):
        mx.add(bell(mtof(m), .7, idx=1.8, tau=.28, glock=.2), .25 + .45 * i / len(scale), .13, -.7 + 1.4 * i / len(scale), rv=.4)
    sw = pad((62, 66, 69, 74), .62, .5, .25)
    mx.add(sw, .25, .5, rv=.3)
    mx.add(nsweep(.62, 600, 5200, .35, r) * np.linspace(0, 1, n_(.62)) ** 2, .25, .1, rv=.3)
    mx.add(nsweep(.5, 3200, 700, .4, r) * np.exp(-tl(n_(.5)) / .15), .85, .1, rv=.3)
    # ファンファーレ
    for t, m in ((1.29, 69), (1.36, 71), (1.43, 73)):                            # A4 B4 C#5（ためて）
        mx.add(brass(m, .055, r, False), t, .3, rv=.2)
    for t, ch, d, g in ((1.5, (62, 69, 74, 78, 81), .3, .34), (1.85, (67, 71, 74, 79), .11, .3), (2.0, (69, 73, 76, 81), .11, .3),
                        (2.2, (62, 69, 74, 78, 81, 86), .85, .32)):
        for i, m in enumerate(ch):
            mx.add(brass(m, d, r), t, g, (i / max(1, len(ch) - 1) - .5) * .7, rv=.25)
    for t in (1.5, 2.2):
        mx.add(kick(120, 45, .5, 2.0, .2, .2, r), t, .6, rv=.08)
        mx.add(crash(r, 1.8, .55), t, .2, -.4, rv=.25)
        mx.add(crash(r, 1.8, .55), t, .2, .4, rv=.25)
    for i, m in enumerate((86, 90, 93)):
        mx.add(bell(mtof(m), 1.0, idx=2.0, tau=.45), 1.5 + .02 * i, .17, (-.3, 0, .3)[i], rv=.35)
    for t, m in ((1.75, 90), (1.9, 93)):                                      # 買い目
        mx.add(bell(mtof(m), .6, idx=1.5, tau=.28), t, .18, rv=.3)
        mx.add(coin(3500, r, .3, False), t, .1, rv=.2)
    mx.add(bell(mtof(98), 1.3, idx=1.3, tau=.6), 2.2, .24, rv=.45)               # 合計
    coins(mx, 2.2, .9, 14, .2, r)
    mx.add(pad((62, 66, 69, 74), 1.1, .3, .6), 2.2, .3, rv=.3)
    return mx.render(1.5, target=-15)


# ---------- ど的中ボタン（フリーズ・ホ長調・いちばん派手） ----------
def sfx_fz_push():
    """PUSHが出たとき：ドゥン＋重いギュイイイン！＋キラキラ"""
    mx = Mix(2.4, 31)
    r = mx.rng
    mx.add(kick(90, 38, .9, 2.6, .5, .2, r), 0, .65, rv=.15)
    mx.add(cuin(520, 2640, 1.7, .36, r), 0, .5, -.1, rv=.35)
    mx.add(cuin(260, 1320, 1.7, .36, r), .01, .28, .1, rv=.3)
    mx.add(crash(r, 1.8, .5), .02, .12, 0, rv=.3)
    sparkle(mx, .3, 1.0, 12, (88, 92, 95, 100, 104, 107), .07, r)
    return mx.render(1.6, target=-15)


def sfx_fz():
    """押してから（秒は gen_fx.py の FZ_T）：
       0〜E バグる音（GL_SCRIPT のコマごとに ジッ・ブッ・チッ・色ずれのうなり）→ C アイコンのドアップでヴォン → H 光の筋がシュイーン
       → E 青い画面でジジジ（静電気）と高い音が上がる → W プチュン → 線のジジ → Z 線が縮んでシュン → 真っ暗（無音）
       → M ドン！→「とんでも！」1文字ずつダダダダ＋「！」でジャン（E → F# → G# → A と上がる）→ M＋2.2 白い光でシャーン
       →「ど！」×4（B のコードで上がる・スネアの連打とせり上がる音）→ M＋3.4「ど的中！！！！」でジャーン!!（E）＋光の波に合わせて .45秒ごとのリズム
       → R 結果：パッパッパーン＋コインがジャラジャラ → R＋.6「フリーズ的中!!!」キラーン → 買い目 R＋.85〜 → 合計 R＋1.3 チャリーン"""
    fz, gl = read_fx_times()
    C, H, E, W, Z, M, R = (fz[k] for k in 'CHEWZMR')
    mx = Mix(R + 3.4, 32)
    r = mx.rng
    # --- バグる（0〜E） ---
    mx.add(kick(110, 40, .4, 3.0, .15, .4, r), 0, .7, rv=.1)
    mx.add(glitch('zip', .08, r), 0, .5, rv=.1)
    for t0, t1, fx in gl:
        d = max(.02, t1 - t0)
        for f in fx.split():
            v = float(f[1:]) if len(f) > 1 else 0
            if f[0] == 'S':
                rb = np.random.default_rng(int(v * 7 + 3))
                mx.add(glitch('buzz', d, rb), t0, .1 + .008 * v, rv=.05)
            elif f[0] == 'L':
                mx.add(glitch('zip', min(d, .05), r), t0, .35 + v / 120, r.uniform(-.6, .6), rv=.08)
            elif f[0] == 'B':
                mx.add(glitch('thud', min(d, .05), r), t0, .5, rv=.05)
            elif f[0] == 'T':
                mx.add(glitch('tick', .02, r), t0, .45, r.uniform(-.5, .5), rv=.05)
    # アイコンのドアップ（C〜E）：ヴォン（電気のうなり）
    n = n_(E - C)
    hum = bp(saw(55, n, .15) + .5 * saw(110.5, n, .2), 80, 1800) * np.minimum(tl(n) / .03, 1) * np.clip((E - C - tl(n)) / .05, 0, 1)
    mx.add(fade(hum), C, .22, rv=.1)
    mx.add(fade(np.sin(phase(np.geomspace(1300, 180, n_(.12)), n_(.12))) * np.exp(-tl(n_(.12)) / .05)), C, .3, rv=.15)
    # 光の筋（H〜E）：シュイーン（左から右へ）
    wd = E - H + .05
    mx.add(nsweep(wd, 1500, 6500, .3, r) * np.sin(np.linspace(0, np.pi, n_(wd))), H, .14, np.linspace(-.8, .8, 8), rv=.2)
    mx.add(fade(np.sin(phase(np.geomspace(800, 3000, n_(wd)), n_(wd))) * np.sin(np.linspace(0, np.pi, n_(wd)))), H, .06, rv=.2)
    # 青い画面（E〜W）：ジジジ＋上がる高い音＋白い光がふくらむ
    d = W - E
    mx.add(crackle(d, 130, r), E, .4, rv=.15)
    wh = np.sin(phase(np.geomspace(1800, 6000, n_(d)), n_(d)) + .4 * np.sin(2 * np.pi * 37 * tl(n_(d)))) * np.linspace(.2, 1, n_(d))
    mx.add(fade(wh), E, .1, rv=.2)
    mx.add(lp(r.standard_normal(n_(d)), 3000) * np.linspace(0, 1, n_(d)) ** 2, E, .06, rv=.2)
    # プチュン（W）→ 線のジジ → 縮んでシュン（Z）
    mx.add(crt_off(r), W, 1.6, rv=.25)
    mx.add(crackle(Z - W - .04, 55, r), W + .04, .2, rv=.2)
    sd = .2
    mx.add(fade(np.sin(phase(np.geomspace(2600, 500, n_(sd)), n_(sd))) * np.exp(-tl(n_(sd)) / .08)), Z, .25, rv=.25)
    # --- 真っ暗（Z＋.3〜M）は無音 ---
    # --- ネオンのカット（M〜R） ---
    mx.add(kick(120, 38, .9, 3.0, .45, .3, r), M, 1.0, rv=.15)
    mx.add(crash(r, 1.6, .5), M, .2, -.5, rv=.25)
    mx.add(crash(r, 1.6, .5), M, .2, .5, rv=.25)
    mx.add(stab((52, 59, 64), .45, r), M, .45, rv=.25)
    cuts = (((M + .08 + .06 * i for i in range(5)), 52), ((M + .8 + .06 * i for i in range(5)), 54),
            ((M + 1.5 + .045 * i for i in range(5)), 56), ((M + 1.72 + .045 * i for i in range(5)), 57))
    for k, (times, root) in enumerate(cuts):
        times = list(times)
        for i, t in enumerate(times[:4]):                                          # と・ん・で・も
            mx.add(tom(mtof(root - 12 + 2 * i), r), t, .38, (-.4, -.15, .15, .4)[i], rv=.12)
            mx.add(glitch('zip', .03, r), t, .12, r.uniform(-.5, .5), rv=.05)
        tx = times[4]                                                               # ！
        mx.add(stab((root, root + 7, root + 12), .38, r), tx, .5, (-.2, .2, -.1, .1)[k], rv=.25)
        mx.add(kick(130, 45, .45, 2.4, .2, .25, r), tx, .65, rv=.08)
        mx.add(crash(r, .6, .2), tx, .08, (-.4, .4, -.3, .3)[k], rv=.2)
    # 下で鳴る低いうなり（コードに合わせて E → F# → G# → A → B）・8分で刻む
    roots = ((M, 40), (M + .8, 42), (M + 1.5, 44), (M + 1.72, 45), (M + 2.2, 47))
    g0 = M + 2.34 - 10 * .22
    for k in range(15):
        t = g0 + .22 * k
        if t >= M + 3.4 - .05:
            break
        rt = [m for s, m in roots if s <= t + 1e-6][-1]
        mx.add(stab((rt, rt + 7), .2, r, 1.2, 0), t, .1 + .008 * k, rv=.1)
    # 白い光（M＋2.2）：シャーン＋キラキラ↑ →「ど！」×4（B）
    mx.add(crash(r, 1.4, .45), M + 2.2, .18, -.4, rv=.3)
    mx.add(crash(r, 1.4, .45), M + 2.2, .18, .4, rv=.3)
    for i, m in enumerate((83, 87, 90, 95, 99, 102, 107)):
        mx.add(bell(mtof(m), .5, idx=1.6, tau=.25, glock=.2), M + 2.2 + .025 * i, .1, -.6 + .2 * i, rv=.4)
    for i, ch in enumerate(((47, 54, 59), (51, 54, 59, 63), (54, 59, 63, 66), (59, 63, 66, 71))):
        t = M + 2.34 + .22 * i
        mx.add(stab(ch, .2, r, 2.2), t, .48 + .05 * i, rv=.2)
        mx.add(kick(140, 48, .35, 2.6, .14, .3, r), t, .7, rv=.06)
        mx.add(snare(r, .2, .06), t, .25, rv=.15)
    t = M + 3.0
    while t < M + 3.38:                                                             # スネアの連打（だんだん速く・大きく）
        u = (t - M - 3.0) / .4
        mx.add(snare(r, .12, .04), t, .12 + .25 * u, r.uniform(-.2, .2), rv=.15)
        t += .055 - .03 * u
    rd = 1.2
    mx.add(nsweep(rd, 500, 8000, .35, r) * np.linspace(0, 1, n_(rd)) ** 2, M + 2.2, .2, rv=.3)
    mx.add(fade(np.sin(phase(np.geomspace(mtof(59), mtof(83), n_(rd)), n_(rd))) * np.linspace(0, 1, n_(rd))), M + 2.2, .06, rv=.3)
    # 「ど的中！！！！」（M＋3.4）：ジャーン!!（E）
    T5 = M + 3.4
    mx.add(kick(110, 36, 1.0, 3.0, .5, .3, r), T5, 1.0, rv=.2)
    mx.add(crash(r, 2.2, .8), T5, .28, -.5, rv=.35)
    mx.add(crash(r, 2.2, .8), T5, .28, .5, rv=.35)
    for i, m in enumerate((52, 59, 64, 68, 71, 76)):
        mx.add(brass(m, 1.4, r), T5, .32, (i / 5 - .5) * .8, rv=.3)
    mx.add(pad((64, 68, 71, 76), 1.7, .2, .5), T5, .3, rv=.35)
    mx.add(bell(mtof(88), 1.2, idx=2.2, tau=.5), T5 + .02, .24, rv=.4)
    for i, m in enumerate((92, 95, 100, 104)):                                     # ！×4
        mx.add(bell(mtof(m), .9, idx=1.6, tau=.4), T5 + .08 + .06 * i, .2, (-.45, -.15, .15, .45)[i], rv=.4)
    # 光の波（.45秒ごと）に合わせたリズムと、ピロピロ（16分）
    k = 1
    while T5 + .45 * k < R - .1:
        tb = T5 + .45 * k
        mx.add(kick(120, 45, .35, 2.0, .15, .2, r), tb, .35, rv=.06)
        mx.add(pad((64, 68, 71), .3, .03, .2, .25), tb, .2, rv=.25)
        k += 1
    arp = (76, 80, 83, 88, 83, 80)
    j = 0
    while T5 + .2 + .1125 * j < R - .05:
        tj = T5 + .2 + .1125 * j
        mx.add(pluck(arp[j % len(arp)] + 12 * (j // 12 % 2), .25, .1), tj, .13, (-.3, .3)[j % 2], rv=.3)
        if j % 2:
            mx.add(hat(r), tj, .1, rv=.05)
        j += 1
    # --- 結果（R）：パッパッパーン＋コイン → 「フリーズ的中!!!」キラーン → 買い目 → 合計 チャリーン ---
    mx.add(kick(120, 40, .8, 2.6, .4, .3, r), R, .9, rv=.15)
    for i, m in enumerate((88, 92, 95, 100, 104, 107)):
        mx.add(bell(mtof(m), .6, idx=1.5, tau=.3, glock=.2), R + .02 * i, .12, -.5 + .2 * i, rv=.4)
    for t, m in ((R, 76), (R + .09, 80), (R + .18, 83)):
        mx.add(brass(m, .07, r, False), t, .34, rv=.2)
    for i, m in enumerate((64, 71, 76, 80, 83, 88)):
        mx.add(brass(m, 1.3, r), R + .27, .3, (i / 5 - .5) * .8, rv=.3)
    mx.add(crash(r, 2.0, .6), R + .27, .2, -.4, rv=.35)
    mx.add(crash(r, 2.0, .6), R + .27, .2, .4, rv=.35)
    mx.add(kick(110, 40, .6, 2.4, .3, .2, r), R + .27, .8, rv=.1)
    coins(mx, R + .1, 2.2, 40, .17, r, 1.8)
    mx.add(bell(mtof(95), 1.2, idx=2.0, tau=.5), R + .6, .24, -.2, rv=.4)
    mx.add(bell(mtof(100), 1.2, idx=1.6, tau=.5), R + .62, .2, .2, rv=.4)
    for t, m in ((R + .85, 92), (R + 1.0, 95), (R + 1.15, 100)):                   # 買い目
        mx.add(bell(mtof(m), .6, idx=1.4, tau=.28), t, .17, rv=.3)
    mx.add(bell(mtof(100), 1.4, idx=1.3, tau=.6), R + 1.3, .26, rv=.45)            # 合計
    mx.add(coin(3000, r, .5), R + 1.3, .3, -.2, rv=.25)
    mx.add(coin(4100, r, .45), R + 1.36, .22, .25, rv=.25)
    mx.add(pad((64, 68, 71, 76), 1.4, .3, .8), R + 1.3, .28, rv=.35)
    return mx.render(1.6, target=-14)


SOUNDS = (('sfx_hit_push', sfx_hit_push), ('sfx_hit', sfx_hit), ('sfx_big_push', sfx_big_push), ('sfx_big', sfx_big),
          ('sfx_fz_push', sfx_fz_push), ('sfx_fz', sfx_fz))

def wave_env(x, per_sec=50):
    """メモの波形：1/50秒ごとのいちばん大きい所（0〜1）の平方根（小さい音も見えるように。-6dB≒0.7・-20dB≒0.3・-40dB＝0.1）"""
    a = np.max(np.abs(x), 1)
    n = max(1, int(round(len(a) / SR * per_sec)))
    ed = np.linspace(0, len(a), n + 1).astype(int)
    pk = np.array([a[ed[i]:ed[i + 1]].max() if ed[i + 1] > ed[i] else 0.0 for i in range(n)])
    return [round(float(v), 2) for v in np.sqrt(np.clip(pk, 0, 1))]


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    waves = {}
    for name, fn in SOUNDS:
        x = fn()
        write_wav(f'{out}/{name}.wav', x)
        lu, pk = lufs(x), 20 * np.log10(np.max(np.abs(x)))
        waves[name] = dict(d=round(len(x) / SR, 2), lufs=round(lu, 1), peak=round(float(pk), 1), h=wave_env(x))
        print(f'{name}.wav  {len(x) / SR:.2f}秒  {lu:.1f} LUFS  ピーク {pk:.1f}dB')
    with open(f'{out}/sfx_wave.json', 'w', encoding='utf-8') as f:
        json.dump(waves, f, separators=(',', ':'))
    print('sfx_wave.json')
