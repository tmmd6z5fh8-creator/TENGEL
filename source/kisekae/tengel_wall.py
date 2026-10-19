"""マスター帯の壁紙の動き（まさちゃんの指定「常にテンゲルのアイコンの馬がアイコン上で走ってる、お尻から後ろ脚の当たりにある数字も常に動いている、
   全体的に緑の雷が枠全体にビリビリと輝いている」）：ページに入れる HTML と CSS
   - 絵は flat/tengel_run.py の 足と頭を ぬいた絵（plate）と、足（前足2本・後ろ足2本：それぞれ 上と下）・頭・体と騎手の 切りぬき。
     キャンバスでは /_blob/<id>（tengel_blobs.json）・置く場所と 回る中心・数字の場所は tengel_run.json。1つの <svg>（780×320 を 390×160 に）に重ねる
   - 馬が走る（GALLOP 秒で 1歩）：足は 上の部品が つけね（ひじ・もも）で、下の部品が ひざで まわる（下は 上に ついていく）。
     前足は「ふり出す → のばす → うしろへ かく → たたむ」・後ろ足は 半歩おくれて けりだす。頭は 足に合わせて 少し うなずく。
     足は 体のうしろを 通る（体と騎手の 切りぬきを 足の上に重ねる）
   - 数字：おしり（ドーム）・その左の行・後ろ足の下の行の 0と1 が、かわるがわる 反対の数字に（字のうしろの色で 前の字を かくして 書く）。
     かわる時は 右（馬）から 左へ 波のように 流れる（DIGIT_V）
   - 緑の雷：枠（上下左右のはし）に そって ぎざぎざの 光の線が ビリビリ（FLICK 秒ごとに 形が かわる・ところどころ とぎれる・内がわへ 小さく 枝わかれ）。
     まわりに 緑の光（ゆっくり 強く 弱く）。ときどき 枠から 中へ 大きな いなずまが 走る（BOLTS）。光るのは 細い線だけ（画面の 10% より ずっと小さい）
   - 視差効果を減らす（prefers-reduced-motion）なら 動かさない（いまの絵：雷も なし）
   クラスの名前は tq…（的中ボタンの .tg とは別）
   python3 tengel_wall.py --judge <Judge_Tengel.dc.html> <tengel_blobs.json> <tengel_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）"""
import sys, re, json, math, random

ALT = ('テンゲルの絵（金と紺の盾のエンブレムに、騎手を乗せて走る馬・上がるグラフ・王冠・データの数字と線、TENGER の金の文字・「独自の統計・オッズ分析による馬券検討支援システム」・「テンゲル」の金の札）'
       '（いつも エンブレムの馬が 走り、おしりから 後ろ足の まわりの 数字が 動いて、枠じゅうに 緑の雷が ビリビリ 光る）')
GALLOP = 0.52                   # 1歩（秒）
SWING = dict(                   # 部品の まわり方：(まん中の角度, ふれはば, ずれ（1歩の何割))。＋＝時計回り（足の先が うしろへ）
    FL1u=(0, 14, 0.0), FL1l=(-14, 24, 0.1), FL2u=(0, 12, 0.12), FL2l=(8, 18, 0.22),
    HL1u=(0, 9, 0.5), HL1l=(0, 14, 0.6), HL2=(0, 12, 0.4), HEAD=(0, 3.5, 0.3))
CHAIN = dict(FL1l='FL1u', FL2l='FL2u', HL1l='HL1u')       # 下の部品 → 上の部品（ひざから下は 上に ついていく）
STEPS = 16                      # 1歩の キーフレーム
DIGIT_P = (0.9, 1.3, 1.7, 2.1, 2.6)   # 数字が かわる 間（秒）
DIGIT_V = 70.0                  # 数字の かわる 波が 左へ 流れる 速さ（780×320 の座標／秒）
FLICK = 0.07                    # 雷の形が かわる 間（秒）
VARIANTS = 5                    # 雷の形の 数
INSET = 3.0                     # 枠から 内がわへ
GREEN = dict(core='#F4FFF8', mid='#6BFFAE', glow='#26FF82')
BOLT_LOOP = 12.0                # 大きな いなずまの 1回り（秒）
BOLTS = [(0.8, (520, 0), (478, 62)), (3.4, (780, 250), (712, 292)), (5.9, (0, 60), (85, 120)), (8.1, (300, 320), (330, 250)),
         (10.3, (640, 0), (612, 58))]   # (はじまる秒, 枠の点, 先の点)：TENGER の字の上は 通らない


