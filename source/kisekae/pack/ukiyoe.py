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
   第4.103版「ダメだ小波だけがどうしても納得いかない。絵を大波に似せた小波で作成して」「そしたら大波が崩れはじめて横長になったあたりの大波にして！あと小波は上の白い波と少し青の海が目立つ部分だけが見えるようにして、海が動いているようにして！」）
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
   上の絵：和紙の 地・空の 上に 藍の ぼかし・赤い 日・藍の ぼかしの 山なみ・かすみ（横の 雲の 帯）。
     左に 神奈川沖浪裏の 大波（画像から 切りぬいて 浮世絵の 平らな 4つの 色＝白・明るい 青・藍・濃い 藍 に まとめた 絵。
     白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点。空・題箋・落款は すける・舟と 人・富士山は 入れない。
     泡の 爪は 少し まるく・ぼかし（bokashi）で 根もとと 巻きの 下を 濃く・白い 背中の 下を 明るい 青に）。
     海は 小波（大波が くずれはじめて 横長に なった 所の 上の 白い 波と 少しの 青：大波と 同じ 絵を 小さく・1つずつ 大きさと コマが ちがう）が
     列 2つ（おく＝大波の うしろ・手前＝大波の 前）と 潮しぶき。
     沖に 帆かけ舟。手前に 海ぞいの 街道（松並木・土の 道・草の 土手）。白い 馬（朱の 布と 手綱・墨の 輪郭：pack/make/ukiyoe_art.py）が 街道を 右へ 走る。右上に 朱の 印（白い 蹄鉄）
   動き（3秒に 1回 大波：出て きて から 水平に なる まで 約1.9秒・止まらずに）：
     海の 中から うしろへ ねた 波が 出て きて 立ち上がり（頭が 立って 爪が のびる）→ 神奈川沖浪裏（止まらずに すぎる）→ 波の 先が 前へ 投げ出されて 爪が 下へ
     巻きこみ、しぶきの 点が 前へ とび、頭から しぶきと もやが うしろ（左）へ 吹き飛ぶ → 波の 先が 落ちて 白い 水に なり、
     大波は 前へ たおれて 低く なりながら 横長に のびて 右へ 走る（白い 水の 先で 潮しぶきが 左から 右へ じゅんに ふき上がる）→ 走る 馬を 追いこして、
     馬の 右で 水平に なって 手前の 小波の むこうへ 消える（うすく しない）→ しずか → 次の 波。
     小波は 1つずつ 時を ずらして 海の 線の 下から 上がって きて、白い 波が 前へ たおれながら 右へ のび、少し 上下して また 海の 線の 下へ 沈む
     （うすく しない・生きて いる 間 ずっと 右へ 進む＝海が 動いて 見える・おくの 列は 小さく ゆっくり）。列 ぜんたいは 大波が 水平に なる 間に ふくらむ。舟が ゆれる・かすみが ゆっくり ただよう・街道と 松並木と 土手が 右から 左へ 流れる（馬が 前へ 進んで 見える）。
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


