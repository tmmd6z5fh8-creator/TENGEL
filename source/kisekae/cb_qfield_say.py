# 決戦調査の フィールド：セリフに 合わせた 音（ためし：まだ アプリには 入れない）
#   まさちゃん 2026/11/19 12:29「Lvごとのセリフ表示して！ そのセリフに合わせて臨場感が出るように音作れる？」
#   セリフの 中の 音の 字（チリン♪・ギギギ……ガシャン！ など）や ようす（薔薇が一斉に揺れる など）を、その 字が 出た とき に 鳴らす（行ごとの きっかけ）
#   ＋ 下に エリアの 環境音（cb_qfield_bgm.py の 風・洞窟・炎 など：足音・雷 などの 出来事は 入れない ＝ セリフの 音と ぶつからない）を 小さく
#   聞いて みる 版：アプリと 同じ 流れ（フィールドが 出て 0.7秒で 1行目・字は 1字 34ms・読む 時間の あと タップの 音で 次の 行・敵の 行で アプリの magic・appear の 音・
#     さいごの 行の あと 敵の 名前 →「タップで バトル開始！」まで）。セリフは cb/cb_app.js の QUEST から 読む（まさちゃんの 表の まま）
#   ぜんぶ 計算で 作る（録音・よその 音は 使わない）
#   python3 kisekae/cb_qfield_say.py <出す フォルダ> [Lv ...]     … 聞く 用の m4a（Lv ごと）・まとめて 聞く 1こ（12 ぜんぶの とき）
import os, re, sys
import numpy as np
from scipy import signal
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import cb_qfield_bgm as B
import cb_sfx
SR = B.SR; TAU = B.TAU
CH = 0.034                       # 1字の 時間（アプリ：34ms）
APP = os.path.join(os.path.dirname(H), 'cb', 'cb_app.js')


def says():
    """cb/cb_app.js の QUEST から [エリア, 敵, [セリフ], 敵が 出る 行] を 読む"""
    s = open(APP, encoding='utf8').read()
    out = []
    for m in re.finditer(r"\['([^']+)', '([^']+)', '[^']+', \d+, \d+, \{[^}]*\}, \[(.*?)\], (\d+)\]", s):
        out.append((m.group(1), m.group(2), re.findall(r"'([^']*)'", m.group(3)), int(m.group(4))))
    assert len(out) == 12
    return out


ts, lpf, hpf, bpf, reson, tvf, sat, fade_end, thump, metal = B.ts, B.lpf, B.hpf, B.bpf, B.reson, B.tvf, B.sat, B.fade_end, B.thump, B.metal


def pad(x, sec):
    return np.concatenate([x, np.zeros(int(sec * SR))])


def mix(*parts):
    """[(音, 何秒 あと, 大きさ)] を 1つに"""
    n = max(int(t * SR) + len(x) for x, t, g in parts); y = np.zeros(n)
    for x, t, g in parts:
        i = int(t * SR); y[i:i + len(x)] += x * g
    return y


# ---------------- セリフの 音 ----------------
def bell(rng, strikes=((0.0, 0.55), (0.075, 1.0)), f0=None):
    """チリン（小さな 鈴）"""
    f0 = f0 or rng.uniform(2650, 2950); sec = 2.4; n = int(sec * SR); y = np.zeros(n)
    for t0, a in strikes:
        i = int(t0 * SR); x = metal(rng, f0 * rng.uniform(0.996, 1.004), [1.0, 2.09, 2.98, 4.31, 5.62], [0.9, 0.55, 0.38, 0.22, 0.14], [1.0, 0.5, 0.35, 0.2, 0.12], sec, 0.12, 0.002)
        y[i:] += x[:n - i] * a
    return fade_end(y * 0.5, 0.3)


def jingle(rng, sec=1.0, rate=9.0):
    """チリンチリンッ（鈴が はずんで ゆれる）"""
    st = []; t = 0.0
    while t < sec: st.append((t, rng.uniform(0.4, 1.0))); t += rng.uniform(0.5, 1.4) / rate
    return bell(rng, tuple(st), rng.uniform(2700, 3000)) * 0.9


def hoof_dirt(rng, cut=3000, g=1.0):
    """草地を ける ひづめ（ダッ）"""
    sec = 0.25; t = ts(sec); n = len(t)
    x = sat(thump(190, 95, 0.012, 0.045, sec) * 1.0 + lpf(rng.standard_normal(n), 400) * np.exp(-t / 0.02) * 0.6, 1.6)
    x += bpf(rng.standard_normal(n), 400, cut) * np.exp(-t / 0.018) * 0.55
    return fade_end(x * g)


def gallop(rng, sec=1.6, start=0.25, end=1.0, bells=True, cut=(900, 4000)):
    """ダダダッ（子馬が 走って 来る：3つずつ・近づく）"""
    n = int((sec + 0.4) * SR); y = np.zeros(n); t = 0.0; stride = 0.34
    while t < sec - 0.1:
        u = t / sec; a = start + (end - start) * u ** 1.3; c = cut[0] + (cut[1] - cut[0]) * u
        for dt, k in ((0.0, 0.8), (0.075, 1.0), (0.14, 0.9)):
            h = hoof_dirt(rng, c, a * k); i = int((t + dt + rng.normal(0, 0.006)) * SR); L = min(len(h), n - i); y[i:i + L] += h[:L]
        if bells:
            b = bell(rng, ((0.0, 0.5), (0.05, 0.8)), rng.uniform(2700, 3000)) * a * 0.55; i = int((t + 0.03) * SR); L = min(len(b), n - i); y[i:i + L] += b[:L]
        t += stride * rng.uniform(0.95, 1.05)
    return fade_end(y)


def flag_burst(rng, sec=1.3):
    """バタバタバタッ（旗が 強い 風で）"""
    n = int(sec * SR); t = np.arange(n) / SR; g = np.clip(t / 0.12, 0, 1) * np.clip((sec - t) / 0.25, 0, 1) * 0.95
    x = B.flag(rng, n, g, 1.0, (11.0, 16.0))
    m = n + int(0.3 * SR); cr = np.zeros(m); cr[int((sec - 0.18) * SR)] = 1.0; cr = bpf(cr, 1200, 7000) * 6.0      # さいごの パンッ
    return fade_end(np.r_[x, np.zeros(m - n)] + cr * 0.8)


