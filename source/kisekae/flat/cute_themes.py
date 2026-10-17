"""5つのテーマ（午年・雪・紅葉・海・桜）のかわいい競走馬：色・飾り・ポーズ・置き場所
   draw_cute(img, theme, W, Hh) → 馬（と影・白い息・しぶき）を重ねた img
   形はすべて一から作ったオリジナル"""
import math
import numpy as np
import cv2
from cute_horse import cute_horse, number_svg, Place, svg_layer, smooth, V, unit, f2, path, stroke, circ, ell, TORSO, mix

PALS = {
    'newyear': dict(body='#FFFFFF', shade='#EAD6CF', muzzle='#F9E0D8', mane='#EDBF52', maneD='#C9952E', hoof='#7A4A3A', eye='#2A1410',
                    blush='#F5A49A', tack='#C8161D', ring='#F2C14E', cloth='#C8161D', clothTrim='#F2C14E', num='#FFF6E4', saddle='#2A1714'),
    'snow': dict(body='#B7C2D1', shade='#8F9BB0', muzzle='#DCE3EC', mane='#F7F9FC', maneD='#D2DAE5', hoof='#4C5466', eye='#1E2230',
                 blush='#F1B3BE', tack='#22375A', ring='#E9EEF5', cloth='#2C4874', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#252A37'),
    'autumn': dict(body='#D27B3D', shade='#AA5A2A', muzzle='#F0BA8D', mane='#F6D9A4', maneD='#E0B676', hoof='#4A3328', eye='#2A160C',
                   blush='#F08A6A', tack='#5A2A18', ring='#F6B93B', cloth='#B5281F', clothTrim='#F6B93B', num='#FFF4E0', saddle='#4A2A1E'),
    'sea': dict(body='#B5693A', shade='#8B4B27', muzzle='#DEA87E', mane='#3A2A25', maneD='#221916', hoof='#2E2A2E', eye='#1E120C',
                blush='#F2A07A', tack='#1F3E66', ring='#FFFFFF', cloth='#1E5AA8', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#22252E'),
    'sakura': dict(body='#FFFFFF', shade='#E6DCEC', muzzle='#FCE4EE', mane='#F5A6C4', maneD='#E27FA8', hoof='#8C7A86', eye='#3A2440',
                   blush='#F7A8C8', tack='#C95E8C', ring='#FFFFFF', cloth='#F28DB2', clothTrim='#FFFFFF', num='#FFFFFF', saddle='#5B3B4A'),
}
# ポーズ・置き場所（左上 x, y・大きさ・向き）・影の色
SPOTS = {
    'newyear': dict(pose='prance', x=376, y=296 - 290 * 0.85, sc=0.85, facing='left', shadow=('#6A0A0E', 0.30)),
    'snow': dict(pose='stand', x=372, y=294 - 290 * 0.86, sc=0.86, facing='left', shadow=('#6E86A6', 0.30)),
    'autumn': dict(pose='walk', x=262, y=294 - 290 * 0.88, sc=0.88, facing='right', shadow=('#7A3A16', 0.30)),
    'sea': dict(pose='gallop', x=268, y=0.0, sc=0.90, facing='right', shadow=('#8A6A3A', 0.22), ground=266.0),
    'sakura': dict(pose='stand', x=404, y=296 - 290 * 0.88, sc=0.88, facing='left', shadow=('#6A8A5A', 0.24)),
}


def rope(m, a, b, sag, w, c1, c2, n=18):
    """紅白の綱：2色のしまの太い線"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid = (a + b) / 2 + np.asarray(sag, float)
    P = [(1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t ** 2 * b for t in np.linspace(0, 1, n * 4 + 1)]
    out = [stroke(smooth(P[::2], closed=False), '#7A0A10', w + 2.2), stroke(smooth(P[::2], closed=False), c1, w)]
    for k in range(n * 2):
        if k % 2:
            continue
        q0, q1 = P[k * 2], P[k * 2 + 2]
        dv = unit(q1 - q0)
        nv = np.array([-dv[1], dv[0]])
        poly = [q0 + nv * w / 2 + dv * 1.5, q1 + nv * w / 2 + dv * 2.5, q1 - nv * w / 2 - dv * 1.5, q0 - nv * w / 2 - dv * 2.5]
        out.append(path('M' + ' L'.join(f'{f2(p[0])},{f2(p[1])}' for p in poly) + ' Z', c2))
    return out, P


def acc_newyear(m):
    """首の紅白の綱と金の鈴"""
    a, b, ax = m['collar'](0.10, 20.0, 22.0)                         # 首のつけねに、首輪のように
    out, P = rope(m, a, b, tuple(-ax * 5), 9.5, '#E0262E', '#FFFFFF', n=6)
    bell = P[len(P) // 2] + V(2, 11)
    out += [circ(bell, 8.6, '#E9B949'), circ(bell + V(-2.6, -2.6), 2.8, '#FFF0B8'), stroke(f'M{f2(bell[0] - 6)},{f2(bell[1] + 2.5)} H{f2(bell[0] + 6)}', '#9A6A14', 1.6),
            circ(bell + V(0, 5.2), 1.5, '#7A4A10')]
    # 鈴のひも
    out.append(stroke(smooth([P[len(P) // 2], bell + V(0, -6)], closed=False), '#C8161D', 2.0))
    return out


def acc_snow(m):
    """毛糸のマフラー（首）"""
    out = []
    a, b, ax = m['collar'](0.13, 20.0, 22.0)                         # 首のつけねに巻く（大きな頭の下で見えるように）
    mid = (a + b) / 2 - ax * 4
    dv = unit(b - a)
    nv = -ax                                                          # 首の下（体）がわ
    wd = 17.0
    hh = wd / 2                                                      # 太さは首にそって（頭がわ ↔ 体がわ）
    band = [a + ax * hh - dv * 3, mid + ax * hh, b + ax * hh + dv * 3, b - ax * hh + dv * 3, mid - ax * hh, a - ax * hh - dv * 3]
    out.append(path(smooth(band), '#7FAEDB'))
    for t in (0.2, 0.42, 0.64, 0.86):                                 # 白いしま
        c = a + (b - a) * t + (mid - (a + b) / 2) * math.sin(math.pi * t)
        out.append(stroke(smooth([c + ax * hh * 0.9, c - ax * hh * 0.9], closed=False), '#FFFFFF', 3.4))
    # のどの結び目から、下へたれる端（ふさつき）
    k0 = b - dv * 4 + nv * 3
    end = [k0 + V(-6, -2), k0 + V(6, 2), k0 + V(10, 30), k0 + V(0, 34), k0 + V(-4, 14)]
    out.append(path(smooth(end, sharp=(2, 3)), '#6E9FD0'))
    out.append(stroke(smooth([k0 + V(-1, 12), k0 + V(6, 20)], closed=False), '#FFFFFF', 3.2))
    for j in range(4):
        p0 = k0 + V(10, 30) + (V(0, 34) - V(10, 30)) * (j / 3)
        out.append(stroke(f'M{f2(p0[0])},{f2(p0[1])} l{f2(-1 + j * 0.4)},{f2(6)}', '#6E9FD0', 2.2))
    out.append(circ(k0, 6.0, '#7FAEDB'))                              # 結び目
    return out


def maple(c, r, rot, col):
    pts = []
    for k in range(5):
        a0 = math.radians(rot - 90 + k * 72)
        L = r * (1.0 if k in (0, 1, 4) else 0.78)
        for da, rr in ((-0.5, 0.36), (-0.26, 0.7), (-0.14, 0.6), (0.0, 1.0), (0.14, 0.6), (0.26, 0.7), (0.5, 0.36)):
            pts.append(np.asarray(c, float) + np.array([math.cos(a0 + da), math.sin(a0 + da)]) * L * rr)
    return path('M' + ' L'.join(f'{f2(p[0])},{f2(p[1])}' for p in pts) + ' Z', col)


def acc_autumn(m):
    """もみじの髪かざり（前髪のところ）と、布のすみのもみじ"""
    H = m['H']
    out = [maple(H(10, 22), 9, 18, '#E2452A'), circ(H(10, 22), 2.0, '#F6B93B')]
    out.append(maple(V(136, 132), 7, -10, '#F6B93B'))
    return out


def acc_sea(m):
    """布に白いしま（マリン）"""
    out = ['<defs><clipPath id="seacloth"><rect x="126" y="116" width="74" height="62" rx="9"/></clipPath></defs><g clip-path="url(#seacloth)">']
    for y in (124, 136):
        out.append(f'<rect x="120" y="{y}" width="90" height="5" fill="#FFFFFF" fill-opacity=".95"/>')
    out.append('</g>')
    return out


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
    H = m['H']
    out = sakura_flower(H(6, 22), 10, 10, '#FFFFFF', '#F28DB2') + sakura_flower(H(18, 24), 7, 40, '#F9C9DA', '#E27FA8')
    out += sakura_flower(V(138, 132), 7, 0, '#FFFFFF', '#E27FA8')
    return out


def acc_snow_body(m):
    """まだら模様（胴）"""
    out = [f'<defs><clipPath id="snowtorso"><path d="{smooth(TORSO)}"/></clipPath></defs><g clip-path="url(#snowtorso)">']
    for (x, y, r) in ((78, 150, 9), (96, 136, 7), (70, 172, 6), (104, 160, 8), (88, 184, 6), (122, 146, 6), (214, 168, 6), (226, 150, 5)):
        out.append(circ(V(x, y), r, '#CED6E1'))
    out.append('</g>')
    return out


ACC = dict(newyear=None, snow=acc_snow_body, autumn=acc_autumn, sea=acc_sea, sakura=acc_sakura)
ACC_NECK = dict(newyear=acc_newyear, snow=acc_snow, autumn=None, sea=None, sakura=None)


def horse_svg(theme):
    sp = dict(SPOTS[theme])
    if 'ground' in sp:                                               # 走る馬：いちばん下のひづめを地面に合わせる
        from cute_horse import cute_horse as _ch
        _, m0 = _ch(sp['pose'], PALS[theme], None)
        low = max(h[1] for h in m0['hooves'])
        sp['y'] = sp['ground'] - low * sp['sc']
        SPOTS[theme]['y'] = sp['y']
    pal = PALS[theme]
    parts, m = cute_horse(sp['pose'], pal, ACC[theme], acc_neck=ACC_NECK[theme])
    pl = Place(sp['x'], sp['y'], sp['sc'], sp['facing'], width=360.0)
    inner = [pl.g(parts), number_svg(m, pl, '1', pal['num'], 30 * sp['sc'])]
    return inner, m, pl


def draw_cute(img, theme, W, Hh):
    sp = SPOTS[theme]
    inner, m, pl = horse_svg(theme)
    hv = [pl(h) for h in m['hooves']]
    gy = 290 * sp['sc'] + sp['y']
    xs = [p[0] for p in hv]
    # 影（地面）：ぼかしは numpy で（いつも同じ絵になるように）
    col, k = sp['shadow']
    cx = (min(xs) + max(xs)) / 2
    rx = (max(xs) - min(xs)) / 2 + 26
    shadow = (cx, gy + 1, rx, 7.0)
    extra_back, extra_front = [], []
    if theme == 'snow':                                              # 白い息
        mz = pl(m['muzzle'])
        dx = -1 if sp['facing'] == 'left' else 1
        for i, (d, r) in enumerate(((12, 6), (24, 8.5), (38, 10.5))):
            c = mz + np.array([dx * d, -2 - i * 2.5])
            extra_front.append(circ(c, r, '#FFFFFF', 'fill-opacity=".72"'))
    if theme == 'sea':                                               # しぶき：地面に近い2つのひづめから、うしろへ
        rng = np.random.default_rng(311)
        g0 = sp['ground']
        low2 = sorted(hv, key=lambda h: -h[1])[:2]
        for (hx, hy) in low2:
            for i in range(16):
                ang = rng.uniform(-math.pi * 0.92, -math.pi * 0.40)
                d = rng.uniform(5, 30)
                x, y = hx + math.cos(ang) * d * 1.3, g0 - 1 + math.sin(ang) * d * 0.8
                extra_front.append(circ(V(x, y), rng.uniform(1.3, 3.2), '#FFFFFF', 'fill-opacity=".95"'))
            extra_back.append(f'<ellipse cx="{f2(hx - 4)}" cy="{f2(g0 + 1)}" rx="18" ry="4.5" fill="#FFFFFF" fill-opacity=".9"/>')
        xs2 = [p[0] for p in hv]
        shadow = ((min(xs2) + max(xs2)) / 2, g0 + 3, (max(xs2) - min(xs2)) / 2 + 20, 6.0)
    sm = np.zeros((Hh * 4, W * 4), np.float32)
    cv2.ellipse(sm, (int(round(shadow[0] * 4)), int(round(shadow[1] * 4))), (int(round(shadow[2] * 4)), int(round(shadow[3] * 4))), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    sm = cv2.GaussianBlur(cv2.resize(sm, (W, Hh), interpolation=cv2.INTER_AREA), (0, 0), 3.4) * k
    img = img * (1 - sm[..., None]) + np.array([int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32) * sm[..., None]
    layer = ''.join(extra_back) + ''.join(inner) + ''.join(extra_front)
    rgb, a = svg_layer(layer, W, Hh, scale=3, tmpname=f'cute_{theme}.png')
    return img * (1 - a[..., None]) + rgb * a[..., None]
