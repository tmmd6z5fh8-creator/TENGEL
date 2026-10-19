"""お正月（午年）の壁紙の動き（まさちゃんの指定「初日の出の太陽から出る光が、右回りで常に動いている」）：ページに入れる HTML と CSS
   絵は flat/newyear_banner.py --layers の2まい（光より うしろ＝赤地と青海波・光より前＝初日の出・富士山・金の雲・馬・「午」・金の粉＝すき通しつき）。
   キャンバスでは /_blob/<id>（newyear_blobs.json）
   - あいだに初日の出の光（12本・金・まん中から遠いほど うすい＝いままでの絵の光と同じ決まり・newyear_sun.json）を SVG で描いて、
     太陽のまん中を中心に 右回り（時計回り）に いつも回す（ROT_S 秒で1回り）
   - 回る前は いままでの絵とほぼ同じ。視差効果を減らす（prefers-reduced-motion）なら回らない（いままでの絵のまま）
   - アプリのファイルの形：svg/newyear_rays.svg（光だけ・中の <style> で回る・390×160・背景なし）を、2まいの絵のあいだに <img> で重ねる
   クラスの名前は ny…
   python3 newyear_wall.py <出力フォルダ> [--judge <Judge_NewYear.dc.html> <newyear_blobs.json>] [--step <step_blobs.json> <step_run.json>] <newyear_sun.json>
     → newyear_rays.svg（＋判定画面の上の絵を「回る光」の形に書きかえる・何回やっても同じ。--step で 馬が いつも ゆっくり足ぶみして 首を動かす：step_wall.py）"""
import sys, os, re, json, math

W, H = 390, 160
ROT_S = 36                                   # 1回りの秒
ALT = '赤い青海波の背景に富士山と初日の出、前足を上げる白い競走馬（金のたてがみ・赤い頭のベルト・首に紅白の綱と金の鈴・ゼッケン1）のイラスト（初日の出の光が右回りに回っている）'


def rays_svg_inner(sun, gid='nyG'):
    """光（<defs> と回るグループ）。sun：newyear_sun.json（780×320 の大きさで書いてある → 半分にする）"""
    sx, sy, _ = (v / 2 for v in sun['sun'])
    n, thr, a0, dec = sun['n'], sun['thr'], sun['alpha'], sun['decay'] / 2
    R = 300                                  # 光の長さ（絵のすみまでとどく）
    stops = ''.join(f'<stop offset="{t:.2f}" stop-color="{sun["color"]}" stop-opacity="{a0 * math.exp(-t * R / dec):.4f}"/>'
                    for t in (0, .05, .1, .15, .2, .3, .4, .5, .6, .7, .8, .9, 1))
    t1, t2 = math.asin(thr), math.pi - math.asin(thr)          # sin(角度×n) > thr の はば
    d = ''
    for k in range(n):
        a1, a2 = (t1 + 2 * math.pi * k) / n, (t2 + 2 * math.pi * k) / n
        d += (f'M0 0L{R * math.cos(a1):.2f} {R * math.sin(a1):.2f}A{R} {R} 0 0 1 {R * math.cos(a2):.2f} {R * math.sin(a2):.2f}Z')
    defs = f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="{R}">{stops}</radialGradient>'
    body = f'<g transform="translate({sx:g} {sy:g})"><g class="nyrr"><path d="{d}" fill="url(#{gid})"/></g></g>'
    return defs, body


def rays_css(sel='', tag=True):
    pre = f'{sel} ' if sel else ''
    css = (f'{pre}.nyrr{{transform-box:view-box;transform-origin:0 0;animation:nyRot {ROT_S}s linear infinite}}'
           '@keyframes nyRot{to{transform:rotate(360deg)}}'
           f'@media (prefers-reduced-motion:reduce){{{pre}.nyrr{{animation:none}}}}')
    return f'<style>{css}</style>' if tag else css


def rays_file(sun):
    """アプリのファイルの形（光だけ・<style>つき）"""
    defs, body = rays_svg_inner(sun)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">'
            f'<defs>{rays_css()}{defs}</defs>{body}</svg>')


def inline(blobs, sun, alt=ALT, p='nj', step=None):
    """(html, css)。blobs：bg・top → '/_blob/<id>'。p：id の頭（ページの中で ほかと ぶつからないように）。
       step：(step_blobs, step_run)（step_wall.load）があれば、馬が いつも ゆっくり足ぶみして 首を動かす：光より前の絵は 馬の所を すき通しにした top に かえて、
       その四角に コマのシートを重ねる（四角の中と外で 重ならないので、前の絵との上下は どちらでもよい）"""
    defs, body = rays_svg_inner(sun, gid=f'{p}nyG')
    top, hh, hc = blobs['top'], '', ''
    if step is not None:
        import step_wall
        top = step[0]['newyear']['top']
        hh, hc = step_wall.sprite('newyear', *step)
        alt = step_wall.alt_with(alt)
    html = (f'<div class="nyw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["bg"]}" alt="">'
            f'<svg class="nyr" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true"><defs>{defs}</defs>{body}</svg>'
            f'{hh}<img class="nyt" src="{top}" alt=""></div>')
    css = ('.nyw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.nyw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           '.nyw .nyr,.nyw .nyt{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + rays_css('.nyw', tag=False) + hc)
    return html, css


def judge_inline(fn, blobs, sun, step=None):
    """判定画面（Judge_NewYear.dc.html）の上の絵を「回る光」の形に書きかえる（<img class="bnr"> か、前に入れた <div class="nyw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, sun, step=step)
    page, n = re.subn(r'<div class="nyw" .*?<img class="nyt" [^>]*></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* お正月の壁紙：初日の出の光が右回り（newyear_wall.py） */\n{css}\n/* /お正月の壁紙 */\n'
    if '/* お正月の壁紙：' in page:
        page = re.sub(r'/\* お正月の壁紙：.*?/\* /お正月の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    out, sun = sys.argv[1], json.load(open(sys.argv[-1]))
    open(f'{out}/newyear_rays.svg', 'w').write(rays_file(sun))
    step = None
    if '--step' in sys.argv:                         # 馬の足ぶみ（step_blobs.json・step_run.json）
        import step_wall
        i = sys.argv.index('--step')
        step = step_wall.load(sys.argv[i + 1], sys.argv[i + 2])
    if '--judge' in sys.argv:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), sun, step=step)
