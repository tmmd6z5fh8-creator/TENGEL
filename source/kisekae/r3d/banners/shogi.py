"""将棋：榧の盤の上の「桂馬」の駒（大きく）と「歩兵」の駒（780×320）"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from paint import fbm, warp

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(141)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'
# 盤（木目）
g = fbm(Hh, W, 90, 4, seed=1)
grain = np.sin((yy * 0.35 + warp(g, (fbm(Hh, W, 120, 3, seed=2) - .5) * 40, xx * 0) * 30)) * 0.5 + 0.5
wood = hexc('#E9C27A') * (0.92 + 0.08 * grain)[..., None] * (0.96 + 0.06 * fbm(Hh, W, 20, 3, seed=3))[..., None]
img = wood.copy()
# 線（ます目）と星
for k in range(-2, 12):
    x = 30 + k * 76
    cv2.line(img, (int(x * 16), 0), (int(x * 16 - 120 * 16), Hh * 16), (0.18, 0.12, 0.06), 2, cv2.LINE_AA, shift=4)
for j in range(0, 6):
    y = 10 + j * 62
    cv2.line(img, (0, int(y * 16)), (W * 16, int(y * 16)), (0.18, 0.12, 0.06), 2, cv2.LINE_AA, shift=4)


def koma(img, cx, cy, w, h, rot, text, size):
    """駒：五角形・厚み・文字（縦書き）"""
    pts = np.array([(0, -h / 2), (w * 0.42, -h * 0.30), (w / 2, h / 2), (-w / 2, h / 2), (-w * 0.42, -h * 0.30)])
    c, s = math.cos(rot), math.sin(rot)
    P = lambda q: np.array([(cx + x * c - y * s, cy + x * s + y * c) for x, y in q])
    sh = P(pts + np.array([6, 10]))
    img = over(img, hexc('#5A3A16'), blur(poly_aa((Hh, W), [sh]), 4) * 0.45)
    side = P(pts + np.array([0, 7]))
    img = over(img, hexc('#B8873E'), poly_aa((Hh, W), [side]))
    top = poly_aa((Hh, W), [P(pts)])
    kw = hexc('#F2D6A0') * (0.94 + 0.06 * grain)[..., None]
    img = over(img, kw, top)
    inner = poly_aa((Hh, W), [P(pts * 0.9)])
    img = over(img, hexc('#E8C88A'), (top - inner).clip(0, 1) * 0.6)
    # 文字（回転してのせる）
    tile = Image.new('L', (int(w * 2), int(h * 2)), 0)
    dd = ImageDraw.Draw(tile)
    f = ImageFont.truetype(SERIF, int(size))
    for i, ch in enumerate(text):
        dd.text((w, h * 0.78 + (i - (len(text) - 1) / 2) * size * 1.02), ch, font=f, fill=255, anchor='mm')
    tile = tile.rotate(-math.degrees(rot), resample=Image.BICUBIC, center=(w, h))
    tm = np.zeros((Hh, W), np.float32)
    ta = np.asarray(tile).astype(np.float32) / 255
    x0, y0 = int(cx - w), int(cy - h * 0.78)
    xs0, ys0 = max(0, -x0), max(0, -y0)
    x1, y1 = min(W, x0 + ta.shape[1]), min(Hh, y0 + ta.shape[0])
    tm[max(0, y0):y1, max(0, x0):x1] = ta[ys0:ys0 + (y1 - max(0, y0)), xs0:xs0 + (x1 - max(0, x0))]
    img = over(img, hexc('#1A120C'), tm * top)
    return img


img = koma(img, 600, 170, 104, 128, 0.12, '歩兵', 40)
img = koma(img, 360, 168, 170, 210, -0.10, '桂馬', 66)
# 光（左上から）
light = np.exp(-(((xx - 200) / 500) ** 2 + ((yy + 50) / 300) ** 2)) * 0.12
img = np.clip(img + light[..., None], 0, 1)
save_webp(img, out)
print(out)
