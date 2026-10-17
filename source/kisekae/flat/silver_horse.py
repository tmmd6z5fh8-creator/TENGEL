"""銀の像：全力で駆ける馬（まさちゃんが送った芦毛の競走馬の写真の「走る形」に寄せて、一から作った創作の像）
   体・首・頭・足は3Dの馬（r3d/horse3d.py）。たてがみとしっぽは、うしろへ流れてうねる丸い筒の房（彫刻のうねり）。
   写真の形はなぞっていない（ポーズ・たてがみ・しっぽは一から。騎手・ゼッケン・名前は出さない）。
   build_statue(sc, pose, mats) → 骨組み S（目印）"""
import os, sys, math, contextlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import horse3d as Hm
from h3d import nrm, basis
from marble_horse import tube, frames, bez3, neck_hw, forelock, NEAR
from throat_fix import slim_throat

# 伸びきった駆け足（写真と同じ瞬間）：手前の前足を前へ伸ばして地面に・むこうの前足はたたむ・後ろ足は2本ともうしろへ伸ばす
# 左向きで描く（カメラは -z）ので、手前の足は R
POSE = dict(theta=-3.0, neck_rot=-30.0, head_ang=-14.0,
            fore=dict(R=[-70, -56, -48, -30], L=[-118, -84, 170, 150]),
            hind=dict(R=[-150, -165, -172, -168], L=[-138, -158, -170, -166]),
            tail=[-172, -168])


def mane_stream(S, n=15, seed=21):
    """たてがみ：首の上のふちの生えぎわから、うしろへ（風に）流れてうねる丸い房。2列に少しずつ重ねる。
       根元は首にそい、先は細く上へはねる → [(道, 太さ, すじ)]"""
    rng = np.random.default_rng(seed)
    crest = lambda t: Hm.bez(S['crest'], t)
    out_at = lambda t: nrm(Hm.bez(S['crest'], t) - Hm.bez(S['throat'], t))
    tg_at = lambda t: nrm(Hm.bez(S['crest'], min(t + 0.02, 1)) - Hm.bez(S['crest'], max(t - 0.02, 0)))   # 首の方向（き甲 → うなじ）
    locks = []
    tb = np.linspace(0.03, 0.97, 24)
    locks.append(([np.r_[crest(t) - out_at(t) * 0.01, 0.0] for t in tb], [0.045 + 0.02 * math.sin(math.pi * t) for t in tb], ()))   # 生えぎわの土手
    ph0 = rng.random() * 6.28
    for i, t in enumerate(np.linspace(0.06, 0.96, n)):
        c, out, tg = crest(t), out_at(t), tg_at(t)
        d0 = nrm(-tg * 0.94 + out * 0.20)                                  # うしろ（き甲の方）へ・少し上へ（首にそって流れる）
        perp = np.array([-d0[1], d0[0]])
        L = (0.30 + 0.24 * math.sin(math.pi * (0.1 + 0.8 * t))) * (0.9 + 0.2 * rng.random())
        ph = ph0 + t * 2.4 + rng.random() * 0.4
        r0 = 0.060 + 0.012 * rng.random()
        z0 = (0.035 if i % 2 else -0.035)
        m = 18
        pts, rad = [], []
        for j in range(m + 1):
            u = j / m
            q2 = c - out * 0.02 + d0 * L * u + out * L * 0.14 * u * u       # 先は少し上へそる
            q2 = q2 + perp * 0.045 * math.sin(2 * math.pi * 0.9 * u + ph) * u ** 0.9
            pts.append(np.array([q2[0], q2[1], z0 * (1 + 0.6 * u)]))
            rad.append(max(0.009, r0 * (1 - 0.86 * u ** 1.4)))
        locks.append((pts, rad, ()))
    return locks


def tail_stream(S, length=1.05, seed=23):
    """しっぽ：つけねから うしろへ張り出して少し持ち上がり、波を打ちながら流れて先は少し下がる。
       丸い房6本を なわのように少しねじって束ねる（房のあいだが彫ったみぞになる）"""
    rng = np.random.default_rng(seed)
    ta = np.asarray(S['tailhead'], float)
    P = [ta + Hm.adir(-168) * 0.02, ta + np.array([-0.30, 0.10]), ta + np.array([-0.62, 0.14]), ta + np.array([-length, -0.02])]
    m = 40
    C = []
    for j in range(m + 1):
        u = j / m
        q2 = bez3(P, u)
        tgt = nrm(bez3(P, min(u + 0.02, 1)) - bez3(P, max(u - 0.02, 0)))
        nn = np.array([-tgt[1], tgt[0]])
        q2 = q2 + nn * 0.05 * math.sin(2 * math.pi * 1.1 * u + 0.4) * math.sin(math.pi * min(1.0, u * 1.1))
        C.append(np.array([q2[0], q2[1], 0.0]))
    T, N, B = frames(C)
    locks = [(C[:7], [0.075 - 0.003 * k for k in range(7)], ())]           # つけね
    nl = 6
    for k in range(nl):
        a0 = 2 * math.pi * k / nl + rng.uniform(-0.2, 0.2)
        pts, rad = [], []
        for j in range(m + 1):
            u = j / m
            spread = 0.045 + 0.045 * math.sin(math.pi * min(1.0, u * 1.25)) + 0.06 * max(0.0, u - 0.75) ** 1.2 * 2.5
            a = a0 + 1.4 * u
            off = N[j] * math.cos(a) * spread + B[j] * math.sin(a) * spread * 0.7
            pts.append(C[j] + off)
            r = 0.052 * (0.8 + 0.3 * math.sin(math.pi * min(1.0, u * 1.1))) * (0.9 + 0.2 * ((k * 7) % 3) / 2) * (1 - 0.55 * max(0.0, u - 0.7) / 0.3)
            if u < 0.06:
                r *= 0.7 + 5 * u
            rad.append(max(0.008, r))
        locks.append((pts, rad, ()))
    return locks


