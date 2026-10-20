"""5つのテーマ（午年・雪・紅葉・海・桜）の競走馬（第2版：馬らしい形）：色・飾り・ポーズ・置き場所
   draw_cute(img, theme, W, Hh) → 馬（と影・白い息・しぶき）を重ねた img
   馬の形は horse_flat（3Dの馬の形を、ぺたっとした色でぬる）。飾りは馬の目印（首・耳・布）に合わせて置く。
   形はすべて一から作ったオリジナル"""
import math
import numpy as np
import cv2
from cute_horse import smooth, V, unit, f2, path, stroke, circ, ell, mix
from horse_flat import draw_horse

PALS = {
    'newyear': dict(body='#FFFFFF', shade='#E2CCC6', muzzle='#F9E0D8', mane='#EDBF52', maneD='#C9952E', hoof='#7A4A3A', eye='#2A1410',
                    blush='#F5A49A', tack='#C8161D', ring='#F2C14E', cloth='#C8161D', clothTrim='#F2C14E', num='#FFF6E4', saddle='#2A1714',
                    bodyShade='#F1E6E2'),
    'snow': dict(body='#B7C2D1', shade='#8F9BB0', muzzle='#DCE3EC', mane='#F7F9FC', maneD='#D2DAE5', hoof='#4C5466', eye='#1E2230',
                 blush='#F1B3BE', tack='#22375A', ring='#E9EEF5', cloth='#2C4874', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#252A37',
                 bodyShade='#A6B1C3'),
    'autumn': dict(body='#D27B3D', shade='#A65628', muzzle='#F0BA8D', mane='#F6D9A4', maneD='#E0B676', hoof='#4A3328', eye='#2A160C',
                   blush='#F08A6A', tack='#5A2A18', ring='#F6B93B', cloth='#B5281F', clothTrim='#F6B93B', num='#FFF4E0', saddle='#4A2A1E',
                   bodyShade='#C06A32'),
    'sea': dict(body='#B5693A', shade='#874825', muzzle='#DEA87E', mane='#3A2A25', maneD='#221916', hoof='#2E2A2E', eye='#1E120C',
                blush='#F2A07A', tack='#1F3E66', ring='#FFFFFF', cloth='#1E5AA8', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#22252E',
                bodyShade='#A35C31'),
    'sakura': dict(body='#FFFFFF', shade='#DFD3E7', muzzle='#FCE4EE', mane='#F5A6C4', maneD='#E27FA8', hoof='#8C7A86', eye='#3A2440',
                   blush='#F7A8C8', tack='#C95E8C', ring='#FFFFFF', cloth='#F28DB2', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#5B3B4A',
                   bodyShade='#EFE8F3'),
    # 行事の4テーマ（まさちゃんの指定・flat/event_art.py と flat/<テーマ>_banner.py）
    'xmas': dict(body='#A0612F', shade='#79451F', muzzle='#CF9A72', mane='#2C1C16', maneD='#160D09', hoof='#2E2420', eye='#1A100A',
                 blush='#EE8C72', tack='#2C1C16', ring='#F2C14E', cloth='#D7323A', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#2B1A12',
                 bodyShade='#8E5429'),
    'halloween': dict(body='#DAD6E4', shade='#A8A1BE', muzzle='#EEEAF5', mane='#3B2A50', maneD='#22172F', hoof='#4A4058', eye='#1E1630',
                      blush='#F0A2B6', tack='#2A1E38', ring='#FF8A1F', cloth='#4B2A6E', clothTrim='#FF8A1F', num='#FFE2B8', saddle='#1E1428',
                      bodyShade='#C6C1D5'),
    'valentine': dict(body='#7C4A30', shade='#5A3420', muzzle='#B37C5A', mane='#F6E6CF', maneD='#E0C6A2', hoof='#3A2418', eye='#1E1008',
                      blush='#F08A9C', tack='#4A2A1A', ring='#F7A8C0', cloth='#E8547C', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#3A2018',
                      bodyShade='#6C3F27'),
    'whiteday': dict(body='#FFFFFF', shade='#BFD0E2', muzzle='#F4F7FB', mane='#A9D2EE', maneD='#7FB6DE', hoof='#7A8A9C', eye='#22304A',
                     blush='#F5B5C8', tack='#4A7DB0', ring='#FFFFFF', cloth='#79B4E0', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#3B4E66',
                     bodyShade='#E2EAF3'),
}
# ポーズ・置き場所（馬の絵がちょうど入る箱 x0, y0, x1, y1：下のふち＝ひづめ）・向き・影の色
SPOTS = {
    'newyear': dict(pose='prance', facing='left', box=(376, 50, 610, 296), azim=-6, shadow=('#6A0A0E', 0.30)),
    'snow': dict(pose='stand', facing='left', box=(394, 54, 627, 294), azim=-6, shadow=('#6E86A6', 0.30)),
    'autumn': dict(pose='walk', facing='right', box=(290, 59, 523, 294), azim=6, shadow=('#7A3A16', 0.30)),
    'sea': dict(pose='gallop', facing='right', box=(280, 64, 572, 266), azim=6, shadow=('#8A6A3A', 0.22)),
    'sakura': dict(pose='stand', facing='left', box=(421, 52, 649, 296), azim=-6, shadow=('#6A8A5A', 0.24),
                   throat=dict(neck_k=0.03, amount=0.5, jowl=1.0, chest=1.0)),          # のど元すっきり（まさちゃんのオレンジの線）
    'xmas': dict(pose='stand', facing='right', box=(300, 66, 512, 298), azim=6, shadow=('#8FA9C8', 0.30)),
    'halloween': dict(pose='stand', facing='left', box=(262, 74, 478, 300), azim=-6, shadow=('#0E0818', 0.45)),
    'valentine': dict(pose='stand', facing='right', box=(100, 62, 318, 298), azim=6, shadow=('#C9708E', 0.30)),
    'whiteday': dict(pose='stand', facing='left', box=(470, 62, 688, 298), azim=-6, shadow=('#8FB4D6', 0.30)),
}


