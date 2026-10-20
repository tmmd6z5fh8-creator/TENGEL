"""シルバー帯・ゴールド帯の壁紙の動き（まさちゃんの指定「常にシルバーの馬がキラキラ輝いている」「常にゴールドの馬の像がキラキラゴールドに輝いている」）：
   ページに入れる HTML と CSS（銀も金も 同じ作り・色だけ ちがう）
   - 絵は flat/metal_run.py の いまの絵（きらめきつき：silver_banner・gold_banner）と、そこから きらめき（4本の光）だけ ぬいた絵（silver_base・gold_base）。
     キャンバスでは /_blob/<id>（metal_blobs.json）・像の形（ふちの線）と きらめきの場所は metal_run.json。1つの <svg>（780×320 を 390×160 に）に重ねる
   - いつも キラキラ：
     ・きらめき（いまの絵の4つ＋またたく所）が TWINKLE 秒に 2回ずつ、ばらばらの順で きらっ（左から右へ 順に 光らせない）
     ・像の上の こまかい光の粒が ばらばらに ちかっ
     ・光の粒（金は 金の粉）が 像の うしろがわ（しっぽ・おしり・後ろ足）から うしろへ ふわっと流れて 消える
     ・うしろの光の輪を 光が ゆっくり回る（像の うしろを通る・床の下は 通らない）
   - まえは 光の帯が 像の上を 左から右へ ななめに すうっと通って 体を 光らせていたが、まさちゃん「シルバー帯とゴールド帯の馬の銅像に
     左から右へ光が馬の身体を光らせる演出いらない！」で やめた（帯を 追いかけて 左から右へ つぎつぎに 光っていた きらめきも ばらばらの順に）
   - 強く光らせない（光るのは 小さい所だけ）。視差効果を減らす（prefers-reduced-motion）なら 動かさない（いまの絵）
   クラスの名前は mxs…（銀）・mxg…（金）（的中ボタンの .ag・.au とは別）
   python3 metal_wall.py --judge <Judge_Silver.dc.html> silver <metal_blobs.json> <metal_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 metal_wall.py --judge <Judge_Golden.dc.html> gold <metal_blobs.json> <metal_run.json>
   python3 metal_wall.py --plan <metal_run.json>  → きらめきの 予定（と 左右との 相関）"""
import sys, re, json, math, random

ALT = dict(
    silver=('銀の地（ヘアライン）と光の輪の前を、全力で駆ける銀の馬の像（うしろへ流れるたてがみとしっぽ・みがいた床にうつる）のイラスト'
            '（いつも キラキラ：あちこちが きらっと またたく・光の粒が うしろへ流れる・光の輪を 光が回る）'),
    gold=('金の地（ヘアライン）と光の輪の前を、全力で駆ける金の馬の像（うしろへ流れるたてがみとしっぽ・みがいた床にうつる）のイラスト'
          '（いつも 金に キラキラ：あちこちが きらっと またたく・金の粉が うしろへ流れる・光の輪を 光が回る）'))
PRE = dict(silver='mxs', gold='mxg')
NAME = dict(silver='シルバー帯', gold='ゴールド帯')

TWINKLE = 4.0                  # きらめきの1回り（秒）：どの きらめきも この間に 2回 きらっ
TW_T0 = .08                    # 1回りの中で いちばん はじめの きらっ（秒）
TW_GAP = 7                     # 同じ きらめきの 2回の きらっ は 7こま（約0.8秒）以上 はなす（1回りの つなぎ目を またいでも）
STAR_L = 16.0                  # きらめきの形の 大きさ（横の光の長さ）
FLARE = (2.0, 1.45)            # 1回目の きらっ の大きさ（いまの絵の4つ・またたく所。いまの絵の きらめきの何倍）
TW2 = .82                      # 2回目の きらっ の大きさ（1回目の何倍）
DOT_P = (1.9, 3.4)             # こまかい光の粒の ちかっ の間（秒）
TRAIL = 20                     # うしろへ流れる 光の粒（ふちの 右を向いた所から 最大20・たがいに はなす。いまの像では17）
TRAIL_X = 430.0                # 光の粒が 出る所（像の ふちの この x より右）
RING_S = 10.0                  # 光の輪の光が 1回り（秒）
RING_ARC = 75.0                # 光の輪の光の 尾の長さ（度）

COL = dict(
    silver=dict(star='#FFFFFF', glow='#AECBFF', dust='#FFFFFF', dglow='#B7D0FF', ring='#FFFFFF'),
    gold=dict(star='#FFFBEA', glow='#FFC83A', dust='#FFF0BA', dglow='#F5B829', ring='#FFF1C0'))


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


def corr(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))


