"""龍馬（りゅうま）：3Dの馬（r3d/horse3d.py）に、龍の角（金・枝分かれ）・長いひげ（金）・あごひげ・ひたいの飾り板と玉・
   首のつけねの金の輪・金のひづめ をつけ、体と首に うろこ の凹凸をつけた、一から作った創作の生きもの。
   頭と首だけを上から見て yaw 度まわして、顔を少しこちら（カメラ）へ向ける。
   たてがみ・しっぽ・足もと・背すじの炎は、flat/ryuma_banner.py で2Dの炎として重ねる（ここは体だけ）。
   build(sc, pose, yaw, mats) → 目印（3Dの点：crest・throat・poll・eyes・tailhead・hooves・muzzle・antler の先 など）"""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import horse3d as Hm
from h3d import nrm, basis

# 跳ぶ（天へかける）ポーズ：体は少し前上がり・前足は2本ともひざを曲げてたたむ・後ろ足は2本ともうしろへのばす
# 左向きで描く（カメラは -z）ので、手前の足は R
POSE = dict(theta=13.0, neck_rot=-12.0, head_ang=-30.0,
            fore=dict(R=[-58, 26, -106, -150], L=[-44, 40, -66, -104]),
            hind=dict(R=[-104, -154, -142, -160], L=[-94, -146, -132, -152]),
            tail=[-165, -150])
NEAR = -1.0


