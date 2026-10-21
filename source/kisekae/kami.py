"""神様的中（まさちゃんの指定）：3連単の 当たりの 3頭に 超大穴（10〜12番人気）と、ほかに 大穴以上（7〜12番人気）が 1頭 以上 いる 時 ※仮
   押した あと（0秒＝押した 瞬間）：
     白と 金の いちばん 細い ピクセルの 雷が 画面 じゅうに 落ちて 下まで ビリビリ → 黄色 → 白い 光に つつまれる →
     ①真っ暗の 中を 金色に かがやく「神様的中」が 左から 右へ ゆっくり（5秒・画面から はみ出る 大きさ）→ ②右から 左へ ゆっくり（5秒）→ 金 → 白い 光 →
     うんと 上から ゆっくり、金の オーラを まとった たて書きの「ど的中！！」が おりてきて、まん中で 止まった 時に 金の 雷と 金の オーラで つつむ → ボード
   （まさちゃん 第4.40版「神様的中ボタン タップしたら、ピクセルの細い黄色の細かい雷が画面上に落雷して、黄色から白い閃光に画面が包まれる！ …
     最後にめちゃくちゃ上からゆったり金色のオーラを纏ったど的中！！が縦文字で画面に降りてきて、最後画面の中心で止まった時に金の雷と金色のオーラで！ど的中の文字を包み込む！で終わり」
     第4.41版「入りの雷がダサすぎる！ もっとピクセル1番細く、白と金色の雷のエフェクト、もっと下までビリビリさせて！ あと雷エフェクトは、もっと画面全体的に！
     あと、ど！ど！ど！のシーン消して！ 真っ暗の背景の中を、神様的中、が金色に輝きながら、左から右、ゆっくり5秒くらい、次のシーンで、神様的中、右から左にゆったり5秒、
     どちらとも、神様的中、の文字画面からはみ出る勢いで演出して！」）
   絵：flat/kami_art.py（gd_word＝金の 神様的中・gd_word_aura＝その オーラ・gd_fin＝たて書きの ど的中！！・gd_fin_aura＝その オーラ。キャンバスの アセット：
       id は kami_blobs.json・大きさは kami_layers.json）。ほかは CSS と SVG（ピクセルの 雷・光・きらめき）
   点めつ：画面の 大きな 光は 3回（黄色 → 白・金 → 白・ボードの 前の うすい 光）。雷は いちばん 細い 1px の 線（まわりに 1px の 金）で、
   1回 光る たびに 形が かわる（同じ 所が 何回も 光らない）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/kami_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
GD_T = dict(BOLT=(.05, 1.45),                  # 白と 金の ピクセルの 雷（ビリビリ）
            W1=(1.3, 1.55, 1.75, 2.3),         # 黄色 → 白い 光（はじまり・黄色 いちばん・白 いちばん・消える）
            A=2.05, B=7.05, SC=5.0,            # 神様的中 ①左 → 右・②右 → 左（はじまり・長さ 5秒）
            W2=(11.6, 11.95, 12.13, 12.7),     # 金 → 白い 光
            FIN=12.4, FD2=3.2,                 # たて書きの ど的中！！が 上から ゆっくり おりてくる（はじまり・長さ）
            RES=17.05)                         # ボード
GD_T['GOD'] = round(GD_T['FIN'] + GD_T['FD2'], 2)    # まん中で 止まる：金の 雷と オーラ
FL_ON = .05                                    # 雷が 1回 光る 長さ（3コマ）
_FLS = ((0, .05, .1, .18), (0, .067, .13), (0, .05, .12, .17, .25), (0, .067, .15, .2), (0, .05, .1, .17, .23))
BOLTS = tuple((x, dx, t, k, _FLS[i % len(_FLS)]) for i, (x, dx, t, k) in enumerate((
    (30, 80, .05, 0), (250, -40, .1, 1), (150, 40, .16, 1), (360, -120, .21, 0), (80, 40, .27, 1), (300, 40, .32, 0), (200, -80, .38, 0),
    (15, 120, .44, 1), (330, -80, .49, 0), (120, 80, .55, 1), (270, 80, .6, 1), (60, 0, .66, 0), (375, -40, .72, 1), (180, -120, .77, 0),
    (230, 120, .83, 0), (100, -80, .88, 1), (345, 0, .94, 0), (40, 40, 1.0, 1), (290, -120, 1.06, 0), (195, 0, 1.12, 1))))
# 白と 金の 雷（上から 下へ）：(上の x・下へ ずれる はば・時刻・0＝白／1＝金・光る 時刻（その 雷の はじまりから）)。画面の 外から 外へ（下まで ビリビリ）。
# 1回 光る たびに 形が かわる（同じ 向きの 形 6つから じゅんに）
SIDE = ((180, 300, .3, 0, (0, .05, .12)), (520, 420, .5, 1, (0, .067, .13)), (330, 460, .7, 0, (0, .05, .1, .17)),
        (700, 620, .9, 1, (0, .05, .12)), (90, 160, 1.05, 0, (0, .067, .13)))
# よこに はしる 雷（画面 じゅうに）：(左の y・右の y・時刻・白／金・光る 時刻)
GOLD_DT = (.02, .1, .2, .3, .42, .52, .66, .78, 1.02, 1.14)    # 止まった 時の 金の 雷（GOD からの 秒）
GOLD_FL = (0, .06, .13)                                       # 金の 雷が 光る 時刻（1本ごと）
WORD_CY = 422.0                      # 神様的中の まん中の 高さ（画面の まん中）
WORD_M = 30.0                        # 神様的中が 画面の はしから はみ出す はば（はじめと おわり）
FIN_C = (195.0, 432.0)               # たて書きの ど的中！！が 止まる まん中
LN = (('#FFFFFF', '#FFE6A0'), ('#FFE070', '#FFA200'))    # 雷の しん（1px）と まわりの 光（3px・7px）：白・金
GLD = ('#FFF1B0', '#FFA800')                              # 止まった 時の 金の 雷


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def hide(t0=None, t1=None):
    """見えない 間は 描かない（出る 前・消えた あと）：animation に 足す 文（先頭に ,）"""
    o = ''
    if t0 is not None:
        o += f',gdH .001s linear {sec(t0)} backwards'
    if t1 is not None:
        o += f',gdH .001s linear {sec(t1)} forwards'
    return o


def blob(name):
    ids = json.load(open(os.environ.get('KAMI_BLOBS', f'{K}/kami_blobs.json'), encoding='utf-8'))
    return f'/_blob/{ids[name]}'


# ---------------------------------------------------------------- ピクセルの 雷（1px の ます・たて よこ だけで つながる 線）
PROF = (.25, .35, .5, .65, .85, 1.0)   # 中点を ずらす 大きさ（大きい 曲がりは 小さく・こまかい ギザギザは 大きく＝雷らしく）


def _displace(rng, a, b, depth, rough):
    pts = [a, b]
    for lv in range(depth):
        nw = [pts[0]]
        r = rough * PROF[min(len(PROF) - 1, lv + 6 - depth)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            off = rng.gauss(0, r * L / 2)
            nw += [((ax + bx) / 2 + nx * off, (ay + by) / 2 + ny * off), (bx, by)]
        pts = nw
    return pts


def _chain(pts):
    """点の 列 → 1px の ますの 列（ななめは よこ → たて に わけて、たて よこ だけで つながる）"""
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        x0, y0, x1, y1 = round(ax), round(ay), round(bx), round(by)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if not out or out[-1] != (x0, y0):
                if out and out[-1][0] != x0 and out[-1][1] != y0:
                    out.append((x0, out[-1][1]))
                out.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
    return out


def _runs(cells):
    """ますの 列 → path（ますの まん中を 通る：M x y h… v…。まっすぐ 続く 所は 1つに）"""
    if len(cells) < 2:
        return ''
    d = [f'M{cells[0][0] + .5:g} {cells[0][1] + .5:g}']
    run, axis = 0, None
    for (ax, ay), (bx, by) in zip(cells, cells[1:]):
        ax_ = 'h' if by == ay else 'v'
        st = (bx - ax) if ax_ == 'h' else (by - ay)
        if ax_ == axis and (run > 0) == (st > 0):
            run += st
        else:
            if axis:
                d.append(f'{axis}{run}')
            axis, run = ax_, st
    d.append(f'{axis}{run}')
    return ''.join(d)


def bolt_d(seed, a, b, branches=4, rough=.5, depth=6, sub=.85, specks=14):
    """1本の 雷（本線＋えだ＋小えだ＋まわりに とぶ 1px の 火花）→ path（1px の ますの 線）"""
    rng = random.Random(seed)
    main = _displace(rng, a, b, depth, rough)
    lines = [main]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    base = math.atan2(b[1] - a[1], b[0] - a[0])
    for _ in range(branches):
        i = rng.randint(len(main) // 8, len(main) * 7 // 8)
        p = main[i]
        ang = base + rng.choice((-1, 1)) * rng.uniform(.4, 1.15)
        ln = rng.uniform(.12, .32) * L
        e = (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang))
        br = _displace(rng, p, e, 4, rough * 1.1)
        lines.append(br)
        if rng.random() < sub:                       # 小えだ
            j = rng.randint(len(br) // 4, len(br) * 3 // 4)
            q = br[j]
            a2 = ang + rng.choice((-1, 1)) * rng.uniform(.3, .9)
            l2 = ln * rng.uniform(.3, .55)
            lines.append(_displace(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), 3, rough * 1.2))
    sp = ''
    for _ in range(specks):                          # ビリビリ：線の まわりに 1px の 火花
        p = main[rng.randrange(len(main))]
        sp += f'M{round(p[0] + rng.uniform(-7, 7)) + .5:g} {round(p[1] + rng.uniform(-7, 7)) + .5:g}h{rng.choice((-1, 1))}'
    return ''.join(_runs(_chain(ln_)) for ln_ in lines) + sp


SLANT = (0, 40, 80, 120)             # 雷の 形の 向き（下へ ずれる はば）。左へ ずれる 雷は 形を 左右 はんてん
NV = 6                               # 向きごとの 形の 数


def bolt_defs():
    """雷の 形（向き 4つ × 6）：上の はし (0, -8) → 下の はし (ずれ, 852)"""
    o = ''
    for si, dx in enumerate(SLANT):
        for v in range(NV):
            o += f'<path id="gdl{si}_{v}" d="{bolt_d(500 + si * 31 + v, (0, -8), (dx, 852), branches=5 + v % 3)}"/>'
    return o


def flick(t, dur, inner):
    return f'<g class="gdfl" style="animation:gdFl {sec(dur)} linear {sec(t)} forwards{hide(t, t + dur)}">{inner}</g>'


def bolts_svg():
    """入りの 雷：白と 金の いちばん 細い ピクセルの 雷（しん 1px・まわりに 1px の 光・うすい 光）が 画面 じゅうに。1回 光る たびに 形が かわって ビリビリ"""
    g = ''
    for i, (x, dx, t, kind, fl) in enumerate(BOLTS):
        si = min(range(len(SLANT)), key=lambda k: abs(SLANT[k] - abs(dx)))
        tf = f'translate({x} 0)' + (' scale(-1 1)' if dx < 0 else '')
        for j, o in enumerate(fl):
            v = (i * 2 + j) % NV
            ref = f'#gdl{si}_{v}'
            g += flick(t + o, FL_ON, ''.join(f'<use href="{ref}" transform="{tf}" class="{c}{kind}"/>' for c in 'hc'))
    for i, (yl, yr, t, kind, fl) in enumerate(SIDE):
        for j, o in enumerate(fl):
            d = bolt_d(700 + i * 11 + j, (-8, yl), (398, yr), branches=4 + j % 2)
            g += flick(t + o, FL_ON, ''.join(f'<path d="{d}" class="{c}{kind}"/>' for c in 'hc'))
    return f'<svg class="gdyb" viewBox="0 0 390 844" shape-rendering="crispEdges" aria-hidden="true"><defs>{bolt_defs()}</defs>{g}</svg>'


def ground_sparks():
    """雷が 下に とどいた 所で ピクセルの 火花（2px の 四角）が とびちる"""
    o = ''
    for i, (x, dx, t, kind, fl) in enumerate(BOLTS):
        rng = random.Random(70 + i)
        bx = x + dx
        for k in range(5):
            a = math.radians(rng.uniform(200, 340))
            d = rng.uniform(16, 44)
            col = LN[kind][0] if k % 2 else LN[kind][1]
            o += (f'<i class="gdgs" style="left:{bx:.0f}px;top:838px;background:{col};--dx:{d * math.cos(a):.0f}px;--dy:{d * math.sin(a):.0f}px;'
                  f'animation:gdGs .34s steps(6) {sec(t + .02)} forwards{hide(t + .02, t + .36)}"></i>')
    return o


def gold_bolts():
    """止まった 時の 金の 雷（GOD〜）：入りの 雷と 同じ 細さ。まわりから 字へ・字の 左右に そって。1本 3回 光って 形が かわる"""
    t = GD_T['GOD']
    fx, fy = FIN_C
    ends = (((24, -12), (fx - 70, fy - 250), 3), ((366, -12), (fx + 66, fy - 270), 3), ((-12, 520), (fx - 80, fy + 60), 2), ((402, 470), (fx + 80, fy - 10), 2),
            ((fx - 104, fy - 330), (fx - 96, fy + 300), 4), ((fx + 104, fy - 320), (fx + 98, fy + 310), 4), ((40, 860), (fx - 60, fy + 260), 2),
            ((350, 860), (fx + 60, fy + 250), 2), ((fx - 104, fy - 320), (fx - 98, fy + 300), 3), ((fx + 104, fy - 330), (fx + 96, fy + 300), 3))
    g = ''
    for k, ((a, b, nb), dt) in enumerate(zip(ends, GOLD_DT)):
        for j, o in enumerate(GOLD_FL):
            d = bolt_d(901 + k * 7 + j, a, b, nb, depth=5)
            g += flick(t + dt + o, FL_ON, ''.join(f'<path d="{d}" class="{c}g"/>' for c in 'ghc'))
    return f'<svg class="gdgb" viewBox="0 0 390 844" shape-rendering="crispEdges" aria-hidden="true">{g}</svg>'


# ---------------------------------------------------------------- 光の つぶ
def sparks(x, y, t, n, seed, dist=(90, 170), col='#FFE27A', size=(10, 3), dur=.55):
    rng = random.Random(seed)
    o = ''
    for k in range(n):
        a = 2 * math.pi * (k + rng.uniform(-.3, .3)) / n
        d = rng.uniform(*dist)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;--dx:{d * math.cos(a):.0f}px;--dy:{d * math.sin(a):.0f}px;--r:{math.degrees(a):.0f}deg;'
              f'width:{size[0]}px;height:{size[1]}px;background:{col};animation:gdSp {sec(dur)} cubic-bezier(.15,.7,.35,1) {sec(t)} forwards{hide(t, t + dur)}"></i>')
    return o


def dust(n, seed, up=True, box=(0, 0, 390, 844)):
    """金の ちり（ゆっくり 上へ／下へ・ちらちら しない 程度に 明るさが かわる）"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        s = rng.uniform(2, 5)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dy:{(-1 if up else 1) * rng.uniform(60, 160):.0f}px;'
              f'animation-duration:{rng.uniform(3, 6):.1f}s;animation-delay:-{rng.uniform(0, 6):.1f}s"></i>')
    return o


