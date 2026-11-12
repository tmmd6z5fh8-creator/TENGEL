"""超神様の 動画（② 金の 字・③ 神様的中と 鳥居）で、まさちゃんの Meshy の 3D を 映画の カメラで 描く（第4.162版）
   まさちゃん 2026/11/12 22:32「鳥居とか文字関係はこのファイルのデータを使って！」・22:34「画質は綺麗にデータが重くなりすぎないようによろしく！」・
   22:50「これ送れてなかった！万馬券」
   もらった 3D（6つ・どれも Meshy の GLB：三角 32万〜320万・絵 3まい（色・金属と つや・面の 向き）2048×2048）
     manba  …「きせき／万馬券」           ② の 1つ目（左から 右へ ズーン）
     tengan …「テンゲル／天眼」           ② の 2つ目（右から 左へ ズーン）
     phrase …「万馬券（きせき）は／偶然にあらず／天眼（テンゲル）が導く／必然なり」  ② の 4行の 文
     logo   …「神様／的中」（赤い ふち）   ③ の 寄り（神・様・的・中：行ごとに 分ける）と さいごの 字
     omede  …「おめでとう／御座います」   ③ の さいごの 字（神様的中の 下）
     gate   … 朱ぬりの 鳥居（金の 笠木・金の 台・額「天眼」）  ③ の さいご（字の うしろ）
   3D は リポジトリに 入れない（まさちゃんの 絵と 同じ）。場所は SGD_GLB_DIR（1つずつは SGD_<名前>_GLB）で 決める。ない ときは kami_film2.py・kami_film3.py は 前の 字（Dela Gothic One の 立体）で 描く
   描き方：映画の カメラ（焦点 1500 画素・1170×2532・x 右・y 下・z おく）に 合わせて、kisekae/r3d/glb（C の ラスタライザ）で 2倍の 細かさの 見える 点を 出す
     → 点ごとに 色（絵）・金属・つや・面の 向き（法線の 絵）を 読んで、映画の まわりの 光（金の 空・夕やけ）の 映りこみで 光らせる（金＝金属：色の ついた 映りこみ／朱・黒＝ぬり：色＋うすい つや）
     → 2倍から もどす（ふちが なめらか）。字の 座標は 前の 字と 同じ（1000 単位＝大きい 字 1つ・x 右・y 下・z おく・前の 面が 0・まん中が 0）＝カメラと 動きは そのまま 使える
   ふち（雷が はしる 道）・キラッの 場所・かげの 形は、3D を 正面から 見た 形（地図）から 作る（前の 字と 同じ 形の データ）"""
import copy
import math
import os
import sys
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))

DIR = os.environ.get('SGD_GLB_DIR', '/home/claude/work/sgd162/orig')
FILES = dict(manba='manbaken.glb', tengan='golden_tengan.glb', phrase='tengan_manbaken.glb', logo='kamisama_tekichu.glb', omede='omedetou.glb', gate='celestial_gate.glb')
SSA = 2                              # 2倍で 描いて もどす
NEAR, FAR = 40.0, 60000.0            # カメラの 手前・おく（1000 単位）
GAMMA = 2.2                          # 映画の 色（画面の 明るさ）↔ 光の 計算（まっすぐな 明るさ）


def path(name):
    return os.environ.get(f'SGD_{name.upper()}_GLB') or os.path.join(DIR, FILES[name])


def have():
    """6つとも ある（ない ときは 前の 字で 描く）"""
    return all(os.path.exists(path(n)) for n in FILES)


_M = {}


def _mods():
    import glb as GLB
    import raster as RS
    return GLB, RS


def prim(name):
    """3D の 中身（1つの かたまり：頂点・面の 向き・絵の 場所・三角・絵）"""
    if name not in _M:
        GLB, _ = _mods()
        ps = GLB.load(path(name)).flatten()
        assert len(ps) == 1, (name, len(ps))
        _M[name] = ps[0]
    return _M[name]


