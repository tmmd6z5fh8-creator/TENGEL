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
   押した あと（0秒＝押した 瞬間）：
     ① 紫の 炎（0〜1.5秒）：紫の 夜に 金の 水晶の かけら → 黒い 馬の 影が ぐっと 寄って 立ち上がる → 十字の 光が 2回 → 目が 赤く 光って 炎が 紫から 赤へ → 炎の 中を「的中」の 字が ただよう
     ② GIF の 21コマ（1.5〜5.86秒：秒は GIF の 長さ。0.08秒の コマは 0.1秒）：
        GIF 0（1.5〜1.7）白黒の 煙・白い 線の「的中」・黒い 馬・虹色の 光の 筋 → GIF 1（1.7〜1.94）赤い 炎の 馬が 横に ずれる バグ → GIF 2（1.94〜2.14）炎の 場面に 桃色の 雷
        → GIF 3（2.14〜2.24）光る 目の ドアップに 黒い 切り裂きと 黄色い 光 → GIF 4（2.24〜2.36）目の ドアップ → GIF 5（2.36〜2.46）赤黒い 画面を 白い 裂け目が 裂く
        → GIF 6（2.46〜2.58）青と 黒の 画面を 黒い 裂け目が 裂く → GIF 7〜15（2.58〜4.7）割れた 鏡の かけらの 世界（左から 金の 炎の 流れが まん中の ピンクの 光へ・左に 虹色の プリズム・右下に 赤い 目の 黒い 馬・寄って いく）
        → GIF 16（4.7〜4.82）白と 水色に 反転した かけらと 黒い 穴 → GIF 17（4.82〜4.92）黒い 穴と 銀の かけら → GIF 18（4.92〜5.02）黒の 中に 金の 小さな 光
        → GIF 19〜20（5.02〜5.86）暗い 緑に 金の 輪と 横に 伸びる 光（だんだん 強く）。GIF 16〜20 は 左右に 炎の 柱
     ③ ど！！！的中（5.86秒〜）：光が 弾けて、その 中から「ど」「！」×3（上から 下へ 小さく）「的中」が 白熱の まま 画面から 出てきて 金と 虹に 冷める（6.42秒）
        → ロゴ 全体に 雷を まとう（ずっと ジリジリ）・不定期に 大きな 雷が 画面の 全方位へ → 8.64秒 ボード
   絵（ios/fx_assets の sd_….webp・id は shiden_blobs.json・大きさは shiden_layers.json）：① と ロゴは flat/shiden_art.py、② は flat/shiden_cuts.py。ほかは CSS と SVG
   点めつ：② の コマの 切りかえは GIF の 長さ（0.1〜0.24秒）。どの 1点も 1秒に 3回 以下（test_fx_flash.py sd で 確かめる）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/shiden_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0
CX = 195.0

# ---------------------------------------------------------------- 時刻（秒・押した 瞬間が 0）
SD_T = dict(A=(0.0, 2.14),                      # ① 紫の 炎（見える 間：GIF 2 の 終わりまで）
            HORSE=(0.0, .38),                   # 馬の 影が 寄って 止まる
            CROSS=(.72, .98),                   # 十字の 光 2回（目・画面の まん中）
            EYES=1.18,                          # 目が 赤く 光る → 炎が 赤へ（EYES〜EYES+.6 で 入れかわる）
            GLY=(1.05, 2.1),                    # 「的中」の 字が ただよう（出はじめ・おわり）
            C0=(1.5, 1.7),                      # GIF 0：白黒の 煙・虹色の 光の 筋
            C1=(1.7, 1.94),                     # GIF 1：横に ずれる バグ
            LT=(1.94, 2.14),                    # GIF 2：炎の 場面に 桃色の 雷
            EYE=(2.14, 2.24, 2.36),             # GIF 3（切り裂き つき）・GIF 4
            C5=(2.36, 2.46),                    # GIF 5：赤黒い 画面・白い 裂け目
            C6=(2.46, 2.58),                    # GIF 6：青と 黒の 画面・黒い 裂け目
            W=(2.58, 4.7),                      # GIF 7〜15：割れた 鏡の かけらの 世界
            C16=(4.7, 4.82), C17=(4.82, 4.92), C18=(4.92, 5.02),   # GIF 16・17・18
            C19=(5.02, 5.86),                   # GIF 19〜20：暗い 緑・金の 輪・横の 光
            GF=(5.86, 5.94, 6.36, 6.69),        # 光が 弾ける（金色の 光：出る・いちばん・ロゴが 出きる まで そのまま・消える）
            C=5.86,                             # ③ の はじまり
            LOGO=5.98, EMERGE=.44,              # ど！！！的中が 光の 中から 出てくる（はじまり・かかる 時間）
            LAND=6.42,                          # 出きった 瞬間（ドンッ：揺れ・金の 粒）
            ARCS=(6.34, 9.04),                  # ロゴに まとう 電気（ずっと）
            BOLTS=((6.42, 2), (6.72, 1), (6.82, 2), (7.24, 1), (7.36, 1), (7.72, 2), (8.04, 1), (8.16, 2), (8.52, 1), (8.84, 1)),   # 大きな 雷（時刻・本数）：不定期
            RES=8.64)                           # ボード
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


