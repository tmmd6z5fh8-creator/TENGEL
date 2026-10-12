# 撮った画面を説明書用のWebPにする（切り出し・つなぎ合わせ）。座標は2倍のピクセル
import json, os, sys
from PIL import Image, ImageDraw
SP = sys.argv[1]
RAW = SP + '/man/raw'; IMG = SP + '/man/img'
meta = json.load(open(RAW + '/meta.json', encoding='utf-8'))
CROP = {  # name: (top, bottom) in raw px
    'result_c': (0, 1330), 'record_open': (1712, None), 'set_mother': (0, 1500), 'ocr_need': (0, 720),
}
out = {}
PARTS = {'result_a1': ('result_a', 0, 1104), 'result_a2': ('result_a', 1104, None), 'record_1': ('record', 0, 1052), 'record_2': ('record', 1052, None)}


def save(name, im):
    p = f'{IMG}/s_{name}.webp'
    im.save(p, 'WEBP', quality=80, method=6)
    out[name] = {'w': im.width // 2, 'h': im.height // 2, 'kb': round(os.path.getsize(p) / 1024)}


for f in sorted(os.listdir(RAW)):
    if not f.endswith('.png'):
        continue
    name = f[:-4]
    im = Image.open(f'{RAW}/{f}').convert('RGB')
    if name == 'judge_odds':
        top = im.crop((0, 0, im.width, 480)); bot = im.crop((0, 1140, im.width, im.height))
        gap = 44
        c = Image.new('RGB', (im.width, top.height + gap + bot.height), im.getpixel((20, 300)))
        c.paste(top, (0, 0)); c.paste(bot, (0, top.height + gap))
        d = ImageDraw.Draw(c)
        for k in range(3):
            x = 64 + k * 14; y = top.height + gap // 2
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(150, 156, 172))
        # 左右のふち（カードの線）をつなぐ
        edge = im.getpixel((1, 300));
        d.line((0, top.height, 0, top.height + gap), fill=edge, width=3); d.line((im.width - 1, top.height, im.width - 1, top.height + gap), fill=edge, width=3)
        save(name, c); continue
    if name in CROP:
        a, b = CROP[name]
        im = im.crop((0, a, im.width, b or im.height))
        m = meta.get(name)
        if m:
            m['cropTop'] = a / 2; m['H'] = im.height / 2
    save(name, im)
for pn, (src, a, b) in PARTS.items():
    im = Image.open(f'{RAW}/{src}.png').convert('RGB')
    im = im.crop((0, a, im.width, b or im.height))
    m = json.loads(json.dumps(meta[src])); m['cropTop'] = a / 2; m['H'] = im.height / 2; meta[pn] = m
    save(pn, im)
json.dump(meta, open(RAW + '/meta2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(out, open(IMG + '/../dims.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = sum(v['kb'] for v in out.values())
for k, v in out.items():
    print(k, v)
print('total KB', tot)
