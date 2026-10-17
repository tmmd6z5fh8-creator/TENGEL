"""新しい20個の着せ替え：色・文字・形・飾り（判定画面・選ぶ画面・メモで共通に使う）"""
import math
import random
from urllib.parse import quote


# ---------------------------------------------------------------- 小さな道具
def uri(svg):
    """SVG を CSS の url() に入れられる形にする"""
    s = ' '.join(svg.split()).replace('"', "'")
    return 'url("data:image/svg+xml,' + quote(s, safe=" =:/;,.'()-_") + '")'


def svg(w, h, body, vb=None):
    vb = vb or f'0 0 {w} {h}'
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='{vb}'>{body}</svg>"


def P(pts, close=True):
    s = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s + (' Z' if close else '')


def rot(pts, a, cx=0, cy=0):
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


# ---------------------------------------------------------------- 背景のもよう（タイル）
def tile_petals():
    rnd = random.Random(3)
    petal = 'M0 -6 C3 -6 5 -2 4 2 C3 5 1 6 0 4 C-1 6 -3 5 -4 2 C-5 -2 -3 -6 0 -6 Z'
    body = ''
    for (x, y, a, s, o) in [(18, 22, 20, 1.0, .55), (78, 14, -40, .8, .45), (52, 62, 75, 1.1, .5), (104, 86, 140, .9, .45),
                            (24, 100, -110, .75, .4), (86, 50, 200, .7, .35)]:
        body += f"<path d='{petal}' fill='#F5BCCD' opacity='{o}' transform='translate({x} {y}) rotate({a}) scale({s})'/>"
    return uri(svg(120, 120, body))


def maple_pts(r_scale=1.0, serr=0.9, n=260):
    lobes = [(-90, 15), (-140, 13.5), (-40, 13.5), (-192, 10.5), (12, 10.5)]
    pts = []
    for i in range(n):
        th = -math.pi / 2 + 2 * math.pi * i / n
        d = math.degrees(th)
        r = 4.2
        lf = 0
        for (phi, L) in lobes:
            dd = (d - phi + 540) % 360 - 180
            f = max(0.0, 1 - abs(dd) / 23) ** 1.35
            if f * L > lf:
                lf = f * L
        r += lf
        if lf > 2:
            r += serr * math.sin(th * 46) * min(1, lf / 8)
        pts.append((r * r_scale * math.cos(th), r * r_scale * math.sin(th)))
    return pts


def tile_leaves():
    body = ''
    for (x, y, a, s, c, o) in [(26, 30, 15, .55, '#E4572E', .16), (100, 24, -30, .45, '#F2A13A', .2), (66, 86, 60, .5, '#C9431C', .14),
                               (126, 112, -10, .4, '#E4572E', .16), (20, 120, 40, .42, '#F2A13A', .18)]:
        pts = [(x + px, y + py) for px, py in rot(maple_pts(s, .5, 120), math.radians(a))]
        body += f"<path d='{P(pts)}' fill='{c}' opacity='{o}'/>"
    return uri(svg(150, 150, body))


def clover_body(cx, cy, s, fill, stroke, vein, sw=1.0):
    heart = 'M0 0 C-2 -3 -9 -5 -9 -10 C-9 -14 -4 -15 0 -11 C4 -15 9 -14 9 -10 C9 -5 2 -3 0 0 Z'
    b = f"<path d='M{cx} {cy} q{4*s} {9*s} {1*s} {18*s}' stroke='{stroke}' stroke-width='{2*s:.2f}' fill='none' stroke-linecap='round'/>"
    for k in range(4):
        a = 45 + 90 * k
        b += (f"<path d='{heart}' fill='{fill}' stroke='{stroke}' stroke-width='{sw/s:.2f}' stroke-linejoin='round' "
              f"transform='translate({cx} {cy}) rotate({a}) scale({s})'/>")
        if vein:
            b += f"<path d='M0 0 L0 -10' stroke='{vein}' stroke-width='{.9/s:.2f}' transform='translate({cx} {cy}) rotate({a}) scale({s})'/>"
    return b


def tile_clovers():
    body = ''
    for (x, y, s, o) in [(24, 26, .5, .13), (92, 70, .42, .11), (40, 104, .36, .1)]:
        body += f"<g opacity='{o}'>" + clover_body(x, y, s, '#2E8A48', '#2E8A48', None) + '</g>'
    return uri(svg(130, 130, body))


def tile_lucky():
    """白い地にうすく：小さな桜（桃色）と小判の線（金）"""
    body = ''
    for (x, y, r, o) in [(26, 30, 7, .55), (88, 86, 6, .5)]:
        pet = ''.join(f"<ellipse cx='{x}' cy='{y - r * .58:.2f}' rx='{r * .42:.2f}' ry='{r * .58:.2f}' transform='rotate({k * 72} {x} {y})' fill='#F7C6D2'/>"
                      for k in range(5))
        body += f"<g opacity='{o}'>{pet}<circle cx='{x}' cy='{y}' r='{r * .22:.2f}' fill='#EDBF55'/></g>"
    body += ("<g opacity='.5' fill='none' stroke='#E2C27C' stroke-width='1.4'><ellipse cx='86' cy='28' rx='6' ry='8.5'/>"
             "<ellipse cx='30' cy='94' rx='5' ry='7'/></g>")
    return uri(svg(120, 120, body))


def tile_seigaiha(bg, line, w=40):
    h = w // 2
    body = ''
    for (cx, cy) in [(0, 0), (w, 0), (h, h / 2 * 0 + w / 4), (0, h), (w, h)]:
        body += f"<circle cx='{cx}' cy='{cy}' r='{h - .3:.2f}' fill='{bg}'/>"
        for r in (h - 1.2, h * .72, h * .46, h * .2):
            body += f"<circle cx='{cx}' cy='{cy}' r='{r:.2f}' fill='none' stroke='{line}' stroke-width='1.1'/>"
    return uri(svg(w, h, body))


def tile_waves():
    body = ("<path d='M0 8 Q7.5 3 15 8 T30 8 T45 8 T60 8' fill='none' stroke='#0E3A66' stroke-opacity='.06' stroke-width='1.4'/>"
            "<path d='M-15 20 Q-7.5 15 0 20 T15 20 T30 20 T45 20 T60 20' fill='none' stroke='#0E3A66' stroke-opacity='.045' stroke-width='1.4'/>")
    return uri(svg(60, 24, body))


def wave_edge():
    body = ("<path d='M0 0 H28 V4 Q21 9 14 4 Q7 -1 0 4 Z' fill='#14558A'/>"
            "<path d='M0 4 Q7 -1 14 4 Q21 9 28 4' fill='none' stroke='#FFFFFF' stroke-opacity='.75' stroke-width='1.3'/>")
    return uri(svg(28, 9, body))


def lanterns():
    def one(x, c, hi):
        return (f"<line x1='{x}' y1='1.2' x2='{x}' y2='3.6' stroke='#3A2A18' stroke-width='.7'/>"
                f"<ellipse cx='{x}' cy='8.6' rx='4.3' ry='4.8' fill='{c}'/>"
                f"<ellipse cx='{x}' cy='8.6' rx='2.2' ry='3.6' fill='{hi}' opacity='.75'/>"
                f"<path d='M{x-4} 7.2 H{x+4} M{x-4.2} 9.4 H{x+4.2} M{x-3.6} 11.4 H{x+3.6}' stroke='#000' stroke-opacity='.18' stroke-width='.6'/>"
                f"<rect x='{x-2.2}' y='3.4' width='4.4' height='1.6' rx='.4' fill='#2A1A10'/>"
                f"<rect x='{x-2.2}' y='12.6' width='4.4' height='1.4' rx='.4' fill='#2A1A10'/>")
    body = ("<path d='M0 1.2 Q15 3.4 30 1.2 T60 1.2' fill='none' stroke='#5A4A30' stroke-width='.8'/>"
            + one(15, '#E8343C', '#FF9A6A') + one(45, '#F28C28', '#FFD08A'))
    return uri(svg(60, 15, body))


def stars_line():
    pts = [(0, 7), (17, 3.5), (38, 8.5), (60, 3), (79, 7.5), (96, 7)]
    body = f"<path d='{P(pts, False)}' fill='none' stroke='#B9ACFF' stroke-opacity='.55' stroke-width='.8'/>"
    for i, (x, y) in enumerate(pts[:-1]):
        r = 1.6 if i % 2 == 0 else 1.1
        body += f"<circle cx='{x}' cy='{y}' r='{r}' fill='#FFD86B'/>"
    return uri(svg(96, 12, body))


def washi_full(seed=7, W=390, H=900, n=260):
    rnd = random.Random(seed)
    body = ''
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        L = rnd.uniform(8, 26)
        a = rnd.uniform(0, math.pi)
        x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
        cx, cy = (x + x2) / 2 + rnd.uniform(-4, 4), (y + y2) / 2 + rnd.uniform(-4, 4)
        o = rnd.uniform(.05, .13)
        body += f"<path d='M{x:.1f} {y:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}' fill='none' stroke='#7A6A50' stroke-opacity='{o:.2f}' stroke-width='.6'/>"
    return uri(svg(W, H, body))


def marble_full(seed=11, W=390, H=900):
    rnd = random.Random(seed)
    body = ''
    for k in range(9):
        y0 = rnd.uniform(-100, H)
        pts = []
        x, y = -10, y0
        ang = rnd.uniform(-.35, .55)
        while x < W + 10:
            pts.append((x, y))
            ang += rnd.uniform(-.25, .25)
            ang = max(-.8, min(.9, ang))
            x += 14
            y += 14 * math.tan(ang)
        o = rnd.uniform(.05, .11)
        w = rnd.uniform(.6, 1.3)
        body += f"<path d='{P(pts, False)}' fill='none' stroke='#8C7E6A' stroke-opacity='{o:.2f}' stroke-width='{w:.2f}'/>"
        # 細い枝
        if len(pts) > 6:
            i = rnd.randint(2, len(pts) - 4)
            bx, by = pts[i]
            q = [(bx, by)]
            a2 = ang + rnd.choice([-1, 1]) * .7
            for _ in range(6):
                bx += 10
                by += 10 * math.tan(a2)
                a2 += rnd.uniform(-.3, .3)
                q.append((bx, by))
            body += f"<path d='{P(q, False)}' fill='none' stroke='#8C7E6A' stroke-opacity='{o*.7:.2f}' stroke-width='.5'/>"
    return uri(svg(W, H, body))


def brush_line():
    rnd = random.Random(5)
    top, bot = [], []
    n = 60
    for i in range(n + 1):
        x = 374 * i / n
        t = i / n
        th = 2.2 + 3.2 * math.sin(math.pi * min(1, t * 1.15)) ** .6
        y = 3.6 + .6 * math.sin(t * 9)
        top.append((x, y - th / 2 + rnd.uniform(-.25, .25)))
        bot.append((x, y + th / 2 + rnd.uniform(-.25, .25)))
    pts = top + bot[::-1]
    body = f"<path d='{P(pts)}' fill='#1A1A1A' opacity='.88'/>"
    for k in range(5):  # かすれ
        y = rnd.uniform(2.5, 4.8)
        x0 = rnd.uniform(200, 330)
        body += f"<path d='M{x0:.1f} {y:.1f} H{x0 + rnd.uniform(20, 44):.1f}' stroke='#F6F3EC' stroke-width='.45' opacity='.9'/>"
    return uri(svg(374, 8, body))


def enso_uri():
    return uri(svg(70, 70, ENSO_BODY, '0 0 44 44'))


ENSO_BODY = ("<defs><filter id='rg' x='-20%' y='-20%' width='140%' height='140%'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='3'/>"
             "<feDisplacementMap in='SourceGraphic' scale='1.6'/></filter></defs>"
             "<g filter='url(#rg)'><path d='M29.5 9.0 A15 15 0 1 0 36.1 16.9' fill='none' stroke='#1A1A1A' stroke-width='3.6' stroke-linecap='round' opacity='.22'/></g>")


# ---------------------------------------------------------------- カードのすみの飾り（44×44）
def orn_sakura():
    petal = 'M0 0 C-6 -4 -9 -13 -4.4 -18.5 L0 -15.6 L4.4 -18.5 C9 -13 6 -4 0 0 Z'
    b = ''
    for k in range(5):
        b += f"<path d='{petal}' fill='#F9C3D3' stroke='#C9577F' stroke-width='1.2' stroke-linejoin='round' transform='translate(22 22) rotate({k*72 + 8})'/>"
    for k in range(5):
        a = math.radians(k * 72 + 44 - 90)
        x, y = 22 + 6 * math.cos(a), 22 + 6 * math.sin(a)
        b += f"<line x1='22' y1='22' x2='{x:.1f}' y2='{y:.1f}' stroke='#E0668F' stroke-width='.9'/><circle cx='{x:.1f}' cy='{y:.1f}' r='1.1' fill='#E0668F'/>"
    b += "<circle cx='22' cy='22' r='2.6' fill='#E0668F'/>"
    return b


