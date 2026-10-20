"""行事の4テーマの 的中ボタン（まさちゃんの指定）：クリスマスツリーのPUSH（xm）・かぼちゃのPUSH（hw）・チョコのPUSH（vl）・マシュマロのPUSH（wd）
   gen_fx.py が つかう：push_svg(code, sfx) … ボタンの中の 面と まわりの飾り（sfx：押したあとの コピーで id が ぶつからないように）
                         burst(code)         … 押した瞬間に はじける かけら
                         CSS[code]           … そのボタンの CSS（形・色・動き・視差効果を減らす時）
   どれも 強く光らせない（白く光る 全体の光なし・きらめきは 小さな点だけ・1秒に3回まで）。形は すべて一から作ったオリジナル"""
import math
import random
from urllib.parse import quote

CODES = ('xm', 'hw', 'vl', 'wd')


def durl(svg):
    s = ' '.join(svg.split()).replace('"', "'")
    return 'data:image/svg+xml,' + quote(s, safe=" =:/;,.'()-_")


def star_d(cx, cy, r, r2=None, n=5, rot=-90.0):
    r2 = r * 0.45 if r2 is None else r2
    P = [(cx + math.cos(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2),
          cy + math.sin(math.radians(rot + k * 180 / n)) * (r if k % 2 == 0 else r2)) for k in range(n * 2)]
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in P) + ' Z'


def heart_d(cx, cy, r):
    return (f'M{cx:.1f} {cy + r * 0.95:.1f} C{cx - r * 0.2:.1f} {cy + r * 0.75:.1f} {cx - r * 1.05:.1f} {cy + r * 0.25:.1f} {cx - r:.1f} {cy - r * 0.25:.1f} '
            f'C{cx - r * 0.95:.1f} {cy - r * 0.85:.1f} {cx - r * 0.2:.1f} {cy - r * 0.95:.1f} {cx:.1f} {cy - r * 0.42:.1f} '
            f'C{cx + r * 0.2:.1f} {cy - r * 0.95:.1f} {cx + r * 0.95:.1f} {cy - r * 0.85:.1f} {cx + r:.1f} {cy - r * 0.25:.1f} '
            f'C{cx + r * 1.05:.1f} {cy + r * 0.25:.1f} {cx + r * 0.2:.1f} {cy + r * 0.75:.1f} {cx:.1f} {cy + r * 0.95:.1f} Z')


def sparkle_d(cx, cy, r):
    q = r * 0.22
    return (f'M{cx:.1f} {cy - r:.1f} Q{cx + q:.1f} {cy - q:.1f} {cx + r:.1f} {cy:.1f} Q{cx + q:.1f} {cy + q:.1f} {cx:.1f} {cy + r:.1f} '
            f'Q{cx - q:.1f} {cy + q:.1f} {cx - r:.1f} {cy:.1f} Q{cx - q:.1f} {cy - q:.1f} {cx:.1f} {cy - r:.1f} Z')


def fly_burst(code, kinds, n, seed, spread=300, dist=(85, 170), up=-30, sizes=None):
    """押した瞬間に まん中から ふん水のように はじけて、回りながら 落ちる かけら（kinds：クラスの名前の くり返し）"""
    rnd = random.Random(seed)
    sizes = sizes or {}
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * spread + rnd.uniform(-8, 8))
        d = rnd.uniform(*dist)
        x, y = math.cos(a) * d * 1.25, math.sin(a) * d * .9 + up
        k = kinds[i % len(kinds)]
        z = rnd.uniform(*sizes.get(k, (12, 18)))
        r = rnd.choice((-1, 1)) * rnd.uniform(120, 360)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .12):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips {code}" aria-hidden="true">{out}</div>'


def fly_css(code, ring, pieces):
    """はじける かけらの CSS（pieces：{クラス: 'background:…'}）"""
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


