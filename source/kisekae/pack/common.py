"""壁紙パック（第4.92版・11枚）の 共通の 道具：絵（SVG）と 動き（CSS）を 作る 部品。
   上の絵は 390×160 の 舞台（#ksBnr .ksb）に、部品ごとの 絵（SVG の data URI か、馬の コマの シート＝WebP）を 重ねて、CSS の アニメーションで 動かす。
   ・絵の 中の id（グラデーションなど）は、判定タブの 壁紙と 選ぶ画面の 動く見本で 同じ id が 2つに なって 消える ことが ある → 絵は <img>／背景の data URI
     （1まいずつ 別の 書類＝id が ぶつからない）。ページに じかに 置く <svg> には id を 使わない
   ・動きは CSS だけ（アプリの 光の 点めつの テストが Web Animations で 止めて 1/60秒ずつ 進める）。ときどきの 動きは 長い 1回りの 中の 区間で
   ・「視差効果を減らす」（と 設定の 控えめ）は 止まった 絵（<img class="bnr">）だけ（@media の 中身は build_kisekae が .calm にも 効かせる）
   形・絵は すべて 一から 作った オリジナル"""
import math
import random
from urllib.parse import quote

W, H = 390, 160


def f(x, n=2):
    """数を 短く（1.50 → 1.5・2.00 → 2）"""
    s = f'{x:.{n}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def durl(svg):
    """SVG の 文字列 → data URI（属性の 中に 置ける ように " は ' に）"""
    s = ' '.join(svg.split()).replace('"', "'")
    return 'data:image/svg+xml,' + quote(s, safe=" =:/;,.'()-_!*~")


def curi(svg):
    """CSS の url("…") に 入れる 形"""
    return 'url("' + durl(svg) + '")'


def tile(w, h, body, vb=None):
    """背景の もよう（くり返す 小さな 絵）"""
    vb = vb or f'0 0 {f(w)} {f(h)}'
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{f(w)}' height='{f(h)}' viewBox='{vb}'>{body}</svg>"


def fly_burst(code, kinds, n, seed, spread=300, dist=(85, 170), up=-30, sizes=None):
    """押した 瞬間に まん中から ふん水の ように はじけて、回りながら 落ちる かけら（push_events.fly_burst と 同じ 形）"""
    R = random.Random(seed)
    sizes = sizes or {}
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * spread + R.uniform(-8, 8))
        d = R.uniform(*dist)
        x, y = math.cos(a) * d * 1.25, math.sin(a) * d * .9 + up
        k = kinds[i % len(kinds)]
        z = R.uniform(*sizes.get(k, (12, 18)))
        r = R.choice((-1, 1)) * R.uniform(120, 360)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{R.uniform(0, .12):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips {code}" aria-hidden="true">{out}</div>'


def fly_css(code, ring, pieces):
    """はじける かけらの CSS（push_events.fly_css と 同じ 形。pieces：{クラス: 'background:…'}）"""
    css = (f'.clips.{code}{{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}}\n'
           f'.clips.{code} i{{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);'
           f'animation:{code}Fly 1.5s cubic-bezier(.2,.6,.4,1) calc(var(--d) + .1s) both;background:center/contain no-repeat}}\n')
    for k, bg in pieces.items():
        css += f'.clips.{code} .{k}{{{bg}}}\n'
    css += (f'.clips.{code} .ring{{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid {ring};box-shadow:0 0 16px {ring};'
            f'animation:{code}Ring .8s ease-out .1s forwards}}\n'
            f'@keyframes {code}Fly{{0%{{opacity:0;transform:translate(0,0) rotate(0) scale(.35)}}8%{{opacity:1}}45%{{opacity:1;transform:translate(calc(var(--x) * .8),var(--y)) rotate(calc(var(--r) * .45)) scale(1)}}'
            f'100%{{opacity:0;transform:translate(var(--x),calc(var(--y) + 170px)) rotate(var(--r)) scale(.9)}}}}\n'
            f'@keyframes {code}Ring{{0%{{opacity:.95;transform:scale(.3)}}100%{{opacity:0;transform:scale(2.2)}}}}\n')
    return css


def piece(svg):
    """はじける かけらの 絵（background-image）"""
    return f'background-image:url("{durl(svg)}")'


def doc(w, h, body, vb=None, defs=''):
    """1まいの SVG（xmlns つき）。vb：viewBox（なければ 0 0 w h）"""
    vb = vb or f'0 0 {f(w)} {f(h)}'
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{vb}' width='{f(w)}' height='{f(h)}' preserveAspectRatio='none'>"
            + (f'<defs>{defs}</defs>' if defs else '') + body + '</svg>')


