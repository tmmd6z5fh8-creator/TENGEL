"""ど的中・紫電（しでん・sd）：ど的中の 新しい 演出（第4.66版・まさちゃんの 指定）。
   まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出 圧倒的な迫力 見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   送ってくれた 動画（パチンコの 当たりの 演出）は 流れ・色・迫力の 見本に するだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
   人物の 代わりは テンゲルの 馬（後ろ足で 立ち上がる 黒い 馬の 影）。絵（flat/shiden_art.py）・音（gen_sfx.py の sfx_sd）は 一から 作る。
   第4.67版・まさちゃん「一枚目から二枚目までのシーンを無くして、…三枚目から四枚目までの画像を確認して、フレーム数を増やしていいから画面を切り裂いて、虹色、白、青、黒が入れ替わり入って激しく
   最後の光が弾けて、ど！！！的中が画面から出てくるように作成して！ ど！！！的中は、もっと全体的に雷を纏って激しく、不定期にど！！！的中にまとった雷が画面の全方位にビリビリと届く演出も入れて」
   → ②の「金の 光の 筋の ため」と「砕けて ロゴが 落ちて くる」を やめて、②を「切り裂き」に・ロゴは 光が 弾けた あとに 画面から 出てくる・雷を まとう
   第4.68版・まさちゃん「え？ファイルのこの、画像からこの画像まで確認して！は確認してないってこと？ もう一度送る！」（送ってくれた GIF：21コマ・4.28秒）
   → ②を 送ってくれた GIF の 1コマずつに 合わせて 作り直した（第4.67版の 帯の 切り裂きは やめた）。GIF の 絵・人物・機械・字は 使わない・なぞらない。
   第4.69版・まさちゃん「もう一度動画みて作り直して！ 二枚目の写真は左から右に切り裂くんだよ！ 三枚目の馬の顔は動きをつけて長めにして！ リアルに！」
   「8秒くらいあっていいからね！」「馬の尻尾直して！」「画面を切るのをコーンじゃなくて馬の蹄にして！」「このシーンの青丸の模様と馬いらない！」
   「炎のようなエフェクトは、蹄が、左から右に進むと同時に、切れて言って、元にした画像ファイルのカットシーンみたいにして！」「蹄こっちの角度の方がいい！」
   → 動画を コマ送りで 見て、GIF に なかった コマを 足し、② を 約8.6秒に。顔は リアルな 3D（12コマ）・世界を 切り裂くのは 馬の 蹄（通った あとの 炎は 黒い
     ギザギザの 裂け目で 切れていく＝見本の 画像 027）・鏡の 世界の 宇宙の 窓と 金属の 馬は やめた・① の 馬に ふさふさの しっぽ。
   押した あと（0秒＝押した 瞬間）：
     ① 紫の 炎（0〜1.5秒）：紫の 夜に 金の 水晶の かけら → 黒い 馬の 影（しっぽは 左下へ ふさふさ）が ぐっと 寄って 立ち上がる → 十字の 光が 2回 → 目が 赤く 光って 炎が 紫から 赤へ
        → 炎の 中を「的中」の 字が ただよう
     ② 動画の コマ（1.5〜10.1秒）：
        1.5 白黒の 煙・虹色の 光の 筋 → 1.8 明るい 炎と 桃色 → 2.05 暗い 画面・まっ黒な 馬・赤い 目・青緑の 雷 → 2.25 横に ずれる バグ → 2.5 炎に 桃色の 雷
        → 2.8 暗い 画面と 青緑の 雷 → 2.95 大きな 桃色の 雷 → 3.15 白黒の ネガ（まん中で 水色に 反転）
        → 3.45〜5.05 リアルな 馬の 顔の ドアップ（12コマ：はじめは 青く・頭が 上がって こちらを 向く・耳が 立つ・目へ 寄る・目が 赤く 光る・おわりに 黒い 切り裂きが 左から 右へ）
        → 5.05 色ずれの 割れた 白黒 → 5.25 白と 桃色の ひび → 5.45 赤黒い うず → 5.65 だいだいの 爆発 → 5.85 赤黒い うず → 6.0 緑と 黒の うず
        → 6.2〜9.0 割れた 鏡の かけらの 世界（寄って いく。6.3〜7.05 焼けた 蹄鉄の 馬の 蹄が 足ごと 左から 右へ 走り（まん中で ゆっくり）、通った あとの 炎が
          黒い ギザギザの 裂け目で 切れていく → 7.05〜7.55 裂け目が 少し 開いて 消える。7.4 炎が 光の 右で 1つに。8.85 青く 反転）
        → 9.0 白と 水色 → 9.15 黒と 赤 → 9.3 白と 青 → 9.4 黒い 穴 → 9.52 金の 小さな 光 → 9.72〜10.1 暗い 緑に 金の 輪と 横の 光（9.0〜 左右に 炎の 柱）
     ③ ど！！！的中（10.1秒〜）：光が 弾けて、その 中から「ど」「！」×3（上から 下へ 小さく）「的中」が 白熱の まま 画面から 出てきて 金と 虹に 冷める（10.66秒）
        → ロゴ 全体に 雷を まとう（ずっと ジリジリ）・不定期に 大きな 雷が 画面の 全方位へ → 12.88秒 ボード
   絵（ios/fx_assets の sd_….webp・id は shiden_blobs.json・大きさは shiden_layers.json）：① と ロゴは flat/shiden_art.py、② は flat/shiden_cuts.py
   （顔は flat/shiden_face.py・蹄は flat/shiden_hoof.py）。ほかは CSS と SVG
   点めつ：② の コマの 切りかえは 0.12秒 以上。どの 1点も 1秒に 3回 以下（test_fx_flash.py sd で 確かめる）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/shiden_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0
CX = 195.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
SD_T = dict(A=(0.0, 1.55),                      # ① 紫の 炎（② の はじめの コマで おおわれる まで）
            HORSE=(0.0, .38),                   # 馬の 影が 寄って 止まる
            CROSS=(.72, .98),                   # 十字の 光 2回（目・画面の まん中）
            EYES=1.18,                          # 目が 赤く 光る → 炎が 赤へ（EYES〜EYES+.6 で 入れかわる）
            GLY=(1.05, 2.1),                    # 「的中」の 字が ただよう（出はじめ・おわり）
            # ② 見本の 動画（1.50〜5.03秒）の コマ（第4.69版：コマ送りで 見て 足した コマ・まさちゃん「8秒くらいあっていいからね！」で 約8.6秒に）
            C0=(1.5, 1.8),                      # 動画 1.50：白黒の 煙・虹色の 光の 筋
            F1=(1.8, 2.05),                     # 動画 1.57：明るい 炎と 桃色
            DK1=(2.05, 2.25),                   # 動画 1.70：暗い 画面・まっ黒な 馬・赤い 目・青緑の 雷
            C1=(2.25, 2.5),                     # 動画 1.73：横に ずれる バグ
            LT=(2.5, 2.8),                      # 動画 1.90：炎に 桃色の 雷
            DK2=(2.8, 2.95),                    # 動画 1.93：暗い 画面と 青緑の 雷（2回め）
            LT2=(2.95, 3.15),                   # 動画 1.97：大きな 桃色の 雷
            BW=(3.15, 3.45), BWC=(3.27, 3.33),  # 動画 2.03〜2.10：白黒の ネガ（まん中で 水色に 反転）
            FACE=(3.45, 5.05),                  # 動画 2.13〜2.25：馬の 顔の ドアップ（まさちゃん「動きをつけて長めにして！リアルに！」：12コマ）
            FBLUE=(3.45, 3.57),                 # 顔の はじめは 青く（動画 2.13 の 青い コマ）
            FSL=(4.85, 4.95, 5.05),             # 黒い 切り裂きが 左から 右へ 走る（走る・おわり・つぎの コマ）
            CHR=(5.05, 5.25),                   # 動画 2.27：色ずれの 割れた 白黒
            CRK=(5.25, 5.45),                   # 動画 2.33：白と 桃色・黒い 裂け目と ひび
            C5=(5.45, 5.65),                    # 動画 2.37：赤黒い うず・白い 裂け目
            BOOM=(5.65, 5.85),                  # 動画 2.40：だいだいの 爆発・黒い 裂け目
            C5B=(5.85, 6.0),                    # 動画 2.43：赤黒い うず（2回め）
            C6=(6.0, 6.2),                      # 動画 2.47：緑と 黒の うず・黒い 裂け目
            W=(6.2, 9.0),                       # 動画 2.50〜4.68：割れた 鏡の かけらの 世界（寄って いく）
            HOOF=(6.3, 7.05),                   # 馬の 蹄が 左から 右へ 画面を 切り裂く（まさちゃん「左から右に切り裂くんだよ！」「コーンじゃなくて馬の蹄にして！」）：速く 入る → まん中で ゆっくり → 速く 抜ける
            CUT=(6.3, 7.55),                    # 切り口の 光（蹄と いっしょに のびる → 光って 消える）
            FIRE3=(7.4, 7.85),                  # 炎が 光の 右で 1つに なる 形へ（動画 3.6〜）
            WN=(8.85, 9.0),                     # 動画 4.65：世界が 青く 反転
            C16=(9.0, 9.15), C16R=(9.15, 9.3), C16B=(9.3, 9.4),   # 動画 4.72・4.75・4.78：白と 水色・黒と 赤・白と 青
            C17=(9.4, 9.52), C18=(9.52, 9.72),  # 動画 4.82・4.85〜4.97
            C19=(9.72, 10.1),                   # 動画 4.98〜5.00：暗い 緑・金の 輪・横の 光
            GF=(10.1, 10.18, 10.6, 10.93),      # 光が 弾ける（金色の 光：出る・いちばん・ロゴが 出きる まで そのまま・消える）＝ 動画 5.02
            C=10.1,                             # ③ の はじまり
            LOGO=10.22, EMERGE=.44,             # ど！！！的中が 光の 中から 出てくる（はじまり・かかる 時間）
            LAND=10.66,                         # 出きった 瞬間（ドンッ：揺れ・金の 粒）
            ARCS=(10.58, 13.28),                # ロゴに まとう 電気（ずっと）
            BOLTS=((10.66, 2), (10.96, 1), (11.06, 2), (11.48, 1), (11.6, 1), (11.96, 2), (12.28, 1), (12.4, 2), (12.76, 1), (13.08, 1)),   # 大きな 雷（時刻・本数）：不定期
            RES=12.88)                          # ボード
AR_DT = .085                                    # まとう 電気の 1コマ
# ロゴの 置き場所（まん中の x・y・絵の 表示の 幅）：絵は 字の まわりに 光の あきが ある（shiden_art.py の pad）ので、字より 大きい
LOGO = dict(sd_t_do=(150.0, 232.0, 400.0), e1=(305.0, 212.0, 278.0), e2=(323.0, 336.0, 196.0), e3=(336.0, 420.0, 130.0), sd_t_hit=(CX, 586.0, 474.0))
HORSE_K = 1.1                                   # ① の 馬：絵の 1.1倍
HORSE_EYE = (274.4, 322.6)                      # ① の 馬の 目の 場所（第4.69版：しっぽを 足して 絵が 左に 広がっても 体の 場所は 第4.68版と 同じ）


def horse_a(lay=None):
    """① の 馬：left・top・幅（絵の 目の 位置から）"""
    L = lay or LAY['sd_horse']
    ex, ey = L['eye']
    return (round(HORSE_EYE[0] - ex * HORSE_K, 1), round(HORSE_EYE[1] - ey * HORSE_K, 1), round(L['w'] * HORSE_K, 1))


HORSE_A = horse_a()                             # ① の 馬：left・top・幅
HIT_C = (CX, 586.0)                             # 「的中」の まん中（金の 粒・金の 光・雷の もと）


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def hide(t0=None, t1=None):
    """見えない 間は 描かない（出る 前・消えた あと）：animation に 足す 文（先頭に ,）
       第4.69版：消える のは t1 の 0.003秒 あと（つぎの コマが 出きる まで 前の コマを のこす：コマの さかいめで 1コマ まっ黒に ならない ように）"""
    o = ''
    if t0 is not None:
        o += f',sdH .001s linear {sec(t0)} backwards'
    if t1 is not None:
        o += f',sdH .001s linear {sec(t1 + .003)} forwards'
    return o


def blob(name):
    ids = json.load(open(os.environ.get('SHIDEN_BLOBS', f'{K}/shiden_blobs.json'), encoding='utf-8'))
    return f'/_blob/{ids[name]}'


def _img(name, x, y, w, h=None, cls='', style=''):
    if h is None:
        h = w * LAY[name]['h'] / LAY[name]['w']
    return f'<img class="{cls}" src="{blob(name)}" alt="" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;{style}">'


def _img_c(name, cx, cy, w, cls='', style=''):
    """まん中の 位置で 置く"""
    h = w * LAY[name]['h'] / LAY[name]['w']
    return _img(name, cx - w / 2, cy - h / 2, w, h, cls, style)


def eye_pos():
    x0, y0, w = HORSE_A
    k = w / LAY['sd_horse']['w']
    ex, ey = LAY['sd_horse']['eye']
    return x0 + ex * k, y0 + ey * k


# ---------------------------------------------------------------- ① 紫の 炎
def fires():
    """紫の 炎 3まい（ゆっくり 入れかわる：1まいが 見える → 次へ .8秒 かけて）＋ 赤い 炎 3まい（EYES から 紫と 入れかわる）。少しずつ 上へ 流れる"""
    T = SD_T
    a0, a1 = T['A']
    e0 = T['EYES']
    o = ''
    for tag, cls, extra in (('p', 'sdfp', f'animation:sdFiP {sec(e0 + .6 - a0)} linear {sec(a0)} both'), ('o', 'sdfo', f'animation:sdFiO .6s linear {sec(e0)} both{hide(e0)}')):
        o += f'<div class="sdfi {cls}" style="{extra}">'
        for k in range(3):
            o += _img(f'sd_fire_{tag}{k + 1}', -20, -30, W_ + 40, H_ + 60, 'sdfl', f'animation:sdFl{k} 2.4s linear 0s infinite,sdFlUp 2.4s linear 0s infinite')
        o += '</div>'
    return o


def cross(cx, cy, size, t, dur, cls=''):
    """十字の 光（レンズの 光の 星）：まん中の 光 ＋ 細い 4本の 線 ＋ 輪"""
    return (f'<i class="sdcx{cls}" style="left:{cx - size / 2:.0f}px;top:{cy - size / 2:.0f}px;width:{size}px;height:{size}px;'
            f'animation:sdCx {sec(dur)} cubic-bezier(.2,.8,.3,1) {sec(t)} both{hide(t, t + dur)}"></i>')


def glyphs(n=7, seed=21):
    """炎の 中を ただよう「的中」の 字（送ってくれた 動画の「鬼」の 字の 所：まさちゃん「鬼の文字を的中に変えて」）：下から 上へ・ゆれて・にじんで 消える"""
    T = SD_T
    g0, g1 = T['GLY']
    rng = random.Random(seed)
    L = LAY['sd_glyph']
    o = ''
    for i in range(n):
        w = rng.uniform(64, 118)
        h = w * L['h'] / L['w']
        x = rng.uniform(14, W_ - w - 14)
        y = rng.uniform(560, 760)
        t = g0 + (g1 - g0 - 1.3) * i / max(1, n - 1) + rng.uniform(0, .12)
        dur = rng.uniform(1.15, 1.5)
        o += (f'<img class="sdgy" src="{blob("sd_glyph")}" alt="" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;--dy:{-rng.uniform(190, 320):.0f}px;'
              f'--dx:{rng.uniform(-28, 28):.0f}px;--r:{rng.uniform(-9, 9):.0f}deg;animation:sdGy {sec(dur)} cubic-bezier(.2,.5,.6,1) {sec(t)} both{hide(t, t + dur)}">')
    return o


def scene_a():
    T = SD_T
    a0, a1 = T['A']
    h0, h1 = T['HORSE']
    c1, c2 = T['CROSS']
    ex, ey = eye_pos()
    x0, y0, w = HORSE_A
    return f'''<div class="sdA" aria-hidden="true" style="animation:sdIn .001s linear 0s both{hide(None, a1)}">
      {_img('sd_bg', -20, -40, W_ + 40, H_ + 80, 'sdbg', f'animation:sdBg {sec(a1 - a0)} linear 0s both')}
      <i class="sdau"></i>
      {fires()}
      {_img('sd_horse', x0, y0, w, None, 'sdho', f'transform-origin:{CX - x0:.0f}px {(570.8 - y0):.0f}px;animation:sdHo {sec(h1 - h0)} cubic-bezier(.15,.75,.3,1) {sec(h0)} both,sdBr 1.3s ease-in-out {sec(h1)} infinite alternate')}
      <i class="sdey" style="left:{ex - 46:.0f}px;top:{ey - 46:.0f}px;animation:sdEy .5s ease-out {sec(T['EYES'])} both,sdEyP .9s ease-in-out {sec(T['EYES'] + .5)} infinite alternate{hide(T['EYES'])}"></i>
      <div class="sdgl">{glyphs()}</div>
      {cross(ex, ey, 440, c1, .3)}
      {cross(CX, 430, 980, c2, .36, ' big')}
    </div>'''


# ---------------------------------------------------------------- ② 見本の 動画の コマ（第4.68版：GIF の 1コマずつ／第4.69版：動画を コマ送りで 見て 足した コマ・リアルな 顔・切り裂く 馬の 蹄）
def cut(name, t0, t1, cls='', anim=''):
    """1コマの 絵（画面 いっぱい）：t0 に 出て t1 に 消える（anim＝ほかの 動き）"""
    return _img(name, 0, 0, W_, H_, 'sdcut' + (' ' + cls if cls else ''), f'animation:sdIn .001s linear {sec(t0)} both{anim}{hide(t0, t1)}')


BOLTS_A = (((-20, 120), (400, 610)), ((300, -20), (120, 860)), ((410, 300), (-20, 520)))      # 動画 1.90：桃色の 雷 3本
BOLTS_B = (((-30, 700), (420, 40)), ((-20, 520), (300, 120)))                                   # 動画 1.97：画面を ななめに 走る 大きな 桃色の 雷


def pink_bolts(t0, t1, specs=BOLTS_A, seed=41, cls=''):
    """炎の 場面を 走る 桃色の 雷（ちらつく）"""
    rng = random.Random(seed)
    o = ''
    for (a, b) in specs:
        main = _disp(rng, a, b, (.12, .16, .22, .3, .36))
        paths = [_path(main)]
        for _ in range(3):
            i = rng.randrange(2, len(main) - 2)
            bx, by = main[i]
            L = rng.uniform(40, 110)
            ang = math.atan2(b[1] - a[1], b[0] - a[0]) + rng.choice((-1, 1)) * rng.uniform(.5, 1.1)
            paths.append(_path(_disp(rng, (bx, by), (bx + L * math.cos(ang), by + L * math.sin(ang)), (.4, .45))))
        d = ''.join(f'<path d="{p_}"/>' for p_ in paths)
        o += f'<g class="g1">{d}</g><g class="g2">{d}</g><g class="g3">{d}</g>'
    return f'<svg class="sdpb{cls}" viewBox="0 0 390 844" aria-hidden="true" style="animation:sdPb {sec(t1 - t0)} steps(2,jump-none) {sec(t0)} both{hide(t0, t1)}">{o}</svg>'


def slash_svg():
    """顔の ドアップを ななめに 走る 黒い 切り裂き（ギザギザ）と 白い 光の 筋"""
    rng = random.Random(43)
    top = _disp(rng, (-30, 300), (420, 70), (.03, .05, .06))
    bot = _disp(rng, (-30, 352), (420, 110), (.03, .05, .06))
    poly = ' '.join(f'{x:.0f},{y:.0f}' for x, y in top + bot[::-1])
    return (f'<polygon points="{poly}" fill="#000"/>'
            f'<path d="M-30 690 L420 330" stroke="#FFF2B0" stroke-width="16" stroke-opacity=".35" stroke-linecap="round"/>'
            f'<path d="M-30 690 L420 330" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>')


def face():
    """リアルな 黒い 馬の 顔の ドアップ（sd_rf00〜：コマを 少し 重ねて 入れかえる・ゆっくり 寄る）→ はじめは 青く・おわりに 黒い 切り裂きが 左から 右へ"""
    T = SD_T
    f0, f1 = T['FACE']
    b0, b1 = T['FBLUE']
    s0, s1, s2 = T['FSL']
    names = sorted(k for k in LAY if k.startswith('sd_rf'))
    n = len(names)
    dt = (f1 - f0) / n
    o = f'<div class="sdface" style="animation:sdIn .001s linear {sec(f0)} both,sdFaceZ {sec(f1 - f0)} cubic-bezier(.3,0,.7,1) {sec(f0)} both{hide(f0, f1)}">'
    for k, nm in enumerate(names):
        t0 = f0 + k * dt
        t1 = min(f1, t0 + dt + .08)
        an = f'sdIn .001s linear {sec(t0)} both' if k == 0 else f'sdIn .08s linear {sec(t0)} both'
        o += _img(nm, 0, 0, W_, H_, 'sdrf', f'animation:{an}{hide(t0, t1)}')
    o += f'<i class="sdfblue" style="animation:sdIn .001s linear {sec(b0)} both{hide(b0, b1)}"></i>'
    o += f'<svg class="sdslash" viewBox="0 0 390 844" aria-hidden="true" style="animation:sdSlashLR {sec(s1 - s0)} cubic-bezier(.5,0,.6,1) {sec(s0)} both{hide(s0, s2)}">{slash_svg()}</svg>'
    return o + '</div>'


HOOF_W = 640.0                                  # 馬の 蹄の 絵の 表示の 幅（蹄の 裏が 右・足は 左へ ぶれて すき通る）
HOOF_X = (-30.0, 150.0, 260.0)                  # 蹄の 裏（切り口の 線の 先）の 画面の x：はじまり・まん中の ゆっくりの 入り・出


def hoof_geo():
    """蹄の 絵の 置き方：(倍率 k, 高さ h, 裏の まん中 tx ty, 左の 位置 left, 動く 長さ（まん中の ゆっくりの 入り・出・おわり）)"""
    L = LAY['sd_w_hoof']
    k = HOOF_W / L['w']
    tx, ty = L['tip'][0] * k, L['tip'][1] * k
    left = HOOF_X[0] - tx
    d1, d2 = HOOF_X[1] - HOOF_X[0], HOOF_X[2] - HOOF_X[0]
    dend = (W_ + 10 - L['x0'] * k) - left                       # 見える 左の はしが 右の 外へ 出きる まで
    return k, L['h'] * k, tx, ty, left, (d1, d2, dend)


HOOF_K = (.38, .66)                                 # まん中の ゆっくりの 入り・出（時間の わりあい）


def hoof_tip_t(x):
    """蹄の 裏が 画面の x を 通る 時間の わりあい（0〜1・だいたい）"""
    x0, x1, x2 = HOOF_X
    k1, k2 = HOOF_K
    if x <= x1:
        return k1 * max(0.0, (x - x0) / (x1 - x0))
    if x <= x2:
        return k1 + (k2 - k1) * (x - x1) / (x2 - x1)
    _, _, _, _, _, (d1, d2, dend) = hoof_geo()
    return min(1.0, k2 + (1 - k2) * ((x - x0 - d2) / (dend - d2)) ** .5)


TEAR_Y = 430.0                                  # 蹄の 裏（切り口）の 高さ


def tear_svg():
    """蹄が 通った あとの 黒い 裂け目（見本の 画像 027 の ような ギザギザの 太い 黒い 帯・帯に そって ななめに のびる 細い とげ・そばの ひび）：画面の 座標"""
    rng = random.Random(61)
    y0 = TEAR_Y

    def edge(sign):
        pts, x = [], -30.0
        ph = rng.uniform(0, 6)
        while x < 425:
            th = 17 + 6 * math.sin(x / 53 + ph) + 3 * math.sin(x / 17 + 2 * ph) + rng.uniform(-3, 3)   # 帯の 半分の 太さ
            pts.append((x, y0 + sign * th))
            if rng.random() < .1:                                                # ななめに 寝た とげ（帯に そって 右か 左へ）
                L = rng.uniform(16, 46) * rng.choice((-1, 1))
                pts.append((x + L, y0 + sign * (th + rng.uniform(5, 13))))
                pts.append((x + rng.uniform(4, 8), y0 + sign * (th - 1)))
            x += rng.uniform(4, 11)
        return pts
    top, bot = edge(-1), edge(1)
    poly = ' '.join(f'{x:.0f},{y:.0f}' for x, y in top + bot[::-1])
    o = f'<polygon points="{poly}" fill="#000"/>'
    for _ in range(10):                                                          # 帯から 長く のびる 細い かけら（ほぼ 横・少し ななめ）
        x = rng.uniform(-10, 370)
        sy = rng.choice((-1, 1))
        L = rng.uniform(50, 150) * rng.choice((-1, 1))
        a = math.radians(rng.uniform(3, 12))
        by = y0 + sy * rng.uniform(8, 16)
        tx_, ty_ = x + L, by + sy * abs(L) * math.tan(a)
        w = rng.uniform(2.5, 5.5)
        o += f'<polygon points="{x:.0f},{by - w:.0f} {tx_:.0f},{ty_:.0f} {x:.0f},{by + w:.0f}" fill="#000"/>'
    for _ in range(6):                                                           # 帯の そばの 細い ひび
        ya = y0 + rng.choice((-1, 1)) * rng.uniform(22, 40)
        pts = _disp(rng, (rng.uniform(-20, 250), ya), (rng.uniform(140, 410), ya + rng.uniform(-8, 8)), (.06, .07, .06))
        o += f'<path d="{_path(pts)}" fill="none" stroke="#000" stroke-width="{rng.uniform(1.2, 2.6):.1f}"/>'
    return o


def hoof():
    """鏡の 世界を 左から 右へ 切り裂く 馬の 蹄（第4.69版・まさちゃん「コーンじゃなくて馬の蹄にして！」）：
       焼けた 蹄鉄の 蹄が 足ごと 左から とびこみ、まん中で ゆっくり、少し けりあげながら 右へ 抜ける（裂け目は つま先から：足は その 下）。
       蹄が 通った あとの 炎は 黒い ギザギザの 裂け目で 切れていく（まさちゃん「蹄が、左から右に進むと同時に、切れて言って、元にした画像ファイルのカットシーンみたいにして！」：
       見本の 画像 027）。裂け目は 蹄の 裏に ぴったり ついて のび（同じ 動きの 入れものの 右の はしで 切る）、抜けると 少し 開いて 消える"""
    T = SD_T
    c0, c1 = T['HOOF']
    k0, k1 = T['CUT']
    k, h, tx, ty, left, _ = hoof_geo()
    WW = 1400.0
    o = (f'<div class="sdtr" style="left:{HOOF_X[0] - WW:.0f}px;top:{TEAR_Y - 130:.0f}px;width:{WW:.0f}px;animation:sdIn .001s linear {sec(c0)} both,sdHoofX {sec(c1 - c0)} linear {sec(c0)} both{hide(c0, k1)}">'
         f'<div class="sdtri" style="left:{WW - HOOF_X[0]:.0f}px;animation:sdHoofXi {sec(c1 - c0)} linear {sec(c0)} both">'
         f'<svg class="sdtear" viewBox="0 {TEAR_Y - 130:.0f} 390 260" aria-hidden="true" style="animation:sdTear {sec(k1 - c1)} cubic-bezier(.3,0,.7,1) {sec(c1)} both">{tear_svg()}</svg></div></div>')
    y = TEAR_Y - ty
    o += f'<div class="sdhf" style="left:{left:.0f}px;top:{y:.1f}px;width:{HOOF_W:.0f}px;height:{h:.1f}px;transform-origin:{tx:.0f}px {ty:.0f}px;animation:sdIn .001s linear {sec(c0)} both,sdHoof {sec(c1 - c0)} linear {sec(c0)} both{hide(c0, c1 + .05)}">'
    o += _img('sd_w_hoof', 0, 0, HOOF_W, h, 'sdhfi', f'transform-origin:{tx:.0f}px {ty:.0f}px;animation:sdHfR {sec(c1 - c0)} cubic-bezier(.4,0,.6,1) {sec(c0)} both')
    return o + '</div>'


def world_sparks(n=40, seed=51):
    """GIF 7〜15：左から まん中の 光へ 吸いこまれる 光の 粒（くり返し）"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        y0 = rng.uniform(260, 620)
        s = rng.uniform(2.5, 6)
        o += (f'<i style="left:{CX - s / 2:.1f}px;top:{430 - s / 2:.1f}px;width:{s:.1f}px;height:{s:.1f}px;--x:{-rng.uniform(230, 420):.0f}px;--y:{y0 - 430:.0f}px;'
              f'animation:sdSp {rng.uniform(.45, .8):.2f}s cubic-bezier(.4,0,.9,.7) {-rng.uniform(0, .8):.2f}s infinite"></i>')
    return o


