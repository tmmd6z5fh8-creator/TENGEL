# 思い出フィギュアの 形を へらして、アプリ用の 絵（色・物の 向きの 法線・金属／あらさ）を 作る（11/09 21:10 に 作業場所が 消えた あとに 作り直した 版）
#   python3 kisekae/fig/fig_prep.py <まさちゃんの GLB> <出す 名前（…/out/fig1）> [三角の 数 90000] [色 2048] [法線 1024] [金属 1024] [--keep（形は 前の .npz の まま・絵だけ 作り直す）]
#   → <名前>.npz（V：高さ 2.15・y 0〜・x／z まん中・T・UVc＝三角の 角ごとの UV）・<名前>_c.webp・_n.webp・_m.webp（どれも 劣化なしの WebP）
#   ・形：QEM で へらす。UV の 継ぎ目で 分かれた 頂点は いっしょに たたむ（同じ 絵の 島の 中で）→ 元の UV と 絵を そのまま 使える（絵の 焼き直しが いらない）
#   ・法線：元の 細かい 形（と 法線マップ）を UV の 上に 塗って「物の 向き」の 法線の 絵に する → へらした 形でも 細かい でこぼこが 見える
#   ・へらす ときは UV の 上で 面が うら返らない・島の ふちが 1点（FIG_UVTOL）より 動かない ように する（島の 外に はみ出て 別の 場所の 色を 塗らない）
#   ・それでも はみ出る ところは 3D で 元の 同じ 場所の 色に する（fix_maps）・重なった 三角は あいて いる 所へ 引っこす
#   ・法線・金属／あらさ は 色と 同じ 大きさで 作って、島を またがずに 小さく する（chart_down：島の ふちに となりの 金属が まざらない）
#   （まさちゃん 11/09 23:01「ところどころ破片のようなパーツが出てきてしまってる」）
#   ・材質が いくつも ある ときは 絵を 1枚に ならべる（UV も ずらす）
#   ・まさちゃんの GLB と それから 作った もの は リポジトリに 入れない（この スクリプトだけ）
import ctypes, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
import glb


def lib():
    import hashlib
    c = os.path.join(HERE, 'qem.c'); h = hashlib.sha1(open(c, 'rb').read()).hexdigest()[:10]
    so = os.path.join(tempfile.gettempdir(), f'tengel_libqem_{h}.so')      # 中身ごとに 別の 名前（動いて いる 計算の .so を 上書き しない）
    if not os.path.exists(so):
        tmp = so + '.tmp'; subprocess.run(['gcc', '-O2', '-shared', '-fPIC', '-o', tmp, c, '-lm'], check=True); os.replace(tmp, so)
    L = ctypes.CDLL(so)
    L.qem_decimate.restype = ctypes.c_int
    L.qem_decimate.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_void_p]
    L.uv_raster.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
    L.uv_raster_v.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
    L.qem_decimate2.restype = ctypes.c_int
    L.qem_decimate2.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p]
    return L


def decimate(L, V, F, lock, target, maxcos=0.2):
    V = np.ascontiguousarray(V, np.float64); F = np.ascontiguousarray(F, np.int32); lock = np.ascontiguousarray(lock, np.uint8)
    out = np.zeros_like(F)
    n = L.qem_decimate(len(V), V.ctypes.data, len(F), F.ctypes.data, lock.ctypes.data, int(target), float(maxcos), out.ctypes.data)
    return out[:n]


def uv_raster(L, UV, F, A, W, H):
    UV = np.ascontiguousarray(UV, np.float64); F = np.ascontiguousarray(F, np.int32); A = np.ascontiguousarray(A, np.float64)
    K = A.shape[2]; out = np.zeros((H, W, K), np.float32); cov = np.zeros((H, W), np.uint8)
    L.uv_raster(len(F), UV.ctypes.data, F.ctypes.data, A.ctypes.data, K, W, H, out.ctypes.data, cov.ctypes.data)
    return out, cov.astype(bool)


