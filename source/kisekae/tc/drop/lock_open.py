# 「保留結果を見る」の かぎの 絵を「あいた かぎ」に かえた 台の 絵（その 所 だけ）を 作る
#   絵（テクスチャ）の 点を 3D の 場所から 決めて ぬる（目の ぬり直しと 同じ やり方）→ その 帯 だけ 描き直す → かぎの まわり だけ 切り出す
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from cam import *
import eyes as EY
import drop_render as DR
from scipy import ndimage as ndi
from PIL import Image

BOX = (-0.262, -0.166, -0.832, -0.718)        # かぎの 絵の はんい（x0, x1, y0, y1）
INK = np.array([45, 15, 12], np.float64) / 255


def sd_box(x, y, cx, cy, hx, hy, r):
    qx, qy = np.abs(x - cx) - hx + r, np.abs(y - cy) - hy + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def lock_sdf(x, y, open_=True):
    """かぎの 形（中＝マイナス）。open_＝つるが 上がって 左の 足が 本体から はなれて いる"""
    cx = -0.2138
    body = sd_box(x, y, cx, -0.789, 0.0308, 0.022, 0.006)
    key = np.minimum(np.hypot(x - cx, y + 0.783) - 0.0088, sd_box(x, y, cx, -0.796, 0.0042, 0.008, 0.001))
    body = np.maximum(body, -key)                                   # かぎ穴を くりぬく
    yc = -0.749 if open_ else -0.760                                # つるの 丸の 中心
    ro, ri = 0.0232, 0.0138
    arc = np.maximum(np.abs(np.hypot(x - cx, y - yc) - (ro + ri) / 2) - (ro - ri) / 2, -(y - yc))      # 上の 半分の 輪
    w = (ro - ri) / 2; xr, xl = cx + (ro + ri) / 2, cx - (ro + ri) / 2
    legr = sd_box(x, y, xr, (yc + -0.770) / 2, w, (yc + 0.770) / 2, 0.0005)                            # 右の 足：本体まで
    yl = -0.7585 if open_ else -0.770
    legl = sd_box(x, y, xl, (yc + yl) / 2, w, (yc - yl) / 2, 0.0015)                                    # 左の 足：あいた ときは 短い
    return np.minimum(np.minimum(body, arc), np.minimum(legr, legl))


