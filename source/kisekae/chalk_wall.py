"""黒板の壁紙の動き（まさちゃんの指定「1〜2で、黒板の馬を消して、3〜5秒でまた馬を黒板に書く、10秒に一度リピートで繰り返す。馬の絵の種類を3種類にする」）：
   ページに入れる HTML と CSS
   - 絵は flat/chalk_run.py の 馬のない黒板（chalk_base）と、馬3頭の ぬり（chalk_f）・外の線と地面の線（chalk_l）・消したあとの もや（chalk_z）。
     キャンバスでは /_blob/<id>（chalk_blobs.json）・置く場所と線は chalk_run.json。1つの <svg>（780×320 を 390×160 に）に重ねる
   - 10秒で1回り（CYCLE）・3頭で 30秒（LOOP）。0秒は いまの絵（馬1）。10秒ごとに（まさちゃん「もっとゆったりめで」→ 前の 約2倍の時間）：
     0.6〜1秒 黒板消しが 入ってくる → 1〜2.85秒 たてに ごしごし（頭 → しっぽ）して 馬を消す（こすった所は もやの残る黒板）→ 外へ。
     2.9秒から もやが ゆっくり うすくなる（9.5秒まで）→ 3.05〜3.45秒 チョークが 入ってくる → 3.45〜7.35秒 つぎの馬を書く
     （外の線を 鼻先から ひと回り → ゼッケンのふち（黄色のチョーク）→ 地面の線 → しっぽから頭へ ジグザグに ぬる）→ 外へ
   - 書く・消すは 線（stroke）の のび（stroke-dashoffset）：書く線は 馬の絵（pattern）で、消す線は もやの残る黒板（pattern）で ぬる。
     書きおわった 7.4秒に 同じ絵の <image> と入れかえ・消しおわった 2.9秒に もやだけの <image> と入れかえる（どちらも 見た目は同じ）
   - 黒板消し・チョークは ページの SVG。動きは 線の 点ごとの translate（線ののびと 同じ時刻）
   - 視差効果を減らす（prefers-reduced-motion）なら 動かさない（いまの絵：馬1）
   クラスの名前は cw…（的中ボタンの .kk とは別）
   python3 chalk_wall.py --judge <Judge_Chalk.dc.html> <chalk_blobs.json> <chalk_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 chalk_wall.py --plan <chalk_run.json>                                         → 時刻の表"""
import sys, re, json, math

ALT = ('黒板にチョークでかいた走る馬と、メモや星の落書き'
       '（10秒ごとに 黒板消しで 馬を消して、チョークで 書きなおす。馬は 走る馬・ゼッケンをつけた競走馬・立っている馬の 3つ）')
CYCLE = 10.0
N = 3
LOOP = CYCLE * N
# まさちゃん「消して、書く速度もっとゆったりめで！」→ 消すのも 書くのも 前の 約2倍の時間に（前は 消す 1〜1.95秒・書く 3〜4.92秒）
ERASE = (1.0, 2.85)                  # 消す（黒板消しが ごしごし）
SWAP_E = 2.9                         # 消しおわり → もやだけの絵に
TOOL_E = (0.6, 3.25)                 # 黒板消しが 見えている（入る・出るは 0.4秒）
HAZE_T = (2.9, 9.5)                  # もやが うすくなる
DRAW = (3.45, 7.35)                  # 書く
SWAP_D = 7.4                         # 書きおわり → 馬の絵に
TOOL_C = (3.05, 7.75)                # チョークが 見えている（入る・出るは 0.4秒）
PEN_UP = 0.13                        # 線と線のあいだ（チョークを はなして うつる）
FILL_SPEED = 1.3                     # ぬる ジグザグは 線より 何倍 はやいか
E_HOME = (800.0, 360.0)              # 黒板消しが 来る所・帰る所（外）
C_HOME = (812.0, 352.0)              # チョークが 来る所・帰る所（外）
STICK_EPS = 2.0                      # チョークの動きの 点の まとめ（780×320）
CHALK_COL = dict(w=('#F7F5EC', '#D8D4C6'), y=('#F6E27F', '#D6BF55'))
GROUND = '#D9D9CC'                   # 地面の線（いまの絵と同じ色：0.85, 0.85, 0.8）
DUST = 9                             # 黒板消しから 落ちる チョークの粉（1回に）
DUST_T = 0.6                         # 粉が 落ちて 消えるまで


