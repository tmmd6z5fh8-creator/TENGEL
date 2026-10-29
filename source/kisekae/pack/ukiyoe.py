"""壁紙パック ⑧浮世絵風（まさちゃんの 指定「大波と街道を走る馬（オリジナルの絵で）」→ 第4.93版「波しぶきと 波の 表現を もっと 海っぽく・9秒に 1回 お侍さん 1人か 2人
   （ランダム）に 出会う」→ 第4.94版「四枚目の 波の 浮世絵を 正確に 参考に・5個目の 動画（実際の 波）の 動きを 参考に」→
   第4.95版「波だけ七枚目の画像と形を全く同じにして！」「波の動きが不自然だから滑らかにもっと自然にして！」→
   第4.96版「浮世絵の赤丸の波はもっと動きを出してリアルにして！波飛沫とか波の高さが変わったりとか！リアルな波の映像から波ができてから消えていく動きを
   勉強して、浮世絵に転用して！」→ 第4.97版「🌊自体をもう少し波の先や小波など丸い絵に変えて！」「小波を作成してを何層か入れ替わりで上下させて波を表現して
   波の動きに合わせて少し大きくなったり、小さくなったりして！あとは潮飛沫の演出入れてリアルにして！」「この赤丸の木のところおかしいから自然に直して！」→
   第4.98版「大波の絵をもう少し可愛く…薄くせず小波にのまれるようにきえるようにして！大波が出てくるのは3秒に一回にして！小波の白いところをもっと細くして！
   小波の先を少し尖らせて！白い丸はけして！小波はもう少しそれぞれが動くようにして！」→
   第4.99版「小波の数減らして、もう少し滑らかにして！」「大波の表現がおかしい やっぱり二枚目のような波にして、リアルで立体的に波がでてきて、消えていく表現にして！」→
   第4.100版「波の先端だけ動くの変だから、波が出てきて、徐々に水平になっていくようにして！今だと今ある絵が伸び縮みしてて変だから、ちゃんと形を変えながら
   リアルに出てきたり、水平になっていったりして！大波は出てきてから水平になるまで、もっと早くして！大波の動作も止まったり鈍いとへんだからリアルに！
   赤四角の小波は、大波と同じ絵の質感にして！あと小波の形は3枚目と同じ感じにして！」「三枚目の赤線の小波のように！」）→
   第4.101版「小波この真ん中の第4に書き足した赤線に合わせて作成して！あともっと大波によせた絵にして！」「あと大波は水平に近くにつれて横長になり、走ってる馬を超えて水平になった方が速度的にもリアルかも！」→
   第4.102版「小波の形を全て統一せずに、バラバラにして！」「小波の絵は一枚目の赤丸みたいにして！」「あと小波はもっと波っぽく動いて！」→
   第4.103版「ダメだ小波だけがどうしても納得いかない。絵を大波に似せた小波で作成して」「そしたら大波が崩れはじめて横長になったあたりの大波にして！あと小波は上の白い波と少し青の海が目立つ部分だけが見えるようにして、海が動いているようにして！」→
   第4.104版「小波もう少し大きくして、海が埋まるように数を増やして！」「あと小波と海と地面と地面の間に隙間ができてて不自然だから、隙間が見えないように調整して！」
   「小波は同じ絵だから数を増やして何層かに重ねて自然に見えるようにして！」「あと、大波も今の大きさと一段高さが下がってサイズが小さくなった2層に重ねて、
   お互いに出るタイミングをずらして大波の唐突に絵が浮いてるよいには見えないようにして！」→
   第4.105版「小波達をいい感じに繋げて何層か作成し、海が波で見えなくなってほしい！」「あと、大波は出るタイミングは少しだけずれてほぼ同じタイミングで
   2層が動くようにして！」「むしろ馬の方が早くて小波は、右から左へスライドしているくらいがいい！それをループして！」
   「小波も多少は右に進んでいるように見えるようにして！」→
   第4.106版「小波を各層ごとに絵をつなげて一個の層を一つの絵みたいに小波が個々にならないようにして！あと小波の青の部分画面上に見えるところ増やして！
   あと、大波が沈む瞬間もっと大きく潮飛沫が上がるようにして！大波が水平に消えるまで！」→
   第4.107版「大波は出てくる位置ランダムにして！あと絵が伸びたり縮んだりするのやめて！」「ごめん！大波7秒に1回にして！」→
   第4.108版「この船もランダムで動くようにして！」「ランダムで船は、馬より右側に行くようにして！9秒に1回中心と右側でいききして！船のゆらゆらはそのままで！」）
   大波は 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波と 同じ 形（まさちゃんの 指定・いちばん 高い 時）。
   第4.99版：第4.98版の かわいい 平らな 大波を やめて 第4.97版の 絵（泡の 爪を 少し まるく）に もどし、ぼかしの かげで 立体的に した。
   第4.100版：大波は 波の 一生を 1まいずつ 描いた コマ（make/ukiyoe_great.py の life：24コマ／秒）に して、絵を のばしたり ちぢめたり しない。
     小波は まさちゃんの 赤い 線の 形（make/ukiyoe_foam.py の small_wave）を 大波と 同じ 色と 線で ぬった もの。
   第4.101版：小波は まさちゃんの 書きこみ どおり（上の ふち ぜんぶに 白い 泡の 帯・帯の 下に 大波の 泡の 爪の ような 小さな 指・中の 白い 線・
     その 下は 大波の 体と 同じ 濃い 藍に 藍の すじと 小さな 明るい 点・波の 先の かぎは なし）。大波は くずれて 低く なる 間に 横長に のびて 右へ 走り、
     走る 馬を 追いこして 水平に なる（make/ukiyoe_great.py の のばす ゆがみ D：白い 背中が 長く なり 頭は そのまま 右へ・scaleX では ない）。
   第4.102版：小波の 絵は 大波の 模様 そのもの（赤丸＝大波の 上の 所：白い 背中に 藍の 巻いた 泡の 爪）を 小波の 形に 写した もの
     （make/ukiyoe_foam.py の small_wave：上の ふちに 大波の 背中と 頭の 巻いた 泡の 爪・すそに 大波の 前の 面）＝ 大波の 小さな かけら。
     （第4.103版で やめた）
   第4.103版：小波は 大波の 一生の コマの うち くずれはじめて 横長に なった 所（コマ 28〜39）を そのまま 小さく 使う（同じ シート・絵を 足さない）。
     上の 白い 波と 少しの 青だけ 見せて（その 下は 列の 海の 線で 切る）、1つずつ 海の 線の 下から 上がって 白い 波が 前へ たおれながら 右へ のび、
     また 沈む（うすく しない）。生きて いる 間 ずっと 右へ 進む＝海が 動いて 見える。
   第4.104版：小波を 大きく（前の 1.3倍 ほど）・数を ふやして 4列に 重ねた（おく → 手前：16・13・11・10こ）。海が 小波で うまり、
     いちばん 手前の 列の 下の はしは 石の 土手の うしろ（海と 地面の 間に すき間が 見えない）・ほかの 列の 下の はしは ぼかして 海に とける。
     小波の コマは 同じ 大きさの 箱に ならべた 帯（make/ukiyoe_mini.py → ukiyoe.mini）で、箱の 中の 背景の 場所だけ を ずらす（数が 多くても かるい）。
     大波は 2つ：いまの 大波と、ひとまわり 小さくて 低い 大波（0.7倍・手前に 重ねる・少し 右）。出る 時を 1.5秒 ずらして、いつも どちらかが
     小波の 中から 立ち上がって いる（大波の 絵が とつぜん 浮かんで 見えない）。
   第4.105版：小波を つないで 波の 帯（リボン）4層に した（make/ukiyoe_mini.py → ukiyoe.ribbon：コマを すきまなく 重ねて 白い 背中どうしが
     つながり、波の 頭より 下は 大波の 体と 同じ 藍の 体で うめる・帯は 石の 土手の うしろまで）＝ 海は 波だけで 平らな 海が 見えない。
     帯は 右から 左へ 流れて くり返す（まさちゃん「小波は、馬と同じ速度で右に移動する必要はないよ！むしろ馬の方が早くて小波は、右から左へ
     スライドしているくらいがいい！それをループして！」＝走る 馬の 方が はやい ので 海は うしろへ 流れて 見える。遠い 海ほど ゆっくり・どの 層も
     松並木と 街道より ゆっくり）。おくの 層ほど 小さく かすむ。動く 小波は 帯の 上を 右へ 進む（まさちゃん「小波も多少は右に進んでいるように
     見えるようにして！」：帯の 半分の はやさで 左へ 流れる＝帯に 対して 右へ 進む ので、海は うしろへ 流れても 波は 右へ ころがって 見える）。
     帯の うしろから 頭を 出して 立ち上がり、白い 波が 右へ たおれながら のびて、また 帯の うしろへ 沈む。
     大波 2つは ほぼ 同じ 時に 動く（小さい 大波は 0.28秒 おくれ）。
     動く 小波は 1つ 1つが 1つの 箱（ukNo）：左右と 上下の 動きを 1つの transform に、コマを 背景の 場所に（動く 部品 67・かるく）。（第4.106版で やめた）
   第4.106版：小波の 層 4つを それぞれ 1まいの つながった 絵に した（make/ukiyoe_mini.py → ukiyoe.ribbon・小波が 1つずつに 見えない）。
     1つの 層は 波の 頭（ukRc）と 波の 体（ukRb）の 2本で、どちらも はば 390px で くり返す 絵：
     頭＝大波が くずれはじめて 横長に なった 所（コマ 26〜40）の 頭の 線に そった 帯（墨の 線・うすい 白い 泡・その 下の 大波の 爪と 藍の 顔）を
     切れめ なく つなぎ、ゆるく うねる 頭の 線（頭が 少し とがり 谷は ひろい・前の 右が 少し 急）に そって 巻きもどした もの
     （頭の 所ほど 白い 泡が 少し 厚い・爪の すき間と 帯の 下は 藍）。体＝大波の 体と 同じ 藍の ぼかしに 明るい 青の さざなみ（短い 弧）。
     白い 泡を うすく して 爪の すき間と 体を 藍に したので 青の 見える 所が ふえた（海の 所で 白：青 ＝ 約 1：0.5 → 約 1：1.7）。
     体は 右から 左へ 流れ（遠い 層ほど ゆっくり・どの 層も 松並木より ゆっくり）、頭は 体の 半分の はやさで 左へ 流れる＝体に 対して 右へ ころがる。
     大波が 沈みはじめて から 水平に なって 消える まで、白い 水の 先で 高い 潮しぶき（もやの 柱と 白い つぶ・上は うしろへ 流れる）が
     左から 右へ つぎつぎに ふき上がる（PLUME：落ちる 所が いちばん 大きく、水平に なるに つれて 小さく。白く なるのは どれも 0.3秒 以上 かけて）。
   第4.107版：大波は 7秒に 1回（出て きて から 水平に なる まで 約2秒・止まらずに → 約5秒 しずかに 小波の 層だけ 動く → 次の 波）。
     大波 2つの 出る 場所を 1回ごとに かえる（UK_POS：7回で 1回り＝49秒・左右の とびと 2つの 間を ばらばらに・1回目は 第4.106版と 同じ 場所）。
     場所を かえるのは 2つとも 見えない 間だけ（UK_SW）。左に 出た 大波は くずれて 右へ 走る 間に 少し 長く 走って、どの 場所でも 走る 馬を 追いこす。
     絵を のばしたり ちぢめたり しない：大波の コマは 回して うつす だけ（make/ukiyoe_great.py：のばす ゆがみ D・かたむき・頭を 外へ のばす ε を やめ、
     左の はしの 背中は 海へ 沈める＝右へ ずらしても 切れて 見えない）。小波の 層の ふくらみ（scale）と しぶき・もやの scale も やめた：
     層は 少し 上がる だけ（translateY）、しぶきと もやは 大きさを かえずに うつって うすく なる、潮しぶきは 小波の うしろ（海の 線の 下）から
     ふき上がって うしろへ 流れながら 落ちる（どれも translate と こさ だけ）。
   第4.108版（まさちゃん「この船もランダムで動くようにして！」→「ランダムで船は、馬より右側に行くようにして！9秒に1回中心と右側でいききして！
     船のゆらゆらはそのままで！」）：帆かけ舟は 9秒ごとに まん中と 走る 馬の 右がわを 行き来する（BT_PATH：72秒で 1回り＝8回 行き来・
     行き先と 出る 間と はやさは 1回ごとに ちがう）。舟は すぐ 前の 小波の 層（3つ目）の 波の 頭に のって 上下し、波の かたむきに 合わせて
     かたむく（その 層の 頭の 線＝ ukiyoe.ribbon の edge：make/ukiyoe_mini.py --edge で 絵から はかった もの）。7秒ごとに 層と いっしょに
     少し 上がり、大波が 落ちた あとは 大きく ゆれる。舟の 底は いつも 波の 頭の 線の 下（うかない）・帆は いつも 波の 上（しずまない）・
     舟の 体が 少し 見える（第4.107版は 波に 沈んで 帆だけ だった）。大波の うしろに かくれる。絵は のばさない（うつす・回す だけ）。
   上の絵：和紙の 地・空の 上に 藍の ぼかし・赤い 日・藍の ぼかしの 山なみ・かすみ（横の 雲の 帯）。
     左に 神奈川沖浪裏の 大波（画像から 切りぬいて 浮世絵の 平らな 4つの 色＝白・明るい 青・藍・濃い 藍 に まとめた 絵。
     白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点。空・題箋・落款は すける・舟と 人・富士山は 入れない。
     泡の 爪は 少し まるく・ぼかし（bokashi）で 根もとと 巻きの 下を 濃く・白い 背中の 下を 明るい 青に）。
     海は 小波の 層 4つ（1つの 層が 1まいの つながった 絵：うねる 頭の 線・墨の 線と うすい 白い 泡・大波の 爪と 藍・その 下は 藍の 体に
     明るい 青の さざなみ。おくの 2層＝大波の うしろ・手前の 2層＝大波の 前・おくほど 小さく かすむ）と 潮しぶき。大波は 2つ（いまの 大波と、手前に 小さく 低い 大波）。
     沖に 帆かけ舟（9秒ごとに まん中と 馬の 右がわを 行き来する・波に のって ゆれる）。手前に 海ぞいの 街道（松並木・土の 道・草の 土手）。白い 馬（朱の 布と 手綱・墨の 輪郭：pack/make/ukiyoe_art.py）が 街道を 右へ 走る。右上に 朱の 印（白い 蹄鉄）
   動き（7秒に 1回 大波：出て きて から 水平に なる まで 約2秒・止まらずに。小さい 大波は 0.28秒 おくれて 同じ 一生。出る 場所は 毎回 ちがう）：
     海の 中から うしろへ ねた 波が 出て きて 立ち上がり（頭が 立って 爪が のびる）→ 神奈川沖浪裏（止まらずに すぎる）→ 波の 先が 前へ 投げ出されて 爪が 下へ
     巻きこみ、しぶきの 点が 前へ とび、頭から しぶきと もやが うしろ（左）へ 吹き飛ぶ → 波の 先が 落ちて 白い 水に なり、
     大波は 前へ たおれて 低く なりながら 右へ 走る（沈みはじめ から 水平に なって 消える まで、白い 水の 先で 高い 潮しぶきが
     小波の うしろから 左から 右へ つぎつぎに ふき上がり、うしろへ 流れて 落ちる）→ 走る 馬を 追いこして、
     馬の 右で 水平に なって 手前の 小波の むこうへ 消える（うすく しない）→ しずか → 次の 波。
     小波の 層は 右から 左へ 流れて くり返し（馬の 方が はやい：おくほど ゆっくり・どの 層も 松並木より ゆっくり）、波の 頭は 体より ゆっくり
     左へ 流れる＝体に 対して 右へ ころがる（海は いつも 波で うまって いる）。層 ぜんたいは 大波が 水平に なる 間に 少し 上がる。帆かけ舟は 9秒ごとに まん中と 馬の 右がわを 行き来し（とちゅうは 馬の うしろを とおる・着くと 波に 押されて 少し 左へ ながれる）、
     すぐ 前の 層の 波の 頭に のって 上下に ゆれて かたむく（大波が 落ちた あとは 大きく ゆれる）。かすみが ゆっくり ただよう・街道と 松並木と 土手が 右から 左へ 流れる（馬が 前へ 進んで 見える）。
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
    """沖の 海（水平線 から 街道の むこう まで）：藍の ぼかしに 遠い 小さな 波頭（白い 弧と 明るい 青の すじ）を びっしり
       （第4.105版：小波の 帯の 頭の すきまから 見えても 平らな 海に 見えない）"""
    defs = washi_defs(5) + (f"<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{AI['l']}'/><stop offset='.35' stop-color='{AI['m']}'/>"
                            f"<stop offset='1' stop-color='{AI['d']}'/></linearGradient>")
    o = f"<path d='M0 86 H150 L170 88 L396 92 V130 H0 Z' fill='url(#s)'/>"
    R = rnd(8)
    for i in range(170):                                                    # 遠い 波頭（手前ほど 大きい）
        y = 86.6 + R.uniform(0, 1) ** 1.3 * 26
        x = R.uniform(-10, 396)
        if y < 86.6 + (6 if x > 170 else (2 * (x - 150) / 20 if x > 150 else 0)):
            continue
        w = R.uniform(4, 9) * (0.6 + (y - 86) / 18)
        sw = .45 + (y - 86) / 40
        o += (f"<path d='M{f(x)} {f(y)} q{f(w * .45)} {f(-w * .3)} {f(w)} {f(-w * .05)} q{f(-w * .12)} {f(w * .02)} {f(-w * .18)} {f(w * .14)}' fill='none' "
              f"stroke='#F4EEDF' stroke-width='{f(sw)}' stroke-linecap='round' opacity='.9'/>"
              f"<path d='M{f(x - w * .3)} {f(y + 1.2 + w * .08)} q{f(w * .6)} {f(-w * .16)} {f(w * 1.2)} 0' fill='none' stroke='{AI['p']}' stroke-width='{f(sw * .8)}' "
              f"stroke-linecap='round' opacity='.6'/>")
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


# ---------------------------------------------------------------- 大波（第4.95版 → 第4.100版：まさちゃん「波の先端だけ動くの変だから、波が出てきて、徐々に水平になっていくようにして！
#   今だと今ある絵が伸び縮みしてて変だから、ちゃんと形を変えながらリアルに出てきたり、水平になっていったりして！」「大波は出てきてから水平になるまで、もっと早くして！」
#   「大波の動作も止まったり鈍いとへんだからリアルに！」）
# 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波を 画像から 切りぬいて 浮世絵の 平らな 4つの 色（白・明るい 青・藍・濃い 藍）に まとめた 絵
# （make/ukiyoe_great.py：空・題箋・落款は すける・舟と 人・富士山は 入れない・泡の 爪を 少し まるく（第4.97版）・ぼかしで 立体の かげ（第4.99版））。
# 第4.100版：波の 一生を 1まいずつ 描いた コマ（life：24コマ／秒・1.9秒）に した。絵を のばしたり ちぢめたり（scale）しない：
#   ① 海の 中から うしろへ ねた 波が 出て きて 立ち上がる（うつす・回す・高い 所ほど かたむける・頭の 巻き c −1→0＝頭が 立って 爪が のびる）
#   ② 神奈川沖浪裏（止まらずに すぎる）③ 波の 先を 投げ出して 前へ のりだす（c 0→1・爪の 下の しぶきの 点が 前へ とんで 落ちる）
#   ④ 落ちる（c→1.6・落ちた 所で 潮しぶき）⑤ 左の 根もとを 軸に 前へ たおれて だんだん 低く なり、水平に なって 手前の 小波の むこうへ 消える（うすく しない）
#   ⑥ 次の 波まで しずか（第4.107版：7秒に 1回）。コマは 中身の ある 四角だけ を 1まいの シートに つめて あり、step-end で 入れかえる（すけて 形を 入れかえる こと なし）
WB = (-22, 2)                          # コマの 絵の 左上（上の絵の 中・第4.97版と 同じ 場所）
WAVE_T = 7.0                           # 7秒に 1回 大波（第4.107版 まさちゃん「ごめん！大波7秒に1回にして！」：約2秒の 一生 → 約5秒 しずか）
T_PEAK, T_PITCH, T_LAND, T_FLAT = 0.75, 1.12, 1.30, 2.05   # いちばん 高い・のりだす・落ちる・水平（make/ukiyoe_great.py の LIFE_KEYS と 同じ）
PLUME = [(1.12, 220, .9, 'pl0'), (1.24, 224, 1.05, 'pl1'), (1.36, 232, 1.1, 'pl0'), (1.48, 250, 1.02, 'pl1'),
         (1.60, 276, .95, 'pl0'), (1.72, 300, .86, 'pl1'), (1.84, 318, .76, 'pl0'), (1.96, 330, .66, 'pl1')]
#   第4.107版：大波は のびずに 回って 右へ 走る ので、潮しぶきの 場所を 新しい 白い 水の 先（make/ukiyoe_great.py の life）に 合わせた
#   第4.106版（まさちゃん「大波が沈む瞬間もっと大きく潮飛沫が上がるようにして！大波が水平に消えるまで！」）：大波が 沈みはじめて（1.1秒）から
#   水平に なって 消える（2.05秒）まで、白い 水の 先（大波が 右へ 走る 先）で 高い 潮しぶき（もやの 柱と 白い つぶ）が 左から 右へ
#   つぎつぎに ふき上がる（時・上の絵の x・大きさ・絵）。落ちる 所が いちばん 大きく、水平に なるに つれて 小さく。馬（x 190〜312）の うしろを とおって
#   追いこす（馬と 手前の 小波は 手前）。1つの しぶきは PL_RISE 秒 かけて 高く なり（白く なるのは 0.3秒 以上 かけて）、上は うしろ（左）へ 流れて 落ちる
PL_LIFE, PL_RISE, PL_END = 1.3, .32, 3.4    # 1つの しぶきの 長さ・ふき上がる 長さ・どの しぶきも この 時までに 消える（次の 波の 前）
PL_W, PL_H = 110, 120                       # しぶきの 絵の 大きさ（下の まん中が ふき上がる 所）
CROWN = (1.24, 222, 1.5)                    # 波の 先が 落ちた 所で 横へ ひろがる しぶき（時・x・大きさ：burst_svg）
#   第4.107版（まさちゃん「あと絵が伸びたり縮んだりするのやめて！」）：しぶきの 絵は 1つずつ 決まった 大きさ（sc）で、のばしたり ちぢめたり しない。
#   小波の うしろ（海の 線の 下）から translateY で ふき上がり、上で 少し 止まって うしろ（左）へ 流れながら 落ちて うすく なる

# 第4.107版（まさちゃん「大波は出てくる位置ランダムにして！」）：大波 2つの 出る 場所を 1回ごとに かえる（7回で 1回り＝49秒。くり返しに 見えない
#   ように 左右の とびを ばらばらに）。(大波を 右へ ずらす px, 小さい 大波の 間の ずれ px)。1回目は 第4.106版と 同じ 場所（止まった 絵も これ）。
#   場所を かえるのは 2つとも 見えない 間（1回の UK_SW 秒：大波は 2.05秒・潮しぶきは PL_END 秒までに 消える）だけ。
#   左に 出た 大波は くずれて 右へ 走る 間（T_LAND → UK_RUN 秒）に 少し 長く 走って、どの 場所でも 走る 馬を 追いこす
#   （波の 先が UK_PASS を こえる：ずらし 0 では UK_FRONT まで 行く）
UK_POS = [(0, 0), (50, -20), (-45, 15), (25, 25), (-60, -10), (60, 5), (-25, -25)]
UK_SW, UK_RUN = 5.0, 1.95
UK_PASS, UK_FRONT = 318, 328.5


# ---------------------------------------------------------------- 小波（第4.97版 → … → 第4.105版 → 第4.106版：まさちゃん「小波を各層ごとに絵をつなげて
#   一個の層を一つの絵みたいに小波が個々にならないようにして！」）
# 小波は 大波の 子ども（小さな 大波・第4.103版）：大波の 一生の コマの うち くずれはじめて 横長に なった 所（コマ 28〜39）を そのまま 小さく 使う
#   （たて横 同じ 倍率・左右に うら返さない・絵を 足さない）。上の 白い 波と 少しの 青（頭から 44px まで）を 見せる。
# 第4.105版：小波を つないで 波の 帯（リボン）を 4層 作った（make/ukiyoe_mini.py → ukiyoe.ribbon）。帯の 1本は はば 390px で くり返す 絵：
#   コマを 右から 左へ すきまなく 重ね（左の 波の 巻きが 右の 波の 白い 背中に かぶさる＝白い 背中どうしが つながる）、波の 頭より 下は
#   大波の 体と 同じ 藍の 体（藍 → 濃い 藍の ぼかし・明るい 青の 帯・白い すじ）で うめる＝帯の 下は ぜんぶ 波（平らな 海が 見えない）。
#   帯は 下の はし（石の 土手の うしろ）まで あるので、層を 重ねると 海は 波だけに なる。おくの 層ほど 小さく かすむ（絵に かすみの 色を まぜる）。
#   帯は 右から 左へ 流れる（まさちゃん「むしろ馬の方が早くて小波は、右から左へスライドしているくらいがいい！それをループして！」：
#   2まいぶんの はばの 箱を translateX で 左へ 1まいぶん うごかして くり返す＝つなぎめなし・おくほど ゆっくり・どの 層も 松並木
#   （390px／3.47秒）より ゆっくり＝遠い 海）。
# 第4.106版（まさちゃん「小波を各層ごとに絵をつなげて一個の層を一つの絵みたいに小波が個々にならないようにして！あと小波の青の部分画面上に
#   見えるところ増やして！」）：層 1つ＝1まいの つながった 絵（動く 小波 ukNo は やめた）。層は 波の 頭（ukRc）と 波の 体（ukRb）の 2本
#   （どちらも はば 390px で くり返す：make/ukiyoe_mini.py → ukiyoe.ribbon）：
#   頭＝大波が くずれはじめて 横長に なった 所（コマ 26〜40）の 頭の 線に そって ほどいた 帯（墨の 線・白い 泡・爪と 藍の 顔）を、列ごとに 白い 泡の
#   下の はし（爪の はじまり）を そろえて つなぎ（白い 泡は RB_GW だけ＝うすく）、うねる 頭の 線（A：でこぼこ・n：1まいの 頭の 数・トロコイド RB_R・
#   前が 少し 急 RB_PEAK）に そって 巻きもどす（頭ほど 白い 泡が RB_BETA だけ 厚い）。爪の すき間と 帯の 下は 藍の 下地。
#   体＝藍の ぼかしに 明るい 青の さざなみ（上の はしは 頭の 帯の 下に かくれる・下の はしは 次の 層の 頭の 線の いちばん 下より RB_UNDER 下＝すきまなし。
#   いちばん 手前の 層は 石の 土手の うしろ RB_BOT まで）。s：大波の 絵の 何倍（おくほど 小さい）・haze：かすみ。
#   体は v（px/秒）で 右から 左へ 流れ、頭は v×(1−RB_FWD) で 左へ＝体に 対して 右へ ころがる（まさちゃん「小波も多少は右に進んでいるように見えるようにして！」）。
#   層 ぜんたいは 大波に 合わせて 少し 上がる（rise：上がる px。第4.107版：ふくらむ scale は やめた＝のばさない。
#   いちばん 手前の 層は 上がっても 下の はしが 街道（y 116）の うしろに のこる 2.2px まで）
RB_ROWS = [dict(top=84.6, A=.9, n=17, s=.082, haze=.26, v=10.0, rise=.6, seed=31),
           dict(top=88.3, A=1.25, n=12, s=.102, haze=.12, v=19.5, rise=1.2, seed=32),
           dict(top=92.9, A=2.4, n=9, s=.145, haze=.04, v=32.5, rise=1.8, seed=33),
           dict(top=99.3, A=3.6, n=7, s=.2385, haze=0.0, v=52.0, rise=2.2, seed=34)]
RB_BACK = 2                           # おくの 2層は 大波の うしろ・手前の 2層は 大波の 前
RB_BOT = 118.5                        # いちばん 手前の 層の 体の 下の はし（石の 土手 y 110〜 の うしろ）
RB_PAD = 2.0                          # 層の 箱の 上の よゆう（画面の px：波の 頭の 線より 上）
RB_UNDER = 3.0                        # 体の 下の はし：次の 層の 頭の 線の いちばん 下より 何 px 下
RB_CAP, RB_GW, RB_DC, RB_THR = 6, 30, 18, .45   # 頭の 帯（大波の シートの 画素）：墨の 線・白い 泡・爪と 顔の 厚さ・爪と 見る 濃さ（赤の 0..1）
RB_FADE, RB_BSTART = 8, 2.0           # 頭の 帯の 下の ぼかし（シートの 画素）・藍の 下地の はじまり（頭の 線から：大波の 絵の px）
RB_R, RB_PEAK, RB_BETA = .65, .6, .45  # 頭の 線：トロコイド（頭の とがり）・頭の 場所（0..1：.5 より 小さい＝前が 急）・頭ほど 白い 泡が 厚い わりあい
RB_Z, RB_TILE = 3, 390                # 層の 絵の 細かさ（画面の 1px あたりの 画素）・くり返しの はば
RB_FWD = .5                           # 頭が 体に 対して 右へ ころがる はやさ（体の はやさの 何倍：画面では 体より ゆっくり 左へ）


# 大波の 2つ目（第4.104版：まさちゃん「大波も今の大きさと一段高さが下がってサイズが小さくなった2層に重ねて、お互いに出るタイミングをずらして」）：
#   いまの 大波と 同じ コマ・しぶきを、根もと（海の 線 y 112・大波の 左の はし）を 中心に G2_S 倍に して 少し 右へ（G2_DX）・手前に 重ねる。
#   第4.105版：ほぼ 同じ 時に 動く（0.28秒 だけ おくれ）＝2つの 大波が いっしょに 小波の 中から 立ち上がる
G2_S, G2_DX, G2_LAG = 0.7, 70, 0.28     # 第4.105版：まさちゃん「大波は出るタイミングは少しだけずれてほぼ同じタイミングで2層が動くようにして！」（1.5秒 → 0.28秒）


def plume_svg(seed=61, w=PL_W, h=PL_H, lean=16):
    """大波が 沈む ときに 白い 水の 先で 高く ふき上がる 潮しぶき（第4.106版）：下の まん中から 上へ のびる もやの 柱（下ほど 濃い・右と 下に
       うすい 藍の かげ＝和紙の 空でも 形が 見える）と ふん水の ような 白い つぶ（藍の ふち）。上ほど うしろ（左）へ 流れる"""
    defs = ("<filter id='b1' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='2.6'/></filter>"
            "<filter id='b2' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='5'/></filter>")
    cx, by = w * .55, h - 4
    R = rnd(seed)
    o = ''
    for u, rx, ry, op, bl in ((0.04, 30, 9, .6, 'b1'), (.2, 16, 20, .58, 'b1'), (.42, 18, 19, .46, 'b2'), (.64, 21, 16, .34, 'b2'), (.84, 22, 12, .2, 'b2')):
        x, y = cx - lean * u * u, by - u * (h - 14)
        o += (f"<ellipse cx='{f(x + 2.5)}' cy='{f(y + 2.5)}' rx='{f(rx)}' ry='{f(ry)}' fill='{AI['l']}' opacity='{f(op * .45)}' filter='url(#{bl})'/>"
              f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='{f(rx * .92)}' ry='{f(ry * .92)}' fill='#FFFFFF' opacity='{f(op)}' filter='url(#{bl})'/>")
    for i in range(150):
        th = math.radians(R.uniform(-130, -50))
        d = (h - 12) * R.uniform(.06, 1) ** .75
        x = cx + math.cos(th) * d * .58 - lean * (d / h) ** 2 + R.gauss(0, 2)
        y = by - d * (-math.sin(th)) ** .5
        r = R.uniform(.6, 1.8) * (1.15 - .4 * d / h)
        if 0 < x < w and 0 < y < h:
            o += (f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='#FDFCF7' stroke='#5F82B0' stroke-width='{f(.32 if r > .8 else .24)}' "
                  f"opacity='{f(R.uniform(.8, 1))}'/>")
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


# ---------------------------------------------------------------- 波の 一生（7秒）の 時の ながれ


def _pc(t):
    return t / WAVE_T * 100


def _win(name, keys):
    """[(秒, 宣言)] → @keyframes（はしの 0% と 100% を 足す）"""
    st = [(_pc(t), d) for t, d in keys]
    if st[0][0] > 0:
        st.insert(0, (0, keys[0][1]))
    if st[-1][0] < 100:
        st.append((100, keys[-1][1]))
    return kf(name, st)


def life_css(wave):
    """大波の コマ（make/ukiyoe_great.py の life）：コマ k（t＝k/fps の 形）を k/fps の まわりに 出す（step-end）。
       水平に なった あとは 出さない（こさを 下げて 消す のでは なく、もう 海の 線の 下）"""
    z, fps = wave['z'], wave['fps']
    st = [(0.0, 'opacity:0')]
    for k, (x, y, w, h, ox, oy) in enumerate(wave['cells'], 1):
        t = (k - .5) / fps
        st.append((_pc(t), f'opacity:1;transform:translate({f(ox / z, 2)}px,{f(oy / z, 2)}px);width:{f(w / z, 2)}px;height:{f(h / z, 2)}px;'
                           f'background-position:{f(-x / z, 2)}px {f(-y / z, 2)}px'))
    st.append((_pc((len(wave['cells']) + .5) / fps), 'opacity:0'))
    st.append((100, 'opacity:0'))
    return kf('ukWv', st)


def sea_amp(t):
    """t 秒の 海の ふくらみ（0〜1）：大波が 出て くる 間に ふえ、前へ たおれて 水平に なる 間（大波を のみこむ）が いちばん 大きく、そのあと しずまる"""
    def ss(u):
        u = min(1.0, max(0.0, u))
        return u * u * (3 - 2 * u)
    if t < T_PEAK:
        return .2 + .25 * ss(t / T_PEAK)
    if t < T_LAND:
        return .45 + .25 * ss((t - T_PEAK) / (T_LAND - T_PEAK))
    if t < 1.85:
        return .7 + .3 * ss((t - T_LAND) / (1.85 - T_LAND))
    if t < 2.9:
        return 1.0 - .8 * ss((t - 1.85) / 1.05)
    return .2


def row_stops(k, step=.1):
    """小波の 層 k の 上がり（上がる px だけ：第4.107版 ふくらむ scale は やめた＝のばさない）＝ 0.1秒ごとの 点（2.9秒 から 次の 波までは しずか）"""
    p = RB_ROWS[k]
    out, t = [], 0.0
    while t < 2.9 + 1e-6:
        out.append((_pc(t), f'transform:translateY({f(-p["rise"] * sea_amp(t), 3)}px)'))
        t = round(t + step, 6)
    out.append((100, f'transform:translateY({f(-p["rise"] * sea_amp(WAVE_T), 3)}px)'))
    return out


def wave_life_css():
    """頭から 吹き飛ぶ しぶきと もや・沈みはじめて から 水平に なる まで 白い 水の 先で ふき上がる 高い 潮しぶき・落ちた 所の しぶき・
       小波の 層の ふくらみと 流れ（白く なるのは どれも 0.3秒 以上 かけて）"""
    o0 = 'opacity:0'
    css = ''
    # 頭から うしろ（左）へ 吹き飛ぶ しぶき（点の 帯）と もや：波の 先を 投げ出す とき（第4.107版：大きさは かえない＝うつって うすく なる だけ）
    for nm, t0 in (('ukSp1', .78), ('ukSp2', 1.0)):
        css += _win(nm, [(0, f'{o0};transform:translate(6px,3px)'), (t0, f'{o0};transform:translate(6px,3px)'),
                         (t0 + .3, 'opacity:1;transform:translate(-6px,-2px)'), (t0 + .8, 'opacity:.7;transform:translate(-24px,-7px)'),
                         (t0 + 1.3, f'{o0};transform:translate(-40px,-11px)')])
    for nm, t0 in (('ukMs1', .85), ('ukMs2', 1.08)):
        css += _win(nm, [(0, f'{o0};transform:translate(4px,2px)'), (t0, f'{o0};transform:translate(4px,2px)'),
                         (t0 + .4, 'opacity:.85;transform:translate(-9px,-3px)'), (t0 + 1.25, f'{o0};transform:translate(-46px,-10px)')])
    # 第4.106版：大波が 沈みはじめて から 水平に なって 消える まで、白い 水の 先で 高い 潮しぶきが 左から 右へ つぎつぎに ふき上がる。
    #   第4.107版：絵の 大きさは かえない。小波の うしろ（海の 線の 下：D だけ 下）から PL_RISE 秒 かけて ふき上がり（白く なるのも 0.3秒 以上
    #   かけて）、上で 少し 止まって、うしろ（左）へ 流れながら 落ちて うすく なる
    for k, (t0, x, sc, nm) in enumerate(PLUME):
        L = min(PL_LIFE, PL_END - t0)
        D = PL_H * sc
        css += _win(f'ukPl{k}', [(0, f'{o0};transform:translate(0,{f(D, 1)}px)'), (t0, f'{o0};transform:translate(0,{f(D, 1)}px)'),
                                 (t0 + .12, f'opacity:.7;transform:translate(0,{f(.35 * D, 1)}px)'),
                                 (t0 + PL_RISE, 'opacity:.95;transform:translate(0,0)'),
                                 (t0 + PL_RISE + .22, 'opacity:.9;transform:translate(-3px,-3px)'),
                                 (t0 + .55 + (L - .55) * .5, f'opacity:.5;transform:translate(-9px,{f(.14 * D, 1)}px)'),
                                 (t0 + L, f'{o0};transform:translate(-14px,{f(.32 * D, 1)}px)')])
    t0, x, sc = CROWN                          # 波の 先が 落ちた 所で はねる しぶき（第4.107版：小波の うしろから ふき上がる・大きさは かえない）
    D = 70 * sc
    css += _win('ukCr', [(0, f'{o0};transform:translate(0,{f(D, 1)}px)'), (t0, f'{o0};transform:translate(0,{f(D, 1)}px)'),
                         (t0 + .12, f'opacity:.7;transform:translate(0,{f(.4 * D, 1)}px)'),
                         (t0 + .32, 'opacity:.92;transform:translate(-1px,0)'),
                         (t0 + .52, 'opacity:.85;transform:translate(-3px,-3px)'),
                         (t0 + .95, f'{o0};transform:translate(-8px,{f(.25 * D, 1)}px)')])
    # 小波の 層（第4.106版）：層の 上がり（大波に 合わせて）・体と 頭が 右から 左へ 流れる（1まいぶん で くり返し・頭は 体より ゆっくり）
    css += kf('ukRb', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-RB_TILE}px)')])
    for k, p in enumerate(RB_ROWS):
        css += kf(f'ukRwL{k}', row_stops(k))
    return css


def pos_css():
    """第4.107版（まさちゃん「大波は出てくる位置ランダムにして！」）：大波 2つの 出る 場所（UK_POS：1回ごとに かえる・7回で 1回り）の @keyframes。
       ukP1＝大波（左に 出た 回は くずれて 右へ 走る 間 T_LAND → UK_RUN に 少し 長く 走って 馬を 追いこす）・ukP2＝小さい 大波
       （0.7倍は いつも 同じ＝のばさない）。場所を かえるのは 1回の UK_SW 秒（2つとも 見えない 間）だけ（4ミリ秒で とぶ）"""
    N = len(UK_POS)
    T = N * WAVE_T
    e = .004

    def pc(t):
        return t / T * 100

    def tr1(x):
        return f'transform:translateX({f(x, 2)}px)'

    def tr2(x):
        return f'transform:translateX({f(G2_DX + x, 2)}px) scale({f(G2_S)})'

    s1, s2 = [(0, tr1(UK_POS[0][0]))], [(0, tr2(sum(UK_POS[0])))]
    for j, (x, dg) in enumerate(UK_POS):
        t0 = j * WAVE_T
        E = max(0.0, UK_PASS - UK_FRONT - x)
        if E > 0:
            s1 += [(pc(t0 + T_LAND), tr1(x) + ';animation-timing-function:ease-in-out'), (pc(t0 + UK_RUN), tr1(x + E))]
        nx, ndg = UK_POS[(j + 1) % N]
        s1 += [(pc(t0 + UK_SW - e), tr1(x + E)), (pc(t0 + UK_SW), tr1(nx))]
        s2 += [(pc(t0 + UK_SW - e), tr2(x + dg)), (pc(t0 + UK_SW), tr2(nx + ndg))]
    s1.append((100, tr1(UK_POS[0][0])))
    s2.append((100, tr2(sum(UK_POS[0]))))
    return kf('ukP1', s1) + kf('ukP2', s2)


# ---------------------------------------------------------------- 帆かけ舟（第4.108版：まさちゃん「この船もランダムで動くようにして！」→
#   「ランダムで船は、馬より右側に行くようにして！9秒に1回中心と右側でいききして！船のゆらゆらはそのままで！」）
# 舟は 9秒ごとに まん中（x 177〜197）と 走る 馬の 右がわ（x 334〜353：馬の 鼻先 x 約308 より 右）を 行き来する（BT_PATH：72秒で 1回り＝
#   8回 行き来。行き先・出る までの 間（0.6〜1.4秒）・かかる 秒（6.8〜7.6秒）を 1回ごとに かえて くり返しに 見えない ように。着いたら 波に
#   押されて 左へ 2〜3px ながれる）。とちゅうは 馬の うしろを とおる。舟は 3つ目の 層（BT_ROW：舟の すぐ 前の 層）の 波の 頭に のって 上下し、
#   波の かたむきに 合わせて かたむく（その 層の 波の 頭の 線＝ ukiyoe.ribbon の edge を 舟の 下で ならした 高さと かたむき：bt_ride。72秒は
#   その 層の 頭が 流れる 24秒の 3回り＝舟と 波が いつも 合う）。大波が 落ちて 海が ふくらむ 間は 層と いっしょに 上がり、大きく ゆれる
#   （7秒ごと：bt_rock_stops）。この ゆらゆらは 第4.108版の はじめの 形の まま（まさちゃん「船のゆらゆらはそのままで！」）。
#   舟の 底は いつも 波の 頭の 線より 下（うかない）・帆は いつも 波の 上（しずまない）。大波は 舟の 前を とおる（舟は 大波の うしろに かくれる）。
#   絵は のばさない（うつす・回す だけ）
BT_T = 72.0                 # 舟の 1回り（秒）＝ 9秒の 行き来 8回 ＝ 舟の 前の 層の 波の 頭が 流れる 1回り（24秒）の 3回り
BT_AT = (166, 72)           # 舟の 箱の 左上（第4.107版と 同じ 所：行き来する 道は ここからの ずれ）。止まった 絵の 時（0.75秒）は 大波の うしろ（見えない）
BT_O = (19, 26.1)           # 舟を 回す 中心（絵の 中：底の まん中の 少し 上）
BT_ROW = 2                  # 舟の すぐ 前の 波の 層（この 層の 波の 頭に のる）
# 舟の まん中の x（秒, x, はやさ px/秒）：3次の 曲線で つなぐ（はやさ 0 の 所で 止まる）。9秒ごとに（0・9・18…63秒）まん中 ⇄ 馬の 右がわ：
#   出る（0.6〜1.4秒 あと）→ 6.8〜7.6秒 かけて 着く（いちばん はやくて 約35px/秒）→ 波に 押されて 左へ 少し ながれて 次の 出る 時を まつ
BT_PATH = [(0.0, 185, 0.0), (1.0, 184, 0.0), (8.0, 341, 0.0), (9.7, 338, 0.0), (17.0, 191, 0.0), (19.4, 189, 0.0),
           (26.2, 335, 0.0), (27.9, 332, 0.0), (35.3, 179, 0.0), (36.6, 177, 0.0), (44.2, 353, 0.0), (46.2, 350, 0.0),
           (53.2, 197, 0.0), (54.8, 195, 0.0), (61.9, 339, 0.0), (64.3, 336, 0.0), (71.5, 186, 0.0)]
BT_HULL = 12                # 舟の 底の 半分の 長さ（絵の x 7〜31）
BT_SPAN = 15                # 波の 高さと かたむきを ならす 半分の はば（舟の 長さ くらい）
BT_LIFT = 2.0               # 回す 中心が 波の 頭の 線（舟の 下で ならした 所）より 何 px 下（底は その 0.9px 下）
BT_TAU = .08                # 舟の 動きの おくれ（秒：2回 ならす）
BT_TILT = (.55, 4.0)        # 波の かたむきの 何倍 かたむくか・いちばん 大きい 角度（やわらかく おさえる）
BT_ROCK = (4.5, 1.5, 1.2, 1.35)   # 大波が 落ちた あとの ゆれ：角度・1回りの 秒・へる 秒・はじまる 秒（7秒の 中）


def bt_x(t):
    """舟の まん中の x（t 秒：BT_PATH を 3次の 曲線で つなぐ・BT_T で くり返す）"""
    t %= BT_T
    P = BT_PATH + [(BT_T, BT_PATH[0][1], BT_PATH[0][2])]
    for (t0, x0, v0), (t1, x1, v1) in zip(P, P[1:]):
        if t <= t1:
            h = t1 - t0
            s = (t - t0) / h
            return ((2 * s ** 3 - 3 * s ** 2 + 1) * x0 + (s ** 3 - 2 * s ** 2 + s) * h * v0
                    + (3 * s ** 2 - 2 * s ** 3) * x1 + (s ** 3 - s ** 2) * h * v1)
    return P[-1][1]


def bt_edge(ribbon, k=BT_ROW):
    """層 k の 波の 頭の 線（ukiyoe.ribbon の edge：画面の 1px ごと・帯の 上から 下へ の px）。なければ []"""
    E = (ribbon or {}).get('edge') or []
    s = E[k] if k < len(E) else ''
    return [int(s[j:j + 2], 16) * .02 for j in range(0, len(s) - 1, 2)]


def bt_ride(edge, dt=.048):
    """舟の 1回り（BT_T 秒）の (秒, x, y, 角度)：舟の 下の 波の 頭の 線（edge）を ならした 高さと かたむきに のる
       （x・y：回す 中心の 上の絵の 中の 場所。y は 層の 上がりを 入れない＝ukBb が 7秒ごとに 足す）"""
    p = RB_ROWS[BT_ROW]
    Tc = float(f(RB_TILE / (p['v'] * (1 - RB_FWD)), 2))        # 層の 波の 頭の 流れの 1回り（CSS と 同じ 秒）
    N = len(edge)

    def E(u):
        u = (u - .5) % N
        i = int(u)
        a = u - i
        return edge[i] * (1 - a) + edge[(i + 1) % N] * a
    Wt = [(dx, math.cos(math.pi * dx / (2 * (BT_SPAN + 1))) ** 2) for dx in range(-BT_SPAN, BT_SPAN + 1)]
    sw = sum(w for _, w in Wt)
    sxx = sum(w * dx * dx for dx, w in Wt)
    al = 1 - math.exp(-dt / BT_TAU)
    n = int(round(BT_T / dt))
    y1 = y2 = a1 = a2 = None
    out = []
    for i in range(3 * n):                                       # 2回り 回して ならしを おちつかせ、3回り目を 使う
        t = i * dt
        x = bt_x(t)
        u = x + RB_TILE * ((t / Tc) % 1)
        ys = [(dx, w, E(u + dx)) for dx, w in Wt]
        m = sum(w * e for _, w, e in ys) / sw
        sl = sum(w * dx * (e - m) for dx, w, e in ys) / sxx
        ang = BT_TILT[1] * math.tanh(math.degrees(math.atan(sl)) * BT_TILT[0] / BT_TILT[1])
        if y1 is None:
            y1 = y2 = m
            a1 = a2 = ang
        y1 += al * (m - y1)
        y2 += al * (y1 - y2)
        a1 += al * (ang - a1)
        a2 += al * (a1 - a2)
        if i >= 2 * n:
            out.append((t - 2 * BT_T, x, p['top'] + y2 + BT_LIFT, a2))
    return out


def _simplify(pts, tol):
    """折れ線を へらす（どの 値も tol より ずれない 点だけ のこす）：pts＝[(秒, 値…)]"""
    keep = [0]
    i = 0
    n = len(pts)
    while i < n - 1:
        j = i + 2
        while j < n:
            t0, t1 = pts[i][0], pts[j][0]
            ok = True
            for m in range(i + 1, j):
                s = (pts[m][0] - t0) / (t1 - t0)
                for c, tl in enumerate(tol, 1):
                    if abs(pts[i][c] + (pts[j][c] - pts[i][c]) * s - pts[m][c]) > tl:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
            j += 1
        i = j - 1
        keep.append(i)
    return [pts[k] for k in keep]


def bt_stops(edge):
    """舟の 1回りの @keyframes の 点（ukBt：translate と rotate だけ・のばさない。0.048秒＝0.1％ ごとの 点を へらす）"""
    ride = bt_ride(edge)
    ride.append((BT_T,) + ride[0][1:])
    pts = _simplify(ride, (.12, .08, .25))
    ox, oy = BT_AT[0] + BT_O[0], BT_AT[1] + BT_O[1]
    return [(t / BT_T * 100, f'transform:translate({f(x - ox, 1)}px,{f(y - oy)}px) rotate({f(a, 1)}deg)') for t, x, y, a in pts]


def bt_rock(t):
    """舟の ゆれ（7秒の 中の t 秒）：(下へ の px, 角度)。層と いっしょに 上がる（row_stops と 同じ）・大波が 落ちた あとは 大きく ゆれる
       （回すと 高く なる 方の 舟の 底の はしは そのまま の 高さ＝底が 波の 上に 出ない）"""
    p = RB_ROWS[BT_ROW]
    A, P, D, S = BT_ROCK
    u = t - S
    ph = A * math.sin(2 * math.pi * u / P) * math.exp(-u / D) * min(1.0, u / .3) if u > 0 else 0.0
    return -p['rise'] * sea_amp(t) + BT_HULL * abs(math.sin(math.radians(ph))), ph


def bt_rock_stops(step=.1, end=5.0):
    """舟の ゆれの @keyframes（ukBb：7秒ごと。row_stops と 同じ 0.1秒ごとの 点を へらす）"""
    pts, t = [], 0.0
    while t < end + 1e-6:
        pts.append((t,) + bt_rock(t))
        t = round(t + step, 6)
    pts.append((WAVE_T,) + bt_rock(0.0))
    return [(_pc(t), f'transform:translateY({f(dy)}px) rotate({f(ph, 1)}deg)') for t, dy, ph in _simplify(pts, (.03, .1))]


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。「神奈川沖浪裏」の形の大波（白い背中、濃い藍に白いすじ、'
           'まるい爪のような白い泡の先、爪から落ちるしぶきの点。根もとと巻きの下は濃い藍のぼかし）。七秒ごとに、毎回ちがう場所で、うしろへねた波が海の中から出てきて立ち上がり、'
           'いちばん高くなると止まらずに波の先が前へ投げ出されて爪が下へ巻きこみ、しぶきの点が前へとび、頭からしぶきともやがうしろへ吹き飛ぶ。'
           '波の先が落ちて白い水になり、大波は前へたおれて低くなりながら右へ走る。沈みはじめてから水平になって消えるまで、'
           '白い水の先で高い潮しぶき（もやの柱と白いつぶ）が小波のうしろからつぎつぎにふき上がり、うしろへ流れながら落ちる。'
           '走る馬を追いこして、馬の右で水平になり、手前の小波のむこうへ消える。手前には、ひとまわり小さく低い大波が重なり、ほぼ同じときに少しおくれて同じように立ち上がってくずれる。'
           'そのあとは、次の大波まで小波だけが動く。'
           '海は小波の層が四つ重なってうめつくす（ひとつの層がひとつのつながった絵：ゆるくうねる波の頭に墨の線とうすい白い泡、その下に大波と同じ爪と藍、'
           'さらに下は藍の体に明るい青のさざなみ。おくほど小さくかすむ）。層は右から左へ流れ（走る馬の方がはやいので、海はうしろへ流れて見える。遠い海ほどゆっくり）、'
           '波の頭は体よりゆっくり流れるので、波は右へころがって見える。大波が水平になるときに層が少し上がる。'
           '沖の帆かけ舟は、九秒ごとにまん中と走る馬の右がわを行き来し（行き先と速さは毎回少しずつちがう）、'
           'すぐ前の小波の頭にのって上下にゆれ、波のかたむきに合わせてかたむく。大波が落ちたあとは大きくゆれ、大波のうしろにかくれることもある。'
           '手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走る。'
           'ときどき街道のむこうから、ちょんまげに羽織と袴、刀を二本さしたお侍さんが一人か二人歩いてきて、馬とすれちがうときに会釈する。右上に朱の印のイラスト')
    foam = B.get('foam')                     # しぶき（make/ukiyoe_foam.py の 絵の シート）
    parts = foam['parts'] if foam else {}
    wave = B.get('wave')                     # 大波の 一生の コマ
    ribbon = B.get('ribbon')                 # 小波の 層 4つ（第4.106版：1つの 層が 頭と 体の 2本の つながった 絵：make/ukiyoe_mini.py → ukiyoe.ribbon）

    def row(k):                              # 層 k：波の 体（右から 左へ）→ 波の 頭（前・体より ゆっくり 左へ＝体に 対して 右へ ころがる）
        if not ribbon:
            return ''
        return f'<i class="ukRw ukR{k}"><i class="ukRb"></i><i class="ukRc"></i></i>'

    def big(g):                              # 大波（g1：いまの 大波・g2：小さく 低い 大波＝同じ コマと しぶきを 0.7倍・0.28秒 おくれ）
        o = f'<i class="ukG g{g}">'
        if wave and wave.get('cells'):
            o += '<i class="ukWv"></i>'
        if 'sp1' in parts:
            o += '<i class="ukSp s1 ukF sp1"></i><i class="ukSp s2 ukF sp2"></i>'
        o += img('ukMs m1', mist_svg()) + img('ukMs m2', mist_svg())
        if 'bs0' in parts:                   # 波の 先が 落ちた 所で 横へ ひろがる しぶき
            o += '<i class="ukCr ukF bs0"></i>'
        if 'pl0' in parts:                   # 沈みはじめて から 水平に なる まで 白い 水の 先で ふき上がる 高い 潮しぶき（第4.106版）
            o += ''.join(f'<i class="ukPl p{k} ukF {nm}"></i>' for k, (t0, x, sc, nm) in enumerate(PLUME))
        return o + '</i>'

    html = f'<div class="ukw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ukSky', sky_svg()) + img('ukKs', kasumi_svg()) + img('ukSea', sea_svg())
    html += ''.join(row(k) for k in range(RB_BACK))                  # おくの 波の 層 2つ（大波と 舟の うしろ）
    html += f'<i class="ukBt">{img("ukBb", boat_svg())}</i>'      # 帆かけ舟（第4.108版：外＝行き来する 道と 波に のる・中＝7秒ごとの ゆれ）
    html += big(1) + big(2)                  # 神奈川沖浪裏の 大波 2つ（make/ukiyoe_great.py の 波の 一生の コマ）
    html += ''.join(row(k) for k in range(RB_BACK, len(RB_ROWS)))    # 手前の 波の 層 2つ（大波は この むこうへ 消える・いちばん 手前は 石の 土手の うしろまで）
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
           f'.ukw .ukBt{{left:{BT_AT[0]}px;top:{BT_AT[1]}px;width:38px;height:29px;transform-origin:{f(BT_O[0])}px {f(BT_O[1])}px;animation:ukBt {f(BT_T)}s linear infinite}}'
           f'.ukw .ukBt>img{{position:absolute;display:block;left:0;top:0;width:38px;height:29px;transform-origin:{f(BT_O[0])}px {f(BT_O[1])}px;'
           f'animation:ukBb {f(WAVE_T)}s linear infinite}}'
           '.ukw .ukG{left:0;top:0;width:390px;height:160px}.ukw .ukG>*{position:absolute;display:block}'
           # 第4.107版：大波 2つの 出る 場所（1回ごとに かえる：pos_css）。小さい 大波の 0.7倍は いつも 同じ（のばさない）
           f'.ukw .ukG.g1{{animation:ukP1 {f(len(UK_POS) * WAVE_T)}s linear infinite}}'
           f'.ukw .ukG.g2{{transform:translateX({f(G2_DX)}px) scale({f(G2_S)});transform-origin:{WB[0]}px 112px;animation:ukP2 {f(len(UK_POS) * WAVE_T)}s linear infinite}}'
           f'.ukw .ukMs{{width:90px;height:40px;opacity:0}}.ukw .ukMs.m1{{left:112px;top:-6px;animation:ukMs1 {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukMs.m2{{left:146px;top:2px;animation:ukMs2 {f(WAVE_T)}s linear infinite}}'
           f'.ukw .ukSp{{left:87px;top:-18px;width:84px;height:44px;opacity:0}}'
           f'.ukw .ukSp.s1{{animation:ukSp1 {f(WAVE_T)}s linear infinite}}.ukw .ukSp.s2{{top:-12px;animation:ukSp2 {f(WAVE_T)}s linear infinite}}'
           # 波の 層（外：大波に 合わせた 上がり／ukRb：波の 体・右から 左へ 流れる／ukRc：波の 頭・体より ゆっくり 左へ＝体に 対して 右へ ころがる）
           '.ukw .ukRw{left:0;width:390px;height:30px}'
           '.ukw .ukRw i{position:absolute;display:block}'
           '.ukw .ukCr,.ukw .ukPl{opacity:0}'      # 場所と 大きさ（しぶきの 絵の シートの 中）は 下の foam の 所
           + f'.ukw .ukPn{{left:0;top:{56 - PN_UP}px;width:{2 * TILE}px;height:{PN_H}px;background-size:{TILE}px {PN_H}px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * 1.12, 3)}s linear infinite}}'
           f'.ukw .ukRd{{left:0;top:116px;width:{2 * TILE}px;height:26px;background-size:{TILE}px 26px;background-repeat:repeat-x;animation:ukFlow {ROAD_S}s linear infinite}}'
           f'.ukw .ukBk{{left:0;top:136px;width:{2 * TILE}px;height:28px;background-size:{TILE}px 28px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * .82, 3)}s linear infinite}}'
           '.ukw .ukSl{left:364px;top:6px;width:18px;height:18px}'
           f'.ukw .ukSm{{left:0;top:{f(SM_TOP)}px;width:{f(SM_W * SM_K)}px;height:{f(SM_H * SM_K)}px;overflow:hidden;transform:translateX(500px)}}'
           f'.ukw .ukSm>i{{position:absolute;display:block;left:0;top:0;height:{f(SM_H * SM_K)}px;background-repeat:no-repeat}}'
           f'.ukw .ukSm .w{{width:{f(12 * SM_W * SM_K)}px}}.ukw .ukSm .b{{width:{f(len(BOW) * SM_W * SM_K)}px;opacity:0}}')
    for k, p in enumerate(RB_ROWS):             # 層 k の 箱：上の はしは 波の 頭の 線より RB_PAD 上・下の はしは 石の 土手の うしろ・大波に 合わせて 少し 上がる
        top = p['top'] - RB_PAD
        css += (f'.ukw .ukRw.ukR{k}{{top:{f(top, 2)}px;height:{f(RB_BOT - top, 2)}px;'
                f'transform-origin:50% 100%;animation:ukRwL{k} {f(WAVE_T)}s linear infinite}}')
    if ribbon:                                  # 小波の 層（1まいの シートに 4層 × 頭と 体 が たてに ならぶ・はばは くり返しの 1まいぶん）
        zr = ribbon['z']
        rw_, rh_ = ribbon['sheet'][0] / zr, ribbon['sheet'][1] / zr
        for k, p in enumerate(RB_ROWS):
            cy, ch, by, bh, bt = ribbon['rows'][k]
            bg = f'background:url({ribbon["url"]}) 0 {{}}px/{f(rw_, 2)}px {f(rh_, 2)}px repeat-x'
            css += (f'.ukw .ukR{k} .ukRb{{left:0;top:{f(RB_PAD + bt, 3)}px;width:{2 * RB_TILE}px;height:{f(bh / zr, 3)}px;'
                    f'{bg.format(f(-by / zr, 3))};animation:ukRb {f(RB_TILE / p["v"], 2)}s linear infinite}}'
                    f'.ukw .ukR{k} .ukRc{{left:0;top:{f(RB_PAD)}px;width:{2 * RB_TILE}px;height:{f(ch / zr, 3)}px;'
                    f'{bg.format(f(-cy / zr, 3))};animation:ukRb {f(RB_TILE / (p["v"] * (1 - RB_FWD)), 2)}s linear infinite}}')
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
    if wave and wave.get('cells'):             # 大波：コマを step-end で 入れかえ（のばさない・ちぢめない）
        z = wave['z']
        sw_, sh_ = wave['sheet']
        css += (f'.ukw .ukWv{{left:{WB[0]}px;top:{WB[1]}px;width:0;height:0;opacity:0;'
                f'background:url({wave["url"]}) 0 0/{f(sw_ / z, 2)}px {f(sh_ / z, 2)}px no-repeat;animation:ukWv {f(WAVE_T)}s step-end infinite}}'
                + life_css(wave))
    if foam:                                        # 小波と しぶきの 部品は 1まいの シートの 中の 場所で えらぶ
        z_ = foam['z']
        sw_, sh_ = foam['sheet']
        css += f'.ukw .ukF{{background:url({foam["url"]}) 0 0/{f(sw_ / z_, 3)}px {f(sh_ / z_, 3)}px no-repeat}}'
        css += ''.join(f'.ukw .ukF.{nm}{{background-position:{f(-x_ / z_, 3)}px {f(-y_ / z_, 3)}px}}' for nm, (x_, y_, w_, h_) in parts.items())

        def at(nm, sc, bx, by, fx, fy):
            """しぶきの 部品 nm を sc 倍の 決まった 大きさで（時間で かえない）：部品の 中の (fx, fy)（0..1）が 上の絵の (bx, by) に くる"""
            x_, y_, w_, h_ = parts[nm]
            w, h = w_ / z_ * sc, h_ / z_ * sc
            return (f'left:{f(bx - w * fx, 2)}px;top:{f(by - h * fy, 2)}px;width:{f(w, 2)}px;height:{f(h, 2)}px;'
                    f'background-size:{f(sw_ / z_ * sc, 3)}px {f(sh_ / z_ * sc, 3)}px;background-position:{f(-x_ / z_ * sc, 3)}px {f(-y_ / z_ * sc, 3)}px')
        if 'bs0' in parts:                          # 波の 先が 落ちた 所の しぶき（下の まん中が 海の 線）
            css += f'.ukw .ukCr.ukF{{{at("bs0", CROWN[2], CROWN[1], 108, .5, 66 / 70)};animation:ukCr {f(WAVE_T)}s linear infinite}}'
        if 'pl0' in parts:                          # 白い 水の 先の 高い 潮しぶき（下の まん中が ふき上がる 所）
            css += ''.join(f'.ukw .ukPl.ukF.p{k}{{{at(nm, sc, x, 112, .55, (PL_H - 4) / PL_H)};animation:ukPl{k} {f(WAVE_T)}s linear infinite}}'
                           for k, (t0, x, sc, nm) in enumerate(PLUME))
    css += samurai_css()
    if run:
        n, (cw, ch), (ax, ay) = run['frames'], run['cell'], run['at']
        w, h = cw / 2, ch / 2
        css += (f'.ukw .ukH{{left:{f(ax / 2)}px;top:{f(ay / 2 - 7)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'   # 7px 上：ひづめを 街道の まん中に
                f'.ukw .ukH>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({run["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;animation:ukRun .48s steps({n}) infinite}}'
                + kf('ukRun', [(100, f'transform:translateX({f(-n * w)}px)')]))
    css += (kf('ukFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-TILE}px)')])
            + kf('ukKs', [(0, 'transform:translateX(-8px)'), (50, 'transform:translateX(10px)'), (100, 'transform:translateX(-8px)')])
            + kf('ukBt', bt_stops(bt_edge(ribbon) or [1.3] * RB_TILE)) + kf('ukBb', bt_rock_stops())
            + wave_life_css() + pos_css())
    # 小さい 大波は 0.28秒 おくれ（第4.107版：−(7−0.28)秒 ずらす＝ほんとうに おくれる。ほかの animation の 書き方より 強く）。
    #   場所の animation（ukP2：.ukG.g2 じしん）は ずらさない（場所を かえる 時は 2つとも 見えない）
    css += f'.ukw.ukw .ukG.g2 *{{animation-delay:{f(-(WAVE_T - G2_LAG), 2)}s}}'
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
    alt='浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。「神奈川沖浪裏」の形の大波（白い背中・濃い藍に白いすじ・まるい爪の泡：七秒ごとに、毎回ちがう場所で、海の中から出てきて立ち上がり、波の先を投げ出してしぶきをとばし、前へたおれながら右へ走る。沈みはじめてから水平になって消えるまで、白い水の先で高い潮しぶきがつぎつぎにふき上がり、走る馬を追いこして水平になって消える。手前にはひとまわり小さく低い大波が重なり、ほぼ同じときに少しおくれて同じように立ち上がる）。海は小波の層が四つ重なってうめつくし（ひとつの層がひとつのつながった絵：うねる波の頭にうすい白い泡と大波と同じ爪、その下は藍の体に明るい青のさざなみ）、層は右から左へ流れ（走る馬の方がはやく、遠い海ほどゆっくり）、波の頭は体よりゆっくり流れて右へころがって見える。沖の帆かけ舟は九秒ごとにまん中と馬の右がわを行き来して、波にのってゆれる。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走り、ときどきお侍さんとすれちがう。右上に朱の印',
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
                   '7秒ごとに 毎回 ちがう 場所で 海の 中から 出て きて 立ち上がり、波の 先を 投げ出して しぶきが とび、前へ たおれて 低く なりながら 右へ 走り、'
                   '沈みはじめ から 水平に なって 消える まで 白い 水の 先で 高い 潮しぶきが つぎつぎに ふき上がる・'
                   '走る 馬を 追いこして 水平に なって 消える。手前に 小さく 低い 大波が ほぼ 同じ 時に（0.28秒 おくれ）重なる）・'
                   '小波の 層 4つ（1つの 層が 1まいの つながった 絵：うねる 波の 頭に うすい 白い 泡と 大波と 同じ 爪・その 下は 藍の 体に 明るい 青の さざなみ＝青が 多く 見える・'
                   'おくほど 小さく かすむ・右から 左へ 流れる（馬の 方が はやい・遠い 海ほど ゆっくり）・波の 頭は 体より ゆっくり 流れて 右へ ころがって 見える・'
                   '大波が 水平に なる と 層が 少し 上がる）・'
                   '9秒ごとに まん中と 馬の 右がわを 行き来する 帆かけ舟（波に のって ゆれる・大波の あとは 大きく ゆれる）・松並木の 街道・朱の 布の 白い 馬（墨の 輪郭）・ときどき すれちがう お侍さん・朱の 印'),
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
