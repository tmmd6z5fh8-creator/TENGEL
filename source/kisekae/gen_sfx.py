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
    """gen_fx.py から FZ_T・MT_T（ネオンのカットの時刻）と GL_SCRIPT を読む（見本の動きと音の時刻をそろえるため）"""
    tree = ast.parse(open(f'{HERE}/gen_fx.py', encoding='utf-8').read())
    fz = gl = mt = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'FZ_T':
                fz = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            elif node.targets[0].id == 'MT_T':
                mt = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            elif node.targets[0].id == 'GL_SCRIPT':
                gl = ast.literal_eval(node.value)
    return fz, gl, mt


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


def kyuin(f0, f1, d=.42, tau=.035, per=.16):
    """キュウィン：「キュ」とすばやく上がって少し行きすぎ、「ウィン」と鳴って消える明るいシンセ（パチスロの告知音のような）"""
    n = n_(d)
    t = tl(n)
    s = 1 - np.exp(-t / tau) * np.cos(2 * np.pi * t / per)          # 少し上へ行きすぎて戻る
    f = f0 * (f1 / f0) ** s
    f = f * (1 + .008 * np.clip((t - .14) / .08, 0, 1) * np.sin(2 * np.pi * 8 * t))
    dk = .12 + .45 * np.exp(-t / .03) + .25 * np.clip((t - .14) / .22, 0, 1)   # こもる → 開く（ウィ）→ 少しこもる（ン）
    x = (.5 * saw(f, n, dk, nh=24) + .3 * saw(f * 1.004, n, dk, nh=24, odd=.5)
         + .45 * np.sin(phase(f, n)) + .18 * np.sin(phase(f / 2, n)))
    a = np.minimum(t / .004, 1) * np.where(t < .16, 1, np.exp(-(t - .16) / .11))
    return fade(x * a / 1.3, .001, .04)


# ---------- 低音・重低音（ど的中） ----------
def boom(f0=95, f1=30, d=1.6, tau=.55, drop=.06, drive=2.2, rng=None, grit=.25, body=.7, click=.35):
    """ドォォン：重低音（音程がゆっくり下がって長く響く）＋1オクターブ上の「ドン」と、低い「ドッ」（空気の音）。
       ひずませて倍音を出し、スマホのスピーカー（重低音が出ない）でも低音を感じるように"""
    n = n_(d)
    t = tl(n)
    f = f1 + (f0 - f1) * np.exp(-t / drop)
    ph = phase(f, n)
    x = np.tanh(drive * np.sin(ph) * np.exp(-t / tau)) / np.tanh(drive)
    x = x + body * np.tanh(2.5 * np.sin(2 * ph) * np.exp(-t / (tau * .45))) / np.tanh(2.5)
    if grit and rng is not None:
        x = x + grit * bp(rng.standard_normal(n), 150, 1500) * np.exp(-t / .05) * 4
        x = x + click * bp(rng.standard_normal(n), 1200, 5000) * np.exp(-t / .004) * 3
    return fade(x, .001, .08)


def nlow(d, fc0, fc1, tau, rng):
    """ザーッという音（ノイズ）の、こもり具合を時間で変える：ローパスの境目が fc0 → fc1 へ（tau 秒で 1/e）"""
    n = n_(d)
    x = rng.standard_normal(n + 4096)
    f, tt, z = signal.stft(x, fs=SR, nperseg=1024, noverlap=768)
    fc = fc1 + (fc0 - fc1) * np.exp(-tt / tau)
    m = 1 / (1 + (np.maximum(f, 1)[:, None] / fc[None, :]) ** 4)
    _, y = signal.istft(z * m, fs=SR, nperseg=1024, noverlap=768)
    y = y[:n]
    return y / (np.std(y[:max(1, n_(.05))]) + 1e-9)


EX_MIX = (.6, .9, .6, .25, .35)    # 爆発の中身の大きさ：はじける音・爆風・重低音・地ひびき・かけら


