"""超プレミアムど的中（手書き）：まさちゃんの指定
   「新しく、超プレミアムど的中ボタン演出追加したい！この感じで、ちょっとぎゃくに線を雑にして手書きっぽく作れる？」
   （まさちゃんの 画面録画：はじめの プレミアムど的中（第4.12〜4.13版・コミット f6b4190）の 見本を iPhone で 撮った もの＝
    PUSH → ラベンダーの 空に ハートが 降って つもる → はじけて 白い 光 → ピンクの 水玉の 画面で、大きな ハートを だいて 立つ ポニーが
    ど！・て！・き！・ちゅ！・う！ → ハートに つつまれた「ど的中」→ ボード）
   → その 流れと 絵（全身の かわいい ポニー・パステルの 虹の ハート・ピンクの 水玉）を そのまま に、線を **手書き** に した 新しい 演出：
   - 線は ゆれて 太さが かわる 筆の 線・はしは 少し はみ出す・細い 下書きの 線が もう1本（rough.py）。ぬりは 線から 少し ずれる
   - 字（ど！ など）も 手書きの 線・ハート（降る・つもる・とぶ・のぼる）・キラキラ・水玉・光の 筋も 手書き
   - 秒は プレミアムど的中と 同じ（premium_cute.py の PC_T）＝効果音も 同じ（snd_pc）
   - 出る 回数：プレミアムど的中の 8回に1回（ランダム）＝ど的中の 48回に1回（まさちゃんの指定「超プレミアムど的中ボタンを入れる
     プレミアムど的中演出の8回に1回ランダムで発生。」）。超プレミアムの 時は プレミアムは 出ない
   - 鉛筆（まさちゃん「線をもっと細くして！ 脚あと少し伸ばして！ 鉛筆で描いたかんじで！」）：ふちの 線は 細い 鉛筆の 線（rough.py の pencil：
     1.3px・太さが 少し かわる・うすい 線で もう1回 なぞる・はしが 少し 行きすぎて 交わる）を ぬりの 上に。絵 ぜんたいに 紙の ざらざら（白い こまかい 点）を
     うすく 重ねて 鉛筆と 色鉛筆の 感じに（ボードには 重ねない）。うしろ足は 40px 長く
   - 重さ：見えない 間は 描かない（zpH：出る 前・消えた あと）・drop-shadow なし
   絵は ぜんぶ SVG（一から 作った 形・cute.py の ポニーと 同じ 形と 色）。まさちゃんの 画面録画は ふんいきの 参考だけ（なぞっていない）
   このファイルは 絵（zp_layers の HTML）と 動き（zp_css）。見本の 画面は gen_fx.py の fz_zp。CSS の 名前は zp…（ほかの 演出と かぶらない）"""
import math
import random
import art
from art import f, smooth, limb, ellipse_pts, heart, sparkle
import cute as C
import rough as R
import premium_cute as PC

LINE = C.LINE                  # ふち（かわいいの 壁紙と 同じ こい ピンク）
PINK, DEEP = C.PINK, C.DEEP
SEED = 2026                    # 手書きの 乱数（何回 作っても 同じ 絵）


def path(d, **a):
    return art.path(d, **a)     # hand() の 中では 手書きに なる（art.path を 呼ぶ）


def outlined(parts, fill, line, lw):
    return art.outlined(parts, fill, line, lw)


STYLE = 'pencil'               # 線の 描き方：鉛筆（まさちゃん「線をもっと細くして！」「鉛筆で描いたかんじで！」）。'brush' で 前の 筆の 線


def hand(scale=1.0, seed=0):
    """この 中で 描く 線と ぬりは 手書き（cute.py の 部品も）。ふちの 色（LINE）と こい 色の 線は 鉛筆の 線に"""
    return R.hand(scale=scale, seed=SEED + seed, mods=(C,), style=STYLE, inks=(LINE,))


# ---------------------------------------------------------------- 字（太い まるい 線で 書いた 字：手書きの 線）
# 字の 形（はじめの プレミアムど的中（f6b4190）の 字と 同じ：1文字＝(はば, [線（点の 列）…])。100×100 の ますに 太い まるい 線で 書いた 字。
# プレミアムの 字（premium_cute.py）が かわっても こちらは かわらない ように 写しを 持つ）
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
RAINBOW = (('0', '#FF5FA8'), ('.2', '#FF9A4A'), ('.38', '#FFE04A'), ('.55', '#6BE08A'), ('.72', '#4CC8FF'), ('.88', '#8F7BFF'), ('1', '#D46BFF'))


def glyph_strokes(ch, x0, y0, s):
    small = SMALL.get(ch)
    if small:
        base, k, _ = small
        w, strokes = GLYPHS[base]
        ox, oy, sc = x0 + 4 * s, y0 + (100 - 100 * k) * s - 4 * s, s * k
    else:
        w, strokes = GLYPHS[ch]
        ox, oy, sc = x0, y0, s
    return [[(ox + x * sc, oy + y * sc) for x, y in st] for st in strokes]


def advance(ch):
    return SMALL[ch][2] if ch in SMALL else GLYPHS[ch][0]


def word_strokes(text, cx, cy, s, gap=-4):
    adv = [advance(c) for c in text]
    total = (sum(adv) + gap * (len(text) - 1)) * s
    x = cx - total / 2
    out = []
    for c, a in zip(text, adv):
        out += glyph_strokes(c, x, cy - 50 * s, s)
        x += (a + gap) * s
    return out


def rainbow_grad(gid, y0, y1):
    stops = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in RAINBOW)
    return f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{f(y0)}" x2="0" y2="{f(y1)}">{stops}</linearGradient>'


def word_svg(text, cx, cy, s, gid, w=15.0, gap=-4, seed=0):
    """手書きの 虹色の 字：1本の 字の 線ごとに 手書きの 中心線を 1つ 作り、こい ピンクの ふち（筆）→ 白 → 虹色 → つや を 同じ 中心線で 重ねる
       （ふちだけ 少し ずれた 下書きの 線も）"""
    W = w * s
    layers = ['', '', '', '', '']
    with hand(1.0, 500 + seed):
        rnd = R._S['rnd']
        for st in word_strokes(text, cx, cy, s, gap):
            _word_stroke(st, rnd, W, s, gid, layers)
    return ''.join(layers)


