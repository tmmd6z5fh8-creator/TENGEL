"""ど的中・紫電（しでん・sd）：ど的中の 新しい 演出（第4.66版・まさちゃんの 指定）。
   まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出 圧倒的な迫力 見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   送ってくれた 動画（パチンコの 当たりの 演出）は 流れ・色・迫力の 見本に するだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
   馬は テンゲルの 馬（r3d の 3Dの 馬）。絵・動画（flat/shiden_film.py・flat/shiden_art.py）・音（gen_sfx.py の sfx_sd）は 一から 作る。
   第4.67版〜第4.69版：② を 送ってくれた GIF・動画の コマに 合わせて 作った（白黒の 煙・桃色の 雷・リアルな 馬の 顔・切り裂く 馬の 蹄・割れた 鏡の 世界 …）。
   第4.70版・まさちゃん「一枚目の画像から、二枚目の画像までの映像まで消して！ 三枚目のシーンからヒズメカットインまでのシーン消して、雑すぎる！
   もっと二枚目の馬みたいに蹄カットインをリアルな映像で作成して！ あと蹄カットインのあとから四枚目までのシーン消して！
   四枚目の光はもっと立体的に、リアルもっと強く発光した映像にして！ 蹄カットインの背景は、もっとリアルに立体的で、激しい映像にして！
   あと蹄カットインは、蹄が画面を切り裂いてるイメージね！ めちゃくちゃリアルで立体感のある表現にして！ 馬の顔のシーンもっと長くていい！ 動き方は任せる！
   あくまで参考にするのは、おくってるファイルの画像と動きをもとにしてね！ 求めているのは、全部二枚目の写真のようなリアルなエフェクトにしてほしい！」
   → ① 紫の 炎と 黒い 馬の 影・② の 平たい コマ（白黒の 煙〜割れた 鏡の 世界〜緑の 光の 輪）は やめた。
     押して すぐ ② の 動画（sd_film.mp4：flat/shiden_film.py が 1コマずつ 3D で 光と つやまで 計算して 描く・30コマ/秒・音なし・7.6秒）→ ③（CSS と SVG）→ ボード。
     動画は 超神様的中と 同じ しくみ（fx.js：押した 瞬間に 再生 → 動きだした 時を 0秒に して 音と ③ の 時計を そろえる（go）。
     動かない・読めない・視差効果を減らす／控えめ → 動画は 出さず ③ の ロゴを 止めた 絵で 出して 1.3秒から ボード（still））
   押した あと（0秒＝動画が 動きだした 瞬間）：
     ② 動画（0〜7.6秒）
        A 馬の 顔（0〜4.0秒）：闇から 青むらさきの 光の 中に 黒い 馬の 横顔が 浮かぶ → 頭が 上がって こちらを 向き・耳が 立ち・鼻から 白い 息（1.45・2.6秒）・
          たてがみが 風に なびく → 目に 火が ともって 強く 光る（2.9秒 から あふれる）→ カメラが 目へ 寄って 目の 光が 画面を つつむ
        B 蹄の カットイン（4.0〜6.4秒）：むらさきの 雷雲の トンネルを 前へ 突き進む（もくもくの 雲・雷・雨と 光の 粒・岩の かけら）→ 焼けた 蹄鉄の 蹄が 左から
          画面を 切り裂いて 右へ（まん中で スローモーション）→ 切り口が 光って 画面の ガラスが 割れて とぶ → 切り口が 開いて 光が あふれ → その 光へ 寄って 白く
        C 光（6.4〜7.6秒）：深い 緑の 空間に 白熱の 光の 玉・まわる 金の 輪・光の 筋・らせんで 集まる 金の 粒 → 光が ふくらんで 画面が 光で うまる
     ③ ど！！！的中（7.6秒〜）：白い 光が ひいて いく 中、金の 光の 中から「ど」「！」×3（上から 下へ 小さく）「的中」が 白熱の まま 画面から 出てきて
        金と 虹に 冷める（8.16秒）→ ロゴ 全体に 雷を まとう（ずっと ジリジリ）・不定期に 大きな 雷が 画面の 全方位へ → 10.38秒 ボード
   絵（ios/fx_assets の sd_….webp 4まい・id は shiden_blobs.json・大きさは shiden_layers.json）：flat/shiden_art.py（虹の 布・ど・！・的中）。ほかは CSS と SVG
   点めつ：どの 1点も 1秒に 3回 以下（test_fx_flash.py sd で 動画と ③ を つないで 確かめる）"""
import os, json, math, random

K = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(f'{K}/shiden_layers.json', encoding='utf-8'))
W_, H_ = 390.0, 844.0
CX = 195.0

