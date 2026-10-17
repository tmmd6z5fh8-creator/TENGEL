"""開運：金の蹄鉄（U字で幸運をためる）の中に走る金の馬・四つ葉・金貨（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
from h3d import Scene, nrm, basis
import horse3d as Hm
from fire2d import aces, to_srgb

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

# 蹄鉄の中に、走る金の馬
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (318, 120, 462, 210), W, Hh, facing='right', azim=0, elev=2)
Rh = render_horse(pose, e, t, 26, W, Hh, ss=2, name='lucky_h')
hair, ha = mane_tail(Rh, (Hh, W), '#FFFFFF', '#FFFFFF', mode='flow', scale=0.8, seed=4, wind_ang=math.pi)
HA = np.clip(Rh['a'] + ha, 0, 1)
gold = grad_v(Hh, W, [(0, '#FFF0A8'), (0.45, '#F0C24A'), (0.6, '#C9952B'), (1, '#F7DE8A')])
img = over(img, hexc('#7A5208'), np.roll(HA, 2, 0) * 0.7)
img = over(img, gold, HA)

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