def flyers(t, dur, n=16, seed=53):
    """GIF 18：黒の 中を かけらが 外へ とぶ（小さな 三角）"""
    rng = random.Random(seed)
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rng.uniform(-.3, .3)) / n
        r0 = rng.uniform(30, 120)
        px, py = CX + r0 * math.cos(a), 422 + r0 * math.sin(a) * 1.6
        L = rng.uniform(16, 48)
        w = L * rng.uniform(.3, .6)
        tip = (px + L * math.cos(a), py + L * math.sin(a))
        nx, ny = -math.sin(a) * w / 2, math.cos(a) * w / 2
        poly = ','.join(f'{x:.0f}px {y:.0f}px' for x, y in ((px + nx, py + ny), tip, (px - nx, py - ny)))
        d = rng.uniform(160, 340)
        o += (f'<i style="clip-path:polygon({poly});--x:{d * math.cos(a):.0f}px;--y:{d * math.sin(a) * 1.4:.0f}px;--r:{rng.uniform(-80, 80):.0f}deg;'
              f'animation:sdFly {sec(dur)} cubic-bezier(.2,.5,.6,1) {sec(t)} both"></i>')
    return o


def cut_sparks(n=28, seed=57):
    """切り口（黒い 裂け目）から 上下へ とぶ 火の粉（蹄が 通った 所から 左 → 右へ じゅんに）"""
    T = SD_T
    c0, c1 = T['HOOF']
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        x = rng.uniform(0, W_)
        s_ = rng.uniform(2.5, 5.5)
        dy = rng.choice((-1, 1)) * rng.uniform(40, 170)
        dx = rng.uniform(10, 120)
        d = rng.uniform(.35, .7)
        t = c0 + hoof_tip_t(x) * (c1 - c0) + .02
        o += (f'<i style="left:{x:.0f}px;top:{430 - s_ / 2:.1f}px;width:{s_:.1f}px;height:{s_:.1f}px;--x:{dx:.0f}px;--y:{dy:.0f}px;'
              f'animation:sdCsp {sec(d)} cubic-bezier(.2,.6,.4,1) {sec(t)} both"></i>')
    return f'<div class="sdcsp">{o}</div>'


