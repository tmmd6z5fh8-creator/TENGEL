# 決戦調査の フィールドの 音（エリアごと・ためし：まだ アプリには 入れない）
#   まさちゃん 2026/11/19 10:12「敵が現れる前からバトルに入るまでのBGMをエリアごとに作りたい
#     Lv1:風の音、鳥の声 Lv2:強い風の音、旗が靡く音 Lv3:弱い風の音、枝が折れる音 Lv4:思い出鉄が動く音（＝重い鉄が動く音）、ドン！ドン！ドン！の足音
#     Lv5:洞窟のような音、水の音 Lv6:砂漠の音、砂が落ちる音 Lv7:強い風の音、落雷の音、瞬間移動の音 Lv8:静かな洞窟の音、ドシン！ドシン！ドシン！と重たい足音
#     Lv9:炎の音、鉄がカン！カン！カン！となる音 Lv10:静かな風の音、バァサ！バァサ！バァサ！と大きな羽が動く音
#     Lv11:おっきな針時計の針が動く音、ドシン！ドシン！ドシン！と大きな足音 Lv12:追い詰められるような音、ドシン！ドシン！ドシン！大きな足音とバァサ！バァサ！大きな羽が開く音
#     これまだアプリに入れなくていいから、音だけ作成してみて！」
#   ぜんぶ 計算で 作る（録音・よその 音は 使わない）。1エリア LOOP 秒の くり返せる 音：
#     雑音・ゆれ（風の 強さ など）は 円く つながる 作り（FFT）・時間で かわる フィルターは 2回 通して 2回目・はみ出した しっぽ（ひびき）は 頭へ 回す → つなぎ目なし
#   iPhone の スピーカーでも わかる ように：低い ドシン は 倍音（100〜400Hz）と 当たる 音を 足す・大きさは スピーカーで 聞こえる 所（280Hz〜7kHz）で そろえる
#   python3 kisekae/cb_qfield_bgm.py <出す フォルダ>              … 聞く 用：Lv01〜Lv12 の m4a（1回り ＋ 4秒・頭と おしりは ふわっと）・まとめて 聞く 1こ
#   python3 kisekae/cb_qfield_bgm.py <出す フォルダ> wav <Lv>     … その レベルの 1回り（くり返す 形）を wav で（測る 用）
import os, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
TAU = 2 * np.pi
LOOP = 32.0                      # 1回り（秒）
NL = int(round(LOOP * SR))
TAIL = int(10.0 * SR)            # 1回りの うしろに はみ出して よい 長さ（あとで 頭へ 回す）
PHONE = 0.040                    # スピーカーで 聞こえる 所の ふつうの 大きさ（12 エリア そろえる）
PEAK = 0.89
FULL_MAX = 0.085                 # ぜんぶの 音の ふつうの 大きさの 上限（イヤホンで 低い 音が 大きく なりすぎない）
VOL = {1: -2.0, 3: -4.0, 5: -3.0, 8: -3.0, 10: -3.0}      # しずかな 所は 少し 小さく（dB：風の 弱い 森・洞窟・高い 空）
AREAS = ['若草の原', '風見峠', '茨の森', '鉄門の関所', '霧鏡の湖', '刻砂の王墓', '雷鳴峡', '氷晶砦', '紅蓮の鍛冶場', '星月の回廊', '黒曜の天文台', '日蝕の玉座']


# ---------------- 道具 ----------------
def ts(sec):
    return np.arange(int(round(sec * SR))) / SR


def sos_lp(fc, order=2):
    return signal.butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos')


def sos_hp(fc, order=2):
    return signal.butter(order, fc, 'high', fs=SR, output='sos')


def sos_bp(lo, hi, order=2):
    return signal.butter(order, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos')


def lpf(x, fc, order=2):
    return signal.sosfilt(sos_lp(fc, order), x)


def hpf(x, fc, order=2):
    return signal.sosfilt(sos_hp(fc, order), x)


def bpf(x, lo, hi, order=2):
    return signal.sosfilt(sos_bp(lo, hi, order), x)


def cf(x, sos):
    """くり返す 音に 同じ フィルター（2回 ならべて 2回目 ＝ つなぎ目なし）"""
    n = len(x)
    return signal.sosfilt(sos, np.concatenate([x, x]))[n:]


def reson(x, f0, q):
    """山の 高さ 1 の 細い 山（RBJ の バンドパス）"""
    w = TAU * f0 / SR; al = np.sin(w) / (2 * q); a0 = 1 + al
    return signal.lfilter([al / a0, 0, -al / a0], [1, -2 * np.cos(w) / a0, (1 - al) / a0], x)


def tvf(x, fc, q=0.7, kind='lp', circ=True, blk=96):
    """時間で かわる フィルター（fc は 数 か 配列）。circ＝くり返す 音（2回 通して 2回目）"""
    n = len(x); fc = np.broadcast_to(np.asarray(fc, float), (n,))
    xx, ff = (np.concatenate([x, x]), np.concatenate([fc, fc])) if circ else (x, fc)
    y = np.empty_like(xx); zi = np.zeros(2)
    for s in range(0, len(xx), blk):
        f0 = min(max(float(ff[s]), 20.0), SR * 0.45); w = TAU * f0 / SR; cw = np.cos(w); al = np.sin(w) / (2 * q)
        if kind == 'lp': b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        elif kind == 'hp': b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        else: b = [al, 0.0, -al]
        a0 = 1 + al
        y[s:s + blk], zi = signal.lfilter(np.array(b) / a0, [1, -2 * cw / a0, (1 - al) / a0], xx[s:s + blk], zi=zi)
    return y[n:] if circ else y


def shaped(rng, n, lo=20.0, hi=18000.0, tilt=0.0, order=2):
    """円く つながる 雑音（lo〜hi・tilt：-0.5 ＝ ピンク・-1 ＝ ブラウン）。ふつうの 大きさ 1"""
    f = np.fft.rfftfreq(n, 1 / SR); f1 = np.maximum(f, 1e-3)
    m = (1 / np.sqrt(1 + (lo / f1) ** (2 * order))) * (1 / np.sqrt(1 + (f1 / hi) ** (2 * order))) * (np.maximum(f1, 10) / 1000.0) ** tilt
    m[0] = 0
    y = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * m, n)
    return y / (np.std(y) + 1e-12)


def curve(rng, n, fmax):
    """円く つながる ゆっくりの ゆれ（fmax Hz より 遅い）：平均 0・ふつう 1"""
    f = np.fft.rfftfreq(n, 1 / SR); m = np.exp(-(f / fmax) ** 2); m[0] = 0
    y = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * m, n)
    return y / (np.std(y) + 1e-12)


def gust(rng, n, fmax=0.12, bias=0.0, k=1.2):
    """風の 強さ（0〜1）：円く つながる"""
    return 0.5 + 0.5 * np.tanh(k * curve(rng, n, fmax) + bias)


def grains(rng, n, rate, env=None, a=3.0, sign=True):
    """こまかい 粒（砂・はじける 音）：rate＝1秒の 粒の 数・env で うすく（円く つながる 位置）"""
    k = rng.poisson(rate * n / SR); x = np.zeros(n)
    if k:
        i = rng.integers(0, n, k); v = rng.pareto(a, k) + 1.0
        if sign: v *= rng.choice([-1.0, 1.0], k)
        if env is not None: v *= env[i]
        np.add.at(x, i, v)
    return x


