"""プレミアムど的中（かわいいど的中）：まさちゃんの指定
   「プレミアムど的中演出 発動条件、ど的中の6回に1回発動、ランダム
    ・かわいいど的中 かわいいの馬がひらがなを持っている絵で タップしたらハートが上から下に落ちて画面上に積もっていき、画面一杯になったら、ハートが弾ける演出、
    一瞬白い光に包まれてから でっかいハートの中に、ど！が書いてる そのハートを写真の馬が持っている！
    ①ど！、左から画面中央(馬顔右向き) ②て！、右から画面中央(馬顔左向き) ③き！、下から画面中央(馬顔やや右向き)
    ④ちゅ！❤️、上から画面中央(馬顔やや左向き、左目ウィンク) ⑤う！画面中央に出てくる(馬顔正面) 一文字づつの画面で演出
    最後に ど的中❤️、細かいハートのエフェクトが上に消えていき、大きなハートに包まれたど的中を画面中央に表示する で終わり」
   「かわいいのど的中ボタン限定ではなくて、ど的中ボタンのプレミアムだからどの壁紙使ってても、ど的中の6回に1回はこれが出るようにって意味だった。」
   → どの着せ替えでも ど的中の 6回に1回。最後の ボードは その着せ替えの ど的中の ボード（見本は ど的中と 同じ デフォルト＝牧場）
   - 絵は ぜんぶ 一から作った形（SVG）。ポニーは かわいいの壁紙の ポニー（cute.py）と 同じ 形と 色で、大きな ハートを 前に だいて 立つ。
     まさちゃんの 写真（つやつやの ハートを だく ポニー）は ふんいきの 参考だけ（なぞっていない）
   - 字（ど・て・き・ち・ゅ・う・！・的・中）は 太い まるい 線で 書いた 字（フォントを 使わない：GLYPHS）。こい ピンクの ふち → 白い ふち → 虹色 → つや
   このファイルは 部品（絵と字）。動き（時刻・CSS）は 下の 方（PC_T・pc_layers・PC_CSS）・見本の 画面は gen_fx.py の fz_pc"""
import math
import random
from art import f, smooth, limb, ellipse_pts, heart, sparkle, path, g, outlined
import cute as C

LINE = C.LINE                  # ふち（かわいいの壁紙と同じ こい ピンク）
PINK, DEEP = C.PINK, C.DEEP

# ---------------------------------------------------------------- 字（太い まるい 線で 書いた 字。100×100 の ます・y は下向き）
# 1つの字 ＝ (はば, [線…])。線 ＝ 点の 列（なめらかに つなぐ。同じ 点を 2回 ならべると 角）。点 1つ だけの 線は まるい 点
GLYPHS = {
    'ど': (104, [[(38, 14), (44, 46)],
                 [(76, 28), (58, 38), (40, 50), (30, 62), (29, 76), (38, 86), (56, 89), (78, 86)],
                 [(78, 8), (83, 20)], [(90, 4), (95, 16)]]),
    'て': (100, [[(14, 32), (50, 24), (86, 20), (86, 20), (62, 32), (46, 48), (42, 66), (50, 82), (68, 90)]]),
    'き': (100, [[(22, 24), (74, 18)], [(16, 44), (82, 36)],
                 [(38, 6), (50, 30), (62, 52), (66, 60)],
                 [(32, 64), (30, 74), (38, 84), (56, 88), (76, 86)]]),
    'ち': (100, [[(18, 28), (80, 22)],
                 [(46, 6), (42, 30), (36, 54), (36, 54), (52, 46), (68, 46), (78, 56), (78, 72), (66, 84), (46, 90), (34, 88)]]),
    'ゆ': (100, [[(22, 24), (20, 62), (20, 62), (30, 48), (46, 38), (64, 36), (80, 46), (82, 62), (72, 74), (56, 76)],
                 [(52, 14), (54, 40), (54, 64), (50, 82), (40, 92)]]),
    'う': (100, [[(40, 10), (62, 16)],
                 [(24, 40), (44, 34), (64, 32), (76, 40), (78, 56), (70, 72), (54, 84), (36, 92)]]),
    '！': (48, [[(24, 10), (24, 60)], [(24, 84)]]),
    '的': (100, [[(28, 6), (22, 18)],
                 [(12, 24), (12, 90)], [(12, 24), (42, 24), (42, 24), (42, 90)], [(12, 56), (42, 56)], [(12, 88), (42, 88)],
                 [(62, 6), (54, 24)],
                 [(54, 28), (88, 28), (88, 28), (86, 70), (82, 86), (70, 90)],
                 [(64, 50), (72, 64)]]),
    '中': (100, [[(16, 28), (16, 68)], [(16, 28), (84, 28), (84, 28), (84, 68)], [(16, 66), (84, 66)], [(50, 6), (50, 96)]]),
}
SMALL = {'ゅ': ('ゆ', .62, 70)}     # 小さい字：(もとの字・大きさ・はば)。下に そろえる


def glyph_d(ch, x0, y0, s):
    """字 ch の 線（path の d）。(x0, y0)＝ますの 左上・s＝1ます の 大きさ（px）"""
    small = SMALL.get(ch)
    if small:
        base, k, _ = small
        w, strokes = GLYPHS[base]
        ox, oy, sc = x0 + 4 * s, y0 + (100 - 100 * k) * s - 4 * s, s * k
    else:
        w, strokes = GLYPHS[ch]
        ox, oy, sc = x0, y0, s
    d = ''
    for st in strokes:
        pts = [(ox + x * sc, oy + y * sc) for x, y in st]
        if len(pts) == 1:
            d += f'M{f(pts[0][0])} {f(pts[0][1])} L{f(pts[0][0])} {f(pts[0][1])} '
        elif len(pts) == 2:
            d += f'M{f(pts[0][0])} {f(pts[0][1])} L{f(pts[1][0])} {f(pts[1][1])} '
        else:
            d += smooth(pts, closed=False) + ' '
    return d.strip()


def advance(ch):
    return SMALL[ch][2] if ch in SMALL else GLYPHS[ch][0]