def decimate2(L, V, F, target, maxcos=0.2, UV=None, uvtol=0.0):       # 継ぎ目ごと（同じ 場所の 頂点を いっしょに）へらす・UV：うら返し／島の ふちの ずれ を 見る
    P, pid = np.unique(V, axis=0, return_inverse=True); pid = pid.astype(np.int32).ravel()
    a_ = np.concatenate([pid[F[:, 0]], pid[F[:, 1]], pid[F[:, 2]]]).astype(np.int64); b_ = np.concatenate([pid[F[:, 1]], pid[F[:, 2]], pid[F[:, 0]]]).astype(np.int64)
    key = np.minimum(a_, b_) * len(P) + np.maximum(a_, b_); del a_, b_
    ue, cnt = np.unique(key, return_counts=True); del key
    be = ue[cnt == 1]; del ue, cnt
    plock = np.zeros(len(P), np.uint8); plock[be // len(P)] = 1; plock[be % len(P)] = 1; del be
    print('場所', len(P), '（分かれた 頂点', len(V), '）・ほんとうの ふち', int(plock.sum()), flush=True)
    P = np.ascontiguousarray(P, np.float64); F = np.ascontiguousarray(F, np.int32); out = np.zeros_like(F)
    U = None if UV is None else np.ascontiguousarray(UV, np.float64)
    n = L.qem_decimate2(len(V), pid.ctypes.data, len(P), P.ctypes.data, len(F), F.ctypes.data, plock.ctypes.data, int(target), float(maxcos),
                        None if U is None else U.ctypes.data, float(uvtol), out.ctypes.data)
    return out[:n]


def uv_raster_v(L, UV, F, A, W, H):         # A：頂点ごと（nv×K）
    UV = np.ascontiguousarray(UV, np.float64); F = np.ascontiguousarray(F, np.int32); A = np.ascontiguousarray(A, np.float32)
    K = A.shape[1]; out = np.zeros((H, W, K), np.float32); cov = np.zeros((H, W), np.uint8)
    L.uv_raster_v(len(F), UV.ctypes.data, F.ctypes.data, A.ctypes.data, K, W, H, out.ctypes.data, cov.ctypes.data)
    return out, cov.astype(bool)


def fill(img, cov):            # 塗れなかった ところ（すき間）を いちばん 近い 塗れた 色で うめる（ミップマップで ふちが にじまない）
    if cov.all(): return img
    _, (iy, ix) = ndimage.distance_transform_edt(~cov, return_indices=True)
    return img[iy, ix]


def fix_maps(L, V, N, UV, F, V2, T2, UVc, maps, tol=0.02, k=0.05, log=print, pad=4):
    """へらした 三角が 元の 絵の 島の 外（すき間・ほかの 島）に はみ出て 塗る ところを、元の 形の 同じ 3D の 場所の 色に する（まさちゃん 11/09 23:01「破片のようなパーツ」）
       ・へらすと 島の ふちの 線が まっすぐに なって、三角が 島の 外の すき間に はみ出る → 前は すき間を「絵の 上で 近い 色」で うめて いたので、
         となりの 島（金の わく・白い 大理石 など 別の 場所）の 色が 破片の ように 出て いた
       ・絵の 1まい ごとに：へらした 三角の 3D の 位置 と 元の 三角の 3D の 位置 が 合う（tol 以内・同じ 向き）→ 元の まま／合わない → 3D で いちばん 近い 元の 場所（向きも 近い）の 色
       ・のこりの すき間は 近くの 正しい 色で うめる（ミップマップ 用）
       ・はみ出た 三角が ほかの 三角の 使う 島に かぶる（重なり）→ その 三角だけ 絵の あいて いる 所へ 引っこして（自分だけの 小さい 島）3D で 元の 色を 塗る
       maps：{大きさ: [元の 絵（H×W×C・元の 三角が 塗った ところ だけ 正しい）, ...]} → 同じ 形で 直した 絵・大きさ ごとの 数（直した 割合 など）・新しい UVc（引っこした 三角）"""
    from scipy.spatial import cKDTree
    VN = np.concatenate([V, N], 1).astype(np.float32)
    P2 = V2[T2].astype(np.float64); fn = np.cross(P2[:, 1] - P2[:, 0], P2[:, 2] - P2[:, 0]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    A2 = np.concatenate([P2, np.repeat(fn[:, None], 3, 1), np.repeat(np.arange(len(T2), dtype=np.float64)[:, None, None], 3, 1)], 2)
    idx = np.arange(len(T2) * 3, dtype=np.int32).reshape(-1, 3); UVc = np.asarray(UVc, np.float64).copy()
    orig = {}

    def org(S):                                                                         # 元：絵の 1まい ごとの 3D の 位置・向き
        if S not in orig:
            Ro, covo = uv_raster_v(L, UV, F, VN, S, S); no = Ro[..., 3:6]; no /= np.maximum(np.linalg.norm(no, axis=2, keepdims=True), 1e-9); orig[S] = (Ro, covo, no)
        return orig[S]

    def look(S):                                                                        # へらした 三角を 両方の 順で 塗る（重なりを 見つける）・元と 合うか
        Ro, covo, no = org(S); r = []
        for order in (slice(None), slice(None, None, -1)):
            Rd, cv = uv_raster(L, UVc[order].reshape(-1, 2), idx, A2[order], S, S)
            ok = cv & covo & (np.linalg.norm(Rd[..., :3] - Ro[..., :3], axis=2) < tol) & ((Rd[..., 3:6] * no).sum(2) > 0)
            r.append((Rd, cv, ok))
        return r
    # 重なり：はみ出た 三角が、ほかの 三角が 使って いる 島に かぶる → その 絵は 持ち主の 色の まま なので、はみ出た 三角を 絵の あいて いる 所へ 引っこす（自分だけの 小さい 島）
    S0 = max(maps); moved = 0; lost = 0
    for it in range(4):
        (R1, c1, a1), (R2, c2, a2) = look(S0)
        f1 = np.rint(R1[..., 6]).astype(np.int64); f2 = np.rint(R2[..., 6]).astype(np.int64); ov = c1 & (f1 != f2)
        bad = np.unique(np.concatenate([f2[ov & a1 & ~a2], f1[ov & a2 & ~a1], f2[ov & ~a1 & ~a2]]))
        if not len(bad): break
        occ = ndimage.binary_dilation(c1 | c2, iterations=pad)
        UVc, ok_n = _place(UVc, bad, occ, S0, pad)
        moved += ok_n; lost += len(bad) - ok_n
        if ok_n == 0: break
    if moved or lost: log('  重なった 三角を 引っこした %d（場所が なかった %d）' % (moved, lost))
    out, stat = {}, {}
    for S, imgs in maps.items():
        Ro, covo, no = org(S)
        (Rq, c1, a1), (_, c2, a2) = look(S)
        agree = a1 | a2; covd = c1 | c2                                                 # どちらかが 元と 合えば 元の まま
        need = covd & ~agree
        src = np.nonzero(covo.ravel())[0]
        tree = cKDTree(np.concatenate([Ro[..., :3].reshape(-1, 3)[src], k * no.reshape(-1, 3)[src]], 1))
        q = Rq.reshape(-1, Rq.shape[2])[need.ravel()]
        _, j = tree.query(np.concatenate([q[:, :3], k * q[:, 3:6]], 1), workers=-1)
        take = src[j]; flat = np.nonzero(need.ravel())[0]
        valid = covd | covo; res = []
        for img in imgs:
            a = img.reshape(-1, img.shape[2]).copy(); a[flat] = a[take]
            res.append(fill(a.reshape(img.shape), valid))
        out[S] = res; stat[S] = (float(covd.mean()), float(need.sum() / max(1, covd.sum())), moved, lost)
        log('  絵 %d：へらした 三角が 塗る %.3f・元の 島の 外 → 3D で 元の 色に した %.4f' % (S, stat[S][0], stat[S][1]))
    return out, stat, UVc.astype(np.float32)


def _place(UVc, faces, occ, S, pad, blk=4):
    """三角（faces）を 絵の あいて いる 所（occ が False）へ 引っこす：形と 大きさは そのまま（UV の 中で 平行に 動かす）・まわりに pad の すき間
       大きい 順に、左上から 空いた 所を 探す（blk×blk の ます で 数える）→ 新しい UVc・引っこせた 数"""
    G = S // blk
    gb = occ[:G * blk, :G * blk].reshape(G, blk, G, blk).any((1, 3))
    uvp = UVc[faces] * S; mn = uvp.min(1); ext = uvp.max(1) - mn
    n_ok = 0
    for i in np.argsort(-(ext[:, 0] * ext[:, 1])):
        bw = int(np.ceil((ext[i, 0] + 2 * pad + 2) / blk)); bh = int(np.ceil((ext[i, 1] + 2 * pad + 2) / blk))
        if bw > G or bh > G: continue
        sat = np.zeros((G + 1, G + 1), np.int32); sat[1:, 1:] = gb.astype(np.int32).cumsum(0).cumsum(1)
        win = sat[bh:, bw:] - sat[:-bh, bw:] - sat[bh:, :-bw] + sat[:-bh, :-bw]
        ys, xs = np.nonzero(win == 0)
        if not len(ys): continue
        y0, x0 = int(ys[0]), int(xs[0])
        off = np.array([x0 * blk + pad + 1.0, y0 * blk + pad + 1.0]) - mn[i]
        UVc[faces[i]] = (uvp[i] + off) / S
        gb[y0:y0 + bh, x0:x0 + bw] = True; n_ok += 1
    return UVc, n_ok


def mesh_pos(L, V2, T2, UVc, S):   # へらした 三角の 絵の 1まい ごとの 3D の 位置（S×S×3）と 塗れたか
    P2 = np.asarray(V2, np.float64)[T2]
    return uv_raster(L, np.asarray(UVc, np.float64).reshape(-1, 2), np.arange(len(T2) * 3, dtype=np.int32).reshape(-1, 3), P2, S, S)


def chart_down(img, Ph, ch, Pl, cl, tol=0.02):
    """絵を 小さく する（島を またいで まぜない）：小さい 絵の 1まいは、大きい 絵の その 中の 点の うち 3D で 同じ 場所（tol 以内）の ものだけ 平均
       （ふつうに 小さく すると となりの 島の 色・金属が まざって、島の ふちが 紙を はった ように 見える：まさちゃん 11/09 23:01）
       img：大きい 絵（Sh×Sh×C）・Ph／ch：大きい 絵の 3D の 位置と 塗れたか・Pl／cl：小さい 絵の → 小さい 絵（すき間は 近くの 色で うめる）"""
    S = Pl.shape[0]; k = img.shape[0] // S; C = img.shape[2]
    I = img.reshape(S, k, S, k, C); Pr = Ph.reshape(S, k, S, k, 3); cr = ch.reshape(S, k, S, k)
    w = (cr & (np.linalg.norm(Pr - Pl[:, None, :, None, :], axis=-1) < tol)).astype(np.float32)
    ws = w.sum((1, 3)); wc = cr.astype(np.float32); wcs = wc.sum((1, 3))
    a = (I * w[..., None]).sum((1, 3)) / np.maximum(ws, 1e-9)[..., None]
    b = (I * wc[..., None]).sum((1, 3)) / np.maximum(wcs, 1e-9)[..., None]
    out = np.where((ws > 0)[..., None], a, np.where((wcs > 0)[..., None], b, I.mean((1, 3))))
    return fill(out, cl)


def smooth_mr(mr, Ph, ch, cell=0.025, rbin=0.04):
    """金属／あらさ を 3D の 近くで ならす（バイラテラル：3D の 位置 と あらさ の 4次元の ます・金属の 強さで 3つに 分ける）
       ・元の 絵は 島ごとに あらさが 少し ちがう（大理石で 0.38〜0.41）→ この アプリの 光では 島の 形の まだら（紙を はった ような 形）に 見える
       ・あらさが 近い もの（rbin 0.04 くらい）・同じ 金属の 強さ の 中だけ 平均：大理石と 赤い 布・金の わく などは まぜない
       ・島の ふちに まざった 中くらいの 金属も その 材料の 値に もどる
       Ph／ch：へらした 三角の 絵の 1まい ごとの 3D の 位置と 塗れたか（同じ 大きさ）"""
    pos = Ph[ch].astype(np.float64); v = mr[ch].astype(np.float64)
    cls = np.digitize(v[:, 2], [0.33, 0.66])
    lo = pos.min(0) - cell; g = (pos - lo) / cell; nr = int(np.ceil(1 / rbin)) + 3
    gr = np.clip(v[:, 1], 0, 1) / rbin + 1.0
    dims = tuple(np.floor(g).astype(int).max(0) + 3) + (nr,); size = int(np.prod(dims))
    out = v.copy()
    for c in range(3):
        m = cls == c
        if m.sum() < 10: continue
        G4 = np.concatenate([g[m], gr[m][:, None]], 1)
        flat = np.ravel_multi_index(tuple(np.floor(G4).astype(int).T), dims)
        crd = (G4 - 0.5).T; sig = (1.0, 1.0, 1.0, 0.8)
        n = ndimage.map_coordinates(ndimage.gaussian_filter(np.bincount(flat, minlength=size).astype(np.float32).reshape(dims), sig), crd, order=1)
        for j in (1, 2):
            acc = ndimage.gaussian_filter(np.bincount(flat, weights=v[m, j], minlength=size).astype(np.float32).reshape(dims), sig)
            out[m, j] = ndimage.map_coordinates(acc, crd, order=1) / np.maximum(n, 1e-6)
    res = mr.copy(); res[ch] = out.astype(res.dtype)
    return res


def rs(img, size):            # float の 絵（H×W×C・0〜1）→ size×size
    im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)[..., :3])
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255


