# 見なおし用：見本の 動画（4つの 段・1段 約4.93秒）から 止まって いる 時と 動いた 時の コマを 段ごとに ならべる
#   python3 video_sheet.py <動画> <出す png> [--box x0,y0,x1,y1（動画の px：780×1688）] [--w 260] [--t 0.2,1.1,1.6,2.4]
import sys, os, subprocess, tempfile
from PIL import Image
a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    return d
BOX = tuple(int(v) for v in opt('--box', '0,120,780,1500').split(',')); TW = int(opt('--w', '260')); TS = [float(v) for v in opt('--t', '0.2,1.1,1.6,2.4').split(',')]
V, OUT = a[0], a[1]; tmp = tempfile.mkdtemp(); rows = []
for k in range(4):
    tiles = []
    for t in TS:
        f = os.path.join(tmp, f'{k}_{t}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(round(t + k * 4.93, 2)), '-i', V, '-frames:v', '1', f], check=True)
        im = Image.open(f).convert('RGB').crop(BOX); s = TW / im.width; tiles.append(im.resize((TW, int(im.height * s)), Image.LANCZOS))
    R = Image.new('RGB', (len(tiles) * (TW + 4), tiles[0].height), 'white')
    for i, t in enumerate(tiles): R.paste(t, (i * (TW + 4), 0))
    rows.append(R)
S = Image.new('RGB', (rows[0].width, sum(r.height for r in rows) + 4 * len(rows)), 'white'); y = 0
for r in rows: S.paste(r, (0, y)); y += r.height + 4
S.save(OUT); print(OUT, S.size)
