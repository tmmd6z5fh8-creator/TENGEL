# 決戦調査の フィールドの BGM（作り直し・ためし：まだ アプリには 入れない）
#   まさちゃん 2026/11/19 12:58「違う！ Lvのセリフの効果音とか背景に合わせて作り直してほしいの！」
#     （10:12 の「敵が現れる前からバトルに入るまでのBGMをエリアごとに作りたい」を、12:29 の セリフの 音〈cb_qfield_say.py〉と フィールドの 絵〈cb_q_fNN.webp〉に 合わせて 作り直す）
#   1つの エリアの BGM は いくつかの「層」（どれも 32秒で 切れ目なく くり返せる）：
#     env ＝ 絵の 場所の 音（たとえば 鉄門：門を ぬける 風・左右の たいまつ・右の 赤い 旗・左の 巻き上げ車の 鎖）。フィールドが 出てから バトルまで ずっと
#     ほかの 層 ＝ セリフの 流れで 入る／止まる 音（たとえば 鍛冶場：炉の 奥で 鉄を 打つ 音は 2行目「カン、カン、カカカンッ！」で 止まる ＝「音が止まった…？」）
#     en ＝ 敵が いる 間の 音（敵が 出た とき から：たとえば 関守の ドン！ドン！ドン！と 門の 鎖が ゆれる 音）。セリフの 音と 同じ 作りの 音を 使う
#   聞いて みる 版：アプリと 同じ 流れ（cb_qfield_say.py と 同じ 時刻：0.7秒で 1行目・読む 時間の あと タップ・敵の 行で アプリの magic・appear）＋
#     さいごの 行の あと「タップで バトル開始！」を 待つ 間（TAIL 秒）も BGM が つづく → タップで バトルへ（BGM は 止まる）
#   ぜんぶ 計算で 作る（録音・よその 音は 使わない）
#   python3 kisekae/cb_qfield_scene.py <出す フォルダ> [Lv ...]        … 聞く 用の m4a（Lv ごと）・まとめて 聞く 1こ（12 ぜんぶの とき）
#   python3 kisekae/cb_qfield_scene.py <出す フォルダ> loops <Lv>       … その レベルの 層（くり返す 形・聞く 版と 同じ 大きさ）を wav で（アプリに 入れる ときの もと）
import os, sys
import numpy as np
from scipy import signal
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import cb_qfield_bgm as B
import cb_qfield_say as S
import cb_sfx
SR, TAU, NL, LOOP = B.SR, B.TAU, B.NL, B.LOOP
ts, lpf, hpf, bpf, reson, tvf, sat, fade_end, thump, metal = B.ts, B.lpf, B.hpf, B.bpf, B.reson, B.tvf, B.sat, B.fade_end, B.thump, B.metal
TAIL = 11.0            # さいごの 行の あと「タップで バトル開始！」を 待つ 間（聞く 版）
BGM_G = 0.5            # BGM の 大きさ（場所の 音 env を スピーカーで 聞こえる 所 PHONE に そろえた うえで）
SAY = 0.049            # セリフの 音の 大きさ（cb_qfield_say の 聞く 版と 同じ）
AREAS = B.AREAS


# ---------------- 道具 ----------------
def qf(f):
    """くり返しで つながる 高さ（1回り LOOP 秒で ちょうど 何回）"""
    return round(f * LOOP) / LOOP


def p2(x, pan):
    l, r = B.pang(pan); return np.stack([x * l, x * r])


def pst(x2, pan):
    """ステレオの 床を 左右に よせる"""
    l, r = B.pang(pan); return np.stack([x2[0] * l, x2[1] * r])


def ring_add(x, ev, i):
    n = x.shape[-1]; i %= n; L = ev.shape[-1]; k = min(L, n - i)
    x[..., i:i + k] += ev[..., :k]
    if L > k: x[..., :L - k] += ev[..., k:L]


def io(x, a=0.5, b=1.0):
    """頭と おしりを ふわっと"""
    n = len(x); t = np.arange(n) / SR; return x * np.minimum(1, t / a) * np.clip((n / SR - t) / b, 0, 1)


def flag2(r, n, g, rate=(4.0, 15.0)):
    """旗・布の バタバタ（cb_qfield_bgm.flag と 同じ 作り：1回りで ちょうど 何回 ゆれる）"""
    rr = rate[0] + (rate[1] - rate[0]) * g ** 1.2
    ph = np.cumsum(rr) / SR; ph *= max(1.0, round(ph[-1])) / ph[-1]
    soft = np.zeros(n); hard = np.zeros(n)
    for i in np.nonzero(np.diff(np.floor(ph)) > 0)[0]:
        j = (i + int(r.normal(0, 0.12) / max(rr[i], 1) * SR)) % n; a = g[i] ** 1.5 * r.uniform(0.55, 1.0)
        if r.random() < 0.16 + 0.2 * g[i]: hard[j] += a * r.uniform(0.8, 1.4)
        else: soft[j] += a
    kt = np.arange(int(0.07 * SR)) / SR
    ks = signal.sosfilt(B.sos_bp(300, 2600), r.standard_normal(len(kt))) * np.exp(-kt / 0.014)
    kh = signal.sosfilt(B.sos_bp(1200, 7000), r.standard_normal(len(kt))) * np.exp(-kt / 0.0045)
    body = B.cf(B.shaped(r, n, 90, 420, -0.3), B.sos_lp(500)) * (0.5 + 0.5 * np.cos(TAU * ph)) ** 2 * g ** 1.4 * 0.22
    return B.ccirc(soft, ks) * 1.1 + B.ccirc(hard, kh) * 1.6 + body


def leaves(r, n, g, lo=2400, k=14.0):
    """葉・草の さらさら（風の 強さ g で）"""
    return B.shaped(r, n, lo, 9000, -0.2) * (0.35 + 0.65 * (0.5 + 0.5 * B.curve(r, n, k))) * g ** 1.5


def pad(r, n, freqs, amps, rate=0.0625, swell=0.5):
    """やわらかな ひびき（くり返しで つながる）"""
    t = np.arange(n) / SR; x = np.zeros(n)
    for k, (f, a) in enumerate(zip(freqs, amps)):
        x += a * np.sin(TAU * qf(f) * t + r.uniform(0, TAU)) * (1 - swell + swell * np.sin(TAU * qf(rate * (1 + 0.5 * k)) * t + k) ** 2)
    return x


def stream_loop(r, n, rate=2600, lo=1800, hi=6500):
    """細い 砂が 落ちつづける（サラサラ：くり返す）"""
    g = B.grains(r, n, rate, None, 6.0)
    x = B.cf(g, B.sos_bp(lo, hi)) * 0.05 + B.cf(B.shaped(r, n, 2500, 8000, 0.0), B.sos_lp(9000)) * 0.012
    return x * (0.85 + 0.15 * (0.5 + 0.5 * B.curve(r, n, 0.7)))


# ---------------- 場所の 音 ----------------
def lark(r, sec=7.0):
    """ヒバリ（空の 高い 所で ずっと さえずる）"""
    out = []; t = 0.0
    while t < sec:
        u = r.random()
        if u < 0.45:
            for _ in range(r.integers(3, 9)):
                d = r.uniform(0.018, 0.04); tt = ts(d); f = r.uniform(3200, 5600) * (1 + r.uniform(-0.25, 0.25) * tt / d)
                out += [np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 1.5, np.zeros(int(r.uniform(0.008, 0.03) * SR))]
        elif u < 0.8:
            d = r.uniform(0.15, 0.35); tt = ts(d); f = r.uniform(2800, 4800) * (1 + 0.08 * np.sin(TAU * r.uniform(28, 45) * tt))
            out.append(np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 1.2)
        else:
            d = r.uniform(0.06, 0.12); tt = ts(d); f = r.uniform(2400, 3200) * 1.6 ** (tt / d)
            out.append(np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * tt / d))
        out.append(np.zeros(int(r.uniform(0.02, 0.09) * SR))); t = sum(len(o) for o in out) / SR
    return io(np.concatenate(out), 0.8, 1.2) * 0.35


