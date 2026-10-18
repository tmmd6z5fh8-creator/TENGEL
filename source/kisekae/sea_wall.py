"""海の壁紙の動き（まさちゃんの指定「常に馬が走っている・背景が移動する、同じ模様をリピートする」）：ページに入れる HTML と CSS
   絵は flat/sea_run.py の4まい（空・海・砂浜＝横にくり返せる絵・馬＝ギャロップのコマを横に並べた絵）。キャンバスでは /_blob/<id>（sea_blobs.json）
   - 景色は右から左へ流れて、同じ模様がくり返す（右向きに走る馬が前に進んで見える）。遠いほどゆっくり：
     空と雲とかもめ 28秒・海 7秒・波打ちぎわと砂浜 2.3秒で1まいぶん（390px）
   - 馬はギャロップのコマを0.48秒で1回（N_FRAMES コマ・steps）。いつも走っている
   - いちばん下は、いまの止まった絵（<img class="bnr">）。視差効果を減らす（prefers-reduced-motion）なら、動く絵を消して止まった絵だけ
   クラスの名前は sq…（ページの .sr（読み上げ用の字）などとぶつからないように）
   python3 sea_wall.py --judge <Judge_Sea.dc.html> <sea_blobs.json> <sea_run.json>  → 判定画面の上の絵を「動く海」に書きかえる（何回やっても同じ）"""
import sys, os, re, json

STATIC = '/_blob/df12d9f0de6cbd26596259ec8f3e4475'        # いまの止まった絵（WebP）
ALT = '波打ちぎわを走る鹿毛の競走馬（紺に白いしまのゼッケン1）と、青い海と空のイラスト（いつも走っていて、景色が流れる）'
FLOW = dict(sq1=28, sq2=7, sq3=2.3)          # 1まいぶん流れる秒（空・海・砂浜）
RUN_S = .48                                  # ギャロップ1回の秒
DIR = -1                                     # 景色の流れる向き（-1＝右から左）


def inline(blobs, run, alt=ALT, static=STATIC):
    """(html, css)。blobs：sky・sea・shore・horse → '/_blob/<id>'。run：sea_run.json（大きさ・置き場所）"""
    W2 = run['size'][0] // 2
    b = run['bands']
    h = run['horse']
    n, (cw, ch), (ax, ay) = h['frames'], h['cell'], h['at']
    cw2, ch2 = cw // 2, ch // 2
    lay = dict(sq1=('sky', b['sky']), sq2=('sea', b['sea']), sq3=('shore', b['shore']))
    html = (f'<div class="seaw" role="img" aria-label="{alt}"><img class="bnr" src="{static}" alt="">'
            + ''.join(f'<div class="sql {k}"></div>' for k in lay) + '<div class="sqh"><div class="sqr"></div></div></div>')
    css = ('.seaw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.seaw .bnr{position:absolute;left:0;top:0}'
           f'.seaw .sql{{position:absolute;left:{0 if DIR < 0 else -W2}px;width:{2 * W2}px;background-repeat:repeat-x;will-change:transform}}')
    for k, (name, (y0, y1)) in lay.items():
        css += (f'.seaw .{k}{{top:{y0 // 2}px;height:{(y1 - y0) // 2}px;background-image:url({blobs[name]});background-size:{W2}px {(y1 - y0) // 2}px;'
                f'animation:seaFlow {FLOW[k]}s linear infinite}}')
    css += (f'@keyframes seaFlow{{from{{transform:translateX(0)}}to{{transform:translateX({DIR * W2}px)}}}}'
            f'.seaw .sqh{{position:absolute;left:{ax // 2}px;top:{ay // 2}px;width:{cw2}px;height:{ch2}px;overflow:hidden}}'
            f'.seaw .sqr{{width:{n * cw2}px;height:{ch2}px;background:url({blobs["horse"]}) 0 0/{n * cw2}px {ch2}px no-repeat;animation:seaRun {RUN_S}s steps({n}) infinite}}'
            f'@keyframes seaRun{{to{{transform:translateX(-{n * cw2}px)}}}}'
            '@media (prefers-reduced-motion:reduce){.seaw .sql,.seaw .sqh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Sea.dc.html）の上の絵を「動く海」に書きかえる（<img class="bnr"> か、前に入れた <div class="seaw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="seaw" .*?<div class="sqr"></div></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 海の壁紙：馬が走って景色が流れる（sea_wall.py） */\n{css}\n/* /海の壁紙 */\n'
    if '/* 海の壁紙：' in page:
        page = re.sub(r'/\* 海の壁紙：.*?/\* /海の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], json.load(open(sys.argv[i + 2])), json.load(open(sys.argv[i + 3])))
