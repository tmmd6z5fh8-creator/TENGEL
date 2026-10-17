"""大理石の像：後ろ足で立ち上がる馬（波打つたてがみ・台までとどく太いしっぽ・岩の台座）
   体・首・頭・足は3Dの馬（r3d/horse3d.py）。たてがみとしっぽは、太さの変わる丸い筒をつないだ房（彫刻のうねり）。
   像ぜんたいを、上から見て yaw 度まわして（顔を少しこちらへ）、後ろ足のひづめを岩の上へ置く。
   形はすべて一から作ったオリジナル（参考の写真の形はなぞっていない）。
   build_statue(sc, foot, yaw, mats) → 目印"""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import horse3d as Hm
from h3d import nrm, basis

POSE = dict(theta=44.0, neck_rot=-26.0, head_ang=-50.0,
            fore=dict(R=[-62, 10, -98, -130], L=[-48, 38, -62, -100]),
            hind=dict(R=[-33.9, -127.3, -70, -48], L=[-38.8, -139.7, -92, -64]),     # 2つのひづめが同じ高さ（手前の足が少し前）
            tail=[-165, -140])


def roty(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class Xf:
    """像の形を、大きさ g 倍にして・まわして（yaw）・動かして（o）から sc に出す（ひづめの点 piv が中心）"""
    def __init__(self, sc, Rw, o, piv, g=1.0):
        self.sc, self.Rw, self.o, self.piv, self.g = sc, Rw, np.asarray(o, float), np.asarray(piv, float), float(g)

    def p(self, q):
        return self.Rw @ (np.asarray(q, float) - self.piv) * self.g + self.piv + self.o

    def R(self, R):
        R = np.eye(3) if R is None else np.asarray(R, float)
        return R @ self.Rw.T

    def kw(self, kw):
        kw = dict(kw)
        if 'k' in kw:
            kw['k'] = kw['k'] * self.g
        return kw

    def ell(self, c, radii, R=None, **kw): self.sc.ell(self.p(c), tuple(np.asarray(radii, float) * self.g), self.R(R), **self.kw(kw))
    def rcone(self, a, b, ra, rb, **kw): self.sc.rcone(self.p(a), self.p(b), ra * self.g, rb * self.g, **self.kw(kw))
    def sph(self, c, r, **kw): self.sc.sph(self.p(c), r * self.g, **self.kw(kw))
    def rbox(self, c, half, rnd, R=None, **kw): self.sc.rbox(self.p(c), tuple(np.asarray(half, float) * self.g), rnd * self.g, self.R(R), **self.kw(kw))
    def ccone(self, a, b, ra, rb, rnd=0.0, side=(1, 0, 0), **kw):
        self.sc.ccone(self.p(a), self.p(b), ra * self.g, rb * self.g, rnd=rnd * self.g, side=self.Rw @ np.asarray(side, float), **self.kw(kw))
    def begin(self, op='U', k=0.0, mat=0): self.sc.begin(op, k * self.g, mat)
    def end(self): self.sc.end()


def chain(sc, pts, rad, k=0.0, kg=0.02, mat=1):
    """太さの変わる丸い筒をつないだ房（ひとまとまり＝グループ）"""
    sc.begin('U', kg, mat)
    for i in range(len(pts) - 1):
        sc.rcone(pts[i], pts[i + 1], rad[i], rad[i + 1], k=k, mat=mat)
    sc.end()


def frames(pts):
    """道にそった向き（T）と、それに直角な2つの向き（N・B）：ねじれないように前の N を引きつぐ"""
    P = np.asarray(pts, float)
    n = len(P)
    T, N, B = [], [], []
    for i in range(n):
        t = nrm(P[min(i + 1, n - 1)] - P[max(i - 1, 0)])
        if i == 0:
            nn = np.array([-t[1], t[0], 0.0])
            if np.linalg.norm(nn) < 1e-6:
                nn = np.array([1.0, 0, 0])
        else:
            nn = N[-1] - t * np.dot(N[-1], t)
        nn = nrm(nn)
        T.append(t); N.append(nn); B.append(np.cross(t, nn))
    return T, N, B


def tube(sc, pts, rad, grooves=(), mat=1, kg=0.04, gk=0.008, kseg=0.0):
    """太さの変わる筒（ひとまとまり）。grooves＝彫ったすじ：(角度, ねじれ, 太さ, 始め u, 終わり u)"""
    sc.begin('U', kg, mat)
    for i in range(len(pts) - 1):
        sc.rcone(pts[i], pts[i + 1], rad[i], rad[i + 1], k=kseg, mat=mat)
    if grooves:
        T, N, B = frames(pts)
        n = len(pts)
        for a0, tw, gr, u0, u1 in grooves:
            g = []
            for i in range(n):
                u = i / (n - 1)
                if u0 - 1e-9 <= u <= u1 + 1e-9:
                    a = a0 + tw * u
                    taper = min(1.0, (u - u0) / 0.08 + 0.25, (u1 - u) / 0.08 + 0.25)
                    g.append((np.asarray(pts[i], float) + (N[i] * math.cos(a) + B[i] * math.sin(a)) * rad[i] * 1.0, gr * max(0.25, taper)))
            for j in range(len(g) - 1):
                sc.rcone(g[j][0], g[j + 1][0], g[j][1], g[j + 1][1], op='S', k=gk, mat=mat)
    sc.end()


def bez3(P, t):
    P = np.asarray(P, float)
    t = np.asarray(t, float)[..., None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]


NEAR = -1.0      # こちら（カメラ）がわの z の向き（左向きの像：カメラは -z）


def neck_hw(t):
    return float(np.interp(t, [0, .35, .8, 1], [0.19, 0.14, 0.095, 0.075]))


def mane(S, n=16, seed=11):
    """たてがみ：首の上のふちの生えぎわから、外へ・うしろへ流れて うねる丸い房を、2列（こちら・むこう）に
       少しずつ重ねてならべる（となりの房とのあいだが、彫った みぞ になる）。先は細く、少しだけ首の方へ。
       首のこちらがわには、たれる房をいくつか。→ [(道, 太さ, すじ)]"""
    rng = np.random.default_rng(seed)
    crest = lambda t: Hm.bez(S['crest'], t)
    out_at = lambda t: nrm(Hm.bez(S['crest'], t) - Hm.bez(S['throat'], t))
    tg_at = lambda t: nrm(Hm.bez(S['crest'], min(t + 0.02, 1)) - Hm.bez(S['crest'], max(t - 0.02, 0)))
    locks = []
    tb = np.linspace(0.03, 0.97, 24)
    locks.append(([np.r_[crest(t) - out_at(t) * 0.01, 0.0] for t in tb], [0.05 + 0.025 * math.sin(math.pi * t) for t in tb], ()))
    ph0 = rng.random() * 6.28
    for i, t in enumerate(np.linspace(0.05, 0.95, n)):
        c, out, tg = crest(t), out_at(t), tg_at(t)
        d0 = nrm(out * 0.68 - tg * 0.73)
        perp = np.array([-d0[1], d0[0]])
        L = (0.20 + 0.28 * math.sin(math.pi * (0.06 + 0.88 * t))) * (0.92 + 0.16 * rng.random())
        ph = ph0 + t * 2.2 + rng.random() * 0.5                       # となりの房と、うねりがそろう
        r0 = 0.068 + 0.012 * rng.random()
        z0 = (0.03 if i % 2 else -0.03)
        m = 18
        pts, rad = [], []
        for j in range(m + 1):
            u = j / m
            q2 = c - out * 0.025 + d0 * L * u + (-tg) * L * 0.20 * u * u
            q2 = q2 + perp * 0.05 * math.sin(2 * math.pi * 0.8 * u + ph) * u ** 0.8
            q2 = q2 - out * L * 0.22 * max(0.0, u - 0.72) ** 2 * 3.0
            pts.append(np.array([q2[0], q2[1], z0 * (1 + 0.8 * u)]))
            rad.append(max(0.010, r0 * (1 - 0.86 * u ** 1.4)))
        locks.append((pts, rad, ()))
    for i, t in enumerate(np.linspace(0.12, 0.88, 7)):
        c, out, tg = crest(t), out_at(t), tg_at(t)
        d1 = nrm(-out * 0.55 - tg * 0.62)
        L = 0.16 + 0.08 * rng.random()
        ph = ph0 + t * 2.2
        m = 14
        pts, rad = [], []
        for j in range(m + 1):
            u = j / m
            q2 = c + d1 * L * u + np.array([-d1[1], d1[0]]) * 0.022 * math.sin(2 * math.pi * 0.8 * u + ph)
            z = NEAR * (0.02 + neck_hw(t) * 0.92 * math.sin(min(1.0, u * 1.6) * math.pi / 2))
            pts.append(np.array([q2[0], q2[1], z]))
            rad.append(max(0.008, 0.042 * (1 - 0.85 * u ** 1.3)))
        locks.append((pts, rad, ()))
    return locks


def forelock(S):
    """前髪：耳のあいだから、ひたいへ"""
    hp = lambda s, w, z=0.0: Hm.head_pt(S, s, w, z)
    out = []
    for z, s1 in ((0.03, 0.20), (-0.03, 0.17)):
        P = [hp(-0.02, 0.10, z), hp(0.06, 0.13, z * 1.4), hp(0.13, 0.11, z * 1.6), hp(s1, 0.08, z * 1.5)]
        pts = [bez3(P, s) for s in np.linspace(0, 1, 9)]
        rad = [0.035 * (1 - 0.75 * s) for s in np.linspace(0, 1, 9)]
        out.append((pts, rad, ()))
    return out


def tail(S, end):
    """しっぽ：つけねから うしろへ張り出し、ゆるいS字で岩までたれる。丸い房6本を、なわのように少しねじって束ね、
       下で岩の上へ扇のように広げる（房のあいだが、彫った みぞ になる）"""
    ta = np.asarray(S['tailhead'], float)
    end = np.asarray(end, float)
    P = [ta + Hm.adir(-165) * 0.02, ta + np.array([-0.46, 0.06]), np.array([end[0] - 0.32, end[1] + 0.66]), np.array([end[0], end[1] + 0.02])]
    m = 40
    C = []
    for j in range(m + 1):
        u = j / m
        q2 = bez3(P, u)
        tgt = nrm(bez3(P, min(u + 0.02, 1)) - bez3(P, max(u - 0.02, 0)))
        nn = np.array([-tgt[1], tgt[0]])
        q2 = q2 + nn * 0.04 * math.sin(2 * math.pi * 0.9 * u + 0.6) * math.sin(math.pi * u)
        C.append(np.array([q2[0], q2[1], 0.0]))
    T, N, B = frames(C)
    locks = [(C[:8], [0.085 - 0.002 * k for k in range(8)], ())]          # つけね
    nl = 6
    for k in range(nl):
        a0 = 2 * math.pi * k / nl
        pts, rad = [], []
        for j in range(m + 1):
            u = j / m
            spread = 0.055 + 0.03 * math.sin(math.pi * min(1.0, u * 1.4)) + 0.10 * max(0.0, u - 0.82) ** 1.2 * 3.5
            a = a0 + 1.6 * u                                                  # ねじれ
            off = N[j] * math.cos(a) * spread + B[j] * math.sin(a) * spread * (1.0 - 0.5 * max(0.0, u - 0.82) * 5)
            pts.append(C[j] + off)
            r = 0.060 * (0.85 + 0.25 * math.sin(math.pi * min(1.0, u * 1.2))) * (0.9 + 0.2 * ((k * 7) % 3) / 2)
            if u < 0.06:
                r *= 0.7 + 5 * u
            rad.append(r)
        locks.append((pts, rad, ()))
    return locks


def build_statue(sc, foot, yaw=0.0, g=1.0, pose=POSE, mats=None, tail_back=0.58):
    """foot＝後ろ足のひづめ（2つのまん中・下のふち）を置く世界の点。g＝大きさ。tail_back＝しっぽの先をひづめからどれだけうしろへ（m）"""
    M = dict(body=1, neck=1, hoof=6, eye=5, head=1)
    if mats:
        M.update(mats)
    S0 = Hm.skeleton(pose)
    hm = np.array([np.mean([S0['HL']['hf'][0], S0['HR']['hf'][0]]), S0['ground'] + 0.035, 0.0])
    Rw = roty(yaw)
    o = np.asarray(foot, float) - hm
    X = Xf(sc, Rw, o, hm, g)
    S = Hm.build(X, pose, mats=M)
    B = M['body']
    for pts, rad, gr in mane(S):
        tube(X, pts, rad, gr, mat=B, kg=0.012)
    for pts, rad, gr in forelock(S):
        tube(X, pts, rad, gr, mat=B, kg=0.02)
    end = np.array([hm[0] - tail_back, hm[1]])
    for pts, rad, gr in tail(S, end):
        tube(X, pts, rad, gr, mat=B, kg=0.012)
    S['X'] = X
    S['tail_end_world'] = X.p(np.array([end[0], end[1], 0.0]))
    S['foot_world'] = np.asarray(foot, float)
    return S


def rock(sc, foot, tail_end, top, mat=2, seed=5):
    """岩の台座：ひづめとしっぽの先の下に、平たい丸い石をいくつか重ねる（上の面＝top）"""
    rng = np.random.default_rng(seed)
    f, te = np.asarray(foot, float), np.asarray(tail_end, float)
    cx = (f[0] + te[0]) / 2
    span = abs(f[0] - te[0]) / 2 + 0.20
    h = top - (top - 0.0)
    pieces = [((cx, 0.0), (span, 0.08, 0.30), 0.0), ((f[0] + 0.05, 0.05), (0.26, 0.07, 0.24), 8.0), ((te[0] - 0.02, -0.06), (0.24, 0.065, 0.22), -6.0),
              ((cx + 0.08, 0.14), (0.22, 0.06, 0.16), 3.0), ((cx - 0.15, -0.14), (0.20, 0.055, 0.15), -4.0)]
    sc.begin('U', 0.05, mat)
    for (x, z), r, ang in pieces:
        yc = top - r[1] * 0.92 + rng.uniform(-0.01, 0.01)
        a = math.radians(ang)
        R = np.array([[math.cos(a), math.sin(a), 0], [-math.sin(a), math.cos(a), 0], [0, 0, 1]])
        sc.ell(np.array([x, yc, z]), r, R, k=0.05, mat=mat)
    sc.end()
