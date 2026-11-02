"""神様極的中（gk）：神様的中の いちばん 上の 演出（第4.117版・まさちゃんの 指定 2026/11/01〜11/03）。
   まさちゃん（11/01 08:54）「神様極的中演出を作る 発動条件:買い目に超大穴と大穴が入っている。券種別も的中しているが、30レースの記録の中で2回以上で発生する」
   出る 条件（fx.js の show）：第4.118版（まさちゃんの 指定）から G（当たった 組に 超大穴＝10〜12番人気と、ほかに 7〜12番人気）かつ M（当たった 券種が 2つ以上）の レースが、
     結果を 決めた さいごの 50レース（その レースまで・中止と 締切済みは 入れない：src.html の godCount）の 中で 2回以上（その レースも 入れて）→ 神様極的中
     （超プレミアム神様的中より 先）。1回目は 超プレミアム神様的中（G・M）。第4.117版は「3連単で 神様の 条件・30レース・1回目は くじ」だった。
   PUSH（11/03 01:44・まさちゃん「金のpushボタンはいらない！今まで通りでいいよ！」）：超神様と 同じ 虹色の 超デカ PUSH（1.6倍）と その 音（fz_push）。
   押した あと：ノーマルど的中と 同じ 押した 画面（.ndt：押された PUSH が ポチッと へこむ・うすい 光の 輪・音 ndt）→ 動画（gk_film.mp4・はじめの 0.5秒は 真っ暗）→ ボード。
   動画（第13稿・11/03 01:40 に まさちゃんの OK）：まさちゃんが Meshy で 作った 3D（神様馬の 胸像・蹄の 脚・神様的中・神様極的中の 字・岩の かけら）と
     背景の 絵（光の 筋と 雲・光の 輪の 空）を 使って 1コマずつ 描いた（W/gf/film13.py ほか・W/glb の GLB の 描き方・W/horse_in/w の 顔の 3D）。
     入れる 物（3D・背景の 絵）は まさちゃんの もの で、リポジトリの 外（作業フォルダ）に ある。できた 動画（MASTER）から build_fx_films.py の gk_film() が
     アプリの 動画（CRF 23）と さいごの 1まいを 作る。点めつ（16.6）：flash_px.py AREA=.1 で 0個（いちばん 多い 窓で 7.9%）。
   動画の 流れ（0秒＝動画が 動きだした 瞬間＝押した 瞬間。30コマ/秒・780×1688・12.03秒）：
     0〜0.5 真っ暗 → 0.5〜1.25 神様馬の 顔が じわじわ（下を 向いて ゆっくり 動く）→ 1.25 両目が 同時に 金色に 光る →（顔を 上げる・目と たてがみに 金の 雷）
     → 3.75 目の 光が はじけて 大爆発（白・岩・小石・雷）→ 4.35 雲の 場（光の 筋・金粉・金紙）→ 4.58 神様的中が 上から ゆっくり →
     5.17／5.53／5.90／6.27 「神」「様」「的」「中」の 寄り → 6.63 引き → 7.33 着地（強調 0.5秒）→ 8.03 蹄の カットイン → 8.48 踏みつけて ひび（虹の 雷）
     → 8.56 画面と 神様的中が 砕ける・神様極的中が 出る → 8.84 ドーン → 最後の 場面（虹色の 極・金と 虹の 雷・光の 輪の 空）→ 12.0 ボード"""

W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 動画の 時刻（秒・第13稿）
FILM = dict(FPS=30, W=780, H=1688,
            DARK=0.5,                 # はじめの 真っ暗（押した 画面の 下）
            FACE=(0.5, 1.25),         # 顔が じわじわ
            IGNITE=1.25,              # 両目が 光る
            RAISE=(1.25, 3.65),       # 顔を 上げる（目と たてがみに 金の 雷）
            BLAST=3.75,               # 大爆発（白・岩・小石・雷）
            CLOUDS=4.35,              # 雲の 場
            FALL=4.58,                # 神様的中が 上から
            CU=(5.167, 5.533, 5.9, 6.267),   # 神・様・的・中 の 寄り（1つ 0.37秒）
            WIDE=6.633,               # 引き
            LAND=7.333,               # 着地 → 強調（0.5秒）
            HOOF=8.033,               # 蹄の カットイン
            HIT=8.483,                # 踏みつけて ひび
            SHAT=8.563,               # 砕ける・神様極的中が 出る
            DOON=8.843,               # ドーン
            END=12.033)
RES = 11.85                           # ボード（さいごの 場面 3秒の あと・動画の おわりと いっしょに）
GK_T = dict(FILM=(0.0, FILM['END']), BLAST=FILM['BLAST'], LAND=FILM['LAND'], HIT=FILM['HIT'], DOON=FILM['DOON'], RES=RES)
# 押した 画面（ノーマルど的中と 同じ 形：normal_do.TAP。動画の はじめの 真っ暗が 0.5秒 なので 早めに 消す）
TAP = dict(PRESS=.5, RING=(.03, .4), DARK=(.22, .5), END=.55)
# 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：さいごの 1まい → 押して 1秒後に 音の STILL_FROM 秒から → ボードの ポンッ（RES＋0.2秒）で ボードが ふわっと
STILL_WAIT = 1.0
STILL_FROM = round(RES - .1, 2)
STILL_BOARD = round(STILL_WAIT + (RES + .2 - STILL_FROM), 2)      # 1.3秒
STILL_T0 = round(STILL_WAIT + (RES + .45 - STILL_FROM), 2)        # 1.55秒（買い目の はじまり）
BOARD = round(RES + .15, 2)                                       # ボードが 出る（動画の とき）
# できた 動画（第13稿・CRF 20）。リポジトリの 外：GK_MASTER=<mp4> で ほかの 所も
MASTER = '/home/claude/work/pack/deliver_gk/神様極的中_第13稿.mp4'
CRF = 23                              # アプリの 動画（約10.3MB・第13稿と 見た目 同じ：SSIM 0.976）


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