def ccirc(x, k):
    """円く たたみこむ（x：くり返す 長さ・k：短い 形）"""
    n = len(x)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(k, n), n)


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.where(t < a, t / max(a, 1e-5), np.exp(-(t - a) / d))


def fade_end(x, sec=0.05):
    k = min(len(x), int(sec * SR)); x = x.copy(); x[-k:] *= np.linspace(1, 0, k); return x


def sat(x, k=1.8):
    return np.tanh(k * x) / np.tanh(k)


def pang(p):
    a = (np.asarray(p, float) + 1) * np.pi / 4
    return np.cos(a) * np.sqrt(2), np.sin(a) * np.sqrt(2)


def stereo(rng, make, corr=0.5):
    """ステレオの 雑音の 床：make(rng) を 3つ（まん中・左・右）まぜる"""
    c, l, r = make(rng), make(rng), make(rng); a = np.sqrt(corr); b = np.sqrt(1 - corr)
    return np.stack([a * c + b * l, a * c + b * r])


# ---------------- ひびき ----------------
def make_ir(rng, rt, pre=0.02, dark=6000, low=120, er=0.0, echoes=()):
    n = int((rt * 1.25 + pre + 0.1) * SR); t = np.arange(n) / SR; ir = np.zeros((2, n))
    for c in range(2):
        x = rng.standard_normal(n) * (t >= pre)
        d = np.exp(-6.9 * np.maximum(0, t - pre) / rt); dh = np.exp(-6.9 * np.maximum(0, t - pre) / (rt * 0.45))
        x = signal.sosfilt(sos_lp(2500), x) * d + signal.sosfilt(sos_hp(2500), x) * dh      # 高い 音は 早く 消える
        x = signal.sosfilt(sos_lp(dark, 1), x); x = signal.sosfilt(sos_hp(low, 1), x)
        x /= np.sqrt(np.sum(x ** 2))
        for _ in range(7 if er else 0):                                                  # はじめの はねかえり（石・岩の 部屋）
            k = int(rng.uniform(0.004, pre + 0.035) * SR); x[k] += er * rng.uniform(0.4, 1.0) * rng.choice([-1, 1]) * 0.08
        for dt, g in echoes:                                                             # 谷の こだま（遠い 岩かべ）
            k = int(dt * SR)
            if k < n: e = signal.sosfilt(sos_bp(250, 3000), rng.standard_normal(int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.008)); x[k:k + len(e)] += g * e / np.sqrt(np.sum(e ** 2)) * (0.7 if c else 1.0)
        ir[c] = x
    return ir


class Mix:
    """音を ならべる 所：dry（そのまま）と wet（ひびきへ）。はみ出した 分は 頭へ 回す"""
    def __init__(s, seed):
        s.rng = np.random.default_rng(seed); s.N = NL + TAIL
        s.dry = np.zeros((2, s.N)); s.wet = np.zeros((2, s.N))

    def ev(s, x, t0, pan=0.0, g=1.0, wet=0.35, pan2=None):
        i = int(round(t0 * SR)) % NL; L = min(len(x), s.N - i); x = np.asarray(x[:L]) * g
        pl, pr = pang(pan) if pan2 is None else pang(np.linspace(pan, pan2, L))
        s.dry[0, i:i + L] += x * pl; s.dry[1, i:i + L] += x * pr
        if wet: s.wet[0, i:i + L] += x * pl * wet; s.wet[1, i:i + L] += x * pr * wet

    def bed(s, x2, g=1.0, wet=0.0):
        s.dry[:, :NL] += x2 * g
        if wet: s.wet[:, :NL] += x2 * g * wet

    def out(s, ir):
        d = s.dry[:, :NL].copy(); d[:, :TAIL] += s.dry[:, NL:]
        w = s.wet[:, :NL].copy(); w[:, :TAIL] += s.wet[:, NL:]
        m = (w[0] + w[1]) * 0.5; sd = (w[0] - w[1]) * 0.5
        wl = ccirc(m, ir[0]) + 0.35 * ccirc(sd, ir[0]); wr = ccirc(m, ir[1]) - 0.35 * ccirc(sd, ir[1])
        return d + np.stack([wl, wr])


# ---------------- 風・水・火・砂（くり返す 床）----------------
def wind(rng, n, g, lo=250, hi=1200, gain=1.0, howl=(), rustle=0.0, rust_lo=2500):
    """風：g（0〜1）で 強さと 高さが かわる。howl＝[(低い Hz, 高い Hz, q, 大きさ)]：ヒュー と 鳴る 所。rustle＝草・葉の さらさら"""
    def one(r):
        x = shaped(r, n, 70, 6000, -0.6)
        y = tvf(x, lo + (hi - lo) * g, 0.8, 'lp') * (0.25 + 0.75 * g)
        for a, b, q, v in howl:
            y += tvf(shaped(r, n, 80, 8000, -0.3), a + (b - a) * g ** 1.3, q, 'bp') * v * g ** 2 * 3.0
        if rustle:
            fl = 0.4 + 0.6 * (0.5 + 0.5 * curve(r, n, 18.0))                                   # 葉が こまかく ゆれる
            y += shaped(r, n, rust_lo, 9000, -0.2) * fl * g ** 1.6 * rustle
        return y
    return stereo(rng, one, 0.35) * gain


def flag(rng, n, g, gain=1.0, rate=(4.0, 15.0)):
    """旗の バタバタ（g：風の 強さ）。強い ほど 速く 大きく・ときどき パンッ と はじける"""
    r = rate[0] + (rate[1] - rate[0]) * g ** 1.2
    ph = np.cumsum(r) / SR; k = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    soft = np.zeros(n); hard = np.zeros(n)
    for i in k:
        j = (i + int(rng.normal(0, 0.12) / max(r[i], 1) * SR)) % n; a = g[i] ** 1.5 * rng.uniform(0.55, 1.0)
        if rng.random() < 0.16 + 0.2 * g[i]: hard[j] += a * rng.uniform(0.8, 1.4)
        else: soft[j] += a
    kt = np.arange(int(0.07 * SR)) / SR
    ks = signal.sosfilt(sos_bp(300, 2600), rng.standard_normal(len(kt))) * np.exp(-kt / 0.014)
    kh = signal.sosfilt(sos_bp(1200, 7000), rng.standard_normal(len(kt))) * np.exp(-kt / 0.0045)
    body = cf(shaped(rng, n, 90, 420, -0.3), sos_lp(500)) * (0.5 + 0.5 * np.cos(TAU * ph)) ** 2 * g ** 1.4 * 0.22    # 布の おもさ（ボフッ）
    x = ccirc(soft, ks) * 1.1 + ccirc(hard, kh) * 1.6 + body
    return x * gain


