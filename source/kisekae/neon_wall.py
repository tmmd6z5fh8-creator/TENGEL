"""ネオンの壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回流れ星が背景に通る」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">・光のつぶなし）。その上に 光のつぶ（236こ・1つずつ <i>・plus-lighter）、
     馬の動く所に flat/neon_run.py の走るコマ（馬と騎手と その光だけの すき通し・横に並べた1まい）を重ねて、RUN_S 秒でギャロップ1回（steps）
     （2026/10/25 まさちゃん「ネオンの黄色丸の中の小さな光は常にキラキラと光りながら動いているようにして！」）
   - 光のつぶ（第4.87版・まさちゃん「六枚目のネオンは、お尻から出る光が全体的にそれぞれランダムに動いたり消えたり、輝いたりしてないから直して！」）：
     前は つぶの 足す光の 絵（neon_dust.webp）が まとめて ただよい、明るい 44こだけが きらめいて いた → 236こ ぜんぶが ばらばらに：
     ふわっと 出て → お尻から うしろへ 流れながら（向き・速さ・ゆれ・長さは つぶごと）ぱっと 強く 光る／ふっと 消える／ちかちか → すっと 消えて もとの 場所から また。
     動きと 明るさの 予定は LIFE_K 本（life_programs）を つぶごとに 1つ（流れる 向きが お尻からの 向きに 近い もの）・長さと ずらしは つぶごと。
     CSS の 変数（var()）は keyframes の 中で 使わない（iOS 16.3 までの WebKit は keyframes の 中の 変数が 効かない ことが ある）
   - 右上の空（馬のうしろの空・太陽の上）を、STAR_S 秒に1回 流れ星が右上から左下へ流れる（白いしんに水色とピンクの光の尾・1秒たらず）。
     流れ星は 馬のコマにかからない所を通る
   - いちばん下の 止まった絵は 背景だけ（馬も 光のつぶも なし・neon_static.webp）。馬は すき通しの コマだけ（下に 止まった 馬が あると 足が 二重に 見える）
   - 視差効果を減らす（prefers-reduced-motion）なら、流れ星を 消し、馬は コマ0 で 止め、光のつぶは もとの 場所に 止めて 置く
   - キャンバスでは /_blob/<id>（neon_blobs.json の run）・切りぬく場所とコマ数は neon_run.json
   クラスの名前は nq…（的中ボタンの .nn とは別）
   python3 neon_wall.py --judge <Judge_Neon.dc.html> <neon_blobs.json> <neon_run.json>  → 判定画面の上の絵を「走る馬と流れ星」に書きかえる（何回やっても同じ）"""
import sys, re, json, random, math

ALT = '紫の夜空と光る格子、しま模様の太陽の前を、騎手を乗せて走ってくる光る線の競走馬のイラスト（馬がいつも走り、うしろの光のつぶが流れながらきらめき、ときどき流れ星が流れる）'
RUN_S = .52                                   # ギャロップ1回の秒
STAR_S = 10                                   # 流れ星の間かく（秒）
STAR = dict(x0=800, y0=-12, x1=520, y1=70)    # 流れ星のしん（頭）の通り道（絵の画素 780×320）


def star_svg():
    """流れ星（頭が 0,0・尾は右上へ）。動きは CSS（.nqm）"""
    dx, dy = STAR['x0'] - STAR['x1'], STAR['y0'] - STAR['y1']
    L = (dx * dx + dy * dy) ** .5
    ux, uy = dx / L, dy / L                                  # 尾の向き（頭から右上へ）
    tx, ty = ux * 180, uy * 180
    return ('<svg class="nqs" viewBox="0 0 780 320" width="390" height="160" aria-hidden="true"><defs>'
            f'<linearGradient id="nqT" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{tx:.1f}" y2="{ty:.1f}">'
            '<stop offset="0" stop-color="#FFFFFF"/><stop offset=".18" stop-color="#C8FBFF"/><stop offset=".55" stop-color="#2EEBFF" stop-opacity=".55"/>'
            '<stop offset="1" stop-color="#FF2BD6" stop-opacity="0"/></linearGradient>'
            '<filter id="nqB" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter></defs>'
            '<g class="nqm">'
            f'<path d="M0 0L{tx:.1f} {ty:.1f}" stroke="url(#nqT)" stroke-width="9" stroke-linecap="round" filter="url(#nqB)" opacity=".9"/>'
            f'<path d="M0 0L{tx:.1f} {ty:.1f}" stroke="url(#nqT)" stroke-width="3" stroke-linecap="round"/>'
            '<circle r="8" fill="#2EEBFF" opacity=".55" filter="url(#nqB)"/><circle r="3" fill="#FFFFFF"/></g></svg>')


