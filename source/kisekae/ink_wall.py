"""水墨画の壁紙の動き（まさちゃんの指定「常に馬が走っている」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。その上の、2頭が動く所だけに
     flat/sumi_run.py の走るコマ（紙・山・地面ごと切りぬいて横に並べた1まい・すき通しなし）を重ねて、RUN_S 秒でギャロップ1回（steps）。
     コマの紙・山・地面・しぶき・落款は いまの絵と同じなので、切れ目は見えない
   - 視差効果を減らす（prefers-reduced-motion）なら、走るコマを消して いまの止まった絵だけ
   - キャンバスでは /_blob/<id>（ink_blobs.json の run）・切りぬく場所とコマ数は ink_run.json
   クラスの名前は ik…（競馬新聞の news_wall.py と同じ形）
   python3 ink_wall.py --judge <Judge_Ink.dc.html> <ink_blobs.json> <ink_run.json>  → 判定画面の上の絵を「走る2頭」に書きかえる（何回やっても同じ）"""
import sys, os, re, json
from wall_util import feather   # コマの 入れものの ふちを ぼかす（拡大した 時の 細い 線を 消す・2026/10/25）

ALT = '和紙に墨の線と灰色のぼかしでえがいた、騎手を乗せて競り合う2頭の競走馬と、朱色の落款のイラスト（2頭がいつも走っている）'
RUN_S = .52                                  # ギャロップ1回の秒


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵）・run（走るコマ）→ '/_blob/<id>'。run：ink_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    html = (f'<div class="ikw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="ikh"><div class="ikr"></div></div></div>')
    css = ('.ikw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.ikw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.ikw .ikh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}' + feather('.ikw .ikh', x0, y0, cw, ch) +
           f'.ikw .ikr{{width:{n * cw}px;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;'
           f'animation:ikRun {RUN_S}s steps({n}) infinite}}'
           f'@keyframes ikRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           '@media (prefers-reduced-motion:reduce){.ikw .ikh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Ink.dc.html）の上の絵を「走る2頭」に書きかえる（<img class="bnr"> か、前に入れた <div class="ikw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="ikw" .*?<div class="ikr"></div></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 水墨画の壁紙：2頭がいつも走る（ink_wall.py） */\n{css}\n/* /水墨画の壁紙 */\n'
    if '/* 水墨画の壁紙：' in page:
        page = re.sub(r'/\* 水墨画の壁紙：.*?/\* /水墨画の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
