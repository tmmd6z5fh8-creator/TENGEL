"""壁紙パック ⑨スチームパンク（まさちゃんの 指定「歯車で動く機械仕掛けの馬。蒸気がしゅっ」）
   上の絵：夕ぐれの 工場の 町（工場・えんとつ・時計台・ガスタンク）・飛行船・石だたみの 道。左上と 右上に 大きな 歯車。
     まん中を 真ちゅうの 機械の 馬が 速足で 走る：ボイラーの 胴（びょう・銅の 帯・のぞき窓の 中で 歯車が 回る・圧力計）・えんとつ・
     本物の 馬の 形の 首（上が 弓なり・板を 重ねた よろい・のどに 銅の 管）と 頭（ひたい・目の 上の まゆの 板・こはく色の ランプの 目・
     長い 鼻すじの 板・まるい ほおの 板と あごの 歯車・銅の 鼻先と 鼻の あなの すきま・口・耳 2まい・前髪）・
     流れる 毛の 房の たてがみ（銅と 真ちゅうの うすい 板）・銅線の しっぽ。肩と 腰の 大きな 歯車が 回って、機関車の 動輪のように 連結棒が 回る。
     第4.93版（まさちゃん「後ろ脚の動き方が変だから実際の馬の動きに合わせて！顔と立髪をもっとリアルな馬に近くして！」）：
     足は 本物の 馬の 関節：うしろ足＝腰 → もも（しりの 筋肉の 板）→ ひざ（前へ）→ すね → 飛節（うしろへ 出る かかと・けんの 鉄の 棒）→ 管 → 球節 → つなぎ → ひづめ
     （ひざと 飛節は いっしょに まがる）・前足＝ひじ → 前腕 → ひざ（歯車）→ 管 → 球節 → つなぎ → ひづめ。
   動き（CSS だけ・1回り 0.84秒の 速足＝ななめの 2本が いっしょ）：ひづめは 地面に ついて いる 間 道と 同じ 速さで うしろへ（すべらない）・
     最後に かかとから 上がって つま先で けり、宙では ひざと 飛節を まげて ひづめを うしろへ 折って 前へ はこぶ。体は 足が 地面に ついた まん中で 少し 下がる。
     歯車が 回る・連結棒が 円を えがく・頭が うなずく・たてがみが ゆれる・しっぽが ゆれる。道と 町が 流れる（遠いほど ゆっくり）・飛行船が ゆっくり 横切る。
     えんとつから 蒸気が 「しゅっ しゅっ」（3.6秒ごとに 3つ）・鼻から 「しゅっ」。強く 光らせない
     第4.94版（まさちゃん「スチームパンクは、16秒に一回、馬がオーバーヒートして、背中の煙突が爆発して、口をパックリ開けて、破壊光線を打つようにして！」）：
     16秒に 1回（1回りの 4秒め から 7秒 ほど）：体が ゆっくり 赤く 熱く なり（2.4秒・まわりに だいだいの もや）、圧力計の 針が 上がって ふるえ、
     板の すきまから 蒸気が しゅー → えんとつが 爆発（火の玉が 0.3秒 かけて ふくらむ・うしろに 黒い けむり・火の 粉・ふたが 回りながら 上へ 飛んで、
     3秒 あとに 回りながら 落ちて きて のる）→ 頭を 上げて 口を ぱっくり（頭を 上の 頭と 下あごに 分けて、ほおの 歯車が ちょうつがい。
     口の 中は 3まいの くさび＝あごと いっしょ・半分の 角度・上の 頭に つく で、とじて いる 間は 上の 頭と あごの うしろに かくれる）→
     口に 光を ためて 右へ 破壊光線（白い しんと まわりの だいだいの 光の もや・右の はしで 光が はじける。0.3秒 かけて 明るく、0.35秒 かけて 消える）→
     口を とじて 頭を もどし、ゆっくり さめる。速足は ずっと つづく（足は すべらない）。鼻の 蒸気は オーバーヒートの ない ころに 16秒に 2回"""
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
# 第4.93版：足は 本物の 馬の 関節（まさちゃん「後ろ脚の動き方が変だから実際の馬の動きに合わせて」）
#   うしろ足：腰 → もも → ひざ（前へ 出る）→ すね → 飛節（うしろへ 出る）→ 管 → 球節 → つなぎ → ひづめ。
#     ひざと 飛節は いっしょに まがる（管は いつも ももより DELTA 度 立つ：本物の 馬の しくみ）
#   前足：ひじ → 前腕 → ひざ（まがると 前へ 出る）→ 管 → 球節 → つなぎ → ひづめ。地面に ついて いる 間は ひざが のびた まま
#   速足：ななめの 2本が いっしょ（左前と 右うしろ・右前と 左うしろ）。ひづめは 地面に ついて いる 間 道と 同じ 速さで うしろへ（すべらない）・
#     最後に かかとから 上がって つま先で けり、宙では ひづめが うしろへ 折れて 前へ はこぶ
T = 0.84            # 速足の 1回り（秒）
NS = 24             # 1回りを 何コマで 書くか（あいだは なめらかに つなぐ）
GROUND = 146        # ひづめの 底
SH = (240, 92)      # 前足の 軸（ひじ）
HP = (166, 88)      # うしろ足の 軸（腰）
LA, LB = 25.5, 19.0                 # 前：前腕・管
LF, LG, LC = 18.4, 21.9, 13.6       # うしろ：もも・すね・管
LP = 7.0            # つなぎ（球節 → 蹄冠）
HOOF_H = 5.2        # ひづめの 高さ
DELTA = 20.0        # うしろ足：管は ももより 20° 立つ
STRIDE = 28.0       # ひづめが 地面に ついて いる 間に うしろへ 進む 長さ
LIFT_F, LIFT_H = 9.0, 7.0           # 宙で ひづめを 上げる 高さ（前・うしろ）
XOFF = dict(f=2.0, h=-3.0)          # ひづめの まん中の 前後（軸から）
SPEED = STRIDE / (T / 2)            # 道の 速さ（px／秒）＝ひづめが うしろへ 進む 速さ
ROAD_W = 120
BOB = 1.4
CRANK = 7.5         # 肩と 腰の 歯車の クランクの 半径
OFFS = dict(fl=0.0, hr=0.0, fr=0.5, hl=0.5)      # 速足：ななめの 足が いっしょ


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * u)


def bob(t):
    """体の 上下：ななめの 2本が 地面に ついた まん中（t＝.25・.75）で いちばん 低い"""
    return -BOB * 0.5 * math.cos(4 * math.pi * t)


def hoof_path(q, front):
    """足の 位相 q の ひづめの 底の まん中（軸から の ずれ・前が +x・上が −y）と 傾き（度：＋＝つま先を 軸に かかとが 上がる／宙で うしろへ 折れる）"""
    lift = LIFT_F if front else LIFT_H
    if q < 0.5:
        u = q / 0.5
        tilt = 0.0 if u < 0.85 else 24.0 * ((u - 0.85) / 0.15) ** 1.5      # けり出し：最後の 15% で かかとが 上がる
        return STRIDE / 2 - STRIDE * u, 0.0, tilt
    u = (q - 0.5) / 0.5
    x = -STRIDE / 2 + STRIDE * ease(u)
    y = -lift * math.sin(math.pi * u) ** 1.1
    tilt = 24.0 + 36.0 * math.sin(math.pi / 2 * u / 0.55) if u < 0.55 else 60.0 * (1 - (u - 0.55) / 0.45) ** 1.3
    return x, y, tilt


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


HOOF_REL = dict(heel=(-3.1, 4.9), toe=(5.5, 4.9), top_f=(2.7, -0.3), top_b=(-2.7, 0.3))      # ひづめ（蹄冠から・傾き 0）


def coronet_at(bx, by, tilt):
    """ひづめの 底の まん中 (bx, by)・傾き → 蹄冠（つなぎの 下の はし）。つま先を 軸に 回す"""
    toe = (bx + 4.6, by)
    c0 = (bx - 0.9, by - 4.9)
    v = rot((c0[0] - toe[0], c0[1] - toe[1]), -tilt)
    return toe[0] + v[0], toe[1] + v[1]


def ik2(px, py, tx, ty, l1, l2):
    """前足：ひじ → ひざ → 球節（ひざは まがると 前へ 出る）。画面の 角度（x 右・y 下）"""
    dx, dy = tx - px, ty - py
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1.0, min(1.0, c)))
    a1 = a - b
    kx, ky = px + l1 * math.cos(a1), py + l1 * math.sin(a1)
    return (kx, ky), math.degrees(a1), math.degrees(math.atan2(ty - ky, tx - kx))


def hind_ik(px, py, tx, ty):
    """うしろ足：腰 → ひざ（もも LF）→ 飛節（すね LG）→ 球節（管 LC：ももより DELTA 立つ）。ももの 向きを さがす（飛節は ひざより うしろ）"""
    best = None
    for k in range(1801):
        af = math.radians(25 + k * 0.05)
        ac = af + math.radians(DELTA)
        sx, sy = px + LF * math.cos(af), py + LF * math.sin(af)
        rx, ry = tx - LC * math.cos(ac), ty - LC * math.sin(ac)
        if rx > sx - 2:
            continue
        err = abs(math.hypot(rx - sx, ry - sy) - LG)
        if best is None or err < best[0]:
            best = (err, af, ac, (sx, sy), (rx, ry))
    err, af, ac, st, hk = best
    return st, hk, math.degrees(af), math.degrees(math.atan2(hk[1] - st[1], hk[0] - st[0])), math.degrees(ac), err


def leg_solve(name):
    """1回り（NS+1 コマ）の 骨の 向き（画面の 角度）と 関節の 場所"""
    front = name[0] == 'f'
    piv = SH if front else HP
    out = []
    for i in range(NS + 1):
        t = i / NS
        q = (t + OFFS[name]) % 1.0
        px, py = piv[0], piv[1] + bob(t)
        hx, hy, tilt = hoof_path(q, front)
        bx, by = piv[0] + XOFF['f' if front else 'h'] + hx, GROUND + hy
        cx, cy = coronet_at(bx, by, tilt)
        alpha = 58.0 + tilt * 0.4                                         # つなぎの 立ち（地面から）。届かない ときは 立てる
        lim = (LA + LB - 0.6) if front else (LF + LG + LC) * 0.97
        while True:
            fx_, fy_ = cx - LP * math.cos(math.radians(alpha)), cy - LP * math.sin(math.radians(alpha))
            if math.hypot(fx_ - px, fy_ - py) <= lim or alpha >= 88:
                break
            alpha += 0.5
        ap = math.degrees(math.atan2(cy - fy_, cx - fx_))                  # つなぎ（球節 → 蹄冠）
        if front:
            kn, a1, a2 = ik2(px, py, fx_, fy_, LA, LB)
            segs = [a1, a2, ap]
            joints = [(px, py), kn, (fx_, fy_), (cx, cy)]
        else:
            st, hk, af, ag, ac, err = hind_ik(px, py, fx_, fy_)
            segs = [af, ag, ac, ap]
            joints = [(px, py), st, hk, (fx_, fy_), (cx, cy)]
        out.append(dict(segs=segs, hoof=-tilt, joints=joints, bottom=(bx, by), tilt=tilt))
    return out