def word_d(text, cx, cy, s, gap=-4):
    """横に ならべた 字の 線と、はば（cx, cy＝まん中・s＝1ます の px）"""
    adv = [advance(c) for c in text]
    total = (sum(adv) + gap * (len(text) - 1)) * s
    x = cx - total / 2
    d = ''
    for c, a in zip(text, adv):
        d += glyph_d(c, x, cy - 50 * s, s) + ' '
        x += (a + gap) * s
    return d.strip(), total


RAINBOW = (('0', '#FF5FA8'), ('.2', '#FF9A4A'), ('.38', '#FFE04A'), ('.55', '#6BE08A'), ('.72', '#4CC8FF'), ('.88', '#8F7BFF'), ('1', '#D46BFF'))


def rainbow_grad(gid, y0, y1):
    stops = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in RAINBOW)
    return f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{f(y0)}" x2="0" y2="{f(y1)}">{stops}</linearGradient>'


def word_svg(text, cx, cy, s, gid, w=15.0, gap=-4):
    """虹色の まるい 字（ふち：こい ピンク → 白 → 虹色 → つや）。gid：虹色の グラデーションの id（defs は べつに 入れる）"""
    d, _ = word_d(text, cx, cy, s, gap)
    W = w * s
    common = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<path d="{d}" {common} stroke="#7A1C4A" stroke-width="{f(W + 16 * s)}" transform="translate(0 {f(5 * s)})" opacity=".35"/>'
            f'<path d="{d}" {common} stroke="{LINE}" stroke-width="{f(W + 15 * s)}"/>'
            f'<path d="{d}" {common} stroke="#FFFFFF" stroke-width="{f(W + 8 * s)}"/>'
            f'<path d="{d}" {common} stroke="url(#{gid})" stroke-width="{f(W)}"/>'
            f'<path d="{d}" {common} stroke="#FFFFFF" stroke-width="{f(W * .3)}" opacity=".55" transform="translate({f(-1.6 * s)} {f(-2.2 * s)})"/>')


# ---------------------------------------------------------------- ポニー（かわいいの壁紙の ポニーと 同じ 形と 色。大きな ハートを 前に だいて 立つ）
S_HEAD = 2.7                   # 頭の 大きさ（壁紙の ポニーの 何倍）
HEART_C, HEART_S = (195.0, 470.0), 150.0     # ハートの まん中と 大きさ（390×844 の 画面。ハートの はば＝2×HEART_S）
HEAD_AT = dict(R=(186.0, 262.0), L=(204.0, 262.0), r=(190.0, 262.0), l=(200.0, 262.0), F=(195.0, 262.0))   # 顔の 向きごとの 頭の まん中（画面）


def T(cx, cy, s, inner, ox=80.0, oy=48.0, flip=False):
    """壁紙の ポニーの 座標（頭の まん中 ox, oy）→ 画面の (cx, cy) に s 倍（flip：左右 うらがえし）"""
    sx = -s if flip else s
    return f'<g transform="translate({f(cx)} {f(cy)}) scale({f(sx)} {f(s)}) translate({f(-ox)} {f(-oy)})">{inner}</g>'


def gloss_curls(curls):
    """たてがみの くるくるに つやの 白い すじ"""
    o = ''
    for cx, cy, r in curls:
        o += path(f'M{f(cx - r * .55)} {f(cy - r * .35)} Q{f(cx - r * .2)} {f(cy - r * .8)} {f(cx + r * .3)} {f(cy - r * .62)}',
                  fill='none', stroke='#FFFFFF', stroke_width=f(max(1.0, r * .18)), stroke_linecap='round', opacity='.85')
    return o


SIDE_CURLS = ((60, 25, 11), (53, 37, 11), (51, 51, 10), (55, 63, 8), (71, 17, 9), (96, 26, 7.5))
FRONT_CURLS = ((54, 28, 10), (49, 40, 10.5), (49, 52, 10), (54, 63, 8), (72, 18, 8.5), (87, 17, 8))
TQ_CURLS = ((52, 28, 10), (46, 40, 10.5), (46, 52, 10), (50, 63, 8), (65, 17, 8.5), (79, 14, 7.5))


def head_side():
    """横向きの頭（右向き）：壁紙の ポニーの 頭（首は 描かない）＋ たてがみの つや"""
    head = smooth(ellipse_pts(80, 48, 31, 27, 14))
    snout = smooth(ellipse_pts(105, 60, 18, 14, 12, rot=8))
    return (outlined([head, snout], '#FFFFFF', LINE, 2.2) + C.pony_face_side() + C.pony_mane() + gloss_curls(SIDE_CURLS[:5])
            + C.pony_ears())


def head_front():
    """正面の頭：壁紙の こっちを向いた 顔（首は 描かない）＋ たてがみの つや"""
    head = smooth(ellipse_pts(80, 47, 30, 27, 14))
    muzzle = smooth(ellipse_pts(80, 63, 16, 11.5, 12))
    out = outlined([head, muzzle], '#FFFFFF', LINE, 2.2)
    out += path(smooth(ellipse_pts(80, 64, 12.5, 8.6, 12)), fill='#FFE4EE')
    out += '<ellipse cx="75.6" cy="62.4" rx="1.7" ry="2.3" fill="#C0607F"/><ellipse cx="84.4" cy="62.4" rx="1.7" ry="2.3" fill="#C0607F"/>'
    out += path('M75.5 68.2 q2.25 2.6 4.5 0 q2.25 2.6 4.5 0', fill='none', stroke=LINE, stroke_width='1.6', stroke_linecap='round', stroke_linejoin='round')
    out += '<ellipse cx="63" cy="57" rx="5.8" ry="3.5" fill="#FF9FC4" opacity=".85"/><ellipse cx="97" cy="57" rx="5.8" ry="3.5" fill="#FF9FC4" opacity=".85"/>'
    for ex, side in ((68.5, -1), (91.5, 1)):
        out += C.front_eye(ex, 45, side)
    out += C.pony_mane(FRONT_CURLS, ((54, 28, 4.6), (49, 40, 4.8), (49, 52, 4.5), (72, 18, 3.8))) + gloss_curls(FRONT_CURLS[:5])
    out += C.pony_ears((((59, 27), (55, 5), (70, 19)), ((101, 27), (105, 5), (90, 19))),
                       (((61, 22), (58, 10), (67, 18)), ((99, 22), (102, 10), (93, 18))), bow_at=(64, 14))
    return out


