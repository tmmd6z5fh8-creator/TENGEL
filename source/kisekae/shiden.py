"""ど的中・紫電（しでん・sd）：ど的中の 新しい 演出（第4.66版・まさちゃんの 指定）。
   まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出 圧倒的な迫力 見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   送ってくれた 動画（パチンコの 当たりの 演出）は 流れ・色・迫力の 見本に するだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
   馬は テンゲルの 馬（r3d の 3Dの 馬）。動画（flat/shiden_film.py・flat/shiden_logo.py）・音（gen_sfx.py の sfx_sd・sfx_sdp）は 一から 作る。
   第4.67版〜第4.69版：② を 送ってくれた GIF・動画の コマに 合わせて 作った。第4.70版：② を 1コマずつ 3D で 描いた 動画に（リアルな 馬の 顔 → 蹄の カットイン → 光の 玉）・
   ③ ど！！！的中は CSS と SVG。
   第4.71版・まさちゃん「一枚目のこのシーン消して、二枚目の蹄カットインか入って画面が光に包まれて、すぐに、ど！！！的中が出てくるようにして！
   三枚目のど！！！の、！！！のビックリマークがデカすぎて、バランス悪いから！！！の上から下にかけて小さくする、はそのままでサイズとか、配置考えて青四角×の幅が開かないようにして！
   あと、ど！！！的中も馬とか蹄カットインと同じリアルで立体的に作成して！」
   「ど！的中演出のプチュン演出をボタンタップした瞬間に入るようにして！ プチュンして0.8秒で、一枚目の馬の顔が暗闇から目だけを光らせて、徐々に顔がみえる、
   暗闇から目が光り顔が全部見えて(今の馬の顔の演出と繋げて)、蹄カットインに入るまでを2秒くらいにして！ 二枚目の蹄カットインの入りの映像を1.3秒にして、
   奥の光りから、的中(縦文字で)が画面近くまで飛んできて、0.8秒停止、すぐに蹄カットインで的中の文字を的と中の真ん中から切り裂いて、
   画面が光りに包まれてど！！！的中が出てくる。ど！！！的中表示2.5秒にして！」
   → 光の 玉の 場面は やめた。ど！！！的中も 動画の 中で 3D に（flat/shiden_logo.py：sdfr で 字を 厚みと 面取りの ある 金属の 形に して、映り込み・白熱・雷の 光まで 計算）。
     「！」は「ど」の 右に 上から 下へ 小さく・3つで「ど」の 高さに おさめて「的中」を「ど」の すぐ 下に（あきを 作らない）。
     押した 瞬間に ど的中と 同じ プチュン（gen_fx.py の フリーズ：CSS・音は sfx_sdp）。動画（sd_film.mp4・30コマ/秒・音なし・10.5秒）も 押した 瞬間に 再生し、
     はじめの 1.8秒は 黒（プチュンの 下）。しくみは 超神様的中と 同じ（fx.js：動きだした 時を 0秒に して 音（sfx_sd）と ボードの 時計を そろえる（go）。
     動かない・読めない・視差効果を減らす／控えめ → プチュンは 出さず 動画の さいごの 1まい（sd_last.webp）→ 1.3秒 ボード（still））
   押した あと（0秒＝押した 瞬間・動画が 動きだした 瞬間）：
     P プチュン（0〜約1.0秒：CSS）→ 真っ暗 0.8秒
     A 馬の 顔（1.8〜3.8秒）：暗闇に 目だけが 光る → だんだん 青むらさきの 光で 黒い 馬の 横顔が 見えて くる → 頭が 上がって こちらを 向き・耳が 立ち・
       鼻から 白い 息・たてがみが 風に なびく → 目の 火が 強く なって あふれる → カメラが 目へ 寄って 目の 光が 画面を つつむ
     B 蹄の カットイン（3.8〜7.4秒）：むらさきの 雷雲の トンネルを 前へ 突き進む・奥の 光から 縦書きの 3D の「的中」が 画面の 近くまで とんでくる（〜5.1秒）
       → 0.8秒 止まる → 焼けた 蹄鉄の 蹄が 左から「的」と「中」の あいだを 切り裂いて 右へ（まん中で スローモーション）→ 切り口が 光って 開き 画面が 光に つつまれる
     D ど！！！的中（7.4秒〜）：光の 中から すぐに 白熱の 3D の ロゴが 手前へ とんでくる → 7.9秒 ドンッ（金の かけら・衝撃の 輪・ゆれ）→ 金と 虹に 冷める
       → ロゴ 全体に 雷を まとう（ずっと ジリジリ・雷の 光が 金属に 映る）・不定期に 大きな 雷が 画面の 全方位へ・光の 筋が 字を 走る → 2.5秒 見せて 9.9秒 ボード
   点めつ：どの 1点も 1秒に 3回 以下（test_fx_flash.py sd・film で 確かめる）"""