LIFE_K = 16                                    # 光のつぶの 一生の 予定（プログラム）の 数
LIFE_S = (2.6, 6.2)                            # つぶの 一生（秒）：つぶごとに この あいだで
DOT_Z = (1.2, 1.6, 2.0, 2.5)                   # 点の 大きさ（画面の px・4つに まとめる）
LINE_Z = (2.4, 3.4, 4.4, 5.6)                  # 筋の 長さ（画面の px）
W_Q = (.25, .5, .75, 1.0)                      # こさ（4つに まとめる）
LINE_TILT = -math.degrees(math.atan(.12))      # 筋の かたむき（いまの絵と 同じ：うしろの はしが 少し 下）


def life_programs(rnd):
    """光の つぶ 1つの 一生の 予定 LIFE_K 本：dict(a＝流れる 向き（ラジアン・π＝左）, stops＝[(時 0〜1, x px, y px, 明るさ, 大きさ)…])。
       ふわっと 出る → 流れながら ランダムに：ぱっと 強く 光る（flare：こく 大きく）／ふっと 消える（out）／ちかちか（blip）→ すっと 消える。
       流れは 向き a へ D px（はじめ 速い／ずっと 同じ／あとで 速い）＋ 横に ゆれ（波）。マスター帯の 壁紙の 雷（tengel_wall.py）と 同じ 考え方"""
    progs = []
    for p in range(LIFE_K):
        a = math.pi + (p + rnd.uniform(.15, .85)) / LIFE_K * 1.5 - .75          # 左の ±43° を 16本で わける（向きは かぶらない）
        D, A = rnd.uniform(6, 18), rnd.uniform(.8, 2.8)
        ease, ph, cyc = rnd.choice((.6, .8, 1.0, 1.3)), rnd.uniform(0, 2 * math.pi), rnd.choice((.6, 1.0, 1.4))
        base = rnd.uniform(.7, .92)
        ein, eout = rnd.uniform(.06, .13), rnd.uniform(.8, .9)
        ev = [(0.0, 0.0, .5), (ein, base, 1.0)]
        t = ein + rnd.uniform(.03, .12)
        while t < eout - .12:
            kind = rnd.choice(('flare', 'flare', 'out', 'blip'))
            if kind == 'flare':
                r, d = rnd.uniform(.02, .045), rnd.uniform(.07, .16)
                ev += [(t, base, 1.0), (t + r, 1.0, rnd.uniform(1.6, 2.2)), (t + r + d, base, 1.0)]
                t += r + d
            elif kind == 'out':
                d = rnd.uniform(.05, .16)
                ev += [(t, base, 1.0), (t + .02, 0.0, .7), (t + .02 + d, 0.0, .7), (t + .04 + d, base, 1.0)]
                t += d + .04
            else:
                for _ in range(rnd.randint(2, 3)):
                    f = rnd.uniform(.018, .03)
                    ev += [(t, base * .3, .85), (t + f * .4, 1.0, 1.35), (t + f, base * .3, .85)]
                    t += f + rnd.uniform(.012, .03)
                ev.append((t, base, 1.0))
            t += rnd.uniform(.05, .18)
        ev = [e for e in ev if e[0] < eout - .01] + [(eout, base, 1.0), (1.0, 0.0, .6)]
        stops = []
        for t, v, k in ev:
            f = t ** ease
            g = math.sin(ph + 2 * math.pi * cyc * t) - math.sin(ph)
            # 向き a へ f×D・それと 直角に g×A
            x = math.cos(a) * f * D - math.sin(a) * g * A
            y = math.sin(a) * f * D + math.cos(a) * g * A
            stops.append((t, x, y, v, k))
        progs.append(dict(a=a, stops=stops))
    return progs


def life_css(progs, pre='nqL'):
    """予定 → @keyframes nqL0〜（opacity と transform：数は ぜんぶ 書きこみ・変数なし）"""
    f2 = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.') if abs(v) >= .005 else '0'
    out = []
    for p, pr in enumerate(progs):
        seen, kf = set(), ''
        for t, x, y, v, k in pr['stops']:
            pc = f'{t * 100:.2f}'.rstrip('0').rstrip('.') + '%'
            assert pc not in seen, (p, pc)
            seen.add(pc)
            kf += f'{pc}{{opacity:{f2(v)};transform:translate({f2(x)}px,{f2(y)}px) scale({f2(k)})}}'
        out.append(f'@keyframes {pre}{p}{{{kf}}}')
    return ''.join(out)


def dust_html(run):
    """光のつぶ 236こ（<i>：点は まるい 光・筋は 細い 光の 線（<b class="ln"> で かたむける））。(html, 予定)"""
    d = run['dust']
    cx, cy = d['center']
    rnd = random.Random(57)
    progs = life_programs(random.Random(91))
    near = lambda v, zs: min(range(len(zs)), key=lambda i: abs(zs[i] - v))
    out = ['<div class="nqp" aria-hidden="true">']
    for x, y, kind, size, ci, w in d['parts']:
        # 流れる 向き：雲の まん中から この つぶへの 向き ＋ ゆらぎ → いちばん 近い 向きの 予定
        a = math.atan2(y - cy, x - cx) + rnd.gauss(0, .3)
        p = min(range(LIFE_K), key=lambda i: abs(math.remainder(progs[i]['a'] - a, 2 * math.pi)))
        dur = rnd.uniform(*LIFE_S)
        tm = f'animation-duration:{dur:.2f}s;animation-delay:{-rnd.random() * dur:.2f}s'
        cls = f'k{p} w{ci}{near(w, W_Q)}'
        if kind == 0:
            out.append(f'<i class="z{near(size * 1.05, DOT_Z)} {cls}" style="left:{x / 2:.1f}px;top:{y / 2:.1f}px;{tm}"></i>')
        else:
            out.append(f'<b class="ln" style="left:{x / 2:.1f}px;top:{y / 2:.1f}px"><i class="q{near(size / 2, LINE_Z)} {cls}" style="{tm}"></i></b>')
    out.append('</div>')
    return ''.join(out), progs


