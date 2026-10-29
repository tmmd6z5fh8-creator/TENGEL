"""壁紙パック ⑧浮世絵風（まさちゃんの 指定「大波と街道を走る馬（オリジナルの絵で）」→ 第4.93版「波しぶきと 波の 表現を もっと 海っぽく・9秒に 1回 お侍さん 1人か 2人
   （ランダム）に 出会う」→ 第4.94版「四枚目の 波の 浮世絵を 正確に 参考に・5個目の 動画（実際の 波）の 動きを 参考に」→
   第4.95版「波だけ七枚目の画像と形を全く同じにして！」「波の動きが不自然だから滑らかにもっと自然にして！」→
   第4.96版「浮世絵の赤丸の波はもっと動きを出してリアルにして！波飛沫とか波の高さが変わったりとか！リアルな波の映像から波ができてから消えていく動きを
   勉強して、浮世絵に転用して！」→ 第4.97版「🌊自体をもう少し波の先や小波など丸い絵に変えて！」「小波を作成してを何層か入れ替わりで上下させて波を表現して
   波の動きに合わせて少し大きくなったり、小さくなったりして！あとは潮飛沫の演出入れてリアルにして！」「この赤丸の木のところおかしいから自然に直して！」→
   第4.98版「大波の絵をもう少し可愛く…薄くせず小波にのまれるようにきえるようにして！大波が出てくるのは3秒に一回にして！小波の白いところをもっと細くして！
   小波の先を少し尖らせて！白い丸はけして！小波はもう少しそれぞれが動くようにして！」→
   第4.99版「小波の数減らして、もう少し滑らかにして！」「大波の表現がおかしい やっぱり二枚目のような波にして、リアルで立体的に波がでてきて、消えていく表現にして！」）
   大波は 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波と 同じ 形（まさちゃんの 指定・いちばん 高い 時）。
   第4.99版：第4.98版の かわいい 平らな 大波を やめて 第4.97版の 絵（泡の 爪を 少し まるく）に もどし、ぼかしの かげと 奥行きの ある 動きで 立体的に した。
   上の絵：和紙の 地・空の 上に 藍の ぼかし・赤い 日・藍の ぼかしの 山なみ・かすみ（横の 雲の 帯）。
     左に 神奈川沖浪裏の 大波（make/ukiyoe_great.py：画像から 切りぬいて 浮世絵の 平らな 4つの 色＝白・明るい 青・藍・濃い 藍 に まとめた 絵。
     白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点。空・題箋・落款は すける・舟と 人・富士山は 入れない。
     泡の 爪は 少し まるく・ぼかし（bokashi）で 根もとと 巻きの 下を 濃く・白い 背中の 下を 明るい 青に。体と、波の 先（爪の ある 頭）を 巻きの 強さの じゅんに
     なめらかに ゆがめた 55コマ）。海は 先の 少し とがった 大きめの 小波（細い 白い 泡の かさ・白い 丸は なし）を 1つずつ べつの 部品に した 列 2つ
     （おく＝大波の うしろ・手前＝大波の 前）と 潮しぶき（make/ukiyoe_foam.py の シート）。
     沖に 帆かけ舟。手前に 海ぞいの 街道（松並木・土の 道・草の 土手）。白い 馬（朱の 布と 手綱・墨の 輪郭：pack/make/ukiyoe_art.py）が 街道を 右へ 走る。右上に 朱の 印（白い 蹄鉄）
   動き（波の 一生 3秒で 1回り＝3秒に 1回 大波・奥行きの ある 動き）：
     手前の 小波の うしろの 海から 大波が もり上がり、うしろへ ねて いた 波が 立ち上がって 少し こちらへ 近づく（大きく なる・頭が 立って 爪が のびる）→
     いちばん 高い 時は 神奈川沖浪裏 → 波の 先が 前へ 投げ出されて 爪が 下へ 巻きこみ、波 ぜんたいが 少し こちらへ のりだす（巻きの 下の 水に かげ）・
     しぶきの 点が 前へ とんで 落ち、頭から しぶきと もやが うしろ（左）へ 吹き飛ぶ → 落ちた 所で 潮しぶきが 右から 左へ ふき上がる →
     大波は ふくらむ 手前の 小波の 中へ 沈んで のまれる（うすく しない）→ 次の 波。
     小波は 1つずつ ちがう 長さ・ずれで ゆっくり なめらかに 上下し（かたむかない）、列 ぜんたいは 大波に 合わせて ふくらむ（のみこむ 時が いちばん 大きい）。
     小波の 頭から ときどき 潮しぶきが はねる。舟が ゆれる・かすみが ゆっくり ただよう・街道と 松並木と 土手が 右から 左へ 流れる（馬が 前へ 進んで 見える）。
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


# ---------------------------------------------------------------- 大波（第4.95版 → 第4.99版：まさちゃん「やっぱり二枚目のような波にして、リアルで立体的に波がでてきて、消えていく表現にして！」）
# 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波を 画像から 切りぬいて 浮世絵の 平らな 4つの 色（白・明るい 青・藍・濃い 藍）に まとめた 絵
# （make/ukiyoe_great.py：空・題箋・落款は すける・舟と 人・富士山は 入れない・泡の 爪を 少し まるく（第4.97版）・ぼかしで 立体の かげ（第4.99版））。
# 絵は 体（body）・爪の 下の しぶきの 点（dots）と、波の 先（爪の ある 頭）を 巻きの 強さ c の じゅんに ゆがめた 55コマ
# （crest：c＝−1 立つ 前 → 0 神奈川沖浪裏 → 1 投げ出す → 1.6 落ちる）。
# 波の 一生 3秒（第4.98版 まさちゃん「大波が出てくるのは3秒に一回にして！」「薄くせず小波にのまれるようにきえるようにして！」）を 奥行きの ある 動きで：
#   ① 海の 中から もり上がる（c＝−1 → 0）：手前の 小波の うしろから 立ち上がる（はやく 出て 上で ゆっくり）・うしろへ ねて いた 波が 立つ
#      （rotateX：上が 奥 → まっすぐ）・少し こちらへ 近づいて 大きく なる
#   ② いちばん 高い（c＝0：神奈川沖浪裏）・少し せり出す
#   ③ 波の 先が 前へ 投げ出される（c＝0 → 1）：波 ぜんたいが こちらへ のりだす（rotateX：上が 手前・少し 大きく）・巻きの 下の 水に かげ（.ukSh）・
#      爪の 下の しぶきの 点が 前へ とんで 落ちる・頭から しぶきと もやが うしろへ 吹き飛ぶ
#   ④ 落ちる（c＝1 → 1.6）・落ちた 所で 潮しぶきが 右から 左へ ふき上がる
#   ⑤ ふくらむ 手前の 小波の 中へ 沈んで のまれる（こさは かえない＝すけない）⑥ しずか → ①
#   体・点・頭の コマは 同じ 箱（.ukWg）の 中＝高さ・かたむき・奥行き・沈む のは 箱の transform（0.05秒ごとの 点を まっすぐ つなぐ）で なめらかに。
#   頭の コマは step-end で 入れかえ（すけて 形を 入れかえる こと なし）
WB = (-22, 2)                          # 上の絵の 中の 波の 箱（260×175）の 左上（第4.97版と 同じ）
WG_O = (117.0, 175.0)                  # 波の 箱の 中の 回す・ちぢめる 中心（根もと）
PERSP = 520                            # 奥行き（perspective の px）
WAVE_T = 3.0                           # 波の 一生 1回りの 秒
W_RISE, W_PEAK, W_PITCH = (0.0, 0.95), (0.95, 1.35), (1.35, 1.75)    # もり上がる・いちばん 高い・波の 先が 投げ出される（秒）
W_FALL, W_SINK = (1.75, 2.25), (1.95, 2.85)                          # 頭が 落ちる（c 1 → 1.45）・小波に のまれて 沈む（だんだん はやく）
# 波の 箱の 形（右へ px・下へ px・横の 大きさ・高さ・かたむき°（skewX）・前後の かたむき°（rotateX：＋＝上が 奥へ ねる・−＝上が こちらへ のりだす））：根もとが 軸
WG_LOW = (-4.0, 18.0, .9, .5, 4.0, 20.0)         # 海の 中（低い うねり：手前の 小波の うしろに かくれる ぎりぎり・うしろへ ねて 遠い）
WG_PEAK = (0.0, 0.0, 1.0, 1.0, 0.0, 0.0)         # 神奈川沖浪裏
WG_PEAK2 = (1.5, 1.5, 1.012, 1.012, 0.0, -1.5)    # いちばん 高い まま 少し せり出す
WG_PITCH = (3.5, 9.0, 1.03, 1.0, -3.0, -7.0)     # 波の 先を 投げ出して こちらへ のりだす（上の はしが 切れない）
WG_SUNK = (7.0, 30.0, 1.05, .52, -6.0, -12.0)    # くずれて 低く なり 小波に のまれた（手前の 小波の うしろに かくれる ぎりぎり）
C_FALL = .45                           # 頭が 落ちる 強さ（c＝1 → 1.45：沈みながら 落ちる ので 落としすぎない）
PEEL = [(1.85, 206, 1.15), (1.95, 182, 1.05), (2.05, 158, .95), (2.15, 134, .9)]   # 波の 先が 落ちた 所で 潮しぶきが ふき上がる（時・上の絵の x・大きさ：右から 左へ）
SH = (138, 90, 124, 26)                # 巻きの 下の 水の かげ（左・上・はば・高さ：手前の 小波の 上に のる）
FOAM_W, FOAM_L, FOAM_M, FOAM_LINE = '#F6F1E3', '#B2C7DE', '#5470A0', '#1B255C'   # 浮世絵の 平らな 色（大波の 絵と 同じ）


def _hexmix(a, b, t):
    """2つの 色（#RRGGBB）の あいだ"""
    a_ = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b_ = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join('%02X' % round(x + (y - x) * t) for x, y in zip(a_, b_))