def pct(t):
    s = f'{t / LOOP * 100:.4f}'.rstrip('0').rstrip('.')
    return (s or '0') + '%'


def num(v, nd=1):
    s = f'{v:.{nd}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def plen(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


def path_d(p):
    out = f'M{num(p[0][0])} {num(p[0][1])}'
    for (x0, y0), (x1, y1) in zip(p[:-1], p[1:]):
        out += f'l{num(x1 - x0)} {num(y1 - y0)}'
    return out


def snap(p):
    """点を 0.1 に まるめた 絶対座標（path_d の 相対の足し算と同じ点になるように）"""
    out = [(round(p[0][0], 1), round(p[0][1], 1))]
    for (x0, y0), (x1, y1) in zip(p[:-1], p[1:]):
        dx, dy = round(x1 - x0, 1), round(y1 - y0, 1)
        out.append((round(out[-1][0] + dx, 1), round(out[-1][1] + dy, 1)))
    return out


def dp(pts, eps):
    """点の列を まとめる（のこる点の 番号）"""
    keep = {0, len(pts) - 1}

    def rec(i, j):
        if j <= i + 1:
            return
        (x0, y0), (x1, y1) = pts[i], pts[j]
        L = math.hypot(x1 - x0, y1 - y0) or 1e-9
        best, bk = -1, -1
        for k in range(i + 1, j):
            x, y = pts[k]
            d = abs((x1 - x0) * (y0 - y) - (x0 - x) * (y1 - y0)) / L
            if d > best:
                best, bk = d, k
        if best > eps:
            keep.add(bk)
            rec(i, bk)
            rec(bk, j)
    rec(0, len(pts) - 1)
    return sorted(keep)


def seg_of(h):
    """馬 h（0〜2）を 書く・消す 10秒の番目"""
    return (h - 1) % N, h


