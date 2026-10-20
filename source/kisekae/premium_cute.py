"""プレミアムど的中（かわいいど的中）：まさちゃんの指定
   「プレミアムど的中演出 発動条件、ど的中の6回に1回発動、ランダム
    ・かわいいど的中 かわいいの馬がひらがなを持っている絵で タップしたらハートが上から下に落ちて画面上に積もっていき、画面一杯になったら、ハートが弾ける演出、
    一瞬白い光に包まれてから でっかいハートの中に、ど！が書いてる そのハートを写真の馬が持っている！
    ①ど！、左から画面中央(馬顔右向き) ②て！、右から画面中央(馬顔左向き) ③き！、下から画面中央(馬顔やや右向き)
    ④ちゅ！❤️、上から画面中央(馬顔やや左向き、左目ウィンク) ⑤う！画面中央に出てくる(馬顔正面) 一文字づつの画面で演出
    最後に ど的中❤️、細かいハートのエフェクトが上に消えていき、大きなハートに包まれたど的中を画面中央に表示する で終わり」
   「かわいいのど的中ボタン限定ではなくて、ど的中ボタンのプレミアムだからどの壁紙使ってても、ど的中の6回に1回はこれが出るようにって意味だった。」
   → どの着せ替えでも ど的中の 6回に1回。最後の ボードは その着せ替えの ど的中の ボード（見本は ど的中と 同じ デフォルト＝牧場）
   「プレミアムど的中の、馬はこの画像の馬をモデルにして！ この画像も俺が作ったやつ！ 背景はこの写真のような虹色で！
    演出内で出てくるハートは、一つ一つもっとプルンプルンさせて光沢つけて！」
   - 絵は ぜんぶ 一から 作った形（SVG）。ポニーは まさちゃんが 作った 絵の ポニーを モデルに した（なぞっていない・絵は リポジトリに 入れない）：
     こい 赤の ふち・白い 体・つやつやの ピンクの くるくるの たてがみと しっぽ・大きな つやつやの リボン・大きな キラキラの 紫の 目（まん中に 星）・
     ピンクの ほお・ハートの 左右の ふちを つかむ まるい ひづめ。ハートは こい ピンクの ふちに 虹色の 星空・字は 虹色で こい 赤 → マゼンタ → うすい ピンクの ふち・濁点は つやつやの 玉
   - 背景は 写真のような 虹色（水色・黄緑・黄色・ピンク・紫）に さくら・花びら・光の 玉・小さな ハート。ハートは つやつやの ゼリーで、つもる 時・とぶ 時・のぼる 時・だいた ハートも ぷるんぷるん
   - 字（ど・て・き・ち・ゅ・う・！・的・中）は 太い まるい 線で 書いた 字（フォントを 使わない：GLYPHS）
   このファイルは 部品（絵と字）。動き（時刻・CSS）は 下の 方（PC_T・pc_layers・pc_css）・見本の 画面は gen_fx.py の fz_pc"""
import math
import random
from art import f, smooth, limb, ellipse_pts, heart, sparkle, path, g, outlined

# ---------------------------------------------------------------- 字（太い まるい 線で 書いた 字。100×100 の ます・y は下向き）
# 1つの字 ＝ (はば, [線…])。線 ＝ 点の 列（なめらかに つなぐ。同じ 点を 2回 ならべると 角）。点 1つ だけの 線は まるい 点
GLYPHS = {
    'ど': (104, [[(38, 14), (44, 46)],
                 [(76, 28), (58, 38), (40, 50), (30, 62), (29, 76), (38, 86), (56, 89), (78, 86)]]),
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
DAKU = {'ど': ((81, 13, 9.5), (96, 8, 9.5))}     # 濁点は つやつやの 玉（写真の「ど！」）：(x, y, 半径)。ますの 中


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
    """横に ならべた 字の 線・はば・濁点の 玉 [(x, y, 半径)]（cx, cy＝まん中・s＝1ます の px）"""
    adv = [advance(c) for c in text]
    total = (sum(adv) + gap * (len(text) - 1)) * s
    x = cx - total / 2
    d, balls = '', []
    for c, a in zip(text, adv):
        d += glyph_d(c, x, cy - 50 * s, s) + ' '
        balls += [(x + bx * s, cy - 50 * s + by * s, br * s) for bx, by, br in DAKU.get(c, ())]
        x += (a + gap) * s
    return d.strip(), total, balls


RAINBOW = (('0', '#FF4F86'), ('.17', '#FF9A3C'), ('.34', '#FFE53C'), ('.5', '#5FE07A'), ('.66', '#3CD2FF'), ('.82', '#4F7BFF'), ('1', '#A65CFF'))


def rainbow_grad(gid, y0, y1):
    stops = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in RAINBOW)
    return f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{f(y0)}" x2="0" y2="{f(y1)}">{stops}</linearGradient>'


# ---------------------------------------------------------------- 色と つやの 部品（まさちゃんの 写真の ポニーを モデルに：こい 赤の ふち・つやつやの ピンク）
OUT = '#A3233F'                                   # ふち（写真の こい 赤）
EYE_D = '#2A0723'                                 # 目の ふちと まつげ


def art_defs():
    """絵で 使う グラデーション（形の 大きさに あわせて のびる・<use> の 中でも 使える）"""
    return ('<radialGradient id="pmgC" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFD6E8"/><stop offset=".4" stop-color="#F59AC4"/>'
            '<stop offset=".78" stop-color="#E86BA5"/><stop offset="1" stop-color="#D9488B"/></radialGradient>'           # くるくる・リボン・濁点の 玉
            '<radialGradient id="pmgK" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFF3F8"/><stop offset=".55" stop-color="#FFC9E0"/>'
            '<stop offset="1" stop-color="#F59CC4"/></radialGradient>'                                                        # ひづめ・耳の 中・くつ下
            '<radialGradient id="pmgH" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#FFE6F1"/><stop offset=".5" stop-color="#F8B2D0"/>'
            '<stop offset="1" stop-color="#E77FB0"/></radialGradient>'                                                        # ひづめ
            '<linearGradient id="pmgE" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A0723"/><stop offset=".42" stop-color="#5E1452"/>'
            '<stop offset=".78" stop-color="#B53A86"/><stop offset="1" stop-color="#F07CB8"/></linearGradient>'               # 目（上が こい 紫・下が マゼンタ）
            '<radialGradient id="pmgW" cx=".42" cy=".36" r=".72"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".78" stop-color="#FFFFFF"/>'
            '<stop offset="1" stop-color="#F8E4EF"/></radialGradient>'                                                      # 白い 体（ふちが 少し ピンク）
            '<radialGradient id="pmgJ" cx=".36" cy=".32" r=".78"><stop offset="0" stop-color="#FFD0E6"/><stop offset=".55" stop-color="#FF62AB"/>'
            '<stop offset="1" stop-color="#DD3484"/></radialGradient>')                                                     # つやつやの ゼリーの ハート


def circ(cx, cy, r, n=16):
    return smooth(ellipse_pts(cx, cy, r, r, n))