def tw_slots(xs, seed=5):
    """きらめき n こ（左右の位置 xs）の きらっ 2回ずつ（2n回）を、1回りの 2n この こまに ばらばらに わける：(1回目の こま, 2回目の こま) の list。
       1回目は 前の半分（0〜n−1）・2回目は うしろの半分（n〜2n−1）。同じ きらめきの 2回は TW_GAP こま以上 はなす（1回りの つなぎ目を またいでも）。
       左から右（右から左）へ 順に 光って 見えないように、こまの 順と 左右の位置の 相関が ±0.1 より 小さい わけかたを えらぶ"""
    n = len(xs)
    rnd = random.Random(seed)
    while True:
        a, b = list(range(n)), list(range(n))
        rnd.shuffle(a)
        rnd.shuffle(b)
        if (all(TW_GAP <= n + b[i] - a[i] <= 2 * n - TW_GAP for i in range(n))
                and abs(corr(xs, a)) < .1 and abs(corr(xs, b)) < .1):
            return [(a[i], n + b[i]) for i in range(n)]


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


def twinkles(R):
    """きらめき（いまの絵の4つ＝main・またたく所）ごとの (x, y, 大きさ, main か, 1回目の秒, 2回目の秒)"""
    stars = [(x, y, L, True) for x, y, L in R['spark']] + [(x, y, L, False) for x, y, L in R['glint']]
    n = len(stars)
    step = (TWINKLE - TW_T0 - .72) / (2 * n - 1)          # 2回目（.7秒）が 1回りの中で おわる
    return [(x, y, L, main, TW_T0 + a * step, TW_T0 + b * step) for (x, y, L, main), (a, b) in zip(stars, tw_slots([v[0] for v in stars]))]


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
    a0 = math.radians(-RING_ARC)
    tx, ty = cx + rr * math.cos(a0), cy + rr * math.sin(a0)
    hx, hy = cx + rr, cy
    defs = (f'<clipPath id="{p}O"><path clip-rule="evenodd" d="M0 0H780V{floor - 1}H0Z{d}"/></clipPath>'
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
    # ---------- きらめき（TWINKLE 秒に 2回ずつ・ばらばらの順で きらっ） ----------
    for i, (x, y, L, main, t1, t2) in enumerate(twinkles(R)):
        s = L / STAR_L * FLARE[0 if main else 1]
        keys = [(0, (0, 0, -20), 'linear'), (t1 - .06, (0, 0, -20), 'cubic-bezier(.2,.8,.4,1)'), (t1 + .1, (s, 1, 0), 'ease-out'),
                (t1 + .32, (s * .55, .9, 18), 'ease-in'), (t1 + .62, (0, 0, 40), 'linear')]
        keys += [(t2, (0, 0, -10), 'ease-out'), (t2 + .22, (s * TW2, 1, 8), 'ease-in-out'), (t2 + .7, (0, 0, 30), 'linear')]
        keys.append((TWINKLE, (0, 0, 40), 'linear'))
        c = f'{p}F{i}'
        body += f'<g transform="translate({x} {y})"><g class="{p}F {c}"><use href="#{p}{"Sm" if main else "St"}"/></g></g>'
        css.append(f'.{p}w .{c}{{animation:{c} {TWINKLE:g}s linear infinite}}'
                   + kf(c, keys, TWINKLE, lambda v: f'opacity:{num(v[1])};transform:scale({num(v[0], 3)}) rotate({num(v[2], 1)}deg)'))
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
    block = f'/* {nm}の壁紙：いつも キラキラ（きらめき・光の粒・光の輪。metal_wall.py） */\n{css}\n/* /{nm}の壁紙 */\n'
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


def plan(run):
    """きらめきの 予定（1回目・2回目の秒）と、x（左右）との 相関（左から右へ 順に 光っていないか）"""
    for name in ('silver', 'gold'):
        tw = twinkles(run[name])
        print(NAME[name], len(tw), 'こ')
        for x, y, L, main, t1, t2 in sorted(tw, key=lambda v: v[4]):
            print(f'  {t1:5.2f}秒 / {t2:5.2f}秒  x={x:6.1f} y={y:6.1f}' + ('  （いまの絵の きらめき）' if main else ''))
        for k in (4, 5):
            print(f'  {k - 3}回目の 秒と x の 相関 {corr([v[0] for v in tw], [v[k] for v in tw]):+.2f}')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan(json.load(open(sys.argv[sys.argv.index('--plan') + 1])))
        sys.exit()
    i = sys.argv.index('--judge')
    fn, name, bfn, rfn = sys.argv[i + 1:i + 5]
    judge_inline(fn, name, load_blobs(bfn, name), json.load(open(rfn)))
