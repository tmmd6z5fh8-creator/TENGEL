"""ノーマルど的中（nd）：ど的中の 新しい ふつうの 演出（第4.77版・まさちゃんの 指定）。
   まさちゃん「ノーマルのど的中演出も作りたい！ pushボタンをタップしたら暗闇から、一枚目の画像の玉が現れて、玉の中心から馬が二枚目の線に合わせて
   走り出して一周半したら玉が弾けて、玉の光に包まれて、ど！的中が現れるようにしてみて！ リアルな画質で作成して！」
   「ノーマルど的中演出はタップしてプチュンは、いらないよ！ タップしたら画面が1秒暗くなり、今作ってる演出に入って！」
   「馬の動き方、この動画を参考にして！」「馬の形もジョッキー乗せた状態で、この動画の馬を参考に作成して！」「馬の色はシルバーにして！ あと尻尾もリアルにね！」
   「ノーマル的中演出、最後は芝の上に、上から、ど！的中、の文字が落ちてくる演出にして！ 背景は、一枚目の画像の玉(かなり大きい)の前にど！的中の文字が
   落ちてきて、芝や地面、周りの明るさ、雰囲気は一枚目の画像の玉の映像の雰囲気で作成して！ 最後のど！的中の文字は背景や地面、芝に負けない立体的で
   リアルに作成して！ あと、常に不定期に輝きを放っているようにして！」
   送ってくれた 画像・動画は 色と 雰囲気・動きの 見本に するだけ。絵・形は 一から 作る（なぞらない）。
   動画（flat/normal_film.py・馬の 走りは flat/nd_horse.py・「ど！的中」は flat/shiden_logo.py の 3D）・音（gen_sfx.py の sfx_nd）は 一から 作る。
   押した あと（0秒＝押した 瞬間・動画が 動きだした 瞬間）：
     P 真っ暗 1秒（プチュンは なし）
     A 光の 玉（1.0秒〜）：暗闇に 光の 点 → 若草色の 光の 玉（芝から 1.2m 浮く）・金の 輪 3つ・光の 筋・光の 粒・玉の 光で 芝が 見える
     B 馬（2.0〜5.2秒）：玉の まん中から シルバーの 競走馬と 騎手が とびおりて、芝の うずまき（画面で 右まわり・1周半・さいごは 上を 右へ）を ギャロップ
     C 光る（5.0〜5.65秒）：玉が ふくらんで 強く 光り → 光に つつまれる → 低い 目線の 場面（芝の 上・うしろに 大きな 光の 玉と 金の 輪）
     D ど！的中（5.8秒〜）：上から 落ちて 芝に ドーン（6.2秒：芝と 土が はねる・光の 輪・ゆれ）→ いつも 不定期に キラッ・光の 筋 → 7.6秒 ボード
   点めつ：どの 1点も 1秒に 3回 以下（test_fx_flash.py nd・film で 確かめる）"""

W_, H_ = 390.0, 844.0

# ---------------------------------------------------------------- 動画（flat/normal_film.py が 描く）の 時刻（秒）
FILM = dict(FPS=30, W=780, H=1688,                # 30コマ/秒・画面 390×844 の 2倍
            BLACK=1.0,                            # はじめの 真っ暗 1秒（プチュンは なし：まさちゃんの 指定）
            ORB_IN=(1.0, 1.9),                    # 光の 点 → 光の 玉
            RINGS=(1.3, 2.1),                     # 金の 輪が ひろがる
            RUN=(2.0, 5.2),                       # 馬：玉の まん中から とびおりて 芝の うずまきを 1周半
            TURNS=1.5,
            SWELL=(4.95, 5.3),                    # 玉が ふくらんで 強く 光る
            BURST=5.3,                            # 光が はじける
            WHITE=(5.3, 5.65),                    # 画面が 光に つつまれる → 低い 目線の 場面（芝・大きな 玉）
            SHOT2=5.45,                           # 低い 目線の 場面（光の 中から）
            LOGO=(5.8, 6.2),                      # ど！的中 が 上から 落ちて 芝に ドーン（6.2秒）
            HOT=(6.15, 6.75),                     # 白熱 → 金と 虹
            SWEEP=(6.95, 7.4),                    # 光の 筋が 字を 走る（キラーン）
            SWEEP2=(7.75, 8.1),
            GLINT=6.3,                            # ここから ずっと 不定期に キラッ
            RES=7.6,                              # ボード
            END=8.2)


