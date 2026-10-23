"""的中ボタン・デカ的中ボタン・ど的中ボタン（フリーズ的中ボタン）・プレミアムど的中（かわいいど的中）の効果音。音は全部ここで合成する（録音や、ほかの音のデータは使わない）。
   超プレミアムの ①〜⑤の 声「どぉ！」「てぇ！」「きぃ！」「ちゅ！」「う！」も 人の 声の しくみを 計算で まねて 作る（voice：フォルマント合成。録音・声の データは 使わない）
   python3 gen_sfx.py <出力フォルダ>
   → sfx_hit_push.wav・sfx_hit.wav（的中）／sfx_big_push.wav・sfx_big.wav（デカ）／sfx_fz_push.wav・sfx_fz.wav（ど的中＝フリーズ）
     ／sfx_pc.wav（プレミアムど的中（かわいいど的中）：タップの音だけ。PUSHの音は ど的中と同じ）
     ／sfx_zp.wav（超プレミアムど的中（手書き・鉛筆）：プレミアムの 音の ①〜⑤を 声に。PUSHの音は ど的中と同じ）
     ／sfx_gd.wav（神様的中：kami.py の 時刻）／sfx_sgd.wav（超神様的中（第4.51版）：1コマずつ 描いた 動画 ①②③ の 時刻＝kami_super.film_events()。PUSHの音は ど的中と同じ）
     *_push＝PUSHが出たとき（当たりのお知らせ）。それ以外＝PUSHを押してから（0秒＝押した瞬間）。44.1kHz・16bit・ステレオ
     ＋ sfx_wave.json（音の大きさの形・1/50秒ごと。効果音のメモ Fx_Sound.dc.html の波形に使う。gen_fx.py と同じフォルダに置く）
   秒は見本の動き（gen_fx.py）に合わせる。フリーズは gen_fx.py の FZ_T（フリーズの時刻）と MT_T（ネオンのカットの時刻）をそのまま読む。
   プレミアムは premium_cute.py の PC_T と SCREENS を読む
   乱数の種が決まっているので、何回作っても同じ音になる
   アプリ・見本に入れるとき（AAC 160kbps）：ffmpeg -i sfx_hit.wav -c:a aac -b:a 160k -movflags +faststart sfx_hit.m4a
   （見本のキャンバスは .m4a を受け付けないので、中身は同じで名前だけ .mp4 にして入れている）"""
import os, sys, ast, wave, json, math
import numpy as np
from scipy import signal

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))


def read_fx_times():
    """gen_fx.py から FZ_T（フリーズの時刻）・MT_T（ネオンのカットの時刻）を読む（見本の動きと音の時刻をそろえるため）"""
    tree = ast.parse(open(f'{HERE}/gen_fx.py', encoding='utf-8').read())
    fz = mt = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'FZ_T':
                fz = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            elif node.targets[0].id == 'MT_T':
                mt = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
    return fz, mt


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

    def duck(self, t0, t1, db, ramp=.03):
        """t0〜t1 の 間、これまでに 置いた 音を db だけ 小さく（声を 聞こえやすく。前後 ramp 秒で なめらかに）"""
        t = tl(len(self.b))
        e = np.clip(np.minimum((t - (t0 - ramp)) / ramp, ((t1 + ramp) - t) / ramp), 0, 1)
        k = (1 - (1 - 10 ** (db / 20)) * e)[:, None]
        self.b *= k
        self.r *= k

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


def arc_zap(d, rng, rate=260):
    """バチバチッ・ジジッ：細い電気（放電）の音。はじける粒（とても短い・高い音が多い）がかたまって鳴る＋シャーという細いノイズ"""
    n = n_(d)
    x = np.zeros(n)
    for _ in range(int(rng.poisson(rate * d))):
        i = int(rng.integers(0, max(1, n - 120)))
        k = int(rng.integers(8, 90))
        x[i:i + k] += (rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 5)))[:len(x[i:i + k])] * rng.uniform(.4, 1)
    hiss = bp(rng.standard_normal(n), 3500, 11000) * .25
    return fade(hp(x, 1800) + hiss, .001, .006)


def sfx_fz():
    """押してから（秒は gen_fx.py の FZ_T・MT_T）。押した瞬間にフリーズ（まさちゃんの送ってくれたパチスロのフリーズの動画のような音。動画の音は使わず、ここで作る）：
       0 ドンッ（重低音）＋ギュッ↓（低い音がいっきに下がる）＋ビーーッ（角ばった電子音 460Hz。画面のコマに合わせて揺れて、ときどき途切れる・ザザッ・チリチリ）
       → B・B＋.11 白い光がふくらむたびに低いヴォン → W ブツッ（電子音がいきなり消える）→ 線にまとわりつく細い電気でバチバチッ・ジジッ
       → Z ヒュゥン↓（線が縮む）→ プツッ → 真っ暗（無音）
       → M ドガーン!!（大爆発）→「どてき！！」ど・て・き は1文字ずつ小さな爆発でドドド＋1つ目の「！」でドガッ・2つ目の「！」で爆発と低いジャン（E → F# → G# → A）・低いベースが刻む
       → M＋T4 白い光でゴォーン →「ど！」×4（爆発がだんだん高く・低いジャン）→ 低いタムの連打
       → M＋T5「ど的中！！！！」で大爆発＋低い金管の和音＋「！」×4で小さな爆発 → 光の波に合わせて .45秒ごとに重いドン（爆発）
       → R 結果：大爆発＋低いパッパッパーン → R＋.3 着地のズドン・「ど的中！！！」ジャーン → 買い目 R＋.45〜（.08秒おき）→ 合計 R＋.69（メダル）"""
    fz, mt = read_fx_times()
    B, W, Z, M, R = (fz[k] for k in 'BWZMR')
    mx = Mix(R + 3.4, 32)
    r = mx.rng
    FR = 1 / 30
    # --- 押した瞬間：ドンッ（重低音）＋ギュッ↓＋カチッ ---
    mx.add(boom(110, 30, .55, .18, .03, 2.8, r), 0, 1.0 * FZ_LOW, rv=.03)       # すぐ消える（W からは無音に近く）
    n = n_(.18)
    t = tl(n)
    mx.add(fade(np.tanh(2.2 * np.sin(phase(70 + 190 * np.exp(-t / .045), n))) * np.exp(-t / .08)), 0, .6, rv=.06)
    mx.add(glitch('tick', .03, r), 0, .5, rv=.04)
    # --- ビーーッ（0〜W）：角ばった電子音（460Hz と1オクターブ下）。1コマごとに音程が少しずれて、ときどき小さくなる（途切れる）→ W でいきなり消える ---
    n = n_(W)
    t = tl(n)
    fi = np.minimum((t / FR).astype(int), int(W / FR))
    rr = np.random.default_rng(461)
    det = 1 + rr.uniform(-.025, .025, fi.max() + 1)[fi]
    gate = np.where(rr.random(fi.max() + 1) < .25, .3, 1.0)[fi]
    f = 460 * det
    sq = np.tanh(6 * np.sin(phase(f, n))) / np.tanh(6)
    sub = np.tanh(4 * np.sin(phase(f / 2 * 1.003, n))) / np.tanh(4)
    bz = lp(.7 * sq + .5 * sub, 7000) * lp(gate, 250, 1) * np.minimum(t / .004, 1)
    bz[-n_(.003):] *= np.linspace(1, 0, n_(.003))
    mx.add(bz, 0, .78, rv=0)                                                     # 残響なし（W でいきなり消える）
    # ザザッ（横に流れる帯 .067〜.2）・チリチリ（赤い粒 .2〜.267）・点々（B＋1コマ）
    for k in range(4):
        mx.add(glitch('zip', FR * .9, r), .067 + k * FR, .32, r.uniform(-.4, .4), rv=.05)
    mx.add(crackle(.067, 900, r), .2, .45, rv=.05)
    mx.add(glitch('zip', FR * .9, r), B + FR, .3, rv=.05)
    # 白い光がふくらむ（B・B＋.11）：低いヴォン
    for tt in (B, B + .11):
        n = n_(.12)
        t = tl(n)
        mx.add(fade(np.tanh(1.8 * np.sin(phase(62 + 30 * np.exp(-t / .03), n))) * np.exp(-t / .06)), tt, .45, rv=.08)
    # --- ブツッ（W）：電子音が消える瞬間の短いポップ ---
    n = n_(.08)
    t = tl(n)
    mx.add(fade(.8 * np.sin(phase(50 + 90 * np.exp(-t / .01), n)) * np.exp(-t / .025) + .5 * lp(r.standard_normal(n), 2500) * np.exp(-t / .003)), W, .7, rv=.05)
    # --- 細い電気（W〜Z＋.15）：バチバチッ・ジジッ（電気の形が変わるコマごとに、はじける粒がかたまる）---
    k = 0
    while W + k * FR < Z + .15:
        tt = W + k * FR
        sz = 1.0 if tt < Z else max(.3, 1 - (tt - Z) / .18)
        mx.add(arc_zap(FR * 1.2, r, rate=420 * sz), tt, 1.25 * sz, r.uniform(-.5, .5), rv=.04)
        k += 1
    # --- ヒュゥン↓（Z〜）：線が縮む・高い音がいっきに下がる → プツッ ---
    n = n_(.2)
    t = tl(n)
    wh = np.sin(phase(2600 * np.exp(-t / .06) + 180, n)) * np.minimum(t / .01, 1) * np.clip((.2 - t) / .03, 0, 1)
    mx.add(fade(wh), Z, .16, rv=.05)
    mx.add(glitch('tick', .02, r), Z + .19, .35, rv=.04)
    # --- 真っ暗（Z＋.2〜M）は無音 ---
    # --- ネオンのカット（M〜R）：爆発のような重低音 ---
    T2, T3, T4, T5 = (M + mt[k] for k in ('T2', 'T3', 'T4', 'T5'))
    mx.add(explosion(r, 1.4), M, 1.0, rv=.15)                                      # ドガーン!!（大爆発）
    mx.add(boom(90, 26, 1.6, .45, .08, 2.8, r), M, 1.0 * FZ_LOW, rv=.15)
    mx.add(lcrash(r, 1.8, .55), M, .16 * FZ_MID, -.5, rv=.25)
    mx.add(lcrash(r, 1.8, .55), M, .16 * FZ_MID, .5, rv=.25)
    mx.add(stab((40, 47, 52), .55, r, 3.0, .5), M, .55 * FZ_MID, rv=.25)           # E2・B2・E3（下に E1）
    # 「どてき！！」×4（T1・T2・T3の2つ）：ど・て・き は小さな爆発でドドド、1つ目の「！」でドガッ（少し大きい爆発）、2つ目の「！」で爆発＋低いジャン（E → F# → G# → A）
    # 時刻は gen_fx.py の mt_layers（5文字が d0 から step 秒おき・5文字目＝2つ目の「！」が tx）
    cuts = ((M + .05, .05, M + .27, 52), (T2 + .03, .045, T2 + .21, 54), (T3 + .03, .04, T3 + .19, 56), (T3 + .22, .04, T3 + .38, 57))
    for k, (d0, step, tx, root) in enumerate(cuts):
        for i in range(4):
            t = d0 + step * i
            if i < 3:
                mx.add(explosion(r, .3, 1 + .08 * i), t, .5, (-.4, -.15, .15, .4)[i], rv=.1)
            else:
                mx.add(explosion(r, .5, 1.1), t, .7, .4, rv=.12)
                mx.add(boom(120, 34, .4, .16, .02, 2.4, r), t, .5 * FZ_LOW, rv=.06)
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
    # --- 結果（R）：大爆発＋低いパッパッパーン → R＋.3 着地のズドン・「ど的中！！！」ジャーン → 買い目（.08秒おき）→ 合計 ---
    mx.add(explosion(r, 1.6), R, 1.0, rv=.15)
    mx.add(boom(100, 30, 1.3, .4, .05, 2.4, r), R, .95 * FZ_LOW, rv=.15)
    for t, m in ((R, 52), (R + .08, 56), (R + .16, 59)):                          # E3 G#3 B3
        mx.add(brass(m, .06, r, False), t, .38 * FZ_MID, rv=.2)
    mx.add(boom(110, 30, 1.0, .35, .04, 2.8, r), R + .3, .9 * FZ_LOW, rv=.1)       # 着地（ズドン）
    mx.add(explosion(r, .6), R + .3, .6, rv=.12)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):                               # 「ど的中！！！」
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


# ---------- プレミアムど的中（かわいいど的中・ハ長調・オルゴールと鐘で かわいく。PUSHの音は ど的中と同じ） ----------
def read_pc_times():
    """premium_cute.py から PC_T（時刻）と SCREENS（①〜⑤：字・顔・入ってくる方）を読む（見本の動きと音の時刻をそろえるため）"""
    tree = ast.parse(open(f'{HERE}/premium_cute.py', encoding='utf-8').read())
    pc = sc = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'PC_T':
                pc = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            elif node.targets[0].id == 'SCREENS':
                sc = ast.literal_eval(node.value)
    return pc, sc


def tine(f, d=1.2, tau=.6):
    """オルゴールの 音（細い 金属の 歯：はじいた 瞬間だけ 高い 倍音・すぐ すんだ 音に）"""
    n = n_(d)
    t = tl(n)
    x = np.sin(2 * np.pi * f * t) + .22 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / (tau * .4))
    if f * 5.4 < 16000:
        x = x + .3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .025)
    return fade(x * env(n, .001, tau), .001, .03)


def kiss(rng):
    """チュッ：くちびるの 小さな 音（とても 短い ノイズ）＋ すっと 上がる 高い 音"""
    n = n_(.15)
    t = tl(n)
    f = 1150 + 1700 * (1 - np.exp(-t / .022))
    x = np.sin(phase(f, n)) * np.minimum(t / .004, 1) * np.exp(-t / .032)
    x = x + .45 * bp(rng.standard_normal(n), 1800, 7000) * np.exp(-t / .005)
    return fade(x, .0005, .02)


def clap(rng, d=.2):
    """パン：やわらかい 手拍子（ノイズが 3回 すぐ つづく）"""
    n = n_(d)
    t = tl(n)
    e = np.zeros(n)
    for k, dt in enumerate((0, .009, .018)):
        e += (t >= dt) * np.exp(-np.maximum(t - dt, 0) / (.006 if k < 2 else .055))
    return fade(bp(rng.standard_normal(n), 900, 6000) * e, .0005, .02)


