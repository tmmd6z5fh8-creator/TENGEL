"""桜・紅葉・雪・お正月の壁紙の馬が、いつも ゆったり 足ぶみして 首を動かす（まさちゃんの指定「この４つの壁紙、常に足と首を動かして！ゆったりめで！」）：
   ページに入れる HTML と CSS（コマの絵は flat/step_run.py）。
   - 動く所だけ切りぬいた コマ（N コマ）を たて・よこに並べた1まい（シート）を、いまの絵の上の 同じ場所に重ねて、CSS の steps で めくる
     （よこ COLS コマを 1段の秒で・たての段を 1回りの秒で。どちらも ミリ秒の整数なので ずれない）。ページを開くと コマ0（いまの絵と同じ）から。
     シートの コマの まわりには のりしろ（pad：絵の となりの画素）があって、見えるのは まん中の四角だけ（3倍の画面で となりのコマが にじまない）
   - 桜・紅葉・雪：シートは 背景ごと（すき通しなし）。視差効果を減らす（prefers-reduced-motion）なら シートを消して いまの絵のまま
   - お正月：シートは 光より前の絵の 切りぬき（すき通しつき）で、光より前の絵は その四角を すき通しにした1まい（top）に かえる
     （光が うしろで回るので）。視差効果を減らすなら めくらない（コマ0＝いまの絵）
   - キャンバスの id は step_blobs.json（テーマごとに sheet・お正月は top も）・置く場所と大きさは step_run.json（flat/step_run.py --sheet が書く）
   クラスの名前は テーマごとに skh（桜）・mjh（紅葉）・ykh（雪）・nyh（お正月）"""
import json

PREFIX = dict(sakura='skh', autumn='mjh', snow='ykh', newyear='nyh')
ALT_ADD = '・馬が いつも ゆっくり足ぶみして 首を上下に動かす'


def alt_with(alt):
    """絵の説明（読み上げ）に 足ぶみ を足す（さいごの かっこの中へ）"""
    return alt[:-1] + ALT_ADD + '）' if alt.endswith('）') else alt + ALT_ADD


def load(blobs_json, run_json):
    """(blobs, run)：blobs はテーマごとの {名前: '/_blob/<id>'}"""
    b = json.load(open(blobs_json))
    return {t: {k: f'/_blob/{v}' for k, v in d.items()} for t, d in b.items()}, json.load(open(run_json))


def sprite(theme, blobs, run):
    """(html, css)。いまの絵（390×160）の上の 同じ場所に重ねる"""
    p = PREFIX[theme]
    r = run[theme]
    n, cols, rows = r['frames'], r['cols'], r['rows']
    assert n == cols * rows
    cw, ch = (v // 2 for v in r['cell'])
    ax, ay = (v // 2 for v in r['at'])
    g = r.get('pad', 0) // 2                          # コマの まわりの のりしろ（画面の px）：シートの1コマは (cw+2g)×(ch+2g)
    sw, sh = cols * (cw + 2 * g), rows * (ch + 2 * g)
    cyc = int(round(r['cycle'] * 1000))
    assert cyc % rows == 0
    row = cyc // rows
    html = f'<div class="{p}" aria-hidden="true"><div class="{p}y"><div class="{p}x"></div></div></div>'
    css = (f'.{p}{{position:absolute;left:{ax}px;top:{ay}px;width:{cw}px;height:{ch}px;overflow:hidden;pointer-events:none}}'
           f'.{p}y{{position:absolute;left:-{g}px;top:-{g}px;width:{sw}px;height:{sh}px;animation:{p}Y {cyc}ms steps({rows}) infinite;will-change:transform}}'
           f'.{p}x{{width:{sw}px;height:{sh}px;background:url({blobs[theme]["sheet"]}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:{p}X {row}ms steps({cols}) infinite;will-change:transform}}'
           f'@keyframes {p}Y{{to{{transform:translateY(-{sh}px)}}}}'
           f'@keyframes {p}X{{to{{transform:translateX(-{sw}px)}}}}')
    if theme == 'newyear':
        css += f'@media (prefers-reduced-motion:reduce){{.{p}y,.{p}x{{animation:none}}}}'
    else:
        css += f'@media (prefers-reduced-motion:reduce){{.{p}{{display:none}}}}'
    return html, css