def thrush(r):
    """森の 鳥（笛の ような ホー・ピリリ）"""
    z = lambda s: np.zeros(int(s * SR)); out = []
    for _ in range(r.integers(2, 5)):
        d = r.uniform(0.12, 0.35); tt = ts(d); f0 = r.uniform(1800, 3400); f1 = f0 * r.uniform(0.85, 1.25)
        f = f0 * (f1 / f0) ** (tt / d) * (1 + 0.012 * np.sin(TAU * 6 * tt)); ph = TAU * np.cumsum(f) / SR
        out += [(np.sin(ph) + 0.08 * np.sin(2 * ph)) * np.minimum(1, tt / 0.02) * np.clip((d - tt) / 0.05, 0, 1), z(r.uniform(0.04, 0.12))]
    if r.random() < 0.7:
        for _ in range(r.integers(4, 9)):
            tt = ts(0.03); f = r.uniform(4000, 5200) * (1 - 0.15 * tt / 0.03)
            out += [np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.03), z(0.012)]
    return np.concatenate(out) * 0.4


def woodpecker(r):
    """キツツキ（遠くで ココココッ）"""
    k = int(r.integers(12, 20)); rate = r.uniform(14, 19); n = int((k / rate + 0.4) * SR); x = np.zeros(n); f0 = r.uniform(900, 1400)
    for j in range(k):
        tt = ts(0.06); L = len(tt)
        hit = (reson(r.standard_normal(L) * np.exp(-tt / 0.003), f0, 8) * 3 + reson(r.standard_normal(L) * np.exp(-tt / 0.002), f0 * 2.3, 10)) * np.exp(-tt / 0.02)
        i = int(j / rate * SR); x[i:i + L] += hit[:n - i] * (0.6 + 0.4 * np.sin(np.pi * j / k)) * (1 - 0.3 * j / k)
    return fade_end(x * 0.5)


def fly(r, sec=2.4):
    """羽虫が 横切る（ブゥーン）"""
    n = int(sec * SR); t = np.arange(n) / SR
    f = r.uniform(190, 230) * (1 + 0.04 * np.tanh((sec / 2 - t) * 3)) * (1 + 0.02 * np.sin(TAU * 9 * t)); ph = TAU * np.cumsum(f) / SR
    x = sum(np.sin(h * ph) / h for h in range(1, 14))
    return fade_end(bpf(x, 300, 5000) * np.exp(-((t - sec / 2) / (sec / 4)) ** 2) * 0.12)


def kite(r):
    """トンビ（ピーヒョロロ：谷の 上の 空）"""
    def tone(f0, f1, d, vib=0.0, vr=0.0):
        t = ts(d); f = f0 * (f1 / f0) ** (t / d) * (1 + vib * np.sin(TAU * vr * t)); ph = TAU * np.cumsum(f) / SR
        return (np.sin(ph) + 0.05 * np.sin(2 * ph)) * np.minimum(1, t / 0.03) * np.clip((d - t) / 0.05, 0, 1)
    return np.concatenate([tone(2300, 2900, 0.65), np.zeros(int(0.05 * SR)), tone(2600, 1500, 0.22), tone(1500, 1900, 0.12, 0.05, 18),
                           tone(1900, 1400, 0.14, 0.05, 18), tone(1500, 1250, 0.18, 0.04, 16)]) * 0.25


def pebbles(r):
    """コロコロ（岩から 小石が ころがる）"""
    n = int(1.4 * SR); x = np.zeros(n); t = 0.0; k = int(r.integers(4, 8))
    for j in range(k):
        L = int(0.05 * SR); tt = np.arange(L) / SR
        c = bpf(r.standard_normal(L) * np.exp(-tt / 0.002), 1200, 5500) * np.exp(-tt / 0.01) * r.uniform(0.4, 1.0) * (1 - 0.5 * j / k)
        i = int(t * SR); x[i:i + L] += c[:n - i]; t += r.uniform(0.07, 0.2)
    return fade_end(x * 0.8)


def iron_creak(r, sec=1.0, f=(90, 150), modes=(820, 1650, 2480), q=22):
    """キィ…／ギィ…（鉄の 金具・鎖が きしむ）"""
    n = int(sec * SR); t = np.arange(n) / SR
    fr = f[0] + (f[1] - f[0]) * np.sin(np.pi * t / sec) + 8 * np.sin(TAU * 4.3 * t)
    ph = np.cumsum(fr) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0; p *= 0.6 + 0.4 * r.random(n)
    x = sum(reson(p, m * r.uniform(0.98, 1.02), q) * a for m, a in zip(modes, (1.0, 0.6, 0.35)))
    return fade_end(x * np.sin(np.pi * t / sec) ** 1.3 * 2.5)


def chain_sway(r, sec=1.6):
    """鎖が ゆれる（ジャラ… ＋ ギィ…）"""
    x = B.chains(r, sec, 14.0) * 0.6; c = iron_creak(r, sec * 0.8, (60, 110), (700, 1400, 2300), 18) * 0.5
    y = np.zeros(max(len(x), len(c))); y[:len(x)] += x; y[:len(c)] += c
    return y


def torch(r, n):
    """たいまつ（小さな 炎：ボボッ ＋ パチッ）"""
    fl = 0.6 + 0.4 * (0.5 + 0.5 * np.tanh(1.5 * B.curve(r, n, 5.0)))
    roar = B.cf(B.shaped(r, n, 120, 1400, -0.4), B.sos_lp(1600)) * fl * 0.35
    kt = ts(0.02); pk = bpf(r.standard_normal(len(kt)), 1200, 7000) * np.exp(-kt / 0.003)
    return roar + B.ccirc(B.grains(r, n, 5.0, None, 2.0), pk) * 0.14


def armor_shift(r, ice=False):
    """よろいが カチャ（重い 体が 少し 動く）"""
    n = int(0.9 * SR); x = np.zeros(n)
    for _ in range(int(r.integers(3, 6))):
        i = int(r.uniform(0.0, 0.5) * SR)
        c = metal(r, r.uniform(3200, 4200) if ice else r.uniform(2100, 2600), [1.0, 1.5, 2.2], [0.12, 0.08, 0.05], [1.0, 0.5, 0.3], 0.4, 0.3) * r.uniform(0.2, 0.5)
        x[i:i + len(c)] += c[:n - i]
    x += bpf(r.standard_normal(n), 400, 2500) * np.sin(np.pi * np.clip(np.arange(n) / SR / 0.6, 0, 1)) ** 2 * 0.05
    return fade_end(x)


def waterfall(r, n):
    """滝（ずっと ザー：遠い）"""
    return B.cf(B.shaped(r, n, 150, 7000, -0.35) * (0.85 + 0.15 * (0.5 + 0.5 * B.curve(r, n, 3.0))), B.sos_lp(3500))


def shimmer(r):
    """湖霊の 水の きらめき（ぬれた ガラスの ような 音が ふわっと）"""
    sec = 3.0; tt = ts(sec); f0 = float(r.choice([523.25, 587.33, 659.25, 783.99, 880.0]))
    x = sum(np.sin(TAU * f0 * m * tt + r.uniform(0, TAU)) * a for m, a in ((1, 1.0), (2.0, 0.35), (3.01, 0.15)))
    return fade_end(x * np.clip(tt / 0.6, 0, 1) ** 2 * np.exp(-np.maximum(0, tt - 0.8) / 0.9) * (0.75 + 0.25 * np.sin(TAU * 5.5 * tt)) * 0.05)


def swirl(r, sec=2.0):
    """水が うずを まく（ザワ…ちゃぷ）"""
    n = int(sec * SR); t = np.arange(n) / SR
    x = tvf(r.standard_normal(n), 500 + 900 * np.sin(np.pi * t / sec), 3.0, 'bp', circ=False) * np.sin(np.pi * t / sec) ** 2 * 0.35
    for _ in range(5):
        d = B.drip(r, r.uniform(700, 1500), r.uniform(0.1, 0.3)); i = int(r.uniform(0.2, 0.8) * sec * SR); x[i:i + len(d)] += d[:n - i]
    return fade_end(x)