def leg_keys(name):
    """CSS の 回転（関節ごと：はじめは 骨の 向き、あとは 1つ上の 骨から の 差。最後は ひづめ）の コマ（NS+1 こ）"""
    fr = leg_solve(name)
    series = []
    nseg = len(fr[0]['segs'])
    for j in range(nseg + 1):
        arr = []
        for f_ in fr:
            ab = [a - 90.0 for a in f_['segs']] + [f_['hoof']]          # 下向きが 0・時計回りが ＋
            arr.append(ab[j] if j == 0 else ab[j] - ab[j - 1])
        for i in range(1, len(arr)):
            while arr[i] - arr[i - 1] > 180:
                arr[i] -= 360
            while arr[i] - arr[i - 1] < -180:
                arr[i] += 360
        series.append(arr)
    return series


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


def _bolt(x, y, r, c, far=False):
    """関節の ボルト（輪と まん中の 穴・光）"""
    return (f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r)}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='.8'/>"
            f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(r * 0.42)}' fill='{c['dd']}'/>"
            f"<path d='M{f(x - r * 0.62)} {f(y - r * 0.2)} A{f(r * 0.66)} {f(r * 0.66)} 0 0 1 {f(x + r * 0.1)} {f(y - r * 0.64)}' fill='none' stroke='{c['hl'] if 'hl' in c else c['l']}' stroke-width='.8' stroke-linecap='round' opacity='.8'/>")


# 足の 部品：どれも 自分の 軸（関節）を 絵の 中の (ox, oy) に おいて、骨は 下（+y）へ のびる。返り値：(svg, ox, oy, w, h)
def seg_thigh(far=False):
    """うしろ足の もも（腰の 軸 → ひざ）：馬の しりの 大きな 筋肉の 形の 真ちゅうの 板（うしろへ ふくらむ・ひざで 細く）"""
    c = dark(BR) if far else BR
    cu = dark(CU) if far else CU
    ox, oy, w, h = 19, 15, 33, 44
    T_ = lambda x, y: (x + ox, y + oy)
    pts = [(-13, -6), (-17, 4), (-15.4, 14), (-9.4, 20.6), (-4, LF + 3.6), (2.8, LF + 3.6), (6.2, LF - 1.2), (8.6, 10), (8.6, 0), (5.4, -8.6), (-4.4, -11.8)]
    o = f"<path d='{smooth([T_(*q) for q in pts], True, 0.32)}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
    o += f"<path d='{smooth([T_(*q) for q in ((4.2, -6.2), (6.4, 1), (6.4, 10), (4.4, LF - 2))], False, 0.35)}' fill='none' stroke='{c['hl'] if 'hl' in c else c['l']}' stroke-width='1.6' stroke-linecap='round' opacity='.75'/>"
    o += f"<path d='{smooth([T_(*q) for q in ((-12.6, 3), (-11.6, 12), (-7.4, 18), (-3, LF + 1.4))], False, 0.35)}' fill='none' stroke='{c['d']}' stroke-width='1.6' stroke-linecap='round' opacity='.8'/>"
    a, b = T_(-13.4, 8.6), T_(6.9, 6.2)                                  # 銅の 帯
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])} L{f(b[0] - 0.4)} {f(b[1] + 3)} L{f(a[0] + 0.6)} {f(a[1] + 3.4)} Z' fill='{cu['m']}' stroke='{cu['dd']}' stroke-width='.6'/>"
    for q in ((-9.6, 1.6), (-5, -6.4), (3, -6.6), (-10.4, 14), (-1, 15.6)):
        x, y = T_(*q)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.9' fill='{c['dd']}'/>"
    return doc(w, h, o), ox, oy, w, h


def seg_gaskin(far=False):
    """うしろ足の すね（ひざ → 飛節）：真ちゅうの 柱・うしろに 飛節の 出っぱり（かかと）と けんの 鉄の 棒"""
    c = dark(BR) if far else BR
    fe = dark(FE, 0.2) if far else FE
    ox, oy, w, h = 10, 5, 19, 36
    T_ = lambda x, y: (x + ox, y + oy)
    body = [(-4.6, -1.4), (4.6, -1.4), (3.6, LG - 2), (2.6, LG + 1.6), (-3.2, LG + 1.6), (-4.2, LG - 3)]
    o = f"<path d='{P([T_(*q) for q in body])}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='1' stroke-linejoin='round'/>"
    a, b = T_(-2.6, 1), T_(-1.8, LG - 3)
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{c['hl'] if 'hl' in c else c['l']}' stroke-width='1.3' stroke-linecap='round' opacity='.75'/>"
    knob = [(-3.4, LG - 6.6), (-7.6, LG - 3.4), (-7.4, LG + 0.2), (-4.4, LG + 2.2), (-1, LG + 1)]       # 飛節の かかと
    o += f"<path d='{smooth([T_(*q) for q in knob], True, 0.3)}' fill='{c['d']}' stroke='{c['dd']}' stroke-width='.9'/>"
    a, b = T_(-4.4, 1.6), T_(-6.6, LG - 2.6)                               # けん（鉄の 棒）
    o += (f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{fe['dd']}' stroke-width='2.4' stroke-linecap='round'/>"
          f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{fe['l']}' stroke-width='.8' stroke-linecap='round' opacity='.8'/>")
    for yy in (5.5, 11.5):
        x, y = T_(0.2, yy)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.85' fill='{c['dd']}'/>"
    x, y = T_(0, 0)
    o += _bolt(x, y, 3.6, c)                                                # ひざの ボルト
    return doc(w, h, o), ox, oy, w, h


def seg_forearm(far=False):
    """前足の 前腕（ひじ → ひざ）：上が 太い 真ちゅうの 板（筋肉の 形）・銅の 帯"""
    c = dark(BR) if far else BR
    cu = dark(CU) if far else CU
    ox, oy, w, h = 9, 4, 18, 34
    T_ = lambda x, y: (x + ox, y + oy)
    pts = [(-5.6, -1), (6.4, -1.6), (5.2, 9), (3.8, LA - 1), (3, LA + 1.6), (-3, LA + 1.6), (-3.6, LA - 1), (-5.2, 10)]
    o = f"<path d='{smooth([T_(*q) for q in pts], True, 0.22)}' fill='{c['m']}' stroke='{c['dd']}' stroke-width='1' stroke-linejoin='round'/>"
    a, b = T_(4.2, 1), T_(2.6, LA - 2)
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{c['hl'] if 'hl' in c else c['l']}' stroke-width='1.4' stroke-linecap='round' opacity='.75'/>"
    a, b = T_(-4.4, 2), T_(-2.8, LA - 2)
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{c['d']}' stroke-width='1.3' stroke-linecap='round' opacity='.8'/>"
    y0 = LA * 0.46
    a = T_(-4.8, y0)
    o += f"<rect x='{f(a[0])}' y='{f(a[1])}' width='{f(9.4)}' height='2.6' rx='.8' fill='{cu['m']}' stroke='{cu['dd']}' stroke-width='.5'/>"
    for yy in (4, 17):
        x, y = T_(0.4, yy)
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.85' fill='{c['dd']}'/>"
    return doc(w, h, o), ox, oy, w, h


def seg_cannon(front, far=False):
    """管（ひざ／飛節 → 球節）：鉄の すね・まん中に 真ちゅうの 輪。うしろ足は 上に 飛節の ボルト"""
    fe = dark(FE, 0.2) if far else FE
    b = dark(BR) if far else BR
    L = LB if front else LC
    ox, oy, w, h = 6, 5, 12, int(L + 9)
    T_ = lambda x, y: (x + ox, y + oy)
    a = T_(-3, -1)
    o = (f"<rect x='{f(a[0])}' y='{f(a[1])}' width='6' height='{f(L + 2)}' rx='2.4' fill='{fe['m']}' stroke='{fe['dd']}' stroke-width='.8'/>"
         f"<rect x='{f(a[0] + 0.8)}' y='{f(a[1] + 1)}' width='1.4' height='{f(L)}' rx='.7' fill='{fe['l']}' opacity='.8'/>")
    a = T_(-3.9, L * 0.44)
    o += f"<rect x='{f(a[0])}' y='{f(a[1])}' width='7.8' height='3.6' rx='1.3' fill='{b['m']}' stroke='{b['dd']}' stroke-width='.6'/>"
    if not front:
        x, y = T_(0, 0)
        o += _bolt(x, y, 3.3, b)                                            # 飛節の ボルト
    return doc(w, h, o), ox, oy, w, h


def seg_pastern(far=False):
    """つなぎ（球節 → 蹄冠）：上に 球節の 丸い 鉄の 玉（真ちゅうの ふち）"""
    fe = dark(FE, 0.2) if far else FE
    b = dark(BR) if far else BR
    ox, oy, w, h = 5, 5, 10, int(LP + 8)
    T_ = lambda x, y: (x + ox, y + oy)
    a = T_(-2.2, 0)
    o = f"<rect x='{f(a[0])}' y='{f(a[1])}' width='4.4' height='{f(LP + 1)}' rx='1.8' fill='{fe['m']}' stroke='{fe['dd']}' stroke-width='.7'/>"
    x, y = T_(0, 0)
    o += (f"<circle cx='{f(x)}' cy='{f(y)}' r='3.4' fill='{fe['m']}' stroke='{b['d']}' stroke-width='1.1'/>"
          f"<circle cx='{f(x - 1)}' cy='{f(y - 1)}' r='1' fill='{fe['l']}' opacity='.9'/>")
    return doc(w, h, o), ox, oy, w, h


def seg_hoof(far=False):
    """ひづめ（蹄冠が 軸・傾き 0 で 底が 水平）：鉄の ひづめ・底に 真ちゅうの 蹄鉄"""
    fe = dark(FE, 0.2) if far else FE
    b = dark(BR) if far else BR
    ox, oy, w, h = 5, 3, 13, 10
    T_ = lambda q: (q[0] + ox, q[1] + oy)
    hr = HOOF_REL
    pts = [T_(hr['top_b']), T_(hr['top_f']), T_(hr['toe']), T_(hr['heel'])]
    o = f"<path d='{P(pts)}' fill='{fe['d']}' stroke='{fe['dd']}' stroke-width='.8' stroke-linejoin='round'/>"
    a, c2 = T_((hr['heel'][0] - 0.3, hr['heel'][1] - 1.5)), T_((hr['toe'][0] + 0.2, hr['toe'][1] - 1.5))
    o += f"<rect x='{f(a[0])}' y='{f(a[1])}' width='{f(c2[0] - a[0])}' height='1.6' rx='.6' fill='{b['d']}'/>"
    a, c2 = T_((-1.8, 1.4)), T_((2.4, 1.2))
    o += f"<path d='M{f(a[0])} {f(a[1])} L{f(c2[0])} {f(c2[1])}' stroke='{fe['l']}' stroke-width='.8' opacity='.6'/>"
    return doc(w, h, o), ox, oy, w, h


BOILER_CLIP = "<clipPath id='gwBo'><rect x='150' y='62' width='104' height='40' rx='19'/></clipPath>"   # 胴の 形（明るい 帯を 切りぬく：第4.113版）


def body_svg():
    """胴（ボイラー）・えんとつ・首・のぞき窓の 中の 暗い 所・圧力計の 盤・しっぽの 根もと（絵は 舞台の 座標）"""
    o = ''
    # 首（第4.93版：本物の 馬の 首の 形＝上が 弓なりの たてがみの 線・下は のどの 線。板を 重ねた よろいの ような 真ちゅう・のどに 銅の 管）
    o += f"<path d='{smooth(NECK, True, 0.3)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
    hl = [(226, 64), (236, 53), (249, 42), (263, 33), (276, 27)]
    o += f"<path d='{smooth([(x + 3, y + 4) for x, y in hl], False, 0.35)}' fill='none' stroke='{BR['l']}' stroke-width='5' stroke-linecap='round' opacity='.75'/>"
    o += f"<path d='{smooth([(x + 2, y + 2.4) for x, y in hl], False, 0.35)}' fill='none' stroke='{BR['hl']}' stroke-width='1.4' stroke-linecap='round' opacity='.7'/>"
    for k in range(1, 6):                                                # 板の つなぎ目（首を よこぎる）と びょう
        t = k / 6
        a = crest_at(t)
        b = throat_at(t)
        m = ((a[0] + b[0]) / 2 + 2.2, (a[1] + b[1]) / 2 + 1.2)
        o += f"<path d='M{f(a[0] + 0.6)} {f(a[1] + 1.2)} Q{f(m[0])} {f(m[1])} {f(b[0] - 0.6)} {f(b[1] - 0.6)}' fill='none' stroke='{BR['dd']}' stroke-width='.9' opacity='.8'/>"
        for u in (0.3, 0.55, 0.8):
            x = a[0] + (b[0] - a[0]) * u + 1.2
            y = a[1] + (b[1] - a[1]) * u + 1.4
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.75' fill='{BR['dd']}'/>"
    # のどの 銅の 管（胸 → のど）と 留め金
    pipe = [(250, 94), (254, 82), (261, 70), (269, 59), (277, 50)]
    o += (f"<path d='{smooth(pipe, False, 0.35)}' fill='none' stroke='{CU['dd']}' stroke-width='4.4' stroke-linecap='round'/>"
          f"<path d='{smooth(pipe, False, 0.35)}' fill='none' stroke='{CU['m']}' stroke-width='3' stroke-linecap='round'/>"
          f"<path d='{smooth([(x - 0.8, y - 0.6) for x, y in pipe], False, 0.35)}' fill='none' stroke='{CU['hl']}' stroke-width='.9' stroke-linecap='round' opacity='.7'/>")
    for x, y in pipe[1:4]:
        o += f"<rect x='{f(x - 3)}' y='{f(y - 1.2)}' width='6' height='2.4' rx='.8' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='.5' transform='rotate(-35 {f(x)} {f(y)})'/>"
    # 胴（ボイラー）
    # 第4.113版：明るい 帯・すじ・下の かげは 胴の 形（丸い すみ）で 切りぬく（前は 帯の まるい はし（rx 4.5）が 胴の すみ（rx 19）の 外に
    #   はみ出て いて、熱で 赤く なった とき 両はしに 黄色い 光が 飛び出して 見えた：まさちゃん「光が飛び出してしまっているからボディ内に納めて！」）
    o += (f"<rect x='150' y='62' width='104' height='40' rx='19' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.3'/>"
          f"<g clip-path='url(#gwBo)'><rect x='153' y='65' width='98' height='9' rx='4.5' fill='{BR['l']}' opacity='.9'/>"
          f"<rect x='158' y='66' width='70' height='2.6' rx='1.3' fill='{BR['hl']}' opacity='.8'/>"
          f"<rect x='152' y='90' width='100' height='10' rx='5' fill='{BR['d']}' opacity='.6'/></g>")
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
          f"<rect x='214' y='54' width='14' height='2.6' fill='{BR['d']}'/>")
    # 鞍の かわりの 銅の 座（き甲の うしろ）と 番号板の かわりの 歯車の しるし
    o += (f"<path d='M186 62.6 Q198 56 210 62.6 Z' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.9'/>")
    # しっぽの 根もと
    o += f"<circle cx='152' cy='72' r='3.4' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.8'/>"
    return doc(W, H, o, defs=BOILER_CLIP)


