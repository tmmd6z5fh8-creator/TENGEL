"""星座・ペガサスの壁紙の動き（まさちゃんの指定「背景の星が動く・常にペガサスがキラキラしてる」）：ページに入れる HTML と CSS
   - 下の絵（flat/pegasus_banner.py --base：いまの絵から うしろの小さい星700こだけを ぬいたもの。夜空・天の川・三日月・ペガサスはそのまま）の上に、
     同じ星（同じ場所・同じ明るさ・1画素の点）を SVG で描いて、右から左へ ゆっくり流す（ペガサスが右へかけていくように）。
     明るい星（手前）は速く・暗い星（奥）はゆっくり（2つの速さで奥行き）。1画素ずつ動く（steps）ので点がにじまない。
     星は三日月のうしろを通る（三日月の所は mask でかくす）。光は足し算（mix-blend-mode: plus-lighter）なので、止まった所は いまの絵と同じ
   - ペガサスの明るい星（星座の21こ）が かわるがわる きらっと光って回る・外の線の上の小さい星を 光がぐるっと走る
   - 8秒に1回、鼻の頭から しっぽの先へ 星が つぎつぎに キラキラ（まさちゃんの指定「8秒に一回、鼻の頭から尻尾の先に向けて、星がキラキラ輝く演出」）：
     鼻 → 頭 → 首 → 背中 → おしり → しっぽの先（星座の線と 外の線の しっぽ）の道すじ（spine）を 金の光の玉（尾を引く）が SWEEP_S 秒で進み、
     星座の星・外の線の星・道すじの上に足した 小さい星が、道すじの いちばん近い所を 光が通った時に キラッ・キラッ と2回（足や翼の星は 道すじから はなれているほど 少しおくれて）
   - 視差効果を減らす（prefers-reduced-motion）なら止まって、キラキラも消える（いまの絵と同じ）
   - キャンバスでは下の絵は /_blob/<id>（stars_blobs.json の base）・星の位置は stars_pts.json（flat/pegasus_banner.py --base が書く）
   クラスの名前は sz…（的中ボタンの .sz・.szp などとは別の名前）
   python3 stars_wall.py --judge <Judge_Stars.dc.html> <stars_blobs.json> <stars_pts.json>  → 判定画面の上の絵を「流れる星とキラキラ」に書きかえる（何回やっても同じ）"""
import sys, re, json

ALT = '天の川の夜空に、星をむすんだ翼のある馬の星座と三日月のイラスト（うしろの星がゆっくり流れ、ペガサスの星がきらきら光る。8秒に1回 鼻の頭から しっぽの先へ 星がキラキラ）'
NEAR_V = 0.55                  # これより明るい星は手前（速く流れる）
NEAR_S, FAR_S = 40, 100        # 絵のはば（780）ぶん流れる秒（手前・奥）
TW_S, GL_S = 2.6, 4.0          # 明るい星が きらっとする1回の秒・外の線を光が1周する秒
SW_S, SWEEP_S, SW_T0 = 8.0, 1.8, 2.0   # 鼻から しっぽへの キラキラ：何秒に1回・鼻から しっぽの先まで 進む秒・ページを開いて はじめの秒
SW_DRIP, SW_FAR = 0.45, 160.0  # 道すじから はなれた星の おくれ（いちばん おくれる秒・その はなれ方：絵の画素）
SPINE_CON, SPINE_DOTS = (0, 1, 2, 3, 4, 5, 6), (17, 18, 19, 20, 21)   # 道すじ：鼻先（外の線 63）→ 星座の 0〜6 → 外の線の しっぽ 17〜21（先）
NOSE_DOT = 63
SW_EXTRA = 30                  # 道すじの上に足す 小さい星
SW_TRAIL = ((1, 1), (.78, .55), (.6, .38), (.45, .25), (.32, .15))   # 光の玉と 尾（大きさ・こさ。0.05秒ずつ おくれて ついていく）
Q = 0.025                      # 星の明るさの きざみ


def _f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def star_tiles(bg):
    """うしろの星：奥（暗い）と手前（明るい）の2まい。明るさごとに1本の path（1画素の四角＝太さ1の線で長さ1）"""
    out = {}
    for name, sel in (('F', lambda v: v < NEAR_V), ('N', lambda v: v >= NEAR_V)):
        groups = {}
        for x, y, v in sorted(bg, key=lambda t: (t[1], t[0])):
            if sel(v):
                groups.setdefault(round(round(v / Q) * Q, 3), []).append(f'M{x} {y}.5h1')
        out[name] = ''.join(f'<path d="{"".join(d)}" stroke-opacity="{_f(min(v, 1))}"/>' for v, d in sorted(groups.items()))
    return out