# ---------- 声（まさちゃん「プレミアムど的中、音を変えて！ ど！ 音:どぉ！ て！ 音:てぇ！ き！ 音:きぃ！ ちゅ！ 音:ちゅ！ う！ 音:う！」）----------
# 録音は 使わず、人の 声の しくみを 計算で まねて 作る（フォルマント合成）：声帯の 音（のどの ふるえ：高さ・ゆらぎ・息）→ 口の 中の ひびき（フォルマント 5つ）。
# 子音は 破裂（ぱっと 出る 短い ノイズ）・息（口の ひびきを 通る ノイズ）・こすれる 音（ちゅ の「ち」）を 足す。かわいい 高めの 声（女の子の アニメの 声くらい）
VOWELS = dict(  # 母音の ひびき（F1〜F8 Hz）と はば（Hz）：かわいい 声（口が 小さめ）。日本語の う は くちびるを まるめない う。F7・F8 は 息の 明るさ（高い 所が 落ちすぎない）
    o=((560, 980, 2900, 3950, 4900, 6200, 7600, 9000), (80, 100, 150, 250, 300, 500, 700, 900)),
    e=((620, 2300, 3050, 4050, 4950, 6300, 7600, 9000), (80, 110, 170, 250, 300, 500, 700, 900)),
    i=((350, 2850, 3500, 4350, 5000, 6400, 7700, 9100), (60, 130, 200, 250, 300, 500, 700, 900)),
    u=((400, 1600, 2800, 3950, 4900, 6200, 7600, 9000), (70, 110, 160, 250, 300, 500, 700, 900)))
# 音節：v 母音・d 長さ・von 声が 出はじめる 秒・pre 声の 前の のどの ふるえ（だ行）・
#   burst 破裂（秒・長さ・高さの 下・上・大きさ（母音の 大きさ に たいして））・asp 息（はじめ・おわり・大きさ）・fric こすれる 音（はじめ・おわり・高さの 下・上・大きさ）・
#   tr 子音から 母音への ひびきの 動き（F1〜F3 の はじめ・秒）
SYL = dict(
    do=dict(v='o', d=.46, von=.03, pre=.03, burst=(.03, .004, 2500, 6000, 1.2), tr=((260, 1650, 2650), .055)),
    te=dict(v='e', d=.46, von=.034, burst=(0, .006, 3000, 8000, 2.0), asp=(.005, .034, .35), tr=((360, 1750, 2700), .045)),
    ki=dict(v='i', d=.46, von=.055, burst=(0, .007, 2600, 4200, 2.2), asp=(.006, .055, .28), fric=(.008, .05, 3500, 7000, .22), tr=((300, 2600, 3300), .035)),
    chu=dict(v='u', d=.31, von=.075, burst=(0, .004, 3000, 7500, 1.4), fric=(.004, .075, 2800, 7000, .55), tr=((320, 2150, 2850), .06)),
    u=dict(v='u', d=.33, von=0.0, asp=(0, .02, .12)))


def _reson(x, F, B):
    """口の ひびき 1つ（2次の 共鳴：時間で 高さ F・はば B が かわる。Klatt の 形）"""
    T = 1.0 / SR
    C = -np.exp(-2 * np.pi * B * T)
    Bc = 2 * np.exp(-np.pi * B * T) * np.cos(2 * np.pi * F * T)
    A = 1 - Bc - C
    y = np.zeros(len(x))
    y1 = y2 = 0.0
    for k in range(len(x)):
        v = A[k] * x[k] + Bc[k] * y1 + C[k] * y2
        y[k] = v
        y2, y1 = y1, v
    return y


def _track(keys, n):
    """[(秒, 値) …] を 1サンプルごとに（直線で つなぐ）"""
    ts, vs = zip(*keys)
    return np.interp(tl(n), ts, vs)


def _tract(x, S, t, n):
    """口の ひびき（8つ を つなぐ）：子音の 形から 母音へ（tr）。息の 間は F1 の はばが 広い"""
    Fv, Bv = VOWELS[S['v']]
    von = S['von']
    for k in range(len(Fv)):
        F, B = Fv[k], Bv[k]
        if S.get('tr') and k < 3:
            f_s, tdur = S['tr'][0][k], S['tr'][1]
            Ft = _track([(0, f_s), (von, f_s), (von + tdur, F), (t[-1] + 1e-3, F)], n)
        else:
            Ft = np.full(n, float(F))
        Bt = np.full(n, float(B)) + (160 * (t < von) if k == 0 else 0)
        x = _reson(x, Ft, Bt)
    return x


def _noise(rng, n, lo, hi, order=2):
    y = bp(rng.standard_normal(n), lo, min(SR / 2 - 500, hi), order)
    return y / (np.std(y) + 1e-12)


def voice(syl, note, rng, d=None):
    """声の 音節（どぉ・てぇ・きぃ・ちゅ・う）。note＝声の 高さの まん中（MIDI）。母音の 大きさ（RMS）を 0.25 に そろえる"""
    S = SYL[syl]
    d = S['d'] if d is None else d
    n = n_(d)
    t = tl(n)
    von = S['von']
    dv = d - von
    # 声の 高さ：出だしで ぐっと 上がって（びっくり）少し もどり、のばす 所で ゆれ（ビブラート）、さいごに 下がる（！）
    st = _track([(0, note - 2.6), (von + .07, note + .8), (von + .16, note), (von + max(.17, dv - .13), note - .5), (d, note - 4.2)], n)
    vib = .28 * np.sin(2 * np.pi * 5.8 * t) * np.clip((t - von - .17) / .1, 0, 1)
    jit = lp(rng.standard_normal(n), 30, 1)
    jit = jit / (np.std(jit) + 1e-12) * .12                                          # 高さの ゆらぎ（人の 声の ように 少し：±0.12半音 くらい）
    f0 = 440.0 * 2 ** ((st + vib + jit - 69) / 12)
    # 声帯の 音（4倍の 細かさで 作って もどす：かくかくの ノイズを 出さない）：のどが ひらいて とじる 形の 変化（KLGLOTT88）
    up = 4
    ph = np.cumsum(np.repeat(f0, up) / (SR * up)) % 1.0
    oq = .62
    tau = ph / oq
    g = signal.resample_poly(np.where(ph < oq, 2 * tau - 3 * tau ** 2, 0.0), 1, up)[:n]
    g = lp(g, 7000, 1)
    gate = signal.resample_poly((ph < oq).astype(float), 1, up)[:n]
    shim = lp(rng.standard_normal(n), 40, 1)
    shim = 1 + .04 * shim / (np.std(shim) + 1e-12)                                    # 大きさの ゆらぎ（4% くらい）
    rel = min(.09, dv * .3)
    av = _track([(0, 0), (max(0, von - 1e-4), 0), (von + .012, 1), (von + .05, 1), (d - rel - .02, .82), (d, 0)], n)
    if S.get('pre'):                                                              # だ行：声の 前に のどだけ ふるえる（低い ブー）
        av = np.maximum(av, _track([(0, 0), (.006, .1), (S['pre'], .14), (S['pre'] + .004, 0)], n) * (t < S['pre'] + .004))
    breath = hp(rng.standard_normal(n), 400) * (.35 + .65 * gate)
    voiced = _tract(g * av * shim + breath * .05 * av, S, t, n)
    i0, i1 = n_(von + .08), n_(von + .18)
    voiced = voiced / (np.sqrt(np.mean(voiced[i0:i1] ** 2)) + 1e-12) * .25
    air = hp(g * av * shim + breath * .08 * av, 3200, 2)                            # 高い 所の 声と 息（口の ひびきを 通らない 少しの 音：こもらない ように）
    out = voiced + air / (np.sqrt(np.mean(air[i0:i1] ** 2)) + 1e-12) * .25 * PC_AIR
    if S.get('asp'):                                                              # 息（口の ひびきを 通る ノイズ）
        a0, a1, aa = S['asp']
        e = _track([(0, 0), (a0, 0), (a0 + .004, 1), (a1 - .006, .8), (a1 + .01, 0), (d, 0)], n)
        asp = _tract(hp(rng.standard_normal(n), 300) * e, S, t, n)
        m = e > .5
        out = out + asp / (np.sqrt(np.mean(asp[m] ** 2)) + 1e-12) * .25 * aa
    if S.get('burst'):                                                            # 破裂（ぱっと 出る 短い ノイズ）
        b0, bd, lo, hi, ba = S['burst']
        e = np.exp(-np.maximum(t - b0, 0) / max(bd / 2.5, 1e-4)) * (t >= b0) * (t < b0 + bd * 2)
        out = out + _noise(rng, n, lo, hi) * e * .25 * ba
    if S.get('fric'):                                                             # こすれる 音（ち・き）
        f0_, f1_, lo, hi, fa = S['fric']
        e = _track([(0, 0), (f0_, 0), (f0_ + .012, .55), (f1_ - .012, 1), (f1_ + .004, 0), (d, 0)], n)
        out = out + _noise(rng, n, lo, hi) * e * .25 * fa
    out = signal.sosfilt(signal.tf2sos(*biquad('shelf_hi', 4500, .7071, 3.0)), out)  # 明るさ（口の ひびきの 高い 所の 落ちこみを 少し おぎなう）
    out = hp(out, 90)
    return fade(out, .001, .02)


# ---------- 声の ことば：超プレミアムの 声（voice）と 同じ しくみ（フォルマント合成）で 音を つないで ことばに ----------
# まさちゃん「一枚目のこの爆発のシーンで、超プレミアムど的中演出で使っている声で、いやーーーん！！！て音声入れて！」
#           「二枚目のシーンで、超プレミアムど的中演出で使っている声で、おめでとう御座います入れて！」
VOWELS['a'] = ((920, 1450, 2950, 4000, 4950, 6300, 7600, 9000), (90, 110, 160, 250, 300, 500, 700, 900))
_WIDE = (90, 160, 220, 300, 350, 500, 700, 900)
PH = dict(  # 音の かた：F（口の ひびき 8つ）・B（はば）・av（声の 大きさ）・burst（破裂：高さの 下・上・大きさ・長さ）・asp（息：長さ・大きさ）・fric（こすれる 音：下・上・大きさ）
    y=dict(F=(300, 2550, 3300, 4300, 5000, 6400, 7700, 9100), B=(70, 140, 220, 260, 300, 500, 700, 900), av=.85),
    m=dict(F=(290, 1150, 2350, 3700, 4900, 6200, 7600, 9000), B=(70, 350, 450, 550, 650, 750, 850, 950), av=.36),
    n=dict(F=(290, 1650, 2650, 3800, 4900, 6200, 7600, 9000), B=(70, 350, 450, 550, 650, 750, 850, 950), av=.36),
    N=dict(F=(300, 1350, 2550, 3800, 4900, 6200, 7600, 9000), B=(70, 300, 420, 550, 650, 750, 850, 950), av=.5),
    d=dict(F=(250, 1700, 2700, 3900, 4900, 6200, 7600, 9000), B=_WIDE, av=.1, burst=(3000, 6500, 1.3, .006)),
    g=dict(F=(260, 1950, 2500, 3900, 4900, 6200, 7600, 9000), B=_WIDE, av=.1, burst=(1500, 3800, 1.5, .01)),
    t=dict(F=(320, 1750, 2700, 3900, 4900, 6200, 7600, 9000), B=(250, 200, 250, 300, 350, 500, 700, 900), av=0.0, burst=(3000, 8000, 2.0, .006), asp=(.022, .35)),
    s=dict(F=(350, 1650, 2800, 3900, 4900, 6200, 7600, 9000), B=(250, 200, 250, 300, 350, 500, 700, 900), av=0.0, fric=(4200, 9500, .55)),
    z=dict(F=(280, 1650, 2700, 3900, 4900, 6200, 7600, 9000), B=(120, 180, 240, 300, 350, 500, 700, 900), av=.3, fric=(3500, 8500, .45)),
    U=dict(F=VOWELS['u'][0], B=(200, 200, 250, 300, 350, 500, 700, 900), av=0.0, asp=(1.0, .28)),     # 声の 出ない う（「ます」の す）
    pause=dict(F=VOWELS['o'][0], B=_WIDE, av=0.0))                                                   # 、（声を 止める 間）
for _v, (_F, _B) in VOWELS.items():
    PH[_v] = dict(F=_F, B=_B, av=1.0)
IYAN = (('i', .12, 73), ('y', .07, (77, 79)), ('a', 1.15, (80, 74)), ('N', .38, (73, 68)))         # いやーーーーん！！！（まさちゃん「もっと長く大きな声で！」：ぐっと 上がって ゆれながら 下がる）
OMEDETOU = (('o', .11, (70, 71)), ('m', .06, 74), ('e', .10, 76), ('d', .03, None), ('e', .09, 76), ('t', .045, None), ('o', .10, 75),
            ('o', .12, (75, 73.5)), ('g', .035, None), ('o', .08, 73), ('z', .06, 74.5), ('a', .10, 77), ('i', .09, 76), ('m', .05, 75),
            ('a', .1, (75, 73.5)), ('s', .08, None), ('U', .07, None))                                # おめでとう御座います！（明るく 言いきる）
IYAN_END = (('i', .1, 74), ('y', .06, (78, 80)), ('a', .8, (81, 75)), ('N', .3, (74, 69)))     # いやーーーーん！（さいごの 照れ：大きな 声・カットインの いやーーーーん より 少し 短く）
# まさちゃん「もっと息が混じったリアルな人間みたいな大きな声で！」→（のばす 言い方を 試して）→「おめでとう御座います！にして！」
# →「おめでとう御座います の後にいやーーーーん！入れて！」