def _glints():
    """不定期な キラッ（時刻）：0.12〜0.42秒ごと（まさちゃん「常に不定期に輝きを放っているようにして！」）"""
    import random
    r = random.Random(4077)
    out, t = [], FILM['GLINT']
    while t < FILM['END'] - .05:
        out.append(round(t, 3))
        t += r.uniform(.12, .42)
    return tuple(out)


GLINT_T = _glints()
ND_T = dict(FILM=(0.0, FILM['END']), ORB=FILM['ORB_IN'][0], RUN=FILM['RUN'], BURST=FILM['BURST'], LOGO=FILM['LOGO'][0], LAND=FILM['LOGO'][1],
            SWEEP=FILM['SWEEP'][0], RES=FILM['RES'])
# 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：動画の さいごの 1まい → 押して 1秒後に 音の STILL_FROM 秒から → ボードの ポンッ（音の RES＋0.2秒）で ボードが ふわっと
STILL_WAIT = 1.0
STILL_FROM = round(ND_T['RES'] - .1, 2)
STILL_BOARD = round(STILL_WAIT + (ND_T['RES'] + .2 - STILL_FROM), 2)      # 1.3秒
STILL_T0 = round(STILL_WAIT + (ND_T['RES'] + .45 - STILL_FROM), 2)        # 1.55秒（買い目の はじまり）
BOARD = round(ND_T['RES'] + .15, 2)                                       # ボードが 出る（動画の とき）


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


SR = ('ど的中！画面が 暗く なり、暗闇から 金の 輪を まとった 光の 玉が 現れる。玉の まん中から 騎手を 乗せた 銀色の 馬が とびだして 芝の 上で うずまきを 描いて 走り、'
      '玉が 強く 光る。大きな 光の 玉の 前の 芝の 上に、金と 虹の 立体の「ど！的中」が 上から 落ちて きて、キラキラと 輝く')


def nd_layers(board_html, last_url):
    """押したあと（下から）：（動画は fx.js が 舞台に 置く video.sgv）→ さいごの 1まい（still の 時）→ ボードの うしろを 少し 暗く → ボード（board_html）。
       プチュンは なし（押すと 1秒 真っ暗 → 動画）"""
    return f'''<img class="nds" src="{last_url}" alt="">
    <div class="ndk" aria-hidden="true"></div>
    <div class="hb">{board_html}</div>
    <p class="sr">{SR}</p>'''


def nd_css():
    T = ND_T
    return f'''
/* ---------- ノーマルど的中（nd）：normal_do.py（第4.77版：押すと 1秒 真っ暗 → 動画 nd_film.mp4＝flat/normal_film.py・ど！的中は flat/shiden_logo.py の 3D・プチュンは なし） ---------- */
/* 押してから 動画が 動きだす まで（読みこみ）は 黒。動きだしたら（go）幕は すきとおって 動画（video.sgv）が 見える → {sec(BOARD)} ボード */
.ov.fz.nd{{--t0:{sec(T['RES'] + .45)};--tc:.3s;z-index:31;background:#000}}
.ov.fz.nd.go{{background:transparent}}
.ov.fz.nd:not(.go):not(.still) *{{animation-play-state:paused!important}}
.ov.fz.nd .nds{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:none}}
.ov.fz.nd.still .nds{{display:block}}
.ov.fz.nd .ndk{{position:absolute;inset:0;background:rgba(2,8,3,.55);opacity:0;pointer-events:none}}
.ov.fz.nd.go .ndk{{animation:fadeIn .5s ease-out {sec(BOARD - .05)} both}}
.ov.fz.nd .hb{{z-index:10;visibility:hidden}}
.ov.fz.nd.go .hb{{visibility:visible;animation:sdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(BOARD)} both}}
/* 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：動画の さいごの 1まい → {sec(STILL_BOARD)} から ボードを ふわっと（音の ポンッと 同じ 時） */
.ov.fz.nd.still{{--t0:{sec(STILL_T0)}}}
.ov.fz.nd.still .ndk{{animation:fadeIn .5s ease-out {sec(STILL_BOARD - .15)} both}}
.ov.fz.nd.still .hb{{visibility:visible;animation:fadeIn .5s ease-out {sec(STILL_BOARD)} both!important}}
.ov.fz.nd.still .bh{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .3)} both,rbowText 1.2s linear {sec(STILL_BOARD + .3)} infinite}}
.ov.fz.nd.still .zrib{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .4)} both}}
'''
