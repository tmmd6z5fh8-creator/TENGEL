# 見なおし用：ヒラヒラ（sway）の キャラを 大きめに 回して かさねる（2つの 向き）・キャラなしの 背景と ならべる
#   python3 sway_sheet.py <出す png> <box x0,y0,x1,y1> <幅> [--k 2] <chr の 出力> …
import sys, json, os
import numpy as np, cv2
from PIL import Image
a = sys.argv[1:]
K = 2.0
if '--k' in a: i = a.index('--k'); K = float(a[i + 1]); del a[i:i + 2]
out, box, W_ = a[0], [int(v) for v in a[1].split(',')], int(a[2])
cols = []
for O in a[3:]:
    c = json.load(open(os.path.join(O, 'cfg.json'))); mo = json.load(open(os.path.join(O, 'motion.json')))
    mop = {p['id']: p for p in mo['parts']}
    bg = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.float32); H, W = bg.shape[:2]
    frames = [bg]
    for sgn in (1, -1):
        comp = bg.copy()
        for j, p in enumerate(c['parts']):
            L = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA')).astype(np.float32)
            m = mop.get(p['id'], {}); ox, oy = m.get('o', [W / 2, H / 2])
            ang = sgn * (1 if j % 2 == 0 else -1) * m.get('sw', 3.0) * K
            R = cv2.getRotationMatrix2D((float(ox), float(oy)), ang, 1.0)
            pm = np.dstack([L[..., :3] * (L[..., 3:4] / 255), L[..., 3]])
            w = cv2.warpAffine(pm, R, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
            comp = w[..., :3] + comp * (1 - w[..., 3:4] / 255)
        frames.append(comp)
    col = []
    for t in frames:
        im = Image.fromarray(np.clip(t, 0, 255).astype(np.uint8)).crop(box); s = W_ / im.width; col.append(im.resize((W_, int(im.height * s)), Image.LANCZOS))
    T = Image.new('RGB', (W_, sum(t.height for t in col) + 6 * (len(col) - 1)), 'white'); y = 0
    for t in col: T.paste(t, (0, y)); y += t.height + 6
    cols.append(T)
S = Image.new('RGB', (len(cols) * (W_ + 8) - 8, cols[0].height), 'white')
for k, t in enumerate(cols): S.paste(t, (k * (W_ + 8), 0))
S.save(out); print(out, S.size)