def _ss(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- 小波（第4.97版 → 第4.98版 → 第4.99版：まさちゃん「小波の数減らして、もう少し滑らかにして！」）
# 先の 少し とがった 小波（右へ 巻く 頭・細い 白い 泡の かさ（先へ むかって 細く とがる）・巻きの かげ・明るい すじ・白い 丸は なし：第4.98版と 同じ 形）を
# 1つずつ べつの 部品に して 横に ならべた 列 2つ（おく＝大波の うしろ・手前＝大波の 前：大波は 手前の 列の 中へ 沈む）。
# 第4.99版：数を へらして（2列で 13こ）1つずつ 大きく・動きは ゆっくり なめらかに（1つずつ ちがう 長さ 2.6〜3.8秒・ずれで 上下と 少し ふくらむ だけ・かたむかない）。
# 列の うしろに 体の つづきの 帯（すき間が 出ない）。列 ぜんたいは 波の 一生に 合わせて ふくらむ（大波を のみこむ 時が いちばん 大きく、そのあと しずまる）
# （top：上の絵の y・H：列の 高さ・w：波 1つの はば・h：頭の 高さ・haze：かすみ・lw：線・bob：上下 px・sy／sx：ふくらみ）
ROW_W, ROW_X = 430, -20               # 列の はば と 左の はし
ROWS = [dict(top=82, H=34, w=64, h=12.0, seed=7, haze=.22, lw=.6, bob=.9, sy=(.95, 1.12), sx=.015),
        dict(top=92, H=27, w=78, h=16.0, seed=8, haze=0.0, lw=.75, bob=1.3, sy=(.9, 1.32), sx=.025)]
SW_N = 3                              # 列ごとの 波の 形の 数
SW_PAD = 3                            # 波の 部品の 上の よゆう（px）


def row_cols(k):
    """列 k の 色（上・まん中・下・泡・線・すじ・巻きの かげ）"""
    hz = ROWS[k]['haze']
    return (_hexmix('#86A7C9', '#F1E6CF', hz * .6), _hexmix('#3E5F94', '#C9D3DE', hz * .7), _hexmix(AI['d'], '#9DB2C9', hz * .7),
            _hexmix(FOAM_W, '#F1E6CF', hz * .3), _hexmix(FOAM_LINE, '#7D8FB0', hz * .7), _hexmix(FOAM_L, '#E6E3D8', hz * .5),
            _hexmix('#24356E', '#8FA2C2', hz * .7))


def row_base(k):
    return ROWS[k]['h'] + 2.5


def sw_shapes(k):
    """列 k の 波の 形 SW_N こ：[(はば（整数 px）, 頭の 高さ)]"""
    p = ROWS[k]
    R = rnd(p['seed'])
    return [(int(round(p['w'] * R.uniform(.9, 1.1))), p['h'] * R.uniform(.88, 1.1)) for _ in range(SW_N)]


def row_layout(k):
    """列 k の 波の ならび：[(左の x, 形, 上下の 1回り 秒, ずらす 秒, しぶき)]（ROW_W を うめる・となりと 同じ 形に しない）"""
    p, sh = ROWS[k], sw_shapes(k)
    R = rnd(p['seed'] + 100)
    x, out, i, v = -int(R.uniform(0, p['w'] * .4)), [], 0, -1
    while x < ROW_W:
        v = (v + 1 + R.randrange(SW_N - 1)) % SW_N
        dur = R.uniform(2.6, 3.8)
        out.append((x, v, dur, -R.uniform(0, 2 * dur), k == len(ROWS) - 1 and i % 2 == 1))
        x += sh[v][0]
        i += 1
    return out


def _grad_at(k, y):
    """列 k の 体の 色（上の絵の 列の 中の y）"""
    top_c, mid_c, bot_c = row_cols(k)[:3]
    p = ROWS[k]
    ym = p['h'] * .9
    if y <= ym:
        return _hexmix(top_c, mid_c, max(0.0, y) / ym)
    return _hexmix(mid_c, bot_c, min(1.0, (y - ym) / (p['H'] - ym)))


def wavelet_parts(x0, base, w, h):
    """小さな 波 1つ（右へ 巻く・先が 少し とがる）→ (体の ふち・泡の かさ・巻きの かげ・明るい すじ)"""
    cx, top = x0 + 0.55 * w, base - h
    tx, ty = x0 + 0.93 * w, base - 0.40 * h          # 先（とがり）
    ix, iy = x0 + 0.76 * w, base - 0.30 * h          # 巻きの 内がわ
    edge = (f"C{f(x0 + 0.22 * w)} {f(base - 0.04 * h)} {f(x0 + 0.33 * w)} {f(top + 0.10 * h)} {f(cx)} {f(top)} "
            f"C{f(cx + 0.20 * w)} {f(top - 0.04 * h)} {f(tx + 0.02 * w)} {f(top + 0.20 * h)} {f(tx)} {f(ty)} "
            f"C{f(tx - 0.05 * w)} {f(ty - 0.08 * h)} {f(ix + 0.06 * w)} {f(iy - 0.10 * h)} {f(ix)} {f(iy)} "
            f"C{f(ix - 0.02 * w)} {f(iy + 0.22 * h)} {f(x0 + 0.86 * w)} {f(base)} {f(x0 + w)} {f(base)} ")
    t = 0.17 * h                                     # 泡の かさの いちばん 太い 所（細く）
    fx0, fy0 = x0 + 0.30 * w, base - 0.62 * h
    foam = (f"M{f(fx0)} {f(fy0)} C{f(x0 + 0.38 * w)} {f(top + 0.20 * h)} {f(x0 + 0.45 * w)} {f(top + 0.03 * h)} {f(cx)} {f(top)} "
            f"C{f(cx + 0.20 * w)} {f(top - 0.04 * h)} {f(tx + 0.02 * w)} {f(top + 0.20 * h)} {f(tx)} {f(ty)} "
            f"C{f(tx - 0.03 * w)} {f(top + 0.30 * h + t)} {f(cx + 0.10 * w)} {f(top + t * 1.1)} {f(cx)} {f(top + t)} "
            f"C{f(x0 + 0.45 * w)} {f(top + t * 1.05)} {f(x0 + 0.38 * w)} {f(top + 0.25 * h + t * .5)} {f(fx0)} {f(fy0)} Z")
    curl = (f"M{f(tx)} {f(ty)} C{f(tx - 0.05 * w)} {f(ty - 0.08 * h)} {f(ix + 0.06 * w)} {f(iy - 0.10 * h)} {f(ix)} {f(iy)} "
            f"C{f(ix - 0.02 * w)} {f(iy + 0.16 * h)} {f(x0 + 0.84 * w)} {f(base - 0.16 * h)} {f(x0 + 0.92 * w)} {f(base - 0.18 * h)} "
            f"C{f(x0 + 0.84 * w)} {f(iy + 0.06 * h)} {f(ix + 0.02 * w)} {f(iy - 0.02 * h)} {f(tx)} {f(ty)} Z")
    streak = f"M{f(x0 + 0.40 * w)} {f(base - 0.20 * h)} Q{f(x0 + 0.58 * w)} {f(top + 0.62 * h)} {f(x0 + 0.70 * w)} {f(iy + 0.05 * h)}"
    return edge, foam, curl, streak


def small_wave_svg(k, v):
    """列 k の 波の 形 v（1つの 部品）→ (svg, はば, 高さ)：左右に 1px・上に SW_PAD の よゆう・下は 根もとの 6px 下まで（うしろの 帯と 重なる）"""
    p = ROWS[k]
    ww, hh = sw_shapes(k)[v]
    top_c, mid_c, bot_c, foam_c, line_c, st_c, curl_c = row_cols(k)
    base = row_base(k) + SW_PAD
    W_, H_ = ww + 2, int(math.ceil(base + 6))
    ym = p['h'] * .9
    defs = (f"<linearGradient id='g' x1='0' y1='{f(SW_PAD, 2)}' x2='0' y2='{f(p['H'] + SW_PAD, 2)}' gradientUnits='userSpaceOnUse'>"
            f"<stop offset='0' stop-color='{top_c}'/><stop offset='{f(ym / p['H'], 3)}' stop-color='{mid_c}'/><stop offset='1' stop-color='{bot_c}'/></linearGradient>")
    e, fm, cu, st = wavelet_parts(1, base, ww, hh)
    body = f"M1 {f(H_)} L1 {f(base)} " + e + f"L{f(1 + ww)} {f(H_)} Z"
    o = (f"<path d='{body}' fill='url(#g)'/>"
         f"<path d='M1 {f(base)} {e}' fill='none' stroke='{line_c}' stroke-width='{f(p['lw'])}' stroke-linejoin='round' stroke-linecap='round'/>"
         f"<path d='{cu}' fill='{curl_c}' opacity='.75'/>"
         f"<path d='{st}' fill='none' stroke='{st_c}' stroke-width='{f(p['lw'] * 1.2)}' stroke-linecap='round' opacity='.8'/>"
         f"<path d='{fm}' fill='{foam_c}' stroke='{line_c}' stroke-width='{f(p['lw'] * .8)}' stroke-linejoin='miter'/>")
    return doc(W_, H_, o, defs=defs), W_, H_


def puff_svg(seed=51, w=40, h=26):
    """小波の 頭から はねる 潮しぶき（右下の 頭から 左上へ ひらく 白い つぶと うすい もや）"""
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='2'/></filter>"
    R = rnd(seed)
    o = (f"<ellipse cx='{w - 17}' cy='{h - 10}' rx='12' ry='5.5' fill='#FFFFFF' opacity='.42' filter='url(#bl)' transform='rotate(-20 {w - 17} {h - 10})'/>"
         f"<ellipse cx='{w - 27}' cy='{h - 15}' rx='7' ry='3.5' fill='#FFFFFF' opacity='.3' filter='url(#bl)'/>")
    for i in range(28):
        a = math.radians(R.uniform(-172, -92))
        d = R.uniform(2, 22) ** .92
        x, y = w - 7 + math.cos(a) * d * 1.3, h - 3 + math.sin(a) * d * .85
        if 0 < x < w and 0 < y < h:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.55, 1.35) * (1.15 - d / 40))}' fill='#FBFAF4' opacity='{f(R.uniform(.75, 1))}'/>"
    return doc(w, h, o, defs=defs)


