"""壁紙パック ⑩近未来都市（まさちゃんの 指定「空飛ぶ車と、光のレーンを走る馬」）
   上の絵：夜の 未来の 町（遠くの 高い ビルと 光る 窓・塔・近くの ビルの ネオンの ふち・浮かぶ ホログラムの 看板）。
     空の 中ほどに 光の レーン（すき通った 道・水色に 光る ふち）が 横に のびて、その 上を 黒に 近い 鉄の 色の 馬
     （水色に 光る たてがみと しっぽ・光の ふちどり：pack/make/future_art.py）が 走る。いろいろな 高さを 空飛ぶ 車が 行き来する。
   動き（CSS だけ）：馬は いつも 走る（10コマを 0.48秒）。レーンの 光の すじと 支柱は 速く・近くの ビルは ゆっくり・遠くの ビルは もっと ゆっくり 流れる。
     空飛ぶ 車（近く・中くらい・遠く）が 光の 尾を 引いて 右へ 左へ（いろいろな 速さと 間）。馬の うしろに 光の すじ。
     ホログラムの 看板は ゆっくり ゆらぐ。窓の 光は 動かさない（強く 光らせない・点めつ なし）
   第4.93版（まさちゃん「常に足元に青い雷を纏っているようにして！」）：馬の 足もとに いつも 青い 雷。ひづめの まわりの 光の もやは 馬の シートに、
     ぱちぱち 走る 細い 雷は 雷だけの シート 3まい（pack/make/future_art.py の bolt0〜2：馬と 同じ 10コマ・同じ 場所）を 馬と いっしょに めくりながら、
     0.1秒ずつ 入れかえる（雷が コマごとの ひづめに ついて いく・小さい ので 点めつの 面積は ごく 小さい）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'future'
CODE = 'ft'
CY = '#3FE0FF'      # 水色の 光
MG = '#FF4FD8'      # 赤むらさきの 光
LANE_Y = 129        # レーンの 上の 面（馬の ひづめ）
RUN = 0.48          # ギャロップ 1回（10コマ）
LANE_SPEED = 260    # レーンの 光の 流れ（px／秒）


# ---------------------------------------------------------------- 背景
def sky_svg():
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#050816'/><stop offset='.45' stop-color='#0E1534'/>"
            "<stop offset='.8' stop-color='#1E1E52'/><stop offset='1' stop-color='#2C2364'/></linearGradient>"
            f"<radialGradient id='a' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='{CY}' stop-opacity='.32'/><stop offset='1' stop-color='{CY}' stop-opacity='0'/></radialGradient>"
            f"<radialGradient id='b' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='{MG}' stop-opacity='.26'/><stop offset='1' stop-color='{MG}' stop-opacity='0'/></radialGradient>")
    o = (f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
         "<ellipse cx='110' cy='112' rx='170' ry='46' fill='url(#a)'/><ellipse cx='320' cy='104' rx='130' ry='40' fill='url(#b)'/>")
    R = rnd(17)
    for i in range(40):
        x, y = R.uniform(0, W), R.uniform(2, 60) ** 1.0
        r = R.choice((0.5, 0.6, 0.7, 0.9))
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{r}' fill='#DDEBFF' opacity='{f(R.uniform(.25, .7))}'/>"
    return doc(W, H, o, defs=defs)


def city_far_svg(w=390, h=108, seed=21):
    """遠くの 高い ビル（くり返せる：はば w）：青むらさきの すき通った かげ・光る 窓の つぶ・アンテナの 赤い 灯・細い 光の すじ"""
    R = rnd(seed)
    o = ''
    x = -6
    blds = []
    while x < w + 6:
        bw = R.uniform(14, 30)
        bh = R.uniform(30, 92)
        blds.append((x, bw, bh, R.random()))
        x += bw + R.uniform(-2, 4)
    for x0, bw, bh, r in blds:
        for dx in (-w, 0, w):
            xx = x0 + dx
            if xx > w + 40 or xx + bw < -40:
                continue
            top = h - bh
            c = mix('#1C2558', '#2A2E6E', r)
            o += f"<rect x='{f(xx)}' y='{f(top)}' width='{f(bw)}' height='{f(bh)}' fill='{c}' opacity='.92'/>"
            if r > 0.6:                                                  # 屋上の 段と アンテナ
                o += f"<rect x='{f(xx + bw * 0.25)}' y='{f(top - 6)}' width='{f(bw * 0.5)}' height='6' fill='{c}'/>"
                o += f"<path d='M{f(xx + bw / 2)} {f(top - 6)} V{f(top - 18)}' stroke='{c}' stroke-width='1.2'/><circle cx='{f(xx + bw / 2)}' cy='{f(top - 18)}' r='1.1' fill='#FF5A7A' opacity='.85'/>"
            if r < 0.3:                                                  # たての 光の すじ
                o += f"<rect x='{f(xx + bw * 0.45)}' y='{f(top + 4)}' width='1.2' height='{f(bh - 8)}' fill='{CY}' opacity='.35'/>"
            Rw = rnd(int(x0 * 10) + 3)
            for yy in range(int(top + 5), int(h - 3), 6):                # 窓の つぶ
                for xw in range(int(xx + 3), int(xx + bw - 3), 5):
                    if Rw.random() < 0.34:
                        col = Rw.choice(('#9FE8FF', '#E8F2FF', '#FFC6F0', '#9FE8FF'))
                        o += f"<rect x='{xw}' y='{yy}' width='2' height='2.4' fill='{col}' opacity='{f(Rw.uniform(.35, .75))}'/>"
    return doc(w, h, o)


def tower_svg():
    """遠くの 細長い 塔（光の 輪 2つ）：動かない"""
    o = (f"<path d='M28 140 L30 30 L32 140 Z' fill='#26306A'/><path d='M26 140 L29 60 L30 140 Z' fill='#1C2558'/>"
         f"<path d='M30 30 V6' stroke='#26306A' stroke-width='1.4'/><circle cx='30' cy='6' r='1.6' fill='#FF5A7A'/>"
         f"<ellipse cx='30' cy='52' rx='16' ry='3.6' fill='none' stroke='{CY}' stroke-width='1.4' opacity='.75'/>"
         f"<ellipse cx='30' cy='78' rx='11' ry='2.6' fill='none' stroke='{MG}' stroke-width='1.2' opacity='.7'/>"
         f"<rect x='22' y='50' width='16' height='5' rx='2' fill='#2E3A7A'/>")
    return doc(60, 140, o)


def city_mid_svg(w=260, h=96, seed=33):
    """近くの ビル（くり返せる：はば w）：こい 紺・ネオンの ふち（水色・赤むらさき）・窓の 帯"""
    R = rnd(seed)
    o = ''
    x = -4
    blds = []
    while x < w + 4:
        bw = R.uniform(28, 46)
        bh = R.uniform(34, 78)
        blds.append((x, bw, bh, R.random()))
        x += bw + R.uniform(6, 14)
    for x0, bw, bh, r in blds:
        for dx in (-w, 0, w):
            xx = x0 + dx
            if xx > w + 50 or xx + bw < -50:
                continue
            top = h - bh
            o += f"<path d='M{f(xx)} {h} V{f(top + 6)} L{f(xx + 6)} {f(top)} H{f(xx + bw)} V{h} Z' fill='#0C1230'/>"
            edge = CY if r < 0.55 else MG
            o += f"<path d='M{f(xx)} {f(top + 6)} L{f(xx + 6)} {f(top)} H{f(xx + bw)}' fill='none' stroke='{edge}' stroke-width='1.2' opacity='.85'/>"
            for k in range(int((bh - 10) // 9)):                        # 窓の 帯
                yy = top + 8 + k * 9
                o += f"<rect x='{f(xx + 4)}' y='{f(yy)}' width='{f(bw - 8)}' height='2.4' fill='#3A4C9A' opacity='.7'/>"
                Rw = rnd(int(xx * 7 + k))
                if Rw.random() < 0.5:
                    a = Rw.uniform(0, bw - 16)
                    o += f"<rect x='{f(xx + 4 + a)}' y='{f(yy)}' width='{f(Rw.uniform(6, 12))}' height='2.4' fill='#BFEFFF' opacity='.75'/>"
    return doc(w, h, o)


def holo_svg():
    """浮かぶ ホログラムの 看板（字なし：走る 馬の 形と 輪と 線。水色の すき通った 光）"""
    o = (f"<rect x='1' y='1' width='62' height='34' rx='4' fill='{CY}' fill-opacity='.12' stroke='{CY}' stroke-width='1.2' stroke-opacity='.85'/>"
         f"<path d='M6 7 h10 M6 29 h6 M58 7 h-8 M58 29 h-10' stroke='{CY}' stroke-width='1.4' stroke-linecap='round'/>")
    # 馬の 頭の かげ（横顔：アーチの 首・たてがみ・耳・鼻）
    head = [(14, 31), (13, 22), (15, 14), (19, 9), (22, 6.5), (23.2, 3), (25, 6), (28, 7.4), (31, 10), (36.5, 18.5), (37, 21.5), (35, 23), (31.4, 22.4),
            (28, 21), (25, 22), (23.6, 26), (24.6, 31)]
    o += f"<path d='{smooth(head, True, 0.4)}' fill='{CY}' fill-opacity='.72'/>"
    o += f"<path d='M15 15 Q17 10 21 8' fill='none' stroke='#E8FBFF' stroke-width='1.2' stroke-linecap='round' opacity='.8'/><circle cx='28.4' cy='12.6' r='1' fill='#0C1638'/>"
    o += f"<circle cx='52' cy='20' r='6' fill='none' stroke='{MG}' stroke-width='1.2' opacity='.85'/><path d='M49 20 h6 M52 17 v6' stroke='{MG}' stroke-width='1' opacity='.8'/>"
    for k in range(4):
        o += f"<path d='M4 {f(4 + k * 9)} H60' stroke='#FFFFFF' stroke-width='.5' opacity='.12'/>"
    return doc(64, 36, o)


def lane_svg(w=130, h=34):
    """光の レーン（くり返せる：はば w）：すき通った 道・上の ふちの 水色の 光・流れる 光の すじ・下の 支柱"""
    defs = (f"<linearGradient id='l' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{CY}' stop-opacity='.38'/><stop offset='.35' stop-color='#3A6AD8' stop-opacity='.22'/>"
            "<stop offset='1' stop-color='#1A2A6E' stop-opacity='.05'/></linearGradient>")
    o = (f"<rect x='0' y='2' width='{w}' height='9' fill='url(#l)'/>"
         f"<rect x='0' y='1' width='{w}' height='1.6' fill='{CY}'/><rect x='0' y='0' width='{w}' height='4' fill='{CY}' opacity='.18'/>"
         f"<rect x='0' y='10.4' width='{w}' height='1' fill='{MG}' opacity='.7'/>")
    for k, (x, L) in enumerate(((6, 26), (52, 14), (84, 30))):           # 道の 上の 光の すじ
        o += f"<rect x='{x}' y='{4.6 + (k % 2) * 2.4}' width='{L}' height='1.2' rx='.6' fill='#E8FBFF' opacity='.75'/>"
    # 支柱（下へ のびる 光の 柱）
    x = 96
    o += (f"<path d='M{x} 11 L{x - 4} {h} H{x + 4} Z' fill='#16205A' opacity='.9'/><path d='M{x} 11 V{h}' stroke='{CY}' stroke-width='.8' opacity='.55'/>")
    return doc(w, h, o, defs=defs)


def below_svg(w=200, h=30, seed=41):
    """レーンの 下の 町の 明かり（くり返せる：はば w）"""
    R = rnd(seed)
    o = f"<rect width='{w}' height='{h}' fill='#080C22'/>"
    for i in range(70):
        x, y = R.uniform(0, w), R.uniform(2, h - 2)
        col = R.choice(('#7FDFFF', '#FFFFFF', '#FF9FE6', '#FFD27A'))
        for dx in (0, -w, w):
            if 0 <= x + dx <= w:
                o += f"<rect x='{f(x + dx)}' y='{f(y)}' width='{f(R.uniform(1, 3))}' height='1.2' fill='{col}' opacity='{f(R.uniform(.25, .65))}'/>"
    o += f"<rect width='{w}' height='6' fill='#0A1030' opacity='.8'/>"
    return doc(w, h, o)


def car_svg(body='#D8E2F0', body2='#8C9AB8', glass='#3FE0FF', glow=CY, w=60, h=18, trail=True, left=False):
    """空飛ぶ 車（右向き・横から）：低く 長い 車の 形（トランク・屋根・前の ガラス・ボンネット）・横の 窓 2まい・
       車輪の かわりに 光る 浮き台 2つ（下に 光）・横の 光の 線・うしろに 赤い 灯・前に 白い 灯。うしろに 光の 尾"""
    tx = 26 if trail else 0
    tot = w + tx
    defs = (f"<linearGradient id='t' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='{glow}' stop-opacity='0'/><stop offset='1' stop-color='{glow}' stop-opacity='.7'/></linearGradient>"
            f"<radialGradient id='u' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='{glow}' stop-opacity='.95'/><stop offset='1' stop-color='{glow}' stop-opacity='0'/></radialGradient>")
    x0 = tx
    X = lambda k: x0 + w * k
    Y = lambda k: h * k
    o = ''
    if trail:
        o += f"<path d='M0 {f(Y(.6))} L{f(X(.02))} {f(Y(.46))} L{f(X(.02))} {f(Y(.72))} Z' fill='url(#t)'/>"
        o += f"<path d='M4 {f(Y(.56))} L{f(X(.02))} {f(Y(.52))}' stroke='#FF5A7A' stroke-width='1' opacity='.55'/>"
    for k in (.24, .76):                                                 # 浮き台の 下の 光
        o += f"<ellipse cx='{f(X(k))}' cy='{f(Y(.9))}' rx='{f(w * .13)}' ry='{f(h * .12)}' fill='url(#u)'/>"
    body_d = (f"M{f(X(.02))} {f(Y(.72))} L{f(X(.03))} {f(Y(.48))} C{f(X(.06))} {f(Y(.42))} {f(X(.18))} {f(Y(.4))} {f(X(.3))} {f(Y(.38))} "
              f"L{f(X(.4))} {f(Y(.14))} C{f(X(.43))} {f(Y(.1))} {f(X(.58))} {f(Y(.1))} {f(X(.62))} {f(Y(.14))} L{f(X(.76))} {f(Y(.38))} "
              f"C{f(X(.88))} {f(Y(.4))} {f(X(.97))} {f(Y(.44))} {f(X(.99))} {f(Y(.54))} L{f(X(.99))} {f(Y(.66))} C{f(X(.97))} {f(Y(.74))} {f(X(.92))} {f(Y(.76))} {f(X(.86))} {f(Y(.76))} "
              f"L{f(X(.1))} {f(Y(.76))} C{f(X(.06))} {f(Y(.76))} {f(X(.02))} {f(Y(.75))} {f(X(.02))} {f(Y(.72))} Z")
    o += f"<path d='{body_d}' fill='{body}'/>"
    o += f"<path d='M{f(X(.03))} {f(Y(.6))} L{f(X(.99))} {f(Y(.6))} L{f(X(.99))} {f(Y(.66))} C{f(X(.97))} {f(Y(.74))} {f(X(.92))} {f(Y(.76))} {f(X(.86))} {f(Y(.76))} L{f(X(.1))} {f(Y(.76))} C{f(X(.06))} {f(Y(.76))} {f(X(.02))} {f(Y(.75))} {f(X(.02))} {f(Y(.72))} Z' fill='{body2}'/>"
    o += (f"<path d='M{f(X(.33))} {f(Y(.38))} L{f(X(.42))} {f(Y(.17))} H{f(X(.49))} V{f(Y(.38))} Z' fill='{glass}' opacity='.85'/>"
          f"<path d='M{f(X(.52))} {f(Y(.38))} V{f(Y(.17))} H{f(X(.6))} L{f(X(.72))} {f(Y(.38))} Z' fill='{glass}' opacity='.85'/>"
          f"<path d='M{f(X(.44))} {f(Y(.2))} L{f(X(.41))} {f(Y(.3))}' stroke='#FFFFFF' stroke-width='.9' opacity='.8'/>"
          f"<path d='M{f(X(.04))} {f(Y(.54))} H{f(X(.98))}' stroke='{glow}' stroke-width='1' opacity='.95'/>"
          f"<rect x='{f(X(.015))}' y='{f(Y(.45))}' width='3' height='{f(h * .14)}' rx='.8' fill='#FF4A6A'/>"
          f"<rect x='{f(X(.955))}' y='{f(Y(.47))}' width='{f(w * .04)}' height='{f(h * .09)}' rx='.6' fill='#FFFFFF'/>")
    for k in (.24, .76):                                                 # 浮き台（車輪の かわり）
        o += (f"<ellipse cx='{f(X(k))}' cy='{f(Y(.76))}' rx='{f(w * .1)}' ry='{f(h * .13)}' fill='#1A2240'/>"
              f"<ellipse cx='{f(X(k))}' cy='{f(Y(.8))}' rx='{f(w * .075)}' ry='{f(h * .06)}' fill='{glow}'/>")
    s = doc(tot, h, o, defs=defs)
    if left:
        s = doc(tot, h, f"<g transform='translate({tot} 0) scale(-1 1)'>{o}</g>", defs=defs)
    return s


def streak_svg():
    """馬の うしろの 光の すじ（左へ 消える）"""
    defs = (f"<linearGradient id='g' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='{CY}' stop-opacity='0'/><stop offset='1' stop-color='{CY}' stop-opacity='.85'/></linearGradient>")
    return doc(90, 4, "<rect x='0' y='1' width='90' height='2' rx='1' fill='url(#g)'/>", defs=defs)


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
CARS = [  # (クラス, 向き, 上, 大きさ倍, 秒, 遅れ, 体の色, 光)
    ('c1', 1, 62, 1.0, 7.0, 0.0, '#E6ECF6', CY),
    ('c2', -1, 34, 0.62, 9.5, -3.2, '#F2D6EE', MG),
    ('c3', 1, 18, 0.36, 13.0, -6.0, '#C8D4EA', CY),
    ('c4', -1, 50, 0.44, 11.0, -8.4, '#D6E6F2', CY),
    ('c5', 1, 140, 0.7, 8.6, -5.1, '#F0E2C8', MG),
]


def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('夜の未来の町の空にのびる光のレーンを、水色に光るたてがみの黒い馬が、足もとに青い雷をまといながら走るイラスト。まわりを空飛ぶ車が光の尾を引いて行き来し、'
           '遠くに光る窓の高いビルと塔、浮かぶホログラムの看板')
    html = f'<div class="ftw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ftSky', sky_svg())
    html += img('ftTw', tower_svg())
    html += f'<i class="ftFar" style="background-image:url(&quot;{durl(city_far_svg())}&quot;)"></i>'
    html += f'<i class="ftMid" style="background-image:url(&quot;{durl(city_mid_svg())}&quot;)"></i>'
    html += img('ftHo', holo_svg())
    for cls, d, top, sc, sec, dl, col, gl in CARS:
        if top < LANE_Y:
            html += img(f'ftCar {cls}', car_svg(body=col, body2=mix(col, '#3A4A7A', 0.5), glow=gl, left=d < 0))
    html += f'<i class="ftBl" style="background-image:url(&quot;{durl(below_svg())}&quot;)"></i>'
    html += f'<i class="ftLn" style="background-image:url(&quot;{durl(lane_svg())}&quot;)"></i>'
    html += '<i class="ftPool"></i>'
    for k in range(4):
        html += img(f'ftSk s{k}', streak_svg())
    if run:
        html += '<i class="ftH"><i></i></i>'
        for v in range(3):                                             # 足もとの 雷（3とおりを 0.1秒ずつ）
            if f'bolt{v}' in B:
                html += f'<i class="ftB b{v}"><i></i></i>'
    for cls, d, top, sc, sec, dl, col, gl in CARS:
        if top >= LANE_Y:
            html += img(f'ftCar {cls}', car_svg(body=col, body2=mix(col, '#3A4A7A', 0.5), glow=gl, left=d < 0))
    html += '</div>'

    lane_w = 130
    css = ('.ftw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#0E1534}'
           '.ftw img,.ftw i{position:absolute;display:block}'
           '.ftw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.ftw .ftSky{left:0;top:0;width:390px;height:160px}'
           '.ftw .ftTw{left:286px;top:-6px;width:60px;height:140px;opacity:.9}'
           '.ftw .ftFar{left:0;top:26px;width:782px;height:108px;background-size:390px 108px;background-repeat:repeat-x;animation:ftFar 70s linear infinite;will-change:transform}'
           '.ftw .ftMid{left:0;top:40px;width:652px;height:96px;background-size:260px 96px;background-repeat:repeat-x;animation:ftMid 9s linear infinite;will-change:transform}'
           '.ftw .ftHo{left:40px;top:30px;width:64px;height:36px;animation:ftHolo 5.6s ease-in-out infinite;will-change:opacity,transform}'
           '.ftw .ftBl{left:0;top:130px;width:600px;height:30px;background-size:200px 30px;background-repeat:repeat-x;animation:ftBelow 3.2s linear infinite;will-change:transform}'
           f'.ftw .ftLn{{left:0;top:{LANE_Y - 1}px;width:{390 + lane_w}px;height:34px;background-size:{lane_w}px 34px;background-repeat:repeat-x;animation:ftLane {f(lane_w / LANE_SPEED, 4)}s linear infinite;will-change:transform}}'
           f'.ftw .ftPool{{left:110px;top:{LANE_Y - 7}px;width:170px;height:16px;border-radius:50%;background:radial-gradient(closest-side,rgba(63,224,255,.42),rgba(63,224,255,0))}}'
           '.ftw .ftSk{width:90px;height:4px;opacity:0;animation:ftStreak 1.1s linear infinite;will-change:transform,opacity}'
           '.ftw .ftCar{will-change:transform}')
    for k, (x, y, dl) in enumerate(((70, 66, 0.0), (52, 92, -0.42), (84, 108, -0.7), (62, 80, -0.9))):
        css += f'.ftw .ftSk.s{k}{{left:{x}px;top:{y}px;animation-delay:{f(dl)}s}}'
    if run:
        n, (cw, ch), (ax, ay) = run['frames'], run['cell'], run['at']
        css += (f'.ftw .ftH{{left:{f(ax / 2)}px;top:{f(ay / 2)}px;width:{f(cw / 2)}px;height:{f(ch / 2)}px;overflow:hidden}}'
                f'.ftw .ftH>i{{left:0;top:0;width:{f(n * cw / 2)}px;height:{f(ch / 2)}px;background:url({run["url"]}) 0 0/{f(n * cw / 2)}px {f(ch / 2)}px no-repeat;'
                f'animation:ftRun {RUN}s steps({n}) infinite}}'
                + kf('ftRun', [(100, f'transform:translateX({f(-n * cw / 2)}px)')]))
        for v in range(3):
            bo = B.get(f'bolt{v}')
            if not bo:
                continue
            css += (f'.ftw .ftB.b{v}{{left:{f(ax / 2)}px;top:{f(ay / 2)}px;width:{f(cw / 2)}px;height:{f(ch / 2)}px;overflow:hidden;opacity:0;'
                    f'animation:ftZap .3s step-end {f(-0.1 * v, 2)}s infinite}}'
                    f'.ftw .ftB.b{v}>i{{left:0;top:0;width:{f(n * cw / 2)}px;height:{f(ch / 2)}px;background:url({bo["url"]}) 0 0/{f(n * cw / 2)}px {f(ch / 2)}px no-repeat;'
                    f'animation:ftRun {RUN}s steps({n}) infinite}}')
        css += kf('ftZap', [(0, 'opacity:1'), (33.33, 'opacity:0'), (100, 'opacity:0')])
    for cls, d, top, sc, sec, dl, col, gl in CARS:
        w, h = 86 * sc, 18 * sc
        css += f'.ftw .ftCar.{cls}{{left:0;top:{top}px;width:{f(w)}px;height:{f(h)}px;animation:ftCar{cls} {f(sec)}s linear {f(dl)}s infinite}}'
        if d > 0:
            a, b = -w - 10, 400
        else:
            a, b = 400, -w - 10
        dy = 6 if cls in ('c1', 'c5') else 3
        css += kf(f'ftCar{cls}', [(0, f'transform:translate({f(a)}px,0)'), (32, f'transform:translate({f(a + (b - a) * 0.5)}px,{-dy}px)'),
                                  (64, f'transform:translate({f(b)}px,0)'), (100, f'transform:translate({f(b)}px,0)')])
    css += (kf('ftFar', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-390px)')])
            + kf('ftMid', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-260px)')])
            + kf('ftBelow', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-200px)')])
            + kf('ftLane', [(0, 'transform:translateX(0)'), (100, f'transform:translateX(-{lane_w}px)')])
            + kf('ftHolo', [(0, 'opacity:.7;transform:translateY(0)'), (50, 'opacity:.95;transform:translateY(-2px)'), (100, 'opacity:.7;transform:translateY(0)')])
            + kf('ftStreak', [(0, 'opacity:0;transform:translateX(30px) scaleX(.4)'), (12, 'opacity:.9;transform:translateX(10px) scaleX(1)'),
                              (100, 'opacity:0;transform:translateX(-120px) scaleX(1.2)')]))
    if still:
        css += reduced('.ftw>*:not(.bnr)')
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_circuit():
    """背景の もよう：うすい 回路の 線と 点（水色）"""
    o = (f"<path d='M0 30 H34 L46 18 H90 M120 60 H96 L84 72 H40 L28 84 V120 M70 0 V12 M70 120 V104 L82 92 H120' fill='none' stroke='{CY}' stroke-width='1' opacity='.14'/>")
    for x, y in ((34, 30), (46, 18), (90, 18), (96, 60), (40, 72), (28, 84), (82, 92), (70, 104)):
        o += f"<circle cx='{x}' cy='{y}' r='2' fill='none' stroke='{CY}' stroke-width='1' opacity='.22'/>"
    o += f"<circle cx='104' cy='34' r='1.4' fill='{MG}' opacity='.3'/><circle cx='14' cy='100' r='1.4' fill='{MG}' opacity='.3'/>"
    return tile(120, 120, o)


def lane_strip():
    """上の 帯の 下の ふち：光の レーン（水色の 線と 流れる 点線）"""
    o = (f"<rect y='1' width='40' height='2' fill='{CY}'/><rect y='0' width='40' height='4' fill='{CY}' opacity='.25'/>"
         f"<rect x='4' y='5' width='14' height='1.4' rx='.7' fill='#E8FBFF' opacity='.8'/><rect x='26' y='5' width='6' height='1.4' rx='.7' fill='{MG}' opacity='.8'/>")
    return tile(40, 7, o)


def orn():
    """すみの 飾り（44×44）：小さな 空飛ぶ 車と 光の 尾"""
    o = (f"<path d='M2 30 L18 26 L18 33 Z' fill='{CY}' opacity='.45'/>"
         f"<ellipse cx='26' cy='35' rx='11' ry='2.6' fill='{CY}' opacity='.55'/>"
         "<path d='M14 30 C14 27 18 26 22 26 L25 20 C27 17 31 17 33 20 L36 26 C40 27 42 28 42 30 C41 33 38 33 34 33 H19 C16 33 14 32 14 30 Z' fill='#E6ECF6'/>"
         f"<path d='M26 25.6 L27.6 21 C28.6 19.6 30.6 19.6 31.6 21 L33.4 25.6 Z' fill='{CY}'/>"
         f"<path d='M16 29.6 H40' stroke='{CY}' stroke-width='1'/><circle cx='41' cy='29.6' r='1' fill='#FFFFFF'/><rect x='14.2' y='28.6' width='2' height='1.8' fill='#FF4A6A'/>")
    o += f"<path d='{sparkle_d(8, 12, 4.5, 0.16)}' fill='{CY}' opacity='.8'/><path d='{sparkle_d(36, 8, 3, 0.16)}' fill='{MG}' opacity='.75'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='近未来都市', desc='光のレーン', title='近未来都市（夜×水色の光）', banner=ID,
    alt='夜の未来の町の空にのびる光のレーンを、水色に光るたてがみの黒い馬が足もとに青い雷をまとって走り、まわりを空飛ぶ車が光の尾を引いて行き来するイラスト',
    fonts=['Stick', 'Zen+Kaku+Gothic+New:wght@500;700'],
    v=dict(bg='#0B1024', ink='#EAF3FF', sub='#9FB2D6', card='#121A36', cardB='1px solid #2A3A70', cardO='0 solid transparent', cardS='0 8px 22px rgba(0,0,0,.4)',
           radius='12px', rs='8px', font='"Zen Kaku Gothic New"', dfont='"Stick"', dw='400', logo='#7FEFFF', logoS='0 0 12px rgba(63,224,255,.55)',
           iii=CY, iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#070B1C,#101A3A)', hdInk='#EAF3FF', hdB='0 solid transparent',
           mBg='rgba(63,224,255,.06)', mLine='rgba(63,224,255,.55)', mInk='#EAF3FF', pill='rgba(255,255,255,.05)', pillLine='rgba(63,224,255,.35)', pillInk='#DDEBFF',
           coin=CY, coinInk='#06101E', badge='#16224A', badgeInk='#7FEFFF', badgeB='1.5px solid #3FE0FF', tagBg='rgba(63,224,255,.07)', tagInk='#CFE4FF',
           tagLine='#2E4A86', warnBg='rgba(255,79,216,.16)', warnInk='#FFB2EC', zBg='rgba(255,255,255,.03)', zB='1px solid #26346A', znBg=MG, znInk='#1A0618',
           znB='0 solid transparent', znR='4px', znS='none', acc='#7FEFFF', nR='6px', w2B='1.5px solid #8A9AC2', sep='1px solid #26346A',
           btn=CY, btnInk='#06101E', btnB='0 solid transparent', btnR='10px', btnS='0 0 16px rgba(63,224,255,.45)', btn2='transparent', btn2Ink='#7FEFFF',
           btn2B='1.5px solid #3FE0FF', tab='#070B1C', tabB='1px solid #1E2A56', tabInk='#8FA2CC', tabOn='rgba(63,224,255,.14)', tabOnInk='#7FEFFF',
           tabR='10px', sel=CY, selInk='#06101E', h1='#7FEFFF'),
    chk=dict(hd=['#070B1C', '#101A3A']),
    css=[('', 'background-image:' + curi(tile_circuit()) + ',radial-gradient(ellipse 70% 30% at 50% 0%,rgba(63,224,255,.08),transparent 70%);background-size:120px 120px,100% 100%'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-6px;height:7px;background:' + curi(lane_strip()) + ' 0 0/40px 7px repeat-x'),
         ('.card::before', 'content:"";position:absolute;left:14px;right:14px;top:-1px;height:2px;border-radius:2px;background:linear-gradient(90deg,transparent,rgba(63,224,255,.85),transparent)')],
    orn=orn(),
    guide=dict(colors=[('#0B1024', '夜'), (CY, '光の水色'), (MG, '赤むらさき'), ('#121A36', 'カード'), ('#EAF3FF', '文字')],
               fonts='見出し：Stick<br>本文：Zen Kaku Gothic New', shape='角丸12px・暗い カード（上に 光の 線）・帯の 下に 光の レーン・回路の 背景・すみに 空飛ぶ 車・的中ボタンは ホログラムの PUSH',
               pic='夜の 未来の 町・光る 窓の ビルと 塔・ホログラムの 看板・空飛ぶ 車・光の レーンを 走る 黒い 馬（水色に 光る たてがみ・足もとに いつも 青い 雷）'),
)


# ================================================================== 的中ボタン：ホログラムの PUSH（ft）
def push_face(sfx=''):
    """ボタン（200×100）が すき通った ガラスの 板（水色の ふち・すみの かぎ形・横の 走査線が ゆっくり 下へ .ftsc）"""
    o = (f"<rect x='0' y='0' width='200' height='100' rx='16' fill='#0C1638' fill-opacity='.88' stroke='{CY}' stroke-width='2.6'/>"
         f"<rect x='5' y='5' width='190' height='90' rx='12' fill='none' stroke='{CY}' stroke-width='1' stroke-opacity='.45'/>"
         f"<rect x='8' y='8' width='184' height='26' rx='9' fill='{CY}' fill-opacity='.1'/>")
    for x0, y0, sx, sy in ((10, 10, 1, 1), (190, 10, -1, 1), (10, 90, 1, -1), (190, 90, -1, -1)):
        o += f"<path d='M{x0} {y0 + 14 * sy} V{y0} H{x0 + 14 * sx}' fill='none' stroke='{MG}' stroke-width='2.6' stroke-linecap='round'/>"
    for k in range(9):
        o += f"<path d='M14 {16 + k * 9} H186' stroke='#FFFFFF' stroke-width='.6' opacity='.08'/>"
    o += f"<g class='ftsc'><rect x='6' y='0' width='188' height='5' fill='{CY}' fill-opacity='.22'/></g>"
    return f'<i class="ftf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{o}</svg></i>'


def push_decor(sfx=''):
    """まわりの ホログラムの 輪（ゆっくり 回る .ftrg）と うかぶ 六角形（.ftbx）"""
    o = (f"<g class='ftrg'><circle cx='100' cy='50' r='118' fill='none' stroke='{CY}' stroke-width='1.6' stroke-dasharray='24 10 6 10' opacity='.55'/></g>"
         f"<g class='ftrg r'><circle cx='100' cy='50' r='104' fill='none' stroke='{MG}' stroke-width='1.2' stroke-dasharray='4 14' opacity='.6'/></g>")
    for j, (x, y, r, c) in enumerate(((-18, -6, 7, CY), (218, 96, 6, MG), (226, -10, 5, CY), (-24, 98, 5, MG), (100, -46, 5, CY))):
        hx = ' '.join(f'{x + math.cos(math.radians(60 * k + 30)) * r:.1f},{y + math.sin(math.radians(60 * k + 30)) * r:.1f}' for k in range(6))
        o += f'<g class="ftbx" style="animation-delay:{-0.7 * j:.1f}s"><polygon points="{hx}" fill="{c}" fill-opacity=".18" stroke="{c}" stroke-width="1.4"/></g>'
    return f'<i class="ftd" aria-hidden="true"><svg viewBox="-40 -80 280 260" width="280" height="260">{o}</svg></i>'


def _hex(c, fillop=.3):
    pts = ' '.join(f'{10 + math.cos(math.radians(60 * k + 30)) * 8.6:.1f},{10 + math.sin(math.radians(60 * k + 30)) * 8.6:.1f}' for k in range(6))
    return doc(20, 20, f"<polygon points='{pts}' fill='{c}' fill-opacity='{fillop}' stroke='{c}' stroke-width='1.8'/>")


PIECES = dict(
    hc=piece(_hex(CY)), hm=piece(_hex(MG)),
    cv=piece(doc(20, 20, f"<path d='M4 4 L12 10 L4 16 M10 4 L18 10 L10 16' fill='none' stroke='{CY}' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/>")),
    sq=piece(doc(20, 20, f"<rect x='4' y='4' width='12' height='12' rx='2' fill='none' stroke='{MG}' stroke-width='2'/><rect x='8' y='8' width='4' height='4' fill='{MG}'/>")),
    ln='border-radius:2px;background:linear-gradient(90deg,rgba(63,224,255,0),#3FE0FF);height:calc(var(--z) * .22)',
)


def push_burst():
    return fly_burst(CODE, ['hc', 'cv', 'hm', 'ln', 'sq', 'hc', 'ln', 'cv'], 28, 57, sizes=dict(hc=(14, 20), hm=(13, 18), cv=(13, 17), sq=(12, 16), ln=(24, 34)))


PUSH_CSS = r'''
/* ---------- 近未来都市の的中ボタン：ホログラムの PUSH（壁紙パック） ----------
   ボタンは すき通った ガラスの 板（水色の ふち・赤むらさきの すみの かぎ形・横の 線）に 光る「PUSH」。走査線が ゆっくり 下へ 通る。
   まわりに ホログラムの 輪が ゆっくり 回り、六角形が うかぶ。上下の 動きは 的中と 同じ。押すと 板が ちぢんで ふくらみ（強く 光らせない）、
   六角形・山形・四角・光の 線が はじけて 落ち、水色の 光の 輪が 広がる */
.ft{--pushA:#0C1638;--pushB:#06101E;--pushC:#3FE0FF;--rim:#3FE0FF;--rimD:#06101E}
.push.ft{--pr:16px;background:none;border-radius:16px;box-shadow:0 0 18px rgba(63,224,255,.35),0 18px 26px rgba(0,0,0,.45)}
.push.ft span{font:400 44px/1 "Stick",sans-serif;letter-spacing:.1em;color:#BFF6FF;text-shadow:0 0 6px rgba(63,224,255,.9),0 0 16px rgba(63,224,255,.45),0 2px 0 #06101E}
.push.ft::after{border-radius:30px;border-color:rgba(63,224,255,.8)}
.ft .ftf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:16px;overflow:hidden;pointer-events:none;font-style:normal}
.ft .ftf svg{display:block;width:200px;height:100px}
.ft .ftd{position:absolute;left:-40px;top:-80px;width:280px;height:260px;pointer-events:none;z-index:3;font-style:normal}
.ft .ftd svg{display:block;width:280px;height:260px;overflow:visible}
.ft .ftsc{transform-box:view-box;animation:ftfScan 3.2s linear infinite}
@keyframes ftfScan{0%{transform:translateY(-6px)}100%{transform:translateY(104px)}}
.ft .ftrg{transform-box:view-box;transform-origin:100px 50px;animation:ftfRg 14s linear infinite}
.ft .ftrg.r{animation-duration:20s;animation-direction:reverse}
@keyframes ftfRg{to{transform:rotate(360deg)}}
.ft .ftbx{transform-box:fill-box;transform-origin:50% 50%;animation:ftfBx 3s ease-in-out infinite alternate}
@keyframes ftfBx{from{transform:translateY(-4px) rotate(-12deg);opacity:.55}to{transform:translateY(4px) rotate(12deg);opacity:1}}
.pshadow.ft{width:220px;background:rgba(63,224,255,.25)}
.tap.ft{font-family:"Stick",sans-serif;font-weight:400;color:#7FEFFF;letter-spacing:.16em;text-shadow:0 0 8px rgba(63,224,255,.7)}
.pressed.ft{border-radius:16px;background:#0C1638;box-shadow:0 0 0 2.6px #3FE0FF,0 0 18px rgba(63,224,255,.45);animation-name:ftPress,fxH}
@keyframes ftPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.ft .ftsc,.ft .ftrg,.ft .ftbx{animation:none}.ft .ftsc,.clips.ft{display:none}}
''' + fly_css(CODE, 'rgba(63,224,255,.85)', PIECES)

PUSH = dict(code=CODE, face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
