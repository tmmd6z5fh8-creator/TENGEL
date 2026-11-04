# 次…！（miss2）：ボードの 下の ふち（白い 帯）を 動かさない 所の マスクに する（旗・耳・しずく・玉・紙ふぶきは のぞく）
#   python3 next_band.py <clean.png> <出す png>
import sys, numpy as np, cv2
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int); H, W = a.shape[:2]
V = a.max(-1); mn = a.min(-1); sat = (V - mn) / np.maximum(V, 1)
def yq(x): return 833.6 - (x - 162.8) * (833.6 - 801.2) / (966.2 - 162.8)      # ボードの 四角の 下の 線
skip = [(0, 266), (273, 323), (357, 413), (497, 562), (806, W)]
m = np.zeros((H, W), np.uint8); bs = {}
for x in range(W):
    if any(lo <= x < hi for lo, hi in skip): continue
    top = int(yq(x)) - 6
    if x < 357:                         # しずくと 玉の あいだ：帯の 下は 馬の 光（はっきりした さかいが ない）
        bs[x] = 852; continue
    band = False; b = None
    for y in range(int(yq(x)) - 2, int(yq(x)) + 45):
        if V[y, x] > 170 and sat[y, x] < 0.3: band = True
        if band and (V[y, x] < 110 or (sat[y, x] > 0.65 and V[y, x] > 150)): b = y; break
    if b is not None: bs[x] = b
xs = np.array(sorted(bs)); ys = np.array([bs[x] for x in xs], float)
# となりの 列と くらべて とびはねた 所は ならす（紙ふぶき・きらきら）
ys_s = ys.copy()
for i in range(len(xs)):
    sel = np.abs(xs - xs[i]) <= 6; ys_s[i] = np.median(ys[sel])
for x, b in zip(xs, ys_s):
    top = int(yq(x)) - 6; bot = int(round(b)) - 3
    if bot > top: m[top:bot, x] = 1
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((1, 3), np.uint8))
Image.fromarray(m * 255).save(sys.argv[2])
print(sys.argv[2], 'px', int(m.sum()), 'cols', len(xs))
