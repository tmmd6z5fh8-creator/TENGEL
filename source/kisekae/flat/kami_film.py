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
     0.4〜0.63秒 ガラスの ドームが 床から ふくらむ（ふちが 光る）・0.43〜0.63秒 ピンクの 電気の 光
     0.6〜1.4秒 嵐の 頂点：ドームの ふちの ジリジリと 肩の 電気・とんでくる 岩・しぶき
     0.52〜0.74秒 ドームが 床から 上がりながら 丸い 玉に なる（まわりに 雷を まとう：第4.47版）→ 0.68〜1.333秒 止まらずに 玉が まん中へ 小さく なって 金の 光に 入る
       ドームが 床から 上がり はじめて から 玉が 消えるまで ずっと ブルブル（左右・大きさ）・床から はなれる 時は 下で 雷が スパークして 金の 爆発（0.52〜1.06秒）
     0.24〜1.4秒 上から 下への 雷（上は 細く 下ほど 太い・だんだん 太く・上の 方は 不定期に ガクッと かわる）・0.73〜1.3秒 玉から 画面の はしへ はしる 雷（不定期）
     1.33〜1.6秒 金の 光が 集まって 金の 爆発（金の かけら・金の 粒・光の 筋）→ まっ白（② 金の 字へ）。ドームは もう ない
   光は 足し算で 重ねて、明るい 所の にじみ（ブルーム）と、白く とぶ 前に ゆるやかに 頭うち（肩の ある 曲線）
   点めつ：強い 光は どの 点でも 1秒に 3回まで（大きな 白は はじめの 1回と さいごの 金→白 だけ。雷の 太い 所は 動かさず、同じ 所には つづけて 出さない）。画面ぜんたいは 動かさない（動くのは 光・ドーム・帯・岩）
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
RIBS = ((0, .24, 1.0), (1, .3, .9), (2, .56, 1.36), (5, .72, 1.2), (3, .9, 1.4), (4, 1.04, 1.4))
# 上から 下への 雷（前の 白い 光の 帯の 所：第4.47版）：(kami.py の RIBBONS の 番号, 出る 秒, 消える 秒)
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


def surge_img():
    return cache('surge', lambda: KS.surge(k=S).astype(np.float32))


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


# ---------------------------------------------------------------- ドーム（第4.47版：床から 上がりながら 丸い 玉に なる → まん中へ 小さく なって 金の 光へ）
# まさちゃん「一枚目のオレンジで例を描いたように、上に上がるに連れて、丸くなっていき(周りには雷を纏ってる
#   二枚目の写真のように、丸が3枚目のシーンに入る(周りの丸は消えてる)タイミングに合わせて小さくなり、3枚目のシーンに入るようにして！
#   で、四枚目のシーン(周りの丸は消えてる)は進んでいく。」「周りの丸は消えてるは、3枚目のことを指してるよ」
#   「いや、ドームが下から上に上がるに連れて丸くなるってこと」
# → ドームが 床から はなれて 上がりながら 丸い 玉に なる（まわりに 雷を まとう）。
#   金の 光（GOLD の はじめ）に 合わせて 玉が まん中へ 小さく なって 消える（3枚目＝金の 光の 点だけ・ドームは もう ない）
ORB_C = (195.0, 432.0)          # 玉の まん中（金の 光も ここ）
ORB_R = 192.0                   # 玉の 半径（上は ドームの てっぺんの あたり）
MORPH = (.52, .74)              # ドームが 床から 上がりながら 丸く なる（まさちゃん「ドームから球体に変わる速度もっと早くてもいいかも！」）
SHRINK = (.68, 1.333)           # 玉が 小さく なる（おわり＝金の 光の はじめ）：まさちゃん「ドームから球体になる時に一度、止まる演出無くて、その分球体が小さくなるのを…長くして！」
#   → 玉に なって 止まる 間を なくし、丸く なりきる 前から ゆっくり 小さく なり はじめる（ゆっくり → だんだん 速く → まん中へ すいこまれる）
ORB_VIB_PX = (1.5, 3.2, 6.0)    # 大きさの ふるえ（画面の px）：ドームの 間・玉に なった 時・小さく なる おわりの 方（だんだん 大きく）
ORB_SHAKE_PX = (1.8, 3.2, 6.0)  # 左右の ブルブル（画面の px）：同じ。小さい 玉では 半径の 11〜12% まで
ORB_VIB_W = .008                # はばだけの ふるえ（左右の 大きさ：ドームが 上がり はじめた 時から）
#   まさちゃん「球体になってからもっと大きく振動しながら小さくして！」→ 玉に なったら ふるえを 大きく・小さく なる ほど もっと 大きく
#   まさちゃん「ドーム型から球体へ変形する下から上に上がる時もドームを左右に大きさ変えて振動させて！」→ ふるえは ドームが 床から 上がり はじめる 時から
#   まさちゃん「球体常に、大きさが変わって振動しているようにして！」「左右にもブルブルして、振動の速度早くして違和感ないようにして！」
#   → 丸く なって から 消えるまで ずっと ふるえる：コマごとに 大きさと 左右が 細かく かわる（ブルブル）。ふちと 電気は いっしょに ふるえ、
#     ふちは 少し ぶれて 見える（速く ふるえる 物は ぶれて 見えるのが 自然）。中の もようは ふるえない（点めつを ふやさない）・小さめ（画面ぜんたいが 近づく ように 見えない）
SP_ENV = (.45, .85, 1.0, .85, .6, .3)   # 玉の まわりの 雷（とげ）の コマごとの 明るさ（ゆっくり ついて 消える：点めつを ふやさない）
WR_ENV = (.5, .9, 1.0, .7, .35)         # 玉に まきつく 雷の コマごとの 明るさ


def dome_scale(t):
    d0, d1, d2, d3 = T['DOME']
    if t < d0:
        return 0.0
    if t < d1:
        return .06 + .94 * ease_out((t - d0) / (d1 - d0))
    if t < d2:
        return 1.0 + .15 * (t - d1) / (d2 - d1)
    return 1.15 + .03 * min(1.0, (t - d2) / (d3 - d2))