def num(v, nd=2):
    s = f'{v:.{nd}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def pct(t, period):
    s = f'{t / period * 100:.3f}'.rstrip('0').rstrip('.')
    return (s or '0') + '%'


def vis_kf(name, ranges, period):
    """見えている間（(はじめ, おわり) 秒・1回りの中）→ visibility の @keyframes（step-end）"""
    iv = []
    for a, b in ranges:
        a, b = a % period, b % period if b % period else period
        if b <= a:
            iv += [(a, period), (0.0, b)]
        else:
            iv.append((a, b))
    on = lambda t: any(a <= t < b for a, b in iv)
    ts = sorted({0.0} | {a for a, b in iv} | {b for a, b in iv if b < period})
    out, last = [], None
    for t in ts:
        v = on(t)
        if v != last:
            out.append(f'{pct(t, period)}{{visibility:{"visible" if v else "hidden"}}}')
            last = v
    out.append(f'100%{{visibility:{"visible" if last else "hidden"}}}')
    return f'@keyframes {name}{{' + ''.join(out) + '}'


# ---------- 馬 ----------
def horse(blobs, run):
    """(svg, css)：足・体・頭"""
    P = run['parts']

    def img(k):
        x, y, w, h = P[k]['box']
        return f'<image href="{blobs[k.lower()]}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>'
    css = []
    for k, (m, a, ph) in SWING.items():
        px, py = P[k]['pivot']
        keys = ''.join(f'{pct(i * GALLOP / STEPS, GALLOP)}{{transform:rotate({num(m + a * math.sin(2 * math.pi * (i / STEPS - ph)), 2)}deg)}}'
                       for i in range(STEPS + 1))
        css.append(f'.tqw .tq{k}{{transform-box:view-box;transform-origin:{num(px)}px {num(py)}px;animation:tq{k} {GALLOP:g}s linear infinite}}'
                   f'@keyframes tq{k}{{{keys}}}')
    svg = ''
    for k in run['order']:
        if k in CHAIN:
            continue                                   # 上の部品の中に入れる
        if k == 'BODY':
            svg += img(k)
            continue
        low = [c for c, up in CHAIN.items() if up == k]
        inner = ''.join(f'<g class="tq{c}">{img(c)}</g>' for c in low)
        svg += f'<g class="tq{k}">{inner}{img(k)}</g>'
    return svg, ''.join(css)


# ---------- 数字 ----------
def glyph(kind, x, y, w, h, col):
    """0（たて長の まるい わく）・1（たての線と 上の小さな はた）"""
    sw = max(.8, h * .17)
    if kind == '0':
        return (f'<rect x="{num(x + sw / 2)}" y="{num(y + sw / 2)}" width="{num(max(.6, w - sw))}" height="{num(h - sw)}" rx="{num((w - sw) / 2)}" '
                f'fill="none" stroke="{col}" stroke-width="{num(sw)}"/>')
    cx = x + w / 2
    return (f'<path d="M{num(cx)} {num(y + h)}V{num(y)}l{num(-w * .42)} {num(h * .22)}" fill="none" stroke="{col}" stroke-width="{num(sw)}" '
            f'stroke-linecap="square" stroke-linejoin="miter"/>')


def digits(run):
    """(svg, css)：字ごとに 反対の数字（うしろの色の四角で 前の字を かくす）を かわるがわる 出す"""
    rnd = random.Random(19)
    xr = max(d['x'] + d['w'] for d in run['digits'])
    W0 = dict(D=3.76, L=3.76, B=4.52)
    W1 = 2.26
    svg, css = '', []
    for i, P in enumerate(DIGIT_P):
        css.append(vis_kf(f'tqD{i}', [(0, P * .5)], P))
    for d in run['digits']:
        new = '1' if d['k'] == '0' else '0'
        nw = W1 if new == '1' else W0[d['r']]
        cx = d['x'] + d['w'] / 2
        bx0 = min(d['x'], cx - nw / 2) - .7
        bx1 = max(d['x'] + d['w'], cx + nw / 2) + .7
        p = rnd.randrange(len(DIGIT_P))
        P = DIGIT_P[p]
        dl = ((xr - cx) / DIGIT_V + rnd.uniform(0, .25)) % P - P
        svg += (f'<g class="tqd tqD{p}" style="animation-delay:{num(dl, 3)}s"><rect x="{num(bx0)}" y="{num(d["y"] - .6)}" width="{num(bx1 - bx0)}" '
                f'height="{num(d["h"] + 1.2)}" fill="{d["b"]}"/>{glyph(new, cx - nw / 2, d["y"], nw, d["h"], d["c"])}</g>')
    css.append('.tqw .tqd{visibility:hidden;animation:tqD0 1s step-end infinite}' + ''.join(f'.tqw .tqD{i}{{animation-name:tqD{i};animation-duration:{P:g}s}}' for i, P in enumerate(DIGIT_P)))
    return svg, ''.join(css)