def inhale(d, rng):
    """すぅっ：話す 前に 息を すう 音（口の ひびきを 通る ノイズ・だんだん 大きく → すっと 止まる）"""
    n = n_(d)
    t = tl(n)
    Fv, Bv = VOWELS['a']
    x = hp(rng.standard_normal(n), 500)
    x = _tract_tracks(x, [np.full(n, float(F)) for F in Fv], [np.full(n, float(B) * 2.2) for B in Bv])
    e = np.clip(t / (d * .8), 0, 1) ** 1.5 * np.clip((d - t) / .04, 0, 1)
    x = x * e
    return fade(x / (np.sqrt(np.mean(x[n // 2:] ** 2)) + 1e-12) * .25, .005, .01)


def applause(d, rng, people=36, rate=(3.6, 5.4), swell=.9, release=1.2):
    """パチパチパチ：たくさんの 人の 拍手（ひとりずつ 速さ・手の 音・左右が ちがう・だんだん 大きく → さいごは ひく）。左右 2ch"""
    n = n_(d)
    out = np.zeros((n, 2))
    kinds = []
    for _ in range(14):                                                         # 手の 音（14種：手の 合わせ方で 高さ・長さが ちがう）
        k = n_(rng.uniform(.02, .035))
        tk = tl(k)
        c = rng.uniform(900, 2600)
        y = bp(rng.standard_normal(k), c * .55, min(c * 2.4, 9000)) * np.exp(-tk / rng.uniform(.004, .009))
        kinds.append(y / (np.abs(y).max() + 1e-12))
    for _ in range(people):
        pan = rng.uniform(-.9, .9)
        a = (pan + 1) * np.pi / 4
        lr = np.array([np.cos(a), np.sin(a)]) * np.sqrt(2)
        g0 = rng.uniform(.35, 1.0)
        per = 1 / rng.uniform(*rate)
        tt = rng.uniform(0, swell * .6)
        while tt < d:
            y = kinds[rng.integers(len(kinds))] * g0 * rng.uniform(.75, 1.0)
            i = n_(tt)
            j = min(n, i + len(y))
            out[i:j] += y[:j - i, None] * lr[None, :]
            tt += per * rng.uniform(.88, 1.12)
    t = tl(n)
    e = np.clip(t / swell, 0, 1) ** 1.5 * np.clip((d - t) / release, 0, 1)
    out *= e[:, None]
    return out / (np.sqrt(np.mean(out[n_(swell):n - n_(release)] ** 2)) + 1e-12) * .25


def _tract_tracks(x, Fk, Bk):
    for F, B in zip(Fk, Bk):
        x = _reson(x, F, B)
    return x


SAY_LOUD = dict(oq=.5, breath=.08, bright=9500, jit=.16, shim=.05, vib=.45)        # 大きな 声（のどを しめて 明るく・ゆれ 大きく）
SAY_BREATHY = dict(oq=.7, breath=.32, bright=4800, jit=.2, shim=.08, vib=.22, air=.14)   # 息の まじった 人の 声（のどが ひらいて やわらかく・高い 所に 息）


def say(seq, rng, vib=.32, oq=.62, breath=.05, bright=7000, jit=.12, shim=.04, air=None):
    """ことば（音の ならび：(音, 長さ, 高さ（MIDI・(はじめ, おわり)・None）)）→ 声。母音の 大きさ（RMS）を 0.25 に そろえる（voice と 同じ）。
       oq：のどの ひらく 割合・breath：息の まざる 量・bright：声の 明るさ（Hz）・jit／shim：高さ／大きさの ゆらぎ・air：高い 所の 息（ふつうは PC_AIR）"""
    starts = np.cumsum([0.0] + [d for _, d, _ in seq])
    D = float(starts[-1])
    n = n_(D + .03)
    t = tl(n)
    tin = {'stop': .045, 'nas': .03, 'v': .05, 'fric': .02}

    def kind(p):
        return 'fric' if p == 'pause' else 'stop' if p in 'dgt' else 'nas' if p in 'mnN' else 'fric' if p in 'szU' else 'v'
    # 口の ひびき（となりの 音へ なめらかに：止める 音の あとは 母音へ すばやく）
    keysF = [[] for _ in range(8)]
    keysB = [[] for _ in range(8)]
    for i, (p, d, _) in enumerate(seq):
        s0, s1 = starts[i], starts[i + 1]
        prev = kind(seq[i - 1][0]) if i else 'v'
        a = s0 + (0.0 if i == 0 else min(d * .45, {'stop': .045, 'nas': .028, 'fric': .03, 'v': .035}[prev] if kind(p) == 'v' else .012))
        b = s1 - (min(d * .45, .02) if kind(p) == 'v' and i + 1 < len(seq) and kind(seq[i + 1][0]) == 'v' else (0.0 if kind(p) == 'stop' else min(d * .3, .01)))
        if b < a:
            a = b = (s0 + s1) / 2
        for k in range(8):
            keysF[k] += [(a, PH[p]['F'][k]), (b, PH[p]['F'][k])]
            keysB[k] += [(a, PH[p]['B'][k]), (b, PH[p]['B'][k])]
    Fk = [_track(sorted(kf) + [(t[-1] + 1e-3, kf[-1][1])], n) for kf in keysF]
    Bk = [_track(sorted(kb) + [(t[-1] + 1e-3, kb[-1][1])], n) for kb in keysB]
    # 声の 大きさ（音ごと・つなぎは 8ミリ秒）。さいごの 音は 後ろ半分で 消える
    ka = [(0.0, 0.0)]
    rr = .008
    for i, (p, d, _) in enumerate(seq):
        s0, s1 = starts[i], starts[i + 1]
        av = PH[p]['av']
        if i == len(seq) - 1 and av > 0:
            ka += [(s0 + rr, av), (s0 + d * .4, av), (s1, 0.0)]
        else:
            ka += [(s0 + rr, av), (s1 - rr, av)]
    ka.append((t[-1] + 1e-3, 0.0))
    av = _track(sorted(ka), n)
    # 声の 高さ：出だしは 少し 下から すくい上げる・長い 母音は ゆれ（ビブラート）・さいごは 下がる
    kn = []
    first = True
    for i, (p, d, note) in enumerate(seq):
        if note is None:
            continue
        s0, s1 = starts[i], starts[i + 1]
        if isinstance(note, tuple):
            pts = [(s0 + d * .15, note[0]), (s1 - d * .15, note[1])]
        else:
            pts = [((s0 + s1) / 2, note)]
        if first:
            kn.append((s0, pts[0][1] - 2.0))
            first = False
        kn += pts
    kn.append((D, kn[-1][1] - 2.5))
    st = _track(kn, n)
    vb = np.zeros(n)
    for i, (p, d, _) in enumerate(seq):
        if PH[p]['av'] >= 1.0 and d > .25:
            s0, s1 = starts[i], starts[i + 1]
            ramp = np.clip((t - s0 - .14) / .1, 0, 1) * (t < s1)
            vb += vib * np.sin(2 * np.pi * 6.0 * (t - s0)) * ramp
    jt = lp(rng.standard_normal(n), 30, 1)
    drift = lp(rng.standard_normal(n), 3, 1)                                     # ゆっくり ゆれる 高さ（人の 声らしく）
    f0 = 440.0 * 2 ** ((st + vb + jt / (np.std(jt) + 1e-12) * jit + drift / (np.std(drift) + 1e-12) * jit * .8 - 69) / 12)
    # 声帯の 音（voice と 同じ しくみ・oq と 明るさを えらぶ）
    up = 4
    ph = np.cumsum(np.repeat(f0, up) / (SR * up)) % 1.0
    tau = ph / oq
    g = signal.resample_poly(np.where(ph < oq, 2 * tau - 3 * tau ** 2, 0.0), 1, up)[:n]
    g = lp(g, bright, 1)
    gate = signal.resample_poly((ph < oq).astype(float), 1, up)[:n]
    sh = lp(rng.standard_normal(n), 40, 1)
    sh = 1 + shim * sh / (np.std(sh) + 1e-12)
    br = hp(rng.standard_normal(n), 400) * (.35 + .65 * gate)
    voiced = _tract_tracks(g * av * sh + br * breath * av, Fk, Bk)
    vm = av > .9
    k_ = .25 / (np.sqrt(np.mean(voiced[vm] ** 2)) + 1e-12)
    voiced *= k_
    ai = hp(g * av * sh + br * (.08 + breath) * av, 3200, 2)
    out = voiced + ai / (np.sqrt(np.mean(ai[vm] ** 2)) + 1e-12) * .25 * (PC_AIR if air is None else air)
    # 息・破裂・こすれる 音
    for i, (p, d, _) in enumerate(seq):
        s0, s1 = starts[i], starts[i + 1]
        P = PH[p]
        if P.get('asp'):
            ad, aa = P['asp']
            a0, a1 = (s0, s1) if p == 'U' else (s1, s1 + ad)
            e = _track([(0, 0), (a0, 0), (a0 + .004, 1), (a1 - .006, .7), (a1 + .01, 0), (t[-1] + 1e-3, 0)], n)
            asp = _tract_tracks(hp(rng.standard_normal(n), 300) * e, Fk, Bk)
            m = e > .5
            out = out + asp / (np.sqrt(np.mean(asp[m] ** 2)) + 1e-12) * .25 * aa
        if P.get('burst'):
            lo, hi, ba, bd = P['burst']
            e = np.exp(-np.maximum(t - s1, 0) / max(bd / 2.5, 1e-4)) * (t >= s1) * (t < s1 + bd * 2)
            out = out + _noise(rng, n, lo, hi) * e * .25 * ba
        if P.get('fric'):
            lo, hi, fa = P['fric']
            f0_ = s0 + (.012 if p == 'z' else 0.0)
            e = _track([(0, 0), (f0_, 0), (f0_ + .015, 1), (s1 - .01, 1), (s1 + .008, 0), (t[-1] + 1e-3, 0)], n)
            out = out + _noise(rng, n, lo, hi) * e * .25 * fa
    out = signal.sosfilt(signal.tf2sos(*biquad('shelf_hi', 4500, .7071, 3.0)), out)
    out = hp(out, 90)
    return fade(out, .002, .03)


VOICE_IYAN = (.1, -10.0, 1.7)    # いやーーーん！！！：カットインの 大きな 爆発の はじまりから 0.1秒・その 間 まわりを 10dB 小さく・声の 大きさ
VOICE_OMEDETOU = (.62, -9.0, 1.7, .12)   # おめでとう御座います！いやーーーーん！：鳥居の ファンファーレ（パッパッパーン）の 大きな 和音の あと・その 間 まわりを 9dB 小さく・
                                         # 声の 大きさ・いやーん の 前の 間（秒）。ボードの 前に 言いおわる ように ③ の さいごを 少し のばす（kami_film3.XN）
PC_VOICE = (('do', 69), ('te', 71), ('ki', 72), ('chu', 72), ('u', 74))    # ①〜⑤の 声：どぉ！（A4）・てぇ！（B4）・きぃ！（C5）・ちゅ！（C5）・う！（D5）。だんだん 高く
PC_AIR = .05                                                                      # 声の 高い 所の 明るさ（母音の 大きさに たいして）
PC_VOICE_G = 1.1                                                                  # 声の 大きさ（ミックスの 中で：ほかの 音より 前に）
PC_DUCK = (-10.0, -6.0, -6.0, -6.0, -6.0)                                         # 声の 間 まわりの 音を 小さく する 量（dB。①は 白い 光の 鐘の ひびきが のこって いるので 深く）


PC_NOTES = (72, 74, 76, 77, 79)                                                   # ど・て・き・ちゅ・う ＝ ド・レ・ミ・ファ・ソ（C5〜G5）。最後の ど的中 ＝ 高い ド（プレミアム）
PC_CHORDS = ((60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60), (55, 59, 62))  # ①〜⑤の 和音：C・G・Am・F・G → 最後 C


def sfx_pc(with_voice=False):
    """押してから（秒は premium_cute.py の PC_T・SCREENS）：0 ポン＋キラリン → ハートが 降って つもる（オルゴールの ポロポロが だんだん 多く 高く・和音が ふくらむ）
       → BURST パーン＋ポポポポン（まん中から じゅんに はじける）→ W キラーーン（白い 光）
       → ①〜⑤ 入ってくる 方から シュッ → 止まった 時に ポン＋鐘（ド・レ・ミ・ファ・ソ）・④ は チュッ＋ウィンクで キラッ（下で オルゴールの 分散和音と 手拍子）
       with_voice=True（超プレミアムど的中：sfx_zp）：止まった 時の 鐘と チュッ を 声「どぉ！」「てぇ！」「きぃ！」「ちゅ！」「う！」に（voice：だんだん 高く・その 間 まわりを 小さく）。
         まさちゃん「プレミアムど的中、音を変えて！ … これでおとだせる？」→「これ超プレミアムど的中の音声に使用して！」（超プレミアムだけ 声・プレミアムは 前の 音）
       → FIN ふわっ → ジャーン（ど的中・高い ド）→ ドクン・ドクン（ハートの 鼓動）・シャララ↑（のぼる ハート）
       → RES ヒューン↑（ハートが 上へ）→ ポンッ（ボード）→ 買い目 ピン・ピン・ピン（0.08秒おき）→ 合計 キラリーン"""
    T, SC = read_pc_times()
    S, IN, FIN, RES, FILL, B = T['S'], T['IN'], T['FIN'], T['RES'], T['FILL'], T['BURST']
    W1 = T['W'][1]
    t0b = RES + .45                                                                # ボードの 行（gen_fx の --t0）
    mx = Mix(t0b + 2.4, 41)
    r = mx.rng
    # --- 0：ポン＋キラリン ---
    mx.add(pop(700, 380, .12, r, .2), 0, .7, rv=.15)
    for i, m in enumerate((84, 88, 91, 96)):
        mx.add(bell(mtof(m), 1.0, idx=1.6, tau=.35), .03 + .05 * i, .15, (-.3, -.1, .1, .3)[i], rv=.35)
    # --- 0〜FILL：ハートが 降って つもる（オルゴールの ポロポロ：つもるほど 多く・高く）＋ 和音が ふくらむ ＋ シュワーッ ---
    penta = (72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98)
    tt = .5
    while tt < FILL:
        u = (tt - .5) / (FILL - .5)
        m = penta[min(len(penta) - 1, int(u * 7) + int(r.integers(0, 5)))]
        mx.add(tine(mtof(m), .9, .35), tt, .09 + .06 * u, r.uniform(-.8, .8), rv=.35)
        tt += .12 - .075 * u + r.uniform(-.015, .015)
    mx.add(pad((60, 64, 67, 74), FILL, FILL * .9, .25, .45), .1, .2, rv=.4)
    w = nsweep(FILL, 300, 5000, .5, r) * np.linspace(0, 1, n_(FILL)) ** 2
    mx.add(w, .1, .05, rv=.3)
    # --- BURST：パーン＋ポポポポン（まん中から 外へ）---
    mx.add(pop(420, 160, .2, r, .35), B, .8, rv=.15)
    mx.add(kick(140, 55, .4, 1.6, .12, .2, r), B, .4, rv=.05)
    for k in range(10):
        mx.add(pop(1500 + 120 * k, 900, .07, r, .15), B + T['CHAIN'] * k / 9 + r.uniform(0, .01), .26, r.uniform(-.8, .8), rv=.2)
    # --- W：キラーーン（白い 光）---
    d = W1 - B + .05
    mx.add(nsweep(d, 2000, 9000, .4, r) * np.linspace(0, 1, n_(d)) ** 2, B, .07, rv=.3)
    for i, m in enumerate((84, 88, 91, 96, 100)):
        mx.add(bell(mtof(m), 2.2, idx=1.8, tau=.9), W1 + .012 * i, .18, (-.4, -.2, 0, .2, .4)[i], rv=.5)
    sparkle(mx, W1, .6, 10, (96, 98, 100, 103, 105, 108), .06, r)
    mx.add(pad((60, 64, 67, 72), .9, .02, .7, .3), W1, .12, rv=.5)
    # --- ①〜⑤：シュッ（入ってくる 方から）→ ポン＋鐘（ド・レ・ミ・ファ・ソ）／超プレミアムは 声（どぉ！・てぇ！・きぃ！・ちゅ！・う！：母音が 止まる 時に 出る）。
    #     下で オルゴールの 分散和音・ベース・手拍子（止まる 時が 2拍目）---
    vr = np.random.default_rng(77)                                                 # 声の 乱数（ほかの 音の 乱数と 分ける）
    vq = []                                                                        # 声は まわりの 音を 置いて から（その 間 まわりを 小さく して）のせる
    for i, (text, face, frm, s_txt) in enumerate(SC):
        ti = S[i]
        land = ti + IN * .72
        d = land - ti + .05
        f0, f1 = {'L': (500, 2600), 'R': (500, 2600), 'B': (300, 2800), 'T': (2800, 500), 'C': (400, 2200)}[frm]
        wh = nsweep(d, f0, f1, .45, r) * np.sin(np.linspace(0, np.pi, n_(d))) ** 2
        p0 = {'L': -.9, 'R': .9}.get(frm, 0.0)
        mx.add(wh, ti, .09, np.linspace(p0, 0, 8), rv=.25)
        if with_voice:                                                             # 超プレミアム：声（まわりを 置いた あとで のせる）
            mx.add(pop(600, 300, .1, r, .15), land, .2, rv=.12)
            syl, note = PC_VOICE[i]
            vq.append((syl, note, land - SYL[syl]['von']))
        else:                                                                      # プレミアム：ポン＋鐘（ド・レ・ミ・ファ・ソ）
            m = PC_NOTES[i]
            mx.add(pop(600, 300, .1, r, .15), land, .45, rv=.12)
            mx.add(bell(mtof(m + 12), 1.4, idx=1.5, tau=.55), land, .28, rv=.4)
            mx.add(tine(mtof(m), 1.4, .7), land, .28, rv=.35)
            mx.add(tine(mtof(m + 24), .8, .3), land + .01, .09, rv=.35)
        sparkle(mx, land, .35, 4, (96, 100, 103, 108), .045, r)
        for k in range(4):                                                         # とびちる 小さな ハート
            mx.add(pop(1700 + 150 * k, 1100, .06, r, .1), land + .03 + .04 * k, .1, r.uniform(-.7, .7), rv=.2)
        if text.startswith('ちゅ') and with_voice:                                 # ウィンクの キラッ（声「ちゅ！」の あと）
            mx.add(bell(mtof(103), .8, idx=1.0, tau=.25), land + .3, .11, .35, rv=.35)
        elif text.startswith('ちゅ'):                                              # チュッ＋ウィンクの キラッ
            mx.add(kiss(r), land + .06, .5, .1, rv=.15)
            mx.add(bell(mtof(103), .8, idx=1.0, tau=.25), land + .22, .11, .35, rv=.35)
        base = land - .3
        ch = PC_CHORDS[i]
        arp = (ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[2] + 12)
        for k in range(8):
            mx.add(tine(mtof(arp[k]), .5, .2), base + .15 * k, .055, (-.3, .3)[k % 2], rv=.3)
        for k in (0, 2):
            mx.add(pluck(ch[0] - 12, .3, .15), base + .3 * k, .1, rv=.15)
        for k in (1, 3):
            mx.add(clap(r), base + .3 * k, .07, rv=.2)
    for k, (syl, note, ts) in enumerate(vq):                                        # 声：その 間 まわりの 音を 小さく（PC_DUCK dB）して のせる
        mx.duck(ts, ts + SYL[syl]['d'], PC_DUCK[k])
        mx.add(voice(syl, note, vr), ts, PC_VOICE_G, rv=.22)
    # --- FIN：ふわっ → ジャーン（ど的中・高い ド）---
    hit = FIN + .28
    mx.add(nsweep(.3, 400, 3000, .45, r) * np.linspace(0, 1, n_(.3)) ** 2, FIN, .1, rv=.3)
    for i, m in enumerate((60, 64, 67, 72, 76, 79)):
        mx.add(brass(m + 12, 1.1, r), hit, .09, (i / 5 - .5) * .8, rv=.35)
    for i, m in enumerate((84, 88, 91, 96)):
        mx.add(bell(mtof(m), 2.0, idx=1.6, tau=.8), hit + .01 * i, .2, (-.3, -.1, .1, .3)[i], rv=.5)
    mx.add(tine(mtof(84), 1.6, .8), hit, .25, rv=.4)
    mx.add(kick(150, 55, .5, 1.6, .15, .2, r), hit, .45, rv=.05)
    mx.add(crash(r, 2.0, .7), hit, .08, rv=.4)
    sparkle(mx, hit, .5, 8, (96, 100, 103, 108), .055, r)
    for k in range(6):
        mx.add(pop(1600 + 140 * k, 1000, .06, r, .1), hit + .02 + .03 * k, .1, r.uniform(-.8, .8), rv=.2)
    mx.add(pad((48, 60, 64, 67, 72), RES - FIN + .6, .3, .6, .4), FIN, .15, rv=.45)
    # ドクン・ドクン（ハートの 鼓動：大きくなる 2回）
    for tb in (FIN + .5, FIN + 1.4):
        for k, dt in enumerate((.16, .42)):
            mx.add(kick(110, 50, .35, 1.6, .1, .05, r), tb + dt, (.5, .36)[k], rv=.08)
    # シャララ↑（のぼる ハート）
    for k in range(3):
        t = FIN + .6 + .55 * k
        for j, m in enumerate((84, 86, 88, 91, 93, 96, 98, 100)):
            mx.add(tine(mtof(m), .6, .25), t + .045 * j, .045, r.uniform(-.6, .6), rv=.4)
    # --- RES：ヒューン↑（ハートが 上へ）→ ポンッ（ボード）→ 買い目 → 合計 ---
    n = n_(.5)
    t = tl(n)
    mx.add(fade(np.sin(phase(900 * 2.2 ** np.clip(t / .4, 0, 1), n)) * np.minimum(t / .03, 1) * np.clip((.5 - t) / .12, 0, 1)), RES - .1, .1, rv=.3)
    mx.add(pop(560, 260, .14, r, .2), RES + .12, .6, rv=.15)
    for i, m in enumerate((96, 100, 103)):
        mx.add(tine(mtof(m), .7, .3), t0b + .08 * i, .2, (-.2, 0, .2)[i], rv=.35)
        mx.add(coin(3600, r, .3, False), t0b + .08 * i, .07, rv=.2)
    tt = t0b + .08 * 3
    for i, m in enumerate((84, 88, 91, 96)):
        mx.add(bell(mtof(m), 1.6, idx=1.4, tau=.6), tt + .015 * i, .2, (-.3, -.1, .1, .3)[i], rv=.45)
    mx.add(coin(3000, r, .5), tt, .2, -.2, rv=.25)
    mx.add(coin(4200, r, .45), tt + .06, .15, .25, rv=.25)
    mx.add(pad((60, 64, 67, 72), 1.0, .2, .8, .35), tt, .14, rv=.45)
    return mx.render(1.6, target=-14)


def sfx_zp():
    """超プレミアムど的中（手書き・鉛筆）の タップの 音：プレミアムの 音の ①〜⑤を 声に（PUSHの 音は ど的中と 同じ）"""
    return sfx_pc(with_voice=True)


# ---------- 神様的中（ホ長調・嵐の 雷と 爆発・金管と 合唱・金の 粒。秒は kami.py の GD_T と cr_frames・BOLT_D・RIBBONS。PUSHの 音は ど的中と 同じ） ----------
def read_gd():
    """kami.py の 時刻（見本の 動きと 音の 時刻を そろえる。kami.py は 軽いので そのまま 読みこむ）"""
    sys.path.insert(0, HERE)
    import kami
    return kami


CHOIR_A = ((730, 1090, 2440, 3400, 4300), (90, 110, 160, 250, 300))      # 「あ」の ひびき（大人の 声）
CHOIR_A_HI = ((850, 1220, 2810, 3800, 4950), (100, 120, 170, 260, 320))  # 高い 声の「あ」


def choir(ms, d, rng, att=.35, rel=.6, n_v=3, bright=1.0):
    """ああぁぁ：合唱（声の しくみを 計算で まねる：のどの 音 → 口の ひびき「あ」。1つの 高さに 声 n_v 人・少しずつ ずらす・ビブラート・息）→ ステレオ"""
    n = n_(d + rel)
    t = tl(n)
    a = np.minimum(t / att, 1) ** 1.5 * np.clip((d + rel - t) / rel, 0, 1)
    out = np.zeros((n, 2))
    for i, m in enumerate(ms):
        F, B = CHOIR_A_HI if m >= 60 else CHOIR_A
        for v in range(n_v):
            det = rng.uniform(-14, 14)
            vib = .18 * np.sin(2 * np.pi * rng.uniform(4.6, 5.6) * t + rng.uniform(0, 6.28)) * np.clip((t - .25) / .4, 0, 1)
            drift = lp(rng.standard_normal(n), 3, 1)
            drift = drift / (np.std(drift) + 1e-9) * .06
            f0 = mtof(m + (det / 100) + vib + drift)
            ph = np.cumsum(f0 / SR) % 1.0
            g = (ph < .6) * (2 * (ph / .6) - 3 * (ph / .6) ** 2)                 # のどの ふるえ（ひらいて とじる）
            g = g - np.mean(g)
            src = lp(g, 5000, 1) + .04 * hp(rng.standard_normal(n), 500)
            y = np.zeros(n)
            for k, (f, b) in enumerate(zip(F, B)):
                r = np.exp(-np.pi * b / SR)
                bb, aa = [1 - r], [1, -2 * r * np.cos(2 * np.pi * f / SR), r * r]
                y += signal.lfilter(bb, aa, src) * (1, .7, .45 * bright, .3 * bright, .2 * bright)[k]
            y = y / (np.std(y) + 1e-9)
            p = rng.uniform(-.8, .8)
            ang = (p + 1) * np.pi / 4
            out[:, 0] += y * a * np.cos(ang)
            out[:, 1] += y * a * np.sin(ang)
    return out / (len(ms) * n_v) * 1.4


def laser(f0, f1, d, rng):
    """ズバァン：光の 帯（高い 音が すっと 下がる＋明るい ノイズ）"""
    n = n_(d)
    t = tl(n)
    f = f1 + (f0 - f1) * np.exp(-t / (d / 4))
    x = .6 * np.sin(phase(f, n)) + .3 * np.sin(phase(f * 1.5, n)) + .5 * bp(rng.standard_normal(n), 2500, 9000)
    return fade(x * np.exp(-t / (d / 2.5)), .001, .02)


def whoosh(d, rng, f0=3000, f1=400):
    """ヒュンッ：岩が そばを 通る（ノイズの 高さが 下がる・だんだん 大きく → すっと 消える）"""
    n = n_(d)
    t = tl(n)
    x = nsweep(d, f0, f1, .6, rng)
    a = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return fade(x * a, .005, .02)


def buzz(d, rng, f=118):
    """ビリビリ：電気の うなり（少し ずらした 四角い 波 2つ＋こまかい ノイズ・大きさが ゆれる）"""
    n = n_(d)
    t = tl(n)
    x = .5 * np.sign(np.sin(phase(f * (1 + .01 * np.sin(2 * np.pi * 7 * t)), n))) + .35 * np.sign(np.sin(phase(f * 2.01, n)))
    x = bp(x, 300, 5000) + .5 * bp(rng.standard_normal(n), 2000, 9000)
    am = .55 + .45 * np.sign(np.sin(2 * np.pi * 23 * t + rng.uniform(0, 6)))
    return fade(x * lp(am, 80, 1), .01, .05)


def jingle(mx, t0, dur, count, g, rng, pan=.8):
    """ジャラジャラ：金の 粒（コインより 少し 低く 重い）"""
    for _ in range(count):
        mx.add(coin(rng.uniform(1800, 3600), rng, rng.uniform(.25, .5)), t0 + dur * rng.uniform(0, 1) ** 1.5, g * rng.uniform(.5, 1), rng.uniform(-pan, pan), rv=.3)


def sfx_gd():
    """神様的中の タップの 音（秒は kami.py の GD_T・cr_frames・BOLT_D・RIBBONS）：
       0 ドガーン!!（光の 爆発）＋キィィン → ゴォッ（赤い 炎）→ 青い 嵐：ゴゴゴ（低い うなり）＋ゴォォォ（光の 滝）＋ドン・ブォォン↑・シュワーッ↑・キラッ（ドームが ひろがる）
       ＋ギュイーン・バリバリ（ピンクの 電気）＋バリバリッ・ドーン（大きな 雷 6本）＋ビリビリ・ジジジ・バチッ（ドームの 電気）＋シュンッ（白い 光の 帯）＋ヒュンッ（岩）
       → ドガーン＋ジャラジャラ（金の 輪と 金の 爆発）＋シュワーッ↑ → パァーン（白）→ ジャーン（金管と 合唱：ミ）万馬券 → ジャーン（ラ）天眼 → シュワーッ↑ → ドーン＋どら＋ジャーン（白 → 4行の 文）＋ああぁぁ（合唱）＋キラーン（光の 帯）
       → シュワーッ↑ → ドガーン!!＋ジャラジャラ（金の 粒）→ ドン（神）・ドン（様）・ドン（的）・ドン（中）→ ドガーン!!＋ジャーン（神様／的中）→ グォォ↑（ひく）→ パッパッパーン（ファンファーレ）
       → シャラララ↑ → ポンッ（ボード）→ 買い目 ピン・ピン・ピン → 合計 キラリーン＋メダル"""
    G = read_gd()
    T = G.GD_T
    RES = T['RES']
    t0b = RES + .45
    mx = Mix(t0b + 2.0, 61)
    r = mx.rng
    E = (40, 47, 52, 56)          # ホ長調（E2・B2・E3・G#3）
    A_ = (45, 52, 57, 61)         # ラ（A2・E3・A3・C#4）
    # --- ① 光の 爆発（0）・白 → 赤い 炎 ---
    mx.add(boom(110, 30, 1.4, .45, .05, 2.6, r), 0, .9 * FZ_LOW, rv=.1)
    mx.add(explosion(r, 1.0, .9), .01, .75, rv=.3)
    mx.add(arc_zap(.35, r, 900), 0, .45, rv=.2)
    n = n_(1.0)
    tt = tl(n)
    ring = np.sin(phase(5200 - 1400 * (1 - np.exp(-tt / .3)), n)) * np.exp(-tt / .35) * .35          # キィィン
    mx.add(ring, .02, .22, rv=.4)
    fr0, fr1 = T['FIRE']
    mx.add(nlow(fr1 - fr0 + .3, 2500, 300, .2, r) * np.exp(-tl(n_(fr1 - fr0 + .3)) / .25), fr0, .35, rv=.3)      # ゴォッ
    # --- 青い 嵐（第4.46版）：ゴォォォ（光の 滝）＋ドン・ブォォン↑・シュワーッ↑（ドームが ひろがる）＋ギュイーン・バリバリ（ピンクの 電気）
    #     ＋バリバリッ・ドーン（大きな 雷）＋ビリビリ・ジジジ・バチッ（ドームの 電気：コマごと）＋シュンッ（白い 光の 帯）＋ヒュンッ（岩）---
    s0, s1 = T['STORM']
    mx.add(rumble(s1 - s0 + .2, r, 150, 9), s0, .5, rv=.3)
    mx.add(growl(30.9, 41.2, s1 - s0, s1 - s0, 2.0), s0, .16, rv=.2)                           # 低い うなり
    dw = s1 - s0 + .1
    tw = tl(n_(dw))
    mx.add(nlow(dw, 3400, 1900, 1.0, r) * np.minimum(tw / .08, 1) * np.clip((dw - tw) / .3, 0, 1), s0, .26, rv=.35)   # ゴォォォ（光の 滝）
    d0, d1, d2 = T['DOME']
    mx.add(boom(72, 28, 1.2, .4, .05, 2.4, r), d0, .75 * FZ_LOW, rv=.15)                      # ドン（ドームが ひろがる）
    mx.add(growl(41.2, 98.0, d1 - d0 + .3, d1 - d0, 2.2), d0, .2, rv=.25)                     # ブォォン↑
    dd = d1 - d0 + .06
    mx.add(nsweep(dd, 300, 6500, .5, r) * np.linspace(0, 1, n_(dd)) ** 1.5, d0, .28, rv=.35)   # シュワーッ↑
    for j, m in enumerate((76, 83, 88, 95)):                                                     # キラッ（ガラスの ドーム）
        mx.add(bell(mtof(m), .9, idx=1.2, tau=.35), d1 - .03 + .025 * j, .07, (j / 3 - .5) * .9, rv=.5)
    g0, g1, g2, g3 = T['SURGE']
    mx.add(buzz(g3 - g0 + .12, r, 74), g0, .3, rv=.2)                                          # ギュイーン（ピンクの 電気）
    mx.add(crackle(g3 - g0, 380, r), g0, .4, -.5, rv=.25)
    mx.add(crackle(g3 - g0, 300, r), g0, .32, .5, rv=.25)
    mx.add(arc_zap(g3 - g0, r, 700), g0, .35, rv=.25)
    c0, c1 = T['CRACK']
    mx.add(buzz(c1 - c0 + .1, r), c0, .13, rv=.15)                                            # ビリビリ（ドームの 電気の うなり）
    mx.add(crackle(c1 - c0, 140, r), c0, .22, rv=.25)                                          # ジジジ
    for t, pan in G.cr_frames():                                                               # ドームの 電気：コマごとに バチッ
        mx.add(arc_zap(.05, r, 900), t, .2, pan, rv=.2)
    for t, (a, b, tone) in zip(T['BOLTS'], G.BOLT_D):                                         # 大きな 雷：バリバリッ＋ドーン
        pan = ((a[0] + b[0]) / 390 - 1) * .8
        mx.add(arc_zap(.12, r, 1400), t, .5, pan, rv=.25)
        mx.add(explosion(r, .35, 1.5), t + .005, .35, pan, rv=.35)
        mx.add(boom(85, 30, .9, .3, .03, 2.4, r), t + .01, .42 * FZ_LOW, rv=.2)
    for p, t0, t1 in G.RIBBONS:                                                                # シュンッ（白い 光の 帯）
        mx.add(laser(4200, 1200, .3, r), t0, .13, (p[0][0] / 195 - 1) * .7, rv=.35)
    for k, t in enumerate(T['ROCKS']):
        pan = (-.7, .7)[k % 2]
        mx.add(whoosh(.5, r), t, .3, np.linspace(0, pan * 1.2, 12), rv=.2)
    # --- 金の 輪（立体の かたまり）と 金の 爆発 → 白（① → ②）---
    r0 = T['RING'][0]
    pk = T['WA2'][1]
    mx.add(explosion(r, .9, 1.0), r0, .6, rv=.3)                                             # ドガーン（金の 爆発）
    mx.add(boom(110, 34, 1.0, .35, .05, 2.4, r), r0, .7 * FZ_LOW, rv=.15)
    jingle(mx, r0 + .04, .45, 16, .14, r)                                                    # ジャラジャラ（金の 粒）
    d = pk - r0 + .05
    mx.add(nsweep(d, 500, 9000, .45, r) * np.linspace(0, 1, n_(d)) ** 2, r0, .35, rv=.35)
    for j, m in enumerate((76, 80, 83, 88, 92, 95, 100)):
        mx.add(bell(mtof(m), .8, idx=1.4, tau=.4), r0 + j * (d - .05) / 7, .1, (j / 6 - .5) * .9, rv=.5)
    mx.add(boom(120, 40, .8, .25, .03, 2.0, r), pk, .55 * FZ_LOW, rv=.2)
    mx.add(crash(r, 2.2, .8), pk, .35, .3, rv=.45)
    for i, m in enumerate((64, 68, 71, 76, 80, 83)):
        mx.add(bell(mtof(m + 12), 2.0, idx=1.6, tau=.7), pk + .012 * i, .2, (i / 5 - .5) * .9, rv=.5)
    # --- ② 金の 字：万馬券（ミ）・天眼（ラ）---
    for (c0, c1), ch, pn in ((T['CU1'], E, -.3), (T['CU2'], A_, .3)):
        mx.add(boom(85, 30, 1.0, .35, .05, 2.4, r), c0, .6 * FZ_LOW, rv=.15)
        mx.add(gong(mtof(ch[0]), 2.0, .9, r), c0 + .02, .22 * FZ_MID, rv=.5)
        for i, m in enumerate(ch):
            mx.add(brass(m + 12, c1 - c0 + .15, r), c0, .24 * FZ_MID, (i / 3 - .5) * .8, rv=.4)
        mx.add(choir((ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 24), c1 - c0, r, .12, .4), c0, .55, rv=.6)
        mx.add(lcrash(r, 1.8, .7), c0, .12 * FZ_MID, pn, rv=.45)
        sparkle(mx, c0 + .05, c1 - c0, 8, (96, 100, 103, 108), .05, r)
    # 白 → 4行の 文：シュワーッ↑ → ドーン＋どら＋ジャーン（ホ長調）→ ああぁぁ（合唱）＋キラキラ
    w0, w1 = T['WB'][0], T['WB'][1]
    d = w1 - w0 + .02
    mx.add(nsweep(d, 400, 8000, .5, r) * np.linspace(0, 1, n_(d)) ** 2, w0, .3, rv=.35)
    tx = T['TXT']
    mx.add(explosion(r, .9, .8), tx, .5, rv=.3)
    mx.add(boom(80, 26, 1.8, .55, .07, 2.6, r), tx, .9 * FZ_LOW, rv=.15)
    mx.add(gong(mtof(40), 3.0, 1.2, r), tx + .02, .32 * FZ_MID, rv=.5)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):
        mx.add(brass(m + 12, 1.4, r), tx, .26 * FZ_MID, (i / 5 - .5) * .8, rv=.4)
    hold = T['WC'][0] - tx
    mx.add(choir((52, 56, 59, 64, 68, 71), hold, r, .25, .5), tx + .05, .8, rv=.7)
    mx.add(pad((52, 59, 64, 68), hold, .6, .5, .25), tx + .1, .3, rv=.6)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 2.2, idx=1.5, tau=.8), tx + .02 + .012 * i, .18, (-.3, -.1, .1, .3)[i], rv=.5)
    sparkle(mx, tx + .3, hold - .3, 22, (96, 98, 100, 103, 105, 108), .05, r)
    for t in T['SHINE']:                                                                         # 光の 帯：キラーン
        for j, m in enumerate((96, 100, 103, 108)):
            mx.add(bell(mtof(m), .9, idx=1.2, tau=.4, glock=.2), t + .25 + .07 * j, .07, (j / 3 - .5) * 1.2, rv=.5)
    # --- ③ 神様的中：シュワーッ↑ → 金の 粒の 爆発・神・様・的・中 ---
    w0, w1 = T['WC'][0], T['WC'][1]
    d = w1 - w0 + .02
    mx.add(nsweep(d, 400, 9000, .5, r) * np.linspace(0, 1, n_(d)) ** 2, w0, .32, rv=.35)
    for k, (t, kind) in enumerate(T['BU']):
        big = kind > 0
        mx.add(explosion(r, (.5, .9, 1.4)[kind], .9), t, (.35, .6, .9)[kind], rv=.3)
        mx.add(boom(100, 30, (.6, 1.0, 1.8)[kind], .3, .05, 2.4, r), t, (.4, .7, 1.0)[kind] * FZ_LOW, rv=.15)
        jingle(mx, t + .02, (.35, .6, 1.0)[kind], (10, 18, 30)[kind], (.1, .14, .18)[kind], r)
        if big:
            mx.add(crash(r, 1.8, .7), t, .25, (-.3, .3)[k % 2], rv=.45)
    for k, (c0, c1) in enumerate(T['CH']):                                                      # ドン（神・様・的・中：だんだん 高く）
        mx.add(tom(70 + 6 * k, r, .5), c0 + .02, .35 * FZ_MID, rv=.25)
        mx.add(boom(75 + 8 * k, 30, .9, .3, .05, 2.4, r), c0 + .02, .7 * FZ_LOW, rv=.15)
        ch = ((40, 47, 52, 56), (42, 49, 54, 57), (44, 51, 56, 59), (45, 52, 57, 61))[k]          # ミ → ファ# → ソ# → ラ
        mx.add(stab(tuple(m + 12 for m in ch), .45, r, 1.8, .4), c0 + .02, .22 * FZ_MID, rv=.35)
        mx.add(choir((ch[1] + 12, ch[2] + 12, ch[3] + 12), c1 - c0 - .05, r, .06, .2, 2), c0 + .02, .4, rv=.55)
    # --- 神様／的中：ドガーン!!＋ジャーン（ホ長調）→ グォォ↑（ひく）→ パッパッパーン ---
    lg = T['LOGO']
    mx.add(gong(mtof(40), 3.0, 1.2, r), lg + .02, .35 * FZ_MID, rv=.5)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):
        mx.add(brass(m + 12, .9, r), lg, .3 * FZ_MID, (i / 5 - .5) * .8, rv=.35)
    mx.add(lcrash(r, 2.4, .8), lg, .2 * FZ_MID, -.5, rv=.4)
    mx.add(lcrash(r, 2.4, .8), lg, .2 * FZ_MID, .5, rv=.4)
    p0, p1 = T['PULL']
    mx.add(growl(41.2, 82.4, p1 - p0 + .1, p1 - p0), p0, .22, rv=.15)
    mx.add(nsweep(p1 - p0, 300, 7000, .5, r) * np.linspace(0, 1, n_(p1 - p0)) ** 2.5, p0, .3, rv=.35)
    tt = p0
    while tt < p1 - .03:                                                                        # ドロロロ…（ティンパニ）
        u = (tt - p0) / (p1 - p0)
        mx.add(tom(62 + 8 * u, r, .3), tt, (.05 + .3 * u ** 1.5) * FZ_MID, r.uniform(-.2, .2), rv=.3)
        tt += .05
    fz = p1                                                                                     # パッパッパーン（ミ・ミ・シ → 高い ミ）
    for k, (dt, dd, top) in enumerate(((0, .14, 64), (.18, .14, 64), (.36, .14, 71), (.54, .9, 76))):
        for i, m in enumerate((top - 12, top - 5, top)):
            mx.add(brass(m, dd, r), fz + dt, (.2 if k < 3 else .3) * FZ_MID, (i - 1) * .4, rv=.4)
    mx.add(explosion(r, .9, .9), fz + .54, .45, rv=.3)
    mx.add(boom(80, 25, 2.0, .6, .08, 2.6, r), fz + .54, .9 * FZ_LOW, rv=.2)
    mx.add(gong(mtof(40), 2.6, 1.0, r), fz + .56, .3 * FZ_MID, rv=.5)
    mx.add(choir((52, 56, 59, 64, 68, 71, 76), RES - fz + .2, r, .15, .6), fz + .54, .7, rv=.7)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 2.4, idx=1.5, tau=.9), fz + .56 + .012 * i, .2, (-.3, -.1, .1, .3)[i], rv=.5)
    sparkle(mx, fz + .6, RES - fz - .4, 16, (96, 98, 100, 103, 105, 108), .06, r)
    # --- RES：シャラララ↑ → ポンッ（ボード）→ 買い目 ピン・ピン・ピン → 合計 キラリーン＋メダル ---
    for jj, m in enumerate((88, 90, 92, 95, 97, 100, 102, 104)):
        mx.add(tine(mtof(m), .6, .25), RES + .03 * jj, .08, (jj % 2 * 2 - 1) * .4, rv=.4)
    mx.add(pop(560, 260, .14, r, .2), RES + .2, .5, rv=.15)
    for i, m in enumerate((56, 59, 64)):
        mx.add(bell(mtof(m), .7, idx=1.4, tau=.3), t0b + .08 * i, .22 * FZ_MID, rv=.3)
    tt = t0b + .08 * 3
    mx.add(bell(mtof(64), 1.4, idx=1.3, tau=.6), tt, .28 * FZ_MID, rv=.45)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 1.6, idx=1.4, tau=.6), tt + .015 * i, .14, (-.3, -.1, .1, .3)[i], rv=.45)
    mx.add(coin(1500, r, .5), tt, .2, -.2, rv=.25)
    mx.add(coin(1900, r, .45), tt + .06, .15, .25, rv=.25)
    mx.add(pad((40, 44, 47, 52), 1.0, .3, .7, .45), tt, .22, rv=.35)
    medals(mx, RES + .1, 1.8, 26, .2 * FZ_MID, r)
    return mx.render(1.8, target=-13, bass=True)


