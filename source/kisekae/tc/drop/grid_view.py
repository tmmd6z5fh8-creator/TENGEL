# 正面の 絵に 目もり（台の 座標）を つける：<npz> <出力> x0 x1 y0 y1 [倍]
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import hmap as HM
d = np.load(sys.argv[1]); out = sys.argv[2]
x0, x1, y0, y1 = [float(v) for v in sys.argv[3:7]]; K = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
step = float(sys.argv[8]) if len(sys.argv) > 8 else 0.05
alb = d['alb'].astype(np.float32) / 255
srgb = np.where(alb <= 0.0031308, alb * 12.92, 1.055 * np.power(np.maximum(alb, 1e-6), 1 / 2.4) - 0.055)
a = d['a'][..., None]
img = (np.clip(srgb * a + 0.9 * (1 - a), 0, 1) * 255).astype(np.uint8)
PX = HM.PX
c0, c1 = int((x0 - HM.X0) * PX), int((x1 - HM.X0) * PX); r0, r1 = int((HM.Y1 - y1) * PX), int((HM.Y1 - y0) * PX)
im = Image.fromarray(img[r0:r1, c0:c1]).resize((int((c1 - c0) * K), int((r1 - r0) * K)), Image.LANCZOS)
dr = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 16, index=0)
v = np.ceil(x0 / step) * step
while v < x1:
    X = (v - x0) * PX * K
    dr.line((X, 0, X, im.height), fill=(255, 0, 0) if abs(v) < 1e-9 else (0, 0, 0), width=1); dr.text((X + 2, 2), f'{v:+.2f}', font=f, fill=(200, 0, 0)); v += step
v = np.ceil(y0 / step) * step
while v < y1:
    Y = (y1 - v) * PX * K
    dr.line((0, Y, im.width, Y), fill=(0, 0, 0), width=1); dr.text((2, Y + 2), f'{v:+.2f}', font=f, fill=(0, 0, 200)); v += step
im.save(out); print(im.size)
