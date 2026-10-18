"""ネオンの競走馬と騎手：3Dの馬（ななめ前から）＋3Dの形で作った騎手（前かがみの乗り方）
   形はすべて一から作ったオリジナル"""
import sys, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm

# 素材の番号（線の色分けに使う）
M_SILK, M_PANTS, M_HELMET, M_BOOT, M_CLOTH = 7, 8, 9, 10, 11
MATS = [(M_SILK, 1, (0.8, 0.2, 0.5), 0.5), (M_PANTS, 1, (0.9, 0.9, 0.9), 0.5), (M_HELMET, 1, (0.8, 0.2, 0.5), 0.3),
        (M_BOOT, 1, (0.1, 0.1, 0.1), 0.4), (M_CLOTH, 1, (0.95, 0.95, 0.95), 0.6)]

POSE = dict(theta=8.0, neck_rot=-26.0, head_ang=-40.0,
            fore=dict(L=[-96, -46, -58, -36], R=[-78, 22, -98, -138]),
            hind=dict(L=[-114, -152, -134, -154], R=[-70, -114, -86, -64]),
            tail=[-162, -152])


JS = 1.0


def P3(p2, y=0.0, x=0.0, z=0.0):
    return np.array([p2[0] + x * JS, p2[1] + y * JS, z * JS], float)


def jockey(sc, S, side_z=0.30):
    """前かがみの騎手（右向きの馬の上）。S['withers'] を目安に置く。ゼッケン（白い布）も"""
    w = np.asarray(S['withers'], float)
    J = {}
    J['pelvis'] = P3(w, 0.24, -0.30)
    J['chest'] = P3(w, 0.33, 0.06)
    J['neck'] = P3(w, 0.37, 0.15)
    J['head'] = P3(w, 0.45, 0.24)
    a, b = J['pelvis'], J['chest']
    sc.ell_ax((a + b) / 2, b - a, (np.linalg.norm(b - a) / 2 + 0.07 * JS, 0.12 * JS, 0.15 * JS), up=(0, 1, 0), k=0.04, mat=M_SILK)
    sc.ell(a + np.array([0.02, -0.02, 0]) * JS, (0.13 * JS, 0.10 * JS, 0.15 * JS), k=0.05, mat=M_PANTS)                       # おしり
    sc.rcone(J['chest'], J['neck'], 0.07 * JS, 0.05 * JS, k=0.03, mat=M_SILK)
    sc.sph(J['head'], 0.095 * JS, k=0.02, mat=M_HELMET)                                                         # ヘルメット
    sc.ell(J['head'] + np.array([0.08, -0.035, 0]) * JS, (0.05 * JS, 0.012 * JS, 0.07 * JS), k=0.01, mat=M_HELMET)            # つば
    for z in (1, -1):
        sh = P3(w, 0.34, 0.06, 0.13 * z)
        el = P3(w, 0.18, 0.10, 0.21 * z)
        hd = P3(w, 0.06, 0.36, 0.10 * z)
        sc.rcone(sh, el, 0.05 * JS, 0.042 * JS, k=0.02, mat=M_SILK)          # 上の腕
        sc.rcone(el, hd, 0.04 * JS, 0.032 * JS, k=0.02, mat=M_SILK)          # 下の腕
        sc.sph(hd, 0.035 * JS, k=0.01, mat=M_PANTS)                      # 手（白い手ぶくろ）
        hip = P3(w, 0.22, -0.26, 0.12 * z)
        kn = P3(w, 0.14, 0.02, side_z * z)
        an = P3(w, -0.18, -0.18, (side_z + 0.06) * z)
        toe = P3(w, -0.22, -0.06, (side_z + 0.07) * z)
        sc.rcone(hip, kn, 0.075 * JS, 0.055 * JS, k=0.03, mat=M_PANTS)        # もも
        sc.rcone(kn, an, 0.052 * JS, 0.04 * JS, k=0.02, mat=M_BOOT)           # すね（ブーツ）
        sc.rcone(an, toe, 0.04 * JS, 0.03 * JS, k=0.01, mat=M_BOOT)           # 足
        sc.rbox(P3(w, -0.30, -0.42, 0.29 * z), (0.19, 0.13, 0.02), 0.03, k=0.02, mat=M_CLOTH)   # ゼッケン
        J[f'hand{z}'] = hd
    return J


def render_rider(box, W, Hh, azim=40, elev=6, ss=2, name='neonrider', head_scale=1.1, js=1.0, pose=None, cam=None):
    """pose：馬の形（なければ POSE）。cam：決めたカメラ (eye, tgt)（走るコマで いまの絵と同じカメラを使う）。R['cam'] に入れる"""
    global JS
    JS = js
    Hm.HEAD_SCALE = head_scale
    holder = {}
    pose = POSE if pose is None else pose

    def extra(sc, S):
        holder['J'] = jockey(sc, S)
    if cam is None:
        e, t = frame_horse(pose, box, W, Hh, facing='right', azim=azim, elev=elev)
    else:
        e, t = (np.asarray(v, float) for v in cam)
    R = render_horse(pose, e, t, 26, W, Hh, ss=ss, name=name, extra=extra, mats=MATS)
    R['J'] = holder['J']
    R['cam'] = (e, t)
    return R


if __name__ == '__main__':
    import cv2
    W, Hh = 780, 320
    az = float(sys.argv[2]) if len(sys.argv) > 2 else 40
    R = render_rider((150, 22, 470, 300), W, Hh, azim=az, js=1.15)
    m = R['m']
    col = np.zeros((Hh, W, 3), np.float32)
    pal = {1: (0.35, 0.35, 0.35), 5: (0, 0, 0), 6: (0.2, 0.2, 0.2), M_SILK: (0.9, 0.2, 0.6), M_PANTS: (0.95, 0.95, 0.95),
           M_HELMET: (1.0, 0.4, 0.7), M_BOOT: (0.1, 0.1, 0.1), M_CLOTH: (1, 1, 0.6)}
    for k, c in pal.items():
        col[np.abs(m - k) < 0.5] = c
    col *= (R['a'] > 0.5)[..., None]
    ln = edges(R, width=2, crease=0.6)
    col = np.clip(col + ln[..., None] * np.array([0.0, 0.9, 1.0]), 0, 1)
    cv2.imwrite(sys.argv[1], cv2.cvtColor((col * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    print('ok', sorted(set(np.round(np.unique(m)).astype(int).tolist()))[:20])