def eye_tq(ex, ey, k=1.0):
    """ななめの顔の 目（k：はばの ちぢみ。向こうの目は 細く）。まつげは 右（顔の 向く方）"""
    rx = 6.8 * k
    lash = f'M{f(ex + rx * .82)} {f(ey - 6.2)} l{f(4 * k)} -3.2 M{f(ex + rx * 1.03)} {f(ey - 3.2)} l{f(4.6 * k)} -1.6'
    return (f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(rx)}" ry="8.8" fill="#3A1F2B"/>'
            f'<ellipse cx="{f(ex + .4 * k)}" cy="{f(ey + 2.8)}" rx="{f(5 * k)}" ry="5" fill="#7A3C5C" opacity=".8"/>'
            f'<circle cx="{f(ex + 2.2 * k)}" cy="{f(ey - 4.2)}" r="{f(2.7 * min(1, k + .15))}" fill="#fff"/><circle cx="{f(ex - 2.2 * k)}" cy="{f(ey + 4.4)}" r="1.3" fill="#fff"/>'
            + path(lash, fill='none', stroke='#3A1F2B', stroke_width='1.7', stroke_linecap='round'))


def eye_wink(ex, ey):
    """ウィンクの 目（とじて にっこり：上に まるい 線 ＋ まつげ）"""
    return path(f'M{f(ex - 7)} {f(ey + 1.5)} Q{f(ex)} {f(ey - 7.5)} {f(ex + 7)} {f(ey + 1.5)}', fill='none', stroke='#3A1F2B', stroke_width='2.6',
                stroke_linecap='round') + path(f'M{f(ex + 6.2)} {f(ey - 1.6)} l4.4 -2.6 M{f(ex + 7)} {f(ey + 1.6)} l4.8 -.4', fill='none', stroke='#3A1F2B',
                                               stroke_width='1.7', stroke_linecap='round')


def head_tq(wink=False):
    """ななめ（右に少し むいた）頭：手前の目（ポニーの 右目）は まん中より 左・向こうの目は 細く 右の ふち・鼻先は 右へ。
       wink：手前の目を ウィンクに（左右 うらがえすと ポニーの 左目＝まさちゃんの「左目ウィンク」）"""
    head = smooth(ellipse_pts(80, 47, 29.5, 27, 14))
    muzzle = smooth(ellipse_pts(89, 63, 15.5, 11.2, 12, rot=-4))
    out = outlined([head, muzzle], '#FFFFFF', LINE, 2.2)
    out += path(smooth(ellipse_pts(89.5, 64, 12, 8.2, 12, rot=-4)), fill='#FFE4EE')
    out += '<ellipse cx="85" cy="62.2" rx="1.7" ry="2.3" fill="#C0607F"/><ellipse cx="95" cy="61.6" rx="1.4" ry="2.2" fill="#C0607F"/>'
    out += path('M84.6 68 q2.25 2.6 4.5 0 q2.1 2.4 4.2 -.2', fill='none', stroke=LINE, stroke_width='1.6', stroke_linecap='round', stroke_linejoin='round')
    out += '<ellipse cx="65" cy="57" rx="6" ry="3.5" fill="#FF9FC4" opacity=".85"/><ellipse cx="102" cy="56.4" rx="3.6" ry="3.2" fill="#FF9FC4" opacity=".8"/>'
    out += eye_wink(72, 45) if wink else eye_tq(72, 45)
    out += eye_tq(96.5, 45, .74)
    out += C.pony_mane(TQ_CURLS, ((52, 28, 4.6), (46, 40, 4.8), (46, 52, 4.5), (65, 17, 3.8))) + gloss_curls(TQ_CURLS[:5])
    out += C.pony_ears((((56, 27), (51, 5), (67, 19)), ((92, 25), (98, 4), (85, 18))),
                       (((58, 22), (55, 10), (64, 18)), ((91, 21), (96, 10), (88, 18))), bow_at=(60, 13))
    return out


def head_svg(face):
    """face：R＝右向き・L＝左向き・r＝やや右・l＝やや左（ウィンク）・F＝正面。頭の 絵は shared_defs の pmHS・pmHT・pmHW・pmHF を 使う"""
    hx, hy = HEAD_AT[face]
    ref, oy, flip = dict(R=('pmHS', 48, False), L=('pmHS', 48, True), r=('pmHT', 47, False), l=('pmHW', 47, True), F=('pmHF', 47, False))[face]
    sx = -S_HEAD if flip else S_HEAD
    return f'<use href="#{ref}" transform="translate({f(hx)} {f(hy)}) scale({f(sx)} {f(S_HEAD)}) translate(-80 -{oy})"/>'


def heart_box(cx, cy, s):
    """art.heart の 形の だいたいの はば・高さ（画面）：(x0, y0, x1, y1)"""
    return cx - 1.0 * s, cy - .92 * s, cx + 1.0 * s, cy + 1.0 * s


def frill(cx, cy, w, n=5, col='#FFB3CF'):
    """くつ下の フリル（よこに ならんだ まるい なみ）"""
    r = w / n / 2
    o = ''.join(f'<circle cx="{f(cx - w / 2 + r + i * 2 * r)}" cy="{f(cy)}" r="{f(r * 1.25)}" fill="{col}" stroke="{LINE}" stroke-width="2.4"/>' for i in range(n))
    return o + f'<rect x="{f(cx - w / 2 + 1)}" y="{f(cy - r * .2)}" width="{f(w - 2)}" height="{f(r * 1.3)}" fill="{col}"/>'