def explosion(rng, size=1.0, pitch=1.0):
    """ドガーン：爆発。はじける音＋だんだんこもる爆風＋重低音のドスン＋長い地ひびき＋飛び散るかけら（size で大きさ・長さ。pitch で高さ）"""
    d = .6 + 1.4 * size
    n = n_(d)
    t = tl(n)
    crack = bp(rng.standard_normal(n), 300, 7000) * np.exp(-t / .012)
    blast = nlow(d, 4000, 250, .18 * size + .05, rng) * np.minimum(t / .003, 1) * np.exp(-t / (.35 * size + .08))
    f = (24 + 66 * np.exp(-t / .06)) * pitch
    sub = np.tanh(2.0 * np.sin(phase(f, n)) * np.exp(-t / (.22 * size + .06))) / np.tanh(2.0)
    rum = lp(rng.standard_normal(n), 140, 4)
    rum = rum / (np.std(rum) + 1e-9) * (.7 + .3 * np.sin(2 * np.pi * 9 * t)) * np.minimum(t / .06, 1) * np.exp(-t / (.7 * size + .1))
    deb = np.zeros(n)
    for _ in range(int(6 * size) + 2):
        i = int(rng.uniform(.04, .5 * size + .1) * SR)
        k = int(rng.integers(80, 400))
        if i + k < n:
            deb[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 5)) * rng.uniform(.3, 1)
    deb = bp(deb, 200, 2500)
    x = EX_MIX[0] * crack + EX_MIX[1] * blast + EX_MIX[2] * sub + EX_MIX[3] * rum + EX_MIX[4] * deb
    return fade(np.tanh(1.5 * x) / np.tanh(1.5), .0005, .1)


def growl(f0, f1, d, rise, drive=2.6):
    """グォォォン↑：低いうなり（少しずらした2つののこぎり波＋1オクターブ下）が上がりながら明るくなる"""
    n = n_(d)
    t = tl(n)
    s = np.clip(t / rise, 0, 1)
    s = s * s * (3 - 2 * s)
    f = f0 * (f1 / f0) ** s
    dk = .3 - .22 * s
    x = .5 * saw(f * 2 ** (-10 / 1200), n, dk, nh=60) + .5 * saw(f * 2 ** (10 / 1200), n, dk, nh=60) + .6 * np.sin(phase(f / 2, n))
    x = x + .5 * saw(f * 2, n, dk + .05, nh=40)
    x = np.tanh(drive * x) / np.tanh(drive)
    a = np.minimum(t / .05, 1) * np.where(t < rise + .1, 1, np.exp(-(t - rise - .1) / .35))
    return fade(x * a, .003, .08)


def gong(f, d=2.5, tau=1.0, rng=None):
    """ゴォーン：低いどら（ふぞろいな倍音が長く鳴る）"""
    n = n_(d)
    t = tl(n)
    x = np.zeros(n)
    for r, a, k in ((1, 1, 1), (1.48, .6, .8), (1.99, .5, .6), (2.57, .35, .45), (3.11, .25, .35), (3.73, .18, .25)):
        if f * r < 12000:
            x += a * np.sin(2 * np.pi * f * r * t + (rng.uniform(0, 6.28) if rng is not None else 0)) * np.exp(-t / (tau * k))
    x = x * np.minimum(t / .006, 1)
    if rng is not None:
        x = x + .3 * lp(rng.standard_normal(n), 1200) * np.exp(-t / .03)
    return fade(x / 2.2, .001, .1)


def lsnare(rng, d=.28, tau=.08, tone=110):
    """低いスネア（ドスッ）"""
    n = n_(d)
    t = tl(n)
    nz = bp(rng.standard_normal(n), 250, 2600) * np.exp(-t / tau)
    tn = (.8 * np.sin(2 * np.pi * tone * t) + .4 * np.sin(2 * np.pi * tone * 1.6 * t)) * np.exp(-t / .06)
    return fade(.7 * nz + tn, .0005, .02)


def lcrash(rng, d=2.0, tau=.6):
    """暗いシャーン（低めの金属の板＋こもったノイズ）"""
    n = n_(d)
    t = tl(n)
    m = np.zeros(n)
    for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0):
        m += np.sign(np.sin(2 * np.pi * f * .8 * t + rng.uniform(0, 6.28)))
    m = bp(m, 900, 5500)
    nz = bp(rng.standard_normal(n), 600, 4500)
    x = (.5 * m / 6 + .5 * nz) * np.exp(-t / tau) * np.minimum(t / .004, 1)
    return fade(x, .001, .15)


def rumble(d, rng, fc=160, am=14):
    """ゴゴゴ：地ひびき（こもったノイズを細かくゆらす＋とても低い音）"""
    n = n_(d)
    t = tl(n)
    x = lp(rng.standard_normal(n), fc, 4)
    x = x / (np.std(x) + 1e-9) * (.65 + .35 * np.sin(2 * np.pi * am * t + rng.uniform(0, 6.28)))
    x = x + .5 * np.sin(phase(36 + 4 * np.sin(2 * np.pi * .7 * t), n))
    g = bp(rng.standard_normal(n), 180, 700)
    x = x + .6 * g / (np.std(g) + 1e-9) * (.5 + .5 * np.sin(2 * np.pi * am * 1.5 * t)) ** 2
    return fade(x / 2, .05, .1)