def burst_svg(seed=11, w=90, h=70):
    """くずれた ときに はねる しぶき（下の まん中から 上へ ひらく 白い 点・うすい もや）"""
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='3.2'/></filter>"
    R = rnd(seed)
    o = (f"<ellipse cx='{w / 2}' cy='{h - 18}' rx='24' ry='13' fill='#FFFFFF' opacity='.4' filter='url(#bl)'/>"
         f"<ellipse cx='{w / 2 - 14}' cy='{h - 34}' rx='15' ry='8' fill='#FFFFFF' opacity='.28' filter='url(#bl)'/>")
    for i in range(80):
        a = math.radians(R.uniform(-160, -20))
        d = R.uniform(4, 62) ** .95
        x, y = w / 2 + math.cos(a) * d * .9, h - 4 + math.sin(a) * d
        if 0 < x < w and 0 < y < h:
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.6, 1.7))}' fill='#FBFAF4' opacity='{f(R.uniform(.7, 1))}'/>"
    return doc(w, h, o, defs=defs)


def mist_svg(w=90, h=40):
    """波の 上から うしろへ 吹きとぶ もや（ぼかした 白）"""
    defs = "<filter id='bl' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='4'/></filter>"
    o = ("<ellipse cx='60' cy='22' rx='26' ry='9' fill='#FFFFFF' opacity='.55' filter='url(#bl)'/>"
         "<ellipse cx='36' cy='18' rx='22' ry='8' fill='#FFFFFF' opacity='.42' filter='url(#bl)'/>"
         "<ellipse cx='16' cy='22' rx='14' ry='6' fill='#FFFFFF' opacity='.3' filter='url(#bl)'/>")
    return doc(w, h, o, defs=defs)


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


