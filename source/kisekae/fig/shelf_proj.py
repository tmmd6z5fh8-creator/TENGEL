# 3D の 棚（まさちゃんの 棚の GLB → fig_prep.py で へらした 形）に、色ちがいの 正面の 写真（7まい）を はる（11/09 21:10 の あとに 作り直した 版）
#   python3 kisekae/fig/shelf_proj.py <out/shelf（.npz）> <写真1> <写真2> ... → out/shelf_c1.webp …（棚の UV の 絵・2048）・out/shelf_align.json（合わせた カメラ）
#   ・カメラ：正面・高さ まん中（y 1.075）・きょり 8（fov 17 度 くらいの 遠近）。写真の 棚の 形（背景との ちがい）に 大きさ・位置を 合わせる
#   ・見える 面：写真の 色。見えない 面：箱の 横の かべ＝反対がわの かべを 鏡に・床＝いちばん 下の 段の 床・天井＝いちばん 上の 段の 天井・
#     外がわ（横・上・下）＝正面の ふちの 色・のこり＝近くの 色
#   ・まさちゃんの 棚の 写真と それから 作った もの は リポジトリに 入れない（この スクリプトだけ）
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_prep import lib, uv_raster, fill
L = lib()
import ctypes
L.zbuffer.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
FLOOR = [1.585, 1.072, 0.572, 0.062]; CUB_H = 0.46; XC = 0.343; HALF = 0.322; FRONT = 0.244; EY = 1.075
D = float(os.environ.get('SHELF_D', '40'))     # 写真の カメラの 遠さ（写真は ほぼ 真正面・遠近 少し：大きいほど 平ら）
base = sys.argv[1]; photos = sys.argv[2:]; TS = 2048
d = np.load(base + '.npz'); V = d['V'].astype(np.float64); T = d['T'].astype(np.int32); UVc = d['UVc'].astype(np.float64)
P = V[T]; fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
# 絵の 1まい ごとの 位置と 向き（UV の 上に 三角を 塗る）
A = np.concatenate([P, np.repeat(fn[:, None], 3, 1)], 2)
R, cov = uv_raster(L, UVc.reshape(-1, 2), np.arange(len(T) * 3, dtype=np.int32).reshape(-1, 3), A, TS, TS)
pos = R[..., :3].reshape(-1, 3).astype(np.float64); nrm = R[..., 3:6].reshape(-1, 3).astype(np.float64); cov = cov.reshape(-1)
nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)


def proj(p, cam):                       # → 画面の x・y（下向き）・深さ
    f, cx, cy = cam; dz = D - p[..., 2]
    return np.stack([cx + f * p[..., 0] / dz, cy - f * (p[..., 1] - EY) / dz, dz], -1)


def zbuf(cam, W, H):
    S = np.ascontiguousarray(proj(V, cam), np.float64); zb = np.full((H, W), 1e9, np.float32)
    L.zbuffer(len(T), S.ctypes.data, np.ascontiguousarray(T).ctypes.data, W, H, zb.ctypes.data); return zb


def fgmask(img):                        # 写真の 棚（背景との ちがい）
    a = np.asarray(img.convert('RGBA'), np.float32); rgb, al = a[..., :3], a[..., 3]
    if al.min() < 250: return al > 128
    b = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]); bg = np.median(b, 0)
    return np.linalg.norm(rgb - bg, axis=2) > 38


def align(img):
    m = fgmask(img); H, W = m.shape; ys, xs = np.nonzero(m)
    pu0, pu1, pv0, pv1 = np.percentile(xs, 0.5), np.percentile(xs, 99.5), np.percentile(ys, 0.5), np.percentile(ys, 99.5)
    q = proj(V, (1.0, 0.0, 0.0)); u0, u1, v0, v1 = q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max()
    f = (pv1 - pv0) / (v1 - v0); cam = [f, (pu0 + pu1) / 2 - f * (u0 + u1) / 2, (pv0 + pv1) / 2 - f * (v0 + v1) / 2]
    k = 4; ms = m[::k, ::k]; Hs, Ws = ms.shape
    def iou(c):
        zb = zbuf((c[0] / k, c[1] / k, c[2] / k), Ws, Hs) < 1e8; return (zb & ms).sum() / max(1, (zb | ms).sum())
    best = (iou(cam), cam)
    for step in (0.02, 0.008, 0.003):
        for _ in range(3):
            for i, dl in ((0, best[1][0] * step), (1, W * step), (2, H * step)):
                for sg in (-1, 1):
                    c = list(best[1]); c[i] += sg * dl; s = iou(c)
                    if s > best[0]: best = (s, c)
    return best[1], best[0], m


