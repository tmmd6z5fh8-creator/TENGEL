"""シルバー帯・ゴールド帯の壁紙の動き（まさちゃんの指定「常にシルバーの馬がキラキラ輝いている」「常にゴールドの馬の像がキラキラゴールドに輝いている」）：
   ページに入れる HTML と CSS（銀も金も 同じ作り・色だけ ちがう）
   - 絵は flat/metal_run.py の いまの絵（きらめきつき：silver_banner・gold_banner）と、そこから きらめき（4本の光）だけ ぬいた絵（silver_base・gold_base）。
     キャンバスでは /_blob/<id>（metal_blobs.json）・像の形（ふちの線）と きらめきの場所は metal_run.json。1つの <svg>（780×320 を 390×160 に）に重ねる
   - いつも キラキラ（SHEEN 秒で1回り）：
     ・光の帯が 像の上を ななめに すうっと通る（像の形で 切りぬいた帯を スクリーンで重ねる。金は 金の光）
     ・帯が通った所の きらめき（いまの絵の4つ＋またたく所）が 帯を追いかけて つぎつぎに きらっ（いまの絵の4つは 帯のあとにも もう1回 きらっ）
     ・像の上の こまかい光の粒が ばらばらに ちかっ
     ・光の粒（金は 金の粉）が 像の うしろがわ（しっぽ・おしり・後ろ足）から うしろへ ふわっと流れて 消える
     ・うしろの光の輪を 光が ゆっくり回る（像の うしろを通る・床の下は 通らない）
   - 強く光らせない（光るのは 小さい所だけ・帯は SHEEN 秒に1回）。視差効果を減らす（prefers-reduced-motion）なら 動かさない（いまの絵）
   クラスの名前は mxs…（銀）・mxg…（金）（的中ボタンの .ag・.au とは別）
   python3 metal_wall.py --judge <Judge_Silver.dc.html> silver <metal_blobs.json> <metal_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 metal_wall.py --judge <Judge_Golden.dc.html> gold <metal_blobs.json> <metal_run.json>"""
import sys, re, json, math, random

ALT = dict(
    silver=('銀の地（ヘアライン）と光の輪の前を、全力で駆ける銀の馬の像（うしろへ流れるたてがみとしっぽ・みがいた床にうつる）のイラスト'
            '（いつも キラキラ：光の帯が 像の上を すうっと通り、あちこちが きらっと またたく・光の粒が うしろへ流れる・光の輪を 光が回る）'),
    gold=('金の地（ヘアライン）と光の輪の前を、全力で駆ける金の馬の像（うしろへ流れるたてがみとしっぽ・みがいた床にうつる）のイラスト'
          '（いつも 金に キラキラ：金の光の帯が 像の上を すうっと通り、あちこちが きらっと またたく・金の粉が うしろへ流れる・光の輪を 光が回る）'))
PRE = dict(silver='mxs', gold='mxg')
NAME = dict(silver='シルバー帯', gold='ゴールド帯')

SHEEN = 4.0                    # 光の帯の1回り（秒）
SW = (0.35, 1.65)              # 帯が 左はしから 右はしまで 通る（1回りの中の秒）
X0, X1 = 40.0, 880.0           # 帯のまん中（高さ0の所）の はじめと おわり（780×320）
TILT = 0.45                    # 帯の かたむき（上へ行くほど 右へ：高さ1で 0.45）
BAND = 150.0                   # 帯の はば
STAR_L = 16.0                  # きらめきの形の 大きさ（横の光の長さ）
FLARE = (2.0, 1.45)            # 帯が通る時の きらっ の大きさ（いまの絵の4つ・またたく所。いまの絵の きらめきの何倍）
TW2 = (1.85, 4.0, .82)         # 帯のあとの もう1回の きらっ（この間に ばらばらの順で・帯の時の何倍）
DOT_P = (1.9, 3.4)             # こまかい光の粒の ちかっ の間（秒）
TRAIL = 20                     # うしろへ流れる 光の粒（ふちの 右を向いた所から 最大20・たがいに はなす。いまの像では17）
TRAIL_X = 430.0                # 光の粒が 出る所（像の ふちの この x より右）
RING_S = 10.0                  # 光の輪の光が 1回り（秒）
RING_ARC = 75.0                # 光の輪の光の 尾の長さ（度）