def comp_labels(p):
    """三角ごとの つながった かたまりの 番号（頂点を 場所で 溶接して から）→ (番号, かたまりの 数)"""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    q = np.round(p.pos.astype(np.float64) / 1e-5).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    w = inv.ravel()[p.idx]
    n = int(w.max()) + 1
    g = coo_matrix((np.ones(len(w) * 3, np.int8), (np.concatenate([w[:, 0], w[:, 1], w[:, 2]]), np.concatenate([w[:, 1], w[:, 2], w[:, 0]]))), shape=(n, n))
    nc, lab = connected_components(g, directed=False)
    return lab[w[:, 0]], nc


def subset(p, tmask):
    """三角の 一部 だけの 3D（使う 頂点 だけに 詰める）"""
    idx = p.idx[tmask]
    used = np.unique(idx)
    remap = np.full(len(p.pos), -1, np.int64)
    remap[used] = np.arange(len(used))
    q = copy.copy(p)
    q.pos, q.nrm, q.uv, q.idx = p.pos[used], p.nrm[used], p.uv[used], remap[idx]
    q.tangent = p.tangent[used] if p.tangent is not None else None
    q.color = p.color[used] if p.color is not None else None
    q.uv1 = p.uv1[used] if getattr(p, 'uv1', None) is not None else None
    return q


def bake(p, s, cx, cy, zf, ox=0.0, oy=0.0):
    """GLB の 座標（x 右・y 上・z 手前）→ 字の 座標（1000 単位・x 右・y 下・z おく）：(cx, cy)＝まん中に する 所・zf＝いちばん 手前（前の 面 0）・s＝1 あたりの 単位。
       (ox, oy)：字の 座標での ずらし。向きは x 軸の まわりの 半回転（鏡うつしでは ない：三角の 向きは そのまま）"""
    q = copy.copy(p)
    P = p.pos.astype(np.float64)
    q.pos = np.stack([(P[:, 0] - cx) * s + ox, -(P[:, 1] - cy) * s + oy, (zf - P[:, 2]) * s], 1).astype(np.float32)
    f = np.float32([1, -1, -1])
    q.nrm = (p.nrm * f).astype(np.float32)
    if p.tangent is not None:
        q.tangent = np.concatenate([p.tangent[:, :3] * f, p.tangent[:, 3:]], 1).astype(np.float32)
    return q


def tone(p, gain):
    """3D の 色を 明るく／暗く（頂点の 色に かける：絵は そのまま）"""
    q = copy.copy(p)
    q.color = np.full((len(p.pos), 4), 1.0, np.float32)
    q.color[:, :3] = gain
    return q


# ---------------------------------------------------------------- 正面から 見た 形（地図）・ふち・キラッ
def front_mask(prims, k, pad):
    """字の 座標の 3D を 正面から 見た 形（1 単位 あたり k 画素）→ (0/1 の 絵, まん中の 画素 (cx, cy))。C の ラスタライザで おおい だけ 出す"""
    _, RS = _mods()
    P = np.concatenate([q.pos for q in prims]).astype(np.float64)
    lo, hi = P.min(0), P.max(0)
    Wm = int(math.ceil((hi[0] - lo[0]) * k)) + 2 * pad
    Hm = int(math.ceil((hi[1] - lo[1]) * k)) + 2 * pad
    cx, cy = -lo[0] * k + pad, -lo[1] * k + pad
    out = np.zeros(Wm * Hm, bool)
    for q in prims:
        xy = q.pos.astype(np.float64)
        z = (xy[:, 2] - lo[2]) / max(hi[2] - lo[2], 1e-6) * .98 + .01
        xyzw = np.stack([xy[:, 0] * k + cx, xy[:, 1] * k + cy, z, np.ones(len(xy))], 1).astype(np.float32)
        out |= _cover(RS, xyzw, q.idx, Wm, Hm)
    return out.reshape(Hm, Wm).astype(np.float32), (cx, cy)


