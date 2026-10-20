"""紅葉の壁紙の動き（まさちゃんの指定「常に紅葉が降っている」）：壁紙の絵（WebP）の上に重ねる、もみじの葉が降りつづける SVG。
   もみじ18枚（判定画面のすみのもみじと同じ形・赤・朱・橙・山吹）：上から下へ（7〜12秒）・風で少し右へ流れながら大きく左右にゆれる。
   半分は ゆらゆら（左右にかたむきながら裏返る）、半分は くるくる回りながら裏返る。奥の葉は小さく・うすく・ゆっくり、手前は大きく・濃く・速く。
   ページを開いたときから全体に散っている（負の遅れ）。形は <defs> に1つ置いて <use> で何度も使う。
   SVG の中の CSS アニメーション（<style>）なので、アプリの中のファイルなら <img> で壁紙の上に重ねても動く（背景はすき通し）。
   視差効果を減らす（prefers-reduced-motion）なら消える（壁紙の絵にも舞う葉が描いてある）。
   claude.ai のキャンバスは、アップロードした SVG の <style> を消してしまうので、キャンバスの判定画面には じかに入れる（inline・動きの CSS はページの <style>）：
     python3 momiji.py <出力フォルダ>                                → momiji_fall.svg（ファイルの形・<style>つき・390×160・背景なし）
     python3 momiji.py <出力フォルダ> --judge <Judge_Autumn.dc.html>  → ＋判定画面の上の絵を「絵＋もみじ」の形に書きかえる
     python3 momiji.py <出力フォルダ> --judge <Judge_Autumn.dc.html> --step <step_blobs.json> <step_run.json>  → ＋馬が ときどき 前足を動かしたり 首を下げて 草を食べたりする（step_wall.py）"""
import sys, os, math, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from themes20 import maple_pts, P

W, H = 390, 160
N_LEAVES = 18
ALT = '紅葉の林を歩く栗毛の競走馬（亜麻色のたてがみ・もみじの髪かざり・赤いゼッケン1）のイラスト（いつも紅葉が降っている）'
COLORS = (('#E4572E', '#A33A16'), ('#C8341C', '#82200C'), ('#F08A24', '#B85A12'), ('#F2B634', '#B98418'))   # (面, ふちと柄)
INLINE_IDS = ('mjL',)


def leaf_d(n=96):
    """もみじの形（まん中が 0,0・葉の先まで約16）"""
    return P(maple_pts(1.05, n=n))


def leaves(seed=23):
    """葉1枚ずつの決まり"""
    rnd = random.Random(seed)
    out = []
    for i in range(N_LEAVES):
        z = i / (N_LEAVES - 1)
        z = rnd.uniform(max(0, z - .15), min(1, z + .15))
        d = 12 - 5 * z + rnd.uniform(-.6, .6)
        out.append(dict(x0=rnd.uniform(-60, 370), dx=rnd.uniform(20, 65), d=round(d, 2), dl=round(-rnd.uniform(0, d), 2),
                        a=round(rnd.uniform(10, 22) * (.6 + .4 * z), 1), n=rnd.choice((2, 2, 3)), tw=round(rnd.uniform(2.6, 4.6), 2),
                        kind='sp' if i % 2 else 'rk', rev=rnd.random() < .5, s=round(.36 + .3 * z + rnd.uniform(-.03, .03), 2),
                        c=COLORS[rnd.randrange(len(COLORS))], o=round(.7 + .3 * z, 2), r0=rnd.randrange(0, 360, 15)))
    return out


def fall_css(sel='', kn='mj', tag=True):
    """葉の動き。sel：前につけるセレクタ（ページに入れるとき '.bnrw'）・kn：キーフレームの名前の頭"""
    pre = f'{sel} ' if sel else ''
    css = (f'{pre}.mjy,{pre}.mjx,{pre}.mjt{{transform-box:view-box;transform-origin:0 0}}'
           f'{pre}.mjy{{animation:{kn}Y 9s linear infinite}}'
           f'{pre}.mjt{{animation:{kn}Rk 3.5s ease-in-out infinite}}{pre}.mjt.sp{{animation-name:{kn}Sp;animation-timing-function:linear}}{pre}.mjt.rv{{animation-direction:reverse}}'
           f'@keyframes {kn}Y{{from{{transform:translate(0,-22px)}}to{{transform:translate(0,{H + 22}px)}}}}'
           # ゆらゆら：左右にかたむきながら、2回裏返る（横に細くなる）
           f'@keyframes {kn}Rk{{0%{{transform:rotate(-34deg) scale(1,1)}}25%{{transform:rotate(4deg) scale(.45,1)}}50%{{transform:rotate(38deg) scale(1,1)}}'
           f'75%{{transform:rotate(4deg) scale(.45,1)}}100%{{transform:rotate(-34deg) scale(1,1)}}}}'
           # くるくる：回りながら、2回裏返る
           f'@keyframes {kn}Sp{{0%{{transform:rotate(0deg) scale(1,1)}}25%{{transform:rotate(90deg) scale(.35,1)}}50%{{transform:rotate(180deg) scale(1,1)}}'
           f'75%{{transform:rotate(270deg) scale(.35,1)}}100%{{transform:rotate(360deg) scale(1,1)}}}}')
    for i, p in enumerate(leaves()):
        n, kf = p['n'], [f'0%{{transform:translate({p["x0"]:.1f}px,0)}}']
        for j in range(2 * n):
            t = (2 * j + 1) / (4 * n)
            x = p['x0'] + p['dx'] * t + p['a'] * (1 if j % 2 == 0 else -1)
            kf.append(f'{100 * t:.2f}%{{transform:translate({x:.1f}px,0)}}')
        kf.append(f'100%{{transform:translate({p["x0"] + p["dx"]:.1f}px,0)}}')
        css += f'@keyframes {kn}X{i}{{{"".join(kf)}}}'
    css += f'@media (prefers-reduced-motion:reduce){{{pre}.mjf{{display:none}}}}'
    return f'<style>{css}</style>' if tag else css


