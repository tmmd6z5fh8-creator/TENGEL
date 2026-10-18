"""ドット絵の壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回止まる2秒止まってまた走りだす」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。馬の動く所だけに flat/pixel_run.py のコマ（空・丘・コースごと切りぬいて横に並べた1まい・
     すき通しなし）を重ねる。コマの空・丘・コースは いまの絵と同じなので、切れ目は見えない
   - 10秒で1回り（CYCLE_S）：走りだす（けり出す・土けむり → 1歩め ゆっくり → 2歩め 少し速く・2秒）→ 全速で走る（2〜8秒・RUN_S 秒でギャロップ1回）→
     すべって止まる（ブレーキ2コマ・土けむり）→ 立って待つ（首と頭が少し上下する2コマ）→ かまえる → 10秒で また けり出す。止まっているのは2秒
     （全速の重ね（.pqr・steps）と、それ以外のコマを1つずつ決めた重ね（.pqx・10秒の step-end）を入れかえる。
     どれも同じ時に始まるので ずれない。全速の始まりと終わりは RUN_S の倍数なので、つなぎ目も同じコマ）
   - ページを開いた時は「かまえる」から始まる（どの動きも同じだけ先へ進めて始める：animation-delay -START_AT 秒）
   - 下の絵もコマも ロスなしの WebP（pixel_run.py）で、ドットは ぼかさずに大きくする（image-rendering:pixelated）。画面の細かさが ちがっても
     重ねた所の さかい目が出ない（ドットも くっきり）
   - 視差効果を減らす（prefers-reduced-motion）なら、重ねを消して いまの止まった絵だけ
   - キャンバスでは /_blob/<id>（pixel_blobs.json の static＝下の絵・run＝コマ）・切りぬく場所とコマの並びは pixel_run.json
   クラスの名前は pq…（的中ボタンの .dp とは別）
   python3 pixel_wall.py --judge <Judge_Pixel.dc.html> <pixel_blobs.json> <pixel_run.json>  → 判定画面の上の絵を「走って ときどき止まる馬」に書きかえる（何回やっても同じ）"""
import sys, re, json

ALT = '昔のゲームのようなドット絵で、コースを走る馬と「GO!」の文字（馬がいつも走り、10秒に1回 止まって2秒立ち、また走りだす）'
CYCLE_S = 10                       # 1回りの秒
RUN_S = .5                         # 全速のギャロップ1回の秒（.pqr）
RUN_FROM, RUN_TO = 2.0, 8.0        # 全速で走る時（秒）。どちらも RUN_S の倍数（つなぎ目で同じコマになる）
# 全速のほかの時（.pqx）：(はじまる秒, コマ)。走りだし：けり出す → 1歩め（1コマ0.125秒・ゆっくり）→ 2歩め（0.0875秒・少し速く）→ 全速（0.0625秒）
#   止まる：ブレーキ2コマ → 立つ（交互）→ かまえる → 10秒で けり出す。止まっているのは 8〜10秒の2秒
SEQ = ([(0.0, 'push')] + [(0.30 + 0.125 * i, 'dash' if i == 0 else f'run{i}') for i in range(8)]
       + [(1.30 + 0.0875 * i, f'run{i}') for i in range(8)] + [(RUN_FROM, None)]
       + [(RUN_TO, 'brake0'), (8.15, 'brake1'), (8.30, 'stand0'), (8.75, 'stand1'), (9.20, 'stand0'), (9.65, 'ready')])
START_AT = 9.65                    # ページを開いた時は「かまえる」から（よーい → どん）


def pct(t):
    return f'{round(t / CYCLE_S * 100, 4):g}%'


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵）・run（コマ）→ '/_blob/<id>'。run：pixel_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    order = run['order']
    n, nr = len(order), run['run']
    assert abs(RUN_FROM / RUN_S - round(RUN_FROM / RUN_S)) < 1e-9 and abs(RUN_TO / RUN_S - round(RUN_TO / RUN_S)) < 1e-9
    kx = ''.join(f'{pct(t)}{{opacity:0}}' if k is None else f'{pct(t)}{{opacity:1;transform:translateX({-order.index(k) * cw}px)}}' for t, k in SEQ)
    kx += f'100%{{opacity:1;transform:translateX({-order.index(SEQ[-1][1]) * cw}px)}}'      # 最後のコマ（かまえる）のまま 10秒へ
    d = f'-{START_AT}s'
    html = (f'<div class="pqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="pqh"><i class="pqr"></i><i class="pqx"></i></div></div>')
    css = ('.pqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.pqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%;image-rendering:pixelated}'
           f'.pqw .pqh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.pqw .pqh i{{position:absolute;left:0;top:0;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;image-rendering:pixelated}}'
           f'.pqw .pqh .pqr{{width:{nr * cw}px;opacity:0;animation:pqRun {RUN_S}s steps({nr}) {d} infinite,pqA {CYCLE_S}s step-end {d} infinite}}'
           f'.pqw .pqh .pqx{{width:{n * cw}px;animation:pqX {CYCLE_S}s step-end {d} infinite}}'
           f'@keyframes pqRun{{to{{transform:translateX(-{nr * cw}px)}}}}'
           f'@keyframes pqA{{0%{{opacity:0}}{pct(RUN_FROM)}{{opacity:1}}{pct(RUN_TO)},100%{{opacity:0}}}}'
           f'@keyframes pqX{{{kx}}}'
           '@media (prefers-reduced-motion:reduce){.pqw .pqh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Pixel.dc.html）の上の絵を「走って ときどき止まる馬」に書きかえる（<img class="bnr"> か、前に入れた <div class="pqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, k = re.subn(r'<div class="pqw" .*?</i></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)   # 前に入れた重ね（何回でも同じ）
    assert k == 1, 'banner not found'
    block = f'/* ドット絵の壁紙：馬がいつも走り、10秒に1回 止まって2秒立ち、また走りだす（pixel_wall.py） */\n{css}\n/* /ドット絵の壁紙 */\n'
    if '/* ドット絵の壁紙：' in page:
        page = re.sub(r'/\* ドット絵の壁紙：.*?/\* /ドット絵の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
