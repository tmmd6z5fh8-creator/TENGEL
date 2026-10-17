"""メリーゴーランド：しま模様の屋根と電球、金の柱の木馬（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(171)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#FBE3EE'), (1, '#E9DDF7')])
# ぼけた光
for i in range(40):
    x, y = rng.uniform(0, W), rng.uniform(60, Hh); r = rng.uniform(8, 24)
    img = over(img, hexc(['#FFFFFF', '#FFE7A8', '#FFD1E6'][rng.integers(0, 3)]), soft_circle(Hh, W, x, y, r, 3) * 0.35)
# 床
img = over(img, hexc('#E7C9E9'), np.clip((yy - 288) / 1.5 + .5, 0, 1))


def pole(img, x):
    m = (np.abs(xx - x) < 5).astype(np.float32)
    tw = (np.sin((yy + xx * 0) * 0.45) > 0).astype(np.float32)
    col = np.where((tw * m)[..., None] > 0, hexc('#F7DE8A'), hexc('#C9952B'))
    hl = np.exp(-((xx - x + 2) / 1.5) ** 2) * m
    img = over(img, col, m)
    return over(img, hexc('#FFF6D0'), hl * 0.8)


# 木馬（奥・手前）
for k, (box, sc_, body, mane, saddle, seed) in enumerate([
        ((470, 92, 730, 270), 0.9, ('#FFF7FB', '#E8C9DC'), ('#F7D06A', '#E0A93A'), '#9ED8D0', 31),
        ((90, 84, 430, 300), 1.0, ('#FFFFFF', '#E3CDE6'), ('#F49AC1', '#E06A9E'), '#F49AC1', 32)]):
    pose = dict(Hm.PRANCE); pose['head_ang'] = -58.0
    rgb, a, R = horse_illust(pose, box, W, Hh, facing='right', azim=10, elev=4, body=body, mane=mane, line='#8A5A7A',
                             mode='stand', hoof='#C9952B', eye='#3A2030', mane_scale=1.4, tail_len=1.1, seed=seed, name=f'car{k}', hi='#FFFFFF')
    S = R['S']; scn = R['scene']
    wx, wy = S['withers']
    # 鞍（ピンク／ミント＋金のふち）
    q = scn.project(np.array([[wx - 0.10, wy + 0.02, 0.30], [wx - 0.62, wy - 0.02, 0.31], [wx - 0.66, wy - 0.42, 0.30], [wx - 0.12, wy - 0.44, 0.30]]))[0]
    sm = poly_aa((Hh, W), [q]) * (a > .5)
    rgb = over(rgb, hexc(saddle), sm)
    edge = cv2.GaussianBlur(cv2.morphologyEx((sm > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)), (3, 3), .6)
    rgb = over(rgb, hexc('#D9A93A'), edge)
    # 柱
    px = scn.project(np.array([[wx - 0.32, wy + 0.2, 0.0]]))[0][0][0]
    img = ground_shadow(img, R, k=0.15, w=110, h=7)
    img = over(img, rgb, a)
    img = pole(img, px)
    img = over(img, hexc('#C9952B'), ((np.abs(xx - px) < 5) & (yy > R['scene'].project(np.array([[wx - 0.32, wy - 0.2, 0.0]]))[0][0][1])).astype(np.float32) * (a < 0.5) * 0)

# 屋根（しま模様のふち）と電球
roof_y = 44
stripe = ((xx // 40) % 2 == 0)
roof = np.where(stripe[..., None], hexc('#F49AC1'), hexc('#FFFFFF'))
sc_edge = roof_y + 16 * np.sqrt(np.clip(1 - ((xx % 40) - 20) ** 2 / 400, 0, 1))
rm = np.clip((sc_edge - yy) / 1.2 + .5, 0, 1)
img = over(img, roof, rm)
img = over(img, hexc('#C9952B'), np.clip(1 - np.abs(yy - roof_y) / 2.5, 0, 1))
bl = np.zeros((Hh, W), np.float32)
for x in range(20, W, 40):
    cv2.circle(bl, (x * 4, int((roof_y + 22) * 4)), 4 * 4, 1.0, -1, cv2.LINE_AA, shift=2)
img = img + blur(bl, 7)[..., None] * hexc('#FFE08A') * 0.8
img = over(img, hexc('#FFF6D0'), bl)
save_webp(np.clip(img, 0, 1), out)
print(out)