# ================================================================== クリスマスツリーのPUSH（xm）
def xm_face(sfx=''):
    """ボタン（200×100）が いちばん下の だん。上に 2だんと 金の星（-30〜230 × -96〜118）。雪・金の かざり・玉・あかり（またたく .xmlt）"""
    G, GD, GL = '#2F8A55', '#1E6A40', '#4CA86C'
    tiers = [(-66, -14, 52), (-38, 34, 84), (-6, 100, 116)]
    o = ''
    o += '<rect x="88" y="94" width="24" height="20" rx="3" fill="#6B4428"/><rect x="100" y="94" width="12" height="20" rx="2" fill="#53321C"/>'
    for k, (top, bot, hw) in enumerate(tiers):
        n = 5 + k * 2
        d = f'M100 {top} C{100 + hw * 0.3:.1f} {top + (bot - top) * 0.35:.1f} {100 + hw * 0.78:.1f} {bot - 14:.1f} {100 + hw:.1f} {bot - 2:.1f}'
        for i in range(n):
            x0 = 100 + hw - 2 * hw * i / n
            x1 = 100 + hw - 2 * hw * (i + 1) / n
            d += f' Q{(x0 + x1) / 2:.1f} {bot + 9:.1f} {x1:.1f} {bot - 2:.1f}'
        d += f' C{100 - hw * 0.78:.1f} {bot - 14:.1f} {100 - hw * 0.3:.1f} {top + (bot - top) * 0.35:.1f} 100 {top} Z'
        o += f'<path d="{d}" fill="{G}" stroke="#14492C" stroke-width="2.2" stroke-linejoin="round"/>'
        o += (f'<path d="M100 {top} C{100 + hw * 0.3:.1f} {top + (bot - top) * 0.35:.1f} {100 + hw * 0.78:.1f} {bot - 14:.1f} {100 + hw:.1f} {bot - 2:.1f} '
              f'Q{100 + hw * 0.6:.1f} {bot + 6:.1f} {100 + hw * 0.25:.1f} {bot - 1:.1f} C{100 + hw * 0.2:.1f} {top + (bot - top) * 0.5:.1f} {100 + hw * 0.08:.1f} {top + 18:.1f} 100 {top} Z" fill="{GD}" opacity=".5"/>')
        o += (f'<path d="M{100 - hw * 0.16:.1f} {top + 20:.1f} C{100 - hw * 0.3:.1f} {top + (bot - top) * 0.5:.1f} {100 - hw * 0.55:.1f} {bot - 18:.1f} {100 - hw * 0.72:.1f} {bot - 9:.1f}" '
              f'fill="none" stroke="{GL}" stroke-width="5" stroke-linecap="round" opacity=".75"/>')
        o += (f'<path d="M{100 - hw:.1f} {bot - 2:.1f} Q{100 - hw * 0.82:.1f} {bot + 7:.1f} {100 - hw * 0.6:.1f} {bot - 1:.1f} Q{100 - hw * 0.45:.1f} {bot + 6:.1f} {100 - hw * 0.3:.1f} {bot - 2:.1f} '
              f'Q{100 - hw * 0.5:.1f} {bot - 9:.1f} {100 - hw * 0.82:.1f} {bot - 8:.1f} Z" fill="#FFFFFF"/>')
    for y0, x0, x1, sag in ((-30, 62, 140, 9), (14, 36, 166, 12)):        # 金の かざり（玉の つらなり）
        for i in range(16):
            t = i / 15
            x = x0 + (x1 - x0) * t
            y = y0 + (x1 - x0) * 0.1 * (t - 0.5) + sag * math.sin(math.pi * t)
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="#F6CE5A"/>'
    for x, y, r, c in ((84, -46, 6, '#E23B3B'), (118, -30, 5.5, '#4A8FE0'), (70, 0, 6.5, '#F2C14E'), (138, 6, 6.5, '#E23B3B'), (104, -8, 5, '#C9D6E6'),
                       (18, 84, 7, '#E23B3B'), (182, 84, 7, '#4A8FE0'), (40, 40, 6.5, '#4A8FE0'), (160, 40, 6.5, '#F2C14E')):
        o += (f'<rect x="{x - 2.2:.1f}" y="{y - r - 3:.1f}" width="4.4" height="3.4" rx="1" fill="#C9A13E"/>'
              f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="#14492C" stroke-width="1.2"/><circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#FFFFFF" opacity=".8"/>')
    for j, (x, y) in enumerate(((96, -52), (122, -48), (78, -20), (128, -12), (56, 22), (148, 24), (92, 26), (30, 70), (170, 70))):
        o += f'<g class="xmlt" style="animation-delay:{-0.37 * j:.2f}s"><circle cx="{x}" cy="{y}" r="5.5" fill="#FFE9A0" opacity=".35"/><circle cx="{x}" cy="{y}" r="2.4" fill="#FFF6CC"/></g>'
    o += (f'<g class="xmst"><path d="{star_d(100, -74, 17)}" fill="#F6C445" stroke="#9A6A14" stroke-width="2" stroke-linejoin="round"/>'
          f'<path d="{star_d(98.6, -76, 8, 3.6)}" fill="#FFF3C2"/></g>')
    return (f'<i class="xmf" aria-hidden="true"><svg viewBox="-30 -96 260 214" width="260" height="214">{o}</svg></i>')


def xm_decor(sfx=''):
    """まわりに ふる 雪（.xmsn）と 小さな キラッ"""
    o = ''
    for j, (x, y, r) in enumerate(((-18, -60, 3.2), (226, -40, 3.6), (-30, 30, 2.6), (232, 60, 2.8), (10, -84, 2.4), (196, -88, 2.6))):
        o += f'<circle class="xmsn" cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" style="animation-delay:{-0.55 * j:.2f}s"/>'
    for j, (x, y, r) in enumerate(((-6, -20, 6), (214, -4, 5), (40, -78, 4.5))):
        o += f'<path class="xmtw" d="{sparkle_d(x, y, r)}" fill="#FFF3C2" style="animation-delay:{-0.8 * j:.2f}s"/>'
    return f'<i class="xmd" aria-hidden="true"><svg viewBox="-40 -100 280 230" width="280" height="230">{o}</svg></i>'


XM_PIECES = dict(
    st=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-12 -12 24 24\'><path d=\'" + star_d(0, 0, 11) + "\' fill=\'#F6C445\' stroke=\'#9A6A14\' stroke-width=\'1.4\'/></svg>")}")',
    rb=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-12 -14 24 26\'><rect x=\'-2.5\' y=\'-13\' width=\'5\' height=\'4\' rx=\'1\' fill=\'#C9A13E\'/><circle r=\'10\' fill=\'#E23B3B\' stroke=\'#7A1414\' stroke-width=\'1.4\'/><circle cx=\'-3.5\' cy=\'-3.5\' r=\'3\' fill=\'#FFFFFF\' opacity=\'.8\'/></svg>")}")',
    gb=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-12 -14 24 26\'><rect x=\'-2.5\' y=\'-13\' width=\'5\' height=\'4\' rx=\'1\' fill=\'#C9A13E\'/><circle r=\'10\' fill=\'#4A8FE0\' stroke=\'#1E4E8C\' stroke-width=\'1.4\'/><circle cx=\'-3.5\' cy=\'-3.5\' r=\'3\' fill=\'#FFFFFF\' opacity=\'.8\'/></svg>")}")',
    sf=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-12 -12 24 24\'><g stroke=\'#FFFFFF\' stroke-width=\'2.2\' stroke-linecap=\'round\'><path d=\'M0 -10V10M-8.7 -5L8.7 5M-8.7 5L8.7 -5\'/></g></svg>")}")',
)


def xm_burst():
    return fly_burst('xm', ['st', 'rb', 'sf', 'gb', 'st', 'sf'], 28, 25, sizes=dict(st=(16, 22), rb=(14, 19), gb=(14, 19), sf=(12, 17)))


XM_CSS = r'''
/* ---------- クリスマスの的中ボタン：クリスマスツリーのPUSH（まさちゃんの指定） ----------
   ボタンが まるごと クリスマスツリー：いちばん下の だん（200×100）に「PUSH」・上に 2だんと 金の星。だんの ふちに 雪・金の かざり・赤と青と金の玉・
   あかりが ゆっくり またたく（小さな点だけ）・星が ゆっくり ふくらむ。まわりに 雪が ふる・キラッ。上下の動きは的中と同じ。
   押すと ツリーが ちぢんで ふくらみ（強く光らせない）、金の星と 玉と 雪の結晶が はじけて 落ち、金の 光の輪が広がる */
.xm{--pushA:#2F8A55;--pushB:#14492C;--pushC:#4CA86C;--rim:#F6CE5A;--rimD:#14492C}
.push.xm{background:none;border-radius:0;box-shadow:none;filter:drop-shadow(0 10px 0 rgba(10,40,24,.55)) drop-shadow(0 20px 26px rgba(0,0,0,.45))}
.push.xm span{top:16px;font:800 36px/1 "Kaisei Tokumin",serif;letter-spacing:.06em;color:#FFF7E0;text-shadow:0 3px 0 #A8202A,0 0 10px rgba(255,236,170,.65)}
.push.xm::after{inset:-30px -26px -18px;border-radius:50% 50% 40% 40%;border-color:rgba(246,206,90,.9)}
.xm .xmf{position:absolute;left:-30px;top:-96px;width:260px;height:214px;pointer-events:none;font-style:normal}
.xm .xmf svg{display:block;width:260px;height:214px;overflow:visible}
.xm .xmd{position:absolute;left:-40px;top:-100px;width:280px;height:230px;pointer-events:none;z-index:3;font-style:normal}
.xm .xmd svg{display:block;width:280px;height:230px;overflow:visible}
.xm .xmlt{animation:xmLt 1.8s ease-in-out infinite}
@keyframes xmLt{0%,100%{opacity:.45}50%{opacity:1}}
.xm .xmst{transform-box:fill-box;transform-origin:50% 55%;animation:xmSt 2.4s ease-in-out infinite}
@keyframes xmSt{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
.xm .xmsn{animation:xmSn 3.3s linear infinite}
@keyframes xmSn{0%{opacity:0;transform:translateY(-10px)}15%{opacity:.95}85%{opacity:.95}100%{opacity:0;transform:translateY(44px)}}
.xm .xmtw{transform-box:fill-box;transform-origin:50% 50%;animation:xmTw 2.4s ease-in-out infinite}
@keyframes xmTw{0%,100%{opacity:.2;transform:scale(.5)}50%{opacity:1;transform:scale(1.1)}}
.pshadow.xm{width:230px}
.tap.xm{font-family:"Kaisei Tokumin",serif;font-weight:800;color:#FFE9A0;letter-spacing:.12em;text-shadow:0 2px 0 #14492C,0 0 10px rgba(255,220,120,.6)}
.pressed.xm{background:none;border-radius:0;box-shadow:none;animation-name:xmPress}
@keyframes xmPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.xm .xmlt,.xm .xmst,.xm .xmsn,.xm .xmtw{animation:none}.xm .xmsn,.clips.xm{display:none}}
''' + fly_css('xm', 'rgba(246,206,90,.9)', XM_PIECES)


# ================================================================== かぼちゃのPUSH（hw）
def hw_face(sfx=''):
    """ボタンが まるごと ジャック・オー・ランタン（-24〜224 × -40〜114）：オレンジの みぞ・緑のへたと つる・光る 三角の目（「PUSH」は 光る口）・中の光が ゆっくり ゆらぐ（.hwgl）"""
    g = f'hwG{sfx}'
    defs = (f'<defs><radialGradient id="{g}" cx=".5" cy=".55" r=".55"><stop offset="0" stop-color="#FFE36A" stop-opacity=".95"/>'
            '<stop offset=".6" stop-color="#FFB02E" stop-opacity=".5"/><stop offset="1" stop-color="#FF8A1F" stop-opacity="0"/></radialGradient></defs>')
    o = ''
    for cx, rx, c in ((34, 50, '#E8781A'), (166, 50, '#E8781A'), (64, 56, '#F28A1E'), (136, 56, '#F28A1E'), (100, 56, '#FFA640')):
        o += f'<ellipse cx="{cx}" cy="54" rx="{rx}" ry="56" fill="{c}" stroke="#8A3E08" stroke-width="2.2"/>'
    o += '<ellipse cx="100" cy="54" rx="40" ry="50" fill="#FFB65A" opacity=".45"/>'
    o += '<path d="M28 20 Q40 6 58 4" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity=".35"/>'
    o += ('<path d="M94 2 Q90 -20 104 -30 L112 -24 Q102 -14 106 2 Z" fill="#4E7A2A" stroke="#2E4A16" stroke-width="2" stroke-linejoin="round"/>'
          '<path d="M108 -18 Q128 -34 146 -22 Q130 -20 118 -10 Z" fill="#6AA03A" stroke="#2E4A16" stroke-width="1.6" stroke-linejoin="round"/>'
          '<path d="M90 -6 Q74 -20 80 -32 Q86 -40 78 -44" fill="none" stroke="#4E7A2A" stroke-width="2.4" stroke-linecap="round"/>')
    o += (f'<g class="hwgl"><ellipse cx="100" cy="58" rx="86" ry="44" fill="url(#{g})" opacity=".55"/>'
          '<path d="M46 34 L62 10 L78 34 Z M122 34 L138 10 L154 34 Z" fill="#FFE36A" stroke="#8A3E08" stroke-width="2" stroke-linejoin="round"/>'
          '<path d="M94 40 L100 31 L106 40 Z" fill="#FFE36A" stroke="#8A3E08" stroke-width="1.6" stroke-linejoin="round"/></g>')
    return f'<i class="hwf" aria-hidden="true"><svg viewBox="-24 -48 248 166" width="248" height="166">{defs}{o}</svg></i>'


def hw_decor(sfx=''):
    """まわりに こうもり（はばたく .hwbt）と あめ（ゆれる .hwcd）"""
    bat = ('M0,-4 Q-6,-10 -10,-6 Q-18,-16 -30,-14 Q-26,-8 -28,-2 Q-22,-4 -18,2 Q-14,-2 -10,4 Q-6,0 0,6 '
           'Q6,0 10,4 Q14,-2 18,2 Q22,-4 28,-2 Q26,-8 30,-14 Q18,-16 10,-6 Q6,-10 0,-4 Z')
    o = ''
    for j, (x, y, s) in enumerate(((-14, -30, .8), (214, -42, .9), (230, 30, .6))):
        o += (f'<g transform="translate({x} {y}) scale({s})"><g class="hwbt" style="animation-delay:{-0.23 * j:.2f}s">'
              f'<path d="{bat}" fill="#2A1840" stroke="#C9B6E8" stroke-width="1.2"/><circle cx="-2.4" cy="-3" r="1.4" fill="#FFD34A"/><circle cx="2.4" cy="-3" r="1.4" fill="#FFD34A"/></g></g>')
    for j, (x, y, c, a) in enumerate(((-26, 96, '#B05BD0', -20), (226, 100, '#3BB37A', 16))):
        o += (f'<g transform="translate({x} {y}) rotate({a})"><g class="hwcd" style="animation-delay:{-0.9 * j:.1f}s">'
              f'<path d="M-15 -6 L-9 0 L-15 6 Z M15 -6 L9 0 L15 6 Z" fill="{c}" stroke="#2A1840" stroke-width="1.2" stroke-linejoin="round"/>'
              f'<ellipse rx="10" ry="7.5" fill="{c}" stroke="#2A1840" stroke-width="1.4"/><path d="M-5 -5 L-1 5 M3 -5 L6 4" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".7"/></g></g>')
    return f'<i class="hwd" aria-hidden="true"><svg viewBox="-50 -70 300 200" width="300" height="200">{o}</svg></i>'


HW_BAT = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-32 -18 64 28'><path d='M0,-4 Q-6,-10 -10,-6 Q-18,-16 -30,-14 Q-26,-8 -28,-2 Q-22,-4 -18,2 Q-14,-2 -10,4 Q-6,0 0,6 "
          "Q6,0 10,4 Q14,-2 18,2 Q22,-4 28,-2 Q26,-8 30,-14 Q18,-16 10,-6 Q6,-10 0,-4 Z' fill='#2A1840' stroke='#C9B6E8' stroke-width='1.6'/></svg>")