def scene_b():
    """② 見本の 動画の コマ"""
    T = SD_T
    c0, c1 = T['C0'], T['C1']
    w0, w1 = T['W']
    c18, c19 = T['C18'], T['C19']
    p0, p1 = T['C16'][0], T['GF'][1]
    c17 = T['C17']
    o = f'<div class="sdB" aria-hidden="true" style="animation:sdIn .001s linear {sec(c0[0])} both{hide(c0[0], T["GF"][1])}">'
    o += (f'<div class="sdc0" style="animation:sdIn .001s linear {sec(c0[0])} both{hide(c0[0], c0[1])}">'
          + _img('sd_c0', 0, 0, W_, H_, 'sdcut', f'animation:sdC0z {sec(c0[1] - c0[0])} linear {sec(c0[0])} both')
          + _img('sd_rbs', -30, 0, W_ + 60, H_, 'sdrbs', f'animation:sdRbs {sec(c0[1] - c0[0])} linear {sec(c0[0])} both')
          + '</div>')
    o += cut('sd_c2', *T['F1'], anim=f',sdC0z {sec(T["F1"][1] - T["F1"][0])} linear {sec(T["F1"][0])} both')
    o += cut('sd_dk', *T['DK1'])
    o += _img('sd_c1', -12, 0, W_ + 24, H_, 'sdcut', f'animation:sdIn .001s linear {sec(c1[0])} both{hide(c1[0], c1[1])}')     # ゆらさない（点めつ）
    for key, specs, seed in (('LT', BOLTS_A, 41), ('LT2', BOLTS_B, 47)):
        lt = T[key]
        o += (f'<div class="sdc2" style="animation:sdIn .001s linear {sec(lt[0])} both{hide(lt[0], lt[1])}">'
              + _img('sd_c2', 0, 0, W_, H_, 'sdcut', f'animation:sdC0z {sec(lt[1] - lt[0])} linear {sec(lt[0])} both') + pink_bolts(lt[0], lt[1], specs, seed, '' if key == 'LT' else ' big') + '</div>')
        if key == 'LT':
            o += cut('sd_dk', *T['DK2'])
    o += cut('sd_bw', *T['BW'], anim=f',sdC0z {sec(T["BW"][1] - T["BW"][0])} linear {sec(T["BW"][0])} both')
    o += cut('sd_bwc', *T['BWC'])
    o += face()
    o += cut('sd_chr', *T['CHR'])
    o += cut('sd_crk', *T['CRK'])
    o += cut('sd_c5', *T['C5'])
    o += cut('sd_boom', *T['BOOM'], anim=f',sdC0z {sec(T["BOOM"][1] - T["BOOM"][0])} linear {sec(T["BOOM"][0])} both')
    o += cut('sd_c5', *T['C5B'])
    o += cut('sd_c6', *T['C6'])
    wa = f'{sec(w1 - w0)} cubic-bezier(.3,.2,.6,1) {sec(w0)} both'
    n0, n1 = T['WN']
    f3 = T['FIRE3']
    fo = f',sdFo {sec(f3[1] - f3[0])} linear {sec(f3[0])} forwards'
    o += (f'<div class="sdw" style="animation:sdIn .001s linear {sec(w0)} both,sdNeg {sec(n1 - n0)} linear {sec(n0)} forwards{hide(w0, w1)}">'
          + _img('sd_w_bg', 0, 0, W_, H_, 'sdwbg', f'animation:sdWz {wa}')
          + _img('sd_w_prism', 0, 0, W_, H_, 'sdwpr', f'animation:sdWz {wa},sdPr .6s ease-in-out {sec(w0)} infinite alternate')
          + _img('sd_w_fire1', -20, 0, W_ + 40, H_, 'sdwf', f'animation:sdWf {wa},sdWf1 .9s ease-in-out {sec(w0)} infinite alternate{fo}')
          + _img('sd_w_fire2', -20, 0, W_ + 40, H_, 'sdwf', f'animation:sdWf {wa},sdWf2 .9s ease-in-out {sec(w0)} infinite alternate{fo}')
          + _img('sd_w_fire3', -20, 0, W_ + 40, H_, 'sdwf f3', f'animation:sdWf {wa},sdFi {sec(f3[1] - f3[0])} linear {sec(f3[0])} both,sdF3 .45s ease-in-out {sec(f3[1])} infinite alternate{hide(f3[0])}')
          + f'<i class="sdcore" style="animation:sdCore .5s ease-in-out {sec(w0)} infinite alternate"></i>'
          + f'<div class="sdwsp">{world_sparks()}</div>'
          + hoof() + cut_sparks()
          + _img('sd_w_near', 0, 0, W_, H_, 'sdwn', f'animation:sdWn {sec(w1 - w0)} cubic-bezier(.3,.1,.7,1) {sec(w0)} both')
          + '</div>')
    o += cut('sd_c16', *T['C16'])
    o += cut('sd_c16r', *T['C16R'])
    o += cut('sd_c16b', *T['C16B'])
    o += cut('sd_c17', *c17, anim=f',sdC17z {sec(c17[1] - c17[0])} linear {sec(c17[0])} both')
    o += (f'<div class="sdc18" style="animation:sdIn .001s linear {sec(c18[0])} both{hide(c18[0], c18[1])}">'
          + _img('sd_c18', 0, 0, W_, H_, 'sdcut')
          + f'<div class="sdfly">{flyers(c18[0], c18[1] - c18[0] + .02)}</div>'
          + f'<i class="sdspk" style="animation:sdSpk {sec(c18[1] - c18[0])} ease-in {sec(c18[0])} both"></i>'
          + '</div>')
    o += (f'<div class="sdc19" style="animation:sdIn .001s linear {sec(c19[0])} both{hide(c19[0], T["GF"][1])}">'
          + _img('sd_c19', 0, 0, W_, H_, 'sdcut', f'animation:sdC19z {sec(c19[1] - c19[0])} linear {sec(c19[0])} both')
          + f'<i class="sdc19g" style="animation:sdC19g {sec(c19[1] - c19[0])} cubic-bezier(.5,0,.9,.5) {sec(c19[0])} both"></i>'
          + f'<i class="sdc19f" style="animation:sdC19f {sec(c19[1] - c19[0])} cubic-bezier(.5,0,.9,.5) {sec(c19[0])} both"></i>'
          + '</div>')
    o += _img('sd_pillar', -22, 0, 60, H_, 'sdpil', f'animation:sdIn .001s linear {sec(p0)} both,sdPil .3s ease-in-out {sec(p0)} infinite alternate{hide(p0, p1)}')
    o += _img('sd_pillar', W_ - 38, 0, 60, H_, 'sdpil r', f'animation:sdIn .001s linear {sec(p0)} both,sdPil .3s ease-in-out {sec(p0 - .15)} infinite alternate{hide(p0, p1)}')
    return o + '</div>'


