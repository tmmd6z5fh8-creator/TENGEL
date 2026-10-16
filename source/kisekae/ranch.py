"""牧場：青空・芝・木の柵・栗毛の馬（左向き・立ち姿）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

CH = '#B8642C'      # 栗毛
CH_D = '#97501F'    # 向こう側の脚
MANE = '#5A2D12'
HOOF = '#3A2A1E'
LINE = '#4A2410'


def horse():
    """左向きの馬（だいたい 0〜128 × -6〜108）"""
    far = [
        limb([(54, 60), (58, 80), (60, 94), (60, 102)], [13, 9, 6.5, 7]),        # 前の向こう脚（少し前に）
        limb([(92, 54), (87, 72), (96, 86), (94, 98), (94, 103)], [20, 13, 8, 6.5, 7]),  # 後ろの向こう脚
    ]
    body = smooth([(34, 50), (40, 38), (52, 32), (68, 36), (84, 34), (100, 32), (112, 40), (116, 54),
                   (110, 66), (96, 70), (70, 72), (48, 70), (38, 64)])
    neck = smooth([(56, 36), (48, 22), (38, 11), (29, 7), (21, 14), (19, 25), (25, 38), (32, 50), (44, 54)])
    head = smooth([(31, 4), (22, 5), (14, 13), (7, 23), (3, 31), (6, 37), (13, 38), (20, 34), (27, 26), (32, 15)])
    near = [
        limb([(42, 62), (42, 82), (43, 95), (43, 102)], [14, 9, 6.5, 7]),        # 前の手前脚
        limb([(104, 52), (98, 72), (108, 86), (106, 98), (106, 103)], [24, 15, 8.5, 6.5, 7]),  # 後ろの手前脚（飛節はうしろへ）
    ]
    ears = [smooth([(26, 7), (28, -6), (33, 4)]), smooth([(31, 8), (35, -4), (37, 7)])]
    out = ''
    # しっぽ（体のうしろ）
    out += path(limb([(113, 42), (123, 50), (127, 66), (122, 86)], [8, 11, 10, 5]), fill=MANE)
    out += path(smooth([(116, 46), (126, 58), (128, 76), (124, 92), (120, 80), (121, 62)]), fill=MANE)
    # 向こう側
    out += ''.join(path(d, fill=CH_D) for d in far)
    out += path(ears[1], fill=CH_D)
    # ひづめ（向こう）
    out += path('M56 101 L64 101 L65 106 L55 106 Z', fill=HOOF)
    out += path('M90 101 L98 101 L99 106 L89 106 Z', fill=HOOF)
    # 手前（まとめて塗る）
    for d in [body, neck, head] + near + [ears[0]]:
        out += path(d, fill=CH)
    # おなかの影・首の影
    out += path(smooth([(48, 66), (70, 68), (96, 66), (90, 72), (70, 73), (50, 71)]), fill=CH_D, opacity='.55')
    # 白い靴下
    out += path('M39.6 95 L46.4 95 L46.6 101.5 L39.4 101.5 Z', fill='#FFF6E8')
    # ひづめ（手前）
    out += path('M39 101 L47 101 L48 106 L38 106 Z', fill=HOOF)
    out += path('M102 101 L110 101 L111 106 L101 106 Z', fill=HOOF)
    # 耳の中
    out += path(smooth([(28, 5), (29, -2), (31, 4)]), fill='#7A3A16')
    # たてがみ（ふさが3つ）
    out += path(smooth([(29, 4), (37, 6), (45, 12), (52, 21), (58, 31), (60, 37), (55, 35), (51, 29), (48, 31), (45, 24), (41, 25), (39, 18), (34, 17), (31, 10)]), fill=MANE)
    # 前髪
    out += path(smooth([(28, 5), (22, 7), (18, 12), (22, 12), (25, 10)]), fill=MANE)
    # 鼻すじの白（流星）
    out += path(limb([(23, 11), (16, 19), (9, 29)], [4.5, 4, 3.2]), fill='#FFF6E8')
    # 目・鼻・口
    out += '<circle cx="19.5" cy="18.5" r="2.4" fill="#22140C"/><circle cx="20.3" cy="17.7" r=".8" fill="#fff"/>'
    out += path('M7.5 29.5 q2 -2 3.5 .5', fill='none', stroke=LINE, stroke_width='1.4', stroke_linecap='round')
    out += path('M8 35 q3 1 6 -.5', fill='none', stroke=LINE, stroke_width='1.1', stroke_linecap='round', opacity='.7')
    # ほっぺの丸み
    out += path(smooth([(22, 25), (26, 22), (27, 27), (24, 31)]), fill=CH_D, opacity='.35')
    return out


def tuft(x, y, s=1, c='#5C9A23'):
    return path(f'M{f(x)} {f(y)} l{f(2*s)} {f(-8*s)} l{f(1.6*s)} {f(8*s)} l{f(2.4*s)} {f(-6*s)} l{f(1.4*s)} {f(6*s)} l{f(2.2*s)} {f(-9*s)} l{f(1.6*s)} {f(9*s)} Z', fill=c)


def cloud(x, y, s, o='1'):
    return g(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(10*s)}"/><circle cx="{f(x+12*s)}" cy="{f(y-6*s)}" r="{f(13*s)}"/>'
             f'<circle cx="{f(x+27*s)}" cy="{f(y-1*s)}" r="{f(10*s)}"/><rect x="{f(x)}" y="{f(y-2*s)}" width="{f(27*s)}" height="{f(12*s)}" rx="{f(6*s)}"/>',
             fill='#FFFFFF', opacity=o)


def fence(x0, x1, ytop, ybot, n):
    out = ''
    step = (x1 - x0) / (n - 1)
    rails = ''
    for yy in (ytop + 7, ytop + 18):
        rails += f'<rect x="{f(x0 - 3)}" y="{f(yy)}" width="{f(x1 - x0 + 6)}" height="5" rx="1.5" fill="#D29A5E" stroke="#8A5A2B" stroke-width="1.2"/>'
    posts = ''
    for i in range(n):
        x = x0 + i * step
        posts += f'<path d="M{f(x - 3.5)} {f(ybot)} L{f(x - 3.5)} {f(ytop + 3)} L{f(x)} {f(ytop - 1)} L{f(x + 3.5)} {f(ytop + 3)} L{f(x + 3.5)} {f(ybot)} Z" fill="#C88B4E" stroke="#8A5A2B" stroke-width="1.2" stroke-linejoin="round"/>'
    return posts + rails


def banner():
    W, H = 390, 160
    defs = ('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9DDF6"/><stop offset="1" stop-color="#E6F6FC"/></linearGradient>'
            '<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6C2"/><stop offset=".55" stop-color="#FFE57A" stop-opacity=".9"/><stop offset="1" stop-color="#FFE57A" stop-opacity="0"/></radialGradient>')
    b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    b += '<circle cx="342" cy="34" r="30" fill="url(#sun)"/><circle cx="342" cy="34" r="15" fill="#FFD84A"/>'
    b += cloud(52, 34, 1.0) + cloud(196, 22, .75, '.95') + cloud(282, 50, .55, '.9')
    # 遠くの丘・小屋
    b += path('M0 92 C 50 70, 110 66, 170 82 S 300 60, 390 80 L390 160 L0 160 Z', fill='#B9DE7E')
    bx, by = 300, 64
    b += f'<rect x="{bx}" y="{by}" width="30" height="20" fill="#C8553D"/><path d="M{bx - 4} {by + 1} L{bx + 15} {by - 13} L{bx + 34} {by + 1} Z" fill="#9C3A2A"/>'
    b += f'<rect x="{bx + 10}" y="{by + 7}" width="10" height="13" fill="#F3E3C8"/><path d="M{bx + 10} {by + 7} L{bx + 20} {by + 20} M{bx + 20} {by + 7} L{bx + 10} {by + 20}" stroke="#C8553D" stroke-width="1.4"/>'
    b += path('M0 108 C 70 94, 150 98, 230 108 S 340 98, 390 104 L390 160 L0 160 Z', fill='#92CB45')
    b += fence(14, 150, 92, 128, 5)
    b += path('M0 128 C 110 118, 250 120, 390 126 L390 160 L0 160 Z', fill='#7DBA34')
    # 草・花
    for x, y, s in [(8, 146, 1), (40, 152, .8), (70, 141, 1.1), (122, 150, .9), (160, 140, 1), (260, 148, 1.1), (300, 139, .8), (338, 151, 1), (372, 142, .9), (226, 156, .7)]:
        b += tuft(x, y, s)
    for x, y, c in [(30, 136, '#FFFFFF'), (96, 146, '#FFE14D'), (142, 134, '#FFFFFF'), (284, 132, '#FFE14D'), (318, 146, '#FFFFFF'), (356, 132, '#FFFFFF'), (250, 138, '#FFE14D')]:
        b += f'<g fill="{c}"><circle cx="{x - 2.2}" cy="{y}" r="2"/><circle cx="{x + 2.2}" cy="{y}" r="2"/><circle cx="{x}" cy="{y - 2.2}" r="2"/><circle cx="{x}" cy="{y + 2.2}" r="2"/></g><circle cx="{x}" cy="{y}" r="1.3" fill="#F2A33A"/>'
    # 馬（影＋本体）
    b += '<ellipse cx="236" cy="139" rx="50" ry="5" fill="#4E8A1C" opacity=".35"/>'
    b += g(horse(), transform='translate(186 52) scale(.84)')
    return svg(W, H, b, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/ranch.svg', 'w').write(banner())
    open(f'{out}/ranch_horse.svg', 'w').write(svg(140, 120, g(horse(), transform='translate(4 10)')))