# 首の形（まさちゃんが引いた線に合わせる）
# 1回目（黄色の線）：首を細く → 2回目（赤線）：首の下のふちを広げて、あごのうしろの下（ほおの丸い板の下のはし）から胸までを1本の線に
# のどの線：胸がわの3つの点は（もとの のどの点 → たてがみの点）の割合、頭がわの端は頭の座標（s, w）
#   頭がわの端＝赤線の角（あごのうしろの下）を、体のまん中の面へもどした点。
#   3つの割合は、絵の首の下のふちが赤線にそうように（ずれ −1.4〜+2.7 画素）何回か描いて決めた
THROAT_IN = (0.10, 0.55, -0.04)
THROAT_END = (0.1463, -0.2146)
CREST_IN = (0.0, 0.06, 0.08, 0.04)


@contextlib.contextmanager
def slim_neck(throat_in=THROAT_IN, throat_end=THROAT_END, crest_in=CREST_IN):
    orig = Hm.skeleton

    def skel(p):
        S = orig(p)
        C, T = np.asarray(S['crest'], float).copy(), np.asarray(S['throat'], float).copy()
        S['crest'] = np.array([C[i] + (T[i] - C[i]) * crest_in[i] for i in range(4)])
        th = [T[i] + (C[i] - T[i]) * throat_in[i] for i in range(3)]
        th.append(Hm.head_pt(S, throat_end[0], throat_end[1])[:2])
        S['throat'] = np.array(th)
        return S
    Hm.skeleton = skel
    try:
        yield skel
    finally:
        Hm.skeleton = orig


@contextlib.contextmanager
def flat_eye(sc, eye_mat):
    """目のところを平らに（まさちゃん「目が二つになってるから赤バツのところはフラットにして！」）：
       目（ふくらんだアーモンド）・まゆ・下まぶたを作らない。ひたいの前のかどの丸み（光る玉に見える所）が目に見える"""
    HS = Hm.HEAD_SCALE
    ell0 = sc.ell
    skip = [(np.array([0.046, 0.017, 0.026]) * HS, 0.022), (np.array([0.034, 0.010, 0.018]) * HS, 0.016)]

    def ell(c, radii, R=None, *args, **kw):
        if kw.get('mat') == eye_mat:
            return
        r = np.asarray(radii, float)
        for rr, k in skip:
            if np.allclose(r, rr) and abs(kw.get('k', 0.0) - k) < 1e-9:
                return
        return ell0(c, radii, R, *args, **kw)
    sc.ell = ell
    try:
        yield
    finally:
        sc.ell = ell0


@contextlib.contextmanager
def slim_muscle(sc, S, f=0.38, t_top=0.88, r=(0.026, 0.040)):
    """首の横の筋（あご → 肩）：細くした首の中へ（のどの線とたてがみの線のあいだ f の所）"""
    rc0 = sc.rcone

    def rc(a_, b_, ra, rb, *args, **kw):
        a_ = np.asarray(a_, float)
        if abs(ra - 0.04) < 1e-9 and abs(rb - 0.06) < 1e-9 and abs(abs(a_[2]) - 0.075) < 1e-9:
            z = np.sign(a_[2])
            th, cr = Hm.bez(S['throat'], t_top), Hm.bez(S['crest'], t_top)
            q = th + (cr - th) * f
            th2, cr2 = Hm.bez(S['throat'], 0.12), Hm.bez(S['crest'], 0.12)
            q2 = th2 + (cr2 - th2) * f
            return rc0(np.array([q[0], q[1], 0.055 * z]), np.array([q2[0], q2[1], 0.10 * z]), r[0], r[1], *args, **kw)
        return rc0(a_, b_, ra, rb, *args, **kw)
    sc.rcone = rc
    try:
        yield
    finally:
        sc.rcone = rc0


def build_statue(sc, pose=POSE, mats=None, tail_len=1.05, slim=True):
    M = dict(body=1, neck=1, hoof=1, eye=1, head=1)
    if mats:
        M.update(mats)
    EYE_SKIP = 97
    M_build = dict(M, eye=EYE_SKIP)
    if slim:
        with slim_neck() as skel:
            S1 = skel(pose)
            with slim_muscle(sc, S1), slim_throat(sc, pose, neck_k=0.04, neck_k_from=0.3), flat_eye(sc, EYE_SKIP):
                S = Hm.build(sc, pose, mats=M_build)
    else:
        with flat_eye(sc, EYE_SKIP):
            S = Hm.build(sc, pose, mats=M_build)
    B = M['body']
    for pts, rad, gr in mane_stream(S):
        tube(sc, pts, rad, gr, mat=B, kg=0.012)
    for pts, rad, gr in forelock(S):
        tube(sc, pts, rad, gr, mat=B, kg=0.02)
    for pts, rad, gr in tail_stream(S, tail_len):
        tube(sc, pts, rad, gr, mat=B, kg=0.012)
    return S
