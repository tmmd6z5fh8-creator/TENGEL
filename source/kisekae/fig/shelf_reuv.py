# 3D の 棚の「絵の 貼り方」を 作り直す（第4.153版：まさちゃん「やって！」＝ きれいな まま 軽く）
#   python3 kisekae/fig/shelf_reuv.py <作業フォルダ（out/shelf.npz・out/shelf_align.json・out/shelf_c1〜7.webp・shelf/shelf_1〜7.png）> [出す フォルダ] [アプリ用を 置く フォルダ（ios/fig_assets）]
#   → <出す フォルダ>/shelf2.npz（V・T・UVc＝新しい 貼り方）・shelf2_c1〜7.webp（劣化なし・2048）・shelf2_info.json
#   → <アプリ用>/fg_shelf2.bin・fg_shelf2.json・fg_shelf2_c1〜7.webp（新しい 名前で 足す。もとの fg_shelf.* は そのまま 残す）
#
#   もと（shelf_proj.py）：3D を 作った AI の 貼り方（細かい 島が ばらばら）の 上に 写真を 焼いて いた
#     ・島の ふちで となりの 色が にじむので 劣化の ある 圧縮が 使えない（第4.151版：劣化なし 6bit で 7まい 8.89MB）
#     ・絵の 細かさは 写真の 半分 くらい（1mあたり 357点・写真は 646点）
#   作り直し：
#     ①「写真の カメラから ぜんぶ 見える 三角」は 1つの 大きな 島＝ **写真 そのもの の 並び**（頂点を 写真の カメラで 写した 場所）。つなぎ目 なし・写真と 同じ 細かさ
#     ② のこり（見えない 面・一部だけ 見える 面）は 面の 向き（±x・±y・±z）ごとに つながった かたまりを 平らに 写す。奥行きは 細かさを 落とす（色が 奥行きで かわらない）
#     ③ 色は shelf_proj.py と 同じ 決め方（見える 点＝写真・見えない 点＝きまり・のこり＝もとの 絵の 色）。島の まわりは 近くの 色で うめる
#        ＋ 見えない 点でも、かくして いる 物の すぐ うしろ なら 写真の その 場所の 色（ライトの まわりの 黒い 点を なくす：bake の 中の 説明）
#        ＋ 写真の すき通った 所（棚の 外）は 近くの 棚の 色で うめて から 読む（棚の 右と 左の ふちの 赤・白の すじを なくす）
#        ＋ 細すぎて 点が のらない 三角：見える なら 写真の 島へ・それ 以外は 重心の 点を もらう（うしろの かべの 短い 茶色の 線を なくす）
#     ④ アプリ用の 絵は 劣化あり（WebP quality 93）で よい：大きな 島の まわりは 同じ 色で うめて ある ので、ふちで ほかの 色が にじまない
#   はかった もの（第4.153版）：7まい 8.89MB → 2.83MB・形 362KB → 318KB（頂点 21816 → 17447）。写真の 島＝塗った 点の 65%（1065×1391）
#   まさちゃんの 棚の 写真・3D と それから 作った もの は リポジトリに 入れない（この スクリプトと reuv.c だけ）
import ctypes, hashlib, json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fig_prep import lib, uv_raster, fill

FLOOR = [1.585, 1.072, 0.572, 0.062]; CUB_H = 0.46; XC = 0.343; HALF = 0.322; FRONT = 0.244; EY = 1.075      # shelf_proj.py と 同じ
TS = 2048
KD = 0.25          # 奥行きの 細かさ（写真の 何倍か）
KB = 0.15          # うしろの 板
KS = 0.5           # 小さい かたまり
GUT = 6            # 島の まわりの あき（点）
A_BIG = 0.02       # これより 小さい かたまりは「小さい」
R_MIN = 0.02       # 写真の 島に 入れる：写真での 広さ ÷ 本当の 広さ が これ 以上
E_MAX = 1e9         # 写真の 島に 入れる：三角の 中の ずれ（点）の 上限（色は 点ごとに 本当の 場所で 焼くので ずれて いても 正しい → 上限 なし）
GAP = float(os.environ.get('SHELF_GAP', '0.04'))      # かくして いる 物の うしろ これ 以内（m）の 見えない 点は 写真の 色（大きな 面）
GAP_S = float(os.environ.get('SHELF_GAP_S', '0.2'))   # 同じ（小さい かたまり）
AX = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)