W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 動画（flat/shiden_film.py が 描く）の 時刻（秒）
FILM = dict(FPS=30, W=780, H=1688,                # 30コマ/秒・画面 390×844 の 2倍
            BLACK=1.8,                            # はじめの 黒（押した 瞬間の プチュン（CSS：約1.0秒）＋ 真っ暗 0.8秒）
            FACE=3.8, HOOF=7.4, END=10.5,         # 場面の おわり：A 馬の 顔（BLACK から）・B 蹄の カットイン・D ど！！！的中（＝動画の 長さ）
            # A（場面の 中の 秒・BLACK から）：目だけ 光る・顔が 見えて くる・鼻から 白い 息・目の 火が 強く なって あふれる・目へ 寄って 光に つつまれる
            EYE_ON=.12, LIT=(.2, 1.0), PUFFS=(.62, 1.22), EYE=(1.0, 1.5), RUSH=1.5,
            # B（場面の 中の 秒・FACE から）：的中が とんでくる（出る・止まる）・雷・蹄（第4.70版と 同じ 動きを H_SHIFT コマ おそく）・切り口が 開く・光へ 寄る・光に つつまれる
            T_FLY=(.1, 1.3), H_BOLTS=(.45, 1.72), H_SHIFT=54,
            H_IN=2.08, H_SLOW=(2.35, 2.75), H_OUT=2.98, H_OPEN=2.96, H_ZOOM=3.1, H_WASH=3.28,
            # D（場面の 中の 秒・HOOF から）：ロゴが 光の 中から 出る・止まる（ドンッ）・白熱が 冷める・白い 光が ひく・まとう 電気・大きな 雷（LAND からの 秒・本数）・光の 筋・ボード
            L_IN=.04, L_LAND=.5, L_HOT=(.3, .95), L_WASH=(.02, .42), L_ARCS=.42,
            L_BOLTS=((0.0, 2), (.3, 1), (.4, 2), (.82, 1), (.94, 1), (1.3, 2), (1.62, 1), (1.74, 2), (2.1, 1), (2.28, 1)),
            L_SWEEP=((.8, 1.4), (1.85, 2.4)), L_RES=2.5)

# ---------------------------------------------------------------- 時刻（秒・動画が 動きだした 瞬間が 0）
_A, _B, _H = FILM['BLACK'], FILM['FACE'], FILM['HOOF']
SD_T = dict(FILM=(0.0, FILM['END']),                                   # 動画
            EYE=round(_A, 2),                                          # 暗闇に 目が 光る
            FLY=(round(_B + FILM['T_FLY'][0], 2), round(_B + FILM['T_FLY'][1], 2)),   # 縦書きの 的中が とんでくる・止まる
            CUT=round(_B + FILM['H_IN'], 2),                           # 蹄が 的中を 切り裂く
            LOGO=round(_H + FILM['L_IN'], 2),                          # ど！！！的中が 光の 中から 出る
            LAND=round(_H + FILM['L_LAND'], 2),                        # 止まる（ドンッ）
            ARCS=(round(_H + FILM['L_ARCS'], 2), FILM['END']),         # ロゴに まとう 電気
            BOLTS=tuple((round(_H + FILM['L_LAND'] + t, 2), n) for t, n in FILM['L_BOLTS']),   # 大きな 雷（時刻・本数）
            RES=round(_H + FILM['L_RES'], 2))                          # ボード
