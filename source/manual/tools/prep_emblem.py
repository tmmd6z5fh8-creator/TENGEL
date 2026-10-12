import sys
from PIL import Image, ImageDraw, ImageFilter
src, out, prev = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert('RGB')
cx, cy, r = 384, 388, 252
e = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((384, 384), Image.LANCZOS).convert('RGBA')
mask = Image.new('L', e.size, 0)
ImageDraw.Draw(mask).ellipse((22, 18, 366, 370), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(20))
e.putalpha(mask)
e.save(out + '/emblem.webp', 'WEBP', quality=85, method=6)
e.resize((160, 160), Image.LANCZOS).save(out + '/emblem-160.webp', 'WEBP', quality=85, method=6)
bg = Image.new('RGBA', e.size, (11, 30, 37, 255)); bg.alpha_composite(e); bg.convert('RGB').save(prev)