def zoom(rng):
    """ビュンッ（すごい 速さで 横切る：風を 切る ＋ ひづめ）"""
    sec = 1.1; n = int(sec * SR); t = np.arange(n) / SR
    fc = 2600 * (650 / 2600) ** np.clip((t - 0.05) / 0.35, 0, 1)
    w = tvf(rng.standard_normal(n), fc, 1.3, 'bp', circ=False) * np.exp(-((t - 0.17) / 0.08) ** 2) * 3.0
    w += lpf(rng.standard_normal(n), 350) * np.exp(-((t - 0.17) / 0.07) ** 2) * 0.9
    for k in range(4):
        h = hoof_dirt(rng, 2500, 0.45 * np.exp(-((0.05 + k * 0.07 - 0.17) / 0.12) ** 2)); i = int((0.05 + k * 0.07) * SR); y = min(len(h), n - i); w[i:i + y] += h[:y]
    return fade_end(w)


def step_leaves(rng, g=1.0):
    """ザク（落ち葉と 小枝を ふむ）"""
    sec = 0.6; t = ts(sec); n = len(t)
    cr = B.grains(rng, n, 2600, np.exp(-t / 0.09) * np.clip(t / 0.01, 0, 1), 4.0)
    x = bpf(cr, 900, 7000) * 0.35 + lpf(rng.standard_normal(n), 260) * np.exp(-t / 0.035) * 0.45
    if rng.random() < 0.6: x += B.crack(rng, 0.5)[:n] * 0.25
    return fade_end(x * g)


def rustle(rng, sec=0.6, sharp=False, g=1.0):
    """ガサ／ガサッ（しげみ・茨が ゆれる）"""
    n = int(sec * SR); t = np.arange(n) / SR
    fl = (0.5 + 0.5 * np.sin(TAU * (16 + 10 * rng.random()) * t + 2.0 * np.sin(TAU * 3.3 * t))) ** 2
    e = np.clip(t / (0.02 if sharp else 0.12), 0, 1) * np.exp(-np.maximum(0, t - (0.05 if sharp else 0.18)) / (0.12 if sharp else 0.25))
    x = bpf(rng.standard_normal(n), 800, 7500) * fl * e * 0.6
    if sharp:
        x += bpf(B.grains(rng, n, 500, e, 3.0), 2000, 8000) * 0.5 + B.crack(rng, 0.6)[:n] * 0.3                 # とげが こすれて パキッ
    return fade_end(x * g)


def snort(rng, sec=0.9):
    """ブルルッ（馬が 鼻を 鳴らす：くちびるが ふるえる）"""
    n = int(sec * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n)
    fr = 26 - 8 * t / sec
    fl = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(TAU * np.cumsum(fr) / SR + 0.6 * np.sin(TAU * 4 * t))) ** 1.6
    e = np.clip(t / 0.03, 0, 1) * np.clip((sec - t) / 0.25, 0, 1)
    br = reson(nz, 380, 3.5) * 1.0 + reson(nz, 1050, 4.5) * 0.7 + reson(nz, 2400, 5.0) * 0.45 + hpf(nz, 3200) * 0.06
    x = br * fl * e * 3.2 + reson(rng.standard_normal(n), 170, 2.5) * fl * e * 1.6
    x += lpf(rng.standard_normal(n), 900) * np.exp(-t / 0.04) * 0.5                                          # ブ（はじめに 息が 出る）
    return fade_end(sat(x * 0.7, 1.5))


def hoof_stone(rng, g=1.0, big=False):
    """カツン（石の 床を ひづめで）"""
    sec = 0.9; t = ts(sec); n = len(t)
    x = hpf(rng.standard_normal(n), 2500) * np.exp(-t / 0.0028) * 0.9
    x += reson(rng.standard_normal(n) * np.exp(-t / 0.004), rng.uniform(1000, 1250), 6) * np.exp(-t / 0.045) * 5.0
    x += np.sin(TAU * rng.uniform(2200, 2500) * t) * np.exp(-t / 0.05) * 0.12
    x += sat(lpf(rng.standard_normal(n), 300) * np.exp(-t / (0.05 if big else 0.03)) * (1.6 if big else 0.6), 1.5) * 0.6
    if big: x += B.footstep(rng, 1.2, 'stone')[:n] * 0.55
    return fade_end(x * g)


def stomp(rng, g=1.0, size=1.35):
    """ダンッ（強く ふみ鳴らす）"""
    x = B.footstep(rng, size, 'stone'); t = ts(len(x) / SR)
    x += bpf(rng.standard_normal(len(x)), 300, 2500) * np.exp(-t / 0.03) * 0.8                                 # ダン の 当たり
    return x * g


def gust1(rng, sec=2.2, f=(500, 900, 600), q=9.0, body=0.6, hiss=0.0):
    """ヒュゥゥ（風が 1つ 吹く：鳴る 高さが 上がって 下がる）"""
    n = int(sec * SR); t = np.arange(n) / SR; e = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 1.4
    fc = np.interp(t, [0, 0.45 * sec, sec], f)
    x = tvf(rng.standard_normal(n), fc, q, 'bp', circ=False) * e * 2.4
    x += tvf(rng.standard_normal(n), 250 + 700 * e, 0.8, 'lp', circ=False) * e * body
    if hiss: x += hpf(rng.standard_normal(n), 3500) * e ** 2 * hiss
    return fade_end(x)


def plop(rng):
    """ポチャン（大きな しずく・何かが 水に）"""
    sec = 1.0; t = ts(sec); n = len(t)
    f = 330 * (1 + 2.0 * (1 - np.exp(-t / 0.02)))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.001) * 0.9
    x += bpf(rng.standard_normal(n), 700, 5000) * np.exp(-t / 0.035) * 0.35
    for _ in range(3):
        d = B.drip(rng, rng.uniform(900, 1800), rng.uniform(0.15, 0.35)); i = int(rng.uniform(0.12, 0.4) * SR); x[i:i + len(d)] += d[:n - i]
    return fade_end(x)


def turn(rng):
    """そっと 振り向く（服が こすれる・ぬれた 石の 上で 足を ずらす）"""
    sec = 1.0; t = ts(sec); n = len(t)
    e = np.sin(np.pi * np.clip(t / 0.8, 0, 1)) ** 2
    x = bpf(rng.standard_normal(n), 1500, 6000) * e * (0.5 + 0.5 * np.sin(TAU * 7 * t) ** 2) * 0.12
    x += bpf(B.grains(rng, n, 300, e, 3.0), 1000, 5000) * 0.18
    return fade_end(x)


