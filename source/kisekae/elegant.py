"""綺麗：レッド×ブラック・眼鏡の大人の女性・薔薇・赤い月とたてがみがなびく馬"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

RED = '#C1121F'
RED2 = '#E0303F'
DARK = '#0B0708'
SKIN = '#F2D2C3'
SKIN_S = '#DDAE9C'
HAIR = '#140B0D'


def rose(cx, cy, r, base='#A30F1A', dark='#5E0710', light='#E0303F'):
    out = ''
    # 外の花びら（5枚）
    for i in range(5):
        a = math.radians(i * 72 - 90)
        px, py = cx + math.cos(a) * r * .55, cy + math.sin(a) * r * .55
        out += path(smooth(ellipse_pts(px, py, r * .62, r * .5, 10, rot=i * 72)), fill=base)
    out += path(smooth(ellipse_pts(cx, cy, r * .78, r * .72, 12)), fill='#B8131F')
    # うず（花びらの重なり）
    for i, rr in enumerate([.72, .52, .34, .18]):
        a0 = i * 95 + 20
        a1 = a0 + 230
        x0, y0 = cx + math.cos(math.radians(a0)) * r * rr, cy + math.sin(math.radians(a0)) * r * rr
        x1, y1 = cx + math.cos(math.radians(a1)) * r * rr, cy + math.sin(math.radians(a1)) * r * rr
        out += f'<path d="M{f(x0)} {f(y0)} A{f(r * rr)} {f(r * rr)} 0 1 1 {f(x1)} {f(y1)}" fill="none" stroke="{dark}" stroke-width="{f(max(1.1, r * .09))}" stroke-linecap="round"/>'
        xa, ya = cx + math.cos(math.radians(a0 + 40)) * r * rr * .9, cy + math.sin(math.radians(a0 + 40)) * r * rr * .9
        xb, yb = cx + math.cos(math.radians(a0 + 120)) * r * rr * .9, cy + math.sin(math.radians(a0 + 120)) * r * rr * .9
        out += f'<path d="M{f(xa)} {f(ya)} A{f(r * rr * .9)} {f(r * rr * .9)} 0 0 1 {f(xb)} {f(yb)}" fill="none" stroke="{light}" stroke-width="{f(max(.8, r * .05))}" stroke-linecap="round" opacity=".7"/>'
    return out


def rleaf(x, y, ln, w, ang, c='#2F4A2C'):
    a = math.radians(ang)
    return (path(leaf(x, y, ln, w, ang), fill=c)
            + f'<path d="M{f(x)} {f(y)} L{f(x + math.cos(a) * ln * .85)} {f(y + math.sin(a) * ln * .85)}" stroke="#1B2E1A" stroke-width=".9"/>')


def lady():
    """眼鏡をかけた大人の女性（正面・肩まで）。だいたい 20〜140 × 10〜160"""
    out = ''
    # うしろの髪（長いウェーブ）
    out += path(smooth([(78, 18), (104, 22), (120, 40), (124, 64), (126, 90), (132, 114), (128, 136), (118, 150), (108, 140),
                        (104, 118), (100, 96), (60, 96), (54, 120), (48, 142), (36, 150), (28, 134), (34, 110), (36, 84),
                        (38, 58), (48, 34), (62, 22)]), fill=HAIR)
    # 首・肩（ドレスは肩を出したデザイン）
    out += path(smooth([(70, 90), (90, 90), (91, 108), (100, 118), (124, 128), (138, 140), (142, 160), (18, 160), (22, 140),
                        (36, 128), (60, 118), (69, 108)]), fill=SKIN)
    out += path(smooth([(70, 93), (90, 93), (86, 99), (80, 101), (74, 99)]), fill=SKIN_S, opacity='.55')
    # 鎖骨
    out += path('M62 126 q10 3 16 1 M98 126 q-10 3 -16 1', fill='none', stroke=SKIN_S, stroke_width='1.3', stroke_linecap='round')
    # 黒いドレス（肩を出したライン・赤いふち）
    out += path('M14 140 C 40 134, 60 140, 80 144 C 100 140, 120 134, 146 140 L150 160 L10 160 Z', fill='#120C0E')
    out += path('M14 140 C 40 134, 60 140, 80 144 C 100 140, 120 134, 146 140', fill='none', stroke=RED, stroke_width='1.6')
    # ネックレス（赤い雫）
    out += path('M66 114 q14 12 28 0', fill='none', stroke='#D9A35B', stroke_width='.9', opacity='.9')
    out += path(smooth([(80, 121), (83, 126), (80, 130), (77, 126)]), fill=RED)
    # 顔
    face = smooth([(80, 30), (96, 34), (104, 46), (105, 62), (101, 77), (93, 89), (80, 96), (67, 89), (59, 77), (55, 62), (56, 46), (64, 34)])
    out += path(face, fill=SKIN)
    # ほお
    out += '<ellipse cx="65" cy="75" rx="6" ry="3.4" fill="#E48A8A" opacity=".35"/><ellipse cx="95" cy="75" rx="6" ry="3.4" fill="#E48A8A" opacity=".35"/>'
    # まゆ
    out += path('M60 50 Q67 45 75 48.5', fill='none', stroke=HAIR, stroke_width='1.7', stroke_linecap='round')
    out += path('M85 48.5 Q93 45 100 50', fill='none', stroke=HAIR, stroke_width='1.7', stroke_linecap='round')
    # 目（ふせ目）
    for ex, sgn in [(69, -1), (91, 1)]:
        out += path(f'M{ex - 7} 62 Q{ex} 57.5 {ex + 7} 62 Q{ex} 65.5 {ex - 7} 62 Z', fill='#FFFFFF')
        out += f'<circle cx="{ex}" cy="62" r="3" fill="#3B1418"/><circle cx="{ex + .9}" cy="61" r=".8" fill="#fff"/>'
        out += path(f'M{ex - 7.5} 61.6 Q{ex} 56.2 {ex + 7.5} 61.6', fill='none', stroke=HAIR, stroke_width='2.4', stroke_linecap='round')
        tx = ex + 7.5 * sgn
        out += path(f'M{tx} 61.4 l{f(2.6 * sgn)} -2.6 M{tx - 1.6 * sgn} 60 l{f(2 * sgn)} -3', fill='none', stroke=HAIR, stroke_width='1.2', stroke_linecap='round')
        out += path(f'M{ex - 6} 64.4 Q{ex} 67 {ex + 6} 64.4', fill='none', stroke=SKIN_S, stroke_width='.9')
    # 眼鏡（細いキャットアイ・外側がはね上がる）
    for cx, sgn in [(69, -1), (91, 1)]:
        o = lambda x, y: (cx + x * sgn, y)   # x＋が外側
        lens = smooth([o(-8.5, 57.6), o(0, 57), o(8, 56.2), o(12.5, 53.4), o(11.6, 59), o(9.5, 65), o(3, 68.4), o(-4, 68.2), o(-8.6, 64.6), o(-9.4, 60.4)])
        out += path(lens, fill='#FFFFFF', fill_opacity='.07', stroke='#0A0607', stroke_width='1.5', stroke_linejoin='round')
        tx, ty = o(12.5, 53.4)
        out += f'<circle cx="{f(tx)}" cy="{f(ty)}" r="1.25" fill="{RED}"/>'
        hx1, hy1 = o(5, 58.4); hx2, hy2 = o(1, 64.8)
        out += f'<path d="M{f(hx1)} {f(hy1)} L{f(hx2)} {f(hy2)}" stroke="#FFFFFF" stroke-width="1" opacity=".5" stroke-linecap="round"/>'
        ax, ay = o(11.8, 56)
        out += f'<path d="M{f(ax)} {f(ay)} L{f(ax + 4 * sgn)} {f(ay + 1.5)}" stroke="#0A0607" stroke-width="1.4" stroke-linecap="round"/>'
    out += path('M77.8 60.2 Q80 58.2 82.2 60.2', fill='none', stroke='#0A0607', stroke_width='1.4')
    # 鼻
    out += path('M80.5 66 Q78.5 73 78.5 76 Q80 77.5 82.5 76.5', fill='none', stroke=SKIN_S, stroke_width='1.2', stroke_linecap='round')
    # 赤い口紅
    out += path('M71.5 83.3 Q75.5 80.3 78.6 82 Q80 81 81.4 82 Q84.5 80.3 88.5 83.3 Q84 84.6 80 84.6 Q76 84.6 71.5 83.3 Z', fill='#A30F1A')
    out += path('M72 83.6 Q80 91.2 88 83.6 Q84 85.6 80 85.6 Q76 85.6 72 83.6 Z', fill=RED)
    out += path('M77 87.2 Q80 88.4 83 87.2', fill='none', stroke='#FFFFFF', stroke_width='.9', opacity='.55', stroke_linecap='round')
    # 前髪（横に流す）と顔の横のウェーブ
    out += path(smooth([(56, 50), (58, 34), (68, 24), (84, 20), (100, 24), (110, 34), (114, 48), (112, 62), (108, 52), (101, 42), (92, 35), (82, 32), (72, 33), (64, 39)]), fill=HAIR)
    out += path(smooth([(104, 40), (112, 52), (110, 70), (114, 88), (110, 104), (116, 120), (108, 126), (102, 112), (104, 94), (101, 76), (104, 60)]), fill=HAIR)
    out += path(smooth([(58, 46), (52, 60), (55, 76), (51, 94), (56, 110), (50, 118), (46, 104), (47, 86), (46, 66), (50, 50)]), fill=HAIR)
    # 髪のつや（赤みの線）
    for d in ['M68 30 Q84 22 104 32', 'M107 62 Q112 80 108 100', 'M50 64 Q48 84 52 104']:
        out += path(d, fill='none', stroke='#5A1A22', stroke_width='1.6', stroke_linecap='round', opacity='.9')
    # イヤリング
    out += f'<path d="M106 82 l0 5" stroke="#D9A35B" stroke-width=".9"/>' + path(smooth([(106, 87), (108.5, 91), (106, 95), (103.5, 91)]), fill=RED)
    # 髪の薔薇
    out += rleaf(52, 34, 12, 6, 200) + rleaf(54, 30, 11, 5.5, 240)
    out += rose(56, 34, 9)
    return out


def horse_head():
    """赤い月の前の、右向きの馬の頭と首（黒のシルエット・赤いふち）。だいたい 0〜130 × 0〜150"""
    head = smooth([(64, 6), (70, 20), (82, 25), (95, 40), (107, 60), (116, 76), (121, 86), (119, 95), (111, 99), (103, 97),
                   (94, 91), (85, 84), (77, 83), (73, 92), (72, 114), (76, 150), (12, 150), (20, 118), (30, 88), (40, 58),
                   (48, 36), (55, 20)])
    ear2 = smooth([(54, 22), (52, 4), (62, 14)])
    out = path(ear2, fill='#060405', stroke=RED, stroke_width='1.3', stroke_linejoin='round')
    out += path(head, fill='#060405', stroke=RED, stroke_width='1.5', stroke_linejoin='round')
    # ふちの光（顔の前）
    out += path('M84 27 Q100 44 111 66 Q118 79 120 88', fill='none', stroke='#FF6B76', stroke_width='1.2', opacity='.8', stroke_linecap='round')
    # 目・鼻・口
    out += path('M84 44 Q89 40 94 44 Q89 46.5 84 44 Z', fill=RED2)
    out += path('M84 43 l-3.5 -2.2 M86 41.6 l-2.4 -3', fill='none', stroke=RED2, stroke_width='1', stroke_linecap='round')
    out += path('M110 83 Q114 80 116 85', fill='none', stroke=RED2, stroke_width='1.3', stroke_linecap='round')
    out += path('M104 95 Q108 96 112 94', fill='none', stroke=RED, stroke_width='1', stroke_linecap='round', opacity='.8')
    out += path('M78 80 Q86 70 96 66', fill='none', stroke=RED, stroke_width='.9', opacity='.5')
    # なびくたてがみ（首すじから左へ流れる・先が細い）
    locks = [
        ([(58, 14), (44, 8), (30, 12), (16, 6), (4, 10)], [5, 4.4, 3.4, 2.2, .8], RED),
        ([(54, 26), (40, 24), (28, 32), (14, 28), (0, 34)], [6, 5, 4, 2.6, .8], RED2),
        ([(50, 40), (36, 40), (24, 50), (12, 48), (0, 56)], [6, 5, 4, 2.4, .8], RED),
        ([(46, 54), (34, 58), (24, 68), (12, 70), (2, 78)], [5.5, 4.6, 3.6, 2.2, .8], RED2),
        ([(42, 68), (32, 74), (24, 86), (14, 90), (6, 100)], [5, 4.2, 3.2, 2, .8], RED),
        ([(38, 84), (30, 92), (24, 104), (16, 110), (10, 120)], [4.5, 3.8, 3, 1.8, .7], RED2),
    ]
    for pts, ws, c in locks:
        out += path(limb(pts, ws), fill=c, opacity='.95')
    for d in ['M56 20 C 44 18, 34 22, 22 18', 'M48 48 C 38 50, 30 58, 18 60', 'M40 76 C 32 82, 26 92, 18 98']:
        out += path(d, fill='none', stroke='#FF7A85', stroke_width='.9', stroke_linecap='round', opacity='.8')
    return out


def banner():
    W, H = 390, 160
    defs = ('<radialGradient id="glow" cx=".76" cy=".45" r=".6"><stop offset="0" stop-color="#3A0A10"/><stop offset="1" stop-color="#0B0708"/></radialGradient>'
            '<radialGradient id="moon" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="#9E1420"/><stop offset=".7" stop-color="#5E0A12"/><stop offset="1" stop-color="#2A0509"/></radialGradient>')
    b = f'<rect width="{W}" height="{H}" fill="url(#glow)"/>'
    # 赤い月と馬
    b += '<circle cx="86" cy="80" r="62" fill="url(#moon)"/><circle cx="86" cy="80" r="66" fill="none" stroke="#C1121F" stroke-width=".8" opacity=".7"/>'
    b += g(horse_head(), transform='translate(30 10) scale(.98)')
    # 薔薇（まん中の下）
    b += rleaf(170, 138, 22, 10, 200) + rleaf(196, 146, 20, 9, 330) + rleaf(222, 140, 18, 8, 300) + rleaf(182, 128, 16, 7, 250)
    b += rose(178, 140, 15) + rose(206, 146, 12) + rose(160, 152, 10)
    b += rleaf(352, 20, 16, 7, 150) + rose(372, 16, 10)
    # 女性
    b += g(lady(), transform='translate(218 2) scale(1.0)')
    # 細い赤の二重線
    b += '<rect x="5" y="5" width="380" height="150" fill="none" stroke="#C1121F" stroke-width=".8" opacity=".75"/>'
    b += '<rect x="8.5" y="8.5" width="373" height="143" fill="none" stroke="#C1121F" stroke-width=".4" opacity=".55"/>'
    return svg(W, H, b, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/elegant.svg', 'w').write(banner())
    open(f'{out}/elegant_lady.svg', 'w').write(svg(160, 160, f'<rect width="160" height="160" fill="#2A0A10"/>' + lady()))
    open(f'{out}/elegant_horse.svg', 'w').write(svg(140, 160, f'<rect width="140" height="160" fill="#5E0A12"/>' + g(horse_head(), transform='translate(5 5)')))
