"""かわいい：ピンク・ハート・リボン・目の大きいポニー（右向き）
   python3 cute.py <出力フォルダ>   → cute.svg（いつもの絵）・cute_pony.svg
   壁紙の動き（cute_wall.py）のために、banner(parts) で 絵を部品に分けて受けとれる：下の絵（水玉・レース）・ハート（1つめが大きいハート）・
   大きいハートの光・右上のリボン・キラキラ・かげ・ポニー。部品を同じ順に重ねると いつもの絵（いつもの絵は前と1バイトもちがわない）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

LINE = '#A8416F'
PINK = '#FF8DC0'
DEEP = '#FF4F9A'
# ハート：(まん中 x, y, 大きさ, 色, ふち)。1つめが 大きいハート
HEARTS = [(316, 72, 26, '#FF6FA8', ''), (360, 112, 13, '#FFA6CB', ''), (284, 124, 9, '#FFFFFF', LINE),
          (34, 34, 10, '#FF8DC0', ''), (168, 28, 8, '#FFB7D3', ''), (226, 112, 10, '#FF6FA8', ''),
          (246, 40, 6, '#FFFFFF', LINE), (20, 112, 7, '#FFB7D3', '')]
BIG_BOW = (356, 34, 1.15)     # 右上の大きいリボン（結び目と大きさ）
PONY_AT = (66, 24)            # ポニーを置く所


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


def pony_shapes():
    """ポニーの 頭・鼻先・体・首・脚の形（ふちどりで ひとまとまりにする所）"""
    head = smooth(ellipse_pts(80, 48, 31, 27, 14))
    snout = smooth(ellipse_pts(105, 60, 18, 14, 12, rot=8))
    body = smooth(ellipse_pts(56, 90, 29, 19, 12))
    neck = limb([(66, 72), (74, 60)], [24, 26])
    legs = [limb([(40, 98), (38, 113)], [12, 12]), limb([(51, 101), (51, 115)], [12, 12]),
            limb([(66, 101), (67, 115)], [12, 12]), limb([(76, 98), (78, 112)], [12, 12])]
    return head, snout, body, neck, legs


def pony_tail():
    out = ''
    for cx, cy, r in [(28, 84, 9), (18, 78, 8.5), (11, 89, 8.5), (17, 100, 7.5), (28, 96, 6.5)]:
        out += outlined([smooth(ellipse_pts(cx, cy, r, r, 10))], PINK, LINE, 2.0)
    for cx, cy, r in [(18, 78, 4), (11, 89, 4), (17, 100, 3.4)]:
        out += path(smooth(ellipse_pts(cx + .8, cy + .8, r, r * .7, 8)), fill='none', stroke=LINE, stroke_width='1.1', opacity='.5')
    return out


def pony_hooves():
    out = ''
    for x, y in [(38, 113), (51, 115), (67, 115), (78, 112)]:
        out += path(smooth([(x - 6, y - 4), (x + 6, y - 4), (x + 6, y + 2), (x - 6, y + 2)]), fill='#FFB3CF')
    return out


def pony_face_side():
    """横向きの顔：鼻先・ほっぺ・鼻・口・大きい目"""
    out = path(smooth(ellipse_pts(108, 62, 13, 10, 12, rot=8)), fill='#FFE4EE')
    out += '<ellipse cx="96" cy="64" rx="7" ry="4" fill="#FF9FC4" opacity=".85"/>'
    out += '<ellipse cx="116" cy="58" rx="1.8" ry="2.4" fill="#C0607F"/>'
    out += path('M104 70 q4 4 9 0', fill='none', stroke=LINE, stroke_width='1.8', stroke_linecap='round')
    # 大きい目
    out += '<ellipse cx="90" cy="46" rx="7.5" ry="9.5" fill="#3A1F2B"/>'
    out += '<ellipse cx="90" cy="49" rx="5.5" ry="5.5" fill="#7A3C5C" opacity=".8"/>'
    out += '<circle cx="92.6" cy="41.6" r="3" fill="#fff"/><circle cx="87.6" cy="51" r="1.5" fill="#fff"/>'
    out += path('M95.5 39 l4 -3.5 M97 42 l4.6 -1.8', fill='none', stroke='#3A1F2B', stroke_width='1.7', stroke_linecap='round')
    return out


def pony_mane(curls=((60, 25, 11), (53, 37, 11), (51, 51, 10), (55, 63, 8), (71, 17, 9), (96, 26, 7.5)),
              inner=((60, 25, 5), (53, 37, 5), (51, 51, 4.5), (71, 17, 4))):
    """たてがみ（くるくる）"""
    out = ''
    for cx, cy, r in curls:
        out += outlined([smooth(ellipse_pts(cx, cy, r, r, 10))], PINK, LINE, 2.0)
    for cx, cy, r in inner:
        out += path(smooth(ellipse_pts(cx + 1, cy + 1, r, r * .7, 8)), fill='none', stroke=LINE, stroke_width='1.2', opacity='.5')
    return out


def pony_ears(ears=(((60, 26), (55, 4), (71, 18)), ((84, 22), (92, 3), (97, 25))),
              inner=(((61, 22), (58, 10), (67, 18)), ((87, 20), (92, 9), (94, 22))), bow_at=(76, 15)):
    """耳（たてがみの上）と 頭のリボン"""
    out = outlined([smooth(list(e)) for e in ears], '#FFFFFF', LINE, 2.2)
    for e in inner:
        out += path(smooth(list(e)), fill='#FFC2DA')
    out += bow(bow_at[0], bow_at[1], .6)
    return out


def pony():
    """右向きのポニー（だいたい 0〜135 × 0〜122）"""
    head, snout, body, neck, legs = pony_shapes()
    out = pony_tail()
    # 向こうの脚は少しだけ濃く
    out += outlined(legs[0:1] + legs[2:3], '#FFF0F6', LINE, 2.2)
    out += outlined([body, neck, head, snout] + legs[1:2] + legs[3:4], '#FFFFFF', LINE, 2.2)
    out += pony_hooves()
    out += pony_face_side()
    out += pony_mane()
    out += pony_ears()
    return out


# ---------- 壁紙で頭を回す（こっちを見る）ための部品（cute_wall.py）：体と頭を分けて重ねると いつものポニーと同じ ----------
def pony_body():
    """体：しっぽ・脚・体と首（ふちどり）・ひづめ（頭は べつ）"""
    head, snout, body, neck, legs = pony_shapes()
    return (pony_tail() + outlined(legs[0:1] + legs[2:3], '#FFF0F6', LINE, 2.2)
            + outlined([body, neck] + legs[1:2] + legs[3:4], '#FFFFFF', LINE, 2.2) + pony_hooves())


def pony_head_side():
    """横向きの頭：頭と鼻先の ふちどり → 首も白でぬって 首の上の ふちを消す（いつもの ひとまとまりの形と同じに見える）→ 顔・たてがみ・耳・リボン"""
    head, snout, body, neck, legs = pony_shapes()
    return outlined([head, snout], '#FFFFFF', LINE, 2.2) + path(neck, fill='#FFFFFF') + pony_face_side() + pony_mane() + pony_ears()


def front_eye(ex, ey, side):
    """正面の顔の 大きい目（side：-1＝左の目・1＝右の目。まつげは外がわ）"""
    lash = f'M{ex + side * 5.6:g} {ey - 6.2:g} l{side * 4:g} -3.2 M{ex + side * 7:g} {ey - 3.2:g} l{side * 4.6:g} -1.6'
    return (f'<ellipse cx="{ex:g}" cy="{ey:g}" rx="6.8" ry="8.8" fill="#3A1F2B"/>'
            f'<ellipse cx="{ex:g}" cy="{ey + 2.8:g}" rx="5" ry="5" fill="#7A3C5C" opacity=".8"/>'
            f'<circle cx="{ex + 2.2:g}" cy="{ey - 4.2:g}" r="2.7" fill="#fff"/><circle cx="{ex - 2.2:g}" cy="{ey + 4.4:g}" r="1.3" fill="#fff"/>'
            + path(lash, fill='none', stroke='#3A1F2B', stroke_width='1.7', stroke_linecap='round'))


def pony_head_front(eye_cls=''):
    """こっちを向いた顔（正面）：横向きと同じ白い頭・大きい目2つ（eye_cls：目の まばたき・びっくり用のクラス）・ほっぺ・鼻のまわり・
       たてがみ（左に流れる・前髪）・耳・リボン。首は横向きと同じ"""
    head = smooth(ellipse_pts(80, 47, 30, 27, 14))
    muzzle = smooth(ellipse_pts(80, 63, 16, 11.5, 12))
    neck = pony_shapes()[3]
    out = outlined([head, muzzle], '#FFFFFF', LINE, 2.2) + path(neck, fill='#FFFFFF')
    out += path(smooth(ellipse_pts(80, 64, 12.5, 8.6, 12)), fill='#FFE4EE')
    out += '<ellipse cx="75.6" cy="62.4" rx="1.7" ry="2.3" fill="#C0607F"/><ellipse cx="84.4" cy="62.4" rx="1.7" ry="2.3" fill="#C0607F"/>'
    out += path('M75.5 68.2 q2.25 2.6 4.5 0 q2.25 2.6 4.5 0', fill='none', stroke=LINE, stroke_width='1.6', stroke_linecap='round', stroke_linejoin='round')
    out += '<ellipse cx="63" cy="57" rx="5.8" ry="3.5" fill="#FF9FC4" opacity=".85"/><ellipse cx="97" cy="57" rx="5.8" ry="3.5" fill="#FF9FC4" opacity=".85"/>'
    c = f' class="{eye_cls}"' if eye_cls else ''
    for ex, side in ((68.5, -1), (91.5, 1)):
        out += f'<g{c}>{front_eye(ex, 45, side)}</g>'
    out += pony_mane(((54, 28, 10), (49, 40, 10.5), (49, 52, 10), (54, 63, 8), (72, 18, 8.5), (87, 17, 8)),
                     ((54, 28, 4.6), (49, 40, 4.8), (49, 52, 4.5), (72, 18, 3.8)))
    out += pony_ears((((59, 27), (55, 5), (70, 19)), ((101, 27), (105, 5), (90, 19))),
                     (((61, 22), (58, 10), (67, 18)), ((99, 22), (102, 10), (93, 18))), bow_at=(64, 14))
    return out


def heart_shape(cx, cy, s, c, o):
    if o:
        return path(heart(cx, cy, s), fill=c, stroke=o, stroke_width='1.6')
    return path(heart(cx, cy, s), fill=c)


def banner(parts=None):
    """いつもの絵（SVG）。parts に dict を入れると 部品を入れて返す（壁紙の動き・cute_wall.py）"""
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
    hearts = [heart_shape(*h) for h in HEARTS]
    shine = path(heart(316, 72, 26), fill='none', stroke='#FFFFFF', stroke_width='2', opacity='.0')
    shine += path('M300 58 q4 -6 10 -4', fill='none', stroke='#FFFFFF', stroke_width='3', stroke_linecap='round', opacity='.8')
    # 大きいリボン（右上）
    big_bow = bow(*BIG_BOW)
    # キラキラ
    spark = ''
    for cx, cy, r, c in [(268, 30, 8, '#FFFFFF'), (196, 66, 5, '#FFF3A6'), (126, 26, 6, '#FFFFFF'), (346, 140, 6, '#FFFFFF'), (210, 140, 4.5, '#FFF3A6'), (14, 70, 5, '#FFFFFF')]:
        spark += path(sparkle(cx, cy, r), fill=c)
    # ポニー
    shadow = '<ellipse cx="128" cy="146" rx="46" ry="5" fill="#E77BAA" opacity=".25"/>'
    pony_g = g(pony(), transform=f'translate({PONY_AT[0]} {PONY_AT[1]}) scale(1.0)')
    if parts is not None:
        at = f'translate({PONY_AT[0]} {PONY_AT[1]}) scale(1.0)'
        parts.update(size=(W, H), defs=defs, bg=b, hearts=hearts, shine=shine, bow=big_bow, sparkles=spark, shadow=shadow, pony=pony_g,
                     pony_body=g(pony_body(), transform=at), pony_head=g(pony_head_side(), transform=at), pony_front=g(pony_head_front('cwe'), transform=at))
    return svg(W, H, b + ''.join(hearts) + shine + big_bow + spark + shadow + pony_g, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/cute.svg', 'w').write(banner())
    open(f'{out}/cute_pony.svg', 'w').write(svg(140, 130, g(pony(), transform='translate(2 4)')))
