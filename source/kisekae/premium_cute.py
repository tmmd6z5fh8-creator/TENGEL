"""プレミアムど的中（かわいいど的中）：まさちゃんの指定
   「プレミアムど的中演出 発動条件、ど的中の6回に1回発動、ランダム
    ・かわいいど的中 かわいいの馬がひらがなを持っている絵で タップしたらハートが上から下に落ちて画面上に積もっていき、画面一杯になったら、ハートが弾ける演出、
    一瞬白い光に包まれてから でっかいハートの中に、ど！が書いてる そのハートを写真の馬が持っている！
    ①ど！、左から画面中央(馬顔右向き) ②て！、右から画面中央(馬顔左向き) ③き！、下から画面中央(馬顔やや右向き)
    ④ちゅ！❤️、上から画面中央(馬顔やや左向き、左目ウィンク) ⑤う！画面中央に出てくる(馬顔正面) 一文字づつの画面で演出
    最後に ど的中❤️、細かいハートのエフェクトが上に消えていき、大きなハートに包まれたど的中を画面中央に表示する で終わり」
   「かわいいのど的中ボタン限定ではなくて、ど的中ボタンのプレミアムだからどの壁紙使ってても、ど的中の6回に1回はこれが出るようにって意味だった。」
   → どの着せ替えでも ど的中の 6回に1回。最後の ボードは その着せ替えの ど的中の ボード（見本は ど的中と 同じ デフォルト＝牧場）
   「プレミアムど的中の、馬はこの画像の馬をモデルにして！ この画像も俺が作ったやつ！ 背景はこの写真のような虹色で！
    演出内で出てくるハートは、一つ一つもっとプルンプルンさせて光沢つけて！」
   「馬の絵だけヤバすぎる 全身写そうとするから変になるから、アップで、馬の顔も手、ハートだけ見えればいいから！ あとは黄金比とかだけ合ってれば大丈夫！
    背景もまだまだ、虹の感じが弱い！パチンコの大当たりのくらい派手な虹色にしないと！ この画像くらいリアルにして！」
   「背景はOK! 1枚目、2枚目のところは、もう少し顔正面よりにして！ 3.4.5馬の立髪なのに、両方に立髪写ってるから上手く調整して！立髪だから！
    後耳は6枚目の写真が正しいから全部この耳に合わせて！」
   - ①〜⑤は ポニーの アップ（顔・前足・ハートだけ）。比は まさちゃんの 絵に あわせた（頭の 白い はば ≒ ハートの はば × 0.54 を 1割 大きく）。
     ①②（右向き・左向き）は 向こうの 目が 細く 見える ななめ・たてがみは 首の 片がわ だけ・耳は どの 顔も ②の 耳と 同じ（リボンを はさんで 2つ）
   - 絵は ぜんぶ flat/premium_art.py で 作った WebP（キャンバスの アセット・リポジトリには 入れない。まさちゃんの 絵も 入れない・なぞっていない）：
     頭（右向き・やや右・やや右で ウィンク・正面。左向き・やや左は 左右 うらがえす）・ハート・字（ど！ など）・ひづめ・最後の「ど的中」・
     背景（パチンコの 大当たりのような 虹色の 光線）・つやつやの ゼリーの ハート 6色（つもる・とぶ・のぼる・ふわふわ ハート）
     premium_blobs.json（名前 → キャンバスの id）・premium_layers.json（名前 → 画面の 箱：flat/premium_art.py が 書く）
   - 背景の 上で 白い 光線が ゆっくり 回る（1つの 所を 光線が 通るのは 1秒に 1回 くらい＝点めつ しない）
   - 字（ど・て・き・ち・ゅ・う・！・的・中）は 太い まるい 線で 書いた 字（フォントを 使わない：GLYPHS。flat/premium_art.py が 使う）
   このファイルは 字の 形・ならべ方・動き（時刻・HTML・CSS）。見本の 画面は gen_fx.py の fz_pc"""
import json
import math
import os
import random
from art import f, smooth, heart, sparkle, path