def pony_tail():
    """しっぽ（くるくる）：ハートの 下の 左の よこから 出て 下へ たれる（右は 左右 うらがえし）"""
    cx, cy = HEART_C
    side = -1
    tx, ty = cx + side * 132, cy + 40
    curls = [(tx, ty, 25), (tx + side * 22, ty + 22, 24), (tx + side * 30, ty + 50, 22), (tx + side * 22, ty + 76, 19), (tx + side * 4, ty + 94, 15)]
    out = outlined([smooth(ellipse_pts(x, y, r, r, 12)) for x, y, r in curls], PINK, LINE, 2.6)
    for x, y, r in curls[1:4]:
        out += path(smooth(ellipse_pts(x + 1.5, y + 1.5, r * .45, r * .32, 8)), fill='none', stroke=LINE, stroke_width='2.2', opacity='.5')
    return out + gloss_curls(curls)


def pony_legs():
    """うしろ足：ハートの とがった所の 左右から 下へ（白い 足・ピンクの フリルの くつ下・ピンクの ひづめ）"""
    cx, cy = HEART_C
    out = ''
    for lx, fx in ((cx - 44, cx - 50), (cx + 44, cx + 50)):
        leg = limb([(lx, cy + 70), (fx, cy + 196)], [50, 46])
        out += outlined([leg], '#FFFFFF', LINE, 2.8)
        out += frill(fx, cy + 180, 52, 6)
        out += outlined([smooth([(fx - 25, cy + 190), (fx + 25, cy + 190), (fx + 26, cy + 212), (fx - 26, cy + 212)])], '#FFB3CF', LINE, 2.6)
        out += path(f'M{f(fx - 16)} {f(cy + 197)} L{f(fx + 16)} {f(cy + 197)}', fill='none', stroke='#FFFFFF', stroke_width='3', stroke_linecap='round', opacity='.7')
    return out


def pony_torso(face):
    """体（肩）と 首：ひとまとまりで ふちどり（首は 頭の 下から ハートの うしろへ）"""
    hx, hy = HEAD_AT[face]
    cx, cy = HEART_C
    nx = hx + (-12 if face == 'R' else 12 if face == 'L' else -4 if face == 'r' else 4 if face == 'l' else 0)
    torso = smooth(ellipse_pts(cx, cy - 118, 104, 58, 16))
    neck = limb([(nx, hy + 30), ((nx + cx) / 2, cy - 150), (cx, cy - 100)], [74, 80, 90], cap=False)
    return outlined([torso, neck], '#FFFFFF', LINE, 2.8)


def pony_hooves():
    """ハートの 上の ふちに かけた 前足（ハートの 前）"""
    cx, cy = HEART_C
    out = ''
    for side in (-1, 1):
        x0, y0 = cx + side * 80, cy - 150          # 肩（体の 上・ハートの うしろ）
        x1, y1 = cx + side * 100, cy - 112         # ひづめ（ハートの 前）
        leg = limb([(x0, y0), (x1, y1)], [42, 38])
        out += outlined([leg], '#FFFFFF', LINE, 2.8)
        hoof = smooth(ellipse_pts(x1 + side * 1, y1 + 12, 23, 15, 12, rot=side * 10))
        out += outlined([hoof], '#FFB3CF', LINE, 2.6)
        out += path(f'M{f(x1 - 10)} {f(y1 + 10)} Q{f(x1)} {f(y1 + 4)} {f(x1 + 10)} {f(y1 + 10)}', fill='none', stroke=LINE, stroke_width='2', opacity='.5')
    return out


def big_heart(cx, cy, s, key):
    """つやつやの 大きな ハート（ふち：ピンク・中：パステルの 虹と 白い 光・つや・キラキラ）。key：グラデーションの id の 頭"""
    defs = (f'<linearGradient id="{key}r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8CC4"/><stop offset=".55" stop-color="#FF4F9A"/>'
            f'<stop offset="1" stop-color="#E02F7E"/></linearGradient>'
            f'<linearGradient id="{key}i" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFD6EC"/><stop offset=".25" stop-color="#FFE7C9"/>'
            f'<stop offset=".45" stop-color="#FFF6C4"/><stop offset=".62" stop-color="#D9F7DE"/><stop offset=".8" stop-color="#D6EEFF"/><stop offset="1" stop-color="#E9DBFF"/></linearGradient>'
            f'<radialGradient id="{key}w" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".55" stop-color="#FFFFFF" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>')
    out = path(heart(cx, cy + 8, s * 1.0), fill='#B8336E', opacity='.25')
    out += path(heart(cx, cy, s), fill=f'url(#{key}r)', stroke=LINE, stroke_width='6', stroke_linejoin='round')
    out += path(heart(cx, cy + s * .035, s * .84), fill=f'url(#{key}i)')
    out += path(heart(cx, cy + s * .035, s * .84), fill=f'url(#{key}w)')
    out += path(heart(cx, cy + s * .035, s * .84), fill='none', stroke='#FFFFFF', stroke_width='3', opacity='.9')
    # つや：左上の 大きい 光・右上の 小さい 光
    out += path(f'M{f(cx - s * .72)} {f(cy - s * .3)} Q{f(cx - s * .72)} {f(cy - s * .74)} {f(cx - s * .38)} {f(cy - s * .79)}', fill='none', stroke='#FFFFFF',
                stroke_width=f(s * .07), stroke_linecap='round', opacity='.9')
    out += f'<circle cx="{f(cx - s * .82)} " cy="{f(cy - s * .12)}" r="{f(s * .035)}" fill="#FFFFFF" opacity=".9"/>'
    out += path(f'M{f(cx + s * .42)} {f(cy - s * .8)} Q{f(cx + s * .62)} {f(cy - s * .84)} {f(cx + s * .74)} {f(cy - s * .66)}', fill='none', stroke='#FFFFFF',
                stroke_width=f(s * .045), stroke_linecap='round', opacity='.8')
    rnd = random.Random(7)
    for _ in range(14):
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(.25, .7)
        x, y = cx + math.cos(a) * r * s * .78, cy - s * .12 + math.sin(a) * r * s * .55
        out += path(sparkle(x, y, rnd.uniform(3, 7)), fill='#FFFFFF', opacity=f'{rnd.uniform(.6, 1):.2f}')
    return defs, out


