"""壁紙パック ⑨スチームパンク（まさちゃんの 指定「歯車で動く機械仕掛けの馬。蒸気がしゅっ」）
   上の絵：夕ぐれの 工場の 町（工場・えんとつ・時計台・ガスタンク）・飛行船・石だたみの 道。左上と 右上に 大きな 歯車。
     まん中を 真ちゅうの 機械の 馬が 速足で 走る：ボイラーの 胴（びょう・銅の 帯・のぞき窓の 中で 歯車が 回る・圧力計）・えんとつ・
     板を 重ねた 首と 頭（こはく色の ランプの 目）・銅の ひれの たてがみ・銅線の しっぽ。肩と 腰の 大きな 歯車が 回って、
     機関車の 動輪のように 連結棒が 回り、足（ひざに 小さな 歯車・鉄の すね・鉄の ひづめ）が 動く。
   動き（CSS だけ・1回り 0.84秒の 速足）：足は ひづめが 地面に つく 間は 道と 同じ 速さで うしろへ（すべらない）・宙では ひざを まげて 前へ。
     歯車が 回る・連結棒が 円を えがく・頭が うなずく・しっぽが ゆれる・体が 少し 上下。道と 町が 流れる（遠いほど ゆっくり）・飛行船が ゆっくり 横切る。
     えんとつから 蒸気が 「しゅっ しゅっ」（3.6秒ごとに 3つ）・鼻から 「しゅっ」（7.2秒ごと）。強く 光らせない"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'steam'
CODE = 'gw'

# ---------------------------------------------------------------- 色
BR = dict(hl='#FFE7A6', l='#E9C46A', m='#C99A3E', d='#94692A', dd='#5E4019')      # 真ちゅう
CU = dict(hl='#F6C29A', l='#D98A58', m='#B5683A', d='#80441F', dd='#4E2810')      # 銅
FE = dict(l='#7A7672', m='#4E4A48', d='#2E2B2A', dd='#1A1817')                   # 鉄
FAR = 0.38          # 奥の 足を 暗く する 量

# ---------------------------------------------------------------- 馬の 形（舞台の 座標・右向き）
T = 0.84            # 速足の 1回り（秒）
NS = 24             # 1回りを 何コマで 書くか（あいだは なめらかに つなぐ）
GROUND = 146        # ひづめの 下
SH = (238, 92)      # 肩の 軸
HP = (164, 90)      # 腰の 軸
L1, L2 = 29.0, 29.0
STRIDE = 28.0       # ひづめが 地面に ついて いる 間に うしろへ 進む 長さ
LIFT = 10.0         # 宙で ひづめを 上げる 高さ
SPEED = STRIDE / (T / 2)          # 道の 速さ（px／秒）＝ひづめが うしろへ 進む 速さ
ROAD_W = 120
BOB = 1.2
CRANK = 7.5         # 肩と 腰の 歯車の クランクの 半径
OFFS = dict(fl=0.0, hr=0.0, fr=0.5, hl=0.5)      # 速足：ななめの 足が いっしょ


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * u)


def bob(t):
    """体の 上下（1回りに 2回・宙の 足が いちばん 上の とき 少し 高い）"""
    return -BOB * math.cos(4 * math.pi * t) * 0.5 - BOB * 0.5


def hoof_target(q, y0):
    """足の 位相 q の ひづめの 場所（軸から の ずれ・前が +x・下が +y）"""
    if q < 0.5:
        u = q / 0.5
        return STRIDE / 2 - STRIDE * u, y0
    u = (q - 0.5) / 0.5
    return -STRIDE / 2 + STRIDE * ease(u), y0 - LIFT * math.sin(math.pi * u) ** 1.2


def ik(x, y, knee_fwd):
    """2つの 骨（L1・L2）で 軸から (x, y) に ひづめを とどかせる 角度（たてから 前へ ＋・度）：上の 骨・下の 骨（どちらも 画面での 向き）"""
    d = math.hypot(x, y)
    d = min(d, L1 + L2 - 0.01)
    a = math.atan2(x, y)
    c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    b = math.acos(max(-1.0, min(1.0, c)))
    a1 = a + b if knee_fwd else a - b
    kx, ky = L1 * math.sin(a1), L1 * math.cos(a1)
    a2 = math.atan2(x - kx, y - ky)
    return math.degrees(a1), math.degrees(a2)


def leg_keys(name):
    """足の 上の 骨の 角度・下の 骨の 角度（上の 骨から の 差）の コマ（NS+1 こ）。CSS の rotate は 前へ ＝ マイナス"""
    front = name[0] == 'f'
    piv = SH if front else HP
    up, lo = [], []
    for i in range(NS + 1):
        t = i / NS
        q = (t + OFFS[name]) % 1.0
        y0 = GROUND - (piv[1] + bob(t))
        x, y = hoof_target(q, y0)
        a1, a2 = ik(x, y, knee_fwd=front)
        up.append(-a1)
        lo.append(-(a2 - a1))
    # 角度の つなぎ目（-180〜180 の とび）を なくす
    for arr in (up, lo):
        for i in range(1, len(arr)):
            while arr[i] - arr[i - 1] > 180:
                arr[i] -= 360
            while arr[i] - arr[i - 1] < -180:
                arr[i] += 360
    return up, lo


# ---------------------------------------------------------------- 部品の 絵
def gear_d(cx, cy, ro, ri, n, tw=0.5, round_=0.0):
    """歯車の 外がわ（n 枚の 歯：外の 半径 ro・歯の 根もとの 半径 ri・歯の はば tw）"""
    pts = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        step = 2 * math.pi / n
        w = step * tw
        for a, r in ((a0 - w * 0.5, ri), (a0 - w * 0.32, ro), (a0 + w * 0.32, ro), (a0 + w * 0.5, ri)):
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return P(pts)


def gear_svg(r, n, c=BR, spokes=5, hole=0.22, rim=0.72, size=None, shade=True):
    """歯車 1つ（中心は 絵の まん中）：歯・ふち・スポーク（spokes 本・0＝板）・軸の 穴"""
    s = size or (2 * r + 4)
    cx = cy = s / 2
    ri = r * 0.84
    o = f"<path d='{gear_d(cx, cy, r, ri, n)}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='{f(max(0.6, r * 0.04))}' stroke-linejoin='round'/>"
    if spokes:
        rr = ri * rim
        o += f"<circle cx='{f(cx)}' cy='{f(cy)}' r='{f(rr)}' fill='{c['dd']}' opacity='.85'/>"
        for k in range(spokes):
            a = 2 * math.pi * k / spokes
            x2, y2 = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            o += f"<path d='M{f(cx)} {f(cy)} L{f(x2)} {f(y2)}' stroke='{c['m']}' stroke-width='{f(r * 0.17)}' stroke-linecap='round'/>"
    else:
        o += f"<circle cx='{f(cx)}' cy='{f(cy)}' r='{f(ri * 0.78)}' fill='none' stroke='{c['d']}' stroke-width='{f(r * 0.06)}'/>"
    o += f"<circle cx='{f(cx)}' cy='{f(cy)}' r='{f(ri * 0.98)}' fill='none' stroke='{c['l']}' stroke-width='{f(max(0.6, r * 0.05))}' opacity='.8'/>"
    if shade:
        o += (f"<path d='M{f(cx - ri * 0.9)} {f(cy - ri * 0.2)} A{f(ri * 0.92)} {f(ri * 0.92)} 0 0 1 {f(cx + ri * 0.2)} {f(cy - ri * 0.9)}' fill='none' "
              f"stroke='{c['hl']}' stroke-width='{f(max(0.7, r * 0.07))}' stroke-linecap='round' opacity='.7'/>")
    o += (f"<circle cx='{f(cx)}' cy='{f(cy)}' r='{f(r * hole)}' fill='{c['l']}' stroke='{c['dd']}' stroke-width='{f(max(0.5, r * 0.04))}'/>"
          f"<circle cx='{f(cx)}' cy='{f(cy)}' r='{f(r * hole * 0.42)}' fill='{c['dd']}'/>")
    return doc(s, s, o)


def dark(c, k=FAR):
    return {kk: mix(v, '#1E1410', k) for kk, v in c.items()}


def upper_svg(front, far=False):
    """足の 上の 骨（真ちゅうの 板）：軸（上の まん中・絵の (12, 4)）から 下へ L1。ひざに 小さな 輪"""
    c = dark(BR) if far else BR
    w0, w1 = (15, 9) if front else (17, 10)
    x = 12
    o = (f"<path d='M{f(x - w0 / 2)} 4 Q{f(x)} -2 {f(x + w0 / 2)} 4 L{f(x + w1 / 2)} {f(4 + L1)} Q{f(x)} {f(8 + L1)} {f(x - w1 / 2)} {f(4 + L1)} Z' "
         f"fill='{c['m']}' stroke='{c['dd']}' stroke-width='1' stroke-linejoin='round'/>"
         f"<path d='M{f(x - w0 / 2 + 2)} 6 L{f(x - w1 / 2 + 1.6)} {f(2 + L1)}' stroke='{c['hl']}' stroke-width='1.4' stroke-linecap='round' opacity='.75'/>"
         f"<path d='M{f(x + w0 / 2 - 1.6)} 7 L{f(x + w1 / 2 - 1.4)} {f(2 + L1)}' stroke='{c['d']}' stroke-width='1.2' stroke-linecap='round' opacity='.8'/>")
    for k in range(3):
        yy = 10 + k * 7
        o += f"<circle cx='{x}' cy='{yy}' r='.9' fill='{c['dd']}'/>"
    o += f"<rect x='{f(x - w0 / 2 + 1)}' y='{f(4 + L1 * 0.55)}' width='{f(w0 - 2 - (w0 - w1) * 0.55)}' height='2.4' rx='.8' fill='{(dark(CU) if far else CU)['m']}'/>"
    return doc(24, 12 + L1, o)


def lower_svg(front, far=False):
    """足の 下の 骨（鉄の すね・まん中に 真ちゅうの 輪）と 鉄の ひづめ：ひざ（絵の (10, 3)）から 下へ L2"""
    c = dark(FE, 0.2) if far else FE
    b = dark(BR) if far else BR
    x = 10
    o = (f"<rect x='{x - 3}' y='2' width='6' height='{f(L2 - 6)}' rx='2.4' fill='{c['m']}' stroke='{c['dd']}' stroke-width='.8'/>"
         f"<rect x='{x - 2.2}' y='3' width='1.4' height='{f(L2 - 9)}' rx='.7' fill='{c['l']}' opacity='.8'/>"
         f"<rect x='{x - 4}' y='{f(L2 * 0.42)}' width='8' height='4' rx='1.4' fill='{b['m']}' stroke='{b['dd']}' stroke-width='.7'/>")
    # ひづめ（前が 少し 長い・底に 蹄鉄の 帯）
    hy = 3 + L2 - 6
    o += (f"<path d='M{x - 5} {f(hy)} H{x + 4.2} L{x + 6.6} {f(hy + 6.4)} H{x - 5.8} Z' fill='{c['d']}' stroke='{c['dd']}' stroke-width='.8' stroke-linejoin='round'/>"
          f"<rect x='{x - 6}' y='{f(hy + 5.2)}' width='12.8' height='1.8' rx='.6' fill='{b['d']}'/>"
          f"<path d='M{x - 4} {f(hy + 1.2)} H{x + 3}' stroke='{c['l']}' stroke-width='.9' opacity='.6'/>")
    return doc(20, 6 + L2, o)


def body_svg():
    """胴（ボイラー）・えんとつ・首・のぞき窓の 中の 暗い 所・圧力計の 盤・しっぽの 根もと（絵は 舞台の 座標）"""
    o = ''
    # 首（板を 重ねた 柱：胴の 前から 頭へ）
    neck = [(234, 74), (246, 64), (265, 44), (279, 34), (289, 44), (262, 70), (252, 84)]
    o += f"<path d='{smooth(neck, True, 0.35)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
    for k in range(5):
        t = k / 5
        ax, ay = 246 + (279 - 246) * t, 64 + (34 - 64) * t
        bx, by = 252 + (289 - 252) * t, 84 + (44 - 84) * t
        o += f"<path d='M{f(ax - 1)} {f(ay)} Q{f((ax + bx) / 2 + 3)} {f((ay + by) / 2 + 2)} {f(bx)} {f(by)}' fill='none' stroke='{BR['dd']}' stroke-width='.9' opacity='.75'/>"
        o += f"<circle cx='{f((ax + bx) / 2 + 1)}' cy='{f((ay + by) / 2 + 1)}' r='.9' fill='{BR['dd']}'/>"
    o += f"<path d='M249 66 L268 46' stroke='{BR['hl']}' stroke-width='1.6' stroke-linecap='round' opacity='.7'/>"
    # 胴（ボイラー）
    o += (f"<rect x='150' y='62' width='104' height='40' rx='19' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.3'/>"
          f"<rect x='153' y='65' width='98' height='9' rx='4.5' fill='{BR['l']}' opacity='.9'/>"
          f"<rect x='158' y='66' width='70' height='2.6' rx='1.3' fill='{BR['hl']}' opacity='.8'/>"
          f"<rect x='152' y='90' width='100' height='10' rx='5' fill='{BR['d']}' opacity='.6'/>")
    for x in (172, 206, 236):                                           # 銅の 帯
        o += (f"<rect x='{x - 3.2}' y='62.4' width='6.4' height='39.2' rx='1.6' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.7'/>"
              f"<rect x='{x - 2.2}' y='63' width='1.6' height='38' fill='{CU['hl']}' opacity='.55'/>")
        for yy in (67, 75, 83, 91, 98):
            o += f"<circle cx='{x}' cy='{yy}' r='.85' fill='{CU['dd']}'/>"
    for k in range(13):                                                 # びょう（上と 下の ふち）
        x = 160 + k * 7.4
        o += f"<circle cx='{f(x)}' cy='64.6' r='.8' fill='{BR['dd']}'/><circle cx='{f(x)}' cy='99.6' r='.8' fill='{BR['dd']}'/>"
    # のぞき窓（中の 暗い 所。歯車と ガラスの ふちは 別の 部品）
    o += f"<circle cx='196' cy='83' r='12.5' fill='{FE['dd']}'/>"
    # 圧力計の 盤（針は 別の 部品）
    o += (f"<circle cx='222' cy='84' r='7.2' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='1'/><circle cx='222' cy='84' r='5.6' fill='#F4E9CF'/>")
    for k in range(7):
        a = math.radians(150 + k * 40)
        o += f"<path d='M{f(222 + math.cos(a) * 4.2)} {f(84 + math.sin(a) * 4.2)} L{f(222 + math.cos(a) * 5.2)} {f(84 + math.sin(a) * 5.2)}' stroke='#5A4A3A' stroke-width='.7'/>"
    o += f"<path d='M{f(222 + math.cos(math.radians(30)) * 4.4)} {f(84 + math.sin(math.radians(30)) * 4.4)} A4.4 4.4 0 0 0 {f(222 + math.cos(math.radians(-20)) * 4.4)} {f(84 + math.sin(math.radians(-20)) * 4.4)}' fill='none' stroke='#C8322A' stroke-width='1.1'/>"
    # えんとつ（胴の 上・き甲の 少し うしろ）
    o += (f"<path d='M214 64 L216 46 H226 L228 64 Z' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='1'/>"
          f"<path d='M217 47 L216 63' stroke='{CU['hl']}' stroke-width='1.2' opacity='.7'/>"
          f"<rect x='212.5' y='41' width='17' height='6' rx='1.6' fill='{FE['m']}' stroke='{FE['dd']}' stroke-width='.9'/>"
          f"<rect x='213.5' y='41.6' width='15' height='1.6' rx='.8' fill='{FE['l']}'/>"
          f"<rect x='214' y='54' width='14' height='2.6' fill='{BR['d']}'/>")
    # 鞍の かわりの 銅の 座（き甲の うしろ）と 番号板の かわりの 歯車の しるし
    o += (f"<path d='M186 62.6 Q198 56 210 62.6 Z' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.9'/>")
    # しっぽの 根もと
    o += f"<circle cx='152' cy='72' r='3.4' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.8'/>"
    return doc(W, H, o)


def head_svg():
    """頭（板を 重ねた 馬の 顔・こはく色の ランプの 目・耳・鼻の 穴の すきま・はみの 輪）：うなずく 軸は 絵の (14, 22)＝舞台の (282, 34)"""
    ox, oy = 268, 12       # 絵の 左上（舞台の 座標）
    tr = lambda x, y: (x - ox, y - oy)
    face = [tr(*p) for p in ((278, 30), (283, 20), (292, 17), (304, 26), (318, 42), (318, 49), (311, 53), (300, 52), (290, 48), (281, 41))]
    o = f"<path d='{smooth(face, True, 0.3)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
    o += f"<path d='{P([tr(285, 22), tr(293, 19), tr(306, 30), tr(296, 30)])}' fill='{BR['l']}' opacity='.85'/>"
    o += f"<path d='{P([tr(306, 31), tr(317, 43), tr(317, 48), tr(304, 40)])}' fill='{BR['d']}' opacity='.55'/>"
    for a, b in (((294, 22), (290, 46)), ((304, 30), (300, 51))):    # 板の つなぎ目
        o += f"<path d='M{f(tr(*a)[0])} {f(tr(*a)[1])} L{f(tr(*b)[0])} {f(tr(*b)[1])}' stroke='{BR['dd']}' stroke-width='.8' opacity='.7'/>"
    for p in ((292, 25), (297, 33), (302, 40), (295, 44)):
        x, y = tr(*p)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.8' fill='{BR['dd']}'/>"
    # 耳（2まい）
    for ex, ey, c in ((283, 21, BR['d']), (288, 18, BR['m'])):
        x, y = tr(ex, ey)
        o += f"<path d='M{f(x - 3)} {f(y + 2)} L{f(x - 1.6)} {f(y - 10)} L{f(x + 3.4)} {f(y + 1.2)} Z' fill='{c}' stroke='{BR['dd']}' stroke-width='.9' stroke-linejoin='round'/>"
    # 銅の 鼻の 先・鼻の 穴の すきま
    x, y = tr(313, 45)
    o += (f"<path d='M{f(x - 4)} {f(y - 6)} L{f(x + 5)} {f(y - 3)} L{f(x + 5)} {f(y + 4)} L{f(x - 2)} {f(y + 7)} Z' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.8'/>"
          f"<path d='M{f(x)} {f(y - 2)} h3 M{f(x - 0.4)} {f(y + 0.6)} h3.4 M{f(x - 0.8)} {f(y + 3.2)} h3' stroke='{CU['dd']}' stroke-width='.9' stroke-linecap='round'/>")
    # 目（こはく色の ランプ・まわりに やわらかい 光の 輪）
    x, y = tr(296, 28)
    o += (f"<circle cx='{f(x)}' cy='{f(y)}' r='6.2' fill='#FFB648' opacity='.22'/>"
          f"<circle cx='{f(x)}' cy='{f(y)}' r='3.9' fill='{BR['dd']}'/><circle cx='{f(x)}' cy='{f(y)}' r='2.8' fill='#FFB648'/>"
          f"<circle cx='{f(x - 0.8)}' cy='{f(y - 0.9)}' r='1' fill='#FFF0C8'/>")
    # はみの 輪と 手綱の かわりの 鎖
    x, y = tr(303, 49)
    o += f"<circle cx='{f(x)}' cy='{f(y)}' r='2.6' fill='none' stroke='{CU['l']}' stroke-width='1.2'/>"
    return doc(56, 48, o)


def mane_svg():
    """たてがみ：首の 上の ふちに ならぶ 銅の ひれ（うしろへ ねる）"""
    o = ''
    for k in range(6):
        t = k / 6
        x, y = 265 - (265 - 240) * t, 42 + (64 - 42) * t
        o += (f"<path d='M{f(x)} {f(y)} Q{f(x - 6)} {f(y - 9)} {f(x - 13)} {f(y - 7)} Q{f(x - 7)} {f(y - 2)} {f(x - 4)} {f(y + 5)} Z' "
              f"fill='{CU['m'] if k % 2 else CU['l']}' stroke='{CU['dd']}' stroke-width='.8' stroke-linejoin='round'/>")
    return doc(W, H, o)


def tail_svg():
    """しっぽ（銅線の たば 3本）：根もとは 絵の (26, 4)＝舞台の (152, 72)"""
    o = ''
    for k, (c, dx, dy, w) in enumerate(((CU['d'], -24, 30, 2.4), (CU['m'], -20, 34, 2.6), (CU['l'], -15, 36, 2.2))):
        o += f"<path d='M26 4 C{f(26 - 10)} {f(6 + k)} {f(26 + dx * 0.8)} {f(dy * 0.5)} {f(26 + dx)} {f(dy)}' fill='none' stroke='{c}' stroke-width='{w}' stroke-linecap='round'/>"
        o += f"<circle cx='{f(26 + dx)}' cy='{f(dy)}' r='{f(w * 0.8)}' fill='{c}'/>"
    o += f"<path d='M26 4 C20 8 10 14 6 24' fill='none' stroke='{CU['hl']}' stroke-width='.8' opacity='.6'/>"
    return doc(34, 42, o)


def window_svg():
    """のぞき窓の ふち（真ちゅうの 輪・ボルト）と ガラスの 光（中の 歯車の 上に 重ねる）。中心は 絵の (15, 15)"""
    o = (f"<circle cx='15' cy='15' r='12.6' fill='none' stroke='{BR['d']}' stroke-width='3.2'/>"
         f"<circle cx='15' cy='15' r='12.6' fill='none' stroke='{BR['l']}' stroke-width='1.2' stroke-dasharray='9 6' opacity='.85'/>")
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        o += f"<circle cx='{f(15 + math.cos(a) * 12.6)}' cy='{f(15 + math.sin(a) * 12.6)}' r='.9' fill='{BR['dd']}'/>"
    o += ("<path d='M7 11 A9 9 0 0 1 14 6' fill='none' stroke='#FFFFFF' stroke-width='1.8' stroke-linecap='round' opacity='.45'/>"
          "<path d='M8.6 14 A7 7 0 0 1 10.6 10.4' fill='none' stroke='#FFFFFF' stroke-width='1.2' stroke-linecap='round' opacity='.3'/>")
    return doc(30, 30, o)


def needle_svg():
    """圧力計の 針（中心 (6, 6)・右上を さす）"""
    return doc(12, 12, f"<path d='M6 6 L9.8 3.2' stroke='#2A1A12' stroke-width='1' stroke-linecap='round'/><circle cx='6' cy='6' r='1.2' fill='{BR['dd']}'/>")


def rod_svg():
    """連結棒（肩の 歯車と 腰の 歯車の クランクを つなぐ 鉄の 棒）：左の はし＝絵の (4, 5)"""
    L = SH[0] - HP[0]
    dy = SH[1] - HP[1]
    o = (f"<path d='M4 5 L{f(4 + L)} {f(5 + dy)}' stroke='{FE['dd']}' stroke-width='5' stroke-linecap='round'/>"
         f"<path d='M4 5 L{f(4 + L)} {f(5 + dy)}' stroke='{FE['m']}' stroke-width='3.2' stroke-linecap='round'/>"
         f"<path d='M6 4 L{f(2 + L)} {f(4 + dy)}' stroke='{FE['l']}' stroke-width='.9' stroke-linecap='round' opacity='.8'/>")
    for x, y in ((4, 5), (4 + L, 5 + dy)):
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='3.1' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='.8'/><circle cx='{f(x)}' cy='{f(y)}' r='1.1' fill='{BR['dd']}'/>"
    return doc(L + 8, 10 + max(0, dy), o)


def puff_svg(seed=1, w=34, h=26, col='#FBF4E6', shade='#D9CDBA'):
    """蒸気の かたまり（白に 近い 色の 丸の 重なり・下に うすい かげ）"""
    R = rnd(seed)
    o = ''
    blobs = []
    for k in range(6):
        x = w * (0.22 + 0.56 * k / 5) + R.uniform(-2, 2)
        y = h * 0.55 + R.uniform(-4, 3) - math.sin(math.pi * k / 5) * 4
        r = R.uniform(5.2, 8.4) * (0.75 + 0.35 * math.sin(math.pi * k / 5))
        blobs.append((x, y, r))
    for x, y, r in blobs:
        o += f"<circle cx='{f(x)}' cy='{f(y + 1.6)}' r='{f(r)}' fill='{shade}'/>"
    for x, y, r in blobs:
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='{col}'/>"
    o += f"<circle cx='{f(blobs[2][0] - 2)}' cy='{f(blobs[2][1] - 3)}' r='{f(blobs[2][2] * 0.45)}' fill='#FFFFFF' opacity='.8'/>"
    return doc(w, h, o)


def jet_svg():
    """鼻から しゅっ と 出る 蒸気（右へ のびる 細長い 白）"""
    o = ("<path d='M2 9 C10 4 22 3 36 6 C46 8 54 6 62 9 C54 12 46 11 36 13 C22 15 10 14 2 9 Z' fill='#FBF4E6' opacity='.92'/>"
         "<circle cx='54' cy='9' r='6' fill='#FBF4E6' opacity='.85'/><circle cx='62' cy='7' r='5' fill='#FFFFFF' opacity='.7'/>"
         "<path d='M6 9 C16 7 28 7 40 8' stroke='#FFFFFF' stroke-width='1.6' fill='none' stroke-linecap='round' opacity='.8'/>")
    return doc(70, 18, o)


# ---------------------------------------------------------------- 背景
def sky_svg():
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#4A3A4E'/><stop offset='.38' stop-color='#8E6458'/>"
            "<stop offset='.72' stop-color='#D29A62'/><stop offset='1' stop-color='#F0CF96'/></linearGradient>"
            "<radialGradient id='g' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FFE8B0' stop-opacity='.75'/><stop offset='.4' stop-color='#FFD890' stop-opacity='.3'/>"
            "<stop offset='1' stop-color='#FFD890' stop-opacity='0'/></radialGradient>")
    o = (f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
         "<circle cx='300' cy='92' r='70' fill='url(#g)'/><circle cx='300' cy='92' r='17' fill='#FBE3AE' opacity='.85'/>")
    # 遠くの けむりの すじ（横に のびる うすい 雲）
    for y, x0, x1, op in ((26, -10, 160, .18), (40, 120, 330, .14), (16, 230, 400, .16)):
        o += f"<path d='M{x0} {y} C{x0 + 40} {y - 6} {x1 - 60} {y + 5} {x1} {y - 1}' fill='none' stroke='#F6DDB8' stroke-width='7' stroke-linecap='round' opacity='{op}'/>"
    return doc(W, H, o, defs=defs)


def skyline_svg(w=390, h=112, seed=4):
    """遠くの 工場の 町（くり返せる：はば w）：のこぎり屋根の 工場・えんとつと けむり・時計台・ガスタンク・あかりの 窓"""
    R = rnd(seed)
    base = '#6A5060'
    o = ''
    items = []
    x = -10
    kinds = ['fac', 'chim', 'tank', 'fac', 'tower', 'chim', 'fac', 'tank', 'chim', 'fac']
    k = 0
    while x < w:
        kind = kinds[k % len(kinds)]
        k += 1
        if kind == 'fac':
            fw = R.uniform(48, 70)
            items.append(('fac', x, fw, R.uniform(16, 24)))
            x += fw + R.uniform(2, 8)
        elif kind == 'chim':
            items.append(('chim', x + 4, R.uniform(5, 7), R.uniform(38, 52)))
            x += 14
        elif kind == 'tank':
            tw = R.uniform(26, 34)
            items.append(('tank', x, tw, R.uniform(20, 26)))
            x += tw + 6
        else:
            items.append(('tower', x + 6, 16, 64))
            x += 30
    win = []
    for kind, x0, ww, hh in items:
        for dx in (-w, 0, w):
            xx = x0 + dx
            if xx > w + 80 or xx + ww < -80:
                continue
            if kind == 'fac':
                n = max(2, int(ww // 12))
                pts = [(xx, h), (xx, h - hh)]
                for i in range(n):
                    a = xx + ww * i / n
                    b = xx + ww * (i + 1) / n
                    pts += [(a, h - hh), (b - 2, h - hh - 8), (b, h - hh)]
                pts += [(xx + ww, h)]
                o += f"<path d='{P(pts)}' fill='{base}'/>"
                for i in range(int(ww // 9)):
                    if (i * 7 + int(x0)) % 3:
                        win.append((xx + 4 + i * 9, h - hh + 6))
            elif kind == 'chim':
                o += f"<rect x='{f(xx)}' y='{f(h - hh)}' width='{f(ww)}' height='{f(hh)}' fill='{base}'/><rect x='{f(xx - 1)}' y='{f(h - hh)}' width='{f(ww + 2)}' height='3' fill='#5A4252'/>"
                cx, cy = xx + ww / 2, h - hh - 2
                o += (f"<path d='M{f(cx)} {f(cy)} C{f(cx - 6)} {f(cy - 10)} {f(cx - 16)} {f(cy - 12)} {f(cx - 30)} {f(cy - 20)} C{f(cx - 40)} {f(cy - 25)} {f(cx - 56)} {f(cy - 24)} {f(cx - 70)} {f(cy - 30)}' "
                      f"fill='none' stroke='#E7D2B8' stroke-width='7' stroke-linecap='round' opacity='.22'/>")
            elif kind == 'tank':
                o += (f"<rect x='{f(xx)}' y='{f(h - hh)}' width='{f(ww)}' height='{f(hh)}' rx='2' fill='#5E4656'/>"
                      f"<ellipse cx='{f(xx + ww / 2)}' cy='{f(h - hh)}' rx='{f(ww / 2)}' ry='3' fill='#6E5666'/>")
                for i in range(1, 4):
                    o += f"<path d='M{f(xx)} {f(h - hh + hh * i / 4)} H{f(xx + ww)}' stroke='#4E3A48' stroke-width='.8'/>"
                for i in range(4):
                    o += f"<path d='M{f(xx + ww * i / 3)} {f(h - hh)} V{h}' stroke='#4E3A48' stroke-width='.7'/>"
            else:
                o += (f"<rect x='{f(xx)}' y='{f(h - hh)}' width='{f(ww)}' height='{f(hh)}' fill='{base}'/>"
                      f"<path d='M{f(xx - 2)} {f(h - hh)} L{f(xx + ww / 2)} {f(h - hh - 14)} L{f(xx + ww + 2)} {f(h - hh)} Z' fill='#5A4252'/>"
                      f"<circle cx='{f(xx + ww / 2)}' cy='{f(h - hh + 10)}' r='6' fill='#F2D9A0' opacity='.75'/>"
                      f"<circle cx='{f(xx + ww / 2)}' cy='{f(h - hh + 10)}' r='6' fill='none' stroke='#5A4252' stroke-width='1'/>"
                      f"<path d='M{f(xx + ww / 2)} {f(h - hh + 10)} V{f(h - hh + 6)} M{f(xx + ww / 2)} {f(h - hh + 10)} H{f(xx + ww / 2 + 3.6)}' stroke='#4A3442' stroke-width='1' stroke-linecap='round'/>")
                for i in range(4):
                    win.append((xx + ww / 2 - 1.2, h - hh + 24 + i * 9))
    for x, y in win:
        o += f"<rect x='{f(x)}' y='{f(y)}' width='2.6' height='3.4' fill='#F6C86E' opacity='.6'/>"
    return doc(w, h, o)


def mid_svg(w=195, h=60):
    """近くの 町なみ（くり返せる：はば w）：ひくい 石の へい（真ちゅうの 手すり）と ガス灯。馬の 足の うしろが 見やすい ように ひくく"""
    R = rnd(13)
    o = ''
    y0 = h - 13
    o += f"<rect x='0' y='{y0}' width='{w}' height='13' fill='#5A4646'/>"
    x = -4
    for j in range(2):
        yy = y0 + 1 + j * 6
        x = -R.uniform(0, 8) - j * 9
        while x < w:
            bw = R.uniform(15, 22)
            c = mix('#6E5858', '#5E4A4A', R.random())
            for dx in ((0, -w) if x + bw > w else (0, w) if x < 0 else (0,)):
                o += f"<rect x='{f(x + dx + 0.6)}' y='{f(yy)}' width='{f(bw - 1.2)}' height='5' rx='1' fill='{c}'/>"
            x += bw
    o += (f"<rect x='0' y='{y0 - 3}' width='{w}' height='3.4' fill='{BR['d']}'/><rect x='0' y='{y0 - 3}' width='{w}' height='1.2' fill='{BR['l']}' opacity='.8'/>")
    for xx in (30, 128):
        o += f"<rect x='{xx - 2}' y='{y0 - 7}' width='4' height='7' fill='{BR['d']}'/><circle cx='{xx}' cy='{y0 - 8}' r='2.4' fill='{BR['m']}'/>"
    # ガス灯
    x = 80
    o += (f"<rect x='{x - 1.5}' y='6' width='3' height='{y0 - 6}' fill='#2E2420'/><rect x='{x - 3.5}' y='{y0 - 6}' width='7' height='6' fill='#2E2420'/>"
          f"<path d='M{x - 6} 6 H{x + 6} L{x + 4} 16 H{x - 4} Z' fill='#3A2E28'/>"
          f"<rect x='{x - 3.4}' y='8' width='6.8' height='7' fill='#FFD58A' opacity='.9'/>"
          f"<circle cx='{x}' cy='11' r='13' fill='#FFD58A' opacity='.15'/><circle cx='{x}' cy='11' r='7' fill='#FFE2A6' opacity='.2'/>"
          f"<path d='M{x - 7} 6 L{x} 2 L{x + 7} 6 Z' fill='#2E2420'/>")
    return doc(w, h, o)


def road_svg(w=ROAD_W, h=22):
    """石だたみの 道（くり返せる：はば w）：上に 真ちゅうの へり"""
    R = rnd(9)
    o = f"<rect width='{w}' height='{h}' fill='#5E4E48'/>"
    rows = [(4, 6), (10, 6), (16, 6)]
    for j, (y, hh) in enumerate(rows):
        x = -R.uniform(0, 10) - (j % 2) * 7
        while x < w:
            sw = R.uniform(11, 16)
            c = mix('#7E6E64', '#6E6058', R.random())
            for dx in (0, w):
                if x + dx < w + 20:
                    o += (f"<rect x='{f(x + dx + 0.6)}' y='{f(y + 0.6)}' width='{f(sw - 1.2)}' height='{f(hh - 1.2)}' rx='2.2' fill='{c}'/>"
                          f"<rect x='{f(x + dx + 1.4)}' y='{f(y + 1)}' width='{f(sw - 3.4)}' height='1.3' rx='.6' fill='#A89888' opacity='.35'/>")
            x += sw
    o += (f"<rect width='{w}' height='4' fill='{BR['d']}'/><rect width='{w}' height='1.4' fill='{BR['l']}'/>")
    for i in range(4):
        o += f"<circle cx='{f(i * w / 4 + 8)}' cy='2.4' r='.9' fill='{BR['dd']}'/>"
    return doc(w, h, o)


def airship_svg():
    """飛行船（右から 左へ ゆっくり。プロペラは 別の 部品で 回す）：左向き"""
    o = ("<ellipse cx='40' cy='14' rx='34' ry='11' fill='#9C6A52'/><ellipse cx='40' cy='11' rx='31' ry='7' fill='#B88466'/>"
         "<path d='M10 14 Q40 20 72 14' fill='none' stroke='#6E4636' stroke-width='1'/>")
    for x in (24, 40, 56):
        o += f"<path d='M{x} 3.4 Q{x - 2} 14 {x} 24.6' fill='none' stroke='#6E4636' stroke-width='.8' opacity='.8'/>"
    o += ("<path d='M68 9 L80 3 L78 14 L80 25 L68 19 Z' fill='#7A5040'/>"
          "<rect x='30' y='25' width='22' height='6' rx='2' fill='#4A3A34'/><path d='M34 24 L32 25 M48 24 L50 25' stroke='#4A3A34' stroke-width='.8'/>"
          "<rect x='33' y='26.4' width='3' height='2.2' fill='#F6C86E' opacity='.8'/><rect x='39' y='26.4' width='3' height='2.2' fill='#F6C86E' opacity='.8'/><rect x='45' y='26.4' width='3' height='2.2' fill='#F6C86E' opacity='.8'/>")
    return doc(84, 34, o)


def prop_svg():
    return doc(10, 14, "<ellipse cx='5' cy='7' rx='1.6' ry='6.4' fill='#3A2E28' opacity='.85'/><circle cx='5' cy='7' r='1.3' fill='#C99A3E'/>")


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
LEGS = ('hr', 'fr', 'hl', 'fl')        # 描く 順（奥 → 手前）


def banner(B):
    still = B.get('still')
    alt = ('夕ぐれの工場の町の石だたみを、真ちゅうと銅でできた機械仕掛けの馬が速足で走るイラスト。肩と腰の大きな歯車が回って連結棒が回り、'
           '足が動く。のぞき窓の中でも歯車が回り、えんとつと鼻から蒸気がしゅっと出る。空に飛行船、左上と右上に大きな歯車')
    html = f'<div class="gww" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('gwSky', sky_svg())
    html += f'<i class="gwFar" style="background-image:url(&quot;{durl(skyline_svg())}&quot;)"></i>'
    html += '<i class="gwAir">' + img('gwAs', airship_svg()) + img('gwPr', prop_svg()) + '</i>'
    html += f'<i class="gwMid" style="background-image:url(&quot;{durl(mid_svg())}&quot;)"></i>'
    html += img('gwG1', gear_svg(46, 22, BR, spokes=6)) + img('gwG2', gear_svg(30, 15, CU, spokes=5)) + img('gwG3', gear_svg(20, 11, BR, spokes=0))
    html += f'<i class="gwRd" style="background-image:url(&quot;{durl(road_svg())}&quot;)"></i>'
    html += '<i class="gwSh"></i>'
    # 馬（体ごと 少し 上下）
    h = '<i class="gwH">'
    for nm in ('hr', 'fr'):
        h += f'<i class="gwL {nm}">' + img('u', upper_svg(nm[0] == 'f', True)) + '<i class="k">' + img('l', lower_svg(nm[0] == 'f', True)) + '</i></i>'
    h += img('gwTl', tail_svg()) + img('gwBd', body_svg()) + img('gwMn', mane_svg())
    h += '<i class="gwWn">' + img('gwWg1', gear_svg(9, 10, BR, spokes=4, size=22)) + img('gwWg2', gear_svg(6, 8, CU, spokes=0, size=16)) + img('gwWg3', gear_svg(5, 7, BR, spokes=0, size=14)) + '</i>'
    h += img('gwWr', window_svg()) + img('gwNd', needle_svg()) + img('gwHd', head_svg())
    for nm in ('hl', 'fl'):
        kg = img('kg', gear_svg(5.2, 8, BR, spokes=0, size=14))
        h += f'<i class="gwL {nm}">' + img('u', upper_svg(nm[0] == 'f')) + '<i class="k">' + img('l', lower_svg(nm[0] == 'f')) + kg + '</i></i>'
    h += img('gwDh', gear_svg(13, 12, BR, spokes=5, size=30)) + img('gwDs', gear_svg(13, 12, BR, spokes=5, size=30))
    h += img('gwRod', rod_svg())
    h += '</i>'
    html += h
    # 蒸気
    for k in range(3):
        html += img(f'gwPf p{k}', puff_svg(3 + k))
    html += img('gwJt', jet_svg())
    html += '</div>'

    # ---- CSS
    sky_uri = durl(skyline_svg())
    css = ('.gww{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#8E6458}'
           '.gww img,.gww i{position:absolute;display:block}'
           '.gww .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.gww .gwSky{left:0;top:0;width:390px;height:160px}'
           '.gww .gwFar{left:0;top:30px;width:782px;height:112px;background-size:390px 112px;background-repeat:repeat-x;animation:gwFar 64s linear infinite;will-change:transform}'
           '.gww .gwMid{left:0;top:82px;width:590px;height:60px;background-size:195px 60px;background-repeat:repeat-x;animation:gwMid 4.4s linear infinite;will-change:transform}'
           f'.gww .gwRd{{left:0;top:140px;width:{390 + ROAD_W}px;height:22px;background-size:{ROAD_W}px 22px;background-repeat:repeat-x;animation:gwRoad {f(ROAD_W / SPEED, 4)}s linear infinite;will-change:transform}}'
           '.gww .gwSh{left:150px;top:143px;width:118px;height:9px;border-radius:50%;background:radial-gradient(closest-side,rgba(30,18,10,.45),rgba(30,18,10,0))}'
           '.gww .gwAir{left:0;top:6px;width:84px;height:34px;animation:gwAir 46s linear infinite;will-change:transform}'
           '.gww .gwAs{left:0;top:0;width:84px;height:34px}'
           '.gww .gwPr{left:78px;top:7px;width:10px;height:14px;animation:gwProp .5s linear infinite}'
           '.gww .gwG1{left:-56px;top:-58px;width:96px;height:96px;animation:gwRot 24s linear infinite}'
           '.gww .gwG2{left:28px;top:-26px;width:64px;height:64px;animation:gwRotR 16.36s linear infinite}'
           '.gww .gwG3{left:356px;top:-14px;width:44px;height:44px;animation:gwRotR 12s linear infinite}'
           # 馬
           '.gww .gwH{left:0;top:0;width:390px;height:160px;animation:gwBob ' + f(T) + 's linear infinite;will-change:transform}'
           '.gww .gwBd,.gww .gwMn{left:0;top:0;width:390px;height:160px}'
           '.gww .gwTl{left:126px;top:68px;width:34px;height:42px;transform-origin:26px 4px;animation:gwTail ' + f(T) + 's ease-in-out infinite}'
           '.gww .gwHd{left:265px;top:16px;width:56px;height:48px;transform-origin:14px 22px;animation:gwHead ' + f(T) + 's ease-in-out infinite}'
           '.gww .gwWn{left:183.5px;top:70.5px;width:25px;height:25px;border-radius:50%;overflow:hidden}'
           '.gww .gwWg1{left:-1px;top:-2px;width:22px;height:22px;animation:gwRot ' + f(T * 2) + 's linear infinite}'
           '.gww .gwWg2{left:13px;top:10px;width:16px;height:16px;animation:gwRotR ' + f(T * 2 * 8 / 10) + 's linear infinite}'
           '.gww .gwWg3{left:2px;top:14px;width:14px;height:14px;animation:gwRotR ' + f(T * 2 * 7 / 10) + 's linear infinite}'
           '.gww .gwWr{left:181px;top:68px;width:30px;height:30px}'
           '.gww .gwNd{left:216px;top:78px;width:12px;height:12px;animation:gwNeedle 2.6s ease-in-out infinite}'
           '.gww .gwDh{left:' + f(HP[0] - 15) + 'px;top:' + f(HP[1] - 15) + 'px;width:30px;height:30px;animation:gwRot ' + f(T) + 's linear infinite}'
           '.gww .gwDs{left:' + f(SH[0] - 15) + 'px;top:' + f(SH[1] - 15) + 'px;width:30px;height:30px;animation:gwRot ' + f(T) + 's linear infinite}'
           '.gww .gwRod{left:' + f(HP[0] - 4) + 'px;top:' + f(HP[1] - 5) + 'px;width:' + f(SH[0] - HP[0] + 8) + 'px;height:' + f(10 + max(0, SH[1] - HP[1])) + 'px;animation:gwRod ' + f(T) + 's linear infinite}'
           # 足：軸の 所に はば 0 の 入れもの（上の 骨を 回す）→ ひざの 入れもの（下の 骨を 回す）
           '.gww .gwL{width:0;height:0;transform-origin:0 0}'
           '.gww .gwL .u{left:-12px;top:-4px;width:24px;height:' + f(12 + L1) + 'px}'
           '.gww .gwL .k{left:0;top:' + f(L1) + 'px;width:0;height:0;transform-origin:0 0}'
           '.gww .gwL .l{left:-10px;top:-3px;width:20px;height:' + f(6 + L2) + 'px}'
           '.gww .gwL .kg{left:-7px;top:-7px;width:14px;height:14px;animation:gwRotR ' + f(T / 2) + 's linear infinite}'
           # 蒸気
           '.gww .gwPf{left:204px;top:20px;width:34px;height:26px;opacity:0;transform-origin:50% 80%;animation:gwPuff 3.6s ease-out infinite;will-change:transform,opacity}'
           '.gww .gwPf.p1{animation-delay:.28s}.gww .gwPf.p2{animation-delay:.56s}'
           '.gww .gwJt{left:315px;top:42px;width:70px;height:18px;opacity:0;transform-origin:0 50%;animation:gwJet 7.2s ease-out 1.8s infinite;will-change:transform,opacity}')
    for nm in LEGS:
        piv = SH if nm[0] == 'f' else HP
        css += f'.gww .gwL.{nm}{{left:{f(piv[0])}px;top:{f(piv[1])}px;animation:gwU{nm} {f(T)}s linear infinite}}'
        css += f'.gww .gwL.{nm} .k{{animation:gwK{nm} {f(T)}s linear infinite}}'
        up, lo = leg_keys(nm)
        css += kf(f'gwU{nm}', [(100 * i / NS, f'transform:rotate({f(a, 2)}deg)') for i, a in enumerate(up)])
        css += kf(f'gwK{nm}', [(100 * i / NS, f'transform:rotate({f(a, 2)}deg)') for i, a in enumerate(lo)])
    css += kf('gwBob', [(100 * i / NS, f'transform:translateY({f(bob(i / NS), 2)}px)') for i in range(NS + 1)])
    css += kf('gwRod', [(100 * i / NS, f'transform:translate({f(CRANK * math.cos(2 * math.pi * i / NS + math.pi), 2)}px,{f(CRANK * math.sin(2 * math.pi * i / NS + math.pi), 2)}px)') for i in range(NS + 1)])
    css += (kf('gwRot', [(0, 'transform:rotate(0)'), (100, 'transform:rotate(360deg)')])
            + kf('gwRotR', [(0, 'transform:rotate(0)'), (100, 'transform:rotate(-360deg)')])
            + kf('gwFar', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-390px)')])
            + kf('gwMid', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-195px)')])
            + kf('gwRoad', [(0, 'transform:translateX(0)'), (100, f'transform:translateX(-{ROAD_W}px)')])
            + kf('gwAir', [(0, 'transform:translate(400px,0)'), (50, 'transform:translate(150px,5px)'), (100, 'transform:translate(-100px,0)')])
            + kf('gwProp', [(0, 'transform:scaleY(1)'), (50, 'transform:scaleY(.2)'), (100, 'transform:scaleY(1)')])
            + kf('gwHead', [(0, 'transform:rotate(-2deg)'), (25, 'transform:rotate(2.2deg)'), (50, 'transform:rotate(-2deg)'), (75, 'transform:rotate(2.2deg)'), (100, 'transform:rotate(-2deg)')])
            + kf('gwTail', [(0, 'transform:rotate(-7deg)'), (50, 'transform:rotate(6deg)'), (100, 'transform:rotate(-7deg)')])
            + kf('gwNeedle', [(0, 'transform:rotate(-30deg)'), (40, 'transform:rotate(18deg)'), (55, 'transform:rotate(8deg)'), (70, 'transform:rotate(22deg)'), (100, 'transform:rotate(-30deg)')])
            # えんとつの 蒸気：1つ 1.6秒（3.6秒の うち 44%）。ふくらんで うしろ（左）上へ 流れて 消える
            + kf('gwPuff', [(0, 'opacity:0;transform:translate(0,2px) scale(.25)'), (4, 'opacity:.95;transform:translate(-2px,-3px) scale(.5)'),
                            (24, 'opacity:.7;transform:translate(-24px,-14px) scale(1.15)'), (44, 'opacity:0;transform:translate(-52px,-24px) scale(1.7)'),
                            (100, 'opacity:0;transform:translate(-52px,-24px) scale(1.7)')])
            # 鼻の 蒸気：しゅっ（0.2秒で のびて 0.8秒で 消える）
            + kf('gwJet', [(0, 'opacity:0;transform:scaleX(.1) translateY(0)'), (2.5, 'opacity:.95;transform:scaleX(1) translateY(1px)'),
                           (12, 'opacity:0;transform:scaleX(1.25) translateY(4px)'), (100, 'opacity:0;transform:scaleX(1.25) translateY(4px)')]))
    if still:
        css += reduced('.gww>*:not(.bnr)')
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_gears():
    """背景の もよう：うすい 歯車の りんかく と びょう（真ちゅうの 紙）"""
    o = (f"<path d='{gear_d(28, 30, 18, 15, 12)}' fill='none' stroke='#B8925A' stroke-width='1.1' opacity='.32'/>"
         f"<circle cx='28' cy='30' r='5' fill='none' stroke='#B8925A' stroke-width='1' opacity='.32'/>"
         f"<path d='{gear_d(98, 96, 12, 10, 9)}' fill='none' stroke='#B8925A' stroke-width='1' opacity='.28'/>"
         f"<circle cx='98' cy='96' r='3.4' fill='none' stroke='#B8925A' stroke-width='.9' opacity='.28'/>")
    for x, y in ((92, 22), (100, 22), (108, 22), (20, 112), (28, 112), (36, 112)):
        o += f"<circle cx='{x}' cy='{y}' r='1.3' fill='#B8925A' opacity='.3'/>"
    o += "<path d='M60 68 H130' stroke='#B8925A' stroke-width='1' stroke-dasharray='2 5' opacity='.25'/>"
    return tile(130, 130, o)


def rivet_strip():
    """上の 帯の 下の ふち：真ちゅうの 帯に びょう"""
    o = (f"<rect width='18' height='7' fill='{BR['m']}'/><rect width='18' height='1.6' fill='{BR['hl']}' opacity='.8'/><rect y='5.6' width='18' height='1.4' fill='{BR['dd']}'/>"
         f"<circle cx='9' cy='3.6' r='1.5' fill='{BR['d']}'/><circle cx='8.6' cy='3.2' r='.6' fill='{BR['hl']}'/>")
    return tile(18, 7, o)


def orn():
    """すみの 飾り（44×44）：かみ合う 歯車 2つ と 小さな 蒸気"""
    def g(cx, cy, r, n, c):
        ri = r * 0.82
        return (f"<path d='{gear_d(cx, cy, r, ri, n)}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='1' stroke-linejoin='round'/>"
                f"<circle cx='{cx}' cy='{cy}' r='{f(ri * 0.62)}' fill='{c['d']}'/><circle cx='{cx}' cy='{cy}' r='{f(r * 0.24)}' fill='{c['l']}' stroke='{c['dd']}' stroke-width='.8'/>")
    o = g(17, 27, 13, 12, BR) + g(33, 13, 9, 9, CU)
    o += "<circle cx='36' cy='33' r='4' fill='#F4EBDA' opacity='.9'/><circle cx='40' cy='29' r='3' fill='#F4EBDA' opacity='.8'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='スチームパンク', desc='歯車の馬', title='スチームパンク（真ちゅう×銅×夕ぐれ）', banner=ID,
    alt='夕ぐれの工場の町の石だたみを、真ちゅうと銅でできた機械仕掛けの馬が速足で走る。肩と腰の大きな歯車が回り、えんとつと鼻から蒸気がしゅっと出るイラスト',
    fonts=['Kaisei+Tokumin:wght@800', 'Murecho:wght@500;700'],
    v=dict(bg='#EFE2C6', ink='#2C2016', sub='#6A5640', card='#FBF4E2', cardB='1.5px solid #C9A86A', cardO='0 solid transparent', cardS='0 3px 0 #D9C092',
           radius='10px', rs='8px', font='"Murecho"', dfont='"Kaisei Tokumin"', dw='800', logo='#F0C76A', logoS='0 2px 0 #1E140C',
           iii='#E9C46A', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#4A3A32,#2E2420)', hdInk='#F4E4C0', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.08)', mLine='rgba(233,196,106,.6)', mInk='#F4E4C0', pill='rgba(0,0,0,.24)', pillLine='rgba(233,196,106,.5)', pillInk='#F4E4C0',
           coin='#E9C46A', coinInk='#2E2420', badge='#FFF2D4', badgeInk='#7A4A1E', badgeB='1.5px solid #C9A86A', tagBg='#F6EBD2', tagInk='#5A4026',
           tagLine='#C9A86A', warnBg='#F6DCCB', warnInk='#8E2E1A', zBg='#FFFAEE', zB='1.5px solid #E2CFA6', znBg='#2F6A62', znInk='#FFFFFF',
           znB='0 solid transparent', znR='3px', znS='none', acc='#8A4A1E', nR='6px', w2B='0 solid transparent', sep='1.5px dashed #C9A86A',
           btn='#9A5528', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='8px', btnS='0 3px 0 #5E3014', btn2='#FBF4E2', btn2Ink='#7A4A1E',
           btn2B='1.5px solid #B8925A', tab='#2E2420', tabB='1px solid #1E1612', tabInk='#D6C09A', tabOn='rgba(233,196,106,.16)', tabOnInk='#F0C76A',
           tabR='8px', sel='#9A5528', selInk='#FFFFFF', h1='#7A4A1E'),
    chk=dict(hd=['#4A3A32', '#2E2420']),
    css=[('', 'background-image:' + curi(tile_gears()) + ';background-size:130px 130px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-6px;height:7px;background:' + curi(rivet_strip()) + ' 0 0/18px 7px repeat-x'),
         ('.card', 'background-image:linear-gradient(180deg,rgba(201,154,62,.08),transparent 30%)')],
    orn=orn(),
    guide=dict(colors=[('#2E2420', '鉄'), ('#C99A3E', '真ちゅう'), ('#9A5528', '銅のボタン'), ('#2F6A62', '青さび'), ('#EFE2C6', '背景')],
               fonts='見出し：Kaisei Tokumin<br>本文：Murecho', shape='角丸10px・帯は 鉄の色で 下に 真ちゅうの びょうの 帯・うすい 歯車の 背景・すみに かみ合う 歯車・的中ボタンは 歯車と 圧力計の PUSH',
               pic='夕ぐれの 工場の 町・飛行船・石だたみ・大きな 歯車・真ちゅうと 銅の 機械仕掛けの 馬（歯車と 連結棒で 足が 動く・えんとつと 鼻から 蒸気）'),
)


# ================================================================== 的中ボタン：歯車と 圧力計の PUSH（gw）
def push_face(sfx=''):
    """ボタン（200×100）が 真ちゅうの 板（びょう・銅の ふち）。左右に 歯車が かみ合って 回り（.gwfg）、上に 圧力計（針が ゆれる .gwfn）と バルブ"""
    o = ''
    # うしろの 歯車（左右・回る）
    o += (f"<g class='gwfg'><path d='{gear_d(-6, 70, 30, 25, 14)}' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='2'/>"
          f"<circle cx='-6' cy='70' r='15' fill='{CU['d']}'/><circle cx='-6' cy='70' r='6' fill='{CU['l']}' stroke='{CU['dd']}' stroke-width='1.6'/></g>"
          f"<g class='gwfg r'><path d='{gear_d(206, 22, 24, 20, 11)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='2'/>"
          f"<circle cx='206' cy='22' r='12' fill='{BR['d']}'/><circle cx='206' cy='22' r='5' fill='{BR['l']}' stroke='{BR['dd']}' stroke-width='1.4'/></g>")
    # 圧力計（上の まん中）と パイプ
    o += (f"<rect x='92' y='-14' width='16' height='18' fill='{CU['d']}' stroke='{CU['dd']}' stroke-width='1.4'/>"
          f"<circle cx='100' cy='-30' r='20' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='2'/><circle cx='100' cy='-30' r='16' fill='#F6EDD6'/>")
    for k in range(9):
        a = math.radians(150 + k * 30)
        o += f"<path d='M{f(100 + math.cos(a) * 12)} {f(-30 + math.sin(a) * 12)} L{f(100 + math.cos(a) * 15)} {f(-30 + math.sin(a) * 15)}' stroke='#4A3A2A' stroke-width='1.4'/>"
    o += (f"<path d='M{f(100 + math.cos(math.radians(330)) * 13)} {f(-30 + math.sin(math.radians(330)) * 13)} A13 13 0 0 1 {f(100 + math.cos(math.radians(30)) * 13)} {f(-30 + math.sin(math.radians(30)) * 13)}' fill='none' stroke='#C8322A' stroke-width='3'/>"
          "<g class='gwfn' style='transform-origin:100px -30px'><path d='M100 -30 L110 -40' stroke='#2A1A12' stroke-width='2.4' stroke-linecap='round'/></g>"
          f"<circle cx='100' cy='-30' r='3' fill='{BR['dd']}'/><path d='M88 -40 A15 15 0 0 1 98 -45' stroke='#FFFFFF' stroke-width='2.4' fill='none' stroke-linecap='round' opacity='.6'/>")
    # 板（ボタン）
    o += (f"<rect x='0' y='0' width='200' height='100' rx='14' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='2.4'/>"
          f"<rect x='7' y='7' width='186' height='86' rx='9' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.6'/>"
          f"<rect x='9' y='9' width='182' height='14' rx='7' fill='{BR['l']}' opacity='.85'/>"
          f"<rect x='9' y='74' width='182' height='17' rx='8' fill='{BR['d']}' opacity='.55'/>")
    for x, y in ((16, 16), (184, 16), (16, 84), (184, 84), (100, 13), (100, 87)):
        o += f"<circle cx='{x}' cy='{y}' r='3.2' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='1'/><circle cx='{x - 0.9}' cy='{y - 0.9}' r='1.1' fill='{BR['hl']}'/>"
    o += f"<path d='M14 30 Q100 22 186 30' stroke='{BR['hl']}' stroke-width='1.6' fill='none' opacity='.6'/>"
    return f'<i class="gwf" aria-hidden="true"><svg viewBox="-40 -56 280 160" width="280" height="160">{o}</svg></i>'


def push_decor(sfx=''):
    """まわりの 蒸気（ふわっと 出て 消える .gwst）と 小さな ボルト"""
    o = ''
    for j, (x, y, r) in enumerate(((-26, 4, 10), (226, 70, 9), (-12, -30, 8), (230, 4, 8))):
        o += (f'<g class="gwst" style="animation-delay:{-0.9 * j:.1f}s;transform-origin:{x}px {y}px"><circle cx="{x}" cy="{y}" r="{r}" fill="#FBF4E6" opacity=".9"/>'
              f'<circle cx="{x + r * 0.8:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.7:.1f}" fill="#FBF4E6" opacity=".85"/><circle cx="{x - r * 0.7:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.6:.1f}" fill="#FFFFFF" opacity=".7"/></g>')
    return f'<i class="gwd" aria-hidden="true"><svg viewBox="-40 -60 280 180" width="280" height="180">{o}</svg></i>'


PIECES = dict(
    ga=piece(gear_svg(11, 10, BR, spokes=4, size=26)),
    gb=piece(gear_svg(11, 10, CU, spokes=0, size=26)),
    bt=piece(doc(20, 20, f"<path d='M10 2 L16.9 6 V14 L10 18 L3.1 14 V6 Z' fill='{FE['m']}' stroke='{FE['dd']}' stroke-width='1.2'/><circle cx='10' cy='10' r='3.2' fill='{FE['l']}'/>")),
    sp=piece(doc(20, 20, f"<path d='M4 16 Q2 12 6 11 T6 6 T10 4 T14 6 T14 11 T16 15' fill='none' stroke='{BR['m']}' stroke-width='2.2' stroke-linecap='round'/>")),
    st=piece(puff_svg(7, 34, 26)),
)


def push_burst():
    return fly_burst(CODE, ['ga', 'bt', 'gb', 'st', 'ga', 'sp', 'gb', 'bt'], 28, 92, sizes=dict(ga=(16, 22), gb=(15, 20), bt=(11, 15), sp=(13, 17), st=(22, 30)))


PUSH_CSS = r'''
/* ---------- スチームパンクの的中ボタン：歯車と 圧力計の PUSH（壁紙パック） ----------
   ボタンは 真ちゅうの 板（銅の ふち・びょう）に「PUSH」。左と 右上で 歯車が かみ合って 回り、上の 圧力計の 針が ゆれる。まわりに 蒸気が ふわっ。
   上下の 動きは 的中と 同じ。押すと 板が ちぢんで ふくらみ（強く 光らせない）、歯車・ボルト・ばね・蒸気が はじけて 落ち、真ちゅうの 光の 輪が 広がる */
.gw{--pushA:#C99A3E;--pushB:#5E4019;--pushC:#E9C46A;--rim:#E9C46A;--rimD:#4E2810}
.push.gw{--pr:14px;background:none;border-radius:14px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(46,30,16,.6)) drop-shadow(0 18px 24px rgba(0,0,0,.4))}
.push.gw span{top:2px;font:800 40px/1 "Kaisei Tokumin",serif;letter-spacing:.06em;color:#4E2810;text-shadow:0 1.5px 0 #FFE7A6,0 -1px 0 #5E4019}
.push.gw::after{inset:-24px -30px -18px;top:-74px;border-radius:30px;border-color:rgba(233,196,106,.85)}
.gw .gwf{position:absolute;left:-40px;top:-56px;width:280px;height:160px;pointer-events:none;font-style:normal}
.gw .gwf svg{display:block;width:280px;height:160px;overflow:visible}
.gw .gwd{position:absolute;left:-40px;top:-60px;width:280px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.gw .gwd svg{display:block;width:280px;height:180px;overflow:visible}
.gw .gwfg{transform-box:fill-box;transform-origin:50% 50%;animation:gwfRot 6s linear infinite}
.gw .gwfg.r{animation:gwfRotR 4.7s linear infinite}
@keyframes gwfRot{to{transform:rotate(360deg)}}
@keyframes gwfRotR{to{transform:rotate(-360deg)}}
.gw .gwfn{transform-box:view-box;animation:gwfNd 2.4s ease-in-out infinite}
@keyframes gwfNd{0%,100%{transform:rotate(-24deg)}45%{transform:rotate(16deg)}60%{transform:rotate(6deg)}75%{transform:rotate(20deg)}}
.gw .gwst{transform-box:view-box;opacity:0;animation:gwfSt 3.6s ease-out infinite}
@keyframes gwfSt{0%{opacity:0;transform:scale(.4) translateY(4px)}12%{opacity:.9}60%{opacity:0;transform:scale(1.25) translateY(-14px)}100%{opacity:0;transform:scale(1.25) translateY(-14px)}}
.pshadow.gw{width:230px}
.tap.gw{font-family:"Kaisei Tokumin",serif;font-weight:800;color:#F0C76A;letter-spacing:.12em;text-shadow:0 2px 0 #2E2420,0 0 10px rgba(233,196,106,.5)}
.pressed.gw{border-radius:14px;background:#C99A3E;box-shadow:0 0 0 4px #B5683A,0 7px 0 4px #4E2810;animation-name:gwPress,fxH}
@keyframes gwPress{0%{transform:scale(1)}22%{transform:scale(.9)}45%{transform:scale(1.07)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.gw .gwfg,.gw .gwfn,.gw .gwst{animation:none}.gw .gwst,.clips.gw{display:none}}
''' + fly_css(CODE, 'rgba(233,196,106,.85)', PIECES)

PUSH = dict(code=CODE, face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