# ---------- 超神様的中（第4.51版：1コマずつ 描いた 動画 ①②③ に 合わせる。秒は kami_super.film_events()＝動画の 絵の スクリプトの 時刻。PUSHの 音は ど的中と 同じ） ----------
def read_sgd():
    """kami_super.py（動画の 長さ・ボードの 時刻）と、動画の 絵の スクリプト（flat/kami_film*.py）の 時刻"""
    sys.path.insert(0, HERE)
    import kami_super
    return kami_super, kami_super.film_events()


def koban(f, rng, d=.7):
    """チャリーン：小判（大きく 平たい 金の 板 → コインより 低く、長く ひびく）＋当たる 音＋2回 はねる"""
    n = n_(d)
    t = tl(n)
    x = np.zeros(n)
    for r_, a, tau in ((1, 1, .3), (1.53, .6, .19), (2.31, .45, .12), (2.94, .3, .08), (4.1, .18, .05)):
        fr = f * r_ * (1 + rng.uniform(-.006, .006))
        if fr < 15000:
            x += a * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    x += .4 * bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t / .003)
    for dt, g in ((rng.uniform(.04, .07), .45), (rng.uniform(.1, .14), .2)):
        k = n_(dt)
        x[k:] += g * x[:n - k]
    return fade(x / 1.6, .0008, .03)


