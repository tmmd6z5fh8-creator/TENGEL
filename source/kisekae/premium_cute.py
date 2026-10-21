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
   「ここ耳がおかしい！二枚目に合わせて！ あと顔もう少し細く！馬っぽく！ 目の位置ももっと自然にして！ あと後ろ脚もいいサイズ感で入れて！
    この感じなら短い方がいいと思う！3枚目参考にして！」（⑤う！の スクショ・②て！の 耳の スクショ・まさちゃんの 絵）
   - 頭は 3D の 形（まるい 頭・ほお・前へ のびる 鼻先＝細めの 馬の 顔）を 顔の 向きに 回して 描く：目・耳・鼻の 場所が どの 向きでも 自然に そろう。
     耳は まっすぐ 上へ のびる 長い 耳（頭の うしろから）。うしろ足は ハートの 下から 少し 見える 短い 足（まさちゃんの 絵の うしろ足）
   「全体的に、首がなく、肩が出てて変、手の奥にある身体がおかしい手は手だけでいいよ！、脚は、せめて関節入れて！」
   - 頭を 少し 上げて 首（頭の うしろから ハートの うしろへ）を 見せる。うしろ足は 関節（ひざ）で 少し 曲がる
   「ハートの持ち方が手が下から入ってるから変！上から持って！首から手の位置まで、肩を入れたり自然にして！」
   - 前足は 首の 横の 肩から ハートの 山の 前を ななめに おりて、ひづめで ハートの 左右の ふちを 上から つかむ（pm_hoof：肩・うで・ふわふわの 毛・ひづめ）。
     前足は ハートと いっしょに ぷるんっ（持っている 所を 中心に ハートの 下が ゆれる）
   「もっと腕の長さ短くして！鉤爪で、支えてるくらいが丁度いい！腕の角度とか、肩とかはいい感じ！ あと赤丸の位置にリボンの位置合わせて！
    左右の耳の中央にくるように！ あと5枚目のところ耳が散れちゃってるからリボンで隠して！」「あと赤丸の立髪は馬の顔の後ろにあるようにして！1枚目が求めている形」
   - 前足は 肩と 角度は そのまま 短く：ひづめを 手首で 少し 下へ 曲げて、ハートの 上の 方に ひっかけて 支える。リボンは 左右の 耳の まん中（少し 小さく）・
     耳の 外がわの つけねを 頭の 中へ（つけねの 線が 出て 耳が 切れて 見えていた）・たてがみは どの 顔でも 頭の うしろ
   「ど！、て！、き！、ちゅ！、う！全部ハートと腕しか動いてないから不自然！馬もプルンプルン系で、全体的に動いて！結構プルルンて感じにして！全体的に！
    でも身体が歪んだりは変だから構造は身体の構造を考えて作成して！」
   - ポニーを 部品（うしろ足・首・たてがみ・耳 左右・顔・リボン）に 分けて、体の つくりどおりの 関節で ぷるるん（pony_tree・pony_motion）：
     うしろ足は 地面に ついたまま・体は 着地で はずむ・頭は 首の 上を 中心に・耳は つけね・たてがみは 上の はし・リボンは むすびめを 中心に ゆれる。
     白い ふちの 光は CSS の drop-shadow（動く 部品に ついていく）
   「そしたら全体的にもっと顔とハートの文字を画面にアップにして！カメラだと思って、ど！は右正面からアップに、て！は左正面からアップに、
    き！は右正面斜め上からアップに、ちゅ！は左正面斜め上からアップに、う！は真正面からドアップに！カメラ目線で作成して！
    後、馬とハートが登場してプルルンと揺れる時に、光沢があるピンクと白のオーラが全体的に馬とハートから出るようにして！ハートも周りに飛ぶように！」
   - ①〜⑤は カメラ（CAMS・camera）：世界の 座標で 作った ポニーと ハートを 1.28〜1.55倍の アップに。ハート・字・前足は カメラの 向きに かたむける
     （CSS の perspective・rotateX・rotateY）。顔の 向き・上からの 角度・カメラ目線は flat/premium_art.py（YAW・PITCH・GAZE）
   - 着地で ぷるるん する 間：動く 絵に ついていく 白 → ピンクの 光（.pmQ の drop-shadow：pmAu）・外へ 広がる つやつやの ピンクと 白の オーラ
     （pm_aura_…：ripple・2回）・まわりへ とびだして 背景を うめる つやつやの ハート（bloom_hearts）・下に つもった 小さな ハート（pile_bottom）
   「いい感じ！背景のオーラとハートはもっと多くていいよ！画面馬とハート以外の画面埋まるくらい！あと、ど！からもっとアップで！どんどん画面に近く感じにして！
    後、画面下側は小さな光沢のあるプルンプルンしたハートが積もってて、そこに馬もハートも乗ってる感じにして！そしたら、ど！、て！、のカットも後ろ脚を映さなくて
    良くなるから違和感なくせる！馬とハートが揺れる時に、下のハートも揺れて！馬とハートがカットインして、中央に入った時、近い位置にある小さな、
    馬とハートに押される感じで、前に移動して！」
   - ①〜⑤で だんだん 近く（1.40 → 1.66倍）・どの 画面も その 間に 少し 近づく（PUSH_IN）。うしろ足は 出さない（下の ハートに うまる）。
     まわりの ハートは 着地ごとに ふえて 消えない（⑤では ポニーと ハートの ほかが ハートで いっぱい）＋ オーラの キラキラ。
     下に つもった 小さな ハートは 着地ごとに ぷるん・まん中の 近くは 前へ おされて もどる
   「下とか周りのハート小さすぎてちょっと気持ち悪い！写真赤丸のハートより少し大きめにして！」（④の ウィンクの ハート）
   - 下と まわりの ハート・背景の ふわふわ ハートは ますの はば 58〜72px（→ 下の 指定で 70〜88px：HEART_W）
   「画面下は、ハートで埋め尽くして！背景にカットごとに入ってくるハートは、カットごとに増やして、最後は馬と馬が持ってるハート以外画面埋め尽くして！
    イメージ、最後画面全体ハートで埋め尽くして、その上に馬のエフェクトが乗ってるイメージ！」
   - 下の ハートは すきまなく（PILE_D）。まわりの ハートは 画面を すきまなく うめる 場所（heart_slots）を ①〜⑤で だんだん うめて（BLOOM_FILL）、
     入ってくる 数も カットごとに ふやす（BLOOM_IN：30・40・50・60・72）。⑤で ポニーと ハートの ほかは 画面ぜんぶ ハート
   「画面下は、最初のど！からハートで埋めつくて！あと、小さなハートは全体的にあと一回り大きく！もっと光沢付けて、プルンプルンにして！
    あと最後のど的中の時に周りのハート消さないで！画面をハートで埋め尽くした上に、でっかいハートで、ど的中、ね！ハートとど的中もう少し大きくして！」
   「あと、ど！、て！、き！、ちゅ！、う！のカットインごとに、背景にハート付け足されるエフェクト、カットインと同時にハート足されるようにして！」
   - 下は ①から すきまなく：ポニーと ハートの うしろにも ハートを つむ（pile_bottom の うしろ：BACK_Y・BACK_RISE）＋ 前の ハート（FRONT_Y・FRONT_RISE）
   - ハートは ひと回り 大きく（HEART_W 70〜88px）・つやを ふやして（flat/premium_art.py の glossy_heart）・いつも ぷるぷる（pmJly）
   - まわりの ハートは カットインと 同時に、ポニーが 入ってくる 方から とんできて ふえる（BLOOM_T）。⑤では のこりの 場所を ぜんぶ うめる
   - 最後の「ど的中」でも まわりの ハートは 消さない。その 上に でっかい ハート（FIN_S：165 → 185）と「ど的中」
   「プレミアムど的中ボタンだけ試すと落ちちゃう！」
   - 重さ（iPhone で 落ちない ように）：見えない 間は 描かない（hide()・pmH：①〜⑤は その 画面の 1.2秒 だけ・白い 光の 形は 入ってくる 間・
     広がる オーラは 広がる 間・つもる ハートの 雨は はじけるまで・まわりの ハートと キラキラは 入ってくる 時から・最後の ハートなどは 出る 時から）。
     オーラの 光の drop-shadow は 1つの 箱に 1つ（中 .pmQi＝白い ふち・外 .pmQ＝ピンクの 光）・広がる オーラは 絵（img）を そのまま 動かす・
     回る 光線の 箱は 1040px。はかり方は layer_mem.py（層の 画素：いちばん 多い 時 1075MB → 225MB）
   - 絵は ぜんぶ flat/premium_art.py で 作った WebP（キャンバスの アセット・リポジトリには 入れない。まさちゃんの 絵も 入れない・なぞっていない）：
     ポニーの 部品（顔の 向き 4つ：右正面から・右正面 斜め上から・その ウィンク・真正面 × 首・たてがみ・耳 左右・顔・リボン・オーラ。左は 左右 うらがえす）・
     ハート・字（ど！ など）・ひづめ・最後の「ど的中」・
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
HEAD_BOX = (-30.0, 80.0, 450.0, 660.0)            # ポニーの 部品の 絵を 描く 箱（pm_neck_…・pm_mane_…・pm_ear…・pm_face_…・pm_bow_…・pm_aura_…は もっと 大きい 箱：世界の まん中で 左右 対称）
HEART_BOX = (0.0, 330.0, 390.0, 360.0)            # ハートと 字の 絵を 描く 箱（pm_heart・pm_t…）
HOOF_BOX = (0.0, 330.0, 390.0, 230.0)             # 前足（肩から ひづめ）の 絵を 描く 箱（pm_hoof）
HERE = os.path.dirname(os.path.abspath(__file__))
FACE = dict(R=('R', False), L=('R', True), r=('T', False), l=('W', True), F=('F', False))   # 顔の 向き → (部品の 絵の 顔, 左右 うらがえす)
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
SCREENS = (('ど！', 'R', 'L', 1.32), ('て！', 'L', 'R', 1.32), ('き！', 'r', 'B', 1.32), ('ちゅ！', 'l', 'T', 1.0), ('う！', 'F', 'C', 1.24))
TEXT_GAP = (2, 2, 2, -6, 2)       # 字の あいだ（ますの 何分の100。④ちゅ！は 3文字なので せまく：アップでも 画面に 入る）
# ①〜⑤の カメラ（まさちゃん「全体的にもっと顔とハートの文字を画面にアップにして！カメラだと思って、ど！は右正面からアップに、て！は左正面からアップに、
#  き！は右正面斜め上からアップに、ちゅ！は左正面斜め上からアップに、う！は真正面からドアップに！カメラ目線で作成して！」
#  「ど！からもっとアップで！どんどん画面に近く感じにして！」）：
#  ポニーと ハートは 世界の 座標（390×844 の 画面と 同じ 大きさ）で 作り、カメラで 画面へ：世界の FOCUS が 画面の at に くるように z 倍（アップ）。
#  ①から⑤へ だんだん 近く（z が 大きく）・どの 画面も その 間に PUSH_IN だけ 少しずつ 近づく（字の まん中を 中心に）。
#  耳の 先は 画面の 上・字の 下は 下に つもった ハートの 上（PILE_Y）に 入るように at を 決める（⑤ドアップは 耳の 先が 少し 画面の 外）。
#  ハート（と 字・前足）は カメラの 向きに かたむける（ry＝左右・rx＝上下。度。PERSP＝遠近の きょり。fs：斜め上からは 頭より 遠いので 少し 小さく）。
#  うしろ足は 下に つもった ハートに うまって 見えない（まさちゃん「そしたら、ど！、て！、のカットも後ろ脚を映さなくて良くなるから違和感なくせる！」）。
#  顔の 向き・上からの 角度・目線・頭の 高さは flat/premium_art.py（YAW・PITCH・GAZE・HEAD_C）
FOCUS = (195.0, 400.0)
CAMS = (dict(z=1.40, at=(195.0, 444.6), ry=14.0, rx=0.0, fs=1.0),       # ①ど！：右正面から アップ
        dict(z=1.46, at=(195.0, 452.5), ry=-14.0, rx=0.0, fs=1.0),      # ②て！：左正面から アップ（①の 左右 うらがえし・少し 近く）
        dict(z=1.52, at=(195.0, 467.1), ry=8.0, rx=-22.0, fs=.95),      # ③き！：右正面 斜め上から アップ
        dict(z=1.58, at=(195.0, 477.1), ry=-8.0, rx=-22.0, fs=.95),     # ④ちゅ！：左正面 斜め上から アップ（③の 左右 うらがえし）
        dict(z=1.66, at=(195.0, 426.0), ry=0.0, rx=0.0, fs=1.0))        # ⑤う！：真正面から ドアップ