COL = dict(
    silver=dict(sheen=[(0, '#EEF3FF', 0), (.25, '#EEF3FF', .16), (.5, '#FFFFFF', .62), (.75, '#EEF3FF', .16), (1, '#EEF3FF', 0)],
                core=[(0, '#FFFFFF', 0), (.5, '#FFFFFF', 1), (1, '#FFFFFF', 0)],
                star='#FFFFFF', glow='#AECBFF', dust='#FFFFFF', dglow='#B7D0FF', ring='#FFFFFF'),
    gold=dict(sheen=[(0, '#FFD45A', 0), (.25, '#FFD45A', .22), (.5, '#FFE9A0', .7), (.75, '#FFD45A', .22), (1, '#FFD45A', 0)],
              core=[(0, '#FFF8DC', 0), (.5, '#FFFDF4', 1), (1, '#FFF8DC', 0)],
              star='#FFFBEA', glow='#FFC83A', dust='#FFF0BA', dglow='#F5B829', ring='#FFF1C0'))
CORE = 12.0                    # 帯のまん中の 細い光の はば


def pct(t, period):
    s = f'{t / period * 100:.3f}'.rstrip('0').rstrip('.')
    return (s or '0') + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def kf(name, keys, period, fmt):
    """@keyframes（keys：(秒, 値, 次までの動き)。動きが linear なら 書かない）"""
    out, last = [], None
    for t, v, e in keys:
        p = pct(min(max(t, 0.0), period), period)
        if p == last:
            continue
        out.append(f'{p}{{{fmt(v)}' + (f';animation-timing-function:{e}' if e != 'linear' else '') + '}')
        last = p
    return f'@keyframes {name}{{' + ''.join(out) + '}'


def star_d(L=STAR_L, k=(1, .35, .75, .35), waist=1.8):
    """きらめきの形（いまの絵と同じ：横の光 L・たて .75L・ななめ .35L。細い光）"""
    pts = []
    for i in range(8):
        a = math.radians(i * 45)
        r = L * k[i % 4]
        pts.append((r * math.cos(a), r * math.sin(a)))
        a2 = math.radians(i * 45 + 22.5)
        pts.append((waist * math.cos(a2), waist * math.sin(a2)))
    return 'M' + 'L'.join(f'{num(x)} {num(y)}' for x, y in pts) + 'Z'


def polys(d):
    """ふちの線（M…L…Z）→ 点の列の list"""
    out = []
    for sub in re.findall(r'M([^Z]*)Z', d):
        nums = [float(v) for v in re.findall(r'-?[\d.]+', sub)]
        out.append(list(zip(nums[0::2], nums[1::2])))
    return out


def inside(P, x, y):
    """像の中か（偶奇）"""
    c = False
    for p in P:
        for (x0, y0), (x1, y1) in zip(p, p[1:] + p[:1]):
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
    return c


def pass_t(x, y):
    """帯のまん中が (x, y) を通る秒（1回りの中）"""
    return SW[0] + (x + TILT * y - X0) / (X1 - X0) * (SW[1] - SW[0])


def trail_src(P, n=TRAIL, gap=13.0):
    """光の粒が 出る所：像の ふちの 右を向いた所（右は外・左は中）で、TRAIL_X より右。たがいに gap はなす"""
    cand = []
    for p in P:
        for x, y in p:
            if x > TRAIL_X and not inside(P, x + 6, y) and inside(P, x - 4, y):
                cand.append((x, y))
    rnd = random.Random(23)
    rnd.shuffle(cand)
    out = []
    for x, y in cand:
        if all((x - a) ** 2 + (y - b) ** 2 > gap ** 2 for a, b in out):
            out.append((x, y))
        if len(out) >= n:
            break
    return sorted(out, key=lambda q: (q[1], q[0]))


