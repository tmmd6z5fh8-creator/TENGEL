"""花火の壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   はじめは「…6秒から7秒で馬の花火を打ち上げる 12秒に一回リピートする」。いまは（2026/10/19）
   「花火の消え方、もっと散り散りに花火っぽく消して！ 馬以外の花火、打ち上げてから1秒で花火を咲かせて、3秒かけて消える
    馬の花火は、打ち上げて1秒で馬の花火を咲かせて、3秒かけて消える 消えてから3秒後にリピートする。
    3回〜6回に一度、ランダムで一斉に打ち上げて、一斉に咲かせて、一斉に消える 馬の花火は、他の花火が消え始めるタイミングで打ち上げて！」
   →「全体的に花火の消える時間1.7秒間増やして！」：花火も馬も 消えるまで 3秒 → 4.7秒（FADE）。散り方は 3秒の時（BASE_FADE）と同じ流れを
     ゆっくりにのばす（stretch：広がりきってから あとの時刻を のばす。広がる大きさ・落ちる長さは 同じ）
   - いちばん下は 夜空・星・ちょうちんの絵（花火なし・<img class="bnr">）。花火4つと馬は「足す光」の絵（flat/fireworks_banner.py --layers）を
     mix-blend-mode:plus-lighter で足す（ぜんぶ足すと いつもの絵と同じ）
   - 散り散りに消す：足す光の絵を 光の粒（花火は 光の点・馬は 線の上に 6px ごとの点）ごとに 8組に分けた絵にする（--scatter。
     となりの粒は ちがう組・境目は ぼかして分けるので 足すと もとの絵と同じ）。組ごとに 外へ広がる速さ・落ちる速さ・消える時間を変え、
     組ごとに ちらちら またたく → 咲いたあと 光の粒が ばらばらに広がりながら下へ落ち、ちらつきながら 1つずつ 消えていく。
     そこへ 火の粉（3組・またたきながら 尾を引いて落ちる）
   - ふつうの回：まわりの花火4つを 0〜0.3秒ずらして打ち上げる（ちょうちんの上から 光の玉が 1秒で上がる）→ 咲く（まん中から 0.45秒で広がる・
     ぱっと光る）→ 4.7秒かけて 散り散りに消える。馬は 4つが ぜんぶ咲いた（消えはじめた）ところで打ち上げ → 1秒で咲く → 4.7秒で消える。
     ぜんぶ消えて 3秒後に 次の回
   - 一斉の回（3〜6回に1回・GAPS の順で ばらばら）：5つ ぜんぶ いっしょに打ち上げ・咲いて・消える。消えて3秒後に 次の回
   - GAPS の回ぶん（18回・174.8秒）で1回り。ページを開くと 一斉の回の 咲ききったところから（いつもの絵と同じ）
   - 「キラキラ」：花火の光の点と 馬の線の上に、4つの角の きらっ（白いしん・花火の色の光）が ばらばらに光る（咲いている間）
   - 1つの花火・馬の 動くものは みな 同じ キーフレーム（hqP0〜hqP4）を使い、ちがう所は CSS の変数（--y5 など）で わたす
   - 視差効果を減らす（prefers-reduced-motion）なら 動かさない（花火と馬が ぜんぶ出た いつもの絵）
   - キャンバスでは /_blob/<id>（fireworks_blobs.json の base＝下の絵・scatter＝8組に分けた足す光）・置く場所は fireworks_layers.json
   クラスの名前は hq…
   python3 fireworks_wall.py --judge <Judge_Fireworks.dc.html> <fireworks_blobs.json> <fireworks_layers.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 fireworks_wall.py --scatter <fireworks_layers.webp> <fireworks_layers.json> <fireworks_scatter.webp>
     → 足す光の絵（flat/fireworks_banner.py --layers）から 8組に分けた絵をつくり、火の粉の出る点（sparks）を json に足す"""
import sys, re, json, math, random

ALT = ('夜空に上がる花火と、金とピンクの光の線でえがいた、かける馬（しっぽはしだれ柳の花火）、ちょうちんのイラスト'
       '（花火が打ち上がって咲き、散り散りに消える。ときどき 5つ一斉に）')