def P(pts, close=True):
    """点の ならび → path の d（直線）"""
    s = 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts)
    return s + (' Z' if close else '')


def smooth(pts, close=True, k=0.5):
    """点を なめらかに つなぐ path の d（Catmull-Rom → ベジェ）。k：まるみ（0.5 ＝ ふつう）"""
    n = len(pts)
    if n < 3:
        return P(pts, close)
    out = f'M{f(pts[0][0])} {f(pts[0][1])}'
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        out += f' C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}'
    return out + (' Z' if close else '')


def star_d(cx, cy, r, r2=None, n=5, rot=-90.0):
    r2 = r * 0.45 if r2 is None else r2
    pts = [(cx + math.cos(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2),
            cy + math.sin(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2)) for k in range(n * 2)]
    return P(pts)


def sparkle_d(cx, cy, r, k=0.22):
    """4つの とがりの キラッ"""
    q = r * k
    return (f'M{f(cx)} {f(cy - r)} Q{f(cx + q)} {f(cy - q)} {f(cx + r)} {f(cy)} Q{f(cx + q)} {f(cy + q)} {f(cx)} {f(cy + r)} '
            f'Q{f(cx - q)} {f(cy + q)} {f(cx - r)} {f(cy)} Q{f(cx - q)} {f(cy - q)} {f(cx)} {f(cy - r)} Z')


def heart_d(cx, cy, r):
    return (f'M{f(cx)} {f(cy + r * 0.95)} C{f(cx - r * 0.2)} {f(cy + r * 0.75)} {f(cx - r * 1.05)} {f(cy + r * 0.25)} {f(cx - r)} {f(cy - r * 0.25)} '
            f'C{f(cx - r * 0.95)} {f(cy - r * 0.85)} {f(cx - r * 0.2)} {f(cy - r * 0.95)} {f(cx)} {f(cy - r * 0.42)} '
            f'C{f(cx + r * 0.2)} {f(cy - r * 0.95)} {f(cx + r * 0.95)} {f(cy - r * 0.85)} {f(cx + r)} {f(cy - r * 0.25)} '
            f'C{f(cx + r * 1.05)} {f(cy + r * 0.25)} {f(cx + r * 0.2)} {f(cy + r * 0.75)} {f(cx)} {f(cy + r * 0.95)} Z')


def hexrgb(c):
    c = c.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """色 a と b を t（0＝a・1＝b）で まぜる"""
    ra, rb = hexrgb(a), hexrgb(b)
    return '#%02X%02X%02X' % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def rgba(c, al):
    r, g, b = hexrgb(c)
    return f'rgba({r},{g},{b},{f(al)})'


def kf(name, stops):
    """@keyframes：stops＝[(%, '宣言')…]"""
    return f'@keyframes {name}{{' + ''.join(f'{f(p, 3)}%{{{d}}}' for p, d in stops) + '}'


def img(cls, svg, extra=''):
    """絵の 部品（<img>）。場所と 大きさは CSS の クラスで"""
    return f'<img class="{cls}" src="{durl(svg)}" alt=""{extra}>'


def box(cls, x, y, w, h, more=''):
    """部品の 置き場の CSS（左上・大きさ）"""
    return f'{cls}{{position:absolute;left:{f(x)}px;top:{f(y)}px;width:{f(w)}px;height:{f(h)}px;{more}}}'


def flow_layer(cls, uri, y, h, w, sec, direction=-1, more=''):
    """横に くり返す 帯（w：1まいの はば）。右から 左へ（direction=-1）流れる。uri：絵（data URI か /_blob/…）"""
    left = 0 if direction < 0 else -w
    return (f'{cls}{{position:absolute;left:{f(left)}px;top:{f(y)}px;width:{f(2 * w + 2)}px;height:{f(h)}px;background:url("{uri}") 0 0/{f(w)}px {f(h)}px repeat-x;'
            f'will-change:transform;animation:{{KF}} {f(sec, 3)}s linear infinite;{more}}}'), (direction * w)