def inline(name, blobs, run, alt=None):
    """(html, css)。name：'silver'・'gold'。blobs：{'banner','base'} の /_blob/<id>。html は <div class="bnr mxsw">（判定画面の <img class="bnr"> と入れかえる）"""
    p = PRE[name]
    C = COL[name]
    R = run[name]
    shape = run['shape']
    d = shape['d']
    P = polys(d)
    floor = shape['floor']
    cx, cy, rr = shape['ring']
    css = []

    def im(href):
        return f'<image href="{href}" width="780" height="320" preserveAspectRatio="none"/>'
    # ---------- defs ----------
    stops = ''.join(f'<stop offset="{num(o)}" stop-color="{c}" stop-opacity="{num(a)}"/>' for o, c, a in C['sheen'])
    cstops = ''.join(f'<stop offset="{num(o)}" stop-color="{c}" stop-opacity="{num(a)}"/>' for o, c, a in C['core'])
    a0 = math.radians(-RING_ARC)
    tx, ty = cx + rr * math.cos(a0), cy + rr * math.sin(a0)
    hx, hy = cx + rr, cy
    defs = (f'<clipPath id="{p}H"><path d="{d}"/></clipPath>'
            f'<clipPath id="{p}O"><path clip-rule="evenodd" d="M0 0H780V{floor - 1}H0Z{d}"/></clipPath>'
            f'<linearGradient id="{p}Sg" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>'
            f'<linearGradient id="{p}Cg" x1="0" y1="0" x2="1" y2="0">{cstops}</linearGradient>'
            f'<linearGradient id="{p}Lg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["glow"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{p}Gl"><stop offset="0" stop-color="{C["glow"]}" stop-opacity=".95"/><stop offset=".35" stop-color="{C["glow"]}" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{p}Dg"><stop offset="0" stop-color="{C["dglow"]}" stop-opacity=".9"/><stop offset="1" stop-color="{C["dglow"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{p}Rg" gradientUnits="userSpaceOnUse" x1="{num(tx, 1)}" y1="{num(ty, 1)}" x2="{num(hx, 1)}" y2="{num(hy, 1)}">'
            f'<stop offset="0" stop-color="{C["ring"]}" stop-opacity="0"/><stop offset=".7" stop-color="{C["ring"]}" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="{C["ring"]}" stop-opacity=".95"/></linearGradient>'
            # きらめき（大）・光の粒（小）・こまかい粒
            f'<g id="{p}St"><circle r="13" fill="url(#{p}Gl)"/><path d="{star_d()}" fill="{C["star"]}"/><circle r="2.8" fill="#FFFFFF"/></g>'
            f'<g id="{p}Sm"><rect x="-44" y="-1.1" width="88" height="2.2" fill="url(#{p}Lg)"/><use href="#{p}St"/></g>'
            f'<g id="{p}Sp"><circle r="8" fill="url(#{p}Dg)"/><path d="{star_d(9, (1, .3, 1, .3), 1.1)}" fill="{C["dust"]}"/><circle r="1.6" fill="#FFFFFF"/></g>'
            f'<g id="{p}Dt"><circle r="6" fill="url(#{p}Gl)"/><path d="{star_d(6.5, (1, .25, 1, .25), .9)}" fill="{C["star"]}"/></g>')
    body = im(blobs['banner']) + f'<g class="{p}A">' + im(blobs['base'])
    # ---------- うしろの光の輪を 光が回る（像の うしろ・床より上だけ） ----------
    arc = f'M{num(tx, 1)} {num(ty, 1)}A{num(rr)} {num(rr)} 0 0 1 {num(hx, 1)} {num(hy, 1)}'
    body += (f'<g clip-path="url(#{p}O)"><g class="{p}R">'
             f'<path d="{arc}" fill="none" stroke="url(#{p}Rg)" stroke-width="11" stroke-linecap="round" opacity=".28"/>'
             f'<path d="{arc}" fill="none" stroke="url(#{p}Rg)" stroke-width="3.6" stroke-linecap="round"/>'
             f'<circle cx="{num(hx, 1)}" cy="{num(hy, 1)}" r="11" fill="url(#{p}Gl)"/></g></g>')
    css.append(f'.{p}w .{p}R{{transform-box:view-box;transform-origin:{num(cx, 1)}px {num(cy, 1)}px;animation:{p}R {RING_S:g}s linear infinite}}'
               f'@keyframes {p}R{{to{{transform:rotate(360deg)}}}}')
    # ---------- 光の帯（像の形で 切りぬく・スクリーン） ----------
    skew = -math.degrees(math.atan(TILT))
    body += (f'<g class="{p}Sb" clip-path="url(#{p}H)"><g class="{p}S"><g transform="skewX({num(skew)})">'
             f'<rect x="{num(-BAND / 2)}" y="-30" width="{num(BAND)}" height="380" fill="url(#{p}Sg)"/>'
             f'<rect x="{num(-CORE / 2)}" y="-30" width="{num(CORE)}" height="380" fill="url(#{p}Cg)"/></g></g></g>')
    css.append(f'.{p}w .{p}Sb{{mix-blend-mode:screen}}'
               f'.{p}w .{p}S{{transform-box:view-box;transform-origin:0 0;transform:translateX({num(X0)}px);animation:{p}S {SHEEN:g}s linear infinite}}'
               + kf(f'{p}S', [(0, X0, 'linear'), (SW[0], X0, 'linear'), (SW[1], X1, 'linear'), (SHEEN, X1, 'linear')], SHEEN,
                    lambda v: f'transform:translateX({num(v)}px)'))
    # ---------- こまかい光の粒（像の上・ばらばらに ちかっ） ----------
    rnd = random.Random(31)
    dots = ''
    for i, (x, y) in enumerate(R['dots']):
        per = rnd.uniform(*DOT_P)
        dots += (f'<g transform="translate({x} {y})"><g class="{p}D" style="animation-duration:{num(per)}s;animation-delay:{num(-rnd.uniform(0, per))}s">'
                 f'<use href="#{p}Dt"/></g></g>')
    body += dots
    css.append(f'.{p}w .{p}D{{opacity:0;transform-box:view-box;transform-origin:0 0;animation:{p}D 2.5s ease-in-out infinite}}'
               f'@keyframes {p}D{{0%,30%,100%{{opacity:0;transform:scale(.3)}}15%{{opacity:1;transform:scale(1)}}}}')
    # ---------- うしろへ流れる 光の粒（金は 金の粉） ----------
    rnd = random.Random(47)
    trail = ''
    for i, (x, y) in enumerate(trail_src(P)):
        dur = rnd.uniform(1.8, 2.8)
        dx, dy = rnd.uniform(80, 160), rnd.uniform(-22, 4)
        s = rnd.uniform(.7, 1.15)
        c = f'{p}P{i}'
        trail += f'<g transform="translate({num(x, 1)} {num(y, 1)})"><g class="{p}P {c}"><use href="#{p}Sp"/></g></g>'
        css.append(f'.{p}w .{c}{{animation:{c} {num(dur)}s linear {num(-dur * ((i * 7) % TRAIL) / TRAIL)}s infinite}}'
                   f'@keyframes {c}{{0%{{opacity:0;transform:translate(0,0) scale({num(s * .5)})}}'
                   f'12%{{opacity:1;transform:translate({num(dx * .1)}px,{num(dy * .1)}px) scale({num(s)})}}'
                   f'40%{{opacity:.45;transform:translate({num(dx * .4)}px,{num(dy * .4)}px) scale({num(s * .75)})}}'
                   f'58%{{opacity:.95;transform:translate({num(dx * .58)}px,{num(dy * .58)}px) scale({num(s * .85)})}}'
                   f'100%{{opacity:0;transform:translate({num(dx)}px,{num(dy)}px) scale({num(s * .3)})}}}}')
    body += trail
    css.append(f'.{p}w .{p}P{{opacity:0;transform-box:view-box;transform-origin:0 0}}')
    # ---------- きらめき（帯を追いかけて きらっ → 帯のあとに もう1回 ばらばらの順で きらっ） ----------
    stars = [(x, y, L, True) for x, y, L in R['spark']] + [(x, y, L, False) for x, y, L in R['glint']]
    order = list(range(len(stars)))
    random.Random(5).shuffle(order)
    step = (TW2[1] - TW2[0] - .7) / max(1, len(stars) - 1)
    for i, (x, y, L, main) in enumerate(stars):
        tp = pass_t(x, y)
        s = L / STAR_L * FLARE[0 if main else 1]
        keys = [(0, (0, 0, -20), 'linear'), (tp - .06, (0, 0, -20), 'cubic-bezier(.2,.8,.4,1)'), (tp + .1, (s, 1, 0), 'ease-out'),
                (tp + .32, (s * .55, .9, 18), 'ease-in'), (tp + .62, (0, 0, 40), 'linear')]
        t2 = TW2[0] + order.index(i) * step
        keys += [(t2, (0, 0, -10), 'ease-out'), (t2 + .22, (s * TW2[2], 1, 8), 'ease-in-out'), (t2 + .7, (0, 0, 30), 'linear')]
        keys.append((SHEEN, (0, 0, 40), 'linear'))
        c = f'{p}F{i}'
        body += f'<g transform="translate({x} {y})"><g class="{p}F {c}"><use href="#{p}{"Sm" if main else "St"}"/></g></g>'
        css.append(f'.{p}w .{c}{{animation:{c} {SHEEN:g}s linear infinite}}'
                   + kf(c, keys, SHEEN, lambda v: f'opacity:{num(v[1])};transform:scale({num(v[0], 3)}) rotate({num(v[2], 1)}deg)'))
    css.append(f'.{p}w .{p}F{{opacity:0;transform-box:view-box;transform-origin:0 0}}')
    body += '</g>'
    html = (f'<div class="bnr {p}w" role="img" aria-label="{alt or ALT[name]}"><svg viewBox="0 0 780 320" width="390" height="160" '
            f'preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs>{defs}</defs>{body}</svg></div>')
    css = (f'.{p}w{{position:relative;overflow:hidden}}.{p}w svg{{display:block;width:100%;height:100%}}'
           + ''.join(css)
           + f'@media (prefers-reduced-motion:reduce){{.{p}w *{{animation:none!important}}.{p}w .{p}A{{visibility:hidden}}}}')
    return html, css


def judge_inline(fn, name, blobs, run, alt=None):
    """判定画面（Judge_Silver・Judge_Golden）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr mxsw">）。CSS は <style> の最後（印のあいだ）"""
    p = PRE[name]
    page = open(fn, encoding='utf-8').read()
    html, css = inline(name, blobs, run, alt)
    page, k = re.subn(rf'<div class="bnr {p}w" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    nm = NAME[name]
    block = f'/* {nm}の壁紙：いつも キラキラ（光の帯・きらめき・光の粒・光の輪。metal_wall.py） */\n{css}\n/* /{nm}の壁紙 */\n'
    if f'/* {nm}の壁紙：' in page:
        page = re.sub(rf'/\* {nm}の壁紙：.*?/\* /{nm}の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn, name):
    """metal_blobs.json（silver_banner・silver_base・gold_banner・gold_base → id）から その色の2まい"""
    b = json.load(open(fn))
    f = lambda v: v if v.startswith('/_blob/') else f'/_blob/{v}'
    return dict(banner=f(b[f'{name}_banner']), base=f(b[f'{name}_base']))


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    fn, name, bfn, rfn = sys.argv[i + 1:i + 5]
    judge_inline(fn, name, load_blobs(bfn, name), json.load(open(rfn)))