# ---------------------------------------------------------------- ② の 動画（flat/shiden_film.py が 描く）の 時刻（秒）
FILM = dict(FPS=30, W=780, H=1688,                # 30コマ/秒・画面 390×844 の 2倍
            FACE=4.0, HOOF=6.4, END=7.6,          # 場面の おわり：A 馬の 顔・B 蹄の カットイン・C 光（＝動画の 長さ）
            PUFFS=(1.45, 2.6),                    # A：鼻から 白い 息
            EYE=(2.0, 2.9),                       # A：目の 火が 強く なる・光が あふれる
            RUSH=3.5,                             # A：目の 光へ 寄って 画面を つつむ（〜FACE）
            H_BOLTS=(.16, .97),                   # B（場面の 中の 秒）：雷
            H_IN=.28, H_SLOW=(.55, .95), H_OUT=1.18,   # B：蹄が 入る・まん中で スローモーション・抜ける
            H_OPEN=1.16, H_ZOOM=1.45, H_WASH=1.95,     # B：切り口が 開く・光へ 寄る・白く なる（〜HOOF）
            L_CHARGE=.75, L_WASH=.95)                  # C（場面の 中の 秒）：光が 強く なる・画面を うめる（〜END）

# ---------------------------------------------------------------- 時刻（秒・動画が 動きだした 瞬間が 0）
_C = FILM['END']
SD_T = dict(FILM=(0.0, _C),                       # ② 動画
            C=_C,                                 # ③ の はじまり（動画の さいごの 白い 光と つながる）
            WH=(_C, _C + .5),                     # 白い 光が ひいて いく
            GF=(_C, _C + .08, _C + .5, _C + .83),  # 金色の 光（出る・いちばん・ロゴが 出きる まで そのまま・消える）
            LOGO=round(_C + .12, 2), EMERGE=.44,  # ど！！！的中が 光の 中から 出てくる（はじまり・かかる 時間）
            LAND=round(_C + .56, 2),              # 出きった 瞬間（ドンッ：揺れ・金の 粒）
            ARCS=(round(_C + .48, 2), round(_C + 3.18, 2)),   # ロゴに まとう 電気（ずっと）
            BOLTS=tuple((round(_C + t, 2), n) for t, n in ((.56, 2), (.86, 1), (.96, 2), (1.38, 1), (1.5, 1), (1.86, 2), (2.18, 1), (2.3, 2), (2.66, 1), (2.98, 1))),   # 大きな 雷（時刻・本数）：不定期
            RES=round(_C + 2.78, 2))              # ボード
AR_DT = .085                                    # まとう 電気の 1コマ
# 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：動画は 出さず ③ の ロゴ（止めた 絵）→ 押して 1秒後に 音の STILL_FROM 秒から → ボードの ポンッ（音の RES＋0.2秒）で ボードが ふわっと
STILL_WAIT = 1.0
STILL_FROM = round(SD_T['RES'] - .1, 2)
STILL_BOARD = round(STILL_WAIT + (SD_T['RES'] + .2 - STILL_FROM), 2)      # 1.3秒
STILL_T0 = round(STILL_WAIT + (SD_T['RES'] + .45 - STILL_FROM), 2)        # 1.55秒（買い目の はじまり）
# ロゴの 置き場所（まん中の x・y・絵の 表示の 幅）：絵は 字の まわりに 光の あきが ある（shiden_art.py の pad）ので、字より 大きい
LOGO = dict(sd_t_do=(150.0, 232.0, 400.0), e1=(305.0, 212.0, 278.0), e2=(323.0, 336.0, 196.0), e3=(336.0, 420.0, 130.0), sd_t_hit=(CX, 586.0, 474.0))
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
    """③（第4.70版：動画の さいごの 白い 光から つながる）：黒い 下じき・虹の 布・白い 光が ひいて いく・金の 光・ど！！！的中・金の 粒・雷・火の 粉"""
    T = SD_T
    c0 = round(T['C'] - .04, 2)                     # 動画の さいごの コマ（白い 光）より 少し 前から 白い 幕で おおう（さかいめに すきまを 作らない）
    g0, g1, g2, g3 = T['GF']
    w0, w1 = T['WH']
    return f'''<div class="sdC" aria-hidden="true" style="animation:sdIn .001s linear {sec(c0)} both,sdPunch .4s cubic-bezier(.1,.8,.3,1) {sec(T['LAND'])} both{hide(c0)}">
      <i class="sdbk"></i>
      {_img('sd_rtex', -10, -30, W_ + 20, H_ + 100, 'sdrt', f'animation:sdRt 7s ease-in-out 0s infinite alternate,sdRtIn .4s linear {sec(g2)} both')}
      <i class="sdvg"></i>
      <i class="sdgf" style="left:{CX - 560:.0f}px;top:{430 - 560:.0f}px;animation:sdGf {sec(g3 - g0)} linear {sec(g0)} both{hide(g0, g3)}"></i>
      <i class="sdwh" style="animation:sdWh {sec(w1 - w0)} cubic-bezier(.3,0,.6,1) {sec(w0)} both{hide(None, w1)}"></i>
      {logo()}
      <div class="sdco">{coins()}</div>
      {lightning()}
      {embers()}
    </div>'''