def oval(cx, cy, rx, ry, rot=0, n=14):
    return smooth(ellipse_pts(cx, cy, rx, ry, n, rot=rot))


def curl(cx, cy, r, spin=1):
    """つやつやの くるくる（まいた ロールの 切り口）：ピンクの 玉・うずまきの みぞ・左上の 白い つや。spin：うずの 向き（1・-1）"""
    o = f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="url(#pmgC)" stroke="{OUT}" stroke-width="{f(max(2.8, r * .1))}"/>'
    pts = []
    for i in range(29):
        t = i / 28
        a = math.radians(spin * (150 + 420 * t))
        rr = r * (.1 + .64 * t)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = smooth(pts, closed=False)
    o += path(d, fill='none', stroke='#D24C8C', stroke_width=f(r * .15), stroke_linecap='round', opacity='.6')
    o += path(d, fill='none', stroke='#B8306E', stroke_width=f(r * .05), stroke_linecap='round', opacity='.55')
    o += path(f'M{f(cx - r * .7)} {f(cy - r * .02)} A{f(r * .7)} {f(r * .7)} 0 0 1 {f(cx - r * .1)} {f(cy - r * .7)}', fill='none',
              stroke='#FFFFFF', stroke_width=f(r * .17), stroke_linecap='round', opacity='.82')
    return o + f'<circle cx="{f(cx + r * .2)}" cy="{f(cy - r * .66)}" r="{f(r * .075)}" fill="#FFFFFF" opacity=".9"/>'


def ball(x, y, r, grad='pmgC'):
    """つやつやの 玉（濁点・リボンの まん中・ひづめ）"""
    hx, hy = x - r * .34, y - r * .36
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#{grad})" stroke="{OUT}" stroke-width="{f(max(2.0, r * .15))}"/>'
            f'<ellipse cx="{f(hx)}" cy="{f(hy)}" rx="{f(r * .34)}" ry="{f(r * .22)}" fill="#FFFFFF" opacity=".92" transform="rotate(-32 {f(hx)} {f(hy)})"/>'
            f'<circle cx="{f(x + r * .36)}" cy="{f(y + r * .34)}" r="{f(r * .1)}" fill="#FFFFFF" opacity=".75"/>')


def ear(b1, tip, b2, k=.3):
    """耳（白・中は うすい ピンク）：b1・b2＝つけね・tip＝先（ふくらみ k）"""
    cen = ((b1[0] + tip[0] + b2[0]) / 3, (b1[1] + tip[1] + b2[1]) / 3)

    def bulge(p, q, kk):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        vx, vy = mx - cen[0], my - cen[1]
        L = math.hypot(vx, vy) or 1
        dd = math.hypot(q[0] - p[0], q[1] - p[1])
        return mx + vx / L * dd * kk, my + vy / L * dd * kk

    def shape(p1, t, p2, kk):
        c1, c2 = bulge(p1, t, kk), bulge(t, p2, kk)
        return f'M{f(p1[0])} {f(p1[1])} Q{f(c1[0])} {f(c1[1])} {f(t[0])} {f(t[1])} Q{f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])} Z'

    lerp = lambda p, q, u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    bm = lerp(b1, b2, .5)
    i1, i2, it = lerp(lerp(b1, bm, .35), tip, .12), lerp(lerp(b2, bm, .35), tip, .12), lerp(tip, bm, .2)
    return (path(shape(b1, tip, b2, k), fill='url(#pmgW)', stroke=OUT, stroke_width='3.6', stroke_linejoin='round')
            + path(shape(i1, it, i2, k * .8), fill='url(#pmgK)'))


def bow(cx, cy, s=1.0, rot=0.0):
    """大きな つやつやの リボン：うしろに 下へ 広がる ひだの リボン・左右の ふくらんだ わ・まん中の 玉"""
    o = ''
    # ひだの リボン（下へ 広がる 5まい）
    for i in range(5):
        a0, a1 = math.radians(64 + i * 11), math.radians(64 + (i + 1) * 11)
        L = 46 - abs(i - 2) * 4
        p = [(math.cos(a0) * 10, math.sin(a0) * 10), (math.cos(a0) * L, math.sin(a0) * L), (math.cos(a1) * L, math.sin(a1) * L), (math.cos(a1) * 10, math.sin(a1) * 10)]
        d = f'M{f(p[0][0])} {f(p[0][1])} L{f(p[1][0])} {f(p[1][1])} Q{f((p[1][0] + p[2][0]) / 2)} {f((p[1][1] + p[2][1]) / 2 + 5)} {f(p[2][0])} {f(p[2][1])} L{f(p[3][0])} {f(p[3][1])} Z'
        o += path(d, fill=('#F48DBE' if i % 2 else '#FBB3D6'), stroke=OUT, stroke_width='2.2', stroke_linejoin='round')
    # 左右の わ
    for side in (-1, 1):
        pts = [(side * 6, -4), (side * 22, -26), (side * 44, -30), (side * 56, -14), (side * 54, 8), (side * 40, 22), (side * 20, 18), (side * 6, 8)]
        o += path(smooth(pts), fill='url(#pmgC)', stroke=OUT, stroke_width='3.2', stroke_linejoin='round')
        o += path(f'M{f(side * 14)} {f(-4)} Q{f(side * 30)} {f(-14)} {f(side * 42)} {f(-6)}', fill='none', stroke='#D24C8C', stroke_width='3', stroke_linecap='round', opacity='.65')
        o += path(f'M{f(side * 14)} {f(6)} Q{f(side * 28)} {f(14)} {f(side * 40)} {f(10)}', fill='none', stroke='#D24C8C', stroke_width='2.4', stroke_linecap='round', opacity='.5')
        o += path(f'M{f(side * 24)} {f(-22)} Q{f(side * 38)} {f(-26)} {f(side * 48)} {f(-16)}', fill='none', stroke='#FFFFFF', stroke_width='4', stroke_linecap='round', opacity='.8')
    o += ball(0, 0, 12)
    return g(o, transform=f'translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(s)})')