def clib():
    c = os.path.join(HERE, 'reuv.c'); h = hashlib.sha1(open(c, 'rb').read()).hexdigest()[:10]
    so = os.path.join(tempfile.gettempdir(), f'tengel_libreuv_{h}.so')
    if not os.path.exists(so):
        tmp = so + '.tmp'; subprocess.run(['gcc', '-O2', '-shared', '-fPIC', '-o', tmp, c, '-lm'], check=True); os.replace(tmp, so)
    R = ctypes.CDLL(so); P = ctypes.c_void_p; I = ctypes.c_int
    R.vis_count.argtypes = [I, P, P, I, I, P, ctypes.c_double, P, P]; R.idbuffer.argtypes = [I, P, P, I, I, P, P]; R.cover_count.argtypes = [I, P, I, I, P]
    return R


L = lib(); L.zbuffer.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
RL = clib()


def proj(p, cam, D):                    # → 写真の x・y（下向き）・深さ（shelf_proj.py と 同じ）
    f, cx, cy = cam; dz = D - p[..., 2]
    return np.stack([cx + f * p[..., 0] / dz, cy - f * (p[..., 1] - EY) / dz, dz], -1)


def load(work):
    O = os.path.join(work, 'out'); d = np.load(os.path.join(O, 'shelf.npz'))
    V = d['V'].astype(np.float64); T = np.ascontiguousarray(d['T'].astype(np.int32)); UVo = d['UVc'].astype(np.float64)
    al = json.load(open(os.path.join(O, 'shelf_align.json'))); n = len(al)
    cams = np.array([al[str(i)]['cam'] for i in range(1, n + 1)], float); D = float(al['1']['D'])
    photos = [os.path.join(work, 'shelf', al[str(i)]['photo']) for i in range(1, n + 1)]
    return O, V, T, UVo, cams, D, photos


def topo(V, T):                          # 同じ 場所の 頂点を 1つに・となりの 三角（辺を 分け合う 2つ）と その 辺の 長さ
    key = np.round(V * 1e5).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
    VW = np.zeros((inv.max() + 1, 3)); VW[inv] = V; W = inv[T]; nT = len(T)
    E = np.concatenate([W[:, [0, 1]], W[:, [1, 2]], W[:, [2, 0]]]); E.sort(1); tri = np.tile(np.arange(nT), 3)
    o = np.lexsort((E[:, 1], E[:, 0])); E = E[o]; tri = tri[o]; same = (E[1:] == E[:-1]).all(1)
    ea = tri[:-1][same]; eb = tri[1:][same]; el = np.linalg.norm(VW[E[:-1][same][:, 0]] - VW[E[:-1][same][:, 1]], axis=1)
    return W, ea, eb, el


def comps(nT, ea, eb, ok):               # ok（辺ごと）の つながりで かたまりに 分ける
    G = coo_matrix((np.ones(int(ok.sum())), (ea[ok], eb[ok])), shape=(nT, nT)); return connected_components(G, directed=False)[1]


