"""カッコいい：金ピカ・ゴージャス・走る金の馬（右向き）・月桂樹・光の筋・キラキラ
   壁紙の動き（まさちゃんの指定「ぷりけつのお馬」）：3秒に1回、馬のおしりが ぷるんっ と揺れる（くり返す）。
   SVG の中の CSS アニメーション（<style>）なので、アプリの中のファイルなら <img> で出しても動く。視差効果を減らす（prefers-reduced-motion）なら止まる。
   claude.ai のキャンバスは、アップロードした SVG の <style> を消してしまうので、キャンバスの判定画面には絵をじかに入れる（inline・動きの CSS はページの <style>）：
     python3 gold.py <出力フォルダ>                                  → gold.svg（ファイルの形・<style>つき）・gold_horse.svg
     python3 gold.py <出力フォルダ> --judge <Judge_Gold.dc.html>      → ＋判定画面の上の絵を inline の形に書きかえる"""
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

EDGE = '#5A400A'

# おしりの ぷるん：おしり（hind）の線と塗りと、おしりの白いつやを .rp に入れて、おしりの下（馬の座標 RP_O）を中心に
# 縦横に のびちぢみ（ぷ → るん → だんだん小さく）。3秒で1回（はじめの約0.9秒だけ動いて、あとは止まる）
RP_O = (92, 84)
RP_KEYS = [(0, 1, 1), (4, 1.10, .89), (10, .93, 1.10), (16, 1.05, .95), (22, .98, 1.03), (27, 1.01, .99), (31, 1, 1), (100, 1, 1)]
RUMP_GLOSS = 'M70.8 50.6 C 76.6 43.9, 85.3 38.2, 94.8 40.8'


def purun_css(sel='.rp', name='purun', tag=True):
    ox, oy = RP_O
    kf = ''.join(f'{p}%{{transform:translate({ox}px,{oy}px) scale({sx:g},{sy:g}) translate(-{ox}px,-{oy}px)}}' for p, sx, sy in RP_KEYS)
    css = (f'{sel}{{transform-box:view-box;transform-origin:0 0;animation:{name} 3s ease-in-out .6s infinite}}'
           f'@keyframes {name}{{{kf}}}'
           f'@media (prefers-reduced-motion:reduce){{{sel}{{animation:none}}}}')
    return f'<style>{css}</style>' if tag else css


ALT = '黒地に光の筋と月桂樹、金ピカに輝きながら走る馬のイラスト（3秒に1回おしりがぷるんと揺れる）'
INLINE_IDS = ('gh', 'gl', 'bg', 'halo')


def inline(alt=ALT, p='gb'):
    """ページの中にじかに入れる形（<svg class="bnr">）と、そのページの <style> に入れる動きの CSS。
       id に p をつけて、ページのほかの SVG とぶつからないようにする。戻り値 (svg, css)"""
    s = re.sub(r'<style>.*?</style>', '', banner(), flags=re.S)
    for i in INLINE_IDS:
        s = s.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'url(#{i})', f'url(#{p}{i})')
    s = s.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '').replace('<svg ', f'<svg class="bnr" role="img" aria-label="{alt}" ', 1)
    return s, purun_css('.bnr .rp', f'{p}Purun', tag=False)