# 首と 頭の 形（第4.93版：本物の 馬に 近く）
NECK = [(222, 64), (232, 54), (246, 42), (262, 32), (276, 25), (285, 23), (290, 30), (289, 40), (285, 45), (278, 53), (269, 63), (261, 75), (256, 87), (253, 99),
        (238, 99), (224, 78)]
POLL = (284, 24)                    # うなじ（頭の 軸の ちかく）
HEAD_ANG = 41.0                     # 頭の 向き（鼻すじ・水平から 下へ）
HEAD_SC = 1.0
HEAD_BOX = (270, 4, 58, 70)         # 頭の 絵の 箱（舞台の 座標：左上・はば・高さ）
HEAD_PIV = (285, 36)                # うなずく 軸


def crest_at(t):
    """首の 上の 線（き甲 t=0 → うなじ t=1）"""
    pts = NECK[:6]
    return _along(pts, t)


def throat_at(t):
    """首の 下の 線（胸 t=0 → のど t=1）"""
    pts = [NECK[13], NECK[12], NECK[11], NECK[10], NECK[9], NECK[8]]
    return _along(pts, t)


def _along(pts, t):
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    d = t * L[-1]
    for i in range(len(pts) - 1):
        if L[i + 1] >= d:
            u = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
    return pts[-1]


def hpt(x, y):
    """頭の 中の 点（うなじが 原点・x は 鼻すじに そって 鼻へ・y は あごの がわ）→ 舞台の 座標"""
    a = math.radians(HEAD_ANG)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -math.sin(a), math.cos(a)
    return (POLL[0] + (x * ux + y * vx) * HEAD_SC, POLL[1] + (x * uy + y * vy) * HEAD_SC)


HEAD_OUT = [(0, 0), (8, -1.3), (20, -0.7), (31, 0.4), (39.5, 1.6), (43.4, 3.8), (44.6, 6.8), (44, 9.8), (41.6, 10.9), (42.4, 12.4), (39.6, 14.6),
            (35.4, 14.2), (28, 15.8), (20, 18.4), (12, 19.8), (6, 18), (2.4, 13.4), (1.6, 7.6), (2.6, 3.2)]


# ---- 第4.94版：口が あく 頭（まさちゃん「16秒に一回、馬がオーバーヒートして、背中の煙突が爆発して、口をパックリ開けて、破壊光線を打つようにして！」）
#   頭を 上の 頭（目・耳・鼻すじ・ほおの 歯車）と 下あごに 分ける。下あごは ほおの 歯車を ちょうつがいに して ひらく。
#   口の 中（こい 色・歯）は 下あごと いっしょに 回り、とじて いる 間は 見えない（上の 頭の うしろ・opacity 0）
HINGE = (10.5, 12.4)        # あごの ちょうつがい（頭の 座標）＝ほおの 歯車の 中心
LIP = (43.6, 10.4)          # くちびるの 先（口の 線＝ちょうつがい → くちびる）
JAW_MAX = 26.0              # 口を あける 角度（度）
CHEEK_R = 6.1
MO_UP, MO_DN, MO_R = 10.0, 2.6, 32.4     # 口の 中の くさび：口の 線より 上・下の 角度（とじて いる とき かくれる はば）・長さ


def mouth_y(x):
    """口の 線の y（頭の 座標）"""
    return HINGE[1] + (LIP[1] - HINGE[1]) * (x - HINGE[0]) / (LIP[0] - HINGE[0])


def hrot(p, deg, c=HINGE):
    """頭の 座標で 点 p を c の まわりに deg 度（あごが あく 向きが ＋）"""
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def _arc(c, r, a0, a1, n):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


# 上の 頭の りんかく：うなじ → 鼻すじ → 鼻先 → くちびる → 口の 線を うしろへ → ほおの 歯車の ふち → のど
UPPER_OUT = (HEAD_OUT[:8] + [(43.9, 10.2)] + [(x, mouth_y(x)) for x in (40.0, 34.0, 28.0, 22.0)]
             + _arc(HINGE, CHEEK_R, -3.5, 76.0, 4) + [(8.4, 18.9), (6, 18), (2.4, 13.4), (1.6, 7.6), (2.6, 3.2)])
# 下あご：口の 線（ちょうつがい → くちびる）→ あご先 → あごの 下 → ちょうつがいの まわり（ほおの 歯車の 下に かくれる）
JAW_OUT = ([(x, mouth_y(x)) for x in (16.4, 22.0, 28.0, 34.0, 40.0)] + [LIP, (43.3, 11.6), (42.4, 12.4), (39.6, 14.6), (35.4, 14.2), (28, 15.8), (20, 18.4), (13.4, 18.5)]
           + _arc(HINGE, 5.9, 95.0, 345.0, 6))


