"""水墨画：和紙に墨でえがいた、駆ける馬と遠くの山・赤い落款（780×320）"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from paint import fbm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(121)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = np.broadcast_to(hexc('#F5F0E4'), (Hh, W, 3)).copy()
fib = fbm(Hh, W, 30, 4, seed=3)
img = img * (0.95 + 0.05 * fib)[..., None]
for i in range(160):                                   # 和紙の繊維
    x, y = rng.uniform(0, W), rng.uniform(0, Hh); a = rng.uniform(0, math.pi); L = rng.uniform(6, 22)
    cv2.line(img, (int(x * 16), int(y * 16)), (int((x + math.cos(a) * L) * 16), int((y + math.sin(a) * L) * 16)), (0.86, 0.83, 0.76), 1, cv2.LINE_AA, shift=4)
INK = hexc('#1C1A18')


def wash(img, mask, k):
    return img * (1 - mask[..., None] * k) + INK * (mask[..., None] * k)


# 遠くの山（にじむ墨）
for y0, amp, k, f, sd in [(150, 50, 0.16, 140, 1), (190, 36, 0.26, 90, 2)]:
    ridge = y0 - amp * np.abs(np.sin(xx / f + sd)) - 12 * np.sin(xx / 33 + sd)
    m = np.clip((yy - ridge) / 3 + .5, 0, 1) * np.clip(1 - (yy - ridge) / 70, 0, 1)
    m = blur(m, 2) * (0.75 + 0.25 * fbm(Hh, W, 40, 3, seed=sd + 5))
    img = wash(img, m, k)

# 墨の馬（左向き・走る）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (250, 50, 590, 268), W, Hh, facing='left', azim=-8, elev=4)
R = render_horse(pose, e, t, 26, W, Hh, ss=2, name='ink')
A = R['a']; n = R['n']
l = np.sum(n * nrm((-0.3, 0.8, -0.5)), -1)
a_ = (A > .5).astype(np.float32)
l = blur(l * a_, 4) / np.maximum(blur(a_, 4), 1e-3)
tone = np.clip(0.18 + (0.6 - l) * 0.55, 0.12, 0.95) * A
dry = fbm(Hh, W, 6, 3, seed=9)
tone = tone * (0.8 + 0.35 * dry)
img = wash(img, blur(tone, 0.8), 0.9)
ln = edges(R, width=3)
ln = ln * (fbm(Hh, W, 18, 3, seed=11) > 0.32)
img = wash(img, ln * A, 0.95)
hair, ha = mane_tail(R, (Hh, W), '#000000', '#000000', mode='flow', scale=1.45, seed=6, wind_ang=0.0, tail_len=1.3)
brush = ha * (0.75 + 0.35 * (np.sin(xx * 0.3 + yy * 1.2 + fbm(Hh, W, 10, 2, seed=4) * 6) > -0.2))
img = wash(img, np.clip(brush, 0, 1), 0.95)
# 地面の筆
gr = np.exp(-((yy - (max(p[1] for p in R['hooves']) + 4)) / 4) ** 2) * np.clip(1 - np.abs(xx - 420) / 300, 0, 1)
img = wash(img, gr * (fbm(Hh, W, 12, 3, seed=13) > 0.4), 0.6)
# 墨のしぶき
for i in range(16):
    x, y = rng.uniform(150, 650), rng.uniform(40, 300)
    m = soft_circle(Hh, W, x, y, rng.uniform(0.8, 3.0), 1.0)
    img = wash(img, m, 0.85)
# 落款（赤い四角に白い「馬」）
pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
d = ImageDraw.Draw(pil)
x0, y0, s = 660, 210, 58
d.rectangle((x0, y0, x0 + s, y0 + s), fill=(183, 40, 46))
d.text((x0 + s / 2, y0 + s / 2 + 2), '馬', font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc', 44), fill=(245, 240, 228), anchor='mm')
img = np.asarray(pil).astype(np.float32) / 255
grain = blur(rng.random((Hh, W)).astype(np.float32), 0.8)
seal = np.zeros((Hh, W), np.float32); seal[y0:y0 + s, x0:x0 + s] = 1
img = img + ((grain > 0.62) * seal * 0.25)[..., None]
save_webp(np.clip(img, 0, 1), out)
print(out)
