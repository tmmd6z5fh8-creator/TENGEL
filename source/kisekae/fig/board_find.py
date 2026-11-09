# フィギュアの ボードの 板（金の わくの 中の くぼんだ 平らな 面）を 形から さがす：python3 kisekae/fig/board_find.py <out/figN.npz> ...
#   → out/figN_board.json：{ c:[x,y,z], w, h }（フィギュアの 体の 座標：高さ 2.15・y 0〜・まん中 x=z=0）
import sys, json
import numpy as np
for src in sys.argv[1:]:
    d = np.load(src); V = d['V'].astype(np.float64); T = d['T'].astype(np.int64)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; fn = np.cross(b - a, c - a); ar = np.linalg.norm(fn, axis=1) / 2; fn /= (2 * ar[:, None] + 1e-30); cen = (a + b + c) / 3
    lo, hi = V.min(0), V.max(0); wid = hi[0] - lo[0]
    sel = (fn[:, 2] > 0.97) & (np.abs(cen[:, 0]) < wid * 0.3) & (cen[:, 1] > 0.25 * hi[1]) & (cen[:, 1] < 0.85 * hi[1])
    zs = np.round(cen[sel, 2] / 0.01) * 0.01; zv, inv = np.unique(zs, return_inverse=True); area = np.bincount(inv, weights=ar[sel])
    best = None
    for k in np.argsort(-area)[:6]:
        m = sel.copy(); m[sel] = inv == k
        pts = np.concatenate([a[m], b[m], c[m]])
        x0, x1 = np.percentile(pts[:, 0], [1, 99]); y0, y1 = np.percentile(pts[:, 1], [1, 99])
        sc = area[k] * (1 - abs((x0 + x1) / 2) / wid)          # 大きくて まん中に ある 面
        if best is None or sc > best[0]: best = (sc, float(zv[k]), x0, x1, y0, y1, float(area[k]))
    sc, z, x0, x1, y0, y1, A = best
    # 同じ 深さの 面の うち いちばん 大きく つながった かたまり（ボードの 板）の 四角：上の かざりの 面を まぜない
    from scipy import ndimage
    m = sel.copy(); m[sel] = np.abs(np.round(cen[sel, 2] / 0.01) * 0.01 - z) < 1e-6
    g = 0.01; gx0, gy0 = x0 - 0.05, y0 - 0.05; nx, ny = int((x1 - x0 + 0.1) / g) + 2, int((y1 - y0 + 0.1) / g) + 2; occ = np.zeros((ny, nx), bool)
    ws = np.random.default_rng(0).dirichlet([1, 1, 1], 24)
    for t in np.nonzero(m)[0]:
        P = ws @ np.stack([a[t], b[t], c[t]]); ix = ((P[:, 0] - gx0) / g).astype(int); iy = ((P[:, 1] - gy0) / g).astype(int)
        ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny); occ[iy[ok], ix[ok]] = True
    occ = ndimage.binary_closing(occ, iterations=2); lab, nl = ndimage.label(occ)
    if nl:
        big = 1 + int(np.argmax(ndimage.sum(occ, lab, range(1, nl + 1)))); ys_, xs_ = np.nonzero(lab == big)
        # かたまりの 中の いちばん 大きな 四角（行ごとに うまって いる はば）
        sub = lab == big; rows = np.nonzero(sub.sum(1) > 0.6 * sub.sum(1).max())[0]; cols = np.nonzero(sub[rows].sum(0) > 0.6 * len(rows))[0]
        x0, x1 = gx0 + cols.min() * g, gx0 + (cols.max() + 1) * g; y0, y1 = gy0 + rows.min() * g, gy0 + (rows.max() + 1) * g
    # 板の 深さは 面の いちばん 前（0.01 きざみの 丸めでは なく：板を 少し 前に 出した とき 元の 面が すけない ように）
    zin = cen[m & (np.abs(cen[:, 0] - (x0 + x1) / 2) < (x1 - x0) / 2) & (np.abs(cen[:, 1] - (y0 + y1) / 2) < (y1 - y0) / 2), 2]
    if len(zin): z = float(np.percentile(zin, 99.5))
    out = {'c': [float((x0 + x1) / 2), float((y0 + y1) / 2), z], 'w': float(x1 - x0), 'h': float(y1 - y0), 'area': A}
    json.dump(out, open(src.replace('.npz', '_board.json'), 'w')); print(src, {k: (round(v, 3) if isinstance(v, float) else [round(x, 3) for x in v]) for k, v in out.items()})
