"""のど（頭と首のつなぎ目）を すっきりさせる：3Dの馬（horse3d）の作り方は変えずに、組み立てるときだけ差しかえる
   （まさちゃんが絵に引いた「あごの線」と「のどの線」に合わせるため）
   - neck_k：首をつくる楕円どうしの なめらかさ（もとは 0.12）。小さくすると、楕円のつなぎ目のふくらみが減って、
             首の前のふち（のど）が、骨組みの のどの線の上にくる（もとは そこから 8cm ほど前にふくらんでいた）
     neck_k_from：首の根元から この割合までは もとの 0.12 のまま（そこから先を neck_k へ）→ 首の根元の太さは残す
   - amount：のどの線の終わりを、ほおの下のなかから、ほおのうしろ（のど元）へ 寄せる割合（0＝もとのまま … 1）
   - jowl：ほお（あごの丸い板）と下あごの骨の、下へのふくらみを小さくする割合（0 … 1）→ あごの線がすっきり
   - chest：胸の前へのふくらみ（胸の大きな楕円・胸の筋肉）を うしろへ・うすくする割合（0 … 1）→ のどの線が そのまま前足へ
   - あごから肩へ走る首の横の筋は、amount に合わせて上の端を のど元へ寄せ、少し細くする
   with slim_throat(sc, pose, amount, neck_k, jowl) as sc2: Hm.build(sc2, pose, ...) のように使う（ぜんぶ 0／None なら、もとのまま）"""
import contextlib
import numpy as np
import horse3d as Hm


def throat_curve(S, amount=1.0, end=(0.05, -0.13), mid_pull=0.30):
    """新しいのどの線（4つの点）：はじめの2点（胸の前）はそのまま、終わりは頭の (s, w) の点（のど元）の方へ"""
    P = np.asarray(S['throat'], float).copy()
    C = np.asarray(S['crest'], float)
    p3 = Hm.head_pt(S, end[0], end[1])[:2]
    q3 = P[3] + (p3 - P[3]) * amount
    q2 = P[2] + ((P[2] + (C[2] - P[2]) * mid_pull) - P[2]) * amount       # まん中の点を たてがみがわへ少しよせる
    q2 = q2 + (q3 - P[3]) * 0.35 * amount
    return np.array([P[0], P[1], q2, q3])


def _same(a, b, tol=1e-6):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol)


@contextlib.contextmanager
def slim_throat(sc, pose, amount=0.0, neck_k=None, neck_k_from=0.0, jowl=0.0, chest=0.0, end=(0.05, -0.13), mid_pull=0.30, muscle_top=(0.10, -0.12), muscle_r=0.03):
    """組み立てのあいだだけ、skeleton() と いくつかの形（首の楕円・首の横の筋・ほお・下あごの骨）を差しかえる"""
    if amount <= 0 and neck_k is None and jowl <= 0 and chest <= 0:
        yield sc
        return
    orig = Hm.skeleton

    def skel(p):
        S = orig(p)
        if amount > 0:
            S['throat'] = throat_curve(S, amount, end, mid_pull)
        return S

    S1 = skel(pose)
    HS = Hm.HEAD_SCALE
    hp = lambda s_, w_, z=0.0: Hm.head_pt(S1, s_, w_, z)
    a_old = hp(0.26, -0.12)[:2]
    a_new = hp(muscle_top[0], muscle_top[1])[:2]
    rc0, ell0 = sc.rcone, sc.ell
    nk = [0]                                                           # 首の楕円の番号（0 … 29：き甲 → うなじ）

    def rc(a_, b_, ra, rb, *args, **kw):
        a_ = np.asarray(a_, float)
        # 首の横の筋（あご → 肩）
        if amount > 0 and abs(ra - 0.04) < 1e-9 and abs(rb - 0.06) < 1e-9 and abs(abs(a_[2]) - 0.075) < 1e-9 and _same(a_[:2], a_old):
            a2 = a_old + (a_new - a_old) * amount
            return rc0(np.array([a2[0], a2[1], np.sign(a_[2]) * 0.06]), b_, ra + (muscle_r - ra) * amount, rb, *args, **kw)
        # 下あごの骨：うしろの端を少し上へ（ほおの下のふくらみを小さく）
        if jowl > 0 and abs(ra - 0.035 * HS) < 1e-9 and abs(rb - 0.026 * HS) < 1e-9:
            for z in (1, -1):
                if _same(a_, hp(0.25, -0.20, 0.045 * z)):
                    return rc0(hp(0.25, -0.20 + 0.04 * jowl, 0.045 * z), b_, ra * (1 - 0.15 * jowl), rb, *args, **kw)
        return rc0(a_, b_, ra, rb, *args, **kw)

    def ell(c, radii, R=None, *args, **kw):
        radii = np.asarray(radii, float)
        k = kw.get('k', 0.0)
        # 首の楕円（長さ 0.07／0.06・なめらかさ 0.12）
        if neck_k is not None and abs(k - 0.12) < 1e-9 and (abs(radii[0] - 0.07) < 1e-9 or abs(radii[0] - 0.06) < 1e-9):
            nk[0] += 1
            t = nk[0] / 29.0
            kw = dict(kw)
            kw['k'] = float(np.interp(t, [0.0, neck_k_from, min(1.0, neck_k_from + 0.25), 1.0], [0.12, 0.12, neck_k, neck_k])) if neck_k_from > 0 else neck_k
            return ell0(c, radii, R, *args, **kw)
        # 胸（前へのふくらみ）：胸の大きな楕円と、胸の筋肉（左右）を少しうしろへ・うすく
        if chest > 0 and R is not None and abs(k - 0.14) < 1e-9 and _same(radii, (0.30, 0.32, 0.27)):
            ax = np.asarray(R, float)[0]
            return ell0(np.asarray(c, float) - ax * 0.02 * chest, radii - np.array([0.04, 0.0, 0.0]) * chest, R, *args, **kw)
        if chest > 0 and R is not None and abs(k - 0.12) < 1e-9 and _same(radii, (0.11, 0.17, 0.10)):
            ax = np.asarray(R, float)[0]
            return ell0(np.asarray(c, float) - ax * 0.035 * chest, radii - np.array([0.04, 0.0, 0.0]) * chest, R, *args, **kw)
        # ほお（丸い板）：下のふち（w=-0.23）を上へ
        if jowl > 0 and _same(radii, np.array([0.125, 0.115, 0.05]) * HS):
            for z in (1, -1):
                if _same(c, hp(0.215, -0.115, 0.058 * z)):
                    ry = 0.115 - 0.035 * jowl
                    return ell0(hp(0.215, -0.115 + 0.015 * jowl, 0.058 * z), np.array([0.125, ry, 0.05]) * HS, R, *args, **kw)
        return ell0(c, radii, R, *args, **kw)

    Hm.skeleton = skel
    sc.rcone, sc.ell = rc, ell
    try:
        yield sc
    finally:
        Hm.skeleton = orig
        sc.rcone, sc.ell = rc0, ell0
