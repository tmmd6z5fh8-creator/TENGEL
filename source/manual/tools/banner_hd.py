"""説明書の上の絵（テンゲルの バナー）を 描き直す（第4.59版・2026-10-25・まさちゃんの指定）
   元の 絵（manual/tools/banner_src.jpg：1408×768・まさちゃんの バナー）の 右の 文字の 所（TENGER・説明の 行・「テンゲル」の 金の 札）を、
   **元の 絵の 字体・輝き・位置に 合わせて** 3倍の 解像度で 描き直す（まさちゃん「字体と輝き、文字の位置が大分違うからこの画像に合わせて！」）。
   - TENGER：Montserrat（太さ 650）を 1字ずつ 元の 字の 幅と 高さ（元の 絵から 測った 値 LETTERS）に 合わせて 置く。
             面の 色は 元の 字を 縦に 測った 金（GOLD_STOPS：上は 金・2割の 所から まん中まで 明るい クリーム金・7〜8割は こい 金・いちばん下は また 明るい）。
             **立体**（まさちゃん「三枚目のように文字に立体感出して」＝元の 絵と 同じ 面取り）：字の ふち 2px を 面取り（上向きの へりは 明るい クリーム・
             下向きの へりは こげ茶・横の へりは 上が こく 下が 明るい 金）・面取りと 面の さかいに 細い こい 線。
             字の まわりに **背景と 同じ 色の 線**（STROKE：元の 絵と 同じ、背景より 少し こい 紺緑の 1.5px。まさちゃん「テンゲル背景の色と同じ線を立体的な文字の枠に入れて」）、
             上に うすい 明るい 光（GLOW）、右下に やわらかい 影。
   - 説明の 行：Noto Sans JP（太さ 600）・白・やわらかい 影。文は「独自の統計・オッズ分析による競馬検討支援システム」（「馬券」→「競馬」：まさちゃん「2にして！」）
   - 「テンゲル」の 札：角を 落とした 金の 札（横に 明るさが かわる：ふちは こい 金・まん中は 明るい 金・下の へりは こい）・字は Noto Sans JP（太さ 750）の 紺
   - 「バージョン …」の 行は 入れない。左の エンブレムは 元の 絵の まま（大きくして 少し くっきり）
   - **的中ボタンの 面（push）だけ 文字の 高さを 左の エンブレムに 合わせる**（まさちゃん「テンゲルpushボタンだけは、左のテンゲルアイコンに文字の高さ合わせて！」）：
     TENGER の 上を 盾の 上（y 172）に、PUSH（gen_fx.py の tg_face_svg が SVG で 書く）の 下を 盾の 下の とがり（y 543）に。行の あきは 元の 絵の 割合の まま（PUSH_LAYOUT）
   できる もの：
     manual/img/banner.webp            2400×1310（説明書の 上の絵：Web版・App Store版の 説明書）
     ios/kisekae_blobs/<banner>.webp   2340×960（マスター帯の 壁紙の 上の絵：kisekae/tengel_blobs.json の banner・リポジトリには 入れない）
     ios/kisekae_blobs/<push>.webp     1800×982（マスター帯の 的中ボタンの 面：tengel_blobs.json の push。文字は PUSH_LAYOUT の 位置）
   python3 manual/tools/banner_hd.py [元の絵] [--no-blobs] [--preview]
   字：Montserrat・Noto Sans JP（どちらも OFL。google/fonts の ofl/montserrat・ofl/notosansjp。MONTSERRAT／NOTOSANSJP で 場所を 指定できる）"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
S = 3                                            # 描く 倍率（1408×768 → 4224×2304）
SW, SH = 1408, 768                               # 元の 絵の 大きさ
FONT_MONT = os.environ.get('MONTSERRAT', '/home/claude/google/fonts/ofl/montserrat/Montserrat[wght].ttf')
FONT_NOTO = os.environ.get('NOTOSANSJP', '/home/claude/google/fonts/ofl/notosansjp/NotoSansJP[wght].ttf')
TAGLINE = '独自の統計・オッズ分析による競馬検討支援システム'
# 元の 絵（1408×768）から 測った 置き場所（ピクセル）
LETTERS = [('T', 624, 715), ('E', 731, 815), ('N', 833, 923), ('G', 939, 1033), ('E', 1051, 1136), ('R', 1153, 1243)]   # 字と 左右
CAP = (270, 356)                                 # TENGER の 字の 上と 下
TAG = (641, 388, 1243, 413)                      # 説明の 行（白）の 箱
PLATE = (634, 430, 1251, 504)                    # 「テンゲル」の 金の 札
CHAMFER = 14                                     # 札の 角の 落とし
PTEXT = (829, 440, 1054, 491)                    # 札の 字「テンゲル」の 箱
CLEAR = (606, 246, 1290, 556)                    # 文字を 消す 所（左の エンブレムには かからない）
NAVY = (19, 45, 52)                              # 札の 字の 色（RGB）
# 的中ボタンの 面だけ：文字の 高さを 左の エンブレム（盾：上 y≈170・下の とがり y≈545）に 合わせる。
# TENGER の 上＝172・PUSH の 下＝543（PUSH は gen_fx.py の tg_face_svg が 書く：ボタンの 座標で 字の 下の 線 115.7・大きさ 27＝元の 絵の 449〜543）。
# 行の あき（35・18・39）は 元の 絵の 割合（32・17・36）の まま
PUSH_LAYOUT = dict(cap=(172, 258), tag=(293, 318), plate=(336, 410))
# TENGER の 金：面の 色（字の 上 0 → 下 1。元の 字の 面を 行ごとに 測った 値）
GOLD_STOPS = [(0.00, (214, 192, 134)), (0.06, (222, 200, 138)), (0.19, (248, 231, 175)), (0.36, (247, 238, 188)), (0.49, (241, 231, 172)),
              (0.56, (220, 196, 135)), (0.62, (181, 153, 103)), (0.70, (150, 116, 60)), (0.81, (134, 101, 50)), (0.90, (165, 130, 74)),
              (0.97, (204, 173, 116)), (1.00, (222, 190, 138))]
# 面取り（元の 絵から 測った 値）
BEVEL = 2.8                                      # 面取りの はば（元の 絵の px）
RIM_TOP = [(0.0, (240, 250, 214)), (1.0, (236, 232, 186))]      # 上向きの へり：明るい クリーム（下の 行ほど 少し おさえる）
RIM_SIDE = [(0.0, (118, 110, 74)), (1.0, (228, 208, 158))]      # 横の へり：上は こく・下は 明るい（面と 逆）
RIM_BOT = (94, 73, 34)                                           # 下向きの へり：こげ茶
STROKE = 1.8                                     # 字の まわりの 線の はば（元の 絵の px）
STROKE_COL = (20, 38, 34)                        # 線の 色：背景（紺緑）と 同じ 系統で 少し こい（元の 絵から 測った 値）
GLOW_COL = (96, 150, 160)                        # 上の 明るい 帯と まわりの 輪の 色（元の 絵の 字の 上の 明るい 帯から）
GLOW_W = 1.2                                     # まわりの 明るい 輪の はば（元の 絵の px）


def grad(stops, t):
    """t（0〜1・配列）→ 色（float 0〜1・…×3）"""
    out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = np.clip((t[m] - t0) / max(1e-6, t1 - t0), 0, 1)[:, None]
        out[m] = (np.array(c0, np.float32) * (1 - k) + np.array(c1, np.float32) * k) / 255.0
    return out


def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def glyph_mask(text, f):
    """字の マスク（PIL の L）。字の ふち ぴったりに 切る"""
    x0, y0, x1, y1 = f.getbbox(text)
    pad = 20
    im = Image.new('L', (x1 - x0 + pad * 2, y1 - y0 + pad * 2), 0)
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=f, fill=255)
    return im.crop(im.getbbox())


def paste(canvas, rgb, alpha, x, y):
    h, w = alpha.shape
    H, W = canvas.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    c = rgb[y0 - y:y1 - y, x0 - x:x1 - x] if rgb.ndim == 3 else rgb
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + c * a


def shifted(alpha, dx, dy, blur):
    """alpha を (dx, dy) ずらして ぼかした もの（大きさは pad ぶん 広がる）→ (配列, pad)"""
    pad = int(blur * 3 + max(abs(dx), abs(dy)) + 2)
    big = np.zeros((alpha.shape[0] + pad * 2, alpha.shape[1] + pad * 2), np.float32)
    big[pad + dy:pad + dy + alpha.shape[0], pad + dx:pad + dx + alpha.shape[1]] = alpha
    if blur > 0:
        big = cv2.GaussianBlur(big, (0, 0), blur)
    return big, pad


def soft_shadow(canvas, alpha, x, y, dy, blur, strength, dx=0):
    """alpha の 形の 影（黒）を (x+dx, y+dy) に"""
    big, pad = shifted(alpha, dx, dy, blur)
    paste(canvas, np.zeros(3, np.float32), big * strength, x - pad, y - pad)


def gold_letter(mask):
    """TENGER の 1字：マスク（0〜1）→ 色（float）。面は 縦の 金の グラデーション（GOLD_STOPS）。
       ふち BEVEL px は 面取り：へりの 向き（上・横・下）で 色を 変える（元の 絵と 同じ：上は 明るい クリーム・下は こげ茶・横は 上が こく 下が 明るい）。
       面取りと 面の さかいに 細い こい 線"""
    h, w = mask.shape
    t = np.linspace(0, 1, h)[:, None].repeat(w, 1)
    face = grad(GOLD_STOPS, t)
    P = int(BEVEL * S + 6)                                                    # マスクは 字の ふち ぴったりなので、外に 0 を 足してから 距離と 法線を とる
    mp = np.pad(mask, P)
    m8 = (mp > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(m8, cv2.DIST_L2, 5)[P:-P, P:-P]              # ふちからの 距離（字の 中）
    B = BEVEL * S
    rim = np.clip((B - dist) / (0.6 * S), 0, 1) * (mask > 0.5)                # 面取り（ふちで 1 → B で 0）
    line = np.clip(1 - np.abs(dist - B - 0.3 * S) / (0.7 * S), 0, 1) * (mask > 0.5)   # さかいの 細い 線
    bm = cv2.GaussianBlur(mp, (0, 0), 1.0 * S)
    gx = cv2.Sobel(bm, cv2.CV_32F, 1, 0, ksize=3)[P:-P, P:-P]
    gy = cv2.Sobel(bm, cv2.CV_32F, 0, 1, ksize=3)[P:-P, P:-P]
    n = np.sqrt(gx * gx + gy * gy) + 1e-6
    ny = -gy / n                                                              # 外向きの 法線の 縦（上向き ＝ −1）
    w_top = np.clip(-ny, 0, 1) ** 1.4
    w_bot = np.clip(ny, 0, 1) ** 1.4
    w_side = np.clip(1 - w_top - w_bot, 0, 1)
    rimc = grad(RIM_TOP, t) * w_top[..., None] + grad(RIM_SIDE, t) * w_side[..., None] + np.array(RIM_BOT, np.float32) / 255.0 * w_bot[..., None]
    col = face * (1 - rim[..., None]) + rimc * rim[..., None]
    col = col * (1 - line[..., None] * 0.20)
    return np.clip(col, 0, 1)


def clean_background(src):
    """元の 絵の 右の 文字を 消して 3倍に（RGB float）"""
    base = cv2.imread(src, cv2.IMREAD_COLOR)
    assert base is not None and base.shape[:2] == (SH, SW), (src, None if base is None else base.shape)
    # 文字の 所（CLEAR の 四角）を、四角の ふちの 色から なめらかに 埋める（上下左右の ふちを 結ぶ：背景は なめらかな グラデーションなので 自然に つながる。
    # 古い 文字の 影や 札の あとも 残らない：的中ボタンの 面では 文字を 上に ずらすので、ここが 見える）
    x0, y0, x1, y1 = CLEAR
    b = base.astype(np.float32)
    sm1 = lambda v: cv2.GaussianBlur(v.reshape(-1, 1, 3), (0, 0), 3).reshape(-1, 3)
    top, bot = sm1(b[y0 - 2, x0:x1]), sm1(b[y1 + 1, x0:x1])
    left, right = sm1(b[y0:y1, x0 - 2]), sm1(b[y0:y1, x1 + 1])
    h, w = y1 - y0, x1 - x0
    u = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    v = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    H = (1 - u) * left[:, None, :] + u * right[:, None, :]
    V = (1 - v) * top[None, :, :] + v * bot[None, :, :]
    C = ((1 - u) * (1 - v) * top[0] + u * (1 - v) * top[-1] + (1 - u) * v * bot[0] + u * v * bot[-1])
    fill = H + V - C
    fm = np.zeros((SH, SW), np.float32); fm[y0 + 3:y1 - 3, x0 + 3:x1 - 3] = 1
    fm = cv2.GaussianBlur(fm, (0, 0), 2)[..., None]
    full = np.zeros_like(b); full[y0:y1, x0:x1] = fill
    clean = np.clip(b * (1 - fm) + full * fm, 0, 255).astype(np.uint8)
    big = cv2.resize(clean, (SW * S, SH * S), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(big, (0, 0), 2.0)
    big = cv2.addWeighted(big, 1.28, blur, -0.28, 0)
    return big[..., ::-1].astype(np.float32) / 255.0


def draw_text(canvas, cap=CAP, tag_y=TAG[1:4:2], plate_y=PLATE[1:4:2]):
    """右の 文字を 描く（TENGER・説明の 行・「テンゲル」の 札）。縦の 位置は cap／tag_y／plate_y（元の 絵の px・ふつうは 元の 位置）"""
    canvas = canvas.copy()
    # 1) TENGER：1字ずつ 元の 位置と 大きさに（Montserrat 650）。右下に 影 → 上に うすい 光 → 背景の 色の 線 → 面取りした 金の 字
    fm = font(FONT_MONT, 120 * S, 650)
    cy0, cy1 = cap[0] * S, cap[1] * S
    hh = cy1 - cy0
    letters = []
    for ch, lx0, lx1 in LETTERS:
        gm = glyph_mask(ch, fm).resize(((lx1 - lx0 + 1) * S, hh), Image.LANCZOS)
        letters.append((lx0 * S, np.asarray(gm).astype(np.float32) / 255.0))
    allm = np.zeros((hh, (LETTERS[-1][2] - LETTERS[0][1] + 1) * S), np.float32)
    for lx, a in letters:
        ox = lx - LETTERS[0][1] * S
        allm[:, ox:ox + a.shape[1]] = np.maximum(allm[:, ox:ox + a.shape[1]], a)
    ax, ay = LETTERS[0][1] * S, cy0
    soft_shadow(canvas, allm, ax, ay, dx=int(2.5 * S), dy=int(3.5 * S), blur=2.5 * S, strength=0.62)     # 右下の やわらかい 影
    k = int(round(STROKE * S))
    k2 = k + int(round(GLOW_W * S))
    m8 = (allm > 0.5).astype(np.uint8)
    big = np.zeros((hh + 2 * k2, allm.shape[1] + 2 * k2), np.uint8); big[k2:-k2, k2:-k2] = m8
    ell = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    d1 = cv2.dilate(big, ell(k)).astype(np.float32)                                                        # 線の 外がわ
    d2 = cv2.dilate(big, ell(k2)).astype(np.float32)                                                       # その 外の 明るい 輪
    ring = cv2.GaussianBlur(np.clip(d2 - d1, 0, 1), (0, 0), 0.6 * S) * 0.42
    paste(canvas, np.array(GLOW_COL, np.float32) / 255.0, ring, ax - k2, ay - k2)                           # 字の まわりの うすい 明るい 輪（元の 絵）
    glow, pad = shifted(allm, 0, -int(2.0 * S), 1.1 * S)                                                   # 上の 明るい 帯（元の 絵の 字の 上の 光）
    paste(canvas, np.array(GLOW_COL, np.float32) / 255.0, np.clip(glow * 1.3, 0, 1) * 0.9, ax - pad, ay - pad)
    stroke = d1[k2 - k:-(k2 - k), k2 - k:-(k2 - k)].copy()
    stroke[k:-k, k:-k] = np.clip(stroke[k:-k, k:-k] - allm, 0, 1)
    stroke = cv2.GaussianBlur(stroke, (0, 0), 0.5)
    paste(canvas, np.array(STROKE_COL, np.float32) / 255.0, stroke, ax - k, ay - k)                          # 背景の 色の 線（元の 絵と 同じ）
    for lx, a in letters:
        paste(canvas, gold_letter(a), a, lx, cy0)
    # 2) 説明の 行（Noto Sans JP 600・白・影）
    tx0, tx1 = TAG[0], TAG[2]
    ty0, ty1 = tag_y
    f = font(FONT_NOTO, 40 * S, 600)
    tm0 = glyph_mask(TAGLINE, f).resize(((tx1 - tx0 + 1) * S, (ty1 - ty0 + 1) * S), Image.LANCZOS)   # 元の 行の 箱（字の ふち）に ぴったり
    ta = np.zeros((SH * S, SW * S), np.float32)
    ta[ty0 * S:ty0 * S + tm0.height, tx0 * S:tx0 * S + tm0.width] = np.asarray(tm0).astype(np.float32) / 255.0
    sh = cv2.GaussianBlur(np.roll(ta, 2 * S, axis=0), (0, 0), 2.5 * S) * 0.75
    canvas = canvas * (1 - sh[..., None])
    canvas = canvas * (1 - ta[..., None]) + np.array([238, 241, 241], np.float32) / 255.0 * ta[..., None]
    # 3) 「テンゲル」の 金の 札（角を 落とした 形・横の グラデーション＋上が 明るく 下が こい・ふちの 帯と 内がわの 明るい 線＝元の 札の 額ぶち）
    px0, px1 = PLATE[0], PLATE[2]
    py0, py1 = plate_y
    pw, ph = (px1 - px0 + 1) * S, (py1 - py0 + 1) * S
    c = CHAMFER * S

    def octa(d):
        """札の 八角形を d だけ 内がわに"""
        cc = max(0.0, c - 0.586 * d)
        return [(d + cc, d), (pw - 1 - d - cc, d), (pw - 1 - d, d + cc), (pw - 1 - d, ph - 1 - d - cc), (pw - 1 - d - cc, ph - 1 - d), (d + cc, ph - 1 - d), (d, ph - 1 - d - cc), (d, d + cc)]

    def poly_mask(pts, outline_w=None):
        im = Image.new('L', (pw, ph), 0)
        if outline_w:
            ImageDraw.Draw(im).polygon(pts, outline=255, width=int(round(outline_w)))
        else:
            ImageDraw.Draw(im).polygon(pts, fill=255)
        return np.asarray(im).astype(np.float32) / 255.0

    pm = poly_mask(octa(0))
    soft_shadow(canvas, pm, px0 * S, py0 * S, dy=4 * S, blur=5 * S, strength=0.6)
    u = np.linspace(0, 1, pw)[None, :].repeat(ph, 0)
    v = np.linspace(0, 1, ph)[:, None].repeat(pw, 1)
    side = grad([(0.0, (188, 152, 90)), (0.22, (216, 184, 118)), (0.5, (254, 242, 182)), (0.78, (218, 186, 120)), (1.0, (188, 152, 90))], u)
    vert = 1.0 - np.clip((v - 0.30) / 0.70, 0, 1) * 0.30                         # 上が 明るく 下が こい
    pc = np.clip(side * vert[..., None], 0, 1)
    band = pm - poly_mask(octa(4.0 * S))                                           # ふちの 帯（4px）：少し こい
    pc = pc * (1 - np.clip(band, 0, 1)[..., None] * 0.22)
    line = poly_mask(octa(4.6 * S), outline_w=1.4 * S)                             # 内がわの 明るい 線（額ぶち）
    pc = pc * (1 - line[..., None] * 0.9) + np.array([255, 247, 205], np.float32) / 255.0 * line[..., None] * 0.9
    edge = poly_mask(octa(0), outline_w=1.0 * S)                                   # 外の ふち：こい
    pc = pc * (1 - edge[..., None] * 0.45)
    paste(canvas, pc, pm, px0 * S, py0 * S)
    qx0, qx1 = PTEXT[0], PTEXT[2]                                                 # 札の 字「テンゲル」（Noto Sans JP 750・紺）：札の 中の 位置は 元の まま
    qy0, qy1 = py0 + (PTEXT[1] - PLATE[1]), py1 - (PLATE[3] - PTEXT[3])
    f9 = font(FONT_NOTO, 60 * S, 750)
    tm = glyph_mask('テンゲル', f9).resize(((qx1 - qx0 + 1) * S, (qy1 - qy0 + 1) * S), Image.LANCZOS)
    ta2 = np.asarray(tm).astype(np.float32) / 255.0
    soft_shadow(canvas, ta2, qx0 * S, qy0 * S, dy=1 * S, blur=1 * S, strength=0.25)
    paste(canvas, np.array(NAVY, np.float32) / 255.0, ta2, qx0 * S, qy0 * S)
    return np.clip(canvas, 0, 1)


def build(src, layout=None):
    """元の 絵 → 描き直した 絵（RGB float・SW*S×SH*S）。layout＝PUSH_LAYOUT で 的中ボタンの 面（文字の 高さを エンブレムに 合わせる）"""
    bg = clean_background(src)
    if layout:
        return draw_text(bg, cap=layout['cap'], tag_y=layout['tag'], plate_y=layout['plate'])
    return draw_text(bg)


def save_webp(rgb, path, size, q):
    im = cv2.resize((rgb[..., ::-1] * 255).round().astype(np.uint8), size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, im, [cv2.IMWRITE_WEBP_QUALITY, q])
    print(path, size, f'{os.path.getsize(path) / 1e3:.0f}KB')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src = args[0] if args else os.path.join(HERE, 'banner_src.jpg')   # 元の 絵（1408×768・文字は 前の まま）
    bg = clean_background(src)
    canvas = draw_text(bg)
    out_dir = os.path.join(SRC_DIR, 'manual', 'img')
    if '--preview' in sys.argv:
        save_webp(canvas, os.path.join(out_dir, 'banner_preview.webp'), (SW * S, SH * S), 90)
    else:
        save_webp(canvas, os.path.join(out_dir, 'banner.webp'), (2400, 1310), 82)
    if '--no-blobs' not in sys.argv:
        sys.path.insert(0, os.path.join(SRC_DIR, 'kisekae', 'flat'))
        import tengel_banner as TB
        ids = json.load(open(os.path.join(SRC_DIR, 'kisekae', 'tengel_blobs.json')))
        bl = os.path.join(SRC_DIR, 'ios', 'kisekae_blobs'); os.makedirs(bl, exist_ok=True)
        k = SW / 1200.0                                                     # 1200×655 の 座標（tengel_banner.CROP）→ 1408×768
        cx0, cy0, cx1, cy1 = (int(round(v * k * S)) for v in TB.CROP)
        save_webp(canvas[cy0:cy1, cx0:cx1], os.path.join(bl, ids['banner'] + '.webp'), (TB.W * 3, TB.Hh * 3), 85)
        push = draw_text(bg, cap=PUSH_LAYOUT['cap'], tag_y=PUSH_LAYOUT['tag'], plate_y=PUSH_LAYOUT['plate'])   # 的中ボタンの 面：文字の 高さを エンブレムに
        save_webp(push, os.path.join(bl, ids['push'] + '.webp'), (1800, 982), 88)
        if '--preview' in sys.argv:
            save_webp(push, os.path.join(out_dir, 'push_preview.webp'), (SW * S, SH * S), 90)