PUSH_IN = 1.03                    # 1つの 画面の 間に カメラが 近づく 大きさ
PERSP = 1000.0
FIN_C, FIN_S = (195.0, 415.0), 185.0     # 大きな ハートの まん中と 大きさ（まさちゃん「ハートとど的中もう少し大きくして！」：165 → 185）
FIN_BOX = (-8.0, 213.0, 406.0, 395.0)    # 最後の ハートの 絵の 箱（flat/premium_art.py の pm_fin）
TITLE_Y, TITLE_K = 112.0, .48 * 165 / 185   # ボードの 上に 動いた ハートの まん中と 大きさ（ボードの 上では 前と 同じ 大きさ）
UP_VEIL = (.12, .77)                     # 上へ 動く 前に 白く なりはじめる（RES の 0.12秒 前）・白い 光の 長さ（動く 0.5秒の あと 0.15秒で 色が もどる）
PILE_COLS = (('#FF5FA6', '#FFC2DE', '#DD3484'), ('#FF8CC2', '#FFDCEC', '#EE5EA0'), ('#FFA9D1', '#FFEAF4', '#F07CB4'),   # つやつやの ゼリーの ハート：(色・光・かげ)
             ('#F25CC4', '#FFC8EE', '#C63A9E'), ('#FF7E9E', '#FFD3DC', '#E5547A'), ('#FFD1E6', '#FFFFFF', '#F2A0C6'))   # ホットピンク・ピンク・うすい ピンク・マゼンタ・コーラル・白っぽい ピンク


def sec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'


