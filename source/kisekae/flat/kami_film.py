"""神様的中 ① 赤い 嵐（第4.47版）：1コマずつ 描く 絵（パラパラ漫画）。1170×2532（iPhone の 画面の 画素）・1秒 30コマ・48コマ＝1.6秒
   色：まさちゃん「今青色のところを赤に変えて、紫色のところを金と白に変えられる？」→ 青・水色は 赤（kami_storm.pc）・紫と ピンク（雲・肩の 電気・ピンクの 雷）は 金と 白。
       PALETTE＝'blue' に すると はじめの 青い 嵐（下の 説明の 色は 青い 嵐の 時の 名前）
   まさちゃん「ここの手前までどうしても納得いかない。一度この一枚目の画像(画像のシーンも含み)より手前のシーンは削除して、作り直して！
   アプリで動かすのに問題がでない程度で、どれくらい細かく作れる？ … まずは48枚を一枚づつ描いて作成して！ 質感や光沢、動きなど精密に再現して！」
   → 送ってくれた 動画の コマは 描き写さない（ほかの 人の 作品の コピーに なる）。テンポと 明るさの 流れだけ 参考に して、形・構図・色は 姫の オリジナルで 1コマずつ 描く
     （まさちゃんが「オリジナルで1コマずつ」を えらんだ）
   流れ（0秒＝押した 瞬間）：
     0〜0.23秒 点火：光の 玉が はじけて ひろがる（光の 筋・電気・横に のびる 光・火花）→ まっ白
     0.2〜0.33秒 白が ひいて 嵐の 空・光の 滝が 上から おりて 床に 当たる（しぶき・床の 光の 輪）
     0.4〜0.63秒 ガラスの ドームが 床から ふくらむ（ふちが 光る）・0.43〜0.63秒 ピンクの 電気の 光・大きな 雷
     0.6〜1.4秒 嵐の 頂点：ドームの ふちの ジリジリと 肩の ピンクの 電気・大きな 雷・白い 光の 帯・とんでくる 岩・しぶき（ドームは ゆっくり 大きく）
     1.33〜1.6秒 金の 光が 集まって 金の 爆発（金の かけら・金の 粒・光の 筋）→ まっ白（② 金の 字へ）
   光は 足し算で 重ねて、明るい 所の にじみ（ブルーム）と、白く とぶ 前に ゆるやかに 頭うち（肩の ある 曲線）
   点めつ：強い 光は どの 点でも 1秒に 3回まで（大きな 白は はじめの 1回と さいごの 金→白 だけ。雷は 1本 2コマ・同じ 所は 1回）。画面ぜんたいは 動かさない（動くのは 光・ドーム・帯・岩）
   python3 flat/kami_film.py <出力フォルダ> [コマ番号（1〜48）…]  → f01.png〜f48.png（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami as KM
import kami_storm as KS
import kami_art as KA

S = 3.0                    # 画面の px → 絵の 画素
W, H = 1170, 2532
FPS, N = 30, 48
CX, BASE = KM.DOME2[0], KM.DOME2[1]

# ---------------------------------------------------------------- 時刻（秒）
T = dict(IGN=(0.0, .133, .2, .233, .367),       # 点火：はじまり・白が 出はじめ・まっ白・白が ひきはじめ・白が 消える
         COL=(.233, .367),                      # 光の 滝が おりる（上 → 床に 当たる）
         IMPACT=.367,                           # 床に 当たる
         DOME=(.42, .65, 1.333, 1.6),           # ドーム：ふくらみ はじめ・おわり・ゆっくり 大きく・おわり
         SURGE=(.45, .483, .55, .65),           # ピンクの 電気の 光
         CRACK=(.6, 1.4),                       # ドームの 電気
         GOLD=(1.333, 1.4, 1.467, 1.567))       # 金：光が 集まる・爆発・白が 出はじめ・まっ白
BOLTS = ((16, (14, 800), (382, 110), 'c'), (22, (376, 20), (356, 640), 'c'), (27, (40, -12), (100, 360), 'p'),
         (31, (330, -12), (236, 330), 'p'), (35, (14, 60), (34, 600), 'c'), (38, (160, -12), (286, 320), 'p'))
# 大きな 雷：(はじめの コマ（0から）, はじめ, おわり, 色)。1本 2コマ
RIBS = ((0, .24, 1.0), (1, .3, .9), (2, .56, 1.36), (5, .72, 1.2), (3, .9, 1.4), (4, 1.04, 1.4))
# 白い 光の 帯：(kami.py の RIBBONS の 番号, 出る 秒, 消える 秒)
ROCKS = ((.45, -1, 0), (.6, 1, 1), (.78, -1, 2), (.95, 1, 3), (1.12, -1, 0))
# 岩：(とび はじめ, 左右, 形の 番号)


def smoothstep(e0, e1, x):
    u = np.clip((x - e0) / (e1 - e0), 0, 1)
    return u * u * (3 - 2 * u)


def sstep(e0, e1, x):
    u = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


# ---------------------------------------------------------------- 道具
def fblur(img, sig):
    """大きな ぼかしは 小さく して ぼかす（速い）"""
    if sig <= 6:
        return cv2.GaussianBlur(img, (0, 0), sig)
    f = int(min(16, max(2, sig // 4)))
    h, w = img.shape[:2]
    sm = cv2.resize(img, (max(1, w // f), max(1, h // f)), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), sig / f)
    return cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR)


def place(dst, rgba, x, y, alpha=1.0):
    """premultiplied RGBA を (x, y)（絵の 画素・左上）に 重ねる"""
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x)), int(round(y))
    xs0, ys0 = max(0, X0), max(0, Y0)
    xs1, ys1 = min(W, X0 + w), min(H, Y0 + h)
    if xs1 <= xs0 or ys1 <= ys0:
        return
    sub = rgba[ys0 - Y0:ys1 - Y0, xs0 - X0:xs1 - X0]
    if alpha != 1.0:
        sub = sub * alpha
    dst[ys0:ys1, xs0:xs1] = sub[..., :3] + dst[ys0:ys1, xs0:xs1] * (1 - sub[..., 3:4])


def add_place(dst, rgb, x, y, gain=1.0):
    """光（RGB）を 足す"""
    h, w = rgb.shape[:2]
    X0, Y0 = int(round(x)), int(round(y))
    xs0, ys0 = max(0, X0), max(0, Y0)
    xs1, ys1 = min(W, X0 + w), min(H, Y0 + h)
    if xs1 <= xs0 or ys1 <= ys0:
        return
    dst[ys0:ys1, xs0:xs1] += rgb[ys0 - Y0:ys1 - Y0, xs0 - X0:xs1 - X0, :3] * gain


def warp_full(rgba, M):
    """sprite を 画面いっぱいへ 2x3 行列で うつす"""
    return cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def scale_about(s, cx, cy, ox=0.0, oy=0.0):
    """（絵の 中の 左上 ox, oy に ある sprite を）画面の (cx, cy) を 中心に s 倍"""
    return np.float32([[s, 0, cx - s * (cx - ox)], [0, s, cy - s * (cy - oy)]])


def motion_blur(img, dx, dy):
    """動きの ぶれ（dx, dy 画素 の 線で ぼかす）"""
    L = math.hypot(dx, dy)
    if L < 1.5:
        return img
    n = int(math.ceil(L)) | 1
    k = np.zeros((n, n), np.float32)
    c = n // 2
    cv2.line(k, (int(round(c - dx / 2)), int(round(c - dy / 2))), (int(round(c + dx / 2)), int(round(c + dy / 2))), 1.0, 1, cv2.LINE_AA)
    k /= k.sum()
    pad = c + 1
    big = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    out = cv2.filter2D(big, -1, k)
    return out


def sprite_to_screen(spr, M, vx=0.0, vy=0.0):
    """sprite を 行列 M で 画面へ。動きの ぶれ（画面の 画素 vx, vy）は sprite の 中で かけて から うつす（速い）"""
    if math.hypot(vx, vy) > 1.5:
        A = np.array(M[:, :2], np.float64)
        v = np.linalg.solve(A, np.array([vx, vy]))
        b = motion_blur(spr, float(v[0]), float(v[1]))
        pad = (b.shape[0] - spr.shape[0]) // 2
        M2 = M.copy()
        M2[:, 2] -= A @ np.array([pad, pad])
        return warp_full(b, np.float32(M2))
    return warp_full(spr, M)


def lines_mask(polys, width, val=1.0, shape=(H, W)):
    """点の 列（画面の px）を 絵の 画素で 細い 線に"""
    m = np.zeros(shape, np.float32)
    for pts, v in polys:
        if len(pts) < 2:
            continue
        q = np.int32(np.round(np.array(pts) * S * 8))
        cv2.polylines(m, [q], False, float(v * val), max(1, int(round(width * S))), cv2.LINE_AA, shift=3)
    return m


def glow_add(dst, mask, layers):
    """mask の 光を 色ごとの ぼかしで 足す：layers＝[(ぼかし（画面の px）, 色, 強さ)]（ぼかし 0 は しん）"""
    for sig, col, g in layers:
        m = mask if sig <= 0 else fblur(mask, sig * S)
        dst += m[..., None] * (KS.pc(col) * g)


def bloom(img):
    """明るい 所の にじみ"""
    lum = img.max(-1)
    br = img * (np.clip(lum - .62, 0, None) / np.maximum(lum, 1e-4))[..., None]
    out = img.copy()
    for sig, g in ((4, .35), (14, .3), (40, .25)):
        out += fblur(br, sig * S) * g
    return out


def tonemap(img):
    """白く とぶ 前に ゆるやかに 頭うち（.8 から 上を やわらかく）"""
    x0 = .8
    y = np.where(img < x0, img, 1 - (1 - x0) * np.exp(-(img - x0) / (1 - x0)))
    return np.clip(y, 0, 1)


# ---------------------------------------------------------------- 線の 形（雷・電気）
def bolt_polys(seed, a, b, branches=9, rough=None):
    """大きな 雷の 線（本線・えだ・小えだ）→ [(点の 列, 明るさ)]"""
    rng = random.Random(seed)
    R = rough or KM.BOLT_ROUGH
    main = KM._disp_ms(rng, a, b, R)
    out = [(main, 1.0)]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    base = math.atan2(b[1] - a[1], b[0] - a[0])
    for _ in range(branches):
        i = rng.randint(len(main) // 8, len(main) * 7 // 8)
        p = main[i]
        ang = base + rng.choice((-1, 1)) * rng.uniform(.35, .9)
        ln = rng.uniform(.1, .3) * L
        br = KM._disp_ms(rng, p, (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang)), R[1:])
        out.append((br, .75))
        if rng.random() < .6:
            j = rng.randint(len(br) // 4, len(br) * 3 // 4)
            p2 = br[j]
            a2 = ang + rng.choice((-1, 1)) * rng.uniform(.3, .8)
            l2 = ln * rng.uniform(.3, .55)
            out.append((KM._disp_ms(rng, p2, (p2[0] + l2 * math.cos(a2), p2[1] + l2 * math.sin(a2)), R[3:]), .55))
    return out


def ray_polys(rng, c, n, r0, r1, rough=.35):
    """まん中から 外へ はしる 電気（点火）"""
    out = []
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        p0 = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a))
        ln = r1 * rng.uniform(.5, 1.0)
        p1 = (c[0] + ln * math.cos(a), c[1] + ln * math.sin(a))
        out.append((KM._disp_ms(rng, p0, p1, (rough * .6, rough, rough * 1.4, rough * 1.6, rough * 1.6)), rng.uniform(.6, 1.0)))
    return out


# ---------------------------------------------------------------- 動かない 絵（1回だけ 作る）
_C = {}


def cache(name, fn):
    if name not in _C:
        _C[name] = fn()
    return _C[name]


PALETTE = 'red'      # 色の くみ（第4.47版：まさちゃん「今青色のところを赤に変えて、紫色のところを金と白に変えられる？」）。'blue'＝はじめの 青い 嵐
SKY_DIM = .72        # 空の 明るさ（光の 物が 映える ように 少し 暗く）


def sky0():
    return cache('sky0', lambda: KS.storm_bg(W, H, falls=0.0).astype(np.float32) * SKY_DIM)


def sky_falls():
    def f():
        s1 = KS.storm_bg(W, H, falls=1.0).astype(np.float32)
        return s1 - sky0()
    return cache('skyf', f)


def veins(j):
    return cache(f'vein{j}', lambda: KS.veins(4 + j, k=S).astype(np.float32))


def fall_tile():
    return cache('ftile', lambda: KS.fall_tile2(k=S).astype(np.float32))


def fall_mask():
    return cache('fmask', lambda: KS.fall_mask(k=S).astype(np.float32))


def dome_img():
    return cache('dome', lambda: KS.dome_glass(k=S, gloss=True).astype(np.float32))


def surge_img():
    return cache('surge', lambda: KS.surge(k=S).astype(np.float32))


def ribbon_img(j):
    def f():
        p = KM.RIBBONS[j][0]
        return KS.ribbon(p, 500 + 7 * j, k=S).astype(np.float32)
    return cache(f'rib{j}', f)


def rock_img(j):
    return cache(f'rock{j}', lambda: KS.rock(130.0, 90 + 11 * j).astype(np.float32))


# ---------------------------------------------------------------- ① 点火
IGN_C = (195.0, 392.0)


_IGN = {}


def ign_arcs():
    """点火の 電気（1回だけ 作る：コマごとに 先へ のびる。同じ 所で ついたり 消えたり しない）"""
    if not _IGN:
        rng = random.Random(100)
        _IGN['arcs'] = ray_polys(rng, IGN_C, 16, 6, 520, .3)
    return _IGN['arcs']


def grow_poly(pts, f):
    """線の 前から f（0〜1）だけ"""
    n = max(2, int(len(pts) * f))
    return pts[:n]


def ignition(img, t):
    """光の 玉が はじけて ひろがる：白い しん・光の 筋（水色・紫・白）・まわりへ のびる 電気・横に のびる 光・火花"""
    t0, t1, t2, t3, t4 = T['IGN']
    if t > t3 + .02:
        return
    u = min(1.0, t / t2)
    cx, cy = IGN_C
    X = (np.arange(W, dtype=np.float32)[None, :] / S) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / S) * np.ones((1, W), np.float32)
    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    rc = 4 + 260 * u ** 2.6
    core = np.exp(-(d / rc) ** 2) * 2.6 + np.exp(-(d / (rc * 2.4)) ** 2) * .8
    img += core[..., None] * KS.pc((1.0, 1.0, 1.0))
    img += np.exp(-(d / (rc * 4.5 + 30)) ** 2)[..., None] * KS.pc((.3, .55, 1.0)) * (.5 + .6 * u)
    # 光の 筋（まん中から 外へ のびる）
    rng = np.random.default_rng(11)
    ang = np.arctan2(Y - cy, X - cx)
    rays = np.zeros((H, W), np.float32)
    for k in range(70):
        a0 = rng.uniform(-np.pi, np.pi)
        wd = rng.uniform(.004, .028)
        da = np.angle(np.exp(1j * (ang - a0)))
        ln = (20 + 950 * u ** 1.4) * rng.uniform(.4, 1.0)
        rays = np.maximum(rays, np.exp(-(da / wd) ** 2) * np.clip(1 - d / ln, 0, 1) ** 1.5 * rng.uniform(.4, 1.0))
    img += rays[..., None] * KS.pc((.75, .9, 1.0)) * (.9 + 1.4 * u)
    tint = np.exp(-((ang - 2.4) / .7) ** 2) + np.exp(-((ang + .9) / .6) ** 2)
    img += (rays * tint)[..., None] * KS.pc((.7, .2, 1.0)) * 1.3
    # 横に のびる 光（細い）
    hs = np.exp(-((Y - cy) / (1.0 + 2.5 * u)) ** 2) * np.exp(-((X - cx) / (30 + 700 * u ** 1.3)) ** 2)
    img += hs[..., None] * KS.pc((.6, .95, 1.0)) * (1.2 + 2 * u)
    # まわりへ のびる 電気（先へ のびる だけ）
    polys = [(grow_poly(p, min(1.0, .15 + 1.1 * u)), v) for p, v in ign_arcs()]
    m = lines_mask(polys, 1.1)
    glow_add(img, m, ((0, (1, 1, 1), 1.1), (1.2, (.55, .85, 1.0), 1.4), (5, (.5, .3, 1.0), 1.2)))
    # 火花（外へ とぶ・すじ）
    sp = np.zeros((H, W), np.float32)
    r3 = random.Random(7)
    for _ in range(140):
        a = r3.uniform(0, 2 * math.pi)
        v = r3.uniform(500, 2200)
        r0 = r3.uniform(4, 30)
        dist = r0 + v * t
        tail = 10 + v * .025
        p0 = (cx + (dist - tail) * math.cos(a), cy + (dist - tail) * math.sin(a))
        p1 = (cx + dist * math.cos(a), cy + dist * math.sin(a))
        cv2.line(sp, (int(p0[0] * S * 4), int(p0[1] * S * 4)), (int(p1[0] * S * 4), int(p1[1] * S * 4)), float(r3.uniform(.5, 1.0)), 2, cv2.LINE_AA, shift=2)
    glow_add(img, sp, ((0, (1, .95, .9), 1.0), (2, (.5, .8, 1.0), 1.2)))


def white_level(t):
    """画面の 白（点火の 白 と 金 → 白）"""
    t0, t1, t2, t3, t4 = T['IGN']
    w = 0.0
    if t1 <= t <= t4:
        w = sstep(t1, t2, t) if t < t3 else 1 - sstep(t3, t4, t)
    g0, g1, g2, g3 = T['GOLD']
    w = max(w, sstep(g2, g3, t))
    return w


# ---------------------------------------------------------------- 嵐の 空・光の 滝
def storm(img, t):
    """嵐の 空（電気の もや・雲・床）＋光の 滝（上から おりる → 落ちつづける すじ）"""
    img += sky0()
    # まわりの 電気の 脈（2まいが ゆっくり かわるがわる）
    a = .5 + .25 * math.sin(2 * math.pi * t / 1.8)
    for j, wgt in ((1, a), (2, .9 - a)):
        v = veins(j)
        img[:] = v[..., :3] * wgt + img * (1 - v[..., 3:4] * wgt)
    c0, c1 = T['COL']
    if t < c0:
        return
    head = -40 + (BASE + 60) * ease_out((t - c0) / (c1 - c0)) ** .9      # 光の 滝の 先
    Y = (np.arange(H, dtype=np.float32)[:, None] / S)
    reveal = smoothstep(head + 30, head - 60, Y)                        # 先より 上だけ
    img += sky_falls() * reveal[..., None]
    # すじ（2まい：速さ ちがい）
    tile = fall_tile()
    fm = fall_mask()
    fx, fy, fw, fh = KS.FALL_BOX
    X0, Y0 = int(round(fx * S)), int(round(fy * S))
    th, tw = tile.shape[:2]
    hh, ww = fm.shape
    for spd, scl, g in ((1.0, 1.0, 1.0), (.55, 1.45, .5)):
        tl = tile if scl == 1.0 else cv2.resize(tile, (int(tw * scl), int(th * scl)), interpolation=cv2.INTER_LINEAR)
        ty = tl.shape[0]
        off = int(round(t * 900 * S * spd)) % ty
        reps = hh // ty + 3
        col = np.concatenate([tl] * reps, 0)[ty - off:ty - off + hh]
        cw = col.shape[1]
        if cw >= ww:
            x0 = (cw - ww) // 2
            col = col[:, x0:x0 + ww]
        else:
            pad = (ww - cw) // 2
            col = cv2.copyMakeBorder(col, 0, 0, pad, ww - cw - pad, cv2.BORDER_CONSTANT, value=0)
        rv = reveal[Y0:Y0 + hh] if Y0 >= 0 else np.concatenate([np.zeros((-Y0, 1), np.float32), reveal[:hh + Y0]], 0)
        m = (fm * rv[:hh, :1])[..., None] * g
        place(img, col * m, X0, Y0)
    # 光の 滝の 先の 光（おりて いる 間）
    if t < c1 + .05:
        hy = min(head, BASE)
        X = (np.arange(W, dtype=np.float32)[None, :] / S)
        dy = (Y - hy)
        fl = np.exp(-((X - CX) / 70) ** 2) * np.exp(-(dy / 26) ** 2) * (1 - sstep(c1, c1 + .05, t))
        img += fl[..., None] * KS.pc((.7, .95, 1.0)) * 1.6


def impact(img, t):
    """床に 当たる：光（せまい 所）・床の 光の 輪・しぶき"""
    t0 = T['IMPACT']
    if t < t0:
        return
    u = t - t0
    X = (np.arange(W, dtype=np.float32)[None, :] / S) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / S) * np.ones((1, W), np.float32)
    if u < .2:
        g = math.exp(-u / .07)
        fl = np.exp(-(((X - CX) / (90 + 300 * u)) ** 2 + ((Y - BASE + 6) / (26 + 60 * u)) ** 2))
        img += fl[..., None] * KS.pc((.75, .97, 1.0)) * 1.6 * g
    if u < .5:
        r = 20 + 520 * ease_out(u / .5)
        ring = np.exp(-((np.sqrt(((X - CX) / r) ** 2 + ((Y - BASE - 2) / (r * .12)) ** 2) - 1) * r / 5) ** 2)
        img += ring[..., None] * KS.pc((.5, .9, 1.0)) * .9 * (1 - u / .5)
    # しぶき（光の 粒が 上と 左右へ とぶ・すじ）
    sp = np.zeros((H, W), np.float32)
    rng = random.Random(21)
    for _ in range(170):
        b0 = t0 + rng.uniform(0, 1.2)
        age = t - b0
        life = rng.uniform(.3, .6)
        if not (0 <= age <= life):
            continue
        a = rng.uniform(-math.pi * .95, -math.pi * .05)
        v = rng.uniform(120, 420)
        x0 = CX + rng.gauss(0, 34)
        vx, vy = math.cos(a) * v * 1.3, math.sin(a) * v
        x = x0 + vx * age
        y = BASE - 4 + vy * age + 700 * age * age
        tx, ty = x - vx * .02, y - (vy + 1400 * age) * .02
        cv2.line(sp, (int(tx * S * 4), int(ty * S * 4)), (int(x * S * 4), int(y * S * 4)), float(1 - age / life), 3, cv2.LINE_AA, shift=2)
    glow_add(img, sp, ((0, (.9, 1, 1), .9), (2, (.4, .85, 1.0), 1.1)))


# ---------------------------------------------------------------- ドーム
def dome_scale(t):
    d0, d1, d2, d3 = T['DOME']
    if t < d0:
        return 0.0
    if t < d1:
        return .06 + .94 * ease_out((t - d0) / (d1 - d0))
    if t < d2:
        return 1.0 + .15 * (t - d1) / (d2 - d1)
    return 1.15 + .03 * min(1.0, (t - d2) / (d3 - d2))


def dome(img, t):
    s = dome_scale(t)
    if s <= 0:
        return
    d0, d1 = T['DOME'][:2]
    dm = dome_img()
    x0, y0, bw, bh = KS.dome_box()
    M = scale_about(s, CX * S, BASE * S, x0 * S, y0 * S)
    full = warp_full(dm, M)
    fade = sstep(d0, d0 + .04, t)
    img[:] = full[..., :3] * fade + img * (1 - full[..., 3:4] * fade)
    # ふくらむ 間は ふちが 強く 光る
    e = 1 - sstep(d1, d1 + .12, t)
    if e > 0:
        OL = KM.dome_outline(400)
        pts = [(CX + (x - CX) * s, BASE + (y - BASE) * s) for x, y, nx, ny, u in OL]
        m = lines_mask([(pts, 1.0)], 2.2)
        glow_add(img, m, ((0, (1, 1, 1), .9 * e), (2, (.5, .9, 1.0), 1.4 * e), (8, (.3, .6, 1.0), 1.2 * e)))


def dome_pt(p, s):
    return (CX + (p[0] - CX) * s, BASE + (p[1] - BASE) * s)


_EL = {}


def elec_events():
    """ドームの 電気の コマごとの 形（はじめに まとめて 作る：乱数の 順を 決めて おく）"""
    if _EL:
        return _EL
    c0, c1 = T['CRACK']
    f0, f1 = int(math.ceil(c0 * FPS)), int(c1 * FPS)
    OL = KM.dome_outline()
    rng = random.Random(77)
    clusters, arcs = [], []
    for f in range(f0, f1 + 1):
        k = f - f0
        for _ in range(3):
            clusters.append((f, crackle_pts(rng, OL, k)))
        if k % 3 == 0:
            side = 1 if (k // 3) % 2 else -1
            pts = KM.surface_arc(rng, side)
            arcs.append((f, pts, arc_br(rng, pts), rng.choice('cv')))
    _EL.update(f0=f0, f1=f1, cl=clusters, arcs=arcs, OL=OL)
    return _EL


def crackle_pts(rng, OL, k):
    N_ = len(OL)
    while True:
        o = rng.random()
        x, y, nx, ny, u = OL[int(o * (N_ - 1))]
        if u > .3 and KM._spread_ok(o, k):
            break
    dep = rng.uniform(5, 40)
    c = (x - nx * dep, y - ny * dep)
    polys = []
    a0 = rng.uniform(0, 2 * math.pi)
    for j in range(rng.randint(3, 5)):
        a = a0 + j * 2.1 + rng.uniform(-.5, .5)
        ln = rng.uniform(10, 30)
        p0 = (c[0] + rng.uniform(-3, 3), c[1] + rng.uniform(-3, 3))
        main = KM._disp_ms(rng, p0, (p0[0] + ln * math.cos(a), p0[1] + ln * math.sin(a)), KM.CRK_ROUGH)
        polys.append((main, 1.0))
        if rng.random() < .7:
            q = main[rng.randint(1, len(main) - 2)]
            a2 = a + rng.choice((-1, 1)) * rng.uniform(.5, 1.2)
            l2 = ln * rng.uniform(.3, .55)
            polys.append((KM._disp_ms(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), KM.CRK_ROUGH[1:]), .8))
    return c, polys


def arc_br(rng, main):
    out = []
    for _ in range(rng.randint(3, 6)):
        p = main[rng.randint(len(main) // 8, len(main) * 7 // 8)]
        a = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(8, 30)
        out.append((KM._disp(rng, p, (p[0] + ln * math.cos(a), p[1] + ln * math.sin(a)), 3, .6), .7))
    return out


def twitch_polys(rng, pts, n, lo=4, hi=10):
    out = []
    for _ in range(n):
        p = pts[rng.randrange(len(pts))]
        a = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(lo, hi)
        out.append((KM._disp(rng, p, (p[0] + ln * math.cos(a), p[1] + ln * math.sin(a)), 2, .9), .8))
    return out


def dome_elec(img, t, fi):
    """ドームの 電気（ドームと いっしょに 大きく）：ふちの ジリジリ・肩の ピンクの 電気・表面を はしる 電気"""
    E = elec_events()
    if not (E['f0'] <= fi <= E['f1']):
        return
    s = dome_scale(t)
    k = fi - E['f0']
    rng = random.Random(900 + fi)
    OL = E['OL']
    sizz = []
    N_ = len(OL)
    c = 0
    while c < 18:
        o = rng.random()
        if not KM._spread_ok(o, k):
            continue
        x, y, nx, ny, u = OL[int(o * (N_ - 1))]
        ang = math.atan2(ny, nx) + rng.uniform(-1.2, 1.2)
        ln = rng.uniform(4, 12)
        p0 = (x + nx * rng.uniform(-2, 2), y + ny * rng.uniform(-2, 2))
        sizz.append((KM._disp(rng, p0, (p0[0] + ln * math.cos(ang), p0[1] + ln * math.sin(ang)), 2, .9), 1.0))
        c += 1
    pink, arcs_c, arcs_v = [], [], []
    for f0, (cc, polys) in E['cl']:
        if f0 <= fi < f0 + 4:
            pink += polys + twitch_polys(rng, [cc], 1, 3, 8)
    for f0, pts, br, tone in E['arcs']:
        if f0 <= fi < f0 + 4:
            (arcs_c if tone == 'c' else arcs_v).extend([(pts, 1.0)] + br + twitch_polys(rng, pts, 2))

    def tr(polys):
        return [([dome_pt(p, s) for p in pts], v) for pts, v in polys]
    m = lines_mask(tr(sizz), .9)
    glow_add(img, m, ((0, (1, 1, 1), 1.0), (.8, (.6, .95, 1.0), 1.0), (3, (.3, .75, 1.0), .5)))
    m = lines_mask(tr(pink), 1.0)
    glow_add(img, m, ((0, (1, .9, .98), 1.0), (.9, (1.0, .45, .9), 1.3), (3.5, (1.0, .2, .8), .8)))
    for polys, col in ((arcs_c, (.6, .95, 1.0)), (arcs_v, (.75, .65, 1.0))):
        if polys:
            m = lines_mask(tr(polys), 1.1)
            glow_add(img, m, ((0, (1, 1, 1), 1.0), (1, col, 1.2), (4, col, .5)))


def surge(img, t):
    s0, s1, s2, s3 = T['SURGE']
    if not (s0 <= t <= s3):
        return
    a = sstep(s0, s1, t) if t < s1 else (1.0 if t < s2 else 1 - sstep(s2, s3, t))
    sg = surge_img()
    img[:] = sg[..., :3] * a + img * (1 - sg[..., 3:4] * a)


# ---------------------------------------------------------------- 大きな 雷
def big_bolts(img, fi):
    for k, (f0, a, b, tone) in enumerate(BOLTS):
        if not (f0 <= fi <= f0 + 1):
            continue
        g = 1.0 if fi == f0 else .55
        polys = bolt_polys(700 + k * 13, a, b)
        m = lines_mask(polys, 2.2)
        if tone == 'c':
            lay = ((0, (1, 1, 1), 1.2 * g), (1.6, (.75, .95, 1.0), 1.2 * g), (6, (.4, .75, 1.0), 1.0 * g), (18, (.3, .5, 1.0), .7 * g))
        else:
            lay = ((0, (1, .95, 1), 1.2 * g), (1.6, (1.0, .6, .95), 1.2 * g), (6, (.95, .3, 1.0), 1.0 * g), (18, (.6, .2, 1.0), .7 * g))
        glow_add(img, m, lay)


# ---------------------------------------------------------------- 白い 光の 帯
def ribbons(img, t):
    for j, t0, t1 in RIBS:
        if not (t0 <= t <= t1):
            continue
        rb = ribbon_img(j)
        x0, y0, bw, bh = KS.ribbon_box(KM.RIBBONS[j][0])
        u = (t - t0) / .13                       # 0.13秒で 上から すべりこむ
        dy = -170 * (1 - ease_out(u)) if u < 1 else 0.0
        sway = 3 * math.sin(2 * math.pi * (t - t0) / 1.3)
        fade = 1 - sstep(t1 - .2, t1, t)
        inn = sstep(0, .5, u)
        a = fade * inn
        if a <= 0:
            continue
        spr = rb
        if u < 1:
            vy = 170 * 3 * (1 - u) ** 2 / .13 / FPS * .6        # このコマの 動き（画素）
            spr = motion_blur(rb, 0, vy * S)
            pad = (spr.shape[0] - rb.shape[0]) // 2
            place(img, spr * a, (x0 + sway) * S - pad, (y0 + dy) * S - pad)
        else:
            place(img, spr * a, (x0 + sway) * S, (y0 + dy) * S)


# ---------------------------------------------------------------- 岩
def rocks(img, t):
    rng = random.Random(9)
    for k, (t0, side, j) in enumerate(ROCKS):
        x0, y0 = 195 + side * rng.uniform(20, 70), rng.uniform(330, 520)
        dx, dy = side * rng.uniform(220, 300), rng.uniform(-300, 140)
        dur = rng.uniform(.42, .5)
        rot = side * rng.uniform(70, 160)
        s1 = rng.uniform(1.3, 1.9)
        if not (t0 <= t <= t0 + dur):
            continue

        def pos(tt):
            u = min(1.0, max(0.0, (tt - t0) / dur))
            e = u ** 1.6
            return x0 + dx * e, y0 + dy * e, .3 + (s1 - .3) * e, rot * e, u
        x, y, sc, r, u = pos(t)
        xp, yp, _, _, _ = pos(t - .5 / FPS)
        spr = rock_img(j)
        hh, ww = spr.shape[:2]
        M = cv2.getRotationMatrix2D((ww / 2, hh / 2), -r, sc * .85)
        M[0, 2] += x * S - ww / 2
        M[1, 2] += y * S - hh / 2
        full = sprite_to_screen(spr, np.float32(M), (x - xp) * S, (y - yp) * S)
        a = sstep(0, .12, u)
        img[:] = full[..., :3] * a + img * (1 - full[..., 3:4] * a)


# ---------------------------------------------------------------- 金の 爆発
def gold_shard(R, seed):
    """金の かけら（面の ある 結晶）：面ごとに 金の 映りこみの グラデーション・左上からの 光・面取りの 光る ふち・こい ふち・キラッ → premultiplied RGBA（2.4R の 四角）"""
    rng = np.random.default_rng(seed)
    Sz = int(R * 2.4)
    c = np.array([Sz / 2, Sz / 2])
    n = int(rng.integers(5, 8))
    angs = np.sort(rng.uniform(0, 2 * np.pi, n))
    sq = rng.uniform(.5, .9)
    pts = np.array([c + np.array([math.cos(a), math.sin(a) * sq]) * R * rng.uniform(.6, 1.0) for a in angs])
    apex = c + rng.normal(0, R * .15, 2)
    img = np.zeros((Sz, Sz, 4), np.float32)
    ld = np.array([-.5, -.7, .5])
    ld /= np.linalg.norm(ld)
    yy, xx = np.mgrid[0:Sz, 0:Sz].astype(np.float32)
    best = None
    for i in range(n):
        tri = np.array([apex, pts[i], pts[(i + 1) % n]])
        mid = tri.mean(0) - c
        nrm = np.array([mid[0] / R * 1.2, mid[1] / R * 1.2, .7 + rng.uniform(-.2, .2)])
        nrm /= np.linalg.norm(nrm)
        lv = max(0.0, float(nrm @ ld))
        # 面の 中の 映りこみ（ななめの グラデーション）
        dirv = rng.normal(0, 1, 2)
        dirv /= np.linalg.norm(dirv) + 1e-6
        g = ((xx - c[0]) * dirv[0] + (yy - c[1]) * dirv[1]) / R
        tt = np.clip(.45 - .45 * lv + .25 * g, 0, 1)
        col = KA.ramp(tt, KA.GOLD) * (.78 + .55 * lv)
        m = np.zeros((Sz * 4, Sz * 4), np.uint8)
        cv2.fillPoly(m, [np.int32(tri * 4 * 4)], 255, cv2.LINE_AA, shift=2)
        m = cv2.resize(m.astype(np.float32) / 255, (Sz, Sz), interpolation=cv2.INTER_AREA)
        img[..., :3] = img[..., :3] * (1 - m[..., None]) + col * m[..., None]
        img[..., 3] = np.maximum(img[..., 3], m)
        if best is None or lv > best[0]:
            best = (lv, tri.mean(0))
    # 面取りの 光る ふち（面の さかい）と 外の こい ふち
    edge = np.zeros((Sz, Sz), np.float32)
    for p_ in pts:
        cv2.line(edge, (int(apex[0] * 4), int(apex[1] * 4)), (int(p_[0] * 4), int(p_[1] * 4)), .8, max(1, int(R * .035)), cv2.LINE_AA, shift=2)
    cv2.polylines(edge, [np.int32(np.vstack([pts, pts[:1]]) * 4)], False, 1.0, max(1, int(R * .05)), cv2.LINE_AA, shift=2)
    edge = cv2.GaussianBlur(edge, (0, 0), max(.6, R * .015)) * (img[..., 3] > .05)
    img[..., :3] += edge[..., None] * KS.pc((1.0, .95, .75)) * .75
    outl = np.clip(KA.grow(img[..., 3], max(1.0, R * .025)) - img[..., 3], 0, 1)
    img[..., :3] = img[..., :3] * img[..., 3:4] + np.array(KA.EDGE, np.float32) / 255 * outl[..., None]
    img[..., 3] = np.clip(img[..., 3] + outl, 0, 1)
    # キラッ（いちばん 光る 面に）
    gx, gy = best[1] + rng.normal(0, R * .08, 2)
    spot = np.exp(-(((xx - gx) ** 2 + (yy - gy) ** 2) / (2 * (R * .09) ** 2)))
    star = np.zeros((Sz, Sz), np.float32)
    L = R * .45
    cv2.line(star, (int((gx - L) * 4), int(gy * 4)), (int((gx + L) * 4), int(gy * 4)), 1.0, max(1, int(R * .02)), cv2.LINE_AA, shift=2)
    cv2.line(star, (int(gx * 4), int((gy - L) * 4)), (int(gx * 4), int((gy + L) * 4)), 1.0, max(1, int(R * .02)), cv2.LINE_AA, shift=2)
    star = cv2.GaussianBlur(star, (0, 0), max(.8, R * .012)) * np.exp(-(((xx - gx) ** 2 + (yy - gy) ** 2) / (2 * (R * .25) ** 2)))
    gl = np.clip(spot * 1.2 + star, 0, 1.5)
    img[..., :3] += gl[..., None] * KS.pc((1.0, .98, .9))
    img[..., 3] = np.clip(np.maximum(img[..., 3], np.clip(gl, 0, 1)), 0, 1)
    return img


_GP = {}


def gold_polar():
    """金の 炎の 輪の もよう（まわりに つながる ノイズ：角度 1024 × はば 256）"""
    if not _GP:
        N_ = 1024
        tex = KS.fbm(256, 2 * N_, 10, 401, 5, .55)
        w_ = np.linspace(0, 1, N_, endpoint=False, dtype=np.float32)[None, :]
        tex = tex[:, N_:] * (1 - w_) + tex[:, :N_] * w_
        _GP['t'] = ((tex - tex.mean()) / (tex.std() + 1e-6)).astype(np.float32)
    return _GP['t']


def gold_assets():
    def f():
        shards = [gold_shard(140.0, 300 + j) for j in range(8)]
        nug = [KA.nugget(60.0, 70 + j * 7).astype(np.float32) for j in range(4)]
        blast = KA.gold_blast(1600).astype(np.float32)
        return shards, nug, blast
    return cache('gold', f)


GOLD_C = (195.0, 470.0)


def over_col(img, alpha, col):
    """色 col を alpha で 上に ぬる（足さない：下の 青と まざって 白く ならない）"""
    a = np.clip(alpha, 0, 1)[..., None]
    img[:] = img * (1 - a) + np.asarray(col, np.float32) * a


def gold(img, t):
    """金：まん中に 金の 光が 集まる（光の 筋）→ 金の 炎が ひろがり、金の 炎の 輪が 外へ・金の かけらと 金の 粒が とぶ（回る・ぶれ）。
       金は 上に ぬる（青い 光に 足すと 白く なって 金に 見えない）"""
    g0, g1, g2, g3 = T['GOLD']
    if t < g0:
        return
    shards, nug, blast = gold_assets()
    gx, gy = GOLD_C
    X = (np.arange(W, dtype=np.float32)[None, :] / S) * np.ones((H, 1), np.float32)
    Y = (np.arange(H, dtype=np.float32)[:, None] / S) * np.ones((1, W), np.float32)
    d = np.sqrt((X - gx) ** 2 + (Y - gy) ** 2)
    ang = np.arctan2(Y - gy, X - gx)
    u = sstep(g0, g1 + .03, t)
    v = max(0.0, t - g1)
    # 金の 光（まわりは 金を ぬる・まん中だけ 白く 光る）
    rc = 8 + 30 * u + 60 * sstep(0, .1, v)
    over_col(img, np.exp(-(d / (rc * 3.2)) ** 2) * (.55 + .3 * u), (1.0, .7, .2))
    over_col(img, np.exp(-(d / (rc * 1.4)) ** 2) * .9, (1.0, .86, .45))
    img += (np.exp(-(d / (rc * .5)) ** 2) * 1.3)[..., None] * KS.pc((1.0, .97, .85))
    # 金の 光の 筋（ゆっくり 回る）
    rng = np.random.default_rng(31)
    rays = np.zeros((H, W), np.float32)
    rot = (t - g0) * .5
    for k in range(40):
        a0 = rng.uniform(-np.pi, np.pi) + rot
        wd = rng.uniform(.005, .02)
        da = np.angle(np.exp(1j * (ang - a0)))
        ln = (60 + 420 * u + 520 * sstep(0, .15, v)) * rng.uniform(.4, 1.0)
        rays = np.maximum(rays, np.exp(-(da / wd) ** 2) * np.clip(1 - d / ln, 0, 1) ** 1.3 * rng.uniform(.5, 1.0))
    over_col(img, rays * .75, (1.0, .84, .42))
    if t < g1:
        return
    # 金の 炎（上に ぬる・ひろがる）
    sc = (.18 + .95 * ease_out(v / .17)) * W / 1600 * 1.15
    M = np.float32([[sc, 0, gx * S - 800 * sc], [0, sc, gy * S - 800 * sc]])
    full = warp_full(blast, M)
    img[:] = full[..., :3] + img * (1 - full[..., 3:4])
    # 金の 炎の 輪（外へ ひろがる）
    r = 30 + 560 * ease_out(v / .2)
    th = 10 + 46 * min(1.0, v / .2)
    tex = gold_polar()
    pa = ((ang + np.pi) / (2 * np.pi) * 1024) % 1024
    pr = np.clip((d - r) / (th * 3) * 64 + 128, 0, 255)
    nz = cv2.remap(tex, pa.astype(np.float32), pr.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    edge = d - r + nz * th * .6
    ring = np.exp(-(edge / th) ** 2) * (1 - .3 * min(1.0, v / .2))
    inner = np.clip(1 - np.abs(edge + th * .5) / (th * .45), 0, 1)
    over_col(img, ring * .85, (1.0, .6, .12))
    over_col(img, inner * .9, (1.0, .9, .55))
    # 金の かけらと 金の 粒（外へ とぶ・回る・ぶれ・だんだん 大きく）
    r2 = random.Random(55)
    items = []
    for k in range(26):
        a_ = 2 * math.pi * k / 26 + r2.uniform(-.12, .12)
        sp = r2.uniform(380, 900)
        items.append((r2.uniform(.6, 1.2), a_, sp, r2.uniform(0, 360), r2.uniform(-420, 420), k % 3 != 2, k))
    for s0, a_, sp, rot0, rs, is_sh, k in sorted(items, key=lambda q: q[0]):
        dist = 40 + sp * v * 1.15
        x, y = gx + dist * math.cos(a_), gy + dist * math.sin(a_) + 120 * v * v
        spr = shards[k % len(shards)] if is_sh else nug[k % len(nug)]
        hh, ww = spr.shape[:2]
        scl = s0 * (.5 + 1.3 * min(1.0, v / .16)) * (1.0 if is_sh else 1.05)
        Mr = cv2.getRotationMatrix2D((ww / 2, hh / 2), rot0 + rs * v, scl)
        Mr[0, 2] += x * S - ww / 2
        Mr[1, 2] += y * S - hh / 2
        full = sprite_to_screen(spr, np.float32(Mr), sp * math.cos(a_) / FPS * .5 * S, sp * math.sin(a_) / FPS * .5 * S)
        img[:] = full[..., :3] + img * (1 - full[..., 3:4])


# ---------------------------------------------------------------- ぬれた 床の 映りこみ
def floor_reflect(img, t):
    """床（ぬれた 青）に 上の 光が 映る（さかさま・ぼかし・横に ゆれる 波）"""
    b = int(BASE * S) + 4
    hgt = H - b
    src = img[b - hgt:b][::-1].copy()
    src = cv2.GaussianBlur(src, (0, 0), 2.2 * S)
    yy, xx = np.mgrid[0:hgt, 0:W].astype(np.float32)
    rip = (np.sin(yy / (5.0 * S) + t * 9) * 1.5 + np.sin(yy / (2.3 * S) - t * 13 + xx / (40 * S)) * .8) * S * (yy / hgt + .2)
    src = cv2.remap(src, xx + rip, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fade = np.exp(-yy / (55 * S))[..., None]
    img[b:] += src * fade * .3


# ---------------------------------------------------------------- 1コマ
def frame(fi):
    """fi：0〜47 → 8bit RGB"""
    KS.PAL = PALETTE
    t = fi / FPS
    img = np.zeros((H, W, 3), np.float32)
    if t >= T['IGN'][2] - .001:
        storm(img, t)
        impact(img, t)
        dome(img, t)
        dome_elec(img, t, fi)
        surge(img, t)
        ribbons(img, t)
        big_bolts(img, fi)
        floor_reflect(img, t)
        rocks(img, t)
    else:
        img += sky0() * .25 * sstep(0, .15, t)
    ignition(img, t)
    gold(img, t)
    img = bloom(img)
    w = white_level(t)
    if w > 0:
        img = img * (1 - w) + KS.pc((1.0, 1.0, 1.0)) * w * 1.2 + img * w * .2
    out = tonemap(img)
    return (out * 255 + .5).astype(np.uint8)


def main(out, which=None):
    os.makedirs(out, exist_ok=True)
    for fi in (which or range(N)):
        im = frame(fi)
        cv2.imwrite(os.path.join(out, f'f{fi + 1:02d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('f', fi + 1, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], [int(v) - 1 for v in sys.argv[2:]] or None)