def shared_defs():
    """①〜⑤ で 同じ 絵（ハート・前足・うしろ足・しっぽ・頭 4つ）：かくした <svg> の defs に 1回だけ 入れて <use> で 使う"""
    cx, cy = HEART_C
    hd, hb = big_heart(cx, cy, HEART_S, 'pmH')
    return (f'<svg class="pmdefs" width="0" height="0" aria-hidden="true"><defs>{hd}<g id="pmHt">{hb}</g><g id="pmHv">{pony_hooves()}</g>'
            f'<g id="pmLg">{pony_legs()}</g><g id="pmTl">{pony_tail()}</g><g id="pmHS">{head_side()}</g><g id="pmHT">{head_tq()}</g>'
            f'<g id="pmHW">{head_tq(wink=True)}</g><g id="pmHF">{head_front()}</g></defs></svg>')


def screen_art(text, face, key, s_txt=1.32):
    """1文字の 画面の 絵：ポニーが 字の 書いてある ハートを だく（390×844 の 画面。まん中に いる時）。shared_defs と いっしょに 使う"""
    cx, cy = HEART_C
    defs = rainbow_grad(key + 't', cy - 50 * s_txt - 10, cy + 50 * s_txt + 10)
    tail = '<use href="#pmTl"/>' if face in 'RrF' else f'<use href="#pmTl" transform="translate({f(2 * cx)} 0) scale(-1 1)"/>'
    body = (tail + '<use href="#pmLg"/>' + pony_torso(face) + '<use href="#pmHt"/>' + word_svg(text, cx, cy - 6, s_txt, key + 't', w=17)
            + '<use href="#pmHv"/>' + head_svg(face))
    return defs, body


# ---------------------------------------------------------------- 動き（タップした 瞬間が 0秒）
# 点めつ（1秒に 3回まで）の ために：落ちている ハートは 空と 同じ 明るさの パステル（色だけ ちがう）で、つもった 時に ふちと つやが つく。
# 先に つもった ハートほど 前に かさねる（あとから 落ちる ハートは うしろを とおる）。①〜⑤と 最後の ハートは 白い 光の 形で 入ってきて、止まる 時に 色が つく
PC_T = dict(FILL=2.4,                   # ハートが 画面 いっぱいに つもる（0〜2.4）
            BURST=2.48, CHAIN=.16,      # ハートが まん中から 外へ じゅんに はじける（2.48〜2.64 に はじけはじめ・1つ 0.22秒）
            W=(2.66, 2.78, 2.92, 3.32),  # 白い 光：明るくなりはじめ・いちばん 明るい・ここまで・消える
            BG=2.84,                    # 白い 光の 中で ピンクの 画面に かわる
            S=(3.0, 4.2, 5.4, 6.6, 7.8),   # ①〜⑤ の 画面（1つ 1.2秒）
            IN=.45, OUT=.12,           # 入ってくる・消える（つぎの 画面の 前）
            FIN=9.0,                    # 大きな ハートの ど的中
            RES=10.9)                   # ハートが 上へ・ボード
# ①〜⑤：(字, 顔の 向き, 入ってくる 方, 字の 大きさ)。顔：R＝右・L＝左・r＝やや右・l＝やや左（ウィンク）・F＝正面。方：L＝左から・R＝右から・B＝下から・T＝上から・C＝まん中に 出る
SCREENS = (('ど！', 'R', 'L', 1.32), ('て！', 'L', 'R', 1.32), ('き！', 'r', 'B', 1.32), ('ちゅ！', 'l', 'T', 1.1), ('う！', 'F', 'C', 1.32))
FIN_C, FIN_S = (195.0, 415.0), 165.0     # 大きな ハートの まん中と 大きさ
TITLE_Y, TITLE_K = 112.0, .48            # ボードの 上に 動いた ハートの まん中と 大きさ
UP_VEIL = (.12, .77)                     # 上へ 動く 前に 白く なりはじめる（RES の 0.12秒 前）・白い 光の 長さ（動く 0.5秒の あと 0.15秒で 色が もどる）
PILE_COLS = (('#FF6FA8', LINE), ('#FF8DC0', LINE), ('#FFB7D3', LINE), ('#FF4F9A', LINE), ('#FFFFFF', LINE), ('#FFD3E5', LINE))
RAIN_BG = ('#DBC9FC', '#D7C2FC')        # ハートが 降る 空（ラベンダー：まん中・はし。相対輝度 0.64・0.60）
FLY_COLS = ('#FFBCD8', '#FFBDCD', '#FFC0B6', '#FBB8FB', '#FFBADD')   # 落ちている ハート（ピンク・ローズ・コーラル・オーキッド・ホットピンク。どれも 相対輝度 0.62 前後）


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def heart_uri(fill, line, gloss=True):
    """ハートの 絵（CSS の 背景）"""
    d = heart(0, 0, 1)
    gl = ("<path d='M-.62 -.42 Q-.6 -.78 -.28 -.8' fill='none' stroke='%23FFFFFF' stroke-width='.13' stroke-linecap='round' opacity='.85'/>" if gloss else '')
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1.12 -1.08 2.24 2.24'><path d='{d}' fill='{fill.replace('#', '%23')}' stroke='{line.replace('#', '%23')}' "
           f"stroke-width='.09' stroke-linejoin='round'/>{gl}</svg>")
    return f'url("data:image/svg+xml,{svg}")'


def fly_uri(fill):
    """落ちている ハートの 絵：ふちなし・うすい つや（空と 明るさの 差が 0.1 より 小さい）"""
    d = heart(0, 0, 1)
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1.12 -1.08 2.24 2.24'><path d='{d}' fill='{fill.replace('#', '%23')}'/>"
           "<path d='M-.62 -.42 Q-.6 -.78 -.28 -.8' fill='none' stroke='%23FFFFFF' stroke-width='.13' stroke-linecap='round' opacity='.15'/></svg>")
    return f'url("data:image/svg+xml,{svg}")'