def charts(work, out, log=print):
    O, V, T, UVo, cams, D, photos = load(work); nT = len(T)
    P = V[T]; fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); ar = np.linalg.norm(fn, axis=1) / 2; fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    W, ea, eb, el = topo(V, T)
    ref = cams.mean(0); s0 = ref[0] / (D - FRONT)                 # いちばん 前の 面での 写真の 細かさ（1mあたりの 点）
    # ── 写真の カメラから 見えるか（写真の 3倍の 細かさ）
    K = 3; im0 = Image.open(photos[0]); PW, PH = im0.size
    S = np.ascontiguousarray(proj(V, ref * K, D)); zb = np.full((PH * K, PW * K), 1e9, np.float32); L.zbuffer(nT, S.ctypes.data, T.ctypes.data, PW * K, PH * K, zb.ctypes.data)
    tot = np.zeros(nT, np.int32); vis = np.zeros(nT, np.int32); RL.vis_count(nT, S.ctypes.data, T.ctypes.data, PW * K, PH * K, zb.ctypes.data, 0.004, tot.ctypes.data, vis.ctypes.data)
    eye = np.array([0, EY, D]); cen = P.mean(1); facing = ((eye - cen) * fn).sum(1) > 0
    q = proj(P, ref, D)[..., :2]                                  # 角の 写真での 場所（nT×3×2）
    pa = np.abs((q[:, 1, 0] - q[:, 0, 0]) * (q[:, 2, 1] - q[:, 0, 1]) - (q[:, 2, 0] - q[:, 0, 0]) * (q[:, 1, 1] - q[:, 0, 1])) / 2
    ratio = pa / np.maximum(ar * s0 * s0, 1e-12)
    err = np.zeros(nT)                                             # 三角の 中の ずれ：辺の まん中・重心で「本当に 写した 場所」と「角を まぜた 場所」の ちがい
    for a, b in ((0, 1), (1, 2), (2, 0)): err = np.maximum(err, np.linalg.norm(proj((P[:, a] + P[:, b]) / 2, ref, D)[:, :2] - (q[:, a] + q[:, b]) / 2, axis=1))
    err = np.maximum(err, np.linalg.norm(proj(cen, ref, D)[:, :2] - q.mean(1), axis=1))
    full = facing & (tot > 0) & (vis == tot)
    # 細すぎて 点が 1つも のらない 三角（すき間を うめる 針の ような 三角）：角 3つと 重心が 見える なら「見える」あつかい（まわりと 同じ 写真の 色に なる）
    zm = ndimage.maximum_filter(zb, 3); Sc = proj(cen, ref * K, D)
    def seen(q_):
        xi = np.clip(np.floor(q_[..., 0]).astype(int), 0, PW * K - 1); yi = np.clip(np.floor(q_[..., 1]).astype(int), 0, PH * K - 1)
        return (q_[..., 0] >= 0) & (q_[..., 0] < PW * K) & (q_[..., 1] >= 0) & (q_[..., 1] < PH * K) & (q_[..., 2] <= zm[yi, xi] + 0.004)
    thin = facing & (tot == 0) & seen(S[T]).all(1) & seen(Sc); full |= thin
    photo = full & (ratio >= R_MIN) & (err <= E_MAX)
    log(f'見える 三角 {int(full.sum())}（広さ {ar[full].sum():.3f}・うち 針の ような 三角 {int(thin.sum())}）→ 写真の 島 {int(photo.sum())}（{ar[photo].sum():.3f}・ななめすぎて はずす {int((full & (ratio < R_MIN)).sum())}）／ぜんぶ {nT}（{ar.sum():.3f}）')
    # ── のこり：面の 向き ごとに つながった かたまり。小さい かたまりは となりの 大きい かたまりへ（うら返らない とき だけ）
    ax = np.argmax(np.abs(fn), 1); cls = ax * 2 + (fn[np.arange(nT), ax] < 0); rem = ~photo
    for it in range(20):
        lab = comps(nT, ea, eb, (cls[ea] == cls[eb]) & rem[ea] & rem[eb]); A = np.bincount(lab, weights=ar, minlength=lab.max() + 1)
        m = rem[ea] & rem[eb] & (lab[ea] != lab[eb]); x = np.concatenate([ea[m], eb[m]]); y = np.concatenate([eb[m], ea[m]]); l = np.concatenate([el[m], el[m]])
        k = A[lab[x]] < A_BIG; x, y, l = x[k], y[k], l[k]; nb = {}
        for xi, yi, li in zip(lab[x].tolist(), y.tolist(), l.tolist()):
            dd = nb.setdefault(xi, {}); kk = (int(lab[yi]), int(cls[yi])); dd[kk] = dd.get(kk, 0.0) + li
        moved = 0
        for c, dd in nb.items():
            tris = np.nonzero(lab == c)[0]
            for (c2, k2), ln in sorted(dd.items(), key=lambda t: -t[1]):
                if A[c2] > A[c] and (fn[tris] @ AX[k2]).min() >= 0.3: cls[tris] = k2; moved += 1; break
        if not moved: break
    lab = comps(nT, ea, eb, (cls[ea] == cls[eb]) & rem[ea] & rem[eb]); A = np.bincount(lab, weights=ar, minlength=lab.max() + 1)
    ids = np.unique(lab[rem]); log(f'のこりの かたまり {len(ids)}（大きい {int((A[ids] >= A_BIG).sum())}・小さい {int((A[ids] < A_BIG).sum())}＝広さ {A[ids][A[ids] < A_BIG].sum():.3f}）')
    # ── 島ごとの 平らな 場所（点の 単位）
    UV = np.zeros((nT, 3, 2)); chart = np.full(nT, -1); rects = []       # rects：[島の 番号, 幅, 高さ]
    UV[photo] = q[photo]; chart[photo] = 0
    lo = UV[photo].reshape(-1, 2).min(0); UV[photo] -= lo; hi = UV[photo].reshape(-1, 2).max(0); rects.append([0, hi[0], hi[1]])
    order = ids[np.argsort(-A[ids])]
    for n_, c in enumerate(order, 1):
        tr = np.nonzero(lab == c)[0]; k = int(cls[tr[0]]); a = k // 2; big = A[c] >= A_BIG; p = P[tr]
        if a == 0: uv = np.stack([p[..., 2] * (KD if big else KS), -p[..., 1] * (1 if big else KS)], -1)
        elif a == 1: uv = np.stack([p[..., 0] * (1 if big else KS), p[..., 2] * (KD if big else KS)], -1)
        else: kk = (KB if k == 5 else 1) * (1 if big else KS); uv = np.stack([p[..., 0] * kk, -p[..., 1] * kk], -1)
        uv = uv * s0; uv -= uv.reshape(-1, 2).min(0); UV[tr] = uv; chart[tr] = n_; hi = uv.reshape(-1, 2).max(0); rects.append([n_, hi[0], hi[1]])
    # ── 同じ 島の 中で 三角が 重なって いないか（重なった 所が 多い 島は 知らせる）
    over = []
    for n_, w, h in rects[1:]:
        tr = np.nonzero(chart == n_)[0]; Wc, Hc = int(np.ceil(w)) + 2, int(np.ceil(h)) + 2; cnt = np.zeros((Hc, Wc), np.uint8)
        u = np.ascontiguousarray(UV[tr] + 0.5); RL.cover_count(len(tr), u.ctypes.data, Wc, Hc, cnt.ctypes.data)
        if (cnt > 1).sum() > max(2, 0.01 * (cnt > 0).sum()): over.append((n_, int((cnt > 1).sum()), int((cnt > 0).sum())))
    log(f'中で 重なる 島 {len(over)}：{over[:12]}')
    small = rem & (A[lab] < A_BIG)
    np.savez(os.path.join(out, 'shelf2_charts.npz'), UV=UV, chart=chart, rects=np.array(rects), photo=photo, cls=cls, s0=s0, ref=ref, small=small)
    return UV, chart, rects, photo, over, small


