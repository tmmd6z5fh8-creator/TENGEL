"""神様的中 ③ の うしろの 鳥居（第4.49版）：朱ぬりの 明神鳥居を 本当の 立体（三角の 面）で 作って、z バッファで 1コマずつ 描く。
   まさちゃん「⛩️ももっとリアルに豪華な感じにして！」
   → 柱は まるい 朱の 漆（つや：まわりの 金の 光が 映る）・笠木は 黒い 漆・島木と 貫と 額束は 朱・
     台輪・柱の 帯・笠木と 島木と 貫の 端の 飾り金具（彫りの 線と 鋲・端の 面に 丸い 紋）・笠木の ふちの 線は 金・
     額は 金の わく（鋲つき）に 黒い 漆・もり上がった 金の「天眼」・額は 上が 少し 前へ かたむく（本物の 額の ように）。
   単位：柱と 柱の あいだ＝1（D）。x 右・y 下・z おく。原点＝柱の まん中の 線の 上（笠木の 下の あたり）の まん中
   render(...) → 画面の (premultiplied 色, alpha)。形は 1回だけ 作る（build）"""
import math
import numpy as np
import cv2
import kami_art as KA

VER, BLK, GOLD, CAP, CAPEND, PLQ = 0, 1, 2, 3, 4, 5      # 材料：朱の 漆・黒の 漆・金・金の 飾り金具（彫り）・金具の 端の 面（紋）・額の 前の 面

PR = .05             # 柱の 半径
HP = 3.1             # 柱の 長さ（下は 画面の 外）
LEAN = .02           # 柱の かたむき（下ほど 外へ：内転び）
LK = .72             # 笠木の 長さの 半分
SORI = .056          # 反り（笠木の 端で 上がる 量）
SHI_H, SHI_D, SHI_L = .066, .094, .65          # 島木：高さ・おく行き・長さの 半分
KAS_H, KAS_D = .084, .132                      # 笠木：高さ・おく行き
NUKI_Y, NUKI_H, NUKI_D, NUKI_L = .36, .074, .052, .68   # 貫：まん中の y・高さ・おく行き・長さの 半分
CAP_L = .062         # 笠木の 端の 金具の 長さ
PLQ_W, PLQ_H, PLQ_T, PLQ_TILT = .2, .3, .034, 8.0       # 額：はば・高さ・厚み・前への かたむき（度）
SHI_Y0 = -.05        # 島木の 下（まん中）


def curve(x):
    """反り（端ほど 上：y は 下向き なので 引く 量）"""
    return SORI * (np.abs(x) / LK) ** 2.2


TOP_Y = SHI_Y0 - float(curve(.5)) + .05       # 柱の 上の はし（台輪の 下）：台輪の 上が 島木の 下に とどく


# ---------------------------------------------------------------- 形の 道具
class Mesh:
    def __init__(self):
        self.V, self.N, self.U, self.F, self.M = [], [], [], [], []
        self.n = 0

    def add(self, V, N, U, F, M):
        V = np.asarray(V, np.float64).reshape(-1, 3)
        F = np.asarray(F, np.int64).reshape(-1, 3) + self.n
        self.V.append(V)
        self.N.append(np.asarray(N, np.float64).reshape(-1, 3))
        self.U.append(np.asarray(U, np.float64).reshape(-1, 2))
        self.F.append(F)
        self.M.append(np.full(len(F), M, np.int32) if np.isscalar(M) else np.asarray(M, np.int32))
        self.n += len(V)

    def done(self):
        N = np.concatenate(self.N)
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
        return dict(V=np.concatenate(self.V), N=N, U=np.concatenate(self.U), F=np.concatenate(self.F), M=np.concatenate(self.M))


def grid_faces(nr, k, wrap):
    i, j = np.meshgrid(np.arange(nr - 1), np.arange(k if wrap else k - 1), indexing='ij')
    i, j = i.ravel(), j.ravel()
    j1 = (j + 1) % k
    a, b, c, d = i * k + j, i * k + j1, (i + 1) * k + j1, (i + 1) * k + j
    return np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])


