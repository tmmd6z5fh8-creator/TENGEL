# 見なおし用：アプリで 写した コマ（shots_sel.py）から 段ごとに「止まって いる 時」と「いちばん 動いた 時」を ならべる（ボードの まわり）
#   python3 peak_sheet.py <コマの フォルダ> <出す png> [--box x0,y0,x1,y1（2倍の 画面 px）] [--w 380] [--n 1]
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
a = sys.argv[1:]
def opt(k, d, f=str):
    if k in a: i = a.index(k); v = f(a[i + 1]); del a[i:i + 2]; return v
    return d
BOX = opt('--box', '0,140,780,1400'); TW = opt('--w', 380, int); N = opt('--n', 1, int)
FR, OUT = a[0], a[1]; box = tuple(int(v) for v in BOX.split(','))
cols = []
for d in sorted(glob.glob(os.path.join(FR, '*'))):
    if not os.path.isdir(d): continue
    rp = os.path.join(d, 'f0042.png')
    if not os.path.exists(rp): continue
    R = np.asarray(Image.open(rp).convert('RGB')).astype(np.int16)
    sc = []
    for f in sorted(glob.glob(os.path.join(d, 'f*.png'))):
        if f == rp: continue
        X = np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
        sc.append((float((np.abs(X - R).max(-1) > 24).sum()), f))
    sc.sort(reverse=True)
    for f in [rp] + [f for _, f in sc[:N]]:
        im = Image.open(f).convert('RGB').crop(box); s = TW / im.width
        im = im.resize((TW, int(im.height * s)), Image.LANCZOS)
        ImageDraw.Draw(im).text((4, 4), os.path.basename(d) + ' ' + os.path.basename(f)[1:5], fill=(255, 255, 0))
        cols.append(im)
S = Image.new('RGB', (len(cols) * (TW + 4), cols[0].height), 'white')
for k, t in enumerate(cols): S.paste(t, (k * (TW + 4), 0))
S.save(OUT); print(OUT, S.size)
