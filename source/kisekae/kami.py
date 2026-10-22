"""神様的中（まさちゃんの指定）：3連単の 当たりの 3頭に 超大穴（10〜12番人気）と、ほかに 大穴以上（7〜12番人気）が 1頭 以上 いる 時 ※仮
   まさちゃん（第4.44版）「スタート一個目の動画にして、次に、二個目の動画にして、文章に 万馬券（きせき）は偶然にあらず 天眼（テンゲル）が導く必然なり
   を入れて！ 三個目の動画をその後に入れて、GODの文字を、神様的中にして！ 全く同じような演出で一度作成してみて！」
   送ってくれた 3つの 動画と 同じ 流れで、絵と 音は 一から 作った（動画の 絵・音・字・ロゴは 使わない・なぞらない）。
   押した あと（0秒＝押した 瞬間）：
     ① 青い 嵐：光の 爆発 → 白 → 赤い 炎の 一瞬 → 青い 嵐（光の 柱・光の ドームを はしる 電気・白い 光の 帯・とんでくる 岩・水色の 光の つぶ）→ 金の 輪の 光 → 白
     ② 金の 字：金の 雲の 空に 金の 立体の 字。「万馬券（きせき）」の 寄り → 「天眼（テンゲル）」の 寄り → 白 → 4行の 文「万馬券（きせき）は／偶然にあらず／天眼（テンゲル）が導く／必然なり」
     ③ 神様的中：白 → 金の 粒が はじけて「神」の 寄り → 金の 粒 →「様」→ 金の 粒 →「的」→ 金の 粒 →「中」→ 金の 粒の 大爆発の 中に「神様／的中」→ ひいて 金の 鳥居 → ボード
   絵：flat/kami_art.py（キャンバスの アセット：id は kami_blobs.json・大きさは kami_layers.json）。ほかは CSS と SVG（雷・光の 帯・岩・光の つぶ・光）
   点めつ：画面の 大きな 光は 白（押した 瞬間・①→②・②の 中・②→③）と ③の 金の 粒の 大きい 爆発（3回）だけ。どの 1秒にも 3回 以下"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/kami_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
GD_T = dict(BURST=(0.0, .24),                      # ① 光の 爆発
            WA1=(.02, .1, .16, .34),               # 白（はじまり・まっ白・まっ白の おわり・消える）
            FIRE=(.12, .44),                       # 赤い 炎の 一瞬
            STORM=(.3, 1.66),                      # 青い 嵐
            BEAMS=(.44, .64, .86, 1.06, 1.24),     # 白い 光の 帯（上から 下へ）
            ROCKS=(.36, .48, .6, .74, .88, 1.0, 1.12, 1.24),     # とんでくる 岩
            ZAP=(.36, 1.4),                        # 光の ドームを はしる 電気・まわりの 雷
            RING=(1.3, 1.64),                      # 金の 輪の 光
            WA2=(1.42, 1.56, 1.66, 1.84),          # 白（① → ②）
            B=1.6,
            CU1=(1.6, 2.08), CU2=(2.08, 2.82),     # 万馬券（きせき）・天眼（テンゲル）の 寄り
            WB=(2.66, 2.8, 2.88, 3.12),            # 白（寄り → 4行の 文）
            TXT=2.82, SHINE=(3.55, 4.45),          # 4行の 文・光の 帯が 通る
            WC=(4.84, 4.98, 5.04, 5.3),            # 白（② → ③）
            C=5.0,
            CH=((5.04, 5.6), (5.6, 6.06), (6.06, 6.52), (6.52, 7.0)),     # 神・様・的・中 の 寄り（見える 間）
            BU=((5.0, 1), (5.6, 0), (6.06, 1), (6.52, 0), (7.0, 2)),      # 金の 粒の 爆発（時刻・強さ 0＝大きな 粒が 手前を 横切るだけ（光らない）・1＝大・2＝いちばん 大）
            LOGO=7.0, PULL=(7.32, 7.9),            # 神様／的中・ひいて 金の 鳥居
            RES=9.0)                               # ボード
FX, FY = 195.0, 444.0                              # 神様／的中 の まん中


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


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


def _img(name, x, y, w, h, cls='', style=''):
    return f'<img class="{cls}" src="{blob(name)}" alt="" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;{style}">'


# ---------------------------------------------------------------- 線（雷・光の 帯）
def _disp(rng, a, b, depth, rough):
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


def _pd(pts):
    return 'M' + ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts)


def bolt(seed, a, b, branches=3, rough=.42, depth=6):
    """細い 雷（本線＋えだ）→ path"""
    rng = random.Random(seed)
    main = _disp(rng, a, b, depth, rough)
    d = _pd(main)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    base = math.atan2(b[1] - a[1], b[0] - a[0])
    for _ in range(branches):
        p = main[rng.randint(len(main) // 6, len(main) * 5 // 6)]
        ang = base + rng.choice((-1, 1)) * rng.uniform(.4, 1.1)
        ln = rng.uniform(.12, .3) * L
        d += _pd(_disp(rng, p, (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang)), depth - 2, rough * 1.1))
    return d


DOME = (195.0, 709.0, 242.0, 338.0)          # 光の ドーム（まん中・よこ・たての 半径）：flat/kami_art.py の storm と 同じ


def dome_arc(seed, a0, a1):
    """光の ドームの ふちを はしる 電気：(角度 a0 → a1 の 弧を ギザギザに）"""
    rng = random.Random(seed)
    cx, cy, rx, ry = DOME
    n = 18
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        j = rng.gauss(0, 5)
        pts.append((cx + (rx + j) * math.cos(a), cy + (ry + j) * math.sin(a)))
    d = ''
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d += _pd(_disp(rng, (ax, ay), (bx, by), 3, .5))[0 if not d else 0:]
    # 外へ 小さな えだ
    for _ in range(3):
        p = pts[rng.randint(2, n - 2)]
        ang = math.atan2(p[1] - cy, p[0] - cx) + rng.uniform(-.6, .6)
        ln = rng.uniform(14, 34)
        d += _pd(_disp(rng, p, (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang)), 3, .5))
    return d


def flick(t, dur, inner, cls='gdfk'):
    return f'<g class="{cls}" style="animation:gdFk {sec(dur)} linear {sec(t)} forwards{hide(t, t + dur)}">{inner}</g>'


SIDE_BOLTS = ((30, 70, 420, .52), (360, 320, 380, .7), (60, 20, 520, .92), (340, 372, 470, 1.12), (20, 90, 360, 1.3))
# まわりの 雷（左右の 上から）：(上の x・下の x・下の y・時刻)。それぞれ 0.07秒 あとに もう1回（形を かえて）


def zap_events():
    """光の ドームの 電気：[(時刻, はじめの 角度, おわりの 角度, 色 c／p)]（音も この 時刻で 鳴らす：gen_sfx.py）"""
    t0, t1 = GD_T['ZAP']
    rng = random.Random(5)
    ev = []
    t = t0
    k = 0
    while t < t1:
        a0 = rng.uniform(190, 300)
        a1 = min(a0 + rng.uniform(30, 70), 350)
        ev.append((round(t, 3), a0, a1, 'p' if k % 2 else 'c'))
        b0 = (a0 + 70 + rng.uniform(0, 60)) % 160 + 190
        ev.append((round(t + .02, 3), b0, min(b0 + rng.uniform(24, 50), 350), 'c' if k % 2 else 'p'))
        t += rng.uniform(.07, .1)
        k += 1
    return ev


def zaps():
    """光の ドームの 電気（白い しんと ピンク・水色の 光）と まわりの 紫の 雷：1回 光る たびに 形が かわる（同じ 所が 何回も 光らない）"""
    g = ''
    for k, (t, a0, a1, tone) in enumerate(zap_events()):
        d = dome_arc(100 + k, a0, a1)
        g += flick(t, .06, f'<path d="{d}" class="zg{tone}"/><path d="{d}" class="zh{tone}"/><path d="{d}" class="zc"/>')
    for j, (x0, x1, y1, t) in enumerate(SIDE_BOLTS):
        for q, o in enumerate((0, .07)):
            d2 = bolt(300 + j, (x0, -10), (x1, y1), 3) if q == 0 else bolt(320 + j, (x0, -10), (x1 + 10, y1 - 20), 3)
            g += flick(t + o, .05, f'<path d="{d2}" class="zgp"/><path d="{d2}" class="zhp"/><path d="{d2}" class="zc"/>')
    return g


BEAM_D = (((120, -30), (60, 240), (190, 480), (150, 760)), ((282, -30), (350, 260), (200, 520), (246, 760)),
          ((40, 60), (10, 300), (130, 520), (96, 780)), ((356, 40), (390, 330), (260, 560), (300, 780)), ((210, -30), (150, 250), (250, 520), (204, 760)))


def beams():
    """白い 光の 帯（上から 下へ 走って 消える）：しん 3px＋まわりの 光"""
    g = ''
    for k, (t, (p0, p1, p2, p3)) in enumerate(zip(GD_T['BEAMS'], BEAM_D)):
        d = f'M{p0[0]} {p0[1]} C{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}'
        st = f'animation:gdBm .12s ease-out {sec(t)} both,gdBo .34s ease-in {sec(t + .26)} forwards{hide(t, t + .6)}'
        g += (f'<g class="gdbm" style="{st}"><path d="{d}" pathLength="100" class="bg1"/><path d="{d}" pathLength="100" class="bg2"/>'
              f'<path d="{d}" pathLength="100" class="bg3"/></g>')
    return g


def rocks():
    """とんでくる 岩（暗い 青・ふちに 水色の 光）：まん中から 手前へ（大きく なって 画面の 外へ）"""
    o = ''
    rng = random.Random(9)
    for k, t in enumerate(GD_T['ROCKS']):
        n = rng.randint(7, 9)
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n + rng.uniform(-.25, .25)
            r = rng.uniform(18, 30)
            pts.append((40 + r * math.cos(a), 40 + r * math.sin(a) * rng.uniform(.75, 1.0)))
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
        side = -1 if k % 2 == 0 else 1
        x0, y0 = 195 + side * rng.uniform(10, 50), rng.uniform(300, 460)
        dx, dy = side * rng.uniform(230, 320), rng.uniform(-260, 200)
        dur = rng.uniform(.45, .6)
        o += (f'<svg class="gdrk" viewBox="0 0 80 80" style="left:{x0 - 40:.0f}px;top:{y0 - 40:.0f}px;--dx:{dx:.0f}px;--dy:{dy:.0f}px;--r:{side * rng.uniform(60, 140):.0f}deg;--s:{rng.uniform(2.6, 4.8):.1f};'
              f'animation:gdRk {sec(dur)} cubic-bezier(.5,0,.9,.6) {sec(t)} both{hide(t, t + dur)}">'
              f'<path d="{d}" fill="url(#gdrkg)"/><path d="{d}" fill="none" stroke="#5FDcFF" stroke-width="1.6" stroke-opacity=".85"/></svg>')
    return o


def motes(n, seed):
    """水色の 光の つぶ（地面から 上へ）"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        x = 195 + rng.gauss(0, 70)
        y = rng.uniform(640, 820)
        s = rng.uniform(2, 4.5)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dy:{-rng.uniform(90, 260):.0f}px;--dx:{rng.uniform(-30, 30):.0f}px;'
              f'animation-duration:{rng.uniform(.8, 1.3):.2f}s;animation-delay:{rng.uniform(.3, 1.0):.2f}s"></i>')
    return o


