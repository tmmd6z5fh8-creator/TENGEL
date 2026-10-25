"""紫電（第4.68版）：まさちゃんが 送ってくれた GIF（21コマ・4.28秒：送ってくれた 動画の 1.55秒〜5.00秒）の 1コマずつに 合わせた 絵（WebP）。
   まさちゃん「え？ファイルのこの、画像からこの画像まで確認して！は確認してないってこと？ もう一度送る！」
   GIF の 絵・人物・機械・字は 使わない・なぞらない。もらうのは コマの 順・長さ・色・形の 種類だけ。
   人物の 代わりは テンゲルの 黒い 馬（r3d の 3Dの 馬）、機械の 代わりは 銀の 金属の 黒い 馬（赤い 目）、白い 線の 文字は「的中」。
   色は GIF の コマの とおり（まさちゃんの「青」は GIF 16 の 水色）。
   出す 絵（shiden_art.py の build から 呼ぶ。大きさは shiden_layers.json・id は shiden_blobs.json。どれも 画面と 同じ 390×844 の 2倍）：
     sd_c0      … GIF 0（0.20秒）：白黒の 煙・白い 線の「的中」と うず・黒い 馬（白い ふち）
     sd_rbs     … GIF 0：虹色の 光の 筋（緑・紫・白・桃：ななめ・すき通し）
     sd_c1      … GIF 1（0.24秒）：赤い 炎の 馬が 横に ずれる バグの 1コマ
     sd_eye     … GIF 3〜4（0.08＋0.12秒）：光る 目の ドアップ（白い 光に 焼けた 馬の 顔・うすい 紫と 白・桃色）
     sd_c5      … GIF 5（0.08秒）：赤黒い 筋の 画面を 白い ギザギザの 裂け目が 横に 裂く・右上に 虹色の ずれ
     sd_c6      … GIF 6（0.12秒）：緑と 黒の 筋の 画面を 黒い 裂け目が 横に 裂く・裂け目の 中に 炎
     sd_w_bg    … GIF 7〜15（2.12秒）：割れた 鏡の かけらの 世界（上に 黒い 宇宙の 窓・右に 白い 光・まん中に 赤い 角と ピンクの 光・下に 銀の 金属の 馬）
     sd_w_near  … 手前の かけら（ふちの 大きな ぼけた かけら・炎の 上を とぶ 小さな かけら）
     sd_w_fire1・sd_w_fire2 … 上と 下から まん中の 光へ 集まって 右上へ 抜ける 大きな 炎（すき通し・2まいを ゆっくり 入れかえる）
     sd_w_prism … 左の 虹色の プリズム（すき通し・炎の 下）
     sd_c16     … GIF 16（0.12秒）：白い 地に 水色の かけら・まん中に 横に 広い 黒い 穴と 炎
     sd_c17     … GIF 17（0.08秒）：まん中が 黒い 穴・まわりは 銀の かけら・白い かたまり
     sd_c18     … GIF 18（0.08秒）：黒の 中を かけらが 外へ（金の 小さな 光は CSS）
     sd_c19     … GIF 19〜20（0.84秒）：暗い 緑に 金の 輪（横の 光は sd_flare と CSS）
     sd_pillar  … GIF 16〜20：左右の 炎の 柱（すき通し・右は 左右 反転で 使う）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
from kami_art import mask, run, ramp, fbm, noise, radial, smoothstep, grow, dist_in, over, save, save_rgb
import shiden_art as SA

W2, H2 = 780, 1688                       # 画面（390×844）の 2倍
CXs, CYs = 390.0, 860.0                  # 鏡の 世界の まん中（穴と ピンクの 光：2倍の 座標）
MG = 220                                 # かけらを 描く ときの 外の あき


def hexc(h):
    return SA.hexc(h)


def load(name, out):
    """出力フォルダの 絵 → (rgb 0〜1, a 0〜1)"""
    im = cv2.imread(os.path.join(out, name + '.webp'), cv2.IMREAD_UNCHANGED)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    if im.shape[2] == 3:
        rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        return rgb, np.ones(rgb.shape[:2], np.float32)
    rgba = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
    return rgba[..., :3], rgba[..., 3]


def place(dst, rgb, a, x, y, w, h, opacity=1.0, add=False):
    """dst（2倍の 画面）に 絵を 置く（left, top, 幅, 高さ は 2倍の px）"""
    w, h = int(round(w)), int(round(h))
    r2 = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA if w < rgb.shape[1] else cv2.INTER_CUBIC)
    a2 = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA if w < a.shape[1] else cv2.INTER_CUBIC)
    H, W = dst.shape[:2]
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    dx1, dy1 = min(W, x + w), min(H, y + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return dst
    sub = r2[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    sa = np.clip(a2[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0] * opacity, 0, 1)[..., None]
    if add:
        dst[dy0:dy1, dx0:dx1] = dst[dy0:dy1, dx0:dx1] + sub * sa
    else:
        dst[dy0:dy1, dx0:dx1] = dst[dy0:dy1, dx0:dx1] * (1 - sa) + sub * sa
    return dst


RAINBOW = ((0, (255, 50, 80)), (.16, (255, 160, 40)), (.33, (255, 238, 70)), (.5, (70, 240, 120)), (.66, (60, 170, 255)), (.83, (190, 80, 255)), (1, (255, 50, 80)))


# ---------------------------------------------------------------- 割れた 鏡の かけら
CHROME = ((0, (255, 255, 255)), (.16, (232, 236, 246)), (.36, (158, 164, 180)), (.54, (40, 42, 54)), (.72, (128, 134, 150)), (.9, (236, 240, 250)), (1, (255, 255, 255)))
DARK = ((0, (210, 214, 228)), (.25, (80, 82, 96)), (.55, (10, 10, 16)), (.8, (40, 42, 52)), (1, (170, 176, 192)))


def shard_pts(r, cx, cy, size, elong=(1.0, 2.6)):
    """とがった かけらの 形（3〜5角・細長い）"""
    n = r.choice((3, 3, 4, 4, 4, 5))
    rot = r.uniform(0, 2 * math.pi)
    el = r.uniform(*elong)
    angs = sorted(r.uniform(0, 2 * math.pi) for _ in range(n))
    pts = []
    for a in angs:
        rr = size * r.uniform(.45, 1.0)
        x, y = rr * math.cos(a) * el, rr * math.sin(a)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def draw_shard(img, al, pts, r, style='chrome', tint=None, edge=1.0, edge_col=(1, 1, 1), fill=None, outline=None, chroma=0.0):
    """かけら 1つ（画面の 外の あき MG を 足した img・al に 描く）：金属の ような 明るさの 流れ・光る ふち（1〜2辺）。
       tint＝(色, 強さ) で 色を つける・fill＝1色で ぬる・outline＝(色, 太さ) で ふち どり"""
    P = np.array(pts, np.float32) + MG
    H, W = al.shape
    x0, y0 = (np.floor(P.min(0)) - 4).astype(int)
    x1, y1 = (np.ceil(P.max(0)) + 4).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    h, w = y1 - y0, x1 - x0
    Q = P - (x0, y0)
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [np.round(Q * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    if fill is not None:
        col = np.ones((h, w, 3), np.float32) * np.array(fill, np.float32)
    else:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        ang = r.uniform(0, 2 * math.pi)
        proj = xx * math.cos(ang) + yy * math.sin(ang)
        t = (proj - proj.min()) / (float(np.ptp(proj)) + 1e-3)
        t = np.clip(t * r.uniform(.7, 1.5) + r.uniform(-.35, .2), 0, 1)
        col = ramp(t, CHROME if style == 'chrome' else DARK)
        if tint is not None:
            c, k = tint
            lum = col.mean(-1, keepdims=True)
            col = col * (1 - k) + np.clip(lum * 1.25, 0, 1) * np.array(c, np.float32) * k
    e = np.zeros((h, w), np.float32)
    n = len(Q)
    for i in range(n):
        if r.random() < .55:
            p, q = Q[i], Q[(i + 1) % n]
            cv2.line(e, (int(p[0] * 16), int(p[1] * 16)), (int(q[0] * 16), int(q[1] * 16)), 1.0, max(1, int(r.uniform(1, 3))), cv2.LINE_AA, shift=4)
    e = np.clip(e * m * 1.3, 0, 1) * edge
    col = col * (1 - e[..., None]) + np.array(edge_col, np.float32) * e[..., None]
    if chroma:
        for col_, dx, dy in (((.2, .95, 1.0), 2, 0), ((1.0, .3, .85), -2, 1)):         # 色の ずれた ふち（水色・桃色）
            o = np.zeros((h, w), np.float32)
            cv2.polylines(o, [np.round((Q + (dx, dy)) * 16).astype(np.int32)], True, 1.0, 1, cv2.LINE_AA, shift=4)
            o = o * chroma
            col = col * (1 - o[..., None]) + np.array(col_, np.float32) * o[..., None]
            m = np.maximum(m, o)
    if outline is not None:
        oc, ow = outline
        o = np.zeros((h, w), np.float32)
        cv2.polylines(o, [np.round(Q * 16).astype(np.int32)], True, 1.0, ow, cv2.LINE_AA, shift=4)
        col = col * (1 - o[..., None]) + np.array(oc, np.float32) * o[..., None]
        m = np.maximum(m, o)
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - m[..., None]) + col * m[..., None]
    al[y0:y1, x0:x1] = np.maximum(al[y0:y1, x0:x1], m)


def shard_layer(seed, specs, w=W2, h=H2):
    """specs：[(数, (x0, y0, x1, y1), (大きさ min, max), 色の 決め方 fn(r, x, y) → dict)] → (img, al)（2倍の 画面）"""
    r = random.Random(seed)
    img = np.zeros((h + 2 * MG, w + 2 * MG, 3), np.float32)
    al = np.zeros((h + 2 * MG, w + 2 * MG), np.float32)
    items = []
    for n, box, size, how in specs:
        for _ in range(n):
            x, y = r.uniform(box[0], box[2]), r.uniform(box[1], box[3])
            s = r.uniform(*size) if r.random() < .8 else r.uniform(size[1], size[1] * 1.7)
            items.append((s, x, y, how))
    items.sort(key=lambda it: -it[0] * .3 + r.random() * 40)       # 大きい ものを 先に（小さい ものが 手前に 来やすい）
    for s, x, y, how in items:
        kw = how(r, x, y) if how else {}
        draw_shard(img, al, shard_pts(r, x, y, s), r, **kw)
    return img[MG:-MG, MG:-MG], al[MG:-MG, MG:-MG]


# ---------------------------------------------------------------- 線（雷・裂け目）
def disp(r, a, b, rough):
    pts = [a, b]
    for rr in rough:
        nw = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            off = r.gauss(0, rr * L / 2)
            nw += [((ax + bx) / 2 + nx * off, (ay + by) / 2 + ny * off), (bx, by)]
        pts = nw
    return pts


def jag_edge(r, x0, x1, y0, y1, n, amp, spike=0.25, spike_amp=3.0):
    """ギザギザの 線（左 x0,y0 → 右 x1,y1）：細かい ぶれ＋ときどき 大きな とげ"""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t + r.uniform(-.4, .4) * (x1 - x0) / n
        y = y0 + (y1 - y0) * t + r.gauss(0, amp)
        if r.random() < spike:
            y += r.choice((-1, 1)) * amp * r.uniform(1.2, spike_amp)
        pts.append((x, y))
    return pts


def tear_mask(r, cy, thick, slope, n=60, amp=10, spike=.3, spike_amp=4.0, w=W2, h=H2):
    """画面を 横に 裂く ギザギザの 帯（cy＝まん中・thick＝太さ・slope＝かたむき）→ 0〜1"""
    top = jag_edge(r, -40, w + 40, cy - thick / 2 - slope * w / 2, cy - thick / 2 + slope * w / 2, n, amp, spike, spike_amp)
    bot = jag_edge(r, -40, w + 40, cy + thick / 2 - slope * w / 2, cy + thick / 2 + slope * w / 2, n, amp, spike, spike_amp)
    poly = np.array(top + bot[::-1], np.float32)
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [np.round(poly * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    return m


def veins(seed, w=W2, h=H2):
    """もり上がった 太い 筋（前の 画面を 浮きぼりに した ような うず）→ (光る ふち 0〜1, 面の 明るさ 0〜1, 暗い ところ 0〜1)"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = fbm(h, w, 4, seed, 5)
    q1, q2 = fbm(h, w, 3, seed + 3, 3), fbm(h, w, 3, seed + 7, 3)
    f = cv2.remap(f, (xx + 260 * (q1 - .5)).astype(np.float32), (yy + 260 * (q2 - .5)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    band = (f * 7.0) % 1.0                                           # 等高線の 帯（うずの 形）
    ridge = np.exp(-((band - .5) / .09) ** 2)
    hgt = cv2.GaussianBlur(ridge, (0, 0), 6)
    gx, gy = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=5), cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=5)
    lit = np.clip(.5 + (-gx * .6 - gy * .8) * 1.6, 0, 1)            # 左上からの 光（浮きぼり）
    face = smoothstep(.25, .75, fbm(h, w, 3, seed + 11, 4))
    dark = smoothstep(.6, .75, fbm(h, w, 3, seed + 21, 4))
    return np.clip(ridge, 0, 1), lit * (.45 + .55 * face), dark


