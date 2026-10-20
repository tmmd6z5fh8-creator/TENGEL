"""雪の壁紙の動き（まさちゃんの指定「常に雪が降っている」）：壁紙の絵（WebP）の上に重ねる、雪が降りつづける SVG。
   雪つぶ 40こ（白い丸・ふちは やわらかくぼかす・外がわに うすい水色）＋ 雪の結晶 6こ（判定画面のすみの結晶と同じ形・白に水色のふち・ゆっくり回る）。
   上から下へ（奥は 13〜16秒・手前は 6.5〜8秒）・風で少し右へ流れながら、ふわふわ左右にゆれる。
   奥は小さく・うすく・ゆっくり・小さくゆれる、手前は大きく・濃く・速く・大きくゆれる（奥・まん中・手前の3つの層。ゆれは層ごとに2組）。
   ページを開いたときから全体に散っている（負の遅れ）。結晶の形は <defs> に置いて <use> で使う。
   SVG の中の CSS アニメーション（<style>）なので、アプリの中のファイルなら <img> で壁紙の上に重ねても動く（背景はすき通し）。
   視差効果を減らす（prefers-reduced-motion）なら消える（壁紙の絵にも降る雪が描いてある）。
   claude.ai のキャンバスは、アップロードした SVG の <style> を消してしまうので、キャンバスの判定画面には じかに入れる（inline・動きの CSS はページの <style>）：
     python3 yuki.py <出力フォルダ>                               → yuki_fall.svg（ファイルの形・<style>つき・390×160・背景なし）
     python3 yuki.py <出力フォルダ> --judge <Judge_Snow.dc.html>  → ＋判定画面の上の絵を「絵＋降る雪」の形に書きかえる
     python3 yuki.py <出力フォルダ> --judge <Judge_Snow.dc.html> --step <step_blobs.json> <step_run.json>  → ＋馬が ときどき 前足を動かしたり 首を下げて 草を食べたりする（step_wall.py）"""
import sys, os, math, re, random

W, H = 390, 160
N_DOTS = 40
N_CRYS = 6
ALT = '雪の中で白い息をはいて立つ芦毛の競走馬（まだら模様・水色のマフラー・紺のゼッケン1）と、雪をかぶった木のイラスト（いつも雪が降っている）'
EDGE = '#8FB3D6'                       # 雪のふちの水色（判定画面のすみの結晶 #7FB2DD より少しうすい）
INLINE_IDS = ('ykC1', 'ykC2', 'ykG')
# 層：(ゆれの幅 px, 組ごとのゆれの秒)
LAYERS = ((3, (3.4, 4.1)), (6, (3.0, 3.6)), (10, (2.6, 3.2)))