PN_UP = 20                 # 松並木の 絵の 上の よゆう（第4.97版：まさちゃん「この赤丸の木のところおかしいから自然に直して！」＝高い 松の てっぺんの 葉が
                           #   絵の 上の はしで 切れて、平たい 黒い 刃の ように 見えて いた → 絵を 上へ 20px 高く して 葉を ぜんぶ 描く）
PN_H = 62 + PN_UP


def pines_svg():
    """松並木（街道の むこうがわ・くり返し）と 石の 土手。上に PN_UP の よゆう（いちばん 高い 松の てっぺんの 葉まで 切れずに 入る）"""
    u = PN_UP
    o = (f"<path d='M0 {54 + u} H{TILE} V{62 + u} H0 Z' fill='#9A8C70'/><path d='M0 {54 + u} H{TILE} V{55.6 + u} H0 Z' fill='#B9AD92'/>")
    for i in range(14):                                                     # 石がき の 目地
        x = i * TILE / 14
        o += f"<path d='M{f(x)} {55.6 + u} V{62 + u}' stroke='#7A6C52' stroke-width='.7'/>"
    for x, h, lean in ((40, 50, .5), (130, 62, -.3), (215, 46, .4), (300, 58, .2), (372, 52, -.4)):
        for xx in _wrap(x, pad=40):
            o += pine(xx, 56 + u, h, lean)
    return doc(TILE, PN_H, o)


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


# ---------------------------------------------------------------- 波の 一生（3秒）の 時の ながれ
PF_T = (3.3, 4.5, 5.7)                # 小波の 頭の しぶきの くり返し（秒）


def _pc(t):
    return t / WAVE_T * 100


