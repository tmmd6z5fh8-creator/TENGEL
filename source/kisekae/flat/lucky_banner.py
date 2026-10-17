"""開運の絵（780×320）：緑の地・四つ葉・金の蹄鉄（3D）・金貨・きらめきは前の lucky.py のまま、
   蹄鉄の中の馬だけ描き直す → 金運の馬のキャラクター（flat/lucky_pony.py：金色の子馬が前足をあげて福を招き、小判をだく）
   python3 flat/lucky_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
sys.path.insert(0, HERE)
from style2d import *
from h3d import Scene, nrm, basis
from fire2d import aces, to_srgb
from lucky_pony import pony_svg
from flat_horse import to_png

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(161)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#1C6B3B'), (1, '#0F4A27')])
glow = np.exp(-(((xx - 390) / 260) ** 2 + ((yy - 160) / 150) ** 2))
img = img + glow[..., None] * hexc('#3FAF5F') * 0.45


def clover(x, y, s, rot):
    polys = []
    for k in range(4):
        a = rot + k * math.pi / 2
        c = (x + math.cos(a) * s * 0.55, y + math.sin(a) * s * 0.55)
        pts = []
        for j in range(24):
            t = j / 24 * 2 * math.pi
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            px, py = hx / 17 * s * 0.6, hy / 17 * s * 0.6
            ca, sa = math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)
            pts.append((c[0] + px * ca - py * sa, c[1] + px * sa + py * ca))
        polys.append(np.array(pts))
    return polys


# 背景の四つ葉（うすく）
for i in range(18):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    img = over(img, hexc('#2E8B4F'), poly_aa((Hh, W), clover(x, y, rng.uniform(10, 18), rng.uniform(0, 6))) * 0.55)

# 金の蹄鉄（3D）
sc = Scene()
sc.image(400, 320, 2)
sc.camera(np.array((0.0, 0.05, 3.3)), np.array((0.0, -0.02, 0.0)), 30)
sc.bounce(1)
sc.env((0.30, 0.22, 0.10), (0.10, 0.07, 0.03), (0.05, 0.03, 0.01))
sc.lobe((0.3, 0.8, 0.6), (5.0, 4.2, 3.0), 18.0)
sc.lobe((-0.8, 0.2, 0.5), (1.6, 1.3, 0.8), 8.0)
sc.lobe((0.0, -1.0, 0.3), (0.6, 0.9, 0.4), 3.0)
sc.light((0.4, 0.7, 0.6), (3.0, 2.7, 2.2), 10, 1)
sc.mat(7, 0, (1.0, 0.76, 0.33), 0.16)
sc.begin('U', 0.0, 7)
sc.ctorus(np.array((0, 0.02, 0)), (0, 0, 1), (0, -1, 0), 0.62, 0.12, 2.35, mat=7)
for k in range(-3, 4):
    if k == 0:
        continue
    a = k * 0.62
    p = np.array((math.sin(a) * 0.62, 0.02 - math.cos(a) * 0.62, 0.10))
    sc.rbox(p, (0.025, 0.045, 0.1), 0.01, basis(np.array((math.cos(a), math.sin(a), 0)), (0, 0, 1)), op='S', k=0.01, mat=7)
sc.end()
R = sc.render(os.path.join(TMP, 'shoe'))
rgb = to_srgb(aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None]))
A = R['a']
x0, y0 = 190, 0
layer = np.zeros((Hh, W, 3), np.float32); la = np.zeros((Hh, W), np.float32)
layer[y0:y0 + 320, x0:x0 + 400] = rgb; la[y0:y0 + 320, x0:x0 + 400] = A
img = img + blur(la, 14)[..., None] * hexc('#FFD45E') * 0.35
img = over(img, layer, la)

# ---------- 蹄鉄の中に、金運の馬のキャラクター ----------
halo = np.exp(-(((xx - 390) / 74) ** 2 + ((yy - 150) / 74) ** 2))          # うしろの光
img = img + halo[..., None] * hexc('#FFF2B8') * 0.42
PH = 174                                                                       # キャラクターの高さ（画素）
pw = int(round(PH * 200 / 210))
tmp = os.path.join(TMP, 'lucky_pony.png')
to_png(pony_svg(200, 210), 200, 210, tmp, scale=6)
pim = cv2.imread(tmp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
pa = pim[..., 3]
prem = pim[..., :3][..., ::-1] * pa[..., None]
prem = cv2.resize(prem, (pw, PH), interpolation=cv2.INTER_AREA)
pa = cv2.resize(pa, (pw, PH), interpolation=cv2.INTER_AREA)
prgb = prem / np.maximum(pa[..., None], 1e-4)
px0, py0 = 390 - pw // 2, 58
sh = np.zeros((Hh, W), np.float32)                                             # 足もとのうすい影
cv2.ellipse(sh, (390 * 16, int((py0 + PH * 0.975) * 16)), (int(pw * 0.40 * 16), int(5 * 16)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
img = img * (1 - blur(sh, 2.5)[..., None] * 0.30)
img[py0:py0 + PH, px0:px0 + pw] = over(img[py0:py0 + PH, px0:px0 + pw], prgb, pa)

# 金貨と四つ葉（手前）
for (x, y, r) in [(120, 250, 26), (165, 280, 22), (640, 262, 28), (690, 230, 20)]:
    m = soft_circle(Hh, W, x, y, r, 1.0)
    img = over(img, hexc('#B98322'), np.roll(m, 3, 0))
    img = over(img, hexc('#F2C14E'), m)
    img = over(img, hexc('#FFE08A'), soft_circle(Hh, W, x, y, r * 0.72, 1.0) - soft_circle(Hh, W, x, y, r * 0.62, 1.0))
for (x, y, s, rot) in [(70, 120, 30, 0.3), (720, 110, 26, 1.1), (590, 60, 18, 0.7), (210, 60, 20, 2.0)]:
    m = poly_aa((Hh, W), clover(x, y, s, rot))
    img = over(img, hexc('#0E3E21'), np.roll(m, 2, 0) * 0.6)
    img = over(img, hexc('#5CC26E'), m)
# きらめき
sp = np.zeros((Hh, W), np.float32)
for i in range(40):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh); s = rng.uniform(3, 8)
    cv2.line(sp, (int((x - s) * 16), int(y * 16)), (int((x + s) * 16), int(y * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
    cv2.line(sp, (int(x * 16), int((y - s) * 16)), (int(x * 16), int((y + s) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
img = img + blur(sp, 1)[..., None] * hexc('#FFE9A8') * 0.9
save_webp(np.clip(img, 0, 1), out)
print(out)