def roty(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class Yaw:
    """形を、点 piv を通る たての軸で Rw だけまわしてから sc に出す（頭と首だけに使う）"""
    def __init__(self, sc, Rw, piv):
        self.sc, self.Rw, self.piv = sc, np.asarray(Rw, float), np.asarray(piv, float)

    def p(self, q):
        return self.Rw @ (np.asarray(q, float) - self.piv) + self.piv

    def d(self, v):
        return self.Rw @ np.asarray(v, float)

    def R(self, R):
        R = np.eye(3) if R is None else np.asarray(R, float)
        return R @ self.Rw.T

    def ell(self, c, radii, R=None, **kw): self.sc.ell(self.p(c), radii, self.R(R), **kw)
    def rcone(self, a, b, ra, rb, **kw): self.sc.rcone(self.p(a), self.p(b), ra, rb, **kw)
    def sph(self, c, r, **kw): self.sc.sph(self.p(c), r, **kw)
    def rbox(self, c, half, rnd, R=None, **kw): self.sc.rbox(self.p(c), half, rnd, self.R(R), **kw)
    def torus(self, c, axis, Rb, rs, **kw): self.sc.torus(self.p(c), self.d(axis), Rb, rs, **kw)
    def ctorus(self, c, normal, mid, Rb, rs, half, **kw): self.sc.ctorus(self.p(c), self.d(normal), self.d(mid), Rb, rs, half, **kw)
    def ccone(self, a, b, ra, rb, rnd=0.0, side=(1, 0, 0), **kw): self.sc.ccone(self.p(a), self.p(b), ra, rb, rnd=rnd, side=self.d(side), **kw)
    def begin(self, *a, **kw): self.sc.begin(*a, **kw)
    def end(self): self.sc.end()


def chain(sc, pts, rad, mat, k=0.0, kg=0.012):
    sc.begin('U', kg, mat)
    for i in range(len(pts) - 1):
        sc.rcone(pts[i], pts[i + 1], rad[i], rad[i + 1], k=k, mat=mat)
    sc.end()


def bez3(P, t):
    P = np.asarray(P, float)
    t = np.asarray(t, float)[..., None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]


def antler(X, S, z, mat, seed=0):
    """龍の角：耳の前から うしろ上へのびる幹に、前上へ向く枝が3本（金）。先の点を返す"""
    rng = np.random.default_rng(seed + (1 if z > 0 else 2))
    U3, V3 = S['head_u'], S['head_v']
    HS = Hm.HEAD_SCALE
    hp = lambda s_, w_, zz=0.0: Hm.head_pt(S, s_, w_, zz)
    out = np.array([0, 0, 1.0]) * z
    b = hp(0.035, 0.055, 0.040 * z)
    d0 = nrm(-U3 * 0.50 + V3 * 0.80 + out * 0.30)
    d1 = nrm(-U3 * 0.92 + V3 * 0.30 + out * 0.12)                     # 先はうしろへ寝る
    L = 0.56 * HS
    P = [b, b + d0 * L * 0.36, b + d0 * L * 0.70 + d1 * L * 0.12, b + d0 * L * 0.55 + d1 * L * 0.55]
    n = 12
    pts = [bez3(P, u) for u in np.linspace(0, 1, n + 1)]
    rad = [0.046 * HS * (1 - 0.74 * u ** 1.1) for u in np.linspace(0, 1, n + 1)]
    chain(X, pts, rad, mat, kg=0.02)
    tips = [pts[-1]]
    for u0, Lt, lean in ((0.28, 0.22, 0.25), (0.52, 0.20, 0.05), (0.76, 0.15, -0.10)):
        q = bez3(P, u0)
        tg = nrm(bez3(P, min(u0 + 0.03, 1)) - bez3(P, max(u0 - 0.03, 0)))
        dt = nrm(V3 * 0.85 + U3 * 0.45 + out * (0.20 + rng.uniform(-0.1, 0.1)) + tg * lean)
        Q = [q, q + dt * Lt * 0.45, q + dt * Lt * 0.8 - tg * Lt * 0.05, q + dt * Lt * HS - tg * Lt * 0.15]
        m = 7
        p2 = [bez3(Q, v) for v in np.linspace(0, 1, m + 1)]
        r2 = [0.022 * HS * (1 - 0.78 * v) for v in np.linspace(0, 1, m + 1)]
        chain(X, p2, r2, mat, kg=0.015)
        tips.append(p2[-1])
    return tips


def whisker(X, S, z, mat, seed=0):
    """龍のひげ：鼻の横から うしろへ、波を打ちながら下がって流れる細い金のすじ"""
    rng = np.random.default_rng(seed + (3 if z > 0 else 4))
    U3, V3 = S['head_u'], S['head_v']
    HS = Hm.HEAD_SCALE
    hp = lambda s_, w_, zz=0.0: Hm.head_pt(S, s_, w_, zz)
    out = np.array([0, 0, 1.0]) * z
    b = hp(0.50, -0.02, 0.078 * z)
    L = 0.70
    d0 = nrm(U3 * 0.30 + out * 0.85 - V3 * 0.05)                        # 前・外へ
    d1 = nrm(-U3 * 0.20 - V3 * 0.95 + out * 0.15)                       # 下へ（あごの下をまわって、首の前にたれる）
    d2 = nrm(-U3 * 0.80 - V3 * 0.55 + out * 0.05)                       # うしろ下へ流れる
    P = [b, b + d0 * L * 0.16, b + d0 * L * 0.18 + d1 * L * 0.50, b + d0 * L * 0.10 + d1 * L * 0.55 + d2 * L * 0.55]
    n = 20
    ph = rng.uniform(0, 6.28)
    pts, rad = [], []
    for u in np.linspace(0, 1, n + 1):
        q = bez3(P, u)
        tg = nrm(bez3(P, min(u + 0.02, 1)) - bez3(P, max(u - 0.02, 0)))
        nn = np.cross(tg, out)
        q = q + nn * 0.03 * math.sin(2 * math.pi * 1.4 * u + ph) * u + out * 0.02 * math.sin(2 * math.pi * u + ph)
        pts.append(q)
        rad.append(max(0.004, 0.020 * (1 - 0.78 * u ** 1.2)))
    chain(X, pts, rad, mat, kg=0.0)
    return pts


def build(sc, pose, yaw=0.0, mats=None, seed=0):
    """龍馬の体（しっぽの根元の3Dの出っぱりは作らない：しっぽは2Dの炎）。mats: body・neck・head・hoof・eye・gold・gem"""
    M = dict(body=1, neck=2, head=1, hoof=6, eye=5, gold=7, gem=4)
    if mats:
        M.update(mats)
    th = pose['theta']
    piv2 = np.array([-0.60, 1.25])
    T = lambda p: Hm.rot2(p, piv2, th)
    nb = Hm.v3(T((0.52, 1.40)))                                           # 首のつけね（まわす軸）
    Rw = roty(yaw)
    X = Yaw(sc, Rw, nb)
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead'])
    t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rc0 = sc.rcone

    def rc(a_, b_, *args, **kw):
        if np.allclose(np.asarray(a_, float), ta0) or np.allclose(np.asarray(a_, float), t10):
            return
        return rc0(a_, b_, *args, **kw)

    nh0 = Hm._neck_head

    def nh(sc_, pose_, S_, M_):
        return nh0(X, pose_, S_, M_)                                       # 頭と首だけ まわして出す

    sc.rcone = rc
    Hm._neck_head = nh
    try:
        S = Hm.build(sc, pose, mats=dict(body=M['body'], neck=M['neck'], hoof=M['hoof'], eye=M['eye'], head=M['head']))
    finally:
        sc.rcone = rc0
        Hm._neck_head = nh0
    G = M['gold']
    U3, V3 = S['head_u'], S['head_v']
    HS = Hm.HEAD_SCALE
    hp = lambda s_, w_, zz=0.0: Hm.head_pt(S, s_, w_, zz)
    # 角・ひげ（頭といっしょに まわす）
    tips = {}
    for z in (1, -1):
        tips[z] = antler(X, S, z, G, seed)
    whisk = {z: whisker(X, S, z, G, seed) for z in (1, -1)}
    # あごひげ：あごの下に3本の短い房（金）
    for i, (dz, L_) in enumerate(((0.0, 0.11), (0.03, 0.08), (-0.03, 0.08))):
        b = hp(0.47, -0.125, dz)
        d = nrm(-U3 * 0.35 - V3 * 0.9 + np.array([0, 0, dz * 3]))
        pts = [b + d * L_ * u + (-U3) * L_ * 0.5 * u * u for u in np.linspace(0, 1, 6)]
        chain(X, pts, [0.018 * (1 - 0.8 * u) for u in np.linspace(0, 1, 6)], G, kg=0.01)
    # ひたいの飾り板と玉
    HR = basis(U3, V3)
    X.ell(hp(0.145, 0.088), (0.062 * HS, 0.010 * HS, 0.046 * HS), HR, k=0.004, mat=G)
    X.rcone(hp(0.08, 0.082), hp(0.40, 0.064), 0.010 * HS, 0.007 * HS, k=0.006, mat=G)         # 鼻すじの細い金
    X.sph(hp(0.145, 0.108), 0.024 * HS, k=0.0, mat=M['gem'])
    # 首のつけねの金の輪（首にそった うすい帯）
    a = Hm.bez(S['crest'], 0.20); b = Hm.bez(S['throat'], 0.24)
    c = (a + b) / 2
    axis = nrm(Hm.v3(np.array([-(a - b)[1], (a - b)[0]])))
    if axis[0] < 0:
        axis = -axis
    R0 = np.linalg.norm(a - b) / 2
    X.begin('U', 0.0, G)
    X.ell(Hm.v3(c), (0.05, R0 + 0.025, 0.215), basis(axis, Hm.v3(a - b)), shell=0.016, mat=G)
    X.rbox(Hm.v3(c), (0.030, 0.6, 0.6), 0.0, basis(axis, Hm.v3(a - b)), op='I', mat=G)
    X.end()
    for ang in (-1.1, -0.55, 0.0, 0.55, 1.1):                              # 輪の玉
        d_up = nrm(Hm.v3(a - b))
        p = Hm.v3(c) + d_up * math.cos(ang) * (R0 + 0.04) + np.array([0, 0, 1.0]) * math.sin(ang) * 0.235
        X.sph(p, 0.022, k=0.004, mat=G)
    # 肩と腰の金の飾り板（うすい板・輪・赤い玉）：手前がわだけ
    fx = Hm.v3(Hm.adir(th))
    for (p2, rx, ry, zz) in (((0.40, 1.36), 0.13, 0.10, 0.285), ((-0.60, 1.42), 0.12, 0.10, 0.275)):
        c3 = Hm.v3(T(p2), zz * NEAR)
        sc.ell(c3, (rx, ry, 0.030), basis(fx, (0, 1, 0)), k=0.02, mat=G)
        sc.torus(c3 + np.array([0, 0, 0.022 * NEAR]), np.array([0, 0, 1.0]), rx * 0.62, 0.011, k=0.004, mat=G)
        sc.sph(c3 + np.array([0, 0, 0.03 * NEAR]), 0.03, k=0.0, mat=M['gem'])

    # ---------- 目印（世界の3Dの点） ----------
    ts = np.linspace(0, 1, 40)
    crest = Hm.bez(S['crest'], ts); throat = Hm.bez(S['throat'], ts)
    marks = dict(
        crest=[X.p(Hm.v3(q)) for q in crest], crest_near=[X.p(Hm.v3(q, 0.07 * NEAR)) for q in crest],
        crest_far=[X.p(Hm.v3(q, -0.07 * NEAR)) for q in crest], throat=[X.p(Hm.v3(q)) for q in throat],
        poll=X.p(Hm.v3(S['poll'])), eye=X.p(hp(0.152, 0.036, 0.091 * NEAR)), eye_far=X.p(hp(0.152, 0.036, -0.091 * NEAR)),
        muzzle=X.p(hp(0.60, -0.03)), nostril=X.p(hp(0.535, 0.022, 0.05 * NEAR)), gem=X.p(hp(0.145, 0.118)),
        tailhead=Hm.v3(S['tailhead']), croup=Hm.v3(S['croup']), withers=Hm.v3(S['withers']), back=Hm.v3(S['back']), loin=Hm.v3(S['loin']),
        hooves=[Hm.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')],
        fetlocks=[Hm.v3(S[k]['ft'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')],
        antler_tips=[X.p(q) for z in (1, -1) for q in tips[z]], whiskers={z: [X.p(q) for q in whisk[z]] for z in (1, -1)},
        chest=Hm.v3(S['chest']), neck_base=nb, Rw=Rw, S=S,
    )
    return marks
