"""海（780×320）：青い空と海・雲・波打ちぎわ・かもめは前の r3d/banners/sea.py のまま（同じ乱数の順）、
   馬だけ描き直す → ぺたっとした色のかわいい競走馬：波打ちぎわを走る鹿毛の馬（黒いたてがみ・紺に白いしまの布）と、ひづめのしぶき
   python3 flat/sea_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import *
from cute_themes import draw_cute

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(31)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

img = grad_v(Hh, W, [(0, '#3FA9EC'), (0.45, '#9AD8F6'), (0.47, '#1E86CF'), (0.7, '#46B7E2'), (0.72, '#F6E3B8'), (1, '#EBCB8E')])
# 雲
cl = np.zeros((Hh, W), np.float32)
for cx, cy, n in [(110, 46, 7), (640, 36, 8), (430, 70, 4)]:
    for i in range(n):
        x = cx + rng.uniform(-50, 50); y = cy + rng.uniform(-10, 8); r = rng.uniform(14, 26)
        cv2.circle(cl, (int(x * 4), int(y * 4)), int(r * 4), 1.0, -1, cv2.LINE_AA, shift=2)
cl = np.clip(cl, 0, 1)
img = over(img, hexc('#D9EEFA'), np.roll(cl, 4, 0) * 0.9)
img = over(img, hexc('#FFFFFF'), cl)
# 海のきらめき・波の線
hz = 0.46 * Hh
for i in range(70):
    y = rng.uniform(hz + 4, 0.71 * Hh); x = rng.uniform(0, W); L = rng.uniform(10, 40) * (y - hz) / 60
    cv2.line(img, (int(x * 16), int(y * 16)), (int((x + L) * 16), int(y * 16)), (1, 1, 1), 1, cv2.LINE_AA, shift=4)
img = np.clip(img, 0, 1)
# 波打ちぎわ（ぬれた砂・白い泡）
shore = 0.715 * Hh + 5 * np.sin(xx / 55) + 3 * np.sin(xx / 23 + 1)
wet = np.clip((yy - shore) / 2 + .5, 0, 1) * np.clip((shore + 22 - yy) / 6, 0, 1)
img = over(img, hexc('#D9BC86'), wet * 0.8)
foam = np.exp(-((yy - shore) / 3.0) ** 2)
img = over(img, hexc('#FFFFFF'), foam * 0.95)
foam2 = np.exp(-((yy - (shore - 14 + 3 * np.sin(xx / 30))) / 2.0) ** 2) * (np.sin(xx / 9) > -0.3)
img = over(img, hexc('#E8F8FF'), foam2 * 0.7)

# かわいい競走馬（flat/cute_themes.py・波打ちぎわを走る鹿毛の馬（黒いたてがみ・紺に白いしまの布）と、ひづめのしぶき）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'sea', W, Hh)
# かもめ
for (x, y, s) in [(150, 96, 9), (190, 80, 7), (700, 110, 8)]:
    pts = np.array([(x - s, y), (x - s * .45, y - s * .5), (x, y), (x + s * .45, y - s * .5), (x + s, y)])
    m = np.zeros((Hh * 4, W * 4), np.uint8)
    cv2.polylines(m, [np.round(pts * 64).astype(np.int32)], False, 255, 5, cv2.LINE_AA, shift=4)
    img = over(img, hexc('#2C5672'), cv2.resize(m, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255)
save_webp(img, out)
print(out)