def hide(t0=None, t1=None, gap=None):
    """見えない 間は 描かない（まさちゃん「プレミアムど的中ボタンだけ試すと落ちちゃう！」）：
       出る 前・消えた あとの 絵も、アニメが ついていると 画面の 外の 層（合成の 層）の 画素を 使いつづける（ぜんぶで iPhone の 3倍の 画素で 約1GB）。
       t0 より 前・t1 より あと・gap＝(a, b) の 間は visibility:hidden（pmH）に して 描かない → animation に 足す 文（先頭に ,）"""
    o = ''
    if t0 is not None:
        o += f',pmH .001s linear {sec(t0)} backwards'
    if t1 is not None:
        o += f',pmH .001s linear {sec(t1)} forwards'
    if gap is not None:
        o += f',pmH {sec(gap[1] - gap[0])} linear {sec(gap[0])}'
    return o


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
    """背景の 上で ふわふわ うく つやつやの ゼリーの ハート（はば 58〜72px の ます：④の ウィンクの ハートより 少し 大きい）"""
    rnd = random.Random(21)
    o = ''
    for x, y, sz, rot in ((38, 214, 36, -14), (354, 206, 33, 12), (22, 648, 34, 10), (366, 654, 38, -12), (318, 296, 32, 8), (86, 112, 33, -8),
                          (300, 790, 32, 10), (60, 470, 32, -10)):
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
        s = rnd.uniform(12, 24)
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


# ---------------------------------------------------------------- ①〜⑤の ぷるるん（まさちゃん「ど！、て！、き！、ちゅ！、う！全部ハートと腕しか動いてないから不自然！
# 馬もプルンプルン系で、全体的に動いて！結構プルルンて感じにして！全体的に！でも身体が歪んだりは変だから構造は身体の構造を考えて作成して！」）
# 体の つくりどおりに：体（首・肩・前足・ハート）は 着地で 上下に はずむ（うしろ足は 下に つもった ハートに うまって 見えない）・頭は 首の 上を 中心に おくれて かたむく・
# 耳は つけねを 中心に・たてがみは 上の はしを 中心に・リボンは むすびめを 中心に ゆれる（どれも 形は ゆがめない。ゆがむのは ゼリーの ハートと リボンだけ）。
# 入ってくる 間は 頭・耳・たてがみが 動く 向きと 反対へ おくれて、着いた時に ゆりもどす
JIG_D, JIG_N = 1.05, 30          # 1つの 画面の 動きの 長さ（秒：入ってくる 所から 次の 画面まで）・キーフレームの 数
IMPACT = .30                     # 着地（入ってくる 動きの 0.30秒め）


def osc(t, t0, amp, f, tau, ph=0.0):
    """t0 から はじまる だんだん 小さくなる ゆれ（amp・f＝1秒の 回数・tau＝小さくなる 速さ）"""
    if t < t0:
        return 0.0
    u = t - t0
    return amp * math.exp(-u / tau) * math.sin(2 * math.pi * f * u + ph)


def entry_lag(t, frm):
    """入ってくる 間の おくれ（画面で：右へ 動く 時は 頭が 左へ かたむく＝−。度）と、着いてから の ゆりもどし。frm：入ってくる 方"""
    a0 = dict(L=-6.0, R=6.0).get(frm, 0.0)
    if not a0 or t <= 0:
        return 0.0
    if t < IMPACT:
        x = min(1.0, t / .12)
        return a0 * x * x * (3 - 2 * x)
    u = t - IMPACT
    return a0 * math.exp(-u / .2) * math.cos(2 * math.pi * JIG_F * u)


def rise_lag(t, frm):
    """下から 上がる 時は 頭が 下へ おくれる（＋）・上から 落ちる 時は 上へ おくれる（−）：px。着いてから ゆりもどす"""
    a0 = dict(B=6.0, T=-5.0).get(frm, 0.0)
    if not a0 or t <= 0:
        return 0.0
    if t < IMPACT:
        x = min(1.0, t / .12)
        return a0 * x * x * (3 - 2 * x)
    u = t - IMPACT
    return a0 * math.exp(-u / .15) * math.cos(2 * math.pi * JIG_F * u)


JIG_F, JIG_TAU = 3.0, .26        # ゆれの 速さ（1秒に 3回）と 小さくなる 速さ：体から 頭・リボン・耳・たてがみへ 少しずつ おくれて つたわる（同じ 速さで ゆれる＝ばらばらに ちらつかない）


def pony_motion(frm, mir, g=1.0):
    """部品ごとの 動き（t 秒 → CSS の transform）。mir：左右 うらがえした 顔（かたむきの 向きを 画面に あわせる）。
       g：ゆれの 大きさ（カメラの アップで 画面の 上の 動きが 大きく なりすぎないように：JIG_G）"""
    sg = -1.0 if mir else 1.0
    amp = dict(T=17.0, C=12.0).get(frm, 14.0) * g                  # 着地で 体が 沈む 大きさ（上から 落ちる 時は 大きく）
    F, TAU = JIG_F, JIG_TAU

    def tilt(t, d=0.0, k=1.0):
        return sg * k * g * entry_lag(t - d, frm)

    def bow(t):
        q = osc(t, IMPACT + .04, .09 * g, F, TAU, math.pi / 2)
        return f'rotate({tilt(t, .02, 1.3) + osc(t, IMPACT + .04, 11.0 * g, F, TAU):.2f}deg) scale({1 + q:.3f},{1 - q:.3f})'

    def ear(sd):
        return lambda t: f'rotate({tilt(t, .03, 1.5) + sd * g * (osc(t, IMPACT + .05, 13.0, F, TAU) + 1.4 * rise_lag(t - .02, frm)):.2f}deg)'

    return dict(
        body=lambda t: f'translateY({osc(t, IMPACT, amp, F, TAU):.2f}px)',
        head=lambda t: (f'translateY({g * (osc(t, IMPACT + .02, 6.0, F, TAU) + rise_lag(t, frm)):.2f}px) '
                        f'rotate({tilt(t) + g * osc(t, IMPACT + .03, 4.0, F, TAU):.2f}deg)'),
        mane=lambda t: f'rotate({tilt(t, .05, 1.2) + g * osc(t, IMPACT + .07, 5.0, F, TAU):.2f}deg)',
        earL=ear(-1.0), earR=ear(1.0), bow=bow,
        heart=lambda t: f'scale({1 + g * osc(t, IMPACT + .01, .055, F, TAU):.3f},{1 - g * osc(t, IMPACT + .01, .11, F, TAU):.3f})',
    )


JIG_G = 1.0          # カメラの 倍率 z の とき ゆれを z**-JIG_G 倍（1＝画面の 上の 動きは アップ 前と 同じ）


def pony_css():
    """①〜⑤の キーフレーム（pmJ<部品><画面>）"""
    out = ''
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        for name, fn in pony_motion(frm, FACE[face][1], CAMS[i]['z'] ** -JIG_G).items():
            stops = ''.join(f'{k * 100 / JIG_N:.4g}%{{transform:{fn(JIG_D * k / JIG_N)}}}' for k in range(JIG_N + 1))
            out += f'@keyframes pmJ{name}{i}{{{stops}}}\n'
    return out


def pimg(name, at):
    """部品の 絵（at＝親の 動きの 中心から の 場所）"""
    x, y, w, h = art()[1][name]
    return f'<img class="pmi" src="{blob(name)}" alt="" style="left:{x - at[0]:.3f}px;top:{y - at[1]:.3f}px;width:{w:.3f}px;height:{h:.3f}px">'


def joint(at, parent, inner, anim=''):
    """動きの 中心（関節）：at に 置いた 大きさ 0 の 箱（transform-origin が 関節）"""
    st = f'left:{at[0] - parent[0]:.2f}px;top:{at[1] - parent[1]:.2f}px'
    return f'<div class="pmJ" style="{st}{";animation:" + anim if anim else ""}">{inner}</div>'