def head_part(part):
    """頭の 部品（絵は HEAD_BOX の 箱・舞台の 座標で 重なる）：upper（上の 頭）・jaw（下あご）・mouth_a／b／c（口の 中と 歯）・heat_u／heat_j（熱で 赤く）"""
    bx, by, bw, bh = HEAD_BOX
    tr = lambda q: (q[0] - bx, q[1] - by)
    H_ = lambda x, y: tr(hpt(x, y))
    o = ''
    defs = ''
    if part == 'jaw':
        o += f"<path d='{smooth([H_(*q) for q in JAW_OUT], True, 0.22)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
        a, b = H_(18, mouth_y(18) + 1.6), H_(40, mouth_y(40) + 1.3)                 # 口の 線の 下の 明るい ふち
        o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{BR['l']}' stroke-width='1.3' stroke-linecap='round' opacity='.8'/>"
        jw = [H_(14, 19.2), H_(22, 17.6), H_(30, 15.4), H_(36, 14.2)]             # あごの 下の ふち（暗い）
        o += f"<path d='{smooth(jw, False, 0.3)}' fill='none' stroke='{BR['d']}' stroke-width='2' stroke-linecap='round' opacity='.7'/>"
        ch = [H_(43.3, 11.0), H_(42.4, 12.4), H_(39.6, 14.6), H_(35.4, 14.2), H_(37.6, 11.6)]   # 銅の あご先
        o += f"<path d='{smooth(ch, True, 0.25)}' fill='{CU['d']}' opacity='.85'/>"
        for q in ((24, 13.4), (31, 12.6)):
            x, y = H_(*q)
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.75' fill='{BR['dd']}'/>"
    elif part in ('mouth_a', 'mouth_b', 'mouth_c'):
        # 口の 中（3まい・どれも ちょうつがいが 頂点の くさび）：とじて いる 間は 上の 頭（口の 線より 上 MO_UP 度まで）と
        #   あご（下 MO_DN 度まで）の うしろに かくれる。A＝あごと いっしょに 回る・B＝半分の 角度で 回る・C＝上の 頭に つく。
        #   3まいで いつも 0〜あいた 角度 の すきまを ふさぐ（JAW_MAX ≦ 2×(MO_UP＋MO_DN)）
        lo_a, hi_a = (-MO_UP, 0.0) if part == 'mouth_a' else (-MO_UP, MO_DN)
        R0 = MO_R
        base = math.degrees(math.atan2(LIP[1] - HINGE[1], LIP[0] - HINGE[0]))
        pts = [HINGE] + [(HINGE[0] + R0 * math.cos(math.radians(base + a_)), HINGE[1] + R0 * math.sin(math.radians(base + a_)))
                         for a_ in [lo_a + (hi_a - lo_a) * k / 6 for k in range(7)]]
        o += f"<path d='{P([H_(*q) for q in pts])}' fill='#3A1208'/>"
        if part == 'mouth_c':                                            # 上の 歯（真ちゅう：口の 線から 下へ）
            for x in (25.0, 30.0, 35.0, 40.0):
                t = ((x - 1.7, mouth_y(x - 1.7)), (x, mouth_y(x) + 2.6), (x + 1.7, mouth_y(x + 1.7)))
                o += f"<path d='{P([H_(*q) for q in t])}' fill='{BR['hl']}' stroke='{BR['d']}' stroke-width='.5' stroke-linejoin='round'/>"
            g = H_(36, mouth_y(36) + 1)                                  # 奥の 赤い 光
            o += f"<circle cx='{f(g[0])}' cy='{f(g[1])}' r='5' fill='#C8401A' opacity='.45'/>"
        if part == 'mouth_a':                                            # 下の 歯（あごの 口の 線から 上へ）
            for x in (23.0, 28.0, 33.0, 38.0):
                t = ((x - 1.6, mouth_y(x - 1.6)), (x, mouth_y(x) - 2.6), (x + 1.6, mouth_y(x + 1.6)))
                o += f"<path d='{P([H_(*q) for q in t])}' fill='{BR['hl']}' stroke='{BR['d']}' stroke-width='.5' stroke-linejoin='round'/>"
    elif part == 'mouth_l':                                              # 第4.113版：光線を うつ とき 口の 中を みたす 光（口の あな＝口の 線と 24° あいた あごの 口の 線の 間）
        xs = [HINGE[0] + 3 + (LIP[0] - HINGE[0] - 3) * k / 8 for k in range(9)]
        up = [(x, mouth_y(x)) for x in xs]
        dn = [hrot((x, mouth_y(x)), JAW_MAX - 2) for x in xs]
        poly = [H_(*q) for q in up] + [H_(*q) for q in dn[::-1]]
        a, b = H_(HINGE[0] + 6, mouth_y(HINGE[0] + 6) + 2), H_(LIP[0] - 1, mouth_y(LIP[0] - 1) + 3)
        defs += (f"<linearGradient id='ml' gradientUnits='userSpaceOnUse' x1='{f(a[0])}' y1='{f(a[1])}' x2='{f(b[0])}' y2='{f(b[1])}'>"
                 "<stop offset='0' stop-color='#FF7A20' stop-opacity='.85'/><stop offset='.45' stop-color='#FFC24A'/><stop offset='1' stop-color='#FFFBE6'/></linearGradient>")
        o += f"<path d='{P(poly)}' fill='url(#ml)'/>"
        c = H_(LIP[0] - 6, mouth_y(LIP[0] - 6) + 4.5)
        o += f"<circle cx='{f(c[0])}' cy='{f(c[1])}' r='5' fill='#FFFFFF' opacity='.8'/>"
    elif part in ('heat_u', 'heat_j'):                                   # 熱で 赤く（opacity で 上げ下げ）
        out = UPPER_OUT if part == 'heat_u' else JAW_OUT
        o += f"<path d='{smooth([H_(*q) for q in out], True, 0.22 if part == 'heat_j' else 0.28)}' fill='#E8301A' opacity='.56'/>"
        if part == 'heat_u':
            a, b = H_(14, 1.6), H_(38, 3.2)
            o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='#FFD27A' stroke-width='1.6' stroke-linecap='round' opacity='.7'/>"
    else:                                                                # upper：上の 頭
        for (b0, b1, tip, c) in (((-1.2, -0.6), (3.4, -1.4), (-6.4, -12.2), BR['d']), ((1.6, -0.9), (6.2, -1.4), (-2.6, -12.8), BR['m'])):   # 耳（奥 → 手前）
            pa, pb, pt_ = H_(*b0), H_(*b1), H_(*tip)
            mid = ((pa[0] + pt_[0]) / 2 - 1.2, (pa[1] + pt_[1]) / 2)
            mid2 = ((pb[0] + pt_[0]) / 2 + 1.6, (pb[1] + pt_[1]) / 2 + 0.6)
            o += (f"<path d='M{f(pa[0])} {f(pa[1])} Q{f(mid[0])} {f(mid[1])} {f(pt_[0])} {f(pt_[1])} Q{f(mid2[0])} {f(mid2[1])} {f(pb[0])} {f(pb[1])} Z' "
                  f"fill='{c}' stroke='{BR['dd']}' stroke-width='.9' stroke-linejoin='round'/>")
            ci = ((pa[0] * 0.3 + pb[0] * 0.7 + pt_[0]) / 2, (pa[1] * 0.3 + pb[1] * 0.7 + pt_[1]) / 2)
            o += f"<path d='M{f(pa[0] * 0.5 + pb[0] * 0.5)} {f(pa[1] * 0.5 + pb[1] * 0.5 - 0.6)} Q{f(ci[0])} {f(ci[1])} {f(pt_[0] + 0.4)} {f(pt_[1] + 1.6)}' fill='none' stroke='{CU['m']}' stroke-width='1.6' stroke-linecap='round' opacity='.85'/>"
        o += f"<path d='{smooth([H_(*q) for q in UPPER_OUT], True, 0.28)}' fill='{BR['m']}' stroke='{BR['dd']}' stroke-width='1.1' stroke-linejoin='round'/>"
        nas = [H_(10, 0.4), H_(39, 2.4), H_(40, 6.4), H_(13, 5.8)]                # 鼻すじの 板（明るい）と まん中の すじ
        o += f"<path d='{smooth(nas, True, 0.2)}' fill='{BR['l']}' opacity='.9'/>"
        a, b = H_(14, 1.6), H_(38, 3.2)
        o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{BR['hl']}' stroke-width='1.2' stroke-linecap='round' opacity='.8'/>"
        seam = [H_(9, 6.6), H_(20, 8.0), H_(32, 9.2), H_(38, 9.6)]
        o += f"<path d='{smooth(seam, False, 0.3)}' fill='none' stroke='{BR['dd']}' stroke-width='.8' opacity='.75'/>"
        mz = [H_(35, 1.0), H_(43.4, 3.8), H_(44.6, 6.8), H_(44, 9.8), H_(41.6, 10.7), H_(37, 10.6), H_(34, 8)]   # 銅の 鼻先（上くちびるまで）
        o += f"<path d='{smooth(mz, True, 0.25)}' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.8' stroke-linejoin='round'/>"
        a, b = H_(36.4, 2.6), H_(42.6, 4.6)
        o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{CU['hl']}' stroke-width='1' stroke-linecap='round' opacity='.75'/>"
        nc = H_(40.2, 5.8)
        o += f"<ellipse cx='{f(nc[0])}' cy='{f(nc[1])}' rx='2.7' ry='1.7' transform='rotate({f(HEAD_ANG + 12)} {f(nc[0])} {f(nc[1])})' fill='{CU['dd']}'/>"
        for k in range(3):
            a, b = H_(38.8 + k * 1.0, 4.9 + k * 0.5), H_(39.8 + k * 1.0, 6.9 + k * 0.5)
            o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{CU['l']}' stroke-width='.5' opacity='.8'/>"
        a, b = H_(43.8, 10.3), H_(36.6, 10.9)                                         # 上くちびるの ふち
        o += f"<path d='M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' stroke='{BR['dd']}' stroke-width='1' stroke-linecap='round'/>"
        ec = H_(13.6, 3.4)                                                             # 目：まゆの 板・アーモンド形の こはく色の ランプ
        br_ = [H_(9.4, 0.8), H_(13.6, -0.2), H_(18.2, 1.6), H_(16.4, 2.4), H_(11.4, 2.2)]
        o += f"<path d='{smooth(br_, True, 0.3)}' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='.6'/>"
        o += (f"<ellipse cx='{f(ec[0])}' cy='{f(ec[1])}' rx='4.2' ry='2.9' transform='rotate({f(HEAD_ANG - 6)} {f(ec[0])} {f(ec[1])})' fill='#FFB648' opacity='.22'/>"
              f"<ellipse cx='{f(ec[0])}' cy='{f(ec[1])}' rx='3.1' ry='2.0' transform='rotate({f(HEAD_ANG - 6)} {f(ec[0])} {f(ec[1])})' fill='{BR['dd']}'/>"
              f"<ellipse cx='{f(ec[0] + 0.2)}' cy='{f(ec[1])}' rx='2.3' ry='1.45' transform='rotate({f(HEAD_ANG - 6)} {f(ec[0])} {f(ec[1])})' fill='#FFB648'/>"
              f"<circle cx='{f(ec[0] + 0.9)}' cy='{f(ec[1] + 0.2)}' r='.9' fill='#7A3A0A'/><circle cx='{f(ec[0] - 0.4)}' cy='{f(ec[1] - 0.5)}' r='.6' fill='#FFF0C8'/>")
        for q in ((22, 4.6), (30, 5.6)):
            x, y = H_(*q)
            o += f"<circle cx='{f(x)}' cy='{f(y)}' r='.75' fill='{BR['dd']}'/>"
        rg = H_(37.6, 11.0)                                                            # はみの 輪
        o += f"<circle cx='{f(rg[0])}' cy='{f(rg[1])}' r='2.3' fill='none' stroke='{CU['l']}' stroke-width='1.1'/>"
        cc = H_(*HINGE)                                                                # まるい ほお：あごの ちょうつがいの 歯車
        o += (f"<circle cx='{f(cc[0])}' cy='{f(cc[1])}' r='{CHEEK_R}' fill='{BR['d']}' stroke='{BR['dd']}' stroke-width='.9'/>"
              f"<path d='M{f(cc[0] - 4.8)} {f(cc[1] - 1.8)} A5.2 5.2 0 0 1 {f(cc[0] + 1.4)} {f(cc[1] - 5)}' fill='none' stroke='{BR['l']}' stroke-width='1.2' stroke-linecap='round' opacity='.7'/>")
        for k in range(8):
            a_ = 2 * math.pi * k / 8
            o += f"<circle cx='{f(cc[0] + math.cos(a_) * 4.6)}' cy='{f(cc[1] + math.sin(a_) * 4.6)}' r='.65' fill='{BR['dd']}'/>"
        o += f"<path d='{gear_d(cc[0], cc[1], 2.8, 2.2, 8)}' fill='{CU['m']}' stroke='{CU['dd']}' stroke-width='.6'/><circle cx='{f(cc[0])}' cy='{f(cc[1])}' r='.9' fill='{CU['dd']}'/>"
        for k, (L, bend, c) in enumerate(((10.5, 2.2, CU['m']), (8.6, 1.4, BR['l']), (7.2, 2.6, CU['l']))):   # 前髪
            p0 = H_(1.0 + k * 0.9, -1.2)
            p1 = H_(4.6 + k * 1.2, 1.2 + bend)
            p2 = H_(L + k * 0.6, 3.2 + k * 0.5)
            o += (f"<path d='M{f(p0[0] - 1.1)} {f(p0[1])} Q{f(p1[0] - 1.4)} {f(p1[1])} {f(p2[0])} {f(p2[1])} Q{f(p1[0] + 1.2)} {f(p1[1] - 0.8)} {f(p0[0] + 1.3)} {f(p0[1] - 0.4)} Z' "
                  f"fill='{c}' stroke='{CU['dd']}' stroke-width='.5' stroke-linejoin='round'/>")
    return doc(bw, bh, o, defs=defs)


