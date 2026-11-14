# 台の 絵の 中の 場所を 測る（液晶の 丸・当選の ます・ボタン）
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import cam as C
d = np.load(ROOT + '/app/base.npz')
z, al, alb = d['z'], d['alpha'], d['albedo'].astype(np.float32) / 255
H, W = z.shape
YY, XX = np.mgrid[0:H, 0:W]


def box_px(x0, x1, y0, y1, zz=0.02):
    (a, b), (c, e) = C.proj(x0, y1, zz), C.proj(x1, y0, zz)
    return int(a), int(c), int(b), int(e)


# 液晶：暗い 丸
bx = box_px(-0.16, 0.16, -0.42, -0.13)
sub = np.zeros((H, W), bool); sub[bx[2]:bx[3], bx[0]:bx[1]] = True
dark = sub & (alb.max(2) < 0.06) & (al > 250)
lab, n = ndi.label(dark); cnt = np.bincount(lab.ravel()); cnt[0] = 0; m = lab == cnt.argmax()
ys, xs = np.nonzero(m)
cx, cy = xs.mean(), ys.mean(); r = np.sqrt(m.sum() / np.pi)
print(f'LCD dark disc: center px ({cx:.1f},{cy:.1f}) r {r:.1f}px  z median {np.median(z[m]):.4f}  bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]')
zl = float(np.median(z[m])); s = C.scale_at(zl)
print(f'   model: center ({(cx - W / 2) / s:+.4f},{-(cy - H / 2) / s:+.4f}) radius {r / s:.4f}')
# 黄色い 輪の 外の 半径：中心から 外へ 黄色が つづく ところ
yel = (alb[..., 0] > 0.7) & (alb[..., 1] > 0.3) & (alb[..., 2] < 0.25)
rr = []
for a in np.linspace(0, 2 * np.pi, 180, endpoint=False):
    t = np.arange(r + 2, r + 90, 0.5)
    x = np.clip(np.rint(cx + t * np.cos(a)).astype(int), 0, W - 1); y = np.clip(np.rint(cy + t * np.sin(a)).astype(int), 0, H - 1)
    k = np.nonzero(~yel[y, x])[0]
    rr.append(t[k[0]] if len(k) else np.nan)
rr = np.array(rr)
print('   ring outer radius px: p10', np.nanpercentile(rr, 10), 'p50', np.nanpercentile(rr, 50), 'p90', np.nanpercentile(rr, 90))
# 当選の ます：へこみ（まわりより z が 低い）
bx = box_px(-0.30, 0.50, -0.53, -0.37)
zz = z[bx[2]:bx[3], bx[0]:bx[1]]
base = np.median(zz)
print('row z median', base, 'p1', np.percentile(zz, 1), 'p99', np.percentile(zz, 99))
low = zz < base - 0.0025
low = ndi.binary_opening(low, iterations=2)
lab, n = ndi.label(low)
print('recess blobs', n)
socks = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    mk = lab[sl] == i
    if mk.sum() < 800: continue
    y0, x0 = sl[0].start + bx[2], sl[1].start + bx[0]
    hh, ww = mk.shape
    ys, xs = np.nonzero(mk)
    print(f'  blob {i}: px {int(mk.sum())} bbox x[{x0},{x0 + ww}] y[{y0},{y0 + hh}] center ({x0 + xs.mean():.1f},{y0 + ys.mean():.1f}) w {ww} h {hh} depth {base - np.median(zz[sl][mk]):.4f}')
    socks.append((x0 + (xs.min() + xs.max()) / 2, y0 + (ys.min() + ys.max()) / 2, ww, hh))
Image.fromarray((np.clip((zz - base + 0.01) / 0.02, 0, 1) * 255).astype(np.uint8)).save(ROOT + '/app/row_z.png')
# ますの ふち（もり上がった 八角の 輪）
hi = ndi.binary_opening(zz > base + 0.002, iterations=1)
lab, n = ndi.label(hi)
rings = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    mk = lab[sl] == i
    hh, ww = mk.shape
    if mk.sum() < 500 or ww > 140 or hh > 140 or ww < 70: continue
    y0, x0 = sl[0].start + bx[2], sl[1].start + bx[0]
    # 中の あな（輪の 内がわ）
    fill = ndi.binary_fill_holes(mk) & ~mk
    ys, xs = np.nonzero(fill)
    rings.append(dict(cx=x0 + (ww - 1) / 2, cy=y0 + (hh - 1) / 2, w=ww, h=hh, iw=int(xs.max() - xs.min() + 1) if len(xs) else 0, ih=int(ys.max() - ys.min() + 1) if len(ys) else 0, zrim=float(np.median(zz[sl][mk]))))
rings.sort(key=lambda q: q['cx'])
for q in rings:
    s = C.scale_at(base)
    print(f"  socket: center px ({q['cx']:.1f},{q['cy']:.1f}) outer {q['w']}×{q['h']} inner {q['iw']}×{q['ih']}  model ({(q['cx'] - W / 2) / s:+.4f},{-(q['cy'] - H / 2) / s:+.4f}) w {q['w'] / s:.4f}  rim z {q['zrim']:.4f}")
print('count', len(rings), ' spacing px', np.diff([q['cx'] for q in rings]).round(1))
json.dump(dict(lcd=dict(cx=float(cx), cy=float(cy), r=float(r), z=zl), sockets=rings, row_z=float(base)), open(ROOT + '/app/layout1.json', 'w'), indent=1)