def fire(rng, n, gain=1.0, crack=9.0):
    """炎：ゴォー（低い うなり・ゆらぐ）＋ パチパチ（はじける）＋ シュー"""
    def one(r):
        fl = 0.55 + 0.45 * (0.5 + 0.5 * np.tanh(1.3 * curve(r, n, 7.0)))
        roar = shaped(r, n, 70, 650, -0.5) * fl
        roar = roar + shaped(r, n, 300, 1600, -0.3) * fl ** 2 * 0.35
        p = grains(r, n, crack, None, 2.2)
        kt = np.arange(int(0.02 * SR)) / SR
        pk = signal.sosfilt(sos_bp(900, 6000), r.standard_normal(len(kt))) * np.exp(-kt / 0.0035)
        pops = ccirc(p, pk) * 0.16
        hiss = shaped(r, n, 3000, 10000, 0.0) * (0.5 + 0.5 * curve(r, n, 2.0) * 0.5) * 0.10
        return roar * 0.55 + pops + hiss
    return stereo(rng, one, 0.4) * gain


def sand_stream(rng, sec, rate=2600, lo=1800, hi=6500):
    """サラサラ（砂時計の ように 落ちる 細い 砂）：こまかい 粒 ＋ うすい シャー"""
    n = int(sec * SR); t = np.arange(n) / SR
    e = np.clip(t / 0.6, 0, 1) * np.clip((sec - t) / 0.9, 0, 1) * (0.75 + 0.25 * np.sin(TAU * 0.7 * t + rng.uniform(0, TAU)))
    g = np.zeros(n); k = rng.poisson(rate * sec); i = rng.integers(0, n, k); np.add.at(g, i, rng.uniform(0.3, 1.0, k) * rng.choice([-1.0, 1.0], k))
    x = bpf(g * e, lo, hi, 2) * 0.55 + bpf(rng.standard_normal(n), 2500, 8000) * e * 0.10
    return fade_end(x)


# ---------------- 一つずつの 音 ----------------
def thump(f_hi, f_lo, tau_f, tau_a, sec):
    t = ts(sec); f = f_lo + (f_hi - f_lo) * np.exp(-t / tau_f)
    return np.sin(TAU * np.cumsum(f) / SR) * np.minimum(1, t / 0.003) * np.exp(-t / tau_a)


def footstep(rng, size=1.0, surf='stone', armor=False):
    """重い 足音（ドン／ドシン）：ド（当たる 胴の 音：スピーカーでも 聞こえる 250Hz〜1.3kHz）＋ ン（低い 胴と 倍音）＋ シン（地面が ふるえる）＋ 床の 音。
       低すぎる 音（〜80Hz）は イヤホン 用に 少し だけ（iPhone の スピーカーは 鳴らない ので 当たる 音と 倍音で 重さを 出す）"""
    sec = 2.2; n = int(sec * SR); t = np.arange(n) / SR; nz = lambda: rng.standard_normal(n)
    sub = thump(110 + 15 * rng.random(), 46 + 10 / size, 0.05, 0.24 * size ** 0.6, sec) * 0.3
    knock = thump(250 + 30 * rng.random(), 150 / size ** 0.2, 0.03, 0.12 * size ** 0.4, sec) * 0.7          # 胴の ドン（太鼓の ように 少し 下がる）
    body = reson(nz() * np.exp(-t / 0.012), 120 + 25 * rng.random(), 2.0) * np.exp(-t / (0.10 * size ** 0.5)) * 6.0
    x = sat(sub + knock + body, 2.4) * 0.75                                                                 # ドン（倍音つき）
    x += bpf(nz(), 250, 1500) * np.exp(-t / 0.07) * 1.9                                                     # ド（当たる：スピーカーで 聞こえる 所）
    x += reson(nz() * np.exp(-t / 0.05), 190 + 40 * rng.random(), 6) * np.exp(-t / (0.28 * size ** 0.5)) * 2.4   # シン（地面が ふるえる）
    x += hpf(nz(), 1100) * np.exp(-t / 0.0045) * 0.22                                                       # 当たる 音
    x += lpf(nz(), 85) * np.exp(-t / (0.5 * size)) * np.minimum(1, t / 0.02) * 0.18                         # 地ひびき
    if surf == 'stone':
        x += bpf(rng.standard_normal(n), 1300, 5200) * np.exp(-t / 0.018) * 0.12
        dbr = np.zeros(n); k = rng.integers(4, 10); i = (rng.uniform(0.04, 0.45, k) * SR).astype(int); np.add.at(dbr, i, rng.uniform(0.2, 1.0, k))
        x += bpf(dbr, 1800, 7000) * 0.10                                                                  # 小石が はねる
    if surf == 'ice':
        cr = np.zeros(n); k = rng.integers(60, 120); i = (rng.exponential(0.035, k) * SR).astype(int) % n; np.add.at(cr, i, rng.uniform(0.2, 1.0, k) * rng.choice([-1.0, 1.0], k))
        x += bpf(cr, 2000, 9000) * 0.28                                                                    # 氷を ふむ（ザクッ）
        sh = np.zeros(n); k = rng.integers(5, 12); i = (rng.uniform(0.08, 0.7, k) * SR).astype(int); np.add.at(sh, i, rng.uniform(0.3, 1.0, k))
        x += reson(sh, rng.uniform(3800, 5600), 25) * 0.9                                                 # 氷の かけらが チリン
    if armor:
        ar = np.zeros(n); i0 = int(rng.uniform(0.025, 0.06) * SR)
        for f, d, a in ((2310, 0.16, 0.10), (3470, 0.11, 0.08), (5120, 0.07, 0.06)):
            ar[i0:] += a * np.sin(TAU * f * (1 + rng.normal(0, 0.01)) * t[:n - i0]) * np.exp(-t[:n - i0] / d)
        x += ar                                                                                           # よろいの カチャ
    return fade_end(x * 0.9, 0.2)


def metal(rng, f0, ratios, decays, amps, sec, click=0.25, jit=0.004):
    t = ts(sec); x = np.zeros(len(t))
    for r, d, a in zip(ratios, decays, amps):
        f = f0 * r * (1 + rng.normal(0, jit)); x += a * np.sin(TAU * f * t + rng.uniform(0, TAU)) * np.exp(-t / d)
        x += a * 0.35 * np.sin(TAU * f * 1.0027 * t) * np.exp(-t / d)                       # ゆっくり うなる（2つの 山が 少し ずれる）
    x *= np.minimum(1, t / 0.0006)
    x += hpf(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.0025) * click
    return fade_end(x)


def anvil(rng, g=1.0):
    """カン！（金床を ハンマーで）"""
    f0 = 1180 * (1 + rng.normal(0, 0.012))
    x = metal(rng, f0, [1.0, 1.52, 2.43, 3.38, 4.69, 6.12, 7.9], [0.95, 0.62, 0.45, 0.32, 0.22, 0.15, 0.10], [1.0, 0.62, 0.55, 0.42, 0.3, 0.2, 0.12], 2.2, 0.45)
    t = ts(2.2); x += sat(lpf(rng.standard_normal(len(t)), 600) * np.exp(-t / 0.025), 1.5) * 0.5      # ハンマーの 重さ
    return x * g


def clink(rng, f=None):
    f = f or rng.uniform(2600, 6200); t = ts(0.12)
    x = sum(a * np.sin(TAU * f * r * t + rng.uniform(0, TAU)) * np.exp(-t / d) for r, d, a in ((1.0, 0.045, 1.0), (1.47, 0.03, 0.6), (2.31, 0.018, 0.4)))
    return x * np.minimum(1, t / 0.0004)