# ---------------------------------------------------------------- 神様的中（①左 → 右・②右 → 左）
TWINKLE = ((.07, .22), (.2, .7), (.31, .18), (.46, .62), (.58, .25), (.69, .78), (.83, .2), (.93, .6))   # きらっ（字の 絵の 中の 場所：はば・高さの 割合）


def word_scene(t0, to_right):
    """真っ暗の 中を 金色に かがやく 神様的中が ゆっくり 動く（5秒）。字は 画面の はばの 約2.2倍（はみ出る）：
       左 → 右 は 的中 → 神様、右 → 左 は 神様 → 的中 が 見える。オーラが ゆっくり 明るく・暗く・光の 帯が 字の 上を 通る・きらっ"""
    A, G = LAY['gd_word_aura'], LAY['gd_word']
    T = GD_T
    half = G['w'] / 2
    c_l, c_r = W_ + WORD_M - half, -WORD_M + half          # 字の まん中：右の はしが 見える 所 ／ 左の はしが 見える 所
    c0, c1 = (c_l, c_r) if to_right else (c_r, c_l)
    left, top = c0 - A['w'] / 2, WORD_CY - A['h'] / 2
    word = blob('gd_word')
    tw = ''
    for k, (u, v) in enumerate(TWINKLE):
        tw += (f'<i class="gdtw" style="left:{G["x"] + u * G["w"] - 22:.1f}px;top:{G["y"] + v * G["h"] - 22:.1f}px;'
               f'animation-delay:{sec(t0 + .3 + (k * .37 + (0 if to_right else .19)) % 1.6)}"></i>')
    shine = 'gdShR' if to_right else 'gdShL'
    return (f'<div class="gdwd" style="left:{left:.1f}px;top:{top:.1f}px;width:{A["w"]}px;height:{A["h"]}px;--tx:{c1 - c0:.1f}px;'
            f'animation:gdWm {sec(T["SC"])} cubic-bezier(.35,.12,.65,.88) {sec(t0)} both,gdWo {sec(T["SC"])} linear {sec(t0)} both{hide(t0, t0 + T["SC"])}">'
            f'<img class="gdwa" src="{blob("gd_word_aura")}" alt="" style="animation-delay:{sec(t0)}">'
            f'<img class="gdww" src="{word}" alt="" style="left:{G["x"]}px;top:{G["y"]}px;width:{G["w"]}px;height:{G["h"]}px">'
            f'<div class="gdws" style="left:{G["x"]}px;top:{G["y"]}px;width:{G["w"]}px;height:{G["h"]}px;-webkit-mask-image:url({word});mask-image:url({word})">'
            f'<i style="animation:{shine} 1.9s cubic-bezier(.45,0,.55,1) {sec(t0 + .25)} infinite"></i></div>{tw}</div>')