# ---------------------------------------------------------------- 大波（第4.95版 → 第4.100版：まさちゃん「波の先端だけ動くの変だから、波が出てきて、徐々に水平になっていくようにして！
#   今だと今ある絵が伸び縮みしてて変だから、ちゃんと形を変えながらリアルに出てきたり、水平になっていったりして！」「大波は出てきてから水平になるまで、もっと早くして！」
#   「大波の動作も止まったり鈍いとへんだからリアルに！」）
# 葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 左の 大波を 画像から 切りぬいて 浮世絵の 平らな 4つの 色（白・明るい 青・藍・濃い 藍）に まとめた 絵
# （make/ukiyoe_great.py：空・題箋・落款は すける・舟と 人・富士山は 入れない・泡の 爪を 少し まるく（第4.97版）・ぼかしで 立体の かげ（第4.99版））。
# 第4.100版：波の 一生を 1まいずつ 描いた コマ（life：24コマ／秒・1.9秒）に した。絵を のばしたり ちぢめたり（scale）しない：
#   ① 海の 中から うしろへ ねた 波が 出て きて 立ち上がる（うつす・回す・高い 所ほど かたむける・頭の 巻き c −1→0＝頭が 立って 爪が のびる）
#   ② 神奈川沖浪裏（止まらずに すぎる）③ 波の 先を 投げ出して 前へ のりだす（c 0→1・爪の 下の しぶきの 点が 前へ とんで 落ちる）
#   ④ 落ちる（c→1.6・落ちた 所で 潮しぶき）⑤ 左の 根もとを 軸に 前へ たおれて だんだん 低く なり、水平に なって 手前の 小波の むこうへ 消える（うすく しない）
#   ⑥ 次の 波まで しずか（3秒に 1回）。コマは 中身の ある 四角だけ を 1まいの シートに つめて あり、step-end で 入れかえる（すけて 形を 入れかえる こと なし）
WB = (-22, 2)                          # コマの 絵の 左上（上の絵の 中・第4.97版と 同じ 場所）
WAVE_T = 3.0                           # 3秒に 1回 大波（第4.98版 まさちゃん「大波が出てくるのは3秒に一回にして！」）
T_PEAK, T_PITCH, T_LAND, T_FLAT = 0.75, 1.12, 1.30, 2.05   # いちばん 高い・のりだす・落ちる・水平（make/ukiyoe_great.py の LIFE_KEYS と 同じ）
PEEL = [(1.12, 214, 1.1), (1.25, 232, 1.05), (1.38, 254, 1.0), (1.51, 280, .95), (1.64, 306, .9), (1.77, 330, .85), (1.90, 352, .75)]
#   第4.101版：白い 水の 先（大波が 横長に のびて 右へ 走る 先）で 潮しぶきが 左から 右へ じゅんに ふき上がる（時・上の絵の x・大きさ）。
#   馬（x 190〜312）の うしろを とおって 追いこす（馬は 手前）


# ---------------------------------------------------------------- 小波（第4.97版 → … → 第4.102版 → 第4.103版：まさちゃん「ダメだ小波だけがどうしても納得いかない。
#   絵を大波に似せた小波で作成して」「そしたら大波が崩れはじめて横長になったあたりの大波にして！あと小波は上の白い波と少し青の海が目立つ部分だけが
#   見えるようにして、海が動いているようにして！」）
# 小波は 大波の 子ども（小さな 大波）：大波の 一生の コマ（make/ukiyoe_great.py の life＝ukiyoe.wave の シート）の うち、くずれはじめて 横長に なった 所
#   （コマ 28〜39：波の 先が 白い 水に 落ちて、前へ たおれながら 横に のびる 所）を そのまま 小さく 使う（0.17〜0.31倍・絵を 足さない・同じ シート）。
#   上の 白い 波（白い 背中・藍の 巻いた 泡の 爪）と その 下の 少しの 青だけ が 見える（MW_D：絵の 上から 44px より 下は 列の 海の 線で 切る）。
#   左右に うら返さない・のばしたり ちぢめたり しない（たて横 同じ 倍率の まま・コマを step-end で 入れかえる）。
# 動き（海が 動いて 見える）：小波 1つずつ 海の 線の 下から 上がって きて（0〜16%）、コマが すすんで 白い 波が 前へ たおれながら 右へ のび
#   （16〜80%・すこし 上下）、また 海の 線の 下へ 沈む（〜92%：うすく しない）。生きて いる 間 ずっと 右へ 進む（MW_ROWS の dx）。
#   1つずつ コマの はんい（MW_VARS）・倍率・長さ・ずれが ちがう＝となりどうしは 似ない。おくの 列は 小さく ゆっくり かすむ。
#   列 ぜんたいは 大波に 合わせて 少し ふくらむ（たて横 同じ 倍率・大波が 水平に なる 間が いちばん 大きい）
MW_D = 44.0                           # 見せる 深さ（大波の コマの 絵の px）：上の 白い 波＋少しの 青
MW_SINK = MW_D + 6                    # 沈む ときの 深さ（絵の px）：見せる 所が ぜんぶ 海の 線の 下へ
MW_KEEP = .85                         # コマが すすむと 上の はしが 下がる ぶんを この わりあい だけ もどす（白い 波が 少しずつ 低く なる）
MW_ROWS = [dict(clip=100.0, dx=12, swell=1.04, rise=.8, haze=.88, head=6),
           dict(clip=108.0, dx=18, swell=1.08, rise=1.6, haze=1.0, head=8)]
