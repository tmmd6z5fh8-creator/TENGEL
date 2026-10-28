"""宇宙の 壁紙（壁紙パック・第4.92版）の 馬：いままでの 壁紙と 同じ 馬（horse_flat）を 芦毛（銀に 近い 白）に して、頭に 宇宙の ヘルメット（ガラスの 玉・
   首の ところに 銀の 輪）・紺の 布（金の ふち・金の 星）。月の 上なので ギャロップを ゆっくり（コマを めくる はやさは ページ）。
   第4.93版（まさちゃん「足がしっかり地面についてるかも確認！」）：宙に 浮く 高さ（LIFT）を 16 → 6 に（ほかの 壁紙と 同じ ふつうの ギャロップ・
   地面に ついて いる ひづめは 地面の 線＝GROUND に そろう）。ふわっと 浮くのは ページで 5秒に 1回（space.py）
   python3 kisekae/pack/make/space_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の space.run（コマの シート）"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import gallop_sheet, save_webp, record, preview_png  # noqa: E402
from cute_horse import smooth, path, stroke, circ, ell, unit, V, f2  # noqa: E402

PAL = dict(body='#ECEFF5', shade='#B9C0CF', muzzle='#F7F8FB', mane='#56607A', maneD='#363E54', hoof='#5A6072', eye='#161A26',
           blush='#E9A6B0', tack='#24305E', ring='#F2D16B', cloth='#1C2B66', clothTrim='#F2D16B', num='#FFFFFF', saddle='#1A2140',
           bodyShade='#DCE0EA')
SPOT = dict(pose='gallop', facing='right', box=(196, 78, 470, 268), azim=6, shadow=('#05070F', 0.0))
GROUND = 264.0
N = 10


def star_pts(c, r, r2, n=5, rot=-90.0):
    return [c + V(math.cos(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2), math.sin(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2)) for k in range(2 * n)]


def acc_for(i):
    def acc(m):
        p = m['p1u']
        poll, muz, tip = m['poll'], m['muzzle'], m['ear_tip']
        hd = unit(m['head_dir'])
        # ヘルメット：頭ぜんぶ（耳の 先から 鼻先まで）を つつむ ガラスの 玉
        c = poll + (muz - poll) * 0.46 + V(0, -0.02 * p)
        r = max(float(math.hypot(*(c - tip))), float(math.hypot(*(c - muz)))) + 0.045 * p
        out = [circ(c, r, '#DDEBFF', 'fill-opacity=".14"'),
               circ(c, r, 'none', f'stroke="#E8F2FF" stroke-width="{f2(0.022 * p)}" stroke-opacity=".9"'),
               circ(c, r - 0.02 * p, 'none', f'stroke="#9EC4F0" stroke-width="{f2(0.01 * p)}" stroke-opacity=".55"')]
        # つや（左上の 弧 2本）
        a0, a1 = math.radians(200), math.radians(260)
        arc = lambda rr, s, e: f'M{f2(c[0] + math.cos(s) * rr)},{f2(c[1] + math.sin(s) * rr)} A{f2(rr)},{f2(rr)} 0 0 1 {f2(c[0] + math.cos(e) * rr)},{f2(c[1] + math.sin(e) * rr)}'
        out.append(stroke(arc(r * 0.8, a0, a1), '#FFFFFF', 0.035 * p, 'stroke-opacity=".75"'))
        out.append(stroke(arc(r * 0.8, math.radians(272), math.radians(285)), '#FFFFFF', 0.035 * p, 'stroke-opacity=".75"'))
        out.append(circ(c + V(math.cos(math.radians(320)), math.sin(math.radians(320))) * r * 0.72, 0.022 * p, '#FFFFFF', 'fill-opacity=".8"'))
        # 首の ところの 銀の 輪（玉の 下の ふちに そって）
        top, bot, ax = m['collar'](0.84)
        mid = (top + bot) / 2
        dv = unit(bot - top)
        L = float(math.hypot(*(bot - top))) * 0.62 + 0.03 * p
        a, b = mid - dv * L, mid + dv * L
        out.append(stroke(f'M{f2(a[0])},{f2(a[1])} L{f2(b[0])},{f2(b[1])}', '#7E8AA8', 0.075 * p))
        out.append(stroke(f'M{f2(a[0])},{f2(a[1])} L{f2(b[0])},{f2(b[1])}', '#C9D2E6', 0.045 * p))
        out.append(stroke(f'M{f2(a[0] + ax[0] * 0.012 * p)},{f2(a[1] + ax[1] * 0.012 * p)} L{f2(b[0] + ax[0] * 0.012 * p)},{f2(b[1] + ax[1] * 0.012 * p)}', '#EEF3FF', 0.014 * p))
        for t in (0.25, 0.5, 0.75):
            q = a + (b - a) * t
            out.append(circ(q, 0.012 * p, '#5A6684'))
        # 布の すみに 金の 星
        x0, x1, yt, yb, trim = m['cloth']
        sc = V(x1 - 0.1 * p if m['fx'] > 0 else x0 + 0.1 * p, yt + 0.085 * p)
        cloth = [path('M' + ' L'.join(f'{f2(q[0])},{f2(q[1])}' for q in star_pts(sc, 0.055 * p, 0.024 * p)) + ' Z', '#F2D16B')]
        return dict(head=out, cloth=cloth)
    return acc


if __name__ == '__main__':
    u8, meta, frames, cam = gallop_sheet(PAL, SPOT, acc=acc_for, n=N, number='1', tag='pkspace', ground=GROUND, lift=6.0, workers=1)
    xs = [h[0] for fr in frames for h in fr[2]]
    meta['hx'] = [round(min(xs) / 2, 2), round(max(xs) / 2, 2)]        # ひづめの 左右の はし（ページの px）：影の 置き場
    meta['ground'] = GROUND / 2
    out = os.environ.get('OUT')
    if out:
        preview_png(u8, os.path.join(out, 'space_run.png'), bg=(20, 26, 52))
    bid = save_webp(u8, quality=90)
    record('space', 'run', bid, meta)
    print('run', bid, meta)