def cam_tf(i, k=1.0):
    """①〜⑤の カメラの transform（k：その 画面の 間に 近づいた 大きさ。字の まん中を 中心に）"""
    c = CAMS[i]
    z = c['z']
    tx, ty = c['at'][0] - FOCUS[0] * z, c['at'][1] - FOCUS[1] * z
    if k != 1.0:
        px, py = cam_pt(i, (HEART_C[0], HEART_C[1] - 6))
        tx, ty, z = px + k * (tx - px), py + k * (ty - py), z * k
    return f'translate({tx:.2f}px,{ty:.2f}px) scale({z:.4f})'


def camera(i, inner):
    """カメラ：世界の 座標の 絵を ①〜⑤の 画面へ（世界の FOCUS → 画面の at・z 倍）。その 画面の 間に PUSH_IN だけ 近づく（pmCam…）"""
    S = PC_T['S']
    t_in = S[i]
    t_end = S[i + 1] if i + 1 < len(S) else PC_T['FIN']
    return (f'<div class="pmJ" style="left:0;top:0;transform:{cam_tf(i)};animation:pmCam{i} {sec(t_end - t_in)} linear {sec(t_in)} both">'
            f'{inner}</div>')


def cam_css():
    """カメラが 近づく キーフレーム（pmCam…）"""
    return ''.join(f'@keyframes pmCam{i}{{from{{transform:{cam_tf(i)}}}to{{transform:{cam_tf(i, PUSH_IN)}}}}}\n' for i in range(len(CAMS)))


def cam_pt(i, p, mir=False):
    """世界の 点 → ①〜⑤の 画面の 点（近づく 前。mir：左右 うらがえした ポニーの 点）"""
    c = CAMS[i]
    x = 390 - p[0] if mir else p[0]
    return c['at'][0] + (x - FOCUS[0]) * c['z'], c['at'][1] + (p[1] - FOCUS[1]) * c['z']


def pony_tree(i, face, t_in):
    """①〜⑤の 絵（カメラの 中）：体（首・頭（たてがみ・耳・顔・リボン））→ カメラの 向きに かたむいた ハート（字）と 前足。
       うしろ足は 下に つもった ハートに うまって 見えない。左右 うらがえす 顔は ポニーだけ うらがえす（字は うらがえさない）"""
    hv, mir = FACE[face]
    c = CAMS[i]
    R = art()[1]['rig'][hv]
    hp = art()[1]['rig']['heart']
    an = lambda n: f'pmJ{n}{i} {sec(JIG_D)} linear {sec(t_in)} both'
    O, M, B = (0.0, 0.0), (195.0, 0.0), (195.0, 400.0)            # 世界の 左上・左右 うらがえす 中心・体（上下に はずむ）
    hd = R['head']
    head = (joint(R['mane'], hd, pimg(f'pm_mane_{hv}', R['mane']), an('mane'))
            + joint(R['earL'], hd, pimg(f'pm_earL_{hv}', R['earL']), an('earL'))
            + joint(R['earR'], hd, pimg(f'pm_earR_{hv}', R['earR']), an('earR'))
            + pimg(f'pm_face_{hv}', hd)
            + joint(R['bow'], hd, pimg(f'pm_bow_{hv}', R['bow']), an('bow')))
    body = pimg(f'pm_neck_{hv}', B) + joint(hd, B, head, an('head'))
    pony = f'<div class="pmJ{" pmM" if mir else ""}" style="left:{M[0]:.0f}px;top:0">{joint(B, M, body, an("body"))}</div>'
    tilt = (f'<div class="pmJ" style="left:{HEART_C[0] - B[0]:.2f}px;top:{HEART_C[1] - B[1]:.2f}px;'
            f'transform:perspective({PERSP:g}px) rotateX({c["rx"]:g}deg) rotateY({c["ry"]:g}deg) scale({c["fs"]:g})">'
            f'{joint(hp, HEART_C, pimg("pm_heart", hp) + pimg(f"pm_t{i}", hp), an("heart"))}{pimg("pm_hoof", HEART_C)}</div>')
    front = joint(B, O, tilt, an('body'))
    return camera(i, pony + front)


# ---------------------------------------------------------------- オーラと ハート（まさちゃん「馬とハートが登場してプルルンと揺れる時に、
# 光沢があるピンクと白のオーラが全体的に馬とハートから出るようにして！ハートも周りに飛ぶように！」
# 「背景のオーラとハートはもっと多くていいよ！画面馬とハート以外の画面埋まるくらい！」）
AURA_T = (IMPACT - .02, .9)              # まわりの 光（.pmQ・.pmQi）：着地の 少し 前から 0.9秒
# 光は drop-shadow を 1つずつ：中（.pmQi）＝白い ふち・外（.pmQ）＝ピンクの 光。drop-shadow を 1つの 箱に 2つ 以上 かさねると、
# iPhone（Safari）では 画面の 合成で 描けず、動く ポニーを 毎コマ 描きなおす（重い）ので 分けた（まさちゃん「プレミアムど的中ボタンだけ試すと落ちちゃう！」）
AURA_W = ('drop-shadow(0 0 4px #FFFFFF)',                      # 白い ふち：ふだん
          'drop-shadow(0 0 10px #FFFFFF)',                     # 着地（いちばん 強い）
          'drop-shadow(0 0 8px rgba(255,255,255,.95))')        # ゆっくり もどる
AURA_P = ('drop-shadow(0 0 0 rgba(255,95,175,0))',             # ピンクの 光：ふだん（なし）
          'drop-shadow(0 0 36px rgba(255,95,175,.95))',        # 着地（いちばん 強い）
          'drop-shadow(0 0 30px rgba(255,95,175,.88))')        # ゆっくり もどる
RIP_T = (IMPACT - .02, IMPACT + .3)       # 外へ 広がる つやつやの オーラ（pm_aura_…）：着地と 0.32秒 あと
RIP_D, RIP_S = .9, 1.55                  # 広がる 長さ（秒）・どこまで 広がるか（倍：画面の はしまで）


def ripple(i, face, t_in):
    """外へ 広がる つやつやの ピンクと 白の オーラ（ポニーと かたむいた ハートの 形：pm_aura_…・ポニーと いっしょに 左右 うらがえす）"""
    hv, mir = FACE[face]
    name = f'pm_aura_{hv}'
    ac = art()[1]['rig'][hv]['aura']
    x, y, w, h = art()[1][name]
    M = (195.0, 0.0)
    S = PC_T['S']
    t_end = S[i + 1] if i + 1 < len(S) else PC_T['FIN']                 # この 画面が 消える 時
    rr = ''.join(f'<img class="pmi" src="{blob(name)}" alt="" style="left:{x - M[0]:.3f}px;top:{y - M[1]:.3f}px;width:{w:.3f}px;height:{h:.3f}px;'
                 f'transform-origin:{ac[0] - x:.3f}px {ac[1] - y:.3f}px;opacity:0;'
                 f'animation:pmRip {sec(RIP_D)} cubic-bezier(.2,.65,.35,1) {sec(t_in + t)} both{hide(t_in + t, min(t_in + t + RIP_D, t_end))}">'
                 for t in RIP_T)
    return camera(i, f'<div class="pmJ{" pmM" if mir else ""}" style="left:{M[0]:.0f}px;top:0">{rr}</div>')


