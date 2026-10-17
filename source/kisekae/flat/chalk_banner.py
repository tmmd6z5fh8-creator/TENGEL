"""黒板の絵（780×320）：黒板・もや・メモの字・矢印・星・「1着」・木の枠・チョークは前の chalk.py のまま、馬だけ描き直す
   走る競走馬（3Dの馬の形・右向き＝「1着」へ向かう）＋一から作ったたてがみ・しっぽを、
   チョークでぬった形（うすく・こすった筋）＋チョークの外の線＋目と鼻の小さい線で描く
   python3 flat/chalk_banner.py <出力.webp> [形だけの見本PNG]"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm
from paint import fbm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(191)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# ---------- 黒板（前の絵と同じ） ----------
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


# ---------- 走る競走馬（形だけ使う。右向き） ----------
POSE = dict(theta=0.0, neck_rot=-38.0, head_ang=-30.0,
            fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
            hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]),
            tail=[-172, -162])
BOX = (292, 44, 612, 258)
Hm.HEAD_SCALE = 1.08
e, t = frame_horse(POSE, BOX, W, Hh, facing='right', azim=6, elev=3)
R = render_horse(POSE, e, t, 26, W, Hh, ss=2, name='chalk2')
body_a = np.clip(R['a'], 0, 1)

# たてがみ（短く、うしろへなびく）・前髪・しっぽ（うしろへ長く流れる）
hr = np.random.default_rng(23)
crest = np.asarray(R['crest'], float)
nC = len(crest)
locks = []
for i in range(3, nC - 6, 2):
    p = crest[i]
    tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
    up = math.atan2(tg[1], tg[0]) - math.pi / 2
    if math.cos(up) > 0.3:
        up += math.pi
    L = 20 + 12 * math.sin(i / nC * math.pi)
    pts = flow(p, up - 0.9, L, 8, wind=0.35, wind_ang=math.pi + 0.15, rng=hr, wave=1.0, phase=i)
    locks.append(lock_poly(pts, 9, 0.6))
pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
fd = (mz - pp) / np.linalg.norm(mz - pp)
pts = flow(pp + fd * 2, math.atan2(fd[1], fd[0]) - 1.2, 12, 6, wind=0.3, wind_ang=math.pi + 0.2, rng=hr)
locks.append(lock_poly(pts, 6, 0.6))
th_ = np.asarray(R['tail'][0], float)
for k in range(5):
    a0 = math.pi + 0.10 + (k - 2) * 0.07
    L = 96 + (2 - abs(k - 2)) * 12
    pts = flow(th_ + np.array([1.0, 2.0]), a0, L, 16, wind=0.10, wind_ang=math.pi + 0.06, rng=hr, wave=1.3, phase=k * 1.1)
    locks.append(lock_poly(pts, 15 - abs(k - 2) * 2, 0.8))
hair_a = poly_aa((Hh, W), locks)
mask = np.clip(np.maximum(body_a, hair_a), 0, 1)

# ---------- チョークでぬる（うすく・ななめにこすった筋） ----------
ang = math.radians(-28)
u = xx * math.cos(ang) + yy * math.sin(ang)
streak = 0.5 + 0.5 * np.sin(u * 0.85 + fbm(Hh, W, 18, 3, seed=7) * 7.0)
fill = mask * (0.52 + 0.22 * streak) * (0.75 + 0.25 * fbm(Hh, W, 40, 3, seed=9))
img = chalk(img, fill, k=0.84)

# ---------- チョークの外の線（なめらかに・少しかすれる） ----------
SS = 2
m2 = cv2.resize(mask, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
cs, _ = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
ln2 = np.zeros((Hh * SS, W * SS), np.float32)
for c in cs:
    if cv2.contourArea(c) < 30 * SS * SS:
        continue
    p = c[:, 0, :].astype(np.float32)
    kk = np.arange(-6, 7); g = np.exp(-(kk / 2.4) ** 2); g /= g.sum()
    ps = np.stack([np.convolve(np.r_[p[-6:, d], p[:, d], p[:6, d]], g, 'valid') for d in (0, 1)], 1)
    cv2.polylines(ln2, [(ps * 16).astype(np.int32)], True, 1.0, 3, cv2.LINE_AA, shift=4)
ln = np.clip(cv2.resize(ln2, (W, Hh), interpolation=cv2.INTER_AREA), 0, 1)
breaks = np.clip(0.55 + 0.6 * fbm(Hh, W, 9, 2, seed=11), 0, 1)              # ところどころかすれる
img = chalk(img, ln * breaks, k=0.98)

# 毛の流れ（たてがみ・しっぽの中の線）
det = np.zeros((Hh * SS, W * SS), np.float32)
for poly in locks:
    n2 = len(poly) // 2
    mid = (poly[:n2] + poly[::-1][:n2]) / 2
    cv2.polylines(det, [(mid[: int(n2 * 0.85)] * SS * 16).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA, shift=4)
det = cv2.resize(det, (W, Hh), interpolation=cv2.INTER_AREA)
img = chalk(img, det * hair_a, k=0.75)

# 目（黒板の色でぬく）・鼻の穴
ex, ey = np.asarray(R['eye'], float)[:2]
eye = soft_circle(Hh, W, ex, ey, 2.4, 0.8)
img = over(img, hexc('#24423A') * (0.92 + 0.16 * smudge)[..., None], eye * 0.95)
nx, ny = mz[:2] + (pp[:2] - mz[:2]) * 0.10
nos = np.zeros((Hh * 4, W * 4), np.float32)
cv2.ellipse(nos, (int(nx * 16), int(ny * 16)), (int(2.6 * 16), int(1.6 * 16)), math.degrees(math.atan2(fd[1], fd[0])), 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
img = over(img, hexc('#24423A'), cv2.resize(nos, (W, Hh), interpolation=cv2.INTER_AREA) * 0.8)

# 地面の線（前の絵と同じく ひづめの下）
gy_ = max(p[1] for p in R['hooves']) + 6
cv2.line(img, (300, int(gy_)), (620, int(gy_)), (0.85, 0.85, 0.8), 2, cv2.LINE_AA)

# ---------- メモ（チョークの字）・矢印・星・木の枠・チョーク（前の絵と同じ） ----------
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
st = np.zeros((Hh, W), np.float32)
cv2.arrowedLine(st, (210 * 4, 200 * 4), (290 * 4, 160 * 4), 1.0, 12, cv2.LINE_AA, shift=2, tipLength=0.25)
for (x, y, s) in [(120, 230, 14), (660, 220, 12), (230, 60, 10)]:
    pts = np.array([(x + math.cos(-math.pi / 2 + j * math.pi * 4 / 5) * s, y + math.sin(-math.pi / 2 + j * math.pi * 4 / 5) * s) for j in range(6)])
    cv2.polylines(st, [np.round(pts * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
img = chalk(img, st, '#F2F1E8', 0.85)
img = over(img, hexc('#8A5A2B'), np.clip((yy - 300) / 1.2 + .5, 0, 1))
img = over(img, hexc('#6E4520'), np.clip((yy - 300) / 1.2 + .5, 0, 1) * np.clip((yy - 312), 0, 1))
for (x, c) in [(520, '#F2F1E8'), (560, '#F6E27F'), (590, '#F4A6C0')]:
    m = np.zeros((Hh, W), np.float32)
    cv2.rectangle(m, (x * 4, 292 * 4), ((x + 26) * 4, 300 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    img = over(img, hexc(c), m)
save_webp(np.clip(img, 0, 1), out)
if len(sys.argv) > 2:
    cv2.imwrite(sys.argv[2], (mask * 255).astype(np.uint8))
print(out)