def _word_stroke(st, rnd, W, s, gid, layers):
    """字の 線 1本（layers：かげ・ふち・白・虹色・つや に 足す）"""
    if len(st) == 1:
        st = [st[0], (st[0][0] + .01, st[0][1] + .01)]
    pts = R.parse(smooth(st, closed=False), step=1.5)[0][0] if len(st) > 2 else st     # なめらかな 線に してから
    hp = R.hand_pts(pts, False, rnd, R.P['amp'] * .9, 2.5, R.P['step'])
    d = R.qspline(hp, closed=False)
    if STYLE == 'pencil':      # 鉛筆：白い ふちの 外に 細い 鉛筆の 線（白の 下に 描く）＋ ずれた うすい 線
        layers[0] += f'<path d="{d}" fill="none" stroke="#7A1C4A" stroke-width="{f(W + 12 * s)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 {f(4 * s)})" opacity=".2"/>'
        rim = W + 8 * s + 2 * R.PEN['w']
        layers[1] += (f'<path d="{d}" fill="none" stroke="{R.PEN["ink"]}" stroke-width="{f(rim)}" stroke-linecap="round" stroke-linejoin="round" '
                      f'opacity="{R.PEN["op"]}"/>')
        rp = R.hand_pts(pts, False, rnd, R.PEN['re_amp'] * 1.4, 5.0, R.P['step'], both=True)
        layers[1] += (f'<path d="{R.qspline(rp, closed=False)}" fill="none" stroke="{R.PEN["ink"]}" stroke-width="{f(rim + 1.6)}" stroke-linecap="round" '
                      f'stroke-linejoin="round" opacity="{R.PEN["re_op"]}"/>')
    else:
        layers[0] += f'<path d="{d}" fill="none" stroke="#7A1C4A" stroke-width="{f(W + 16 * s)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 {f(5 * s)})" opacity=".3"/>'
        layers[1] += f'<path d="{R.brush_d(hp, W + 15 * s, rnd)}" fill="{LINE}"/>'
        sk = R.hand_pts(pts, False, rnd, R.P['sketch_amp'] * 1.3, 4.0, R.P['step'])
        layers[1] += (f'<path d="{R.qspline(sk, closed=False)}" fill="none" stroke="{LINE}" stroke-width="{f(2.2 * s)}" stroke-linecap="round" opacity=".6" '
                      f'transform="translate({f(rnd.uniform(-2, 2) * s)} {f(rnd.uniform(-2, 2) * s)})"/>')
    layers[2] += f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{f(W + 8 * s)}" stroke-linecap="round" stroke-linejoin="round"/>'
    off = f'transform="translate({f(rnd.uniform(-1.2, 1.2) * s)} {f(rnd.uniform(-1.2, 1.2) * s)})"'
    layers[3] += f'<path d="{d}" fill="none" stroke="url(#{gid})" stroke-width="{f(W)}" stroke-linecap="round" stroke-linejoin="round" {off}/>'
    if len(hp) > 3:
        g0 = hp[:max(2, int(len(hp) * .55))]
        layers[4] += (f'<path d="{R.qspline(g0, closed=False)}" fill="none" stroke="#FFFFFF" stroke-width="{f(W * .26)}" stroke-linecap="round" opacity=".6" '
                      f'transform="translate({f(-1.8 * s)} {f(-2.4 * s)})"/>')


# ---------------------------------------------------------------- ポニー（かわいいの 壁紙の ポニーと 同じ 形と 色。大きな ハートを 前に だいて 立つ）
S_HEAD = 2.7                   # 頭の 大きさ（壁紙の ポニーの 何倍）
HEART_C, HEART_S = (195.0, 470.0), 150.0     # ハートの まん中と 大きさ（390×844 の 画面。ハートの はば＝2×HEART_S）
HEAD_AT = dict(R=(186.0, 262.0), L=(204.0, 262.0), r=(190.0, 262.0), l=(200.0, 262.0), F=(195.0, 262.0))


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
    head = smooth(ellipse_pts(80, 48, 31, 27, 14))
    snout = smooth(ellipse_pts(105, 60, 18, 14, 12, rot=8))
    return (outlined([head, snout], '#FFFFFF', LINE, 2.2) + C.pony_face_side() + C.pony_mane() + gloss_curls(SIDE_CURLS[:5])
            + C.pony_ears())


def head_front():
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
    """ななめの 顔の 目（k：はばの ちぢみ。向こうの 目は 細く）。まつげは 右"""
    rx = 6.8 * k
    lash = f'M{f(ex + rx * .82)} {f(ey - 6.2)} l{f(4 * k)} -3.2 M{f(ex + rx * 1.03)} {f(ey - 3.2)} l{f(4.6 * k)} -1.6'
    return (f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(rx)}" ry="8.8" fill="#3A1F2B"/>'
            f'<ellipse cx="{f(ex + .4 * k)}" cy="{f(ey + 2.8)}" rx="{f(5 * k)}" ry="5" fill="#7A3C5C" opacity=".8"/>'
            f'<circle cx="{f(ex + 2.2 * k)}" cy="{f(ey - 4.2)}" r="{f(2.7 * min(1, k + .15))}" fill="#fff"/><circle cx="{f(ex - 2.2 * k)}" cy="{f(ey + 4.4)}" r="1.3" fill="#fff"/>'
            + path(lash, fill='none', stroke='#3A1F2B', stroke_width='1.7', stroke_linecap='round'))


def eye_wink(ex, ey):
    return path(f'M{f(ex - 7)} {f(ey + 1.5)} Q{f(ex)} {f(ey - 7.5)} {f(ex + 7)} {f(ey + 1.5)}', fill='none', stroke='#3A1F2B', stroke_width='2.6',
                stroke_linecap='round') + path(f'M{f(ex + 6.2)} {f(ey - 1.6)} l4.4 -2.6 M{f(ex + 7)} {f(ey + 1.6)} l4.8 -.4', fill='none', stroke='#3A1F2B',
                                               stroke_width='1.7', stroke_linecap='round')