def time_chime(r):
    """時の 鈴（キィン…：金の 馬の 胸の 砂時計）"""
    return metal(r, r.uniform(1480, 1560), [1.0, 2.76, 5.4], [1.4, 0.7, 0.3], [1.0, 0.3, 0.12], 3.0, 0.05) * 0.18


def rain(r, n, g):
    """雨（シャー ＋ 岩に 当たる 粒 ＋ 水たまりの ポツ）"""
    def one(q):
        hiss = B.shaped(q, n, 1500, 12000, -0.2) * (0.5 + 0.5 * g) * 0.5
        kt = ts(0.012); k = bpf(q.standard_normal(len(kt)), 1500, 9000) * np.exp(-kt / 0.002)
        drops = B.ccirc(B.grains(q, n, 160, 0.4 + 0.6 * g, 3.0), k) * 0.35
        kt2 = ts(0.1); k2 = np.sin(TAU * np.cumsum(1300 * (1 + 0.8 * (1 - np.exp(-kt2 / 0.01)))) / SR) * np.exp(-kt2 / 0.02)
        return hiss + drops + B.ccirc(B.grains(q, n, 6, None, 3.0, False), k2) * 0.08
    return B.stereo(r, one, 0.15)


def river(r, n):
    """谷底の 川（低い ゴォー）"""
    return B.stereo(r, lambda q: B.cf(B.shaped(q, n, 60, 900, -0.8), B.sos_lp(700)) * (0.85 + 0.15 * B.curve(q, n, 0.5)), 0.5)


def ehum(r, n):
    """電気の ジジジ（迅雷の まわり）"""
    t = np.arange(n) / SR; f = qf(100.0)
    x = sum(np.sin(TAU * f * h * t + r.uniform(0, TAU)) / h ** 0.8 for h in range(1, 12)) * (0.6 + 0.4 * (0.5 + 0.5 * B.curve(r, n, 4.0)))
    x = B.cf(x, B.sos_bp(150, 3000)); x = x / np.std(x) * 0.05
    kt = ts(0.008); k = hpf(r.standard_normal(len(kt)), 2500) * np.exp(-kt / 0.0015)
    return x + B.ccirc(B.grains(r, n, 25, None, 2.0), k) * 0.12


def ice_groan(r, sec=2.2):
    """氷が きしむ（低い ゴゴ…ッ ＋ さいごに ピシッ）"""
    n = int(sec * SR); t = np.arange(n) / SR
    ph = np.cumsum(18 + 30 * np.sin(np.pi * t / sec) ** 2) / SR; p = np.zeros(n); p[np.nonzero(np.diff(np.floor(ph)) > 0)[0]] = 1.0
    x = sat((reson(p, 160, 6) + reson(p, 340, 9) * 0.6 + reson(p, 700, 12) * 0.3) * 2.5 * np.sin(np.pi * t / sec) ** 1.5, 1.3)
    c = B.crack(r, 0.5); i = int(sec * 0.75 * SR); x[i:i + len(c)] += c[:n - i] * 0.5
    return fade_end(x * 0.6)


def frost_breath(r):
    """フシューッ（大きな 白い 息）"""
    sec = 1.8; tt = ts(sec); n = len(tt); nz = r.standard_normal(n)
    e = np.clip(tt / 0.15, 0, 1) * np.exp(-np.maximum(0, tt - 0.4) / 0.45)
    x = (reson(nz, 420, 3) * 0.8 + reson(nz, 1100, 4) * 0.6 + reson(nz, 2600, 5) * 0.35 + hpf(nz, 3000) * 0.06) * e * 1.6
    return fade_end(x + lpf(r.standard_normal(n), 250) * e * 0.5)


def bellows(r, sec=4.6):
    """ふいご（スゥー… ボフゥー：吸って はく）＋ 木と 革が きしむ"""
    n = int(sec * SR); t = np.arange(n) / SR
    inh = np.clip(t / 1.6, 0, 1) * np.clip((2.0 - t) / 0.3, 0, 1); exh = np.clip((t - 2.3) / 0.15, 0, 1) * np.exp(-np.maximum(0, t - 2.5) / 0.55)
    x = bpf(r.standard_normal(n), 300, 2500) * inh * 0.18 + lpf(r.standard_normal(n), 900) * exh * 0.9 + bpf(r.standard_normal(n), 500, 3000) * exh * 0.25
    c = B.creak_wood(r, 1.0) * 0.12; x[:len(c)] += c[:n]
    c2 = B.creak_wood(r, 0.8) * 0.1; i = int(2.2 * SR); x[i:i + len(c2)] += c2[:n - i]
    return fade_end(x)


def bubble(r):
    """ゴポッ（とけた 鉄の 重い あわ）"""
    tt = ts(0.5); f = r.uniform(110, 220) * (1 + 0.8 * (1 - np.exp(-tt / 0.03)))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt / 0.06) * np.minimum(1, tt / 0.004) + bpf(r.standard_normal(len(tt)), 300, 2000) * np.exp(-tt / 0.02) * 0.25
    return fade_end(sat(x, 1.3) * 0.6)


def steam(r, sec=1.6):
    """シュー（管から 湯気）"""
    n = int(sec * SR); t = np.arange(n) / SR; e = np.clip(t / 0.05, 0, 1) * np.exp(-np.maximum(0, t - 0.2) / 0.5)
    return fade_end(hpf(r.standard_normal(n), 2500) * e * 0.35 + bpf(r.standard_normal(n), 900, 3000) * e * 0.1)


def hoof_metal(r, g=1.0):
    """カン！（鉄の ひづめで 鉄を たたく：遠くの 鍛冶より 低く 重い）"""
    x = metal(r, r.uniform(820, 900), [1.0, 1.52, 2.43, 3.38, 4.69, 6.12], [0.7, 0.5, 0.36, 0.26, 0.18, 0.12], [1.0, 0.6, 0.5, 0.38, 0.25, 0.15], 1.8, 0.5)
    t = ts(1.8); x += sat(thump(160, 70, 0.02, 0.08, 1.8) * 0.9 + lpf(r.standard_normal(len(t)), 500) * np.exp(-t / 0.02) * 0.6, 1.6) * 0.8
    return x * g


def sparks(r, sec=0.8):
    """火花が パチパチ"""
    n = int(sec * SR); t = np.arange(n) / SR
    return fade_end(bpf(B.grains(r, n, 220, np.exp(-t / 0.25), 2.5), 2500, 9500) * 0.5)


def fire_snort(r):
    """ブルッ ＋ 鼻から 火が ボワッ"""
    x = S.snort(r, 0.8) * 0.8; n = len(x) + int(0.6 * SR); y = np.zeros(n); y[:len(x)] += x; t = np.arange(n) / SR
    y += tvf(r.standard_normal(n), 300 + 1500 * np.exp(-((t - 0.25) / 0.25) ** 2), 0.8, 'bp', circ=False) * np.exp(-((t - 0.3) / 0.3) ** 2) * 0.9
    return fade_end(y)


def twinkle(r):
    """星が キラッ"""
    f = r.uniform(2600, 7000); tt = ts(1.6)
    x = np.sin(TAU * f * tt) * np.minimum(1, tt / 0.01) * np.exp(-tt / r.uniform(0.25, 0.6)) + np.sin(TAU * f * 2.01 * tt) * np.exp(-tt / 0.12) * 0.25
    return fade_end(x * 0.05)


def gear_ticks(r, n, rate=6.0, f=(2600, 3400), g=(0.2, 0.45)):
    """歯車の 小さな カラカラ（くり返す）"""
    rate = qf(rate); x = np.zeros(n)
    for j in range(int(round(rate * LOOP))):
        ring_add(x, B.clink(r, r.uniform(*f)) * r.uniform(*g), int((j / rate + r.normal(0, 0.004)) * SR))
    return x


