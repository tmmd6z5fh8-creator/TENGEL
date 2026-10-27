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
   「プレミアムど的中の馬とハートもっと光沢とプルンプルン感まして！ ど！て！き！ちゅ！う！の白とピンクのオーラはもっと幅を広く大きく演出して！」
   - つやは flat/premium_art.py（白い 毛の 上ぬり coat・ハートの ガラス glass）。ぷるるんは 1.35倍・ハートは もっと のびちぢみ ＋ 左右に ゆがむ。
     速さは 1秒に 2.2回（大きく ゆれる ほど 点めつが ふえるので ゆっくり 大きく：JIG_F・JIG_K・HEART_JIG）。
     オーラの 光は 着地で 白 24px・ピンク 66px に 広げて その 画面の おわりまで 広い まま（AURA_W・AURA_P）・外へ 広がる わは 太く 遠くまで（RIP_S）。
     ⑤で 画面が ハートで うまって いる 間は 光線を 描かない（PK_GAP：いちばん 多い 時 230MB）。点めつ 8.4%
   - 絵は ぜんぶ flat/premium_art.py で 作った WebP（キャンバスの アセット・リポジトリには 入れない。まさちゃんの 絵も 入れない・なぞっていない）：
     ポニーの 部品（顔の 向き 4つ：右正面から・右正面 斜め上から・その ウィンク・真正面 × 首・たてがみ・耳 左右・顔・リボン・オーラ。左は 左右 うらがえす）・
     ハート・字（ど！ など）・ひづめ・最後の「ど的中」・
     背景（パチンコの 大当たりのような 虹色の 光線）・つやつやの ゼリーの ハート 6色（つもる・とぶ・のぼる・ふわふわ ハート）
     premium_blobs.json（名前 → キャンバスの id）・premium_layers.json（名前 → 画面の 箱：flat/premium_art.py が 書く）
   - 背景の 上で 白い 光線が ゆっくり 回る（1つの 所を 光線が 通るのは 1秒に 1回 くらい＝点めつ しない）
   - 字（ど・て・き・ち・ゅ・う・！・的・中）は 太い まるい 線で 書いた 字（フォントを 使わない：GLYPHS。flat/premium_art.py が 使う）
   「プレミアムど的中演出、一枚目の画像のハートは、常にかわいくぷりんぷりん動いてるようにして！ あと、ど的中のハートは、上から落ちてきて地面にハートが
    積み重なってるところに落ちてくる演出にして！ 落ちてきた、ハートのど的中が落ちてきた時にプルンプルンして、光沢とゼリーのようなような柔らかい演出にして！
    ハートのど的中が落ちてきたら、下に積み重なってるハートは、弾けたり、こぼれ落ちたり、ズレたりする演出も入れて！ 立体的でリアルな画質でよろしく！」
   「ハート画面の中心に落ちてくるようにして！ あと、地面に落ちてきた感がかなり弱いから、積み重ねられてるハート達の上にハートのど的中が落ちてくる。を
    ちゃんとイメージできる演出にして！」「この青線いっぱいにハートがあって、落ちてきたらハートのど的中の先端が3/1くらいハートの地面に刺さるようにして！」
   「ど的中の文字も若干ハートで隠れてもいいくらい！ここはイメージだから任せる！ 3/1は落ちてきたあと埋まるように作ってみて！」
   「あと、ど！、て！、き！、ちゅ！、う！の映像もう少しだけど！からう！までいく速度早くして！」
   「このシーンもっと、全体的にぷるんぷるんにして！結果ボードでるところまで大きく揺れ続けて！」
   「落ちてきた時、ハートのど的中をもっとプルンプルン揺らして！ あと落ちてきたあとの他のハートの揺れ方も滑らかにして！」（第4.80版）
   - 背景の ふわふわ ハートは ずっと ぷりんぷりん（bob_hearts・pmPurin）・まわりの 小さな ハートも 1回 ぷりんっと はずむ（pmJly）
   - ①〜⑤は 1つ 1.0秒（PM_T：前は 1.2秒。超プレミアムは PC_T の まま）
   - 最後：まわりの ハートの 壁に もや（.pmhz：奥に 見える）→ 画面の 下に 横 いっぱいの ハートの 地面（heap_html：上の はしは 青い 線・光の ハートで 落ちて
     つもると ゼリーに・奥ほど 小さく）→ ゼリーの ハートが 上から 落ちて 先が 地面に 着いて ズボッと 刺さって ずぶずぶ うまる（ハートの 1/3：BURY・
     見えて いる 所の まん中が 画面の まん中）→ ぷるんぷるん（星空と 字は おくれて ゆれる・つやは すべる）・前の ハートは 前へ おされる・ふちの まわりは
     弾ける・こぼれ落ちる・ずれる（DROP・HEAP・BURY・JELLY・HIT・MOUND・fin_html・fin_css）→ ボードが 出る ころまで 大きな ハート・地面の ハート・
     まわりの ハートの 壁が いっしょに 左右に 大きく ぷるんぷるん（JELLY の SUS・PURIN・pmPB・pmBW）→ PC_RES（10.3秒）に 上へ 動いて ボード
   第4.86版 「地面のハートができるのと、ハートのど的中が落ちてくるテンポもう少し早くして！」：地面は FIN の すぐ あとに 0.34秒で つもり、ど的中は
     その とちゅうから 0.40秒で 落ちて FIN＋0.55秒（8.55秒）に 刺さる（前は 8.91秒）→ PC_RES 9.95秒に ボード（刺さってからは 前と 同じ 1.4秒）
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
# 第4.80版（まさちゃん「ど！、て！、き！、ちゅ！、う！の映像もう少しだけど！からう！までいく速度早くして！」）：プレミアムだけ ①〜⑤を 1つ 1.0秒に
#  （1.2秒 → 1.0秒・最後は 1秒 はやく）。PC_T は 超プレミアム（super_premium.py の ZP_T）と 超プレミアム神様（gen_fx の spg_events）が 使うので その まま。
#  RES は 使わない（プレミアムの ボードは PC_RES）
PM_T = dict(FILL=2.4, BURST=2.48, CHAIN=.16, W=(2.66, 2.78, 2.92, 3.32), BG=2.84,
            S=(3.0, 4.0, 5.0, 6.0, 7.0),   # ①〜⑤ の 画面（1つ 1.0秒）
            IN=.45, OUT=.12,
            FIN=8.0,                    # 地面が できて 大きな ハートの ど的中が 落ちる
            RES=9.95)                   # （PC_RES と 同じ）
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
HEART_K = ((0, -.5), (-.2, -.94), (-1.0, -1.0), (-1.02, -.4), (-1.04, .12), (-.44, .52), (0, .88))   # 大きな ハートの 左半分の 3次ベジェ（くぼみ → 左の 山 → とがった 先：flat/premium_art.py も 使う）
HEART_KY = .94                           # 大きな ハートの 高さ（はばに 対して 少し ひくく：まさちゃんの 絵の ハート）
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
    """背景の 上で ふわふわ うく つやつやの ゼリーの ハート（はば 58〜72px の ます：④の ウィンクの ハートより 少し 大きい）。
       第4.80版（まさちゃん「一枚目の画像のハートは、常にかわいくぷりんぷりん動いてるようにして！」）：外の i が ふわふわ うく（pmBob）・
       中の b が ずっと ぷりんぷりん（pmPurin：ぐにゅっと つぶれて ぴょこんと はねて ぷるん・ハートごとに 長さと はじまりが ちがう）"""
    rnd = random.Random(21)
    rp = random.Random(22)
    o = ''
    for x, y, sz, rot in ((38, 214, 36, -14), (354, 206, 33, 12), (22, 648, 34, 10), (366, 654, 38, -12), (318, 296, 32, 8), (86, 112, 33, -8),
                          (300, 790, 32, 10), (60, 470, 32, -10)):
        w = sz * 2.24
        k = rnd.choice((0, 1, 3, 4))                                 # 色と ふわふわの はじまりは 前と 同じ
        o += (f'<i class="pmj" style="left:{x - w / 2:.0f}px;top:{y - w / 2:.0f}px;width:{w:.0f}px;height:{w:.0f}px;'
              f'--r:{rot}deg;animation-delay:-{rnd.uniform(0, 3):.2f}s"><b class="pm{k}" style="animation-duration:{rp.uniform(1.15, 1.45):.2f}s;'
              f'animation-delay:-{rp.uniform(0, 1.4):.2f}s"></b></i>')
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
    t_first, t_last = .62, PM_T['FILL']
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
        bd = PM_T['BURST'] + PM_T['CHAIN'] * min(1.0, L / 480) + rnd.uniform(0, .02)
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


JIG_F, JIG_TAU = 2.2, .22        # ゆれの 速さ（1秒に 2.2回）と 小さくなる 速さ：体から 頭・リボン・耳・たてがみへ 少しずつ おくれて つたわる（同じ 速さで ゆれる＝ばらばらに ちらつかない）。
                                 #  第4.80版：①〜⑤が 1つ 1.0秒に なって 1秒の 中に ゆれ・消える・つぎの 画面が ぜんぶ 入る → .27 → .22（はじめの 大きな ゆれは 同じ・
                                 #  あとの 小さな ゆれが 早く おさまる）・広がる オーラは 1つに（RIP_T）：点めつ 11.2% → 7.2%
                                 #  まさちゃん「プレミアムど的中の馬とハートもっと光沢とプルンプルン感まして！」：ゆれを 1.35倍・少し 長く（.26 → .27）。
                                 #  速さは 3 → 2.2回：大きく ゆれる ほど ふちの 線が 同じ 所を 何回も 行き来して 点めつが ふえる（3回の まま 大きく すると 面積 13〜27%）。
                                 #  ゆっくり 大きく ぷるーん ぷるーん と ゆれる ほうが 点めつが 少ない（60コマ／秒で しらべて 8.4%）
JIG_K = 1.35                     # ゆれの 大きさ（前の 何倍：体・頭・耳・たてがみ・リボン）
HEART_JIG = (.075, .14, 1.8)     # ハートの ぷるんっ（よこに のびる・たてに ちぢむ・左右に ゆがむ（skewX・度）：前は .055・.11・0）