def rrect(ha, hb, rf, nf=5):
    """角の まるい 四角の 断面：(点 (k,2), 外向きの 法線, 周の 割合)。さいごに はじめの 点を もう 一度（つなぎ目で 周の 割合が とばない）"""
    pts, nrm = [], []
    for ca, cb, a0 in ((ha - rf, hb - rf, 0.0), (-ha + rf, hb - rf, 90.0), (-ha + rf, -hb + rf, 180.0), (ha - rf, -hb + rf, 270.0)):
        for a in np.radians(np.linspace(a0, a0 + 90, nf)):
            pts.append((ca + rf * math.cos(a), cb + rf * math.sin(a)))
            nrm.append((math.cos(a), math.sin(a)))
    pts.append(pts[0])
    nrm.append(nrm[0])
    pts, nrm = np.array(pts), np.array(nrm)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    per = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()
    return pts, nrm, per


def sweep(mesh, P, A, B, sec, mat, caps=(True, True), cap_mat=None, sa=None, sb=None, rev=False):
    """道 P (n,3) に そって 断面 sec を ならべる（A, B：断面の 軸 (n,3)）。sa, sb：断面の 大きさの 倍率 (n,)。
       UV＝(道の 長さ, 周の 割合)。端の 面の UV＝断面の 座標 (a, b)"""
    pts, nr, per = sec
    n, k = len(P), len(pts)
    sa = np.ones(n) if sa is None else np.asarray(sa)
    sb = np.ones(n) if sb is None else np.asarray(sb)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    pa = pts[None, :, 0] * sa[:, None]
    pb = pts[None, :, 1] * sb[:, None]
    V = P[:, None, :] + pa[..., None] * A[:, None, :] + pb[..., None] * B[:, None, :]
    N = nr[None, :, 0, None] * A[:, None, :] + nr[None, :, 1, None] * B[:, None, :]
    N = N - np.sum(N * T[:, None, :], -1, keepdims=True) * T[:, None, :]
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    U = np.stack(np.broadcast_arrays(L[:, None], per[None, :]), -1)
    mesh.add(V, N, U, grid_faces(n, k, False), mat)
    for end, on in ((0, caps[0]), (n - 1, caps[1])):
        if not on:
            continue
        ring = V[end, :-1]
        c = ring.mean(0)
        nn = -T[end] if end == 0 else T[end]
        Vc = np.concatenate([c[None], ring])
        Nc = np.repeat(nn[None], len(Vc), 0)
        sc_ = min(np.abs(pa[end]).max(), np.abs(pb[end]).max())                # 小さい 方の 半分の はばで わる（紋の 大きさを そろえる）
        Uc = np.concatenate([[[0.0, 0.0]], np.stack([pa[end, :-1], pb[end, :-1]], 1) / sc_])
        F = [(0, 1 + j, 1 + (j + 1) % (k - 1)) for j in range(k - 1)]
        mesh.add(Vc, Nc, Uc, F, cap_mat if cap_mat is not None else mat)


def ring_face(mesh, P, A, B, sec_in, sec_out, nn, mat):
    """太さの ちがう 2つの 断面の あいだの 輪の 面（金具の ふち）"""
    pi, po = sec_in[0], sec_out[0]
    k = len(pi)
    Vi = P + pi[:, 0, None] * A + pi[:, 1, None] * B
    Vo = P + po[:, 0, None] * A + po[:, 1, None] * B
    V = np.concatenate([Vi, Vo])
    N = np.repeat(np.asarray(nn, np.float64)[None], 2 * k, 0)
    U = np.zeros((2 * k, 2))
    F = []
    for j in range(k - 1):
        F += [(j, j + 1, k + j + 1), (j, k + j + 1, k + j)]
    mesh.add(V, N, U, F, mat)


def lathe(mesh, segs, top, axis, e1, e2, nseg=72):
    """まわして 作る 形（柱）：segs＝[(点 [(半径, 軸に そった 長さ)], 材料)]。軸の 上の 点 top から 下向きの 軸 axis へ"""
    th = np.linspace(0, 2 * math.pi, nseg + 1)
    rad = np.cos(th)[:, None] * e1[None, :] + np.sin(th)[:, None] * e2[None, :]
    for pts, mat in segs:
        pts = np.asarray(pts, np.float64)
        d = np.gradient(pts, axis=0)
        n2 = np.stack([d[:, 1], -d[:, 0]], 1)
        n2 /= np.linalg.norm(n2, axis=1, keepdims=True) + 1e-12
        V = top[None, None, :] + pts[:, 1, None, None] * axis[None, None, :] + pts[:, 0, None, None] * rad[None, :, :]
        N = n2[:, 0, None, None] * rad[None] + n2[:, 1, None, None] * axis[None, None, :]
        U = np.stack(np.broadcast_arrays(th[None, :] / (2 * math.pi), pts[:, 1, None]), -1)
        mesh.add(V, N, U, grid_faces(len(pts), nseg + 1, False), mat)