def scene_a():
    T = GD_T
    st0, st1 = T['STORM']
    fa = LAY['gd_fall']
    ring = LAY['gd_ring']
    r0, r1 = T['RING']
    return f'''<div class="gdA" aria-hidden="true" style="animation:{hide(t1=T['WA2'][2])[1:]}">
      {_img('gd_storm', 0, 0, W_, H_, 'gdst', f'animation:gdIn .1s linear {sec(st0)} both{hide(st0)}')}
      <div class="gdpl" style="animation:gdIn .14s linear {sec(st0)} both{hide(st0)}"><i style="background-image:url({blob('gd_fall')});background-size:{fa['w']:g}px {fa['h']:g}px;--fh:{fa['h']:g}px"></i></div>
      <svg class="gdzap" viewBox="0 0 390 844" aria-hidden="true"><defs><radialGradient id="gdrkg" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#2A3270"/><stop offset=".6" stop-color="#0E1030"/><stop offset="1" stop-color="#05060F"/></radialGradient><linearGradient id="gdbmw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".22" stop-color="#FFFFFF"/><stop offset=".8" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".15"/></linearGradient><linearGradient id="gdbmc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9BE6FF" stop-opacity="0"/><stop offset=".3" stop-color="#C8F2FF"/><stop offset=".85" stop-color="#9BE6FF"/><stop offset="1" stop-color="#9BE6FF" stop-opacity=".1"/></linearGradient></defs>{zaps()}{beams()}</svg>
      <div class="gdmo">{motes(34, 3)}</div>
      {rocks()}
      {_img('gd_fire', 0, 0, W_, H_, 'gdfi', f'animation:gdFi {sec(T["FIRE"][1] - T["FIRE"][0])} linear {sec(T["FIRE"][0])} both{hide(T["FIRE"][0], T["FIRE"][1])}')}
      {_img('gd_burst', 0, 0, W_, H_, 'gdbu', f'animation:gdBu {sec(T["BURST"][1])} cubic-bezier(.2,.8,.3,1) 0s both{hide(None, T["BURST"][1])}')}
      {_img('gd_ring', FX - ring['w'] / 2, 422 - ring['h'] / 2, ring['w'], ring['h'], 'gdrg', f'animation:gdRg {sec(r1 - r0)} cubic-bezier(.3,.6,.4,1) {sec(r0)} both{hide(r0, r1)}')}
    </div>'''


