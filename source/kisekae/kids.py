"""子供向け：薄い黄色×パウダーホワイト・毛糸の編み目とフェルト・ぬいぐるみの馬・ロボット
   python3 kids.py <出力フォルダ>   → kids.svg（いつもの絵）
   壁紙の動き（kids_wall.py）のために、banner(parts) で 絵を部品に分けて受けとれる：下の絵・毛糸玉と糸・枠・かげ・
   馬（目なし）・馬のボタンの目・ロボット（黒目なし）・ロボットの黒目。部品を同じ順に重ねると いつもの絵（いつもの絵は前と1バイトもちがわない）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

BR = '#8A5A35'        # 縫い目・ふち
FELT = '#E9B47C'      # ぬいぐるみの馬（キャラメル）
FELT_L = '#F8DEBB'
YARN = '#E8843F'
STITCH = dict(fill='none', stroke=BR, stroke_width='1.3', stroke_dasharray='3 2.4', stroke_linecap='round')
HORSE_AT = (62, 22, .98)      # 馬を置く所（translate・scale）
ROBOT_AT = (216, 26, .98)     # ロボットを置く所
HORSE_EYE = (93, 44)          # 馬のボタンの目のまん中（馬の座標）
ROBOT_EYES = (35, 57)         # ロボットの目のまん中の x（y は 39・ロボットの座標）
YARN_BALL = (352, 128, 15)    # 毛糸玉のまん中と半径（絵の座標）


def stitched(d, fill, lw=2.0, inset_d=None, filt=True):
    out = path(d, fill=fill, stroke=BR, stroke_width=f(lw), stroke_linejoin='round', **({'filter': 'url(#felt)'} if filt else {}))
    if inset_d:
        out += path(inset_d, **STITCH)
    return out


def horse_eye():
    """馬のボタンの目（馬の座標）"""
    return ('<circle cx="93" cy="44" r="6.2" fill="#2B1E16"/><circle cx="91" cy="44" r="1.2" fill="#8A6A55"/><circle cx="95" cy="44" r="1.2" fill="#8A6A55"/>'
            '<circle cx="91.2" cy="41.2" r="1.4" fill="#FFFFFF" opacity=".85"/>')


def robot_pupil(ex):
    """ロボットの黒目と光（ロボットの座標・ex＝目のまん中の x）"""
    return f'<circle cx="{ex + 1}" cy="40" r="3.8" fill="#2B1E16"/><circle cx="{ex + 2.3}" cy="38.4" r="1.3" fill="#FFFFFF"/>'


def plush_horse(eye=True):
    """右向きのぬいぐるみの馬（だいたい 0〜135 × 0〜128）。eye=False なら ボタンの目なし（壁紙で目だけ動かす）"""
    head = smooth(ellipse_pts(84, 46, 28, 24, 14))
    snout = smooth(ellipse_pts(107, 59, 18, 14, 12, rot=10))
    body = smooth(ellipse_pts(58, 92, 33, 22, 14))
    neck = limb([(70, 76), (79, 62)], [28, 30])
    legs = [limb([(36, 104), (34, 120)], [15, 15]), limb([(50, 108), (50, 123)], [15, 15]),
            limb([(70, 108), (71, 123)], [15, 15]), limb([(84, 103), (87, 118)], [15, 15])]
    out = ''
    # しっぽ（毛糸）
    for d in ['M28 86 C 14 80, 8 88, 10 100', 'M28 90 C 18 90, 14 98, 16 108', 'M28 82 C 18 72, 8 74, 4 84']:
        out += path(d, fill='none', stroke=YARN, stroke_width='4.2', stroke_linecap='round')
        out += path(d, fill='none', stroke='#F6B27A', stroke_width='1.2', stroke_linecap='round', stroke_dasharray='2 3')
    # 脚（向こう）
    out += stitched(legs[0], '#D9A066') + stitched(legs[2], '#D9A066')
    # 体・首・頭（ひとまとまり＝フチどり）
    out += g(outlined([body, neck, head], FELT, BR, 1.0), filter='url(#felt)')
    out += stitched(legs[1], FELT) + stitched(legs[3], FELT)
    # ひづめのフェルト
    for x, y in [(34, 120), (50, 123), (71, 123), (87, 118)]:
        out += path(smooth([(x - 7, y - 5), (x + 7, y - 5), (x + 7, y + 3), (x - 7, y + 3)]), fill='#A8743F', stroke=BR, stroke_width='1.4')
    # 鼻先（別の布）
    out += stitched(snout, FELT_L, 2.0, smooth(ellipse_pts(107, 59, 14.5, 10.8, 12, rot=10)))
    # 縫い目
    out += path('M60 72 C 62 84, 60 100, 56 112', **STITCH)
    out += path('M70 64 C 76 70, 84 72, 92 70', **STITCH)
    # ハートのつぎあて
    out += stitched(heart(46, 92, 9), '#F7A8C0', 1.6, heart(46, 92, 6.6))
    # 耳
    for e, inner in [(smooth([(66, 30), (62, 8), (77, 22)]), smooth([(67, 26), (65, 13), (73, 22)])),
                     (smooth([(84, 23), (91, 4), (97, 26)]), smooth([(87, 21), (91, 10), (94, 23)]))]:
        out += stitched(e, FELT)
        out += path(inner, fill='#F7B3C6')
    # たてがみ（毛糸のループ）
    for cx, cy in [(64, 30), (59, 40), (56, 52), (57, 63), (62, 72), (72, 24), (98, 28)]:
        out += f'<circle cx="{cx}" cy="{cy}" r="6.4" fill="{YARN}" stroke="#C4652A" stroke-width="1.2"/>'
        out += f'<path d="M{cx - 3.6} {cy - 1} q3.6 -4 7.2 0" fill="none" stroke="#F6B27A" stroke-width="1.3" stroke-linecap="round"/>'
    # ボタンの目
    if eye:
        out += horse_eye()
    # ほっぺ・鼻・口（縫い目）
    out += '<circle cx="96" cy="58" r="4.6" fill="#F7A8C0" opacity=".9"/>'
    out += path('M114 55 l3 3 M117 55 l-3 3', fill='none', stroke=BR, stroke_width='1.4', stroke_linecap='round')
    out += path('M104 67 q5 4 10 0', **STITCH)
    return out


def robot(pupils=True):
    """手をふるロボット（だいたい 0〜95 × 0〜122）。pupils=False なら 黒目なし（壁紙で黒目だけ動かす）"""
    out = ''
    out += f'<path d="M46 9 L46 21" stroke="{BR}" stroke-width="2.4" stroke-linecap="round"/>'
    out += stitched(smooth(ellipse_pts(46, 8, 5.5, 5.5, 10)), '#FF9AA8', 1.6)
    # 腕（うしろ）
    out += stitched(limb([(24, 72), (14, 86), (12, 98)], [10, 9, 9]), '#9FD5C0', 1.8)
    out += stitched(smooth(ellipse_pts(12, 100, 6.5, 6.5, 10)), '#D9D9D9', 1.6)
    out += stitched(limb([(68, 70), (80, 58), (86, 46)], [10, 9, 9]), '#9FD5C0', 1.8)
    out += stitched(smooth(ellipse_pts(87, 42, 6.5, 6.5, 10)), '#D9D9D9', 1.6)
    # 足
    for x in (32, 50):
        out += stitched(f'M{x} 98 h12 v14 h-12 Z', '#9CCFEA', 1.6)
        out += stitched(smooth(ellipse_pts(x + 6, 114, 9, 4.6, 10)), '#7FB8D8', 1.6)
    # 体
    out += stitched('M30 62 h32 q10 0 10 10 v20 q0 10 -10 10 h-32 q-10 0 -10 -10 v-20 q0 -10 10 -10 Z', '#B6E8D1', 2.0,
                    'M31.5 66 h29 q7 0 7 7 v18 q0 7 -7 7 h-29 q-7 0 -7 -7 v-18 q0 -7 7 -7 Z')
    out += stitched(star5(46, 82, 9), '#FFD966', 1.5)
    # 頭
    out += stitched(smooth(ellipse_pts(16, 40, 5.2, 5.2, 10)), '#D9D9D9', 1.6) + stitched(smooth(ellipse_pts(76, 40, 5.2, 5.2, 10)), '#D9D9D9', 1.6)
    out += stitched('M30 20 h32 q12 0 12 12 v18 q0 12 -12 12 h-32 q-12 0 -12 -12 v-18 q0 -12 12 -12 Z', '#A9DCF3', 2.0,
                    'M31 24.5 h30 q8.5 0 8.5 8.5 v16 q0 8.5 -8.5 8.5 h-30 q-8.5 0 -8.5 -8.5 v-16 q0 -8.5 8.5 -8.5 Z')
    for ex in ROBOT_EYES:
        out += f'<circle cx="{ex}" cy="39" r="7.4" fill="#FFFFFF" stroke="{BR}" stroke-width="1.5"/>' + (robot_pupil(ex) if pupils else '')
    out += '<circle cx="28" cy="50" r="3.6" fill="#F7A8C0"/><circle cx="64" cy="50" r="3.6" fill="#F7A8C0"/>'
    out += path('M40 50 q6 5 12 0', fill='none', stroke=BR, stroke_width='1.8', stroke_linecap='round')
    return out


def cloud(x, y, s):
    d = smooth([(x, y), (x + 6 * s, y - 9 * s), (x + 18 * s, y - 12 * s), (x + 28 * s, y - 6 * s), (x + 38 * s, y - 9 * s),
                (x + 48 * s, y - 2 * s), (x + 46 * s, y + 6 * s), (x + 2 * s, y + 6 * s)])
    return stitched(d, '#FCFBF7', 1.6)


def at(t):
    x, y, s = t
    return f'translate({f(x)} {f(y)}) scale({s:g})'.replace('scale(0.', 'scale(.')


def banner(parts=None):
    """いつもの絵（SVG）。parts に dict を入れると 部品を入れて返す（壁紙の動き・kids_wall.py）"""
    W, H = 390, 160
    defs = ('<pattern id="knit" width="12" height="10" patternUnits="userSpaceOnUse">'
            '<ellipse cx="3.1" cy="5" rx="2.5" ry="4.7" transform="rotate(-30 3.1 5)" fill="#F4DC82"/>'
            '<ellipse cx="8.9" cy="5" rx="2.5" ry="4.7" transform="rotate(30 8.9 5)" fill="#F4DC82"/>'
            '<path d="M2 2.4 q1.2 1.6 1.6 4 M10 2.4 q-1.2 1.6 -1.6 4" stroke="#FFF7CF" stroke-width=".9" fill="none" stroke-linecap="round"/></pattern>'
            '<filter id="felt" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="3" result="n"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .9 -.32" result="w"/>'
            '<feComposite in="w" in2="SourceGraphic" operator="in" result="t"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="t"/></feMerge></filter>')
    b = f'<rect width="{W}" height="{H}" fill="#FFF3B8"/><rect width="{W}" height="{H}" fill="url(#knit)"/>'
    # パウダーホワイトの布（下）
    b += stitched(smooth([(-10, 128), (40, 118), (110, 124), (180, 116), (250, 124), (320, 116), (400, 124), (400, 170), (-10, 170)]), '#FCFBF7', 1.8)
    b += path(smooth([(-10, 133), (40, 123), (110, 129), (180, 121), (250, 129), (320, 121), (400, 129)], closed=False), **STITCH)
    # 雲・星・毛糸玉
    b += cloud(20, 34, .9) + cloud(250, 24, .75)
    for cx, cy, r, c in [(150, 26, 9, '#FFD966'), (212, 54, 6.5, '#FFB7C5'), (366, 74, 7.5, '#FFD966'), (330, 30, 6, '#A9DCF3')]:
        b += stitched(star5(cx, cy, r), c, 1.4)
    yx, yy, yr = YARN_BALL
    ball = stitched(smooth(ellipse_pts(yx, yy, yr, yr, 12)), '#F7A8C0', 1.8)
    for d in [f'M{yx - 12} {yy - 6} q12 -6 24 4', f'M{yx - 14} {yy + 2} q14 -8 27 2', f'M{yx - 10} {yy + 10} q10 -6 21 0', f'M{yx - 4} {yy - 14} q-4 14 2 28']:
        ball += path(d, fill='none', stroke='#D9799A', stroke_width='1.4', stroke_linecap='round')
    thread = path(f'M{yx - 14} {yy + 8} C {yx - 40} {yy + 22}, {yx - 70} {yy + 6}, {yx - 92} {yy + 18}', fill='none', stroke='#F7A8C0', stroke_width='2.2', stroke_linecap='round')
    # 糸のかがりの枠
    frame = '<rect x="6" y="6" width="378" height="148" rx="12" fill="none" stroke="#B88A5A" stroke-width="1.6" stroke-dasharray="6 4" stroke-linecap="round"/>'
    # ぬいぐるみの馬・ロボット
    shadow_h = '<ellipse cx="128" cy="146" rx="48" ry="5" fill="#C9A27A" opacity=".3"/>'
    shadow_r = '<ellipse cx="262" cy="146" rx="30" ry="4.5" fill="#C9A27A" opacity=".3"/>'
    horse = g(plush_horse(), transform=at(HORSE_AT))
    rob = g(robot(), transform=at(ROBOT_AT))
    if parts is not None:
        parts.update(size=(W, H), defs=defs, bg=b, ball=ball, thread=thread, frame=frame, shadow_h=shadow_h, shadow_r=shadow_r,
                     horse=g(plush_horse(eye=False), transform=at(HORSE_AT)), eye=g(horse_eye(), transform=at(HORSE_AT)),
                     robot=g(robot(pupils=False), transform=at(ROBOT_AT)), pupils=[g(robot_pupil(ex), transform=at(ROBOT_AT)) for ex in ROBOT_EYES])
    return svg(W, H, b + ball + thread + frame + shadow_h + shadow_r + horse + rob, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/kids.svg', 'w').write(banner())
