"""開運の絵（780×320・アニメの塗り）：白い地に金の光、まん中に銀の蹄鉄、その中に白い招き馬（flat/lucky_maneki.py）
   - 地：白（あたたかい白）に、うすい金の放射の光とやわらかい光の輪、すみにうすい青海波
   - 蹄鉄：銀（本物の蹄鉄の形：つま先のでっぱり・溝・くぎ穴・四角い頭のくぎ・丸いかかと）。くっきりした影と白いつや・太い線
   - まわり：金貨・桜・四つ葉・金と赤のキラキラ（どれも太い線とくっきりした影）
   ぜんぶSVGで描いて Chromium で2倍に描き、縮める。形はすべて一から作ったオリジナル
   python3 flat/lucky_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
sys.path.insert(0, HERE)
from style2d import save_webp, TMP
from flat_horse import to_png
from lucky_maneki import maneki_svg, VB_W as MW, VB_H as MH, OUT

W, Hh = 780, 320
SC = 2                                  # 描く倍率


def f2(v):
    return f'{v:.2f}'


def poly(pts):
    return 'M' + ' L'.join(f'{f2(x)} {f2(y)}' for x, y in pts) + ' Z'


def shoe_svg(cx, cy, rx, ry, web=(42, 36, 30), th0=152):
    """銀の蹄鉄（U が上に開く）。中心線は だ円の弧（下がつま先）。web：つま先・横・かかとの幅"""
    S = []
    ths = np.radians(np.linspace(-th0, th0, 241))
    cxs = cx + rx * np.sin(ths); cys = cy + ry * np.cos(ths)
    C = np.stack([cxs, cys], 1)
    tg = np.gradient(C, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    nr = np.stack([tg[:, 1], -tg[:, 0]], 1)                     # 外向き
    if np.dot(nr[120], C[120] - np.array([cx, cy])) < 0:
        nr = -nr
    a = np.abs(np.degrees(ths)) / th0
    wd = np.interp(a, [0, 0.45, 1.0], web)
    outer = C + nr * (wd / 2)[:, None]
    inner = C - nr * (wd / 2)[:, None]
    # かかとは丸く
    def cap(i, fwd):
        """外がわ → 先 → 内がわ と回る半円（fwd：先の向き）"""
        c0 = C[i]; r = wd[i] / 2
        base = math.atan2(nr[i][1], nr[i][0])
        sgn = 1.0 if (nr[i][0] * fwd[1] - nr[i][1] * fwd[0]) > 0 else -1.0
        return [(c0[0] + r * math.cos(base + sgn * t), c0[1] + r * math.sin(base + sgn * t)) for t in np.linspace(0, math.pi, 13)]
    end_cap = cap(len(C) - 1, tg[-1])
    start_cap = cap(0, -tg[0])
    body = list(map(tuple, outer)) + end_cap[1:-1] + list(map(tuple, inner[::-1])) + start_cap[::-1][1:-1]
    D = poly(body)
    # 厚み（下と右の外がわの側面）
    side = list(map(tuple, outer + np.array([3.5, 7.0]))) + list(map(tuple, outer[::-1]))
    S.append(f"<path d='{poly(side)}' fill='#7E8A99' stroke='{OUT}' stroke-width='4' stroke-linejoin='round'/>")
    S.append(f"<path d='{D}' fill='#E8EDF3' stroke='{OUT}' stroke-width='4.4' stroke-linejoin='round'/>")
    # 影（内がわのふちにそって・右がわは広く）
    sh_w = wd * (0.30 + 0.22 * (np.sin(ths) > 0) * np.abs(np.sin(ths)))
    shp = list(map(tuple, inner)) + list(map(tuple, (inner + nr * sh_w[:, None])[::-1]))
    S.append(f"<path d='{poly(shp)}' fill='#BAC4D1'/>")
    # 溝（外がわ寄り・左右の枝）と、くぎ穴・くぎ
    for sgn in (-1, 1):
        sel = [i for i in range(len(C)) if 0.20 < sgn * np.degrees(ths[i]) / th0 < 0.90]
        g = C[sel] + nr[sel] * (wd[sel] * 0.12)[:, None]
        gw = wd[sel] * 0.20
        gpoly = list(map(tuple, g + nr[sel] * (gw / 2)[:, None])) + list(map(tuple, (g - nr[sel] * (gw / 2)[:, None])[::-1]))
        S.append(f"<path d='{poly(gpoly)}' fill='#9AA6B5' stroke='{OUT}' stroke-width='2' stroke-linejoin='round'/>")
        hl = g - nr[sel] * (gw / 2 + 1.6)[:, None]
        S.append("<path d='M" + ' L'.join(f'{f2(x)} {f2(y)}' for x, y in hl) + "' fill='none' stroke='#FFFFFF' stroke-width='1.8' stroke-linecap='round'/>")
        for k, f in enumerate((0.30, 0.47, 0.63, 0.80)):
            th = math.radians(sgn * f * th0)
            i = int(round((th + math.radians(th0)) / (2 * math.radians(th0)) * (len(C) - 1)))
            p = C[i] + nr[i] * wd[i] * 0.12
            ang = math.degrees(math.atan2(tg[i][1], tg[i][0]))
            if k in (0, 3):                                  # くぎ：四角い頭（古いくぎの色）
                S.append(f"<g transform='translate({f2(p[0])} {f2(p[1])}) rotate({f2(ang)})'>"
                         f"<rect x='-6.5' y='-6.5' width='13' height='13' rx='2.2' fill='#7A4E2C' stroke='{OUT}' stroke-width='2.4'/>"
                         f"<rect x='-3.8' y='-4.6' width='5.5' height='4' rx='1.2' fill='#B98457'/>"
                         f"<path d='M-6.5 3.5 L6.5 3.5' stroke='#4E2F18' stroke-width='2'/></g>")
            else:                                            # 空いた くぎ穴
                S.append(f"<g transform='translate({f2(p[0])} {f2(p[1])}) rotate({f2(ang)})'>"
                         f"<rect x='-5.5' y='-2.8' width='11' height='5.6' rx='1.4' fill='#3B4250' stroke='{OUT}' stroke-width='1.4'/></g>")
    # つま先のでっぱり（まん中の下）
    i0 = len(C) // 2
    p = C[i0] + nr[i0] * (wd[i0] / 2 - 1)
    S.append(f"<path d='M{f2(p[0] - 14)} {f2(p[1] - 2)} C{f2(p[0] - 12)} {f2(p[1] + 9)} {f2(p[0] + 12)} {f2(p[1] + 9)} {f2(p[0] + 14)} {f2(p[1] - 2)} Z' "
             f"fill='#C9D2DD' stroke='{OUT}' stroke-width='3' stroke-linejoin='round'/>")
    q = C[i0] + nr[i0] * (wd[i0] * 0.05)
    S.append(f"<rect x='{f2(q[0] - 9)}' y='{f2(q[1] - 3)}' width='18' height='6' rx='2' fill='#9AA6B5' stroke='{OUT}' stroke-width='1.6'/>")
    # 白いつや（左の枝に長い光、右の枝に短い光）
    for sgn, f0, f1, wk in ((-1, 0.25, 0.85, 0.16), (1, 0.55, 0.80, 0.10)):
        sel = [i for i in range(len(C)) if f0 < sgn * np.degrees(ths[i]) / th0 < f1]
        hp = C[sel] - nr[sel] * (wd[sel] * 0.16)[:, None]
        S.append("<path d='M" + ' L'.join(f'{f2(x)} {f2(y)}' for x, y in hp) +
                 f"' fill='none' stroke='#FFFFFF' stroke-width='{f2(float(np.mean(wd[sel])) * wk)}' stroke-linecap='round'/>")
    # かかとの丸いつや
    for i in (0, len(C) - 1):
        c0 = C[i] - nr[i] * wd[i] * 0.10
        S.append(f"<circle cx='{f2(c0[0])}' cy='{f2(c0[1])}' r='{f2(wd[i] * 0.13)}' fill='#FFFFFF'/>")
    return ''.join(S)


def coin_svg(x, y, r, rot=0):
    return (f"<g transform='translate({f2(x)} {f2(y)}) rotate({rot})'>"
            f"<ellipse cx='2' cy='4' rx='{f2(r)}' ry='{f2(r)}' fill='#B9781C' stroke='{OUT}' stroke-width='3.4'/>"
            f"<circle r='{f2(r)}' fill='#F7C744' stroke='{OUT}' stroke-width='3.4'/>"
            f"<circle r='{f2(r * 0.70)}' fill='none' stroke='#D99A2B' stroke-width='{f2(r * 0.10)}'/>"
            f"<path d='M{f2(-r * 0.62)} {f2(-r * 0.10)} A{f2(r * 0.64)} {f2(r * 0.64)} 0 0 1 {f2(r * 0.10)} {f2(-r * 0.62)}' fill='none' stroke='#FFF6C8' stroke-width='{f2(r * 0.16)}' stroke-linecap='round'/>"
            f"<rect x='{f2(-r * 0.20)}' y='{f2(-r * 0.20)}' width='{f2(r * 0.40)}' height='{f2(r * 0.40)}' fill='#C9851F' stroke='{OUT}' stroke-width='2'/>"
            "</g>")


def sakura_svg(x, y, r, rot=0):
    pet = []
    for k in range(5):
        a = rot + k * 72
        pet.append(f"<path transform='rotate({a})' d='M0 0 C{f2(-r * 0.55)} {f2(-r * 0.30)} {f2(-r * 0.55)} {f2(-r * 0.95)} {f2(-r * 0.16)} {f2(-r * 1.02)} "
                   f"L0 {f2(-r * 0.86)} L{f2(r * 0.16)} {f2(-r * 1.02)} C{f2(r * 0.55)} {f2(-r * 0.95)} {f2(r * 0.55)} {f2(-r * 0.30)} 0 0 Z' "
                   f"fill='#FFC4D2' stroke='{OUT}' stroke-width='2.6' stroke-linejoin='round'/>")
    return (f"<g transform='translate({f2(x)} {f2(y)})'>" + ''.join(pet) +
            f"<circle r='{f2(r * 0.26)}' fill='#F7C744' stroke='{OUT}' stroke-width='1.8'/></g>")


def clover_svg(x, y, r, rot=0):
    lv = []
    for k in range(4):
        a = rot + k * 90
        lv.append(f"<path transform='rotate({a})' d='M0 0 C{f2(-r * 0.75)} {f2(-r * 0.25)} {f2(-r * 0.80)} {f2(-r * 1.05)} {f2(-r * 0.30)} {f2(-r * 1.05)} "
                  f"C{f2(-r * 0.10)} {f2(-r * 1.05)} 0 {f2(-r * 0.85)} 0 {f2(-r * 0.80)} C0 {f2(-r * 0.85)} {f2(r * 0.10)} {f2(-r * 1.05)} {f2(r * 0.30)} {f2(-r * 1.05)} "
                  f"C{f2(r * 0.80)} {f2(-r * 1.05)} {f2(r * 0.75)} {f2(-r * 0.25)} 0 0 Z' fill='#5CC26E' stroke='{OUT}' stroke-width='2.6' stroke-linejoin='round'/>")
    return (f"<g transform='translate({f2(x)} {f2(y)})'>"
            f"<path d='M0 0 C{f2(r * 0.3)} {f2(r * 0.6)} {f2(r * 0.2)} {f2(r * 1.1)} {f2(-r * 0.1)} {f2(r * 1.4)}' fill='none' stroke='{OUT}' stroke-width='3' stroke-linecap='round'/>"
            + ''.join(lv) + "</g>")


def sparkle(x, y, r, fill='#FFD45A', rot=0):
    pts = []
    for i in range(8):
        a = math.radians(rot) + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.26
        pts.append(f'{f2(x + math.cos(a) * rr)},{f2(y + math.sin(a) * rr)}')
    return f"<polygon points='{' '.join(pts)}' fill='{fill}' stroke='{OUT}' stroke-width='1.6' stroke-linejoin='round'/>"


def banner_svg():
    S = []
    S.append("<defs>"
             "<radialGradient id='glow' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#FFF2C4' stop-opacity='1'/>"
             "<stop offset='0.55' stop-color='#FFF6DC' stop-opacity='0.75'/><stop offset='1' stop-color='#FFFDF8' stop-opacity='0'/></radialGradient>"
             "<radialGradient id='raysfade' cx='0.5' cy='0.5' r='0.5'><stop offset='0' stop-color='#fff' stop-opacity='1'/>"
             "<stop offset='0.7' stop-color='#fff' stop-opacity='0.5'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>"
             "<mask id='rm'><rect x='0' y='0' width='780' height='320' fill='url(#raysfade)'/></mask>"
             "<pattern id='sgh' width='36' height='18' patternUnits='userSpaceOnUse'>"
             + ''.join(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='#F1E4C6' stroke-width='1.1'/>"
                       for cx, cy in ((0, 18), (36, 18), (18, 9), (0, 0), (36, 0)) for r in (17, 12.5, 8, 3.5))
             + "</pattern>"
             "</defs>")
    S.append("<rect width='780' height='320' fill='#FFFDF8'/>")
    # すみの青海波（うすく）
    S.append("<g opacity='0.75'><path d='M0 0 H190 C150 40 110 60 0 70 Z' fill='url(#sgh)'/>"
             "<path d='M780 320 H560 C600 290 660 262 780 250 Z' fill='url(#sgh)'/></g>")
    # 放射の光
    rays = []
    n = 28
    for k in range(n):
        if k % 2:
            continue
        a0 = 2 * math.pi * k / n; a1 = 2 * math.pi * (k + 1) / n
        R = 520
        rays.append(f"M390 160 L{f2(390 + R * math.cos(a0))} {f2(160 + R * math.sin(a0))} L{f2(390 + R * math.cos(a1))} {f2(160 + R * math.sin(a1))} Z")
    S.append(f"<g mask='url(#rm)'><path d='{' '.join(rays)}' fill='#FFF0CC' opacity='0.85'/></g>")
    S.append("<ellipse cx='390' cy='160' rx='250' ry='200' fill='url(#glow)'/>")
    # 金貨・桜・四つ葉（うしろ）
    for (x, y, r, rot) in ((96, 62, 15, 10), (668, 52, 13, -14), (712, 168, 11, 20), (30, 150, 10, 0)):
        S.append(sakura_svg(x, y, r, rot))
    for (x, y, r, rot) in ((232, 52, 13, 15), (560, 66, 12, -20), (200, 262, 12, 40)):
        S.append(clover_svg(x, y, r, rot))
    # 蹄鉄
    S.append(shoe_svg(390, 150, 126, 118, web=(48, 42, 36), th0=146))
    # 招き馬
    ch = 236
    cw = ch * MW / MH
    S.append(f"<svg x='{f2(392 - cw / 2)}' y='{f2(314 - ch)}' width='{f2(cw)}' height='{f2(ch)}' viewBox='0 0 {MW} {MH}'>"
             + maneki_svg(MW, MH).split('>', 1)[1].rsplit('</svg>', 1)[0] + "</svg>")
    # 手前の金貨・桜
    for (x, y, r, rot) in ((112, 250, 25, 0), (160, 284, 20, 15), (640, 262, 27, -10), (694, 226, 18, 8)):
        S.append(coin_svg(x, y, r, rot))
    for (x, y, r, rot) in ((52, 262, 14, 30), (742, 290, 15, -12), (588, 296, 10, 4)):
        S.append(sakura_svg(x, y, r, rot))
    # キラキラ（金・赤）
    for (x, y, r, c) in ((150, 120, 9, '#FFD45A'), (618, 132, 10, '#FFD45A'), (276, 26, 7, '#FFD45A'), (520, 22, 6, '#FF8A80'),
                         (60, 110, 6, '#FF8A80'), (735, 100, 8, '#FFD45A'), (300, 300, 5, '#FFD45A'), (470, 300, 6, '#FF8A80')):
        S.append(sparkle(x, y, r, c))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='780' height='320' viewBox='0 0 780 320'>" + ''.join(S) + "</svg>"


if __name__ == '__main__':
    out = sys.argv[1]
    tmp = os.path.join(TMP, 'lucky_banner.png')
    to_png(banner_svg(), W, Hh, tmp, scale=SC)
    im = cv2.imread(tmp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    rgb = im[..., :3][..., ::-1]
    rgb = cv2.resize(rgb, (W, Hh), interpolation=cv2.INTER_AREA)
    save_webp(np.clip(rgb, 0, 1), out)
    print(out)
