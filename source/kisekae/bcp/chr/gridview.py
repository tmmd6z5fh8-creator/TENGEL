# 見なおし用：元の 絵に キャラの さかい（水色）と 50px の ます目（10px ごとの 目もり）を かいて、box の 所を 切りだす
#   python3 gridview.py <出す png> <chr の 出力> <元の clean.png> <box x0,y0,x1,y1> [倍率]
import sys, json, os
import numpy as np, cv2
from PIL import Image, ImageDraw
out, O, cl, box = sys.argv[1:5]; z = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
x0, y0, x1, y1 = [int(v) for v in box.split(',')]
c = json.load(open(os.path.join(O, 'cfg.json')))
src = np.asarray(Image.open(cl).convert('RGB')).astype(np.float32)
im = src.copy()
COL = [(0, 255, 255), (255, 0, 255), (255, 255, 0), (0, 255, 0), (255, 128, 0), (128, 128, 255), (255, 80, 80), (255, 255, 255)]
for i, p in enumerate(c['parts']):
    a = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127
    e = a & ~cv2.erode(a.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    im[e] = COL[i % len(COL)]
I = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).crop((x0, y0, x1, y1))
if z != 1.0: I = I.resize((int(I.width * z), int(I.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(I)
for gx in range((x0 // 50 + 1) * 50, x1, 50):
    X = (gx - x0) * z; d.line([(X, 0), (X, I.height)], fill=(255, 255, 255) if gx % 100 == 0 else (150, 150, 150), width=1)
    d.text((X + 2, 2), str(gx), fill=(255, 255, 0))
for gy in range((y0 // 50 + 1) * 50, y1, 50):
    Y = (gy - y0) * z; d.line([(0, Y), (I.width, Y)], fill=(255, 255, 255) if gy % 100 == 0 else (150, 150, 150), width=1)
    d.text((2, Y + 2), str(gy), fill=(255, 255, 0))
I.save(out); print(out, I.size, [p['id'] for p in c['parts']])