def chains(rng, sec, dens=40.0):
    """ジャラララ（くさりが 動く）"""
    n = int(sec * SR); x = np.zeros(n + int(0.15 * SR)); t = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 0.7
    k = rng.poisson(dens * sec)
    for tt in np.sort(rng.uniform(0, sec, k)):
        a = np.interp(tt, t, e) * rng.uniform(0.3, 1.0); c = clink(rng) * a; i = int(tt * SR); x[i:i + len(c)] += c
    x[:n] += hpf(rng.standard_normal(n), 3000) * e * 0.05                                    # こすれる シャー
    return fade_end(x * 0.5)


def ratchet(rng, sec, rate=9.0, f=3200):
    """カチカチ（歯車が 回る）"""
    n = int(sec * SR); x = np.zeros(n + int(0.2 * SR)); k = int(sec * rate)
    for j in range(k):
        i = int((j + rng.normal(0, 0.06)) / rate * SR) % n; c = clink(rng, f * rng.uniform(0.93, 1.07)) * 0.6
        kn = reson(np.r_[1.0, np.zeros(int(0.08 * SR))], 330, 6) * 3.0
        x[i:i + len(c)] += c; x[i:i + len(kn)] += kn * 0.5
    return fade_end(x * 0.6)


def groan(rng, sec, f_lo=32, f_hi=70, modes=(190, 430, 780, 1260), q=16):
    """ギギギ（重い 鉄が こすれて 動く）：つっかかって すべる パルス → 鉄の 山"""
    n = int(sec * SR); t = np.arange(n) / SR
    f = f_lo + (f_hi - f_lo) * (0.5 + 0.5 * np.sin(TAU * t / sec * 1.3 + rng.uniform(0, TAU))) * (1 + 0.15 * curve(rng, n, 3.0) / 3)
    ph = np.cumsum(f) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    p *= 0.6 + 0.4 * rng.random(n)
    e = np.clip(t / 0.25, 0, 1) * np.clip((sec - t) / 0.35, 0, 1)
    x = sum(reson(p, m * (1 + rng.normal(0, 0.01)), q) * a for m, a in zip(modes, (1.0, 0.8, 0.55, 0.35)))
    x = x * 3.0 + bpf(rng.standard_normal(n), 300, 2500) * 0.06
    return fade_end(sat(x * e, 1.3) * 0.7)


def slam(rng, g=1.0, size=1.0):
    """ガシャン（重い 鉄の 門が しまる）"""
    sec = 3.0; t = ts(sec); n = len(t)
    x = sat(thump(120, 42, 0.04, 0.35 * size, sec) + lpf(rng.standard_normal(n), 300) * np.exp(-t / 0.06) * 0.8, 2.0)
    x += metal(rng, 205 * size ** -0.3, [1.0, 1.93, 2.87, 4.11, 5.6, 7.3, 9.6, 12.4], [1.2, 0.9, 0.7, 0.5, 0.35, 0.25, 0.16, 0.1], [0.6, 0.5, 0.45, 0.4, 0.3, 0.22, 0.15, 0.1], sec, 0.6)
    x += hpf(rng.standard_normal(n), 2500) * np.exp(-t / 0.05) * 0.18
    return fade_end(x * g * 0.8)


def drip(rng, f0=None, g=1.0):
    """ぴちゃん（しずく）：水の 中の 小さな あわが 鳴る（高さが 上がる）"""
    f0 = f0 or rng.uniform(650, 1600); t = ts(0.25); f = f0 * (1 + 1.4 * (1 - np.exp(-t / 0.012)))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t / 0.028) * np.minimum(1, t / 0.0008)
    x += hpf(np.r_[np.zeros(1), np.ones(1), np.zeros(len(t) - 2)], 3000) * 0.4
    return x * g


def lap(rng, sec=1.4):
    """ちゃぷ（岸に 水が よせる）"""
    n = int(sec * SR); t = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2
    x = bpf(rng.standard_normal(n), 180, 1400) * e * 0.5 + bpf(rng.standard_normal(n), 1200, 4000) * e ** 3 * 0.12
    for _ in range(rng.integers(3, 8)):
        d = drip(rng, rng.uniform(900, 2400), rng.uniform(0.05, 0.18)); i = int(rng.uniform(0.1, 0.8) * sec * SR); L = min(len(d), n - i); x[i:i + L] += d[:L]
    return fade_end(x)


def crack(rng, size=1.0):
    """パキッ／バキッ（枝が 折れる）：はじける 音 ＋ 木の 鳴り ＋ さける 細かい 音。大きい 枝は 落ちる 音も"""
    sec = 1.8 if size > 1.2 else 0.8; n = int(sec * SR); t = np.arange(n) / SR
    imp = np.zeros(n); imp[0] = 1.0
    k = rng.integers(3, 9) + int(4 * size)
    i = (np.sort(rng.exponential(0.025 * size, k)) * SR).astype(int) % n; np.add.at(imp, i, rng.uniform(0.15, 0.7, k) * rng.choice([-1.0, 1.0], k))
    x = bpf(imp, 1500, 9500) * 2.2 + hpf(rng.standard_normal(n), 3500) * np.exp(-t / 0.004) * 0.6
    x += reson(imp, rng.uniform(800, 1500) / size ** 0.4, 5) * 1.6 * np.exp(-t / 0.06)
    if size > 1.2:
        x += sat(reson(imp, rng.uniform(230, 320), 3) * 3.0 * np.exp(-t / 0.08), 1.3) * 0.6
        fall = np.clip((t - 0.15) / 0.2, 0, 1) * np.clip((1.3 - t) / 0.5, 0, 1) * (0.5 + 0.5 * (0.5 + 0.5 * np.sin(TAU * 23 * t)))
        x += hpf(rng.standard_normal(n), 2200) * fall * 0.10                                   # 葉が ザザッ
        thud = np.zeros(n); j = int(1.15 * SR); thud[j] = 1.0; x += sat(lpf(thud, 300) * 40, 1.2) * 0.25  # 下に 落ちる
    return fade_end(x * 0.6)


def creak_wood(rng, sec=1.6):
    """木が きしむ（ギィ…）"""
    n = int(sec * SR); t = np.arange(n) / SR
    f = 55 + 25 * np.sin(np.pi * t / sec) + 6 * np.sin(TAU * 3.1 * t)
    ph = np.cumsum(f) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    x = reson(p, 420, 12) + reson(p, 760, 14) * 0.6 + reson(p, 1150, 16) * 0.3
    return fade_end(x * np.sin(np.pi * t / sec) ** 1.5 * 2.2)


def thunder(rng, close=True):
    """落雷：近い ＝ バリバリッ（はじける）＋ ズドォン（低い）＋ ゴロゴロ（長い）／遠い ＝ ゴロゴロ だけ"""
    sec = 7.0; n = int(sec * SR); t = np.arange(n) / SR
    a, d = (0.015, 1.7) if close else (0.35, 2.2)
    roll = 0.35 + 0.65 * np.clip(lpf(grains(rng, n, 6.0, None, 2.5, False), 5) * 9, 0, 1.4)
    env = np.minimum(1, t / a) * np.exp(-t / d)
    rum = (lpf(rng.standard_normal(n), 140 if close else 100, 2) * 0.8 + bpf(rng.standard_normal(n), 150, 1000) * (0.95 if close else 0.6)) * env * roll
    x = sat(rum * (1.4 if close else 0.9), 1.4)
    if close:
        x += sat(thump(95, 30, 0.12, 0.7, sec), 2.0) * 0.9                                   # ズドォン
        x += hpf(rng.standard_normal(n), 900) * np.exp(-t / 0.012) * 1.1                      # バリッ
        cr = np.zeros(n); k = rng.integers(40, 80); i = (rng.exponential(0.12, k) * SR).astype(int) % n; np.add.at(cr, i, rng.uniform(0.2, 1.0, k) * rng.choice([-1.0, 1.0], k))
        x += bpf(cr, 900, 7000) * 1.3 * np.exp(-t / 0.35)                                    # バリバリ
    return fade_end(x * 0.75, 0.6)