HEART_W = (70.0, 88.0)                   # 下と まわりの ハートの ますの はば（ハートは ますの 9割：④の ウィンクの ハート（はば 約46px）より 大きい。
                                         #  まさちゃん「写真赤丸のハートより少し大きめにして！」「小さなハートは全体的にあと一回り大きく！」）
FRONT_Y, FRONT_RISE = 818.0, 26.0        # 前の 下の ハート（ポニーと ハートの 前：ハートの 先と 画面の 下の はし）の 上の はし・左右の はしで 高くなる 分（字に かからない）
BACK_Y, BACK_RISE = 690.0, 70.0          # うしろの 下の ハート（ポニーと ハートの うしろ：ハートの 左右の 下を うめる）の まん中の 上の はし・左右の はしで 高くなる 分
PUSH_R = 190.0                           # 着地で 前へ おされる ハートの はんい（ハートの 下の まん中から）
PILE_D = (46.0, 30.0)                    # 下の ハートの ならび（よこ・たて：ずらして すきまなく）
SLOT_D = (48.0, 36.0)                    # まわりの ハートの ならび（よこ・たて：重ねて すきまを なくす）
BLOOM_FILL = (.25, .45, .65, .85, 1.0)   # ①〜⑤の カットインで、その 画面で 見える まわりの 場所を ハートで うめる わりあい（だんだん ふえて ⑤で ぜんぶ）
BLOOM_IN = (30, 40, 50, 60, 72)          # ①〜⑤で 入ってくる ハートの 数の めやす（うめる 場所が たりなければ もう うまった 所の 上に 重ねる。
                                         #  ①は 重ねる 所が ないので うめる 分だけ・⑤は のこり ぜんぶ。いまは 20・35・49・60・80こ：BLOOM_N）
BLOOM_T = .32                            # カットインから ハートが 入りおわるまで（秒：ポニーが 入ってくる 間）
SPARK_N = 16                             # 着地ごとに ふえる オーラの キラキラ（ハートの 上）


def pile_surface(x):
    """前の 下の ハートの 上の はし（画面の y）：字に かからない ひくさ・左右の はしで 少し 高い"""
    u = min(1.0, abs(x - 195.0) / 195.0)
    return FRONT_Y - FRONT_RISE * u * u


def back_surface(x):
    """うしろの 下の ハートの 上の はし（画面の y）：ハートの 左右の 下を うめる 高さ・左右の はしほど 高い"""
    u = min(1.0, abs(x - 195.0) / 195.0)
    return BACK_Y - BACK_RISE * u


def on_pony(i, x, y, k=1.0):
    """画面の 点が ①〜⑤の ポニーと ハートの 上か（ざっくり：ハート・頭・たてがみ・耳。k：形の 大きさの 倍）"""
    hv, mir = FACE[SCREENS[i][1]]
    R = art()[1]['rig'][hv]
    z = CAMS[i]['z'] * k
    hx, hy = cam_pt(i, R['hc'], mir)
    cx, cy = cam_pt(i, HEART_C)
    sd = 1 if mir else -1                                            # たてがみの がわ（右正面からの 顔は 左）
    return (((x - cx) / (182 * z)) ** 2 + ((y - cy) / (165 * z)) ** 2 < 1
            or ((x - hx) / (92 * z)) ** 2 + ((y - hy) / (118 * z)) ** 2 < 1
            or ((x - hx - sd * 88 * z / k) / (66 * z)) ** 2 + ((y - hy - 70 * z / k) / (150 * z)) ** 2 < 1
            or (abs(x - hx) < 70 * z and hy - 178 * z < y < hy))


def spark_uri():
    """オーラの キラキラ（白い 4つの 光の 星）"""
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-1 -1 2 2'><path d='{sparkle(0, 0, 1, .22)}' fill='#fff'/></svg>"
    return 'url("data:image/svg+xml,' + svg.replace('#', '%23') + '")'


def jelly_b(rnd):
    """ハートの 中の b：つやつやの ゼリーの ハート（6色）が ずっと ぷるんぷるん（pmJly：ゆっくり＝点めつ しない）"""
    return (f'<b class="pm{rnd.randrange(len(PILE_COLS))}" style="animation-duration:{rnd.uniform(1.3, 1.9):.2f}s;'
            f'animation-delay:-{rnd.uniform(0, 1.9):.2f}s"></b>')


def heart_slots(seed):
    """画面を すきま なく うめる まわりの ハートの 場所（ずらした ならび・うしろの 下の ハートの 上だけ）"""
    rnd = random.Random(seed)
    dx, dy = SLOT_D
    out = []
    y, r = -20.0, 0
    while y < 870:
        x = -18.0 + (r % 2) * dx / 2
        while x < 414:
            px, py = x + rnd.uniform(-5, 5), y + rnd.uniform(-4, 4)
            if py < back_surface(px) - 6:
                out.append((px, py))
            x += dx
        y += dy
        r += 1
    return out


def bloom_hearts(seed=61):
    """まわりを うめる つやつやの ゼリーの ハート（まさちゃん「背景にカットごとに入ってくるハートは、カットごとに増やして、
       最後は馬と馬が持ってるハート以外画面埋め尽くして！」「最後画面全体ハートで埋め尽くして、その上に馬のエフェクトが乗ってるイメージ！」
       「カットインごとに、背景にハート付け足されるエフェクト、カットインと同時にハート足されるようにして！」）：
       画面を すきま なく うめる 場所（heart_slots）を ①〜⑤の カットインと 同時に だんだん 多く うめる（ポニーが 入ってくる 方から とんできて ぷるんと とまる。
       消えないで ふえる）。⑤で のこりを ぜんぶ（ポニーの うしろも）うめて、ポニーが いなくなっても 画面ぜんぶ ハート（最後の ど的中も その 上）。
       オーラの キラキラは 着地で ハートの 上（.pmbk）→ (ハート, キラキラ)"""
    rnd = random.Random(seed)
    slots = heart_slots(seed + 1)
    rnd.shuffle(slots)
    seen = [[not on_pony(i, x, y, .8) for i in range(len(SCREENS))] for x, y in slots]   # その 画面で 見えるか（ふちの 近くも うめる）
    used = [False] * len(slots)
    o, sp = '', ''
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        t_cut = PC_T['S'][i]
        last = i == len(SCREENS) - 1
        vis = sum(1 for v in seen if v[i])
        want = round(vis * BLOOM_FILL[i]) - sum(1 for k, v in enumerate(seen) if v[i] and used[k])
        pick = [k for k in range(len(slots)) if seen[k][i] and not used[k]][:max(0, want)]
        if last:                                                     # ⑤：のこり ぜんぶ（ポニーの うしろも：最後に ポニーが いなくなっても すきまが ない）
            pick = [k for k in range(len(slots)) if not used[k]]
        for k in pick:
            used[k] = True
        pos = [slots[k] for k in pick]
        more = [k for k in range(len(slots)) if seen[k][i] and used[k] and k not in pick]   # もう うまった 所の 上に 重ねる
        rnd.shuffle(more)
        pos += [(slots[k][0] + rnd.uniform(-14, 14), slots[k][1] + rnd.uniform(-10, 10)) for k in more[:max(0, BLOOM_IN[i] - len(pos))]]
        rnd.shuffle(pos)
        cx, cy = cam_pt(i, (195.0, 430.0))
        for x, y in pos:
            s = rnd.uniform(*HEART_W)
            dist = rnd.uniform(40, 90)                               # ポニーが 入ってくる 方から とんでくる
            if frm == 'L':
                fx, fy, u = -dist, 0.0, x / 390
            elif frm == 'R':
                fx, fy, u = dist, 0.0, 1 - x / 390
            elif frm == 'B':
                fx, fy, u = 0.0, dist, 1 - y / 844
            elif frm == 'T':
                fx, fy, u = 0.0, -dist, y / 844
            else:
                L = math.hypot(x - cx, y - cy) or 1
                fx, fy, u = -(x - cx) / L * dist * .6, -(y - cy) / L * dist * .6, min(1.0, L / 480)
            d = t_cut + .02 + BLOOM_T * u + rnd.uniform(0, .08)
            o += (f'<i style="left:{x - s / 2:.1f}px;top:{y - s / 2:.1f}px;width:{s:.1f}px;height:{s:.1f}px;'
                  f'--fx:{fx:.0f}px;--fy:{fy:.0f}px;--r:{rnd.uniform(-30, 30):.0f}deg;animation:pmBl .5s cubic-bezier(.2,.8,.3,1) {sec(d)} both{hide(d)}">'
                  f'{jelly_b(rnd)}</i>')
        BLOOM_N[i] = len(pos)
        t0 = t_cut + IMPACT
        k2 = 0                                                       # オーラの キラキラ（白い 星：着地で ハートの 上に 出て ゆっくり またたく）
        for x, y in slots[::-1]:
            if k2 >= SPARK_N:
                break
            if on_pony(i, x, y):
                continue
            k2 += 1
            r = rnd.uniform(8, 16)
            d = t0 + .05 + math.hypot(x - cx, y - cy) / 950 + rnd.uniform(0, .12)
            sp += (f'<i class="sp" style="left:{x - r:.1f}px;top:{y - r:.1f}px;width:{r * 2:.1f}px;height:{r * 2:.1f}px;--fx:0px;--fy:0px;--r:0deg;'
                   f'animation:pmBl .5s cubic-bezier(.2,.8,.3,1) {sec(d)} both{hide(d)}">'
                   f'<b style="animation:pmTw {rnd.uniform(1.4, 2.2):.2f}s ease-in-out -{rnd.uniform(0, 2):.2f}s infinite alternate"></b></i>')
    return o, sp