# ---------------------------------------------------------------- ② 金の 字
CU_POS = dict(gd_cu1=dict(s=1.2, x=-30.0, y=304.0, dx=-26.0, dy=-4.0, z=1.04),
              gd_cu2=dict(s=1.14, x=-14.0, y=284.0, dx=-24.0, dy=4.0, z=1.05))
# 寄りの 字：(大きさ・左・上・動く はば x・y・さいごの 大きさ)。動きは ゆっくり 少しだけ（模様の ある 大きな 字が 速く 動くと 点めつに なる）
TXT_C = (195.0, 436.0)                 # 4行の 文の まん中
TWINKLE_B = ((.1, .16), (.86, .12), (.3, .42), (.72, .5), (.16, .74), (.9, .78), (.5, .95))


def dust(n, seed, box=(0, 0, 390, 844), up=False, cls=''):
    """金の ちり（ゆっくり 下へ／上へ）"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        s = rng.uniform(2, 5)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dy:{(-1 if up else 1) * rng.uniform(60, 160):.0f}px;'
              f'animation-duration:{rng.uniform(2.6, 4.5):.1f}s;animation-delay:-{rng.uniform(0, 4):.1f}s"></i>')
    return f'<div class="gdds{cls}">{o}</div>'


def scene_b():
    T = GD_T
    out = ''
    for name, (t0, t1) in (('gd_cu1', T['CU1']), ('gd_cu2', T['CU2'])):
        L, P = LAY[name], CU_POS[name]
        w, h = L['w'] * P['s'], L['h'] * P['s']
        out += _img(name, P['x'], P['y'], w, h, 'gdcu', f'--dx:{P["dx"]:g}px;--dy:{P["dy"]:g}px;--z:{P["z"]:g};'
                    f'animation:gdPan {sec(t1 - t0)} linear {sec(t0)} both{hide(t0 - .02, t1)}')
    G = LAY['gd_txt']
    w, h = G['w'], G['h']
    x, y = TXT_C[0] - w / 2, TXT_C[1] - h / 2
    txt = blob('gd_txt')
    tw = ''
    for k, (u, v) in enumerate(TWINKLE_B):
        tw += (f'<i class="gdtw" style="left:{u * w - 22:.1f}px;top:{v * h - 22:.1f}px;animation-delay:{sec(T["TXT"] + .5 + (k * .43) % 1.7)}"></i>')
    sh = ''.join(f'<i style="animation:gdShR .9s cubic-bezier(.45,0,.55,1) {sec(t)} both"></i>' for t in T['SHINE'])
    out += (f'<div class="gdtx" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:g}px;height:{h:g}px;transform-origin:{w / 2:.1f}px {h / 2:.1f}px;'
            f'animation:gdTx .6s cubic-bezier(.15,.8,.3,1) {sec(T["TXT"])} both{hide(T["TXT"])}">'
            f'<img src="{txt}" alt="" style="left:0;top:0;width:{w:g}px;height:{h:g}px">'
            f'<div class="gdsh" style="-webkit-mask-image:url({txt});mask-image:url({txt})">{sh}</div>{tw}</div>')
    return f'''<div class="gdB" aria-hidden="true" style="animation:{hide(T['WA2'][1], T['WC'][2])[1:]}">
      {_img('gd_sky', 0, 0, W_, H_, 'gdsk')}
      <i class="gdry gdry1"></i><i class="gdry gdry2"></i>
      {dust(26, 21)}
      {out}
      {dust(14, 23, (0, 300, 390, 844), True, ' gdds2')}
    </div>'''


# ---------------------------------------------------------------- ③ 神様的中
CH_POS = ((1.16, 10.0, 0.0, -10.0, 0.0), (1.12, -10.0, 0.0, 10.0, 0.0), (1.16, 10.0, 0.0, -10.0, 0.0), (1.1, -8.0, 0.0, 8.0, 0.0))
# 神・様・的・中 の 寄り：(大きさ, はじめの ずれ x・y, おわりの ずれ x・y)。よこに 少しだけ（字の しまは よこ なので、たてに 動くと 点めつに なる）
TWINKLE_C = ((.08, .1), (.92, .08), (.45, .48), (.1, .9), (.88, .9), (.62, .2), (.3, .62))


def nug_burst(t, kind, seed, cx=195.0, cy=430.0):
    """金の 粒の 爆発：まん中から 手前へ（大きく なって 画面の 外へ）。kind 0＝大きな 粒が いくつか 手前を 横切る（字の かわり目を かくす）・1＝大・2＝いちばん 大"""
    L = LAY['gd_nug']
    cell = L['cell']
    rng = random.Random(seed)
    n = (6, 18, 28)[kind]
    o = ''
    for k in range(n):
        a = 2 * math.pi * (k + rng.uniform(-.4, .4)) / n
        dist = rng.uniform(240, 520) * (1.2 if kind == 2 else 1.0)
        s0, s1 = rng.uniform(.25, .5), rng.uniform(1.4, 3.6) * (1.25 if kind == 2 else 1.0)
        if kind == 0:
            dist, s0, s1 = rng.uniform(380, 520), rng.uniform(.8, 1.2), rng.uniform(4.0, 6.0)
        dur = rng.uniform(.42, .7) if kind else rng.uniform(.3, .4)
        dl = t + rng.uniform(0, .08)
        sp = rng.randrange(L['n'])
        bx, by = -(sp % 4) * cell, -(sp // 4) * cell
        o += (f'<i style="left:{cx + rng.gauss(0, 18) - cell / 2:.0f}px;top:{cy + rng.gauss(0, 18) - cell / 2:.0f}px;background-position:{bx}px {by}px;'
              f'--dx:{dist * math.cos(a):.0f}px;--dy:{dist * math.sin(a):.0f}px;--s0:{s0:.2f};--s1:{s1:.2f};--r:{rng.uniform(-160, 160):.0f}deg;'
              f'animation:gdNu {sec(dur)} cubic-bezier(.2,.6,.5,1) {sec(dl)} both{hide(dl, dl + dur)}"></i>')
    return o


def scene_c():
    T = GD_T
    c0 = T['C']
    ch = ''
    for k, (t0, t1) in enumerate(T['CH']):
        name = f'gd_c{k + 1}'
        L = LAY[name]
        s, x0, y0, x1, y1 = CH_POS[k]
        w, h = L['w'] * s, L['h'] * s
        ch += _img(name, FX - w / 2, 430 - h / 2, w, h, 'gdch', f'--x0:{x0:g}px;--y0:{y0:g}px;--x1:{x1:g}px;--y1:{y1:g}px;'
                   f'animation:gdCh {sec(t1 - t0)} linear {sec(t0)} both{hide(t0, t1)}')
    nu, gl = '', ''
    for k, (t, kind) in enumerate(T['BU']):
        nu += nug_burst(t, kind, 40 + k * 3, FX, 430 if kind < 2 else FY)
        if kind:
            dur = (0, .42, .62)[kind]
            gl += f'<i class="gdgl gdgl{kind}" style="animation:gdGl{kind} {sec(dur)} ease-out {sec(t)} both{hide(t, t + dur)}"></i>'
    F, G = LAY['gd_frame'], LAY['gd_logo']
    lg_t = T['LOGO']
    p0, p1 = T['PULL']
    logo = blob('gd_logo')
    tw = ''
    for k, (u, v) in enumerate(TWINKLE_C):
        tw += f'<i class="gdtw" style="left:{u * G["w"] - 22:.1f}px;top:{v * G["h"] - 22:.1f}px;animation-delay:{sec(p1 + .1 + (k * .37) % 1.4)}"></i>'
    lx, ly = FX - G['w'] / 2, FY - G['h'] / 2
    group = (f'<div class="gdlg" style="transform-origin:{FX:g}px {FY:g}px;--z:1.42;'
             f'animation:gdPull {sec(p1 - p0)} cubic-bezier(.45,0,.3,1) {sec(p0)} both,gdIn .08s linear {sec(lg_t)} both,gdDim .5s ease-in {sec(T["RES"])} forwards{hide(lg_t)}">'
             + _img('gd_frame', 0, 36, F['w'], F['h'], 'gdfr')
             + f'<div class="gdlo" style="left:{lx:.1f}px;top:{ly:.1f}px;width:{G["w"]:g}px;height:{G["h"]:g}px">'
             f'<img src="{logo}" alt="" style="left:0;top:0;width:{G["w"]:g}px;height:{G["h"]:g}px">'
             f'<div class="gdsh" style="-webkit-mask-image:url({logo});mask-image:url({logo})"><i style="animation:gdShR 1s cubic-bezier(.45,0,.55,1) {sec(p1 + .15)} both"></i></div>{tw}</div></div>')
    return f'''<div class="gdC" aria-hidden="true" style="animation:{hide(T['WC'][1])[1:]}">
      <i class="gdcb"></i><i class="gdcr"></i>
      <div class="gdsp">{sparkles(40, 31)}</div>
      {ch}
      {group}
      <div class="gdnu" style="--nug:url({blob('gd_nug')});--cell:{LAY['gd_nug']['cell']}px;--sw:{LAY['gd_nug']['w']:g}px;--sh:{LAY['gd_nug']['h']:g}px">{nu}</div>
      {gl}
    </div>'''


def sparkles(n, seed):
    """白い 星の きらめき（暗い 背景の 上）"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        s = rng.uniform(10, 26)
        o += (f'<i style="left:{rng.uniform(0, 390) - s / 2:.0f}px;top:{rng.uniform(0, 844) - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;'
              f'animation-duration:{rng.uniform(1.1, 2.0):.2f}s;animation-delay:{rng.uniform(5.0, 7.0):.2f}s"></i>')
    return o