def kjingle(mx, t0, dur, count, g, rng, pan=.85, curve=1.5, f=(1300, 2700)):
    """ジャラジャラ：小判（はじめが 多くて、だんだん 少なく）"""
    for _ in range(count):
        mx.add(koban(rng.uniform(*f), rng, rng.uniform(.45, .75)), t0 + dur * rng.uniform(0, 1) ** curve, g * rng.uniform(.5, 1),
               rng.uniform(-pan, pan), rv=.3)


def suzu(mx, t0, g, rng, pan=0.0, shakes=1, gap=.3):
    """シャン：神社の 鈴（小さな 鈴が たくさん いっしょに ゆれる：1回 ふる ごとに 細かい 当たりが かたまって 鳴る）"""
    fs = rng.uniform(3000, 5600, 7)
    for s in range(shakes):
        ts = t0 + s * gap
        for k in range(26):
            f = fs[int(rng.integers(0, len(fs)))]
            n = n_(.45)
            t = tl(n)
            x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.42 * t) * np.exp(-t / .05)) * np.exp(-t / rng.uniform(.08, .22))
            x = fade(x + .3 * hp(rng.standard_normal(n), 6000) * np.exp(-t / .002), .0005, .03)
            mx.add(x, ts + .09 * rng.uniform(0, 1) ** 1.8, g * rng.uniform(.25, 1) / 4, float(np.clip(pan + rng.uniform(-.4, .4), -1, 1)), rv=.45)


