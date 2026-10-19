"""マスター帯の壁紙の動き（まさちゃんの指定「お尻から後ろ脚の当たりにある数字も常に動いている、全体的に緑の雷が枠全体にビリビリと輝いている」・
   2回目「濃い緑のビリビリも混ぜて、それぞれ消えたりついたり・ピクセル1番細い線に」）：ページに入れる HTML と CSS
   エンブレムの 馬は 動かさない（まさちゃんの指定「やっぱりテンゲルのアイコンは動かさなくていいや・アイコン、元のように戻して」）。
   上の絵は いまの絵（tengel_blobs.json の banner）の まま、その上に 数字と 雷を 重ねる（1つの <svg>：780×320 を 390×160 に）
   - 数字：おしり（ドーム）・その左の行・後ろ足の下の行の 0と1 が、かわるがわる 反対の数字に（字のうしろの色で 前の字を かくして 書く）。
     かわる時は 右（馬）から 左へ 波のように 流れる（DIGIT_V）。場所と 色は tengel_run.json（flat/tengel_run.py）
   - 緑の雷：明るい緑と 濃い緑の いなずまが 枠に そって いくつも（EDGE_N 本）。1本ずつ べつべつに ついたり 消えたり
     （1回に 2〜7回 ちらちら光って、そのたび 形が かわる・つく間かくも 1本ずつ ちがう）。線は いちばん細く（芯は 0.7＝画面の 約1画素）・
     まわりに うすい光。内がわへ 小さく 枝わかれ。ときどき 枠から 中へ 大きな いなずま（同じ道を 3回 光る・枝わかれ：BOLTS）。
     まわりに 緑の光（ゆっくり 強く 弱く）。光るのは 細い線だけ（画面の 10% より ずっと小さい）
   - 視差効果を減らす（prefers-reduced-motion）なら 動かさない（いまの絵：雷も なし）
   クラスの名前は tq…（的中ボタンの .tg とは別）。いなずまの 形の作り方（frac・bolt_use）は 的中ボタン（gen_fx.py）も使う
   python3 tengel_wall.py --judge <Judge_Tengel.dc.html> <tengel_blobs.json> <tengel_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 tengel_wall.py --plan  → 雷の ついている 本数"""
import sys, re, json, math, random

ALT = ('テンゲルの絵（金と紺の盾のエンブレムに、騎手を乗せて走る馬・上がるグラフ・王冠・データの数字と線、TENGER の金の文字・「独自の統計・オッズ分析による馬券検討支援システム」・「テンゲル」の金の札）'
       '（おしりから 後ろ足の まわりの 数字が いつも 動いて、枠じゅうに 明るい緑と 濃い緑の 雷が ビリビリ 光る）')

# ---------- 数字 ----------
DIGIT_P = (0.9, 1.3, 1.7, 2.1, 2.6)   # 数字が かわる 間（秒）
DIGIT_V = 70.0                  # 数字の かわる 波が 左へ 流れる 速さ（780×320 の座標／秒）

# ---------- 雷 ----------
INSET = 3.0                     # 枠から 内がわへ
STYLE = dict(                   # (色, はば, こさ) を 下から 重ねる。芯は いちばん細く（0.7＝画面の 約1画素）。枝は もっと細く うすく
    hi=dict(main=(('#26FF82', 3.4, .13), ('#6BFFAE', 1.5, .45), ('#F2FFF6', .7, 1)),
            br=(('#26FF82', 2.2, .12), ('#B9FFD6', .5, .9))),
    lo=dict(main=(('#07612F', 3.4, .38), ('#0C8C43', 1.5, .7), ('#24C863', .7, 1)),
            br=(('#07612F', 2.2, .32), ('#18A957', .5, .95))))
