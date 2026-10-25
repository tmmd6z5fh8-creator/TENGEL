"""ど的中・紫電（しでん・sd）：ど的中の 新しい 演出（第4.66版・まさちゃんの 指定）。
   まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出 圧倒的な迫力 見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   送ってくれた 動画（パチンコの 当たりの 演出）は 流れ・色・迫力の 見本に するだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
   人物の 代わりは テンゲルの 馬（後ろ足で 立ち上がる 黒い 馬の 影）。絵（flat/shiden_art.py）・音（gen_sfx.py の sfx_sd）は 一から 作る。
   押した あと（0秒＝押した 瞬間）：
     ① 紫の 炎（0〜2.85秒）：紫の 夜に 金の 水晶の かけら → 黒い 馬の 影が ぐっと 寄って 立ち上がる（紫の ふちの 光）→ 十字の 光が 2回 → 目が 赤く 光って 炎が 紫から 赤へ
        → 炎の 中を「的中」の 字が ただよって 上がる → 馬の 影が バグる（横に ずれる・色が ずれる・走査線）→ 墨が 画面を 黒く ぬる → 白
     ② 金の 光の 筋（2.85〜4.6秒）：金と 虹の 光の 筋が まん中から ひろがって、ぐんぐん 寄る（ため）。まん中の 光が 大きく なり、馬の 影が 手前へ とんでくる・光の 粒が 吸いこまれる・輪が ひろがる
     ③ 砕けて ロゴ（4.6秒〜）：白 → 画面が ガラスの ように 砕けて とびちる・金の 光の 線 → 虹の 布の 上に「ど」が ドンと 落ちて くる → 「！」が 上から 下へ 3つ・小さく なりながら → 「的中」が ドンッ（金の 光・金の 粒・雷）→ 「的中」が 脈うつ・火の 粉 → ボード
   絵（ios/fx_assets の sd_….webp・id は shiden_blobs.json・大きさは shiden_layers.json）。ほかは CSS と SVG（十字の 光・走査線・ガラスの かけら・雷・光の 粒・火の 粉）
   点めつ：画面の 大きな 光は 白（①→②・②→③）・十字の 光（2回）・墨・金の 光（的中）だけ。どの 1秒にも 3回 以下。炎は 3まいを ゆっくり 入れかえる（ぱらぱらと 切りかえない）"""
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
            WB=(2.78, 2.86, 2.92, 3.14),        # 白（① → ②）
            B=(2.84, 4.66),                     # ② 金の 光の 筋（見える 間）
            WC=(4.56, 4.63, 4.7, 4.98),         # 白（② → ③）
            C=4.6,                              # ③ の はじまり
            SHAT=(4.6, 5.45),                   # ガラスの かけらが とびちる
            FLARE=(4.62, 5.5),                  # 金の 光の 線
            DO=4.96, EX=(5.18, 5.33, 5.45),     # 「ど」・「！」×3
            HIT=5.78, GF=(5.76, 5.82, 5.9, 6.22),   # 「的中」・金の 光（出る・いちばん・まだ・消える）
            BOLTS=(6.26, 6.74, 7.2),            # 雷
            RES=7.6)                            # ボード
GL_D, INK_D, INK_H = .14, .16, .22              # バグる 1回の 長さ・墨が 広がる 時間・黒い 時間
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


# ---------------------------------------------------------------- ② 金の 光の 筋（ため）
def sparks(n=34, seed=5):
    """光の 粒が まん中へ 吸いこまれる"""
    rng = random.Random(seed)
    o = ''
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(300, 560)
        s = rng.uniform(2.5, 5.5)
        o += (f'<i style="left:{CX - s / 2:.1f}px;top:{430 - s / 2:.1f}px;width:{s:.1f}px;height:{s:.1f}px;--x:{d * math.cos(a):.0f}px;--y:{d * math.sin(a):.0f}px;'
              f'animation:sdSp {rng.uniform(.5, .8):.2f}s cubic-bezier(.5,0,.9,.6) {rng.uniform(0, .8):.2f}s infinite"></i>')
    return o


def rings(times):
    return ''.join(f'<i class="sdrg" style="animation:sdRg .7s cubic-bezier(.1,.6,.3,1) {sec(t)} both{hide(t, t + .7)}"></i>' for t in times)