# ---------------------------------------------------------------- 層
def _img(name, x, y, w, h, cls='', style=''):
    return f'<img class="{cls}" src="{blob(name)}" alt="" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;{style}">'


def gd_layers(board_html):
    """押したあと（下から）：夜の 空 → 白と 金の 雷・火花 → 真っ暗 → 神様的中 ①② → 天からの 光の 画面 → 黄色 → 白・金 → 白の 光 →
       たて書きの 金の ど的中！！（おりてくる）→ 金の 雷・オーラ → ボード（board_html）"""
    T = GD_T
    A, G = LAY['gd_fin_aura'], LAY['gd_fin']
    ax, ay = FIN_C[0] - A['w'] / 2, FIN_C[1] - A['h'] / 2
    god = T['GOD']
    fin = (f'<div class="gdfn" style="left:{ax:.1f}px;top:{ay:.1f}px;width:{A["w"]}px;height:{A["h"]}px;'
           f'animation:gdDesc {sec(T["FD2"])} cubic-bezier(.28,.6,.32,1) {sec(T["FIN"])} both{hide(T["FIN"], T["RES"] + .55)}">'
           f'<div class="gdfn2" style="transform-origin:{A["w"] / 2:.1f}px {A["h"] / 2:.1f}px;animation:gdLand .4s cubic-bezier(.2,.8,.3,1) {sec(god)} both,gdOut .5s ease-in {sec(T["RES"])} forwards">'
           + _img('gd_fin_aura', 0, 0, A['w'], A['h'], 'gdfa', f'transform-origin:{A["w"] / 2:.1f}px {A["h"] / 2:.1f}px;'
                  f'animation:gdAB .7s cubic-bezier(.2,.8,.3,1) {sec(god)} both,gdAP 1.5s ease-in-out {sec(god + .7)} infinite alternate')
           + _img('gd_fin', G['x'], G['y'], G['w'], G['h'], 'gdft', f'animation:gdSharp2 .3s ease-out {sec(god - .05)} forwards')
           + '</div></div>')
    rx, ry = FIN_C
    w1, w2 = T['W1'], T['W2']
    return f'''<div class="gdbg" aria-hidden="true" style="animation:{hide(t1=w1[2])[1:]}"></div>
    {bolts_svg()}
    <div class="gdp" aria-hidden="true">{ground_sparks()}</div>
    <div class="gdk" aria-hidden="true" style="animation:{hide(w1[1], w2[2])[1:]}"></div>
    <div class="gdp gdwp" aria-hidden="true">{word_scene(T['A'], True)}{word_scene(T['B'], False)}</div>
    <div class="gdw gdy1" aria-hidden="true" style="animation:gdY1 {sec(w1[3] - w1[0])} linear {sec(w1[0])} forwards{hide(w1[0], w1[3])}"></div>
    <div class="gdw gdw1" aria-hidden="true" style="animation:gdW1 {sec(w1[3] - w1[0])} linear {sec(w1[0])} forwards{hide(w1[0], w1[3])}"></div>
    <div class="gdsc2" aria-hidden="true" style="animation:fzOn .01s linear {sec(w2[1])} forwards{hide(w2[1])}"><i class="gdr2"></i><i class="gdpl" style="animation:gdPl 1.6s ease-out {sec(T['FIN'] + .3)} both"></i><div class="gdds gdds2">{dust(30, 11, up=False)}</div></div>
    <div class="gdw gdg2" aria-hidden="true" style="animation:gdY1 {sec(w2[3] - w2[0])} linear {sec(w2[0])} forwards{hide(w2[0], w2[3])}"></div>
    <div class="gdw gdw2" aria-hidden="true" style="animation:gdW1 {sec(w2[3] - w2[0])} linear {sec(w2[0])} forwards{hide(w2[0], w2[3])}"></div>
    {fin}
    <div class="gdp gdz" aria-hidden="true">{gold_bolts()}<i class="gdxr gdxr3" style="left:{rx - 130:.0f}px;top:{ry - 130:.0f}px;width:260px;height:260px;animation:gdXr .8s cubic-bezier(.2,.7,.35,1) {sec(god)} forwards{hide(god, god + .8)}"></i>{sparks(rx, ry, god, 18, 77, dist=(150, 260), size=(14, 3), dur=.8)}</div>
    <div class="gdw gdv" aria-hidden="true" style="animation:gdV .62s ease-out {sec(T['RES'] + .02)} forwards{hide(T['RES'], T['RES'] + .64)}"></div>
    <div class="hb">{board_html}</div>
    <p class="sr">神様的中！白と 金の 細い 雷が 画面 じゅうに 落ちて 白く 光り、真っ暗の 中を 金色に かがやく 神様的中が 左から 右へ・右から 左へ、さいごに 金の オーラを まとった ど的中！！が 上から おりてきて 金の 雷に つつまれる</p>'''


