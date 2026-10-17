"""黒板：チョークでかいた走る馬と、予想のメモ・星や矢印（780×320）"""
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
rng = np.random.default_rng(191)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
img = np.broadcast_to(hexc('#24423A'), (Hh, W, 3)).copy()
smudge = fbm(Hh, W, 120, 4, seed=2)
img = img * (0.92 + 0.16 * smudge)[..., None]
for i in range(30):                                     # 消したあとの白いもや
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    img = over(img, hexc('#6E8A80'), soft_circle(Hh, W, x, y, rng.uniform(20, 60), 30) * 0.08)
chalk_tex = (fbm(Hh, W, 3, 2, seed=5) > 0.38).astype(np.float32)


def chalk(img, mask, col='#F2F1E8', k=0.92):
    m = np.clip(mask, 0, 1) * (0.55 + 0.45 * chalk_tex)
    return over(img, hexc(col), m * k)


# チョークの馬（右向き・走る）
pose = dict(Hm.GALLOP)
e, t = frame_horse(pose, (300, 40, 600, 250), W, Hh, facing='right', azim=8, elev=4)
R = render_horse(pose, e, t, 26, W, Hh, ss=2, name='chalk')
hair, ha = mane_tail(R, (Hh, W), '#FFFFFF', '#FFFFFF', mode='flow', scale=1.3, seed=8, wind_ang=math.pi, tail_len=1.2)
ln = edges(R, width=3, crease=0.3)
hl = cv2.dilate(cv2.morphologyEx((ha > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)), np.ones((2, 2), np.uint8))
n = R['n']; A = R['a']
l = np.sum(n * nrm((0.3, 0.8, 0.5)), -1)
hatch = ((np.sin((xx - yy) * 0.55) > 0.82) & (l < 0.25)).astype(np.float32) * (A > .5)
img = chalk(img, hatch, k=0.55)
img = chalk(img, ln + hl, k=0.95)
mane_fill = ((np.sin((xx * 0.25 + yy * 1.2)) > 0.3) * (ha > .5)).astype(np.float32)
img = chalk(img, mane_fill, k=0.7)
gy_ = max(p[1] for p in R['hooves']) + 6
cv2.line(img, (300, int(gy_)), (620, int(gy_)), (0.85, 0.85, 0.8), 2, cv2.LINE_AA)
# メモ（チョークの字）
pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
d = ImageDraw.Draw(pil)
F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
d.text((26, 30), '本日の◎', font=ImageFont.truetype(F, 34), fill=(246, 226, 127))
d.text((30, 86), '①→②→③', font=ImageFont.truetype(F, 24), fill=(242, 241, 232))
d.text((30, 128), 'がんばれ！', font=ImageFont.truetype(F, 24), fill=(244, 166, 192))
d.ellipse((640, 40, 740, 140), outline=(242, 241, 232), width=4)
d.text((690, 90), '1着', font=ImageFont.truetype(F, 30), fill=(246, 226, 127), anchor='mm')
txt = np.asarray(pil).astype(np.float32) / 255
diff = np.abs(txt - img).max(-1) > 0.05
img = np.where(diff[..., None], img * (1 - 0.0) + (txt - img) * (0.55 + 0.45 * chalk_tex)[..., None], img)
# 矢印・星
st = np.zeros((Hh, W), np.float32)
cv2.arrowedLine(st, (210 * 4, 200 * 4), (290 * 4, 160 * 4), 1.0, 12, cv2.LINE_AA, shift=2, tipLength=0.25)
for (x, y, s) in [(120, 230, 14), (660, 220, 12), (230, 60, 10)]:
    pts = np.array([(x + math.cos(-math.pi / 2 + j * math.pi * 4 / 5) * s, y + math.sin(-math.pi / 2 + j * math.pi * 4 / 5) * s) for j in range(6)])
    cv2.polylines(st, [np.round(pts * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
img = chalk(img, st, '#F2F1E8', 0.85)
# 下の木の枠と、チョーク
img = over(img, hexc('#8A5A2B'), np.clip((yy - 300) / 1.2 + .5, 0, 1))
img = over(img, hexc('#6E4520'), np.clip((yy - 300) / 1.2 + .5, 0, 1) * np.clip((yy - 312), 0, 1))
for (x, c) in [(520, '#F2F1E8'), (560, '#F6E27F'), (590, '#F4A6C0')]:
    m = np.zeros((Hh, W), np.float32)
    cv2.rectangle(m, (x * 4, 292 * 4), ((x + 26) * 4, 300 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    img = over(img, hexc(c), m)
save_webp(np.clip(img, 0, 1), out)
print(out)
