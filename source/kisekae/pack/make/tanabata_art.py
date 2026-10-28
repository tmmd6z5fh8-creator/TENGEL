"""七夕の 壁紙（壁紙パック・第4.92版）の 天の川を 渡る 馬：いままでの 壁紙と 同じ 馬（horse_flat）の ギャロップ（flat/sea_run.py と 同じ 足の 動き）を、
   白い 体・うすい 金の たてがみ・金の 手綱・紺の 布に 金の 星で 描いて、まわりに やわらかい 星の 光（ぼかした ふち）を 足す。右を 向いて 走る（10コマ）。
   python3 kisekae/pack/make/tanabata_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の tanabata.run"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import gallop_sheet, save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from cute_horse import circ, V, f2  # noqa: E402

PAL = dict(body='#FFFFFF', shade='#C9D1EC', muzzle='#F4F6FC', mane='#F7E3A6', maneD='#D8BC6E', hoof='#9A96B4', eye='#1E2448',
           blush='#F2B8C8', tack='#C9A44A', ring='#FFF4C8', cloth='#2C3A8E', clothTrim='#F4D27A', num='#FFF6D8', saddle='#232C5E',
           bodyShade='#E6EAF6')
SPOT = dict(pose='gallop', facing='right', box=(40, 40, 296, 222), azim=6, shadow=('#000000', 0.0))
GROUND = 218


def star_path(cx, cy, r, r2):
    pts = [(cx + math.cos(math.radians(-90 + k * 36)) * (r if k % 2 == 0 else r2), cy + math.sin(math.radians(-90 + k * 36)) * (r if k % 2 == 0 else r2)) for k in range(10)]
    return 'M' + ' L'.join(f'{f2(x)},{f2(y)}' for x, y in pts) + ' Z'


def acc_factory(i):
    def acc(m):
        """布の まん中に 金の 星・すみに 小さな 星 2つ"""
        p = m['p1u']
        x0, x1, yt, yb, trim = m['cloth']
        cx, cy = (x0 + x1) / 2, (yt + trim) / 2 + 0.03 * p
        out = [f'<path d="{star_path(cx, cy, 0.085 * p, 0.036 * p)}" fill="#F4D27A" stroke="#B8902E" stroke-width="{f2(0.008 * p)}"/>']
        for dx, dy, r in ((-0.16, -0.05, 0.03), (0.15, 0.03, 0.024)):
            out.append(f'<path d="{star_path(cx + dx * p, cy + dy * p, r * p, r * 0.42 * p)}" fill="#FFF1C2"/>')
        return dict(cloth=out)
    return acc


def hexc(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def glow(i, pre, A):
    """まわりの やわらかい 星の 光（白に 近い 金）"""
    g = np.clip(cv2.GaussianBlur(A, (0, 0), 6.0) * 0.42 + cv2.GaussianBlur(A, (0, 0), 16.0) * 0.22, 0, 1)
    gc = hexc('#FFF0C4')
    pre = pre + gc[None, None, :] * (g * (1 - A))[..., None]
    return pre, A + g * (1 - A)


if __name__ == '__main__':
    u8, meta, frames, cam = gallop_sheet(PAL, SPOT, acc=acc_factory, n=10, number='', tag='pktanabata', ground=GROUND, lift=7.0, shadow=None,
                                         workers=2, extra=glow)
    out = os.environ.get('OUT')
    if out:
        preview_png(u8, os.path.join(out, 'tanabata_run.png'), bg=(20, 28, 70))
    bid = save_webp(u8, quality=90)
    record('tanabata', 'run', bid, meta)
    print('run', bid, meta)