def _lerp(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def _mix(a, b, us):
    """2つの 形の あいだ（成分ごとに ちがう すすみ）"""
    return tuple(x + (y - x) * u for x, y, u in zip(a, b, us))


def wave_state(t):
    """t 秒の 波の 箱の 形（右へ・下へ・横・高さ・かたむき・前後の かたむき）。こさは かえない（小波に のまれて 消える）"""
    if t < W_RISE[0]:
        return WG_LOW
    if t < W_RISE[1]:                     # 海の 中から：ゆっくり 出て、まん中で はやく、上で ゆっくり 立つ（波が できる）・立ち上がって 近づく のも なめらかに
        u = (t - W_RISE[0]) / (W_RISE[1] - W_RISE[0])
        e, s = .5 - .5 * math.cos(math.pi * u ** .8), _ss(u)
        return _mix(WG_LOW, WG_PEAK, (s, e, s, e, s, _ss(min(1.0, u * 1.12))))
    if t < W_PEAK[1]:
        return _lerp(WG_PEAK, WG_PEAK2, _ss((t - W_PEAK[0]) / (W_PEAK[1] - W_PEAK[0])))
    if t < W_PITCH[1]:
        return _lerp(WG_PEAK2, WG_PITCH, _ss((t - W_PITCH[0]) / (W_PITCH[1] - W_PITCH[0])))
    if t < W_SINK[0]:
        return WG_PITCH
    if t < W_SINK[1]:                     # くずれて 沈む：はじめは ゆっくり、だんだん はやく 小波の 中へ
        return _lerp(WG_PITCH, WG_SUNK, ((t - W_SINK[0]) / (W_SINK[1] - W_SINK[0])) ** 1.5)
    if t < WAVE_T - .02:                 # 沈みきった あと 見えない 所で 次の 波の はじめの 形へ
        return _lerp(WG_SUNK, WG_LOW, _ss((t - W_SINK[1]) / (WAVE_T - .02 - W_SINK[1])))
    return WG_LOW


def life_stops(step=.05):
    """波の 箱の transform（0.05秒ごとの 点を まっすぐ つなぐ＝なめらか）。こさは いつも 1"""
    out, t = [], 0.0
    while t < WAVE_T + 1e-6:
        tx, ty, sx, sy, sk, rx = wave_state(t)
        out.append((_pc(t), f'transform:translate({f(tx, 2)}px,{f(ty, 2)}px) perspective({PERSP}px) rotateX({f(rx, 2)}deg) '
                            f'skewX({f(sk, 2)}deg) scale({f(sx, 4)},{f(sy, 4)})'))
        t = round(t + step, 6)
    return out


def crest_c(t):
    """t 秒の 巻きの 強さ c（もり上がる −1→0・いちばん 高い 0・投げ出す 0→1・落ちる 1→1.6）"""
    if t < W_RISE[0]:
        return -1.0
    if t < W_RISE[1]:
        return -1 + _ss((t - W_RISE[0]) / (W_RISE[1] - W_RISE[0]))
    if t < W_PITCH[0]:
        return 0.0
    if t < W_PITCH[1]:
        return ((t - W_PITCH[0]) / (W_PITCH[1] - W_PITCH[0])) ** 1.4
    if t < W_FALL[1]:
        return 1 + C_FALL * _ss((t - W_FALL[0]) / (W_FALL[1] - W_FALL[0]))
    if t < W_SINK[1] + .05:
        return 1 + C_FALL
    return -1.0


def crest_stops(cs, cols, fw, fh):
    """頭の コマ：それぞれの コマを、c が その コマと となりの コマの まん中を こえた 時から 出す（step-end）。沈みきった あと はじめの コマへ"""
    ts = [i * 0.005 for i in range(int(WAVE_T * 200) + 1)]
    cv = [crest_c(t) for t in ts]
    out = []
    for i in range(len(cs)):
        if i == 0:
            t0 = 0.0
        else:
            mid = (cs[i - 1] + cs[i]) / 2
            t0 = next((t for t, c in zip(ts, cv) if c >= mid - 1e-9 and t > 0), WAVE_T)
        r, q = divmod(i, cols)
        out.append((t0, f'background-position:{f(-q * fw, 3)}px {f(-r * fh, 3)}px'))
    out.sort(key=lambda x: x[0])
    t_back = W_SINK[1] + .05                   # 見えない 所で はじめの コマへ もどす
    out.append((t_back, f'background-position:0px 0px'))
    stops, seen = [], set()
    for t0, d in out:
        p = round(_pc(t0), 3)
        if p in seen:
            stops[-1] = (p, d)
            continue
        seen.add(p)
        stops.append((p, d))
    return stops


def _win(name, keys):
    """[(秒, 宣言)] → @keyframes（はしの 0% と 100% を 足す）"""
    st = [(_pc(t), d) for t, d in keys]
    if st[0][0] > 0:
        st.insert(0, (0, keys[0][1]))
    if st[-1][0] < 100:
        st.append((100, keys[-1][1]))
    return kf(name, st)


def sea_amp(t):
    """t 秒の 海の ふくらみ（0〜1）：大波が もり上がる 間に ふえ、くずれた 大波を のみこむ 時（2.45秒）が いちばん 大きく、そのあと しずまる（3秒で 1回り・つなぎめで 同じ）"""
    if t < W_RISE[1]:
        return .25 + .3 * _ss((t - W_RISE[0]) / (W_RISE[1] - W_RISE[0]))
    if t < W_PITCH[1]:
        return .55 + .2 * _ss((t - W_PEAK[0]) / (W_PITCH[1] - W_PEAK[0]))
    if t < 2.45:
        return .75 + .25 * _ss((t - W_PITCH[1]) / (2.45 - W_PITCH[1]))
    if t < 2.98:
        return 1.0 - .75 * _ss((t - 2.45) / .53)
    return .25


def row_stops(k, step=.1):
    """小波の 列 k の ふくらみ（根もとが 軸：高さ sy・横 sx）＝ 0.1秒ごとの 点"""
    p = ROWS[k]
    (s0, s1), sx = p['sy'], p['sx']
    out, t = [], 0.0
    while t < WAVE_T + 1e-6:
        a = sea_amp(t)
        out.append((_pc(t), f'transform:scale({f(1 + sx * a, 4)},{f(s0 + (s1 - s0) * a, 4)})'))
        t = round(t + step, 6)
    return out


def shade_stops(step=.1):
    """巻きの 下の 水の かげ（こさ・はば・波と いっしょに 右へ）：波が 立つ と 出て、こちらへ のりだす 時が いちばん 濃く、沈むと 消える（どれも 0.3秒 以上 かけて）"""
    out, t = [], 0.0
    while t < WAVE_T + 1e-6:
        if t < .45:
            a = 0.0
        elif t < W_PEAK[0]:
            a = .3 * _ss((t - .45) / (W_PEAK[0] - .45))
        elif t < W_PITCH[1]:
            a = .3 + .2 * _ss((t - W_PEAK[0]) / (W_PITCH[1] - W_PEAK[0]))
        elif t < 2.05:
            a = .5
        elif t < 2.6:
            a = .5 * (1 - _ss((t - 2.05) / .55))
        else:
            a = 0.0
        tx = wave_state(t)[0]
        out.append((_pc(t), f'opacity:{f(a, 3)};transform:translateX({f(tx, 2)}px) scaleX({f(.8 + .4 * a, 3)})'))
        t = round(t + step, 6)
    return out


def wave_life_css():
    """しぶきの 点・頭から 吹き飛ぶ しぶきと もや・落ちた 所で ふき上がる しぶき・巻きの 下の かげ・小波の 列の ふくらみ と 1つずつの 上下・小波の 頭の しぶき
       （白く なるのは どれも 0.3秒 以上 かけて）"""
    o0 = 'opacity:0'
    css = ''
    # 爪の 下の しぶきの 点（神奈川沖浪裏の 点）：もり上がる 終わりに 爪の 下に あらわれ、投げ出す ときに 前へ とんで 落ちる・もう 1まいは 投げ出す ときだけ
    css += _win('ukDot1', [(0, f'{o0};transform:translate(-4px,-8px)'), (.55, f'{o0};transform:translate(-4px,-8px)'), (.9, 'opacity:1;transform:translate(0,0)'),
                           (1.35, 'opacity:1;transform:translate(0,0)'), (1.75, 'opacity:.9;transform:translate(5px,9px)'),
                           (2.15, f'{o0};transform:translate(11px,22px)'), (2.2, f'{o0};transform:translate(-4px,-8px)')])
    css += _win('ukDot2', [(0, f'{o0};transform:translate(-4px,-9px)'), (1.35, f'{o0};transform:translate(-4px,-9px)'), (1.65, 'opacity:.95;transform:translate(-1px,-3px)'),
                           (1.95, 'opacity:.7;transform:translate(6px,11px)'), (2.3, f'{o0};transform:translate(12px,24px)')])
    # 頭から うしろ（左）へ 吹き飛ぶ しぶき（点の 帯）と もや
    for nm, t0 in (('ukSp1', 1.05), ('ukSp2', 1.45)):
        css += _win(nm, [(0, f'{o0};transform:translate(0,0) scale(.5)'), (t0, f'{o0};transform:translate(0,0) scale(.5)'),
                         (t0 + .35, 'opacity:1;transform:translate(-5px,-2px) scale(.95)'), (t0 + .9, 'opacity:.75;transform:translate(-20px,-7px) scale(1.25)'),
                         (t0 + 1.45, f'{o0};transform:translate(-34px,-11px) scale(1.5)')])
    for nm, t0 in (('ukMs1', 1.15), ('ukMs2', 1.5)):
        css += _win(nm, [(0, f'{o0};transform:translate(0,0) scale(.8)'), (t0, f'{o0};transform:translate(0,0) scale(.8)'),
                         (t0 + .45, 'opacity:.85;transform:translate(-8px,-3px) scale(1.05)'), (t0 + 1.35, f'{o0};transform:translate(-42px,-9px) scale(1.35)')])
    # 波の 先が 落ちた 所で ふき上がる 潮しぶき（右から 左へ じゅんに：手前の 小波の うしろから ふき上がって、つぶが 落ちて 左へ 流れる）
    for k, (t0, x, sc) in enumerate(PEEL):
        css += _win(f'ukBu{k}', [(0, f'{o0};transform:translate(0,5px) scale({f(.3 * sc, 3)})'), (t0, f'{o0};transform:translate(0,5px) scale({f(.3 * sc, 3)})'),
                                 (t0 + .3, f'opacity:.95;transform:translate(-1px,0) scale({f(.8 * sc, 3)})'),
                                 (t0 + .45, f'opacity:.9;transform:translate(-3px,-3px) scale({f(.95 * sc, 3)})'),
                                 (t0 + .8, f'{o0};transform:translate(-7px,2px) scale({f(1.1 * sc, 3)})')])
    css += kf('ukShd', shade_stops())
    # 小波の 列：ふくらみ（3秒）・波 1つずつの ゆっくりした 上下と 少しの ふくらみ（かたむかない）
    for k, p in enumerate(ROWS):
        b = p['bob']
        css += kf(f'ukRwL{k}', row_stops(k))
        css += kf(f'ukS{k}', [(0, f'transform:translateY({f(-b)}px) scaleY(1.035)'), (100, f'transform:translateY({f(b)}px) scaleY(.965)')])
    # 小波の 頭から はねる しぶき（くり返しの 長さ 3つ・どれも 0.35秒で あらわれて 1.15秒で 消える：上へ はねて 左へ 流れる）
    for j, P_ in enumerate(PF_T):
        q = lambda s_: s_ / P_ * 100
        css += kf(f'ukPf{j}', [(0, f'{o0};transform:translate(0,2px) scale(.45)'), (q(.35), 'opacity:.95;transform:translate(-2px,-2px) scale(.85)'),
                               (q(.75), 'opacity:.7;transform:translate(-6px,-6px) scale(1.05)'), (q(1.15), f'{o0};transform:translate(-11px,-3px) scale(1.2)'),
                               (100, f'{o0};transform:translate(-11px,-3px) scale(1.2)')])
    return css


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（白い背中、濃い藍に白いすじ、'
           'まるい爪のような白い泡の先、爪から落ちるしぶきの点。根もとと巻きの下は濃い藍のぼかし）。三秒ごとに、手前の小波のうしろの海から大波が立ち上がって'
           '少しこちらへ近づき、いちばん高くなると波の先が前へ投げ出されて爪が下へ巻きこみ、こちらへのりだす。しぶきの点が前へとび、頭からしぶきともやがうしろへ吹き飛び、'
           '落ちた所で潮しぶきがふき上がって、大波はふくらんだ手前の小波の中へ沈んでのまれ、また次の波が立ち上がる。'
           '海は先の少しとがった大きめの小波が二列にならび、ひとつずつゆっくり上下し、大波の動きに合わせてふくらんだりしずまったりする。小波の頭からもときどき潮しぶきがはねる。'
           '沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走る。'
           'ときどき街道のむこうから、ちょんまげに羽織と袴、刀を二本さしたお侍さんが一人か二人歩いてきて、馬とすれちがうときに会釈する。右上に朱の印のイラスト')
    foam = B.get('foam')                     # 小波・しぶき（make/ukiyoe_foam.py の 絵の シート）
    parts = foam['parts'] if foam else {}

    def row(k):                              # 波 1つずつの クラスは uw0…（アプリの 枠の 色の クラス .w1〜.w8 と ぶつけない）
        if f'sw{k}0' not in parts:
            return ''
        o = f'<i class="ukRw r{k}"><i class="bd"></i>'
        for i, (x, v, dur, dl, pf) in enumerate(row_layout(k)):
            o += f'<i class="sw ukF sw{k}{v} uw{i}">' + (f'<i class="pf ukF pf{i % 2}"></i>' if pf and 'pf0' in parts else '') + '</i>'
        return o + '</i>'

    html = f'<div class="ukw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ukSky', sky_svg()) + img('ukKs', kasumi_svg()) + img('ukSea', sea_svg())
    html += row(0)                           # おくの 小波（大波と 舟の うしろ）
    html += img('ukBt', boat_svg())
    wave, crest = B.get('wave'), B.get('crest')
    if wave:                                 # 神奈川沖浪裏の 大波（make/ukiyoe_great.py：体・頭の コマ・しぶきの 点）
        html += ('<i class="ukWg"><i class="ukW body"></i>' + ('<i class="ukCf"></i>' if crest else '')
                 + '<i class="ukW dots d1"></i><i class="ukW dots d2"></i></i>')
    if 'sp1' in parts:
        html += '<i class="ukSp s1 ukF sp1"></i><i class="ukSp s2 ukF sp2"></i>'
    html += img('ukMs m1', mist_svg()) + img('ukMs m2', mist_svg())
    if 'bs0' in parts:                       # 波の 先が 落ちた 所で ふき上がる しぶき（右から 左へ）
        html += ''.join(f'<i class="ukBu u{k} ukF bs{k % 2}"></i>' for k in range(len(PEEL)))
    html += row(1)                           # 手前の 小波（大波は この 中へ 沈む）
    html += '<i class="ukSh"></i>'           # 巻きの 下の 水の かげ（波の 先が のりだす と 手前の 小波が かげる＝立体）
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
           f'.ukw .ukMs{{width:90px;height:40px;opacity:0}}.ukw .ukMs.m1{{left:112px;top:-6px;animation:ukMs1 {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukMs.m2{{left:146px;top:2px;animation:ukMs2 {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukSp{{left:87px;top:-18px;width:84px;height:44px;opacity:0;transform-origin:78px 32px}}'
           f'.ukw .ukSp.s1{{animation:ukSp1 {f(WAVE_T)}s linear infinite}}.ukw .ukSp.s2{{top:-12px;animation:ukSp2 {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukSh{{left:{SH[0]}px;top:{SH[1]}px;width:{SH[2]}px;height:{SH[3]}px;border-radius:50%;opacity:0;'
           'background:radial-gradient(closest-side,rgba(16,24,60,.62),rgba(16,24,60,.3) 55%,rgba(16,24,60,0));'
           f'animation:ukShd {f(WAVE_T)}s linear infinite}}'
           # 小波の 列（外：ふくらみ・bd：うしろの 帯・sw：波 1つずつ）
           f'.ukw .ukRw{{left:{ROW_X}px;width:{ROW_W}px;transform-origin:50% 100%}}'
           '.ukw .ukRw i{position:absolute;display:block}'
           '.ukw .ukRw .pf{width:40px;height:26px;opacity:0;transform-origin:33px 23px}'
           '.ukw .ukBu{width:90px;height:70px;opacity:0;transform-origin:45px 66px}'
           + ''.join(f'.ukw .ukBu.u{k}{{left:{f(x - 45)}px;top:34px;animation:ukBu{k} {f(WAVE_T)}s linear infinite}}' for k, (t0, x, sc) in enumerate(PEEL))
           + f'.ukw .ukPn{{left:0;top:{56 - PN_UP}px;width:{2 * TILE}px;height:{PN_H}px;background-size:{TILE}px {PN_H}px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * 1.12, 3)}s linear infinite}}'
           f'.ukw .ukRd{{left:0;top:116px;width:{2 * TILE}px;height:26px;background-size:{TILE}px 26px;background-repeat:repeat-x;animation:ukFlow {ROAD_S}s linear infinite}}'
           f'.ukw .ukBk{{left:0;top:136px;width:{2 * TILE}px;height:28px;background-size:{TILE}px 28px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * .82, 3)}s linear infinite}}'
           '.ukw .ukSl{left:364px;top:6px;width:18px;height:18px}'
           f'.ukw .ukSm{{left:0;top:{f(SM_TOP)}px;width:{f(SM_W * SM_K)}px;height:{f(SM_H * SM_K)}px;overflow:hidden;transform:translateX(500px)}}'
           f'.ukw .ukSm>i{{position:absolute;display:block;left:0;top:0;height:{f(SM_H * SM_K)}px;background-repeat:no-repeat}}'
           f'.ukw .ukSm .w{{width:{f(12 * SM_W * SM_K)}px}}.ukw .ukSm .b{{width:{f(len(BOW) * SM_W * SM_K)}px;opacity:0}}')
    for k, p in enumerate(ROWS):                # 列ごとの 場所・うしろの 帯・波 1つずつの 場所と 動き（長さ・ずれが ばらばら）
        base = row_base(k)
        hh_ = int(math.ceil(base + SW_PAD + 6))
        css += (f'.ukw .ukRw.r{k}{{top:{p["top"]}px;height:{p["H"]}px;animation:ukRwL{k} {f(WAVE_T)}s linear infinite}}'
                f'.ukw .ukRw.r{k} .bd{{left:0;top:{f(base - .6, 2)}px;width:{ROW_W}px;height:{f(p["H"] - base + .6, 2)}px;'
                f'background:linear-gradient({_grad_at(k, base - .6)},{_grad_at(k, p["H"])})}}'
                f'.ukw .ukRw.r{k} .sw{{top:{-SW_PAD}px;height:{hh_}px;transform-origin:50% {f(base + SW_PAD, 2)}px}}')
        shapes = sw_shapes(k)
        css += ''.join(f'.ukw .ukRw.r{k} .sw{k}{v}{{width:{ww + 2}px}}' for v, (ww, hh) in enumerate(shapes))
        R = rnd(p['seed'] + 200)
        for i, (x, v, dur, dl, pf) in enumerate(row_layout(k)):
            css += f'.ukw .ukRw.r{k} .uw{i}{{left:{x - 1}px;animation:ukS{k} {f(dur, 2)}s ease-in-out {f(dl, 2)}s infinite alternate}}'
            if pf:
                ww, hh = shapes[v]
                j = i % len(PF_T)
                css += (f'.ukw .ukRw.r{k} .uw{i} .pf{{left:{f(1 + .6 * ww - 33, 2)}px;top:{f(SW_PAD + base - hh - 23 + 2, 2)}px;'
                        f'animation:ukPf{j} {f(PF_T[j])}s linear {f(-R.uniform(0, PF_T[j]), 2)}s infinite}}')
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
    if wave:                    # 大波：箱は なめらかに（立ち上がる・近づく・のりだす・沈む）、頭の コマは step-end で
        n = wave['frames']
        gw, gh = wave['size']
        wparts = wave['parts']
        css += (f'.ukw .ukWg{{left:{WB[0]}px;top:{WB[1]}px;width:{f(gw)}px;height:{f(gh)}px;transform-origin:{f(WG_O[0])}px {f(WG_O[1])}px;'
                f'animation:ukLife {f(WAVE_T)}s linear infinite}}'
                f'.ukw .ukW{{position:absolute;left:0;top:0;width:{f(gw)}px;height:{f(gh)}px;background:url({wave["url"]}) 0 0/{f(n * gw)}px {f(gh)}px no-repeat}}'
                f'.ukw .ukW.dots{{background-position:{f(-wparts.index("dots") * gw)}px 0}}'
                f'.ukw .ukW.d1{{opacity:0;animation:ukDot1 {f(WAVE_T)}s linear infinite}}.ukw .ukW.d2{{opacity:0;animation:ukDot2 {f(WAVE_T)}s linear infinite}}'
                + kf('ukLife', life_stops()))
        if crest:                                   # 頭の コマ（巻きの 強さ c の じゅん）：c が 今の 時に あう コマを step-end で
            (cw2, ch2), cols, rows = crest['cell'], crest['cols'], crest['rows']
            fw, fh = cw2 / 2, ch2 / 2
            ax, ay = crest['at']
            css += (f'.ukw .ukCf{{position:absolute;left:{f(ax, 3)}px;top:{f(ay, 3)}px;width:{f(fw)}px;height:{f(fh)}px;'
                    f'background:url({crest["url"]}) 0 0/{f(cols * fw)}px {f(rows * fh)}px no-repeat;animation:ukCf {f(WAVE_T)}s step-end infinite}}'
                    + kf('ukCf', crest_stops(crest['cs'], cols, fw, fh)))
    if foam:                                        # 小波と しぶきの 部品は 1まいの シートの 中の 場所で えらぶ
        z_ = foam['z']
        sw_, sh_ = foam['sheet']
        css += f'.ukw .ukF{{background:url({foam["url"]}) 0 0/{f(sw_ / z_, 3)}px {f(sh_ / z_, 3)}px no-repeat}}'
        css += ''.join(f'.ukw .ukF.{nm}{{background-position:{f(-x_ / z_, 3)}px {f(-y_ / z_, 3)}px}}' for nm, (x_, y_, w_, h_) in parts.items())
    css += samurai_css()
    if run:
        n, (cw, ch), (ax, ay) = run['frames'], run['cell'], run['at']
        w, h = cw / 2, ch / 2
        css += (f'.ukw .ukH{{left:{f(ax / 2)}px;top:{f(ay / 2 - 7)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'   # 7px 上：ひづめを 街道の まん中に
                f'.ukw .ukH>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({run["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;animation:ukRun .48s steps({n}) infinite}}'
                + kf('ukRun', [(100, f'transform:translateX({f(-n * w)}px)')]))
    css += (kf('ukFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-TILE}px)')])
            + kf('ukKs', [(0, 'transform:translateX(-8px)'), (50, 'transform:translateX(10px)'), (100, 'transform:translateX(-8px)')])
            + kf('ukBoat', [(0, 'transform:translateY(0) rotate(-3deg)'), (50, 'transform:translateY(2px) rotate(3deg)'), (100, 'transform:translateY(0) rotate(-3deg)')])
            + wave_life_css())
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
    alt='浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（白い背中・濃い藍に白いすじ・まるい爪の泡：三秒ごとに小波のうしろの海から立ち上がってこちらへのりだし、潮しぶきを上げてくずれ、手前の小波にのまれて沈む）。海は先の少しとがった小波が二列にならび、ひとつずつゆっくり上下する。沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走り、ときどきお侍さんとすれちがう。右上に朱の印',
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
               pic='和紙の 地・藍の ぼかしの 空・赤い 日・山なみ・かすみ・神奈川沖浪裏の 形の 大波（白い 背中・濃い 藍に 白い すじ・まるい 爪の 泡・ぼかしの かげ：'
                   '3秒ごとに 手前の 小波の うしろの 海から 立ち上がって こちらへ のりだし、波の 先が 投げ出されて しぶきが とび、落ちた 所で 潮しぶきが ふき上がり、ふくらむ 小波に のまれて 沈むと 次の 波）・'
                   '先の 少し とがった 大きめの 小波 2列（1つずつ ゆっくり 上下・大波に 合わせて ふくらむ・頭から 潮しぶき）・'
                   '帆かけ舟・松並木の 街道・朱の 布の 白い 馬（墨の 輪郭）・ときどき すれちがう お侍さん・朱の 印'),
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
