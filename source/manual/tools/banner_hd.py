"""説明書の上の絵（テンゲルの バナー）を 描き直す（第4.59版・2026-10-25・まさちゃんの指定）
   元の 絵（manual/tools/banner_src.jpg：1408×768・まさちゃんの バナー）の 右の 文字の 所（TENGER・説明の 行・「テンゲル」の 金の 札）を、
   **元の 絵の 字体・輝き・位置に 合わせて** 3倍の 解像度で 描き直す（まさちゃん「字体と輝き、文字の位置が大分違うからこの画像に合わせて！」）。
   - TENGER：Montserrat（太さ 650）を 1字ずつ 元の 字の 幅と 高さ（元の 絵から 測った 値 LETTERS）に 合わせて 置く。
             色は 元の 字の 縦の 色の 変化（上半分 明るい クリーム金・下半分 こい 金・いちばん下に 明るい へり）＝GOLD_STOPS。うすい 立体（下に 押し出し）と 影
   - 説明の 行：Noto Sans JP（太さ 600）・白・やわらかい 影。文は「独自の統計・オッズ分析による競馬検討支援システム」（「馬券」→「競馬」：まさちゃん「2にして！」）
   - 「テンゲル」の 札：角を 落とした 金の 札（横に 明るさが かわる：ふちは こい 金・まん中は 明るい 金・下の へりは こい）・字は Noto Sans JP（太さ 750）の 紺
   - 「バージョン …」の 行は 入れない。左の エンブレムは 元の 絵の まま（大きくして 少し くっきり）
   できる もの：
     manual/img/banner.webp            2400×1310（説明書の 上の絵：Web版・App Store版の 説明書）
     ios/kisekae_blobs/<banner>.webp   2340×960（マスター帯の 壁紙の 上の絵：kisekae/tengel_blobs.json の banner・リポジトリには 入れない）
     ios/kisekae_blobs/<push>.webp     1800×982（マスター帯の 的中ボタンの 面：tengel_blobs.json の push）
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
CAP = (270, 356)                                 # TENGER の 字の 上と 下（押し出しは 含まない）
EXTRUDE = 4                                      # 字の 下の 押し出し（px）
TAG = (641, 388, 1243, 413)                      # 説明の 行（白）の 箱
PLATE = (634, 430, 1251, 504)                    # 「テンゲル」の 金の 札
CHAMFER = 14                                     # 札の 角の 落とし
PTEXT = (829, 440, 1054, 491)                    # 札の 字「テンゲル」の 箱
CLEAR = (606, 246, 1290, 556)                    # 文字を 消す 所（左の エンブレムには かからない）
NAVY = (19, 45, 52)                              # 札の 字の 色（RGB）
# TENGER の 金：字の 上（0）から 下（1）への 色（元の 字を 行ごとに 測った 値から）
GOLD_STOPS = [(0.00, (247, 241, 200)), (0.08, (228, 208, 150)), (0.20, (236, 221, 170)), (0.34, (246, 238, 196)), (0.44, (240, 229, 182)),
              (0.50, (214, 188, 128)), (0.58, (176, 144, 86)), (0.70, (160, 129, 74)), (0.86, (170, 139, 82)), (0.95, (192, 160, 100)), (1.00, (208, 178, 120))]


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


def soft_shadow(canvas, alpha, x, y, dy, blur, strength):
    """alpha の 形の 影（黒）を y+dy に"""
    pad = blur * 3 + abs(dy)
    big = np.zeros((alpha.shape[0] + pad * 2, alpha.shape[1] + pad * 2), np.float32)
    big[pad + dy:pad + dy + alpha.shape[0], pad:pad + alpha.shape[1]] = alpha
    big = cv2.GaussianBlur(big, (0, 0), blur) * strength
    paste(canvas, np.zeros(3, np.float32), big, x - pad, y - pad)


def gold_letter(mask):
    """TENGER の 1字：マスク（0〜1）→ 色（float）。上半分 明るい・下半分 こい・ふちの 細い ハイライトと 線"""
    h, w = mask.shape
    t = np.linspace(0, 1, h)[:, None].repeat(w, 1)
    col = grad(GOLD_STOPS, t)
    m8 = (mask > 0.5).astype(np.uint8)
    k = np.ones((3, 3), np.uint8)
    inner = cv2.erode(m8, k, iterations=max(1, S // 2))
    edge = (m8 - inner).astype(np.float32)
    up = np.zeros_like(mask); up[1 * S:, :] = mask[:-1 * S, :]              # 下へ ずらした 形
    top_edge = np.clip(mask - up, 0, 1) * edge                                # 上の ふち
    col = col * (1 - edge[..., None] * 0.22) + np.array([1.0, 0.98, 0.9], np.float32) * (top_edge * 0.85)[..., None]
    return np.clip(col, 0, 1)


def build(src):
    base = cv2.imread(src, cv2.IMREAD_COLOR)
    assert base is not None and base.shape[:2] == (SH, SW), (src, None if base is None else base.shape)
    # 1) 右の 文字を 消す（明るい 所を マスクに して 塗り直す）→ 3倍に 大きく（少し くっきり）
    g = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    x0, y0, x1, y1 = CLEAR
    m = np.zeros(g.shape, np.uint8)
    m[y0:y1, x0:x1] = (g[y0:y1, x0:x1] > 55).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    clean = cv2.inpaint(base, m, 7, cv2.INPAINT_TELEA)
    big = cv2.resize(clean, (SW * S, SH * S), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(big, (0, 0), 2.0)
    big = cv2.addWeighted(big, 1.28, blur, -0.28, 0)
    sm = cv2.GaussianBlur(big, (0, 0), 7)
    mm = cv2.resize(m, (SW * S, SH * S), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    mm = cv2.GaussianBlur(mm, (0, 0), 10)[..., None]
    big = (big * (1 - mm) + sm * mm).astype(np.uint8)
    canvas = big[..., ::-1].astype(np.float32) / 255.0            # RGB float
    # 2) TENGER：1字ずつ 元の 位置と 大きさに（Montserrat 700）。押し出し（下に EXTRUDE）と 影
    fm = font(FONT_MONT, 120 * S, 650)
    cy0, cy1 = CAP[0] * S, CAP[1] * S
    hh = cy1 - cy0
    letters = []
    for ch, lx0, lx1 in LETTERS:
        gm = glyph_mask(ch, fm).resize(((lx1 - lx0 + 1) * S, hh), Image.LANCZOS)
        letters.append((lx0 * S, np.asarray(gm).astype(np.float32) / 255.0))
    allm = np.zeros((hh + EXTRUDE * S, (LETTERS[-1][2] - LETTERS[0][1] + 1) * S), np.float32)
    for lx, a in letters:
        ox = lx - LETTERS[0][1] * S
        allm[:hh, ox:ox + a.shape[1]] = np.maximum(allm[:hh, ox:ox + a.shape[1]], a)
    soft_shadow(canvas, allm, LETTERS[0][1] * S, cy0, dy=5 * S, blur=4 * S, strength=0.55)
    for lx, a in letters:
        for i in range(EXTRUDE * S, 0, -1):                       # 押し出し：下へ EXTRUDE px（こい 金 → 下の へりは 明るい）
            k = i / float(EXTRUDE * S)
            c = np.array([60, 52, 36], np.float32) / 255.0 * (1 - k) + np.array([150, 122, 74], np.float32) / 255.0 * k
            paste(canvas, c, a * 0.9, lx, cy0 + i)
        m8 = (a > 0.5).astype(np.uint8)
        outline = (cv2.dilate(m8, np.ones((3, 3), np.uint8), iterations=max(1, S // 2)) - m8).astype(np.float32)
        paste(canvas, np.array([14, 34, 46], np.float32) / 255.0, outline * 0.85, lx, cy0)   # 元の 絵と 同じ、こい 紺の 細い ふち
        paste(canvas, gold_letter(a), a, lx, cy0)
    # 3) 説明の 行（Noto Sans JP 700・白・影）
    tx0, ty0, tx1, ty1 = TAG
    f = font(FONT_NOTO, 40 * S, 600)
    tm0 = glyph_mask(TAGLINE, f).resize(((tx1 - tx0 + 1) * S, (ty1 - ty0 + 1) * S), Image.LANCZOS)   # 元の 行の 箱（字の ふち）に ぴったり
    ta = np.zeros((SH * S, SW * S), np.float32)
    ta[ty0 * S:ty0 * S + tm0.height, tx0 * S:tx0 * S + tm0.width] = np.asarray(tm0).astype(np.float32) / 255.0
    sh = cv2.GaussianBlur(np.roll(ta, 2 * S, axis=0), (0, 0), 2.5 * S) * 0.75
    canvas = canvas * (1 - sh[..., None])
    canvas = canvas * (1 - ta[..., None]) + np.array([238, 241, 241], np.float32) / 255.0 * ta[..., None]
    # 4) 「テンゲル」の 金の 札（角を 落とした 形・横の グラデーション＋上が 明るく 下が こい・ふちの 帯と 内がわの 明るい 線＝元の 札の 額ぶち）
    px0, py0, px1, py1 = PLATE
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
    qx0, qy0, qx1, qy1 = PTEXT                                                   # 札の 字「テンゲル」（Noto Sans JP 900・紺）
    f9 = font(FONT_NOTO, 60 * S, 750)
    tm = glyph_mask('テンゲル', f9).resize(((qx1 - qx0 + 1) * S, (qy1 - qy0 + 1) * S), Image.LANCZOS)
    ta2 = np.asarray(tm).astype(np.float32) / 255.0
    soft_shadow(canvas, ta2, qx0 * S, qy0 * S, dy=1 * S, blur=1 * S, strength=0.25)
    paste(canvas, np.array(NAVY, np.float32) / 255.0, ta2, qx0 * S, qy0 * S)
    return np.clip(canvas, 0, 1)


def save_webp(rgb, path, size, q):
    im = cv2.resize((rgb[..., ::-1] * 255).round().astype(np.uint8), size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, im, [cv2.IMWRITE_WEBP_QUALITY, q])
    print(path, size, f'{os.path.getsize(path) / 1e3:.0f}KB')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src = args[0] if args else os.path.join(HERE, 'banner_src.jpg')   # 元の 絵（1408×768・文字は 前の まま）
    canvas = build(src)
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
        save_webp(canvas, os.path.join(bl, ids['push'] + '.webp'), (1800, 982), 88)
