"""ネオン：夜の格子の地平線とネオンの太陽、光の線で走る馬（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(131)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#05030F'), (0.55, '#1A0833'), (0.62, '#2B0A3D'), (1, '#07030F')])
hz = 196
# ネオンの太陽（しま入り）
sun = soft_circle(Hh, W, 520, hz - 6, 92, 1.0) * (yy < hz)
stripes = ((yy > hz - 60) & (((yy - (hz - 60)) % 14) > 14 - (yy - (hz - 60)) / 8)).astype(np.float32)
sun = sun * (1 - stripes)
scol = grad_v(Hh, W, [(0, '#FFE45C'), (0.35, '#FFE45C'), (0.62, '#FF3EA5'), (1, '#FF3EA5')])
img = img + blur(sun, 22)[..., None] * hexc('#FF3EA5') * 0.5
img = over(img, scol, sun)
# 格子の床
gl = np.zeros((Hh, W), np.float32)
for k in range(-16, 17):
    x_far = W / 2 + k * 18; x_near = W / 2 + k * 130
    cv2.line(gl, (int(x_far * 16), int(hz * 16)), (int(x_near * 16), int(Hh * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
for j in range(1, 14):
    y = hz + (Hh - hz) * (j / 13) ** 2.2
    cv2.line(gl, (0, int(y * 16)), (W * 16, int(y * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
gl = gl * (yy >= hz)
img = over(img, hexc('#0A0418'), (yy >= hz).astype(np.float32))
img = img + blur(gl, 3)[..., None] * hexc('#FF2BD6') * 0.6 + gl[..., None] * hexc('#FF7AE6') * 0.8
cv2.line(img, (0, hz), (W, hz), (1.0, 0.5, 0.9), 2, cv2.LINE_AA)
# 星
for i in range(80):
    x, y = rng.uniform(0, W), rng.uniform(0, hz - 20)
    m = soft_circle(Hh, W, x, y, rng.uniform(0.6, 1.4), 1.0)
    img = img + m[..., None] * 0.8
# 光の線の馬（右向き・走る）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (150, 40, 470, 250), W, Hh, facing='right', azim=8, elev=4)
R = render_horse(pose, e, t, 26, W, Hh, ss=2, name='neon')
hair, ha = mane_tail(R, (Hh, W), '#FFFFFF', '#FFFFFF', mode='flow', scale=1.35, seed=8, wind_ang=math.pi, tail_len=1.2)
ln = edges(R, width=2, crease=0.35)
hl = cv2.morphologyEx((ha > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
line = np.clip(ln + hl, 0, 1)
img = over(img, hexc('#050310'), np.clip(R['a'] + ha, 0, 1) * 0.85)
img = img + blur(line, 6)[..., None] * hexc('#00E5FF') * 0.9 + blur(line, 2)[..., None] * hexc('#5CF3FF') * 0.8
img = np.maximum(img, line[..., None] * hexc('#E6FDFF'))
img = np.clip(img, 0, 1)
save_webp(img, out)
print(out)