# ---------------------------------------------------------------- 層
def white(cls, w):
    t0, t1, t2, t3 = w
    d = t3 - t0
    k = cls
    return (f'<div class="gdw" aria-hidden="true" style="animation:gdW{k} {sec(d)} linear {sec(t0)} both{hide(t0, t3)}"></div>',
            f'@keyframes gdW{k}{{0%{{opacity:0}}{(t1 - t0) / d * 100:.1f}%{{opacity:1}}{(t2 - t0) / d * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}')


WHITES = (('a1', 'WA1'), ('a2', 'WA2'), ('b', 'WB'), ('c', 'WC'))


def gd_layers(board_html):
    """押したあと（下から）：① 青い 嵐 → ② 金の 字 → ③ 神様的中 → 白い 光 → ボード（board_html）"""
    T = GD_T
    wh = ''.join(white(k, T[n])[0] for k, n in WHITES)
    return f'''<div class="gdk" aria-hidden="true"></div>
    {scene_a()}
    {scene_b()}
    {scene_c()}
    {wh}
    <div class="hb">{board_html}</div>
    <p class="sr">神様的中！青い 嵐の 中で 光が はじけ、金色の 雲の 空に「万馬券（きせき）は偶然にあらず 天眼（テンゲル）が導く必然なり」。金の 粒が はじけて 神・様・的・中 → 金の 鳥居の 中に 神様的中</p>'''


