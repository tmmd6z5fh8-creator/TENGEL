"""壁紙パック ⑥恐竜時代（まさちゃんの 指定「火山と恐竜の横を、馬が並んで走る」）
   上の絵：むかしの 大地。左に けむりを はく 火山（溶岩の すじ）・右に 首の 長い 大きな 恐竜（歩いて いる）・空に 翼竜・
     シダと ソテツの しげみと 草を 食べる トリケラトプス・手前を 馬が 2頭 ならんで 走る（鹿毛 1・芦毛 2：pack/make/dino_art.py）。
   動き：馬は いつも ならんで 走る・地面（足あと・小石）と しげみが 流れる（遠いほど ゆっくり）・首の 長い 恐竜は 足を 動かして ならんで 歩き、
     首と しっぽを ゆっくり ゆらす・翼竜が はばたいて 横切る・ときどき 小さな 恐竜が 馬と ならんで 走って 追いこす・
     火山の けむりが もくもく 上がり、溶岩の あかりが ゆっくり ゆらぐ（強く 光らせない）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'dino'
RUN_S = 0.5        # ギャロップ 1回の 秒
GROUND_S = 2.5     # 手前の 地面が 1まい 流れる 秒（ひづめの 動きに 合わせる）
MID_S = 9.0        # しげみが 1まい 流れる 秒
WALK_S = 2.6       # 首の 長い 恐竜の 1歩（2歩で 1回り）
VX, VY = 84, 32    # 火山の 口
SAU = (232, 0, 168, 120)    # 首の 長い 恐竜の 部品の 箱（左上・はば・高さ）

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
    o += (f"<path d='M-14 112 C10 100 34 70 54 46 C62 36 70 32 {VX - 10} {VY} L{VX + 12} {VY} C{VX + 22} 34 {VX + 30} 44 {VX + 40} 56 "
          f"C{VX + 62} 80 {VX + 84} 100 {VX + 110} 112 Z' fill='url(#v)'/>")
    o += f"<path d='M{VX - 10} {VY} L{VX + 12} {VY} L{VX + 8} {VY + 4} L{VX - 6} {VY + 4} Z' fill='#2E2430'/>"
    o += f"<path d='M{VX + 12} {VY} C{VX + 22} 34 {VX + 30} 44 {VX + 40} 56 C{VX + 62} 80 {VX + 84} 100 {VX + 110} 112 L{VX + 70} 112 C{VX + 50} 92 {VX + 30} 66 {VX + 14} {VY + 8} Z' fill='#2E2430' opacity='.45'/>"
    for k in range(6):                                                   # 岩の すじ
        x = VX - 40 + k * 16
        o += f"<path d='M{x} {104 - k % 2 * 6} q6 -10 8 -22' fill='none' stroke='#3A2E38' stroke-width='1.2' opacity='.6'/>"
    # 溶岩の すじ（口から 下へ）
    lava = [(VX - 4, VY + 3, [(-6, 18), (-14, 36), (-12, 54), (-22, 76)]), (VX + 6, VY + 3, [(8, 16), (12, 34), (24, 52)])]
    for x0, y0, segs in lava:
        pts = [(x0, y0)] + [(x0 + dx, y0 + dy) for dx, dy in segs]
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


# ---- 首の 長い 恐竜（部品ごとの 絵・どれも 同じ 箱 SAU）：左向き・首は 左上へ のびる
SC, SCD, SCL, SCS = '#7E9E5E', '#5D7A44', '#B8C98A', '#6A8A4E'


def sau_part(name):
    bx, by, bw, bh = SAU
    T = lambda x, y: (x - bx, y - by)
    o = ''
    if name in ('legFF', 'legHF', 'legFN', 'legHN'):
        x = {'legFF': 300, 'legHF': 350, 'legFN': 292, 'legHN': 342}[name]
        col = SCD if name.endswith('F') else SC
        top = 78
        x0, y0 = T(x, top)
        o += (f"<path d='M{f(x0 - 7)} {f(y0)} L{f(x0 + 7)} {f(y0)} L{f(x0 + 6)} {f(y0 + 30)} Q{f(x0 + 7)} {f(y0 + 35)} {f(x0 + 3)} {f(y0 + 35)} "
              f"L{f(x0 - 5)} {f(y0 + 35)} Q{f(x0 - 8)} {f(y0 + 35)} {f(x0 - 7)} {f(y0 + 30)} Z' fill='{col}'/>")
        o += f"<path d='M{f(x0 - 6)} {f(y0 + 33)} h{f(10)}' stroke='{mix(col, '#2A2A1A', .35)}' stroke-width='1.2' stroke-dasharray='2 1.4'/>"
        if not name.endswith('F'):
            o += f"<path d='M{f(x0 - 5)} {f(y0 + 4)} V{f(y0 + 26)}' stroke='{SCL}' stroke-width='1.6' stroke-linecap='round' opacity='.45'/>"
    elif name == 'tail':
        p = [T(*q) for q in ((350, 62), (378, 66), (400, 78), (420, 92))]
        o += f"<path d='M{f(p[0][0])} {f(p[0][1] - 8)} C{f(p[1][0])} {f(p[1][1] - 8)} {f(p[2][0])} {f(p[2][1] - 4)} {f(p[3][0])} {f(p[3][1])} C{f(p[2][0] - 2)} {f(p[2][1] + 6)} {f(p[1][0])} {f(p[1][1] + 10)} {f(p[0][0])} {f(p[0][1] + 12)} Z' fill='{SC}'/>"
    elif name == 'shadow':
        sx, sy = T(322, 113.5)
        o += f"<ellipse cx='{f(sx)}' cy='{f(sy)}' rx='46' ry='3.8' fill='#4A3A1E' opacity='.26'/>"
    elif name == 'body':
        cx, cy = T(322, 70)
        o += f"<ellipse cx='{f(cx)}' cy='{f(cy)}' rx='46' ry='21' fill='{SC}'/>"
        o += f"<path d='M{f(cx - 40)} {f(cy + 8)} Q{f(cx)} {f(cy + 26)} {f(cx + 40)} {f(cy + 8)} Q{f(cx)} {f(cy + 18)} {f(cx - 40)} {f(cy + 8)} Z' fill='{SCL}' opacity='.8'/>"
        o += f"<path d='M{f(cx - 34)} {f(cy - 14)} Q{f(cx)} {f(cy - 26)} {f(cx + 34)} {f(cy - 14)}' fill='none' stroke='#9CBC78' stroke-width='3' stroke-linecap='round' opacity='.7'/>"
        R = rnd(9)
        for i in range(9):
            o += f"<ellipse cx='{f(cx - 28 + i * 7 + R.uniform(-2, 2))}' cy='{f(cy - 8 + R.uniform(-5, 5))}' rx='{f(R.uniform(2.4, 4))}' ry='{f(R.uniform(1.6, 2.6))}' fill='{SCS}' opacity='.75'/>"
    elif name == 'neck':
        b = T(298, 66)
        h = T(262, 20)
        o += (f"<path d='M{f(b[0] + 10)} {f(b[1] + 8)} C{f(b[0] - 4)} {f(b[1] - 6)} {f(h[0] + 14)} {f(h[1] + 22)} {f(h[0] + 6)} {f(h[1] + 6)} "
              f"L{f(h[0] - 2)} {f(h[1] + 8)} C{f(h[0] + 4)} {f(h[1] + 30)} {f(b[0] - 18)} {f(b[1] + 2)} {f(b[0] - 12)} {f(b[1] + 16)} Z' fill='{SC}'/>")
        o += f"<path d='M{f(b[0] - 12)} {f(b[1] + 12)} C{f(b[0] - 18)} {f(b[1])} {f(h[0] + 6)} {f(h[1] + 32)} {f(h[0])} {f(h[1] + 12)}' fill='none' stroke='{SCL}' stroke-width='3' opacity='.7'/>"
        # 頭（左向き・まるい 鼻・にっこり）
        o += (f"<path d='M{f(h[0] + 8)} {f(h[1] + 6)} C{f(h[0] + 8)} {f(h[1] - 6)} {f(h[0] - 2)} {f(h[1] - 8)} {f(h[0] - 10)} {f(h[1] - 5)} "
              f"C{f(h[0] - 18)} {f(h[1] - 3)} {f(h[0] - 19)} {f(h[1] + 5)} {f(h[0] - 13)} {f(h[1] + 7)} C{f(h[0] - 6)} {f(h[1] + 9)} {f(h[0] + 2)} {f(h[1] + 10)} {f(h[0] + 8)} {f(h[1] + 6)} Z' fill='{SC}'/>")
        o += f"<circle cx='{f(h[0] - 3)}' cy='{f(h[1] - 2)}' r='1.7' fill='#1E2414'/><circle cx='{f(h[0] - 3.5)}' cy='{f(h[1] - 2.6)}' r='.6' fill='#FFFFFF'/>"
        o += f"<path d='M{f(h[0] - 16)} {f(h[1] + 4)} Q{f(h[0] - 10)} {f(h[1] + 7)} {f(h[0] - 4)} {f(h[1] + 4)}' fill='none' stroke='#2E3A20' stroke-width='1' stroke-linecap='round'/>"
        o += f"<circle cx='{f(h[0] - 15)}' cy='{f(h[1] - 1)}' r='.8' fill='#2E3A20'/>"
    return doc(bw, bh, o)


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
def banner(B):
    near, far = B.get('near'), B.get('far')
    still = B.get('still')
    alt = ('むかしの大地で、けむりをはく火山と首の長い大きな恐竜・草を食べるトリケラトプス・空の翼竜の横を、鹿毛と芦毛の競走馬（ゼッケン1と2）が'
           'ならんで走るイラスト（馬はいつも走っていて、地面としげみが流れ、恐竜も歩き、火山のけむりが上がる）')
    html = f'<div class="dnw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('dnSky', sky_svg()) + img('dnGl', glow_svg())
    for k in range(6):
        html += img(f'dnPf p{k}', puff_svg())
    for k in range(2):
        html += f'<i class="dnPt q{k}">' + img('dnPb', ptero_svg()) + img('dnPw', wing_svg()) + '</i>'
    html += f'<i class="dnMd" style="background-image:url(&quot;{durl(mid_svg())}&quot;)"></i>'
    html += '<i class="dnSa">' + ''.join(img(f'dnS {k}', sau_part(k)) for k in ('shadow', 'legFF', 'legHF', 'tail', 'body', 'legFN', 'legHN', 'neck')) + '</i>'
    html += f'<i class="dnGd" style="background-image:url(&quot;{durl(ground_svg())}&quot;)"></i>'
    if far:
        html += '<i class="dnSd s2"></i><i class="dnH h2"><i></i></i>'
    html += '<i class="dnRx">' + ''.join(img(f'dnR {k}', runner_part(k)) for k in ('legF', 'body', 'legN')) + '</i>'
    if near:
        html += '<i class="dnSd s1"></i><i class="dnH h1"><i></i></i>'
    html += '</div>'

    bx, by, bw, bh = SAU
    css = ('.dnw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#E9DDB2}'
           '.dnw>*{position:absolute;display:block}'
           '.dnw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.dnw .dnSky{left:0;top:0;width:390px;height:160px}'
           f'.dnw .dnGl{{left:{VX - 30}px;top:{VY - 22}px;width:60px;height:40px;animation:dnGlow 3.8s ease-in-out infinite;will-change:opacity}}'
           '.dnw .dnPf{left:0;top:0;width:40px;height:32px;opacity:0;will-change:transform,opacity}'
           '.dnw .dnPt{left:0;top:0;width:40px;height:20px;will-change:transform}'
           '.dnw .dnPt>img{position:absolute;left:0;top:0;width:40px;height:20px}'
           '.dnw .dnPw{transform-origin:15px 10px;animation:dnFlap .7s ease-in-out infinite alternate}'
           f'.dnw .dnMd{{left:0;top:66px;width:{2 * W + 2}px;height:60px;background-size:{W}px 60px;background-repeat:repeat-x;animation:dnMid {MID_S}s linear infinite}}'
           f'.dnw .dnSa{{left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px;animation:dnBob {WALK_S / 2}s ease-in-out infinite}}'
           f'.dnw .dnSa>img{{position:absolute;left:0;top:0;width:{bw}px;height:{bh}px}}'
           f'.dnw .dnGd{{left:0;top:{H - 44}px;width:{2 * W + 2}px;height:44px;background-size:{W}px 44px;background-repeat:repeat-x;animation:dnGround {GROUND_S}s linear infinite}}')
    # 首の 長い 恐竜の 足（ななめの 組が いっしょ）・首・しっぽ
    for k, (px, delay) in (('legFN', (292, 0)), ('legHF', (350, 0)), ('legFF', (300, 0.5)), ('legHN', (342, 0.5))):
        css += f'.dnw .dnS.{k}{{transform-origin:{px - bx}px {78 - by}px;animation:dnLeg {WALK_S}s ease-in-out {f(-WALK_S * delay, 3)}s infinite}}'
    css += (f'.dnw .dnS.neck{{transform-origin:{298 - bx}px {70 - by}px;animation:dnNeck 5.2s ease-in-out infinite}}'
            f'.dnw .dnS.tail{{transform-origin:{352 - bx}px {66 - by}px;animation:dnTail 3.4s ease-in-out infinite}}')
    # 馬（2頭）：影は 体の 下の だ円（浮くと 小さく）
    for k, (cls, meta, delay, sy, dx, dy) in enumerate((('h1', near, 0.0, 146, -6, 0), ('h2', far, 0.17, 116, 46, -2))):
        if not meta:
            continue
        n, (cw, ch), (ax, ay) = meta['frames'], meta['cell'], meta['at']
        w, h = cw / 2, ch / 2
        ax, ay = ax + 2 * dx, ay + 2 * dy                                 # 2頭の 間を あける（おくの 馬は 少し 前・上）
        css += (f'.dnw .dnH.{cls}{{left:{f(ax / 2)}px;top:{f(ay / 2)}px;width:{f(w)}px;height:{f(h)}px;overflow:hidden}}'
                f'.dnw .dnH.{cls}>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({meta["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;'
                f'animation:dnRun{k + 1} {RUN_S}s steps({n}) {f(-delay, 3)}s infinite}}'
                + kf(f'dnRun{k + 1}', [(100, f'transform:translateX({f(-n * w)}px)')]))
        sc = 's1' if cls == 'h1' else 's2'
        css += (f'.dnw .dnSd.{sc}{{left:{f(ax / 2 + w * 0.24)}px;top:{sy - 4}px;width:{f(w * 0.56)}px;height:8px;border-radius:50%;'
                f'background:radial-gradient(closest-side,rgba(80,50,20,.45),rgba(80,50,20,0))}}')
    # 小さな 恐竜：16秒に 1回 うしろから 走って きて、馬を 追いこして 右へ（足は 0.32秒で 1歩）
    css += ('.dnw .dnRx{left:0;top:94px;width:60px;height:46px;animation:dnRace 16s linear infinite;will-change:transform}'
            '.dnw .dnRx>img{position:absolute;left:0;top:0;width:60px;height:46px}'
            '.dnw .dnR.body{animation:dnRBob .16s ease-in-out infinite alternate}'
            '.dnw .dnR.legN{transform-origin:29px 25px;animation:dnRLeg .32s linear infinite}'
            '.dnw .dnR.legF{transform-origin:29px 25px;animation:dnRLeg .32s linear -.16s infinite}'
            + kf('dnRace', [(0, 'transform:translate(-70px,0)'), (4, 'transform:translate(-70px,0)'), (34, 'transform:translate(420px,-3px)'), (100, 'transform:translate(420px,-3px)')])
            + kf('dnRBob', [(0, 'transform:translateY(0)'), (100, 'transform:translateY(-1.6px)')])
            + kf('dnRLeg', [(0, 'transform:rotate(-34deg)'), (50, 'transform:rotate(30deg)'), (100, 'transform:rotate(-34deg)')]))
    # けむり：火山の 口から 右上へ もくもく（6秒・1秒ずつ ずらす）
    for k in range(6):
        css += f'.dnw .dnPf.p{k}{{animation:dnPuff 6s ease-out {f(-k, 2)}s infinite}}'
    css += kf('dnPuff', [(0, f'opacity:0;transform:translate({VX - 20}px,{VY - 16}px) scale(.35)'), (10, f'opacity:.85;transform:translate({VX - 18}px,{VY - 26}px) scale(.55)'),
                         (60, f'opacity:.6;transform:translate({VX + 4}px,{VY - 52}px) scale(1.1)'), (100, f'opacity:0;transform:translate({VX + 30}px,{VY - 74}px) scale(1.6)')])
    # 翼竜：右から 左へ（14秒・18秒）
    for k, (sec, d, y0, y1, s) in enumerate(((14.0, 0.0, 26, 14, 1.0), (18.0, -7.0, 44, 34, 0.75))):
        css += f'.dnw .dnPt.q{k}{{animation:dnFly{k} {sec}s linear {d}s infinite}}'
        css += kf(f'dnFly{k}', [(0, f'transform:translate(410px,{y0}px) scale({s})'), (50, f'transform:translate(190px,{f((y0 + y1) / 2 - 6)}px) scale({s})'),
                                (100, f'transform:translate(-60px,{y1}px) scale({s})')])
    css += (kf('dnGlow', [(0, 'opacity:.55;transform:scale(.92)'), (50, 'opacity:.95;transform:scale(1.06)'), (100, 'opacity:.55;transform:scale(.92)')])
            + kf('dnFlap', [(0, 'transform:scaleY(1)'), (100, 'transform:scaleY(-.55)')])
            + kf('dnMid', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('dnGround', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('dnBob', [(0, 'transform:translateY(0)'), (50, 'transform:translateY(1.2px)'), (100, 'transform:translateY(0)')])
            + kf('dnLeg', [(0, 'transform:rotate(-11deg)'), (50, 'transform:rotate(11deg)'), (100, 'transform:rotate(-11deg)')])
            + kf('dnNeck', [(0, 'transform:rotate(-2.5deg)'), (50, 'transform:rotate(3.5deg)'), (100, 'transform:rotate(-2.5deg)')])
            + kf('dnTail', [(0, 'transform:rotate(-5deg)'), (50, 'transform:rotate(5deg)'), (100, 'transform:rotate(-5deg)')]))
    css += reduced('.dnw .dnSky,.dnw .dnGl,.dnw .dnPf,.dnw .dnPt,.dnw .dnMd,.dnw .dnSa,.dnw .dnGd,.dnw .dnSd,.dnw .dnH,.dnw .dnRx') if still else ''
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
    alt='むかしの大地で、けむりをはく火山と首の長い大きな恐竜・草を食べるトリケラトプス・空の翼竜の横を、鹿毛と芦毛の競走馬（ゼッケン1と2）がならんで走るイラスト',
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
               pic='けむりを はく 火山・首の 長い 大きな 恐竜（歩く）・トリケラトプス・翼竜・ならんで 走る 鹿毛と 芦毛の 馬'),
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
