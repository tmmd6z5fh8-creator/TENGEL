"""神様的中 ① 青い 嵐の 絵（第4.46版で 一から 作り直し：まさちゃん「まずは、この一枚目の演出完全させよ！ 送った二枚目の動画が求めてる映像！
   この動き、広がり方、光の具合、迫力を求める！ ここは、全力で頼む」）
   - 見本の 動画は 見るだけ（なぞらない・動画の 絵は 使わない）。形・色・光は ここで 一から 作った
   - 出す 絵（大きさと 置き場所は kami_layers.json）：
       gd_storm（嵐の 背景：こい 青と 紫の 雲・床・光の 柱の うしろの 光）・gd_vein1／gd_vein2（まわりの 水色の 電気の 脈：かわるがわる）・
       gd_dome（ガラスの ような 光の ドーム：ふち・たての すじ・下の 光の 帯・肩の ピンクの 光）・gd_fall（光の 滝の すじ：たてに つながる）・
       gd_fmask（光の 滝の 形）・gd_bolt（大きな 雷 6本：1まいに ならべる）・gd_surge（ピンクの 電気の 光）・gd_rock（岩 4つ）
   ドームの 形は kami.py の DOME2（ページの 電気と 同じ 形）"""
import os, sys, math, colorsys
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami as KM                                     # DOME2・dome_r（ページと 同じ 形）

W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 色の くみ（第4.47版：まさちゃん「今青色のところを赤に変えて、紫色のところを金と白に変えられる？」）
PAL = 'blue'           # 'blue'＝はじめの 青い 嵐（前の 絵と 1バイトも かわらない）・'red'＝赤い 嵐・'gold'＝金の 嵐（kami_film.py が えらぶ）


CLOUD_EDGE = (1.0, .13, .07)     # 'red' の 雲の はしの 色（赤い 光）
CLOUD_GOLD = (1.0, .8, .22)      # 'red' の 雲の まん中の 色（金）
CLOUD_K = (.33, .88, .34, .97)   # はしの 強さ・金の 強さ・金が 出はじめる こさ・いちばん 明るく なる こさ
CLOUD_TEX = .42                  # 金の 雲の もようの 強さ
CLOUD_EDGE_GOLD = (1.0, .42, .06)  # 'gold' の 雲の はしの 色（こい 金の 光）


def pc(c, scale=1.0):
    """色の 定数（0〜1 の RGB。scale=255 なら 0〜255）→ 今の 色の くみの 色。
       'red'：青・水色 → 赤（水色は 朱・青は 赤・こい 青は 紅。白に 近い 光は あたたかい 白）／紫・ピンク → 金（うすい 色ほど 白に 近い 金）。
       白・黒・灰と 金・だいだいなどは そのまま"""
    if PAL == 'blue':
        return np.array(c, np.float32) if scale == 1.0 else c
    if PAL == 'gold':
        return _pc_gold(c, scale)
    rgb = [float(v) / scale for v in c]
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    h *= 360
    if s < 1e-6:
        out = rgb
    elif 150 <= h <= 258:
        th = float(np.interp(h, (150, 180, 200, 220, 240, 258), (16, 11, 5, 0, -5, -8))) + (1 - s) * 16
        out = colorsys.hsv_to_rgb((th % 360) / 360, s, v)
    elif 258 < h <= 345:
        th = float(np.interp(s, (0, .5, 1), (48, 45, 42)))
        out = colorsys.hsv_to_rgb(th / 360, s * .9, v)
    else:
        out = rgb
    out = [x * scale for x in out]
    return np.array(out, np.float32) if scale == 1.0 else tuple(out)


def _pc_gold(c, scale=1.0):
    """'gold'（第4.50版：まさちゃん「赤色のところを金色にして！」）：青・水色 → 金（こい 青は こい 金・水色は 明るい 金）／
       紫・ピンク → 金／赤・だいだい → 金。白・黒・灰は そのまま"""
    rgb = [float(v) / scale for v in c]
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    h *= 360
    if s < 1e-6:
        out = rgb
    elif 150 <= h <= 258:
        th = float(np.interp(h, (150, 180, 200, 220, 240, 258), (42, 40, 38, 35, 32, 30)))
        out = colorsys.hsv_to_rgb(th / 360, s * .95, v)
    elif 258 < h <= 345:
        th = float(np.interp(s, (0, .5, 1), (44, 40, 36)))
        out = colorsys.hsv_to_rgb(th / 360, s * .92, v)
    elif h > 345 or h < 34:
        hh = h - 360 if h > 345 else h
        th = 33 + max(0.0, hh) * .1
        out = colorsys.hsv_to_rgb(th / 360, s * .95, v)
    else:
        out = rgb
    if s >= 1e-6 and not (34 <= h <= 150):
        out = [x * (1 - .28 * s) for x in out]                 # 金は 赤より ずっと 明るく 見えるので こい 色ほど 少し 暗く（深い 金・点めつも ふやさない）
    out = [x * scale for x in out]
    return np.array(out, np.float32) if scale == 1.0 else tuple(out)