def colors(img, cam):
    H, W = img.size[1], img.size[0]; zb = zbuf(cam, W, H); A_ = np.asarray(img.convert('RGB'), np.float32) / 255
    eye = np.array([0, EY, D])
    def look(p, n):                     # 見えるか・色
        s = proj(p, cam); x, y, dz = s[:, 0], s[:, 1], s[:, 2]
        ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (((eye - p) * n).sum(1) > 0)
        xi = np.clip(x.astype(int), 0, W - 1); yi = np.clip(y.astype(int), 0, H - 1)
        ok &= dz <= zb[yi, xi] + 0.015
        x0 = np.clip(np.floor(x).astype(int), 0, W - 2); y0 = np.clip(np.floor(y).astype(int), 0, H - 2); fx = np.clip(x - x0, 0, 1)[:, None]; fy = np.clip(y - y0, 0, 1)[:, None]
        c = (A_[y0, x0] * (1 - fx) + A_[y0, x0 + 1] * fx) * (1 - fy) + (A_[y0 + 1, x0] * (1 - fx) + A_[y0 + 1, x0 + 1] * fx) * fy
        return ok, c
    out = np.zeros((len(pos), 3), np.float32); done = np.zeros(len(pos), bool)
    ok, c = look(pos, nrm); ok &= cov; out[ok] = c[ok]; done |= ok
    # 見えない 面（写真は ほぼ 真正面なので 箱の 床・天井・横の かべ・棚の 外がわは 写って いない）→ 同じ 材料の 正面の ふちの 色を 使う
    #   床＝その 下の 板の 正面・天井＝上の 板の 正面・横の かべ＝その かべの 柱の 正面・外の 横／上／下＝外わくの 正面
    px, py, pz = pos[:, 0], pos[:, 1], pos[:, 2]; nx, ny, nz = nrm[:, 0], nrm[:, 1], nrm[:, 2]
    xc = np.where(px < 0, -XC, XC); inx = np.abs(px - xc) < HALF + 0.01
    row = np.full(len(pos), -1)
    for r, f0 in enumerate(FLOOR): row[(py >= f0 - 0.012) & (py <= f0 + CUB_H + 0.012) & inx & (pz < FRONT - 0.005)] = r
    cub = row >= 0; fl0 = np.array(FLOOR)[np.maximum(row, 0)]; fz = np.full(len(pos), FRONT + 0.002); n_f = np.tile([0, 0, 1.0], (len(pos), 1))
    def tryp(sel, p2):
        idx = np.nonzero(sel & ~done & cov)[0]
        if not len(idx): return
        ok2, c2 = look(p2[idx], n_f[idx]); out[idx[ok2]] = c2[ok2]; done[idx[ok2]] = True
    tryp(cub & (ny > 0.6), np.stack([px, fl0 - 0.026, fz], 1))                                   # 床
    tryp(cub & (ny < -0.6), np.stack([px, fl0 + CUB_H + 0.026, fz], 1))                          # 天井
    wx = np.where(np.abs(px) < 0.2, 0.0, np.sign(px) * 0.745)                                   # 横の かべ → まん中の 柱・外の 柱
    tryp(cub & (np.abs(nx) > 0.6), np.stack([wx, py, fz], 1))
    tryp(~cub & (np.abs(nx) > 0.6), np.stack([np.sign(px) * 0.745, np.clip(py, 0.02, 2.13), fz], 1))      # 外の 横
    tryp(~cub & (ny > 0.6), np.stack([np.clip(px, -0.79, 0.79), np.full(len(pos), 2.10), fz], 1))          # 上
    tryp(~cub & (ny < -0.6), np.stack([np.clip(px, -0.79, 0.79), np.full(len(pos), 0.03), fz], 1))         # 下
    tryp(~cub & (nz < -0.6), np.stack([np.sign(px) * 0.745, np.clip(py, 0.02, 2.13), fz], 1))              # うしろ（見えない）＝外わくの 色
    img2 = out.reshape(TS, TS, 3); return fill(img2, done.reshape(TS, TS)), done.mean()


al = {}
for i, ph in enumerate(photos, 1):
    im = Image.open(ph); cam, s, _ = align(im)
    tex, fr = colors(im, cam)
    Image.fromarray((np.clip(tex, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(os.path.dirname(base), f'shelf_c{i}.webp'), 'WEBP', lossless=True, method=4)
    al[str(i)] = {'photo': os.path.basename(ph), 'cam': [round(x, 3) for x in cam], 'D': D, 'iou': round(float(s), 4), 'seen': round(float(fr), 3)}
    print(i, al[str(i)], flush=True)
json.dump(al, open(os.path.join(os.path.dirname(base), 'shelf_align.json'), 'w'), indent=1)
