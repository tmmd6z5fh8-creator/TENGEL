"""説明書の上の絵（テンゲルの バナー）を 描き直す（第4.59版・2026-10-25・まさちゃんの指定）
   - 右がわの 文字の 所（TENGER・説明の 行・「テンゲル」の 金の 札）を 大きい 解像度で 描き直す（iPad で 画面いっぱいに 出しても ぼけない）
   - 説明の 行は「独自の統計・オッズ分析による競馬検討支援システム」（「馬券」→「競馬」：まさちゃん「2にして！」）
   - 「バージョン …」の 行は 入れない。左の エンブレム（盾・騎手・馬）は 元の 絵の まま（大きくして 少し くっきり）
   できる もの（src の 1200×655 を 3倍の 3600×1965 で 描いて から）：
     manual/img/banner.webp        2400×1310（説明書の 上の絵：Web版・App Store版の 説明書。前は 1200×655）
     ios/kisekae_blobs/<banner>.webp  2340×960（マスター帯の 壁紙の 上の絵：kisekae/tengel_blobs.json の banner。前は 780×320。リポジトリには 入れない）
     ios/kisekae_blobs/<push>.webp    1800×982（マスター帯の 的中ボタンの 面：tengel_blobs.json の push。前は 900×491）
   python3 manual/tools/banner_hd.py [元の絵（1200×655・なければ manual/tools/banner_src.webp）] [--no-blobs] [--preview]
   字：TENGER と「テンゲル」は Dela Gothic One（アプリの ロゴの 字）・説明の 行は M PLUS 1（太さ 800）。どちらも OFL。"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
S = 3                                            # 描く 倍率（1200×655 → 3600×1965）
FONT_DELA = os.path.join(SRC_DIR, 'ios', 'fonts', 'DelaGothicOne-Regular.ttf')
FONT_MPLUS = os.environ.get('MPLUS1', '/home/claude/google/fonts/ofl/mplus1/MPLUS1[wght].ttf')
TAGLINE = '独自の統計・オッズ分析による競馬検討支援システム'
# 元の 絵（1200×655）での 置き場所（ピクセル）：flat/tengel_banner.py の CROP・VER と 同じ 座標系
TENGER = (532, 230, 1059, 311)                   # TENGER の 字（金）の 箱
TAG = (546, 331, 1059, 352)                      # 説明の 行（白）の 箱
PLATE = (540, 367, 1066, 437)                    # 「テンゲル」の 金の 札
CLEAR = (518, 212, 1092, 472)                    # 文字を 消す 所（左の エンブレムには かからない）
NAVY = (16, 40, 58)                              # 札の 字の 色（RGB）


def rr_mask(w, h, r):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return np.asarray(m).astype(np.float32) / 255.0


def gold_shade(mask, bevel, top=(252, 236, 176), mid=(228, 184, 74), bottom=(150, 102, 26), light=(-0.55, -0.8)):
    """字や 札の マスク（0〜1・h×w）から 金の 面（RGB float 0〜1）と アルファを 作る。
       面は 上が 明るく 下が こい 金の グラデーション。ふちは bevel（px）の はばで もり上がる（距離変換で 高さ → 法線 → 左上からの 光）"""
    h, w = mask.shape
    m8 = (mask > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(m8, cv2.DIST_L2, 5)
    hgt = np.clip(dist / float(bevel), 0, 1)
    hgt = np.sin(hgt * np.pi / 2)                                       # まるい もり上がり
    hgt = cv2.GaussianBlur(hgt, (0, 0), max(1.0, bevel / 6.0))          # 距離変換の 段を ならす（しま模様を 出さない）
    gy, gx = np.gradient(hgt)
    nx, ny = -gx * bevel * 1.6, -gy * bevel * 1.6
    nz = np.ones_like(nx)
    n = np.sqrt(nx * nx + ny * ny + nz * nz); nx, ny, nz = nx / n, ny / n, nz / n
    lx, ly = light; lz = 1.0
    ln = np.sqrt(lx * lx + ly * ly + lz * lz); lx, ly, lz = lx / ln, ly / ln, lz / ln
    diff = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    hx, hy, hz = lx, ly, lz + 1.0
    hn = np.sqrt(hx * hx + hy * hy + hz * hz); hx, hy, hz = hx / hn, hy / hn, hz / hn
    spec = np.clip(nx * hx + ny * hy + nz * hz, 0, 1) ** 28
    t = np.linspace(0, 1, h)[:, None].repeat(w, 1)
    top, mid, bottom = (np.array(c, np.float32) / 255.0 for c in (top, mid, bottom))
    base = np.where((t < 0.5)[..., None], top * (1 - t * 2)[..., None] + mid * (t * 2)[..., None], mid * (1 - (t - 0.5) * 2)[..., None] + bottom * ((t - 0.5) * 2)[..., None])
    # 上 1/3 に 明るい つや（金属の 反射）
    sheen = np.clip(1 - np.abs(t - 0.22) / 0.2, 0, 1) ** 2 * 0.35
    col = base * (0.55 + 0.6 * diff)[..., None] + (spec * 0.55 + sheen)[..., None]
    col = np.clip(col, 0, 1)
    return col, mask


def text_mask(text, font, size, w_target=None, h_target=None, stretch=True):
    """文字の マスク（0〜1）。w_target／h_target に 合わせて 大きさを 決める（stretch なら 横幅も 合わせる）"""
    f = ImageFont.truetype(font, size)
    x0, y0, x1, y1 = f.getbbox(text)
    tw, th = x1 - x0, y1 - y0
    pad = size // 4
    im = Image.new('L', (tw + pad * 2, th + pad * 2), 0)
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=f, fill=255)
    im = im.crop(im.getbbox())
    if h_target:
        k = h_target / im.height
        im = im.resize((max(1, round(im.width * k)), h_target), Image.LANCZOS)
    if w_target and stretch and im.width != w_target:
        im = im.resize((w_target, im.height), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


def paste(canvas, rgb, alpha, x, y):
    """canvas（RGB float）に rgb（float）を alpha で 重ねる"""
    h, w = alpha.shape
    reg = canvas[y:y + h, x:x + w]
    a = alpha[..., None]
    canvas[y:y + h, x:x + w] = reg * (1 - a) + rgb * a


def shadow(alpha, blur, dx, dy, strength=0.75):
    """影（黒）：alpha を ずらして ぼかす → (alpha, rgb) """
    h, w = alpha.shape
    sh = np.zeros((h + abs(dy) * 2 + blur * 4, w + abs(dx) * 2 + blur * 4), np.float32)
    oy, ox = abs(dy) + blur * 2, abs(dx) + blur * 2
    sh[oy + dy:oy + dy + h, ox + dx:ox + dx + w] = alpha
    sh = cv2.GaussianBlur(sh, (0, 0), blur) * strength
    return sh, (oy, ox)


def build(src):
    base = cv2.imread(src, cv2.IMREAD_COLOR)
    assert base is not None and base.shape[:2] == (655, 1200), (src, None if base is None else base.shape)
    # 1) 右の 文字を 消す（明るい 所を マスクに して 塗り直す）→ 3倍に 大きく（少し くっきり）
    g = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    x0, y0, x1, y1 = CLEAR
    m = np.zeros(g.shape, np.uint8)
    m[y0:y1, x0:x1] = (g[y0:y1, x0:x1] > 58).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    clean = cv2.inpaint(base, m, 7, cv2.INPAINT_TELEA)
    big = cv2.resize(clean, (1200 * S, 655 * S), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(big, (0, 0), 2.2)
    big = cv2.addWeighted(big, 1.32, blur, -0.32, 0)
    # 消した 所は なめらかに（塗り直しの すじを ぼかす）
    sm = cv2.GaussianBlur(big, (0, 0), 6)
    mm = cv2.resize(m, (1200 * S, 655 * S), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    mm = cv2.GaussianBlur(mm, (0, 0), 9)[..., None]
    big = (big * (1 - mm) + sm * mm).astype(np.uint8)
    canvas = big[..., ::-1].astype(np.float32) / 255.0            # RGB float
    # 2) TENGER（金の 立体の 字）
    bx0, by0, bx1, by1 = TENGER
    tw, th = (bx1 - bx0) * S, (by1 - by0) * S
    mk = text_mask('TENGER', FONT_DELA, 90 * S, w_target=tw, h_target=th)
    sh, (oy, ox) = shadow(mk, blur=6 * S // 2, dx=0, dy=3 * S, strength=0.8)
    paste(canvas, np.zeros((*sh.shape, 3), np.float32), sh, bx0 * S - ox, by0 * S - oy)
    col, a = gold_shade(mk, bevel=6 * S)
    # こい ふち（字の まわり 1px）
    edge = cv2.dilate((mk > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32) - (mk > 0.5)
    paste(canvas, np.full((*mk.shape, 3), 0.18, np.float32) * np.array([1.0, 0.8, 0.45]), np.clip(edge, 0, 1) * 0.9, bx0 * S, by0 * S)
    paste(canvas, col, a, bx0 * S, by0 * S)
    # 3) 説明の 行（白・こい ふち・影）
    tx0, ty0, tx1, ty1 = TAG
    size = 23 * S
    f = ImageFont.truetype(FONT_MPLUS, size)
    f.set_variation_by_axes([800])
    tb = f.getbbox(TAGLINE)
    # 幅を 元の 行に 合わせる（字の 大きさを 決める）
    size = int(size * ((tx1 - tx0) * S) / (tb[2] - tb[0]))
    f = ImageFont.truetype(FONT_MPLUS, size); f.set_variation_by_axes([800])
    tb = f.getbbox(TAGLINE)
    layer = Image.new('RGBA', (1200 * S, 655 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = (tx0 + tx1) / 2 * S; cy = (ty0 + ty1) / 2 * S
    px, py = cx - (tb[0] + tb[2]) / 2, cy - (tb[1] + tb[3]) / 2
    d.text((px, py), TAGLINE, font=f, fill=(255, 255, 255, 255), stroke_width=max(1, S), stroke_fill=(10, 28, 40, 255))
    la = np.asarray(layer).astype(np.float32) / 255.0
    ta = la[..., 3]
    sh = cv2.GaussianBlur(np.roll(ta, 2 * S, axis=0), (0, 0), 2 * S) * 0.7
    canvas = canvas * (1 - sh[..., None])
    canvas = canvas * (1 - ta[..., None]) + la[..., :3] * ta[..., None]
    # 4) 「テンゲル」の 金の 札
    px0, py0, px1, py1 = PLATE
    pw, ph = (px1 - px0) * S, (py1 - py0) * S
    pm = rr_mask(pw, ph, 7 * S)
    sh, (oy, ox) = shadow(pm, blur=5 * S, dx=0, dy=4 * S, strength=0.7)
    paste(canvas, np.zeros((*sh.shape, 3), np.float32), sh, px0 * S - ox, py0 * S - oy)
    pcol, pa = gold_shade(pm, bevel=5 * S, top=(250, 232, 168), mid=(226, 182, 72), bottom=(160, 110, 30))
    # 札の 内がわの 細い 線（元の 絵の 2重の ふち）
    inner = rr_mask(pw - 6 * S, ph - 6 * S, 5 * S)
    ring = inner - np.pad(rr_mask(pw - 6 * S - 2 * S, ph - 6 * S - 2 * S, 4 * S), S)
    pcol[3 * S:3 * S + ring.shape[0], 3 * S:3 * S + ring.shape[1]] = pcol[3 * S:3 * S + ring.shape[0], 3 * S:3 * S + ring.shape[1]] * (1 - np.clip(ring, 0, 1)[..., None] * 0.35)
    # 外の こい ふち
    edge = pm - np.pad(rr_mask(pw - 2 * S, ph - 2 * S, 6 * S), S)
    pcol = pcol * (1 - np.clip(edge, 0, 1)[..., None] * 0.55)
    paste(canvas, pcol, pa, px0 * S, py0 * S)
    tm = text_mask('テンゲル', FONT_DELA, 50 * S, h_target=int(ph * 0.56), stretch=False)
    tmh, tmw = tm.shape
    tx = px0 * S + (pw - tmw) // 2; ty = py0 * S + (ph - tmh) // 2 - S
    # 字の 影（札の 上に うすく）と 紺の 字
    sh, (oy, ox) = shadow(tm, blur=2 * S, dx=0, dy=S, strength=0.35)
    paste(canvas, np.zeros((*sh.shape, 3), np.float32), sh, tx - ox, ty - oy)
    paste(canvas, np.full((*tm.shape, 3), 1.0, np.float32) * (np.array(NAVY, np.float32) / 255.0), tm, tx, ty)
    return np.clip(canvas, 0, 1)


def save_webp(rgb, path, size, q):
    im = cv2.resize((rgb[..., ::-1] * 255).round().astype(np.uint8), size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, im, [cv2.IMWRITE_WEBP_QUALITY, q])
    print(path, size, f'{os.path.getsize(path) / 1e3:.0f}KB')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src = args[0] if args else os.path.join(HERE, 'banner_src.webp')   # 元の 絵（1200×655・文字は 前の まま）
    canvas = build(src)
    out_dir = os.path.join(SRC_DIR, 'manual', 'img')
    if '--preview' in sys.argv:
        save_webp(canvas, os.path.join(SRC_DIR, 'manual', 'img', 'banner_preview.png').replace('.png', '.webp'), (1200 * S, 655 * S), 90)
    else:
        save_webp(canvas, os.path.join(out_dir, 'banner.webp'), (2400, 1310), 82)
    if '--no-blobs' not in sys.argv:
        sys.path.insert(0, os.path.join(SRC_DIR, 'kisekae', 'flat'))
        import tengel_banner as TB
        ids = json.load(open(os.path.join(SRC_DIR, 'kisekae', 'tengel_blobs.json')))
        bl = os.path.join(SRC_DIR, 'ios', 'kisekae_blobs'); os.makedirs(bl, exist_ok=True)
        cx0, cy0, cx1, cy1 = TB.CROP
        crop = canvas[cy0 * S:cy1 * S, cx0 * S:cx1 * S]
        save_webp(crop, os.path.join(bl, ids['banner'] + '.webp'), (TB.W * 3, TB.Hh * 3), 85)
        save_webp(canvas, os.path.join(bl, ids['push'] + '.webp'), (1800, 982), 88)