def pack(UV, chart, rects, log=print):   # 島を 2048² に 並べる：写真の 島を 左上・のこりは 大きい 順に あいて いる 所へ（4点 きざみ）
    C = 4; G = TS // C; occ = np.zeros((G, G), bool); pos = {}
    def cells(w, h): return int(np.ceil((w + 2 * GUT) / C)), int(np.ceil((h + 2 * GUT) / C))
    def put(n_, w, h, at=None):
        cw, ch = cells(w, h)
        if at is None:
            I = np.zeros((G + 1, G + 1), np.int32); I[1:, 1:] = occ.cumsum(0).cumsum(1)
            if cw > G or ch > G: raise SystemExit(f'島 {n_} が 大きすぎる（{w:.0f}×{h:.0f}）')
            free = (I[ch:, cw:] - I[:-ch, cw:] - I[ch:, :-cw] + I[:-ch, :-cw]) == 0
            ys, xs = np.nonzero(free)
            if not len(ys): raise SystemExit(f'島 {n_}（{w:.0f}×{h:.0f}）を 置く 場所が ない')
            j = np.lexsort((ys, xs)) [0] if h > w else np.lexsort((xs, ys))[0]; at = (int(xs[j]), int(ys[j]))     # たて長は 左から・よこ長は 上から つめる
        occ[at[1]:at[1] + ch, at[0]:at[0] + cw] = True; pos[n_] = (at[0] * C + GUT, at[1] * C + GUT)
    put(0, rects[0][1], rects[0][2], (0, 0))
    for n_, w, h in sorted(rects[1:], key=lambda r: -max(r[1], r[2])): put(int(n_), w, h)
    out = UV.copy()
    for n_, (ox, oy) in pos.items(): out[chart == n_] += (ox, oy)
    log(f'並べた 島 {len(pos)}・使った 広さ {occ.mean() * 100:.1f}%')
    return out / TS, occ