# ---------------------------------------------------------------- ③ ど！！！的中（光の 中から 出てくる・雷を まとう）
def _disp(rng, a, b, rough):
    pts = [a, b]
    for r in rough:
        nw = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay) or 1.0
            nx, ny = -(by - ay) / L, (bx - ax) / L
            off = rng.gauss(0, r * L / 2)
            nw += [((ax + bx) / 2 + nx * off, (ay + by) / 2 + ny * off), (bx, by)]
        pts = nw
    return pts


def _path(pts):
    """みじかく 書いた path（1px に まるめて・となりとの ちがいで）"""
    q = [(round(x), round(y)) for x, y in pts]
    o = f'M{q[0][0]} {q[0][1]}l'
    px, py = q[0]
    st = []
    for x, y in q[1:]:
        if (x, y) != (px, py):
            st.append(f'{x - px} {y - py}')
            px, py = x, y
    return o + ' '.join(st) if st else ''


def logo_boxes():
    """ロゴの 字の 箱（left, top, right, bottom）：絵の 中の 字の 大きさ（shiden_art.py：ど・！は 絵の 幅の 約47%・的中は 約73%）"""
    out = []
    for key, frac in (('sd_t_do', .47), ('e1', .4), ('e2', .4), ('e3', .4), ('sd_t_hit', .73)):
        cx, cy, w = LOGO[key]
        name = 'sd_t_ex' if key.startswith('e') else key
        h = w * LAY[name]['h'] / LAY[name]['w']
        gw, gh = w * frac, h * (frac if key != 'sd_t_hit' else .7)
        if key.startswith('e'):
            gw = w * .18
        out.append((cx - gw / 2, cy - gh / 2, cx + gw / 2, cy + gh / 2))
    return out


