"""競馬新聞：新聞紙の上に、版画のような線で描いた走る馬・題字・予想の印の表（780×320）"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(111)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
paper = hexc('#F1ECDF')
img = np.broadcast_to(paper, (Hh, W, 3)).copy()
img = img * (0.96 + 0.04 * blur(rng.random((Hh, W)).astype(np.float32), 1.2))[..., None]

# 版画風の馬（右向き・走る）：明るい所は白、半分の所は斜線、暗い所は交差線
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (250, 58, 560, 286), W, Hh, facing='right', azim=8, elev=4)
R = render_horse(pose, e, t, 26, W, Hh, ss=2, name='news')
n = R['n']; A = R['a']
L = nrm((0.4, 0.85, 0.45))
l = np.sum(n * L, -1)
a_ = (A > .5).astype(np.float32)
l = blur(l * a_, 3) / np.maximum(blur(a_, 3), 1e-3)
h1 = (np.sin((xx + yy) * 0.9) > 0.35).astype(np.float32)
h2 = (np.sin((xx - yy) * 0.9) > 0.35).astype(np.float32)
ink = np.zeros((Hh, W), np.float32)
ink = np.maximum(ink, h1 * (l < 0.55))
ink = np.maximum(ink, h2 * (l < 0.15))
ink = np.maximum(ink, (l < -0.25).astype(np.float32) * 0.9)
p = world_pos(R)
legs = np.nan_to_num((p[..., 1] - R['S']['ground']) < 0.40)
ink = np.maximum(ink, legs * 0.95)
ink *= a_
hair, ha = mane_tail(R, (Hh, W), '#000000', '#000000', mode='flow', scale=1.3, seed=8, wind_ang=math.pi, tail_len=1.15)
ln = edges(R, width=2)
img = over(img, hexc('#FFFFFF'), A * 0.9)
img = over(img, hexc('#151515'), np.clip(ink, 0, 1))
img = over(img, hexc('#151515'), ha)
streak = (np.sin((xx * 0.2 + yy * 1.4)) > 0.7).astype(np.float32) * ha
img = over(img, hexc('#F1ECDF'), streak * 0.6)
img = over(img, hexc('#151515'), ln * A)
img = over(img, hexc('#151515'), cv2.GaussianBlur(cv2.morphologyEx((ha > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)), (3, 3), .6))

pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
d = ImageDraw.Draw(pil)
INK = (21, 21, 21); RED = (200, 30, 30); GREY = (120, 116, 108)
# 題字
d.rectangle((14, 14, 236, 76), fill=INK)
d.text((125, 45), 'テンゲル競馬', font=ImageFont.truetype(SERIF, 30), fill=(241, 236, 223), anchor='mm')
d.line((14, 84, 236, 84), fill=INK, width=3); d.line((14, 89, 236, 89), fill=INK, width=1)
d.text((16, 98), '本紙予想', font=ImageFont.truetype(SERIF, 24), fill=INK)
d.ellipse((136, 94, 176, 134), outline=RED, width=5)
d.ellipse((147, 105, 165, 123), outline=RED, width=4)
d.text((186, 114), '本命', font=ImageFont.truetype(SERIF, 20), fill=RED, anchor='lm')
for i in range(9):                                     # 記事の文字（灰色の線）
    y = 148 + i * 17
    w_ = rng.uniform(150, 214)
    d.rectangle((16, y, 16 + w_, y + 7), fill=GREY)
# 印の表（馬柱ふう）
x0, y0, cw, ch = 590, 16, 30, 48
marks = ['◎', '○', '▲', '△', '', '☆']
for c in range(6):
    x = x0 + c * cw
    d.rectangle((x, y0, x + cw, y0 + ch * 6), outline=INK, width=1)
    d.text((x + cw / 2, y0 + 14), str(c + 1), font=ImageFont.truetype(SANS, 18), fill=INK, anchor='mm')
    mk = marks[c]
    if mk:
        d.text((x + cw / 2, y0 + 46), mk, font=ImageFont.truetype(SANS, 20), fill=RED if c < 2 else INK, anchor='mm')
    for r in range(2, 6):
        yy0 = y0 + r * ch
        d.line((x, yy0, x + cw, yy0), fill=INK, width=1)
        for q in range(3):
            d.rectangle((x + 6, yy0 + 8 + q * 12, x + cw - 6 - rng.uniform(0, 8), yy0 + 12 + q * 12), fill=GREY)
d.rectangle((x0 - 2, y0 - 2, x0 + cw * 6 + 2, y0 + ch * 6 + 2), outline=INK, width=2)
img = np.asarray(pil).astype(np.float32) / 255
save_webp(img, out)
print(out)
