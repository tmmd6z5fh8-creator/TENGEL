"""神様的中（まさちゃんの指定）：3連単の 当たりの 3頭に 超大穴（10〜12番人気）と、ほかに 大穴以上（7〜12番人気）が 1頭 以上 いる 時 ※仮
   まさちゃん（第4.44版）「スタート一個目の動画にして、次に、二個目の動画にして、文章に 万馬券（きせき）は偶然にあらず 天眼（テンゲル）が導く必然なり
   を入れて！ 三個目の動画をその後に入れて、GODの文字を、神様的中にして！ 全く同じような演出で一度作成してみて！」
   送ってくれた 3つの 動画と 同じ 流れで、絵と 音は 一から 作った（動画の 絵・音・字・ロゴは 使わない・なぞらない）。
   第4.45版「一枚目の青の爆破エフェクト、色の線やじりじりを球体の周りを走る電気をもっと乱雑な線にして！ 球体の周りを走る電気は、もっと球体を全体的に包むようにして！
   ビリビリ感増して！ 二枚目のブロックは一つ一つももっと立体的に金色の爆発エフェクトも混ぜ合わせてみて！」
   第4.46版「まずは、この一枚目の演出完全させよ！ 送った二枚目の動画が求めてる映像！ この動き、広がり方、光の具合、迫力を求める！ ここは、全力で頼む」
   → ① の 青い 嵐を 1つめの 動画の 動き・広がり方・光・迫力に 合わせて 一から 作り直した（絵は flat/kami_storm.py）
   押した あと（0秒＝押した 瞬間）：
     ① 青い 嵐：光の 爆発 → 白 → 赤い 炎の 一瞬 → 青い 嵐（太い 光の 滝と しぶき・ガラスの ような 光の ドームが 床から ひろがって ゆっくり 大きく・ピンクの 電気の 光・
        画面を 横切る 大きな 雷・ドームの ふちの ジリジリと 肩の ピンクの 電気・白い 光の 帯・とんでくる 岩）→ 立体の 金の 輪と 金の 爆発・金の 粒 → 白
     ② 金の 字：金の 雲の 空に 金の 立体の 字。「万馬券（きせき）」の 寄り → 「天眼（テンゲル）」の 寄り → 白 → 4行の 文「万馬券（きせき）は／偶然にあらず／天眼（テンゲル）が導く／必然なり」
     ③ 神様的中：白 → 金の 粒が はじけて「神」の 寄り → 金の 粒 →「様」→ 金の 粒 →「的」→ 金の 粒 →「中」→ 金の 粒の 大爆発の 中に「神様／的中」→ ひいて 金の 鳥居 → ボード
   絵：flat/kami_art.py・flat/kami_storm.py（キャンバスの アセット：id は kami_blobs.json・大きさは kami_layers.json）。ほかは CSS と SVG（電気・雷・光の つぶ・光）
   点めつ：画面の 大きな 光は 白（押した 瞬間・①→②・②の 中・②→③）と ③の 金の 粒の 大きい 爆発（3回）だけ。どの 1秒にも 3回 以下"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/kami_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
GD_T = dict(BURST=(0.0, .24),                      # ① 光の 爆発
            WA1=(.02, .1, .16, .34),               # 白（はじまり・まっ白・まっ白の おわり・消える）
            FIRE=(.12, .4),                        # 赤い 炎の 一瞬
            STORM=(.3, 1.66),                      # 青い 嵐
            DOME=(.4, .66, 1.44),                  # 光の ドーム：ふくらみ はじめ・ふくらみ おわり（ここから ゆっくり 大きく）・おわり
            SURGE=(.44, .47, .53, .66),            # ピンクの 電気の 光（出る・いちばん 明るい・まだ 明るい・消える）
            CRACK=(.58, 1.42),                     # ドームの ふちの ジリジリ・肩の ピンクの 電気・ドームを はしる 電気
            BOLTS=(.5, .62, .76, .92, 1.08, 1.2),  # 大きな 雷（BOLT_D）
            ROCKS=(.4, .56, .72, .9, 1.08),        # とんでくる 岩
            RING=(1.24, 1.66),                     # 金の 輪（立体の かたまり）と 金の 爆発・金の 粒
            WA2=(1.44, 1.58, 1.66, 1.84),          # 白（① → ②）
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


def _pdi(pts):
    """みじかく 書いた path（1px に まるめて・となりとの ちがいで）：たくさんの 電気でも ページが 重く ならない ように"""
    q = [(round(x), round(y)) for x, y in pts]
    o = f'M{q[0][0]} {q[0][1]}l'
    px, py = q[0]
    st = []
    for x, y in q[1:]:
        if (x, y) != (px, py):
            st.append(f'{x - px} {y - py}')
            px, py = x, y
    return o + ' '.join(st) if st else ''


DOME2 = (195.0, 716.0, 186.0, 418.0)         # 光の ドーム（ガラスの ような ドーム）：まん中の x・床の y・床での 半径・高さ（画面の px）
DOME_P, DOME_Q = 2.3, 2.6                    # ドームの 形（下は ほぼ まっすぐ 立ち、上が まるい）
RIBBONS = ((((104, -40), (62, 230), (160, 470), (116, 790)), .3, 1.06),        # 白い 光の 帯：(ベジェの 4点（画面の px）, 出る 秒, 消える 秒)
           (((292, -40), (338, 250), (226, 500), (266, 790)), .36, .94),
           (((176, -40), (132, 270), (236, 520), (184, 780)), .62, 1.4),
           (((334, -40), (296, 270), (366, 500), (320, 770)), .96, 1.42),
           (((44, -40), (12, 300), (112, 530), (66, 800)), 1.08, 1.42),
           (((236, -40), (270, 240), (198, 480), (240, 760)), .74, 1.2))
BOLT_D = (((14, 800), (382, 110), 'c'), ((40, -12), (92, 360), 'c'), ((376, 20), (360, 600), 'c'),
          ((330, -12), (232, 320), 'p'), ((14, 40), (30, 560), 'p'), ((150, -12), (286, 330), 'p'))
# 大きな 雷（GD_T の BOLTS の 時刻）：(はじめ, おわり, 色 c＝水色・p＝ピンク)


def dome_r(h):
    """床からの 高さ h（画面の px：数 か numpy の 配列）→ その 高さの ドームの 半径"""
    RX, HD = DOME2[2], DOME2[3]
    if hasattr(h, 'shape'):
        import numpy as np
        u = np.clip(h / HD, 0, 1)
        return RX * np.clip(1 - u ** DOME_Q, 0, 1) ** (1 / DOME_P)
    u = max(0.0, min(1.0, h / HD))
    return RX * max(0.0, 1 - u ** DOME_Q) ** (1 / DOME_P)


BOLT_ROUGH = (.16, .2, .26, .4, .52, .58, .6)      # 大きな 雷の ギザギザ（あらい 段 → 細かい 段：大きく うねらず 細かく ギザギザ）


def _disp_ms(rng, a, b, rough):
    """段ごとの ギザギザ（rough：段ごとの ずれの 大きさ）"""
    pts = [a, b]
    for r in rough:
        nw = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            off = rng.gauss(0, r * L / 2)
            nw += [((ax + bx) / 2 + nx * off, (ay + by) / 2 + ny * off), (bx, by)]
        pts = nw
    return pts


def dome_outline(n=520):
    """ドームの ふち（左の 床 → てっぺん → 右の 床）を 長さ 等分の 点で → [(x, y, 外向きの nx, ny, 高さの 割合 u)]"""
    cx, base, RX, HD = DOME2
    hs = [HD * (i / 1600) ** .7 for i in range(1601)]
    left = [(cx - dome_r(h), base - h) for h in hs]
    pts = left + [(2 * cx - x, y) for x, y in reversed(left[:-1])]
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    L = acc[-1]
    out = []
    j = 0
    for i in range(n + 1):
        s = L * i / n
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        f = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f
        tx, ty = pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]
        tl = math.hypot(tx, ty) or 1.0
        out.append((x, y, ty / tl, -tx / tl, (base - y) / HD))
    return out


def _jag(rng, pts, rough, depth=3):
    """点の 列を ギザギザに（となりの 点の 間を さらに ずらす）"""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        out += _disp(rng, a, b, depth, rough)[1:]
    return out


def flick(t, dur, inner, cls='gdfk'):
    return f'<g class="{cls}" style="animation:gdFk {sec(dur)} linear {sec(t)} forwards{hide(t, t + dur)}">{inner}</g>'


# ---------------------------------------------------------------- ドームの 電気（ふちの ジリジリ・肩の ピンクの 電気・ドームを はしる 電気）
CR_DT = .05                    # ドームの 電気の 1コマ（ここごとに ジリジリと 小さな パチッが かわる）
CR_LIFE = 5                    # ピンクの 電気・ドームを はしる 電気が 光る コマ数（0.25秒：光って いる 間は 同じ 所で ふるえる）
CR_SIZZLE, CR_NEW = 18, 3      # 1コマの ふちの ジリジリの 数・コマごとに 新しく 出る ピンクの 電気の かたまり（いつも 約15）


def cr_frames():
    """ドームの 電気の コマの 時刻 [(時刻, 左右（-1〜1）)]（音も この 時刻で 鳴らす：gen_sfx.py）"""
    t0, t1 = GD_T['CRACK']
    rng = random.Random(5)
    ev = []
    t = t0
    while t < t1 - .01:
        ev.append((round(t, 3), round(rng.uniform(-.7, .7), 2)))
        t += CR_DT
    return ev


def _spread_ok(o, f):
    """はじめの 4コマは てっぺんから 床へ ひろがる（f：はじまってからの コマ）"""
    w = min(.5, .07 + .11 * f)
    return abs(o - .5) <= w


def rim_sizzle(rng, OL, n, f):
    """ふちの ジリジリ（ふちの 上で 小さく はじける ギザギザ 4〜12px）→ path"""
    d = ''
    N = len(OL)
    k = 0
    while k < n:
        o = rng.random()
        if not _spread_ok(o, f):
            continue
        x, y, nx, ny, u = OL[int(o * (N - 1))]
        ang = math.atan2(ny, nx) + rng.uniform(-1.2, 1.2)
        ln = rng.uniform(4, 12)
        p0 = (x + nx * rng.uniform(-2, 2), y + ny * rng.uniform(-2, 2))
        d += _pdi(_disp(rng, p0, (p0[0] + ln * math.cos(ang), p0[1] + ln * math.sin(ang)), 2, .9))
        k += 1
    return d


CRK_ROUGH = (.3, .5, .6)        # ピンクの 電気の ギザギザ（小さな 雷の かけら）


def crackle(rng, OL, f):
    """肩の ピンクの 電気の かたまり（ふちの 内がわ 5〜40px：小さな ギザギザ 3〜5本）→ (path, 中心)"""
    N = len(OL)
    while True:
        o = rng.random()
        x, y, nx, ny, u = OL[int(o * (N - 1))]
        if u > .3 and _spread_ok(o, f):
            break
    dep = rng.uniform(5, 40)
    c = (x - nx * dep, y - ny * dep)
    d = ''
    a0 = rng.uniform(0, 2 * math.pi)
    for j in range(rng.randint(3, 5)):
        a = a0 + j * 2.1 + rng.uniform(-.5, .5)
        ln = rng.uniform(10, 30)
        p0 = (c[0] + rng.uniform(-3, 3), c[1] + rng.uniform(-3, 3))
        main = _disp_ms(rng, p0, (p0[0] + ln * math.cos(a), p0[1] + ln * math.sin(a)), CRK_ROUGH)
        d += _pdi(main)
        if rng.random() < .7:
            q = main[rng.randint(1, len(main) - 2)]
            a2 = a + rng.choice((-1, 1)) * rng.uniform(.5, 1.2)
            l2 = ln * rng.uniform(.3, .55)
            d += _pdi(_disp_ms(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), CRK_ROUGH[1:]))
    return d, c


def surface_arc(rng, side):
    """ドームの 表面を はしる 電気（ふちから 内へ・球に そって 曲がる ギザギザの 線）→ 点の 列"""
    cx, base, RX, HD = DOME2
    h0 = rng.uniform(.28, .9) * HD
    ph0 = side * 88.0
    ph1 = side * rng.uniform(12, 58)
    h1 = max(14.0, min(HD * .93, h0 + rng.uniform(-.38, .22) * HD))
    pts = []
    for j in range(25):
        u = j / 24
        h = h0 + (h1 - h0) * u
        ph = math.radians(ph0 + (ph1 - ph0) * u)
        pts.append((cx + dome_r(h) * math.sin(ph), base - h))
    return _jag(rng, pts, rng.uniform(.3, .45), 2)


def arc_branches(rng, main):
    d = ''
    for _ in range(rng.randint(3, 6)):
        p = main[rng.randint(len(main) // 8, len(main) * 7 // 8)]
        a = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(8, 30)
        br = _disp(rng, p, (p[0] + ln * math.cos(a), p[1] + ln * math.sin(a)), 3, .6)
        d += _pdi(br)
    return d


def twitch(rng, pts, n, lo=4, hi=10):
    """そのコマだけ パチッと 出る とても 小さな 電気 → path"""
    d = ''
    for _ in range(n):
        p = pts[rng.randrange(len(pts))]
        a = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(lo, hi)
        d += _pdi(_disp(rng, p, (p[0] + ln * math.cos(a), p[1] + ln * math.sin(a)), 2, .9))
    return d


def dome_elec():
    """ドームの 電気（ドームと いっしょに 大きく なる）：
       ・ふちの ジリジリ（白と 水色・コマごとに かわる 小さな ギザギザ）
       ・肩の ピンクの 電気（かたまりは 0.15秒 同じ 所で ふるえて 消える・コマごとに 4つ 出る）
       ・ドームの 表面を はしる 電気（0.1秒ごとに 左右 かわるがわる・0.15秒）
       はじめの 4コマで てっぺんから 床へ ひろがる"""
    OL = dome_outline()
    rng = random.Random(77)
    ev = cr_frames()
    cl, arcs = [], []
    g, defs = '', ''
    for f, (t, pan) in enumerate(ev):
        for _ in range(CR_NEW):
            d, c = crackle(rng, OL, f)
            cl.append((f, d, c))
        if f % 3 == 0:
            side = 1 if (f // 3) % 2 else -1
            pts = surface_arc(rng, side)
            arcs.append((f, _pdi(pts) + arc_branches(rng, pts), pts, rng.choice('cv')))
        by = dict(c=rim_sizzle(rng, OL, CR_SIZZLE, f), p='', v='')
        for f0, d, c in cl:
            if f0 <= f < f0 + CR_LIFE:
                by['p'] += d + twitch(rng, [c], 1, 3, 8)
        for f0, d, pts, tone in arcs:
            if f0 <= f < f0 + CR_LIFE:
                by[tone] += d + twitch(rng, pts, 2)
        inner = ''
        for tone, d in by.items():
            if d:
                defs += f'<path id="gde{f}{tone}" d="{d}"/>'
                inner += ''.join(f'<use href="#gde{f}{tone}" class="{c}"/>' for c in (f'eg{tone}', f'eh{tone}', 'ec'))
        g += flick(t, CR_DT, inner)
    return f'<defs>{defs}</defs>{g}'


def bolt2(seed, a, b, branches=9):
    """大きな 雷（本線は まっすぐ 走って 細かく ギザギザ・えだは 前へ ひらく・小えだ つき）→ path"""
    rng = random.Random(seed)
    main = _disp_ms(rng, a, b, BOLT_ROUGH)
    d = _pdi(main)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    base = math.atan2(b[1] - a[1], b[0] - a[0])
    for _ in range(branches):
        i = rng.randint(len(main) // 8, len(main) * 7 // 8)
        p = main[i]
        ang = base + rng.choice((-1, 1)) * rng.uniform(.35, .9)
        ln = rng.uniform(.1, .3) * L
        q = (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang))
        br = _disp_ms(rng, p, q, BOLT_ROUGH[1:])
        d += _pdi(br)
        if rng.random() < .6:
            j = rng.randint(len(br) // 4, len(br) * 3 // 4)
            p2 = br[j]
            a2 = ang + rng.choice((-1, 1)) * rng.uniform(.3, .8)
            l2 = ln * rng.uniform(.3, .55)
            d += _pdi(_disp_ms(rng, p2, (p2[0] + l2 * math.cos(a2), p2[1] + l2 * math.sin(a2)), BOLT_ROUGH[3:]))
    return d


def big_bolts():
    """大きな 雷（画面を 横切る：白い しん＋水色 か ピンクの 光）：1本 0.08秒（同じ 所は 1回だけ 光る）"""
    g, defs = '', ''
    for k, (t, (a, b, tone)) in enumerate(zip(GD_T['BOLTS'], BOLT_D)):
        d = bolt2(700 + k * 13, a, b)
        defs += f'<path id="gdb{k}" d="{d}"/>'
        g += (f'<g class="gdbt" style="animation:gdBt .09s linear {sec(t)} forwards{hide(t, t + .09)}">'
              + ''.join(f'<use href="#gdb{k}" class="{c}"/>' for c in (f'bb{tone}', f'bm{tone}', f'bg{tone}', f'bh{tone}', 'bc')) + '</g>')
    return f'<defs>{defs}</defs>{g}'


def ribbons():
    """白い 光の 帯（上から 下へ のびて 出る・ゆっくり ゆれる・消える）：絵は gd_rib（1まいに ならべた もの）"""
    L = LAY['gd_rib']
    o = ''
    for (p, t0, t1), (sx, x, y, w, h) in zip(RIBBONS, L['pos']):
        st = (f'left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;'
              f'animation:gdRbIn .14s cubic-bezier(.2,.7,.4,1) {sec(t0)} both,gdRbOut .2s ease-in {sec(t1 - .2)} forwards{hide(t0, t1)}')
        o += f'<i style="{st}"><i style="background-position:-{sx:g}px 0;animation:gdRbSw 1.3s ease-in-out {sec(t0)} infinite alternate"></i></i>'
    return o


def splash(n, seed):
    """光の 滝の 下の しぶき（床から 上と 左右へ とぶ 光の 粒）"""
    rng = random.Random(seed)
    o = ''
    cx, base = DOME2[0], DOME2[1]
    for _ in range(n):
        x = cx + rng.gauss(0, 30)
        y = base + rng.uniform(-8, 2)
        s = rng.uniform(1.6, 3.6)
        ang = rng.uniform(-math.pi * .94, -math.pi * .06)
        sp = rng.uniform(40, 150)
        o += (f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dx:{math.cos(ang) * sp * 1.4:.0f}px;--dy:{math.sin(ang) * sp * .75:.0f}px;'
              f'animation-duration:{rng.uniform(.45, .8):.2f}s;animation-delay:{rng.uniform(.32, 1.0):.2f}s"></i>')
    return o


def rim_sparks(n, seed):
    """ドームの ふちから 外へ とぶ 小さな 光の 粒（水色 と ピンク）"""
    OL = dome_outline(200)
    rng = random.Random(seed)
    c0, c1 = GD_T['CRACK']
    o = ''
    for _ in range(n):
        while True:
            x, y, nx, ny, u = OL[rng.randrange(len(OL))]
            if u > .12:
                break
        ang = math.atan2(ny, nx) + rng.uniform(-.6, .6)
        ln = rng.uniform(16, 46)
        pk = 'p' if u > .45 and rng.random() < .4 else 'c'
        o += (f'<i class="{pk}" style="left:{x - 1:.0f}px;top:{y - 1:.0f}px;--dx:{ln * math.cos(ang):.0f}px;--dy:{ln * math.sin(ang) + 10:.0f}px;'
              f'animation-duration:{rng.uniform(.32, .55):.2f}s;animation-delay:{rng.uniform(c0, c0 + .55):.2f}s"></i>')
    return o


def rocks():
    """とんでくる 岩（暗い 紺・うしろからの 水色の ふちの 光：gd_rock）：ドームの 前から 手前へ（大きく なって 画面の 外へ）"""
    L = LAY['gd_rock']
    cell = L['cell']
    o = ''
    rng = random.Random(9)
    for k, t in enumerate(GD_T['ROCKS']):
        side = -1 if k % 2 == 0 else 1
        x0, y0 = 195 + side * rng.uniform(20, 70), rng.uniform(330, 520)
        dx, dy = side * rng.uniform(220, 300), rng.uniform(-300, 140)
        dur = rng.uniform(.42, .56)
        o += (f'<i class="gdrk" style="left:{x0 - cell / 2:.0f}px;top:{y0 - cell / 2:.0f}px;background-position:-{(k % L["n"]) * cell:g}px 0;'
              f'--dx:{dx:.0f}px;--dy:{dy:.0f}px;--r:{side * rng.uniform(70, 160):.0f}deg;--s:{rng.uniform(1.4, 2.1):.1f};'
              f'animation:gdRk {sec(dur)} cubic-bezier(.5,0,.9,.6) {sec(t)} both{hide(t, t + dur)}"></i>')
    return o


def scene_a():
    T = GD_T
    st0, st1 = T['STORM']
    fa, fb = LAY['gd_fall'], LAY['gd_fmask']
    ring, bl = LAY['gd_ring'], LAY['gd_blast']
    dm = LAY['gd_dome']
    r0, r1 = T['RING']
    d0, d1, d2 = T['DOME']
    s0, s1, s2, s3 = T['SURGE']
    sd = s3 - s0
    return f'''<div class="gdA" aria-hidden="true" style="animation:{hide(t1=T['WA2'][1])[1:]}">
      {_img('gd_storm', 0, 0, W_, H_, 'gdst', f'animation:gdIn .1s linear {sec(st0)} both{hide(st0)}')}
      {_img('gd_vein1', 0, 0, W_, H_, 'gdvn', f'animation:gdVn .9s ease-in-out {sec(st0)} infinite alternate both{hide(st0)}')}
      {_img('gd_vein2', 0, 0, W_, H_, 'gdvn', f'animation:gdVn .9s ease-in-out {sec(st0 - .9)} infinite alternate both{hide(st0)}')}
      <div class="gdwf" style="left:{fb['x']:g}px;top:{fb['y']:g}px;width:{fb['w']:g}px;height:{fb['h']:g}px;-webkit-mask-image:url({blob('gd_fmask')});mask-image:url({blob('gd_fmask')});animation:gdIn .12s linear {sec(st0)} both{hide(st0)}"><i class="f2" style="background-image:url({blob('gd_fall')});--fh:{fa['h'] * 1.45:g}px;background-size:{fa['w'] * 1.45:g}px {fa['h'] * 1.45:g}px"></i><i class="f1" style="background-image:url({blob('gd_fall')});--fh:{fa['h']:g}px;background-size:{fa['w']:g}px {fa['h']:g}px"></i></div>
      <div class="gdsq">{splash(46, 4)}</div>
      <i class="gdsw" style="animation:gdSw .5s cubic-bezier(.15,.7,.3,1) {sec(d0)} both{hide(d0, d0 + .5)}"></i>
      <div class="gddm" style="animation:gdDm {sec(d1 - d0)} cubic-bezier(.12,.8,.25,1) {sec(d0)} both{hide(d0)}"><div class="gddm2" style="animation:gdDm2 {sec(d2 - d1)} linear {sec(d1)} both">
        {_img('gd_dome', dm['x'], dm['y'], dm['w'], dm['h'], 'gddg')}
        <svg class="gdel" viewBox="0 0 390 844" aria-hidden="true">{dome_elec()}</svg>
        <div class="gdrs" style="animation:{hide(T['CRACK'][0])[1:]}">{rim_sparks(40, 12)}</div>
      </div></div>
      <div class="gdrb" style="--rib:url({blob('gd_rib')});--rw:{LAY['gd_rib']['w']:g}px;--rh:{LAY['gd_rib']['h']:g}px">{ribbons()}</div>
      {_img('gd_surge', 0, 0, W_, H_, 'gdsg', f'animation:gdSg {sec(sd)} linear {sec(s0)} both{hide(s0, s3)}')}
      <svg class="gdbo" viewBox="0 0 390 844" aria-hidden="true">{big_bolts()}</svg>
      <div class="gdrks" style="--rock:url({blob('gd_rock')});--cell:{LAY['gd_rock']['cell']:g}px;--rkw:{LAY['gd_rock']['w']:g}px;--rkh:{LAY['gd_rock']['h']:g}px">{rocks()}</div>
      {_img('gd_fire', 0, 0, W_, H_, 'gdfi', f'animation:gdFi {sec(T["FIRE"][1] - T["FIRE"][0])} linear {sec(T["FIRE"][0])} both{hide(T["FIRE"][0], T["FIRE"][1])}')}
      {_img('gd_burst', 0, 0, W_, H_, 'gdbu', f'animation:gdBu {sec(T["BURST"][1])} cubic-bezier(.2,.8,.3,1) 0s both{hide(None, T["BURST"][1])}')}
      {_img('gd_blast', FX - bl['w'] / 2, 422 - bl['h'] / 2, bl['w'], bl['h'], 'gdbl', f'animation:gdBl {sec(r1 - r0)} cubic-bezier(.2,.7,.35,1) {sec(r0)} both{hide(r0, r1)}')}
      {_img('gd_ring', FX - ring['w'] / 2, 422 - ring['h'] / 2, ring['w'], ring['h'], 'gdrg', f'animation:gdRg {sec(r1 - r0)} cubic-bezier(.3,.6,.4,1) {sec(r0)} both{hide(r0, r1)}')}
      <div class="gdnu" style="--nug:url({blob('gd_nug')});--cell:{LAY['gd_nug']['cell']}px;--sw:{LAY['gd_nug']['w']:g}px;--sh:{LAY['gd_nug']['h']:g}px">{nug_burst(r0 + .04, 3, 33, FX, 422)}</div>
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
    """金の 粒の 爆発：まん中から 手前へ（大きく なって 画面の 外へ）。kind 0＝大きな 粒が いくつか 手前を 横切る（字の かわり目を かくす）・1＝大・2＝いちばん 大・
       3＝① の 金の 輪と いっしょの 金の 爆発（少なめ：点めつの ため）"""
    L = LAY['gd_nug']
    cell = L['cell']
    rng = random.Random(seed)
    n = (6, 18, 28, 10)[kind]
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
/* ① 青い 嵐（第4.46版：ガラスの ドーム・光の 滝・白い 光の 帯・電気・大きな 雷・ピンクの 光・岩） */
.ov.gd .gdbu{{transform-origin:50% 46%}}
@keyframes gdBu{{0%{{opacity:0;transform:scale(.55)}}18%{{opacity:1}}100%{{opacity:1;transform:scale(1.3)}}}}
@keyframes gdFi{{0%{{opacity:1}}{(T['STORM'][0] + .06 - fr0) / df * 100:.0f}%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .gdvn{{opacity:0}}
@keyframes gdVn{{from{{opacity:.3}}to{{opacity:.95}}}}
.ov.gd .gdwf{{position:absolute;overflow:hidden;-webkit-mask-size:100% 100%;mask-size:100% 100%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}}
.ov.gd .gdwf i{{left:0;top:calc(-1 * var(--fh));width:100%;height:calc(100% + var(--fh));background-repeat:repeat-y;background-position:50% 0;animation:gdFall .5s linear infinite}}
.ov.gd .gdwf i.f2{{opacity:.5;animation-duration:.95s}}
@keyframes gdFall{{to{{transform:translateY(var(--fh))}}}}
.ov.gd .gdsq{{position:absolute;inset:0}}
.ov.gd .gdsq i{{border-radius:50%;background:#E6FDFF;box-shadow:0 0 5px 1px #3FD4FF;opacity:0;animation:gdSq 1s cubic-bezier(.2,.65,.4,1) infinite}}
@keyframes gdSq{{0%{{opacity:0;transform:none}}12%{{opacity:1}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
.ov.gd .gdsw{{left:135px;top:702px;width:120px;height:28px;border-radius:50%;border:2px solid rgba(200,250,255,.95);box-shadow:0 0 14px 4px rgba(70,200,255,.75),inset 0 0 12px 3px rgba(70,200,255,.6);opacity:0}}
@keyframes gdSw{{0%{{opacity:0;transform:scale(.2)}}15%{{opacity:1}}100%{{opacity:0;transform:scale(3.6)}}}}
.ov.gd .gddm,.ov.gd .gddm2{{position:absolute;inset:0;transform-origin:{DOME2[0]:g}px {DOME2[1]:g}px}}
@keyframes gdDm{{0%{{opacity:0;transform:scale(.06)}}14%{{opacity:1}}100%{{opacity:1;transform:none}}}}
@keyframes gdDm2{{from{{transform:none}}to{{transform:scale(1.18)}}}}
.ov.gd .gdel,.ov.gd .gdbo{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.gd .gdfk{{opacity:0}}
@keyframes gdFk{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .gdel path,.ov.gd .gdbo path{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
.ov.gd .ec{{stroke:#FFFFFF;stroke-width:1}}
.ov.gd .ehc{{stroke:#A8F2FF;stroke-width:2.6;stroke-opacity:.42}}
.ov.gd .egc{{stroke:#46C8FF;stroke-width:6;stroke-opacity:.1}}
.ov.gd .ehp{{stroke:#FF6FDC;stroke-width:3;stroke-opacity:.62}}
.ov.gd .egp{{stroke:#FF30C8;stroke-width:8;stroke-opacity:.16}}
.ov.gd .ehv{{stroke:#C0A6FF;stroke-width:2.8;stroke-opacity:.45}}
.ov.gd .egv{{stroke:#8A5CFF;stroke-width:6.5;stroke-opacity:.12}}
.ov.gd .gdbt{{opacity:0}}
@keyframes gdBt{{0%,70%{{opacity:1}}100%{{opacity:0}}}}
.ov.gd .bc{{stroke:#FFFFFF;stroke-width:2.4}}
.ov.gd .bhc{{stroke:#D8F8FF;stroke-width:4.6;stroke-opacity:.5}}
.ov.gd .bgc{{stroke:#8FDCFF;stroke-width:10;stroke-opacity:.13}}
.ov.gd .bmc{{stroke:#5FB0FF;stroke-width:20;stroke-opacity:.11}}
.ov.gd .bbc{{stroke:#4A7CFF;stroke-width:32;stroke-opacity:.06}}
.ov.gd .bhp{{stroke:#FFD0F4;stroke-width:4.6;stroke-opacity:.5}}
.ov.gd .bgp{{stroke:#FF6EDA;stroke-width:10;stroke-opacity:.15}}
.ov.gd .bmp{{stroke:#E040E0;stroke-width:20;stroke-opacity:.12}}
.ov.gd .bbp{{stroke:#A030FF;stroke-width:32;stroke-opacity:.065}}
.ov.gd .gdrs{{position:absolute;inset:0}}
.ov.gd .gdrs i{{width:2.2px;height:2.2px;border-radius:50%;background:#FFFFFF;box-shadow:0 0 4px 1px #6FE0FF;opacity:0;animation:gdRs .5s ease-out infinite}}
.ov.gd .gdrs i.p{{box-shadow:0 0 4px 1px #FF5CD6}}
@keyframes gdRs{{0%{{opacity:1;transform:none}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
.ov.gd .gdrb{{position:absolute;inset:0}}
.ov.gd .gdrb i i{{inset:0;background-image:var(--rib);background-size:var(--rw) var(--rh);background-repeat:no-repeat}}
@keyframes gdRbIn{{from{{opacity:0;transform:translateY(-170px)}}to{{opacity:1;transform:none}}}}
@keyframes gdRbSw{{from{{transform:translateX(-3px)}}to{{transform:translateX(3px)}}}}
@keyframes gdRbOut{{to{{opacity:0}}}}
.ov.gd .gdsg{{opacity:0}}
@keyframes gdSg{{0%{{opacity:0}}{(T['SURGE'][1] - T['SURGE'][0]) / (T['SURGE'][3] - T['SURGE'][0]) * 100:.0f}%{{opacity:1}}{(T['SURGE'][2] - T['SURGE'][0]) / (T['SURGE'][3] - T['SURGE'][0]) * 100:.0f}%{{opacity:.85}}100%{{opacity:0}}}}
.ov.gd .gdrks{{position:absolute;inset:0}}
.ov.gd .gdrk{{width:var(--cell);height:var(--cell);background-image:var(--rock);background-size:var(--rkw) var(--rkh)}}
@keyframes gdRk{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}12%{{opacity:1}}100%{{opacity:1;transform:translate(var(--dx),var(--dy)) scale(var(--s)) rotate(var(--r))}}}}
@keyframes gdRg{{0%{{opacity:0;transform:scale(.86)}}22%{{opacity:1}}100%{{opacity:1;transform:scale(1.14)}}}}
@keyframes gdBl{{0%{{opacity:0;transform:scale(.6)}}18%{{opacity:1}}100%{{opacity:1;transform:scale(1.5)}}}}
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
