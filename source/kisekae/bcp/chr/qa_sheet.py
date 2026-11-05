# キャラだけ 動かす（実験）の 見なおし用：段ごとに「キャラなしの 背景」と「大きく 動かした 絵（2つの 向き）」を ならべる
#   python3 qa_sheet.py <出す png> <box x0,y0,x1,y1> <幅> [--k 2.5] <chr の 出力>:<元の clean.png> …
#   ・背景に キャラの かけら（ひづめ・耳・しっぽ）が のこって いれば、動かした 絵で 体から はなれて 見える
#   ・キャラに 背景（ボードの ふち・光の すじ）が 入って いれば、動かした 絵で いっしょに ゆがむ
#   ・となりの キャラは 反対の 向きに 動かす（だき合う 腕が 2つの キャラに 分かれて いれば 切れて 見える）
import sys, json, os
import numpy as np, cv2
from PIL import Image
args = sys.argv[1:]
K = 2.5
if '--k' in args:
    i = args.index('--k'); K = float(args[i + 1]); del args[i:i + 2]
out, box, W_ = args[0], [int(v) for v in args[1].split(',')], int(args[2])
PX, PY = 0.024, -0.038          # ぷるんの いちばん つぶれた 所（bcp_chr_exp2.js の PON 14%）
cols = []
for arg in args[3:]:
    O, cl = arg.split(':')
    c = json.load(open(os.path.join(O, 'cfg.json')))
    mo = json.load(open(os.path.join(O, 'motion.json'))) if os.path.exists(os.path.join(O, 'motion.json')) else {'parts': []}
    mop = {p['id']: p for p in mo['parts']}
    src = np.asarray(Image.open(cl).convert('RGB')).astype(np.float32); H, W = src.shape[:2]
    bg = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.float32)
    lays = []
    for p in c['parts']:
        L = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA')).astype(np.float32)
        a = L[..., 3] / 255; yy_, xx_ = np.where(a > 0.5)
        m = mop.get(p['id'], {})
        if isinstance(m.get('o'), list): ox, oy = m['o']
        elif m.get('o') == 'bottom_center':
            ox, oy = float((xx_.min() + xx_.max()) / 2), float(yy_.max())
        elif m.get('o') == 'top':
            yt = yy_.min(); ox, oy = float(xx_[yy_ <= yt + 6].mean()), float(yt)
        else:
            yb = yy_.max(); ox, oy = float(xx_[yy_ >= yb - 6].mean()), float(yb)
        h_px = yy_.max() - yy_.min(); amp = min(1.0, 205.0 * (W / 390.0) / max(h_px, 1))
        lays.append((L, ox, oy, amp))
    frames = []
    for sgn in (1, -1):
        comp = bg.copy()
        for j, (L, ox, oy, amp) in enumerate(lays):
            s = sgn * (1 if j % 2 == 0 else -1)
            sx, sy = 1 + PX * amp * K * s, 1 + PY * amp * K * s
            M = np.array([[sx, 0, ox - sx * ox], [0, sy, oy - sy * oy]], np.float32)
            pm = np.dstack([L[..., :3] * (L[..., 3:4] / 255), L[..., 3]])
            w = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
            a = w[..., 3:4] / 255
            comp = w[..., :3] + comp * (1 - a)
        if os.path.exists(os.path.join(O, 'occl.png')):        # 前に 重ねる 動かない 物（ボードの ふち・びっくりマーク など）
            oc = np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')).astype(np.float32)[..., None] / 255
            comp = src * oc + comp * (1 - oc)
        frames.append(comp)
    tiles = [bg] + frames
    col = []
    for t in tiles:
        im = Image.fromarray(np.clip(t, 0, 255).astype(np.uint8)).crop(box)
        s = W_ / im.width; col.append(im.resize((W_, int(im.height * s)), Image.LANCZOS))
    T = Image.new('RGB', (W_, sum(t.height for t in col) + 6 * (len(col) - 1)), 'white'); y = 0
    for t in col: T.paste(t, (0, y)); y += t.height + 6
    cols.append(T)
S = Image.new('RGB', (len(cols) * (W_ + 8) - 8, cols[0].height), 'white')
for k, t in enumerate(cols): S.paste(t, (k * (W_ + 8), 0))
S.save(out); print(out, S.size)