SR = ('神様極的中！押した ボタンが 光って 暗く なり、暗闇から 王冠を つけた 白い 神様馬の 顔が 現れる。両目が 金色に 光って 顔を 上げ、目と たてがみに 金の 雷が 走り、'
      '目の 光が はじけて 大爆発。金の 雲の 上に 神様的中の 字が ゆっくり 降りて きて、一字ずつ 大きく 映る。着地すると 金の 蹄が 上から 踏みつけ、画面と 字が 砕けて、'
      'その 中から 虹色の 極の 字が 入った 神様極的中が ドーンと 現れる。金と 虹の 雷が まわりを 走る')


def gk_layers(board_html, last_url):
    """押したあと（下から）：（動画は fx.js が 舞台に 置く video.sgv）→ さいごの 1まい（still の 時）→ ボードの うしろを 少し 暗く → 押した 画面（.ndt：
       ノーマルど的中と 同じ。{{PZ}}・{{PC}}・{{PRESSED}}・{{BURST}} は fx.js が テーマで うめる）→ ボード（board_html）"""
    return f'''<img class="gks" src="{last_url}" alt="">
    <div class="gkk" aria-hidden="true"></div>
    <div class="ndt" aria-hidden="true"><div class="ndtb"></div><div class="pzw" style="--pz:{{{{PZ}}}}"><div class="pressed{{{{PC}}}}">{{{{PRESSED}}}}</div>{{{{BURST}}}}<i class="ndtr"></i></div></div>
    <div class="hb">{board_html}</div>
    <p class="sr">{SR}</p>'''


def gk_css():
    return f'''
/* ---------- 神様極的中（gk）：kami_kiwami.py（第4.117版：押した 画面 → 動画 gk_film.mp4（はじめの 0.5秒は 真っ暗）→ {sec(BOARD)} ボード） ---------- */
/* 押した 画面（.ndt）：ノーマルど的中と 同じ 形（押された PUSH が ポチッと へこんで 消える・うすい 光の 輪 → {sec(TAP['DARK'][0])}から 暗く → {sec(TAP['END'])}で 消える）。
   押した 瞬間から 動く（動画を 待たない）。キーフレームは ノーマルど的中（normal_do.nd_css）の もの */
.ov.fz.gk .ndt{{position:absolute;inset:0;z-index:20;pointer-events:none;animation:fxH .001s linear {sec(TAP['END'])} forwards}}
.ov.fz.gk .ndt .pressed{{animation:ndtP {sec(TAP['PRESS'])} cubic-bezier(.25,.7,.35,1) both,fxH .001s linear {sec(TAP['PRESS'])} forwards}}
.ov.fz.gk .ndt .ndtr{{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:226px;height:126px;margin:-63px 0 0 -113px;border-radius:38px;border:3px solid rgba(255,232,150,.9);
  box-shadow:0 0 10px rgba(255,220,120,.7);opacity:0;pointer-events:none;animation:ndtR {sec(TAP['RING'][1] - TAP['RING'][0])} ease-out {sec(TAP['RING'][0])} both}}
.ov.fz.gk .ndtb{{position:absolute;inset:0;background:radial-gradient(circle at 50% 45%,#2A1C06,#060400 70%);animation:ndtB {sec(TAP['DARK'][1] - TAP['DARK'][0])} ease-in {sec(TAP['DARK'][0])} both}}
/* 視差効果を減らす／控えめ（build_fx の scope が .fxs.calm にも 効かせる）：押した 画面は 出さない */
@media (prefers-reduced-motion:reduce){{
  .ov.fz.gk .ndt{{display:none}}
}}
/* 押してから 動画が 動きだす まで（読みこみ）は 黒。動きだしたら（go）幕は すきとおって 動画（video.sgv）が 見える */
.ov.fz.gk{{--t0:{sec(RES + .45)};--tc:.3s;z-index:31;background:#000}}
.ov.fz.gk.go{{background:transparent}}
.ov.fz.gk:not(.go):not(.still) *:not(.ndt):not(.ndt *){{animation-play-state:paused!important}}
.ov.fz.gk .gks{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:none}}
.ov.fz.gk.still .gks{{display:block}}
.ov.fz.gk .gkk{{position:absolute;inset:0;background:rgba(12,7,0,.55);opacity:0;pointer-events:none}}
.ov.fz.gk.go .gkk{{animation:fadeIn .5s ease-out {sec(BOARD - .05)} both}}
.ov.fz.gk .hb{{z-index:10;visibility:hidden}}
.ov.fz.gk.go .hb{{visibility:visible;animation:sdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(BOARD)} both}}
/* 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：さいごの 1まい → {sec(STILL_BOARD)} から ボードを ふわっと（音の ポンッと 同じ 時） */
.ov.fz.gk.still{{--t0:{sec(STILL_T0)}}}
.ov.fz.gk.still .gkk{{animation:fadeIn .5s ease-out {sec(STILL_BOARD - .15)} both}}
.ov.fz.gk.still .hb{{visibility:visible;animation:fadeIn .5s ease-out {sec(STILL_BOARD)} both!important}}
.ov.fz.gk.still .bh{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .3)} both,rbowText 1.2s linear {sec(STILL_BOARD + .3)} infinite}}
.ov.fz.gk.still .zrib{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .4)} both}}
'''