def lglitch(kind, d, rng):
    """低いバグる音：zap＝ヴッ（音程がいっきに下がる）・buzz＝ブブブ（低いデジタルのうなり）・thud＝ドッ・tick＝コッ"""
    n = n_(d)
    t = tl(n)
    if kind == 'zap':
        f = 60 + rng.uniform(300, 700) * np.exp(-t / .012)
        x = lp(np.sign(np.sin(phase(f, n))) * np.exp(-t / .04), 3000)
    elif kind == 'buzz':
        f = rng.uniform(40, 110)
        x = lp(np.round((.6 * np.sign(np.sin(phase(f, n))) + .4 * np.sign(np.sin(phase(f * 1.5, n)))) * 4) / 4, 1600)
    elif kind == 'thud':
        x = np.tanh(2 * np.sin(phase(rng.uniform(42, 60), n)) * np.exp(-t / .04))
    else:
        x = 3 * lp(rng.standard_normal(n), 1200) * np.exp(-t / .006)
    return fade(x, .001, .004)


def lcrackle(d, rate, rng):
    """低いジジジ（こもった静電気）"""
    n = n_(d)
    x = np.zeros(n)
    for _ in range(int(rng.poisson(rate * d))):
        i = int(rng.integers(0, max(1, n - 400)))
        k = int(rng.integers(60, 400))
        seg = rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 4)) * rng.uniform(.3, 1)
        x[i:i + k] += seg[:len(x[i:i + k])]
    return bp(x, 150, 1800)


def crt_low(rng):
    """ブツン（低いプチュン）：重低音がドスンと落ちる「ブ」＋音程がいっきに下がる「ツ」＋短いうなり「ン」"""
    d = .6
    n = n_(d)
    t = tl(n)
    pu = np.tanh(2.2 * np.sin(phase(26 + 130 * np.exp(-t / .03), n)) * np.exp(-t / .16)) / np.tanh(2.2)
    zip_ = np.tanh(3 * np.sin(phase(55 + 1500 * np.exp(-t / .028), n))) * np.exp(-t / .07)
    chu = bp(rng.standard_normal(n), 400, 3000) * np.exp(-np.maximum(t - .005, 0) / .015) * np.minimum(t / .005, 1)
    hum = (np.sin(phase(55, n)) + .5 * np.sin(phase(110, n))) * np.exp(-np.maximum(t - .03, 0) / .12) * np.minimum(t / .03, 1)
    click = lp(rng.standard_normal(n), 3000) * np.exp(-t / .002)
    return fade(.9 * pu + .6 * zip_ + .5 * chu + .3 * hum + .4 * click, .0005, .06)


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

    def render(self, rt=1.5, damp=6500, target=-16.0, peak_db=-1.0, bass=False):
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
        x = master(self.b + np.stack([wl + .25 * wr, wr + .25 * wl], 1), peak_db, bass)
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


BASS_EX = 1.0    # 低音から作る倍音の量（ど的中）
BASS_SAT = 2.5   # 低音（120Hzより下）をまるめる強さ（ど的中。重低音のピークで全体が小さくならないように）


