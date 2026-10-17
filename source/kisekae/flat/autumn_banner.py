"""紅葉（780×320）：もみじの林・遠くの山・舞う葉は前の r3d/banners/autumn.py のまま（同じ乱数の順）、
   馬だけ描き直す → 馬らしい形の、ぺたっとした色の競走馬（第2版・horse_flat）：前足を上げて歩く栗毛の馬（亜麻色のたてがみ・もみじの髪かざり・赤に山吹のふちの布）
   python3 flat/autumn_banner.py <出力.webp>"""
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
rng = np.random.default_rng(41)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#FBE3BE'), (0.6, '#FCEED6'), (1, '#F5D7A8')])
# 遠くの山
for y0, amp, col, f in [(150, 22, '#EBB98A', 70), (182, 16, '#DF9A62', 45)]:
    ridge = y0 + amp * np.sin(xx / f + y0) + amp * 0.5 * np.sin(xx / (f * .37))
    img = over(img, hexc(col), np.clip((yy - ridge) / 2 + .5, 0, 1))
img = over(img, hexc('#C7703A'), np.clip((yy - (262 + 6 * np.sin(xx / 70))) / 2 + .5, 0, 1))
img = over(img, hexc('#B35F2F'), np.clip((yy - (292 + 4 * np.sin(xx / 40))) / 2 + .5, 0, 1))


def leaf_poly(x, y, s, rot):
    """もみじの葉（大きな5つの切れこみ＋ぎざぎざ）"""
    pts = []
    lobes = [(0, 1.0), (1, 0.92), (2, 0.62), (3, 0.62), (4, 0.92)]
    for k in range(5):
        c = rot - math.pi / 2 + k * 2 * math.pi / 5
        L = s * lobes[k][1]
        for j, (da, rr) in enumerate([(-0.55, 0.38), (-0.3, 0.7), (-0.18, 0.62), (0.0, 1.0), (0.18, 0.62), (0.3, 0.7), (0.55, 0.38)]):
            a = c + da
            pts.append((x + math.cos(a) * L * rr, y + math.sin(a) * L * rr))
    return np.array(pts)


# 木（幹）と葉のかたまり
trunks = []
for x0, h, side in [(40, 300, 1), (150, 260, -1), (690, 290, -1), (760, 240, 1)]:
    pts = flow((x0, 330), math.radians(-90 + side * 6), h, 8, rng=rng, wave=0.4)
    trunks.append(lock_poly(pts, 20, 9))
    for k in range(3):
        j = int(len(pts) * rng.uniform(.4, .85))
        b = flow(pts[j], math.radians(-90 + rng.choice([-1, 1]) * rng.uniform(30, 60)), rng.uniform(40, 80), 6, rng=rng)
        trunks.append(lock_poly(b, 6, 2))
img = over(img, hexc('#4E2E22'), poly_aa((Hh, W), trunks))
cols = ['#C93A22', '#E2572A', '#F08A2E', '#F6B93B', '#B52A1E']
for cx, cy, rr, n in [(70, 50, 110, 220), (180, 30, 70, 110), (700, 50, 110, 220), (590, 20, 60, 90)]:
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); d = rr * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d * 1.15, cy + math.sin(a) * d * 0.7
        m = poly_aa((Hh, W), [leaf_poly(x, y, rng.uniform(7, 12), rng.uniform(0, 6))])
        img = over(img, hexc(cols[rng.integers(0, len(cols))]), m)

# かわいい競走馬（flat/cute_themes.py・前足を上げて歩く栗毛の馬（亜麻色のたてがみ・もみじの髪かざり・赤に山吹のふちの布））
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'autumn', W, Hh)
# 舞う葉（手前）
for i in range(28):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    m = poly_aa((Hh, W), [leaf_poly(x, y, rng.uniform(5, 10), rng.uniform(0, 6))])
    img = over(img, hexc(cols[rng.integers(0, len(cols))]), m)
save_webp(img, out)
print(out)
