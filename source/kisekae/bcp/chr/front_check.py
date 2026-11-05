# 見なおし用：前に 重ねる 動かない 物（occl.png）が キャラの 体の 中に 入って いないか（目の 光・ほっぺ など が 止まって 見えない か）
#   python3 front_check.py <出す png> <chr の 出力> …
#   キャラの 絵（すき通し 0.5 より 大きい 所）から 6px 以上 内がわ に ある occl（0.5 より 大きい）の かたまりを ならべる
import sys, json, os
import numpy as np
import scipy.ndimage as ndi
from PIL import Image, ImageDraw
out = sys.argv[1]; tiles = []
for O in sys.argv[2:]:
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(c['clean']).convert('RGB')); H, W = src.shape[:2]
    if not os.path.exists(os.path.join(O, 'occl.png')): print(os.path.basename(O), 'no occl'); continue
    oc = np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')) > 127
    lay = np.zeros((H, W), bool)
    for p in c['parts']: lay |= np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127
    body = ndi.binary_fill_holes(lay | oc) & ~ndi.binary_dilation(~(ndi.binary_fill_holes(lay | oc)), iterations=6)
    # 体の 中で、キャラの 絵に かこまれて いる occl
    lab, n = ndi.label(oc)
    found = []
    for k in range(1, n + 1):
        R = lab == k
        ring = ndi.binary_dilation(R, iterations=3) & ~R
        if ring.sum() == 0: continue
        fr = (ring & lay).sum() / ring.sum()
        if fr > 0.85 and (R & body).any():
            ys, xs = np.where(R); found.append((int(xs.mean()), int(ys.mean()), int(R.sum()), round(float(fr), 2)))
    print(os.path.basename(O), 'enclosed front objects', len(found), found[:8])
    for (cx, cy, sz, fr) in found[:8]:
        r = 40; x0, y0, x1, y1 = max(0, cx - r), max(0, cy - r), min(W, cx + r), min(H, cy + r)
        v = src.astype(np.float32).copy(); v[oc] = v[oc] * 0.5 + np.array([0, 255, 0]) * 0.5
        t = Image.fromarray(v[y0:y1, x0:x1].astype(np.uint8)).resize((160, 160), Image.NEAREST)
        ImageDraw.Draw(t).text((2, 2), f'{os.path.basename(O)} ({cx},{cy}) {sz}', fill=(255, 255, 0)); tiles.append(t)
if tiles:
    NC = 8; R_ = (len(tiles) + NC - 1) // NC; S = Image.new('RGB', (NC * 164, R_ * 164), (200, 200, 200))
    for k, t in enumerate(tiles): S.paste(t, ((k % NC) * 164, (k // NC) * 164))
    S.save(out); print(out, S.size)
