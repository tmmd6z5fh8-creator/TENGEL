"""紫電（sd）の 顔 第2稿（Meshy の 馬 Violet_Nightmare・まさちゃん 09:54・10:13）
   ・まつ毛を 消す：上まぶたから 出て いる 細い 管（左右 3本ずつ）を 消し、根もとの 穴を ふたで ふさいで まぶたの 面に なじませる（双調和）。
                   管の 先の 小さい かけらも 消す（まぶたは そのまま）
   ・ひたいの こぶ（目の 上・うしろ：耳の 付け根との あいだの ふくらみと 深い みぞ）を 平らに：やわらかい しるしの 中を うす板（双調和）で
     なめらかに した 面へ 寄せる。目・まぶた・耳・たてがみの 根もと・鼻すじは さわらない・目の 上の うすい 稜は のこす・その うしろに ごく 浅い くぼみ
   ・首を 動かさずに 頭だけ 上げる（2本の 骨）：首の 上の 付け根（環椎）の まわりで 頭だけ 回す。重みは のどの あたりで なだらかに 0→1
     （のどと あごの 下の 皮が 自然に のびる）。たてがみは 重みで ついて くる
   ・鼻息：鼻の 穴の 場所と 向きを 3D で 追い（頭を 上げた あとも）、そこから ふわっと 出て ひろがり・おそく なって 消える 白い 息
     （3D の つぶ・ゆらぐ 流れ・もこもこ／すじの もよう・うしろの 光で ふちが むらさき白に 光る）
   ・馬の 体を はう むらさきと 白の 雷：G バッファ（面の 場所・向き）に 沿って 顔・首・たてがみ（毛の 流れに 沿って）を はう 細い 枝わかれの 雷
     （白い しん・むらさきの 光・小さな 火花）。1本ごとに 4〜6コマで ついて 消え、ばらばらに 出る。目が ともって から だんだん ふえて
     3.5秒の 白い 光へ。毛なみも かすかに 照らす"""
import os, sys, math
import numpy as np
import cv2
from scipy.spatial import cKDTree
import scipy.sparse as sp
import scipy.sparse.linalg as spl
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
import glb as GL                                                               # noqa: E402
from raster import sample, srgb_to_linear                                      # noqa: E402


