"""チェス：市松の盤の上の、白い大理石と黒いつやのナイト（馬の駒）（780×320）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
from h3d import Scene, nrm, load, basis
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)


def knight(name, mat_line, size):
    """ナイトの駒：馬の首から上＋丸い台。透明の背景で描いて (rgb, a) を返す"""
    pose = dict(Hm.STAND); pose['head_ang'] = -62.0; pose['neck_rot'] = 8.0
    S = Hm.skeleton(pose)
    nb = (Hm.bez(S['crest'], 0.30) + Hm.bez(S['throat'], 0.30)) / 2
    ycut = nb[1] - 0.02
    cx = nb[0] + 0.05
    sc = Scene()
    w, h = size
    sc.image(w, h, 2)
    tgt = np.array([cx + 0.18, ycut + 0.22, 0.0])
    eye = tgt + nrm(np.array([0.12, 0.22, 1.0])) * 4.0
    sc.camera(eye, tgt, 26)
    sc.bounce(1)
    sc.env((0.30, 0.30, 0.32), (0.16, 0.16, 0.17), (0.05, 0.05, 0.05))
    sc.lobe((0.6, 0.7, 0.4), (2.6, 2.5, 2.3), 12.0)
    sc.lobe((-0.7, 0.3, -0.6), (1.2, 1.2, 1.3), 6.0)
    sc.light((-0.45, 0.75, 0.55), (2.4, 2.3, 2.1), 12, 1)
    sc.light((0.6, 0.4, -0.7), (1.2, 1.2, 1.4), 8, 0)
    sc.raw(mat_line)
    sc.mat(5, 1, (0.01, 0.01, 0.01), 0.1)
    Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=1, eye=1, head=1), parts='bust')
    # 首の下を水平に切る
    sc.rbox(np.array([cx, ycut - 1.0, 0.0]), (2.0, 1.0, 2.0), 0.0, op='S', k=0.0, mat=1)
    # 台（えり・輪・円盤）
    sc.ccone(np.array([cx, ycut - 0.20, 0]), np.array([cx, ycut + 0.02, 0]), 0.30, 0.25, rnd=0.02, k=0.04, mat=1)
    sc.torus(np.array([cx, ycut - 0.22, 0]), (0, 1, 0), 0.31, 0.035, k=0.02, mat=1)
    sc.ccone(np.array([cx, ycut - 0.40, 0]), np.array([cx, ycut - 0.24, 0]), 0.44, 0.36, rnd=0.03, k=0.03, mat=1)
    sc.torus(np.array([cx, ycut - 0.42, 0]), (0, 1, 0), 0.43, 0.03, k=0.02, mat=1)
    R = sc.render(os.path.join(TMP, name))
    from fire2d import aces, to_srgb
    rgb = to_srgb(aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None] * 1.2))
    return rgb, R['a']


wr, wa = knight('kw', 'mat 1 3 0.93 0.91 0.87 0.16 4.0 8.0 0', (300, 320))
br, ba = knight('kb', 'mat 1 1 0.012 0.012 0.014 0.10 0.30 0.55 5.0', (300, 320))
# 背景：暗い部屋＋市松の盤（遠近）
img = grad_v(Hh, W, [(0, '#1B1C22'), (0.45, '#2C2D35'), (1, '#121217')])
hz = 120
board = np.zeros((Hh, W, 3), np.float32)
dy_ = np.maximum(yy - hz, 0.5)
X = (xx - W / 2) * 43 / dy_
Z = 43 * 600 / dy_
chk = ((np.floor(X / 26) + np.floor(Z / 26)) % 2 == 0)
light_sq = hexc('#E9E5DC'); dark_sq = hexc('#34343C')
board = np.where(chk[..., None], light_sq, dark_sq)
fade = np.clip((yy - hz) / 60, 0, 1)
board = board * (0.55 + 0.45 * fade[..., None])
img = over(img, board, (yy > hz).astype(np.float32))


def put(img, rgb, a, x, y, s, refl=0.22):
    h, w = a.shape
    rgb2 = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    a2 = cv2.resize(a, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    ys, xs = np.nonzero(a2 > 0.5)
    base = ys.max()
    layer = np.zeros((Hh, W, 3), np.float32); la = np.zeros((Hh, W), np.float32)
    x0, y0 = int(x - a2.shape[1] / 2), int(y - base)
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + a2.shape[1]), min(Hh, y0 + a2.shape[0])
    layer[ya:yb, xa:xb] = rgb2[ya - y0:yb - y0, xa - x0:xb - x0]
    la[ya:yb, xa:xb] = a2[ya - y0:yb - y0, xa - x0:xb - x0]
    # 影と映り込み
    sh = np.exp(-(((xx - x) / (a2.shape[1] * 0.28)) ** 2 + ((yy - y - 2) / 7) ** 2))
    img = img * (1 - 0.5 * sh[..., None])
    rl = np.flipud(la); rr = np.flipud(layer)
    shift = int(2 * y - Hh + 1)
    rl = np.roll(rl, shift, 0); rr = np.roll(rr, shift, 0)
    rl[:int(y)] = 0
    img = over(img, rr, rl * refl * np.clip(1 - (yy - y) / 70, 0, 1))
    return over(img, layer, la)


img = put(img, np.ascontiguousarray(br[:, ::-1]), np.ascontiguousarray(ba[:, ::-1]), 548, 250, 0.74)
img = put(img, wr, wa, 270, 304, 0.98)
save_webp(np.clip(img, 0, 1), out)
print(out)