def vib_seq():
    """コマごとの ふるえ（左右・大きさ・つぶれ）：向きが コマごとに かわる（速い ブルブル）・大きさは ばらばら"""
    def f():
        rng = random.Random(8800)
        out = []
        for k in range(N + 8):
            vx = (1 if k % 2 else -1) * rng.uniform(.55, 1.0)
            vs = (1 if (k + (k // 3)) % 2 else -1) * rng.uniform(.45, 1.0)
            vq = rng.uniform(-1, 1)
            vw = (1 if (k // 2 + k) % 2 else -1) * rng.uniform(.5, 1.0)
            out.append((vx, vs, vq, vw))
        return out
    return cache('vib', f)


def shape_at(t):
    """その時の ドームの 形（dict）か None（金の 光に 入った あと）。
       ye：いちばん はばの 広い 所の y・W：その 半はば・Hu／Hl：そこから 上／下の 高さ・p,q：上の 形（ドームの 形 → 円）・
       m：丸く なった 割合・w：小さく なる 進み・f：大きさ（床での ドームの 半径＝1）"""
    sd = dome_scale(t)
    if sd <= 0 or t >= SHRINK[1]:
        return None
    RX, HD = KM.DOME2[2], KM.DOME2[3]
    m = sstep(MORPH[0], MORPH[1], t)
    R, w = ORB_R, 0.0
    if t > SHRINK[0]:
        w = (t - SHRINK[0]) / (SHRINK[1] - SHRINK[0])
        R = ORB_R * (1 - w * w)                             # ゆっくり 小さく なり はじめて だんだん 速く（まん中へ すいこまれる）
    Wd = RX * sd * (1 - m) + R * m
    ye = BASE + (ORB_C[1] - BASE) * m
    Hu = HD * sd * (1 - m) + R * m
    Hl = R * m
    f = Wd / RX
    if w > 0:
        f = max(f, .32)
    sh = dict(cx=CX, ye=ye, W=Wd, Hu=Hu, Hl=Hl, yt=ye - Hu, yb=ye + Hl, p=KM.DOME_P + (2 - KM.DOME_P) * m,
              q=KM.DOME_Q + (2 - KM.DOME_Q) * m, m=m, w=w, f=f, sd=sd)
    sh['base'] = sh
    # ふるえ（丸く なって くると はじまる）：ふち（形・電気）だけ ふるえる。中の もようは base（ふるえない 形）で 描く
    on = sstep(MORPH[0] - .02, MORPH[0] + .06, t)            # ドームが 床から 上がり はじめる 時から ずっと
    if on > 0:
        vx, vs, vq, vw = vib_seq()[max(0, int(round(t * FPS)))]
        g1 = sstep(MORPH[1] - .06, MORPH[1] + .04, t)              # 玉に なると 大きく
        g2 = sstep(SHRINK[0] + .1, SHRINK[1] - .1, t)              # 小さく なる ほど もっと 大きく

        def amp(a):
            return (a[0] + (a[1] - a[0]) * g1 + (a[2] - a[1]) * g2) * on
        Rn = max(Wd, 1.0)
        ra = min(amp(ORB_VIB_PX), .11 * Rn)                      # 大きさの ふるえ（px）
        shk = min(amp(ORB_SHAKE_PX), .12 * Rn)                   # 左右の ゆれ（px）
        su, sq = 1 + ra / Rn * vs, ra / Rn * .4 * vq
        sw = 1 + ORB_VIB_W * on * vw                          # 左右の 大きさ
        vb = dict(sh)
        vb.update(cx=CX + shk * vx, W=Wd * su * (1 + sq) * sw, Hu=Hu * su * (1 - sq), Hl=Hl * su * (1 - sq))
        vb.update(yt=ye - vb['Hu'], yb=ye + vb['Hl'], vib=on)
        vb['base'] = sh
        return vb
    return sh


def shape_w(sh, y):
    """高さ y（画面の px：配列）→ その 高さの 半はば（形の 外は 0）"""
    y = np.asarray(y, np.float64)
    up = (sh['ye'] - y) / max(sh['Hu'], 1e-3)
    wu = sh['W'] * np.clip(1 - np.clip(up, 0, 1) ** sh['q'], 0, 1) ** (1 / sh['p'])
    wu = np.where(up > 1, 0.0, wu)
    if sh['Hl'] > .05:
        lo = (y - sh['ye']) / sh['Hl']
        wl = sh['W'] * np.sqrt(np.clip(1 - lo * lo, 0, 1))
        wl = np.where(lo > 1, 0.0, wl)
    else:
        wl = np.zeros_like(y)
    return np.where(y <= sh['ye'], wu, wl)


def shape_outline(sh, n=640):
    """形の ふち（下の まん中 → 左 → てっぺん → 右 → 下の まん中）を 長さ 等分の n+1 点 →
       配列 [x, y, 外向きの nx, ny, 下からの 高さの 割合 u, 床（1＝床に ついて いる 所：電気を 出さない）]。o＝0.5 が てっぺん"""
    cx, yt, yb = sh['cx'], sh['yt'], sh['yb']
    tau = np.linspace(0, 1, 1500)
    ys = yt + (yb - yt) * (1 - np.cos(np.pi * tau)) / 2
    ws = shape_w(sh, ys)
    left = np.stack([cx - ws, ys], 1)[::-1]
    right = np.stack([cx + ws, ys], 1)
    pts = np.concatenate([[[cx, yb]], left, right[1:], [[cx, yb]]], 0)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    acc = np.concatenate([[0.0], np.cumsum(seg)])
    s_ = np.linspace(0, acc[-1], n + 1)
    x = np.interp(s_, acc, pts[:, 0])
    y = np.interp(s_, acc, pts[:, 1])
    tx, ty = np.gradient(x), np.gradient(y)
    tl = np.hypot(tx, ty) + 1e-9
    u = np.clip((yb - y) / max(yb - yt, 1e-3), 0, 1)
    flo = ((y > BASE - 1.5) & (sh['Hl'] < 20)).astype(np.float64)
    return np.stack([x, y, ty / tl, -tx / tl, u, flo], 1)


def glass_tex():
    """ガラスの もよう（形に くっつく：横＝左はし 0 〜 右はし 1・たて＝てっぺん 0 〜 下 1）"""
    def f():
        n = 512
        tx = dict(wob=(KS.fbm(n, n, 5, 42, 3) - .5) * .5, rn=KS.fbm(n, n, 7, 33, 4), b2=KS.fbm(n, n, 12, 43, 3),
                  hb=KS.fbm(n, n, 20, 35, 3), band=KS.fbm(n, n, 30, 36, 3), sh=KS.fbm(n, n, 16, 37, 4),
                  shp=KS.plasma(n, n, 18, 40, 6.0), vv=KS.plasma(n, n, 14, 41, 7.0),
                  l1=KS.fbm(1024, 1024, 90, 38, 3), l2=KS.fbm(1024, 1024, 260, 39, 2))
        return {k: v.astype(np.float32) for k, v in tx.items()}
    return cache('gtex', f)


def tex_at(tex, A, B):
    th, tw = tex.shape
    mx = (np.clip(A, -.5, 1.5) * (tw - 1)).astype(np.float32)
    my = (np.clip(B, -.5, 1.5) * (th - 1)).astype(np.float32)
    return cv2.remap(tex, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def floor_bands():
    """床の 光の 映りこみ（ドームの 下の 横の すじ：床から はなれると 消える）"""
    def f():
        rng = np.random.default_rng(131)
        return [(rng.uniform(3, 9) * rng.uniform(1, 9), rng.uniform(.5, 1.4), rng.uniform(-1, 1), rng.uniform(14, 70), rng.uniform(.3, .9)) for _ in range(18)]
    return cache('fbands', f)


def bead_list():
    """ふちの 光の 粒と とげ：(ふちの 上の 場所 o, 半径, 外への ずれ, 明るさ, とげ（長さ, 向きの ずれ, 明るさ）か None)"""
    def f():
        rng = np.random.default_rng(231)
        out = []
        for _ in range(1300):
            if rng.random() > .42:
                continue
            o, rad, off, val = rng.random(), rng.uniform(.7, 2.1), rng.uniform(-.6, 1.2), rng.uniform(.5, 1.0)
            spike = (rng.uniform(2, 8), rng.uniform(-.7, .7), rng.uniform(.5, 1.0)) if rng.random() < .22 else None
            out.append((o, rad, off, val, spike))
        return out
    return cache('beads', f)


def glass(img, sh, t, fade=1.0):
    """ガラスの ような 光の ドーム／玉（kami_storm.dome_glass と 同じ 作り：どんな 形でも その コマで 描く）。
       床から はなれると 床の 光（下の 横の すじ・下の 帯・床との さかいめ）は 消える。小さく なる 間は 中が 金色に 光る"""
    cx, Wd, m, f, w = sh['cx'], sh['W'], sh['m'], sh['f'], sh['w']
    yt, yb = sh['yt'], sh['yb']
    pad = 40 * max(f, .3) + 4
    x0, x1 = max(0, int((cx - Wd - pad) * S)), min(W, int(math.ceil((cx + Wd + pad) * S)))
    y0, y1 = max(0, int((yt - pad) * S)), min(H, int(math.ceil((yb + pad) * S)))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    xs = np.arange(x0, x1, dtype=np.float64) / S
    ys = np.arange(y0, y1, dtype=np.float64) / S
    hh, ww = len(ys), len(xs)
    sb = sh['base']                                          # 中の もようは ふるえない 形で（ふちだけ ふるえる）
    wv = shape_w(sh, ys)[:, None]
    wr = shape_w(sb, ys)[:, None]
    dw = (shape_w(sb, ys + .5) - shape_w(sb, ys - .5))[:, None]
    X = np.broadcast_to(xs[None, :], (hh, ww))
    Y = np.broadcast_to(ys[:, None], (hh, ww))
    inside = ((np.abs(X - sb['cx']) < wr) & (wr > 0)).astype(np.float32)          # 体（ふるえない）
    inside_v = ((np.abs(X - cx) < wv) & (wv > 0)).astype(np.float32)               # ふち（ふるえる）
    sr = (X - sb['cx']) / np.maximum(wr, 1e-3)
    s = np.clip(sr, -1, 1)
    c = np.sqrt(np.clip(1 - s * s, 0, 1))
    rn2 = np.sqrt(1 + dw * dw)
    fres = np.clip(1 - c / rn2, 0, 1).astype(np.float32)
    phi = np.arcsin(s)
    ybb, ytb = sb['yb'], sb['yt']
    u = np.clip((ybb - Y) / max(ybb - ytb, 1e-3), 0, 1).astype(np.float32)
    hgt = (yb - Y).astype(np.float32)
    A = ((np.clip(sr, -1.4, 1.4) + 1) / 2).astype(np.float32)
    B = ((Y - ytb) / max(ybb - ytb, 1e-3)).astype(np.float32)
    TX = glass_tex()
    m8 = (inside > .5).astype(np.uint8)
    din = cv2.distanceTransform(m8, cv2.DIST_L2, 5) / S / max(f, 1e-3)
    if sb is sh:
        sdd = din - cv2.distanceTransform(1 - m8, cv2.DIST_L2, 5) / S / max(f, 1e-3)
    else:                                                    # ふちの 線は ふるえる 形で
        mv = (inside_v > .5).astype(np.uint8)
        sdd = (cv2.distanceTransform(mv, cv2.DIST_L2, 5) - cv2.distanceTransform(1 - mv, cv2.DIST_L2, 5)) / S / max(f, 1e-3)
    abs_s = np.abs(s).astype(np.float32)
    col = np.zeros((hh, ww, 3), np.float32)
    al = np.zeros((hh, ww), np.float32)
    # ガラスの 体
    body = inside * (.05 + .5 * fres ** 2)
    col += KS.pc((.12, .4, 1.0)) * (inside * (.08 + .12 * u))[..., None] * .4
    col += KS.pc((.35, .85, 1.0)) * (inside * fres ** 2)[..., None] * .55
    al = np.maximum(al, body)
    # ガラスが 光を すう・つや（左上からの 光の 映りこみ）・空の 映りこみ
    tint = inside * (.2 + .25 * fres ** 2)
    al = np.maximum(al, tint)
    col += KS.pc((.0, .02, .08)) * tint[..., None]
    nx_, nu_, nz_ = s / rn2, dw / rn2, c / rn2
    Ld = np.array([-.5, .55, .67])
    Ld /= np.linalg.norm(Ld)
    hv = Ld + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    ndh = (np.clip(nx_ * hv[0] + nu_ * hv[1] + nz_ * hv[2], 0, 1) * inside).astype(np.float32)
    ph_d = np.degrees(phi)
    vert = smoothstep(.04, .2, u) * (1 - smoothstep(.6, .9, u)) * inside
    sp1 = ndh ** 40 * .35 + ((np.exp(-((ph_d + 44) / 4.5) ** 2) * .9 + np.exp(-((ph_d + 36) / 1.2) ** 2) * .8 + np.exp(-((ph_d - 57) / 2.2) ** 2) * .5) * vert).astype(np.float32)
    col += KS.pc((.85, .97, 1.0)) * sp1[..., None]
    al = np.maximum(al, np.clip(sp1, 0, 1) * .8)
    band2 = (inside * smoothstep(.45, .62, nu_) * (1 - smoothstep(.7, .86, nu_)) * (.6 + .4 * tex_at(TX['b2'], A, B))).astype(np.float32)
    col += KS.pc((.55, .85, 1.0)) * band2[..., None] * .3
    al = np.maximum(al, band2 * .3)
    # たての 光の すじ
    wob = tex_at(TX['wob'], A, B)
    rib = (.5 + .5 * np.cos(phi * 30 + .7 + wob * 3)) ** 6
    rib2 = (.5 + .5 * np.cos(phi * 75 + 2.1 + wob * 5)) ** 10
    rib_a = (inside * (rib * .9 + rib2 * .45) * (.25 + .75 * smoothstep(.75, .05, u)) * (.35 + .65 * smoothstep(.15, .7, abs_s))
             * (.5 + .9 * tex_at(TX['rn'], A, B))).astype(np.float32)
    col += KS.pc((.55, .92, 1.0)) * rib_a[..., None] * .55
    # 床の 光（床から はなれると 消える）
    flk = 1 - sstep(0, .3, m)
    if flk > 0:
        hb = np.zeros((hh, ww), np.float32)
        for dy, bw_, xr, ln, amp in floor_bands():
            seg = np.exp(-((Y - (yb - dy * f)) / (bw_ * f)) ** 2) * np.exp(-((X - (cx + xr * Wd)) / (ln * f)) ** 2) * amp
            hb = np.maximum(hb, seg.astype(np.float32))
        hb *= inside * (.6 + .6 * tex_at(TX['hb'], A, B))
        col += KS.pc((.75, .97, 1.0)) * hb[..., None] * .9 * flk
        base_band = inside * np.exp(-(hgt / (18 * f)) ** 2) * (.5 + .5 * abs_s)
        col += KS.pc((.3, .85, 1.0)) * base_band[..., None] * .55 * flk
    # ふちの 内がわの 厚み・肩の 光・中の 細い 電気の すじ
    band = (inside * smoothstep(18, 2, din) * (.55 + .45 * tex_at(TX['band'], A, B))).astype(np.float32)
    col += KS.pc((.45, .9, 1.0)) * band[..., None] * .65
    al = np.maximum(al, band * .7)
    shd = (inside * smoothstep(54, 6, din) * smoothstep(.3, .6, u) * smoothstep(1.0, .82, u) * smoothstep(.08, .42, abs_s)
           * (.5 + 1.0 * tex_at(TX['sh'], A, B))).astype(np.float32)
    col += KS.pc((1.0, .22, .8)) * shd[..., None] * .36
    col += KS.pc((1.0, .5, .9)) * (shd * tex_at(TX['shp'], A, B))[..., None] * .5
    vv = (inside * tex_at(TX['vv'], A, B) * (.35 + .65 * smoothstep(.85, .2, u)) * (.4 + .6 * smoothstep(.1, .7, abs_s))).astype(np.float32)
    col += KS.pc((.45, .9, 1.0)) * vv[..., None] * .32
    # ふち：光の 粒が つながった 線と 外の 光
    edge = np.clip(1 - np.abs(sdd - .7) / 1.6, 0, 1)
    lumpy = .55 + .45 * smoothstep(.3, .7, tex_at(TX['l1'], A, B)) + .5 * (tex_at(TX['l2'], A, B) > .62)
    rim = (edge * lumpy * (Y <= BASE + .5)).astype(np.float32)
    rim *= (1 - .5 * smoothstep(20, 0, hgt / f) * flk).astype(np.float32)
    beads = np.zeros((hh, ww), np.float32)
    OL = shape_outline(sh, 900)
    for o, rad, off, val, spike in bead_list():
        x, y, nx, ny, uu, fl = OL[int(o * 900)]
        if fl > .5:
            continue
        px, py = (x + nx * off * f) * S - x0, (y + ny * off * f) * S - y0
        cv2.circle(beads, (int(px * 4), int(py * 4)), max(1, int(rad * f * S * 4)), float(val), -1, cv2.LINE_AA, shift=2)
        if spike is not None:
            ln, da, v2 = spike
            ang = math.atan2(ny, nx) + da
            cv2.line(beads, (int((x * S - x0) * 4), int((y * S - y0) * 4)),
                     (int(((x + ln * f * math.cos(ang)) * S - x0) * 4), int(((y + ln * f * math.sin(ang)) * S - y0) * 4)),
                     float(v2), max(1, int(f * S * .7)), cv2.LINE_AA, shift=2)
    rim = np.maximum(rim, beads)
    if sh.get('vib', 0) > 0:                                 # 速く ふるえる 物は 少し ぶれて 見える（ふちの 白い 線を やわらかく）
        rim = rim * (1 - .7 * sh['vib']) + fblur(rim, 2.2 * S) * 1.3 * .7 * sh['vib']
    rimg = fblur(rim, max(.5, 2.5 * S * f)) * 2.0 + fblur(rim, max(.5, 7 * S * f)) * 1.4 + fblur(rim, max(.5, 16 * S * f)) * .8
    col += KS.pc((.5, .9, 1.0)) * rimg[..., None] * .55
    col += KS.pc((1.0, 1.0, 1.0)) * rim[..., None] * .95
    col += KS.pc((.3, .8, 1.0)) * fblur(rim, max(.5, 1.2 * S * f))[..., None] * .4
    if flk > 0:
        lip = np.exp(-(((Y - yb - 2) / 2.2) ** 2)) * smoothstep(Wd + 6, Wd - 30, np.abs(X - cx))
        lip = np.maximum(lip, fblur(lip.astype(np.float32), max(.5, 6 * S * f)) * 1.2)
        col += KS.pc((.4, .9, 1.0)) * lip.astype(np.float32)[..., None] * .7 * flk
    # 小さく なる 間：中に 金の 光が 集まる（まん中が 強く）
    if w > 0:
        d = np.sqrt((X - cx) ** 2 + (Y - sh['ye']) ** 2) / max(Wd, 1.0)
        core = (np.exp(-(d / .35) ** 2) * (.1 + 1.2 * w * w)).astype(np.float32)
        col += (inside * (.12 + .5 * w * w))[..., None] * np.float32([1.0, .78, .35]) + core[..., None] * np.float32([1.0, .92, .7])
        col *= 1 + .8 * w * w
    col = np.clip(col, 0, 1.5)
    lum = np.clip(col.max(-1), 0, 1)
    a = np.clip(np.maximum(al, lum * .92), 0, 1)
    rgb = np.clip(col, 0, 1)
    alpha = np.maximum(a, rgb.max(-1))
    reg = img[y0:y1, x0:x1]
    reg[:] = rgb * fade + reg * (1 - alpha[..., None] * fade)


def dome(img, t):
    """ドーム（ふくらむ → 床から 上がりながら 丸い 玉に → まん中へ 小さく なる）"""
    sh = shape_at(t)
    if sh is None:
        return
    d0, d1 = T['DOME'][:2]
    glass(img, sh, t, sstep(d0, d0 + .04, t))
    # ふくらむ 間は ふちが 強く 光る（丸く なり はじめたら すぐ 消える：点めつを ふやさない）
    e = 1 - sstep(d1 - .05, d1 + .03, t)
    if e > 0:
        OL = shape_outline(sh['base'], 400)                     # ふくらむ 間の 光は ふるえない 形で（ふちの 線だけ ふるえる）
        pts = [(x, y) for x, y, nx, ny, u, fl in OL if fl < .5]
        m = lines_mask([(pts, 1.0)], 2.2)
        glow_add(img, m, ((0, (1, 1, 1), .9 * e), (2, (.5, .9, 1.0), 1.4 * e), (8, (.3, .6, 1.0), 1.2 * e)))
    # 小さく なる 間：残像の ふち（内へ すいこまれる）
    if sh['w'] > .45:                                        # 速く 小さく なる 所だけ（ゆっくりの 間は ふちが 太く 見える だけ）
        segs = []
        for k_, g_ in ((1, .45), (2, .25), (3, .12)):
            s2 = shape_at(t - k_ / 90)
            if s2 is not None and s2['w'] > 0:
                segs.append(([(x, y) for x, y, *_ in shape_outline(s2, 200)], g_))
        if segs:
            m = lines_mask(segs, 1.6)
            glow_add(img, m, ((1.2, (1, .88, .5), .9), (5, (1, .55, .15), .6)))


_EL = {}


def elec_events():
    """ドームの 電気の コマごとの 形（はじめに まとめて 作る）。場所は ふちの 上の 場所 o（0.5＝てっぺん）で 持ち、コマごとに その時の 形に のせる。
       cl：肩の 電気の かたまり (出る コマ, o, 内への ふかさ, かたまりの 中心からの 線)・arcs：表面を はしる 電気・
       sp：玉の まわりの 雷の とげ (出る コマ, o, 向きの ずれ, 長さ, 1＝外・-1＝内, 種)・wr：玉に まきつく 雷 (出る コマ, o, はば, はなれ, 種)"""
    if _EL:
        return _EL
    f0, f1 = int(math.ceil(T['CRACK'][0] * FPS)), int(math.ceil(SHRINK[1] * FPS)) - 1
    rng = random.Random(77)
    cl, arcs, sp, wr = [], [], [], []
    for f in range(f0, f1 + 1):
        k = f - f0
        for _ in range(3):
            while True:
                o = rng.random()
                if KM._spread_ok(o, k):
                    break
            dep = rng.uniform(5, 40)
            polys = []
            a0 = rng.uniform(0, 2 * math.pi)
            for j in range(rng.randint(3, 5)):
                a = a0 + j * 2.1 + rng.uniform(-.5, .5)
                ln = rng.uniform(10, 30)
                p0 = (rng.uniform(-3, 3), rng.uniform(-3, 3))
                main = KM._disp_ms(rng, p0, (p0[0] + ln * math.cos(a), p0[1] + ln * math.sin(a)), KM.CRK_ROUGH)
                polys.append((main, 1.0))
                if rng.random() < .7:
                    q = main[rng.randint(1, len(main) - 2)]
                    a2 = a + rng.choice((-1, 1)) * rng.uniform(.5, 1.2)
                    l2 = ln * rng.uniform(.3, .55)
                    polys.append((KM._disp_ms(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), KM.CRK_ROUGH[1:]), .8))
            cl.append((f, o, dep, polys))
        if k % 3 == 0:
            arcs.append((f, 1 if (k // 3) % 2 else -1, rng.uniform(.28, .9), rng.uniform(-.38, .22), rng.uniform(12, 58),
                         rng.uniform(.3, .45), rng.randrange(1 << 30), rng.choice('cv')))
        for _ in range(2):
            sp.append((f, rng.random(), rng.uniform(-1.0, 1.0), rng.uniform(18, 58), rng.choice((1, 1, 1, -1)), rng.randrange(1 << 30)))
        wr.append((f, rng.random(), rng.uniform(.04, .16) * rng.choice((-1, 1)), rng.uniform(2, 12), rng.randrange(1 << 30)))
    _EL.update(f0=f0, f1=f1, cl=cl, arcs=arcs, sp=sp, wr=wr)
    return _EL


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
    """ドームの 電気（その時の 形に のる）：ふちの ジリジリ・肩の 電気・表面を はしる 電気・玉の まわりに まとう 雷（丸く なって くると）"""
    E = elec_events()
    if not (E['f0'] <= fi <= E['f1']):
        return
    sh = shape_at(t)
    if sh is None:
        return
    k = fi - E['f0']
    fe = max(.4, sh['f'])
    m_ = sh['m']
    OL = shape_outline(sh, 640)
    N_ = len(OL) - 1

    def P(o):
        return OL[int(round((o % 1.0) * N_))]
    rng = random.Random(900 + fi)
    sizz = []
    c = tries = 0
    while c < 7 and tries < 500:
        tries += 1
        o = rng.random()
        if not KM._spread_ok(o, k):
            continue
        x, y, nx, ny, u, fl = P(o)
        if fl > .5:
            continue
        ang = math.atan2(ny, nx) + rng.uniform(-1.2, 1.2)
        ln = rng.uniform(4, 12) * fe
        p0 = (x + nx * rng.uniform(-2, 2), y + ny * rng.uniform(-2, 2))
        sizz.append((KM._disp(rng, p0, (p0[0] + ln * math.cos(ang), p0[1] + ln * math.sin(ang)), 2, .9), .6))
        c += 1
    pink = []
    for f0_, o, dep, polys in E['cl']:
        if not (f0_ <= fi < f0_ + 4):
            continue
        if (o * 9973.0) % 1.0 < .8 * m_:          # 玉に なると 肩の 電気は 少し へらす（まわりの 雷と かさなって 点めつが ふえない ように）
            continue
        x, y, nx, ny, u, fl = P(o)
        if fl > .5 or u < .3 * (1 - m_):
            continue
        cc = (x - nx * dep * fe, y - ny * dep * fe)
        pink += [([(cc[0] + px * fe, cc[1] + py * fe) for px, py in pts], v) for pts, v in polys]
        pink += twitch_polys(rng, [cc], 1, 3 * fe, 8 * fe)
    arcs_c, arcs_v = [], []
    yb, yt = sh['yb'], sh['yt']
    for f0_, side, u0, du, ph1d, rough, seed, tone in E['arcs']:
        if not (f0_ <= fi < f0_ + 4):
            continue
        rs = random.Random(seed)
        u1 = max(.04, min(.93, u0 + du))
        ys_ = np.array([yb - (u0 + (u1 - u0) * j / 24) * (yb - yt) for j in range(25)])
        ws_ = shape_w(sh, ys_)
        pts = [(sh['cx'] + float(ws_[j]) * math.sin(math.radians(side * (88.0 + (ph1d - 88.0) * j / 24))), float(ys_[j])) for j in range(25)]
        pts = KM._jag(rs, pts, rough, 2)
        (arcs_c if tone == 'c' else arcs_v).extend([(pts, 1.0)] + arc_br(rs, pts) + twitch_polys(rng, pts, 2))
    cor = []
    cw = sstep(.2, .6, m_)                      # 丸く なって くると まわりに 雷を まとう
    if cw > 0:
        for f0_, o, da, L, dirn, seed in E['sp']:
            age = fi - f0_
            if not (0 <= age < len(SP_ENV)):
                continue
            x, y, nx, ny, u, fl = P(o)
            if fl > .5:
                continue
            rs = random.Random(seed)
            ang = math.atan2(ny, nx) + da + (math.pi if dirn < 0 else 0.0)
            ln = L * fe
            main = KM._disp_ms(rs, (x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang)), KM.CRK_ROUGH)
            g = SP_ENV[age] * cw
            cor.append((main, g))
            for _ in range(rs.randint(0, 2)):
                q = main[rs.randint(1, len(main) - 2)]
                a2 = ang + rs.choice((-1, 1)) * rs.uniform(.5, 1.1)
                l2 = ln * rs.uniform(.3, .55)
                cor.append((KM._disp_ms(rs, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), KM.CRK_ROUGH[1:]), g * .8))
        for f0_, o0, do, off, seed in E['wr']:
            age = fi - f0_
            if not (0 <= age < len(WR_ENV)):
                continue
            rs = random.Random(seed)
            n_ = max(4, int(abs(do) * 90))
            pts = []
            for j in range(n_ + 1):
                x, y, nx, ny, u, fl = P(o0 + do * j / n_)
                pts.append((x + nx * off * fe, y + ny * off * fe))
            cor.append((KM._jag(rs, pts, .42, 2), WR_ENV[age] * cw))
    m = lines_mask(sizz, .9)
    glow_add(img, m, ((0, (1, 1, 1), 1.0), (.8, (.6, .95, 1.0), 1.0), (3, (.3, .75, 1.0), .5)))
    m = lines_mask(pink, 1.0)
    glow_add(img, m, ((0, (1, .9, .98), 1.0), (.9, (1.0, .45, .9), 1.3), (3.5, (1.0, .2, .8), .8)))
    for polys, col in ((arcs_c, (.6, .95, 1.0)), (arcs_v, (.75, .65, 1.0))):
        if polys:
            m = lines_mask(polys, 1.1)
            glow_add(img, m, ((0, (1, 1, 1), 1.0), (1, col, 1.2), (4, col, .5)))
    if cor:
        m = lines_mask(cor, 1.25)
        glow_add(img, m, ((0, (1, 1, 1), 1.0), (1.0, (1, .85, .45), 1.3), (3.5, (1, .5, .12), .85), (10, (1, .3, .06), .35)))


# ---------------------------------------------------------------- ドームが 床から 上がる 時の 下の 爆発と 雷の スパーク（第4.47版）
# まさちゃん「ドームから球体に上がる時に、したの方は、雷がスパークして、爆発してる演出も入れて！」
# → 玉が 床から はなれる 所で：床の まん中から 金の 爆発（ふくらむ 炎の 光・床を はしる 衝撃の 輪・とびちる 火花）と、
#   床を はしる 雷・床と 玉の 下を つなぐ 雷・まん中から はじける 短い 雷（スパーク）
LIFT_T = (.52, .6, .88, 1.06)    # 爆発：はじまり・いちばん 強い・消え はじめ・消える（まさちゃん「あと下のスパーク爆発の時間もう少し長くして！」）
LIFT_FR = (16, 29)                # 下の 雷の スパークが 出る コマ（0.53〜0.97秒）
LIFT_BURSTS = ((0.0, 110), (.15, 60), (.29, 45))   # 火花が とぶ 時（はじまりからの 秒）と 数
LIFT_ENV = (.9, 1.0, .6)          # その 雷の コマごとの 明るさ


def lift_tex():
    return cache('lifttex', lambda: KS.fbm(256, 512, 9, 517, 5, .55).astype(np.float32))


def lift_blast(img, t):
    """床の まん中の 金の 爆発（炎の 光・衝撃の 輪・火花）"""
    t0, tp, t2, t1 = LIFT_T
    if not (t0 <= t <= t1):
        return
    u = (t - t0) / (t1 - t0)
    e = sstep(t0, tp, t) * (1 - .18 * sstep(tp, tp + .1, t)) * (1 - sstep(t2, t1, t))   # ぱっと 強く → 少し おちて つづく → 消える
    y0 = max(0, int((BASE - 300) * S))
    y1 = min(H, int((BASE + 70) * S))
    X = (np.arange(W, dtype=np.float32)[None, :] / S)
    Y = (np.arange(y0, y1, dtype=np.float32)[:, None] / S)
    reg = img[y0:y1]
    # 炎の 光（床から 上へ ふくらむ：もようで ゆらぐ）
    r = 26 + 150 * ease_out((t - t0) / .26) + 14 * sstep(tp, t1, t)
    dx, dy = (X - CX) / r, (Y - BASE) / (r * .62)
    d = np.sqrt(dx * dx + dy * dy)
    tx = lift_tex()
    mx = np.broadcast_to(np.clip((dx + 1.5) / 3, 0, 1) * 511, d.shape).astype(np.float32)
    my = np.broadcast_to(np.clip((dy + 1.5) / 3, 0, 1) * 255 + 90 * u, d.shape).astype(np.float32)    # 炎の もようが 上へ ながれる
    nz = cv2.remap(tx, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fire = np.clip(1 - d / (.7 + .5 * nz), 0, 1) ** 1.4 * (Y <= BASE + 6) * e
    core = np.exp(-(d / .28) ** 2) * e
    reg += fire[..., None] * np.float32([1.0, .55, .14]) * 1.1 + (fire ** 2)[..., None] * np.float32([1.0, .85, .45]) * .9
    reg += core[..., None] * np.float32([1.0, .96, .85]) * 1.2
    # 床を はしる 衝撃の 輪
    for rs0, rg in ((0.0, 1.1),):                            # 衝撃の 輪（1つ：点めつを ふやさない）
        uu = (t - t0 - rs0) / .34
        if 0 <= uu <= 1:
            rr = 24 + 330 * ease_out(uu)
            ring = np.exp(-((np.sqrt(((X - CX) / rr) ** 2 + ((Y - BASE - 3) / (rr * .11)) ** 2) - 1) * rr / 7) ** 2) * (1 - uu) ** 1.2
            reg += ring[..., None] * np.float32([1.0, .78, .38]) * rg
    # 火花（金の すじ：上と 左右へ とぶ・おちる）
    sp = np.zeros((H, W), np.float32)
    rng = random.Random(4400)
    for k_ in range(sum(n_ for _, n_ in LIFT_BURSTS)):
        bt = 0.0
        acc = 0
        for bs, n_ in LIFT_BURSTS:
            if k_ >= acc:
                bt = bs
            acc += n_
        b0 = t0 + bt + rng.uniform(0, .07)
        age = t - b0
        life = rng.uniform(.22, .4)
        a = math.radians(rng.uniform(-172, -8))
        v = rng.uniform(260, 820)
        if not (0 <= age <= life):
            continue
        x0 = CX + rng.gauss(0, 30)
        vx, vy = math.cos(a) * v, math.sin(a) * v
        x, y = x0 + vx * age, BASE - 4 + vy * age + 900 * age * age
        tx_, ty_ = x - vx * .025, y - (vy + 1800 * age) * .025
        cv2.line(sp, (int(tx_ * S * 4), int(ty_ * S * 4)), (int(x * S * 4), int(y * S * 4)), float(1 - age / life), 2, cv2.LINE_AA, shift=2)
    glow_add(img, sp, ((0, (1, .95, .8), 1.0), (1.5, (1, .7, .25), 1.2), (5, (1, .4, .1), .6)))


def lift_arcs(mask, t, fi):
    """下の 雷の スパーク：床を はしる 雷・床と 玉の 下を つなぐ 雷・まん中から はじける 短い 雷（形は 雷ごとに 決まる・細かい ギザギザだけ コマごとに）"""
    if not (LIFT_FR[0] <= fi <= LIFT_FR[1] + len(LIFT_ENV)):
        return
    sh = shape_at(t)
    rng = random.Random(4500)
    for f in range(LIFT_FR[0], LIFT_FR[1] + 1):
        for _ in range(2):
            kind = rng.choice(('floor', 'floor', 'up', 'burst'))
            side = rng.choice((-1, 1))
            seed = rng.randrange(1 << 30)
            p = (rng.uniform(-50, 50), rng.uniform(70, 150), rng.uniform(-70, 70), rng.uniform(-110, -35), rng.uniform(25, 60), rng.uniform(-6, 10))
            age = fi - f
            if not (0 <= age < len(LIFT_ENV)):
                continue
            g = LIFT_ENV[age]
            rs = random.Random(seed)
            st = (CX + p[0] * .5, BASE - 2)
            if kind == 'floor':
                en = (CX + side * p[1], BASE + p[5])
                w1 = 3.5
            elif kind == 'up':
                if sh is None:
                    continue
                st = (CX + p[2], BASE - 2)
                en = (CX + p[2] * 1.2 + rs.uniform(-30, 30), sh['yb'] - 4)
                if en[1] > BASE - 12:
                    continue
                w1 = 2.5
            else:
                a = math.radians(p[3] if side > 0 else -180 - p[3])
                en = (st[0] + p[4] * math.cos(a) * 1.6, st[1] + p[4] * math.sin(a) * 1.6)
                w1 = 2.2
            macro = macro_path(rs, st, en, rs.choice(('zig', 'zig', 'step')))
            mid = fine_jag(random.Random(seed + 1), macro, (.16, .22))
            rj = random.Random(seed * 5 + fi)
            pts = [mid[0]]
            for q0, q1 in zip(mid, mid[1:]):
                pts += KM._disp_ms(rj, q0, q1, (.12,))[1:]
            draw_taper(mask, pts, 1.0, w1, g, min(1.0, (age + 1) / 1.5), 1.0)


def surge(img, t):
    s0, s1, s2, s3 = T['SURGE']
    if not (s0 <= t <= s3):
        return
    a = sstep(s0, s1, t) if t < s1 else (1.0 if t < s2 else 1 - sstep(s2, s3, t))
    sg = surge_img()
    img[:] = sg[..., :3] * a + img * (1 - sg[..., 3:4] * a)


# ---------------------------------------------------------------- 玉から 画面の はしへ はしる 雷・上から 下への 雷（第4.47版）
# まさちゃん「一枚目の青の線(雷)みたいに不定期で球体から、画面端側までビリビリと動く演出入れて！
#   あと、二枚目、三枚目の雷は、これももっと不定期に動いて、どんどん画面側に近づいていくにつれ雷が画面上から下にかけて太くなっていく演出入れて！
#   四枚目以降は、二枚目、三枚目の雷の動きを横向きの場合で、ラフに描いたものだよ。そのような動きを混ぜて不定期にして！」
#   「雷は青じゃなくて、例として青にしただけ！周りの雷の色は一緒！」
# → 色は 玉の まわりの 雷と 同じ（白い しん・金・だいだい・赤）。形は 大きな ギザギザ（のこぎり・横に ずれる 段・うねって から のこぎり）に 細かい ギザギザ。
#   はじめ（玉の 所・画面の 上）は 細く、先（画面の はし・下）ほど 太い（手前に 近づく）。出る 時と 形が かわる 時は 不定期
BOLT_GLOW = ((0, (1, 1, 1), 1.0), (1.0, (1, .85, .45), 1.3), (3.5, (1, .5, .12), .85), (10, (1, .3, .06), .35))   # 玉の まわりの 雷と 同じ 色
SB_FR = (22, 39)                         # 玉から 画面の はしへの 雷が 出る コマ（0.73〜1.3秒：玉に なって から）
SB_ENV = (.85, 1.0, 1.0, .8, .5, .25)    # その 雷の コマごとの 明るさ（ついて すぐ のびきり、ビリビリ して 消える）
SB_DIRS = (-140, -112, -68, -40, -8, 12, 40, 68, 112, 140, 172, 192)   # 方向（度：0＝右・90＝下）


def poly_len(pts):
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    return acc


def macro_path(rng, a, b, style):
    """a → b の 大きな ギザギザ：'zig'＝のこぎり（右左に 大きく）・'step'＝まっすぐ 進んで 横に 段・'wander'＝うねって から のこぎり"""
    ax, ay = a
    bx, by = b
    L = math.hypot(bx - ax, by - ay) or 1.0
    ux, uy = (bx - ax) / L, (by - ay) / L
    px, py = -uy, ux
    pts = [a]
    if style == 'zig':
        n = rng.randint(4, 7)
        amp = L * rng.uniform(.07, .13)
        for i in range(1, n):
            s = (i + rng.uniform(-.3, .3)) / n
            off = amp * (1 if i % 2 else -1) * rng.uniform(.6, 1.3)
            pts.append((ax + ux * L * s + px * off, ay + uy * L * s + py * off))
    elif style == 'step':
        n = rng.randint(3, 5)
        off = 0.0
        for i in range(1, n + 1):
            s = i / (n + 1)
            pts.append((ax + ux * L * s + px * off, ay + uy * L * s + py * off))
            off += rng.choice((-1, 1)) * L * rng.uniform(.06, .12)
            s2 = s + rng.uniform(.01, .04)
            pts.append((ax + ux * L * s2 + px * off, ay + uy * L * s2 + py * off))
    else:
        n = rng.randint(5, 8)
        sag = L * rng.uniform(.12, .22) * rng.choice((-1, 1))
        for i in range(1, n):
            s = i / n
            off = sag * math.sin(math.pi * s) + (L * .06 * (1 if i % 2 else -1) if s > .4 else 0.0)
            pts.append((ax + ux * L * s + px * off, ay + uy * L * s + py * off))
    pts.append(b)
    return pts


def fine_jag(rng, pts, rough=(.16, .22, .28)):
    """大きな ギザギザの 間を 細かく ギザギザに（コマごとに かえると ビリビリ 動く）"""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        out += KM._disp_ms(rng, a, b, rough)[1:]
    return out


def draw_taper(mask, pts, w0, w1, val, grow=1.0, gam=1.3):
    """太さ w0 → w1（画面の px）の 線（はじめから grow の 割合まで）"""
    acc = poly_len(pts)
    L = acc[-1] or 1.0
    lim = L * grow
    for i in range(len(pts) - 1):
        if acc[i] >= lim:
            break
        a, b = pts[i], pts[i + 1]
        if acc[i + 1] > lim:
            f = (lim - acc[i]) / max(1e-6, acc[i + 1] - acc[i])
            b = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        s = ((acc[i] + acc[i + 1]) / 2) / L
        wd = w0 + (w1 - w0) * s ** gam
        cv2.line(mask, (int(a[0] * S * 8), int(a[1] * S * 8)), (int(b[0] * S * 8), int(b[1] * S * 8)), float(val),
                 max(1, int(round(wd * S))), cv2.LINE_AA, shift=3)


def edge_point(c, ang):
    """c から ang（度）の 向きに のばして 画面の はし（少し 外）に 当たる 所（下は 床まで）"""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    best = 1e9
    for lim, d, o in ((-8.0, dx, c[0]), (398.0, dx, c[0]), (-8.0, dy, c[1]), (BASE + 18.0, dy, c[1])):
        if abs(d) > 1e-6:
            k = (lim - o) / d
            if k > 0:
                best = min(best, k)
    return c[0] + dx * best, c[1] + dy * best


def sphere_bolt_events():
    """玉から 画面の はしへの 雷：(出る コマ, 方向（度）, 形, 種, 長さ（コマ）)。同じ 向きは つづけて 出さない（同じ 所の 点めつを ふやさない）"""
    def f():
        rng = random.Random(6100)
        ev, last = [], {}
        fi = SB_FR[0]

        def area(d):                               # 先の 場所（同じ 場所には 10コマ あけて 出す）
            e = edge_point(ORB_C, d)
            return (int(e[0] // 130), int(e[1] // 280))
        while fi <= SB_FR[1]:
            sh = shape_at(fi / FPS)
            big = sh is not None and sh['W'] > 150             # 玉が 大きい 間は 横 向きを さける（画面の はしまで 近すぎる）
            for _ in range(rng.choice((1, 1, 2))):
                cand = [d for d in SB_DIRS if fi - last.get(area(d), -99) > 10 and not (big and abs(math.sin(math.radians(d))) < .45)
                        and not (fi < 32 and math.sin(math.radians(d)) > .3)]     # はじめは 下の すみへ 行かない（爆発・床の 光と かさねない）
                if not cand:
                    continue
                d = rng.choice(cand)
                last[area(d)] = fi
                ev.append((fi, d + rng.uniform(-10, 10), rng.choice(('zig', 'zig', 'step', 'wander')), rng.randrange(1 << 30), rng.randint(4, 6)))
            fi += rng.choice((1, 2, 2, 3))
        return ev
    return cache('sbev', f)


def sphere_bolts(mask, t, fi):
    """玉から 画面の はしへ はしる 雷（大きな ギザギザ・先ほど 太い・ビリビリ）"""
    sh = shape_at(t)
    if sh is None:
        return
    cx, cy, R = sh['cx'], sh['ye'], sh['W']
    for f0_, ang, style, seed, life in sphere_bolt_events():
        age = fi - f0_
        if not (0 <= age < life):
            continue
        g = SB_ENV[min(age, len(SB_ENV) - 1)] if age < life - 2 else SB_ENV[len(SB_ENV) - (life - age)]
        rs = random.Random(seed)
        w1 = rs.uniform(3.8, 6.0)
        a_ = math.radians(ang + rs.uniform(-6, 6))
        st = (cx + (R - 3) * math.cos(a_), cy + (R - 3) * math.sin(a_))
        en = edge_point((cx, cy), ang)
        macro = macro_path(rs, st, en, style)
        brs = [(rs.randint(1, len(macro) - 2), rs.uniform(-1, 1), rs.uniform(.15, .3)) for _ in range(rs.randint(1, 2))] if len(macro) > 2 else []
        mid = fine_jag(random.Random(seed + 1), macro, (.14, .2))      # 中くらいの ギザギザ（雷ごとに 決まる）
        rj = random.Random(seed * 7 + fi)                      # ビリビリ：いちばん 細かい ギザギザだけ コマごとに 少し かわる
        pts = [mid[0]]
        for q0, q1 in zip(mid, mid[1:]):
            pts += KM._disp_ms(rj, q0, q1, (.12,))[1:]
        grow = min(1.0, (age + 1) / 2)
        draw_taper(mask, pts, .8, w1, g, grow)
        Ltot = poly_len(macro)[-1]
        for i, sgn, fr in brs:
            if grow < (i / (len(macro) - 1)):
                continue
            p = macro[i]
            q = macro[i + 1]
            ang2 = math.atan2(q[1] - p[1], q[0] - p[0]) + sgn * .9
            ln = Ltot * fr
            br = fine_jag(random.Random(seed + 2 + i), [p, (p[0] + ln * math.cos(ang2), p[1] + ln * math.sin(ang2))], (.25, .3, .35))
            draw_taper(mask, br, .7, w1 * .45, g * .8)


def vbolt_changes(j, f0, f1):
    """上から 下への 雷の 上の 方の 形が かわる コマ（不定期：4〜8コマごと）"""
    rng = random.Random(3300 + j)
    out, f = [], f0
    while f <= f1:
        out.append(f)
        f += rng.choice((5, 6, 8, 10))
    return out


def vertical_bolts(mask, t, fi):
    """上から 下への 雷（前の 白い 光の 帯の 所）：上は 細く 下ほど 太い・だんだん 太く（手前に 近づく）。
       上の 方は 不定期に ガクッと 形が かわる（横に ずれる 段）・下の 太い 所は 動かさない（点めつを ふやさない）"""
    for j, t0, t1 in RIBS:
        if not (t0 <= t <= t1):
            continue
        p = KM.RIBBONS[j][0]
        f0, f1 = int(math.ceil(t0 * FPS)), int(t1 * FPS)
        phase = len([c for c in vbolt_changes(j, f0, f1) if c <= fi])
        age = fi - f0
        grow = min(1.0, (age + 1) / 2)                       # 上から 下へ 2コマで のびる
        life = (t - t0) / max(1e-3, t1 - t0)
        g = (1 - sstep(t1 - .2, t1, t)) * (.85 + .15 * min(1.0, age / 2))
        if g <= 0:
            continue
        base = KS.bez(p, np.linspace(0, 1, 11))
        pts = []                                             # (x, y, もとの 番号)
        for i, (x, y) in enumerate(base):
            u = i / 10
            wgt = max(0.0, 1 - u / .6)                       # 上の 6割だけ 動く
            up = random.Random(5000 + 97 * j + 1000 * phase + i).uniform(-1, 1) * 11
            low = random.Random(5000 + 97 * j + i).uniform(-1, 1) * 4
            pts.append((float(x) + up * wgt + low, float(y), float(i)))
        rp = random.Random(6000 + 97 * j + 1000 * phase)
        for _ in range(rp.randint(1, 2)):                    # 横に ずれる 段（上の 方）
            k = rp.randint(1, 4)
            dx = rp.choice((-1, 1)) * rp.uniform(6, 12)
            x, y, bi = pts[k]
            ky = y
            pts.insert(k + 1, (x + dx, y + rp.uniform(2, 5), bi + .5))
            for q in range(k + 2, len(pts)):
                xq, yq, bq = pts[q]
                pts[q] = (xq + dx * max(0.0, 1 - (yq - ky) / 260), yq, bq)
        out = [(pts[0][0], pts[0][1])]
        for (ax, ay, ai), (bx, by, bi) in zip(pts, pts[1:]):
            lowseg = ai / 10 >= .6
            sd = 9000 + 97 * j + int(ai * 26) + (0 if lowseg else 1000 * phase)
            out += KM._disp_ms(random.Random(sd), (ax, ay), (bx, by), (.1, .16, .22))[1:]
        rsh = random.Random(7000 + 31 * j + fi)               # 上の 細い 所だけ コマごとに ふるえる
        out = [(x + rsh.uniform(-1, 1) * .6 * max(0.0, 1 - (y + 40) / 500), y) for x, y in out]
        cut = []                                              # 床で 止める（床に 当たる 所が 光る）
        for q0, q1 in zip(out, out[1:]):
            cut.append(q0)
            if q1[1] >= BASE + 2:
                f_ = (BASE + 2 - q0[1]) / max(1e-6, q1[1] - q0[1])
                cut.append((q0[0] + (q1[0] - q0[0]) * f_, BASE + 2.0))
                break
        else:
            cut.append(out[-1])
        w1 = 2.5 + 5.5 * min(1.0, life * 1.3)                 # だんだん 太く（手前に 近づく）
        draw_taper(mask, cut, .7, w1, g, grow, 1.6)
        if grow >= 1.0 and cut[-1][1] >= BASE:
            ex, ey = cut[-1]
            cv2.ellipse(mask, (int(ex * S * 8), int(ey * S * 8)), (int(w1 * 2.2 * S * 8), int(w1 * .7 * S * 8)), 0, 0, 360, float(g * .8), -1, cv2.LINE_AA, shift=3)


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


GOLD_C = ORB_C                   # 金の 光の まん中（玉が 小さく なって 入る 所）


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
        lift_blast(img, t)
        surge(img, t)
        bm = np.zeros((H, W), np.float32)
        vertical_bolts(bm, t, fi)
        sphere_bolts(bm, t, fi)
        lift_arcs(bm, t, fi)
        glow_add(img, bm, BOLT_GLOW)
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