def teleport(rng):
    """シュン！（瞬間移動）：風を 切る 音（低→高 一気に）＋ ビッ（電気）＋ キラッ ＋ 空気が はじける"""
    sec = 0.9; n = int(sec * SR); t = np.arange(n) / SR
    fc = 350 * (6000 / 350) ** np.clip(t / 0.13, 0, 1)
    wh = tvf(rng.standard_normal(n), fc, 1.4, 'bp', circ=False) * np.clip(t / 0.09, 0, 1) ** 2 * np.exp(-np.maximum(0, t - 0.12) / 0.06) * 1.6
    f = 250 + 1700 * np.exp(-t / 0.05); zp = np.sign(np.sin(TAU * np.cumsum(f) / SR)) * np.exp(-t / 0.07) * np.minimum(1, t / 0.002)
    zp = lpf(zp, 3800) * 0.28
    sp = np.zeros(n)
    for _ in range(9):
        i = int(rng.uniform(0.09, 0.32) * SR); tt = t[:n - i]; sp[i:] += np.sin(TAU * rng.uniform(4500, 9000) * tt) * np.exp(-tt / 0.03) * rng.uniform(0.05, 0.12)
    pop = sat(thump(110, 45, 0.02, 0.06, sec), 1.5) * 0.6
    return fade_end(wh + zp + sp + pop)


def spark(rng):
    """パチッ（小さな 電気）"""
    t = ts(0.12); x = hpf(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.006)
    x += np.sign(np.sin(TAU * rng.uniform(900, 1500) * t)) * np.exp(-t / 0.015) * 0.15
    return x * 0.6


def flap(rng, size=1.0):
    """バァサ！（大きな 羽：空気を おす ボフッ ＋ 風を 切る ファ ＋ 羽の サササ）"""
    sec = 1.3; n = int(sec * SR); t = np.arange(n) / SR
    wh = sat(lpf(rng.standard_normal(n), 230) * np.clip(t / 0.06, 0, 1) * np.exp(-np.maximum(0, t - 0.06) / 0.16) * 1.6 + thump(75, 36, 0.05, 0.13 * size, sec) * 0.7, 1.6)
    sw = tvf(rng.standard_normal(n), 500 + 1500 * np.sin(np.pi * np.clip(t / 0.45, 0, 1)), 1.1, 'bp', circ=False)
    sw *= np.clip(t / 0.08, 0, 1) * np.exp(-np.maximum(0, t - 0.1) / 0.17) * 1.2
    fl = (0.5 + 0.5 * np.sin(TAU * (32 + 10 * rng.random()) * t + 3 * np.sin(TAU * 7 * t))) ** 3
    ru = hpf(rng.standard_normal(n), 2300) * fl * np.clip((t - 0.03) / 0.05, 0, 1) * np.exp(-np.maximum(0, t - 0.1) / 0.2) * 0.45
    return fade_end((wh * 0.9 + sw + ru) * size ** 0.5)


def wing_open(rng):
    """大きな 羽が 開く（バサァ…：羽が こすれて 広がる ＋ 皮が はる ＋ さいごに 風）"""
    sec = 1.8; n = int(sec * SR); t = np.arange(n) / SR
    up = np.clip(t / 1.2, 0, 1) ** 1.6
    fl = (0.5 + 0.5 * np.sin(TAU * (24 + 18 * t) * t)) ** 2
    ru = hpf(rng.standard_normal(n), 1900) * fl * up * np.clip((1.75 - t) / 0.4, 0, 1) * 0.55
    st = creak_wood(rng, 1.2) * 0.35; st = np.r_[np.zeros(int(0.25 * SR)), st][:n]; st = np.r_[st, np.zeros(n - len(st))]
    sw = bpf(rng.standard_normal(n), 300, 2200) * up ** 2 * np.clip((1.75 - t) / 0.3, 0, 1) * 0.8
    return fade_end(ru + st + sw)


def bird_phrase(rng):
    """小鳥の さえずり（チュン・ピィ・ルルル）"""
    out = []; k = rng.integers(3, 8); kind = rng.choice(['down', 'up', 'trill', 'warble'])
    fc = rng.uniform(2800, 5200)
    for _ in range(k):
        d = rng.uniform(0.045, 0.13); t = ts(d)
        if kind == 'down': f = fc * 1.25 * (0.72) ** (t / d)
        elif kind == 'up': f = fc * 0.8 * (1.5) ** (t / d)
        elif kind == 'warble': f = fc * (1 + 0.1 * np.sin(TAU * 30 * t))
        else: f = fc * (1.15 - 0.3 * (t / d))
        ph = TAU * np.cumsum(f) / SR; x = (np.sin(ph) + 0.12 * np.sin(2 * ph)) * np.sin(np.pi * t / d) ** 1.3
        out += [x, np.zeros(int(rng.uniform(0.035, 0.11) * SR))]
        if rng.random() < 0.3: fc *= rng.uniform(0.9, 1.12)
    return np.concatenate(out) * 0.5


def uguisu(rng):
    """ホーーホケキョ（遠くの うぐいす）"""
    def tone(f0, f1, d, vib=0.0, vr=5.0, att=0.02):
        t = ts(d); f = f0 * (f1 / f0) ** (t / d) * (1 + vib * np.sin(TAU * vr * t))
        ph = TAU * np.cumsum(f) / SR; e = np.minimum(1, t / att) * np.clip((d - t) / 0.03, 0, 1)
        return (np.sin(ph) + 0.06 * np.sin(2 * ph)) * e
    z = lambda s: np.zeros(int(s * SR))
    x = np.concatenate([tone(1060, 1200, 1.0, 0.004, 5.0, 0.15), z(0.13), tone(1350, 1300, 0.07), z(0.03), tone(2250, 1900, 0.07), z(0.025), tone(1550, 2750, 0.3, 0.025, 22.0, 0.01)])
    return x * 0.55


def clock_tick(rng, tock=False, big=False):
    """大きな 時計の カチッ（針が 動く）：高い カチ ＋ 中の カタン ＋ 大きな 針の 重さ。big＝ガコン（大きく 動く）"""
    sec = 1.2; n = int(sec * SR); t = np.arange(n) / SR
    f = 2900 if not tock else 2450
    x = metal(rng, f, [1.0, 1.61, 2.37], [0.03, 0.02, 0.012], [1.0, 0.6, 0.35], sec, 0.3)
    x += reson(np.r_[1.0, np.zeros(n - 1)], 260 if not tock else 220, 5) * 4.0 * np.exp(-t / 0.06)
    x += sat(thump(140, 90, 0.02, 0.18, sec), 1.4) * 0.2
    if big:
        x = x * 1.3 + slam(rng, 0.5, 1.6)[:n] * 0.3
        wr = ratchet(rng, 0.45, 26, 3600)[:n]; x[:len(wr)] += wr * 0.5
    return fade_end(x * 0.6)