RISE, OPEN, FADE, GAP = 1.0, .45, 4.7, 3.0   # 打ち上げてから咲くまで・広がりきるまで・咲いてから消えるまで（3秒 → 4.7秒）・消えてから次の打ち上げまで（秒）
BASE_FADE = 3.0                              # 散り方を決めた時の 消えるまでの秒（下の 1.1・1.75・2.4・1.7・.6 は この時の秒）
GAPS = [4, 6, 3, 5]                          # 一斉の回から 何回目に 次の一斉の回か（3〜6回に1回）
STAGGER = (0, .1, .2, .3)                    # ふつうの回の 4つの打ち上げのずれ（回ごとに 順番を入れかえる）
SEED = 5
GROUND = 236                                 # 光の玉が出てくる高さ（ちょうちんの上・絵の画素）
NCLS, NSPK = 8, 3                            # 光の粒の組・火の粉の組


def stretch(t):
    """BASE_FADE で消える時の t 秒（咲いてから）を、FADE で消える時の秒に（広がりきってから あとを のばす）"""
    return OPEN + (t - OPEN) * (FADE - OPEN) / (BASE_FADE - OPEN)


Q = (-RISE, -RISE + .08, -.02, 0, OPEN, stretch(1.1), stretch(1.75), stretch(2.4), FADE)   # キーの時刻（咲く時から）：打ち上げ・光の玉が見える・上がりきる・咲く・広がりきる・散る3つ・消える
START = RISE + OPEN                          # ページを開いた時：1回目（一斉の回）の 咲ききったところ


def plan():
    """[(回の はじめの秒, 'all'（一斉）|'one'（ふつう）, [花火4つと馬の 打ち上げの秒（回の はじめから）])], 1回りの秒"""
    rng = random.Random(SEED)
    out, t = [], 0.0
    for g in GAPS:
        out.append((t, 'all', [0.0] * 5))
        t += RISE + FADE + GAP
        for _ in range(g - 1):
            d = list(STAGGER)
            rng.shuffle(d)
            h = max(d) + RISE                  # 馬：4つが ぜんぶ咲いた（消えはじめた）ところで打ち上げ
            out.append((t, 'one', d + [h]))
            t += h + RISE + FADE + GAP
    return out, round(t, 4)


