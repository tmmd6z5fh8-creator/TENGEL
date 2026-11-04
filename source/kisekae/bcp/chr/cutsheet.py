# 切りぬきの 見本：キャラごとに 色を つけた 絵（上）と キャラなしの 背景（下）を 段ごとに ならべる
#   python3 cutsheet.py <出す png> <box x0,y0,x1,y1> <幅> <chr の 出力>:<元の clean.png> …
import sys, json, os
import numpy as np
from PIL import Image
out, box, W_ = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], int(sys.argv[3])
COL = [(255, 80, 200), (255, 220, 40), (60, 220, 90), (60, 140, 255), (255, 60, 60), (160, 90, 255), (255, 150, 40), (40, 230, 230)]
tiles = []
for arg in sys.argv[4:]:
    O, cl = arg.split(':')
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(cl).convert('RGB')).astype(np.float32); ov = src * 0.5
    for i, p in enumerate(c['parts']):
        L = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA')).astype(np.float32); a = L[..., 3:4] / 255
        ov = ov * (1 - a) + (src * 0.45 + np.array(COL[i % len(COL)]) * 0.55) * a
    bg = Image.open(os.path.join(O, 'bgx.png')).convert('RGB')
    t1 = Image.fromarray(np.clip(ov, 0, 255).astype(np.uint8)).crop(box); t2 = bg.crop(box)
    s = W_ / t1.width
    t1 = t1.resize((W_, int(t1.height * s)), Image.LANCZOS); t2 = t2.resize((W_, int(t2.height * s)), Image.LANCZOS)
    t = Image.new('RGB', (W_, t1.height * 2 + 6), 'white'); t.paste(t1, (0, 0)); t.paste(t2, (0, t1.height + 6)); tiles.append(t)
S = Image.new('RGB', (len(tiles) * (W_ + 8), tiles[0].height), 'white')
for k, t in enumerate(tiles): S.paste(t, (k * (W_ + 8), 0))
S.save(out); print(out, S.size)