def scene_b():
    T = SD_T
    b0, b1 = T['B']
    d = b1 - b0
    x0, y0, w = HORSE_A
    hw = 330.0
    hh = hw * LAY['sd_horse']['h'] / LAY['sd_horse']['w']
    S = 1100.0
    return f'''<div class="sdB" aria-hidden="true" style="animation:sdIn .001s linear {sec(b0)} both{hide(b0, T['WC'][1])}">
      <i class="sdbb"></i>
      {_img('sd_streaks', CX - S / 2, 430 - S / 2, S, S, 'sdst s1', f'animation:sdSt1 {sec(d)} cubic-bezier(.5,0,.85,.4) {sec(b0)} both')}
      {_img('sd_streaks', CX - S / 2, 430 - S / 2, S, S, 'sdst s2', f'animation:sdSt2 {sec(d)} cubic-bezier(.5,0,.85,.4) {sec(b0)} both')}
      <i class="sdcore" style="animation:sdCore {sec(d)} cubic-bezier(.6,0,.9,.5) {sec(b0)} both"></i>
      <div class="sdsp" style="animation:sdIn .001s linear {sec(b0)} both{hide(b0)}">{sparks()}</div>
      {rings((b0 + .1, b0 + .62, b0 + 1.12, b0 + 1.5))}
      {_img('sd_horse', CX - hw / 2, 430 - hh / 2, hw, hh, 'sdho2', f'animation:sdHo2 {sec(d)} cubic-bezier(.55,0,.9,.45) {sec(b0)} both')}
    </div>'''


# ---------------------------------------------------------------- ③ 砕けて ロゴ
def shards(n=14, seed=11, cx=CX, cy=430.0):
    """画面が ガラスの ように 砕ける：まん中から 外へ ひろがる くさび形の かけら（clip-path）が それぞれ 外へ とんで、まわって、消える"""
    T = SD_T
    s0, s1 = T['SHAT']
    rng = random.Random(seed)
    o = ''
    R = 760.0
    angs = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    for i in range(n):
        a0, a1 = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
        if a1 - a0 < .08:
            a1 = a0 + .08
        am = (a0 + a1) / 2
        pts = [(cx + rng.gauss(0, 10), cy + rng.gauss(0, 10)), (cx + R * math.cos(a0), cy + R * math.sin(a0))]
        for k in (1, 2):
            aa = a0 + (a1 - a0) * k / 3 + rng.uniform(-.03, .03)
            rr = R * rng.uniform(.82, 1.08)
            pts.append((cx + rr * math.cos(aa), cy + rr * math.sin(aa)))
        pts.append((cx + R * math.cos(a1), cy + R * math.sin(a1)))
        poly = ','.join(f'{x:.0f}px {y:.0f}px' for x, y in pts)
        dist = rng.uniform(380, 640)
        dl = s0 + rng.uniform(0, .06)
        dur = s1 - dl
        o += (f'<i style="clip-path:polygon({poly});--x:{dist * math.cos(am):.0f}px;--y:{dist * math.sin(am):.0f}px;--r:{rng.uniform(-70, 70):.0f}deg;--o:{rng.uniform(.75, 1):.2f};'
              f'animation:sdSh {sec(dur)} cubic-bezier(.3,.1,.7,.9) {sec(dl)} both{hide(dl, dl + dur)}"></i>')
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
    return 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts)


def bolts():
    """雷（BOLTS の 時刻）：「的中」の 上から 画面の 外へ・枝つき。白い しん・紫の 光"""
    T = SD_T
    rng = random.Random(3)
    o = ''
    ends = (((40, -20), (150, 470)), ((360, -20), (250, 470)), ((400, 300), (300, 560)))
    for t, (p0, p1) in zip(T['BOLTS'], ends):
        main = _disp(rng, p0, p1, (.3, .3, .35, .4, .4))
        paths = [_path(main)]
        for _ in range(3):
            i = rng.randrange(2, len(main) - 2)
            bx, by = main[i]
            L = rng.uniform(50, 130)
            ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + rng.choice((-1, 1)) * rng.uniform(.5, 1.1)
            paths.append(_path(_disp(rng, (bx, by), (bx + L * math.cos(ang), by + L * math.sin(ang)), (.4, .4, .4))))
        d = ''.join(f'<path d="{p}"/>' for p in paths)
        o += (f'<g class="sdbt" style="animation:sdBt .26s linear {sec(t)} both{hide(t, t + .26)}">'
              f'<g class="g1">{d}</g><g class="g2">{d}</g><g class="g3">{d}</g></g>')
    return f'<svg class="sdbo" viewBox="0 0 390 844" aria-hidden="true">{o}</svg>'


