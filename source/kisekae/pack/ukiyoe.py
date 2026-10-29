"""壁紙パック ⑧浮世絵風（まさちゃんの 指定「大波と街道を走る馬（オリジナルの絵で）」→ 第4.93版「波しぶきと 波の 表現を もっと 海っぽく・9秒に 1回 お侍さん 1人か 2人
   （ランダム）に 出会う」→ 第4.94版「四枚目の 波の 浮世絵を 正確に 参考に・5個目の 動画（実際の 波）の 動きを 参考に」→
   第4.95版「波だけ七枚目の画像と形を全く同じにして！」「波の動きが不自然だから滑らかにもっと自然にして！」）
   大波は 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波と 同じ 形（まさちゃんの 指定）。
   上の絵：和紙の 地・空の 上に 藍の ぼかし・赤い 日・藍の ぼかしの 山なみ・かすみ（横の 雲の 帯）。
     左に 神奈川沖浪裏の 大波（make/ukiyoe_great.py：画像から 切りぬいて 浮世絵の 平らな 4つの 色＝白・明るい 青・藍・濃い 藍 に まとめた 絵の シート。
     白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点。空・題箋・落款は すける・舟と 人・富士山は 入れない）。
     沖に 帆かけ舟。手前に 海ぞいの 街道（松並木・土の 道・草の 土手）。白い 馬（朱の 布と 手綱・墨の 輪郭：pack/make/ukiyoe_art.py）が 街道を 右へ 走る。右上に 朱の 印（白い 蹄鉄）
   動き（本物の 波の 動画を 参考に・7秒の 1回り・形は 1つの まま なめらかに つづけて 動く＝入れかえ・すけ なし）：
     波 ぜんたいが ゆっくり もり上がって 前へ せり出す（根もとが 軸）→ 波の 先と 爪（4まい：先の まい ほど 大きく 回す）が 根もとを 中心に しなって 前へ 巻きこむ →
     しぶきの 点が 前へ とんで 落ちる・根もとで 白い 泡が はじけて ひろがる・波の 上から もやが うしろ（左）へ 吹き飛ぶ → また ゆっくり もどる。
     舟が ゆれる・かすみが ゆっくり ただよう・街道と 松並木と 土手が 右から 左へ 流れる（馬が 前へ 進んで 見える）。
     9秒に 1回 お侍さん（一から 描いた：ちょんまげ・羽織と しまの 袴・刀 2本・白い 足袋）が 1人 か 2人（45秒の 1回りで 1・2・2・1・1人）、街道の 手前を むこうから 歩いて
     きて、馬と すれちがう ときに 会釈して 歩いて いく（歩く はやさは 街道の 流れる はやさ＋歩幅・会釈の 間は 足が 地面に ついた まま 流れる＝足が すべらない）。強く 光らせない"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'ukiyoe'
AI = dict(d='#1E3F73', m='#2F5E95', l='#86A7C9', p='#C9D9E6')        # 藍
PAPER, PAPER2, SHU, INK = '#F1E6CF', '#F7EFDD', '#C8402C', '#2A2420'
TILE = 390
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


# ---------------------------------------------------------------- 大波（第4.95版：まさちゃん「波だけ七枚目の画像と形を全く同じにして！」）
# 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波を 画像から 切りぬいて、浮世絵の 平らな 4つの 色（白・明るい 青・藍・濃い 藍）に
# まとめた 絵（make/ukiyoe_great.py：空・題箋・落款は すける・舟と 人・富士山は 入れない）。
# 第4.96版 まさちゃん「浮世絵の赤丸の波はもっと動きを出してリアルにして！波飛沫とか波の高さが変わったりとか！リアルな波の映像から波ができてから消えていく動きを
#   勉強して、浮世絵に転用して！」：本物の 波の 動画（波が 立って → 波の 先が 投げ出されて 巻き → 落ちた 所で 白い 水が はじけて 横へ 走り → しぶきが うしろへ 吹き → 白い 泡に
#   なって 消える）を 浮世絵に。波の 一生（9秒の 1回り・形は 1つの まま なめらかに・すけて 入れかえる こと なし）：
#   ① 前の 波の 白い 泡の 中から 新しい 波が もり上がる（高さ 約6割 → 10割・うしろへ 起きて いた 頭が 立って 爪が のびる：頭の コマ c＝−1 → 0）
#   ② いちばん 高い 時は 神奈川沖浪裏 そのまま（c＝0・爪から しぶきの 点）
#   ③ 波の 先が 前へ 投げ出されて 爪が のびて 下へ 巻きこむ（c＝0 → 1）・しぶきの 点が 前へ とんで 落ちる・頭の 上から しぶきと もやが うしろへ 吹き飛ぶ
#   ④ 波の 先が 落ちた 所で 白い 泡が はじけて、白い 水が 波の 根もとを 右から 左へ 走る（5つ じゅんに）
#   ⑤ 波が くずれて 沈む（頭が 落ちる c＝1 → 1.6・高さが 下がる）・白い 泡の かたまりが もり上がって 波を つつむ → 泡が ひろがって うすく なる 中から 次の 波（①へ）
#   体（body）と 頭の コマ（crest：c の じゅんの ます目）は 同じ 箱（.ukWg）の 中＝高さ・かたむきは 箱の transform で なめらかに。頭の コマは step-end で 入れかえ
WB = (-22, 2)                          # 上の絵の 中の 波の 箱の 左上
WAVE_T = 9.0                           # 波の 一生 1回りの 秒
W_RISE, W_PEAK, W_PITCH = (0.0, 2.8), (2.8, 3.7), (3.7, 4.6)     # もり上がる・神奈川沖浪裏の 形・波の 先が 投げ出される（秒）
W_FALL, W_SINK = (4.6, 7.6), (4.9, 7.8)                          # 頭が 落ちる（c 1 → 1.6）・波 ぜんたいが 沈む
W_FADE = (0.0, 0.5, 7.6, 8.4)                                    # 波が あらわれる・消える（泡の かげで）
# 波の 箱の 形（右へ px・下へ px・横の 大きさ・高さ・かたむき°）：根もとが 軸
WG_LOW = (0.0, 44.0, 1.06, .74, 5.0)       # 泡の 中から 出る 前（低く・うしろへ ねる）
WG_PEAK = (0.0, 0.0, 1.0, 1.0, 0.0)        # 神奈川沖浪裏
WG_PEAK2 = (1.0, 0.0, 1.012, 1.012, 0.0)   # いちばん 高い まま 少し せり出す
WG_PITCH = (3.0, 1.0, 1.01, 1.0, -3.0)     # 波の 先を 投げ出して 前へ かたむく
WG_SUNK = (8.0, 44.0, 1.04, .74, -6.0)     # くずれて 沈んだ
PEEL = [(4.45, 214, 1.1), (4.7, 184, 1.0), (4.95, 154, .95), (5.2, 124, .9), (5.45, 94, .85)]   # 白い 水が 走る（はじける 時・上の絵の x・大きさ）
FOAM_W, FOAM_L, FOAM_M, FOAM_LINE = '#F6F1E3', '#B2C7DE', '#5470A0', '#1B255C'   # 浮世絵の 平らな 色（シートと 同じ）


def hk_claw(x, y, ang, L, w, curl=1, kids=2, seed=0, fill=FOAM_W, line=FOAM_LINE, lw=.6, tot=None):
    """爪の ような 泡の 指：根もと (x, y) から 向き ang° に のびて、先へ いくほど 強く curl の 向きへ 巻く（細く とがる）。外がわに 小さな 指（kids）。根もとは まるい"""
    R = rnd(seed)
    n = 16
    tot = math.radians(tot if tot is not None else R.uniform(210, 270))
    a0 = math.radians(ang)
    c, th = [], []
    px, py = x, y
    for i in range(n + 1):
        s = i / n
        t = a0 + curl * tot * s * s
        c.append((px, py))
        th.append(t)
        px += math.cos(t) * L / n
        py += math.sin(t) * L / n
    left, right = [], []
    for i, ((cx, cy), t) in enumerate(zip(c, th)):
        s = i / n
        hw = w * (1 - 0.9 * s ** .8) / 2
        nx, ny = -math.sin(t), math.cos(t)
        left.append((cx + nx * hw, cy + ny * hw))
        right.append((cx - nx * hw, cy - ny * hw))
    out = ''
    for k in range(kids):
        s = 0.3 + 0.28 * k + R.uniform(-.05, .05)
        i = min(n, int(s * n))
        t = th[i]
        side = -curl
        hw = w * (1 - .9 * s ** .8) / 2 * 0.8
        out += hk_claw(c[i][0] - math.sin(t) * side * hw, c[i][1] + math.cos(t) * side * hw, math.degrees(t) - curl * R.uniform(35, 60), L * R.uniform(.38, .5), w * .55,
                       curl, 0, seed * 7 + k + 1, fill, line, lw * .85)
    cap = []
    t0 = th[0]
    for k in range(1, 6):
        q = math.pi * k / 6
        cap.append((c[0][0] - math.cos(t0) * math.sin(q) * w * .5 + math.sin(t0) * math.cos(q) * w * .5,
                    c[0][1] - math.sin(t0) * math.sin(q) * w * .5 - math.cos(t0) * math.cos(q) * w * .5))
    poly = left + [(c[-1][0] + math.cos(th[-1]) * w * .12, c[-1][1] + math.sin(th[-1]) * w * .12)] + right[::-1] + cap[::-1]
    out += f"<path d='{smooth(poly, True, .5)}' fill='{fill}' stroke='{line}' stroke-width='{f(lw)}' stroke-linejoin='round'/>"
    return out


def _along(pts, t):
    """折れ線の 道のり t（0〜1）の 点と 向き（rad）"""
    seg, L = [], 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        seg.append((a, b, L, d))
        L += d
    s_ = t * L
    for a, b, l0, d in seg:
        if s_ <= l0 + d or (a, b, l0, d) == seg[-1]:
            u = (s_ - l0) / d if d else 0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), math.atan2(b[1] - a[1], b[0] - a[0])


def foam_svg(seed=21, w=72, h=36):
    """波の 根もとで はじける 白い 泡：大きさの ちがう 泡の 山 3つ（北斎の 泡の ように 爪の 指が 上と 外へ・平らな 色）"""
    R = rnd(seed)
    o = ''
    for k, (cx, top, rw, cl) in enumerate(((16, 17, 14, FOAM_L), (54, 15, 15, FOAM_L), (35, 7, 19, FOAM_W))):   # 奥の 2つ → 手前の まん中
        mound = [(cx - rw, h), (cx - rw * .86, top + (h - top) * .45), (cx - rw * .5, top + 3), (cx, top), (cx + rw * .5, top + 3), (cx + rw * .86, top + (h - top) * .45), (cx + rw, h)]
        o += f"<path d='{smooth(mound, True, .5)}' fill='{cl}' stroke='{FOAM_LINE}' stroke-width='.7'/>"
        if cl == FOAM_W:                                                 # 手前の 山の 下の 明るい 青
            o += f"<path d='{smooth([(cx - rw * .7, h), (cx - rw * .45, h - 7), (cx, h - 9), (cx + rw * .45, h - 7), (cx + rw * .7, h)], True, .5)}' fill='{FOAM_L}'/>"
        arc = [(cx - rw * .8, top + (h - top) * .5), (cx - rw * .45, top + 2.4), (cx, top - .4), (cx + rw * .45, top + 2.4), (cx + rw * .8, top + (h - top) * .5)]
        nk = 4 if rw < 16 else 6
        for i in range(nk):
            t = (i + .5) / nk
            (x, y), an = _along(arc, t)
            L = R.uniform(6.5, 9.5) * (1.15 if cl == FOAM_W else 1)
            o += hk_claw(x, y, math.degrees(an) - 90 + R.uniform(-25, 25), L, L * .34, 1 if t > .5 else -1, 2, seed * 10 + k * 9 + i,
                         FOAM_W if (i + k) % 3 else FOAM_L, FOAM_LINE, .55)
    return doc(w, h, o)


def burst_svg(seed=11, w=90, h=70):
    """くずれた ときに はねる しぶき（下の まん中から 上へ ひらく 白い 点）"""
    R = rnd(seed)
    o = ''
    for i in range(80):
        a = math.radians(R.uniform(-160, -20))
        d = R.uniform(4, 62) ** .95
        x, y = w / 2 + math.cos(a) * d * .9, h - 4 + math.sin(a) * d
        if 0 < x < w and 0 < y < h:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.6, 1.7))}' fill='#FBFAF4' opacity='{f(R.uniform(.7, 1))}'/>"
    return doc(w, h, o)


def mist_svg(w=90, h=40):
    """波の 上から うしろへ 吹きとぶ もや（ぼかした 白）"""
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='4'/></filter>"
    o = ("<ellipse cx='60' cy='22' rx='26' ry='9' fill='#FFFFFF' opacity='.55' filter='url(#bl)'/>"
         "<ellipse cx='36' cy='18' rx='22' ry='8' fill='#FFFFFF' opacity='.42' filter='url(#bl)'/>"
         "<ellipse cx='16' cy='22' rx='14' ry='6' fill='#FFFFFF' opacity='.3' filter='url(#bl)'/>")
    return doc(w, h, o, defs=defs)


def foam_band_svg(kind='f', w=280, h=40, seed=31):
    """くずれた 波の 白い 泡の かたまり（波の 根もとを 横に つつむ 帯）：北斎の 泡の ように 爪の 指が 上と 外へ のびる 山が ならぶ（平らな 色）。
       kind＝'b' おくの 列（明るい 青の 山・白い 爪）・'f' 手前の 列（白い 山・下に 明るい 青）"""
    R = rnd(seed + (0 if kind == 'f' else 50))
    o = ''
    back = kind == 'b'
    x = R.uniform(4, 12) - (14 if back else 0)
    k = 0
    while x < w + 10:
        rw = R.uniform(13, 19) * (1.08 if back else 1)
        top = R.uniform(4, 11) if back else R.uniform(11, 19)
        cl = FOAM_L if back else FOAM_W
        mound = [(x - rw, h), (x - rw * .86, top + (h - top) * .45), (x - rw * .5, top + 3), (x, top), (x + rw * .5, top + 3), (x + rw * .86, top + (h - top) * .45), (x + rw, h)]
        o += f"<path d='{smooth(mound, True, .5)}' fill='{cl}' stroke='{FOAM_LINE}' stroke-width='.7'/>"
        if not back:
            o += f"<path d='{smooth([(x - rw * .7, h), (x - rw * .45, h - 8), (x, h - 10), (x + rw * .45, h - 8), (x + rw * .7, h)], True, .5)}' fill='{FOAM_L}'/>"
        arc = [(x - rw * .8, top + (h - top) * .5), (x - rw * .45, top + 2.4), (x, top - .4), (x + rw * .45, top + 2.4), (x + rw * .8, top + (h - top) * .5)]
        nk = 5
        for i in range(nk):
            t = (i + .5) / nk
            (cx_, cy_), an = _along(arc, t)
            L = R.uniform(6.5, 9.5) * (1.1 if not back else 1)
            o += hk_claw(cx_, cy_, math.degrees(an) - 90 + R.uniform(-25, 25), L, L * .34, 1 if t > .5 else -1, 2, seed * 10 + k * 9 + i,
                         FOAM_W if (i + k) % 3 or back else FOAM_L, FOAM_LINE, .55)
        x += rw * R.uniform(1.15, 1.45)
        k += 1
    o += f"<rect x='0' y='{h - 6}' width='{w}' height='6' fill='{FOAM_L if back else FOAM_W}'/>"
    return doc(w, h, o)


def spray_svg(seed=41, w=84, h=44):
    """波の 頭から うしろ（左）へ 吹き飛ぶ しぶき：右の はしから 左上へ ひろがる 白い 点の 帯と うすい もや"""
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='3'/></filter>"
    R = rnd(seed)
    o = ("<ellipse cx='44' cy='26' rx='30' ry='8' fill='#FFFFFF' opacity='.45' filter='url(#bl)' transform='rotate(-12 44 26)'/>"
         "<ellipse cx='22' cy='18' rx='16' ry='6' fill='#FFFFFF' opacity='.3' filter='url(#bl)' transform='rotate(-14 22 18)'/>")
    for i in range(70):
        u = R.uniform(0, 1) ** .7                      # 0＝右の はし（波の 頭）→ 1＝左の 先（ひろがって うすい）
        x = w - 6 - u * (w - 12)
        y = h - 12 - u * 16 + R.gauss(0, 2 + 6 * u)
        r = R.uniform(.5, 1.5) * (1.15 - .5 * u)
        if 0 < y < h:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='#FBFAF4' opacity='{f(R.uniform(.65, 1) * (1 - .45 * u))}'/>"
    return doc(w, h, o, defs=defs)


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
    alt = ('浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（白い背中、濃い藍に白いすじ、'
           '爪のような白い泡の先、爪から落ちるしぶきの点）。波はゆっくりもり上がって前へせり出し、波の先と爪がしなって前へ巻きこむと、しぶきの点が前へとんで落ち、'
           '根もとで白い泡がはじけてひろがり、波の上のもやがうしろへ吹き飛んで、またゆっくりもどる。'
           '沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走る。'
           'ときどき街道のむこうから、ちょんまげに羽織と袴、刀を二本さしたお侍さんが一人か二人歩いてきて、馬とすれちがうときに会釈する。右上に朱の印のイラスト')
    html = f'<div class="ukw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ukSky', sky_svg()) + img('ukKs', kasumi_svg()) + img('ukSea', sea_svg()) + img('ukBt', boat_svg())
    html += f'<i class="ukCr" style="background-image:url(&quot;{durl(crests_svg())}&quot;)"></i>'
    wave = B.get('wave')
    if wave:                                 # 神奈川沖浪裏の 大波（make/ukiyoe_great.py の 絵の シート：体・波の 先と 爪 4まい・しぶきの 点）
        lips = [p for p in wave['parts'] if p.startswith('lip')]
        html += ('<i class="ukWg"><i class="ukW body"></i>' + ''.join(f'<i class="ukW lip {p}"></i>' for p in lips)
                 + '<i class="ukW dots d1"></i><i class="ukW dots d2"></i></i>')
    html += img('ukMs m1', mist_svg()) + img('ukMs m2', mist_svg()) + img('ukFm', foam_svg()) + img('ukBs', burst_svg())
    html += f'<i class="ukPn" style="background-image:url(&quot;{durl(pines_svg())}&quot;)"></i>'
    html += f'<i class="ukRd" style="background-image:url(&quot;{durl(road_svg())}&quot;)"></i>'
    if run:
        html += '<i class="ukH"><i></i></i>'
    sam = B.get('samurai')
    for who in ('a', 'b', 'c'):                                             # お侍さん（馬の 手前を 歩いて きて 会釈）
        if sam:                                                             # 絵の シート（make/ukiyoe_samurai.py：SVG の まま だと 重い）
            html += f'<i class="ukSm {who}"><i class="w"></i><i class="b"></i></i>'
        else:
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
           f'.ukw .ukMs{{width:90px;height:40px;opacity:0;animation:ukMist {f(WAVE_T)}s linear infinite}}.ukw .ukMs.m1{{left:118px;top:-4px}}.ukw .ukMs.m2{{left:150px;top:4px;animation-delay:-.35s}}'
           f'.ukw .ukFm{{left:124px;top:84px;width:72px;height:36px;opacity:0;transform-origin:36px 36px;animation:ukFoam {f(WAVE_T)}s ease-out infinite}}'
           f'.ukw .ukBs{{left:116px;top:46px;width:90px;height:70px;opacity:0;transform-origin:45px 66px;animation:ukBurst {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukPn{{left:0;top:56px;width:{2 * TILE}px;height:62px;background-size:{TILE}px 62px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * 1.12, 3)}s linear infinite}}'
           f'.ukw .ukRd{{left:0;top:116px;width:{2 * TILE}px;height:26px;background-size:{TILE}px 26px;background-repeat:repeat-x;animation:ukFlow {ROAD_S}s linear infinite}}'
           f'.ukw .ukBk{{left:0;top:136px;width:{2 * TILE}px;height:28px;background-size:{TILE}px 28px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * .82, 3)}s linear infinite}}'
           '.ukw .ukSl{left:364px;top:6px;width:18px;height:18px}'
           f'.ukw .ukSm{{left:0;top:{f(SM_TOP)}px;width:{f(SM_W * SM_K)}px;height:{f(SM_H * SM_K)}px;overflow:hidden;transform:translateX(500px)}}'
           f'.ukw .ukSm>i{{position:absolute;display:block;left:0;top:0;height:{f(SM_H * SM_K)}px;background-repeat:no-repeat}}'
           f'.ukw .ukSm .w{{width:{f(12 * SM_W * SM_K)}px}}.ukw .ukSm .b{{width:{f(len(BOW) * SM_W * SM_K)}px;opacity:0}}')
    if sam:                     # 1まいの シート：行（a の 歩く・会釈・b の …）を background-position で えらぶ
        zs = SM_K / sam['z']
        (sw, sh), rp = sam['sheet'], sam['row']
        css += f'.ukw .ukSm>i{{background-image:url({sam["url"]});background-size:{f(sw * zs, 3)}px {f(sh * zs, 3)}px}}'
        for r, key in enumerate(sam['rows']):
            who, kind = key.split('_')
            css += f'.ukw .ukSm.{who} .{kind}{{background-position:0 {f(-r * rp * zs, 3)}px}}'
    else:
        css += (f'.ukw .ukSm .w{{background-size:{f(12 * SM_W * SM_K)}px {f(SM_H * SM_K)}px}}'
                f'.ukw .ukSm .b{{background-size:{f(len(BOW) * SM_W * SM_K)}px {f(SM_H * SM_K)}px}}')
    if wave:
        n = wave['frames']
        gw, gh = wave['size']
        px_, py_ = wave['pivot']
        parts = wave['parts']
        lips = [p for p in parts if p.startswith('lip')]
        css += (f'.ukw .ukWg{{left:{WB[0]}px;top:{WB[1]}px;width:{f(gw)}px;height:{f(gh)}px;transform-origin:{f(gw * .36)}px {f(gh)}px;animation:ukSurge {f(WAVE_T)}s ease-in-out infinite}}'
                f'.ukw .ukW{{position:absolute;left:0;top:0;width:{f(gw)}px;height:{f(gh)}px;background:url({wave["url"]}) 0 0/{f(n * gw)}px {f(gh)}px no-repeat}}'
                f'.ukw .ukW.lip{{transform-origin:{f(px_)}px {f(py_)}px;animation-duration:{f(WAVE_T)}s;animation-timing-function:ease-in-out;animation-iteration-count:infinite}}'
                + ''.join(f'.ukw .ukW.{p}{{background-position:{f(-parts.index(p) * gw)}px 0;animation-name:ukLip{k + 1}}}' for k, p in enumerate(lips))
                + f'.ukw .ukW.dots{{background-position:{f(-parts.index("dots") * gw)}px 0}}'
                f'.ukw .ukW.d1{{animation:ukDot1 {f(WAVE_T)}s linear infinite}}.ukw .ukW.d2{{opacity:0;animation:ukDot2 {f(WAVE_T)}s linear infinite}}')
        for k in range(len(lips)):                  # 先の まい ほど 大きく 回る（根もとは 少し・爪の 先は いちばん）＝波の 先が しなって 巻きこむ
            w_ = (k + 1) / len(lips)
            css += kf(f'ukLip{k + 1}', [(t_, f'transform:rotate({f(a_ * w_, 3)}deg)') for t_, a_ in LIP_KEYS])
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
            # 波 ぜんたい：ゆっくり もり上がって 前へ せり出す（根もとが 軸）→ ゆっくり もどる
            + kf('ukSurge', [(0, 'transform:translate(0,0) scale(1,1)'), (52, 'transform:translate(4px,0) scale(1.024,1.024)'),
                             (70, 'transform:translate(3px,0) scale(1.016,1.016)'), (100, 'transform:translate(0,0) scale(1,1)')])
            # しぶきの 点：いつもの 点が 前へ とんで 落ちて 消え、見えない 間に もとの 所へ もどって ゆっくり あらわれる・もう 1まいは 巻く ときだけ
            + kf('ukDot1', [(0, 'opacity:1;transform:translate(0,0)'), (46, 'opacity:1;transform:translate(0,0)'), (60, 'opacity:.9;transform:translate(3px,5px)'),
                            (74, 'opacity:0;transform:translate(6px,14px)'), (74.2, 'opacity:0;transform:translate(0,0)'), (100, 'opacity:1;transform:translate(0,0)')])
            + kf('ukDot2', [(0, 'opacity:0;transform:translate(-3px,-6px)'), (52, 'opacity:0;transform:translate(-3px,-6px)'), (60, 'opacity:.95;transform:translate(0,-2px)'),
                            (72, 'opacity:.7;transform:translate(5px,9px)'), (84, 'opacity:0;transform:translate(9px,19px)'), (100, 'opacity:0;transform:translate(9px,19px)')])
            # 波の 上の もや：巻く ときに うしろ（左）へ 吹き飛ぶ
            + kf('ukMist', [(0, 'opacity:0;transform:translate(0,0) scale(.8)'), (40, 'opacity:0;transform:translate(0,0) scale(.8)'), (52, 'opacity:.85;transform:translate(-8px,-2px) scale(1)'),
                            (80, 'opacity:0;transform:translate(-48px,-8px) scale(1.25)'), (100, 'opacity:0;transform:translate(-48px,-8px) scale(1.25)')])
            # 根もとで 白い 泡が はじけて ひろがる・白い しぶき
            + kf('ukFoam', [(0, 'opacity:0;transform:scale(.5,.2)'), (56, 'opacity:0;transform:scale(.5,.2)'), (64, 'opacity:1;transform:scale(1,1)'),
                            (80, 'opacity:.75;transform:translateX(4px) scale(1.25,.86)'), (94, 'opacity:0;transform:translateX(7px) scale(1.42,.7)'), (100, 'opacity:0;transform:translateX(7px) scale(1.42,.7)')])
            + kf('ukBurst', [(0, 'opacity:0;transform:translateY(0) scale(.3)'), (60, 'opacity:0;transform:translateY(0) scale(.3)'), (66, 'opacity:1;transform:translateY(0) scale(1)'),
                             (80, 'opacity:.8;transform:translateY(8px) scale(1.06)'), (92, 'opacity:0;transform:translateY(20px) scale(1.1)'), (100, 'opacity:0;transform:translateY(20px) scale(1.1)')]))
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
    alt='浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（爪のような白い泡の先と、爪から落ちるしぶきの点）、沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走り、ときどきお侍さんとすれちがう。右上に朱の印',
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
               pic='和紙の 地・藍の ぼかしの 空・赤い 日・山なみ・かすみ・「神奈川沖浪裏」の 形の 大波（白い 背中・濃い 藍に 白い すじ・爪の ような 白い 泡・しぶきの 点：'
                   'ゆっくり もり上がって 前へ せり出し、波の 先が しなって 巻きこむ と しぶきが とび 根もとで 泡が はじける）・帆かけ舟・松並木の 街道・朱の 布の 白い 馬（墨の 輪郭）・ときどき すれちがう お侍さん・朱の 印'),
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