def head_tq(wink=False):
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
    hx, hy = HEAD_AT[face]
    ref, oy, flip = dict(R=('zpHS', 48, False), L=('zpHS', 48, True), r=('zpHT', 47, False), l=('zpHW', 47, True), F=('zpHF', 47, False))[face]
    sx = -S_HEAD if flip else S_HEAD
    return f'<use href="#{ref}" transform="translate({f(hx)} {f(hy)}) scale({f(sx)} {f(S_HEAD)}) translate(-80 -{oy})"/>'


def frill(cx, cy, w, n=5, col='#FFB3CF'):
    """くつ下の フリル（よこに ならんだ まるい なみ）"""
    r = w / n / 2
    o = ''.join(f'<circle cx="{f(cx - w / 2 + r + i * 2 * r)}" cy="{f(cy)}" r="{f(r * 1.25)}" fill="{col}" stroke="{LINE}" stroke-width="2.4"/>' for i in range(n))
    return o + f'<rect x="{f(cx - w / 2 + 1)}" y="{f(cy - r * .2)}" width="{f(w - 2)}" height="{f(r * 1.3)}" fill="{col}"/>'


def pony_tail():
    cx, cy = HEART_C
    side = -1
    tx, ty = cx + side * 132, cy + 40
    curls = [(tx, ty, 25), (tx + side * 22, ty + 22, 24), (tx + side * 30, ty + 50, 22), (tx + side * 22, ty + 76, 19), (tx + side * 4, ty + 94, 15)]
    out = outlined([smooth(ellipse_pts(x, y, r, r, 12)) for x, y, r in curls], PINK, LINE, 2.6)
    for x, y, r in curls[1:4]:
        out += path(smooth(ellipse_pts(x + 1.5, y + 1.5, r * .45, r * .32, 8)), fill='none', stroke=LINE, stroke_width='2.2', opacity='.5')
    return out + gloss_curls(curls)


LEG_X = 40.0                   # うしろ足を のばす 長さ（px。まさちゃん「脚あと少し伸ばして！」）


def pony_legs():
    cx, cy = HEART_C
    out = ''
    y = cy + LEG_X                # くつ下と くつの 高さ
    for lx, fx in ((cx - 44, cx - 50), (cx + 44, cx + 50)):
        leg = limb([(lx, cy + 70), (fx, y + 196)], [50, 46])
        out += outlined([leg], '#FFFFFF', LINE, 2.8)
        out += frill(fx, y + 180, 52, 6)
        out += outlined([smooth([(fx - 25, y + 190), (fx + 25, y + 190), (fx + 26, y + 212), (fx - 26, y + 212)])], '#FFB3CF', LINE, 2.6)
        out += path(f'M{f(fx - 16)} {f(y + 197)} L{f(fx + 16)} {f(y + 197)}', fill='none', stroke='#FFFFFF', stroke_width='3', stroke_linecap='round', opacity='.7')
    return out


def pony_torso(face):
    hx, hy = HEAD_AT[face]
    cx, cy = HEART_C
    nx = hx + (-12 if face == 'R' else 12 if face == 'L' else -4 if face == 'r' else 4 if face == 'l' else 0)
    torso = smooth(ellipse_pts(cx, cy - 118, 104, 58, 16))
    neck = limb([(nx, hy + 30), ((nx + cx) / 2, cy - 150), (cx, cy - 100)], [74, 80, 90], cap=False)
    return outlined([torso, neck], '#FFFFFF', LINE, 2.8)


def pony_hooves():
    cx, cy = HEART_C
    out = ''
    for side in (-1, 1):
        x0, y0 = cx + side * 80, cy - 150
        x1, y1 = cx + side * 100, cy - 112
        leg = limb([(x0, y0), (x1, y1)], [42, 38])
        out += outlined([leg], '#FFFFFF', LINE, 2.8)
        hoof = smooth(ellipse_pts(x1 + side * 1, y1 + 12, 23, 15, 12, rot=side * 10))
        out += outlined([hoof], '#FFB3CF', LINE, 2.6)
        out += path(f'M{f(x1 - 10)} {f(y1 + 10)} Q{f(x1)} {f(y1 + 4)} {f(x1 + 10)} {f(y1 + 10)}', fill='none', stroke=LINE, stroke_width='2', opacity='.5')
    return out


def big_heart(cx, cy, s, key):
    """手書きの 大きな ハート（ふち：ピンク・中：パステルの 虹と 白い 光・つや・キラキラ）"""
    defs = (f'<linearGradient id="{key}r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8CC4"/><stop offset=".55" stop-color="#FF4F9A"/>'
            f'<stop offset="1" stop-color="#E02F7E"/></linearGradient>'
            f'<linearGradient id="{key}i" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFD6EC"/><stop offset=".25" stop-color="#FFE7C9"/>'
            f'<stop offset=".45" stop-color="#FFF6C4"/><stop offset=".62" stop-color="#D9F7DE"/><stop offset=".8" stop-color="#D6EEFF"/><stop offset="1" stop-color="#E9DBFF"/></linearGradient>'
            f'<radialGradient id="{key}w" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".55" stop-color="#FFFFFF" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>')
    out = path(heart(cx, cy + 8, s * 1.0), fill='#B8336E', opacity='.25')
    out += outlined([heart(cx, cy, s)], f'url(#{key}r)', LINE, 3)
    inner = heart(cx, cy + s * .035, s * .84)
    out += path(inner, fill=f'url(#{key}i)')
    out += path(inner, fill=f'url(#{key}w)')
    out += path(inner, fill='none', stroke='#FFFFFF', stroke_width='3', opacity='.9')
    out += path(f'M{f(cx - s * .72)} {f(cy - s * .3)} Q{f(cx - s * .72)} {f(cy - s * .74)} {f(cx - s * .38)} {f(cy - s * .79)}', fill='none', stroke='#FFFFFF',
                stroke_width=f(s * .07), stroke_linecap='round', opacity='.9')
    out += f'<circle cx="{f(cx - s * .82)}" cy="{f(cy - s * .12)}" r="{f(s * .035)}" fill="#FFFFFF" opacity=".9"/>'
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
    with hand(1.0, 1):
        hd, hb = big_heart(cx, cy, HEART_S, 'zpK')
        hb = R.ellipses(hb)
        hv = R.ellipses(pony_hooves())
        lg = R.ellipses(pony_legs())
        tl = R.ellipses(pony_tail())
    heads = {}
    for k, fn, sd in (('zpHS', head_side, 2), ('zpHT', head_tq, 3), ('zpHW', lambda: head_tq(wink=True), 3), ('zpHF', head_front, 4)):
        with hand(S_HEAD, sd):
            heads[k] = R.ellipses(fn())
    return (f'<svg class="zpdefs" width="0" height="0" aria-hidden="true"><defs>{hd}<g id="zpHt">{hb}</g><g id="zpHv">{hv}</g>'
            f'<g id="zpLg">{lg}</g><g id="zpTl">{tl}</g>' + ''.join(f'<g id="{k}">{v}</g>' for k, v in heads.items()) + '</defs></svg>')