BLOOM_N = [0] * 5                        # ①〜⑤で 入った まわりの ハートの 数（bloom_hearts が 書く：説明用）


def pile_bottom(seed=71):
    """画面の 下に すきまなく つもった つやつやの ゼリーの ハート（まさちゃん「画面下側は小さな光沢のあるプルンプルンしたハートが積もってて、
       そこに馬もハートも乗ってる感じにして！」「馬とハートが揺れる時に、下のハートも揺れて！」
       「馬とハートがカットインして、中央に入った時、近い位置にある小さな、馬とハートに押される感じで、前に移動して！」「画面下は、ハートで埋め尽くして！」
       「画面下は、最初のど！からハートで埋めつくて！」）：
       うしろ（ポニーと ハートの うしろ：ハートの 左右の 下を BACK まで うめる）と 前（ポニーと ハートの 前：ハートの 先と 画面の 下の はし）の 2つ。
       白い 光の 中で つもって いて、ずっと ぷるんぷるん。①〜⑤の 着地ごとに まん中から 外へ じゅんに ぷるん・前の まん中の 近くは 前（手前・下・外）へ おされて もどる。
       上の ハートほど うしろ・おされる ハートは いちばん 前 → (うしろ, 前)"""
    rnd = random.Random(seed)
    dx, dy = PILE_D
    cx, cy = 195.0, FRONT_Y + 10                                     # ハートの 下の まん中（おす 所）

    def heart(x, y, s, front):
        d = math.hypot(x - cx, (y - cy) * 1.4)
        f = max(0.0, 1 - d / PUSH_R) ** 1.3 if front else 0.0
        sg = 1 if x >= cx else -1
        if f > 0:
            px, py, g, w = sg * (16 + 36 * f) * f, (12 + 30 * f) * f, .3 * f, .1 + .05 * f
        else:
            px, py, g, w = 0.0, 0.0, 0.0, .09 * max(.3, 1 - d / 430)
        lag = d / 900
        anim = [f'pmPA .12s linear {sec(PC_T["BG"])} both']
        anim += [f'pmPP .8s linear {sec(t + IMPACT - .02 + lag)}' for t in PC_T['S']]
        return (f > 0, y, f'<i style="left:{x - s * 1.12:.1f}px;top:{y - s * 1.08:.1f}px;width:{s * 2.24:.1f}px;height:{s * 2.24:.1f}px;'
                          f'--px:{px:.1f}px;--py:{py:.1f}px;--g:{g:.3f};--w:{w:.3f};--r:{rnd.uniform(-28, 28):.0f}deg;animation:{",".join(anim)}">'
                          f'{jelly_b(rnd)}</i>')

    back, front = [], []
    y, row = 900.0, 0
    while y > BACK_Y - BACK_RISE - 40:
        x = -24.0 + (row % 2) * dx / 2 + rnd.uniform(-4, 4)
        while x < 418:
            yy = y + rnd.uniform(-4, 4)
            s = rnd.uniform(*HEART_W) / 2.24
            if yy >= pile_surface(x) - 8:
                front.append(heart(x, yy, s, True))
            elif yy >= back_surface(x) - 8:
                back.append(heart(x, yy, s, False))
            x += dx + rnd.uniform(-3, 3)
        y -= dy + rnd.uniform(-2, 2)
        row += 1
    back.sort(key=lambda it: it[1])                                  # 上（うしろ）→ 下（前）
    front.sort(key=lambda it: (it[0], it[1]))                        # おされる ハートは いちばん 前
    return ''.join(h for _, _, h in back), ''.join(h for _, _, h in front)


