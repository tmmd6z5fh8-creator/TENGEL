"""海賊の 壁紙（壁紙パック・第4.92版）の 馬の 船長：いままでの 壁紙と 同じ 馬（horse_flat）に、三角帽（金の ふち・金の 蹄鉄の しるし・赤い 羽）・
   赤い スカーフ・布の すみに 金の 蹄鉄。左を 向いて 宝箱を 見て 立つ（止まった 1コマ）。
   python3 kisekae/pack/make/pirate_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の pirate.captain"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import still_sheet, save_webp, record, preview_png, FLAT  # noqa: E402
import numpy as np  # noqa: E402
from cute_horse import smooth, path, stroke, circ, ell, unit, V, f2  # noqa: E402

PAL = dict(body='#E6E1DA', shade='#B8B0A6', muzzle='#F4F0EA', mane='#3A3434', maneD='#211D1D', hoof='#4A4440', eye='#1A1414',
           blush='#E8A898', tack='#2A1A12', ring='#E8B84A', cloth='#8E1E1E', clothTrim='#E8B84A', num='#F6E2B0', saddle='#2A1C14',
           bodyShade='#D3CCC3')
SPOT = dict(pose='stand', facing='left', box=(232, 84, 446, 300), azim=-6, shadow=('#2A1A0E', 0.30), ext=(0.067, 0.0765))
GOLD, GOLD_D, HAT, HAT_D = '#F0C24E', '#A8781C', '#1E1A1C', '#0C0A0B'


def horseshoe(c, r, rot, col, hole):
    """蹄鉄（U が 上に ひらく）：中心 c・大きさ r・回す rot°"""
    pts_o, pts_i = [], []
    for k in range(25):
        a = math.radians(-200 + 220 * k / 24)          # 下を まわる U
        pts_o.append((math.cos(a) * r, -math.sin(a) * r * 1.08))
        pts_i.append((math.cos(a) * r * 0.58, -math.sin(a) * r * 0.64))
    pts = pts_o + pts_i[::-1]
    cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    tr = lambda q: V(c[0] + q[0] * cs - q[1] * sn, c[1] + q[0] * sn + q[1] * cs)
    d = 'M' + ' L'.join(f'{f2(tr(q)[0])},{f2(tr(q)[1])}' for q in pts) + ' Z'
    out = [path(d, col, 'stroke="#5A3A0A" stroke-width="0.6" stroke-linejoin="round"')]
    for k in (3, 8, 16, 21):
        a = math.radians(-200 + 220 * k / 24)
        out.append(circ(tr((math.cos(a) * r * 0.79, -math.sin(a) * r * 0.86)), r * 0.075, hole))
    return out


def acc(m):
    p, fx = m['p1u'], m['fx']
    hd = unit(m['head_dir'])
    # ---- 三角帽：頭の 上（耳の うしろ → 前髪の あいだ）に、ふねの 形の つば（前と うしろが 上へ 反る）と まるい 山
    tilt = -6.0
    up = V(-math.sin(math.radians(tilt)) * fx, -math.cos(math.radians(tilt)))
    br = unit(V(-up[1], up[0]))
    if br[0] * fx < 0:
        br = -br
    base = m['poll'] + (m['forelock'] - m['poll']) * 0.38 + up * 0.035 * p
    Z = 1.12
    L = lambda x, y: base + br * x * Z * p + up * y * Z * p
    crown = [L(-0.17, 0.02), L(-0.19, 0.12), L(-0.12, 0.22), L(0.0, 0.25), L(0.12, 0.22), L(0.18, 0.12), L(0.16, 0.02)]
    brim = [L(-0.36, 0.16), L(-0.30, 0.07), L(-0.16, 0.00), L(0.0, -0.025), L(0.16, 0.0), L(0.30, 0.08), L(0.37, 0.18),
            L(0.30, 0.15), L(0.16, 0.085), L(0.0, 0.065), L(-0.16, 0.085), L(-0.30, 0.13)]
    hat = [path(smooth(crown, sharp=(0, 6)), HAT),
           path(smooth([L(-0.16, 0.03), L(-0.17, 0.12), L(-0.10, 0.20), L(-0.02, 0.215), L(-0.06, 0.12), L(-0.08, 0.03)], sharp=(0, 5)), '#3A3236', 'fill-opacity=".55"'),
           path(smooth(brim, sharp=(0, 6)), HAT_D),
           stroke(smooth([L(-0.36, 0.16), L(-0.30, 0.13), L(-0.16, 0.085), L(0.0, 0.065), L(0.16, 0.085), L(0.30, 0.15), L(0.37, 0.18)], closed=False), GOLD, 0.028 * p),
           stroke(smooth([L(-0.33, 0.13), L(-0.28, 0.065), L(-0.15, 0.012), L(0.0, -0.012), L(0.15, 0.012), L(0.28, 0.07), L(0.34, 0.15)], closed=False), '#3A3236', 0.012 * p)]
    hat += horseshoe(L(0.02, 0.12), 0.055 * p, -math.degrees(math.atan2(br[1], br[0])) * 0 + (0 if fx > 0 else 0), GOLD, HAT_D)
    # 赤い 羽（うしろへ）
    fb = L(-0.14, 0.17)
    hat.insert(0, path(smooth([fb, L(-0.30, 0.34), L(-0.46, 0.36), L(-0.34, 0.27), L(-0.20, 0.18)], sharp=(0, 2)), '#C8322A'))
    hat.insert(1, stroke(smooth([fb, L(-0.28, 0.30), L(-0.44, 0.35)], closed=False), '#7A1414', 0.012 * p))
    # ---- 眼帯（目の 上・ひもは ひたい と 耳の うしろへ）
    e = m['eye']
    ang = math.degrees(math.atan2(hd[1], hd[0]))
    patch = [stroke(smooth([e + hd * 0.05 * p + up * 0.03 * p, (e + m['forelock']) / 2 + hd * 0.02 * p, m['forelock'] + up * 0.01 * p], closed=False), '#141010', 0.02 * p),
             stroke(smooth([e - hd * 0.05 * p + up * 0.01 * p, (e + m['poll']) / 2 - up * 0.01 * p, m['poll']], closed=False), '#141010', 0.02 * p),
             ell(e + up * 0.004 * p, 0.062 * p, 0.048 * p, ang, '#141010'),
             ell(e + up * 0.014 * p - hd * 0.01 * p, 0.03 * p, 0.012 * p, ang, '#3A3236')]
    # ---- 赤い スカーフ（首の 根もと・のどの 下で むすんで 三角が たれる）
    top, bot, ax = m['collar'](0.74)
    dv = unit(bot - top)
    a, b = top - dv * 0.02 * p, bot + dv * 0.015 * p
    mid = (a + b) / 2 - ax * 0.03 * p
    hh = 0.05 * p
    band = [a + ax * hh, mid + ax * hh, b + ax * hh, b - ax * hh, mid - ax * hh, a - ax * hh]
    k = b - dv * 0.01 * p
    nv = V(-dv[1], dv[0])
    tri = [k - ax * 0.07 * p, k + ax * 0.07 * p, k + dv * 0.2 * p + ax * 0.02 * p]
    neck = [path(smooth(band), '#C8322A'), path(smooth(tri, sharp=(0, 1, 2)), '#B02A22')]
    for t in (0.2, 0.45, 0.75):
        q = a + (b - a) * t
        neck.append(circ(q + ax * 0.012 * p, 0.012 * p, '#FFF1D8'))
    neck.append(circ(k + dv * 0.09 * p, 0.012 * p, '#FFF1D8'))
    neck.append(circ(k, 0.032 * p, '#8E1E1A'))
    # ---- 布の まん中に 金の 蹄鉄
    x0, x1, yt, yb, trim = m['cloth']
    cloth = horseshoe(V((x0 + x1) / 2, (yt + trim) / 2 + 0.01 * p), 0.085 * p, 0, GOLD, '#8E1E1E')
    return dict(head=hat, neck=neck, cloth=cloth)


if __name__ == '__main__':
    u8, meta, fr = still_sheet(PAL, SPOT, acc=acc, number='', tag='pkpirate', shadow=('#2A1A0E', 0.32))
    out = os.environ.get('OUT')
    if out:
        preview_png(u8, os.path.join(out, 'captain.png'), bg=(120, 160, 190))
    bid = save_webp(u8, quality=92)
    record('pirate', 'captain', bid, meta)
    print('captain', bid, meta)
