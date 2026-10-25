"""ネオンの壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回流れ星が背景に通る」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">・光のつぶなし）。その上に 光のつぶの 足す光（neon_dust.webp・plus-lighter で 重ねると いまの絵と 同じ
     明るさ・ぜんたいが ゆっくり ただよう）と きらめく 粒（<i>・明るさが ふわふわ・少し ゆれる）、馬の動く所に flat/neon_run.py の走るコマ
     （馬と騎手と その光だけの すき通し・横に並べた1まい）を重ねて、RUN_S 秒でギャロップ1回（steps）
     （2026/10/25 まさちゃん「ネオンの黄色丸の中の小さな光は常にキラキラと光りながら動いているようにして！」）
   - 右上の空（馬のうしろの空・太陽の上）を、STAR_S 秒に1回 流れ星が右上から左下へ流れる（白いしんに水色とピンクの光の尾・1秒たらず）。
     流れ星は 馬のコマにかからない所を通る
   - いちばん下の 止まった絵は 背景だけ（馬も 光のつぶも なし・neon_static.webp）。馬は すき通しの コマだけ（下に 止まった 馬が あると 足が 二重に 見える）
   - 視差効果を減らす（prefers-reduced-motion）なら、流れ星と きらめく 粒を 消し、馬は コマ0 で 止め、光のつぶの 層は 止めて 置く
   - キャンバスでは /_blob/<id>（neon_blobs.json の run）・切りぬく場所とコマ数は neon_run.json
   クラスの名前は nq…（的中ボタンの .nn とは別）
   python3 neon_wall.py --judge <Judge_Neon.dc.html> <neon_blobs.json> <neon_run.json>  → 判定画面の上の絵を「走る馬と流れ星」に書きかえる（何回やっても同じ）"""
import sys, re, json, random

ALT = '紫の夜空と光る格子、しま模様の太陽の前を、騎手を乗せて走ってくる光る線の競走馬のイラスト（馬がいつも走り、うしろの光のつぶがきらめき、ときどき流れ星が流れる）'
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


TW_N = 8                                       # きらめきの 予定（プログラム）の 数。粒は どれかを 使い、速さと ずらしを 粒ごとに 変える


def twinkle_programs(rnd):
    """きらめく 粒の 明るさの 予定を TW_N 本（[(1回りの秒, [(秒, 明るさ)…])]・明るさは --w の 何倍か）。
       ふだんは うすく（0.18〜0.32）、1回りの あいだに ランダムに：ぱっと 強く 光って すっと もどる（flare・1.3倍まで）／ふっと 消える（out・0.15〜0.9秒）／
       ちかちか 2〜4回（blip）。マスター帯の 壁紙の 雷（tengel_wall.py：1本ずつ べつべつに ついたり 消えたり）と 同じ 考え方で、粒ごとに 見え方が ちがう
       （2026/10/25 まさちゃん「テンゲルの壁紙のテンゲルアイコンのように、ランダムにキラキラさせて、それぞれが消えたり、より光ったりして、ランダムな見え方にして！」）"""
    progs = []
    for p in range(TW_N):
        P = rnd.uniform(3.6, 6.8)
        base = rnd.uniform(.18, .32)
        pts = [(0.0, base)]
        t = rnd.uniform(.1, .6)
        while t < P - 1.0:
            kind = rnd.choice(('flare', 'flare', 'out', 'blip'))
            if kind == 'flare':
                r, d, pk = rnd.uniform(.06, .14), rnd.uniform(.3, .7), rnd.uniform(.9, 1.3)
                pts += [(t, base), (t + r, pk), (t + r + d, base)]
                t += r + d
            elif kind == 'out':
                d = rnd.uniform(.15, .9)
                pts += [(t, base), (t + .05, 0.0), (t + d, 0.0), (t + d + .05, base)]
                t += d + .1
            else:
                for k in range(rnd.randint(2, 4)):
                    f, pk = rnd.uniform(.05, .1), rnd.uniform(.75, 1.0)
                    pts += [(t, base * .5), (t + f * .4, pk), (t + f, base * .5)]
                    t += f + rnd.uniform(.07, .16)
                pts.append((t, base))
            t += rnd.uniform(.25, 1.1)
        pts.append((P, base))
        progs.append((P, pts))
    return progs


def twinkle_css(progs):
    """予定 → @keyframes nqK0〜（明るさは opacity:calc(var(--w) * 倍)・1 を こえる 分は 1 に なる）"""
    out = []
    for p, (P, pts) in enumerate(progs):
        kf = ''.join(f'{t / P * 100:.2f}%{{opacity:calc(var(--w) * {v:.2f})}}' for t, v in pts)
        out.append(f'@keyframes nqK{p}{{{kf}}}')
    return ''.join(out)


