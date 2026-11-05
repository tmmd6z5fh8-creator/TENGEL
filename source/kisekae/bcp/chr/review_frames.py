# 見なおし用：アプリで 写した コマ（shots_sel.py）から「止まって いる 時」と「いちばん 動いた 時」を ならべる
#   python3 review_frames.py <コマの フォルダ> <出す png> [--box x0,y0,x1,y1（2倍の 画面 px）] [--n 2] [--w 300]
#   段ごとに 1行：止まって いる 時（f0042）・動きが 大きい コマ n まい（止まって いる 時との ちがいが 大きい 順）
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
a = sys.argv[1:]
def opt(k, d, f=str):
    if k in a: i = a.index(k); v = f(a[i + 1]); del a[i:i + 2]; return v
    return d
BOX = opt('--box', None); N = opt('--n', 2, int); TW = opt('--w', 300, int); REST = opt('--rest', 42, int)
FR, OUT = a[0], a[1]
rows = []
for d in sorted(glob.glob(os.path.join(FR, '*'))):
    if not os.path.isdir(d): continue
    fs = sorted(glob.glob(os.path.join(d, 'f*.png')))
    rp = os.path.join(d, f'f{REST:04d}.png')
    if not os.path.exists(rp): continue
    R = np.asarray(Image.open(rp).convert('RGB')).astype(np.int16)
    sc = []
    for f in fs:
        if f == rp: continue
        X = np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
        dd = np.abs(X - R).max(-1)
        sc.append((float((dd > 24).sum()), f))
    sc.sort(reverse=True)
    pick = [rp] + [f for _, f in sc[:N]]
    if BOX: box = tuple(int(v) for v in BOX.split(','))
    else: box = (0, 0, R.shape[1], R.shape[0])
    tiles = []
    for f in pick:
        im = Image.open(f).convert('RGB').crop(box); s = TW / im.width
        im = im.resize((TW, int(im.height * s)), Image.LANCZOS)
        ImageDraw.Draw(im).text((4, 4), os.path.basename(d) + ' ' + os.path.basename(f)[1:5], fill=(255, 255, 0))
        tiles.append(im)
    row = Image.new('RGB', (len(tiles) * (TW + 4), tiles[0].height), 'white')
    for k, t in enumerate(tiles): row.paste(t, (k * (TW + 4), 0))
    rows.append(row)
S = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows) + 4 * len(rows)), 'white'); y = 0
for r in rows: S.paste(r, (0, y)); y += r.height + 4
S.save(OUT); print(OUT, S.size)