# ---- オーバーヒートの 部品
OH_S = 16.0                 # 1回り（秒）
OH_AT = 4.0                 # 1回りの 中で はじまる 時刻
OH_TILT = -40.0             # 光線を うつ とき 頭を 上げる 角度（うなずく 軸の まわり）
BEAM_DIR = 6.0              # 光線の 向き（画面で 水平から 下へ 度）
BEAM_L = 150.0              # 光線の 長さ（右の はしの 外まで）
MOUTH = (42.35, 17.75)      # 口の あいだ（あいた とき・頭の 座標）＝光線の 出る 所
CHIM = (221.0, 41.0)        # えんとつの 口（舞台の 座標）


def cap_svg():
    """えんとつの ふた（爆発で 飛んで、あとで 落ちて もどる）：絵の (1, 1)＝舞台の (212.5, 41)"""
    return doc(19, 8, f"<rect x='1' y='1' width='17' height='6' rx='1.6' fill='{FE['m']}' stroke='{FE['dd']}' stroke-width='.9'/>"
                      f"<rect x='2' y='1.6' width='15' height='1.6' rx='.8' fill='{FE['l']}'/>")


def heat_svg():
    """熱で 赤く 光る 色（胴・首・えんとつに 重ねる。opacity で ゆっくり 上げ下げ）"""
    defs = "<linearGradient id='h' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FF5A22'/><stop offset='1' stop-color='#C8180A'/></linearGradient>"
    o = (f"<g fill='url(#h)' opacity='.6'><path d='{smooth(NECK, True, 0.3)}'/><rect x='150' y='62' width='104' height='40' rx='19'/>"
         "<path d='M214 64 L216 46 H226 L228 64 Z'/></g>")
    o += "<g clip-path='url(#gwBo)'>"                                    # 第4.113版：光る 帯も 胴の 形の 中だけ
    for x in (172, 206, 236):                                            # 銅の 帯が 明るく
        o += f"<rect x='{x - 1.3}' y='63.4' width='2.6' height='37.2' rx='1.3' fill='#FFC266' opacity='.75'/>"
    o += "<rect x='160' y='66.2' width='84' height='2.6' rx='1.3' fill='#FFE29A' opacity='.6'/></g>"
    return doc(W, H, o, defs=defs + BOILER_CLIP)


def halo_svg():
    """熱の まわりの もや（体の うしろ・だいだい）"""
    defs = ("<radialGradient id='g' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FF8A3A' stop-opacity='.7'/>"
            "<stop offset='.6' stop-color='#FF5A1E' stop-opacity='.28'/><stop offset='1' stop-color='#FF4A10' stop-opacity='0'/></radialGradient>")
    return doc(184, 104, "<ellipse cx='92' cy='52' rx='92' ry='52' fill='url(#g)'/>", defs=defs)


def fireball_svg():
    """えんとつの 爆発の 火の玉（下の まん中が えんとつの 口）"""
    defs = ("<radialGradient id='f' cx='.5' cy='.62' r='.58'><stop offset='0' stop-color='#FFFBE6'/><stop offset='.28' stop-color='#FFE27A'/>"
            "<stop offset='.62' stop-color='#FF9A2E'/><stop offset='1' stop-color='#D8401A'/></radialGradient>")
    R = rnd(7)
    pts = []
    for k in range(20):                                                  # もこもこ ふくらむ 火の かたまり（上の ほうが 高く のびる）
        a = -math.pi / 2 + 2 * math.pi * k / 20
        up = max(0.0, -math.sin(a))
        r = (12.6 + (2.2 if k % 2 == 0 else 0.0) + R.uniform(-0.8, 0.8)) * (1.0 + 0.3 * up)
        pts.append((24 + math.cos(a) * r, 30 + math.sin(a) * r * 0.92))
    o = f"<path d='{smooth(pts, True, 0.5)}' fill='url(#f)'/>"
    for x, y, r in ((17, 22, 5.5), (30, 20, 6), (24, 14, 5)):           # 中の もこもこ（明るい）
        o += f"<circle cx='{x}' cy='{y}' r='{r}' fill='#FFD25A' opacity='.55'/>"
    o += "<ellipse cx='24' cy='31' rx='8' ry='6.4' fill='#FFFFFF' opacity='.7'/>"
    return doc(48, 46, o, defs=defs)


def spark_svg():
    return doc(6, 6, "<circle cx='3' cy='3' r='2.2' fill='#FFD25A'/><circle cx='3' cy='3' r='1' fill='#FFFBE6'/>")


def charge_svg():
    """口の 中で ためる 光（光線の 根もと）"""
    defs = ("<radialGradient id='c' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FFFFFF'/><stop offset='.3' stop-color='#FFF2B0'/>"
            "<stop offset='.6' stop-color='#FFB040' stop-opacity='.6'/><stop offset='1' stop-color='#FF7A20' stop-opacity='0'/></radialGradient>")
    return doc(32, 32, "<circle cx='16' cy='16' r='16' fill='url(#c)'/>", defs=defs)


BEAM_IN = dict(core=7.0, glow=22.0)   # 光線の 左の はし（口）を やわらかく 消す 長さ（第4.113版：前は もやの 半円が 絵の 外で 四角く 切れて いた）


def beam_svg(core=False):
    """破壊光線（左の はしが 口・右へ のびる）：core＝白い しん・ほか＝まわりの 光の もや。左の はしは mask で やわらかく（口の 光から つながる）"""
    L = BEAM_L
    fade = BEAM_IN['core' if core else 'glow']
    mk = (f"<linearGradient id='m' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#000'/><stop offset='{f(fade / L, 4)}' stop-color='#fff'/>"
          f"<stop offset='1' stop-color='#fff'/></linearGradient>")
    if core:
        h = 12
        defs = ("<linearGradient id='b' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FFE89A'/><stop offset='.3' stop-color='#FFFFFF'/>"
                "<stop offset='.7' stop-color='#FFFFFF'/><stop offset='1' stop-color='#FFE89A'/></linearGradient>")
        o = f"<rect x='0' y='1.5' width='{f(L)}' height='9' fill='url(#b)'/>"
    else:
        h = 34
        defs = ("<linearGradient id='b' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FF7A2A' stop-opacity='0'/><stop offset='.3' stop-color='#FF9A3A' stop-opacity='.45'/>"
                "<stop offset='.5' stop-color='#FFD25A' stop-opacity='.9'/><stop offset='.7' stop-color='#FF9A3A' stop-opacity='.45'/><stop offset='1' stop-color='#FF7A2A' stop-opacity='0'/></linearGradient>")
        o = f"<rect x='0' y='0' width='{f(L)}' height='34' fill='url(#b)'/>"
        for k, x in enumerate((30, 62, 94, 126)):                        # 光の もやの つぶ
            o += f"<ellipse cx='{x}' cy='{17 + (-6 if k % 2 else 6)}' rx='5' ry='2.2' fill='#FFF2B0' opacity='.5'/>"
    defs += mk + f"<mask id='k' maskUnits='userSpaceOnUse' x='0' y='0' width='{f(L)}' height='{h}'><rect x='0' y='0' width='{f(L)}' height='{h}' fill='url(#m)'/></mask>"
    return doc(L, h, f"<g mask='url(#k)'>{o}</g>", defs=defs)


def splash_svg():
    """光線の 先で はじける 光（右の はし）"""
    defs = ("<radialGradient id='s' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FFFFFF'/><stop offset='.35' stop-color='#FFE89A' stop-opacity='.9'/>"
            "<stop offset='1' stop-color='#FF9A3A' stop-opacity='0'/></radialGradient>")
    o = "<circle cx='22' cy='22' r='22' fill='url(#s)'/>"
    for k in range(10):
        a = 2 * math.pi * k / 10
        L = 20 if k % 2 == 0 else 13
        x1, y1 = 22 + math.cos(a) * L, 22 + math.sin(a) * L
        xa, ya = 22 + math.cos(a + 0.16) * 6, 22 + math.sin(a + 0.16) * 6
        xb, yb = 22 + math.cos(a - 0.16) * 6, 22 + math.sin(a - 0.16) * 6
        o += f"<path d='M{f(xa)} {f(ya)} L{f(x1)} {f(y1)} L{f(xb)} {f(yb)} Z' fill='#FFF6C8' opacity='.9'/>"
    o += "<circle cx='22' cy='22' r='9' fill='none' stroke='#FFFFFF' stroke-width='1.6' opacity='.8'/>"
    return doc(44, 44, o, defs=defs)