def crystal_loop(r, n):
    """紫水晶が 低く うなる ヴゥゥン（ずっと：セリフの ヴゥゥン と 同じ 高さ）"""
    t = np.arange(n) / SR; f = qf(98.0)
    x = (np.sin(TAU * f * t) + 0.6 * np.sin(TAU * 2 * f * t) + 0.4 * np.sin(TAU * 3 * f * t) + 0.25 * np.sin(TAU * 4 * f * t)) * (0.7 + 0.3 * np.sin(TAU * qf(3.0) * t))
    sw = 0.75 + 0.25 * np.sin(TAU * qf(0.125) * t) ** 2
    return sat(x * 0.6, 1.4) * 0.5 * sw + np.sin(TAU * qf(1176) * t) * (0.5 + 0.5 * np.sin(TAU * qf(5) * t)) * 0.02


def saws(r, n, freqs, amps, cut):
    """低い うなり（のこぎり波：くり返しで つながる）"""
    t = np.arange(n) / SR; x = np.zeros(n)
    for f, a in zip(freqs, amps):
        x += a * sum(np.sin(TAU * qf(f) * h * t + r.uniform(0, TAU)) / h for h in range(1, 9))
    return B.cf(x, B.sos_lp(cut))


def hoof_leaves(r, g=1.0):
    """落ち葉の 上の 重い ひづめ（ザフッ）"""
    sec = 0.7; tt = ts(sec); n = len(tt)
    x = sat(thump(150, 70, 0.02, 0.07, sec) * 0.9 + lpf(r.standard_normal(n), 300) * np.exp(-tt / 0.03) * 0.5, 1.5)
    s = S.step_leaves(r, 0.8); x[:len(s)] += s[:n]
    return fade_end(x * g)


def gravel_step(r, g=1.0):
    """砂利を ける ひづめ（ザッ）"""
    h = S.hoof_dirt(r, 3500, 1.0); n = len(h) + int(0.3 * SR); x = np.zeros(n); x[:len(h)] += h
    x += bpf(B.grains(r, n, 900, np.exp(-np.arange(n) / SR / 0.06), 3.0), 1500, 7000) * 0.25
    return fade_end(x * g)


# ---------------- 12 エリア（絵 ＋ セリフ に 合わせた 層）----------------
#   stems：(名前, 作る 関数, はじまり, おわり, ふわっと 入る 秒, ふわっと 消える 秒, 大きさ)
#     はじまり／おわり：None（はじめ から／おわり まで）・'en'（敵が 出る とき）・(行, 目じるしの 字, 何秒 あと)
#     大きさ：('max'｜'med', dB) ＝ 0.1秒 ごとの 大きさの いちばん 大きい 所｜まん中 を、場所の 音（env）の まん中 より 何 dB に するか
#   quiet：(行, 目じるし, 何秒 あと から, まで, どれだけ 小さく, 層〈None＝ぜんぶ〉)  muffle：(行, 目じるし, 秒)
#   drop：鳴らさない セリフの 音（BGM の 層が 同じ 音を 鳴らす）・pan：セリフの 音の 左右（絵の 場所に 合わせる）
def lv1():
    def env(m):      # 若草の原：夕焼けの 草原・右に 大きな 木・左に 木の 柵・空の 高い 所の ヒバリ・近くの 小鳥・遠くの うぐいす
        r = m.rng; g = B.gust(r, NL, 0.10, -0.3, 1.0)
        m.bed(B.wind(r, NL, g, 220, 800, 0.26, rustle=0.45, rust_lo=2800), wet=0.12)
        m.bed(p2(leaves(r, NL, g, 2600), 0.6), 0.10, wet=0.2)
        for t0, p in ((2.6, -0.3), (17.2, 0.25)): m.ev(lpf(lark(r, 7.5), 6500), t0, p, 0.45, 0.6)
        for t0 in (6.6, 10.4, 13.9, 21.8, 25.6, 29.2):
            d = r.uniform(0.35, 0.9); m.ev(B.bird_phrase(r), t0 + r.uniform(-0.25, 0.25), r.uniform(-0.8, 0.8), 0.75 * d, 0.2 + 0.4 * (1 - d))
        m.ev(B.uguisu(r), 12.0, 0.65, 0.38, 0.6)
    def en(m):       # 鈴駒（子馬）が いる：ときどき 鈴が チリン・草を ける・ブルッ
        r = m.rng
        for t0, p in ((3.8, 0.35), (9.4, 0.45), (16.0, 0.3), (22.6, 0.4), (28.5, 0.35)):
            m.ev(S.bell(r, ((0.0, 0.5), (0.07, 0.9)) if r.random() < 0.5 else ((0.0, 0.9),)), t0, p, 0.42, 0.35)
        for t0 in (6.1, 6.45, 19.2, 19.5, 19.8): m.ev(S.hoof_dirt(r, 2400, 0.35), t0, 0.35, 1.0, 0.3)
        m.ev(S.snort(r, 0.6) * 0.5, 12.6, 0.35, 0.45, 0.3)
    return dict(room=S.ROOM[1], vol=-2.0, stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 10.0))])


def lv2():
    def env(m):      # 風見峠：強い 風・左上の 風見と 2本の 吹き流し・右の すすき・谷の 上の トンビ・岩の 小石
        r = m.rng; g = B.gust(r, NL, 0.16, 0.8, 1.0)
        m.bed(B.wind(r, NL, g, 300, 1700, 0.50, howl=((380, 820, 14, 0.45), (950, 1500, 18, 0.22))), wet=0.12)
        f1 = flag2(r, NL, np.roll(g, int(0.2 * SR))); f2 = flag2(r, NL, np.roll(g, int(0.5 * SR)))
        m.bed(p2(f1, -0.45) + p2(f2, -0.6) * 0.7, 0.75, wet=0.2)
        m.bed(p2(leaves(r, NL, g, 1800, 9.0), 0.6), 0.14, wet=0.1)
        for t0 in (3.4, 12.3, 20.4, 27.7): m.ev(iron_creak(r, r.uniform(0.5, 0.9), (110, 190), (1400, 2600, 3900), 25), t0, -0.5, 0.6 * (0.4 + g[int(t0 * SR)]), 0.3)
        m.ev(kite(r), 9.2, 0.35, 1.0, 0.6)
        for t0 in (15.5, 24.9): m.ev(pebbles(r), t0, -0.55, 1.0, 0.3)
    def en(m):       # 疾風：砂利を ける・すばやく 横へ 動く・鼻を 鳴らす
        r = m.rng
        for t0, p in ((3.6, 0.3), (3.9, 0.3), (12.4, -0.2), (12.7, -0.25), (20.2, 0.4), (26.8, 0.1), (27.1, 0.1)): m.ev(gravel_step(r, 0.8), t0, p, 1.0, 0.25)
        m.ev(S.zoom(r) * 0.45, 8.0, 0.6, 1.0, 0.25, pan2=-0.4)
        m.ev(S.snort(r, 0.7) * 0.6, 16.0, 0.2, 0.7, 0.3)
        m.ev(S.zoom(r) * 0.4, 23.0, -0.5, 1.0, 0.25, pan2=0.5)
    return dict(room=S.ROOM[2], vol=0.0, pan={0: -0.45}, stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 10.0))])


