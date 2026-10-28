"""壁紙パック ⑤深海（まさちゃんの 指定「タツノオトシゴ（海の馬🐴）たちのレース。泡がぷくぷく」）
   上の絵：青い 深い 海。上から 光の すじ・遠くの 岩の かげ・ゆれる 海そう・さんご・砂の 海の 底。
     騎手の 帽子と ゼッケン（星）を つけた タツノオトシゴ 4ひき（オレンジ・黄・ピンク・ミント）が 右へ レース。
   動き：景色が 右から 左へ 流れる（遠いほど ゆっくり・タツノオトシゴが 前へ 進んで 見える）・4ひきが 前へ 出たり 下がったり して 順位が 入れかわる・
     上下に ゆれて 背びれが ぱたぱた・口から 泡が ぷくぷく・海の 底から 泡の 列・光の すじが ゆっくり ゆらぐ・遠くを 小さな 魚の むれと くらげ・
     32秒に 1回 ゴールの 門（さんごの 柱と チェックの 旗）が 海の 底と 同じ 速さで 通りすぎる。強く 光らせない"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'deepsea'
WATER = ('#2386B8', '#0F4C7A', '#072646')
TILE = 390          # 流れる 帯の 1まいの はば

# タツノオトシゴ：背骨の 点（右向き：口の 先 → 頭 → 首 → おなか → しっぽの うず）と (背中がわ, おなかがわ) の はば（絵の 単位。1ぴき 60×104）
SPINE = [((52, 22), (1.6, 1.6)), ((44, 21), (1.9, 1.9)), ((37, 19), (2.7, 2.9)), ((28, 15), (8.4, 7.2)), ((20, 20.5), (8.2, 6.2)),
         ((16, 31), (5.6, 6.4)), ((17, 43), (6.6, 11)), ((20, 56), (7, 13.4)), ((20, 68), (6, 10)), ((17, 78), (4.3, 5.6)),
         ((15, 88), (3.4, 3.9)), ((19, 96), (2.8, 3.1)), ((27, 99.5), (2.3, 2.5)), ((34, 94.5), (1.9, 2.0)), ((34.5, 87.5), (1.6, 1.6)),
         ((29.5, 84), (1.25, 1.25)), ((25.5, 87.5), (0.95, 0.95)), ((27.5, 91.5), (0.6, 0.6))]
# 色：(体, かげ, 明るい おなか, ふし, ひれ)・帽子と ゼッケン：(地, 星と すじ)
RIDERS = [dict(col=('#F59A3C', '#D9772A', '#FFC98A', '#B95A1A', '#FFE3B0'), cap=('#E8384A', '#FFFFFF')),
          dict(col=('#F7CC45', '#DDA92A', '#FFE79A', '#B8860F', '#FFF4C8'), cap=('#2F6FD6', '#FFFFFF')),
          dict(col=('#F27D96', '#D65E78', '#FFB8C6', '#B04460', '#FFE0E8'), cap=('#2EAA6A', '#FFFFFF')),
          dict(col=('#46C9B5', '#2FA796', '#9BEADF', '#1D7F70', '#D8FFF8'), cap=('#F7B731', '#1E2A5A'))]
# 4ひきの 置き場（まん中の x・y・大きさ・遠さ）と 前後する 動き（ずれ px・1回り 秒・ずらし 秒）
LANES = [dict(x=170, y=89, s=0.84, far=0.0, dx=96, per=13.0, ph=0.0),
         dict(x=222, y=76, s=0.74, far=0.1, dx=100, per=16.0, ph=-6.5),
         dict(x=148, y=62, s=0.66, far=0.18, dx=88, per=11.0, ph=-3.2),
         dict(x=252, y=50, s=0.58, far=0.26, dx=84, per=19.0, ph=-11.0)]


def _cr(p0, p1, p2, p3, u):
    u2, u3 = u * u, u * u * u
    return tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3) for a, b, c, d in zip(p0, p1, p2, p3))


def _outline(n_per=8):
    """背骨を なめらかに つないで、背中がわ・おなかがわの ふちの 点"""
    S = SPINE
    pts, ws = [], []
    for i in range(len(S) - 1):
        p0, p1, p2, p3 = S[max(0, i - 1)][0], S[i][0], S[i + 1][0], S[min(len(S) - 1, i + 2)][0]
        w1, w2 = S[i][1], S[i + 1][1]
        for k in range(n_per):
            u = k / n_per
            pts.append(_cr(p0, p1, p2, p3, u))
            e = u * u * (3 - 2 * u)
            ws.append((w1[0] + (w2[0] - w1[0]) * e, w1[1] + (w2[1] - w1[1]) * e))
    pts.append(S[-1][0])
    ws.append(S[-1][1])
    back, front = [], []
    for i, (p, (wb, wf)) in enumerate(zip(pts, ws)):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        back.append((p[0] + nx * wb, p[1] + ny * wb))
        front.append((p[0] - nx * wf, p[1] - ny * wf))
    return pts, back, front


def seahorse_svg(rider, far=0.0, fin=False):
    """1ぴき（60×104 の 絵）。far：遠さ（水の 色に よせる）。fin：背びれだけの 絵（ぱたぱた 動かす 部品）"""
    tint = lambda c: mix(c, '#1E6A94', far)
    body, shade, light, ridge, finc = (tint(c) for c in rider['col'])
    c1, c2 = (tint(c) for c in rider['cap'])
    vb = '-2 -2 60 104'
    if fin:
        o = f"<path d='M14.6 49.5 Q2.6 49 1.2 57.6 Q2.6 66.6 15 66.4 Z' fill='{finc}' opacity='.88'/>"
        for k in range(6):
            y = 51 + k * 2.9
            o += f"<path d='M14.6 {f(y + 0.5)} L{f(2.4 + abs(k - 2.5) * 0.6)} {f(y)}' stroke='{mix(finc, ridge, .45)}' stroke-width='.7' opacity='.85'/>"
        return doc(60, 104, o, vb=vb)
    pts, back, front = _outline()
    d = P(back + front[::-1])
    defs = (f"<linearGradient id='g' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='{shade}'/><stop offset='.55' stop-color='{body}'/><stop offset='1' stop-color='{light}'/></linearGradient>"
            f"<clipPath id='c'><path d='{d}'/></clipPath>")
    o = f"<path d='{d}' fill='url(#g)'/><g clip-path='url(#c)'>"
    o += f"<path d='{P([(x - 3.5, y) for x, y in front[40:96]], False)}' fill='none' stroke='{light}' stroke-width='5' opacity='.5'/>"
    for i in range(36, len(pts) - 2, 6):                       # ふし（輪の すじ）
        bx, by = back[i]
        fx, fy = front[i]
        o += f"<path d='M{f(bx)} {f(by)} Q{f((bx + fx) / 2)} {f((by + fy) / 2 + 1.2)} {f(fx)} {f(fy)}' fill='none' stroke='{ridge}' stroke-width='.8' opacity='.5'/>"
    o += (f"<path d='M2 37 L36 33 L37 46 L3 51 Z' fill='{c1}'/>"                                   # ゼッケン（体に まく 布・白い ふち・星）
          f"<path d='M2 37 L36 33 L36.2 35 L2.2 39 Z M3 49 L37 44 L37 46 L3 51 Z' fill='{tint('#FFFFFF')}'/>"
          f"<path d='{star_d(24.5, 41.6, 3.7, 1.6)}' fill='{c2}'/>")
    for x, y, r in ((30, 52, 1.1), (27, 61, .8), (22, 74, .7), (31, 57.5, .6)):
        o += f"<circle cx='{x}' cy='{y}' r='{r}' fill='#FFFFFF' opacity='.65'/>"
    o += '</g>'
    o += (f"<path d='M24.6 17 Q21 22 23 27' fill='none' stroke='{ridge}' stroke-width='1' stroke-linecap='round' opacity='.7'/>"      # ほお
          f"<ellipse cx='52.4' cy='22' rx='1.3' ry='2.2' fill='{ridge}' opacity='.8'/>"                                            # 口
          f"<path d='M21 27 Q14 25 13.5 30 Q16 32 21.5 30 Z' fill='{finc}' opacity='.8'/>"                                          # 胸びれ
          f"<circle cx='29.5' cy='15.5' r='4.2' fill='{tint('#FFFFFF')}'/><circle cx='30.4' cy='15.9' r='3' fill='#1E2A3A'/>"
          f"<circle cx='31.4' cy='14.6' r='1.1' fill='#FFFFFF'/><circle cx='29.4' cy='17.2' r='.5' fill='#FFFFFF' opacity='.8'/>")
    o += (f"<path d='M14 13 Q14 1.5 24.5 1 Q33.5 1 34.5 10.5 Q25 13.6 14 13 Z' fill='{c1}'/>"          # 騎手の 帽子（つば・すじ・ぼたん）
          f"<path d='M23.2 1.2 Q26 1 27.2 1.4 L28.6 11.6 Q26.4 12.2 24.4 12.4 Z' fill='{c2}'/>"
          f"<path d='M31.5 9.6 Q38 9 41 12.4 Q36.4 13.2 31 12.4 Z' fill='{mix(c1, '#000000', .25)}'/>"
          f"<circle cx='24.6' cy='1.6' r='1.6' fill='{c2}'/>"
          f"<path d='M17 5.5 Q19.5 2.6 23 2.2' fill='none' stroke='#FFFFFF' stroke-width='1.3' stroke-linecap='round' opacity='.5'/>")
    return doc(60, 104, o, vb=vb, defs=defs)


# ---------------------------------------------------------------- 景色
def water_svg():
    """海の 色（上が 明るい）と 光の すじの もと・遠くの 岩の かげ（止まった 絵）"""
    defs = (f"<linearGradient id='w' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{WATER[0]}'/><stop offset='.45' stop-color='{WATER[1]}'/>"
            f"<stop offset='1' stop-color='{WATER[2]}'/></linearGradient>"
            "<radialGradient id='s' cx='.5' cy='0' r='.9'><stop offset='0' stop-color='#BFF1FF' stop-opacity='.45'/><stop offset='1' stop-color='#BFF1FF' stop-opacity='0'/></radialGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#w)'/><ellipse cx='150' cy='-10' rx='260' ry='70' fill='url(#s)'/>"
    # 水面の ゆらぎ（上の ふち）
    o += "<path d='M0 4 Q20 0 40 4 T80 4 T120 4 T160 4 T200 4 T240 4 T280 4 T320 4 T360 4 T400 4 V0 H0 Z' fill='#9FE6F6' opacity='.25'/>"
    return doc(W, H, o, defs=defs)


def rays_svg():
    """上から さしこむ 光の すじ（うすい 白の 台形）"""
    defs = "<linearGradient id='r' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E6FBFF' stop-opacity='.55'/><stop offset='1' stop-color='#E6FBFF' stop-opacity='0'/></linearGradient>"
    o = ''
    for x0, w0, x1, w1, op in ((40, 22, 10, 56, .5), (120, 16, 104, 46, .38), (196, 26, 196, 70, .45), (282, 14, 300, 44, .34), (348, 20, 376, 52, .3)):
        o += f"<path d='M{x0} 0 H{x0 + w0} L{x1 + w1} 150 H{x1} Z' fill='url(#r)' opacity='{op}'/>"
    return doc(W, H, o, defs=defs)


def _wrap(x, w=TILE, pad=60):
    return [x + dx for dx in (-w, 0, w) if -pad <= x + dx <= w + pad]


def far_svg():
    """遠くの 岩と さんごの かげ（くり返し・ゆっくり 流れる）"""
    R = rnd(12)
    c = '#14507A'
    o = ''
    for x, w, h in ((40, 90, 34), (170, 70, 22), (260, 110, 40), (360, 60, 26)):
        for xx in _wrap(x):
            o += f"<path d='M{f(xx - w / 2)} 70 C{f(xx - w * 0.4)} {f(70 - h * 0.7)} {f(xx - w * 0.15)} {f(70 - h)} {f(xx)} {f(70 - h)} C{f(xx + w * 0.2)} {f(70 - h)} {f(xx + w * 0.42)} {f(70 - h * 0.6)} {f(xx + w / 2)} 70 Z' fill='{c}' opacity='.85'/>"
    for x in (110, 220, 330):                                    # さんごの 木の かげ
        for xx in _wrap(x):
            o += f"<path d='M{xx} 70 V{f(40 + R.uniform(-4, 4))}' stroke='{c}' stroke-width='3' stroke-linecap='round'/>"
            for k in range(4):
                a = math.radians(-150 + k * 40)
                L = R.uniform(9, 15)
                y0 = 58 - k * 4
                o += f"<path d='M{xx} {y0} q{f(math.cos(a) * L * 0.5)} {f(math.sin(a) * L * 0.8)} {f(math.cos(a) * L)} {f(math.sin(a) * L)}' fill='none' stroke='{c}' stroke-width='2.2' stroke-linecap='round'/>"
    return doc(TILE, 70, o)


def kelp_svg():
    """海そうと さんご（まん中の 帯・くり返し）。ゆれは 帯ごと（skew）"""
    R = rnd(5)
    o = ''
    for x, h, c in ((22, 64, '#1F8A70'), (34, 48, '#2BA083'), (140, 70, '#1F8A70'), (152, 52, '#2BA083'), (262, 60, '#1F8A70'), (330, 74, '#24957A'), (342, 50, '#2EAA8C')):
        for xx in _wrap(x):
            pts_l, pts_r = [], []
            for k in range(9):
                t = k / 8
                y = 74 - h * t
                sw = math.sin(t * 5.2 + x) * 4.5 * t
                wdt = 3.6 * (1 - t * 0.55)
                pts_l.append((xx + sw - wdt, y))
                pts_r.append((xx + sw + wdt, y))
            o += f"<path d='{smooth(pts_l + pts_r[::-1])}' fill='{c}'/>"
            o += f"<path d='{smooth([(xx + math.sin(k / 8 * 5.2 + x) * 4.5 * k / 8, 74 - h * k / 8) for k in range(9)], False)}' fill='none' stroke='#5FD3B2' stroke-width='.8' opacity='.5'/>"
    for x, col, n in ((80, '#E8698A', 5), (205, '#F0904F', 4), (296, '#B07AE0', 5)):     # さんご（えだ）
        for xx in _wrap(x):
            for k in range(n):
                a = math.radians(-150 + k * (120 / (n - 1)))
                L = R.uniform(12, 18)
                ex, ey = xx + math.cos(a) * L, 74 + math.sin(a) * L
                o += f"<path d='M{xx} 74 Q{f(xx + math.cos(a) * L * 0.3)} {f(74 + math.sin(a) * L * 0.75)} {f(ex)} {f(ey)}' fill='none' stroke='{col}' stroke-width='3.4' stroke-linecap='round'/>"
                o += f"<circle cx='{f(ex)}' cy='{f(ey)}' r='2.4' fill='{mix(col, '#FFFFFF', .25)}'/>"
    return doc(TILE, 76, o)


def floor_svg():
    """海の 底（砂・石・貝・ひとで・いそぎんちゃく：手前の 帯・くり返し）"""
    R = rnd(9)
    defs = "<linearGradient id='f' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#5F8E9C'/><stop offset='1' stop-color='#2E5568'/></linearGradient>"
    top = [(x, 10 + 3 * math.sin(x / TILE * 2 * math.pi * 2) + 2 * math.sin(x / TILE * 2 * math.pi * 5 + 1)) for x in range(0, TILE + 1, 10)]
    o = f"<path d='M0 40 V{f(top[0][1])} " + ' '.join(f'L{f(x)} {f(y)}' for x, y in top) + f" V40 Z' fill='url(#f)'/>"
    o += f"<path d='{P(top, False)}' fill='none' stroke='#8FC0C8' stroke-width='1.2' opacity='.55'/>"
    for i in range(26):                                          # 砂の 点
        x, y = R.uniform(0, TILE), R.uniform(16, 38)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.5, 1.1))}' fill='#9CC6CC' opacity='.45'/>"
    for x, y, r in ((60, 18, 7), (66, 20, 5), (230, 20, 8), (238, 22, 5.5), (350, 17, 6)):   # 石
        for xx in _wrap(x):
            o += f"<ellipse cx='{f(xx)}' cy='{y}' rx='{r}' ry='{f(r * 0.62)}' fill='#3E6170'/><ellipse cx='{f(xx - r * 0.25)}' cy='{f(y - r * 0.2)}' rx='{f(r * 0.5)}' ry='{f(r * 0.25)}' fill='#6E97A4' opacity='.6'/>"
    for x in (120, 300):                                         # ひとで
        for xx in _wrap(x):
            o += f"<path d='{star_d(xx, 24, 6.5, 2.8)}' fill='#F08A4B' transform='rotate(14 {xx} 24)'/><circle cx='{xx}' cy='24' r='1.1' fill='#FFC08A'/>"
    for x in (176, 26):                                          # 貝（ほたて）
        for xx in _wrap(x):
            o += (f"<path d='M{xx - 7} 24 Q{xx} 12 {xx + 7} 24 Z' fill='#F4D6C0'/><path d='M{xx - 2.6} 24 L{xx - 1} 16 M{xx + 2.6} 24 L{xx + 1} 16 M{xx} 24 V15' stroke='#C79C82' stroke-width='.8'/>"
                  f"<rect x='{xx - 2.6}' y='23.6' width='5.2' height='2.4' rx='.8' fill='#E6BFA6'/>")
    for x, col in ((90, '#C85FA8'), (268, '#E86A6A')):           # いそぎんちゃく
        for xx in _wrap(x):
            o += f"<ellipse cx='{xx}' cy='20' rx='7' ry='4' fill='{mix(col, '#000000', .2)}'/>"
            for k in range(9):
                a = math.radians(-170 + k * 20)
                o += f"<path d='M{xx} 18 q{f(math.cos(a) * 5)} {f(math.sin(a) * 9 - 2)} {f(math.cos(a) * 9)} {f(math.sin(a) * 11)}' fill='none' stroke='{col}' stroke-width='2' stroke-linecap='round'/>"
    return doc(TILE, 40, o, defs=defs)


def snow_svg():
    """ただよう 小さな つぶ（マリンスノー）"""
    R = rnd(3)
    o = ''.join(f"<circle cx='{f(R.uniform(0, 200))}' cy='{f(R.uniform(0, 160))}' r='{f(R.uniform(.5, 1.1))}' fill='#D8F6FF' opacity='{f(R.uniform(.25, .6))}'/>" for _ in range(26))
    return doc(200, 160, o)


def bubble_svg():
    return doc(12, 12, "<circle cx='6' cy='6' r='5' fill='#BFF3FF' fill-opacity='.18' stroke='#E8FCFF' stroke-width='1.1' stroke-opacity='.85'/>"
                       "<path d='M3.4 5 Q4 3.2 5.8 2.8' fill='none' stroke='#FFFFFF' stroke-width='1.2' stroke-linecap='round'/>")


def fish_svg():
    """小さな 魚の むれ（7ひき・左向き）"""
    o = ''
    for x, y, s in ((6, 10, 1), (20, 4, .85), (22, 16, .9), (36, 9, 1), (48, 3, .8), (50, 15, .85), (64, 9, .9)):
        o += (f"<g transform='translate({x} {y}) scale({s})'><path d='M0 0 Q6 -4 12 0 Q6 4 0 0 Z' fill='#8FD6F2' opacity='.75'/>"
              f"<path d='M11 0 L16 -3.4 L15 0 L16 3.4 Z' fill='#8FD6F2' opacity='.75'/><circle cx='2.6' cy='-.6' r='.7' fill='#0F3456'/></g>")
    return doc(84, 22, o)


def jelly_svg():
    """くらげ（うすい ピンク・すき通し）"""
    o = ("<path d='M4 18 Q4 2 18 2 Q32 2 32 18 Q28 16 25 18 Q22 16 18 18 Q14 16 11 18 Q8 16 4 18 Z' fill='#F7B8E0' fill-opacity='.55' stroke='#FFE0F4' stroke-width='.8'/>"
         "<path d='M9 9 Q12 5 17 4.4' fill='none' stroke='#FFFFFF' stroke-width='1.4' stroke-linecap='round' opacity='.7'/>")
    for x, c in ((8, .5), (13, .8), (18, .6), (23, .9), (28, .5)):
        o += f"<path d='M{x} 18 q-3 7 0 13 q3 6 0 13' fill='none' stroke='#F7C8E8' stroke-width='1.2' opacity='{c}' stroke-linecap='round'/>"
    return doc(36, 48, o)


def gate_svg():
    """ゴールの 門：さんごの 柱 2本・海そうの 綱・チェックの 旗（字なし）"""
    o = ''
    for x in (6, 70):
        o += (f"<path d='M{x - 5} 96 Q{x - 6} 50 {x - 2} 18 Q{x} 12 {x + 2} 18 Q{x + 6} 50 {x + 5} 96 Z' fill='#E8698A'/>"
              f"<path d='M{x - 2.6} 92 Q{x - 3.4} 52 {x - 0.6} 20' fill='none' stroke='#FFB3C6' stroke-width='1.6' opacity='.7'/>")
        for y in (34, 52, 70):
            o += f"<circle cx='{x + 4}' cy='{y}' r='2' fill='#FFB3C6'/><circle cx='{x - 4}' cy='{y + 8}' r='1.8' fill='#FFB3C6'/>"
    o += "<path d='M8 24 Q38 36 68 24' fill='none' stroke='#2BA083' stroke-width='2.6'/>"
    cw = 6
    for i in range(9):
        for j in range(3):
            x0, y0 = 11 + i * cw, 26 + j * cw + 3.4 * math.sin(math.pi * (i + .5) / 9)
            o += f"<rect x='{f(x0)}' y='{f(y0)}' width='{cw}' height='{cw}' fill='{'#1E2A3A' if (i + j) % 2 else '#FFFFFF'}'/>"
    return doc(76, 98, o)


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    still = B.get('still')
    alt = ('青い深い海で、騎手の帽子と星のゼッケンをつけたオレンジ・黄・ピンク・ミントのタツノオトシゴ4ひきがレースしている。'
           '上から光のすじ、海の底に海そう・さんご・ひとで・貝のイラスト（景色が流れて、順位が入れかわり、泡がぷくぷく上る）')
    html = f'<div class="dsw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('dsWa', water_svg())
    html += f'<i class="dsFar" style="background-image:url(&quot;{durl(far_svg())}&quot;)"></i>'
    html += img('dsJe', jelly_svg()) + img('dsFi', fish_svg())
    html += f'<i class="dsSn" style="background-image:url(&quot;{durl(snow_svg())}&quot;)"></i>'
    html += img('dsRy', rays_svg())
    html += '<i class="dsKp"><i style="background-image:url(&quot;' + durl(kelp_svg()) + '&quot;)"></i></i>'
    html += img('dsGt', gate_svg())
    bub = bubble_svg()
    for k, ln in enumerate(LANES[::-1]):                         # 遠い じゅんに（手前が 上に 重なる）
        i = len(LANES) - 1 - k
        r = RIDERS[i]
        html += (f'<i class="dsH h{i}"><i class="dsB">' + img('dsFn', seahorse_svg(r, ln['far'], fin=True)) + img('dsBd', seahorse_svg(r, ln['far']))
                 + '</i>' + ''.join(img(f'dsBb b{j}', bub) for j in range(3)) + '</i>')
    html += f'<i class="dsFl" style="background-image:url(&quot;{durl(floor_svg())}&quot;)"></i>'
    for j in range(12):
        html += img(f'dsUp u{j}', bub)
    html += '</div>'

    css = ('.dsw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#0F4C7A}'
           '.dsw>*{position:absolute;display:block}'
           '.dsw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.dsw .dsWa{left:0;top:0;width:390px;height:160px}'
           f'.dsw .dsFar{{left:0;top:78px;width:{2 * TILE}px;height:70px;background-size:{TILE}px 70px;background-repeat:repeat-x;animation:dsFlow 60s linear infinite}}'
           '.dsw .dsJe{left:300px;top:8px;width:30px;height:40px;opacity:.85;animation:dsJe 9s ease-in-out infinite}'
           '.dsw .dsFi{left:0;top:22px;width:84px;height:22px;animation:dsFi 26s linear infinite}'
           f'.dsw .dsSn{{left:0;top:0;width:{2 * 200}px;height:160px;background-size:200px 160px;background-repeat:repeat-x;animation:dsSn 30s linear infinite}}'
           '.dsw .dsRy{left:0;top:0;width:390px;height:160px;transform-origin:50% 0;animation:dsRy 11s ease-in-out infinite}'
           f'.dsw .dsKp{{left:0;top:72px;width:{2 * TILE}px;height:76px;animation:dsFlow 24s linear infinite}}'
           f'.dsw .dsKp>i{{position:absolute;left:0;top:0;width:{2 * TILE}px;height:76px;background-size:{TILE}px 76px;background-repeat:repeat-x;transform-origin:50% 100%;animation:dsSway 5s ease-in-out infinite}}'
           '.dsw .dsGt{left:0;top:36px;width:95px;height:122px;transform:translateX(420px);animation:dsGate 32s linear infinite}'
           f'.dsw .dsFl{{left:0;top:122px;width:{2 * TILE}px;height:40px;background-size:{TILE}px 40px;background-repeat:repeat-x;animation:dsFlow 11s linear infinite}}'
           '.dsw .dsH{left:0;top:0;width:0;height:0}'
           '.dsw .dsB{position:absolute;left:0;top:0}'
           '.dsw .dsB>img{position:absolute;left:0;top:0;display:block}'
           '.dsw .dsFn{animation:dsFin .32s ease-in-out infinite alternate}'
           '.dsw .dsBb{position:absolute;width:7px;height:7px;opacity:0;animation:dsBub 3.6s ease-out infinite}'
           '.dsw .dsUp{width:9px;height:9px;opacity:0;animation:dsUp 6s linear infinite}')
    for i, ln in enumerate(LANES):
        s = ln['s']
        w, h = 60 * s, 104 * s
        css += (f'.dsw .dsH.h{i}{{transform:translate({f(ln["x"] - w / 2)}px,{f(ln["y"] - h / 2)}px)}}'
                f'.dsw .dsH.h{i}>.dsB{{width:{f(w)}px;height:{f(h)}px;animation:dsBob{i} {f(1.7 + i * 0.23, 2)}s ease-in-out {f(-i * 0.5, 2)}s infinite;'
                f'transform-origin:{f(w * 0.45)}px {f(h * 0.4)}px}}'
                f'.dsw .dsH.h{i} .dsB>img{{width:{f(w)}px;height:{f(h)}px}}'
                f'.dsw .dsH.h{i} .dsFn{{transform-origin:{f(15 / 60 * w)}px {f(58 / 104 * h)}px}}')
        # 口から 泡（口の 先：絵の (53, 22)）
        mx, my = 53 / 60 * w, 21 / 104 * h
        for j in range(3):
            css += f'.dsw .dsH.h{i} .dsBb.b{j}{{left:{f(mx - 3.5)}px;top:{f(my - 3.5)}px;animation-delay:{f(-(i * 1.1 + j * 0.42), 2)}s;width:{f(5 + j * 1.6)}px;height:{f(5 + j * 1.6)}px}}'
        # 前後（順位が 入れかわる）・上下の ゆれ
        css += f'.dsw .dsH.h{i}{{animation:dsRace{i} {ln["per"]}s ease-in-out {ln["ph"]}s infinite}}'
        x0, y0 = ln['x'] - w / 2, ln['y'] - h / 2
        css += kf(f'dsRace{i}', [(0, f'transform:translate({f(x0)}px,{f(y0)}px)'), (25, f'transform:translate({f(x0 + ln["dx"])}px,{f(y0 - 2)}px)'),
                                 (50, f'transform:translate({f(x0 + ln["dx"] * 0.2)}px,{f(y0 + 2)}px)'), (75, f'transform:translate({f(x0 - ln["dx"])}px,{f(y0)}px)'),
                                 (100, f'transform:translate({f(x0)}px,{f(y0)}px)')])
        a = 3.2 + i * 0.4
        css += kf(f'dsBob{i}', [(0, f'transform:translateY({f(-a)}px) rotate(-4deg)'), (50, f'transform:translateY({f(a)}px) rotate(3deg)'), (100, f'transform:translateY({f(-a)}px) rotate(-4deg)')])
    # 海の 底から 上る 泡（12こ：場所・大きさ・ずらし）
    R = rnd(17)
    for j in range(12):
        x = 12 + j * 32 + R.uniform(-8, 8)
        sz = R.uniform(5, 11)
        css += f'.dsw .dsUp.u{j}{{left:{f(x)}px;top:150px;width:{f(sz)}px;height:{f(sz)}px;animation-duration:{f(R.uniform(5, 7.5), 2)}s;animation-delay:{f(-R.uniform(0, 7), 2)}s}}'
    css += (kf('dsFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-TILE}px)')])
            + kf('dsSn', [(0, 'transform:translate(0,0)'), (100, 'transform:translate(-200px,-10px)')])
            + kf('dsSway', [(0, 'transform:skewX(-3deg)'), (50, 'transform:skewX(3deg)'), (100, 'transform:skewX(-3deg)')])
            + kf('dsRy', [(0, 'opacity:.75;transform:translateX(-6px) skewX(-2deg)'), (50, 'opacity:1;transform:translateX(6px) skewX(2deg)'), (100, 'opacity:.75;transform:translateX(-6px) skewX(-2deg)')])
            + kf('dsJe', [(0, 'transform:translate(0,4px) scale(1,1)'), (20, 'transform:translate(-3px,-3px) scale(1.06,.9)'), (40, 'transform:translate(-6px,-6px) scale(.96,1.06)'),
                          (70, 'transform:translate(-10px,0) scale(1.04,.94)'), (100, 'transform:translate(0,4px) scale(1,1)')])
            + kf('dsFi', [(0, 'transform:translate(420px,0)'), (50, 'transform:translate(150px,-6px)'), (100, 'transform:translate(-110px,4px)')])
            + kf('dsGate', [(0, 'transform:translateX(400px)'), (55, 'transform:translateX(400px)'), (99, 'transform:translateX(-110px)'), (100, 'transform:translateX(-110px)')])
            + kf('dsFin', [(0, 'transform:scaleX(1)'), (100, 'transform:scaleX(.72)')])
            + kf('dsBub', [(0, 'opacity:0;transform:translate(0,0) scale(.5)'), (6, 'opacity:.95;transform:translate(2px,-3px) scale(.8)'),
                           (55, 'opacity:.8;transform:translate(-10px,-28px) scale(1)'), (100, 'opacity:0;transform:translate(-26px,-58px) scale(1.15)')])
            + kf('dsUp', [(0, 'opacity:0;transform:translate(0,0)'), (8, 'opacity:.85'), (25, 'transform:translate(4px,-38px)'), (50, 'transform:translate(-3px,-78px)'),
                          (75, 'transform:translate(4px,-118px)'), (92, 'opacity:.7'), (100, 'opacity:0;transform:translate(-2px,-158px)')]))
    css += reduced('.dsw>:not(.bnr)') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_bubbles():
    """背景の もよう：小さな 泡と 海そうの かげ（うすく）"""
    o = ''
    for x, y, r, op in ((20, 22, 5, .32), (28, 12, 2.6, .28), (96, 70, 6.5, .26), (104, 58, 3, .24), (54, 118, 4, .28), (120, 112, 2.4, .22)):
        o += (f"<circle cx='{x}' cy='{y}' r='{r}' fill='none' stroke='#7FD8EE' stroke-width='1.1' opacity='{op}'/>"
              f"<path d='M{f(x - r * 0.5)} {f(y - r * 0.2)} q{f(r * 0.1)} {f(-r * 0.4)} {f(r * 0.45)} {f(-r * 0.45)}' fill='none' stroke='#BFF1FF' stroke-width='.9' opacity='{op}'/>")
    o += "<path d='M64 140 q-4 -9 0 -17 q4 -8 0 -16' fill='none' stroke='#2BA083' stroke-width='2.4' stroke-linecap='round' opacity='.22'/>"
    o += "<path d='M12 140 q3 -7 0 -13' fill='none' stroke='#2BA083' stroke-width='2' stroke-linecap='round' opacity='.18'/>"
    return tile(140, 140, o)


def wave_strip():
    """上の 帯の 下の ふち：まるい 波（帯の 色）と 小さな 泡"""
    o = ("<path d='M0 0 H24 V3 Q18 9 12 4.6 Q6 9 0 3 Z' fill='#0B2E52'/>"
         "<circle cx='18' cy='8.2' r='1' fill='none' stroke='#7FD8EE' stroke-width='.6' opacity='.7'/>")
    return tile(24, 10, o)


def orn():
    """すみの 飾り（44×44）：帽子を かぶった 小さな タツノオトシゴ（ページに じかに 置くので id なし）"""
    r = RIDERS[0]
    body, shade, light, ridge, finc = r['col']
    c1, c2 = r['cap']
    pts, back, front = _outline(5)
    d = P(back + front[::-1])
    o = (f"<g transform='translate(9 1.6) scale(.4)'>"
         f"<path d='M14.6 49.5 Q2.6 49 1.2 57.6 Q2.6 66.6 15 66.4 Z' fill='{finc}'/>"
         f"<path d='{d}' fill='{body}' stroke='{shade}' stroke-width='1.4'/>"
         f"<path d='M4 38.2 L35.6 34.3 L36.4 45.4 L5 49.6 Z' fill='{c1}'/>"
         f"<path d='{star_d(23.5, 41.8, 4, 1.7)}' fill='{c2}'/>"
         f"<circle cx='29.5' cy='15.5' r='4.6' fill='#FFFFFF'/><circle cx='30.4' cy='15.9' r='3.2' fill='#1E2A3A'/><circle cx='31.4' cy='14.6' r='1.2' fill='#FFFFFF'/>"
         f"<path d='M14 13 Q14 1.5 24.5 1 Q33.5 1 34.5 10.5 Q25 13.6 14 13 Z' fill='{c1}'/><path d='M23.2 1.2 Q26 1 27.2 1.4 L28.6 11.6 Q26.4 12.2 24.4 12.4 Z' fill='{c2}'/>"
         f"<path d='M31.5 9.6 Q38 9 41 12.4 Q36.4 13.2 31 12.4 Z' fill='{mix(c1, '#000000', .25)}'/></g>"
         "<circle cx='34' cy='12' r='3.2' fill='none' stroke='#BFF3FF' stroke-width='1.1'/><circle cx='38' cy='5' r='2' fill='none' stroke='#BFF3FF' stroke-width='1'/>")
    return o


THEME = dict(
    id=ID, cat=7, name='深海', desc='タツノオトシゴのレース', title='深海（紺×ミント×さんご）', banner=ID,
    alt='青い深い海で、騎手の帽子と星のゼッケンをつけたオレンジ・黄・ピンク・ミントのタツノオトシゴ4ひきがレースしている。上から光のすじ、海の底に海そう・さんご・ひとで・貝のイラスト',
    fonts=['Kiwi+Maru:wght@500', 'M+PLUS+Rounded+1c:wght@500;700;800'],
    v=dict(bg='#0B2340', ink='#EAF6FF', sub='#A9C6DD', card='#11304F', cardB='1px solid #22547A', cardO='0 solid transparent', cardS='0 8px 22px rgba(0,0,0,.35)',
           radius='16px', rs='12px', font='"M PLUS Rounded 1c"', dfont='"Kiwi Maru"', dw='500', logo='#7FF0E2', logoS='0 0 12px rgba(95,224,208,.5)',
           iii='#7FF0E2', iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#14507A,#0B2E52)', hdInk='#E3F6FF', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.06)', mLine='rgba(127,240,226,.5)', mInk='#E3F6FF', pill='rgba(255,255,255,.07)', pillLine='rgba(127,240,226,.35)', pillInk='#E3F6FF',
           coin='#FF8A7A', coinInk='#3A0E08', badge='#16395C', badgeInk='#7FF0E2', badgeB='1.5px solid #3DD1C1', tagBg='rgba(255,255,255,.06)', tagInk='#D6ECF8',
           tagLine='#2A5A80', warnBg='rgba(255,138,122,.18)', warnInk='#FFB4A8', zBg='rgba(255,255,255,.04)', zB='1px solid #22547A', znBg='#FF8A7A', znInk='#3A0E08',
           znB='0 solid transparent', znR='999px', znS='none', acc='#7FF0E2', nR='9px', w2B='1.5px solid #8FB3CC', sep='1px dashed #2A5A80',
           btn='#3DD1C1', btnInk='#062A2A', btnB='0 solid transparent', btnR='999px', btnS='0 3px 0 #1F8E84', btn2='transparent', btn2Ink='#7FF0E2',
           btn2B='1.5px solid #3DD1C1', tab='#071B33', tabB='1px solid #14385A', tabInk='#8FB3CC', tabOn='rgba(95,224,208,.14)', tabOnInk='#7FF0E2',
           tabR='14px', sel='#3DD1C1', selInk='#062A2A', h1='#7FF0E2'),
    chk=dict(hd=['#14507A', '#0B2E52']),
    css=[('', 'background-image:' + curi(tile_bubbles()) + ';background-size:140px 140px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-9px;height:10px;background:' + curi(wave_strip()) + ' 0 0/24px 10px repeat-x'),
         ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(95,224,208,.10),transparent 45%)')],
    orn=orn(),
    guide=dict(colors=[('#0B2340', '深い海'), ('#3DD1C1', 'ミント'), ('#FF8A7A', 'さんご'), ('#11304F', 'カード'), ('#EAF6FF', '文字')],
               fonts='見出し：Kiwi Maru<br>本文：M PLUS Rounded 1c', shape='角丸16px・まるい ボタン・帯の 下の ふちが まるい 波と 泡・泡の 背景・すみに 帽子の タツノオトシゴ・的中ボタンは 貝と 真珠の PUSH',
               pic='青い 深い 海・光の すじ・騎手の 帽子と 星の ゼッケンの タツノオトシゴ 4ひきの レース・海そう・さんご・ひとで・貝・泡・くらげ・魚の むれ・ゴールの 門'),
)


# ================================================================== 的中ボタン：貝と 真珠の PUSH（ds）
def push_face(sfx=''):
    """ボタン（200×100）が 大きな 真珠（白い つや・ピンクと 水色の にじ）。まわりに ひらいた 貝（上の から・下の から）。
       ページに じかに 置く SVG なので id は sfx つき（押したあとの コピーと ぶつからない）"""
    g, h = f'dsP{sfx}', f'dsS{sfx}'
    defs = (f'<defs><radialGradient id="{g}" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#F7EEF8"/>'
            '<stop offset=".75" stop-color="#E2D2EC"/><stop offset="1" stop-color="#B9A6CF"/></radialGradient>'
            f'<linearGradient id="{h}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFD6EC" stop-opacity="0"/><stop offset=".35" stop-color="#FFD6EC" stop-opacity=".55"/>'
            '<stop offset=".6" stop-color="#C9F2FF" stop-opacity=".5"/><stop offset="1" stop-color="#C9F2FF" stop-opacity="0"/></linearGradient></defs>')
    o = ''
    # 上の から（うしろに ひらく）
    o += '<path d="M-6 30 Q-4 -40 100 -46 Q204 -40 206 30 Z" fill="#D88AB8"/>'
    o += '<path d="M4 30 Q8 -30 100 -36 Q192 -30 196 30 Z" fill="#F7D6EA"/>'
    for k in range(9):
        a = math.radians(-160 + k * 17.5)
        o += f'<path d="M100 30 L{100 + math.cos(a) * 100:.1f} {30 + math.sin(a) * 66:.1f}" stroke="#E8AACF" stroke-width="2.4" opacity=".75"/>'
    # 下の から
    o += '<path d="M-14 62 Q-10 122 100 124 Q210 122 214 62 Q160 82 100 82 Q40 82 -14 62 Z" fill="#C973A6"/>'
    for k in range(11):
        x = -8 + k * 21.6
        o += f'<path d="M100 120 Q{100 + (x - 100) * 0.55:.1f} {96 + abs(x - 100) * 0.05:.1f} {x:.1f} {66 + abs(x - 100) * 0.06:.1f}" fill="none" stroke="#E79AC6" stroke-width="3" opacity=".8"/>'
    o += '<path d="M-14 62 Q40 82 100 82 Q160 82 214 62" fill="none" stroke="#F4C2DE" stroke-width="3"/>'
    # 真珠（ボタン）
    o += f'<rect x="0" y="0" width="200" height="100" rx="50" fill="url(#{g})"/>'
    o += f'<rect x="0" y="0" width="200" height="100" rx="50" fill="url(#{h})" opacity=".8"/>'
    o += '<ellipse cx="60" cy="24" rx="40" ry="11" fill="#FFFFFF" opacity=".85"/><ellipse cx="160" cy="84" rx="22" ry="6" fill="#FFFFFF" opacity=".45"/>'
    o += '<rect x="1" y="1" width="198" height="98" rx="49" fill="none" stroke="#B9A6CF" stroke-width="2" opacity=".7"/>'
    return f'<i class="dsf" aria-hidden="true"><svg viewBox="-20 -50 240 178" width="240" height="178">{defs}{o}</svg></i>'


def push_decor(sfx=''):
    """まわりの 泡（ゆっくり 上る）と 小さな キラッ"""
    o = ''
    for j, (x, y, r) in enumerate(((-24, 70, 6), (-12, 30, 4), (226, 60, 7), (236, 20, 4.4), (208, -30, 5), (-6, -24, 5.6))):
        o += (f'<g class="dsbo" style="animation-delay:{-0.7 * j:.1f}s"><circle cx="{x}" cy="{y}" r="{r}" fill="#BFF3FF" fill-opacity=".2" stroke="#E8FCFF" stroke-width="1.4"/>'
              f'<path d="M{x - r * 0.5:.1f} {y - r * 0.15:.1f} q{r * 0.1:.1f} {-r * 0.45:.1f} {r * 0.5:.1f} {-r * 0.5:.1f}" fill="none" stroke="#FFFFFF" stroke-width="1.3" stroke-linecap="round"/></g>')
    for j, (x, y, r) in enumerate(((40, -58, 5), (172, -62, 4.4), (100, 130, 4))):
        o += f'<path class="dstw" d="{sparkle_d(x, y, r, 0.18)}" fill="#FFF6FF" style="animation-delay:{-0.9 * j:.1f}s"/>'
    return f'<i class="dsd" aria-hidden="true"><svg viewBox="-40 -80 280 230" width="280" height="230">{o}</svg></i>'


def _bub():
    return doc(24, 24, "<circle cx='12' cy='12' r='10' fill='#BFF3FF' fill-opacity='.2' stroke='#E8FCFF' stroke-width='2'/><path d='M6.6 10 Q7.6 6 11.4 5.4' fill='none' stroke='#FFFFFF' stroke-width='2' stroke-linecap='round'/>")


def _fish(c):
    return doc(26, 16, f"<path d='M2 8 Q10 0 19 8 Q10 16 2 8 Z' fill='{c}'/><path d='M18 8 L25 3 L23.4 8 L25 13 Z' fill='{c}'/><circle cx='6.4' cy='7' r='1.3' fill='#0F2A40'/>")


def _shell():
    return doc(22, 20, "<path d='M2 18 Q11 -2 20 18 Z' fill='#F4C2DE'/><path d='M11 18 L11 4 M7 18 L8.4 6 M15 18 L13.6 6 M4.4 18 L6 9 M17.6 18 L16 9' stroke='#D88AB8' stroke-width='1.2'/>"
                       "<rect x='8' y='17' width='6' height='3' rx='1' fill='#E79AC6'/>")


PIECES = dict(bu=piece(_bub()), pe='border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFFFF,#F2E6F2 50%,#B9A6CF)',
              fo=piece(_fish('#FF9A5A')), fy=piece(_fish('#F7CC45')), sf=piece(doc(24, 24, f"<path d='{star_d(12, 12.6, 11, 4.6)}' fill='#F08A4B'/><circle cx='12' cy='12.6' r='2' fill='#FFC08A'/>")),
              sh=piece(_shell()))


def push_burst():
    return fly_burst('ds', ['bu', 'pe', 'fo', 'bu', 'sf', 'sh', 'bu', 'fy', 'pe'], 30, 51,
                     sizes=dict(bu=(13, 22), pe=(8, 12), fo=(16, 21), fy=(15, 20), sf=(15, 20), sh=(14, 19)))


PUSH_CSS = r'''
/* ---------- 深海の的中ボタン：貝と真珠のPUSH（壁紙パック） ----------
   ボタンが まるごと 大きな 真珠（白い つや・ピンクと 水色の にじ）に「PUSH」。うしろに ひらいた 貝の から（上と 下）。
   まわりに 泡が ゆっくり 上り、小さな キラッ。上下の 動きは 的中と 同じ。押すと 真珠が ちぢんで ふくらみ（強く 光らせない）、
   泡・真珠・魚・ひとで・貝が はじけて 落ち、ミントの 光の 輪が 広がる */
.ds{--pushA:#F7EEF8;--pushB:#14507A;--pushC:#B9A6CF;--rim:#7FF0E2;--rimD:#14507A}
.push.ds{--pr:50px;background:none;border-radius:50px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(8,30,60,.5)) drop-shadow(0 18px 24px rgba(0,0,0,.4))}
.push.ds span{font:500 40px/1 "Kiwi Maru",serif;letter-spacing:.06em;color:#14507A;text-shadow:0 2px 0 #FFFFFF,0 -1px 0 #E2D2EC,0 0 10px rgba(255,255,255,.7)}
.push.ds::after{inset:-22px;border-radius:72px;border-color:rgba(127,240,226,.9)}
.ds .dsf{position:absolute;left:-20px;top:-50px;width:240px;height:178px;pointer-events:none;font-style:normal;z-index:-1}
.ds .dsf svg{display:block;width:240px;height:178px;overflow:visible}
.ds .dsd{position:absolute;left:-40px;top:-80px;width:280px;height:230px;pointer-events:none;z-index:3;font-style:normal}
.ds .dsd svg{display:block;width:280px;height:230px;overflow:visible}
.ds .dsbo{animation:dsBo 3.2s ease-in-out infinite}
@keyframes dsBo{0%{transform:translateY(8px);opacity:0}20%{opacity:1}80%{opacity:1}100%{transform:translateY(-22px);opacity:0}}
.ds .dstw{transform-box:fill-box;transform-origin:50% 50%;animation:dsTw 2.8s ease-in-out infinite}
@keyframes dsTw{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1.05) rotate(20deg)}}
.pshadow.ds{width:230px}
.tap.ds{font-family:"Kiwi Maru",serif;font-weight:500;color:#BFF6EE;letter-spacing:.12em;text-shadow:0 2px 0 #0B2E52,0 0 10px rgba(127,240,226,.6)}
.pressed.ds{border-radius:50px;background:radial-gradient(circle at 38% 30%,#FFFFFF,#F7EEF8 45%,#E2D2EC 75%,#B9A6CF);box-shadow:0 0 0 4px #F7D6EA,0 7px 0 4px #C973A6;animation-name:dsPress,fxH}
@keyframes dsPress{0%{transform:scale(1)}22%{transform:scale(.9)}45%{transform:scale(1.07)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.ds .dsbo,.ds .dstw{animation:none}.clips.ds{display:none}}
''' + fly_css('ds', 'rgba(127,240,226,.9)', PIECES)

PUSH = dict(code='ds', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