def screen_art(i, text, face, key, s_txt=1.32):
    """1文字の 画面の 絵：ポニーが 字の 書いてある ハートを だく（まん中に いる 時）"""
    cx, cy = HEART_C
    defs = rainbow_grad(key + 't', cy - 50 * s_txt - 10, cy + 50 * s_txt + 10)
    tail = '<use href="#zpTl"/>' if face in 'RrF' else f'<use href="#zpTl" transform="translate({f(2 * cx)} 0) scale(-1 1)"/>'
    with hand(1.0, 10 + i):
        torso = R.ellipses(pony_torso(face))
    body = (tail + '<use href="#zpLg"/>' + torso + '<use href="#zpHt"/>' + word_svg(text, cx, cy - 6, s_txt, key + 't', w=17, seed=i)
            + '<use href="#zpHv"/>' + head_svg(face))
    return defs, body


FIN_C, FIN_S = (195.0, 415.0), 165.0     # 最後の 大きな ハートの まん中と 大きさ
TITLE_Y, TITLE_K = 112.0, .48            # ボードの 上に 動いた ハートの まん中と 大きさ


def final_art():
    """最後の 大きな ハート：手書きの ハートに つつまれた「ど的中」＋ 小さな ハート"""
    cx, cy = FIN_C
    with hand(1.0, 20):
        hd, hb = big_heart(cx, cy, FIN_S, 'zpF')
        hx, hy = cx + 124, cy - 84
        small = (path(heart(hx, hy + 3, 21), fill='#B8336E', opacity='.3') + outlined([heart(hx, hy, 21)], '#FF4F9A', LINE, 1.7)
                 + path(f'M{f(hx - 12)} {f(hy - 7)} Q{f(hx - 11)} {f(hy - 15)} {f(hx - 4)} {f(hy - 16)}', fill='none', stroke='#FFFFFF', stroke_width='3.4',
                        stroke_linecap='round', opacity='.9'))
        hb, small = R.ellipses(hb), R.ellipses(small)
    s_txt = .98
    defs = hd + rainbow_grad('zpFt', cy - 50 * s_txt - 14, cy + 50 * s_txt + 14)
    body = hb + word_svg('ど的中', cx - 4, cy - 4, s_txt, 'zpFt', w=14, gap=-6, seed=9) + small
    return defs, body


# ---------------------------------------------------------------- 動き（タップした 瞬間が 0秒）：はじめの プレミアムど的中（f6b4190）と 同じ 流れ・同じ 秒
# 点めつ（1秒に 3回まで）の ために：落ちている ハートは 空と 同じ 明るさの パステル（ふちなし・色だけ ちがう）で、つもった 時に 手書きの ふちと つやが つく。
# 先に つもった ハートほど 前に かさねる（あとから 落ちる ハートは うしろを とおる）。①〜⑤と 最後の ハートは 白い 光の 形で 入ってきて、止まる 時に 色が つく
ZP_T = PC.PC_T                 # 秒は プレミアムど的中と 同じ（効果音 snd_pc が そのまま 合う）
# ①〜⑤：(字, 顔の 向き, 入ってくる 方, 字の 大きさ)。顔：R＝右・L＝左・r＝やや右・l＝やや左（ウィンク）・F＝正面。方：L＝左から・R＝右から・B＝下から・T＝上から・C＝まん中に 出る
SCREENS = (('ど！', 'R', 'L', 1.32), ('て！', 'L', 'R', 1.32), ('き！', 'r', 'B', 1.32), ('ちゅ！', 'l', 'T', 1.1), ('う！', 'F', 'C', 1.32))
UP_VEIL = (.12, .77)                     # 上へ 動く 前に 白く なりはじめる（RES の 0.12秒 前）・白い 光の 長さ
PILE_COLS = (('#FF6FA8', LINE), ('#FF8DC0', LINE), ('#FFB7D3', LINE), ('#FF4F9A', LINE), ('#FFFFFF', LINE), ('#FFD3E5', LINE))   # つもる ハート（ぬり・ふち）
RAIN_BG = ('#DBC9FC', '#D7C2FC')        # ハートが 降る 空（ラベンダー：まん中・はし。相対輝度 0.64・0.60）
FLY_COLS = ('#FFBCD8', '#FFBDCD', '#FFC0B6', '#FBB8FB', '#FFBADD')   # 落ちている ハート（どれも 相対輝度 0.62 前後＝空と 同じ 明るさ）
BURST_C = (195.0, 422.0)                 # はじける まん中
HS = 30.0                                # ハートの 絵の 大きさ（px。CSS で のばす：手書きの ゆれは この 大きさで 1px くらい）
HVB = (-1.26, -1.2, 2.52)                # ハートの 絵の 箱（大きさ 1 の ハートで：左・上・はば）。手書きの 線が はみ出しても 切れない


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def hide(t0=None, t1=None, gap=None):
    """見えない 間は 描かない（出る 前・消えた あとの 絵が 層の 画素を 使わない ように）：
       t0 より 前・t1 より あと・gap＝(a, b) の 間は visibility:hidden（zpH）→ animation に 足す 文（先頭に ,）"""
    o = ''
    if t0 is not None:
        o += f',zpH .001s linear {sec(t0)} backwards'
    if t1 is not None:
        o += f',zpH .001s linear {sec(t1)} forwards'
    if gap is not None:
        o += f',zpH {sec(gap[1] - gap[0])} linear {sec(gap[0])}'
    return o


