# 見なおし用：キャラごとに「キャラなしの 背景」を 切りだして ならべる（ぬいた 所の さかいを 赤い 線で）
#   背景に のこった ひづめ・耳・しっぽ・腕の かけら（＝動くと 体から はなれて 見える 所）を さがす
#   python3 leftover.py <出す png> <chr の 出力> <元の clean.png> [タイルの 大きさ] [ならべる 数]
import sys, json, os
import numpy as np, cv2
from PIL import Image, ImageDraw
out, O, cl = sys.argv[1:4]; T = int(sys.argv[4]) if len(sys.argv) > 4 else 300; NC = int(sys.argv[5]) if len(sys.argv) > 5 else 4
c = json.load(open(os.path.join(O, 'cfg.json')))
src = np.asarray(Image.open(cl).convert('RGB')).astype(np.int32)
bg = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.int32)
H, W = src.shape[:2]
hole = (np.abs(src - bg).max(-1) > 2).astype(np.uint8)
hole = cv2.morphologyEx(hole, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
edge = hole.astype(bool) & ~cv2.erode(hole, np.ones((3, 3), np.uint8)).astype(bool)
vis = bg.copy(); vis[edge] = [255, 40, 40]
tiles = []
for p in c['parts']:
    a = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127
    ys, xs = np.where(a)
    if not len(xs): continue
    x0, y0, x1, y1 = max(0, xs.min() - 30), max(0, ys.min() - 30), min(W, xs.max() + 30), min(H, ys.max() + 30)
    im = Image.fromarray(vis[y0:y1, x0:x1].astype(np.uint8))
    s = T / max(im.width, im.height); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    t = Image.new('RGB', (T, T + 16), 'white'); t.paste(im, (0, 16)); d = ImageDraw.Draw(t); d.text((3, 2), f"{p['id']} {x0},{y0}-{x1},{y1} x{s:.2f}", fill=(0, 0, 0))
    tiles.append(t)
R = (len(tiles) + NC - 1) // NC
S = Image.new('RGB', (NC * (T + 6), R * (T + 22)), 'white')
for k, t in enumerate(tiles): S.paste(t, ((k % NC) * (T + 6), (k // NC) * (T + 22)))
S.save(out); print(out, S.size)