def heartbeat(rng):
    """ドクン・ドクン（追いつめられる 心臓）"""
    sec = 0.7; t = ts(sec); n = len(t)
    one = lambda a: sat(thump(85, 42, 0.03, 0.09, sec) * a + lpf(rng.standard_normal(n), 160) * np.exp(-t / 0.05) * 0.5 * a, 2.0)
    x = one(1.0); j = int(0.24 * SR); x[j:] += one(0.7)[:n - j]
    return fade_end(x)


def shepard(n, base=55.0, octs=7, per=16.0, rise=True, bright=1800):
    """どこまでも 上がって いく 音（シェパード：1回りで ぴったり つながる）"""
    t = np.arange(n) / SR; x = np.zeros(n); u = (t / per) % 1.0 if rise else (1 - (t / per) % 1.0)
    for k in range(octs):
        p = (k + u) % octs; f = base * 2 ** p
        w = np.exp(-0.5 * ((p - octs / 2) / (octs / 5.5)) ** 2)
        ph = TAU * np.cumsum(f) / SR
        x += w * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
    return lpf(x, bright) / octs


# ---------------- 12 エリア ----------------
def lv1(m):
    """若草の原：そよ風 ＋ 草の さらさら ＋ 小鳥 ＋ 遠くの うぐいす"""
    r = m.rng; g = gust(r, NL, 0.10, -0.2, 1.0)
    m.bed(wind(r, NL, g, 220, 850, 0.30, rustle=0.55, rust_lo=2800), wet=0.15)
    for t0 in (1.2, 4.6, 7.9, 10.2, 14.8, 17.3, 20.6, 23.9, 26.1, 29.4):
        p = r.uniform(-0.85, 0.85); d = r.uniform(0.25, 1.0)
        m.ev(bird_phrase(r), t0 + r.uniform(-0.3, 0.3), p, 1.0 * d, 0.2 + 0.4 * (1 - d))
    m.ev(uguisu(r), 12.0, -0.35, 0.75, 0.45)
    m.ev(uguisu(r), 27.0, 0.55, 0.42, 0.6)
    return dict(rt=1.0, pre=0.015, dark=7000)


def lv2(m):
    """風見峠：強い 風（ヒュー）＋ 旗の バタバタ ＋ 旗ざおの 金具が カン"""
    r = m.rng; g = gust(r, NL, 0.16, 0.9, 1.0)
    m.bed(wind(r, NL, g, 300, 1700, 0.55, howl=((380, 820, 14, 0.5), (950, 1500, 18, 0.25)), rustle=0.18), wet=0.15)
    f1 = flag(r, NL, np.roll(g, int(0.15 * SR)), 1.0); f2 = flag(r, NL, np.roll(g, int(0.6 * SR)), 0.5)
    pl, pr = pang(0.35); ql, qr = pang(-0.6)
    m.bed(np.stack([f1 * pl + f2 * ql, f1 * pr + f2 * qr]), 0.8, wet=0.25)
    for t0 in (3.4, 9.8, 16.1, 22.7, 28.3):
        m.ev(metal(r, r.uniform(1900, 2300), [1.0, 2.71, 5.2], [0.25, 0.12, 0.06], [1.0, 0.5, 0.3], 0.8, 0.2), t0, 0.35, 0.12 * (0.5 + g[int(t0 * SR)]), 0.3)
    return dict(rt=0.8, pre=0.012, dark=6000)


def lv3(m):
    """茨の森：弱い 風 ＋ 葉が ゆれる ＋ 枝が 折れる（パキッ・バキッ）＋ 木が きしむ"""
    r = m.rng; g = gust(r, NL, 0.07, -0.5, 0.6)
    m.bed(wind(r, NL, g, 300, 800, 0.07, rustle=0.9, rust_lo=2200), wet=0.2)
    for t0, sz, p, gg in ((2.2, 0.8, 0.6, 0.8), (5.9, 1.0, -0.4, 1.0), (6.25, 0.7, -0.45, 0.55), (11.4, 1.6, 0.2, 1.15), (16.8, 0.8, -0.8, 0.45),
                          (20.5, 1.0, 0.7, 0.9), (24.9, 0.8, -0.2, 0.7), (25.3, 0.6, -0.15, 0.4), (29.1, 1.1, 0.4, 0.85)):
        m.ev(crack(r, sz), t0, p, gg * 1.6, 0.45)
    m.ev(creak_wood(r, 1.8), 14.2, -0.55, 0.18, 0.6)
    return dict(rt=1.3, pre=0.02, dark=5500, er=0.4)


def lv4(m):
    """鉄門の関所：重い 鉄が 動く（ジャラララ・カチカチ・ギギギ・ガシャン）＋ ドン！ドン！ドン！"""
    r = m.rng; g = gust(r, NL, 0.08, -0.6, 1.0)
    m.bed(wind(r, NL, g, 150, 480, 0.22), wet=0.1)
    m.bed(stereo(r, lambda q: shaped(q, NL, 35, 140, -1.0), 0.6), 0.04)
    m.ev(chains(r, 4.0), 0.8, -0.3, 0.9, 0.35, pan2=0.1); m.ev(ratchet(r, 4.2), 0.7, -0.15, 0.7, 0.3); m.ev(groan(r, 4.6), 0.9, 0.0, 0.8, 0.4)
    m.ev(slam(r, 1.0), 6.0, 0.0, 1.0, 0.5)
    for k, t0 in enumerate((9.6, 10.35, 11.1)): m.ev(footstep(r, 1.0, 'stone', True), t0, 0.25, 0.75, 0.4)
    m.ev(chains(r, 2.8), 15.0, 0.45, 0.6, 0.45); m.ev(groan(r, 3.0, 28, 55), 15.2, 0.35, 0.65, 0.45); m.ev(slam(r, 0.55, 1.1), 18.4, 0.4, 0.8, 0.6)
    for k, t0 in enumerate((22.4, 23.15, 23.9)): m.ev(footstep(r, 1.05, 'stone', True), t0, -0.1, 1.0, 0.32)
    m.ev(slam(r, 0.3, 0.9), 28.6, -0.6, 0.6, 0.9)
    return dict(rt=1.9, pre=0.03, dark=5000, er=0.8)


