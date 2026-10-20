"""桜の壁紙の動き（まさちゃんの指定「常に桜が降っている」）：壁紙の絵（WebP）の上に重ねる、花びらが降りつづける SVG。
   花びら28枚：上から下へ（6.5〜11秒）・風で少し右へ流れながら左右にゆれる・くるくる回りながら裏返る（細くなる）。
   奥の花びらは小さく・うすく・ゆっくり、手前は大きく・濃く・速く。ページを開いたときから全体に散っている（負の遅れ）。
   SVG の中の CSS アニメーション（<style>）なので、アプリの中のファイルなら <img> で壁紙の上に重ねても動く（背景はすき通し）。
   視差効果を減らす（prefers-reduced-motion）なら消える（壁紙の絵にも舞う花びらが描いてある）。
   claude.ai のキャンバスは、アップロードした SVG の <style> を消してしまうので、キャンバスの判定画面には じかに入れる（inline・動きの CSS はページの <style>）：
     python3 sakura.py <出力フォルダ>                                → sakura_fall.svg（ファイルの形・<style>つき・390×160・背景なし）
     python3 sakura.py <出力フォルダ> --judge <Judge_Sakura.dc.html>  → ＋判定画面の上の絵を「絵＋花びら」の形に書きかえる
     python3 sakura.py <出力フォルダ> --judge <Judge_Sakura.dc.html> --step <step_blobs.json> <step_run.json>  → ＋馬が ときどき 前足を動かしたり 首を下げて 草を食べたりする（step_wall.py）"""
import sys, os, math, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 390, 160
PETAL = 'M0 -6 C3 -6 5 -2 4 2 C3 5 1 6 0 4 C-1 6 -3 5 -4 2 C-5 -2 -3 -6 0 -6 Z'    # 花びら（判定画面の背景の花びらと同じ形。先にくぼみ）
N_PETALS = 28
ALT = '満開の桜の下に立つ白い競走馬（すらりとした足・桜色のたてがみ・耳もとの桜の花かざり・桜色のゼッケン1）のイラスト（いつも桜の花びらが降っている）'
INLINE_IDS = ('skA', 'skB', 'skC')


def petals(seed=17):
    """花びら1枚ずつの決まり：(x0, 流れる幅, 落ちる秒, 遅れ, ゆれ幅, ゆれ回数, 回る秒, 回る向き, 大きさ, 色, こさ)"""
    rnd = random.Random(seed)
    out = []
    for i in range(N_PETALS):
        z = i / (N_PETALS - 1)                       # 0＝奥 … 1＝手前
        z = rnd.uniform(max(0, z - .15), min(1, z + .15))
        d = 11 - 4.5 * z + rnd.uniform(-.6, .6)      # 奥ほどゆっくり
        out.append(dict(x0=rnd.uniform(-60, 370), dx=rnd.uniform(30, 85), d=round(d, 2), dl=round(-rnd.uniform(0, d), 2),
                        a=round(rnd.uniform(5, 12) * (.6 + .4 * z), 1), n=rnd.choice((2, 3, 3, 4)), tw=round(rnd.uniform(3.2, 6.5), 2),
                        rev=rnd.random() < .5, s=round(.58 + .62 * z + rnd.uniform(-.05, .05), 2),
                        g=('skC', 'skB', 'skA')[min(2, int(z * 3))], o=round(.62 + .38 * z, 2)))
    return out


def fall_css(sel='', kn='sk', tag=True):
    """花びらの動き。sel：前につけるセレクタ（ページに入れるとき '.bnrw'）・kn：キーフレームの名前の頭"""
    pre = f'{sel} ' if sel else ''
    css = (f'{pre}.sky,{pre}.skx,{pre}.skt{{transform-box:view-box;transform-origin:0 0}}'
           f'{pre}.sky{{animation:{kn}Y 8s linear infinite}}'
           f'{pre}.skt{{animation:{kn}Tw 5s linear infinite}}{pre}.skt.rv{{animation-direction:reverse}}'
           f'@keyframes {kn}Y{{from{{transform:translate(0,-16px)}}to{{transform:translate(0,{H + 16}px)}}}}'
           # くるくる回りながら、2回裏返る（横に細くなる）
           f'@keyframes {kn}Tw{{0%{{transform:rotate(0deg) scale(1,1)}}25%{{transform:rotate(90deg) scale(.28,1)}}50%{{transform:rotate(180deg) scale(1,1)}}'
           f'75%{{transform:rotate(270deg) scale(.28,1)}}100%{{transform:rotate(360deg) scale(1,1)}}}}')
    for i, p in enumerate(petals()):
        # 横：風で右へ流れる（dx）＋ 左右にゆれる（a・n回）。ゆれのいちばん大きい所だけキーフレーム（あいだは ease-in-out）
        n, kf = p['n'], [f'0%{{transform:translate({p["x0"]:.1f}px,0)}}']
        for j in range(2 * n):
            t = (2 * j + 1) / (4 * n)
            x = p['x0'] + p['dx'] * t + p['a'] * (1 if j % 2 == 0 else -1)
            kf.append(f'{100 * t:.2f}%{{transform:translate({x:.1f}px,0)}}')
        kf.append(f'100%{{transform:translate({p["x0"] + p["dx"]:.1f}px,0)}}')
        css += f'@keyframes {kn}X{i}{{{"".join(kf)}}}'
    css += f'@media (prefers-reduced-motion:reduce){{{pre}.skf{{display:none}}}}'
    return f'<style>{css}</style>' if tag else css