def sparkle(L, w=.07):
    """4本の光（細い）"""
    w = L * w
    return f'M0 {-L:g}Q{w:.2f} {-w:.2f} {L:g} 0Q{w:.2f} {w:.2f} 0 {L:g}Q{-w:.2f} {w:.2f} {-L:g} 0Q{-w:.2f} {-w:.2f} 0 {-L:g}Z'


def spine(pts):
    """鼻の頭から しっぽの先への 道すじ（折れ線・絵の座標）"""
    P = [pts['dots'][NOSE_DOT][:2]] + [pts['con'][i][:2] for i in SPINE_CON] + [pts['dots'][i][:2] for i in SPINE_DOTS]
    return [(float(x), float(y)) for x, y in P]


def along(P, q):
    """点 q に いちばん近い 道すじの所：(鼻からの道のり, はなれ方)"""
    best, s0 = (1e9, 0.0), 0.0
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((q[0] - ax) * dx + (q[1] - ay) * dy) / L2))
        cx, cy = ax + dx * t, ay + dy * t
        d = ((q[0] - cx) ** 2 + (q[1] - cy) ** 2) ** .5
        if d < best[0]:
            best = (d, s0 + t * L2 ** .5)
        s0 += L2 ** .5
    return best[1], best[0]


def sweep_stars(pts):
    """鼻から しっぽへの キラキラ：[(x, y, 大きさ, おくれ秒)]（星座の星・外の線の星・道すじの上の小さい星）"""
    import random
    P = spine(pts)
    total = sum(((bx - ax) ** 2 + (by - ay) ** 2) ** .5 for (ax, ay), (bx, by) in zip(P, P[1:]))
    out = []
    def add(x, y, L):
        s_, d = along(P, (x, y))
        out.append((x, y, L, SW_T0 + s_ / total * SWEEP_S + SW_DRIP * min(d / SW_FAR, 1.0)))
    for x, y, big in pts['con']:
        add(x, y, 30 if big else 22)
    for x, y, big in pts['dots']:
        add(x, y, 18 if big else 14)
    rnd = random.Random(7)
    cum = [0.0]
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        cum.append(cum[-1] + ((bx - ax) ** 2 + (by - ay) ** 2) ** .5)
    for k in range(SW_EXTRA):
        s_ = total * (k + .5 + rnd.uniform(-.3, .3)) / SW_EXTRA
        i = max(j for j in range(len(P) - 1) if cum[j] <= s_)
        t = (s_ - cum[i]) / (cum[i + 1] - cum[i])
        (ax, ay), (bx, by) = P[i], P[i + 1]
        nx, ny = -(by - ay), bx - ax
        nl = (nx * nx + ny * ny) ** .5
        j = rnd.uniform(-9, 9)
        add(ax + (bx - ax) * t + nx / nl * j, ay + (by - ay) * t + ny / nl * j, rnd.choice((12, 15, 18)))
    return out


def comet_kf(pts):
    """金の光の玉が 道すじを進む キーフレーム（SW_S 秒の中の %：はじめの SWEEP_S 秒で 鼻の頭 → しっぽの先・同じ速さ）"""
    P = spine(pts)
    cum = [0.0]
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        cum.append(cum[-1] + ((bx - ax) ** 2 + (by - ay) ** 2) ** .5)
    run = SWEEP_S / SW_S * 100
    kf = ''.join(f'{_f(c / cum[-1] * run)}%{{transform:translate({x:.1f}px,{y:.1f}px)}}' for c, (x, y) in zip(cum, P))
    kf += f'100%{{transform:translate({P[-1][0]:.1f}px,{P[-1][1]:.1f}px)}}'
    op = f'0%{{opacity:0}}{_f(run * .06)}%{{opacity:1}}{_f(run * .9)}%{{opacity:1}}{_f(run * 1.04)}%,100%{{opacity:0}}'
    return '@keyframes szCm{' + kf + '}@keyframes szCo{' + op + '}'