def mane_svg(layer=0):
    """たてがみ（第4.93版：流れる 毛の 房を 銅と 真ちゅうの うすい 板で）：首の 上の 線から うしろ（き甲の 方）へ なびいて 首の 横に たれる 房を、
       き甲 → うなじ の 順に 重ねる（頭に 近い 房が 上）。layer 0＝房の うらの 暗い かげ（首の 上の ふちの 外に のぞく 厚み）・1＝房"""
    o = ''
    n = 11
    locks = []
    for k in range(n):
        t0 = 0.04 + 0.92 * k / n
        t1 = 0.04 + 0.92 * (k + 1.7) / n
        t1 = min(t1, 0.995)
        a, b = crest_at(t0), crest_at(t1)
        tx, ty = b[0] - a[0], b[1] - a[1]
        tl = math.hypot(tx, ty) or 1
        tx, ty = tx / tl, ty / tl
        nx, ny = ty, -tx
        if ny > 0:
            nx, ny = -nx, -ny                                             # 首の 外がわ（上）
        tm = (t0 + t1) / 2
        prof = 0.6 + 0.4 * math.sin(math.pi * (0.1 + 0.8 * tm))
        L = (15.5 + 6.5 * prof) * (1.08 if k % 3 == 1 else 0.92 if k % 3 == 2 else 1.0)
        dx, dy = -tx * 0.86 - nx * 0.5, -ty * 0.86 - ny * 0.5              # うしろへ なびいて 首の 横へ
        dl = math.hypot(dx, dy)
        dx, dy = dx / dl, dy / dl
        lift = 1.4 if layer == 0 else 0.0
        A = (a[0] + nx * (1.0 + lift), a[1] + ny * (1.0 + lift))
        Bp = (b[0] + nx * (1.4 + lift), b[1] + ny * (1.4 + lift))
        tip = (A[0] + dx * L - nx * (2.0 - lift), A[1] + dy * L - ny * (2.0 - lift))
        # 外がわの ふち（B → 先）は ふくらむ・内がわ（先 → A）は へこむ
        c1 = (Bp[0] + dx * L * 0.45 + nx * 4.2, Bp[1] + dy * L * 0.45 + ny * 4.2)
        c2 = (tip[0] + nx * 2.2 - dx * 3.0, tip[1] + ny * 2.2 - dy * 3.0)
        c3 = (A[0] + dx * L * 0.55 - nx * 1.2, A[1] + dy * L * 0.55 - ny * 1.2)
        locks.append((k, A, Bp, tip, c1, c2, c3, nx, ny, dx, dy, L))
    for k, A, Bp, tip, c1, c2, c3, nx, ny, dx, dy, L in locks:           # き甲 → うなじ（頭に 近い 房が 上）
        if layer == 0:
            fill, edge = mix(CU['dd'], '#1E1410', 0.15), CU['dd']
        else:
            fill, edge = (CU['m'], CU['dd']) if k % 2 == 0 else (BR['m'], BR['dd'])
        o += (f"<path d='M{f(Bp[0])} {f(Bp[1])} Q{f(c1[0])} {f(c1[1])} {f(tip[0])} {f(tip[1])} Q{f(c3[0])} {f(c3[1])} {f(A[0])} {f(A[1])} Z' "
              f"fill='{fill}' stroke='{edge}' stroke-width='.8' stroke-linejoin='round'/>")
        if layer:
            hlc = CU['hl'] if k % 2 == 0 else BR['hl']
            m0 = ((A[0] + Bp[0]) / 2 + nx * 0.6, (A[1] + Bp[1]) / 2 + ny * 0.6)
            o += (f"<path d='M{f(m0[0])} {f(m0[1])} Q{f(m0[0] + dx * L * 0.5 + nx * 1.6)} {f(m0[1] + dy * L * 0.5 + ny * 1.6)} {f(tip[0] * 0.7 + m0[0] * 0.3)} {f(tip[1] * 0.7 + m0[1] * 0.3)}' "
                  f"fill='none' stroke='{hlc}' stroke-width='.9' stroke-linecap='round' opacity='.75'/>")
            o += (f"<path d='M{f(A[0] * 0.6 + Bp[0] * 0.4)} {f(A[1] * 0.6 + Bp[1] * 0.4)} Q{f(c3[0] + nx * 0.8)} {f(c3[1] + ny * 0.8)} {f(tip[0] * 0.85 + A[0] * 0.15)} {f(tip[1] * 0.85 + A[1] * 0.15)}' "
                  f"fill='none' stroke='{edge}' stroke-width='.6' stroke-linecap='round' opacity='.6'/>")
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


def leg_parts(front, far):
    """足の 部品（関節の 順）：前＝前腕・管・つなぎ・ひづめ／うしろ＝もも・すね・管・つなぎ・ひづめ"""
    if front:
        return [('fa', seg_forearm(far)), ('cn', seg_cannon(True, far)), ('ps', seg_pastern(far)), ('hf', seg_hoof(far))]
    return [('th', seg_thigh(far)), ('gs', seg_gaskin(far)), ('cn', seg_cannon(False, far)), ('ps', seg_pastern(far)), ('hf', seg_hoof(far))]


def leg_lens(front):
    return [LA, LB, LP] if front else [LF, LG, LC, LP]


