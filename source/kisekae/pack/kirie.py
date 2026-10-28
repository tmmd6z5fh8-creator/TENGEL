"""壁紙パック ⑦切り絵（まさちゃんの 指定「紙を重ねた奥行きのある絵で、馬がぱたぱた走る」）
   上の絵：紙を 何まいも 重ねた 景色（空の 紙・紙の 太陽と 雲・遠くの 丘（小さな 木）・まん中の 丘（家と 木）・手前の 野原・いちばん 手前の 草と 花）。
     紙と 紙の あいだには やわらかい かげ（重なりの 奥行き）・紙の すじ（ざらっと した 手ざわり）。
     馬は 赤い 紙の 紙人形（体に 切りぬきの もよう・白い 紙が 下から のぞく・ティールの 鞍の 布・ぎざぎざの たてがみ）。足と しっぽは 金の ピンで とめた 別の 紙
   動き：馬の 足が ピンを 中心に ぱたぱた（ななめの 2本ずつ 交互）・体が ぴょこぴょこ 上下・しっぽが ゆれる。景色の 紙が 右から 左へ 流れる（遠いほど ゆっくり＝奥行き）・
     太陽が ゆっくり 回る・紙の 鳥が はばたいて 横切る。強く 光らせない
   第4.93版：足の ぱたぱたを 少し ゆっくり（1回り 0.5 → 0.68秒）・鳥の はねは 根もとを 体の 背中に 重ねて、根もとを 中心に はばたく（はなれて 見えない）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'kirie'
RED, REDD, CREAM, MAROON, TEAL, GOLD = '#D8473A', '#A63328', '#FFF4E0', '#7E2424', '#2F8A84', '#E2B24A'
TILE = 390
# 馬（紙人形）：絵の 単位（100×80・右向き）→ 舞台の px（SC 倍）。左上 HX, HY
SC, HX, HY = 1.12, 104, 46
BODY = [(18, 36), (22, 29), (32, 26.5), (46, 28.5), (56, 26), (62, 20), (67, 13), (72, 8), (79, 6.5), (86, 10), (92, 15.5), (96, 21), (94.5, 26.5),
        (90, 27.5), (83, 26.5), (77, 24.5), (72, 30), (67.5, 39), (65, 47), (61, 53), (48, 55), (31, 54), (22, 50.5), (16.5, 43)]
EAR = [(70.6, 8.6), (73, -2.6), (76.4, 6.8)]
PIV = dict(fn=(60, 45), hn=(25.5, 43), ff=(63, 44), hf=(29, 42), tail=(18.5, 33))     # ピンの 所（手前／奥の 前足・うしろ足・しっぽ）
LEG_PER = 0.68         # 足の ぱたぱた 1回り（秒）（第4.93版：まさちゃん「馬の脚の動きを少しゆっくりにして！」0.5 → 0.68）


def paper_defs(seed=4, blur=1.1):
    """紙の かげ（ぼかし）と 紙の すじ（ノイズ）の フィルター（data URI の 絵の 中だけ＝id は ぶつからない）"""
    return (f"<filter id='sh' x='-20%' y='-30%' width='140%' height='160%'><feGaussianBlur stdDeviation='{blur}'/></filter>"
            f"<filter id='tx' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' seed='{seed}'/>"
            "<feColorMatrix values='0 0 0 0 .32  0 0 0 0 .2  0 0 0 0 .1  0 0 0 .1 0'/><feComposite in2='SourceGraphic' operator='in'/></filter>")


def paper(d, col, sh=(1.1, 2.0, .32), tex=True, extra=''):
    """1まいの 紙：かげ（sh＝(dx, dy, こさ)・なし＝None）・色・紙の すじ"""
    o = ''
    if sh:
        o += f"<path d='{d}' fill='#4A2A18' opacity='{sh[2]}' transform='translate({sh[0]} {sh[1]})' filter='url(#sh)'/>"
    o += f"<path d='{d}' fill='{col}'/>"
    if tex:
        o += f"<path d='{d}' fill='#000' filter='url(#tx)'/>"
    return f'<g {extra}>{o}</g>' if extra else o


# ---------------------------------------------------------------- 馬（紙人形）
def body_svg():
    d = smooth(BODY, True, 0.6)
    cuts = ''
    for cx, cy, r in ((29, 40, 3.4), (39, 36.5, 2.6), (43, 46, 3), (33, 47.5, 2.2), (52, 41, 2.4), (24, 44, 2)):     # しずくの 切りぬき
        cuts += f" M{f(cx)} {f(cy - r)} Q{f(cx + r)} {f(cy)} {f(cx)} {f(cy + r * 1.4)} Q{f(cx - r)} {f(cy)} {f(cx)} {f(cy - r)} Z"
    for cx, cy, r in ((25.5, 37.5, 1.2), (47.5, 50, 1.3), (36.5, 31.5, 1), (56.5, 47, 1.1), (39.5, 52, .9)):         # まるい 切りぬき
        cuts += f" M{f(cx - r)} {f(cy)} a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0 a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0 Z"
    for k in range(3):                                                                                              # 首の 山形
        x, y = 65 + k * 2.6, 33 - k * 6.2
        cuts += f" M{f(x - 3)} {f(y + 2)} L{f(x)} {f(y - 1.6)} L{f(x + 3)} {f(y + 2)} L{f(x)} {f(y + 0.4)} Z"
    o = paper(d, CREAM, sh=(1.2, 2.2, .34), extra="transform='translate(-.9 -.9)'")
    o += paper(d + cuts, RED, sh=None, extra="fill-rule='evenodd'")
    o += paper(smooth(EAR, True, .4), RED, sh=None) + f"<path d='M72 7.6 L73 3 L74.8 7.4 Z' fill='{CREAM}'/>"
    sad = [(37, 28.4), (53, 27.4), (54.6, 38.4), (52, 41), (49, 38.8), (46, 41.4), (43, 38.8), (40, 41.4), (37.4, 38.6)]       # 鞍の 布
    o += paper(smooth(sad, True, .35), TEAL, sh=(.6, 1.4, .3)) + f"<path d='{star_d(45.6, 33, 3.1, 1.35)}' fill='{CREAM}'/>"
    mane = [(55, 27)]                                                                                               # たてがみ（ぎざぎざ）
    for k in range(7):
        t = (k + .5) / 7
        bx, by = 55 + (72.5 - 55) * t, 27 + (7.5 - 27) * t
        mane += [(bx - 1.6, by - 4.4), (bx + 1.3, by + 0.6)]
    mane += [(73, 6.4), (69.6, 11.6), (64.6, 18.6), (59.6, 24.4)]
    o += paper(P(mane), MAROON, sh=(.5, 1.2, .28))
    o += (f"<path d='M80.4 12.6 Q83.2 10.2 86 12.6 Q83.2 15 80.4 12.6 Z' fill='{CREAM}'/><circle cx='83.6' cy='12.6' r='1.3' fill='#2A1410'/>"
          f"<circle cx='84.1' cy='12.1' r='.4' fill='#FFFFFF'/>"
          f"<ellipse cx='93.2' cy='20.6' rx='1.1' ry='.8' fill='{MAROON}'/><path d='M89.6 25 Q91.8 25.9 94 25' fill='none' stroke='{MAROON}' stroke-width='.7' stroke-linecap='round'/>"
          f"<path d='M84 22 Q86.6 23 88.6 21.6' fill='none' stroke='#F2A08E' stroke-width='1.6' stroke-linecap='round' opacity='.7'/>")
    return doc(100, 80, o, vb='0 -6 100 80', defs=paper_defs())


def leg_svg(col, hind=False):
    """足：ピンの 所＝(0,0)・下へ。絵の 箱 -9〜9 × -7〜35"""
    if hind:
        pts = [(-6, -3), (-2, -6), (4, -4.5), (5.4, 4), (3.6, 13), (1.6, 22), (2.4, 26.4), (4.2, 30.6), (-3.6, 30.8), (-2.6, 26.4), (-3.2, 21),
               (-6.2, 14.4), (-5.6, 8)]
    else:
        pts = [(-5.2, -3), (-1, -5.6), (4.4, -3.4), (4.6, 6), (3.4, 15), (2.4, 23), (3, 26.6), (4.6, 30.6), (-3.4, 30.8), (-2.6, 26.4), (-2.8, 22),
               (-3.6, 14), (-4.8, 4)]
    d = smooth(pts, True, .35)
    hoof = P([(-3.6, 27.6), (3.6, 27.6), (4.6, 30.8), (-3.6, 30.9)])
    return doc(18, 42, paper(d, col) + f"<path d='{hoof}' fill='{mix(col, '#000000', .45)}'/>", vb='-9 -7 18 42', defs=paper_defs(7))


def tail_svg():
    o = ''
    for k, (ex, ey) in enumerate(((-12, 22), (-16, 17), (-17, 11), (-14, 26), (-7, 27))):
        d = smooth([(0, -2), (ex * .45 - 1.5, ey * .4 - 2), (ex - 1.2, ey), (ex + 1.4, ey + .4), (ex * .45 + 1.8, ey * .4), (1.6, 0)], True, .4)
        o += paper(d, MAROON if k % 2 == 0 else mix(MAROON, '#000000', .18), sh=(.6, 1.4, .28) if k == 0 else None)
    return doc(24, 34, o, vb='-19 -4 24 34', defs=paper_defs(9))


def pin_svg():
    return doc(8, 8, f"<circle cx='4' cy='4' r='3' fill='{GOLD}' stroke='#8A6420' stroke-width='.7'/><circle cx='3.1' cy='3.1' r='1' fill='#FFF2C8'/>")


# ---------------------------------------------------------------- 景色の 紙
def _wrap(x, w=TILE, pad=40):
    return [x + dx for dx in (-w, 0, w) if -pad <= x + dx <= w + pad]


def ridge(y0, amps, n=78):
    """くり返せる 丘の ふち（はば TILE で ちょうど 1周）"""
    pts = []
    for i in range(n + 1):
        x = TILE * i / n
        y = y0 + sum(a * math.sin(2 * math.pi * k * x / TILE + p) for a, k, p in amps)
        pts.append((x, y))
    return pts


def hill_svg(y0, amps, col, h, deco='', seed=1, shadow=.34):
    """1まいの 丘の 紙（はば TILE・高さ h）：上の ふちは ridge・かげ・紙の すじ・飾り（木・家）"""
    top = ridge(y0, amps)
    d = f"M0 {h + 4} L" + ' L'.join(f'{f(x)} {f(y)}' for x, y in top) + f" L{TILE} {h + 4} Z"
    o = paper(d, col, sh=(0, -.6, shadow)) + deco
    return doc(TILE, h, o, defs=paper_defs(seed, 1.8))


def tree(x, y, s, col, trunk='#8A5A3A'):
    """まるい 木（紙）：幹と まるい 葉っぱ・葉に 切りぬきの すじ"""
    return (paper(P([(x - 1.2 * s, y), (x + 1.2 * s, y), (x + .8 * s, y - 7 * s), (x - .8 * s, y - 7 * s)]), trunk, sh=None)
            + paper(f'M{f(x - 6 * s)} {f(y - 9 * s)} a{f(6 * s)} {f(6.5 * s)} 0 1 0 {f(12 * s)} 0 a{f(6 * s)} {f(6.5 * s)} 0 1 0 {f(-12 * s)} 0 Z', col, sh=(.4, 1, .28))
            + f"<path d='M{f(x)} {f(y - 4 * s)} V{f(y - 13 * s)} M{f(x)} {f(y - 8 * s)} l{f(-2.6 * s)} {f(-2.4 * s)} M{f(x)} {f(y - 10 * s)} l{f(2.6 * s)} {f(-2.4 * s)}' "
              f"stroke='{mix(col, '#FFFFFF', .35)}' stroke-width='{f(.8 * s)}' fill='none' stroke-linecap='round'/>")


def pine(x, y, s, col):
    """三角の 木"""
    return paper(P([(x, y - 16 * s), (x + 6 * s, y - 6 * s), (x + 3.4 * s, y - 6 * s), (x + 7.4 * s, y), (x - 7.4 * s, y), (x - 3.4 * s, y - 6 * s), (x - 6 * s, y - 6 * s)]), col, sh=(.3, .8, .25))


def house(x, y, s, wall, roof):
    o = paper(P([(x - 7 * s, y), (x + 7 * s, y), (x + 7 * s, y - 8 * s), (x - 7 * s, y - 8 * s)]), wall, sh=(.4, 1, .28))
    o += paper(P([(x - 9 * s, y - 7.5 * s), (x, y - 15 * s), (x + 9 * s, y - 7.5 * s)]), roof, sh=None)
    o += f"<rect x='{f(x - 4.6 * s)}' y='{f(y - 6 * s)}' width='{f(3 * s)}' height='{f(3 * s)}' fill='#F2C46A'/><rect x='{f(x + 1.4 * s)}' y='{f(y - 5 * s)}' width='{f(3 * s)}' height='{f(5 * s)}' fill='{mix(roof, '#000000', .3)}'/>"
    return o


def flower(x, y, r, col, core='#F7D35A'):
    o = ''
    for k in range(5):
        a = math.radians(-90 + k * 72)
        o += f"<ellipse cx='{f(x + math.cos(a) * r)}' cy='{f(y + math.sin(a) * r)}' rx='{f(r * .78)}' ry='{f(r * .55)}' transform='rotate({f(math.degrees(a))} {f(x + math.cos(a) * r)} {f(y + math.sin(a) * r)})' fill='{col}'/>"
    return o + f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r * .55)}' fill='{core}'/>"


def sky_svg():
    """空の 紙（うすい 桃色 → クリーム）と 遠い 山の 紙"""
    defs = paper_defs(2) + ("<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#F9D7C2'/><stop offset='.6' stop-color='#FCE9CF'/>"
                            "<stop offset='1' stop-color='#FFF3DE'/></linearGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#g)'/><rect width='{W}' height='{H}' fill='#000' filter='url(#tx)'/>"
    # 遠い 山（2まい・うすい 青むらさき）
    for pts, col in ((ridge(66, ((7, 2, .6), (4, 5, 1.8), (2, 9, .4))), '#C9C4E2'), (ridge(76, ((6, 3, 2.2), (3, 7, .9))), '#B3BEDD')):
        d = f"M0 {H} L" + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts) + f" L{W} {H} Z"
        o += paper(d, col, sh=(0, -.5, .2))
    return doc(W, H, o, defs=defs)


def sun_svg():
    """紙の 太陽（ぎざぎざの 光・二重の まる）。まん中 (40, 40)"""
    o = ''
    pts = []
    for k in range(32):
        a = math.radians(k * 360 / 32)
        r = 36 if k % 2 == 0 else 27
        pts.append((40 + math.cos(a) * r, 40 + math.sin(a) * r))
    o += paper(P(pts), '#F6B04A', sh=(.8, 1.6, .26))
    o += paper('M18 40 a22 22 0 1 0 44 0 a22 22 0 1 0 -44 0 Z', '#F48A3C', sh=(.6, 1.2, .25))
    o += paper('M25 40 a15 15 0 1 0 30 0 a15 15 0 1 0 -30 0 Z', '#F9C25A', sh=(.4, 1, .2))
    return doc(80, 80, o, defs=paper_defs(5))


def clouds_svg():
    """紙の 雲（くり返し）"""
    o = ''
    for x, y, s in ((50, 22, 1.0), (180, 12, .8), (300, 30, 1.1)):
        for xx in _wrap(x, pad=50):
            d = (f"M{f(xx - 26 * s)} {f(y + 8 * s)} Q{f(xx - 30 * s)} {f(y - 2 * s)} {f(xx - 18 * s)} {f(y - 3 * s)} Q{f(xx - 14 * s)} {f(y - 14 * s)} {f(xx - 2 * s)} {f(y - 11 * s)} "
                 f"Q{f(xx + 6 * s)} {f(y - 18 * s)} {f(xx + 16 * s)} {f(y - 8 * s)} Q{f(xx + 30 * s)} {f(y - 8 * s)} {f(xx + 28 * s)} {f(y + 8 * s)} Z")
            o += paper(d, '#FFFFFF', sh=(.8, 1.8, .26))
            o += f"<path d='M{f(xx - 20 * s)} {f(y + 4 * s)} Q{f(xx)} {f(y + 1 * s)} {f(xx + 20 * s)} {f(y + 4 * s)}' fill='none' stroke='#F2E2CC' stroke-width='{f(1.2 * s)}' stroke-linecap='round'/>"
    return doc(TILE, 50, o, defs=paper_defs(3, 1.4))


def far_svg():
    R = rnd(14)
    deco = ''
    for x in (20, 70, 120, 168, 230, 290, 350):
        for xx in _wrap(x + R.uniform(-6, 6)):
            y = 40 + sum(a * math.sin(2 * math.pi * k * xx / TILE + p) for a, k, p in ((5, 2, 1.2), (3, 5, .3)))
            deco += pine(xx, y + 2, R.uniform(.55, .75), '#7FB8A2')
    return hill_svg(40, ((5, 2, 1.2), (3, 5, .3)), '#A9D6C0', 70, deco, seed=6)


def mid_svg():
    R = rnd(15)
    deco = ''
    amps = ((6, 1, 2.0), (4, 3, .6), (2, 7, 1.4))
    for x, kind in ((40, 't'), (96, 'h'), (150, 't'), (210, 't'), (262, 'h'), (320, 't'), (365, 't')):
        for xx in _wrap(x):
            y = 34 + sum(a * math.sin(2 * math.pi * k * xx / TILE + p) for a, k, p in amps) + 3
            deco += house(xx, y, .9, '#FFF4E0', ['#D8473A', '#2F8A84'][int(x) % 2]) if kind == 'h' else tree(xx, y, R.uniform(.8, 1.0), '#5FAE74')
    return hill_svg(34, amps, '#86C796', 64, deco, seed=8)


def near_svg():
    amps = ((4, 2, .3), (3, 4, 2.2), (1.5, 9, .8))
    deco = ''
    for x, c in ((30, '#F7F0E0'), (140, '#F7D35A'), (230, '#F7F0E0'), (330, '#F59BB0')):
        for xx in _wrap(x):
            y = 16 + sum(a * math.sin(2 * math.pi * k * xx / TILE + p) for a, k, p in amps) + 8
            deco += flower(xx, y, 2.2, c)
    # 柵（紙の くい と 横木）
    for x0 in (60, 250):
        for xx in _wrap(x0, pad=60):
            for k in range(5):
                px = xx + k * 11
                y = 16 + sum(a * math.sin(2 * math.pi * kk * px / TILE + p) for a, kk, p in amps)
                deco += paper(P([(px - 1.6, y + 6), (px + 1.6, y + 6), (px + 1.6, y - 8), (px, y - 10), (px - 1.6, y - 8)]), '#F2E2C2', sh=(.4, 1, .25))
            ya = 16 + sum(a * math.sin(2 * math.pi * kk * (xx + 22) / TILE + p) for a, kk, p in amps)
            deco += paper(P([(xx - 3, ya - 5), (xx + 47, ya - 5), (xx + 47, ya - 2.6), (xx - 3, ya - 2.6)]), '#F2E2C2', sh=None)
    return hill_svg(16, amps, '#58A36F', 48, deco, seed=10)


def front_svg():
    """いちばん 手前の 草と 花（帯・くり返し）"""
    R = rnd(19)
    o = ''
    blades = []
    for i in range(70):
        x = i * TILE / 70 + R.uniform(-2, 2)
        h = R.uniform(7, 15)
        blades.append((x, h))
    d = f"M0 22 L0 12"
    for x, h in blades:
        d += f" L{f(x - 2.6)} 12 L{f(x)} {f(12 - h * .7)} L{f(x + 2.6)} 12"
    d += f" L{TILE} 12 L{TILE} 22 Z"
    o += paper(d, '#3F8A5A', sh=(0, -.6, .3))
    for x, c in ((40, '#F59BB0'), (120, '#FFF4E0'), (200, '#F7D35A'), (270, '#F59BB0'), (350, '#FFF4E0')):
        for xx in _wrap(x):
            o += f"<path d='M{xx} 14 Q{xx + 1} 8 {xx} 4' fill='none' stroke='#2F6E46' stroke-width='1.1'/>" + flower(xx, 4, 2.6, c)
    return doc(TILE, 22, o, defs=paper_defs(12, 1.4))


def bird_svg():
    """紙の 鳥（はねは 別の 部品で はばたく）"""
    return doc(20, 12, paper("M2 7 Q6 4 10 6 Q14 4 18 6 Q15 7 12 8.6 Q10 11 8 8.6 Q5 7.6 2 7 Z", '#3E5A8A', sh=(.4, .8, .25), tex=False)
               + "<circle cx='14.6' cy='6.4' r='.7' fill='#FFF4E0'/>", defs=paper_defs(1, .8))


def wing_svg():
    """はね（根もと＝下の 2〜8 が 体の 背中に 重なる：第4.93版 まさちゃん「鳥の羽が身体と離れてるからくっつけて！」）"""
    return doc(16, 10, paper("M1.6 9.4 Q5.6 1 14 2 Q11.4 6 8.6 9.4 Q5 10.4 1.6 9.4 Z", '#5274AE', sh=None, tex=False), defs=paper_defs(1))


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    still = B.get('still')
    alt = ('紙を重ねた切り絵の景色：うすい桃色の空に紙の太陽と雲、遠くの丘の小さな木、家と木のある丘、柵と花の野原、手前の草と花。'
           '赤い紙で作った紙人形の馬（切りぬきのもよう・ティールの鞍の布・金のピンでとめた足）が走っている（足がぱたぱた動き、景色の紙が流れる）')
    html = f'<div class="kgw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('kgSky', sky_svg()) + img('kgSun', sun_svg())
    for cls, svg_, h_ in (('kgCl', clouds_svg(), 50), ('kgFar', far_svg(), 70), ('kgMid', mid_svg(), 64), ('kgNear', near_svg(), 48)):
        html += f'<i class="{cls}" style="background-image:url(&quot;{durl(svg_)}&quot;)"></i>'
    html += ('<i class="kgBd b1">' + img('kgBb', bird_svg()) + img('kgWg', wing_svg()) + '</i>'
             + '<i class="kgBd b2">' + img('kgBb', bird_svg()) + img('kgWg', wing_svg()) + '</i>')
    # 馬：奥の 足 → しっぽ → 体 → 手前の 足 → ピン
    legN, legNH, legF, legFH = leg_svg(RED), leg_svg(RED, True), leg_svg(REDD), leg_svg(REDD, True)
    html += ('<i class="kgH"><i class="kgSh"></i><i class="kgB">' + img('kgL hf', legFH) + img('kgL ff', legF) + img('kgT', tail_svg()) + img('kgBody', body_svg())
             + img('kgL hn', legNH) + img('kgL fn', legN) + ''.join(img(f'kgPin p{k}', pin_svg()) for k in range(3)) + '</i></i>')
    html += f'<i class="kgFr" style="background-image:url(&quot;{durl(front_svg())}&quot;)"></i>'
    html += '</div>'

    s = SC
    css = ('.kgw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#FCE9CF}'
           '.kgw>*{position:absolute;display:block}'
           '.kgw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.kgw .kgSky{left:0;top:0;width:390px;height:160px}'
           '.kgw .kgSun{left:300px;top:4px;width:58px;height:58px;animation:kgSun 80s linear infinite}'
           f'.kgw .kgCl{{left:0;top:2px;width:{2 * TILE}px;height:50px;background-size:{TILE}px 50px;background-repeat:repeat-x;animation:kgFlow 90s linear infinite}}'
           f'.kgw .kgFar{{left:0;top:58px;width:{2 * TILE}px;height:70px;background-size:{TILE}px 70px;background-repeat:repeat-x;animation:kgFlow 48s linear infinite}}'
           f'.kgw .kgMid{{left:0;top:80px;width:{2 * TILE}px;height:64px;background-size:{TILE}px 64px;background-repeat:repeat-x;animation:kgFlow 26s linear infinite}}'
           f'.kgw .kgNear{{left:0;top:114px;width:{2 * TILE}px;height:48px;background-size:{TILE}px 48px;background-repeat:repeat-x;animation:kgFlow 13s linear infinite}}'
           f'.kgw .kgFr{{left:0;top:140px;width:{2 * TILE}px;height:22px;background-size:{TILE}px 22px;background-repeat:repeat-x;animation:kgFlow 7s linear infinite}}'
           '.kgw .kgBd{left:0;top:0;width:20px;height:12px}'
           '.kgw .kgBd>img{position:absolute;display:block}'
           '.kgw .kgBb{left:0;top:0;width:20px;height:12px}'
           '.kgw .kgWg{left:5px;top:0;width:12px;height:8px;transform-origin:31% 86%;animation:kgWing .38s ease-in-out infinite alternate}'
           '.kgw .kgBd.b1{animation:kgB1 22s linear infinite}'
           '.kgw .kgBd.b2{animation:kgB2 22s linear -9s infinite}'
           f'.kgw .kgH{{left:{HX}px;top:{HY}px;width:{f(100 * s)}px;height:{f(80 * s)}px}}'
           f'.kgw .kgSh{{position:absolute;left:{f(14 * s)}px;top:{f(76 * s)}px;width:{f(60 * s)}px;height:{f(6 * s)}px;border-radius:50%;background:rgba(60,40,20,.22);animation:kgShd {LEG_PER / 2}s ease-in-out infinite alternate}}'
           f'.kgw .kgB{{position:absolute;left:0;top:0;width:{f(100 * s)}px;height:{f(80 * s)}px;animation:kgBob {LEG_PER / 2}s ease-in-out infinite alternate}}'
           '.kgw .kgB>img{position:absolute;display:block}'
           f'.kgw .kgBody{{left:0;top:0;width:{f(100 * s)}px;height:{f(80 * s)}px}}'
           f'.kgw .kgT{{left:{f((PIV["tail"][0] - 19) * s)}px;top:{f((PIV["tail"][1] - 4 + 6) * s)}px;width:{f(24 * s)}px;height:{f(34 * s)}px;transform-origin:{f(19 * s)}px {f(4 * s)}px;animation:kgTail {LEG_PER * 2}s ease-in-out infinite alternate}}'
           f'.kgw .kgL{{width:{f(18 * s)}px;height:{f(42 * s)}px;transform-origin:{f(9 * s)}px {f(7 * s)}px}}')
    for k, key in ((0, 'fn'), (1, 'hn'), (2, 'ff'), (3, 'hf')):
        px, py = PIV[key]
        # 体の 絵は viewBox の 上が -6（6 だけ 下に ずれる）
        css += f'.kgw .kgL.{key}{{left:{f((px - 9) * s)}px;top:{f((py - 7 + 6) * s)}px;animation:kgLeg{"A" if key in ("fn", "hf") else "B"} {LEG_PER}s ease-in-out infinite}}'
    for k, key in enumerate(('fn', 'hn', 'tail')):
        px, py = PIV[key]
        css += f'.kgw .kgPin.p{k}{{left:{f(px * s - 3.6)}px;top:{f((py + 6) * s - 3.6)}px;width:7.2px;height:7.2px}}'
    css += (kf('kgFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-TILE}px)')])
            + kf('kgSun', [(0, 'transform:rotate(0)'), (100, 'transform:rotate(360deg)')])
            + kf('kgLegA', [(0, 'transform:rotate(28deg)'), (50, 'transform:rotate(-30deg)'), (100, 'transform:rotate(28deg)')])
            + kf('kgLegB', [(0, 'transform:rotate(-30deg)'), (50, 'transform:rotate(28deg)'), (100, 'transform:rotate(-30deg)')])
            + kf('kgBob', [(0, 'transform:translateY(0) rotate(-1.2deg)'), (100, 'transform:translateY(-4px) rotate(1deg)')])
            + kf('kgShd', [(0, 'transform:scale(1);opacity:1'), (100, 'transform:scale(.86);opacity:.75')])
            + kf('kgTail', [(0, 'transform:rotate(-14deg)'), (100, 'transform:rotate(12deg)')])
            + kf('kgWing', [(0, 'transform:scaleY(1)'), (100, 'transform:scaleY(-.7)')])
            + kf('kgB1', [(0, 'transform:translate(-30px,30px)'), (30, 'transform:translate(110px,18px)'), (60, 'transform:translate(250px,28px)'), (100, 'transform:translate(420px,14px)')])
            + kf('kgB2', [(0, 'transform:translate(-30px,46px) scale(.8)'), (35, 'transform:translate(130px,36px) scale(.8)'), (70, 'transform:translate(280px,44px) scale(.8)'), (100, 'transform:translate(420px,34px) scale(.8)')]))
    css += reduced('.kgw>:not(.bnr)') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_paper():
    """背景の もよう：紙の すじと、小さな 切り紙（花・葉・まる）の 形（うすく）"""
    R = rnd(23)
    o = ''
    for i in range(14):
        x, y = R.uniform(0, 150), R.uniform(0, 150)
        L = R.uniform(8, 20)
        a = R.uniform(0, math.pi)
        o += f"<path d='M{f(x)} {f(y)} l{f(math.cos(a) * L)} {f(math.sin(a) * L)}' stroke='#E3CFB0' stroke-width='.7' opacity='.6'/>"
    for x, y, r, c in ((30, 34, 5, '#E9B7A8'), (112, 98, 4.4, '#B9D6CC')):
        for k in range(5):
            a = math.radians(-90 + k * 72)
            o += f"<ellipse cx='{f(x + math.cos(a) * r)}' cy='{f(y + math.sin(a) * r)}' rx='{f(r * .75)}' ry='{f(r * .5)}' transform='rotate({f(math.degrees(a))} {f(x + math.cos(a) * r)} {f(y + math.sin(a) * r)})' fill='{c}' opacity='.45'/>"
    o += "<path d='M70 130 Q80 118 92 124 Q84 134 70 130 Z' fill='#B9D6CC' opacity='.45'/><path d='M120 30 q6 -8 14 -4 q-6 8 -14 4 Z' fill='#E9B7A8' opacity='.4'/>"
    return tile(150, 150, o)


def edge_strip():
    """上の 帯の 下の ふち：2まい 重ねた 紙の なみなみ（赤の 下に クリーム）"""
    o = ("<path d='M0 0 H20 V4 Q15 12 10 7 Q5 12 0 4 Z' fill='#6E2A20' opacity='.25' transform='translate(0 1.6)'/>"
         "<path d='M0 0 H20 V5 Q15 13 10 8 Q5 13 0 5 Z' fill='#FFF4E0'/>"
         "<path d='M0 0 H20 V2.6 Q15 10 10 5 Q5 10 0 2.6 Z' fill='#C23B30'/>")
    return tile(20, 14, o)


def orn():
    """すみの 飾り（44×44）：重ねた 紙の 花と 葉（ページに じかに 置くので id なし）"""
    o = "<path d='M9 36 Q14 22 28 24 Q22 36 9 36 Z' fill='#2F8A84'/><path d='M12 34 Q18 27 25 26' fill='none' stroke='#BDE3DA' stroke-width='1'/>"
    for dx, dy, col in ((1.4, 2.2, '#6E2A20'), (0, 0, '#D8473A')):
        for k in range(6):
            a = math.radians(-90 + k * 60)
            cx, cy = 26 + math.cos(a) * 7.4 + dx, 18 + math.sin(a) * 7.4 + dy
            o += f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='6' ry='4.2' transform='rotate({f(math.degrees(a))} {f(cx)} {f(cy)})' fill='{col}'{' opacity=\".35\"' if dx else ''}/>"
    o += "<circle cx='26' cy='18' r='5.4' fill='#FFF4E0'/><circle cx='26' cy='18' r='2.6' fill='#E2B24A'/>"
    for k in range(6):
        a = math.radians(-60 + k * 60)
        o += f"<circle cx='{f(26 + math.cos(a) * 7.2)}' cy='{f(18 + math.sin(a) * 7.2)}' r='1.1' fill='#FFF4E0'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='切り絵', desc='紙を重ねた絵', title='切り絵（クリーム×朱×ティール）', banner=ID,
    alt='紙を重ねた切り絵の景色：うすい桃色の空に紙の太陽と雲、遠くの丘の小さな木、家と木のある丘、柵と花の野原、手前の草と花。赤い紙で作った紙人形の馬（切りぬきのもよう・ティールの鞍の布・金のピンでとめた足）',
    fonts=['Zen+Kurenaido', 'Zen+Maru+Gothic:wght@500;700'],
    v=dict(bg='#FBF3E6', ink='#3A2A22', sub='#76604F', card='#FFFDF8', cardB='1px solid #EAD9BE', cardO='0 solid transparent',
           cardS='0 1px 0 #E6D3B4,0 6px 14px rgba(120,80,40,.12)', radius='14px', rs='10px', font='"Zen Maru Gothic"', dfont='"Zen Kurenaido"', dw='400',
           logo='#FFF4E0', logoS='0 2px 0 #8E2A22', iii='#FFF4E0', iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#D8473A,#C23B30)',
           hdInk='#FFF4E0', hdB='0 solid transparent', mBg='rgba(255,255,255,.14)', mLine='rgba(255,244,224,.6)', mInk='#FFF4E0', pill='rgba(255,255,255,.16)',
           pillLine='rgba(255,244,224,.5)', pillInk='#FFF4E0', coin='#E2B24A', coinInk='#3A2A22', badge='#FFF0E4', badgeInk='#B03328', badgeB='1.5px solid #F0C9B4',
           tagBg='#FBEFE2', tagInk='#7A3A2A', tagLine='#EAD0B8', warnBg='#FCE3DE', warnInk='#A8322A', zBg='#FFFBF4', zB='1.5px dashed #EAD9BE', znBg='#B8362C',
           znInk='#FFFFFF', znB='0 solid transparent', znR='6px', znS='none', acc='#B03328', nR='8px', w2B='0 solid transparent', sep='1.5px dashed #E2CBB0',
           btn='#2B7F79', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='12px', btnS='0 3px 0 #1E5C57', btn2='#FFFDF8', btn2Ink='#B03328',
           btn2B='1.5px solid #EBC3B2', tab='#FFFDF8', tabB='1px solid #EAD9BE', tabInk='#76604F', tabOn='#FBE3DB', tabOnInk='#B03328', tabR='12px',
           sel='#2B7F79', selInk='#FFFFFF', h1='#B03328'),
    chk=dict(hd=['#D8473A', '#C23B30']),
    css=[('', 'background-image:' + curi(tile_paper()) + ';background-size:150px 150px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-12px;height:14px;background:' + curi(edge_strip()) + ' 0 0/20px 14px repeat-x')],
    orn=orn(),
    guide=dict(colors=[('#D8473A', '朱の紙'), ('#2B7F79', 'ティール'), ('#E2B24A', '金のピン'), ('#FBF3E6', '紙'), ('#3A2A22', '文字')],
               fonts='見出し：Zen Kurenaido<br>本文：Zen Maru Gothic', shape='角丸14px・帯は 朱の 紙で 下に 2まい 重ねた なみなみ・紙の すじと 切り紙の 背景・点線の 切り取り線・すみに 重ねた 紙の 花・的中ボタンは 重ねた 紙の PUSH',
               pic='紙を 重ねた 景色（空・紙の 太陽と 雲・丘・家と 木・柵と 花）・赤い 紙人形の 馬（切りぬき・金の ピンで とめた 足が ぱたぱた）・紙の 鳥'),
)


# ================================================================== 的中ボタン：重ねた 紙の PUSH（kg）
def push_face(sfx=''):
    """ボタン（200×100）が 3まい 重ねた 紙（下から ティール・クリーム・朱）：ふちは なみなみに 切って ずらして 重ねる。紙の 花と 葉を ピンで とめる"""
    def scallop(x0, y0, w, h, n=10, r=5):
        pts = []
        for i in range(n * 2 + 1):
            pts.append((x0 + w * i / (n * 2), y0 - (r * 0.55 if i % 2 else 0)))
        return pts

    o = ''
    for dx, dy, col, rr in ((8, 9, '#2B7F79', 16), (4, 4.5, '#FFF4E0', 15), (0, 0, '#D8473A', 14)):
        o += f'<rect x="{dx}" y="{dy}" width="200" height="100" rx="{rr}" fill="#5A2E1E" opacity=".22" transform="translate(1.6 3)"/>'
        o += f'<rect x="{dx}" y="{dy}" width="200" height="100" rx="{rr}" fill="{col}"/>'
    # 朱の 紙の 中の 切りぬき（ふちの 小さな まる・すみの しずく）
    for i in range(18):
        x = 12 + i * 10.4
        o += f'<circle cx="{x:.1f}" cy="8" r="1.8" fill="#FFF4E0"/><circle cx="{x:.1f}" cy="92" r="1.8" fill="#FFF4E0"/>'
    for cx, cy, a in ((14, 50, 0), (186, 50, 180)):
        o += (f'<g transform="rotate({a} {cx} {cy})"><path d="M{cx - 5} {cy} Q{cx + 3} {cy - 9} {cx + 6} {cy} Q{cx + 3} {cy + 9} {cx - 5} {cy} Z" fill="#FFF4E0"/>'
              f'<circle cx="{cx - 1}" cy="{cy}" r="1.6" fill="#D8473A"/></g>')
    # 紙の 花（左上）と 葉（右下）・金の ピン
    for k in range(5):
        a = math.radians(-90 + k * 72)
        cx, cy = 18 + math.cos(a) * 9, 4 + math.sin(a) * 9
        o += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="8" ry="5.4" transform="rotate({math.degrees(a):.0f} {cx:.1f} {cy:.1f})" fill="#F7D35A" stroke="#C9A13E" stroke-width="1"/>'
    o += '<circle cx="18" cy="4" r="5" fill="#FFF4E0"/><circle cx="18" cy="4" r="2.6" fill="#E2B24A" stroke="#8A6420" stroke-width=".8"/>'
    o += ('<path d="M168 102 Q182 84 202 90 Q190 106 168 102 Z" fill="#2F8A84"/><path d="M172 100 Q184 92 196 92" fill="none" stroke="#BDE3DA" stroke-width="1.4"/>'
          '<path d="M184 108 Q196 98 212 104 Q200 114 184 108 Z" fill="#58A36F"/>')
    return f'<i class="kgf" aria-hidden="true"><svg viewBox="-10 -12 228 128" width="228" height="128">{o}</svg></i>'


def push_decor(sfx=''):
    """まわりに うかぶ 紙の 花・葉・まる（ゆっくり ゆれる）"""
    o = ''
    items = ((-26, -18, '#F59BB0', 'f'), (226, -8, '#F7D35A', 'f'), (-22, 96, '#2F8A84', 'l'), (232, 92, '#D8473A', 'c'), (110, -50, '#FFF4E0', 'f'), (40, -46, '#58A36F', 'l'))
    for j, (x, y, c, kind) in enumerate(items):
        if kind == 'f':
            g = ''.join(f'<ellipse cx="{x + math.cos(math.radians(-90 + k * 72)) * 5:.1f}" cy="{y + math.sin(math.radians(-90 + k * 72)) * 5:.1f}" rx="4.4" ry="3" '
                        f'transform="rotate({-90 + k * 72} {x + math.cos(math.radians(-90 + k * 72)) * 5:.1f} {y + math.sin(math.radians(-90 + k * 72)) * 5:.1f})" fill="{c}"/>' for k in range(5))
            g += f'<circle cx="{x}" cy="{y}" r="2.6" fill="#E2B24A"/>'
        elif kind == 'l':
            g = f'<path d="M{x - 9} {y + 4} Q{x - 2} {y - 9} {x + 10} {y - 4} Q{x + 2} {y + 9} {x - 9} {y + 4} Z" fill="{c}"/>'
        else:
            g = f'<circle cx="{x}" cy="{y}" r="6" fill="{c}"/><circle cx="{x}" cy="{y}" r="2.4" fill="#FFF4E0"/>'
        o += f'<g class="kgbo" style="animation-delay:{-0.6 * j:.1f}s">{g}</g>'
    return f'<i class="kgd" aria-hidden="true"><svg viewBox="-40 -70 280 210" width="280" height="210">{o}</svg></i>'


def _flower(c, core='#E2B24A'):
    o = ''
    for k in range(5):
        a = math.radians(-90 + k * 72)
        cx, cy = 12 + math.cos(a) * 5.4, 12 + math.sin(a) * 5.4
        o += f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='5' ry='3.4' transform='rotate({f(math.degrees(a))} {f(cx)} {f(cy)})' fill='{c}'/>"
    return doc(24, 24, o + f"<circle cx='12' cy='12' r='3' fill='{core}'/>")


PIECES = dict(fr=piece(_flower('#D8473A', '#FFF4E0')), fy=piece(_flower('#F7D35A')), fp=piece(_flower('#F59BB0')),
              lf=piece(doc(24, 16, "<path d='M2 10 Q9 0 22 5 Q14 16 2 10 Z' fill='#2F8A84'/><path d='M5 9 Q12 5 19 6' fill='none' stroke='#BDE3DA' stroke-width='1.2'/>")),
              ci=piece(doc(20, 20, "<circle cx='10' cy='10' r='9' fill='#FFF4E0'/><circle cx='10' cy='10' r='4' fill='#D8473A'/>")),
              st=piece(doc(22, 22, f"<path d='{star_d(11, 11.6, 10, 4.4)}' fill='#E2B24A'/>")))


def push_burst():
    return fly_burst('kg', ['fr', 'lf', 'fy', 'ci', 'fp', 'st', 'lf', 'fr'], 30, 61,
                     sizes=dict(fr=(16, 22), fy=(15, 20), fp=(15, 20), lf=(15, 21), ci=(10, 14), st=(13, 17)))


PUSH_CSS = r'''
/* ---------- 切り絵の的中ボタン：重ねた紙のPUSH（壁紙パック） ----------
   ボタンが 3まい 重ねた 紙（下から ティール・クリーム・朱）：少しずつ ずらして 重ね、紙と 紙の あいだに やわらかい かげ。
   朱の 紙の ふちに 小さな まるい 切りぬき・左右に しずくの 切りぬき・すみに ピンで とめた 紙の 花と 葉。「PUSH」は クリームの 紙の 字。
   まわりに 紙の 花・葉・まるが ゆっくり ゆれる。上下の 動きは 的中と 同じ。押すと 紙が ちぢんで ふくらみ（強く 光らせない）、
   紙の 花・葉・まる・星が はじけて 落ち、朱の 輪が 広がる */
.kg{--pushA:#D8473A;--pushB:#6E2A20;--pushC:#2B7F79;--rim:#F7D35A;--rimD:#6E2A20}
.push.kg{--pr:14px;background:none;border-radius:14px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(90,46,30,.35)) drop-shadow(0 16px 20px rgba(0,0,0,.3))}
.push.kg span{font:400 42px/1 "Zen Kurenaido",sans-serif;letter-spacing:.08em;color:#FFF4E0;text-shadow:1.5px 2px 0 #8E2A22,0 0 8px rgba(255,244,224,.35)}
.push.kg::after{inset:-20px;border-radius:30px;border-color:rgba(247,211,90,.9)}
.kg .kgf{position:absolute;left:-10px;top:-12px;width:228px;height:128px;pointer-events:none;font-style:normal;z-index:-1}
.kg .kgf svg{display:block;width:228px;height:128px;overflow:visible}
.kg .kgd{position:absolute;left:-40px;top:-70px;width:280px;height:210px;pointer-events:none;z-index:3;font-style:normal}
.kg .kgd svg{display:block;width:280px;height:210px;overflow:visible}
.kg .kgbo{transform-box:fill-box;transform-origin:50% 50%;animation:kgBo 2.8s ease-in-out infinite alternate}
@keyframes kgBo{from{transform:translateY(-4px) rotate(-12deg)}to{transform:translateY(4px) rotate(12deg)}}
.pshadow.kg{width:220px}
.tap.kg{font-family:"Zen Kurenaido",sans-serif;font-weight:400;color:#FFF4E0;letter-spacing:.14em;text-shadow:0 2px 0 #8E2A22,0 0 10px rgba(255,244,224,.5)}
.pressed.kg{border-radius:14px;background:#D8473A;box-shadow:4px 4.5px 0 #FFF4E0,8px 9px 0 #2B7F79;animation-name:kgPress,fxH}
@keyframes kgPress{0%{transform:scale(1)}22%{transform:scale(.9) rotate(-2deg)}45%{transform:scale(1.07) rotate(1deg)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.kg .kgbo{animation:none}.clips.kg{display:none}}
''' + fly_css('kg', 'rgba(216,71,58,.85)', PIECES)

PUSH = dict(code='kg', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
