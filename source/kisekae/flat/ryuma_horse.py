"""龍馬（りゅうま）第2版：まさちゃんが送った龍馬の像の「形」（龍の頭・口を開けた牙・うろこの体・のどの板・金の飾り板・
   前足を上げた立ち方・流れるたてがみとしっぽ）に寄せて、一から作った創作の生きもの。参考の絵そのものは使っていない。
   - 体・首・足：3Dの馬（r3d/horse3d.py）。頭は馬の頭を出さず、ここで龍の頭を組み立てる
     （長い鼻すじ・開いた口と牙・まゆ・ほお・うしろへ曲がる角（節つき）・耳・ほおのひれ・ひげ・あごひげ）
   - のどと胸の板（象牙色）・肩と腰の金の飾り板（彫り模様）・背すじの小さなひれ・金のひづめ
   - 頭と首だけを上から見て yaw 度まわして、顔をこちら（カメラ）へ向ける
   たてがみ・しっぽ・足もとの毛は flat/ryuma_banner.py で2Dの銀色の房として重ねる（ここは体だけ）。
   build(sc, pose, yaw, mats) → 目印（3Dの点）"""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import horse3d as Hm
from h3d import nrm, basis

# 前足を上げて立つ（参考の像と同じ立ち方）：左向きで描く（カメラは -z）ので、手前の足は R
POSE = dict(theta=9.0, neck_rot=8.0, head_ang=-30.0,
            fore=dict(R=[-84, -4, -96, -134], L=[-123, -92, -90, -62]),
            hind=dict(R=[-55, -112, -88, -60], L=[-66, -122, -95, -64]),
            tail=[-150, -120])
NEAR = -1.0