def _cover(RS, xyzw, tri, Wm, Hm):
    """画面の 点（x, y, z, 1/w）と 三角 → おおった 画素"""
    import ctypes
    n = len(tri)
    tflag = np.ones(n, np.int32)
    tmat = np.zeros(n, np.int32)
    atex = (RS._fp * 1)()
    atex[0] = ctypes.cast(None, RS._fp)
    aw = np.zeros(1, np.int32)
    ah = np.zeros(1, np.int32)
    acut = np.zeros(1, np.float32)
    uv = np.zeros((len(xyzw), 2), np.float32)
    depth = np.full(Wm * Hm, np.inf, np.float32)
    tid = np.full(Wm * Hm, -1, np.int32)
    bary = np.zeros(Wm * Hm * 2, np.float32)
    facing = np.zeros(Wm * Hm, np.int8)
    RS._lib.rasterize(len(xyzw), RS._f32(xyzw).ctypes.data_as(RS._fp), RS._f32(uv).ctypes.data_as(RS._fp), n, RS._i32(tri).ctypes.data_as(RS._ip),
                      RS._i32(tflag).ctypes.data_as(RS._ip), RS._i32(tmat).ctypes.data_as(RS._ip), 1, atex, aw.ctypes.data_as(RS._ip), ah.ctypes.data_as(RS._ip), acut.ctypes.data_as(RS._fp),
                      Wm, Hm, depth.ctypes.data_as(RS._fp), tid.ctypes.data_as(RS._ip), bary.ctypes.data_as(RS._fp), facing.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)))
    return tid >= 0


def outlines(m, k, cx, cy, row, sp_px=10.0, min_px=40):
    """形の ふちを 等間隔の 点に（雷が はしる 道：kami_film3.py の _outlines と 同じ 形）：[dict(P＝点（字の 座標）, N＝外向き, L＝ふちに そった 長さ, tot＝1周, row＝行)]"""
    b = (m > .5).astype(np.uint8)
    cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    Hm, Wm = b.shape
    out = []
    for c in cs:
        c = c[:, 0, :].astype(np.float64)
        if len(c) < min_px:
            continue
        kern = np.ones(5) / 5
        c = np.stack([np.convolve(np.r_[c[-2:, i], c[:, i], c[:2, i]], kern, 'valid') for i in (0, 1)], 1)
        cc = np.vstack([c, c[:1]])
        Lc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(cc, axis=0).T))])
        tot = Lc[-1]
        n = max(8, int(tot / sp_px))
        ss = np.linspace(0, tot, n, endpoint=False)
        P = np.stack([np.interp(ss, Lc, cc[:, 0]), np.interp(ss, Lc, cc[:, 1])], 1)
        tg = np.roll(P, -1, 0) - np.roll(P, 1, 0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
        tx = np.clip(np.round(P[:, 0] + nr[:, 0] * 3).astype(int), 0, Wm - 1)
        ty = np.clip(np.round(P[:, 1] + nr[:, 1] * 3).astype(int), 0, Hm - 1)
        if (b[ty, tx] > 0).mean() > .5:
            nr = -nr
        out.append(dict(P=(P - [cx, cy]) / k, N=nr, L=ss / k, tot=tot / k, row=row))
    return out


def glint_px(m, em_px, n=14, seed=1, lo=2.0, hi=.07, gap=.42):
    """キラッの 場所の 候補（ふちの すぐ 内がわ：ばらばらに）→ 地図の 画素 (x, y)"""
    d = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 5)
    cand = np.argwhere((d > lo) & (d < hi * em_px))
    rng = np.random.default_rng(seed)
    pick = []
    if len(cand):
        for i in rng.permutation(len(cand))[:6000]:
            y_, x_ = cand[i]
            if all((x_ - a) ** 2 + (y_ - b) ** 2 > (gap * em_px) ** 2 for a, b in pick):
                pick.append((x_, y_))
            if len(pick) >= n:
                break
    return np.array(pick, np.float64).reshape(-1, 2)