def glass_knock(rng):
    """コン（大きな ガラスを 内がわから たたく）"""
    sec = 1.0; t = ts(sec); n = len(t)
    x = metal(rng, rng.uniform(780, 860), [1.0, 2.73, 4.9, 7.6], [0.28, 0.15, 0.08, 0.05], [1.0, 0.45, 0.25, 0.12], sec, 0.05)
    x += reson(rng.standard_normal(n) * np.exp(-t / 0.006), 240, 4) * np.exp(-t / 0.07) * 3.0
    return fade_end(x * 0.6)


def sand_up(rng):
    """砂が 上に 落ちる（サラサラが 逆に ふえて いく ＋ ふしぎな 上がる 音）"""
    x = B.sand_stream(rng, 2.6, 2200)[::-1].copy() * 1.2; n = len(x); t = np.arange(n) / SR
    f = 1500 * 2 ** (1.4 * t / (n / SR))
    x += np.sin(TAU * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(TAU * 6 * t)) * np.sin(np.pi * t / (n / SR)) ** 2 * 0.05
    return fade_end(x)


def vanish(rng):
    """足跡が 砂に 消えて いく（風で 砂が すべる シャー）"""
    x = B.sand_stream(rng, 2.4, 1400, 1200, 5000) * 0.9; n = len(x); t = np.arange(n) / SR
    return fade_end(x + bpf(rng.standard_normal(n), 600, 3000) * np.sin(np.pi * t / (n / SR)) ** 2 * 0.08)


def sand_boom(rng):
    """ドゴォンッ（砂が 噴き上がる）＋ 砂が 降る ＋ 馬が 飛び出す ゴォッ"""
    sec = 4.0; t = ts(sec); n = len(t)
    x = sat(thump(115, 32, 0.08, 0.55, sec) * 1.0 + lpf(rng.standard_normal(n), 300) * np.exp(-t / 0.12) * 0.9, 2.4) * 0.9
    x += hpf(rng.standard_normal(n), 700) * np.exp(-t / 0.02) * 0.9
    x += bpf(rng.standard_normal(n), 300, 5000) * np.exp(-t / 0.35) * 0.55
    x += bpf(B.grains(rng, n, 1200, np.exp(-np.maximum(0, t - 0.3) / 0.9) * np.clip((t - 0.2) / 0.3, 0, 1), 3.0), 1500, 8000) * 0.5   # 砂が 降る
    wf = tvf(rng.standard_normal(n), 400 + 1800 * np.exp(-((t - 0.55) / 0.15) ** 2), 1.2, 'bp', circ=False) * np.exp(-((t - 0.55) / 0.14) ** 2) * 1.6
    return fade_end(x + wf, 0.5)


def pant(rng, n_br=2, g=1.0):
    """ハァ……ハァ……（息が あがって いる）"""
    out = []
    for k in range(n_br):
        sec = 0.55; t = ts(sec); n = len(t); nz = rng.standard_normal(n)
        e = np.clip(t / 0.06, 0, 1) * np.exp(-np.maximum(0, t - 0.12) / 0.18)
        ex = (reson(nz, 720, 5) * 1.0 + reson(nz, 1220, 6) * 0.7 + reson(nz, 2600, 7) * 0.35 + hpf(nz, 1500) * 0.05) * e * 2.4
        si = 0.32; ti = ts(si); ni = len(ti); nz2 = rng.standard_normal(ni)
        ei = np.sin(np.pi * np.clip(ti / si, 0, 1)) ** 2
        inh = (reson(nz2, 320, 4) * 0.5 + reson(nz2, 2300, 6) * 0.6 + hpf(nz2, 3000) * 0.08) * ei * 1.3
        out += [ex, np.zeros(int(0.06 * SR)), inh, np.zeros(int(0.1 * SR))]
    return fade_end(np.concatenate(out) * g)


def bridge_creak(rng):
    """ギシッ（つり橋の 板と なわが きしむ）"""
    sec = 0.5; t = ts(sec); n = len(t)
    f = 70 + 40 * np.sin(np.pi * t / sec); ph = np.cumsum(f) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    x = reson(p, 640, 10) + reson(p, 1300, 12) * 0.7 + reson(p, 2100, 14) * 0.4
    x = x * np.sin(np.pi * t / sec) ** 1.2 * 3.0 + reson(rng.standard_normal(n) * np.exp(-np.maximum(0, t - 0.38) / 0.004) * (t > 0.38), 420, 4) * 1.5
    return fade_end(x)


def volley(rng):
    """ズドドドォンッ！！（落雷が つづけて）"""
    return mix(*[(B.thunder(rng, True), dt, g) for dt, g in ((0.0, 0.8), (0.13, 0.9), (0.26, 1.0), (0.42, 1.2))])


def ring_ears(rng):
    """キィィン……（大きな 音の あと 耳が 鳴る）"""
    sec = 2.6; t = ts(sec)
    x = (np.sin(TAU * 5200 * t) + 0.7 * np.sin(TAU * 5231 * t)) * np.minimum(1, t / 0.05) * np.exp(-t / 1.1)
    return fade_end(x * 0.09)


def mane_sparks(rng):
    """パチッ ＋ 青い 火花が たてがみを 走る（バチバチ）"""
    sec = 1.6; t = ts(sec); n = len(t)
    e = np.clip(t / 0.1, 0, 1) * np.exp(-np.maximum(0, t - 0.6) / 0.4)
    x = bpf(B.grains(rng, n, 160, e, 2.5), 1800, 9000) * 0.9
    x += np.sign(np.sin(TAU * 118 * t)) * e * 0.025 * (0.5 + 0.5 * np.sin(TAU * 9 * t))
    return fade_end(x)


def cold_gust(rng):
    """ヒュウゥ（つめたい 風）"""
    return gust1(rng, 2.4, (700, 1250, 850), 11.0, 0.35, 0.10)


def breath_out(rng):
    """ふぅ（白い 息）"""
    sec = 0.8; t = ts(sec); nz = rng.standard_normal(len(t))
    e = np.clip(t / 0.08, 0, 1) * np.exp(-np.maximum(0, t - 0.2) / 0.25)
    return fade_end((reson(nz, 900, 3) + reson(nz, 2400, 5) * 0.5 + hpf(nz, 2500) * 0.05) * e * 1.2)


def quake(rng):
    """ズシィンッ（門の 向こうの 大きな 一歩：足もとまで ゆれる）"""
    x = B.footstep(rng, 1.9, 'ice') * 1.2; n = len(x) + int(1.6 * SR); t = np.arange(n) / SR
    y = np.r_[x, np.zeros(n - len(x))]
    y += lpf(rng.standard_normal(n), 110) * np.clip(t / 0.03, 0, 1) * np.exp(-t / 0.9) * 0.6
    y += bpf(B.grains(rng, n, 200, np.exp(-np.maximum(0, t - 0.15) / 0.5) * (t > 0.1), 3.0), 2000, 7000) * 0.35      # 氷の かけらが ふるえる
    return fade_end(y)


