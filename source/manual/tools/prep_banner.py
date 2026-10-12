import sys
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W, H = im.size
# 1) ヒーロー用バナー（1200px幅・WebP）
b = im.resize((1200, round(H * 1200 / W)), Image.LANCZOS)
b.save(out + '/banner.webp', 'WEBP', quality=82, method=6)
# 2) エンブレム（盾と馬）だけ切り出して、ふちを透明にぼかす
cx, cy, r = 368, 392, 238
box = (cx - r, cy - r, cx + r, cy + r)
e = im.crop(box).resize((384, 384), Image.LANCZOS).convert('RGBA')
mask = Image.new('L', e.size, 0)
d = ImageDraw.Draw(mask)
d.ellipse((34, 26, 350, 366), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(26))
e.putalpha(mask)
e.save(out + '/emblem.png', optimize=True)
e.resize((192, 192), Image.LANCZOS).save(out + '/emblem-192.png', optimize=True)
# 背景色の見本（バナーの中央付近と四隅）
for p in [(700, 384), (40, 40), (1360, 40), (40, 720), (1360, 720), (980, 150), (700, 640)]:
    print(p, '#%02x%02x%02x' % im.getpixel(p))
print('ok', b.size)
