# 確認用：撮った画面の一部を切り出して横に並べる（座標はCSS px、画像は2倍）
import json, sys
from PIL import Image
m = json.load(open('shots/meta.json'))
out = sys.argv[1]; items = sys.argv[2:]   # name:y0:y1
ims = []
for it in items:
    name, y0, y1 = it.split(':'); y0, y1 = float(y0), float(y1)
    im = Image.open(f'shots/{name}.png').convert('RGB')
    sc = im.width / m[name]['W'] if name in m else 2
    ims.append(im.crop((0, int(y0 * sc), im.width, int(min(y1 * sc, im.height)))).resize((390, int((y1 - y0)))))
H = max(i.height for i in ims)
sheet = Image.new('RGB', (sum(i.width for i in ims) + 10 * (len(ims) - 1), H), (40, 40, 40))
x = 0
for i in ims:
    sheet.paste(i, (x, 0)); x += i.width + 10
sheet.save(out)