# ---------------------------------------------------------------- 層
SR = ('ど的中！闇の 中に 黒い 馬の 横顔が 浮かび、目に 火が ともる。雷雲の 中を 焼けた 蹄鉄の 蹄が 画面を 切り裂き、切り口から 光が あふれる。'
      '金の 輪が まわる 光の 玉が 弾けて「ど！！！的中」が 雷を まとって 出てくる')


def sd_layers(board_html):
    """押したあと（下から）：（② の 動画は fx.js が 舞台に 置く video.sgv）→ ③ 光が 弾けて ど！！！的中（雷を まとう）→ ボード（board_html）"""
    return f'''{scene_c()}
    <div class="hb">{board_html}</div>
    <p class="sr">{SR}</p>'''


def sd_css():
    T = SD_T
    g0, g1, g2, g3 = T['GF']
    gd = g3 - g0
    return f'''
/* ---------- ど的中・紫電（sd）：shiden.py（② は 動画 sd_film.mp4＝flat/shiden_film.py・③ の 字と 虹の 布は flat/shiden_art.py・金の 光・雷・金の 粒・火の 粉は CSS と SVG） ---------- */
/* 押してから 動画が 動きだす まで（読みこみ）は 黒。動きだしたら（go）幕は すきとおって 動画（video.sgv）が 見える → {sec(T['C'])} から ③ */
.ov.fz.sd{{--t0:{sec(T['RES'] + .45)};--tc:.3s;z-index:31;background:#000}}
.ov.fz.sd.go{{background:transparent}}
.ov.fz.sd:not(.go):not(.still) *{{animation-play-state:paused!important}}
@keyframes sdH{{0%,100%{{visibility:hidden}}}}
@keyframes sdIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes sdFk{{0%,99%{{opacity:1}}100%{{opacity:0}}}}
.ov.sd .sdC{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}
.ov.sd img{{position:absolute;display:block;max-width:none}}
.ov.sd .sdC i{{position:absolute;display:block}}
/* ③ 光が 弾けて ど！！！的中が 出てくる・雷を まとう */
.ov.sd .sdbk{{inset:0;background:#050208}}
.ov.sd .sdwh{{inset:0;background:#FFF7D1}}                    /* 動画の さいごの コマと 同じ 色 */
@keyframes sdWh{{from{{opacity:1}}to{{opacity:0}}}}
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
/* 動画が 動かない・読めない・視差効果を減らす／控えめ（still）：動画は 出さず、金の 光・雷・粒は 出さない。虹の 布の 上に ロゴ（動かさない）→ {sec(STILL_BOARD)} から ボードを ふわっと（音の ポンッと 同じ 時）
   ど的中の ボードの 見出し（.fz .bh）・帯（.zrib）は ど的中の 時刻を 待たず ボードと いっしょに（{sec(STILL_BOARD + .3)}・{sec(STILL_BOARD + .4)}） */
.ov.fz.sd.still{{--t0:{sec(STILL_T0)}}}
.ov.fz.sd.still .sdgf,.ov.fz.sd.still .sdwh,.ov.fz.sd.still .sdco,.ov.fz.sd.still .sdbo,.ov.fz.sd.still .sdem{{display:none}}
.ov.fz.sd.still .sdC{{animation:fadeIn .5s ease-out .2s both!important}}
.ov.fz.sd.still .sdrt{{animation:none!important}}
.ov.fz.sd.still .sdt{{animation:none!important;opacity:1;transform:none;filter:none}}
.ov.fz.sd.still .sdlogo{{animation:sdDim .5s ease-in {sec(STILL_BOARD - .15)} forwards!important;transform:none}}
.ov.fz.sd.still .hb{{animation:fadeIn .5s ease-out {sec(STILL_BOARD)} both!important}}
.ov.fz.sd.still .bh{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .3)} both,rbowText 1.2s linear {sec(STILL_BOARD + .3)} infinite}}
.ov.fz.sd.still .zrib{{animation:fadeIn .4s ease-out {sec(STILL_BOARD + .4)} both}}
'''
