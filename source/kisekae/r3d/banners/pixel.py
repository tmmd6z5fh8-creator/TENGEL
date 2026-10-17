"""ドット絵：昔のゲームのような、コースを走る馬（156×64 で描いて 5倍）（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 156, 64
out = sys.argv[1]
rng = np.random.default_rng(181)
PAL = {k: hexc(v) for k, v in dict(sky1='#29ADFF', sky2='#7FD3FF', cloud='#FFF1E8', hill='#00B543', hill2='#008751', dirt='#AB5236',
                                   dirt2='#8A3F28', rail='#FFF1E8', post='#FF004D', horse='#8A4A24', horse2='#5A2A14', mane='#1D1D1D',
                                   white='#FFF1E8', yel='#FFEC27', black='#000000').items()}
img = np.zeros((Hh, W, 3), np.float32)
img[:] = PAL['sky1']
img[18:40] = PAL['sky2']
# 雲（ドット）
for cx, cy in [(20, 9), (70, 6), (128, 11)]:
    for dx, dy, w in [(0, 0, 14), (3, -2, 8), (-2, 1, 4)]:
        img[cy + dy:cy + dy + 3, cx + dx:cx + dx + w] = PAL['cloud']
# 丘
for x in range(W):
    h1 = int(34 + 3 * math.sin(x / 9) + 2 * math.sin(x / 4.3))
    img[h1:40, x] = PAL['hill2'] if (x // 2 + h1) % 5 == 0 else PAL['hill']
# コース
img[40:64] = PAL['dirt']
for y in range(42, 64, 3):
    for x in range((y * 7) % 6, W, 6):
        img[y, x] = PAL['dirt2']
img[40, :] = PAL['rail']; img[39, ::4] = PAL['rail']
img[60, :] = PAL['rail']
# ゴール板
img[22:40, 140] = PAL['white']; img[22:28, 136:145] = PAL['post']; img[24:26, 138:143] = PAL['white']
# 馬（低い解像度で描いて、4色にへらす）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (40, 15, 110, 58), W, Hh, facing='right', azim=4, elev=4, fov=26)
R = render_horse(pose, e, t, 26, W, Hh, ss=3, name='pix')
hair, ha = mane_tail(R, (Hh, W), '#000000', '#000000', mode='flow', scale=0.25, seed=4, wind_ang=math.pi)
A = R['a']
n = R['n']
l = np.sum(n * nrm((0.3, 0.8, 0.5)), -1)
body = (A > 0.45)
img[body & (l > 0.2)] = PAL['horse']
img[body & (l <= 0.2)] = PAL['horse2']
p = world_pos(R)
legs = np.nan_to_num((p[..., 1] - R['S']['ground']) < 0.38).astype(bool) & body
img[legs] = PAL['black']
img[(ha > 0.45) & ~body] = PAL['mane']
# 輪郭（1ドット）
m = (body | (ha > 0.45)).astype(np.uint8)
edge = (cv2.dilate(m, np.ones((3, 3), np.uint8)) - m).astype(bool)
img[edge & (np.arange(Hh)[:, None] < 60)] = PAL['black']
# 目
ex, ey = R['eye']; img[int(round(ey)), int(round(ex))] = PAL['white']
# 文字「GO!」（ドットの文字）
F = {'G': ['01110', '10000', '10111', '10001', '01110'], 'O': ['01110', '10001', '10001', '10001', '01110'], '!': ['1', '1', '1', '0', '1']}
x = 118
for ch in 'GO!':
    g = F[ch]
    for r_, row in enumerate(g):
        for c_, v in enumerate(row):
            if v == '1':
                img[44 + r_ * 1:45 + r_ * 1, x + c_] = PAL['yel']
    x += len(g[0]) + 1
big = cv2.resize(img, (W * 5, Hh * 5), interpolation=cv2.INTER_NEAREST)
save_webp(big, out, q=95)
print(out)