def eye(ex, ey, s=1.0, kx=1.0, side=1, wink=False):
    """大きな キラキラの 目：こい 紫 → 下が マゼンタ・まん中に 星・大きな 白い 光・まつげ 3本（side：まつげの 向き 1＝右・-1＝左）。
       kx：はばの ちぢみ（ななめの 顔の 向こうの 目）。wink：とじて にっこり"""
    s *= 1.22
    rx, ry = 15 * s * kx, 20 * s
    sw = 3.6 * s
    if wink:
        d = f'M{f(ex - rx * 1.2)} {f(ey + 3 * s)} Q{f(ex)} {f(ey - ry * .95)} {f(ex + rx * 1.2)} {f(ey + 3 * s)}'
        o = path(d, fill='none', stroke=EYE_D, stroke_width=f(4.4 * s), stroke_linecap='round')
        lx, ly = ex + side * rx * 1.15, ey + 1 * s
        o += path(f'M{f(lx)} {f(ly)} l{f(side * 8 * s)} {f(-5 * s)} M{f(lx - side * 4 * s)} {f(ly - 7 * s)} l{f(side * 7 * s)} {f(-8 * s)}',
                  fill='none', stroke=EYE_D, stroke_width=f(2.8 * s), stroke_linecap='round')
        return o
    o = f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#pmgE)" stroke="{EYE_D}" stroke-width="{f(2.4 * s)}"/>'
    o += f'<ellipse cx="{f(ex)}" cy="{f(ey + ry * .1)}" rx="{f(rx * .5)}" ry="{f(ry * .48)}" fill="#22051B" opacity=".7"/>'
    o += path(f'M{f(ex - rx * .74)} {f(ey + ry * .38)} Q{f(ex)} {f(ey + ry * 1.0)} {f(ex + rx * .74)} {f(ey + ry * .38)}', fill='none',
              stroke='#FF9BD0', stroke_width=f(2.6 * s), stroke_linecap='round', opacity='.85')
    o += path(sparkle(ex + rx * .04, ey + ry * .4, 4.6 * s), fill='#FFFFFF', opacity='.95')
    hk = min(1.0, kx + .2)
    o += f'<ellipse cx="{f(ex - side * rx * .28)}" cy="{f(ey - ry * .44)}" rx="{f(5.8 * s * hk)}" ry="{f(6.4 * s)}" fill="#FFFFFF"/>'
    o += f'<circle cx="{f(ex + side * rx * .42)}" cy="{f(ey + ry * .02)}" r="{f(2.3 * s * hk)}" fill="#FFFFFF"/>'
    # 上の まぶた（外がわが 少し 長い）と まつげ 3本（外へ はねる）
    x0, x1 = ex - side * rx * 1.0, ex + side * rx * 1.08
    o += path(f'M{f(x0)} {f(ey - ry * .26)} Q{f(ex - side * rx * .3)} {f(ey - ry * 1.2)} {f(x1)} {f(ey - ry * .44)}', fill='none',
              stroke=EYE_D, stroke_width=f(sw), stroke_linecap='round')
    for k, (u, ang, L) in enumerate(((.98, -18, 10), (.78, -42, 10), (.5, -66, 9))):
        bx = ex + side * rx * u
        by = ey - ry * (.5 + .45 * (1 - u))
        a = math.radians(ang)
        o += path(f'M{f(bx)} {f(by)} q{f(side * math.cos(a) * L * .5 * s)} {f(math.sin(a) * L * .2 * s)} {f(side * math.cos(a) * L * s)} {f(math.sin(a) * L * s)}',
                  fill='none', stroke=EYE_D, stroke_width=f(2.6 * s), stroke_linecap='round')
    return o


# ---------------------------------------------------------------- ポニー（まさちゃんの 写真の ポニーを モデルに。頭の まん中が (0, 0)・画面の 大きさ）
HEART_C, HEART_S = (195.0, 470.0), 150.0          # ハートの まん中と 大きさ（390×844 の 画面。ハートの はば＝2×HEART_S）
HEAD_AT = dict(R=(188.0, 266.0), L=(202.0, 266.0), r=(197.0, 266.0), l=(193.0, 266.0), F=(195.0, 266.0))   # 顔の 向きごとの 頭の まん中（画面）
HEAD_K = 1.25                                     # 頭の 大きさ（頭の 絵の 何倍）


def head_R():
    """横向き（右）の 頭：写真の ポニー。うしろに たてがみの くるくる・耳・白い 頭と 鼻先・大きな 目・ほお・前髪の くるくる・大きな リボン"""
    o = ''
    for x, y, r in ((-62, -58, 24), (-88, -22, 30), (-100, 22, 32), (-94, 66, 31), (-76, 104, 28), (-54, 134, 24)):
        o += curl(x, y, r)
    o += ear((-62, -42), (-76, -104), (-30, -64))
    o += outlined([circ(-8, -6, 74), oval(52, 24, 46, 36, rot=8)], 'url(#pmgW)', OUT, 2.2)
    o += path(oval(64, 41, 30, 15, rot=6), fill='#FFE1EE', opacity='.95')
    o += f'<ellipse cx="88" cy="20" rx="4" ry="5.6" fill="none" stroke="#E07AA8" stroke-width="2.4" transform="rotate(-12 88 20)"/>'
    o += path(oval(14, 36, 18, 11), fill='#FF9DC6', opacity='.62')
    o += eye(28, -4, 1.0, 1.0, 1)
    o += ear((-6, -66), (16, -124), (36, -58))
    o += curl(40, -58, 19, -1) + curl(-26, -70, 22)
    return o + bow(-34, -66, 1.0, -14)


def head_F():
    """正面の 頭：たてがみは 両がわ・目は 2つ（まつげは 外へ）・鼻先は 下・リボンは 左上"""
    o = ''
    for side in (-1, 1):
        for x, y, r in ((80, -34, 25), (96, 6, 30), (96, 50, 30), (82, 90, 27)):
            o += curl(side * x, y, r, side)
    o += ear((-62, -40), (-78, -108), (-28, -64)) + ear((62, -40), (78, -108), (28, -64))
    o += outlined([circ(0, -6, 74), oval(0, 38, 46, 32)], 'url(#pmgW)', OUT, 2.2)
    o += path(oval(0, 48, 34, 16), fill='#FFE1EE', opacity='.95')
    o += '<ellipse cx="-13" cy="40" rx="3.6" ry="5" fill="none" stroke="#E07AA8" stroke-width="2.2"/><ellipse cx="13" cy="40" rx="3.6" ry="5" fill="none" stroke="#E07AA8" stroke-width="2.2"/>'
    o += path(oval(-50, 26, 16, 10), fill='#FF9DC6', opacity='.62') + path(oval(50, 26, 16, 10), fill='#FF9DC6', opacity='.62')
    o += eye(-30, -6, .95, 1.0, -1) + eye(30, -6, .95, 1.0, 1)
    o += curl(24, -70, 20, -1) + curl(-2, -78, 18) + curl(-28, -68, 21)
    return o + bow(-42, -70, .9, -16)


def head_TQ(wink=False):
    """ななめ（右に 少し むいた）頭：手前の 目（ポニーの 右目）は まん中より 左で 大きく・向こうの 目は 細く 右・鼻先は 右下。
       wink：手前の 目を ウィンク（左右 うらがえすと ポニーの 左目＝まさちゃんの「左目ウィンク」）"""
    o = ''
    for x, y, r in ((-68, -50, 24), (-92, -14, 29), (-102, 28, 31), (-94, 70, 30), (-74, 106, 26)):
        o += curl(x, y, r)
    o += curl(76, -34, 17, -1)
    o += ear((-62, -40), (-78, -106), (-28, -64))
    o += outlined([circ(-4, -6, 74), oval(30, 32, 44, 33, rot=-4)], 'url(#pmgW)', OUT, 2.2)
    o += path(oval(36, 46, 32, 15, rot=-4), fill='#FFE1EE', opacity='.95')
    o += '<ellipse cx="20" cy="38" rx="3.4" ry="5" fill="none" stroke="#E07AA8" stroke-width="2.2"/><ellipse cx="45" cy="36" rx="3" ry="4.6" fill="none" stroke="#E07AA8" stroke-width="2.2"/>'
    o += path(oval(-40, 26, 17, 10.5), fill='#FF9DC6', opacity='.62') + path(oval(66, 22, 10, 8), fill='#FF9DC6', opacity='.55')
    o += eye(-20, -6, 1.0, 1.0, -1, wink=wink) + eye(40, -7, .95, .7, 1)
    o += ear((14, -66), (34, -120), (50, -52))
    o += curl(14, -74, 19, -1) + curl(-28, -70, 22)
    return o + bow(-46, -66, .95, -16)