def smoothstep(e0, e1, x):
    u = np.clip((x - e0) / (e1 - e0), 0, 1)
    return u * u * (3 - 2 * u)


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    xs = np.array([s for s, _ in stops])
    cs = np.array([c for _, c in stops], np.float32) / 255
    return np.stack([np.interp(t, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def noise(h, w, cells, seed, interp=cv2.INTER_CUBIC):
    rng = np.random.default_rng(seed)
    cy, cx = max(2, int(round(cells * h / max(h, w)))), max(2, int(round(cells * w / max(h, w))))
    g = rng.random((cy + 3, cx + 3)).astype(np.float32)
    big = cv2.resize(g, (int(w * (cx + 3) / cx), int(h * (cy + 3) / cy)), interpolation=interp)
    return big[:h, :w]


def fbm(h, w, cells, seed, oct=5, gain=.5):
    t = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(oct):
        t += amp * noise(h, w, cells * 2 ** o, seed + o * 17)
        tot += amp
        amp *= gain
    return t / tot


def over(dst, src):
    return src + dst * (1 - src[..., 3:4])


def glow(img, sig):
    return cv2.GaussianBlur(img, (0, 0), sig)


def finish(rgb, a=None):
    """光の 絵（足した 光）→ premultiplied RGBA：明るい 所ほど 不とうめい（黒は すき通し）"""
    rgb = np.clip(rgb, 0, 1)
    lum = rgb.max(-1)
    al = np.clip(lum if a is None else np.maximum(a, lum), 0, 1)
    return np.dstack([rgb, al])


# ---------------------------------------------------------------- 線を 描く 道具
def disp(rng, a, b, depth, rough):
    pts = [a, b]
    for _ in range(depth):
        nw = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            o = rng.normal(0, rough * L / 2)
            nw += [((ax + bx) / 2 + nx * o, (ay + by) / 2 + ny * o), (bx, by)]
        pts = nw
    return pts


def poly(img, pts, k, val, w):
    """線（画面の px の 点の 列）を k 倍の 絵に"""
    q = np.int32(np.round(np.array(pts) * k * 8))
    cv2.polylines(img, [q], False, float(val), max(1, int(round(w * k))), cv2.LINE_AA, shift=3)


# ---------------------------------------------------------------- 嵐の 背景
def plasma(H, W, cells, seed, p=6.0):
    """電気の もやの すじ（ゆがめた ノイズの 0.5 の 所が 細く 光る）→ 0〜1"""
    q1 = fbm(H, W, cells * .6, seed + 1, 4)
    q2 = fbm(H, W, cells * .6, seed + 2, 4)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = fbm(H, W, cells, seed, 5, .55)
    n = cv2.remap(n, xx + (q1 - .5) * W * .12, yy + (q2 - .5) * H * .08, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    n = (n - n.mean()) / (n.std() + 1e-6)
    return np.clip(1 - np.abs(n) * 1.6, 0, 1) ** p


def storm_bg(W, H, seed=21, falls=1.0):
    """嵐の 背景（RGB・画面いっぱい）：こい 青の 空に 水色の 電気の もや・紫と ピンクの 雲・光の 滝の 体と 床の しぶき・
       床（ぬれた 青・光の つぶ・横の 光の すじ）。ドーム・滝の すじ・電気は べつの 層"""
    k = W / W_
    ys = (np.arange(H, dtype=np.float32)[:, None] / k) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / k) * np.ones((H, 1), np.float32)
    cx, base = KM.DOME2[0], KM.DOME2[1]
    # 空：まん中が こい 青 → はしと 上は 暗い 紺
    r = np.sqrt(((xs - cx) / 300) ** 2 + ((ys - 560) / 520) ** 2)
    col = ramp(r, tuple((q, pc(c, 255)) for q, c in ((0, (20, 50, 210)), (.35, (14, 30, 150)), (.65, (10, 12, 84)), (.9, (6, 5, 36)), (1.2, (2, 2, 12)))))
    fog = fbm(H, W, 5, seed, 6, .55)
    fog2 = fbm(H, W, 14, seed + 3, 4, .5)
    col = col * (.62 + .55 * fog[..., None] + .18 * (fog2[..., None] - .5))
    # 水色・青の 電気の もや（すじ：空いっぱい・まん中の 滝の 所は うすく）
    pl1 = plasma(H, W, 7, seed + 20, 5.0)
    pl2 = plasma(H, W, 13, seed + 30, 7.0)
    side = .35 + .65 * smoothstep(40, 150, np.abs(xs - cx))
    m1 = (.55 + .45 * fbm(H, W, 4, seed + 40, 3)) * side * smoothstep(base + 10, base - 40, ys)
    col = col + pc((.1, .55, 1.0)) * (pl1 * m1)[..., None] * .55
    col = col + pc((.3, .85, 1.0)) * (pl2 * m1)[..., None] * .35
    col = col + pc((.08, .3, 1.0)) * glow(pl1 * m1, 6 * k)[..., None] * .5
    # 上の 左右の 紫・ピンクの 雲（もやもや）＋ピンクの すじ
    for (px, py, rr, c, s_) in ((40, 150, 240, (150, 40, 230), seed + 7), (360, 120, 230, (210, 50, 210), seed + 8),
                                (340, 400, 170, (120, 40, 240), seed + 9), (40, 440, 180, (100, 30, 220), seed + 10)):
        g = np.clip(1 - np.sqrt((xs - px) ** 2 + (ys - py) ** 2) / rr, 0, 1) ** 1.5
        tx = fbm(H, W, 9, s_, 5, .55)
        g = g * smoothstep(.33, .75, tx + g * .35)
        if PAL == 'blue':
            col = col + np.array(pc(c, 255), np.float32) / 255 * g[..., None] * .8
        else:
            # 金の 雲：うすい 所は 赤い 光（空に とける。暗い 金は 茶色に 見えるので 作らない）→ こい 所ほど 明るい 金
            col = col + np.array(CLOUD_EDGE_GOLD if PAL == 'gold' else CLOUD_EDGE, np.float32) * g[..., None] * CLOUD_K[0]
            gt = g * (1 - CLOUD_TEX + 2 * CLOUD_TEX * tx)                    # 雲の もよう（ぼんやりした 玉に しない）
            col = col + np.array(CLOUD_GOLD, np.float32) * (smoothstep(CLOUD_K[2], CLOUD_K[3], gt) ** 1.5)[..., None] * CLOUD_K[1]
        col = col + pc((1.0, .35, .9)) * (plasma(H, W, 11, s_ + 50, 7.0) * g)[..., None] * .35
    # 光の 滝の 体（上から 床まで：明るい しん・下ほど ひろく 明るい）
    u = np.clip(ys / base, 0, 1)
    half = 48 + 76 * u ** 1.5
    wf = np.exp(-((xs - cx) / (half * 1.05)) ** 2) * (.6 + .4 * u) * smoothstep(base + 30, base - 10, ys)
    wcore = np.exp(-((xs - cx) / (half * .38)) ** 2) * (.55 + .45 * u) * smoothstep(base + 20, base - 10, ys)
    wout = np.exp(-((xs - cx) / (half * 2.2)) ** 2) * (.3 + .7 * u)
    wtex = .75 + .5 * fbm(H, W, 24, seed + 60, 4)                      # 滝の 体の もようの こさ（動かない）
    col = col + pc((.05, .3, 1.0)) * wout[..., None] * .35 * falls
    col = col + pc((.1, .78, 1.0)) * (wf * wtex)[..., None] * .75 * falls
    col = col + pc((.62, .97, 1.0)) * wcore[..., None] * .62 * falls
    pool = np.exp(-(((xs - cx) / 220) ** 2 + ((ys - base) / 62) ** 2))
    col = col + pc((.15, .7, 1.0)) * pool[..., None] * .7 * falls
    # 床の しぶき（白い あわ：滝の 下で ばらばらに 光る かたまり）
    foam_n = fbm(H, W, 40, seed + 70, 4)
    fe = np.exp(-(((xs - cx) / 150) ** 2 + ((ys - base + 6) / 22) ** 2))
    foam = smoothstep(.52, .7, foam_n + fe * .25) * fe
    foam = np.maximum(foam, glow(foam, 3 * k) * 1.2)
    col = col + pc((.75, .98, 1.0)) * foam[..., None] * .9 * falls
    hot = np.exp(-(((xs - cx) / 120) ** 2 + ((ys - base + 8) / 28) ** 2))
    col = col + pc((.6, .97, 1.0)) * hot[..., None] * .55 * falls
    # 床（ぬれた 青：横の 光の すじ・光の つぶ）
    gnd = smoothstep(base - 6, base + 16, ys)
    fl = ramp((ys - base) / (H / k - base), tuple((q, pc(c, 255)) for q, c in ((0, (14, 40, 170)), (.4, (8, 20, 110)), (1, (3, 6, 40)))))
    rng = np.random.default_rng(seed + 12)
    st = np.zeros((H, W), np.float32)
    for _ in range(170):
        y = rng.uniform(base + 4, H / k - 4)
        x = rng.normal(cx, 120)
        L = rng.uniform(12, 70) * (1 + (y - base) / 120)
        cv2.line(st, (int((x - L / 2) * k * 4), int(y * k * 4)), (int((x + L / 2) * k * 4), int(y * k * 4)), float(rng.uniform(.2, .8)),
                 max(1, int(k)), cv2.LINE_AA, shift=2)
    st = glow(st, .8 * k) * 1.4
    near = np.exp(-((xs - cx) / 170) ** 2)
    fl = fl + pc((.3, .75, 1.0)) * (st * (.35 + .65 * near))[..., None] * .7
    dots = np.zeros((H, W), np.float32)
    for _ in range(int(W * H * .0018)):
        x = rng.normal(cx, 110)
        y = rng.uniform(base - 6, H / k)
        if not (0 <= x < W_):
            continue
        cv2.circle(dots, (int(x * k), int(y * k)), int(rng.integers(0, 2)), float(rng.uniform(.4, 1.0)), -1, cv2.LINE_AA)
    dots = np.maximum(dots, glow(dots, 1.6 * k) * 1.6)
    fl = fl + pc((.45, .9, 1.0)) * dots[..., None] * .75
    col = col * (1 - gnd[..., None]) + fl * gnd[..., None]
    col = col + pc((.2, .7, 1.0)) * (pool * gnd)[..., None] * .5 * falls
    vig = 1 - .5 * smoothstep(.55, 1.15, np.sqrt(((xs - cx) / 260) ** 2 + ((ys - 470) / 560) ** 2))
    return np.clip(col * vig[..., None], 0, 1)


# ---------------------------------------------------------------- 光の ドーム（ガラスの ような）
DOME_PAD = (28.0, 30.0, 34.0)          # ドームの 絵の あき（左右・上・下）画面の px
DOME_DPR = 2.0


def dome_box():
    cx, base, RX, HD = KM.DOME2[:4]
    x0 = cx - RX - DOME_PAD[0]
    y0 = base - HD - DOME_PAD[1]
    return x0, y0, 2 * (RX + DOME_PAD[0]), HD + DOME_PAD[1] + DOME_PAD[2]


def dome_glass(seed=31, k=None, gloss=False):
    """光の ドーム（前の 面）→ premultiplied RGBA（dome_box の 大きさ × DOME_DPR）。
       すき通る ガラス（まん中は うすく・はしほど 光る）・たての 光の すじ（下ほど 強い）・下の 横の 光の 帯・ふち（光の 粒が つながった 線）と 外の 光・
       ふちの 内がわの 厚み・肩の ピンクの 光"""
    cx, base, RX, HD = KM.DOME2[:4]
    k = k or DOME_DPR
    x0, y0, bw, bh = dome_box()
    W, H = int(round(bw * k)), int(round(bh * k))
    X = (np.arange(W, dtype=np.float32)[None, :] / k + x0) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / k + y0) * np.ones((1, W), np.float32)
    h = base - Y
    r = KM.dome_r(np.clip(h, 0, HD))
    s = np.clip((X - cx) / np.maximum(r, 1e-3), -1, 1)
    inside = ((np.abs(X - cx) < r) & (h >= 0) & (h <= HD)).astype(np.float32)
    # 形の ふちからの きょり（画面の px：内は ＋）
    m8 = (inside > .5).astype(np.uint8)
    din = cv2.distanceTransform(m8, cv2.DIST_L2, 5) / k
    dout = cv2.distanceTransform(1 - m8, cv2.DIST_L2, 5) / k
    sd = din - dout
    # 面の 向き
    dh = 1.0
    rp = (KM.dome_r(np.clip(h + dh, 0, HD)) - KM.dome_r(np.clip(h - dh, 0, HD))) / (2 * dh)
    c = np.sqrt(np.clip(1 - s * s, 0, 1))
    nz = c / np.sqrt(1 + rp * rp)
    fres = np.clip(1 - nz, 0, 1)
    phi = np.arcsin(s)
    u = np.clip(h / HD, 0, 1)
    rng = np.random.default_rng(seed)
    col = np.zeros((H, W, 3), np.float32)
    al = np.zeros((H, W), np.float32)
    # ガラスの 体：まん中は うすい 青・はしほど 明るい 水色
    body = inside * (.05 + .5 * fres ** 2.0)
    col += pc((.12, .4, 1.0)) * (inside * (.08 + .12 * u))[..., None] * .4
    col += pc((.35, .85, 1.0)) * (inside * fres ** 2.0)[..., None] * .55
    al = np.maximum(al, body)
    if gloss:
        # ガラスが 光を すう（おくの 光が 少し 暗く 青く：奥行き）
        tint = inside * (.2 + .25 * fres ** 2)
        al = np.maximum(al, tint)
        col += pc((.0, .02, .08)) * tint[..., None]
        # つや：左上からの 光の 映りこみ（広い つや＋細い つや）
        rn2 = np.sqrt(1 + rp * rp)
        nx_, nu_, nz_ = s * c / c.clip(1e-3) / rn2, -rp / rn2, c / rn2
        Ld = np.array([-.5, .55, .67])
        Ld /= np.linalg.norm(Ld)
        hv = Ld + np.array([0, 0, 1.0])
        hv /= np.linalg.norm(hv)
        ndh = np.clip(nx_ * hv[0] + nu_ * hv[1] + nz_ * hv[2], 0, 1) * inside
        sp1 = ndh ** 40 * .35
        # 細長い つや（たての 光の 映りこみ：左に 太く・右に 細く。上と 下は うすく）
        ph_d = np.degrees(phi)
        vert = smoothstep(.04, .2, u) * (1 - smoothstep(.6, .9, u)) * inside
        sp1 = sp1 + (np.exp(-((ph_d + 44) / 4.5) ** 2) * .9 + np.exp(-((ph_d + 36) / 1.2) ** 2) * .8 + np.exp(-((ph_d - 57) / 2.2) ** 2) * .5) * vert
        col += pc((.85, .97, 1.0)) * sp1[..., None]
        al = np.maximum(al, np.clip(sp1, 0, 1) * .8)
        # 空の 映りこみ（上の ほうの 弓なりの 光の 帯）
        band2 = inside * smoothstep(.45, .62, nu_) * (1 - smoothstep(.7, .86, nu_)) * (.6 + .4 * fbm(H, W, 12, seed + 12, 3))
        col += pc((.55, .85, 1.0)) * band2[..., None] * .3
        al = np.maximum(al, band2 * .3)
    # たての 光の すじ（球の 表面に そって・下ほど 強い・はしほど 細かい）
    nrib = 15
    wob = (fbm(H, W, 5, seed + 11, 3) - .5) * .5                     # すじの ゆらぎ（まっすぐ すぎない）
    rib = (.5 + .5 * np.cos(phi * nrib * 2 + .7 + wob * 3)) ** 6
    rib2 = (.5 + .5 * np.cos(phi * nrib * 5 + 2.1 + wob * 5)) ** 10
    rn = fbm(H, W, 7, seed + 2, 4)
    rib_a = inside * (rib * .9 + rib2 * .45) * (.25 + .75 * smoothstep(.75, .05, u)) * (.35 + .65 * smoothstep(.15, .7, np.abs(s))) * (.5 + .9 * rn)
    col += pc((.55, .92, 1.0)) * rib_a[..., None] * .55
    # 下の 横の 光の 帯（ガラスに 映る 光：きらきら した 横の すじ）
    hb = np.zeros((H, W), np.float32)
    for _ in range(18):
        yy = base - rng.uniform(3, 9) * rng.uniform(1, 9)
        ww = rng.uniform(.5, 1.4)
        xc = rng.uniform(cx - RX, cx + RX)
        ln = rng.uniform(14, 70)
        amp = rng.uniform(.3, .9)
        seg = np.exp(-((Y - yy) / ww) ** 2) * np.exp(-((X - xc) / ln) ** 2) * amp
        hb = np.maximum(hb, seg)
    hb *= inside * (.6 + .6 * fbm(H, W, 20, seed + 4, 3))
    col += pc((.75, .97, 1.0)) * hb[..., None] * .9
    base_band = inside * np.exp(-(h / 18) ** 2) * (.5 + .5 * np.abs(s))
    col += pc((.3, .85, 1.0)) * base_band[..., None] * .55
    # ふちの 内がわの 厚み（明るい 帯）
    band = inside * smoothstep(18, 2, din) * (.55 + .45 * fbm(H, W, 30, seed + 5, 3))
    col += pc((.45, .9, 1.0)) * band[..., None] * .65
    al = np.maximum(al, band * .7)
    # 肩の ピンクの 光（ふちの 内がわ：電気が はしる 所）
    sh = inside * smoothstep(54, 6, din) * smoothstep(.3, .6, u) * smoothstep(1.0, .82, u) * smoothstep(.08, .42, np.abs(s))
    sh *= .5 + 1.0 * fbm(H, W, 16, seed + 6, 4)
    col += pc((1.0, .22, .8)) * sh[..., None] * .36
    col += pc((1.0, .5, .9)) * (sh * plasma(H, W, 18, seed + 9, 6.0))[..., None] * .5
    # ガラスの 中の 細い 電気の すじ（水色：下と 横に 多い）
    vv = inside * plasma(H, W, 14, seed + 10, 7.0) * (.35 + .65 * smoothstep(.85, .2, u)) * (.4 + .6 * smoothstep(.1, .7, np.abs(s)))
    col += pc((.45, .9, 1.0)) * vv[..., None] * .32
    # ふち：光の 粒が つながった 線（明るさが ゆらぐ）と 外の 光
    edge = np.clip(1 - np.abs(sd - .7) / 1.6, 0, 1)
    lumpy = .55 + .45 * smoothstep(.3, .7, fbm(H, W, 90, seed + 7, 3)) + .5 * (fbm(H, W, 260, seed + 8, 2) > .62)
    rim = edge * lumpy * (h > -1)
    rim *= 1 - .5 * smoothstep(20, 0, h)                    # 床の 所は 少し 弱く
    beads = np.zeros((H, W), np.float32)
    # 粒（ふちに そって 小さな 光の 玉と とげ）
    tpar = np.linspace(0, 1, 1200)
    for tt in tpar:
        if rng.random() > .58:
            continue
        side = -1 if tt < .5 else 1
        uu = abs(tt - .5) * 2                               # 0＝てっぺん・1＝床
        hh = HD * (1 - uu)
        rr = float(KM.dome_r(hh))
        px, py = cx + side * rr, base - hh
        # ふちの 外向き
        rr2 = float(KM.dome_r(min(HD, hh + 1.5)))
        tx_, ty_ = side * (rr2 - rr), -1.5
        nx_, ny_ = -ty_, tx_
        L = math.hypot(nx_, ny_) or 1
        nx_, ny_ = side * abs(nx_ / L) if abs(nx_) > 1e-6 else 0.0, -abs(ny_ / L)
        if hh < HD * .02:
            nx_, ny_ = 0.0, -1.0
        rad = rng.uniform(.7, 2.1)
        off = rng.uniform(-.6, 1.2)
        cv2.circle(beads, (int((px + nx_ * off - x0) * k * 4), int((py + ny_ * off - y0) * k * 4)), int(rad * k * 4), float(rng.uniform(.5, 1.0)), -1, cv2.LINE_AA, shift=2)
        if rng.random() < .22:
            ln = rng.uniform(2, 8)
            ang = math.atan2(ny_, nx_) + rng.uniform(-.7, .7)
            cv2.line(beads, (int((px - x0) * k * 4), int((py - y0) * k * 4)),
                     (int((px + ln * math.cos(ang) - x0) * k * 4), int((py + ln * math.sin(ang) - y0) * k * 4)), float(rng.uniform(.5, 1.0)), max(1, int(k * .7)), cv2.LINE_AA, shift=2)
    rim = np.maximum(rim, beads)
    rimg = glow(rim, 2.5 * k) * 2.0 + glow(rim, 7 * k) * 1.4 + glow(rim, 16 * k) * .8
    col += pc((.5, .9, 1.0)) * rimg[..., None] * .55
    col += pc((1.0, 1.0, 1.0)) * rim[..., None] * .95
    col += pc((.3, .8, 1.0)) * glow(rim, 1.2 * k)[..., None] * .4
    # 床との さかいめの 光（ドームの 下の ふち）
    lip = np.exp(-(((Y - base - 2) / 2.2) ** 2)) * smoothstep(RX + 6, RX - 30, np.abs(X - cx))
    lip = np.maximum(lip, glow(lip, 6 * k) * 1.2)
    col += pc((.4, .9, 1.0)) * lip[..., None] * .7
    col = np.clip(col, 0, 1.5)
    out = np.zeros((H, W, 4), np.float32)
    lum = np.clip(col.max(-1), 0, 1)
    a = np.clip(np.maximum(al, lum * .92), 0, 1)
    out[..., :3] = np.clip(col, 0, 1)
    out[..., 3] = np.maximum(a, out[..., :3].max(-1))
    return out


# ---------------------------------------------------------------- 光の 滝
FALL2 = (340.0, 420.0, 1.5)            # 光の 滝の すじの 絵（画面の px：はば・高さ（たてに つながる）・倍率）
FALL_BOX = (25.0, -10.0, 340.0, 744.0)  # 光の 滝の 置き場所（左・上・はば・高さ）


def fall_tile2(seed=33, k=None):
    """光の 滝の すじ（上から 下へ 落ちる 細かい 光の すじ：たてに つながる 絵）→ premultiplied RGBA。
       細い すじを たくさん（太い かたまりは 作らない：速く 動くと 点めつに なる）"""
    Wc, Hc, k0 = FALL2
    k = k or k0
    W, H = int(Wc * k), int(Hc * k)
    rng = np.random.default_rng(seed)
    a = np.zeros((H, W), np.float32)
    n = int(Wc * 3.8)
    clumps = [(rng.normal(.5, .16) * Wc, rng.uniform(0, Hc)) for _ in range(14)]     # すじの かたまり（しぶきの 束）
    for _ in range(n):
        if rng.random() < .3:
            c_ = clumps[rng.integers(len(clumps))]
            x = float(np.clip(c_[0] + rng.normal(0, 7), 2, Wc - 2))
        else:
            x = np.clip(rng.normal(.5, .17), 0.02, .98) * Wc
        cen = math.exp(-((x / Wc - .5) / .2) ** 2)
        L = rng.uniform(10, 80)
        y0 = rng.uniform(0, Hc)
        w = rng.choice((.6, .8, 1.0, 1.0, 1.3))
        lv = rng.uniform(.15, .5) * (.55 + .45 * cen)
        for off in (-Hc, 0, Hc):
            p0 = (x, y0 + off)
            p1 = (x + rng.uniform(-.6, .6), y0 + L + off)
            if p1[1] < 0 or p0[1] > Hc:
                continue
            # 下が 明るい（落ちる 先）：3つに 分けて だんだん 明るく
            for j in range(3):
                q0 = (p0[0] + (p1[0] - p0[0]) * j / 3, p0[1] + (p1[1] - p0[1]) * j / 3)
                q1 = (p0[0] + (p1[0] - p0[0]) * (j + 1) / 3, p0[1] + (p1[1] - p0[1]) * (j + 1) / 3)
                cv2.line(a, (int(q0[0] * k * 8), int(q0[1] * k * 8)), (int(q1[0] * k * 8), int(q1[1] * k * 8)),
                         float(lv * (.45 + .55 * (j + 1) / 3)), max(1, int(round(w * k))), cv2.LINE_AA, shift=3)
    # 細かい しぶきの 点
    for _ in range(int(Wc * 2.2)):
        x = np.clip(rng.normal(.5, .25), 0, 1) * Wc
        y = rng.uniform(0, Hc)
        for off in (-Hc, 0, Hc):
            cv2.circle(a, (int(x * k * 4), int((y + off) * k * 4)), int(rng.uniform(.4, 1.0) * k * 4), float(rng.uniform(.3, .7)), -1, cv2.LINE_AA, shift=2)
    a = np.maximum(a, glow(a, 1.2 * k) * .9)
    a = np.clip(a, 0, 1)
    if PAL == 'blue':
        col = np.stack([.5 + .5 * a, .92 + .08 * a, np.ones_like(a)], -1)
    else:
        c0 = pc((.5, .92, 1.0))
        col = c0[None, None, :] + (1 - c0)[None, None, :] * a[..., None]
    return np.dstack([col * a[..., None], a])


def fall_mask(k=1.0):
    """光の 滝の 形（上は せまく 下ほど ひろい・ふちは やわらか）→ 0〜1（k 倍）"""
    x0, y0, w, h = FALL_BOX
    W, H = int(round(w * k)), int(round(h * k))
    ys = (np.arange(H, dtype=np.float32)[:, None] / k + y0) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / k + x0) * np.ones((H, 1), np.float32)
    cx, base = KM.DOME2[0], KM.DOME2[1]
    u = np.clip(ys / base, 0, 1)
    half = 50 + 92 * u ** 1.5
    m = smoothstep(half + 26, half - 18, np.abs(xs - cx))
    m *= smoothstep(base + 18, base - 12, ys)
    return m


# ---------------------------------------------------------------- まわりの 水色の 電気の 脈
def vein_tree(rng, img, k, p, ang, length, w, lv, depth):
    """枝わかれ する 電気の 脈（ギザギザ・先ほど 細く・暗く）"""
    pts = [p]
    x, y = p
    seg = 6.0
    n = max(2, int(length / seg))
    a = ang
    for i in range(n):
        a += rng.normal(0, .42)
        a = ang + max(-.9, min(.9, a - ang))
        x += seg * math.cos(a)
        y += seg * math.sin(a)
        pts.append((x, y))
        if depth > 0 and rng.random() < .22:
            vein_tree(rng, img, k, (x, y), a + rng.choice((-1, 1)) * rng.uniform(.4, 1.1), length * rng.uniform(.35, .65) * (1 - i / n * .5),
                      w * .72, lv * .82, depth - 1)
    for i in range(len(pts) - 1):
        f = 1 - .55 * i / len(pts)
        poly(img, [pts[i], pts[i + 1]], k, lv * f, max(.5, w * f))


def veins(seed, k=1.5):
    """まわりの 水色の 電気の 脈（ドームの 外の 左右と 上：枝わかれ する 光）→ premultiplied RGBA（画面いっぱい）"""
    W, H = int(W_ * k), int(H_ * k)
    rng = np.random.default_rng(seed)
    a = np.zeros((H, W), np.float32)
    cx, base, RX, HD = KM.DOME2
    # ドームの ふちの 外から 外へ のびる 脈・上の すみの 脈
    for j in range(26):
        side = -1 if j % 2 == 0 else 1
        hh = rng.uniform(.05, .95) * HD
        rr = float(KM.dome_r(hh))
        px, py = cx + side * (rr + rng.uniform(4, 14)), base - hh
        out_a = math.atan2(-hh * .6 / HD, side * 1.0) if side > 0 else math.atan2(-hh * .6 / HD, -1.0)
        vein_tree(rng, a, k, (px, py), out_a + rng.uniform(-.6, .6), rng.uniform(50, 120), rng.uniform(1.0, 1.6), rng.uniform(.6, 1.0), 4)
    for j in range(12):
        px, py = rng.choice((rng.uniform(-10, 90), rng.uniform(300, 400))), rng.uniform(10, 260)
        vein_tree(rng, a, k, (px, py), rng.uniform(0, 2 * math.pi), rng.uniform(50, 110), rng.uniform(.9, 1.4), rng.uniform(.5, .9), 3)
    # ドームの 中には 描かない（ドームの 外の 脈）
    X = (np.arange(W, dtype=np.float32)[None, :] / k) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / k) * np.ones((1, W), np.float32)
    h = base - Y
    r = KM.dome_r(np.clip(h, 0, HD))
    ins = ((np.abs(X - cx) < r - 8) & (h > 0) & (h < HD - 8)).astype(np.float32)
    a *= 1 - glow(ins, 6 * k)
    g = np.clip(glow(a, 1.6 * k) * 1.6 + glow(a, 5 * k) * 1.3 + glow(a, 13 * k) * .9, 0, 1.5)
    col = np.zeros((H, W, 3), np.float32)
    col += pc((.15, .7, 1.0)) * g[..., None] * .75
    col += pc((.85, 1.0, 1.0)) * a[..., None] * .85
    return finish(col)