def uri(svg):
    """SVG の 絵 → CSS の url()"""
    return 'url("data:image/svg+xml,' + svg.replace('"', "'").replace('#', '%23') + '")'


def heart_svg(fill, line, seed):
    """手書きの ハートの 絵（つもる・とぶ・のぼる ハート）：ふちは 筆の 線（太さが かわる・はしが 少し 行きすぎる・下書きの 線）・ぬりは 少し ずれる・つやも 手書き"""
    s = HS
    x0, y0, w = (v * s for v in HVB)
    with hand(1.0, 100 + seed):
        body = outlined([heart(0, 0, s)], fill, line, s * .09)
        body += path(f'M{f(-.62 * s)} {f(-.42 * s)} Q{f(-.6 * s)} {f(-.78 * s)} {f(-.28 * s)} {f(-.8 * s)}', fill='none', stroke='#FFFFFF',
                     stroke_width=f(.13 * s), stroke_linecap='round', opacity='.85')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x0)} {f(y0)} {f(w)} {f(w)}">{body}</svg>'


def fly_svg(fill, seed):
    """落ちている ハートの 絵：ふちなし・ぬりの ふちが 少し ゆれる・うすい つや（空と 明るさの 差が 0.1 より 小さい）"""
    s = HS
    x0, y0, w = (v * s for v in HVB)
    with hand(1.0, 200 + seed):
        body = path(heart(0, 0, s), fill=fill)
        body += path(f'M{f(-.62 * s)} {f(-.42 * s)} Q{f(-.6 * s)} {f(-.78 * s)} {f(-.28 * s)} {f(-.8 * s)}', fill='none', stroke='#FFFFFF',
                     stroke_width=f(.13 * s), stroke_linecap='round', opacity='.15')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x0)} {f(y0)} {f(w)} {f(w)}">{body}</svg>'


def hbox(x, y, s):
    """ハートの 絵（まん中 x, y・大きさ s）を おく 箱の style"""
    return f'left:{x + HVB[0] * s:.1f}px;top:{y + HVB[1] * s:.1f}px;width:{HVB[2] * s:.1f}px;height:{HVB[2] * s:.1f}px'


RING = 240.0                             # 着いた時の 輪の 絵の 箱（px）


def ring_svg():
    """着いた時に 広がる 輪：白い 太い 筆の 輪 ＋ 外と 内に ピンクの 細い 線（手書き）"""
    c = RING / 2
    with hand(1.0, 300):
        o = path(smooth(ellipse_pts(c, c, 111, 111, 16)), fill='none', stroke='#FF8CC4', stroke_width='3.2', opacity='.75')
        o += path(smooth(ellipse_pts(c, c, 102, 102, 16)), fill='none', stroke='#FFFFFF', stroke_width='8')
        o += path(smooth(ellipse_pts(c, c, 93, 93, 16)), fill='none', stroke='#FF9FCB', stroke_width='2.4', opacity='.6')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(RING)} {f(RING)}">{o}</svg>'


RAYS = 1040.0                            # 光の 筋の 箱（画面の いちばん 遠い すみ まで：まん中から 509px）


def rays_svg():
    """手書きの 光の 筋（白と うすい ピンクの くさび：へりが ゆっくり ゆれる・はばも 少しずつ ちがう）。15度ごと（白 → ピンク → 白 …）"""
    rnd = random.Random(SEED + 400)
    c = RAYS / 2
    o = ''
    for k in range(24):
        a0 = math.radians(k * 15.0 + rnd.uniform(-1.5, 1.5))
        a1 = a0 + math.radians(6.0 + rnd.uniform(-1.2, 1.2))
        col, op = ('#FFFFFF', '.9') if k % 2 == 0 else ('#FFD6EC', '.8')
        side = []
        for a in (a0, a1):
            nz = R.noise(rnd, rnd.uniform(110, 170))
            px, py = -math.sin(a), math.cos(a)
            side.append([(c + math.cos(a) * r + px * 5.0 * nz(r)[0] * min(1.0, r / 160), c + math.sin(a) * r + py * 5.0 * nz(r)[0] * min(1.0, r / 160))
                         for r in [14.0 + i * 24.0 for i in range(23)]])
        pts = side[0] + side[1][::-1]
        o += f'<path d="{R.qspline(pts)}" fill="{col}" opacity="{op}"/>'
    return f'<svg viewBox="0 0 {f(RAYS)} {f(RAYS)}" aria-hidden="true">{o}</svg>'


def dots_svg():
    """ピンクの 画面の 白い 水玉（手書き：大きさと 形が 少しずつ ちがう）。88px の ます（11px ごとに ななめに ならぶ）"""
    rnd = random.Random(SEED + 450)
    o = ''
    with hand(1.0, 450):
        for a in range(8):
            for b in range(8):
                if (a + b) % 2:
                    continue
                x, y, r = 5.5 + 11 * a, 5.5 + 11 * b, rnd.uniform(2.6, 3.2)
                o += path(smooth(ellipse_pts(x, y, r * rnd.uniform(.9, 1.1), r * rnd.uniform(.9, 1.1), 7, rot=rnd.uniform(0, 180))), fill='#FFFFFF')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88">{o}</svg>'


GRAIN = dict(tile=180, freq=.85, oct=2, seed=7, k=3.4, t=1.86, op=.55)   # 紙の ざらざら（鉛筆）：ますの 大きさ・こまかさ・かさね・種・白い 点の こさ（k×のこぎり − t）・ぜんたいの こさ


def grain_svg():
    """紙の ざらざら（鉛筆の 線と 色鉛筆の ぬりに 紙の 白い 点が のこる 感じ）：白い こまかい 点の ます（SVG の feTurbulence・つなぎめ なし）。
       絵の 上に うすく 重ねる（ラスターの 絵は 使わない）"""
    g = GRAIN
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{g["tile"]}" height="{g["tile"]}"><filter id="g" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{g["freq"]}" numOctaves="{g["oct"]}" seed="{g["seed"]}" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 {g["k"]} 0 0 0 -{g["t"]}"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg>')