def ice_spread(rng, sec=1.0):
    """ピキピキピキッ（足もとから 凍って いく）"""
    n = int((sec + 0.6) * SR); y = np.zeros(n); k = 14
    for j in range(k):
        u = j / (k - 1); tt = sec * (1 - (1 - u) ** 0.55)
        c = metal(rng, rng.uniform(3200, 6800), [1.0, 1.52, 2.43], [0.035, 0.022, 0.014], [1.0, 0.5, 0.3], 0.2, 0.5) * rng.uniform(0.4, 0.9) * (0.6 + 0.6 * u)
        i = int(tt * SR); y[i:i + len(c)] += c[:n - i]
    c = B.crack(rng, 0.7); i = int(sec * SR); y[i:i + len(c)] += c[:n - i] * 1.0                              # さいごの ピキッ
    t = np.arange(n) / SR
    y += hpf(rng.standard_normal(n), 4500) * np.clip(t / sec, 0, 1) ** 2 * np.exp(-np.maximum(0, t - sec) / 0.15) * 0.06
    return fade_end(y)


def anvil_far(rng):
    return lpf(B.anvil(rng, 1.0), 3800)


def scrape(rng):
    """ギリッ（ひづめが 鉄を こする）"""
    sec = 0.9; t = ts(sec); n = len(t)
    f = 150 - 60 * t / sec + 10 * np.sin(TAU * 7 * t); ph = np.cumsum(f) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    p *= 0.5 + 0.5 * rng.random(n)
    x = reson(p, 1850, 25) + reson(p, 2650, 28) * 0.7 + reson(p, 3900, 30) * 0.4
    x = x * 4.0 + bpf(rng.standard_normal(n), 2000, 7000) * 0.05
    return fade_end(x * np.clip(t / 0.08, 0, 1) * np.clip((sec - t) / 0.25, 0, 1))


def big_clang(rng):
    """ガァンッ（鉄床を けった 大きな 音）＋ 火花の 幕を 破る ゴワッ ＋ 火の 粉"""
    sec = 3.0; t = ts(sec); n = len(t)
    x = metal(rng, 390, [1.0, 1.9, 2.75, 3.9, 5.3, 6.8, 8.6, 11.2], [2.2, 1.6, 1.2, 0.9, 0.6, 0.42, 0.28, 0.18], [1.0, 0.8, 0.7, 0.55, 0.42, 0.3, 0.22, 0.15], sec, 0.7)
    x += sat(thump(130, 50, 0.03, 0.2, sec), 1.8) * 0.7
    x += tvf(rng.standard_normal(n), 300 + 2200 * np.exp(-((t - 0.25) / 0.2) ** 2), 0.9, 'bp', circ=False) * np.exp(-((t - 0.3) / 0.25) ** 2) * 1.2
    x += bpf(B.grains(rng, n, 400, np.exp(-t / 0.8), 2.5), 3000, 9500) * 0.45
    return fade_end(x * 0.55, 0.4)


def charge(rng):
    """突進して くる（重い ひづめが 一気に 近づく）"""
    n = int(1.4 * SR); y = np.zeros(n); t = 0.0
    while t < 1.1:
        u = t / 1.1; h = B.footstep(rng, 1.0, 'stone')[:int(0.6 * SR)] * (0.3 + 0.8 * u); i = int(t * SR); L = min(len(h), n - i); y[i:i + L] += h[:L]; t += 0.16
    return fade_end(y * 0.7)


def feather(rng):
    """ふわり（白い 羽が まう）"""
    sec = 1.4; t = ts(sec); n = len(t)
    e = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2
    x = bpf(rng.standard_normal(n), 500, 2600) * e * 0.18
    for _ in range(6):
        i = int(rng.uniform(0.1, 0.9) * SR); tt = t[:n - i]; x[i:] += np.sin(TAU * rng.uniform(4800, 8200) * tt) * np.exp(-tt / 0.25) * 0.03
    return fade_end(x)


def stars(rng):
    """星が すうっと 動く（キラキラが 上へ ながれる ＋ やわらかな 和音）"""
    sec = 2.6; t = ts(sec); n = len(t); x = np.zeros(n)
    for k in range(26):
        t0 = rng.uniform(0, 1.9); f = 3000 * 2 ** (1.3 * t0 / 1.9) * rng.uniform(0.95, 1.05); i = int(t0 * SR); tt = t[:n - i]
        x[i:] += np.sin(TAU * f * tt) * np.exp(-tt / 0.18) * rng.uniform(0.02, 0.05)
    pad_ = sum(np.sin(TAU * f * t) for f in (880.0, 1318.5, 1760.0)) * np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2 * 0.025
    return fade_end(x + pad_)


def cheek_wind(rng):
    """風が 頬を 打つ（ゴッ）"""
    return gust1(rng, 0.9, (400, 900, 500), 2.0, 1.4)


def spin(rng):
    """ギィ……クルクルクルッ（天球儀が ひとりでに 回る）"""
    c = B.creak_wood(rng, 0.9) * 0.6
    n = int(1.8 * SR); y = np.zeros(n); t = 0.0; r = 7.0
    while t < 1.35:
        k = B.clink(rng, rng.uniform(2500, 3600)) * 0.35; i = int(t * SR); y[i:i + len(k)] += k[:n - i]; t += 1 / r; r = min(30.0, r * 1.09)
    tt = np.arange(n) / SR
    y += sum(np.sin(TAU * f * tt) for f in (1210.0, 1530.0)) * np.clip(tt / 0.4, 0, 1) * np.exp(-np.maximum(0, tt - 1.2) / 0.3) * (0.5 + 0.5 * np.sin(TAU * 12 * tt)) * 0.03
    return mix((c, 0.0, 1.0), (fade_end(y), 0.75, 1.0))


def winding(rng):
    """キリ……キリキリキリッ（ねじを 巻く）"""
    def click(g=1.0): return metal(rng, rng.uniform(3400, 3800), [1.0, 1.6, 2.3], [0.025, 0.016, 0.01], [1.0, 0.5, 0.3], 0.12, 0.3) * g
    parts = [(click(0.6), 0.0, 1.0), (click(0.7), 0.16, 1.0)]
    t = 0.75
    for j in range(9): parts.append((click(0.6 + 0.04 * j), t, 1.0)); t += 0.075
    parts.append((click(1.1), t + 0.03, 1.0))
    return mix(*parts) * 0.8