# ---------------------------------------------------------------- 字（太い まるい 線で 書いた 字。100×100 の ます・y は下向き）
# 1つの字 ＝ (はば, [線…])。線 ＝ 点の 列（なめらかに つなぐ。同じ 点を 2回 ならべると 角）。点 1つ だけの 線は まるい 点
GLYPHS = {
    'ど': (104, [[(38, 14), (44, 46)],
                 [(76, 28), (58, 38), (40, 50), (30, 62), (29, 76), (38, 86), (56, 89), (78, 86)]]),
    'て': (100, [[(14, 32), (50, 24), (86, 20), (86, 20), (62, 32), (46, 48), (42, 66), (50, 82), (68, 90)]]),
    'き': (100, [[(22, 24), (74, 18)], [(16, 44), (82, 36)],
                 [(38, 6), (50, 30), (62, 52), (66, 60)],
                 [(32, 64), (30, 74), (38, 84), (56, 88), (76, 86)]]),
    'ち': (100, [[(18, 28), (80, 22)],
                 [(46, 6), (42, 30), (36, 54), (36, 54), (52, 46), (68, 46), (78, 56), (78, 72), (66, 84), (46, 90), (34, 88)]]),
    'ゆ': (100, [[(22, 24), (20, 62), (20, 62), (30, 48), (46, 38), (64, 36), (80, 46), (82, 62), (72, 74), (56, 76)],
                 [(52, 14), (54, 40), (54, 64), (50, 82), (40, 92)]]),
    'う': (100, [[(40, 10), (62, 16)],
                 [(24, 40), (44, 34), (64, 32), (76, 40), (78, 56), (70, 72), (54, 84), (36, 92)]]),
    '！': (48, [[(24, 10), (24, 60)], [(24, 84)]]),
    '的': (100, [[(28, 6), (22, 18)],
                 [(12, 24), (12, 90)], [(12, 24), (42, 24), (42, 24), (42, 90)], [(12, 56), (42, 56)], [(12, 88), (42, 88)],
                 [(62, 6), (54, 24)],
                 [(54, 28), (88, 28), (88, 28), (86, 70), (82, 86), (70, 90)],
                 [(64, 50), (72, 64)]]),
    '中': (100, [[(16, 28), (16, 68)], [(16, 28), (84, 28), (84, 28), (84, 68)], [(16, 66), (84, 66)], [(50, 6), (50, 96)]]),
}
SMALL = {'ゅ': ('ゆ', .62, 70)}     # 小さい字：(もとの字・大きさ・はば)。下に そろえる
DAKU = {'ど': ((81, 13, 9.5), (96, 8, 9.5))}     # 濁点は つやつやの 玉（写真の「ど！」）：(x, y, 半径)。ますの 中


def glyph_d(ch, x0, y0, s):
    """字 ch の 線（path の d）。(x0, y0)＝ますの 左上・s＝1ます の 大きさ（px）"""
    small = SMALL.get(ch)
    if small:
        base, k, _ = small
        w, strokes = GLYPHS[base]
        ox, oy, sc = x0 + 4 * s, y0 + (100 - 100 * k) * s - 4 * s, s * k
    else:
        w, strokes = GLYPHS[ch]
        ox, oy, sc = x0, y0, s
    d = ''
    for st in strokes:
        pts = [(ox + x * sc, oy + y * sc) for x, y in st]
        if len(pts) == 1:
            d += f'M{f(pts[0][0])} {f(pts[0][1])} L{f(pts[0][0])} {f(pts[0][1])} '
        elif len(pts) == 2:
            d += f'M{f(pts[0][0])} {f(pts[0][1])} L{f(pts[1][0])} {f(pts[1][1])} '
        else:
            d += smooth(pts, closed=False) + ' '
    return d.strip()


def advance(ch):
    return SMALL[ch][2] if ch in SMALL else GLYPHS[ch][0]


def word_d(text, cx, cy, s, gap=-4):
    """横に ならべた 字の 線・はば・濁点の 玉 [(x, y, 半径)]（cx, cy＝まん中・s＝1ます の px）"""
    adv = [advance(c) for c in text]
    total = (sum(adv) + gap * (len(text) - 1)) * s
    x = cx - total / 2
    d, balls = '', []
    for c, a in zip(text, adv):
        d += glyph_d(c, x, cy - 50 * s, s) + ' '
        balls += [(x + bx * s, cy - 50 * s + by * s, br * s) for bx, by, br in DAKU.get(c, ())]
        x += (a + gap) * s
    return d.strip(), total, balls


# ---------------------------------------------------------------- ならべ方（390×844 の 画面）と 絵（flat/premium_art.py の WebP）
HEART_C, HEART_S = (195.0, 520.0), 170.0          # ハートの まん中と 大きさ（ハートの はば＝2×HEART_S）
HEAD_BOX = (-30.0, 140.0, 450.0, 560.0)           # 頭の 絵を 描く 箱（pm_head_…：画面の まん中で 左右 対称。まわりの 白い 光は ハートの 下まで）
HEART_BOX = (0.0, 330.0, 390.0, 360.0)            # ハートと 字の 絵を 描く 箱（pm_heart・pm_t…）
HOOF_BOX = (0.0, 450.0, 390.0, 110.0)             # ひづめの 絵を 描く 箱（pm_hoof）
HERE = os.path.dirname(os.path.abspath(__file__))
FACE = dict(R=('R', False), L=('R', True), r=('T', False), l=('W', True), F=('F', False))   # 顔の 向き → (頭の 絵, 左右 うらがえす)
_ART = {}