def band(r0, r1, s0, s1, rr, n=5):
    """柱に まく 帯の 断面（柱の 面 r0 から 外へ r1：外の かどは まるく）"""
    pts = [(r0, s0)]
    for a in np.linspace(-math.pi / 2, 0, n):
        pts.append((r1 - rr + rr * math.cos(a), s0 + rr + rr * math.sin(a)))
    for a in np.linspace(0, math.pi / 2, n):
        pts.append((r1 - rr + rr * math.cos(a), s1 - rr + rr * math.sin(a)))
    pts.append((r0, s1))
    return pts


# ---------------------------------------------------------------- 鳥居の 形（1回だけ）
def build():
    m = Mesh()
    ex, ey, ez = np.eye(3)
    # 柱（台輪・帯・根巻き）
    for sgn in (-1, 1):
        top = np.array([sgn * .5, TOP_Y, 0.0])
        axis = np.array([sgn * LEAN, 1.0, 0.0])
        axis /= np.linalg.norm(axis)
        e1 = np.array([axis[1], -axis[0], 0.0]) * sgn
        segs = [(band(PR, PR + .019, -.05, 0.0, .009, 6), GOLD),          # 台輪（金）
                ([(PR, 0.0), (PR, .292)], VER),
                (band(PR, PR + .0045, .292, .31, .003), GOLD),
                ([(PR, .31), (PR, .41)], VER),
                (band(PR, PR + .0045, .41, .428, .003), GOLD),
                ([(PR, .428), (PR, HP - .175)], VER),
                (band(PR, PR + .006, HP - .175, HP - .158, .004), GOLD),
                (band(PR, PR + .009, HP - .158, HP, .006), BLK)]        # 根巻き（黒）
        lathe(m, segs, top, axis, e1, ez, 72)
    # 島木（朱）と 笠木（黒）：反り
    def beam(L, nx, ybase, h, d, mat, grow=0.0, rf=.006):
        xs = np.linspace(-L, L, nx)
        g = grow * (np.abs(xs) / LK) ** 4
        yc = ybase - curve(xs) - h / 2 * g
        P = np.stack([xs, yc, np.zeros(nx)], 1)
        A = np.repeat(ey[None], nx, 0)
        B = np.repeat(ez[None], nx, 0)
        sweep(m, P, A, B, rrect(h / 2, d / 2, rf), mat, caps=(False, False), sa=1 + g)
        return xs
    beam(SHI_L - .045, 70, SHI_Y0 - SHI_H / 2, SHI_H, SHI_D, VER)
    kas_y = SHI_Y0 - SHI_H - KAS_H / 2
    beam(LK - CAP_L + .002, 90, kas_y, KAS_H, KAS_D, BLK, grow=.16, rf=.008)
    # 笠木の ふちの 金の 線（前の 下の かど・前の 上の かど：上は 端ほど 高く なる 分も）
    xs = np.linspace(-(LK - CAP_L), LK - CAP_L, 80)
    g = .16 * (np.abs(xs) / LK) ** 4
    for yy in (kas_y + KAS_H / 2 - .005 - curve(xs), kas_y - KAS_H / 2 + .005 - curve(xs) - KAS_H * g):
        P = np.stack([xs, yy, np.full(len(xs), -KAS_D / 2 + .0015)], 1)
        sweep(m, P, np.repeat(ey[None], len(xs), 0), np.repeat(ez[None], len(xs), 0), rrect(.0042, .0042, .0041, 4), GOLD, caps=(False, False))
    # 端の 飾り金具（笠木・島木・貫）
    def caps(xa, xb, yfun, h, d, grow, e, nx=10, rf=.008):
        for sgn in (-1, 1):
            xs = sgn * np.linspace(xa, xb, nx)                     # 内 → 外（UV の 長さ＝内から）
            g = grow * (np.abs(xs) / LK) ** 4
            yc = yfun(xs) - h / 2 * g
            P = np.stack([xs, yc, np.zeros(nx)], 1)
            A = np.repeat(ey[None], nx, 0)
            B = np.repeat(ez[None], nx, 0)
            sec_o = rrect(h / 2 + e, d / 2 + e, rf + e)
            sweep(m, P, A, B, sec_o, CAP, caps=(False, True), cap_mat=CAPEND, sa=(1 + g * (h / 2) / (h / 2 + e)))
            ring_face(m, P[0], A[0], B[0], rrect(h / 2 * (1 + g[0]), d / 2, rf), rrect((h / 2 + e) * (1 + g[0]), d / 2 + e, rf + e),
                      -np.array([sgn, 0.0, 0.0]), CAP)
    caps(LK - CAP_L, LK, lambda xs: kas_y - curve(xs), KAS_H, KAS_D, .16, .004)
    caps(SHI_L - .047, SHI_L, lambda xs: SHI_Y0 - SHI_H / 2 - curve(xs), SHI_H, SHI_D, 0.0, .0035, nx=8)
    # 貫（朱：まっすぐ・端は 金具）
    nl = NUKI_L - .036
    P = np.array([[-nl, NUKI_Y, 0.0], [nl, NUKI_Y, 0.0]])
    sweep(m, P, np.repeat(ey[None], 2, 0), np.repeat(ez[None], 2, 0), rrect(NUKI_H / 2, NUKI_D / 2, .005), VER, caps=(False, False))
    caps(nl - .002, NUKI_L, lambda xs: np.full_like(xs, NUKI_Y), NUKI_H, NUKI_D, 0.0, .003, nx=2, rf=.005)
    # 楔（黒：貫が 柱を ぬける 外の 所）
    for sgn in (-1, 1):
        xk = sgn * (.5 + LEAN * (NUKI_Y - TOP_Y) + PR + .013)
        P = np.array([[xk, NUKI_Y - .062, 0.0], [xk, NUKI_Y + .062, 0.0]])
        sweep(m, P, np.repeat(ex[None], 2, 0), np.repeat(ez[None], 2, 0), rrect(.0125, .031, .003), VER)
    # 額束（朱）
    P = np.array([[0.0, SHI_Y0 - .004, 0.0], [0.0, NUKI_Y - NUKI_H / 2 + .002, 0.0]])
    sweep(m, P, np.repeat(ex[None], 2, 0), np.repeat(ez[None], 2, 0), rrect(.035, .022, .004), VER, caps=(False, False))
    # 額（金の わく＋前の 面）：上が 前へ かたむく（下の ふちを 軸に）
    m2 = Mesh()
    yc_p = (SHI_Y0 + NUKI_Y - NUKI_H / 2) / 2
    y0p, y1p = yc_p - PLQ_H / 2, yc_p + PLQ_H / 2
    zf = -.03 - PLQ_T                                             # 前の 面
    P = np.array([[0.0, y0p, zf + PLQ_T / 2], [0.0, y1p, zf + PLQ_T / 2]])
    sweep(m2, P, np.repeat(ex[None], 2, 0), np.repeat(ez[None], 2, 0), rrect(PLQ_W / 2, PLQ_T / 2, .007), GOLD)
    ix, iy = PLQ_W / 2 - .004, PLQ_H / 2 - .004
    Vq = np.array([[-ix, yc_p - iy, zf - .0004], [ix, yc_p - iy, zf - .0004], [ix, yc_p + iy, zf - .0004], [-ix, yc_p + iy, zf - .0004]])
    m2.add(Vq, np.repeat(-ez[None], 4, 0), [[0, 0], [1, 0], [1, 1], [0, 1]], [(0, 1, 2), (0, 2, 3)], PLQ)
    g2 = m2.done()
    a = math.radians(PLQ_TILT)
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    piv = np.array([0.0, y1p, zf + PLQ_T])
    g2['V'] = (g2['V'] - piv) @ Rx.T + piv
    g2['N'] = g2['N'] @ Rx.T
    out = m.done()
    nb = len(out['V'])
    for key in ('V', 'N', 'U', 'M'):
        out[key] = np.concatenate([out[key], g2[key]])
    out['F'] = np.concatenate([out['F'], g2['F'] + nb])
    out['plq'] = dict(Rx=Rx, piv=piv, yc=yc_p)
    return out