# ---------- 緑の雷 ----------
def jag(p0, p1, rnd, step=(5, 10), amp=3.0, spike=.2):
    """p0 → p1 の ぎざぎざの線の点"""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts, t = [(x0, y0)], 0.0
    while True:
        t += rnd.uniform(*step)
        if t >= L - 4:
            break
        a = rnd.uniform(-amp, amp) * (2.2 if rnd.random() < spike else 1)
        pts.append((x0 + ux * t + nx * a, y0 + uy * t + ny * a))
    pts.append((x1, y1))
    return pts


def pd(pts):
    return 'M' + 'L'.join(f'{num(x, 1)} {num(y, 1)}' for x, y in pts)


def frame_variant(rnd, W=780, H=320):
    """枠の雷の 1つの形：4辺を ぎざぎざに（ところどころ とぎれる）＋ 内がわへの 小さな枝"""
    i = INSET
    corners = [(i, i), (W - i, i), (W - i, H - i), (i, H - i)]
    inward = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    d = ''
    for e in range(4):
        a, b = corners[e], corners[(e + 1) % 4]
        d += pd(jag(a, b, rnd, step=(7, 14), amp=2.2, spike=.1))       # 細い もう1本（よりあわせる）
        pts = jag(a, b, rnd)
        # とぎれ：2〜4か所で 少し あける
        cuts = sorted(rnd.sample(range(2, max(3, len(pts) - 2)), k=min(len(pts) - 4, rnd.randint(2, 4)))) if len(pts) > 8 else []
        segs, cur = [], [pts[0]]
        for k, q in enumerate(pts[1:], 1):
            if k in cuts:
                if len(cur) > 1:
                    segs.append(cur)
                cur = [q]
            else:
                cur.append(q)
        if len(cur) > 1:
            segs.append(cur)
        d += ''.join(pd(sg) for sg in segs)
        # 枝
        for _ in range(rnd.randint(2, 5)):
            q = pts[rnd.randrange(1, len(pts) - 1)]
            ix, iy = inward[e]
            L = rnd.uniform(8, 26)
            ang = math.atan2(iy, ix) + rnd.uniform(-.9, .9)
            tip = (q[0] + math.cos(ang) * L, q[1] + math.sin(ang) * L)
            br = jag(q, tip, rnd, step=(3, 6), amp=1.8, spike=0)
            d += pd(br)
            if len(br) > 3 and rnd.random() < .5:                           # 枝の 枝
                q2 = br[len(br) // 2]
                a2 = ang + rnd.choice((-1, 1)) * rnd.uniform(.5, 1.1)
                d += pd(jag(q2, (q2[0] + math.cos(a2) * L * .5, q2[1] + math.sin(a2) * L * .5), rnd, step=(3, 5), amp=1.2, spike=0))
    return d


def lightning():
    """(svg, css)：枠の雷（VARIANTS 形を FLICK 秒ずつ）・まわりの 緑の光・ときどきの 大きな いなずま"""
    rnd = random.Random(7)
    svg, css, dfs = '', [], []
    period = FLICK * VARIANTS

    def bolt_paths(d, pid):
        """線は 1回だけ（<defs>）書いて、光の はば 4本を <use> で 重ねる"""
        dfs.append(f'<path id="{pid}" d="{d}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        return ''.join(f'<use href="#{pid}" stroke="{c}" stroke-width="{w}"{f" opacity={chr(34)}{o}{chr(34)}" if o else ""}/>'
                       for c, w, o in ((GREEN['glow'], 10, '.16'), (GREEN['glow'], 5, '.38'), (GREEN['mid'], 2.2, '.9'), (GREEN['core'], .95, '')))
    # まわりの 緑の光（4辺の グラデーション）
    svg += ('<g class="tqG"><rect width="780" height="22" fill="url(#tqGt)"/><rect y="298" width="780" height="22" fill="url(#tqGb)"/>'
            '<rect width="22" height="320" fill="url(#tqGl)"/><rect x="758" width="22" height="320" fill="url(#tqGr)"/></g>')
    css.append('.tqw .tqG{animation:tqG 1.6s ease-in-out infinite alternate}@keyframes tqG{from{opacity:.55}to{opacity:.95}}')
    for v in range(VARIANTS):
        svg += f'<g class="tqF tqF{v}">{bolt_paths(frame_variant(rnd), f"tqFp{v}")}</g>'
        css.append(f'.tqw .tqF{v}{{animation:tqF{v} {num(period, 3)}s step-end infinite}}' + vis_kf(f'tqF{v}', [(v * FLICK, (v + 1) * FLICK)], period))
    css.append('.tqw .tqF{visibility:hidden}')
    # 大きな いなずま
    for j, (t0, a, b) in enumerate(BOLTS):
        pts = jag(a, b, rnd, step=(7, 13), amp=6, spike=.25)
        fork = jag(pts[len(pts) // 2], (pts[len(pts) // 2][0] + rnd.uniform(-30, 30), pts[len(pts) // 2][1] + rnd.uniform(15, 30) * (1 if b[1] > a[1] else -1)),
                   rnd, step=(5, 9), amp=3, spike=0)
        svg += f'<g class="tqB tqB{j}">{bolt_paths(pd(pts) + pd(fork), f"tqBp{j}")}</g>'
        css.append(f'.tqw .tqB{j}{{animation:tqB{j} {BOLT_LOOP:g}s step-end infinite}}'
                   + vis_kf(f'tqB{j}', [(t0, t0 + .06), (t0 + .1, t0 + .2)], BOLT_LOOP))
    css.append('.tqw .tqB{visibility:hidden}')
    return svg, ''.join(css), ''.join(dfs)


def defs():
    g = GREEN['glow']
    lin = lambda i, x1, y1, x2, y2: (f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{g}" stop-opacity=".5"/>'
                                     f'<stop offset="1" stop-color="{g}" stop-opacity="0"/></linearGradient>')
    return lin('tqGt', 0, 0, 0, 1) + lin('tqGb', 0, 1, 0, 0) + lin('tqGl', 0, 0, 1, 0) + lin('tqGr', 1, 0, 0, 0)


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：banner・plate・部品（小文字）→ /_blob/<id>。html は <div class="bnr tqw">（判定画面の <img class="bnr"> と入れかえる）"""
    hs, hc = horse(blobs, run)
    ds, dc = digits(run)
    ls, lc, ld = lightning()
    im = lambda h: f'<image href="{h}" width="780" height="320" preserveAspectRatio="none"/>'
    # 帯の下に 1px の金の線（.bnr の border-bottom）があるので、上の絵は 上に そろえる（<img> の object-fit:cover と 同じ所に）
    html = (f'<div class="bnr tqw" role="img" aria-label="{alt}"><svg viewBox="0 0 780 320" width="390" height="160" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<defs>{defs()}{ld}</defs>{im(blobs["banner"])}<g class="tqA">{im(blobs["plate"])}{hs}{ds}{ls}</g></svg></div>')
    css = ('.tqw{position:relative;overflow:hidden}.tqw svg{display:block;width:100%;height:100%}'
           + hc + dc + lc
           + '@media (prefers-reduced-motion:reduce){.tqw *{animation:none!important}.tqw .tqA{visibility:hidden}}')
    return html, css


def judge_inline(fn, blobs, run, alt=ALT):
    """判定画面（Judge_Tengel.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr tqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run, alt)
    page, k = re.subn(r'<div class="bnr tqw" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* マスター帯の壁紙：アイコンの馬が走る・数字が動く・緑の雷（tengel_wall.py） */\n{css}\n/* /マスター帯の壁紙 */\n'
    if '/* マスター帯の壁紙：' in page:
        page = re.sub(r'/\* マスター帯の壁紙：.*?/\* /マスター帯の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: (v if v.startswith('/_blob/') else f'/_blob/{v}') for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
