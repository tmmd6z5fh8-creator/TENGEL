"""壁紙パック ⑧浮世絵風（まさちゃんの 指定「大波と街道を走る馬（オリジナルの絵で）」→ 第4.93版「波しぶきと 波の 表現を もっと 海っぽく・9秒に 1回 お侍さん 1人か 2人
   （ランダム）に 出会う」）
   上の絵（一から 描いた 浮世絵ふうの 景色）：和紙の 地・空の 上に 藍の ぼかし・赤い 日・藍の ぼかしの 山なみ・かすみ（横の 雲の 帯）。
     左に 大きな 波：うしろの 斜面は 深い 藍 → 青 → 波の 頭の 近くは 明るい 水の 色（重ねた 帯）・とぎれとぎれの 水の すじ・前へ 巻く すきとおる 波の ふち・
     巻いた 内がわは 暗い 藍・波の 頭の 白い 泡（まるい ふくらみの ならぶ ふち・小さな 穴・はなれた 泡の つぶ）。有名な 浮世絵の 波（爪の ような 泡）や 構図は まねて いない。
     沖に 帆かけ舟。手前に 海ぞいの 街道（松並木・土の 道・草の 土手）。白い 馬（朱の 布と 手綱・墨の 輪郭：pack/make/ukiyoe_art.py）が 街道を 右へ 走る。右上に 朱の 印（白い 蹄鉄）
   動き：大波が ゆっくり もり上がって くずれる（5.2秒：巻いた 先から 水の まくが おちて、根もとに 白い 泡が 広がる・しぶきは こまかい 水の つぶと しずくと もやが
     上がって 落ちる）・小さな 波が 流れる・舟が ゆれる・かすみが ゆっくり ただよう・街道と 松並木と 土手が 右から 左へ 流れる（馬が 前へ 進んで 見える）。
     9秒に 1回 お侍さん（一から 描いた：ちょんまげ・羽織と しまの 袴・刀 2本・白い 足袋）が 1人 か 2人（45秒の 1回りで 1・2・2・1・1人）、街道の 手前を むこうから 歩いて
     きて、馬と すれちがう ときに 会釈して 歩いて いく（歩く はやさは 街道の 流れる はやさ＋歩幅・会釈の 間は 足が 地面に ついた まま 流れる＝足が すべらない）。強く 光らせない"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'ukiyoe'
AI = dict(d='#1E3F73', m='#2F5E95', l='#86A7C9', p='#C9D9E6')        # 藍
PAPER, PAPER2, SHU, INK = '#F1E6CF', '#F7EFDD', '#C8402C', '#2A2420'
TILE = 390
SURGE = 5.2        # 大波の 1回り（秒）
ROAD_S = 3.1       # 街道の 1まいぶん（秒）：馬の ギャロップ（0.48秒）に 合わせた 速さ


def washi_defs(seed=3):
    """和紙の すじ（ノイズ）と ぼかし（data URI の 絵の 中だけ）"""
    return (f"<filter id='tx' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.7' numOctaves='2' seed='{seed}'/>"
            "<feColorMatrix values='0 0 0 0 .4  0 0 0 0 .3  0 0 0 0 .18  0 0 0 .09 0'/><feComposite in2='SourceGraphic' operator='in'/></filter>")


def sky_svg():
    """和紙の 地・空の 上の 藍の ぼかし・赤い 日・山なみ（藍の ぼかし）・遠い 浜"""
    defs = washi_defs(3) + (f"<linearGradient id='b' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{AI['d']}'/><stop offset='.55' stop-color='{AI['m']}' stop-opacity='.55'/>"
                            f"<stop offset='1' stop-color='{AI['m']}' stop-opacity='0'/></linearGradient>"
                            "<linearGradient id='w' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#F7E9CC'/><stop offset='1' stop-color='#F1DDB8'/></linearGradient>"
                            f"<linearGradient id='m' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{AI['d']}'/><stop offset='.5' stop-color='#58779F'/><stop offset='1' stop-color='#9DB2C9'/></linearGradient>"
                            "<linearGradient id='n' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3E5A54'/><stop offset='1' stop-color='#7D9478'/></linearGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#w)'/><rect width='{W}' height='40' fill='url(#b)'/>"
    o += f"<circle cx='322' cy='60' r='13' fill='{SHU}'/>"
    far = [(170, 86), (196, 74), (214, 70), (232, 62), (250, 66), (266, 58), (284, 54), (300, 60), (318, 66), (336, 62), (356, 70), (374, 66), (396, 72), (396, 88), (170, 88)]
    o += f"<path d='{smooth(far[:-2], False, .5)} L396 88 L170 88 Z' fill='url(#m)'/>"
    near = [(150, 92), (196, 84), (236, 80), (270, 84), (300, 78), (334, 82), (370, 76), (396, 80), (396, 92)]
    o += f"<path d='{smooth(near[:-1], False, .5)} L396 92 L150 92 Z' fill='url(#n)' opacity='.9'/>"
    for x, y in ((214, 82), (226, 81), (290, 80), (300, 79.5), (352, 78)):                 # 遠い 松（点）
        o += f"<path d='M{x} {y} q2 -5 4 0 Z' fill='#2F4B38'/>"
    o += f"<rect width='{W}' height='{H}' fill='#000' filter='url(#tx)'/>"
    return doc(W, H, o, defs=defs)


def kasumi_svg():
    """かすみ（横に のびる 雲の 帯：まるい はし・うすい 桃色と クリーム）"""
    def band(x, y, w, h, col):
        r = h / 2
        return f"<path d='M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z' fill='{col}'/>"
    o = band(150, 38, 150, 9, '#F3D9C2') + band(196, 47, 120, 7, '#F7E7CF') + band(250, 70, 150, 7, '#F7E7CF') + band(120, 30, 70, 6, '#F3D9C2')
    return doc(W, H, o)


def sea_svg():
    """沖の 海（水平線 から 街道の むこう まで）：藍の ぼかし・波の すじ"""
    defs = washi_defs(5) + (f"<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{AI['l']}'/><stop offset='.35' stop-color='{AI['m']}'/>"
                            f"<stop offset='1' stop-color='{AI['d']}'/></linearGradient>")
    o = f"<path d='M0 86 H150 L170 88 L396 92 V130 H0 Z' fill='url(#s)'/>"
    R = rnd(8)
    for i in range(22):                                                     # 波の すじ（藍の 明るい 弧）
        y = R.uniform(94, 124)
        x = R.uniform(140, 390)
        w = R.uniform(10, 22) * (0.7 + (y - 90) / 40)
        o += f"<path d='M{f(x)} {f(y)} q{f(w / 2)} {f(-w * .22)} {f(w)} 0' fill='none' stroke='{AI['p']}' stroke-width='{f(.8 + (y - 90) / 40)}' stroke-linecap='round' opacity='.75'/>"
    o += f"<rect width='{W}' height='{H}' fill='#000' filter='url(#tx)'/>"
    return doc(W, H, o, defs=defs)


def boat_svg():
    """帆かけ舟（小さく）：舟・帆（たての すじ）・人の かげ"""
    o = (f"<path d='M2 22 L36 22 L31 27 L7 27 Z' fill='#6B4A30' stroke='{INK}' stroke-width='.8'/>"
         f"<path d='M18.6 2 V22' stroke='{INK}' stroke-width='1'/>"
         f"<path d='M10 4 H28 V19 H10 Z' fill='#F4EBD6' stroke='{INK}' stroke-width='.8'/>")
    for x in (14.5, 19, 23.5):
        o += f"<path d='M{x} 4 V19' stroke='#C9B48E' stroke-width='.8'/>"
    o += f"<circle cx='30' cy='18.4' r='1.6' fill='{INK}'/><path d='M28.4 21.6 L30 19.4 L31.6 21.6 Z' fill='{INK}'/>"
    return doc(38, 29, o)


# ---------------------------------------------------------------- 大波（第4.93版：もっと 海っぽく）
# 絵の 箱 200×150（上の絵の 中では 左 -10・上 -2）。波は 右へ くずれる：うしろの 斜面 → 波の 頭（泡）→ 前へ 巻く うすい 波の ふち（すきとおる）→
# 巻いた 内がわの 暗い 所 → 下へ おちる 水の まく（くずれる ときだけ）→ 根もとの 白い 泡。輪郭は 墨の 細い 線（浮世絵の 味）・色は 平らな 重ね
WB = (-10, -2)             # 波の 絵の 左上（上の絵の 中）
CREST = [(-4, 76), (14, 62), (32, 47), (50, 33), (68, 22), (86, 15), (102, 11), (116, 12), (129, 16), (140, 23), (148, 32), (152, 42), (150, 51)]
LIP_IN = [(144, 55), (137, 52), (132, 46)]            # 波の ふちの 下がわ（巻いた 先から もどる）
FACE = [(126, 51), (121, 60), (118, 72), (119, 86), (125, 98), (136, 108), (154, 116), (176, 121), (204, 124)]


def _norm(pts, i):
    a = pts[max(0, i - 1)]
    b = pts[min(len(pts) - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    return dy / L, -dx / L            # 進む 向きの 左（波の 外がわ＝上）


def _offset(pts, d):
    """線を 内がわ（下）へ d だけ ずらした 点"""
    out = []
    for i, (x, y) in enumerate(pts):
        nx, ny = _norm(pts, i)
        out.append((x - nx * d, y - ny * d))
    return out


def _body_pts():
    return CREST + LIP_IN + FACE + [(204, 152), (-4, 152)]


def wave_svg():
    """大波の 体：深い 藍 → 青 → 波の 頭の 近くは 明るい 水の 色（重ねた 帯）・すきとおる 波の ふち・巻いた 内がわの 暗い 所・水の すじ・波の 頭の 泡（ふぞろいな ふち と 穴）"""
    body = smooth(_body_pts(), True, .5)
    defs = washi_defs(7) + (f"<clipPath id='c'><path d='{body}'/></clipPath>"
                            "<linearGradient id='v' gradientUnits='userSpaceOnUse' x1='40' y1='150' x2='120' y2='10'>"
                            "<stop offset='0' stop-color='#102A52'/><stop offset='.45' stop-color='#1B3D6E'/><stop offset='.8' stop-color='#2A5A90'/>"
                            "<stop offset='1' stop-color='#3C72A6'/></linearGradient>"
                            "<linearGradient id='lp' gradientUnits='userSpaceOnUse' x1='112' y1='10' x2='152' y2='54'>"
                            "<stop offset='0' stop-color='#6FA9CC'/><stop offset='.55' stop-color='#8CC3DA'/><stop offset='1' stop-color='#A9D6E4'/></linearGradient>"
                            "<linearGradient id='tb' gradientUnits='userSpaceOnUse' x1='122' y1='0' x2='170' y2='0'>"
                            "<stop offset='0' stop-color='#132E58'/><stop offset='.55' stop-color='#1E4677' stop-opacity='.92'/><stop offset='1' stop-color='#3C6E9F' stop-opacity='.35'/></linearGradient>"
                            "<linearGradient id='fc' gradientUnits='userSpaceOnUse' x1='120' y1='50' x2='150' y2='118'>"
                            "<stop offset='0' stop-color='#0D2246'/><stop offset='1' stop-color='#1A3A68'/></linearGradient>")
    # 巻いた 波の 内がわ（波の ふちの 下〜海まで：奥の 波の 面＝暗い 藍。右へ いくほど うすく）
    tube = [(150, 52), (144, 56), (137, 53), (131, 47), (124, 54), (119, 66), (118, 80), (121, 94), (129, 104), (142, 110), (160, 114), (171, 112), (166, 96), (160, 80), (155, 64)]
    o = f"<path d='{smooth(tube, True, .5)}' fill='url(#tb)'/>"
    o += f"<path d='{body}' fill='url(#v)'/>"
    o += "<g clip-path='url(#c)'>"
    # 斜面の 帯（波の 頭に 近いほど 明るい）
    for d0, d1, col in ((0, 7, '#5B91C1'), (7, 15, '#4479AE'), (15, 27, '#2F6197'), (27, 42, '#25528A')):
        a, b = _offset(CREST[:10], d0), _offset(CREST[:10], d1)
        o += f"<path d='{smooth(a + b[::-1], True, .5)}' fill='{col}' opacity='.92'/>"
    # 巻いた 内がわ（暗い）
    hollow = [(150, 53), (144, 57), (137, 55), (131, 50), (124, 56), (120, 67), (120, 80), (124, 92), (131, 100), (141, 92), (147, 78), (151, 64)]
    o += f"<path d='{smooth(hollow, True, .5)}' fill='url(#fc)'/>"
    # すきとおる 波の ふち（巻いた 先まで）：明るい 水の 色と 白い すじ
    lip = CREST[7:] + LIP_IN + [(126, 40), (118, 26), (112, 18)]
    o += f"<path d='{smooth(lip, True, .5)}' fill='url(#lp)' opacity='.95'/>"
    for k, (d, op) in enumerate(((3.2, .75), (6.5, .5))):
        ln = _offset(CREST[7:12], d)
        o += f"<path d='{smooth(ln, False, .5)}' fill='none' stroke='#E6F3F6' stroke-width='{1.1 - k * .3:.1f}' stroke-linecap='round' opacity='{op}'/>"
    # 水の すじ（斜面に そって・とぎれとぎれ）
    R = rnd(21)
    for k in range(9):
        d = 5 + k * 4.6
        ln = _offset(CREST[:9], d)
        L = 90 + k * 6
        dash = ' '.join(f'{f(R.uniform(10, 26))} {f(R.uniform(5, 14))}' for _ in range(5))
        o += (f"<path d='{smooth(ln, False, .5)}' fill='none' stroke='{'#D6E7F0' if k < 4 else '#9DBFD8'}' stroke-width='{f(1.15 - k * .06)}' "
              f"stroke-linecap='round' stroke-dasharray='{dash}' stroke-dashoffset='{f(R.uniform(0, 30))}' opacity='{f(.85 - k * .05)}'/>")
    # 前の 面の すじ（下へ 流れる）
    for k, (x0, y0) in enumerate(((123, 62), (121, 76), (124, 90), (131, 101))):
        o += f"<path d='M{x0} {y0} q{f(6 + k)} {f(6 + k * .6)} {f(14 + k * 3)} {f(8 + k)}' fill='none' stroke='#5F8DB9' stroke-width='.9' stroke-linecap='round' opacity='.7'/>"
    o += "</g>"
    o += f"<path d='{body}' fill='none' stroke='{INK}' stroke-width='1' stroke-linejoin='round'/>"
    # 波の 頭の 泡（ふぞろいな もこもこの ふち・下へ たれる 泡・穴）
    o += _foam_cap()
    # 根もとの 白い 泡（海との さかい）
    for x, y, w in ((128, 104, 16), (140, 112, 22), (160, 118, 24), (182, 122, 22)):
        o += f"<path d='M{x} {y} q{f(w / 2)} -4 {w} 0' fill='none' stroke='#EEF4F2' stroke-width='2' stroke-linecap='round'/>"
    o += f"<path d='{body}' fill='#000' filter='url(#tx)'/>"
    return doc(200, 150, o, defs=defs)


def _foam_cap():
    """波の 頭の 泡：波の 頭の 線に そって、上の ふちは 小さな もこもこ・下の ふちは まるい 波形（雲を さかさに した ような まるい ふくらみの ならび・
       大きさは ふぞろい・とがらせない）・中に 小さな 穴・はなれた 小さな 泡の つぶ"""
    R = rnd(33)
    crest = CREST[2:]                                  # (32, 47) から 先
    pts = []                                           # 1画素ごとの 点
    for a, b in zip(crest, crest[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(2, int(L))
        for j in range(k):
            t = j / k
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    pts.append(crest[-1])
    n = len(pts)
    # 下の ふちの まるい ふくらみ（幅 4〜9 画素・深さ ふぞろい）
    depth = [0.0] * n
    i = 0
    while i < n:
        w = R.randint(4, 9)
        u = i / (n - 1)
        amp = R.uniform(1.6, 4.2) * (0.55 + u)
        for j in range(w):
            if i + j < n:
                uu = (i + j) / (n - 1)
                base = 2.2 + 4.2 * uu
                depth[i + j] = base + amp * math.sqrt(max(0.0, math.sin(math.pi * (j + .5) / w)))
        i += w
    top, bot = [], []
    for i, (x, y) in enumerate(pts):
        nx, ny = _norm(pts, i)
        u = i / (n - 1)
        bump = 1.2 + 1.1 * math.sqrt(abs(math.sin(i * 0.55))) * (0.5 + u)        # 上の もこもこ（まるく）
        top.append((x + nx * bump, y + ny * bump))
        d = depth[i] * (0.6 if u > 0.9 else 1.0)
        bot.append((x - nx * d, y - ny * d))
    shape = top[::2] + bot[::-1][::2]
    o = f"<path d='{smooth(shape, True, .5)}' fill='#F5F1E6' stroke='{INK}' stroke-width='.7' stroke-linejoin='round'/>"
    # 泡の かげ（下がわ うすい 水色）と 穴
    inner = [(x - (x - bx) * 0.5, y - (y - by) * 0.5) for (x, y), (bx, by) in zip(pts, bot)]
    o += f"<path d='{smooth(inner[6:-10:3], False, .5)}' fill='none' stroke='#C9DBE6' stroke-width='1.5' stroke-linecap='round' opacity='.8'/>"
    for i in range(10, n - 12, 17):
        x, y = pts[i]
        bx, by = bot[i]
        cx, cy = x + (bx - x) * 0.6, y + (by - y) * 0.6
        o += f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='{f(R.uniform(.8, 1.4))}' ry='{f(R.uniform(.5, .8))}' fill='#4C83B8' opacity='.8'/>"
    # はなれた 小さな 泡の つぶ（斜面の 上）
    for i in range(8, n - 14, 11):
        bx, by = bot[i]
        nx, ny = _norm(pts, i)
        for k in range(2):
            d = R.uniform(2.2, 6.5)
            o += f"<circle cx='{f(bx - nx * d + R.uniform(-2, 2))}' cy='{f(by - ny * d + R.uniform(-1, 1))}' r='{f(R.uniform(.5, 1.05))}' fill='#EEF3F2' opacity='.9'/>"
    return o


def curtain_svg():
    """巻いた 先から 下へ おちる 水の まく（すきとおる 水色・白い すじ）：絵の 箱 30×70（上の はしが 波の ふちの 先）"""
    o = ("<path d='M8 0 C14 8 18 20 19 34 C20 46 22 56 27 68 L12 68 C9 56 6 44 5 32 C4 20 4 8 8 0 Z' fill='#9CCFE0' opacity='.55'/>"
         f"<path d='M8 0 C14 8 18 20 19 34 C20 46 22 56 27 68' fill='none' stroke='{INK}' stroke-width='.6' opacity='.6'/>")
    for k, (x, op) in enumerate(((9, .8), (13, .6), (16, .7))):
        o += f"<path d='M{x} {6 + k * 3} C{x + 3} {22 + k * 4} {x + 4} {40 + k * 2} {x + 7} {62}' fill='none' stroke='#F2F8F8' stroke-width='.9' stroke-linecap='round' opacity='{op}'/>"
    return doc(30, 70, o)


def spray_svg(seed=6, w=78, h=64):
    """しぶき：こまかい 水の つぶ（たくさん）・少し 大きい しずく（墨の 細い ふち・飛ぶ 向きに のびる）・もや（ぼかした 白）。左下が 波の ふちの 先"""
    R = rnd(seed)
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='3.2'/></filter>"
    o = ''
    for cx, cy, rx, ry, op in ((22, 40, 16, 9, .42), (38, 28, 18, 10, .34), (52, 40, 14, 8, .28)):
        o += f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='#FFFFFF' opacity='{op}' filter='url(#bl)'/>"
    for i in range(70):                                  # こまかい つぶ（扇の 形：左下 → 右上）
        a = math.radians(R.uniform(-85, -10))
        d = R.uniform(4, 60) ** 0.9
        x, y = 8 + math.cos(a) * d * 1.15, 56 + math.sin(a) * d * 0.95
        if 0 < x < w and 0 < y < h:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.35, .95))}' fill='#F7F6EE' opacity='{f(R.uniform(.6, 1))}'/>"
    for i in range(11):                                  # しずく
        a = R.uniform(-80, -15)
        d = R.uniform(10, 48)
        x, y = 8 + math.cos(math.radians(a)) * d * 1.15, 56 + math.sin(math.radians(a)) * d * 0.95
        r = R.uniform(1.0, 1.9)
        line = f" stroke='{INK}' stroke-width='.4'" if i % 4 == 0 else ''
        o += (f"<g transform='translate({f(x)} {f(y)}) rotate({f(a + 180)})'><path d='M{f(-r)} 0 Q{f(-r)} {f(-r * .8)} 0 {f(-r * .8)} Q{f(r * 3.2)} 0 0 {f(r * .8)} Q{f(-r)} {f(r * .8)} {f(-r)} 0 Z' "
              f"fill='#F7F4EA' opacity='.92'{line}/></g>")
    return doc(w, h, o, defs=defs)


def whitewater_svg():
    """根もとで くずれた 波の 白い 泡（ふぞろいな もこもこ・つぶ）：絵の 箱 90×26"""
    R = rnd(41)
    o = ''
    pts = []
    for i in range(16):
        x = 4 + i * 5.4
        pts.append((x, 13 - R.uniform(2, 7) * math.sin(math.pi * i / 15) ** .6))
    shape = pts + [(86, 18), (60, 21), (30, 21), (4, 17)]
    o += f"<path d='{smooth(shape, True, .5)}' fill='#F2F1E8' stroke='{INK}' stroke-width='.6' opacity='.95'/>"
    o += "<path d='M10 17 Q30 13 50 16 T84 15' fill='none' stroke='#C9DBE6' stroke-width='1.4' opacity='.8'/>"
    for i in range(14):
        o += f"<circle cx='{f(R.uniform(4, 86))}' cy='{f(R.uniform(2, 9))}' r='{f(R.uniform(.5, 1.2))}' fill='#F2F1E8' opacity='.9'/>"
    return doc(90, 26, o)


def crests_svg(w=130, h=22):
    """沖の 小さな 波頭（白い 泡の 弧・くり返し）"""
    o = ''
    for x, y in ((10, 12), (58, 6), (96, 16)):
        for dx in (-w, 0, w):
            xx = x + dx
            o += (f"<path d='M{xx} {y + 4} q7 -9 16 -2' fill='none' stroke='#F7F1E2' stroke-width='1.6' stroke-linecap='round'/>"
                  f"<circle cx='{xx + 15}' cy='{y + 1.6}' r='1.4' fill='#F7F1E2'/>")
    return doc(w, h, o)


def _wrap(x, w=TILE, pad=50):
    return [x + dx for dx in (-w, 0, w) if -pad <= x + dx <= w + pad]


def pine(x, base, h, lean, s=1.0):
    """浮世絵の 松：曲がった 幹（墨の ふち）・平たい 葉の かたまり（墨の ふち・明るい 先）"""
    top = (x + lean * h * 0.35, base - h)
    mid = (x + lean * h * 0.05 - 3 * s, base - h * .5)
    o = (f"<path d='M{f(x - 2.6 * s)} {f(base)} Q{f(mid[0] - 2 * s)} {f(mid[1])} {f(top[0] - 1.2 * s)} {f(top[1] + 4)} L{f(top[0] + 1.6 * s)} {f(top[1] + 4)} "
         f"Q{f(mid[0] + 3 * s)} {f(mid[1])} {f(x + 2.6 * s)} {f(base)} Z' fill='#6A4A34' stroke='{INK}' stroke-width='.9'/>")
    R = rnd(int(x * 7 + h))
    for k in range(4):
        t = 0.15 + k * 0.24
        cx = x + lean * h * 0.35 * (1 - t) + R.uniform(-6, 6) * s + (lean * 8 if k % 2 else -lean * 6)
        cy = base - h * (1 - t * 0.85) - 2
        w = (24 - k * 3) * s
        hh = 7.5 * s
        d = (f"M{f(cx - w / 2)} {f(cy)} Q{f(cx - w * .3)} {f(cy - hh)} {f(cx)} {f(cy - hh * .8)} Q{f(cx + w * .3)} {f(cy - hh * 1.1)} {f(cx + w / 2)} {f(cy)} "
             f"Q{f(cx + w * .2)} {f(cy + hh * .45)} {f(cx)} {f(cy + hh * .2)} Q{f(cx - w * .25)} {f(cy + hh * .5)} {f(cx - w / 2)} {f(cy)} Z")
        o += f"<path d='{d}' fill='#2F4B38' stroke='{INK}' stroke-width='.9'/>"
        o += f"<path d='M{f(cx - w * .35)} {f(cy - hh * .35)} Q{f(cx)} {f(cy - hh * .9)} {f(cx + w * .35)} {f(cy - hh * .4)}' fill='none' stroke='#6E9466' stroke-width='1.6' stroke-linecap='round'/>"
    return o


def pines_svg():
    """松並木（街道の むこうがわ・くり返し）と 石の 土手"""
    o = (f"<path d='M0 54 H{TILE} V62 H0 Z' fill='#9A8C70'/><path d='M0 54 H{TILE} V55.6 H0 Z' fill='#B9AD92'/>")
    for i in range(14):                                                     # 石がき の 目地
        x = i * TILE / 14
        o += f"<path d='M{f(x)} 55.6 V62' stroke='#7A6C52' stroke-width='.7'/>"
    for x, h, lean in ((40, 50, .5), (130, 62, -.3), (215, 46, .4), (300, 58, .2), (372, 52, -.4)):
        for xx in _wrap(x, pad=40):
            o += pine(xx, 56, h, lean)
    return doc(TILE, 62, o)


def road_svg():
    """土の 街道（くり返し）：明るい 土・わだち の すじ・小石"""
    defs = washi_defs(9) + "<linearGradient id='r' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E9D3A2'/><stop offset='1' stop-color='#D9BD86'/></linearGradient>"
    o = f"<rect width='{TILE}' height='26' fill='url(#r)'/><rect width='{TILE}' height='1.6' fill='#BFA270'/>"
    R = rnd(13)
    for i in range(16):
        x, y = R.uniform(0, TILE), R.uniform(5, 22)
        w = R.uniform(16, 40)
        o += f"<path d='M{f(x)} {f(y)} h{f(w)}' stroke='#C9AA74' stroke-width='.9' stroke-linecap='round' opacity='.8'/>"
    for i in range(18):
        x, y = R.uniform(0, TILE), R.uniform(4, 24)
        o += f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='{f(R.uniform(.8, 1.8))}' ry='{f(R.uniform(.5, 1))}' fill='#A88E62'/>"
    o += f"<rect width='{TILE}' height='26' fill='#000' filter='url(#tx)'/>"
    return doc(TILE, 26, o, defs=defs)


def bank_svg():
    """手前の 草の 土手（くり返し）：草の 房（墨の ふち）・小さな 花"""
    o = f"<path d='M0 6 Q{TILE / 4} 2 {TILE / 2} 6 T{TILE} 6 V28 H0 Z' fill='#7C8E4E' stroke='{INK}' stroke-width='.9'/>"
    o += f"<path d='M0 12 Q{TILE / 4} 8 {TILE / 2} 12 T{TILE} 12 V28 H0 Z' fill='#5E7040'/>"
    R = rnd(15)
    for i in range(30):
        x = i * TILE / 30 + R.uniform(-4, 4)
        h = R.uniform(5, 10)
        for xx in _wrap(x, pad=10):
            o += f"<path d='M{f(xx - 3)} 8 Q{f(xx - 1)} {f(8 - h)} {f(xx + 1)} {f(8 - h * 1.1)} Q{f(xx)} {f(8 - h * .4)} {f(xx + 3)} 8' fill='#6E8A44' stroke='{INK}' stroke-width='.6'/>"
    for x in (60, 190, 320):
        for xx in _wrap(x, pad=10):
            o += f"<circle cx='{xx}' cy='9' r='1.8' fill='{SHU}'/><circle cx='{xx + 5}' cy='11' r='1.4' fill='#F7F1E2'/>"
    return doc(TILE, 28, o)


def seal_svg():
    """朱の 印（白い 蹄鉄：字は 入れない）"""
    o = f"<rect x='1' y='1' width='18' height='18' rx='2' fill='{SHU}'/><rect x='2.6' y='2.6' width='14.8' height='14.8' rx='1.2' fill='none' stroke='#F7E8D6' stroke-width='.7'/>"
    pts_o, pts_i = [], []
    for k in range(17):
        a = math.radians(-200 + 220 * k / 16)
        pts_o.append((10 + math.cos(a) * 5.6, 10.6 - math.sin(a) * 6))
        pts_i.append((10 + math.cos(a) * 3.2, 10.6 - math.sin(a) * 3.6))
    o += f"<path d='{P(pts_o + pts_i[::-1])}' fill='#F7E8D6'/>"
    return doc(20, 20, o)


# ---------------------------------------------------------------- お侍さん（第4.93版：9秒に 1回 1人 か 2人 と 出会う）
# 一から 描いた お侍さん（左を 向いて 歩く）：ちょんまげ（そった 頭の 上に のせた まげ）・羽織と 袴（たての しま）・腰に 刀 2本（つかは 前へ 上向き・さやは うしろへ）・
# 白い 足袋と ぞうり。歩く コマ 12（1.125秒で 2歩）と 会釈の コマ 8（1.125秒：おじぎして もどる）
SM_W, SM_H = 46, 58        # 1コマ（絵の 単位）
SM_K = 1.16               # 画面の 大きさ（絵の 単位 × SM_K ＝ px）：街道の 手前を 歩くので 馬と つりあう 大きさ
SM_HIP = (25, 33)          # 腰（回す 中心）
SM_FOOT = 55               # 足の うら
SM_T = 1.125               # 歩く 1回り（秒）・会釈の 長さ
SM_S = 17.0                # 足が 地面に ついて いる 間に うしろへ 動く 長さ（＝0.6回りで）
SM_V = SM_S * SM_K / (0.6 * SM_T)              # 地面に 対する 歩く はやさ（px/秒）
ROAD_V = TILE / ROAD_S                         # 街道の 流れる はやさ（px/秒）
SAMURAI = dict(a=dict(haori='#2E4A75', haoriD='#22385C', hakama='#77736E', hakamaD='#5C5955', stripe='#4C4945'),
               b=dict(haori='#8C4B2E', haoriD='#6E3820', hakama='#3C4360', hakamaD='#2B3048', stripe='#59628A'),
               c=dict(haori='#56663A', haoriD='#43502C', hakama='#6E5640', hakamaD='#56422F', stripe='#46352A'))
SKIN, SKIN_D, HAIR = '#F0CFA8', '#D9B48C', '#1C1818'


def _foot_svg(x, y, lift):
    """足袋（白）と ぞうり（x：かかと・y：足の うら・lift：持ち上げた とき つま先を 下げる）"""
    a = math.radians(-12 * lift)
    tx, ty = x - 5.0 * math.cos(a), y - 5.0 * math.sin(a)
    return (f"<path d='M{f(x + .6)} {f(y - 2.2)} Q{f(x + 1.2)} {f(y)} {f(x)} {f(y)} L{f(tx)} {f(ty)} Q{f(tx - 1)} {f(ty - 1.2)} {f(tx + .8)} {f(ty - 2.0)} Z' "
            f"fill='#F4F0E6' stroke='{INK}' stroke-width='.5'/>"
            f"<path d='M{f(x + .8)} {f(y + .5)} L{f(tx - .4)} {f(ty + .5)}' stroke='#6A4A30' stroke-width='1.1' stroke-linecap='round'/>")


def _hakama(h, front, back, c):
    """袴（すその 広い ひだの ある 布：前の 足と うしろの 足で すそが ひらく）。front・back：(足の x, 足の うらの y)"""
    x, y = h
    hem_f = front[1] - 2.6
    hem_b = back[1] - 2.6
    mid_x = (front[0] + back[0]) / 2
    shape = [(x - 6.2, y - 2.2), (x - 7.0, y + 4), (front[0] - 4.8, (y + hem_f) / 2 + 2), (front[0] - 6.6, hem_f), (front[0] - 1.0, hem_f + 1.0),
             (mid_x, min(hem_f, hem_b) - 1.4), (back[0] + 2.4, hem_b + .8), (back[0] + 6.0, hem_b - .4), (x + 6.4, (y + hem_b) / 2 + 2), (x + 5.4, y - 2.2)]
    o = f"<path d='{smooth(shape, True, .4)}' fill='{c['hakama']}' stroke='{INK}' stroke-width='.6' stroke-linejoin='round'/>"
    # 足の あいだ（またの わかれ）と ひだ
    o += f"<path d='M{f(x + .4)} {f(y + 9)} Q{f(mid_x + .6)} {f(y + 15)} {f(mid_x)} {f(min(hem_f, hem_b) - 1.2)}' fill='none' stroke='{c['hakamaD']}' stroke-width='1.2'/>"
    for t in (-4.6, -1.6, 3.0, 5.4):
        tgt = (front[0] - 4 + (t + 4.6) * 0.25, hem_f) if t < 0 else (back[0] + 1 + (t - 3) * 0.9, hem_b)
        o += f"<path d='M{f(x + t * .8)} {f(y)} Q{f((x + tgt[0]) / 2 + t * .2)} {f((y + tgt[1]) / 2)} {f(tgt[0])} {f(tgt[1])}' fill='none' stroke='{c['stripe']}' stroke-width='.55' opacity='.9'/>"
    return o


def _leg(h, foot, col, dcol, stripe):
    return ''


def _upper(h, tilt, c):
    """上半身（羽織・帯・えり・腕・頭）：腰 h を 中心に tilt°（前へ）まげる"""
    x, y = h
    o = f"<g transform='rotate({f(-tilt)} {f(x)} {f(y)})'>"
    # 胴（羽織）
    body = [(x - 5.8, y - 1.2), (x - 6.6, y - 10), (x - 5.4, y - 17.0), (x - 1.8, y - 18.6), (x + 3.4, y - 18.2), (x + 6.0, y - 15.2), (x + 5.6, y - 6.5), (x + 5.0, y - 1.0)]
    o += f"<path d='{smooth(body, True, .4)}' fill='{c['haori']}' stroke='{INK}' stroke-width='.6' stroke-linejoin='round'/>"
    # えり（白い 下着の えりと 羽織の えり）
    o += f"<path d='M{f(x - 2.4)} {f(y - 18.3)} L{f(x - 5.6)} {f(y - 10.5)} L{f(x - 4.6)} {f(y - 10.2)} L{f(x - 1.4)} {f(y - 17.8)} Z' fill='#F4F0E6' stroke='{INK}' stroke-width='.4'/>"
    o += f"<path d='M{f(x - 1.2)} {f(y - 18)} L{f(x - 4.6)} {f(y - 9.8)}' stroke='{c['haoriD']}' stroke-width='1.1'/>"
    # 帯
    o += f"<path d='M{f(x - 6.0)} {f(y - 3.8)} L{f(x + 5.2)} {f(y - 3.6)} L{f(x + 5.0)} {f(y - 1.0)} L{f(x - 5.7)} {f(y - 1.2)} Z' fill='#D9C9A0' stroke='{INK}' stroke-width='.45'/>"
    # 家紋（白い 輪と 点）
    o += f"<circle cx='{f(x + 2.6)}' cy='{f(y - 13.6)}' r='1.25' fill='none' stroke='#F4F0E6' stroke-width='.6'/><circle cx='{f(x + 2.6)}' cy='{f(y - 13.6)}' r='.4' fill='#F4F0E6'/>"
    # 腕（手前の そで）：手は 刀の つかに そえる
    sleeve = [(x - 1.6, y - 17.2), (x + 3.6, y - 16.4), (x + 3.8, y - 7.0), (x + .6, y - 5.2), (x - 2.4, y - 6.0)]
    o += f"<path d='{smooth(sleeve, True, .35)}' fill='{c['haoriD']}' stroke='{INK}' stroke-width='.55' stroke-linejoin='round'/>"
    o += f"<path d='M{f(x - 1.6)} {f(y - 6.6)} L{f(x - 5.4)} {f(y - 4.6)}' stroke='{c['haoriD']}' stroke-width='2.4' stroke-linecap='round'/>"
    o += f"<ellipse cx='{f(x - 6.3)}' cy='{f(y - 4.4)}' rx='1.5' ry='1.15' fill='{SKIN}' stroke='{INK}' stroke-width='.45'/>"
    # 首と 頭（左を 向いた 横顔）
    hx, hy = x - 1.4, y - 23.6
    o += f"<path d='M{f(x - 2.6)} {f(y - 18.4)} L{f(x - 2.2)} {f(y - 20.6)} L{f(x + .8)} {f(y - 20.6)} L{f(x + 1.2)} {f(y - 18.2)} Z' fill='{SKIN_D}'/>"
    face = [(hx + 3.6, hy - 2.2), (hx + 1.0, hy - 4.6), (hx - 2.6, hy - 4.2), (hx - 4.0, hy - 1.6), (hx - 4.7, hy + .4), (hx - 4.0, hy + 1.0), (hx - 4.2, hy + 2.6),
            (hx - 2.8, hy + 4.0), (hx + .4, hy + 4.4), (hx + 3.4, hy + 2.4)]
    o += f"<path d='{smooth(face, True, .5)}' fill='{SKIN}' stroke='{INK}' stroke-width='.55' stroke-linejoin='round'/>"
    # 髪（うしろと 横）・そった 頭の 上・まげ
    hair = [(hx + .2, hy - 4.3), (hx + 3.0, hy - 3.6), (hx + 4.4, hy - .8), (hx + 4.0, hy + 2.6), (hx + 1.6, hy + 3.2), (hx + .8, hy + .6), (hx + .2, hy - 1.6)]
    o += f"<path d='{smooth(hair, True, .5)}' fill='{HAIR}'/>"
    o += f"<path d='M{f(hx - 2.8)} {f(hy - 4.0)} Q{f(hx - .8)} {f(hy - 5.0)} {f(hx + .6)} {f(hy - 4.4)}' fill='none' stroke='#B7C3CF' stroke-width='.9' opacity='.8'/>"
    o += (f"<path d='M{f(hx + 1.2)} {f(hy - 4.6)} L{f(hx - 2.2)} {f(hy - 6.0)} Q{f(hx - 2.9)} {f(hy - 5.5)} {f(hx - 2.3)} {f(hy - 5.0)} L{f(hx + 1.4)} {f(hy - 3.8)} Z' fill='{HAIR}'/>"
          f"<path d='M{f(hx + 1.0)} {f(hy - 4.2)} L{f(hx + 2.0)} {f(hy - 4.6)}' stroke='#F4F0E6' stroke-width='.5'/>")
    o += f"<ellipse cx='{f(hx + .6)}' cy='{f(hy + .6)}' rx='.9' ry='1.3' fill='{SKIN_D}' stroke='{INK}' stroke-width='.35'/>"       # 耳
    o += f"<circle cx='{f(hx - 2.6)}' cy='{f(hy - .6)}' r='.55' fill='{INK}'/><path d='M{f(hx - 3.6)} {f(hy - 1.8)} L{f(hx - 1.6)} {f(hy - 2.0)}' stroke='{INK}' stroke-width='.55'/>"
    o += f"<path d='M{f(hx - 3.4)} {f(hy + 2.4)} L{f(hx - 2.2)} {f(hy + 2.4)}' stroke='#9A5A48' stroke-width='.45'/>"
    o += '</g>'
    return o


def _swords(h):
    """腰の 刀 2本（つかは 前へ 上向き・さやは うしろへ 下向き）"""
    x, y = h
    o = ''
    for (fx_, fy_, bx_, by_, w) in ((x - 9.6, y - 6.0, x + 11.6, y + 1.6, 1.6), (x - 11.6, y - 4.8, x + 15.6, y + 3.6, 1.8)):
        cx, cy = x - 4.2, y - 2.6
        o += f"<path d='M{f(cx)} {f(cy)} L{f(bx_)} {f(by_)}' stroke='#1B1717' stroke-width='{f(w)}' stroke-linecap='round'/>"
        o += f"<path d='M{f(cx + 2)} {f(cy - .3)} L{f(bx_ - 1)} {f(by_ - .5)}' stroke='#5A5050' stroke-width='.4' opacity='.8'/>"
        o += f"<path d='M{f(cx)} {f(cy)} L{f(fx_)} {f(fy_)}' stroke='#23242C' stroke-width='{f(w + .2)}' stroke-linecap='round'/>"
        o += f"<ellipse cx='{f(cx - .2)}' cy='{f(cy - .1)}' rx='.7' ry='1.6' fill='#B8902E' stroke='{INK}' stroke-width='.3' transform='rotate(20 {f(cx)} {f(cy)})'/>"
    return o


def _samurai(ox, c, feet, bob=0.0, tilt=0.0, lifts=(0.0, 0.0)):
    """1コマ（ox：シートの 中の 左）。feet：[(手前の 足の x, y), (おくの 足の x, y)]（x は かかと）"""
    h = (ox + SM_HIP[0], SM_HIP[1] + bob)
    pts = [(ox + feet[0][0], feet[0][1], lifts[0]), (ox + feet[1][0], feet[1][1], lifts[1])]
    fr, bk = sorted(pts, key=lambda q: q[0])
    o = _foot_svg(pts[1][0], pts[1][1], pts[1][2])                                    # おくの 足（袴の うしろ）
    o += _hakama(h, (fr[0], fr[1]), (bk[0], bk[1]), c)
    o += _foot_svg(pts[0][0], pts[0][1], pts[0][2])
    o += _upper(h, tilt, c)
    o += _swords(h)
    return o


def _foot(phase):
    """歩く 足の 場所（腰からの x・y）：0〜0.6 は 地面（前 → うしろへ）・のこりで 持ち上げて 前へ"""
    if phase < 0.6:
        return -SM_S / 2 + phase / 0.6 * SM_S, SM_FOOT
    u = (phase - 0.6) / 0.4
    return SM_S / 2 - u * SM_S, SM_FOOT - 2.8 * math.sin(math.pi * u)


def samurai_walk_svg(who):
    c = SAMURAI[who]
    o = ''
    for k in range(12):
        t = k / 12
        pn, pf = (t + 0.3) % 1, (t + 0.8) % 1                  # t=0：手前の 足が まん中（足が そろう）
        (ax, ay), (bx, by) = _foot(pn), _foot(pf)
        lf = lambda ph: math.sin(math.pi * (ph - 0.6) / 0.4) if ph >= 0.6 else 0.0
        o += _samurai(k * SM_W, c, [(SM_HIP[0] + ax, ay), (SM_HIP[0] + bx, by)], bob=-0.5 * math.cos(4 * math.pi * t), lifts=(lf(pn), lf(pf)))
    return doc(SM_W * 12, SM_H, o)


BOW = (0, 7, 16, 26, 30, 26, 14, 4)


def samurai_bow_svg(who):
    c = SAMURAI[who]
    o = ''
    for k, a in enumerate(BOW):
        o += _samurai(k * SM_W, c, [(SM_HIP[0] + .8, SM_FOOT), (SM_HIP[0] + 3.4, SM_FOOT)], bob=0.0, tilt=a)
    return doc(SM_W * len(BOW), SM_H, o)


SM_CYCLE = 45.0            # 5回 出会う 1回り（9秒ごと）
SM_SLOTS = [('a',), ('c', 'b'), ('a', 'b'), ('c',), ('a',)]     # 1回ごとの お侍さん（1人 か 2人：ばらばらに）
SM_TOP = 140 - SM_FOOT * SM_K     # 足の うらが 街道の 手前の はし（y 140）
SM_BOW0 = 3 * SM_T         # 9秒の 中で 会釈を はじめる 時（歩く 1回りの 区切り）
SM_XB = 345                # 会釈を はじめる 所（腰の x）：馬の 鼻の 少し 前
SM_GAP = 30                # 2人の とき うしろの 人との 間


def samurai_css():
    """お侍さんの 動き（45秒の 1回りの 中の 区間）：歩いて くる（街道の はやさ＋歩く はやさ）→ 会釈（足は 地面＝街道と 同じ はやさ）→ 歩いて いく"""
    walk_v = ROAD_V + SM_V
    css = ''
    for who in ('a', 'b', 'c'):
        lead = who != 'b'
        pos, vis_w, vis_b = [], [], []
        hp = SM_HIP[0] * SM_K
        off = 460 - hp
        for e, slot in enumerate(SM_SLOTS):
            if who not in slot:
                continue
            r = slot.index(who)
            tb = 9 * e + SM_BOW0
            xb = SM_XB + SM_GAP * r
            t_in = tb - (460 - xb) / walk_v
            x_end_bow = xb - ROAD_V * SM_T
            t_out = tb + SM_T + (x_end_bow + 50) / walk_v
            pos += [(t_in, 460), (tb, xb), (tb + SM_T, x_end_bow), (t_out, -50)]
            vis_w += [(tb, 0), (tb + SM_T, 1)]
            vis_b += [(tb + k * SM_T / len(BOW), k) for k in range(len(BOW))] + [(tb + SM_T, -1)]
        # 位置（linear）：出会いの 間 以外は 右の 外
        stops = [(0, f'transform:translateX({f(off)}px)')]
        for i in range(0, len(pos), 4):
            (t0, x0), (t1, x1), (t2, x2), (t3, x3) = pos[i:i + 4]
            stops += [(t0 / SM_CYCLE * 100, f'transform:translateX({f(x0 - hp)}px)'), (t1 / SM_CYCLE * 100, f'transform:translateX({f(x1 - hp)}px)'),
                      (t2 / SM_CYCLE * 100, f'transform:translateX({f(x2 - hp)}px)'), (t3 / SM_CYCLE * 100, f'transform:translateX({f(x3 - hp)}px)'),
                      (t3 / SM_CYCLE * 100 + 0.01, f'transform:translateX({f(off)}px)')]
        stops.append((100, f'transform:translateX({f(off)}px)'))
        css += f'.ukw .ukSm.{who}{{animation:ukSmX{who} {f(SM_CYCLE)}s linear infinite}}' + kf(f'ukSmX{who}', stops)
        # 歩く コマ（会釈の 間は 消す）。うしろの 人は 半歩 ずらす（会釈を はじめる 時に 足が そろう）
        ws = [(0, 'opacity:1')] + [(t / SM_CYCLE * 100, f'opacity:{v}') for t, v in vis_w] + [(100, 'opacity:1')]
        css += (f'.ukw .ukSm.{who} .w{{animation:ukSmW {f(SM_T, 3)}s steps(12) {"0s" if lead else f"{f(-SM_T / 2, 4)}s"} infinite,ukSmWv{who} {f(SM_CYCLE)}s step-end infinite}}'
                + kf(f'ukSmWv{who}', ws))
        bs = [(0, 'opacity:0;transform:translateX(0)')]
        for t, k in vis_b:
            bs.append((t / SM_CYCLE * 100, 'opacity:0;transform:translateX(0)' if k < 0 else f'opacity:1;transform:translateX({f(-k * SM_W * SM_K)}px)'))
        bs.append((100, 'opacity:0;transform:translateX(0)'))
        css += f'.ukw .ukSm.{who} .b{{animation:ukSmB{who} {f(SM_CYCLE)}s step-end infinite}}' + kf(f'ukSmB{who}', bs)
    css += kf('ukSmW', [(100, f'transform:translateX({f(-12 * SM_W * SM_K)}px)')])
    return css


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に大きな波（深い藍から明るい水の色へ、白い泡の頭、前へ巻くすきとおった波のふち）'
           'と、こまかい水のしぶき。沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走る。'
           'ときどき街道のむこうから、ちょんまげに羽織と袴、刀を二本さしたお侍さんが一人か二人歩いてきて、馬とすれちがうときに会釈する。右上に朱の印のイラスト')
    html = f'<div class="ukw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ukSky', sky_svg()) + img('ukKs', kasumi_svg()) + img('ukSea', sea_svg()) + img('ukBt', boat_svg())
    html += f'<i class="ukCr" style="background-image:url(&quot;{durl(crests_svg())}&quot;)"></i>'
    html += ('<i class="ukWg">' + img('ukWv', wave_svg()) + img('ukCt', curtain_svg()) + '</i>' + img('ukWw', whitewater_svg())
             + img('ukSp s1', spray_svg(6)) + img('ukSp s2', spray_svg(9)))
    html += f'<i class="ukPn" style="background-image:url(&quot;{durl(pines_svg())}&quot;)"></i>'
    html += f'<i class="ukRd" style="background-image:url(&quot;{durl(road_svg())}&quot;)"></i>'
    if run:
        html += '<i class="ukH"><i></i></i>'
    for who in ('a', 'b', 'c'):                                             # お侍さん（馬の 手前を 歩いて きて 会釈）
        html += (f'<i class="ukSm {who}"><i class="w" style="background-image:url(&quot;{durl(samurai_walk_svg(who))}&quot;)"></i>'
                 f'<i class="b" style="background-image:url(&quot;{durl(samurai_bow_svg(who))}&quot;)"></i></i>')
    html += f'<i class="ukBk" style="background-image:url(&quot;{durl(bank_svg())}&quot;)"></i>'
    html += img('ukSl', seal_svg())
    html += '</div>'

    css = ('.ukw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#F1E6CF}'
           '.ukw>*{position:absolute;display:block}'
           '.ukw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.ukw .ukSky,.ukw .ukKs,.ukw .ukSea{left:0;top:0;width:390px;height:160px}'
           '.ukw .ukKs{animation:ukKs 20s ease-in-out infinite}'
           '.ukw .ukBt{left:166px;top:72px;width:38px;height:29px;transform-origin:50% 90%;animation:ukBoat 3.6s ease-in-out infinite}'
           '.ukw .ukCr{left:130px;top:94px;width:390px;height:22px;background-size:130px 22px;background-repeat:repeat-x;animation:ukCrest 9s linear infinite}'
           f'.ukw .ukWg{{left:{WB[0]}px;top:{WB[1]}px;width:200px;height:150px;transform-origin:70px 150px;animation:ukSurge {SURGE}s ease-in-out infinite}}'
           '.ukw .ukWg>img{position:absolute;display:block}'
           '.ukw .ukWv{left:0;top:0;width:200px;height:150px}'
           f'.ukw .ukCt{{left:138px;top:53px;width:30px;height:70px;transform-origin:8px 0;opacity:0;animation:ukCurtain {SURGE}s ease-in-out infinite}}'
           f'.ukw .ukWw{{left:122px;top:94px;width:90px;height:26px;transform-origin:30px 22px;opacity:0;animation:ukWw {SURGE}s ease-out infinite}}'
           f'.ukw .ukSp{{width:78px;height:64px;opacity:0;transform-origin:8px 56px;animation:ukSpray {SURGE}s ease-out infinite}}'
           '.ukw .ukSp.s1{left:130px;top:-12px}'
           f'.ukw .ukSp.s2{{left:136px;top:2px;animation-delay:-.3s}}'
           f'.ukw .ukPn{{left:0;top:56px;width:{2 * TILE}px;height:62px;background-size:{TILE}px 62px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * 1.12, 3)}s linear infinite}}'
           f'.ukw .ukRd{{left:0;top:116px;width:{2 * TILE}px;height:26px;background-size:{TILE}px 26px;background-repeat:repeat-x;animation:ukFlow {ROAD_S}s linear infinite}}'
           f'.ukw .ukBk{{left:0;top:136px;width:{2 * TILE}px;height:28px;background-size:{TILE}px 28px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * .82, 3)}s linear infinite}}'
           '.ukw .ukSl{left:364px;top:6px;width:18px;height:18px}'
           f'.ukw .ukSm{{left:0;top:{f(SM_TOP)}px;width:{f(SM_W * SM_K)}px;height:{f(SM_H * SM_K)}px;overflow:hidden;transform:translateX(500px)}}'
           f'.ukw .ukSm>i{{position:absolute;display:block;left:0;top:0;height:{f(SM_H * SM_K)}px;background-repeat:no-repeat}}'
           f'.ukw .ukSm .w{{width:{f(12 * SM_W * SM_K)}px;background-size:{f(12 * SM_W * SM_K)}px {f(SM_H * SM_K)}px}}'
           f'.ukw .ukSm .b{{width:{f(len(BOW) * SM_W * SM_K)}px;background-size:{f(len(BOW) * SM_W * SM_K)}px {f(SM_H * SM_K)}px;opacity:0}}')
    css += samurai_css()
    if run:
        n, (cw, ch), (ax, ay) = run['frames'], run['cell'], run['at']
        w, h = cw / 2, ch / 2
        css += (f'.ukw .ukH{{left:{f(ax / 2)}px;top:{f(ay / 2 - 7)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'   # 7px 上：ひづめを 街道の まん中に
                f'.ukw .ukH>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({run["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;animation:ukRun .48s steps({n}) infinite}}'
                + kf('ukRun', [(100, f'transform:translateX({f(-n * w)}px)')]))
    css += (kf('ukFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-TILE}px)')])
            + kf('ukCrest', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-130px)')])
            + kf('ukKs', [(0, 'transform:translateX(-8px)'), (50, 'transform:translateX(10px)'), (100, 'transform:translateX(-8px)')])
            + kf('ukBoat', [(0, 'transform:translateY(0) rotate(-3deg)'), (50, 'transform:translateY(2px) rotate(3deg)'), (100, 'transform:translateY(0) rotate(-3deg)')])
            + kf('ukSurge', [(0, 'transform:rotate(-1.3deg) scale(.97,.94)'), (45, 'transform:rotate(1deg) scale(1.02,1.05)'), (60, 'transform:rotate(1.5deg) scale(1.03,1.06)'),
                             (100, 'transform:rotate(-1.3deg) scale(.97,.94)')])
            + kf('ukCurtain', [(0, 'opacity:0;transform:scaleY(.2)'), (40, 'opacity:0;transform:scaleY(.2)'), (47, 'opacity:.9;transform:scaleY(.55)'),
                               (62, 'opacity:.85;transform:scaleY(1)'), (80, 'opacity:0;transform:scaleY(1.05)'), (100, 'opacity:0;transform:scaleY(1.05)')])
            + kf('ukWw', [(0, 'opacity:0;transform:scale(.55,.5)'), (52, 'opacity:0;transform:scale(.55,.5)'), (62, 'opacity:1;transform:scale(1,1)'),
                          (84, 'opacity:.55;transform:scale(1.12,.95)'), (98, 'opacity:0;transform:scale(1.16,.9)'), (100, 'opacity:0;transform:scale(.55,.5)')])
            + kf('ukSpray', [(0, 'opacity:0;transform:translate(-4px,10px) scale(.45)'), (44, 'opacity:0;transform:translate(-4px,10px) scale(.45)'),
                             (53, 'opacity:1;transform:translate(2px,-2px) scale(.95)'), (74, 'opacity:.85;transform:translate(10px,4px) scale(1.08)'),
                             (92, 'opacity:0;transform:translate(16px,18px) scale(1.12)'), (100, 'opacity:0;transform:translate(16px,18px) scale(1.12)')]))
    css += reduced('.ukw>:not(.bnr)') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_chidori():
    """背景の もよう：波と 千鳥（うすい 藍・むかしからの もよう を 一から 描いた もの）"""
    o = ''
    for x, y in ((20, 30), (92, 96)):
        o += (f"<path d='M{x} {y} q6 -8 14 -2 q-4 -1 -6 3 q4 -6 10 -2' fill='none' stroke='#9DB4D2' stroke-width='1.3' stroke-linecap='round' opacity='.55'/>")
    for x, y, s in ((70, 40, 1), (118, 18, .8), (34, 104, .9)):
        o += (f"<g transform='translate({x} {y}) scale({s})' opacity='.5'><path d='M0 0 Q5 -6 12 -3 Q8 -2 6 1 Q10 0 14 2 Q8 5 2 3 Q1 4 -2 6 Q-1 3 0 0 Z' fill='#5E7EA8'/>"
              "<circle cx='10' cy='-2' r='.7' fill='#F3EBDC'/></g>")
    return tile(140, 130, o)


def edge_strip():
    """上の 帯の 下の ふち：藍の 波頭（まるい 泡の ふち）"""
    o = (f"<path d='M0 0 H28 V3 Q24 10 18 7 Q20 3 15 3 Q10 3 9 7 Q4 10 0 3 Z' fill='{AI['m']}'/>"
         "<circle cx='15' cy='3.6' r='1.5' fill='#F3EBDC'/><circle cx='5.6' cy='6.4' r='.9' fill='#F3EBDC'/>")
    return tile(28, 10, o)


def orn():
    """すみの 飾り（44×44）：朱の 印（白い 蹄鉄）と 小さな 波（ページに じかに 置くので id なし）"""
    pts_o, pts_i = [], []
    for k in range(17):
        a = math.radians(-200 + 220 * k / 16)
        pts_o.append((24 + math.cos(a) * 8, 18 - math.sin(a) * 8.6))
        pts_i.append((24 + math.cos(a) * 4.6, 18 - math.sin(a) * 5.2))
    o = (f"<path d='M8 36 Q14 26 24 30 Q18 30 17 34 Q22 28 30 33 Q36 37 40 34' fill='none' stroke='{AI['m']}' stroke-width='2.2' stroke-linecap='round'/>"
         f"<g transform='rotate(-6 24 18)'><rect x='11' y='5' width='26' height='26' rx='3' fill='{SHU}'/><rect x='13.2' y='7.2' width='21.6' height='21.6' rx='2' fill='none' stroke='#F7E8D6' stroke-width='1'/>"
         f"<path d='{P(pts_o + pts_i[::-1])}' fill='#F7E8D6'/></g>")
    return o


THEME = dict(
    id=ID, cat=7, name='浮世絵風', desc='大波と街道', title='浮世絵風（藍×和紙×朱）', banner=ID,
    alt='浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に大きな波（白い泡の頭と、すきとおった波のふち）と水のしぶき、沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走り、ときどきお侍さんとすれちがう。右上に朱の印',
    fonts=['Shippori+Antique+B1', 'Zen+Old+Mincho:wght@600;700'],
    v=dict(bg='#F3EBDC', ink='#2A2420', sub='#6A5D4E', card='#FBF7EE', cardB='1px solid #DCCDB2', cardO='0 solid transparent', cardS='0 2px 0 #E5D8C0',
           radius='8px', rs='6px', font='"Zen Old Mincho"', dfont='"Shippori Antique B1"', dw='400', logo='#F4EFE4', logoS='0 2px 0 #10223F',
           iii='#F4EFE4', iiiB='0 solid transparent', iiiR='2px', hd=f"linear-gradient(180deg,{AI['d']},{AI['m']})", hdInk='#F4EFE4', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.1)', mLine='rgba(244,239,228,.55)', mInk='#F4EFE4', pill='rgba(0,0,0,.18)', pillLine='rgba(244,239,228,.4)', pillInk='#F4EFE4',
           coin=SHU, coinInk='#FFFFFF', badge='#EAF0F8', badgeInk=AI['d'], badgeB='1.5px solid #9DB4D2', tagBg='#F1E7D6', tagInk='#4A3A2C', tagLine='#D9C7A8',
           warnBg='#F8E0DA', warnInk='#9A2A22', zBg='#FFFCF5', zB='1px solid #E2D5BE', znBg=AI['d'], znInk='#FFFFFF', znB='0 solid transparent', znR='3px',
           znS='none', acc='#B23A28', nR='5px', w2B='0 solid transparent', sep='1px solid #D9C7A8', btn='#B8362A', btnInk='#FFFFFF', btnB='0 solid transparent',
           btnR='6px', btnS='0 3px 0 #7A1E18', btn2='#FBF7EE', btn2Ink=AI['d'], btn2B=f"1.5px solid {AI['l']}", tab='#FBF7EE', tabB='1px solid #DCCDB2',
           tabInk='#6A5D4E', tabOn='#E3ECF6', tabOnInk=AI['d'], tabR='8px', sel='#B8362A', selInk='#FFFFFF', h1=AI['d']),
    chk=dict(hd=[AI['d'], AI['m']]),
    css=[('', 'background-image:' + curi(tile_chidori()) + ';background-size:140px 130px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-9px;height:10px;background:' + curi(edge_strip()) + ' 0 0/28px 10px repeat-x')],
    orn=orn(),
    guide=dict(colors=[(AI['d'], '藍'), ('#B8362A', '朱'), ('#F3EBDC', '和紙'), (AI['l'], '水あさぎ'), ('#2A2420', '墨')],
               fonts='見出し：Shippori Antique B1<br>本文：Zen Old Mincho', shape='角丸8px・帯は 藍の ぼかしで 下に 波頭・波と 千鳥の 背景・すみに 朱の 印・的中ボタンは 題箋の PUSH',
               pic='和紙の 地・藍の ぼかしの 空・赤い 日・山なみ・かすみ・大きな 波（深い 藍 → 明るい 水の 色・白い 泡の 頭・すきとおる 波の ふち）と 水の しぶき・帆かけ舟・松並木の 街道・朱の 布の 白い 馬（墨の 輪郭）・ときどき すれちがう お侍さん・朱の 印'),
)


# ================================================================== 的中ボタン：題箋の PUSH（uk）
def push_face(sfx=''):
    """ボタン（200×100）が 浮世絵の 題箋（たんざく形の 札）：うすい 黄の 和紙・藍と 朱の 二重の ふち。左上から 藍の 波頭が かぶさり、右下に 朱の 印"""
    o = ''
    o += (f'<rect x="0" y="0" width="200" height="100" rx="4" fill="#F7EDD3" stroke="{AI["d"]}" stroke-width="5"/>'
          f'<rect x="7" y="7" width="186" height="86" rx="2" fill="none" stroke="{SHU}" stroke-width="2"/>')
    for i in range(7):                                                      # 和紙の すじ
        y = 14 + i * 12
        o += f'<path d="M12 {y} h176" stroke="#E8D9B4" stroke-width="1" opacity=".7"/>'
    # 左上の 波頭（藍・泡の まる）
    o += (f'<path d="M-14 46 Q-16 10 14 -6 Q44 -20 70 -10 Q58 -6 50 2 Q40 10 30 8 Q22 8 18 18 Q12 30 -2 50 Z" fill="{AI["m"]}" stroke="{INK}" stroke-width="1.4"/>'
          f'<path d="M-8 40 Q-8 14 16 2 Q36 -8 56 -6" fill="none" stroke="{AI["p"]}" stroke-width="2" opacity=".8"/>')
    for x, y, r in ((70, -10, 5.4), (60, -2, 4.4), (50, 4, 3.8), (40, 9, 3.2), (30, 9, 2.8)):
        o += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#F7F1E2" stroke="{INK}" stroke-width="1"/>'
    # 右下の 朱の 印（白い 蹄鉄）
    pts_o, pts_i = [], []
    for k in range(17):
        a = math.radians(-200 + 220 * k / 16)
        pts_o.append((184 + math.cos(a) * 7, 86 - math.sin(a) * 7.6))
        pts_i.append((184 + math.cos(a) * 4, 86 - math.sin(a) * 4.5))
    o += (f'<rect x="170" y="72" width="28" height="28" rx="3" fill="{SHU}" transform="rotate(-4 184 86)"/>'
          f'<path d="{P(pts_o + pts_i[::-1])}" fill="#F7E8D6" transform="rotate(-4 184 86)"/>')
    return f'<i class="ukf" aria-hidden="true"><svg viewBox="-20 -24 230 132" width="230" height="132">{o}</svg></i>'


def push_decor(sfx=''):
    """まわりを 千鳥が とぶ（ゆっくり 上下）・小さな 泡の しぶき"""
    o = ''
    for j, (x, y, s) in enumerate(((214, -18, 1.3), (232, 30, 1.1), (-30, 92, 1.2), (110, -58, 1.0))):
        o += (f'<g transform="translate({x} {y}) scale({s})"><g class="ukbo" style="animation-delay:{-0.7 * j:.1f}s"><path d="M0 0 Q5 -6 12 -3 Q8 -2 6 1 Q10 0 14 2 Q8 5 2 3 Q1 4 -2 6 Q-1 3 0 0 Z" fill="{AI["m"]}" stroke="{INK}" stroke-width=".6"/>'
              f'<circle cx="10" cy="-2" r=".8" fill="#F7F1E2"/></g></g>')
    for j, (x, y, r) in enumerate(((-24, 10, 3.4), (-18, 30, 2.4), (226, 92, 3), (60, 116, 2.6))):
        o += f'<circle class="uktw" cx="{x}" cy="{y}" r="{r}" fill="#F7F1E2" stroke="{INK}" stroke-width=".8" style="animation-delay:{-0.5 * j:.1f}s"/>'
    return f'<i class="ukd" aria-hidden="true"><svg viewBox="-40 -70 280 210" width="280" height="210">{o}</svg></i>'


def _plover():
    return doc(24, 16, f"<path d='M4 8 Q9 2 16 5 Q12 6 10 9 Q14 8 18 10 Q12 13 6 11 Q5 12 2 14 Q3 11 4 8 Z' fill='{AI['m']}' stroke='{INK}' stroke-width='.7'/><circle cx='14' cy='6' r='.8' fill='#F7F1E2'/>")


PIECES = dict(pl=piece(_plover()), fo=piece(doc(20, 20, f"<circle cx='10' cy='10' r='8' fill='#F7F1E2' stroke='{INK}' stroke-width='1.2'/><circle cx='7.4' cy='7.4' r='2.4' fill='#FFFFFF'/>")),
              se=piece(doc(20, 20, f"<rect x='2' y='2' width='16' height='16' rx='2' fill='{SHU}'/><rect x='4' y='4' width='12' height='12' rx='1' fill='none' stroke='#F7E8D6' stroke-width='1'/>")),
              wv=piece(doc(26, 18, f"<path d='M2 16 Q2 4 12 2 Q20 1 24 6 Q18 6 16 10 Q12 8 10 12 Q6 13 2 16 Z' fill='{AI['m']}' stroke='{INK}' stroke-width='1'/><circle cx='22' cy='6' r='2.4' fill='#F7F1E2' stroke='{INK}' stroke-width='.7'/>")),
              pn=piece(doc(24, 14, f"<path d='M2 9 Q6 2 12 4 Q18 1 22 8 Q16 12 12 10 Q7 13 2 9 Z' fill='#2F4B38' stroke='{INK}' stroke-width='1'/><path d='M5 7 Q12 3 19 7' fill='none' stroke='#6E9466' stroke-width='1.4'/>")))


def push_burst():
    return fly_burst('uk', ['pl', 'fo', 'wv', 'se', 'fo', 'pn', 'pl', 'fo'], 28, 71, sizes=dict(pl=(16, 22), fo=(9, 14), wv=(16, 22), se=(11, 15), pn=(16, 21)))


PUSH_CSS = r'''
/* ---------- 浮世絵風の的中ボタン：題箋のPUSH（壁紙パック） ----------
   ボタンが まるごと 浮世絵の 題箋（うすい 黄の 和紙・藍と 朱の 二重の ふち・和紙の すじ）に 墨の「PUSH」。左上から 藍の 波頭（白い 泡の まる）が かぶさり、
   右下に 朱の 印（白い 蹄鉄）。まわりを 千鳥が とび、白い しぶきが ゆれる。上下の 動きは 的中と 同じ。押すと 札が ちぢんで ふくらみ（強く 光らせない）、
   千鳥・しぶき・波頭・朱の 印・松葉が はじけて 落ち、藍の 輪が 広がる */
.uk{--pushA:#F7EDD3;--pushB:#1E3F73;--pushC:#C8402C;--rim:#86A7C9;--rimD:#1E3F73}
.push.uk{--pr:4px;background:none;border-radius:4px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(20,34,60,.45)) drop-shadow(0 16px 22px rgba(0,0,0,.35))}
.push.uk span{font:400 42px/1 "Shippori Antique B1",serif;letter-spacing:.08em;color:#2A2420;text-shadow:0 2px 0 #FFFFFF,0 0 6px rgba(255,255,255,.6)}
.push.uk::after{inset:-20px;border-radius:14px;border-color:rgba(134,167,201,.95)}
.uk .ukf{position:absolute;left:-20px;top:-24px;width:230px;height:132px;pointer-events:none;font-style:normal;z-index:-1}
.uk .ukf svg{display:block;width:230px;height:132px;overflow:visible}
.uk .ukd{position:absolute;left:-40px;top:-70px;width:280px;height:210px;pointer-events:none;z-index:3;font-style:normal}
.uk .ukd svg{display:block;width:280px;height:210px;overflow:visible}
.uk .ukbo{animation:ukBo 2.4s ease-in-out infinite alternate}
@keyframes ukBo{from{transform:translateY(-4px) rotate(-6deg)}to{transform:translateY(4px) rotate(6deg)}}
.uk .uktw{transform-box:fill-box;transform-origin:50% 50%;animation:ukTw 2.2s ease-in-out infinite}
@keyframes ukTw{0%,100%{opacity:.25;transform:scale(.6)}50%{opacity:1;transform:scale(1.1)}}
.pshadow.uk{width:220px}
.tap.uk{font-family:"Shippori Antique B1",serif;font-weight:400;color:#F7EDD3;letter-spacing:.14em;text-shadow:0 2px 0 #1E3F73,0 0 10px rgba(134,167,201,.6)}
.pressed.uk{border-radius:4px;background:#F7EDD3;box-shadow:0 0 0 5px #1E3F73,0 7px 0 5px #10223F;animation-name:ukPress,fxH}
@keyframes ukPress{0%{transform:scale(1)}22%{transform:scale(.9)}45%{transform:scale(1.07)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.uk .ukbo,.uk .uktw{animation:none}.clips.uk{display:none}}
''' + fly_css('uk', 'rgba(134,167,201,.9)', PIECES)

PUSH = dict(code='uk', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