def clicks_ring(rng):
    """カチッ、カチッ、カチン！ ＋ 金の 輪が 一直線に 重なる（キラーン）"""
    def click(): return metal(rng, rng.uniform(2700, 3000), [1.0, 1.6, 2.4], [0.04, 0.025, 0.015], [1.0, 0.55, 0.3], 0.2, 0.35) * 0.8
    ring = metal(rng, 1567.98, [1.0, 2.0, 3.01, 4.2], [1.6, 1.0, 0.6, 0.35], [1.0, 0.45, 0.22, 0.12], 3.0, 0.2) * 0.5
    chord = sum(B.metal(rng, f, [1.0, 2.0], [2.0, 1.2], [1.0, 0.3], 3.0, 0.0) for f in (1046.5, 1318.5, 1568.0)) * 0.12
    return mix((click(), 0.0, 1.0), (click(), 0.36, 1.0), (click(), 0.72, 1.0), (ring, 0.74, 1.0), (chord, 0.95, 1.0))


def steps_light(rng, k=2, gap=0.95, g=1.0):
    """コツ……コツ……（ゆっくり 近づく ひづめ）"""
    return mix(*[(hoof_stone(rng, 0.55 + 0.25 * j), j * gap, g) for j in range(k)])


def crystal_hum(rng):
    """ヴゥゥン……（紫水晶が 低く うなる）"""
    sec = 2.4; t = ts(sec)
    e = np.clip(t / 0.4, 0, 1) * np.exp(-np.maximum(0, t - 1.3) / 0.5)
    x = (np.sin(TAU * 98 * t) + 0.6 * np.sin(TAU * 196.6 * t) + 0.4 * np.sin(TAU * 294 * t) + 0.25 * np.sin(TAU * 392.8 * t)) * (0.7 + 0.3 * np.sin(TAU * 3 * t))
    x = sat(x * 0.6, 1.4) * e * 0.5 + np.sin(TAU * 1176 * t) * e * (0.5 + 0.5 * np.sin(TAU * 5 * t)) * 0.02
    return fade_end(x)


def door_creak(rng):
    """ギィィ……（大きな 扉が ゆっくり 開く）"""
    sec = 1.8; t = ts(sec); n = len(t)
    f = 38 + 22 * np.sin(np.pi * t / sec) + 4 * np.sin(TAU * 2.3 * t); ph = np.cumsum(f) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    x = reson(p, 310, 10) + reson(p, 620, 12) * 0.7 + reson(p, 980, 14) * 0.4 + reson(p, 1560, 16) * 0.2
    return fade_end(sat(x * np.sin(np.pi * t / sec) ** 1.3 * 3.0, 1.2) * 0.8)


def roses(rng):
    """ザワ……ザワザワッ（薔薇が いっせいに ゆれる）"""
    return mix((rustle(rng, 0.7, False, 0.7), 0.0, 1.0), (rustle(rng, 0.5, False, 0.9), 0.85, 1.0), (rustle(rng, 0.6, False, 1.0), 1.1, 1.0), (rustle(rng, 0.45, True, 0.9), 1.35, 1.0))


def feathers_rub(rng):
    """ファサ……（羽が こすれる）"""
    return B.wing_open(rng)[:int(1.2 * SR)] * 0.45


def huge_wings(rng):
    """バサァァッ！！（黒い 大きな 翼が ひらく）＋ 花びらが 舞う"""
    x = mix((B.wing_open(rng), 0.0, 0.7), (B.flap(rng, 2.0), 0.15, 1.5), (cheek_wind(rng), 0.2, 0.6))
    n = len(x); t = np.arange(n) / SR
    pet = bpf(rng.standard_normal(n), 1500, 6000) * np.clip((t - 0.3) / 0.2, 0, 1) * np.exp(-np.maximum(0, t - 0.5) / 0.5) * (0.5 + 0.5 * np.sin(TAU * 11 * t) ** 2) * 0.12
    return x + pet


def card_swish(rng):
    """シャッ（カードを 構える）"""
    sec = 0.35; t = ts(sec); n = len(t)
    x = tvf(rng.standard_normal(n), 2500 + 5000 * np.clip(t / 0.08, 0, 1), 1.0, 'bp', circ=False) * np.clip(t / 0.02, 0, 1) * np.exp(-np.maximum(0, t - 0.05) / 0.05)
    return fade_end(x * 0.9)


