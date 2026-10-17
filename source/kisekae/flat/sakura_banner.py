"""桜（780×320）：満開の桜・若草の丘・舞う花びらは前の r3d/banners/sakura.py のまま（同じ乱数の順）、
   馬だけ描き直す → 馬らしい形の、ぺたっとした色の競走馬（第2版・horse_flat）：桜の下に立つ白い馬（桜色のたてがみ・耳もとの桜の花かざり・桜色の布）
   python3 flat/sakura_banner.py <出力.webp>"""
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
rng = np.random.default_rng(21)

# 空・遠くの丘
img = grad_v(Hh, W, [(0, '#BFE0F4'), (0.55, '#F3EEF6'), (1, '#FDEFF4')])
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
hill = 205 + 18 * np.sin(xx / 120 + 1.2) + 10 * np.sin(xx / 47)
img = over(img, hexc('#CFE3C8'), np.clip((yy - hill) / 2 + .5, 0, 1) * 0.9)
img = over(img, hexc('#B5D69A'), np.clip((yy - (250 + 8 * np.sin(xx / 90))) / 2 + .5, 0, 1))
img = over(img, hexc('#9CC97C'), np.clip((yy - (290 + 5 * np.sin(xx / 60 + 2))) / 2 + .5, 0, 1))

# 桜の木（左と右の上から枝がのびる）
def tree(img, x0, y0, side, seed):
    r = np.random.default_rng(seed)
    trunk = []
    polys = []
    pts = flow((x0, y0), math.radians(-90 + side * 12), 150, 10, rng=r, wave=0.6)
    polys.append(lock_poly(pts, 30, 12))
    for k in range(5):
        j = int(len(pts) * r.uniform(.35, .9))
        a = math.radians(-90 + side * r.uniform(25, 70))
        b = flow(pts[j], a, r.uniform(60, 130), 8, rng=r, wave=0.8, phase=k)
        polys.append(lock_poly(b, r.uniform(7, 12), 2))
    m = poly_aa((Hh, W), polys)
    img = over(img, hexc('#5B3B33'), m)
    return img, pts

img, t1 = tree(img, 70, 330, 1, 3)
img, t2 = tree(img, 760, 330, -1, 4)
# 花のかたまり
blossom = np.zeros((Hh, W), np.float32)
shade = np.zeros((Hh, W), np.float32)
for cx, cy, rr, n in [(90, 60, 120, 260), (20, 140, 70, 90), (210, 20, 80, 120), (700, 40, 120, 260), (770, 150, 60, 70), (560, 10, 70, 80)]:
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); d = rr * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d * 1.2, cy + math.sin(a) * d * 0.75
        r0 = rng.uniform(6, 13)
        cv2.circle(blossom, (int(x * 4), int(y * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        cv2.circle(shade, (int((x + 3) * 4), int((y + 4) * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
blossom = np.clip(blossom, 0, 1); shade = np.clip(shade, 0, 1)
img = over(img, hexc('#E99AB4'), shade * 0.9)
img = over(img, hexc('#F7C3D3'), blossom)
hl = np.zeros((Hh, W), np.float32)
for i in range(420):
    x, y = rng.uniform(0, W), rng.uniform(0, 200)
    if blossom[int(min(y, Hh - 1)), int(min(x, W - 1))] > .5:
        cv2.circle(hl, (int(x * 4), int(y * 4)), int(rng.uniform(2, 4.5) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
img = over(img, hexc('#FFE8EF'), np.clip(hl, 0, 1) * blossom)

# かわいい競走馬（flat/cute_themes.py・桜の下に立つ白い馬（桜色のたてがみ・耳もとの桜の花かざり・桜色の布））
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'sakura', W, Hh)
# 舞う花びら（手前）
pet = np.zeros((Hh, W), np.float32)
pet2 = np.zeros((Hh, W), np.float32)
for i in range(70):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    s = rng.uniform(3, 7); a = rng.uniform(0, 180)
    tgt = pet if rng.random() < .7 else pet2
    cv2.ellipse(tgt, (int(x * 4), int(y * 4)), (int(s * 4), int(s * 2.2)), a, 0, 360, 1.0, -1, cv2.LINE_AA, shift=2)
img = over(img, hexc('#F9B9CD'), np.clip(pet, 0, 1))
img = over(img, hexc('#FFDCE6'), np.clip(pet2, 0, 1))
save_webp(img, out)
print(out)