def art():
    """(名前 → キャンバスの id, 名前 → 画面の 箱 [x, y, w, h])"""
    if not _ART:
        _ART['ids'] = json.load(open(os.path.join(HERE, 'premium_blobs.json')))
        _ART['box'] = json.load(open(os.path.join(HERE, 'premium_layers.json')))
    return _ART['ids'], _ART['box']


def blob(name):
    return '/_blob/' + art()[0][name]


def img(name, mirror=False):
    """絵 1まい（画面の 決まった 箱に。mirror：画面の まん中で 左右 うらがえす）"""
    x, y, w, h = art()[1][name]
    if mirror:
        x = 390 - x - w
    t = ';transform:scaleX(-1)' if mirror else ''
    return f'<img class="pmi" src="{blob(name)}" alt="" style="left:{x:.3f}px;top:{y:.3f}px;width:{w:.3f}px;height:{h:.3f}px{t}">'


# ---------------------------------------------------------------- 動き（タップした 瞬間が 0秒）
# 点めつ（1秒に 3回まで）の ために：落ちている ハートの ほとんどは すき通った 光の ハート（白 12%）で、つもった 時に つやつやの ゼリーに なって ぷるんっ
# （16こに 1こだけ つやつやの まま ぷるぷる 落ちる）。先に つもった ハートほど 前に かさねる（あとから 落ちる ハートは うしろを とおる）。
# ①〜⑤と 最後の ハートは 白い 光の 形で 入ってきて、止まる 時に 色が つく
PC_T = dict(FILL=2.4,                   # ハートが 画面 いっぱいに つもる（0〜2.4）
            BURST=2.48, CHAIN=.16,      # ハートが まん中から 外へ じゅんに はじける（2.48〜2.64 に はじけはじめ・1つ 0.22秒）
            W=(2.66, 2.78, 2.92, 3.32),  # 白い 光：明るくなりはじめ・いちばん 明るい・ここまで・消える
            BG=2.84,                    # 白い 光の 中で 光の 筋と キラキラが 出る
            S=(3.0, 4.2, 5.4, 6.6, 7.8),   # ①〜⑤ の 画面（1つ 1.2秒）
            IN=.45, OUT=.12,           # 入ってくる・消える（つぎの 画面の 前）
            FIN=9.0,                    # 大きな ハートの ど的中
            RES=10.9)                   # ハートが 上へ・ボード
# ①〜⑤：(字, 顔の 向き, 入ってくる 方, 字の 大きさ)。顔：R＝右・L＝左・r＝やや右・l＝やや左（ウィンク）・F＝正面。方：L＝左から・R＝右から・B＝下から・T＝上から・C＝まん中に 出る
SCREENS = (('ど！', 'R', 'L', 1.32), ('て！', 'L', 'R', 1.32), ('き！', 'r', 'B', 1.32), ('ちゅ！', 'l', 'T', 1.1), ('う！', 'F', 'C', 1.32))
FIN_C, FIN_S = (195.0, 415.0), 165.0     # 大きな ハートの まん中と 大きさ
FIN_BOX = (0.0, 225.0, 390.0, 390.0)     # 最後の ハートの 絵の 箱（flat/premium_art.py の pm_fin）
TITLE_Y, TITLE_K = 112.0, .48            # ボードの 上に 動いた ハートの まん中と 大きさ
UP_VEIL = (.12, .77)                     # 上へ 動く 前に 白く なりはじめる（RES の 0.12秒 前）・白い 光の 長さ（動く 0.5秒の あと 0.15秒で 色が もどる）
PILE_COLS = (('#FF5FA6', '#FFC2DE', '#DD3484'), ('#FF8CC2', '#FFDCEC', '#EE5EA0'), ('#FFA9D1', '#FFEAF4', '#F07CB4'),   # つやつやの ゼリーの ハート：(色・光・かげ)
             ('#F25CC4', '#FFC8EE', '#C63A9E'), ('#FF7E9E', '#FFD3DC', '#E5547A'), ('#FFD1E6', '#FFFFFF', '#F2A0C6'))   # ホットピンク・ピンク・うすい ピンク・マゼンタ・コーラル・白っぽい ピンク


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def jelly_bg(k):
    """つやつやの ゼリーの ハート k 色め（pm_jelly：6色を よこに ならべた 1まいの 絵）の CSS の 背景"""
    return f'url({blob("pm_jelly")}) {k * 100 / (len(PILE_COLS) - 1):.1f}% 0/{len(PILE_COLS) * 100}% 100% no-repeat'