def pc_layers(board_html):
    """押したあと（下から）：虹色の 背景（パチンコの 大当たりのような 光線・ふわふわの ハート）→ つもる ハート → 回る 白い 光線・キラキラ →
       まわりを うめる ハート → ①〜⑤ の ポニーの アップ（カメラ。着いた時に オーラが 出て ハートが とびだす）→ 下に つもった 小さな ハート →
       最後の 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。
       board_html：テーマの ボード（gen_fx の board）"""
    T = PC_T
    hearts, n = pile_html()
    scr = ''
    S = T['S']
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        t_in = S[i]
        t_out = (S[i + 1] if i + 1 < len(S) else T['FIN']) - T['OUT']
        tree = pony_tree(i, face, t_in)
        scr += (f'<div class="pms" aria-hidden="true" style="animation:{enter_anim(frm)} {sec(T["IN"])} cubic-bezier(.25,.9,.35,1) {sec(t_in)} both,'
                f'pmOut {sec(T["OUT"])} linear {sec(t_out)} forwards{hide(t_in, t_out + T["OUT"])}">{ripple(i, face, t_in)}'
                f'<div class="pmQ" style="animation:pmAu {sec(AURA_T[1])} linear {sec(t_in + AURA_T[0])} both">'
                f'<div class="pmQi" style="animation:pmAw {sec(AURA_T[1])} linear {sec(t_in + AURA_T[0])} both">{tree}</div></div>'
                f'{veil(tree, t_in, T["IN"], hide(t1=t_in + T["IN"]))}</div>')
    back, front = pile_bottom()
    bloom, spark = bloom_hearts()
    fx, fy = FIN_C
    bx, by = BURST_C
    fin = img('pm_fin')
    up0 = T['RES'] - UP_VEIL[0]                                       # 最後の ハートが 上へ 動く 前に 白く なりはじめる 時
    pop_d = T['FIN'] + .28                                            # 最後の ハートの 白い 輪と とぶ ハート
    return f'''<div class="pmbg" aria-hidden="true"><img class="pmi" src="{blob('pm_bg')}" alt="" style="left:0;top:0;width:390px;height:844px">{bob_hearts()}</div>
    <div class="pmp" aria-hidden="true" style="animation:{hide(t1=T['W'][2])[1:]}">{hearts}</div>
    <div class="pml pmlb" style="animation:{hide(T['BURST'], T['W'][3])[1:]}">{pop_hearts(bx, by, T['BURST'], 20, 23, dist=(170, 300), size=(24, 40))}</div>
    <div class="pmpk" aria-hidden="true"><i class="rays"></i><i class="glow"></i><svg class="spk" viewBox="0 0 390 844">{twinkles(26, 5)}</svg></div>
    <div class="pmbh" aria-hidden="true">{bloom}</div>
    <div class="pmpl pmpb" aria-hidden="true">{back}</div>
    <div class="pmbh pmbk" aria-hidden="true">{spark}</div>
    {scr}
    <div class="pmpl" aria-hidden="true">{front}</div>
    <div class="pmu" aria-hidden="true">{rising_hearts(40, 9, T['FIN'])}</div>
    <div class="pmf" aria-hidden="true">{fin}{veil(fin, T["FIN"], .5, f",pmVu {sec(UP_VEIL[1])} linear {sec(up0)} forwards" + hide(t1=up0 + UP_VEIL[1], gap=(T['FIN'] + .5, up0)))}</div>
    <i class="pmr pmrf" style="--d:{sec(pop_d)};animation:pmRing .55s ease-out {sec(pop_d)} both{hide(pop_d, pop_d + .55)}"></i>
    <div class="pml" style="animation:{hide(pop_d, pop_d + .8)[1:]}">{pop_hearts(fx, fy - 10, pop_d, 18, 47, dist=(150, 230), size=(26, 42))}</div>
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
/* 見えない 間は 描かない（hide()：出る 前・消えた あとの 絵が 層の 画素を 使わない ように。iPhone で 落ちない ため） */
@keyframes pmH{{0%,100%{{visibility:hidden}}}}
/* 虹色の 背景（パチンコの 大当たりのような 光線・まん中の 白い 光・虹の 輪・さくら・キラキラ：pm_bg）の 上で つやつやの ハートが ふわふわ */
.ov.pm .pmbg{{position:absolute;inset:0;overflow:hidden;background:#FF6FC4}}
.ov.pm .pmbg .pmj{{position:absolute;display:block;transform:rotate(var(--r));animation:pmBob 2.8s ease-in-out infinite alternate}}
@keyframes pmBob{{to{{transform:translateY(-6px) rotate(var(--r))}}}}
/* つもる ハート：外の i＝はじける（{sec(T['BURST'])}〜・まん中から じゅんに・ぷくっと ふくらんで）・中の b＝上から 落ちる
   （b::before＝すき通った 光の ハート・b::after＝つもった 時に つやつやの ゼリーの ハートに なって ぷるんっ）。
   落ちてくる 前（画面の 上の 外）・つもる 前の ゼリーの ハート・消えた 光の ハート・はじけた ハートは pmH で 描かない（重さ対策） */
.ov.pm .pmp{{position:absolute;inset:0;z-index:2;pointer-events:none}}
.ov.pm .pmp i{{position:absolute;display:block;background:none!important;animation:pmB .24s linear var(--bd) forwards,pmH .001s linear calc(var(--bd) + .24s) forwards}}
.ov.pm .pmp b{{position:absolute;inset:0;transform:translateY(var(--y0)) rotate(var(--r0));animation:pmF var(--t) cubic-bezier(.333,0,.667,.333) var(--d) both,pmH .001s linear var(--d) backwards}}
.ov.pm .pmp b::before,.ov.pm .pmp b::after{{content:'';position:absolute;inset:0}}
.ov.pm .pmp b::before{{background:{fly_uri()} center/contain no-repeat;animation:pmLo .08s linear var(--l) forwards,pmH .001s linear calc(var(--l) + .08s) forwards}}
.ov.pm .pmp b::after{{opacity:0;transform-origin:50% 88%;animation:pmL .1s linear var(--l) forwards,pmJ .55s ease-out var(--l) both,pmH .001s linear var(--l) backwards}}
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
/* 白い 光の 中で 出る：細い 白い 光線（ゆっくり 回る＝大当たりの 光。1つの 所を 光線が 通るのは 1秒に 1回 くらい）・まん中の 光・キラキラ。
   光線の 箱は 画面の いちばん 遠い すみ（まん中から 509px）が 入る 大きさ（はば 1040px）：前の 1500px と 見た目は 同じで、層の 画素が 半分 */
.ov.pm .pmpk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;animation:fzOn .01s linear {sec(T['BG'])} forwards{hide(T['BG'])}}}
.ov.pm .pmpk .rays{{position:absolute;left:50%;top:{BG_C[1]:.0f}px;width:1040px;height:1040px;margin:-520px 0 0 -520px;border-radius:50%;opacity:.6;
  background:repeating-conic-gradient(rgba(255,255,255,.9) 0 2deg,rgba(255,255,255,0) 2deg 12deg);
  -webkit-mask-image:radial-gradient(circle 1060px,transparent 0 9%,#000 20%,#000 40%,transparent 62%);mask-image:radial-gradient(circle 1060px,transparent 0 9%,#000 20%,#000 40%,transparent 62%);
  animation:spin 36s linear infinite}}
.ov.pm .pmpk .glow{{position:absolute;left:50%;top:{BG_C[1]:.0f}px;width:440px;height:440px;margin:-220px 0 0 -220px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.6),rgba(255,255,255,.22) 40%,rgba(255,255,255,0) 70%)}}
.ov.pm .pmpk .spk{{position:absolute;inset:0;width:390px;height:844px}}
.ov.pm .pmpk .spk path{{animation:pmTw 1.6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes pmTw{{from{{opacity:.25;transform:scale(.55)}}to{{opacity:1;transform:scale(1)}}}}
/* ①〜⑤：ハートを だいた ポニーが 左・右・下・上から 入ってくる／まん中に 出る（1つ {sec(T['S'][1] - T['S'][0])}） */
.ov.pm .pms{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:5;opacity:0;pointer-events:none;transform-origin:{HEART_C[0]:.0f}px {HEART_C[1]:.0f}px}}
@keyframes pmInL{{0%{{opacity:1;transform:translateX(-480px) rotate(-7deg)}}72%{{transform:translateX(8px) rotate(1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInR{{0%{{opacity:1;transform:translateX(480px) rotate(7deg)}}72%{{transform:translateX(-8px) rotate(-1deg)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInB{{0%{{opacity:1;transform:translateY(900px)}}72%{{transform:translateY(-14px)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInT{{0%{{opacity:1;transform:translateY(-900px)}}72%{{transform:translateY(6px) scale(1.02,.98)}}100%{{opacity:1;transform:none}}}}
@keyframes pmInC{{0%{{opacity:0;transform:scale(.15)}}55%{{opacity:1;transform:scale(1.13)}}78%{{transform:scale(.95)}}100%{{opacity:1;transform:none}}}}
@keyframes pmOut{{from{{opacity:1}}to{{opacity:0}}}}
/* 白い 光の 形：入ってくる 間は 白く つつみ（0.92）、止まる 前に 消えて 色が つく */
.ov.pm .pmv{{position:absolute;inset:0;width:390px;height:844px;filter:brightness(0) invert(1);opacity:0;pointer-events:none}}
@keyframes pmVl{{0%,62%{{opacity:.92}}100%{{opacity:0}}}}
/* 最後の ハートが 上へ 動く 間も 白く つつむ（{sec(T['RES'] - UP_VEIL[0])}〜） */
@keyframes pmVu{{0%{{opacity:0}}{UP_VEIL[0] / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}{(UP_VEIL[0] + .5) / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}100%{{opacity:0}}}}
/* 最後の ハートが 着いた時：白い 輪と 小さな ハートが とびちる（①〜⑤は オーラと とぶ ハート） */
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
/* ①〜⑤：ポニーの ぷるるん（体の つくりどおり：関節＝大きさ 0 の 箱 .pmJ を 中心に 回す・上下に はずむ）。
   まわりの 白い 光の ふちは 動く 絵に あわせて つける（.pmQ） */
.ov.pm .pmJ{{position:absolute;width:0;height:0;transform-origin:0 0}}
.ov.pm .pmM{{transform:scaleX(-1)}}
/* オーラ（着地で ぷるるん する 間）：動く 絵に ついていく 白 → ピンクの 光（.pmQ の drop-shadow）と、外へ 広がる つやつやの オーラ（pm_aura_…・2回） */
.ov.pm .pmQ,.ov.pm .pmQi{{position:absolute;left:0;top:0;width:0;height:0}}
.ov.pm .pmQ{{filter:{AURA_P[0]}}}
.ov.pm .pmQi{{filter:{AURA_W[0]}}}
@keyframes pmAu{{0%,100%{{filter:{AURA_P[0]}}}12%{{filter:{AURA_P[1]}}}45%{{filter:{AURA_P[2]}}}}}
@keyframes pmAw{{0%,100%{{filter:{AURA_W[0]}}}12%{{filter:{AURA_W[1]}}}45%{{filter:{AURA_W[2]}}}}}
@keyframes pmRip{{0%{{opacity:0;transform:scale(.97)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale({RIP_S})}}}}
{pony_css()}{cam_css()}/* まわりを うめる ハート（ポニーの 方から 少し とんできて とまる・4こに 1こは ふわふわ・⑤で 画面ぜんぶ）・その 上の キラキラ・下に すきまなく つもった ハート（着地で ぷるん・まん中の 近くは 前へ おされる） */
.ov.pm .pmbh{{position:absolute;inset:0;z-index:4;pointer-events:none}}
.ov.pm .pmbh i,.ov.pm .pmpl i{{position:absolute;display:block;opacity:0}}
.ov.pm .pmbh b,.ov.pm .pmpl b{{position:absolute;inset:0;display:block;transform:rotate(var(--r));transform-origin:50% 82%;animation:pmJly 1.6s ease-in-out infinite}}
@keyframes pmJly{{0%,100%{{transform:rotate(var(--r)) scale(1.045,.955)}}50%{{transform:rotate(var(--r)) translateY(-2px) scale(.96,1.04)}}}}
@keyframes pmBl{{0%{{opacity:0;transform:translate(var(--fx),var(--fy)) scale(.3)}}25%{{opacity:1}}55%{{transform:translate(calc(var(--fx) * .1),calc(var(--fy) * .1)) scale(1.16,.88)}}
  78%{{transform:scale(.94,1.06)}}100%{{opacity:1;transform:none}}}}
@keyframes pmDis{{to{{opacity:0;transform:translateY(-34px) scale(.7)}}}}
.ov.pm .pmbh .sp b{{background:{spark_uri()} center/contain no-repeat;transform-origin:center}}
.ov.pm .pmpl{{position:absolute;inset:0;z-index:6;pointer-events:none;overflow:hidden;animation:{hide(T['BG'])[1:]}}}
.ov.pm .pmpb{{z-index:4}}
.ov.pm .pmpl i{{transform-origin:50% 75%}}
@keyframes pmPA{{to{{opacity:1}}}}
@keyframes pmPP{{0%{{transform:none}}
  14%{{transform:translate(var(--px),var(--py)) scale(calc(1 + var(--g) + var(--w)),calc(1 + var(--g) - var(--w)))}}
  32%{{transform:translate(calc(var(--px) * .8),calc(var(--py) * .8)) scale(calc(1 + var(--g) * .85 - var(--w) * .7),calc(1 + var(--g) * .85 + var(--w) * .7))}}
  52%{{transform:translate(calc(var(--px) * .5),calc(var(--py) * .5)) scale(calc(1 + var(--g) * .5 + var(--w) * .4),calc(1 + var(--g) * .5 - var(--w) * .4))}}
  74%{{transform:translate(calc(var(--px) * .2),calc(var(--py) * .2)) scale(calc(1 + var(--g) * .2 - var(--w) * .15),calc(1 + var(--g) * .2 + var(--w) * .15))}}
  100%{{transform:none}}}}/* 最後：大きな ハートの ど的中（{sec(T['FIN'])}）→ {sec(T['RES'])} に 上へ 動いて ボード */
.ov.pm .pmf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;opacity:0;pointer-events:none;transform-origin:{FIN_C[0]:.0f}px {fy:.0f}px;
  animation:pmInC .5s cubic-bezier(.25,.9,.35,1) {sec(T['FIN'])} both,pmBeat .9s ease-in-out {sec(T['FIN'] + .5)} 2,pmUp .5s cubic-bezier(.3,.8,.3,1) {sec(T['RES'])} forwards{hide(T['FIN'])}}}
@keyframes pmBeat{{0%,100%{{transform:none}}14%{{transform:scale(1.08,.93)}}30%{{transform:scale(.95,1.06)}}46%{{transform:scale(1.03,.97)}}62%{{transform:scale(.99,1.01)}}}}
@keyframes pmUp{{from{{opacity:1;transform:none}}to{{opacity:1;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.pm .pmu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {sec(T['FIN'])} forwards{hide(T['FIN'])}}}
.ov.pm .pmu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:pmRise var(--t) linear var(--d) infinite}}
@keyframes pmRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}25%{{transform:translate(calc(var(--w) * .5),-220px) scale(1.12,.9)}}
  50%{{transform:translate(var(--w),-440px) scale(.92,1.08)}}75%{{transform:translate(calc(var(--w) * .5),-670px) scale(1.06,.95)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.pm .hb{{z-index:8;animation:pmBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .12)} both{hide(T['RES'] + .12)}}}
@keyframes pmBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.pm .pmw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:pmWhite {sec(wd)} linear {sec(w0)} forwards{hide(w0, w3)}}}
@keyframes pmWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハート・回る 光線を 出さず、背景の 小さな ハートも 止める。虹色の 背景のまま 1秒 → まん中の 光と キラキラ・上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.pm .pmp,.ov.pm .pms,.ov.pm .pmr,.ov.pm .pml,.ov.pm .pmu,.ov.pm .pmw,.ov.pm .pmpk .rays,.ov.pm .pmf .pmv,.ov.pm .pmbh,.ov.pm .pmpl{{display:none}}
  .ov.fz.pm{{--t0:1.9s}}
  .ov.pm .pmpk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.pm .pmpk .spk path,.ov.pm .pmbg .pmj{{animation:none!important}}
  .ov.pm .pmf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.pm .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