# ---------------------------------------------------------------- 額の 前の 面の 絵（高さ・金の 所）
def plaque_tex():
    TW, TH = 360, 540
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    de = np.minimum(np.minimum(xx, TW - 1 - xx), np.minimum(yy, TH - 1 - yy))
    fw = 32.0
    t = np.clip(de / fw, 0, 1)
    h = np.where(de < fw, .55 + .45 * np.sin(t * math.pi) - .25 * np.exp(-((t - .5) / .09) ** 2), 0.0).astype(np.float32)
    g = (de < fw).astype(np.float32)
    bead = np.exp(-((de - (fw + 9)) / 2.0) ** 2)                 # 内の 細い 金の 線
    h += .32 * bead
    g = np.maximum(g, np.clip(bead * 1.6 - .2, 0, 1))
    # わくの 鋲（まん中の 線に そって）
    cl = fw * .5
    per = []
    for x in np.arange(cl + 26, TW - cl - 20, 38):
        per += [(x, cl), (x, TH - 1 - cl)]
    for y in np.arange(cl + 26, TH - cl - 20, 40):
        per += [(cl, y), (TW - 1 - cl, y)]
    per += [(cl, cl), (TW - 1 - cl, cl), (cl, TH - 1 - cl), (TW - 1 - cl, TH - 1 - cl)]
    stud = np.zeros_like(h)
    for x, y in per:
        stud = np.maximum(stud, np.clip(1 - ((xx - x) ** 2 + (yy - y) ** 2) / 5.5 ** 2, 0, 1))
    h += .5 * np.sqrt(stud)
    # 天眼（もり上がった 金の 字）
    its, boxes = [], []
    for j, c in enumerate('天眼'):
        it, bx, w = KA.run([(c, 1.0)], 0.0, 880.0 + j * 1000)
        its += it
        boxes.append(bx)
    box = KA.union_box(*boxes)
    fh = TH - 2 * (fw + 30)
    kk = fh / (box[3] - box[1])
    tm = KA.mask(its, box, kk, 0)
    th_, tw_ = tm.shape
    L = np.zeros((TH, TW), np.float32)
    ty, tx = (TH - th_) // 2, (TW - tw_) // 2
    L[ty:ty + th_, tx:tx + tw_] = tm[:TH - ty, :TW - tx]
    dl = KA.dist_in(L)
    h += .75 * KA.bevel(dl, 7.0) * (L > .5) + .0 * L
    g = np.maximum(g, L)
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), .9)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    nz = KA.fbm(TH, TW, 6, 4411, 4, .55).astype(np.float32)
    return dict(g=g.astype(np.float32), gx=gx, gy=gy, nz=nz, TW=TW, TH=TH)


