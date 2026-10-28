"""壁紙パック ②宇宙（まさちゃんの 指定「月面を走る馬。うしろに地球、ときどき流れ星」）
   上の絵：月の 上を、ガラスの ヘルメットを かぶった 芦毛の 馬（pack/make/space_art.py）が 走る。うしろの 空に 青い 地球（右上）と 星。
     遠くの 月の 山と クレーター・手前の 月の 地面（くぼみ・石）。遠くの 山に 小さな 旗（金の 蹄鉄）。
   動き：馬は いつも 走って いる（月なので ゆっくり）・地面と 遠くの 山が 流れる（遠いほど ゆっくり）・
     ひづめの うしろに 月の 砂ぼこりが ふわっと 立つ・地球が ゆっくり 回る（雲は 少し 速く）・星が ゆっくり またたく・
     ときどき 流れ星（19秒に 3回・細い 光の すじ・強く 光らせない）
   第4.93版（まさちゃん「8秒に一回UFOが馬を見に来る演出入れて！ あと、足がしっかり地面についてるかも確認！ 5秒に一回宙に浮いてしまう演出入れて！」）：
     ・地面：ギャロップの 地面に ついた ひづめが 地面の 線（132px）に そろう（コマの シートの 浮きを 小さく）・影は その 線の 上（前は 8px 下に あって 浮いて 見えた）
     ・5秒に 1回 ふわっと 宙に 浮く（月の 重力：1秒で 22px 上がって 少し ただよい、1秒で おりる。鼻先が 少し 上を 向く・影は 小さく うすく・
       浮いて いる 間は 砂ぼこりが 出ない・おりた ときに 砂ぼこりが ふわっ）
     ・8秒に 1回 UFO（銀の 円盤と ガラスの 屋根・中に 小さな 緑の 宇宙人）が 右上から 飛んで きて 馬の 背中の 上で とまり、宇宙人が 乗りだして のぞく・
       やわらかい 光の すじ（ゆっくり 出て ゆっくり 消える・点めつ しない）→ 左上へ 飛んで いく"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'space'
RUN_S = 0.62       # ギャロップ 1回の 秒（月なので ゆっくり）
GROUND_S = 3.1     # 手前の 地面が 1まい（390px）流れる 秒（ひづめの 動きに 合わせる：海の 壁紙の 0.48秒／2.3秒 から ギャロップの 秒と 馬の 大きさで）
HILL_S = 26.0      # 遠くの 山が 1まい 流れる 秒
SHOOT = 19.0       # 流れ星の 1回り（秒）
FLOAT = 5.0        # ふわっと 浮く 1回り（秒）
UFO_T = 8.0        # UFO が 見に くる 1回り（秒）
UFO_AT = (128, -2) # UFO が とまる 所（左上・ページの px）：馬の 背中の 上（頭や たてがみに 重ならない・浮いた 馬とも ぶつからない）
UFO_K = 0.79       # UFO の 大きさ（絵 56×30 の 倍）
RISE = 22          # ふわっと 浮く 高さ（px：ヘルメットが 上の はしに かからない）
EARTH = (320, 64, 38)      # 地球の 中心と 半径（下の ほうは 遠くの 山に かくれる＝月から 見る 地球の出）
HZ = 104           # 遠くの 山の すそ（だいたいの 地平線）


# ---------------------------------------------------------------- 絵
def sky_svg():
    """空：こい 紺 → 地平線の 近くは 少し 明るい・うすい 星雲・止まった 星（小さな 点）"""
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#050816'/><stop offset='.62' stop-color='#0C1333'/>"
            "<stop offset='1' stop-color='#1A2552'/></linearGradient>"
            "<radialGradient id='n1' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#5B3FA8' stop-opacity='.42'/><stop offset='1' stop-color='#5B3FA8' stop-opacity='0'/></radialGradient>"
            "<radialGradient id='n2' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#2E6FB0' stop-opacity='.36'/><stop offset='1' stop-color='#2E6FB0' stop-opacity='0'/></radialGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
    o += "<ellipse cx='120' cy='40' rx='140' ry='46' fill='url(#n1)' transform='rotate(-14 120 40)'/>"
    o += "<ellipse cx='225' cy='70' rx='110' ry='34' fill='url(#n2)' transform='rotate(10 225 70)'/>"
    R = rnd(19)
    for i in range(150):
        x, y = R.uniform(0, W), R.uniform(0, HZ + 4) ** 1.0
        if math.hypot(x - EARTH[0], y - EARTH[1]) < EARTH[2] + 4:
            continue
        r = R.choice((0.45, 0.55, 0.6, 0.7, 0.8, 1.0)) * (1.25 if R.random() < 0.08 else 1)
        c = R.choice(('#FFFFFF', '#FFFFFF', '#DCE8FF', '#FFF2D6', '#CFE0FF'))
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='{c}' opacity='{f(R.uniform(.45, .95))}'/>"
    # 天の川の ように 細かい 星の 帯（うすく）
    for i in range(90):
        t = R.random()
        x = t * W
        y = 18 + t * 52 + R.gauss(0, 6)
        if math.hypot(x - EARTH[0], y - EARTH[1]) < EARTH[2] + 4:
            continue
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.3, .55))}' fill='#E6EEFF' opacity='{f(R.uniform(.3, .7))}'/>"
    return doc(W, H, o, defs=defs)


def blob(cx, cy, rx, ry, R, n=30, rough=0.22):
    """でこぼこの ある 形（大陸・島）：まわりの 長さを 何本かの なみで ゆらす"""
    ph = [R.uniform(0, 6.3) for _ in range(4)]
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = 1 + rough * (0.55 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2]) + 0.12 * math.sin(9 * a + ph[3]))
        pts.append((cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr))
    return pts


def earth_strip(w, h, seed=4):
    """地球の 表面（横に くり返す）：海（こい 青 → 明るい 青）・大陸（緑・こい 緑・さばくの 茶）・島・北と 南の 氷"""
    R = rnd(seed)
    defs = ("<linearGradient id='o' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2B6FC0'/><stop offset='.5' stop-color='#3C8EDB'/>"
            "<stop offset='1' stop-color='#2A66B4'/></linearGradient>")
    o = f"<rect width='{w}' height='{h}' fill='url(#o)'/>"
    lands = [(0.08, 0.36, 0.10, 0.17), (0.17, 0.66, 0.06, 0.16), (0.40, 0.40, 0.09, 0.20), (0.47, 0.70, 0.05, 0.12),
             (0.66, 0.34, 0.15, 0.15), (0.74, 0.62, 0.05, 0.09), (0.90, 0.72, 0.06, 0.07)]
    for cx, cy, rx, ry in lands:
        pts = blob(cx * w, cy * h, rx * w, ry * h, R)
        inner = blob(cx * w + rx * w * 0.15, cy * h - ry * h * 0.1, rx * w * 0.55, ry * h * 0.55, R, rough=0.3)
        desert = blob(cx * w - rx * w * 0.25, cy * h + ry * h * 0.15, rx * w * 0.4, ry * h * 0.35, R, rough=0.35)
        for dx in (-w, 0, w):
            sh = lambda q: [(x + dx, y) for x, y in q]
            o += f"<path d='{smooth(sh(pts))}' fill='#5FAE58'/>"
            o += f"<path d='{smooth(sh(inner))}' fill='#3F8E46' opacity='.85'/>"
            o += f"<path d='{smooth(sh(desert))}' fill='#C9B06A' opacity='.8'/>"
            o += f"<path d='{smooth(sh(pts))}' fill='none' stroke='#9ED68A' stroke-width='.8' opacity='.5'/>"
    for i in range(10):                                                  # 小さな 島
        x, y = R.uniform(0, w), R.uniform(0.2, 0.8) * h
        pts = blob(x, y, R.uniform(1.6, 3.2), R.uniform(1.2, 2.4), R, n=12)
        for dx in (-w, 0, w):
            o += f"<path d='{smooth([(px + dx, py) for px, py in pts])}' fill='#6DBA62'/>"
    for x0 in (0.05, 0.38, 0.7):                                       # 北と 南の 氷（ふちが ぎざぎざ）
        for top in (True, False):
            pts = []
            n = 9
            for k in range(n + 1):
                x = (x0 + 0.28 * k / n) * w
                yy = (0.06 + 0.05 * abs(math.sin(k * 1.7 + x0 * 9))) * h
                pts.append((x, yy if top else h - yy))
            pts += [(pts[-1][0], 0 if top else h), (pts[0][0], 0 if top else h)]
            for dx in (-w, 0, w):
                o += f"<path d='{P([(x + dx, y) for x, y in pts])}' fill='#F2F7FF' opacity='.9'/>"
    return doc(w, h, o, defs=defs)


def cloud_strip(w, h, seed=8):
    """地球の 雲（横に くり返す）：白い うず・すじ"""
    R = rnd(seed)
    o = ''
    for i in range(16):
        x, y = R.uniform(0, w), R.uniform(h * 0.12, h * 0.88)
        L = R.uniform(10, 34)
        th = R.uniform(1.4, 3.4)
        bend = R.uniform(-5, 5)
        for dx in (-w, 0, w):
            o += f"<path d='M{f(x + dx)} {f(y)} q{f(L * 0.5)} {f(bend)} {f(L)} {f(R.uniform(-2, 2))}' fill='none' stroke='#FFFFFF' stroke-width='{f(th)}' stroke-linecap='round' opacity='{f(R.uniform(.6, .9))}'/>"
        if i % 4 == 0:                                                   # ところどころ ふわっと した 雲の かたまり
            for dx in (-w, 0, w):
                o += (f"<ellipse cx='{f(x + dx + L * 0.5)}' cy='{f(y + 2)}' rx='{f(L * 0.35)}' ry='{f(th * 1.1)}' fill='#FFFFFF' opacity='.55'/>")
    return doc(w, h, o)


def earth_shade(r):
    """地球の 丸み：左上から 光・右下は 夜（ふちは 暗く）・大気の うすい 青"""
    d = 2 * r
    defs = ("<radialGradient id='a' cx='.36' cy='.34' r='.75'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.22'/><stop offset='.45' stop-color='#FFFFFF' stop-opacity='0'/>"
            "<stop offset='.72' stop-color='#020617' stop-opacity='.35'/><stop offset='1' stop-color='#020617' stop-opacity='.85'/></radialGradient>"
            "<linearGradient id='t' x1='0' y1='0' x2='1' y2='.4'><stop offset='.52' stop-color='#020617' stop-opacity='0'/><stop offset='.74' stop-color='#020617' stop-opacity='.55'/>"
            "<stop offset='1' stop-color='#020617' stop-opacity='.8'/></linearGradient>")
    o = (f"<circle cx='{r}' cy='{r}' r='{r}' fill='url(#a)'/><circle cx='{r}' cy='{r}' r='{r}' fill='url(#t)'/>"
         f"<circle cx='{r}' cy='{r}' r='{f(r - 0.8)}' fill='none' stroke='#9FD3FF' stroke-width='1.6' opacity='.55'/>")
    return doc(d, d, o, defs=defs)


def earth_glow(r):
    g = r + 10
    d = 2 * g
    defs = (f"<radialGradient id='g' cx='.5' cy='.5' r='.5'><stop offset='{f(r / g * 0.97, 3)}' stop-color='#7CC4FF' stop-opacity='.55'/>"
            "<stop offset='1' stop-color='#7CC4FF' stop-opacity='0'/></radialGradient>")
    return doc(d, d, f"<circle cx='{g}' cy='{g}' r='{g}' fill='url(#g)'/>", defs=defs)


def crater(cx, cy, rx, ry, base, deep=1.0):
    """くぼみ（光は 左上から）：ふちの 明るい 輪・中の かげ（左がわ）"""
    lt, dk, rim = mix(base, '#FFFFFF', 0.28), mix(base, '#1A1C26', 0.32 * deep), mix(base, '#FFFFFF', 0.42)
    return (f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='{f(rx * 1.12)}' ry='{f(ry * 1.2)}' fill='{lt}' opacity='.55'/>"
            f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='{f(rx)}' ry='{f(ry)}' fill='{dk}'/>"
            f"<ellipse cx='{f(cx + rx * 0.14)}' cy='{f(cy + ry * 0.12)}' rx='{f(rx * 0.84)}' ry='{f(ry * 0.8)}' fill='{mix(base, '#1A1C26', 0.12)}'/>"
            f"<path d='M{f(cx + rx * 0.2)} {f(cy + ry * 0.98)} A{f(rx)} {f(ry)} 0 0 0 {f(cx + rx * 0.98)} {f(cy + ry * 0.1)}' fill='none' stroke='{rim}' stroke-width='{f(max(0.8, ry * 0.18))}' stroke-linecap='round' opacity='.9'/>")


def ground_svg(w=W, h=58, seed=12):
    """手前の 月の 地面（横に くり返す：はば w）：上は 明るい 灰色 → 手前は 少し 暗い・くぼみ・小石・こまかい つぶ"""
    R = rnd(seed)
    defs = ("<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#B9BDC8'/><stop offset='.35' stop-color='#A6AAB6'/>"
            "<stop offset='1' stop-color='#7C808E'/></linearGradient>")
    o = f"<rect width='{w}' height='{h}' fill='url(#g)'/>"
    o += f"<rect width='{w}' height='1.4' fill='#D6D9E0' opacity='.8'/>"
    items = []
    for i in range(16):
        x = R.uniform(0, w)
        y = R.uniform(8, h - 6)
        k = 0.5 + y / h
        items.append((y, 'c', x, R.uniform(6, 16) * k, R.uniform(1.6, 3.6) * k))
    for i in range(26):
        x, y = R.uniform(0, w), R.uniform(4, h - 3)
        k = 0.5 + y / h
        items.append((y, 'r', x, R.uniform(1.2, 3.2) * k, R.uniform(0.8, 1.8) * k))
    items.sort()
    for y, kind, x, a, b in items:
        base = mix('#B4B8C3', '#7C808E', y / h)
        for dx in (-w, 0, w):
            if kind == 'c':
                o += crater(x + dx, y, a, b, base)
            else:
                o += (f"<ellipse cx='{f(x + dx + 0.6)}' cy='{f(y + b * 0.6)}' rx='{f(a)}' ry='{f(b * 0.5)}' fill='#5A5E6C' opacity='.45'/>"
                      f"<ellipse cx='{f(x + dx)}' cy='{f(y)}' rx='{f(a)}' ry='{f(b)}' fill='{mix(base, '#5A5E6C', .35)}'/>"
                      f"<ellipse cx='{f(x + dx - a * 0.3)}' cy='{f(y - b * 0.35)}' rx='{f(a * 0.45)}' ry='{f(b * 0.35)}' fill='{mix(base, '#FFFFFF', .35)}'/>")
    for i in range(160):
        x, y = R.uniform(0, w), R.uniform(2, h)
        for dx in (-w, 0, w):
            if -2 < x + dx < w + 2:
                o += f"<circle cx='{f(x + dx)}' cy='{f(y)}' r='{f(R.uniform(.3, .7))}' fill='{R.choice(('#E2E4EA', '#6E7280'))}' opacity='.55'/>"
    return doc(w, h, o, defs=defs)


def hills_svg(w=W, h=40, seed=31):
    """遠くの 月の 山（横に くり返す）：遠い 山なみ（こい）と 近い 山なみ（明るい ふち・左がわに 影）・ふちの くぼみ・小さな 旗（金の 蹄鉄）"""
    R = rnd(seed)
    o = ''
    back = []
    for k in range(0, 17):
        x = w * k / 16
        back.append((x, 12 + 7 * math.sin(k * 1.3) + 3 * math.sin(k * 2.9) + (R.uniform(-2, 2) if 0 < k < 16 else 0)))
    back[-1] = (w, back[0][1])
    o += f"<path d='{smooth(back, close=False)} L{w} {h} L0 {h} Z' fill='#4A5068'/>"
    o += f"<path d='{smooth(back, close=False)}' fill='none' stroke='#7A819A' stroke-width='.9' opacity='.8'/>"
    front = []
    for k in range(0, 11):
        x = w * k / 10
        front.append((x, 22 + 5 * math.sin(k * 2.1 + 0.6) + (R.uniform(-1.5, 1.5) if 0 < k < 10 else 0)))
    front[-1] = (w, front[0][1])
    o += f"<path d='{smooth(front, close=False)} L{w} {h} L0 {h} Z' fill='#7A8094'/>"
    o += f"<path d='{smooth(front, close=False)}' fill='none' stroke='#C2C7D4' stroke-width='1.1' opacity='.85'/>"
    for x, y, rx, ry in ((60, 31, 9, 2.2), (190, 29, 12, 2.6), (300, 33, 7, 1.8)):
        o += crater(x, y, rx, ry, '#7A8094', 0.8)
    o += f"<rect y='{h - 3}' width='{w}' height='3' fill='#9A9FAD'/>"
    fx, fy = 236, 22
    o += (f"<path d='M{fx} {fy + 9} V{fy - 9}' stroke='#D7DBE6' stroke-width='.9'/>"
          f"<path d='M{fx + .4} {fy - 9} H{fx + 11} V{fy - 2.6} H{fx + .4} Z' fill='#1C2B66'/>"
          f"<path d='M{fx + 3.6} {fy - 7.6} a2.3 2.3 0 0 0 4.6 0 v2.6 a2.3 2.3 0 0 1 -4.6 0 Z' fill='none' stroke='#F2D16B' stroke-width='.9'/>")
    return doc(w, h, o)


def dust_svg():
    return doc(20, 14, "<ellipse cx='10' cy='8' rx='9' ry='5.5' fill='#C9CDD8' opacity='.75'/><ellipse cx='8' cy='6.5' rx='5' ry='3.4' fill='#E2E5EC' opacity='.8'/>")


def shoot_svg():
    """流れ星：細い 光の すじ（右下が 先）"""
    defs = ("<linearGradient id='l' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#9FD3FF' stop-opacity='0'/><stop offset='.85' stop-color='#E6F4FF' stop-opacity='.85'/>"
            "<stop offset='1' stop-color='#FFFFFF'/></linearGradient>")
    return doc(70, 6, "<path d='M0 3 L66 2.2 L66 3.8 Z' fill='url(#l)'/><circle cx='66.5' cy='3' r='1.6' fill='#FFFFFF'/>", defs=defs)


def twinkle_svg():
    return doc(12, 12, f"<path d='{sparkle_d(6, 6, 5.6, 0.14)}' fill='#FFFFFF'/><circle cx='6' cy='6' r='1.1' fill='#FFFFFF'/>")


def ufo_saucer():
    """UFO の 円盤（56×30：まん中 28・円盤の まん中の 高さ 20）：銀の 円盤・下の こい 輪・ふちの 小さな 明かり・屋根の ガラスの ふちと つや（中身は 別）"""
    defs = ("<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#F4F7FF'/><stop offset='.45' stop-color='#C3CBE0'/>"
            "<stop offset='.6' stop-color='#9AA4C2'/><stop offset='1' stop-color='#5E6888'/></linearGradient>")
    o = ("<path d='M2 20 C2 13 54 13 54 20 C54 26.5 2 26.5 2 20 Z' fill='url(#g)' stroke='#3E4868' stroke-width='.8'/>"
         "<path d='M4 19 C12 15.6 44 15.6 52 19' fill='none' stroke='#FFFFFF' stroke-width='.9' stroke-linecap='round' opacity='.75'/>"
         "<ellipse cx='28' cy='25.6' rx='12' ry='2.4' fill='#3E4868'/><ellipse cx='28' cy='25' rx='9' ry='1.4' fill='#8FD3FF' opacity='.65'/>")
    for k, c in enumerate(('#FFD166', '#7CE0FF', '#FF8FB1', '#FFD166', '#7CE0FF')):
        t = (k + 0.5) / 5
        o += f"<circle cx='{f(6 + t * 44)}' cy='{f(21.6 + math.sin(math.pi * t) * 1.6)}' r='1.25' fill='{c}'/>"
    o += ("<path d='M16 14.6 C16.6 4.4 39.4 4.4 40 14.6' fill='none' stroke='#DDF4FF' stroke-width='.9'/>"
          "<path d='M19.4 11.6 C20.6 7.6 24.6 6 28 5.8' fill='none' stroke='#FFFFFF' stroke-width='1.3' stroke-linecap='round' opacity='.8'/>")
    return doc(56, 30, o, defs=defs)


def ufo_dome():
    """屋根の ガラス（すき通った 水色）"""
    defs = ("<radialGradient id='d' cx='.38' cy='.3' r='.85'><stop offset='0' stop-color='#E9FBFF' stop-opacity='.7'/><stop offset='.6' stop-color='#7FD3F5' stop-opacity='.45'/>"
            "<stop offset='1' stop-color='#2E7FB8' stop-opacity='.55'/></radialGradient>")
    return doc(56, 30, "<path d='M16 14.8 C16.6 4.4 39.4 4.4 40 14.8 Z' fill='url(#d)'/>", defs=defs)


def ufo_alien():
    """中の 小さな 宇宙人（緑の 頭・大きな 黒い 目・つの 2本）。12×12（目は 右を 向く）"""
    o = ("<path d='M4.2 2.6 L3.4 .6 M7.8 2.6 L8.8 .6' stroke='#5CC46A' stroke-width='.8' stroke-linecap='round'/>"
         "<circle cx='3.4' cy='.7' r='.8' fill='#B6F07A'/><circle cx='8.8' cy='.7' r='.8' fill='#B6F07A'/>"
         "<path d='M6 2.2 C9.4 2.2 10.6 4.6 10.4 6.8 C10.2 9.4 8 11 6 11 C4 11 1.8 9.4 1.6 6.8 C1.4 4.6 2.6 2.2 6 2.2 Z' fill='#7EDB7A'/>"
         "<ellipse cx='4.4' cy='6.2' rx='1.3' ry='1.8' transform='rotate(-14 4.4 6.2)' fill='#141820'/>"
         "<ellipse cx='7.9' cy='6.2' rx='1.3' ry='1.8' transform='rotate(14 7.9 6.2)' fill='#141820'/>"
         "<circle cx='4.8' cy='5.5' r='.42' fill='#FFFFFF'/><circle cx='8.3' cy='5.5' r='.42' fill='#FFFFFF'/>"
         "<path d='M5 9 Q6 9.7 7 9' fill='none' stroke='#2E6E3A' stroke-width='.55' stroke-linecap='round'/>")
    return doc(12, 12, o)


def ufo_beam():
    """UFO の 下の やわらかい 光の すじ（上が 細く 下へ ひろがる・下ほど うすい）。60×74"""
    defs = ("<linearGradient id='b' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#DFF6FF' stop-opacity='.9'/><stop offset='.55' stop-color='#9FE0FF' stop-opacity='.45'/>"
            "<stop offset='1' stop-color='#9FE0FF' stop-opacity='0'/></linearGradient>"
            "<linearGradient id='e' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#FFFFFF' stop-opacity='0'/><stop offset='.5' stop-color='#FFFFFF' stop-opacity='.35'/>"
            "<stop offset='1' stop-color='#FFFFFF' stop-opacity='0'/></linearGradient>")
    return doc(60, 74, "<path d='M22 0 H38 L60 74 H0 Z' fill='url(#b)'/><path d='M26 0 H34 L42 74 H18 Z' fill='url(#e)' opacity='.6'/>", defs=defs)


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    run = B.get('run')
    still = B.get('still')
    alt = ('星空の月面を、ガラスのヘルメットをかぶった芦毛の競走馬（紺のゼッケン1）が走る。うしろの空に青い地球、遠くに月の山と小さな旗のイラスト'
           '（馬はいつも走っていて、月の地面が流れ、砂ぼこりがふわっと立つ。ときどき馬がふわっと宙に浮いて、ゆっくりおりる。'
           'ときどき小さな宇宙人の乗ったUFOが飛んできて、馬の上でとまってのぞきこみ、また飛んでいく。ときどき流れ星）')
    ex, ey, er = EARTH
    html = f'<div class="ucw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('ucSky', sky_svg())
    for k in range(7):
        html += img(f'ucTw t{k}', twinkle_svg())
    html += img('ucGl', earth_glow(er))
    html += (f'<i class="ucE"><i class="ucEl" style="background-image:url(&quot;{durl(earth_strip(int(2 * math.pi * er), 2 * er))}&quot;)"></i>'
             f'<i class="ucEc" style="background-image:url(&quot;{durl(cloud_strip(int(2 * math.pi * er), 2 * er))}&quot;)"></i>'
             + img('ucEs', earth_shade(er)) + '</i>')
    for k in range(3):
        html += img(f'ucSh s{k}', shoot_svg())
    html += f'<i class="ucHl" style="background-image:url(&quot;{durl(hills_svg())}&quot;)"></i>'
    html += f'<i class="ucGd" style="background-image:url(&quot;{durl(ground_svg())}&quot;)"></i>'
    html += '<i class="ucSw"><i class="ucSd"></i></i>'                 # 影（浮くと 小さく）
    html += '<i class="ucDw">' + ''.join(img(f'ucDs d{k}', dust_svg()) for k in range(4)) + '</i>'   # 砂ぼこり（浮いて いる 間は 出ない）
    html += img('ucLd l0', dust_svg()) + img('ucLd l1', dust_svg())     # おりた ときの 砂ぼこり
    if run:
        html += '<i class="ucFl"><i class="ucH"><i></i></i></i>'        # 5秒に 1回 ふわっと 浮く
    html += ('<i class="ucU"><i class="ucUb">' + img('ucBm', ufo_beam()) + '</i><i class="ucUr"><i class="ucUt">'
             + img('ucUd', ufo_dome()) + img('ucUa', ufo_alien()) + img('ucUs', ufo_saucer()) + '</i></i></i>')   # 8秒に 1回 UFO
    html += '</div>'

    css = ('.ucw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#0C1333}'
           '.ucw>*{position:absolute;display:block}'
           '.ucw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.ucw .ucSky{left:0;top:0;width:390px;height:160px}'
           '.ucw .ucTw{width:9px;height:9px;opacity:.2;animation:ucTw 3.4s ease-in-out infinite;will-change:opacity,transform}'
           f'.ucw .ucGl{{left:{ex - er - 10}px;top:{ey - er - 10}px;width:{2 * er + 20}px;height:{2 * er + 20}px}}'
           f'.ucw .ucE{{left:{ex - er}px;top:{ey - er}px;width:{2 * er}px;height:{2 * er}px;border-radius:50%;overflow:hidden;-webkit-mask-image:radial-gradient(circle,#000 70%,#000 71%);transform:translateZ(0)}}'
           f'.ucw .ucE>*{{position:absolute;display:block;top:0;height:{2 * er}px}}'
           f'.ucw .ucEl{{left:0;width:{2 * int(2 * math.pi * er) + 2}px;background-size:{int(2 * math.pi * er)}px {2 * er}px;background-repeat:repeat-x;animation:ucSpin 60s linear infinite}}'
           f'.ucw .ucEc{{left:0;width:{2 * int(2 * math.pi * er) + 2}px;background-size:{int(2 * math.pi * er)}px {2 * er}px;background-repeat:repeat-x;animation:ucSpin 38s linear infinite}}'
           f'.ucw .ucEs{{left:0;width:{2 * er}px}}'
           '.ucw .ucSh{left:0;top:0;width:70px;height:6px;opacity:0;transform-origin:66px 3px;will-change:transform,opacity}'
           f'.ucw .ucHl{{left:0;top:{HZ - 28}px;width:{2 * W + 2}px;height:40px;background-size:{W}px 40px;background-repeat:repeat-x;animation:ucHill {HILL_S}s linear infinite}}'
           f'.ucw .ucGd{{left:0;top:{H - 58 + 2}px;width:{2 * W + 2}px;height:58px;background-size:{W}px 58px;background-repeat:repeat-x;animation:ucGround {GROUND_S}s linear infinite}}'
           '.ucw .ucDs{width:20px;height:14px;opacity:0;will-change:transform,opacity}'
           '.ucw .ucSw>*,.ucw .ucDw>*,.ucw .ucFl>*,.ucw .ucU *{position:absolute;display:block}'
           '.ucw .ucSw,.ucw .ucDw,.ucw .ucFl{left:0;top:0;width:390px;height:160px}'
           f'.ucw .ucDw{{animation:ucDw {FLOAT}s linear infinite}}'
           f'.ucw .ucFl{{transform-origin:165px 100px;animation:ucFloat {FLOAT}s linear infinite;will-change:transform}}'
           f'.ucw .ucLd{{width:20px;height:14px;opacity:0;animation:ucLand {FLOAT}s linear infinite;will-change:transform,opacity}}'
           '.ucw .ucLd.l0{left:192px;top:124px}.ucw .ucLd.l1{left:104px;top:125px;animation-delay:-.06s}'
           # UFO（56×30）：とまる 所は UFO_AT
           f'.ucw .ucU{{left:0;top:0;width:56px;height:30px;opacity:0;transform-origin:0 0;animation:ucUfo {UFO_T}s linear infinite;will-change:transform,opacity}}'
           f'.ucw .ucUb{{left:-2px;top:22px;width:60px;height:74px;opacity:0;animation:ucBeam {UFO_T}s linear infinite}}'
           '.ucw .ucBm{left:0;top:0;width:60px;height:74px}'
           '.ucw .ucUr{left:0;top:0;width:56px;height:30px;animation:ucBob 1.7s ease-in-out infinite alternate}'
           f'.ucw .ucUt{{left:0;top:0;width:56px;height:30px;transform-origin:28px 20px;animation:ucTilt {UFO_T}s linear infinite}}'
           '.ucw .ucUd,.ucw .ucUs{left:0;top:0;width:56px;height:30px}'
           f'.ucw .ucUa{{left:22px;top:4.6px;width:12px;height:12px;transform-origin:6px 11px;animation:ucPeek {UFO_T}s linear infinite}}')
    if run:
        n, (cw, ch), (ax, ay) = run['frames'], run['cell'], run['at']
        w, h = cw / 2, ch / 2
        css += (f'.ucw .ucH{{left:{f(ax / 2)}px;top:{f(ay / 2)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'
                f'.ucw .ucH>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({run["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;'
                f'animation:ucRun {RUN_S}s steps({n}) infinite}}'
                + kf('ucRun', [(100, f'transform:translateX({f(-n * w)}px)')]))
        # 影：浮くと 小さく うすく（コマごと）
        dys = run.get('dy') or [0] * n
        lo, hi = min(dys), max(dys)
        stops = []
        for i, d in enumerate(dys):
            t = (hi - d) / (hi - lo) if hi > lo else 0
            stops.append((100 * i / n, f'transform:scale({f(1 - 0.32 * t, 3)},{f(1 - 0.25 * t, 3)});opacity:{f(0.55 - 0.25 * t, 3)}'))
        stops.append((100, stops[0][1]))
        g = run.get('ground', 132.0)
        hx0, hx1 = run.get('hx', [ax / 2 + w * 0.2, ax / 2 + w * 0.84])
        sw_ = (hx1 - hx0) * 0.66
        scx = (hx0 + hx1) / 2
        css += (f'.ucw .ucSd{{left:{f(scx - sw_ / 2)}px;top:{f(g - 3.5)}px;width:{f(sw_)}px;height:9px;border-radius:50%;background:radial-gradient(closest-side,rgba(10,12,24,.85),rgba(10,12,24,0));'
                f'animation:ucShad {RUN_S}s step-end infinite}}' + kf('ucShad', stops)
                + f'.ucw .ucSw{{transform-origin:{f(scx)}px {f(g + 1)}px;animation:ucSwF {FLOAT}s linear infinite}}')
        # 砂ぼこり：うしろ足の あたりから うしろへ ふわっと（ギャロップ 2回に 1こ）
        hx = ax / 2 + w * 0.2
        for k in range(4):
            css += f'.ucw .ucDs.d{k}{{left:{f(hx - 6 + (k % 2) * 8)}px;top:{f(126 + (k % 2) * 3)}px;animation:ucDust {f(RUN_S * 4, 3)}s ease-out {f(-RUN_S * k, 3)}s infinite}}'
    else:
        css += '.ucw .ucSd{display:none}'
    for k, (x, y, d) in enumerate(((30, 18, 0.0), (96, 50, 1.2), (150, 12, 2.3), (214, 34, 0.6), (262, 66, 1.8), (380, 14, 2.8), (58, 70, 3.1))):
        css += f'.ucw .ucTw.t{k}{{left:{f(x - 4.5)}px;top:{f(y - 4.5)}px;animation-delay:{f(-d, 2)}s}}'
    # 流れ星（19秒に 3回）：右上 → 左下 の ななめ（すじの 先は 右下）
    for k, (t0, x0, y0, x1, y1, ang) in enumerate(((2.0, 60, -6, 190, 46, 22), (9.5, 200, -8, 300, 32, 20), (15.4, 10, 10, 120, 58, 24))):
        a, b, c = 100 * t0 / SHOOT, 100 * (t0 + 0.12) / SHOOT, 100 * (t0 + 0.95) / SHOOT
        stops = [(0, f'opacity:0;transform:translate({x0}px,{y0}px) rotate({ang}deg) scaleX(.3)'),
                 (a, f'opacity:0;transform:translate({x0}px,{y0}px) rotate({ang}deg) scaleX(.3)'),
                 (b, f'opacity:.95;transform:translate({f(x0 + (x1 - x0) * 0.15)}px,{f(y0 + (y1 - y0) * 0.15)}px) rotate({ang}deg) scaleX(1)'),
                 (c, f'opacity:0;transform:translate({x1}px,{y1}px) rotate({ang}deg) scaleX(.6)'),
                 (100, f'opacity:0;transform:translate({x1}px,{y1}px) rotate({ang}deg) scaleX(.6)')]
        css += f'.ucw .ucSh.s{k}{{animation:ucShoot{k} {SHOOT}s linear infinite}}' + kf(f'ucShoot{k}', stops)
    css += (kf('ucTw', [(0, 'opacity:.15;transform:scale(.45)'), (50, 'opacity:.95;transform:scale(1)'), (100, 'opacity:.15;transform:scale(.45)')])
            + kf('ucSpin', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-int(2 * math.pi * er)}px)')])
            + kf('ucHill', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('ucGround', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('ucDust', [(0, 'opacity:0;transform:translate(0,0) scale(.35)'), (6, 'opacity:.85;transform:translate(-12px,-4px) scale(.6)'),
                            (45, 'opacity:.45;transform:translate(-118px,-12px) scale(1.15)'), (72, 'opacity:0;transform:translate(-190px,-15px) scale(1.35)'),
                            (100, 'opacity:0;transform:translate(-190px,-15px) scale(1.35)')]))   # 砂ぼこりは 地面と いっしょに うしろへ（月なので ゆっくり 上へ）
    # 5秒に 1回 ふわっと 浮く（0.3秒から 1秒で RISE px 上へ → ただよう → 1秒で おりる＝2.9秒）。影は 小さく うすく・砂ぼこりは 止める・おりた ときに ふわっ
    F = lambda t: 100 * t / FLOAT
    css += kf('ucFloat', [(0, 'transform:translateY(0) rotate(0)'), (F(0.3), 'transform:translateY(0) rotate(0);animation-timing-function:cubic-bezier(.2,.7,.35,1)'),
                          (F(1.3), f'transform:translateY({-RISE}px) rotate(-3deg);animation-timing-function:ease-in-out'),
                          (F(1.9), f'transform:translateY({-RISE - 1.5}px) rotate(-1.2deg);animation-timing-function:cubic-bezier(.55,0,.85,.55)'),
                          (F(2.9), 'transform:translateY(0) rotate(1.4deg);animation-timing-function:ease-out'), (F(3.15), 'transform:translateY(0) rotate(0)'),
                          (100, 'transform:translateY(0) rotate(0)')])
    css += kf('ucSwF', [(0, 'transform:scale(1);opacity:1'), (F(0.3), 'transform:scale(1);opacity:1;animation-timing-function:cubic-bezier(.2,.7,.35,1)'),
                        (F(1.3), 'transform:scale(.5);opacity:.45;animation-timing-function:ease-in-out'), (F(1.9), 'transform:scale(.48);opacity:.42;animation-timing-function:cubic-bezier(.55,0,.85,.55)'),
                        (F(2.9), 'transform:scale(1);opacity:1'), (100, 'transform:scale(1);opacity:1')])
    css += kf('ucDw', [(0, 'opacity:1'), (F(0.3), 'opacity:1'), (F(0.55), 'opacity:0'), (F(2.9), 'opacity:0'), (F(3.0), 'opacity:1'), (100, 'opacity:1')])
    css += kf('ucLand', [(0, 'opacity:0;transform:translate(0,0) scale(.4)'), (F(2.88), 'opacity:0;transform:translate(0,0) scale(.4)'),
                         (F(2.92), 'opacity:.85;transform:translate(0,0) scale(.5)'), (F(3.5), 'opacity:.5;transform:translate(-75px,-7px) scale(1.25)'),
                         (F(3.8), 'opacity:0;transform:translate(-113px,-9px) scale(1.45)'), (100, 'opacity:0;transform:translate(-113px,-9px) scale(1.45)')])
    # 8秒に 1回 UFO：右上から 来て（0.8〜2.2秒）馬の 上で とまる（〜5.6秒・宇宙人が のぞく・光の すじ）→ 左上へ（〜6.6秒）
    U = lambda t: 100 * t / UFO_T
    ux, uy = UFO_AT
    K = f'scale({UFO_K})'
    css += kf('ucUfo', [(0, f'opacity:0;transform:translate(430px,-44px) {K}'), (U(0.8), f'opacity:1;transform:translate(430px,-44px) {K};animation-timing-function:ease-out'),
                        (U(1.6), f'opacity:1;transform:translate({ux + 80}px,{uy - 12}px) {K};animation-timing-function:ease-out'),
                        (U(2.2), f'opacity:1;transform:translate({ux}px,{uy}px) {K};animation-timing-function:ease-in-out'),
                        (U(3.3), f'opacity:1;transform:translate({ux - 6}px,{uy + 1}px) {K};animation-timing-function:ease-in-out'),
                        (U(4.6), f'opacity:1;transform:translate({ux + 4}px,{uy}px) {K};animation-timing-function:ease-in-out'),
                        (U(5.6), f'opacity:1;transform:translate({ux}px,{uy}px) {K};animation-timing-function:cubic-bezier(.5,0,.9,.6)'),
                        (U(6.6), f'opacity:1;transform:translate(-90px,-48px) {K}'), (U(6.62), f'opacity:0;transform:translate(-90px,-48px) {K}'),
                        (100, f'opacity:0;transform:translate(430px,-44px) {K}')])
    css += kf('ucTilt', [(0, 'transform:rotate(-12deg)'), (U(1.6), 'transform:rotate(-10deg)'), (U(2.2), 'transform:rotate(2deg)'), (U(2.6), 'transform:rotate(0)'),
                         (U(3.0), 'transform:rotate(-8deg)'), (U(5.0), 'transform:rotate(-7deg)'), (U(5.6), 'transform:rotate(0)'), (U(6.0), 'transform:rotate(-14deg)'),
                         (U(6.6), 'transform:rotate(-14deg)'), (100, 'transform:rotate(-12deg)')])
    css += kf('ucPeek', [(0, 'transform:translate(0,3px) rotate(0)'), (U(2.5), 'transform:translate(0,3px) rotate(0)'),
                         (U(2.85), 'transform:translate(-2px,-1.4px) rotate(-14deg)'), (U(5.0), 'transform:translate(-2px,-1.4px) rotate(-14deg)'),
                         (U(5.35), 'transform:translate(0,3px) rotate(0)'), (100, 'transform:translate(0,3px) rotate(0)')])
    css += kf('ucBeam', [(0, 'opacity:0'), (U(2.6), 'opacity:0'), (U(3.1), 'opacity:.36'), (U(4.9), 'opacity:.36'), (U(5.4), 'opacity:0'), (100, 'opacity:0')])
    css += kf('ucBob', [(0, 'transform:translateY(-1.2px)'), (100, 'transform:translateY(1.2px)')])
    css += reduced('.ucw .ucSky,.ucw .ucTw,.ucw .ucGl,.ucw .ucE,.ucw .ucSh,.ucw .ucHl,.ucw .ucGd,.ucw .ucSw,.ucw .ucDw,.ucw .ucLd,.ucw .ucFl,.ucw .ucU') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_space():
    """背景の もよう：小さな 星・点・小さな わの ある 星（うすく）"""
    R = rnd(3)
    o = ''
    for i in range(16):
        x, y = R.uniform(2, 128), R.uniform(2, 128)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R.uniform(.5, 1.1))}' fill='#C9D8FF' opacity='{f(R.uniform(.25, .5))}'/>"
    for x, y, r in ((30, 36, 3.6), (96, 92, 2.8)):
        o += f"<path d='{sparkle_d(x, y, r, 0.16)}' fill='#F2D16B' opacity='.35'/>"
    o += ("<circle cx='92' cy='30' r='5' fill='#6E7FD6' opacity='.3'/><ellipse cx='92' cy='30' rx='9' ry='2.4' fill='none' stroke='#A9B6F0' stroke-width='1' opacity='.32' transform='rotate(-18 92 30)'/>")
    return tile(130, 130, o)


def orbit_strip():
    """上の 帯の 下の ふち：小さな 星と 点の 列（軌道の 線）"""
    o = ("<path d='M0 3.5 H28' stroke='#3E5AA8' stroke-width='1' stroke-dasharray='2 3' opacity='.9'/>"
         f"<path d='{sparkle_d(14, 3.5, 3.2, 0.18)}' fill='#F2D16B'/><circle cx='4' cy='3.5' r='1' fill='#8FD3FF'/><circle cx='24' cy='3.5' r='1' fill='#8FD3FF'/>")
    return tile(28, 7, o)


def orn():
    """すみの 飾り（44×44）：わの ある 星（土星の ような）と 三日月と 小さな 星"""
    o = ("<ellipse cx='20' cy='24' rx='17' ry='5.2' fill='none' stroke='#F2D16B' stroke-width='2.4' transform='rotate(-18 20 24)'/>"
         "<circle cx='20' cy='24' r='10' fill='#6E7FD6'/><path d='M12 21 Q20 15 28 19' fill='none' stroke='#9FB0F0' stroke-width='2.2' stroke-linecap='round'/>"
         "<path d='M11.6 27 Q20 32 29 26' fill='none' stroke='#4E5DB6' stroke-width='2' stroke-linecap='round'/>"
         "<path d='M4.6 29.4 A17 5.2 0 0 0 35.4 18.6' fill='none' stroke='#F2D16B' stroke-width='2.4' transform='rotate(0 20 24)'/>"
         "<path d='M35 4 a6.4 6.4 0 1 0 4.6 10.8 a5.2 5.2 0 1 1 -4.6 -10.8 Z' fill='#FFF1B8'/>")
    o += f"<path d='{sparkle_d(37, 33, 3.4, 0.18)}' fill='#FFFFFF'/><circle cx='6' cy='8' r='1.3' fill='#FFFFFF'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='宇宙', desc='月面と地球', title='宇宙（紺×月の銀×星の金）', banner=ID,
    alt='星空の月面を、ガラスのヘルメットをかぶった芦毛の競走馬（紺のゼッケン1）が走る。うしろの空に青い地球、遠くに月の山と小さな旗。ときどき小さな宇宙人の乗ったUFOが馬を見にくるイラスト',
    fonts=['Tsukimi+Rounded:wght@700', 'Zen+Kaku+Gothic+New:wght@500;700'],
    v=dict(bg='#0B1028', ink='#EEF2FF', sub='#A9B3D6', card='#151C3C', cardB='1px solid #2B3566', cardO='0 solid transparent', cardS='0 8px 22px rgba(0,0,0,.4)',
           radius='16px', rs='12px', font='"Zen Kaku Gothic New"', dfont='"Tsukimi Rounded"', dw='700', logo='#F4F7FF', logoS='0 0 12px rgba(143,211,255,.55)',
           iii='#8FD3FF', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#060A1E,#111A40)', hdInk='#EEF2FF', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.06)', mLine='rgba(143,211,255,.5)', mInk='#EEF2FF', pill='rgba(255,255,255,.06)', pillLine='rgba(143,211,255,.35)', pillInk='#E3E9FF',
           coin='#F2D16B', coinInk='#1A1530', badge='#1D2650', badgeInk='#F2D16B', badgeB='1.5px solid #3A4A8A', tagBg='rgba(255,255,255,.05)', tagInk='#D6DDF5',
           tagLine='#2F3A6E', warnBg='rgba(242,209,107,.14)', warnInk='#F6D98A', zBg='rgba(255,255,255,.035)', zB='1px solid #2B3566', znBg='#F2D16B', znInk='#1A1530',
           znB='0 solid transparent', znR='999px', znS='none', acc='#8FD3FF', nR='8px', w2B='1.5px solid #8A93BF', sep='1px dashed #2F3A6E',
           btn='#386CDD', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='999px', btnS='0 3px 0 #2549A8,0 0 16px rgba(62,123,250,.35)', btn2='transparent',
           btn2Ink='#8FD3FF', btn2B='1.5px solid #3E5AA8', tab='#070B1E', tabB='1px solid #1C244A', tabInk='#8F9AC4', tabOn='rgba(143,211,255,.12)', tabOnInk='#8FD3FF',
           tabR='14px', sel='#3E7BFA', selInk='#FFFFFF', h1='#F2D16B'),
    chk=dict(hd=['#060A1E', '#111A40']),
    css=[('', 'background-image:' + curi(tile_space()) + ',radial-gradient(ellipse 80% 40% at 80% 0,rgba(91,63,168,.22),transparent 70%);background-size:130px 130px,100% 100%'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-6px;height:7px;background:' + curi(orbit_strip()) + ' 0 0/28px 7px repeat-x'),
         ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(143,211,255,.08),transparent 40%)')],
    orn=orn(),
    guide=dict(colors=[('#0B1028', '宇宙'), ('#3E7BFA', 'ボタン'), ('#8FD3FF', '地球の青'), ('#F2D16B', '星の金'), ('#C9D2E6', '月の銀')],
               fonts='見出し：Tsukimi Rounded（月見）<br>本文：Zen Kaku Gothic New', shape='角丸16px・まるい ボタン・帯の 下に 星の 軌道・星の 背景・すみに わの ある 星と 三日月・的中ボタンは UFOの PUSH',
               pic='星空の 月面・ガラスの ヘルメットの 芦毛の 馬（ギャロップ・ときどき ふわっと 浮く）・青い 地球・遠くの 月の 山と 小さな 旗・ときどき 馬を 見に くる UFO・ときどき 流れ星'),
)


# ================================================================== 的中ボタン：UFO の PUSH（uc）
def push_face(sfx=''):
    """ボタン（200×100）が 空飛ぶ円盤：銀の 円盤（上が 明るい）・ふちに 小さな 明かり（ゆっくり じゅんばんに）・上に ガラスの まるい 屋根（中に 小さな 馬の 頭）"""
    g, d = f'ucG{sfx}', f'ucD{sfx}'
    defs = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F7FF"/><stop offset=".45" stop-color="#C3CBE0"/>'
            f'<stop offset=".55" stop-color="#9AA4C2"/><stop offset="1" stop-color="#5E6888"/></linearGradient>'
            f'<radialGradient id="{d}" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#E9FBFF" stop-opacity=".95"/><stop offset=".55" stop-color="#7FD3F5" stop-opacity=".75"/>'
            '<stop offset="1" stop-color="#2E7FB8" stop-opacity=".85"/></radialGradient></defs>')
    o = ''
    # 屋根（ガラス）と 中の 馬の 頭
    o += f'<path d="M48 22 C50 -30 150 -30 152 22 Z" fill="url(#{d})" stroke="#DDF4FF" stroke-width="2"/>'
    o += ('<path d="M86 22 C84 4 92 -10 104 -14 L108 -24 L111 -13 C118 -10 124 -4 126 6 C127 12 124 16 118 16 L112 14 C110 18 106 22 104 22 Z" fill="#26305A" opacity=".85"/>'
          '<circle cx="112" cy="-2" r="1.8" fill="#FFFFFF" opacity=".9"/>')
    o += '<path d="M62 4 C66 -14 82 -20 96 -20" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity=".75"/>'
    # 円盤
    o += f'<path d="M0 52 C0 22 200 22 200 52 C200 82 0 82 0 52 Z" fill="url(#{g})" stroke="#3E4868" stroke-width="2"/>'
    o += '<path d="M6 50 C30 34 170 34 194 50" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
    o += '<path d="M2 56 C40 70 160 70 198 56 C190 74 10 74 2 56 Z" fill="#46507A" opacity=".55"/>'
    o += '<ellipse cx="100" cy="80" rx="46" ry="9" fill="#3E4868"/><ellipse cx="100" cy="78" rx="38" ry="6" fill="#8FD3FF" opacity=".55"/>'
    return f'<i class="ucf" aria-hidden="true"><svg viewBox="-6 -34 212 130" width="212" height="130">{defs}{o}</svg></i>'


def push_decor(sfx=''):
    """円盤の ふちの 明かり（.uclt：ゆっくり じゅんばんに）・まわりの 星（.uctw）・うかぶ 小さな 星（わの ある 星）"""
    o = ''
    for j in range(9):
        t = j / 8
        x = 14 + t * 172
        y = 60 + math.sin(math.pi * t) * 6
        c = ('#FFD166', '#7CE0FF', '#FF8FB1')[j % 3]
        o += f'<circle class="uclt" cx="{f(x)}" cy="{f(y)}" r="4.2" fill="{c}" style="animation-delay:{-0.22 * j:.2f}s"/>'
    for j, (x, y, r) in enumerate(((-16, 0, 6), (218, -12, 5.4), (30, -52, 4.6), (176, -60, 5), (-26, 70, 4), (228, 74, 4.4))):
        o += f'<path class="uctw" d="{sparkle_d(x, y, r, 0.16)}" fill="#FFF6CC" style="animation-delay:{-0.7 * j:.2f}s"/>'
    o += ('<g transform="translate(-18 -40)"><g class="ucpl"><ellipse rx="13" ry="3.6" fill="none" stroke="#F2D16B" stroke-width="2" transform="rotate(-16)"/>'
          '<circle r="7" fill="#7E8FE6"/><path d="M-13 3.6 A13 3.6 0 0 0 13 -3.6" fill="none" stroke="#F2D16B" stroke-width="2" transform="rotate(-16)"/></g></g>')
    return f'<i class="ucd" aria-hidden="true"><svg viewBox="-40 -80 280 200" width="280" height="200">{o}</svg></i>'


def _star(c='#F2D16B', e='#B8901E'):
    return doc(24, 24, f"<path d='{star_d(12, 12.6, 11, 4.8)}' fill='{c}' stroke='{e}' stroke-width='1.2' stroke-linejoin='round'/>")


def _planet():
    return doc(28, 20, "<ellipse cx='14' cy='10' rx='13' ry='3.6' fill='none' stroke='#F2D16B' stroke-width='2' transform='rotate(-14 14 10)'/>"
                       "<circle cx='14' cy='10' r='6.4' fill='#7E8FE6'/><path d='M1.4 13 A13 3.6 0 0 0 26.6 7' fill='none' stroke='#F2D16B' stroke-width='2'/>")


def _moon():
    return doc(22, 22, "<path d='M14 2 a9 9 0 1 0 6.4 15.4 a7.4 7.4 0 1 1 -6.4 -15.4 Z' fill='#FFF1B8' stroke='#C9A84A' stroke-width='1'/>")


PIECES = dict(sy=piece(_star()), sb=piece(_star('#9FD8FF', '#3E7BB8')), pl=piece(_planet()), mo=piece(_moon()),
              dt='border-radius:50%;background:radial-gradient(circle,#FFFFFF,#BFE6FF 60%,rgba(191,230,255,0))')


def push_burst():
    return fly_burst('uc', ['sy', 'pl', 'sb', 'mo', 'sy', 'dt'], 28, 23, sizes=dict(sy=(15, 21), sb=(12, 17), pl=(20, 26), mo=(14, 19), dt=(7, 10)))


PUSH_CSS = r'''
/* ---------- 宇宙の的中ボタン：UFO の PUSH（壁紙パック） ----------
   ボタンが まるごと 空飛ぶ円盤：銀の 円盤（上が 明るい）に「PUSH」・上に ガラスの まるい 屋根（中に 小さな 馬の 頭）・ふちの 明かりが ゆっくり じゅんばんに 明るく なる（小さな 点だけ）。
   まわりに 星の キラッと わの ある 星。上下の 動きは 的中と 同じ。押すと 円盤が ちぢんで ふくらみ（強く 光らせない）、星・わの ある 星・三日月が はじけて 落ち、水色の 光の 輪が 広がる */
.uc{--pushA:#9AA4C2;--pushB:#26305A;--pushC:#C3CBE0;--rim:#8FD3FF;--rimD:#3E4868}
.push.uc{--pr:50px;background:none;border-radius:50px;box-shadow:none;filter:drop-shadow(0 9px 0 rgba(10,14,40,.5)) drop-shadow(0 18px 24px rgba(0,0,0,.45))}
.push.uc span{top:6px;font:700 38px/1 "Tsukimi Rounded",sans-serif;letter-spacing:.06em;color:#FFFFFF;text-shadow:0 2px 0 #26305A,0 0 10px rgba(143,211,255,.8)}
.push.uc::after{inset:-22px -20px -18px;top:-50px;border-radius:60px;border-color:rgba(143,211,255,.9)}
.uc .ucf{position:absolute;left:-6px;top:-34px;width:212px;height:130px;pointer-events:none;font-style:normal}
.uc .ucf svg{display:block;width:212px;height:130px;overflow:visible}
.uc .ucd{position:absolute;left:-40px;top:-80px;width:280px;height:200px;pointer-events:none;z-index:3;font-style:normal}
.uc .ucd svg{display:block;width:280px;height:200px;overflow:visible}
.uc .uclt{animation:ucLt 2s ease-in-out infinite}
@keyframes ucLt{0%,100%{opacity:.35}50%{opacity:1}}
.uc .uctw{transform-box:fill-box;transform-origin:50% 50%;animation:ucTwk 2.6s ease-in-out infinite}
@keyframes ucTwk{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1.05) rotate(20deg)}}
.uc .ucpl{animation:ucPl 3.2s ease-in-out infinite alternate}
@keyframes ucPl{from{transform:translate(0,-4px) rotate(-8deg)}to{transform:translate(0,4px) rotate(8deg)}}
.pshadow.uc{width:200px}
.tap.uc{font-family:"Tsukimi Rounded",sans-serif;font-weight:700;color:#BFE6FF;letter-spacing:.12em;text-shadow:0 2px 0 #26305A,0 0 10px rgba(143,211,255,.7)}
.pressed.uc{border-radius:50px;background:#9AA4C2;box-shadow:0 0 0 4px #8FD3FF,0 7px 0 4px #3E4868;animation-name:ucPress,fxH}
@keyframes ucPress{0%{transform:scale(1)}22%{transform:scale(1.1,.82)}45%{transform:scale(.96,1.08)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.uc .uclt,.uc .uctw,.uc .ucpl{animation:none}.clips.uc{display:none}}
''' + fly_css('uc', 'rgba(143,211,255,.9)', PIECES)

PUSH = dict(code='uc', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
