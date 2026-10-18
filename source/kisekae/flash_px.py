"""動画のコマ（PNG・60コマ/秒）で、点めつを「画面の点ごと」に数える（WCAG 2.3.1 の一般の点めつに近い数え方）。
   点ごとに明るさ（相対輝度）の山と谷を追い、0.1以上の上がり下がり（暗いほうが0.8未満）を1回の「変化」、変化2回で点めつ1回。
   1秒の窓で点めつが3回を超えた点の面積が AREA（画面の割合）以上なら「多すぎ」。
   python3 flash_px.py <コマのフォルダ> <タップのコマ> [ここから] [ここまで]   AREA=.1（スマホは画面が目に近いので小さめ）"""
import sys, os
import numpy as np
from PIL import Image

D, start = sys.argv[1], int(sys.argv[2])
lo = int(sys.argv[3]) if len(sys.argv) > 3 else start
hi = int(sys.argv[4]) if len(sys.argv) > 4 else 99999
FPS, AREA = 60, float(os.environ.get('AREA', '.1'))
files = sorted(f for f in os.listdir(D) if f.startswith('f') and f.endswith('.png') and lo <= int(f[1:5]) <= hi)


def lum(fn):
    a = np.asarray(Image.open(os.path.join(D, fn)).convert('RGB').resize((98, 211), Image.BILINEAR), dtype=np.float32) / 255
    a = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)
    return .2126 * a[..., 0] + .7152 * a[..., 1] + .0722 * a[..., 2]


L0 = lum(files[0])
ext = L0.copy()                      # いまの山（または谷）
dirn = np.zeros_like(L0, dtype=np.int8)
trans = []                           # (時刻, その時に変化した点のマスク)
times = []
for fn in files[1:]:
    t = (int(fn[1:5]) - start) / FPS
    L = lum(fn)
    up = (L - ext >= .1) & (np.minimum(L, ext) < .8) & (dirn <= 0)
    dn = (ext - L >= .1) & (np.minimum(L, ext) < .8) & (dirn >= 0)
    ch = up | dn
    dirn = np.where(up, 1, np.where(dn, -1, dirn)).astype(np.int8)
    ext = np.where(ch, L, np.where(dirn > 0, np.maximum(ext, L), np.where(dirn < 0, np.minimum(ext, L), ext)))
    trans.append(ch)
    times.append(t)
T = np.array(times)
C = np.stack(trans).astype(np.int16)        # [時刻, 点]
cs = np.concatenate([np.zeros((1,) + C.shape[1:], np.int16), np.cumsum(C, 0)], 0)
worst = []
for i, t0 in enumerate(T):
    j = np.searchsorted(T, t0 + 1.0)
    n = cs[j] - cs[i]                       # 1秒の中の変化の回数（点ごと）
    flashes = n // 2
    frac = float((flashes > 3).mean())
    worst.append((frac, t0, int(flashes.max())))
bad = [(f, t, m) for f, t, m in worst if f >= AREA]
print(f'AREA={AREA}：1秒に点めつ4回以上の点が{AREA * 100:.0f}%以上になる窓 {len(bad)}個')
for f, t, m in sorted(bad, key=lambda x: x[1])[:40:4]:
    print(f'  {t:5.2f}秒から：面積 {f * 100:4.1f}%（いちばん多い点で{m}回）')
f, t, m = max(worst)
print(f'いちばん多い窓：{t:.2f}秒から 面積 {f * 100:.1f}%・いちばん多い点で{m}回')
