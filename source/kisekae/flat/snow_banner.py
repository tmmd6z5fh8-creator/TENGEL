"""雪（780×320）：雪の丘とモミの木・降る雪は前の r3d/banners/snow.py のまま（同じ乱数の順）、
   馬だけ描き直す → ぺたっとした色のかわいい競走馬：白い息をはいて立つ芦毛の馬（白いたてがみ・うすいまだら・水色と白の毛糸のマフラー・紺の布）
   python3 flat/snow_banner.py <出力.webp>"""
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
rng = np.random.default_rng(51)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#B9CDE2'), (0.6, '#E2EAF3'), (1, '#F2F6FA')])


def pine(x, y, h, col, snow):
    """雪をかぶったモミの木"""
    polys, caps = [], []
    for k in range(4):
        t = k / 4
        w = h * (0.42 - t * 0.08) * (1 - t * 0.3)
        yb = y - h * t * 0.78
        top = yb - h * 0.34
        polys.append(np.array([(x - w, yb), (x + w, yb), (x, top)]))
        caps.append(np.array([(x - w * .55, yb - h * .12), (x + w * .5, yb - h * .14), (x, top), ]))
    return polys, caps


for (x, y, h, c, a_) in [(60, 240, 120, '#5E8A84', .55), (120, 250, 90, '#5E8A84', .55), (700, 236, 130, '#5E8A84', .55), (640, 250, 80, '#5E8A84', .55),
                         (30, 300, 170, '#2F5D50', 1), (745, 305, 180, '#2F5D50', 1), (690, 312, 110, '#2F5D50', 1)]:
    p, c2 = pine(x, y, h, c, True)
    img = over(img, hexc(c), poly_aa((Hh, W), p) * a_)
    img = over(img, hexc('#F7FBFF'), poly_aa((Hh, W), c2) * a_)
# 雪の丘
for y0, amp, col, f in [(232, 10, '#E8F0F8', 90), (262, 8, '#F7FAFD', 60)]:
    ridge = y0 + amp * np.sin(xx / f + y0 * .1) + amp * .6 * np.sin(xx / (f * .4))
    m = np.clip((yy - ridge) / 2 + .5, 0, 1)
    img = over(img, hexc(col), m)
    img = over(img, hexc('#D3E1EE'), m * np.clip((ridge + 10 - yy) / 10, 0, 1) * 0.6)

# かわいい競走馬（flat/cute_themes.py・白い息をはいて立つ芦毛の馬（白いたてがみ・うすいまだら・水色と白の毛糸のマフラー・紺の布））
rng.random((Hh, W))      # 前の絵のまだら模様で使っていた乱数：降る雪の位置を前と同じにするため、同じだけ進める
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'snow', W, Hh)
# 降る雪
for size, n, bl in [(1.2, 260, 0.6), (2.2, 90, 1.0), (3.4, 30, 1.6)]:
    sn = np.zeros((Hh, W), np.float32)
    for i in range(n):
        cv2.circle(sn, (int(rng.uniform(0, W) * 4), int(rng.uniform(0, Hh) * 4)), int(size * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    img = over(img, hexc('#FFFFFF'), blur(np.clip(sn, 0, 1), bl) * 0.85)
save_webp(img, out)
print(out)