def bake(work, out, UVn, photo, small, log=print):      # 新しい 貼り方の 上に 7色を 焼く（色の 決め方は shelf_proj.py と 同じ）
    O, V, T, UVo, cams, D, photos = load(work); nT = len(T)
    P = V[T]; fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    A = np.concatenate([P, np.repeat(fn[:, None], 3, 1), UVo, np.repeat(photo[:, None, None].astype(np.float64), 3, 1), np.repeat(small[:, None, None].astype(np.float64), 3, 1), np.repeat(np.arange(nT, dtype=np.float64)[:, None, None], 3, 1)], 2)       # 角ごと：場所 3・向き 3・もとの UV 2・写真の 島か 1・小さい 島か 1・三角の 番号 1
    R, cov = uv_raster(L, UVn.reshape(-1, 2), np.arange(nT * 3, dtype=np.int32).reshape(-1, 3), A, TS, TS)
    R = R.reshape(-1, 11); cov = cov.reshape(-1)
    # 細すぎて 絵の 点が 1つも のらない 三角は、まわりの あき（ほかの 島の 色で うまる）の 色に なって しまう → 重心の 所の 点を その 三角の ものに する（あいて いる とき だけ）
    got = np.zeros(nT, bool); got[np.rint(R[cov, 10]).astype(int)] = True; miss = np.nonzero(~got)[0]; uc = UVn[miss].mean(1)
    tx = np.clip(np.floor(uc[:, 0] * TS).astype(int), 0, TS - 1) + TS * np.clip(np.floor(uc[:, 1] * TS).astype(int), 0, TS - 1); n_fix = 0
    for t, o in zip(miss.tolist(), tx.tolist()):
        if not cov[o]: R[o] = A[t].mean(0); cov[o] = True; n_fix += 1
    log(f'絵の 点が 1つも のらない 三角 {len(miss)}（うち 重心の 点を もらった {n_fix}）')
    ci = np.nonzero(cov)[0]
    pos = R[ci, :3].astype(np.float64); nrm = R[ci, 3:6].astype(np.float64); nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9); uvo = R[ci, 6:8].astype(np.float64); isph = R[ci, 8] > 0.5; issm = R[ci, 9] > 0.5
    eye = np.array([0, EY, D]); n = len(ci); info = {}
    ff = np.ascontiguousarray(T[((eye - P.mean(1)) * fn).sum(1) > 0])            # カメラの 方を 向いた 三角 だけ（かくして いる 物の 深さ 用）
    px, py, pz = pos[:, 0], pos[:, 1], pos[:, 2]; nx, ny, nz = nrm[:, 0], nrm[:, 1], nrm[:, 2]
    xc = np.where(px < 0, -XC, XC); inx = np.abs(px - xc) < HALF + 0.01; row = np.full(n, -1)
    for r, f0 in enumerate(FLOOR): row[(py >= f0 - 0.012) & (py <= f0 + CUB_H + 0.012) & inx & (pz < FRONT - 0.005)] = r
    cub = row >= 0; fl0 = np.array(FLOOR)[np.maximum(row, 0)]; fz = np.full(n, FRONT + 0.002); n_f = np.tile([0, 0, 1.0], (n, 1))
    for k, ph in enumerate(photos, 1):
        im = Image.open(ph); W, H = im.size; cam = cams[k - 1]; a4 = np.asarray(im.convert('RGBA')); A_ = a4[..., :3].astype(np.float32) / 255
        # 写真の すき通った 所（棚の 外）の 色は でたらめ（赤・白・黒の 点）→ いちばん 近い 棚の 色で うめて から 読む（棚の ふちに でたらめな 色の すじが 出ない）
        fg = a4[..., 3] >= 128
        if not fg.all(): A_ = A_[tuple(ndimage.distance_transform_edt(~fg, return_indices=True)[1])]
        S = np.ascontiguousarray(proj(V, cam, D), np.float64); zb = np.full((H, W), 1e9, np.float32); L.zbuffer(nT, S.ctypes.data, T.ctypes.data, W, H, zb.ctypes.data)
        zf = np.full((H, W), 1e9, np.float32); L.zbuffer(len(ff), S.ctypes.data, ff.ctypes.data, W, H, zf.ctypes.data)
        def look(p, nn):                 # 見えるか・色（shelf_proj.py の look と 同じ）
            s = proj(p, cam, D); x, y, dz = s[:, 0], s[:, 1], s[:, 2]
            ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (((eye - p) * nn).sum(1) > 0)
            xi = np.clip(x.astype(int), 0, W - 1); yi = np.clip(y.astype(int), 0, H - 1); ok &= dz <= zb[yi, xi] + 0.015
            x0 = np.clip(np.floor(x).astype(int), 0, W - 2); y0 = np.clip(np.floor(y).astype(int), 0, H - 2); fx = np.clip(x - x0, 0, 1)[:, None]; fy = np.clip(y - y0, 0, 1)[:, None]
            c = (A_[y0, x0] * (1 - fx) + A_[y0, x0 + 1] * fx) * (1 - fy) + (A_[y0 + 1, x0] * (1 - fx) + A_[y0 + 1, x0 + 1] * fx) * fy
            return ok, c
        col = np.zeros((n, 3), np.float32); done = np.zeros(n, bool)
        # 写真の 島：写真を そのまま（ほぼ 1対1 なので なめらかな 曲線で 読む＝ぼけない）
        i = np.nonzero(isph)[0]; s = proj(pos[i], cam, D)
        for c in range(3): col[i, c] = ndimage.map_coordinates(A_[..., c], [s[:, 1], s[:, 0]], order=3, mode='nearest')
        done[i] = True; n_ph = len(i)
        # のこり：見える 点＝写真・見えない 点＝きまり（床＝下の 板の 正面・天井＝上の 板の 正面・横の かべ＝柱の 正面・外＝外わくの 正面）
        ok, c = look(pos, nrm); ok &= ~isph; col[ok] = c[ok]; done |= ok; n_vis = int(ok.sum())
        # 見えない 点でも、かくして いる 物（カメラの 方を 向いた 面）の すぐ うしろ なら 写真の その 場所の 色（＝かくして いる 物の 色）。
        #   アプリの カメラは 写真の カメラより 遠いので、写真から 見えない 点が 少し だけ 見える。そこに きまりの 色（木の 色）が 出ると ライトの まわりに 黒い 点が 出る
        #   大きな 面（床・かべ・天井）は うしろ GAP（4cm）まで・小さい かたまり（ライトの 部品 など）は 前後 GAP_S（20cm）まで。それより 奥は きまりの 色
        i = np.nonzero(~done)[0]; s = proj(pos[i], cam, D); x, y, dz = s[:, 0], s[:, 1], s[:, 2]
        xi = np.clip(np.rint(x).astype(int), 0, W - 1); yi = np.clip(np.rint(y).astype(int), 0, H - 1); g = dz - zf[yi, xi]
        near = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (zf[yi, xi] < 1e8) & (g >= np.where(issm[i], -GAP_S, -0.004)) & (g <= np.where(issm[i], GAP_S, GAP))
        i = i[near]; x, y = x[near], y[near]; x0 = np.clip(np.floor(x).astype(int), 0, W - 2); y0 = np.clip(np.floor(y).astype(int), 0, H - 2); fx = np.clip(x - x0, 0, 1)[:, None]; fy = np.clip(y - y0, 0, 1)[:, None]
        col[i] = (A_[y0, x0] * (1 - fx) + A_[y0, x0 + 1] * fx) * (1 - fy) + (A_[y0 + 1, x0] * (1 - fx) + A_[y0 + 1, x0 + 1] * fx) * fy; done[i] = True; n_gap = len(i)
        def tryp(sel, p2):
            idx = np.nonzero(sel & ~done)[0]
            if not len(idx): return
            ok2, c2 = look(p2[idx], n_f[idx]); col[idx[ok2]] = c2[ok2]; done[idx[ok2]] = True
        d0 = int(done.sum())
        tryp(cub & (ny > 0.6), np.stack([px, fl0 - 0.026, fz], 1))
        tryp(cub & (ny < -0.6), np.stack([px, fl0 + CUB_H + 0.026, fz], 1))
        wx = np.where(np.abs(px) < 0.2, 0.0, np.sign(px) * 0.745)
        tryp(cub & (np.abs(nx) > 0.6), np.stack([wx, py, fz], 1))
        tryp(~cub & (np.abs(nx) > 0.6), np.stack([np.sign(px) * 0.745, np.clip(py, 0.02, 2.13), fz], 1))
        tryp(~cub & (ny > 0.6), np.stack([np.clip(px, -0.79, 0.79), np.full(n, 2.10), fz], 1))
        tryp(~cub & (ny < -0.6), np.stack([np.clip(px, -0.79, 0.79), np.full(n, 0.03), fz], 1))
        tryp(~cub & (nz < -0.6), np.stack([np.sign(px) * 0.745, np.clip(py, 0.02, 2.13), fz], 1))
        n_rule = int(done.sum()) - d0
        # それでも 決まらない 点：もとの 絵（もとの 貼り方）の 同じ 場所の 色
        i = np.nonzero(~done)[0]; old = np.asarray(Image.open(os.path.join(O, f'shelf_c{k}.webp')).convert('RGB'), np.float32) / 255; OS = old.shape[0]
        x = np.clip(uvo[i, 0] * OS - 0.5, 0, OS - 1); y = np.clip(uvo[i, 1] * OS - 0.5, 0, OS - 1)
        x0 = np.clip(np.floor(x).astype(int), 0, OS - 2); y0 = np.clip(np.floor(y).astype(int), 0, OS - 2); fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
        col[i] = (old[y0, x0] * (1 - fx) + old[y0, x0 + 1] * fx) * (1 - fy) + (old[y0 + 1, x0] * (1 - fx) + old[y0 + 1, x0 + 1] * fx) * fy
        img = np.zeros((TS * TS, 3), np.float32); img[ci] = np.clip(col, 0, 1); img = fill(img.reshape(TS, TS, 3), cov.reshape(TS, TS))
        Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(os.path.join(out, f'shelf2_c{k}.webp'), 'WEBP', lossless=True, method=4)
        info[str(k)] = {'photo': n_ph, 'seen': n_vis, 'gap': n_gap, 'rule': n_rule, 'old': int(len(i)), 'all': int(n)}
        log(f'{k}：写真の 島 {n_ph / n * 100:.1f}%・見える 点 {n_vis / n * 100:.1f}%・すぐ うしろ {n_gap / n * 100:.1f}%・きまり {n_rule / n * 100:.1f}%・もとの 絵から {len(i) / n * 100:.1f}%（塗った 点 {n}＝絵の {n / TS / TS * 100:.1f}%）')
    return info


