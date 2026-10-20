"""桜・紅葉・雪の壁紙の馬が、ときどき 首を下げて 草を食べる（足は 4本とも 動かさない）
   （まさちゃんの指定「この4枚の壁紙後ろ脚動かさない 前足は、6秒〜9秒のランダムで2回動かす。ゆったり 1秒〜5秒のランダムで、地面の草を食べる5秒〜10秒でリピートする。」
    →「やっぱり4枚とも前脚も動かさなくていいよ！ あと首の動きもっとスムーズにして！」。お正月は「一枚目太陽の位置を富士山の真ん中に合わせて！馬の動きは無くして！」で 馬を動かさない）：
   ページに入れる HTML と CSS（コマの絵は flat/step_run.py・時間わりは step_plan.py）。
   - 動く所だけ切りぬいた コマ（55コマ）を たて・よこに並べた1まい（シート）を、いまの絵の上の 同じ場所に重ねて、
     CSS の keyframes で めくる（step-end：つぎの時まで そのコマ。同じコマの時は まとめて1つに書く）。
     時間わりは きまった種の ランダム（約2分で くり返し・つなぎめも 決まりどおり）。ページを開くと コマ0（いまの絵と同じ）から。
     シートの コマの まわりには のりしろ（pad：絵の となりの画素）があって、見えるのは まん中の四角だけ（3倍の画面で となりのコマが にじまない）
   - シートは 背景ごと（すき通しなし）。視差効果を減らす（prefers-reduced-motion）なら シートを消して いまの絵のまま
   - キャンバスの id は step_blobs.json（テーマごとに sheet）・置く場所と大きさ・首の下げぐあい（lower）・時間わりの種は step_run.json
     （flat/step_run.py --sheet が書く）
   クラスの名前は テーマごとに skh（桜）・mjh（紅葉）・ykh（雪）"""
import json
import step_plan

PREFIX = dict(sakura='skh', autumn='mjh', snow='ykh')
ALT_ADD = '・馬が ときどき 首を下げて 草を食べる'


def alt_with(alt):
    """絵の説明（読み上げ）に 馬の動きを足す（さいごの かっこの中へ）"""
    return alt[:-1] + ALT_ADD + '）' if alt.endswith('）') else alt + ALT_ADD


def load(blobs_json, run_json):
    """(blobs, run)：blobs はテーマごとの {名前: '/_blob/<id>'}"""
    b = json.load(open(blobs_json))
    return {t: {k: f'/_blob/{v}' for k, v in d.items()} for t, d in b.items()}, json.load(open(run_json))


def keyframes(theme, run):
    """(くり返しの ミリ秒, keyframes の中身)：コマごとに、そのコマを出す時（%）を まとめて translate を1つ"""
    r = run[theme]
    assert r['names'] == step_plan.frames(theme), 'コマの名前が step_plan とちがう（コマを描きなおす）'
    T_ms, tl = step_plan.timeline(theme, r['lower'], seed=r['plan']['seed'], k=r['plan']['k'])
    assert T_ms == r['plan']['loop_ms'] and len(tl) == r['plan']['changes'], '時間わりが step_run.json とちがう'
    cols = r['cols']
    cw, ch = (v // 2 for v in r['cell'])
    g = r.get('pad', 0) // 2
    by = {}
    for ms, f in tl:
        by.setdefault(f, []).append(ms)
    pct = lambda ms: f'{ms * 100 / T_ms:.3f}'.rstrip('0').rstrip('.') + '%'
    out = []
    for f in sorted(by):
        sel = [pct(ms) for ms in by[f]] + (['100%'] if f == 0 else [])
        assert len(set(sel)) == len(sel)
        row, col = divmod(f, cols)
        x, y = -col * (cw + 2 * g), -row * (ch + 2 * g)
        out.append(f'{",".join(sel)}{{transform:translate({x}px,{y}px)}}')
    return T_ms, ''.join(out)


def sprite(theme, blobs, run):
    """(html, css)。いまの絵（390×160）の上の 同じ場所に重ねる"""
    p = PREFIX[theme]
    r = run[theme]
    n, cols, rows = r['frames'], r['cols'], r['rows']
    assert n <= cols * rows
    cw, ch = (v // 2 for v in r['cell'])
    ax, ay = (v // 2 for v in r['at'])
    g = r.get('pad', 0) // 2                          # コマの まわりの のりしろ（画面の px）：シートの1コマは (cw+2g)×(ch+2g)
    sw, sh = cols * (cw + 2 * g), rows * (ch + 2 * g)
    T_ms, kf = keyframes(theme, run)
    html = f'<div class="{p}" aria-hidden="true"><div class="{p}x"></div></div>'
    css = (f'.{p}{{position:absolute;left:{ax}px;top:{ay}px;width:{cw}px;height:{ch}px;overflow:hidden;pointer-events:none}}'
           f'.{p}x{{position:absolute;left:-{g}px;top:-{g}px;width:{sw}px;height:{sh}px;background:url({blobs[theme]["sheet"]}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:{p}A {T_ms}ms step-end infinite;will-change:transform}}'
           f'@keyframes {p}A{{{kf}}}')
    css += f'@media (prefers-reduced-motion:reduce){{.{p}{{display:none}}}}'
    return html, css