# ---------------------------------------------------------------- 描く（z バッファ）
def rasterize(xy, iz, F, Wb, Hb):
    """三角を 画素へ：xy (n,2)（画素）・iz (n,)＝1/z。→ (1/z の 地図（0＝何も ない）, 三角の 番号, 重み w0, w1（画面の 上の））"""
    zb = np.zeros((Hb, Wb), np.float32)
    tid = np.full((Hb, Wb), -1, np.int32)
    B0 = np.zeros((Hb, Wb), np.float32)
    B1 = np.zeros((Hb, Wb), np.float32)
    T = xy[F]
    Z = iz[F]
    x0 = np.maximum(np.floor(T[..., 0].min(1) - .5).astype(np.int64), 0)
    x1 = np.minimum(np.ceil(T[..., 0].max(1) - .5).astype(np.int64), Wb - 1)
    y0 = np.maximum(np.floor(T[..., 1].min(1) - .5).astype(np.int64), 0)
    y1 = np.minimum(np.ceil(T[..., 1].max(1) - .5).astype(np.int64), Hb - 1)
    ok = np.flatnonzero((x1 >= x0) & (y1 >= y0))
    for i in ok:
        (ax, ay), (bx, by), (cx, cy) = T[i]
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9:
            continue
        xs = np.arange(x0[i], x1[i] + 1, dtype=np.float32) + .5
        ys = np.arange(y0[i], y1[i] + 1, dtype=np.float32)[:, None] + .5
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / d
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / d
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-5) & (w1 >= -1e-5) & (w2 >= -1e-5)
        if not ins.any():
            continue
        z = w0 * Z[i, 0] + w1 * Z[i, 1] + w2 * Z[i, 2]
        sl = (slice(y0[i], y1[i] + 1), slice(x0[i], x1[i] + 1))
        up = ins & (z > zb[sl])
        if not up.any():
            continue
        zb[sl] = np.where(up, z, zb[sl])
        tid[sl] = np.where(up, i, tid[sl])
        B0[sl] = np.where(up, w0, B0[sl])
        B1[sl] = np.where(up, w1, B1[sl])
    return zb, tid, B0, B1