def dust_html(run):
    """光のつぶの 層（足す光の 絵・ゆっくり ただよう）と、きらめく 粒（<b>：明るさが 予定（nqK0〜）どおりに ランダムに かわる・少し ゆれる）。(html, 箱, 予定)"""
    d = run['dust']
    bx, by, bw, bh = (v / 2 for v in d['box'])
    cols = d['cols']
    rnd = random.Random(57)
    progs = twinkle_programs(random.Random(91))
    out = [f'<i class="nqd" aria-hidden="true"></i><div class="nqp" aria-hidden="true">']
    for i, (x, y, ci, w, size) in enumerate(d['sparks']):
        p = rnd.randrange(TW_N)                                                   # どの 予定か
        dur = progs[p][0] * rnd.uniform(.85, 1.2)                                 # 1回りの 速さも 粒ごとに
        sw = max(1.4, min(3.2, size * 1.1))                                      # 粒の 大きさ（画面の px）
        out.append(f'<b class="k{p}" style="left:{x / 2:.1f}px;top:{y / 2:.1f}px;--c:{cols[ci]};--w:{w:.2f};--s:{sw:.1f}px;--d:{dur:.2f}s;--l:{-rnd.random() * dur:.2f}s;'
                   f'--m:{1.5 + rnd.random() * 2.5:.2f}s;--mx:{rnd.uniform(-3, 3):.1f}px;--my:{rnd.uniform(-1.5, 1.5):.1f}px"></b>')
    out.append('</div>')
    return ''.join(out), (bx, by, bw, bh), progs


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵・光のつぶなし）・dust（光のつぶの 足す光）・run（走るコマ：馬だけの すき通し）→ '/_blob/<id>'。run：neon_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    dh, (bx, by, bw, bh), progs = dust_html(run)
    # いちばん下は 背景だけの 止まった絵（static＝馬も 光のつぶも なし・flat/neon_run.py の neon_static.webp）。馬は すき通しの コマだけ。
    #   前は 馬入りの いまの絵を 下に しいていたので、コマの 馬の 足と 下の 止まった 馬の 足が 二重に 見えた（2026/10/25 まさちゃん「馬の足とか馬の絵が重なって…」）
    html = (f'<div class="nqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            f'{dh}<div class="nqh"><div class="nqr"></div></div>{star_svg()}</div>')
    css = ('.nqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;isolation:isolate}'
           '.nqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           # 光のつぶ：足す光（plus-lighter）で 下の絵に 重ねる＝いまの絵と 同じ 明るさ。ぜんたいが ゆっくり ただよう（左右 ±3px・上下 ±1.5px）
           f'.nqw .nqd{{position:absolute;left:{bx:g}px;top:{by:g}px;width:{bw:g}px;height:{bh:g}px;background:url({blobs["dust"]}) 0 0/{bw:g}px {bh:g}px no-repeat;'
           'mix-blend-mode:plus-lighter;will-change:transform;animation:nqDx 5.2s ease-in-out infinite alternate,nqDy 3.1s ease-in-out infinite alternate}'
           '@keyframes nqDx{from{margin-left:-3px}to{margin-left:3px}}'
           '@keyframes nqDy{from{transform:translateY(-1.5px)}to{transform:translateY(1.5px)}}'
           # きらめく 粒：明るさは 予定（nqK0〜7・twinkle_programs）どおりに ランダムに（ぱっと 強く・ふっと 消える・ちかちか）・粒ごとに 予定と 速さと ずらしが ちがう。
           #   小さく ゆれる。色の まわりに 光（box-shadow）
           '.nqw .nqp{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none;mix-blend-mode:plus-lighter}'
           '.nqw .nqp b{position:absolute;display:block;width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;'
           'background:var(--c);box-shadow:0 0 3px var(--c),0 0 6px var(--c);opacity:0;will-change:opacity,transform;'
           'animation:nqK0 var(--d) linear var(--l) infinite,nqMv var(--m) ease-in-out infinite alternate var(--l)}'
           + ''.join(f'.nqw .nqp b.k{p}{{animation-name:nqK{p},nqMv}}' for p in range(1, TW_N))
           + twinkle_css(progs)
           + '@keyframes nqMv{from{transform:translate(calc(var(--mx) * -1),calc(var(--my) * -1))}to{transform:translate(var(--mx),var(--my))}}'
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
           # 視差効果を減らす：流れ星と きらめく 粒は 消す。馬は コマ0 で 止める（下の絵に 馬が ないので 消さない）・光のつぶの 層は 止めて 置く
           '@media (prefers-reduced-motion:reduce){.nqw .nqs,.nqw .nqp{display:none}.nqw .nqr,.nqw .nqd{animation:none}}')
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
