"""大理石：白い大理石の像（後ろ足で立つ馬）と金の台・月桂樹（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
from h3d import Scene, nrm
import horse3d as Hm
from fire2d import aces, to_srgb
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from paint import fbm, warp

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(151)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
# 背景：あたたかい白・うすい大理石のすじ
img = grad_v(Hh, W, [(0, '#F4F0E8'), (1, '#E6DFD2')])
v = np.sin(xx / 60 + yy / 35 + warp(fbm(Hh, W, 120, 4, seed=2), (fbm(Hh, W, 160, 3, seed=3) - .5) * 80, xx * 0) * 9)
vein = (1 - np.abs(v)) ** 10
img = img * (1 - 0.035 * vein[..., None])
vig = np.exp(-(((xx - 400) / 330) ** 2 + ((yy - 150) / 200) ** 2))
img = img * (0.90 + 0.10 * vig[..., None])

# 像
pose = dict(Hm.REAR)
S0 = Hm.skeleton(pose); gy = S0['ground']
sc = Scene()
sc.image(W, Hh, 2)
e, t = frame_horse(pose, (268, 10, 530, 248), W, Hh, facing='left', azim=-6, elev=8)
sc.camera(e, t, 26)
sc.bounce(1)
sc.env((0.85, 0.82, 0.78), (0.55, 0.52, 0.48), (0.25, 0.23, 0.20))
sc.lobe((0.3, 0.9, -0.4), (1.6, 1.55, 1.45), 4.0)
sc.light((0.6, 0.7, -0.6), (2.2, 2.1, 1.9), 10, 1)
sc.light((-0.7, 0.4, 0.5), (0.8, 0.8, 0.85), 8, 0)
sc.mat(1, 3, (0.95, 0.93, 0.89), 0.2, 3.2, 8.0)
sc.mat(5, 3, (0.95, 0.93, 0.89), 0.2, 3.2, 8.0)
sc.mat(6, 3, (0.95, 0.93, 0.89), 0.2, 3.2, 8.0)
sc.mat(7, 0, (1.0, 0.78, 0.40), 0.18)
S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
hx = np.mean([S['HL']['hf'][0], S['HR']['hf'][0]])
sc.rbox(np.array([hx - 0.05, gy - 0.30, 0.0]), (0.62, 0.30, 0.42), 0.03, k=0.0, mat=1)
sc.rbox(np.array([hx - 0.05, gy - 0.05, 0.0]), (0.645, 0.028, 0.445), 0.01, k=0.0, mat=7)
sc.rbox(np.array([hx - 0.05, gy - 0.56, 0.0]), (0.66, 0.035, 0.46), 0.01, k=0.0, mat=7)
R = sc.render(os.path.join(TMP, 'marble'))
rgb = to_srgb(aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None] * 1.05))
A = R['a']
sh = np.exp(-(((xx - (R['a'].sum(0).argmax())) / 140) ** 2 + ((yy - (np.nonzero(A.sum(1) > 0)[0].max())) / 8) ** 2))
img = img * (1 - 0.25 * sh[..., None])
img = over(img, rgb, A)


# 金の月桂樹（左右）
def laurel(img, cx, cy, r, a0, a1, flip):
    m = np.zeros((Hh, W), np.float32)
    stem = []
    for k in range(40):
        a = a0 + (a1 - a0) * k / 39
        stem.append((cx + math.cos(a) * r * flip, cy + math.sin(a) * r))
    stem = np.array(stem)
    cv2.polylines(m, [np.round(stem * 16).astype(np.int32)], False, 1.0, 3 * 16 // 16, cv2.LINE_AA, shift=4)
    leaves = []
    for k in range(2, 40, 3):
        p = stem[k]; d = stem[min(k + 1, 39)] - stem[k - 1]; d /= np.linalg.norm(d)
        nrm_ = np.array([-d[1], d[0]])
        for sgn in (1, -1):
            tip = p + nrm_ * sgn * 15 + d * 6
            mid = (p + tip) / 2
            q = [p, mid + nrm_ * 3 * sgn + d * 4, tip, mid - nrm_ * 2 * sgn - d * 2]
            leaves.append(np.array(q))
    m = np.maximum(m, poly_aa((Hh, W), leaves))
    gold = grad_v(Hh, W, [(0, '#F3D27A'), (0.5, '#C9952B'), (1, '#F0CF7A')])
    img = over(img, hexc('#8A6514'), np.roll(m, 1, 0) * 0.6)
    return over(img, gold, m)


img = laurel(img, 160, 170, 120, math.radians(110), math.radians(250), 1)
img = laurel(img, 620, 170, 120, math.radians(110), math.radians(250), -1)
save_webp(np.clip(img, 0, 1), out)
print(out)