# ---------------- エリアの 環境音（出来事は 入れない）----------------
def bed(lv, r, n):
    g = lambda fm, b, k: B.gust(r, n, fm, b, k)
    if lv == 1:
        x = B.wind(r, n, g(0.10, -0.2, 1.0), 220, 850, 0.30, rustle=0.55, rust_lo=2800)
        for t0 in (2.5, 9.5, 17.0, 24.0):
            p = B.bird_phrase(r) * 0.35; i = int(t0 * SR); pl, pr = B.pang(r.uniform(-0.8, 0.8)); L = min(len(p), n - i); x[0, i:i + L] += p[:L] * pl; x[1, i:i + L] += p[:L] * pr
        return x
    if lv == 2: return B.wind(r, n, g(0.16, 0.9, 1.0), 300, 1700, 0.55, howl=((380, 820, 14, 0.5), (950, 1500, 18, 0.25)), rustle=0.18)
    if lv == 3: return B.wind(r, n, g(0.07, -0.5, 0.6), 300, 800, 0.07, rustle=0.9, rust_lo=2200)
    if lv == 4: return B.wind(r, n, g(0.08, -0.6, 1.0), 150, 480, 0.22) + B.stereo(r, lambda q: B.shaped(q, n, 35, 140, -1.0), 0.6) * 0.04
    if lv == 5:
        t = np.arange(n) / SR; sw = 0.6 + 0.4 * (0.5 + 0.5 * B.curve(r, n, 0.08))
        hum = (np.sin(TAU * 58 * t) * 0.6 + np.sin(TAU * 87.5 * t) * 0.4 + 0.25 * np.sin(TAU * 175 * t)) * 0.02
        return B.stereo(r, lambda q: B.shaped(q, n, 30, 150, -1.0), 0.5) * 0.07 + B.stereo(r, lambda q: B.shaped(q, n, 160, 900, -0.5) * sw, 0.3) * 0.07 + np.stack([hum, hum])
    if lv == 6:
        gg = g(0.10, 0.4, 0.9)
        x = B.wind(r, n, gg, 260, 950, 0.40)
        x += B.stereo(r, lambda q: B.shaped(q, n, 1500, 7500, -0.2) * gg ** 1.8 * 0.15, 0.3)
        mo = tvf(B.shaped(r, n, 80, 3000, -0.5), 230 + 110 * gg, 9, 'bp') * gg ** 2 * 0.27
        return x + np.stack([mo, mo * 0.8])
    if lv == 7: return B.wind(r, n, g(0.2, 0.9, 1.0), 250, 1600, 0.55, howl=((300, 700, 12, 0.45), (800, 1300, 16, 0.2)), rustle=0.12)
    if lv == 8:
        ice = B.cf(B.grains(r, n, 1.4, None, 3.0), B.sos_bp(2800, 7500)); ice = reson(np.concatenate([ice, ice]), 4300, 18)[n:] * 1.2
        return (B.stereo(r, lambda q: B.shaped(q, n, 25, 120, -1.0), 0.5) * 0.035 + B.stereo(r, lambda q: B.shaped(q, n, 3000, 10000, 0.0) * (0.6 + 0.4 * (0.5 + 0.5 * B.curve(q, n, 0.1))), 0.2) * 0.05
                + np.stack([ice, np.roll(ice, int(0.3 * SR))]))
    if lv == 9: return B.fire(r, n, 1.0) * 0.75
    if lv == 10:
        gg = g(0.07, -0.4, 1.0)
        return B.wind(r, n, gg, 280, 700, 0.26, howl=((1150, 1550, 25, 0.12),)) + B.stereo(r, lambda q: B.shaped(q, n, 2000, 8000, -0.2) * (0.5 + 0.5 * gg), 0.2) * 0.05
    if lv == 11:
        x = B.stereo(r, lambda q: B.shaped(q, n, 40, 220, -0.8), 0.6) * 0.035
        for k in range(int(n / SR)):
            c = B.clock_tick(r, k % 2 == 1, False) * 0.35; i = int((0.5 + k) * SR)
            if i < n: L = min(len(c), n - i); x[:, i:i + L] += c[:L] * 0.8
        return x
    t = np.arange(n) / SR; sw = 0.65 + 0.35 * np.sin(TAU * t / 32.0 * 2) ** 2
    saw = lambda f: sum(np.sin(TAU * f * h * t + r.uniform(0, TAU)) / h for h in range(1, 9))
    dr = lpf(saw(73.42) + saw(77.78) * 0.8 + saw(36.71) * 0.25, 420) * sw * 0.11
    sh = B.shepard(n, 55.0, 7, 16.0, True, 1800) * 0.55
    x = np.stack([dr + sh, dr * 0.95 + np.roll(sh, int(0.01 * SR))])
    for k in range(int(n / SR / 0.8)):
        h = B.heartbeat(r) * 0.22; i = int(k * 0.8 * SR); L = min(len(h), n - i); x[:, i:i + L] += h[:L]
    return x


ROOM = {1: dict(rt=1.0, pre=0.015, dark=7000), 2: dict(rt=0.8, pre=0.012, dark=6000), 3: dict(rt=1.3, pre=0.02, dark=5500, er=0.4), 4: dict(rt=1.9, pre=0.03, dark=5000, er=0.8),
        5: dict(rt=4.2, pre=0.04, dark=4500, er=1.0), 6: dict(rt=2.4, pre=0.03, dark=5000, er=0.6), 7: dict(rt=2.2, pre=0.05, dark=5500, echoes=((0.42, 0.22), (0.78, 0.12))),
        8: dict(rt=3.6, pre=0.05, dark=8500, er=0.8), 9: dict(rt=1.4, pre=0.02, dark=6000, er=0.6), 10: dict(rt=2.8, pre=0.03, dark=7000), 11: dict(rt=3.0, pre=0.04, dark=5500, er=0.7),
        12: dict(rt=3.4, pre=0.05, dark=5000, er=0.6)}