GOLDC = np.float32([1.0, .8, .43])
VERC = np.float32([.86, .2, .075])
BLKC = np.float32([.03, .024, .02])
KEY_L = np.array([-.42, -.8, -.43])
KEY_L /= np.linalg.norm(KEY_L)
KEY_C = np.float32([1.0, .9, .74])


def _rnd(x, w):
    """ほぼ 一様な ばらつき（場所の 関数）"""
    return np.sin(x * 12.9898 + w * 78.233) * 43758.5453 % 1.0


def render(geo, tex, R, T, Dsc, W, H, focal, cx, cy, env, env_rot=0.0, ss=2, key=1.0):
    """鳥居を 描く：R, T（鳥居の 座標 → カメラ）・Dsc（D の 大きさ：1000 単位）。env(向き, rot, 0＝はっきり 1＝少し ぼけ 2＝まわりの 光)→色。
       → (premultiplied 色 (H,W,3), alpha (H,W))"""
    V = geo['V'] * Dsc @ R.T + T
    Nw = geo['N'] @ R.T
    F = geo['F']
    z = V[:, 2]
    xy = np.stack([focal * V[:, 0] / z + cx, focal * V[:, 1] / z + cy], 1) * ss
    iz = (1.0 / z).astype(np.float64)
    # うら 向きの 三角を すてる（3つの 点の 法線が どれも うら）
    vd = V / np.linalg.norm(V, axis=1, keepdims=True)
    face = np.einsum('ij,ij->i', Nw, vd) < .06
    keep = face[F].any(1)
    Wb, Hb = W * ss, H * ss
    T2 = xy[F]
    inb = (T2[..., 0].max(1) >= 0) & (T2[..., 0].min(1) < Wb) & (T2[..., 1].max(1) >= 0) & (T2[..., 1].min(1) < Hb)
    sel = np.flatnonzero(keep & inb)
    Fs = F[sel]
    zb, tid, B0, B1 = rasterize(xy, iz, Fs, Wb, Hb)
    cov = tid >= 0
    idx_all = np.flatnonzero(cov)
    rgb = np.zeros((Hb * Wb, 3), np.float32)
    for c0 in range(0, len(idx_all), 600000):                              # 少しずつ（メモリを 使いすぎない）
        idx = idx_all[c0:c0 + 600000]
        t_ = tid.ravel()[idx]
        f = Fs[t_]
        w0 = B0.ravel()[idx].astype(np.float64)
        w1 = B1.ravel()[idx].astype(np.float64)
        w2 = 1 - w0 - w1
        i0, i1, i2 = iz[f[:, 0]], iz[f[:, 1]], iz[f[:, 2]]
        izp = w0 * i0 + w1 * i1 + w2 * i2
        p0, p1, p2 = w0 * i0 / izp, w1 * i1 / izp, w2 * i2 / izp            # 遠近を 正しく した 重み
        N = Nw[f[:, 0]] * p0[:, None] + Nw[f[:, 1]] * p1[:, None] + Nw[f[:, 2]] * p2[:, None]
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
        U = geo['U'][f[:, 0]] * p0[:, None] + geo['U'][f[:, 1]] * p1[:, None] + geo['U'][f[:, 2]] * p2[:, None]
        mat = geo['M'][sel][t_]
        ys, xs = np.divmod(idx, Wb)
        zz = 1.0 / izp
        P = np.stack([((xs + .5) / ss - cx) / focal * zz, ((ys + .5) / ss - cy) / focal * zz, zz], 1)
        Vd = P / np.linalg.norm(P, axis=1, keepdims=True)
        vn = np.sum(Vd * N, 1)
        N = np.where((vn > 0)[:, None], N - 2 * vn[:, None] * N, N)          # うらの 法線は 返す
        loc = (P - T) @ R / Dsc                                              # 鳥居の 座標
        # 金具の 彫り（線・鋲）・端の 紋・額の 絵：法線を ずらす
        cav = np.zeros(len(idx))
        gmix = np.zeros(len(idx))
        m = mat == CAP
        if m.any():
            u = U[m, 0] / CAP_L                                              # 0＝内 → 1＝外
            v = U[m, 1]
            hgt, du, dv = _cap_pattern(u, v)
            tp = np.sign(loc[m, 0])[:, None] * R[:, 0][None, :]
            tq = np.cross(tp, N[m])
            tq /= np.linalg.norm(tq, axis=1, keepdims=True) + 1e-12
            N[m] = N[m] - tp * (du * 1.0)[:, None] - tq * (dv * 1.0)[:, None]
            cav[m] = np.clip(-hgt, 0, 1)
        m = mat == CAPEND
        if m.any():
            a, b = U[m, 0], U[m, 1]
            r = np.sqrt(a * a + b * b) + 1e-9
            prof = lambda r_: .9 * np.exp(-((r_ - .56) / .08) ** 2) + 1.0 / (1 + np.exp((r_ - .32) / .03)) - .6 * np.exp(-((r_ - .76) / .04) ** 2)
            dr = (prof(r + 1e-3) - prof(r - 1e-3)) / 2e-3 * .07
            ua = R[:, 1][None, :] * (a / r)[:, None] + R[:, 2][None, :] * (b / r)[:, None]
            N[m] = N[m] - ua * dr[:, None]
            cav[m] = np.clip(.6 * np.exp(-((r - .76) / .04) ** 2), 0, 1)
        m = mat == PLQ
        if m.any():
            uu = np.clip(U[m, 0], 0, 1) * (tex['TW'] - 1.001)
            vv = np.clip(U[m, 1], 0, 1) * (tex['TH'] - 1.001)
            smp = lambda a_: _bilin(a_, uu, vv)
            gmix[m] = smp(tex['g'])
            gx, gy = smp(tex['gx']), smp(tex['gy'])
            Rp = R @ geo['plq']['Rx']
            N[m] = N[m] - (Rp[:, 0][None, :] * gx[:, None] + Rp[:, 1][None, :] * gy[:, None]) * 4.0
            cav[m] = .25 * smp(tex['nz']) * (1 - gmix[m])
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
        vn = np.sum(Vd * N, 1)
        cosv = np.clip(-vn, 0, 1)
        Rr = Vd - 2 * vn[:, None] * N
        Rr = Rr + (P - T) / 5200.0
        Rr /= np.linalg.norm(Rr, axis=1, keepdims=True)
        Hh = KEY_L[None, :] - Vd
        Hh /= np.linalg.norm(Hh, axis=1, keepdims=True)
        ndl = np.clip(N @ KEY_L, 0, 1)
        ndh = np.clip(np.sum(N * Hh, 1), 0, 1)
        yl = loc[:, 1]
        fall = (1 - .5 * np.clip((yl - .5) / 1.8, 0, 1)) * key                # 上から の 光（下ほど 暗い）
        e_sharp = env(Rr, env_rot, 0).astype(np.float32)
        e_soft = env(Rr, env_rot, 1).astype(np.float32)
        e_dif = env(N, env_rot, 2).astype(np.float32)
        col = np.zeros((len(idx), 3), np.float32)
        isg = (mat == GOLD) | (mat == CAP) | (mat == CAPEND)
        gm = np.where(isg, 1.0, gmix)                                        # 金の 割合
        # 漆（朱・黒）
        alb = np.where((mat == VER)[:, None], VERC[None, :], BLKC[None, :])
        F0 = np.where(mat == VER, .045, .07)                                   # 黒い 漆は 映りこみを 少し 強く（つやを 見せる）
        Fr = (F0 + (1 - F0) * (1 - cosv) ** 5).astype(np.float32)
        base = alb * (e_dif * .55 + (ndl * .7 * fall)[:, None] * KEY_C + .03)
        lac = base * (1 - Fr)[:, None] + e_soft * (Fr * .95)[:, None] + ((ndh ** 260) * 2.4 * fall)[:, None].astype(np.float32) * KEY_C
        lac = lac + ((ndh ** 40) * .1 * fall)[:, None].astype(np.float32) * KEY_C * alb * 3
        lac = lac + ((ndh ** 18) * .07 * fall * (mat == BLK))[:, None].astype(np.float32) * KEY_C   # 黒い 漆の やわらかい つや
        # 金
        gold = e_sharp * GOLDC * .95 + ((ndh ** 70) * 1.7 * fall)[:, None].astype(np.float32) * KEY_C * GOLDC + e_dif * GOLDC * .12
        gold = gold * (.62 + .45 * fall)[:, None].astype(np.float32)
        col = lac * (1 - gm)[:, None].astype(np.float32) + gold * gm[:, None].astype(np.float32)
        col *= (1 - .75 * np.clip(cav, 0, 1))[:, None].astype(np.float32)
        # もや（下ほど）
        hz = (.05 + .12 * np.clip((yl - .7) / 1.9, 0, 1))[:, None].astype(np.float32)
        col = col * (1 - hz) + hz * np.float32([.13, .055, .016])
        rgb[idx] = col
    rgb = rgb.reshape(Hb, Wb, 3)
    # かさなりの かげ（奥行きの ぼかしとの 差：まわりより おくに ある 所を 暗く）
    if len(idx_all):
        dep = np.where(cov, 1.0 / np.maximum(zb, 1e-9), 0).astype(np.float32)
        far = float(dep[cov].max()) + 3000.0
        dep = np.where(cov, dep, far)
        sm = cv2.resize(dep, (Wb // 8, Hb // 8), interpolation=cv2.INTER_AREA)
        bl = cv2.resize(cv2.GaussianBlur(sm, (0, 0), 3.0), (Wb, Hb), interpolation=cv2.INTER_LINEAR)
        ao = np.clip((dep - bl) / (Dsc * .07), 0, 1)
        rgb *= (1 - .55 * ao * cov)[..., None]
    a = cov.astype(np.float32)
    rgba = np.dstack([rgb * a[..., None], a])
    if ss > 1:
        rgba = cv2.resize(rgba, (W, H), interpolation=cv2.INTER_AREA)
    return rgba[..., :3].copy(), rgba[..., 3].copy()


def _bilin(a, u, v):
    """絵 a を (u, v)（画素）で なめらかに 読む"""
    u0 = np.floor(u).astype(np.int64)
    v0 = np.floor(v).astype(np.int64)
    fu, fv = u - u0, v - v0
    return (a[v0, u0] * (1 - fu) + a[v0, u0 + 1] * fu) * (1 - fv) + (a[v0 + 1, u0] * (1 - fu) + a[v0 + 1, u0 + 1] * fu) * fv


def _cap_pattern(u, v):
    """飾り金具の 彫り：内と 外の はしの 近くに 線・まん中に 鋲の ならび → (高さ（-1〜1）, d/du, d/dv)（法線の ずれ）"""
    def f(u_, v_):
        h = -np.exp(-((u_ - .14) / .03) ** 2) - np.exp(-((u_ - .86) / .03) ** 2) - .7 * np.exp(-((u_ - .22) / .02) ** 2)
        vv = (v_ * 15.0) % 1.0 - .5
        h = h + 1.2 * np.exp(-(((u_ - .55) / .1) ** 2 + (vv / .16) ** 2))
        h = h + .35 * np.sin(v_ * 2 * math.pi * 30) * np.exp(-((u_ - .55) / .2) ** 2) * .3
        return h
    e = 1e-3
    h = f(u, v)
    du = (f(u + e, v) - f(u - e, v)) / (2 * e) * .006 / CAP_L
    dv = (f(u, v + e) - f(u, v - e)) / (2 * e) * .006 / .4
    return h, du, dv