def lv3():
    def env(m):      # 茨の森：大きな 古い 木（右）・木もれ日・弱い 風で 高い 枝葉が さわさわ・遠くで 枝が 折れる・羽虫
        r = m.rng; g = B.gust(r, NL, 0.07, -0.2, 0.5)
        m.bed(B.wind(r, NL, g, 250, 700, 0.06, rustle=1.0, rust_lo=2400), wet=0.25)
        m.bed(B.stereo(r, lambda q: leaves(q, NL, g, 1200, 10.0), 0.3), 0.05, wet=0.3)
        for t0, sz, p, gg in ((8.7, 0.7, -0.7, 0.5), (19.7, 1.4, 0.55, 0.6), (27.2, 0.6, -0.3, 0.4)): m.ev(lpf(B.crack(r, sz), 5000), t0, p, gg, 0.6)
        m.ev(B.creak_wood(r, 2.0), 12.6, 0.65, 0.15, 0.6); m.ev(B.creak_wood(r, 1.4), 25.0, 0.6, 0.11, 0.6)
        m.ev(fly(r), 15.2, -0.6, 0.25, 0.2, pan2=0.4)
    def birds(m):    # 森の 鳥（2行目「ガサ……」で しずまる）
        r = m.rng
        for t0, p in ((1.6, -0.5), (10.8, 0.4), (22.0, -0.2)): m.ev(thrush(r), t0, p, 0.5, 0.65)
        for t0 in (5.3, 16.4, 29.0): m.ev(B.bird_phrase(r), t0, r.uniform(-0.7, 0.7), 0.35, 0.5)
        m.ev(woodpecker(r), 8.2, -0.65, 0.5, 0.6); m.ev(woodpecker(r), 24.6, 0.7, 0.35, 0.7)
    def en(m):       # 茨鎧の森番：茨の よろいが ガサッ・落ち葉を ふむ・ブルルッ
        r = m.rng
        for t0, p in ((4.0, 0.35), (12.6, 0.4), (21.0, 0.3), (28.2, 0.35)): m.ev(S.rustle(r, 0.6, True, 0.6), t0, p, 1.0, 0.3)
        for t0 in (7.2, 7.75, 24.2, 24.8): m.ev(hoof_leaves(r, 0.85), t0, 0.35, 1.0, 0.25)
        m.ev(S.snort(r) * 0.6, 16.6, 0.35, 0.8, 0.3)
    return dict(room=S.ROOM[3], vol=-1.5, stems=[('env', env, None, None, 0.8, 0.0, None), ('birds', birds, None, (1, 'ガサ', 0.0), 0.8, 0.6, ('max', 6.0)), ('en', en, 'en', None, 1.0, 0.0, ('max', 13.0))])


def lv4():
    def env(m):      # 鉄門の関所：門の アーチを ぬける 風・左右の たいまつ・右の 赤い 旗・左の 巻き上げ車の 鎖・遠くで 鉄が ゴトン
        r = m.rng; g = B.gust(r, NL, 0.09, -0.3, 1.0)
        m.bed(B.wind(r, NL, g, 160, 520, 0.20, howl=((300, 460, 10, 0.25),)), wet=0.15)
        m.bed(B.stereo(r, lambda q: B.shaped(q, NL, 35, 140, -1.0), 0.6), 0.035)
        m.bed(p2(torch(r, NL), -0.5) + p2(torch(r, NL), 0.5), 0.4, wet=0.2)
        m.bed(p2(B.cf(flag2(r, NL, np.roll(g, int(0.4 * SR)), (1.4, 4.0)), B.sos_lp(2600)), 0.55), 0.45, wet=0.25)
        for t0 in (5.6, 14.1, 23.6): m.ev(chain_sway(r, 1.6), t0, -0.6, 1.2, 0.4)
        m.ev(lpf(B.slam(r, 0.3, 1.2), 1800), 29.4, 0.0, 0.8, 0.8)
    def en(m):       # 鉄門の関守：よろいの 重い 足音 ドン！ドン！ドン！ → 門の 鎖が ゆれる・よろいが カチャ・鼻息
        r = m.rng
        for grp, (gg, p) in zip(((4.6, 5.35, 6.1), (18.0, 18.75, 19.5)), ((0.85, 0.15), (1.0, 0.25))):
            for t0 in grp: m.ev(B.footstep(r, 1.15, 'stone', True), t0, p, gg, 0.4)
            m.ev(B.chains(r, 1.4, 50.0), grp[-1] + 0.25, -0.55, 0.7, 0.4)
        for t0 in (10.6, 25.2): m.ev(armor_shift(r), t0, 0.2, 0.6, 0.3)
        m.ev(S.snort(r) * 0.5, 12.2, 0.2, 0.7, 0.35)
    return dict(room=S.ROOM[4], vol=0.0, pan={0: -0.55, 1: -0.5, 8: -0.55}, stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 12.0))])


def lv5():
    def env(m):      # 霧鏡の湖：霧・右の 滝（遠い）・左の 葦・岸に よせる 水・霧の 奥の しずく・ふしぎな ひびき（ほら穴の ような）
        r = m.rng; n = NL; g = B.gust(r, n, 0.06, -0.3, 1.0)
        m.bed(p2(waterfall(r, n), 0.65), 0.05, wet=0.5)
        m.bed(B.wind(r, n, g, 300, 700, 0.05, howl=((450, 800, 9, 0.6),)), wet=0.6)
        m.bed(p2(leaves(r, n, g, 1500, 8.0), -0.6), 0.05, wet=0.3)
        pd = pad(r, n, (110.0, 164.81, 261.63, 246.94), (1.0, 0.6, 0.35, 0.2), 0.0625, 0.6); m.bed(np.stack([pd, np.roll(pd, int(0.011 * SR))]), 0.010, wet=0.6)
        for t0 in (11.6, 15.6, 20.0, 24.0, 28.3): m.ev(B.lap(r, r.uniform(1.1, 1.7)), t0, -0.45, 0.35, 0.5)
        for t0 in (12.9, 17.2, 20.6, 23.4, 29.8): m.ev(B.drip(r), t0, r.uniform(-0.8, 0.8), 0.35, 0.9)
    def en(m):       # 霧鏡の湖霊：水の きらめき・うずを まく 水・ちゃぷ・低い ふしぎな うなり・鼻息
        r = m.rng; n = NL
        lo = pad(r, n, (55.0, 82.41), (1.0, 0.6), 0.125, 0.5); m.bed(np.stack([lo, lo]), 0.02, wet=0.3)
        for t0, p in ((5.5, 0.4), (12.0, -0.2), (19.5, 0.6), (26.0, 0.1)): m.ev(shimmer(r), t0, p, 0.9, 0.7)
        for t0 in (8.5, 22.5): m.ev(swirl(r), t0, 0.35, 0.8, 0.5)
        for t0 in (15.0, 29.0): m.ev(B.lap(r, 0.9), t0, 0.4, 0.5, 0.45)
        m.ev(S.snort(r) * 0.4, 17.0, 0.35, 0.6, 0.45)
    return dict(room=S.ROOM[5], vol=-3.0, quiet=[(1, 'そっと振り向く', 0.1, 2.6, 0.5, None)],
                stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.5, 0.0, ('max', 10.0))])


def lv6():
    def env(m):      # 刻砂の王墓：入口から 風が ヒュオォ・床の 砂が 舞う・左の 石だなから 砂が 落ちる
        r = m.rng; n = NL; g = B.gust(r, n, 0.10, 0.2, 0.9)
        m.bed(B.wind(r, n, g, 240, 900, 0.32), wet=0.2)
        m.bed(B.stereo(r, lambda q: B.shaped(q, n, 1500, 7500, -0.2) * g ** 1.8 * 0.15, 0.3), 1.0, wet=0.1)
        mo = tvf(B.shaped(r, n, 80, 3000, -0.5), 230 + 110 * g, 9, 'bp') * g ** 2 * 0.25; m.bed(np.stack([mo, mo * 0.8]), 1.0, wet=0.6)
        for t0, sec, p in ((15.6, 3.5, -0.55), (21.0, 2.6, -0.4)): m.ev(B.sand_stream(r, sec, 1800), t0, p, 1.8, 0.4)
        m.ev(B.sand_stream(r, 1.6, 7000, 900, 6000), 27.2, -0.6, 1.6, 0.45)
    def fall(m):     # 右の 大砂時計：砂が 落ちつづける サラサラ（2行目「コン……」の あと 止まる）
        m.bed(p2(stream_loop(m.rng, NL), 0.6), 1.0, wet=0.35)
    def rise(m):     # 砂が 上に 落ちる（逆の サラサラ ＋ どこまでも 上がる きらめき）
        r = m.rng; s = stream_loop(r, NL, 2200, 2000, 7000)
        sh = B.cf(B.shepard(NL, 440.0, 5, 8.0, True, 7000), B.sos_hp(1500))
        m.bed(p2(s + sh * 0.025, 0.6), 1.0, wet=0.45)
    def en(m):       # 刻砂の時守：時の 鈴・金の ひづめ（砂の 上の 石）・体から 砂が こぼれる・ブルル
        r = m.rng
        for t0, p in ((6.0, 0.45), (20.5, 0.35)): m.ev(time_chime(r), t0, p, 1.0, 0.6)
        for t0 in (9.5, 10.3, 24.0, 24.8): m.ev(S.hoof_stone(r, 0.5), t0, 0.4, 1.0, 0.5)
        m.ev(B.sand_stream(r, 1.8, 3500, 1500, 6500), 13.5, 0.4, 0.9, 0.4)
        m.ev(S.snort(r) * 0.5, 16.5, 0.4, 0.7, 0.4)
    return dict(room=S.ROOM[6], vol=0.0, pan={2: 0.6, 3: 0.6, 4: 0.55},
                stems=[('env', env, None, None, 0.8, 0.0, None), ('fall', fall, None, (1, 'コン', 2.3), 0.8, 1.2, ('med', -4.0)), ('rise', rise, (1, 'コン', 2.3), None, 1.5, 0.0, ('med', -4.0)),
                       ('en', en, 'en', None, 1.0, 0.0, ('max', 11.0))])


