"""神様的中の 絵（WebP）：まさちゃん「スタート一個目の動画にして、次に、二個目の動画にして、文章に
   万馬券（きせき）は偶然にあらず 天眼（テンゲル）が導く必然なり を入れて！ 三個目の動画をその後に入れて、GODの文字を、神様的中にして！」
   - 送ってくれた 動画は 見るだけ（なぞらない・動画の 絵や 音は 使わない）。字・背景・金の 粒・鳥居の わくは ここで 一から 作った
   - 字の 形は Dela Gothic One（SIL OFL・アプリに 入れて いる フォント：ios/fonts）の 形を fontTools で 読んで librsvg で ぬる
   - 金の 立体の 字：前の 面（金の ふちの 面取り＋字の 面）＋ななめ うしろへの 厚み（こい 茶色の 側面・うしろの はしに 金の 線）＋外の こい ふち。
     光（左上・手前）・金の 映りこみ（上から 下へ）・つや・キラッ を numpy で
   - 出す 絵（すき通しの ある WebP。大きさと 置き場所は kami_layers.json）：
       ① 青い 嵐（はじまり）：gd_burst（はじめの 光の 爆発）・gd_fire（赤い 炎の 一瞬）・
          gd_ring（立体の 金の 輪：まん中へ むかう 厚み）・gd_blast（金の 爆発）
          青い 嵐の 絵（第4.46版で 作り直し）は flat/kami_storm.py：gd_storm・gd_vein1／gd_vein2・gd_dome・gd_fall・gd_fmask・gd_rib・gd_surge・gd_rock
       ② 金の 字：gd_sky（金の 雲の 空）・gd_cu1（万馬券（きせき）の 寄り）・gd_cu2（天眼（テンゲル）の 寄り）・gd_txt（4行の 文）
       ③ 神様的中：gd_c1〜gd_c4（神・様・的・中 の 寄り：しまの 金の 字）・gd_logo（神様／的中）・gd_frame（金の 鳥居）・gd_nug（金の 粒 8つ）
   python3 flat/kami_art.py <出力フォルダ> [名前 …]   → <名前>.webp と kami_layers.json（名前を つけた 時は その 絵の 所だけ かわる）
   （絵を 作りなおしたら キャンバスに 入れて、id を kami_blobs.json に。絵は リポジトリに 入れない）"""
import sys, os, json, math
import numpy as np
import cv2
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
from cute_horse import svg_rgba
import kami_storm as KS

FONT_PATH = os.path.join(K, '..', 'ios', 'fonts', 'DelaGothicOne-Regular.ttf')
SS = 3                     # 細かく 作って もどす 倍率（ふちを なめらかに）
L_DIR = np.array([-.45, -.62, .64])          # 光（左上・手前）
L_DIR = L_DIR / np.linalg.norm(L_DIR)
R_DIR = np.array([.55, .55, .63])            # はねかえりの 光（右下から 少し）
R_DIR = R_DIR / np.linalg.norm(R_DIR)
# 金（上から 下への 映りこみ：明るい 空 → 金 → 地平の こい 線 → 明るい 金 → こい 金）
GOLD = ((0.0, (255, 252, 226)), (0.20, (255, 222, 92)), (0.40, (232, 160, 20)), (0.47, (132, 74, 4)), (0.52, (255, 232, 140)),
        (0.70, (246, 178, 26)), (0.88, (176, 102, 8)), (1.0, (96, 52, 4)))
EDGE = (30, 14, 2)         # いちばん 外の こい 茶色の ふち


# ---------------------------------------------------------------- 字の 形（Dela Gothic One）
_F = {}


def font():
    if not _F:
        f = TTFont(FONT_PATH)
        _F['gs'], _F['cm'] = f.getGlyphSet(), f.getBestCmap()
    return _F['gs'], _F['cm']


def gpath(c):
    """1文字の 形：(path（フォントの 単位・y は 上向き）, 箱 (x0, y0, x1, y1), 送り)"""
    gs, cm = font()
    g = gs[cm[ord(c)]]
    pen, bp = SVGPathPen(gs), BoundsPen(gs)
    g.draw(pen)
    g.draw(bp)
    return pen.getCommands(), bp.bounds, g.width


def run(chars, x=0.0, base=0.0, track=-40.0):
    """1行の 字の ならび：chars＝[(字, 大きさ), …]（大きさ 1＝1000）。字は 下の 線（base）に そろえる → (items, 箱（y は 下向き）, 行の はば)
       items：(path, x, base, 大きさ)。track：字の 間の つめ（1000 単位）"""
    items = []
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for c, s in chars:
        d, (bx0, by0, bx1, by1), adv = gpath(c)
        items.append((d, x, base, s))
        x0, x1 = min(x0, x + bx0 * s), max(x1, x + bx1 * s)
        y0, y1 = min(y0, base - by1 * s), max(y1, base - by0 * s)
        x += adv * s + track * s
    return items, (x0, y0, x1, y1), x - track * chars[-1][1]


def union_box(*bs):
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


def shift_items(items, dx, dy):
    return [(d, x + dx, y + dy, s) for d, x, y, s in items]


def mask(items, box, k, pad):
    """形の ぬり（0〜1）：1000 単位 → 絵の 画素（k：1 単位あたりの 画素・pad：まわりの あき 画素（左右・上下））"""
    x0, y0, x1, y1 = box
    px, py = pad if isinstance(pad, tuple) else (pad, pad)
    W, H = int(np.ceil((x1 - x0) * k + 2 * px)), int(np.ceil((y1 - y0) * k + 2 * py))
    s = SS
    paths = ''.join(f'<path d="{d}" fill="#fff" transform="translate({((tx - x0) * k + px) * s:.2f} {((ty - y0) * k + py) * s:.2f}) '
                    f'scale({k * s * sc:.5f} {-k * s * sc:.5f})"/>' for d, tx, ty, sc in items)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * s}" height="{H * s}" viewBox="0 0 {W * s} {H * s}">{paths}</svg>'
    a = svg_rgba(svg, W * s, H * s)[..., 3]
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)