def pink_bolts():
    """GIF 2：炎の 場面を 走る 桃色の 雷（3本・ちらつく）"""
    T = SD_T
    t0, t1 = T['LT']
    rng = random.Random(41)
    o = ''
    for (a, b) in (((-20, 120), (400, 610)), ((300, -20), (120, 860)), ((410, 300), (-20, 520))):
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
    return f'<svg class="sdpb" viewBox="0 0 390 844" aria-hidden="true" style="animation:sdPb {sec(t1 - t0)} steps(2,jump-none) {sec(t0)} both{hide(t0, t1)}">{o}</svg>'


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
      {_img('sd_horse', x0, y0, w, None, 'sdho', f'animation:sdHo {sec(h1 - h0)} cubic-bezier(.15,.75,.3,1) {sec(h0)} both,sdBr 1.3s ease-in-out {sec(h1)} infinite alternate')}
      <i class="sdey" style="left:{ex - 46:.0f}px;top:{ey - 46:.0f}px;animation:sdEy .5s ease-out {sec(T['EYES'])} both,sdEyP .9s ease-in-out {sec(T['EYES'] + .5)} infinite alternate{hide(T['EYES'])}"></i>
      <div class="sdgl">{glyphs()}</div>
      {cross(ex, ey, 440, c1, .3)}
      {cross(CX, 430, 980, c2, .36, ' big')}
    </div>'''


# ---------------------------------------------------------------- ② 送ってくれた GIF の 1コマずつ（第4.68版）
def cut(name, t0, t1, cls='', anim=''):
    """1コマの 絵（画面 いっぱい）：t0 に 出て t1 に 消える（anim＝ほかの 動き）"""
    return _img(name, 0, 0, W_, H_, 'sdcut' + (' ' + cls if cls else ''), f'animation:sdIn .001s linear {sec(t0)} both{anim}{hide(t0, t1)}')


def slash_svg():
    """GIF 3：目の ドアップを ななめに 走る 黒い 切り裂き（ギザギザ）と 黄色い 光の 筋"""
    rng = random.Random(43)
    top = _disp(rng, (-30, 300), (420, 70), (.03, .05, .06))
    bot = _disp(rng, (-30, 352), (420, 110), (.03, .05, .06))
    poly = ' '.join(f'{x:.0f},{y:.0f}' for x, y in top + bot[::-1])
    return (f'<polygon points="{poly}" fill="#000"/>'
            f'<path d="M-30 690 L420 330" stroke="#FFF2B0" stroke-width="16" stroke-opacity=".35" stroke-linecap="round"/>'
            f'<path d="M-30 690 L420 330" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>')


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


def scene_b():
    """② GIF の 1コマずつ（GIF 2 の 間は ① の 場面に 桃色の 雷：scene_a）"""
    T = SD_T
    c0, c1 = T['C0'], T['C1']
    e0, e1, e2 = T['EYE']
    w0, w1 = T['W']
    c18, c19 = T['C18'], T['C19']
    p0, p1 = T['C16'][0], T['GF'][1]
    c5, c17 = T['C5'], T['C17']
    o = f'<div class="sdB" aria-hidden="true" style="animation:sdIn .001s linear {sec(c0[0])} both{hide(c0[0], T["GF"][1])}">'
    o += (f'<div class="sdc0" style="animation:sdIn .001s linear {sec(c0[0])} both{hide(c0[0], c0[1])}">'
          + _img('sd_c0', 0, 0, W_, H_, 'sdcut', f'animation:sdC0z {sec(c0[1] - c0[0])} linear {sec(c0[0])} both')
          + _img('sd_rbs', -30, 0, W_ + 60, H_, 'sdrbs', f'animation:sdRbs {sec(c0[1] - c0[0])} linear {sec(c0[0])} both')
          + '</div>')
    o += _img('sd_c1', -12, 0, W_ + 24, H_, 'sdcut', f'animation:sdIn .001s linear {sec(c1[0])} both{hide(c1[0], c1[1])}')     # ゆらさない（点めつ）
    lt = T['LT']
    o += (f'<div class="sdc2" style="animation:sdIn .001s linear {sec(lt[0])} both{hide(lt[0], lt[1])}">'
          + _img('sd_c2', 0, 0, W_, H_, 'sdcut', f'animation:sdC0z {sec(lt[1] - lt[0])} linear {sec(lt[0])} both') + pink_bolts() + '</div>')
    o += (f'<div class="sdeye" style="animation:sdEyeZ {sec(e2 - e0)} linear {sec(e0)} both{hide(e0, e2)}">'
          + _img('sd_eye', 0, 0, W_, H_, 'sdcut')
          + f'<svg class="sdslash" viewBox="0 0 390 844" aria-hidden="true" style="animation:sdIn .001s linear {sec(e0)} both{hide(e0, e1)}">{slash_svg()}</svg>'
          + '</div>')
    o += cut('sd_c5', *c5)
    o += cut('sd_c6', *T['C6'])
    wa = f'{sec(w1 - w0)} cubic-bezier(.3,.2,.6,1) {sec(w0)} both'
    o += (f'<div class="sdw" style="animation:sdIn .001s linear {sec(w0)} both{hide(w0, w1)}">'
          + _img('sd_w_bg', 0, 0, W_, H_, 'sdwbg', f'animation:sdWz {wa}')
          + _img('sd_w_fire1', -20, 0, W_ + 40, H_, 'sdwf', f'animation:sdWf {wa},sdWf1 .9s ease-in-out {sec(w0)} infinite alternate')
          + _img('sd_w_fire2', -20, 0, W_ + 40, H_, 'sdwf', f'animation:sdWf {wa},sdWf2 .9s ease-in-out {sec(w0)} infinite alternate')
          + _img('sd_w_prism', 0, 0, W_, H_, 'sdwpr', f'animation:sdWz {wa},sdPr .6s ease-in-out {sec(w0)} infinite alternate')
          + f'<i class="sdcore" style="animation:sdCore .5s ease-in-out {sec(w0)} infinite alternate"></i>'
          + f'<div class="sdwsp">{world_sparks()}</div>'
          + _img('sd_w_near', 0, 0, W_, H_, 'sdwn', f'animation:sdWn {sec(w1 - w0)} cubic-bezier(.3,.1,.7,1) {sec(w0)} both')
          + '</div>')
    o += cut('sd_c16', *T['C16'])
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
    <p class="sr">ど的中！紫の 炎の 中に 黒い 馬の 影が 立ち上がり、目が 赤く 光る。白黒の 煙と 虹色の 光・桃色の 雷・光る 目・赤と 青の 裂け目・割れた 鏡の 世界の 金の 炎・黒い 穴・緑の 光の 輪。光が 弾けて「ど！！！的中」が 雷を まとって 出てくる</p>'''