def banner(B):
    still = B.get('still')
    alt = ('夕ぐれの工場の町の石だたみを、真ちゅうと銅でできた機械仕掛けの馬が速足で走るイラスト。本物の馬のような頭と首、流れるたてがみ。'
           '肩と腰の大きな歯車が回って連結棒が回り、ひざと飛節のある本物の馬と同じ形の足が動く。のぞき窓の中でも歯車が回り、えんとつと鼻から蒸気がしゅっと出る。'
           '16秒に1回オーバーヒートして体が赤く熱くなり、圧力計の針がふり切れて、背中のえんとつが爆発してふたが飛び、口をぱっくりあけて右へ光線をうつ（光はゆっくり明るくなって消える）。'
           '空に飛行船、左上と右上に大きな歯車')
    html = f'<div class="gww" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('gwSky', sky_svg())
    html += f'<i class="gwFar" style="background-image:url(&quot;{durl(skyline_svg())}&quot;)"></i>'
    html += '<i class="gwAir">' + img('gwAs', airship_svg()) + img('gwPr', prop_svg()) + '</i>'
    html += f'<i class="gwMid" style="background-image:url(&quot;{durl(mid_svg())}&quot;)"></i>'
    html += img('gwG1', gear_svg(46, 22, BR, spokes=6)) + img('gwG2', gear_svg(30, 15, CU, spokes=5)) + img('gwG3', gear_svg(20, 11, BR, spokes=0))
    html += f'<i class="gwRd" style="background-image:url(&quot;{durl(road_svg())}&quot;)"></i>'
    html += '<i class="gwSh"></i>'
    # 馬（体ごと 少し 上下）。足は 関節ごとの 入れもの（.j0 → .j1 → …：本物の 馬の 関節・LEG_PARTS）
    def leg(nm, far):
        parts = leg_parts(nm[0] == 'f', far)
        o = f'<i class="gwL {nm}">'
        close = ''
        for j, (cls, (svg, ox_, oy_, w_, h_)) in enumerate(parts):
            o += f'<i class="j{j}">' + img(cls, svg)
            if nm[0] == 'f' and cls == 'cn':
                o += img('kg', gear_svg(5.2, 8, dark(BR) if far else BR, spokes=0, size=14))
            close += '</i>'
        return o + close + '</i>'
    h = '<i class="gwH">' + img('gwHa', halo_svg())
    for nm in ('hr', 'fr'):
        h += leg(nm, True)
    h += img('gwTl', tail_svg()) + img('gwMb', mane_svg(0)) + img('gwBd', body_svg()) + img('gwHt', heat_svg()) + img('gwCp', cap_svg()) + img('gwMn', mane_svg(1))
    h += '<i class="gwWn">' + img('gwWg1', gear_svg(9, 10, BR, spokes=4, size=22)) + img('gwWg2', gear_svg(6, 8, CU, spokes=0, size=16)) + img('gwWg3', gear_svg(5, 7, BR, spokes=0, size=14)) + '</i>'
    h += img('gwWr', window_svg()) + '<i class="gwNw">' + img('gwNd', needle_svg()) + '</i>'
    # 頭：上げる 入れもの（オーバーヒート）→ うなずく 入れもの → 下あご（ほおの 歯車で ひらく：口の 中・あご・熱）・上の 頭・熱・ためる 光・光線
    h += ('<i class="gwHw"><i class="gwHn">' + img('gwMo c', head_part('mouth_c')) + '<i class="gwJb">' + img('gwMo b', head_part('mouth_b')) + '</i>'
          + '<i class="gwJw">' + img('gwMo a', head_part('mouth_a')) + img('gwJa', head_part('jaw')) + img('gwJh', head_part('heat_j')) + '</i>'
          + img('gwMl', head_part('mouth_l'))                                                 # 第4.113版：口の 中の 光（あごの 上・上の 頭の 下）
          + img('gwHd', head_part('upper')) + img('gwHh', head_part('heat_u')) + img('gwCg', charge_svg())
          + '<i class="gwBm">' + img('gwBg', beam_svg()) + img('gwBc', beam_svg(True)) + img('gwSp', splash_svg()) + '</i></i></i>')
    for nm in ('hl', 'fl'):
        h += leg(nm, False)
    h += img('gwDh', gear_svg(13, 12, BR, spokes=5, size=30)) + img('gwDs', gear_svg(13, 12, BR, spokes=5, size=30))
    h += img('gwRod', rod_svg())
    h += '</i>'
    html += h
    # 蒸気
    for k in range(3):
        html += img(f'gwPf p{k}', puff_svg(3 + k))
    html += img('gwJt', jet_svg())
    # オーバーヒート：すきまから しゅー（4か所）・えんとつの 爆発（火の玉・黒い けむり・火の 粉）
    for k in range(4):
        html += img(f'gwHs s{k}', jet_svg())
    for k in range(5):
        html += img(f'gwSm m{k}', puff_svg(11 + k, 40, 30, '#6A605C', '#4A423F'))
    html += img('gwFb', fireball_svg())
    for k in range(6):
        html += img(f'gwSk k{k}', spark_svg())
    html += '</div>'

    # ---- CSS
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
           '.gww .gwBd,.gww .gwHt{left:0;top:0;width:390px;height:160px}'
           '.gww .gwTl{left:126px;top:68px;width:34px;height:42px;transform-origin:26px 4px;animation:gwTail ' + f(T) + 's ease-in-out infinite}'
           '.gww .gwMb,.gww .gwMn{left:0;top:0;width:390px;height:160px;transform-origin:250px 46px;animation:gwMane ' + f(T) + 's ease-in-out infinite}'
           '.gww .gwMb{animation-delay:-' + f(T * 0.18, 3) + 's}'
           '.gww .gwWn{left:183.5px;top:70.5px;width:25px;height:25px;border-radius:50%;overflow:hidden}'
           '.gww .gwWg1{left:-1px;top:-2px;width:22px;height:22px;animation:gwRot ' + f(T * 2) + 's linear infinite}'
           '.gww .gwWg2{left:13px;top:10px;width:16px;height:16px;animation:gwRotR ' + f(T * 2 * 8 / 10) + 's linear infinite}'
           '.gww .gwWg3{left:2px;top:14px;width:14px;height:14px;animation:gwRotR ' + f(T * 2 * 7 / 10) + 's linear infinite}'
           '.gww .gwWr{left:181px;top:68px;width:30px;height:30px}'
           '.gww .gwNw{left:222px;top:84px;width:0;height:0;transform-origin:0 0}'
           '.gww .gwNd{left:-6px;top:-6px;width:12px;height:12px;animation:gwNeedle 2.6s ease-in-out infinite}'
           '.gww .gwDh{left:' + f(HP[0] - 15) + 'px;top:' + f(HP[1] - 15) + 'px;width:30px;height:30px;animation:gwRot ' + f(T) + 's linear infinite}'
           '.gww .gwDs{left:' + f(SH[0] - 15) + 'px;top:' + f(SH[1] - 15) + 'px;width:30px;height:30px;animation:gwRot ' + f(T) + 's linear infinite}'
           '.gww .gwRod{left:' + f(HP[0] - 4) + 'px;top:' + f(HP[1] - 5) + 'px;width:' + f(SH[0] - HP[0] + 8) + 'px;height:' + f(10 + max(0, SH[1] - HP[1])) + 'px;animation:gwRod ' + f(T) + 's linear infinite}'
           # 足：関節の 所に はば 0 の 入れもの（.j0 は 腰／ひじ・つぎは 1つ上の 骨の 先）。中の 絵は 自分の 関節を 原点に
           '.gww .gwL,.gww .gwL i{width:0;height:0;transform-origin:0 0}'
           '.gww .gwL .kg{left:-7px;top:-7px;width:14px;height:14px;animation:gwRotR ' + f(T / 2) + 's linear infinite}'
           # 蒸気
           '.gww .gwPf{left:204px;top:20px;width:34px;height:26px;opacity:0;transform-origin:50% 80%;animation:gwPuff 3.6s ease-out infinite;will-change:transform,opacity}'
           '.gww .gwPf.p1{animation-delay:.28s}.gww .gwPf.p2{animation-delay:.56s}'
           f'.gww .gwJt{{left:{f(hpt(43, 6)[0] - 2)}px;top:{f(hpt(43, 6)[1] - 9)}px;width:70px;height:18px;opacity:0;transform-origin:0 50%;animation:gwJet {f(OH_S)}s ease-out infinite;will-change:transform,opacity}}')
    # 頭：上げる 入れもの・うなずく 入れもの（どちらも 舞台の 座標・軸は うなずく 軸）・下あご（ほおの 歯車が 軸）
    bx, by, bw, bh = HEAD_BOX
    hg = hpt(*HINGE)
    mo = hpt(*MOUTH)
    css += (f'.gww .gwHw,.gww .gwHn,.gww .gwJw,.gww .gwJb,.gww .gwBm{{width:0;height:0}}'
            f'.gww .gwHw{{left:0;top:0;transform-origin:{HEAD_PIV[0]}px {HEAD_PIV[1]}px;animation:gwTilt {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwHn{{left:0;top:0;transform-origin:{HEAD_PIV[0]}px {HEAD_PIV[1]}px;animation:gwHead {f(T)}s ease-in-out infinite}}'
            f'.gww .gwJw,.gww .gwJb{{left:0;top:0;transform-origin:{f(hg[0])}px {f(hg[1])}px;animation:gwJaw {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwJb{{animation-name:gwJawH}}'
            f'.gww .gwHd,.gww .gwHh,.gww .gwMo,.gww .gwJa,.gww .gwJh,.gww .gwMl{{left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px}}'
            f'.gww .gwMl{{opacity:0;animation:gwMouthL {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwHh,.gww .gwJh{{opacity:0;animation:gwHeat {f(OH_S)}s linear infinite}}'
            f'.gww .gwCg{{left:{f(mo[0] - 16)}px;top:{f(mo[1] - 16)}px;width:32px;height:32px;opacity:0;animation:gwCharge {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwBm{{left:{f(mo[0])}px;top:{f(mo[1])}px;transform:rotate({f(BEAM_DIR - OH_TILT)}deg);transform-origin:0 0}}'
            # 第4.113版：もやは 口から 前だけ（left 0・左の はしは やわらかく）・しんは 口の 中 5px から
            f'.gww .gwBg{{left:0;top:-17px;width:{f(BEAM_L)}px;height:34px;transform-origin:0 50%;opacity:0;animation:gwBeamG {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwBc{{left:-5px;top:-6px;width:{f(BEAM_L)}px;height:12px;transform-origin:5px 50%;opacity:0;animation:gwBeamC {f(OH_S)}s ease-in-out infinite}}'
            f'.gww .gwSp{{left:{f(66 - 22)}px;top:-22px;width:44px;height:44px;opacity:0;animation:gwSplash {f(OH_S)}s ease-in-out infinite}}'
            # 熱（体）・もや・ふた・圧力計の 針
            f'.gww .gwHt{{opacity:0;animation:gwHeat {f(OH_S)}s linear infinite}}'
            f'.gww .gwHa{{left:113px;top:26px;width:184px;height:104px;opacity:0;animation:gwHalo {f(OH_S)}s linear infinite}}'
            f'.gww .gwCp{{left:211.5px;top:40px;width:19px;height:8px;animation:gwCap {f(OH_S)}s linear infinite}}'
            f'.gww .gwNw{{animation:gwGauge {f(OH_S)}s ease-in-out infinite}}'
            # 爆発
            f'.gww .gwFb{{left:{f(CHIM[0] - 24)}px;top:{f(CHIM[1] - 42)}px;width:48px;height:46px;transform-origin:50% 92%;opacity:0;animation:gwFire {f(OH_S)}s ease-out infinite}}'
            '.gww .gwSm{left:' + f(CHIM[0] - 20) + 'px;top:' + f(CHIM[1] - 24) + 'px;width:40px;height:30px;opacity:0;will-change:transform,opacity}'
            '.gww .gwSk{left:' + f(CHIM[0] - 3) + 'px;top:' + f(CHIM[1] - 4) + 'px;width:6px;height:6px;opacity:0}'
            '.gww .gwHs{width:28px;height:8px;opacity:0;transform-origin:0 50%}')

    def ev(name, pts):
        return cycle_kf(name, [(OH_AT + e, d) for e, d in pts], OH_S)
    # 熱：ゆっくり 赤く（2.4秒）→ 光線の 間 そのまま → ゆっくり さめる（2秒）
    css += ev('gwHeat', [(0, 'opacity:0'), (0.3, 'opacity:.04'), (1.2, 'opacity:.3'), (1.9, 'opacity:.65'), (2.4, 'opacity:.92'), (3.2, 'opacity:1'), (5.0, 'opacity:1'), (7.2, 'opacity:0')])
    css += ev('gwHalo', [(0, 'opacity:0'), (0.8, 'opacity:0'), (2.4, 'opacity:.75'), (5.0, 'opacity:.8'), (7.0, 'opacity:0')])
    # 圧力計の 針：だんだん 上がって ふるえ、爆発で ふり切れる → さめると もどる（中の 針の ゆれは そのまま）
    css += ev('gwGauge', [(0, 'transform:rotate(0deg)'), (0.6, 'transform:rotate(8deg)'), (1.1, 'transform:rotate(34deg)'), (1.35, 'transform:rotate(28deg)'), (1.6, 'transform:rotate(48deg)'),
                          (1.8, 'transform:rotate(43deg)'), (2.0, 'transform:rotate(62deg)'), (2.15, 'transform:rotate(57deg)'), (2.3, 'transform:rotate(76deg)'), (2.42, 'transform:rotate(98deg)'),
                          (2.6, 'transform:rotate(91deg)'), (2.8, 'transform:rotate(97deg)'), (3.0, 'transform:rotate(92deg)'), (3.5, 'transform:rotate(97deg)'), (4.0, 'transform:rotate(93deg)'),
                          (4.5, 'transform:rotate(97deg)'), (5.0, 'transform:rotate(94deg)'), (5.6, 'transform:rotate(60deg)'), (6.3, 'transform:rotate(0deg)')])
    # えんとつの ふた：ふるえて → 爆発で 回りながら 上へ 飛ぶ（画面の 外）→ 3秒 あとに 回りながら 落ちて きて のる（はねる）
    cap = [(0, 'transform:translate(0,0) rotate(0deg)'), (1.4, 'transform:translate(0,0) rotate(0deg)'), (1.55, 'transform:translate(.5px,-.6px) rotate(3deg)'),
           (1.7, 'transform:translate(-.4px,0) rotate(-2deg)'), (1.85, 'transform:translate(.6px,-.8px) rotate(4deg)'), (2.0, 'transform:translate(-.5px,-.3px) rotate(-3deg)'),
           (2.15, 'transform:translate(.6px,-1px) rotate(5deg)'), (2.3, 'transform:translate(-.4px,-.6px) rotate(-4deg)'),
           (2.4, 'transform:translate(0,-1px) rotate(0deg);animation-timing-function:ease-out'), (3.0, 'transform:translate(-26px,-76px) rotate(-270deg)'),
           (6.0, 'transform:translate(2px,-76px) rotate(-180deg);animation-timing-function:ease-in'), (6.42, 'transform:translate(0,0) rotate(0deg);animation-timing-function:ease-out'),
           (6.56, 'transform:translate(0,-6px) rotate(0deg);animation-timing-function:ease-in'), (6.7, 'transform:translate(0,0) rotate(0deg);animation-timing-function:ease-out'),
           (6.78, 'transform:translate(0,-1.6px) rotate(0deg);animation-timing-function:ease-in'), (6.86, 'transform:translate(0,0) rotate(0deg)')]
    css += ev('gwCap', cap)
    # 火の玉：0.32秒 かけて 明るく ふくらみ → 上へ 上がって けむりに なって 消える
    css += ev('gwFire', [(0, 'opacity:0;transform:scale(.2)'), (2.38, 'opacity:0;transform:scale(.2)'), (2.7, 'opacity:1;transform:scale(1.3)'),
                         (3.05, 'opacity:.95;transform:translateY(-6px) scale(1.55)'), (3.5, 'opacity:.6;transform:translateY(-14px) scale(1.7)'), (3.95, 'opacity:0;transform:translateY(-22px) scale(1.85)')])
    for k in range(5):                                                   # 黒い けむり：ふくらんで うしろ（左）上へ
        t0 = 2.6 + 0.08 * k
        dx = (-14, -30, 6, -46, -20)[k]
        css += (f'.gww .gwSm.m{k}{{animation:gwSm{k} {f(OH_S)}s ease-out infinite}}'
                + ev(f'gwSm{k}', [(0, 'opacity:0;transform:translate(0,0) scale(.4)'), (t0, 'opacity:0;transform:translate(0,0) scale(.4)'),
                                  (t0 + 0.3, f'opacity:.9;transform:translate({f(dx * 0.3)}px,-10px) scale(1)'),
                                  (t0 + 1.4, f'opacity:.75;transform:translate({dx}px,{-30 - 6 * k}px) scale(1.9)'),
                                  (t0 + 2.8, f'opacity:0;transform:translate({f(dx * 1.6)}px,{-48 - 8 * k}px) scale(2.6)')]))
    R = rnd(29)
    for k in range(6):                                                   # 火の 粉：放物線で 飛び 散る
        vx = (-1 if k % 2 else 1) * R.uniform(14, 44)
        vy = R.uniform(18, 34)
        st = [(0, 'opacity:0;transform:translate(0,0)'), (2.4, 'opacity:0;transform:translate(0,0)'), (2.42, 'opacity:1;transform:translate(0,0)')]
        for i in range(1, 7):
            u = i / 6
            x, y = vx * u, -vy * 4 * u * (1 - u) + 30 * u * u
            st.append((2.42 + 1.0 * u, f'opacity:{f(1 if u < 0.7 else (1 - u) / 0.3)};transform:translate({f(x)}px,{f(y)}px)'))
        css += f'.gww .gwSk.k{k}{{animation:gwSk{k} {f(OH_S)}s linear infinite}}' + ev(f'gwSk{k}', st)
    # すきまから しゅー（だんだん 熱く なる 間）・さめる ときに 2か所
    jets = [((172, 63), -128, (0.9, 1.7, 5.9)), ((237, 63), -62, (1.25, 2.05, 6.2)), ((192, 101), 152, (1.5, 2.2)), ((262, 46), -36, (1.05, 1.85))]
    for k, ((x, y), ang, times) in enumerate(jets):
        st = [(0, f'opacity:0;transform:rotate({ang}deg) scaleX(.2)')]
        for t0 in times:
            big = 1.5 if t0 > 5 else 1.0
            st += [(t0, f'opacity:0;transform:rotate({ang}deg) scaleX(.2)'), (t0 + 0.06, f'opacity:.9;transform:rotate({ang}deg) scaleX({f(0.8 * big)})'),
                   (t0 + 0.4, f'opacity:0;transform:rotate({ang}deg) scaleX({f(1.3 * big)})')]
        css += f'.gww .gwHs.s{k}{{left:{x}px;top:{y - 4}px;animation:gwHs{k} {f(OH_S)}s ease-out infinite}}' + ev(f'gwHs{k}', st)
    # 頭を 上げて（ふた が 飛んだ あと）→ 口を ぱっくり → ためる 光 → 光線（0.3秒 かけて 明るく）→ 消えて（0.35秒）→ 口を とじて 頭を もどす
    css += ev('gwTilt', [(0, 'transform:rotate(0deg)'), (2.7, 'transform:rotate(0deg)'), (3.05, f'transform:rotate({f(OH_TILT)}deg)'), (3.8, f'transform:rotate({f(OH_TILT - 1)}deg)'),
                         (4.4, f'transform:rotate({f(OH_TILT + 0.6)}deg)'), (5.0, f'transform:rotate({f(OH_TILT - 0.8)}deg)'), (5.4, f'transform:rotate({f(OH_TILT)}deg)'), (5.95, 'transform:rotate(0deg)')])
    jaw = [(0, 0), (2.85, 0), (3.12, JAW_MAX), (3.6, JAW_MAX - 2), (4.1, JAW_MAX), (4.6, JAW_MAX - 2), (5.1, JAW_MAX), (5.32, JAW_MAX), (5.6, 0)]
    css += ev('gwJaw', [(e, f'transform:rotate({f(a)}deg)') for e, a in jaw])
    css += ev('gwJawH', [(e, f'transform:rotate({f(a / 2)}deg)') for e, a in jaw])        # 口の 中の まん中の 1まい（半分の 角度）
    css += ev('gwCharge', [(0, 'opacity:0;transform:scale(.3)'), (3.0, 'opacity:0;transform:scale(.3)'), (3.32, 'opacity:1;transform:scale(1.1)'), (3.6, 'opacity:.95;transform:scale(.95)'),
                           (4.0, 'opacity:1;transform:scale(1.12)'), (4.4, 'opacity:.95;transform:scale(1)'), (4.8, 'opacity:1;transform:scale(1.12)'), (5.15, 'opacity:.95;transform:scale(1)'),
                           (5.5, 'opacity:0;transform:scale(.5)')])
    css += ev('gwMouthL', [(0, 'opacity:0'), (3.1, 'opacity:0'), (3.4, 'opacity:1'), (5.2, 'opacity:1'), (5.4, 'opacity:0')])   # 口の 中の 光（第4.113版）
    css += ev('gwBeamG', [(0, 'opacity:0;transform:scale(0,1)'), (3.22, 'opacity:0;transform:scale(0,1)'), (3.52, 'opacity:.85;transform:scale(1,1)'), (3.9, 'opacity:.82;transform:scale(1,.93)'),
                          (4.3, 'opacity:.85;transform:scale(1,1.06)'), (4.7, 'opacity:.82;transform:scale(1,.93)'), (5.15, 'opacity:.85;transform:scale(1,1)'), (5.5, 'opacity:0;transform:scale(1,.3)')])
    css += ev('gwBeamC', [(0, 'opacity:0;transform:scale(0,1)'), (3.22, 'opacity:0;transform:scale(0,1)'), (3.52, 'opacity:1;transform:scale(1,1)'), (3.9, 'opacity:1;transform:scale(1,.9)'),
                          (4.3, 'opacity:1;transform:scale(1,1.05)'), (4.7, 'opacity:1;transform:scale(1,.9)'), (5.15, 'opacity:1;transform:scale(1,1)'), (5.48, 'opacity:0;transform:scale(1,.2)')])
    css += ev('gwSplash', [(0, 'opacity:0;transform:scale(.3) rotate(0deg)'), (3.35, 'opacity:0;transform:scale(.3) rotate(0deg)'), (3.65, 'opacity:1;transform:scale(1.05) rotate(20deg)'),
                           (4.0, 'opacity:.9;transform:scale(.92) rotate(40deg)'), (4.4, 'opacity:1;transform:scale(1.08) rotate(60deg)'), (4.8, 'opacity:.9;transform:scale(.92) rotate(80deg)'),
                           (5.15, 'opacity:1;transform:scale(1.04) rotate(100deg)'), (5.5, 'opacity:0;transform:scale(.6) rotate(120deg)')])
    # 鼻の 蒸気：16秒に 2回（オーバーヒートの ない ころ）
    jet0, jet1, jet2 = 'opacity:0;transform:scaleX(.1) translateY(0)', 'opacity:.95;transform:scaleX(1) translateY(1px)', 'opacity:0;transform:scaleX(1.25) translateY(4px)'
    css += cycle_kf('gwJet', [(1.4, jet0), (1.58, jet1), (2.26, jet2), (13.0, jet0), (13.18, jet1), (13.86, jet2)], OH_S)
    for nm in LEGS:
        piv = SH if nm[0] == 'f' else HP
        parts = leg_parts(nm[0] == 'f', nm in ('hr', 'fr'))
        lens = leg_lens(nm[0] == 'f')
        css += f'.gww .gwL.{nm}{{left:{f(piv[0])}px;top:{f(piv[1])}px}}'
        for j, (cls, (svg, ox_, oy_, w_, h_)) in enumerate(parts):
            sel = f'.gww .gwL.{nm} ' + ' > '.join(f'.j{k}' for k in range(j + 1))
            top = 0 if j == 0 else lens[j - 1]
            css += f'{sel}{{left:0;top:{f(top, 2)}px;animation:gwJ{nm}{j} {f(T)}s linear infinite}}'
            css += f'{sel} > .{cls}{{left:{f(-ox_)}px;top:{f(-oy_)}px;width:{f(w_)}px;height:{f(h_)}px}}'
        for j, arr in enumerate(leg_keys(nm)):
            css += kf(f'gwJ{nm}{j}', [(100 * i / NS, f'transform:rotate({f(a, 2)}deg)') for i, a in enumerate(arr)])
    css += kf('gwBob', [(100 * i / NS, f'transform:translateY({f(bob(i / NS), 2)}px)') for i in range(NS + 1)])
    css += kf('gwRod', [(100 * i / NS, f'transform:translate({f(CRANK * math.cos(2 * math.pi * i / NS + math.pi), 2)}px,{f(CRANK * math.sin(2 * math.pi * i / NS + math.pi), 2)}px)') for i in range(NS + 1)])
    css += (kf('gwRot', [(0, 'transform:rotate(0)'), (100, 'transform:rotate(360deg)')])
            + kf('gwRotR', [(0, 'transform:rotate(0)'), (100, 'transform:rotate(-360deg)')])
            + kf('gwFar', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-390px)')])
            + kf('gwMid', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-195px)')])
            + kf('gwRoad', [(0, 'transform:translateX(0)'), (100, f'transform:translateX(-{ROAD_W}px)')])
            + kf('gwAir', [(0, 'transform:translate(400px,0)'), (50, 'transform:translate(150px,5px)'), (100, 'transform:translate(-100px,0)')])
            + kf('gwProp', [(0, 'transform:scaleY(1)'), (50, 'transform:scaleY(.2)'), (100, 'transform:scaleY(1)')])
            + kf('gwHead', [(0, 'transform:rotate(-1.6deg)'), (25, 'transform:rotate(1.8deg)'), (50, 'transform:rotate(-1.6deg)'), (75, 'transform:rotate(1.8deg)'), (100, 'transform:rotate(-1.6deg)')])
            + kf('gwMane', [(0, 'transform:rotate(0deg)'), (25, 'transform:rotate(.7deg)'), (50, 'transform:rotate(0deg)'), (75, 'transform:rotate(.7deg)'), (100, 'transform:rotate(0deg)')])
            + kf('gwTail', [(0, 'transform:rotate(-7deg)'), (50, 'transform:rotate(6deg)'), (100, 'transform:rotate(-7deg)')])
            + kf('gwNeedle', [(0, 'transform:rotate(-30deg)'), (40, 'transform:rotate(18deg)'), (55, 'transform:rotate(8deg)'), (70, 'transform:rotate(22deg)'), (100, 'transform:rotate(-30deg)')])
            # えんとつの 蒸気：1つ 1.6秒（3.6秒の うち 44%）。ふくらんで うしろ（左）上へ 流れて 消える
            + kf('gwPuff', [(0, 'opacity:0;transform:translate(0,2px) scale(.25)'), (4, 'opacity:.95;transform:translate(-2px,-3px) scale(.5)'),
                            (24, 'opacity:.7;transform:translate(-24px,-14px) scale(1.15)'), (44, 'opacity:0;transform:translate(-52px,-24px) scale(1.7)'),
                            (100, 'opacity:0;transform:translate(-52px,-24px) scale(1.7)')]))
    if still:
        css += reduced('.gww>*:not(.bnr)')
    return html, css