def hw_candy(c):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-17 -9 34 18'><path d='M-16 -7 L-9 0 L-16 7 Z M16 -7 L9 0 L16 7 Z' fill='{c}' stroke='#2A1840' stroke-width='1.2'/>"
            f"<ellipse rx='10' ry='7.5' fill='{c}' stroke='#2A1840' stroke-width='1.4'/><path d='M-5 -5 L-1 5 M3 -5 L6 4' stroke='#FFFFFF' stroke-width='2' stroke-linecap='round' opacity='.7'/></svg>")


HW_PIECES = dict(
    bt=f'background-image:url("{durl(HW_BAT)}");height:calc(var(--z) * .5);top:calc(var(--z) * -.25)',
    c1=f'background-image:url("{durl(hw_candy("#B05BD0"))}");height:calc(var(--z) * .55);top:calc(var(--z) * -.27)',
    c2=f'background-image:url("{durl(hw_candy("#3BB37A"))}");height:calc(var(--z) * .55);top:calc(var(--z) * -.27)',
    pk=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-12 -14 24 25\'><path d=\'M-1 -9 Q-2 -13 2 -14 L3 -12 Q1 -11 1.6 -9 Z\' fill=\'#4E7A2A\'/><ellipse cx=\'-4\' cy=\'0\' rx=\'7\' ry=\'9\' fill=\'#E8781A\'/><ellipse cx=\'4\' cy=\'0\' rx=\'7\' ry=\'9\' fill=\'#E8781A\'/><ellipse rx=\'6\' ry=\'9.4\' fill=\'#FFA640\'/></svg>")}")',
    sp='border-radius:50%;background:radial-gradient(circle,#FFE36A 0 30%,#FF9A2E 60%,rgba(255,138,31,0) 72%)',
)