def orn_sea():
    c = 2 * math.pi * 13 / 8
    return ("<circle cx='22' cy='23' r='13' fill='none' stroke='#FFFFFF' stroke-width='7.4'/>"
            f"<circle cx='22' cy='23' r='13' fill='none' stroke='#E5484D' stroke-width='7.4' stroke-dasharray='{c:.2f} {c:.2f}' transform='rotate(-22.5 22 23)'/>"
            "<circle cx='22' cy='23' r='16.8' fill='none' stroke='#0E3A66' stroke-width='1.3'/>"
            "<circle cx='22' cy='23' r='9.2' fill='none' stroke='#0E3A66' stroke-width='1.3'/>"
            "<path d='M8 12 Q14 6 22 6.4 Q30 6 36 12' fill='none' stroke='#0E3A66' stroke-width='1' stroke-dasharray='2 2'/>")


def orn_sunset():
    return ("<defs><linearGradient id='sg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FFE0A0'/><stop offset='1' stop-color='#FF6A4D'/></linearGradient></defs>"
            "<clipPath id='sk'><circle cx='22' cy='25' r='16.5'/></clipPath>"
            "<circle cx='22' cy='25' r='17.5' fill='#FFFFFF'/>"
            "<g clip-path='url(#sk)'><rect x='0' y='0' width='44' height='44' fill='#FFE7D6'/>"
            "<circle cx='22' cy='29' r='16' fill='#FFB98A' opacity='.45'/>"
            "<circle cx='22' cy='29' r='10.5' fill='url(#sg)'/>"
            "<path d='M0 32 C8 26.5 15 25.5 22 28.5 C29 31.5 35 28.5 44 26.5 V44 H0 Z' fill='#4B2470'/>"
            "<path d='M0 37 C10 32.5 19 34 29 36 C35 37.2 40 35.5 44 34.5 V44 H0 Z' fill='#2E1748'/></g>"
            "<circle cx='22' cy='25' r='16.5' fill='none' stroke='#E2A08A' stroke-width='1.2'/>"
            "<path d='M12 17 q2.4 -2.4 4.8 0 q2.4 -2.4 4.8 0' fill='none' stroke='#3A1D5C' stroke-width='1.3' stroke-linecap='round'/>"
            "<path d='M25 13 q1.7 -1.7 3.4 0 q1.7 -1.7 3.4 0' fill='none' stroke='#3A1D5C' stroke-width='1.1' stroke-linecap='round'/>")


def orn_autumn():
    pts = [(22 + x, 21 + y) for x, y in rot(maple_pts(1.05), math.radians(-12))]
    b = f"<path d='M22 25 Q24 33 21 41' stroke='#8E2E14' stroke-width='1.8' fill='none' stroke-linecap='round'/>"
    b += f"<path d='{P(pts)}' fill='#E4572E' stroke='#A33A16' stroke-width='1.1' stroke-linejoin='round'/>"
    for (phi, L) in [(-90, 13), (-140, 11.5), (-40, 11.5), (-192, 8.5), (12, 8.5)]:
        a = math.radians(phi - 12)
        b += f"<line x1='22' y1='21' x2='{22 + L*math.cos(a):.1f}' y2='{21 + L*math.sin(a):.1f}' stroke='#B8401A' stroke-width='.9'/>"
    return b


def orn_snow():
    b = "<g stroke='#7FB2DD' stroke-width='2.2' stroke-linecap='round' fill='none'>"
    for k in range(6):
        a = math.radians(k * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        b += f"<line x1='22' y1='22' x2='{22+17*ca:.1f}' y2='{22+17*sa:.1f}'/>"
        for (r, L) in [(8, 4.6), (12.5, 3.8)]:
            px, py = 22 + r * ca, 22 + r * sa
            for s in (-1, 1):
                b2 = a + s * math.radians(45)
                b += f"<line x1='{px:.1f}' y1='{py:.1f}' x2='{px+L*math.cos(b2):.1f}' y2='{py+L*math.sin(b2):.1f}'/>"
    b += "</g><circle cx='22' cy='22' r='2.6' fill='#FFFFFF' stroke='#7FB2DD' stroke-width='1.6'/>"
    return b


def orn_newyear():
    b = ''
    for k in range(5):
        a = math.radians(k * 72 - 90)
        b += f"<circle cx='{22+7.4*math.cos(a):.1f}' cy='{22+7.4*math.sin(a):.1f}' r='7' fill='#E04A5A' stroke='#9E1F30' stroke-width='1.1'/>"
    b += "<circle cx='22' cy='22' r='5.2' fill='#FFF3D6'/>"
    for k in range(5):
        a = math.radians(k * 72 - 54)
        x, y = 22 + 4.6 * math.cos(a), 22 + 4.6 * math.sin(a)
        b += f"<line x1='22' y1='22' x2='{x:.1f}' y2='{y:.1f}' stroke='#C9952B' stroke-width='.9'/><circle cx='{x:.1f}' cy='{y:.1f}' r='1.2' fill='#E8B33A'/>"
    b += "<circle cx='22' cy='22' r='1.8' fill='#C9952B'/>"
    return b


def orn_fireworks():
    b = ''
    for k in range(16):
        a = math.radians(k * 22.5 + 6)
        c = '#FF6B9A' if k % 2 == 0 else '#FFD45E'
        r1 = 5 if k % 2 == 0 else 7
        b += (f"<line x1='{22+r1*math.cos(a):.1f}' y1='{22+r1*math.sin(a):.1f}' x2='{22+15*math.cos(a):.1f}' y2='{22+15*math.sin(a):.1f}' "
              f"stroke='{c}' stroke-width='1.8' stroke-linecap='round'/><circle cx='{22+18.5*math.cos(a):.1f}' cy='{22+18.5*math.sin(a):.1f}' r='1.5' fill='{c}'/>")
    b += "<circle cx='22' cy='22' r='2.4' fill='#FFFFFF'/>"
    return "<g style='filter:drop-shadow(0 0 3px rgba(255,107,154,.6))'>" + b + "</g>"


def orn_night():
    b = ("<defs><linearGradient id='bm' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.35'/><stop offset='1' stop-color='#FFFFFF' stop-opacity='0'/></linearGradient></defs>"
         "<path d='M8 20 H36 L46 44 H-2 Z' fill='url(#bm)'/>"
         "<rect x='20.5' y='20' width='3' height='24' fill='#6A738F'/>"
         "<rect x='6' y='3' width='32' height='18' rx='2' fill='#232B48' stroke='#8790AE' stroke-width='1.2'/>")
    for r in range(2):
        for c in range(4):
            x, y = 11 + c * 7.3, 8 + r * 7
            b += f"<circle cx='{x:.1f}' cy='{y}' r='4.2' fill='#FFF3C8' opacity='.35'/><circle cx='{x:.1f}' cy='{y}' r='2.5' fill='#FFFFFF'/>"
    return b


def orn_news():
    return ("<defs><filter id='st' x='-10%' y='-10%' width='120%' height='120%'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' seed='4'/>"
            "<feDisplacementMap in='SourceGraphic' scale='1.4'/></filter></defs>"
            "<g filter='url(#st)' transform='rotate(-10 22 22)' fill='none' stroke='#C81E1E' stroke-width='2.8'>"
            "<circle cx='22' cy='22' r='15.5'/><circle cx='22' cy='22' r='8.6'/></g>")


def orn_silks():
    body = 'M14 4 L19.5 6 Q22 9.5 24.5 6 L30 4 L40.5 12.5 L35.5 19 L31 15.5 L31 41 L13 41 L13 15.5 L8.5 19 L3.5 12.5 Z'
    return ("<defs><clipPath id='jb'><path d='" + body + "'/></clipPath></defs>"
            f"<path d='{body}' fill='#1A3FB8'/>"
            "<g clip-path='url(#jb)'><path d='M14 4 L3.5 12.5 L8.5 19 L13 15.5 Z M30 4 L40.5 12.5 L35.5 19 L31 15.5 Z' fill='#E02424'/>"
            "<path d='M10 6 L16 3 L40 38 L34 44 Z' fill='#FFC400'/></g>"
            f"<path d='{body}' fill='none' stroke='#121A33' stroke-width='1.4' stroke-linejoin='round'/>"
            "<path d='M19.5 6 Q22 9.5 24.5 6' fill='none' stroke='#FFFFFF' stroke-width='1.4'/>")


def orn_chess():
    knight = ('M14 35 C14 31 15 28 17 26 C15 25 13 24 11 24.5 L7 25.5 C5.5 25.8 4.5 24.5 5 23 L6.5 19.5 C8 16 10 13.5 12.5 11.5 '
              'L14.5 7.5 L17 3 L18.5 7.2 C23 7 28 10 30.5 15 C32.5 20 32 28 30 35 Z')
    return ("<g transform='translate(3 0)'>"
            "<path d='M8 44 H34 V40 H8 Z M10 40 H32 L30 35 H12 Z' fill='#111111'/>"
            f"<path d='{knight}' fill='#111111'/>"
            "<circle cx='13.6' cy='15' r='1.3' fill='#FFFFFF'/>"
            "<path d='M20.5 8.6 C25.5 11 28.4 17 28.2 26' fill='none' stroke='#FFFFFF' stroke-opacity='.45' stroke-width='1'/></g>")


def orn_shogi():
    pc = '20,3 33,9 37,43 3,43 7,9'
    return ("<defs><linearGradient id='pg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#F9E9C0'/><stop offset='1' stop-color='#E0BE7A'/></linearGradient></defs>"
            f"<polygon points='{pc}' fill='#3E2611' opacity='.25' transform='translate(1.6 1.8)'/>"
            f"<polygon points='{pc}' fill='url(#pg)' stroke='#8A6A3A' stroke-width='1.3' stroke-linejoin='round'/>"
            "<text x='20' y='33' text-anchor='middle' font-family='Zen Antique, serif' font-size='19' fill='#1A1208'>桂</text>")


def orn_ink():
    return ("<defs><filter id='rg2' x='-20%' y='-20%' width='140%' height='140%'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='3'/>"
            "<feDisplacementMap in='SourceGraphic' scale='1.8'/></filter></defs>"
            "<g filter='url(#rg2)'><path d='M29.5 9.0 A15 15 0 1 0 36.1 16.9' fill='none' stroke='#1A1A1A' stroke-width='4.2' stroke-linecap='round'/>"
            "<path d='M31 11 A12.6 12.6 0 0 0 10 16' fill='none' stroke='#F6F3EC' stroke-width='.7' opacity='.8'/></g>"
            "<rect x='30.5' y='29' width='9.5' height='9.5' rx='1' fill='#B7282E'/>"
            "<path d='M33 31.6 H37.6 M35.3 31.6 V36.2 M33 34 H37.6' stroke='#F6F3EC' stroke-width='1'/>")


def orn_neon():
    return ("<defs><linearGradient id='ng' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FFE45E'/><stop offset='1' stop-color='#FF2BD6'/></linearGradient>"
            "<mask id='nm'><rect width='44' height='44' fill='#FFFFFF'/><rect x='0' y='23' width='44' height='1.6' fill='#000'/>"
            "<rect x='0' y='27.4' width='44' height='2' fill='#000'/><rect x='0' y='32' width='44' height='2.4' fill='#000'/></mask>"
            "<filter id='gl' x='-40%' y='-40%' width='180%' height='180%'><feGaussianBlur stdDeviation='2'/></filter></defs>"
            "<circle cx='22' cy='23' r='14' fill='#FF2BD6' filter='url(#gl)' opacity='.8'/>"
            "<circle cx='22' cy='23' r='14' fill='url(#ng)' mask='url(#nm)'/>"
            "<path d='M4 38.5 H40' stroke='#00F0FF' stroke-width='1.6' stroke-linecap='round' style='filter:drop-shadow(0 0 2px #00F0FF)'/>")


def orn_pixel():
    H = ['.XX...XX.', 'XXXX.XXXX', 'XXXXXXXXX', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..', '...XXX...', '....X....']
    filled = {(x, y) for y, row in enumerate(H) for x, c in enumerate(row) if c == 'X'}
    s = 4
    ox, oy = 4, 6
    b = "<g shape-rendering='crispEdges'>"
    out = set()
    for (x, y) in filled:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in filled:
                out.add(q)
    for (x, y) in out:
        b += f"<rect x='{ox + x*s}' y='{oy + y*s}' width='{s}' height='{s}' fill='#000000'/>"
    for (x, y) in filled:
        c = '#FF004D'
        if (x, y) in {(1, 1), (1, 2), (2, 1)}:
            c = '#FFF1E8'
        elif (x, y) in {(7, 4), (6, 5), (5, 6), (8, 3)}:
            c = '#7E2553'
        b += f"<rect x='{ox + x*s}' y='{oy + y*s}' width='{s}' height='{s}' fill='{c}'/>"
    return b + '</g>'


def orn_chalk():
    pts = []
    for i in range(80):
        t = i / 79 * 3.4 * math.pi
        r = .8 + 1.55 * t
        pts.append((22 + r * math.cos(t), 22 + r * math.sin(t)))
    d = P(pts, False)
    pet = ''
    n = 9
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        x0, y0 = 22 + 12 * math.cos(a0), 22 + 12 * math.sin(a0)
        x1, y1 = 22 + 12 * math.cos(a1), 22 + 12 * math.sin(a1)
        cx, cy = 22 + 22 * math.cos(am), 22 + 22 * math.sin(am)
        pet += (f'M{x0:.1f} {y0:.1f} ' if k == 0 else '') + f'Q{cx:.1f} {cy:.1f} {x1:.1f} {y1:.1f} '
    return ("<defs><filter id='ck' x='-10%' y='-10%' width='120%' height='120%'><feTurbulence type='fractalNoise' baseFrequency='1.6' numOctaves='2' seed='9' result='n'/>"
            "<feDisplacementMap in='SourceGraphic' in2='n' scale='1.3' result='d'/><feComposite in='d' in2='n' operator='arithmetic' k1='0' k2='1' k3='-.35' k4='.1'/></filter></defs>"
            f"<g filter='url(#ck)' fill='none' stroke='#F4A6C0' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'>"
            f"<path d='{d}'/><path d='{pet}Z'/></g>")


def orn_carousel():
    xs = [4, 10, 16, 22, 28, 34, 40]
    b = "<line x1='22' y1='1' x2='22' y2='8' stroke='#C9952B' stroke-width='1.4'/><path d='M22 1.2 L30 3.4 L22 5.6 Z' fill='#E86A92'/>"
    for i in range(6):
        c = '#F49AC1' if i % 2 == 0 else '#FFFFFF'
        b += f"<path d='M22 8 L{xs[i]} 24 L{xs[i+1]} 24 Z' fill='{c}'/>"
    b += "<path d='M22 8 L40 24 H4 Z' fill='none' stroke='#C9952B' stroke-width='1.3' stroke-linejoin='round'/>"
    for i in range(6):
        c = '#F49AC1' if i % 2 == 0 else '#FFFFFF'
        x = 7 + i * 6
        b += f"<path d='M{x-3} 24 A3 3 0 0 0 {x+3} 24 Z' fill='{c}' stroke='#C9952B' stroke-width='1'/>"
    b += "<rect x='8' y='29' width='28' height='3' rx='1.5' fill='#E9C46A'/>"
    for x in (11, 22, 33):
        b += f"<line x1='{x}' y1='29' x2='{x}' y2='42' stroke='#C9952B' stroke-width='1.6'/>"
    b += "<rect x='6' y='41' width='32' height='3' rx='1.5' fill='#E9C46A'/>"
    for x in (7, 13, 19, 25, 31, 37):
        b += f"<circle cx='{x}' cy='27' r='1.1' fill='#FFF3B8'/>"
    return b


def orn_stars():
    return ("<defs><mask id='cm'><rect width='44' height='44' fill='#FFFFFF'/><circle cx='26.5' cy='17.5' r='11' fill='#000'/></mask></defs>"
            "<circle cx='20' cy='23' r='13' fill='#FFD86B' mask='url(#cm)' style='filter:drop-shadow(0 0 4px rgba(255,216,107,.6))'/>"
            "<path d='M35 3 Q36 9 42 10 Q36 11 35 17 Q34 11 28 10 Q34 9 35 3 Z' fill='#FFF4D6'/>"
            "<circle cx='31' cy='31' r='1.4' fill='#FFF4D6'/><circle cx='6' cy='6' r='1' fill='#FFF4D6'/>")


def orn_lucky():
    """小判（金の楕円・ござ目・まん中の刻印・上下の丸い印・つや）＋キラッ"""
    b = ("<defs><linearGradient id='kb1' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFF6CC'/><stop offset='.45' stop-color='#F2C94F'/>"
         "<stop offset='1' stop-color='#B9861F'/></linearGradient></defs>")
    g = "<g transform='rotate(-14 22 23)'>"
    g += "<ellipse cx='22' cy='23' rx='12.5' ry='17.5' fill='url(#kb1)' stroke='#7A560E' stroke-width='1.5'/>"
    g += "<ellipse cx='22' cy='23' rx='9.3' ry='14.2' fill='none' stroke='#C9952B' stroke-width='.9'/>"
    for k in range(-5, 6):
        y = 23 + k * 2.4
        hw = 8.6 * math.sqrt(max(0.0, 1 - ((y - 23) / 14.4) ** 2))
        if hw > 2.2 and abs(k) > 2:
            g += f"<line x1='{22 - hw:.2f}' y1='{y:.2f}' x2='{22 + hw:.2f}' y2='{y:.2f}' stroke='#D9A63A' stroke-width='.8'/>"
    g += "<rect x='18.4' y='16.6' width='7.2' height='12.8' rx='1' fill='#FFF1BC' stroke='#9A6A12' stroke-width='.8'/>"
    g += "<path d='M20 20h4M20 23h4M20.6 26h2.8M22 19v8' stroke='#8A5A0E' stroke-width='.9' stroke-linecap='round'/>"
    g += "<circle cx='22' cy='10.6' r='1.7' fill='#E9B840' stroke='#9A6A12' stroke-width='.6'/>"
    g += "<circle cx='22' cy='35.4' r='1.7' fill='#E9B840' stroke='#9A6A12' stroke-width='.6'/>"
    g += "<path d='M13.6 15.5 C14.6 11.2 17.4 8.4 21 7.4' stroke='#FFFFFF' stroke-width='1.5' fill='none' stroke-linecap='round' opacity='.85'/>"
    g += "</g>"
    st = "<path d='M37 3.5 L38.2 7.3 L42 8.5 L38.2 9.7 L37 13.5 L35.8 9.7 L32 8.5 L35.8 7.3 Z' fill='#FFE7A6' stroke='#C9952B' stroke-width='.5'/>"
    return b + g + st


def orn_marble():
    """月桂樹の冠（左右の枝・下に結び目）"""
    leaf = 'M0 0 C2.6 -2.4 7.4 -2.5 10 0 C7.4 2.5 2.6 2.4 0 0 Z'
    b = ("<defs><linearGradient id='lg' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#F6DC8C'/><stop offset='.55' stop-color='#C9952B'/>"
         "<stop offset='1' stop-color='#E9C46A'/></linearGradient></defs>")
    for side in (-1, 1):
        p0, p1, p2 = (22 + side * 2.5, 40.5), (22 + side * 19, 33), (22 + side * 13, 6)

        def bez(t):
            return tuple((1 - t) ** 2 * p0[i] + 2 * (1 - t) * t * p1[i] + t * t * p2[i] for i in (0, 1))

        def tan(t):
            return tuple(2 * (1 - t) * (p1[i] - p0[i]) + 2 * t * (p2[i] - p1[i]) for i in (0, 1))
        b += f"<path d='M{p0[0]} {p0[1]} Q{p1[0]} {p1[1]} {p2[0]} {p2[1]}' fill='none' stroke='#A87C22' stroke-width='1.3' stroke-linecap='round'/>"
        for t in (.16, .34, .52, .70, .86):
            x, y = bez(t)
            tx, ty = tan(t)
            a = math.degrees(math.atan2(ty, tx))
            for k in (-1, 1):
                ang = a + k * 38
                sc_ = 1.0 - t * .3
                b += f"<path d='{leaf}' transform='translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({sc_:.2f})' fill='url(#lg)' stroke='#9A7420' stroke-width='.6'/>"
        x, y = p2
        tx, ty = tan(1)
        b += f"<path d='{leaf}' transform='translate({x:.1f} {y:.1f}) rotate({math.degrees(math.atan2(ty, tx)):.0f}) scale(.75)' fill='url(#lg)' stroke='#9A7420' stroke-width='.6'/>"
    b += "<path d='M22 40 L17.5 44 M22 40 L26.5 44' stroke='#C9952B' stroke-width='1.6' stroke-linecap='round'/><circle cx='22' cy='40' r='2' fill='#E9C46A' stroke='#9A7420' stroke-width='.6'/>"
    return b


def tile_scales():
    """龍馬：うすい金の線の うろこ（六角の うろこを 互いちがいに）"""
    body = ''
    arc = 'M-10 0 A10 10 0 0 0 10 0'
    for (x, y) in [(10, 8), (30, 8), (0, 18), (20, 18), (40, 18), (10, 28), (30, 28), (0, 38), (20, 38), (40, 38)]:
        body += f"<path d='{arc}' fill='none' stroke='#C9952B' stroke-width='.7' opacity='.16' transform='translate({x} {y}) scale(1 -1)'/>"
    return uri(svg(40, 40, body))


def orn_ryuma():
    """瑞雲（金の線のうず）と、赤い玉"""
    out = ("<defs><linearGradient id='rg' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#F6DC8C'/><stop offset='.6' stop-color='#C9952B'/>"
           "<stop offset='1' stop-color='#E9C46A'/></linearGradient></defs>")
    for (cx, cy, r0, flip) in ((17, 24, 11, 1), (31, 29, 7, -1), (29, 15, 6, -1)):
        pts = []
        for k in range(61):
            u = k / 60
            a = u * 1.3 * 2 * math.pi * flip + (math.pi if flip < 0 else 0)
            r = r0 * (1 - 0.84 * u)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.85))
        out += f"<path d='{P(pts, close=False)}' fill='none' stroke='url(#rg)' stroke-width='1.5' stroke-linecap='round'/>"
    out += "<path d='M5 20 C9 10 17 7 26 9' fill='none' stroke='#C9952B' stroke-width='1.1' stroke-linecap='round' opacity='.8'/>"
    out += "<path d='M8 32 C12 38 22 40 34 37' fill='none' stroke='#C9952B' stroke-width='1.1' stroke-linecap='round' opacity='.8'/>"
    out += "<circle cx='36' cy='8' r='3.2' fill='#E0362C'/><circle cx='35' cy='7' r='1' fill='#FFB4A0'/>"
    return out


