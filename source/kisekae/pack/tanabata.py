"""壁紙パック ⑪七夕（まさちゃんの 指定「七夕（7月）：天の川を渡る馬と、ゆれる短冊」→ 第4.93版「馬の 道と 馬は 消して、天の川の 両はしから 織姫と 彦星の 馬が
   出会いたくて 天の川を 行ったり 来たり」）
   上の絵：夏の 夜空に ななめに 流れる 天の川（星の つぶと やわらかい 光）。川の 左上に 織姫星・右下に 彦星。
     天の川の 左下の はしから 織姫の 馬（白い 馬・桃色の 布・花の かざり・うすい 桃色の 羽衣）、右上の はしから 彦星の 馬（明るい 栗毛・青い 布・首に 金の 鈴）が
     天の川の すじに そって 走って くる（pack/make/tanabata_art.py：ギャロップ 10コマと 立って 鼻を よせる 1コマ）。
     左上と 右上から 笹の 枝。色とりどりの 短冊（字は 書かない）・紙の 星・紙の くさりが さがる。下に 夜の 町の 丘と 家の あかり（馬は 町の うしろから 出て くる）。
   動き（CSS だけ・14秒の 1回り）：2頭が 両はしから 走って きて（天の川の 向きに かたむき・手前ほど 大きく）まん中で 会う → 鼻を よせて 小さな ハートと 星の キラッ →
     くるっと うしろを 向いて また 両はしへ 走って もどる → くり返す。短冊と 笹の 葉は いつも ゆらゆら。天の川の 星が ゆっくり 流れる。星は ゆっくり 小さく
     またたく（強く 光らせない）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, heart_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'tanabata'
CODE = 'tn'
RUN = 0.48           # ギャロップ 1回（10コマ）
HS = 0.34            # 馬の 絵の 大きさ（2倍の 絵 → 画面）
GOLD = '#F4D27A'
COLORS = ['#E8475A', '#F6C945', '#4A8FE0', '#3FB27F', '#9A6ADE', '#F49AC1', '#F4F1FF']
BAND = ((-20, 150), (410, -20))     # 天の川の まん中の 線（左下 → 右上）
CYCLE = 14.0                        # 行って 会って もどる 1回り（秒）
NOSE = (417, 89)                    # 立った コマの 鼻先（780×320 の 絵の 中）
U_FAR = 330.0                       # 天の川の まん中から の 道のり：はし（外）
U_MEET = (NOSE[0] - 290.2) * HS + 2.5   # 会う 所（鼻先が 少し あいて 向き合う）
T_ARR, T_TURN, T_GO, T_GONE, T_BACK = 4.7, 7.8, 8.2, 13.4, 13.7   # 着く・ふりむく・走りだす・外へ 出る・向きを もどす（外で）
YOFF = 30.0                         # ひづめの 道（天の川の まん中の 線より 下：2頭とも 上の絵に おさまる）


def band_y(x):
    (x0, y0), (x1, y1) = BAND
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


BAND_ANG = math.degrees(math.atan2(BAND[1][1] - BAND[0][1], BAND[1][0] - BAND[0][0]))
BAND_D = (math.cos(math.radians(BAND_ANG)), math.sin(math.radians(BAND_ANG)))     # 右上へ 向かう 向き
CENTER = (195.0, band_y(195) + YOFF)


# ---------------------------------------------------------------- 背景
def sky_svg():
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#081032'/><stop offset='.55' stop-color='#141F56'/>"
            "<stop offset='1' stop-color='#2A2B6E'/></linearGradient>"
            "<linearGradient id='m' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#B9C8FF' stop-opacity='0'/><stop offset='.32' stop-color='#C9D2FF' stop-opacity='.16'/>"
            "<stop offset='.5' stop-color='#F2EAFF' stop-opacity='.3'/><stop offset='.68' stop-color='#D9C8FF' stop-opacity='.16'/><stop offset='1' stop-color='#B9C8FF' stop-opacity='0'/></linearGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
    # 天の川の 光の 帯（ななめ）：まん中の 線に そって 太い 帯を 回す
    cx, cy = 195, band_y(195)
    o += (f"<g transform='translate({f(cx)} {f(cy)}) rotate({f(BAND_ANG)})'>"
          "<rect x='-300' y='-46' width='600' height='92' fill='url(#m)'/>")
    R = rnd(7)
    for i in range(30):                                                   # もやもや（雲の ような 光）
        x = R.uniform(-280, 280)
        y = R.gauss(0, 12)
        o += f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='{f(R.uniform(14, 34))}' ry='{f(R.uniform(5, 11))}' fill='#E6DEFF' opacity='{f(R.uniform(.05, .12))}'/>"
    for i in range(12):                                                   # 暗い すじ
        x = R.uniform(-260, 260)
        o += f"<ellipse cx='{f(x)}' cy='{f(R.gauss(0, 6))}' rx='{f(R.uniform(10, 22))}' ry='{f(R.uniform(1.6, 3.2))}' fill='#141F56' opacity='.25'/>"
    o += '</g>'
    # 遠くの 星（動かない）
    for i in range(110):
        x, y = R.uniform(0, W), R.uniform(0, 140)
        d = abs(y - band_y(x)) * math.cos(math.radians(BAND_ANG))
        if R.random() < (0.35 if d > 40 else 0.9):
            r = R.choice((0.4, 0.5, 0.6, 0.8)) * (1.15 if d < 30 else 1)
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='#F2F0FF' opacity='{f(R.uniform(.3, .85))}'/>"
    return doc(W, H, o, defs=defs)


def river_svg(w=200, h=60, seed=12):
    """天の川の 中を 流れる 星の つぶ（くり返せる：はば w。帯の 向きに そって 置く）"""
    R = rnd(seed)
    o = ''
    for i in range(150):
        x = R.uniform(0, w)
        y = h / 2 + R.gauss(0, h * 0.17)
        r = R.choice((0.4, 0.5, 0.6, 0.7, 0.9, 1.1))
        col = R.choice(('#FFFFFF', '#F2EEFF', '#FFF4D6', '#DDE6FF'))
        for dx in ((0, -w) if x > w - 3 else (0, w) if x < 3 else (0,)):
            o += f"<circle cx='{f(x + dx)}' cy='{f(y)}' r='{r}' fill='{col}' opacity='{f(R.uniform(.45, 1))}'/>"
    return doc(w, h, o)


def big_star(c='#FFF6E0', glow='#FFE9B0'):
    """織姫星・彦星（光の 輪と 4つの とがり）"""
    o = (f"<circle cx='12' cy='12' r='10' fill='{glow}' opacity='.18'/><circle cx='12' cy='12' r='5.5' fill='{glow}' opacity='.3'/>"
         f"<path d='{sparkle_d(12, 12, 11, 0.1)}' fill='{c}' opacity='.9'/><circle cx='12' cy='12' r='2.1' fill='#FFFFFF'/>")
    return doc(24, 24, o)


def tw_star():
    return doc(10, 10, f"<path d='{sparkle_d(5, 5, 4.8, 0.14)}' fill='#FFF8E6'/>")


def town_svg():
    """下の 夜の 町（ゆるい 丘と 家の かげ・あかり）"""
    o = (f"<path d='M0 152 C40 146 80 150 120 147 C170 143 210 150 260 146 C300 143 340 149 390 145 V160 H0 Z' fill='#0C1234'/>")
    R = rnd(5)
    x = 4
    while x < W:
        bw = R.uniform(9, 16)
        bh = R.uniform(5, 10)
        base = 150 + R.uniform(-2, 2)
        o += f"<path d='M{f(x)} {f(base)} V{f(base - bh)} L{f(x + bw / 2)} {f(base - bh - 4)} L{f(x + bw)} {f(base - bh)} V{f(base)} Z' fill='#0A0F2C'/>"
        if R.random() < 0.55:
            o += f"<rect x='{f(x + bw * 0.35)}' y='{f(base - bh + 2)}' width='2.2' height='2' fill='#FFD27A' opacity='.75'/>"
        x += bw + R.uniform(4, 20)
    return doc(W, H, o)


# ---------------------------------------------------------------- 笹と 短冊
def leaf(x, y, L, a, c1, c2):
    """笹の 葉 1まい（根もと (x, y)・長さ L・向き a°）"""
    r = math.radians(a)
    ux, uy = math.cos(r), math.sin(r)
    nx, ny = -uy, ux
    w = L * 0.17
    tip = (x + ux * L, y + uy * L)
    p1 = (x + ux * L * 0.35 + nx * w, y + uy * L * 0.35 + ny * w)
    p2 = (x + ux * L * 0.4 - nx * w * 0.8, y + uy * L * 0.4 - ny * w * 0.8)
    d = (f"M{f(x)} {f(y)} Q{f(p1[0])} {f(p1[1])} {f(tip[0])} {f(tip[1])} Q{f(p2[0])} {f(p2[1])} {f(x)} {f(y)} Z")
    return (f"<path d='{d}' fill='{c1}'/>"
            f"<path d='M{f(x)} {f(y)} L{f(x + ux * L * 0.85)} {f(y + uy * L * 0.85)}' stroke='{c2}' stroke-width='.6' opacity='.8'/>")


def leaves_svg(n, seed, size=38, ang0=200, spread=110, L=(13, 19)):
    """葉の かたまり（中心 (size/2, size/2) から 葉が ひらく）"""
    R = rnd(seed)
    o = ''
    c = size / 2
    for k in range(n):
        a = ang0 + spread * (k / max(1, n - 1) - 0.5) + R.uniform(-8, 8)
        o += leaf(c, c, R.uniform(*L), a, R.choice(('#3E9A52', '#4FB061', '#2F7E44')), '#1E5A30')
    return doc(size, size, o)


def branch_svg(pts, w=2.4):
    """笹の 枝（ふしの ある 細い 茎）"""
    o = f"<path d='{smooth(pts, False, 0.5)}' fill='none' stroke='#3F7A3A' stroke-width='{w}' stroke-linecap='round'/>"
    o += f"<path d='{smooth(pts, False, 0.5)}' fill='none' stroke='#7BB86A' stroke-width='{w * 0.35}' stroke-linecap='round' opacity='.6' transform='translate(0 -.6)'/>"
    for p in pts[1:-1]:
        o += f"<ellipse cx='{f(p[0])}' cy='{f(p[1])}' rx='1.8' ry='1.2' fill='#2F6A30'/>"
    return doc(W, H, o)


def tanzaku_svg(c, L=30, string=8):
    """短冊（ひもで さがる 細長い 紙。上に 穴・紙の つや。字は 書かない）：ひもの 上の はしが 絵の (6, 0)"""
    o = (f"<path d='M6 0 V{string}' stroke='#E8E2D0' stroke-width='.7'/>"
         f"<rect x='1.5' y='{string}' width='9' height='{L}' rx='.8' fill='{c}'/>"
         f"<rect x='1.5' y='{string}' width='9' height='4' rx='.8' fill='#FFFFFF' opacity='.22'/>"
         f"<rect x='9' y='{string}' width='1.5' height='{L}' fill='#000000' opacity='.12'/>"
         f"<circle cx='6' cy='{string + 2}' r='.9' fill='#1A1E40' opacity='.6'/>")
    return doc(12, string + L + 1, o)


def paperstar_svg():
    """紙の 星（黄色・ひもで さがる）：ひもの 上の はしが 絵の (8, 0)"""
    o = (f"<path d='M8 0 V7' stroke='#E8E2D0' stroke-width='.7'/>"
         f"<path d='{star_d(8, 14, 7.4, 3.2)}' fill='#F6C945' stroke='#C8962A' stroke-width='.7'/>"
         f"<path d='M8 14 L8 6.6 M8 14 L15 11.7 M8 14 L12.4 20 M8 14 L3.6 20 M8 14 L1 11.7' stroke='#FFE9A0' stroke-width='.5' opacity='.8'/>")
    return doc(16, 23, o)


def chain_svg():
    """紙の くさり（色の ちがう 輪が つながる）：上の はしが 絵の (5, 0)"""
    o = ''
    cols = ['#E8475A', '#F6C945', '#4A8FE0', '#3FB27F', '#9A6ADE', '#F49AC1']
    for k in range(6):
        y = 2 + k * 5.4
        c = cols[k % len(cols)]
        if k % 2 == 0:
            o += f"<ellipse cx='5' cy='{f(y + 2.6)}' rx='2.6' ry='3.2' fill='none' stroke='{c}' stroke-width='1.6'/>"
        else:
            o += f"<ellipse cx='5' cy='{f(y + 2.6)}' rx='1' ry='3.2' fill='none' stroke='{c}' stroke-width='1.6'/>"
    return doc(10, 36, o)


def sprig(side):
    """笹の 枝の 部品：(枝の 点, 葉の かたまり[(x, y, n, seed, 角度)], さがる もの[(x, y, 種類, 色, 長さ, ひも)])"""
    if side == 'l':
        pts = [(-4, 28), (26, 20), (56, 14), (88, 9), (118, 7)]
        lv = [(24, 18, 5, 1, 210), (52, 12, 5, 2, 190), (84, 6, 6, 3, 230), (114, 4, 5, 4, 260), (8, 26, 4, 5, 160)]
        hang = [(18, 23, 't', COLORS[0], 30, 6), (42, 17, 't', COLORS[1], 26, 10), (66, 13, 's', None, 0, 0), (78, 10, 't', COLORS[2], 30, 12),
                (104, 8, 't', COLORS[3], 26, 7)]
    else:
        pts = [(394, 34), (366, 24), (338, 17), (308, 12), (282, 10)]
        lv = [(364, 22, 5, 6, 330), (336, 15, 5, 7, 300), (306, 10, 6, 8, 280), (284, 8, 5, 9, 250), (384, 30, 4, 10, 10)]
        hang = [(374, 27, 't', COLORS[4], 28, 8), (350, 20, 'c', None, 0, 0), (326, 15, 't', COLORS[5], 30, 6), (300, 11, 't', COLORS[6], 26, 12),
                (290, 10, 's', None, 0, 0)]
    return pts, lv, hang


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def _ease_out(x):
    return 1 - (1 - x) ** 2


def _ease_in(x):
    return x * x


def _u(t):
    """まん中から の 道のり（2頭 同じ：織姫は −・彦星は ＋）"""
    if t < T_ARR:
        return U_FAR - (U_FAR - U_MEET) * _ease_out(t / T_ARR)
    if t < T_GO:
        return U_MEET
    if t < T_GONE:
        return U_MEET + (U_FAR - U_MEET) * _ease_in((t - T_GO) / (T_GONE - T_GO))
    return U_FAR


def _pt(u):
    return CENTER[0] + BAND_D[0] * u, CENTER[1] + BAND_D[1] * u


def _k(u):
    """手前（左下）ほど 大きく"""
    return 1 - u * 0.0006


def _face(who, t):
    """向き（1＝右・−1＝左）。織姫は はじめ 右（まん中へ）、彦星は はじめ 左"""
    first = 1 if who == 'o' else -1
    return first if (t < T_TURN or t >= T_BACK) else -first


def horse_frames(who, anchor):
    """馬の 入れものの 動き（14秒・こまかい 点を まっすぐ つなぐ）：天の川に そって 走る・会う・ふりむく・もどる"""
    ax, ay = anchor[0] * HS, anchor[1] * HS
    sg = -1 if who == 'o' else 1
    times = [i * 0.1 for i in range(int(CYCLE * 10) + 1)]
    for t in (T_ARR, T_TURN, T_GO, T_GONE, T_BACK):
        times += [t - 0.001, t]
    times = sorted(set(round(t, 4) for t in times if 0 <= t <= CYCLE))
    stops = []
    for t in times:
        u = sg * _u(t)
        x, y = _pt(u)
        k = HS * _k(u) / HS
        sx = k * _face(who, t)
        stops.append((t / CYCLE * 100, f'transform:translate({f(x - ax)}px,{f(y - ay)}px) rotate({f(BAND_ANG)}deg) scale({f(sx, 3)},{f(k, 3)})'))
    return stops


def meet_point():
    """2頭の 鼻先の まん中（会う 所）"""
    pts = []
    for who in ('o', 'h'):
        sg = -1 if who == 'o' else 1
        u = sg * U_MEET
        x, y = _pt(u)
        k = _k(u)
        dx, dy = (NOSE[0] - 290.2) * HS * k * (-sg), (NOSE[1] - 218) * HS * k
        a = math.radians(BAND_ANG)
        pts.append((x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)))
    return (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2


def heart_svg():
    o = (f"<path d='{heart_d(12, 12, 10)}' fill='#F7A3C8' stroke='#FFFFFF' stroke-width='1.4'/>"
         f"<path d='{heart_d(12, 12, 10)}' fill='none' stroke='#E5609A' stroke-width='.6' opacity='.6'/>"
         "<ellipse cx='8' cy='8' rx='2.6' ry='1.7' fill='#FFFFFF' opacity='.75' transform='rotate(-30 8 8)'/>")
    return doc(24, 24, o)


def banner(B):
    still = B.get('still')
    hs = {w: (B.get(f'{w}_run'), B.get(f'{w}_stand')) for w in ('o', 'h')}
    ok = all(r and s_ for r, s_ in hs.values())
    alt = ('夏の夜空にななめに流れる天の川の両はしから、花のかざりと桃色の羽衣の白い馬（織姫の馬）と、青い布の栗毛の馬（彦星の馬）が走ってきて、'
           'まん中で鼻をよせて小さなハートが浮かび、またそれぞれのはしへもどっていくイラスト。川の左上に織姫星、右下に彦星。'
           '左上と右上の笹の枝に、色とりどりの短冊と紙の星と紙のくさりがゆれる。下に夜の町のあかり')
    html = f'<div class="tnw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('tnSky', sky_svg())
    html += f'<i class="tnRv"><i style="background-image:url(&quot;{durl(river_svg())}&quot;)"></i></i>'
    html += img('tnBs v', big_star('#FFF6E0', '#CFE0FF')) + img('tnBs a', big_star('#FFF0D6', '#FFD9A0'))
    tw = tw_star()
    for k in range(8):
        html += img(f'tnTw t{k}', tw)
    if ok:
        for w in ('o', 'h'):
            html += f'<i class="tnHo {w}"><i class="g"><i></i></i><i class="s"></i></i>'
        html += img('tnHt', heart_svg())
        sp = doc(10, 10, f"<path d='{sparkle_d(5, 5, 4.8, 0.14)}' fill='#FFF1C4'/>")
        for k in range(4):
            html += img(f'tnSp p{k}', sp)
    html += img('tnTn', town_svg())
    # 笹（手前）
    for side in ('l', 'r'):
        pts, lv, hang = sprig(side)
        html += img(f'tnBc {side}', branch_svg(pts))
        for j, (x, y, kind, c, L, sl) in enumerate(hang):
            if kind == 't':
                html += img(f'tnTz {side}{j}', tanzaku_svg(c, L, sl))
            elif kind == 's':
                html += img(f'tnTz {side}{j}', paperstar_svg())
            else:
                html += img(f'tnTz {side}{j}', chain_svg())
        for j, (x, y, n, seed, a) in enumerate(lv):
            html += img(f'tnLv {side}{j}', leaves_svg(n, seed, 38, a))
    html += '</div>'

    # ---- CSS
    cx, cy = 195, band_y(195)
    css = ('.tnw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#141F56}'
           '.tnw img,.tnw i{position:absolute;display:block}'
           '.tnw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.tnw .tnSky,.tnw .tnTn,.tnw .tnBc{left:0;top:0;width:390px;height:160px}'
           # 天の川の 星の 流れ：帯の 向きに 回した 入れものの 中を 横に 流す（ふちは ぼかす）
           f'.tnw .tnRv{{left:{f(cx - 300)}px;top:{f(cy - 30)}px;width:600px;height:60px;transform-origin:300px 30px;transform:rotate({f(BAND_ANG)}deg);overflow:hidden;'
           '-webkit-mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent);mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent)}'
           '.tnw .tnRv>i{left:0;top:0;width:800px;height:60px;background-size:200px 60px;background-repeat:repeat-x;animation:tnRiver 26s linear infinite;will-change:transform}'
           '.tnw .tnBs{width:24px;height:24px;animation:tnBig 4.8s ease-in-out infinite}'
           '.tnw .tnBs.v{left:126px;top:22px}.tnw .tnBs.a{left:250px;top:104px;animation-delay:-2.4s}'
           '.tnw .tnTw{width:10px;height:10px;opacity:.2;animation:tnTw 3.6s ease-in-out infinite}'
           '.tnw .tnTz{transform-origin:50% 0}'
           '.tnw .tnLv{width:38px;height:38px;transform-origin:50% 50%}')
    for k, (x, y, d) in enumerate(((176, 18, 0), (214, 52, -1.2), (60, 70, -2.0), (330, 70, -0.6), (150, 120, -2.6), (368, 112, -1.6), (232, 22, -3.0), (24, 96, -0.3))):
        css += f'.tnw .tnTw.t{k}{{left:{x - 5}px;top:{y - 5}px;animation-delay:{f(d)}s}}'
    if ok:
        # 馬：780×320 の 絵の 場所 × HS の 入れもの。ひづめの まん中（anchor）を 天の川の 道に 合わせて 回す・大きさ・向き
        for w in ('o', 'h'):
            run, st = hs[w]
            anchor = run.get('anchor', [290.2, 218])
            ax, ay = anchor[0] * HS, anchor[1] * HS
            n, (cw, ch), (gx, gy) = run['frames'], run['cell'], run['at']
            (sw_, sh_), (sx_, sy_) = st['cell'], st['at']
            css += (f'.tnw .tnHo.{w}{{left:0;top:0;width:{f(780 * HS)}px;height:{f(320 * HS)}px;transform-origin:{f(ax)}px {f(ay)}px;'
                    f'animation:tnGo{w} {f(CYCLE)}s linear infinite;will-change:transform}}'
                    f'.tnw .tnHo.{w} .g{{left:{f(gx * HS)}px;top:{f(gy * HS)}px;width:{f(cw * HS)}px;height:{f(ch * HS)}px;overflow:hidden;'
                    f'animation:tnGv {f(CYCLE)}s step-end infinite}}'
                    f'.tnw .tnHo.{w} .g>i{{left:0;top:0;width:{f(n * cw * HS)}px;height:{f(ch * HS)}px;background:url({run["url"]}) 0 0/{f(n * cw * HS)}px {f(ch * HS)}px no-repeat;'
                    f'animation:tnRun {RUN}s steps({n}) {"0s" if w == "o" else "-.24s"} infinite}}'
                    f'.tnw .tnHo.{w} .s{{left:{f(sx_ * HS)}px;top:{f(sy_ * HS)}px;width:{f(sw_ * HS)}px;height:{f(sh_ * HS)}px;'
                    f'background:url({st["url"]}) 0 0/{f(sw_ * HS)}px {f(sh_ * HS)}px no-repeat;opacity:0;animation:tnSv {f(CYCLE)}s step-end infinite}}'
                    + kf(f'tnGo{w}', horse_frames(w, anchor)))
        P_ = lambda t: t / CYCLE * 100
        css += (kf('tnRun', [(100, 'transform:translateX(-100%)')])
                + kf('tnGv', [(0, 'opacity:1'), (P_(T_ARR), 'opacity:0'), (P_(T_GO), 'opacity:1'), (100, 'opacity:1')])
                + kf('tnSv', [(0, 'opacity:0'), (P_(T_ARR), 'opacity:1'), (P_(T_GO), 'opacity:0'), (100, 'opacity:0')]))
        # ハートと 星の キラッ（会った とき）
        mx, my = meet_point()
        css += (f'.tnw .tnHt{{left:{f(mx - 9)}px;top:{f(my - 27)}px;width:18px;height:18px;opacity:0;transform-origin:50% 80%;animation:tnHeart {f(CYCLE)}s linear infinite}}'
                + kf('tnHeart', [(0, 'opacity:0;transform:translateY(4px) scale(.3)'), (P_(5.0), 'opacity:0;transform:translateY(4px) scale(.3)'),
                                 (P_(5.4), 'opacity:1;transform:translateY(0) scale(1.08)'), (P_(5.7), 'opacity:1;transform:translateY(-1px) scale(1)'),
                                 (P_(7.0), 'opacity:1;transform:translateY(-7px) scale(1)'), (P_(7.6), 'opacity:0;transform:translateY(-11px) scale(.95)'),
                                 (100, 'opacity:0;transform:translateY(-11px) scale(.95)')]))
        for k, (dx, dy, d) in enumerate(((-17, -20, 5.3), (15, -24, 5.6), (-11, -3, 6.1), (19, -6, 6.4))):
            css += (f'.tnw .tnSp.p{k}{{left:{f(mx + dx - 5)}px;top:{f(my + dy - 5)}px;width:10px;height:10px;opacity:0;animation:tnSp{k} {f(CYCLE)}s linear infinite}}'
                    + kf(f'tnSp{k}', [(0, 'opacity:0;transform:scale(.4)'), (P_(d), 'opacity:0;transform:scale(.4)'), (P_(d + .35), 'opacity:.95;transform:scale(1) rotate(20deg)'),
                                      (P_(d + .7), 'opacity:.15;transform:scale(.5) rotate(40deg)'), (P_(d + 1.05), 'opacity:.9;transform:scale(.9) rotate(60deg)'),
                                      (P_(d + 1.45), 'opacity:0;transform:scale(.4) rotate(80deg)'), (100, 'opacity:0;transform:scale(.4)')]))
    # 笹・短冊（さがる 所に 置いて、上の はしを 中心に ゆらす）
    R = rnd(3)
    for side in ('l', 'r'):
        pts, lv, hang = sprig(side)
        for j, (x, y, kind, c, L, sl) in enumerate(hang):
            if kind == 't':
                ww, hh, ox = 12, sl + L + 1, 6
            elif kind == 's':
                ww, hh, ox = 16, 23, 8
            else:
                ww, hh, ox = 10, 36, 5
            sec = R.uniform(2.3, 3.4)
            amp = R.uniform(7, 12)
            css += (f'.tnw .tnTz.{side}{j}{{left:{f(x - ox)}px;top:{f(y)}px;width:{ww}px;height:{hh}px;animation:tnSway{side}{j} {f(sec)}s ease-in-out {f(-R.uniform(0, sec))}s infinite}}'
                    + kf(f'tnSway{side}{j}', [(0, f'transform:rotate({f(-amp)}deg)'), (50, f'transform:rotate({f(amp * 0.8)}deg)'), (100, f'transform:rotate({f(-amp)}deg)')]))
        for j, (x, y, n, seed, a) in enumerate(lv):
            sec = R.uniform(2.6, 3.8)
            css += (f'.tnw .tnLv.{side}{j}{{left:{x - 19}px;top:{y - 19}px;animation:tnLeaf {f(sec)}s ease-in-out {f(-R.uniform(0, sec))}s infinite}}')
    css += (kf('tnRiver', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-200px)')])
            + kf('tnBig', [(0, 'transform:scale(.9);opacity:.85'), (50, 'transform:scale(1.08);opacity:1'), (100, 'transform:scale(.9);opacity:.85')])
            + kf('tnTw', [(0, 'opacity:.15;transform:scale(.5)'), (50, 'opacity:.95;transform:scale(1)'), (100, 'opacity:.15;transform:scale(.5)')])
            + kf('tnLeaf', [(0, 'transform:rotate(-4deg)'), (50, 'transform:rotate(4deg)'), (100, 'transform:rotate(-4deg)')]))
    if still:
        css += reduced('.tnw>*:not(.bnr)')
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_tanabata():
    """背景の もよう：小さな 星と 短冊（うすく）"""
    o = ''
    for x, y, r, op in ((20, 22, 5.5, .32), (96, 70, 4.5, .26), (52, 110, 3.6, .24), (118, 18, 3, .2)):
        o += f"<path d='{star_d(x, y, r, r * 0.45)}' fill='{GOLD}' opacity='{op}'/>"
    for x, y, c, a in ((70, 16, '#E8475A', -8), (24, 74, '#4A8FE0', 6), (112, 104, '#3FB27F', -4)):
        o += f"<rect x='{x}' y='{y}' width='6' height='18' rx='.6' fill='{c}' opacity='.28' transform='rotate({a} {x + 3} {y})'/>"
    for x, y in ((40, 48), (84, 40), (12, 130), (128, 60), (64, 136)):
        o += f"<circle cx='{x}' cy='{y}' r='1.1' fill='#F2F0FF' opacity='.4'/>"
    return tile(140, 140, o)


def chain_strip():
    """上の 帯の 下の ふち：紙の くさり（色の ちがう 輪）"""
    cols = ['#E8475A', '#F6C945', '#4A8FE0', '#3FB27F', '#9A6ADE', '#F49AC1']
    o = ''
    for k, c in enumerate(cols):
        x = 4 + k * 8
        if k % 2 == 0:
            o += f"<ellipse cx='{x + 2}' cy='4' rx='4' ry='2.6' fill='none' stroke='{c}' stroke-width='1.6'/>"
        else:
            o += f"<ellipse cx='{x + 2}' cy='4' rx='4' ry='1' fill='none' stroke='{c}' stroke-width='1.6'/>"
    return tile(48, 8, o)


def orn():
    """すみの 飾り（44×44）：笹の 小枝と 短冊 2まいと 星"""
    o = ("<path d='M4 8 Q22 4 40 10' fill='none' stroke='#3F7A3A' stroke-width='2' stroke-linecap='round'/>")
    for x, y, a in ((10, 7, 200), (22, 5, 240), (34, 8, 300), (40, 10, 20)):
        o += leaf(x, y, 9, a, '#4FB061', '#1E5A30')
    o += ("<path d='M16 7 V12' stroke='#E8E2D0' stroke-width='.7'/><rect x='12.5' y='12' width='7' height='22' rx='.6' fill='#E8475A'/>"
          "<path d='M28 7 V14' stroke='#E8E2D0' stroke-width='.7'/><rect x='24.5' y='14' width='7' height='20' rx='.6' fill='#4A8FE0'/>")
    o += f"<path d='{star_d(37, 30, 5.6, 2.4)}' fill='{GOLD}' stroke='#B8902E' stroke-width='.6'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='七夕', desc='天の川と短冊', title='七夕（夏の夜空×短冊）', banner=ID,
    alt='夏の夜空に流れる天の川の両はしから、織姫の馬（花のかざりと桃色の羽衣の白い馬）と彦星の馬（青い布の栗毛の馬）が走ってきて、まん中で会うイラスト。笹の枝に色とりどりの短冊がゆれる',
    fonts=['Yuji+Mai', 'Zen+Maru+Gothic:wght@500;700'],
    v=dict(bg='#0F1838', ink='#F3F4FF', sub='#AEB8E0', card='#18234C', cardB='1px solid #33407A', cardO='0 solid transparent', cardS='0 8px 22px rgba(0,0,0,.35)',
           radius='16px', rs='12px', font='"Zen Maru Gothic"', dfont='"Yuji Mai"', dw='400', logo='#FFE9A8', logoS='0 0 10px rgba(244,210,122,.45)',
           iii=GOLD, iiiB='0 solid transparent', iiiR='3px', hd='linear-gradient(180deg,#0A1130,#18235A)', hdInk='#F3F4FF', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.06)', mLine='rgba(244,210,122,.55)', mInk='#F3F4FF', pill='rgba(255,255,255,.06)', pillLine='rgba(244,210,122,.4)', pillInk='#ECEEFF',
           coin=GOLD, coinInk='#1A1A40', badge='#22306A', badgeInk='#FFE9A8', badgeB='1.5px solid #F4D27A', tagBg='rgba(255,255,255,.06)', tagInk='#DDE2FF',
           tagLine='#3A4886', warnBg='rgba(232,71,90,.2)', warnInk='#FFB4BE', zBg='rgba(255,255,255,.04)', zB='1px solid #2E3A72', znBg='#C93C4F', znInk='#FFFFFF',
           znB='0 solid transparent', znR='999px', znS='none', acc='#FFE09A', nR='8px', w2B='1.5px solid #8C96C6', sep='1px dashed #3A4886',
           btn=GOLD, btnInk='#1A1A40', btnB='0 solid transparent', btnR='14px', btnS='0 3px 0 #A8862E', btn2='transparent', btn2Ink='#FFE09A',
           btn2B='1.5px solid #F4D27A', tab='#0A1130', tabB='1px solid #222D62', tabInk='#98A4D6', tabOn='rgba(244,210,122,.14)', tabOnInk='#FFE09A',
           tabR='14px', sel=GOLD, selInk='#1A1A40', h1='#FFE09A'),
    chk=dict(hd=['#0A1130', '#18235A']),
    css=[('', 'background-image:' + curi(tile_tanabata()) + ',linear-gradient(160deg,transparent 30%,rgba(214,206,255,.07) 48%,transparent 66%);background-size:140px 140px,100% 100%'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-7px;height:8px;background:' + curi(chain_strip()) + ' 0 0/48px 8px repeat-x'),
         ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(244,210,122,.1),transparent 40%)')],
    orn=orn(),
    guide=dict(colors=[('#0F1838', '夜空'), (GOLD, '金の星'), ('#E8475A', '赤の短冊'), ('#3FB27F', '笹'), ('#18234C', 'カード')],
               fonts='見出し：Yuji Mai<br>本文：Zen Maru Gothic', shape='角丸16px・夜空の カード・帯の 下に 紙の くさり・星と 短冊の 背景・すみに 笹と 短冊・的中ボタンは 天の川の PUSH',
               pic='夏の 夜空の 天の川・織姫星と 彦星・天の川の 両はしから 走って きて まん中で 会う 織姫の 馬と 彦星の 馬（小さな ハート）・笹の 枝の 色とりどりの 短冊・紙の 星と くさり・夜の 町'),
)


# ================================================================== 的中ボタン：天の川の PUSH（tn）
def push_face(sfx=''):
    """ボタン（200×100）が 夜空（天の川の 光の 帯・星）。左上から 笹の 枝と 短冊が さがる（.tnfz が ゆれる）"""
    o = ''
    g = f'tnG{sfx}'
    defs = (f"<defs><linearGradient id='{g}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#22307A'/><stop offset='1' stop-color='#0E1640'/></linearGradient></defs>")
    o += (f"<rect x='0' y='0' width='200' height='100' rx='22' fill='url(#{g})' stroke='{GOLD}' stroke-width='3'/>"
          "<path d='M8 92 C60 70 120 40 192 10' stroke='#E8E0FF' stroke-width='22' stroke-linecap='round' opacity='.12' fill='none'/>"
          "<path d='M8 92 C60 70 120 40 192 10' stroke='#FFFFFF' stroke-width='8' stroke-linecap='round' opacity='.1' fill='none'/>")
    R = rnd(19)
    for i in range(46):
        t = R.random()
        x = 8 + 184 * t
        y = 92 - 82 * t + R.gauss(0, 8)
        if 6 < y < 94:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.choice((0.6, 0.8, 1.1)))}' fill='#FFFFFF' opacity='{f(R.uniform(.4, .95))}'/>"
    o += f"<path d='{sparkle_d(30, 24, 6, 0.12)}' fill='#FFF6E0'/><path d='{sparkle_d(170, 76, 6, 0.12)}' fill='#FFF0D6'/>"
    return f'<i class="tnf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}{o}</svg></i>'


def push_decor(sfx=''):
    """左上と 右上の 笹の 枝と ゆれる 短冊（.tnfz）・まわりの 星（.tnft）"""
    o = "<path d='M-34 -10 Q0 -22 40 -12' fill='none' stroke='#3F7A3A' stroke-width='3' stroke-linecap='round'/>"
    o += "<path d='M240 -4 Q206 -20 168 -12' fill='none' stroke='#3F7A3A' stroke-width='3' stroke-linecap='round'/>"
    for x, y, a in ((-26, -14, 200), (-6, -18, 240), (14, -18, 290), (34, -13, 330), (232, -8, 340), (210, -15, 300), (188, -17, 250), (170, -13, 210)):
        o += leaf(x, y, 15, a, '#4FB061', '#1E5A30')
    for j, (x, y, c, L) in enumerate(((-14, -16, '#E8475A', 34), (10, -18, '#F6C945', 30), (198, -15, '#4A8FE0', 32), (222, -10, '#9A6ADE', 28))):
        o += (f'<g class="tnfz" style="transform-origin:{x}px {y}px;animation-delay:{-0.7 * j:.1f}s"><path d="M{x} {y} V{y + 6}" stroke="#E8E2D0" stroke-width="1"/>'
              f'<rect x="{x - 6}" y="{y + 6}" width="12" height="{L}" rx="1" fill="{c}"/><rect x="{x - 6}" y="{y + 6}" width="12" height="5" rx="1" fill="#FFFFFF" opacity=".25"/></g>')
    for j, (x, y, r) in enumerate(((-30, 60, 6), (232, 70, 5.4), (100, -40, 5), (60, 120, 4.4), (150, 124, 4.8))):
        o += f'<path class="tnft" d="{star_d(x, y, r, r * 0.45)}" fill="{GOLD}" style="animation-delay:{-0.6 * j:.2f}s"/>'
    return f'<i class="tnd" aria-hidden="true"><svg viewBox="-40 -60 280 200" width="280" height="200">{o}</svg></i>'


PIECES = dict(
    sg=piece(doc(22, 22, f"<path d='{star_d(11, 11.6, 10, 4.4)}' fill='{GOLD}' stroke='#B8902E' stroke-width='1'/>")),
    tr=piece(doc(10, 24, "<rect x='1' y='1' width='8' height='22' rx='1' fill='#E8475A'/>")) + ';width:calc(var(--z) * .45)',
    ty=piece(doc(10, 24, "<rect x='1' y='1' width='8' height='22' rx='1' fill='#F6C945'/>")) + ';width:calc(var(--z) * .45)',
    tb=piece(doc(10, 24, "<rect x='1' y='1' width='8' height='22' rx='1' fill='#4A8FE0'/>")) + ';width:calc(var(--z) * .45)',
    lf=piece(doc(24, 24, leaf(3, 21, 24, -45, '#4FB061', '#1E5A30'))),
    sw=piece(doc(16, 16, f"<path d='{sparkle_d(8, 8, 7.6, 0.14)}' fill='#FFF6E0'/>")),
)


def push_burst():
    return fly_burst(CODE, ['sg', 'tr', 'lf', 'ty', 'sw', 'tb', 'sg', 'lf'], 28, 77, sizes=dict(sg=(15, 21), tr=(18, 24), ty=(18, 24), tb=(18, 24), lf=(15, 20), sw=(11, 15)))


PUSH_CSS = r'''
/* ---------- 七夕の的中ボタン：天の川の PUSH（壁紙パック） ----------
   ボタンは 夜空（ななめの 天の川の 光・星の つぶ・金の ふち）に 金の「PUSH」。左上と 右上の 笹の 枝から 短冊が さがって ゆれる。
   まわりの 金の 星が ゆっくり ひかる。上下の 動きは 的中と 同じ。押すと 夜空が ちぢんで ふくらみ（強く 光らせない）、
   金の 星・短冊・笹の 葉・キラッが はじけて 落ち、金の 光の 輪が 広がる */
.tn{--pushA:#22307A;--pushB:#0E1640;--pushC:#F4D27A;--rim:#F4D27A;--rimD:#0E1640}
.push.tn{--pr:22px;background:none;border-radius:22px;box-shadow:0 7px 0 #0A0F30,0 18px 26px rgba(0,0,0,.45)}
.push.tn span{font:400 42px/1 "Yuji Mai",serif;letter-spacing:.08em;color:#FFE9A8;text-shadow:0 2px 0 #3A2A10,0 0 12px rgba(244,210,122,.55)}
.push.tn::after{border-radius:36px;border-color:rgba(244,210,122,.85)}
.tn .tnf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:22px;overflow:hidden;pointer-events:none;font-style:normal}
.tn .tnf svg{display:block;width:200px;height:100px}
.tn .tnd{position:absolute;left:-40px;top:-60px;width:280px;height:200px;pointer-events:none;z-index:3;font-style:normal}
.tn .tnd svg{display:block;width:280px;height:200px;overflow:visible}
.tn .tnfz{transform-box:view-box;animation:tnfSw 2.8s ease-in-out infinite}
@keyframes tnfSw{0%,100%{transform:rotate(-9deg)}50%{transform:rotate(8deg)}}
.tn .tnft{transform-box:fill-box;transform-origin:50% 50%;animation:tnfTw 2.8s ease-in-out infinite}
@keyframes tnfTw{0%,100%{opacity:.35;transform:scale(.7)}50%{opacity:1;transform:scale(1.05)}}
.pshadow.tn{width:220px}
.tap.tn{font-family:"Yuji Mai",serif;font-weight:400;color:#FFE9A8;letter-spacing:.14em;text-shadow:0 2px 0 #0E1640,0 0 10px rgba(244,210,122,.6)}
.pressed.tn{border-radius:22px;background:#1A2566;box-shadow:0 0 0 3px #F4D27A,0 7px 0 3px #0A0F30;animation-name:tnPress,fxH}
@keyframes tnPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.tn .tnfz,.tn .tnft{animation:none}.clips.tn{display:none}}
''' + fly_css(CODE, 'rgba(244,210,122,.88)', PIECES)

PUSH = dict(code=CODE, face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
