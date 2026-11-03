# 結果ボードカスタム（絵の ボード）：紺の 上に 描いて ある 飾り（星 など）を すき通しの PNG に 切り出す
#   python3 bcp_cutout.py <デザインの フォルダ>   → cfg の cutout ごとに <name>.png（cfg['cutout'] = [{name, rect:[x0,y0,x1,y1], chan:'R', ref:245}]）
import json, os, sys
import numpy as np, cv2
from PIL import Image
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
src = np.asarray(Image.open(os.path.join(D, cfg.get('src', 'src.png'))).convert('RGB')).astype(np.float32)
for c in cfg.get('cutout', []):
    x0, y0, x1, y1 = c['rect']
    p = src[y0:y1, x0:x1].copy()
    # 地の 紺：まわりの はしの 色の 中央値
    edge = np.concatenate([p[:3].reshape(-1, 3), p[-3:].reshape(-1, 3), p[:, :3].reshape(-1, 3), p[:, -3:].reshape(-1, 3)])
    bg = np.median(edge, 0)
    ch = 'RGB'.index(c.get('chan', 'R'))
    ref = c.get('ref', 245.0)
    a = np.clip((p[..., ch] - bg[ch]) / max(ref - bg[ch], 1), 0, 1)
    a = np.clip(a * c.get('gain', 1.15), 0, 1)
    col = (p - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 1e-3)
    col = np.clip(col, 0, 255)
    # はしは すき通しに（となりの 飾りの かけらを 入れない）
    fe = c.get('feather', 3)
    m = np.ones_like(a); m[:fe] = np.linspace(0, 1, fe)[:, None]; m[-fe:] = np.linspace(1, 0, fe)[:, None]
    m[:, :fe] *= np.linspace(0, 1, fe)[None]; m[:, -fe:] *= np.linspace(1, 0, fe)[None]
    for ex in c.get('exclude', []):                 # ほかの 飾り（紙ふぶき など）は 入れない
        ex0, ey0, ex1, ey1 = ex; m[max(0, ey0 - y0):max(0, ey1 - y0), max(0, ex0 - x0):max(0, ex1 - x0)] = 0
    rgba = np.dstack([col, a * m * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(D, c['name'] + '.png'))
    print('cutout', c['name'], p.shape[1], 'x', p.shape[0], 'bg', bg.astype(int).tolist())