def lv7():
    def env(m):      # 雷鳴峡：あらしの 谷・強い 風・雨・谷底の 川・左上の 雷雲の 遠い ゴロゴロ・吊り橋が 風で ギシッ
        r = m.rng; n = NL; g = B.gust(r, n, 0.2, 0.9, 1.0)
        m.bed(B.wind(r, n, g, 250, 1600, 0.50, howl=((300, 700, 12, 0.42), (800, 1300, 16, 0.18))), wet=0.12)
        m.bed(rain(r, n, g), 0.10, wet=0.15)
        m.bed(river(r, n), 0.05, wet=0.3)
        for t0, p in ((9.6, -0.6), (26.2, -0.35)): m.ev(B.thunder(r, False), t0, p, 1.2, 0.5)
        for t0 in (4.1, 15.6, 21.3): m.ev(S.bridge_creak(r), t0, 0.1, 0.9 * (0.4 + g[int(t0 * SR)]), 0.35)
    def en(m):       # 雷鳴峡の迅雷：電気の ジジジ・パチッ・瞬間移動 シュン！・近くに 落雷
        r = m.rng; n = NL
        m.bed(p2(ehum(r, n), 0.3), 0.5, wet=0.1)
        m.ev(B.teleport(r), 5.2, -0.7, 0.75, 0.3, pan2=0.6); m.ev(B.spark(r), 5.8, 0.6, 0.6, 0.2)
        m.ev(B.thunder(r, True), 11.2, -0.4, 0.75, 0.35)
        m.ev(B.teleport(r), 17.6, 0.7, 0.75, 0.3, pan2=-0.3); m.ev(S.mane_sparks(r), 18.3, -0.3, 0.8, 0.3)
        for t0 in (8.3, 14.4, 22.6, 28.0): m.ev(B.spark(r), t0, r.uniform(0.1, 0.5), 0.45, 0.2)
        m.ev(B.thunder(r, False), 24.2, 0.5, 0.6, 0.5)
    return dict(room=S.ROOM[7], vol=0.0, muffle=[(2, 'キィィン', 2.2)], stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 12.0))])


def lv8():
    def env(m):      # 氷晶砦：氷の 砦の 前の 氷原・つめたい 風が ヒュウゥ・こまかい 雪・氷の かけらが チリッ・遠くで 氷が きしむ・門の 奥の 低い うなり
        r = m.rng; n = NL; g = B.gust(r, n, 0.08, -0.3, 1.0)
        m.bed(B.wind(r, n, g, 400, 900, 0.05, howl=((700, 1250, 11, 0.5),)), wet=0.45)
        m.bed(B.stereo(r, lambda q: B.shaped(q, n, 3000, 11000, 0.0) * (0.4 + 0.6 * g), 0.2), 0.05, wet=0.3)
        m.bed(B.stereo(r, lambda q: B.shaped(q, n, 25, 120, -1.0), 0.5), 0.03)
        ice = B.cf(B.grains(r, n, 1.4, None, 3.0), B.sos_bp(2800, 7500)); ice = reson(np.concatenate([ice, ice]), 4300, 18)[n:] * 1.2
        m.bed(np.stack([ice, np.roll(ice, int(0.3 * SR))]), 0.6, wet=0.8)
        for t0, p in ((8.2, -0.5), (21.6, 0.4)): m.ev(ice_groan(r), t0, p, 0.35, 0.6)
    def en(m):       # 氷晶砦の守将：とても 大きな 足音 ドシン！ドシン！ドシン！（氷を ふむ）・白い 息・氷の よろい
        r = m.rng
        for grp, (gg, p) in zip(((5.0, 6.2, 7.4), (19.2, 20.4, 21.6)), ((0.9, 0.2), (1.05, 0.1))):
            for t0 in grp: m.ev(B.footstep(r, 1.6, 'ice'), t0, p, gg, 0.45)
        for t0 in (12.2, 26.6): m.ev(frost_breath(r), t0, 0.2, 0.6, 0.35)
        for t0 in (14.6, 29.2): m.ev(armor_shift(r, True), t0, 0.2, 0.5, 0.4)
    return dict(room=S.ROOM[8], vol=-3.0, stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 17.0))])


def lv9():
    def env(m):      # 紅蓮の鍛冶場：左の 炉が ゴォー（ふいごの あと ゴワッ）・右の 大きな ふいご・とけた 鉄が ゴポッ・管から シュー・ふいごの 鎖
        r = m.rng; n = NL; t = np.arange(n) / SR; tb = (1.0, 9.0, 17.0, 25.0)
        fl = 1.0 + 0.5 * sum(np.exp(-((t - b - 2.4) % LOOP) / 1.3) * np.minimum(1, ((t - b - 2.2) % LOOP) / 0.3) for b in tb)
        m.bed(pst(B.fire(r, n, 1.0), -0.45) * fl, 0.7, wet=0.15)
        for b in tb: m.ev(bellows(r), b, 0.55, 0.9, 0.3)
        for t0 in (3.3, 8.3, 12.1, 19.4, 22.8, 29.6): m.ev(bubble(r), t0, 0.45, 0.8, 0.3)
        m.ev(steam(r), 13.6, 0.7, 0.7, 0.3); m.ev(chain_sway(r, 1.2), 20.6, 0.5, 0.6, 0.4)
    def ham(m):      # 炉の 奥で 鉄を 打つ カーン……カーン……（1行目 ＝ この 音。2行目「カン、カン、カカカンッ！」で 止まる）
        r = m.rng
        for k in range(24): m.ev(lpf(B.anvil(r, 1.0), 3200), 0.7 + k * LOOP / 24, 0.3, 0.42, 0.75)
    def en(m):       # 紅蓮の鉄槌：鉄の ひづめで カン！カン！カン！・火花・ひづめが 鉄を こする ギリッ・火を はく ブルッ
        r = m.rng
        for grp, (gg, p) in zip(((5.0, 5.42, 5.84), (18.2, 18.62, 19.04)), ((0.75, 0.1), (0.9, 0.2))):
            for k, t0 in enumerate(grp): m.ev(hoof_metal(r, (0.85, 0.9, 1.1)[k]), t0, p, gg, 0.35)
            m.ev(sparks(r), grp[-1] + 0.05, p, 0.8, 0.3)
        m.ev(S.scrape(r), 11.6, -0.1, 1.5, 0.45)
        for t0 in (9.0, 24.2): m.ev(fire_snort(r), t0, 0.15, 0.7, 0.3)
    return dict(room=S.ROOM[9], vol=0.0, drop={0, 1}, quiet=[(1, 'カン', 1.5, 2.7, 0.6, None)],
                stems=[('env', env, None, None, 0.8, 0.0, None), ('ham', ham, None, (1, 'カン', 0.0), 0.6, 0.35, ('max', 7.0)), ('en', en, 'en', None, 1.0, 0.0, ('max', 13.0))])


