# 台を 盤と 平行な 面（z＝一定）で 切った 切り口（線分の 集まり）
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *

V2 = ROOT + '/out/Tenger_Lucky_Drop_v2.glb'


def slice_z(pos, idx, z0, box=None):
    """三角と 面 z=z0 の 交わり → (n,2,2) の 線分（x,y）。box＝(x0,x1,y0,y1) の 中だけ"""
    P = pos.astype(np.float64)
    T = P[idx]                                   # (n,3,3)
    if box is not None:
        x0, x1, y0, y1 = box
        keep = (T[:, :, 0].max(1) >= x0) & (T[:, :, 0].min(1) <= x1) & (T[:, :, 1].max(1) >= y0) & (T[:, :, 1].min(1) <= y1)
        T = T[keep]
    d = T[:, :, 2] - z0
    cross = (d.min(1) < 0) & (d.max(1) > 0)
    T, d = T[cross], d[cross]
    segs = []
    pts = np.full((len(T), 2, 2), np.nan)
    cnt = np.zeros(len(T), int)
    for a, b in ((0, 1), (1, 2), (2, 0)):
        da, db = d[:, a], d[:, b]
        m = (da < 0) != (db < 0)
        u = np.where(m, da / np.where(m, da - db, 1), 0)
        p = T[:, a, :2] + (T[:, b, :2] - T[:, a, :2]) * u[:, None]
        k = np.nonzero(m)[0]
        ok = cnt[k] < 2
        pts[k[ok], cnt[k[ok]]] = p[k[ok]]
        cnt[k] += 1
    good = cnt >= 2
    return pts[good]


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    js, binb = read_glb(V2)
    pos, uv, nrm, idx = arrays(js, binb)
    box = (-0.52, 0.52, -0.42, 0.50)
    K = 2200
    W, H = int((box[1] - box[0]) * K), int((box[3] - box[2]) * K)
    zs = [float(v) for v in sys.argv[2:]] or [0.035, 0.053, 0.075]
    cols = [(220, 40, 40), (30, 110, 220), (20, 150, 60), (160, 60, 200)]
    im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
    for z0, c in zip(zs, cols):
        S = slice_z(pos, idx, z0, box)
        print('z', z0, 'segments', len(S))
        for (a, b) in S:
            dr.line(((a[0] - box[0]) * K, (box[3] - a[1]) * K, (b[0] - box[0]) * K, (box[3] - b[1]) * K), fill=c, width=2)
        np.save(ROOT + f'/out/look/slice_{z0:.3f}.npy', S)
    for v in np.arange(-0.5, 0.51, 0.1):
        X = (v - box[0]) * K; dr.line((X, 0, X, H), fill=(210, 210, 210)); dr.text((X + 3, 3), f'{v:+.1f}', fill=(120, 0, 0))
    for v in np.arange(-0.4, 0.51, 0.1):
        Y = (box[3] - v) * K; dr.line((0, Y, W, Y), fill=(210, 210, 210)); dr.text((3, Y + 3), f'{v:+.1f}', fill=(0, 0, 120))
    im.save(sys.argv[1]); print(im.size)
