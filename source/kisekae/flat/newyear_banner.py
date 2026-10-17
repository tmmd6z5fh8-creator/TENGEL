"""午年（お正月）（780×320）：赤地に金の雲・富士山と初日の出・「午」の丸い印・金の粉は前の r3d/banners/newyear.py のまま（同じ乱数の順）、
   馬だけ描き直す → ぺたっとした色のかわいい競走馬：前足を高く上げる白い馬（金のたてがみ・赤い頭のベルト・首に紅白の綱と金の鈴・赤に金のふちの布）
   python3 flat/newyear_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import *
from cute_themes import draw_cute

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(71)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
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
# 初日の出（金の円と光）
sun = soft_circle(Hh, W, 250, 150, 78, 1.2)
ray = (np.sin(np.arctan2(yy - 150, xx - 250) * 12) > 0.4) * np.exp(-np.sqrt((xx - 250) ** 2 + (yy - 150) ** 2) / 220)
img = over(img, hexc('#F2C14E'), np.clip(ray * 0.22, 0, 1))
img = over(img, hexc('#F7D66B'), sun)
# 富士山
fuji = np.array([(60, 300), (215, 120), (240, 112), (262, 118), (420, 300)])
img = over(img, hexc('#1F3A6B'), poly_aa((Hh, W), [fuji]))
cap = np.array([(178, 165), (215, 120), (240, 112), (262, 118), (300, 165), (284, 158), (270, 172), (252, 156), (236, 174), (220, 158), (204, 172), (192, 160)])
img = over(img, hexc('#FFFFFF'), poly_aa((Hh, W), [cap]))


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
save_webp(img, out)
print(out)