def roty(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class Yaw:
    """形を、点 piv を通る たての軸で Rw だけまわしてから sc に出す（頭と首だけに使う）。mat が skip のものは出さない"""
    def __init__(self, sc, Rw, piv, skip=()):
        self.sc, self.Rw, self.piv, self.skip = sc, np.asarray(Rw, float), np.asarray(piv, float), set(skip)

    def p(self, q):
        return self.Rw @ (np.asarray(q, float) - self.piv) + self.piv

    def d(self, v):
        return self.Rw @ np.asarray(v, float)

    def R(self, R):
        R = np.eye(3) if R is None else np.asarray(R, float)
        return R @ self.Rw.T

    def ok(self, kw):
        return kw.get('mat', 0) not in self.skip

    neck_scale = (1.0, 1.0)                                                # 首の楕円の（上下, 幅）の倍率

    def ell(self, c, radii, R=None, **kw):
        if not self.ok(kw):
            return
        radii = np.asarray(radii, float)
        k = kw.get('k', 0.0)
        if (abs(k - 0.12) < 1e-9 or abs(k - 0.16) < 1e-9) and (abs(radii[0] - 0.07) < 1e-9 or abs(radii[0] - 0.06) < 1e-9):
            radii = radii * np.array([1.0, self.neck_scale[0], self.neck_scale[1]])    # 首を太く
        self.sc.ell(self.p(c), tuple(radii), self.R(R), **kw)
    def rcone(self, a, b, ra, rb, **kw):
        if self.ok(kw): self.sc.rcone(self.p(a), self.p(b), ra, rb, **kw)
    def sph(self, c, r, **kw):
        if self.ok(kw): self.sc.sph(self.p(c), r, **kw)
    def rbox(self, c, half, rnd, R=None, **kw):
        if self.ok(kw): self.sc.rbox(self.p(c), half, rnd, self.R(R), **kw)
    def torus(self, c, axis, Rb, rs, **kw):
        if self.ok(kw): self.sc.torus(self.p(c), self.d(axis), Rb, rs, **kw)
    def ctorus(self, c, normal, mid, Rb, rs, half, **kw):
        if self.ok(kw): self.sc.ctorus(self.p(c), self.d(normal), self.d(mid), Rb, rs, half, **kw)
    def ccone(self, a, b, ra, rb, rnd=0.0, side=(1, 0, 0), **kw):
        if self.ok(kw): self.sc.ccone(self.p(a), self.p(b), ra, rb, rnd=rnd, side=self.d(side), **kw)
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


def dragon_head(X, S, M, seed=0):
    """龍の頭（頭の座標：s＝うなじから鼻先へ・w＝上・z＝横）。目印を返す
       箱のように深い鼻先・上を向いた大きな鼻・めくれた上くちびると牙・大きく開いた下あご・張り出したまゆ・うしろへ流れる枝つきの角"""
    HD, HORN, EY, TEETH, MOUTH, FIN = M['head'], M['horn'], M['eye'], M['teeth'], M['mouth'], M['fin']
    HS = Hm.HEAD_SCALE
    U3, V3 = S['head_u'], S['head_v']
    hp = lambda s_, w_, z=0.0: Hm.head_pt(S, s_, w_, z)
    out3 = np.array([0, 0, 1.0])

    def hdir(rot):
        a = math.radians(rot)
        return U3 * math.cos(a) + V3 * math.sin(a), -U3 * math.sin(a) + V3 * math.cos(a)

    def E(s_, w, z, r, k, op='U', rot=0.0, mat=HD):
        dx, dy = hdir(rot)
        X.ell(hp(s_, w, z), tuple(x * HS for x in r), basis(dx, dy), op=op, k=k, mat=mat)

    def RB(s_, w, z, half, rnd, k, rot=0.0, op='U', mat=HD):
        dx, dy = hdir(rot)
        X.rbox(hp(s_, w, z), tuple(x * HS for x in half), rnd * HS, basis(dx, dy), op=op, k=k, mat=mat)

    def RC(a, b, ra, rb, k, mat=HD):
        X.rcone(hp(*a), hp(*b), ra * HS, rb * HS, k=k, mat=mat)

    # ---------- 上あご・頭蓋（箱のように深い鼻先・上を向いた鼻・めくれた上くちびる・大きなまゆ） ----------
    X.begin('U', 0.03, HD)
    E(0.10, 0.01, 0, (0.165, 0.135, 0.145), k=0.05)                        # 頭蓋（大きく）
    E(0.03, 0.085, 0, (0.11, 0.06, 0.11), k=0.04)                          # ひたいの盛り上がり（角のあいだ）
    RB(0.35, 0.005, 0, (0.21, 0.098, 0.088), 0.06, k=0.04, rot=-2)         # 鼻先（箱のように深く）
    E(0.57, 0.025, 0, (0.10, 0.092, 0.098), k=0.03)                        # 鼻先の丸み（上を向いた大きな鼻）
    RC((0.24, -0.100, 0.0), (0.57, -0.108, 0.0), 0.034, 0.034, k=0.03)     # 上くちびる（厚い・めくれ）
    for z in (1, -1):
        E(0.19, 0.105, 0.082 * z, (0.125, 0.045, 0.052), k=0.02, rot=-12)  # まゆ（眉弓：大きく張り出す）
        E(0.06, 0.125, 0.088 * z, (0.08, 0.030, 0.040), k=0.02, rot=-35)   # まゆの うしろの流れ（炎のように）
        E(0.24, -0.045, 0.088 * z, (0.14, 0.10, 0.045), k=0.03)            # ほお
        E(0.50, -0.062, 0.084 * z, (0.065, 0.045, 0.030), k=0.02, rot=6)   # 牙の上の ふくらみ（うなる口もと）
        E(0.58, 0.075, 0.066 * z, (0.05, 0.034, 0.040), k=0.02, rot=10)    # 鼻の穴のふくらみ
        X.sph(hp(0.625, 0.080, 0.070 * z), 0.022 * HS, op='S', k=0.006, mat=HD)   # 鼻の穴（前を向く）
    # 口のすき間（上あごの下を少し削る：歯ぐきの線）
    RB(0.40, -0.118, 0, (0.20, 0.010, 0.09), 0.006, k=0.004, op='S', rot=-1)
    X.end()
    # ---------- 下あご（大きく開いている） ----------
    OPEN = 40.0
    hinge = hp(0.19, -0.095)
    dj, nj = hdir(-OPEN)                                                   # あごの向き（下へ開く）
    JL = 0.42
    jaw_end = hinge + dj * JL * HS
    X.begin('U', 0.02, HD)
    X.rcone(hinge, jaw_end, 0.074 * HS, 0.046 * HS, k=0.02, mat=HD)
    X.ell(jaw_end + nj * 0.014 * HS, (0.055 * HS, 0.040 * HS, 0.052 * HS), basis(dj, nj), k=0.02, mat=HD)    # あご先
    X.ell(jaw_end - dj * 0.02 * HS + nj * 0.046 * HS, (0.050 * HS, 0.022 * HS, 0.050 * HS), basis(dj, nj), k=0.02, mat=HD)   # 下くちびる
    for z in (1, -1):
        X.rcone(hinge + out3 * 0.058 * z * HS, jaw_end + out3 * 0.038 * z * HS, 0.040 * HS, 0.026 * HS, k=0.02, mat=HD)
    X.end()
    # 口の中（暗い赤）：上あごと下あごのあいだ
    mc = (hp(0.40, -0.11) + (hinge + dj * 0.24 * HS)) / 2
    X.ell(mc, (0.20 * HS, 0.045 * HS, 0.060 * HS), basis(dj * 0.5 + U3 * 0.5, nj), k=0.0, mat=MOUTH)
    # 舌（そり上がる）
    X.ell(hinge + dj * 0.22 * HS + nj * 0.030 * HS, (0.13 * HS, 0.016 * HS, 0.034 * HS), basis(dj * 0.9 + nj * 0.1, nj), k=0.0, mat=MOUTH)
    # ---------- 歯 ----------
    for z in (1, -1):
        for s_ in np.arange(0.27, 0.58, 0.05):                              # 上の歯（下向き）
            a = hp(s_, -0.108, 0.066 * z)
            fang = s_ >= 0.50
            L = 0.034 if not fang else 0.092                                # 前の2本は大きな牙
            r0 = 0.013 if not fang else 0.018
            X.ccone(a + V3 * 0.012 * HS, a - V3 * L * HS - U3 * 0.006 * HS, r0 * HS, 0.0025 * HS, rnd=0.002, side=U3, k=0.0, mat=TEETH)
        for u in np.arange(0.22, 0.98, 0.12):                               # 下の歯（上向き）：あごにそって
            a = hinge + dj * u * (JL - 0.02) * HS + out3 * 0.048 * z * HS + nj * 0.040 * HS
            fang = u >= 0.85
            L = 0.030 if not fang else 0.070
            r0 = 0.012 if not fang else 0.016
            X.ccone(a - nj * 0.01 * HS, a + nj * L * HS - dj * (0.01 if fang else 0) * HS, r0 * HS, 0.0025 * HS, rnd=0.002, side=U3, k=0.0, mat=TEETH)
    # ---------- 目（金に光る）とまぶた ----------
    for z in (1, -1):
        X.sph(hp(0.20, 0.045, 0.098 * z), 0.038 * HS, k=0.0, mat=EY)
        E(0.20, 0.075, 0.100 * z, (0.058, 0.018, 0.028), k=0.01, rot=-12)   # 上まぶた（するどい目つき）
    # ---------- 角（うしろへ流れる・枝つき：鹿の角のように）----------
    tips = []
    for z in (1, -1):
        b = hp(0.02, 0.105, 0.058 * z)
        d0 = nrm(-U3 * 0.55 + V3 * 0.75 + out3 * 0.30 * z)                # 根元：上へ
        d1 = nrm(-U3 * 0.92 + V3 * 0.25 + out3 * 0.10 * z)                # 中：うしろへ流れる
        d2 = nrm(-U3 * 0.70 + V3 * 0.70 + out3 * 0.02 * z)                # 先：上へそる
        L = 0.56 * HS
        P = [b, b + d0 * L * 0.30, b + d0 * L * 0.40 + d1 * L * 0.32, b + d0 * L * 0.32 + d1 * L * 0.42 + d2 * L * 0.26]
        n = 16
        us = np.linspace(0, 1, n + 1)
        pts = [bez3(P, u) for u in us]
        rad = [0.060 * HS * (1 - 0.80 * u ** 1.1) for u in us]
        chain(X, pts, rad, HORN, kg=0.014)
        for (u0, dt_, Lt, r0) in (((0.30), nrm(V3 * 0.80 + U3 * 0.50 + out3 * 0.25 * z), 0.17, 0.026),        # 枝1：前上へ
                                  ((0.62), nrm(V3 * 0.90 - U3 * 0.10 + out3 * 0.40 * z), 0.13, 0.020)):       # 枝2：上・外へ
            q = bez3(P, u0)
            Q = [q, q + dt_ * Lt * HS * 0.45, q + dt_ * Lt * HS * 0.8 - U3 * Lt * HS * 0.08, q + dt_ * Lt * HS - U3 * Lt * HS * 0.22]
            p2 = [bez3(Q, v) for v in np.linspace(0, 1, 8)]
            chain(X, p2, [r0 * HS * (1 - 0.82 * v) for v in np.linspace(0, 1, 8)], HORN, kg=0.012)
            tips.append(p2[-1])
        tips.append(pts[-1])
    # 耳（うしろへ向く とがった耳：角の下・外がわ）
    for z in (1, -1):
        X.rcone(hp(0.02, 0.040, 0.095 * z), hp(-0.12, 0.080, 0.140 * z), 0.026 * HS, 0.005 * HS, k=0.01, mat=HD)
    # ほおのひれ（うしろへ広がる うすい板：3枚、あごのつけ根から）
    for z in (1, -1):
        for i, rot in enumerate((165, 190, 215)):
            dx, dy = hdir(rot)
            c = hp(0.14, -0.050 - 0.025 * i, 0.105 * z)
            X.ell(c + dx * 0.11 * HS, (0.13 * HS, 0.045 * HS * (1 - 0.15 * i), 0.007 * HS), basis(dx, dy), k=0.004, mat=FIN)
    # あごひげ（2本の房：あご先から下・うしろへ）
    for z, L_ in ((0.02, 0.16), (-0.02, 0.13)):
        b = jaw_end + nj * 0.0 * HS + out3 * z * HS * 1.2 - dj * 0.02 * HS
        d = nrm(-U3 * 0.35 - V3 * 0.90 + out3 * z * 3)
        pts = [b + d * L_ * u + (-U3) * L_ * 0.60 * u * u for u in np.linspace(0, 1, 7)]
        chain(X, pts, [0.017 * HS * (1 - 0.8 * u) for u in np.linspace(0, 1, 7)], FIN, kg=0.01)
    return dict(tips=tips, hinge=hinge, jaw_end=jaw_end, eye=[hp(0.20, 0.045, 0.098 * z) for z in (-1, 1)])


def whisker(X, S, z, mat, seed=0):
    """龍のひげ：鼻の横から外へ出て、あごの下をまわり、うしろへ波を打って流れる細いすじ（3Dの道。2Dでも同じ道に銀のすじを重ねる）"""
    rng = np.random.default_rng(seed + (3 if z > 0 else 4))
    U3, V3 = S['head_u'], S['head_v']
    HS = Hm.HEAD_SCALE
    hp = lambda s_, w_, zz=0.0: Hm.head_pt(S, s_, w_, zz)
    out = np.array([0, 0, 1.0]) * z
    b = hp(0.58, 0.0, 0.090 * z)
    L = 0.78
    d0 = nrm(U3 * 0.25 + out * 0.75 - V3 * 0.35)                          # 鼻の横から 外・下へ
    d1 = nrm(-U3 * 0.35 - V3 * 0.90 + out * 0.10)                         # 下へ たれる
    d2 = nrm(-U3 * 0.95 - V3 * 0.20 + out * 0.05)                         # あごの下を うしろへ流れる
    P = [b, b + d0 * L * 0.14, b + d0 * L * 0.16 + d1 * L * 0.42, b + d0 * L * 0.10 + d1 * L * 0.50 + d2 * L * 0.50]
    n = 22
    ph = rng.uniform(0, 6.28)
    pts, rad = [], []
    for u in np.linspace(0, 1, n + 1):
        q = bez3(P, u)
        tg = nrm(bez3(P, min(u + 0.02, 1)) - bez3(P, max(u - 0.02, 0)))
        nn = np.cross(tg, out)
        q = q + nn * 0.025 * math.sin(2 * math.pi * 1.4 * u + ph) * u + out * 0.03 * math.sin(2 * math.pi * 0.8 * u + ph) * u
        pts.append(q)
        rad.append(max(0.0035, 0.014 * HS * (1 - 0.8 * u ** 1.2)))
    chain(X, pts, rad, mat, kg=0.0)
    return pts


LEG_R = ((0.044, 0.04), (0.028, 0.026), (0.045, 0.05), (0.048, 0.042), (0.03, 0.027), (0.046, 0.051))      # 管・けん・つなぎ（前・後ろ）
LEG_E = ((0.062, 0.058, 0.052), (0.06, 0.062, 0.054), (0.068, 0.07, 0.056), (0.062, 0.064, 0.055))         # ひざ・球節・飛節


def build(sc, pose, yaw=0.0, mats=None, seed=0, neck_scale=(1.12, 1.15), chest_scale=1.1, leg_scale=1.2):
    """龍馬の体（しっぽの根元の3Dの出っぱりは作らない：しっぽは2Dの房）。
       mats: body・neck・head・horn・hoof・eye・teeth・mouth・fin・plate（のどの板）・gold（飾り板）・gem"""
    M = dict(body=1, neck=2, head=8, horn=7, hoof=6, eye=5, teeth=9, mouth=10, fin=11, plate=9, gold=3, gem=4)
    if mats:
        M.update(mats)
    th = pose['theta']
    piv2 = np.array([-0.60, 1.25])
    T = lambda p: Hm.rot2(p, piv2, th)
    nb = Hm.v3(T((0.52, 1.40)))                                           # 首のつけね（まわす軸）
    Rw = roty(yaw)
    SKIP = 97
    X = Yaw(sc, Rw, nb, skip=(SKIP,))
    X.neck_scale = neck_scale
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead'])
    t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rc0 = sc.rcone

    def rc(a_, b_, *args, **kw):
        if np.allclose(np.asarray(a_, float), ta0) or np.allclose(np.asarray(a_, float), t10):
            return
        if len(args) >= 2 and any(abs(args[0] - r0) < 1e-9 and abs(args[1] - r1) < 1e-9 for r0, r1 in LEG_R):   # 足の下半分を太く
            args = (args[0] * leg_scale, args[1] * leg_scale) + tuple(args[2:])
        return rc0(a_, b_, *args, **kw)

    nh0 = Hm._neck_head

    def nh(sc_, pose_, S_, M_):
        M2 = dict(M_); M2['head'] = SKIP; M2['eye'] = SKIP                # 馬の頭と目は出さない（首だけ）
        return nh0(X, pose_, S_, M2)

    ell0 = sc.ell

    def ell(c, radii, R=None, **kw):                                      # 胸を厚く（参考の像のように がっしり）
        radii = np.asarray(radii, float)
        if abs(kw.get('k', 0) - 0.14) < 1e-9 and np.allclose(radii, (0.30, 0.32, 0.27)):
            radii = radii * chest_scale
        elif abs(kw.get('k', 0) - 0.12) < 1e-9 and np.allclose(radii, (0.11, 0.17, 0.10)):
            radii = radii * (1.0 + (chest_scale - 1.0) * 1.6)
        elif any(np.allclose(radii, e) for e in LEG_E):                   # ひざ・球節・飛節
            radii = radii * leg_scale
        return ell0(c, tuple(radii), R, **kw)

    sc.rcone = rc
    sc.ell = ell
    Hm._neck_head = nh
    try:
        S = Hm.build(sc, pose, mats=dict(body=M['body'], neck=M['neck'], hoof=M['hoof'], eye=M['eye'], head=M['head']))
    finally:
        sc.rcone = rc0
        sc.ell = ell0
        Hm._neck_head = nh0
    # ---------- 龍の頭・ひげ ----------
    H = dragon_head(X, S, M, seed)
    whisk = {z: whisker(X, S, z, M['fin'], seed) for z in (1, -1)}
    # ---------- のどの板（象牙色の うろこ板：首の下にそって）----------
    ts = np.linspace(0, 1, 40)
    crest = Hm.bez(S['crest'], ts); throat = Hm.bez(S['throat'], ts)
    hw = np.interp(ts, [0, .35, .8, 1], [0.19, 0.14, 0.095, 0.075])
    PL = M['plate']
    X.begin('U', 0.0, PL)
    for i in range(2, 39, 3):
        c2, c2n = throat[i], throat[min(i + 2, 39)]
        tg = nrm(Hm.v3(c2n - c2))
        up = nrm(Hm.v3(crest[i] - throat[i]))
        c3 = Hm.v3(c2) + up * 0.006
        X.rbox(c3, (0.036, 0.012, hw[i] * 0.78), 0.010, basis(tg, up), k=0.0, mat=PL)
    X.end()
    # 胸の板（のどの板のつづき：胸の前を下へ）
    sc.begin('U', 0.0, PL)
    for (p2, w_) in (((0.715, 1.30), 0.15), ((0.735, 1.20), 0.17), ((0.735, 1.10), 0.18), ((0.715, 1.00), 0.17), ((0.67, 0.91), 0.15)):
        c3 = Hm.v3(T(p2))
        sc.rbox(c3, (0.016, 0.040, w_), 0.010, basis(Hm.v3(Hm.adir(th)), (0, 1, 0)), k=0.0, mat=PL)
    sc.end()
    # ---------- 肩と腰の金の飾り板（彫り模様）・赤い玉 ----------
    G = M['gold']
    fx = Hm.v3(Hm.adir(th))
    for (p2, rx, ry, zz) in (((0.40, 1.34), 0.15, 0.12, 0.315), ((-0.60, 1.40), 0.14, 0.12, 0.295)):
        c3 = Hm.v3(T(p2), zz * NEAR)
        sc.ell(c3, (rx, ry, 0.030), basis(fx, (0, 1, 0)), k=0.02, mat=G)
        sc.torus(c3 + np.array([0, 0, 0.024 * NEAR]), np.array([0, 0, 1.0]), rx * 0.55, 0.010, k=0.004, mat=G)
        sc.sph(c3 + np.array([0, 0, 0.032 * NEAR]), 0.028, k=0.0, mat=M['gem'])
    # ---------- 背すじの小さなひれ（首の上〜腰）----------
    FIN = M['fin']
    spine = [Hm.v3(crest[i]) for i in range(6, 36, 5)]
    backline = [Hm.v3(T(p)) for p in ((0.34, 1.615), (0.20, 1.59), (0.06, 1.555), (-0.10, 1.545), (-0.26, 1.555), (-0.42, 1.59), (-0.56, 1.605))]
    allp = [(X.p(q), X.d(nrm(Hm.v3(crest[min(i + 2, 39)] - crest[max(i - 2, 0)])))) for i, q in zip(range(6, 36, 5), spine)]
    allp += [(q, fx) for q in backline]
    for i, (q, tg) in enumerate(allp):
        up = np.array([0, 1.0, 0])
        d = nrm(up * 0.75 - tg * 0.65)                                     # うしろへ寝たひれ
        sz = 0.045 if i < 6 else 0.038
        sc.ell(q + up * 0.012 + d * sz * 0.6, (sz, 0.018, 0.006), basis(d, up), k=0.004, mat=FIN)

    # ---------- 目印（世界の3Dの点） ----------
    marks = dict(
        crest=[X.p(Hm.v3(q)) for q in crest], crest_near=[X.p(Hm.v3(q, 0.07 * NEAR)) for q in crest],
        crest_far=[X.p(Hm.v3(q, -0.07 * NEAR)) for q in crest], throat=[X.p(Hm.v3(q)) for q in throat],
        poll=X.p(Hm.v3(S['poll'])), eye=X.p(H['eye'][0 if NEAR < 0 else 1]), eye_far=X.p(H['eye'][1 if NEAR < 0 else 0]),
        muzzle=X.p(Hm.head_pt(S, 0.62, -0.02)), jaw=X.p(H['jaw_end']),
        tailhead=Hm.v3(S['tailhead']), croup=Hm.v3(S['croup']), withers=Hm.v3(S['withers']), back=Hm.v3(S['back']), loin=Hm.v3(S['loin']),
        hooves=[Hm.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')],
        fetlocks=[Hm.v3(S[k]['ft'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')],
        horn_tips=[X.p(q) for q in H['tips']], whiskers={z: [X.p(q) for q in whisk[z]] for z in (1, -1)},
        chest=Hm.v3(S['chest']), neck_base=nb, Rw=Rw, S=S,
    )
    return marks
