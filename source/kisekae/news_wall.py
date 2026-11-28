"""競馬新聞の壁紙：ページに入れる HTML と CSS
   第4.234版（まさちゃん 2026/11/28 02:44「壁紙の競馬新聞は、馬の絵を消して、2枚目みたいなデザインで、三枚目の馬券入れて！馬券の中の数字を15秒起きにランダムに変えて！
   合計25種類の組み合わせが欲しい」・02:49「数字の前に0を入れないでってこと！」「10はいいよ！」）＝ inline()：
   - いちばん下は 新聞の 紙と 字（馬なし：<img class="bnr">・news_blobs.json の paper）。その 上の まん中（左の 記事と 右の 印の 表の あいだ）に
     馬券 2まい（まさちゃんの 絵：馬単・3連単・news_blobs.json の tickets）。置く 場所と 数字の 枠 5つは news_tk.json（flat/news_ticket.py が 絵から 見つけた もの）
   - 数字は 絵に 描かず 字で 書く（Kaisei Tokumin 800＝競馬新聞の 見出しの 字・頭に 0 を つけない）。枠ごとに 枠の 形（かたむき）に 合わせる（CSS の matrix）
   - 組は TK_COMBOS の 25組（3連単 1着→2着→3着・馬単は その 1着→2着）。TK_S 秒ごとに ランダム：数字の 層（.nsq）の 動き nsTk（TK_S 秒で 1回り・はじめと おわりに
     0.4秒 うすく なる）の 1回りの さかい目で kisekae.js が 次の 組を 書く（止めて いる 間は かわらない）。視差効果を減らす・演出を控えめにする なら 動きなし（数字は 出た まま）
   - 第4.235版（まさちゃん 2026/11/28 08:41「競馬新聞の壁紙、数字切り替わる速度15秒から7秒に変えて！」）：TK_S 15 → 7 秒（うすく なる 0.4秒は そのまま）
   - 前の 形（第4.233版まで：墨の 馬が いつも 走る）は inline_run()（テストと 見本の ため に のこす：アプリには 入れない）
   クラスの名前は ns…
   python3 news_wall.py --judge <Judge_News.dc.html> <news_blobs.json> <news_tk.json>  → 判定画面の上の絵を 馬券の 形に 書きかえる（何回やっても同じ）"""
import sys, os, re, json
from wall_util import feather   # コマの 入れものの ふちを ぼかす（拡大した 時の 細い 線を 消す・2026/10/25）

TK_S = 7                                     # 馬券の 数字が かわる 秒（まさちゃんの 指定：第4.234版 15秒 → 第4.235版 7秒）
ALT = f'競馬新聞の紙面のような、題字と馬柱、馬単と3連単の馬券（馬券の数字が{TK_S}秒ごとにかわる）'
ALT_RUN = '競馬新聞の紙面のような、題字と馬柱、墨の筆でえがいた馬のイラスト（馬がいつも走っている）'
RUN_S = .5                                   # ギャロップ1回の秒（前の 形）
TK_FADE = 0.4                                # かわる ときに うすく なる 秒（前と あと それぞれ）
#  25組（姫が 決めた：1〜16番・頭に 0 なし・3頭は ちがう 馬・馬単の 2頭の 組も 25とおり ぜんぶ ちがう。1組目は まさちゃんの 見本の 番号）
TK_COMBOS = ('3-7-12', '5-2-8', '1-6-3', '8-4-11', '2-9-5', '6-1-14', '4-3-7', '11-5-2', '7-12-1', '9-8-6', '12-3-9', '1-4-16', '5-11-7',
             '13-2-4', '10-6-1', '14-7-5', '2-1-13', '6-10-2', '8-5-3', '15-4-8', '4-12-6', '7-2-10', '16-3-5', '9-1-7', '3-13-15')
TK_INK = '#161616'


