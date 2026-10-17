"""水墨画の絵（780×320）：和紙・遠くの山・墨のしぶき・赤い落款は前の r3d/banners/ink.py のまま（同じ乱数の順）、
   馬だけ描き直す → 騎手を乗せて競り合う2頭（flat/sumi_rider.py：墨の線＋灰色のぼかし）。
   手前の馬は濃い墨（光の当たる所は筆のかすれで白く抜く）で先頭、奥の馬はうすい墨（遠いほどうすい）で追う。
   足もとは乾いた筆で横にはいた地面と、うしろへ流れる細い筆の線
   python3 flat/sumi_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from sumi_rider import *
from sumi_rider import _bristles
sys.path.insert(0, K)
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
paper = img.copy()                                     # 馬の中に見せる紙（山のぼかしなし）
INK = hexc('#1C1A18')


def wash(img, mask, k):
    return img * (1 - mask[..., None] * k) + INK * (mask[..., None] * k)


# 遠くの山（にじむ墨）
for y0, amp, k, f, sd in [(150, 50, 0.16, 140, 1), (190, 36, 0.26, 90, 2)]:
    ridge = y0 - amp * np.abs(np.sin(xx / f + sd)) - 12 * np.sin(xx / 33 + sd)
    m = np.clip((yy - ridge) / 3 + .5, 0, 1) * np.clip(1 - (yy - ridge) / 70, 0, 1)
    m = blur(m, 2) * (0.75 + 0.25 * fbm(Hh, W, 40, 3, seed=sd + 5))
    img = wash(img, m, k)

# ---------- 2頭（左向き：3Dは右向きで描いて、左右をかえす） ----------
HORSES = [
    dict(name='far', box=(372, 62, 648, 228), tones='light', seed=4, lw=0.85, line_ink=0.72, hair_ink=0.72, silk=(0.10, 0.14, 0.06), sleeve=(0.10, 0.14, 0.06),
         wash=dict(base=0.10, shadow=0.17, deep=0.13, legs=0.30), hi=0.9, tail_len=118,
         pose=dict(theta=1.0, neck_rot=-32.0, head_ang=-34.0, fore=dict(L=[-96, -48, -44, -28], R=[-128, -36, -140, -165]),
                   hind=dict(L=[-118, -150, -128, -150], R=[-70, -112, -84, -62]), tail=[-166, -154])),
    dict(name='near', box=(120, 92, 470, 296), tones='dark', seed=3, lw=1.0, silk=(0.26, 0.24, 0.10), sleeve=(0.26, 0.24, 0.10), wash=dict(base=0.52, shadow=0.44, deep=0.36, legs=0.72), hi_t=0.50,
         tail_len=88, tail_ang=171,
         pose=dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0, fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                   hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]), tail=[-170, -158])),
]
grng = np.random.default_rng(131)                      # 地面の筆（背景の乱数とは別）
layers = []
for h in HORSES:
    x0, y0, x1, y1 = h['box']
    R = render_anime(h['pose'], (W - x1, y0, W - x0, y1), W, Hh, name='sumi_' + h['name'])
    k, A = paint_sumi(R, h)
    hv = np.asarray(R['hooves'], float) / R['s']
    hv[:, 0] = W - hv[:, 0]
    layers.append((k[:, ::-1], A[:, ::-1], hv, h))


def dry_ground(img, gy, xa, xb, scl, ink, rng_):
    """乾いた筆で横にはいた地面（うしろ＝右へ長く、かすれる）と、うしろへ流れる細い線"""
    S3 = 3
    cv_ = np.zeros((Hh * S3, W * S3), np.float32)
    for i in range(int(7 * scl) + 3):
        y = gy + rng_.normal(0, 2.2 * scl)
        x = xa + rng_.uniform(-20, 40) * scl
        L = rng_.uniform(150, 330) * scl
        path = np.array([[x + L * t, y + math.sin(t * math.pi * rng_.uniform(0.6, 1.4)) * rng_.uniform(-2, 2) * scl] for t in np.linspace(0, 1, 40)]) * S3
        P = resample(path, 1.0)
        t = np.linspace(0, 1, len(P))
        w = (rng_.uniform(5, 11) * scl * S3) * (0.35 + 0.65 * np.sin(np.pi * np.clip(t * 1.3, 0, 1)) ** 0.5) * (1 - 0.7 * t)
        _bristles(cv_, P, w, rng_, nb=22, lw=2, dry=rng_.uniform(0.05, 0.25), split=0.5, gap=0.62, wander=0.5,
                  ink=rng_.uniform(0.55, 1.0), start=0.2)
    for i in range(int(6 * scl) + 2):                  # 細い線（スピード）
        y = gy - rng_.uniform(6, 70) * scl
        x = xb + rng_.uniform(-30, 60) * scl
        L = rng_.uniform(60, 160) * scl
        P = resample(np.array([[x, y], [x + L, y + rng_.uniform(-1.5, 1.5)]]) * S3, 1.0)
        t = np.linspace(0, 1, len(P))
        w = 1.4 * S3 * np.sin(np.pi * t) ** 0.6 + 0.5
        _bristles(cv_, P, w, rng_, nb=4, lw=2, dry=0.4, split=0.3, gap=0.5, ink=0.8)
    g = cv2.resize(cv_, (W, Hh), interpolation=cv2.INTER_AREA)
    return wash(img, np.clip(g, 0, 1), ink)


for k_, A_, hv, h in layers:
    gy = hv[:, 1].max() + 2.0
    scl = 1.0 if h['tones'] == 'dark' else 0.8
    img = dry_ground(img, gy, hv[:, 0].min() - 10, hv[:, 0].max() + 10, scl, 0.42 if h['tones'] == 'dark' else 0.26, grng)
for k_, A_, hv, h in layers:                           # 奥 → 手前
    col = paper * (1 - k_[..., None]) + INK * k_[..., None]
    img = img * (1 - A_[..., None]) + col * A_[..., None]

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