def logo_outline(n=160, seed=3):
    """ロゴの ふち（字の 箱の まわり）を 等間隔に → [(x, y, 外向きの nx, ny)]"""
    rng = random.Random(seed)
    pts = []
    for (l, t, r, b) in logo_boxes():
        per = 2 * ((r - l) + (b - t))
        k = max(8, int(n * per / 2600))
        for i in range(k):
            u = (i + rng.random() * .5) / k * per
            if u < r - l:
                pts.append((l + u, t, 0, -1))
            elif u < (r - l) + (b - t):
                pts.append((r, t + (u - (r - l)), 1, 0))
            elif u < 2 * (r - l) + (b - t):
                pts.append((r - (u - (r - l) - (b - t)), b, 0, 1))
            else:
                pts.append((l, b - (u - 2 * (r - l) - (b - t)), -1, 0))
    return pts


def arc_frames():
    """ロゴに まとう 電気の コマ（ARCS の 間・AR_DT ごと）：ふちの 上で 小さく はじける ギザギザ（10〜34px）12〜16本 と、字と 字を つなぐ 電気 1〜2本。コマごとに 形が かわる（ジリジリ）"""
    T = SD_T
    a0, a1 = T['ARCS']
    rng = random.Random(17)
    OL = logo_outline()
    o = ''
    t = a0
    while t < a1:
        d = ''
        for _ in range(rng.randint(18, 24)):
            x, y, nx, ny = OL[rng.randrange(len(OL))]
            ang = math.atan2(ny, nx) + rng.uniform(-1.3, 1.3)
            ln = rng.uniform(12, 46)
            p0 = (x + nx * rng.uniform(-3, 3), y + ny * rng.uniform(-3, 3))
            main = _disp(rng, p0, (p0[0] + ln * math.cos(ang), p0[1] + ln * math.sin(ang)), (.5, .6, .6))
            d += _path(main)
            if rng.random() < .45:
                q = main[rng.randint(1, len(main) - 2)]
                a2 = ang + rng.choice((-1, 1)) * rng.uniform(.6, 1.3)
                l2 = ln * rng.uniform(.3, .6)
                d += _path(_disp(rng, q, (q[0] + l2 * math.cos(a2), q[1] + l2 * math.sin(a2)), (.5, .6)))
        for _ in range(rng.randint(2, 3)):                                        # 字と 字を つなぐ
            p, q = OL[rng.randrange(len(OL))], OL[rng.randrange(len(OL))]
            if math.hypot(p[0] - q[0], p[1] - q[1]) > 60:
                d += _path(_disp(rng, (p[0], p[1]), (q[0], q[1]), (.25, .3, .35, .4)))
        life = AR_DT * rng.choice((1, 1, 1, 2))
        o += (f'<g class="sdar" style="animation:sdFk {sec(life)} linear {sec(t)} forwards{hide(t, t + life)}">'
              f'<g class="g1"><path d="{d}"/></g><g class="g2"><path d="{d}"/></g><g class="g3"><path d="{d}"/></g></g>')
        t += AR_DT
    return o


def big_bolts():
    """不定期に ロゴから 画面の 全方位へ 届く 大きな 雷（BOLTS の 時刻と 本数）：ロゴの ふちの 点 → 上下左右の ふちの 外（枝つき）。白い しん・紫の 光・0.2〜0.26秒 光って 消える"""
    T = SD_T
    rng = random.Random(29)
    OL = logo_outline(seed=9)
    o = ''
    sides = ['top', 'bottom', 'left', 'right']
    for (t, n) in T['BOLTS']:
        rng.shuffle(sides)
        for k in range(n):
            x, y, nx, ny = OL[rng.randrange(len(OL))]
            side = sides[k % 4]
            if side == 'top':
                e = (rng.uniform(-30, W_ + 30), -30.0)
            elif side == 'bottom':
                e = (rng.uniform(-30, W_ + 30), H_ + 30)
            elif side == 'left':
                e = (-30.0, rng.uniform(-30, H_ + 30))
            else:
                e = (W_ + 30, rng.uniform(-30, H_ + 30))
            main = _disp(rng, (x, y), e, (.22, .28, .3, .36, .4, .42))
            paths = [_path(main)]
            for _ in range(rng.randint(2, 4)):
                i = rng.randrange(2, len(main) - 2)
                bx, by = main[i]
                L = rng.uniform(40, 130)
                ang = math.atan2(e[1] - y, e[0] - x) + rng.choice((-1, 1)) * rng.uniform(.5, 1.2)
                paths.append(_path(_disp(rng, (bx, by), (bx + L * math.cos(ang), by + L * math.sin(ang)), (.4, .4, .45))))
            d = ''.join(f'<path d="{p_}"/>' for p_ in paths)
            dl = t + k * rng.uniform(.02, .06)
            dur = rng.uniform(.2, .26)
            o += (f'<g class="sdbt" style="animation:sdBt {sec(dur)} steps(3,jump-none) {sec(dl)} both{hide(dl, dl + dur)}">'
                  f'<g class="g1">{d}</g><g class="g2">{d}</g><g class="g3">{d}</g></g>')
    return o