def svg(pts, p='sz'):
    W, H = pts['size']
    (mx, my, mr), (sx, sy, sr) = pts['moon']
    tiles = star_tiles(pts['bg'])
    gold = (5 ** .5 - 1) / 2
    shapes = ''
    for big, L in ((1, 25), (0, 17)):                                # 明るい星の きらっ（大・小）：にじむ光・先へ うすくなる細い4本の光・ななめの短い光・まん中の点
        shapes += (f'<g id="{p}K{big}"><circle r="{L * .26:.1f}" fill="url(#{p}kr)" opacity=".75"/>'
                   f'<ellipse rx="{L}" ry="{L * .065:.2f}" fill="url(#{p}kr)"/><ellipse rx="{L * .065:.2f}" ry="{L}" fill="url(#{p}kr)"/>'
                   f'<g transform="rotate(45)" opacity=".55"><ellipse rx="{L * .4:.1f}" ry="{L * .04:.2f}" fill="url(#{p}kr)"/><ellipse rx="{L * .04:.2f}" ry="{L * .4:.1f}" fill="url(#{p}kr)"/></g>'
                   f'<circle r="1.4" fill="#FFFFFF"/></g>')
    for big, r in ((1, 9.0), (0, 7.0)):                              # 外の線の光（大・小）
        shapes += (f'<g id="{p}G{big}"><circle r="{r * .45:.1f}" fill="url(#{p}kr)" opacity=".9"/>'
                   f'<ellipse rx="{r}" ry="{r * .11:.2f}" fill="url(#{p}kr)"/><ellipse rx="{r * .11:.2f}" ry="{r}" fill="url(#{p}kr)"/></g>')
    shapes += (f'<g id="{p}S"><circle r="5.5" fill="url(#{p}vr)"/>'                                  # 鼻から しっぽへの キラキラ（長さ 20・使う所で のばす）：金の光
               f'<ellipse rx="20" ry="1.3" fill="url(#{p}vr)"/><ellipse rx="1.3" ry="20" fill="url(#{p}vr)"/>'
               f'<g transform="rotate(45)" opacity=".7"><ellipse rx="9" ry=".9" fill="url(#{p}vr)"/><ellipse rx=".9" ry="9" fill="url(#{p}vr)"/></g>'
               f'<circle r="1.7" fill="#FFFFFF"/></g>')
    shapes += (f'<g id="{p}C"><circle r="17" fill="url(#{p}cr)"/>'                                   # 金の光の玉（道すじを進む）
               f'<ellipse rx="15" ry="1" fill="url(#{p}vr)"/><ellipse rx="1" ry="15" fill="url(#{p}vr)"/><circle r="2.6" fill="#FFFFFF"/></g>')
    kira = ''
    for i, (x, y, big) in enumerate(pts['con']):                     # 星座の明るい星：かわるがわる きらっと光って回る
        d = -((i * gold) % 1) * TW_S
        kira += f'<g transform="translate({x:g} {y:g})"><use class="{p}k" href="#{p}K{big}" style="animation-delay:{d:.2f}s"/></g>'
    n = len(pts['dots'])
    for i, (x, y, big) in enumerate(pts['dots']):                    # 外の線の上の小さい星：光がぐるっと走る
        d = -(i / n) * GL_S
        kira += f'<use class="{p}g" href="#{p}G{big}" x="{x:.1f}" y="{y:.1f}" style="animation-delay:{d:.2f}s"/>'
    for k, (sc, op) in reversed(list(enumerate(SW_TRAIL))):          # 鼻から しっぽへ：金の光の玉と 尾（うしろの尾から 重ねる）
        kira += (f'<g class="{p}c" style="animation-delay:{SW_T0 + k * .05:.2f}s"><use href="#{p}C"'
                 + (f' transform="scale({sc:g})" opacity="{op:g}"' if k else '') + '/></g>')
    for x, y, L, d in sweep_stars(pts):                              # 光の玉が 通った所の星が キラッ・キラッ（SW_S 秒に1回）
        kira += (f'<g transform="translate({x:.1f} {y:.1f}) scale({L / 20:.2f})"><use class="{p}v" href="#{p}S" '
                 f'style="animation-delay:{d:.2f}s"/></g>')
    defs = (f'<defs><mask id="{p}mm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
            f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#000000"/><circle cx="{sx}" cy="{sy}" r="{sr}" fill="#FFFFFF"/></mask>'
            f'<g id="{p}F">{tiles["F"]}</g><g id="{p}N">{tiles["N"]}</g></defs>')
    defs2 = (f'<defs><radialGradient id="{p}kr"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".3" stop-color="#FFF6DE" stop-opacity=".9"/>'
             f'<stop offset="1" stop-color="#FFE7A8" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="{p}vr"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".3" stop-color="#FFF0BE" stop-opacity=".95"/>'
             f'<stop offset="1" stop-color="#FFD27A" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="{p}cr"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".22" stop-color="#FFF2C6" stop-opacity=".9"/>'
             f'<stop offset=".55" stop-color="#FFD983" stop-opacity=".35"/><stop offset="1" stop-color="#FFC861" stop-opacity="0"/></radialGradient>{shapes}</defs>')
    flow = (f'<g mask="url(#{p}mm)" fill="none" stroke="#FFFFFF" stroke-width="1">'
            f'<g class="{p}r"><use href="#{p}F"/><use href="#{p}F" x="{W}"/></g>'
            f'<g class="{p}n"><use href="#{p}N"/><use href="#{p}N" x="{W}"/></g></g>')
    return (f'<svg class="{p}s" viewBox="0 0 {W} {H}" width="390" height="160" aria-hidden="true">{defs}{flow}</svg>'
            f'<svg class="{p}x" viewBox="0 0 {W} {H}" width="390" height="160" aria-hidden="true">{defs2}{kira}</svg>')


