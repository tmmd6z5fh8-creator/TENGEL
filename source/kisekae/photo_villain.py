"""ヴィラン版の背景：黒馬の写真（まさちゃんの見本）をレッド×ブラックに。赤く光る目・火の粉・赤い稲妻
   python3 -I photo_villain.py <ref/stallion_c.png> <出力フォルダ>
   → villain_wall.jpg（780×1688＝画面いっぱい・2倍）・villain_thumb.jpg（780×320）"""
import sys, math, random
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import numpy as np

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float32) / 255.0
L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

# コントラスト（S字）と黒のしめ
def curve(x):
    x = np.clip((x - 0.04) / 0.92, 0, 1)
    return x * x * (3 - 2 * x) * 0.85 + x * 0.15

Lc = curve(L)
# 色の段（黒→血の赤→深紅→赤オレンジ→薄いピンク）
stops = [(0.0, (4, 2, 3)), (0.18, (18, 4, 6)), (0.38, (62, 8, 14)), (0.58, (138, 16, 26)), (0.78, (214, 46, 40)), (0.92, (255, 112, 84)), (1.0, (255, 214, 200))]
xs = np.array([s[0] for s in stops])
col = np.zeros(a.shape, np.float32)
for c in range(3):
    col[..., c] = np.interp(Lc, xs, np.array([s[1][c] for s in stops], np.float32)) / 255.0
# もとの明るさの細かさを少し残す
gray = np.repeat(Lc[..., None], 3, axis=2)
res = col * 0.86 + gray * np.array([0.16, 0.05, 0.06], np.float32) * 0.9
res = np.clip(res, 0, 1)
img = Image.fromarray((res * 255).astype(np.uint8))

W, H = img.size
# 赤く光る目
eye = (705, 330)
glow = Image.new('RGB', (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, c in [(24, (110, 0, 0)), (15, (200, 16, 12)), (9, (255, 50, 36)), (5, (255, 140, 110)), (2.6, (255, 236, 220))]:
    gd.ellipse([eye[0] - r, eye[1] - r * .55, eye[0] + r, eye[1] + r * .55], fill=c)
gd.line([eye[0] - 34, eye[1] + 1, eye[0] + 34, eye[1] - 1], fill=(255, 70, 50), width=1)
glow = glow.filter(ImageFilter.GaussianBlur(3.2))
img = ImageChops.screen(img, glow)

# 赤い稲妻（左上の空）
bolt = Image.new('RGB', (W, H), (0, 0, 0))
bd = ImageDraw.Draw(bolt)
random.seed(7)
def zig(x, y, ang, n, step, w):
    pts = [(x, y)]
    for i in range(n):
        ang += random.uniform(-0.6, 0.6)
        x += math.cos(ang) * step; y += math.sin(ang) * step
        pts.append((x, y))
        if random.random() < 0.18 and w > 1:
            zig(x, y, ang + random.choice([-0.8, 0.8]), n // 3, step * .7, w - 1)
    bd.line(pts, fill=(255, 190, 175), width=w)
zig(935, 0, math.radians(100), 11, 20, 3)
zig(965, 24, math.radians(84), 6, 16, 2)
bolt_g = bolt.filter(ImageFilter.GaussianBlur(5))
img = ImageChops.screen(img, bolt_g)
img = ImageChops.screen(img, bolt.filter(ImageFilter.GaussianBlur(.8)))

# 火の粉（下のほう・上へ舞う）
emb = Image.new('RGB', (W, H), (0, 0, 0))
ed = ImageDraw.Draw(emb)
random.seed(3)
for i in range(130):
    x = random.uniform(0, W); y = H - abs(random.gauss(0, H * 0.22))
    r = random.choice([1.2, 1.6, 2.2, 3.0])
    c = random.choice([(255, 70, 40), (255, 120, 60), (255, 40, 30), (255, 170, 110)])
    ed.ellipse([x - r, y - r, x + r, y + r], fill=c)
emb_g = emb.filter(ImageFilter.GaussianBlur(3))
img = ImageChops.screen(img, emb_g)
img = ImageChops.screen(img, emb.filter(ImageFilter.GaussianBlur(.6)))

# 周りを暗く（ビネット）
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W * .58) / (W * .75)) ** 2 + ((yy - H * .32) / (H * .78)) ** 2)
v = np.clip(1.05 - d * .55, .35, 1)[..., None]
img = Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * v, 0, 255).astype(np.uint8))
img.save(f'{out}/villain_full.jpg', quality=90)

# 画面いっぱい（2倍：780×1688）：上に40px（2倍で80）空をのばし、横は x=200 から
z = 0.962
sc = img.resize((round(W * z), round(H * z)), Image.LANCZOS)
wall = Image.new('RGB', (780, 1688), (6, 3, 4))
top = sc.crop((0, 0, sc.width, 6)).resize((sc.width, 80))
wall.paste(top.filter(ImageFilter.GaussianBlur(24)), (-192, 0))
wall.paste(sc, (-192, 80))
wall = wall.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
wall.save(f'{out}/villain_wall.jpg', quality=84, optimize=True, progressive=True)
# 選ぶ画面の見本（頭のまわり）
th = sc.crop((250, 150, 250 + 780, 150 + 320))
th.save(f'{out}/villain_thumb.jpg', quality=84, optimize=True)
print('ok', wall.size, th.size)