def make(prims, k, em=1000.0, pad_em=.12, glint_n=14, seed=1, rows=None):
    """字の 座標の 3D（1つか いくつか）→ 立体（kami_film2・kami_film3 の 字と 同じ 名前の データ）：
       prims・size（はば, 高さ）・地図 3段（lv：かげ・キラッの 場所の 行列 用）・outl（ふち）・glints（字の 座標）・glints_px（地図の 画素）・k・c・shape・alpha
       rows：prims ごとの 行の 番号（雷が 字から 字へ とぶ とき 用。なければ ぜんぶ 0）"""
    pad = int(pad_em * em * k)
    m, (cx, cy) = front_mask(prims, k, pad)
    P = np.concatenate([q.pos for q in prims])
    lo, hi = P.min(0), P.max(0)
    outl = []
    if rows is None:
        outl = outlines(m, k, cx, cy, 0)
    else:
        for q, r in zip(prims, rows):
            mq, (qx, qy) = front_mask([q], k, pad)
            outl += outlines(mq, k, qx, qy, r)
    gp = glint_px(m, em * k, glint_n, seed)
    lv = []
    m4 = np.dstack([m, np.zeros_like(m), np.zeros_like(m), np.zeros_like(m)]).astype(np.float32)
    kk, ccx, ccy = k, cx, cy
    for _ in range(3):
        lv.append(dict(m4=m4, rim=None, extra=None, k=kk, c=(ccx, ccy)))
        h_, w_ = m4.shape[:2]
        m4 = cv2.resize(m4, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        kk *= (w_ // 2) / w_
        ccx, ccy = ccx * (w_ // 2) / w_, ccy * (h_ // 2) / h_
    return dict(glb=True, prims=prims, size=(float(hi[0] - lo[0]), float(hi[1] - lo[1])), depth=float(hi[2] - lo[2]), lo=lo, hi=hi, k=k, c=(cx, cy), shape=m.shape, alpha=m,
                lv=lv, outl=outl, glints_px=gp, glints=(gp - np.array([cx, cy])) / k if len(gp) else np.zeros((0, 2)), ymid=0.0, style='glb')


# ---------------------------------------------------------------- 映画の カメラ・見える 点
def camera(W, H, focal, ss=SSA):
    """映画の カメラ（まん中 (W/2, H/2)・焦点 focal 画素）を ss 倍の 細かさで"""
    _, RS = _mods()
    fov = math.degrees(2 * math.atan((H / 2) / focal))
    return RS.Camera.look_at((0, 0, 0), (0, 0, -1), (0, 1, 0), fov_y=fov, W=W * ss, H=H * ss, near=NEAR, far=FAR)


def model_matrix(R, Tv):
    """字の 座標 → カメラ（映画：x 右・y 下・z おく）→ ラスタライザの カメラ（x 右・y 上・z 手前）"""
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = Tv
    return np.diag([1.0, -1.0, -1.0, 1.0]) @ M


CHUNK = int(os.environ.get('SGD_CHUNK', '500000'))      # 見える 点を この 数ずつ 色に する（メモリを おさえる：1点ずつの 計算なので 絵は 同じ）


def _raster(prims, R, Tv, cam):
    """見える 点を 出す（C の ラスタライザ：cam の 画素）→ 点ごとの 三角と 重み。色・面の 向きなどは _attrs() が 点の 一部ずつ 読む。
       kisekae/r3d/glb/raster.py の render() の 前半（光は ここでは 計算しない：映画の 光で shade() が 光らせる）"""
    import ctypes
    _, RS = _mods()
    sc = RS.Scene(prims, model_matrix(R, Tv))
    clip = RS._project(cam, sc.pos)
    xyzw, tri, src, lerp = RS._clip_and_screen(cam, clip, sc.tri, None)
    tmat = sc.tmat[src]
    tflag = np.ones(len(tri), np.int32)                         # 両面を 描く（取りこんだ 形の 面の 向きは 信じない）
    uvs = RS._lerp_attr(sc.uv, lerp)
    nmat = len(sc.mats)
    atex = (RS._fp * nmat)()
    for i in range(nmat):
        atex[i] = ctypes.cast(None, RS._fp)
    aw = np.zeros(nmat, np.int32)
    ah = np.zeros(nmat, np.int32)
    acut = np.zeros(nmat, np.float32)
    W, H = cam.W, cam.H
    depth = np.full(W * H, np.inf, np.float32)
    tid = np.full(W * H, -1, np.int32)
    bary = np.zeros(W * H * 2, np.float32)
    facing = np.zeros(W * H, np.int8)
    RS._lib.rasterize(len(xyzw), RS._f32(xyzw).ctypes.data_as(RS._fp), RS._f32(uvs).ctypes.data_as(RS._fp), len(tri), RS._i32(tri).ctypes.data_as(RS._ip),
                      RS._i32(tflag).ctypes.data_as(RS._ip), RS._i32(tmat).ctypes.data_as(RS._ip), nmat, atex, aw.ctypes.data_as(RS._ip), ah.ctypes.data_as(RS._ip), acut.ctypes.data_as(RS._fp),
                      W, H, depth.ctypes.data_as(RS._fp), tid.ctypes.data_as(RS._ip), bary.ctypes.data_as(RS._fp), facing.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)))
    pix = np.flatnonzero(tid >= 0)
    if not len(pix):
        return None
    at = dict(pos=RS._lerp_attr(sc.pos, lerp), nrm=RS._lerp_attr(sc.nrm, lerp), tan=RS._lerp_attr(sc.tan, lerp), col=RS._lerp_attr(sc.col, lerp))
    return dict(mats=sc.mats, tri=tri, tmat=tmat, uvs=uvs, xy=xyzw[:, :2], at=at, pix=pix, t=tid[pix], b1=bary[pix * 2], b2=bary[pix * 2 + 1], W=W, H=H)


def _attrs(st, sl=slice(None)):
    """見える 点（の 一部：sl）ごとの 場所・面の 向き（法線の 絵も）・色・金属・つや（どれも 映画の カメラの 向き：x 右・y 下・z おく）"""
    _, RS = _mods()
    tri, tmat, uvs, at = st['tri'], st['tmat'], st['uvs'], st['at']
    pix, t, b1, b2 = st['pix'][sl], st['t'][sl], st['b1'][sl], st['b2'][sl]
    n = len(pix)
    b0 = 1 - b1 - b2
    vi = tri[t]

    def interp(a):
        return a[vi[:, 0]] * b0[:, None] + a[vi[:, 1]] * b1[:, None] + a[vi[:, 2]] * b2[:, None]
    P = interp(at['pos'])
    N = RS.normalize(interp(at['nrm']))
    UV = interp(uvs)
    T = interp(at['tan'])
    C = interp(at['col'])                                       # 頂点の 色（tone() で かけた 明るさ：ふつうは 1）
    V = RS.normalize(-P)                                        # 目は 0
    fc = np.where(np.sum(N * V, -1) < 0, -1.0, 1.0).astype(np.float32)
    N = N * fc[:, None]
    mid = tmat[t]
    xy = st['xy']
    sa = 0.5 * np.abs((xy[vi[:, 1], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 2], 1] - xy[vi[:, 0], 1]) - (xy[vi[:, 2], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 1], 1] - xy[vi[:, 0], 1]))
    ua = 0.5 * np.abs((uvs[vi[:, 1], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 2], 1] - uvs[vi[:, 0], 1]) - (uvs[vi[:, 2], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 1], 1] - uvs[vi[:, 0], 1]))
    alb = np.zeros((n, 3), np.float32)
    mr = np.zeros((n, 2), np.float32)
    Nn = N.copy()
    for i, m in enumerate(st['mats']):
        sel = np.flatnonzero(mid == i)
        if not len(sel):
            continue
        uv = UV[sel]

        def lod_of(tx):
            th, tw = tx.img.shape[:2]
            return 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
        bc = np.tile(np.asarray(m.base_color[:3], np.float32), (len(sel), 1))
        if m.base_tex is not None:
            s = RS.sample(m.base_tex.tex, m.base_tex.uv(uv), lod_of(m.base_tex.tex))
            bc = bc * RS.srgb_to_linear(s[:, :3])
        alb[sel] = bc * C[sel, :3]
        m_r = np.tile([m.metallic, m.roughness], (len(sel), 1)).astype(np.float32)
        if m.mr_tex is not None:
            s = RS.sample(m.mr_tex.tex, m.mr_tex.uv(uv), lod_of(m.mr_tex.tex))
            m_r = m_r * np.stack([s[:, 2], s[:, 1]], 1)
        mr[sel] = m_r
        if m.normal_tex is not None and np.any(np.abs(T[sel, :3]).sum(1) > 0):
            s = RS.sample(m.normal_tex.tex, m.normal_tex.uv(uv), lod_of(m.normal_tex.tex))
            tn = s[:, :3] * 2 - 1
            tn[:, :2] *= m.normal_tex.scale
            tn = RS.normalize(tn)
            Ns = N[sel]
            Ts = T[sel, :3] * fc[sel][:, None]
            Ts = RS.normalize(Ts - Ns * np.sum(Ns * Ts, 1, keepdims=True))
            Bs = np.cross(Ns, Ts) * T[sel, 3:4]
            Nn[sel] = RS.normalize(Ts * tn[:, 0:1] + Bs * tn[:, 1:2] + Ns * tn[:, 2:3])
    f = np.float32([1, -1, -1])                                 # ラスタライザの カメラ → 映画の カメラ
    return dict(pix=pix, W=st['W'], H=st['H'], P=P * f, N=Nn * f, Ng=N * f, V=V * f, alb=alb, metal=np.clip(mr[:, 0], 0, 1), rough=np.clip(mr[:, 1], .04, 1))


