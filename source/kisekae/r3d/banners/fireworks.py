"""花火：夏の夜空に大きな花火と、馬の形の花火・下に提灯（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(91)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#0A0F2C'), (0.7, '#1B2457'), (1, '#2A2F63')])
# 星
st = np.zeros((Hh, W), np.float32)
for i in range(120):
    cv2.circle(st, (int(rng.uniform(0, W) * 4), int(rng.uniform(0, 200) * 4)), int(rng.uniform(0.4, 1.0) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
img = over(img, hexc('#FFFFFF'), np.clip(st, 0, 1) * 0.6)
glow = np.zeros((Hh, W, 3), np.float32)


def burst(cx, cy, r, col, n=64, inner=None):
    lines = np.zeros((Hh, W), np.float32)
    dots = np.zeros((Hh, W), np.float32)
    for k in range(n):
        a = k / n * 2 * math.pi + rng.normal(0, 0.03)
        r0 = r * 0.18
        for j in range(7):
            rr = r0 + (r - r0) * j / 6
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr + (rr / r) ** 2 * 6
            cv2.circle(dots, (int(x * 4), int(y * 4)), int((1.0 + j * 0.25) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        x1, y1 = cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95 + 5
        cv2.line(lines, (int((cx + math.cos(a) * r0) * 16), int((cy + math.sin(a) * r0) * 16)), (int(x1 * 16), int(y1 * 16)), 0.5, 1, cv2.LINE_AA, shift=4)
    m = np.clip(dots + lines, 0, 1)
    c = hexc(col)
    return m[..., None] * c, blur(m, 6)[..., None] * c


for cx, cy, r, col in [(110, 92, 80, '#FF6FA8'), (300, 60, 60, '#FFD45E'), (690, 84, 86, '#6FE3FF'), (560, 40, 44, '#FF9F5A')]:
    core, g = burst(cx, cy, r, col)
    img = img + g * 0.9
    img = np.where(core.max(-1, keepdims=True) > 0, np.maximum(img, core), img)

# 馬の形の花火（走る馬の輪郭を光の粒で）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (330, 70, 560, 200), W, Hh, facing='right', azim=0, elev=2)
R = render_horse(pose, e, t, 26, W, Hh, ss=1, name='fw')
hair, ha = mane_tail(R, (Hh, W), '#FFFFFF', '#FFFFFF', mode='flow', scale=1.1, seed=4, wind_ang=math.pi)
A = np.clip(R['a'] + ha, 0, 1)
cont = cv2.morphologyEx((A > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
ys, xs = np.nonzero(cont)
sel = rng.choice(len(xs), size=min(520, len(xs)), replace=False)
sp = np.zeros((Hh, W), np.float32)
for i in sel:
    cv2.circle(sp, (int(xs[i] * 4), int(ys[i] * 4)), int(rng.uniform(0.9, 1.8) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
sp = np.clip(sp, 0, 1)
img = img + blur(sp, 5)[..., None] * hexc('#FFE08A') * 1.2 + blur(A, 3)[..., None] * hexc('#FFB43A') * 0.16
img = np.maximum(img, sp[..., None] * hexc('#FFF4C8'))
# 提灯のひも・提灯
yl = 268
cv2.line(img, (0, int(yl - 8)), (W, int(yl - 8)), (0.15, 0.12, 0.1), 2, cv2.LINE_AA)
for k, x in enumerate(np.arange(30, W, 62)):
    y = yl + 6 * math.sin(k)
    lm = np.zeros((Hh, W), np.float32)
    cv2.ellipse(lm, (int(x * 4), int(y * 4)), (int(19 * 4), int(25 * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=2)
    col = hexc('#E8352E') if k % 2 == 0 else hexc('#F2A23A')
    img = img + blur(lm, 14)[..., None] * col * 0.6
    img = over(img, col, lm)
    img = over(img, hexc('#FFE3A0'), lm * np.clip(1 - np.abs(xx - x) / 9, 0, 1) * 0.55)
    for dy in (-15, -5, 5, 15):
        rib = np.exp(-((yy - y - dy) / 1.0) ** 2) * lm
        img = over(img, hexc('#6E1410'), rib * 0.6)
    cap = np.zeros((Hh, W), np.float32)
    cv2.rectangle(cap, (int((x - 9) * 4), int((y - 29) * 4)), (int((x + 9) * 4), int((y - 23) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
    cv2.rectangle(cap, (int((x - 9) * 4), int((y + 23) * 4)), (int((x + 9) * 4), int((y + 29) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
    img = over(img, hexc('#1E1410'), cap)
img = np.clip(img, 0, 1)
save_webp(img, out)
print(out)