def fall_svg(kn='mj', css=True, cls=''):
    """もみじが降る SVG（390×160・背景なし）。css：<style> を中に入れる（ファイルの形）"""
    defs = f'<g id="mjL"><path d="{leaf_d()}"/><path d="M1 3 Q2.5 11 0.5 19" fill="none" stroke-width="2" stroke-linecap="round"/></g>'
    body = ''
    for i, p in enumerate(leaves()):
        tm = f'animation-duration:{p["d"]}s;animation-delay:{p["dl"]}s'
        f_, s_ = p['c']
        body += (f'<g class="mjy" style="{tm}"><g class="mjx" style="animation:{kn}X{i} {p["d"]}s ease-in-out {p["dl"]}s infinite">'
                 f'<g class="mjt {p["kind"]}{" rv" if p["rev"] else ""}" style="animation-duration:{p["tw"]}s;animation-delay:{-p["tw"] * ((i * 7) % 10) / 10:.2f}s">'
                 f'<use href="#mjL" transform="rotate({p["r0"]}) scale({p["s"]})" fill="{f_}" stroke="{s_}" stroke-width="1.3" stroke-linejoin="round" opacity="{p["o"]}"/></g></g></g>')
    st = fall_css(kn=kn) if css else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{c} viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">'
            f'<defs>{st}{defs}</defs><g class="mjf">{body}</g></svg>')


def inline(blob, alt=ALT, p='ab', step=None):
    """ページにじかに入れる形：<div class="bnrw">（壁紙の絵の <img class="bnr"> ＋ もみじの <svg class="mjfall">）と、ページの <style> に入れる CSS。戻り値 (html, css)"""
    s = fall_svg(kn=f'{p}k', css=False, cls='mjfall')
    for i in INLINE_IDS:
        s = s.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'href="#{i}"', f'href="#{p}{i}"')
    s = s.replace(' xmlns="http://www.w3.org/2000/svg"', '')
    hh, hc = '', ''
    if step is not None:                             # 馬が ときどき 前足を動かしたり 草を食べたりする（step_wall.py・コマは flat/step_run.py・時間わりは step_plan.py）
        import step_wall
        hh, hc = step_wall.sprite('autumn', *step)
        alt = step_wall.alt_with(alt)
    html = f'<div class="bnrw"><img class="bnr" src="{blob}" alt="{alt}">{hh}{s}</div>'
    css = (hc + '.bnrw{position:relative;flex:none;overflow:hidden}.bnrw .mjfall{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + fall_css('.bnrw', f'{p}k', tag=False))
    return html, css


def judge_inline(fn, step=None):
    """判定画面（Judge_Autumn.dc.html）の上の絵を「絵＋もみじ」の形に書きかえる（<img class="bnr"> か、前に入れた <div class="bnrw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    m = re.search(r'<img class="bnr" src="(/_blob/[0-9a-f]{32})"', page)
    html, css = inline(m.group(1), step=step)
    page, n = re.subn(r'<div class="bnrw">.*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 紅葉の壁紙：もみじが降る（momiji.py） */\n{css}\n/* /紅葉の壁紙 */\n'
    if '/* 紅葉の壁紙：' in page:
        page = re.sub(r'/\* 紅葉の壁紙：.*?/\* /紅葉の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/momiji_fall.svg', 'w').write(fall_svg())
    step = None
    if '--step' in sys.argv:                         # 馬の動き（step_blobs.json・step_run.json）
        import step_wall
        i = sys.argv.index('--step')
        step = step_wall.load(sys.argv[i + 1], sys.argv[i + 2])
    if '--judge' in sys.argv:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1], step=step)
