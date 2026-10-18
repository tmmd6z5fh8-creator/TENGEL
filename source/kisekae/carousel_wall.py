"""メリーゴーランドの壁紙の動き（まさちゃんの指定「馬が上下に動く」）：ページに入れる HTML と CSS
   - 下の絵（flat/carousel_banner.py --base：いまの絵から木馬・柱の金の輪・床の影だけをぬいたもの。背景・柱・台・屋根・電球はそのまま）の上に、
     木馬と金の輪と床の影を SVG で描く（いまの絵と同じ形：carousel_banner.horse_parts）
   - 2頭が柱にそって上下する（UP_S 秒で1往復・下へ DOWN・上へ UP（絵の画素）・奥と手前は半分ずらして交互に）。
     木馬と金の輪が一緒に動き、柱と台は動かない。床の影は木馬が上がると小さく・うすくなる
   - 木馬は屋根のふちと電球の うしろを通る（屋根と電球の所を切りぬく clipPath）。柱の下の台は いまの絵と同じく木馬の上に描く
   - 視差効果を減らす（prefers-reduced-motion）なら止まる（いまの絵と同じ場所）
   - キャンバスでは下の絵は /_blob/<id>（carousel_blobs.json の base）
   クラスの名前は cr…
   python3 carousel_wall.py --judge <Judge_Carousel.dc.html> <carousel_blobs.json>  → 判定画面の上の絵を「上下する木馬」に書きかえる（何回やっても同じ）"""
import sys, os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'flat'))
import carousel_banner as CB

ALT = 'しま模様の屋根と電球の下の、金の柱の木馬のイラスト（木馬が柱にそって上下する）'
UP_S = 2.8                     # 1往復の秒
DOWN, UP = 8, 18               # いまの場所から下へ・上へ（絵の画素＝ページでは半分）
PHASE = dict(gold=-UP_S / 2, pink=0.0)   # 奥（金）と手前（ピンク）は半分ずらす


def visible_path():
    """屋根（しま模様の丸い波のふち）と電球の所を ぬいた、見える所（evenodd）"""
    W = CB.W
    d = f'M0 {CB.ROOF_Y}' + ''.join(f'A20 16 0 0 0 {x + 40} {CB.ROOF_Y}' for x in range(0, W, 40)) + f'L{W + 40} {CB.Hh + 40}L0 {CB.Hh + 40}Z'
    r = CB.BULB_R + .7
    for x in range(20, W, 40):
        d += f'M{x - r} {CB.BULB_Y}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0Z'
    return d


def svg(p='cq'):
    """木馬・金の輪・床の影（いまの絵と同じ部品）を、動くグループに入れた SVG（780×320 の座標・ページでは 390×160）"""
    body = ''
    for key, x0, y0, sc in CB.HORSES:                                   # 奥 → 手前
        parts, m = CB.horse_parts(key, x0, y0, sc)
        cx, cy, rx, ry = m['shadow']
        dl = f'animation-delay:{PHASE[key]:g}s'
        get = lambda kind: ''.join(s for k, s in parts if k == kind)
        shadow = get('shadow').replace('url(#sh)', f'url(#{p}sh)').replace(f'cx="{cx:.1f}" cy="296"', 'cx="0" cy="0"')
        body += (f'<g transform="translate({cx:.1f} {cy})"><g class="crd" style="{dl}">{shadow}</g></g>'
                 f'<g clip-path="url(#{p}cl)"><g class="cru" style="{dl}">{get("horse")}{get("ring")}</g></g>{get("base")}')
    defs = (f'<defs><filter id="{p}sh" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="3.2"/></filter>'
            f'<clipPath id="{p}cl"><path d="{visible_path()}" clip-rule="evenodd"/></clipPath></defs>')
    return (f'<svg class="crs" viewBox="0 0 {CB.W} {CB.Hh}" width="390" height="160" aria-hidden="true">{defs}{body}</svg>')


def inline(blobs, alt=ALT):
    """(html, css)。blobs：base（下の絵）→ '/_blob/<id>'"""
    html = f'<div class="crw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt="">{svg()}</div>'
    css = ('.crw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.crw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           '.crw .crs{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           '.crw .cru,.crw .crd{transform-box:view-box;transform-origin:0 0}'
           f'.crw .cru{{animation:crUp {UP_S}s ease-in-out infinite}}'
           f'@keyframes crUp{{0%,100%{{transform:translateY({DOWN}px)}}50%{{transform:translateY(-{UP}px)}}}}'
           f'.crw .crd{{animation:crSh {UP_S}s ease-in-out infinite}}'
           '@keyframes crSh{0%,100%{transform:scale(1.06,1);opacity:1}50%{transform:scale(.8,.9);opacity:.55}}'
           '@media (prefers-reduced-motion:reduce){.crw .cru,.crw .crd{animation:none}}')
    return html, css


def judge_inline(fn, blobs):
    """判定画面（Judge_Carousel.dc.html）の上の絵を「上下する木馬」に書きかえる（<img class="bnr"> か、前に入れた <div class="crw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs)
    page, n = re.subn(r'<div class="crw" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* メリーゴーランドの壁紙：木馬が上下する（carousel_wall.py） */\n{css}\n/* /メリーゴーランドの壁紙 */\n'
    if '/* メリーゴーランドの壁紙：' in page:
        page = re.sub(r'/\* メリーゴーランドの壁紙：.*?/\* /メリーゴーランドの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]))
