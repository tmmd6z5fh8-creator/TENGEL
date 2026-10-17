"""星座：天の川の夜空に、星をむすんだ翼のある馬（ペガサス）の星座と三日月（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from paint import fbm, warp

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(201)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#070A24'), (0.6, '#1B1546'), (1, '#2D1B5A')])
# 天の川
band = np.exp(-(((yy - (220 - xx * 0.28)) / 60) ** 2))
neb = warp(fbm(Hh, W, 70, 5, seed=3), (fbm(Hh, W, 120, 3, seed=4) - .5) * 60, (fbm(Hh, W, 120, 3, seed=5) - .5) * 30)
img = img + (band * neb ** 2)[..., None] * hexc('#9C7BFF') * 0.45 + (band * neb ** 4)[..., None] * hexc('#FFD6F2') * 0.35
# 星
for i in range(700):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    b = rng.random() ** 3
    xi, yi = int(x), int(y)
    img[yi, xi] = np.minimum(1, img[yi, xi] + 0.35 + b * 0.65)
# 三日月
moon = soft_circle(Hh, W, 700, 58, 30, 1.0) - soft_circle(Hh, W, 712, 50, 27, 1.0)
img = img + blur(np.clip(moon, 0, 1), 10)[..., None] * hexc('#FFE9A8') * 0.4
img = over(img, hexc('#FFF2C4'), np.clip(moon, 0, 1))
# 星座（走る馬の目印をむすぶ）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (220, 110, 560, 292), W, Hh, facing='right', azim=0, elev=2)
R = render_horse(pose, e, t, 26, W, Hh, ss=1, name='const')
S = R['S']; sc = R['scene']
hair, ha = mane_tail(R, (Hh, W), '#FFFFFF', '#FFFFFF', mode='flow', scale=1.2, seed=8, wind_ang=math.pi)
body = np.clip(R['a'] + ha, 0, 1)
# 翼（せなかから上へ）
wb = np.array(R['crest'][4]) + np.array([-34, 6])
wing = np.array([wb, wb + (-40, -40), wb + (-10, -100), wb + (30, -122), wb + (36, -96), wb + (52, -104), wb + (50, -72),
                 wb + (66, -74), wb + (54, -40), wb + (64, -36), wb + (36, -8), wb + (20, 4)])
wing = wb + (wing - wb) * np.array([1.0, 0.82])
wm = poly_aa((Hh, W), [wing])
shape = (np.clip(body + wm, 0, 1) > 0.5).astype(np.uint8)
shape = cv2.morphologyEx(shape, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
cs, _ = cv2.findContours(shape, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)
poly = cv2.approxPolyDP(c, 9.0, True)[:, 0, :].astype(np.float32)
# うすい光の形
img = img + blur(shape.astype(np.float32), 5)[..., None] * hexc('#7F8CFF') * 0.14
ln = np.zeros((Hh, W), np.float32)
for i in range(len(poly)):
    p0, p1 = poly[i], poly[(i + 1) % len(poly)]
    cv2.line(ln, (int(p0[0] * 16), int(p0[1] * 16)), (int(p1[0] * 16), int(p1[1] * 16)), 1.0, 2, cv2.LINE_AA, shift=4)
img = img + blur(ln, 3)[..., None] * hexc('#8FB6FF') * 0.55
img = over(img, hexc('#D4E2FF'), ln * 0.6)
fl = np.zeros((Hh, W), np.float32)
for i, (x, y) in enumerate(poly):
    big = (i % 3 == 0)
    s_ = 9 if big else 5
    cv2.circle(fl, (int(x * 16), int(y * 16)), int((2.4 if big else 1.6) * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    if big:
        cv2.line(fl, (int((x - s_) * 16), int(y * 16)), (int((x + s_) * 16), int(y * 16)), 0.8, 1, cv2.LINE_AA, shift=4)
        cv2.line(fl, (int(x * 16), int((y - s_) * 16)), (int(x * 16), int((y + s_) * 16)), 0.8, 1, cv2.LINE_AA, shift=4)
ex, ey = R['eye']
cv2.circle(fl, (int(ex * 16), int(ey * 16)), int(1.8 * 16), 1.0, -1, cv2.LINE_AA, shift=4)
img = img + blur(fl, 4)[..., None] * hexc('#FFE08A') * 0.8
img = np.maximum(img, fl[..., None] * hexc('#FFF8E0'))
save_webp(np.clip(img, 0, 1), out)
print(out)