def lightning():
    return f'<svg class="sdbo" viewBox="0 0 390 844" aria-hidden="true">{arc_frames()}{big_bolts()}</svg>'


def coins(n=40, seed=17):
    """金の 粒（出きった 瞬間に ロゴから とびちる）"""
    T = SD_T
    rng = random.Random(seed)
    cx, cy = CX, 420.0
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rng.uniform(-.4, .4)) / n
        d = rng.uniform(200, 460)
        s = rng.uniform(5, 13)
        dl = T['LAND'] + rng.uniform(0, .05)
        dur = rng.uniform(.6, .95)
        o += (f'<i style="left:{cx - s / 2:.0f}px;top:{cy - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;--x:{d * math.cos(a):.0f}px;--y:{d * math.sin(a) * .9 - 30:.0f}px;--r:{rng.uniform(-200, 200):.0f}deg;'
              f'animation:sdCo {sec(dur)} cubic-bezier(.1,.7,.3,1) {sec(dl)} both{hide(dl, dl + dur)}"></i>')
    return o


def embers(n=22, seed=9):
    """火の 粉（下から 上へ・ゆれる）"""
    T = SD_T
    rng = random.Random(seed)
    t0 = T['LAND'] + .2
    o = ''
    for _ in range(n):
        s = rng.uniform(2.5, 5)
        o += (f'<i style="left:{rng.uniform(10, W_ - 10):.0f}px;top:{rng.uniform(700, 860):.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dy:{-rng.uniform(560, 900):.0f}px;--sx:{rng.uniform(-30, 30):.0f}px;'
              f'animation:sdEm {rng.uniform(2.4, 3.8):.1f}s linear {sec(t0 + rng.uniform(0, 2.4))} infinite,sdEmX {rng.uniform(.9, 1.6):.1f}s ease-in-out 0s infinite alternate"></i>')
    return f'<div class="sdem" style="animation:sdIn .001s linear {sec(t0)} both{hide(t0)}">{o}</div>'


def logo():
    """ど！！！的中：まとめて 画面の 奥から 出てくる（.sdlogo が 0.1倍 → 1倍）。字は 白熱（まぶしい 白）の まま 出て、出きる ころに 金と 虹の 色に 冷める（.sdt の filter）。字ごとに 少し ずらす。
       出きった 瞬間の 揺れは 小さく（±3px・2往復：ふちの 点めつを ふやさない）"""
    T = SD_T
    t0, d = T['LOGO'], T['EMERGE']
    o = ''
    for k, (key, name) in enumerate((('sd_t_do', 'sd_t_do'), ('e1', 'sd_t_ex'), ('e2', 'sd_t_ex'), ('e3', 'sd_t_ex'), ('sd_t_hit', 'sd_t_hit'))):
        cx, cy, w = LOGO[key]
        dl = t0 + .04 * k
        o += _img_c(name, cx, cy, w, 'sdt' + (' hit' if key == 'sd_t_hit' else ''),
                    f'animation:sdPop {sec(d - .04 * k)} cubic-bezier(.2,.9,.3,1.2) {sec(dl)} both,sdHot {sec(d + .25)} ease-out {sec(dl)} both{hide(dl)}'
                    + (f',sdPulse 1.15s ease-in-out {sec(T["LAND"] + .4)} infinite alternate' if key == 'sd_t_hit' else ''))
    return f'<div class="sdlogo" style="animation:sdEmerge {sec(d)} cubic-bezier(.2,.8,.3,1) {sec(t0)} both,sdShkB .3s linear {sec(T["LAND"])} both{hide(t0)}">{o}</div>'


def scene_c():
    T = SD_T
    c0 = T['C']
    g0, g1, g2, g3 = T['GF']
    return f'''<div class="sdC" aria-hidden="true" style="animation:sdIn .001s linear {sec(c0)} both,sdPunch .4s cubic-bezier(.1,.8,.3,1) {sec(T['LAND'])} both{hide(c0)}">
      {_img('sd_rtex', -10, -30, W_ + 20, H_ + 100, 'sdrt', f'animation:sdRt 7s ease-in-out 0s infinite alternate,sdRtIn .4s linear {sec(g2)} both')}
      <i class="sdvg"></i>
      <i class="sdgf" style="left:{CX - 560:.0f}px;top:{430 - 560:.0f}px;animation:sdGf {sec(g3 - g0)} linear {sec(g0)} both{hide(g0, g3)}"></i>
      {logo()}
      <div class="sdco">{coins()}</div>
      {lightning()}
      {embers()}
    </div>'''


# ---------------------------------------------------------------- 層
def sd_layers(board_html):
    """押したあと（下から）：① 紫の 炎 → ② GIF の 1コマずつ → ③ 光が 弾けて ど！！！的中（雷を まとう）→ ボード（board_html）"""
    return f'''<div class="sdk" aria-hidden="true"></div>
    {scene_a()}
    {scene_b()}
    {scene_c()}
    <div class="hb">{board_html}</div>
    <p class="sr">ど的中！紫の 炎の 中に 黒い 馬の 影が 立ち上がり、目が 赤く 光る。白黒の 煙と 虹色の 光・桃色の 雷・光る 目・赤と 緑の 裂け目・割れた 鏡の 世界の 金の 炎・黒い 穴・緑の 光の 輪。光が 弾けて「ど！！！的中」が 雷を まとって 出てくる</p>'''


