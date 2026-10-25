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
    """(html, css)。blobs：tile（背景・1まい）・tile2（背景を 2つ つなげた 1まい・<img> で 流す）・run（走るコマ）→ '/_blob/<id>'。run：silks_run.json"""
    P = run['period'] // 2
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    n = run['frames']
    # 背景は くり返しの 1まいを 2つ つなげた 1まいの 絵（tile2・2424×320＝ページの 1212×160）を <img> で 置いて 流す。
    # 1まい分（P）流れたら はじめに もどる（左はしの 390px と P から 390px は 同じ 絵なので、もどる 瞬間に 絵は 変わらない）。
    # iPad では 壁紙を 2〜3.5倍に 拡大するので、流れる 層は 画面より ずっと 大きく、合成の 層は タイルに 分けて 描かれる。
    # 2026/10/25 その1：<div> の background-image（repeat-x）→ <img>（まさちゃん「画面がリピートされている時に、画面が一瞬白くなる、繋ぎ目なくして！」）
    # 2026/10/25 その2（まさちゃん「まだ一瞬画面が白くなる…よく確認して！」）：もどる 瞬間に 見せる 所（層の 左はし 390px）は、14秒 ずっと 画面の 外に あって
    #   その タイルが 捨てられて いるので、もどった 瞬間に 描き直しが 間に 合わず 白く 見えた と 考えて、2つの 仕組みで 白を 出さない：
    #   ① 流れる 絵を 2まい（a・b）にして 14秒ごとに 交代する：動いている 方が 1まい分 流れ おわったら 消え（opacity 0）、もう 1まいが
    #      その 瞬間に 左はし（translateX 0）で 現れて 流れだす。待っている 方は 14秒間 ずっと 左はしに 置いたまま（見えないだけ）なので、
    #      見せる 所の タイルは 描かれて いる。交代は 同じ 絵の 同じ 所どうし（絵は 変わらない）
    #   ② いちばん 下に 同じ 絵（tile2）を 止めて しく（sbb0）：流れる 層が 一瞬 描けなくても、もどる 瞬間の 絵と 同じ 絵が 下に 見える＝白く ならない
    #   （A：0〜14秒 流れる → 14秒で 左はしへ もどって 消える（step-start）→ 28秒で 現れる／B：0〜14秒 左はしで 消えている（step-end）→ 14秒で 現れて 流れる）
    html = (f'<div class="sbw" role="img" aria-label="{alt}">'
            f'<img class="sbb0" src="{blobs["tile2"]}" alt="" draggable="false">'
            f'<img class="sbb a" src="{blobs["tile2"]}" alt="" draggable="false">'
            f'<img class="sbb b" src="{blobs["tile2"]}" alt="" draggable="false">'
            '<div class="sbh"><div class="sbr"></div></div></div>')
    css = ('.sbw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           f'.sbw .sbb0,.sbw .sbb{{position:absolute;left:0;top:0;width:{2 * P}px;height:160px;max-width:none;display:block}}'
           f'.sbw .sbb{{will-change:transform,opacity;animation-duration:{2 * FLOW_S}s;animation-timing-function:linear;animation-iteration-count:infinite}}'
           '.sbw .sbb.a{animation-name:sbFlowA}.sbw .sbb.b{animation-name:sbFlowB}'
           f'@keyframes sbFlowA{{0%{{transform:translateX(0);opacity:1}}50%{{transform:translateX(-{P}px);opacity:1;animation-timing-function:step-start}}100%{{transform:translateX(0);opacity:0}}}}'
           f'@keyframes sbFlowB{{0%{{transform:translateX(0);opacity:0;animation-timing-function:step-end}}50%{{transform:translateX(0);opacity:1}}100%{{transform:translateX(-{P}px);opacity:1}}}}'
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