def head_svg(face):
    """face：R＝右向き・L＝左向き・r＝やや右・l＝やや左（ウィンク）・F＝正面。頭の 絵は shared_defs の pmHS・pmHT・pmHW・pmHF を 使う"""
    hx, hy = HEAD_AT[face]
    ref, flip = dict(R=('pmHS', False), L=('pmHS', True), r=('pmHT', False), l=('pmHW', True), F=('pmHF', False))[face]
    return f'<use href="#{ref}" transform="translate({f(hx)} {f(hy)}) scale({f(-HEAD_K if flip else HEAD_K)} {f(HEAD_K)})"/>'


def pony_tail():
    """しっぽ（大きな つやつやの くるくる）：ハートの 左下の うしろ（右は 左右 うらがえし）"""
    return ''.join(curl(x, y, r, sp) for x, y, r, sp in ((80, 566, 24, 1), (94, 640, 26, -1), (48, 584, 31, 1), (30, 628, 32, -1), (60, 664, 30, 1)))


def pony_legs():
    """うしろ足：ハートの とがった所の 左右から 下へ（白い 足・ふわふわの ピンクの くつ下・ピンクの ひづめ）"""
    cx, cy = HEART_C
    o = ''
    for side in (-1, 1):
        x0, x1 = cx + side * 40, cx + side * 50
        o += outlined([limb([(x0, cy + 100), (x1, cy + 196)], [60, 58])], 'url(#pmgW)', OUT, 1.8)
        y = cy + 176
        sc = [(x1 - 33, y + 12), (x1 - 25, y), (x1 - 12, y + 6), (x1, y - 2), (x1 + 12, y + 6), (x1 + 25, y), (x1 + 33, y + 12), (x1 + 33, y + 30), (x1 - 33, y + 30)]
        o += path(smooth(sc), fill='url(#pmgK)', stroke=OUT, stroke_width='3', stroke_linejoin='round')
        o += path(smooth([(x1 - 30, y + 28), (x1 + 30, y + 28), (x1 + 32, y + 48), (x1 - 32, y + 48)]), fill='url(#pmgH)', stroke=OUT, stroke_width='3', stroke_linejoin='round')
        o += path(f'M{f(x1 - 18)} {f(y + 34)} L{f(x1 + 12)} {f(y + 34)}', fill='none', stroke='#FFFFFF', stroke_width='3.4', stroke_linecap='round', opacity='.75')
    return o


def pony_torso(face):
    """体と 首（白・ハートの うしろ）"""
    hx, hy = HEAD_AT[face]
    cx, cy = HEART_C
    torso = oval(cx, cy - 20, 126, 110, n=16)
    neck = limb([(hx, hy + 40), ((hx + cx) / 2, cy - 120), (cx, cy - 70)], [96, 104, 110], cap=False)
    return outlined([torso, neck], 'url(#pmgW)', OUT, 1.5)


def pony_arms():
    """前足（ハートの うしろから 左右の 外へ 出て、ハートの ふちを つかむ）"""
    cx, cy = HEART_C
    o = ''
    for side in (-1, 1):
        o += outlined([limb([(cx + side * 98, cy - 64), (cx + side * 146, cy - 46), (cx + side * 150, cy - 14)], [48, 46, 44])], 'url(#pmgW)', OUT, 1.8)
    return o


def pony_hooves():
    """ハートの 左右の ふちを つかむ まるい ひづめ（ハートの 前）"""
    cx, cy = HEART_C
    o = ''
    for side in (-1, 1):
        x, y = cx + side * 138, cy - 8
        o += ball(x, y, 25, 'pmgH')
        o += path(f'M{f(x - side * 6)} {f(y + 6)} q{f(side * 8)} {f(8)} {f(side * 18)} {f(4)}', fill='none', stroke='#E07AA8', stroke_width='2.2', stroke_linecap='round', opacity='.7')
    return o


def heart_poly(cx, cy, s, n=24):
    """art.heart と 同じ 形の 点（中かどうかを しらべる ため）"""
    P = lambda x, y: (cx + x * s, cy + y * s)
    segs = (((0, -.45), (-.15, -1.05), (-1.05, -1.0), (-1.0, -.25)), ((-1.0, -.25), (-.95, .3), (-.35, .62), (0, 1.0)),
            ((0, 1.0), (.35, .62), (.95, .3), (1.0, -.25)), ((1.0, -.25), (1.05, -1.0), (.15, -1.05), (0, -.45)))
    pts = []
    for p0, p1, p2, p3 in segs:
        for i in range(n):
            t = i / n
            u = 1 - t
            x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
            y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
            pts.append(P(x, y))
    return pts


def inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def big_heart(cx, cy, s, key):
    """つやつやの 大きな ハート（写真の ハート）：こい ピンクの ふち・中は 虹色の 星空と キラキラ・白い つや。key：グラデーションの id の 頭"""
    defs = (f'<radialGradient id="{key}r" cx=".3" cy=".22" r=".95"><stop offset="0" stop-color="#FFC1DF"/><stop offset=".4" stop-color="#FF64AA"/>'
            f'<stop offset=".78" stop-color="#EA2F8A"/><stop offset="1" stop-color="#C51A6C"/></radialGradient>'
            f'<linearGradient id="{key}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF62C8"/><stop offset=".2" stop-color="#FF9A55"/>'
            f'<stop offset=".35" stop-color="#FFEA52"/><stop offset=".5" stop-color="#78EB6E"/><stop offset=".64" stop-color="#3FD6FF"/>'
            f'<stop offset=".8" stop-color="#5877FF"/><stop offset="1" stop-color="#B05BFF"/></linearGradient>'
            f'<radialGradient id="{key}n" cx=".48" cy=".42" r=".6"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"/>'
            f'<stop offset=".55" stop-color="#FFFFFF" stop-opacity=".14"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{key}v" cx=".5" cy=".5" r=".55"><stop offset=".6" stop-color="#6A1488" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#5A0E78" stop-opacity=".4"/></radialGradient>')
    ic = (cx, cy + s * .05)
    inner = heart(ic[0], ic[1], s * .8)
    o = path(heart(cx, cy + 9, s), fill='#7A1840', opacity='.25')
    o += path(heart(cx, cy, s), fill=f'url(#{key}r)', stroke=OUT, stroke_width='6', stroke_linejoin='round')
    o += path(inner, fill=f'url(#{key}g)', stroke=OUT, stroke_width='3.4', stroke_linejoin='round')
    o += path(inner, fill=f'url(#{key}v)') + path(inner, fill=f'url(#{key}n)')
    # 星空の キラキラ（小さな 点と 4つの 角の 星）
    poly = heart_poly(ic[0], ic[1], s * .72)
    rnd = random.Random(7)
    x0, x1, y0, y1 = cx - s * .8, cx + s * .8, cy - s * .8, cy + s * .8
    dots, n = '', 0
    while n < 70:
        p = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
        if inside(p, poly):
            dots += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(rnd.uniform(.7, 1.9) * s / 150)}" fill="#FFFFFF" opacity="{rnd.uniform(.55, 1):.2f}"/>'
            n += 1
    n = 0
    while n < 16:
        p = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
        if inside(p, poly):
            dots += path(sparkle(p[0], p[1], rnd.uniform(3, 9) * s / 150), fill='#FFFFFF', opacity=f'{rnd.uniform(.7, 1):.2f}')
            n += 1
    o += dots
    # 内がわの ふちの 白い 線・ふちの つや（左上の 太い 光・右上の 光・小さな 点）
    o += path(heart(ic[0], ic[1], s * .765), fill='none', stroke='#FFFFFF', stroke_width='2.2', opacity='.5')
    o += path(f'M{f(cx - s * .86)} {f(cy - s * .2)} Q{f(cx - s * .86)} {f(cy - s * .8)} {f(cx - s * .42)} {f(cy - s * .9)}', fill='none',
              stroke='#FFFFFF', stroke_width=f(s * .07), stroke_linecap='round', opacity='.88')
    o += f'<circle cx="{f(cx - s * .9)}" cy="{f(cy - s * .02)}" r="{f(s * .035)}" fill="#FFFFFF" opacity=".9"/>'
    o += path(f'M{f(cx + s * .4)} {f(cy - s * .9)} Q{f(cx + s * .68)} {f(cy - s * .94)} {f(cx + s * .84)} {f(cy - s * .66)}', fill='none',
              stroke='#FFFFFF', stroke_width=f(s * .045), stroke_linecap='round', opacity='.8')
    o += path(f'M{f(cx + s * .55)} {f(cy + s * .42)} Q{f(cx + s * .74)} {f(cy + s * .22)} {f(cx + s * .82)} {f(cy - s * .02)}', fill='none',
              stroke='#FFFFFF', stroke_width=f(s * .03), stroke_linecap='round', opacity='.45')
    return defs, o


def word_svg(text, cx, cy, s, gid, w=15.0, gap=-4):
    """つやつやの 虹色の 字（写真の「ど！」）：こい 赤の ふち → マゼンタ → うすい ピンク → 虹色 → 白い つや。濁点は つやつやの 玉"""
    d, _, balls = word_d(text, cx, cy, s, gap)
    W = w * s
    cm = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    o = (f'<path d="{d}" {cm} stroke="#6E1030" stroke-width="{f(W + 18 * s)}" transform="translate(0 {f(4 * s)})" opacity=".3"/>'
         f'<path d="{d}" {cm} stroke="{OUT}" stroke-width="{f(W + 17 * s)}"/>'
         f'<path d="{d}" {cm} stroke="#EE4C97" stroke-width="{f(W + 11 * s)}"/>'
         f'<path d="{d}" {cm} stroke="#FFD3E8" stroke-width="{f(W + 5 * s)}"/>'
         f'<path d="{d}" {cm} stroke="url(#{gid})" stroke-width="{f(W)}"/>'
         f'<path d="{d}" {cm} stroke="#FFFFFF" stroke-width="{f(W * .3)}" opacity=".6" transform="translate({f(-1.8 * s)} {f(-2.6 * s)})"/>')
    for bx, by, br in balls:
        o += f'<circle cx="{f(bx)}" cy="{f(by + 3 * s)}" r="{f(br + 1 * s)}" fill="#6E1030" opacity=".3"/>' + ball(bx, by, br)
    return o


def shared_defs():
    """①〜⑤ で 同じ 絵（ハート・前足・ひづめ・うしろ足・しっぽ・頭 4つ）：かくした <svg> の defs に 1回だけ 入れて <use> で 使う"""
    cx, cy = HEART_C
    hd, hb = big_heart(cx, cy, HEART_S, 'pmH')
    return (f'<svg class="pmdefs" width="0" height="0" aria-hidden="true"><defs>{art_defs()}{hd}<g id="pmHt">{hb}</g><g id="pmHo">{pony_hooves()}</g>'
            f'<g id="pmAr">{pony_arms()}</g><g id="pmLg">{pony_legs()}</g><g id="pmTl">{pony_tail()}</g><g id="pmHS">{head_R()}</g><g id="pmHT">{head_TQ()}</g>'
            f'<g id="pmHW">{head_TQ(wink=True)}</g><g id="pmHF">{head_F()}</g></defs></svg>')


def screen_art(text, face, key, s_txt=1.32, land=0.0):
    """1文字の 画面の 絵：ポニーが 字の 書いてある ハートを だく（390×844 の 画面。まん中に いる時）。shared_defs と いっしょに 使う。
       ハートと 字は 止まった時（land 秒）に ぷるんっ（pmhj）"""
    cx, cy = HEART_C
    defs = rainbow_grad(key + 't', cy - 50 * s_txt - 10, cy + 50 * s_txt + 10)
    tail = '<use href="#pmTl"/>' if face in 'RrF' else f'<use href="#pmTl" transform="translate({f(2 * cx)} 0) scale(-1 1)"/>'
    body = (tail + '<use href="#pmLg"/>' + pony_torso(face) + head_svg(face) + '<use href="#pmAr"/>'
            + f'<g class="pmhj" style="animation-delay:{land:.2f}s"><use href="#pmHt"/>{word_svg(text, cx, cy - 4, s_txt, key + "t", w=17)}</g>'
            + '<use href="#pmHo"/>')
    return defs, body


# ---------------------------------------------------------------- 動き（タップした 瞬間が 0秒）
# 点めつ（1秒に 3回まで）の ために：落ちている ハートの ほとんどは すき通った 光の ハート（白 12%）で、つもった 時に つやつやの ゼリーに なって ぷるんっ
# （16こに 1こだけ つやつやの まま ぷるぷる 落ちる）。先に つもった ハートほど 前に かさねる（あとから 落ちる ハートは うしろを とおる）。
# ①〜⑤と 最後の ハートは 白い 光の 形で 入ってきて、止まる 時に 色が つく
PC_T = dict(FILL=2.4,                   # ハートが 画面 いっぱいに つもる（0〜2.4）
            BURST=2.48, CHAIN=.16,      # ハートが まん中から 外へ じゅんに はじける（2.48〜2.64 に はじけはじめ・1つ 0.22秒）
            W=(2.66, 2.78, 2.92, 3.32),  # 白い 光：明るくなりはじめ・いちばん 明るい・ここまで・消える
            BG=2.84,                    # 白い 光の 中で 光の 筋と キラキラが 出る
            S=(3.0, 4.2, 5.4, 6.6, 7.8),   # ①〜⑤ の 画面（1つ 1.2秒）
            IN=.45, OUT=.12,           # 入ってくる・消える（つぎの 画面の 前）
            FIN=9.0,                    # 大きな ハートの ど的中
            RES=10.9)                   # ハートが 上へ・ボード
