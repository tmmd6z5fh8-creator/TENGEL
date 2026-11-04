# 見なおし用：細かい ます目（10px・50px ごとに 数字）を かいた 切りだし：python3 finegrid.py <出す png> <倍率> <x0,y0,x1,y1> <絵> [<絵> …]（よこに ならべる）
import sys
from PIL import Image, ImageDraw
out, z, box = sys.argv[1], float(sys.argv[2]), [int(v) for v in sys.argv[3].split(',')]
x0, y0, x1, y1 = box; tiles = []
for f in sys.argv[4:]:
    I = Image.open(f).convert('RGB').crop(box); I = I.resize((int(I.width * z), int(I.height * z)), Image.LANCZOS); d = ImageDraw.Draw(I, 'RGBA')
    for gx in range((x0 // 10 + 1) * 10, x1, 10):
        X = (gx - x0) * z; d.line([(X, 0), (X, I.height)], fill=(255, 255, 255, 200) if gx % 50 == 0 else (255, 255, 255, 60), width=1)
        if gx % 50 == 0: d.text((X + 2, 2), str(gx), fill=(255, 255, 0, 255))
    for gy in range((y0 // 10 + 1) * 10, y1, 10):
        Y = (gy - y0) * z; d.line([(0, Y), (I.width, Y)], fill=(255, 255, 255, 200) if gy % 50 == 0 else (255, 255, 255, 60), width=1)
        if gy % 50 == 0: d.text((2, Y + 2), str(gy), fill=(255, 255, 0, 255))
    tiles.append(I)
T = Image.new('RGB', (sum(t.width for t in tiles) + 8 * (len(tiles) - 1), tiles[0].height), 'white'); x = 0
for t in tiles: T.paste(t, (x, 0)); x += t.width + 8
T.save(out); print(out, T.size)