def pile(seed=11, W=390, H=844):
    """つもる ハート [(x, y（まん中）, s（はばの 半分）, 色, 回る角度 …)]。下から 順に つもる（つもる 順）。画面の いちばん ひくい 所が 上の はしを こえるまで"""
    rnd = random.Random(seed)
    step = 6
    cols = W // step + 1
    top = [H + 16.0] * cols
    out = []
    while max(top) > -28:
        s = rnd.uniform(22, 38)
        lo = max(range(cols), key=lambda c: top[c] + rnd.uniform(0, 70))     # ひくい 所（top が 大きい）に 落ちやすい
        x = min(W + s * .2, max(-s * .2, lo * step + rnd.uniform(-s * .6, s * .6)))
        c0, c1 = max(0, int((x - s * .85) // step)), min(cols - 1, int((x + s * .85) // step))
        under = top[c0:c1 + 1]
        base = (min(under) + sum(under) / len(under)) / 2
        yc = base + s * .05
        for c in range(c0, c1 + 1):
            u = min(1.0, abs(c * step - x) / (s * .85))
            top[c] = min(top[c], yc - s * (.8 - .3 * u * u))
        out.append(dict(x=x, y=yc, s=s, k=rnd.randrange(len(PILE_COLS)), r0=rnd.uniform(-40, 40), r1=rnd.uniform(-18, 18)))
    return out


BURST_C = (195.0, 422.0)                 # はじける まん中


def pile_html(seed=11, g=3000.0):
    """つもる ハート（外の i：はじける・中の b：落ちる うすい ハート・b::after：つもった ハート（ふち・つや））。
       先に つもった ハートほど あと（前）に 書く：あとから 落ちる ハートは つもった ハートの うしろを とおる"""
    hs = pile(seed)
    rnd = random.Random(seed + 1)
    n = len(hs)
    t_first, t_last = .62, PC_T['FILL']
    items = []
    for i, h in enumerate(hs):
        land = t_first + (t_last - t_first) * (i / max(1, n - 1)) ** .9
        y0 = min(-h['s'] * 1.3 - rnd.uniform(0, 140), h['y'] - h['s'] * 2.4 - 40)     # 画面の 上の 外から
        dist = h['y'] - y0
        tf = math.sqrt(2 * dist / g)
        d = max(0.0, land - tf)
        tf = land - d
        dx, dy = h['x'] - BURST_C[0], h['y'] - BURST_C[1]
        L = math.hypot(dx, dy) or 1
        k = rnd.uniform(10, 34)
        bx, by = dx / L * k, dy / L * k
        bd = PC_T['BURST'] + PC_T['CHAIN'] * min(1.0, L / 480) + rnd.uniform(0, .02)
        items.append(f'<i class="pm{h["k"]}" style="left:{h["x"] - h["s"] * 1.12:.1f}px;top:{h["y"] - h["s"] * 1.08:.1f}px;width:{h["s"] * 2.24:.1f}px;height:{h["s"] * 2.24:.1f}px;'
                     f'--y0:{y0 - h["y"]:.0f}px;--t:{tf:.2f}s;--d:{d:.2f}s;--l:{max(0.0, land - .02):.2f}s;--r0:{h["r0"]:.0f}deg;--r1:{h["r1"]:.0f}deg;'
                     f'--bx:{bx:.0f}px;--by:{by:.0f}px;--br:{rnd.uniform(-25, 25):.0f}deg;--bd:{bd:.2f}s"><b class="pf{rnd.randrange(len(FLY_COLS))}"></b></i>')
    return ''.join(reversed(items)), n


def pop_hearts(x, y, d, n, seed, dist=(90, 160), size=(14, 26)):
    """着いた時に まわりへ とびちる 小さな ハート"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        r = rnd.uniform(*dist)
        s = rnd.uniform(*size)
        o += (f'<i class="pm{rnd.randrange(len(PILE_COLS))}" style="left:{x - s / 2:.0f}px;top:{y - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;'
              f'--dx:{math.cos(a) * r:.0f}px;--dy:{math.sin(a) * r:.0f}px;--d:{sec(d + rnd.uniform(0, .05))};--r:{rnd.uniform(-90, 90):.0f}deg"></i>')
    return o


def rising_hearts(n, seed, t0):
    """下から 上へ のぼって 消える 細かい ハート（いつまでも）"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        s = rnd.uniform(7, 17)
        dur = rnd.uniform(2.2, 3.8)
        o += (f'<i class="pm{rnd.choice((0, 1, 2, 4, 5))}" style="left:{rnd.uniform(4, 386) - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;'
              f'--t:{dur:.2f}s;--d:{t0 + rnd.uniform(-dur * .6, 1.6):.2f}s;--w:{rnd.uniform(-26, 26):.0f}px"></i>')
    return o


def twinkles(n, seed, box=(10, 60, 380, 800)):
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        x, y, r = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3]), rnd.uniform(5, 12)
        o += path(sparkle(x, y, r), fill='#FFFFFF', style=f'animation-duration:{rnd.uniform(1.1, 2.1):.2f}s;animation-delay:-{rnd.uniform(0, 2):.2f}s')
    return o


def final_art():
    """最後の 大きな ハート：ハートに つつまれた「ど的中」＋ 小さな ハート"""
    cx, cy = FIN_C
    hd, hb = big_heart(cx, cy, FIN_S, 'pmF')
    s_txt = .98
    defs = hd + rainbow_grad('pmFt', cy - 50 * s_txt - 14, cy + 50 * s_txt + 14)
    body = hb + word_svg('ど的中', cx - 4, cy - 4, s_txt, 'pmFt', w=14, gap=-6)
    hx, hy = cx + 124, cy - 84
    body += (path(heart(hx, hy + 3, 21), fill='#B8336E', opacity='.3') + path(heart(hx, hy, 21), fill='#FF4F9A', stroke=LINE, stroke_width='3.4', stroke_linejoin='round')
             + path(f'M{f(hx - 12)} {f(hy - 7)} Q{f(hx - 11)} {f(hy - 15)} {f(hx - 4)} {f(hy - 16)}', fill='none', stroke='#FFFFFF', stroke_width='3.4', stroke_linecap='round', opacity='.9'))
    return defs, body


