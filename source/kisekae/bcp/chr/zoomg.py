# 見なおし用：いくつかの 所を 拡大（元の 絵＋キャラの さかい（水色）＋10px の ます目｜キャラなしの 背景＋ます目）
#   python3 zoomg.py <出す png> <倍率> <chr の 出力>:<元の clean.png>:<x0,y0,x1,y1> …
import sys, json, os
import numpy as np, cv2
from PIL import Image, ImageDraw
out, z = sys.argv[1], float(sys.argv[2]); rows = []
def grid(I, x0, y0, x1, y1):
    d = ImageDraw.Draw(I, 'RGBA')
    for gx in range((x0 // 10 + 1) * 10, x1, 10):
        X = (gx - x0) * z; d.line([(X, 0), (X, I.height)], fill=(255, 255, 255, 170) if gx % 50 == 0 else (255, 255, 255, 55), width=1)
        if gx % 50 == 0: d.text((X + 2, 1), str(gx), fill=(255, 255, 0, 255))
    for gy in range((y0 // 10 + 1) * 10, y1, 10):
        Y = (gy - y0) * z; d.line([(0, Y), (I.width, Y)], fill=(255, 255, 255, 170) if gy % 50 == 0 else (255, 255, 255, 55), width=1)
        if gy % 50 == 0: d.text((1, Y + 1), str(gy), fill=(255, 255, 0, 255))
for a in sys.argv[3:]:
    O, cl, b = a.split(':'); x0, y0, x1, y1 = [int(v) for v in b.split(',')]
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(cl).convert('RGB')).astype(np.float32)
    bg = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.float32)
    im = src.copy()
    for p in c['parts']:
        al = (np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127).astype(np.uint8)
        e = al.astype(bool) & ~cv2.erode(al, np.ones((3, 3), np.uint8)).astype(bool); im[e] = (0, 255, 255)
    A = Image.fromarray(np.clip(im[y0:y1, x0:x1], 0, 255).astype(np.uint8)); B = Image.fromarray(np.clip(bg[y0:y1, x0:x1], 0, 255).astype(np.uint8))
    A = A.resize((int(A.width * z), int(A.height * z)), Image.LANCZOS); B = B.resize(A.size, Image.LANCZOS)
    grid(A, x0, y0, x1, y1); grid(B, x0, y0, x1, y1)
    R = Image.new('RGB', (A.width * 2 + 6, A.height + 14), 'white'); R.paste(A, (0, 14)); R.paste(B, (A.width + 6, 14))
    ImageDraw.Draw(R).text((2, 1), f'{O.split("/")[-1]} {b}', fill=(0, 0, 0)); rows.append(R)
NC = int(os.environ.get('NC', '2'))
cw = max(r.width for r in rows); rh = max(r.height for r in rows); NR = (len(rows) + NC - 1) // NC
T = Image.new('RGB', (NC * (cw + 8), NR * (rh + 8)), (220, 220, 220))
for i, r in enumerate(rows): T.paste(r, ((i % NC) * (cw + 8), (i // NC) * (rh + 8)))
T.save(out); print(out, T.size)
