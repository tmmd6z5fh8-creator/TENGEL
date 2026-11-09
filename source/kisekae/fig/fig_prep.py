# 思い出フィギュアの 形を へらして、アプリ用の 絵（色・物の 向きの 法線・金属／あらさ）を 作る（11/09 21:10 に 作業場所が 消えた あとに 作り直した 版）
#   python3 kisekae/fig/fig_prep.py <まさちゃんの GLB> <出す 名前（…/out/fig1）> [三角の 数 90000] [色 2048] [法線 1024] [金属 512]
#   → <名前>.npz（V：高さ 2.15・y 0〜・x／z まん中・T・UVc＝三角の 角ごとの UV）・<名前>_c.webp・_n.webp・_m.webp（どれも 劣化なしの WebP）
#   ・形：QEM で へらす。UV の 継ぎ目・ふちの 頂点は 動かさない → 元の UV と 絵を そのまま 使える（絵の 焼き直しが いらない）
#   ・法線：元の 細かい 形（と 法線マップ）を UV の 上に 塗って「物の 向き」の 法線の 絵に する → へらした 形でも 細かい でこぼこが 見える
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
    so = os.path.join(tempfile.gettempdir(), 'tengel_libqem.so'); c = os.path.join(HERE, 'qem.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(c):
        subprocess.run(['gcc', '-O2', '-shared', '-fPIC', '-o', so, c, '-lm'], check=True)
    L = ctypes.CDLL(so)
    L.qem_decimate.restype = ctypes.c_int
    L.qem_decimate.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_void_p]
    L.uv_raster.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
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


def fill(img, cov):            # 塗れなかった ところ（すき間）を いちばん 近い 塗れた 色で うめる（ミップマップで ふちが にじまない）
    if cov.all(): return img
    _, (iy, ix) = ndimage.distance_transform_edt(~cov, return_indices=True)
    return img[iy, ix]


def rs(img, size):            # float の 絵（H×W×C・0〜1）→ size×size
    im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)[..., :3])
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255


def main():
    src, outp = sys.argv[1], sys.argv[2]
    TARGET = int(sys.argv[3]) if len(sys.argv) > 3 else 90000
    CS = int(sys.argv[4]) if len(sys.argv) > 4 else 2048; NS = int(sys.argv[5]) if len(sys.argv) > 5 else 1024; MS = int(sys.argv[6]) if len(sys.argv) > 6 else 512
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
        F.append(np.asarray(p.idx, np.int64).reshape(-1, 3) + base); base += len(p.pos)
    V = np.concatenate(V); N = np.concatenate(N); UV = np.concatenate(UV); T = np.concatenate(T); F = np.concatenate(F)
    # 高さ 2.15・地面 y=0・x／z まん中（向きは そのまま：fig_bake.py の PROP と 同じ）
    lo, hi = V.min(0), V.max(0); s = 2.15 / (hi[1] - lo[1]); off = np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
    V = (V - off) * s
    # ふち（三角 1つだけの 辺）の 頂点は 動かさない（UV の 継ぎ目も ここに 入る）
    E = np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1)
    ue, cnt = np.unique(E, axis=0, return_counts=True); lock = np.zeros(len(V), np.uint8); lock[ue[cnt == 1].ravel()] = 1
    print('うごかさない 頂点', int(lock.sum()), '/', len(V), flush=True)
    F2 = decimate(L, V, F, lock, TARGET) if len(F) > TARGET else F.astype(np.int32)
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
    mr = atlas(lambda mt: np.dstack([np.ones(mt.mr_tex.tex.img.shape[:2], np.float32), mt.mr_tex.tex.img[..., 1] * mt.roughness, mt.mr_tex.tex.img[..., 2] * mt.metallic]) if mt.mr_tex is not None else None, MS,
               lambda mt: (1.0, mt.roughness, mt.metallic))
    nmap = atlas(lambda mt: mt.normal_tex.tex.img[..., :3] if mt.normal_tex is not None else None, NS, lambda mt: (0.5, 0.5, 1.0))
    has_nmap = any(mt.normal_tex is not None for mt in mats)
    # 物の 向きの 法線：元の 細かい 三角を UV の 上に 塗る（法線・接線・向き）→ 法線マップを かける
    A = np.concatenate([N[F], T[F]], 2)                     # 三角×角×（N 3・T 4）
    R, cov = uv_raster(L, UV, F.astype(np.int32), A, NS, NS)
    n = R[..., :3]; t = R[..., 3:6]; w = np.where(R[..., 6:7] < 0, -1.0, 1.0)
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-9)
    if has_nmap:
        t = t - (t * n).sum(2, keepdims=True) * n; t /= np.maximum(np.linalg.norm(t, axis=2, keepdims=True), 1e-9)
        b = np.cross(n, t) * w; q = nmap * 2 - 1
        n2 = t * q[..., :1] + b * q[..., 1:2] + n * q[..., 2:3]; n = n2 / np.maximum(np.linalg.norm(n2, axis=2, keepdims=True), 1e-9)
    n = fill(n, cov)
    print('法線を 焼いた（塗れた 割合 %.2f）' % cov.mean(), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    np.savez_compressed(outp + '.npz', V=V2, T=T2, UVc=UVc)
    sv = lambda a, nm_: Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(outp + nm_, 'WEBP', lossless=True, method=4)
    sv(col, '_c.webp'); sv(n * 0.5 + 0.5, '_n.webp'); sv(mr, '_m.webp')
    print('できた', outp, flush=True)


if __name__ == '__main__':
    main()