def omedetou_voice(fz, vr):
    """鳥居の 中の 神様的中 おめでとう御座います の 声：(おめでとう の 声, 時刻, いやーん の 声, 時刻)。fz＝ファンファーレの 時刻"""
    v = say(OMEDETOU, vr, **SAY_BREATHY)
    tv = fz + VOICE_OMEDETOU[0]
    v2 = say(IYAN_END, vr, **SAY_LOUD)
    return v, tv, v2, tv + len(v) / SR + VOICE_OMEDETOU[3]


def sfx_sgd():
    """超神様的中の タップの 音（第4.51版）。0秒＝動画の はじめ（見本では 動画が 動きだした 時に その 時刻から 鳴らす）：
       ① 金の 嵐（0〜1.6秒）：キュイッ↑（光の 粒）→ ドガーン!!（光の 爆発）＋パァーン（まっ白）→ ザァッ↓（光の 滝）→ ドーン（床に 当たる）＋ゴゴゴ・ゴォォォ（嵐）
          → ブォォン↑・シュワーッ↑（ドームが 床から 上がる）＋ギュイーン（電気の 光）＋ドガーン・パチパチ（下の 火花の 爆発）
          ＋バリバリッ・ドーン（上から 下への 雷 6本・形が かわる たびに バチッ）＋ジジジ・ビリビリ（ドームの 電気）＋バリッ（玉から 画面の はしへの 雷）＋ヒュンッ（岩）
          ＋キュゥゥン↑（玉が 小さく なる）→ キィン（金の 光が 集まる）→ ドガーン!!＋ジャラジャラ（金の 爆発）→ シュワーッ↑ → パァーン（まっ白）
       ② 金の 字（2.93〜7.63秒：白い 光の あと）：ゴォォッ（左から すべって くる）→ ズーン!!（万馬券：ミの ジャーン＋どら＋合唱）→ ゴォォッ（右から）→ ズーン!!（天眼：ラ）
          → シュワーッ↑ → ドーン＋どら＋ジャーン（4行の 文：ホ長調）＋ああぁぁ（合唱）＋キラーン（光が すべる 2回）→ シュワーッ↑
       ③ 神様的中（7.63〜14.23秒）：ドガーン＋ジャラジャラ（小判が はじける）・ドン（神）→ ヒュオッ（大きな 小判が 横切る）・ドン（様）→ ドガーン＋ジャラジャラ・ドン（的）
          → ヒュオッ・ドン（中）（ドンは だんだん 高く）＋バチバチ（字の ふちを はしる 雷）・バリバリッ（外へ はしる 雷）
          → ドガーン!!＋ジャラジャラジャラ（小判の 大爆発）＋ジャーン（神様的中）→ グォォ↑＋ドロロロ（ひいて 鳥居）＋シャララン（神社の 鈴）
          → パッパッパーン（ファンファーレ）＋すぅっ・声「おめでとう御座います！」「いやーーーーん！」＋ああぁぁ（合唱）＋ビリビリ・バチッ（字の 雷：不定期）＋キラーン（光が すべる 2回）＋シャン・シャン・シャン
       → 白い 光：シャラララ↑ → ポンッ（ボード）→ 買い目 ピン・ピン・ピン → 合計 キラリーン＋小判の ジャラジャラ
       ① と ② の 間の 白い 光（1.5秒：kami_super.NW）は ああぁぁ（合唱）＋ふわぁ＋キラキラ → シュワッ↑"""
    SG, ev = read_sgd()
    mx = Mix(SG.T0B + 2.0, 71)
    sgd_mix(mx, mx.rng, SG, ev, 0.0)
    return mx.render(1.8, target=-13, bass=True)