def lv10():
    def env(m):      # 星月の回廊：夜空の 上の 回廊・しずかな 高い 空の 風・下の 雲海・星が キラッ・やわらかな ひびき
        r = m.rng; n = NL; g = B.gust(r, n, 0.06, -0.4, 1.0)
        m.bed(B.wind(r, n, g, 280, 650, 0.20, howl=((1150, 1550, 25, 0.10),)), wet=0.35)
        m.bed(B.stereo(r, lambda q: B.cf(B.shaped(q, n, 60, 400, -0.8), B.sos_lp(380)), 0.5), 0.03, wet=0.2)
        pd = pad(r, n, (220.0, 329.63, 440.0, 659.26), (1.0, 0.7, 0.5, 0.25), 0.0625, 0.5); m.bed(np.stack([pd, np.roll(pd, int(0.013 * SR))]), 0.012, wet=0.6)
        for t0 in np.sort(r.uniform(0, LOOP, 10)): m.ev(twinkle(r), t0, r.uniform(-0.9, 0.9), 1.0, 0.7)
    def en(m):       # 星月の天馬：大きな 羽 バァサ！バァサ！バァサ！・羽の 風・青い 石床に カツン・羽が ふわり
        r = m.rng
        for grp, (gg, p0, p1) in zip(((5.0, 5.85, 6.7), (18.6, 19.45, 20.3)), ((0.8, 0.2, 0.5), (0.95, 0.5, 0.1))):
            for k, t0 in enumerate(grp): m.ev(B.flap(r, 1.3), t0, p0 + (p1 - p0) * k / 2, gg, 0.45)
            m.ev(S.cheek_wind(r) * 0.5, grp[-1] + 0.2, 0.3, 0.6, 0.2)
        for t0 in (11.6, 25.6): m.ev(S.hoof_stone(r, 0.7), t0, 0.35, 1.0, 0.55)
        m.ev(S.feather(r), 14.0, 0.2, 0.8, 0.5)
    return dict(room=S.ROOM[10], vol=-1.5, stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, 'en', None, 1.0, 0.0, ('max', 15.0))])


def lv11():
    def env(m):      # 黒曜の天文台：夕ぐれの 高い 所の 風・左の 天球儀の 大きな 時計（カチッ・コチッ・8つに 1回 ガコン）・歯車・右の 紫水晶が かすかに
        r = m.rng; n = NL; g = B.gust(r, n, 0.08, -0.2, 1.0)
        m.bed(B.wind(r, n, g, 260, 800, 0.18, howl=((520, 760, 14, 0.15),)), wet=0.25)
        m.bed(B.stereo(r, lambda q: B.shaped(q, n, 40, 220, -0.8), 0.6), 0.03)
        for k in range(int(LOOP)): m.ev(B.clock_tick(r, k % 2 == 1, k % 8 == 7), 0.5 + k, -0.4, 0.5, 0.45)
        m.bed(p2(gear_ticks(r, n, 6.0), -0.45), 0.5, wet=0.4)
        hi = pad(r, n, (1176.0, 1568.0), (1.0, 0.5), 0.25, 0.7); m.bed(p2(hi, 0.6), 0.006, wet=0.6)
    def en(m):       # 黒曜の覇王：紫水晶の ヴゥゥン（右）・大きな 足音 ドシン！ドシン！ドシン！・ひづめが コツ
        r = m.rng; n = NL
        m.bed(p2(crystal_loop(r, n), 0.5), 0.22, wet=0.35)
        for grp, (gg, p) in zip(((5.0, 6.2, 7.4), (19.2, 20.4, 21.6)), ((0.85, 0.15), (1.0, 0.05))):
            for t0 in grp: m.ev(B.footstep(r, 1.35, 'stone', True), t0, p, gg, 0.45)
        for t0 in (12.6, 27.2): m.ev(S.hoof_stone(r, 0.6), t0, 0.1, 1.0, 0.6)
    return dict(room=S.ROOM[11], vol=0.0, pan={0: -0.45, 1: -0.35, 2: -0.3, 4: 0.5}, quiet=[(1, 'キリ', 0.0, 2.8, 0.55, ('env',))],
                stems=[('env', env, None, None, 0.8, 0.0, None), ('en', en, (2, 'ヴゥゥン', 0.0), None, 2.0, 0.0, ('max', 12.0))])


def lv12():
    def env(m):      # 日蝕の玉座：赤い 日蝕の 窓・玉座・薔薇の 柱・追いつめられる 音（低い うなり・どこまでも 上がる 音・高い ふるえ）・すきま風・薔薇が かすかに
        r = m.rng; n = NL; t = np.arange(n) / SR
        sw = 0.65 + 0.35 * np.sin(TAU * qf(1 / 16) * t) ** 2
        dr = saws(r, n, (73.42, 77.78, 36.71), (1.0, 0.8, 0.25), 420) * sw; m.bed(np.stack([dr, dr * 0.95]), 0.10, wet=0.3)
        sh = B.shepard(n, 55.0, 7, 16.0, True, 1800); m.bed(np.stack([sh, np.roll(sh, int(0.01 * SR))]), 0.5, wet=0.4)
        tr = (np.sin(TAU * qf(1318.5) * t) + np.sin(TAU * qf(1396.9) * t) * 0.8) * (0.5 + 0.5 * np.sin(TAU * qf(7.0) * t)) * (0.5 + 0.5 * np.sin(TAU * qf(0.125) * t + 1.0)) ** 2
        m.bed(np.stack([tr, tr * 0.7]), 0.015, wet=0.6)
        g = B.gust(r, n, 0.06, -0.5, 1.0); m.bed(B.wind(r, n, g, 200, 600, 0.06, howl=((600, 900, 18, 0.2),)), wet=0.5)
        for t0, p in ((7.0, -0.7), (19.5, 0.7), (28.0, -0.6)): m.ev(S.rustle(r, 0.8, False, 0.25), t0, p, 1.0, 0.5)
    def hb(m):       # 心臓（ゆっくり）：女王が 出る 前の「一瞬、静まり返る」まで
        r = m.rng
        for k in range(40): m.ev(B.heartbeat(r), k * 0.8, 0.0, 0.3, 0.15)
    def en(m):       # 日蝕の薔薇女王：大きな 黒い 羽が 開く バァサ！バァサ！・段を おりる ドシン！ドシン！ドシン！・薔薇が ザワザワ・心臓が 速く・うなりが 強く
        r = m.rng; n = NL
        for k in range(50): m.ev(B.heartbeat(r), k * 0.64, 0.0, 0.2, 0.15)
        d2 = saws(r, n, (110.0, 116.54), (1.0, 0.7), 600); m.bed(np.stack([d2, d2]), 0.05, wet=0.3)
        for t0 in (9.0, 10.3, 11.6, 23.0, 24.3, 25.6): m.ev(B.footstep(r, 1.5, 'stone'), t0, 0.1, 0.95, 0.45)       # 女王が 話す 間・4行目の 前は しずか
        for t0, p in ((14.5, -0.2), (28.0, 0.3)):
            m.ev(B.wing_open(r), t0, p, 0.8, 0.5); m.ev(B.flap(r, 1.5), t0 + 1.6, p, 0.95, 0.5); m.ev(B.flap(r, 1.5), t0 + 2.5, p + 0.1, 1.0, 0.5)
            m.ev(S.roses(r) * 0.5, t0 + 3.2, 0.0, 0.8, 0.4)
    return dict(room=S.ROOM[12], vol=0.0, quiet=[(2, '一瞬', 0.0, 0.95, 0.95, None)],
                stems=[('env', env, None, None, 0.8, 0.0, None), ('hb', hb, None, (2, '一瞬', 0.0), 0.8, 0.2, ('max', -5.0)), ('en', en, (2, '一瞬', 0.95), None, 0.3, 0.0, ('max', 14.0))])


PLAN = {k + 1: f for k, f in enumerate([lv1, lv2, lv3, lv4, lv5, lv6, lv7, lv8, lv9, lv10, lv11, lv12])}


