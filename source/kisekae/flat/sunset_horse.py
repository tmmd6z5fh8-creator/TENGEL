"""夕焼けの馬：夕日を背に丘をかける馬のシルエット（左向き）
   - 体と足は3Dの馬（horse3d）を4倍の大きさで描いた形（頭は小さめ。前足を1本ついて、もう1本はたたみ、うしろ足は2本ともうしろへけり出す走り）
   - たてがみ・前髪・しっぽは、細い毛の束をたくさん重ねて、先が風にほどける形（根元はまとまり、先は1本ずつ細く）
   - ふちの光：夕日に向いたふちに細いオレンジの光、上のふちにうすい桃色の光。夕日に重なる所は光が少しまわりこむ
   形はすべて一から作ったオリジナル。silhouette(W, Hh) → (おおう量, 夕日がわのふちの光, 上のふちの光)"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm

S4 = 4
POSE = dict(theta=-1.0, neck_rot=-28.0, head_ang=-42.0,                 # 前足を1本ついて、もう1本はたたみ、うしろ足は2本ともうしろへけり出す
            fore=dict(L=[-92, -82, -88, -62], R=[-100, 0, -120, -150]),
            hind=dict(L=[-120, -160, -135, -150], R=[-108, -150, -122, -140]),
            tail=[-150, -140])
BOX = (186, 50, 556, 244)
SUN = (520.0, 236.0)


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


def bez3(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def strand_poly(P, w0, w1=0.15, tip=1.0):
    """毛の束：根元 w0 → 先 w1 の太さの細長い形（1倍の座標の点の列 → 多角形）"""
    P = np.asarray(P, float)
    tg = np.gradient(P, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    t = np.linspace(0, 1, len(P))
    w = (w0 + (w1 - w0) * t ** tip) / 2
    return np.vstack([P + nr * w[:, None], (P - nr * w[:, None])[::-1]])


def fill(mask4, poly):
    cv2.fillPoly(mask4, [np.round(np.asarray(poly) * S4 * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)


def silhouette(W, Hh, seed=11, pose=POSE, box=BOX):
    rng = np.random.default_rng(seed)
    Hm.HEAD_SCALE = 1.0
    e, t = frame_horse(pose, tuple(v * S4 for v in box), W * S4, Hh * S4, facing='left', azim=0, elev=2)
    R = render_horse(pose, e, t, 26, W * S4, Hh * S4, ss=1, name='sunset_sil')
    a4 = R['a']
    hair = np.zeros(a4.shape, np.uint8)
    H3, W3 = a4.shape

    def ins(p):
        xi, yi = int(p[0] * S4), int(p[1] * S4)
        return 0 <= xi < W3 and 0 <= yi < H3 and a4[yi, xi] >= 0.5

    crest = np.asarray(R['crest'], float) / S4                         # き甲 → うなじ
    throat = np.asarray(R['throat'], float) / S4
    poll = np.asarray(R['poll'], float) / S4
    back = unit(crest[0] - crest[-1])                                   # うなじ → き甲（うしろ）
    # ---- たてがみ：首の上のふちから、うしろ上へなびく束
    tops = []
    for i in range(len(crest)):
        c = crest[i]
        tg = crest[min(len(crest) - 1, i + 1)] - crest[max(0, i - 1)]
        n_ = unit([tg[1], -tg[0]])
        if np.dot(throat[i] - c, n_) > 0:
            n_ = -n_
        p = c.copy()
        for _ in range(200):
            q = p + n_ * 0.25
            if not ins(q):
                break
            p = q
        tops.append((p - n_ * 1.2, n_))
    def lock(spine, n_strands, spread, w0, lmin=0.65, wav=1.2, wisp=0.5):
        """束：背骨の線にそって、何本もの毛が先へ少しずつ広がる"""
        tg = np.gradient(spine, axis=0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
        t = np.linspace(0, 1, len(spine))
        for j in range(n_strands):
            o = rng.uniform(-1, 1)
            lf = rng.uniform(lmin, 1.0)
            m = t <= lf
            tt = t[m] / lf
            off = o * spread(t[m]) + np.sin(tt * math.pi * rng.uniform(1.2, 2.4) + rng.uniform(0, 6)) * wav * rng.uniform(0.4, 1.0) * tt
            P = spine[m] + nr[m] * off[:, None]
            if len(P) < 4:
                continue
            fill(hair, strand_poly(P, w0 * rng.uniform(0.7, 1.15), 0.10, tip=0.7))
            if rng.random() < wisp:                                     # 先でほどける細い毛
                k0 = int(len(P) * rng.uniform(0.55, 0.8))
                q0 = P[k0]
                d2 = unit(tg[m][k0] + nr[m][k0] * rng.uniform(-0.45, 0.45))
                Lw = np.linalg.norm(P[-1] - P[k0]) * rng.uniform(0.7, 1.2) + 3
                Q = bez3(q0, q0 + d2 * Lw * 0.3, q0 + d2 * Lw * 0.65 + nr[m][k0] * rng.uniform(-3.0, 3.0), q0 + d2 * Lw, 24)
                tq = np.linspace(0, 1, len(Q))[:, None]
                Q = Q + nr[m][k0] * np.sin(tq * math.pi * rng.uniform(1.5, 3.0) + rng.uniform(0, 6)) * rng.uniform(0.8, 2.0) * tq   # くるっと波打つ
                fill(hair, strand_poly(Q, 0.9, 0.06))

    NL = 11
    for k in range(NL):
        f = k / (NL - 1)                                                # 0：き甲 … 1：うなじの少しうしろ（耳とは輪にしない）
        i = int(round((0.05 + 0.80 * f) * (len(tops) - 1)))
        p0, n_ = tops[i]
        L = (30 + 26 * math.sin(math.pi * min(1.0, 0.2 + 0.9 * f))) * rng.uniform(0.85, 1.15)
        droop = rng.uniform(3, 9)
        rise = 0.30 if f < 0.75 else 0.16
        sp = bez3(p0, p0 + n_ * L * rise + back * L * 0.15, p0 + back * L * 0.62 + n_ * L * (0.16 + 0.08 * f),
                  p0 + back * L * 1.0 + n_ * L * 0.04 + np.array([0, droop]), 50)
        lock(sp, 7, lambda tt: 0.8 + 5.0 * tt ** 1.1, 3.2, wav=1.6, wisp=0.6)
    # 前髪（風でうしろへ）
    hu = unit(np.asarray(R['muzzle'], float) / S4 - poll)
    for k in range(4):
        p0 = poll + hu * (2.0 + k * 1.2) + rng.normal(0, 0.3, 2)
        dv = unit(-hu * 0.85 + back * 0.15)
        L = rng.uniform(7, 11)
        P = bez3(p0, p0 + dv * L * 0.3, p0 + dv * L * 0.7 + np.array([0, rng.uniform(-1.5, 1.5)]), p0 + dv * L, 20)
        fill(hair, strand_poly(P, rng.uniform(1.8, 2.6), 0.1))
    # ---- しっぽ：お尻のうしろから、うしろへ流れて先がほどける
    tl = np.asarray(R['tail'], float) / S4
    root = tl[0]
    d0 = unit(tl[-1] - tl[0])
    p = root.copy()
    for _ in range(200):
        q = p + d0 * 0.25
        if not ins(q):
            break
        p = q
    root = p - d0 * 2.5
    # 背骨：根元から少し上がって、うしろへ流れ、先は少し下がる（ゆるく波打つ）
    sp = bez3(root, root + unit(d0 * 0.4 + np.array([0.6, -0.8])) * 22, root + np.array([72, -8]), root + np.array([130, 14]), 90)
    tt = np.linspace(0, 1, len(sp))[:, None]
    sp = sp + np.array([0, 1.0]) * np.sin(tt * math.pi * 1.8 + 0.4) * 4.0 * tt
    fill(hair, strand_poly(sp[:26], 10.0, 6.0, tip=1.0))                # 根元のまとまり
    lock(sp, 36, lambda t_: 2.0 + 10.5 * t_ ** 0.9, 3.4, lmin=0.62, wav=2.8, wisp=0.6)
    lock(sp, 14, lambda t_: 3.0 + 14.0 * t_ ** 0.85, 1.5, lmin=0.78, wav=3.4, wisp=0.8)    # 外がわの細い毛
    A4 = np.maximum(a4, hair.astype(np.float32) / 255)
    A = cv2.resize(A4, (W, Hh), interpolation=cv2.INTER_AREA)
    # ---- ふちの光
    Ab = cv2.GaussianBlur(A, (0, 0), 1.1)
    gx = cv2.Sobel(Ab, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(Ab, cv2.CV_32F, 0, 1, ksize=3)
    gm = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    nx, ny = -gx / gm, -gy / gm                                         # 外向き
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    sx, sy = SUN[0] - xx, SUN[1] - yy
    sd = np.sqrt(sx ** 2 + sy ** 2) + 1e-6
    face_sun = np.clip(nx * sx / sd + ny * sy / sd, 0, 1)
    band = np.clip(A - cv2.erode(A, np.ones((3, 3), np.uint8)), 0, 1)      # ふちの内がわ1画素
    band = np.maximum(band, np.clip(A - cv2.GaussianBlur(A, (0, 0), 0.9), 0, 1) * 1.5)
    near_sun = np.exp(-sd / 150.0)
    rim_sun = np.clip(band * np.clip((face_sun - 0.25) / 0.75, 0, 1) ** 2.0 * near_sun * 2.2, 0, 1) * A
    rim_top = np.clip(band * np.clip((-ny - 0.55) / 0.45, 0, 1) ** 2 * 0.6, 0, 1) * A
    return A, rim_sun, rim_top, R


def draw(img, W, Hh):
    A, rim_sun, rim_top, R = silhouette(W, Hh)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    img = over(img, hexc('#22102C'), A)
    # 夕日に重なる所：光が少しまわりこむ（ふちが明るく、うすくぼける）
    sun = soft_circle(Hh, W, SUN[0], SUN[1], 64, 1.2)
    wrap = cv2.GaussianBlur(sun * (1 - A), (0, 0), 1.4) * A
    img = img + wrap[..., None] * hexc('#FFC27A') * 0.42
    img = over(img, hexc('#FFB45A'), rim_sun * 0.95)
    img = over(img, hexc('#FF8E7A'), rim_top * 0.55)
    return img
