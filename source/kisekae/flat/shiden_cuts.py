"""紫電（第4.68版〜第4.69版）：見本の 動画（1.55秒〜5.00秒）の コマに 合わせた ② の 絵（WebP）。
   第4.68版：まさちゃん「え？ファイルのこの、画像からこの画像まで確認して！は確認してないってこと？ もう一度送る！」（GIF 21コマ）
   第4.69版：まさちゃん「もう一度動画みて作り直して！ 二枚目の写真は左から右に切り裂くんだよ！ 三枚目の馬の顔は動きをつけて長めにして！ リアルに！」
            「8秒くらいあっていいからね！」→ 動画を コマ送りで 見て、GIF に なかった コマ（暗い 影と 青緑の 雷・白黒の ネガ・色ずれの 割れた 画面・
            白と 桃色の ひび・だいだいの 爆発・反転の 赤と 青）を 足し、② を 約8.6秒に。顔は flat/shiden_face.py（リアルな 3D の 黒い 馬の 顔：12コマ）。
            「画面を切るのをコーンじゃなくて馬の蹄にして！」→ 世界を 切り裂くのは 馬の 蹄（flat/shiden_hoof.py）。
            「このシーンの青丸の模様と馬いらない！」→ 鏡の 世界の 宇宙の 窓と 銀の 金属の 馬を やめた。
   動画の 絵・人物・機械・字は 使わない・なぞらない。もらうのは コマの 順・長さ・色・形の 種類だけ。
   人物の 代わりは テンゲルの 黒い 馬（r3d の 3Dの 馬）、機械の 代わりは 銀の 金属の 馬（赤い 目）、白い 線の 文字は「的中」。
   出す 絵（shiden_art.py の build から 呼ぶ。大きさは shiden_layers.json・id は shiden_blobs.json。どれも 画面と 同じ 390×844 の 2倍）：
     sd_c0・sd_rbs … 白黒の 煙・白い 線の「的中」・黒い 馬・虹色の 光の 筋 ／ sd_c1 … 炎と 桃色の バグ ／ sd_c2 … 明るい 炎（桃色の 雷は SVG）
     sd_dk  … 暗い 画面・まっ黒な 馬の 影・赤い 目・青緑の 雷 ／ sd_bw・sd_bwc … 白黒の ネガ・水色の 反転
     sd_rf00〜 … リアルな 馬の 顔（shiden_face.py）
     sd_chr … 色ずれの 割れた 白黒 ／ sd_crk … 白と 桃色・黒い 裂け目と ひび ／ sd_c5 … 赤黒い うずと 白い 裂け目 ／ sd_boom … だいだいの 爆発と 黒い 裂け目 ／ sd_c6 … 緑と 黒の うずと 黒い 裂け目
     sd_w_bg・sd_w_near・sd_w_fire1〜3・sd_w_prism … 割れた 鏡の かけらの 世界（かけら・ピンクの 光・集まる 炎・虹色。第4.69版：宇宙の 窓と 銀の 金属の 馬は やめた）
     sd_w_hoof … 世界を 左から 右へ 切り裂く 馬の 蹄（flat/shiden_hoof.py：3D の 黒い 馬の 足・灰色の 蹄・焼けた 蹄鉄・すき通し）
     sd_c16・sd_c16r・sd_c16b … 白と 水色・黒と 赤・白と 青の 割れた 画面と 穴 ／ sd_c17 … 黒い 穴と 白い かけら ／ sd_c18 … 黒と 金の 光 ／ sd_c19 … 緑に 金の 輪 ／ sd_pillar … 左右の 炎の 柱"""
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
    x0, y0, w = shiden.horse_a(SA.LAY['sd_horse'])                 # いま 作った 馬の 絵の 大きさで（第4.69版：しっぽ）
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


# GIF 3〜4（目の ドアップ）は 第4.69版から リアルな 馬の 顔の コマ（flat/shiden_face.py：sd_rf00〜）


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
#   まん中：ピンクの 光（第4.68版の 赤い 角は 第4.69版で やめて 馬の 蹄に）・上と 下から 大きな 炎の 流れが 集まって 右へ 抜ける
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


