"""神様的中（まさちゃんの指定）：3連単の 当たりの 3頭に 超大穴（10〜12番人気）と、ほかに 大穴以上（7〜12番人気）が 1頭 以上 いる 時 ※仮
   押した あと（0秒＝押した 瞬間）：
     黄色い ピクセルの 細い 雷が こまかく 落ちる → 黄色 → 白い 光に つつまれる →
     ①金の でっかい「ど！」が 左から 右へ 動きながら 消える → ②右から 左へ 動きながら 消える →
     ③金の オーラに つつまれた 金の でっかい「ど！」が 奥から 手前へ 爆発しながら 10こ とんできて 画面を うめる → 金 → 白い 光 →
     うんと 上から ゆっくり、金の オーラを まとった たて書きの「ど的中！！」が おりてきて、まん中で 止まった 時に 金の 雷と 金の オーラで つつむ → ボード
   （まさちゃん「神様的中ボタン タップしたら、ピクセルの細い黄色の細かい雷が画面上に落雷して、黄色から白い閃光に画面が包まれる！
     金色のでっかい、ど！、が1回目、左から右にフェードアウトしていくリアルな文字で、2回目、金色のでっかい、ど！、が右から左にフェードアウトする、
     3回目、金色の、でっかい、ど！、が金色のオーラに包まれながら奥側から画面手前側へ爆発演出で10個飛んできて、画面を埋め尽くし、
     画面が金色から白色の閃光に包まれて、最後にめちゃくちゃ上からゆったり金色のオーラを纏ったど的中！！が縦文字で画面に降りてきて、
     最後画面の中心で止まった時に金の雷と金色のオーラで！ど的中の文字を包み込む！で終わり」）
   絵：flat/kami_art.py（gd_dox＝金の ど！と オーラ・gd_fin＝たて書きの ど的中！！・gd_fin_aura＝その オーラ。キャンバスの アセット：
       id は kami_blobs.json・大きさは kami_layers.json）。ほかは CSS と SVG（ピクセルの 雷・光・爆発・光の 筋・金の ちり）
   点めつ：画面の 大きな 光は 3回（黄色 → 白・金 → 白・ボードの 前の うすい 光）。雷は 細い（画面の 2% 未満）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/kami_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
GD_T = dict(BOLT=(.05, .98),                  # 黄色い ピクセルの 雷
            W1=(.98, 1.26, 1.46, 1.95),       # 黄色 → 白い 光（はじまり・黄色 いちばん・白 いちばん・消える）
            D1=2.0, D2=3.4, DD=1.3,           # ど！①（左 → 右）・②（右 → 左）・長さ
            FLY=4.7, GAP=.155, FD=.38,        # ③ 10この ど！：最初が とびはじめる 時・つぎまでの 間・とんでくる 長さ
            W2=(6.6, 6.95, 7.13, 7.7),        # 金 → 白い 光
            FIN=7.4, FD2=3.2,                 # たて書きの ど的中！！が 上から ゆっくり おりてくる（はじまり・長さ）
            RES=12.05)                        # ボード
GD_T['GOD'] = round(GD_T['FIN'] + GD_T['FD2'], 2)    # まん中で 止まる：金の 雷と オーラ
BOLTS_Y = ((70, 110, 560, .05), (300, 262, 700, .13), (190, 206, 470, .21), (352, 336, 822, .29), (24, 54, 760, .37),
           (244, 214, 640, .45), (130, 150, 846, .53), (330, 300, 520, .61), (100, 70, 690, .69), (270, 292, 610, .77))
# 黄色い 雷：(上の x・下の x・下の y・時刻)。1本 0.16秒 → いつも 2本くらい。1本は 1回だけ 光る（ちかちか させない：点めつ）・となりどうしは 時刻を はなす
FLY = ((110, 232, .82, -9), (286, 612, .86, 7), (292, 214, .8, 8), (94, 650, .88, -6), (200, 118, .78, 3),
       (190, 782, .9, -4), (80, 440, .84, 10), (316, 428, .84, -10), (195, 566, 1.0, 5), (195, 404, 1.24, -3))   # 10この ど！：(字の まん中 x・y・大きさ・かたむき)
GOLD_DT = (.02, .1, .2, .3, .42, .52, .66, .78, 1.02, 1.14)    # 止まった 時の 金の 雷（GOD からの 秒）
VP = (195.0, 410.0)                  # 奥の まん中（とんでくる ど！が 出てくる 所）
DO_C = (195.0, 400.0)                # ①②の ど！の まん中
FIN_C = (195.0, 432.0)               # たて書きの ど的中！！が 止まる まん中
PX = 3                               # ピクセルの 雷の 1ます（画面の px）
YEL = ('#FFFBD6', '#FFE13A', '#FFB300')       # 黄色い 雷：しん・ふち・まわり
GLD = ('#FFF8DC', '#FFC41F', '#FF8A00')       # 金の 雷


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


# ---------------------------------------------------------------- ピクセルの 雷（SVG：1ます PX px の 四角の ならび）
def _displace(rng, a, b, depth, rough):
    pts = [a, b]
    for _ in range(depth):
        nw = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            off = rng.gauss(0, rough * L / 2)
            nw += [((ax + bx) / 2 + nx * off, (ay + by) / 2 + ny * off), (bx, by)]
        pts = nw
    return pts


def _cells(pts):
    out = set()
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        x0, y0, x1, y1 = round(ax / PX), round(ay / PX), round(bx / PX), round(by / PX)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            out.add((x0, y0))
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


def _ring(cells):
    return {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells


def _path(cells):
    """ますの ならび → path（たてに つながる ますは 1つの 四角に）"""
    cols = {}
    for x, y in cells:
        cols.setdefault(x, []).append(y)
    d = []
    for x in sorted(cols):
        ys = sorted(cols[x])
        s = p = ys[0]
        for y in ys[1:] + [None]:
            if y is not None and y == p + 1:
                p = y
                continue
            d.append(f'M{x * PX} {s * PX}h{PX}v{(p - s + 1) * PX}h-{PX}z')
            if y is not None:
                s = p = y
    return ''.join(d)


def bolt(seed, a, b, branches=3, rough=.3, sub=.8):
    """1本の 雷（本線＋えだ＋小えだ）→ (しん・ふち・まわり の path)"""
    rng = random.Random(seed)
    main = _displace(rng, a, b, 6, rough)
    lines = [main]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    base = math.atan2(b[1] - a[1], b[0] - a[0])
    for _ in range(branches):
        i = rng.randint(len(main) // 5, len(main) * 3 // 4)
        p = main[i]
        ang = base + rng.choice((-1, 1)) * rng.uniform(.35, .95)
        ln = rng.uniform(.14, .3) * L
        e = (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang))
        br = _displace(rng, p, e, 4, rough * 1.1)
        lines.append(br)
        if rng.random() < sub:                       # 小えだ
            j = rng.randint(len(br) // 4, len(br) * 3 // 4)
            q = br[j]
            a2 = ang + rng.choice((-1, 1)) * rng.uniform(.3, .8)
            l2 = ln * rng.uniform(.3, .55)
            lines.append(_displace(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), 3, rough * 1.2))
    core = set()
    for ln_ in lines:
        core |= _cells(ln_)
    halo = _ring(core)
    glow = _ring(core | halo)
    return _path(core), _path(halo), _path(glow)


def bolts_svg(specs, cols, cls):
    """雷を まとめた SVG：specs＝[(seed, 上の 点, 下の 点, 時刻, えだの 数)]。1本ずつ <g> に（時刻で ちかちか）"""
    g = ''
    for seed, a, b, t, nb in specs:
        c, h, w = bolt(seed, a, b, nb)
        g += (f'<g style="animation:gdBolt .16s linear {sec(t)} forwards{hide(t, t + .16)}">'
              f'<path d="{w}" fill="{cols[2]}" opacity=".42"/><path d="{h}" fill="{cols[1]}" opacity=".9"/><path d="{c}" fill="{cols[0]}"/></g>')
    return f'<svg class="{cls}" viewBox="0 0 390 844" shape-rendering="crispEdges" aria-hidden="true">{g}</svg>'


def gold_bolts():
    """止まった 時の 金の 雷：まわりから 字へ・字の 左右に そって（GOD〜）"""
    t = GD_T['GOD']
    fx, fy = FIN_C
    ends = (((24, -12), (fx - 70, fy - 250), 3), ((366, -12), (fx + 66, fy - 270), 3), ((-12, 520), (fx - 80, fy + 60), 2), ((402, 470), (fx + 80, fy - 10), 2),
            ((fx - 104, fy - 330), (fx - 96, fy + 300), 4), ((fx + 104, fy - 320), (fx + 98, fy + 310), 4), ((40, 860), (fx - 60, fy + 260), 2),
            ((350, 860), (fx + 60, fy + 250), 2), ((fx - 104, fy - 320), (fx - 98, fy + 300), 3), ((fx + 104, fy - 330), (fx + 96, fy + 300), 3))
    sp = [(901 + k, a, b, t + dt, nb) for k, ((a, b, nb), dt) in enumerate(zip(ends, GOLD_DT))]
    return bolts_svg(sp, GLD, 'gdgb')


def yellow_bolts():
    sp = [(101 + k, (x0, -12), (x1, y1), t, 4 + k % 3) for k, (x0, x1, y1, t) in enumerate(BOLTS_Y)]
    return bolts_svg(sp, YEL, 'gdyb')


# ---------------------------------------------------------------- 爆発・光の つぶ
def sparks(x, y, t, n, seed, dist=(90, 170), col='#FFE27A', size=(10, 3), dur=.55):
    rng = random.Random(seed)
    o = ''
    for k in range(n):
        a = 2 * math.pi * (k + rng.uniform(-.3, .3)) / n
        d = rng.uniform(*dist)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;--dx:{d * math.cos(a):.0f}px;--dy:{d * math.sin(a):.0f}px;--r:{math.degrees(a):.0f}deg;'
              f'width:{size[0]}px;height:{size[1]}px;background:{col};animation:gdSp {sec(dur)} cubic-bezier(.15,.7,.35,1) {sec(t)} forwards{hide(t, t + dur)}"></i>')
    return o


def boom(x, y, t, seed, k=1.0):
    """着いた 時の 爆発：金の 光（白く しすぎない）・輪・とびちる 金の つぶ"""
    f, r = 110 * k, 90 * k
    return (f'<i class="gdxf" style="left:{x - f / 2:.0f}px;top:{y - f / 2:.0f}px;width:{f:.0f}px;height:{f:.0f}px;animation:gdXf .34s ease-out {sec(t)} forwards{hide(t, t + .34)}"></i>'
            f'<i class="gdxr gdxs" style="left:{x - r / 2:.0f}px;top:{y - r / 2:.0f}px;width:{r:.0f}px;height:{r:.0f}px;animation:gdXs .45s cubic-bezier(.2,.7,.35,1) {sec(t)} forwards{hide(t, t + .45)}"></i>'
            + sparks(x, y, t, 5, seed, dist=(60, 110), size=(8, 2)))         # とびちる つぶは 少なく 小さく（たくさん 動く 明るい つぶは 点めつに なる）


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


# ---------------------------------------------------------------- 層
def _img(name, x, y, w, h, cls='', style=''):
    return f'<img class="{cls}" src="{blob(name)}" alt="" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;{style}">'


def gd_layers(board_html):
    """押したあと（下から）：夜の 空 → 黄色い ピクセルの 雷 → 黄色 → 白い 光 → 金の 光の 筋の 画面 → ①②の 金の ど！ → 10この 金の ど！と 爆発 →
       金 → 白い 光 → 天からの 光 → たて書きの 金の ど的中！！（おりてくる）→ 金の 雷・オーラ → ボード（board_html）"""
    T = GD_T
    L = LAY['gd_dox']
    W, H, tx, ty = L['w'], L['h'], L['tx'], L['ty']
    dox = blob('gd_dox')
    # ①② ど！（左 → 右・右 → 左。うしろに うすい のこりの 字 2つ）
    dos = ''
    for k, (t, kf) in enumerate(((T['D1'], 'gdL2R'), (T['D2'], 'gdR2L'))):
        x, y = DO_C[0] - tx, DO_C[1] - ty
        for j, (dl, op) in enumerate(((0, 1),)):
            dos += (f'<div class="gdd" style="left:{x:.1f}px;top:{y:.1f}px;width:{W}px;height:{H}px;transform-origin:{tx}px {ty}px;opacity:0;'
                    f'--o:{op};animation:{kf} {sec(T["DD"])} cubic-bezier(.3,.6,.4,1) {sec(t + dl)} forwards{hide(t + dl, t + dl + T["DD"])}">'
                    f'<img src="{dox}" alt=""></div>')
        land = t + .12
        dos += (f'<i class="gdxr gdxr2" style="left:{DO_C[0] - 80:.0f}px;top:{DO_C[1] - 80:.0f}px;width:160px;height:160px;animation:gdXr .55s cubic-bezier(.2,.7,.35,1) {sec(land)} forwards{hide(land, land + .55)}"></i>'
                + sparks(DO_C[0] + (-60 if k == 0 else 60), DO_C[1], land, 12, 40 + k, dist=(110, 210), size=(12, 3)))
    # ③ 10この ど！（奥の まん中から 手前へ：はやく なりながら 大きく → 着いた 時に 爆発）
    fl = ''
    for i, (x, y, s, r) in enumerate(FLY):
        t0 = T['FLY'] + i * T['GAP']
        ta = t0 + T['FD']
        sx, sy = (VP[0] - x) * .12, (VP[1] - y) * .12
        fl += (f'<div class="gdf" style="left:{x - tx:.1f}px;top:{y - ty:.1f}px;width:{W}px;height:{H}px;transform-origin:{tx}px {ty}px;z-index:{20 + i};'
               f'--sx:{sx:.0f}px;--sy:{sy:.0f}px;--s:{s};--r:{r}deg;--r0:{r * -2}deg;'
               f'animation:gdFly {sec(T["FD"])} cubic-bezier(.3,.55,.5,1) {sec(t0)} forwards{hide(t0, T["W2"][2])}">'
               f'<img src="{dox}" alt="" style="transform-origin:{tx}px {ty}px;filter:contrast(.6) brightness(1.12);animation:gdBump .22s cubic-bezier(.2,.8,.3,1) {sec(ta)} both,gdSharp .08s linear {sec(ta)} forwards"></div>'
               f'<div class="gdx" style="z-index:{21 + i}">{boom(x, y, ta, 60 + i, .9 + .25 * s)}</div>')
    # たて書きの ど的中！！（オーラの 箱の まん中が FIN_C）
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
    return f'''<div class="gdbg" aria-hidden="true" style="animation:{hide(t1=T['W2'][2])[1:]}"></div>
    {yellow_bolts()}
    <div class="gdsc" aria-hidden="true" style="animation:fzOn .01s linear {sec(w1[1])} forwards{hide(w1[1], w2[2])}"><i class="gdry"></i><i class="gdgl"></i><i class="gdgo" style="animation:gdGo .5s ease-in-out {sec(T['FLY'] - .25)} forwards"></i><div class="gdds">{dust(26, 7)}</div></div>
    <div class="gdw gdy1" aria-hidden="true" style="animation:gdY1 {sec(w1[3] - w1[0])} linear {sec(w1[0])} forwards{hide(w1[0], w1[3])}"></div>
    <div class="gdw gdw1" aria-hidden="true" style="animation:gdW1 {sec(w1[3] - w1[0])} linear {sec(w1[0])} forwards{hide(w1[0], w1[3])}"></div>
    <div class="gdp" aria-hidden="true">{dos}</div>
    <div class="gdp" aria-hidden="true">{fl}</div>
    <div class="gdsc2" aria-hidden="true" style="animation:fzOn .01s linear {sec(w2[1])} forwards{hide(w2[1])}"><i class="gdr2"></i><i class="gdpl" style="animation:gdPl 1.6s ease-out {sec(T['FIN'] + .3)} both"></i><div class="gdds gdds2">{dust(30, 11, up=False)}</div></div>
    <div class="gdw gdg2" aria-hidden="true" style="animation:gdY1 {sec(w2[3] - w2[0])} linear {sec(w2[0])} forwards{hide(w2[0], w2[3])}"></div>
    <div class="gdw gdw2" aria-hidden="true" style="animation:gdW1 {sec(w2[3] - w2[0])} linear {sec(w2[0])} forwards{hide(w2[0], w2[3])}"></div>
    {fin}
    <div class="gdp gdz" aria-hidden="true">{gold_bolts()}<i class="gdxr gdxr3" style="left:{rx - 130:.0f}px;top:{ry - 130:.0f}px;width:260px;height:260px;animation:gdXr .8s cubic-bezier(.2,.7,.35,1) {sec(god)} forwards{hide(god, god + .8)}"></i>{sparks(rx, ry, god, 18, 77, dist=(150, 260), size=(14, 3), dur=.8)}</div>
    <div class="gdw gdv" aria-hidden="true" style="animation:gdV .62s ease-out {sec(T['RES'] + .02)} forwards{hide(T['RES'], T['RES'] + .64)}"></div>
    <div class="hb">{board_html}</div>
    <p class="sr">神様的中！黄色い 雷が 落ちて 白く 光り、金の ど！が 左から 右へ・右から 左へ、金の ど！が 10こ 爆発しながら とんできて、さいごに 金の オーラを まとった ど的中！！が 上から おりてきて 金の 雷に つつまれる</p>'''


def gd_css():
    T = GD_T
    w1 = T['W1']
    d1 = w1[3] - w1[0]
    rx, ry = FIN_C
    return f'''
/* ---------- 神様的中：kami.py（金の 字の 絵は flat/kami_art.py・ピクセルの 雷・光・爆発は CSS と SVG） ---------- */
.ov.fz.gd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes gdH{{0%,100%{{visibility:hidden}}}}
.ov.gd .gdbg{{position:absolute;inset:0;background:radial-gradient(ellipse 120% 70% at 50% 0%,#1B1638,#0B0A1A 55%,#050409)}}
.ov.gd .gdp{{position:absolute;inset:0;pointer-events:none}}
.ov.gd .gdp i,.ov.gd .gdds i{{position:absolute;display:block}}
/* 黄色い ピクセルの 雷・金の 雷（1本ずつ ちかちか：しん・ふち・まわり の ます） */
.ov.gd .gdyb,.ov.gd .gdgb{{position:absolute;left:0;top:0;width:390px;height:844px;pointer-events:none;z-index:2}}
.ov.gd .gdyb g,.ov.gd .gdgb g{{opacity:0}}
@keyframes gdBolt{{0%{{opacity:1}}62%{{opacity:1}}100%{{opacity:0}}}}
/* 黄色 → 白い 光・金 → 白い 光（{sec(d1)}） */
.ov.gd .gdw{{position:absolute;inset:0;opacity:0;pointer-events:none;z-index:30}}
.ov.gd .gdy1{{background:#FFE04A}}
.ov.gd .gdg2{{background:#FFC62E}}
.ov.gd .gdw1,.ov.gd .gdw2{{background:#FFFFFF;z-index:31}}
.ov.gd .gdv{{background:radial-gradient(circle at 50% 46%,#FFFFFF,#FFF3C4 60%,#FFE08A);z-index:7}}
@keyframes gdY1{{0%{{opacity:0}}{(w1[1] - w1[0]) / d1 * 100:.1f}%{{opacity:.94}}{(w1[2] - w1[0]) / d1 * 100:.1f}%{{opacity:.94}}100%{{opacity:0}}}}
@keyframes gdW1{{0%,{(w1[1] - w1[0]) / d1 * 100:.1f}%{{opacity:0}}{(w1[2] - w1[0]) / d1 * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
@keyframes gdV{{0%{{opacity:0}}30%{{opacity:.6}}100%{{opacity:0}}}}
/* 金の 光の 筋の 画面（①②③の うしろ）：ゆっくり 回る 光の 筋・まん中の 光・金の ちり */
.ov.gd .gdsc,.ov.gd .gdsc2{{position:absolute;inset:0;opacity:0;overflow:hidden;z-index:1}}
.ov.gd .gdsc{{background:radial-gradient(circle at 50% 47%,#7A4A06,#3A2002 42%,#120903 78%,#070403)}}
.ov.gd .gdry{{position:absolute;left:50%;top:400px;width:900px;height:900px;margin:-450px 0 0 -450px;opacity:.5;
  background:repeating-conic-gradient(from 0deg,rgba(255,214,90,.55) 0deg 5deg,rgba(255,214,90,0) 9deg 17deg,rgba(255,214,90,0) 0deg 18deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 8%,transparent 62%);mask-image:radial-gradient(circle,#000 0 8%,transparent 62%);animation:spin 28s linear infinite}}
.ov.gd .gdgl{{position:absolute;left:50%;top:400px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,226,140,.55),rgba(255,180,40,.22) 40%,rgba(255,160,0,0) 70%)}}
.ov.gd .gdgo{{position:absolute;inset:0;opacity:0;background:radial-gradient(circle at 50% 46%,#E8B23A,#B67A12 50%,#7A4A08)}}
@keyframes gdGo{{to{{opacity:.85}}}}
.ov.gd .gdds{{position:absolute;inset:0}}
.ov.gd .gdds i{{border-radius:50%;background:#FFE7A0;box-shadow:0 0 6px #FFC21A;opacity:0;animation:gdDu 4s ease-in-out infinite}}
@keyframes gdDu{{0%{{opacity:0;transform:translateY(0)}}25%{{opacity:.9}}75%{{opacity:.7}}100%{{opacity:0;transform:translateY(var(--dy))}}}}
/* ①② 金の でっかい ど！：左から（右から）たたきつけて 止まり、右へ（左へ）動きながら 消える。うしろに うすい のこりの 字 */
.ov.gd .gdd,.ov.gd .gdf{{position:absolute;pointer-events:none}}
.ov.gd .gdd img,.ov.gd .gdf img{{position:absolute;inset:0;width:100%;height:100%}}
.ov.gd .gdd{{z-index:5}}
@keyframes gdL2R{{0%{{opacity:0;transform:translateX(-120px) scale(1.25)}}9%{{opacity:var(--o);transform:translateX(-46px) scale(.97)}}15%{{transform:translateX(-42px) scale(1.02)}}21%{{transform:translateX(-38px) scale(1)}}
  46%{{opacity:var(--o);transform:translateX(-8px) scale(1)}}100%{{opacity:0;transform:translateX(120px) scale(1)}}}}
@keyframes gdR2L{{0%{{opacity:0;transform:translateX(120px) scale(1.25)}}9%{{opacity:var(--o);transform:translateX(46px) scale(.97)}}15%{{transform:translateX(42px) scale(1.02)}}21%{{transform:translateX(38px) scale(1)}}
  46%{{opacity:var(--o);transform:translateX(8px) scale(1)}}100%{{opacity:0;transform:translateX(-120px) scale(1)}}}}
/* ③ 10この ど！：奥の まん中（{VP[0]:.0f}, {VP[1]:.0f}）から 手前へ（はやく なりながら 大きく）→ 着いた 時に ぐっと はねて 爆発 */
.ov.gd .gdf{{opacity:0}}
@keyframes gdFly{{0%{{opacity:0;transform:translate(var(--sx),var(--sy)) scale(calc(var(--s) * .3)) rotate(var(--r0))}}30%{{opacity:.22}}88%{{opacity:.27}}100%{{opacity:1;transform:translate(0,0) scale(var(--s)) rotate(var(--r))}}}}
/* とぶ 間は 金の かげ（すけて ぼんやり：動く 字の こい ふちが 点めつに ならない ように）→ 着いた 時に くっきり */
@keyframes gdSharp{{to{{filter:none}}}}
@keyframes gdBump{{0%{{transform:scale(1.13)}}100%{{transform:none}}}}
.ov.gd .gdx{{position:absolute;inset:0;pointer-events:none}}
.ov.gd .gdxf{{border-radius:50%;opacity:0;background:radial-gradient(circle,rgba(255,226,150,.42),rgba(255,190,50,.28) 30%,rgba(255,150,0,.1) 55%,rgba(255,140,0,0) 72%)}}
@keyframes gdXf{{0%{{opacity:0;transform:scale(.2)}}18%{{opacity:1;transform:scale(.8)}}100%{{opacity:0;transform:scale(1.35)}}}}
.ov.gd .gdxr{{border-radius:50%;opacity:0;border:5px solid #FFE07A;box-shadow:0 0 12px #FFB300,inset 0 0 10px #FFB300}}
.ov.gd .gdxr2{{z-index:4}}
.ov.gd .gdxr3{{z-index:9;border-width:4px}}
@keyframes gdXr{{0%{{opacity:0;transform:scale(.25)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(2.5)}}}}
.ov.gd .gdxs{{border-width:3px}}
@keyframes gdXs{{0%{{opacity:0;transform:scale(.3)}}15%{{opacity:.6}}100%{{opacity:0;transform:scale(1.8)}}}}
.ov.gd .gdp i[style*="gdSp"]{{border-radius:2px;opacity:0;box-shadow:0 0 6px #FFB300}}
@keyframes gdSp{{0%{{opacity:0;transform:translate(-50%,-50%) rotate(var(--r)) scaleX(.3)}}10%{{opacity:1}}70%{{opacity:1}}100%{{opacity:0;transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) rotate(var(--r)) scaleX(1)}}}}
/* 天からの 光（さいごの 画面）：上から ひろがる 光の 筋・字の うしろの 光の 柱・おりてくる 金の ちり */
.ov.gd .gdsc2{{z-index:6;background:linear-gradient(180deg,#4A3204,#1E1304 34%,#0B0705 70%,#050305)}}
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
/* 視差効果を減らす：雷・光・とぶ 字を 出さない。1秒 さいごの 画面と ど的中！！ → ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.gd .gdyb,.ov.gd .gdgb,.ov.gd .gdw,.ov.gd .gdsc,.ov.gd .gdp,.ov.gd .gdds{{display:none}}
  .ov.fz.gd{{--t0:1.9s}}
  .ov.gd .gdbg{{animation:none!important}}
  .ov.gd .gdsc2{{animation:fadeIn .6s ease-out .3s both!important}}
  .ov.gd .gdpl{{animation:none!important;opacity:1}}
  .ov.gd .gdfn{{animation:fadeIn .6s ease-out .5s both!important}}
  .ov.gd .gdfn2,.ov.gd .gdfa{{animation:none!important}}
  .ov.gd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
