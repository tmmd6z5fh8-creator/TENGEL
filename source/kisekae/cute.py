"""かわいい：ピンク・ハート・リボン・目の大きいポニー（右向き）
   python3 cute.py <出力フォルダ>   → cute.svg（いつもの絵）・cute_pony.svg
   壁紙の動き（cute_wall.py）のために、banner(parts) で 絵を部品に分けて受けとれる：下の絵（水玉・レース）・ハート（1つめが大きいハート）・
   大きいハートの光・右上のリボン・キラキラ・かげ・ポニー。部品を同じ順に重ねると いつもの絵（いつもの絵は前と1バイトもちがわない）"""
import sys, os, re, math
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


HOOVES = [(38, 113), (51, 115), (67, 115), (78, 112)]   # 脚の もよう（ピンクの 帯）の まん中（legs と 同じ じゅん：0・2 が 向こうの 脚）
FAR, NEAR = (0, 2), (1, 3)


def _sample(d, step=.2):
    """smooth() の 形（M … C … Z）を こまかい 点の 列に（絵に なる 形と 同じ：小数1けたに まるめた 値の まま）"""
    pts, cur = [], None
    for cmd, arg in re.findall(r'([MC])([^MCZ]*)', d):
        v = [float(s) for s in re.findall(r'-?\d+(?:\.\d+)?', arg)]
        if cmd == 'M':
            cur = (v[0], v[1]); pts.append(cur); continue
        for i in range(0, len(v), 6):
            c1, c2, p3 = (v[i], v[i + 1]), (v[i + 2], v[i + 3]), (v[i + 4], v[i + 5])
            n = max(4, int((math.dist(cur, c1) + math.dist(c1, c2) + math.dist(c2, p3)) / step))
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                pts.append(tuple(u * u * u * cur[j] + 3 * u * u * t * c1[j] + 3 * u * t * t * c2[j] + t * t * t * p3[j] for j in (0, 1)))
            cur = p3
    if math.dist(pts[0], pts[-1]) < 1e-9:
        pts.pop()
    return pts


def _area(P):
    return sum(P[i - 1][0] * P[i][1] - P[i][0] * P[i - 1][1] for i in range(len(P))) / 2


def _grow(P, r):
    """形を まわりへ r だけ ふくらませる（こまかい 点の 列）"""
    s, n, out = (1 if _area(P) > 0 else -1), len(P), []
    for i in range(n):
        a, b = P[i - 1], P[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]; ln = math.hypot(tx, ty) or 1
        out.append((P[i][0] + s * ty / ln * r, P[i][1] - s * tx / ln * r))
    return out


def _clip(subj, clip):
    """subj を clip（ふくらんだ 形）の 中だけに 切る（Sutherland–Hodgman）"""
    s, out = (1 if _area(clip) > 0 else -1), subj
    for i in range(len(clip)):
        a, b = clip[i - 1], clip[i]
        side = lambda p: s * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            sp, sq = side(p), side(q)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
            if sq >= 0:
                out.append(q)
    return out


def _rdp(P, eps):
    if len(P) < 3:
        return P
    (ax, ay), (bx, by) = P[0], P[-1]; ln = math.hypot(bx - ax, by - ay) or 1e-9
    d = [abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / ln for x, y in P[1:-1]]
    k = max(range(len(d)), key=d.__getitem__)
    if d[k] <= eps:
        return [P[0], P[-1]]
    return _rdp(P[:k + 2], eps)[:-1] + _rdp(P[k + 1:], eps)


def hoof_d(i, legs):
    """脚 i の もよう（ピンクの 帯）：前と 同じ 帯の 形を、脚の ふちの 内がわ だけに 切る（＋0.3 だけ ふちに かかる＝白い すき間が 出ない）。
       第4.217版（まさちゃん 2026/11/24 17:07「足の模様が繋ぎ目が無くなってるから、ちゃんと境目が分かるようにして！」）：
       前は 帯が 脚の はばより 左右 1.5 ずつ はみ出して、となりの 脚との あいだの ふちの 線を かくして いた"""
    x, y = HOOVES[i]
    band = _sample(smooth([(x - 6, y - 4), (x + 6, y - 4), (x + 6, y + 2), (x - 6, y + 2)]))
    P = _clip(_grow(_sample(legs[i]), .3), band)
    k = max(range(len(P)), key=lambda j: math.dist(P[0], P[j]))      # とじた 形：いちばん 遠い 点で 2つに 分けて 点を へらす
    P = _rdp(P[:k + 1], .02)[:-1] + _rdp(P[k:] + [P[0]], .02)[:-1]
    g2 = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    return 'M' + ' L'.join(f'{g2(px)} {g2(py)}' for px, py in P) + ' Z'


def pony_hooves(which=FAR + NEAR):
    legs = pony_shapes()[4]
    return ''.join(path(hoof_d(i, legs), fill='#FFB3CF') for i in which)


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


SIDE_EARS = (((60, 26), (55, 4), (71, 18)), ((84, 22), (92, 3), (97, 25)))      # 横向きの 頭の 耳（左・右）
SIDE_INNER = (((61, 22), (58, 10), (67, 18)), ((87, 20), (92, 9), (94, 22)))     # 耳の 中の ピンク
SIDE_BOW = (76, 15)                                                             # 頭の リボンの 結び目
FRONT_DX = 4      # 正面の 顔：横向きと 同じ 耳2つ・リボンを 4 右へ（リボンが 顔の まん中 x=80 に くる）


def pony_ears(ears=SIDE_EARS, inner=SIDE_INNER, bow_at=SIDE_BOW):
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
    # 向こうの脚は少しだけ濃く。脚の もようは 向こうの 脚の 分を 先に（手前の 脚の ふちが 上に のる＝さかい目が 見える）
    out += outlined(legs[0:1] + legs[2:3], '#FFF0F6', LINE, 2.2) + pony_hooves(FAR)
    out += outlined([body, neck, head, snout] + legs[1:2] + legs[3:4], '#FFFFFF', LINE, 2.2)
    out += pony_hooves(NEAR)
    out += pony_face_side()
    out += pony_mane()
    out += pony_ears()
    return out


# ---------- 壁紙で頭を回す（こっちを見る）ための部品（cute_wall.py）：体と頭を分けて重ねると いつものポニーと同じ ----------
def pony_body():
    """体：しっぽ・脚・体と首（ふちどり）・ひづめ（頭は べつ）"""
    head, snout, body, neck, legs = pony_shapes()
    return (pony_tail() + outlined(legs[0:1] + legs[2:3], '#FFF0F6', LINE, 2.2) + pony_hooves(FAR)
            + outlined([body, neck] + legs[1:2] + legs[3:4], '#FFFFFF', LINE, 2.2) + pony_hooves(NEAR))


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
    # 第4.217版（まさちゃん 2026/11/24 17:07「一枚目、の上側の赤丸の耳とリボンの形で、二枚目、三枚目も統一して！」）：
    #   耳と リボンは 横向きの 頭と 同じ 形（耳2つの あいだに リボン）。前は リボンが 左の 耳の 上（左の 耳が かくれる）・右の 耳だけ 大きかった
    sh = lambda E: tuple(tuple((x + FRONT_DX, y) for x, y in e) for e in E)
    out += pony_ears(sh(SIDE_EARS), sh(SIDE_INNER), bow_at=(SIDE_BOW[0] + FRONT_DX, SIDE_BOW[1]))
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
