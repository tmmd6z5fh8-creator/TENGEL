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
}
# ポーズ・置き場所（馬の絵がちょうど入る箱 x0, y0, x1, y1：下のふち＝ひづめ）・向き・影の色
SPOTS = {
    'newyear': dict(pose='prance', facing='left', box=(376, 50, 610, 296), azim=-6, shadow=('#6A0A0E', 0.30)),
    'snow': dict(pose='stand', facing='left', box=(394, 54, 627, 294), azim=-6, shadow=('#6E86A6', 0.30)),
    'autumn': dict(pose='walk', facing='right', box=(290, 59, 523, 294), azim=6, shadow=('#7A3A16', 0.30)),
    'sea': dict(pose='gallop', facing='right', box=(280, 64, 572, 266), azim=6, shadow=('#8A6A3A', 0.22)),
    'sakura': dict(pose='stand', facing='left', box=(421, 52, 649, 296), azim=-6, shadow=('#6A8A5A', 0.24),
                   throat=dict(neck_k=0.03, amount=0.5, jowl=1.0, chest=1.0)),          # のど元すっきり（まさちゃんのオレンジの線）
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


ACC = dict(newyear=acc_newyear, snow=acc_snow, autumn=acc_autumn, sea=acc_sea_all, sakura=acc_sakura)


def draw_cute(img, theme, W, Hh, spec=None, shadow_marks=None):
    """spec：ポーズやカメラを かえた spec（足ぶみのコマ：step_run.py）。shadow_marks：影の大きさを この目印（ひづめ・いちばん下）で決める（コマで影が動かないように）"""
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
