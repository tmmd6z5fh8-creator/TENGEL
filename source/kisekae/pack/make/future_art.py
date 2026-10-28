"""近未来都市の 壁紙（壁紙パック・第4.92版）の 走る 馬：いままでの 壁紙と 同じ 馬（horse_flat）の ギャロップ（flat/sea_run.py と 同じ 足の 動き）を、
   黒に 近い 鉄の 色の 体・水色に 光る たてがみと しっぽ・水色の 光の 帯の 布で 描いて、まわりに 水色の 光（ぼかした ふち）と、
   体の 上の ふちに 細い 光の 線（リムライト）を 足す。右を 向いて 光の レーンを 走る（10コマ）。
   python3 kisekae/pack/make/future_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の future.run"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import gallop_sheet, save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from cute_horse import smooth, path, stroke, circ, unit, V, f2  # noqa: E402

PAL = dict(body='#2E3448', shade='#1D2232', muzzle='#4A5370', mane='#5FE6FF', maneD='#1C9CC4', hoof='#9EE9FF', eye='#06080F',
           blush='#3A4A6A', tack='#45E0FF', ring='#DFFBFF', cloth='#121829', clothTrim='#45E0FF', num='#BFF6FF', saddle='#0E1220',
           bodyShade='#262C3E')
SPOT = dict(pose='gallop', facing='right', box=(250, 70, 520, 262), azim=6, shadow=('#000000', 0.0))
GROUND = 258


def acc_factory(i):
    def acc(m):
        """布に 光の 帯（水色の すじ 2本）と 小さな 六角の しるし"""
        p = m['p1u']
        x0, x1, yt, yb, trim = m['cloth']
        out = [f'<defs><clipPath id="ftc{i}"><path d="{m["cloth_d"]}"/></clipPath></defs><g clip-path="url(#ftc{i})">']
        for off, w, op in ((0.07, 0.022, .95), (0.12, 0.012, .7)):
            y = yt + off * p
            out.append(f'<rect x="{f2(x0 - 4)}" y="{f2(y)}" width="{f2(x1 - x0 + 8)}" height="{f2(w * p)}" fill="#5FE6FF" fill-opacity="{op}"/>')
        out.append('</g>')
        cx, cy = (x0 + x1) / 2, (yt + trim) / 2 + 0.035 * p
        r = 0.07 * p
        hexd = 'M' + ' L'.join(f'{f2(cx + math.cos(math.radians(60 * k + 30)) * r)},{f2(cy + math.sin(math.radians(60 * k + 30)) * r)}' for k in range(6)) + ' Z'
        out.append(f'<path d="{hexd}" fill="none" stroke="#5FE6FF" stroke-width="{f2(0.016 * p)}"/>')
        out.append(circ(V(cx, cy), 0.022 * p, '#BFF6FF'))
        return dict(cloth=out)
    return acc


def hexc(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def neon(i, pre, A):
    """まわりの 水色の 光（ぼかした ふち）と、上の ふちの 細い 光の 線"""
    k5 = np.ones((5, 5), np.uint8)
    er = cv2.erode(A, k5)
    edge = np.clip(A - er, 0, 1)
    dy = np.zeros_like(A)
    dy[2:-2] = A[4:] - A[:-4]
    top = np.clip(dy * 1.6, 0, 1)
    rim = np.clip(edge * (0.25 + top), 0, 1) * 0.85
    rc = hexc('#9FF4FF')
    pre = pre * (1 - rim[..., None]) + rc[None, None, :] * (rim * A)[..., None]
    g = np.clip(cv2.GaussianBlur(A, (0, 0), 5.0) * 0.55 + cv2.GaussianBlur(A, (0, 0), 14.0) * 0.25, 0, 1)
    gc = hexc('#36D6FF')
    pre = pre + gc[None, None, :] * (g * (1 - A))[..., None]
    A2 = A + g * (1 - A)
    return pre, A2


if __name__ == '__main__':
    u8, meta, frames, cam = gallop_sheet(PAL, SPOT, acc=acc_factory, n=10, number='', tag='pkfuture', ground=GROUND, lift=6.0, shadow=None,
                                         workers=2, extra=neon)
    out = os.environ.get('OUT')
    if out:
        preview_png(u8, os.path.join(out, 'future_run.png'), bg=(18, 22, 44))
    bid = save_webp(u8, quality=90)
    record('future', 'run', bid, meta)
    print('run', bid, meta)