def master(x, peak_db=-1.0, bass=False):
    """仕上げ：低すぎる音を切る → 低音を少し下げ、こもりを少し取り、輪郭を少し出す → まとめて少し圧縮（大きいところだけ下げる）→ 少しだけ丸める → いちばん大きい所を -1dB に
       bass（ど的中）：低音を下げずに持ち上げ（100Hzより下 +3dB）、1.5kHz あたりを少し出して輪郭を作る。
       120Hzより下だけ頭をまるめて（重低音のピークで全体が小さくならないように）、160Hzより下の音をひずませて 200〜1500Hz の倍音を足す
       （スマホのスピーカーは重低音が出ないので、倍音で低音を感じるように）"""
    x = np.stack([hp(x[:, c] - x[:, c].mean(), 25 if bass else 30, 2) for c in range(2)], 1)
    eq = ((('shelf_lo', 100, .7071, 3.0), ('peak', 320, 1.0, -2.0), ('peak', 1500, .9, 2.5), ('shelf_hi', 7000, .7071, -1.5)) if bass
          else (('shelf_lo', 150, .7071, -3.0), ('peak', 320, 1.0, -2.0), ('peak', 2600, .9, 1.5)))
    for kind, f0, q, g in eq:
        b, a = biquad(kind, f0, q, g)
        x = signal.lfilter(b, a, x, axis=0)
    if bass:
        lo = np.stack([lp(lp(x[:, c], 120, 2), 120, 2) for c in range(2)], 1)
        pk = np.max(np.abs(lo)) + 1e-12
        x = x - lo + np.tanh(BASS_SAT * lo / pk) * pk / BASS_SAT
        lo = np.stack([lp(x[:, c], 160, 4) for c in range(2)], 1)
        pk = np.max(np.abs(lo)) + 1e-12
        h = np.tanh(6 * lo / pk) * pk
        x = x + BASS_EX * np.stack([bp(h[:, c], 200, 1500, 2) for c in range(2)], 1)
    x = x / (np.max(np.abs(x)) + 1e-12)
    e = np.sqrt(np.maximum(lp(np.mean(x ** 2, 1), 15, 1), 1e-10))
    g = np.minimum(1.0, (.22 / e) ** (1 - 1 / 2.5))
    g = lp(np.concatenate([np.ones(2000), g]), 6, 1)[2000:]
    x = x * g[:, None]
    x = x / (np.max(np.abs(x)) + 1e-12)
    k = 1.8 if bass else 1.3
    x = np.tanh(k * x) / np.tanh(k)
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
    """押してから：0 ポン → .25〜.8 ヒュイーン（ボードが上がる）→ .95「的中！」キラーン → 1.15・1.3 買い目でピン・ポン → 1.6 合計でチャリーン
       （的中の見本：ボード .3秒〜・「的中！」.95秒・買い目 1.15秒から .15秒ごと・合計は 1.15＋.15×3秒）"""
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
    """PUSHが出たとき：ドゥン（重低音）＋キュイーン↑（低めから上がる）＋低いうなり（D2 → D3）＋低めのキラキラ"""
    mx = Mix(1.9, 21)
    r = mx.rng
    mx.add(boom(95, 30, 1.5, .45, .06, 2.4, r), 0, .55, rv=.1)
    mx.add(cuin(440, 1400, 1.3, .24, r), .02, .5, rv=.3)
    mx.add(growl(mtof(38), mtof(50), 1.6, .8), .02, .4, rv=.2)
    mx.add(lcrash(r, 1.4, .45), .02, .1, rv=.3)
    sparkle(mx, .25, .6, 5, (74, 78, 81, 86), .05, r)
    return mx.render(1.5, target=-14, bass=True)


def sfx_big():
    """押してから（パチンコの当たりのように速く・重く。gen_fx.py の BIG_CSS の秒）：0 ガツッ → .04 ドォォン!!（白く光る・爆発）
       → .1・.25・.4 キュウィン×3（虹の輪・下にドン。D6 → F#6 → A6）→ .38〜.55 ボードが落ちてきてズドン（着地・爆発）
       → .7「デカ的中!!」ジャーン!!（低い金管・D）→ .9・.98 買い目 → 1.14 合計（メダルがジャラジャラ・パッパッ）→ 1.4 パーン（D）
       （ジャーンとパーンは低い金管が中心。上に高めの金管を小さく重ねて、スマホのスピーカーでも聞こえるようにする）"""
    mx = Mix(3.0, 22)
    r = mx.rng
    mx.add(pop(300, 110, .12, r, .3), 0, .7, rv=.1)
    mx.add(explosion(r, .9), .04, 1.0, rv=.15)
    mx.add(boom(100, 28, 1.4, .45, .06, 2.6, r), .04, .9, rv=.1)
    mx.add(lcrash(r, 1.6, .5), .04, .2, -.5, rv=.25)
    mx.add(lcrash(r, 1.6, .5), .04, .2, .5, rv=.25)
    for t, m, g, p in ((.1, 86, .42, -.3), (.25, 90, .45, .3), (.4, 93, .5, 0)):
        mx.add(kyuin(mtof(m) / 2.3, mtof(m)), t, g, p, rv=.3)
        mx.add(boom(120, 40, .35, .14, .03, 2.4, r), t, .45, rv=.05)
    mx.add(nsweep(.18, 2400, 300, .4, r) * np.linspace(0, 1, n_(.18)) ** 2, .38, .2, rv=.2)
    mx.add(boom(110, 30, 1.0, .35, .04, 2.8, r), .55, .9, rv=.1)
    mx.add(explosion(r, .5), .55, .5, rv=.15)
    for i, m in enumerate((38, 45, 50, 54, 57, 62)):                               # D2 A2 D3 F#3 A3 D4
        mx.add(brass(m, .9, r), .7, .42, (i / 5 - .5) * .8, rv=.25)
    mx.add(boom(90, 28, 1.2, .4, .05, 2.6, r), .7, .8, rv=.1)
    mx.add(lcrash(r, 1.8, .6), .7, .2, -.4, rv=.3)
    mx.add(lcrash(r, 1.8, .6), .7, .2, .4, rv=.3)
    mx.add(gong(mtof(50), 1.8, .7, r), .7, .3, rv=.35)
    for t, m in ((.9, 62), (.98, 66)):                                               # 買い目（D4・F#4）
        mx.add(bell(mtof(m), .6, idx=1.4, tau=.3), t, .25, rv=.3)
        mx.add(coin(1600, r, .3, False), t, .12, rv=.2)
    medals(mx, 1.14, 1.2, 18, .28, r)                                                # 合計
    mx.add(bell(mtof(69), 1.2, idx=1.3, tau=.6), 1.14, .25, rv=.4)
    for t, m in ((1.14, 50), (1.22, 54), (1.3, 57)):
        mx.add(brass(m, .07, r, False), t, .38, rv=.2)
    for i, m in enumerate((38, 45, 50, 54, 57, 62)):
        mx.add(brass(m, .9, r), 1.4, .36, (i / 5 - .5) * .8, rv=.3)
    mx.add(boom(90, 28, 1.1, .35, .05, 2.4, r), 1.4, .7, rv=.1)
    mx.add(lcrash(r, 1.6, .55), 1.4, .15, -.4, rv=.3)
    mx.add(lcrash(r, 1.6, .55), 1.4, .15, .4, rv=.3)
    mx.add(pad((38, 45, 50, 54), 1.0, .2, .6, .45), 1.4, .25, rv=.35)
    # 上の金管（F#4・A4・D5）を小さく重ねる：重低音はスマホのスピーカーから出ないので、ジャーンとファンファーレがスマホでも聞こえるように
    for t, g in ((.7, .16), (1.4, .16 * .9)):
        for i, m in enumerate((66, 69, 74)):
            mx.add(brass(m, .9, r), t, g, (i - 1) * .5, rv=.3)
    for t, m in ((1.14, 62), (1.22, 66), (1.3, 69)):
        mx.add(brass(m, .07, r, False), t, .16 * 1.2, rv=.2)
    return mx.render(1.5, target=-13, bass=True)