def inline(blobs, pts, alt=ALT):
    """(html, css)。blobs：base（下の絵）→ '/_blob/<id>'。pts：stars_pts.json"""
    W = pts['size'][0]
    html = f'<div class="szw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt="">{svg(pts)}</div>'
    css = ('.szw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;isolation:isolate}'
           '.szw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           '.szw .szs,.szw .szx{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           '.szw .szs{mix-blend-mode:plus-lighter}'
           '.szw .szr,.szw .szn,.szw .szk,.szw .szg,.szw .szv,.szw .szc{transform-box:view-box;transform-origin:0 0}'
           f'.szw .szr{{animation:szFlow {FAR_S}s steps({W}) infinite}}'
           f'.szw .szn{{animation:szFlow {NEAR_S}s steps({W}) infinite}}'
           f'@keyframes szFlow{{to{{transform:translateX(-{W}px)}}}}'
           f'.szw .szk{{opacity:0;animation:szTw {TW_S}s ease-in-out infinite}}'
           '@keyframes szTw{0%,100%{opacity:0;transform:scale(.2) rotate(0deg)}45%{opacity:1;transform:scale(1) rotate(45deg)}70%{opacity:.55;transform:scale(.6) rotate(70deg)}}'
           f'.szw .szg{{opacity:0;animation:szGl {GL_S}s linear infinite}}'
           '@keyframes szGl{0%{opacity:0}6%{opacity:1}22%{opacity:0}100%{opacity:0}}'
           f'.szw .szv{{opacity:0;animation:szSw {SW_S:g}s ease-out infinite}}'
           '@keyframes szSw{0%{opacity:0;transform:scale(.2) rotate(0deg)}1.5%{opacity:1;transform:scale(1.15) rotate(20deg)}3%{opacity:.3;transform:scale(.7) rotate(32deg)}'
           '4.5%{opacity:.95;transform:scale(1) rotate(44deg)}7%{opacity:.35;transform:scale(.7) rotate(58deg)}9%,100%{opacity:0;transform:scale(.35) rotate(66deg)}}'
           f'.szw .szc{{opacity:0;animation:szCm {SW_S:g}s linear infinite,szCo {SW_S:g}s linear infinite}}'
           + comet_kf(pts) +
           '@media (prefers-reduced-motion:reduce){.szw .szr,.szw .szn{animation:none}.szw .szk,.szw .szg,.szw .szv,.szw .szc{display:none}}')
    return html, css


def judge_inline(fn, blobs, pts):
    """判定画面（Judge_Stars.dc.html）の上の絵を「流れる星とキラキラ」に書きかえる（<img class="bnr"> か、前に入れた <div class="szw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, pts)
    page, n = re.subn(r'<div class="szw" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 星座の壁紙：星が流れて、ペガサスがきらきら（stars_wall.py） */\n{css}\n/* /星座の壁紙 */\n'
    if '/* 星座の壁紙：' in page:
        page = re.sub(r'/\* 星座の壁紙：.*?/\* /星座の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
