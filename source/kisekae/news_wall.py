"""競馬新聞の壁紙の動き（まさちゃんの指定「常に馬が走っている」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。その上の、馬が動く所だけに
     flat/news_run.py の走るコマ（紙と字ごと切りぬいて横に並べた1まい・すき通しなし）を重ねて、RUN_S 秒でギャロップ1回（steps）。
     コマの紙と字は いまの絵と同じなので、切れ目は見えない
   - 視差効果を減らす（prefers-reduced-motion）なら、走るコマを消して いまの止まった絵だけ
   - キャンバスでは /_blob/<id>（news_blobs.json の run）・切りぬく場所とコマ数は news_run.json
   クラスの名前は ns…
   python3 news_wall.py --judge <Judge_News.dc.html> <news_blobs.json> <news_run.json>  → 判定画面の上の絵を「走る馬」に書きかえる（何回やっても同じ）"""
import sys, os, re, json

ALT = '競馬新聞の紙面のような、題字と馬柱、墨の筆でえがいた馬のイラスト（馬がいつも走っている）'
RUN_S = .5                                   # ギャロップ1回の秒


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵）・run（走るコマ）→ '/_blob/<id>'。run：news_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    html = (f'<div class="nsw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="nsh"><div class="nsr"></div></div></div>')
    css = ('.nsw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.nsw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.nsw .nsh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.nsw .nsr{{width:{n * cw}px;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;'
           f'animation:nsRun {RUN_S}s steps({n}) infinite}}'
           f'@keyframes nsRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           '@media (prefers-reduced-motion:reduce){.nsw .nsh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_News.dc.html）の上の絵を「走る馬」に書きかえる（<img class="bnr"> か、前に入れた <div class="nsw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="nsw" .*?<div class="nsr"></div></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 競馬新聞の壁紙：墨の馬がいつも走る（news_wall.py） */\n{css}\n/* /競馬新聞の壁紙 */\n'
    if '/* 競馬新聞の壁紙：' in page:
        page = re.sub(r'/\* 競馬新聞の壁紙：.*?/\* /競馬新聞の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