def sgd_mix(mx, r, SG, ev, o=0.0):
    """超神様の 音の 中身を mx に 置く（o：ずらす 秒。宇宙の カットインの あとに 鳴らす 時は カットインの 長さ）"""
    o1, o2, o3 = (v + o for v in SG.OFS)
    RES, t0b, FILM = SG.RES + o, SG.T0B + o, SG.FILM + o
    E = (40, 47, 52, 56)          # ホ長調（E2・B2・E3・G#3）
    A_ = (45, 52, 57, 61)         # ラ（A2・E3・A3・C#4）
    T1, T2, T3 = ev['T1'], ev['T2'], ev['T3']
    # ======== ① 金の 嵐 ========
    ig0, igw, igf, igr, ige = (o1 + v for v in T1['IGN'])        # 点火：はじまり・白が 出はじめ・まっ白・白が ひきはじめ・白が 消える
    mx.add(cuin(700, 3600, igw - ig0 + .06, igw - ig0, r), ig0, .14, rv=.3)          # キュイッ↑（光の 粒が ふくらむ）
    mx.add(arc_zap(igw - ig0, r, 500), ig0, .3, rv=.2)
    mx.add(explosion(r, 1.1, .9), igw - .01, .8, rv=.3)                              # ドガーン!!（光の 爆発）
    mx.add(boom(110, 28, 1.6, .5, .05, 2.6, r), igw - .01, 1.0 * FZ_LOW, rv=.1)
    mx.add(crash(r, 2.0, .7), igf, .3, -.2, rv=.45)                                 # パァーン（まっ白）
    for i, m in enumerate((76, 83, 88, 95)):
        mx.add(bell(mtof(m), 1.4, idx=1.3, tau=.5), igf + .01 * i, .1, (i / 3 - .5) * .8, rv=.5)
    c0, c1 = (o1 + v for v in T1['COL'])
    dcol = c1 - c0 + .03
    mx.add(nsweep(dcol, 7000, 900, .6, r) * np.linspace(.3, 1, n_(dcol)), c0, .3, rv=.3)          # ザァッ↓（光の 滝が おりる）
    im = o1 + T1['IMPACT']
    mx.add(boom(90, 28, 1.3, .45, .05, 2.4, r), im, .85 * FZ_LOW, rv=.15)                       # ドーン（床に 当たる）
    mx.add(explosion(r, .6, 1.1), im, .45, rv=.3)
    gl, gx, gw, gk = (o1 + v for v in T1['GOLD'])                                 # 金：光が 集まる・爆発・白が 出はじめ・まっ白
    dw = gw - c0
    tw = tl(n_(dw))
    mx.add(nlow(dw, 3400, 1900, 1.0, r) * np.minimum(tw / .1, 1) * np.clip((dw - tw) / .25, 0, 1), c0, .24, rv=.35)   # ゴォォォ（光の 滝）
    mx.add(rumble(gw - im + .2, r, 150, 9), im, .5, rv=.3)                                      # ゴゴゴ（嵐）
    mx.add(growl(30.9, 41.2, gw - im, gw - im, 2.0), im, .14, rv=.2)
    d0, d1 = (o1 + v for v in T1['DOME'][:2])                                     # ドームが 床から 上がる
    mx.add(growl(41.2, 98.0, d1 - d0 + .3, d1 - d0, 2.2), d0, .2, rv=.25)                       # ブォォン↑
    dd = d1 - d0 + .06
    mx.add(nsweep(dd, 300, 6500, .5, r) * np.linspace(0, 1, n_(dd)) ** 1.5, d0, .26, rv=.35)     # シュワーッ↑
    for j, m in enumerate((76, 83, 88, 95)):                                                     # キラッ（ガラスの 玉）
        mx.add(bell(mtof(m), .9, idx=1.2, tau=.35), d1 - .03 + .025 * j, .07, (j / 3 - .5) * .9, rv=.5)
    g0, _, _, g3 = (o1 + v for v in T1['SURGE'])
    mx.add(buzz(g3 - g0 + .12, r, 74), g0, .28, rv=.2)                                          # ギュイーン（電気の 光）
    mx.add(crackle(g3 - g0, 380, r), g0, .35, -.5, rv=.25)
    mx.add(crackle(g3 - g0, 300, r), g0, .3, .5, rv=.25)
    l0 = o1 + ev['LIFT_T'][0]                                                                    # 下の 火花の 爆発
    mx.add(explosion(r, .8, 1.0), l0, .5, rv=.3)
    mx.add(boom(100, 30, 1.0, .35, .05, 2.4, r), l0 + .01, .55 * FZ_LOW, rv=.15)
    for dt, cnt in ev['LIFT_BURSTS']:                                                            # パチパチパチ（火花が とぶ）
        mx.add(crackle(.45, cnt * 2.2, r), l0 + dt, .3, r.uniform(-.3, .3), rv=.3)
        mx.add(arc_zap(.1, r, 900), l0 + dt, .2, r.uniform(-.3, .3), rv=.2)
    for t0, t1, pan, chg in ev['RIBS']:                                                          # 上から 下への 雷
        t0, t1 = o1 + t0, o1 + t1
        mx.add(arc_zap(.14, r, 1400), t0, .45, pan, rv=.25)                                      # バリバリッ
        mx.add(explosion(r, .35, 1.5), t0 + .005, .3, pan, rv=.35)                               # ドーン
        mx.add(boom(85, 30, .9, .3, .03, 2.4, r), t0 + .01, .38 * FZ_LOW, rv=.2)
        mx.add(buzz(t1 - t0, r, 96 + 10 * pan), t0 + .03, .05, pan, rv=.15)                      # ジジジ（のこって いる 間）
        for tc in chg:                                                                           # バチッ（形が かわる）
            mx.add(arc_zap(.06, r, 1100), o1 + tc, .2, pan, rv=.2)
    k0, k1 = (o1 + v for v in ev['CRACK'])                                                       # ドームの 電気
    mx.add(buzz(k1 - k0 + .1, r), k0, .12, rv=.15)                                               # ビリビリ
    mx.add(crackle(k1 - k0, 160, r), k0, .22, rv=.25)                                            # ジジジ
    for t, pan in ev['ARCS']:                                                                    # バチッ（玉の 表面を はしる 電気）
        mx.add(arc_zap(.08, r, 900), o1 + t, .2, pan, rv=.2)
    for t, pan, life in ev['SB']:                                                                # バリッ（玉から 画面の はしへの 雷）
        mx.add(arc_zap(life, r, 1300), o1 + t, .3, pan, rv=.25)
        mx.add(explosion(r, .15, 1.9), o1 + t + .004, .12, pan, rv=.3)
    for t, side, _ in ev['ROCKS']:                                                               # ヒュンッ（岩）
        mx.add(whoosh(.5, r), o1 + t, .28, np.linspace(0, side, 12), rv=.2)
    s0, s1 = (o1 + v for v in ev['SHRINK'])                                                      # キュゥゥン↑（玉が 小さく なる）
    mx.add(cuin(330, 1320, s1 - s0 + .1, s1 - s0, r), s0, .07, rv=.35)
    mx.add(growl(55.0, 110.0, s1 - s0 + .1, s1 - s0, 2.0), s0, .1, rv=.2)
    for j, m in enumerate((88, 95, 100)):                                                        # キィン（金の 光が 集まる）
        mx.add(bell(mtof(m), .5, idx=1.2, tau=.25), gl + .02 * j, .08, rv=.4)
    mx.add(explosion(r, 1.0, 1.0), gx, .7, rv=.3)                                               # ドガーン!!（金の 爆発）
    mx.add(boom(115, 32, 1.2, .4, .05, 2.5, r), gx, .85 * FZ_LOW, rv=.15)
    jingle(mx, gx + .03, .5, 18, .15, r)                                                         # ジャラジャラ（金の かけら）
    dsw = gk - gx + .05
    mx.add(nsweep(dsw, 500, 9000, .45, r) * np.linspace(0, 1, n_(dsw)) ** 2, gx, .32, rv=.35)    # シュワーッ↑
    mx.add(boom(120, 40, .8, .25, .03, 2.0, r), gk, .5 * FZ_LOW, rv=.2)                         # パァーン（まっ白：① → ②）
    mx.add(crash(r, 2.2, .8), gk, .32, .3, rv=.45)
    for i, m in enumerate((64, 68, 71, 76, 80, 83)):
        mx.add(bell(mtof(m + 12), 2.0, idx=1.6, tau=.7), gk + .012 * i, .18, (i / 5 - .5) * .9, rv=.5)
    wd = o2 + .2 - gk                                                                            # 白い 光に つつまれる（1.5秒）：ああぁぁ＋ふわぁ＋キラキラ → シュワッ↑（② へ）
    if wd > .6:
        mx.add(choir((64, 68, 71, 76, 80), wd, r, .35, .6), gk + .08, .42, rv=.7)
        mx.add(pad((52, 59, 64, 68, 71), wd, .4, .6, .22), gk + .1, .2, rv=.6)
        sparkle(mx, gk + .25, wd - .45, 30, (96, 98, 100, 103, 105, 108), .042, r)                # シャラシャラ（金粉）
        mx.add(nsweep(.45, 600, 7000, .5, r) * np.linspace(0, 1, n_(.45)) ** 2, o2 - .32, .18, rv=.35)
    # ======== ② 金の 字：重たい 金が ズーン（万馬券 ← 左から・天眼 ← 右から）========
    for (ha, hl, he), ch, side in ((ev['HEAVY'][0], E, -1), (ev['HEAVY'][1], A_, 1)):
        a, l, e = o2 + ha, o2 + hl, o2 + he
        dsl = l - a + .06
        u = np.linspace(.15, 1, n_(dsl)) ** 1.6
        mx.add(nlow(dsl, 800, 2600, .35, r) * u, a, .3, np.linspace(side * .9, 0, 12), rv=.25)   # ゴォォッ（横から すべって くる）
        mx.add(growl(36.7, 55.0, dsl, dsl, 2.4), a, .12, np.linspace(side * .6, 0, 8), rv=.2)
        mx.add(boom(70, 24, 2.2, .7, .08, 2.8, r), l, 1.0 * FZ_LOW, rv=.15)                      # ズーン!!（着地）
        mx.add(explosion(r, .7, .7), l, .45, rv=.3)
        mx.add(lsnare(r, .4, .12, 90), l, .3, rv=.3)
        mx.add(gong(mtof(ch[0]), 2.6, 1.1, r), l + .02, .3 * FZ_MID, rv=.5)
        for i, m in enumerate(ch):
            mx.add(brass(m + 12, e - l + .1, r), l, .24 * FZ_MID, (i / 3 - .5) * .8, rv=.4)
        mx.add(choir((ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 24), e - l, r, .12, .4), l, .55, rv=.6)
        mx.add(lcrash(r, 1.8, .7), l, .12 * FZ_MID, side * .3, rv=.45)
        dr_ = .5                                                                                  # シュワァン（金の 輪が ひろがる）＋キラーン
        mx.add(nsweep(dr_, 2500, 9000, .5, r) * np.exp(-tl(n_(dr_)) / .18), l + .1, .16, rv=.4)
        for j, m in enumerate((88, 95, 100)):
            mx.add(bell(mtof(m), 1.2, idx=1.3, tau=.5), l + .12 + .05 * j, .09, (j - 1) * .5, rv=.5)
        sparkle(mx, l + .15, e - l - .15, 8, (96, 100, 103, 108), .05, r)
    w0, w1 = o2 + T2['WB'][0], o2 + T2['WB'][1]                                                  # シュワーッ↑（白）
    dsw = w1 - w0 + .02
    mx.add(nsweep(dsw, 400, 8000, .5, r) * np.linspace(0, 1, n_(dsw)) ** 2, w0, .3, rv=.35)
    tx = o2 + T2['TXT']                                                                          # ドーン＋どら＋ジャーン（4行の 文）
    mx.add(explosion(r, .9, .8), tx, .5, rv=.3)
    mx.add(boom(80, 26, 1.8, .55, .07, 2.6, r), tx, .9 * FZ_LOW, rv=.15)
    mx.add(gong(mtof(40), 3.0, 1.2, r), tx + .02, .32 * FZ_MID, rv=.5)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):
        mx.add(brass(m + 12, 1.4, r), tx, .26 * FZ_MID, (i / 5 - .5) * .8, rv=.4)
    hold = o2 + T2['WC'][0] - tx
    mx.add(choir((52, 56, 59, 64, 68, 71), hold, r, .25, .5), tx + .05, .8, rv=.7)                # ああぁぁ（合唱）
    mx.add(pad((52, 59, 64, 68), hold, .6, .5, .25), tx + .1, .3, rv=.6)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 2.2, idx=1.5, tau=.8), tx + .02 + .012 * i, .18, (-.3, -.1, .1, .3)[i], rv=.5)
    sparkle(mx, tx + .3, hold - .3, 22, (96, 98, 100, 103, 105, 108), .05, r)
    for t in T2['SHINE']:                                                                        # キラーン（光が すべる）
        for j, m in enumerate((96, 100, 103, 108)):
            mx.add(bell(mtof(m), .9, idx=1.2, tau=.4, glock=.2), o2 + t + .25 + .07 * j, .07, (j / 3 - .5) * 1.2, rv=.5)
    w0, w1 = o2 + T2['WC'][0], o2 + T2['WC'][1]                                                  # シュワーッ↑（白：② → ③）
    dsw = w1 - w0 + .02
    mx.add(nsweep(dsw, 400, 9000, .5, r) * np.linspace(0, 1, n_(dsw)) ** 2, w0, .32, rv=.35)
    # ======== ③ 神様的中：小判と 神・様・的・中 → 鳥居の 中に 神様的中 おめでとう御座います ========
    for k, (t, kind, _) in enumerate(T3['BU']):
        tt = o3 + t
        if kind == 0:                                                                            # ヒュオッ（大きな 小判が 手前を 横切る）
            dirn = -1 if k % 4 == 1 else 1
            for q in range(3):
                mx.add(whoosh(.36, r, 2400, 500), tt + .05 + .04 * q - .18, .24, np.linspace(-dirn * .9, dirn * .9, 12), rv=.2)
            mx.add(koban(900, r, 1.0), tt + .05, .12, rv=.4)
            continue
        big = kind == 2
        mx.add(explosion(r, 1.4 if big else .8, .9), tt, .9 if big else .55, rv=.3)              # ドガーン（小判が はじける）
        mx.add(boom(100, 30, 1.8 if big else 1.0, .3, .05, 2.4, r), tt, (1.0 if big else .7) * FZ_LOW, rv=.15)
        kjingle(mx, tt + .02, 1.1 if big else .6, 42 if big else 18, .2 if big else .15, r)      # ジャラジャラ
        if big:
            mx.add(crash(r, 1.8, .7), tt, .25, rv=.45)
    for k, (c0, c1) in enumerate(T3['CU']):                                                      # ドン（神・様・的・中：だんだん 高く）
        cs, ce = o3 + c0, o3 + c1
        mx.add(tom(70 + 6 * k, r, .5), cs + .02, .35 * FZ_MID, rv=.25)
        mx.add(boom(75 + 8 * k, 30, .9, .3, .05, 2.4, r), cs + .02, .7 * FZ_LOW, rv=.15)
        ch = ((40, 47, 52, 56), (42, 49, 54, 57), (44, 51, 56, 59), (45, 52, 57, 61))[k]          # ミ → ファ# → ソ# → ラ
        mx.add(stab(tuple(m + 12 for m in ch), .45, r, 1.8, .4), cs + .02, .22 * FZ_MID, rv=.35)
        mx.add(choir((ch[1] + 12, ch[2] + 12, ch[3] + 12), ce - cs - .05, r, .06, .2, 2), cs + .02, .4, rv=.55)
    lg = o3 + T3['LOGO']                                                                         # ジャーン（神様的中：ホ長調）
    mx.add(gong(mtof(40), 3.0, 1.2, r), lg + .02, .35 * FZ_MID, rv=.5)
    for i, m in enumerate((40, 47, 52, 56, 59, 64)):
        mx.add(brass(m + 12, .9, r), lg, .3 * FZ_MID, (i / 5 - .5) * .8, rv=.35)
    mx.add(lcrash(r, 2.4, .8), lg, .2 * FZ_MID, -.5, rv=.4)
    mx.add(lcrash(r, 2.4, .8), lg, .2 * FZ_MID, .5, rv=.4)
    p0, p1 = o3 + T3['TURN'][0], o3 + T3['TURN'][1]                                              # グォォ↑（ひいて 鳥居）＋ドロロロ
    mx.add(growl(41.2, 82.4, p1 - p0 + .1, p1 - p0), p0, .22, rv=.15)
    mx.add(nsweep(p1 - p0, 300, 7000, .5, r) * np.linspace(0, 1, n_(p1 - p0)) ** 2.5, p0, .3, rv=.35)
    tt = p0 + .1
    while tt < p1 - .03:
        u = (tt - p0) / (p1 - p0)
        mx.add(tom(62 + 8 * u, r, .3), tt, (.05 + .3 * u ** 1.5) * FZ_MID, r.uniform(-.2, .2), rv=.3)
        tt += .05
    suzu(mx, p0 + .15, .5, r, 0.0)                                                               # シャララン（神社の 鈴：鳥居が 見えて くる）
    fz = p1                                                                                      # パッパッパーン（ミ・ミ・シ → 高い ミ）
    for k, (dt, dd, top) in enumerate(((0, .14, 64), (.18, .14, 64), (.36, .14, 71), (.54, .9, 76))):
        for i, m in enumerate((top - 12, top - 5, top)):
            mx.add(brass(m, dd, r), fz + dt, (.2 if k < 3 else .3) * FZ_MID, (i - 1) * .4, rv=.4)
    mx.add(explosion(r, .9, .9), fz + .54, .45, rv=.3)
    mx.add(boom(80, 25, 2.0, .6, .08, 2.6, r), fz + .54, .9 * FZ_LOW, rv=.2)
    mx.add(gong(mtof(40), 2.6, 1.0, r), fz + .56, .3 * FZ_MID, rv=.5)
    bed = RES - fz - .54 + .2
    mx.add(choir((52, 56, 59, 64, 68, 71, 76), bed, r, .15, .6), fz + .54, .7, rv=.7)             # ああぁぁ（合唱）
    mx.add(pad((40, 52, 59, 64, 68), bed, .5, .6, .3), fz + .6, .22, rv=.6)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 2.4, idx=1.5, tau=.9), fz + .56 + .012 * i, .2, (-.3, -.1, .1, .3)[i], rv=.5)
    sparkle(mx, fz + .6, RES - fz - .8, 22, (96, 98, 100, 103, 105, 108), .05, r)
    for t0, _ in T3['SHINE']:                                                                    # キラーン（光が すべる）
        for j, m in enumerate((96, 100, 103, 108)):
            mx.add(bell(mtof(m), .9, idx=1.2, tau=.4, glock=.2), o3 + t0 + .25 + .07 * j, .08, (j / 3 - .5) * 1.2, rv=.5)
    suzu(mx, o3 + T3['SHINE'][1][0] - .65, .32, r, -.2, 3, .3)                                   # シャン・シャン・シャン（鈴）
    for t, kind, life, pan in ev['EL3']:                                                         # 字の 雷（不定期）
        tt = o3 + t
        if kind == 'run':                                                                        # バチバチ（ふちを はしる）
            mx.add(arc_zap(max(.05, life * .7), r, 700), tt, .13 if tt < lg else .1, pan * .8, rv=.2)
        elif kind == 'out':                                                                      # バリバリッ（外へ はしる）
            mx.add(arc_zap(life + .05, r, 1400), tt, .3, pan, rv=.25)
            mx.add(explosion(r, .2, 1.8), tt + .005, .14, pan, rv=.3)
        else:                                                                                    # バチッ（字から 字へ とぶ）
            mx.add(arc_zap(life + .03, r, 1200), tt, .2, pan * .8, rv=.25)
    cu0 = o3 + T3['CU'][0][0] + .1                                                               # ふちの ビリビリ（毎コマ ちがう 所）
    for pn in (-.3, .3):
        mx.add(crackle(lg - cu0, 90, r), cu0, .12, pn, rv=.2)
    e0 = o3 + ev['LOGO0']
    for pn in (-.4, .4):
        mx.add(crackle(FILM - e0, 110, r), e0, .1, pn, rv=.2)
    mx.add(buzz(FILM - e0 + .1, r, 98), e0, .03, rv=.15)
    # ======== RES：白い 光 シャラララ↑ → ポンッ（ボード）→ 買い目 ピン・ピン・ピン → 合計 キラリーン＋小判 ========
    for jj, m in enumerate((88, 90, 92, 95, 97, 100, 102, 104)):
        mx.add(tine(mtof(m), .6, .25), RES - .15 + .03 * jj, .08, (jj % 2 * 2 - 1) * .4, rv=.4)
    mx.add(pop(560, 260, .14, r, .2), RES + .2, .5, rv=.15)
    for i, m in enumerate((56, 59, 64)):
        mx.add(bell(mtof(m), .7, idx=1.4, tau=.3), t0b + .08 * i, .22 * FZ_MID, rv=.3)
    tt = t0b + .08 * 3
    mx.add(bell(mtof(64), 1.4, idx=1.3, tau=.6), tt, .28 * FZ_MID, rv=.45)
    for i, m in enumerate((88, 92, 95, 100)):
        mx.add(bell(mtof(m), 1.6, idx=1.4, tau=.6), tt + .015 * i, .14, (-.3, -.1, .1, .3)[i], rv=.45)
    mx.add(koban(1500, r, .6), tt, .2, -.2, rv=.25)
    mx.add(koban(1900, r, .55), tt + .06, .15, .25, rv=.25)
    mx.add(pad((40, 44, 47, 52), 1.0, .3, .7, .45), tt, .22, rv=.35)
    kjingle(mx, RES + .1, 1.8, 28, .2 * FZ_MID, r, curve=1.8)
    vr = np.random.default_rng(79)
    v, tv, v2, t2 = omedetou_voice(fz, vr)                                                   # 声「おめでとう御座います！」（息の まじった 人の 声）＋「いやーーーーん！」（大きな 声）
    mx.duck(tv, t2 + len(v2) / SR - .05, VOICE_OMEDETOU[1], ramp=.05)
    mx.add(inhale(.32, vr), tv - .36, .4, rv=.15)                                            # すぅっ（話す 前に 息を すう）
    mx.add(v, tv, VOICE_OMEDETOU[2], rv=.22)
    mx.add(v2, t2, VOICE_OMEDETOU[2], rv=.25)


# ---------- 超神様的中の 宇宙の カットイン（超神様的中の 4回に1回 ※仮：flat/kami_cutin.py の SEQ・隕石・雷に 合わせる） ----------
def read_cutin():
    sys.path.insert(0, os.path.join(HERE, 'flat'))
    import kami_cutin
    return kami_cutin


def whomp(d, rng, f0=140, f1=42):
    """ワァン：衝撃波の 低い ゆれ（音程が 下がりながら ゆらゆら・こもる）"""
    n = n_(d)
    t = tl(n)
    f = f1 + (f0 - f1) * np.exp(-t / (d / 3))
    vib = 1 + .05 * np.sin(2 * np.pi * 6.5 * t)
    x = np.sin(phase(f * vib, n)) + .45 * np.sin(phase(2 * f * vib, n)) + .25 * saw(f * 1.5, n, .4, nh=12)
    x = np.tanh(1.8 * x) / np.tanh(1.8)
    a = np.minimum(t / .008, 1) * np.exp(-t / (d / 2.5))
    return fade(x * a, .002, .05)


def glassring(f, d, rng, rate=8.0):
    """ワンワン…：ガラスの 波紋の ひびき（高い 鐘が ゆれる）"""
    n = n_(d)
    t = tl(n)
    x = bell(f, d, ratio=2.76, idx=.9, tau=d / 3, glock=.1)[:n]
    am = .55 + .45 * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6.28))
    return fade(x * am, .002, .05)


def fire_roar(d, rng, fc0=2500, fc1=300, tau=.35):
    """ゴォォッ：炎の うなり（こもって いく ノイズ＋ゆらぎ）"""
    n = n_(d)
    t = tl(n)
    x = nlow(d, fc0, fc1, tau, rng)
    x = x * (.7 + .3 * np.sin(2 * np.pi * 11 * t + rng.uniform(0, 6)))
    return fade(x * np.minimum(t / .02, 1) * np.exp(-t / (d / 2.2)), .003, .05)