def coins(n=40, seed=17):
    """金の 粒（「的中」から とびちる）"""
    T = SD_T
    rng = random.Random(seed)
    cx, cy = HIT_C
    o = ''
    for i in range(n):
        a = 2 * math.pi * (i + rng.uniform(-.4, .4)) / n
        d = rng.uniform(170, 420)
        s = rng.uniform(5, 13)
        dl = T['HIT'] + rng.uniform(0, .05)
        dur = rng.uniform(.6, .95)
        o += (f'<i style="left:{cx - s / 2:.0f}px;top:{cy - s / 2:.0f}px;width:{s:.0f}px;height:{s:.0f}px;--x:{d * math.cos(a):.0f}px;--y:{d * math.sin(a) * .8 - 40:.0f}px;--r:{rng.uniform(-200, 200):.0f}deg;'
              f'animation:sdCo {sec(dur)} cubic-bezier(.1,.7,.3,1) {sec(dl)} both{hide(dl, dl + dur)}"></i>')
    return o


def embers(n=22, seed=9):
    """火の 粉（下から 上へ・ゆれる）"""
    T = SD_T
    rng = random.Random(seed)
    t0 = T['HIT'] + .3
    o = ''
    for _ in range(n):
        s = rng.uniform(2.5, 5)
        o += (f'<i style="left:{rng.uniform(10, W_ - 10):.0f}px;top:{rng.uniform(700, 860):.0f}px;width:{s:.1f}px;height:{s:.1f}px;--dy:{-rng.uniform(560, 900):.0f}px;--sx:{rng.uniform(-30, 30):.0f}px;'
              f'animation:sdEm {rng.uniform(2.4, 3.8):.1f}s linear {sec(t0 + rng.uniform(0, 2.4))} infinite,sdEmX {rng.uniform(.9, 1.6):.1f}s ease-in-out 0s infinite alternate"></i>')
    return f'<div class="sdem" style="animation:sdIn .001s linear {sec(t0)} both{hide(t0)}">{o}</div>'


def shock(cx, cy, size, t, cls=''):
    """ドンと 落ちた ときの 衝撃の 輪"""
    return (f'<i class="sdsk{cls}" style="left:{cx - size / 2:.0f}px;top:{cy - size / 2:.0f}px;width:{size}px;height:{size}px;'
            f'animation:sdSk .4s cubic-bezier(.1,.7,.3,1) {sec(t)} both{hide(t, t + .4)}"></i>')


def logo():
    T = SD_T
    o = ''
    dx, dy, dw = LOGO['sd_t_do']
    o += _img_c('sd_t_do', dx, dy, dw, 'sdt', f'animation:sdSlam .3s cubic-bezier(.2,.8,.3,1) {sec(T["DO"])} both{hide(T["DO"])}')
    o += shock(dx, dy, 360, T['DO'] + .12)
    for k, t in enumerate(T['EX']):
        ex, ey, ew = LOGO[f'e{k + 1}']
        o += _img_c('sd_t_ex', ex, ey, ew, 'sdt', f'animation:sdSlam .26s cubic-bezier(.2,.8,.3,1) {sec(t)} both{hide(t)}')
        o += shock(ex, ey, 300 - 60 * k, t + .1)
    hx, hy, hw = LOGO['sd_t_hit']
    o += _img_c('sd_t_hit', hx, hy, hw, 'sdt hit', f'animation:sdSlamB .38s cubic-bezier(.2,.8,.3,1) {sec(T["HIT"])} both,sdPulse 1.15s ease-in-out {sec(T["HIT"] + .5)} infinite alternate{hide(T["HIT"])}')
    o += shock(hx, hy, 620, T['HIT'] + .14, ' big')
    return f'<div class="sdlogo" style="animation:sdShk .28s linear {sec(T["DO"])} both,sdShkB .34s linear {sec(T["HIT"])} both">{o}</div>'