def mirror_world(out, seed=131):
    """GIF 7〜15 の 下じき（GIF 10 を 横に 置いて 作り直し）。第4.69版：上の 宇宙の 窓・下の 金属の 馬と 輪と 赤い 線は やめて、かけらの 世界に"""
    W, H = W2, H2
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = fbm(H, W, 5, seed, 4)
    f2 = fbm(H, W, 9, seed + 2, 4)
    # 1) 下じき：赤黒い 闇に 灰色の 金属の むら
    img = ramp(f, ((0, (6, 3, 6)), (.45, (30, 8, 14)), (.68, (86, 26, 40)), (.85, (150, 120, 128)), (1, (210, 200, 206))))
    # 2) （第4.69版：上の 黒い 宇宙の 窓は やめた・まさちゃん「このシーンの青丸の模様と馬いらない！」）
    win = np.zeros((H, W), np.float32)
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
    # 4) （第4.69版：下の 暗い 金属の 輪は やめた）
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
    # 6) まん中：ピンクの 光（第4.69版：赤い 角は やめた。世界を 切り裂くのは 馬の 蹄 sd_w_hoof：flat/shiden_hoof.py）
    rr = np.sqrt(((xx - (CXs + 30)) / 1.0) ** 2 + ((yy - CYs) / 1.25) ** 2)
    img = img + hexc('#FF7AD8') * np.exp(-(rr / 130) ** 2)[..., None] * .85 + hexc('#FFD8F6') * np.exp(-(rr / 70) ** 2)[..., None] * .75
    # 7)・8) （第4.69版：下の 銀の 金属の 馬と 赤い 光の 線は やめた・まさちゃん「馬いらない！」）
    # 9) 手前の かけら（少し）・明るい ところの にじみ
    specs2 = ((60, (-60, -60, W + 60, H + 60), (6, 22), how),)
    sh2, sa2 = shard_layer(seed + 77, specs2)
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
    a = np.clip(reg * .95, 0, 1)
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


# ---------------------------------------------------------------- 第4.69版：見本の 動画を コマ送りで 見て 足した コマ
def cut_shadow(out, seed=181):
    """動画 1.70・1.93秒：画面が 暗く なり 馬は まっ黒な 影・赤く 光る 目・右に 青緑の 雷（sd_dk）"""
    W, H = W2, H2
    import shiden
    base = scene_a_flat(out, bright=True)
    img = base * np.array([.6, .28, .36], np.float32)                     # 暗く した 炎（まだ 見える）
    hr, ha, (x, y, w, h) = horse_layer(out)
    blk = np.zeros((H, W, 3), np.float32) + hexc('#050207')
    M = place(np.zeros((H, W, 3), np.float32), np.ones(hr.shape, np.float32), ha, x, y, w, h)[..., 0]
    img = img * (1 - M[..., None]) + blk * M[..., None]
    ex, ey = shiden.horse_a(SA.LAY['sd_horse'])[0] + SA.LAY['sd_horse']['eye'][0] * shiden.HORSE_K, shiden.horse_a(SA.LAY['sd_horse'])[1] + SA.LAY['sd_horse']['eye'][1] * shiden.HORSE_K
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - ex * 2) ** 2 + (yy - ey * 2) ** 2)
    img = img + hexc('#FF1830') * np.exp(-(rr / 70) ** 1.4)[..., None] * 1.3 + hexc('#FFFFFF') * np.exp(-(rr / 14) ** 2)[..., None]
    # 青緑の 雷（右から 下へ・枝つき）
    r = random.Random(seed)
    bolt = np.zeros((H, W), np.float32)
    for (a, b) in (((W * .82, -20), (W * .55, H * .62)), ((W * .9, H * .2), (W * .72, H * .95))):
        pts = disp(r, a, b, (.14, .18, .24, .3, .34))
        cv2.polylines(bolt, [np.round(np.array(pts) * 16).astype(np.int32)], False, 1.0, 4, cv2.LINE_AA, shift=4)
        for _ in range(3):
            i = r.randrange(2, len(pts) - 2)
            q = pts[i]
            ang = math.atan2(b[1] - a[1], b[0] - a[0]) + r.choice((-1, 1)) * r.uniform(.5, 1.1)
            L = r.uniform(60, 160)
            br = disp(r, q, (q[0] + L * math.cos(ang), q[1] + L * math.sin(ang)), (.4, .45))
            cv2.polylines(bolt, [np.round(np.array(br) * 16).astype(np.int32)], False, .8, 2, cv2.LINE_AA, shift=4)
    img = img + hexc('#E8FFFF') * bolt[..., None] + hexc('#28E0C8') * cv2.GaussianBlur(bolt, (0, 0), 6)[..., None] * 1.2 + hexc('#2A6CFF') * cv2.GaussianBlur(bolt, (0, 0), 18)[..., None] * .8
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_dk.webp'), q=78)
    SA.put_lay('sd_dk', 390, 844)
    return 'sd_dk'


