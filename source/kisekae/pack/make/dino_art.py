"""恐竜時代の 壁紙（壁紙パック・第4.92版）の 馬：いままでの 壁紙と 同じ 馬（horse_flat）が 2頭 ならんで ギャロップ。
   手前＝鹿毛（黒い たてがみ・若葉色の 布 1）・おく＝芦毛（灰色の たてがみ・溶岩色の 布 2・少し 小さく 前へ）。布の すみに 小さな シダの 葉。
   python3 kisekae/pack/make/dino_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の dino.near・dino.far（コマの シート）"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import gallop_sheet, save_webp, record, preview_png  # noqa: E402
from cute_horse import path, stroke, unit, V, f2  # noqa: E402

NEAR = dict(body='#9A552C', shade='#6E3818', muzzle='#C9906A', mane='#231612', maneD='#120A08', hoof='#2E2420', eye='#1A100A',
            blush='#EE9070', tack='#2A1A10', ring='#F2C14E', cloth='#3E8A3A', clothTrim='#F2E6A8', num='#FFFFFF', saddle='#2A1A12',
            bodyShade='#8A4A24')
FAR = dict(body='#E4E0D8', shade='#B3ABA0', muzzle='#F3F0EA', mane='#56504C', maneD='#36322F', hoof='#4A4440', eye='#1A1414',
           blush='#E8A898', tack='#3A2418', ring='#F2C14E', cloth='#E0662A', clothTrim='#FFE2A8', num='#FFFFFF', saddle='#2A1C14',
           bodyShade='#D2CBC1')
SPOT_NEAR = dict(pose='gallop', facing='right', box=(190, 98, 468, 292), azim=6, shadow=('#5A3A1A', 0.0))
SPOT_FAR = dict(pose='gallop', facing='right', box=(262, 70, 498, 236), azim=6, shadow=('#5A3A1A', 0.0))
N = 10


def fern(c, L, ang, col):
    """小さな シダの 葉（布の すみ）"""
    u = V(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    n = V(-u[1], u[0])
    out = [stroke(f'M{f2(c[0])},{f2(c[1])} L{f2(c[0] + u[0] * L)},{f2(c[1] + u[1] * L)}', col, L * 0.08)]
    for k in range(1, 6):
        t = k / 6
        b = c + u * L * t
        w = L * 0.32 * (1 - t * 0.7)
        for sgn in (1, -1):
            tip = b + n * sgn * w + u * L * 0.12
            out.append(path(f'M{f2(b[0])},{f2(b[1])} Q{f2(b[0] + n[0] * sgn * w * 0.6)},{f2(b[1] + n[1] * sgn * w * 0.6 - L * 0.04)} {f2(tip[0])},{f2(tip[1])} '
                            f'Q{f2(b[0] + n[0] * sgn * w * 0.3 + u[0] * L * 0.1)},{f2(b[1] + n[1] * sgn * w * 0.3 + u[1] * L * 0.1)} {f2(b[0])},{f2(b[1])} Z', col))
    return out


def acc_for(leaf):
    def mk(i):
        def acc(m):
            p = m['p1u']
            x0, x1, yt, yb, trim = m['cloth']
            c = V(x1 - 0.06 * p if m['fx'] > 0 else x0 + 0.06 * p, yt + 0.06 * p)
            return dict(cloth=fern(c, 0.16 * p, 150 if m['fx'] > 0 else 30, leaf))
        return acc
    return mk


if __name__ == '__main__':
    out = os.environ.get('OUT')
    for name, pal, spot, num, leaf in (('near', NEAR, SPOT_NEAR, '1', '#BFE38A'), ('far', FAR, SPOT_FAR, '2', '#FFE2A8')):
        u8, meta, frames, cam = gallop_sheet(pal, spot, acc=acc_for(leaf), n=N, number=num, tag='pkdino' + name, ground=spot['box'][3] - 4, lift=6.0, workers=1)
        if out:
            preview_png(u8, os.path.join(out, f'dino_{name}.png'), bg=(200, 170, 120))
        bid = save_webp(u8, quality=90)
        record('dino', name, bid, meta)
        print(name, bid, meta, flush=True)
