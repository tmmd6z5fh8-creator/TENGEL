"""ナイター：照明に照らされた夜のコースを走る3頭（騎手つき）（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(101)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = grad_v(Hh, W, [(0, '#090C24'), (0.55, '#1E1B4B'), (0.62, '#2A2A5E'), (1, '#1A1A33')])
# 遠くのスタンド（光の粒）
stand = np.clip((yy - (150 - 18 * np.exp(-((xx - 390) / 300) ** 2))) / 1.5 + .5, 0, 1) * (yy < 190)
img = over(img, hexc('#14163A'), stand)
for i in range(500):
    x = rng.uniform(0, W); y = rng.uniform(138, 186)
    if stand[int(y), int(x)] > .5:
        img[int(y), int(x)] = img[int(y), int(x)] * 0.3 + hexc(['#FFE7A8', '#FFFFFF', '#A8C8FF'][rng.integers(0, 3)]) * 0.7
# 照明の塔
for tx, ty in [(70, 40), (720, 34), (390, 20)]:
    cv2.line(img, (int(tx), int(ty)), (int(tx), 190), (0.08, 0.08, 0.16), 4)
    lamp = np.zeros((Hh, W), np.float32)
    for i in range(3):
        for j in range(5):
            cv2.circle(lamp, (int((tx - 16 + j * 8) * 4), int((ty - 8 + i * 7) * 4)), int(3 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    lamp = np.clip(lamp, 0, 1)
    img = img + blur(lamp, 18)[..., None] * hexc('#BFD4FF') * 1.1 + blur(lamp, 60)[..., None] * hexc('#7F8BFF') * 0.5
    img = np.maximum(img, lamp[..., None])
    # 光の筋
    ang = np.arctan2(yy - ty, xx - tx)
    rays = (np.sin(ang * 22) > 0.85) * np.exp(-np.sqrt((xx - tx) ** 2 + (yy - ty) ** 2) / 120) * 0.2
    img = img + rays[..., None] * hexc('#DCE6FF')
# コース（ダート）と白い柵
track_top = 196 + 0 * xx
img = over(img, hexc('#4A3426'), np.clip((yy - 196) / 1.5 + .5, 0, 1))
img = img + (np.exp(-((yy - 230) / 40) ** 2) * 0.25)[..., None] * hexc('#C9B8FF') * (yy > 196)[..., None]
for ry in (194, 300):
    cv2.line(img, (0, ry), (W, ry), (0.95, 0.96, 1.0), 2, cv2.LINE_AA)
    for x in range(0, W, 26):
        cv2.line(img, (x, ry), (x, ry + 10), (0.85, 0.86, 0.95), 2, cv2.LINE_AA)
img = np.clip(img, 0, 1)
# 3頭（右向き）・奥から手前へ
pose = dict(Hm.GALLOP)
for k, (box, jc, pat, pc, cap, body) in enumerate([
        ((470, 110, 640, 232), '#E02424', 'hoops', '#FFFFFF', '#FFFFFF', ('#3A2416', '#1E120B')),
        ((70, 120, 270, 262), '#0F9D58', 'check', '#FFFFFF', '#FFC400', ('#6E4126', '#3A2010')),
        ((250, 104, 520, 300), '#1A3FB8', 'diamond', '#FFC400', '#E02424', ('#8A4A24', '#4A2410'))]):
    post = lambda rgb, R: leg_points(rgb, R, '#1A120E', height=0.40)
    rgb, a, R = horse_illust(pose, box, W, Hh, facing='right', azim=8, elev=4, body=body, mane=('#140D0A', '#0A0605'), line='#08060A',
                             mode='flow', hoof='#111', eye='#050303', mane_scale=1.15, seed=20 + k, name=f'nr{k}', post=post,
                             light=(-0.2, 0.9, 0.4), bands=(0.25, 0.8), hi='#C9D6FF')
    jr, ja = jockey(R, (Hh, W), jacket=jc, pattern=pat, pcol=pc, cap=cap)
    dark = 0.75 if k == 0 else (0.88 if k == 1 else 1.0)
    img = ground_shadow(img, R, k=0.3, w=110, h=6)
    img = over(img, rgb * dark, a)
    img = over(img, jr * dark, ja)
save_webp(img, out)
print(out)