def flow_css(cls, kfname, uri, y, h, w, sec, direction=-1, more=''):
    """flow_layer の CSS と @keyframes（名前 kfname）"""
    css, dx = flow_layer(cls, uri, y, h, w, sec, direction, more)
    return css.replace('{KF}', kfname) + kf(kfname, [(0, 'transform:translateX(0)'), (100, f'transform:translateX({f(dx)}px)')])


def sheet_css(cls, blob, meta, sec, scale=0.5, delay=0.0, more='', inner_more=''):
    """馬の コマの シート（横に n コマ）を steps で めくる。meta：frames・cell（2倍の 画素）・at（2倍の 画素）。scale：絵の 画素 → CSS px"""
    n, (cw, ch), (ax, ay) = meta['frames'], meta['cell'], meta['at']
    w, h = cw * scale, ch * scale
    name = cls.replace('.', '').replace(' ', '') + 'R'
    return (f'{cls}{{position:absolute;left:{f(ax * scale)}px;top:{f(ay * scale)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden;{more}}}'
            f'{cls}>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({blob}) 0 0/{f(n * w)}px {f(h)}px no-repeat;'
            f'animation:{name} {f(sec, 3)}s steps({n}) {f(-delay, 3)}s infinite;{inner_more}}}'
            + kf(name, [(100, f'transform:translateX({f(-n * w)}px)')]))


def strips(cls, uri, w, h, n, amp, sec, skew=0.0, phase=1.0, grow=True):
    """旗・布の なびき：絵を たて n 本の 帯に 切って、帯ごとに ずらして 上下に ゆらす（波が 先へ 進む）。
       grow：根もと（左）ほど ゆれを 小さく。返り値：(html, css)。cls の 中に 置く"""
    sw = w / n
    html = f'<i class="{cls[1:]}">' + ''.join(f'<b style="left:{f(i * sw)}px;background-position:{f(-i * sw)}px 0;animation-delay:{f(-sec * phase * i / n, 3)}s;--a:{f(amp * ((i + 1) / n if grow else 1), 2)}px"></b>' for i in range(n)) + '</i>'
    name = cls.replace('.', '').replace(' ', '') + 'W'
    css = (f'{cls}{{position:absolute;display:block;width:{f(w)}px;height:{f(h)}px}}'
           f'{cls}>b{{position:absolute;top:0;width:{f(sw + 0.6)}px;height:{f(h)}px;background:url("{uri}") 0 0/{f(w)}px {f(h)}px no-repeat;'
           f'animation:{name} {f(sec, 3)}s ease-in-out infinite;will-change:transform}}'
           + kf(name, [(0, 'transform:translateY(calc(var(--a) * -1))'), (50, 'transform:translateY(var(--a))'), (100, 'transform:translateY(calc(var(--a) * -1))')]))
    return html, css


def rnd(seed):
    return random.Random(seed)


def path_keys(pts, closed=True):
    """点の 道（[(x, y)…]）→ 道のりで そろえた (割合, x, y, 向き°)。closed：1周の 道"""
    seg = []
    pp = pts + ([pts[0]] if closed else [])
    L = 0.0
    for a, b in zip(pp, pp[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        seg.append((a, b, L, d))
        L += d
    return seg, L


def along(seg, L, s):
    """道のり s（0〜L）の 点と 向き°"""
    s = s % L if L else 0
    for a, b, l0, d in seg:
        if l0 <= s <= l0 + d or (a, b, l0, d) == seg[-1]:
            t = (s - l0) / d if d else 0
            return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    a, b, l0, d = seg[-1]
    return b[0], b[1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def reduced(sel_hide, sel_show='', extra=''):
    """「視差効果を減らす」：動く 部品を 消して（sel_hide）、止まった 絵（sel_show）を 出す"""
    return ('@media (prefers-reduced-motion:reduce){' + f'{sel_hide}{{display:none!important}}' + (f'{sel_show}{{visibility:visible!important}}' if sel_show else '') + extra + '}')