MW_VARS = dict(a=(28, 34), b=(29, 36), c=(30, 37), d=(31, 38), e=(32, 39))     # コマの はんい（1 から かぞえる ukiyoe.wave の cells）
# 小波 1つずつ（はじめの 左の x（大波の 絵の 左の はし）・倍率 s・コマの はんい v・一生の 長さ P 秒・ずれ ph（0〜1）・pf：頭の しぶき）
MW_WAVES = [
    [dict(x=-40, s=.19, v='b', P=5.2, ph=.05), dict(x=8, s=.17, v='d', P=4.6, ph=.41), dict(x=56, s=.21, v='a', P=5.6, ph=.77),
     dict(x=104, s=.18, v='e', P=4.9, ph=.23), dict(x=150, s=.20, v='c', P=5.4, ph=.59), dict(x=198, s=.17, v='b', P=4.4, ph=.95),
     dict(x=244, s=.21, v='d', P=5.8, ph=.31), dict(x=292, s=.18, v='a', P=4.8, ph=.67), dict(x=338, s=.20, v='e', P=5.1, ph=.13)],
    [dict(x=-70, s=.28, v='c', P=4.3, ph=.50, pf=True), dict(x=-10, s=.31, v='a', P=3.8, ph=.86), dict(x=52, s=.26, v='e', P=4.6, ph=.22, pf=True),
     dict(x=112, s=.30, v='b', P=4.0, ph=.58), dict(x=172, s=.27, v='d', P=4.4, ph=.94, pf=True), dict(x=230, s=.29, v='c', P=3.9, ph=.30),
     dict(x=290, s=.26, v='a', P=4.7, ph=.66, pf=True), dict(x=346, s=.30, v='e', P=4.1, ph=.02)],
]
MW_T = (.12, .80)                     # コマが すすむ 間（0〜1）
MW_PUFF = 2.0                         # 頭の しぶきの 大きさ（大波の 絵の px の 倍：小波と いっしょに 小さく なる）


def mw_top(wave, k):
    """コマ k（1 から）の 上の はしの y（大波の 絵の px）"""
    return wave['cells'][k - 1][5] / wave['z']


def mw_row_top(k):
    """列 k の 箱の 上の y（いちばん 大きい 小波が ふくらんでも 入る＋しぶきの よゆう）"""
    p = MW_ROWS[k]
    return p['clip'] - max(w['s'] for w in MW_WAVES[k]) * (MW_D + 4) * p['swell'] - p['head']


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