def enter_anim(frm):
    return dict(L='pmInL', R='pmInR', B='pmInB', T='pmInT', C='pmInC')[frm]


def veil(gid, t, dur, more=''):
    """白い 光の 形（絵と 同じ 形の 白）：入ってくる 間は 絵を 白く つつみ、止まる 時に 消えて 色が つく（点めつ しない 入り方）。more：あとの 動き"""
    return f'<svg class="pmv" viewBox="0 0 390 844" aria-hidden="true" style="animation:pmVl {sec(dur)} linear {sec(t)} both{more}"><use href="#{gid}"/></svg>'


def pc_layers(board_html):
    """押したあと（下から）：ラベンダーの 空 → つもる ハート → ピンクの 画面（水玉・光の 筋・キラキラ）→ ①〜⑤ の ポニー（着いた時に ハートが とぶ）→
       最後の 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。board_html：テーマの ボード（gen_fx の board）"""
    T = PC_T
    hearts, n = pile_html()
    scr = ''
    S = T['S']
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        defs, body = screen_art(text, face, f'pm{i}', s_txt)
        t_in = S[i]
        t_out = (S[i + 1] if i + 1 < len(S) else T['FIN']) - T['OUT']
        land = t_in + T['IN'] * .72
        cx, cy = HEART_C
        scr += (f'<div class="pms" style="animation:{enter_anim(frm)} {sec(T["IN"])} cubic-bezier(.25,.9,.35,1) {sec(t_in)} both,pmOut {sec(T["OUT"])} linear {sec(t_out)} forwards">'
                f'<svg viewBox="0 0 390 844" aria-hidden="true"><defs>{defs}</defs><g id="pmG{i}">{body}</g></svg>{veil(f"pmG{i}", t_in, T["IN"])}</div>'
                f'<i class="pmr" style="--d:{sec(land)}"></i><div class="pml">{pop_hearts(cx, cy - 20, land, 14, 30 + i)}</div>')
    fdefs, fbody = final_art()
    fx, fy = FIN_C
    bx, by = BURST_C
    return f'''{shared_defs()}<div class="pmbg"></div>
    <div class="pmp" aria-hidden="true">{hearts}</div>
    <div class="pml pmlb">{pop_hearts(bx, by, T['BURST'], 20, 23, dist=(170, 300), size=(16, 30))}</div>
    <div class="pmpk" aria-hidden="true"><i class="rays"></i><i class="glow"></i><svg class="spk" viewBox="0 0 390 844">{twinkles(22, 5)}</svg></div>
    {scr}
    <div class="pmu" aria-hidden="true">{rising_hearts(40, 9, T['FIN'])}</div>
    <div class="pmf"><svg viewBox="0 0 390 844" aria-hidden="true"><defs>{fdefs}</defs><g id="pmFG">{fbody}</g></svg>{veil("pmFG", T["FIN"], .5, f",pmVu {sec(UP_VEIL[1])} linear {sec(T['RES'] - UP_VEIL[0])} forwards")}</div>
    <i class="pmr pmrf" style="--d:{sec(T['FIN'] + .28)}"></i><div class="pml">{pop_hearts(fx, fy - 10, T['FIN'] + .28, 18, 47, dist=(130, 210))}</div>
    <div class="hb">{board_html}</div>
    <div class="pmw" aria-hidden="true"></div>
    <p class="sr">プレミアムど的中！ハートが いっぱいに つもって はじけ、ハートを だいた ポニーが ど・て・き・ちゅ・う と 1文字ずつ 出てきて、さいごに ハートに つつまれた ど的中</p>'''


PILE_CSS = ''.join(f'.ov.pm .pm{k}{{background:{heart_uri(c, l)} center/contain no-repeat}}' for k, (c, l) in enumerate(PILE_COLS))