def pile(seed=11, W=390, H=844):
    """つもる ハート [(x, y（まん中）, s（はばの 半分）, 色, 回る角度 …)]。下から 順に つもる。画面の いちばん ひくい 所が 上の はしを こえるまで"""
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


def pile_html(seed=11, g=3000.0):
    """つもる ハート（外の i：はじける・中の b：落ちる うすい ハート・b::after：つもった ハート（手書きの ふち・つや））。
       先に つもった ハートほど あと（前）に 書く：あとから 落ちる ハートは つもった ハートの うしろを とおる"""
    T = ZP_T
    hs = pile(seed)
    rnd = random.Random(seed + 1)
    n = len(hs)
    t_first, t_last = .62, T['FILL']
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
        bd = T['BURST'] + T['CHAIN'] * min(1.0, L / 480) + rnd.uniform(0, .02)
        items.append(f'<i class="zpc{h["k"]}" style="{hbox(h["x"], h["y"], h["s"])};'
                     f'--y0:{y0 - h["y"]:.0f}px;--t:{tf:.2f}s;--d:{d:.2f}s;--l:{max(0.0, land - .02):.2f}s;--r0:{h["r0"]:.0f}deg;--r1:{h["r1"]:.0f}deg;'
                     f'--bx:{bx:.0f}px;--by:{by:.0f}px;--br:{rnd.uniform(-25, 25):.0f}deg;--bd:{bd:.2f}s"><b class="zpd{rnd.randrange(len(FLY_COLS))}"></b></i>')
    return ''.join(reversed(items)), n


def pop_hearts(x, y, d, n, seed, dist=(90, 160), size=(14, 26)):
    """着いた時に まわりへ とびちる 小さな 手書きの ハート（size：ハートの はば）"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        r = rnd.uniform(*dist)
        s = rnd.uniform(*size) / 2.24
        o += (f'<i class="zpc{rnd.randrange(len(PILE_COLS))}" style="{hbox(x, y, s)};'
              f'--dx:{math.cos(a) * r:.0f}px;--dy:{math.sin(a) * r:.0f}px;--d:{sec(d + rnd.uniform(0, .05))};--r:{rnd.uniform(-90, 90):.0f}deg"></i>')
    return o


def rising_hearts(n, seed, t0):
    """下から 上へ のぼって 消える 細かい 手書きの ハート（いつまでも）"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        s = rnd.uniform(7, 17) / 2.24
        dur = rnd.uniform(2.2, 3.8)
        x = rnd.uniform(4, 386)
        o += (f'<i class="zpc{rnd.choice((0, 1, 2, 4, 5))}" style="left:{x + HVB[0] * s:.0f}px;width:{HVB[2] * s:.0f}px;height:{HVB[2] * s:.0f}px;'
              f'--t:{dur:.2f}s;--d:{t0 + rnd.uniform(-dur * .6, 1.6):.2f}s;--w:{rnd.uniform(-26, 26):.0f}px"></i>')
    return o


def twinkles(n, seed, box=(10, 60, 380, 800)):
    """キラキラ（白い ぬり・ピンクの 細い ふち：手書き）"""
    rnd = random.Random(seed)
    o = ''
    with hand(1.0, 600 + seed):
        for i in range(n):
            x, y, r = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3]), rnd.uniform(5, 12)
            o += (f'<g style="animation-duration:{rnd.uniform(1.1, 2.1):.2f}s;animation-delay:-{rnd.uniform(0, 2):.2f}s">'
                  + path(sparkle(x, y, r), fill='#FFFFFF', stroke='#FF9FCB', stroke_width='1.1') + '</g>')
    return o


def enter_anim(frm):
    return dict(L='zpInL', R='zpInR', B='zpInB', T='zpInT', C='zpInC')[frm]


def veil(gid, t, dur, more=''):
    """白い 光の 形（絵と 同じ 形の 白）：入ってくる 間は 絵を 白く つつみ、止まる 時に 消えて 色が つく（点めつ しない 入り方）。more：あとの 動き"""
    return f'<svg class="zpv" viewBox="0 0 390 844" aria-hidden="true" style="animation:zpVl {sec(dur)} linear {sec(t)} both{more}"><use href="#{gid}"/></svg>'


