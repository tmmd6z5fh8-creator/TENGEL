# 屋根の 馬の 目（まるい こぶ 2つ）を ぬり直す 道具
#   こぶ＝球の あてはめ（ana4.py）。こぶの 表面に のっている 絵の 点（テクセル）だけ を、3D の 場所から 決めて ぬる
#   → どの 向きから 見ても 同じ（前は 正面から 見える ところ だけ 黒く、上は 肌色の ままだった）
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
from scipy import ndimage as ndi

SPH = dict(L=(np.array([-0.06904, 0.82518, 0.07643]), 0.01468, np.array([-0.6183, 0.3122, 0.7213]), 95.0),
           R=(np.array([0.00726, 0.81862, 0.07828]), 0.01691, np.array([0.4219, 0.1977, 0.8848]), 84.0))     # 中心・半径・こぶの 向き・こぶの 広がり（度：これより 外は ぬらない）
D_IN, D_OUT = 0.0004, 0.0012       # 球の 表面から この 分 外まで ぬる（D_IN まで 全部・D_OUT で 0）
NEAR = 0.006                       # こぶの まわり（この 分 外までの 三角を 調べる）
GUT = 4                            # 島の 外（三角が ない ところ）へ 色を ひろげる 画素


def _raster(uvpx, P3, W, H, posmap, cov):
    """三角を 絵の 上に 描く（テクセルの 中心が 三角の 中 → その 点の 3D の 場所）"""
    x0 = np.floor(uvpx[:, :, 0].min(1)).astype(int); x1 = np.ceil(uvpx[:, :, 0].max(1)).astype(int)
    y0 = np.floor(uvpx[:, :, 1].min(1)).astype(int); y1 = np.ceil(uvpx[:, :, 1].max(1)).astype(int)
    for t in range(len(uvpx)):
        a, b, c = uvpx[t]
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12:
            continue
        xs = np.arange(max(x0[t], 0), min(x1[t], W - 1) + 1); ys = np.arange(max(y0[t], 0), min(y1[t], H - 1) + 1)
        if not len(xs) or not len(ys):
            continue
        X, Y = np.meshgrid(xs, ys)
        w0 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
        w1 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not ins.any():
            continue
        yy, xx = Y[ins], X[ins]
        cov[yy, xx] = True
        if posmap is not None:
            posmap[yy, xx] = w0[ins][:, None] * P3[t, 0] + w1[ins][:, None] * P3[t, 1] + w2[ins][:, None] * P3[t, 2]


def alpha_map(pos, uv, idx, W, H, verbose=True):
    """ぬる 強さ（0〜1）の 地図（H×W）と 目ごとの 印"""
    P = pos.astype(np.float64)
    UV = uv.astype(np.float64) * [W, H] - 0.5                 # テクセルの 中心＝整数
    alpha = np.zeros((H, W), np.float64)
    which = np.zeros((H, W), np.uint8)
    info = {}
    for ei, (name, (c, r, ax, lim)) in enumerate(SPH.items(), 1):
        d = np.linalg.norm(P - c, axis=1) - r
        tm = (d < NEAR)[idx].any(1)
        tri = idx[tm]
        up = UV[tri]
        # 目の 三角が ある 島の まわり（箱）ごとに
        posmap = np.zeros((H, W, 3)); cov = np.zeros((H, W), bool)
        _raster(up, P[tri], W, H, posmap, cov)
        dd = np.linalg.norm(posmap - c, axis=2) - r
        a = np.clip((D_OUT - dd) / (D_OUT - D_IN), 0, 1)
        a = a * a * (3 - 2 * a)
        cosang = ((posmap - c) @ ax) / np.maximum(np.linalg.norm(posmap - c, axis=2), 1e-12)
        ang = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
        a = np.where(cov & (ang < lim), a, 0.0)
        amax = float(ang[cov & (a > 0)].max()) if (cov & (a > 0)).any() else 0.0
        # 島の 外（どの 三角も ない ところ）へ ひろげる
        ys, xs = np.nonzero(a > 0)
        bx0, bx1, by0, by1 = xs.min() - 12, xs.max() + 13, ys.min() - 12, ys.max() + 13
        ua = UV[idx]
        hit = (ua[:, :, 0].max(1) >= bx0) & (ua[:, :, 0].min(1) <= bx1) & (ua[:, :, 1].max(1) >= by0) & (ua[:, :, 1].min(1) <= by1)
        cov_any = np.zeros((H, W), bool)
        _raster(ua[hit], None, W, H, None, cov_any)
        dist, (iy, ix) = ndi.distance_transform_edt(~cov, return_indices=True)
        gut = (~cov_any) & (dist <= GUT) & (a[iy, ix] > 0)
        a2 = a.copy(); a2[gut] = a[iy, ix][gut]
        n_in, n_gut = int((a > 0).sum()), int(gut.sum())
        new = a2 > alpha
        which[new & (a2 > 0)] = ei
        alpha = np.maximum(alpha, a2)
        info[name] = dict(tris=int(tm.sum()), texels=n_in, full=int((a >= 0.999).sum()), gutter=n_gut, max_angle=round(amax, 1), limit=lim)
        if verbose:
            print(name, info[name])
        assert amax < lim - 3, (name, amax, lim)
    return alpha, which, info