# ---------------- 層を 作る（くり返す 形）----------------
def loops(lv):
    P = PLAN[lv](); R = P['room']
    ir = B.make_ir(np.random.default_rng(lv * 7), R['rt'], R.get('pre', 0.02), R.get('dark', 6000), 120, R.get('er', 0.0), R.get('echoes', ()))
    out = {}
    for k, (nm, fn, *_r) in enumerate(P['stems']):
        m = B.Mix(9000 + lv * 37 + k); fn(m); x = m.out(ir)
        out[nm] = np.stack([B.cf(c, B.sos_hp(42, 2)) for c in x])
    out['env'] *= B.PHONE * 10 ** (P.get('vol', 0.0) / 20) / B.phone_rms(out['env'])      # 場所の 音（env）を そろえる
    med = np.median(short(out['env']))
    for nm, fn, st, sp, fi, fo, tg in P['stems']:                                         # ほかの 層は env の まん中 から 何 dB
        if tg: v = short(out[nm]); out[nm] *= med * 10 ** (tg[1] / 20) / (v.max() if tg[0] == 'max' else np.median(v))
    return P, out


def short(x, w=0.1):
    """0.1秒 ごとの 大きさ（スピーカーで 聞こえる 所）"""
    y = B.cf(x.mean(axis=0), signal.butter(4, [280, 7000], 'band', fs=SR, output='sos')); k = int(w * SR); m = len(y) // k
    return np.sqrt(np.mean(y[:m * k].reshape(m, k) ** 2, axis=1))


# ---------------- 聞いて みる 版（アプリと 同じ 流れ）----------------
def timeline(lv, data):
    area, enemy, say, en = data[lv - 1]
    t = 0.7; starts = []
    for i, s in enumerate(say):                                       # cb_qfield_say.render と 同じ 時刻
        starts.append(t); t += S.read_time(s)
        t = max(t, max([S.at(starts[-1], s, c[1]) + c[3] + 2.0 for c in S.CUES[lv] if c[0] == i] + [0]))
    return starts, t


def scene(lv, data, tail=TAIL, dbg=None):
    area, enemy, say, en = data[lv - 1]; P, L = loops(lv); sfx = cb_sfx.render()
    starts, t_name = timeline(lv, data); t_go = t_name + tail; t_en = starts[en - 1]
    N = int((t_go + 1.2) * SR); M = N + int(8 * SR)
    def mark(spec, dflt):
        if spec is None: return dflt
        if spec == 'en': return t_en + 0.45
        li, mk, dt = spec; return S.at(starts[li], say[li], mk) + dt
    # セリフの 音（cb_qfield_say と 同じ 音：同じ 順に 作る）
    rng = np.random.default_rng(5000 + lv); dry = np.zeros((2, M)); wet = np.zeros_like(dry)
    def put(x, t0, g=1.0, pan=0.0, w=0.3):
        i = max(0, int(t0 * SR)); n = min(len(x), M - i); pl, pr = B.pang(pan)
        dry[0, i:i + n] += x[:n] * g * pl; dry[1, i:i + n] += x[:n] * g * pr
        wet[0, i:i + n] += x[:n] * g * pl * w; wet[1, i:i + n] += x[:n] * g * pr * w
    for k, (li, mk, fn, dt, g, pan, w) in enumerate(S.CUES[lv]):
        x = fn(rng)
        if k in P.get('drop', ()): continue
        put(x, S.at(starts[li], say[li], mk) + dt, g, P.get('pan', {}).get(k, pan), w)
    R = P['room']; ir = B.make_ir(np.random.default_rng(lv * 7), R['rt'], R.get('pre', 0.02), R.get('dark', 6000), 120, R.get('er', 0.0), R.get('echoes', ()))
    wv = np.stack([signal.fftconvolve(wet[0] + wet[1], ir[c])[:M] for c in range(2)]) * 0.5
    cues = (dry + wv)[:, :N]
    for i in range(1, len(say)): cues[:, int((starts[i] - 0.02) * SR):][:, :len(sfx['tap'])] += sfx['tap'] * 0.3       # 次の 行へ タップ
    for tt in (t_name, t_go): cues[:, int(tt * SR):][:, :len(sfx['tap'])] += sfx['tap'] * 0.3                          # 名前 → バトル開始の タップ
    i = int(t_en * SR); cues[:, i:i + len(sfx['magic'])] += sfx['magic'] * 0.5
    i = int((t_en + 0.42) * SR); cues[:, i:i + len(sfx['appear'])] += sfx['appear']                                    # 敵 出現（アプリの 音）
    # BGM の 層（はじまり・おわりは セリフの 流れ）
    tt = np.arange(N) / SR; parts = {}
    for nm, fn, st, sp, fi, fo, tg in P['stems']:
        a = mark(st, 0.0); b = mark(sp, 1e9); i = int(a * SR); x = np.zeros((2, N))
        e = np.clip((tt[i:] - a) / fi, 0, 1) if fi else np.ones(N - i)
        if b < 1e9: e = e * (np.clip((b + fo - tt[i:]) / fo, 0, 1) if fo else (tt[i:] < b))
        x[:, i:] = np.tile(L[nm], (1, (N - i) // NL + 2))[:, :N - i] * e; parts[nm] = x
    for li, mk, d0, d1, dep, only in P.get('quiet', []):                # しずまる 所
        a = S.at(starts[li], say[li], mk) + d0; b = S.at(starts[li], say[li], mk) + d1
        q = 1 - dep * np.clip((tt - a) / 0.15, 0, 1) * np.clip((b + 0.1 - tt) / 0.1, 0, 1)
        for nm in parts:
            if not only or nm in only: parts[nm] *= q
    bgm = sum(parts.values())
    if dbg is not None: dbg.update(parts=parts, cues=cues, k=SAY / B.phone_rms(cues[:, :int(t_name * SR)]))
    mu = np.zeros(N)
    for li, mk, d in P.get('muffle', []):
        a = S.at(starts[li], say[li], mk); mu = np.maximum(mu, np.clip((tt - a) / 0.05, 0, 1) * np.clip((a + d - tt) / 0.8, 0, 1))
    if mu.any(): bgm = bgm * (1 - mu) + np.stack([lpf(c, 350) for c in bgm]) * mu * 0.8
    cues *= SAY / B.phone_rms(cues[:, :int(t_name * SR)])               # セリフの 音の 大きさは cb_qfield_say と 同じ
    y = bgm * BGM_G + cues
    y = np.stack([B.cf(c, B.sos_hp(38, 2)) for c in y])
    y = B.limit(y)
    i = int((t_go + 0.08) * SR); fo = int(0.9 * SR); y[:, i:i + fo] *= np.linspace(1, 0, fo) ** 1.5; y[:, i + fo:] = 0     # バトルへ（BGM は 止まる）
    return y, area, starts, t_name, t_go


def name(lv):
    return f'決戦調査_BGM作り直し_Lv{lv:02d}_{AREAS[lv - 1]}_ためし.m4a'


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); data = S.says()
    if len(sys.argv) > 3 and sys.argv[2] == 'loops':
        lv = int(sys.argv[3]); P, L = loops(lv)
        for k, x in L.items():
            x = x * BGM_G; p = os.path.join(out, f'field2_lv{lv:02d}_{k}.wav'); B.save_wav(x, p); print(p, f'山 {np.abs(x).max():.2f}・スピーカーの 所 {B.phone_rms(x):.4f}')
        sys.exit(0)
    lvs = [int(v) for v in sys.argv[2:]] or list(range(1, 13)); allx = []
    for lv in lvs:
        y, area, starts, t_name, t_go = scene(lv, data); B.to_m4a(y, os.path.join(out, name(lv))); allx.append(y)
        print(f'Lv{lv:02d} {area}：{y.shape[1] / SR:.1f}秒・行の はじめ {[round(s, 1) for s in starts]}・名前 {t_name:.1f}・バトル {t_go:.1f}・山 {np.abs(y).max():.2f}・'
              f'スピーカーの 所 {B.phone_rms(y):.4f}', flush=True)
    if len(lvs) == 12:
        gap = np.zeros((2, int(1.5 * SR)))
        B.to_m4a(np.concatenate(sum([[y, gap] for y in allx], [])[:-1], axis=1), os.path.join(out, '決戦調査_BGM作り直し_12エリア_まとめて聞く_ためし.m4a'))
        print('まとめ：できた')
