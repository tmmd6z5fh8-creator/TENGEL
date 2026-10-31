"""壁紙パック ⑥恐竜時代（まさちゃんの 指定「火山と恐竜の横を、馬が並んで走る」）
   上の絵：むかしの 大地。左に けむりを はく 火山（溶岩の すじ）・空に 翼竜・シダと ソテツの しげみと 草を 食べる トリケラトプス・
     しげみと いっしょに 流れる 背景の 恐竜（首の 長い 恐竜＝首を 上げて まわりを 見て、下げて しだを 食べる／背中に 板の ある 恐竜）・
     手前を 原始人が 乗った 馬が 2頭 ならんで 走る（鹿毛＝骨の こん棒を ふる 原始人・芦毛＝石の やりを かかげる 原始人：pack/make/dino_art.py）。
   第4.93版（まさちゃん「赤丸の馬の脚がしっかり地面について走るようにして！ 馬からゼッケンを消して、立髪と尻尾をもっと長くして、原始人が馬の上に乗ってる演出にして！
     黄丸の火山を8秒に一回噴火させて！4回に１回ランダムで大噴火するようにして！ 青丸の恐竜が、滑っているように見えるからちゃんと背景として違和感がないようにして！」）：
     ・地面は 手前の 馬の 地面に ついた ひづめと 同じ はやさで 流れる（シートの spf から）・おくの 馬は 1回りの 秒を かえて 同じ はやさ＝ひづめが すべらない。
       影は シートの 中（地面の 線）
     ・ゼッケン・鞍・番号 なし。たてがみと しっぽは 長く なびく
     ・火山：8秒に 1回 噴火（溶岩の 柱・溶岩の つぶ・けむり・斜面の 溶岩が 明るく）。4回に 1回は 大噴火（もっと 高く・岩が 飛ぶ・大きな けむり）で、
       128秒の 1回りの 中で 何回目が 大噴火かが かわる（8・56・80・96秒）。あかりは ゆっくり（強く 光らせない）
     ・首の 長い 恐竜は 歩かない（足は 地面に 止まった まま）：しげみと 同じ はやさで 流れる 背景（18秒ごと・背中に 板の ある 恐竜と 9秒 ずらして いつも どれか 見える）
   第4.94版（まさちゃん「青丸の恐竜の首の角度、動き方がおかしいから自然にして！黄丸は9秒１回赤丸は6秒に一回背景に通るようにして！
     17秒に１回、ティラノサウルスが出てきて、それを馬達で避ける演出いれて！」）：
     ・首の 長い 恐竜の 首は 8つの 短い ふしの くさり（根もと 21 → 頭 10.5 に 細く・はしは まるく 重なる）。まがりを ふしで 同じに 分けて いつも なめらかな 弓なり。
       上げる・下げる ときは 根もとの 向きと まがりを いっしょに かえる（首 ぜんぶが しなる・頭は 首の 先に ついた まま）。首の 根もとは 体の うしろから 出る
     ・しげみを 少し 速く（5.75秒で 390px）：首の 長い 恐竜は 9秒で 画面を 通りぬけて すぐ 次が 入る＝9秒に 1回。
       背中に 板の ある 恐竜は 2頭が 12秒の 1回りを 6秒 ずらして＝6秒に 1回（首の 長い 恐竜の 首と 頭に 重ならない ずらし）。足は 地面に 止まった まま
     ・17秒に 1回 ティラノサウルス（オリジナル：大きな 頭・小さな 手・しまの せなか・太い もも）が 右から 走って きて、頭を 上げて 口を あけて ほえる（ほえる 線）。
       2頭の 馬は 上（おく）と 下（手前）に わかれて よけ、ティラノは その あいだを 左へ 走りぬける → 馬は もとの ならびに もどる。
       原始人は びっくり（目と 口が まるく・武器を まっすぐ 上げる シートに 入れかえ）・頭の 上に 「！」。強い 光は なし。
       ティラノの 足は もも → すね → 足の くさりで、地面に ついた 足は 地面と 同じ はやさで うしろへ（すべらない）
     ・小さな 恐竜は ティラノの 出ない ころに 17秒に 1回
   動き：馬は いつも ならんで 走る・地面（足あと・小石）と しげみと 背景の 恐竜が 流れる（遠いほど ゆっくり）・翼竜が はばたいて 横切る・
     ときどき 小さな 恐竜が 馬と ならんで 走って 追いこす・火山の けむりが もくもく 上がる"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'dino'
RUN_S = 0.5        # ギャロップ 1回の 秒
GROUND_S = 2.5     # 手前の 地面が 1まい 流れる 秒（ひづめの 動きに 合わせる）
MID_S = 5.75       # しげみが 1まい 流れる 秒（第4.94版：背景の 恐竜を 9秒・6秒ごとに 通す ため 少し 速く＝67.8px／秒）
VX, VY = 84, 44    # 火山の 口（第4.93版：噴火が 上の 絵に おさまる ように 少し 低く）
LAVA_K = (112 - VY) / 80.0   # 溶岩の すじの 長さ（火山の 高さに 合わせる）

GREEN = dict(d='#3E6630', m='#5A8A3E', l='#7FB04E', ll='#A8CF6A')


# ---------------------------------------------------------------- 絵
def sky_svg():
    """空：上は 青みの 灰色 → 地平線は もやの かかった だいだい・遠い 山なみ・火山（溶岩の すじ）"""
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#86BFD0'/><stop offset='.5' stop-color='#E9DDB2'/>"
            "<stop offset='.8' stop-color='#F4BE82'/><stop offset='1' stop-color='#EFA36A'/></linearGradient>"
            "<linearGradient id='v' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#4A3D48'/><stop offset='.55' stop-color='#5E4E58'/><stop offset='1' stop-color='#3C3140'/></linearGradient>"
            "<radialGradient id='h' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FFE0A0' stop-opacity='.8'/><stop offset='1' stop-color='#FFC27A' stop-opacity='0'/></radialGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
    o += "<circle cx='300' cy='70' r='46' fill='url(#h)'/><circle cx='300' cy='70' r='11' fill='#FFF0C8' opacity='.85'/>"
    # 遠い 山なみ（もや）
    R = rnd(5)
    for col, base, amp, k0, op in (('#B8A2A8', 84, 9, 0.6, .7), ('#9C8592', 92, 7, 1.7, .8)):
        pts = [(x, base - amp * (0.6 + 0.4 * math.sin(x / 37 + k0)) * (0.7 + 0.3 * math.sin(x / 13 + k0 * 2))) for x in range(140, W + 12, 12)]
        o += f"<path d='M140 {base + 30} L{P(pts, False)[1:]} L{W + 10} {base + 30} Z' fill='{col}' opacity='{op}'/>"
    # 火山
    o += (f"<path d='M-14 112 C10 100 34 {VY + 38} 54 {VY + 14} C62 {VY + 4} 70 {VY} {VX - 10} {VY} L{VX + 12} {VY} C{VX + 22} {VY + 2} {VX + 30} {VY + 12} {VX + 40} {VY + 24} "
          f"C{VX + 62} {VY + 48} {VX + 84} 100 {VX + 110} 112 Z' fill='url(#v)'/>")
    o += f"<path d='M{VX - 10} {VY} L{VX + 12} {VY} L{VX + 8} {VY + 4} L{VX - 6} {VY + 4} Z' fill='#2E2430'/>"
    o += f"<path d='M{VX + 12} {VY} C{VX + 22} {VY + 2} {VX + 30} {VY + 12} {VX + 40} {VY + 24} C{VX + 62} {VY + 48} {VX + 84} 100 {VX + 110} 112 L{VX + 70} 112 C{VX + 50} 92 {VX + 30} {VY + 34} {VX + 14} {VY + 8} Z' fill='#2E2430' opacity='.45'/>"
    for k in range(6):                                                   # 岩の すじ
        x = VX - 40 + k * 16
        o += f"<path d='M{x} {104 - k % 2 * 6} q6 -10 8 -22' fill='none' stroke='#3A2E38' stroke-width='1.2' opacity='.6'/>"
    # 溶岩の すじ（口から 下へ）
    lava = [(VX - 4, VY + 3, [(-6, 18), (-14, 36), (-12, 54), (-22, 76)]), (VX + 6, VY + 3, [(8, 16), (12, 34), (24, 52)])]
    for x0, y0, segs in lava:
        pts = [(x0, y0)] + [(x0 + dx, y0 + dy * LAVA_K) for dx, dy in segs]
        o += f"<path d='{smooth(pts, close=False)}' fill='none' stroke='#C8401A' stroke-width='5' stroke-linecap='round'/>"
        o += f"<path d='{smooth(pts, close=False)}' fill='none' stroke='#FF7A2E' stroke-width='3' stroke-linecap='round'/>"
        o += f"<path d='{smooth(pts[:3], close=False)}' fill='none' stroke='#FFC45A' stroke-width='1.4' stroke-linecap='round'/>"
    return doc(W, H, o, defs=defs)


def glow_svg():
    """火山の 口の あかり（ゆっくり ゆらぐ）"""
    defs = ("<radialGradient id='g' cx='.5' cy='.6' r='.5'><stop offset='0' stop-color='#FFD27A' stop-opacity='.95'/><stop offset='.4' stop-color='#FF8A3A' stop-opacity='.55'/>"
            "<stop offset='1' stop-color='#FF6A2A' stop-opacity='0'/></radialGradient>")
    return doc(60, 40, "<ellipse cx='30' cy='24' rx='30' ry='16' fill='url(#g)'/>", defs=defs)


def puff_svg(c='#8E8088', c2='#B3A6A8'):
    return doc(40, 32, f"<circle cx='14' cy='18' r='11' fill='{c}'/><circle cx='26' cy='16' r='12' fill='{c}'/><circle cx='20' cy='10' r='9' fill='{c}'/>"
                       f"<circle cx='16' cy='14' r='7' fill='{c2}' opacity='.8'/><circle cx='24' cy='11' r='5' fill='{c2}' opacity='.7'/>")


def cycad(x, base, s, R):
    """ソテツ（太い 幹・まわりに 葉）"""
    o = (f"<path d='M{f(x - 4 * s)} {base} C{f(x - 5 * s)} {f(base - 10 * s)} {f(x - 3 * s)} {f(base - 18 * s)} {f(x - 2.4 * s)} {f(base - 22 * s)} "
         f"L{f(x + 2.4 * s)} {f(base - 22 * s)} C{f(x + 3 * s)} {f(base - 18 * s)} {f(x + 5 * s)} {f(base - 10 * s)} {f(x + 4 * s)} {base} Z' fill='#8A6A44'/>")
    for k in range(4):
        y = base - 4 * s - k * 5 * s
        o += f"<path d='M{f(x - 3.4 * s)} {f(y)} q{f(3.4 * s)} {f(2 * s)} {f(6.8 * s)} 0' fill='none' stroke='#6A4E30' stroke-width='{f(0.9 * s)}'/>"
    top = (x, base - 22 * s)
    for a in (-160, -130, -100, -75, -50, -20, 200):
        r = math.radians(a)
        L = (16 + R.uniform(-2, 3)) * s
        ex, ey = top[0] + math.cos(r) * L, top[1] + math.sin(r) * L * 0.7 + 4 * s
        cx, cy = top[0] + math.cos(r) * L * 0.5, top[1] + math.sin(r) * L * 0.5 - 4 * s
        o += f"<path d='M{f(top[0])} {f(top[1])} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['d']}' stroke-width='{f(4.2 * s)}' stroke-linecap='round'/>"
        o += f"<path d='M{f(top[0])} {f(top[1])} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['m']}' stroke-width='{f(2.6 * s)}' stroke-linecap='round' stroke-dasharray='{f(1.6 * s)} {f(0.8 * s)}'/>"
    return o


def treefern(x, base, s):
    """木の シダ（細い 幹・上に 弓なりの 葉）"""
    o = f"<path d='M{f(x)} {base} C{f(x - 2 * s)} {f(base - 18 * s)} {f(x + 2 * s)} {f(base - 34 * s)} {f(x)} {f(base - 44 * s)}' fill='none' stroke='#6E5236' stroke-width='{f(2.6 * s)}' stroke-linecap='round'/>"
    top = (x, base - 44 * s)
    for a, L in ((-170, 20), (-140, 18), (-110, 14), (-70, 14), (-40, 18), (-10, 20)):
        r = math.radians(a)
        ex, ey = top[0] + math.cos(r) * L * s, top[1] + math.sin(r) * L * s * 0.5 + 9 * s
        cx, cy = top[0] + math.cos(r) * L * s * 0.55, top[1] - 5 * s
        o += f"<path d='M{f(top[0])} {f(top[1])} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['d']}' stroke-width='{f(3.4 * s)}' stroke-linecap='round'/>"
        o += f"<path d='M{f(top[0])} {f(top[1])} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['l']}' stroke-width='{f(1.6 * s)}' stroke-linecap='round' stroke-dasharray='{f(1.4 * s)} {f(1 * s)}'/>"
    return o


def bush(x, base, s, col1, col2):
    return (f"<path d='M{f(x - 14 * s)} {base} C{f(x - 16 * s)} {f(base - 10 * s)} {f(x - 6 * s)} {f(base - 16 * s)} {f(x)} {f(base - 12 * s)} "
            f"C{f(x + 6 * s)} {f(base - 18 * s)} {f(x + 16 * s)} {f(base - 10 * s)} {f(x + 14 * s)} {base} Z' fill='{col1}'/>"
            f"<path d='M{f(x - 8 * s)} {f(base - 8 * s)} q{f(4 * s)} {f(-6 * s)} {f(9 * s)} {f(-3 * s)}' fill='none' stroke='{col2}' stroke-width='{f(1.6 * s)}' stroke-linecap='round'/>")


def triceratops(x, base, s):
    """草を 食べる トリケラトプス（左向き・頭を 下げる）"""
    c, cd, cl = '#C8874A', '#9A6232', '#E8B57A'
    o = f"<ellipse cx='{f(x + 4 * s)}' cy='{f(base + 1)}' rx='{f(26 * s)}' ry='{f(3 * s)}' fill='#5A4020' opacity='.25'/>"
    for lx in (x - 10 * s, x + 14 * s):                                  # おくの 足
        o += f"<rect x='{f(lx)}' y='{f(base - 12 * s)}' width='{f(6 * s)}' height='{f(12 * s)}' rx='{f(2 * s)}' fill='{cd}'/>"
    o += f"<path d='M{f(x + 30 * s)} {f(base - 16 * s)} Q{f(x + 40 * s)} {f(base - 14 * s)} {f(x + 44 * s)} {f(base - 8 * s)} Q{f(x + 36 * s)} {f(base - 10 * s)} {f(x + 28 * s)} {f(base - 10 * s)} Z' fill='{c}'/>"
    o += f"<ellipse cx='{f(x + 8 * s)}' cy='{f(base - 18 * s)}' rx='{f(23 * s)}' ry='{f(12 * s)}' fill='{c}'/>"
    o += f"<path d='M{f(x - 12 * s)} {f(base - 14 * s)} Q{f(x + 8 * s)} {f(base - 4 * s)} {f(x + 28 * s)} {f(base - 14 * s)}' fill='none' stroke='{cl}' stroke-width='{f(3 * s)}' opacity='.7'/>"
    for k in range(5):
        o += f"<circle cx='{f(x - 4 * s + k * 7 * s)}' cy='{f(base - 24 * s + (k % 2) * 3 * s)}' r='{f(1.8 * s)}' fill='{cd}' opacity='.7'/>"
    # 頭（下げて 草を 食べる）：えり かざり・角 3本
    hx, hy = x - 16 * s, base - 12 * s
    o += f"<path d='M{f(hx + 6 * s)} {f(hy - 12 * s)} C{f(hx + 14 * s)} {f(hy - 20 * s)} {f(hx + 18 * s)} {f(hy - 6 * s)} {f(hx + 12 * s)} {f(hy + 2 * s)} Z' fill='{cd}'/>"
    o += f"<path d='M{f(hx + 6 * s)} {f(hy - 12 * s)} C{f(hx + 13 * s)} {f(hy - 17 * s)} {f(hx + 15 * s)} {f(hy - 7 * s)} {f(hx + 11 * s)} {f(hy)}' fill='none' stroke='{cl}' stroke-width='{f(1.4 * s)}'/>"
    o += f"<path d='M{f(hx + 10 * s)} {f(hy - 6 * s)} C{f(hx + 4 * s)} {f(hy - 10 * s)} {f(hx - 6 * s)} {f(hy - 4 * s)} {f(hx - 8 * s)} {f(hy + 6 * s)} L{f(hx - 2 * s)} {f(hy + 9 * s)} C{f(hx + 4 * s)} {f(hy + 6 * s)} {f(hx + 10 * s)} {f(hy + 4 * s)} {f(hx + 12 * s)} {f(hy)} Z' fill='{c}'/>"
    o += f"<path d='M{f(hx + 2 * s)} {f(hy - 7 * s)} L{f(hx - 10 * s)} {f(hy - 13 * s)} L{f(hx)} {f(hy - 4 * s)} Z M{f(hx - 1 * s)} {f(hy - 4 * s)} L{f(hx - 12 * s)} {f(hy - 7 * s)} L{f(hx - 2 * s)} {f(hy - 1 * s)} Z' fill='#F4E6C8'/>"
    o += f"<path d='M{f(hx - 6 * s)} {f(hy + 3 * s)} L{f(hx - 12 * s)} {f(hy + 1 * s)} L{f(hx - 7 * s)} {f(hy + 6 * s)} Z' fill='#F4E6C8'/>"
    o += f"<circle cx='{f(hx + 3 * s)}' cy='{f(hy - 3 * s)}' r='{f(1.2 * s)}' fill='#2A1A10'/>"
    for lx in (x - 4 * s, x + 20 * s):                                   # 手前の 足
        o += f"<rect x='{f(lx)}' y='{f(base - 13 * s)}' width='{f(6.4 * s)}' height='{f(13 * s)}' rx='{f(2 * s)}' fill='{c}'/>"
    for k in range(4):                                                   # 口もとの 草
        o += f"<path d='M{f(hx - 10 * s + k * 2.4 * s)} {f(base + 0.5)} l{f(-1 * s)} {f(-5 * s)}' stroke='{GREEN['l']}' stroke-width='{f(1.1 * s)}' stroke-linecap='round'/>"
    return o


def mid_svg(w=W, h=60, seed=17):
    """しげみ（横に くり返す）：ソテツ・木の シダ・しげみ・岩・草を 食べる トリケラトプス。下の ふち＝地面との さかい"""
    R = rnd(seed)
    base = h - 6
    o = f"<path d='M0 {base - 6} C60 {base - 10} 120 {base - 4} 195 {base - 8} S330 {base - 4} {w} {base - 6} L{w} {h} L0 {h} Z' fill='#9C8A4E'/>"
    o += f"<path d='M0 {base - 2} H{w} V{h} H0 Z' fill='#B08A50'/>"
    items = [('tf', 24, 1.0), ('cy', 92, 0.9), ('bu', 140, 1.0), ('tc', 205, 0.72), ('cy', 268, 1.05), ('tf', 330, 0.85), ('bu', 372, 0.8)]
    for kind, x, s in items:
        for dx in (-w, 0, w):
            xx = x + dx
            if not (-60 < xx < w + 60):
                continue
            if kind == 'cy':
                o += cycad(xx, base, s, rnd(int(x)))
            elif kind == 'tf':
                o += treefern(xx, base, s)
            elif kind == 'bu':
                o += bush(xx, base, s, GREEN['m'], GREEN['ll'])
            elif kind == 'tc':
                o += triceratops(xx, base - 1, s)
    for i in range(10):
        x = R.uniform(0, w)
        for dx in (-w, 0, w):
            o += f"<ellipse cx='{f(x + dx)}' cy='{base - 1}' rx='{f(R.uniform(3, 6))}' ry='{f(R.uniform(2, 3.4))}' fill='#8A7A68'/>"
    return doc(w, h, o)


def ground_svg(w=W, h=44, seed=23):
    """手前の 地面（横に くり返す）：土・草の ふさ・小石・恐竜の 足あと（3本ゆび）"""
    R = rnd(seed)
    defs = ("<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#C9A262'/><stop offset='1' stop-color='#A47838'/></linearGradient>")
    o = f"<rect width='{w}' height='{h}' fill='url(#g)'/><rect width='{w}' height='2' fill='#8E7A40' opacity='.6'/>"
    for i in range(18):
        x, y = R.uniform(0, w), R.uniform(4, h - 3)
        for dx in (-w, 0, w):
            o += (f"<ellipse cx='{f(x + dx + .6)}' cy='{f(y + 1)}' rx='{f(R.uniform(1.6, 3.2))}' ry='{f(R.uniform(1, 1.8))}' fill='#7A5626' opacity='.45'/>"
                  f"<ellipse cx='{f(x + dx)}' cy='{f(y)}' rx='{f(R.uniform(1.4, 2.8))}' ry='{f(R.uniform(.9, 1.6))}' fill='#D9BC88'/>")
    for i in range(14):
        x, y = R.uniform(0, w), R.uniform(3, h - 2)
        for dx in (-w, 0, w):
            for k in range(4):
                o += f"<path d='M{f(x + dx + k * 1.4)} {f(y)} l{f(R.uniform(-1.5, 1.5))} {f(-R.uniform(3, 6))}' stroke='{R.choice((GREEN['m'], GREEN['l']))}' stroke-width='1' stroke-linecap='round'/>"
    for x, y in ((70, 20), (96, 30), (250, 18), (276, 28)):              # 足あと
        for dx in (-w, 0, w):
            xx = x + dx
            o += (f"<path d='M{xx} {y} l-5 -3.4 M{xx} {y} l-5.6 .4 M{xx} {y} l-4.6 3.6' stroke='#7A5626' stroke-width='1.8' stroke-linecap='round' opacity='.6'/>"
                  f"<ellipse cx='{xx + 1.4}' cy='{y}' rx='2.4' ry='1.8' fill='#7A5626' opacity='.5'/>")
    return doc(w, h, o, defs=defs)


# ---- 首の 長い 恐竜（第4.93版：背景の 恐竜＝しげみと 同じ はやさで 流れる・足は 地面に 止まった まま。首は 3つの ふしで まがって しだを 食べる）
SC, SCD, SCL, SCS = '#7E9E5E', '#5D7A44', '#B8C98A', '#6A8A4E'
BRO = (196, 126)            # 首の 長い 恐竜の 箱（はば・高さ）。足の 下＝y 120
BRO_NECK = (72, 58)         # 首の 根もと（箱の 中）
NECK_N = 8                  # 第4.94版：首は 8つの 短い ふし（まがりを みんなで 分けて なめらかな 弓なりに：まさちゃん「首の角度、動き方がおかしいから自然にして！」）
NECK_SEG = 9.0              # ふし 1つの 長さ（首 ぜんぶで 72）
NECK_W = [21.0 - 10.5 * k / NECK_N for k in range(NECK_N + 1)]   # 関節ごとの 太さ（根もと 21 → 頭 10.5）
BRO_S = 9.0                 # 首の 長い 恐竜が 通る 間かく（秒）＝1回りで 1回 食べる
STEGO_S = 6.0               # 背中に 板の ある 恐竜が 通る 間かく（秒）


def bro_part(name):
    """首の 長い 恐竜（左向き・立って いる）の 部品：shadow・legF（おくの 足）・tail・body・legN（手前の 足）・fern（食べる しだ）"""
    bw, bh = BRO
    o = ''
    if name == 'shadow':
        o += "<ellipse cx='112' cy='120.5' rx='58' ry='3.8' fill='#4A3A1E' opacity='.26'/>"
    elif name in ('legF', 'legN'):
        xs = (94, 150) if name == 'legF' else (82, 140)
        col = SCD if name == 'legF' else SC
        for x0 in xs:
            o += (f"<path d='M{x0 - 8} 76 L{x0 + 8} 76 L{x0 + 7.4} 112 Q{x0 + 8.4} 120 {x0 + 3} 120 L{x0 - 5} 120 Q{x0 - 9} 120 {x0 - 8} 113 Z' fill='{col}'/>"
                  f"<path d='M{x0 - 7} 117.6 h3 M{x0 - 2} 118 h3 M{x0 + 3} 117.6 h3' stroke='{mix(col, '#F0E6C8', .55)}' stroke-width='1.6' stroke-linecap='round'/>")
            if name == 'legN':
                o += f"<path d='M{x0 - 5} 80 V108' stroke='{SCL}' stroke-width='1.8' stroke-linecap='round' opacity='.4'/>"
    elif name == 'tail':
        o += f"<path d='M150 52 C168 54 182 66 194 92 C186 82 172 74 152 76 Z' fill='{SC}'/>"
        o += f"<path d='M156 70 C170 72 182 80 190 88' fill='none' stroke='{SCL}' stroke-width='2' stroke-linecap='round' opacity='.55'/>"
    elif name == 'body':
        o += f"<ellipse cx='114' cy='66' rx='52' ry='24' fill='{SC}'/>"
        o += f"<path d='M70 74 Q114 96 158 74 Q114 86 70 74 Z' fill='{SCL}' opacity='.8'/>"
        o += "<path d='M76 50 Q114 36 152 50' fill='none' stroke='#9CBC78' stroke-width='3' stroke-linecap='round' opacity='.7'/>"
        R = rnd(9)
        for i in range(10):
            o += f"<ellipse cx='{f(80 + i * 7.4 + R.uniform(-2, 2))}' cy='{f(58 + R.uniform(-6, 5))}' rx='{f(R.uniform(2.4, 4))}' ry='{f(R.uniform(1.6, 2.6))}' fill='{SCS}' opacity='.75'/>"
    elif name == 'fern':
        R = rnd(31)
        for k in range(9):                                               # 食べる しだ（頭の 下の 地面）
            x = 18 + k * 5.2 + R.uniform(-1.5, 1.5)
            a = math.radians(-150 + k * 15 + R.uniform(-6, 6))
            L = R.uniform(12, 18)
            ex, ey = x + math.cos(a) * L * 0.5, 120 + math.sin(a) * L
            o += f"<path d='M{f(x)} 120 Q{f(x + math.cos(a) * L * 0.2)} {f(120 - L * 0.7)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['d']}' stroke-width='3.6' stroke-linecap='round'/>"
            o += f"<path d='M{f(x)} 120 Q{f(x + math.cos(a) * L * 0.2)} {f(120 - L * 0.7)} {f(ex)} {f(ey)}' fill='none' stroke='{GREEN['l']}' stroke-width='1.6' stroke-linecap='round' stroke-dasharray='1.4 1'/>"
    return doc(bw, bh, o)


def neck_seg(k):
    """首の ふし k（関節が 絵の (ox, oy)・左へ のびる・はしは まるい＝となりの ふしと 重なって 角が 出ない）。返り値：(svg, ox, oy, w, h)"""
    L = NECK_SEG
    w0, w1 = NECK_W[k], NECK_W[k + 1]
    ox, oy = L + w1 / 2 + 1, w0 / 2 + 1
    w, h = ox + w0 / 2 + 1, w0 + 2
    T_ = lambda x, y: (x + ox, y + oy)
    a, b = T_(0, -w0 / 2), T_(-L, -w1 / 2)
    c, d = T_(-L, w1 / 2), T_(0, w0 / 2)
    o = (f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])} A{f(w1 / 2)} {f(w1 / 2)} 0 0 0 {f(c[0])} {f(c[1])} L{f(d[0])} {f(d[1])} A{f(w0 / 2)} {f(w0 / 2)} 0 0 0 {f(a[0])} {f(a[1])} Z' fill='{SC}'/>")
    a, b = T_(0, w0 * 0.3), T_(-L, w1 * 0.3)                              # のどの 明るい すじ（となりと つながる）
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{SCL}' stroke-width='{f(w0 * 0.3)}' stroke-linecap='round' opacity='.7'/>"
    a, b = T_(0, -w0 * 0.27), T_(-L, -w1 * 0.27)                          # 首の 上の 光
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='#9CBC78' stroke-width='1.6' stroke-linecap='round' opacity='.55'/>"
    if k % 2 == 0:
        x, y = T_(-L * 0.5, -w0 * 0.05)
        o += f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='{f(1.6 + w0 * 0.05)}' ry='{f(1.1 + w0 * 0.03)}' fill='{SCS}' opacity='.75'/>"
    return doc(w, h, o), ox, oy, w, h


def bro_head():
    """頭（首の 先が 絵の (ox, oy)・左へ のびる）：首の 先に なめらかに つながる まるい 頭の うしろ・まるい 鼻・目・にっこり"""
    ox, oy, w, h = 28, 10, 32, 20
    r0 = NECK_W[-1] / 2
    o = (f"<path d='M{f(ox + r0 * 0.6)} {f(oy - r0)} C{ox - 5} {oy - 8.2} {ox - 17} {oy - 7.6} {ox - 23.4} {oy - 2.8} C{ox - 26} {oy - 0.2} {ox - 25.2} {oy + 3.6} {ox - 21} {oy + 4.4} "
         f"L{ox - 7} {oy + 5} C{f(ox - 1)} {f(oy + r0)} {f(ox + r0 * 0.6)} {f(oy + r0)} {f(ox + r0 * 0.6)} {f(oy + r0 * 0.4)} Z' fill='{SC}'/>")
    o += f"<circle cx='{ox}' cy='{oy}' r='{f(r0)}' fill='{SC}'/>"
    o += f"<path d='M{ox - 21} {oy - 3} C{ox - 15} {oy - 6.8} {ox - 6} {oy - 7} {ox + 1} {oy - 4.6}' fill='none' stroke='#9CBC78' stroke-width='1.6' stroke-linecap='round' opacity='.6'/>"
    o += f"<circle cx='{ox - 9}' cy='{oy - 2.4}' r='1.9' fill='#1E2414'/><circle cx='{ox - 9.6}' cy='{oy - 3}' r='.7' fill='#FFFFFF'/>"
    o += f"<circle cx='{ox - 22.4}' cy='{oy - 1.4}' r='.9' fill='#2E3A20'/>"
    o += f"<path d='M{ox - 22} {oy + 2.4} Q{ox - 16} {oy + 4.6} {ox - 10} {oy + 2.6}' fill='none' stroke='#2E3A20' stroke-width='1' stroke-linecap='round'/>"
    o += f"<ellipse cx='{ox - 13}' cy='{oy + 1.4}' rx='2' ry='1.2' fill='#E89A7A' opacity='.6'/>"
    return doc(w, h, o), ox, oy, w, h


def neck_poses():
    """首の 形＝(根もとの 向き φ0・ふしごとの まがり δ・頭の 向き)（画面の 角度・度：180＝左・270＝上）。
       up＝首を ゆるい 弓なりに 上げて まわりを 見る・down＝首を なめらかに 下へ まげて しだを 食べる"""
    up = (204.0, 3.4, 192.0)
    down = (194.0, -12.0, 102.0)
    return up, down


def neck_rel(pose, look=0.0, chew=0.0):
    """首の 形 → 関節ごとの CSS の 回転（はじめは 根もとの 向き−180、あとは まがり δ・最後は 頭）"""
    a0, d, ah = pose
    d_last = d + chew * 0.4
    ang = [a0 + d * k for k in range(NECK_N - 1)] + [a0 + d * (NECK_N - 2) + d_last]
    rel = [ang[0] - 180.0] + [ang[k] - ang[k - 1] for k in range(1, NECK_N)]
    rel.append(ah + look + chew - ang[-1])
    return rel


STEGO = (150, 82)


def stego_svg(part):
    """背中に 板の ある 恐竜（左向き・立って 草を 食べる）：body（体・足・板）・tail（しっぽの とげ）・head（頭）"""
    c, cd, cl, pl, pd = '#6E9A8E', '#4E7A6E', '#A8CCC0', '#E0884A', '#B8642E'
    w, h = STEGO
    o = ''
    if part == 'body':
        o += "<ellipse cx='76' cy='79' rx='44' ry='3' fill='#4A3A1E' opacity='.24'/>"
        for x0 in (52, 96):                                              # おくの 足
            o += f"<rect x='{x0 - 5}' y='54' width='10' height='24' rx='3' fill='{cd}'/>"
        for k in range(9):                                               # 背中の 板
            x = 40 + k * 8.4
            hh = 13 + 9 * math.sin(math.pi * (k + 0.5) / 9)
            yb = 46 - 10 * math.sin(math.pi * (k + 0.5) / 9)
            o += f"<path d='M{f(x - 5)} {f(yb + 4)} L{f(x)} {f(yb - hh)} L{f(x + 5)} {f(yb + 4)} Z' fill='{pl if k % 2 else pd}'/>"
        o += f"<path d='M28 58 C30 36 60 26 82 28 C104 30 122 42 126 58 C110 66 50 68 28 58 Z' fill='{c}'/>"
        o += f"<path d='M34 60 Q76 72 120 60 Q76 66 34 60 Z' fill='{cl}' opacity='.8'/>"
        for x0 in (44, 90):                                              # 手前の 足
            o += f"<rect x='{x0 - 5.6}' y='56' width='11.2' height='23' rx='3.4' fill='{c}'/><path d='M{x0 - 4} 77 h8' stroke='{mix(c, '#F0E6C8', .5)}' stroke-width='1.6' stroke-linecap='round'/>"
        R = rnd(5)
        for i in range(8):
            o += f"<ellipse cx='{f(44 + i * 9 + R.uniform(-2, 2))}' cy='{f(46 + R.uniform(-4, 5))}' rx='2.6' ry='1.7' fill='{cd}' opacity='.6'/>"
    elif part == 'tail':
        o += f"<path d='M120 50 C134 52 144 58 150 66 C140 62 130 60 118 62 Z' fill='{c}'/>"
        for x, y, a in ((140, 56, -60), (146, 60, -30), (143, 66, 40), (148, 64, 70)):
            r = math.radians(a)
            o += f"<path d='M{x - 2} {y} L{f(x + math.cos(r) * 9)} {f(y + math.sin(r) * 9)} L{x + 2} {y} Z' fill='#F0E6C8'/>"
    elif part == 'head':
        o += (f"<path d='M34 52 C26 54 18 60 12 66 C8 70 10 75 15 74 C20 73 24 70 28 66 C32 62 36 58 38 56 Z' fill='{c}'/>"
              f"<circle cx='17' cy='68' r='1.4' fill='#1E2414'/><path d='M10 72 Q14 74 18 72' fill='none' stroke='#2E3A20' stroke-width='.9' stroke-linecap='round'/>")
        for k in range(4):                                               # 口もとの 草
            o += f"<path d='M{6 + k * 2.4} 80 l-1 -6' stroke='{GREEN['l']}' stroke-width='1.2' stroke-linecap='round'/>"
    return doc(w, h, o)


# ---- ティラノサウルス（第4.94版：まさちゃん「17秒に1回、ティラノサウルスが出てきて、それを馬達で避ける演出いれて！」）
#   オリジナルの かわいめの ティラノ（大きな 頭・小さな 手・しまの せなか）。絵は 右向きで 作って ページで 左右を 反転（左へ 走る）。
#   右から 走って きて ほえる（頭を 上げて 口を あける・ほえる 線）→ 2頭の 馬が 上下に わかれた あいだを 走りぬけて 左へ。
TREX_S = 17.0               # 1回り（秒）
TREX_AT = 3.0               # 1回りの 中で 出て くる 時刻（秒）
TREX_RUN = 0.36             # 足の 1回り（秒）
TREX_V = 300.0              # 画面での はやさ（px／秒・左へ）
TREX_SC = 0.8               # 大きさ
TREX_GROUND = 138           # 足の 下（画面の y）
TR_BOX = (-10, 0, 164, 104)  # 絵の 箱（左・上・はば・高さ：右向きの 座標）
TR_HIP = (60, 56)
TR_LT, TR_LS = 21.0, 22.0   # もも・すね
TR_ANK = 8.0                # 足首の 高さ
TR_C, TR_D, TR_S2, TR_B = '#C46A3E', '#8E4426', '#A4502E', '#F6DCAE'


def trex_part(name, far=False):
    """ティラノの 部品（右向き・TR_BOX の 座標・足は 関節が 原点）"""
    c, d, s2, b = (mix(TR_C, '#2A1410', .3), mix(TR_D, '#2A1410', .3), mix(TR_S2, '#2A1410', .3), mix(TR_B, '#2A1410', .3)) if far else (TR_C, TR_D, TR_S2, TR_B)
    bx, by, bw, bh = TR_BOX
    o = ''
    if name == 'tail':
        o += f"<path d='M44 40 C26 36 10 32 -8 26 C6 36 22 48 42 60 Z' fill='{c}'/>"
        for k, x in enumerate((30, 18, 6)):
            o += f"<path d='M{x} {31 + k * -1.6} q2 4 1 8' fill='none' stroke='{s2}' stroke-width='2.4' stroke-linecap='round'/>"
        o += f"<path d='M40 56 C26 48 12 40 -4 30' fill='none' stroke='{b}' stroke-width='2.2' stroke-linecap='round' opacity='.6'/>"
    elif name == 'body':
        o += f"<ellipse cx='62' cy='48' rx='34' ry='22' transform='rotate(-14 62 48)' fill='{c}'/>"
        o += f"<path d='M78 34 C86 28 94 24 102 22 L108 38 C100 44 92 50 86 56 Z' fill='{c}'/>"          # 首
        o += f"<path d='M40 62 C56 74 82 66 96 50 C88 58 70 66 52 64 Z' fill='{b}'/>"                  # おなか
        for k, (x, y) in enumerate(((50, 30), (62, 27), (74, 25), (86, 25))):                        # せなかの しま
            o += f"<path d='M{x} {y} q3 5 1 10' fill='none' stroke='{s2}' stroke-width='3' stroke-linecap='round'/>"
    elif name in ('arm',):
        o += f"<path d='M88 56 C94 58 98 62 100 66 L97 67 C95 64 92 61 87 60 Z' fill='{d if far else c}'/>"
        o += f"<path d='M100 66 l3 1 M100 66 l1.6 3' stroke='{b}' stroke-width='1.4' stroke-linecap='round'/>"
    elif name == 'head':
        o += (f"<path d='M96 24 C100 12 116 6 132 10 C142 12 150 18 151 26 C152 32 148 35 142 35 L106 38 C100 38 94 32 96 24 Z' fill='{c}'/>"
              f"<path d='M100 14 C112 8 128 8 142 14' fill='none' stroke='{s2}' stroke-width='2.4' stroke-linecap='round' opacity='.8'/>"
              f"<path d='M110 15 q6 -4 12 -1' fill='none' stroke='{d}' stroke-width='2.6' stroke-linecap='round'/>")       # まゆ
        o += "<circle cx='117' cy='21' r='5.6' fill='#FFFFFF'/><circle cx='118.6' cy='21.6' r='3.2' fill='#2A1410'/><circle cx='119.6' cy='20.4' r='1.1' fill='#FFFFFF'/>"
        o += f"<ellipse cx='145' cy='20' rx='1.6' ry='1' fill='{d}'/>"
        for k in range(6):                                               # 上の 歯
            x = 112 + k * 6
            o += f"<path d='M{x} 35.6 l2.2 4 l2.2 -4 Z' fill='#FFFDF2'/>"
        o += f"<ellipse cx='128' cy='29' rx='3' ry='1.8' fill='#F09A78' opacity='.55'/>"
    elif name == 'jaw':                                                  # 下あご（ちょうつがい 102,38）＋上に 口の 中（とじると 頭の うしろに かくれる）
        o += "<path d='M101 38.4 L116 30 L130 23 L143 18.6 L147.4 22 L148 39 C140 41.4 120 42.4 104 41 Z' fill='#6E1A14'/>"
        o += "<path d='M112 40.6 C122 42.2 134 41.6 143 38.8' fill='none' stroke='#E8666A' stroke-width='3' stroke-linecap='round'/>"
        o += (f"<path d='M102 36 C110 40 126 41 142 38 C146 37 148 39 146 42 C140 48 120 50 106 46 C100 44 98 40 102 36 Z' fill='{c}'/>"
              f"<path d='M106 44 C120 48 134 46 144 41' fill='none' stroke='{b}' stroke-width='2' stroke-linecap='round' opacity='.7'/>")
        for k in range(5):                                               # 下の 歯
            x = 116 + k * 6
            o += f"<path d='M{x} 39.6 l2 -3.6 l2 3.6 Z' fill='#FFFDF2'/>"
    return doc(bw, bh, o, vb=f'{bx} {by} {bw} {bh}')


def trex_leg_seg(kind, far=False):
    """足の ふし（関節が 原点・下へ のびる）：thigh（太い もも）・shin（すね）・foot（足首と 3本の ゆび）。返り値：(svg, ox, oy, w, h)"""
    c, d, b = (mix(TR_C, '#2A1410', .3), mix(TR_D, '#2A1410', .3), mix(TR_B, '#2A1410', .3)) if far else (TR_C, TR_D, TR_B)
    if kind == 'thigh':                                                  # 太い もも（上が ふくらむ・ふちに こい 線で 体と 分ける）
        ox, oy, w, h = 17, 17, 34, 46
        L = TR_LT
        o = (f"<path d='M{ox - 15} {oy - 4} C{ox - 16} {oy + 10} {ox - 8} {oy + L - 2} {ox - 4} {oy + L + 2} C{ox} {oy + L + 6} {ox + 6} {oy + L + 4} {ox + 7} {oy + L} "
             f"C{ox + 12} {oy + 12} {ox + 16} {oy + 2} {ox + 14} {oy - 8} C{ox + 10} {oy - 16} {ox - 10} {oy - 16} {ox - 15} {oy - 4} Z' fill='{c}' stroke='{d}' stroke-width='1.6'/>")
        o += f"<path d='M{ox + 8} {oy - 8} C{ox + 11} {oy - 1} {ox + 9} {oy + 8} {ox + 5} {oy + 15}' fill='none' stroke='{b}' stroke-width='2.4' stroke-linecap='round' opacity='.55'/>"
        o += f"<path d='M{ox - 9} {oy - 2} q-2 9 2 17' fill='none' stroke='{d}' stroke-width='2' stroke-linecap='round' opacity='.5'/>"
    elif kind == 'shin':
        ox, oy, w, h = 9, 8, 18, 34
        L = TR_LS
        o = (f"<path d='M{ox - 6.4} {oy} C{ox - 6} {oy + 8} {ox - 4.6} {oy + L - 6} {ox - 3.6} {oy + L} L{ox + 3.6} {oy + L} C{ox + 4.4} {oy + L - 6} {ox + 6} {oy + 8} {ox + 6.4} {oy} Z' fill='{c}' stroke='{d}' stroke-width='1.2'/>"
             f"<circle cx='{ox}' cy='{oy}' r='6.6' fill='{c}'/>")
    else:                                                                # 足首 → つま先（地面に ふむ 形・前が +x）
        ox, oy, w, h = 7, 6, 30, 16
        A = TR_ANK
        o = (f"<path d='M{ox - 4} {oy - 3} L{ox + 4} {oy - 3} L{ox + 7} {oy + A - 2.4} L{ox + 18} {oy + A - 1.6} C{ox + 21} {oy + A - 1} {ox + 21.4} {oy + A + 1.6} {ox + 18.6} {oy + A + 1.6} "
             f"L{ox - 5} {oy + A + 1.6} C{ox - 6.4} {oy + A} {ox - 6} {oy + 2} {ox - 4} {oy - 3} Z' fill='{c}' stroke='{d}' stroke-width='1.2' stroke-linejoin='round'/>")
        for k in range(3):                                               # つめ
            o += f"<path d='M{ox + 12 + k * 3.2} {oy + A + 1.6} l2.2 .9' stroke='#FFFDF2' stroke-width='1.6' stroke-linecap='round'/>"
    return doc(w, h, o), ox, oy, w, h


def trex_leg_keys(off):
    """走る 足（右向き）：足首の 通る 道（地面に ついて いる 間は うしろへ まっすぐ＝地面と 同じ はやさ・宙は 上げて 前へ）→ もも・すね・足の 回転（NT+1 コマ）"""
    NT = 16
    stride = (TREX_V - 189.0) * TREX_RUN / 2 / TREX_SC                  # 地面に ついた 足が うしろへ 進む 長さ（絵の 座標）
    lift = 13.0
    out = ([], [], [])
    for i in range(NT + 1):
        q = (i / NT + off) % 1.0
        if q < 0.5:
            u = q / 0.5
            ax, ay, toe = 4 + stride / 2 - stride * u, 100 - TR_ANK, 0.0
        else:
            u = (q - 0.5) / 0.5
            e = 0.5 - 0.5 * math.cos(math.pi * u)
            ax, ay = 4 - stride / 2 + stride * e, 100 - TR_ANK - lift * math.sin(math.pi * u)
            toe = 34 * math.sin(math.pi * u)                             # 宙では つま先が 下へ
        px, py = TR_HIP[0], TR_HIP[1] + trex_bob(q)                     # 腰は からだと いっしょに 上下（足の 下は 地面の まま）
        tx, ty = px + ax, ay
        dx, dy = tx - px, ty - py
        dd = min(math.hypot(dx, dy), TR_LT + TR_LS - 0.01)
        a = math.atan2(dy, dx)
        cc = (TR_LT ** 2 + dd ** 2 - TR_LS ** 2) / (2 * TR_LT * dd)
        bb = math.acos(max(-1.0, min(1.0, cc)))
        a1 = a - bb                                                      # ひざは 前（+x）
        kx, ky = px + TR_LT * math.cos(a1), py + TR_LT * math.sin(a1)
        a2 = math.atan2(ty - ky, tx - kx)
        r1 = math.degrees(a1) - 90
        r2 = math.degrees(a2) - 90 - r1
        r3 = toe - (r1 + r2)
        out[0].append(r1)
        out[1].append(r2)
        out[2].append(r3)
    return out


# ---- 火山の 噴火（第4.93版：8秒に 1回・4回に 1回は 大噴火＝長い 1回りの 中で 大噴火の 順番が かわる）
ERUPT_S = 8.0
BIG_TOTAL = 128.0
BIG_AT = (8.0, 56.0, 80.0, 96.0)     # 大噴火の 時刻（32秒ごとの 組で 2・4・3・1回目）


def lava_svg(r=6.0):
    defs = ("<radialGradient id='l' cx='.42' cy='.38' r='.6'><stop offset='0' stop-color='#FFF2B0'/><stop offset='.35' stop-color='#FFC24A'/>"
            "<stop offset='.75' stop-color='#F06A1E'/><stop offset='1' stop-color='#B8320E'/></radialGradient>")
    s_ = 2 * r + 2
    return doc(s_, s_, f"<circle cx='{f(s_ / 2)}' cy='{f(s_ / 2)}' r='{f(r)}' fill='url(#l)'/>", defs=defs)


def column_svg(big=False):
    """噴き上がる 溶岩の 柱（下が 火口・上に 広がる ほのお形）"""
    w, h = (40, 66) if big else (28, 42)
    defs = ("<linearGradient id='c' x1='0' y1='1' x2='0' y2='0'><stop offset='0' stop-color='#FFE9A0'/><stop offset='.3' stop-color='#FFB43A'/>"
            "<stop offset='.75' stop-color='#F06A1E' stop-opacity='.9'/><stop offset='1' stop-color='#C8401A' stop-opacity='0'/></linearGradient>")
    o = (f"<path d='M{w * 0.42} {h} C{w * 0.36} {h * 0.7} {w * 0.12} {h * 0.42} {w * 0.18} {h * 0.18} C{w * 0.24} {h * 0.04} {w * 0.4} 0 {w * 0.5} {h * 0.08} "
         f"C{w * 0.6} 0 {w * 0.8} {h * 0.06} {w * 0.84} {h * 0.22} C{w * 0.9} {h * 0.44} {w * 0.64} {h * 0.7} {w * 0.58} {h} Z' fill='url(#c)'/>")
    o += f"<path d='M{w * 0.47} {h} C{w * 0.45} {h * 0.66} {w * 0.36} {h * 0.4} {w * 0.44} {h * 0.2} C{w * 0.5} {h * 0.34} {w * 0.56} {h * 0.66} {w * 0.53} {h} Z' fill='#FFF6C8' opacity='.85'/>"
    return doc(w, h, o, defs=defs)


def rock_svg():
    """飛ぶ 岩（ごつごつ・下の ふちが 溶岩で 赤く 光る）"""
    return doc(14, 12, "<path d='M1.6 7.4 L3 3.2 L6.6 1.2 L10.6 2 L12.8 5.6 L11.8 9.6 L7.4 11 L3.4 10.2 Z' fill='#3E3238' stroke='#241C22' stroke-width='.7' stroke-linejoin='round'/>"
                       "<path d='M3 3.2 L6.6 1.2 L10.6 2 L9 4.6 L5.4 4.4 Z' fill='#5A4C54'/>"
                       "<path d='M2.6 9 Q6.6 11.4 11.4 9.2' fill='none' stroke='#FF7A2E' stroke-width='1.4' stroke-linecap='round' opacity='.9'/>")


def eglow_svg(big=False):
    w, h = (130, 90) if big else (90, 60)
    defs = ("<radialGradient id='g' cx='.5' cy='.55' r='.5'><stop offset='0' stop-color='#FFE2A0' stop-opacity='.9'/><stop offset='.45' stop-color='#FF9A4A' stop-opacity='.45'/>"
            "<stop offset='1' stop-color='#FF7A3A' stop-opacity='0'/></radialGradient>")
    return doc(w, h, f"<ellipse cx='{w / 2}' cy='{h * 0.55}' rx='{w / 2}' ry='{h * 0.45}' fill='url(#g)'/>", defs=defs)


def flows_svg():
    """斜面の 溶岩の すじを 明るく（噴火の ときに 重ねる）"""
    o = ''
    lava = [(VX - 4, VY + 3, [(-6, 18), (-14, 36), (-12, 54), (-22, 76)]), (VX + 6, VY + 3, [(8, 16), (12, 34), (24, 52)])]
    for x0, y0, segs in lava:
        pts = [(x0, y0)] + [(x0 + dx, y0 + dy * LAVA_K) for dx, dy in segs]
        o += f"<path d='{smooth(pts, close=False)}' fill='none' stroke='#FFB43A' stroke-width='4.4' stroke-linecap='round'/>"
        o += f"<path d='{smooth(pts, close=False)}' fill='none' stroke='#FFF0A0' stroke-width='1.8' stroke-linecap='round'/>"
    return doc(W, H, o)


def arc_stops(x0, y0, vx, vy, t0, dur, n=7, g=1.0, s0=1.0, s1=0.6, spin=0):
    """放物線（t0 秒に 火口から 出て dur 秒で 落ちる）の 停止点：[(秒, 宣言)]。vx：横の 合計・vy：上がる 高さ"""
    out = [(t0 - 0.01, f'opacity:0;transform:translate({f(x0)}px,{f(y0)}px) scale({s0})'), (t0, f'opacity:1;transform:translate({f(x0)}px,{f(y0)}px) scale({s0})')]
    for k in range(1, n + 1):
        u = k / n
        x = x0 + vx * u
        y = y0 - vy * 4 * u * (1 - u) + g * 26 * u * u
        sc = s0 + (s1 - s0) * u
        op = 1.0 if u < 0.75 else max(0.0, 1 - (u - 0.75) / 0.25)
        rot = f' rotate({f(spin * u, 1)}deg)' if spin else ''
        out.append((t0 + dur * u, f'opacity:{f(op)};transform:translate({f(x)}px,{f(y)}px) scale({f(sc)}){rot}'))
    return out


def cycle_kf(name, stops, total):
    """[(秒, 宣言)] → 1回り total 秒の keyframes（0% と 100% は 最初の 隠れた 形）"""
    stops = sorted(stops, key=lambda q: q[0])
    hidden = stops[0][1]
    lst = [(0, hidden)] + [(max(0.0, min(100.0, 100 * t / total)), d) for t, d in stops] + [(100, hidden)]
    return kf(name, lst)


def events_kf(name, stops, total, at):
    """同じ 動き（stops：0秒 はじまり）を at の 時刻ごとに くり返す keyframes"""
    allst = []
    for t0 in at:
        allst += [(t0 + t, d) for t, d in stops]
    allst = sorted(allst, key=lambda q: q[0])
    hidden = stops[0][1]
    return kf(name, [(0, hidden)] + [(100 * t / total, d) for t, d in allst] + [(100, hidden)])


def runner_part(name):
    """馬と ならんで 走る 小さな 恐竜（ダチョウの ような 2本足・右向き）：部品ごと（同じ 箱 0 0 60 46）"""
    c, cd, cl = '#4FA88C', '#2E7A62', '#BFE6C8'
    o = ''
    if name in ('legF', 'legN'):
        col = cd if name == 'legF' else c
        o += (f"<path d='M27 25 L31 25 L33 36 L30 44 L27 44 L29 36 Z' fill='{col}'/>"
              f"<path d='M27 44 L35 44' stroke='{mix(col, '#102820', .4)}' stroke-width='2' stroke-linecap='round'/>")
    elif name == 'body':
        o += f"<path d='M28 18 Q14 18 4 22 Q14 26 26 28 Z' fill='{c}'/>"                        # しっぽ
        o += f"<ellipse cx='30' cy='23' rx='11' ry='7.5' fill='{c}'/>"
        o += f"<path d='M22 26 Q30 31 38 25' fill='none' stroke='{cl}' stroke-width='3' stroke-linecap='round' opacity='.8'/>"
        o += f"<path d='M36 19 Q40 12 42 6 L46 7 Q44 14 40 22 Z' fill='{c}'/>"                  # 首
        o += f"<ellipse cx='46' cy='6' rx='6' ry='4' fill='{c}'/><path d='M50 5 L57 6.4 L50 8.2 Z' fill='#E8C46A'/>"   # 頭と くちばし
        o += "<circle cx='47' cy='4.6' r='1.3' fill='#10201A'/><circle cx='46.6' cy='4.2' r='.45' fill='#FFFFFF'/>"
        for x in (24, 30, 36):
            o += f"<path d='M{x} 17.6 l2 -3 l2 3' fill='{cd}'/>"
        o += f"<path d='M37 22 l5 3 M38 24 l4 4' stroke='{cd}' stroke-width='1.6' stroke-linecap='round'/>"   # うで
    return doc(60, 46, o)


def ptero_svg():
    """翼竜（左向き）：体・頭の とさか。翼は 別の 部品（はばたく）"""
    return doc(40, 20, "<path d='M8 10 L2 8.6 L9 8 Q14 6 20 8 Q27 9 31 11 Q26 12 20 12 Q14 13 8 10 Z' fill='#B9744A'/>"
                       "<path d='M9 8 L14 3 L13 7.6 Z' fill='#D99A5E'/><circle cx='10' cy='9.2' r='.8' fill='#1E1410'/>")


def wing_svg():
    return doc(40, 20, "<path d='M14 10 Q18 0 34 2 Q26 6 24 11 Z' fill='#C98A5A'/><path d='M16 10 Q20 4 30 3' fill='none' stroke='#8E5A36' stroke-width='.8'/>")


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
LAYOUT = dict(near=(-4, 0), far=(40, 0))      # 馬の シートの ずらし（1倍の 画素：右・下）


def bang_svg():
    """びっくりの しるし（白い ふきだしに 赤い「！」の 形）"""
    o = ("<path d='M9 1 C14 1 17 4 17 9 C17 14 14 17 10 17 L6.6 21 L7.2 16.6 C3.6 15.8 1 13 1 9 C1 4 4 1 9 1 Z' fill='#FFFFFF' stroke='#5A3A1E' stroke-width='1.4' stroke-linejoin='round'/>"
         "<path d='M7.5 4 L10.5 4 L9.8 10.8 L8.2 10.8 Z' fill='#E0402A'/><circle cx='9' cy='13.4' r='1.6' fill='#E0402A'/>")
    return doc(18, 22, o)


def trex_roar():
    """ほえる 線（口の 前：絵の 座標 148〜182）"""
    o = ''
    for k, r in enumerate((8.0, 14.0, 20.0)):
        o += (f"<path d='M{f(150 + r * 0.25)} {f(34 - r * 0.9)} Q{f(152 + r)} 38 {f(150 + r * 0.25)} {f(42 + r * 0.9)}' fill='none' stroke='#FFFFFF' "
              f"stroke-width='{f(3.0 - k * 0.5)}' stroke-linecap='round' opacity='{f(0.95 - k * 0.22)}'/>")
    return doc(34, 76, o, vb='148 0 34 76')


def trex_html():
    """ティラノの 部品の ならび（反転する 箱の 中・絵の 座標＋10＝箱の 左から）"""
    def chain(cls, far):
        th, sh, ft = (trex_leg_seg(k, far) for k in ('thigh', 'shin', 'foot'))
        return (f'<i class="tl0 {cls}">' + img('tth', th[0]) + '<i class="tl1">' + img('tsh', sh[0]) + '<i class="tl2">' + img('tft', ft[0]) + '</i></i></i>')
    o = '<i class="dnTx"><i class="dnTb">'
    o += img('dnT tail', trex_part('tail'))
    o += chain('lf', True)
    o += img('dnT body', trex_part('body'))
    o += img('dnT arm', trex_part('arm'))
    o += '<i class="dnTh"><i class="dnTn">' + img('dnT jaw', trex_part('jaw')) + img('dnT head', trex_part('head')) + img('dnTr', trex_roar()) + '</i></i>'
    o += chain('ln', False)
    o += '</i></i>'
    return o


def trex_bob(q):
    """からだの 上下（絵の 座標・下が +）：どちらかの 足が 地面の まん中で いちばん 下"""
    return -1.6 * math.cos(4 * math.pi * q)


# ---- ティラノの 出る 時の ながれ（e＝出てから の 秒）
TX_X0, TX_X1 = 532.0, -6.0          # 反転した 箱の 右はし（画面の x）：右の 外 → 左の 外
TX_TOP = TREX_GROUND - 101.4 * TREX_SC
TX_ROAR = (0.22, 0.95)              # ほえる（頭を 上げて 口を あける）
DODGE = (0.0, 0.42, 1.78, 2.45)     # 馬が よける（よけ はじめ・よけ おわり・もどり はじめ・もどり おわり）
SHOCK = (0.12, 1.9)                 # 原始人が びっくり（武器を 上げる）


def banner(B):
    near, far = B.get('near'), B.get('far')
    near_s, far_s = B.get('near_s'), B.get('far_s')
    still = B.get('still')
    alt = ('むかしの大地で、けむりをはく火山と首の長い大きな恐竜・背中に板のある恐竜・草を食べるトリケラトプス・空の翼竜の横を、'
           '原始人が乗った鹿毛と芦毛の馬（長いたてがみとしっぽ）がならんで走るイラスト（馬はいつも走っていて、地面としげみと恐竜が流れ、'
           '首の長い恐竜は首をなめらかに上げ下げしてしだを食べる。火山は8秒に1回噴火して、ときどき大噴火。17秒に1回ティラノサウルスが'
           '右から走ってきてほえ、2頭の馬が上と下にわかれてよけたあいだを走りぬける）')
    html = f'<div class="dnw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('dnSky', sky_svg()) + img('dnGl', glow_svg())
    # 噴火（ふつう・大噴火）
    html += img('dnEg', eglow_svg()) + img('dnBg', eglow_svg(True)) + img('dnFl', flows_svg()) + img('dnBf', flows_svg())
    for k in range(6):                                                   # けむり（溶岩の うしろ）
        html += img(f'dnPf p{k}', puff_svg())
    for k in range(3):
        html += img(f'dnSb s{k}', puff_svg('#7E7078', '#A39498'))
    for k in range(4):
        html += img(f'dnBs s{k}', puff_svg('#6E6068', '#968890'))
    html += img('dnCo', column_svg()) + img('dnBc', column_svg(True))
    NB, NBB, NR = 7, 10, 5
    for k in range(NB):
        html += img(f'dnLb b{k}', lava_svg(4.2 + (k % 3) * 0.9))
    for k in range(NBB):
        html += img(f'dnLB b{k}', lava_svg(4.8 + (k % 3) * 1.0))
    for k in range(NR):
        html += img(f'dnRk r{k}', rock_svg())
    for k in range(2):
        html += f'<i class="dnPt q{k}">' + img('dnPb', ptero_svg()) + img('dnPw', wing_svg()) + '</i>'
    # 背景の 恐竜（しげみと 同じ はやさで 流れる）：首の 長い 恐竜（首は 8つの ふしの くさり・体の うしろから 出る）→ 背中に 板の ある 恐竜（2頭 交代）
    up, down = neck_poses()
    segs = [neck_seg(k) for k in range(NECK_N)]
    hd = bro_head()
    chain = ''
    for k in range(NECK_N):
        chain += f'<i class="n{k}">' + img(f'ns{k}', segs[k][0])
    chain += '<i class="hd">' + img('hh', hd[0]) + '</i>' + '</i>' * NECK_N
    html += ('<i class="dnBr">' + ''.join(img(f'dnB {k}', bro_part(k)) for k in ('shadow', 'legF', 'tail')) + chain
             + ''.join(img(f'dnB {k}', bro_part(k)) for k in ('body', 'legN', 'fern')) + '</i>')
    for k in range(2):
        html += f'<i class="dnSt t{k}">' + img('dnS tail', stego_svg('tail')) + img('dnS body', stego_svg('body')) + img('dnS head', stego_svg('head')) + '</i>'
    html += f'<i class="dnMd" style="background-image:url(&quot;{durl(mid_svg())}&quot;)"></i>'
    html += f'<i class="dnGd" style="background-image:url(&quot;{durl(ground_svg())}&quot;)"></i>'
    bang = img('dnEx', bang_svg())
    if far:
        html += '<i class="dnDg g2"><i class="dnH h2"><i></i></i>' + ('<i class="dnH h2s"><i></i></i>' if far_s else '') + bang + '</i>'
    html += '<i class="dnRx">' + ''.join(img(f'dnR {k}', runner_part(k)) for k in ('legF', 'body', 'legN')) + '</i>'
    html += trex_html()
    if near:
        html += '<i class="dnDg g1"><i class="dnH h1"><i></i></i>' + ('<i class="dnH h1s"><i></i></i>' if near_s else '') + bang + '</i>'
    html += '</div>'

    # ---- はやさ：地面は 手前の 馬の 地面に ついた ひづめと 同じ はやさ（すべらない）。おくの 馬は 1回りの 秒を かえて 同じ はやさに
    v = (near['spf'] / 2 * near['frames'] / RUN_S) if near and near.get('spf') else W / 2.5
    ground_s = W / v
    css = ('.dnw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#E9DDB2}'
           '.dnw>*{position:absolute;display:block}'
           '.dnw i,.dnw i>img{position:absolute;display:block}'
           '.dnw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.dnw .dnSky{left:0;top:0;width:390px;height:160px}'
           f'.dnw .dnGl{{left:{VX - 30}px;top:{VY - 22}px;width:60px;height:40px;animation:dnGlow 3.8s ease-in-out infinite;will-change:opacity}}'
           '.dnw .dnPf,.dnw .dnSb,.dnw .dnBs{left:0;top:0;width:40px;height:32px;opacity:0;will-change:transform,opacity}'
           '.dnw .dnPt{left:0;top:0;width:40px;height:20px;will-change:transform}'
           '.dnw .dnPt>img{position:absolute;left:0;top:0;width:40px;height:20px}'
           '.dnw .dnPw{transform-origin:15px 10px;animation:dnFlap .7s ease-in-out infinite alternate}'
           f'.dnw .dnMd{{left:0;top:66px;width:{2 * W + 2}px;height:60px;background-size:{W}px 60px;background-repeat:repeat-x;animation:dnMid {MID_S}s linear infinite}}'
           f'.dnw .dnGd{{left:0;top:{H - 44}px;width:{2 * W + 2}px;height:44px;background-size:{W}px 44px;background-repeat:repeat-x;animation:dnGround {f(ground_s, 4)}s linear infinite}}')
    # 噴火の 部品の 場所
    css += (f'.dnw .dnEg{{left:{VX - 45}px;top:{VY - 36}px;width:90px;height:60px;opacity:0;animation:dnEg {ERUPT_S}s linear infinite}}'
            f'.dnw .dnBg{{left:{VX - 65}px;top:{VY - 56}px;width:130px;height:90px;opacity:0;animation:dnBg {BIG_TOTAL}s linear infinite}}'
            f'.dnw .dnFl{{left:0;top:0;width:390px;height:160px;opacity:0;animation:dnFl {ERUPT_S}s linear infinite}}'
            f'.dnw .dnBf{{left:0;top:0;width:390px;height:160px;opacity:0;animation:dnBf {BIG_TOTAL}s linear infinite}}'
            f'.dnw .dnCo{{left:{VX - 14}px;top:{VY - 39}px;width:28px;height:42px;transform-origin:50% 100%;opacity:0;animation:dnCo {ERUPT_S}s linear infinite}}'
            f'.dnw .dnBc{{left:{VX - 20}px;top:{VY - 62}px;width:40px;height:66px;transform-origin:50% 100%;opacity:0;animation:dnBc {BIG_TOTAL}s linear infinite}}'
            '.dnw .dnLb,.dnw .dnLB,.dnw .dnRk{left:0;top:0;opacity:0;will-change:transform,opacity}'
            '.dnw .dnRk{width:14px;height:12px}')
    css += (cycle_kf('dnCo', [(0, 'opacity:0;transform:scaleY(0)'), (0.12, 'opacity:.95;transform:scaleY(.5)'), (0.5, 'opacity:1;transform:scaleY(1)'),
                              (1.2, 'opacity:.9;transform:scaleY(.85)'), (1.8, 'opacity:.6;transform:scaleY(.4)'), (2.3, 'opacity:0;transform:scaleY(0)')], ERUPT_S)
            + cycle_kf('dnEg', [(0, 'opacity:0'), (0.45, 'opacity:.85'), (2.4, 'opacity:.45'), (4.6, 'opacity:0')], ERUPT_S)
            + cycle_kf('dnFl', [(0, 'opacity:0'), (0.8, 'opacity:.75'), (3.5, 'opacity:.4'), (6.5, 'opacity:0')], ERUPT_S)
            + events_kf('dnBc', [(0, 'opacity:0;transform:scaleY(0)'), (0.15, 'opacity:.95;transform:scaleY(.6)'), (0.6, 'opacity:1;transform:scaleY(1)'),
                                 (1.6, 'opacity:.9;transform:scaleY(.9)'), (2.4, 'opacity:.6;transform:scaleY(.45)'), (3.0, 'opacity:0;transform:scaleY(0)')], BIG_TOTAL, BIG_AT)
            + events_kf('dnBg', [(0, 'opacity:0'), (0.5, 'opacity:.95'), (3.0, 'opacity:.5'), (6.0, 'opacity:0')], BIG_TOTAL, BIG_AT)
            + events_kf('dnBf', [(0, 'opacity:0'), (0.7, 'opacity:1'), (5.0, 'opacity:.6'), (9.0, 'opacity:0')], BIG_TOTAL, BIG_AT))
    R = rnd(41)
    for k in range(NB):                                                  # ふつうの 噴火の 溶岩の つぶ
        r = 4.2 + (k % 3) * 0.9
        sz = 2 * r + 2
        side = -1 if k % 2 else 1
        st = arc_stops(VX - sz / 2, VY - sz / 2 - 2, side * R.uniform(8, 30), R.uniform(16, 28), 0.06 + k * 0.07, R.uniform(1.0, 1.4), s0=1.0, s1=0.55)
        css += f'.dnw .dnLb.b{k}{{width:{f(sz)}px;height:{f(sz)}px;animation:dnLb{k} {ERUPT_S}s linear infinite}}' + cycle_kf(f'dnLb{k}', st, ERUPT_S)
    for k in range(NBB):                                                 # 大噴火の 溶岩の つぶ（高く 遠く）
        r = 4.8 + (k % 3) * 1.0
        sz = 2 * r + 2
        side = -1 if k % 2 else 1
        st = arc_stops(VX - sz / 2, VY - sz / 2 - 4, side * R.uniform(18, 60), R.uniform(30, 44), 0.05 + k * 0.08, R.uniform(1.5, 2.1), s0=1.1, s1=0.6)
        css += f'.dnw .dnLB.b{k}{{width:{f(sz)}px;height:{f(sz)}px;animation:dnLB{k} {BIG_TOTAL}s linear infinite}}' + events_kf(f'dnLB{k}', st, BIG_TOTAL, BIG_AT)
    for k in range(NR):                                                  # 大噴火の 岩
        side = -1 if k % 2 else 1
        st = arc_stops(VX - 7, VY - 8, side * R.uniform(56, 100), R.uniform(26, 40), 0.1 + k * 0.12, R.uniform(1.8, 2.4), g=2.6, s0=1.0, s1=0.9, spin=side * 540)
        css += f'.dnw .dnRk.r{k}{{animation:dnRk{k} {BIG_TOTAL}s linear infinite}}' + events_kf(f'dnRk{k}', st, BIG_TOTAL, BIG_AT)
    for k in range(3):                                                   # ふつうの 噴火の けむり
        dx = (-1, 1, 0)[k] * 10
        st = [(0.1 + k * 0.3 - 0.01, f'opacity:0;transform:translate({VX - 20}px,{VY - 22}px) scale(.5)'), (0.1 + k * 0.3, f'opacity:0;transform:translate({VX - 20}px,{VY - 22}px) scale(.5)'),
              (0.4 + k * 0.3, f'opacity:.9;transform:translate({VX - 20 + dx * 0.4}px,{VY - 32}px) scale(.9)'),
              (2.6 + k * 0.3, f'opacity:.6;transform:translate({VX - 20 + dx}px,{VY - 58}px) scale(1.7)'),
              (4.8 + k * 0.3, f'opacity:0;transform:translate({VX - 14 + dx * 1.6}px,{VY - 78}px) scale(2.3)')]
        css += f'.dnw .dnSb.s{k}{{animation:dnSb{k} {ERUPT_S}s linear infinite}}' + cycle_kf(f'dnSb{k}', st, ERUPT_S)
    for k in range(4):                                                   # 大噴火の けむり
        dx = (-1.4, 1.2, -0.4, 0.6)[k] * 14
        st = [(0.15 + k * 0.25 - 0.01, f'opacity:0;transform:translate({VX - 20}px,{VY - 24}px) scale(.6)'), (0.15 + k * 0.25, f'opacity:0;transform:translate({VX - 20}px,{VY - 24}px) scale(.6)'),
              (0.5 + k * 0.25, f'opacity:.85;transform:translate({VX - 20 + dx * 0.4}px,{VY - 38}px) scale(1.2)'),
              (3.6 + k * 0.25, f'opacity:.6;transform:translate({VX - 20 + dx}px,{VY - 66}px) scale(2.2)'),
              (7.0 + k * 0.25, f'opacity:0;transform:translate({VX - 12 + dx * 1.5}px,{VY - 88}px) scale(2.8)')]
        css += f'.dnw .dnBs.s{k}{{animation:dnBs{k} {BIG_TOTAL}s linear infinite}}' + events_kf(f'dnBs{k}', st, BIG_TOTAL, BIG_AT)
    # ---- 背景の 恐竜：しげみ（MID_S 秒で 390px）と 同じ はやさで 右から 左へ。足は 地面に 止まった まま
    #   首の 長い 恐竜：9秒で 画面を 通りぬけ、すぐ 次が 入る（9秒に 1回）。背中に 板の ある 恐竜：2頭が 12秒の 1回りを 6秒 ずらして（6秒に 1回）
    vmid = W / MID_S
    bw, bh = BRO
    sw_, sh_ = STEGO
    bro_d = -3.5                                                          # 首の 長い 恐竜の ずらし（0秒で 画面の まん中・しだを 食べて いる）
    bx0, bx1 = 400, -bw - 14
    css += (f'.dnw .dnBr{{left:0;top:-2px;width:{bw}px;height:{bh}px;animation:dnBro {BRO_S}s linear {bro_d}s infinite;will-change:transform}}'
            + kf('dnBro', [(0, f'transform:translateX({bx0}px)'), (100, f'transform:translateX({f((bx0 - vmid * BRO_S), 2)}px)')]))
    sx0, sx1 = 400, -sw_ - 14
    s_cyc = 2 * STEGO_S
    s_run = (sx0 - sx1) / vmid
    for k in range(2):
        enter = (bro_d + 0.9 + k * STEGO_S) % s_cyc                     # 首の 長い 恐竜より 0.9秒 あと（からだの 前に 少し 重なる）→ 6秒ごと
        css += f'.dnw .dnSt.t{k}{{left:0;top:{118 - 79}px;width:{sw_}px;height:{sh_}px;animation:dnSte {f(s_cyc)}s linear {f(enter - s_cyc, 3)}s infinite;will-change:transform}}'
    css += kf('dnSte', [(0, f'transform:translateX({sx0}px)'), (100 * s_run / s_cyc, f'transform:translateX({sx1}px)'), (100, f'transform:translateX({sx1}px)')])
    css += (f'.dnw .dnBr>img{{position:absolute;left:0;top:0;width:{bw}px;height:{bh}px}}'
            f'.dnw .dnB.tail{{transform-origin:150px 64px;animation:dnTail 4.2s ease-in-out infinite}}'
            f'.dnw .dnBr i{{width:0;height:0;transform-origin:0 0;animation-duration:{BRO_S}s;animation-timing-function:ease-in-out;animation-iteration-count:infinite;animation-delay:{bro_d}s}}'
            f'.dnw .dnBr .n0{{left:{BRO_NECK[0]}px;top:{BRO_NECK[1]}px;animation-name:dnN0}}')
    for k in range(1, NECK_N):
        css += f'.dnw .dnBr .n{k}{{left:{f(-NECK_SEG)}px;top:0;animation-name:dnN{k}}}'
    css += f'.dnw .dnBr .hd{{left:{f(-NECK_SEG)}px;top:0;animation-name:dnNh}}'
    for k, (svg, ox_, oy_, w_, h_) in enumerate(segs):
        css += f'.dnw .dnBr .ns{k}{{left:{f(-ox_)}px;top:{f(-oy_)}px;width:{f(w_)}px;height:{f(h_)}px}}'
    css += f'.dnw .dnBr .hh{{left:{f(-hd[1])}px;top:{f(-hd[2])}px;width:{f(hd[3])}px;height:{f(hd[4])}px}}'
    # 首の 動き（9秒）：上げて まわりを 見る → 首を ぜんぶ なめらかに まげて 下げる → しだを もぐもぐ → なめらかに 上げる → まわりを 見る
    seq = [(0.0, neck_rel(up)), (0.9, neck_rel(up, 9)), (1.6, neck_rel(up, 3)), (3.0, neck_rel(down)), (3.45, neck_rel(down, 0, 8)), (3.85, neck_rel(down)),
           (4.25, neck_rel(down, 0, 8)), (4.65, neck_rel(down)), (5.05, neck_rel(down, 0, 8)), (5.5, neck_rel(down)), (6.9, neck_rel(up)), (7.8, neck_rel(up, -7)),
           (8.6, neck_rel(up)), (BRO_S, neck_rel(up))]
    for j in range(NECK_N + 1):
        nm = f'dnN{j}' if j < NECK_N else 'dnNh'
        css += kf(nm, [(100 * t / BRO_S, f'transform:rotate({f(v_[j], 2)}deg)') for t, v_ in seq])
    css += (f'.dnw .dnSt>img{{position:absolute;left:0;top:0;width:{sw_}px;height:{sh_}px}}'
            '.dnw .dnS.tail{transform-origin:120px 56px;animation:dnTail 3.6s ease-in-out infinite}'
            '.dnw .dnS.head{transform-origin:36px 54px;animation:dnSHead 2.8s ease-in-out infinite}'
            '.dnw .dnSt.t1 .dnS.head{animation-delay:-1.3s}'
            + kf('dnSHead', [(0, 'transform:rotate(0deg)'), (50, 'transform:rotate(-6deg)'), (100, 'transform:rotate(0deg)')]))
    # ---- ティラノ（17秒に 1回）と 馬の よけかた
    def ev(name, pts):
        return cycle_kf(name, [(TREX_AT + e, d) for e, d in pts], TREX_S)
    # 馬（2頭）：シートの 地面に ついた ひづめが 地面と 同じ はやさで うしろへ（おくの 馬は 1回りの 秒を かえる）。びっくりの シートと 入れかえ
    for k, (cls, meta, delay, key) in enumerate((('h1', near, 0.0, 'near'), ('h2', far, 0.17, 'far'), ('h1s', near_s, 0.0, 'near'), ('h2s', far_s, 0.17, 'far'))):
        if not meta:
            continue
        n, (cw, ch), (ax, ay) = meta['frames'], meta['cell'], meta['at']
        w, h = cw / 2, ch / 2
        dx, dy = LAYOUT[key]
        run = (meta['spf'] / 2 * n / v) if meta.get('spf') else RUN_S
        css += (f'.dnw .dnH.{cls}{{left:{f(ax / 2 + dx)}px;top:{f(ay / 2 + dy)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'
                f'.dnw .dnH.{cls}>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({meta["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;'
                f'animation:dnRun{k + 1} {f(run, 4)}s steps({n}) {f(-delay, 3)}s infinite}}'
                + kf(f'dnRun{k + 1}', [(100, f'transform:translateX({f(-n * w)}px)')]))
    s0, s1 = SHOCK
    if near_s or far_s:
        css += ('.dnw .dnH.h1,.dnw .dnH.h2{animation:dnCalm 17s linear infinite}.dnw .dnH.h1s,.dnw .dnH.h2s{opacity:0;animation:dnShock 17s linear infinite}'
                + ev('dnCalm', [(0, 'opacity:1'), (s0, 'opacity:1'), (s0 + 0.02, 'opacity:0'), (s1, 'opacity:0'), (s1 + 0.02, 'opacity:1')])
                + ev('dnShock', [(0, 'opacity:0'), (s0, 'opacity:0'), (s0 + 0.02, 'opacity:1'), (s1, 'opacity:1'), (s1 + 0.02, 'opacity:0')]))
    d0, d1, d2, d3 = DODGE
    # 第4.113版：おくの 白い 馬（g2）は 上へ よけない（上へ 9px 動くと ひづめが 地面から うく：まさちゃん「白い馬の脚が宙に浮いてるから地面につけて」）→ うしろへ 6px だけ
    for cls, (ddx, ddy), (ex, ey) in (('g1', (2, 10), (150, 22)), ('g2', (-6, 0), (224, 12))):
        css += (f'.dnw .dnDg.{cls}{{left:0;top:0;width:0;height:0;animation:dnDg{cls} {TREX_S}s ease-in-out infinite}}'
                + ev(f'dnDg{cls}', [(0, 'transform:translate(0,0)'), (d0, 'transform:translate(0,0)'), (d1, f'transform:translate({ddx}px,{ddy}px)'),
                                    (d2, f'transform:translate({ddx}px,{ddy}px)'), (d3, 'transform:translate(0,0)')])
                + f'.dnw .dnDg.{cls} .dnEx{{left:{ex}px;top:{ey}px;width:18px;height:22px;transform-origin:6px 22px;opacity:0;animation:dnEx {TREX_S}s linear infinite}}')
    css += ev('dnEx', [(0, 'opacity:0;transform:scale(0)'), (s0, 'opacity:0;transform:scale(0)'), (s0 + 0.1, 'opacity:1;transform:scale(1.25)'),
                       (s0 + 0.2, 'opacity:1;transform:scale(1)'), (1.45, 'opacity:1;transform:scale(1)'), (1.7, 'opacity:0;transform:scale(.8)')])
    css += '.dnw .dnDg.g2 .dnEx{animation-delay:-.06s}'
    # ティラノの 体（反転した 箱：右から 左へ 走る）
    D = (TX_X0 - TX_X1) / TREX_V
    r0, r1 = TX_ROAR
    css += (f'.dnw .dnTx{{left:0;top:0;width:0;height:0;transform-origin:0 0;animation:dnTx {TREX_S}s linear infinite}}'
            + kf('dnTx', [(0, f'transform:translate({f(TX_X0)}px,{f(TX_TOP)}px) scale(-{TREX_SC},{TREX_SC})'),                     # 右の 外で まつ
                          (100 * TREX_AT / TREX_S, f'transform:translate({f(TX_X0)}px,{f(TX_TOP)}px) scale(-{TREX_SC},{TREX_SC})'),
                          (100 * (TREX_AT + D) / TREX_S, f'transform:translate({f(TX_X1)}px,{f(TX_TOP)}px) scale(-{TREX_SC},{TREX_SC})'),   # 左の 外へ ぬけて
                          (100, f'transform:translate({f(TX_X1)}px,{f(TX_TOP)}px) scale(-{TREX_SC},{TREX_SC})')])                            # 左の 外で まつ（次の 回は 右の 外から）
            + f'.dnw .dnTb,.dnw .dnTh,.dnw .dnTn{{left:0;top:0;width:0;height:0}}'
            + f'.dnw .dnTx .dnT{{left:0;top:0;width:164px;height:104px}}'
            + f'.dnw .dnTb{{animation:dnTBob {f(TREX_RUN / 2, 3)}s linear infinite}}'
            + kf('dnTBob', [(100 * i / 8, f'transform:translateY({f(trex_bob(i / 16), 2)}px)') for i in range(9)])
            + f'.dnw .dnT.tail{{transform-origin:54px 44px;animation:dnTTail {f(TREX_RUN, 3)}s ease-in-out infinite}}'
            + kf('dnTTail', [(0, 'transform:rotate(-3deg)'), (50, 'transform:rotate(3deg)'), (100, 'transform:rotate(-3deg)')])
            + f'.dnw .dnT.arm{{transform-origin:98px 57px;animation:dnTArm {f(TREX_RUN, 3)}s ease-in-out infinite}}'
            + kf('dnTArm', [(0, 'transform:rotate(-12deg)'), (50, 'transform:rotate(10deg)'), (100, 'transform:rotate(-12deg)')])
            + f'.dnw .dnTh{{transform-origin:108px 30px;animation:dnTHead {TREX_S}s ease-in-out infinite}}'
            + ev('dnTHead', [(0, 'transform:rotate(0deg)'), (r0 - 0.04, 'transform:rotate(0deg)'), (r0 + 0.12, 'transform:rotate(-15deg)'), (r1 - 0.2, 'transform:rotate(-13deg)'),
                             (r1, 'transform:rotate(0deg)')])
            + f'.dnw .dnTn{{transform-origin:108px 30px;animation:dnTNod {f(TREX_RUN / 2, 3)}s ease-in-out infinite alternate}}'
            + kf('dnTNod', [(0, 'transform:rotate(1.5deg)'), (100, 'transform:rotate(-1.5deg)')])
            + f'.dnw .dnT.jaw{{transform-origin:112px 38px;animation:dnTJaw {TREX_S}s ease-in-out infinite}}'
            + ev('dnTJaw', [(0, 'transform:rotate(0deg)'), (r0, 'transform:rotate(0deg)'), (r0 + 0.14, 'transform:rotate(22deg)'), (r0 + 0.32, 'transform:rotate(18deg)'),
                            (r0 + 0.48, 'transform:rotate(22deg)'), (r1 - 0.12, 'transform:rotate(20deg)'), (r1, 'transform:rotate(0deg)')])
            + f'.dnw .dnTr{{left:158px;top:0;width:34px;height:76px;transform-origin:2px 38px;opacity:0;animation:dnTRoar {TREX_S}s ease-in-out infinite}}'
            + ev('dnTRoar', [(0, 'opacity:0;transform:scale(.6)'), (r0 + 0.08, 'opacity:0;transform:scale(.6)'), (r0 + 0.2, 'opacity:1;transform:scale(1)'),
                             (r0 + 0.34, 'opacity:.8;transform:scale(1.18)'), (r0 + 0.48, 'opacity:1;transform:scale(.95)'), (r0 + 0.62, 'opacity:.8;transform:scale(1.16)'),
                             (r1 - 0.06, 'opacity:0;transform:scale(1.3)')]))
    # 足（くさり：もも → すね → 足）。地面に ついた 足は 地面と 同じ はやさで うしろへ（すべらない）
    keys = trex_leg_keys(0.0)
    th, sh, ft = (trex_leg_seg(k) for k in ('thigh', 'shin', 'foot'))
    css += (f'.dnw .dnTx .tl0{{left:{TR_HIP[0] - TR_BOX[0]}px;top:{TR_HIP[1]}px}}.dnw .dnTx .tl1{{left:0;top:{f(TR_LT)}px}}.dnw .dnTx .tl2{{left:0;top:{f(TR_LS)}px}}'
            f'.dnw .dnTx .tl0,.dnw .dnTx .tl1,.dnw .dnTx .tl2{{width:0;height:0;transform-origin:0 0;animation-duration:{f(TREX_RUN, 3)}s;animation-timing-function:linear;animation-iteration-count:infinite}}'
            '.dnw .dnTx .tl0{animation-name:dnTL0}.dnw .dnTx .tl1{animation-name:dnTL1}.dnw .dnTx .tl2{animation-name:dnTL2}'
            f'.dnw .dnTx .lf,.dnw .dnTx .lf i{{animation-delay:{f(-TREX_RUN / 2, 3)}s}}'
            f'.dnw .dnTx .tth{{left:{-th[1]}px;top:{-th[2]}px;width:{th[3]}px;height:{th[4]}px}}'
            f'.dnw .dnTx .tsh{{left:{-sh[1]}px;top:{-sh[2]}px;width:{sh[3]}px;height:{sh[4]}px}}'
            f'.dnw .dnTx .tft{{left:{-ft[1]}px;top:{-ft[2]}px;width:{ft[3]}px;height:{ft[4]}px}}')
    nt = len(keys[0]) - 1
    for j in range(3):
        css += kf(f'dnTL{j}', [(100 * i / nt, f'transform:rotate({f(keys[j][i], 1)}deg)') for i in range(nt + 1)])
    # 小さな 恐竜：17秒に 1回（ティラノの 出ない ころ：8.5〜13.3秒）うしろから 走って きて、馬を 追いこして 右へ（足は 0.32秒で 1歩）
    css += (f'.dnw .dnRx{{left:0;top:100px;width:60px;height:46px;animation:dnRace {TREX_S}s linear infinite;will-change:transform}}'
            '.dnw .dnRx>img{position:absolute;left:0;top:0;width:60px;height:46px}'
            '.dnw .dnR.body{animation:dnRBob .16s ease-in-out infinite alternate}'
            '.dnw .dnR.legN{transform-origin:29px 25px;animation:dnRLeg .32s linear infinite}'
            '.dnw .dnR.legF{transform-origin:29px 25px;animation:dnRLeg .32s linear -.16s infinite}'
            + kf('dnRace', [(0, 'transform:translate(-70px,0)'), (100 * 8.5 / TREX_S, 'transform:translate(-70px,0)'), (100 * 13.3 / TREX_S, 'transform:translate(420px,-3px)'),
                            (100, 'transform:translate(420px,-3px)')])
            + kf('dnRBob', [(0, 'transform:translateY(0)'), (100, 'transform:translateY(-1.6px)')])
            + kf('dnRLeg', [(0, 'transform:rotate(-34deg)'), (50, 'transform:rotate(30deg)'), (100, 'transform:rotate(-34deg)')]))
    # けむり：火山の 口から 右上へ もくもく（6秒・1秒ずつ ずらす）
    for k in range(6):
        css += f'.dnw .dnPf.p{k}{{animation:dnPuff 6s ease-out {f(-k, 2)}s infinite}}'
    css += kf('dnPuff', [(0, f'opacity:0;transform:translate({VX - 20}px,{VY - 16}px) scale(.35)'), (10, f'opacity:.85;transform:translate({VX - 18}px,{VY - 26}px) scale(.55)'),
                         (60, f'opacity:.6;transform:translate({VX + 4}px,{VY - 52}px) scale(1.1)'), (100, f'opacity:0;transform:translate({VX + 30}px,{VY - 74}px) scale(1.6)')])
    # 翼竜：右から 左へ（14秒・18秒）
    for k, (sec, d, y0, y1, s_) in enumerate(((14.0, 0.0, 26, 14, 1.0), (18.0, -7.0, 44, 34, 0.75))):
        css += f'.dnw .dnPt.q{k}{{animation:dnFly{k} {sec}s linear {d}s infinite}}'
        css += kf(f'dnFly{k}', [(0, f'transform:translate(410px,{y0}px) scale({s_})'), (50, f'transform:translate(190px,{f((y0 + y1) / 2 - 6)}px) scale({s_})'),
                                (100, f'transform:translate(-60px,{y1}px) scale({s_})')])
    css += (kf('dnGlow', [(0, 'opacity:.55;transform:scale(.92)'), (50, 'opacity:.95;transform:scale(1.06)'), (100, 'opacity:.55;transform:scale(.92)')])
            + kf('dnFlap', [(0, 'transform:scaleY(1)'), (100, 'transform:scaleY(-.55)')])
            + kf('dnMid', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('dnGround', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('dnTail', [(0, 'transform:rotate(-4deg)'), (50, 'transform:rotate(4deg)'), (100, 'transform:rotate(-4deg)')]))
    css += reduced('.dnw>*:not(.bnr)') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_dino():
    """背景の もよう：恐竜の 足あと（3本ゆび）と 小さな シダの 葉（うすく）"""
    o = ''
    for x, y, a in ((30, 34, -20), (54, 50, -20), (100, 96, 30), (122, 116, 30)):
        r = math.radians(a)
        o += f"<g transform='translate({x} {y}) rotate({a})' opacity='.18'><path d='M0 0 l-6 -4 M0 0 l-7 .4 M0 0 l-5.6 4.4' stroke='#6E5A2E' stroke-width='2.4' stroke-linecap='round'/><ellipse cx='2' cy='0' rx='3' ry='2.4' fill='#6E5A2E'/></g>"
    for x, y, a in ((96, 30, -30), (24, 110, 20)):
        o += f"<g transform='translate({x} {y}) rotate({a})' opacity='.22'><path d='M0 0 V-18' stroke='#4E7A3A' stroke-width='1.4'/>"
        for k in range(1, 5):
            o += f"<path d='M0 {-k * 4} q-5 -1 -6 -5 M0 {-k * 4} q5 -1 6 -5' fill='none' stroke='#4E7A3A' stroke-width='1.6' stroke-linecap='round'/>"
        o += "</g>"
    return tile(150, 150, o)


def leaf_strip():
    """上の 帯の 下の ふち：たれさがる シダの 葉の ぎざぎざ"""
    o = ("<path d='M0 0 H30 V2 Q27 2 26 5 Q25 9 22 9 Q21 6 19 4 Q17 8 15 11 Q13 8 11 4 Q9 7 8 9 Q5 9 4 5 Q3 2 0 2 Z' fill='#2C4220'/>"
         "<path d='M15 2 V9' stroke='#4E7A3A' stroke-width='.8'/>")
    return tile(30, 11, o)


def orn():
    """すみの 飾り（44×44）：ひびの 入った 恐竜の たまご（てんてん）と シダの 葉"""
    o = ("<path d='M8 40 Q2 30 9 22' fill='none' stroke='#4E7A3A' stroke-width='2' stroke-linecap='round'/>"
         "<path d='M7 34 q-4 -1 -5 -4 M8 30 q-4 -2 -4 -5 M8 26 q-3 -2 -2 -5 M8 34 q3 -2 6 -1 M8 30 q3 -3 6 -2' fill='none' stroke='#6E9A48' stroke-width='1.8' stroke-linecap='round'/>"
         "<ellipse cx='26' cy='26' rx='12' ry='15' fill='#F4EAD2' stroke='#B8A47A' stroke-width='1.4'/>"
         "<circle cx='21' cy='20' r='2.2' fill='#8FB060'/><circle cx='30' cy='29' r='2.8' fill='#8FB060'/><circle cx='24' cy='34' r='1.8' fill='#8FB060'/><circle cx='31' cy='17' r='1.6' fill='#8FB060'/>"
         "<path d='M15 22 L19 25 L22 21 L26 25 L29 21 L33 24 L37 21' fill='none' stroke='#7A6A4A' stroke-width='1.4' stroke-linejoin='round'/>"
         "<path d='M20 14 Q24 11 29 13' fill='none' stroke='#FFFFFF' stroke-width='1.8' stroke-linecap='round' opacity='.85'/>")
    return o


THEME = dict(
    id=ID, cat=7, name='恐竜時代', desc='火山と恐竜', title='恐竜時代（シダの緑×溶岩×土）', banner=ID,
    alt='むかしの大地で、噴火する火山と首の長い恐竜・背中に板のある恐竜・草を食べるトリケラトプス・空の翼竜の横を、原始人が乗った鹿毛と芦毛の馬（長いたてがみとしっぽ）がならんで走り、ときどきティラノサウルスが走ってきて馬がよけるイラスト',
    fonts=['Yuji+Boku', 'M+PLUS+1p:wght@500;700'],
    v=dict(bg='#EEF0DC', ink='#26281A', sub='#5C5E40', card='#FFFDF2', cardB='1.5px solid #CFD2A6', cardO='0 solid transparent', cardS='0 3px 0 #DADDB4',
           radius='14px', rs='10px', font='"M PLUS 1p"', dfont='"Yuji Boku"', dw='400', logo='#FFC15A', logoS='0 2px 0 #1A2410',
           iii='#FFC15A', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#41602C,#2C4220)', hdInk='#F4F1DC', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.1)', mLine='rgba(255,193,90,.6)', mInk='#F4F1DC', pill='rgba(0,0,0,.2)', pillLine='rgba(255,226,168,.4)', pillInk='#F4F1DC',
           coin='#FFC15A', coinInk='#2C2410', badge='#FFF4D8', badgeInk='#9A3E14', badgeB='1.5px solid #E6C27A', tagBg='#F4F6E2', tagInk='#46502A',
           tagLine='#CFD2A6', warnBg='#FBE2D2', warnInk='#9A3416', zBg='#FFFEF6', zB='1.5px solid #E2E4C2', znBg='#4E6B2E', znInk='#FFFFFF',
           znB='0 solid transparent', znR='6px', znS='none', acc='#B44A18', nR='8px', w2B='0 solid transparent', sep='1.5px dashed #CFD2A6',
           btn='#C75126', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='12px', btnS='0 3px 0 #8E3414', btn2='#FFFDF2', btn2Ink='#8E3A14',
           btn2B='1.5px solid #D9B488', tab='#2C4220', tabB='1px solid #1E3016', tabInk='#C9D2A8', tabOn='rgba(255,193,90,.16)', tabOnInk='#FFC15A',
           tabR='12px', sel='#D8582A', selInk='#FFFFFF', h1='#9A3E14'),
    chk=dict(hd=['#41602C', '#2C4220']),
    css=[('', 'background-image:' + curi(tile_dino()) + ';background-size:150px 150px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-10px;height:11px;background:' + curi(leaf_strip()) + ' 0 0/30px 11px repeat-x'),
         ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(255,193,90,.12),transparent 40%)')],
    orn=orn(),
    guide=dict(colors=[('#2C4220', 'シダの 緑'), ('#D8582A', '溶岩'), ('#FFC15A', '火の あかり'), ('#EEF0DC', '背景'), ('#26281A', '文字')],
               fonts='見出し：Yuji Boku<br>本文：M PLUS 1p', shape='角丸14px・帯は シダの 緑で 下に たれる 葉・足あとの 背景・すみに 恐竜の たまご・的中ボタンは 溶岩の 石の PUSH',
               pic='8秒に 1回 噴火する 火山（ときどき 大噴火）・首を なめらかに 上げ下げして しだを 食べる 首の 長い 恐竜（9秒に 1回 通る）と 背中に 板の ある 恐竜（6秒に 1回 通る）・'
                   'トリケラトプス・翼竜・17秒に 1回 ほえながら 走って くる ティラノサウルス（2頭の 馬が 上と 下に よけて 原始人は びっくり）・原始人が 乗って ならんで 走る 鹿毛と 芦毛の 馬'),
)


# ================================================================== 的中ボタン：溶岩の 石の PUSH（dn）
def push_face(sfx=''):
    """ボタン（200×100）が 黒い 溶岩の 石：ごつごつの ふち・ひびから 溶岩の あかり（.dnlv：ゆっくり ゆらぐ）・左右に シダの 葉・上に 恐竜の たまご 2つ"""
    g = f'dnG{sfx}'
    defs = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A4A50"/><stop offset=".6" stop-color="#3A2E36"/>'
            '<stop offset="1" stop-color="#241C22"/></linearGradient></defs>')
    o = ''
    for x, a in ((-6, -30), (206, 210)):                                 # シダの 葉（うしろ）
        r = math.radians(a)
        o += f'<g transform="translate({x} 80) rotate({a})"><path d="M0 0 H62" stroke="#3E6630" stroke-width="3" stroke-linecap="round"/>'
        for k in range(1, 8):
            o += f'<path d="M{k * 8} 0 q-3 -10 -10 -13 M{k * 8} 0 q-3 10 -10 13" fill="none" stroke="{GREEN["m"] if k % 2 else GREEN["l"]}" stroke-width="4" stroke-linecap="round"/>'
        o += '</g>'
    edge = []
    R = rnd(13)
    for k in range(28):
        a = 2 * math.pi * k / 28
        rr = 1 + R.uniform(-0.04, 0.05)
        x = 100 + math.cos(a) * 104 * rr
        y = 50 + math.sin(a) * 56 * rr
        edge.append((max(-6, min(206, x)), max(-6, min(106, y))))
    o += f'<path d="{smooth(edge)}" fill="url(#{g})" stroke="#1A1418" stroke-width="2.4"/>'
    o += f'<path d="{smooth([(x, y - 4) for x, y in edge[16:26]], close=False)}" fill="none" stroke="#7A6A72" stroke-width="2.4" opacity=".6"/>'
    cracks = [((30, 74), (44, 64), (52, 72), (66, 66)), ((140, 80), (152, 70), (166, 76), (176, 66)), ((20, 30), (32, 38), (40, 30)), ((160, 24), (172, 32), (184, 26))]
    o += '<g class="dnlv">'
    for cr in cracks:
        o += f'<path d="{P(cr, False)}" fill="none" stroke="#FF7A2E" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
        o += f'<path d="{P(cr, False)}" fill="none" stroke="#FFD27A" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
    o += '</g>'
    for x, y, rx in ((70, -6, 13), (120, -10, 15)):                     # 恐竜の たまご
        o += (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * 1.25:.1f}" fill="#F4EAD2" stroke="#B8A47A" stroke-width="1.6"/>'
              f'<circle cx="{x - 4}" cy="{y - 6}" r="2.6" fill="#8FB060"/><circle cx="{x + 5}" cy="{y + 3}" r="3.2" fill="#8FB060"/><circle cx="{x - 2}" cy="{y + 8}" r="2" fill="#8FB060"/>'
              f'<path d="M{x - rx * 0.5:.1f} {y - rx * 0.8:.1f} q{rx * 0.4:.1f} -3 {rx * 0.8:.1f} -1" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".85"/>')
    return f'<i class="dnf" aria-hidden="true"><svg viewBox="-30 -36 260 150" width="260" height="150">{defs}{o}</svg></i>'


def push_decor(sfx=''):
    """まわりに 火の 粉（小さく ゆっくり 上がる .dnem）と 小さな 翼竜（.dnpt）"""
    o = ''
    for j, (x, y) in enumerate(((10, 90), (40, 100), (160, 98), (190, 88), (100, 104), (70, 96))):
        o += f'<circle class="dnem" cx="{x}" cy="{y}" r="2.4" fill="#FFB547" style="animation-delay:{-0.45 * j:.2f}s"/>'
    o += ('<g transform="translate(206 -30)"><g class="dnpt"><path d="M-14 0 L-20 -1.4 L-13 -2 Q-8 -4 -2 -2 Q5 -1 9 1 Q4 2 -2 2 Q-8 3 -14 0 Z" fill="#B9744A"/>'
          '<path d="M-6 0 Q-2 -12 12 -10 Q4 -6 2 0 Z" fill="#C98A5A"/></g></g>')
    return f'<i class="dnd" aria-hidden="true"><svg viewBox="-40 -70 280 190" width="280" height="190">{o}</svg></i>'


def _rock():
    return doc(22, 20, "<path d='M3 14 L6 5 L13 2 L20 8 L19 16 L10 19 Z' fill='#4A3C44' stroke='#241C22' stroke-width='1.2'/><path d='M7 9 L12 12 L16 9' fill='none' stroke='#FF8A3A' stroke-width='1.4' stroke-linecap='round'/>")


def _leaf():
    o = "<path d='M2 20 L22 2' stroke='#3E6630' stroke-width='1.6'/>"
    for k in range(1, 6):
        x, y = 2 + k * 3.6, 20 - k * 3.4
        o += f"<path d='M{f(x)} {f(y)} q-1 -5 -5 -6 M{f(x)} {f(y)} q4 1 6 -3' fill='none' stroke='#6E9A48' stroke-width='2' stroke-linecap='round'/>"
    return doc(24, 24, o)


def _shell():
    return doc(22, 18, "<path d='M2 10 Q4 2 12 2 Q20 3 20 10 L16 8 L13 12 L9 8 L5 12 Z' fill='#F4EAD2' stroke='#B8A47A' stroke-width='1.2'/><circle cx='9' cy='5.6' r='1.6' fill='#8FB060'/>")


def _print():
    return doc(20, 20, "<g transform='translate(12 10)'><path d='M0 0 l-7 -5 M0 0 l-8 .5 M0 0 l-6.6 5.4' stroke='#7A5626' stroke-width='2.6' stroke-linecap='round'/><ellipse cx='2.4' cy='0' rx='3.4' ry='2.8' fill='#7A5626'/></g>")


PIECES = dict(rk=piece(_rock()), lf=piece(_leaf()), sh=piece(_shell()), fp=piece(_print()),
              em='border-radius:50%;background:radial-gradient(circle,#FFE2A0,#FF8A3A 60%,rgba(255,138,58,0))')


def push_burst():
    return fly_burst('dn', ['rk', 'lf', 'sh', 'em', 'fp', 'lf', 'rk', 'em'], 28, 61, sizes=dict(rk=(14, 19), lf=(16, 22), sh=(13, 17), em=(7, 10), fp=(14, 18)))


PUSH_CSS = r'''
/* ---------- 恐竜時代の的中ボタン：溶岩の 石の PUSH（壁紙パック） ----------
   ボタンが まるごと 黒い 溶岩の 石（ごつごつの ふち）：ひびから 溶岩の あかりが ゆっくり ゆらぐ・左右に シダの 葉・上に 恐竜の たまご 2つ。「PUSH」は 火の 色。
   まわりに 火の 粉が ゆっくり 上がる（小さな 点だけ）・小さな 翼竜。上下の 動きは 的中と 同じ。押すと 石が ちぢんで ふくらみ（強く 光らせない）、
   岩・シダの 葉・たまごの から・火の 粉・足あとが はじけて 落ち、だいだいの 光の 輪が 広がる */
.dn{--pushA:#3A2E36;--pushB:#1A1418;--pushC:#5A4A50;--rim:#FF8A3A;--rimD:#241C22}
.push.dn{--pr:40px;background:none;border-radius:40px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(30,20,10,.5)) drop-shadow(0 18px 24px rgba(0,0,0,.4))}
.push.dn span{top:2px;font:400 42px/1 "Yuji Boku",serif;letter-spacing:.06em;color:#FFC15A;text-shadow:0 3px 0 #7A2A0E,0 0 12px rgba(255,138,58,.65)}
.push.dn::after{inset:-24px;top:-46px;border-radius:60px;border-color:rgba(255,160,80,.9)}
.dn .dnf{position:absolute;left:-30px;top:-36px;width:260px;height:150px;pointer-events:none;font-style:normal}
.dn .dnf svg{display:block;width:260px;height:150px;overflow:visible}
.dn .dnd{position:absolute;left:-40px;top:-70px;width:280px;height:190px;pointer-events:none;z-index:3;font-style:normal}
.dn .dnd svg{display:block;width:280px;height:190px;overflow:visible}
.dn .dnlv{animation:dnLv 3.2s ease-in-out infinite}
@keyframes dnLv{0%,100%{opacity:.6}50%{opacity:1}}
.dn .dnem{animation:dnEm 2.7s ease-out infinite}
@keyframes dnEm{0%{opacity:0;transform:translateY(0)}20%{opacity:.95}100%{opacity:0;transform:translateY(-46px)}}
.dn .dnpt{animation:dnPtB 2.4s ease-in-out infinite alternate}
@keyframes dnPtB{from{transform:translate(0,-4px) rotate(-6deg)}to{transform:translate(-6px,4px) rotate(6deg)}}
.pshadow.dn{width:230px}
.tap.dn{font-family:"Yuji Boku",serif;font-weight:400;color:#FFC15A;letter-spacing:.12em;text-shadow:0 2px 0 #2C4220,0 0 10px rgba(255,138,58,.6)}
.pressed.dn{border-radius:40px;background:#3A2E36;box-shadow:0 0 0 4px #FF8A3A,0 7px 0 4px #241C22;animation-name:dnPress,fxH}
@keyframes dnPress{0%{transform:scale(1)}22%{transform:scale(.9,.84)}45%{transform:scale(1.07)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.dn .dnlv,.dn .dnem,.dn .dnpt{animation:none}.dn .dnem,.clips.dn{display:none}}
''' + fly_css('dn', 'rgba(255,160,80,.9)', PIECES)

PUSH = dict(code='dn', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