def hw_burst():
    return fly_burst('hw', ['c1', 'bt', 'pk', 'c2', 'sp', 'bt', 'c1', 'sp'], 28, 31,
                     sizes=dict(bt=(26, 34), c1=(24, 30), c2=(24, 30), pk=(16, 22), sp=(8, 12)))


HW_CSS = r'''
/* ---------- ハロウィンの的中ボタン：かぼちゃのPUSH（まさちゃんの指定） ----------
   ボタンが まるごと ジャック・オー・ランタン：オレンジの みぞ・緑の へたと 葉と つる・光る 三角の目と鼻・「PUSH」は 光る口（黄色い字に オレンジの光）。
   中の光が ゆっくり ゆらぐ（強く光らせない）。まわりに こうもりが はばたき・あめが ゆれる。上下の動きは的中と同じ。
   押すと かぼちゃが ちぢんで ふくらみ、あめと こうもりと 小さな かぼちゃと 光の粒が はじけて 落ち、オレンジの 光の輪が広がる */
.hw{--pushA:#F28A1E;--pushB:#8A3E08;--pushC:#FFB65A;--rim:#FFB65A;--rimD:#8A3E08}
.push.hw{background:none;border-radius:50%;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(90,36,4,.55)) drop-shadow(0 20px 26px rgba(0,0,0,.5))}
.push.hw span{top:22px;font:400 38px/1 "Reggae One",sans-serif;letter-spacing:.06em;color:#FFE36A;text-shadow:0 0 6px #FF9A2E,0 0 14px rgba(255,154,46,.9),0 2px 0 #8A3E08}
.push.hw::after{inset:-26px -30px -18px;border-radius:50%;border-color:rgba(255,166,64,.9)}
.hw .hwf{position:absolute;left:-24px;top:-48px;width:248px;height:166px;pointer-events:none;font-style:normal}
.hw .hwf svg{display:block;width:248px;height:166px;overflow:visible}
.hw .hwd{position:absolute;left:-50px;top:-70px;width:300px;height:200px;pointer-events:none;z-index:3;font-style:normal}
.hw .hwd svg{display:block;width:300px;height:200px;overflow:visible}
.hw .hwgl{animation:hwGl 2.6s ease-in-out infinite}
@keyframes hwGl{0%,100%{opacity:.82}50%{opacity:1}}
.hw .hwbt{transform-box:fill-box;transform-origin:50% 50%;animation:hwBt .5s ease-in-out infinite alternate}
@keyframes hwBt{from{transform:scale(1,1) translateY(0)}to{transform:scale(1,.55) translateY(-3px)}}
.hw .hwcd{transform-box:fill-box;transform-origin:50% 50%;animation:hwCd 2.2s ease-in-out infinite alternate}
@keyframes hwCd{from{transform:rotate(-10deg) translateY(-2px)}to{transform:rotate(10deg) translateY(3px)}}
.pshadow.hw{width:230px}
.tap.hw{font-family:"Reggae One",sans-serif;font-weight:400;color:#FFB65A;letter-spacing:.12em;text-shadow:0 2px 0 #3A1A0A,0 0 10px rgba(255,154,46,.6)}
.pressed.hw{background:none;border-radius:50%;box-shadow:none;animation-name:hwPress}
@keyframes hwPress{0%{transform:scale(1)}22%{transform:scale(.9,.94)}45%{transform:scale(1.08,1.04)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.hw .hwgl,.hw .hwbt,.hw .hwcd{animation:none}.clips.hw{display:none}}
''' + fly_css('hw', 'rgba(255,154,46,.9)', HW_PIECES)