def paint(prims):
    """色の 絵の かぎを あいた かぎに 描きかえる（その場で）→ 変えた 点の 数"""
    p = prims[0]
    tex = p.mat.base_tex.tex
    img = tex.img                                  # float32 H×W×4（0〜1・sRGB の まま）
    H, W = img.shape[:2]
    P = p.pos.astype(np.float64); UV = p.uv.astype(np.float64) * [W, H] - 0.5
    idx = p.idx
    T = P[idx]
    x0, x1, y0, y1 = BOX
    sel = (T[:, :, 0].max(1) >= x0 - 0.01) & (T[:, :, 0].min(1) <= x1 + 0.01) & (T[:, :, 1].max(1) >= y0 - 0.01) & (T[:, :, 1].min(1) <= y1 + 0.01) & (T[:, :, 2].min(1) > 0.06) & (p.nrm[idx][:, :, 2].min(1) > 0.5)
    tri = idx[sel]
    posmap = np.zeros((H, W, 3)); cov = np.zeros((H, W), bool)
    EY._raster(UV[tri], P[tri], W, H, posmap, cov)
    X, Y = posmap[..., 0], posmap[..., 1]
    inb = cov & (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
    c0 = img[..., :3].astype(np.float64)
    lum = c0 @ [0.299, 0.587, 0.114]
    mint = np.median(c0[inb & (lum > 0.6)], 0)
    pool = c0[inb & (lum > 0.6)] - mint
    rng = np.random.default_rng(4)
    # 点の 大きさ（台の 単位）：となりの 点との 3D の きょり
    ys, xs = np.nonzero(inb)
    dx = np.hypot(np.diff(X, axis=1), np.diff(Y, axis=1)); texel = float(np.median(dx[inb[:, 1:] & inb[:, :-1]]))
    sd = lock_sdf(X, Y, True)
    a = np.clip(0.5 - sd / (1.2 * texel), 0, 1)
    edge = np.clip(np.minimum(np.minimum(X - x0, x1 - X), np.minimum(Y - y0, y1 - Y)) / 0.004, 0, 1)      # はんいの はしは もとの 色へ なめらかに
    bg = mint + pool[rng.integers(0, len(pool), (H, W))]
    new = bg * (1 - a[..., None]) + INK * a[..., None]
    new = c0 * (1 - edge[..., None]) + new * edge[..., None]
    out = c0.copy(); out[inb] = new[inb]
    # 島の 外へ ひろげる
    ua = UV[idx]
    bx0, bx1, by0, by1 = xs.min() - 12, xs.max() + 13, ys.min() - 12, ys.max() + 13
    hit = (ua[:, :, 0].max(1) >= bx0) & (ua[:, :, 0].min(1) <= bx1) & (ua[:, :, 1].max(1) >= by0) & (ua[:, :, 1].min(1) <= by1)
    cov_any = np.zeros((H, W), bool); EY._raster(ua[hit], None, W, H, None, cov_any)
    box = np.zeros((H, W), bool); box[max(by0, 0):by1, max(bx0, 0):bx1] = True
    dist, (iy, ix) = ndi.distance_transform_edt(~cov_any, return_indices=True)
    g = box & (~cov_any) & (dist <= 4) & inb[iy, ix]
    out[g] = out[iy, ix][g]
    img[..., :3] = out.astype(np.float32)
    tex._mips = None
    return int(inb.sum()), int(g.sum()), texel, mint


if __name__ == '__main__':
    APP = ROOT + '/app/'
    m = GLB.load(V2); prims = m.flatten()
    print('painted', paint(prims))
    # かぎの ある 帯 だけ 描き直す
    (xa, ya), (xb, yb) = proj(BOX[0] - 0.02, BOX[3] + 0.015, 0.084, DR.K), proj(BOX[1] + 0.02, BOX[2] - 0.015, 0.084, DR.K)
    r0, r1 = int(ya) // 2 * 2, (int(np.ceil(yb)) + 1) // 2 * 2
    o = DR.render_full(prims, rows=(r0, r1))
    f = DR.finish(o)
    d = np.load(APP + 'base.npz')
    ao = d['ao'][r0 // 2:r1 // 2]                      # まわりの 光の 影は もとと 同じ（形は かわらない）
    rgb = (np.clip(DR.color(f, ao), 0, 1) * 255 + 0.5).astype(np.uint8)
    base = d['rgb'][r0 // 2:r1 // 2]
    df = np.abs(rgb.astype(int) - base.astype(int)).max(2)
    ys, xs = np.nonzero(df > 3)
    print('rows', r0 // 2, r1 // 2, 'diff px', len(xs), 'bbox x', xs.min(), xs.max(), 'y', ys.min() + r0 // 2, ys.max() + r0 // 2)
    # かぎの まわり だけ 切り出す（ふちは すき通るように：もとの 絵と 同じ 色なので つなぎ目は 見えない）
    x0, x1, y0, y1 = xs.min() - 6, xs.max() + 7, ys.min() - 6, ys.max() + 7
    yy, xx = np.mgrid[y0:y1, x0:x1]
    a = np.clip(np.minimum(np.minimum(xx - x0, x1 - 1 - xx), np.minimum(yy - y0, y1 - 1 - yy)) / 4.0, 0, 1)
    spr = np.dstack([rgb[y0:y1, x0:x1], (a * 255 + 0.5).astype(np.uint8)])
    Image.fromarray(spr, 'RGBA').save(APP + 'see_open.png')
    import json
    json.dump(dict(x=int(x0), y=int(y0 + r0 // 2), w=int(x1 - x0), h=int(y1 - y0)), open(APP + 'see_open.json', 'w'))
    print('sprite', spr.shape, 'at', x0, y0 + r0 // 2)
    # 見る 用
    full = d['rgb'].copy(); full[r0 // 2:r1 // 2] = rgb
    Image.fromarray(np.concatenate([d['rgb'][1500:1760, 150:980], full[1500:1760, 150:980]], 0)).save(APP + 'see_view.png')
