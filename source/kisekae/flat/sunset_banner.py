"""夕焼け（780×320）：空・夕日・雲の筋・丘・草・鳥は前の r3d/banners/sunset.py のまま（同じ乱数の順）、
   馬だけ描き直す → 夕日を背に丘をかける馬のシルエット（flat/sunset_horse.py：細い毛の束のたてがみとしっぽ・夕日がわのふちの光）
   python3 flat/sunset_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sunset_horse import *

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(81)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#3B1E5E'), (0.32, '#8E3B78'), (0.58, '#F0663F'), (0.78, '#FFB15A'), (1, '#FFD98A')])
sx, sy = 520, 236
glow = np.exp(-np.sqrt((xx - sx) ** 2 + ((yy - sy) * 1.3) ** 2) / 120)
img = img + glow[..., None] * hexc('#FFB46A') * 0.45
img = over(img, hexc('#FFE7A6'), soft_circle(Hh, W, sx, sy, 64, 1.2))
# うすい雲の筋
for y0, w_, c in [(70, 4, '#C2507A'), (96, 3, '#D8607A'), (128, 3, '#F08A5E'), (152, 2.5, '#FFB37A')]:
    band = np.exp(-((yy - y0 - 6 * np.sin(xx / 90 + y0)) / w_) ** 2) * (0.5 + 0.5 * np.sin(xx / 37 + y0))
    img = over(img, hexc(c), np.clip(band, 0, 1) * 0.6)
# 丘（シルエット）
hill = 262 - 34 * np.exp(-((xx - 480) / 260) ** 2) + 5 * np.sin(xx / 30)
img = over(img, hexc('#2A1235'), np.clip((yy - hill) / 1.5 + .5, 0, 1))
# 草
gr = np.zeros((Hh, W), np.float32)
for i in range(260):
    x = rng.uniform(0, W); y = 262 - 34 * math.exp(-((x - 480) / 260) ** 2) + 5 * math.sin(x / 30) + 2
    h = rng.uniform(6, 16)
    cv2.line(gr, (int(x * 16), int(y * 16)), (int((x + rng.uniform(-4, 4)) * 16), int((y - h) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
img = over(img, hexc('#2A1235'), np.clip(gr, 0, 1))
# 走る馬のシルエット（左向き）＋夕日がわのふちの光
if os.environ.get('SUNSET_NO_HORSE') != '1':
    img = draw(img, W, Hh)
# 鳥
for (x, y, s) in [(120, 70, 8), (150, 58, 6), (176, 76, 7), (650, 60, 7)]:
    pts = np.array([(x - s, y), (x - s * .45, y - s * .5), (x, y), (x + s * .45, y - s * .5), (x + s, y)])
    m = np.zeros((Hh * 4, W * 4), np.uint8)
    cv2.polylines(m, [np.round(pts * 64).astype(np.int32)], False, 255, 5, cv2.LINE_AA, shift=4)
    img = over(img, hexc('#2A1235'), cv2.resize(m, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255)
save_webp(img, out)
print(out)
