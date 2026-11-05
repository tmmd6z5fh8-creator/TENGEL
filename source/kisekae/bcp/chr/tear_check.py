# 見なおし用：キャラの 絵の ふちが 絵の ふち線（はっきりした さかい）では なく、なめらかな 所（布・雲・毛の 中）を 通って いる 所＝動くと「切れて」見える 所 を さがす
#   python3 tear_check.py <出す png> <chr の 出力> … [--g 0.05] [--min 14] [--dif 14]
#   ふち（キャラの 絵の すき通しが 0.5 の さかい）で：まわり 2px の 絵の ふちの 強さ（sobel）が g より 小さく、
#   すぐ 内がわ（2〜5px）で 元の 絵と キャラなしの 背景が ちがう（dif より 大きい：動くと ちがう 色が 見える）所が min px 以上 つづく
#   のぞく 所：絵の はし・ほかの キャラとの さかい・ボードの 前に 重ねる 所（occl）
import sys, json, os
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image, ImageDraw
from skimage.filters import sobel
a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = float(a[i + 1]); del a[i:i + 2]; return v
    return d
GT, MIN, DIF = opt('--g', 0.05), opt('--min', 14), opt('--dif', 14)
out = a[0]; tiles = []; summary = []
for O in a[1:]:
    c = json.load(open(os.path.join(O, 'cfg.json')))
    img = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.float32); H, W = img.shape[:2]
    bgx = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.float32)
    g = np.max(np.stack([sobel(cv2.GaussianBlur(img[..., k] / 255, (0, 0), 0.8)) for k in range(3)]), 0)
    gmax = ndi.maximum_filter(g, size=5)
    dif = np.abs(img - bgx).max(-1)
    A = {}; AL = {}
    for p in c['parts']:
        AL[p['id']] = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3].astype(np.float32) / 255
        A[p['id']] = AL[p['id']] > 0.5
    occ = np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')) > 127 if os.path.exists(os.path.join(O, 'occl.png')) else np.zeros((H, W), bool)
    border = np.zeros((H, W), bool); border[:3, :] = border[-3:, :] = True; border[:, :3] = border[:, -3:] = True
    tot = 0; places = []
    for pid, m in A.items():
        others = np.zeros((H, W), bool)
        for q, mm in A.items():
            if q != pid: others |= mm
        er = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        bd = m & ~er
        outside = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m
        ok_out = outside & ~others & ~occ & ~border
        bd &= cv2.dilate(ok_out.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        inner = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~cv2.erode(m.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
        difn = ndi.maximum_filter(np.where(inner, dif, 0), size=9)
        hardn = ndi.maximum_filter(AL[pid], size=5) - ndi.minimum_filter(AL[pid], size=5)   # かたい ふち（すき通しが 2px で 0.7 より 大きく かわる）だけ
        weak = bd & (gmax < GT) & (difn > DIF) & (hardn > 0.7)
        lab, n = ndi.label(weak, structure=np.ones((3, 3)))
        if not n: continue
        sz = ndi.sum(weak, lab, range(1, n + 1))
        for k in range(n):
            if sz[k] < MIN: continue
            ys, xs = np.where(lab == k + 1); cx, cy = int(xs.mean()), int(ys.mean()); tot += int(sz[k])
            places.append((pid, cx, cy, int(sz[k])))
            r = 55; x0, y0, x1, y1 = max(0, cx - r), max(0, cy - r), min(W, cx + r), min(H, cy + r)
            v = img.copy(); e = m & ~er; v[e] = [0, 255, 255]; v[lab == k + 1] = [255, 0, 255]
            t1 = Image.fromarray(np.clip(v[y0:y1, x0:x1], 0, 255).astype(np.uint8)).resize((180, 180), Image.NEAREST)
            t2 = Image.fromarray(np.clip(bgx[y0:y1, x0:x1], 0, 255).astype(np.uint8)).resize((180, 180), Image.LANCZOS)
            t = Image.new('RGB', (364, 194), 'white'); t.paste(t1, (0, 14)); t.paste(t2, (184, 14))
            ImageDraw.Draw(t).text((2, 1), f'{os.path.basename(O)} {pid} ({cx},{cy}) {int(sz[k])}px', fill=(0, 0, 0)); tiles.append(t)
    summary.append((os.path.basename(O), tot, places))
    print(os.path.basename(O), 'tear px', tot, [(p, x, y, s) for p, x, y, s in sorted(places, key=lambda t: -t[3])][:10])
if tiles:
    NC = 4; R = (len(tiles) + NC - 1) // NC; S = Image.new('RGB', (NC * 368, R * 198), (210, 210, 210))
    for k, t in enumerate(tiles): S.paste(t, ((k % NC) * 368, (k // NC) * 198))
    S.save(out); print(out, S.size, len(tiles))