# ---------------------------------------------------------------- 白い 光の 帯（上から 下へ のびる 光の 流れ）
RIB_DPR = 1.5
RIB_PAD = 62.0


def bez(p, t):
    p0, p1, p2, p3 = [np.array(q, np.float64) for q in p]
    t = np.asarray(t)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def ribbon_box(p):
    pts = bez(p, np.linspace(0, 1, 200))
    x0, y0 = pts.min(0) - RIB_PAD
    x1, y1 = pts.max(0) + RIB_PAD
    return float(x0), float(y0), float(x1 - x0), float(y1 - y0)


def ribbon(p, seed, strands=3, k=None):
    """白い 光の 帯 1本（2〜3本の 光の 糸が ねじれながら ならぶ・まん中が 明るく 両はしは うすく）→ premultiplied RGBA（ribbon_box の 大きさ × RIB_DPR）"""
    k = k or RIB_DPR
    x0, y0, bw, bh = ribbon_box(p)
    W, H = int(round(bw * k)), int(round(bh * k))
    rng = np.random.default_rng(seed)
    n = 700
    t = np.linspace(0, 1, n)
    pts = bez(p, t)
    d = np.gradient(pts, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    core = np.zeros((H, W), np.float32)
    thin = np.zeros((H, W), np.float32)
    env = np.clip(np.sin(np.pi * np.clip(t * 1.08 - .02, 0, 1)) ** .6, 0, 1)      # 両はしは うすく
    for s in range(strands):
        ph = rng.uniform(0, 2 * np.pi)
        fq = rng.uniform(1.2, 2.4)
        amp = rng.uniform(2.5, 6)
        off = (s - (strands - 1) / 2) * rng.uniform(4, 7) + amp * np.sin(2 * np.pi * fq * t + ph)
        q = pts + nrm * off[:, None]
        lv = (.55 + .45 * np.sin(2 * np.pi * rng.uniform(.6, 1.4) * t + rng.uniform(0, 6))) * env
        w = rng.uniform(4.4, 5.6) if s == strands // 2 else rng.uniform(2.0, 3.0)
        for i in range(0, n - 1, 2):
            a_ = (int((q[i, 0] - x0) * k * 8), int((q[i, 1] - y0) * k * 8))
            b_ = (int((q[i + 2 if i + 2 < n else n - 1, 0] - x0) * k * 8), int((q[i + 2 if i + 2 < n else n - 1, 1] - y0) * k * 8))
            cv2.line(core if s == strands // 2 else thin, a_, b_, float(lv[i]), max(1, int(round(w * k))), cv2.LINE_AA, shift=3)
    allc = np.maximum(core, thin * .85)
    g1 = glow(allc, 2.6 * k)
    g2 = glow(allc, 8 * k)
    g3 = glow(allc, 20 * k)
    col = np.zeros((H, W, 3), np.float32)
    col += pc((.2, .5, 1.0)) * g3[..., None] * 3.2
    col += pc((.4, .82, 1.0)) * g2[..., None] * 2.6
    col += pc((.8, .97, 1.0)) * g1[..., None] * 2.0
    col += pc((1.0, 1.0, 1.0)) * allc[..., None] * 1.2
    yy = np.minimum(np.arange(H), np.arange(H)[::-1])[:, None]
    xx = np.minimum(np.arange(W), np.arange(W)[::-1])[None, :]
    taper = smoothstep(0, 14 * k, np.minimum(yy, xx).astype(np.float32))
    return finish(col * taper[..., None])


def ribbon_sheet():
    """白い 光の 帯（kami.py の RIBBONS）を 横に ならべた 1まい → (premultiplied RGBA, [(絵の 中の x, 画面の 箱)…])"""
    imgs, boxes = [], []
    for j, (p, t0, t1) in enumerate(KM.RIBBONS):
        imgs.append(ribbon(p, 500 + 7 * j))
        boxes.append(ribbon_box(p))
    H = max(im.shape[0] for im in imgs)
    W = sum(im.shape[1] for im in imgs) + 2 * (len(imgs) - 1)
    sheet = np.zeros((H, W, 4), np.float32)
    x = 0
    pos = []
    for im, bx in zip(imgs, boxes):
        sheet[:im.shape[0], x:x + im.shape[1]] = im
        pos.append((round(x / RIB_DPR, 2), bx))
        x += im.shape[1] + 2
    return sheet, pos


# ---------------------------------------------------------------- ピンクの 電気の 光（ドームの 左右の 肩が ピンクに 光る 一瞬）
def surge(seed=81, k=1.0):
    """ドームの 左右の 肩に ピンク・紫の 電気の 光（ピンクの もやの すじ＋光＋細かい 電気）→ premultiplied RGBA（画面いっぱい・k 倍）"""
    W, H = int(W_ * k), int(H_ * k)
    X = (np.arange(W, dtype=np.float32)[None, :] / k) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / k) * np.ones((1, W), np.float32)
    cx, base, RX, HD = KM.DOME2
    col = np.zeros((H, W, 3), np.float32)
    rng = np.random.default_rng(seed)
    for (px, py, rx, ry, s, amp) in ((cx - 118, base - 236, 168, 250, seed, 1.0), (cx + 128, base - 214, 128, 196, seed + 1, .75)):
        e = np.clip(1 - np.sqrt(((X - px) / rx) ** 2 + ((Y - py) / ry) ** 2), 0, 1)
        tx = fbm(H, W, 7, s, 5, .55)
        m = e ** 1.1 * smoothstep(.28, .7, tx + e * .35) * amp
        fil = plasma(H, W, 10, s + 5, 4.5) * e * amp
        col += pc((1.0, .16, .74)) * m[..., None] * .95
        col += pc((.6, .12, 1.0)) * glow(m, 26 * k)[..., None] * .9
        col += pc((1.0, .55, .95)) * fil[..., None] * 1.1
        col += pc((1.0, .7, .97)) * (m ** 2.5)[..., None] * .7
        ln = np.zeros((H, W), np.float32)
        for _ in range(int(40 * amp)):
            a = (px + rng.normal(0, rx * .42), py + rng.normal(0, ry * .42))
            ang = rng.uniform(0, 2 * np.pi)
            L = rng.uniform(16, 56)
            b = (a[0] + L * math.cos(ang), a[1] + L * math.sin(ang))
            poly(ln, disp(rng, a, b, 4, .8), k, rng.uniform(.6, 1.0), 1.3)
        ln *= e > .05
        col += pc((1.0, .85, .97)) * ln[..., None] * 1.0
        col += pc((1.0, .3, .85)) * glow(ln, 2.5 * k)[..., None] * 1.8
        col += pc((.9, .2, 1.0)) * glow(ln, 7 * k)[..., None] * 1.0
    return finish(col)


# ---------------------------------------------------------------- 岩
ROCK_CELL, ROCK_DPR, ROCK_N = 110.0, 2.0, 4


def rock(R, seed):
    """とんでくる 岩 1つ（暗い 紺・ごつごつ・うしろからの 水色の ふちの 光）→ premultiplied RGBA（2.6R の 四角）"""
    rng = np.random.default_rng(seed)
    S = int(R * 2.6)
    c = S / 2
    n = 11
    angs = np.sort(rng.uniform(0, 2 * np.pi, n))
    pts = [(c + math.cos(a) * R * rng.uniform(.6, 1.0), c + math.sin(a) * R * rng.uniform(.6, 1.0) * rng.uniform(.7, 1.0)) for a in angs]
    m = np.zeros((S * 4, S * 4), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(pts) * 4)], 255, cv2.LINE_AA)
    m = cv2.resize(m.astype(np.float32) / 255, (S, S), interpolation=cv2.INTER_AREA)
    rough = fbm(S, S, 9, seed + 3, 4)
    m = smoothstep(.45, .55, cv2.GaussianBlur(m, (0, 0), R * .05) + (rough - .5) * .25)
    din = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 5)
    hgt = np.sqrt(np.clip(din / (R * .8), 0, 1)) * R * .6 + (fbm(S, S, 6, seed + 5, 5) - .5) * R * .45
    gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8
    nz = 1 / np.sqrt(1 + gx * gx + gy * gy)
    nx, ny = -gx * nz, -gy * nz
    ld = np.array([.35, .55, .76])
    ndl = np.clip(nx * ld[0] + ny * ld[1] + nz * ld[2], 0, 1)
    col = pc((.03, .035, .09))[None, None, :] + pc((.08, .1, .25)) * ndl[..., None] ** 2
    # うしろからの 水色の ふちの 光
    rimz = smoothstep(R * .14, 0, din) * (m > .1)
    side = np.clip(-(nx * .3 + ny * .95), 0, 1)
    col += pc((.3, .8, 1.0)) * (rimz * (.5 + .8 * side))[..., None] * .9
    col = np.clip(col, 0, 1)
    out = np.dstack([col * m[..., None], m])
    return out


def rock_sheet():
    cell = int(ROCK_CELL * ROCK_DPR)
    sheet = np.zeros((cell, cell * ROCK_N, 4), np.float32)
    for j in range(ROCK_N):
        g = rock(cell / 2.6, 90 + 11 * j)
        g = cv2.resize(g, (cell, cell), interpolation=cv2.INTER_AREA)
        sheet[:, j * cell:(j + 1) * cell] = g
    return sheet

