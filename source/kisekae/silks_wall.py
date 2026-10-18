"""勝負服の壁紙の動き（まさちゃんの指定「常に走っている、背景が常に右から左に模様が動く同じ模様をリピートする」）：ページに入れる HTML と CSS
   - いちばん下は 背景のくり返しの1まい（flat/silks_run.py の silks_tile.webp・はば PERIOD・左はしの780は いまの絵と同じ）を横にならべ、
     右から左へ FLOW_S 秒で1まい分 流して くり返す（同じ柄がずっと続く）
   - その上に 馬と騎手の走るコマ（silks_run.webp・すき通しつき・もくもく・かげ・顔・流線もいっしょ）を重ねて、RUN_S 秒でギャロップ1回（steps）
   - 視差効果を減らす（prefers-reduced-motion）なら 背景も馬も止まる（コマ0＋背景の左はし＝いまの絵と同じ）
   - キャンバスでは /_blob/<id>（silks_blobs.json の tile・run）・切りぬく場所とコマ数は silks_run.json
   クラスの名前は sb…（的中ボタンの .sj とは別）
   python3 silks_wall.py --judge <Judge_Silks.dc.html> <silks_blobs.json> <silks_run.json>  → 判定画面の上の絵を「走る馬と流れる柄」に書きかえる（何回やっても同じ）"""
import sys, re, json

ALT = '勝負服の柄（市松・縦じま・星・輪）のコマ割りを背に、首と足をいっぱいにのばして走る栗毛の馬と、ひし形の勝負服の騎手の漫画風イラスト（馬がいつも走り、うしろの柄が右から左へ流れる）'
FLOW_S = 14                                   # 背景が1まい分（PERIOD）流れる秒
RUN_S = .5                                    # ギャロップ1回の秒


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：tile（背景）・run（走るコマ）→ '/_blob/<id>'。run：silks_run.json"""
    P = run['period'] // 2
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    html = (f'<div class="sbw" role="img" aria-label="{alt}"><div class="sbb"></div>'
            '<div class="sbh"><div class="sbr"></div></div></div>')
    css = ('.sbw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           f'.sbw .sbb{{position:absolute;left:0;top:0;width:{2 * P}px;height:160px;background:url({blobs["tile"]}) 0 0/{P}px 160px repeat-x;'
           f'animation:sbFlow {FLOW_S}s linear infinite}}'
           f'@keyframes sbFlow{{to{{transform:translateX(-{P}px)}}}}'
           f'.sbw .sbh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.sbw .sbr{{width:{n * cw}px;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;'
           f'animation:sbRun {RUN_S}s steps({n}) infinite}}'
           f'@keyframes sbRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           '@media (prefers-reduced-motion:reduce){.sbw .sbb,.sbw .sbr{animation:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Silks.dc.html）の上の絵を「走る馬と流れる柄」に書きかえる（<img class="bnr"> か、前に入れた <div class="sbw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="sbw" .*?<div class="sbr"></div></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 勝負服の壁紙：馬がいつも走り、柄が右から左へ流れる（silks_wall.py） */\n{css}\n/* /勝負服の壁紙 */\n'
    if '/* 勝負服の壁紙：' in page:
        page = re.sub(r'/\* 勝負服の壁紙：.*?/\* /勝負服の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