def suck(d, rng, f0=2600, f1=260):
    """シュゥゥン↓：光が 小さく なって 吸いこまれる（高い 音が 下がる・きらきら・こもる ノイズ）"""
    n = n_(d)
    t = tl(n)
    u = np.clip(t / d, 0, 1)
    f = f0 * (f1 / f0) ** (u ** 1.3)
    x = .5 * np.sin(phase(f, n)) + .25 * np.sin(phase(f * 1.5, n)) + .2 * np.sin(phase(f * 2.01, n))
    x = x * (.6 + .4 * np.sin(2 * np.pi * (14 - 8 * u) * t))
    x = x + .5 * nsweep(d, 9000, 700, .5, rng)
    a = np.minimum(t / .06, 1) * (1 - u) ** .6
    return fade(x * a, .004, .03)


def cutin_mix(mx, r, CI, o=0.0):
    """宇宙の カットイン 第2版（flat/kami_cutin.py の SEQ・隕石・雷・爆発・波紋に 合わせる・o 秒 ずらす）：
       ゴォォ（宇宙の うなり）＋ヒュゥゥン（隕石が 落ちる：1つずつ・当たると ドスッ）＋ゴオォォォ↑キィィン（大きな 隕石が せまる）
       → バシュゥン!!＋キィーン（当たって 青い 光に つつまれる）→ ドッゴォォォン!!（大きな 爆発）＋声「いやーーーん！！！」＋バリバリッ・ドーン（惑星を はしる 雷）
       ＋パチパチ（火花）＋ワァン（衝撃波）→ シャラララ↑（まん中の 光が あらわれる）
       → バシュッ（黄色）→ キィン（赤）→ ヴォン（黒）→ ズゥン（赤い 惑星）＋バリバリッ（のこる 雷）→ シュゥゥン↓（まん中の 光が 小さく なる）→ 超神様の 音へ
       （白い 反転の 波紋の 場面は けした：まさちゃん「一枚目、二枚目のこのシーンいらない！」）"""
    fps = CI.FPS
    seg = {m: (a / fps + o, b / fps + o) for a, b, m in CI.SEQ}
    W = float(CI.W)

    def pan_x(x):
        return float(np.clip((x / W) * 2 - 1, -1, 1)) * .8
    m0, m1 = seg['M']
    ti = CI.IMPACT / fps + o
    tb = CI.BOOM / fps + o
    dd = m1 - m0 + .15
    mx.add(rumble(dd, r, 90, 6) * np.linspace(.35, 1, n_(dd)), m0, .3, rv=.3)               # ゴォォ（宇宙の うなり）
    for (t0, te, xe, hit, sz) in CI.meteor_events()[:-1]:                                    # ヒュゥゥン（隕石）・ドスッ（当たる）
        if t0 + o >= ti:
            continue
        d = float(np.clip(te - t0, .25, .9))
        g = .1 + .025 * sz
        mx.add(whoosh(d, r, 3200, 450), t0 + o, g, np.linspace(.75, pan_x(xe), 12), rv=.25)
        if hit and 0 <= xe <= W and te + o < ti:
            mx.add(explosion(r, .12, 1.8), te + o, .12 + .02 * sz, pan_x(xe), rv=.3)
            mx.add(glitch('thud', .05, r), te + o, .12, pan_x(xe), rv=.1)
    db = ti - m0                                                                             # ゴオォォォ↑（大きな 隕石が せまる）
    u = np.clip(tl(n_(db)) / db, 0, 1)
    mx.add(fire_roar(db, r, 1800, 900, 3.0) * (.15 + .85 * u ** 2), m0, .45, np.linspace(.6, 0, 12), rv=.25)
    mx.add(growl(45.0, 90.0, db, db, 2.2) * u ** 1.5, m0, .16, rv=.2)
    mx.add(cuin(600, 3200, .55, .5, r), ti - .5, .1, rv=.3)                                   # キィィン↑
    # --- 当たる → 青い 光（バシュゥン!!＋キィーン）---
    mx.add(explosion(r, .45, 2.0), ti, .55, rv=.3)
    mx.add(glitch('zip', .08, r), ti, .35, -.45, rv=.1)
    mx.add(glitch('zip', .08, r), ti + .01, .35, .45, rv=.1)
    mx.add(nsweep(.4, 12000, 2500, .5, r) * np.exp(-tl(n_(.4)) / .15), ti, .3, rv=.45)
    for j, m in enumerate((96, 100, 103, 108)):
        mx.add(bell(mtof(m), .9, idx=1.0, tau=.35), ti + .015 * j, .09, (j / 3 - .5) * .9, rv=.55)
    # --- 大きな 爆発（ドッゴォォォン!!）---
    mx.add(explosion(r, 1.7, .75), tb, 1.0, rv=.3)
    mx.add(boom(80, 24, 2.2, .8, .07, 2.8, r), tb, 1.0 * FZ_LOW, rv=.15)
    mx.add(crash(r, 2.2, .8), tb, .32, rv=.45)
    mx.add(rumble(1.6, r, 140, 9), tb + .05, .4, rv=.3)
    mx.add(whomp(.8, r, 130, 38), tb + .03, .5 * FZ_MID, rv=.35)
    mx.add(crackle(.9, 260, r), tb + .05, .22, -.3, rv=.3)                                    # パチパチ（火花）
    mx.add(crackle(.9, 260, r), tb + .05, .22, .3, rv=.3)
    for (f0, kind, life, w1) in CI.PBOLTS:                                                   # バリバリッ・ドーン（惑星を はしる 雷）
        t = f0 / fps + o
        (sa, da), (sb, dbb), _ = CI.PB_KIND[kind]
        xe = CI.sd_xy(sb, dbb)[0]
        big = w1 >= 15
        mx.add(arc_zap(life / fps + .04, r, 1400), t, .42 if big else .32, pan_x(xe), rv=.25)
        mx.add(explosion(r, .3 if big else .2, 1.6), t + .005, .26 if big else .16, pan_x(xe), rv=.35)
        if big:
            mx.add(boom(85, 30, .9, .3, .03, 2.4, r), t + .01, .3 * FZ_LOW, rv=.2)
    tl_ = tb + .4 / 1.0                                                                       # シャラララ↑（まん中の 光が あらわれる）
    for j, m in enumerate((84, 88, 91, 96, 100)):
        mx.add(bell(mtof(m), .8, idx=1.1, tau=.3), tl_ + .09 * j, .08, (j / 4 - .5) * .8, rv=.5)
    mx.add(nsweep(.5, 2000, 11000, .5, r) * np.linspace(0, 1, n_(.5)) ** 1.5, tl_, .16, rv=.4)
    # --- 黄色 → 赤 → 黒 ---
    ty = seg['Nyel'][0]                                                                      # バシュッ（黄色）
    mx.add(explosion(r, .5, 1.6), ty, .45, rv=.25)
    mx.add(glitch('zip', .07, r), ty, .3, -.4, rv=.1)
    mx.add(glitch('zip', .07, r), ty + .01, .3, .4, rv=.1)
    t2 = seg['R2'][0]                                                                        # キィン（赤）
    for i, m in enumerate((88, 95)):
        mx.add(bell(mtof(m), .6, idx=1.2, tau=.25), t2 + .01 * i, .1, (i - .5) * .6, rv=.4)
    mx.add(glitch('tick', .02, r), t2, .3, rv=.1)
    tk = seg['K'][0]                                                                         # ヴォン（黒）
    mx.add(boom(62, 30, .55, .22, .03, 2.0, r, grit=.1), tk, .5 * FZ_LOW, rv=.15)
    mx.add(glitch('thud', .08, r), tk, .3, rv=.1)
    d2 = seg['R3'][0] - t2
    mx.add(nsweep(d2, 1500, 12000, .4, r) * np.linspace(0, 1, n_(d2)) ** 2, t2, .25, rv=.3)
    # --- 赤い 惑星（爆発と 雷は のこる）→ まん中の 光が 小さく なる ---
    t3, t3e = seg['R3']
    mx.add(boom(70, 30, .7, .3, .05, 2.0, r, grit=.05), t3, .45 * FZ_LOW, rv=.15)
    k0, k1 = (t3 + v / fps for v in CI.R3_SHRINK)                                            # シュゥゥン↓
    mx.add(suck(k1 - k0 + .1, r), k0, .22, rv=.4)
    mx.duck(k0 + .1, t3e + .3, -10.0, ramp=.25)                                              # 超神様の 音へ ゆずる
    mx.add(bell(mtof(103), .5, idx=.8, tau=.2, glock=0), k1 - .02, .05, rv=.5)               # チン（小さな 光）
    v = say(IYAN, np.random.default_rng(78), **SAY_LOUD)                                     # 声「いやーーーーん！！！」（大きな 爆発：超プレミアムの 声・大きな 声で 長く）
    tv = tb + VOICE_IYAN[0]
    mx.duck(tv, tv + len(v) / SR - .05, VOICE_IYAN[1], ramp=.04)
    mx.add(v, tv, VOICE_IYAN[2], rv=.25)


def read_glitch():
    sys.path.insert(0, os.path.join(HERE, 'flat'))
    import kami_glitch
    return kami_glitch


def powerdown(d, rng):
    """ヒュゥゥン↓：画面が 線に ちぢむ（高い 音が 下がって 消える）＋さいごに プツッ"""
    n = n_(d)
    t = tl(n)
    f = 2400 * (90 / 2400) ** np.clip(t / d, 0, 1)
    x = .6 * np.sin(phase(f, n)) + .25 * np.sign(np.sin(phase(f * .5, n)))
    x = x * np.clip(1 - t / d, 0, 1) ** .7
    k = n_(d - .012)
    if k < n:
        x[k:k + n_(.004)] += .9 * np.sign(rng.standard_normal(min(n_(.004), n - k)))
    return fade(x, .002, .004)


def hum(d, rng, f=58.0):
    """ブーン：電気の うなり（四角い 波・ゆれる・ジジジ）"""
    n = n_(d)
    t = tl(n)
    x = .55 * np.sign(np.sin(phase(f * (1 + .02 * np.sin(2 * np.pi * 3 * t)), n))) + .3 * np.sign(np.sin(phase(f * 2.003, n))) + .2 * np.sin(phase(f * 6, n))
    x = lp(x, 3500, 2) + .25 * bp(rng.standard_normal(n), 2500, 9000) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 11 * t)))
    return fade(x, .004, .02)


def glitch_mix(mx, r, KG, o=0.0):
    """昇格の バグ（2秒・kami_glitch.py の BLACK・STATES・COLLAPSE に 合わせる）：
       ブツッ＋ガッ!!（き！で 画面が 止まる）→ ブーン（電気の うなり）＋ガガッ（ずれ方が かわる たび）＋バチッ（電気）＋チッ（色が 入れかわる）
       → 画面が 消える 間は 音も 消える → ヒュゥゥン↓ プツッ（線に ちぢんで 消える）"""
    fps = KG.FPS
    dur = KG.COLLAPSE[0] / fps
    mx.add(glitch('thud', .12, r), o, .9, rv=.05)                                         # ガッ!!
    mx.add(glitch('zip', .1, r), o, .6, -.5, rv=.05)
    mx.add(glitch('zip', .1, r), o + .01, .6, .5, rv=.05)
    mx.add(boom(110, 38, .6, .2, .03, 2.4, r, grit=.2), o, .6 * FZ_LOW, rv=.1)
    mx.add(arc_zap(.18, r, 1600), o, .45, rv=.15)
    mx.add(hum(dur, r) * np.linspace(1, .8, n_(dur)), o + .02, .26, rv=.1)                # ブーン
    mx.add(crackle(dur, 120, r), o, .14, -.3, rv=.15)
    mx.add(crackle(dur, 120, r), o, .14, .3, rv=.15)
    for k, c in enumerate(KG.STATES[1:]):                                                  # ガガッ（ずれ方が かわる）
        t = o + c / fps
        mx.add(glitch(('zip', 'buzz')[k % 2], rng_d(r, .05, .12), r), t, .5, r.uniform(-.6, .6), rv=.05)
        mx.add(glitch('thud', .06, r), t, .35, rv=.05)
    for fi in range(KG.COLLAPSE[0]):                                                       # バチッ（電気：ときどき）
        if fi in KG.BLACK or r.random() > .3:
            continue
        mx.add(arc_zap(.06, r, 1200), o + fi / fps, .32, r.uniform(-.7, .7), rv=.15)
    for fi in range(2, KG.COLLAPSE[0], 6):                                                 # チッ（色が 入れかわる）
        if fi in KG.BLACK:
            continue
        mx.add(glitch('tick', .02, r), o + fi / fps, .25, (-.4, .4)[(fi // 6) % 2], rv=.05)
    bl = sorted(KG.BLACK)                                                                  # 画面が 消える 間は 音も 消す（ついたり 消えたり）
    i = 0
    while i < len(bl):
        j = i
        while j + 1 < len(bl) and bl[j + 1] == bl[j] + 1:
            j += 1
        mx.duck(o + bl[i] / fps, o + (bl[j] + 1) / fps, -30.0, ramp=.004)
        mx.add(glitch('tick', .015, r), o + (bl[j] + 1) / fps, .4, rv=.05)                 # もどる 時に チッ
        i = j + 1
    c0, c1, c2 = (o + v / fps for v in KG.COLLAPSE)                                        # ヒュゥゥン↓ プツッ
    mx.duck(c0, c2 + .2, -18.0, ramp=.01)
    mx.add(powerdown(c2 - c0 + .02, r), c0, .5, rv=.2)


def rng_d(r, a, b):
    return float(r.uniform(a, b))


def sfx_sgd_up():
    """超神様的中の 昇格（超神様的中の 4回に1回 ※仮）の 音：0秒＝き！で 画面が 止まる → 2秒 バグ → まっ暗 1秒（音も なし）
       → 宇宙の カットイン（2.97〜6.57秒）。このあと 超神様の 動画と 音（sfx_sgd）が つづく。
       超プレミアムど的中の 音（sfx_zp）は き！の 所（押してから 6秒）で 止める"""
    KG, CI = read_glitch(), read_cutin()
    g = KG.N / KG.FPS
    mx = Mix(g + CI.N / CI.FPS + 1.2, 73)
    r = mx.rng
    glitch_mix(mx, r, KG, 0.0)
    cutin_mix(mx, r, CI, g)
    return mx.render(1.5, target=-13, bass=True)


SOUNDS = (('sfx_hit_push', sfx_hit_push), ('sfx_hit', sfx_hit), ('sfx_big_push', sfx_big_push), ('sfx_big', sfx_big),
          ('sfx_fz_push', sfx_fz_push), ('sfx_fz', sfx_fz), ('sfx_pc', sfx_pc), ('sfx_zp', sfx_zp), ('sfx_gd', sfx_gd), ('sfx_sgd', sfx_sgd))

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