# ---------- ど的中ボタン（フリーズ・ホ長調・低音と重低音で、いちばん派手） ----------
FZ_LOW = .5     # 重低音（ドォォン）の大きさ
FZ_MID = 1.5    # 低音の楽器（金管・ジャン・どら・鐘・シャーン）の大きさ。スマホのスピーカーで聞こえるのはおもにこちら


def sfx_fz_push():
    """PUSHが出たとき：ドォォン（重低音）＋グォォォン↑（低いうなりが1オクターブ上がる）＋低いどら＋うしろでゴゴゴ（地ひびき）"""
    mx = Mix(2.4, 31)
    r = mx.rng
    mx.add(boom(100, 30, 1.8, .5, .07, 2.4, r), 0, 1.2 * FZ_LOW, rv=.12)
    mx.add(growl(mtof(40), mtof(52), 1.9, 1.0), .02, .8, -.1, rv=.2)         # E2 → E3
    mx.add(growl(mtof(47), mtof(59), 1.9, 1.0), .03, .35, .1, rv=.2)         # 5度上を重ねる（B2 → B3）
    mx.add(rumble(1.8, r), 0, .15, rv=.1)
    mx.add(lcrash(r, 1.6, .5), .02, .1 * FZ_MID, rv=.3)
    mx.add(gong(mtof(52), 2.0, .8, r), .03, .25 * FZ_MID, rv=.35)                     # E3
    return mx.render(1.6, target=-13, bass=True)


def medals(mx, t0, dur, count, g, rng, curve=1.8):
    """ジャラジャラ：メダル（コインより低め）がたくさん"""
    for _ in range(count):
        mx.add(coin(rng.uniform(1000, 1900), rng, rng.uniform(.25, .45)), t0 + dur * rng.uniform(0, 1) ** curve, g * rng.uniform(.5, 1), rng.uniform(-.8, .8), rv=.25)