def sd_css():
    T = SD_T
    g0, g1, g2, g3 = T['GF']
    gd = g3 - g0
    e0 = T['EYES']
    a0, a1 = T['A']
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
@keyframes sdPb{{0%{{opacity:1}}50%{{opacity:.55}}100%{{opacity:1}}}}
/* ② GIF の 1コマずつ */
.ov.sd .sdcut{{transform-origin:50% 50%}}
@keyframes sdC0z{{from{{transform:scale(1.04)}}to{{transform:scale(1)}}}}
.ov.sd .sdrbs{{opacity:.95}}
@keyframes sdRbs{{from{{transform:translate(-26px,14px)}}to{{transform:translate(26px,-14px)}}}}
.ov.sd .sdeye{{transform-origin:40% 45%}}
@keyframes sdEyeZ{{from{{transform:scale(1)}}to{{transform:scale(1.07)}}}}
.ov.sd .sdslash{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.sd .sdw{{overflow:hidden}}
.ov.sd .sdwbg,.ov.sd .sdwpr{{transform-origin:50% 51%}}
@keyframes sdWz{{from{{transform:scale(1) rotate(-1.2deg)}}to{{transform:scale(1.13) rotate(1.2deg)}}}}
@keyframes sdPr{{from{{opacity:.75}}to{{opacity:1}}}}
.ov.sd .sdwf{{transform-origin:50% 51%}}
@keyframes sdWf{{from{{transform:translateX(-8px) scale(1)}}to{{transform:translateX(6px) scale(1.12)}}}}
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