def sd_css():
    T = SD_T
    g0, g1, g2, g3 = T['GF']
    gd = g3 - g0
    e0 = T['EYES']
    a0, a1 = T['A']
    hd = hoof_geo()[5]
    return f'''
/* ---------- ど的中・紫電（sd）：shiden.py（① と ロゴの 絵は flat/shiden_art.py・② の 絵は flat/shiden_cuts.py・十字の 光・雷・光の 粒・火の 粉は CSS と SVG） ---------- */
.ov.fz.sd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes sdH{{0%,100%{{visibility:hidden}}}}
@keyframes sdIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes sdFk{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdk{{position:absolute;inset:0;background:#050208}}
.ov.sd .sdA,.ov.sd .sdB,.ov.sd .sdC{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}
.ov.sd img{{position:absolute;display:block;max-width:none}}
.ov.sd .sdA i,.ov.sd .sdB i,.ov.sd .sdC i{{position:absolute;display:block}}
.ov.sd .sdB > div{{position:absolute;inset:0}}
/* ① 紫の 炎 */
.ov.sd .sdbg{{transform-origin:50% 55%}}
@keyframes sdBg{{from{{transform:scale(1)}}to{{transform:scale(1.1)}}}}
.ov.sd .sdau{{left:-60px;top:120px;width:510px;height:620px;border-radius:50%;background:radial-gradient(ellipse at 50% 60%,rgba(140,40,230,.55),rgba(80,10,150,.25) 45%,rgba(40,0,80,0) 70%)}}
.ov.sd .sdfi{{position:absolute;inset:0}}
.ov.sd .sdfi.sdfp{{opacity:1}}
@keyframes sdFiP{{0%,{(e0 - a0) / (e0 + .6 - a0) * 100:.1f}%{{opacity:1}}100%{{opacity:.25}}}}
.ov.sd .sdfi.sdfo{{opacity:0}}
@keyframes sdFiO{{from{{opacity:0}}to{{opacity:1}}}}
.ov.sd .sdfl{{transform-origin:50% 100%;opacity:0}}
@keyframes sdFl0{{0%,25%{{opacity:1}}33%,92%{{opacity:0}}100%{{opacity:1}}}}
@keyframes sdFl1{{0%,25%{{opacity:0}}33%,58%{{opacity:1}}67%,100%{{opacity:0}}}}
@keyframes sdFl2{{0%,58%{{opacity:0}}67%,92%{{opacity:1}}100%{{opacity:0}}}}
@keyframes sdFlUp{{from{{transform:translateY(0) scaleY(1)}}to{{transform:translateY(-34px) scaleY(1.06)}}}}
.ov.sd .sdho{{transform-origin:50% 62%;filter:drop-shadow(0 0 14px rgba(170,60,255,.55))}}
@keyframes sdHo{{0%{{opacity:0;transform:scale(1.45) translateY(30px)}}30%{{opacity:1}}100%{{opacity:1;transform:none}}}}
@keyframes sdBr{{from{{transform:scale(1)}}to{{transform:scale(1.014)}}}}
.ov.sd .sdey{{width:92px;height:92px;border-radius:50%;opacity:0;background:radial-gradient(circle,#FFF0F0 0,#FF4050 9%,rgba(255,40,70,.6) 22%,rgba(255,30,60,0) 60%)}}
@keyframes sdEy{{0%{{opacity:0;transform:scale(.3)}}60%{{opacity:1;transform:scale(1.25)}}100%{{opacity:1;transform:scale(1)}}}}
@keyframes sdEyP{{from{{transform:scale(1)}}to{{transform:scale(1.18)}}}}
.ov.sd .sdgl{{position:absolute;inset:0}}
.ov.sd .sdgy{{opacity:0;transform-origin:50% 50%}}
@keyframes sdGy{{0%{{opacity:0;transform:translate(0,0) scale(.7) rotate(0)}}18%{{opacity:1}}72%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1.08) rotate(var(--r))}}}}
.ov.sd .sdcx{{opacity:0;border-radius:50%;transform-origin:50% 50%;
  background:linear-gradient(90deg,transparent 48.6%,#FFFFFF 50%,transparent 51.4%),linear-gradient(0deg,transparent 48.6%,#FFFFFF 50%,transparent 51.4%),
  linear-gradient(45deg,transparent 49.4%,rgba(255,255,255,.7) 50%,transparent 50.6%),linear-gradient(-45deg,transparent 49.4%,rgba(255,255,255,.7) 50%,transparent 50.6%),
  radial-gradient(circle,#FFFFFF 0 3%,rgba(255,230,255,.85) 7%,rgba(220,150,255,.35) 16%,rgba(180,80,255,0) 34%)}}
.ov.sd .sdcx.big{{background:linear-gradient(90deg,transparent 48.8%,#FFFFFF 50%,transparent 51.2%),linear-gradient(0deg,transparent 48.8%,#FFFFFF 50%,transparent 51.2%),
  radial-gradient(circle,#FFFFFF 0 5%,rgba(255,240,255,.9) 10%,rgba(230,170,255,.45) 20%,rgba(180,80,255,0) 38%)}}
@keyframes sdCx{{0%{{opacity:0;transform:scale(.25) rotate(-8deg)}}30%{{opacity:1}}100%{{opacity:0;transform:scale(1.25) rotate(6deg)}}}}
/* GIF 2：桃色の 雷 */
.ov.sd .sdpb{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.sd .sdpb path{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
.ov.sd .sdpb .g1 path{{stroke:#FF3CD2;stroke-width:40;stroke-opacity:.34}}
.ov.sd .sdpb .g2 path{{stroke:#FFA6EC;stroke-width:13;stroke-opacity:.9}}
.ov.sd .sdpb .g3 path{{stroke:#FFFFFF;stroke-width:5}}
.ov.sd .sdpb.big .g1 path{{stroke-width:70;stroke-opacity:.4}}
.ov.sd .sdpb.big .g2 path{{stroke-width:22}}
.ov.sd .sdpb.big .g3 path{{stroke-width:8}}
@keyframes sdPb{{0%{{opacity:1}}50%{{opacity:.55}}100%{{opacity:1}}}}
/* ② GIF の 1コマずつ */
.ov.sd .sdcut{{transform-origin:50% 50%}}
@keyframes sdC0z{{from{{transform:scale(1.04)}}to{{transform:scale(1)}}}}
.ov.sd .sdrbs{{opacity:.95}}
@keyframes sdRbs{{from{{transform:translate(-26px,14px)}}to{{transform:translate(26px,-14px)}}}}
.ov.sd .sdslash{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.sd .sdw{{overflow:hidden}}
.ov.sd .sdwbg,.ov.sd .sdwpr{{transform-origin:50% 51%}}
@keyframes sdWz{{from{{transform:scale(1) rotate(-1.2deg)}}to{{transform:scale(1.24) rotate(1.2deg)}}}}
@keyframes sdPr{{from{{opacity:.75}}to{{opacity:1}}}}
.ov.sd .sdwf{{transform-origin:50% 51%}}
@keyframes sdWf{{from{{transform:translateX(-8px) scale(1)}}to{{transform:translateX(6px) scale(1.2)}}}}
@keyframes sdWf1{{from{{opacity:1}}to{{opacity:.45}}}}
@keyframes sdWf2{{from{{opacity:.45}}to{{opacity:1}}}}
.ov.sd .sdcore{{left:{CX - 85:.0f}px;top:{430 - 85:.0f}px;width:170px;height:170px;border-radius:50%;transform-origin:50% 50%;mix-blend-mode:screen;
  background:radial-gradient(circle,rgba(255,255,255,.95) 0,rgba(255,240,252,.85) 12%,rgba(255,150,226,.6) 34%,rgba(255,100,210,.2) 52%,rgba(255,80,200,0) 64%)}}
@keyframes sdCore{{from{{transform:scale(.92)}}to{{transform:scale(1.14)}}}}
.ov.sd .sdwsp{{position:absolute;inset:0}}
.ov.sd .sdwsp i{{border-radius:50%;background:#FFF6D8;box-shadow:0 0 6px 1px #FFC94A;opacity:0}}
@keyframes sdSp{{0%{{opacity:0;transform:translate(var(--x),var(--y)) scale(1.2)}}20%{{opacity:1}}100%{{opacity:0;transform:translate(0,0) scale(.3)}}}}
.ov.sd .sdwn{{transform-origin:50% 51%;opacity:.95}}
@keyframes sdWn{{from{{transform:scale(1)}}to{{transform:scale(1.32)}}}}
/* 第4.69版：リアルな 馬の 顔（12コマを 少し 重ねて 入れかえ・ゆっくり 寄る・はじめは 青く・おわりに 黒い 切り裂きが 左から 右へ）*/
.ov.sd .sdface{{position:absolute;inset:0;transform-origin:46% 36%}}
@keyframes sdFaceZ{{from{{transform:scale(1)}}to{{transform:scale(1.08)}}}}
.ov.sd .sdfblue{{inset:0;mix-blend-mode:screen;background:radial-gradient(ellipse at 45% 38%,rgba(120,170,255,.7),rgba(30,70,255,.5) 45%,rgba(10,30,200,.45))}}
@keyframes sdSlashLR{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
/* 第4.69版：馬の 蹄が 左から 右へ 切り裂く（まん中で ゆっくり・少し ふりおろす）・通った あとの 炎は 黒い ギザギザの 裂け目で 切れていく（裂け目は 蹄と 同じ 動きの 入れものの 右の はしで 切る → 抜けると 少し 開いて 消える）・炎の 形の 入れかえ・世界の 反転 */
.ov.sd .sdhf{{position:absolute}}
@keyframes sdHoof{{0%{{transform:translateX(0) scale(.9);animation-timing-function:cubic-bezier(.25,.5,.5,1)}}{HOOF_K[0] * 100:.0f}%{{transform:translateX({hd[0]:.0f}px) scale(1);animation-timing-function:linear}}{HOOF_K[1] * 100:.0f}%{{transform:translateX({hd[1]:.0f}px) scale(1.04);animation-timing-function:cubic-bezier(.55,0,.85,.45)}}100%{{transform:translateX({hd[2]:.0f}px) scale(1.1)}}}}
@keyframes sdHoofX{{0%{{transform:translateX(0);animation-timing-function:cubic-bezier(.25,.5,.5,1)}}{HOOF_K[0] * 100:.0f}%{{transform:translateX({hd[0]:.0f}px);animation-timing-function:linear}}{HOOF_K[1] * 100:.0f}%{{transform:translateX({hd[1]:.0f}px);animation-timing-function:cubic-bezier(.55,0,.85,.45)}}100%{{transform:translateX({hd[2]:.0f}px)}}}}
@keyframes sdHoofXi{{0%{{transform:translateX(0);animation-timing-function:cubic-bezier(.25,.5,.5,1)}}{HOOF_K[0] * 100:.0f}%{{transform:translateX({-hd[0]:.0f}px);animation-timing-function:linear}}{HOOF_K[1] * 100:.0f}%{{transform:translateX({-hd[1]:.0f}px);animation-timing-function:cubic-bezier(.55,0,.85,.45)}}100%{{transform:translateX({-hd[2]:.0f}px)}}}}
@keyframes sdHfR{{from{{transform:rotate(-8deg)}}to{{transform:rotate(3deg)}}}}
.ov.sd .sdtr{{position:absolute;height:260px;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 46px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 46px),transparent)}}
.ov.sd .sdtri{{position:absolute;top:0;width:390px;height:260px}}
.ov.sd .sdtear{{position:absolute;left:0;top:0;width:390px;height:260px;overflow:visible;transform-origin:50% 50%}}
@keyframes sdTear{{0%{{transform:scaleY(1);opacity:1}}35%{{transform:scaleY(1.5);opacity:1}}100%{{transform:scaleY(.3);opacity:0}}}}
.ov.sd .sdcsp{{position:absolute;inset:0}}
.ov.sd .sdcsp i{{border-radius:50%;background:#FFF6C8;box-shadow:0 0 6px 2px #FFA020;opacity:0}}
@keyframes sdCsp{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:1}}100%{{opacity:0;transform:translate(var(--x),var(--y))}}}}
@keyframes sdFo{{to{{opacity:0}}}}
@keyframes sdFi{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes sdF3{{from{{opacity:1}}to{{opacity:.72}}}}
@keyframes sdNeg{{0%,100%{{filter:invert(1)}}}}
@keyframes sdC17z{{from{{transform:scale(1)}}to{{transform:scale(1.06)}}}}
.ov.sd .sdfly{{position:absolute;inset:0}}
.ov.sd .sdfly i{{inset:0;background:linear-gradient(135deg,#FFFFFF,#C8D4E8 40%,#4A5068 70%,#E8F0FF)}}
@keyframes sdFly{{from{{transform:translate(0,0) rotate(0)}}to{{transform:translate(var(--x),var(--y)) rotate(var(--r))}}}}
.ov.sd .sdspk{{left:{CX - 170:.0f}px;top:{422 - 45:.0f}px;width:340px;height:90px;border-radius:50%;transform-origin:50% 50%;
  background:radial-gradient(ellipse 22% 34% at 50% 50%,#FFFFFF 0,#FFFFFF 18%,#FFF2A0 34%,rgba(255,220,80,.75) 55%,rgba(255,200,40,0) 100%),linear-gradient(90deg,rgba(255,230,120,0),rgba(255,244,170,1) 50%,rgba(255,230,120,0)) 50% 50%/100% 4px no-repeat}}
@keyframes sdSpk{{from{{transform:scale(.7,.7)}}to{{transform:scale(1.3,1)}}}}
@keyframes sdC19z{{from{{transform:scale(1)}}to{{transform:scale(1.04)}}}}
.ov.sd .sdc19g{{left:{CX - 300:.0f}px;top:{422 - 190:.0f}px;width:600px;height:380px;border-radius:50%;transform-origin:50% 50%;mix-blend-mode:screen;
  background:radial-gradient(ellipse 50% 40% at 50% 50%,#FFFFFF 0,#FFFFFF 10%,#FFFBD0 20%,#FFEA70 32%,rgba(210,255,110,.7) 50%,rgba(120,255,140,0) 78%)}}
@keyframes sdC19g{{0%{{opacity:.75;transform:scale(.55,.45)}}100%{{opacity:1;transform:scale(1.15,1)}}}}
.ov.sd .sdc19f{{left:-40px;top:{422 - 22:.0f}px;width:470px;height:44px;transform-origin:50% 50%;mix-blend-mode:screen;
  background:radial-gradient(ellipse 50% 50% at 50% 50%,rgba(255,255,240,1) 0,rgba(255,240,140,.9) 10%,rgba(255,220,80,.35) 40%,rgba(255,210,60,0) 100%),
  linear-gradient(90deg,rgba(255,236,120,.2),rgba(255,248,190,1) 25%,#FFFFFF 50%,rgba(255,248,190,1) 75%,rgba(255,236,120,.2)) 50% 50%/100% 8px no-repeat,
  linear-gradient(90deg,rgba(255,236,120,0),rgba(255,236,120,.5) 30%,rgba(255,240,150,.7) 50%,rgba(255,236,120,.5) 70%,rgba(255,236,120,0)) 50% 50%/100% 26px no-repeat}}
@keyframes sdC19f{{0%{{opacity:.8;transform:scaleX(.6)}}100%{{opacity:1;transform:scaleX(1.1) scaleY(1.5)}}}}
.ov.sd .sdpil{{transform-origin:50% 50%}}
.ov.sd .sdpil.r{{transform:scaleX(-1)}}
@keyframes sdPil{{from{{opacity:.85}}to{{opacity:1}}}}
/* ③ 光が 弾けて ど！！！的中が 出てくる・雷を まとう */
.ov.sd .sdrt{{opacity:.55}}
@keyframes sdRt{{from{{transform:translateY(0)}}to{{transform:translateY(-60px)}}}}
@keyframes sdRtIn{{from{{opacity:0}}to{{opacity:.55}}}}
.ov.sd .sdvg{{inset:0;background:radial-gradient(ellipse 85% 70% at 50% 46%,rgba(0,0,0,0) 35%,rgba(0,0,0,.7) 100%),linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0) 25%,rgba(0,0,0,0) 75%,rgba(0,0,0,.6))}}
.ov.sd .sdgf{{width:1120px;height:1120px;border-radius:50%;opacity:0;transform-origin:50% 50%;
  background:radial-gradient(circle,#FFFFFF 0,#FFF6DA 7%,#FFE9A0 16%,#FFD86A 30%,rgba(255,190,60,.85) 42%,rgba(255,150,30,0) 64%)}}
@keyframes sdGf{{0%{{opacity:0;transform:scale(.2)}}{(g1 - g0) / gd * 100:.1f}%{{opacity:1;transform:scale(1)}}{(g2 - g0) / gd * 100:.1f}%{{opacity:1;transform:scale(1.08)}}100%{{opacity:0;transform:scale(1.3)}}}}
.ov.sd .sdlogo{{position:absolute;inset:0;transform-origin:50% 420px}}
@keyframes sdEmerge{{0%{{opacity:0;transform:scale(.1)}}18%{{opacity:1}}100%{{opacity:1;transform:scale(1)}}}}
@keyframes sdShkB{{0%,100%{{transform:none}}25%{{transform:translate(-3px,2px)}}65%{{transform:translate(3px,-2px)}}}}
@keyframes sdPunch{{0%{{transform:scale(1.03)}}100%{{transform:none}}}}
.ov.sd .sdt{{opacity:0;transform-origin:50% 50%}}
@keyframes sdPop{{0%{{opacity:0;transform:scale(.55)}}30%{{opacity:1}}70%{{transform:scale(1.03)}}100%{{opacity:1;transform:none}}}}
@keyframes sdHot{{0%,55%{{filter:brightness(2.8) saturate(0) drop-shadow(0 0 18px rgba(255,255,255,.95))}}100%{{filter:brightness(1) saturate(1) drop-shadow(0 0 0 rgba(255,255,255,0))}}}}
@keyframes sdPulse{{from{{transform:scale(1)}}to{{transform:scale(1.045)}}}}
.ov.sd .sdco{{position:absolute;inset:0}}
.ov.sd .sdco i{{border-radius:50%;opacity:0;background:radial-gradient(circle at 35% 35%,#FFFBE0,#FFD24A 45%,#B8780A);box-shadow:0 0 6px rgba(255,210,90,.8)}}
@keyframes sdCo{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}10%{{opacity:1}}80%{{opacity:1}}100%{{opacity:0;transform:translate(var(--x),var(--y)) scale(.9) rotate(var(--r))}}}}
.ov.sd .sdbo{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.sd .sdbo path{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
.ov.sd .sdar{{opacity:0}}
.ov.sd .sdar .g1 path{{stroke:#A050FF;stroke-width:8;stroke-opacity:.26}}
.ov.sd .sdar .g2 path{{stroke:#E0B8FF;stroke-width:2.8;stroke-opacity:.7}}
.ov.sd .sdar .g3 path{{stroke:#FFFFFF;stroke-width:1.2}}
.ov.sd .sdbt{{opacity:0}}
@keyframes sdBt{{0%{{opacity:1}}35%{{opacity:.6}}70%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdbt .g1 path{{stroke:#9A40FF;stroke-width:16;stroke-opacity:.16}}
.ov.sd .sdbt .g2 path{{stroke:#D9A6FF;stroke-width:5;stroke-opacity:.55}}
.ov.sd .sdbt .g3 path{{stroke:#FFFFFF;stroke-width:2}}
.ov.sd .sdem{{position:absolute;inset:0}}
.ov.sd .sdem i{{border-radius:50%;background:#FFD27A;box-shadow:0 0 6px 1px rgba(255,150,40,.9);opacity:0}}
@keyframes sdEm{{0%{{opacity:0;transform:translateY(0)}}12%{{opacity:1}}85%{{opacity:.8}}100%{{opacity:0;transform:translateY(var(--dy))}}}}
@keyframes sdEmX{{from{{margin-left:0}}to{{margin-left:var(--sx)}}}}
.ov.sd .hb{{z-index:10;animation:sdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .15)} both{hide(T['RES'] + .15)}}}
@keyframes sdBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
@keyframes sdDim{{to{{opacity:.3}}}}
/* 視差効果を減らす：① ② と 光・雷・粒を 出さない。③の 虹の 布の 上に ロゴ（動かさない）→ 1.3秒から ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.fz.sd{{--t0:1.9s}}
  .ov.sd .sdA,.ov.sd .sdB,.ov.sd .sdgf,.ov.sd .sdco,.ov.sd .sdbo,.ov.sd .sdem{{display:none}}
  .ov.sd .sdC{{animation:fadeIn .5s ease-out .2s both!important}}
  .ov.sd .sdrt{{animation:none!important}}
  .ov.sd .sdt{{animation:none!important;opacity:1;transform:none;filter:none}}
  .ov.sd .sdlogo{{animation:sdDim .5s ease-in 1.15s forwards!important;transform:none}}
  .ov.sd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
