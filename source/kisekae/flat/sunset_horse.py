"""夕焼けの馬：夕日を背に丘をかける馬のシルエット（左向き）
   - 体と足は3Dの馬（horse3d）を4倍の大きさで描いた形（頭は小さめ。前足を1本ついて、もう1本はたたみ、うしろ足は2本ともうしろへけり出す走り）
   - たてがみ：首の上のふち（き甲からうなじの少しうしろまで）ぜんぶから、うしろ上へなびく30の束。根元はすき間のない帯で首にのせ、
     束の先は細くとがって少しはね上がる。ところどころ先からほどける細い毛
   - しっぽ：お尻のうしろの太い根元（3Dの出っぱりは作らず、うしろ・少し上へ）から、38の束がうしろへ流れて、下の束ほどたれる。
     束はそろって波打ち、先はたくさんの細い毛にほどけて、くるっと曲がる
   - ふちの光：夕日に向いたふちに細いオレンジの光、上のふちにうすい桃色の光。夕日に重なる所は光が少しまわりこむ
   形はすべて一から作ったオリジナル。silhouette(W, Hh) → (おおう量, 夕日がわのふちの光, 上のふちの光)
   壁紙の走るコマ（flat/sunset_run.py）では、cam（カメラを決めて うごかさない）・pose（ギャロップの形）・phase（たてがみとしっぽが波打つ位相）を わたす。
   phase なしなら いつもの絵と1バイトもちがわない"""
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