# ---------------------------------------------------------------- テーマ
SEG_SQ = '.mbtn,.pill,.seg,.tag,.coin,.ocr{border-radius:0}'

THEMES = [
 dict(id='sakura', cat=2, name='桜', desc='ピンク・春の桜', title='桜（ピンク×若草）', banner='sakura', alt='満開の桜の下に立つ白い競走馬（すらりとした足・桜色のたてがみ・耳もとの桜の花かざり・桜色のゼッケン1）のイラスト',
      fonts=['Kaisei+Decol:wght@700', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#FFF6F8', ink='#4A2A35', sub='#87596A', card='#FFFFFF', cardB='1.5px solid #F4C6D4', cardO='0 solid transparent', cardS='0 4px 12px rgba(214,110,150,.12)',
             radius='18px', rs='14px', font='"Zen Kaku Gothic New"', dfont='"Kaisei Decol"', dw='700', logo='#8A2D52', logoS='0 2px 0 rgba(255,255,255,.75)',
             iii='#E77FA1', iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#FDE6EC,#F8C4D4)', hdInk='#6E2440', hdB='3px solid #EE9DB8',
             mBg='#FFFFFF', mLine='#E9A3BA', mInk='#9A2F57', pill='rgba(255,255,255,.78)', pillLine='#F2B5C8', pillInk='#7A2A4A', coin='#D9567F', coinInk='#FFFFFF',
             badge='#FFE9F0', badgeInk='#A3355C', badgeB='1.5px solid #F4C6D4', tagBg='#FFF0F4', tagInk='#8A3456', tagLine='#F4C6D4', warnBg='#FFE3E8', warnInk='#A8323E',
             zBg='#FFF7F9', zB='1.5px solid #FBDDE6', znBg='#B83C66', znInk='#FFFFFF', znB='0 solid transparent', znR='999px', znS='none', acc='#A3355C', nR='8px',
             w2B='0 solid transparent', sep='1.5px dashed #F4C6D4', btn='#C2416E', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='14px', btnS='0 3px 0 #9A2C52',
             btn2='#FFFFFF', btn2Ink='#B23A63', btn2B='1.5px solid #F2B5C8', tab='#FFFFFF', tabB='1px solid #F6D3DE', tabInk='#8E5F72', tabOn='#FCE3EB', tabOnInk='#A3355C', tabR='14px',
             sel='#C2416E', selInk='#FFFFFF', h1='#A3355C'),
      chk=dict(hd=['#FDE6EC', '#F8C4D4']),
      css=[('', 'background-image:' + tile_petals() + ';background-size:120px 120px')],
      orn=orn_sakura(),
      guide=dict(colors=[('#F8C4D4', '桜色'), ('#C2416E', 'ボタン'), ('#A3355C', '濃い桜'), ('#FFF6F8', '背景'), ('#4A2A35', '文字')],
                 fonts='見出し：Kaisei Decol<br>本文：Zen角ゴシック New', shape='角丸18px・やわらかい影・花びらの散る背景・丸い「第1」・すみに桜の花',
                 pic='満開の桜・桜の花かざりの白い競走馬（馬らしい形の、ぺたっとした色の絵）・若草の丘・舞う花びら')),

 dict(id='sea', cat=2, name='海', desc='青・夏の海', title='海（紺×水色×白）', banner='sea', alt='波打ちぎわを走る鹿毛の競走馬（紺に白いしまのゼッケン1）と、青い海と空のイラスト',
      fonts=['Murecho:wght@500;700;800'],
      v=dict(bg='#EEF7FB', ink='#10324F', sub='#4A6A82', card='#FFFFFF', cardB='1.5px solid #CFE5F2', cardO='0 solid transparent', cardS='0 3px 0 #D3E8F4',
             radius='16px', rs='12px', font='"Murecho"', dfont='"Murecho"', dw='800', logo='#FFFFFF', logoS='0 2px 0 #0A2A4A',
             iii='#39C5DD', iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#0E3A66,#14558A)', hdInk='#FFFFFF', hdB='0 solid transparent',
             mBg='rgba(255,255,255,.12)', mLine='rgba(255,255,255,.55)', mInk='#FFFFFF', pill='rgba(255,255,255,.12)', pillLine='rgba(255,255,255,.35)', pillInk='#EAF6FF',
             coin='#FFD27A', coinInk='#0E3A66', badge='#E3F3FB', badgeInk='#0B5E96', badgeB='1.5px solid #BFE0F1', tagBg='#EEF7FB', tagInk='#1B5C86', tagLine='#BFE0F1',
             warnBg='#FFEBD6', warnInk='#A04A12', zBg='#F3F9FD', zB='1.5px solid #DCEEF8', znBg='#0E3A66', znInk='#FFFFFF', znB='0 solid transparent', znR='999px', znS='none',
             acc='#0B5E96', nR='8px', w2B='0 solid transparent', sep='1.5px dashed #CFE5F2', btn='#0B76B8', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='999px',
             btnS='0 3px 0 #08598C', btn2='#FFFFFF', btn2Ink='#0B6AA6', btn2B='1.5px solid #A9D3EC', tab='#FFFFFF', tabB='1px solid #CFE5F2', tabInk='#557089',
             tabOn='#E1F2FB', tabOnInk='#0B5E96', tabR='14px', sel='#0B76B8', selInk='#FFFFFF', h1='#0B5E96'),
      chk=dict(hd=['#0E3A66', '#14558A']),
      css=[('', 'background-image:' + tile_waves() + ';background-size:60px 24px'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-8px;height:9px;background:' + wave_edge() + ' 0 0/28px 9px repeat-x')],
      orn=orn_sea(),
      guide=dict(colors=[('#0E3A66', '紺'), ('#0B76B8', 'ボタン'), ('#39C5DD', '水色'), ('#EEF7FB', '背景'), ('#10324F', '文字')],
                 fonts='見出し：Murecho ExtraBold<br>本文：Murecho', shape='角丸16px・丸いボタン・上の帯のふちが波・うすい波の背景・すみに浮き輪',
                 pic='青空と入道雲・水色の海・砂浜・波打ちぎわを走る鹿毛の競走馬（馬らしい形の、ぺたっとした色の絵）・しぶき')),

 dict(id='sunset', cat=2, name='夕焼け', desc='紫とオレンジ', title='夕焼け（紫×オレンジ）', banner='sunset', alt='夕日を背に丘をかける馬のシルエット（風になびく細い毛のたてがみとしっぽ・夕日がわのふちの光）と、紫からオレンジの空のイラスト',
      fonts=['Kaisei+Opti:wght@700', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#FFF3EA', ink='#3A2340', sub='#7A5A6E', card='#FFFFFF', cardB='0 solid transparent', cardO='0 solid transparent', cardS='0 6px 18px rgba(120,50,90,.13)',
             radius='18px', rs='14px', font='"Zen Kaku Gothic New"', dfont='"Kaisei Opti"', dw='700', logo='#FFD9A8', logoS='none',
             iii='#FF9A5C', iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#24123A,#47226A)', hdInk='#FFE7D1', hdB='0 solid transparent',
             mBg='rgba(255,255,255,.08)', mLine='rgba(255,200,160,.6)', mInk='#FFE7D1', pill='rgba(255,255,255,.08)', pillLine='rgba(255,200,160,.35)', pillInk='#FFE7D1',
             coin='#FF9A5C', coinInk='#2A1640', badge='linear-gradient(180deg,#FFE3C8,#FFD3DC)', badgeInk='#6A2E8E', badgeB='0 solid transparent',
             tagBg='#FFF1E8', tagInk='#8A3A2A', tagLine='#F6D0BF', warnBg='#FFE0D6', warnInk='#A3301C', zBg='#FFF8F3', zB='1px solid #F8E0D3',
             znBg='#3A1D5C', znInk='#FFD9B8', znB='0 solid transparent', znR='4px', znS='none', acc='#6A2E8E', nR='8px', w2B='0 solid transparent',
             sep='1px solid #F6DCCF', btn='linear-gradient(90deg,#C8461F,#A8355E)', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='12px',
             btnS='0 4px 12px rgba(168,53,94,.28)', btn2='#FFFFFF', btn2Ink='#A8355E', btn2B='1.5px solid #F2C1B0', tab='#24123A', tabB='0 solid transparent',
             tabInk='#CDB5E0', tabOn='rgba(255,154,92,.16)', tabOnInk='#FFB98A', tabR='12px', sel='#C8461F', selInk='#FFFFFF', h1='#6A2E8E'),
      chk=dict(hd=['#24123A', '#47226A'], btn=['#C8461F', '#A8355E'], badge=['#FFE3C8', '#FFD3DC'], logo=['#FFE3A8', '#FF9A5C']),
      css=[('', 'background-image:linear-gradient(180deg,#FFF1E6,#FDE8EF)'),
           ('.logo', 'background:linear-gradient(180deg,#FFE3A8,#FF9A5C 70%,#F2706A);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,#FF9A5C,#F2706A,#B05BD0)'),
           ('.card::before', 'content:"";position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:0 0 3px 3px;background:linear-gradient(90deg,#FF9A5C,#C2416B,#6A2E8E)')],
      orn=orn_sunset(),
      guide=dict(colors=[('#47226A', '夕方の紫'), ('#C8461F', '夕日'), ('#FF9A5C', 'オレンジ'), ('#FFF3EA', '背景'), ('#3A2340', '文字')],
                 fonts='見出し：Kaisei Opti（夕日色の文字）<br>本文：Zen角ゴシック New', shape='角丸18px・枠なしの浮いたカード・カードの上に夕焼けの線・上下の帯は濃い紫',
                 pic='紫からオレンジの空・沈む太陽・丘をかける馬のシルエット（細い毛のたてがみとしっぽ・夕日がわのふちの光）・鳥')),

 dict(id='autumn', cat=2, name='紅葉', desc='赤と山吹・秋', title='紅葉（赤×山吹）', banner='autumn', alt='紅葉の林を歩く栗毛の競走馬（亜麻色のたてがみ・もみじの髪かざり・赤いゼッケン1）のイラスト',
      fonts=['Zen+Old+Mincho:wght@900', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#FBF3E6', ink='#3E2A1E', sub='#7A5E48', card='#FFFDF8', cardB='1.5px solid #EED8B8', cardO='0 solid transparent', cardS='0 3px 0 #EAD3B0',
             radius='12px', rs='10px', font='"Zen Kaku Gothic New"', dfont='"Zen Old Mincho"', dw='900', logo='#FFF1DE', logoS='0 2px 0 #6E2410',
             iii='#F2B33D', iiiB='0 solid transparent', iiiR='1px', hd='linear-gradient(180deg,#B3401E,#8E2E14)', hdInk='#FFF1DE', hdB='3px solid #E8A13A',
             mBg='rgba(0,0,0,.12)', mLine='rgba(255,230,200,.6)', mInk='#FFF1DE', pill='rgba(0,0,0,.14)', pillLine='rgba(255,230,200,.35)', pillInk='#FFF1DE',
             coin='#F2B33D', coinInk='#6E2410', badge='#FBE6D0', badgeInk='#A33A16', badgeB='1.5px solid #EBC59E', tagBg='#FBF0DF', tagInk='#7A3A1A', tagLine='#EED8B8',
             warnBg='#FFE2D2', warnInk='#9E2A10', zBg='#FDF7EE', zB='1.5px solid #F3E3CA', znBg='#8E2E14', znInk='#FFF1DE', znB='0 solid transparent', znR='3px',
             znS='0 2px 0 #5E1E0C', acc='#A33A16', nR='7px', w2B='0 solid transparent', sep='1.5px dashed #EED8B8', btn='#A33A16', btnInk='#FFF8EE',
             btnB='0 solid transparent', btnR='10px', btnS='0 3px 0 #74270C', btn2='#FFFDF8', btn2Ink='#A33A16', btn2B='1.5px solid #E2BE96', tab='#FFF8EC',
             tabB='2px solid #EED8B8', tabInk='#7A5E48', tabOn='#FBE3CC', tabOnInk='#A33A16', tabR='10px', sel='#A33A16', selInk='#FFF8EE', h1='#A33A16'),
      chk=dict(hd=['#B3401E', '#8E2E14']),
      css=[('', 'background-image:' + tile_leaves() + ';background-size:150px 150px')],
      orn=orn_autumn(),
      guide=dict(colors=[('#B3401E', '紅葉'), ('#E8A13A', '山吹'), ('#A33A16', 'ボタン'), ('#FBF3E6', '背景'), ('#3E2A1E', '文字')],
                 fonts='見出し：Zen Old Mincho Black<br>本文：Zen角ゴシック New', shape='角丸12px・生成りのカード・山吹の線・もみじの散る背景・すみにもみじ',
                 pic='もみじの木・前足を上げて歩く栗毛の競走馬（亜麻色のたてがみ・もみじの髪かざり・馬らしい形の、ぺたっとした色の絵）・秋の丘')),

 dict(id='snow', cat=2, name='雪', desc='紺と白・冬', title='雪（冬の紺×雪の白）', banner='snow', alt='雪の中で白い息をはいて立つ芦毛の競走馬（まだら模様・水色のマフラー・紺のゼッケン1）と、雪をかぶった木のイラスト',
      fonts=['Kiwi+Maru:wght@500', 'Zen+Maru+Gothic:wght@500;700'],
      v=dict(bg='#F2F7FB', ink='#1E3346', sub='#557089', card='#FFFFFF', cardB='1.5px solid #D6E5F2', cardO='0 solid transparent', cardS='0 3px 0 #DCE8F3',
             radius='16px', rs='12px', font='"Zen Maru Gothic"', dfont='"Kiwi Maru"', dw='500', logo='#FFFFFF', logoS='0 0 10px rgba(255,255,255,.35)',
             iii='#BFE3FF', iiiB='0 solid transparent', iiiR='3px',
             hd='radial-gradient(rgba(255,255,255,.55) 1px,transparent 1.7px) 0 0/22px 22px,radial-gradient(rgba(255,255,255,.35) 1px,transparent 1.6px) 11px 7px/22px 22px,linear-gradient(180deg,#24496E,#2F6390)',
             hdInk='#F2F8FF', hdB='0 solid transparent', mBg='rgba(255,255,255,.12)', mLine='rgba(255,255,255,.55)', mInk='#FFFFFF', pill='rgba(0,0,0,.16)',
             pillLine='rgba(255,255,255,.3)', pillInk='#EAF4FF', coin='#BFE3FF', coinInk='#1E3F5E', badge='#E6F1FA', badgeInk='#23608F', badgeB='1.5px solid #C9DDF0',
             tagBg='#EEF5FB', tagInk='#2A5378', tagLine='#CFE0EF', warnBg='#FFE9E4', warnInk='#A43A2A', zBg='#F5F9FD', zB='1.5px solid #E1ECF6', znBg='#2F6E9E',
             znInk='#FFFFFF', znB='0 solid transparent', znR='999px', znS='none', acc='#23608F', nR='8px', w2B='0 solid transparent', sep='1.5px dashed #D6E5F2',
             btn='#2F6E9E', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='14px', btnS='0 3px 0 #1F5077', btn2='#FFFFFF', btn2Ink='#2F6E9E', btn2B='1.5px solid #B9D3EA',
             tab='#FFFFFF', tabB='1px solid #D6E5F2', tabInk='#557089', tabOn='#E3F0FA', tabOnInk='#23608F', tabR='14px', sel='#2F6E9E', selInk='#FFFFFF', h1='#23608F'),
      chk=dict(hd=['#24496E', '#2F6390']),
      css=[('', 'background-image:radial-gradient(#FFFFFF 2px,transparent 2.6px),radial-gradient(#DCE8F3 1.4px,transparent 2px);background-size:26px 26px,26px 26px;background-position:0 0,13px 13px'),
           ('.card::before', 'content:"";position:absolute;left:12px;right:12px;top:-7px;height:12px;background:radial-gradient(circle at 8px 12px,#FFFFFF 7.6px,transparent 8.2px) 0 0/16px 12px repeat-x;filter:drop-shadow(0 -1px 0 #C9DCEC)')],
      orn=orn_snow(),
      guide=dict(colors=[('#24496E', '冬の紺'), ('#2F6E9E', 'ボタン'), ('#BFE3FF', '氷'), ('#F2F7FB', '背景'), ('#1E3346', '文字')],
                 fonts='見出し：Kiwi Maru<br>本文：Zen Maru Gothic', shape='角丸16px・カードの上に積もった雪・雪の水玉の背景・帯に舞う雪・すみに雪の結晶',
                 pic='雪の原っぱ・雪をかぶった木・水色のマフラーの芦毛の競走馬（馬らしい形の、ぺたっとした色の絵）・白い息・降る雪')),

 dict(id='newyear', cat=2, name='午年', desc='赤と金・お正月', title='午年・お正月（赤×金）', banner='newyear', alt='赤い青海波の背景に富士山と初日の出、前足を上げる白い競走馬（金のたてがみ・赤い頭のベルト・首に紅白の綱と金の鈴・ゼッケン1）のイラスト',
      fonts=['Yuji+Syuku', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#FBF4E8', ink='#3A1A12', sub='#7A4E3A', card='#FFFDF8', cardB='1.5px solid #E2BE6A', cardO='1px solid #F1DFB2', cardS='0 3px 0 #EBD7A8',
             radius='10px', rs='8px', font='"Zen Kaku Gothic New"', dfont='"Yuji Syuku"', dw='400', logo='#F5D27A', logoS='0 2px 0 #7A0A0E',
             iii='#E8B33A', iiiB='0 solid transparent', iiiR='1px', hd=tile_seigaiha('#C8161D', 'rgba(245,210,122,.2)') + ' 0 0/40px 20px,#C8161D',
             hdInk='#FFF3D6', hdB='3px solid #E8B33A', mBg='rgba(0,0,0,.14)', mLine='#E8B33A', mInk='#FFF3D6', pill='rgba(0,0,0,.2)', pillLine='rgba(245,210,122,.55)',
             pillInk='#FFF3D6', coin='#E8B33A', coinInk='#7A0A0E', badge='#C8161D', badgeInk='#FFE6A3', badgeB='0 solid transparent', tagBg='#FFF5E1', tagInk='#8A4A10',
             tagLine='#EBCF8E', warnBg='#FFE1DC', warnInk='#A3121A', zBg='#FFF9EE', zB='1px solid #F1DFB2', znBg='#C8161D', znInk='#FFF3D6', znB='0 solid transparent',
             znR='2px', znS='0 2px 0 #8A0E12', acc='#B0141B', nR='6px', w2B='0 solid transparent', sep='1px solid #EBD7A8', btn='#C8161D', btnInk='#FFF3D6',
             btnB='0 solid transparent', btnR='8px', btnS='0 3px 0 #8A0E12', btn2='#FFFDF8', btn2Ink='#B0141B', btn2B='1.5px solid #E2BE6A', tab='#A80F16',
             tabB='2px solid #E8B33A', tabInk='#F6D9A8', tabOn='rgba(255,230,163,.16)', tabOnInk='#FFE6A3', tabR='8px', sel='#C8161D', selInk='#FFF3D6', h1='#B0141B'),
      chk=dict(hd=['#C8161D']),
      css=[('.lb', 'box-shadow:inset 0 0 0 3px #C8161D,inset 0 0 0 4.5px #E8B33A')],
      orn=orn_newyear(),
      guide=dict(colors=[('#C8161D', '朱赤'), ('#E8B33A', '金'), ('#FFE6A3', '薄い金'), ('#FBF4E8', '背景'), ('#3A1A12', '文字')],
                 fonts='見出し：Yuji Syuku（筆の字）<br>本文：Zen角ゴシック New', shape='角丸10px・金の二重枠・帯に青海波・赤い札・すみに梅の花',
                 pic='赤い青海波・初日の出と富士山・金の雲・紅白の綱と金の鈴の白い競走馬（馬らしい形の、ぺたっとした色の絵）・「午」の印')),

 dict(id='fireworks', cat=2, name='花火', desc='夜空・夏祭り', title='花火（夜空×ピンク・黄）', banner='fireworks', alt='夜空に上がる花火と、金とピンクの光の線でえがいた、かける馬（しっぽはしだれ柳の花火）、ちょうちんのイラスト',
      fonts=['Potta+One', 'M+PLUS+1p:wght@500;700'],
      v=dict(bg='#11183A', ink='#F2F4FF', sub='#AEB6D9', card='#18214A', cardB='1px solid #2E3A72', cardO='0 solid transparent', cardS='0 8px 22px rgba(0,0,0,.35)',
             radius='18px', rs='12px', font='"M PLUS 1p"', dfont='"Potta One"', dw='400', logo='#FFD45E', logoS='none',
             iii='#FFD45E', iiiB='0 solid transparent', iiiR='3px', hd='#0B1029', hdInk='#F2F4FF', hdB='0 solid transparent',
             mBg='rgba(255,255,255,.06)', mLine='#FF6B9A', mInk='#FFE3EC', pill='rgba(255,255,255,.06)', pillLine='rgba(255,255,255,.18)', pillInk='#E6E9FF',
             coin='#FFD45E', coinInk='#1A1030', badge='#222C5E', badgeInk='#FFD45E', badgeB='1.5px solid #FFD45E', tagBg='rgba(255,255,255,.06)', tagInk='#DDE2FF',
             tagLine='#3A4680', warnBg='rgba(255,107,154,.18)', warnInk='#FF9DBD', zBg='rgba(255,255,255,.04)', zB='1px solid #2E3A72',
             znBg='linear-gradient(90deg,#FF6B9A,#FFD45E)', znInk='#1A1030', znB='0 solid transparent', znR='999px', znS='none', acc='#FFD45E', nR='8px',
             w2B='1.5px solid #8A93BF', sep='1px dashed #3A4680', btn='#FF5C8A', btnInk='#1A1030', btnB='0 solid transparent', btnR='999px',
             btnS='0 0 16px rgba(255,92,138,.45)', btn2='transparent', btn2Ink='#FFD45E', btn2B='1.5px solid #FFD45E', tab='#0B1029', tabB='1px solid #2E3A72',
             tabInk='#8E97C4', tabOn='rgba(255,212,94,.12)', tabOnInk='#FFD45E', tabR='14px', sel='#FF5C8A', selInk='#1A1030', h1='#FFD45E'),
      chk=dict(hd=['#0B1029'], zn=['#FF6B9A', '#FFD45E'], logo=['#FF6B9A', '#FFD45E']),
      css=[('', 'background-image:radial-gradient(rgba(255,255,255,.10) 1px,transparent 1.5px),radial-gradient(rgba(255,212,94,.09) 1px,transparent 1.5px);background-size:34px 34px,52px 52px;background-position:0 0,17px 9px'),
           ('.logo', 'background:linear-gradient(90deg,#FF6B9A,#FFD45E);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-13px;height:15px;background:' + lanterns() + ' 0 0/60px 15px repeat-x'),
           ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(255,107,154,.12),transparent 45%)')],
      orn=orn_fireworks(),
      guide=dict(colors=[('#0B1029', '夜空'), ('#FF5C8A', '花火ピンク'), ('#FFD45E', '花火の黄'), ('#18214A', 'カード'), ('#F2F4FF', '文字')],
                 fonts='見出し：Potta One（ピンク→黄の文字）<br>本文：M PLUS 1p', shape='角丸18px・暗いカード・光るボタン・帯の下にちょうちん・すみに花火',
                 pic='夜空の花火・金とピンクの光の線でえがいた、かける馬（たてがみとしっぽは しだれ柳の花火）・ちょうちんの列')),

 dict(id='night', cat=3, name='ナイター', desc='夜のレース場', title='ナイター（夜×照明のアンバー）', banner='nightrace', alt='照明に照らされた夜のコースを走る3頭の馬と騎手のアニメ風イラスト',
      fonts=['RocknRoll+One', 'M+PLUS+1p:wght@500;700'],
      v=dict(bg='#0E1324', ink='#F1F3F9', sub='#A3ACC6', card='#161C33', cardB='1px solid #2A3352', cardO='0 solid transparent', cardS='0 8px 24px rgba(0,0,0,.4)',
             radius='12px', rs='8px', font='"M PLUS 1p"', dfont='"RocknRoll One"', dw='400', logo='#FFFFFF', logoS='0 0 12px rgba(255,255,255,.45)',
             iii='#FFB020', iiiB='0 solid transparent', iiiR='1px', hd='#070A16', hdInk='#F1F3F9', hdB='2px solid #FFB020',
             mBg='rgba(255,255,255,.05)', mLine='rgba(255,255,255,.4)', mInk='#F1F3F9', pill='rgba(255,255,255,.05)', pillLine='rgba(255,255,255,.2)', pillInk='#E3E7F2',
             coin='#FFB020', coinInk='#1A1205', badge='#1E2645', badgeInk='#FFFFFF', badgeB='1.5px solid #FFB020', tagBg='rgba(255,255,255,.05)', tagInk='#D9DEEC',
             tagLine='#2F3858', warnBg='rgba(255,176,32,.14)', warnInk='#FFC86B', zBg='rgba(255,255,255,.03)', zB='1px solid #2A3352', znBg='#FFB020', znInk='#1A1205',
             znB='0 solid transparent', znR='3px', znS='none', acc='#FFC24D', nR='6px', w2B='1.5px solid #8790AE', sep='1px solid #2A3352', btn='#FFB020',
             btnInk='#1A1205', btnB='0 solid transparent', btnR='8px', btnS='0 0 18px rgba(255,176,32,.35)', btn2='transparent', btn2Ink='#F1F3F9',
             btn2B='1.5px solid #46507A', tab='#070A16', tabB='1px solid #20283F', tabInk='#8790AE', tabOn='rgba(255,176,32,.12)', tabOnInk='#FFC24D', tabR='10px',
             sel='#FFB020', selInk='#1A1205', h1='#FFFFFF'),
      chk=dict(hd=['#070A16']),
      css=[('', 'background-image:radial-gradient(ellipse 62% 30% at 12% 0%,rgba(255,255,255,.08),transparent 70%),radial-gradient(ellipse 62% 30% at 88% 0%,rgba(255,255,255,.08),transparent 70%),linear-gradient(180deg,#0E1324,#121A30)'),
           ('.card::before', 'content:"";position:absolute;left:-1px;top:16px;bottom:16px;width:3px;background:#FFB020;border-radius:0 3px 3px 0;box-shadow:0 0 8px rgba(255,176,32,.6)'),
           ('.vt', 'letter-spacing:.02em')],
      orn=orn_night(),
      guide=dict(colors=[('#070A16', '夜'), ('#FFB020', '照明のアンバー'), ('#161C33', 'カード'), ('#8790AE', 'グレー'), ('#F1F3F9', '文字')],
                 fonts='見出し：RocknRoll One<br>本文：M PLUS 1p', shape='角丸12px・暗いカード・カードの左にアンバーの線・照明の光の背景・すみに照明',
                 pic='夜のコース・照明・走る3頭の馬と騎手・白いラチ')),

 dict(id='news', cat=3, name='競馬新聞', desc='新聞紙・黒と赤', title='競馬新聞（新聞紙×黒・赤）', banner='newspaper', alt='競馬新聞の紙面のような、題字と馬柱、墨の筆でえがいた馬のイラスト',
      fonts=['Kaisei+Tokumin:wght@800', 'BIZ+UDPMincho:wght@400;700'],
      v=dict(bg='#F2EEE3', ink='#141414', sub='#4E4A40', card='#FBF9F3', cardB='1.5px solid #141414', cardO='0 solid transparent', cardS='none',
             radius='0', rs='0', font='"BIZ UDPMincho"', dfont='"Kaisei Tokumin"', dw='800', logo='#F2EEE3', logoS='none',
             iii='#C81E1E', iiiB='0 solid transparent', iiiR='0', hd='#F2EEE3', hdInk='#141414', hdB='5px double #141414',
             mBg='transparent', mLine='#141414', mInk='#141414', pill='transparent', pillLine='#141414', pillInk='#141414', coin='#C81E1E', coinInk='#FFFFFF',
             badge='#FBF9F3', badgeInk='#C81E1E', badgeB='0 solid transparent', tagBg='transparent', tagInk='#141414', tagLine='#141414', warnBg='#C81E1E',
             warnInk='#FFFFFF', zBg='#FBF9F3', zB='1px solid #141414', znBg='#141414', znInk='#F2EEE3', znB='0 solid transparent', znR='0', znS='none',
             acc='#141414', nR='2px', w2B='0 solid transparent', sep='1px solid #141414', btn='#C81E1E', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='0',
             btnS='none', btn2='transparent', btn2Ink='#141414', btn2B='1.5px solid #141414', tab='#F2EEE3', tabB='5px double #141414', tabInk='#3A372F',
             tabOn='#141414', tabOnInk='#F2EEE3', tabR='0', sel='#141414', selInk='#F2EEE3', h1='#141414'),
      chk=dict(hd=['#F2EEE3'], logo=['#F2EEE3'], logoBg=['#141414'], pill=['#F2EEE3'], btn2=['#FBF9F3'], tagBg=['#FBF9F3']),
      css=[('', 'background-image:radial-gradient(rgba(20,20,20,.055) .8px,transparent 1.2px);background-size:5px 5px'),
           ('.logo', 'background:#141414;padding:6px 10px 7px;letter-spacing:.06em'),
           (SEG_SQ, ''),
           ('.seg.on', 'background:#141414;color:#F2EEE3'),
           ('.ch', 'color:#141414;border-bottom:2px solid #141414;padding-bottom:5px'),
           ('.lb', 'border-radius:50%;box-shadow:inset 0 0 0 2px #C81E1E,inset 0 0 0 5px #FBF9F3,inset 0 0 0 7px #C81E1E'),
           ('.tb button', 'font-weight:700')],
      orn=orn_news(),
      guide=dict(colors=[('#F2EEE3', '新聞紙'), ('#141414', '黒'), ('#C81E1E', '赤'), ('#FBF9F3', 'カード'), ('#4E4A40', '小さい文字')],
                 fonts='見出し：Kaisei Tokumin（太い明朝）<br>本文：BIZ UDP明朝', shape='角なし（四角）・黒い罫線・二重線の帯・黒地の題字・Aは二重丸・すみに赤い◎',
                 pic='新聞の題字「テンゲル競馬」・馬柱・墨の筆でえがいた馬')),

 dict(id='silks', cat=3, name='勝負服', desc='青・赤・黄・緑', title='勝負服（青・赤・黄・緑）', banner='silks', alt='勝負服の柄（市松・縦じま・星・輪）のコマ割りを背に、首と足をいっぱいにのばして走る栗毛の馬（にらむ目・歯をくいしばった口・鼻息）と、ひし形の勝負服の騎手（ゴーグル・とぶ汗）の漫画風イラスト',
      fonts=['M+PLUS+1:wght@500;700;900'],
      v=dict(bg='#F4F6FB', ink='#121A33', sub='#4A5578', card='#FFFFFF', cardB='2px solid #1A3FB8', cardO='0 solid transparent', cardS='4px 4px 0 #FFC400',
             radius='14px', rs='10px', font='"M PLUS 1"', dfont='"M PLUS 1"', dw='900', logo='#FFFFFF', logoS='2px 2px 0 #E02424',
             iii='#FFC400', iiiB='0 solid transparent', iiiR='1px', hd='#1A3FB8', hdInk='#FFFFFF', hdB='0 solid transparent',
             mBg='rgba(255,255,255,.12)', mLine='rgba(255,255,255,.7)', mInk='#FFFFFF', pill='rgba(0,0,0,.18)', pillLine='rgba(255,255,255,.3)', pillInk='#FFFFFF',
             coin='#FFC400', coinInk='#121A33', badge='#FFC400', badgeInk='#121A33', badgeB='2px solid #121A33', tagBg='#EEF2FF', tagInk='#1A3FB8', tagLine='#C3CFF3',
             warnBg='#FFF1C2', warnInk='#8A5A00', zBg='#F6F8FF', zB='1.5px solid #DCE3FA', znBg='#E02424', znInk='#FFFFFF', znB='0 solid transparent', znR='4px',
             znS='none', acc='#1A3FB8', nR='7px', w2B='0 solid transparent', sep='2px dotted #C3CFF3', btn='#1A3FB8', btnInk='#FFFFFF', btnB='0 solid transparent',
             btnR='10px', btnS='0 3px 0 #0F2A80', btn2='#FFFFFF', btn2Ink='#1A3FB8', btn2B='2px solid #1A3FB8', tab='#FFFFFF', tabB='3px solid #1A3FB8', tabInk='#4A5578',
             tabOn='#1A3FB8', tabOnInk='#FFFFFF', tabR='10px', sel='#E02424', selInk='#FFFFFF', h1='#1A3FB8'),
      chk=dict(hd=['#1A3FB8']),
      css=[('', 'background-image:repeating-linear-gradient(-55deg,rgba(26,63,184,.035) 0 14px,transparent 14px 28px)'),
           ('.hd', 'padding-bottom:19px'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:0;height:7px;background:repeating-linear-gradient(-55deg,#E02424 0 10px,#FFFFFF 10px 14px,#FFC400 14px 24px,#FFFFFF 24px 28px,#0F9D58 28px 38px,#FFFFFF 38px 42px)'),
           ('.zn', 'transform:skewX(-12deg)'),
           ('.card + .card', 'box-shadow:4px 4px 0 #E02424')],
      orn=orn_silks(),
      guide=dict(colors=[('#1A3FB8', '青'), ('#E02424', '赤'), ('#FFC400', '黄'), ('#0F9D58', '緑'), ('#121A33', '文字')],
                 fonts='見出し：M PLUS 1 Black<br>本文：M PLUS 1', shape='角丸14px・青い太枠に黄・赤のずらした影・帯の下に勝負服のしま・ななめの「第1」・すみに勝負服',
                 pic='勝負服の柄のコマ割り（市松・縦じま・星・輪）・青いコマに流線・遊び心のある漫画の馬（のびた走り・にらむ目・歯・鼻息）とひし形の勝負服の騎手（ゴーグル・汗・ゼッケン1）')),

 dict(id='lucky', cat=3, name='開運', desc='白と赤・招き馬', title='開運・招き馬（白×赤×金）', banner='lucky',
      alt='銀の蹄鉄の中で、右の前足をあげて福を招き、千両の小判をだいた白い招き馬（正面の顔・つり目の金色の目・赤い首輪と金の鈴）と、金貨・桜・四つ葉のアニメ風イラスト',
      fonts=['Zen+Antique+Soft', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#FFFCF6', ink='#2A1A16', sub='#6B4E44', card='#FFFFFF', cardB='1.5px solid #E6C66F', cardO='0 solid transparent', cardS='0 3px 0 #F2E2BE',
             radius='16px', rs='12px', font='"Zen Kaku Gothic New"', dfont='"Zen Antique Soft"', dw='400', logo='#C62828', logoS='none',
             iii='linear-gradient(180deg,#FFF1B8,#E9C25A 45%,#B8861F 55%,#F7E08A)', iiiB='1px solid #8A6514', iiiR='1.5px',
             hd='linear-gradient(180deg,#FFFFFF,#FFF7EA)', hdInk='#2A1A16', hdB='0 solid transparent', mBg='#FFFFFF', mLine='#D9302C', mInk='#B71C1C',
             pill='#FFF6E8', pillLine='#E6C66F', pillInk='#5A3A10', coin='linear-gradient(135deg,#FFF1B8,#C9952B)', coinInk='#2A1E05',
             badge='#D32F2F', badgeInk='#FFFFFF', badgeB='0 solid transparent', tagBg='#FFF1EF', tagInk='#A51D22', tagLine='#F2C2BC', warnBg='#FFF1D0', warnInk='#8A5A00',
             zBg='#FFFDF9', zB='1.5px solid #F1DFBC', znBg='#D32F2F', znInk='#FFFFFF', znB='0 solid transparent', znR='999px', znS='none', acc='#B71C1C', nR='8px',
             w2B='0 solid transparent', sep='1.5px dashed #EDD6B0', btn='linear-gradient(180deg,#D63A33,#BE2525)', btnInk='#FFFFFF', btnB='0 solid transparent',
             btnR='12px', btnS='0 3px 0 #8E1B1B', btn2='#FFFFFF', btn2Ink='#B71C1C', btn2B='1.5px solid #EBA9A3', tab='linear-gradient(180deg,#FFFFFF,#FFF7EA)',
             tabB='0 solid transparent', tabInk='#765549', tabOn='#FDE6E3', tabOnInk='#B71C1C', tabR='12px', sel='#C62828', selInk='#FFFFFF', h1='#B71C1C'),
      chk=dict(hd=['#FFFFFF', '#FFF7EA'], btn=['#D63A33', '#BE2525'], tab=['#FFFFFF', '#FFF7EA'], logo=['#C62828', '#C62828']),
      css=[('', 'background-image:' + tile_lucky() + ';background-size:120px 120px'),
           ('.logo', 'color:#C62828;filter:drop-shadow(0 1.5px 0 #F3D27A)'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:0;height:5px;background:linear-gradient(180deg,#E6C66F 0 2px,#D32F2F 2px 5px)'),
           ('.tb', 'box-shadow:inset 0 3px 0 #D32F2F,inset 0 5px 0 #E6C66F')],
      orn=orn_lucky(),
      guide=dict(colors=[('#FFFFFF', '白'), ('#D32F2F', '赤'), ('#D4A63A', '金'), ('#B9C4D1', '銀'), ('#FFFCF6', '背景'), ('#2A1A16', '文字')],
                 fonts='見出し：Zen Antique Soft（赤い文字）<br>本文：Zen角ゴシック New', shape='角丸16px・金の枠・赤いボタン・白地に小さな桜と小判・上下の帯は白に赤と金の線・すみに小判',
                 pic='銀の蹄鉄（つま先のでっぱり・溝・くぎ穴・くぎ）・中に大きな白い招き馬（招き猫ふう：正面の顔・丸みのあるつり目の金色の目（横長のひとみ）・赤い耳・目の上の赤いかざり・赤い首輪に金の鈴・千両の小判・体の横から招く右前足）・金貨・桜・四つ葉・キラキラ（アニメ風）')),

 dict(id='ink', cat=4, name='水墨画', desc='和紙と墨', title='水墨画（和紙×墨・朱）', banner='ink', alt='和紙に墨の線と灰色のぼかしでえがいた、騎手を乗せて競り合う2頭の競走馬と、朱色の落款のイラスト',
      fonts=['Yuji+Mai', 'Zen+Old+Mincho:wght@600;700'],
      v=dict(bg='#F6F3EC', ink='#1A1A1A', sub='#5E5A52', card='#FBFAF6', cardB='1px solid rgba(26,26,26,.2)', cardO='0 solid transparent', cardS='none',
             radius='3px', rs='2px', font='"Zen Old Mincho"', dfont='"Yuji Mai"', dw='400', logo='#1A1A1A', logoS='none',
             iii='#1A1A1A', iiiB='0 solid transparent', iiiR='2px', hd='#F6F3EC', hdInk='#1A1A1A', hdB='0 solid transparent',
             mBg='transparent', mLine='#1A1A1A', mInk='#1A1A1A', pill='transparent', pillLine='rgba(0,0,0,.35)', pillInk='#2A2A2A', coin='#B7282E', coinInk='#FFFFFF',
             badge='transparent', badgeInk='#1A1A1A', badgeB='0 solid transparent', tagBg='transparent', tagInk='#2A2A2A', tagLine='rgba(0,0,0,.28)', warnBg='#B7282E',
             warnInk='#FFFFFF', zBg='transparent', zB='1px solid rgba(26,26,26,.14)', znBg='#B7282E', znInk='#FFFFFF', znB='0 solid transparent', znR='2px', znS='none',
             acc='#1A1A1A', nR='4px', w2B='0 solid transparent', sep='1px solid rgba(0,0,0,.15)', btn='#1A1A1A', btnInk='#F6F3EC', btnB='0 solid transparent',
             btnR='2px', btnS='none', btn2='transparent', btn2Ink='#1A1A1A', btn2B='1px solid #1A1A1A', tab='#F6F3EC', tabB='1px solid rgba(0,0,0,.2)',
             tabInk='#5E5A52', tabOn='#1A1A1A', tabOnInk='#F6F3EC', tabR='2px', sel='#1A1A1A', selInk='#F6F3EC', h1='#1A1A1A'),
      chk=dict(hd=['#F6F3EC'], pill=['#F6F3EC'], mBg=['#F6F3EC'], badge=['#FBFAF6'], tagBg=['#FBFAF6'], zBg=['#FBFAF6'], btn2=['#FBFAF6']),
      css=[('', 'background-image:' + washi_full() + ';background-size:390px 900px;background-repeat:no-repeat'),
           ('.hd::after', 'content:"";position:absolute;left:8px;right:8px;bottom:-2px;height:8px;background:' + brush_line() + ' 0 0/100% 100% no-repeat'),
           ('.logo', 'letter-spacing:.04em;font-size:28px'),
           ('.lb', 'background:' + enso_uri() + ' 50% 46%/64px 64px no-repeat')],
      orn=orn_ink(),
      guide=dict(colors=[('#F6F3EC', '和紙'), ('#1A1A1A', '墨'), ('#B7282E', '朱（落款）'), ('#5E5A52', '薄墨'), ('#FBFAF6', 'カード')],
                 fonts='見出し：Yuji Mai（筆の字）<br>本文：Zen Old Mincho', shape='角丸3px・細い墨の線・帯の下に筆の線・朱色の「第1」・Aは円相・すみに円相と落款',
                 pic='和紙・墨の線とぼかしでえがいた、騎手を乗せて競り合う2頭（手前は濃い墨・奥はうすい墨）・かすれ・朱色の「馬」の落款')),

 dict(id='marble', cat=4, name='大理石', desc='白と金・彫刻', title='大理石（白×金）', banner='marble', alt='金の帯の台の上の岩で、後ろ足で立ち上がる白い大理石の馬の像（波打つたてがみ・台までとどくしっぽ）と月桂樹のイラスト',
      fonts=['Shippori+Mincho+B1:wght@800', 'Shippori+Mincho:wght@500;700'],
      v=dict(bg='#F7F5F2', ink='#2B2620', sub='#6E665A', card='#FFFFFF', cardB='1px solid #D9D2C5', cardO='1px solid #EEE8DC', cardS='0 10px 30px rgba(80,60,30,.08)',
             radius='2px', rs='2px', font='"Shippori Mincho"', dfont='"Shippori Mincho B1"', dw='800', logo='#3A332A', logoS='none',
             iii='#B8935A', iiiB='0 solid transparent', iiiR='0', hd='#FBFAF7', hdInk='#2B2620', hdB='1px solid #B8935A',
             mBg='#FFFFFF', mLine='#B8935A', mInk='#4A4236', pill='#FFFFFF', pillLine='#D9D2C5', pillInk='#4A4236', coin='linear-gradient(135deg,#F3E2B8,#B8935A)',
             coinInk='#2B2620', badge='#FBF9F5', badgeInk='#6E5428', badgeB='1px solid #B8935A', tagBg='#FBF9F5', tagInk='#4A4236', tagLine='#E2DACB', warnBg='#F6E9E2',
             warnInk='#8A3A22', zBg='#FCFBF8', zB='1px solid #EEE8DC', znBg='transparent', znInk='#8A6A38', znB='1px solid #B8935A', znR='0', znS='none',
             acc='#6E5428', nR='3px', w2B='0 solid transparent', sep='1px solid #EEE8DC', btn='#2B2620', btnInk='#F0DDB0', btnB='0 solid transparent', btnR='2px',
             btnS='none', btn2='#FFFFFF', btn2Ink='#2B2620', btn2B='1px solid #B8935A', tab='#FBFAF7', tabB='1px solid #D9D2C5', tabInk='#6E665A', tabOn='#F1EBDF',
             tabOnInk='#2B2620', tabR='2px', sel='#2B2620', selInk='#F0DDB0', h1='#2B2620'),
      chk=dict(hd=['#FBFAF7'], zn=['#FCFBF8']),
      css=[('', 'background-image:' + marble_full() + ';background-size:390px 900px;background-repeat:no-repeat'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-5px;height:1px;background:#D9C39A'),
           ('.logo', 'letter-spacing:.08em;font-size:25px'),
           ('.mbtn,.pill,.seg,.tag', 'border-radius:2px'),
           ('.vt,.zf', 'letter-spacing:.03em')],
      orn=orn_marble(),
      guide=dict(colors=[('#F7F5F2', '大理石'), ('#B8935A', '金'), ('#2B2620', '黒（ボタン）'), ('#F0DDB0', '薄い金'), ('#6E665A', '小さい文字')],
                 fonts='見出し：Shippori Mincho B1 ExtraBold<br>本文：しっぽり明朝', shape='角丸2px・細い二重の枠・金の細い線・大理石のすじの背景・黒いボタンに金の字・すみに月桂樹',
                 pic='大理石の像（後ろ足で立ち上がる馬・波打つたてがみ・ねじれながら台までとどくしっぽ・岩の台座）・金の帯の台・金の月桂樹')),

 dict(id='ryuma', cat=4, name='龍馬', desc='墨黒と金・双龍', title='龍馬（墨黒×金）', banner='ryuma',
      alt='金の双龍の額縁（左右の上すみで向かい合う口を開けた龍の頭・うろこの体が左右のふちを下へうねり・前足の爪が下の横木をつかむ・上下のまん中に赤い玉の飾り）の中に、雷雲の夜空と金の日輪・雷・金の線の瑞雲のアニメ調イラスト',
      fonts=['Shippori+Antique+B1', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#0B0D14', ink='#F3E9D2', sub='#B9AD92', card='#141827', cardB='1px solid #8A6A2A', cardO='1px solid rgba(201,149,43,.28)', cardS='0 10px 30px rgba(0,0,0,.45)',
             radius='6px', rs='4px', font='"Zen Kaku Gothic New"', dfont='"Shippori Antique B1"', dw='400', logo='#F2C94F', logoS='0 0 12px rgba(242,201,79,.45)',
             iii='#F2C94F', iiiB='0 solid transparent', iiiR='1px', hd='linear-gradient(180deg,#0E1120,#151B2F)', hdInk='#F3E9D2', hdB='2px solid #C9952B',
             mBg='rgba(242,201,79,.08)', mLine='#C9952B', mInk='#F2C94F', pill='rgba(255,255,255,.05)', pillLine='rgba(201,149,43,.5)', pillInk='#F3E9D2', coin='#F2C94F',
             coinInk='#1A1408', badge='#1B2033', badgeInk='#F2C94F', badgeB='1.5px solid #C9952B', tagBg='rgba(201,149,43,.10)', tagInk='#F0DDA8', tagLine='#6E5428',
             warnBg='rgba(214,60,40,.22)', warnInk='#FFB4A0', zBg='rgba(255,255,255,.03)', zB='1px solid #3A3350', znBg='#C9952B', znInk='#1A1408',
             znB='0 solid transparent', znR='2px', znS='none', acc='#F2C94F', nR='4px', w2B='1.5px solid #8C8C9A', sep='1px solid #3A3350', btn='#C9952B',
             btnInk='#1A1408', btnB='0 solid transparent', btnR='4px', btnS='0 0 14px rgba(201,149,43,.35)', btn2='transparent', btn2Ink='#F2C94F',
             btn2B='1px solid #C9952B', tab='#0B0D14', tabB='1px solid #2A2A3A', tabInk='#A39A86', tabOn='rgba(242,201,79,.14)', tabOnInk='#F2C94F', tabR='4px',
             sel='#C9952B', selInk='#1A1408', h1='#F2C94F', pageInk='#F3E9D2', pageSub='#B9AD92', pageAcc='#F2C94F'),
      chk=dict(hd=['#0E1120', '#151B2F']),
      css=[('', 'background-image:' + tile_scales() + ',radial-gradient(ellipse at 50% 18%,rgba(201,149,43,.16),transparent 60%);background-size:40px 40px,100% 100%'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-6px;height:1px;background:rgba(201,149,43,.5)'),
           ('.logo', 'letter-spacing:.06em;font-size:27px'),
           ('.lb', 'box-shadow:inset 0 0 0 3px #141827,inset 0 0 0 4px rgba(201,149,43,.6)'),
           ('.lb b', 'text-shadow:0 0 10px rgba(242,201,79,.5)'),
           ('.zf', 'text-shadow:0 0 8px rgba(242,201,79,.35)'),
           ('.mbtn,.pill,.seg,.tag', 'border-radius:3px')],
      orn=orn_ryuma(),
      guide=dict(colors=[('#0B0D14', '墨黒'), ('#C9952B', '金'), ('#F2C94F', '明るい金'), ('#141827', 'カード'), ('#E0362C', '赤い玉')],
                 fonts='見出し：Shippori Antique B1<br>本文：Zen角ゴシック New', shape='角丸6px・金の細い枠（二重）・帯の下に金の線・金の「第1」と金のボタン・うろこの背景・すみに瑞雲と赤い玉',
                 pic='金の双龍の額縁（アニメ調：向かい合う龍の頭・うろこの体・爪が横木をつかむ・上下に赤い玉の飾り）・まん中は雷雲の夜空と金の日輪・雷・金の線の瑞雲')),

 dict(id='neon', cat=5, name='ネオン', desc='光る線・80年代', title='ネオン（黒×ピンク・水色）', banner='neon', alt='紫の夜空と光る格子、しま模様の太陽の前を、騎手を乗せて走ってくる光る線の競走馬のイラスト',
      fonts=['Rampart+One', 'Zen+Kaku+Gothic+New:wght@500;700'],
      v=dict(bg='#0A0718', ink='#F4F0FF', sub='#B9AEDD', card='#120C2A', cardB='1.5px solid #00F0FF', cardO='0 solid transparent',
             cardS='0 0 0 1px rgba(0,240,255,.2),0 0 18px rgba(0,240,255,.35)', radius='14px', rs='10px', font='"Zen Kaku Gothic New"', dfont='"Rampart One"', dw='400',
             logo='#CFFBFF', logoS='0 0 4px #00F0FF,0 0 12px #00F0FF,0 0 24px rgba(0,240,255,.6)', iii='#FF2BD6', iiiB='0 solid transparent', iiiR='3px',
             hd='#07051A', hdInk='#F4F0FF', hdB='2px solid #FF2BD6', mBg='transparent', mLine='#FF2BD6', mInk='#FFD6F6', pill='rgba(255,255,255,.04)',
             pillLine='rgba(0,240,255,.4)', pillInk='#DFFBFF', coin='#FF2BD6', coinInk='#1A0820', badge='transparent', badgeInk='#FF6BE4', badgeB='1.5px solid #FF2BD6',
             tagBg='rgba(0,240,255,.06)', tagInk='#BFFAFF', tagLine='rgba(0,240,255,.4)', warnBg='rgba(255,43,214,.16)', warnInk='#FF9BEA', zBg='rgba(255,255,255,.03)',
             zB='1px solid rgba(0,240,255,.25)', znBg='#FF2BD6', znInk='#1A0820', znB='0 solid transparent', znR='999px', znS='0 0 10px rgba(255,43,214,.6)',
             acc='#00F0FF', nR='8px', w2B='1.5px solid #9C90C8', sep='1px dashed rgba(0,240,255,.35)', btn='#00F0FF', btnInk='#07051A', btnB='0 solid transparent',
             btnR='999px', btnS='0 0 16px rgba(0,240,255,.55)', btn2='transparent', btn2Ink='#FF7BE6', btn2B='1.5px solid #FF2BD6', tab='#07051A',
             tabB='1px solid rgba(255,43,214,.5)', tabInk='#9C90C8', tabOn='rgba(0,240,255,.1)', tabOnInk='#7FF7FF', tabR='12px', sel='#00F0FF', selInk='#07051A', h1='#CFFBFF'),
      chk=dict(hd=['#07051A']),
      css=[('', 'background-image:linear-gradient(rgba(255,43,214,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(0,240,255,.05) 1px,transparent 1px);background-size:100% 30px,30px 100%'),
           ('.hd', 'box-shadow:0 0 14px rgba(255,43,214,.6)'),
           ('.iii i', 'box-shadow:0 0 6px #FF2BD6'),
           ('.mbtn', 'box-shadow:0 0 8px rgba(255,43,214,.5),inset 0 0 8px rgba(255,43,214,.3)'),
           ('.zf', 'text-shadow:0 0 8px rgba(0,240,255,.55)'),
           ('.lb', 'box-shadow:0 0 12px rgba(255,43,214,.45),inset 0 0 10px rgba(255,43,214,.25)'),
           ('.lb b', 'text-shadow:0 0 8px rgba(255,43,214,.8)'),
           ('.card + .card', 'border-color:#FF2BD6;box-shadow:0 0 0 1px rgba(255,43,214,.2),0 0 18px rgba(255,43,214,.35)')],
      orn=orn_neon(),
      guide=dict(colors=[('#0A0718', '黒紫'), ('#FF2BD6', 'ネオンピンク'), ('#00F0FF', 'ネオン水色'), ('#120C2A', 'カード'), ('#F4F0FF', '文字')],
                 fonts='見出し：Rampart One（光る字）<br>本文：Zen角ゴシック New', shape='角丸14px・光る線の枠（水色とピンク）・丸い光るボタン・格子の背景・すみにしま模様の太陽',
                 pic='紫の夜空・光る格子・しま模様の太陽・光る線でえがいた馬')),

 dict(id='pixel', cat=5, name='ドット絵', desc='昔のゲーム', title='ドット絵（レトロゲーム）', banner='pixel', alt='昔のゲームのようなドット絵で、コースを走る馬と「GO!」の文字',
      fonts=['DotGothic16'],
      v=dict(bg='#1D2B53', ink='#1D2B53', sub='#4A433C', card='#FFF1E8', cardB='0 solid transparent', cardO='0 solid transparent',
             cardS='0 -4px 0 0 #000,0 4px 0 0 #000,-4px 0 0 0 #000,4px 0 0 0 #000,6px 10px 0 0 rgba(0,0,0,.35)', radius='0', rs='0', font='"DotGothic16"',
             dfont='"DotGothic16"', dw='400', logo='#FFEC27', logoS='3px 3px 0 #FF004D', iii='#00E436', iiiB='0 solid transparent', iiiR='0', hd='#000000',
             hdInk='#FFF1E8', hdB='4px solid #29ADFF', mBg='transparent', mLine='#FFF1E8', mInk='#FFF1E8', pill='#1D2B53', pillLine='#29ADFF', pillInk='#FFF1E8',
             coin='#FFEC27', coinInk='#000000', badge='#FFEC27', badgeInk='#000000', badgeB='0 solid transparent', tagBg='#C2C3C7', tagInk='#000000', tagLine='#000000',
             warnBg='#FFA300', warnInk='#000000', zBg='#FFFFFF', zB='2px solid #1D2B53', znBg='#1D2B53', znInk='#FFEC27', znB='0 solid transparent', znR='0', znS='none',
             acc='#7E2553', nR='0', w2B='0 solid transparent', sep='2px dashed #83769C', btn='#00E436', btnInk='#000000', btnB='0 solid transparent', btnR='0',
             btnS='0 -3px 0 0 #000,0 3px 0 0 #000,-3px 0 0 0 #000,3px 0 0 0 #000,inset -3px -3px 0 0 #008751', btn2='#FFF1E8', btn2Ink='#1D2B53',
             btn2B='0 solid transparent', tab='#000000', tabB='4px solid #29ADFF', tabInk='#C2C3C7', tabOn='#29ADFF', tabOnInk='#000000', tabR='0', sel='#FFEC27',
             selInk='#000000', h1='#FFEC27', pageInk='#FFF1E8', pageSub='#C2C3C7', pageAcc='#FFEC27'),
      chk=dict(hd=['#000000']),
      css=[('', 'background-image:linear-gradient(rgba(255,255,255,.045) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.045) 2px,transparent 2px);background-size:16px 16px'),
           (SEG_SQ, ''),
           ('.ct', 'padding:18px 18px 0;gap:18px'),
           ('.seg', 'border:2px solid #1D2B53'),
           ('.seg.on', 'background:#29ADFF;color:#000000;border-color:#000000'),
           ('.btn.sub', 'box-shadow:0 -3px 0 0 #000,0 3px 0 0 #000,-3px 0 0 0 #000,3px 0 0 0 #000,inset -3px -3px 0 0 #C2C3C7'),
           ('.acts', 'gap:14px;margin-top:16px'),
           ('.lb', 'box-shadow:0 -3px 0 0 #000,0 3px 0 0 #000,-3px 0 0 0 #000,3px 0 0 0 #000'),
           ('.n', 'border-radius:0')],
      orn=orn_pixel(),
      guide=dict(colors=[('#1D2B53', '紺'), ('#FFEC27', '黄'), ('#00E436', '緑（ボタン）'), ('#29ADFF', '水色'), ('#FF004D', '赤')],
                 fonts='見出し・本文：DotGothic16（ドットの字）', shape='角なし・ギザギザのドットの枠・ボタンは段のある影・枠の色は16色だけ・すみにドットのハート',
                 pic='ドットの空と丘・コース・ゴール板・ドットの馬・「GO!」')),

 dict(id='chalk', cat=5, name='黒板', desc='チョーク・学校', title='黒板（緑×チョーク）', banner='chalk', alt='黒板にチョークでかいた走る馬と、メモや星の落書き',
      fonts=['Yomogi', 'Klee+One:wght@600'],
      v=dict(bg='#24423A', ink='#F3F1E7', sub='#C9D6CF', card='#2C4E44', cardB='2px dashed rgba(243,241,231,.5)', cardO='0 solid transparent', cardS='none',
             radius='8px', rs='6px', font='"Klee One"', dfont='"Yomogi"', dw='400', logo='#F3F1E7', logoS='0 0 2px rgba(255,255,255,.4)',
             iii='#F6E27F', iiiB='0 solid transparent', iiiR='2px',
             hd='repeating-linear-gradient(90deg,rgba(0,0,0,.06) 0 2px,transparent 2px 13px),linear-gradient(180deg,#9A6834,#7E5128)', hdInk='#FBEBD3',
             hdB='3px solid #5E3A18', mBg='rgba(0,0,0,.12)', mLine='#FBEBD3', mInk='#FBEBD3', pill='rgba(0,0,0,.18)', pillLine='rgba(255,240,210,.4)', pillInk='#FBEBD3',
             coin='#F6E27F', coinInk='#3E2611', badge='transparent', badgeInk='#F6E27F', badgeB='2px solid #F6E27F', tagBg='transparent', tagInk='#F3F1E7',
             tagLine='rgba(243,241,231,.5)', warnBg='rgba(244,166,192,.18)', warnInk='#FFD3E2', zBg='rgba(255,255,255,.04)', zB='1.5px solid rgba(243,241,231,.22)',
             znBg='#F6E27F', znInk='#24423A', znB='0 solid transparent', znR='4px', znS='none', acc='#F6E27F', nR='6px', w2B='1.5px solid #C9D6CF',
             sep='2px dashed rgba(243,241,231,.3)', btn='#F3F1E7', btnInk='#24423A', btnB='0 solid transparent', btnR='8px', btnS='0 3px 0 rgba(0,0,0,.25)',
             btn2='transparent', btn2Ink='#F4A6C0', btn2B='2px dashed #F4A6C0',
             tab='repeating-linear-gradient(90deg,rgba(0,0,0,.06) 0 2px,transparent 2px 13px),linear-gradient(180deg,#8A5A2B,#734A22)', tabB='3px solid #5E3A18',
             tabInk='#FBEBD3', tabOn='rgba(0,0,0,.22)', tabOnInk='#FFFFFF', tabR='8px', sel='#F6E27F', selInk='#24423A', h1='#F3F1E7'),
      chk=dict(hd=['#9A6834', '#7E5128'], tab=['#8A5A2B', '#734A22']),
      css=[('', 'background-image:radial-gradient(ellipse 130px 60px at 20% 30%,rgba(255,255,255,.05),transparent),radial-gradient(ellipse 170px 80px at 80% 70%,rgba(255,255,255,.045),transparent),radial-gradient(ellipse 110px 50px at 60% 8%,rgba(255,255,255,.04),transparent)'),
           ('.lb', 'border-radius:50%'),
           ('.vt,.zf,.logo,.lb b', 'text-shadow:0 0 1.5px rgba(255,255,255,.35)'),
           ('.tb', 'position:relative'),
           ('.tb::before', 'content:"";position:absolute;top:-10px;right:26px;width:64px;height:7px;border-radius:2px;background:linear-gradient(90deg,#F3F1E7 0 18px,transparent 18px 23px,#F6E27F 23px 41px,transparent 41px 46px,#F4A6C0 46px 64px)')],
      orn=orn_chalk(),
      guide=dict(colors=[('#24423A', '黒板'), ('#F3F1E7', 'チョーク白'), ('#F6E27F', 'チョーク黄'), ('#F4A6C0', 'チョークピンク'), ('#8A5A2B', '木の枠')],
                 fonts='見出し：Yomogi（手書き）<br>本文：Klee One', shape='角丸8px・チョークの点線の枠・Aは丸で囲む・上下の帯は木の枠・タブの上にチョーク・すみに花丸',
                 pic='黒板・チョークの馬・「本日の◎」のメモ・矢印と星・チョーク受け')),

 dict(id='carousel', cat=5, name='メリーゴーランド', desc='パステル・遊園地', title='メリーゴーランド（パステル×金）', banner='carousel', alt='しま模様の屋根と電球の下の、金の柱の木馬のイラスト',
      fonts=['Cherry+Bomb+One', 'Zen+Maru+Gothic:wght@500;700'],
      v=dict(bg='#FBEFF6', ink='#4A2A4E', sub='#82607F', card='#FFFFFF', cardB='2px solid #E9C46A', cardO='1px solid #F7DDEA', cardS='0 4px 0 #EBD3A4',
             radius='20px', rs='14px', font='"Zen Maru Gothic"', dfont='"Cherry Bomb One"', dw='400', logo='#B83A74', logoS='none',
             iii='#E9C46A', iiiB='0 solid transparent', iiiR='3px', hd='repeating-linear-gradient(90deg,#F49AC1 0 20px,#FFFFFF 20px 40px)', hdInk='#6A2C5A',
             hdB='0 solid transparent', mBg='#FFFFFF', mLine='#E9C46A', mInk='#6A2C5A', pill='#FFFFFF', pillLine='#E9C46A', pillInk='#6A2C5A', coin='#E9C46A',
             coinInk='#5A2A00', badge='linear-gradient(180deg,#FFF6D8,#F9DDEB)', badgeInk='#8A3A9A', badgeB='2px solid #E9C46A', tagBg='#FFF2F8', tagInk='#8A2F62',
             tagLine='#F3C6DC', warnBg='#FFE6D6', warnInk='#A0461A', zBg='#FFF8FB', zB='1.5px solid #F7DDEA', znBg='#B83A74', znInk='#FFFFFF', znB='1.5px solid #E9C46A',
             znR='999px', znS='none', acc='#8A3A9A', nR='9px', w2B='0 solid transparent', sep='2px dotted #F3C6DC', btn='#B83A74', btnInk='#FFFFFF',
             btnB='0 solid transparent', btnR='999px', btnS='0 3px 0 #8A2556', btn2='#FFFFFF', btn2Ink='#8A3A9A', btn2B='2px solid #E9C46A', tab='#FFFFFF',
             tabB='3px solid #E9C46A', tabInk='#82607F', tabOn='#FCE4F0', tabOnInk='#A8326A', tabR='14px', sel='#B83A74', selInk='#FFFFFF', h1='#8A3A9A'),
      chk=dict(hd=['#FFFFFF'], logo=['#B83A74'], logoBg=['#FFFFFF'], badge=['#FFF6D8', '#F9DDEB']),
      css=[('', 'background-image:radial-gradient(circle at 22px 30px,rgba(255,255,255,.75) 0 5px,transparent 6px),radial-gradient(circle at 84px 92px,rgba(255,214,232,.9) 0 7px,transparent 8px),radial-gradient(circle at 104px 20px,rgba(255,236,180,.7) 0 4px,transparent 5px),linear-gradient(180deg,#FBEFF6,#EFE6FA);background-size:124px 124px,124px 124px,124px 124px,100% 100%'),
           ('.logo', 'background:#FFFFFF;border:2px solid #E9C46A;border-radius:999px;padding:5px 12px 6px 13px;box-shadow:0 2px 0 #C9A044'),
           ('.mbtn', 'box-shadow:0 2px 0 #C9A044')],
      orn=orn_carousel(),
      guide=dict(colors=[('#F49AC1', 'ピンク'), ('#E9C46A', '金'), ('#B83A74', 'ボタン'), ('#8A3A9A', '紫'), ('#FBEFF6', '背景')],
                 fonts='見出し：Cherry Bomb One<br>本文：Zen Maru Gothic', shape='角丸20px・金の枠・上の帯はしま模様の屋根（絵とつながる）・ロゴは看板・丸いボタン・すみにテント',
                 pic='しま模様の屋根・電球・金の柱の木馬（ピンクとミントの鞍）・ぼけた光')),

 dict(id='stars', cat=5, name='星座', desc='夜空・ペガサス', title='星座・ペガサス（紺紫×金）', banner='constellation', alt='天の川の夜空に、星をむすんだ翼のある馬の星座と三日月のイラスト',
      fonts=['Tsukimi+Rounded:wght@500;700'],
      v=dict(bg='#0D0B2A', ink='#F3F0FF', sub='#B7AEE0', card='#17143A', cardB='1px solid #4A3F8F', cardO='0 solid transparent', cardS='0 8px 24px rgba(0,0,0,.35)',
             radius='16px', rs='12px', font='"Tsukimi Rounded"', dfont='"Tsukimi Rounded"', dw='700', logo='#FFF4D6', logoS='0 0 10px rgba(255,216,107,.55)',
             iii='#FFD86B', iiiB='0 solid transparent', iiiR='3px', hd='#0B0924', hdInk='#F3F0FF', hdB='0 solid transparent',
             mBg='transparent', mLine='#8E7CFF', mInk='#E8E4FF', pill='rgba(255,255,255,.05)', pillLine='rgba(185,172,255,.35)', pillInk='#E8E4FF', coin='#FFD86B',
             coinInk='#1A1440', badge='#221C55', badgeInk='#FFD86B', badgeB='1.5px solid #8E7CFF', tagBg='rgba(185,172,255,.08)', tagInk='#DCD6FF', tagLine='#4A3F8F',
             warnBg='rgba(255,216,107,.14)', warnInk='#FFE29A', zBg='rgba(255,255,255,.03)', zB='1px solid #3A3178', znBg='#FFD86B', znInk='#1A1440',
             znB='0 solid transparent', znR='999px', znS='none', acc='#FFE7A3', nR='8px', w2B='1.5px solid #9A92CC', sep='1px dashed #4A3F8F', btn='#B9ACFF',
             btnInk='#140F33', btnB='0 solid transparent', btnR='999px', btnS='0 0 16px rgba(185,172,255,.4)', btn2='transparent', btn2Ink='#FFD86B',
             btn2B='1px solid #FFD86B', tab='#0B0924', tabB='1px solid #2E2766', tabInk='#9A92CC', tabOn='rgba(255,216,107,.12)', tabOnInk='#FFD86B', tabR='14px',
             sel='#FFD86B', selInk='#1A1440', h1='#FFF4D6'),
      chk=dict(hd=['#0B0924']),
      css=[('', 'background-image:radial-gradient(1.3px 1.3px at 20px 30px,#FFFFFF,transparent),radial-gradient(1px 1px at 90px 80px,rgba(255,255,255,.8),transparent),radial-gradient(1.5px 1.5px at 150px 22px,#FFE7A3,transparent),radial-gradient(1px 1px at 60px 140px,rgba(255,255,255,.7),transparent),radial-gradient(1.2px 1.2px at 172px 118px,rgba(255,255,255,.9),transparent),linear-gradient(180deg,#0D0B2A,#1B1546);background-size:200px 160px,200px 160px,200px 160px,200px 160px,200px 160px,100% 100%'),
           ('.hd', 'padding-bottom:22px'),
           ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:3px;height:12px;background:' + stars_line() + ' 0 0/96px 12px repeat-x'),
           ('.lb b', 'text-shadow:0 0 10px rgba(255,216,107,.6)')],
      orn=orn_stars(),
      guide=dict(colors=[('#0D0B2A', '夜空'), ('#FFD86B', '星の金'), ('#B9ACFF', 'ラベンダー'), ('#17143A', 'カード'), ('#F3F0FF', '文字')],
                 fonts='見出し・本文：Tsukimi Rounded（月見）', shape='角丸16px・星の背景・帯の下に星座の線・金の「第1」・丸いボタン・すみに三日月',
                 pic='天の川・星でむすんだ翼のある馬（ペガサス）・三日月')),
]

CATS = {1: '定番', 2: '季節・行事', 3: '競馬', 4: '和・アート', 5: 'レトロ・ポップ'}
ORN = {t['id']: t['orn'] for t in THEMES}