def mini_css(wave):
    """小波（大波が くずれはじめて 横長に なった 所の コマ）：コマの はんい v ごとに コマを step-end で 出す（上の はしが 下がる ぶんを MW_KEEP だけ もどす）・
       海の 線の 下から 上がって 少し 上下して また 沈む（うすく しない）・頭の しぶき（0.3秒 以上 かけて あらわれ、上へ はねて 左へ 流れて 消える）"""
    z = wave['z']
    cells = wave['cells']
    css = ''
    for v, (f0, f1) in MW_VARS.items():
        t0 = mw_top(wave, f0)

        def put(k):
            x, y, w, h, ox, oy = cells[k - 1]
            dy = (oy / z - t0) * MW_KEEP
            return (f'transform:translate({f(ox / z, 2)}px,{f(oy / z - dy, 2)}px);width:{f(w / z, 2)}px;height:{f(h / z, 2)}px;'
                    f'background-position:{f(-x / z, 2)}px {f(-y / z, 2)}px')
        seq = list(range(f0, f1 + 1))
        a, b = MW_T
        st = [(0, put(f0))]
        for j, k in enumerate(seq):
            st.append((round((a + (b - a) * j / len(seq)) * 100, 3), put(k)))
        st.append((100, put(f1)))
        css += kf(f'ukNf{v}', st)
    E_UP, E_IO, E_DN = 'cubic-bezier(.25,.6,.35,1)', 'ease-in-out', 'cubic-bezier(.55,0,.75,.45)'
    css += kf('ukNu', [(0, f'transform:translateY({f(MW_SINK)}px);animation-timing-function:{E_UP}'),
                       (16, f'transform:translateY(0);animation-timing-function:{E_IO}'),
                       (42, f'transform:translateY(-4px);animation-timing-function:{E_IO}'),
                       (66, f'transform:translateY(0);animation-timing-function:{E_DN}'),
                       (92, f'transform:translateY({f(MW_SINK)}px)'), (100, f'transform:translateY({f(MW_SINK)}px)')])
    o0 = 'opacity:0'
    css += kf('ukNpA', [(0, f'{o0};transform:translate(0,2px) scale(.45)'), (26, f'{o0};transform:translate(0,2px) scale(.45)'),
                         (36, 'opacity:.95;transform:translate(-2px,-2px) scale(.85)'), (46, 'opacity:.7;transform:translate(-6px,-6px) scale(1.05)'),
                         (58, f'{o0};transform:translate(-11px,-3px) scale(1.2)'), (100, f'{o0};transform:translate(-11px,-3px) scale(1.2)')])
    return css


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
    """小波の 列 k の ふくらみ（根もとが 軸：上がる px と たて横 同じ 倍率＝のばさない）＝ 0.1秒ごとの 点"""
    p = MW_ROWS[k]
    out, t = [], 0.0
    while t < WAVE_T + 1e-6:
        a = sea_amp(t)
        out.append((_pc(t), f'transform:translateY({f(-p["rise"] * a, 3)}px) scale({f(1 + (p["swell"] - 1) * a, 4)})'))
        t = round(t + step, 6)
    return out