def gd_css():
    T = GD_T
    w1 = T['W1']
    d1 = w1[3] - w1[0]
    return f'''
/* ---------- 神様的中：kami.py（金の 字の 絵は flat/kami_art.py・ピクセルの 雷・光・きらめきは CSS と SVG） ---------- */
.ov.fz.gd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes gdH{{0%,100%{{visibility:hidden}}}}
.ov.gd .gdbg{{position:absolute;inset:0;background:radial-gradient(ellipse 120% 70% at 50% 0%,#14112B,#07061A 55%,#030307)}}
.ov.gd .gdk{{position:absolute;inset:0;background:#000}}
.ov.gd .gdp{{position:absolute;inset:0;pointer-events:none}}
.ov.gd .gdp i,.ov.gd .gdds i{{position:absolute;display:block}}
/* 白と 金の ピクセルの 雷・止まった 時の 金の 雷：しん 1px＋まわりに 1px（線の 太さ 3px）。1回 光る たびに 形が かわる */
.ov.gd .gdyb,.ov.gd .gdgb{{position:absolute;left:0;top:0;width:390px;height:844px;pointer-events:none;z-index:2;overflow:hidden}}
.ov.gd .gdfl{{opacity:0}}
.ov.gd .gdfl use,.ov.gd .gdfl path{{fill:none;stroke-linecap:square;stroke-linejoin:miter}}
.ov.gd .h0{{stroke:{LN[0][1]};stroke-width:3;stroke-opacity:.11}}
.ov.gd .c0{{stroke:{LN[0][0]};stroke-width:1}}
.ov.gd .h1{{stroke:{LN[1][1]};stroke-width:3;stroke-opacity:.2}}
.ov.gd .c1{{stroke:{LN[1][0]};stroke-width:1}}
.ov.gd .gg{{stroke:{GLD[1]};stroke-width:7;stroke-opacity:.12}}
.ov.gd .hg{{stroke:{GLD[1]};stroke-width:3;stroke-opacity:.6}}
.ov.gd .cg{{stroke:{GLD[0]};stroke-width:1}}
@keyframes gdFl{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .gdgs{{width:2px;height:2px;opacity:0}}
@keyframes gdGs{{0%{{opacity:1;transform:none}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
/* 黄色 → 白い 光・金 → 白い 光（{sec(d1)}） */
.ov.gd .gdw{{position:absolute;inset:0;opacity:0;pointer-events:none;z-index:30}}
.ov.gd .gdy1{{background:#FFE04A}}
.ov.gd .gdg2{{background:#FFC62E}}
.ov.gd .gdw1,.ov.gd .gdw2{{background:#FFFFFF;z-index:31}}
.ov.gd .gdv{{background:radial-gradient(circle at 50% 46%,#FFFFFF,#FFF3C4 60%,#FFE08A);z-index:7}}
@keyframes gdY1{{0%{{opacity:0}}{(w1[1] - w1[0]) / d1 * 100:.1f}%{{opacity:.94}}{(w1[2] - w1[0]) / d1 * 100:.1f}%{{opacity:.94}}100%{{opacity:0}}}}
@keyframes gdW1{{0%,{(w1[1] - w1[0]) / d1 * 100:.1f}%{{opacity:0}}{(w1[2] - w1[0]) / d1 * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
@keyframes gdV{{0%{{opacity:0}}30%{{opacity:.6}}100%{{opacity:0}}}}
/* 神様的中（真っ暗の 中・{sec(T['SC'])}ずつ）：オーラ → 金の 字 → 光の 帯（字の 形で 切りぬく）→ きらっ。入り {sec(T['SC'] * .07)}・消え {sec(T['SC'] * .09)} */
.ov.gd .gdwp{{z-index:3;overflow:hidden}}
.ov.gd .gdwd{{position:absolute;opacity:0}}
.ov.gd .gdwd img{{position:absolute;display:block}}
.ov.gd .gdwa{{left:0;top:0;width:100%;height:100%;opacity:.8;animation:gdWp 1.4s ease-in-out infinite alternate}}
.ov.gd .gdws{{position:absolute;overflow:hidden;-webkit-mask-size:100% 100%;mask-size:100% 100%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}}
.ov.gd .gdws i{{position:absolute;top:-15%;height:130%;left:0;width:20%;background:linear-gradient(90deg,rgba(255,250,226,0),rgba(255,252,236,.85) 50%,rgba(255,250,226,0));transform:translateX(-140%) skewX(-18deg)}}
.ov.gd .gdtw{{width:44px;height:44px;opacity:0;animation:gdTw 1.6s ease-in-out infinite;
  background:linear-gradient(90deg,transparent 46%,#FFFDF0 50%,transparent 54%),linear-gradient(0deg,transparent 46%,#FFFDF0 50%,transparent 54%),radial-gradient(circle,#FFFFFF 0 7%,rgba(255,226,140,.55) 16%,rgba(255,200,60,0) 42%);
  -webkit-mask-image:radial-gradient(circle,#000 18%,transparent 66%);mask-image:radial-gradient(circle,#000 18%,transparent 66%)}}
@keyframes gdWm{{from{{transform:none}}to{{transform:translateX(var(--tx))}}}}
@keyframes gdWo{{0%{{opacity:0}}7%{{opacity:1}}91%{{opacity:1}}100%{{opacity:0}}}}
@keyframes gdWp{{from{{opacity:.72}}to{{opacity:1}}}}
@keyframes gdShR{{0%{{transform:translateX(-140%) skewX(-18deg)}}70%,100%{{transform:translateX(560%) skewX(-18deg)}}}}
@keyframes gdShL{{0%{{transform:translateX(560%) skewX(-18deg)}}70%,100%{{transform:translateX(-140%) skewX(-18deg)}}}}
@keyframes gdTw{{0%,100%{{opacity:0;transform:scale(.2) rotate(0deg)}}45%{{opacity:1;transform:scale(1) rotate(30deg)}}70%{{opacity:0;transform:scale(.4) rotate(50deg)}}}}
.ov.gd .gdxr{{border-radius:50%;opacity:0;border:5px solid #FFE07A;box-shadow:0 0 12px #FFB300,inset 0 0 10px #FFB300}}
.ov.gd .gdxr3{{z-index:9;border-width:4px}}
@keyframes gdXr{{0%{{opacity:0;transform:scale(.25)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(2.5)}}}}
.ov.gd .gdp i[style*="gdSp"]{{border-radius:2px;opacity:0;box-shadow:0 0 6px #FFB300}}
@keyframes gdSp{{0%{{opacity:0;transform:translate(-50%,-50%) rotate(var(--r)) scaleX(.3)}}10%{{opacity:1}}70%{{opacity:1}}100%{{opacity:0;transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) rotate(var(--r)) scaleX(1)}}}}
.ov.gd .gdds{{position:absolute;inset:0}}
.ov.gd .gdds i{{border-radius:50%;background:#FFE7A0;box-shadow:0 0 6px #FFC21A;opacity:0;animation:gdDu 4s ease-in-out infinite}}
@keyframes gdDu{{0%{{opacity:0;transform:translateY(0)}}25%{{opacity:.9}}75%{{opacity:.7}}100%{{opacity:0;transform:translateY(var(--dy))}}}}
/* 天からの 光（さいごの 画面）：上から ひろがる 光の 筋・字の うしろの 光の 柱・おりてくる 金の ちり */
.ov.gd .gdsc2{{position:absolute;inset:0;opacity:0;overflow:hidden;z-index:6;background:linear-gradient(180deg,#4A3204,#1E1304 34%,#0B0705 70%,#050305)}}
.ov.gd .gdr2{{position:absolute;left:50%;top:-140px;width:1000px;height:1000px;margin-left:-500px;opacity:.7;
  background:repeating-conic-gradient(from 150deg at 50% 0%,rgba(255,220,120,.5) 0deg 3deg,rgba(255,220,120,0) 6deg 10deg);
  -webkit-mask-image:radial-gradient(ellipse 50% 90% at 50% 0%,#000 10%,transparent 75%);mask-image:radial-gradient(ellipse 50% 90% at 50% 0%,#000 10%,transparent 75%)}}
.ov.gd .gdpl{{position:absolute;left:50%;top:0;width:280px;height:844px;margin-left:-140px;opacity:0;
  background:linear-gradient(90deg,rgba(255,214,110,0),rgba(255,226,150,.38) 35%,rgba(255,244,210,.55) 50%,rgba(255,226,150,.38) 65%,rgba(255,214,110,0))}}
@keyframes gdPl{{to{{opacity:1}}}}
.ov.gd .gdds2 i{{background:#FFF0C0}}
/* たて書きの 金の ど的中！！：うんと 上から ゆっくり おりて まん中で 止まる → ぐっと はねて オーラが ふくらみ ひかり つづける → ボードの 前に 消える */
.ov.gd .gdfn{{position:absolute;z-index:8;pointer-events:none}}
.ov.gd .gdfn2{{position:absolute;inset:0}}
.ov.gd .gdfn img{{position:absolute;display:block}}
.ov.gd .gdfa{{opacity:.5}}
/* おりてくる 間は 光る 金の かげ（あかるく・こさを おさえる：動く 字の こまかい 明るさの ちがいが 点めつに ならない ように）→ 止まる 時に くっきりした 金に */
.ov.gd .gdft{{filter:brightness(1.45) contrast(.32) blur(1.6px);opacity:.5}}
@keyframes gdSharp2{{to{{filter:none;opacity:1}}}}
@keyframes gdDesc{{0%{{transform:translateY(-1300px)}}100%{{transform:none}}}}
@keyframes gdLand{{0%{{transform:none}}35%{{transform:scale(1.06)}}100%{{transform:none}}}}
@keyframes gdAB{{0%{{opacity:.5;transform:none}}35%{{opacity:1;transform:scale(1.32)}}100%{{opacity:1;transform:scale(1.14)}}}}
@keyframes gdAP{{from{{opacity:.86;transform:scale(1.12)}}to{{opacity:1;transform:scale(1.2)}}}}
@keyframes gdOut{{to{{opacity:0;transform:scale(1.08)}}}}
.ov.gd .gdz{{z-index:9}}
.ov.gd .hb{{z-index:10;animation:gdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .15)} both{hide(T['RES'] + .15)}}}
@keyframes gdBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 視差効果を減らす：雷・光・神様的中・金の 雷を 出さない。さいごの 画面に くっきりした ど的中！！（動かさない）→ 1.15秒から 消えて ボードを ふわっと */
@keyframes gdFade{{to{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{
  .ov.gd .gdyb,.ov.gd .gdgb,.ov.gd .gdw,.ov.gd .gdk,.ov.gd .gdp,.ov.gd .gdds{{display:none}}
  .ov.fz.gd{{--t0:1.9s}}
  .ov.gd .gdbg{{animation:none!important}}
  .ov.gd .gdsc2{{animation:fadeIn .6s ease-out .3s both!important}}
  .ov.gd .gdpl{{animation:none!important;opacity:1}}
  .ov.gd .gdfn{{animation:fadeIn .5s ease-out .2s both!important}}
  .ov.gd .gdfn2{{animation:gdFade .45s ease-in 1.15s forwards!important}}
  .ov.gd .gdfa{{animation:none!important;opacity:1}}
  .ov.gd .gdft{{animation:none!important;filter:none;opacity:1}}
  .ov.gd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