def _f(v, n=2):
    s = f'{v:.{n}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def inline(blobs, tk, alt=ALT, combos=TK_COMBOS):
    """(html, css)。blobs：paper（新聞の 紙と 字・馬なし）・tickets（馬券 2まい）→ '/_blob/<id>'。tk：news_tk.json（置く 場所・数字の 枠）"""
    L, T, Wd, Hd = tk['box']; fk = tk['font']
    first = combos[0].split('-')
    cells, rules = [], []
    for n, c in enumerate(tk['cells']):
        (x0, y0), (x1, y1), _, (x3, y3) = c['quad']
        w = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5; h = ((x3 - x0) ** 2 + (y3 - y0) ** 2) ** .5
        m = [(x1 - x0) / w, (y1 - y0) / w, (x3 - x0) / h, (y3 - y0) / h]
        i = c['i']
        cells.append(f'<i class="nsn k{n}" data-tki="{i}">{first[i]}</i>')
        rules.append(f'.nsw .nsn.k{n}{{width:{_f(w)}px;height:{_f(h)}px;font-size:{_f(h * fk)}px;transform:matrix({",".join(_f(v, 4) for v in m)},{_f(x0)},{_f(y0)})}}')
    fi = round(100 * TK_FADE / TK_S, 4)
    html = (f'<div class="nsw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["paper"]}" alt="">'
            f'<div class="nst"><img class="nstk" src="{blobs["tickets"]}" alt=""><div class="nsq" data-tkc="{" ".join(combos)}">{"".join(cells)}</div></div></div>')
    css = ('.nsw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.nsw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.nsw .nst{{position:absolute;left:{L}px;top:{T}px;width:{Wd}px;height:{Hd}px;pointer-events:none}}'
           f'.nsw .nstk{{position:absolute;left:0;top:0;width:{Wd}px;height:{Hd}px}}'
           f'.nsw .nsq{{position:absolute;left:0;top:0;width:{Wd}px;height:{Hd}px;animation:nsTk {TK_S}s linear infinite}}'
           f'.nsw .nsn{{position:absolute;left:0;top:0;display:flex;align-items:center;justify-content:center;box-sizing:border-box;margin:0;padding:0;'
           f'font-family:"Kaisei Tokumin",serif;font-weight:800;font-style:normal;line-height:1;letter-spacing:-.02em;color:{TK_INK};white-space:nowrap;transform-origin:0 0}}'
           + ''.join(rules) +
           f'@keyframes nsTk{{0%{{opacity:0}}{fi}%{{opacity:1}}{_f(100 - fi, 4)}%{{opacity:1}}100%{{opacity:0}}}}'
           '@media (prefers-reduced-motion:reduce){.nsw .nsq{animation:none}}')
    return html, css


def inline_run(blobs, run, alt=ALT_RUN):
    """(html, css)。blobs：static（いまの止まった絵）・run（走るコマ）→ '/_blob/<id>'。run：news_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    html = (f'<div class="nsw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="nsh"><div class="nsr"></div></div></div>')
    css = ('.nsw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.nsw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.nsw .nsh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}' + feather('.nsw .nsh', x0, y0, cw, ch) +
           f'.nsw .nsr{{width:{n * cw}px;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;'
           f'animation:nsRun {RUN_S}s steps({n}) infinite}}'
           f'@keyframes nsRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           '@media (prefers-reduced-motion:reduce){.nsw .nsh{display:none}}')
    return html, css


def judge_inline(fn, blobs, tk):
    """判定画面（Judge_News.dc.html）の上の絵を 馬券の 形に 書きかえる（<img class="bnr">・前の「走る馬」・前に入れた 馬券の <div class="nsw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, tk)
    page, n = re.subn(r'<div class="nsw" .*?<div class="nsr"></div></div></div>|<div class="nsw" .*?</i></div></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 競馬新聞の壁紙：馬単と3連単の馬券・数字は{TK_S}秒ごと（news_wall.py） */\n{css}\n/* /競馬新聞の壁紙 */\n'
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