def cut_bw(out, seed=183):
    """動画 2.03〜2.10秒：白黒の ネガ（黒い 地に 太い 白い 線・下は 白く ぬれる）＝ sd_bw と、水色に 反転した 1コマ sd_bwc"""
    W, H = W2, H2
    base = scene_a_flat(out, bright=True)
    L = cv2.GaussianBlur(base.mean(-1), (0, 0), 5)
    hr, ha, (x, y, w, h) = horse_layer(out)
    M = place(np.zeros((H, W, 3), np.float32), np.ones(hr.shape, np.float32), ha, x, y, w, h)[..., 0]
    lines = np.zeros((H, W), np.float32)
    m = (L > .6).astype(np.uint8)                                         # 明るい 所の 形の ふちを 太い 白い 線に（ほそい 線は 出さない）
    cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for c in cs:
        if len(c) > 120:
            cv2.polylines(lines, [c], True, 1.0, 14, cv2.LINE_AA)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fillw = (L > .82).astype(np.float32) * smoothstep(H * .35, H * .62, yy)   # 下の 明るい 所は 白く ぬる
    fillw = np.maximum(fillw, (cv2.GaussianBlur(fbm(H, W, 5, seed + 3, 3), (0, 0), 3) > .62).astype(np.float32) * smoothstep(H * .55, H * .8, yy))
    mb = (M > .5).astype(np.uint8)
    edge = cv2.morphologyEx(mb, cv2.MORPH_GRADIENT, np.ones((15, 15), np.uint8)).astype(np.float32)
    img = np.clip(lines + fillw, 0, 1) * (1 - M) + edge
    r = random.Random(seed)
    for _ in range(26):                                                   # 白い かけら
        pts = shard_pts(r, r.uniform(0, W), r.uniform(0, H), r.uniform(10, 40), (1.2, 3))
        cv2.fillPoly(img, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    img = np.clip(cv2.GaussianBlur(img, (0, 0), .8) * 1.15, 0, 1)
    save_rgb(np.dstack([img, img, img]), os.path.join(out, 'sd_bw.webp'), q=80)
    SA.put_lay('sd_bw', 390, 844)
    # 水色の 反転：白い 地・こい 青の 線・うすい 水色の むら
    inv = 1 - img
    f = fbm(H, W, 4, seed + 1, 3)
    col = ramp(np.clip(inv * .9 + f * .2, 0, 1), ((0, (10, 30, 210)), (.35, (40, 120, 255)), (.7, (170, 235, 255)), (1, (250, 254, 255))))
    save_rgb(np.clip(col, 0, 1), os.path.join(out, 'sd_bwc.webp'), q=80)
    SA.put_lay('sd_bwc', 390, 844)
    return ['sd_bw', 'sd_bwc']


def cut_chroma(out, seed=185):
    """動画 2.27〜2.30秒：黒と 白の 割れた 画面・ふちが 赤と 水色と 青に ずれる（sd_chr）"""
    W, H = W2, H2
    r = random.Random(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(80):                                                   # 白い 大きな 割れた 形
        pts = shard_pts(r, r.uniform(-60, W + 60), r.uniform(-60, H + 60), r.uniform(60, 240), (1.2, 3.2))
        cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], r.uniform(.55, 1.0), cv2.LINE_AA, shift=4)
    cx_, cy_ = W * .5, H * .48
    for k in range(26):                                                   # まん中から 外への ひび（放射）
        a_ = 2 * math.pi * k / 26 + r.uniform(-.1, .1)
        pts = disp(r, (cx_, cy_), (cx_ + math.cos(a_) * 1100, cy_ + math.sin(a_) * 1100), (.1, .14, .18))
        cv2.polylines(m, [np.round(np.array(pts) * 16).astype(np.int32)], False, 1.0, r.randint(3, 7), cv2.LINE_AA, shift=4)
    for _ in range(34):                                                   # 黒い 割れた 形（上に 重ねる）
        pts = shard_pts(r, r.uniform(-60, W + 60), r.uniform(-60, H + 60), r.uniform(40, 180), (1.4, 3.4))
        cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], 0.0, cv2.LINE_AA, shift=4)
    tm = tear_mask(r, H * .52, 120, -.12, n=40, amp=26, spike=.4)
    m = m * (1 - tm)
    edge = np.abs(cv2.Sobel(cv2.GaussianBlur(m, (0, 0), 1.5), cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(cv2.GaussianBlur(m, (0, 0), 1.5), cv2.CV_32F, 0, 1, ksize=3))
    edge = np.clip(edge * 2.5, 0, 1)
    img = np.dstack([m, m, m]) * .9
    for col, dx, dy in (((1, .15, .2), 9, 0), ((.2, .95, 1), -9, 3), ((.25, .35, 1), 0, -7)):
        e2 = np.roll(np.roll(edge, dx, 1), dy, 0)
        img = img + np.array(col, np.float32) * e2[..., None] * .9
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_chr.webp'), q=78)
    SA.put_lay('sd_chr', 390, 844)
    return 'sd_chr'


def cut_crack(out, seed=187):
    """動画 2.33〜2.35秒：白と 桃色の 明るい 画面・左から 黒い ギザギザの 裂け目・黒い ひびの 線・左上に 炎の 筋（sd_crk）"""
    W, H = W2, H2
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = fbm(H, W, 5, seed, 4)
    img = ramp(f, ((0, (255, 200, 214)), (.5, (255, 232, 238)), (1, (255, 252, 252))))
    img = img * (1 - radial(H, W, W * .78, H * .58, W * .55, 1.2)[..., None] * np.array([0, .25, .18], np.float32))
    # 黒い 裂け目（左から 右へ 細く なる）
    top = jag_edge(r, -40, W * .95, H * .5 - 78, H * .5 - 4, 36, 12, .4, 3.2)
    bot = jag_edge(r, -40, W * .95, H * .5 + 70, H * .5 + 3, 36, 12, .4, 3.2)
    tear = fillm(top + bot[::-1])
    for _ in range(9):                                                    # とげ
        x0 = r.uniform(0, W * .7)
        pts = [(x0, H * .5), (x0 + r.uniform(30, 90), H * .5 + r.choice((-1, 1)) * r.uniform(40, 110)), (x0 + r.uniform(60, 140), H * .5)]
        cv2.fillPoly(tear, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    # ひび（左の くもの 巣）
    cr = np.zeros((H, W), np.float32)
    cx, cy = W * .12, H * .48
    for k in range(9):
        a = 2 * math.pi * k / 9 + r.uniform(-.2, .2)
        pts = disp(r, (cx, cy), (cx + math.cos(a) * r.uniform(220, 420), cy + math.sin(a) * r.uniform(220, 420)), (.12, .16, .2))
        cv2.polylines(cr, [np.round(np.array(pts) * 16).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA, shift=4)
    for rad in (90, 170, 260):
        pts = [(cx + math.cos(t) * rad * r.uniform(.9, 1.1), cy + math.sin(t) * rad * r.uniform(.9, 1.1)) for t in np.linspace(0, 2 * math.pi, 14)]
        cv2.polylines(cr, [np.round(np.array(pts) * 16).astype(np.int32)], True, 1.0, 2, cv2.LINE_AA, shift=4)
    cr = cr * smoothstep(W * .55, W * .3, xx)
    img = img * (1 - np.clip(tear + cr, 0, 1)[..., None])
    fire = np.zeros((H, W, 3), np.float32)
    streaks(r, fire, W * .2, H * .3, math.radians(-14), 360, 40, 70, FIRE_COLS, (1, 3))
    img = img * (1 - np.clip(fire.max(-1), 0, 1)[..., None] * .6) + fire + glow_of(fire, ((3, .5), (10, .3)))
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_crk.webp'), q=78)
    SA.put_lay('sd_crk', 390, 844)
    return 'sd_crk'


def cut_boom(out, seed=189):
    """動画 2.40秒：だいだいと 黄色の 大きな 爆発・光の 筋と 火花・まん中を 黒い 裂け目（sd_boom）"""
    W, H = W2, H2
    r = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * .48, H * .44
    rr = np.sqrt((xx - cx) ** 2 + ((yy - cy) * .8) ** 2)
    ang = np.arctan2(yy - cy, xx - cx)
    rays = np.zeros((H, W), np.float32)
    for _ in range(46):
        a0 = r.uniform(-math.pi, math.pi); wd = r.uniform(.01, .05)
        rays += np.exp(-((np.angle(np.exp(1j * (ang - a0)))) / wd) ** 2) * r.uniform(.4, 1)
    heat = np.clip(np.exp(-(rr / 260) ** 1.2) * 1.3 + rays * np.exp(-(rr / 700)) * .5 + fbm(H, W, 8, seed, 4) * .25, 0, 1.4)
    img = ramp(np.clip(heat, 0, 1), ((0, (90, 20, 4)), (.3, (220, 80, 10)), (.55, (255, 160, 30)), (.8, (255, 230, 110)), (1, (255, 255, 235))))
    sp = np.zeros((H, W, 3), np.float32)
    for _ in range(4):
        streaks(r, sp, cx, cy, r.uniform(-math.pi, math.pi), 700, 300, 60, FIRE_COLS, (1, 3))
    img = img + sp * .7
    tm = tear_mask(r, H * .52, 50, .02, n=50, amp=12, spike=.45, spike_amp=3.5)
    img = img * (1 - tm[..., None])
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_boom.webp'), q=78)
    SA.put_lay('sd_boom', 390, 844)
    return 'sd_boom'


STREAMS3 = (                                                 # 第4.69版：寄った あとの 炎（上と 下から 光の 右で 1つに なる「＞」）
    (((-180, 300), (60, 380), (300, 640), (CXs + 130, CYs - 10)), 360, 120, 2800, 36),
    (((-180, 1440), (60, 1360), (300, 1090), (CXs + 130, CYs + 10)), 380, 120, 2800, -36),
    (((CXs + 60, CYs), (CXs + 120, CYs - 20), (CXs + 170, CYs - 10), (CXs + 220, CYs)), 160, 40, 500, 0))


def mirror_fire3(out):
    img = fire_stream(157, STREAMS3)
    SA.save(img, os.path.join(out, 'sd_w_fire3.webp'), q=80)
    SA.put_lay('sd_w_fire3', 390, 844)
    return 'sd_w_fire3'


def cut_invert_red(out, seed=191):
    """動画 4.75秒：黒い 地・赤く ぬった 大きな 穴・黒い かけら・右へ 炎（sd_c16r）"""
    W, H = W2, H2
    r = random.Random(seed)
    img = np.zeros((H, W, 3), np.float32) + hexc('#060203')
    pts = []
    for k in range(44):
        a = 2 * math.pi * k / 44
        rr = r.uniform(.8, 1.12)
        pts.append((W * .5 + math.cos(a) * W * .47 * rr, H * .5 + math.sin(a) * H * .2 * rr))
    hole = fillm(pts)
    red = ramp(fbm(H, W, 6, seed, 4), ((0, (150, 0, 8)), (.6, (225, 10, 20)), (1, (255, 60, 40))))
    img = img * (1 - hole[..., None]) + red * hole[..., None]
    fire = np.zeros((H, W, 3), np.float32)
    streaks(r, fire, W * .35, H * .5, math.radians(-12), 560, 160, 260, FIRE_COLS, (1, 3))
    img = img + fire * .9 + glow_of(fire, ((4, .6),))
    def how(r_, x, y):
        return dict(fill=(.02, .01, .015), outline=((.55, .05, .08), r_.randint(2, 4)), edge=0)
    sh, sa = shard_layer(seed, ((40, (-60, -60, W + 60, H * .32), (50, 140), how), (40, (-60, H * .68, W + 60, H + 60), (50, 140), how), (12, (-60, H * .3, W + 60, H * .7), (24, 70), how)))
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c16r.webp'), q=78)
    SA.put_lay('sd_c16r', 390, 844)
    return 'sd_c16r'


def cut_invert_blue(out, seed=193):
    """動画 4.78秒：白い 地・まん中の 帯に こい 青と 水色の かけらが ぎっしり・右に 炎（sd_c16b）"""
    W, H = W2, H2
    r = random.Random(seed)
    img = np.ones((H, W, 3), np.float32) * hexc('#F6FAFF')
    BL = ((.05, .2, .85), (.1, .45, 1.0), (.35, .75, 1.0), (.02, .1, .55))
    def how(r_, x, y):
        return dict(fill=BL[r_.randrange(len(BL))], outline=((.8, .95, 1), r_.randint(1, 3)), edge=0)
    sh, sa = shard_layer(seed, ((260, (-60, H * .3, W + 60, H * .7), (14, 60), how), (30, (-60, -60, W + 60, H + 60), (10, 40), how)))
    img = img * (1 - sa[..., None]) + sh * sa[..., None]
    fire = np.zeros((H, W, 3), np.float32)
    streaks(r, fire, W * .55, H * .5, math.radians(-8), 420, 120, 140, FIRE_COLS, (1, 3))
    img = img * (1 - np.clip(fire.max(-1), 0, 1)[..., None] * .7) + fire
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_c16b.webp'), q=78)
    SA.put_lay('sd_c16b', 390, 844)
    return 'sd_c16b'


def build(out, names=None):
    def face():
        import shiden_face
        return shiden_face.build(out, SA=SA)

    def hoof():
        import shiden_hoof
        return shiden_hoof.build_asset(out, SA=SA)
    todo = dict(sd_c0=lambda: cut_gray(out), sd_rbs=lambda: rainbow_bands(out), sd_c1=lambda: cut_glitch(out), sd_c2=lambda: cut_fire(out),
                sd_dk=lambda: cut_shadow(out), sd_bw=lambda: cut_bw(out), sd_rf=face, sd_chr=lambda: cut_chroma(out), sd_crk=lambda: cut_crack(out),
                sd_c5=lambda: cut_tear(out, 'red'), sd_boom=lambda: cut_boom(out), sd_c6=lambda: cut_tear(out, 'green'),
                sd_w_bg=lambda: mirror_world(out), sd_w_near=lambda: mirror_near(out), sd_w_fire=lambda: mirror_fire(out), sd_w_fire3=lambda: mirror_fire3(out),
                sd_w_prism=lambda: mirror_prism(out), sd_w_hoof=hoof,
                sd_c16=lambda: cut_invert(out), sd_c16r=lambda: cut_invert_red(out), sd_c16b=lambda: cut_invert_blue(out), sd_c17=lambda: cut_hole(out),
                sd_c18=lambda: cut_dark(out), sd_c19=lambda: cut_ring(out), sd_pillar=lambda: pillar(out))
    made = []
    for k, fn in todo.items():
        if names and k not in names:
            continue
        r = fn()
        made += r if isinstance(r, list) else [r]
        print('made', r, flush=True)
    return made