# セリフの きっかけ：{レベル: [(行, 字の 目じるし, 音を 作る 関数, 何秒 あと, 大きさ, 左右, ひびき)]}
#   目じるしの 字が 出た とき（1字 34ms）＋ 何秒 あと に 鳴る。字は 速く 出るので、つづく 音（ザク、ザク・カン、カン…）は 1つ目の 字に 合わせて、あとは 音の 間で ならべる
CUES = {
    1: [(0, 'チリン♪', lambda r: bell(r), 0.0, 0.55, 0.45, 0.4),
        (1, 'チリンチリンッ', lambda r: jingle(r, 1.1), 0.0, 0.7, 0.3, 0.3),
        (1, 'チリンチリンッ', lambda r: gallop(r, 1.8, 0.3, 1.0), 0.3, 1.0, 0.2, 0.25)],
    2: [(0, 'バタバタバタッ', lambda r: flag_burst(r, 1.4), 0.0, 0.9, 0.35, 0.2),
        (0, 'バタバタバタッ', lambda r: hoof_dirt(r, 1500, 0.25), 2.0, 1.0, -0.6, 0.6),
        (1, 'ビュンッ', lambda r: zoom(r), 0.0, 1.0, -0.8, 0.25)],
    3: [(0, 'ザク', lambda r: step_leaves(r, 0.9), 0.0, 1.0, -0.1, 0.25), (0, 'ザク', lambda r: step_leaves(r, 0.8), 0.5, 1.0, 0.1, 0.25),
        (1, 'ガサ', lambda r: rustle(r, 0.6, False, 0.8), 0.0, 1.0, 0.5, 0.35), (1, 'ガサ', lambda r: rustle(r, 0.5, True, 1.0), 0.9, 1.0, 0.45, 0.35),
        (2, 'ブルルッ', lambda r: snort(r), 0.0, 0.9, 0.3, 0.35), (2, 'ブルルッ', lambda r: rustle(r, 0.7, True, 0.8), 0.9, 1.0, 0.25, 0.3)],
    4: [(0, 'ジャラララ', lambda r: B.chains(r, 2.4, 45.0), 0.0, 1.0, -0.2, 0.35), (0, 'ジャラララ', lambda r: B.ratchet(r, 1.6), 0.4, 0.7, -0.1, 0.35),
        (1, 'ギギギ', lambda r: B.groan(r, 1.6), 0.0, 0.9, 0.0, 0.4), (1, 'ギギギ', lambda r: B.slam(r, 1.0), 1.5, 1.0, 0.0, 0.45),
        (1, 'ギギギ', lambda r: hoof_stone(r, 0.45), 2.7, 1.0, 0.15, 0.6), (1, 'ギギギ', lambda r: hoof_stone(r, 0.6), 3.5, 1.0, 0.1, 0.55),
        (1, 'ギギギ', lambda r: stomp(r, 0.9), 4.3, 1.0, 0.05, 0.5),
        (2, '関守のひと踏み', lambda r: stomp(r, 1.1, 1.5), 0.0, 1.0, 0.0, 0.45), (2, '関守のひと踏み', lambda r: B.chains(r, 1.6, 55.0), 0.25, 0.9, -0.3, 0.4)],
    5: [(0, 'ヒュゥゥ', lambda r: gust1(r, 2.2, (450, 820, 560), 9.0, 0.5), 0.0, 0.7, -0.3, 0.4),
        (0, 'ヒュゥゥ', lambda r: B.drip(r, 1150), 1.1, 0.7, 0.5, 0.85), (0, 'ヒュゥゥ', lambda r: B.drip(r, 980), 2.3, 0.55, -0.4, 0.9),
        (1, 'そっと振り向く', lambda r: turn(r), 0.0, 1.0, 0.0, 0.3),
        (2, 'ちゃぷ', lambda r: B.lap(r, 1.2), 0.0, 0.8, -0.5, 0.5), (2, 'ちゃぷ', lambda r: plop(r), 1.4, 0.8, -0.35, 0.55),
        (2, 'ちゃぷ', lambda r: snort(r), 2.8, 1.0, -0.25, 0.45)],
    6: [(0, 'ヒュオォ', lambda r: gust1(r, 2.4, (240, 420, 300), 8.0, 0.6), 0.0, 0.8, 0.2, 0.4), (0, 'ヒュオォ', lambda r: vanish(r), 1.2, 0.9, -0.3, 0.3),
        (1, 'コン', lambda r: glass_knock(r), 0.0, 0.8, 0.4, 0.75), (1, 'コン', lambda r: glass_knock(r), 0.95, 0.7, 0.4, 0.75),
        (1, 'コン', lambda r: sand_up(r), 2.3, 1.0, 0.35, 0.5),
        (2, 'ドゴォンッ', lambda r: sand_boom(r), 0.0, 1.0, 0.45, 0.35)],
    7: [(0, 'ハァ', lambda r: pant(r, 2, 0.9), 0.0, 1.0, 0.0, 0.15), (0, 'ハァ', lambda r: bridge_creak(r), 2.1, 1.0, 0.1, 0.35),
        (1, 'ズドォン', lambda r: B.thunder(r, True), 0.0, 0.8, -0.5, 0.35), (1, 'ズドォン', lambda r: B.thunder(r, True), 0.55, 0.9, 0.5, 0.35),
        (1, 'ズドォン', lambda r: B.thunder(r, True), 1.15, 0.85, -0.2, 0.35), (1, 'ズドォン', lambda r: volley(r), 1.9, 0.85, 0.1, 0.35),
        (2, 'キィィン', lambda r: ring_ears(r), 0.0, 1.0, 0.0, 0.0), (2, 'キィィン', lambda r: B.spark(r), 1.7, 1.0, 0.3, 0.2),
        (2, 'キィィン', lambda r: mane_sparks(r), 1.9, 1.0, 0.3, 0.3)],
    8: [(0, 'ヒュウゥ', lambda r: cold_gust(r), 0.0, 0.8, -0.2, 0.45), (0, 'ヒュウゥ', lambda r: breath_out(r), 2.0, 0.5, 0.0, 0.2),
        (1, 'ズン', lambda r: lpf(B.footstep(r, 1.4, 'stone'), 900), 0.0, 0.6, 0.2, 0.7), (1, 'ズン', lambda r: lpf(B.footstep(r, 1.45, 'stone'), 1100), 0.75, 0.75, 0.15, 0.65),
        (1, 'ズン', lambda r: quake(r), 1.6, 1.1, 0.1, 0.5),
        (2, '門をくぐる', lambda r: lpf(B.footstep(r, 1.6, 'ice'), 2500), 0.0, 0.8, 0.1, 0.5), (2, '門をくぐる', lambda r: ice_spread(r), 0.7, 1.0, 0.0, 0.5)],
    9: [(0, 'カーン', lambda r: anvil_far(r), 0.0, 0.5, 0.3, 0.8), (0, 'カーン', lambda r: anvil_far(r), 1.25, 0.5, 0.3, 0.8),
        (1, 'カン', lambda r: B.anvil(r, 0.8), 0.0, 0.8, 0.2, 0.4), (1, 'カン', lambda r: B.anvil(r, 0.85), 0.34, 0.8, 0.2, 0.4),
        (1, 'カン', lambda r: B.anvil(r, 0.7), 0.68, 0.8, 0.2, 0.4), (1, 'カン', lambda r: B.anvil(r, 0.75), 0.8, 0.8, 0.2, 0.4), (1, 'カン', lambda r: B.anvil(r, 1.1), 0.92, 0.85, 0.2, 0.4),
        (1, 'カン', lambda r: scrape(r), 2.7, 0.8, -0.2, 0.45),
        (2, 'ガァンッ', lambda r: big_clang(r), 0.0, 1.0, 0.1, 0.4), (2, 'ガァンッ', lambda r: charge(r), 0.8, 1.0, 0.0, 0.35)],
    10: [(0, 'ふわり', lambda r: feather(r), 0.0, 1.0, 0.2, 0.5),
         (1, 'すうっと動く', lambda r: stars(r), -0.3, 1.0, 0.0, 0.6),
         (2, 'ファサ', lambda r: B.wing_open(r)[:int(1.0 * SR)], 0.0, 0.45, -0.2, 0.45), (2, 'ファサ', lambda r: B.flap(r, 1.2), 0.6, 0.9, -0.1, 0.4),
         (2, 'ファサ', lambda r: B.flap(r, 1.6), 1.2, 1.1, 0.0, 0.4), (2, 'ファサ', lambda r: cheek_wind(r), 1.35, 0.7, 0.0, 0.2),
         (2, 'ファサ', lambda r: hoof_stone(r, 1.0, True), 2.2, 1.0, 0.1, 0.5)],
    11: [(0, 'ギィ', lambda r: spin(r), 0.0, 1.0, -0.2, 0.5),
         (1, 'キリ', lambda r: winding(r), 0.0, 1.0, 0.2, 0.45), (1, 'キリ', lambda r: clicks_ring(r), 1.75, 1.0, 0.0, 0.55),
         (2, 'コツ', lambda r: steps_light(r, 2, 0.95), 0.0, 1.0, 0.1, 0.6), (2, 'コツ', lambda r: crystal_hum(r), 1.9, 1.0, 0.0, 0.5),
         (2, 'コツ', lambda r: stomp(r, 1.1, 1.5), 3.5, 1.0, 0.0, 0.45)],
    12: [(0, 'ギィィ', lambda r: door_creak(r), 0.0, 1.0, 0.0, 0.6),
         (1, 'ザワ', lambda r: roses(r), 0.0, 1.0, 0.0, 0.4), (1, 'ザワ', lambda r: feathers_rub(r), 2.3, 1.0, -0.4, 0.55),
         (2, '一瞬', lambda r: huge_wings(r), 0.95, 0.95, 0.0, 0.45), (2, '一瞬', lambda r: hoof_stone(r, 1.0, True), 2.6, 1.0, 0.0, 0.55),
         (3, 'シャッ', lambda r: card_swish(r), 0.0, 1.0, 0.0, 0.15)],
}
QUIET = {12: [(2, '一瞬', 0.0, 0.95)], 9: [(1, 'カン', 1.5, 2.7)]}      # しずまる 所：（行, 目じるし, 何秒 あとから, 何秒 あとまで）下の 音を 小さく
MUFFLE = {7: [(2, 'キィィン', 2.2)]}                                       # 耳が 鳴って 外の 音が こもる 所（秒）


