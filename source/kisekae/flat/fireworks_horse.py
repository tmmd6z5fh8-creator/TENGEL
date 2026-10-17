"""花火の馬：光の線でえがいた、夜空をかける馬
   - 3Dの馬（horse3d）を4倍の大きさで描き、外の形と「重なり」の線（手前の足がおなかの前を通る所など）をひろって、
     角（ひづめ・足のつけね・耳）で区切った光の線にする。線ごとに入りと抜きがあり、奥の足の線はうすい
   - 肩・もも・ほおの線、目・鼻の穴・口は、骨の目印から足す
   - たてがみとしっぽは「しだれ柳」の花火：金の光のすじが先でピンクになり、火の粉になって落ちる
   - 光の点のきらめき・ひづめから散る「松葉」の火花・体の中のうすい光
   形はすべて一から作ったオリジナル。light_horse(img, W, Hh) → 馬を重ねた img"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm

S4 = 4                                     # 4倍で描いて縮める
BOX = (296, 78, 586, 231)                  # 馬（体）を入れる場所（ちょうちんにかからない高さ）
POSE = dict(theta=6.0, neck_rot=-22.0, head_ang=-42.0,
            fore=dict(L=[-78, -40, -52, -40], R=[-100, -55, -125, -150]),
            hind=dict(L=[-112, -140, -118, -135], R=[-50, -105, -75, -50]),
            tail=[-170, -160])
AZIM, ELEV = 3.0, 2.0

GOLD = hexc('#FFC24A')        # 光のまわり（金）
GOLD_HOT = hexc('#FFF4D2')    # 光のしん（白っぽい金）
PINK = hexc('#FF6FA8')        # 花火ピンク
PINK_HOT = hexc('#FFC9DD')


# ---------------------------------------------------------------- 線の道具
def resample(P, step):
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    L = np.r_[0, np.cumsum(seg)]
    if L[-1] < step:
        return P[[0, -1]]
    t = np.linspace(0, L[-1], int(L[-1] / step) + 1)
    return np.stack([np.interp(t, L, P[:, 0]), np.interp(t, L, P[:, 1])], 1)


def smooth_open(P, k):
    if len(P) < 2 * k + 3:
        return P
    return np.stack([np.convolve(np.r_[np.full(k, P[0, i]), P[:, i], np.full(k, P[-1, i])], np.ones(2 * k + 1) / (2 * k + 1), 'valid')
                     for i in (0, 1)], 1)


def smooth_closed(P, k):
    return np.stack([np.convolve(np.r_[P[-k:, i], P[:, i], P[:k, i]], np.ones(2 * k + 1) / (2 * k + 1), 'valid') for i in (0, 1)], 1)


def bez3(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def taper(n, a=0.10, b=0.18, lo=0.25, pa=0.5, pb=0.7):
    t = np.linspace(0, 1, n)
    e = np.clip(t / a, 0, 1) ** pa * np.clip((1 - t) / b, 0, 1) ** pb
    return lo + (1 - lo) * e


class Light:
    """4倍の紙に、光のしん（白っぽい色）と光のまわり（こい色）を描く"""

    def __init__(self, W, Hh):
        self.W, self.Hh = W, Hh
        self.core = np.zeros((Hh * S4, W * S4, 3), np.uint8)
        self.glow = np.zeros((Hh * S4, W * S4, 3), np.uint8)
        self.a = np.zeros((Hh * S4, W * S4), np.uint8)

    def stroke(self, P, w, core, glow, step=0.35):
        """P：1倍の点の列、w：1倍の太さ（1つ、または点ごと）、core/glow：色（(3,)、または点ごとに (n,3)）"""
        P = np.asarray(P, float)
        if len(P) < 2:
            return
        Q = resample(P, step)
        cl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        tp = cl / max(cl[-1], 1e-9)                      # もとの点の位置（0〜1）
        cq = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
        u = cq / max(cq[-1], 1e-9)
        w = np.asarray(w, float)

        def at(v):                                      # 点ごとの値（長さが点の数と同じ）／それ以外は線の上に等間隔
            v = np.asarray(v, float)
            x = tp if len(v) == len(P) else np.linspace(0, 1, len(v))
            return np.interp(u, x, v)

        ww = np.full(len(Q), float(w)) if w.ndim == 0 else at(w)

        def col(v):
            v = np.asarray(v, float)
            if v.ndim == 1:
                return np.tile(v, (len(Q), 1))
            return np.stack([at(v[:, c]) for c in range(3)], 1)
        cc, gg = col(core), col(glow)
        for (x, y), r, c, g in zip(Q, ww, cc, gg):
            ctr = (int(round(x * S4 * 4)), int(round(y * S4 * 4)))
            rad = max(1, int(round(r * S4 / 2 * 4)))
            cv2.circle(self.core, ctr, rad, tuple(int(v * 255) for v in np.clip(c, 0, 1)), -1, cv2.LINE_AA, shift=2)
            cv2.circle(self.glow, ctr, rad, tuple(int(v * 255) for v in np.clip(g, 0, 1)), -1, cv2.LINE_AA, shift=2)
            cv2.circle(self.a, ctr, rad, 255, -1, cv2.LINE_AA, shift=2)

    def dot(self, x, y, r, core, glow):
        self.stroke(np.array([[x, y], [x + 1e-3, y]]), r * 2, core, glow)

    def down(self):
        f = lambda m: cv2.resize(m, (self.W, self.Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        return f(self.core), f(self.glow), f(self.a)


def flare(add, x, y, L, col, k=1.0, ang=0.0, thin=0.55):
    """4本の光のすじのきらめき（十字）＋まんなかの点"""
    Hh, W = add.shape[:2]
    r = int(L * 1.6) + 4
    x0, x1, y0, y1 = max(0, int(x) - r), min(W, int(x) + r + 1), max(0, int(y) - r), min(Hh, int(y) + r + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - x, yy - y
    ca, sa = math.cos(ang), math.sin(ang)
    u, v = dx * ca + dy * sa, -dx * sa + dy * ca
    ray = np.exp(-(v / thin) ** 2) * np.clip(1 - np.abs(u) / L, 0, 1) ** 2.2 + np.exp(-(u / thin) ** 2) * np.clip(1 - np.abs(v) / L, 0, 1) ** 2.2
    rr = np.sqrt(dx ** 2 + dy ** 2)
    m = ray * 0.9 + np.exp(-(rr / (0.9 + L * 0.06)) ** 2) * 1.2 + np.exp(-(rr / (L * 0.35)) ** 2) * 0.25
    add[y0:y1, x0:x1] += m[..., None] * np.asarray(col, np.float32) * k


# ---------------------------------------------------------------- 3Dの形と目印
def render_body(pose, eye, tgt, fov, W, Hh, name='fw_light'):
    """style2d.render_horse と同じ描き方で、しっぽの根元の3Dの出っぱりだけ作らない（しっぽは光のすじで描く）"""
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

    def rc(a, b, *args, **kw):
        if np.allclose(np.asarray(a, float), ta0) or np.allclose(np.asarray(a, float), t10):
            return
        return rc0(a, b, *args, **kw)

    sc.rcone = rc
    S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    sc.rcone = rc0
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['throat'] = P(np.c_[Hm.bez(S['throat'], ts), np.zeros(len(ts))])
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['tail'] = P([Hm.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - tgt, np.asarray(eye, float) - tgt) > np.dot(e1 - tgt, np.asarray(eye, float) - tgt) else e1])[0]
    R['S'], R['scene'] = S, sc
    return R


HEAD_SCALE = 1.25                          # 頭を少し大きく（目が見えるように）


def shape(W, Hh, pose=POSE, box=BOX, azim=AZIM, elev=ELEV):
    Hm.HEAD_SCALE = HEAD_SCALE
    e, t = frame_horse(pose, tuple(v * S4 for v in box), W * S4, Hh * S4, facing='right', azim=azim, elev=elev)
    R = render_body(pose, e, t, 26, W * S4, Hh * S4)
    sc, S = R['scene'], R['S']

    def pj(p, z=0.0):
        p = np.asarray(p, float)
        if p.shape[-1] == 2:
            p = Hm.v3(p, z)
        return sc.project(np.asarray([p], float))[0][0] / S4

    L = {}
    for k in ('withers', 'back', 'loin', 'croup', 'tailhead', 'buttock', 'hip', 'sternum', 'chest', 'scap', 'poll'):
        L[k] = pj(S[k])
    for leg in ('FL', 'FR', 'HL', 'HR'):
        G = S[leg]
        for j, v in G.items():
            if j in ('z', 'ang'):
                continue
            L[leg + '_' + j] = pj(v, 0.155 * G['z'])
    hp = lambda s, w, z=0.0: pj(Hm.head_pt(S, s, w, z))
    L['hp'] = hp
    L['pj'] = pj
    L['eye'] = np.asarray(R['eye'], float) / S4
    L['muzzle'] = np.asarray(R['muzzle'], float) / S4
    L['crest'] = np.asarray(R['crest'], float) / S4          # き甲 → うなじ
    L['tail'] = np.asarray(R['tail'], float) / S4
    L['throat'] = np.asarray(R['throat'], float) / S4
    return R, L


def outline(R, thr=0.04, k_corner=22, ang_min=56.0):
    """外の形と重なりの線（4倍）→ 角で区切った線の列。[(1倍の点, 種類, 奥の足か)]"""
    a, d = R['a'], R['d']
    inside = a > 0.5
    H3, W3 = a.shape
    dd = np.where(inside, d, 1e3)
    nj = np.zeros_like(inside)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                nj |= inside & (np.roll(np.roll(dd, dy, 0), dx, 1) < dd - thr)
    cut = cv2.dilate(nj.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    region = (inside & ~cut).astype(np.uint8)
    cs, _ = cv2.findContours(region, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    Pw = world_pos(R)
    zmap = np.nan_to_num(Pw[..., 2], nan=0.0)

    def samp(M, Q):
        qi = np.round(Q).astype(int)
        qi[:, 0] = np.clip(qi[:, 0], 0, W3 - 1)
        qi[:, 1] = np.clip(qi[:, 1], 0, H3 - 1)
        return M[qi[:, 1], qi[:, 0]]

    out = []
    for c in cs:
        P = c[:, 0, :].astype(float)
        if len(P) < 60:
            continue
        Ps = smooth_closed(P, 6)
        tg = np.gradient(Ps, axis=0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
        if samp(region, Ps + nr * 3).mean() > 0.5:
            nr = -nr                                             # 外向きに
        oin = samp(inside, Ps + nr * 5)
        cls = np.where(~oin, 1, np.where(samp(d, Ps + nr * 5) > samp(d, Ps - nr * 2) + thr, 2, 0))
        # ちらつきをならす（多数決）
        n = len(cls)
        win = 7
        ext = np.r_[cls[-win:], cls, cls[:win]]
        cls = np.array([np.bincount(ext[i:i + 2 * win + 1], minlength=3).argmax() for i in range(n)])
        z = samp(zmap, Ps - nr * 4)
        good = cls > 0
        if not good.any():
            continue
        if good.all():
            runs = [(np.arange(n), True)]
        else:
            st = int(np.argmin(good))
            order = (st + np.arange(n)) % n
            runs, cur = [], []
            for i in order:
                if good[i]:
                    cur.append(i)
                else:
                    if len(cur) > 10:
                        runs.append((np.array(cur), False))
                    cur = []
            if len(cur) > 10:
                runs.append((np.array(cur), False))
        for idx, closed in runs:
            Q, cq, zq = Ps[idx], cls[idx], z[idx]
            m = len(Q)
            ang = np.zeros(m)
            for i in range(m):
                if not closed and (i < k_corner or i >= m - k_corner):
                    continue
                v1 = Q[i] - Q[(i - k_corner) % m]
                v2 = Q[(i + k_corner) % m] - Q[i]
                cs_ = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
                ang[i] = math.degrees(math.acos(np.clip(cs_, -1, 1)))
            # 外へ出っぱる角（ひづめ・耳・鼻先）だけで区切る。へこんだ角（足のつけね）はとてもするどい時だけ
            tg_ = np.gradient(Q, axis=0)
            turn = np.zeros(m)
            for i in range(m):
                if not closed and (i < k_corner or i >= m - k_corner):
                    continue
                v1 = Q[i] - Q[(i - k_corner) % m]
                v2 = Q[(i + k_corner) % m] - Q[i]
                turn[i] = v1[0] * v2[1] - v1[1] * v2[0]
            nq = nr[idx]
            convex = np.array([np.dot(Q[(i + k_corner) % m] + Q[(i - k_corner) % m] - 2 * Q[i], nq[i]) < 0 for i in range(m)])
            cand = []
            for i in range(m):
                if ang[i] < (ang_min if convex[i] else 100.0):
                    continue
                lo, hi = i - k_corner, i + k_corner + 1
                if closed:
                    nb = ang[np.arange(lo, hi) % m]
                else:
                    nb = ang[max(0, lo):min(m, hi)]
                if ang[i] >= nb.max():
                    if not cand or i - cand[-1] > k_corner:
                        cand.append(i)
            if closed:
                if not cand:
                    cand = [0, m // 2]
                cuts = cand + [cand[0] + m]
                segs = [np.arange(cuts[j], cuts[j + 1] + 1) % m for j in range(len(cuts) - 1)]
            else:
                cuts = [0] + cand + [m - 1]
                segs = [np.arange(cuts[j], cuts[j + 1] + 1) for j in range(len(cuts) - 1)]
            for sg in segs:
                if len(sg) < 12:
                    continue
                kind = 'occ' if (cq[sg] == 2).mean() > 0.5 else 'sil'
                out.append(dict(P=Q[sg] / S4, kind=kind, z=float(np.median(zq[sg]))))
    return out


def break_near(strokes, pt, gap, rmax=8):
    """pt にいちばん近い線を、そこで切って gap（1倍）だけすき間をあける"""
    best, bi, bj = 1e9, -1, -1
    for i, s in enumerate(strokes):
        dd = np.linalg.norm(s['P'] - pt, axis=1)
        j = int(dd.argmin())
        if dd[j] < best:
            best, bi, bj = dd[j], i, j
    if bi < 0 or best > rmax:
        return strokes
    s = strokes.pop(bi)
    P = s['P']
    cl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    c0 = cl[bj]
    A = P[cl < c0 - gap / 2]
    B = P[cl > c0 + gap / 2]
    for Q in (A, B):
        if len(Q) >= 6:
            strokes.append(dict(s, P=Q))
    return strokes


def neck_top(R, L):
    """たてがみの根元：首の上のふち（き甲 → うなじ）と外向きの向き"""
    a = R['a']
    H3, W3 = a.shape
    C, T = L['crest'], L['throat']

    def ins(p):
        xi, yi = int(p[0] * S4), int(p[1] * S4)
        return 0 <= xi < W3 and 0 <= yi < H3 and a[yi, xi] >= 0.5

    out = []
    for i in range(len(C)):
        c = C[i]
        tg = C[min(len(C) - 1, i + 1)] - C[max(0, i - 1)]
        tg = tg / (np.linalg.norm(tg) + 1e-9)
        n = np.array([tg[1], -tg[0]])
        if np.dot(T[i] - c, n) > 0:
            n = -n
        p = c.copy()
        if not ins(p):
            for _ in range(200):
                p = p - n * 0.25
                if ins(p):
                    break
        for _ in range(200):
            q = p + n * 0.25
            if not ins(q):
                break
            p = q
        out.append((p - n * 0.6, n))
    return out


TIPS = []                                  # 光のすじの先（きらめきを置く）


def strand(lt, P, w0, rng, cut=0.72, w1=0.55, hot=(GOLD_HOT, PINK_HOT), col=(GOLD, PINK), gamma=1.2, fall=0, k=1.0):
    """光のすじ：根元は金、先はピンク。cut から先は火の粉（点）になり、fall 個はそのまま下へ落ちる"""
    P = resample(P, 0.5)
    n = len(P)
    t = np.linspace(0, 1, n)
    m = t <= cut
    w = w0 + (w1 - w0) * np.clip(t / cut, 0, 1) ** 0.9
    mix = (t ** gamma)[:, None]
    core = (hot[0] * (1 - mix) + hot[1] * mix) * k
    glow = (col[0] * (1 - mix) + col[1] * mix) * k
    lt.stroke(P[m], w[m], core[m], glow[m])
    TIPS.append(P[m][-1])
    # 先の火の粉
    cl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    pos = cl[m.sum() - 1] + 2.0
    gap = 2.2
    r = w1 * 0.62
    last = P[-1]
    while pos < cl[-1]:
        i = int(np.searchsorted(cl, pos))
        i = min(i, n - 1)
        q = P[i] + rng.normal(0, 0.35, 2)
        lt.dot(q[0], q[1], max(0.32, r), core[i], glow[i])
        pos += gap
        gap *= rng.uniform(1.12, 1.28)
        r *= 0.86
        last = P[i]
    if fall:
        v = P[-1] - P[-6]
        v = v / (np.linalg.norm(v) + 1e-9)
        q = P[-1].copy()
        vel = v * 3.2
        rr = max(0.35, r)
        for j in range(fall):
            vel = vel * 0.78 + np.array([0, 1.6])
            q = q + vel + rng.normal(0, 0.5, 2)
            rr *= 0.9
            kk = 0.85 ** (j + 1)
            lt.dot(q[0], q[1], max(0.3, rr), hot[1] * k * kk + (1 - kk) * 0.2, col[1] * k * kk)


def matsuba(lt, x, y, ang, L, rng, k=1.0):
    """松葉の火花：まっすぐな光の線から、小さな枝が左右に出る"""
    d = np.array([math.cos(ang), math.sin(ang)])
    p0 = np.array([x, y])
    lt.stroke(np.array([p0, p0 + d * L]), np.array([0.85, 0.4]), GOLD_HOT * k, GOLD * k)
    for j in range(int(rng.integers(2, 4))):
        s = rng.uniform(0.35, 0.85)
        b = ang + math.radians(rng.choice([-1, 1]) * rng.uniform(32, 58))
        q0 = p0 + d * L * s
        lt.stroke(np.array([q0, q0 + np.array([math.cos(b), math.sin(b)]) * L * rng.uniform(0.28, 0.45)]),
                  np.array([0.6, 0.3]), GOLD_HOT * k, GOLD * k)


def curve(pts, n=60):
    """点を通るなめらかな線（Catmull-Rom）"""
    P = np.asarray(pts, float)
    P = np.r_[P[:1] * 2 - P[1:2], P, P[-1:] * 2 - P[-2:-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.array(out)


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


def body_line(lt, P, w0, k=1.0, far=False, a=5.0, b=8.0):
    P = smooth_open(resample(P, 0.5), 2)
    n = len(P)
    if n < 3:
        return
    Lp = n * 0.5
    w = w0 * taper(n, a=min(0.4, a / Lp), b=min(0.45, b / Lp), lo=0.3)
    if far:
        lt.stroke(P, w, (GOLD_HOT * 0.55 + PINK_HOT * 0.45) * 0.62 * k, (GOLD * 0.6 + PINK * 0.4) * 0.55 * k)
    else:
        lt.stroke(P, w, GOLD_HOT * k, GOLD * k)


def light_horse(img, W, Hh, seed=7, debug=None):
    rng = np.random.default_rng(seed)
    TIPS.clear()
    R, L = shape(W, Hh)
    st = outline(R)
    # 光の線の区切り：き甲（たてがみの根元のうしろ）・うなじ・のどの角・おなかのまんなか
    hp = L['hp']
    for pt, gap in ((L['withers'], 9.0), (hp(-0.02, 0.06), 4.0), (hp(0.16, -0.22), 5.0),
                    (L['tail'][0], 7.0)):
        pt = np.asarray(pt, float)
        if pt.shape[0] == 3:
            pt = pt[:2]
        st = break_near(st, pt, gap, rmax=14)
    lt = Light(W, Hh)
    add = np.zeros((Hh, W, 3), np.float32)

    # ---- 体の線（奥の足 → 手前）
    for s_ in sorted(st, key=lambda s_: s_['z']):
        far = s_['z'] < -0.06
        w0 = (2.3 if s_['kind'] == 'sil' else 1.7) * (0.72 if far else 1.0)
        body_line(lt, s_['P'], w0, far=far)

    # ---- 中の線：肩・もも・ほお（細め）
    back = unit(L['croup'] - L['withers'])
    down = np.array([-back[1], back[0]])
    if down[1] < 0:
        down = -down
    el, sc_, ps = L['FL_el'], L['scap'], L['FL_ps']
    body_line(lt, curve([sc_ + down * 3 + back * 2, (sc_ + el) / 2 + back * 7, el + back * 2 - down * 4]), 1.5, k=0.9)
    lo_, st_ = L['loin'], L['HL_st']
    body_line(lt, curve([lo_ + down * 8 - back * 3, (lo_ + st_) / 2 + down * 2 - back * 7, st_ - back * 4 - down * 2]), 1.5, k=0.9)
    cheek = [hp(0.215 + 0.125 * math.cos(math.radians(f)), -0.115 + 0.115 * math.sin(math.radians(f)), 0.10)[:2] for f in (78, 40, 5, -35)]
    body_line(lt, curve(cheek), 1.2, k=0.85, a=3, b=4)
    # 目・鼻の穴・口
    ex, ey = L['eye']
    hu = unit(L['muzzle'] - L['poll'])
    hv = np.array([hu[1], -hu[0]])
    if hv[1] > 0:
        hv = -hv
    E = lambda s__, w__: L["eye"] + hu * (s__ + 0.8) + hv * (w__ - 2.2)
    lt.stroke(curve([E(-3.6, -0.6), E(-0.6, 0.5), E(3.0, 0.9)], 16), np.array([0.5, 1.5, 2.3, 1.7, 0.6]),       # 光る目（アーモンド形）
              np.array([1.0, 1.0, 1.0]), PINK * 0.9 + GOLD * 0.1)
    no = hp(0.535, 0.022, 0.055)[:2]
    lt.stroke(curve([no - hu * 1.6 + hv * 0.9, no + hu * 0.4 + hv * 0.6, no + hu * 1.1 - hv * 1.0], 12), np.array([0.6, 1.1, 0.6]), GOLD_HOT, GOLD)
    mo = [hp(0.47, -0.10, 0.07)[:2], hp(0.53, -0.085, 0.07)[:2], hp(0.575, -0.07, 0.06)[:2]]
    lt.stroke(curve(mo, 12), np.array([0.5, 0.9, 0.5]), GOLD_HOT * 0.9, GOLD * 0.85)

    # ---- しっぽ（しだれ柳）：たてがみより先に（体のうしろ）
    th0 = L['tail'][0]
    bk = unit(th0 - L['withers'])
    a = R['a']
    p = th0.copy()
    for _ in range(200):
        q = p + bk * 0.25
        xi, yi = int(q[0] * S4), int(q[1] * S4)
        if a[yi, xi] < 0.5:
            break
        p = q
    root = p - bk * 1.0
    side = np.array([-bk[1], bk[0]])
    NT = 12
    for k in range(NT):
        f = k / (NT - 1)
        r0 = root + side * (f - 0.5) * 5.0 + rng.normal(0, 0.4, 2)
        Lk = rng.uniform(92, 150) * (0.85 + 0.3 * math.sin(math.pi * f))
        thd = 174 + 34 * (f - 0.5) + rng.uniform(-4, 4)
        th = math.radians(thd)
        dv = np.array([math.cos(th), math.sin(th)])
        up = math.radians(thd + rng.uniform(14, 26))
        p1 = r0 + np.array([math.cos(up), math.sin(up)]) * 0.36 * Lk
        p2 = r0 + dv * 0.74 * Lk + np.array([0, 0.02 * Lk])
        p3 = r0 + dv * Lk + np.array([0, rng.uniform(0.16, 0.42) * Lk])
        P = bez3(r0, p1, p2, p3, 100)
        tt = np.linspace(0, 1, len(P))
        tg = np.gradient(P, axis=0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nv = np.stack([-tg[:, 1], tg[:, 0]], 1)
        P = P + nv * (rng.uniform(0.8, 2.0) * np.sin(2 * math.pi * (rng.uniform(0.6, 1.2) * tt + rng.uniform(0, 1))) * tt)[:, None]
        strand(lt, P, rng.uniform(1.6, 2.3), rng, cut=rng.uniform(0.58, 0.70), fall=int(rng.integers(2, 6)))

    # ---- たてがみ：首にそって、うしろへなびく光のすじ
    roots = neck_top(R, L)
    nC = len(roots)
    along = unit(L['withers'] - L['poll'])
    NM = 13
    for k in range(NM):
        t = 0.06 + 0.90 * k / (NM - 1)                 # 0：き甲 → 1：うなじ
        i = int(round(t * (nC - 1)))
        p0, nn = roots[i]
        Lk = (44 + 34 * math.sin(math.pi * min(1.0, 0.25 + t * 0.85))) * rng.uniform(0.85, 1.15)
        lift = math.radians(16 + 22 * t + rng.uniform(-6, 6))
        ca_, sa_ = math.cos(lift), math.sin(lift)
        dv = np.array([along[0] * ca_ - along[1] * sa_, along[0] * sa_ + along[1] * ca_])
        if dv[1] > along[1]:                            # 上へ回す（画面の上は y がへる）
            dv = np.array([along[0] * ca_ + along[1] * sa_, -along[0] * sa_ + along[1] * ca_])
        d0 = unit(nn * 0.45 + dv * 0.9)
        p3 = p0 + dv * Lk
        p1 = p0 + d0 * 0.30 * Lk
        p2 = p3 - unit(dv + np.array([0, 0.25])) * 0.35 * Lk
        P = bez3(p0, p1, p2, p3, 90)
        tt = np.linspace(0, 1, len(P))
        tg = np.gradient(P, axis=0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nv = np.stack([-tg[:, 1], tg[:, 0]], 1)
        P = P + nv * (rng.uniform(0.8, 2.0) * np.sin(2 * math.pi * (rng.uniform(0.7, 1.3) * tt + rng.uniform(0, 1))) * tt)[:, None]
        strand(lt, P, rng.uniform(1.4, 2.0), rng, cut=rng.uniform(0.66, 0.80), w1=0.5)
    # ---- ひづめから散る松葉の火花
    for key, base in (('FL_hf', 200), ('HL_hf', 150), ('HR_hf', 120)):
        h = L[key]
        for j in range(2):
            ang = math.radians(base + rng.uniform(-30, 30))
            off = np.array([math.cos(ang), math.sin(ang)]) * rng.uniform(3.5, 6.5)
            matsuba(lt, h[0] + off[0], h[1] + off[1], ang, rng.uniform(5.5, 8.5), rng, k=0.95)

    core, glow, ca = lt.down()
    gl = blur(glow, 1.0) * 0.9 + blur(glow, 3.0) * 0.6 + blur(glow, 8.0) * 0.36 + blur(glow, 18.0) * 0.15
    img = img + gl
    img = img * (1 - ca[..., None] * 0.92) + core * 0.92
    # ---- きらめき
    for (x, y), Lf, col in ((L['FL_hf'] + np.array([2, 1]), 9, GOLD_HOT), (L['FL_ps'] + np.array([-2, -3]), 7, GOLD_HOT),
                            (L['croup'] + np.array([0, -4]), 6, PINK_HOT)):
        flare(add, x, y, Lf, col * 0.9 + GOLD * 0.1, k=0.9)
    tips = np.array(TIPS)
    for j in rng.choice(len(tips), 5, replace=False):
        flare(add, tips[j][0], tips[j][1], rng.uniform(4.5, 7.0), PINK_HOT * 0.8 + GOLD_HOT * 0.2, k=0.8, ang=rng.uniform(0, 0.6))
    pts = np.array([s_['P'][rng.integers(len(s_['P']))] for s_ in st for _ in range(2)])
    pts = pts[pts[:, 0] < L['withers'][0]]                 # 体のうしろ半分だけ（前は線をすっきり）
    for _ in range(12):
        q = pts[rng.integers(len(pts))] + rng.normal(0, 6, 2)
        col = [GOLD_HOT, PINK_HOT, np.array([1.0, 1.0, 1.0]), hexc('#C8F4FF')][rng.choice(4, p=[0.45, 0.3, 0.17, 0.08])]
        flare(add, q[0], q[1], rng.uniform(1.8, 3.6), col, k=rng.uniform(0.5, 0.9), ang=rng.uniform(0, 0.5))
    img = img + add
    if debug is not None:
        debug.update(R=R, L=L, st=st)
    return img