# ================================================================== チョコのPUSH（vl）
def vl_face(sfx=''):
    """ボタン（200×100）が 板チョコ：つやの ある こげ茶・4×2の 四角の くぼみ・右はしに ピンクの 包み紙（金の ふち・白い ハート）・
       左上から ピンクの すじ（とろっと）・ときどき つやが すっと通る（.vlsh）"""
    c, s, g = f'vlC{sfx}', f'vlS{sfx}', f'vlG{sfx}'
    defs = (f'<defs><clipPath id="{c}"><rect width="200" height="100" rx="12"/></clipPath>'
            f'<linearGradient id="{s}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A5232"/><stop offset=".5" stop-color="#6B3A22"/><stop offset="1" stop-color="#4A2614"/></linearGradient>'
            f'<linearGradient id="{g}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".45"/>'
            '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    o = f'<rect width="200" height="100" fill="url(#{s})"/>'
    for i in range(4):
        for j in range(2):
            x, y = 8 + i * 37, 8 + j * 44
            o += (f'<rect x="{x}" y="{y}" width="33" height="40" rx="5" fill="#5A2E1A"/>'
                  f'<rect x="{x + 2}" y="{y + 2}" width="29" height="36" rx="4" fill="#7A4430"/>'
                  f'<path d="M{x + 4} {y + 33} V{y + 6} Q{x + 4} {y + 4} {x + 6} {y + 4} H{x + 27}" fill="none" stroke="#A86E4C" stroke-width="2" stroke-linecap="round" opacity=".7"/>')
    o += '<path d="M2 18 Q20 6 38 18 T76 18 T112 14" fill="none" stroke="#F7A8C0" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
    o += '<path d="M2 30 Q16 22 30 30 T60 28" fill="none" stroke="#F7A8C0" stroke-width="3" stroke-linecap="round" opacity=".8"/>'
    o += ('<rect x="150" y="-4" width="56" height="108" fill="#E8547C"/><rect x="146" y="-4" width="7" height="108" fill="#F2C14E"/>'
          '<rect x="153" y="-4" width="53" height="12" fill="#C7375F" opacity=".5"/>'
          f'<path d="{heart_d(178, 52, 12)}" fill="#FFFFFF"/>'
          '<path d="M160 86 L196 86" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="3 4" opacity=".7"/>')
    o += f'<g class="vlsh"><rect x="-70" y="-10" width="36" height="130" fill="url(#{g})" transform="rotate(18)"/></g>'
    return (f'<i class="vlf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{c})">{o}</g></svg></i>')


def vl_decor(sfx=''):
    """まわりに ハートのチョコと トリュフ（ふわふわ .vlbo）・ピンクの リボン"""
    o = ''
    for j, (x, y, r, a) in enumerate(((-16, 96, 13, -14), (214, -14, 12, 12), (-20, -8, 10, -8))):
        o += (f'<g transform="translate({x} {y}) rotate({a})"><g class="vlbo" style="animation-delay:{-0.8 * j:.1f}s">'
              f'<path d="{heart_d(0, 0, r)}" fill="#5A2E1C" stroke="#2E160C" stroke-width="1.4"/><path d="{heart_d(-1, -1.4, r * 0.82)}" fill="#7A4430"/>'
              f'<path d="M{-r * 0.6:.1f} {-r * 0.1:.1f} Q{-r * 0.2:.1f} {-r * 0.4:.1f} {r * 0.2:.1f} {-r * 0.1:.1f} T{r * 0.7:.1f} {-r * 0.2:.1f}" fill="none" stroke="#F7A8C0" stroke-width="2" stroke-linecap="round"/></g></g>')
    for j, (x, y) in enumerate(((222, 92), (232, 58))):
        o += (f'<g transform="translate({x} {y})"><g class="vlbo" style="animation-delay:{-1.3 - 0.6 * j:.1f}s">'
              '<circle r="10" fill="#5A3020" stroke="#2E160C" stroke-width="1.4"/><path d="M-7 -3 Q-3 -8 0 -3 Q3 2 7 -3" fill="none" stroke="#F6E6CF" stroke-width="2.2" stroke-linecap="round"/>'
              '<circle cx="-3.5" cy="-5" r="1.8" fill="#FFFFFF" opacity=".6"/></g></g>')
    o += ('<path d="M8 -4 Q-6 -20 -10 -6 Q-4 2 8 -4 Z M8 -4 Q22 -20 26 -6 Q20 2 8 -4 Z" fill="#E8547C" stroke="#9E2240" stroke-width="1.4"/>'
          '<path d="M8 -4 L2 12 L6 10 Z M8 -4 L14 12 L10 10 Z" fill="#C7375F"/><circle cx="8" cy="-4" r="3.4" fill="#C7375F"/>')
    return f'<i class="vld" aria-hidden="true"><svg viewBox="-40 -40 280 180" width="280" height="180">{o}</svg></i>'


VL_PIECES = dict(
    sq=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 20 22\'><rect width=\'20\' height=\'22\' rx=\'3\' fill=\'#4E2816\'/><rect x=\'1.5\' y=\'1.5\' width=\'17\' height=\'19\' rx=\'2.4\' fill=\'#7A4430\'/><path d=\'M3.5 17V4H16\' fill=\'none\' stroke=\'#A86E4C\' stroke-width=\'1.6\' stroke-linecap=\'round\'/></svg>")}");height:calc(var(--z) * 1.1)',
    ht=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-11 -11 22 22\'><path d=\'" + heart_d(0, 0, 10) + "\' fill=\'#E8547C\' stroke=\'#9E2240\' stroke-width=\'1.2\'/></svg>")}")',
    hc=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-11 -11 22 22\'><path d=\'" + heart_d(0, 0, 10) + "\' fill=\'#5A2E1C\' stroke=\'#2E160C\' stroke-width=\'1.2\'/><path d=\'M-5 -1 Q-2 -4 1 -1 T6 -2\' fill=\'none\' stroke=\'#F7A8C0\' stroke-width=\'1.8\' stroke-linecap=\'round\'/></svg>")}")',
    tr=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-11 -11 22 22\'><circle r=\'10\' fill=\'#5A3020\' stroke=\'#2E160C\' stroke-width=\'1.2\'/><path d=\'M-7 -3 Q-3 -8 0 -3 Q3 2 7 -3\' fill=\'none\' stroke=\'#F6E6CF\' stroke-width=\'2.2\' stroke-linecap=\'round\'/></svg>")}")',
    sp='border-radius:2px;background:linear-gradient(90deg,#F7A8C0,#FFFFFF)',
)


def vl_burst():
    return fly_burst('vl', ['sq', 'ht', 'tr', 'hc', 'sp', 'sq', 'ht', 'sp'], 28, 14,
                     sizes=dict(sq=(14, 18), ht=(14, 20), hc=(16, 21), tr=(13, 17), sp=(5, 8)))


VL_CSS = r'''
/* ---------- バレンタインの的中ボタン：チョコのPUSH（まさちゃんの指定） ----------
   ボタンが まるごと 板チョコ：つやの ある こげ茶・4×2の 四角の くぼみ・左上から ピンクの すじ・右はしに ピンクの 包み紙（金の ふち・白い ハート）。
   「PUSH」は チョコに うかした字（ミルクチョコの色・上に 光・下に かげ）。ときどき つやが すっと通る。まわりに ハートのチョコと トリュフが ふわふわ・ピンクの リボン。
   上下の動きは的中と同じ。押すと チョコが ちぢんで ふくらみ（強く光らせない）、チョコの かけら・ハート・トリュフ・ピンクの つぶが はじけて 落ち、ピンクの 光の輪が広がる */
.vl{--pushA:#6B3A22;--pushB:#2E160C;--pushC:#8A5232;--rim:#F7A8C0;--rimD:#5A2E1C}
.push.vl{--pr:12px;background:#6B3A22;box-shadow:inset 0 2px 0 rgba(255,255,255,.25),0 0 0 4px #F7A8C0,0 0 0 6px #5A2E1C,0 7px 0 6px #3E1F10,0 22px 30px rgba(40,10,0,.45)}
.push.vl span{font:400 42px/1 "Yusei Magic",sans-serif;letter-spacing:.06em;color:#A8714E;text-shadow:0 -1.5px 0 #D9A27C,0 2px 0 #2E160C,0 3px 2px rgba(0,0,0,.35);margin-right:44px}
.push.vl::after{border-radius:22px;border-color:rgba(247,168,192,.95)}
.vl .vlf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:12px;overflow:hidden;pointer-events:none;font-style:normal}
.vl .vlf svg{display:block;width:200px;height:100px}
.vl .vld{position:absolute;left:-40px;top:-40px;width:280px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.vl .vld svg{display:block;width:280px;height:180px;overflow:visible}
.vl .vlsh{transform-box:view-box;transform-origin:0 0;animation:vlShine 4.8s ease-in-out infinite}
@keyframes vlShine{0%,58%{transform:translateX(0)}88%,100%{transform:translateX(300px)}}
.vl .vlbo{animation:vlBob 2.6s ease-in-out infinite alternate}
@keyframes vlBob{from{transform:translate(0,-3px) rotate(-6deg)}to{transform:translate(0,3px) rotate(6deg)}}
.tap.vl{font-family:"Yusei Magic",sans-serif;font-weight:400;color:#FFD3E1;letter-spacing:.12em;text-shadow:0 2px 0 #5A2E1C,0 0 10px rgba(247,168,192,.7)}
.pressed.vl{border-radius:12px;background:#6B3A22;box-shadow:0 0 0 4px #F7A8C0,0 0 0 6px #5A2E1C,0 7px 0 6px #3E1F10;animation-name:vlPress}
@keyframes vlPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.vl .vlsh,.vl .vlbo{animation:none}.vl .vlsh,.clips.vl{display:none}}
''' + fly_css('vl', 'rgba(247,168,192,.9)', VL_PIECES)


# ================================================================== マシュマロのPUSH（wd）
def wd_face(sfx=''):
    """ボタン（200×100）が ふわふわの マシュマロ：白い 面（下は うすい水色）・上に ふんわり光・こなを ふった 点・下に やわらかい かげ"""
    c, s = f'wdC{sfx}', f'wdS{sfx}'
    rnd = random.Random(7)
    defs = (f'<defs><clipPath id="{c}"><rect width="200" height="100" rx="42"/></clipPath>'
            f'<linearGradient id="{s}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#F7FAFD"/><stop offset="1" stop-color="#D4E6F6"/></linearGradient></defs>')
    o = f'<rect width="200" height="100" fill="url(#{s})"/>'
    o += '<ellipse cx="100" cy="18" rx="80" ry="16" fill="#FFFFFF"/>'
    o += '<ellipse cx="100" cy="96" rx="92" ry="16" fill="#BFD8EE" opacity=".55"/>'
    for i in range(26):
        o += f'<circle cx="{rnd.uniform(18, 182):.1f}" cy="{rnd.uniform(14, 86):.1f}" r="{rnd.uniform(.8, 1.6):.1f}" fill="#BFD8EE" opacity=".55"/>'
    o += '<path d="M30 28 Q40 16 58 14" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>'
    return (f'<i class="wdf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{c})">{o}</g></svg></i>')


def wd_decor(sfx=''):
    """まわりに ピンクと水色の 小さな マシュマロ（ぽよん .wdbo）・左上に 水色の リボン・キラッ（.wdtw）"""
    o = ''
    for j, (x, y, c, cd, a) in enumerate(((-22, 84, '#FFD6E2', '#F2B5C8', -16), (222, 88, '#D6ECFB', '#B5D6EF', 14), (226, 8, '#FFFFFF', '#D4E6F6', 10), (-26, 20, '#D6ECFB', '#B5D6EF', -8))):
        o += (f'<g transform="translate({x} {y}) rotate({a})"><g class="wdbo" style="animation-delay:{-0.7 * j:.1f}s">'
              f'<rect x="-14" y="-11" width="28" height="22" rx="10" fill="{cd}"/><rect x="-14" y="-12" width="28" height="17" rx="8.5" fill="{c}"/>'
              '<ellipse cx="-4" cy="-7" rx="5" ry="2.4" fill="#FFFFFF" opacity=".9"/></g></g>')
    o += ('<path d="M24 0 Q8 -18 4 -2 Q10 6 24 0 Z M24 0 Q40 -18 44 -2 Q38 6 24 0 Z" fill="#8CC4EC" stroke="#4F8CC4" stroke-width="1.4"/>'
          '<path d="M24 0 L18 18 L22 16 Z M24 0 L30 18 L26 16 Z" fill="#6FAEDB"/><circle cx="24" cy="0" r="3.6" fill="#6FAEDB"/>')
    for j, (x, y, r) in enumerate(((100, -24, 6), (186, -16, 5), (8, 116, 4.5))):
        o += f'<path class="wdtw" d="{sparkle_d(x, y, r)}" fill="#BFE0F6" style="animation-delay:{-0.8 * j:.1f}s"/>'
    return f'<i class="wdd" aria-hidden="true"><svg viewBox="-40 -40 280 180" width="280" height="180">{o}</svg></i>'


def wd_mm(c, cd):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-15 -13 30 26'><rect x='-14' y='-10' width='28' height='22' rx='10' fill='{cd}'/>"
            f"<rect x='-14' y='-12' width='28' height='17' rx='8.5' fill='{c}'/><ellipse cx='-4' cy='-7' rx='5' ry='2.4' fill='#FFFFFF' opacity='.9'/></svg>")


