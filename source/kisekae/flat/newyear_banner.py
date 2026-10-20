"""午年（お正月）（780×320）：赤地に金の雲・富士山と初日の出・「午」の丸い印・金の粉は前の r3d/banners/newyear.py のまま（同じ乱数の順）、
   馬だけ描き直す → 馬らしい形の、ぺたっとした色の競走馬（第2版・horse_flat）：前足を高く上げる白い馬（金のたてがみ・赤い頭のベルト・首に紅白の綱と金の鈴・赤に金のふちの布）
   python3 flat/newyear_banner.py <出力.webp>
   python3 flat/newyear_banner.py --layers <フォルダ>   → 初日の出の光を回すための2まい（まさちゃん「初日の出の太陽から出る光が、右回りで常に動いている」）：
     newyear_bg.webp  … 光より うしろ（赤地と青海波だけ・すき通しなし）
     newyear_top.webp … 光より 前（初日の出・富士山・金の雲・馬・「午」・金の粉・すき通しつき）。黒と白の上に同じものを描いて、その差から すき通しを出す
     newyear_sun.json … 光の決まり（まん中・本数・はば・うすくなり方）。光はページの SVG で描いて回す（flat/../newyear_wall.py）
     （この2まいと光を重ねると、光が回る前は いままでの絵とほぼ同じ＝ちがいは 1/255 くらい）"""
import sys, os, math, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import *
from cute_themes import draw_cute

W, Hh = 780, 320
SUN = (240, 150, 78)                 # 初日の出のまん中と半径（まん中の x は 富士山の頂上と同じ 240：まさちゃん「太陽の位置を富士山の真ん中に合わせて！」・まえは 250）
RAYS = dict(n=12, thr=0.4, alpha=0.22, decay=220, color='#F2C14E')   # 光：sin(角度×n) > thr の所・こさ alpha×exp(−きょり/decay)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)