def sfx_fz():
    """押してから（秒は gen_fx.py の FZ_T・MT_T）。全体を低音・重低音で、とんでも！からは爆発のようにずっしり重く：
       0〜E バグる音（ドッ＋GL_SCRIPT のコマごとに低いブブッ・ヴッ・ドッ・コッ）→ C アイコンのドアップでヴォォン＋ギュゥン↓
       → H 光の筋でゴォッ → E 青い画面でゴゴゴ（地ひびき）と低いうなりが上がる → W ブツン（低いプチュン）→ Z ズゥン↓ → 真っ暗（無音）
       → M ドガーン!!（大爆発）→「とんでも！」1文字ずつ小さな爆発でドドドド＋「！」で爆発と低いジャン（E → F# → G# → A）・低いベースが刻む
       → M＋T4 白い光でゴォーン →「ど！」×4（爆発がだんだん高く・低いジャン）→ 低いタムの連打
       → M＋T5「ど的中！！！！」で大爆発＋低い金管の和音＋「！」×4で小さな爆発 → 光の波に合わせて .45秒ごとに重いドン（爆発）
       → R 結果：大爆発＋低いパッパッパーン → R＋.3 着地のズドン・「フリーズ的中!!!」ジャーン → 買い目 R＋.45〜（.08秒おき）→ 合計 R＋.69（メダル）"""
    fz, gl, mt = read_fx_times()
    C, H, E, W, Z, M, R = (fz[k] for k in 'CHEWZMR')
    mx = Mix(R + 3.4, 32)
    r = mx.rng
    # --- バグる（0〜E） ---
    mx.add(boom(120, 32, .9, .3, .03, 2.8, r), 0, .9 * FZ_LOW, rv=.08)
    mx.add(lglitch('zap', .08, r), 0, .45, rv=.08)
    for t0, t1, fx in gl:
        d = max(.02, t1 - t0)
        for f in fx.split():
            v = float(f[1:]) if len(f) > 1 else 0
            if f[0] == 'S':
                rb = np.random.default_rng(int(v * 7 + 3))
                mx.add(lglitch('buzz', d, rb), t0, .2 + .012 * v, rv=.05)
            elif f[0] == 'L':
                mx.add(lglitch('zap', min(d, .06), r), t0, .55 + v / 80, r.uniform(-.5, .5), rv=.08)
            elif f[0] == 'B':
                mx.add(lglitch('thud', min(d, .06), r), t0, .7, rv=.05)
            elif f[0] == 'T':
                mx.add(lglitch('tick', .03, r), t0, .6, r.uniform(-.4, .4), rv=.05)
    # アイコンのドアップ（C〜E）：ヴォォン（低い電気のうなり）＋ギュゥン↓
    n = n_(E - C)
    hum = lp(saw(41.2, n, .1) + .6 * saw(55.0 * 1.003, n, .15), 700) * np.minimum(tl(n) / .03, 1) * np.clip((E - C - tl(n)) / .05, 0, 1)
    mx.add(fade(hum), C, .32, rv=.1)
    gd = .25
    mx.add(fade(np.sin(phase(np.geomspace(420, 42, n_(gd)), n_(gd))) * np.exp(-tl(n_(gd)) / .1)), C, .45, rv=.15)
    mx.add(boom(80, 30, .6, .25, .04, 2.0, r), C, .5 * FZ_LOW, rv=.1)
    # 光の筋（H〜E）：ゴォッ（低いノイズが左から右へ）
    wd = E - H + .05
    mx.add(nsweep(wd, 70, 600, .45, r) * np.sin(np.linspace(0, np.pi, n_(wd))), H, .3, np.linspace(-.7, .7, 8), rv=.2)
    # 青い画面（E〜W）：ゴゴゴ＋低いうなりが上がる＋低いジジジ
    d = W - E
    mx.add(rumble(d, r, 180, 16) * np.linspace(.3, 1, n_(d)), E, .45, rv=.1)
    mx.add(fade(np.tanh(1.5 * np.sin(phase(np.geomspace(32, 80, n_(d)), n_(d)))) * np.linspace(.3, 1, n_(d))), E, .35, rv=.1)
    mx.add(lcrackle(d, 90, r), E, .3, rv=.15)
    # ブツン（W）→ 線の低いジジ → ズゥン↓（Z）
    mx.add(crt_low(r), W, 1.8, rv=.25)
    mx.add(lcrackle(Z - W - .04, 45, r), W + .04, .18, rv=.2)
    sd = .35
    mx.add(fade(np.tanh(1.8 * np.sin(phase(np.geomspace(300, 34, n_(sd)), n_(sd)))) * np.exp(-tl(n_(sd)) / .12)), Z, .5, rv=.25)
    # --- 真っ暗（Z＋.3〜M）は無音 ---
    # --- ネオンのカット（M〜R）：爆発のような重低音 ---
    T2, T3, T4, T5 = (M + mt[k] for k in ('T2', 'T3', 'T4', 'T5'))
    mx.add(explosion(r, 1.4), M, 1.0, rv=.15)                                      # ドガーン!!（大爆発）
    mx.add(boom(90, 26, 1.6, .45, .08, 2.8, r), M, 1.0 * FZ_LOW, rv=.15)
    mx.add(lcrash(r, 1.8, .55), M, .16 * FZ_MID, -.5, rv=.25)
    mx.add(lcrash(r, 1.8, .55), M, .16 * FZ_MID, .5, rv=.25)
    mx.add(stab((40, 47, 52), .55, r, 3.0, .5), M, .55 * FZ_MID, rv=.25)           # E2・B2・E3（下に E1）
    # 「とんでも！」×4（T1・T2・T3の2つ）：と・ん・で・も は小さな爆発でドドドド、「！」で爆発＋低いジャン（E → F# → G# → A）
    cuts = ((M + .05, .05, M + .27, 52), (T2 + .03, .045, T2 + .21, 54), (T3 + .03, .04, T3 + .19, 56), (T3 + .22, .04, T3 + .38, 57))
    for k, (d0, step, tx, root) in enumerate(cuts):
        for i in range(4):
            t = d0 + step * i
            mx.add(explosion(r, .3, 1 + .08 * i), t, .5, (-.4, -.15, .15, .4)[i], rv=.1)
            mx.add(tom(mtof(root - 17 + 2 * i), r, .4), t, .35 * FZ_MID, (-.4, -.15, .15, .4)[i], rv=.12)
        mx.add(explosion(r, .8), tx, .85, (-.2, .2, -.1, .1)[k], rv=.15)
        mx.add(stab((root - 12, root - 5, root), .42, r, 3.0, .45), tx, .55 * FZ_MID, (-.2, .2, -.1, .1)[k], rv=.22)
        mx.add(boom(110, 32, .6, .22, .03, 2.6, r), tx, .75 * FZ_LOW, rv=.08)
        mx.add(lcrash(r, .8, .3), tx, .1 * FZ_MID, (-.4, .4, -.3, .3)[k], rv=.2)
    # 下で刻む低いベース（E → F# → G# → A → B）：「ど！」と同じ .17秒の刻み
    roots = ((M, 28), (T2, 30), (T3, 32), (T3 + .22, 33), (T4, 35))
    dd = T4 + .12
    k = 0
    while dd - .17 * (k + 1) >= M + .05:
        k += 1
    t = dd - .17 * k
    j = 0
    while t < T5 - .05:
        rt = [m for s0, m in roots if s0 <= t + 1e-6][-1]
        mx.add(stab((rt + 12, rt + 24), .16, r, 2.6, .5), t, (.14 + .006 * j) * FZ_MID, rv=.08)
        t += .17
        j += 1
    # 白い光（M＋T4）：ゴォーン＋暗いシャーン →「ど！」×4（爆発がだんだん高く・低いジャン）
    mx.add(gong(mtof(47), 1.6, .6, r), T4, .35 * FZ_MID, rv=.35)                  # B2
    mx.add(lcrash(r, 1.2, .4), T4, .12 * FZ_MID, -.4, rv=.3)
    mx.add(lcrash(r, 1.2, .4), T4, .12 * FZ_MID, .4, rv=.3)
    for i, ch in enumerate(((47, 54, 59), (51, 54, 59, 63), (54, 59, 63, 66), (59, 63, 66, 71))):
        t = T4 + .12 + .17 * i
        mx.add(explosion(r, .9, 1 + .12 * i), t, .9 + .04 * i, (-.25, .25, -.15, .15)[i], rv=.12)
        mx.add(stab(ch, .2, r, 3.0, .5), t, (.45 + .05 * i) * FZ_MID, rv=.2)
        mx.add(lsnare(r, .22), t, .3, rv=.12)
    t = T4 + .12 + .17 * 3 + .08
    while t < T5 - .02:                                                             # 低いタムの連打（だんだん速く・高く）
        u = (t - (T4 + .71)) / max(.01, T5 - T4 - .71)
        mx.add(tom(70 + 80 * u, r, .16), t, (.3 + .3 * u) * FZ_MID, r.uniform(-.3, .3), rv=.12)
        t += .045 - .015 * u
    rd = T5 - T4
    mx.add(nsweep(rd, 60, 1200, .4, r) * np.linspace(0, 1, n_(rd)) ** 2, T4, .3, rv=.25)
    mx.add(fade(np.tanh(1.4 * np.sin(phase(np.geomspace(30, 66, n_(rd)), n_(rd)))) * np.linspace(0, 1, n_(rd)) ** 1.5), T4, .3, rv=.1)
    # 「ど的中！！！！」（M＋T5）：大爆発＋ドォォォン＋低い金管の和音（E）＋「！」×4で小さな爆発
    mx.add(explosion(r, 1.8), T5, 1.0, rv=.2)
    mx.add(boom(80, 25, 2.0, .55, .1, 2.6, r), T5, 1.0 * FZ_LOW, rv=.2)
    mx.add(lcrash(r, 2.4, .8), T5, .22 * FZ_MID, -.5, rv=.35)
    mx.add(lcrash(r, 2.4, .8), T5, .22 * FZ_MID, .5, rv=.35)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):                               # E2・B2・E3・G#3・B3・E4
        mx.add(brass(m, 1.5, r), T5, .34 * FZ_MID, (i / 5 - .5) * .8, rv=.3)
    for i, m in enumerate((68, 71)):                                               # 上に G#4・B4 を少し（輪郭）
        mx.add(brass(m, 1.5, r), T5, .2 * FZ_MID, (-.3, .3)[i], rv=.3)
    mx.add(pad((40, 47, 52), 1.4, .15, .5, .5), T5, .25, rv=.3)
    mx.add(gong(mtof(52), 2.0, .75, r), T5 + .02, .35 * FZ_MID, rv=.4)
    for i in range(4):                                                              # ！×4
        mx.add(explosion(r, .35, 1.1 + .1 * i), T5 + .08 + .05 * i, .5, (-.45, -.15, .15, .45)[i], rv=.12)
    # 光の波（.45秒ごと）に合わせて重いドン（小さな爆発）と、低いピロピロ（16分）
    k = 1
    while T5 + .45 * k < R - .1:
        tb = T5 + .45 * k
        mx.add(explosion(r, .45), tb, .55, rv=.08)
        mx.add(boom(110, 32, .55, .22, .03, 2.6, r), tb, .5 * FZ_LOW, rv=.06)
        mx.add(stab((40, 52), .3, r, 2.2, .5), tb, .2 * FZ_MID, rv=.15)
        k += 1
    arp = (52, 56, 59, 64, 59, 56)
    j = 0
    while T5 + .2 + .1125 * j < R - .05:
        tj = T5 + .2 + .1125 * j
        mx.add(pluck(arp[j % len(arp)] + 12 * (j // 12 % 2), .25, .1), tj, .12, (-.3, .3)[j % 2], rv=.25)
        j += 1
    # --- 結果（R）：大爆発＋低いパッパッパーン → R＋.3 着地のズドン・「フリーズ的中!!!」ジャーン → 買い目（.08秒おき）→ 合計 ---
    mx.add(explosion(r, 1.6), R, 1.0, rv=.15)
    mx.add(boom(100, 30, 1.3, .4, .05, 2.4, r), R, .95 * FZ_LOW, rv=.15)
    for t, m in ((R, 52), (R + .08, 56), (R + .16, 59)):                          # E3 G#3 B3
        mx.add(brass(m, .06, r, False), t, .38 * FZ_MID, rv=.2)
    mx.add(boom(110, 30, 1.0, .35, .04, 2.8, r), R + .3, .9 * FZ_LOW, rv=.1)       # 着地（ズドン）
    mx.add(explosion(r, .6), R + .3, .6, rv=.12)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):                               # 「フリーズ的中!!!」
        mx.add(brass(m, 1.3, r), R + .3, .32 * FZ_MID, (i / 5 - .5) * .8, rv=.3)
    for i, m in enumerate((68, 71)):
        mx.add(brass(m, 1.3, r), R + .3, .2 * FZ_MID, (-.3, .3)[i], rv=.3)
    mx.add(lcrash(r, 2.0, .6), R + .3, .16 * FZ_MID, -.4, rv=.35)
    mx.add(lcrash(r, 2.0, .6), R + .3, .16 * FZ_MID, .4, rv=.35)
    mx.add(gong(mtof(47), 1.8, .7, r), R + .3, .3 * FZ_MID, -.2, rv=.4)
    medals(mx, R + .1, 1.8, 26, .22 * FZ_MID, r)
    for t, m in ((R + .45, 56), (R + .53, 59), (R + .61, 64)):                    # 買い目
        mx.add(bell(mtof(m), .7, idx=1.4, tau=.3), t, .22 * FZ_MID, rv=.3)
    mx.add(bell(mtof(64), 1.4, idx=1.3, tau=.6), R + .69, .28 * FZ_MID, rv=.45)  # 合計
    mx.add(coin(1500, r, .5), R + .69, .2, -.2, rv=.25)
    mx.add(coin(1900, r, .45), R + .75, .15, .25, rv=.25)
    mx.add(pad((40, 44, 47, 52), 1.0, .3, .7, .45), R + .69, .22, rv=.35)
    return mx.render(1.8, target=-13, bass=True)


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