EDGE_N = 44                     # 枠の いなずまの 本数（明るい緑と 濃い緑 半分ずつ）
EDGE_LEN = (46.0, 150.0)        # 1本の 長さ（枠に そって）
EDGE_VAR = 3                    # 1本の 形の 数（ちらちら光る たびに かわる）
EDGE_P = (1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.4, 2.7)   # 1本の 1回り（秒）：本ごとに ばらばら
BOLT_LOOP = 12.0                # 大きな いなずまの 1回り（秒）
BOLTS = [(0.8, (520, 0), (478, 62), 'hi'), (3.4, (780, 250), (712, 292), 'lo'), (5.9, (0, 60), (85, 120), 'hi'),
         (8.1, (300, 320), (330, 250), 'lo'), (10.3, (640, 0), (612, 58), 'hi')]   # (はじまる秒, 枠の点, 先の点, 色)：TENGER の字の上は 通らない
STROKES = ((0.0, .05), (.09, .07), (.22, .045))   # 大きな いなずまの 光り方（同じ道を 3回：はじめ・長さ 秒）


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


# ---------- いなずまの 形（的中ボタン gen_fx.py も使う） ----------
def frac(p0, p1, rnd, rough=.22, seg=3.0):
    """p0 → p1 の いなずまの線（まん中を ずらして 半分ずつ…をくり返す：大きな うねりと こまかい ぎざぎざ）"""
    def rec(a, b, amp):
        L = math.dist(a, b)
        if L < seg:
            return [b]
        nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        o = rnd.gauss(0, 1) * amp * L
        m = ((a[0] + b[0]) / 2 + nx * o, (a[1] + b[1]) / 2 + ny * o)
        return rec(a, m, amp * .92) + rec(m, b, amp * .92)
    return [p0] + rec(p0, p1, rough)


def pd(pts, nd=1):
    """点の列 → path の d（はじめは M・あとは 相対の l：短く）"""
    x0, y0 = pts[0]
    out = [f'M{num(x0, nd)} {num(y0, nd)}l']
    px, py = round(x0, nd), round(y0, nd)
    for x, y in pts[1:]:
        x, y = round(x, nd), round(y, nd)
        dx, dy = num(x - px, nd), num(y - py, nd)
        out.append(f'{dx}{"" if dy.startswith("-") else " "}{dy} ')
        px, py = x, y
    return ''.join(out).rstrip()


