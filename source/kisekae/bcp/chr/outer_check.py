# 見なおし用：キャラの outer（手で かいた 四角・形）が 小さくて キャラが 切れて いる 所を さがす
#   モデルが キャラと 見る 所（M > thr）で、outer（4px ふくらませた もの）の 外・キャラの 絵の すぐ そば（dist px）
#   python3 outer_check.py <出す png> <chr の 出力> … [--thr 0.6] [--dist 6] [--min 30]
import sys, json, os
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image, ImageDraw
a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = float(a[i + 1]); del a[i:i + 2]; return v
    return d
THR, DIST, MIN = opt('--thr', 0.6), opt('--dist', 6), opt('--min', 30)
out = a[0]; tiles = []
for O in a[1:]:
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.uint8); H, W = src.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    def shape(s):
        m = np.zeros((H, W), np.uint8)
        if 'rect' in s: x0, y0, x1, y1 = s['rect']; m[y0:y1, x0:x1] = 1
        elif 'poly' in s: cv2.fillPoly(m, [np.round(np.array(s['poly'], np.float64) * 8).astype(np.int32)], 1, shift=3)
        elif 'ell' in s: (cx, cy), rx, ry = s['ell']; m = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1).astype(np.uint8)
        return m.astype(bool)
    M = np.zeros((H, W), np.float32)
    for f in c['masks']: M = np.maximum(M, np.asarray(Image.open(f).convert('L')).astype(np.float32) / 255)
    outer = np.zeros((H, W), bool)
    for p in c['parts']:
        for s in p.get('outer', []): outer |= shape(s)
    if not outer.any(): print(O, 'no outer'); continue
    lay = np.zeros((H, W), bool)
    for p in c['parts']: lay |= np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127
    cut = (M > THR) & ~ndi.binary_dilation(outer, iterations=4) & ndi.binary_dilation(lay, iterations=int(DIST)) & ~lay
    lab, n = ndi.label(cut); sz = ndi.sum(cut, lab, range(1, n + 1)) if n else []
    keep = [i for i in range(n) if sz[i] >= MIN]
    print(os.path.basename(O), 'cut by outer:', int(sum(sz[i] for i in keep)), 'px in', len(keep), 'places', [tuple(int(v) for v in np.array(np.where(lab == i + 1)).mean(1)[::-1]) for i in keep][:8])
    for i in keep:
        ys, xs = np.where(lab == i + 1); cx, cy = int(xs.mean()), int(ys.mean()); r = 60
        x0, y0, x1, y1 = max(0, cx - r), max(0, cy - r), min(W, cx + r), min(H, cy + r)
        v = src.copy(); e = outer & ~cv2.erode(outer.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool); v[e] = [0, 255, 0]; v[lab == i + 1] = [255, 0, 255]
        t = Image.fromarray(v[y0:y1, x0:x1]).resize((200, 200), Image.NEAREST); ImageDraw.Draw(t).text((3, 3), f'{os.path.basename(O)} ({cx},{cy})', fill=(255, 255, 0)); tiles.append(t)
if tiles:
    NC = 6; R = (len(tiles) + NC - 1) // NC; S = Image.new('RGB', (NC * 204, R * 204), (200, 200, 200))
    for k, t in enumerate(tiles): S.paste(t, ((k % NC) * 204, (k // NC) * 204))
    S.save(out); print(out, S.size)