def fly_uri():
    """落ちている ハート：すき通った 光の ハート（白 12%・ふち 7%。どの 背景の 色の 上でも 明るさの 差が 0.1 より 小さい＝点めつ しない）"""
    d = heart(0, 0, 1)
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1.12 -1.08 2.24 2.24'><path d='{d}' fill='#fff' fill-opacity='.12' stroke='#fff' stroke-opacity='.07' stroke-width='.08'/>"
           "<ellipse cx='-.48' cy='-.5' rx='.25' ry='.14' transform='rotate(-38 -.48 -.5)' fill='#fff' opacity='.07'/></svg>")
    return 'url("data:image/svg+xml,' + svg.replace('#', '%23') + '")'


def bob_hearts():
    """背景の 上で ふわふわ うく つやつやの ゼリーの ハート"""
    rnd = random.Random(21)
    o = ''
    for x, y, sz, rot in ((38, 214, 18, -14), (354, 206, 15, 12), (22, 648, 16, 10), (366, 654, 20, -12), (318, 296, 11, 8), (86, 112, 12, -8),
                          (300, 790, 13, 10), (60, 470, 10, -10)):
        w = sz * 2.24
        o += (f'<i class="pmj pm{rnd.choice((0, 1, 3, 4))}" style="left:{x - w / 2:.0f}px;top:{y - w / 2:.0f}px;width:{w:.0f}px;height:{w:.0f}px;'
              f'--r:{rot}deg;animation-delay:-{rnd.uniform(0, 3):.2f}s"></i>')
    return o