def branches(pts, rnd, inward, n=(1, 3), length=(6.0, 22.0), spread=(.35, 1.05), sub=.4):
    """線から 内がわ（inward：点ごとの (nx, ny) か 1つ）へ 枝わかれ：点の列の list"""
    out = []
    if len(pts) < 6:
        return out
    for _ in range(rnd.randint(*n)):
        j = rnd.randrange(len(pts) // 6, len(pts) - len(pts) // 6)
        q = pts[j]
        nx, ny = inward[j] if isinstance(inward, list) else inward
        a = math.atan2(ny, nx) + rnd.choice((-1, 1)) * rnd.uniform(*spread)
        L = rnd.uniform(*length)
        tip = (q[0] + math.cos(a) * L, q[1] + math.sin(a) * L)
        br = frac(q, tip, rnd, rough=.24, seg=2.6)
        out.append(br)
        if rnd.random() < sub and len(br) > 4:
            q2 = br[len(br) // 2]
            a2 = a + rnd.choice((-1, 1)) * rnd.uniform(.4, .9)
            out.append(frac(q2, (q2[0] + math.cos(a2) * L * .5, q2[1] + math.sin(a2) * L * .5), rnd, rough=.24, seg=2.6))
    return out


def bolt_use(pid, kind, part='main', pre='tq'):
    """1本の 線（<defs> の pid）を、色と はばの ちがう 線で 重ねる（<use>）。色と はばは クラス（bolt_css）"""
    return ''.join(f'<use href="#{pid}" class="{pre}{kind[0]}{part[0]}{i}"/>' for i in range(len(STYLE[kind][part])))


def bolt_css(pre, scope, sc=1.0):
    """bolt_use の クラスの 色・はば・こさ（sc＝はばの 倍率）"""
    return ''.join(f'{scope} .{pre}{k[0]}{p[0]}{i}{{stroke:{c};stroke-width:{num(w * sc)}' + (f';opacity:{num(o)}' if o < 1 else '') + '}'
                   for k, d in STYLE.items() for p, layers in d.items() for i, (c, w, o) in enumerate(layers))


def bolt_defs(pid, main, brs):
    """main と 枝の <path>（<defs> に 入れる）"""
    d = f'<path id="{pid}m" d="{pd(main)}"/>'
    if brs:
        d += f'<path id="{pid}b" d="{" ".join(pd(b) for b in brs)}"/>'
    return d


# ---------- 緑の雷（壁紙） ----------
def _frame(W=780, H=320):
    """枠の線（内がわ INSET）：s（右回りの 長さ）→ (x, y, 内がわの向き)"""
    i = INSET
    sides = [((i, i), (W - i, i), (0, 1)), ((W - i, i), (W - i, H - i), (-1, 0)), ((W - i, H - i), (i, H - i), (0, -1)), ((i, H - i), (i, i), (1, 0))]
    lens = [math.dist(a, b) for a, b, _ in sides]
    total = sum(lens)

    def at(s):
        s %= total
        for (a, b, n), L in zip(sides, lens):
            if s <= L:
                t = s / L
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, n)
            s -= L
        return (sides[0][0][0], sides[0][0][1], sides[0][2])
    return at, total


def edge_shape(s0, L, rnd):
    """枠に そった いなずま 1つ：(main の点, 枝の list)"""
    at, total = _frame()
    n = max(6, int(L / 3.2))
    base = [at(s0 + L * k / n) for k in range(n + 1)]
    off = [0.0] * (n + 1)

    def rec(i0, i1, amp):
        if i1 - i0 < 2:
            return
        m = (i0 + i1) // 2
        off[m] = (off[i0] + off[i1]) / 2 + rnd.gauss(0, 1) * amp
        rec(i0, m, amp * .62)
        rec(m, i1, amp * .62)
    rec(0, n, min(9.0, L * .09))
    pts, inward = [], []
    for k, (x, y, nrm) in enumerate(base):
        o = min(max(off[k] + rnd.uniform(-.7, .7) * (0 < k < n), -2.2), 11.0)
        pts.append((x + nrm[0] * o, y + nrm[1] * o))
        inward.append(nrm)
    return pts, branches(pts, rnd, inward)


def lightning():
    """(svg, css, defs)：枠の いなずま（EDGE_N 本・1本ずつ ついたり消えたり）・ときどきの 大きな いなずま・まわりの 緑の光"""
    rnd = random.Random(7)
    at, total = _frame()
    svg, css, dfs = '', [], []
    # まわりの 緑の光（4辺の グラデーション）
    svg += ('<g class="tqG"><rect width="780" height="22" fill="url(#tqGt)"/><rect y="298" width="780" height="22" fill="url(#tqGb)"/>'
            '<rect width="22" height="320" fill="url(#tqGl)"/><rect x="758" width="22" height="320" fill="url(#tqGr)"/></g>')
    css.append('.tqw .tqG{animation:tqG 1.6s ease-in-out infinite alternate}@keyframes tqG{from{opacity:.45}to{opacity:.85}}')
    # 枠の いなずま：はじまりを 枠に そって ほぼ 同じ間かくに（少し ずらす）・色は かわるがわる（ときどき 入れかえ）
    plans = []
    for j in range(EDGE_N):
        s0 = total * (j + rnd.uniform(-.35, .35)) / EDGE_N
        L = rnd.uniform(*EDGE_LEN)
        kind = ('hi', 'lo')[j % 2] if rnd.random() < .8 else ('lo', 'hi')[j % 2]
        P = rnd.choice(EDGE_P)
        t, ranges = rnd.uniform(0, P), [[] for _ in range(EDGE_VAR)]
        for k in range(rnd.randint(2, 7)):                      # 1回に 2〜7回 ちらちら（そのたび 形が かわる）
            dur = rnd.uniform(.035, .085)
            ranges[k % EDGE_VAR].append((t, t + dur))
            t += dur + rnd.uniform(.025, .075)
        plans.append((s0, L, kind, P, ranges))
        for v in range(EDGE_VAR):
            if not ranges[v]:
                continue
            pid = f'tqE{j}v{v}'
            main, brs = edge_shape(s0, L, rnd)
            dfs.append(bolt_defs(pid, main, brs))
            body = bolt_use(pid + 'm', kind) + (bolt_use(pid + 'b', kind, 'br') if brs else '')
            svg += f'<g class="tqE tqE{j}v{v}">{body}</g>'
            css.append(f'.tqw .tqE{j}v{v}{{animation:tqE{j}v{v} {num(P, 3)}s step-end infinite}}' + vis_kf(f'tqE{j}v{v}', ranges[v], P))
    css.append('.tqw .tqE{visibility:hidden}')
    # 大きな いなずま：同じ道を 3回 光る（枝は 光るたびに ちがう）
    for j, (t0, a, b, kind) in enumerate(BOLTS):
        main = frac(a, b, rnd, rough=.2, seg=3.2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nrm = (dx / L, dy / L)
        dfs.append(f'<path id="tqB{j}m" d="{pd(main)}"/>')
        for v, (ts, dur) in enumerate(STROKES):
            brs = branches(main, rnd, nrm, n=(2, 4), length=(10.0, 34.0), spread=(.25, .8), sub=.55)
            dfs.append(f'<path id="tqB{j}v{v}b" d="{" ".join(pd(x) for x in brs)}"/>')
            svg += f'<g class="tqB tqB{j}v{v}">{bolt_use(f"tqB{j}m", kind)}{bolt_use(f"tqB{j}v{v}b", kind, "br")}</g>'
            css.append(f'.tqw .tqB{j}v{v}{{animation:tqB{j}v{v} {BOLT_LOOP:g}s step-end infinite}}'
                       + vis_kf(f'tqB{j}v{v}', [(t0 + ts, t0 + ts + dur)], BOLT_LOOP))
    css.append('.tqw .tqB{visibility:hidden}' + bolt_css('tq', '.tqw'))
    return svg, ''.join(css), ''.join(dfs), plans


def defs():
    g = '#26FF82'
    lin = lambda i, x1, y1, x2, y2: (f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{g}" stop-opacity=".36"/>'
                                     f'<stop offset="1" stop-color="{g}" stop-opacity="0"/></linearGradient>')
    return lin('tqGt', 0, 0, 0, 1) + lin('tqGb', 0, 1, 0, 0) + lin('tqGl', 0, 0, 1, 0) + lin('tqGr', 1, 0, 0, 0)


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：banner → /_blob/<id>。html は <div class="bnr tqw">（判定画面の <img class="bnr"> と入れかえる）"""
    ds, dc = digits(run)
    ls, lc, ld, _ = lightning()
    im = lambda h: f'<image href="{h}" width="780" height="320" preserveAspectRatio="none"/>'
    # 帯の下に 1px の金の線（.bnr の border-bottom）があるので、上の絵は 上に そろえる（<img> の object-fit:cover と 同じ所に）
    # 重ねる順：いまの絵 → 数字 → 雷。いなずまの線は 色の線を 重ねるので fill なし・角は まるく
    html = (f'<div class="bnr tqw" role="img" aria-label="{alt}"><svg viewBox="0 0 780 320" width="390" height="160" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<defs>{defs()}<g fill="none" stroke-linecap="round" stroke-linejoin="round">{ld}</g></defs>{im(blobs["banner"])}'
            f'<g class="tqA">{ds}<g fill="none" stroke-linecap="round" stroke-linejoin="round">{ls}</g></g></svg></div>')
    css = ('.tqw{position:relative;overflow:hidden}.tqw>svg{display:block;width:100%;height:100%}'
           + dc + lc
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


def plan():
    """枠の いなずまが ついている 本数（30秒ぶん・0.01秒ごと）"""
    _, _, _, plans = lightning()
    cnt = []
    for i in range(3000):
        t = i * .01
        n = 0
        for s0, L, kind, P, ranges in plans:
            tt = t % P
            if any(a <= tt < b or a <= tt + P < b for rr in ranges for a, b in rr):
                n += 1
        cnt.append(n)
    print('枠の いなずま：ついている本数 平均', round(sum(cnt) / len(cnt), 2), '最小', min(cnt), '最大', max(cnt),
          ' 0本の 時間', round(cnt.count(0) * .01, 2), '秒（30秒のうち）')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan()
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
