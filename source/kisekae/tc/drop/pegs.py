# 釘（黄色い ピラミッド 18本）を 見つける・伸ばす ための 道具
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *
from scipy import ndimage as ndi
from scipy.optimize import least_squares
import hmap as HM

PX = HM.PX
BOX = (-0.45, 0.45, -0.16, 0.33)            # 釘の ある あたり（x0, x1, y0, y1）


def _xy(c, r):
    return HM.X0 + (c + 0.5) / PX, HM.Y1 - (r + 0.5) / PX


def find_pegs(npz=ROOT + '/out/look/hmap_orig.npz', verbose=False):
    """高さの 地図から 釘を 見つける → [dict(ax, ay, H, rx, ry, base=(c, gx, gy))]（上から 下・左から 右）"""
    d = np.load(npz)
    z, a, alb = d['z'].astype(np.float64), d['a'], d['alb'].astype(np.float32) / 255
    Hh, Ww = z.shape
    CC, RR = np.meshgrid(np.arange(Ww), np.arange(Hh))
    XX, YY = _xy(CC, RR)
    ok = a > 0.99
    green = (alb[..., 1] > alb[..., 0] * 1.35) & (alb[..., 1] > alb[..., 2] * 1.15) & (alb[..., 0] > 0.2) & (alb[..., 0] < 0.55) & ok
    yel = (alb[..., 0] > 0.7) & (alb[..., 1] > 0.3) & (alb[..., 1] < 0.8) & (alb[..., 2] < 0.2) & ok
    box = (XX > BOX[0]) & (XX < BOX[1]) & (YY > BOX[2]) & (YY < BOX[3])
    gb = green & box
    zg = z[gb]
    sel = np.abs(zg - np.median(zg)) < 0.006
    M = np.c_[XX[gb][sel], YY[gb][sel], np.ones(int(sel.sum()))]
    co, *_ = np.linalg.lstsq(M, zg[sel], rcond=None)
    hgt = np.where(ok, z - (co[0] * XX + co[1] * YY + co[2]), 0.0)
    cand = box & (hgt > 0.02) & yel                       # 高い ところ だけ → ろうとの ふちと 釘が はなれる
    lab, n = ndi.label(cand)
    pegs = []
    for i, s in enumerate(ndi.find_objects(lab), 1):
        mk = lab[s] == i
        if mk.sum() < 150:
            continue
        r_, c_ = np.nonzero(mk); r_ += s[0].start; c_ += s[1].start
        x, y = _xy(c_, r_)
        w, h = x.max() - x.min(), y.max() - y.min()
        if w > 0.05 or h > 0.05:                          # 釘の 上の ほう（高さ 0.02 より 上）は 小さい ひし形
            continue
        k = hgt[r_, c_].argmax()
        ax0, ay0 = x[k], y[k]
        # まわりの 盤（うすい 緑）で その 釘の 土台の 面を 決める
        m = np.abs(XX - ax0) / 0.031 + np.abs(YY - ay0) / 0.031
        ring = (m > 1.25) & (m < 1.9) & green
        Mr = np.c_[XX[ring] - ax0, YY[ring] - ay0, np.ones(int(ring.sum()))]
        zr = z[ring]
        keep = np.abs(zr - np.median(zr)) < 0.003
        cb, *_ = np.linalg.lstsq(Mr[keep], zr[keep], rcond=None)
        # ピラミッドの あてはめ：h = H (1 − |dx|/rx − |dy|/ry)
        reg = (m < 1.0) & yel
        xs, ys = XX[reg], YY[reg]
        hs = z[reg] - (cb[0] * (xs - ax0) + cb[1] * (ys - ay0) + cb[2])

        def res(p):
            ax, ay, H, rx, ry = p
            return np.maximum(H * (1 - np.abs(xs - ax) / rx - np.abs(ys - ay) / ry), 0) - hs
        f = least_squares(res, [ax0, ay0, hs.max(), 0.03, 0.031], loss='soft_l1', f_scale=0.002)
        ax, ay, H, rx, ry = f.x
        rms = float(np.sqrt((res(f.x) ** 2).mean()))
        pegs.append(dict(ax=float(ax), ay=float(ay), H=float(H), rx=float(rx), ry=float(ry), base=(float(cb[2]), float(cb[0]), float(cb[1])), ax0=float(ax0), ay0=float(ay0), rms=rms, hmax=float(hs.max()), nring=int(keep.sum())))
    pegs.sort(key=lambda p: (-round(p['ay'] / 0.04), p['ax']))
    if verbose:
        print('board plane', co)
    return pegs


if __name__ == '__main__':
    pegs = find_pegs(verbose=True)
    for i, p in enumerate(pegs):
        print(f"{i:2d} apex ({p['ax']:+.4f},{p['ay']:+.4f}) H {p['H']:.4f} (max {p['hmax']:.4f}) rx {p['rx']:.4f} ry {p['ry']:.4f} base z {p['base'][0]:.4f} slope ({p['base'][1]:+.4f},{p['base'][2]:+.4f}) rms {p['rms']:.5f} ring {p['nring']}")
    print('count', len(pegs))
    json.dump(pegs, open(ROOT + '/out/pegs_orig.json', 'w'), indent=1)


H0 = 0.0015          # 盤の でこぼこ（±0.0012）より 上 だけ 動かす
TOL0, TOL1 = 0.004, 0.007     # ピラミッドの 形から この 分より 上に 出ている 頂点（ろうとの ふち など）は 動かさない


def stretch(P, N, pegs, k):
    """釘を 前（+z）へ k倍に 伸ばす。土台（盤に ついている ところ）は 動かさない
       P, N: 頂点・面の 向き（float64 の 写し）→ (新しい P, 新しい N, 動かした 頂点の 印, 釘ごとの 記録)"""
    P2, N2 = P.copy(), N.copy()
    moved = np.zeros(len(P), bool)
    log = []
    for i, p in enumerate(pegs):
        dx, dy = P[:, 0] - p['ax'], P[:, 1] - p['ay']
        v = np.nonzero((np.abs(dx) < 0.045) & (np.abs(dy) < 0.045) & (P[:, 2] > 0.0) & (P[:, 2] < 0.09))[0]
        dx, dy = dx[v], dy[v]
        m = np.abs(dx) / p['rx'] + np.abs(dy) / p['ry']
        c, gx, gy = p['base']
        base = c + gx * (P[v, 0] - p['ax0']) + gy * (P[v, 1] - p['ay0'])
        ha = P[v, 2] - base
        hm = p['H'] * np.maximum(1 - m, 0)
        w = np.clip(1 - (ha - hm - TOL0) / (TOL1 - TOL0), 0, 1) * (m < 1.08)
        d = (k - 1) * np.maximum(ha - H0, 0) * w
        on = d > 0
        vv = v[on]
        assert not moved[vv].any(), '釘が 重なっている'
        P2[vv, 2] += d[on]
        ke = 1 + (k - 1) * w[on]                               # その 頂点の 伸び
        n = N[vv]
        n2 = np.c_[n[:, 0] + (ke - 1) / ke * gx * n[:, 2], n[:, 1] + (ke - 1) / ke * gy * n[:, 2], n[:, 2] / ke]
        N2[vv] = n2 / np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-12)
        moved[vv] = True
        log.append(dict(i=i, x=p['ax'], y=p['ay'], moved=int(on.sum()), tip_before=float(P[v, 2][on].max()), tip_after=float(P2[vv, 2].max()), height_before=float(ha[on].max()), height_after=float(ha[on].max() + d[on].max()), partial=int(((w[on] < 1)).sum())))
    return P2, N2, moved, log