def lv5(m):
    """霧鏡の湖：洞窟の ような ひびき（低い うなり・空気）＋ しずく（ぴちゃん）＋ 水が よせる（ちゃぷ）"""
    r = m.rng; n = NL; t = np.arange(n) / SR
    m.bed(stereo(r, lambda q: shaped(q, n, 30, 150, -1.0), 0.5), 0.07)
    sw = 0.6 + 0.4 * (0.5 + 0.5 * curve(r, n, 0.08))
    m.bed(stereo(r, lambda q: shaped(q, n, 160, 900, -0.5) * sw, 0.3), 0.07, wet=0.4)
    hum = (np.sin(TAU * 58 * t) * 0.6 + np.sin(TAU * 87.5 * t) * 0.4 + 0.25 * np.sin(TAU * 175 * t)) * (0.5 + 0.5 * np.sin(TAU * t / LOOP * 2) ** 2)
    m.bed(np.stack([hum, hum]), 0.02)
    for t0 in (0.6, 4.4, 8.9, 13.1, 17.6, 21.2, 25.8, 29.6):
        m.ev(lap(r, r.uniform(1.1, 1.8)), t0, r.uniform(-0.6, 0.6), 0.45, 0.5)
    for t0 in (1.9, 3.3, 6.1, 7.0, 9.8, 11.7, 12.0, 15.4, 18.9, 20.1, 23.5, 24.3, 27.2, 30.5):
        d = r.uniform(0.3, 1.0); m.ev(drip(r), t0 + r.uniform(-0.15, 0.15), r.uniform(-0.8, 0.8), 0.95 * d, 0.45 + 0.5 * (1 - d))
    return dict(rt=4.2, pre=0.04, dark=4500, er=1.0)


def lv6(m):
    """刻砂の王墓：かわいた 砂漠の 風（砂が 舞う シャー）＋ 砂が 落ちる（サラサラ・ザザー）＋ 石の 部屋の 風（ヒュオォ）"""
    r = m.rng; n = NL; g = gust(r, n, 0.10, 0.4, 0.9)
    m.bed(wind(r, n, g, 260, 950, 0.40, rustle=0.0), wet=0.15)
    def hiss(q):
        return shaped(q, n, 1500, 7500, -0.2) * g ** 1.8 * 0.15 + cf(grains(q, n, 700, g ** 2.5, 6.0), sos_bp(2200, 8000)) * 0.06
    m.bed(stereo(r, hiss, 0.3), 1.0, wet=0.1)
    moan = tvf(shaped(r, n, 80, 3000, -0.5), 230 + 110 * g, 9, 'bp') * g ** 2 * 0.9
    m.bed(np.stack([moan, moan * 0.8]), 0.30, wet=0.6)
    for t0, sec, p in ((2.0, 6.0, -0.5), (12.5, 5.0, 0.6), (22.0, 7.0, -0.1)):
        m.ev(sand_stream(r, sec), t0, p, 1.5, 0.35)
    m.ev(sand_stream(r, 1.9, 9000, 900, 6000) * 1.3, 17.0, 0.3, 1.6, 0.45)
    m.ev(sand_stream(r, 3.5, 1800), 18.6, 0.35, 1.0, 0.4)
    return dict(rt=2.4, pre=0.03, dark=5000, er=0.6)


def lv7(m):
    """雷鳴峡：強い 風（ヒュー）＋ 落雷（バリバリッ ズドォン ゴロゴロ）＋ 瞬間移動（シュン！）＋ パチッ"""
    r = m.rng; n = NL; g = gust(r, n, 0.2, 0.9, 1.0)
    m.bed(wind(r, n, g, 250, 1600, 0.55, howl=((300, 700, 12, 0.45), (800, 1300, 16, 0.2)), rustle=0.12), wet=0.15)
    m.ev(thunder(r, True), 3.0, 0.3, 1.0, 0.35)
    m.ev(teleport(r), 8.6, -0.7, 0.85, 0.3, pan2=0.7); m.ev(teleport(r), 9.2, 0.7, 0.75, 0.3, pan2=-0.2)
    m.ev(thunder(r, False), 13.5, -0.5, 0.8, 0.5)
    m.ev(thunder(r, True), 19.0, -0.2, 1.1, 0.35)
    m.ev(teleport(r), 24.0, -0.3, 0.9, 0.3, pan2=0.8)
    m.ev(thunder(r, False), 28.0, 0.6, 0.7, 0.5)
    for t0 in (11.2, 21.6, 26.8, 26.95): m.ev(spark(r), t0, r.uniform(-0.6, 0.6), 0.5, 0.2)
    return dict(rt=2.2, pre=0.05, dark=5500, echoes=((0.42, 0.22), (0.78, 0.12)))


def lv8(m):
    """氷晶砦：しずかな 洞窟（つめたい 空気・氷が チリッ・ピキッ）＋ ドシン！ドシン！ドシン！（重い 足音：氷を ふむ）"""
    r = m.rng; n = NL
    m.bed(stereo(r, lambda q: shaped(q, n, 25, 120, -1.0), 0.5), 0.035)
    m.bed(stereo(r, lambda q: shaped(q, n, 3000, 10000, 0.0) * (0.6 + 0.4 * (0.5 + 0.5 * curve(q, n, 0.1))), 0.2), 0.05, wet=0.3)
    ice = cf(grains(r, n, 1.4, None, 3.0), sos_bp(2800, 7500)); ice = reson(np.concatenate([ice, ice]), 4300, 18)[n:] * 2.0
    m.bed(np.stack([ice, np.roll(ice, int(0.3 * SR))]), 0.6, wet=0.8)
    m.ev(creak_wood(r, 1.4) * 0.6, 12.8, 0.6, 0.25, 0.8)
    for grp, (gg, wt, p) in zip(((5.0, 6.25, 7.5), (15.5, 16.75, 18.0), (26.0, 27.25, 28.5)), ((0.55, 0.6, -0.4), (0.85, 0.45, 0.25), (1.15, 0.35, 0.0))):
        for t0 in grp: m.ev(footstep(r, 1.45, 'ice'), t0, p, gg, wt)
    return dict(rt=3.6, pre=0.05, dark=8500, er=0.8)


def lv9(m):
    """紅蓮の鍛冶場：炎（ゴォー・パチパチ）＋ ふいごで 炎が ゴワッ ＋ 鉄を たたく カン！カン！カン！"""
    r = m.rng; n = NL; t = np.arange(n) / SR
    fl = 1.0 + 0.6 * (np.exp(-((t - 1.2) % LOOP) / 1.4) * np.minimum(1, ((t - 0.6) % LOOP) / 0.6) + np.exp(-((t - 17.0) % LOOP) / 1.4) * np.minimum(1, ((t - 16.4) % LOOP) / 0.6))
    m.bed(fire(r, n, 1.0) * fl, 0.75, wet=0.15)
    for t0 in (0.6, 16.4):
        x = bpf(r.standard_normal(int(1.6 * SR)), 180, 1600) * np.sin(np.pi * np.clip(ts(1.6) / 1.6, 0, 1)) ** 2; m.ev(x * 0.35, t0, 0.2, 1.0, 0.3)
    for grp, p in (((3.2, 3.62, 4.04), 0.15), ((10.8, 11.22, 11.64), -0.25), ((18.6, 19.02, 19.44), 0.3), ((26.2, 26.62, 27.04), -0.1)):
        for k, t0 in enumerate(grp): m.ev(anvil(r, (0.85, 0.9, 1.05)[k]), t0 + r.normal(0, 0.012), p, 0.8, 0.35)
    return dict(rt=1.4, pre=0.02, dark=6000, er=0.6)