def streaks(r, img, cx, cy, ang, length, width, n, cols, thick=(1, 3)):
    """炎の 筋の たば（cx, cy から ang の 向きへ）を img に 足す"""
    for _ in range(n):
        off = r.gauss(0, width / 2.5)
        L = length * r.uniform(.3, 1.0)
        s = r.uniform(0, length - L)
        ca, sa = math.cos(ang), math.sin(ang)
        x0 = cx + ca * s - sa * off
        y0 = cy + sa * s + ca * off
        bend = r.uniform(-.06, .06)
        pts = []
        for k in range(6):
            t = k / 5
            a2 = ang + bend * t
            pts.append((x0 + math.cos(a2) * L * t, y0 + math.sin(a2) * L * t))
        c = np.array(cols[min(len(cols) - 1, int(abs(off) / (width / 2.5) * len(cols) / 1.6))], np.float32) * r.uniform(.6, 1.0)
        cv2.polylines(img, [np.round(np.array(pts) * 16).astype(np.int32)], False, tuple(float(v) for v in c), max(1, int(r.uniform(*thick))), cv2.LINE_AA, shift=4)


FIRE_COLS = ((1.0, .97, .82), (1.0, .82, .25), (1.0, .55, .1), (1.0, .32, .06), (.86, .14, .08))


def glow_of(img, sigs=((4, .9), (14, .55), (36, .3))):
    g = np.zeros_like(img)
    for s, k in sigs:
        g += cv2.GaussianBlur(img, (0, 0), s) * k
    return g


