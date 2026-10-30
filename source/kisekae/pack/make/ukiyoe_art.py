"""浮世絵風の 壁紙（壁紙パック・第4.92版）の 走る 馬：いままでの 壁紙と 同じ 馬（horse_flat）を、浮世絵の 刷りの ように
   白い 馬（胡粉の 白・うすい ねずみ色の かげ）・黒い たてがみと しっぽ・朱の 布（金の ふち・白い 波の もよう）・朱の 手綱で 描いて、
   墨の 輪郭（外の ふち）と 色の さかいの 細い 線を 足す。ギャロップ 10コマ（flat/sea_run.py と 同じ 足の 動き）。影は 描かない（浮世絵には 影が ない）
   python3 kisekae/pack/make/ukiyoe_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.run"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import render, gallop_poses, gallop_stance, ground_dy, make_sheet, save_webp, record, preview_png, Z  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from cute_horse import path, stroke, unit, V, f2  # noqa: E402

PAL = dict(body='#F3EFE4', shade='#CFC7B8', muzzle='#F8F4EC', mane='#2A2622', maneD='#151210', hoof='#3A3430', eye='#1A1614',
           blush='#E8B0A0', tack='#B8322A', ring='#E0B04A', cloth='#B8322A', clothTrim='#E0B04A', num='#FFFFFF', saddle='#2A2420',
           bodyShade='#E4DED2')
SPOT = dict(pose='gallop', facing='right', box=(404, 128, 624, 266), azim=6)
INK = np.array([0x2A, 0x24, 0x20], np.float32) / 255


def acc(i):
    def f(m):
        """布に 白い 波の もよう（小さな 弧 3つ）"""
        x0, x1, yt, yb, trim = m['cloth']
        p = m['p1u']
        out = []
        for k in range(3):
            cx = x0 + (x1 - x0) * (0.25 + 0.25 * k)
            cy = (yt + trim) / 2 + 0.02 * p
            r = 0.05 * p
            out.append(stroke(f'M{f2(cx - r)},{f2(cy)} A{f2(r)},{f2(r)} 0 0 1 {f2(cx + r)},{f2(cy)}', '#F4EFE4', 0.018 * p))
        return dict(cloth=out)
    return f


def ink_lines(i, pre, A):
    """墨の 輪郭：外の ふち（アルファを ふくらませた 輪）と、色の さかいの 細い 線（体の 中）。
       第4.112版：線の 太さ・ぼかしは 画面の px で 同じ（Z 倍の 絵では 画素も Z 倍）"""
    a = np.clip(A, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, pre / np.maximum(a, 1e-3)[..., None], 0)
    hard = (a > 0.4).astype(np.uint8)
    kr = int(round(2 * Z))                                            # 輪の 太さ（2倍の 絵で 2画素＝画面の 1px）
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kr + 1, 2 * kr + 1))
    dil = cv2.dilate(hard, k).astype(np.float32)
    ring = np.clip(cv2.GaussianBlur(dil, (0, 0), 0.7 * Z) - a, 0, 1)
    # 色の さかい（明るさの 差が 大きい 所）：体の 中だけ
    lum = rgb[..., 0] * .3 + rgb[..., 1] * .59 + rgb[..., 2] * .11
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    g = np.sqrt(gx * gx + gy * gy)
    inner = np.clip((g - 0.55) * 1.6, 0, 1) * (cv2.erode(hard, k).astype(np.float32))
    inner = cv2.GaussianBlur(inner, (0, 0), 0.5 * Z) * 0.75
    # 中の 線は 色を 墨へ よせる・外の 輪は 墨を 足す
    rgb2 = rgb * (1 - inner[..., None]) + INK[None, None, :] * inner[..., None]
    A2 = a + ring * (1 - a)
    pre2 = rgb2 * a[..., None] + INK[None, None, :] * (ring * (1 - a))[..., None]
    return pre2, A2


if __name__ == '__main__':
    n = 10
    frames, cam = render(PAL, SPOT, gallop_poses(n), acc=acc, number='', tag='pkuk', workers=2)
    dys = ground_dy(frames, gallop_stance(n), SPOT['box'][3] - 4, lift=6.0)
    u8, meta = make_sheet(frames, dys, shadow=None, extra=ink_lines)
    meta['dy'] = [round(float(d), 2) for d in dys]
    out = os.environ.get('OUT')
    if out:
        preview_png(u8, os.path.join(out, 'uk_run.png'), bg=(243, 235, 220))
    bid = save_webp(u8, quality=92)
    record('ukiyoe', 'run', bid, meta)
    print('run', bid, meta['frames'], meta['cell'], meta['at'])