def zp_layers(board_html):
    """押したあと（下から）：ラベンダーの 空 → つもる 手書きの ハート → ピンクの 画面（手書きの 水玉・光の 筋・キラキラ）→ ①〜⑤ の 手書きの ポニー
       （着いた時に 手書きの 輪と ハートが とぶ）→ 最後の 手書きの 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。
       board_html：テーマの ボード（gen_fx の board）"""
    T = ZP_T
    hearts, n = pile_html()
    scr = ''
    S = T['S']
    cx, cy = HEART_C
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        defs, body = screen_art(i, text, face, f'zp{i}', s_txt)
        t_in = S[i]
        t_out = (S[i + 1] if i + 1 < len(S) else T['FIN']) - T['OUT']
        land = t_in + T['IN'] * .72
        scr += (f'<div class="zps" aria-hidden="true" style="animation:{enter_anim(frm)} {sec(T["IN"])} cubic-bezier(.25,.9,.35,1) {sec(t_in)} both,'
                f'zpOut {sec(T["OUT"])} linear {sec(t_out)} forwards{hide(t_in, t_out + T["OUT"])}">'
                f'<svg viewBox="0 0 390 844"><defs>{defs}</defs><g id="zpG{i}">{body}</g></svg>{veil(f"zpG{i}", t_in, T["IN"], hide(t1=t_in + T["IN"]))}</div>'
                f'<i class="zpr" style="animation:zpRing .55s ease-out {sec(land)} both{hide(land, land + .55)}"></i>'
                f'<div class="zpl" aria-hidden="true" style="animation:{hide(land, land + .8)[1:]}">{pop_hearts(cx, cy - 20, land, 14, 30 + i)}</div>')
    fdefs, fbody = final_art()
    fx, fy = FIN_C
    bx, by = BURST_C
    up0 = T['RES'] - UP_VEIL[0]                                       # 最後の ハートが 上へ 動く 前に 白く なりはじめる 時
    pop_d = T['FIN'] + .28                                            # 最後の ハートの 輪と とぶ ハート
    return f'''{shared_defs()}<div class="zpbg" aria-hidden="true"></div>
    <div class="zpp" aria-hidden="true" style="animation:{hide(t1=T['W'][2])[1:]}">{hearts}</div>
    <div class="zpl zplb" aria-hidden="true" style="animation:{hide(T['BURST'], T['W'][2])[1:]}">{pop_hearts(bx, by, T['BURST'], 20, 23, dist=(170, 300), size=(16, 30))}</div>
    <div class="zppk" aria-hidden="true"><i class="rays">{rays_svg()}</i><i class="glow"></i><svg class="zpk" viewBox="0 0 390 844">{twinkles(22, 5)}</svg></div>
    {scr}
    <div class="zpu" aria-hidden="true">{rising_hearts(40, 9, T['FIN'])}</div>
    <div class="zpf" aria-hidden="true"><svg viewBox="0 0 390 844"><defs>{fdefs}</defs><g id="zpFG">{fbody}</g></svg>{veil("zpFG", T["FIN"], .5, f",zpVu {sec(UP_VEIL[1])} linear {sec(up0)} forwards" + hide(t1=up0 + UP_VEIL[1], gap=(T['FIN'] + .5, up0)))}</div>
    <i class="zpr zprf" style="animation:zpRing .55s ease-out {sec(pop_d)} both{hide(pop_d, pop_d + .55)}"></i>
    <div class="zpl" aria-hidden="true" style="animation:{hide(pop_d, pop_d + .8)[1:]}">{pop_hearts(fx, fy - 10, pop_d, 18, 47, dist=(130, 210))}</div>
    <div class="zpgr" aria-hidden="true"></div>
    <div class="hb">{board_html}</div>
    <div class="zpw" aria-hidden="true"></div>
    <p class="sr">超プレミアムど的中！鉛筆で 描いた ハートが いっぱいに つもって はじけ、鉛筆で 描いた ハートを だいた ポニーが ど・て・き・ちゅ・う と 1文字ずつ 出てきて、さいごに 鉛筆で 描いた ハートに つつまれた ど的中</p>'''