def taper_poly(P, w):
    """点の列 P（1倍）と点ごとの太さ w（全幅）→ 細長い形の多角形（根元は丸く）"""
    P = np.asarray(P, float)
    tg = np.gradient(P, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    h = np.asarray(w, float)[:, None] / 2
    cap = [P[0] - (nr[0] * math.cos(a_) + tg[0] * math.sin(a_)) * h[0, 0] for a_ in np.linspace(0, math.pi, 9)[1:-1]]
    return np.vstack([P + nr * h, (P - nr * h)[::-1], np.array(cap)])


def fill(mask4, poly):
    cv2.fillPoly(mask4, [np.round(np.asarray(poly) * S4 * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)


def rot(v, deg):
    a_ = math.radians(deg)
    return np.array([v[0] * math.cos(a_) - v[1] * math.sin(a_), v[0] * math.sin(a_) + v[1] * math.cos(a_)])


def resample(P, n):
    P = np.asarray(P, float)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    t = np.linspace(0, L[-1], n)
    return np.stack([np.interp(t, L, P[:, 0]), np.interp(t, L, P[:, 1])], 1)


def render_nodock(pose, eye, tgt, fov, W, Hh, name='sunset_sil'):
    """style2d.render_horse と同じ形で、しっぽの根元の3Dの出っぱりだけ作らない（しっぽは毛の束で描く）"""
    from h3d import Scene
    sc = Scene()
    sc.image(W, Hh, 1)
    sc.camera(np.asarray(eye, float), np.asarray(tgt, float), fov)
    sc.bounce(0)
    sc.env((0.5, 0.5, 0.5), (0.4, 0.4, 0.4), (0.2, 0.2, 0.2))
    sc.light((0.5, 0.8, 0.6), (2.0, 2.0, 2.0), 10, 1)
    sc.mat(1, 1, (0.6, 0.6, 0.6), 0.6)
    sc.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    sc.mat(6, 1, (0.3, 0.3, 0.3), 0.6)
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead'])
    t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rc0 = sc.rcone

    def rc(a_, b_, *args, **kw):
        if np.allclose(np.asarray(a_, float), ta0) or np.allclose(np.asarray(a_, float), t10):
            return
        return rc0(a_, b_, *args, **kw)

    sc.rcone = rc
    S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    sc.rcone = rc0
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['throat'] = P(np.c_[Hm.bez(S['throat'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['tailhead'] = P([Hm.v3(S['tailhead'])])[0]
    R['croup'] = P([Hm.v3(S['croup'])])[0]
    R['S'], R['scene'] = S, sc
    return R


def camera(W, Hh, pose=POSE, box=BOX):
    """いつもの絵のカメラ（馬が box にちょうど入る）"""
    Hm.HEAD_SCALE = 1.0
    return frame_horse(pose, tuple(v * S4 for v in box), W * S4, Hh * S4, facing='left', azim=0, elev=2)


def silhouette(W, Hh, seed=11, pose=POSE, box=BOX, cam=None, phase=None, name='sunset_sil'):
    rng = np.random.default_rng(seed)
    Hm.HEAD_SCALE = 1.0
    e, t = camera(W, Hh, pose, box) if cam is None else cam
    R = render_nodock(pose, e, t, 26, W * S4, Hh * S4, name=name)
    a4 = R['a']
    hair = np.zeros(a4.shape, np.uint8)
    H3, W3 = a4.shape

    def ins(p):
        xi, yi = int(p[0] * S4), int(p[1] * S4)
        return 0 <= xi < W3 and 0 <= yi < H3 and a4[yi, xi] >= 0.5

    # ================= たてがみ：首の上のふち（き甲 → うなじ）ぜんぶから、うしろ上へなびく束 =================
    crest = np.asarray(R['crest'], float) / S4                         # き甲 → うなじ
    throat = np.asarray(R['throat'], float) / S4
    tp, nn = [], []
    for i in range(len(crest)):
        c = crest[i]
        tg = crest[min(len(crest) - 1, i + 1)] - crest[max(0, i - 1)]
        n_ = unit([tg[1], -tg[0]])
        if np.dot(throat[i] - c, n_) > 0:
            n_ = -n_
        p = c.copy()
        for _ in range(240):                                            # 首の上のふちまで出る
            q = p + n_ * 0.25
            if not ins(q):
                break
            p = q
        tp.append(p); nn.append(n_)
    tp = resample(np.array(tp), 80)
    tp = np.stack([np.convolve(np.r_[np.full(4, tp[0, j]), tp[:, j], np.full(4, tp[-1, j])], np.ones(9) / 9, 'valid') for j in (0, 1)], 1)
    tg = np.gradient(tp, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nn = np.stack([tg[:, 1], -tg[:, 0]], 1)                              # 外向き（上）
    if nn[len(nn) // 2, 1] > 0:
        nn = -nn
    top = lambda f: tp[int(np.clip(round(f * (len(tp) - 1)), 0, len(tp) - 1))]
    nor = lambda f: nn[int(np.clip(round(f * (len(nn) - 1)), 0, len(nn) - 1))]
    flow = unit([1.0, -0.32])                                           # 風：うしろ（右）へ、少し上へ
    if phase is not None:                                               # 走るコマ：風の向きが少しゆれる
        flow = rot(flow, 3.0 * math.sin(phase))
    # 根元のまとまり（首の上にのる、すき間のない帯）
    fs = np.linspace(0.0, 0.92, 60)
    hgt = 3.2 * np.sin(np.pi * np.clip(fs / 0.92, 0, 1)) ** 0.6
    inner = np.array([top(f) - nor(f) * 2.5 for f in fs])
    outer = np.array([top(f) + nor(f) * h for f, h in zip(fs, hgt)])
    fill(hair, np.vstack([inner, outer[::-1]]))
    locks = []
    NM = 30
    for k in range(NM):
        f = (k + rng.uniform(0.15, 0.85)) / NM * 0.90 + 0.02             # 0：き甲 … 0.92：うなじの少しうしろ（耳はよける）
        n_ = nor(f)
        root = top(f) - n_ * 2.0
        prof = 0.45 + 0.55 * math.sin(math.pi * (0.22 + 0.80 * f)) ** 0.7   # き甲がわから首のまんなかが長い
        L = 27.0 * prof * rng.uniform(0.80, 1.22)
        d0 = unit(n_ * 1.0 + flow * 0.70)
        d1 = rot(unit(flow + n_ * 0.20), rng.uniform(-8, 8))
        d2 = rot(d1, -rng.uniform(4, 22))                                # 先は少しはね上がる
        p1 = root + d0 * L * 0.32
        p2 = p1 + d1 * L * 0.38
        p3 = p2 + d2 * L * 0.36
        P = bez3(root, p1, p2, p3, 44)
        tt = np.linspace(0, 1, len(P))
        tq = np.gradient(P, axis=0)
        tq /= np.linalg.norm(tq, axis=1, keepdims=True) + 1e-9
        nq = np.stack([-tq[:, 1], tq[:, 0]], 1)
        a_, k_, p_ = rng.uniform(0.6, 1.5), rng.uniform(1.2, 2.2), rng.uniform(0, 6)
        if phase is not None:                                           # 走るコマ：束が波打つ（1回で1周）
            p_ = p_ + phase
        P = P + nq * (a_ * np.sin(tt * math.pi * k_ + p_) * tt)[:, None]
        w = rng.uniform(4.2, 6.2) * (1 - tt) ** 0.85 + 0.22
        fill(hair, taper_poly(P, w))
        locks.append((P, L))
    for _ in range(9):                                                  # 先からほどける細い毛
        P, L = locks[rng.integers(len(locks))]
        j = int(len(P) * rng.uniform(0.45, 0.75))
        d = rot(unit(P[j + 1] - P[j - 1]), rng.uniform(-22, 10))
        Lw = L * rng.uniform(0.40, 0.65)
        Q = bez3(P[j], P[j] + d * Lw * 0.35, P[j] + rot(d, rng.uniform(-15, 15)) * Lw * 0.7, P[j] + rot(d, rng.uniform(-25, 10)) * Lw, 24)
        fill(hair, taper_poly(Q, 1.3 * (1 - np.linspace(0, 1, 24)) ** 0.8 + 0.12))

    # ================= しっぽ：お尻のうしろの根元から、うしろへ流れて、先がたくさんの細い毛にほどける =================
    th = np.asarray(R['tailhead'], float) / S4
    dock_dir = unit([1.0, -0.22])                                       # 根元は うしろ・少し上へ
    p = th.copy()
    for _ in range(400):
        q = p + dock_dir * 0.25
        if not ins(q):
            break
        p = q
    base = p - dock_dir * 5.0
    dock = bez3(base, base + dock_dir * 8, base + dock_dir * 15 + np.array([0, 0.5]), base + dock_dir * 21 + np.array([0, 2.0]), 30)
    fill(hair, taper_poly(dock, np.linspace(10.5, 8.0, len(dock))))
    dk_t = np.gradient(dock, axis=0)
    dk_t /= np.linalg.norm(dk_t, axis=1, keepdims=True) + 1e-9
    dk_n = np.stack([-dk_t[:, 1], dk_t[:, 0]], 1)                       # 下向き
    if dk_n[len(dk_n) // 2, 1] < 0:
        dk_n = -dk_n
    tlocks = []
    NT = 38
    ph0 = 0.6 if phase is None else 0.6 + phase                         # 走るコマ：しっぽが波打つ（1回で1周）
    swing = 0.0 if phase is None else 4.0 * math.sin(phase - 1.2)      # 走るコマ：しっぽ全体が少し上下にゆれる
    for k in range(NT):
        f = (k + rng.uniform(0.1, 0.9)) / NT                            # 0：上 … 1：下
        j = int(rng.uniform(0.25, 0.98) * (len(dock) - 1))
        root = dock[j] + dk_n[j] * (f - 0.5) * 6.0
        L = 120.0 * (0.70 + 0.40 * math.sin(math.pi * f)) * rng.uniform(0.85, 1.12)
        d_in = rot(dock_dir, (f - 0.5) * 34 + rng.uniform(-4, 4))
        d_out = rot(unit([1.0, 0.14 + 0.30 * f]), rng.uniform(-5, 5))  # 下の毛ほどたれる
        if phase is not None:
            d_in, d_out = rot(d_in, swing * 0.6), rot(d_out, swing)
        p1 = root + d_in * L * 0.28
        p2 = p1 + d_out * L * 0.40
        p3 = p2 + rot(d_out, rng.uniform(-12, 20)) * L * 0.32
        P = bez3(root, p1, p2, p3, 90)
        tt = np.linspace(0, 1, len(P))
        tq = np.gradient(P, axis=0)
        tq /= np.linalg.norm(tq, axis=1, keepdims=True) + 1e-9
        nq = np.stack([-tq[:, 1], tq[:, 0]], 1)
        amp = 5.6 * rng.uniform(0.8, 1.2)
        P = P + nq * (amp * np.sin(tt * math.pi * 2.3 + ph0 + 0.7 * f + rng.uniform(-0.25, 0.25)) * tt ** 1.1)[:, None]   # そろって波打つ
        w = rng.uniform(4.8, 7.4) * (1 - tt) ** 0.72 + 0.20
        fill(hair, taper_poly(P, w))
        tlocks.append((P, L))
    for _ in range(18):                                                 # 先でほどけて、くるっと曲がる細い毛
        P, L = tlocks[rng.integers(len(tlocks))]
        j = int(len(P) * rng.uniform(0.50, 0.82))
        d = rot(unit(P[j + 1] - P[j - 1]), rng.uniform(-24, 24))
        Lw = L * rng.uniform(0.22, 0.42)
        bend = rng.uniform(-40, 40)
        Q = bez3(P[j], P[j] + d * Lw * 0.35, P[j] + rot(d, bend * 0.5) * Lw * 0.7, P[j] + rot(d, bend) * Lw, 30)
        fill(hair, taper_poly(Q, 1.5 * (1 - np.linspace(0, 1, 30)) ** 0.8 + 0.12))
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