def pile(seed=11, W=390, H=844):
    """つもる ハート [(x, y（まん中）, s（はばの 半分）, 色, 回る角度 …)]。下から 順に つもる（つもる 順）。画面の いちばん ひくい 所が 上の はしを こえるまで"""
    rnd = random.Random(seed)
    step = 6
    cols = W // step + 1
    top = [H + 16.0] * cols
    out = []
    while max(top) > -28:
        s = rnd.uniform(22, 38)
        lo = max(range(cols), key=lambda c: top[c] + rnd.uniform(0, 70))     # ひくい 所（top が 大きい）に 落ちやすい
        x = min(W + s * .2, max(-s * .2, lo * step + rnd.uniform(-s * .6, s * .6)))
        c0, c1 = max(0, int((x - s * .85) // step)), min(cols - 1, int((x + s * .85) // step))
        under = top[c0:c1 + 1]
        base = (min(under) + sum(under) / len(under)) / 2
        yc = base + s * .05
        for c in range(c0, c1 + 1):
            u = min(1.0, abs(c * step - x) / (s * .85))
            top[c] = min(top[c], yc - s * (.8 - .3 * u * u))
        out.append(dict(x=x, y=yc, s=s, k=rnd.randrange(len(PILE_COLS)), r0=rnd.uniform(-40, 40), r1=rnd.uniform(-18, 18)))
    return out


BURST_C = (195.0, 422.0)                 # はじける まん中
BG_C = (195.0, 470.0)                    # 背景の 光の まん中（flat/premium_art.py の BG_C と 同じ）
FALL_EVERY = 16                          # 16こに 1こは つやつやの まま ぷるぷる 落ちる（ほかは すき通った 光の ハートで 落ちて、つもった時に つやつやに。1つの 点を よこぎる 見える ハートが 1秒に 1こ くらい＝点めつ しない）


def pile_html(seed=11, g=3000.0):
    """つもる ハート（外の i：はじける・中の b：落ちる（b::before：すき通った 光の ハート・b::after：つもった 時の つやつやの ゼリーの ハート・ぷるんっ））。
       先に つもった ハートほど あと（前）に 書く：あとから 落ちる ハートは つもった ハートの うしろを とおる"""
    hs = pile(seed)
    rnd = random.Random(seed + 1)
    n = len(hs)
    t_first, t_last = .62, PC_T['FILL']
    items = []
    for i, h in enumerate(hs):
        land = t_first + (t_last - t_first) * (i / max(1, n - 1)) ** .9
        y0 = min(-h['s'] * 1.3 - rnd.uniform(0, 140), h['y'] - h['s'] * 2.4 - 40)     # 画面の 上の 外から
        dist = h['y'] - y0
        tf = math.sqrt(2 * dist / g)
        d = max(0.0, land - tf)
        tf = land - d
        dx, dy = h['x'] - BURST_C[0], h['y'] - BURST_C[1]
        L = math.hypot(dx, dy) or 1
        k = rnd.uniform(10, 34)
        bx, by = dx / L * k, dy / L * k
        bd = PC_T['BURST'] + PC_T['CHAIN'] * min(1.0, L / 480) + rnd.uniform(0, .02)
        pv = ' pv' if i % FALL_EVERY == FALL_EVERY // 2 else ''       # 見える ハート（つやつやの まま ぷるぷる 落ちる）
        items.append(f'<i class="pm{h["k"]}{pv}" style="left:{h["x"] - h["s"] * 1.12:.1f}px;top:{h["y"] - h["s"] * 1.08:.1f}px;width:{h["s"] * 2.24:.1f}px;height:{h["s"] * 2.24:.1f}px;'
                     f'--y0:{y0 - h["y"]:.0f}px;--t:{tf:.2f}s;--d:{d:.2f}s;--l:{max(0.0, land - .02):.2f}s;--r0:{h["r0"]:.0f}deg;--r1:{h["r1"]:.0f}deg;'
                     f'--bx:{bx:.0f}px;--by:{by:.0f}px;--br:{rnd.uniform(-25, 25):.0f}deg;--bd:{bd:.2f}s"><b></b></i>')
    return ''.join(reversed(items)), n


def pop_hearts(x, y, d, n, seed, dist=(90, 160), size=(14, 26)):
    """着いた時に まわりへ とびちる 小さな ハート"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        r = rnd.uniform(*dist)
        s = rnd.uniform(*size)
        o += (f'<i class="pm{rnd.randrange(len(PILE_COLS))}" style="left:{x - s / 2:.0f}px;top:{y - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;'
              f'--dx:{math.cos(a) * r:.0f}px;--dy:{math.sin(a) * r:.0f}px;--d:{sec(d + rnd.uniform(0, .05))};--r:{rnd.uniform(-90, 90):.0f}deg"></i>')
    return o


def rising_hearts(n, seed, t0):
    """下から 上へ のぼって 消える 細かい ハート（いつまでも）"""
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        s = rnd.uniform(7, 17)
        dur = rnd.uniform(2.2, 3.8)
        o += (f'<i class="pm{rnd.choice((0, 1, 2, 4, 5))}" style="left:{rnd.uniform(4, 386) - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;'
              f'--t:{dur:.2f}s;--d:{t0 + rnd.uniform(-dur * .6, 1.6):.2f}s;--w:{rnd.uniform(-26, 26):.0f}px"></i>')
    return o


def twinkles(n, seed, box=(10, 60, 380, 800)):
    rnd = random.Random(seed)
    o = ''
    for i in range(n):
        x, y, r = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3]), rnd.uniform(5, 12)
        o += path(sparkle(x, y, r), fill='#FFFFFF', style=f'animation-duration:{rnd.uniform(1.1, 2.1):.2f}s;animation-delay:-{rnd.uniform(0, 2):.2f}s')
    return o


def enter_anim(frm):
    return dict(L='pmInL', R='pmInR', B='pmInB', T='pmInT', C='pmInC')[frm]


def veil(art_html, t, dur, more=''):
    """白い 光の 形（絵と 同じ 形の 白）：入ってくる 間は 絵を 白く つつみ、止まる 時に 消えて 色が つく（点めつ しない 入り方）。more：あとの 動き"""
    return f'<div class="pmv" aria-hidden="true" style="animation:pmVl {sec(dur)} linear {sec(t)} both{more}">{art_html}</div>'


def pc_layers(board_html):
    """押したあと（下から）：虹色の 背景（パチンコの 大当たりのような 光線・ふわふわの ハート）→ つもる ハート → 回る 白い 光線・キラキラ →
       ①〜⑤ の ポニーの アップ（着いた時に ハートが とぶ）→ 最後の 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。
       board_html：テーマの ボード（gen_fx の board）"""
    T = PC_T
    hearts, n = pile_html()
    scr = ''
    S = T['S']
    cx, cy = HEART_C
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        t_in = S[i]
        t_out = (S[i + 1] if i + 1 < len(S) else T['FIN']) - T['OUT']
        land = t_in + T['IN'] * .72
        hv, mir = FACE[face]
        head = img(f'pm_head_{hv}', mir)
        art_html = (head + f'<div class="pmhj" style="animation-delay:{t_in + T["IN"] * .9:.2f}s">{img("pm_heart")}{img(f"pm_t{i}")}</div>' + img('pm_hoof'))
        scr += (f'<div class="pms" aria-hidden="true" style="animation:{enter_anim(frm)} {sec(T["IN"])} cubic-bezier(.25,.9,.35,1) {sec(t_in)} both,'
                f'pmOut {sec(T["OUT"])} linear {sec(t_out)} forwards">{art_html}{veil(head + img("pm_heart") + img("pm_hoof"), t_in, T["IN"])}</div>'
                f'<i class="pmr" style="--d:{sec(land)}"></i><div class="pml">{pop_hearts(cx, cy - 20, land, 14, 30 + i)}</div>')
    fx, fy = FIN_C
    bx, by = BURST_C
    fin = img('pm_fin')
    return f'''<div class="pmbg" aria-hidden="true"><img class="pmi" src="{blob('pm_bg')}" alt="" style="left:0;top:0;width:390px;height:844px">{bob_hearts()}</div>
    <div class="pmp" aria-hidden="true">{hearts}</div>
    <div class="pml pmlb">{pop_hearts(bx, by, T['BURST'], 20, 23, dist=(170, 300), size=(16, 30))}</div>
    <div class="pmpk" aria-hidden="true"><i class="rays"></i><i class="glow"></i><svg class="spk" viewBox="0 0 390 844">{twinkles(26, 5)}</svg></div>
    {scr}
    <div class="pmu" aria-hidden="true">{rising_hearts(40, 9, T['FIN'])}</div>
    <div class="pmf" aria-hidden="true">{fin}{veil(fin, T["FIN"], .5, f",pmVu {sec(UP_VEIL[1])} linear {sec(T['RES'] - UP_VEIL[0])} forwards")}</div>
    <i class="pmr pmrf" style="--d:{sec(T['FIN'] + .28)}"></i><div class="pml">{pop_hearts(fx, fy - 10, T['FIN'] + .28, 18, 47, dist=(130, 210))}</div>
    <div class="hb">{board_html}</div>
    <div class="pmw" aria-hidden="true"></div>
    <p class="sr">プレミアムど的中！ハートが いっぱいに つもって はじけ、虹色の 大当たりの 光の 中に、ハートを だいた ポニーが ど・て・き・ちゅ・う と 1文字ずつ 出てきて、さいごに ハートに つつまれた ど的中</p>'''


def pile_css():
    return ''.join(f'.ov.pm .pm{k}{{background:{jelly_bg(k)}}}' for k in range(len(PILE_COLS)))


def pc_css():
    T = PC_T
    w0, w1, w2, w3 = T['W']
    wd = w3 - w0
    fy = FIN_C[1]
    return pile_css() + f'''
/* ---------- プレミアムど的中（かわいいど的中）：premium_cute.py（絵は flat/premium_art.py の WebP） ---------- */
.ov.fz.pm{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
.ov.pm .pmi{{position:absolute;display:block;max-width:none;max-height:none;pointer-events:none;-webkit-user-select:none;user-select:none;-webkit-user-drag:none}}
/* 虹色の 背景（パチンコの 大当たりのような 光線・まん中の 白い 光・虹の 輪・さくら・キラキラ：pm_bg）の 上で つやつやの ハートが ふわふわ */
.ov.pm .pmbg{{position:absolute;inset:0;overflow:hidden;background:#FF6FC4}}
.ov.pm .pmbg .pmj{{position:absolute;display:block;transform:rotate(var(--r));animation:pmBob 2.8s ease-in-out infinite alternate}}
@keyframes pmBob{{to{{transform:translateY(-6px) rotate(var(--r))}}}}
/* つもる ハート：外の i＝はじける（{sec(T['BURST'])}〜・まん中から じゅんに・ぷくっと ふくらんで）・中の b＝上から 落ちる
   （b::before＝すき通った 光の ハート・b::after＝つもった 時に つやつやの ゼリーの ハートに なって ぷるんっ） */
.ov.pm .pmp{{position:absolute;inset:0;z-index:2;pointer-events:none}}
.ov.pm .pmp i{{position:absolute;display:block;background:none!important;animation:pmB .24s linear var(--bd) forwards}}
.ov.pm .pmp b{{position:absolute;inset:0;transform:translateY(var(--y0)) rotate(var(--r0));animation:pmF var(--t) cubic-bezier(.333,0,.667,.333) var(--d) both}}
.ov.pm .pmp b::before,.ov.pm .pmp b::after{{content:'';position:absolute;inset:0}}
.ov.pm .pmp b::before{{background:{fly_uri()} center/contain no-repeat;animation:pmLo .08s linear var(--l) forwards}}
.ov.pm .pmp b::after{{opacity:0;transform-origin:50% 88%;animation:pmL .1s linear var(--l) forwards,pmJ .55s ease-out var(--l) both}}
{''.join(f'.ov.pm .pmp .pm{k} b::after{{background:{jelly_bg(k)}}}' for k in range(len(PILE_COLS)))}
@keyframes pmF{{to{{transform:translateY(0) rotate(var(--r1))}}}}
@keyframes pmL{{to{{opacity:1}}}}
@keyframes pmLo{{to{{opacity:0}}}}
.ov.pm .pmp .pv b::before{{display:none}}
.ov.pm .pmp .pv b::after{{opacity:1;animation:pmWob .34s ease-in-out infinite alternate,pmJ .55s ease-out var(--l) forwards}}
@keyframes pmWob{{from{{transform:scale(1.07,.93)}}to{{transform:scale(.94,1.06)}}}}
@keyframes pmJ{{0%{{transform:scale(1.2,.76)}}28%{{transform:scale(.9,1.12)}}52%{{transform:scale(1.06,.95)}}76%{{transform:scale(.98,1.02)}}100%{{transform:none}}}}
@keyframes pmB{{0%{{transform:none}}35%{{transform:translate(calc(var(--bx) * .3),calc(var(--by) * .3)) scale(1.16,.9)}}100%{{transform:translate(var(--bx),var(--by)) scale(1.4) rotate(var(--br));opacity:0}}}}
.ov.pm .pmlb{{z-index:2}}
/* 白い 光の 中で 出る：細い 白い 光線（ゆっくり 回る＝大当たりの 光。1つの 所を 光線が 通るのは 1秒に 1回 くらい）・まん中の 光・キラキラ */
.ov.pm .pmpk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;animation:fzOn .01s linear {sec(T['BG'])} forwards}}
.ov.pm .pmpk .rays{{position:absolute;left:50%;top:{BG_C[1]:.0f}px;width:1500px;height:1500px;margin:-750px 0 0 -750px;border-radius:50%;opacity:.6;
  background:repeating-conic-gradient(rgba(255,255,255,.9) 0 2deg,rgba(255,255,255,0) 2deg 12deg);
  -webkit-mask-image:radial-gradient(circle,transparent 0 9%,#000 20%,#000 40%,transparent 62%);mask-image:radial-gradient(circle,transparent 0 9%,#000 20%,#000 40%,transparent 62%);
  animation:spin 36s linear infinite}}
.ov.pm .pmpk .glow{{position:absolute;left:50%;top:{BG_C[1]:.0f}px;width:440px;height:440px;margin:-220px 0 0 -220px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.6),rgba(255,255,255,.22) 40%,rgba(255,255,255,0) 70%)}}
.ov.pm .pmpk .spk{{position:absolute;inset:0;width:390px;height:844px}}
.ov.pm .pmpk .spk path{{animation:pmTw 1.6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes pmTw{{from{{opacity:.25;transform:scale(.55)}}to{{opacity:1;transform:scale(1)}}}}
/* ①〜⑤：ハートを だいた ポニーが 左・右・下・上から 入ってくる／まん中に 出る（1つ {sec(T['S'][1] - T['S'][0])}） */
.ov.pm .pms{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:5;opacity:0;pointer-events:none;transform-origin:{HEART_C[0]:.0f}px {HEART_C[1]:.0f}px}}
@keyframes pmInL{{0%{{opacity:1;transform:translateX(-440px) rotate(-7deg)}}72%{{transform:translateX(8px) rotate(1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInR{{0%{{opacity:1;transform:translateX(440px) rotate(7deg)}}72%{{transform:translateX(-8px) rotate(-1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInB{{0%{{opacity:1;transform:translateY(760px)}}72%{{transform:translateY(-14px)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInT{{0%{{opacity:1;transform:translateY(-840px)}}72%{{transform:translateY(6px) scale(1.02,.98)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInC{{0%{{opacity:0;transform:scale(.15)}}55%{{opacity:1;transform:scale(1.13)}}78%{{transform:scale(.95)}}100%{{opacity:1;transform:none}}}}
@keyframes pmOut{{from{{opacity:1}}to{{opacity:0}}}}
/* 白い 光の 形：入ってくる 間は 白く つつみ（0.92）、止まる 前に 消えて 色が つく */
.ov.pm .pmv{{position:absolute;inset:0;width:390px;height:844px;filter:brightness(0) invert(1);opacity:0;pointer-events:none}}
@keyframes pmVl{{0%,62%{{opacity:.92}}100%{{opacity:0}}}}
/* 最後の ハートが 上へ 動く 間も 白く つつむ（{sec(T['RES'] - UP_VEIL[0])}〜） */
@keyframes pmVu{{0%{{opacity:0}}{UP_VEIL[0] / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}{(UP_VEIL[0] + .5) / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}100%{{opacity:0}}}}
/* 着いた時：白い 輪と 小さな ハートが とびちる */
.ov.pm .pmr{{position:absolute;z-index:4;left:{HEART_C[0] - 110:.0f}px;top:{HEART_C[1] - 130:.0f}px;width:220px;height:220px;border-radius:50%;border:8px solid #FFFFFF;
  box-shadow:0 0 16px rgba(255,120,190,.8),inset 0 0 12px rgba(255,120,190,.6);opacity:0;animation:pmRing .55s ease-out var(--d) both}}
.ov.pm .pmrf{{top:{fy - 120:.0f}px}}
@keyframes pmRing{{0%{{opacity:0;transform:scale(.3)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(2.1)}}}}
.ov.pm .pml{{position:absolute;inset:0;z-index:6;pointer-events:none}}
.ov.pm .pml i{{position:absolute;display:block;opacity:0;animation:pmPop .7s linear var(--d) both}}
@keyframes pmPop{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}8%{{opacity:1}}
  22%{{transform:translate(calc(var(--dx) * .45),calc(var(--dy) * .45)) scale(1.18,.86) rotate(calc(var(--r) * .3))}}
  40%{{transform:translate(calc(var(--dx) * .7),calc(var(--dy) * .7)) scale(.9,1.1) rotate(calc(var(--r) * .55))}}
  58%{{transform:translate(calc(var(--dx) * .86),calc(var(--dy) * .86)) scale(1.06,.95) rotate(calc(var(--r) * .78))}}70%{{opacity:1}}
  100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1) rotate(var(--r))}}}}
/* ①〜⑤：止まった時に ハートと 字が ぷるんっ */
.ov.pm .pmhj{{position:absolute;inset:0;transform-origin:{HEART_C[0]:.0f}px {HEART_C[1] + HEART_S * .8:.0f}px;animation:pmHJ .62s ease-out both}}
@keyframes pmHJ{{0%{{transform:none}}18%{{transform:scale(1.07,.92)}}38%{{transform:scale(.95,1.05)}}58%{{transform:scale(1.025,.98)}}78%{{transform:scale(.993,1.006)}}100%{{transform:none}}}}
/* 最後：大きな ハートの ど的中（{sec(T['FIN'])}）→ {sec(T['RES'])} に 上へ 動いて ボード */
.ov.pm .pmf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;opacity:0;pointer-events:none;transform-origin:{FIN_C[0]:.0f}px {fy:.0f}px;
  animation:pmInC .5s cubic-bezier(.25,.9,.35,1) {sec(T['FIN'])} both,pmBeat .9s ease-in-out {sec(T['FIN'] + .5)} 2,pmUp .5s cubic-bezier(.3,.8,.3,1) {sec(T['RES'])} forwards}}
@keyframes pmBeat{{0%,100%{{transform:none}}14%{{transform:scale(1.08,.93)}}30%{{transform:scale(.95,1.06)}}46%{{transform:scale(1.03,.97)}}62%{{transform:scale(.99,1.01)}}}}
@keyframes pmUp{{from{{opacity:1;transform:none}}to{{opacity:1;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.pm .pmu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {sec(T['FIN'])} forwards}}
.ov.pm .pmu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:pmRise var(--t) linear var(--d) infinite}}
@keyframes pmRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}25%{{transform:translate(calc(var(--w) * .5),-220px) scale(1.12,.9)}}
  50%{{transform:translate(var(--w),-440px) scale(.92,1.08)}}75%{{transform:translate(calc(var(--w) * .5),-670px) scale(1.06,.95)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.pm .hb{{z-index:8;animation:pmBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .12)} both}}
@keyframes pmBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.pm .pmw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:pmWhite {sec(wd)} linear {sec(w0)} forwards}}
@keyframes pmWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハート・回る 光線を 出さず、背景の 小さな ハートも 止める。虹色の 背景のまま 1秒 → まん中の 光と キラキラ・上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.pm .pmp,.ov.pm .pms,.ov.pm .pmr,.ov.pm .pml,.ov.pm .pmu,.ov.pm .pmw,.ov.pm .pmpk .rays,.ov.pm .pmf .pmv{{display:none}}
  .ov.fz.pm{{--t0:1.9s}}
  .ov.pm .pmpk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.pm .pmpk .spk path,.ov.pm .pmbg .pmj{{animation:none!important}}
  .ov.pm .pmf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.pm .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