def rope(a, b, sag, w, c1, c2, n=6, edge='#7A0A10'):
    """紅白の綱：2色のしまの太い線"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid = (a + b) / 2 + np.asarray(sag, float)
    P = [(1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t ** 2 * b for t in np.linspace(0, 1, n * 4 + 1)]
    out = [stroke(smooth(P[::2], closed=False), edge, w * 1.24), stroke(smooth(P[::2], closed=False), c1, w)]
    k_ = w / 9.5
    for k in range(n * 2):
        if k % 2:
            continue
        q0, q1 = P[k * 2], P[k * 2 + 2]
        dv = unit(q1 - q0)
        nv = np.array([-dv[1], dv[0]])
        poly = [q0 + nv * w / 2 + dv * 1.5 * k_, q1 + nv * w / 2 + dv * 2.5 * k_, q1 - nv * w / 2 - dv * 1.5 * k_, q0 - nv * w / 2 - dv * 2.5 * k_]
        out.append(path('M' + ' L'.join(f'{f2(p[0])},{f2(p[1])}' for p in poly) + ' Z', c2))
    return out, P


def acc_newyear(m):
    """首のつけねの紅白の綱と金の鈴"""
    p = m['p1u']
    top, bot, ax = m['collar'](0.12)
    dv = unit(bot - top)
    out, P = rope(top - dv * 0.02 * p, bot + dv * 0.02 * p, -ax * 0.06 * p, 0.088 * p, '#E0262E', '#FFFFFF', n=6)
    hang = P[len(P) // 2 + 2]
    br = 0.092 * p
    bell = hang + V(0, 0.13 * p)
    out.append(stroke(smooth([hang, bell + V(0, -br * 0.7)], closed=False), '#C8161D', 0.022 * p))      # 鈴のひも
    out += [circ(bell, br, '#E9B949'), circ(bell + V(-br * 0.3, -br * 0.3), br * 0.33, '#FFF0B8'),
            stroke(f'M{f2(bell[0] - br * 0.7)},{f2(bell[1] + br * 0.29)} H{f2(bell[0] + br * 0.7)}', '#9A6A14', 0.018 * p),
            circ(bell + V(0, br * 0.6), br * 0.17, '#7A4A10')]
    return dict(neck=out)


def acc_snow(m):
    """毛糸のマフラー（首）・まだら模様（胴）・白い息"""
    p, fx = m['p1u'], m['fx']
    top, bot, ax = m['collar'](0.16)
    dv = unit(bot - top)                                              # 首の上 → のど
    a, b = top - dv * 0.025 * p, bot + dv * 0.02 * p
    mid = (a + b) / 2 - ax * 0.045 * p                               # 体がわへ少したれる
    hh = 0.088 * p                                                   # 太さの半分（首にそって）
    band = [a + ax * hh, mid + ax * hh, b + ax * hh, b - ax * hh, mid - ax * hh, a - ax * hh]
    neck = [path(smooth(band), '#7FAEDB')]
    for t in (0.2, 0.42, 0.64, 0.86):                                 # 白いしま
        c = a + (b - a) * t + (mid - (a + b) / 2) * math.sin(math.pi * t)
        neck.append(stroke(smooth([c + ax * hh * 0.9, c - ax * hh * 0.9], closed=False), '#FFFFFF', 0.036 * p))
    # のどの結び目から、下へたれる端（ふさつき）
    k0 = b - dv * 0.05 * p - ax * 0.02 * p
    q = lambda x, y: k0 + V(x * fx, y) * p
    end = [q(-0.06, -0.02), q(0.06, 0.02), q(0.10, 0.33), q(0.0, 0.37), q(-0.04, 0.15)]
    neck.append(path(smooth(end, sharp=(2, 3)), '#6E9FD0'))
    neck.append(stroke(smooth([q(-0.01, 0.13), q(0.06, 0.21)], closed=False), '#FFFFFF', 0.034 * p))
    for j in range(4):
        p0 = q(0.10, 0.33) + (q(0.0, 0.37) - q(0.10, 0.33)) * (j / 3)
        neck.append(stroke(f'M{f2(p0[0])},{f2(p0[1])} l{f2((-0.01 + j * 0.004) * p * fx)},{f2(0.065 * p)}', '#6E9FD0', 0.024 * p))
    neck.append(circ(k0, 0.065 * p, '#7FAEDB'))                       # 結び目
    # まだら（胴とおしり）：u は き甲 0 → おしり 1、v は布の上のふちから下へ（m）
    xw, xb = m['torso']
    yt = m['cloth'][2]
    dap = []
    for (u, v, r) in ((0.80, 0.30, 0.10), (0.67, 0.17, 0.075), (0.90, 0.53, 0.07), (0.63, 0.43, 0.085), (0.76, 0.67, 0.065),
                      (0.97, 0.24, 0.07), (0.86, 0.10, 0.06), (0.55, 0.62, 0.06), (0.0, 0.56, 0.065), (-0.07, 0.36, 0.055), (0.06, 0.74, 0.05)):
        dap.append(circ(V(xw + (xb - xw) * u, yt + v * p), r * p, '#CBD4E0'))
    # 白い息（鼻の前に3つ）
    mz = m['P1'](m['hp'](0.58, 0.0, 0.0))                             # 鼻の穴の前から
    front = []
    for i, (d, r) in enumerate(((0.10, 0.062), (0.22, 0.088), (0.36, 0.11))):
        c = mz + V(fx * d * p, 0.01 * p - i * 0.026 * p)
        front.append(circ(c, r * p, '#FFFFFF', 'fill-opacity=".72"'))
    return dict(neck=neck, dapples=dap, front=front)


def maple(c, r, rot, col):
    pts = []
    for k in range(5):
        a0 = math.radians(rot - 90 + k * 72)
        L = r * (1.0 if k in (0, 1, 4) else 0.78)
        for da, rr in ((-0.5, 0.36), (-0.26, 0.7), (-0.14, 0.6), (0.0, 1.0), (0.14, 0.6), (0.26, 0.7), (0.5, 0.36)):
            pts.append(np.asarray(c, float) + np.array([math.cos(a0 + da), math.sin(a0 + da)]) * L * rr)
    return path('M' + ' L'.join(f'{f2(p[0])},{f2(p[1])}' for p in pts) + ' Z', col)


def cloth_corner(m, du=0.12, dv=0.13):
    """布のうしろの上のすみ（飾り用）"""
    p, fx = m['p1u'], m['fx']
    x0, x1 = m['cloth'][:2]
    xb = x0 if fx > 0 else x1
    x = xb + fx * du * p
    return V(x, m['cloth_top'](x) + dv * p)


def acc_autumn(m):
    """もみじの髪かざり（耳のつけね）と、布のすみのもみじ"""
    p, hp, side = m['p1u'], m['hp'], m['side']
    c = m['P1'](hp(0.05, 0.10, 0.095 * side))
    head = [maple(c, 0.105 * p, 18, '#E2452A'), circ(c, 0.022 * p, '#F6B93B')]
    cloth = [maple(cloth_corner(m), 0.08 * p, -10, '#F6B93B')]
    return dict(head=head, cloth=cloth)


def acc_sea(m):
    """布に白いしま（マリン）"""
    p = m['p1u']
    x0, x1, yt = m['cloth'][:3]
    out = [f'<defs><clipPath id="seacloth"><path d="{m["cloth_d"]}"/></clipPath></defs><g clip-path="url(#seacloth)">']
    for off in (0.085, 0.165):                                        # まっすぐ横のしま（布の上のふちから）
        y = yt + off * p
        out.append(f'<rect x="{f2(x0 - 4)}" y="{f2(y - 0.02 * p)}" width="{f2(x1 - x0 + 8)}" height="{f2(0.04 * p)}" fill="#FFFFFF" fill-opacity=".95"/>')
    out.append('</g>')
    return dict(cloth=out)


def sakura_flower(c, r, rot, col, core):
    out = []
    for k in range(5):
        a = math.radians(rot + k * 72)
        pc = np.asarray(c, float) + np.array([math.cos(a), math.sin(a)]) * r * 0.55
        tip = np.asarray(c, float) + np.array([math.cos(a), math.sin(a)]) * r * 1.05
        nv = np.array([-math.sin(a), math.cos(a)])
        pts = [np.asarray(c, float), pc + nv * r * 0.42, tip + nv * r * 0.16, tip - np.array([math.cos(a), math.sin(a)]) * r * 0.12,
               tip - nv * r * 0.16, pc - nv * r * 0.42]
        out.append(path(smooth(pts, sharp=(0, 3)), col))
    out.append(circ(c, r * 0.22, core))
    return out


def acc_sakura(m):
    """耳もとの桜の花かざりと、布のすみの桜"""
    p, hp, side, P1 = m['p1u'], m['hp'], m['side'], m['P1']
    head = sakura_flower(P1(hp(0.03, 0.085, 0.10 * side)), 0.115 * p, 10, '#FFFFFF', '#F28DB2')
    head += sakura_flower(P1(hp(0.13, 0.115, 0.10 * side)), 0.078 * p, 40, '#F9C9DA', '#E27FA8')
    cloth = sakura_flower(cloth_corner(m), 0.078 * p, 0, '#FFFFFF', '#E27FA8')
    return dict(head=head, cloth=cloth)


def acc_sea_splash(m, rng_seed=311):
    """しぶき：地面に近い2つのひづめから、うしろへ"""
    p = m['p1u']
    rng = np.random.default_rng(rng_seed)
    g0 = m['bottom_guess']
    low2 = sorted(m['hooves'], key=lambda h: -h[1])[:2]
    front, back = [], []
    k = p / 92.0
    for (hx, hy) in low2:
        for i in range(16):
            ang = rng.uniform(-math.pi * 0.92, -math.pi * 0.40)
            d = rng.uniform(5, 30) * k
            x, y = hx + math.cos(ang) * d * 1.3, g0 - 1 + math.sin(ang) * d * 0.8
            front.append(circ(V(x, y), rng.uniform(1.3, 3.2) * k, '#FFFFFF', 'fill-opacity=".95"'))
        back.append(f'<ellipse cx="{f2(hx - 4 * k)}" cy="{f2(g0 + 1)}" rx="{f2(18 * k)}" ry="{f2(4.5 * k)}" fill="#FFFFFF" fill-opacity=".9"/>')
    return front, back


def acc_sea_all(m):
    d = acc_sea(m)
    m['bottom_guess'] = SPOTS['sea']['box'][3]
    front, back = acc_sea_splash(m)
    d['front'] = front
    d['back'] = back
    return d


def holly(c, r, col='#2F8A55', berry='#E23B3B'):
    """ひいらぎ（葉2まい・赤い実3つ）"""
    c = np.asarray(c, float)
    out = []
    for rot in (-28, 208):
        a = math.radians(rot)
        d, nv = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        P = [c, c + d * r * 0.5 + nv * r * 0.36, c + d * r * 0.8 + nv * r * 0.16, c + d * r * 1.25, c + d * r * 0.8 - nv * r * 0.16, c + d * r * 0.5 - nv * r * 0.36]
        out.append(path(smooth(P, sharp=(0, 3)), col))
    for dx, dy in ((-0.16, -0.12), (0.16, -0.12), (0.0, 0.14)):
        out.append(circ(c + V(dx * r, dy * r), r * 0.22, berry))
    return out


HAT_OVR = {}      # ためしに 変える時だけ（{'xmas': {'at': …}} のように テーマごと。ふだんは 空）


def hat_on_head(m, wid, hgt, col, colD, band, bandD, flop=True, brim=0.0, at=0.7, tilt=None, hang=(0.21, 0.12), back=0.075, sink=0.0, curve=0.0, wback=0.0, cone_tilt=None, theme=''):
    """馬の頭の上の 帽子（魔女の帽子＝ハロウィン・サンタの帽子＝いまは使っていない：クリスマスは トナカイの カチューシャ＝antler_band）。
       wid・hgt：はば・高さ（m）。flop：先が うしろへ たれて 白い玉（サンタ）。brim：つば の はば（m・魔女の帽子）
       at：のせる所（耳の うしろ（poll）＝0 → 前髪（forelock）＝1。0.5 が 頭の上の まん中）
       tilt：うしろへ かたむける 角度（度。None ＝ 頭の向きから決める＝まえの形）・hang：サンタの帽子の 先の たれかた（うしろへ・下へ。m）
       back：サンタの帽子の うしろがわの ふくらみ（m。大きいほど 耳を つつむ）
       sink：帽子を 頭に かぶせる 深さ（m。大きいほど 下へ）・curve：ふちの 白い帯（つば）の まん中を 下げて 頭を つつむ 丸み（m）
       wback：魔女の帽子の 山の うしろがわの ふくらみ（m）
       cone_tilt：サンタの帽子の 山だけの かたむき（度。None ＝ tilt と同じ。白い帯は tilt のまま）"""
    o = HAT_OVR.get(theme, {})
    wid, at, tilt, hang, back = o.get('wid', wid), o.get('at', at), o.get('tilt', tilt), o.get('hang', hang), o.get('back', back)
    sink, curve, brim, hgt, wback = o.get('sink', sink), o.get('curve', curve), o.get('brim', brim), o.get('hgt', hgt), o.get('wback', wback)
    cone_tilt, flop = o.get('cone_tilt', cone_tilt), o.get('flop', flop)
    p, fx = m['p1u'], m['fx']
    hd = unit(m['head_dir'])
    if tilt is None:
        up = unit(-hd + V(0, -0.9))
    else:
        up = V(-math.sin(math.radians(tilt)) * fx, -math.cos(math.radians(tilt)))
    br = unit(V(-up[1], up[0]))
    if br[0] * fx < 0:
        br = -br
    base = m['poll'] + (m['forelock'] - m['poll']) * at + up * (0.015 - sink) * p
    w = wid * p
    a_b, a_f = base - br * w * 0.5, base + br * w * 0.5
    out = []
    if brim:                                                     # 魔女の帽子：つば → 先の とがった 山（先は うしろへ 折れる）
        bw = (wid + brim) * p
        ang = math.degrees(math.atan2(br[1], br[0]))
        c0 = base - up * 0.005 * p
        out.append(f'<ellipse cx="{f2(c0[0])}" cy="{f2(c0[1])}" rx="{f2(bw * 0.5)}" ry="{f2((0.045 + curve) * p)}" fill="{colD}" transform="rotate({f2(ang)} {f2(c0[0])} {f2(c0[1])})"/>')
        k = base + up * hgt * 0.58 * p - br * 0.03 * p
        tip = k + up * hgt * 0.3 * p - br * 0.2 * p
        bk = a_b + up * 0.17 * p - br * wback * p                # うしろがわは 下を まっすぐ 立てて（wback：うしろへ ふくらませて） 耳を つつむ
        out.append(path(smooth([a_b, bk, k - br * 0.06 * p, tip, k + br * 0.07 * p, a_f], sharp=(0, 3, 5)), col))
        out.append(path(smooth([a_b + up * 0.035 * p, a_f + up * 0.035 * p, a_f + up * 0.1 * p, a_b + up * 0.1 * p], sharp=(0, 1, 2, 3)), band))
        out.append(path(smooth([tip, k + br * 0.07 * p, a_f + up * 0.1 * p, base + up * 0.12 * p + br * 0.02 * p, k + br * 0.01 * p], sharp=(0,)), '#FFFFFF', 'fill-opacity=".08"'))
        return out
    uc, bc = up, br                                                 # 山の 向き（cone_tilt が あれば 山だけ べつの かたむき）
    if cone_tilt is not None:
        uc = V(-math.sin(math.radians(cone_tilt)) * fx, -math.cos(math.radians(cone_tilt)))
        bc = unit(V(-uc[1], uc[0]))
        if bc[0] * fx < 0:
            bc = -bc
    top = base + uc * hgt * p                                       # 先が うしろへ まがる 山（いちばん上が まがり目）
    hang = top + V(-hang[0] * fx * p, hang[1] * p)
    inner = base + uc * hgt * 0.6 * p - bc * back * p
    out.append(path(smooth([a_b, a_b + uc * 0.14 * p, inner, hang, top + bc * 0.03 * p, a_f + uc * 0.2 * p, a_f], sharp=(0, 3, 6)), col))
    out.append(path(smooth([top + bc * 0.03 * p, a_f + uc * 0.2 * p, a_f, base + br * w * 0.12 + uc * 0.1 * p, top - uc * 0.07 * p + bc * 0.01 * p], sharp=(2,)), colD, 'fill-opacity=".38"'))
    if curve:                                                       # ふちの 白い帯：まん中を 下げて 頭を つつむ 丸み
        out.append(path(smooth([a_b - br * 0.03 * p - up * 0.03 * p, base - up * (0.03 + curve) * p, a_f + br * 0.03 * p - up * 0.03 * p,
                                a_f + br * 0.03 * p + up * 0.055 * p, base + up * (0.055 - curve) * p, a_b - br * 0.03 * p + up * 0.055 * p]), band))
    else:
        out.append(path(smooth([a_b - br * 0.03 * p - up * 0.03 * p, a_f + br * 0.03 * p - up * 0.03 * p, a_f + br * 0.03 * p + up * 0.055 * p,
                                a_b - br * 0.03 * p + up * 0.055 * p]), band))
    if flop:
        out += [circ(hang, 0.07 * p, band), circ(hang + V(0.018 * p, 0.022 * p), 0.04 * p, bandD)]
        out.append(circ(hang + V(-0.015 * p, -0.018 * p), 0.028 * p, '#FFFFFF'))
    return out


# トナカイの 角（ふわふわの 布の角）：角の 根もと 0,0 から、(上へ, 前へ) を 角の長さを 1 として。
# まさちゃんの 絵（「こうして！」）のとおり：幹は 前へ たおれて まっすぐ のび（先は 少し 前へ まがる）、枝は 2本とも 前へ よこに のびる
ANTLER_BEAM = ((0, 0), (0.45, -0.03), (0.8, 0.0), (1.0, 0.07))
ANTLER_TINES = (((0.30, -0.02), (0.53, 0.33)), ((0.56, -0.02), (0.74, 0.25)))


def antler(base, up, fwd, L, w, col, hi=None):
    """トナカイの 角 1本（太い まるい線：幹と 枝2本）。hi：前がわの 明るい すじ（なければ なし）"""
    P = lambda a, b: base + up * a * L + fwd * b * L
    out = [stroke(smooth([P(*q) for q in ANTLER_BEAM], closed=False), col, w)]
    for a0, a1 in ANTLER_TINES:
        out.append(stroke(smooth([P(*a0), P(*a1)], closed=False), col, w * 0.85))
    if hi:
        off = fwd * w * 0.24
        out.append(stroke(smooth([P(*q) + off for q in ANTLER_BEAM[1:]], closed=False), hi, w * 0.28, 'opacity=".9"'))
        for a0, a1 in ANTLER_TINES:
            mid = ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2)
            out.append(stroke(smooth([P(*mid), P(*a1)], closed=False), hi, w * 0.24, 'opacity=".85"'))
    return out


def antler_band(m, L=0.62, w=0.072, lean=66.0, at=(0.012, 0.057), band_pts=((0.04, -0.057), (0.072, -0.175)),
                col='#C99358', hi='#EBC089', band='#D7323A', bandD='#A9232B', bw=0.045):
    """トナカイの カチューシャ（まさちゃん「馬やっぱり帽子じゃなくて、トナカイのカチューシャにして！」→ 絵を そえて「こうして！」）：
       頭の上（耳の すぐ前・前髪の 上）に ふわふわの トナカイの角を 1本、前へ たおして 立てる（枝は 2本とも 前へ）。
       赤い カチューシャは 角の 根もとから 耳の 根もとの 前を 通って、目の うしろの 下（のど革の 上）まで。耳は かくさない（角の うしろ＝左）。
       L・w：角の長さ・太さ（m）・lean：角の かたむき（頭の うしろ向き（鼻先 → うなじ）から 前へ 何度 たおすか）・
       at：角の根もと（頭の目印 hp の (s, w)）・band_pts：カチューシャの 下の点（hp の (s, w)）・bw：カチューシャの はば（m）。
       角も カチューシャも 頭の 目印から 置くので、首を のばす コマでも 頭と いっしょに 動いて かたむく。もどり値は 頭の上に かく 部品"""
    p, fx = m['p1u'], m['fx']
    hp, P1, zz = m['hp'], m['P1'], 0.094 * m['side']
    bk = -unit(m['head_dir'])                                  # 頭の うしろ（鼻先 → うなじ）
    nm = V(-bk[1], bk[0]) * fx                                 # ひたいの 向き
    a = math.radians(lean)
    up = unit(bk * math.cos(a) + nm * math.sin(a))
    fw = V(-up[1], up[0]) * fx                                 # 角の 前（顔の 向き）
    base = np.asarray(P1(hp(at[0], at[1], zz)), float)
    bpts = [base] + [np.asarray(P1(hp(s_, w_, zz)), float) for s_, w_ in band_pts]
    out = [stroke(smooth(bpts, closed=False), bandD, bw * 1.25 * p), stroke(smooth(bpts, closed=False), band, bw * p)]
    return out + antler(base, up, fw, L * p, w * p, col, hi)


def acc_xmas(m):
    """トナカイの カチューシャ（頭の上に 前へ たおれた ふわふわの 角と、角の 根もとから 頭の 横を 下りる 赤い カチューシャ）・赤と緑の綱に 金の鈴（首）・布のすみに ひいらぎ"""
    p, fx = m['p1u'], m['fx']
    top, bot, ax = m['collar'](0.12)
    dv = unit(bot - top)
    out, P = rope(top - dv * 0.02 * p, bot + dv * 0.02 * p, -ax * 0.06 * p, 0.075 * p, '#D7323A', '#2F8A55', n=6, edge='#7A1414')
    hang = P[len(P) // 2 + 2]
    br = 0.085 * p
    bell = hang + V(0, 0.12 * p)
    out.append(stroke(smooth([hang, bell + V(0, -br * 0.7)], closed=False), '#7A1414', 0.02 * p))
    out += [circ(bell, br, '#F2C14E'), circ(bell + V(-br * 0.3, -br * 0.3), br * 0.33, '#FFF0B8'),
            stroke(f'M{f2(bell[0] - br * 0.7)},{f2(bell[1] + br * 0.29)} H{f2(bell[0] + br * 0.7)}', '#9A6A14', 0.018 * p),
            circ(bell + V(0, br * 0.6), br * 0.17, '#7A4A10')]
    # 頭：トナカイの カチューシャ（まさちゃん「馬やっぱり帽子じゃなくて、トナカイのカチューシャにして！」→ 絵を そえて「こうして！」：
    #     はじめは 耳の うしろに 角2本（うしろへ たおれる）だったのを、耳の 前に 1本・前へ たおして 枝も 前へ に した）。
    #     まえは サンタの帽子（hat_on_head：at 0.75・tilt −12・back 0.12・hang (0.19, 0.12)・sink 0・curve 0.018）
    cloth = holly(cloth_corner(m), 0.085 * p)
    return dict(neck=out, head=antler_band(m), cloth=cloth)


def acc_halloween(m):
    """魔女の帽子（黒に オレンジの帯・先は うしろへ 折れる）・布のすみに 小さな こうもり"""
    p, fx = m['p1u'], m['fx']
    # 帽子：頭の上に すっぽり かぶせる（まさちゃん「ハロウィンの馬の帽子の位置を、しっかり頭の中心に合わせて！」→「帽子もっと自然！」）。
    #       頭の まん中に 少し深く・前へ 12度（下を向いた 頭に そって、つばが おでこに かかる）。
    #       山の うしろがわを 下から まっすぐ 立てて ふくらませ、耳を つつむ（まえは うしろへ 約19度 → まっすぐ）
    hat = hat_on_head(m, 0.32, 0.62, '#2A1E38', '#140C1E', '#FF8A1F', '#C9661A', flop=False, brim=0.32, at=0.72, tilt=-12,
                      sink=0.035, wback=0.05, theme='halloween')
    c = cloth_corner(m, 0.14, 0.12)
    k = 0.0042 * p
    bat = (f'<g transform="translate({f2(c[0])} {f2(c[1])}) scale({f2(k * fx)} {f2(k)})"><path d="M0,-4 Q-6,-10 -10,-6 Q-18,-16 -30,-14 Q-26,-8 -28,-2 '
           'Q-22,-4 -18,2 Q-14,-2 -10,4 Q-6,0 0,6 Q6,0 10,4 Q14,-2 18,2 Q22,-4 28,-2 Q26,-8 30,-14 Q18,-16 10,-6 Q6,-10 0,-4 Z" fill="#FF8A1F"/></g>')
    return dict(head=hat, cloth=[bat])


def ribbon_bow(m, col, colD, heart=None):
    """首に まいた リボン（のどがわに ちょうむすび・2本の はし）。heart：布のすみの ハートの色"""
    p, fx = m['p1u'], m['fx']
    top, bot, ax = m['collar'](0.14)
    dv = unit(bot - top)
    a, b = top - dv * 0.02 * p, bot + dv * 0.01 * p
    mid = (a + b) / 2 - ax * 0.03 * p
    hh = 0.045 * p
    band = [a + ax * hh, mid + ax * hh, b + ax * hh, b - ax * hh, mid - ax * hh, a - ax * hh]
    neck = [path(smooth(band), col)]
    k = b - dv * 0.03 * p
    nv = V(-dv[1], dv[0])
    loop = lambda sgn: path(smooth([k, k + nv * sgn * 0.17 * p - dv * 0.1 * p, k + nv * sgn * 0.21 * p + dv * 0.02 * p, k + nv * sgn * 0.05 * p + dv * 0.05 * p], sharp=(0,)), col)
    tail = lambda sgn: path(smooth([k, k + nv * sgn * 0.06 * p + dv * 0.24 * p, k + nv * sgn * 0.13 * p + dv * 0.2 * p, k + nv * sgn * 0.03 * p + dv * 0.04 * p], sharp=(0, 1, 2)), colD)
    neck += [tail(1), tail(-1), loop(1), loop(-1), circ(k, 0.045 * p, colD), circ(k + V(-0.012 * p, -0.012 * p), 0.016 * p, '#FFFFFF', 'fill-opacity=".6"')]
    out = dict(neck=neck)
    if heart:
        c = cloth_corner(m, 0.13, 0.12)
        r = 0.07 * p
        out['cloth'] = [path(f'M{f2(c[0])},{f2(c[1] + r * 0.95)} C{f2(c[0] - r * 0.2)},{f2(c[1] + r * 0.75)} {f2(c[0] - r * 1.05)},{f2(c[1] + r * 0.25)} {f2(c[0] - r)},{f2(c[1] - r * 0.25)} '
                             f'C{f2(c[0] - r * 0.95)},{f2(c[1] - r * 0.85)} {f2(c[0] - r * 0.2)},{f2(c[1] - r * 0.95)} {f2(c[0])},{f2(c[1] - r * 0.42)} '
                             f'C{f2(c[0] + r * 0.2)},{f2(c[1] - r * 0.95)} {f2(c[0] + r * 0.95)},{f2(c[1] - r * 0.85)} {f2(c[0] + r)},{f2(c[1] - r * 0.25)} '
                             f'C{f2(c[0] + r * 1.05)},{f2(c[1] + r * 0.25)} {f2(c[0] + r * 0.2)},{f2(c[1] + r * 0.75)} {f2(c[0])},{f2(c[1] + r * 0.95)} Z', heart)]
    return out


def acc_valentine(m):
    """赤い リボン（首）・布のすみに 白い ハート"""
    return ribbon_bow(m, '#D7264A', '#A81A38', heart='#FFFFFF')


def acc_whiteday(m):
    """水色の リボン（首）・布のすみに 白い ハート"""
    return ribbon_bow(m, '#8CC4EC', '#5E9FD0', heart='#FFFFFF')


ACC = dict(newyear=acc_newyear, snow=acc_snow, autumn=acc_autumn, sea=acc_sea_all, sakura=acc_sakura, xmas=acc_xmas, halloween=acc_halloween,
           valentine=acc_valentine, whiteday=acc_whiteday)


def draw_cute(img, theme, W, Hh, spec=None, shadow_marks=None):
    """spec：ポーズやカメラを かえた spec（馬が動くコマ：step_run.py）。shadow_marks：影の大きさを この目印（ひづめ・いちばん下）で決める（コマで影が動かないように）"""
    sp = spec or SPOTS[theme]
    rgb, a, m = draw_horse(sp, PALS[theme], W, Hh, acc=ACC[theme], number='1', name='flat_' + theme)
    # 影（地面）：ぼかしは numpy で（いつも同じ絵になるように）
    col, k = sp['shadow']
    ms = shadow_marks or m
    xs = [h[0] for h in ms['hooves']]
    gy = ms['bottom']
    if theme == 'sea':
        shadow = ((min(xs) + max(xs)) / 2, gy + 3, (max(xs) - min(xs)) / 2 + 20, 6.0)
    else:
        shadow = ((min(xs) + max(xs)) / 2, gy + 1, (max(xs) - min(xs)) / 2 + 26, 7.0)
    sm = np.zeros((Hh * 4, W * 4), np.float32)
    cv2.ellipse(sm, (int(round(shadow[0] * 4)), int(round(shadow[1] * 4))), (int(round(shadow[2] * 4)), int(round(shadow[3] * 4))), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    sm = cv2.GaussianBlur(cv2.resize(sm, (W, Hh), interpolation=cv2.INTER_AREA), (0, 0), 3.4) * k
    img = img * (1 - sm[..., None]) + np.array([int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32) * sm[..., None]
    return img * (1 - a[..., None]) + rgb * a[..., None]