def assets(out, dst, q=93, log=print):       # アプリに 入れる 形：fg_shelf2.bin／.json（fig_render.js の mesh と 同じ 形式）・fg_shelf2_c1〜7.webp（劣化あり quality q）
    d = np.load(os.path.join(out, 'shelf2.npz')); V = d['V'].astype(np.float64); T = d['T'].astype(np.int64); UVc = d['UVc'].astype(np.float64)
    key = np.round(V * 1e5).astype(np.int64); _, wid = np.unique(key, axis=0, return_inverse=True); wid = wid.reshape(-1)      # 同じ 場所の 頂点は 1つに（貼り方が 同じ なら 分け合う）
    cv = T.reshape(-1); cu = UVc.reshape(-1, 2); qu = np.round(np.clip(cu, 0, 1) * 65535).astype(np.int64)
    k2 = wid[cv] * (65536 * 65536) + qu[:, 0] * 65536 + qu[:, 1]
    _, first, inv = np.unique(k2, return_index=True, return_inverse=True)
    P = V[cv[first]]; UV = qu[first]; I = inv.reshape(-1).astype(np.uint32); assert len(P) <= 65535, len(P)
    lo, hi = V.min(0), V.max(0); sc = np.maximum(hi - lo, 1e-9); qp = np.round((P - lo) / sc * 65535).astype(np.uint16)
    parts = (('pos', qp.tobytes()), ('uv', UV.astype(np.uint16).tobytes()), ('idx', I.astype(np.uint16).tobytes())); lay = {}; buf = b''
    for k, b in parts:
        while len(buf) % 4: buf += b'\0'
        lay[k] = [len(buf), len(b)]; buf += b
    names = [f'fg_shelf2_c{c}.webp' for c in range(1, 8)]
    fr = UVc[d['photo']].reshape(-1, 2) * TS; front = [round(float(x), 2) for x in (fr[:, 0].min(), fr[:, 1].min(), fr[:, 0].max(), fr[:, 1].max())]      # 写真の 島の 場所（点：左・上・右・下）＝正面から 見た 棚 そのもの（テストが 画面と くらべる）
    meta = {'v': int(len(P)), 'i': int(len(I)), 'idx32': False, 'layout': lay, 'qo': lo.round(6).tolist(), 'qs': sc.round(6).tolist(), 'bbox': [lo.round(4).tolist(), hi.round(4).tolist()], 'tex': names, 'front': front}
    # 確かめ：読み直して、三角ごとの 場所と 貼り方が もとと 同じ（きざみの 分 だけ ちがう）
    p2 = np.frombuffer(buf, np.uint16, meta['v'] * 3, lay['pos'][0]).reshape(-1, 3) / 65535 * np.array(meta['qs']) + np.array(meta['qo']); u2 = np.frombuffer(buf, np.uint16, meta['v'] * 2, lay['uv'][0]).reshape(-1, 2) / 65535
    i2 = np.frombuffer(buf, np.uint16, meta['i'], lay['idx'][0]).astype(np.int64)
    assert np.abs(p2[i2] - V[cv]).max() < 2e-5 * float(sc.max()) + 1e-6 and np.abs(u2[i2] - cu).max() <= 0.5 / 65535 + 1e-9
    os.makedirs(dst, exist_ok=True); open(os.path.join(dst, 'fg_shelf2.bin'), 'wb').write(buf); json.dump(meta, open(os.path.join(dst, 'fg_shelf2.json'), 'w'))
    tot = len(buf)
    for c, nm in enumerate(names, 1):
        im = Image.open(os.path.join(out, f'shelf2_c{c}.webp')).convert('RGB'); assert im.size == (TS, TS)
        im.save(os.path.join(dst, nm), 'WEBP', quality=q, method=6); tot += os.path.getsize(os.path.join(dst, nm))
    log(f'アプリ用：頂点 {meta["v"]}・三角 {meta["i"] // 3}・形 {len(buf) / 1e3:.0f}KB・絵 7まい（quality {q}）と 合わせて {tot / 1e6:.2f}MB → {dst}')
    return meta, tot


if __name__ == '__main__':
    work = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(work, 'out'); os.makedirs(out, exist_ok=True)
    UV, chart, rects, photo, over, small = charts(work, out)
    UVn, occ = pack(UV, chart, rects)
    O, V, T, UVo, cams, D, photos = load(work)
    assert UVn.min() >= 0 and UVn.max() <= 1
    np.savez(os.path.join(out, 'shelf2.npz'), V=V, T=T, UVc=UVn, chart=chart, photo=photo)
    Image.fromarray((occ * 255).astype(np.uint8)).resize((512, 512), Image.NEAREST).save(os.path.join(out, 'shelf2_occ.png'))
    info = bake(work, out, UVn, photo, small)
    json.dump({'charts': int(chart.max() + 1), 'photo_tris': int(photo.sum()), 'overlap': over, 'bake': info, 'TS': TS}, open(os.path.join(out, 'shelf2_info.json'), 'w'), indent=1, default=lambda o: int(o))
    if len(sys.argv) > 3: assets(out, sys.argv[3])