def lv10(m):
    """星月の回廊：しずかな 風（高い 空の 空気）＋ バァサ！バァサ！バァサ！（大きな 羽）"""
    r = m.rng; n = NL; g = gust(r, n, 0.07, -0.4, 1.0)
    m.bed(wind(r, n, g, 280, 700, 0.26, howl=((1150, 1550, 25, 0.12),), rustle=0.0), wet=0.3)
    m.bed(stereo(r, lambda q: shaped(q, n, 2000, 8000, -0.2) * (0.5 + 0.5 * g), 0.2), 0.05, wet=0.3)
    for grp, (gg, p0, p1) in zip(((6.0, 6.85, 7.7), (17.0, 17.85, 18.7), (27.0, 27.85, 28.7)), ((0.65, -0.6, -0.2), (0.85, 0.55, 0.1), (1.1, -0.1, 0.3))):
        for k, t0 in enumerate(grp):
            p = p0 + (p1 - p0) * k / 2; m.ev(flap(r, 1.25), t0, p, gg, 0.45)
    return dict(rt=2.8, pre=0.03, dark=7000)


def lv11(m):
    """黒曜の天文台：大きな 針時計（カチッ・コチッ・8つに 1回 ガコン）＋ ドシン！ドシン！ドシン！"""
    r = m.rng; n = NL
    m.bed(stereo(r, lambda q: shaped(q, n, 40, 220, -0.8), 0.6), 0.035)
    for k in range(int(LOOP)):
        m.ev(clock_tick(r, k % 2 == 1, k % 8 == 7), 0.5 + k, 0.1, 0.8, 0.45)
    for grp, (gg, p) in zip(((10.3, 11.5, 12.7), (23.3, 24.5, 25.7)), ((0.8, -0.3), (1.05, 0.15))):
        for t0 in grp: m.ev(footstep(r, 1.35, 'stone'), t0, p, gg, 0.45)
    return dict(rt=3.0, pre=0.04, dark=5500, er=0.7)


def lv12(m):
    """日蝕の玉座：追いつめられる 音（低い うなり・どこまでも 上がる 音・心臓・高い 不安な ふるえ）＋ ドシン！ドシン！ドシン！ ＋ 大きな 羽が 開く バァサ！バァサ！"""
    r = m.rng; n = NL; t = np.arange(n) / SR
    sw = 0.65 + 0.35 * np.sin(TAU * t / LOOP * 2) ** 2
    def saw(f):
        return sum(np.sin(TAU * f * h * t + r.uniform(0, TAU)) / h for h in range(1, 9))
    dr = lpf(np.concatenate([saw(73.42) + saw(77.78) * 0.8 + saw(36.71) * 0.25] * 2), 420)[n:] * sw
    m.bed(np.stack([dr, dr * 0.95]), 0.11, wet=0.3)
    sh = shepard(n, 55.0, 7, 16.0, True, 1800); m.bed(np.stack([sh, np.roll(sh, int(0.01 * SR))]), 0.55, wet=0.4)
    tr = (np.sin(TAU * 1318.5 * t) + np.sin(TAU * 1396.9 * t) * 0.8) * (0.5 + 0.5 * np.sin(TAU * 7.0 * t)) * (0.5 + 0.5 * np.sin(TAU * t / LOOP * 4 + 1.0)) ** 2
    m.bed(np.stack([tr, tr * 0.7]), 0.018, wet=0.6)
    for k in range(int(LOOP / 0.8)): m.ev(heartbeat(r), k * 0.8, 0.0, 0.32, 0.15)
    for grp, (gg, p) in zip(((4.0, 5.3, 6.6), (18.0, 19.3, 20.6)), ((0.85, -0.2), (1.1, 0.2))):
        for t0 in grp: m.ev(footstep(r, 1.5, 'stone'), t0, p, gg, 0.45)
    for t0, p in ((10.0, -0.3), (25.0, 0.35)):
        m.ev(wing_open(r), t0, p, 0.9, 0.5); m.ev(flap(r, 1.5), t0 + 1.6, p, 1.0, 0.5); m.ev(flap(r, 1.5), t0 + 2.5, p, 1.05, 0.5)
    return dict(rt=3.4, pre=0.05, dark=5000, er=0.6)


LEVELS = [lv1, lv2, lv3, lv4, lv5, lv6, lv7, lv8, lv9, lv10, lv11, lv12]


# ---------------- 仕上げ ----------------
def phone_rms(x):
    b = signal.butter(4, [280, 7000], 'band', fs=SR, output='sos')
    y = cf(x.mean(axis=0), b)
    return float(np.sqrt(np.mean(y ** 2)))


def limit(x, th=0.62, peak=PEAK):
    a = np.abs(x); o = a > th; y = x.copy()
    y[o] = np.sign(x[o]) * (th + (peak - th) * np.tanh((a[o] - th) / (peak - th)))
    return y


def render(lv):
    m = Mix(1000 + lv * 101); p = LEVELS[lv - 1](m)
    ir = make_ir(np.random.default_rng(lv * 7), p['rt'], p.get('pre', 0.02), p.get('dark', 6000), 120, p.get('er', 0.0), p.get('echoes', ()))
    x = m.out(ir)
    x = np.stack([cf(c, sos_hp(42, 2)) for c in x])      # 聞こえない ほど 低い 音（40Hz より 下）は 切る
    x *= PHONE * 10 ** (VOL.get(lv, 0.0) / 20) / phone_rms(x)
    full = float(np.sqrt(np.mean(x ** 2)))
    if full > FULL_MAX: x *= FULL_MAX / full
    return limit(x)


def listen(x, extra=4.0, fin=0.6, fout=2.5):
    """聞く 用：1回り ＋ extra 秒（くり返しの つづき）・頭は ふわっと・おしりは ゆっくり 消える"""
    k = int(extra * SR); y = np.concatenate([x, x[:, :k]], axis=1); n = y.shape[1]
    e = np.ones(n); a = int(fin * SR); b = int(fout * SR)
    e[:a] = np.linspace(0, 1, a) ** 2; e[-b:] = np.linspace(1, 0, b) ** 1.5
    return y * e


def save_wav(x, path):
    wavfile.write(path, SR, (np.clip(x.T, -1, 1) * 32767).astype(np.int16))


def to_m4a(x, path):
    tmp = tempfile.mkdtemp(); w = os.path.join(tmp, 'a.wav'); save_wav(x, w)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-ac', '2', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', path], check=True)


def name(lv):
    return f'決戦調査_フィールド音_Lv{lv:02d}_{AREAS[lv - 1]}_ためし.m4a'


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 3 and sys.argv[2] == 'wav':
        lv = int(sys.argv[3]); x = render(lv); p = os.path.join(out, f'field_lv{lv:02d}.wav'); save_wav(x, p)
        print(p, f'山 {np.abs(x).max():.2f}・スピーカーの 所 {phone_rms(x):.4f}')
        sys.exit(0)
    only = [int(v) for v in sys.argv[2:]] or list(range(1, 13)); allx = []
    for lv in only:
        x = render(lv); y = listen(x); to_m4a(y, os.path.join(out, name(lv))); allx.append(y)
        print(f'Lv{lv:02d} {AREAS[lv - 1]}：山 {np.abs(x).max():.2f}・ふつう {np.sqrt(np.mean(x ** 2)):.4f}・スピーカーの 所 {phone_rms(x):.4f}', flush=True)
    if len(only) == 12:
        gap = np.zeros((2, int(1.2 * SR)))
        to_m4a(np.concatenate(sum([[y, gap] for y in allx], [])[:-1], axis=1), os.path.join(out, '決戦調査_フィールド音_12エリア_まとめて聞く_ためし.m4a'))
        print('まとめ：できた')
