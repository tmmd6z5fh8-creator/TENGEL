# 見なおし用：元の 絵 と キャラなしの 背景（ぬいた 所の さかい＝赤）を ならべて 拡大：python3 spot.py <出す png> <倍率> <chr の 出力>:<元の clean.png>:<x0,y0,x1,y1> …
import sys, numpy as np, cv2
from PIL import Image, ImageDraw
out, z = sys.argv[1], float(sys.argv[2]); rows = []
for a in sys.argv[3:]:
    O, cl, b = a.split(':'); x0, y0, x1, y1 = [int(v) for v in b.split(',')]
    src = np.asarray(Image.open(cl).convert('RGB')).astype(np.int32); bg = np.asarray(Image.open(O + '/bgx.png').convert('RGB')).astype(np.int32)
    hole = (np.abs(src - bg).max(-1) > 2).astype(np.uint8); hole = cv2.morphologyEx(hole, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    e = hole.astype(bool) & ~cv2.erode(hole, np.ones((3, 3), np.uint8)).astype(bool); v = bg.copy(); v[e] = [255, 40, 40]
    s2 = src.copy(); s2[e] = [255, 40, 40]
    A = Image.fromarray(s2[y0:y1, x0:x1].astype(np.uint8)); B = Image.fromarray(v[y0:y1, x0:x1].astype(np.uint8))
    A = A.resize((int(A.width * z), int(A.height * z)), Image.LANCZOS); B = B.resize(A.size, Image.LANCZOS)
    R = Image.new('RGB', (A.width * 2 + 6, A.height + 14), 'white'); R.paste(A, (0, 14)); R.paste(B, (A.width + 6, 14)); ImageDraw.Draw(R).text((2, 1), f'{O.split("/")[-1]} {b}', fill=(0, 0, 0)); rows.append(R)
W = max(r.width for r in rows); T = Image.new('RGB', (W, sum(r.height for r in rows) + 6 * len(rows)), 'white'); y = 0
for r in rows: T.paste(r, (0, y)); y += r.height + 6
T.save(out); print(out, T.size)
