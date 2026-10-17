"""勝負服：あざやかな勝負服の柄を背に、騎手を乗せて走る馬（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(61)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
# 背景：ななめに区切った勝負服の柄（市松・たすき・縦じま・星）
img = np.broadcast_to(hexc('#1A3FB8'), (Hh, W, 3)).copy()
bands = [('#FFC400', '#E02424', 'check'), ('#FFFFFF', '#0F9D58', 'stripe'), ('#E02424', '#FFFFFF', 'star'), ('#0F9D58', '#FFC400', 'hoop'), ('#1A3FB8', '#FFFFFF', 'sash')]
u = xx + yy * 0.55
for i, (c1, c2, pat) in enumerate(bands):
    x0 = -60 + i * 175
    m = ((u >= x0) & (u < x0 + 175)).astype(np.float32)
    base = np.broadcast_to(hexc(c1), (Hh, W, 3))
    if pat == 'check':
        pm = (((xx // 22) + (yy // 22)) % 2 == 0)
    elif pat == 'stripe':
        pm = ((u // 16) % 2 == 0)
    elif pat == 'hoop':
        pm = ((yy // 24) % 2 == 0)
    elif pat == 'sash':
        pm = np.abs((xx - yy * 1.2) % 120 - 60) < 14
    else:
        pm = np.zeros((Hh, W), bool)
        for k in range(14):
            cx, cy = x0 + 40 + (k % 4) * 40 - (k // 4) * 20, 30 + (k // 4) * 80
            pts = [(cx + math.cos(math.pi / 2 + j * math.pi / 5) * (12 if j % 2 == 0 else 5), cy - math.sin(math.pi / 2 + j * math.pi / 5) * (12 if j % 2 == 0 else 5)) for j in range(10)]
            pm |= poly_aa((Hh, W), [np.array(pts)]) > .5
    tile = np.where(pm[..., None], hexc(c2), base)
    img = over(img, tile, m)
# 中央を少し暗くして馬を目立たせる・スピード線
vig = np.exp(-(((xx - 420) / 300) ** 2 + ((yy - 170) / 160) ** 2))
img = img * (1 - 0.35 * vig[..., None]) + hexc('#0B1E5C') * (0.35 * vig[..., None])
sp = np.zeros((Hh, W), np.float32)
for i in range(40):
    y = rng.uniform(40, 290); x = rng.uniform(-50, 500); L = rng.uniform(60, 200)
    cv2.line(sp, (int(x * 16), int(y * 16)), (int((x + L) * 16), int(y * 16)), 1.0, 2, cv2.LINE_AA, shift=4)
img = over(img, hexc('#FFFFFF'), blur(sp, 0.6) * 0.55)

# 走る馬＋騎手（右向き）
pose = dict(Hm.GALLOP)
post = lambda rgb, R: leg_points(rgb, R, '#1E1612', height=0.40)
rgb, a, R = horse_illust(pose, (250, 70, 560, 290), W, Hh, facing='right', azim=12, elev=5, body=('#7A3E1E', '#4A2310'),
                         mane=('#1C130F', '#0E0907'), line='#120B08', mode='flow', hoof='#222', eye='#0A0606', mane_scale=1.2, tail_len=1.1, seed=9, name='silks', post=post)
# ゼッケン
S = R['S']; sc = R['scene']
wx, wy = S['withers']
c = sc.project(np.array([[wx - 0.62, wy - 0.10, 0.31], [wx - 0.28, wy - 0.10, 0.31], [wx - 0.28, wy - 0.40, 0.30], [wx - 0.62, wy - 0.40, 0.30]]))[0]
cl = poly_aa((Hh, W), [c]) * (a > .5)
rgb = over(rgb, hexc('#FFFFFF'), cl)
cen = c.mean(0)
txt = np.zeros((Hh, W, 3), np.uint8)
cv2.putText(txt, '1', (int(cen[0] - 7), int(cen[1] + 8)), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
rgb = over(rgb, hexc('#111111'), txt[..., 0].astype(np.float32) / 255 * cl)
img = over(img, rgb, a)
jr, ja = jockey(R, (Hh, W), jacket='#FFD21F', pattern='diamond', pcol='#1A3FB8', cap='#E02424')
img = over(img, jr, ja)
save_webp(img, out)
print(out)
