"""ど的中・紫電（しでん・sd）：ど的中の 新しい 演出（第4.66版・まさちゃんの 指定）。
   まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出 圧倒的な迫力 見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   送ってくれた 動画（パチンコの 当たりの 演出）は 流れ・色・迫力の 見本に するだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
   人物の 代わりは テンゲルの 馬（後ろ足で 立ち上がる 黒い 馬の 影）。絵（flat/shiden_art.py）・音（gen_sfx.py の sfx_sd）は 一から 作る。
   第4.67版・まさちゃん「一枚目から二枚目までのシーンを無くして、…三枚目から四枚目までの画像を確認して、フレーム数を増やしていいから画面を切り裂いて、虹色、白、青、黒が入れ替わり入って激しく
   最後の光が弾けて、ど！！！的中が画面から出てくるように作成して！ ど！！！的中は、もっと全体的に雷を纏って激しく、不定期にど！！！的中にまとった雷が画面の全方位にビリビリと届く演出も入れて」
   → ②の「金の 光の 筋の ため」と「砕けて ロゴが 落ちて くる」を やめて、②を「切り裂き」に・ロゴは 光が 弾けた あとに 画面から 出てくる・雷を まとう
   押した あと（0秒＝押した 瞬間）：
     ① 紫の 炎（0〜2.9秒）：紫の 夜に 金の 水晶の かけら → 黒い 馬の 影が ぐっと 寄って 立ち上がる（紫の ふちの 光）→ 十字の 光が 2回 → 目が 赤く 光って 炎が 紫から 赤へ
        → 炎の 中を「的中」の 字が ただよって 上がる → 馬の 影が バグる（横に ずれる・色が ずれる・走査線）→ 墨が 画面を 黒く ぬる → 白
     ② 切り裂き（2.84〜4.75秒）：金と 虹の 光の 川が 横に 走る 暗い 画面（白い 馬の 影が にじむ）を、切り裂きが 次々に 走る：虹色・白・青・黒の 帯が 入れかわりに 画面を 切る（4つの 波・計 28本）
        → さいごの 波は 黒（画面が 黒に 沈む）→ ガラスが とびちる・金の 光の 線と 輪 → 光が 弾ける（金 → 白）
     ③ ど！！！的中（5.2秒〜）：弾けた 光の 中から「ど」「！」×3（上から 下へ 小さく）「的中」が 白熱の まま 画面から 出てきて、金と 虹の 色に 冷める（ドンッ：画面の 揺れ・金の 粒）
        → ロゴ 全体に 雷を まとう（ふちを はう 小さな 電気が ずっと ジリジリ）・不定期に 大きな 雷が ロゴから 画面の 全方位（上下左右の ふち）へ ビリビリと 届く → 脈うつ・火の 粉 → ボード（7.9秒）
   絵（ios/fx_assets の sd_….webp・id は shiden_blobs.json・大きさは shiden_layers.json）。ほかは CSS と SVG（十字の 光・走査線・切り裂き・ガラスの かけら・雷・光の 粒・火の 粉）
   点めつ：画面の 大きな 光は 白（①→②）・十字の 光（2回）・墨・光が 弾ける（金 → 白）だけ。切り裂きは 1本ごとに 画面の 一部だけを 切り、同じ 所は 1秒に 2〜3回しか 変わらない（波は 0.55秒ごと）。
   炎は 3まいを ゆっくり 入れかえる。雷は 細い 線（面積が 小さい）。どの 1点も 1秒に 3回 以下（test_fx_flash.py sd）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/shiden_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0
CX = 195.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
SD_T = dict(A=(0.0, 2.9),                       # ① 紫の 炎（見える 間）
            HORSE=(0.0, .38),                   # 馬の 影が 寄って 止まる
            CROSS=(.72, .98),                   # 十字の 光 2回（目・画面の まん中）
            EYES=1.18,                          # 目が 赤く 光る → 炎が 赤へ（EYES〜EYES+.6 で 入れかわる）
            GLY=(1.05, 2.75),                   # 「的中」の 字が ただよう（出はじめ・おわり）
            GLITCH=(1.56, 1.84),                # バグる 2回（それぞれ GL_D 秒）
            INK=2.32,                           # 墨（INK_D 秒で 広がって INK_H 秒 黒）
            WB=(2.78, 2.84, 2.9, 3.06),         # 白（① → ②）
            B=(2.84, 5.3),                      # ② 切り裂き（見える 間）
            WAVES=(3.0, 3.55, 4.1),             # 切り裂きの 波（虹色・白・青 の 入れかわり：1波 7本・SL_GAP 秒ずつ）
            BLACK=4.62,                         # さいごの 波：黒（画面が 黒に 沈む）
            SHAT=(4.74, 5.3),                   # ガラスの かけら（小さな 三角）が とびちる
            FLARE=(4.84, 5.42),                 # 金の 光の 線
            RING=(4.9, 5.32),                   # 金の 輪が ひろがる
            GF=(5.1, 5.18, 5.62, 5.95),         # 光が 弾ける（金色の 光：出る・いちばん・ロゴが 出きる まで そのまま・消える）
            C=5.1,                              # ③ の はじまり
            LOGO=5.24, EMERGE=.44,              # ど！！！的中が 光の 中から 出てくる（はじまり・かかる 時間）
            LAND=5.68,                          # 出きった 瞬間（ドンッ：揺れ・金の 粒）
            ARCS=(5.6, 8.3),                    # ロゴに まとう 電気（ずっと）
            BOLTS=((5.68, 2), (5.98, 1), (6.08, 2), (6.5, 1), (6.62, 1), (6.98, 2), (7.3, 1), (7.42, 2), (7.78, 1), (8.1, 1)),   # 大きな 雷（時刻・本数）：不定期
            RES=7.9)                            # ボード
GL_D, INK_D, INK_H = .14, .16, .22              # バグる 1回の 長さ・墨が 広がる 時間・黒い 時間
SL_N, SL_GAP, SL_D = 7, .055, .06               # 切り裂き：1波の 本数・1本ごとの ずれ・1本が 切れて 色が つく まで
AR_DT = .085                                    # まとう 電気の 1コマ
# ロゴの 置き場所（まん中の x・y・絵の 表示の 幅）：絵は 字の まわりに 光の あきが ある（shiden_art.py の pad）ので、字より 大きい
LOGO = dict(sd_t_do=(150.0, 232.0, 400.0), e1=(305.0, 212.0, 278.0), e2=(323.0, 336.0, 196.0), e3=(336.0, 420.0, 130.0), sd_t_hit=(CX, 586.0, 474.0))
HORSE_A = (30.0, 240.0, 330.0)                  # ① の 馬：left・top・幅
HIT_C = (CX, 586.0)                             # 「的中」の まん中（金の 粒・金の 光・雷の もと）


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def hide(t0=None, t1=None):
    """見えない 間は 描かない（出る 前・消えた あと）：animation に 足す 文（先頭に ,）"""
    o = ''
    if t0 is not None:
        o += f',sdH .001s linear {sec(t0)} backwards'
    if t1 is not None:
        o += f',sdH .001s linear {sec(t1)} forwards'
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


def glitch():
    """馬の 影が バグる（GLITCH の 2回）：横に 切った 帯が 左右に ずれる（色も ずれる）＋ 赤と 水色の ずれた 影 ＋ 走査線。ずれは 小さめ（点めつの 面積を 小さく）"""
    T = SD_T
    x0, y0, w = HORSE_A
    h = w * LAY['sd_horse']['h'] / LAY['sd_horse']['w']
    rng = random.Random(7)
    o = ''
    for gi, t in enumerate(T['GLITCH']):
        # 帯：馬の 高さを 9つに 切る（高さは ばらばら）
        cuts = sorted([0.0, 1.0] + [rng.random() for _ in range(8)])
        for a, b in zip(cuts, cuts[1:]):
            if b - a < .02:
                continue
            dx = rng.choice((-1, 1)) * rng.uniform(5, 15)
            o += (f'<img class="sdgs" src="{blob("sd_horse")}" alt="" style="left:{x0:.0f}px;top:{y0:.0f}px;width:{w:.0f}px;height:{h:.1f}px;'
                  f'clip-path:inset({a * h:.1f}px 0 {(1 - b) * h:.1f}px 0);--dx:{dx:.0f}px;--hue:{rng.uniform(-70, 70):.0f}deg;'
                  f'animation:sdGs {sec(GL_D)} steps(4,jump-none) {sec(t)} both{hide(t, t + GL_D)}">')
        for cls, dx in (('r', 7), ('c', -7)):
            o += (f'<img class="sdrgb {cls}" src="{blob("sd_horse")}" alt="" style="left:{x0 + dx:.0f}px;top:{y0 + (2 if cls == "r" else -2):.0f}px;width:{w:.0f}px;height:{h:.1f}px;'
                  f'animation:sdIn .001s linear {sec(t)} both{hide(t, t + GL_D)}">')
        for _ in range(5):
            y = rng.uniform(80, 800)
            o += (f'<i class="sdsb" style="top:{y:.0f}px;height:{rng.uniform(2, 7):.0f}px;--o:{rng.uniform(.25, .5):.2f};'
                  f'animation:sdSb {sec(GL_D)} steps(3,jump-none) {sec(t + rng.uniform(0, .03))} both{hide(t, t + GL_D + .03)}"></i>')
    return o


def scene_a():
    T = SD_T
    a0, a1 = T['A']
    h0, h1 = T['HORSE']
    c1, c2 = T['CROSS']
    ex, ey = eye_pos()
    x0, y0, w = HORSE_A
    i0 = T['INK']
    return f'''<div class="sdA" aria-hidden="true" style="animation:sdIn .001s linear 0s both{hide(None, T['WB'][1])}">
      {_img('sd_bg', -20, -40, W_ + 40, H_ + 80, 'sdbg', f'animation:sdBg {sec(a1 - a0)} linear 0s both')}
      <i class="sdau"></i>
      {fires()}
      {_img('sd_horse', x0, y0, w, None, 'sdho', f'animation:sdHo {sec(h1 - h0)} cubic-bezier(.15,.75,.3,1) {sec(h0)} both,sdBr 1.3s ease-in-out {sec(h1)} infinite alternate')}
      <i class="sdey" style="left:{ex - 46:.0f}px;top:{ey - 46:.0f}px;animation:sdEy .5s ease-out {sec(T['EYES'])} both,sdEyP .9s ease-in-out {sec(T['EYES'] + .5)} infinite alternate{hide(T['EYES'])}"></i>
      <div class="sdgl">{glyphs()}</div>
      {glitch()}
      {cross(ex, ey, 440, c1, .3)}
      {cross(CX, 430, 980, c2, .36, ' big')}
      <i class="sdink" style="animation:sdInk {sec(INK_D + INK_H + .14)} linear {sec(i0)} both{hide(i0, i0 + INK_D + INK_H + .14)}"></i>
    </div>'''


# ---------------------------------------------------------------- ② 切り裂き（虹色・白・青・黒が 入れかわりに 画面を 切る）
SL_COLORS = (('rb', 'wh', 'bl', 'rb', 'wh', 'rb', 'bl'), ('bl', 'rb', 'wh', 'bl', 'rb', 'bk', 'wh'), ('wh', 'bl', 'rb', 'wh', 'bk', 'rb', 'bl'))   # 波ごとの 色の 順（rb＝虹色・wh＝白・bl＝青・bk＝黒）
SL_ANG = ((-28, -22, -34, -18, -30, -25, -36), (62, 70, 55, 66, 74, 58, 68), (24, 30, 18, 34, 27, 21, 38))                                     # 波ごとの 角度（度・横が 0）：波の 中は 同じ 向きの 扇で、波ごとに 向きを かえる


SL_SHAPES = ('polygon(0 50%,9% 0,100% 20%,100% 80%,9% 100%)', 'polygon(0 18%,100% 0,100% 58%,90% 100%,0 82%)', 'polygon(0 0,100% 28%,100% 72%,0 100%)',
             'polygon(0 30%,8% 0,100% 50%,8% 100%,0 70%)', 'polygon(0 40%,100% 0,94% 100%,0 60%)')      # 切り裂きの 形（先が 細い 刃の あと：帯の 箱の 中の %）


def slashes():
    """切り裂き：波ごとに 7本の 刃の あと（同じ 向きの 扇・画面を だいたい 1回 おおう）が SL_GAP 秒ずつ 走る。
       1本＝まわした 細長い 箱（刃の あとの 形に 切りぬく）が、切れた 瞬間に 線から 開いて（scaleY 0 → 1）色（虹色・白・青・黒）が つく。上の ふちに 白い 刃の 光。
       同じ 所を 切るのは 波ごとに 1本くらい（帯の 幅 64〜118px・7等分の 間は 106〜133px：点めつ＝1点の 明るさの 変化は 1秒に 2〜4回）。さいごの 波（BLACK）は 黒だけ 7本（幅 120〜190px・画面が 黒に 沈む）。
       白い つや（左から 右へ 走る 光）は 点めつが 増えるので 入れない"""
    T = SD_T
    rng = random.Random(31)
    o = ''
    waves = [(t, SL_COLORS[k], SL_ANG[k]) for k, t in enumerate(T['WAVES'])] + [(T['BLACK'], ('bk',) * SL_N, (-40, 50, -10, 80, 20, -65, 35))]
    BW = 1400.0
    for wi, (t0, cols, angs) in enumerate(waves):
        order = list(range(SL_N))
        rng.shuffle(order)
        for n, k in enumerate(order):
            # 位置：扇の 向きに 直交する 方向に 画面を 7等分 した あたり（少し ばらす）
            u = (k + .5) / SL_N + rng.uniform(-.06, .06)
            a = math.radians(angs[k])
            nx, ny = -math.sin(a), math.cos(a)
            span = abs(nx) * W_ + abs(ny) * H_
            cx, cy = CX + nx * (u - .5) * span, 430.0 + ny * (u - .5) * span
            w = rng.uniform(64, 118) if cols[k] != 'bk' else rng.uniform(120, 190)
            t = t0 + n * SL_GAP
            shape = SL_SHAPES[rng.randrange(len(SL_SHAPES))]
            flip = rng.random() < .5
            o += (f'<i class="sdsl {cols[k]}" style="left:{cx - BW / 2:.0f}px;top:{cy - w / 2:.0f}px;width:{BW:.0f}px;height:{w:.0f}px;--a:{angs[k] + (180 if flip else 0)}deg;clip-path:{shape};'
                  f'--bx:{rng.uniform(0, 100):.0f}% {rng.uniform(0, 100):.0f}%;animation:sdSl {sec(SL_D)} cubic-bezier(.2,.9,.3,1) {sec(t)} both{hide(t)}">'
                  f'<b class="ed" style="animation:sdEd .26s linear {sec(t)} both"></b></i>')
    return o


def rings(times):
    return ''.join(f'<i class="sdrg" style="animation:sdRg .7s cubic-bezier(.1,.6,.3,1) {sec(t)} both{hide(t, t + .7)}"></i>' for t in times)


def scene_b():
    """② 切り裂き：暗い 画面に 金と 虹の 光の 川（横に 流れる）・白く にじむ 馬の 影（色の ずれた 影 2つ）→ 切り裂きの 波 → 黒 → ガラスの かけら・金の 光の 線・金の 輪 → 光が 弾ける"""
    T = SD_T
    b0, b1 = T['B']
    hw = 380.0
    hh = hw * LAY['sd_horse']['h'] / LAY['sd_horse']['w']
    f0, f1 = T['FLARE']
    r0, r1 = T['RING']
    return f'''<div class="sdB" aria-hidden="true" style="animation:sdIn .001s linear {sec(b0)} both{hide(b0, T['GF'][1])}">
      <i class="sdbb"></i>
      <i class="sdstm" style="--img:url({blob('sd_stream')});--sw:{LAY['sd_stream']['w']:g}px;--sh:{LAY['sd_stream']['h']:g}px"></i>
      {_img('sd_horse', CX - hw / 2 + 9, 430 - hh / 2 + 4, hw, hh, 'sdgh c')}
      {_img('sd_horse', CX - hw / 2 - 9, 430 - hh / 2 - 4, hw, hh, 'sdgh m')}
      {_img('sd_horse', CX - hw / 2, 430 - hh / 2, hw, hh, 'sdgh w')}
      <div class="sdsls">{slashes()}</div>
      <div class="sdsh">{shards()}</div>
      {_img_c('sd_flare', CX, 430, 560.0, 'sdfr', f'animation:sdFr {sec(f1 - f0)} cubic-bezier(.2,.7,.3,1) {sec(f0)} both{hide(f0, f1)}')}
      {rings((r0, r0 + .14, r0 + .28))}
    </div>'''


# ---------------------------------------------------------------- ③ ど！！！的中（光の 中から 出てくる・雷を まとう）
def shards(n=18, seed=11, cx=CX, cy=430.0):
    """ガラスの かけら：まん中から 外へ とびちる 小さな 三角（40〜130px・clip-path）。まわりながら 遠ざかって 消える。
       画面 ぜんぶを おおう 大きな くさびは やめた（同じ 所を 何度も 明るく したり 暗く したり して 点めつに なる）"""
    T = SD_T
    s0, s1 = T['SHAT']
    rng = random.Random(seed)
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rng.uniform(-.3, .3)) / n
        r0 = rng.uniform(20, 90)
        px, py = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
        L = rng.uniform(40, 130)
        w = L * rng.uniform(.25, .55)
        ang = a + rng.uniform(-.4, .4)
        tip = (px + L * math.cos(ang), py + L * math.sin(ang))
        nx, ny = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
        pts = ((px + nx, py + ny), tip, (px - nx, py - ny))
        poly = ','.join(f'{x:.0f}px {y:.0f}px' for x, y in pts)
        dist = rng.uniform(260, 520)
        dl = s0 + rng.uniform(0, .06)
        dur = s1 - dl
        o += (f'<i style="clip-path:polygon({poly});--x:{dist * math.cos(a):.0f}px;--y:{dist * math.sin(a):.0f}px;--r:{rng.uniform(-90, 90):.0f}deg;--o:{rng.uniform(.8, 1):.2f};'
              f'animation:sdSh {sec(dur)} cubic-bezier(.2,.5,.6,1) {sec(dl)} both{hide(dl, dl + dur)}"></i>')
    return o


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


# ---------------------------------------------------------------- 白い 光・層
def white(cls, w):
    t0, t1, t2, t3 = w
    d = t3 - t0
    return (f'<div class="sdw" aria-hidden="true" style="animation:sdW{cls} {sec(d)} linear {sec(t0)} both{hide(t0, t3)}"></div>',
            f'@keyframes sdW{cls}{{0%{{opacity:0}}{(t1 - t0) / d * 100:.1f}%{{opacity:1}}{(t2 - t0) / d * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}')


WHITES = (('b', 'WB'),)


def sd_layers(board_html):
    """押したあと（下から）：① 紫の 炎 → ② 切り裂き → ③ 光が 弾けて ど！！！的中（雷を まとう）→ 白い 光 → ボード（board_html）"""
    T = SD_T
    wh = ''.join(white(k, T[n])[0] for k, n in WHITES)
    return f'''<div class="sdk" aria-hidden="true"></div>
    {scene_a()}
    {scene_b()}
    {scene_c()}
    {wh}
    <div class="hb">{board_html}</div>
    <p class="sr">ど的中！紫の 炎の 中に 黒い 馬の 影が 立ち上がり、目が 赤く 光る。画面が バグって 墨に 沈み、虹色・白・青・黒の 切り裂きが 走る。光が 弾けて「ど！！！的中」が 雷を まとって 出てくる</p>'''


def sd_css():
    T = SD_T
    wk = '\n'.join(white(k, T[n])[1] for k, n in WHITES)
    g0, g1, g2, g3 = T['GF']
    gd = g3 - g0
    e0 = T['EYES']
    a0, a1 = T['A']
    ink_tot = INK_D + INK_H + .14
    return f'''
/* ---------- ど的中・紫電（sd）：shiden.py（絵は flat/shiden_art.py・十字の 光・走査線・切り裂き・ガラスの かけら・雷・光の 粒・火の 粉は CSS と SVG） ---------- */
.ov.fz.sd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes sdH{{0%,100%{{visibility:hidden}}}}
@keyframes sdIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes sdFk{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdk{{position:absolute;inset:0;background:#050208}}
.ov.sd .sdA,.ov.sd .sdB,.ov.sd .sdC{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}
.ov.sd img{{position:absolute;display:block;max-width:none}}
.ov.sd .sdA i,.ov.sd .sdB i,.ov.sd .sdC i{{position:absolute;display:block}}
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
.ov.sd .sdgs{{filter:hue-rotate(var(--hue))}}
@keyframes sdGs{{0%{{transform:translateX(var(--dx))}}50%{{transform:translateX(calc(var(--dx) * -.7))}}100%{{transform:translateX(calc(var(--dx) * .4))}}}}
.ov.sd .sdrgb{{opacity:.55;mix-blend-mode:screen}}
.ov.sd .sdrgb.r{{filter:brightness(1.4) sepia(1) saturate(9) hue-rotate(-40deg)}}
.ov.sd .sdrgb.c{{filter:brightness(1.4) sepia(1) saturate(9) hue-rotate(140deg)}}
.ov.sd .sdsb{{left:0;width:100%;background:rgba(150,220,255,var(--o))}}
@keyframes sdSb{{0%{{transform:translateY(0)}}100%{{transform:translateY(-40px)}}}}
.ov.sd .sdcx{{opacity:0;border-radius:50%;transform-origin:50% 50%;
  background:linear-gradient(90deg,transparent 48.6%,#FFFFFF 50%,transparent 51.4%),linear-gradient(0deg,transparent 48.6%,#FFFFFF 50%,transparent 51.4%),
  linear-gradient(45deg,transparent 49.4%,rgba(255,255,255,.7) 50%,transparent 50.6%),linear-gradient(-45deg,transparent 49.4%,rgba(255,255,255,.7) 50%,transparent 50.6%),
  radial-gradient(circle,#FFFFFF 0 3%,rgba(255,230,255,.85) 7%,rgba(220,150,255,.35) 16%,rgba(180,80,255,0) 34%)}}
.ov.sd .sdcx.big{{background:linear-gradient(90deg,transparent 48.8%,#FFFFFF 50%,transparent 51.2%),linear-gradient(0deg,transparent 48.8%,#FFFFFF 50%,transparent 51.2%),
  radial-gradient(circle,#FFFFFF 0 5%,rgba(255,240,255,.9) 10%,rgba(230,170,255,.45) 20%,rgba(180,80,255,0) 38%)}}
@keyframes sdCx{{0%{{opacity:0;transform:scale(.25) rotate(-8deg)}}30%{{opacity:1}}100%{{opacity:0;transform:scale(1.25) rotate(6deg)}}}}
.ov.sd .sdink{{inset:0;opacity:0;transform-origin:46% 52%;
  background:radial-gradient(circle at 30% 38%,#000 0 30%,transparent 36%),radial-gradient(circle at 72% 58%,#000 0 34%,transparent 40%),radial-gradient(circle at 50% 50%,#000 0 42%,transparent 50%),radial-gradient(circle at 58% 22%,#000 0 22%,transparent 28%),radial-gradient(circle at 36% 78%,#000 0 26%,transparent 32%),
  radial-gradient(circle at 14% 58%,#000 0 14%,transparent 19%),radial-gradient(circle at 84% 30%,#000 0 12%,transparent 17%),radial-gradient(circle at 66% 86%,#000 0 16%,transparent 21%),radial-gradient(circle at 22% 14%,#000 0 10%,transparent 14%),radial-gradient(circle at 90% 78%,#000 0 9%,transparent 13%)}}
@keyframes sdInk{{0%{{opacity:1;transform:scale(.3) rotate(-14deg)}}{INK_D / ink_tot * 100:.1f}%{{opacity:1;transform:scale(1.7) rotate(0)}}{(INK_D + INK_H) / ink_tot * 100:.1f}%{{opacity:1;transform:scale(1.9) rotate(2deg)}}100%{{opacity:0;transform:scale(2) rotate(2deg)}}}}
/* 白い 光 */
.ov.sd .sdw{{position:absolute;inset:0;background:#FFFFFF;opacity:0;pointer-events:none;z-index:8}}
{wk}
/* ② 切り裂き：金と 虹の 光の 川・白く にじむ 馬の 影・虹色／白／青／黒の 帯・ガラスの かけら・金の 光の 線・輪 */
.ov.sd .sdbb{{inset:0;background:radial-gradient(ellipse 70% 55% at 50% 51%,#140826,#0A0314 55%,#030108)}}
.ov.sd .sdstm{{left:0;top:280px;width:100%;height:300px;background:var(--img) 0 50%/{LAY['sd_stream']['w'] * 300 / LAY['sd_stream']['h']:.0f}px 300px repeat-x;animation:sdStm 1.9s linear infinite;opacity:.95}}
@keyframes sdStm{{to{{background-position:-{LAY['sd_stream']['w'] * 300 / LAY['sd_stream']['h']:.0f}px 50%}}}}
.ov.sd .sdgh{{transform-origin:50% 50%;animation:sdGh 2.6s ease-in-out infinite alternate}}
.ov.sd .sdgh.w{{filter:grayscale(1) invert(1) brightness(1.1) contrast(1.2);opacity:.42;mix-blend-mode:screen}}
.ov.sd .sdgh.c{{filter:grayscale(1) invert(1) sepia(1) saturate(6) hue-rotate(150deg);opacity:.3;mix-blend-mode:screen;animation-delay:-.9s}}
.ov.sd .sdgh.m{{filter:grayscale(1) invert(1) sepia(1) saturate(6) hue-rotate(260deg);opacity:.3;mix-blend-mode:screen;animation-delay:-1.7s}}
@keyframes sdGh{{from{{transform:scale(1) translateX(0)}}to{{transform:scale(1.06) translateX(6px)}}}}
.ov.sd .sdsls{{position:absolute;inset:0}}
.ov.sd .sdsl{{opacity:0;transform-origin:50% 50%;overflow:hidden}}
.ov.sd .sdsl b{{position:absolute;display:block}}
.ov.sd .sdsl.rb{{background:url({blob('sd_rtex')}) var(--bx)/620px 1340px}}
.ov.sd .sdsl.wh{{background:linear-gradient(90deg,#FFFFFF,#F2F8FF 40%,#FFFFFF 70%,#E8F0FF)}}
.ov.sd .sdsl.bl{{background:repeating-linear-gradient(-30deg,rgba(255,255,255,.35) 0 2px,rgba(255,255,255,0) 2px 11px),linear-gradient(90deg,#1437FF,#3A8CFF 35%,#0B1CB8 60%,#6CD4FF)}}
.ov.sd .sdsl.bk{{background:#000}}
@keyframes sdSl{{0%{{opacity:1;transform:rotate(var(--a)) scaleY(.03)}}100%{{opacity:1;transform:rotate(var(--a)) scaleY(1)}}}}
.ov.sd .sdsl .ed{{left:0;right:0;top:0;height:3px;background:#FFFFFF;box-shadow:0 0 8px 3px rgba(255,255,255,.9)}}
@keyframes sdEd{{0%,45%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdsh{{position:absolute;inset:0}}
.ov.sd .sdsh i{{inset:0;opacity:0;transform-origin:50% 51%;
  background:linear-gradient(135deg,rgba(255,255,255,.85),rgba(190,225,255,.45) 38%,rgba(255,236,170,.7) 70%,rgba(255,255,255,.85)),url({blob('sd_streaks')}) 50% 51%/1300px 1300px no-repeat,#1A0830}}
@keyframes sdSh{{0%{{opacity:var(--o);transform:translate(0,0) rotate(0) scale(1)}}100%{{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1.12)}}}}
.ov.sd .sdfr{{opacity:0;transform-origin:50% 50%;mix-blend-mode:screen}}
@keyframes sdFr{{0%{{opacity:0;transform:scaleX(.1) scaleY(.6)}}25%{{opacity:1;transform:scaleX(1.25) scaleY(1)}}100%{{opacity:0;transform:scaleX(1.9) scaleY(.7)}}}}
.ov.sd .sdrg{{left:50%;top:430px;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;border:2px solid rgba(255,225,150,.9);box-shadow:0 0 14px 3px rgba(255,190,70,.6),inset 0 0 10px 2px rgba(255,190,70,.4);opacity:0}}
@keyframes sdRg{{0%{{opacity:0;transform:scale(.2)}}15%{{opacity:1}}100%{{opacity:0;transform:scale(7)}}}}
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
  .ov.sd .sdA,.ov.sd .sdB,.ov.sd .sdw,.ov.sd .sdgf,.ov.sd .sdco,.ov.sd .sdbo,.ov.sd .sdem{{display:none}}
  .ov.sd .sdC{{animation:fadeIn .5s ease-out .2s both!important}}
  .ov.sd .sdrt{{animation:none!important}}
  .ov.sd .sdt{{animation:none!important;opacity:1;transform:none;filter:none}}
  .ov.sd .sdlogo{{animation:sdDim .5s ease-in 1.15s forwards!important;transform:none}}
  .ov.sd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