def n(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def star(L, col, gid):
    """きらっ（4つの角の星・白いしん・まわりに花火の色の光）"""
    w = L * .16
    d = f'M0 {-L}Q{w:.1f} {-w:.1f} {L} 0Q{w:.1f} {w:.1f} 0 {L}Q{-w:.1f} {w:.1f} {-L} 0Q{-w:.1f} {-w:.1f} 0 {-L}Z'
    return f'<circle r="{L * .9:.1f}" fill="url(#{gid})"/><path d="{d}" fill="#FFFFFF"/>'


def glints(pts, x0, y0, col, gid, seed):
    out = ''
    for i, (x, y) in enumerate(pts):
        dur = 1.5 + ((i * 7 + seed) % 5) * .22
        dl = -((i * 0.53 + seed * .31) % dur)
        L = 7 + ((i * 3 + seed) % 4) * 1.6
        out += (f'<g transform="translate({x - x0:.1f} {y - y0:.1f})"><g class="hqt" style="animation-duration:{dur:.2f}s;animation-delay:{dl:.2f}s">'
                f'{star(L, col, gid)}</g></g>')
    return out


# ---- 散り方（組ごとの 変数：Q の 5〜8 番目）----

def _u(t):
    return (t - OPEN) / (FADE - OPEN)


def scatter_vars(e, f, op):
    """広がり e（いちばん最後の大きさ）・落ちる f（px）・こさ op=（散る3つのキーの時）→ CSS の変数"""
    s = ''
    for q, t in zip((5, 6, 7, 8), Q[5:]):
        u = _u(t)
        s += f'--y{q}:{n(f * u ** 1.8)}px;--s{q}:{n(1 + (e - 1) * (1 - (1 - u) ** 2), 3)};'
    for q, o in zip((5, 6, 7), op):
        s += f'--o{q}:{n(o)};'
    return s


def fade_op(T, rng):
    """T秒（咲いてから）で消える組の こさ（少し ちらつく）"""
    out = []
    for t in Q[5:8]:
        v = max(0.0, min(1.0, (T - t) / (T - stretch(.6)))) ** .8
        out.append(v * rng.uniform(.72, 1.0))
    return out


def group_params(kind, rng):
    """光の粒 8組：(広がり, 落ちる px, 消える秒)。いちばん長い組は FADE ちょうど"""
    k = (FADE - OPEN) / (BASE_FADE - OPEN)
    ends = [stretch(1.7) + (FADE - stretch(1.7)) * i / (NCLS - 1) + rng.uniform(-.08, .08) * k for i in range(NCLS)]
    ends = [min(FADE, t) for t in ends]
    ends[-1] = FADE
    rng.shuffle(ends)
    if kind == 'burst':
        return [(rng.uniform(1.1, 1.35), rng.uniform(6, 20), t) for t in ends]
    return [(rng.uniform(1.015, 1.07), rng.uniform(5, 15), t) for t in ends]


SPARK_OP = [(1.0, .85, .35), (.6, 1.0, .55), (0.0, .9, .8)]     # 火の粉3組の こさ（早く出る・まん中・おそく出る）


def spark_svg(pts, x0, y0, w, h, k, rng):
    """火の粉（尾の長さ2とおり・いちど defs に書いた形を <use> でならべる）"""
    out = ''
    for x, y in pts:
        dur = rng.uniform(.22, .42)
        out += (f'<use href="#hqK{k}{rng.choice("ab")}" x="{x - x0}" y="{y - y0}" class="hqe" '
                f'style="animation-duration:{dur:.2f}s;animation-delay:-{rng.uniform(0, dur):.2f}s"/>')
    return f'<svg class="hqu hqz" viewBox="0 0 {w} {h}" width="{w // 2}" height="{h // 2}" aria-hidden="true">{out}</svg>'


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def inline(blobs, lay, alt=ALT):
    """(html, css)。blobs：base（花火なしの絵）・scatter（8組に分けた足す光）→ '/_blob/<id>'。lay：fireworks_layers.json"""
    sw, sh = lay['sheet']
    rounds, T = plan()
    H, css_l, kf, defs = '', [], [], ''
    for k, e in enumerate(lay['layers']):
        x, y, w, h = e['rect']
        cx, cy = e['center']
        cl = ((cx - x) / 2, (cy - y) / 2)
        col = e.get('color', '#FFE7A8')
        rng = random.Random(1000 + k)
        par = group_params(e['kind'], rng)
        parts = ''
        for g, (ee, ff, TT) in enumerate(par):
            dur = rng.uniform(.38, .75)
            parts += (f'<div class="hqu hqc" style="{scatter_vars(ee, ff, fade_op(TT, rng))}">'
                      f'<i style="background-position:-{g * sw // 2}px -{e["sheet_y"] // 2}px;animation-duration:{dur:.2f}s;animation-delay:-{rng.uniform(0, dur):.2f}s"></i></div>')
        # 火の粉（3組）
        sp = list(e['sparks'])
        rng.shuffle(sp)
        r_, g_, b_ = _hex(col)
        tint = f'#{(r_ + 255) // 2:02X}{(g_ + 255) // 2:02X}{(b_ + 255) // 2:02X}'
        defs += (f'<radialGradient id="hqS{k}"><stop offset="0" stop-color="{tint}" stop-opacity=".95"/><stop offset=".4" stop-color="{col}" stop-opacity=".55"/>'
                 f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>'
                 f'<linearGradient id="hqZ{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/>'
                 f'<stop offset="1" stop-color="{tint}" stop-opacity=".8"/></linearGradient>'
                 + ''.join(f'<g id="hqK{k}{v}"><rect x="-1.2" y="-{L}" width="2.4" height="{L}" rx="1.2" fill="url(#hqZ{k})"/>'
                           f'<circle r="8" fill="url(#hqS{k})"/><circle r="2.2" fill="#FFFBEF"/></g>' for v, L in (('a', 11), ('b', 17))))
        for j in range(NSPK):
            pts = sp[j::NSPK]
            if e['kind'] == 'burst':
                ee, ff = rng.uniform(1.08, 1.25), rng.uniform(16, 30)
            else:
                ee, ff = rng.uniform(1.0, 1.04), rng.uniform(22, 40)
            svg = spark_svg(pts, x, y, w, h, k, rng)
            parts += svg.replace('class="hqu hqz"', f'class="hqu hqz" style="{scatter_vars(ee, ff, SPARK_OP[j])}"', 1)
        # きらっ（咲いている間）
        gid = f'hqG{k}'
        e_m = sum(p[0] for p in par) / NCLS
        f_m = sum(p[1] for p in par) / NCLS
        parts += (f'<svg class="hqu hqgl" style="{scatter_vars(e_m, f_m, (.5, 0, 0))}" viewBox="0 0 {w} {h}" width="{w // 2}" height="{h // 2}" aria-hidden="true">'
                  f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{col}" stop-opacity=".9"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient></defs>'
                  f'{glints(e["glints"], x, y, col, gid, k)}</svg>')
        # 光の玉（ちょうちんの上から 1秒で まっすぐ上がる・少しずつ ゆっくりに）・咲く時の光
        gx = (-5 if k % 2 else 6) if e['kind'] == 'burst' else 0
        gy = (GROUND - cy) / 2
        rho = 1 - (1 - .08 / (RISE - .02)) ** 2.2
        parts += (f'<div class="hqu hqr" style="--gx:{n(gx)}px;--gy:{n(gy)}px;--hx:{n(gx * (1 - rho))}px;--hy:{n(gy * (1 - rho))}px;left:{n(cl[0] - 7)}px;top:{n(cl[1] - 7)}px">'
                  '<svg viewBox="-14 -14 28 76" width="14" height="38"><path d="M0 2V50" stroke="url(#hqTl)" stroke-width="7" stroke-linecap="round" opacity=".35"/>'
                  '<path d="M0 0V44" stroke="url(#hqTl)" stroke-width="2.6" stroke-linecap="round"/><circle r="11" fill="url(#hqHd)"/><circle r="3.6" fill="#FFF8E0"/></svg></div>'
                  f'<div class="hqu hqf" style="left:{n(cl[0] - 10)}px;top:{n(cl[1] - 10)}px"></div>')
        H += f'<div class="hqk hq{k}">{parts}</div>'
        css_l.append(f'.hqw .hq{k}{{left:{x // 2}px;top:{y // 2}px;width:{w // 2}px;height:{h // 2}px}}'
                     f'.hqw .hq{k} .hqu{{transform-origin:{n(cl[0])}px {n(cl[1])}px;animation-name:hqP{k}}}')
        # キーフレーム：回ごとに 打ち上げ → 咲く → 散る
        stops = []
        for t0, kind, d in rounds:
            B = t0 + d[k] + RISE
            for qi, dt in enumerate(Q):
                stops.append((B + dt, qi))
        kf.append(f'@keyframes hqP{k}{{0%{{{KEY[0]}}}' + ''.join(f'{t / T * 100:.3f}%{{{KEY[qi]}}}' for t, qi in stops if t > 0)
                  + f'100%{{{KEY[0]}}}}}')
        # 見えない 間は 描かない（まさちゃん「他も同じようにいらないデータ使ってるものが、もしあれは整えて！」）：
        # 打ち上げ（Q[0]）から 消える（Q[-1]）までの 外は どの 部品も こさ 0 なので、花火 ひとつ ぶんを visibility:hidden（hqV…・step-end）
        win = sorted((t0 + d[k] + RISE + Q[0], t0 + d[k] + RISE + Q[-1]) for t0, kind, d in rounds)
        vk = [(0.0, any(a <= 0.0 < b for a, b in win))]
        for a, b in win:
            assert 0.0 <= a < b <= T, 'firework window across the loop end'
            vk += [(a, True), (b, False)]
        vs = ''
        for t, on in vk:
            if not vs or vs.rsplit('visibility:', 1)[1].startswith('visible') != on:
                vs += f'{t / T * 100:.3f}%{{visibility:{"visible" if on else "hidden"}}}'
        kf.append(f'@keyframes hqV{k}{{{vs}}}')
        css_l.append(f'.hqw .hq{k}{{animation:hqV{k} {T:g}s step-end -{START:g}s infinite}}')
    defs = ('<svg class="hqd" width="0" height="0" aria-hidden="true"><defs>'
            '<linearGradient id="hqTl" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="46"><stop offset="0" stop-color="#FFF1C4"/><stop offset=".45" stop-color="#FFB45A" stop-opacity=".7"/>'
            '<stop offset="1" stop-color="#FF7A3A" stop-opacity="0"/></linearGradient>'
            '<radialGradient id="hqHd"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".35" stop-color="#FFE7A8" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="#FFD45E" stop-opacity="0"/></radialGradient>{defs}</defs></svg>')
    html = f'<div class="hqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt="">{H}{defs}</div>'
    css = ('.hqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;isolation:isolate}'
           '.hqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           '.hqw .hqk,.hqw .hqu,.hqw .hqd{position:absolute}'
           f'.hqw .hqu{{left:0;top:0;mix-blend-mode:plus-lighter;animation:{T:g}s linear -{START:g}s infinite;'
           '--gx:0px;--gy:0px;--hx:0px;--hy:0px;--r:0;--s0:.2;--b:1;--s4:1;--b4:1;--y5:0px;--y6:0px;--y7:0px;--y8:0px;'
           '--s5:1;--s6:1;--s7:1;--s8:1;--o5:1;--o6:1;--o7:1}'
           f'.hqw .hqc,.hqw .hqc i{{width:100%;height:100%}}.hqw .hqc i{{display:block;background:url({blobs["scatter"]}) 0 0/{NCLS * sw / 2:g}px {sh / 2:g}px no-repeat;'
           'animation:hqI .5s ease-in-out infinite}@keyframes hqI{0%,100%{opacity:1}50%{opacity:.62}}'
           '.hqw .hqz,.hqw .hqgl{overflow:visible}.hqw .hqz{--b:0;--b4:0}'
           '.hqw .hqr{--r:1;--s0:1;--b:0;--b4:0;--o5:0;--o6:0;--o7:0}.hqw .hqr svg{display:block;overflow:visible}'
           '.hqw .hqt{transform-box:view-box;transform-origin:0 0;animation:hqTw 1.8s ease-in-out infinite}'
           '@keyframes hqTw{0%,100%{transform:scale(0) rotate(0)}50%{transform:scale(1) rotate(45deg)}}'
           '.hqw .hqe{animation:hqE .3s ease-in-out infinite}@keyframes hqE{0%,100%{opacity:1}50%{opacity:.2}}'
           + ''.join(css_l)
           + '.hqw .hqk .hqu.hqf{width:20px;height:20px;border-radius:50%;transform-origin:50% 50%;'
           'background:radial-gradient(closest-side,rgba(255,255,255,.95),rgba(255,231,168,.6) 40%,rgba(255,212,94,0));--s0:.4;--b:.95;--s4:1.7;--b4:0;--o5:0;--o6:0;--o7:0}'
           + ''.join(kf)
           + '@media (prefers-reduced-motion:reduce){.hqw .hqu,.hqw .hqc i{animation:none}.hqw .hqz,.hqw .hqgl,.hqw .hqr,.hqw .hqf{display:none}}')
    return html, css


# キーの中身（Q の順）。光の玉は --gx/--gy（打ち上げ）→ --hx/--hy → 0、光の粒は --s0（.2）から 咲いて 1、散る 5〜8。書いていない間は linear（.hqu の animation）
KEY = ['translate:var(--gx) var(--gy);scale:var(--s0);opacity:0',
       'translate:var(--hx) var(--hy);opacity:var(--r);animation-timing-function:cubic-bezier(.25,.55,.5,1)',
       'translate:0 0;opacity:var(--r)',
       'scale:var(--s0);opacity:var(--b);animation-timing-function:cubic-bezier(.12,.7,.3,1)',
       'translate:0 0;scale:var(--s4);opacity:var(--b4)',
       'translate:0 var(--y5);scale:var(--s5);opacity:var(--o5)',
       'translate:0 var(--y6);scale:var(--s6);opacity:var(--o6)',
       'translate:0 var(--y7);scale:var(--s7);opacity:var(--o7)',
       'translate:0 var(--y8);scale:var(--s8);opacity:0']


def judge_inline(fn, blobs, lay):
    """判定画面（Judge_Fireworks.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="hqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, lay)
    page, k = re.subn(r'<div class="hqw" .*?</svg></div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 花火の壁紙：花火が打ち上がって咲き、散り散りに消える。ときどき5つ一斉に（fireworks_wall.py） */\n{css}\n/* /花火の壁紙 */\n'
    if '/* 花火の壁紙：' in page:
        page = re.sub(r'/\* 花火の壁紙：.*?/\* /花火の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def _poisson(xs, ys, wgt, dmin, rng, k=None):
    """明るい所を重みに、dmin より近くならないように 点を選ぶ"""
    out, grid = [], {}
    cs = dmin / math.sqrt(2)
    for i in rng.choice(len(xs), size=len(xs), replace=False, p=wgt / wgt.sum()):
        px, py = int(xs[i]), int(ys[i])
        gx, gy = int(px // cs), int(py // cs)
        if all((px - a) ** 2 + (py - b) ** 2 >= dmin * dmin
               for ix in range(gx - 2, gx + 3) for iy in range(gy - 2, gy + 3) for a, b in grid.get((ix, iy), ())):
            out.append((px, py))
            grid.setdefault((gx, gy), []).append((px, py))
            if k and len(out) == k:
                break
    return out


SCATTER_Q = None                             # None：ロスなし（8まい足すので、ロスありだと 色のずれが たまる）


def scatter(sheet_fn, lay_fn, out_fn):
    """足す光の絵を 光の粒ごとに NCLS 組に分けた絵（組 c は 横に c まいめ）・火の粉の出る点を json に"""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    from scipy.spatial import cKDTree
    S = np.asarray(Image.open(sheet_fn).convert('RGB'), np.float32) / 255
    lay = json.load(open(lay_fn))
    sw, sh = lay['sheet']
    out = np.zeros((sh, sw * NCLS, 3), np.float32)
    for k, e in enumerate(lay['layers']):
        x, y, w, h = e['rect']
        y0 = e['sheet_y']
        im = S[y0:y0 + h, :w]
        lum = im.max(-1)
        rng = np.random.default_rng(700 + k)
        if e['kind'] == 'burst':                     # 光の点（明るさの山）
            ls = ndimage.gaussian_filter(lum, 1.0)
            ys, xs = np.nonzero((ndimage.maximum_filter(ls, size=5) == ls) & (ls > .22))
            P = np.stack([xs, ys], 1).astype(np.float64)
        else:                                        # 線の上に 6px ごと
            ys, xs = np.nonzero(lum > .2)
            P = np.array(_poisson(xs, ys, lum[ys, xs], 6, rng), np.float64)
        # 組：となり（9px より近い）は ちがう組・数は そろえる
        nb = [set() for _ in P]
        for a, b in cKDTree(P).query_pairs(9.0):
            nb[a].add(b)
            nb[b].add(a)
        cls, cnt = [-1] * len(P), [0] * NCLS
        for u in rng.permutation(len(P)):
            used = {cls[v] for v in nb[u]}
            ok = [g for g in range(NCLS) if g not in used] or list(range(NCLS))
            lo = min(cnt[g] for g in ok)
            g = int(rng.choice([g for g in ok if cnt[g] == lo]))
            cls[u] = g
            cnt[g] += 1
        # 境目を ぼかして分ける（ガウスの重み・足すと 1）
        sig, R = 2.2, 8
        acc = np.zeros((NCLS, h, w), np.float64)
        for (px, py), g in zip(P, cls):
            xa, xb, ya, yb = max(0, int(px) - R), min(w, int(px) + R + 1), max(0, int(py) - R), min(h, int(py) + R + 1)
            gx, gy = np.arange(xa, xb) - px, np.arange(ya, yb) - py
            acc[g, ya:yb, xa:xb] += np.exp(-(gy[:, None] ** 2 + gx[None, :] ** 2) / (2 * sig * sig))
        eps = 1e-6
        wts = (acc + eps / NCLS) / (acc.sum(0) + eps)
        for g in range(NCLS):
            out[y0:y0 + h, g * sw:g * sw + w] = im * wts[g][..., None]
        print(e['kind'], k, 'points', len(P), 'per group', cnt)
        # 火の粉の出る点（花火：外がわの光の点から24こ・小さい花火は14こ／馬：線としっぽから36こ）
        ys, xs = np.nonzero(lum > .45)
        r2 = np.random.default_rng(500 + k)
        if e['kind'] == 'burst':
            rr = np.hypot(xs - (e['center'][0] - x), ys - (e['center'][1] - y)) / e['r']
            pts = _poisson(xs, ys, lum[ys, xs] * np.clip(rr - .35, .05, 1), 9, r2, 14 if e['r'] < 50 else 24)
        else:
            pts = _poisson(xs, ys, lum[ys, xs] ** 2, 12, r2, 36)
        e['sparks'] = [[a + x, b + y] for a, b in pts]
    q8 = Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8))
    if not out_fn.endswith('.webp'):
        q8.save(out_fn)
    elif SCATTER_Q is None:
        q8.save(out_fn, 'WEBP', lossless=True, method=6)
    else:
        q8.save(out_fn, 'WEBP', quality=SCATTER_Q, method=6)
    json.dump(lay, open(lay_fn, 'w'), ensure_ascii=False)
    back = sum(out[:, g * sw:(g + 1) * sw] for g in range(NCLS))
    print('sum check (float):', float(np.abs(back - S).max()))


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if '--scatter' in sys.argv:
        i = sys.argv.index('--scatter')
        scatter(sys.argv[i + 1], sys.argv[i + 2], sys.argv[i + 3])
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