def scene_c():
    T = SD_T
    c0 = T['C']
    f0, f1 = T['FLARE']
    g0, g1, g2, g3 = T['GF']
    hx, hy = HIT_C
    fw = 560.0
    return f'''<div class="sdC" aria-hidden="true" style="animation:sdIn .001s linear {sec(c0)} both,sdPunch .4s cubic-bezier(.1,.8,.3,1) {sec(T['HIT'])} both{hide(c0)}">
      {_img('sd_rtex', -10, -30, W_ + 20, H_ + 100, 'sdrt', 'animation:sdRt 7s ease-in-out 0s infinite alternate')}
      <i class="sdvg"></i>
      <div class="sdsh">{shards()}</div>
      {_img_c('sd_flare', CX, 430, fw, 'sdfr', f'animation:sdFr {sec(f1 - f0)} cubic-bezier(.2,.7,.3,1) {sec(f0)} both{hide(f0, f1)}')}
      {logo()}
      <i class="sdgf" style="left:{hx - 560:.0f}px;top:{hy - 560:.0f}px;animation:sdGf {sec(g3 - g0)} linear {sec(g0)} both{hide(g0, g3)}"></i>
      <div class="sdco">{coins()}</div>
      {bolts()}
      {embers()}
    </div>'''


# ---------------------------------------------------------------- 白い 光・層
def white(cls, w):
    t0, t1, t2, t3 = w
    d = t3 - t0
    return (f'<div class="sdw" aria-hidden="true" style="animation:sdW{cls} {sec(d)} linear {sec(t0)} both{hide(t0, t3)}"></div>',
            f'@keyframes sdW{cls}{{0%{{opacity:0}}{(t1 - t0) / d * 100:.1f}%{{opacity:1}}{(t2 - t0) / d * 100:.1f}%{{opacity:1}}100%{{opacity:0}}}}')


WHITES = (('b', 'WB'), ('c', 'WC'))


def sd_layers(board_html):
    """押したあと（下から）：① 紫の 炎 → ② 金の 光の 筋 → ③ 砕けて ロゴ → 白い 光 → ボード（board_html）"""
    T = SD_T
    wh = ''.join(white(k, T[n])[0] for k, n in WHITES)
    return f'''<div class="sdk" aria-hidden="true"></div>
    {scene_a()}
    {scene_b()}
    {scene_c()}
    {wh}
    <div class="hb">{board_html}</div>
    <p class="sr">ど的中！紫の 炎の 中に 黒い 馬の 影が 立ち上がり、目が 赤く 光る。画面が バグって 墨に 沈み、金の 光の 筋が 寄ってくる。画面が 砕けて「ど！！！」そして「的中」</p>'''