def gbuf(prims, R, Tv, cam):
    """見える 点 ぜんぶの 場所・面の 向き・色・金属・つや（いちどに：点が 多いと メモリを 食う。draw() は CHUNK ずつ 読む）"""
    st = _raster(prims, R, Tv, cam)
    return None if st is None else _attrs(st)


# ---------------------------------------------------------------- 光らせる（映画の まわりの 光の 映りこみ）
LIGHTS = (((-.45, -.78, -.45), (1.0, .93, .80), 2.6),      # 左上 手前からの 光（映画の カメラ：y 下 → 上は マイナス）：(向き, 色, 強さ)
          ((.62, -.30, -.52), (1.0, .86, .62), .9),         # 右 手前からの うすい 光
          ((.10, -.55, .80), (1.0, .80, .45), 1.4))         # うしろ 上からの ふちの 光


def shade(g, env, env_rot=0.0, R=None, Tv=None, env_r=2600.0, look=None, shine=None):
    """見える 点を 光らせる → 色（映画の 明るさ：0〜1 より 明るい 所 あり）。
       env(rv, rot, level)：映りこみの 向き（映画の カメラ）→ 色（映画の 明るさ）。level 0＝はっきり・1＝少し ぼけ・2＝大きく ぼけ（面を てらす 光）
       金（金属）：色の ついた 映りこみ（つやの ぶん だけ ぼかす）＋光の つや（GGX）／ぬり（朱・黒）：色 × まわりの 光 ＋ うすい つや
       look：見た目の 強さ（dict：gain＝ぜんたい・spec＝映りこみ・diff＝ぬりの 明るさ・coat＝白い つや・key＝光・amb＝金の 面の 下じき・tint＝金の 色の こさ（1＝絵の まま・0＝白）・sat＝さいごの 色の こさ）。
       shine＝(場所, はば[, 強さ])：光が すべる（R・Tv が いる）"""
    _, RS = _mods()
    lk = dict(gain=1.0, spec=1.0, diff=1.0, coat=.1, key=1.0, amb=.16, tint=1.0, sat=1.0)
    lk.update(look or {})
    N, V, a = g['N'], g['V'], g['alb']
    m, r = g['metal'][:, None], g['rough'][:, None]
    ndv = np.clip(np.sum(N * V, -1, keepdims=True), 0, 1)
    rv = 2 * ndv * N - V                                        # 映りこみの 向き
    if Tv is not None:
        rv = rv + (g['P'] - np.asarray(Tv, np.float32)) / env_r          # 字の 場所でも かわる（近い 空）
        rv /= np.linalg.norm(rv, axis=-1, keepdims=True) + 1e-9
    e0 = np.asarray(env(rv, env_rot, 0), np.float32)
    e1 = np.asarray(env(rv, env_rot, 1), np.float32)
    w1 = np.clip((r - .12) / .5, 0, 1)                          # つやが にぶい ほど ぼけた 映りこみ
    es = np.power(np.clip(e0 * (1 - w1) + e1 * w1, 0, None), GAMMA)
    ed = np.power(np.clip(np.asarray(env(N, env_rot, 2), np.float32), 0, None), GAMMA)
    am = a
    if lk['tint'] != 1.0:                                       # 金の 色を 少し 白く（映りこみが こい だいだいに しずまない ように）
        lum = (a @ np.float32([.3, .59, .11]))[:, None]
        am = np.clip(lum + (a - lum) * lk['tint'], 0, None) if lk['tint'] < 1 else a
        am = a * lk['tint'] + (1 - lk['tint']) * np.maximum(a, lum * np.float32([1.0, .82, .5]))
    f0 = .04 * (1 - m) + am * m
    fr = f0 + (1 - f0) * (1 - ndv) ** 5
    col = es * fr * (1 - .45 * r) * lk['spec']                  # 映りこみ（金は 金の 色・ぬりは うすい 白）
    col += a * (1 - m) * ed * lk['diff']                        # ぬりの 色
    col += am * m * ed * lk['amb']                              # 金の 面の 下じき（映りこみが 暗い 向きでも まっ黒に しない）
    col += es * lk['coat'] * (.25 + .75 * (1 - ndv) ** 2)       # 白い つや（ふちほど 強く）
    rr = g['rough']
    for d, c, it in LIGHTS:
        L = np.asarray(d, np.float32)
        L = L / np.linalg.norm(L)
        spec, ndl = RS._ggx(N, V, L[None, :], rr, f0)
        col += (a * (1 - m) / np.pi * lk['diff'] + spec) * ndl[:, None] * (np.asarray(c, np.float32) * (it * lk['key']))
    col = np.power(np.clip(col, 0, None), 1 / GAMMA) * lk['gain']
    if lk['sat'] != 1.0:
        lum = (col @ np.float32([.3, .59, .11]))[:, None]
        col = np.clip(lum + (col - lum) * lk['sat'], 0, None)
    if shine is not None and R is not None:                     # 光が すべる（ななめの 光の 帯）
        s_pos, s_w = shine[:2]
        amt = shine[2] if len(shine) > 2 else .5
        d = g['P'] - np.asarray(Tv, np.float32)
        u = d @ np.asarray(R[:, 0], np.float32)
        v_ = d @ np.asarray(R[:, 1], np.float32)
        band = np.exp(-(((u + v_ * .55) / 1000 - s_pos) / s_w) ** 2)
        col = col + band[:, None] * np.float32([1.0, .9, .62]) * amt
    return col.astype(np.float32)