# 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：動画の さいごの 1まい → 押して 1秒後に 音の STILL_FROM 秒から → ボードの ポンッ（音の RES＋0.2秒）で ボードが ふわっと
STILL_WAIT = 1.0
STILL_FROM = round(SD_T['RES'] - .1, 2)
STILL_BOARD = round(STILL_WAIT + (SD_T['RES'] + .2 - STILL_FROM), 2)      # 1.3秒
STILL_T0 = round(STILL_WAIT + (SD_T['RES'] + .45 - STILL_FROM), 2)        # 1.55秒（買い目の はじまり）
BOARD = round(SD_T['RES'] + .15, 2)                                       # ボードが 出る（動画の とき）


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


# ---------------------------------------------------------------- 層
SR = ('ど的中！プチュンと 画面が 消えて、暗闇に 黒い 馬の 目だけが 光り、だんだん 顔が 見えて くる。雷雲の 奥の 光から 縦書きの「的中」が とんできて 止まり、'
      '焼けた 蹄鉄の 蹄が「的」と「中」の あいだを 切り裂いて 画面が 光に つつまれる。その 光の 中から 金と 虹の 立体の「ど！！！的中」が とびだし、雷を まとう')


def sd_layers(board_html, last_url, puchun=''):
    """押したあと（下から）：（動画は fx.js が 舞台に 置く video.sgv）→ さいごの 1まい（still の 時）→ ボードの うしろを 少し 暗く → ボード（board_html）
       → 押した 瞬間の プチュン（puchun＝gen_fx.py の FZ_HTML：ど的中と 同じ。動画を 待たずに すぐ 動く）"""
    return f'''<img class="sds" src="{last_url}" alt="">
    <div class="sdk" aria-hidden="true"></div>
    <div class="hb">{board_html}</div>
    {puchun}
    <p class="sr">{SR}</p>'''


def sd_css():
    T = SD_T
    return f'''
/* ---------- ど的中・紫電（sd）：shiden.py（第4.71版：押した 瞬間に プチュン（ど的中と 同じ .pc）→ 動画 sd_film.mp4＝flat/shiden_film.py・ど！！！的中は flat/shiden_logo.py の 3D） ---------- */
/* 押してから 動画が 動きだす まで（読みこみ）は 黒。動きだしたら（go）幕は すきとおって 動画（video.sgv）が 見える → {sec(BOARD)} ボード。
   プチュン（.pc）だけは 動画を 待たずに 押した 瞬間から 動く */
.ov.fz.sd{{--t0:{sec(T['RES'] + .45)};--tc:.3s;z-index:31;background:#000}}
.ov.fz.sd.go{{background:transparent}}
.ov.fz.sd:not(.go):not(.still) *:not(.pc):not(.pc *){{animation-play-state:paused!important}}
.ov.fz.sd .sds{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:none}}
.ov.fz.sd.still .sds{{display:block}}
.ov.fz.sd.still .pc{{display:none}}
.ov.fz.sd .sdk{{position:absolute;inset:0;background:rgba(6,2,12,.55);opacity:0;pointer-events:none}}
.ov.fz.sd.go .sdk{{animation:fadeIn .5s ease-out {sec(BOARD - .05)} both}}
.ov.fz.sd .hb{{z-index:10;visibility:hidden}}
.ov.fz.sd.go .hb{{visibility:visible;animation:sdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(BOARD)} both}}
@keyframes sdBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
/* 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：プチュンは 出さず 動画の さいごの 1まい → {sec(STILL_BOARD)} から ボードを ふわっと（音の ポンッと 同じ 時）。
   ど的中の ボードの 見出し（.fz .bh）・帯（.zrib）は ど的中の 時刻を 待たず ボードと いっしょに（{sec(STILL_BOARD + .3)}・{sec(STILL_BOARD + .4)}） */
.ov.fz.sd.still{{--t0:{sec(STILL_T0)}}}
.ov.fz.sd.still .sdk{{animation:fadeIn .5s ease-out {sec(STILL_BOARD - .15)} both}}
.ov.fz.sd.still .hb{{visibility:visible;animation:fadeIn .5s ease-out {sec(STILL_BOARD)} both!important}}
.ov.fz.sd.still .bh{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .3)} both,rbowText 1.2s linear {sec(STILL_BOARD + .3)} infinite}}
.ov.fz.sd.still .zrib{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .4)} both}}
'''