def zp_css():
    T = ZP_T
    w0, w1, w2, w3 = T['W']
    wd = w3 - w0
    fy = FIN_C[1]
    hc = ''.join(f'.ov.zp .zpc{k}{{--h:{uri(heart_svg(c, l, k))}}}' for k, (c, l) in enumerate(PILE_COLS))     # 手書きの ハートの 絵（--h：つもる・とぶ・のぼる ハートで 使う）
    return hc + f'''
/* ---------- 超プレミアムど的中（手書き・鉛筆）：super_premium.py・rough.py（線は 細い 鉛筆の 線・なぞる 線・ずれた ぬり・紙の ざらざら） ---------- */
.ov.fz.zp{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
/* 見えない 間は 描かない（hide()：出る 前・消えた あとの 絵が 層の 画素を 使わない ように） */
@keyframes zpH{{0%,100%{{visibility:hidden}}}}
.zpdefs{{position:absolute;width:0;height:0;overflow:hidden}}
.ov.zp .zpbg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 44%,{RAIN_BG[0]},{RAIN_BG[1]} 70%);animation:{hide(t1=T['W'][2])[1:]}}}
/* つもる ハート：外の i＝はじける（{sec(T['BURST'])}〜・まん中から じゅんに）・中の b＝上から 落ちる うすい ハート・b::after＝つもった時に つく 手書きの ふちと つや。
   落ちてくる 前・つもる 前の ふち・はじけた ハートは zpH で 描かない */
.ov.zp .zpp{{position:absolute;inset:0;z-index:2;pointer-events:none}}
.ov.zp .zpp i{{position:absolute;display:block;animation:zpB .22s cubic-bezier(.2,.7,.3,1) var(--bd) forwards,zpH .001s linear calc(var(--bd) + .22s) forwards}}
.ov.zp .zpp b{{position:absolute;inset:0;transform:translateY(var(--y0)) rotate(var(--r0));animation:zpF var(--t) cubic-bezier(.333,0,.667,.333) var(--d) both,zpH .001s linear var(--d) backwards}}
.ov.zp .zpp b::after{{content:'';position:absolute;inset:0;opacity:0;background:var(--h) center/contain no-repeat;animation:zpL .14s linear var(--l) forwards,zpH .001s linear var(--l) backwards}}
{''.join(f'.ov.zp .zpp .zpd{j}{{background:{uri(fly_svg(c, j))} center/contain no-repeat}}' for j, c in enumerate(FLY_COLS))}
@keyframes zpF{{to{{transform:translateY(0) rotate(var(--r1))}}}}
@keyframes zpL{{to{{opacity:1}}}}
@keyframes zpB{{to{{transform:translate(var(--bx),var(--by)) scale(1.35) rotate(var(--br));opacity:0}}}}
.ov.zp .zplb{{z-index:2}}
/* ピンクの 画面（白い 光の 中で かわる）：手書きの 水玉・光の 筋（ゆっくり 回る）・まん中の 光・キラキラ */
.ov.zp .zppk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;
  background:{uri(dots_svg())} 0 0/88px 88px,linear-gradient(180deg,#FFC9DF,#FFE6F1 55%,#FFD3E5);
  animation:fzOn .01s linear {sec(T['BG'])} forwards{hide(T['BG'])}}}
.ov.zp .zppk .rays{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:{RAYS:.0f}px;height:{RAYS:.0f}px;margin:-{RAYS / 2:.0f}px 0 0 -{RAYS / 2:.0f}px;opacity:.55;
  -webkit-mask-image:radial-gradient(circle 778px,#000 0 10%,transparent 58%);mask-image:radial-gradient(circle 778px,#000 0 10%,transparent 58%);animation:spin 30s linear infinite}}
.ov.zp .zppk .rays svg{{position:absolute;inset:0;width:100%;height:100%}}
.ov.zp .zppk .glow{{position:absolute;left:50%;top:{HEART_C[1]:.0f}px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.95),rgba(255,255,255,.5) 38%,rgba(255,255,255,0) 70%)}}
.ov.zp .zppk .zpk{{position:absolute;inset:0;width:390px;height:844px}}
.ov.zp .zppk .zpk g{{animation:zpTw 1.6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes zpTw{{from{{opacity:.25;transform:scale(.55)}}to{{opacity:1;transform:scale(1)}}}}
/* ①〜⑤：手書きの ハートを だいた 手書きの ポニーが 左・右・下・上から 入ってくる／まん中に 出る（1つ {sec(T['S'][1] - T['S'][0])}） */
.ov.zp .zps{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:5;opacity:0;pointer-events:none;transform-origin:{HEART_C[0]:.0f}px {HEART_C[1]:.0f}px}}
.ov.zp .zps svg,.ov.zp .zpf svg{{position:absolute;inset:0;width:390px;height:844px;overflow:visible}}
@keyframes zpInL{{0%{{opacity:1;transform:translateX(-440px) rotate(-7deg)}}72%{{transform:translateX(8px) rotate(1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes zpInR{{0%{{opacity:1;transform:translateX(440px) rotate(7deg)}}72%{{transform:translateX(-8px) rotate(-1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes zpInB{{0%{{opacity:1;transform:translateY(760px)}}72%{{transform:translateY(-14px)}}100%{{opacity:1;transform:none}}}}
@keyframes zpInT{{0%{{opacity:1;transform:translateY(-840px)}}72%{{transform:translateY(6px) scale(1.02,.98)}}100%{{opacity:1;transform:none}}}}
@keyframes zpInC{{0%{{opacity:0;transform:scale(.15)}}55%{{opacity:1;transform:scale(1.13)}}78%{{transform:scale(.95)}}100%{{opacity:1;transform:none}}}}
@keyframes zpOut{{from{{opacity:1}}to{{opacity:0}}}}
/* 白い 光の 形：入ってくる 間は 白く つつみ（0.92）、止まる 前に 消えて 色が つく */
.ov.zp .zpv{{filter:brightness(0) invert(1);opacity:0;pointer-events:none}}
@keyframes zpVl{{0%,62%{{opacity:.92}}100%{{opacity:0}}}}
/* 最後の ハートが 上へ 動く 間も 白く つつむ（{sec(T['RES'] - UP_VEIL[0])}〜） */
@keyframes zpVu{{0%{{opacity:0}}{UP_VEIL[0] / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}{(UP_VEIL[0] + .5) / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}100%{{opacity:0}}}}
/* 着いた時：手書きの 白い 輪と 小さな ハートが とびちる */
.ov.zp .zpr{{position:absolute;z-index:4;left:{HEART_C[0] - RING / 2:.0f}px;top:{HEART_C[1] - 20 - RING / 2:.0f}px;width:{RING:.0f}px;height:{RING:.0f}px;
  background:{uri(ring_svg())} center/contain no-repeat;opacity:0}}
.ov.zp .zprf{{top:{fy - 10 - RING / 2:.0f}px}}
@keyframes zpRing{{0%{{opacity:0;transform:scale(.3)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(2.1)}}}}
.ov.zp .zpl{{position:absolute;inset:0;z-index:6;pointer-events:none}}
.ov.zp .zpl i,.ov.zp .zpu i{{background:var(--h) center/contain no-repeat}}
.ov.zp .zpl i{{position:absolute;display:block;opacity:0;animation:zpPop .7s cubic-bezier(.15,.75,.35,1) var(--d) both}}
@keyframes zpPop{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}8%{{opacity:1}}70%{{opacity:1}}100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1) rotate(var(--r))}}}}
/* 最後：手書きの 大きな ハートの ど的中（{sec(T['FIN'])}）→ {sec(T['RES'])} に 上へ 動いて ボード */
.ov.zp .zpf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;opacity:0;pointer-events:none;transform-origin:{FIN_C[0]:.0f}px {fy:.0f}px;
  animation:zpInC .5s cubic-bezier(.25,.9,.35,1) {sec(T['FIN'])} both,zpBeat .9s ease-in-out {sec(T['FIN'] + .5)} 2,zpUp .5s cubic-bezier(.3,.8,.3,1) {sec(T['RES'])} forwards{hide(T['FIN'])}}}
@keyframes zpBeat{{0%,100%{{transform:none}}20%{{transform:scale(1.06)}}40%{{transform:scale(.99)}}55%{{transform:scale(1.04)}}}}
@keyframes zpUp{{from{{opacity:1;transform:none}}to{{opacity:1;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.zp .zpu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {sec(T['FIN'])} forwards{hide(T['FIN'])}}}
.ov.zp .zpu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:zpRise var(--t) linear var(--d) infinite}}
@keyframes zpRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}50%{{transform:translate(var(--w),-440px)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.zp .hb{{z-index:8;animation:zpBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .12)} both{hide(T['RES'] + .12)}}}
@keyframes zpBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 紙の ざらざら（鉛筆と 色鉛筆の 感じ：白い こまかい 点の ます {GRAIN['tile']}px・動かない）：絵 ぜんたいの 上・ボードの 下 */
.ov.zp .zpgr{{position:absolute;inset:0;z-index:7;pointer-events:none;background:{uri(grain_svg())} 0 0/{GRAIN['tile']}px {GRAIN['tile']}px;opacity:{GRAIN['op']}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.zp .zpw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:zpWhite {sec(wd)} linear {sec(w0)} forwards{hide(w0, w3)}}}
@keyframes zpWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハートを 出さない。1秒 ラベンダー → ピンクの 画面と 上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.zp .zpp,.ov.zp .zplb,.ov.zp .zps,.ov.zp .zpr,.ov.zp .zpl,.ov.zp .zpu,.ov.zp .zpw,.ov.zp .zppk .rays,.ov.zp .zpf .zpv{{display:none}}
  .ov.fz.zp{{--t0:1.9s}}
  .ov.zp .zpbg{{animation:none!important}}
  .ov.zp .zppk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.zp .zppk .zpk g{{animation:none!important}}
  .ov.zp .zpf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.zp .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