def crystal(arm):
    """雪の結晶（6本の腕・腕ごとに枝2組）：まん中が 0,0。水色の太い線の上に白い細い線"""
    lines = []
    for k in range(6):
        a = math.radians(k * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        lines.append((0, 0, arm * ca, arm * sa))
        for r, L in ((.47, .27), (.74, .22)):
            px, py = arm * r * ca, arm * r * sa
            for s in (-1, 1):
                b = a + s * math.radians(45)
                lines.append((px, py, px + arm * L * math.cos(b), py + arm * L * math.sin(b)))
    d = ''.join(f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1, y1, x2, y2 in lines)
    return (f'<path d="{d}" stroke="{EDGE}" stroke-width="2.3"/><path d="{d}" stroke="#FFFFFF" stroke-width="1.1"/>'
            f'<circle r="{arm * .16:.1f}" fill="#FFFFFF" stroke="{EDGE}" stroke-width=".7"/>')


def flakes(seed=31):
    """雪1つずつの決まり。z：奥 0 → 手前 1・layer：0 奥／1 まん中／2 手前"""
    rnd = random.Random(seed)
    out = []
    n = N_DOTS + N_CRYS
    crys = set(rnd.sample(range(n // 3, n), N_CRYS))        # 結晶は まん中と手前の層だけ
    for i in range(n):
        z = rnd.random() if i not in crys else rnd.uniform(.4, 1)
        layer = 0 if z < .4 else 1 if z < .75 else 2
        d = 16 - 9.5 * z + rnd.uniform(-.6, .6)
        out.append(dict(x0=round(rnd.uniform(-24, 384), 1), d=round(d, 2), dl=round(-rnd.uniform(0, d), 2), z=z, layer=layer,
                        grp=rnd.randrange(2), kind='c' if i in crys else 'd',
                        r=round(1.1 + 3 * z + rnd.uniform(-.2, .2), 2), o=round(.65 + .35 * z, 2),
                        cs=1 if z < .7 else 2, spin=round(rnd.uniform(9, 15), 1), rev=rnd.random() < .5))
    # 結晶は かたまらないように：横は6つの場所に1つずつ（少しずらす）・落ちる途中の位置も 1/6 ずつずらす
    cs = [p for p in out if p['kind'] == 'c']
    slots = list(range(N_CRYS))
    rnd.shuffle(slots)
    for k, p in enumerate(cs):
        p['x0'] = round(-4 + slots[k] * (384 / N_CRYS) + rnd.uniform(0, 384 / N_CRYS - 24), 1)
        p['dl'] = round(-p['d'] * ((k + rnd.uniform(.1, .5)) / N_CRYS), 2)
    return out


def fall_css(sel='', kn='yk', tag=True):
    """雪の動き。sel：前につけるセレクタ（ページに入れるとき '.bnrw'）・kn：キーフレームの名前の頭"""
    pre = f'{sel} ' if sel else ''
    css = (f'{pre}.yky,{pre}.ykx,{pre}.ykr{{transform-box:view-box;transform-origin:0 0}}'
           f'{pre}.yky{{animation:{kn}Y 10s linear infinite}}'
           f'{pre}.ykx{{animation:{kn}S0 3s ease-in-out infinite alternate}}'
           f'{pre}.ykr{{animation:{kn}R 12s linear infinite}}{pre}.ykr.rv{{animation-direction:reverse}}'
           f'@keyframes {kn}Y{{from{{transform:translate(0,-14px)}}to{{transform:translate(12px,{H + 14}px)}}}}'
           f'@keyframes {kn}R{{to{{transform:rotate(360deg)}}}}')
    for li, (a, _) in enumerate(LAYERS):
        css += f'@keyframes {kn}S{li}{{from{{transform:translateX(-{a}px)}}to{{transform:translateX({a}px)}}}}'
    css += f'@media (prefers-reduced-motion:reduce){{{pre}.ykf{{display:none}}}}'
    return f'<style>{css}</style>' if tag else css


def fall_svg(kn='yk', css=True, cls=''):
    """雪が降る SVG（390×160・背景なし）。css：<style> を中に入れる（ファイルの形）"""
    defs = (f'<g id="ykC1" fill="none" stroke-linecap="round">{crystal(5.2)}</g><g id="ykC2" fill="none" stroke-linecap="round">{crystal(7.6)}</g>'
            # 雪つぶ：まん中は白・ふちに向かってぼける（外がわに うすい水色をのこして、白い雪原の上でも少し見える）
            '<radialGradient id="ykG"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".48" stop-color="#FFFFFF"/>'
            '<stop offset=".78" stop-color="#E4EEF8" stop-opacity=".75"/><stop offset="1" stop-color="#A9C2DC" stop-opacity="0"/></radialGradient>')
    fl = flakes()
    body = ''
    for li, (a, periods) in enumerate(LAYERS):            # 奥の層から順に（手前が上に重なる）
        for g, per in enumerate(periods):
            inner = ''
            for p in fl:
                if p['layer'] != li or p['grp'] != g:
                    continue
                tm = f'animation-duration:{p["d"]}s;animation-delay:{p["dl"]}s'
                if p['kind'] == 'd':
                    shape = f'<circle r="{p["r"]}" fill="url(#ykG)" opacity="{p["o"]}"/>'
                else:
                    shape = (f'<g class="ykr{" rv" if p["rev"] else ""}" style="animation-duration:{p["spin"]}s">'
                             f'<use href="#ykC{p["cs"]}" opacity="{p["o"]}"/></g>')
                inner += f'<g transform="translate({p["x0"]} 0)"><g class="yky" style="{tm}">{shape}</g></g>'
            # ゆれ：層ごとの幅（キーフレーム S{層}）・組ごとの秒・組ごとに出だしをずらす
            body += (f'<g class="ykx" style="animation-name:{kn}S{li};animation-duration:{per}s;animation-delay:{-per * (.3 + .4 * g):.2f}s">'
                     f'{inner}</g>')
    st = fall_css(kn=kn) if css else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{c} viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">'
            f'<defs>{st}{defs}</defs><g class="ykf">{body}</g></svg>')


def inline(blob, alt=ALT, p='sn', step=None):
    """ページにじかに入れる形：<div class="bnrw">（壁紙の絵の <img class="bnr"> ＋ 雪の <svg class="ykfall">）と、ページの <style> に入れる CSS。戻り値 (html, css)"""
    s = fall_svg(kn=f'{p}k', css=False, cls='ykfall')
    for i in INLINE_IDS:
        s = s.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'href="#{i}"', f'href="#{p}{i}"')
    s = s.replace(' xmlns="http://www.w3.org/2000/svg"', '')
    hh, hc = '', ''
    if step is not None:                             # 馬が ときどき 前足を動かしたり 草を食べたりする（step_wall.py・コマは flat/step_run.py・時間わりは step_plan.py）
        import step_wall
        hh, hc = step_wall.sprite('snow', *step)
        alt = step_wall.alt_with(alt)
    html = f'<div class="bnrw"><img class="bnr" src="{blob}" alt="{alt}">{hh}{s}</div>'
    css = (hc + '.bnrw{position:relative;flex:none;overflow:hidden}.bnrw .ykfall{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + fall_css('.bnrw', f'{p}k', tag=False))
    return html, css


def judge_inline(fn, step=None):
    """判定画面（Judge_Snow.dc.html）の上の絵を「絵＋降る雪」の形に書きかえる（<img class="bnr"> か、前に入れた <div class="bnrw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    m = re.search(r'<img class="bnr" src="(/_blob/[0-9a-f]{32})"', page)
    html, css = inline(m.group(1), step=step)
    page, n = re.subn(r'<div class="bnrw">.*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 雪の壁紙：雪が降る（yuki.py） */\n{css}\n/* /雪の壁紙 */\n'
    if '/* 雪の壁紙：' in page:
        page = re.sub(r'/\* 雪の壁紙：.*?/\* /雪の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/yuki_fall.svg', 'w').write(fall_svg())
    step = None
    if '--step' in sys.argv:                         # 馬の動き（step_blobs.json・step_run.json）
        import step_wall
        i = sys.argv.index('--step')
        step = step_wall.load(sys.argv[i + 1], sys.argv[i + 2])
    if '--judge' in sys.argv:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1], step=step)