# ①〜⑤：(字, 顔の 向き, 入ってくる 方, 字の 大きさ)。顔：R＝右・L＝左・r＝やや右・l＝やや左（ウィンク）・F＝正面。方：L＝左から・R＝右から・B＝下から・T＝上から・C＝まん中に 出る
SCREENS = (('ど！', 'R', 'L', 1.32), ('て！', 'L', 'R', 1.32), ('き！', 'r', 'B', 1.32), ('ちゅ！', 'l', 'T', 1.1), ('う！', 'F', 'C', 1.32))
FIN_C, FIN_S = (195.0, 415.0), 165.0     # 大きな ハートの まん中と 大きさ
TITLE_Y, TITLE_K = 112.0, .48            # ボードの 上に 動いた ハートの まん中と 大きさ
UP_VEIL = (.12, .77)                     # 上へ 動く 前に 白く なりはじめる（RES の 0.12秒 前）・白い 光の 長さ（動く 0.5秒の あと 0.15秒で 色が もどる）
PILE_COLS = (('#FF5FA6', '#FFC2DE', '#DD3484'), ('#FF8CC2', '#FFDCEC', '#EE5EA0'), ('#FFA9D1', '#FFEAF4', '#F07CB4'),   # つやつやの ゼリーの ハート：(色・光・かげ)
             ('#F25CC4', '#FFC8EE', '#C63A9E'), ('#FF7E9E', '#FFD3DC', '#E5547A'), ('#FFD1E6', '#FFFFFF', '#F2A0C6'))   # ホットピンク・ピンク・うすい ピンク・マゼンタ・コーラル・白っぽい ピンク


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def heart_uri(fill, light, deep):
    """つやつやの ゼリーの ハート（CSS の 背景）：ふちは こい 赤・左上に 大きな 白い つや・右下に うすい 光"""
    d = heart(0, 0, 1)
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1.12 -1.08 2.24 2.24'><defs><radialGradient id='j' cx='.36' cy='.32' r='.78'>"
           f"<stop offset='0' stop-color='{light}'/><stop offset='.55' stop-color='{fill}'/><stop offset='1' stop-color='{deep}'/></radialGradient></defs>"
           f"<path d='{d}' fill='url(#j)' stroke='{OUT}' stroke-width='.085' stroke-linejoin='round'/>"
           "<ellipse cx='-.48' cy='-.5' rx='.27' ry='.16' transform='rotate(-38 -.48 -.5)' fill='#fff' opacity='.92'/>"
           "<circle cx='-.16' cy='-.66' r='.075' fill='#fff' opacity='.9'/>"
           "<path d='M.2 .5 Q.56 .26 .66 -.06' fill='none' stroke='#fff' stroke-width='.08' stroke-linecap='round' opacity='.5'/></svg>")
    return 'url("data:image/svg+xml,' + svg.replace('#', '%23') + '")'


def fly_uri():
    """落ちている ハート：すき通った 光の ハート（白 12%・ふち 7%。どの 背景の 色の 上でも 明るさの 差が 0.1 より 小さい＝点めつ しない）"""
    d = heart(0, 0, 1)
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1.12 -1.08 2.24 2.24'><path d='{d}' fill='#fff' fill-opacity='.12' stroke='#fff' stroke-opacity='.07' stroke-width='.08'/>"
           "<ellipse cx='-.48' cy='-.5' rx='.25' ry='.14' transform='rotate(-38 -.48 -.5)' fill='#fff' opacity='.07'/></svg>")
    return 'url("data:image/svg+xml,' + svg.replace('#', '%23') + '")'


def jelly(x, y, s, rot=0.0):
    """つやつやの ゼリーの ハート（SVG・色は art_defs の pmgJ）"""
    o = (path(heart(0, 0, s), fill='url(#pmgJ)', stroke=OUT, stroke_width=f(max(1.6, s * .085)), stroke_linejoin='round')
         + f'<ellipse cx="{f(-.48 * s)}" cy="{f(-.5 * s)}" rx="{f(.27 * s)}" ry="{f(.16 * s)}" transform="rotate(-38 {f(-.48 * s)} {f(-.5 * s)})" fill="#FFFFFF" opacity=".92"/>'
         + f'<circle cx="{f(-.16 * s)}" cy="{f(-.66 * s)}" r="{f(.075 * s)}" fill="#FFFFFF" opacity=".9"/>'
         + path(f'M{f(.2 * s)} {f(.5 * s)} Q{f(.56 * s)} {f(.26 * s)} {f(.66 * s)} {f(-.06 * s)}', fill='none', stroke='#FFFFFF', stroke_width=f(.08 * s), stroke_linecap='round', opacity='.5'))
    return g(o, transform=f'translate({f(x)} {f(y)}) rotate({f(rot)})')


def sakura(cx, cy, r, fill, rot=0.0, op=.8):
    """さくら（5まいの 花びら・まん中に 黄色い 点）"""
    pd = (f'M0 0 C{f(-r * .55)} {f(-r * .22)} {f(-r * .62)} {f(-r * .86)} {f(-r * .2)} {f(-r * .98)} L0 {f(-r * .84)} L{f(r * .2)} {f(-r * .98)} '
          f'C{f(r * .62)} {f(-r * .86)} {f(r * .55)} {f(-r * .22)} 0 0Z')
    o = ''.join(f'<path d="{pd}" transform="rotate({f(rot + i * 72)})"/>' for i in range(5))
    return f'<g transform="translate({f(cx)} {f(cy)})" fill="{fill}" opacity="{op}">{o}<circle r="{f(r * .17)}" fill="#FFF3A6"/></g>'


def petal(cx, cy, r, rot):
    """ひらひらの 花びら 1まい"""
    return path(f'M0 {f(r)} C{f(-r * .8)} {f(r * .3)} {f(-r * .6)} {f(-r * .7)} {f(-r * .15)} {f(-r)} L0 {f(-r * .78)} L{f(r * .15)} {f(-r)} C{f(r * .6)} {f(-r * .7)} {f(r * .8)} {f(r * .3)} 0 {f(r)}Z',
                fill='#FFC4DD', opacity='.9', transform=f'translate({f(cx)} {f(cy)}) rotate({f(rot)})')