def main():
    KEEP = '--keep' in sys.argv                 # 形は 前に へらした <名前>.npz の まま（絵だけ 作り直す）
    av = [a for a in sys.argv[1:] if not a.startswith('--')]
    src, outp = av[0], av[1]
    TARGET = int(av[2]) if len(av) > 2 else 90000
    CS = int(av[3]) if len(av) > 3 else 2048; NS = int(av[4]) if len(av) > 4 else 1024; MS = int(av[5]) if len(av) > 5 else 1024
    L = lib(); m = glb.load(src); prims = m.flatten()
    print(src, 'prims', len(prims), 'tris', sum(p.ntri for p in prims), 'verts', sum(len(p.pos) for p in prims), flush=True)
    # 材質ごとに 絵の 置き場所（1つなら そのまま・いくつも なら ならべる）
    mats = []
    for p in prims:
        if p.mat not in mats: mats.append(p.mat)
    nm = len(mats); cols = int(np.ceil(np.sqrt(nm))); rows = int(np.ceil(nm / cols))
    def tile(mi): return (mi % cols, mi // cols)
    V, N, UV, T, F, base = [], [], [], [], [], 0
    for p in prims:
        mi = mats.index(p.mat); cx, cy = tile(mi)
        uv = p.uv if p.uv is not None else np.zeros((len(p.pos), 2), np.float32)
        uv = np.clip(np.asarray(uv, np.float64), 0, 1); uv = np.stack([(cx + uv[:, 0]) / cols, (cy + uv[:, 1]) / rows], 1)
        V.append(p.pos.astype(np.float64)); N.append(p.nrm.astype(np.float64)); UV.append(uv)
        T.append(p.tangent.astype(np.float64) if p.tangent is not None else np.tile([1.0, 0, 0, 1], (len(p.pos), 1)))
        F.append((np.asarray(p.idx, np.int64).reshape(-1, 3) + base).astype(np.int32)); base += len(p.pos)
    V = np.concatenate(V); N = np.concatenate(N).astype(np.float32); UV = np.concatenate(UV); T = np.concatenate(T).astype(np.float32); F = np.concatenate(F)
    del prims
    # 高さ 2.15・地面 y=0・x／z まん中（向きは そのまま：fig_bake.py の PROP と 同じ）
    lo, hi = V.min(0), V.max(0); s = 2.15 / (hi[1] - lo[1]); off = np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
    V = (V - off) * s
    # へらす：UV の 継ぎ目で 分かれた 頂点は いっしょに たたむ（継ぎ目に すき間が できない）・ほんとうの ふちだけ 動かさない
    if KEEP:
        d = np.load(outp + '.npz'); V2, T2, UVc = d['V'], d['T'], d['UVc']
        print('形は 前の まま（', outp + '.npz', '）三角', len(T2), '頂点', len(V2), flush=True)
    else:
        UVTOL = float(os.environ.get('FIG_UVTOL', '1.0'))      # 島の ふちが 動いて よい はば（色の 絵の 点の 数）
        F2 = decimate2(L, V, F, TARGET, UV=UV, uvtol=UVTOL / CS) if len(F) > TARGET else F.astype(np.int32)
        used = np.unique(F2); remap = -np.ones(len(V), np.int64); remap[used] = np.arange(len(used))
        V2 = V[used].astype(np.float32); T2 = remap[F2].astype(np.int32); UVc = UV[used][T2].astype(np.float32)
        print('へらした 三角', len(F), '→', len(T2), '頂点', len(V2), flush=True)
    # 色・金属／あらさ の 絵（材質ごとの 絵 × 係数 を ならべる）
    def atlas(get, size, flat):
        A = np.zeros((size, size, 3), np.float32); tw, th = size // cols, size // rows
        for mi, mt in enumerate(mats):
            cx, cy = tile(mi); im = get(mt)
            t = np.broadcast_to(np.asarray(flat(mt), np.float32), (th, tw, 3)) if im is None else rs(im, max(tw, th))[:th, :tw]
            A[cy * th:(cy + 1) * th, cx * tw:(cx + 1) * tw] = t
        return A
    col = atlas(lambda mt: (mt.base_tex.tex.img[..., :3] * mt.base_color[:3]) if mt.base_tex is not None else None, CS, lambda mt: mt.base_color[:3])
    # 金属／あらさ・法線も いったん 色と 同じ 大きさ（CS）で 作って 直し、あとで 島を またがずに 小さく する（chart_down）
    mr = atlas(lambda mt: np.dstack([np.ones(mt.mr_tex.tex.img.shape[:2], np.float32), mt.mr_tex.tex.img[..., 1] * mt.roughness, mt.mr_tex.tex.img[..., 2] * mt.metallic]) if mt.mr_tex is not None else None, CS,
               lambda mt: (1.0, mt.roughness, mt.metallic))
    nmap = atlas(lambda mt: mt.normal_tex.tex.img[..., :3] if mt.normal_tex is not None else None, CS, lambda mt: (0.5, 0.5, 1.0))
    has_nmap = any(mt.normal_tex is not None for mt in mats)
    # 物の 向きの 法線：元の 細かい 三角を UV の 上に 塗る（法線・接線・向き）→ 法線マップを かける
    R, cov = uv_raster_v(L, UV, F, np.concatenate([N, T], 1), CS, CS)      # 頂点ごと（N 3・T 4）を 三角で まぜる
    n = R[..., :3]; t = R[..., 3:6]; w = np.where(R[..., 6:7] < 0, -1.0, 1.0)
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-9)
    if has_nmap:
        t = t - (t * n).sum(2, keepdims=True) * n; t /= np.maximum(np.linalg.norm(t, axis=2, keepdims=True), 1e-9)
        b = np.cross(n, t) * w; q = nmap * 2 - 1
        n2 = t * q[..., :1] + b * q[..., 1:2] + n * q[..., 2:3]; n = n2 / np.maximum(np.linalg.norm(n2, axis=2, keepdims=True), 1e-9)
    print('法線を 焼いた（塗れた 割合 %.2f）' % cov.mean(), flush=True)
    del R, t, nmap
    # へらした 三角が 島の 外に はみ出る ところは 3D で 元の 同じ 場所の 色・法線・金属／あらさ に（破片を 出さない）・のこりの すき間を うめる
    fixed, _, UVc = fix_maps(L, V, N, UV, F, V2, T2, UVc, {CS: [col, mr, n]}, log=lambda s: print(s, flush=True))
    col, mr, n = fixed[CS]
    # 金属／あらさ を 同じ 材料の 中で ならす（島ごとの 小さな ちがいが まだらに 見えない）→ 法線・金属／あらさ を 小さく（島を またいで まぜない）
    Ph, ch = mesh_pos(L, V2, T2, UVc, CS)
    mr = smooth_mr(mr, Ph, ch)
    for nm_, S in (('n', NS), ('m', MS)):
        if S == CS: continue
        Pl, cl = mesh_pos(L, V2, T2, UVc, S)
        if nm_ == 'n': n = chart_down(n, Ph, ch, Pl, cl)
        else: mr = chart_down(mr, Ph, ch, Pl, cl)
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-9)
    print('絵の 大きさ：色 %d・法線 %d・金属／あらさ %d' % (col.shape[0], n.shape[0], mr.shape[0]), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    np.savez_compressed(outp + '.npz', V=V2, T=T2, UVc=UVc)
    sv = lambda a, nm_: Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(outp + nm_, 'WEBP', lossless=True, method=4)
    sv(col, '_c.webp'); sv(n * 0.5 + 0.5, '_n.webp'); sv(mr, '_m.webp')
    print('できた', outp, flush=True)


if __name__ == '__main__':
    main()