def pony_motion(frm, mir, g=1.0):
    """部品ごとの 動き（t 秒 → CSS の transform）。mir：左右 うらがえした 顔（かたむきの 向きを 画面に あわせる）。
       g：ゆれの 大きさ（カメラの アップで 画面の 上の 動きが 大きく なりすぎないように：JIG_G）"""
    sg = -1.0 if mir else 1.0
    amp = dict(T=17.0, C=12.0).get(frm, 14.0) * g * JIG_K         # 着地で 体が 沈む 大きさ（上から 落ちる 時は 大きく）
    F, TAU = JIG_F, JIG_TAU
    gk = g * JIG_K

    def tilt(t, d=0.0, k=1.0):
        return sg * k * g * entry_lag(t - d, frm)

    def bow(t):
        q = osc(t, IMPACT + .04, .09 * gk, F, TAU, math.pi / 2)
        return f'rotate({tilt(t, .02, 1.3) + osc(t, IMPACT + .04, 11.0 * gk, F, TAU):.2f}deg) scale({1 + q:.3f},{1 - q:.3f})'

    def ear(sd):
        return lambda t: f'rotate({tilt(t, .03, 1.5) + sd * (gk * osc(t, IMPACT + .05, 13.0, F, TAU) + g * 1.4 * rise_lag(t - .02, frm)):.2f}deg)'

    hx, hy, hk = HEART_JIG

    def heart(t):
        sk = f' skewX({g * osc(t, IMPACT + .06, hk, F, TAU, math.pi / 2):.2f}deg)' if hk else ''
        return f'scale({1 + g * osc(t, IMPACT + .01, hx, F, TAU):.3f},{1 - g * osc(t, IMPACT + .01, hy, F, TAU):.3f}){sk}'

    return dict(
        body=lambda t: f'translateY({osc(t, IMPACT, amp, F, TAU):.2f}px)',
        head=lambda t: (f'translateY({gk * osc(t, IMPACT + .02, 6.0, F, TAU) + g * rise_lag(t, frm):.2f}px) '
                        f'rotate({tilt(t) + gk * osc(t, IMPACT + .03, 4.0, F, TAU):.2f}deg)'),
        mane=lambda t: f'rotate({tilt(t, .05, 1.2) + gk * osc(t, IMPACT + .07, 5.0, F, TAU):.2f}deg)',
        earL=ear(-1.0), earR=ear(1.0), bow=bow, heart=heart,
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
    S = PM_T['S']
    t_in = S[i]
    t_end = S[i + 1] if i + 1 < len(S) else PM_T['FIN']
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
AURA_T = (IMPACT - .02, .9)              # まわりの 光（.pmQ・.pmQi）：着地の 少し 前から 0.9秒（その 画面の おわりまで）
# 光は drop-shadow を 1つずつ：中（.pmQi）＝白い ふち・外（.pmQ）＝ピンクの 光。drop-shadow を 1つの 箱に 2つ 以上 かさねると、
# iPhone（Safari）では 画面の 合成で 描けず、動く ポニーを 毎コマ 描きなおす（重い）ので 分けた（まさちゃん「プレミアムど的中ボタンだけ試すと落ちちゃう！」）
# まさちゃん「ど！て！き！ちゅ！う！の白とピンクのオーラはもっと幅を広く大きく演出して！」：着地で 白 10 → 24px・ピンク 36 → 66px に 広げて、
# もどらずに その 画面の おわりまで 広い まま（白 18px・ピンク 52px）。外へ 広がる わも 太く（pm_aura_…：はば 12 → 19）・遠くまで（1.55 → 1.8倍）・長く（0.9 → 1.05秒）
AURA_W = ('drop-shadow(0 0 5px #FFFFFF)',                      # 白い ふち：ふだん（入ってくる 間）
          'drop-shadow(0 0 24px #FFFFFF)',                     # 着地（いちばん 強い）
          'drop-shadow(0 0 20px rgba(255,255,255,.97))',       # ゆっくり もどる
          'drop-shadow(0 0 18px rgba(255,255,255,.95))')       # その 画面の おわりまで
AURA_P = ('drop-shadow(0 0 0 rgba(255,95,175,0))',             # ピンクの 光：ふだん（なし）
          'drop-shadow(0 0 66px rgba(255,95,175,.97))',        # 着地（いちばん 強い）
          'drop-shadow(0 0 58px rgba(255,95,175,.92))',        # ゆっくり もどる
          'drop-shadow(0 0 52px rgba(255,95,175,.88))')        # その 画面の おわりまで
RIP_T = (IMPACT - .02,)                   # 外へ 広がる つやつやの オーラ（pm_aura_…）：着地（第4.80版：①〜⑤が 1つ 1.0秒に なったので 0.32秒 あとの 2つめは やめた）
RIP_D, RIP_S = 1.05, 1.8                 # 広がる 長さ（秒）・どこまで 広がるか（倍：画面の はしの 外まで）
RIP_O = ''                       # 広がる わの こさの とちゅう（'40%{opacity:.88}…' で 大きく 広がる 間も こく できるが、点めつが ふえる ので 前と 同じ）
PK_GAP = (PM_T['S'][4] + .6, PM_T['FIN'])  # 光線と まん中の 光（.pmpk）は ⑤で まわりが ぜんぶ ハートで うまって ポニーが まん中に いる 間は 見えないので 描かない（いちばん 重い 時：広がる わが 2つ）。
#  第4.80版：最後も まわりの ハートの 壁と もやで 見えないので PK_GAP[0] から あとは ずっと 描かない（ゼリーの ハートと ハートの 地面の 分：40MB）


def ripple(i, face, t_in):
    """外へ 広がる つやつやの ピンクと 白の オーラ（ポニーと かたむいた ハートの 形：pm_aura_…・ポニーと いっしょに 左右 うらがえす）"""
    hv, mir = FACE[face]
    name = f'pm_aura_{hv}'
    ac = art()[1]['rig'][hv]['aura']
    x, y, w, h = art()[1][name]
    M = (195.0, 0.0)
    S = PM_T['S']
    t_end = S[i + 1] if i + 1 < len(S) else PM_T['FIN']                 # この 画面が 消える 時
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


def jelly_b(rnd, info=None):
    """ハートの 中の b：つやつやの ゼリーの ハート（6色）が ずっと ぷるんぷるん（pmJly：1回 ぷりんっと はずんで しずまる・
       ハートごとに 長さと はじまりが ちがう＝点めつ しない）。info：色を 書く（dict）"""
    k = rnd.randrange(len(PILE_COLS))
    if info is not None:
        info['k'] = k
    return (f'<b class="pm{k}" style="animation-duration:{rnd.uniform(1.3, 1.9):.2f}s;'
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


def bloom_hearts(seed=61, plan=None):
    """まわりを うめる つやつやの ゼリーの ハート（まさちゃん「背景にカットごとに入ってくるハートは、カットごとに増やして、
       最後は馬と馬が持ってるハート以外画面埋め尽くして！」「最後画面全体ハートで埋め尽くして、その上に馬のエフェクトが乗ってるイメージ！」
       「カットインごとに、背景にハート付け足されるエフェクト、カットインと同時にハート足されるようにして！」）：
       画面を すきま なく うめる 場所（heart_slots）を ①〜⑤の カットインと 同時に だんだん 多く うめる（ポニーが 入ってくる 方から とんできて ぷるんと とまる。
       消えないで ふえる）。⑤で のこりを ぜんぶ（ポニーの うしろも）うめて、ポニーが いなくなっても 画面ぜんぶ ハート（最後の ど的中も その 上）。
       オーラの キラキラは 着地で ハートの 上（.pmbk）。最後の ゼリーの ハートの 着地で 近くの ハートは ずれる（下の 近くは こぼれ落ちる：hit_react）→ (ハート, キラキラ)"""
    rnd = random.Random(seed)
    rh = random.Random(seed + 500)                                   # 最後の 着地の ための 乱数（ならびは 前と 同じ）
    slots = heart_slots(seed + 1)
    rnd.shuffle(slots)
    seen = [[not on_pony(i, x, y, .8) for i in range(len(SCREENS))] for x, y in slots]   # その 画面で 見えるか（ふちの 近くも うめる）
    used = [False] * len(slots)
    o, sp = '', ''
    for i, (text, face, frm, s_txt) in enumerate(SCREENS):
        t_cut = PM_T['S'][i]
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
            r = rnd.uniform(-30, 30)
            info = {}
            b = jelly_b(rnd, info)
            more, var = hit_react(x, y, s / 2.24, info['k'], r, rh, 'bloom', plan)
            if plan is not None and not inside(FIN_POLY, x, y):          # 刺さってから ボードまで 壁も ぷるんぷるん（ずれる ハートは ずれ おわってから）
                tw = max(LAND_T + PURIN['WT'], hit_time(x, y) + .52 if 'pmSh' in more else 0.0)
                more += f',pmBW {sec(PURIN["PD"] * PURIN["N"])} linear {tw:.3f}s'
            o += (f'<i style="left:{x - s / 2:.1f}px;top:{y - s / 2:.1f}px;width:{s:.1f}px;height:{s:.1f}px;'
                  f'--fx:{fx:.0f}px;--fy:{fy:.0f}px;--r:{r:.0f}deg;{var}animation:pmBl .5s cubic-bezier(.2,.8,.3,1) {sec(d)} both{hide(d)}{more}">'
                  f'{b}</i>')
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


def pile_bottom(seed=71, plan=None):
    """画面の 下に すきまなく つもった つやつやの ゼリーの ハート（まさちゃん「画面下側は小さな光沢のあるプルンプルンしたハートが積もってて、
       そこに馬もハートも乗ってる感じにして！」「馬とハートが揺れる時に、下のハートも揺れて！」
       「馬とハートがカットインして、中央に入った時、近い位置にある小さな、馬とハートに押される感じで、前に移動して！」「画面下は、ハートで埋め尽くして！」
       「画面下は、最初のど！からハートで埋めつくて！」）：
       うしろ（ポニーと ハートの うしろ：ハートの 左右の 下を BACK まで うめる）と 前（ポニーと ハートの 前：ハートの 先と 画面の 下の はし）の 2つ。
       白い 光の 中で つもって いて、ずっと ぷるんぷるん。①〜⑤の 着地ごとに まん中から 外へ じゅんに ぷるん・前の まん中の 近くは 前（手前・下・外）へ おされて もどる。
       上の ハートほど うしろ・おされる ハートは いちばん 前 → (うしろ, 前)。
       plan：最後の ゼリーの ハートの 着地で 動かす とき（FinPlan・hit_react。第4.80版の 山の 前は 使わない）"""
    rnd = random.Random(seed)
    rh = random.Random(seed + 500)                                   # 最後の 着地の ための 乱数（ならびは 前と 同じ）
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
        anim = [f'pmPA .12s linear {sec(PM_T["BG"])} both']
        anim += [f'pmPP .8s linear {sec(t + IMPACT - .02 + lag)}' for t in PM_T['S']]
        r = rnd.uniform(-28, 28)
        info = {}
        b = jelly_b(rnd, info)
        more, var = hit_react(x, y, s, info['k'], r, rh, 'front' if front else 'back', plan)
        return (f > 0, y, f'<i style="left:{x - s * 1.12:.1f}px;top:{y - s * 1.08:.1f}px;width:{s * 2.24:.1f}px;height:{s * 2.24:.1f}px;'
                          f'--px:{px:.1f}px;--py:{py:.1f}px;--g:{g:.3f};--w:{w:.3f};--r:{r:.0f}deg;{var}animation:{",".join(anim)}{more}">'
                          f'{b}</i>')

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



# ---------------------------------------------------------------- 最後の ゼリーの ハート（第4.80版）
# まさちゃん「ど的中のハートは、上から落ちてきて地面にハートが積み重なってるところに落ちてくる演出にして！ 落ちてきた、ハートのど的中が落ちてきた時に
#  プルンプルンして、光沢とゼリーのようなような柔らかい演出にして！ ハートのど的中が落ちてきたら、下に積み重なってるハートは、弾けたり、こぼれ落ちたり、
#  ズレたりする演出も入れて！ 立体的でリアルな画質でよろしく！」→（ためしを 見て）「ハート画面の中心に落ちてくるようにして！ あと、地面に落ちてきた感が
#  かなり弱いから、積み重ねられてるハート達の上にハートのど的中が落ちてくる。をちゃんとイメージできる演出にして！」→（2回目の ためしに 青い 線を 引いて）
#  「この青線いっぱいにハートがあって、落ちてきたらハートのど的中の先端が3/1くらいハートの地面に刺さるようにして！」「ど的中の文字も若干ハートで
#  隠れてもいいくらい！ここはイメージだから任せる！ 3/1は落ちてきたあと埋まるように作ってみて！」
# - FIN（8.0秒）：ポニーが 消えると、まわりの ハートの 壁に うすい もや（.pmhz：奥に 見える）・画面の 下に 横 いっぱいの **ハートの 地面**（.pmhp：HEAP。
#   上の はしは まさちゃんの 青い 線＝ど的中の 字の 下・奥＝上ほど 小さな ハート）が 下の 段から 上の 段へ ポンポン つもる。
# - FIN＋DROP の AT に 画面の 上の 外から ゼリーの ハートが 落ちて（止まっている 所から だんだん 速く：.pmf の pmDrop）、LAND_T に ハートの 先が
#   地面に 着く → **ズボッと 刺さって ずぶずぶ うまる**（ハートの 高さの 1/3：BURY。地面は 大きな ハートより 前）。
#   うまった ハートの 見えて いる 所の まん中が 画面の まん中。
# - ゼリーの ハート（.pmfj：字の 少し 下が 中心）：落ちる 間は 少し たてに のびて → 刺さった 所で ぐにゃっと つぶれて ぷるんぷるん（ばね）・
#   左右に ゆれる・上が ずれる・つぶれる 時に 上が 手前へ。おさまったら ずっと ゆっくり ぷるん（ボードの 上でも）。星空と 字（.pmfw）は
#   ゼリーの 中に うかんで おくれて ゆれる・つや（.pmfg）は 体の 上を すべる・右上の 小さな ハート（.pmfs）は ぴょこんと はねる。
#   うしろの ハートに 落ちる かげ（pm_fin_sh）・地面に 落ちる 丸い かげ（.pmfc：近づくほど こく 大きく）・地面の 上の 白い 輪
# - 地面の ハート：刺さった ハートの 前の ハートは 前へ おされて ぷるん（のこる：うまった 先は 見えない）・ハートの ふちの まわりの 上の ハートは
#   弾ける・とびだして こぼれ落ちる（画面の 下へ）・もっと まわりは 外へ ずれて とまる。先の まわりの 小さな ハートは 弾ける／とびだす・とびちる 小さな ハート


def smooth01(v):
    v = min(1.0, max(0.0, v))
    return v * v * (3 - 2 * v)


def spring(x0, v0, f, z, t):
    """ばねの ゆれ（はじめ x0・速さ v0・1秒に f 回・へり方 z）の t 秒あと"""
    if t <= 0:
        return x0
    w = 2 * math.pi * f
    wd = w * math.sqrt(1 - z * z)
    return math.exp(-z * w * t) * (x0 * math.cos(wd * t) + (v0 + z * w * x0) / wd * math.sin(wd * t))


def heart_poly(cx, cy, s, ky=HEART_KY, n=16):
    """大きな ハートの ふちの 点（左回り）"""
    p = [(cx + x * s, cy + y * s * ky) for x, y in HEART_K]

    def bez(a, b, c, d, t):
        u = 1 - t
        return (u ** 3 * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t ** 3 * d[0],
                u ** 3 * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t ** 3 * d[1])
    left = [bez(p[0], p[1], p[2], p[3], i / n) for i in range(n)] + [bez(p[3], p[4], p[5], p[6], i / n) for i in range(n + 1)]
    return left + [(2 * cx - x, y) for x, y in reversed(left[1:-1])]


def inside(poly, x, y):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def half_width(poly, cx, y):
    """ハートの 形の y での はばの 半分（ふちを よこぎる 所の いちばん 外）"""
    w = 0.0
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y):
            w = max(w, abs(x1 + (y - y1) * (x2 - x1) / (y2 - y1) - cx))
    return w


# 第4.86版（まさちゃん「地面のハートができるのと、ハートのど的中が落ちてくるテンポもう少し早くして！」）：地面は FIN の 0.08秒 前から 0.34秒で
#  （前は 0.42秒：いちばん 下の 段は ポニーが 消えた 瞬間に つもる・1つの ハートの 落ちる 長さも 少し 短く）・ど的中は 地面が できる とちゅうから 落ちはじめて
#  （前は 地面が できてから）0.40秒で 落ちる（前は 0.46秒）→ 先が 地面に 着くのは FIN から 0.55秒（前は 0.91秒）。地面が できおわってから ハートが 見えるまでの
#  間（前は 0.3秒 くらい 何も 動かない）が ほぼ なくなる。刺さってから ボードまでは 前と 同じ 1.4秒（PC_RES を 0.35秒 はやく）
DROP = dict(AT=.15,             # FIN から 落ちはじめまで（地面が できる とちゅう：画面の 上の 外なので 見えない。前は .45）
            T=.40,              # 落ちる 時間（止まっている 所から だんだん 速く：ハートの 先が 地面に 着くまで。前は .46）
            FROM=220.0)         # 落ちはじめ：ハートの 先が 画面の 上の はしより 220px 上（ハート ぜんぶが 画面の 上の 外：画面に 入る 時は もう 速い＝点めつ しない）
PC_RES = 9.95                   # プレミアムだけ：ハートが 上へ 動いて ボード（PM_T：①〜⑤が 1つ 1.0秒・刺さってから 1.4秒。前は 10.3。超プレミアムは PC_T の RES 10.9 の まま）
HEAP = dict(T=(-.08, .26),      # 地面が できる（FIN から：下の 段から 上の 段へ ポンポン つもる。いちばん 下の 段は FIN＋0.02秒・上の はしは 0.26秒まで。前は (0, .42)）
            TOP=526.0,          # 地面の 上の はし（まん中の 画面の y：まさちゃんの 青い 線＝ど的中の 字の 下。ハートの 先から 1/3 が ここより 下に うまる）
            WAVE=(6.0, 210.0, .7),   # 上の はしの ゆるい 波（高さ px・長さ px・ずれ）
            W=(74.0, 122.0),    # ハートの ますの はば（上＝奥は 小さく・下＝手前は 大きく：立体に 見える）
            ROW=.38, COL=.56,   # 段の 間・よこの 間（ますの はばに 対して：すきまなく）
            D=(110.0, 170.0),   # 落ちてくる 長さ（少し 上から ポンと 落ちて つもる。前は 130〜210）
            HAZE=(-.12, 0.0))   # まわりの ハートの 壁の もや（FIN から：ポニーが 消える 間に うすく なって 奥に 見える。第4.86版：ポニーが 消えるのと 同じ 0.12秒で
                                #  （前は FIN＋0.2秒まで）＝ど的中が 刺さる 1秒 前までに 明るさが かわりおわる：点めつ。地面と ど的中を 早く した ぶん）
BURY = dict(K=.333,             # 地面に うまる 所（ハートの 高さの わり合い：まさちゃん「先端が3/1くらい」）
            A=.8, TAU=(.03, .2),     # うまる 動き：A の 分が TAU[0] 秒で ズボッ・のこりが TAU[1] 秒で ずぶずぶ（はじめの 速さは 落ちる 速さの 7わり くらい。
                                     #  ゆっくり 長く 動くと 星空と 字で 点めつ）
            D=.95, N=36)        # うまる 動きの 長さ（地面に 着いてから 秒）・キーフレームの 数
FIN_TIP = FIN_C[1] + HEART_K[6][1] * FIN_S * HEART_KY + 3.4       # 絵の ハートの 先（こい 赤の ふちの 外：落ちる 前の 画面の y）
FIN_TOPY = min(y for x, y in heart_poly(FIN_C[0], FIN_C[1], FIN_S, n=48)) - 3.4   # 絵の ハートの 上の はし（左右の 山の ふちの 外）
BURY_D = (FIN_TIP - FIN_TOPY) * BURY['K']                           # うまる 深さ（px）
FIN_DY = HEAP['TOP'] + BURY_D - FIN_TIP                             # うまった ハートの 下げ（絵の 場所から：見えて いる 所の まん中が 画面の まん中）
LAND_DY = FIN_DY - BURY_D                                           # 地面に 着いた 時の 下げ（ハートの 先が 地面の 上の はし）
FIN_Y0 = LAND_DY - HEAP['TOP'] - DROP['FROM']                       # 落ちはじめの 下げ（ハートの 先が 画面の 上の 外）
FIN_T0 = PM_T['FIN'] + DROP['AT']                                   # 落ちはじめ（8.15秒。前は 8.45）
LAND_T = FIN_T0 + DROP['T']                                         # ハートの 先が 地面に 着く（8.55秒。前は 8.91）
LAND_TIP = FIN_TIP + FIN_DY                                         # うまった ハートの 先（画面の y）
HIT_C = (FIN_C[0], HEAP['TOP'] + 4.0)                               # 刺さる 点（地面を おす 所）
FIN_POLY = heart_poly(FIN_C[0], FIN_C[1] + FIN_DY, FIN_S)          # うまった 大きな ハートの 形（うしろの ハートが 見えるか）
HW_S = half_width(heart_poly(FIN_C[0], FIN_C[1] + FIN_DY, FIN_S, n=48), FIN_C[0], HEAP['TOP'])   # 地面の 上の はしでの ハートの はばの 半分
JELLY = dict(D=1.3,                                  # 刺さってから ぷるんぷるんが おさまるまで（秒）
             N=120,                                  # キーフレームの 数（落ちる 間も ふくめて：上へ 動き おわるまで）
             ORG=430.0,                              # のびちぢみの 中心（絵の y：字の 少し 下＝字は ほとんど 動かない・上が つぶれる）
             X0=.08, V0=-1.85, F=1.5, Z=.15,         # たての のびちぢみ：落ちる 間に 8% のびて → 刺さって ぐにゃっと つぶれて ぷるんぷるん（ばね：1秒に 1.5回・へり方 .15：
                                                     #  いちばん つぶれて 15%・のびて 9%・つぶれて 6%・のびて 3.5%。まさちゃん「落ちてきた時、ハートのど的中をもっとプルンプルン揺らして！」。
                                                     #  前は 12%・5%・2%＝ゆっくり 大きく・すぐ 小さく）
             PX=-.6,                                 # よこは たての のびちぢみの −0.6乗（つぶれると 横に ひろがる）
             ROT=-1.6, ROT_F=1.1, ROT_TAU=.35,       # 落ちる 間の かたむき（度）→ 刺さって もどりながら 左右に ゆれる
             SKEW=6.0, SKEW_F=1.16, SKEW_TAU=.55,    # 上が 左右に ずれる（ゼリーの ずれ：度。刺さって 大きく ぷるんと 左右に ゆれて ボードまでの ゆれに つながる。前は 2度）
             TILT=3.0,                               # つぶれる 時に 上が 手前へ（rotateX：度／つぶれ 0.2）
             IDLE=(1.3, .014),                       # おさまった あとの ゆっくりの ぷるん（1回の 秒・のびちぢみ）
             WORD=(70.0, 2.2, .25, .62),             # 星空と 字の おくれ（刺さった 瞬間に 下へ 動きつづける 速さ px/秒・ゆれ 1秒の 回数・へり方）・
                                                     #  体の のびちぢみと 左右の ずれを 0.62 だけ もどす（ゼリーの 中に うかぶ：大きく 動くと 点めつ）
             GLOSS=(-.35, 14.0),                     # つやは 体の のびちぢみを その 乗だけ もどす（すべって 見える）・つぶれると 上へ（px／つぶれ）
             SMALL=(26.0, 2400.0, .05),              # 小さな ハート：はねる 高さ（px）・おちる 速さ（px/秒²）・はねる 時（刺さってから 秒）
             SUS=(.03, 5.0, .8, 1.15))               # ボードまで 大きく ゆれつづける（まさちゃん「結果ボードでるところまで大きく揺れ続けて！」）：
                                                     #  左右に ぷるんぷるん（上の ずれ ±5度：地面に 刺さった 所が 中心＝上は ±18px）・のびちぢみ ±3%
                                                     #  （PURIN の PD ごと）・刺さってから 0.8〜1.15秒で 大きく なる（刺さった 時の ぷるんぷるんが 小さく なってから）・
                                                     #  PC_RES から 0.45秒で おさまる（上へ 動く 間：白い 光で つつまれて いる）。
                                                     #  上下の のびちぢみを 大きく すると ふちの 線が 同じ 所を 何回も 行き来して 点めつ（±6.5% で 11.9%）・
                                                     #  左右も ±7度（上 ±25px）では 10.7%
                                                     #  左右の ずれは 上の ふちが 横に すべる だけ（字も 地面の 近くで あまり 動かない）
FIN_D = PC_RES + .5 - (PM_T['FIN'] + DROP['AT'])                     # 落ちはじめから 上へ 動き おわるまで（2.30秒：.pmfj の pmFJ）
DROP_D = DROP['T'] + BURY['D']                                       # 落ちはじめから うまり おわるまで（1.35秒：.pmf の pmDrop）
RISE_T = LAND_T + .7                                                 # 細かい ハートが 下から のぼりはじめる（刺さった ゆれが 小さく なってから：点めつ しない）
FIN_ORG = dict(word=(191.0, FIN_C[1] - 6), gloss=FIN_C,              # 部品の 動きの 中心（字の まん中・ハートの まん中・小さな ハートの 下）
               small=(FIN_C[0] + FIN_S * .73, FIN_C[1] - FIN_S * .55 + 23 * FIN_S / 165 * .92))
HIT = dict(V=1000.0,                     # ゆれが 地面の ハートを つたわる 速さ（px/秒）
           IN=14.0,                      # 刺さった ハートの ふち（地面の 上の はしで）より この px 内がわの ハートは 前へ おされて のこる（うまった 先を かくす）
           EDGE=95.0, P_POP=.3, P_SPILL=.85,   # ふちの まわり（外へ この px まで）の 上の ハートは 弾ける・のこりの 8わりは とびだして こぼれ落ちる・ほかは ずれる
           SHIFT=300.0, MOVE=14.0,       # この きょりより 近い ハートは 外へ ずれる（いちばん 近くで 14px）
           PUSH=7.0,                     # 前へ おされる ハート：外へ・下へ ずれて 少し 大きく（手前へ）
           G=2600.0)                     # こぼれ落ちる 速さ（px/秒²）
# まさちゃん「このシーンもっと、全体的にぷるんぷるんにして！結果ボードでるところまで大きく揺れ続けて！」：刺さってから ボードが 出る ころまで
#  大きな ハート（JELLY の SUS）・地面の ハート（pmPB）・まわりの ハートの 壁（pmBW）が いっしょに 大きく ぷるんぷるん
#  （1秒に 1.16回：ゆっくり 大きく＝点めつ しない。刺さった ゆれが とどいた 所から）
PURIN = dict(PD=.86,             # 1回の ぷるん（秒）
             N=2,                # 地面と 壁の ハートの 回数
             G=(.05, 4.0, 8.0),  # 地面の ハート：のびちぢみ・はねる 高さ（px）・左右に ゆれる（上の はしが ±8px：下が 中心。大きな 手前の ハートほど 角度は 小さく）
             W=(.04, 3.0, 6.0),  # まわりの ハートの 壁（もやの 奥）：のびちぢみ・はねる 高さ（px）・左右に ゆれる（度）
             GT=.4,              # 地面の ハートが ぷるんぷるん しはじめる（ゆれが とどいてから 秒：おされる・ずれる の あと）
             WT=.45)             # 壁が ぷるんぷるん しはじめる（刺さってから 秒：ずれ おわってから）
# 刺さる 所の まわりの 地面の 上の ハート（さいごに つもる）：(まん中から よこ, 地面の 上の はしから たて, はばの 半分, どうなるか)
MOUND = ((0.0, 26.0, 40.0, 'cush'),      # 先の 前：ぐにゅっと つぶれて ぷるん（のこる：うまった 先を かくす）
         (-74.0, -2.0, 21.0, 'pop'),     # 先の 左の 小さな ハート：ハートの ふちが 来ると 弾ける
         (77.0, -4.0, 20.0, 'pop'),      # 先の 右の 小さな ハート
         (-130.0, 3.0, 32.0, 'spill'),   # ハートの 左の ふち：とびだして こぼれ落ちる
         (133.0, 1.0, 31.0, 'spill'),    # ハートの 右の ふち
         (-178.0, 0.0, 22.0, 'pop'),     # もっと 左：弾ける
         (176.0, -2.0, 23.0, 'pop'))     # もっと 右


def bury_depth(u):
    """地面に 着いてから u 秒の うまった 深さ（px：ズボッ → ずぶずぶ）"""
    if u <= 0:
        return 0.0
    a, (t1, t2) = BURY['A'], BURY['TAU']
    return BURY_D * (1 - a * math.exp(-u / t1) - (1 - a) * math.exp(-u / t2))


def drop_kf():
    """.pmf の pmDrop：画面の 上の 外から だんだん 速く 落ちて（2次の ベジェ）→ 地面に 着いて ズボッと 刺さって ずぶずぶ うまる（ハートの 1/3）"""
    L, D, N = DROP['T'], BURY['D'], BURY['N']
    out = f'0%{{transform:translateY({FIN_Y0:.1f}px);animation-timing-function:cubic-bezier(.333,0,.667,.333)}}'
    for i in range(N + 1):
        u = D * (i / N) ** 2
        y = FIN_DY if i == N else LAND_DY + bury_depth(u)
        out += f'{(L + u) / DROP_D * 100:.3f}%{{transform:translateY({y:.2f}px);animation-timing-function:linear}}'
    return f'@keyframes pmDrop{{{out}}}\n'


def fin_pose(t):
    """落ちはじめ（FIN_T0）から t 秒の ゼリーの ハートの 形（中心は JELLY の ORG）→ (下げ px, かたむき, 手前へ, 上の ずれ（度）, よこ, たて)
       （落ちて うまる 下げは .pmf の pmDrop：ここは のびちぢみと ゆれ だけ）"""
    J = JELLY
    L = DROP['T']
    if t < L:
        sy = 1 + J['X0'] * (t / L) ** 2
        return 0.0, J['ROT'], 0.0, 0.0, sy ** J['PX'], sy
    u = t - L
    x = spring(J['X0'], J['V0'], J['F'], J['Z'], u)
    a, sk, r0, r1 = J['SUS']
    env = smooth01((u - r0) / (r1 - r0)) * (1 - smooth01((FIN_T0 + t - PC_RES) / .45))   # ボードまで 大きく ゆれつづける
    ph = 2 * math.pi * (u - r0) / PURIN['PD']
    x += a * env * math.sin(ph)
    sy = 1 + x
    rot = J['ROT'] * math.exp(-u / J['ROT_TAU']) * math.cos(2 * math.pi * J['ROT_F'] * u)
    skew = J['SKEW'] * math.exp(-u / J['SKEW_TAU']) * math.sin(2 * math.pi * J['SKEW_F'] * u) + sk * env * math.cos(ph)
    return 0.0, rot, -J['TILT'] * x / .2, skew, sy ** J['PX'], sy


def fin_times():
    """キーフレームの 時刻（落ちはじめから：刺さる 前後を 入れる）"""
    N = JELLY['N']
    ts = sorted(set([round(FIN_D * k / N, 4) for k in range(N + 1)] + [round(DROP['T'] - .002, 4), DROP['T']]))   # 0.02秒ごと くらい
    return ts


def kf(name, fn):
    """fn(t) → transform（落ちはじめから 0〜FIN_D 秒）の @keyframes。さいごは きっちり 止まった 形（つぎの アニメに つなぐ）"""
    out = ''
    for t in fin_times():
        out += f'{t / FIN_D * 100:.3f}%{{{fn(t)}}}'
    return f'@keyframes {name}{{{out}}}\n'


GROUND_Y = HEAP['TOP'] - FIN_DY                                    # 地面の 上の はし（絵の y：左右の ずれの 中心）


def fin_jelly_tf(t):
    ty, rot, tilt, skew, sx, sy = fin_pose(t)
    if t >= FIN_D - 1e-6:
        return 'transform:none'
    tx = -math.tan(math.radians(skew)) * (GROUND_Y - JELLY['ORG']) * sy  # 左右の ずれは 地面に 刺さった 所が 中心（上が ゆれる）
    return (f'transform:translateX({tx:.2f}px) rotate({rot:.2f}deg) perspective(800px) rotateX({tilt:.2f}deg) '
            f'skewX({skew:.2f}deg) scale({sx:.4f},{sy:.4f})')


def fin_word_tf(t):
    """字：体の のびちぢみを FLOAT だけ もどして（字の まん中の 下がりも もどす）、刺さった 瞬間から おくれて ゆれる"""
    u = t - DROP['T']
    if u <= 0 or t >= FIN_D - 1e-6:
        return 'transform:none'
    v, f, z, fl = JELLY['WORD']
    ty, rot, tilt, skew, sx, sy = fin_pose(t)
    h = JELLY['ORG'] - FIN_ORG['word'][1]                             # 字の まん中の のびちぢみの 中心からの 高さ
    y = spring(0.0, v, f, z, u) - fl * (1 - sy) * h
    x = fl * math.tan(math.radians(skew)) * (GROUND_Y - FIN_ORG['word'][1]) * sy   # 左右の ずれも FLOAT だけ もどす（ゼリーの 中に うかぶ）
    return f'transform:translate({x:.2f}px,{y:.2f}px) skewX({-fl * skew:.2f}deg) scale({sx ** -fl:.4f},{sy ** -fl:.4f})'


def fin_gloss_tf(t):
    if t >= FIN_D - 1e-6:
        return 'transform:none'
    ty, rot, tilt, skew, sx, sy = fin_pose(t)
    k, up = JELLY['GLOSS']
    return f'transform:translateY({-(1 - sy) * up:.2f}px) scale({sx ** k:.4f},{sy ** k:.4f})'


def fin_small_tf(t):
    u = t - DROP['T']
    if u <= 0 or t >= FIN_D - 1e-6:
        return 'transform:none'
    H, g, t0 = JELLY['SMALL']
    v = math.sqrt(2 * g * H)
    th = 2 * v / g                                                    # はねて いる 時間
    a = u - t0
    ty = -(v * a - g * a * a / 2) if 0 < a < th else 0.0
    rot = 16 * math.sin(math.pi * a / th) if 0 < a < th else 0.0
    sy = 1 + spring(0.0, -4.5, 3.2, .25, u) + (spring(0.0, -3.4, 3.2, .25, a - th) if a > th else 0.0)
    return f'transform:translateY({ty:.2f}px) rotate({rot:.2f}deg) scale({sy ** -.6:.4f},{sy:.4f})'


def fin_shadow_kf():
    """地面に 落ちる 丸い かげ（.pmfc）：落ちる 間は 近づくほど こく 大きく → 刺さると ハートの まわりに のこる（うすく・つぶれると 横に ひろがる）"""
    out = ''
    L = DROP['T']
    H0 = HEAP['TOP'] + DROP['FROM']
    for t in fin_times():
        if t < L:
            q = (t / L) ** 2
            k = q                                                     # 1 − 高さ／はじめの 高さ
            out += f'{t / FIN_D * 100:.3f}%{{opacity:{k ** 1.6:.3f};transform:scale({.35 + .65 * k:.3f})}}'
        elif t >= FIN_D - 1e-6:
            out += f'{t / FIN_D * 100:.3f}%{{opacity:.62;transform:none}}'
        else:
            sy = fin_pose(t)[5]
            o = .62 + .38 * math.exp(-(t - L) / .25)
            out += f'{t / FIN_D * 100:.3f}%{{opacity:{o:.3f};transform:scale({1 + (1 - sy) * 1.4:.4f},{1 - (1 - sy) * .3:.4f})}}'
    return f'@keyframes pmFC{{{out}}}\n'


class FinPlan:
    """刺さって こぼれる ハート（front：地面の 前の 板）と 弾けた かけら（bits）を あつめる"""

    def __init__(self):
        self.front, self.bits = [], []
        self.n = dict(pop=0, spill=0, shift=0, push=0)


def spill_html(x, y, s, k, r, t, vx, h, plan_list, rnd):
    """とびだして こぼれ落ちる ハート（よこは 同じ 速さ・たては 上へ はねて 画面の 下の 外まで 落ちる：上がる 間と 落ちる 間の 2つの 動き）"""
    g = HIT['G']
    tp = math.sqrt(2 * h / g)
    tf = math.sqrt(2 * (h + 900 - (y - s)) / g)
    T = tp + tf
    s1 = rnd.uniform(40, 120) * (1 if vx > 0 else -1)
    s2 = s1 * (1 + tf / tp) * rnd.uniform(.8, 1.1)
    plan_list.append(f'<i style="left:{x - s * 1.12:.1f}px;top:{y - s * 1.08:.1f}px;width:{s * 2.24:.1f}px;height:{s * 2.24:.1f}px;'
                     f'--vx:{vx * T:.0f}px;animation:pmSX {T:.3f}s linear {t:.3f}s both{hide(t, t + T)}">'
                     f'<b class="pm{k}" style="--r:{r:.0f}deg;--up:{-h:.0f}px;--dn:{-h + g * tf * tf / 2:.0f}px;--s1:{s1:.0f}deg;--s2:{s2:.0f}deg;'
                     f'animation:pmSU {tp:.3f}s cubic-bezier(.333,.667,.667,1) {t:.3f}s both,pmSD {tf:.3f}s cubic-bezier(.333,0,.667,.333) {t + tp:.3f}s forwards"></b></i>')


def bits_html(x, y, s, t, n, rnd, plan_list):
    """弾けた ハートの かけら（小さな ハートが よこと 少し 上へ とんで 落ちる）"""
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * (2.4 / max(1, n - 1)) + rnd.uniform(-.2, .2)
        sp = rnd.uniform(.9, 1.4) * s * 2.0
        z = rnd.uniform(12, 20)
        plan_list.append(f'<i class="pm{rnd.choice((0, 1, 2, 4, 5))}" style="left:{x - z / 2:.0f}px;top:{y - z / 2:.0f}px;width:{z:.0f}px;height:{z:.0f}px;'
                         f'--dx:{math.cos(a) * sp:.0f}px;--dy:{math.sin(a) * sp + 30:.0f}px;--d:{sec(t)};--r:{rnd.uniform(-90, 90):.0f}deg;'
                         f'animation:pmPop .6s linear {t:.3f}s both{hide(t, t + .6)}"></i>')


def hit_time(x, y):
    """刺さった ハートの ゆれが この 点に とどく 時（ハートが うまって いく 間に ふちが 外へ ひろがる：まん中から つたわる）"""
    return LAND_T + math.hypot(x - HIT_C[0], (y - HIT_C[1]) * 1.5) / HIT['V']


def hit_react(x, y, s, k, r, rnd, kind, plan, surf=False):
    """最後の ゼリーの ハートが 刺さって この ハート（まん中 x, y・はばの 半分 s・色 k・かたむき r 度）が どうなるか
       （kind：'heap' 地面の ハート（surf：地面の 上の はしの ハート）・'bloom' まわりの ハート（ずれる だけ））→ (足す アニメ（, から）, 足す 変数（;まで）)。
       前へ おされる（刺さった ハートの 前：のこって うまった 先を かくす）・弾ける（ふちの まわりの 上の ハート）・とびだして こぼれ落ちる
       （plan.front に もう1つの ハートを 入れて、この ハートは 消す）・外へ ずれて とまる（もっと まわり）・何も しない（遠い・大きな ハートの うしろで 見えない）"""
    if plan is None:
        return '', ''
    d = math.hypot(x - HIT_C[0], (y - HIT_C[1]) * 1.5)
    if d >= HIT['SHIFT'] or (kind == 'bloom' and inside(FIN_POLY, x, y)):
        return '', ''
    t = hit_time(x, y)
    sg = 1 if x >= HIT_C[0] else -1
    e = abs(x - HIT_C[0]) - HW_S                                      # ハートの ふち（地面の 上の はし）から 外へ
    if kind == 'heap' and e < -HIT['IN'] and y - s * 1.08 < LAND_TIP:
        plan.n['push'] += 1
        m = HIT['PUSH'] * (1 - .5 * min(1.0, max(0.0, y - HEAP['TOP']) / (BURY_D + 60)))
        return (f',pmPu .9s linear {t:.3f}s forwards',
                f'--px:{sg * m * (abs(x - HIT_C[0]) / HW_S) ** .5:.1f}px;--py:{m * .7:.1f}px;')
    if kind == 'heap' and surf and e < HIT['EDGE']:
        roll = rnd.random()
        q = 1 - max(0.0, e) / HIT['EDGE']
        if roll < HIT['P_POP']:
            plan.n['pop'] += 1
            bits_html(x, y - s * .3, s, t, 3, rnd, plan.bits)
            return f',pmHP .2s ease-out {t:.3f}s forwards,pmH .001s linear {t + .2:.3f}s forwards', ''
        if roll < HIT['P_POP'] + (1 - HIT['P_POP']) * HIT['P_SPILL']:
            plan.n['spill'] += 1
            spill_html(x, y, s, k, r, t, sg * rnd.uniform(110, 160) * (1 + .8 * q), rnd.uniform(30, 50) + 50 * q, plan.front, rnd)
            return f',pmH .001s linear {t:.3f}s forwards', ''
    plan.n['shift'] += 1
    q = (1 - d / HIT['SHIFT']) ** 1.2
    m = (HIT['MOVE'] if kind == 'heap' else HIT['MOVE'] * .6) * q + 2
    L = math.hypot(x - HIT_C[0], y - HIT_C[1]) or 1
    hx = (x - HIT_C[0]) / L * m * 1.1
    hy = (y - HIT_C[1]) / L * m * .45 + m * .3
    return (f',pmSh .5s cubic-bezier(.2,.7,.3,1) {t:.3f}s forwards',
            f'--hx:{hx:.1f}px;--hy:{hy:.1f}px;--hr:{sg * m * .7 * rnd.uniform(.6, 1.2):.1f}deg;')


def purin_kf():
    """刺さった あとの まわりの ハートの なめらかな 動き（まさちゃん「落ちてきたあとの他のハートの揺れ方も滑らかにして！」）：
       ばねの 動きを 細かく 取った キーフレーム（linear：とちゅうで 止まらない・はじめと おわりは 前の 形と つながる）。
       pmPu（前へ おされて ぷるん）・pmCu（クッション）・pmPB（地面の ハート：b・ハートの 下が 中心で 左右に ゆれて、はしで つぶれて まん中で のびる）・
       pmBW（まわりの ハートの 壁：ずれた 所の まま）。PB・BW は PURIN の PD ごとに N 回（1つの アニメ・はじめと おわりは ゆっくり）"""
    def env(q, a=.12, b=.28):
        return smooth01(q / a) * (1 - smooth01((q - (1 - b)) / b))
    out = ''
    N, D = 36, .9                                                     # 前へ おされる（0.9秒）：少し 行きすぎて もどる・ぐにゅっと つぶれて ぷるん・手前へ 3% 大きく
    st = ''
    for i in range(N + 1):
        u = D * i / N
        d = 1.0 if i == N else 1 + spring(-1.0, 6.0, 2.0, .5, u)
        sq = 0.0 if i == N else .15 * math.sin(2 * math.pi * 2.2 * u) * math.exp(-u / .3)
        sc = 1 + .03 * min(1.0, max(0.0, d))
        st += f'{i * 100 / N:.2f}%{{transform:translate(calc(var(--px) * {d:.4f}),calc(var(--py) * {d:.4f})) scale({sc * (1 + sq * .8):.4f},{sc * (1 - sq):.4f})}}'
    out += f'@keyframes pmPu{{{st}}}\n'
    st = ''                                                           # クッション（0.9秒）：ぐにゅっと つぶれて ぷるんぷるん
    for i in range(N + 1):
        u = D * i / N
        sq = 0.0 if i == N else .17 * math.sin(2 * math.pi * 1.8 * u) * math.exp(-u / .32)
        st += f'{i * 100 / N:.2f}%{{transform:scale({1 + sq * .9:.4f},{1 - sq:.4f})}}'
    out += f'@keyframes pmCu{{{st}}}\n'
    n = PURIN['N']
    ga, gh, gw = PURIN['G']
    wa, wh, ww = PURIN['W']
    pb = bw = ''
    M = 24 * n                                                        # 1回に 24こ（0.036秒ごと）
    for i in range(M + 1):
        q = i / M
        e = env(q)
        th = -math.sin(2 * math.pi * n * q) * e                       # 左右に ゆれる（−1〜1）
        c = math.cos(2 * math.pi * 2 * n * q) * e                     # はしで つぶれて（−）まん中で のびる（＋）
        sy, wy = 1 + ga * c, 1 + wa * c
        hop, whop = -gh * max(0.0, c), -wh * max(0.0, c)
        pb += (f'{q * 100:.2f}%{{transform:rotate(var(--r)) translateY(38%) rotate(calc(var(--pw,6deg) * {th:.4f})) translateY({hop:.2f}px) '
               f'scale({sy ** -.6:.4f},{sy:.4f}) translateY(-38%)}}')
        bw += (f'{q * 100:.2f}%{{transform:translate(var(--hx,0px),calc(var(--hy,0px) + {whop:.2f}px)) rotate(calc(var(--hr,0deg) + {th * ww:.3f}deg)) '
               f'scale({wy ** -.6:.4f},{wy:.4f})}}')
    return out + f'@keyframes pmPB{{{pb}}}\n@keyframes pmBW{{{bw}}}\n'


def heap_surface(x):
    """地面の 上の はし（画面の y）：ゆるい 波（まん中が TOP）"""
    a, L, ph = HEAP['WAVE']
    return HEAP['TOP'] + a * (math.sin(2 * math.pi * (x - 195.0) / L + ph) - math.sin(ph))


def heap_heart(x, y, s, k, r, t_land, d_drop, rnd, more='', var='', pl=None):
    """地面の ハート 1つ：少し 上から すき通った 光の ハートで 落ちて（はじめの ハートの 雨と 同じ：点めつ しない）、つもった 時に つやつやの ゼリーの ハートに なって
       ぐにゅっと ぷるん → ずっと ゆっくり ぷるぷる（外の i：刺さった 時の 反応・中の b：落ちる・b::before：光の ハート・b::after：ゼリーの ハート）"""
    td = math.sqrt(2 * d_drop / 2400.0)
    t0 = t_land - td
    if pl is not None:                                                # ボードまで 大きく ぷるんぷるん（pmPB）：はじめ・左右の 角度（上の はしが 同じ くらい 動く）
        var += f'--pl:{pl + PURIN["GT"]:.3f}s;--pw:{math.degrees(math.atan(PURIN["G"][2] / (1.9 * s))):.1f}deg;'
    return (f'<i class="pm{k}" style="left:{x - s * 1.12:.1f}px;top:{y - s * 1.08:.1f}px;width:{s * 2.24:.1f}px;height:{s * 2.24:.1f}px;--r:{r:.0f}deg;--hd:{-d_drop:.0f}px;'
            f'--t0:{t0:.3f}s;--td:{td:.3f}s;--l:{t_land:.3f}s;--jd:{rnd.uniform(1.3, 1.8):.2f}s;--jl:-{rnd.uniform(0, 1.8):.2f}s;{var}'
            f'animation:pmH .001s linear {t0:.3f}s backwards{more}"><b></b></i>')


def heap_rows(rnd):
    """地面の ハートの ます（下の 段から 上の 段へ：[(x, y, はばの 半分, 上の はしの ハートか)]）。
       手前（下）ほど 大きく・奥（上）ほど 小さく。さいごの 段は 地面の 上の はし（青い 線）に そって ならべる"""
    W0, W1 = HEAP['W']
    y_bot = 864.0
    rows = []
    y, row = y_bot, 0
    while y > HEAP['TOP'] + 20:
        q = (y - HEAP['TOP']) / (y_bot - HEAP['TOP'])
        w = W0 + (W1 - W0) * q
        x = -w * .3 + (row % 2) * w * HEAP['COL'] * .5 + rnd.uniform(-4, 4)
        cells = []
        while x < 390 + w * .3:
            yy = y + rnd.uniform(-3, 3)
            s = w * rnd.uniform(.94, 1.06) / 2.24
            if yy - s * 1.08 >= heap_surface(x) + 8:
                cells.append((x, yy, s, False))
            x += w * HEAP['COL'] * rnd.uniform(.94, 1.06)
        if cells:
            rows.append(cells)
        y -= w * HEAP['ROW'] * rnd.uniform(.96, 1.04)
        row += 1
    cells = []
    x = -W0 * .2 + rnd.uniform(-4, 4)
    while x < 390 + W0 * .3:
        s = W0 * rnd.uniform(.94, 1.08) / 2.24
        cells.append((x, heap_surface(x) + s * 1.08 + rnd.uniform(-1, 4), s, True))
        x += W0 * HEAP['COL'] * rnd.uniform(.94, 1.06)
    rows.append(cells)
    return rows


def heap_html(plan, seed=97):
    """ハートの 地面（.pmhp：大きな ハートより 前）：画面の 下に 横 いっぱい ハートを すきまなく つむ（下の 段から 上の 段へ じゅんに ポンと 落ちて つもる・
       上の 段ほど うしろ）→ さいごに 刺さる 所の まわりの ハート（MOUND）。刺さると 前の ハートは 前へ おされ、ふちの まわりの 上の ハートは 弾けたり
       とびだして こぼれ落ちたり・まわりは ずれる（hit_react）。地面に 落ちる 丸い かげ（.pmfc）と 白い 輪（.pmgr）も この 板（地面の 上）"""
    rnd = random.Random(seed)
    rh = random.Random(seed + 500)
    T = PM_T
    h0, h1 = T['FIN'] + HEAP['T'][0], T['FIN'] + HEAP['T'][1]
    rows = heap_rows(rnd)
    n_rows = len(rows)
    out = []
    for ri, cells in enumerate(rows):                                # 下の 段から 上の 段へ じゅんに つもる
        for x, yy, s, surf in cells:
            k = rnd.randrange(len(PILE_COLS))
            r = rnd.uniform(-26, 26)
            t_land = h0 + .1 + (h1 - h0 - .14) * ri / max(1, n_rows - 1) + rnd.uniform(0, .04)
            more, var = hit_react(x, yy, s, k, r, rh, 'heap', plan, surf)
            pl = None if ',pmH .001s' in more else hit_time(x, yy)         # 刺さった ゆれが とどいたら ボードまで 大きく ぷるんぷるん（弾ける・こぼれる ハートは 消える）
            out.append((yy, heap_heart(x, yy, s, k, r, t_land, rnd.uniform(*HEAP['D']), rnd, more, var, pl)))
    out.sort(key=lambda it: it[0])                                   # 上の 段ほど うしろ（先に 書く）
    o = ''.join(h for _, h in out)
    for dx, dy, s, what in MOUND:                                    # 刺さる 所の まわりの ハート（地面の 上：さいごに つもる）
        x = HIT_C[0] + dx
        yy = heap_surface(x) + dy
        k = rnd.choice((0, 1, 3, 4))
        r = rnd.uniform(-16, 16)
        t = hit_time(x, yy)
        sg = 1 if dx >= 0 else -1
        if what == 'cush':
            more = f',pmCu .9s linear {LAND_T - .01:.3f}s forwards'   # なめらかな ばね（purin_kf）
        elif what == 'spill':
            spill_html(x, yy, s, k, r, t, sg * rnd.uniform(190, 240), rnd.uniform(70, 95), plan.front, rnd)
            more = f',pmH .001s linear {t:.3f}s forwards'
            plan.n['spill'] += 1
        else:
            bits_html(x, yy, s, t, 4, rnd, plan.bits)
            more = f',pmHP .2s ease-out {t:.3f}s forwards,pmH .001s linear {t + .2:.3f}s forwards'
            plan.n['pop'] += 1
        o += heap_heart(x, yy, s, k, r, h1 + rnd.uniform(-.04, 0), rnd.uniform(*HEAP['D']), rnd, more, pl=LAND_T + .2 if what == 'cush' else None)
    o += (f'<i class="pmfc" style="animation:pmFC {FIN_D:.2f}s linear {FIN_T0:.2f}s both,pmFCo .3s linear {sec(PC_RES)} forwards{hide(FIN_T0, PC_RES + .3)}"></i>'
          f'<i class="pmgr" style="animation:pmGR .65s ease-out {LAND_T:.2f}s both{hide(LAND_T, LAND_T + .65)}"></i>')
    return o


def splash_html(seed=89):
    """着地で とびちる 小さな ハート（ハートの 先から 上と 外へ はねて 落ちる）"""
    rnd = random.Random(seed)
    o = ''
    for i in range(6):
        sg = -1 if i % 2 else 1
        z = rnd.uniform(16, 26)
        h = rnd.uniform(40, 110)
        g = HIT['G']
        tp = math.sqrt(2 * h / g)
        tf = math.sqrt(2 * (h + 900 - HIT_C[1]) / g)
        T = tp + tf
        vx = sg * rnd.uniform(120, 320)
        t = LAND_T + rnd.uniform(0, .04)
        s1 = sg * rnd.uniform(60, 160)
        o += (f'<i style="left:{HIT_C[0] + sg * rnd.uniform(15, 50) - z / 2:.0f}px;top:{HIT_C[1] - 8 - z / 2:.0f}px;width:{z:.0f}px;height:{z:.0f}px;'
              f'--vx:{vx * T:.0f}px;animation:pmSX {T:.3f}s linear {t:.3f}s both{hide(t, t + T)}">'
              f'<b class="pm{rnd.choice((0, 1, 2, 3, 4, 5))}" style="--r:0deg;--up:{-h:.0f}px;--dn:{-h + g * tf * tf / 2:.0f}px;--s1:{s1:.0f}deg;--s2:{s1 * 3:.0f}deg;'
              f'animation:pmSU {tp:.3f}s cubic-bezier(.333,.667,.667,1) {t:.3f}s both,pmSD {tf:.3f}s cubic-bezier(.333,0,.667,.333) {t + tp:.3f}s forwards"></b></i>')
    return o


def fin_html():
    """最後の ゼリーの ハート（.pmf：落ちる・上へ 動く ＞ .pmfj：ぷるんぷるん ＞ かげ・星空（.pmfw.pmfn）・体（わく）・字・つや・小さな ハート・白い 光の 形）"""
    up0 = PC_RES - UP_VEIL[0]
    body, small, win = img('pm_fin'), img('pm_fin_s'), img('pm_fin_n')
    vl = (f'<div class="pmv" aria-hidden="true" style="animation:pmVu {sec(UP_VEIL[1])} linear {sec(up0)} both{hide(up0, up0 + UP_VEIL[1])}">'
          f'{win}{body}{small}</div>')
    return (f'<div class="pmf" aria-hidden="true"><div class="pmfj">{img("pm_fin_sh")}<div class="pmfw pmfn">{win}</div>{body}'
            f'<div class="pmfw">{img("pm_fin_w")}</div><div class="pmfg">{img("pm_fin_g")}</div><div class="pmfs">{small}</div>{vl}</div></div>')


def fin_css():
    """最後の ゼリーの ハートと ハートの 山・もやの CSS（第4.80版：fin_html・heap_html）"""
    T = PM_T
    fx, fy = FIN_C
    a = JELLY['IDLE'][1]
    ow, og, osm = FIN_ORG['word'], FIN_ORG['gloss'], FIN_ORG['small']
    z0, z1 = T['FIN'] + HEAP['HAZE'][0], T['FIN'] + HEAP['HAZE'][1]
    return f"""/* 最後（第4.80版）：{sec(T['FIN'])} まわりの ハートの 壁に もや・画面の 下に 横 いっぱいの ハートの 地面 → {FIN_T0:.2f}秒に 画面の 上の 外から ゼリーの ハートが 落ちて
   （だんだん 速く）{LAND_T:.2f}秒に 先が 地面に 着いて ズボッと 刺さって ずぶずぶ うまる（ハートの 1/3・見えて いる 所の まん中が 画面の まん中）→ ぐにゃっと つぶれて
   ぷるんぷるん（星空と 字は おくれて ゆれる・つやは すべる・小さな ハートは ぴょこん）・前の ハートは 前へ おされる・ふちの まわりは 弾ける・こぼれ落ちる・ずれる →
   {sec(PC_RES)} に 上へ 動いて ボード */
.ov.pm .pmhz{{position:absolute;inset:0;z-index:5;pointer-events:none;opacity:0;
  background:radial-gradient(ellipse 70% 40% at 50% 47%,rgba(255,255,255,.36),rgba(255,255,255,0) 70%),
    linear-gradient(to bottom,rgba(255,238,247,.66),rgba(255,234,245,.58) 55%,rgba(255,228,242,.56));
  animation:pmPA {z1 - z0:.2f}s linear {z0:.2f}s both{hide(z0)}}}
.ov.pm .pmhp{{position:absolute;inset:0;z-index:8;pointer-events:none;overflow:hidden}}
.ov.pm .pmhp i{{position:absolute;display:block;transform-origin:50% 86%;background:none!important}}
.ov.pm .pmhp b{{position:absolute;inset:0;display:block;transform:rotate(var(--r));animation:pmHD var(--td) cubic-bezier(.333,0,.667,.333) var(--t0) both,
  pmPB {sec(PURIN['PD'] * PURIN['N'])} linear var(--pl,99s)}}
.ov.pm .pmhp b::before,.ov.pm .pmhp b::after{{content:'';position:absolute;inset:0}}
.ov.pm .pmhp b::before{{background:{fly_uri()} center/contain no-repeat;animation:pmLo .08s linear var(--l) forwards,pmH .001s linear calc(var(--l) + .08s) forwards}}
.ov.pm .pmhp b::after{{opacity:0;transform-origin:50% 88%;animation:pmL .08s linear var(--l) forwards,pmJlyT var(--jd) ease-in-out var(--jl) infinite,pmJ .5s ease-out var(--l) backwards,pmH .001s linear var(--l) backwards}}
{''.join(f'.ov.pm .pmhp .pm{k} b::after{{background:{jelly_bg(k)}}}' for k in range(len(PILE_COLS)))}
@keyframes pmHD{{from{{transform:translateY(var(--hd)) rotate(var(--r))}}to{{transform:rotate(var(--r))}}}}
@keyframes pmJlyT{{0%,100%{{transform:scale(1.04,.96)}}50%{{transform:translateY(-2px) scale(.965,1.035)}}}}
/* 刺さった ゆれが とどいたら ボードまで 大きく ぷるんぷるん（地面の ハート：pmPB・まわりの ハートの 壁：pmBW。ずれた 所の まま） */
{purin_kf()}
.ov.pm .pmf{{position:absolute;left:0;top:0;width:390px;height:844px;z-index:7;pointer-events:none;transform-origin:{fx:.0f}px {fy:.0f}px;
  animation:pmDrop {DROP_D:.2f}s linear {FIN_T0:.2f}s both,pmUp .5s cubic-bezier(.3,.8,.3,1) {sec(PC_RES)} forwards{hide(FIN_T0)}}}
{drop_kf()}@keyframes pmUp{{from{{transform:translateY({FIN_DY:.1f}px)}}to{{transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}}}
.ov.pm .pmfj,.ov.pm .pmfj>div{{position:absolute;left:0;top:0;width:390px;height:844px}}
.ov.pm .pmfj{{transform-origin:{fx:.0f}px {JELLY['ORG']:.0f}px;animation:pmFJ {FIN_D:.2f}s linear {FIN_T0:.2f}s both,pmFI {sec(JELLY['IDLE'][0])} ease-in-out {FIN_T0 + FIN_D:.2f}s infinite}}
.ov.pm .pmfw{{transform-origin:{ow[0]:.0f}px {ow[1]:.0f}px;animation:pmFW {FIN_D:.2f}s linear {FIN_T0:.2f}s both}}
.ov.pm .pmfg{{transform-origin:{og[0]:.0f}px {og[1]:.0f}px;animation:pmFG {FIN_D:.2f}s linear {FIN_T0:.2f}s both}}
.ov.pm .pmfs{{transform-origin:{osm[0]:.0f}px {osm[1]:.0f}px;animation:pmFS {FIN_D:.2f}s linear {FIN_T0:.2f}s both}}
{kf('pmFJ', fin_jelly_tf)}{kf('pmFW', fin_word_tf)}{kf('pmFG', fin_gloss_tf)}{kf('pmFS', fin_small_tf)}@keyframes pmFI{{0%,100%{{transform:none}}
  30%{{transform:scale({(1 - a) ** -.6:.4f},{1 - a:.4f})}}62%{{transform:translateY(-1.5px) scale({(1 + a * .8) ** -.6:.4f},{1 + a * .8:.4f})}}}}
/* 地面に 落ちる 丸い かげ（近づくほど こく 大きく・刺さると ハートの まわりに うすく のこる）・地面の 上の 白い 輪（地面の 板の 上） */
.ov.pm .pmhp .pmfc{{left:{HIT_C[0] - HW_S - 14:.0f}px;top:{HIT_C[1] - 20:.0f}px;width:{2 * HW_S + 28:.0f}px;height:40px;border-radius:50%;transform-origin:50% 50%;
  background:radial-gradient(closest-side,rgba(110,8,56,.5),rgba(110,8,56,.24) 60%,rgba(110,8,56,0))}}
{fin_shadow_kf()}@keyframes pmFCo{{from{{opacity:.62}}to{{opacity:0}}}}
.ov.pm .pmhp .pmgr{{left:{HIT_C[0] - 170:.0f}px;top:{HIT_C[1] - 28:.0f}px;width:340px;height:56px;box-sizing:border-box;border-radius:50%;border:5px solid #FFFFFF;transform-origin:50% 50%;
  box-shadow:0 0 14px rgba(255,120,190,.85),inset 0 0 10px rgba(255,120,190,.6)}}
@keyframes pmGR{{0%{{opacity:0;transform:scale(.2)}}12%{{opacity:.95}}100%{{opacity:0;transform:scale(1.6)}}}}
/* 刺さった ハートの 前の ハートは 前へ おされて ぷるん（外へ・下へ ずれて 少し 大きく：のこって うまった 先を かくす：pmPu は purin_kf） */
/* 地面の ハートが こぼれ落ちる（よこは 同じ 速さ・たては 上へ はねて 落ちる）・弾ける・ずれる・刺さる 所の クッション */
.ov.pm .pmsp{{position:absolute;inset:0;z-index:8;pointer-events:none;overflow:hidden}}
.ov.pm .pmsp i{{position:absolute;display:block}}
.ov.pm .pmsp b{{position:absolute;inset:0;display:block;transform:rotate(var(--r))}}
@keyframes pmSX{{from{{transform:none}}to{{transform:translateX(var(--vx))}}}}
@keyframes pmSU{{from{{transform:rotate(var(--r))}}to{{transform:translateY(var(--up)) rotate(calc(var(--r) + var(--s1)))}}}}
@keyframes pmSD{{from{{transform:translateY(var(--up)) rotate(calc(var(--r) + var(--s1)))}}to{{transform:translateY(var(--dn)) rotate(calc(var(--r) + var(--s2)))}}}}
@keyframes pmHP{{0%{{transform:none;opacity:1}}35%{{transform:scale(1.25,1.12);opacity:1}}100%{{transform:scale(1.5);opacity:0}}}}
@keyframes pmSh{{0%{{transform:none}}100%{{transform:translate(var(--hx),var(--hy)) rotate(var(--hr))}}}}
.ov.pm .pmls{{z-index:8}}
"""


def pc_layers(board_html):
    """押したあと（下から）：虹色の 背景（パチンコの 大当たりのような 光線・ふわふわの ハート）→ つもる ハート → 回る 白い 光線・キラキラ →
       まわりを うめる ハート → ①〜⑤ の ポニーの アップ（カメラ。着いた時に オーラが 出て ハートが とびだす）→ 下に つもった 小さな ハート →
       最後の 大きな ハート（細かい ハートが のぼる）→ ボード → 白い 光。
       board_html：テーマの ボード（gen_fx の board）"""
    T = PM_T
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
    plan = FinPlan()                                                  # 最後の ゼリーの ハートの 着地で こぼれる ハート・弾けた かけら（第4.80版）
    back, front = pile_bottom()
    bloom, spark = bloom_hearts(plan=plan)
    heap = heap_html(plan)
    bx, by = BURST_C
    return f'''<div class="pmbg" aria-hidden="true"><img class="pmi" src="{blob('pm_bg')}" alt="" style="left:0;top:0;width:390px;height:844px">{bob_hearts()}</div>
    <div class="pmp" aria-hidden="true" style="animation:{hide(t1=T['W'][2])[1:]}">{hearts}</div>
    <div class="pml pmlb" style="animation:{hide(T['BURST'], T['W'][3])[1:]}">{pop_hearts(bx, by, T['BURST'], 20, 23, dist=(170, 300), size=(24, 40))}</div>
    <div class="pmpk" aria-hidden="true"><i class="rays"></i><i class="glow"></i><svg class="spk" viewBox="0 0 390 844">{twinkles(26, 5)}</svg></div>
    <div class="pmbh" aria-hidden="true">{bloom}</div>
    <div class="pmpl pmpb" aria-hidden="true">{back}</div>
    <div class="pmbh pmbk" aria-hidden="true">{spark}</div>
    {scr}
    <div class="pmhz" aria-hidden="true"></div>
    <div class="pmpl" aria-hidden="true">{front}</div>
    <div class="pmu" aria-hidden="true">{rising_hearts(28, 9, RISE_T)}</div>
    {fin_html()}
    <div class="pmhp" aria-hidden="true">{heap}</div>
    <div class="pmsp" aria-hidden="true">{''.join(plan.front)}{splash_html()}</div>
    <div class="pml pmls" style="animation:{hide(LAND_T, LAND_T + .7)[1:]}">{''.join(plan.bits)}</div>
    <div class="hb">{board_html}</div>
    <div class="pmw" aria-hidden="true"></div>
    <p class="sr">プレミアムど的中！ハートが いっぱいに つもって はじけ、虹色の 大当たりの 光の 中に、ハートを だいた ポニーが ど・て・き・ちゅ・う と 1文字ずつ 出てきて、さいごに 画面の 下に つもった ハートの 地面に 上から ゼリーの ハートの ど的中が 落ちてきて ズボッと 刺さって うまり ぷるんぷるん（まわりの ハートが 弾けたり こぼれ落ちたり）</p>'''


def pile_css():
    return ''.join(f'.ov.pm .pm{k}{{background:{jelly_bg(k)}}}' for k in range(len(PILE_COLS)))


def pc_css():
    T = PM_T
    w0, w1, w2, w3 = T['W']
    wd = w3 - w0
    fy = FIN_C[1]
    return pile_css() + f'''
/* ---------- プレミアムど的中（かわいいど的中）：premium_cute.py（絵は flat/premium_art.py の WebP） ---------- */
.ov.fz.pm{{--t0:{sec(PC_RES + .45)};--tc:.3s}}
.ov.pm .pmi{{position:absolute;display:block;max-width:none;max-height:none;pointer-events:none;-webkit-user-select:none;user-select:none;-webkit-user-drag:none}}
/* 見えない 間は 描かない（hide()：出る 前・消えた あとの 絵が 層の 画素を 使わない ように。iPhone で 落ちない ため） */
@keyframes pmH{{0%,100%{{visibility:hidden}}}}
/* 虹色の 背景（パチンコの 大当たりのような 光線・まん中の 白い 光・虹の 輪・さくら・キラキラ：pm_bg）の 上で つやつやの ハートが ふわふわ */
.ov.pm .pmbg{{position:absolute;inset:0;overflow:hidden;background:#FF6FC4}}
.ov.pm .pmbg .pmj{{position:absolute;display:block;transform:rotate(var(--r));animation:pmBob 2.8s ease-in-out infinite alternate}}
@keyframes pmBob{{to{{transform:translateY(-6px) rotate(var(--r))}}}}
/* 第4.80版：ずっと ぷりんぷりん（ぐにゅっと つぶれて → ぴょこんと のびて はねて → ぷるん ぷるん → しずまる。ハートの 下が 中心） */
.ov.pm .pmbg .pmj b{{position:absolute;inset:0;display:block;transform-origin:50% 86%;animation:pmPurin 1.3s ease-in-out infinite}}
@keyframes pmPurin{{0%,100%{{transform:none}}10%{{transform:scale(1.13,.86)}}24%{{transform:translateY(-10px) scale(.9,1.12)}}38%{{transform:translateY(-12px) scale(1.05,.96)}}
  52%{{transform:translateY(-2px) scale(.97,1.03)}}63%{{transform:scale(1.08,.92)}}75%{{transform:scale(.97,1.03)}}87%{{transform:scale(1.015,.985)}}}}
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
.ov.pm .pmpk{{position:absolute;inset:0;z-index:3;opacity:0;overflow:hidden;animation:fzOn .01s linear {sec(T['BG'])} forwards{hide(T['BG'], PK_GAP[0])}}}
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
/* 最後の ハートが 上へ 動く 間も 白く つつむ（{sec(PC_RES - UP_VEIL[0])}〜） */
@keyframes pmVu{{0%{{opacity:0}}{UP_VEIL[0] / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}{(UP_VEIL[0] + .5) / UP_VEIL[1] * 100:.1f}%{{opacity:.92}}100%{{opacity:0}}}}
/* はじけた ハートの かけら（とぶ 小さな ハート・白い 輪） */
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
@keyframes pmAu{{0%{{filter:{AURA_P[0]}}}12%{{filter:{AURA_P[1]}}}45%{{filter:{AURA_P[2]}}}100%{{filter:{AURA_P[3]}}}}}
@keyframes pmAw{{0%{{filter:{AURA_W[0]}}}12%{{filter:{AURA_W[1]}}}45%{{filter:{AURA_W[2]}}}100%{{filter:{AURA_W[3]}}}}}
@keyframes pmRip{{0%{{opacity:0;transform:scale(.97)}}10%{{opacity:1}}{RIP_O}100%{{opacity:0;transform:scale({RIP_S})}}}}
{pony_css()}{cam_css()}/* まわりを うめる ハート（ポニーの 方から 少し とんできて とまる・4こに 1こは ふわふわ・⑤で 画面ぜんぶ）・その 上の キラキラ・下に すきまなく つもった ハート（着地で ぷるん・まん中の 近くは 前へ おされる） */
.ov.pm .pmbh{{position:absolute;inset:0;z-index:4;pointer-events:none}}
.ov.pm .pmbh i,.ov.pm .pmpl i{{position:absolute;display:block;opacity:0}}
.ov.pm .pmbh b,.ov.pm .pmpl b{{position:absolute;inset:0;display:block;transform:rotate(var(--r));transform-origin:50% 82%;animation:pmJly 1.6s ease-in-out infinite}}
/* 下に つもった ハートは ゆっくり ぷるぷる（前の まま：ちらつかない ように。山の ハートも 同じ） */
.ov.pm .pmpl b{{animation-name:pmJlyS}}
@keyframes pmJlyS{{0%,100%{{transform:rotate(var(--r)) scale(1.045,.955)}}50%{{transform:rotate(var(--r)) translateY(-2px) scale(.96,1.04)}}}}
@keyframes pmJly{{0%,100%{{transform:rotate(var(--r))}}16%{{transform:rotate(var(--r)) scale(1.055,.95)}}34%{{transform:rotate(var(--r)) translateY(-2px) scale(.965,1.04)}}
  52%{{transform:rotate(var(--r)) scale(1.02,.982)}}70%{{transform:rotate(var(--r)) scale(.995,1.005)}}}}
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
  100%{{transform:none}}}}{fin_css()}
.ov.pm .pmu{{position:absolute;inset:0;z-index:6;pointer-events:none;opacity:0;animation:fzOn .01s linear {RISE_T:.2f}s forwards{hide(RISE_T)}}}
.ov.pm .pmu i{{position:absolute;bottom:-24px;display:block;opacity:0;animation:pmRise var(--t) linear var(--d) infinite}}
@keyframes pmRise{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}25%{{transform:translate(calc(var(--w) * .5),-220px) scale(1.12,.9)}}
  50%{{transform:translate(var(--w),-440px) scale(.92,1.08)}}75%{{transform:translate(calc(var(--w) * .5),-670px) scale(1.06,.95)}}80%{{opacity:.9}}100%{{opacity:0;transform:translate(0,-900px)}}}}
.ov.pm .hb{{z-index:9;animation:pmBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(PC_RES + .12)} both{hide(PC_RES + .12)}}}
@keyframes pmBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 白い 光（ハートが はじける時に 1回だけ） */
.ov.pm .pmw{{position:absolute;inset:0;z-index:40;background:#FFFFFF;opacity:0;pointer-events:none;animation:pmWhite {sec(wd)} linear {sec(w0)} forwards{hide(w0, w3)}}}
@keyframes pmWhite{{0%{{opacity:0}}{(w1 - w0) / wd * 100:.1f}%{{opacity:1}}{(w2 - w0) / wd * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}
/* 視差効果を減らす：つもる ハート・白い 光・ポニー・とぶ ハート・回る 光線を 出さず、背景の 小さな ハートも 止める。虹色の 背景のまま 1秒 → まん中の 光と キラキラ・上の ハートの ど的中・ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.pm .pmp,.ov.pm .pms,.ov.pm .pml,.ov.pm .pmu,.ov.pm .pmw,.ov.pm .pmpk .rays,.ov.pm .pmf .pmv,.ov.pm .pmbh,.ov.pm .pmpl,
  .ov.pm .pmhz,.ov.pm .pmhp,.ov.pm .pmsp{{display:none}}
  .ov.fz.pm{{--t0:1.9s}}
  .ov.pm .pmpk{{animation:fadeIn .6s ease-out 1s both!important}}
  .ov.pm .pmpk .spk path,.ov.pm .pmbg .pmj,.ov.pm .pmbg .pmj b,.ov.pm .pmfj,.ov.pm .pmfj>div{{animation:none!important}}
  .ov.pm .pmf{{animation:fadeIn .6s ease-out 1.1s both!important;transform:translateY({TITLE_Y - fy:.0f}px) scale({TITLE_K})}}
  .ov.pm .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
