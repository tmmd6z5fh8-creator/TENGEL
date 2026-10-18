"""ドット絵の壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回止まる2秒止まってまた走りだす」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。馬の動く所だけに flat/pixel_run.py のコマ（空・丘・コースごと切りぬいて横に並べた1まい・
     すき通しなし）を重ねる。コマの空・丘・コースは いまの絵と同じなので、切れ目は見えない
   - 10秒で1回り（CYCLE_S）：はじめの8秒は走る（RUN_S 秒でギャロップ1回・steps。8秒で ちょうど16回なので、毎回同じコマで止まる）→
     すべって止まる（ブレーキ2コマ・土けむり）→ 立って待つ（首と頭が少し上下する2コマ）→ 10秒で また走りだす。止まっているのは2秒
     （走る・止まる・立つ の3つの重ねを、10秒の steps で入れかえる。どれも同じ時に始まるので ずれない）
   - 下の絵もコマも ロスなしの WebP（pixel_run.py）で、ドットは ぼかさずに大きくする（image-rendering:pixelated）。画面の細かさが ちがっても
     重ねた所の さかい目が出ない（ドットも くっきり）
   - 視差効果を減らす（prefers-reduced-motion）なら、重ねを消して いまの止まった絵だけ
   - キャンバスでは /_blob/<id>（pixel_blobs.json の static＝下の絵・run＝コマ）・切りぬく場所とコマの並びは pixel_run.json
   クラスの名前は pq…（的中ボタンの .dp とは別）
   python3 pixel_wall.py --judge <Judge_Pixel.dc.html> <pixel_blobs.json> <pixel_run.json>  → 判定画面の上の絵を「走って ときどき止まる馬」に書きかえる（何回やっても同じ）"""
import sys, re, json

ALT = '昔のゲームのようなドット絵で、コースを走る馬と「GO!」の文字（馬がいつも走り、10秒に1回 止まって2秒立つ）'
CYCLE_S = 10                       # 1回りの秒
RUN_S = .5                         # ギャロップ1回の秒（8秒で16回）
STOP_AT = 80                       # 止まりはじめ（%）＝8秒
BRAKE = (80, 81.5, 83)             # ブレーキ1コマめ・2コマめ・おわり（%）
STAND = (83, 88.5, 94)             # 立つ：1コマめ・2コマめ・1コマめ（%）。100% で また走る


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵）・run（コマ）→ '/_blob/<id>'。run：pixel_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    order = run['order']
    n, nr = len(order), run['run']
    ib, isd = order.index('brake0'), order.index('stand0')
    html = (f'<div class="pqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="pqh"><i class="pqr"></i><i class="pqb"></i><i class="pqs"></i></div></div>')
    css = ('.pqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.pqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%;image-rendering:pixelated}'
           f'.pqw .pqh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.pqw .pqh i{{position:absolute;left:0;top:0;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;image-rendering:pixelated}}'
           f'.pqw .pqh .pqr{{width:{nr * cw}px;animation:pqRun {RUN_S}s steps({nr}) infinite,pqA {CYCLE_S}s step-end infinite}}'
           f'.pqw .pqh .pqb{{width:{2 * cw}px;background-position:-{ib * cw}px 0;opacity:0;animation:pqB {CYCLE_S}s step-end infinite}}'
           f'.pqw .pqh .pqs{{width:{2 * cw}px;background-position:-{isd * cw}px 0;opacity:0;animation:pqS {CYCLE_S}s step-end infinite}}'
           f'@keyframes pqRun{{to{{transform:translateX(-{nr * cw}px)}}}}'
           f'@keyframes pqA{{0%{{opacity:1}}{STOP_AT}%,100%{{opacity:0}}}}'
           f'@keyframes pqB{{0%,{BRAKE[2]}%,100%{{opacity:0;transform:none}}{BRAKE[0]}%{{opacity:1;transform:none}}'
           f'{BRAKE[1]}%{{opacity:1;transform:translateX(-{cw}px)}}}}'
           f'@keyframes pqS{{0%{{opacity:0;transform:none}}{STAND[0]}%{{opacity:1;transform:none}}{STAND[1]}%{{opacity:1;transform:translateX(-{cw}px)}}'
           f'{STAND[2]}%,100%{{opacity:1;transform:none}}}}'
           '@media (prefers-reduced-motion:reduce){.pqw .pqh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Pixel.dc.html）の上の絵を「走って ときどき止まる馬」に書きかえる（<img class="bnr"> か、前に入れた <div class="pqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, k = re.subn(r'<div class="pqw" .*?</i></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* ドット絵の壁紙：馬がいつも走り、10秒に1回 止まって2秒立つ（pixel_wall.py） */\n{css}\n/* /ドット絵の壁紙 */\n'
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