def ss(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def nrm(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


# ================================================================ 共通：目の まわりなどの 小さい 網（位置で 溶接）
def local(p, C, R):
    V = p.pos.astype(np.float64)
    lv = np.where(np.linalg.norm(V - C, axis=1) < R)[0]
    inl = np.zeros(len(V), bool); inl[lv] = True
    I = np.asarray(p.idx)
    lt = np.where(inl[I].all(1))[0]
    q = np.round(V[lv] / 2e-5).astype(np.int64)
    _, w_of = np.unique(q, axis=0, return_inverse=True)
    w_of = w_of.ravel()
    gid = np.full(len(V), -1); gid[lv] = w_of
    nw = int(w_of.max()) + 1
    Pw = np.zeros((nw, 3)); Pw[w_of] = V[lv]
    T = gid[I[lt]]
    rep = np.zeros(nw, np.int64); rep[w_of] = lv
    return lv, w_of, gid, Pw, T, rep, lt


def face_normals_acc(P, T):
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    Nw = np.zeros_like(P)
    for j in range(3):
        np.add.at(Nw, T[:, j], fn)
    return Nw / (np.linalg.norm(Nw, axis=1, keepdims=True) + 1e-12)


def vert_albedo(p, ids):
    m = p.mat
    if m.base_tex is None:
        return np.tile(m.base_color[:3], (len(ids), 1))
    s = sample(m.base_tex.tex, m.base_tex.uv(p.uv[ids].astype(np.float32)))
    return srgb_to_linear(s[:, :3]) * m.base_color[:3]


def hair_of(alb):
    """たてがみ（あざやかな むらさき：shiden_glb.classify と 同じ きまり）"""
    hsv = cv2.cvtColor(np.clip(alb, 0, 1).astype(np.float32)[None], cv2.COLOR_RGB2HSV)[0]
    h, s_, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    return (h > 250) & (h < 320) & (s_ > .55) & (v > .25)


# ================================================================ まつ毛を 消す
def lashless(p, eyes):
    V = p.pos.astype(np.float64); Nv = p.nrm.astype(np.float64); I = np.asarray(p.idx)
    nV = len(V)
    keep = np.ones(len(I), bool)
    pos = p.pos.copy(); nrm_ = p.nrm.copy()
    extra, fans, log = [], [], []
    for E in eyes:
        lv, w_of, gid, Pw, T, rep, lt = local(p, E, 0.16)
        nw = len(Pw)
        Nw = np.zeros((nw, 3)); np.add.at(Nw, w_of, Nv[lv]); Nw /= np.linalg.norm(Nw, axis=1, keepdims=True) + 1e-12
        # うすい 点：すぐ うしろ（法線の 反対がわ 0.009 いない）に 反対向きの 面が ある（まつ毛の 管の 太さ 約 0.0045）
        kd = cKDTree(Pw)
        thin = np.zeros(nw, bool)
        for a, nb in enumerate(kd.query_ball_point(Pw, 0.009)):
            nb = np.asarray(nb)
            dv = Pw[nb] - Pw[a]
            dl = np.linalg.norm(dv, axis=1) + 1e-12
            if (((Nw[nb] @ Nw[a]) < -0.5) & ((dv @ Nw[a]) < -0.6 * dl) & (dl > 1e-5)).any():
                thin[a] = True
        rm = thin[T].sum(1) >= 2
        # 管の 先の 小さい かけら（消す 三角形に くっついた 120 より 小さい まとまり）
        par = np.arange(nw)

        def f(x):
            r = x
            while par[r] != r:
                r = par[r]
            while par[x] != r:
                par[x], x = r, par[x]
            return r
        for a, b, c in T[~rm]:
            ra, rb, rc = f(a), f(b), f(c)
            par[rb] = ra; par[f(rc)] = ra
        lab = np.array([f(x) for x in range(nw)])
        tl = lab[T[:, 0]]
        rmv = np.zeros(nw, bool); rmv[T[rm].ravel()] = True
        for u in np.unique(tl[~rm]):
            m = (tl == u) & ~rm
            if m.sum() < 120 and rmv[T[m].ravel()].any():
                rm |= m
        # 根もとの 輪（のこす 三角形の 辺の 向きで）
        kept = np.where(~rm)[0]
        rem_e = set()
        for w in T[rm]:
            for a, b in ((w[0], w[1]), (w[1], w[2]), (w[2], w[0])):
                rem_e.add((min(a, b), max(a, b)))
        bedge = []
        for k in kept:
            w = T[k]; o = I[lt[k]]
            for j in range(3):
                a, b = w[j], w[(j + 1) % 3]
                if (min(a, b), max(a, b)) in rem_e:
                    bedge.append((a, b, o[j], o[(j + 1) % 3]))
        bedge = np.array(bedge)
        par2 = {}

        def g(x):
            par2.setdefault(x, x)
            while par2[x] != x:
                par2[x] = par2[par2[x]]; x = par2[x]
            return x
        for a, b, _, _ in bedge:
            par2[g(b)] = g(a)
        rl = np.array([g(a) for a in bedge[:, 0]])
        KT = [tuple(T[k]) for k in kept]
        kept_v = set(np.unique(T[kept].ravel()).tolist())
        rings = []
        for u in np.unique(rl):
            be = bedge[rl == u]
            ring = np.unique(be[:, :2].ravel())
            c = Pw[ring].mean(0)
            cid = nw + 1000000 + len(rings)
            uvr = p.uv[np.r_[be[:, 2], be[:, 3]]]
            uvc = uvr.mean(0) if np.ptp(uvr, 0).max() < 0.05 else p.uv[be[0, 2]]
            fan = [(b, a, cid) for a, b, _, _ in be]
            dk = np.linalg.norm(Pw - c, axis=1)
            Uset = set(np.where(dk < 0.0075)[0].tolist()) & kept_v
            rings.append([c, cid, uvc, fan, be, Uset])
        # 根もとの 台と ふたを 双調和で まぶたの 面に なじませる
        for rg in rings:
            c, cid, uvc, fan, be, Uset = rg
            adj = {}
            for a, b, cc in KT + fan:
                for x, y in ((a, b), (b, cc), (cc, a)):
                    adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
            U = sorted(Uset) + [cid]
            n1 = set()
            for x in U:
                n1 |= adj[x]
            K = sorted(set(U) | n1)
            n2 = set()
            for x in K:
                n2 |= adj[x]
            allv = sorted(set(K) | n2)
            ix = {v: i for i, v in enumerate(allv)}
            Xp = np.array([c if v == cid else Pw[v] for v in allv])
            Lm = np.zeros((len(K), len(allv)))
            for r, v in enumerate(K):
                Lm[r, ix[v]] = len(adj[v])
                for y in adj[v]:
                    Lm[r, ix[y]] -= 1
            ui = [ix[v] for v in U]
            us = set(ui)
            bi = [i for i in range(len(allv)) if i not in us]
            sol = np.linalg.lstsq(Lm[:, ui], -Lm[:, bi] @ Xp[bi], rcond=None)[0]
            for v, x in zip(U, sol):
                if v == cid:
                    rg[0] = x
                else:
                    Pw[v] = x
        allU = set()
        for rg in rings:
            allU |= rg[5]
        cpos = {rg[1]: rg[0] for rg in rings}
        tris = KT + [t_ for rg in rings for t_ in rg[3]]
        P_of = lambda v: cpos[v] if v in cpos else Pw[v]
        touch = allU | set(cpos)
        nacc = {}
        for a, b, cc in tris:
            if a in touch or b in touch or cc in touch:
                fn = np.cross(P_of(b) - P_of(a), P_of(cc) - P_of(a))
                for x in (a, b, cc):
                    nacc[x] = nacc.get(x, 0) + fn
        for orig in lv:
            w = gid[orig]
            if w in allU:
                pos[orig] = Pw[w]
            if w in nacc:
                nrm_[orig] = nacc[w] / (np.linalg.norm(nacc[w]) + 1e-12)
        keep[lt[rm]] = False
        for rg in rings:
            c_new, cid, uvc, fan, be, Uset = rg
            ni = nV + len(extra)
            extra.append((c_new, nacc[cid] / (np.linalg.norm(nacc[cid]) + 1e-12), uvc))
            o_of = {}
            for a, b, oa, ob in be:
                o_of[a] = oa; o_of[b] = ob
            for b, a, _ in fan:
                fans.append((o_of[b], o_of[a], ni))
        log.append((int(rm.sum()), len(rings)))
    n = len(extra)
    rep0 = lambda a: None if a is None else np.concatenate([a, np.repeat(a[:1], n, 0)])
    q = GL.Prim(np.concatenate([pos, np.array([e[0] for e in extra], pos.dtype)]),
                np.concatenate([nrm_, np.array([e[1] for e in extra], nrm_.dtype)]),
                np.concatenate([p.uv, np.array([e[2] for e in extra], p.uv.dtype)]),
                np.concatenate([I[keep], np.array(fans, I.dtype)]), p.mat, p.name, rep0(p.uv1), rep0(p.tangent), rep0(p.color))
    return q, log


# ================================================================ ひたいの こぶを 平らに
BROW = dict(C=np.array([-0.125, 0.615, 0.435]), R=0.15, fossa=(np.array([-0.165, 0.60, 0.395]), 0.003, 0.035))


def lap(T, n):
    r = np.r_[T[:, 0], T[:, 1], T[:, 2], T[:, 1], T[:, 2], T[:, 0]]
    c = np.r_[T[:, 1], T[:, 2], T[:, 0], T[:, 0], T[:, 1], T[:, 2]]
    A = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr()
    A.data[:] = 1.0
    return (sp.diags(np.asarray(A.sum(1)).ravel()) - A).tocsr()


def fair(Pw, T, w):
    """w>0 の 点を うす板（双調和）で なめらかに（w=0 は 固定）"""
    L = lap(T, len(Pw))
    U = np.where(w > 1e-4)[0]; Fx = np.where(w <= 1e-4)[0]
    rows = np.unique(L[:, U].nonzero()[0])
    LK = L[rows]
    LU, LF = LK[:, U], LK[:, Fx]
    solve = spl.factorized((LU.T @ LU).tocsc())
    rhs = -(LU.T @ (LF @ Pw[Fx]))
    X = Pw.copy()
    for k in range(3):
        X[U, k] = solve(rhs[:, k])
    return X


def brow_mask(p, Pw, rep, Ck, Rk, E, side):
    w = 1 - ss(0.5 * Rk, Rk, np.linalg.norm(Pw - Ck, axis=1))                 # こぶの まん中から なだらかに
    w = w * ss(0.065, 0.14, np.linalg.norm(Pw - E, axis=1))                   # 目・まぶた（目の 上の うすい 稜は 半分ほど のこす）
    hair = hair_of(vert_albedo(p, rep))
    if hair.any():
        w = w * ss(0.012, 0.04, cKDTree(Pw[hair]).query(Pw)[0])                # たてがみ（前髪）と その 根もと
    ear = (~hair) & (Pw[:, 1] > 0.78) & (Pw[:, 0] * side > 0.09)
    if ear.any():
        w = w * ss(0.03, 0.07, cKDTree(Pw[ear]).query(Pw)[0])                  # 耳と 耳の 付け根
    w = w * (1 - ss(0.70, 0.76, Pw[:, 1]))
    w = w * ss(0.43, 0.5, Pw[:, 1])                                            # 目より 下（鼻すじ・ほほ）
    w = w * ss(0.025, 0.06, np.abs(Pw[:, 0]))                                  # まん中の 線（ひたいから 鼻すじへの 前の 線）
    return w


def brow_flat(p, eyes):
    pos = p.pos.copy(); nrm_ = p.nrm.astype(np.float64).copy()
    log = []
    for E, side in zip(eyes, (-1, 1)):
        mir = np.array([side * -1.0, 1, 1]) if side > 0 else np.ones(3)
        Ck = BROW['C'] * mir
        lv, w_of, gid, Pw, T, rep, lt = local(p, Ck, BROW['R'] + 0.09)
        w = brow_mask(p, Pw, rep, Ck, BROW['R'], E, side)
        N0 = face_normals_acc(Pw, T)
        Pn = Pw + w[:, None] * (fair(Pw, T, w) - Pw)
        Cf, dep, rf = BROW['fossa']
        Nf = face_normals_acc(Pn, T)
        gk = np.exp(-(np.linalg.norm(Pw - Cf * mir, axis=1) / rf) ** 2) * w
        Pn = Pn - (gk * dep)[:, None] * Nf                                     # 目の 上の 稜の うしろ（耳の 方）に ごく 浅い くぼみ
        Nn = face_normals_acc(Pn, T)
        dN = Nn - N0                                                           # 法線は「面から 作った 法線の 変わった ぶん」を もとの 法線に 足す（つぎめを 出さない）
        ch = np.linalg.norm(Pn - Pw, axis=1) > 1e-7
        sel = np.linalg.norm(dN, axis=1) > 1e-6
        for o, wv in zip(lv, w_of):
            if ch[wv]:
                pos[o] = Pn[wv]
            if sel[wv]:
                n_ = nrm_[o] + dN[wv]
                nrm_[o] = n_ / (np.linalg.norm(n_) + 1e-12)
        h = ((Pn - Pw) * N0).sum(1)
        log.append((int((w > .05).sum()), float(h.min()), float(h.max())))
    return GL.Prim(pos, nrm_.astype(p.nrm.dtype), p.uv, p.idx, p.mat, p.name, p.uv1, p.tangent, p.color), log


# ================================================================ 首を 動かさずに 頭だけ 上げる（2本の 骨）
PIV = np.array([0.0, 0.58, 0.16])                                           # 首の 上の 付け根（環椎：耳の あいだ（頭の てっぺん）の 少し 下・うしろ）
THR = np.array([0.12, 0.15])                                                # のど（あごの うしろの 下と 首の 前の つなぎ目）（y, z）
POLL = np.array([0.80, 0.22])                                               # 頭の てっぺんの うしろ（たてがみの はじまり）
B0 = np.array([0.02, 0.10])                                                 # のどの 下（あごの 下の 線の はじまり：あごの 下の 皮は ぜんぶ 頭がわに）
JAW = np.array([-0.30, 0.62])                                               # あご先の 下


def head_w(P):
    """頭の 重み：頭頂〜のどの 線より 前 かつ のどの 下〜あご先の 下の 線より 上 → 1（首 → 0）。のどの あたりで なだらかに"""
    yz = np.asarray(P, float)[..., 1:3]
    a = nrm(POLL - THR); na = np.array([-a[1], a[0]])                         # 前むき
    b = nrm(JAW - B0); nb = np.array([b[1], -b[0]])
    if nb @ (np.array([0.42, 0.51]) - B0) < 0:                                # 目の がわを ＋に
        nb = -nb
    dA = (yz - THR) @ na
    dB = (yz - B0) @ nb
    return (ss(-0.06, 0.06, dA) * ss(-0.06, 0.06, dB)).astype(np.float32)


HEAD_UP = [(0.0, 0.0), (0.25, 0.0), (0.75, 2.6), (1.15, 7.6), (1.42, 11.0), (1.62, 10.0), (2.1, 10.0)]   # 秒・頭を 上げる 角度（度）：カメラが 動く あいだに 上げて 少し もどって 止まる


# 第4稿（まさちゃん 14:07「首を、もっと馬の位置をリアルな馬に位置を合わせて！」）：首から 下（体）を 環椎の まわりに うしろへ 倒す
#   （首が のどの 所から うしろ下へ ななめに）。頭は 第3稿と まったく 同じ（画面の 場所・角度・上げる 動き）。
#   体の 重み body_w は 頭の 重みより ひろく（首の 上の 方で なだらかに 曲がる）
NECK_A = float(os.environ.get('SD_NECK', '36'))                             # 首を うしろへ 倒す 角度（度：のどから 下を ななめに）。SD_NECK=0 で 第3稿と 同じ


def body_w(P):
    """1＝頭（第3稿の まま）・0＝体（NECK_A だけ うしろへ）。頭頂〜のどの 線・のどの 下の 線から 首の がわへ ひろく なだらかに"""
    yz = np.asarray(P, float)[..., 1:3]
    a = nrm(POLL - THR); na = np.array([-a[1], a[0]])
    b = nrm(JAW - B0); nb = np.array([b[1], -b[0]])
    if nb @ (np.array([0.42, 0.51]) - B0) < 0:
        nb = -nb
    dA = (yz - THR) @ na
    dB = (yz - B0) @ nb
    return (ss(-0.22, 0.02, dA) * ss(-0.2, 0.02, dB)).astype(np.float32)


NECK_Y, NECK_D0 = 0.10, 0.12                                                # 首を たおし はじめる 高さ（のどの 所）・なだらかに 曲がる 長さ


def neck_shear(P, wb):
    """体（頭いがい）を のどの 高さから 下ほど うしろ（−z）へ ずらす（ななめの 首）→ (Δz, ∂z'/∂y)"""
    k = math.tan(math.radians(NECK_A)) * (1 - np.asarray(wb, np.float32))
    d = NECK_Y - np.asarray(P, np.float32)[..., 1]
    r = np.where(d <= 0, 0, np.where(d < NECK_D0, d * d / (2 * NECK_D0), d - NECK_D0 / 2)).astype(np.float32)
    dr = np.where(d <= 0, 0, np.where(d < NECK_D0, d / NECK_D0, 1.0)).astype(np.float32)
    return -k * r, k * dr


def _rot_a(P, a, vec=False):
    c, s = np.cos(a), np.sin(a)
    P = np.asarray(P, np.float32)
    out = P.copy()
    if vec:
        y, z = P[..., 1], P[..., 2]
        out[..., 1] = c * y - s * z
        out[..., 2] = s * y + c * z
    else:
        y, z = P[..., 1] - PIV[1], P[..., 2] - PIV[2]
        out[..., 1] = PIV[1] + c * y - s * z
        out[..., 2] = PIV[2] + s * y + c * z
    return out


def _def(P, phi, wh, wb, N=None, T=None):
    """もとの 場所 P → 首を たおし（ずらす）→ 頭を 上げる（環椎の まわりに 回す）。N（法線）・T（接線）も"""
    P = np.asarray(P, np.float32)
    a = (-math.radians(phi) * np.asarray(wh, np.float32)).astype(np.float32)
    dz, sy = neck_shear(P, wb)
    Q = P.copy(); Q[..., 2] = Q[..., 2] + dz
    out = [_rot_a(Q, a)]
    if N is not None:
        Nn = np.asarray(N, np.float32).copy()
        Nn[..., 1] = Nn[..., 1] - sy * Nn[..., 2]                              # ずらしの 法線（逆転置）
        Nn /= np.linalg.norm(Nn, axis=-1, keepdims=True) + 1e-9
        out.append(_rot_a(Nn, a, vec=True))
    if T is not None:
        Tt = np.asarray(T, np.float32).copy()
        Tt[..., 2] = Tt[..., 2] + sy * Tt[..., 1]
        Tt /= np.linalg.norm(Tt, axis=-1, keepdims=True) + 1e-9
        out.append(_rot_a(Tt, a, vec=True))
    return out if len(out) > 1 else out[0]


def deform_pts(P, phi):
    P = np.asarray(P, np.float32)
    return _def(P, phi, head_w(P), body_w(P))


def deform_vec(P, V, phi):
    P = np.asarray(P, np.float32)
    return _def(P, phi, head_w(P), body_w(P), N=V)[1]


def undeform_pts(Xd, phi, it=8):
    """もとの 場所へ（重みは もとの 場所で きまる ので くりかえして 合わせる）"""
    Xd = np.asarray(Xd, np.float32)
    X = Xd.copy()
    for _ in range(it):
        X = X + (Xd - deform_pts(X, phi))
    return X


def skin2(p, wh, wb, phi):
    if abs(phi) < 1e-7 and abs(NECK_A) < 1e-7:
        return p
    if p.tangent is not None:
        pos, nn, t3 = _def(p.pos, phi, wh, wb, N=p.nrm, T=p.tangent[:, :3])
        tg = p.tangent.copy(); tg[:, :3] = t3
    else:
        pos, nn = _def(p.pos, phi, wh, wb, N=p.nrm)
        tg = None
    return GL.Prim(pos, nn, p.uv, p.idx, p.mat, p.name, p.uv1, tg, p.color)


def head_phi(t):
    from scipy.interpolate import PchipInterpolator
    k = np.array(HEAD_UP)
    return float(PchipInterpolator(k[:, 0], k[:, 1])(np.clip(t, k[0, 0], k[-1, 0])))


def rot_pts(P, w, phi):
    """頭の 重み w で x 軸まわりに 回す（φ＞0 で 鼻が 上がる）"""
    a = -math.radians(phi) * np.asarray(w, np.float32)
    c, s = np.cos(a), np.sin(a)
    P = np.asarray(P, np.float32)
    y, z = P[..., 1] - PIV[1], P[..., 2] - PIV[2]
    out = P.copy()
    out[..., 1] = PIV[1] + c * y - s * z
    out[..., 2] = PIV[2] + s * y + c * z
    return out


def rot_vec(Vv, w, phi):
    a = -math.radians(phi) * np.asarray(w, np.float32)
    c, s = np.cos(a), np.sin(a)
    out = np.asarray(Vv, np.float32).copy()
    y, z = out[..., 1].copy(), out[..., 2].copy()
    out[..., 1] = c * y - s * z
    out[..., 2] = s * y + c * z
    return out


def skin(p, w, phi):
    if abs(phi) < 1e-6:
        return p
    pos = rot_pts(p.pos, w, phi)
    nn = rot_vec(p.nrm, w, phi)
    tg = None
    if p.tangent is not None:
        tg = p.tangent.copy()
        tg[:, :3] = rot_vec(p.tangent[:, :3], w, phi)
    return GL.Prim(pos, nn, p.uv, p.idx, p.mat, p.name, p.uv1, tg, p.color)


# ================================================================ 鼻息（3D の つぶ）
NOSE_C = np.array([-0.064, 0.025, 0.703])                                   # 左の 鼻の 穴の まん中（前から 見て はかった：穴の ふちの 輪の まん中）
NOSE_N = nrm(np.array([-0.53, -0.15, 0.83]))                                # 穴の ふちの 面の 向き（前・外・少し 下）
NOSE_D = nrm(np.array([-0.2, -0.78, 0.6]))                                 # 息の 出る 向き＝鼻の 穴の 軸（顔の すじに 沿って 下前・少し 外）
# 息は 音（sfx_sd の「フォォ…ブルルッ」：shiden.py FILM の PUFFS＝0.62・1.22 秒）に 合わせる（音は 変えない）
BREATHS = [dict(t0=0.58, dur=0.24, n=120, sp=0.75, r1=0.06, life=(1.0, 1.6), k=1.05),    # 1回目：強い 鼻息（フンッ…ブルルッ）
           dict(t0=1.18, dur=0.3, n=110, sp=0.55, r1=0.05, life=(0.95, 1.5), k=0.95)]     # 2回目：ふつうの 息


def noise_tex(n=512, seed=0):
    rng = np.random.default_rng(seed)
    acc = np.zeros((n, n), np.float32); amp, tot = 1.0, 0.0
    for o in range(6):
        k = 4 * 2 ** o
        g = rng.random((k, k)).astype(np.float32)
        g = np.tile(g, (3, 3))
        up = cv2.resize(g, (3 * n, 3 * n), interpolation=cv2.INTER_CUBIC)[n:2 * n, n:2 * n]
        acc += up * amp; tot += amp; amp *= 0.55
    acc /= tot
    return (acc - acc.min()) / (acc.max() - acc.min())


class Breath:
    """息の つぶ：はじめの 場所と 速さは 吐いた 時の 鼻の 穴（頭を 上げた ぶんも）。空気の 中で おそく なり（抵抗）・少し 上へ（あたたかい）・
       少し うしろへ（風）・ゆらぐ（いくつかの なみの 和）・大きく ひろがり うすく なる"""

    def __init__(self, nose_at, seed=4242):
        rng = np.random.default_rng(seed)
        self.P = []
        for b in BREATHS:
            n = b['n']
            te = b['t0'] + b['dur'] * rng.random(n) ** 1.6                    # 出はじめが いちばん 多い
            c, d = nose_at(te)                                                 # 吐いた 時の 鼻の 穴（場所・向き）
            ax = np.cross(d, np.array([0, 1.0, 0])); ax = nrm(ax)
            ay = nrm(np.cross(ax, d))
            ang = rng.uniform(0, 2 * np.pi, n); rr = 0.011 * np.sqrt(rng.random(n))
            x0 = c + ax * (rr * np.cos(ang))[:, None] + ay * (rr * np.sin(ang) * .6)[:, None]
            cone = np.radians(rng.normal(0, 14, (n, 2)))
            v0 = nrm(d + ax * np.tan(cone[:, :1]) + ay * np.tan(cone[:, 1:])) * (b['sp'] * rng.uniform(.65, 1.25, n))[:, None]
            v0 *= (1.15 - 0.5 * (te - b['t0']) / b['dur'])[:, None]           # あとの つぶほど おそい
            life = rng.uniform(*b['life'], n)
            r1 = b['r1'] * rng.uniform(.55, 1.3, n)
            modes = rng.normal(0, 1, (n, 3, 3)); om = rng.uniform(2.5, 7.0, (n, 3)); ph = rng.uniform(0, 6.3, (n, 3))
            self.P.append(dict(te=te, x0=x0, v0=v0, life=life, r1=r1, modes=modes, om=om, ph=ph, k=b['k'],
                               tex=rng.integers(0, 400, (n, 2)), rot=rng.uniform(0, 6.3, n), spin=rng.normal(0, .8, n), kind=rng.random(n)))
        self.tex = noise_tex(512, seed + 1)
        self.tex2 = noise_tex(512, seed + 7)

    def state(self, t):
        out = []
        for B in self.P:
            a = t - B['te']
            ok = (a > 0) & (a < B['life'])
            if not ok.any():
                continue
            a = a[ok]
            kd = 2.7
            disp = B['v0'][ok] * ((1 - np.exp(-kd * a)) / kd)[:, None]
            disp += np.array([0, 1.0, 0]) * (0.5 * 0.07 * a * a)[:, None]       # あたたかい ので 少し 上へ
            disp += np.array([0, 0.015, -0.11]) * a[:, None]                    # うしろへ 流れる 風（たてがみと 同じ 向き）
            md = B['modes'][ok]; om = B['om'][ok]; ph = B['ph'][ok]
            tur = (np.sin(om * a[:, None] + ph) - np.sin(ph))[:, :, None] * md * (0.02 * (a ** 1.1))[:, None, None]
            disp += tur.sum(1)
            r = 0.004 + (B['r1'][ok] - 0.004) * (1 - np.exp(-a / 0.5))
            life = B['life'][ok]
            o = ss(0, 0.05, a) * (1 - ss(0.25 * life, life, a)) * (0.006 / r) ** 0.95 * B['k']
            out.append(dict(x=B['x0'][ok] + disp, r=r, o=o, tex=B['tex'][ok], rot=B['rot'][ok] + B['spin'][ok] * a, kind=B['kind'][ok], age=a / life))
        return out

    def layer(self, t, cam, project, Pg, Ag, W, H, L, to_w, rim_dir):
        """息の こさ（D）と 色（線形）。Pg：G バッファの 場所（奥の 面に かくれる つぶは 消す）"""
        D = np.zeros((H, W), np.float32)
        Rn = np.zeros((H, W), np.float32)                                      # ふちの 光（うしろからの 光に 向く がわ）
        sts = self.state(t)
        if not sts:
            return None
        fpx = H / (2 * math.tan(math.radians(cam.fov_y) / 2))
        camp = cam.eye
        dg = np.linalg.norm(Pg - camp[None, None, :], axis=-1)
        dg = np.where(Ag > .5, dg, 1e9)
        T1, T2 = self.tex, self.tex2
        for S_ in sts:
            X = to_w(S_['x'])
            px = project(cam, X)
            dep = np.linalg.norm(X - camp[None, :], axis=1)
            for j in range(len(px)):
                rs = S_['r'][j] * fpx / dep[j]
                if rs < 0.6:
                    continue
                x, y = px[j]
                ext = rs * 2.2
                x0, x1 = int(max(0, x - ext)), int(min(W, x + ext + 1))
                y0, y1 = int(max(0, y - ext)), int(min(H, y + ext + 1))
                if x1 <= x0 or y1 <= y0:
                    continue
                xi, yi = int(np.clip(x, 0, W - 1)), int(np.clip(y, 0, H - 1))
                vis = np.clip((dg[yi, xi] - dep[j]) / 0.02 + 0.5, 0, 1)        # 馬の 奥へ まわった つぶは 見えない
                if vis <= 0:
                    continue
                yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
                dx, dy = (xx - x) / rs, (yy - y) / rs
                rho2 = dx * dx + dy * dy
                ca, sa = math.cos(S_['rot'][j]), math.sin(S_['rot'][j])
                sc = 70.0 + 40.0 * S_['kind'][j]
                u = (dx * ca - dy * sa) * sc + S_['tex'][j][0]
                v = (dx * sa + dy * ca) * sc + S_['tex'][j][1]
                n1 = cv2.remap(T1, (u % 511).astype(np.float32), (v % 511).astype(np.float32), cv2.INTER_LINEAR)
                n2 = cv2.remap(T2, ((u * 2.3) % 511).astype(np.float32), ((v * 2.3) % 511).astype(np.float32), cv2.INTER_LINEAR)
                ag = S_['age'][j]
                body = np.exp(-rho2 * 1.4)
                billow = ss(0.3, 0.75, n1) ** 1.5                               # もこもこ（こい 所と うすい 所を はっきり）
                wisp = ss(0.28, 0.58, n2 * 0.7 + n1 * 0.5 + (1 - np.sqrt(rho2)) * 0.45 - 0.18 * ag)   # ふちを ちぎれた すじに
                dens = body * (0.12 + 1.3 * billow) * wisp * S_['o'][j] * vis
                D[y0:y1, x0:x1] += dens
                lit = np.clip(dx * rim_dir[0] + dy * rim_dir[1], 0, 1) * np.exp(-rho2 * 0.9)
                Rn[y0:y1, x0:x1] += dens * lit
        if D.max() <= 0:
            return None
        D = cv2.GaussianBlur(D, (0, 0), 0.8)
        al = 1 - np.exp(-D * 0.9)
        Db = cv2.GaussianBlur(D, (0, 0), 3.0)
        gy, gx = np.gradient(Db)
        edge = np.clip(-(gx * rim_dir[0] + gy * rim_dir[1]) / (Db + 0.05) * 6.0, 0, 1)   # 光の 方を 向いた ふち（こさが 光の 方へ へる 所）
        rim = np.clip(np.clip(Rn / (D + 1e-4), 0, 1) * 0.5 + edge * 0.7, 0, 1)
        thin = np.exp(-D * 1.4)                                               # うすい 所ほど うしろの 光が すける（ふちの 光）・こい 所は 少し 暗い（自分の かげ）
        amb = 0.015 + 0.45 * L
        back = 0.8 * L
        col = (np.array([0.42, 0.36, 0.62])[None, None, :] * (amb * (0.35 + 0.4 * (1 - thin)))[..., None]
               + np.array([0.95, 0.84, 1.0])[None, None, :] * (back * (0.55 * thin * (0.4 + 0.6 * rim) + 0.1 * rim))[..., None])
        return al.astype(np.float32), col.astype(np.float32)


# ================================================================ 馬の 体を はう むらさきと 白の 雷
ARC_ENV = {4: (.6, 1.0, .62, .28), 5: (.55, 1.0, .78, .45, .2), 6: (.5, .95, 1.0, .7, .42, .18)}   # 1本の 雷の コマごとの 明るさ


class Arcs:
    """雷の 出る 予定（コマ・長さ・場所の 種類）は はじめに 決める。道すじは 生まれた コマの カメラで 見える 面から はじめて
       面の 上を 歩いて 作る（毛は 毛の 流れに 沿って・毛なみは 面に 沿って）→ 点の 番号で もつ ので 頭を 上げても 面に ついて いく"""

    def __init__(self, prim, hair, f_on, f_end, seed=5150):
        self.p = prim
        V = prim.pos.astype(np.float32)
        self.V = V
        self.N = prim.nrm.astype(np.float32)
        side = V[:, 0] < 0.04
        self.hair_ids = np.where(hair & side & (V[:, 1] > 0.15))[0]
        coat = (~hair) & side & (V[:, 1] > -0.55)
        self.coat_ids = np.where(coat)[0]
        self.kd_h = cKDTree(V[self.hair_ids])
        self.kd_c = cKDTree(V[self.coat_ids])
        self.cache = {}
        rng = np.random.default_rng(seed)
        ev = []
        for f in range(f_on, f_end):
            tt = (f - f_on) / max(1, (f_end - f_on))
            rate = 0.3 + 1.6 * tt ** 1.4                                        # 目が ともって から だんだん ふえる（3.5秒の 白い 光へ）
            for _ in range(rng.poisson(rate)):
                life = int(rng.choice((4, 5, 5, 6)))
                kind = rng.choice(('face', 'face', 'mane', 'neck'), p=None)
                ev.append(dict(f0=f, life=life, kind=str(kind), seed=int(rng.integers(1 << 30)), white=bool(rng.random() < 0.42)))
        self.ev = ev

    def path(self, e, cam_at, Wd, Hd, project, eye_w):
        """道すじ（点の 番号の 列）と 枝"""
        key = id(e)
        if key in self.cache:
            return self.cache[key]
        rng = np.random.default_rng(e['seed'])
        cam, to_w, to_wn = cam_at(e['f0'])                                    # 生まれた コマの カメラ・モデル → 世界
        camp = cam.eye
        hs = e['kind'] == 'mane'
        ids = self.hair_ids if hs else self.coat_ids
        kd = self.kd_h if hs else self.kd_c
        Vw = None
        best = None
        for _try in range(60):                                                # 見える 所から はじめる
            k = ids[rng.integers(len(ids))]
            pw = to_w(self.V[k][None])[0]
            nw_ = nrm(to_wn(self.V[k][None], self.N[k][None])[0])
            if nw_ @ nrm(camp - pw) < 0.15:
                continue
            q = project(cam, pw)[0]
            if not (0.04 * Wd < q[0] < 0.96 * Wd and 0.03 * Hd < q[1] < 0.9 * Hd):
                continue
            de = np.linalg.norm(q - eye_w(e['f0']))
            if e['kind'] == 'face' and de > 0.42 * Hd:
                continue
            if e['kind'] == 'neck' and q[1] < eye_w(e['f0'])[1] + 0.12 * Hd:
                continue
            if de < 0.03 * Hd:
                continue                                                      # 目の 火の 上は さける
            best = k
            break
        if best is None:
            self.cache[key] = None
            return None
        L = rng.uniform(0.10, 0.2) if hs else rng.uniform(0.07, 0.16)
        step = 0.008 if hs else 0.01
        pts = [best]
        P = self.V[best].astype(np.float64)
        nrm0 = self.N[best].astype(np.float64)
        if hs:                                                                # 毛の 流れ：まわりの 毛の 点の いちばん のびる 向き
            nb = kd.query_ball_point(P, 0.012)
            Q = self.V[ids[nb]] - P
            dirv = np.linalg.svd(Q, full_matrices=False)[2][0] if len(nb) > 3 else nrm(rng.normal(0, 1, 3))
        else:
            dirv = nrm(np.cross(nrm0, rng.normal(0, 1, 3)))
        if rng.random() < .5:
            dirv = -dirv
        acc = 0.0
        while acc < L:
            if not hs:
                dirv = nrm(dirv + np.cross(nrm0, dirv) * rng.normal(0, 0.45))     # 面の 上で 向きを ゆらす
            tgt = P + dirv * step
            dd, ii = kd.query(tgt)
            k = ids[ii]
            Pn = self.V[k].astype(np.float64)
            if np.linalg.norm(Pn - P) < step * 0.3:
                tgt = P + dirv * step * 2
                dd, ii = kd.query(tgt); k = ids[ii]; Pn = self.V[k].astype(np.float64)
                if np.linalg.norm(Pn - P) < step * 0.3:
                    break
            nd = nrm(Pn - P)
            if nd @ dirv < 0.2:
                break
            dirv = nrm(dirv * 0.55 + nd * 0.45)
            acc += np.linalg.norm(Pn - P)
            P = Pn; nrm0 = self.N[k].astype(np.float64)
            pts.append(k)
        if len(pts) < 4:
            self.cache[key] = None
            return None
        br = []
        for _ in range(int(rng.integers(1, 4))):                              # 枝（2〜6点）
            j = int(rng.integers(1, len(pts) - 1))
            nb_ = int(rng.integers(2, 6))
            Pb = self.V[pts[j]].astype(np.float64)
            db = nrm(np.cross(self.N[pts[j]], rng.normal(0, 1, 3)))
            bp = [pts[j]]
            for _s in range(nb_):
                dd, ii = kd.query(Pb + db * step)
                k = ids[ii]
                if k == bp[-1]:
                    break
                bp.append(k); Pb = self.V[k].astype(np.float64)
                db = nrm(db + rng.normal(0, .35, 3))
            if len(bp) > 2:
                br.append(bp)
        self.cache[key] = (pts, br)
        return pts, br

    def frame(self, f, cam, to_w, cam_at, project, eye_w, Pg, Ag, Ng, W, H, hs, light_k):
        """この コマの 雷：しん（白い 雷・むらさきの 雷）・毛なみを 照らす 光（線形）・火花"""
        coreW = np.zeros((H, W), np.float32); coreP = np.zeros((H, W), np.float32); spk = np.zeros((H, W), np.float32)
        lit = np.zeros((H, W, 3), np.float32)
        camp = cam.eye
        dg = np.where(Ag > .5, np.linalg.norm(Pg - camp[None, None, :], axis=-1), 1e9)
        fpx = H / (2 * math.tan(math.radians(cam.fov_y) / 2))
        n_on = 0
        for e in self.ev:
            age = f - e['f0']
            if not (0 <= age < e['life']):
                continue
            pb = self.path(e, cam_at, W, H, project, eye_w)
            if pb is None:
                continue
            pts, br = pb
            g = ARC_ENV[e['life']][age]
            rj = np.random.default_rng(e['seed'] * 7 + f)
            g *= rj.uniform(0.78, 1.0)                                          # ビリビリ
            n_on += 1
            for kk, chain in enumerate([pts] + br):
                Pw_ = to_w(self.V[chain])
                q = project(cam, Pw_)
                dep = np.linalg.norm(Pw_ - camp[None, :], axis=1)
                qi = np.clip(q.astype(int), [0, 0], [W - 1, H - 1])
                vis = dep < dg[qi[:, 1], qi[:, 0]] + 0.012 + 0.006 * dep        # 面に かくれた 所は 描かない
                # ギザギザ：大きな 折れ（雷 1本で きまる）→ 細かい ギザギザ（コマごとに かわる：ビリビリ）
                key_i = np.unique(np.r_[np.arange(0, len(q), 3), len(q) - 1])
                kq = q[key_i]; kv = vis[key_i]
                rm_ = np.random.default_rng(e['seed'] * 13 + kk)
                seg, sv = kq, kv
                for lev, amp in enumerate((0.3, 0.17, 0.09)):
                    rr_ = rm_ if lev == 0 else rj
                    ns, nv = [seg[0]], [sv[0]]
                    for i in range(len(seg) - 1):
                        a_, b_ = seg[i], seg[i + 1]
                        dv = b_ - a_
                        ln = np.linalg.norm(dv) + 1e-6
                        pn = np.array([-dv[1], dv[0]]) / ln
                        ns += [(a_ + b_) / 2 + pn * rr_.normal(0, amp) * ln, b_]
                        nv += [sv[i] and sv[i + 1], sv[i + 1]]
                    seg, sv = np.array(ns), np.array(nv)
                wd = (1.0 if kk == 0 else 0.62) * (0.7 + 0.5 * hs)
                gk = g * (1.0 if kk == 0 else 0.72)
                buf = coreW if e['white'] else coreP
                nseg = len(seg) - 1
                for i in range(nseg):
                    if not (sv[i] and sv[i + 1]):
                        continue
                    taper = 1 - 0.6 * (i / max(1, nseg))
                    a_, b_ = seg[i], seg[i + 1]
                    cv2.line(buf, (int(a_[0] * 4), int(a_[1] * 4)), (int(b_[0] * 4), int(b_[1] * 4)), float(gk * taper),
                             max(1, int(round(wd * taper * 4))), cv2.LINE_AA, shift=2)
                # 小さな 枝（画面の 上で 細かく 分かれる・コマごとに）
                for _ in range(int(rj.integers(1, 4)) if kk == 0 else int(rj.integers(0, 2))):
                    i0 = int(rj.integers(1, max(2, nseg - 1)))
                    if not sv[i0]:
                        continue
                    a_ = seg[i0]
                    dv = seg[min(i0 + 1, nseg)] - seg[i0 - 1]
                    ang = math.atan2(dv[1], dv[0]) + rj.choice((-1, 1)) * rj.uniform(0.45, 0.95)
                    Lb = rj.uniform(10, 30) * (0.6 + 0.6 * hs)
                    pb_ = [a_]
                    for k_ in range(4):
                        ang += rj.normal(0, 0.45)
                        pb_.append(pb_[-1] + np.array([math.cos(ang), math.sin(ang)]) * Lb / 4)
                    for k_ in range(4):
                        c0, c1 = pb_[k_], pb_[k_ + 1]
                        cv2.line(buf, (int(c0[0] * 4), int(c0[1] * 4)), (int(c1[0] * 4), int(c1[1] * 4)), float(gk * 0.55 * (1 - k_ / 4)),
                                 max(1, int(round(wd * 0.5 * 4))), cv2.LINE_AA, shift=2)
                if kk == 0 and sv.any():
                    tip = seg[-1] if sv[-1] else seg[0]
                    for _ in range(int(rj.integers(1, 4))):                   # 小さな 火花（先から とぶ）
                        d_ = rj.normal(0, 1, 2); d_ /= np.linalg.norm(d_) + 1e-6
                        r_ = rj.uniform(3, 14) * hs * (age + 1)
                        sp_ = tip + d_ * r_
                        cv2.circle(spk, (int(sp_[0] * 4), int(sp_[1] * 4)), max(1, int(4 * (0.7 + 0.5 * hs))), float(g * rj.uniform(.4, 1.0)), -1, cv2.LINE_AA, shift=2)
                # 毛なみを 照らす（雷の 道すじの 上の 点の 光）
                if kk == 0:
                    col = np.array([0.85, 0.75, 1.0]) if e['white'] else np.array([0.65, 0.22, 1.0])
                    for j in range(0, len(Pw_), max(1, len(Pw_) // 5)):
                        if not vis[j]:
                            continue
                        c3 = Pw_[j]
                        rr = 0.07
                        rp = rr * fpx / dep[j]
                        cx, cy = q[j]
                        x0, x1 = int(max(0, cx - rp)), int(min(W, cx + rp + 1))
                        y0, y1 = int(max(0, cy - rp)), int(min(H, cy + rp + 1))
                        if x1 <= x0 or y1 <= y0:
                            continue
                        Pb_ = Pg[y0:y1, x0:x1]; Nb_ = Ng[y0:y1, x0:x1]; Ab_ = Ag[y0:y1, x0:x1]
                        dv = c3[None, None, :] - Pb_
                        dd = np.linalg.norm(dv, axis=-1) + 1e-6
                        ndl = np.clip((Nb_ * dv).sum(-1) / dd, 0, 1)
                        fall = 1 / (1 + (dd / 0.018) ** 2) * (1 - ss(0.5 * rr, rr, dd))
                        lit[y0:y1, x0:x1] += (ndl * fall * Ab_ * g * light_k)[..., None] * col
        return coreW, coreP, spk, lit, n_on


def arcs_glow(coreW, coreP, spk, s):
    """しん → 白い 芯・むらさきの 光（線形）。白い 雷：白い 芯＋うすむらさき／むらさきの 雷：うす桃白の 芯＋こい むらさき"""
    out = np.zeros(coreW.shape + (3,), np.float32)
    for core, cc, c1, c2, c3, k in ((coreW, (1.0, 0.98, 1.0), (0.9, 0.8, 1.0), (0.6, 0.45, 1.0), (0.4, 0.2, 0.9), (2.2, 2.0, 1.2, 0.7)),
                                    (coreP, (1.0, 0.82, 1.0), (0.82, 0.36, 1.0), (0.58, 0.12, 1.0), (0.42, 0.04, 0.78), (1.9, 2.3, 1.8, 1.1))):
        if core.max() <= 0:
            continue
        out += core[..., None] * np.array(cc) * k[0]
        out += cv2.GaussianBlur(core, (0, 0), 1.3 * s)[..., None] * np.array(c1) * k[1]
        out += cv2.GaussianBlur(core, (0, 0), 4.2 * s)[..., None] * np.array(c2) * k[2]
        out += cv2.GaussianBlur(core, (0, 0), 12 * s)[..., None] * np.array(c3) * k[3]
    if spk.max() > 0:
        out += spk[..., None] * np.array([1.0, 0.92, 1.0]) * 1.6 + cv2.GaussianBlur(spk, (0, 0), 2.5 * s)[..., None] * np.array([0.7, 0.35, 1.0]) * 1.2
    return out


# ================================================================ 第3稿の 雷（まさちゃん 12:24「雷もっと自然にして！」）
#   ・形：細い（しん 1〜2px）長い 雷。中点を ずらす 細かい ギザギザ・細い 枝（先へ 細く うすく）・長さに 沿って 明るさが ゆらぐ
#   ・うごき：面の 上を はう（G バッファの 向きの 変わり方＝稜・すじ（ひたい・ほお骨・あご・首の 筋）と たてがみの 毛の 流れに 沿う）・
#     体の 近い 2点の あいだを とぶ（毛と 毛・たてがみから 首：小さな テスラの 放電）・ふちを こえて 向こうへ まわる（面の 奥は かくれる）
#   ・光と 色：むらさき白の しん・やわらかく ひろがる むらさきの 光・雷の まわりの 毛なみを みじかく 照らす（ふちの 光も 拾う）
#   ・時間：さきがけ → 打つ → ちらつき・ちがう 道で 打ち直し（2〜3回）→ のこり光 → 消える。うすい 雷 たくさん＋明るい 雷 少し
#   ・数：目が ともって から ふえて 3.5秒の 白い 光へ（顔 全体が 光る ような 明るさの 波は 作らない）
ARC3_PAT = {'bright': (('L', .42), ('S', 1.0), ('D', .2), ('R', .85), ('A', .3), ('A', .12)),
            'bright2': (('L', .38), ('S', 1.0), ('R', .9), ('D', .18), ('R', .72), ('A', .26), ('A', .1)),
            'faint': (('L', .5), ('S', 1.0), ('R', .78), ('A', .3)),
            'faint2': (('S', 1.0), ('D', .28), ('R', .75), ('A', .22)),
            'faint3': (('L', .45), ('S', .9), ('A', .25)),
            'jump': (('S', 1.0), ('D', .22), ('R', .9), ('R', .68), ('A', .2))}
ARC3_TIER = dict(bright=1.0, faint=0.34, jump=0.85)


def _bil(img, x, y):
    """img（H×W[×C]）を 小数の 場所で（はしは クリップ）"""
    H_, W_ = img.shape[:2]
    x = np.clip(x, 0, W_ - 1.001); y = np.clip(y, 0, H_ - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    if img.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def arc_features(B, s):
    """G バッファから：面の 向きが 変わる 強さ K（稜・みぞ・毛の すじ）と その 線の 向き（ax, ay）・まとまり coh"""
    A, N = B['A'], B['N']
    m = (A > .5).astype(np.float32)
    mm = m[..., None]
    Nm = N * mm
    gx = np.zeros_like(N); gy = np.zeros_like(N)
    gx[:, 1:-1] = (Nm[:, 2:] - Nm[:, :-2]) * .5
    gy[1:-1] = (Nm[2:] - Nm[:-2]) * .5
    ok = m.copy()
    ok[:, 1:-1] *= m[:, 2:] * m[:, :-2]; ok[1:-1] *= m[2:] * m[:-2]             # ふち（うしろが 背景）の 段差は 数えない
    gx *= ok[..., None]; gy *= ok[..., None]
    sg = 2.2 * s
    Jxx = cv2.GaussianBlur((gx * gx).sum(-1), (0, 0), sg)
    Jxy = cv2.GaussianBlur((gx * gy).sum(-1), (0, 0), sg)
    Jyy = cv2.GaussianBlur((gy * gy).sum(-1), (0, 0), sg)
    tr = Jxx + Jyy
    disc = np.sqrt(np.maximum(tr * tr / 4 - (Jxx * Jyy - Jxy * Jxy), 0))
    l1, l2 = tr / 2 + disc, np.maximum(tr / 2 - disc, 0)
    th = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy) + np.pi / 2                     # 線の 向き（変わり方が いちばん 小さい 向き）
    K = np.sqrt(l1) * m
    coh = ((l1 - l2) / (l1 + l2 + 1e-9)) * m
    return dict(m=m, K=K, coh=coh, ax=np.cos(th).astype(np.float32), ay=np.sin(th).astype(np.float32))


ARC_CUT = int(os.environ.get('SD_ARC_CUT', '77'))                           # 第4稿：この コマ（2.57秒）から 雷を 大はばに へらす（0 で 第3稿）
ARC_CAP = 6                                                                 # その あとの 同時の 雷の 数の 上限


class Arcs3:
    def __init__(self, f_on, f_end, seed=7070):
        rng = np.random.default_rng(seed)
        ev = []
        for f in range(f_on, f_end):
            u = (f - f_on) / max(1, f_end - 1 - f_on)
            ramp = float(ss(0.0, 0.92, u)) ** 1.25
            cut = ARC_CUT and f >= ARC_CUT
            if not cut:
                spec = (('bright', ('ridge', 'ridge', 'mane', 'neck', 'rim'), 0.15 + 0.45 * ramp, ('bright', 'bright2')),
                        ('faint', ('ridge', 'ridge', 'mane', 'mane', 'neck', 'rim'), 1.4 + 4.2 * ramp, ('faint', 'faint2', 'faint3')),
                        ('jump', ('jump',), 0.1 + 0.36 * ramp, ('jump',)))
            else:                                                                 # 1/4 くらい：長く はう 雷（すじ・たてがみ）と たまに 放電だけ
                spec = (('bright', ('ridge', 'mane', 'mane', 'neck'), 0.16 + 0.3 * ramp, ('bright', 'bright2')),
                        ('faint', ('mane', 'mane', 'ridge'), 0.22 + 0.4 * ramp, ('faint', 'faint2')),
                        ('jump', ('jump',), 0.04 + 0.08 * ramp, ('jump',)))
            for tier, kinds, rate, pats in spec:
                for _ in range(rng.poisson(rate)):
                    ev.append(dict(f0=f, tier=tier, kind=str(rng.choice(kinds)), pat=str(rng.choice(pats)), seed=int(rng.integers(1 << 30)), late=bool(cut)))
        self.ev = ev
        self.paths = {}
        self.feat = {}

    # ---------------------------------------------------------------- 生まれた コマで 道すじを 作る（画面で なぞって 3D に もち上げる）
    def _features(self, f, B, s):
        if f not in self.feat:
            if len(self.feat) > 3:
                self.feat.pop(next(iter(self.feat)))
            F = arc_features(B, s)
            H_, W_ = F['m'].shape
            ex, ey = B['M']['eye']
            yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
            near_eye = np.hypot(xx - ex, yy - ey) < 0.055 * H_ * (0.5 + 0.7 * B['hs'])
            edge = (xx > 0.03 * W_) & (xx < 0.97 * W_) & (yy > 0.02 * H_) & (yy < 0.9 * H_)
            base = F['m'] * (~near_eye) * edge
            Kq = F['K'][F['m'] > .5]
            k50, k97 = (np.percentile(Kq, 50), np.percentile(Kq, 97)) if len(Kq) else (0, 1)
            Kn = ss(k50, k97, F['K'])
            mane = (B['mane'] > .5)
            dist_in = cv2.distanceTransform((F['m'] > .5).astype(np.uint8), cv2.DIST_L2, 5)
            gyd, gxd = np.gradient(cv2.GaussianBlur(dist_in, (0, 0), 3))
            F.update(ex_x=-gxd, ex_y=-gyd)                                     # ふちへ 向かう 向き
            rim_band = ((dist_in > 6 * s) & (dist_in < 22 * s)).astype(np.float32)
            wts = dict(ridge=base * (~mane) * (0.04 + Kn * F['coh']),
                       rim=base * rim_band * (0.3 + Kn),
                       mane=base * mane * (0.15 + Kn),
                       neck=base * (~mane) * (yy > ey + 0.1 * H_) * (0.12 + Kn * F['coh']),
                       jump=base * (mane * 1.0 + (~mane) * 0.35 * Kn))
            cum = {}
            for k_, w_ in wts.items():
                sm = cv2.resize(w_.astype(np.float32), (W_ // 4, H_ // 4), interpolation=cv2.INTER_AREA).ravel()
                c_ = np.cumsum(sm)
                cum[k_] = c_ if c_[-1] > 0 else None
            F.update(cum=cum, Kn=Kn, mane=mane, q=(W_ // 4, H_ // 4))
            self.feat[f] = F
        return self.feat[f]

    def _pick(self, F, kind, rng):
        c_ = F['cum'][kind]
        if c_ is None:
            return None
        for _ in range(20):
            j = int(np.searchsorted(c_, rng.random() * c_[-1]))
            qw, qh = F['q']
            x = (j % qw) * 4 + rng.uniform(0, 4); y = (j // qw) * 4 + rng.uniform(0, 4)
            if F['m'][int(y), int(x)] > .5:
                return np.array([x, y])
        return None

    def _trace(self, F, p0, rng, L, step, rim=False):
        H_, W_ = F['m'].shape
        d = np.array([_bil(F['ax'], *p0), _bil(F['ay'], *p0)])
        d = d / (np.linalg.norm(d) + 1e-9) * (1 if rng.random() < .5 else -1)
        if rim:                                                               # ふちへ 向かって（少し ななめに）
            o = np.array([_bil(F['ex_x'], *p0), _bil(F['ex_y'], *p0)])
            o /= np.linalg.norm(o) + 1e-9
            d = o * 0.8 + d * (0.6 if d @ o > 0 else -0.6)
            d /= np.linalg.norm(d) + 1e-9
        pts = [p0.copy()]
        tot, wrap, turn = 0.0, False, 0.0
        while tot < L:
            q = pts[-1] + d * step
            if len(pts) > 14 and np.min(np.linalg.norm(np.array(pts[:-10]) - q, axis=1)) < 3.0 * step:
                break                                                         # 自分に もどって くる（輪に なる）雷は 作らない
            if not (1 <= q[0] < W_ - 2 and 1 <= q[1] < H_ - 2) or F['m'][int(q[1]), int(q[0])] < .5:
                wrap = True
                break
            a = np.array([_bil(F['ax'], *q), _bil(F['ay'], *q)])
            a /= np.linalg.norm(a) + 1e-9
            if a @ d < 0:
                a = -a
            k = (0.12 if rim else 0.35) + (0.2 if rim else 0.5) * float(_bil(F['coh'], *q))
            d = d * (1 - k) + a * k
            ang = rng.normal(0, 0.1)
            c, s_ = math.cos(ang), math.sin(ang)
            d = np.array([c * d[0] - s_ * d[1], s_ * d[0] + c * d[1]])
            d /= np.linalg.norm(d) + 1e-9
            if len(pts) > 1:
                d_prev = pts[-1] - pts[-2]
                d_prev /= np.linalg.norm(d_prev) + 1e-9
                turn += math.atan2(d_prev[0] * d[1] - d_prev[1] * d[0], float(d_prev @ d))   # 向きの 変わった ぶん（＋左・−右：ゆれは 打ち消しあう）
                if abs(turn) > 3.3:                                            # ぐるっと まわる（輪に なる）たら おわり
                    pts.append(q)
                    break
            pts.append(q); tot += step
        return np.array(pts), wrap

    def _lift(self, B, pts, inv_skin):
        P = B['P'][pts[:, 1].astype(int), pts[:, 0].astype(int)]
        Mi = np.linalg.inv(B['Mm'])
        Xd = P @ Mi[:3, :3].T + Mi[:3, 3]
        return inv_skin(Xd, B['phi'])

    def path(self, k, e, buf_at, s, inv_skin):
        if k in self.paths:
            return self.paths[k]
        B = buf_at(e['f0'])
        F = self._features(e['f0'], B, s)
        rng = np.random.default_rng(e['seed'])
        hs = B['hs']
        sc = s * (0.75 + 0.45 * hs)
        res = None
        if e['kind'] == 'jump':
            src = self._pick(F, 'jump', rng)
            if src is not None:
                Ps = B['P'][int(src[1]), int(src[0])]
                best = None
                for _ in range(40):
                    r_ = rng.uniform(22, 105) * sc; a_ = rng.uniform(0, 2 * np.pi)
                    q = src + r_ * np.array([math.cos(a_), math.sin(a_)])
                    H_, W_ = F['m'].shape
                    if not (2 <= q[0] < W_ - 2 and 2 <= q[1] < H_ - 2) or F['m'][int(q[1]), int(q[0])] < .5:
                        continue
                    Pq = B['P'][int(q[1]), int(q[0])]
                    d3 = np.linalg.norm(Pq - Ps)
                    if not (0.012 < d3 < 0.09):
                        continue
                    Ns, Nq = _bil(B['N'], *src), _bil(B['N'], *q)
                    other = (F['mane'][int(src[1]), int(src[0])] != F['mane'][int(q[1]), int(q[0])]) or (Ns @ Nq < 0.75)
                    sc_ = (2.0 if other else 1.0) * rng.random()
                    if best is None or sc_ > best[0]:
                        best = (sc_, q)
                if best is not None:
                    ends = np.array([src, best[1]])
                    res = dict(jump=True, X=self._lift(B, ends, inv_skin))
        else:
            p0 = self._pick(F, e['kind'], rng)
            if p0 is not None:
                bright = e['tier'] == 'bright'
                L = rng.uniform(200, 480) * sc if bright else (rng.uniform(180, 360) * sc if e.get('late') else rng.uniform(90, 260) * sc)
                pts, wrap = self._trace(F, p0, rng, L, 5.0 * sc if e['kind'] == 'mane' else 6.5 * sc, rim=e['kind'] == 'rim')
                if len(pts) >= 4:
                    res = dict(jump=False, X=self._lift(B, pts, inv_skin), wrap=wrap)
        self.paths[k] = res
        return res

    # ---------------------------------------------------------------- この コマ
    def frame(self, f, B, buf_at, project, to_w, inv_skin, s, gain_light):
        H_, W_ = B['A'].shape
        cam = B['cam']; camp = cam.eye
        C2 = np.zeros((2 * H_, 2 * W_), np.float32)                               # しん（2倍の 細かさで 描いて へらす：1〜2px の 線）
        Hot2 = np.zeros((2 * H_, 2 * W_), np.float32)                             # 白熱（明るい 雷の まん中）
        AG = np.zeros((H_, W_), np.float32)                                       # のこり光
        lit = np.zeros((H_, W_, 3), np.float32)
        dg = np.where(B['A'] > .5, B['dep'], 1e9)
        fpx = H_ / (2 * math.tan(math.radians(cam.fov_y) / 2))
        P, N = B['P'], B['N']
        hs = B['hs']
        sc = s * (0.55 + 0.65 * hs)
        n_on = 0
        cand = []
        for k, e in enumerate(self.ev):
            age = f - e['f0']
            pat = ARC3_PAT[e['pat']]
            if not (0 <= age < len(pat)):
                continue
            if ARC_CUT and f >= ARC_CUT and e['tier'] == 'faint' and not e.get('late') and e['kind'] != 'mane':
                continue                                                      # 頬・あご・顔の 短い 雷は まず 消す
            pa = self.path(k, e, buf_at, s, inv_skin)
            if pa is None:
                continue
            cand.append((k, e, pa))
        if ARC_CUT and f >= ARC_CUT:                                          # 長い 雷から（明るい・放電・うすい の 順）・短い ものは 出さない・上限 ARC_CAP
            def plen(pa):
                q_ = project(cam, to_w(pa['X']))
                return float(np.linalg.norm(np.diff(q_, axis=0), axis=1).sum())
            scored = []
            for k, e, pa in cand:
                L_ = plen(pa)
                if not pa['jump'] and L_ < 110 * s:
                    continue
                scored.append(((0 if e['tier'] == 'bright' else 1 if e['tier'] == 'jump' else 2), -L_, k, e, pa))
            scored.sort(key=lambda x: (x[0], x[1]))
            cand = [(k, e, pa) for _, _, k, e, pa in scored]
        drawn = 0
        for k, e, pa in cand:
            if ARC_CUT and f >= ARC_CUT and drawn >= ARC_CAP:
                break
            age = f - e['f0']
            pat = ARC3_PAT[e['pat']]
            state, g = pat[age]
            g *= ARC3_TIER[e['tier']]
            strike = sum(1 for st_, _ in pat[:age + 1] if st_ in ('S', 'R', 'L'))
            if state in ('D', 'A'):
                strike = max(1, strike)
            rs = np.random.default_rng(e['seed'] * 31 + strike)
            rf = np.random.default_rng(e['seed'] * 77 + f)                       # コマごとの ちらつき
            g *= rf.uniform(0.82, 1.0)
            # 世界 → 画面
            if pa['jump']:
                Xw = to_w(pa['X'])
                nseg = max(6, int(np.linalg.norm(project(cam, Xw[1:])[0] - project(cam, Xw[:1])[0]) / (7 * sc)))
                u = np.linspace(0, 1, nseg + 1)[:, None]
                Xs = Xw[0] * (1 - u) + Xw[1] * u
                bow = np.sin(np.pi * u) * rs.normal(0, 0.006)                     # 空中で 少し ふくらむ
                Xs = Xs + bow * nrm(np.cross(Xw[1] - Xw[0], camp - Xw[0]))[None, :]
            else:
                Xs = to_w(pa['X'])
            q = project(cam, Xs)
            dep = np.linalg.norm(Xs - camp[None, :], axis=1)
            qi = np.clip(np.round(q).astype(int), [0, 0], [W_ - 1, H_ - 1])
            vis = dep < dg[qi[:, 1], qi[:, 0]] + 0.008 + 0.005 * dep
            if pa['jump']:
                vis[0] = vis[-1] = True
                inside = (q[:, 0] >= 0) & (q[:, 0] < W_) & (q[:, 1] >= 0) & (q[:, 1] < H_)
                vis &= inside
            else:
                vis &= B['A'][qi[:, 1], qi[:, 0]] > .5
            if not vis.any():
                continue
            n_on += 1
            drawn += 1
            q_l, vis_l, dep_l = q.copy(), vis.copy(), dep.copy()                   # 毛なみを 照らす 光は もとの 点で
            if state == 'R':                                                      # 打ち直し：少し ちがう 道
                nrmv = np.zeros_like(q)
                dq = np.gradient(q, axis=0)
                nrmv[:, 0], nrmv[:, 1] = -dq[:, 1], dq[:, 0]
                nrmv /= np.linalg.norm(nrmv, axis=1, keepdims=True) + 1e-9
                off = np.sin(np.linspace(0, np.pi, len(q))) * rs.normal(0, 3.5) * sc
                q = q + nrmv * off[:, None]
            if state == 'L':                                                      # さきがけ：とちゅうまで
                fr_ = np.random.default_rng(e['seed']).uniform(0.35, 0.7)
                nk = max(2, int(len(q) * fr_))
                q, vis = q[:nk], vis[:nk]
            if pa.get('wrap') and vis[-1] and state != 'L':                         # ふちを こえて 向こうへ まわる：光の しっぽ（空中に 少し）
                dl = q[-1] - q[-2]
                dl /= np.linalg.norm(dl) + 1e-9
                tail = q[-1] + dl[None, :] * (np.arange(1, 4)[:, None] * rs.uniform(3, 5) * sc)
                q = np.vstack([q, tail]); vis = np.r_[vis, [True, True, True]]
                dep = np.r_[dep, [dep[-1]] * 3]
            if not pa['jump'] and len(q) > 3:                                    # 大きな 折れの 間かく（28px くらい）に 間引いて から ギザギザに（雷らしい 折れ）
                stp = np.median(np.linalg.norm(np.diff(q, axis=0), axis=1)) + 1e-6
                kk = max(1, int(round(rs.uniform(20, 34) * sc / stp)))
                ki = np.unique(np.r_[np.arange(0, len(q), kk), len(q) - 1])
                kv = np.array([vis[a_:b_ + 1].all() for a_, b_ in zip(ki[:-1], ki[1:])])
                q = q[ki]
                vis = np.r_[kv, kv[-1:]] & np.r_[kv[:1], kv]
            amps = (0.3, 0.17, 0.09, 0.05, 0.03) if pa['jump'] else (0.24, 0.14, 0.085, 0.05, 0.03)
            seg, sv = q, vis
            for amp in amps:
                ln_med = np.median(np.linalg.norm(np.diff(seg, axis=0), axis=1)) if len(seg) > 1 else 0
                if ln_med < 2.2:
                    break
                ns, nv = [seg[0]], [sv[0]]
                for i in range(len(seg) - 1):
                    a_, b_ = seg[i], seg[i + 1]
                    dv = b_ - a_
                    ln = np.linalg.norm(dv) + 1e-6
                    pn = np.array([-dv[1], dv[0]]) / ln
                    ns += [(a_ + b_) / 2 + pn * rs.normal(0, amp) * ln, b_]
                    nv += [sv[i] and sv[i + 1], sv[i + 1]]
                seg, sv = np.array(ns), np.array(nv)
            n = len(seg)
            sl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(seg, axis=0), axis=1))]
            Ltot = sl[-1] + 1e-6
            uu = sl / Ltot
            f1, f2 = rs.uniform(1.2, 3.5), rs.uniform(4, 9)
            ph1, ph2 = rs.uniform(0, 6.3), rs.uniform(0, 6.3)
            bprof = (0.55 + 0.3 * np.sin(2 * np.pi * f1 * uu + ph1) + 0.15 * np.sin(2 * np.pi * f2 * uu + ph2))
            bprof *= ss(0, 0.06, uu) * (1 - 0.55 * uu ** 1.6) if not pa['jump'] else (0.75 + 0.25 * np.sin(np.pi * uu))
            bright = e['tier'] != 'faint'
            wcore = (1.25 if bright else 0.8) * (0.75 + 0.35 * hs)                 # しんの 太さ（px）
            if state == 'A':
                wcore *= 0.7
            core_k = g * (0.45 if state == 'A' else 1.0)

            def line2(buf, a_, b_, val, wpx):
                cv2.line(buf, (int(a_[0] * 8), int(a_[1] * 8)), (int(b_[0] * 8), int(b_[1] * 8)), float(val), max(1, int(round(wpx * 2))), cv2.LINE_AA, shift=2)
            for i in range(n - 1):
                if not (sv[i] and sv[i + 1]):
                    continue
                v = core_k * bprof[i]
                line2(C2, seg[i], seg[i + 1], v, wcore)
                if bright and state in ('S', 'R') and bprof[i] > 0.7:
                    line2(Hot2, seg[i], seg[i + 1], v * 0.8, max(0.5, wcore * 0.5))
            if state == 'A' or state == 'D':
                for i in range(n - 1):
                    if sv[i] and sv[i + 1]:
                        cv2.line(AG, (int(seg[i][0] * 4), int(seg[i][1] * 4)), (int(seg[i + 1][0] * 4), int(seg[i + 1][1] * 4)), float(g * bprof[i] * 0.8), 2, cv2.LINE_AA, shift=2)
            # 枝（先へ 細く うすく・枝の 枝も）
            if state in ('S', 'R'):
                nb = int(rs.integers(3, 7)) if bright else int(rs.integers(1, 4))
                for _ in range(nb):
                    i0 = int(rs.integers(1, max(2, n - 2)))
                    if not sv[i0]:
                        continue
                    tg = seg[min(i0 + 2, n - 1)] - seg[max(i0 - 2, 0)]
                    ang = math.atan2(tg[1], tg[0]) + rs.choice((-1, 1)) * rs.uniform(0.35, 0.95)
                    Lb = Ltot * rs.uniform(0.1, 0.32) * (1 if bright else 0.7)
                    stack = [(seg[i0], ang, Lb, core_k * bprof[i0] * 0.62, wcore * 0.7, 0)]
                    while stack:
                        p0_, an, Lb_, b0, w0, lev = stack.pop()
                        e_ = p0_ + Lb_ * np.array([math.cos(an), math.sin(an)])
                        bs = np.array([p0_, e_])
                        for amp in (0.26, 0.15, 0.08, 0.045):
                            if np.linalg.norm(bs[1] - bs[0]) < 2.2:
                                break
                            nb_ = [bs[0]]
                            for i in range(len(bs) - 1):
                                dv = bs[i + 1] - bs[i]; ln = np.linalg.norm(dv) + 1e-6
                                pn = np.array([-dv[1], dv[0]]) / ln
                                nb_ += [(bs[i] + bs[i + 1]) / 2 + pn * rs.normal(0, amp) * ln, bs[i + 1]]
                            bs = np.array(nb_)
                        mb = len(bs)
                        for i in range(mb - 1):
                            uq = i / max(1, mb - 1)
                            mx, my_ = (bs[i] + bs[i + 1]) / 2
                            if not (0 <= mx < W_ and 0 <= my_ < H_) or B['A'][int(my_), int(mx)] < .5:
                                break
                            line2(C2, bs[i], bs[i + 1], b0 * (1 - uq) ** 1.4, max(0.45, w0 * (1 - 0.7 * uq)))
                        if lev == 0 and rs.random() < 0.4 and mb > 4:
                            j = int(rs.integers(1, mb - 2))
                            stack.append((bs[j], an + rs.choice((-1, 1)) * rs.uniform(0.3, 0.8), Lb_ * 0.4, b0 * 0.5 * (1 - j / mb), w0 * 0.7, 1))
            # 雷の まわりの 毛なみを みじかく 照らす（ふちの 光も）
            kl = g * gain_light * (1.0 if bright else 0.4)
            if kl > 0.002:
                col = np.array([0.62, 0.3, 1.0])
                idx = np.where(vis_l)[0]
                for j in idx[::max(1, len(idx) // 7)]:
                    c3 = Xs[j]
                    rr = 0.075
                    rp = rr * fpx / max(dep_l[j], 1e-3)
                    cx, cy = q_l[j]
                    x0, x1 = int(max(0, cx - rp)), int(min(W_, cx + rp + 1))
                    y0, y1 = int(max(0, cy - rp)), int(min(H_, cy + rp + 1))
                    if x1 <= x0 or y1 <= y0:
                        continue
                    Pb, Nb, Ab = P[y0:y1, x0:x1], N[y0:y1, x0:x1], B['A'][y0:y1, x0:x1]
                    dv = c3[None, None, :] - Pb
                    dd = np.linalg.norm(dv, axis=-1) + 1e-6
                    ndl = np.clip((Nb * dv).sum(-1) / dd, 0, 1)
                    Vv = camp[None, None, :] - Pb
                    Vv /= np.linalg.norm(Vv, axis=-1, keepdims=True) + 1e-9
                    fres = (1 - np.clip((Nb * Vv).sum(-1), 0, 1)) ** 3
                    fall = (1 - ss(0.35 * rr, rr, dd))
                    term = (ndl / (1 + (dd / 0.016) ** 2) * 0.8 + fres / (1 + (dd / 0.03) ** 2) * 0.7) * fall * Ab
                    lit[y0:y1, x0:x1] += (term * kl)[..., None] * col
        C = cv2.resize(C2, (W_, H_), interpolation=cv2.INTER_AREA)
        Hot = cv2.resize(Hot2, (W_, H_), interpolation=cv2.INTER_AREA)
        return C, Hot, AG, lit, n_on


def arcs3_glow(C, Hot, AG, s):
    """しん（むらさき白）＋白熱＋やわらかく ひろがる むらさきの 光（線形）"""
    out = C[..., None] * np.array([0.9, 0.76, 1.0]) * 2.4 + Hot[..., None] * np.array([1.0, 1.0, 1.0]) * 1.6
    out += cv2.GaussianBlur(C, (0, 0), 1.2 * s)[..., None] * np.array([0.78, 0.52, 1.0]) * 2.0
    out += cv2.GaussianBlur(C, (0, 0), 3.6 * s)[..., None] * np.array([0.56, 0.24, 1.0]) * 1.5
    out += cv2.GaussianBlur(C, (0, 0), 10 * s)[..., None] * np.array([0.36, 0.09, 0.8]) * 1.0
    if AG.max() > 0:
        out += cv2.GaussianBlur(AG, (0, 0), 2.5 * s)[..., None] * np.array([0.55, 0.22, 1.0]) * 1.2
    return out.astype(np.float32)
