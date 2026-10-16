"""黄金の馬のよろい（胸当て・首輪・顔の飾り・おもがい・背中の飾り板）と宝石。オリジナルのデザイン"""
import math
import numpy as np
from h3d import nrm, basis
import horse3d as H


def build(sc, pose, S, A=3, TRIM=7, GEM=4):
    th = pose['theta']
    piv = np.array([-0.60, 1.25])
    T = lambda p: H.rot2(p, piv, th)
    TR = basis(H.v3(H.adir(th)), (0, 1, 0))     # 胴の向き
    fwd = H.v3(H.adir(th)); upv = H.v3(H.adir(th + 90))
    gems = []

    def gem(c, r, normal, ring=True):
        c = np.asarray(c, float)
        sc.sph(c, r, k=0.004, mat=GEM)
        if ring:
            sc.torus(c - nrm(normal) * r * 0.25, normal, r * 1.08, r * 0.22, k=0.004, mat=TRIM)
        gems.append((c, r))

    # ---------- 胸当て（胸の前をぐるりと覆う帯の板） ----------
    cc = H.v3(T((0.40, 1.16)))
    RAD = np.array([0.30 + 0.10, 0.32 + 0.06, 0.27 + 0.10])
    YB0, YB1 = 0.985, 1.245                       # 帯の下と上（胴の座標）

    def on_shell(x_ang, y):
        """胸の楕円体の表面の点と向き：x_ang = 前からの角度（+ が左＝カメラ側）"""
        ly = y - 1.16
        rr = math.sqrt(max(1 - (ly / RAD[1]) ** 2, 0.02))
        lx = RAD[0] * rr * math.cos(x_ang); lz = RAD[2] * rr * math.sin(x_ang)
        p = cc + TR.T @ np.array([lx, ly, lz])
        n = nrm(TR.T @ np.array([lx / RAD[0] ** 2, ly / RAD[1] ** 2, lz / RAD[2] ** 2]))
        return p, n

    sc.begin('U', 0.0, A)
    sc.ell(cc, tuple(RAD), TR, shell=0.010, mat=A)
    sc.rbox(H.v3(T((0.75, (YB0 + YB1) / 2))), (0.30, (YB1 - YB0) / 2, 0.6), 0.0, TR, op='I', k=0.0, mat=A)
    sc.ell(cc, tuple(RAD * 0.995), TR, op='I', k=0.0, mat=A)
    sc.end()
    # 上と下のふちの玉
    for yb, rb in ((YB0, 0.017), (YB1, 0.015)):
        for a in np.linspace(-1.36, 1.36, 27):
            p, n = on_shell(a, yb)
            sc.sph(p + n * 0.006, rb, k=0.008, mat=TRIM)
    # まん中の大きなメダル＋宝石、両はしの丸い飾り
    p, n = on_shell(0.0, (YB0 + YB1) / 2)
    sc.ell(p + n * 0.012, (0.016, 0.085, 0.085), basis(n, upv), k=0.01, mat=TRIM)
    sc.torus(p + n * 0.028, n, 0.068, 0.01, k=0.004, mat=TRIM)
    gem(p + n * 0.045, 0.048, n, ring=False)
    for a in (-0.42, 0.42, -0.86, 0.86):
        p, n = on_shell(a, (YB0 + YB1) / 2)
        gem(p + n * 0.02, 0.024, n)
    for a in (-1.36, 1.36):
        p, n = on_shell(a, (YB0 + YB1) / 2)
        sc.ell(p + n * 0.01, (0.02, 0.07, 0.07), basis(n, upv), k=0.01, mat=TRIM)
        gem(p + n * 0.032, 0.03, n, ring=False)
    # 帯から下がる小さな飾り（しずく形）
    for a in np.linspace(-1.1, 1.1, 9):
        p, n = on_shell(a, YB0 - 0.01)
        q = p - upv * 0.05 + n * 0.004
        sc.rcone(p + n * 0.004, q, 0.008, 0.016, k=0.006, mat=TRIM)
        gem(q - upv * 0.012 + n * 0.006, 0.014, n, ring=False)

    # ---------- 首輪（首のつけ根の太いわっか） ----------
    a = H.bez(S['crest'], 0.06); b = H.bez(S['throat'], 0.10)
    c = (a + b) / 2
    axis = H.v3(np.array([-(a - b)[1], (a - b)[0]]))
    axis = nrm(axis)
    if axis[0] < 0: axis = -axis
    R0 = np.linalg.norm(a - b) / 2
    sc.begin('U', 0.0, TRIM)
    sc.ell(H.v3(c), (0.05, R0 + 0.02, 0.20 + 0.02), basis(axis, H.v3(a - b)), shell=0.018, mat=TRIM)
    sc.rbox(H.v3(c), (0.032, 0.6, 0.6), 0.0, basis(axis, H.v3(a - b)), op='I', mat=TRIM)
    sc.end()
    for t in np.linspace(-1.2, 1.2, 5):
        ang = t
        d_up = nrm(H.v3(a - b))
        p = H.v3(c) + d_up * math.cos(ang) * (R0 + 0.035) * 0.0 + np.array([0, 0, 1.0]) * math.sin(ang) * 0.24 + d_up * math.cos(ang) * (R0 + 0.035)
        gem(p, 0.02, nrm(p - H.v3(c)))

    # ---------- 顔の飾り（ひたい〜鼻すじの板）・おもがい ----------
    U3, V3 = S['head_u'], S['head_v']
    HS = H.HEAD_SCALE
    hp = lambda s_, w, z=0.0: H.head_pt(S, s_, w, z)
    HR = basis(U3, V3)
    sc.begin('U', 0.02, A)
    sc.rbox(hp(0.17, 0.03), (0.112 * HS, 0.046 * HS, 0.10 * HS), 0.04 * HS, HR, shell=0.006, mat=A)
    sc.rbox(hp(0.36, 0.02), (0.14 * HS, 0.044 * HS, 0.074 * HS), 0.036 * HS, HR, shell=0.006, op='U', k=0.03, mat=A)
    sc.rbox(hp(0.27, 0.10), (0.23 * HS, 0.10 * HS, 0.068 * HS), 0.02 * HS, HR, op='I', k=0.008, mat=A)
    sc.end()
    sc.rcone(hp(0.10, 0.075), hp(0.46, 0.062), 0.011 * HS, 0.008 * HS, k=0.01, mat=TRIM)    # まん中のすじ
    gem(hp(0.15, 0.084), 0.026 * HS, V3)
    # 鼻革・ほお革・額革
    sc.torus(hp(0.43, -0.012), U3, 0.088 * HS, 0.011 * HS, k=0.006, mat=TRIM)
    for z in (1, -1):
        sc.rcone(hp(0.43, -0.03, 0.085 * z), hp(0.05, -0.04, 0.095 * z), 0.011 * HS, 0.011 * HS, k=0.006, mat=TRIM)
        gem(hp(0.25, -0.035, 0.103 * z), 0.017 * HS, np.array([0, 0, z]) * 1.0 + V3 * 0.0)
    sc.ctorus(hp(0.03, 0.0), U3, V3, 0.105 * HS, 0.010 * HS, 1.35, k=0.006, mat=TRIM)

    # ---------- 背中の飾り板 ----------
    bc = H.v3(T((-0.08, 1.30)))
    sc.begin('U', 0.0, A)
    sc.ell(bc, (0.50, 0.36, 0.33), TR, shell=0.008, mat=A)
    sc.rbox(H.v3(T((-0.08, 1.62))), (0.26, 0.26, 0.5), 0.05, TR, op='I', k=0.01, mat=A)
    sc.end()
    for i in range(-4, 5):
        for z in (1, -1):
            xx = -0.08 + i * 0.055
            loc_y = 0.36 * 0.0
            # 板の下のふちにそって玉を並べる
            p = H.v3(T((xx, 1.36))) + np.array([0, 0, 0.0])
            ang = math.asin(min(abs(i * 0.055) / 0.5, 0.95))
            zz = 0.33 * math.sqrt(max(1 - ((1.36 - 1.30) / 0.36) ** 2 - (i * 0.055 / 0.5) ** 2, 0.0)) + 0.012
            sc.sph(p + np.array([0, 0, zz * z]), 0.018, k=0.01, mat=TRIM)
    for z in (1, -1):
        p = H.v3(T((-0.08, 1.48)))
        zz = 0.33 * math.sqrt(max(1 - ((1.48 - 1.30) / 0.36) ** 2, 0)) + 0.012
        gem(p + np.array([0, 0, zz * z]), 0.034, np.array([0, 0.3, z]))
    return gems