def bg_svg():
    """虹色の 背景の 絵（まさちゃんの 写真の 背景の ふんいき）：うすい 色の さくら・花びら・光の 玉・つやつやの 小さな ハート（止まっている）"""
    rnd = random.Random(21)
    o = ''
    for x, y, r, col, op in ((46, 66, 46, '#FFFFFF', .5), (336, 92, 54, '#E2FFD2', .62), (296, 30, 30, '#FFFFFF', .5), (26, 300, 30, '#E4F8FF', .55),
                             (362, 332, 36, '#FFE6F3', .55), (56, 774, 42, '#A6F1FF', .62), (350, 764, 48, '#FFFFFF', .45), (198, 812, 30, '#FFE2F1', .5),
                             (118, 154, 22, '#FFFFFF', .45), (262, 168, 18, '#FFFFFF', .4), (18, 524, 26, '#FFD3EA', .55), (374, 566, 26, '#ECDDFF', .6)):
        o += sakura(x, y, r, col, rnd.uniform(0, 72), op)
    for i in range(22):
        o += petal(rnd.uniform(6, 384), rnd.uniform(10, 834), rnd.uniform(6, 11), rnd.uniform(0, 360))
    for i in range(18):
        o += f'<circle cx="{f(rnd.uniform(0, 390))}" cy="{f(rnd.uniform(0, 844))}" r="{f(rnd.uniform(5, 18))}" fill="#FFFFFF" opacity="{rnd.uniform(.18, .38):.2f}"/>'
    for x, y, sz, rot in ((38, 214, 18, -14), (354, 206, 15, 12), (22, 648, 16, 10), (366, 654, 20, -12), (318, 296, 11, 8), (86, 112, 12, -8)):
        o += f'<g class="pmbh" style="animation-delay:-{rnd.uniform(0, 3):.2f}s">{jelly(x, y, sz, rot)}</g>'
    return f'<svg viewBox="0 0 390 844" aria-hidden="true">{o}</svg>'


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
FALL_EVERY = 16                          # 16こに 1こは つやつやの まま ぷるぷる 落ちる（ほかは すき通った 光の ハートで 落ちて、つもった時に つやつやに。1つの 点を よこぎる 見える ハートが 1秒に 1こ くらい＝点めつ しない）