def sd_css():
    T = SD_T
    wk = '\n'.join(white(k, T[n])[1] for k, n in WHITES)
    g0, g1, g2, g3 = T['GF']
    gd = g3 - g0
    e0 = T['EYES']
    a0, a1 = T['A']
    ink_tot = INK_D + INK_H + .14
    return f'''
/* ---------- ど的中・紫電（sd）：shiden.py（絵は flat/shiden_art.py・十字の 光・走査線・ガラスの かけら・雷・光の 粒・火の 粉は CSS と SVG） ---------- */
.ov.fz.sd{{--t0:{sec(T['RES'] + .45)};--tc:.3s}}
@keyframes sdH{{0%,100%{{visibility:hidden}}}}
@keyframes sdIn{{from{{opacity:0}}to{{opacity:1}}}}
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
/* ② 金の 光の 筋（ため） */
.ov.sd .sdbb{{inset:0;background:radial-gradient(ellipse 70% 55% at 50% 51%,#2A0A48,#120420 55%,#040108)}}
.ov.sd .sdst{{transform-origin:50% 50%;opacity:0;mix-blend-mode:screen}}
@keyframes sdSt1{{0%{{opacity:0;transform:scale(.9) rotate(0deg)}}15%{{opacity:.85}}100%{{opacity:1;transform:scale(2.3) rotate(7deg)}}}}
@keyframes sdSt2{{0%{{opacity:0;transform:scale(1.1) rotate(0deg) scaleX(-1)}}15%{{opacity:.6}}100%{{opacity:.9;transform:scale(2.0) rotate(-6deg) scaleX(-1)}}}}
.ov.sd .sdcore{{left:50%;top:430px;width:700px;height:700px;margin:-350px 0 0 -350px;border-radius:50%;transform-origin:50% 50%;
  background:radial-gradient(circle,#FFFFFF 0,#FFF3C4 9%,#FFD25A 20%,rgba(255,170,40,.55) 34%,rgba(200,90,255,.2) 50%,rgba(120,40,200,0) 66%)}}
@keyframes sdCore{{0%{{opacity:.5;transform:scale(.12)}}100%{{opacity:1;transform:scale(2.1)}}}}
.ov.sd .sdsp{{position:absolute;inset:0}}
.ov.sd .sdsp i{{border-radius:50%;background:#FFF6D8;box-shadow:0 0 6px 1px #FFC94A;opacity:0}}
@keyframes sdSp{{0%{{opacity:0;transform:translate(var(--x),var(--y)) scale(1.2)}}20%{{opacity:1}}100%{{opacity:0;transform:translate(0,0) scale(.3)}}}}
.ov.sd .sdrg{{left:50%;top:430px;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;border:2px solid rgba(255,225,150,.9);box-shadow:0 0 14px 3px rgba(255,190,70,.6),inset 0 0 10px 2px rgba(255,190,70,.4);opacity:0}}
@keyframes sdRg{{0%{{opacity:0;transform:scale(.2)}}15%{{opacity:1}}100%{{opacity:0;transform:scale(7)}}}}
.ov.sd .sdho2{{transform-origin:50% 50%;filter:brightness(.45) drop-shadow(0 0 10px rgba(190,80,255,.8))}}
@keyframes sdHo2{{0%{{opacity:0;transform:scale(.16)}}12%{{opacity:1}}100%{{opacity:1;transform:scale(1.7);filter:brightness(.15) drop-shadow(0 0 16px rgba(210,120,255,.9))}}}}
/* ③ 砕けて ロゴ */
.ov.sd .sdrt{{opacity:.55}}
@keyframes sdRt{{from{{transform:translateY(0)}}to{{transform:translateY(-60px)}}}}
.ov.sd .sdvg{{inset:0;background:radial-gradient(ellipse 85% 70% at 50% 46%,rgba(0,0,0,0) 35%,rgba(0,0,0,.7) 100%),linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0) 25%,rgba(0,0,0,0) 75%,rgba(0,0,0,.6))}}
.ov.sd .sdsh{{position:absolute;inset:0}}
.ov.sd .sdsh i{{inset:0;opacity:0;transform-origin:50% 51%;
  background:linear-gradient(135deg,rgba(255,255,255,.92),rgba(190,225,255,.55) 38%,rgba(255,236,170,.75) 70%,rgba(255,255,255,.9)),url({blob('sd_streaks')}) 50% 51%/1300px 1300px no-repeat,#3A1060}}
@keyframes sdSh{{0%{{opacity:var(--o);transform:translate(0,0) rotate(0) scale(1)}}100%{{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1.12)}}}}
.ov.sd .sdfr{{opacity:0;transform-origin:50% 50%;mix-blend-mode:screen}}
@keyframes sdFr{{0%{{opacity:0;transform:scaleX(.1) scaleY(.6)}}25%{{opacity:1;transform:scaleX(1.25) scaleY(1)}}100%{{opacity:0;transform:scaleX(1.9) scaleY(.7)}}}}
.ov.sd .sdlogo{{position:absolute;inset:0}}
@keyframes sdPunch{{0%{{transform:scale(1.07)}}100%{{transform:none}}}}
@keyframes sdShk{{0%,100%{{transform:none}}20%{{transform:translate(-6px,4px)}}40%{{transform:translate(5px,-3px)}}60%{{transform:translate(-3px,2px)}}80%{{transform:translate(2px,-1px)}}}}
@keyframes sdShkB{{0%,100%{{transform:none}}15%{{transform:translate(-9px,6px)}}30%{{transform:translate(8px,-5px)}}45%{{transform:translate(-5px,4px)}}60%{{transform:translate(4px,-2px)}}80%{{transform:translate(-2px,1px)}}}}
.ov.sd .sdt{{opacity:0;transform-origin:50% 50%}}
@keyframes sdSlam{{0%{{opacity:0;transform:scale(2.6)}}55%{{opacity:1;transform:scale(.94)}}78%{{transform:scale(1.05)}}100%{{opacity:1;transform:none}}}}
@keyframes sdSlamB{{0%{{opacity:0;transform:scale(3.4)}}50%{{opacity:1;transform:scale(.93)}}72%{{transform:scale(1.06)}}100%{{opacity:1;transform:none}}}}
@keyframes sdPulse{{from{{transform:scale(1)}}to{{transform:scale(1.045)}}}}
.ov.sd .sdsk{{opacity:0;border-radius:50%;border:3px solid rgba(255,230,160,.95);box-shadow:0 0 18px 4px rgba(255,190,70,.7),inset 0 0 14px 3px rgba(255,190,70,.5);transform-origin:50% 50%}}
.ov.sd .sdsk.big{{border-width:4px}}
@keyframes sdSk{{0%{{opacity:1;transform:scale(.15)}}100%{{opacity:0;transform:scale(1)}}}}
.ov.sd .sdgf{{width:1120px;height:1120px;border-radius:50%;opacity:0;transform-origin:50% 50%;
  background:radial-gradient(circle,#FFFFFF 0,#FFF6D0 10%,#FFD86A 22%,rgba(255,180,50,.7) 36%,rgba(255,150,30,0) 60%)}}
@keyframes sdGf{{0%{{opacity:0;transform:scale(.3)}}{(g1 - g0) / gd * 100:.1f}%{{opacity:1;transform:scale(.9)}}{(g2 - g0) / gd * 100:.1f}%{{opacity:.9;transform:scale(1.05)}}100%{{opacity:0;transform:scale(1.3)}}}}
.ov.sd .sdco{{position:absolute;inset:0}}
.ov.sd .sdco i{{border-radius:50%;opacity:0;background:radial-gradient(circle at 35% 35%,#FFFBE0,#FFD24A 45%,#B8780A);box-shadow:0 0 6px rgba(255,210,90,.8)}}
@keyframes sdCo{{0%{{opacity:0;transform:translate(0,0) scale(.3) rotate(0)}}10%{{opacity:1}}80%{{opacity:1}}100%{{opacity:0;transform:translate(var(--x),var(--y)) scale(.9) rotate(var(--r))}}}}
.ov.sd .sdbo{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible}}
.ov.sd .sdbo path{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
.ov.sd .sdbt{{opacity:0}}
@keyframes sdBt{{0%,65%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdbo .g1 path{{stroke:#9A40FF;stroke-width:14;stroke-opacity:.18}}
.ov.sd .sdbo .g2 path{{stroke:#D9A6FF;stroke-width:5;stroke-opacity:.55}}
.ov.sd .sdbo .g3 path{{stroke:#FFFFFF;stroke-width:1.8}}
.ov.sd .sdem{{position:absolute;inset:0}}
.ov.sd .sdem i{{border-radius:50%;background:#FFD27A;box-shadow:0 0 6px 1px rgba(255,150,40,.9);opacity:0}}
@keyframes sdEm{{0%{{opacity:0;transform:translateY(0)}}12%{{opacity:1}}85%{{opacity:.8}}100%{{opacity:0;transform:translateY(var(--dy))}}}}
@keyframes sdEmX{{from{{margin-left:0}}to{{margin-left:var(--sx)}}}}
.ov.sd .hb{{z-index:10;animation:sdBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(T['RES'] + .15)} both{hide(T['RES'] + .15)}}}
@keyframes sdBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
@keyframes sdDim{{to{{opacity:.3}}}}
/* 視差効果を減らす：① ② と 光・かけら・雷・粒を 出さない。③の 虹の 布の 上に ロゴ（動かさない）→ 1.3秒から ボードを ふわっと */
@media (prefers-reduced-motion:reduce){{
  .ov.fz.sd{{--t0:1.9s}}
  .ov.sd .sdA,.ov.sd .sdB,.ov.sd .sdw,.ov.sd .sdsh,.ov.sd .sdfr,.ov.sd .sdgf,.ov.sd .sdco,.ov.sd .sdbo,.ov.sd .sdem,.ov.sd .sdsk{{display:none}}
  .ov.sd .sdC{{animation:fadeIn .5s ease-out .2s both!important}}
  .ov.sd .sdrt{{animation:none!important}}
  .ov.sd .sdt{{animation:none!important;opacity:1;transform:none}}
  .ov.sd .sdlogo{{animation:sdDim .5s ease-in 1.15s forwards!important}}
  .ov.sd .hb{{animation:fadeIn .5s ease-out 1.3s both!important}}
}}
'''