def judge_inline(fn):
    """判定画面（Judge_Gold.dc.html）の上の絵を inline の形に書きかえる（<img class="bnr"> か、前に入れた <svg class="bnr">）。動きの CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    svg_html, css = inline()
    page, n = re.subn(r'<img class="bnr" [^>]*>|<svg class="bnr" .*?</svg>', lambda m: svg_html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* カッコいいの壁紙：おしりの ぷるん（gold.py） */\n{css}\n/* /カッコいいの壁紙 */\n'
    if '/* カッコいいの壁紙：' in page:
        page = re.sub(r'/\* カッコいいの壁紙：.*?/\* /カッコいいの壁紙 \*/\n', lambda m: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def gold_defs(idp='g', x2=240, y2=150):
    return (f'<linearGradient id="{idp}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            '<stop offset="0" stop-color="#8A6514"/><stop offset=".22" stop-color="#F7E08A"/><stop offset=".42" stop-color="#C9952B"/>'
            '<stop offset=".62" stop-color="#FFF1B8"/><stop offset=".8" stop-color="#D8A537"/><stop offset="1" stop-color="#8A6514"/></linearGradient>')


def gold_horse(fill='url(#gh)'):
    """右向きに走る馬（だいたい 0〜236 × 0〜134）"""
    body = smooth(ellipse_pts(124, 66, 44, 23, 14, rot=-4))
    chest = smooth(ellipse_pts(160, 70, 22, 21, 12))
    hind = smooth(ellipse_pts(90, 63, 28, 26, 12, rot=-10))
    neck = smooth([(136, 52), (148, 32), (164, 16), (184, 7), (200, 16), (200, 34), (190, 54), (180, 72), (162, 84)])
    head = smooth([(184, 8), (197, 6), (210, 14), (222, 26), (232, 38), (231, 47), (222, 50), (211, 46), (200, 40), (191, 32), (185, 20)])
    ear = smooth([(186, 12), (183, -2), (194, 8)])
    far = [limb([(152, 84), (158, 104), (146, 118), (138, 121)], [15, 9, 6.5, 6.5]),      # 前の向こう脚（たたむ）
           limb([(102, 84), (114, 102), (110, 118), (118, 128)], [18, 10, 6.5, 6.5])]      # 後ろの向こう脚（前へ）
    near = [limb([(168, 80), (186, 94), (206, 100), (220, 96)], [16, 10, 6.5, 6.5]),     # 前の手前脚（前へのばす）
            limb([(86, 80), (70, 98), (52, 108), (38, 106)], [21, 11, 6.5, 6.5])]       # 後ろの手前脚（うしろへ）
    tail = limb([(64, 54), (50, 46), (36, 48), (18, 38)], [10, 14, 11, 3])
    tail2 = limb([(64, 58), (50, 58), (36, 66), (20, 62)], [8, 11, 8, 2.5])
    out = ''
    # しっぽ・向こうの脚（少し暗く）
    out += outlined([tail2, tail], fill, EDGE, .9)
    out += g(outlined(far, fill, EDGE, .9), opacity='.82')
    # 体（おしり＝hind だけ .rp に入れて、ぷるんと揺らす。重なりの順は outlined と同じ：線を全部 → 塗りを全部）
    parts = [hind, body, chest, neck, head, ear] + near
    under = [path(d, fill=EDGE, stroke=EDGE, stroke_width=1.8, stroke_linejoin='round') for d in parts]
    over = [path(d, fill=fill) for d in parts]
    rump_gloss = path(RUMP_GLOSS, fill='none', stroke='#FFF8D6', stroke_width='2', stroke_linecap='round', opacity='.85')
    out += f'<g class="rp">{under[0]}</g>' + ''.join(under[1:])
    out += f'<g class="rp">{over[0]}{rump_gloss}</g>' + ''.join(over[1:])
    # ひづめ
    for x, y, a in [(222, 96, 0), (40, 106, 0), (138, 121, 0), (119, 128, 0)]:
        out += f'<ellipse cx="{x}" cy="{y}" rx="4.6" ry="3.4" fill="#5A400A"/>'
    # たてがみ（うしろへなびく）
    for pts, ws in [([(188, 12), (176, 6), (162, 8), (148, 2)], [6, 5, 3.6, 1]),
                    ([(180, 18), (166, 14), (152, 18), (138, 12)], [6.5, 5.5, 4, 1]),
                    ([(170, 26), (156, 24), (144, 30), (130, 26)], [6, 5, 3.6, 1]),
                    ([(160, 36), (148, 36), (136, 42), (124, 40)], [5.5, 4.6, 3.2, 1])]:
        out += outlined([limb(pts, ws)], fill, EDGE, .7)
    # 光のすじ（体のつや）：背中・顔（おしりの1本は上の .rp の中）。背中とおしりの2本は、まさちゃんが赤線で引いた位置（2026/10/18。スクショの赤線をひろって曲線に直した）。
    # 首の上の1本（たてがみに重なっていた所）は、まさちゃんの指定でやめた
    for d in ['M108.5 48 C 123.1 47.3, 140.2 43.9, 153.9 49.8', 'M204 16 C 214 22, 222 30, 228 38']:
        out += path(d, fill='none', stroke='#FFF8D6', stroke_width='2', stroke_linecap='round', opacity='.85')
    # 目・鼻
    out += path('M201 21 Q205 18.5 209 21.5 Q205 23.5 201 21 Z', fill='#3A2806')
    out += path('M225 38 q3 -1 4 2', fill='none', stroke='#3A2806', stroke_width='1.3', stroke_linecap='round')
    return out


def laurel(cx, cy, rx, ry, a0, a1, n=11):
    """月桂樹の枝：だ円の弧（中心 cx,cy）を a0→a1 度へ。葉は先へ向かって2枚ずつ"""
    pts = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    out = path(smooth(pts, closed=False), fill='none', stroke='url(#gl)', stroke_width='2.2', stroke_linecap='round')
    for i in range(1, n + 1):
        x, y = pts[i]
        px, py = pts[i - 1]
        a = math.degrees(math.atan2(y - py, x - px))
        sz = 16 - i * .55
        out += path(leaf(px, py, sz, sz * .42, a - 38), fill='url(#gl)', stroke=EDGE, stroke_width='.6')
        out += path(leaf(px, py, sz, sz * .42, a + 38), fill='url(#gl)', stroke=EDGE, stroke_width='.6')
    tx, ty = pts[-1]
    a = math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))
    out += path(leaf(tx, ty, 12, 5, a), fill='url(#gl)', stroke=EDGE, stroke_width='.6')
    return out


def banner():
    W, H = 390, 160
    defs = purun_css() + gold_defs('gh', 236, 134) + gold_defs('gl', 390, 160)
    defs += ('<radialGradient id="bg" cx=".5" cy=".55" r=".7"><stop offset="0" stop-color="#3A2A08"/><stop offset=".6" stop-color="#140E03"/><stop offset="1" stop-color="#050402"/></radialGradient>'
             '<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE9A3" stop-opacity=".55"/><stop offset="1" stop-color="#FFE9A3" stop-opacity="0"/></radialGradient>')
    b = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
    # 光の筋
    cx, cy = 200, 78
    for i in range(24):
        a = math.radians(i * 15 + 4)
        a2 = math.radians(i * 15 + 9)
        b += f'<path d="M{cx} {cy} L{f(cx + math.cos(a) * 300)} {f(cy + math.sin(a) * 300)} L{f(cx + math.cos(a2) * 300)} {f(cy + math.sin(a2) * 300)} Z" fill="#F6D776" opacity=".07"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="120" ry="70" fill="url(#halo)"/>'
    # 月桂樹
    b += laurel(195, 64, 150, 88, 93, 192) + laurel(195, 64, 150, 88, 87, -12)
    # 金の馬
    b += g(gold_horse(), transform='translate(84 12) scale(.98)')
    # キラキラ
    for x, y, r in [(52, 34, 9), (330, 30, 11), (300, 120, 6), (96, 116, 5), (360, 84, 6), (28, 92, 5), (250, 22, 5), (150, 20, 4)]:
        b += path(sparkle(x, y, r), fill='#FFF6CF')
    for x, y in [(70, 60), (120, 30), (280, 60), (342, 132), (20, 140), (230, 132), (180, 40), (318, 100)]:
        b += f'<circle cx="{x}" cy="{y}" r="1.4" fill="#FFE9A3"/>'
    # 金の二重わく＋角の飾り
    b += '<rect x="5" y="5" width="380" height="150" fill="none" stroke="url(#gl)" stroke-width="2.2"/>'
    b += '<rect x="10" y="10" width="370" height="140" fill="none" stroke="url(#gl)" stroke-width=".8" opacity=".8"/>'
    for x, y in [(5, 5), (385, 5), (5, 155), (385, 155)]:
        b += f'<path d="M{x} {y - 6} L{x + 6} {y} L{x} {y + 6} L{x - 6} {y} Z" fill="url(#gl)" stroke="{EDGE}" stroke-width=".6"/>'
    return svg(W, H, b, defs)


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/gold.svg', 'w').write(banner())
    open(f'{out}/gold_horse.svg', 'w').write(svg(250, 150, f'<rect width="250" height="150" fill="#140E03"/>' + g(gold_horse(), transform='translate(6 8)'), purun_css() + gold_defs('gh', 236, 134)))
    if '--judge' in sys.argv:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