def pc_css():
    T = PC_T
    w0, w1, w2, w3 = T['W']
    wd = w3 - w0
    fy = FIN_C[1]
    return PILE_CSS + f'''
/* ---------- プレミアムど的中（かわいいど的中）：premium_cute.py ---------- */
.ov.fz.pm{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
.ov.pm .pmbg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 44%,{RAIN_BG[0]},{RAIN_BG[1]} 70%)}}
/* つもる ハート：外の i＝はじける（{sec(T['BURST'])}〜・まん中から じゅんに）・中の b＝上から 落ちる うすい ハート・b::after＝つもった時に つく ふちと つや */
.ov.pm .pmp{{position:absolute;inset:0;z-index:2;pointer-events:none}}
.ov.pm .pmp i{{position:absolute;display:block;background:none!important;animation:pmB .22s cubic-bezier(.2,.7,.3,1) var(--bd) forwards}}
.ov.pm .pmp b{{position:absolute;inset:0;transform:translateY(var(--y0)) rotate(var(--r0));animation:pmF var(--t) cubic-bezier(.333,0,.667,.333) var(--d) both}}
.ov.pm .pmp b::after{{content:'';position:absolute;inset:0;opacity:0;animation:pmL .14s linear var(--l) forwards}}
{''.join(f'.ov.pm .pmp .pf{j}{{background:{fly_uri(c)} center/contain no-repeat}}' for j, c in enumerate(FLY_COLS))}
{''.join(f'.ov.pm .pmp .pm{k} b::after{{background:{heart_uri(*PILE_COLS[k])} center/contain no-repeat}}' for k in range(len(PILE_COLS)))}
@keyframes pmF{{to{{transform:translateY(0) rotate(var(--r1))}}}}
@keyframes pmL{{to{{opacity:1}}}}
@keyframes pmB{{to{{transform:translate(var(--bx),var(--by)) scale(1.35) rotate(var(--br));opacity:0}}}}
.ov.pm .pmlb{{z-index:2}}
/* ピンクの 画面（白い 光の 中で かわる）：水玉・パステルの 光の 筋（ゆっくり 回る）・まん中の 光・キラキラ */
.ov.pm .pmpk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;
  background:radial-gradient(#FFFFFF 2.6px,transparent 3.2px) 0 0/22px 22px,radial-gradient(#FFFFFF 2.6px,transparent 3.2px) 11px 11px/22px 22px,linear-gradient(180deg,#FFC9DF,#FFE6F1 55%,#FFD3E5);
  animation:fzOn .01s linear {sec(T['BG'])} forwards}}
.ov.pm .pmpk .rays{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;opacity:.55;
  background:repeating-conic-gradient(rgba(255,255,255,.9) 0 6deg,rgba(255,255,255,0) 6deg 15deg,rgba(255,214,236,.8) 15deg 21deg,rgba(255,255,255,0) 21deg 30deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 10%,transparent 58%);mask-image:radial-gradient(circle,#000 0 10%,transparent 58%);animation:spin 30s linear infinite}}
.ov.pm .pmpk .glow{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.95),rgba(255,255,255,.5) 38%,rgba(255,255,255,0) 70%)}}
.ov.pm .pmpk .spk{{position:absolute;inset:0;width:390px;height:844px}}
.ov.pm .pmpk .spk path{{animation:pmTw 1.6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes pmTw{{from{{opacity:.25;transform:scale(.55)}}to{{opacity:1;transform:scale(1)}}}}
/* ①〜⑤：ハートを だいた ポニーが 左・右・下・上から 入ってくる／まん中に 出る（1つ {sec(T['S'][1] - T['S'][0])}） */
.ov.pm .pms{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:5;opacity:0;pointer-events:none;transform-origin:{HEART_C[0]:.0f}px {HEART_C[1]:.0f}px}}
.ov.pm .pms svg,.ov.pm .pmf svg{{position:absolute;inset:0;width:390px;height:844px;overflow:visible}}
@keyframes pmInL{{0%{{opacity:1;transform:translateX(-440px) rotate(-7deg)}}72%{{transform:translateX(8px) rotate(1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInR{{0%{{opacity:1;transform:translateX(440px) rotate(7deg)}}72%{{transform:translateX(-8px) rotate(-1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInB{{0%{{opacity:1;transform:translateY(760px)}}72%{{transform:translateY(-14px)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInT{{0%{{opacity:1;transform:translateY(-840px)}}72%{{transform:translateY(6px) scale(1.02,.98)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInC{{0%{{opacity:0;transform:scale(.15)}}55%{{opacity:1;transform:scale(1.13)}}78%{{transform:scale(.95)}}100%{{opacity:1;transform:none}}}}
@keyframes pmOut{{from{{opacity:1}}to{{opacity:0}}}}
/* 白い 光の 形：入ってくる 間は 白く つつみ（0.92）、止まる 前に 消えて 色が つく */
.ov.pm .pmv{{position:absolute;inset:0;width:390px;height:844px;overflow:visible;filter:brightness(0) invert(1);opacity:0;pointer-events:none}}
@keyframes pmVl{{0%,62%{{opacity:.92}}100%{{opacity:0}}}}
/* 最後の ハートが 上へ 動く 間も 白く つつむ（{sec(T['RES'] - UP_VEIL[0])}〜） */
@keyframes pmVu{{0%{{opacity:0}}{UP_VEIL[0] / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}{(UP_VEIL[0] + .5) / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}100%{{opacity:0}}}}
/* 着いた時：白い 輪と 小さな ハートが とびちる */
.ov.pm .pmr{{position:absolute;z-index:4;left:{HEART_C[0] - 110:.0f}px;top:{HEART_C[1] - 130:.0f}px;width:220px;height:220px;border-radius:50%;border:8px solid #FFFFFF;
  box-shadow:0 0 16px rgba(255,120,190,.8),inset 0 0 12px rgba(255,120,190,.6);opacity:0;animation:pmRing .55s ease-out var(--d) both}}
.ov.pm .pmrf{{top:{fy - 120:.0f}px}}
@keyframes pmRing{{0%{{opacity:0;transform:scale(.3)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(2.1)}}}}
.ov.pm .pml{{position:absolute;inset:0;z-index:6;pointer-events:none}}
.ov.pm .pml i{{position:absolute;display:block;opacity:0;animation:pmPop .7s cubic-bezier(.15,.75,.35,1) var(--d) both}}
@keyframes pmPop{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}8%{{opacity:1}}70%{{opacity:1}}100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1) rotate(var(--r))}}}}
/* 最後：大きな ハートの ど的中（{sec(T['FIN'])}）→ {sec(T['RES'])} に 上へ 動いて ボード */
.ov.pm .pmf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;opacity:0;pointer-events:none;transform-origin:{FIN_C[0]:.0f}px {fy:.0f}px;
  animation:pmInC .5s cubic-bezier(.25,.9,.35,1) {sec(T['FIN'])} both,pmBeat .9s ease-in-out {sec(T['FIN'] + .5)} 2,pmUp .5s cubic-bezier(.3,.8,.3,1) {sec(T['RES'])} forwards}}
@keyframes pmBeat{{0%,100%{{transform:none}}20%{{transform:scale(1.06)}}40%{{transform:scale(.99)}}55%{{transform:scale(1.04)}}}}
@keyframes pmUp{{from{{opacity:1;transform:none}}to{{opacity:1;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.pm .pmu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {sec(T['FIN'])} forwards}}
.ov.pm .pmu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:pmRise var(--t) linear var(--d) infinite}}
@keyframes pmRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}50%{{transform:translate(var(--w),-440px)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.pm .hb{{z-index:8;animation:pmBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .12)} both}}
@keyframes pmBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.pm .pmw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:pmWhite {sec(wd)} linear {sec(w0)} forwards}}
@keyframes pmWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハートを 出さない。1秒 ラベンダー → ピンクの 画面と 上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.pm .pmp,.ov.pm .pms,.ov.pm .pmr,.ov.pm .pml,.ov.pm .pmu,.ov.pm .pmw,.ov.pm .pmpk .rays,.ov.pm .pmf .pmv{{display:none}}
  .ov.fz.pm{{--t0:1.9s}}
  .ov.pm .pmpk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.pm .pmpk .spk path{{animation:none!important}}
  .ov.pm .pmf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.pm .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
