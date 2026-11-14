# 見くらべの 絵（前 → 後）を 1まいに まとめる
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import sys
from PIL import Image, ImageDraw, ImageFont
D = ROOT + '/out/sheet/'
F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'


def font(sz, black=False):
    return ImageFont.truetype(FB if black else F, sz, index=0)


W = 1680; PAD = 40; GAP = 24
BG = (250, 247, 240); INK = (60, 45, 35); RED = (214, 64, 72); GRN = (58, 140, 96); SUB = (120, 105, 95)
items = []          # (種類, 中身)


def title(t, sub=None):
    items.append(('title', (t, sub)))


def row(pics, labels, colors, h=None):
    items.append(('row', (pics, labels, colors, h)))


which = sys.argv[2]
if which == 'peg':
    title('① 釘（くぎ）を 2倍に のばした', '土台（盤に ついている ところ）は そのまま。先だけ 前へ のびています')
    row(['orig_peg.png', 'v2_peg.png'], ['前', '後（2倍）'], [SUB, RED])
    title('釘の 長さの 見本', '今回は 2倍に しました。ほかの 長さが よければ 言ってね')
    row(['k1.5_peg.png', 'v2_peg.png', 'k2.5_peg.png'], ['1.5倍', '2倍（今回）', '2.5倍'], [SUB, RED, SUB])
else:
    title('② 馬の 目を ぬり直した', '前は 正面から 見える ところ だけ 黒で、上は 肌色の ままでした → 目の まるい ところを ぜんぶ ぬりました')
    row(['orig_eyet.png', 'v2_eyet.png'], ['前（上から）', '後（上から）'], [SUB, RED])
    row(['orig_eyef.png', 'v2_eyef.png'], ['前（正面）', '後（正面）'], [SUB, RED])

# 高さを 数える
y = PAD
lay = []
for kind, v in items:
    if kind == 'title':
        t, sub = v
        lay.append((kind, v, y)); y += 64 + (44 if sub else 0) + 14
    else:
        pics, labels, colors, hh = v
        n = len(pics)
        cw = (W - 2 * PAD - GAP * (n - 1)) // n
        ims = []
        for p in pics:
            im = Image.open(D + p).convert('RGB')
            if hh:
                s = hh / im.height
                im = im.resize((int(im.width * s), hh), Image.LANCZOS)
            else:
                s = cw / im.width
                im = im.resize((cw, int(im.height * s)), Image.LANCZOS)
            ims.append(im)
        h = max(i.height for i in ims)
        lay.append((kind, (ims, labels, colors, cw), y)); y += h + (56 if any(labels) else 0) + 36
H = y + PAD - 20
sheet = Image.new('RGB', (W, H), BG)
dr = ImageDraw.Draw(sheet)
for kind, v, y in lay:
    if kind == 'title':
        t, sub = v
        dr.rounded_rectangle((PAD, y, W - PAD, y + 62), 16, fill=(255, 226, 120))
        dr.text((PAD + 22, y + 31), t, font=font(38, True), fill=INK, anchor='lm')
        if sub:
            dr.text((PAD + 6, y + 62 + 26), sub, font=font(26), fill=SUB, anchor='lm')
    else:
        ims, labels, colors, cw = v
        n = len(ims)
        tw = sum(i.width for i in ims) + GAP * (n - 1)
        x = (W - tw) // 2
        for im, lb, col in zip(ims, labels, colors):
            if lb:
                dr.rounded_rectangle((x, y, x + im.width, y + 48), 12, fill=col)
                dr.text((x + im.width // 2, y + 24), lb, font=font(30, True), fill=(255, 255, 255), anchor='mm')
                yy = y + 56
            else:
                yy = y
            sheet.paste(im, (x, yy))
            dr.rectangle((x, yy, x + im.width - 1, yy + im.height - 1), outline=(205, 195, 180), width=2)
            x += im.width + GAP
out = sys.argv[1]
sheet.save(out, optimize=True)
print(out, sheet.size)