def gd_css():
    T = GD_T
    wk = '\n'.join(white(k, T[n])[1] for k, n in WHITES)
    fr0, fr1 = T['FIRE']
    df = fr1 - fr0
    return f'''
/* ---------- 神様的中：kami.py（絵は flat/kami_art.py・雷・光の 帯・岩・光の つぶ・光は CSS と SVG） ---------- */
.ov.fz.gd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes gdH{{0%,100%{{visibility:hidden}}}}
@keyframes gdIn{{from{{opacity:0}}to{{opacity:1}}}}
.ov.gd .gdk{{position:absolute;inset:0;background:#000}}
.ov.gd .gdA,.ov.gd .gdB,.ov.gd .gdC{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}
.ov.gd img{{position:absolute;display:block;max-width:none}}
.ov.gd .gdA i,.ov.gd .gdB i,.ov.gd .gdC i{{position:absolute;display:block}}
/* ① 青い 嵐 */
.ov.gd .gdbu{{transform-origin:50% 46%}}
@keyframes gdBu{{0%{{opacity:0;transform:scale(.55)}}18%{{opacity:1}}100%{{opacity:1;transform:scale(1.3)}}}}
@keyframes gdFi{{0%{{opacity:1}}{(T['STORM'][0] + .06 - fr0) / df * 100:.0f}%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .gdpl{{position:absolute;left:105px;top:-10px;width:180px;height:740px;overflow:hidden;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 28%,#000 72%,transparent);mask-image:linear-gradient(90deg,transparent,#000 28%,#000 72%,transparent)}}
.ov.gd .gdpl i{{left:0;top:calc(-1 * var(--fh));width:100%;height:calc(100% + 2 * var(--fh));background-repeat:repeat-y;opacity:.42;animation:gdFall .9s linear infinite}}
@keyframes gdFall{{to{{transform:translateY(var(--fh))}}}}
.ov.gd .gdzap{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.gd .gdfk{{opacity:0}}
@keyframes gdFk{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .gdzap path{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
.ov.gd .zc{{stroke:#FFFFFF;stroke-width:1.2}}
.ov.gd .zhc{{stroke:#9BEFFF;stroke-width:3.2;stroke-opacity:.45}}
.ov.gd .zgc{{stroke:#58C8FF;stroke-width:8;stroke-opacity:.14}}
.ov.gd .zhp{{stroke:#FF8AE6;stroke-width:3.2;stroke-opacity:.45}}
.ov.gd .zgp{{stroke:#E040C8;stroke-width:8;stroke-opacity:.14}}
.ov.gd .gdbm path{{stroke-dasharray:100 100}}
.ov.gd .bg1{{stroke:url(#gdbmc);stroke-width:34;stroke-opacity:.16}}
.ov.gd .bg2{{stroke:url(#gdbmc);stroke-width:14;stroke-opacity:.55}}
.ov.gd .bg3{{stroke:url(#gdbmw);stroke-width:5}}
@keyframes gdBm{{from{{stroke-dashoffset:100}}to{{stroke-dashoffset:0}}}}
.ov.gd .gdbm{{animation-fill-mode:both}}
.ov.gd .gdbm path{{animation:inherit}}
@keyframes gdBo{{from{{opacity:1}}to{{opacity:0}}}}
.ov.gd .gdrk{{position:absolute;width:80px;height:80px;overflow:visible}}
@keyframes gdRk{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}12%{{opacity:1}}100%{{opacity:1;transform:translate(var(--dx),var(--dy)) scale(var(--s)) rotate(var(--r))}}}}
.ov.gd .gdmo{{position:absolute;inset:0}}
.ov.gd .gdmo i{{border-radius:50%;background:#BDF6FF;box-shadow:0 0 6px #3FD0FF;opacity:0;animation:gdMo 1s ease-out infinite}}
@keyframes gdMo{{0%{{opacity:0;transform:none}}20%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
@keyframes gdRg{{0%{{opacity:0;transform:scale(.3)}}22%{{opacity:1}}100%{{opacity:1;transform:scale(1.7)}}}}
/* 白い 光 */
.ov.gd .gdw{{position:absolute;inset:0;background:#FFFFFF;opacity:0;pointer-events:none;z-index:8}}
{wk}
/* ② 金の 字 */
.ov.gd .gdry{{left:50%;top:-120px;width:900px;height:900px;margin-left:-450px;opacity:.5;
  background:repeating-conic-gradient(from 150deg at 50% 0%,rgba(255,240,190,.5) 0deg 2.5deg,rgba(255,240,190,0) 5deg 9deg);
  -webkit-mask-image:radial-gradient(ellipse 50% 80% at 50% 0%,#000 10%,transparent 72%);mask-image:radial-gradient(ellipse 50% 80% at 50% 0%,#000 10%,transparent 72%)}}
.ov.gd .gdry2{{background:repeating-conic-gradient(from 152deg at 50% 0%,rgba(255,236,170,.45) 0deg 2deg,rgba(255,236,170,0) 4deg 11deg);animation:gdRy 2.4s ease-in-out infinite alternate}}
.ov.gd .gdry1{{animation:gdRy 2.4s ease-in-out -1.2s infinite alternate}}
@keyframes gdRy{{from{{opacity:.25}}to{{opacity:.6}}}}
.ov.gd .gdcu{{transform-origin:0 50%}}
@keyframes gdPan{{from{{transform:none}}to{{transform:translate(var(--dx),var(--dy)) scale(var(--z))}}}}
.ov.gd .gdtx{{position:absolute}}
@keyframes gdTx{{0%{{transform:scale(1.16)}}100%{{transform:none}}}}
.ov.gd .gdsh{{position:absolute;inset:0;overflow:hidden;-webkit-mask-size:100% 100%;mask-size:100% 100%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}}
.ov.gd .gdsh i{{top:-15%;height:130%;left:0;width:22%;background:linear-gradient(90deg,rgba(255,250,226,0),rgba(255,252,236,.9) 50%,rgba(255,250,226,0));transform:translateX(-140%) skewX(-18deg)}}
@keyframes gdShR{{0%{{transform:translateX(-140%) skewX(-18deg)}}100%{{transform:translateX(560%) skewX(-18deg)}}}}
.ov.gd .gdtw{{width:44px;height:44px;opacity:0;animation:gdTw 1.6s ease-in-out infinite;
  background:linear-gradient(90deg,transparent 46%,#FFFDF0 50%,transparent 54%),linear-gradient(0deg,transparent 46%,#FFFDF0 50%,transparent 54%),radial-gradient(circle,#FFFFFF 0 7%,rgba(255,226,140,.55) 16%,rgba(255,200,60,0) 42%);
  -webkit-mask-image:radial-gradient(circle,#000 18%,transparent 66%);mask-image:radial-gradient(circle,#000 18%,transparent 66%)}}
@keyframes gdTw{{0%,100%{{opacity:0;transform:scale(.2) rotate(0deg)}}45%{{opacity:1;transform:scale(1) rotate(30deg)}}70%{{opacity:0;transform:scale(.4) rotate(50deg)}}}}
.ov.gd .gdds{{position:absolute;inset:0}}
.ov.gd .gdds i{{border-radius:50%;background:#FFF2C0;box-shadow:0 0 6px #FFC21A;opacity:0;animation:gdDu 4s ease-in-out infinite}}
@keyframes gdDu{{0%{{opacity:0;transform:translateY(0)}}25%{{opacity:.9}}75%{{opacity:.7}}100%{{opacity:0;transform:translateY(var(--dy))}}}}
/* ③ 神様的中 */
.ov.gd .gdcb{{inset:0;background:radial-gradient(ellipse 80% 60% at 50% 48%,#5A1A08,#2A0904 55%,#0E0302)}}
.ov.gd .gdcr{{left:50%;top:50%;width:1000px;height:1000px;margin:-500px 0 0 -500px;opacity:.35;
  background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,190,80,.35) 0deg 3deg,rgba(255,190,80,0) 6deg 12deg);
  -webkit-mask-image:radial-gradient(circle,#000 8%,transparent 60%);mask-image:radial-gradient(circle,#000 8%,transparent 60%)}}
.ov.gd .gdsp{{position:absolute;inset:0}}
.ov.gd .gdsp i{{opacity:0;animation:gdTw 1.6s ease-in-out infinite;
  background:linear-gradient(90deg,transparent 46%,#FFFFFF 50%,transparent 54%),linear-gradient(0deg,transparent 46%,#FFFFFF 50%,transparent 54%),radial-gradient(circle,#FFFFFF 0 8%,rgba(255,230,160,.5) 18%,rgba(255,200,60,0) 45%);
  -webkit-mask-image:radial-gradient(circle,#000 18%,transparent 66%);mask-image:radial-gradient(circle,#000 18%,transparent 66%)}}
@keyframes gdCh{{from{{transform:translate(var(--x0),var(--y0))}}to{{transform:translate(var(--x1),var(--y1))}}}}
.ov.gd .gdlg{{position:absolute;inset:0}}
.ov.gd .gdlo{{position:absolute}}
@keyframes gdPull{{from{{transform:scale(var(--z))}}to{{transform:none}}}}
@keyframes gdDim{{to{{opacity:.3}}}}
.ov.gd .gdnu{{position:absolute;inset:0}}
.ov.gd .gdnu i{{width:var(--cell);height:var(--cell);background-image:var(--nug);background-size:var(--sw) var(--sh);opacity:0}}
@keyframes gdNu{{0%{{opacity:0;transform:translate(0,0) scale(var(--s0)) rotate(0)}}10%{{opacity:1}}85%{{opacity:1}}100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(var(--s1)) rotate(var(--r))}}}}
.ov.gd .gdgl{{left:50%;top:51%;width:900px;height:900px;margin:-450px 0 0 -450px;opacity:0;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0,#FFFBE0 14%,#FFE27A 30%,rgba(255,196,40,.6) 46%,rgba(255,170,0,0) 66%)}}
@keyframes gdGl1{{0%{{opacity:0;transform:scale(.5)}}20%{{opacity:1}}45%{{opacity:.95}}100%{{opacity:0;transform:scale(1.5)}}}}
@keyframes gdGl2{{0%{{opacity:0;transform:scale(.5)}}15%{{opacity:1}}45%{{opacity:.95}}100%{{opacity:0;transform:scale(1.7)}}}}
.ov.gd .hb{{z-index:10;animation:gdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .15)} both{hide(T['RES'] + .15)}}}
@keyframes gdBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 視差効果を減らす：① ② と 光・金の 粒を 出さない。③の 背景に 金の 鳥居と 神様／的中（動かさない）→ 1.3秒から ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.fz.gd{{--t0:1.9s}}
  .ov.gd .gdA,.ov.gd .gdB,.ov.gd .gdw,.ov.gd .gdnu,.ov.gd .gdgl,.ov.gd .gdch,.ov.gd .gdsp,.ov.gd .gdtw,.ov.gd .gdsh{{display:none}}
  .ov.gd .gdC{{animation:fadeIn .5s ease-out .2s both!important}}
  .ov.gd .gdlg{{animation:gdDim .5s ease-in 1.15s forwards!important}}
  .ov.gd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