# ---------------------------------------------------------------- GIF 0：白黒の 煙・白い 線の「的中」・黒い 馬
def glyph_outline(text, em, width):
    """字の ふちだけ（白い 線）→ 0〜1"""
    items, box, _ = run([(c, 1.0) for c in text], track=-60)
    k = em / 1000
    a = mask(items, box, k, int(em * .3))
    d_in = dist_in(a)
    d_out = cv2.distanceTransform((a < .5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    line = np.clip(1 - np.abs(np.where(a > .5, -d_in, d_out)) / width, 0, 1)
    return line


def paste_rot(dst, src, cx, cy, ang, scale=1.0, k=1.0):
    """src（0〜1 の 1ch）を まわして dst に 足す（明るい ほうを とる）"""
    h, w = src.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, scale)
    M[0, 2] += cx - w / 2
    M[1, 2] += cy - h / 2
    warped = cv2.warpAffine(src, M, (dst.shape[1], dst.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
    np.maximum(dst, warped * k, out=dst)


def horse_layer(out):
    """① の 馬（sd_horse）：(rgb, a)・置き場所（2倍：x, y, w, h）"""
    import shiden
    rgb, a = load('sd_horse', out)
    x0, y0, w = shiden.HORSE_A
    h = w * SA.LAY['sd_horse']['h'] / SA.LAY['sd_horse']['w']
    return rgb, a, (x0 * 2, y0 * 2, w * 2, h * 2)


def cut_gray(out, seed=101):
    """GIF 0：白黒の 煙（明るい 灰色・白い 線の うず）・白い 線の「的中」・黒い 馬（白い ふち・紫の 光）"""
    W, H = W2, H2
    smoke = fbm(H, W, 4, seed, 5)
    img = ramp(smoke, ((0, (50, 50, 56)), (.3, (118, 118, 124)), (.55, (178, 178, 184)), (.8, (222, 222, 226)), (1, (250, 250, 252))))
    img = img * (.72 + .35 * radial(H, W, W * .62, H * .42, W * 1.2, 1.2))[..., None]
    # 白い 線の うず（煙の 等高線）
    f2 = fbm(H, W, 6, seed + 5, 4)
    sw = np.exp(-((f2 - .5) / .011) ** 2) + np.exp(-((f2 - .36) / .009) ** 2) * .7 + np.exp(-((f2 - .64) / .009) ** 2) * .6
    sw = cv2.GaussianBlur(sw, (0, 0), 1.6)
    img = img + (sw * .8)[..., None] + (cv2.GaussianBlur(sw, (0, 0), 9) * .55)[..., None]
    # 白い 線の「的中」（大きく・まわして）
    gl = np.zeros((H, W), np.float32)
    for (gx, gy, ang, em) in ((170, 300, -14, 380), (630, 600, 12, 420), (190, 1380, 8, 360), (640, 1430, -10, 320)):
        paste_rot(gl, glyph_outline('的中', em, 12), gx, gy, ang)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q1, q2 = fbm(H, W, 4, seed + 9, 3), fbm(H, W, 4, seed + 13, 3)
    gl = cv2.remap(gl, (xx + 70 * (q1 - .5)).astype(np.float32), (yy + 70 * (q2 - .5)).astype(np.float32), cv2.INTER_LINEAR, borderValue=0)   # 煙の ように ゆがめる
    gl = cv2.GaussianBlur(gl, (0, 0), 1.4)
    img = img + (gl * .9)[..., None] + (cv2.GaussianBlur(gl, (0, 0), 10) * .6)[..., None]
    # 黒い 馬（白い ふち・紫の 光）
    hrgb, ha, (x, y, w, h) = horse_layer(out)
    dk = np.dstack([np.full(ha.shape, .07, np.float32), np.full(ha.shape, .06, np.float32), np.full(ha.shape, .09, np.float32)])
    d = dist_in((ha > .5).astype(np.float32))
    rim = np.exp(-d / 2.5) * (ha > .5)
    dk = dk * (1 - rim[..., None]) + rim[..., None] * np.array([1, 1, 1], np.float32)
    purple = np.exp(-d / 14.0) * (ha > .5) * .55
    dk = dk + purple[..., None] * hexc('#9A4CFF')
    place(img, np.clip(dk, 0, 1), ha, x, y, w, h)
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c0.webp'), q=80)
    SA.put_lay('sd_c0', 390, 844)
    return 'sd_c0'


def rainbow_bands(out, seed=103):
    """GIF 0 の 虹色の 光の 筋：ななめの 帯 4本（外は 紫・中は 緑・まん中は 白・ふちに 桃）。すき通し"""
    W, H = W2, H2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = random.Random(seed)
    acc = np.zeros((H, W, 3), np.float32)
    for (y0, wd) in ((300, 150), (560, 110), (1000, 170), (1290, 120)):
        ang = math.radians(-20 + r.uniform(-3, 3))
        # 帯の まん中からの きょり（ゆるく 波うつ）
        d = (yy - y0) * math.cos(ang) - (xx - W / 2) * math.sin(ang) + 18 * np.sin(xx / W * 4.2 + r.uniform(0, 6))
        u = d / wd
        band = np.zeros((H, W, 3), np.float32)
        band += hexc('#8A3CFF') * np.exp(-((u - .5) / .3) ** 2)[..., None] * .95
        band += hexc('#3CFF8C') * np.exp(-((u + .08) / .26) ** 2)[..., None] * .95
        band += hexc('#FFFFFF') * np.exp(-((u - .16) / .12) ** 2)[..., None] * .9
        band += hexc('#FF6AD8') * np.exp(-((u + .6) / .22) ** 2)[..., None] * .7
        along = .55 + .45 * smoothstep(.2, .7, fbm(H, W, 3, seed + int(y0), 3))
        acc += band * along[..., None]
    acc = cv2.GaussianBlur(acc, (0, 0), 5) + glow_of(acc, ((16, .35),))
    a = np.clip(acc.max(-1) * .88, 0, .9)
    SA.save(np.dstack([np.clip(acc, 0, 1) * a[..., None] / np.maximum(a, 1e-3)[..., None] * a[..., None], a]), os.path.join(out, 'sd_rbs.webp'), q=80)
    SA.put_lay('sd_rbs', 390, 844)
    return 'sd_rbs'


# ---------------------------------------------------------------- GIF 1：赤い 炎の 馬が 横に ずれる バグ
def scene_a_flat(out, bright=False):
    """① の 赤い 炎の 場面を 1まいに（背景・オーラ・赤い 炎・馬・赤い 目）→ 2倍の rgb。bright＝炎を 重ねて 明るく（GIF 1 の 炎と 桃色で いっぱいの 画面）"""
    import shiden
    W, H = W2, H2
    img = np.zeros((H, W, 3), np.float32)
    bg, ba = load('sd_bg', out)
    place(img, bg, ba, -40, -80, (390 + 40) * 2, (844 + 80) * 2)
    au = radial(H, W, (-60 + 255) * 2, (120 + 372) * 2, 520, 1.3, sx=.82)
    img = img + au[..., None] * hexc('#8C28E6') * .55
    for name, op in (('sd_fire_p2', .25), ('sd_fire_o1', 1.0)):
        fr, fa = load(name, out)
        place(img, fr, fa, -40, -60, (390 + 40) * 2, (844 + 60) * 2, op)
    if bright:
        for name, op, dy in (('sd_fire_o2', .7, -500), ('sd_fire_o3', .6, -200), ('sd_fire_o1', .55, -900), ('sd_fire_p1', .25, -800)):
            fr, fa = load(name, out)
            place(img, fr, fa, -40, -60 + dy, (390 + 40) * 2, (844 + 60) * 2, op, add=True)
        img = img + radial(H, W, W * .5, H * .45, W * .7, 1.4)[..., None] * hexc('#FF4ADC') * .25
        img = img * .92
        # GIF 1・2 の 明るさ：全体を 炎の 色で 持ち上げ・馬の うしろに 桃色と 白の 光（スクリーン）
        _, _, (hx, hy, hw, hh) = horse_layer(out)
        lift = np.zeros((H, W, 3), np.float32) + hexc('#FF8A2A') * .2
        lift = lift + radial(H, W, hx + hw * .5, hy + hh * .42, W * .62, 1.1, sx=.8)[..., None] * hexc('#FF6AE0') * .62
        lift = lift + radial(H, W, hx + hw * .5, hy + hh * .42, W * .3, 1.4, sx=.8)[..., None] * hexc('#FFE6FA') * .5
        img = 1 - (1 - np.clip(img, 0, 1)) * (1 - np.clip(lift, 0, 1))
    hr, ha, (x, y, w, h) = horse_layer(out)
    place(img, hr, ha, x, y, w, h)
    ex, ey = shiden.eye_pos()
    img = img + radial(H, W, ex * 2, ey * 2, 92, 1.6)[..., None] * hexc('#FF3048') * 1.2
    return np.clip(img, 0, 1)


def cut_glitch(out, seed=107):
    """GIF 1：横に 切った 帯が 左右に ずれる・赤と 青の ずれ・桃色が 強く"""
    base = scene_a_flat(out, bright=True)
    base = np.clip(base * np.array([1.15, .95, 1.1], np.float32) + np.array([.08, .01, .06], np.float32), 0, 1)
    H, W = base.shape[:2]
    r = random.Random(seed)
    img = base.copy()
    y = 0
    while y < H:
        bh = int(r.uniform(4, 46))
        dx = int(r.gauss(0, 26)) if r.random() < .7 else 0
        if dx:
            band = cv2.blur(np.roll(base[y:y + bh], dx, axis=1), (int(abs(dx) * 1.6) + 1, 1))   # 横に にじむ
            if r.random() < .5:
                band[..., 0] = np.roll(band[..., 0], 8, axis=1)
                band[..., 2] = np.roll(band[..., 2], -8, axis=1)
            img[y:y + bh] = band
        y += bh
    # 細い 横の 線（走査線）
    for _ in range(40):
        yy = int(r.uniform(0, H))
        img[yy:yy + 2] = np.clip(img[yy:yy + 2] * 1.6 + .1, 0, 1)
    save_rgb(img, os.path.join(out, 'sd_c1.webp'), q=78)
    SA.put_lay('sd_c1', 390, 844)
    return 'sd_c1'


def cut_fire(out):
    """GIF 2：明るい 炎と 桃色の 場面（赤い 目の 黒い 馬）。桃色の 雷は shiden.py の SVG で 上に"""
    img = scene_a_flat(out, bright=True)
    img = np.clip(img * np.array([1.08, .94, 1.04], np.float32) + np.array([.04, 0, .03], np.float32), 0, 1)
    save_rgb(img, os.path.join(out, 'sd_c2.webp'), q=78)
    SA.put_lay('sd_c2', 390, 844)
    return 'sd_c2'


# ---------------------------------------------------------------- GIF 3〜4：光る 目の ドアップ
def horse_cam(pose, e, t, fov, W, H, body, mane, line, mane_scale, mane_len, tail_len, wind_ang, ss=2, name='cu', line_w=6, light=(0.45, 0.8, 0.5)):
    """style2d.horse_illust と 同じ 描き方で、カメラ（e, t, fov）を じかに 決める（顔の ドアップ用）"""
    import style2d as S2
    R = S2.render_horse(pose, e, t, fov, W, H, ss=ss, name=name)
    rgb = S2.cel(R, body[0], body[1], light=light, bands=(0.18, 0.72), eye='#2A2030', hoof='#6A5A50')
    hair, ha = S2.mane_tail(R, (H, W), mane[0], mane[1], mode='flow', scale=mane_scale, seed=5, tail_len=tail_len, mane_len=mane_len, wind_ang=wind_ang)
    A = R['a']
    ln = S2.edges(R, width=line_w) * np.clip(A, 0, 1)
    out = np.zeros((H, W, 3), np.float32)
    a = np.zeros((H, W), np.float32)
    out = S2.over(out, rgb, A); a = np.maximum(a, A)
    out = S2.over(out, hair, ha); a = np.clip(a + ha * (1 - a), 0, 1)
    out = S2.over(out, S2.hexc(line), ln * 0.9)
    out = np.where(a[..., None] > 1e-4, out / np.maximum(a, 1e-4)[..., None], 0)
    return out, a, R


_HEAD = {}


def head_close(out, W=W2, H=H2):
    """馬の 顔の ドアップ（目が 左の まん中より 上）：全身の カメラから 顔へ ズーム（fov を せまく）→ (rgb, a, R)。1回だけ 描く"""
    if (W, H) in _HEAD:
        return _HEAD[(W, H)]
    cache = os.environ.get('SHIDEN_HEAD_CACHE')          # ためす 時：描いた 顔を 取って おく（作り直しを 速く）
    if cache and os.path.exists(cache):
        z = np.load(cache)
        _HEAD[(W, H)] = (z['rgb'], z['a'], dict(eye=tuple(z['eye'])))
        return _HEAD[(W, H)]
    rgb, a, R = _head_close(out, W, H)
    if cache:
        np.savez_compressed(cache, rgb=rgb, a=a, eye=np.array(R['eye']))
    _HEAD[(W, H)] = (rgb, a, dict(eye=tuple(R['eye'])))
    return _HEAD[(W, H)]


def _head_close(out, W, H):
    import style2d as S2
    import horse3d as Hm
    S2.TMP = os.path.join(out, '_tmp')
    os.makedirs(S2.TMP, exist_ok=True)
    W0, H0 = 300, 560
    fov0 = 26.0
    e0, t0 = S2.frame_horse(Hm.REAR, (25, 30, 280, 545), W0, H0, facing='right', azim=25, elev=6, fov=fov0)
    R0 = S2.render_horse(Hm.REAR, e0, t0, fov0, W0, H0, ss=1, name='cu0')
    P = S2.world_pos(R0)
    ex, ey = R0['eye']
    mx, my = R0['muzzle']
    def wp(x, y):
        xi, yi = int(round(x)), int(round(y))
        for rr in range(0, 8):
            for dy in range(-rr, rr + 1):
                for dx in range(-rr, rr + 1):
                    p = P[min(H0 - 1, max(0, yi + dy)), min(W0 - 1, max(0, xi + dx))]
                    if not np.isnan(p).any():
                        return p
        raise RuntimeError('顔が 見つからない')
    pe = wp(ex, ey)
    pm = wp(ex + (mx - ex) * .55, ey + (my - ey) * .55)
    tgt = pe + (pm - pe) * .12                      # 目より 少し 口の ほうを 見る → 目は 画面の 左より（0.39, 0.44）
    k = 9.0                                         # ズーム（顔が 画面 いっぱい）
    fov = math.degrees(2 * math.atan(math.tan(math.radians(fov0) / 2) / k))
    hscale = H / H0 * k                             # 全身の 絵に くらべた 大きさ
    rgb, a, R = horse_cam(Hm.REAR, e0, tgt, fov, W, H, body=('#3A1840', '#1E0A24'), mane=('#3A1A44', '#1A0A20'), line='#2A0E30',
                          mane_scale=.55 * hscale, mane_len=1.3, tail_len=1.0, wind_ang=-math.pi / 2, ss=2, name='cu1', line_w=10, light=(-0.35, 0.8, 0.5))
    return rgb, a, R


def eye_glow(img, ex, ey, scale=1.0, ang=-18.0, wide=1.0):
    """大きな 光る 目（アーモンド形の 黒い くぼみの 中に 白 → 黄 → だいだい → 赤の 光の 玉）と まわりの 光"""
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(ang)
    u = ((xx - ex) * math.cos(a) + (yy - ey) * math.sin(a)) / (95 * scale)
    v = (-(xx - ex) * math.sin(a) + (yy - ey) * math.cos(a)) / (58 * scale)
    almond = np.clip(1 - (np.abs(u) ** 1.6 + np.abs(v) ** 2.2), 0, 1)
    sock = smoothstep(0, .08, almond)
    img = img * (1 - sock[..., None] * .9) + hexc('#2A0408') * (sock * .9)[..., None]
    rr = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) / scale
    orb = smoothstep(0, .25, almond)
    img = img + orb[..., None] * (hexc('#FFFFFF') * np.exp(-(rr / 30) ** 2)[..., None] * 1.8 + hexc('#FFE070') * np.exp(-(rr / 52) ** 2)[..., None] * 1.3
                                  + hexc('#FF8A20') * np.exp(-((rr - 62) / 18) ** 2)[..., None] * 1.0 + hexc('#FF3A2A') * np.exp(-(rr / 90) ** 2)[..., None] * .7)
    img = img + (hexc('#FFD27A') * np.exp(-(rr / 150) ** 1.3)[..., None] * .55 + hexc('#FF5AB4') * np.exp(-(rr / 420) ** 1.2)[..., None] * .35) * wide
    return img


def strands(r, H, W, n, box, ang0, length, width):
    """たてがみ・前がみの 毛の たば（細長い 曲がった 帯）→ (毛の こさ 0〜1, ふちの 光 0〜1)"""
    hair = np.zeros((H, W), np.float32)
    hi = np.zeros((H, W), np.float32)
    for _ in range(n):
        x0, y0 = r.uniform(box[0], box[2]), r.uniform(box[1], box[3])
        a = math.radians(ang0 + r.uniform(-14, 14))
        L = length * r.uniform(.6, 1.2)
        bend = r.uniform(-.5, .5)
        w0 = width * r.uniform(.5, 1.2)
        pts_l, pts_r, mid = [], [], []
        for k in range(14):
            t = k / 13
            aa = a + bend * t
            x = x0 + math.cos(a) * L * t + math.cos(aa + math.pi / 2) * bend * 60 * t * t
            y = y0 + math.sin(a) * L * t + math.sin(aa + math.pi / 2) * bend * 60 * t * t
            ww = w0 * (1 - t) ** .8 + 1
            nx, ny = -math.sin(aa), math.cos(aa)
            pts_l.append((x + nx * ww, y + ny * ww))
            pts_r.append((x - nx * ww, y - ny * ww))
            mid.append((x + nx * ww * .7, y + ny * ww * .7))
        poly = np.array(pts_l + pts_r[::-1], np.float32)
        cv2.fillPoly(hair, [np.round(poly * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
        cv2.polylines(hi, [np.round(np.array(mid) * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
    return np.clip(hair, 0, 1), np.clip(hi, 0, 1) * np.clip(hair, 0, 1)


def eye_close(out, seed=109):
    """GIF 3〜4：白い 光に 焼けた 馬の 顔の ドアップ（うすい 紫と 白・目の まわりは 桃色）・大きく 光る 目（上に まぶたの 線）・
       前に たれる 白い 毛の たば（紫の ふち線）・目から 右上への 光の 筋（GIF の コマと 同じ 白っぽい 色）"""
    W, H = W2, H2
    rgb, a, R = head_close(out)
    ex, ey = R['eye']
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = fbm(H, W, 3, seed, 4)
    bg = ramp(f, ((0, (112, 78, 160)), (.5, (170, 132, 210)), (1, (230, 210, 246))))
    bg = np.clip(bg + radial(H, W, W * .1, H * .02, W * .8, 1.3)[..., None] * .5, 0, 1)
    # 顔：明るさの 段を うす紫の 色へ（なめらかに）
    lum = cv2.GaussianBlur(rgb, (0, 0), 9).mean(-1)
    inside = a > .5
    med = float(np.median(lum[inside]))
    shadow = cv2.GaussianBlur(np.clip((med - lum) / max(med * .4, 1e-4), 0, 1), (0, 0), 6)       # 暗い 段（影）
    d0 = dist_in(inside.astype(np.float32))
    u = .6 + .3 * (1 - yy / H) - .4 * shadow - .24 * np.exp(-d0 / 50) + .1 * (fbm(H, W, 4, seed + 8, 3) - .5)
    col = ramp(np.clip(u, 0, 1), ((0, (96, 54, 126)), (.35, (160, 116, 190)), (.7, (214, 186, 234)), (1, (244, 230, 252))))
    fur = cv2.GaussianBlur(noise(H, W, 300, seed + 2), (0, 0), .8, sigmaY=3)
    col = col * (.9 + .16 * fur[..., None])
    col = np.clip(col + radial(H, W, W * .1, H * .02, W * .75, 1.3)[..., None] * .35, 0, 1)      # 左上の 白い 光
    rr = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2)
    sk = np.exp(-(rr / 300) ** 1.4) * .7                                                      # 目の まわりの 桃色の はだ
    col = col * (1 - sk[..., None]) + hexc('#E8708E') * sk[..., None]
    d = dist_in((a > .5).astype(np.float32))
    col = col * (1 - (np.exp(-d / 5) * (a > .5) * .8)[..., None]) + hexc('#7A4A96') * (np.exp(-d / 5) * (a > .5) * .8)[..., None]   # 顔の ふちの 線（紫）
    img = bg * (1 - a[..., None]) + col * a[..., None]
    # 前に たれる 白い 毛の たば（左上から ななめ 下へ・紫の ふち線・目に かからない）
    hair, hl = strands(r, H, W, 9, (-120, -160, W * .75, H * .06), 70, 1150, 70)
    keep = 1 - np.exp(-(rr / 210) ** 2)
    hair, hl = hair * keep, hl * keep
    hcol = ramp(np.clip(.55 + .45 * fbm(H, W, 6, seed + 4, 3), 0, 1), ((0, (200, 170, 226)), (.6, (236, 220, 248)), (1, (255, 252, 255))))
    img = img * (1 - hair[..., None]) + hcol * hair[..., None]
    edge = np.clip(hair - cv2.erode(hair, np.ones((5, 5), np.uint8)), 0, 1)
    img = img * (1 - edge[..., None] * .85) + hexc('#6A3A8A') * (edge * .85)[..., None]
    img = img * (1 - hl[..., None] * .4) + hexc('#8A5AAA') * (hl * .4)[..., None]
    # まぶたの 線（目の 上の こい 弧）・まつ毛（こい 紫）
    lid = np.zeros((H, W), np.float32)
    pts = [(ex - 270 + 540 * t, ey - 100 - 100 * math.sin(math.pi * t) + 36 * t) for t in np.linspace(0, 1, 30)]
    cv2.polylines(lid, [np.round(np.array(pts) * 16).astype(np.int32)], False, 1.0, 20, cv2.LINE_AA, shift=4)
    for t in np.linspace(.15, .85, 7):
        x, y = ex - 270 + 540 * t, ey - 100 - 100 * math.sin(math.pi * t) + 36 * t
        cv2.line(lid, (int(x * 16), int(y * 16)), (int((x + 60 * (t - .5) - 8) * 16), int((y - 64) * 16)), 1.0, 7, cv2.LINE_AA, shift=4)
    img = img * (1 - lid[..., None] * .9) + hexc('#3A1446') * (lid * .9)[..., None]
    img = eye_glow(img, ex, ey, 2.3, -16, wide=.3)
    # 光の 筋（目から ななめ 右上へ：白い 黄色・太く）
    s1 = np.exp(-((((yy - ey) + (xx - ex) * .42)) / 14) ** 2) * np.clip(1 - rr / 1000, 0, 1) * (xx > ex)
    img = img + hexc('#FFF2B8') * s1[..., None] * .9 + hexc('#FFE08A') * cv2.GaussianBlur(s1, (0, 0), 14)[..., None] * .6
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_eye.webp'), q=82)
    SA.put_lay('sd_eye', 390, 844, eye=[round(float(ex) / 2, 1), round(float(ey) / 2, 1)])
    return 'sd_eye', (rgb, a, R)


# ---------------------------------------------------------------- GIF 5・6：裂け目
def tear_chunks(r, cy, slope, n, size, w=W2, h=H2):
    """裂け目の 上下の 大きな かけら（裂け目に つながる ギザギザの 大きな 形）→ 0〜1"""
    m = np.zeros((h, w), np.float32)
    for _ in range(n):
        x = r.uniform(-40, w + 40)
        y = cy + slope * (x - w / 2) + r.choice((-1, 1)) * r.uniform(20, 70)
        pts = shard_pts(r, x, y, r.uniform(*size), (1.4, 3.4))
        cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    return m


def cut_tear(out, kind):
    """GIF 5（red）：赤く 浮きぼりに なった うずの 画面・白い 大きな ギザギザの 裂け目・炎の 筋・右上に 虹色の ずれ
       GIF 6（green）：緑に 光る うずの 画面・黒い 大きな 裂け目（ふちに 白い かけら）・裂け目の 中の 炎"""
    W, H = W2, H2
    seed = 111 if kind == 'red' else 113
    r = random.Random(seed)
    ridge, lit, dark = veins(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if kind == 'red':
        img = ramp(lit, ((0, (20, 0, 0)), (.35, (90, 6, 4)), (.6, (170, 22, 14)), (.85, (235, 70, 50)), (1, (255, 170, 150))))
        img = img + hexc('#FF4A30') * (ridge * .35)[..., None]
        img = img * (1 - dark[..., None] * .9)
    else:
        img = ramp(lit, ((0, (0, 8, 0)), (.35, (8, 60, 10)), (.6, (34, 150, 34)), (.85, (110, 235, 96)), (1, (210, 255, 200))))
        img = img + hexc('#46FF4E') * (ridge * .55)[..., None] + hexc('#3CFF46') * cv2.GaussianBlur(ridge, (0, 0), 10)[..., None] * .4
        img = img * (1 - dark[..., None] * .92)
    # 炎の 筋（2たば：裂け目の 上と 下）
    fire = np.zeros((H, W, 3), np.float32)
    streaks(r, fire, 80, 600, math.radians(14), 460, 70, 60, FIRE_COLS, (1, 3))
    streaks(r, fire, 160, 1010, math.radians(-10), 480, 60, 50, FIRE_COLS, (1, 3))
    img = img + fire * .8 + glow_of(fire, ((3, .6), (10, .3)))
    if kind == 'red':
        tm = tear_mask(r, 840, 280, -.1, n=40, amp=34, spike=.45, spike_amp=3.6)
        tm = np.clip(tm + tear_chunks(r, 840, -.1, 24, (60, 170)), 0, 1)
        tm2 = tear_mask(r, 560, 70, .06, n=30, amp=14, spike=.35)
        tm = np.clip(tm + tm2 * smoothstep(W * .55, W * .4, xx), 0, 1)
        img = img * (1 - tm[..., None]) + np.array([1, 1, 1], np.float32) * tm[..., None]
        # 右上の 虹色の ずれ（ギザギザの 形の 中に ななめの 細い 虹の 筋）
        reg = np.zeros((H, W), np.float32)
        pts = [(W * .55, -20), (W + 20, -20), (W + 20, H * .3), (W * .86, H * .26), (W * .9, H * .16), (W * .7, H * .12), (W * .62, H * .05)]
        cv2.fillPoly(reg, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
        reg = reg * (fbm(H, W, 8, seed + 9, 3) > .42)
        hue = ((xx * .8 - yy) / 34) % 1.0
        rb = ramp(hue, RAINBOW)
        img = img * (1 - reg[..., None]) + rb * reg[..., None]
    else:
        tm = tear_mask(r, 860, 260, .07, n=40, amp=30, spike=.45, spike_amp=3.4)
        tm = np.clip(tm + tear_chunks(r, 860, .07, 16, (50, 130)), 0, 1)
        inside = np.zeros((H, W, 3), np.float32)
        streaks(r, inside, 40, 850, math.radians(5), 560, 80, 70, FIRE_COLS, (1, 3))
        inside = inside + glow_of(inside, ((4, .8), (12, .4)))
        img = img * (1 - tm[..., None]) + (inside * tm[..., None])
        al = np.zeros((H, W), np.float32)
        for _ in range(22):
            x = r.uniform(-20, W + 20)
            y = 860 + .07 * (x - W / 2) + r.choice((-1, 1)) * r.uniform(60, 130)
            pts = shard_pts(r, x, y, r.uniform(20, 60), (1.6, 3.4))
            m = np.zeros((H, W), np.float32)
            cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
            al = np.maximum(al, m * r.uniform(.85, 1))
        img = img * (1 - al[..., None]) + np.array([1, 1, 1], np.float32) * al[..., None]
    name = 'sd_c5' if kind == 'red' else 'sd_c6'
    save_rgb(np.clip(img, 0, 1), os.path.join(out, name + '.webp'), q=78)
    SA.put_lay(name, 390, 844)
    return name


def bezier(p, t):
    p0, p1, p2, p3 = (np.array(q, np.float32) for q in p)
    u = 1 - t
    return u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3


# ---------------------------------------------------------------- GIF 7〜15：割れた 鏡の かけらの 世界（GIF 10 を 横に 置いて 作り直し）
#   上：黒い 宇宙の 窓（星・銀の ギザギザの ふちと 赤い 光の 線）／右：白い 光の 筋と 白い 水晶／左：虹色の プリズム
#   まん中：左から のびる 赤い 角（つの）の 口に ピンクの 光・上と 下から 大きな 炎の 流れが 集まって 右へ 抜ける
#   下：銀の 金属の 黒い 馬（何重もの 白い ふち線・赤い 目）と 暗い 金属の 輪
def streak_tex(seed, ang_deg, sx=60, sy=4, W=W2, H=H2):
    """流れの 向き（画面の 角度°・下向きが ＋）に のびた 筋の もよう 0〜1"""
    big = int(math.hypot(W, H)) + 8
    rs = np.random.RandomState(seed)
    t = np.zeros((big, big), np.float32)
    for ax, ay, amp in ((sx, sy, 1.0), (sx / 2.2, sy / 2, .55)):
        small = rs.rand(max(2, int(big / ay)), max(2, int(big / ax))).astype(np.float32)
        t += cv2.resize(small, (big, big), interpolation=cv2.INTER_CUBIC) * amp
    t /= 1.55
    M = cv2.getRotationMatrix2D((big / 2, big / 2), -ang_deg, 1.0)
    t = cv2.warpAffine(t, M, (big, big), borderMode=cv2.BORDER_REFLECT)
    y0, x0 = (big - H) // 2, (big - W) // 2
    return np.clip(t[y0:y0 + H, x0:x0 + W], 0, 1)


FIRE_RAMP = ((0, (100, 6, 0)), (.14, (196, 34, 6)), (.3, (250, 100, 14)), (.46, (255, 164, 30)), (.62, (255, 216, 66)), (.8, (255, 244, 160)), (1, (255, 255, 236)))


def fire_stream(seed, curves, W=W2, H=H2):
    """大きな 炎の 流れ（GIF 7〜15：太くて 明るい 黄色の しん・だいだいと 赤の ふち・火の粉・小さな 黒い かけら）→ premultiplied RGBA。
       curves＝[(ベジェの 4点, 太さ はじめ, 太さ おわり, 筋の 数, 流れの 向き°)]"""
    r = random.Random(seed)
    I = np.zeros((H, W), np.float32)
    fil = np.zeros((H, W), np.float32)
    yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
    cur = list(curves)
    for pts, w0, w1, n, ang in curves[:2]:                       # 横に とび出す 炎（流れの 形を くずす）
        for _ in range(7):
            t = r.uniform(.05, .7)
            p = bezier(pts, t)
            q = bezier(pts, min(1, t + .02))
            a = math.atan2(q[1] - p[1], q[0] - p[0]) + math.radians(r.uniform(-28, 28))
            L = r.uniform(140, 300)
            e = (p[0] + L * math.cos(a), p[1] + L * math.sin(a))
            cur.append(((tuple(p), (p[0] + L * .3 * math.cos(a), p[1] + L * .3 * math.sin(a)), (e[0] - L * .3 * math.cos(a), e[1] - L * .3 * math.sin(a)), e),
                        (w0 + (w1 - w0) * t) * r.uniform(.25, .45), r.uniform(10, 30), 260, math.degrees(a)))
    for ci, (pts, w0, w1, n, ang) in enumerate(cur):
        samp = [bezier(pts, t) for t in np.linspace(0, 1, 220)]
        prof = np.zeros((H, W), np.float32)
        for f, k in ((1.0, .2), (.74, .24), (.5, .28), (.3, .32), (.15, .3)):
            m = np.zeros((H, W), np.float32)
            for i in range(len(samp) - 1):
                t = i / (len(samp) - 1)
                w = (w0 + (w1 - w0) * t) * f
                cv2.line(m, tuple(int(v) for v in samp[i]), tuple(int(v) for v in samp[i + 1]), 1.0, max(1, int(w)), cv2.LINE_AA)
            prof += cv2.GaussianBlur(m, (0, 0), max(2.0, min(w0, w1) * f * .16)) * k
        tex = streak_tex(seed * 7 + ci * 13, ang)
        tex2 = streak_tex(seed * 7 + ci * 13 + 5, ang, sx=150, sy=14)
        flake = smoothstep(.38, .72, streak_tex(seed * 7 + ci * 13 + 9, ang, sx=26, sy=3))
        if ci < 2:                                               # 光の 口の 手前で 少し よわく（まん中が 白く とばない ように）
            dcx = np.sqrt((xx_ - CXs) ** 2 + (yy_ - CYs) ** 2)
            prof = prof * (.4 + .6 * smoothstep(70, 260, dcx))
        I += prof * .8 * (.25 + .9 * tex) * (.5 + .7 * tex2) * (.5 + .7 * flake)
        # 細い 光の 筋（流れに そって・しんは 白い 黄色）
        for _ in range(n):
            t0 = r.random() ** .85
            L = r.uniform(.04, .2)
            off = r.gauss(0, 1) / 2.6
            drift = r.uniform(-.04, .04)
            line = []
            for kk in range(10):
                t = min(1, t0 + L * kk / 9)
                p = bezier(pts, t)
                q = bezier(pts, min(1, t + .01))
                d = q - p
                dn = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
                w = w0 + (w1 - w0) * t
                line.append(p + dn * (off + drift * kk / 9) * w)
            cv2.polylines(fil, [np.round(np.array(line) * 16).astype(np.int32)], False, r.uniform(.2, .55) * (1.4 - min(1, abs(off) * 1.6)), max(1, int(r.uniform(1, 3.4))), cv2.LINE_AA, shift=4)
        # 火の粉（流れの 中と まわり）
        for _ in range(n // 6):
            t = r.random()
            p = bezier(pts, t)
            q = bezier(pts, min(1, t + .01))
            d = q - p
            dn = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
            w = w0 + (w1 - w0) * t
            c = p + dn * r.gauss(0, .55) * w
            cv2.circle(fil, (int(c[0] * 16), int(c[1] * 16)), int(r.uniform(1, 3.2) * 16), r.uniform(.6, 1.2), -1, cv2.LINE_AA, shift=4)
    I = I + fil * .7 + cv2.GaussianBlur(fil, (0, 0), 3) * .35
    # 小さな 黒い かけら（炎の 中の ちり）
    dk = np.zeros((H, W), np.float32)
    for _ in range(900):
        x, y = r.uniform(0, W), r.uniform(0, H)
        if I[int(y), int(x)] < .35:
            continue
        pts = shard_pts(r, x, y, r.uniform(2.5, 8), (1.2, 2.6))
        cv2.fillPoly(dk, [np.round(np.array(pts) * 16).astype(np.int32)], r.uniform(.55, .9), cv2.LINE_AA, shift=4)
    I = I * (1 - dk)
    col = ramp(np.clip(I, 0, 1), FIRE_RAMP)
    a = smoothstep(.05, .4, I)
    pm = col * a[..., None]
    g = glow_of(pm, ((5, .3), (16, .2), (46, .12)))
    pm = pm + g
    a2 = np.clip(np.maximum(a, pm.max(-1) * .92), 0, 1)
    pm = np.minimum(pm, a2[..., None])
    return np.dstack([pm, a2])


STREAMS = (                                                  # 2倍の 座標：上と 下から まん中の 光（CXs, CYs）へ 集まり 右上へ 抜ける
    (((-180, 280), (40, 360), (230, 640), (CXs + 10, CYs - 40)), 360, 110, 2800, 38),
    (((-180, 1460), (40, 1380), (230, 1070), (CXs + 10, CYs + 40)), 380, 110, 2800, -38),
    (((CXs - 10, CYs), (540, 820), (680, 700), (960, 560)), 120, 300, 1700, -24))
CONE = dict(mx=330.0, rx=56.0, ry=176.0, ax=30.0, t0=22.0, b0=30.0)      # 赤い 角：口の まん中 x・口の 半径・左の はし・左の 上下の 幅


def jag_poly(r, corners, n, amp, spike=.2, spike_amp=3.0):
    """角の 点を つないで ギザギザに した 多角形の 点"""
    out = []
    m = len(corners)
    for i in range(m):
        (ax, ay), (bx, by) = corners[i], corners[(i + 1) % m]
        L = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / L, (bx - ax) / L
        k = max(2, int(n * L / 400))
        for j in range(k):
            t = j / k
            o = r.gauss(0, amp)
            if r.random() < spike:
                o += r.choice((-1, 1)) * amp * r.uniform(1.5, spike_amp)
            out.append((ax + (bx - ax) * t + nx * o, ay + (by - ay) * t + ny * o))
    return out


def fillm(pts, W=W2, H=H2):
    m = np.zeros((H, W), np.float32)
    cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    return m


def chrome_band(d, width, f):
    """ふちの 銀の 帯（ふちからの きょり d・幅 width）：銀の 明るさの ゆれ"""
    u = np.clip(d / width, 0, 1)
    return ramp(np.clip(u * .9 + (f - .5) * .5, 0, 1), CHROME)


def neon_line(m_out_d, at, wd):
    """形の 外がわ at px の ところの 光の 線"""
    return np.exp(-((m_out_d - at) / wd) ** 2)


def cone_geo(W=W2, H=H2):
    """赤い 角の 形：(角 全体の 0〜1, 口の 楕円の 0〜1, 角の 面の 上下の 位置 v 0〜1)"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    c = CONE
    mx, my, rx, ry, ax = c['mx'], CYs, c['rx'], c['ry'], c['ax']
    body = fillm([(ax, my - c['t0']), (mx, my - ry), (mx, my + ry), (ax, my + c['b0'])], W, H)
    ell = cv2.GaussianBlur((((xx - mx) / rx) ** 2 + ((yy - my) / ry) ** 2 <= 1).astype(np.float32), (0, 0), 1.2)
    cone = np.clip(body * (xx < mx) + ell, 0, 1)
    top_y = (my - c['t0']) + (xx - ax) / (mx - ax) * (-ry + c['t0'])
    bot_y = (my + c['b0']) + (xx - ax) / (mx - ax) * (ry - c['b0'])
    v = np.clip((yy - top_y) / np.maximum(bot_y - top_y, 1), 0, 1)
    return cone, ell, v


def mirror_world(out, seed=131):
    """GIF 7〜15 の 下じき（GIF 10 を 横に 置いて 作り直し）"""
    W, H = W2, H2
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = fbm(H, W, 5, seed, 4)
    f2 = fbm(H, W, 9, seed + 2, 4)
    # 1) 下じき：赤黒い 闇に 灰色の 金属の むら
    img = ramp(f, ((0, (6, 3, 6)), (.45, (30, 8, 14)), (.68, (86, 26, 40)), (.85, (150, 120, 128)), (1, (210, 200, 206))))
    # 2) 上：黒い 宇宙の 窓（星）・銀の ギザギザの ふち・赤い 光の 線
    win = fillm(jag_poly(r, [(250, 170), (520, 100), (720, 140), (740, 470), (580, 540), (370, 500), (240, 400)], 18, 9, .3, 3.2))
    d_in = dist_in(win)
    d_out = cv2.distanceTransform((win < .5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    space = np.zeros((H, W, 3), np.float32) + hexc('#030208')
    space = space + hexc('#5A1A6A') * (smoothstep(.55, .9, fbm(H, W, 4, seed + 5, 4)) * .35)[..., None]
    stars = (noise(H, W, 700, seed + 6, cv2.INTER_NEAREST) > .985).astype(np.float32)
    stars = cv2.GaussianBlur(stars, (0, 0), .7) * 2.2
    space = space + stars[..., None] * np.array([1, .95, 1], np.float32)
    img = img * (1 - win[..., None]) + space * win[..., None]
    band = (d_in < 26) * win
    img = img * (1 - band[..., None]) + chrome_band(d_in, 26, f2) * band[..., None]
    img = img + hexc('#FFFFFF') * (np.exp(-((d_in - 3) / 1.6) ** 2) * win * .8)[..., None]
    neon = neon_line(d_out, 5, 2.4) * (win < .5)
    img = img + hexc('#FF2A40') * neon[..., None] + hexc('#FF2050') * cv2.GaussianBlur(neon, (0, 0), 7)[..., None] * .8
    # 3) 右：白い 光の 筋
    rr_r = np.sqrt(((xx - (W + 60)) / 1.0) ** 2 + ((yy - 640) / 1.25) ** 2)
    light = np.exp(-(rr_r / 340) ** 1.5)
    ray = np.zeros((H, W), np.float32)
    for _ in range(28):
        a0 = math.radians(r.uniform(150, 215))
        L = r.uniform(300, 760)
        cv2.line(ray, (int((W + 60) * 16), int(640 * 16)), (int((W + 60 + L * math.cos(a0)) * 16), int((640 + L * math.sin(a0)) * 16)), r.uniform(.3, 1), int(r.uniform(3, 14)), cv2.LINE_AA, shift=4)
    ray = cv2.GaussianBlur(ray, (0, 0), 4) * np.exp(-(rr_r / 520) ** 1.4)
    img = img + ((light * 1.1 + ray * .8) * (1 - win))[..., None] * np.array([1, .97, 1], np.float32)
    # 4) 下：暗い 金属の 輪（白い ふち）
    rings = np.zeros((H, W), np.float32)
    dark = np.zeros((H, W), np.float32)
    for k, rad in enumerate((560, 470, 390, 320, 255)):
        e = np.sqrt(((xx - W * .74) / 1.0) ** 2 + ((yy - H * 1.0) / .62) ** 2)
        rings = np.maximum(rings, np.exp(-((e - rad) / (3.2 + k * .4)) ** 2) * (.6 + .4 * smoothstep(.3, .7, fbm(H, W, 6, seed + 30 + k, 3))))
        dark = np.maximum(dark, smoothstep(rad + 6, rad - 30, e) * (.55 + .1 * k))
    metal = ramp(np.clip(f2 * 1.2 - .1, 0, 1), ((0, (8, 8, 12)), (.5, (40, 40, 50)), (.8, (88, 88, 104)), (1, (150, 152, 170))))
    img = img * (1 - dark[..., None] * .92) + metal * (dark * .92)[..., None]
    img = img + hexc('#E8ECF8') * rings[..., None] * .9 + hexc('#FF4AC8') * cv2.GaussianBlur(rings, (0, 0), 9)[..., None] * .35
    # 5) かけら（上と ふちに たくさん・右は 白・左は 虹色・ところどころ 赤）
    def how(r_, x, y):
        k = r_.random()
        d_ = dict(chroma=.9 if r_.random() < .55 else 0.0)
        if x > W * .7 and y < H * .62 and k < .55:
            d_['tint'] = ((1, .96, 1), .6)
        elif x < W * .4 and H * .36 < y < H * .7 and k < .6:
            d_['tint'] = (ramp(np.array([(y / H * 1.8 + r_.random() * .25) % 1]), RAINBOW)[0], .7)
        elif k < .1:
            d_['tint'] = ((1, .25, .3), .6)
        elif k < .18:
            d_['style'] = 'dark'
        return d_
    specs = ((560, (-60, -60, W + 60, H * .4), (5, 28), how), (80, (-60, -60, W + 60, H * .36), (26, 64), how),
             (200, (W * .55, H * .2, W + 60, H * .66), (6, 40), how), (160, (-40, H * .34, W * .45, H * .72), (5, 30), how),
             (110, (W * .3, H * .4, W * .7, H * .62), (4, 16), how), (300, (-60, H * .64, W + 60, H + 60), (5, 30), how), (30, (-60, H * .7, W + 60, H + 60), (26, 60), how))
    sh, sa = shard_layer(seed + 1, specs)
    gaps = smoothstep(.34, .44, fbm(H, W, 7, seed + 41, 3))
    sa = sa * gaps * (1 - win * .9)
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    # 6) まん中：左から のびる 赤い 角（つの）・口の 中は 暗い 赤・ピンクの 光
    mx, my, rx, ry = CONE['mx'], CYs, CONE['rx'], CONE['ry']
    cone, ell, v = cone_geo()
    # 角の 面：上が 明るい だいだい → 下は こい 赤（つやの 筋）
    cc = ramp(v, ((0, (255, 170, 90)), (.12, (255, 120, 50)), (.3, (230, 60, 30)), (.6, (150, 20, 16)), (.85, (80, 8, 10)), (1, (150, 30, 24))))
    cc = cc + hexc('#FFE0B0') * np.exp(-((v - .1) / .03) ** 2)[..., None] * .6
    inner = (((xx - mx) / (rx * .82)) ** 2 + ((yy - my) / (ry * .9)) ** 2 <= 1).astype(np.float32)
    inner = cv2.GaussianBlur(inner, (0, 0), 2)
    inside = ramp(np.clip((xx - (mx - rx)) / (rx * 2), 0, 1), ((0, (40, 6, 8)), (.6, (110, 30, 34)), (1, (230, 120, 170))))
    cc = cc * (1 - inner[..., None]) + inside * inner[..., None]
    rimm = np.exp(-((np.sqrt(((xx - mx) / rx) ** 2 + ((yy - my) / ry) ** 2) - 1) / .035) ** 2)
    cc = cc + hexc('#FFD8F0') * rimm[..., None] * .9
    img = img * (1 - cone[..., None]) + cc * cone[..., None]
    # ピンクの 光（角の 口から 右へ）
    rr = np.sqrt(((xx - (CXs + 30)) / 1.0) ** 2 + ((yy - CYs) / 1.25) ** 2)
    img = img + hexc('#FF7AD8') * np.exp(-(rr / 130) ** 2)[..., None] * .85 + hexc('#FFD8F6') * np.exp(-(rr / 70) ** 2)[..., None] * .75
    # 7) 下：銀の 金属の 黒い 馬（何重もの 白い ふち線・外に 赤い 光の 線・赤い 目）
    hr, ha = load('sd_horse', out)
    sc = 1.42
    lw, lh = SA.LAY['sd_horse']['w'] * 2, SA.LAY['sd_horse']['h'] * 2
    exh, eyh = SA.LAY['sd_horse']['eye']
    ex2, ey2 = W * .76, H * .73
    px, py = ex2 - exh * 2 * sc, ey2 - eyh * 2 * sc
    M = place(np.zeros((H, W, 3), np.float32), np.ones(hr.shape, np.float32), ha, px, py, lw * sc, lh * sc)[..., 0]
    Hr = place(np.zeros((H, W, 3), np.float32), hr, ha, px, py, lw * sc, lh * sc)
    mm = (M > .5).astype(np.float32)
    dh = dist_in(mm)
    dho = cv2.distanceTransform((mm < .5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    lum = Hr.mean(-1) / np.maximum(M, 1e-3)
    met = ramp(np.clip(lum * 1.5 + (f2 - .5) * .5, 0, 1), ((0, (12, 12, 18)), (.45, (44, 44, 56)), (.75, (96, 98, 116)), (1, (190, 194, 210))))
    spec = smoothstep(.6, .66, fbm(H, W, 5, seed + 61, 3)) * smoothstep(.2, .5, f2)
    gloss = cv2.GaussianBlur(smoothstep(.56, .7, fbm(H, W, 3, seed + 63, 3)), (0, 0), 14) * np.clip(dh / 30, 0, 1)
    met = met + spec[..., None] * .55 + gloss[..., None] * np.array([.75, .76, .85], np.float32)
    cont = sum(np.exp(-((dh - k) / 1.7) ** 2) * w for k, w in ((4, 1.0), (14, .8), (27, .55), (44, .35)))
    met = met * (1 - np.clip(cont, 0, 1)[..., None]) + hexc('#F4F6FF') * np.clip(cont, 0, 1)[..., None]
    img = img * (1 - M[..., None]) + met * M[..., None]
    hn = neon_line(dho, 6, 2.2) * (mm < .5)
    img = img + hexc('#FF2A40') * hn[..., None] + hexc('#FF2A50') * cv2.GaussianBlur(hn, (0, 0), 8)[..., None] * .7
    rre = np.sqrt((xx - ex2) ** 2 + (yy - ey2) ** 2)
    img = img + hexc('#FF2030') * np.exp(-(rre / 40) ** 2)[..., None] * 1.6 + hexc('#FFFFFF') * np.exp(-(rre / 13) ** 2)[..., None]
    # 8) 赤い 光の 線（下の ほうの ギザギザ）
    neon2 = np.zeros((H, W), np.float32)
    for _ in range(7):
        x0, y0 = r.uniform(W * .2, W + 40), r.uniform(H * .62, H + 40)
        pts = [(x0, y0)]
        for k in range(r.randint(3, 6)):
            a = r.uniform(0, 2 * math.pi)
            L = r.uniform(50, 180)
            pts.append((pts[-1][0] + L * math.cos(a), pts[-1][1] + L * math.sin(a)))
        cv2.polylines(neon2, [np.round(np.array(pts) * 16).astype(np.int32)], False, 1.0, r.randint(2, 4), cv2.LINE_AA, shift=4)
    img = img + hexc('#FF2A48') * neon2[..., None] + hexc('#FF3A6A') * cv2.GaussianBlur(neon2, (0, 0), 6)[..., None] * .8
    # 9) 手前の かけら（少し）・明るい ところの にじみ
    specs2 = ((60, (-60, -60, W + 60, H + 60), (6, 22), how),)
    sh2, sa2 = shard_layer(seed + 77, specs2)
    sa2 = sa2 * (1 - cone)
    img = img * (1 - sa2[..., None]) + sh2 * sa2[..., None]
    br = np.clip(img - .72, 0, 1)
    img = img + glow_of(br, ((6, .45), (20, .28)))
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_w_bg.webp'), q=80)
    SA.put_lay('sd_w_bg', 390, 844, cx=CXs / 2, cy=CYs / 2)
    return 'sd_w_bg'


def mirror_near(out, seed=137):
    """手前の 大きな かけら（すみと ふち・少し ぼかす）"""
    W, H = W2, H2
    def how(r_, x, y):
        return dict(style='chrome' if r_.random() < .75 else 'dark', edge=1.0, chroma=.9)
    specs = ((7, (-80, -80, W + 80, H * .02), (50, 100), how), (7, (-80, H * .95, W + 80, H + 80), (50, 110), how),
             (3, (-100, H * .2, W * .04, H * .8), (40, 90), how), (3, (W * .96, H * .2, W + 100, H * .8), (40, 90), how))
    sh, sa = shard_layer(seed, specs)
    sh = cv2.GaussianBlur(sh, (0, 0), 2.0)
    sa = cv2.GaussianBlur(sa, (0, 0), 2.0) * .6
    # 炎の 上を とぶ 小さな かけら（ぼかさない・まん中の 光の まわりは あける）
    def how2(r_, x, y):
        return dict(style='chrome' if r_.random() < .8 else 'dark', edge=1.0, chroma=.9 if r_.random() < .5 else 0.0)
    s2, a2 = shard_layer(seed + 5, ((150, (-40, -40, W + 40, H + 40), (4, 15), how2),))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a2 = a2 * smoothstep(110, 190, np.sqrt((xx - CXs) ** 2 + (yy - CYs) ** 2))
    sh = s2 * a2[..., None] + sh * (1 - a2[..., None])
    sa = np.clip(a2 + sa * (1 - a2), 0, 1)
    sh = np.where(sa[..., None] > 1e-4, sh, 0)
    SA.save(np.dstack([sh * sa[..., None], sa]), os.path.join(out, 'sd_w_near.webp'), q=80)
    SA.put_lay('sd_w_near', 390, 844)
    return 'sd_w_near'


def mirror_fire(out):
    for k, seed in ((1, 141), (2, 149)):
        img = fire_stream(seed, STREAMS)
        SA.save(img, os.path.join(out, f'sd_w_fire{k}.webp'), q=80)
        SA.put_lay(f'sd_w_fire{k}', 390, 844)
    return ['sd_w_fire1', 'sd_w_fire2']


def mirror_prism(out, seed=151):
    """左の 虹色の プリズム（なめらかな うずの 虹・水晶の 面・炎の 下）"""
    W, H = W2, H2
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q1, q2 = fbm(H, W, 3, seed + 1, 3), fbm(H, W, 3, seed + 2, 3)
    f = fbm(H, W, 4, seed, 4)
    f = cv2.remap(f, (xx + 220 * (q1 - .5)).astype(np.float32), (yy + 220 * (q2 - .5)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    hue = (f * 2.6 + yy / H * .9 + xx / W * .4) % 1.0
    col = ramp(hue, ((0, (255, 60, 200)), (.18, (150, 90, 255)), (.34, (60, 200, 255)), (.5, (60, 255, 160)), (.66, (210, 255, 70)), (.82, (255, 210, 60)), (1, (255, 60, 200))))
    lum = .7 + .45 * smoothstep(.35, .8, fbm(H, W, 7, seed + 3, 3))
    col = np.clip(col * lum[..., None] + .12, 0, 1)
    # 水晶の 面（細かい かけらの ふち）
    def how(r_, x, y):
        return dict(fill=tuple(float(v) for v in col[int(min(H - 1, max(0, y))), int(min(W - 1, max(0, x)))] * r_.uniform(.7, 1.15)), edge=.9, chroma=.6)
    sh, sa = shard_layer(seed + 9, ((260, (-40, H * .36, W * .46, H * .72), (6, 26), how),))
    col = col * (1 - sa[..., None] * .7) + np.clip(sh, 0, 1) * (sa * .7)[..., None]
    reg = smoothstep(W * .5, W * .08, xx + 40 * (q1 - .5)) * smoothstep(H * .35, H * .42, yy + 60 * (q2 - .5)) * smoothstep(H * .74, H * .66, yy + 60 * (q2 - .5))
    a = np.clip(reg * .95, 0, 1) * (1 - cone_geo()[0])
    SA.save(np.dstack([col * a[..., None], a]), os.path.join(out, 'sd_w_prism.webp'), q=80)
    SA.put_lay('sd_w_prism', 390, 844)
    return 'sd_w_prism'


# ---------------------------------------------------------------- GIF 16〜20
def cut_invert(out, seed=161):
    """GIF 16：白い 地・水色で ぬった かけらと 水色の ふちの 白い かけら・まん中に 横に 広い 黒い 穴（中に 赤から 黄色の 炎）"""
    W, H = W2, H2
    r = random.Random(seed)
    img = np.ones((H, W, 3), np.float32) * hexc('#F8FCFF')
    pts = []
    for k in range(44):
        a = 2 * math.pi * k / 44
        rr = r.uniform(.8, 1.12)
        pts.append((W * .5 + math.cos(a) * W * .47 * rr, H * .5 + math.sin(a) * H * .22 * rr))
    hole = fillm(pts)
    fire = np.zeros((H, W, 3), np.float32)
    streaks(r, fire, W * .28, H * .5, math.radians(-12), 600, 170, 300, FIRE_COLS, (1, 3))
    fire = fire + glow_of(fire, ((4, .8), (12, .5)))
    img = img * (1 - hole[..., None]) + np.clip(fire, 0, 1) * hole[..., None]
    CYS = ((.62, .95, .98), (.46, .9, .96), (.8, .98, 1.0), (.3, .86, .95))
    def how(r_, x, y):
        if r_.random() < .7:
            return dict(fill=CYS[r_.randrange(len(CYS))], outline=((.16, .74, .88), r_.randint(2, 4)), edge=0)
        return dict(fill=(1, 1, 1), outline=((.22, .84, .95), r_.randint(4, 7)), edge=0)
    specs = ((40, (-60, -60, W + 60, H * .29), (50, 140), how), (40, (-60, H * .71, W + 60, H + 60), (50, 140), how), (7, (-60, H * .3, W + 60, H * .7), (24, 60), how))
    sh, sa = shard_layer(seed, specs)
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c16.webp'), q=78)
    SA.put_lay('sd_c16', 390, 844)
    return 'sd_c16'


def cut_hole(out, seed=163):
    """GIF 17：まん中が 黒い 穴・まわりは 銀の かけら（ふちに 青と だいだいの にじみ）・下に 白い かたまり"""
    W, H = W2, H2
    r = random.Random(seed)
    img = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W * .5) / (W * .42)) ** 2 + ((yy - H * .5) / (H * .2)) ** 2)
    keep = (rr + .5 * (fbm(H, W, 10, seed + 3, 3) - .5) > 1.0).astype(np.float32)
    def how(r_, x, y):
        k = r_.random()
        if k < .12:
            return dict(tint=((.5, .66, 1), .5))
        if k < .2:
            return dict(tint=((1, .6, .25), .5))
        if k < .85:
            return dict(tint=((1, 1, 1), .8))
        return dict()
    def how2(r_, x, y):
        d_ = how(r_, x, y)
        d_['chroma'] = .9
        return d_
    specs = ((1100, (-60, -60, W + 60, H + 60), (8, 46), how2), (140, (-60, -60, W + 60, H + 60), (46, 100), how2))
    sh, sa = shard_layer(seed, specs)
    sa = sa * keep
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    # 白い かたまり（手前・下）
    blk = np.zeros((H, W), np.float32)
    pts = [(W * .52, H * .53), (W * .76, H * .57), (W * .7, H * .69), (W * .46, H * .65)]
    cv2.fillPoly(blk, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    g = ramp(np.clip((yy - H * .58) / (H * .16), 0, 1), ((0, (255, 255, 255)), (.6, (230, 232, 238)), (1, (150, 150, 158))))
    img = img * (1 - blk[..., None]) + g * blk[..., None]
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c17.webp'), q=78)
    SA.put_lay('sd_c17', 390, 844)
    return 'sd_c17'


def cut_dark(out, seed=167):
    """GIF 18：黒・上と 下の はしに かけら・とんで いく かけらが いくつか"""
    W, H = W2, H2
    img = np.zeros((H, W, 3), np.float32)
    def how(r_, x, y):
        return dict(tint=((.6, .75, 1), .3)) if r_.random() < .2 else dict()
    specs = ((90, (-60, -60, W + 60, H * .14), (12, 60), how), (60, (-60, H * .88, W + 60, H + 60), (12, 60), how), (12, (0, H * .2, W, H * .8), (14, 40), how))
    sh, sa = shard_layer(seed, specs)
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c18.webp'), q=78)
    SA.put_lay('sd_c18', 390, 844)
    return 'sd_c18'


def cut_ring(out, seed=169):
    """GIF 19〜20：暗い 緑（まん中が 少し 明るい）・うすい けむり・金の 輪"""
    W, H = W2, H2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2)
    f = fbm(H, W, 4, seed, 4)
    img = ramp(np.clip(1 - rr / (H * .62), 0, 1) * .8 + f * .25, ((0, (4, 12, 6)), (.4, (8, 34, 16)), (.75, (20, 80, 36)), (1, (60, 150, 70))))
    ring = np.exp(-((rr - W * .43) / 3.2) ** 2) * (.75 + .25 * smoothstep(.3, .7, f))
    img = img + hexc('#FFD86A') * ring[..., None] + hexc('#FFC03A') * cv2.GaussianBlur(ring, (0, 0), 7)[..., None] * .9
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c19.webp'), q=80)
    SA.put_lay('sd_c19', 390, 844)
    return 'sd_c19'


def pillar(out, seed=171):
    """左右の 炎の 柱（左の 柱：内がわ（右）の ふちが いちばん 明るい 黄色・外は だいだいと 赤）。右は CSS で 左右 反転"""
    W, H = 120, H2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = fbm(H, W, 6, seed, 5)
    q = fbm(H, W, 3, seed + 3, 3)
    f = cv2.remap(f, (xx + 20 * (q - .5)).astype(np.float32), (yy + 120 * (q - .5)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    u = xx / W
    t = np.clip(u * .9 + (f - .5) * .5, 0, 1)
    col = ramp(t, ((0, (90, 8, 4)), (.35, (200, 40, 10)), (.65, (255, 130, 30)), (.85, (255, 220, 120)), (1, (255, 250, 230))))
    edge = np.exp(-((u - .9) / .05) ** 2)
    col = col + hexc('#FFF4C8') * edge[..., None] * .8
    a = np.clip(smoothstep(.0, .25, u) * .9 + .1, 0, 1) * smoothstep(1.0, .93, u)
    SA.save(np.dstack([np.clip(col, 0, 1) * a[..., None], a]), os.path.join(out, 'sd_pillar.webp'), q=80)
    SA.put_lay('sd_pillar', W / 2, H / 2)
    return 'sd_pillar'


def build(out, names=None):
    todo = dict(sd_c0=lambda: cut_gray(out), sd_rbs=lambda: rainbow_bands(out), sd_c1=lambda: cut_glitch(out), sd_c2=lambda: cut_fire(out), sd_eye=lambda: eye_close(out)[0],
                sd_c5=lambda: cut_tear(out, 'red'), sd_c6=lambda: cut_tear(out, 'green'), sd_w_bg=lambda: mirror_world(out), sd_w_near=lambda: mirror_near(out),
                sd_w_fire=lambda: mirror_fire(out), sd_w_prism=lambda: mirror_prism(out), sd_c16=lambda: cut_invert(out), sd_c17=lambda: cut_hole(out),
                sd_c18=lambda: cut_dark(out), sd_c19=lambda: cut_ring(out), sd_pillar=lambda: pillar(out))
    made = []
    for k, fn in todo.items():
        if names and k not in names:
            continue
        r = fn()
        made += r if isinstance(r, list) else [r]
        print('made', r, flush=True)
    return made