WD_PIECES = dict(
    m1=f'background-image:url("{durl(wd_mm("#FFFFFF", "#D4E6F6"))}");height:calc(var(--z) * .86)',
    m2=f'background-image:url("{durl(wd_mm("#FFD6E2", "#F2B5C8"))}");height:calc(var(--z) * .86)',
    m3=f'background-image:url("{durl(wd_mm("#D6ECFB", "#B5D6EF"))}");height:calc(var(--z) * .86)',
    tw=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-10 -10 20 20\'><path d=\'" + sparkle_d(0, 0, 9.5) + "\' fill=\'#8CC4EC\'/></svg>")}")',
    ht=f'background-image:url("{durl("<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-11 -11 22 22\'><path d=\'" + heart_d(0, 0, 10) + "\' fill=\'#8CC4EC\' stroke=\'#4F8CC4\' stroke-width=\'1.2\'/></svg>")}")',
)


def wd_burst():
    return fly_burst('wd', ['m1', 'm2', 'tw', 'm3', 'ht', 'm1', 'm2', 'tw'], 28, 3,
                     sizes=dict(m1=(20, 26), m2=(20, 26), m3=(20, 26), tw=(12, 17), ht=(13, 18)))


WD_CSS = r'''
/* ---------- ホワイトデーの的中ボタン：マシュマロのPUSH（まさちゃんの指定） ----------
   ボタンが まるごと ふわふわの マシュマロ：白い 面（下は うすい水色）・上に ふんわり光・こなを ふった 点・まるい 角。
   「PUSH」は 水色の まるい字に 白い ふち。ボタンが ぽよん ぽよんと ゆれる（上下の動きに 合わせて すこし つぶれる）。
   まわりに ピンクと水色の 小さな マシュマロが ぽよん・左上に 水色の リボン・キラッ。
   押すと マシュマロが ふにゃっと つぶれて ふくらみ（強く光らせない）、白・ピンク・水色の マシュマロと キラッ と ハートが はじけて 落ち、水色の 光の輪が広がる */
.wd{--pushA:#FFFFFF;--pushB:#4F8CC4;--pushC:#FFFFFF;--rim:#D6ECFB;--rimD:#8CC4EC}
.push.wd{--pr:42px;background:#FFFFFF;box-shadow:inset 0 -6px 10px rgba(110,160,210,.25),0 0 0 4px #D6ECFB,0 0 0 6px #8CC4EC,0 8px 0 6px #B5D6EF,0 22px 30px rgba(40,80,130,.35);
  animation:bob .9s ease-in-out infinite,wdSq .9s ease-in-out infinite,popIn .35s cubic-bezier(.2,1.6,.4,1) both}
@keyframes wdSq{0%,100%{scale:1.04 .95}50%{scale:.98 1.03}}
.push.wd span{font:400 40px/1 "Mochiy Pop One",sans-serif;letter-spacing:.04em;color:#5E9FD0;text-shadow:0 0 0 #FFFFFF,2px 2px 0 #FFFFFF,-2px 2px 0 #FFFFFF,2px -2px 0 #FFFFFF,-2px -2px 0 #FFFFFF,0 4px 0 #8CC4EC}
.push.wd::after{border-radius:60px;border-color:rgba(140,196,236,.95)}
.wd .wdf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:42px;overflow:hidden;pointer-events:none;font-style:normal}
.wd .wdf svg{display:block;width:200px;height:100px}
.wd .wdd{position:absolute;left:-40px;top:-40px;width:280px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.wd .wdd svg{display:block;width:280px;height:180px;overflow:visible}
.wd .wdbo{transform-box:fill-box;transform-origin:50% 100%;animation:wdBo 1.8s ease-in-out infinite}
@keyframes wdBo{0%,100%{transform:scale(1.06,.92) translateY(2px)}50%{transform:scale(.96,1.05) translateY(-3px)}}
.wd .wdtw{transform-box:fill-box;transform-origin:50% 50%;animation:wdTw 2.4s ease-in-out infinite}
@keyframes wdTw{0%,100%{opacity:.25;transform:scale(.5)}50%{opacity:1;transform:scale(1.1)}}
.tap.wd{font-family:"Mochiy Pop One",sans-serif;font-weight:400;color:#E3F1FB;letter-spacing:.12em;text-shadow:0 2px 0 #3A78B4,0 0 10px rgba(140,196,236,.7)}
.pressed.wd{border-radius:42px;background:#FFFFFF;box-shadow:0 0 0 4px #D6ECFB,0 0 0 6px #8CC4EC,0 8px 0 6px #B5D6EF;animation-name:wdPress}
@keyframes wdPress{0%{transform:scale(1)}25%{transform:scale(1.12,.78)}50%{transform:scale(.94,1.1)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.push.wd{animation:none!important}.wd .wdbo,.wd .wdtw{animation:none}.clips.wd{display:none}}
''' + fly_css('wd', 'rgba(140,196,236,.95)', WD_PIECES)


FACES = dict(xm=(xm_face, xm_decor), hw=(hw_face, hw_decor), vl=(vl_face, vl_decor), wd=(wd_face, wd_decor))
BURSTS = dict(xm=xm_burst, hw=hw_burst, vl=vl_burst, wd=wd_burst)
CSS = dict(xm=XM_CSS, hw=HW_CSS, vl=VL_CSS, wd=WD_CSS)


def push_svg(code, sfx=''):
    face, decor = FACES[code]
    return face(sfx) + decor(sfx)


def burst(code):
    return BURSTS[code]()