def layer(g, col, W, H, ss=SSA):
    """見える 点の 色 → 画面の 絵（premultiplied RGBA・W×H：ss 倍から 面積で もどす）"""
    out = np.zeros((g['H'] * g['W'], 4), np.float32)
    out[g['pix'], :3] = col
    out[g['pix'], 3] = 1.0
    out = out.reshape(g['H'], g['W'], 4)
    return cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA) if ss != 1 else out


def draw(obj, R, Tv, W, H, focal, env, env_rot=0.0, env_r=2600.0, look=None, shine=None, ss=SSA):
    """立体を 1コマ 描く → premultiplied RGBA（W×H・映画の 明るさ）。見えなければ None。
       見える 点は CHUNK ずつ 色に する（寄りの コマは 点が 800万を こえる：いちどに やると 4GB を こえて 止まった）"""
    cam = camera(W, H, focal, ss)
    st = _raster(obj['prims'], np.asarray(R, np.float64), np.asarray(Tv, np.float64), cam)
    if st is None:
        return None
    n = len(st['pix'])
    col = np.empty((n, 3), np.float32)
    for i in range(0, n, CHUNK):
        col[i:i + CHUNK] = shade(_attrs(st, slice(i, i + CHUNK)), env, env_rot, R, Tv, env_r, look, shine)
    return layer(st, col, W, H, ss)
