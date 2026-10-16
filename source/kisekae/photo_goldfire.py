"""黄金の炎の背景：まさちゃんの見本（炎と宝石の黄金の馬）を画面いっぱいに
   python3 -I photo_goldfire.py <ref/goldfire.jpg> <出力フォルダ>
   → goldfire_wall.jpg（780×1688＝画面いっぱい・2倍）・goldfire_thumb.jpg（780×320）"""
import sys
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
im = ImageEnhance.Contrast(im).enhance(1.08)
im = ImageEnhance.Color(im).enhance(1.06)
W, H = im.size
z = 1.5
sc = im.resize((round(W * z), round(H * z)), Image.LANCZOS)
x0 = round(290 * z)
wall = Image.new('RGB', (780, 1688), (20, 9, 3))
bottom = sc.crop((x0, sc.height - 8, x0 + 780, sc.height)).resize((780, 180)).filter(ImageFilter.GaussianBlur(18))
wall.paste(bottom, (0, 1688 - 180))
wall.paste(sc.crop((x0, 0, x0 + 780, sc.height)), (0, -120))
wall = wall.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
# まわりを少し暗く（文字を読みやすく）
a = np.asarray(wall).astype(np.float32)
yy, xx = np.mgrid[0:1688, 0:780]
d = np.sqrt(((xx - 390) / 560) ** 2 + ((yy - 560) / 1100) ** 2)
v = np.clip(1.08 - d * .5, .45, 1)[..., None]
wall = Image.fromarray(np.clip(a * v, 0, 255).astype(np.uint8))
wall.save(f'{out}/goldfire_wall.jpg', quality=84, optimize=True, progressive=True)
th = im.crop((120, 170, 900, 490))
th.save(f'{out}/goldfire_thumb.jpg', quality=84, optimize=True)
print('ok', wall.size, th.size)