def timeline(run):
    """馬ごとの 書く線の時刻 と チョーク・黒板消しの 動き。(horses, chalk_keys, eraser_keys)
       horses[h]：strokes=[(d, L, t0, t1, kind, col)]・erase=(d, L, t0, t1)・draw_seg・erase_seg"""
    out = []
    ck, ek = [], []           # (秒, x, y, 動き, 色)
    for h, hs in enumerate(run['horses']):
        sd, se = seg_of(h)
        st = [s for s in hs['strokes']]
        pts = [snap(s['pts']) for s in st]
        Ls = [plen(p) for p in pts]
        w = [(1.0 if s['kind'] == 'line' else 1 / FILL_SPEED) for s in st]
        t_all = DRAW[1] - DRAW[0] - PEN_UP * (len(st) - 1)
        unit = t_all / sum(L * k for L, k in zip(Ls, w))
        t = sd * CYCLE + DRAW[0]
        strokes = []
        for s, p, L, k in zip(st, pts, Ls, w):
            dt = L * k * unit
            strokes.append(dict(d=path_d(s['pts']), L=L, t0=t, t1=t + dt, kind=s['kind'], layer=s['layer'], col=s['col'], pts=p))
            t += dt + PEN_UP
        ep = snap(hs['erase'])
        e0, e1 = se * CYCLE + ERASE[0], se * CYCLE + ERASE[1]
        out.append(dict(strokes=strokes, erase=dict(d=path_d(hs['erase']), L=plen(ep), t0=e0, t1=e1, pts=ep), sd=sd, se=se))
    # チョーク：外 → 書きはじめ → 線にそって（点の時刻は 線ののびと同じ）→ つぎの線へ → 外
    for h, H in enumerate(out):
        base = H['sd'] * CYCLE
        S0 = H['strokes'][0]
        cin = (830.0, S0['pts'][0][1] + 70)
        ck.append((base + TOOL_C[0], *cin, 'ease-out', S0['col']))
        for s in H['strokes']:
            p = s['pts']
            cum = [0.0]
            for a, b in zip(p[:-1], p[1:]):
                cum.append(cum[-1] + math.dist(a, b))
            keep = dp(p, STICK_EPS)
            for i in keep:
                tt = s['t0'] + (s['t1'] - s['t0']) * (cum[i] / cum[-1] if cum[-1] else 0)
                ck.append((tt, p[i][0], p[i][1], 'linear' if i != keep[-1] else 'ease-in-out', s['col']))
        last = H['strokes'][-1]['pts'][-1]
        ck.append((base + TOOL_C[1], 830.0, last[1] + 90, 'linear', H['strokes'][-1]['col']))
    # 黒板消し：外 → 消しはじめ → たてに ごしごし（線ののびと同じ時刻）→ 外
    for h, H in enumerate(out):
        base = H['se'] * CYCLE
        E = H['erase']
        p = E['pts']
        cum = [0.0]
        for a, b in zip(p[:-1], p[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        ein = (880.0, p[0][1] - 30) if p[0][0] > 390 else (-100.0, p[0][1] - 30)        # 近い はしから 入る・出る
        eout = (-100.0, p[-1][1] + 40) if p[-1][0] < 390 else (880.0, p[-1][1] + 40)
        ek.append((base + TOOL_E[0], *ein, 'ease-out', -8))
        for i, q in enumerate(p):
            tt = E['t0'] + (E['t1'] - E['t0']) * cum[i] / cum[-1]
            tilt = 0 if i in (0, len(p) - 1) else (-3 if i % 4 in (1, 2) else 3)
            ek.append((tt, q[0], q[1], 'linear' if i < len(p) - 1 else 'ease-in', tilt))
        ek.append((base + TOOL_E[1], *eout, 'linear', 8))
    ck.sort(key=lambda k: k[0])
    ek.sort(key=lambda k: k[0])
    return out, ck, ek


def eraser_svg():
    """黒板消し（まん中が 消す所。はば78＝消す線のはば）：上は 紺の 持つ所・下は チョークの粉のついた フェルト（しまの層）"""
    return ('<g class="cwTw">'
            '<rect x="-37" y="-11" width="78" height="30" rx="6" fill="#000" opacity=".28"/>'
            '<rect x="-39" y="-1" width="78" height="15" rx="5" fill="#EDE8DC"/>'
            '<path d="M-36 6.5H36M-36 10H36" stroke="#C9C1AE" stroke-width="1.2"/>'
            '<path d="M-30 12.5l3-1M-12 13l4-1.5M9 12.5l3-1M27 13l4-1.5" stroke="#FFFFFF" stroke-width="1.3" stroke-linecap="round" opacity=".9"/>'
            '<rect x="-39" y="-15" width="78" height="18" rx="5" fill="#2F4F8C"/>'
            '<rect x="-36" y="-13" width="72" height="6" rx="3" fill="#4A6DB0"/>'
            '<path d="M-28 -2.5H28" stroke="#22396A" stroke-width="2.2" stroke-linecap="round"/>'
            '<rect x="-39" y="-15" width="78" height="29" rx="5" fill="none" stroke="#1C2B4A" stroke-width="1.4"/>'
            '</g>')


def at(p, cum, f):
    """点の列 p の 長さの わりあい f の所"""
    L = cum[-1] * f
    for i in range(1, len(p)):
        if cum[i] >= L:
            k = (L - cum[i - 1]) / ((cum[i] - cum[i - 1]) or 1)
            return (p[i - 1][0] + (p[i][0] - p[i - 1][0]) * k, p[i - 1][1] + (p[i][1] - p[i - 1][1]) * k)
    return p[-1]


def dust(H):
    """黒板消しから 落ちる チョークの粉：(html, css)。ごしごしの間に DUST こ・黒板消しの 下のふちから 下へ ふわっと落ちて 消える"""
    import random
    rnd = random.Random(7)
    html, css = '', ''
    for h, T in enumerate(H, 1):
        E = T['erase']
        p = E['pts']
        cum = [0.0]
        for a, b in zip(p[:-1], p[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        for i in range(DUST):
            f = (i + .5 + rnd.uniform(-.3, .3)) / DUST
            t = E['t0'] + (E['t1'] - E['t0']) * f
            x, y = at(p, cum, f)
            x += rnd.uniform(-30, 30)
            y += 14 + rnd.uniform(0, 4)
            r = rnd.uniform(2.2, 3.4)
            dx, dy = rnd.uniform(-10, 10), rnd.uniform(30, 52)
            c = f'cwP{h}{i}'
            html += f'<g transform="translate({num(x)} {num(y)})"><circle class="{c}" r="{num(r)}" fill="#EEF2EE"/></g>'
            css += (f'.cww .{c}{{opacity:0;animation:{c} {LOOP:g}s linear infinite}}'
                    + kf(c, [(0, (0, 0, 0), 'linear'), (t - .001, (0, 0, 0), 'linear'), (t, (0, 0, .85), 'cubic-bezier(.45,.05,.8,.6)'),
                             (t + DUST_T, (dx, dy, 0), 'linear'), (LOOP, (dx, dy, 0), 'linear')],
                         lambda v: f'transform:translate({num(v[0])}px,{num(v[1])}px);opacity:{num(v[2], 2)}'))
    return html, css


def chalk_svg(col):
    """チョーク（先が 0,0・右上へ のびる）"""
    c0, c1 = CHALK_COL[col]
    return (f'<g class="cwC{col}"><g transform="rotate(-52)">'
            f'<path d="M3.5 -4.6L42 -4.6Q44.6 0 42 4.6L3.5 4.6Q-.8 3.2 -.8 0Q-.8 -3.2 3.5 -4.6Z" fill="{c0}" stroke="#6E7A72" stroke-width=".9"/>'
            f'<path d="M5 2.2L41.2 2.2Q42.4 3.4 41.6 4.2L4.4 4.2Q2.6 3.6 2.4 2.6Z" fill="{c1}"/>'
            f'<ellipse cx="42.3" cy="0" rx="1.5" ry="4.4" fill="{c1}" opacity=".9"/>'
            '</g></g>')


def kf(name, keys, prop, default='linear'):
    """@keyframes（keys：(秒, 値, 次までの動き)）。動きが default（animation に書いた動き）と同じなら 書かない"""
    out, last = [], None
    for t, v, e in keys:
        p = pct(t)
        if p == last:
            continue
        out.append(f'{p}{{{prop(v)}' + (f';animation-timing-function:{e}' if e != default else '') + '}')
        last = p
    return f'@keyframes {name}{{' + ''.join(out) + '}'


def vis_keys(ranges):
    """見えている間（(はじめ, おわり) の秒・LOOP をまたいでもよい）→ visibility の keyframes の keys（1＝見える）"""
    iv = []
    for a, b in ranges:
        if b > LOOP:
            iv += [(a, LOOP), (0.0, b - LOOP)]
        else:
            iv.append((a, b))
    on = lambda t: any(a <= t < b for a, b in iv)
    ts = sorted({0.0} | {a for a, b in iv} | {b for a, b in iv if b < LOOP})
    keys, last = [], None
    for t in ts:
        v = 1 if on(t) else 0
        if v != last:
            keys.append((t, v, 'step-end'))
            last = v
    keys.append((LOOP, last, 'step-end'))
    return keys


def inline(blobs, run, alt=ALT):
    """(html, css)。html は <div class="bnr cww">（判定画面の <img class="bnr"> と入れかえる）"""
    H, ck, ek = timeline(run)
    wid = run['widths']
    ew = wid['erase']

    def im(href, b, cls=''):
        c = f' class="{cls}"' if cls else ''
        return f'<image{c} href="{href}" x="{b[0]}" y="{b[1]}" width="{b[2]}" height="{b[3]}" preserveAspectRatio="none"/>'

    def pat(pid, href, b):
        return f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="780" height="320">{im(href, b)}</pattern>'
    defs = ''
    body = '<image href="{0}" width="780" height="320" preserveAspectRatio="none"/>'.format(blobs['base'])
    for h, hs in enumerate(run['horses'], 1):
        defs += pat(f'cwF{h}', blobs[f'f{h}'], hs['fill']) + pat(f'cwL{h}', blobs[f'l{h}'], hs['line'])
        if 'cloth' in hs:
            defs += pat(f'cwY{h}', blobs[f'c{h}'], hs['cloth'])
        defs += (f'<pattern id="cwE{h}" patternUnits="userSpaceOnUse" width="780" height="320">'
                 f'<image href="{blobs["base"]}" width="780" height="320" preserveAspectRatio="none"/>{im(blobs[f"z{h}"], hs["haze"])}</pattern>')
    body += ''.join(im(blobs[f'z{h}'], hs['haze'], f'cwZ{h}') for h, hs in enumerate(run['horses'], 1))
    css = []
    LAYER = dict(f=('cwF', 'fill'), l=('cwL', 'line'), c=('cwY', 'cloth'), g=('cwG', 'ground'))
    for h, (hs, T) in enumerate(zip(run['horses'], H), 1):
        sd, se = T['sd'], T['se']
        gx0, gx1, gyc = hs['ground']
        x0, x1, gy = int(gx0) + 1, int(gx1) - 2, int(gyc - .5)            # いまの絵の 地面の線（cv2.line・太さ2）と 同じ画素
        gpoly = f'<path d="M{x0} {gy - 1}H{x1 + 1}V{gy}H{x1 + 2}V{gy + 1}H{x1 + 1}V{gy + 2}H{x0}V{gy + 1}H{x0 - 1}V{gy}H{x0}Z" fill="{GROUND}"/>'
        defs += f'<pattern id="cwG{h}" patternUnits="userSpaceOnUse" width="780" height="320">{gpoly}</pattern>'
        body += (f'<g class="cwI{h}">{im(blobs[f"f{h}"], hs["fill"])}{im(blobs[f"l{h}"], hs["line"])}'
                 + (im(blobs[f'c{h}'], hs['cloth']) if 'cloth' in hs else '') + gpoly + '</g>')
        order = sorted(range(len(T['strokes'])), key=lambda k: 'flcg'.index(T['strokes'][k]['layer']))     # 重なりは 絵と同じ順
        body += f'<g class="cwD{h}">'
        for k in order:
            s_ = T['strokes'][k]
            pre, wk = LAYER[s_['layer']]
            wd = wid[wk]
            paint = f'url(#{pre}{h})'
            L = s_['L']
            body += (f'<path class="cwR{h}{k}" d="{s_["d"]}" fill="none" stroke="{paint}" stroke-width="{num(wd)}" stroke-linecap="butt" '
                     f'stroke-linejoin="round" stroke-dasharray="{num(L + .5)} {num(L + wd + 8)}" stroke-dashoffset="{num(L + .5)}"/>')
            css.append(f'.cww .cwR{h}{k}{{animation:cwR{h}{k} {LOOP:g}s linear infinite}}'
                       + kf(f'cwR{h}{k}', [(0, L + .5, 'linear'), (s_['t0'], L + .5, 'linear'), (s_['t1'], 0, 'linear'), (LOOP, 0, 'linear')],
                            lambda v: f'stroke-dashoffset:{num(v)}px'))
        body += '</g>'
        E = T['erase']
        body += (f'<g class="cwX{h}"><path class="cwQ{h}" d="{E["d"]}" fill="none" stroke="url(#cwE{h})" stroke-width="{num(ew)}" stroke-linecap="butt" '
                 f'stroke-linejoin="round" stroke-dasharray="{num(E["L"] + .5)} {num(E["L"] + ew + 8)}" stroke-dashoffset="{num(E["L"] + .5)}"/></g>')
        css.append(f'.cww .cwQ{h}{{animation:cwQ{h} {LOOP:g}s linear infinite}}'
                   + kf(f'cwQ{h}', [(0, E['L'] + .5, 'linear'), (E['t0'], E['L'] + .5, 'linear'), (E['t1'], 0, 'linear'), (LOOP, 0, 'linear')],
                        lambda v: f'stroke-dashoffset:{num(v)}px'))
        # 見えている間
        rng = dict(I=[(sd * CYCLE + SWAP_D, se * CYCLE + SWAP_E + (LOOP if se * CYCLE + SWAP_E < sd * CYCLE + SWAP_D else 0))],
                   D=[(sd * CYCLE + DRAW[0] - 0.02, sd * CYCLE + SWAP_D)],
                   X=[(se * CYCLE + ERASE[0] - 0.02, se * CYCLE + SWAP_E)],
                   Z=[(se * CYCLE + SWAP_E, se * CYCLE + HAZE_T[1] + 0.05)])
        for c, r in rng.items():
            css.append(f'.cww .cw{c}{h}{{animation:cw{c}{h} {LOOP:g}s step-end infinite}}'
                       + kf(f'cw{c}{h}', vis_keys(r), lambda v: f'visibility:{"visible" if v else "hidden"}', 'step-end'))
        z0, z1 = se * CYCLE + HAZE_T[0], se * CYCLE + HAZE_T[1]
        css.append(f'.cww .cwZ{h}{{opacity:0;animation:cwZ{h} {LOOP:g}s step-end infinite,cwZo{h} {LOOP:g}s linear infinite}}'
                   + kf(f'cwZo{h}', [(0, 0, 'linear'), (z0 - .001, 0, 'linear'), (z0, 1, 'cubic-bezier(.3,0,.7,1)'), (z1, 0, 'linear'), (LOOP, 0, 'linear')],
                        lambda v: f'opacity:{num(v, 3)}'))
    # 黒板消し（と 落ちる粉）・チョーク
    dh, dc = dust(H)
    body += f'<g class="cwP">{dh}</g>'
    css.append(dc)
    body += f'<g class="cwT"><g class="cwTm">{eraser_svg()}</g></g>'
    body += f'<g class="cwC"><g class="cwCm">{chalk_svg("w")}{chalk_svg("y")}</g></g>'
    css.append(f'.cww .cwTm{{animation:cwTm {LOOP:g}s linear infinite}}'
               + kf('cwTm', [(0, (*E_HOME, 0), 'linear')] + [(t, (x, y, r), e) for t, x, y, e, r in ek] + [(LOOP, (*E_HOME, 0), 'linear')],
                    lambda v: f'transform:translate({num(v[0])}px,{num(v[1])}px) rotate({num(v[2])}deg)'))
    css.append(f'.cww .cwCm{{animation:cwCm {LOOP:g}s linear infinite}}'
               + kf('cwCm', [(0, C_HOME, 'linear')] + [(t, (x, y), e) for t, x, y, e, c in ck] + [(LOOP, C_HOME, 'linear')],
                    lambda v: f'transform:translate({num(v[0], 0)}px,{num(v[1], 0)}px)'))
    tool = dict(T=[(T['se'] * CYCLE + TOOL_E[0], T['se'] * CYCLE + TOOL_E[1]) for T in H],
                C=[(T['sd'] * CYCLE + TOOL_C[0], T['sd'] * CYCLE + TOOL_C[1]) for T in H])
    for c, r in tool.items():
        css.append(f'.cww .cw{c}{{animation:cw{c} {LOOP:g}s step-end infinite}}'
                   + kf(f'cw{c}', vis_keys(r), lambda v: f'visibility:{"visible" if v else "hidden"}', 'step-end'))
    # チョークの色（黄色の線の間だけ 黄色）
    yr = [(s['t0'] - PEN_UP * .5, s['t1'] + PEN_UP * .5) for T in H for s in T['strokes'] if s['col'] == 'y']
    if yr:
        css.append(f'.cww .cwCy{{animation:cwCy {LOOP:g}s step-end infinite}}'
                   + kf('cwCy', vis_keys(yr), lambda v: f'visibility:{"visible" if v else "hidden"}', 'step-end'))
        css.append(f'.cww .cwCw{{animation:cwCw {LOOP:g}s step-end infinite}}'
                   + kf('cwCw', [(t, 1 - v, e) for t, v, e in vis_keys(yr)], lambda v: f'visibility:{"visible" if v else "hidden"}', 'step-end'))
    hide = ['cwZ1', 'cwZ2', 'cwZ3', 'cwI2', 'cwI3', 'cwD1', 'cwD2', 'cwD3', 'cwX1', 'cwX2', 'cwX3', 'cwT', 'cwC', 'cwCy']
    html = (f'<div class="bnr cww" role="img" aria-label="{alt}"><svg viewBox="0 0 780 320" width="390" height="160" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<defs>{defs}</defs>{body}</svg></div>')
    css = ('.cww{position:relative;overflow:hidden}.cww svg{display:block;width:100%;height:100%}'
           + ','.join(f'.cww .{c}' for c in hide) + '{visibility:hidden}'
           + '.cww .cwTm,.cww .cwCm{transform-box:view-box;transform-origin:0 0}'
           + f'.cww .cwTm{{transform:translate({num(E_HOME[0])}px,{num(E_HOME[1])}px)}}.cww .cwCm{{transform:translate({num(C_HOME[0])}px,{num(C_HOME[1])}px)}}'
           + ''.join(css)
           + '@media (prefers-reduced-motion:reduce){.cww *{animation:none!important}}')
    return html, css


def judge_inline(fn, blobs, run, alt=ALT):
    """判定画面（Judge_Chalk.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr cww">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run, alt)
    page, k = re.subn(r'<div class="bnr cww" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 黒板の壁紙：10秒ごとに 黒板消しで 馬を消して、チョークで 書きなおす（3頭・chalk_wall.py） */\n{css}\n/* /黒板の壁紙 */\n'
    if '/* 黒板の壁紙：' in page:
        page = re.sub(r'/\* 黒板の壁紙：.*?/\* /黒板の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: (v if v.startswith('/_blob/') else f'/_blob/{v}') for k, v in json.load(open(fn)).items()}


def plan(run):
    H, ck, ek = timeline(run)
    for h, T in enumerate(H, 1):
        print(f'馬{h}：書く {T["sd"] * CYCLE + DRAW[0]:.2f}〜{T["strokes"][-1]["t1"]:.2f}秒・消す {T["erase"]["t0"]:.2f}〜{T["erase"]["t1"]:.2f}秒')
        for s in T['strokes']:
            print(f'   {s["kind"]:4s} {s["col"]} {s["t0"]:6.2f}〜{s["t1"]:6.2f}秒  長さ {s["L"]:7.1f}  はやさ {s["L"] / (s["t1"] - s["t0"]):6.0f}/秒')
        E = T['erase']
        print(f'   消す        {E["t0"]:6.2f}〜{E["t1"]:6.2f}秒  長さ {E["L"]:7.1f}  はやさ {E["L"] / (E["t1"] - E["t0"]):6.0f}/秒')
    print(f'チョークの点 {len(ck)}・黒板消しの点 {len(ek)}')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan(json.load(open(sys.argv[sys.argv.index('--plan') + 1])))
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