def fall_svg(kn='sk', css=True, cls=''):
    """花びらが降る SVG（390×160・背景なし）。css：<style> を中に入れる（ファイルの形）"""
    defs = ('<linearGradient id="skA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE6EE"/><stop offset="1" stop-color="#EE7BA5"/></linearGradient>'
            '<linearGradient id="skB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0F5"/><stop offset="1" stop-color="#F49CBC"/></linearGradient>'
            '<linearGradient id="skC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF7FA"/><stop offset="1" stop-color="#F7BCD0"/></linearGradient>')
    body = ''
    for i, p in enumerate(petals()):
        tm = f'animation-duration:{p["d"]}s;animation-delay:{p["dl"]}s'
        body += (f'<g class="sky" style="{tm}"><g class="skx" style="animation:{kn}X{i} {p["d"]}s ease-in-out {p["dl"]}s infinite">'
                 f'<g class="skt{" rv" if p["rev"] else ""}" style="animation-duration:{p["tw"]}s;animation-delay:{-p["tw"] * ((i * 7) % 10) / 10:.2f}s">'
                 f'<path d="{PETAL}" transform="scale({p["s"]})" fill="url(#{p["g"]})" stroke="#E2779C" stroke-width=".7" stroke-opacity=".55" opacity="{p["o"]}"/></g></g></g>')
    st = fall_css(kn=kn) if css else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{c} viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">'
            f'<defs>{st}{defs}</defs><g class="skf">{body}</g></svg>')


def inline(blob, alt=ALT, p='sb', step=None):
    """ページにじかに入れる形：<div class="bnrw">（壁紙の絵の <img class="bnr"> ＋ 花びらの <svg class="skfall">）と、ページの <style> に入れる CSS。戻り値 (html, css)"""
    s = fall_svg(kn=f'{p}k', css=False, cls='skfall')
    for i in INLINE_IDS:
        s = s.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'url(#{i})', f'url(#{p}{i})')
    s = s.replace(' xmlns="http://www.w3.org/2000/svg"', '')
    hh, hc = '', ''
    if step is not None:                             # 馬が ときどき 前足を動かしたり 草を食べたりする（step_wall.py・コマは flat/step_run.py・時間わりは step_plan.py）
        import step_wall
        hh, hc = step_wall.sprite('sakura', *step)
        alt = step_wall.alt_with(alt)
    html = f'<div class="bnrw"><img class="bnr" src="{blob}" alt="{alt}">{hh}{s}</div>'
    css = (hc + '.bnrw{position:relative;flex:none;overflow:hidden}.bnrw .skfall{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + fall_css('.bnrw', f'{p}k', tag=False))
    return html, css


def judge_inline(fn, step=None):
    """判定画面（Judge_Sakura.dc.html）の上の絵を「絵＋花びら」の形に書きかえる（<img class="bnr"> か、前に入れた <div class="bnrw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    m = re.search(r'<img class="bnr" src="(/_blob/[0-9a-f]{32})"', page)
    html, css = inline(m.group(1), step=step)
    page, n = re.subn(r'<div class="bnrw">.*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 桜の壁紙：花びらが降る（sakura.py） */\n{css}\n/* /桜の壁紙 */\n'
    if '/* 桜の壁紙：' in page:
        page = re.sub(r'/\* 桜の壁紙：.*?/\* /桜の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/sakura_fall.svg', 'w').write(fall_svg())
    step = None
    if '--step' in sys.argv:                         # 馬の動き（step_blobs.json・step_run.json）
        import step_wall
        i = sys.argv.index('--step')
        step = step_wall.load(sys.argv[i + 1], sys.argv[i + 2])
    if '--judge' in sys.argv:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1], step=step)