def cycle_kf(name, stops, total):
    """[(秒, 宣言)] → 1回り total 秒の keyframes（0% と 100% は 最初の 形）"""
    stops = sorted(stops, key=lambda q: q[0])
    first = stops[0][1]
    lst = [(0, first)] + [(max(0.0, min(100.0, 100 * t / total)), d) for t, d in stops] + [(100, first)]
    return kf(name, lst)


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
    alt='夕ぐれの工場の町の石だたみを、真ちゅうと銅でできた機械仕掛けの馬（本物の馬のような頭と首・流れるたてがみ・ひざと飛節のある足）が速足で走る。肩と腰の大きな歯車が回り、えんとつと鼻から蒸気がしゅっと出て、ときどきオーバーヒートしてえんとつが爆発し、口から光線をうつイラスト',
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
               pic='夕ぐれの 工場の 町・飛行船・石だたみ・大きな 歯車・真ちゅうと 銅の 機械仕掛けの 馬（本物の 馬の 頭と 首・流れる たてがみ・ひざと 飛節の ある 足で 速足・歯車と 連結棒・えんとつと 鼻から 蒸気）・'
                   '16秒に 1回 オーバーヒート（赤く 熱く なって 圧力計が ふり切れ、えんとつが 爆発して ふたが 飛び、口を ぱっくり あけて 右へ 光線）'),
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