def read_time(text):
    """1行を 読む 時間（字が 出る 時間 ＋ 読む 間）"""
    return max(len(text) * CH + 1.8, len(text) * 0.085 + 0.9)


def at(line_t0, text, mark):
    i = text.find(mark); assert i >= 0, (text, mark)
    return line_t0 + i * CH


def render(lv, data):
    area, enemy, say, en = data[lv - 1]; rng = np.random.default_rng(5000 + lv)
    sfx = cb_sfx.render()
    # 行の 時刻
    t = 0.7; starts = []
    for i, s in enumerate(say):
        starts.append(t); t += read_time(s)
        cue_end = max([at(starts[-1], s, c[1]) + c[3] + 2.0 for c in CUES[lv] if c[0] == i] + [0])
        t = max(t, cue_end)
    end = t + 2.6                                                      # さいごの タップ → 名前 →「タップで バトル開始！」
    N = int((end + 1.0) * SR); dry = np.zeros((2, N + int(8 * SR))); wet = np.zeros_like(dry)
    def put(x, t0, g=1.0, pan=0.0, w=0.3):
        i = max(0, int(t0 * SR)); L = min(len(x), dry.shape[1] - i); pl, pr = B.pang(pan)
        dry[0, i:i + L] += x[:L] * g * pl; dry[1, i:i + L] += x[:L] * g * pr
        wet[0, i:i + L] += x[:L] * g * pl * w; wet[1, i:i + L] += x[:L] * g * pr * w
    for (li, mark, fn, dt, g, pan, w) in CUES[lv]:
        put(fn(rng), at(starts[li], say[li], mark) + dt, g, pan, w)
    for i in range(1, len(say)): put(sfx['tap'] * 0.5, starts[i] - 0.02, 0.6, 0.0, 0.0)      # 次の 行へ タップ
    put(sfx['tap'] * 0.5, end - 2.6, 0.6, 0.0, 0.0)
    e0 = starts[en - 1]; put(sfx['magic'] * 0.5, e0, 1.0, 0.0, 0.1); put(sfx['appear'], e0 + 0.42, 1.0, 0.0, 0.1)      # 敵 出現（アプリの 音）
    ir = B.make_ir(np.random.default_rng(lv * 7), ROOM[lv]['rt'], ROOM[lv].get('pre', 0.02), ROOM[lv].get('dark', 6000), 120, ROOM[lv].get('er', 0.0), ROOM[lv].get('echoes', ()))
    wv = np.stack([signal.fftconvolve(wet[0] + wet[1], ir[0])[:dry.shape[1]], signal.fftconvolve(wet[0] + wet[1], ir[1])[:dry.shape[1]]]) * 0.5
    cues = (dry + wv)[:, :N]
    # 下の 環境音（1回り 32秒：長い ときは くり返す）
    bd = bed(lv, np.random.default_rng(6000 + lv), B.NL)
    bd = np.stack([B.cf(c, B.sos_hp(42, 2)) for c in bd]); bd *= B.PHONE * 10 ** (B.VOL.get(lv, 0.0) / 20) / B.phone_rms(bd)
    bd = np.tile(bd, (1, N // B.NL + 1))[:, :N]
    tt = np.arange(N) / SR; ge = np.clip(tt / 0.8, 0, 1)
    for li, m0, d0, d1 in QUIET.get(lv, []):
        a = at(starts[li], say[li], m0) + d0; b = at(starts[li], say[li], m0) + d1
        ge *= 1 - 0.85 * np.clip((tt - a) / 0.15, 0, 1) * np.clip((b + 0.1 - tt) / 0.1, 0, 1)
    mu = np.zeros(N)
    for li, m0, d in MUFFLE.get(lv, []):
        a = at(starts[li], say[li], m0); mu = np.maximum(mu, np.clip((tt - a) / 0.05, 0, 1) * np.clip((a + d - tt) / 0.8, 0, 1))
    if mu.any():
        bl = np.stack([lpf(c, 350) for c in bd]); bd = bd * (1 - mu) + bl * mu * 0.8
    y = bd * ge * 0.5 + cues
    y = np.stack([B.cf(c, B.sos_hp(38, 2)) for c in y])
    y *= 0.050 / B.phone_rms(y)
    y = B.limit(y)
    fo = int(1.4 * SR); y[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    return y, area, starts, end


def name(lv, area):
    return f'決戦調査_セリフの音_Lv{lv:02d}_{area}_ためし.m4a'


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); data = says()
    lvs = [int(v) for v in sys.argv[2:]] or list(range(1, 13)); allx = []
    for lv in lvs:
        y, area, starts, end = render(lv, data); B.to_m4a(y, os.path.join(out, name(lv, area))); allx.append(y)
        print(f'Lv{lv:02d} {area}：{y.shape[1] / SR:.1f}秒・行の はじめ {[round(s, 1) for s in starts]}・山 {np.abs(y).max():.2f}・スピーカーの 所 {B.phone_rms(y):.4f}', flush=True)
    if len(lvs) == 12:
        gap = np.zeros((2, int(1.5 * SR)))
        B.to_m4a(np.concatenate(sum([[y, gap] for y in allx], [])[:-1], axis=1), os.path.join(out, '決戦調査_セリフの音_12エリア_まとめて聞く_ためし.m4a'))
        print('まとめ：できた')