# ---------------------------------------------------------------- ぬり直し（色・つや・面の 向きの 絵）
EYE_RGB = np.array([32, 21, 17], np.float64)      # 目の 色（今の 黒い ところの まん中の 色：こげ茶に 近い 黒）
EYE_ROUGH = 106                                    # つや（今の 目の あたりの まん中の 値＝0.42）
FLAT_N = np.array([128, 128, 255], np.float64)     # 面の 向きの 絵：平ら（前の ぬり分けの でこぼこを 消す）
NEAR2 = 0.012                                      # 目の まわりの 肌も 調べる（はみ出した 黒を 肌色に もどす）
RING0, RING1 = 0.0042, 0.0060                      # はみ出しを 直す はんい（こぶの 表面から。RING0 まで 全部・RING1 で 0）
SKIN0, SKIN1 = 0.0045, 0.0100                      # 肌色の 見本を とる はんい


def _lum(c):
    return c @ np.array([0.299, 0.587, 0.114])


def paint(tex, pos, uv, idx, verbose=True, seed=7):
    """tex: [色, 金属と つや, 面の 向き]（uint8 H×W×3）→ (新しい 3まい, 変えた 点の 印 3まい, 記録)"""
    H, W = tex[0].shape[:2]
    P = pos.astype(np.float64)
    UV = uv.astype(np.float64) * [W, H] - 0.5
    ua = UV[idx]
    new = [t.astype(np.float64) for t in tex]
    chg = [np.zeros((H, W), bool) for _ in range(3)]
    rng = np.random.default_rng(seed)
    info = {}
    for name, (c, r, ax, lim) in SPH.items():
        d = np.linalg.norm(P - c, axis=1) - r
        tm = (d < NEAR2)[idx].any(1)
        tri = idx[tm]
        posmap = np.zeros((H, W, 3)); cov = np.zeros((H, W), bool)
        _raster(UV[tri], P[tri], W, H, posmap, cov)
        dd = np.where(cov, np.linalg.norm(posmap - c, axis=2) - r, 9.0)
        a = np.clip((D_OUT - dd) / (D_OUT - D_IN), 0, 1)
        a = a * a * (3 - 2 * a)
        cosang = ((posmap - c) @ ax) / np.maximum(np.linalg.norm(posmap - c, axis=2), 1e-12)
        ang = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
        a = np.where(cov & (ang < lim), a, 0.0)
        amax = float(ang[a > 0].max())
        assert amax < lim - 3, (name, amax, lim)
        # 肌色の 見本（こぶの 外の 輪）
        c0 = tex[0].astype(np.float64)
        lum = _lum(c0)
        brown = (c0[..., 0] > c0[..., 1]) & (c0[..., 1] > c0[..., 2]) & (c0[..., 0] - c0[..., 2] > 50)
        ring = cov & (dd >= SKIN0) & (dd < SKIN1) & brown & (lum > 110)
        skin = np.median(c0[ring], 0)
        pool = c0[ring] - skin
        pool = pool[np.abs(_lum(pool)) < 12]                      # ふつうの 肌の ゆらぎ だけ
        sl = float(_lum(skin))
        # はみ出した 黒（こぶの 外・暗い）→ 肌色
        wr = np.clip((RING1 - dd) / (RING1 - RING0), 0, 1)
        wd = np.clip((sl - 17 - lum) / 20, 0, 1)
        wc = np.where(cov & (a < 1), wr * wd, 0.0)
        fill = skin + pool[rng.integers(0, len(pool), (H, W))]
        base = c0 * (1 - wc[..., None]) + fill * wc[..., None]
        out0 = base * (1 - a[..., None]) + EYE_RGB * a[..., None]
        m_eye = a > 0
        m_spill = (wc > 0) & ~(a >= 1)
        m0 = m_eye | (wc > 0)
        new[0][m0] = out0[m0]; chg[0] |= m0
        t1 = new[1].copy(); t1[..., 1] = EYE_ROUGH; t1[..., 2] = 0
        new[1][m_eye] = (new[1] * (1 - a[..., None]) + t1 * a[..., None])[m_eye]; chg[1] |= m_eye
        new[2][m_eye] = (new[2] * (1 - a[..., None]) + FLAT_N * a[..., None])[m_eye]; chg[2] |= m_eye
        # 島の 外（どの 三角も ない ところ）：いちばん 近い 点が 変わった ときは その 色を うつす
        ys, xs = np.nonzero(m0)
        bx0, bx1, by0, by1 = xs.min() - 14, xs.max() + 15, ys.min() - 14, ys.max() + 15
        hit = (ua[:, :, 0].max(1) >= bx0) & (ua[:, :, 0].min(1) <= bx1) & (ua[:, :, 1].max(1) >= by0) & (ua[:, :, 1].min(1) <= by1)
        cov_any = np.zeros((H, W), bool)
        _raster(ua[hit], None, W, H, None, cov_any)
        box = np.zeros((H, W), bool); box[max(by0, 0):by1, max(bx0, 0):bx1] = True
        dist, (iy, ix) = ndi.distance_transform_edt(~cov_any, return_indices=True)
        ngut = [0, 0, 0]
        for k, mk in enumerate((m0, m_eye, m_eye)):
            g = box & (~cov_any) & (dist <= GUT) & mk[iy, ix]
            new[k][g] = new[k][iy, ix][g]; chg[k] |= g; ngut[k] = int(g.sum())
        info[name] = dict(triangles=int(tm.sum()), eye_texels=int(m_eye.sum()), eye_full=int((a >= 0.999).sum()), spill_texels=int(m_spill.sum()), spill_strong=int((m_spill & (wc > 0.5)).sum()),
                          gutter=ngut, max_angle=round(amax, 1), limit=lim, skin_rgb=[round(float(x), 1) for x in skin], skin_samples=int(ring.sum()))
        if verbose:
            print(name, info[name])
    outs = [np.clip(np.rint(n), 0, 255).astype(np.uint8) for n in new]
    for k in range(3):
        assert (outs[k][~chg[k]] == tex[k][~chg[k]]).all()
    return outs, chg, info
