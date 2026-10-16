"""かわいい：ピンク・ハート・リボン・目の大きいポニー（右向き）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

LINE = '#A8416F'
PINK = '#FF8DC0'
DEEP = '#FF4F9A'


def bow(cx, cy, s, c=DEEP, line=LINE, tails=True, dots=True):
    """リボン（結び目が cx,cy）"""
    P = lambda pts: smooth([(cx + x * s, cy + y * s) for x, y in pts])
    loopL = P([(0, 0), (-6, -7), (-16, -10), (-22, -4), (-21, 6), (-14, 10), (-6, 6)])
    loopR = P([(0, 0), (6, -7), (16, -10), (22, -4), (21, 6), (14, 10), (6, 6)])
    out = ''
    if tails:
        tL = P([(-2, 3), (-8, 14), (-12, 24), (-6, 22), (-3, 26), (1, 6)])
        tR = P([(2, 3), (8, 14), (12, 24), (6, 22), (3, 26), (-1, 6)])
        out += outlined([tL, tR], c, line, 1.4 * min(1.4, s))
    out += outlined([loopL, loopR], c, line, 1.4 * min(1.4, s))
    # ひだ（内側の影）
    out += path(P([(-3, -1), (-12, -6), (-17, -2), (-12, 1)]), fill='#000', opacity='.12')
    out += path(P([(3, -1), (12, -6), (17, -2), (12, 1)]), fill='#000', opacity='.12')
    if dots:
        for x, y in [(-15, -3), (-10, 4), (14, -4), (11, 4)]:
            out += f'<circle cx="{f(cx + x * s)}" cy="{f(cy + y * s)}" r="{f(1.3 * s)}" fill="#fff" opacity=".9"/>'
    out += outlined([smooth(ellipse_pts(cx, cy, 4.2 * s, 5 * s, 10))], c, line, 1.4 * min(1.4, s))
    return out


def pony():
    """右向きのポニー（だいたい 0〜135 × 0〜122）"""
    head = smooth(ellipse_pts(80, 48, 31, 27, 14))
    snout = smooth(ellipse_pts(105, 60, 18, 14, 12, rot=8))
    body = smooth(ellipse_pts(56, 90, 29, 19, 12))
    neck = limb([(66, 72), (74, 60)], [24, 26])
    legs = [limb([(40, 98), (38, 113)], [12, 12]), limb([(51, 101), (51, 115)], [12, 12]),
            limb([(66, 101), (67, 115)], [12, 12]), limb([(76, 98), (78, 112)], [12, 12])]
    ears = [smooth([(62, 30), (58, 9), (73, 22)]), smooth([(80, 22), (86, 5), (93, 24)])]
    tail = limb([(30, 84), (17, 76), (9, 86), (15, 97), (24, 95)], [9, 12, 12, 9, 6])
    out = ''
    for cx, cy, r in [(28, 84, 9), (18, 78, 8.5), (11, 89, 8.5), (17, 100, 7.5), (28, 96, 6.5)]:
        out += outlined([smooth(ellipse_pts(cx, cy, r, r, 10))], PINK, LINE, 2.0)
    for cx, cy, r in [(18, 78, 4), (11, 89, 4), (17, 100, 3.4)]:
        out += path(smooth(ellipse_pts(cx + .8, cy + .8, r, r * .7, 8)), fill='none', stroke=LINE, stroke_width='1.1', opacity='.5')
    # 向こうの脚は少しだけ濃く
    out += outlined(legs[0:1] + legs[2:3], '#FFF0F6', LINE, 2.2)
    out += outlined([body, neck, head, snout] + legs[1:2] + legs[3:4], '#FFFFFF', LINE, 2.2)
    # ひづめ
    for x, y in [(38, 113), (51, 115), (67, 115), (78, 112)]:
        out += path(smooth([(x - 6, y - 4), (x + 6, y - 4), (x + 6, y + 2), (x - 6, y + 2)]), fill='#FFB3CF')
    # 鼻先・ほっぺ
    out += path(smooth(ellipse_pts(108, 62, 13, 10, 12, rot=8)), fill='#FFE4EE')
    out += '<ellipse cx="96" cy="64" rx="7" ry="4" fill="#FF9FC4" opacity=".85"/>'
    out += '<ellipse cx="116" cy="58" rx="1.8" ry="2.4" fill="#C0607F"/>'
    out += path('M104 70 q4 4 9 0', fill='none', stroke=LINE, stroke_width='1.8', stroke_linecap='round')
    # 大きい目
    out += '<ellipse cx="90" cy="46" rx="7.5" ry="9.5" fill="#3A1F2B"/>'
    out += '<ellipse cx="90" cy="49" rx="5.5" ry="5.5" fill="#7A3C5C" opacity=".8"/>'
    out += '<circle cx="92.6" cy="41.6" r="3" fill="#fff"/><circle cx="87.6" cy="51" r="1.5" fill="#fff"/>'
    out += path('M95.5 39 l4 -3.5 M97 42 l4.6 -1.8', fill='none', stroke='#3A1F2B', stroke_width='1.7', stroke_linecap='round')
    # たてがみ（くるくる）
    for cx, cy, r in [(60, 25, 11), (53, 37, 11), (51, 51, 10), (55, 63, 8), (71, 17, 9), (96, 26, 7.5)]:
        out += outlined([smooth(ellipse_pts(cx, cy, r, r, 10))], PINK, LINE, 2.0)
    for cx, cy, r in [(60, 25, 5), (53, 37, 5), (51, 51, 4.5), (71, 17, 4)]:
        out += path(smooth(ellipse_pts(cx + 1, cy + 1, r, r * .7, 8)), fill='none', stroke=LINE, stroke_width='1.2', opacity='.5')
    # 耳（たてがみの上）
    out += outlined([smooth([(60, 26), (55, 4), (71, 18)]), smooth([(84, 22), (92, 3), (97, 25)])], '#FFFFFF', LINE, 2.2)
    out += path(smooth([(61, 22), (58, 10), (67, 18)]), fill='#FFC2DA')
    out += path(smooth([(87, 20), (92, 9), (94, 22)]), fill='#FFC2DA')
    # 頭のリボン
    out += bow(76, 15, .6)
    return out


def banner():
    W, H = 390, 160
    defs = ('<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
            '<circle cx="5" cy="5" r="2.6" fill="#FFFFFF" opacity=".75"/><circle cx="16" cy="16" r="2.6" fill="#FFFFFF" opacity=".75"/></pattern>'
            '<linearGradient id="pk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD3E5"/><stop offset="1" stop-color="#FFE9F2"/></linearGradient>')
    b = f'<rect width="{W}" height="{H}" fill="url(#pk)"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
    # レースのふち（下）
    lace = ''
    for i in range(0, 24):
        x = i * 17 + 4
        lace += f'<circle cx="{x}" cy="158" r="10.5" fill="#FFFFFF"/>'
    for i in range(0, 24):
        x = i * 17 + 4
        lace += f'<circle cx="{x}" cy="154" r="2.2" fill="#FFD3E5"/>'
    b += lace + '<rect x="0" y="152" width="390" height="8" fill="#FFFFFF"/>'
    b += ''.join(f'<circle cx="{i * 17 + 12.5}" cy="156" r="1.6" fill="#FFC2DA"/>' for i in range(23))
    # ハート
    for cx, cy, s, c, o in [(316, 72, 26, '#FF6FA8', ''), (360, 112, 13, '#FFA6CB', ''), (284, 124, 9, '#FFFFFF', LINE),
                            (34, 34, 10, '#FF8DC0', ''), (168, 28, 8, '#FFB7D3', ''), (226, 112, 10, '#FF6FA8', ''),
                            (246, 40, 6, '#FFFFFF', LINE), (20, 112, 7, '#FFB7D3', '')]:
        if o:
            b += path(heart(cx, cy, s), fill=c, stroke=o, stroke_width='1.6')
        else:
            b += path(heart(cx, cy, s), fill=c)
    b += path(heart(316, 72, 26), fill='none', stroke='#FFFFFF', stroke_width='2', opacity='.0')
    b += path('M300 58 q4 -6 10 -4', fill='none', stroke='#FFFFFF', stroke_width='3', stroke_linecap='round', opacity='.8')
    # 大きいリボン（右上）
    b += bow(356, 34, 1.15)
    # キラキラ
    for cx, cy, r, c in [(268, 30, 8, '#FFFFFF'), (196, 66, 5, '#FFF3A6'), (126, 26, 6, '#FFFFFF'), (346, 140, 6, '#FFFFFF'), (210, 140, 4.5, '#FFF3A6'), (14, 70, 5, '#FFFFFF')]:
        b += path(sparkle(cx, cy, r), fill=c)
    # ポニー
    b += '<ellipse cx="128" cy="146" rx="46" ry="5" fill="#E77BAA" opacity=".25"/>'
    b += g(pony(), transform='translate(66 24) scale(1.0)')
    return svg(W, H, b, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/cute.svg', 'w').write(banner())
    open(f'{out}/cute_pony.svg', 'w').write(svg(140, 130, g(pony(), transform='translate(2 4)')))