# ---------------------------------------------------------------- 形の 道具
def dist_in(a, thr=.5):
    return cv2.distanceTransform((a > thr).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def grow(a, r):
    """r 画素 ふとらせる（まるく）"""
    if r <= 0:
        return a
    d = cv2.distanceTransform((a < .5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return np.clip(r + .5 - d, 0, 1).astype(np.float32)


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    xs = np.array([s for s, _ in stops])
    cs = np.array([c for _, c in stops], np.float32) / 255
    return np.stack([np.interp(t, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def bevel(d, w):
    """面取り：ふちで 0 → w で 1（まるく）"""
    u = np.clip(d / max(w, 1e-3), 0, 1)
    return 1 - (1 - u) ** 2


def normals_of(h, blur=0.0):
    if blur:
        h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), blur)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def out_normals(b):
    """形の 外向きの 向き（2D）：ふちからの きょりの 傾き"""
    sdf = cv2.distanceTransform((b < .5).astype(np.uint8), cv2.DIST_L2, 5) - cv2.distanceTransform((b >= .5).astype(np.uint8), cv2.DIST_L2, 5)
    sdf = cv2.GaussianBlur(sdf.astype(np.float32), (0, 0), 2.0)
    gx = cv2.Sobel(sdf, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(sdf, cv2.CV_32F, 0, 1, ksize=3)
    L = np.sqrt(gx * gx + gy * gy) + 1e-6
    return gx / L, gy / L


def over(dst, src):
    """premultiplied RGBA を 上に 重ねる"""
    a = src[..., 3:4]
    return src + dst * (1 - a)


def shift(img, dx, dy):
    H, W = img.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def smoothstep(e0, e1, x):
    u = np.clip((x - e0) / (e1 - e0), 0, 1)
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- 金の 立体の 字
# 字の 面の しま（GOD の ような 金の 字：上から 明るい 黄色 → 金 → だいだい → 赤 → こい 赤。波の ような さかいめ）
STRIPE = ((0.0, (255, 250, 196)), (.16, (255, 226, 70)), (.30, (255, 186, 28)), (.36, (255, 236, 120)), (.44, (255, 164, 18)),
          (.58, (238, 92, 8)), (.66, (255, 196, 52)), (.74, (226, 72, 6)), (.88, (176, 34, 4)), (1.0, (120, 18, 2)))
SIDE_NEAR = np.array((70, 40, 8), np.float32) / 255      # 側面（前に 近い 所：こい 金）
SIDE_FAR = np.array((12, 5, 1), np.float32) / 255        # 側面（うしろ：ほぼ 黒い 茶色）
SIDE_HI = np.array((255, 200, 90), np.float32) / 255     # 側面の 光る 所（右を 向いた 面・かど）
BACK_EDGE = np.array((240, 176, 60), np.float32) / 255   # うしろの はしの 金の 線


def front(a, em, rim, style='gold', glints=4, seed=1, face_dark=.0, stripe_box=None, env_box=None):
    """前の 面：金の ふち（面取り）＋字の 面（gold：金の 映りこみ・stripe：しま）→ premultiplied RGBA（alpha＝前の 面）
       rim＝(ふちの 太さ, 外の 面取り, 内の 面取り)（1文字の 何倍）。env_box：金の 映りこみの 上と 下（行ごとに そろえる・なければ 絵の 上下）"""
    H, W = a.shape
    body = grow(a, rim[0] * em)
    db, da = dist_in(body), dist_in(a)
    H1, H2 = .07 * em, .035 * em
    h = H1 * bevel(db, rim[1] * em) - (H1 - H2) * bevel(da, rim[2] * em)
    h += .01 * em * np.clip(da / (.1 * em), 0, 1)
    n = normals_of(h, max(.6, .003 * em))
    ndl = np.clip(n @ L_DIR, 0, 1)
    ndr = np.clip(n @ R_DIR, 0, 1)
    hv = L_DIR + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    ndh = np.clip(n @ hv, 0, 1)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    ye = ys
    if env_box:
        ye = np.clip((ys * H - env_box[0]) / max(1.0, env_box[1] - env_box[0]), -.2, 1.2)
    t = .1 + .8 * ye + .55 * n[..., 1] - .12 * n[..., 0]
    col = ramp(t, GOLD)                                     # ふち：金の 映りこみ
    # ななめの 映りこみの 帯（みがいた 金：明るい 帯と 暗い 帯）＋細い 光の すじ
    dg = (xs * W * .82 + ys * H * .57) / (1.25 * em) + .35 * n[..., 0]
    band = .5 + .5 * np.sin(2 * np.pi * dg + 1.1)
    col *= (.66 + .6 * band ** 3)[..., None]
    if style == 'gold':
        dg2 = (xs * W * .5 + ys * H * .87) / (.55 * em) + .3 * n[..., 0] + .15 * np.sin(xs * W / em * 2.1)
        streak = (.5 + .5 * np.sin(2 * np.pi * dg2)) ** 30
        inner0 = smoothstep(.0, 1.0, (da - rim[2] * em * .8) / (rim[2] * em * .5))
        col += (np.array([1.0, .93, .7], np.float32) * (streak * inner0 * .45)[..., None])
    if style == 'stripe':
        # 字の 面：しま（字ごとの 箱の 高さで）＋ゆるい 波＋左上の つや
        y0, y1 = stripe_box if stripe_box else (0, H)
        u = (np.arange(H, dtype=np.float32)[:, None] - y0) / max(1, y1 - y0)
        u = u + .025 * np.sin(xs * W / em * 5.2 + 1.3) + .012 * np.sin(xs * W / em * 11.0)
        fc = ramp(u, STRIPE)
        gl = np.exp(-((u - .2) / .045) ** 2) * .35 + np.exp(-((u - .62) / .03) ** 2) * .22    # 横の つやの 帯
        fc = np.clip(fc + gl[..., None] * np.array([1, .95, .8], np.float32), 0, 1)
        inner = smoothstep(.0, 1.0, (da - rim[2] * em * .6) / (rim[2] * em * .5))
        col = col * (1 - inner[..., None]) + fc * inner[..., None]
    elif face_dark:
        inner = smoothstep(.0, 1.0, (da - rim[2] * em * .6) / (rim[2] * em * .5))
        col = col * (1 - face_dark * inner[..., None])
    col *= (.62 + .55 * ndl)[..., None]
    col += np.array([.55, .38, .12], np.float32) * (.35 * ndr ** 3)[..., None]
    spec = ndh ** 70 * 1.25 + ndh ** 12 * .2
    col += np.array([1.0, .97, .86], np.float32) * spec[..., None]
    col = np.clip(col, 0, 1)
    # ふちと 字の 面の さかいめに こい 線
    seam = np.clip(1 - np.abs(da - .8) / 1.5, 0, 1) * (body > .5)
    col *= (1 - .55 * cv2.GaussianBlur(seam.astype(np.float32), (0, 0), .7))[..., None]
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = col * body[..., None]
    out[..., 3] = body
    if glints:
        add_glints(out, spec * (body > .5), em, glints)
    return out, body


def add_glints(out, s2, em, n):
    """キラッ（つやの いちばん 強い 所に 小さな 光の 星）"""
    H, W = s2.shape
    s2 = s2.copy()
    pts = []
    for _ in range(n):
        k = int(np.argmax(s2))
        yy, xx = divmod(k, W)
        if s2[yy, xx] < .6:
            break
        pts.append((xx, yy))
        cv2.circle(s2, (xx, yy), int(.4 * em), 0, -1)
    for xx, yy in pts:
        L = int(.09 * em)
        r = int(.14 * em) + 2
        x0, x1, y0, y1 = max(0, xx - r), min(W, xx + r + 1), max(0, yy - r), min(H, yy + r + 1)
        star = np.zeros((y1 - y0, x1 - x0), np.float32)
        cx, cy = xx - x0, yy - y0
        lw = max(1, int(.014 * em))
        cv2.line(star, (cx - L, cy), (cx + L, cy), 1.0, lw, cv2.LINE_AA)
        cv2.line(star, (cx, cy - L), (cx, cy + L), 1.0, lw, cv2.LINE_AA)
        star = cv2.GaussianBlur(star, (0, 0), .9)
        yy_, xx_ = np.mgrid[y0:y1, x0:x1]
        fall = np.exp(-(((xx_ - xx) ** 2 + (yy_ - yy) ** 2) / (2 * (.05 * em) ** 2)))
        core = np.exp(-(((xx_ - xx) ** 2 + (yy_ - yy) ** 2) / (2 * (.02 * em) ** 2)))
        g = np.clip(star * fall + core, 0, 1)
        sub = out[y0:y1, x0:x1]
        sub[..., :3] = sub[..., :3] + (1 - sub[..., :3]) * g[..., None] * np.clip(sub[..., 3:] * 1.5, 0, 1)
        sub[..., 3] = np.maximum(sub[..., 3], g * .9)


def extrude(body, ext, em, steps=None):
    """うしろへの 厚み：前の 面の 形を ext（画素）へ ずらして 重ねる（うしろ → 前）→ premultiplied RGBA"""
    H, W = body.shape
    ex, ey = ext
    L = math.hypot(ex, ey)
    n = steps or max(2, int(math.ceil(L / .8)))
    nx, ny = out_normals(body)
    # 側面の 色（前の 面の ふちの 向きで）：右を 向く 面は 金に 光る（せまく）・下を 向く 面は 暗い・かどは 金の 線
    lit = np.clip(nx * .9 - ny * .2, 0, 1) ** 6 * .75
    rim_lit = np.clip(-nx * .3 - ny * .9, 0, 1) ** 3       # 上を 向く 面（すこし 光る）
    cg = np.abs(cv2.Sobel(nx, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(nx, cv2.CV_32F, 0, 1, ksize=3)) + \
        np.abs(cv2.Sobel(ny, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(ny, cv2.CV_32F, 0, 1, ksize=3))
    band = np.clip(1 - np.abs(cv2.distanceTransform((body >= .5).astype(np.uint8), cv2.DIST_L2, 5) - 1.0) / 2.0, 0, 1)
    corner = np.clip((cv2.GaussianBlur(cg * band, (0, 0), 1.2) - .9) * .5, 0, 1)
    lit = cv2.GaussianBlur(np.clip(lit + corner * .9, 0, 1).astype(np.float32), (0, 0), 1.2)
    acc = np.zeros((H, W, 4), np.float32)
    # うしろの はしの 金の 線（いちばん うしろより 少し 先を 金で）
    edge_a = shift(body, ex * (1 + 1.4 / L), ey * (1 + 1.4 / L))
    acc[..., :3] = BACK_EDGE * edge_a[..., None]
    acc[..., 3] = edge_a
    for i in range(n, 0, -1):
        s = i / n
        a_s = shift(body, ex * s, ey * s)
        l_s = shift(lit, ex * s, ey * s)
        r_s = shift(rim_lit, ex * s, ey * s)
        base = SIDE_NEAR * (1 - s) ** 1.2 + SIDE_FAR * (1 - (1 - s) ** 1.2)
        col = base[None, None, :] + (SIDE_HI[None, None, :] - base[None, None, :]) * (l_s * (1 - .6 * s))[..., None]
        col = col + .18 * r_s[..., None] * (1 - s)
        src = np.dstack([np.clip(col, 0, 1) * a_s[..., None], a_s])
        acc = over(acc, src)
    return acc


def gold3d(a, em, ext=(.06, .1), rim=(.05, .03, .02), style='gold', glints=4, edge=.018, face_dark=0.0, stripe_box=None, env_box=None):
    """金の 立体の 字：外の こい ふち → 厚み → 前の 面。ext：厚みの 向き（1文字の 何倍）→ premultiplied RGBA"""
    fr, body = front(a, em, rim, style, glints, face_dark=face_dark, stripe_box=stripe_box, env_box=env_box)
    ex = (ext[0] * em, ext[1] * em)
    sd = extrude(body, ex, em)
    allm = np.maximum(body, sd[..., 3])
    ring = np.clip(grow(allm, edge * em) - allm, 0, 1)
    out = np.zeros_like(fr)
    out[..., :3] = np.array(EDGE, np.float32) / 255 * ring[..., None]
    out[..., 3] = ring
    out = over(out, sd)
    out = over(out, fr)
    return out


def save(img, fn, q=88):
    a = np.clip(img[..., 3], 0, 1)
    rgb = np.where(a[..., None] > 1e-4, img[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    u8 = (np.clip(np.dstack([rgb, a]), 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(fn, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, q])


def save_rgb(img, fn, q=82):
    u8 = (np.clip(img[..., :3], 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(fn, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, q])


def crop(img, m=2):
    yy, xx = np.where(img[..., 3] > .003)
    H, W = img.shape[:2]
    y0, y1, x0, x1 = max(0, yy.min() - m), min(H, yy.max() + m + 1), max(0, xx.min() - m), min(W, xx.max() + m + 1)
    return img[y0:y1, x0:x1], (x0, y0)


# ---------------------------------------------------------------- ノイズ（雲・炎・嵐）
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


def radial(h, w, cx, cy, r, p=2.0, sx=1.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - cx) / sx) ** 2 + (yy - cy) ** 2) / r
    return np.clip(1 - d, 0, 1) ** p


def rays(h, w, cx, cy, n, seed, width=.5, soft=2.0):
    """光の 筋（cx, cy から 放射）：0〜1"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = np.arctan2(yy - cy, xx - cx)
    rng = np.random.default_rng(seed)
    t = np.zeros((h, w), np.float32)
    for _ in range(n):
        a0 = rng.uniform(-np.pi, np.pi)
        wd = rng.uniform(.3, 1.0) * width * np.pi / n
        da = np.angle(np.exp(1j * (ang - a0)))
        t = np.maximum(t, np.clip(1 - np.abs(da) / wd, 0, 1) ** soft * rng.uniform(.4, 1.0))
    return t


def cloud_layer(col, W, H, xs, ys, seed, ytop, amp, cells, bright, deep, bowl):
    """雲の 海の 1つの 層：上の ふち（ytop＋ノイズ・はしほど 高い）は 光って、下へ 暗く（ふわっと した きめ）"""
    n = fbm(H, W, cells, seed, 7, .56)
    edge = ytop - amp * (n - .5) * 2 - bowl * np.abs(xs - .5) ** 2 * 4
    u = ys - edge
    dens = smoothstep(-.004, .02, u + .03 * (fbm(H, W, 40, seed + 3, 3) - .5))
    tex = fbm(H, W, cells * 3, seed + 7, 5, .55)
    lv = bright - np.clip(u, 0, 1) * deep + (tex - .5) * .4
    lv = lv + smoothstep(.0, .06, .06 - np.clip(u, 0, .06)) * .35
    ccol = ramp(lv, ((0, (104, 44, 6)), (.35, (184, 96, 20)), (.7, (250, 180, 70)), (1, (255, 246, 214))))
    return col * (1 - dens[..., None]) + ccol * dens[..., None]


def sky(W, H, seed=8):
    """金の 雲の 空（文の うしろ）：上に まぶしい 光と 光の 筋・下に 金の 雲の 海（4つの 層：上の ふちが 光る）→ RGB"""
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    col = ramp(ys, ((0, (255, 230, 150)), (.28, (250, 196, 84)), (.6, (232, 148, 40)), (.85, (192, 104, 18)), (1, (130, 62, 8))))
    sx, sy = W * .5, H * .07
    sun = radial(H, W, sx, sy, H * .42, 2.0, 1.4)
    col = col + (np.array([1.0, .98, .86], np.float32) - col) * sun[..., None] * .9
    r = rays(H, W, sx, sy, 22, seed + 1, 1.1, 1.2)
    r = cv2.GaussianBlur(r, (0, 0), W * .01) * np.clip(1 - ys * 1.25, 0, 1)
    col = np.clip(col + r[..., None] * np.array([.3, .24, .1], np.float32) * .7, 0, 1)
    for k, (yt, amp, cells, br, dp, bowl) in enumerate(((.54, .05, 6, .95, 1.4, .26), (.67, .06, 5, .9, 1.7, .18),
                                                         (.8, .07, 4, .86, 2.0, .08), (.92, .06, 4, .8, 2.2, .0))):
        col = cloud_layer(col, W, H, xs, ys, seed + 10 * (k + 1), yt, amp, cells, br, dp, bowl)
    vig = 1 - .28 * smoothstep(.55, 1.2, np.sqrt(((xs - .5) * 1.5) ** 2 + (ys - .45) ** 2) * 1.6)
    return np.clip(col * vig[..., None], 0, 1)


# ---------------------------------------------------------------- ① 青い 嵐（はじまり）
def lightning_lines(H, W, segs, seed, rough=.45, depth=7, branches=3):
    """細い 雷の 線（いく本も・えだ つき）を 0〜1 の 絵に"""
    rng = np.random.default_rng(seed)
    img = np.zeros((H, W), np.float32)

    def disp(a, b, dep, r):
        pts = [a, b]
        for _ in range(dep):
            nw = [pts[0]]
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                L = math.hypot(bx - ax, by - ay) or 1
                nx, ny = -(by - ay) / L, (bx - ax) / L
                o = rng.normal(0, r * L / 2)
                nw += [((ax + bx) / 2 + nx * o, (ay + by) / 2 + ny * o), (bx, by)]
            pts = nw
        return pts
    for (a, b, w, lv) in segs:
        main = disp(a, b, depth, rough)
        cv2.polylines(img, [np.int32(np.array(main) * 8)], False, lv, max(1, int(w)), cv2.LINE_AA, shift=3)
        for _ in range(branches):
            i0 = rng.integers(len(main) // 6, len(main) * 5 // 6)
            p = main[i0]
            ang = math.atan2(b[1] - a[1], b[0] - a[0]) + rng.choice((-1, 1)) * rng.uniform(.4, 1.1)
            ln = rng.uniform(.12, .3) * math.hypot(b[0] - a[0], b[1] - a[1])
            br = disp(p, (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang)), depth - 2, rough * 1.1)
            cv2.polylines(img, [np.int32(np.array(br) * 8)], False, lv * .7, 1, cv2.LINE_AA, shift=3)
    return img


def burst(W, H, seed=41):
    """はじめの 光の 爆発（まん中が 白・水色と 青と 紫の 光の 筋・電気の すじ）→ RGB"""
    ys = (np.arange(H, dtype=np.float32)[:, None]) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :]) * np.ones((H, 1), np.float32)
    cx, cy = W * .5, H * .46
    rr = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / H
    col = ramp(rr * 1.6, ((0, (255, 255, 255)), (.12, (230, 250, 255)), (.3, (120, 210, 255)), (.55, (60, 70, 230)), (.8, (40, 10, 110)), (1.2, (10, 2, 30))))
    ry = rays(H, W, cx, cy, 60, seed, .9, 1.0)
    ry = cv2.GaussianBlur(ry, (0, 0), 1.2)
    col = col + ry[..., None] * np.array([.6, .85, 1.0], np.float32) * np.clip(1.2 - rr, 0, 1)[..., None]
    ry2 = rays(H, W, cx, cy, 24, seed + 3, .5, 1.5)
    col = col + ry2[..., None] * np.array([.7, .3, 1.0], np.float32) * .5 * np.clip(1 - rr, 0, 1)[..., None]
    rng = np.random.default_rng(seed)
    segs = [((cx, cy), (cx + math.cos(a) * H * .7, cy + math.sin(a) * H * .7), 1, 1.0) for a in rng.uniform(0, 2 * np.pi, 10)]
    ln = lightning_lines(H, W, segs, seed + 1, .35, 7, 2)
    col = col + ln[..., None] * np.array([.8, .95, 1.0], np.float32) * .8
    return np.clip(col, 0, 1)


def fire(W, H, seed=51):
    """赤い 炎の 一瞬（青い 嵐の 前）：ゆがめた ノイズの 炎＋まん中の 光の 柱 → RGB"""
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    q1 = fbm(H, W, 5, seed, 5)
    q2 = fbm(H, W, 5, seed + 9, 5)
    mx = (xs + .25 * (q1 - .5)) * W
    my = (ys + .25 * (q2 - .5)) * H
    base = fbm(H, W, 7, seed + 3, 6, .55)
    f = cv2.remap(base, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    t = smoothstep(.35, .8, f)
    col = ramp(t, ((0, (24, 2, 20)), (.3, (120, 8, 60)), (.55, (230, 40, 90)), (.75, (255, 120, 30)), (.9, (255, 210, 80)), (1, (255, 250, 200))))
    pil = np.exp(-((xs - .5) / .03) ** 2) * .9 + np.exp(-((xs - .5) / .08) ** 2) * .4
    col = col + np.array([1.0, .8, .95], np.float32) * pil[..., None]
    return np.clip(col, 0, 1)


def extrude_radial(body, cx, cy, depth, steps=None):
    """まん中へ むかう 厚み（金の 輪の かたまり）：前の 面の 形を まん中へ 小さく して 重ねる（うしろ → 前）→ premultiplied RGBA。
       側面は 左上を 向く 所が 光る（こい 金 → 黒に 近い 茶色）・うしろの はしに 金の 線"""
    H, W = body.shape
    n = steps or max(4, int(depth * max(H, W) / 1.2))
    nx, ny = out_normals(body)
    lit = np.clip(-(nx * -.6 + ny * -.8), 0, 1)                     # まん中を 向く 側面：左上の 光を うける 向き
    lit = np.clip(-nx * .6 - ny * .8, 0, 1) * 0 + np.clip(nx * -.6 + ny * -.8, 0, 1)
    spec = np.clip(nx * -.6 + ny * -.8, 0, 1) ** 12
    acc = np.zeros((H, W, 4), np.float32)

    def warp(img, k):
        M = np.float32([[k, 0, cx * (1 - k)], [0, k, cy * (1 - k)]])
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    e = warp(body, 1 - depth * 1.05)
    acc[..., :3] = BACK_EDGE * e[..., None]
    acc[..., 3] = e
    for i in range(n, 0, -1):
        s = i / n
        k = 1 - depth * s
        a_s = warp(body, k)
        l_s = warp(lit, k)
        p_s = warp(spec, k)
        base = SIDE_NEAR * (1 - s) ** 1.1 + SIDE_FAR * (1 - (1 - s) ** 1.1)
        col = base[None, None, :] + (SIDE_HI[None, None, :] - base[None, None, :]) * (l_s * (1 - .5 * s))[..., None] * .9
        col = col + np.array([1.0, .95, .8], np.float32) * (p_s * (1 - s))[..., None] * .6
        acc = over(acc, np.dstack([np.clip(col, 0, 1) * a_s[..., None], a_s]))
    return acc


def gold_ring(S_, seed=61):
    """金の 輪（青い 嵐 → 金の 字 の 間）：金の 輪の 切れはしを 立体の かたまりに（前の 面の 面取り＋まん中へ むかう 厚み）＋まん中の 白い 光と 光の 筋
       → premultiplied RGBA（金の 爆発は gold_blast で べつの 絵）"""
    H = W = S_
    cx = cy = S_ / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S_ / 2)
    ang = np.arctan2(yy - cy, xx - cx)
    rng = np.random.default_rng(seed)
    a = np.zeros((H, W), np.float32)
    for r0, w, nseg in ((.3, .06, 6), (.47, .085, 8), (.65, .075, 11), (.85, .1, 8)):
        ring = smoothstep(w * .5, w * .5 - .012, np.abs(rr - r0))
        segm = np.zeros_like(a)
        off = rng.uniform(0, 6.28)
        for k in range(nseg):
            a0 = off + k * 2 * np.pi / nseg
            ln = rng.uniform(.5, .78) * 2 * np.pi / nseg
            da = np.mod(ang - a0, 2 * np.pi)
            segm = np.maximum(segm, smoothstep(0, .025, da) * smoothstep(ln, ln - .025, da))
        a = np.maximum(a, ring * segm)
    em = S_ * .045
    sd = extrude_radial(a, cx, cy, .13)
    fr, body = front(a, em, (.0, .32, .0005), 'gold', 10)
    allm = np.maximum(body, sd[..., 3])
    ring_e = np.clip(grow(allm, max(1.0, .03 * em)) - allm, 0, 1)
    blocks = np.zeros((H, W, 4), np.float32)
    blocks[..., :3] = np.array(EDGE, np.float32) / 255 * ring_e[..., None]
    blocks[..., 3] = ring_e
    blocks = over(blocks, sd)
    blocks = over(blocks, fr)
    glow = radial(H, W, cx, cy, S_ * .5, 1.6)
    ry = rays(H, W, cx, cy, 40, seed + 2, .7, 1.2) * np.clip(1 - rr, 0, 1)
    la = np.clip(glow * 1.1 + ry * .6, 0, 1)
    lc = np.stack([np.ones_like(la), .92 + 0 * la, .7 + .3 * glow], -1)
    out = np.dstack([lc * la[..., None], la])
    return over(out, blocks)


def gold_blast(S_, seed=71):
    """金の 爆発（金の 輪と いっしょに）：まん中が 白 → 金 → だいだいの 炎の 舌が 外へ・金の 光の 筋・火の 粉 → premultiplied RGBA"""
    H = W = S_
    cx = cy = S_ / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S_ / 2)
    th = (np.arctan2(yy - cy, xx - cx) + np.pi) / (2 * np.pi)
    N = 512

    def wrap_x(t):                                          # よこに つながる ノイズ（まわりを 1周 しても つなぎめ なし）
        w = np.linspace(0, 1, N, endpoint=False, dtype=np.float32)[None, :]
        return t[:, N:] * (1 - w) + t[:, :N] * w
    tex = wrap_x(fbm(N, 2 * N, 6, seed, 6, .55))
    tex2 = wrap_x(fbm(N, 2 * N, 14, seed + 5, 4, .5))
    tex = (tex - tex.mean()) / (tex.std() + 1e-6) * .16 + .5
    tex2 = (tex2 - tex2.mean()) / (tex2.std() + 1e-6) * .14 + .5
    mx = (th * N * 2) % N                                   # まわりを 2回 まわる（つなぎめ なし）
    my = np.clip(rr * N * .9, 0, N - 1)
    n1 = cv2.remap(tex, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    n2 = cv2.remap(tex2, ((th * N * 5) % N).astype(np.float32), np.clip(rr * N * 1.6, 0, N - 1).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    f = 1.18 - rr * 1.25 + (n1 - .5) * 1.1 + (n2 - .5) * .35
    f = np.clip(f, 0, 1) ** 1.2
    core = radial(H, W, cx, cy, S_ * .2, 1.4)
    f = np.clip(f + core * .8, 0, 1)
    col = ramp(f, ((0, (200, 90, 10)), (.25, (250, 150, 24)), (.5, (255, 196, 50)), (.72, (255, 230, 120)), (.88, (255, 248, 210)), (1, (255, 255, 255))))
    al = smoothstep(.04, .35, f) * (.55 + .45 * smoothstep(.1, .5, f))
    ry = rays(H, W, cx, cy, 34, seed + 2, .5, 1.4) * np.clip(1 - rr * .9, 0, 1) * smoothstep(.05, .25, rr)
    col = np.clip(col + ry[..., None] * np.array([1.0, .85, .4], np.float32) * .7, 0, 1)
    al = np.clip(al + ry * .55, 0, 1)
    rng = np.random.default_rng(seed + 9)
    sp = np.zeros((H, W), np.float32)
    for _ in range(140):                                     # 火の 粉（外へ むかう 短い すじ）
        a_ = rng.uniform(0, 2 * np.pi)
        r0 = rng.uniform(.25, .95) * S_ / 2
        ln = rng.uniform(4, 16) * S_ / 600
        p0 = (cx + r0 * math.cos(a_), cy + r0 * math.sin(a_))
        p1 = (cx + (r0 + ln) * math.cos(a_), cy + (r0 + ln) * math.sin(a_))
        cv2.line(sp, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), float(rng.uniform(.6, 1.0)), max(1, int(S_ / 400)), cv2.LINE_AA, shift=2)
    sp = np.maximum(sp, cv2.GaussianBlur(sp, (0, 0), 1.5) * .8)
    col = col * (1 - sp[..., None]) + np.array([1.0, .95, .7], np.float32) * sp[..., None]
    al = np.clip(np.maximum(al, sp), 0, 1)
    al *= smoothstep(1.0, .8, rr)
    return np.dstack([col * al[..., None], al])


# ---------------------------------------------------------------- ③ 金の 粒・金の 鳥居
def nugget(R, seed):
    """金の 粒（ごつごつした 金の かたまり）1つ → premultiplied RGBA（2R＋あき の 四角）"""
    rng = np.random.default_rng(seed)
    S_ = int(R * 2.6)
    c = S_ / 2
    n = 14
    angs = np.sort(rng.uniform(0, 2 * np.pi, n))
    pts = [(c + math.cos(a) * R * rng.uniform(.62, 1.0), c + math.sin(a) * R * rng.uniform(.62, 1.0) * rng.uniform(.75, 1.0)) for a in angs]
    m = np.zeros((S_ * 4, S_ * 4), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(pts) * 4)], 255, cv2.LINE_AA)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), R * .25)
    m = cv2.resize(m, (S_, S_), interpolation=cv2.INTER_AREA)
    a = smoothstep(.42, .58, m)
    d = cv2.GaussianBlur(dist_in(a), (0, 0), R * .06)
    h = np.sqrt(np.clip(d / (R * .9), 0, 1)) * R * .7
    h += (fbm(S_, S_, 5, seed + 3, 4) - .5) * R * .5 * smoothstep(0, R * .2, d)
    nrm = normals_of(h, 1.0)
    ndl = np.clip(nrm @ L_DIR, 0, 1)
    hv = L_DIR + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    ndh = np.clip(nrm @ hv, 0, 1)
    ys = (np.arange(S_, dtype=np.float32)[:, None] / S_) * np.ones((1, S_), np.float32)
    t = .15 + .7 * ys + .6 * nrm[..., 1] - .2 * nrm[..., 0]
    col = ramp(t, ((0, (255, 250, 220)), (.3, (255, 214, 90)), (.6, (222, 148, 28)), (1, (116, 60, 6))))
    col *= (.5 + .7 * ndl)[..., None]
    col += np.array([1.0, .96, .82], np.float32) * (ndh ** 50 * 1.3 + ndh ** 10 * .2)[..., None]
    cav = np.clip((cv2.GaussianBlur(h, (0, 0), R * .15) - h) / (R * .1), 0, 1)        # くぼみは 暗く
    col *= (1 - .35 * cv2.GaussianBlur(cav, (0, 0), 1.0))[..., None]
    col = np.clip(col, 0, 1)
    edge = np.clip(grow(a, max(1.0, R * .04)) - a, 0, 1)
    out = np.zeros((S_, S_, 4), np.float32)
    out[..., :3] = col * a[..., None] + np.array(EDGE, np.float32) / 255 * edge[..., None]
    out[..., 3] = np.clip(a + edge, 0, 1)
    return out


NUG_CELL, NUG_DPR, NUG_N = 64, 2.0, 8       # 金の 粒の 絵（1つの 箱 64px・8つ：4×2）


def nug_sheet():
    cell = int(NUG_CELL * NUG_DPR)
    sheet = np.zeros((cell * 2, cell * 4, 4), np.float32)
    for k in range(NUG_N):
        g = nugget(cell / 2.6, 70 + k * 7)
        g = cv2.resize(g, (cell, cell), interpolation=cv2.INTER_AREA)
        r, c = divmod(k, 4)
        sheet[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell] = g
    return sheet


FRAME_W, FRAME_H, FRAME_DPR = 390.0, 780.0, 2.0     # 金の 鳥居（画面の px）


def torii_d():
    """鳥居の 形（画面の px）：笠木（上の 反った 木）・島木・額・貫・柱 2本・台 → (path の 文字列, 額の 中の 四角)"""
    def band(x0, x1, top, th, n=40):
        xs = np.linspace(x0, x1, n)
        up = [(x, top(x)) for x in xs]
        dn = [(x, top(x) + th(x)) for x in xs[::-1]]
        return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in up + dn) + 'Z'
    cx = FRAME_W / 2

    def kasa_top(x):
        u = (x - cx) / (FRAME_W / 2)
        return 112 + 10 * (1 - u * u) - 22 * max(0, abs(u) - .55) ** 2 / .2

    def kasa_th(x):
        u = abs(x - cx) / (FRAME_W / 2)
        return 26 - 8 * max(0, u - .7) / .3
    d = band(-2, FRAME_W + 2, kasa_top, kasa_th)                                  # 笠木
    d += band(16, FRAME_W - 16, lambda x: kasa_top(x) + kasa_th(x) - 1, lambda x: 14)   # 島木
    d += band(4, FRAME_W - 4, lambda x: 236, lambda x: 18)                        # 貫
    for xl, xr in ((26, 54), (FRAME_W - 54, FRAME_W - 26)):                      # 柱（下が 少し 太い・上が 少し 内へ）
        lean = 4 if xl < cx else -4
        d += f'M{xl + lean:.1f} 150 L{xr + lean:.1f} 150 L{xr + 4 * (1 if xl > cx else 1):.1f} 742 L{xl - 4:.1f} 742Z'
        d += f'M{xl - 12:.1f} 736 L{xr + 12:.1f} 736 L{xr + 16:.1f} 762 L{xl - 16:.1f} 762Z'   # 台
    d += f'M{cx - 34:.1f} 150 L{cx + 34:.1f} 150 L{cx + 34:.1f} 236 L{cx - 34:.1f} 236Z'      # 額（金の わく）
    return d, (cx - 25, 160, cx + 25, 226)


def torii():
    """金の 鳥居（立体の 金・額の 中は こい 赤に 金の「天眼」）→ premultiplied RGBA"""
    k = FRAME_DPR
    W, H = int(FRAME_W * k), int(FRAME_H * k)
    d, (px0, py0, px1, py1) = torii_d()
    s = SS
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * s}" height="{H * s}" viewBox="0 0 {FRAME_W} {FRAME_H}">'
           f'<path d="{d}" fill="#fff"/></svg>')
    a = cv2.resize(svg_rgba(svg, W * s, H * s)[..., 3], (W, H), interpolation=cv2.INTER_AREA)
    em = 80 * k
    img = gold3d(a, em, ext=(.04, .07), rim=(.0, .12, .06), glints=6)
    # 額の 中：こい 赤 → 金の 天眼（たて）
    pm = np.zeros((H, W), np.float32)
    cv2.rectangle(pm, (int(px0 * k), int(py0 * k)), (int(px1 * k), int(py1 * k)), 1.0, -1)
    pm = cv2.GaussianBlur(pm, (0, 0), .6)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    panel = ramp((ys * H / k - py0) / (py1 - py0), ((0, (120, 14, 10)), (1, (60, 6, 4))))
    img[..., :3] = img[..., :3] * (1 - pm[..., None]) + panel * pm[..., None]
    its, boxes = [], []
    for j, c in enumerate('天眼'):
        it, bx, w = run([(c, 1.0)], 0.0, 880.0 + j * 1000)
        its += it
        boxes.append(bx)
    box = union_box(*boxes)
    kk = (py1 - py0 - 12) / (box[3] - box[1]) * k
    tm = mask(its, box, kk, 0)
    th, tw = tm.shape
    tx, ty = int(((px0 + px1) / 2) * k - tw / 2), int(((py0 + py1) / 2) * k - th / 2)
    full = np.zeros((H, W), np.float32)
    full[ty:ty + th, tx:tx + tw] = tm
    tg, _ = front(full, 30 * k, (.0, .05, .04), 'gold', 0)
    return over(img, tg)


# ---------------------------------------------------------------- 文（4行）・寄り
KANA = .78        # かなの 大きさ（漢字＝1）
RUBY = .4         # ふりがなの 大きさ


def chars_of(text):
    """漢字は 1・かなは KANA"""
    return [(c, 1.0 if '\u4e00' <= c <= '\u9fff' else KANA) for c in text]


def line_layout(parts, base, ruby=None, cx=0.0, track=-40.0):
    """1行（まん中 そろえ）：parts＝文字列・ruby＝(ふりがな, かかる 字の はじめ, おわり（字の 番号）)
       → (字の items, ふりがなの items, 箱)"""
    cs = chars_of(parts)
    items, box, w = run(cs, 0.0, base, track)
    dx = cx - w / 2
    items = shift_items(items, dx, 0)
    box = (box[0] + dx, box[1], box[2] + dx, box[3])
    ritems = []
    if ruby:
        rt, i0, i1 = ruby
        xa = items[i0][1]
        d1, b1, adv1 = gpath(parts[i1 - 1])
        xb = items[i1 - 1][1] + adv1 * cs[i1 - 1][1]
        rcs = [(c, RUBY) for c in rt]
        ri, rb, rw = run(rcs, 0.0, box[1] - 50, -10.0)
        ddx = (xa + xb) / 2 - rw / 2
        ritems = shift_items(ri, ddx, 0)
        box = union_box(box, (rb[0] + ddx, rb[1], rb[2] + ddx, rb[3]))
    return items, ritems, box


TEXT = (('万馬券は', ('きせき', 0, 3)), ('偶然にあらず', None), ('天眼が導く', ('テンゲル', 0, 2)), ('必然なり', None))
TXT_EM = 70.0          # 4行の 文の 1文字（漢字）の 画面の px
TXT_DPR = 3.0


def layout_text():
    """4行の 文：万馬券（きせき）は／偶然にあらず／天眼（テンゲル）が導く／必然なり → ([(字の items, ふりがなの items) 行ごと], 箱)"""
    base = 0.0
    lines, boxes = [], []
    for k, (t, rb) in enumerate(TEXT):
        if rb:
            base += 380          # ふりがなの ぶん
        if k == 2:
            base += 170          # 文の 区切り
        base += 800
        it, ri, bx = line_layout(t, base, rb)
        lines.append((it, ri))
        boxes.append(bx)
        base += 130
    return lines, union_box(*boxes)


def rows_of(a):
    yy = np.where(a.max(1) > .5)[0]
    return (float(yy.min()), float(yy.max())) if len(yy) else None


def text_img(lines, box, em_px, ext, rim, pad, ruby_ext=None, glints=5, warp=None):
    """行ごとに（上の 行から）ふりがな（小）→ 字（大）を 金の 立体に して 重ねる（金の 映りこみは 行ごとに）→ premultiplied RGBA。
       上の 行の 厚みは 下の 行の 字の うしろに なる。warp：ななめから 見た 形（3x3 の 行列を 作る 関数）"""
    k = em_px / 1000
    img = None
    for items, ritems in lines:
        if ritems:
            ar = mask(ritems, box, k, pad)
            rem = em_px * RUBY
            rimg = gold3d(ar, rem, ext=ruby_ext or (ext[0] * 1.5, ext[1] * 1.5), rim=(rim[0] * 1.6, rim[1] * 1.3, rim[2] * 1.2), glints=1, env_box=rows_of(ar))
            img = rimg if img is None else over(img, rimg)
        a = mask(items, box, k, pad)
        g = gold3d(a, em_px, ext=ext, rim=rim, glints=max(1, glints // len(lines) + 1), env_box=rows_of(a))
        img = g if img is None else over(img, g)
    if warp is not None:
        H, W = img.shape[:2]
        M, size = warp(W, H)
        img = cv2.warpPerspective(img, M, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return img


def persp(src, dst, size):
    def f(W, H):
        s = np.float32([(x * W, y * H) for x, y in src])
        d = np.float32([(x * W, y * H) for x, y in dst])
        return cv2.getPerspectiveTransform(s, d), (int(size[0] * W), int(size[1] * H))
    return f


# ---------------------------------------------------------------- 寄りの 字（② 金の 字・③ 神様的中）
CU = dict(gd_cu1=dict(text='万馬券', ruby=('きせき', 0, 3), em=160.0, dpr=2.0,
                      warp=((0, 0), (1, 0), (1, 1), (0, 1)), to=((0, .26), (.84, 0), (.84, .56), (0, 1.0))),
          gd_cu2=dict(text='天眼', ruby=('テンゲル', 0, 2), em=215.0, dpr=2.0,
                      warp=((0, 0), (1, 0), (1, 1), (0, 1)), to=((0, .02), (.86, .24), (.86, .74), (0, .98))))
CHAR_EM, CHAR_DPR = 440.0, 1.6           # 神・様・的・中 の 寄り
CHAR_WARP = (((0, .04), (.96, 0), (.92, 1.0), (0, .94)), ((0, 0), (1, .05), (1, .97), (.02, 1)),
             ((.04, 0), (1, .05), (1, .95), (0, 1)), ((0, .03), (1, 0), (.97, 1), (0, .97)))
LOGO_EM, LOGO_DPR = 150.0, 3.0           # 神様／的中
STRIPE_RIM = (.046, .028, .018)


def char_img(c, em_px, pad, warp=None, glints=3):
    items, box, w = run([(c, 1.0)])
    k = em_px / 1000
    a = mask(items, box, k, pad)
    yy = np.where(a.max(1) > .5)[0]
    img = gold3d(a, em_px, ext=(.05, .085), rim=STRIPE_RIM, style='stripe', glints=glints, stripe_box=(yy.min(), yy.max()))
    if warp is not None:
        H, W = img.shape[:2]
        M, size = persp(((0, 0), (1, 0), (1, 1), (0, 1)), warp, (1, 1))(W, H)
        img = cv2.warpPerspective(img, M, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return img


def logo_img(em_px):
    """神様／的中（2行）：字ごとに しま（字の 高さで）"""
    pad = int(.25 * em_px)
    rows = ('神様', '的中')
    tiles = []
    for r in rows:
        its, box, w = run([(c, 1.0) for c in r], track=-30.0)
        tiles.append((its, box))
    gap = 60.0
    items = []
    for k, (its, box) in enumerate(tiles):
        items += shift_items(its, 0, k * (1000 + gap))
    boxes = [(b[0], b[1] + k * (1000 + gap), b[2], b[3] + k * (1000 + gap)) for k, (its, b) in enumerate(tiles)]
    box = union_box(*boxes)
    k_ = em_px / 1000
    out = None
    for it in items:                       # 字ごとに 描いて 重ねる（しまを 字の 高さで そろえる）
        a = mask([it], box, k_, pad)
        yy = np.where(a.max(1) > .5)[0]
        g = gold3d(a, em_px, ext=(.05, .085), rim=STRIPE_RIM, style='stripe', glints=2, stripe_box=(yy.min(), yy.max()))
        out = g if out is None else over(out, g)
    return out


def build_text(out, names, lay):
    def want(n):
        return not names or n in names
    if want('gd_txt'):
        lines, box = layout_text()
        em = TXT_EM * TXT_DPR
        img = text_img(lines, box, em, (.06, .1), (.035, .022, .016), int(.4 * em), glints=6)
        img, o = crop(img)
        save(img, os.path.join(out, 'gd_txt.webp'), 90)
        lay['gd_txt'] = dict(w=round(img.shape[1] / TXT_DPR, 1), h=round(img.shape[0] / TXT_DPR, 1))
    for name, c in CU.items():
        if not want(name):
            continue
        it, ri, box = line_layout(c['text'], 0.0, c['ruby'])
        em = c['em'] * c['dpr']
        img = text_img([(it, ri)], box, em, (.06, .1), (.032, .02, .015), int(.3 * em), glints=4,
                       warp=persp(c['warp'], c['to'], (max(x for x, y in c['to']), 1.0)))
        img, o = crop(img)
        save(img, os.path.join(out, name + '.webp'), 86)
        lay[name] = dict(w=round(img.shape[1] / c['dpr'], 1), h=round(img.shape[0] / c['dpr'], 1))
    for k, ch in enumerate('神様的中'):
        name = f'gd_c{k + 1}'
        if not want(name):
            continue
        em = CHAR_EM * CHAR_DPR
        img = char_img(ch, em, int(.22 * em), CHAR_WARP[k])
        img, o = crop(img)
        save(img, os.path.join(out, name + '.webp'), 84)
        lay[name] = dict(w=round(img.shape[1] / CHAR_DPR, 1), h=round(img.shape[0] / CHAR_DPR, 1))
    if want('gd_logo'):
        img = logo_img(LOGO_EM * LOGO_DPR)
        img, o = crop(img)
        save(img, os.path.join(out, 'gd_logo.webp'), 90)
        lay['gd_logo'] = dict(w=round(img.shape[1] / LOGO_DPR, 1), h=round(img.shape[0] / LOGO_DPR, 1))


# ---------------------------------------------------------------- まとめて 作る
def build_storm(out, want, lay):
    """① 青い 嵐の 絵（kami_storm.py）"""
    if want('gd_vein1') or want('gd_vein2'):
        for j, sd in ((1, 5), (2, 6)):
            if want(f'gd_vein{j}'):
                save(KS.veins(sd), os.path.join(out, f'gd_vein{j}.webp'), 82)
    for j in (1, 2):
        lay[f'gd_vein{j}'] = dict(w=SCR_W, h=SCR_H)
    if want('gd_dome'):
        save(KS.dome_glass(), os.path.join(out, 'gd_dome.webp'), 86)
    x0, y0, bw, bh = KS.dome_box()
    lay['gd_dome'] = dict(x=round(x0, 2), y=round(y0, 2), w=round(bw, 2), h=round(bh, 2))
    if want('gd_fall'):
        save(KS.fall_tile2(), os.path.join(out, 'gd_fall.webp'), 82)
    lay['gd_fall'] = dict(w=KS.FALL2[0], h=KS.FALL2[1])
    if want('gd_fmask'):
        m = KS.fall_mask()
        save(np.dstack([np.repeat(m[..., None], 3, -1), m]), os.path.join(out, 'gd_fmask.webp'), 80)
    fx, fy, fw, fh = KS.FALL_BOX
    lay['gd_fmask'] = dict(x=fx, y=fy, w=fw, h=fh)
    if want('gd_rib'):
        sheet, pos = KS.ribbon_sheet()
        save(sheet, os.path.join(out, 'gd_rib.webp'), 84)
        lay['gd_rib'] = dict(w=round(sheet.shape[1] / KS.RIB_DPR, 2), h=round(sheet.shape[0] / KS.RIB_DPR, 2),
                             pos=[[sx, round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)] for sx, b in pos])
    if want('gd_surge'):
        save(KS.surge(), os.path.join(out, 'gd_surge.webp'), 80)
    lay['gd_surge'] = dict(w=SCR_W, h=SCR_H)
    if want('gd_rock'):
        save(KS.rock_sheet(), os.path.join(out, 'gd_rock.webp'), 86)
    lay['gd_rock'] = dict(w=KS.ROCK_CELL * KS.ROCK_N, h=KS.ROCK_CELL, cell=KS.ROCK_CELL, n=KS.ROCK_N)


BG = dict(gd_burst=(burst, 1.0, 'rgb'), gd_fire=(fire, 1.0, 'rgb'), gd_storm=(KS.storm_bg, 1.5, 'rgb'), gd_sky=(sky, 1.5, 'rgb'))
SCR_W, SCR_H = 390.0, 844.0
RING = (600.0, 1.4)              # 金の 輪（立体の かたまり）
BLAST = (600.0, 1.0)             # 金の 爆発


def build(out, names=None):
    os.makedirs(out, exist_ok=True)
    lpath = os.path.join(K, 'kami_layers.json')
    lay = json.load(open(lpath, encoding='utf-8')) if names and os.path.exists(lpath) else {}

    def want(n):
        return not names or n in names
    for name, (fn, dpr, kind) in BG.items():
        if want(name):
            save_rgb(fn(int(SCR_W * dpr), int(SCR_H * dpr)), os.path.join(out, name + '.webp'), 80 if name != 'gd_fire' else 72)
        lay[name] = dict(w=SCR_W, h=SCR_H)
    build_storm(out, want, lay)
    if want('gd_ring'):
        save(gold_ring(int(RING[0] * RING[1])), os.path.join(out, 'gd_ring.webp'), 84)
    lay['gd_ring'] = dict(w=RING[0], h=RING[0])
    if want('gd_blast'):
        save(gold_blast(int(BLAST[0] * BLAST[1])), os.path.join(out, 'gd_blast.webp'), 80)
    lay['gd_blast'] = dict(w=BLAST[0], h=BLAST[0])
    if want('gd_nug'):
        save(nug_sheet(), os.path.join(out, 'gd_nug.webp'), 86)
    lay['gd_nug'] = dict(w=NUG_CELL * 4, h=NUG_CELL * 2, cell=NUG_CELL, n=NUG_N)
    if want('gd_frame'):
        save(torii(), os.path.join(out, 'gd_frame.webp'), 86)
    lay['gd_frame'] = dict(w=FRAME_W, h=FRAME_H)
    build_text(out, names, lay)
    with open(lpath, 'w', encoding='utf-8') as f:
        json.dump(lay, f, ensure_ascii=False, indent=1)
    return lay


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2:] or None))