def dust_css(run, progs):
    """光のつぶの CSS（足す光で 重ねる・色と こさ・大きさ・予定）"""
    cols = run['dust']['cols']
    rgb = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    css = ('.nqw .nqp{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none;mix-blend-mode:plus-lighter}'
           '.nqw .nqp i{position:absolute;display:block;border-radius:50%;opacity:.8;animation:nqL0 4s linear infinite}'
           f'.nqw .nqp .ln{{position:absolute;width:0;height:0;transform:rotate({LINE_TILT:.2f}deg)}}'
           '.nqw .nqp .ln i{left:auto;right:0;top:-.5px;height:1px;border-radius:.5px;transform-origin:100% 50%}')
    for i, z in enumerate(DOT_Z):
        css += f'.nqw .nqp .z{i}{{width:{z}px;height:{z}px;margin:-{z / 2:g}px 0 0 -{z / 2:g}px}}'
    for i, z in enumerate(LINE_Z):
        css += f'.nqw .nqp .q{i}{{width:{z}px}}'
    for ci, c in enumerate(cols):                  # 色と こさ：まん中は その色・まわりに 光（いまの絵の ぼかした 光と 同じくらい）
        r, g, b = rgb(c)
        for j, w in enumerate(W_Q):
            col = f'rgba({r},{g},{b},{w:g})'
            css += f'.nqw .nqp .w{ci}{j}{{background:{col};box-shadow:0 0 2px {col},0 0 5px {col}}}'
    css += ''.join(f'.nqw .nqp .k{p}{{animation-name:nqL{p}}}' for p in range(1, LIFE_K)) + life_css(progs)
    return css


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵・光のつぶなし）・run（走るコマ：馬だけの すき通し）→ '/_blob/<id>'。run：neon_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    dh, progs = dust_html(run)
    # いちばん下は 背景だけの 止まった絵（static＝馬も 光のつぶも なし・flat/neon_run.py の neon_static.webp）。馬は すき通しの コマだけ。
    #   前は 馬入りの いまの絵を 下に しいていたので、コマの 馬の 足と 下の 止まった 馬の 足が 二重に 見えた（2026/10/25 まさちゃん「馬の足とか馬の絵が重なって…」）
    html = (f'<div class="nqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            f'{dh}<div class="nqh"><div class="nqr"></div></div>{star_svg()}</div>')
    css = ('.nqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;isolation:isolate}'
           '.nqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           # 光のつぶ：足す光（plus-lighter）で 下の絵に 重ねる。1つずつ ばらばらに 流れて 光って 消える（dust_css・第4.87版）
           + dust_css(run, progs) +
           f'.nqw .nqh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.nqw .nqr{{width:{n * cw}px;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;'
           f'animation:nqRun {RUN_S}s steps({n}) infinite}}'
           f'@keyframes nqRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           '.nqw .nqs{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           '.nqw .nqm{transform-box:view-box;transform-origin:0 0;opacity:0;'
           f'animation:nqStar {STAR_S}s linear 2s infinite}}'
           f'@keyframes nqStar{{0%{{opacity:0;transform:translate({STAR["x0"]}px,{STAR["y0"]}px)}}1.5%{{opacity:1}}'
           f'7%{{opacity:1}}9.5%{{opacity:0;transform:translate({STAR["x1"]}px,{STAR["y1"]}px)}}'
           f'100%{{opacity:0;transform:translate({STAR["x1"]}px,{STAR["y1"]}px)}}}}'
           # 視差効果を減らす：流れ星は 消す。馬は コマ0 で 止める（下の絵に 馬が ないので 消さない）・光のつぶは もとの 場所に 止めて 置く（こさ 0.8）
           '@media (prefers-reduced-motion:reduce){.nqw .nqs{display:none}.nqw .nqr,.nqw .nqp i{animation:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Neon.dc.html）の上の絵を「走る馬と流れ星」に書きかえる（<img class="bnr"> か、前に入れた <div class="nqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="nqw" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* ネオンの壁紙：馬がいつも走り、10秒に1回 流れ星（neon_wall.py） */\n{css}\n/* /ネオンの壁紙 */\n'
    if '/* ネオンの壁紙：' in page:
        page = re.sub(r'/\* ネオンの壁紙：.*?/\* /ネオンの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
