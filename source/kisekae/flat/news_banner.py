"""競馬新聞の絵（780×320）：新聞紙・題字・本紙予想・記事の行・印の表は前の newspaper.py のまま、馬だけ描き直す
   墨の筆で描いた、全力で走る競走馬（flat/ink_horse.py）。墨の黒1色（新聞の黒）で、ふちは筆のかすれ、
   たてがみ・しっぽ・ひづめは穂先の割れた筆の線
   python3 flat/news_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ink_horse import *

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(111)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
paper = hexc('#F1ECDF')
img = np.broadcast_to(paper, (Hh, W, 3)).copy()
img = img * (0.96 + 0.04 * blur(rng.random((Hh, W)).astype(np.float32), 1.2))[..., None]

# ---------- 墨の馬 ----------
POSE = dict(theta=-4.0, neck_rot=-26.0, head_ang=-38.0, fore=dict(L=[-84, -22, -16, -4], R=[-112, -36, -120, -150]),
            hind=dict(L=[-120, -160, -142, -160], R=[-60, -110, -80, -56]), tail=[-168, -150])
R = render_sil(POSE, (272, 62, 560, 290), W, Hh, s=3, azim=4, elev=3, head_scale=1.15, name='news_ink')
ink = paint_ink(R, dict(seed=5, mane=1.0, tail_len=138, tail_ang=173, tail_n=6))
INKC = hexc('#151515')
img = img * (1 - (blur(ink, 1.2) * 0.10)[..., None])                 # 墨が紙に少しにじむ
img = over(img, INKC, ink)

# ---------- 題字・本紙予想・記事・印の表（前の絵と同じ） ----------
pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
d = ImageDraw.Draw(pil)
INK = (21, 21, 21); RED = (200, 30, 30); GREY = (120, 116, 108)
d.rectangle((14, 14, 236, 76), fill=INK)
d.text((125, 45), 'テンゲル競馬', font=ImageFont.truetype(SERIF, 30), fill=(241, 236, 223), anchor='mm')
d.line((14, 84, 236, 84), fill=INK, width=3); d.line((14, 89, 236, 89), fill=INK, width=1)
d.text((16, 98), '本紙予想', font=ImageFont.truetype(SERIF, 24), fill=INK)
d.ellipse((136, 94, 176, 134), outline=RED, width=5)
d.ellipse((147, 105, 165, 123), outline=RED, width=4)
d.text((186, 114), '本命', font=ImageFont.truetype(SERIF, 20), fill=RED, anchor='lm')
for i in range(9):
    y = 148 + i * 17
    w_ = rng.uniform(150, 214)
    d.rectangle((16, y, 16 + w_, y + 7), fill=GREY)
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