def pile_html(seed=11, g=3000.0):
    """つもる ハート（外の i：はじける・中の b：落ちる（b::before：すき通った 光の ハート・b::after：つもった 時の つやつやの ゼリーの ハート・ぷるんっ））。
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
        pv = ' pv' if i % FALL_EVERY == FALL_EVERY // 2 else ''       # 見える ハート（つやつやの まま ぷるぷる 落ちる）
        items.append(f'<i class="pm{h["k"]}{pv}" style="left:{h["x"] - h["s"] * 1.12:.1f}px;top:{h["y"] - h["s"] * 1.08:.1f}px;width:{h["s"] * 2.24:.1f}px;height:{h["s"] * 2.24:.1f}px;'
                     f'--y0:{y0 - h["y"]:.0f}px;--t:{tf:.2f}s;--d:{d:.2f}s;--l:{max(0.0, land - .02):.2f}s;--r0:{h["r0"]:.0f}deg;--r1:{h["r1"]:.0f}deg;'
                     f'--bx:{bx:.0f}px;--by:{by:.0f}px;--br:{rnd.uniform(-25, 25):.0f}deg;--bd:{bd:.2f}s"><b></b></i>')
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
    body += path(heart(hx, hy + 3, 22), fill='#7A1840', opacity='.25') + jelly(hx, hy, 22, 12)
    return defs, body


def enter_anim(frm):
    return dict(L='pmInL', R='pmInR', B='pmInB', T='pmInT', C='pmInC')[frm]


def veil(gid, t, dur, more=''):
    """白い 光の 形（絵と 同じ 形の 白）：入ってくる 間は 絵を 白く つつみ、止まる 時に 消えて 色が つく（点めつ しない 入り方）。more：あとの 動き"""
    return f'<svg class="pmv" viewBox="0 0 390 844" aria-hidden="true" style="animation:pmVl {sec(dur)} linear {sec(t)} both{more}"><use href="#{gid}"/></svg>'


def pc_layers(board_html):
    """押したあと（下から）：虹色の 背景（さくら・花びら・光の 玉・小さな ハート）→ つもる ハート → 光の 筋・キラキラ → ①〜⑤ の ポニー（着いた時に ハートが とぶ）→
       最後の 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。board_html：テーマの ボード（gen_fx の board）"""
    T = PC_T
    hearts, n = pile_html()
    scr = ''
    S = T['S']
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        t_in = S[i]
        defs, body = screen_art(text, face, f'pm{i}', s_txt, land=t_in + T['IN'] * .9)
        t_out = (S[i + 1] if i + 1 < len(S) else T['FIN']) - T['OUT']
        land = t_in + T['IN'] * .72
        cx, cy = HEART_C
        scr += (f'<div class="pms" style="animation:{enter_anim(frm)} {sec(T["IN"])} cubic-bezier(.25,.9,.35,1) {sec(t_in)} both,pmOut {sec(T["OUT"])} linear {sec(t_out)} forwards">'
                f'<svg viewBox="0 0 390 844" aria-hidden="true"><defs>{defs}</defs><g id="pmG{i}">{body}</g></svg>{veil(f"pmG{i}", t_in, T["IN"])}</div>'
                f'<i class="pmr" style="--d:{sec(land)}"></i><div class="pml">{pop_hearts(cx, cy - 20, land, 14, 30 + i)}</div>')
    fdefs, fbody = final_art()
    fx, fy = FIN_C
    bx, by = BURST_C
    return f'''{shared_defs()}<div class="pmbg">{bg_svg()}</div>
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


PILE_CSS = ''.join(f'.ov.pm .pm{k}{{background:{heart_uri(*c)} center/contain no-repeat}}' for k, c in enumerate(PILE_COLS))


def pc_css():
    T = PC_T
    w0, w1, w2, w3 = T['W']
    wd = w3 - w0
    fy = FIN_C[1]
    return PILE_CSS + f'''
/* ---------- プレミアムど的中（かわいいど的中）：premium_cute.py ---------- */
.ov.fz.pm{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
/* 虹色の 背景（まさちゃんの 写真の ふんいき）：水色・黄緑・黄色・ピンク・紫の 光が まざる・まん中は 明るい。上に さくら・花びら・光の 玉・小さな ハート（ゆっくり ふわふわ） */
.ov.pm .pmbg{{position:absolute;inset:0;overflow:hidden;
  background:radial-gradient(ellipse 70% 42% at 50% 47%,rgba(255,253,214,.95),rgba(255,248,170,0) 72%),
    radial-gradient(circle at 10% 6%,rgba(96,206,255,.95),rgba(96,206,255,0) 42%),radial-gradient(circle at 92% 10%,rgba(110,236,120,.95),rgba(110,236,120,0) 46%),
    radial-gradient(circle at 52% 14%,rgba(226,250,110,.9),rgba(226,250,110,0) 38%),radial-gradient(circle at 96% 56%,rgba(255,132,200,.95),rgba(255,132,200,0) 44%),
    radial-gradient(circle at 82% 98%,rgba(124,118,255,.95),rgba(124,118,255,0) 48%),radial-gradient(circle at 6% 94%,rgba(255,140,206,.95),rgba(255,140,206,0) 46%),
    radial-gradient(circle at 2% 50%,rgba(110,214,255,.9),rgba(110,214,255,0) 40%),linear-gradient(170deg,#7CD8FF,#C9F58C 28%,#FFF39A 47%,#FFA5D5 70%,#A08CFF)}}
.ov.pm .pmbg svg{{position:absolute;inset:0;width:390px;height:844px}}
.ov.pm .pmbh{{animation:pmBob 2.8s ease-in-out infinite alternate}}
@keyframes pmBob{{to{{transform:translateY(-6px)}}}}
/* つもる ハート：外の i＝はじける（{sec(T['BURST'])}〜・まん中から じゅんに・ぷくっと ふくらんで）・中の b＝上から 落ちる
   （b::before＝すき通った 光の ハート・b::after＝つもった 時に つやつやの ゼリーの ハートに なって ぷるんっ） */
.ov.pm .pmp{{position:absolute;inset:0;z-index:2;pointer-events:none}}
.ov.pm .pmp i{{position:absolute;display:block;background:none!important;animation:pmB .24s linear var(--bd) forwards}}
.ov.pm .pmp b{{position:absolute;inset:0;transform:translateY(var(--y0)) rotate(var(--r0));animation:pmF var(--t) cubic-bezier(.333,0,.667,.333) var(--d) both}}
.ov.pm .pmp b::before,.ov.pm .pmp b::after{{content:'';position:absolute;inset:0}}
.ov.pm .pmp b::before{{background:{fly_uri()} center/contain no-repeat;animation:pmLo .08s linear var(--l) forwards}}
.ov.pm .pmp b::after{{opacity:0;transform-origin:50% 88%;animation:pmL .1s linear var(--l) forwards,pmJ .55s ease-out var(--l) both}}
{''.join(f'.ov.pm .pmp .pm{k} b::after{{background:{heart_uri(*PILE_COLS[k])} center/contain no-repeat}}' for k in range(len(PILE_COLS)))}
@keyframes pmF{{to{{transform:translateY(0) rotate(var(--r1))}}}}
@keyframes pmL{{to{{opacity:1}}}}
@keyframes pmLo{{to{{opacity:0}}}}
.ov.pm .pmp .pv b::before{{display:none}}
.ov.pm .pmp .pv b::after{{opacity:1;animation:pmWob .34s ease-in-out infinite alternate,pmJ .55s ease-out var(--l) forwards}}
@keyframes pmWob{{from{{transform:scale(1.07,.93)}}to{{transform:scale(.94,1.06)}}}}
@keyframes pmJ{{0%{{transform:scale(1.2,.76)}}28%{{transform:scale(.9,1.12)}}52%{{transform:scale(1.06,.95)}}76%{{transform:scale(.98,1.02)}}100%{{transform:none}}}}
@keyframes pmB{{0%{{transform:none}}35%{{transform:translate(calc(var(--bx) * .3),calc(var(--by) * .3)) scale(1.16,.9)}}100%{{transform:translate(var(--bx),var(--by)) scale(1.4) rotate(var(--br));opacity:0}}}}
.ov.pm .pmlb{{z-index:2}}
/* 白い 光の 中で 出る：光の 筋（ゆっくり 回る）・まん中の 光・キラキラ */
.ov.pm .pmpk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;animation:fzOn .01s linear {sec(T['BG'])} forwards}}
.ov.pm .pmpk .rays{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;opacity:.55;
  background:repeating-conic-gradient(rgba(255,255,255,.9) 0 6deg,rgba(255,255,255,0) 6deg 15deg,rgba(255,214,236,.8) 15deg 21deg,rgba(255,255,255,0) 21deg 30deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 10%,transparent 58%);mask-image:radial-gradient(circle,#000 0 10%,transparent 58%);animation:spin 30s linear infinite}}
.ov.pm .pmpk .glow{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.85),rgba(255,255,255,.42) 38%,rgba(255,255,255,0) 70%)}}
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
.ov.pm .pml i{{position:absolute;display:block;opacity:0;animation:pmPop .7s linear var(--d) both}}
@keyframes pmPop{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}8%{{opacity:1}}
  22%{{transform:translate(calc(var(--dx) * .45),calc(var(--dy) * .45)) scale(1.18,.86) rotate(calc(var(--r) * .3))}}
  40%{{transform:translate(calc(var(--dx) * .7),calc(var(--dy) * .7)) scale(.9,1.1) rotate(calc(var(--r) * .55))}}
  58%{{transform:translate(calc(var(--dx) * .86),calc(var(--dy) * .86)) scale(1.06,.95) rotate(calc(var(--r) * .78))}}70%{{opacity:1}}
  100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1) rotate(var(--r))}}}}
/* ①〜⑤：止まった時に ハートと 字が ぷるんっ */
.ov.pm .pmhj{{transform-origin:{HEART_C[0]:.0f}px {HEART_C[1] + HEART_S * .9:.0f}px;animation:pmHJ .62s ease-out both}}
@keyframes pmHJ{{0%{{transform:none}}18%{{transform:scale(1.07,.92)}}38%{{transform:scale(.95,1.05)}}58%{{transform:scale(1.025,.98)}}78%{{transform:scale(.993,1.006)}}100%{{transform:none}}}}
/* 最後：大きな ハートの ど的中（{sec(T['FIN'])}）→ {sec(T['RES'])} に 上へ 動いて ボード */
.ov.pm .pmf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;opacity:0;pointer-events:none;transform-origin:{FIN_C[0]:.0f}px {fy:.0f}px;
  animation:pmInC .5s cubic-bezier(.25,.9,.35,1) {sec(T['FIN'])} both,pmBeat .9s ease-in-out {sec(T['FIN'] + .5)} 2,pmUp .5s cubic-bezier(.3,.8,.3,1) {sec(T['RES'])} forwards}}
@keyframes pmBeat{{0%,100%{{transform:none}}14%{{transform:scale(1.08,.93)}}30%{{transform:scale(.95,1.06)}}46%{{transform:scale(1.03,.97)}}62%{{transform:scale(.99,1.01)}}}}
@keyframes pmUp{{from{{opacity:1;transform:none}}to{{opacity:1;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.pm .pmu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {sec(T['FIN'])} forwards}}
.ov.pm .pmu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:pmRise var(--t) linear var(--d) infinite}}
@keyframes pmRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}25%{{transform:translate(calc(var(--w) * .5),-220px) scale(1.12,.9)}}
  50%{{transform:translate(var(--w),-440px) scale(.92,1.08)}}75%{{transform:translate(calc(var(--w) * .5),-670px) scale(1.06,.95)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.pm .hb{{z-index:8;animation:pmBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .12)} both}}
@keyframes pmBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.pm .pmw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:pmWhite {sec(wd)} linear {sec(w0)} forwards}}
@keyframes pmWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハート・光の 筋を 出さず、背景の 小さな ハートも 止める。虹色の 背景のまま 1秒 → まん中の 光と キラキラ・上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.pm .pmp,.ov.pm .pms,.ov.pm .pmr,.ov.pm .pml,.ov.pm .pmu,.ov.pm .pmw,.ov.pm .pmpk .rays,.ov.pm .pmf .pmv{{display:none}}
  .ov.fz.pm{{--t0:1.9s}}
  .ov.pm .pmpk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.pm .pmpk .spk path,.ov.pm .pmbh{{animation:none!important}}
  .ov.pm .pmf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.pm .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