def wave_life_css():
    """頭から 吹き飛ぶ しぶきと もや・落ちた 所で ふき上がる しぶき・小波の 列の ふくらみ と 小波 1つずつの 一生（もり上がる → 進む → こぼれる → 沈む）・
       小波の 頭の しぶき（白く なるのは どれも 0.3秒 以上 かけて）"""
    o0 = 'opacity:0'
    css = ''
    # 頭から うしろ（左）へ 吹き飛ぶ しぶき（点の 帯）と もや：波の 先を 投げ出す とき
    for nm, t0 in (('ukSp1', .78), ('ukSp2', 1.0)):
        css += _win(nm, [(0, f'{o0};transform:translate(0,0) scale(.5)'), (t0, f'{o0};transform:translate(0,0) scale(.5)'),
                         (t0 + .3, 'opacity:1;transform:translate(-5px,-2px) scale(.95)'), (t0 + .8, 'opacity:.75;transform:translate(-20px,-6px) scale(1.25)'),
                         (t0 + 1.3, f'{o0};transform:translate(-34px,-9px) scale(1.5)')])
    for nm, t0 in (('ukMs1', .85), ('ukMs2', 1.08)):
        css += _win(nm, [(0, f'{o0};transform:translate(0,0) scale(.8)'), (t0, f'{o0};transform:translate(0,0) scale(.8)'),
                         (t0 + .4, 'opacity:.85;transform:translate(-8px,-3px) scale(1.05)'), (t0 + 1.25, f'{o0};transform:translate(-42px,-9px) scale(1.35)')])
    # 波の 先が 落ちた 所で ふき上がる 潮しぶき（右から 左へ じゅんに）
    for k, (t0, x, sc) in enumerate(PEEL):
        css += _win(f'ukBu{k}', [(0, f'{o0};transform:translate(0,5px) scale({f(.3 * sc, 3)})'), (t0, f'{o0};transform:translate(0,5px) scale({f(.3 * sc, 3)})'),
                                 (t0 + .3, f'opacity:.95;transform:translate(-1px,0) scale({f(.8 * sc, 3)})'),
                                 (t0 + .45, f'opacity:.9;transform:translate(-3px,-3px) scale({f(.95 * sc, 3)})'),
                                 (t0 + .8, f'{o0};transform:translate(-7px,2px) scale({f(1.1 * sc, 3)})')])
    # 小波（第4.103版：小さな 大波）：列の ふくらみ（3秒・大波に 合わせて）と 右へ 進む（列の dx）。一生の コマと 頭の しぶきは mini_css（大波の シートが いる）
    for k, p in enumerate(MW_ROWS):
        css += kf(f'ukRwL{k}', row_stops(k))
        css += kf(f'ukNx{k}', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({f(p["dx"])}px)')])
    return css


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（白い背中、濃い藍に白いすじ、'
           'まるい爪のような白い泡の先、爪から落ちるしぶきの点。根もとと巻きの下は濃い藍のぼかし）。三秒ごとに、うしろへねた波が海の中から出てきて立ち上がり、'
           'いちばん高くなると止まらずに波の先が前へ投げ出されて爪が下へ巻きこみ、しぶきの点が前へとび、頭からしぶきともやがうしろへ吹き飛ぶ。'
           '波の先が落ちて白い水になり、大波は前へたおれて低くなりながら横長にのびて右へ走り、白い水の先で潮しぶきがつぎつぎにふき上がる。'
           '走る馬を追いこして、馬の右で水平になり、手前の小波のむこうへ消える。'
           '海には小波が二列にならぶ（大波がくずれはじめて横長になったところの、上の白い波と少しの青だけが見える。大波と同じ絵を小さくしたもの）。'
           'ひとつずつ海の中から上がってきて、白い波が前へたおれながら右へのび、また海の中へ沈み、海がずっと右へ動いて見える。大波が水平になるときに列がふくらむ。'
           '沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走る。'
           'ときどき街道のむこうから、ちょんまげに羽織と袴、刀を二本さしたお侍さんが一人か二人歩いてきて、馬とすれちがうときに会釈する。右上に朱の印のイラスト')
    foam = B.get('foam')                     # しぶき（make/ukiyoe_foam.py の 絵の シート）
    parts = foam['parts'] if foam else {}
    wave = B.get('wave')                     # 大波の 一生の コマ（小波も 同じ シートを 小さく 使う）

    def row(k):                              # 小波 1つずつ（くずれはじめた 大波の コマ）：外＝右へ 進む・ukNs＝倍率（たて横 同じ）・ukNu＝上がる／沈む・ukNv＝コマ
        if not (wave and wave.get('cells')):
            return ''
        o = f'<i class="ukRw ukR{k}">'
        for i, w in enumerate(MW_WAVES[k]):
            o += (f'<i class="ukNo ukQ{k}{i}"><i class="ukNs"><i class="ukNu"><i class="ukNv ukNw"></i>'
                  + (f'<i class="ukNp"><i class="ukPf ukF pf{i % 2}"></i></i>' if w.get('pf') and 'pf0' in parts else '') + '</i></i></i>')
        return o + '</i>'

    html = f'<div class="ukw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ukSky', sky_svg()) + img('ukKs', kasumi_svg()) + img('ukSea', sea_svg())
    html += row(0)                           # おくの 小波（大波と 舟の うしろ）
    html += img('ukBt', boat_svg())
    if wave and wave.get('cells'):           # 神奈川沖浪裏の 大波（make/ukiyoe_great.py の 波の 一生の コマ）
        html += '<i class="ukWv"></i>'
    if 'sp1' in parts:
        html += '<i class="ukSp s1 ukF sp1"></i><i class="ukSp s2 ukF sp2"></i>'
    html += img('ukMs m1', mist_svg()) + img('ukMs m2', mist_svg())
    if 'bs0' in parts:                       # 波の 先が 落ちた 所で ふき上がる しぶき（右から 左へ）
        html += ''.join(f'<i class="ukBu u{k} ukF bs{k % 2}"></i>' for k in range(len(PEEL)))
    html += row(1)                           # 手前の 小波（大波は この むこうへ 消える）
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
           # 小波の 列（外：大波に 合わせた ふくらみ・海の 線で 切る／ukNo：右へ 進む・ukNs：倍率・ukNv：大波の コマ）
           '.ukw .ukRw{left:0;width:390px;height:30px}'
           '.ukw .ukRw i{position:absolute;display:block}'
           '.ukw .ukRw .ukNs{left:0;top:0;width:420px;height:110px;transform-origin:0 0}'
           '.ukw .ukRw .ukNu{left:0;top:0;width:420px;height:110px}'
           '.ukw .ukRw .ukNv{left:0;top:0;width:0;height:0;animation-timing-function:step-end}'
           '.ukw .ukRw .ukNp{left:0;top:0;width:40px;height:26px}'
           '.ukw .ukRw .ukPf{left:0;top:0;width:40px;height:26px;opacity:0;transform-origin:33px 23px}'
           '.ukw .ukBu{width:90px;height:70px;opacity:0;transform-origin:45px 66px}'
           + ''.join(f'.ukw .ukBu.u{k}{{left:{f(x - 45)}px;top:42px;animation:ukBu{k} {f(WAVE_T)}s linear infinite}}' for k, (t0, x, sc) in enumerate(PEEL))
           + f'.ukw .ukPn{{left:0;top:{56 - PN_UP}px;width:{2 * TILE}px;height:{PN_H}px;background-size:{TILE}px {PN_H}px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * 1.12, 3)}s linear infinite}}'
           f'.ukw .ukRd{{left:0;top:116px;width:{2 * TILE}px;height:26px;background-size:{TILE}px 26px;background-repeat:repeat-x;animation:ukFlow {ROAD_S}s linear infinite}}'
           f'.ukw .ukBk{{left:0;top:136px;width:{2 * TILE}px;height:28px;background-size:{TILE}px 28px;background-repeat:repeat-x;animation:ukFlow {f(ROAD_S * .82, 3)}s linear infinite}}'
           '.ukw .ukSl{left:364px;top:6px;width:18px;height:18px}'
           f'.ukw .ukSm{{left:0;top:{f(SM_TOP)}px;width:{f(SM_W * SM_K)}px;height:{f(SM_H * SM_K)}px;overflow:hidden;transform:translateX(500px)}}'
           f'.ukw .ukSm>i{{position:absolute;display:block;left:0;top:0;height:{f(SM_H * SM_K)}px;background-repeat:no-repeat}}'
           f'.ukw .ukSm .w{{width:{f(12 * SM_W * SM_K)}px}}.ukw .ukSm .b{{width:{f(len(BOW) * SM_W * SM_K)}px;opacity:0}}')
    for k, p in enumerate(MW_ROWS):             # 列ごとの 箱（海の 線で 切る＝上の 白い 波と 少しの 青だけ 見える・根もとが 軸で ふくらむ・おくは かすむ）
        top = mw_row_top(k)
        css += (f'.ukw .ukRw.ukR{k}{{top:{f(top, 2)}px;height:{f(p["clip"] - top, 2)}px;overflow:hidden;'
                + (f'opacity:{f(p["haze"])};' if p['haze'] < 1 else '')
                + f'transform-origin:50% {f(p["clip"] - top, 2)}px;animation:ukRwL{k} {f(WAVE_T)}s linear infinite}}')
        for i, w in enumerate(MW_WAVES[k]):        # 小波 1つずつ：はじめの 場所（コマの 上の はしから MW_D の 所が 海の 線）・倍率・コマ・長さ・ずれ
            if not wave:
                break
            sc, P_ = w['s'], w['P']
            f0, f1 = MW_VARS[w['v']]
            dl = f(-w['ph'] * P_, 2)
            an = f'{f(P_)}s {dl}s infinite'
            css += (f'.ukw .ukRw.ukR{k} .ukQ{k}{i}{{left:{f(w["x"])}px;top:{f(p["clip"] - top - (mw_top(wave, f0) + MW_D) * sc, 2)}px;'
                    f'animation:ukNx{k} {f(P_)}s linear {dl}s infinite}}'
                    f'.ukw .ukRw.ukR{k} .ukQ{k}{i} .ukNs{{transform:scale({f(sc, 3)})}}'
                    f'.ukw .ukRw.ukR{k} .ukQ{k}{i} .ukNu{{animation:ukNu {an}}}'
                    f'.ukw .ukRw.ukR{k} .ukQ{k}{i} .ukNv{{animation:ukNf{w["v"]} {an};animation-timing-function:step-end}}')
            if w.get('pf') and foam:
                x_, y_, w_, h_, ox_, oy_ = wave['cells'][f0 - 1]
                tx_, ty_ = (ox_ + w_) / wave['z'] - 22, mw_top(wave, f0) + 12          # 白い 波の 右の 巻き（大波の 絵の px）
                css += (f'.ukw .ukRw.ukR{k} .ukQ{k}{i} .ukNp{{transform:translate({f(tx_ - 33 * MW_PUFF, 2)}px,{f(ty_ - 23 * MW_PUFF, 2)}px) scale({f(MW_PUFF)});'
                        f'transform-origin:0 0}}'
                        f'.ukw .ukRw.ukR{k} .ukQ{k}{i} .ukPf{{animation:ukNpA {f(P_)}s linear {dl}s infinite}}')
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
    if wave and wave.get('cells'):             # 大波：コマを step-end で 入れかえ（のばさない・ちぢめない）。小波（小さな 大波）も 同じ シート
        z = wave['z']
        sw_, sh_ = wave['sheet']
        css += (f'.ukw .ukWv{{left:{WB[0]}px;top:{WB[1]}px;width:0;height:0;opacity:0;'
                f'background:url({wave["url"]}) 0 0/{f(sw_ / z, 2)}px {f(sh_ / z, 2)}px no-repeat;animation:ukWv {f(WAVE_T)}s step-end infinite}}'
                f'.ukw .ukNw{{background:url({wave["url"]}) 0 0/{f(sw_ / z, 2)}px {f(sh_ / z, 2)}px no-repeat}}'
                + life_css(wave) + mini_css(wave))
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
    alt='浮世絵ふうの絵：和紙の地に藍のぼかしの空と赤い日、藍の山なみとかすみ。左に「神奈川沖浪裏」の形の大波（白い背中・濃い藍に白いすじ・まるい爪の泡：三秒ごとに海の中から出てきて立ち上がり、波の先を投げ出して潮しぶきを上げ、前へたおれながら横長にのびて右へ走り、走る馬を追いこして水平になって消える）。海には大波がくずれはじめて横長になったところの上の白い波（大波と同じ絵を小さくした小波）が二列にならび、ひとつずつ海の中から上がって右へのび、また沈んで、海がずっと動いて見える。沖に帆かけ舟。手前の海ぞいの街道（松並木・土の道・草の土手）を、朱の布と手綱の白い馬が右へ走り、ときどきお侍さんとすれちがう。右上に朱の印',
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
                   '3秒ごとに 海の 中から 出て きて 立ち上がり、波の 先を 投げ出して しぶきが とび、前へ たおれて 低く なりながら 横長に のびて 右へ 走り、白い 水の 先で 潮しぶき・'
                   '走る 馬を 追いこして 水平に なって 消える）・'
                   '小波 2列（大波が くずれはじめて 横長に なった 所の 上の 白い 波と 少しの 青＝大波と 同じ 絵を 小さく・1つずつ 海の 線から 上がって 右へ のび、'
                   'また 沈む＝海が 動いて 見える・大波が 水平に なる と 列が ふくらむ）・'
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