# 金の雲（すやり霞）
def cloud_band(img, x0, y0, w, h):
    m = np.zeros((Hh, W), np.float32)
    for k in range(int(w / 26)):
        cx = x0 + k * 26 + 13
        cv2.circle(m, (int(cx * 4), int((y0 + 3 * math.sin(k)) * 4)), int(h * 0.62 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    cv2.rectangle(m, (int(x0 * 4), int(y0 * 4)), (int((x0 + w) * 4), int((y0 + h * 0.6) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
    m = np.clip(m, 0, 1)
    img = over(img, hexc('#B98322'), np.roll(m, 2, 0))
    img = over(img, hexc('#E9B949'), m)
    return img


def render(mode='full', base=None):
    """mode：'full' いままでの絵／'bg' 光より うしろだけ（赤地と青海波）／'fg' 光より前のものだけを、一色 base（0〜1 の RGB）の上に描く"""
    rng = np.random.default_rng(71)
    if mode == 'fg':
        img = np.zeros((Hh, W, 3), np.float32) + np.asarray(base, np.float32)
    else:
        img = grad_v(Hh, W, [(0, '#B30F17'), (1, '#D21F26')])
        # 青海波（下半分にうすく金の線）
        sg = np.zeros((Hh, W), np.float32)
        R0 = 26
        for row in range(8):
            cy = 170 + row * R0 * 0.5
            off = (row % 2) * R0
            for cx in np.arange(-R0, W + R0, R0 * 2) + off:
                for k in (1.0, 0.72, 0.44):
                    cv2.ellipse(sg, (int(cx * 4), int(cy * 4)), (int(R0 * k * 4), int(R0 * k * 4)), 0, 180, 360, 1.0, 3, cv2.LINE_AA, shift=2)
        img = over(img, hexc('#E7B23F'), np.clip(sg, 0, 1) * 0.28 * (yy > 150))
    if mode == 'bg':
        return img
    # 初日の出（金の円と光）
    sx, sy, sr = SUN
    sun = soft_circle(Hh, W, sx, sy, sr, 1.2)
    if mode == 'full':
        ray = (np.sin(np.arctan2(yy - sy, xx - sx) * RAYS['n']) > RAYS['thr']) * np.exp(-np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / RAYS['decay'])
        img = over(img, hexc(RAYS['color']), np.clip(ray * RAYS['alpha'], 0, 1))
    img = over(img, hexc('#F7D66B'), sun)
    # 富士山
    fuji = np.array([(60, 300), (215, 120), (240, 112), (262, 118), (420, 300)])
    img = over(img, hexc('#1F3A6B'), poly_aa((Hh, W), [fuji]))
    cap = np.array([(178, 165), (215, 120), (240, 112), (262, 118), (300, 165), (284, 158), (270, 172), (252, 156), (236, 174), (220, 158), (204, 172), (192, 160)])
    img = over(img, hexc('#FFFFFF'), poly_aa((Hh, W), [cap]))
    img = cloud_band(img, 20, 236, 300, 26)
    img = cloud_band(img, 330, 286, 260, 24)
    img = cloud_band(img, 600, 52, 160, 22)
    # かわいい競走馬（flat/cute_themes.py・前足を高く上げる白い馬（金のたてがみ・赤い頭のベルト・首に紅白の綱と金の鈴・赤に金のふちの布））
    if os.environ.get('CUTE_NO_HORSE') != '1':
        img = draw_cute(img, 'newyear', W, Hh)
    # 「午」の丸い印
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    cx, cy, r = 700, 236, 46
    d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(233, 185, 73))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 22, 29))
    f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc', 62, index=0)
    d.text((cx, cy + 2), '午', font=f, fill=(255, 246, 228), anchor='mm')
    img = np.asarray(pil).astype(np.float32) / 255
    # 金の粉
    gd = np.zeros((Hh, W), np.float32)
    for i in range(120):
        cv2.circle(gd, (int(rng.uniform(0, W) * 4), int(rng.uniform(0, Hh) * 4)), int(rng.uniform(0.6, 1.8) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    img = over(img, hexc('#F7D66B'), np.clip(gd, 0, 1) * 0.8)
    return img


def layers(outdir):
    """光より うしろ（すき通しなし）と前（すき通しつき）の2まい＋光の決まり"""
    bg = render('bg')
    k, w = render('fg', (0, 0, 0)), render('fg', (1, 1, 1))
    a = np.clip(1 - (w - k).mean(axis=2), 0, 1)                          # 黒の上と白の上の差 ＝ 1 − すき通し
    col = np.where(a[..., None] > 1e-4, k / np.maximum(a, 1e-4)[..., None], 0)
    rgba = np.dstack([np.clip(col, 0, 1), a])
    save_webp(bg, f'{outdir}/newyear_bg.webp')
    Image.fromarray((rgba * 255 + .5).astype(np.uint8), 'RGBA').save(f'{outdir}/newyear_top.webp', 'WEBP', quality=90, method=6)
    sx, sy, sr = SUN
    json.dump(dict(size=[W, Hh], sun=[sx, sy, sr], **RAYS), open(f'{outdir}/newyear_sun.json', 'w'))
    # たしかめ：いまの光（回る前）を重ねると、いままでの絵とどれくらいちがうか
    sx, sy, _ = SUN
    ray = (np.sin(np.arctan2(yy - sy, xx - sx) * RAYS['n']) > RAYS['thr']) * np.exp(-np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / RAYS['decay'])
    comp = over(over(bg, hexc(RAYS['color']), np.clip(ray * RAYS['alpha'], 0, 1)), np.clip(col, 0, 1), a)
    diff = np.abs(comp - render('full')).max() * 255
    print(f'layers: {outdir}/newyear_bg.webp newyear_top.webp newyear_sun.json（重ねたときのちがい 最大 {diff:.1f}/255）')


if __name__ == '__main__':
    if sys.argv[1] == '--layers':
        layers(sys.argv[2])
    else:
        out = sys.argv[1]
        save_webp(render(), out)
        print(out)
