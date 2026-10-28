"""壁紙パック ①海賊（まさちゃんの 指定「海賊船の甲板に、蹄鉄マークの海賊旗。宝箱の金貨がキラッと光って、波で船がゆれる」）
   上の絵：海賊船の 甲板。左に ふたの あいた 宝箱（金貨・宝石・真珠）・甲板を 歩きまわる 三角帽の 馬の 船長（pack/make/pirate_art.py）・右に 舵輪と 旗ざお。
     旗ざおの 上に 黒い 海賊旗（白い 蹄鉄と ぶっちがいの 骨）。手すりの むこうに 海・空・宝島。
   動き：船が 波で ゆれる（甲板は そのまま、手すりの むこうの 海と 空が かたむいて 上下する＝6秒）・旗が なびく・舵輪が ゆれに 合わせて 少し 回る・
     雲が 流れる・波が 流れる・かもめが 飛ぶ・宝箱の 金貨が キラッと 光る（小さな 光が 順に・強く 光らせない）
   第4.93版（まさちゃん「船の揺れの演出もう少し弱くして！ あと、8秒に一回海賊船が背景に通るようにして！ あと、馬は、ランダムに船を歩き回るようにして！」）：
     ゆれは 半分（かたむき 1.7°・上下 2px くらい・舵輪 ±7°）。8秒に 1回 小さな 海賊船（黒い 帆に 白い 蹄鉄）が 水平線の 近くを 通る
     （16秒で 右から 左・左から 右の 2回。少し 大きさと 高さを かえる・波で 上下に ゆれる）。
     船長は 40秒の 1回りの 中で 歩く（常歩の 12コマ・すべらない はやさ）・止まって まわりを 見る（前・見上げる・のぞきこむ）・くるっと 向きを かえる を
     ばらばらの 長さで（宝箱と 舵輪の うしろを 通る）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, box, rnd, reduced, fly_burst, fly_css, piece

ID = 'pirate'

# ---------------------------------------------------------------- 色
SKY = ('#4C9AD6', '#9AD2EF', '#FCE6BC')
SEA = ('#3A97C4', '#1E6E9E', '#174F7A')
WOOD = dict(l='#B98652', m='#8E5E34', d='#5E3A1E', dd='#3C2412', hi='#D9AD72')
GOLD = dict(l='#FFE58A', m='#F2C14E', d='#C8902A', dd='#8A5A14')
ROT = 1.7          # 船の ゆれ（度）：第4.93版 3.4 → 1.7（まさちゃん「もう少し弱くして！」）
BOB = (1.8, 1.0)   # ゆれの 上下（px：上・下）：第4.93版 (3.5, 2) → 半分くらい
WHEEL = (7, 6)     # 舵輪の 回る 角度（度）：第4.93版 (14, 12) → 半分
SHIP_T = 16.0      # 海賊船の 1回り（秒）：8秒に 1回 通る（右から 左・左から 右）
WALK_C = 1.25      # 船長の 歩く 1回り（秒：pirate_art.CYCLE と 同じ）
ROCK = 6.0         # ゆれの 1回り（秒）

# 世界（手すりの むこう：空・雲・島・海）は 舞台より 大きく（かたむけても すみが 見えない）。世界の 座標＝舞台の 座標 + (OX, OY)
OX, OY, WW, WH = 30, 34, 450, 214
HZ = 78            # 水平線（舞台の 座標）


def sky_svg():
    hz = HZ + OY
    defs = (f"<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{SKY[0]}'/><stop offset='.62' stop-color='{SKY[1]}'/>"
            f"<stop offset='1' stop-color='{SKY[2]}'/></linearGradient>"
            "<radialGradient id='g' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#FFF8D8' stop-opacity='.95'/><stop offset='.35' stop-color='#FFF1C0' stop-opacity='.55'/>"
            "<stop offset='1' stop-color='#FFE9B0' stop-opacity='0'/></radialGradient>"
            f"<linearGradient id='w' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{SEA[0]}'/><stop offset='.35' stop-color='{SEA[1]}'/><stop offset='1' stop-color='{SEA[2]}'/></linearGradient>")
    body = (f"<rect width='{WW}' height='{hz + 1}' fill='url(#s)'/>"
            f"<circle cx='{OX + 300}' cy='{OY + 20}' r='64' fill='url(#g)'/><circle cx='{OX + 300}' cy='{OY + 20}' r='15' fill='#FFF6D6'/>"
            f"<rect y='{hz}' width='{WW}' height='{WH - hz}' fill='url(#w)'/>"
            f"<rect y='{hz}' width='{WW}' height='1.6' fill='#BFE6F5' opacity='.7'/>")
    # 島（宝島：左の 水平線）：やしの 木 2本・岩
    ix, iy = OX + 6, hz
    isl = (f"<path d='M{ix - 4} {iy} C{ix + 6} {iy - 9} {ix + 20} {iy - 14} {ix + 34} {iy - 13} C{ix + 46} {iy - 12} {ix + 58} {iy - 7} {ix + 70} {iy - 3} "
           f"C{ix + 76} {iy - 1} {ix + 80} {iy} {ix + 84} {iy} Z' fill='#6FA35A'/>"
           f"<path d='M{ix + 20} {iy} C{ix + 26} {iy - 7} {ix + 40} {iy - 10} {ix + 52} {iy - 6} C{ix + 58} {iy - 4} {ix + 62} {iy - 1} {ix + 66} {iy} Z' fill='#5A8C48'/>"
           f"<path d='M{ix - 6} {iy + 0.2} H{ix + 86} V{iy + 1.8} H{ix - 6} Z' fill='#F2DDA8' opacity='.85'/>")
    for px, ph, lean in ((ix + 30, 22, -0.18), (ix + 44, 17, 0.12)):
        tx, ty = px + ph * lean * 2.2, iy - 11 - ph
        isl += f"<path d='M{px} {iy - 10} Q{px + ph * lean} {iy - 10 - ph * 0.55} {tx} {ty}' fill='none' stroke='#7A5A3A' stroke-width='1.6' stroke-linecap='round'/>"
        for a in (-160, -120, -60, -20, 20):
            r = math.radians(a)
            ex, ey = tx + math.cos(r) * 9, ty + math.sin(r) * 5 + 2.5
            cx, cy = tx + math.cos(r) * 5, ty + math.sin(r) * 4 - 2.2
            isl += f"<path d='M{f(tx)} {f(ty)} Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}' fill='none' stroke='#3E7A3A' stroke-width='2.1' stroke-linecap='round'/>"
    # 遠くの 帆船（小さく）
    sx, sy = OX + 214, hz
    isl += (f"<path d='M{sx - 7} {sy - 1.5} L{sx + 7} {sy - 1.5} L{sx + 5} {sy + 0.6} L{sx - 5} {sy + 0.6} Z' fill='#4A3A30' opacity='.55'/>"
            f"<path d='M{sx - 0.4} {sy - 13} V{sy - 1.5}' stroke='#4A3A30' stroke-width='.8' opacity='.55'/>"
            f"<path d='M{sx} {sy - 12} Q{sx + 5} {sy - 8} {sx} {sy - 3} Z M{sx - 0.8} {sy - 11} Q{sx - 6} {sy - 7} {sx - 0.8} {sy - 3} Z' fill='#F4EEE2' opacity='.6'/>")
    # 海の きらめき（止まった 線）
    R = rnd(5)
    for i in range(46):
        y = hz + 3 + R.random() ** 1.4 * (WH - hz - 8)
        x = R.uniform(0, WW)
        L = R.uniform(4, 14) * (0.6 + (y - hz) / 70)
        isl += f"<path d='M{f(x)} {f(y)} h{f(L)}' stroke='#CFEFFA' stroke-width='{f(0.8 + (y - hz) / 90)}' stroke-linecap='round' opacity='{f(R.uniform(.35, .7))}'/>"
    return doc(WW, WH, body + isl, defs=defs)


def clouds_svg():
    """横に くり返せる 雲（はば WW）"""
    R = rnd(11)
    out = ''
    for cx, cy, n, s in ((60, 26, 6, 1.0), (205, 14, 5, 0.8), (330, 36, 7, 1.1), (430, 20, 4, 0.7)):
        parts = []
        for i in range(n):
            x = cx + (i - n / 2) * 9 * s + R.uniform(-3, 3)
            y = cy + R.uniform(-3, 2) - math.sin(math.pi * (i + .5) / n) * 6 * s
            r = (8 + math.sin(math.pi * (i + .5) / n) * 7) * s
            parts.append((x, y, r))
        for dx in (-WW, 0, WW):
            for x, y, r in parts:
                out += f"<circle cx='{f(x + dx)}' cy='{f(y + 3)}' r='{f(r)}' fill='#D9EEF8'/>"
            for x, y, r in parts:
                out += f"<circle cx='{f(x + dx)}' cy='{f(y)}' r='{f(r)}' fill='#FFFFFF'/>"
            base = cy + 7 * s
            out += f"<rect x='{f(parts[0][0] - 6 + dx)}' y='{f(base - 4)}' width='{f(parts[-1][0] - parts[0][0] + 12)}' height='{f(7 * s)}' rx='3' fill='#FFFFFF'/>"
    return doc(WW, 60, out)


def waves_svg(w=120, h=26, seed=3, op=0.75):
    """横に くり返せる 波頭（白い 弧）"""
    R = rnd(seed)
    out = ''
    for i in range(7):
        x = R.uniform(0, w)
        y = R.uniform(3, h - 3)
        L = R.uniform(7, 15)
        for dx in (-w, 0, w):
            out += (f"<path d='M{f(x + dx)} {f(y)} q{f(L * 0.5)} {f(-3)} {f(L)} 0' fill='none' stroke='#E8F7FD' stroke-width='1.3' stroke-linecap='round' opacity='{op}'/>")
    return doc(w, h, out)


def gull_svg():
    return doc(22, 10, "<path d='M1 6 Q5 0 11 5 Q17 0 21 6 Q17 3 11 7.5 Q5 3 1 6 Z' fill='#FFFFFF' stroke='#3A4A5A' stroke-width='.7'/>")


def ship_svg(right=False):
    """遠くを 通る 海賊船（横から・左が へさき）：こげ茶の 船体（明るい 帯・小さな 砲門・高い とも）・へさきの 斜しょう・2本の 帆柱に 黒い 四角の 帆
       （ふくらむ・大きい 帆に 白い 蹄鉄）・てっぺんに 小さな 黒い 旗と 赤い 吹き流し・水の 白い すじ。right=True は 右向き（反転）。大きさ 64×54（水の 線＝48）"""
    o = ''
    # 水の すじ（船の 下と うしろ）
    o += "<path d='M6 48.6 Q22 47.2 40 48.2 T62 48.6' fill='none' stroke='#E8F7FD' stroke-width='1.2' stroke-linecap='round' opacity='.85'/>"
    o += "<path d='M44 50.4 Q52 49.6 62 50.6' fill='none' stroke='#E8F7FD' stroke-width='.9' stroke-linecap='round' opacity='.6'/>"
    # 帆柱と 綱
    o += ("<path d='M24 41 V9' stroke='#4A2E1A' stroke-width='1.3'/><path d='M40 41 V5' stroke='#4A2E1A' stroke-width='1.4'/>"
          "<path d='M8 36 L24 9 M24 9 L40 5 M40 5 L54 34' fill='none' stroke='#5A4030' stroke-width='.5' opacity='.85'/>"
          "<path d='M4 37.5 L12 33.5' stroke='#4A2E1A' stroke-width='1'/>")
    # 帆（黒・ふくらむ）
    sails = ((24, 12, 9.5, 11), (24, 25, 11, 10), (40, 8, 11, 12), (40, 22, 13.5, 13))
    for cx, top, hw, hh in sails:
        o += (f"<path d='M{cx - hw} {top} Q{cx} {top + 2.2} {cx + hw} {top} Q{cx + hw - 1.2} {top + hh / 2} {cx + hw + 0.4} {top + hh} "
              f"Q{cx} {top + hh + 2.6} {cx - hw - 0.4} {top + hh} Q{cx - hw + 1.2} {top + hh / 2} {cx - hw} {top} Z' fill='#1C1A20'/>"
              f"<path d='M{cx - hw} {top} Q{cx} {top + 2.2} {cx + hw} {top}' fill='none' stroke='#4A4450' stroke-width='.7'/>"
              f"<path d='M{cx - hw * 0.4} {top + 1.6} Q{cx - hw * 0.5} {top + hh / 2} {cx - hw * 0.4} {top + hh + 0.8}' fill='none' stroke='#34303A' stroke-width='.6'/>")
        o += f"<path d='M{cx - hw - 0.6} {top - 0.4} H{cx + hw + 0.6}' stroke='#4A2E1A' stroke-width='.9'/>"
    # 大きい 帆の 白い 蹄鉄（U が 上に ひらく）
    o += f"<path d='{horseshoe_d(40, 28.6, 4.6, 2.7)}' fill='#F2EEE6'/>"
    # てっぺんの 旗と 吹き流し
    o += ("<path d='M40.2 5 H47 L45.6 7 L47 9 H40.2 Z' fill='#16141A'/><circle cx='43.4' cy='7' r='.9' fill='#F2EEE6'/>"
          "<path d='M24.2 9 L30 10 L24.2 11 Z' fill='#C8322A'/>")
    # 船体
    o += ("<path d='M4 38.6 L56 37.4 L60 31.6 L62 31.6 L60.4 41 Q57 47.6 48 48 H14 Q8 47.6 6 43.6 Z' fill='#4A2E1A'/>"
          "<path d='M5.2 40.6 L59.6 39.4 L59.2 41.6 L5.8 42.6 Z' fill='#8A5A34'/>"
          "<path d='M50 37.6 L56 37.4 L60 31.6 L62 31.6 L61.4 34.6 L56.8 39 L50 39.2 Z' fill='#5E3A20'/>")
    for x in (14, 22, 30, 38, 46):
        o += f"<rect x='{x}' y='43.4' width='2.2' height='1.8' fill='#1A1210'/>"
    o += "<path d='M5 44.6 Q30 46.6 58 44.2' fill='none' stroke='#2E1C10' stroke-width='.6' opacity='.7'/>"
    if right:
        o = f"<g transform='translate(64 0) scale(-1 1)'>{o}</g>"
    return doc(64, 54, o)


def railing_svg():
    """手すり（ブルワーク）：上の 太い 板・ろくろの 柱・下の 板。柱の あいだから 海が 見える"""
    y0, y1 = 90, 122
    o = ''
    o += f"<rect x='0' y='{y1 - 5}' width='{W}' height='6' fill='{WOOD['d']}'/>"
    o += f"<rect x='0' y='{y1 - 5}' width='{W}' height='1.4' fill='{WOOD['m']}'/>"
    for i in range(19):
        x = 6 + i * 21.5
        o += (f"<path d='M{f(x - 2.6)} {y0 + 8} H{f(x + 2.6)} L{f(x + 1.6)} {y0 + 12} Q{f(x + 4.2)} {y0 + 17} {f(x + 2.2)} {y0 + 22} L{f(x + 2.8)} {y1 - 5} "
              f"H{f(x - 2.8)} L{f(x - 2.2)} {y0 + 22} Q{f(x - 4.2)} {y0 + 17} {f(x - 1.6)} {y0 + 12} Z' fill='{WOOD['m']}'/>"
              f"<path d='M{f(x - 1.6)} {y0 + 12} Q{f(x - 3.2)} {y0 + 17} {f(x - 1.6)} {y0 + 21}' fill='none' stroke='{WOOD['hi']}' stroke-width='.9' opacity='.8'/>"
              f"<path d='M{f(x + 1.9)} {y0 + 13} Q{f(x + 3.4)} {y0 + 17} {f(x + 1.9)} {y0 + 21} L{f(x + 2.4)} {y1 - 5}' fill='none' stroke='{WOOD['d']}' stroke-width='1' opacity='.7'/>")
    o += (f"<rect x='0' y='{y0}' width='{W}' height='8.5' fill='{WOOD['m']}'/>"
          f"<rect x='0' y='{y0}' width='{W}' height='2.4' fill='{WOOD['hi']}'/>"
          f"<rect x='0' y='{y0 + 7}' width='{W}' height='1.5' fill='{WOOD['d']}'/>")
    for i in range(10):
        x = 20 + i * 41
        o += f"<circle cx='{x}' cy='{y0 + 4.6}' r='.9' fill='{WOOD['dd']}'/>"
    return doc(W, H, o)


def deck_svg():
    """甲板：横の 板（色を 少し ずつ かえる）・つなぎ目・くぎ・手前ほど 暗く"""
    y0 = 121
    R = rnd(21)
    defs = ("<linearGradient id='d' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.18'/><stop offset='.25' stop-color='#000' stop-opacity='0'/>"
            "<stop offset='1' stop-color='#000' stop-opacity='.22'/></linearGradient>")
    o = ''
    rows = [(121, 7), (128, 8.5), (136.5, 10), (146.5, 13.5)]
    tones = ['#A8743F', '#B4804A', '#9E6B3A', '#AE7A44']
    for k, (y, hh) in enumerate(rows):
        o += f"<rect x='0' y='{f(y)}' width='{W}' height='{f(hh)}' fill='{tones[k]}'/>"
        o += f"<rect x='0' y='{f(y)}' width='{W}' height='.9' fill='{WOOD['hi']}' opacity='.55'/>"
        o += f"<rect x='0' y='{f(y + hh - 0.9)}' width='{W}' height='.9' fill='{WOOD['dd']}' opacity='.45'/>"
        x = R.uniform(-40, 0)
        while x < W:
            L = R.uniform(70, 120) * (1 + k * 0.15)
            x += L
            o += f"<rect x='{f(x)}' y='{f(y + 0.6)}' width='1.1' height='{f(hh - 1.2)}' fill='{WOOD['dd']}' opacity='.55'/>"
            for yy in (y + hh * 0.3, y + hh * 0.72):
                o += f"<circle cx='{f(x - 3.2)}' cy='{f(yy)}' r='{f(0.55 + k * 0.12)}' fill='{WOOD['dd']}' opacity='.75'/><circle cx='{f(x + 4.4)}' cy='{f(yy)}' r='{f(0.55 + k * 0.12)}' fill='{WOOD['dd']}' opacity='.75'/>"
        for i in range(10):                                              # 木目
            gx = R.uniform(0, W)
            gl = R.uniform(14, 40)
            gy = y + R.uniform(1.5, hh - 1.5)
            o += f"<path d='M{f(gx)} {f(gy)} q{f(gl / 2)} {f(R.uniform(-1, 1))} {f(gl)} 0' fill='none' stroke='{WOOD['d']}' stroke-width='.6' opacity='.35'/>"
    o += f"<rect y='{y0}' width='{W}' height='{H - y0}' fill='url(#d)'/>"
    # 右の たる・ロープの 輪（左の すみ）
    bx = 364
    o += (f"<ellipse cx='{bx + 12}' cy='152' rx='19' ry='4' fill='#2A1A0E' opacity='.3'/>"
          f"<path d='M{bx - 4} 112 Q{bx - 8} 131 {bx - 4} 150 L{bx + 30} 150 Q{bx + 34} 131 {bx + 30} 112 Z' fill='#9A6436'/>"
          f"<path d='M{bx - 4} 112 Q{bx - 8} 131 {bx - 4} 150 L{bx + 4} 150 Q{bx + 1} 131 {bx + 4} 112 Z' fill='#7A4A26'/>"
          f"<path d='M{bx + 22} 112 Q{bx + 26} 131 {bx + 22} 150 L{bx + 30} 150 Q{bx + 34} 131 {bx + 30} 112 Z' fill='#B8804A' opacity='.7'/>")
    for yy in (118, 131, 144):
        o += f"<path d='M{bx - 6} {yy} Q{bx + 13} {yy + 2.4} {bx + 32} {yy}' fill='none' stroke='#3E3A3A' stroke-width='2.6'/><path d='M{bx - 6} {yy - 0.8} Q{bx + 13} {yy + 1.6} {bx + 32} {yy - 0.8}' fill='none' stroke='#8A8486' stroke-width='.8'/>"
    o += (f"<ellipse cx='{bx + 13}' cy='112' rx='17' ry='3.6' fill='#C08A52'/><ellipse cx='{bx + 13}' cy='112' rx='13' ry='2.4' fill='#A8723E'/>")
    rx0, ry0 = 268, 152
    for k, (rx_, ry_) in enumerate(((15, 4.4), (11.5, 3.3), (8, 2.3), (4.6, 1.4))):
        o += f"<ellipse cx='{rx0}' cy='{ry0 - k * 0.6}' rx='{rx_}' ry='{ry_}' fill='none' stroke='#C9A86A' stroke-width='2.4'/>"
        o += f"<ellipse cx='{rx0}' cy='{ry0 - k * 0.6}' rx='{rx_}' ry='{ry_}' fill='none' stroke='#8A6A3A' stroke-width='.7' stroke-dasharray='1.2 1.6'/>"
    return doc(W, H, o, defs=defs)


def chest_svg():
    """宝箱（ふたが あいて、金貨が あふれる）：止まった 絵。キラッは 別の 部品"""
    x0, y0, w, h = 18, 108, 82, 36            # 箱の 前の 面
    o = "<ellipse cx='60' cy='146' rx='50' ry='5' fill='#2A1A0E' opacity='.35'/>"
    # ふた（うしろへ ひらいて 立つ）
    o += (f"<path d='M{x0 + 3} {y0 - 4} L{x0 - 1} {y0 - 30} Q{x0 + w / 2} {y0 - 44} {x0 + w + 1} {y0 - 30} L{x0 + w - 3} {y0 - 4} Z' fill='{WOOD['d']}'/>"
          f"<path d='M{x0 + 6} {y0 - 6} L{x0 + 3} {y0 - 27} Q{x0 + w / 2} {y0 - 39} {x0 + w - 3} {y0 - 27} L{x0 + w - 6} {y0 - 6} Z' fill='#7A1E22'/>"
          f"<path d='M{x0 + 6} {y0 - 6} L{x0 + 3} {y0 - 27} Q{x0 + w / 2} {y0 - 39} {x0 + w - 3} {y0 - 27} L{x0 + w - 6} {y0 - 6} Z' fill='none' stroke='#5A1216' stroke-width='1.2'/>")
    for t in (0.18, 0.82):
        xx = x0 + w * t
        o += f"<path d='M{f(xx - 3)} {y0 - 5} L{f(xx - 3.5)} {f(y0 - 33 - (1 - abs(t - .5) * 2) * 6)} L{f(xx + 3.5)} {f(y0 - 33 - (1 - abs(t - .5) * 2) * 6)} L{f(xx + 3)} {y0 - 5} Z' fill='{GOLD['d']}' opacity='.9'/>"
    # 金貨の 山（うしろ → 前）
    R = rnd(8)
    pile = (f"<path d='M{x0 + 2} {y0 + 2} C{x0 + 8} {y0 - 16} {x0 + 26} {y0 - 22} {x0 + 42} {y0 - 21} C{x0 + 58} {y0 - 22} {x0 + 76} {y0 - 15} {x0 + w - 2} {y0 + 2} Z' fill='{GOLD['d']}'/>"
            f"<path d='M{x0 + 6} {y0} C{x0 + 12} {y0 - 13} {x0 + 28} {y0 - 18} {x0 + 42} {y0 - 17} C{x0 + 56} {y0 - 18} {x0 + 70} {y0 - 12} {x0 + w - 6} {y0} Z' fill='{GOLD['m']}'/>")
    coins = []
    for i in range(34):
        t = R.random()
        cx = x0 + 6 + t * (w - 12)
        top = y0 - 16 * math.sin(math.pi * (0.08 + 0.84 * t)) - 2
        cy = R.uniform(top, y0 + 1)
        coins.append((cy, cx, R.uniform(3.2, 4.6), R.uniform(-30, 30)))
    for cy, cx, r, a in sorted(coins):
        pile += (f"<g transform='translate({f(cx)} {f(cy)}) rotate({f(a)})'><ellipse rx='{f(r)}' ry='{f(r * 0.62)}' fill='{GOLD['d']}'/>"
                 f"<ellipse cy='-.7' rx='{f(r)}' ry='{f(r * 0.6)}' fill='{GOLD['m']}'/><ellipse cy='-.9' rx='{f(r * 0.62)}' ry='{f(r * 0.34)}' fill='none' stroke='{GOLD['d']}' stroke-width='.7'/>"
                 f"<ellipse cx='{f(-r * 0.35)}' cy='-1.6' rx='{f(r * 0.3)}' ry='{f(r * 0.14)}' fill='{GOLD['l']}'/></g>")
    # 宝石・真珠の くび飾り・金の 杯
    gems = ((x0 + 24, y0 - 11, '#E0284A', '#8E1028'), (x0 + 52, y0 - 13, '#27B07A', '#12654A'), (x0 + 63, y0 - 5, '#3E7BE0', '#1E3E8E'))
    for gx, gy, c1, c2 in gems:
        pile += (f"<path d='M{gx - 4.4} {gy} L{gx - 2.4} {gy - 3.4} H{gx + 2.4} L{gx + 4.4} {gy} L{gx} {gy + 5} Z' fill='{c1}' stroke='{c2}' stroke-width='.7'/>"
                 f"<path d='M{gx - 2.4} {gy - 3.4} L{gx - 0.8} {gy} L{gx} {gy - 3.4} M{gx - 4.4} {gy} H{gx + 4.4}' fill='none' stroke='{c2}' stroke-width='.5' opacity='.8'/>"
                 f"<path d='M{gx - 1.6} {gy - 2.6} L{gx - 0.6} {gy - 0.6}' stroke='#FFFFFF' stroke-width='.8' opacity='.85'/>")
    gx, gy = x0 + 36, y0 - 21
    pile += (f"<path d='M{gx - 6} {gy - 9} H{gx + 6} Q{gx + 6} {gy - 1} {gx} {gy} Q{gx - 6} {gy - 1} {gx - 6} {gy - 9} Z' fill='{GOLD['m']}' stroke='{GOLD['dd']}' stroke-width='.8'/>"
             f"<rect x='{gx - 1}' y='{gy}' width='2' height='5' fill='{GOLD['d']}'/><ellipse cx='{gx}' cy='{gy + 5.6}' rx='4.4' ry='1.4' fill='{GOLD['d']}'/>"
             f"<ellipse cx='{gx}' cy='{gy - 9}' rx='6' ry='1.5' fill='{GOLD['l']}'/><path d='M{gx - 3.6} {gy - 7} Q{gx - 4} {gy - 3.4} {gx - 1.6} {gy - 1.6}' fill='none' stroke='#FFF6C8' stroke-width='1.1' stroke-linecap='round'/>"
             f"<circle cx='{gx}' cy='{gy - 4.4}' r='1.5' fill='#E0284A'/>")
    pearls = ''
    for i in range(15):
        t = i / 14
        px = x0 + w - 18 + t * 20
        py = y0 - 6 + math.sin(t * math.pi) * 12 + t * 8
        pearls += f"<circle cx='{f(px)}' cy='{f(py)}' r='1.5' fill='#F6F1E6' stroke='#B8AE9C' stroke-width='.4'/>"
    # 箱の 前の 面
    o += pile
    o += (f"<path d='M{x0} {y0} H{x0 + w} L{x0 + w - 2} {y0 + h} H{x0 + 2} Z' fill='{WOOD['m']}'/>"
          f"<path d='M{x0} {y0} H{x0 + w} V{y0 + 3.4} H{x0} Z' fill='{WOOD['hi']}' opacity='.8'/>")
    for k in range(1, 4):
        yy = y0 + h * k / 4
        o += f"<path d='M{x0 + 1} {f(yy)} H{x0 + w - 1}' stroke='{WOOD['d']}' stroke-width='.8' opacity='.6'/>"
    for t in (0.14, 0.86):
        xx = x0 + w * t
        o += (f"<rect x='{f(xx - 3.6)}' y='{y0}' width='7.2' height='{h}' fill='{GOLD['d']}'/><rect x='{f(xx - 3.6)}' y='{y0}' width='2' height='{h}' fill='{GOLD['m']}'/>")
        for yy in (y0 + 5, y0 + h / 2, y0 + h - 5):
            o += f"<circle cx='{f(xx)}' cy='{f(yy)}' r='1.1' fill='{GOLD['dd']}'/>"
    o += (f"<rect x='{x0 - 1}' y='{y0 + h - 4}' width='{w + 2}' height='4.5' rx='1' fill='{WOOD['d']}'/>"
          f"<path d='M{x0 + w / 2 - 7} {y0 - 1} H{x0 + w / 2 + 7} V{y0 + 11} Q{x0 + w / 2} {y0 + 16} {x0 + w / 2 - 7} {y0 + 11} Z' fill='{GOLD['m']}' stroke='{GOLD['dd']}' stroke-width='.9'/>"
          f"<path d='M{x0 + w / 2} {y0 + 3.6} m-1.8 0 a1.8 1.8 0 1 0 3.6 0 a1.8 1.8 0 1 0 -3.6 0 M{x0 + w / 2 - 0.8} {y0 + 5} L{x0 + w / 2 - 1.4} {y0 + 9} H{x0 + w / 2 + 1.4} L{x0 + w / 2 + 0.8} {y0 + 5} Z' fill='#3A2410'/>")
    o += pearls
    # こぼれた 金貨（甲板）
    for cx, cy, r in ((x0 + w + 8, 141, 3.8), (x0 + w + 16, 144, 3.4), (x0 - 4, 143, 3.4), (x0 + w + 2, 146, 3.2)):
        o += (f"<ellipse cx='{cx}' cy='{cy + 0.8}' rx='{r}' ry='{f(r * 0.45)}' fill='{GOLD['dd']}'/><ellipse cx='{cx}' cy='{cy}' rx='{r}' ry='{f(r * 0.45)}' fill='{GOLD['m']}'/>"
              f"<ellipse cx='{f(cx - r * 0.3)}' cy='{f(cy - 0.4)}' rx='{f(r * 0.3)}' ry='{f(r * 0.12)}' fill='{GOLD['l']}'/>")
    return doc(124, 152, o, vb='0 0 124 152')


def flagpole_svg():
    """旗ざお（右の はし）・旗を つける 綱・ななめの 綱・見はり台の 先"""
    x = 352
    o = (f"<path d='M{x - 2.6} 0 H{x + 2.6} L{x + 3.4} 124 H{x - 3.4} Z' fill='{WOOD['m']}'/><path d='M{x - 2.6} 0 H{x - 0.8} L{x - 1.2} 124 H{x - 3.4} Z' fill='{WOOD['hi']}' opacity='.7'/>"
         f"<path d='M{x + 1.4} 0 H{x + 2.6} L{x + 3.4} 124 H{x + 2} Z' fill='{WOOD['d']}' opacity='.8'/>"
         f"<rect x='{x - 4}' y='50' width='8' height='3.4' rx='1' fill='{WOOD['d']}'/><rect x='{x - 4}' y='86' width='8' height='3.4' rx='1' fill='{WOOD['d']}'/>"
         f"<path d='M{x + 3} 4 L390 64' stroke='#7A6446' stroke-width='1.1'/><path d='M{x + 3} 8 L390 90' stroke='#7A6446' stroke-width='.9' opacity='.8'/>"
         f"<path d='M{x - 3} 6 Q{x - 60} 60 {x - 120} 94' fill='none' stroke='#7A6446' stroke-width='.9' opacity='.75'/>")
    return doc(W, H, o)


def horseshoe_d(cx, cy, ro, ri, open_up=True, n=30):
    """蹄鉄の 形（U：上に ひらく。かかとは 少し 外へ ひらく）"""
    so, si = [], []
    for k in range(n + 1):
        a = math.radians(-205 + 230 * k / n)
        sx = 1 + 0.08 * abs(math.sin(a)) ** 3 * (1 if math.sin(a) > 0 else 0)
        so.append((cx + math.cos(a) * ro * sx, cy - math.sin(a) * ro * 1.06))
        si.append((cx + math.cos(a) * ri, cy - math.sin(a) * ri * 1.1))
    return P(so + si[::-1])


def flag_svg(w=74, h=46):
    """海賊旗：黒い 布・白い 大きな 蹄鉄（U が 上に ひらく・くぎ穴・みぞ）と 下に ぶっちがいの 骨・すそ（左）が 少し ぎざぎざ"""
    cx, cy = w * 0.5, h * 0.44
    o = (f"<path d='M0 0 H{w} L{w - 3} {h * 0.3} L{w} {h * 0.5} L{w - 4} {h * 0.72} L{w} {h} H0 Z' fill='#16141A'/>"
         f"<path d='M0 0 H{w} V2.2 H0 Z' fill='#2E2A34'/>")
    for a in (28, -28):                                                  # ぶっちがいの 骨（蹄鉄の 下）
        r = math.radians(a)
        dx, dy = math.cos(r) * 17, math.sin(r) * 17
        x1, y1, x2, y2 = cx - dx, cy + 12 - dy * 0.55, cx + dx, cy + 12 + dy * 0.55
        o += f"<path d='M{f(x1)} {f(y1)} L{f(x2)} {f(y2)}' stroke='#F2EEE6' stroke-width='3.6' stroke-linecap='round'/>"
        for ex, ey in ((x1, y1), (x2, y2)):
            nx, ny = -math.sin(r) * 2.1, math.cos(r) * 2.1
            o += f"<circle cx='{f(ex + nx)}' cy='{f(ey + ny)}' r='2.3' fill='#F2EEE6'/><circle cx='{f(ex - nx)}' cy='{f(ey - ny)}' r='2.3' fill='#F2EEE6'/>"
    o += f"<path d='{horseshoe_d(cx, cy, 15.5, 9.2)}' fill='#F7F3EA' stroke='#16141A' stroke-width='1.4' stroke-linejoin='round'/>"
    groove = []
    for k in range(25):
        a = math.radians(-196 + 212 * k / 24)
        groove.append((cx + math.cos(a) * 12.4, cy - math.sin(a) * 13.3))
    o += f"<path d='{P(groove, False)}' fill='none' stroke='#9A948A' stroke-width='.8'/>"
    for k in (2, 6, 10, 14, 18, 22):
        a = math.radians(-196 + 212 * k / 24)
        x, y = cx + math.cos(a) * 12.4, cy - math.sin(a) * 13.3
        o += f"<rect x='{f(x - 0.9)}' y='{f(y - 1.3)}' width='1.8' height='2.6' rx='.3' transform='rotate({f(-math.degrees(a) + 90)} {f(x)} {f(y)})' fill='#16141A'/>"
    return doc(w, h, f"<g transform='translate({w} 0) scale(-1 1)'>{o}</g>")


def wheel_svg():
    """舵輪（木の 輪・8本の 取っ手・まん中に 金の 金具）。中心 (36, 36)"""
    c = 36
    o = (f"<circle cx='{c}' cy='{c}' r='22' fill='none' stroke='{WOOD['d']}' stroke-width='6.4'/>"
         f"<circle cx='{c}' cy='{c}' r='22' fill='none' stroke='{WOOD['m']}' stroke-width='4.2'/>"
         f"<circle cx='{c}' cy='{c}' r='22.8' fill='none' stroke='{WOOD['hi']}' stroke-width='1' opacity='.7' stroke-dasharray='20 14'/>")
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        ca, sa = math.cos(a), math.sin(a)
        o += (f"<path d='M{f(c + ca * 7)} {f(c + sa * 7)} L{f(c + ca * 34)} {f(c + sa * 34)}' stroke='{WOOD['d']}' stroke-width='3.8' stroke-linecap='round'/>"
              f"<path d='M{f(c + ca * 7)} {f(c + sa * 7)} L{f(c + ca * 34)} {f(c + sa * 34)}' stroke='{WOOD['m']}' stroke-width='2.2' stroke-linecap='round'/>"
              f"<ellipse cx='{f(c + ca * 31)}' cy='{f(c + sa * 31)}' rx='3.1' ry='2.3' transform='rotate({f(math.degrees(a))} {f(c + ca * 31)} {f(c + sa * 31)})' fill='{WOOD['m']}' stroke='{WOOD['d']}' stroke-width='1'/>")
    o += (f"<circle cx='{c}' cy='{c}' r='8.4' fill='{GOLD['d']}'/><circle cx='{c}' cy='{c}' r='6.6' fill='{GOLD['m']}'/><circle cx='{c - 1.6}' cy='{c - 1.6}' r='2.2' fill='{GOLD['l']}'/>"
          f"<circle cx='{c}' cy='{c}' r='2' fill='{GOLD['dd']}'/>")
    return doc(72, 72, o)


def stand_svg():
    """舵輪の 台（木の 柱）"""
    return doc(20, 60, f"<path d='M4 0 H16 L18 56 H2 Z' fill='{WOOD['d']}'/><path d='M4 0 H8 L6 56 H2 Z' fill='{WOOD['m']}'/>"
                       f"<rect x='0' y='54' width='20' height='6' rx='1.4' fill='{WOOD['dd']}'/><ellipse cx='10' cy='60' rx='14' ry='2.4' fill='#2A1A0E' opacity='.3'/>")


def glint_svg():
    """金貨の キラッ（小さな 4つ角の 光）"""
    return doc(16, 16, f"<path d='{sparkle_d(8, 8, 7.6, 0.16)}' fill='#FFFDF0'/><circle cx='8' cy='8' r='1.8' fill='#FFFFFF'/>")


# ---------------------------------------------------------------- 船長の 歩き方（40秒の 1回り）
STANDS = ('front', 'up1', 'up', 'down1', 'down')     # pirate_art.STANDS と 同じ じゅん
# ('stop', [(形, 秒)…], 向きを かえる 時刻（止まって から の 秒・なし＝None）) ／ ('walk', 1回りの 数, 向き：+1 右・-1 左)
# 歩く 区間は 1回り（1.25秒）の 数・止まる 区間も 1.25秒の 倍数（歩きだす ときの 足の 形が いつも 同じ）。はじめは 左を 向いて 宝箱の 前
PLAN = [
    ('stop', [('front', 1.0), ('down1', .15), ('down', 1.45), ('down1', .15), ('front', 1.0)], 2.95),   # 宝箱の 前：のぞきこむ → 右を 向く
    ('walk', 2, 1),
    ('stop', [('front', .5), ('up1', .15), ('up', 1.2), ('up1', .15), ('front', .5)], None),          # 見上げる（旗・空）
    ('walk', 2, 1),
    ('stop', [('front', 1.0), ('down1', .15), ('down', .9), ('down1', .15), ('front', 1.55)], 2.85),   # 舵輪の うしろ：下を 見る → 左を 向く
    ('walk', 3, -1),
    ('stop', [('front', .4), ('up1', .15), ('up', .4), ('up1', .15), ('front', .15)], None),
    ('walk', 2, -1),
    ('stop', [('front', .6), ('down1', 1.8), ('front', 1.35)], 3.2),                                   # 宝箱を ながめる → 右を 向く
    ('walk', 2, 1),
    ('stop', [('front', .6), ('up1', .15), ('up', .95), ('up1', .15), ('front', .65)], None),
    ('walk', 1, 1),
    ('stop', [('front', .9), ('down1', .15), ('down', .6), ('down1', .15), ('front', .7)], 2.0),
    ('walk', 2, -1),
]
TURN = 0.36        # くるっと 向きを かえる 秒


def walk_keys(speed, cx):
    """PLAN → 動きの キー（時刻・値）。返り値：(1回りの 秒, 位置, 向き, 歩いて いるか, 止まった 形)"""
    step = speed * WALK_C
    t, x, face = 0.0, 0.0, -1
    pos, flip, walking, frame = [(0.0, 0.0)], [(0.0, face)], [(0.0, 0)], []
    for blk in PLAN:
        if blk[0] == 'walk':
            _, n, d = blk
            assert d == face, (blk, face)
            dur = n * WALK_C
            walking.append((t, 1))
            x += d * n * step
            t += dur
            pos.append((t, x))
            walking.append((t, 0))
            frame.append((t - dur, None))
        else:
            _, looks, turn = blk
            dur = sum(d for _, d in looks)
            assert abs(dur / WALK_C - round(dur / WALK_C)) < 1e-6, (dur, blk)
            tt = t
            for nm, d in looks:
                frame.append((tt, STANDS.index(nm)))
                tt += d
            pos.append((t + dur, x))
            if turn is not None:
                flip += [(t + turn, face), (t + turn + TURN / 2, face * 0.06), (t + turn + TURN, -face)]
                face = -face
            t += dur
    assert abs(x) < 1e-6 and face == -1, (x, face)
    return t, pos, flip, walking, frame


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    wk, sd = B.get('walk'), B.get('stand')
    still = B.get('still')
    alt = ('海賊船の甲板を、三角帽と赤いスカーフの芦毛の馬の船長が歩きまわる。左に金貨と宝石があふれる宝箱、右に舵輪と、白い蹄鉄の海賊旗。'
           '手すりのむこうに青い海と空と宝島のイラスト（船が波で少しゆれて、ときどき遠くを黒い帆の海賊船が通り、旗がなびき、金貨がキラッと光る。'
           '船長は歩いたり、止まって宝箱をのぞいたり空を見上げたり、向きをかえたりする）')
    html = f'<div class="prw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += ('<div class="prW">' + img('prSky', sky_svg()) + f'<i class="prCl" style="background-image:url(&quot;{durl(clouds_svg())}&quot;)"></i>'
             + f'<i class="prWv a" style="background-image:url(&quot;{durl(waves_svg(120, 24, 3, .8))}&quot;)"></i>'
             + f'<i class="prWv b" style="background-image:url(&quot;{durl(waves_svg(150, 30, 9, .6))}&quot;)"></i>'
             + img('prGl g1', gull_svg()) + img('prGl g2', gull_svg())
             + '<i class="prSp a"><i>' + img('prSi', ship_svg(False)) + '</i></i>'
             + '<i class="prSp b"><i>' + img('prSi', ship_svg(True)) + '</i></i>' + '</div>')
    html += img('prRl', railing_svg()) + img('prFp', flagpole_svg())
    fl = flag_svg()
    NF = 32
    html += '<i class="prFg">' + ''.join(f'<b style="left:{f(i * 74 / NF)}px;background-position:{f(-i * 74 / NF)}px 0;--mx:{f(-i * 74 / NF)}px;animation-delay:{f(-1.6 * i / NF, 3)}s;--a:{f(0.5 + 2.9 * (NF - i) / NF)}px"></b>' for i in range(NF)) + '</i>'
    html += img('prDk', deck_svg())
    if wk and sd:                                                       # 船長（宝箱と 舵輪の うしろを 歩く）
        html += '<i class="prHm"><i class="prHf"><i class="prHw"><i></i></i><i class="prHs"><i></i></i></i></i>'
    html += img('prSt', stand_svg()) + img('prWh', wheel_svg())
    html += img('prCh', chest_svg())
    gl = glint_svg()
    for k in range(6):
        html += img(f'prGt t{k}', gl)
    html += '</div>'

    # ---- CSS
    fl_uri = durl(fl)
    css = ('.prw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#9AD2EF}'
           '.prw>*{position:absolute;display:block}'
           '.prw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           # 世界（手すりの むこう）：船の ゆれで かたむいて 上下する
           f'.prw .prW{{left:{-OX}px;top:{-OY}px;width:{WW}px;height:{WH}px;overflow:hidden;transform-origin:{OX + 195}px {OY + 104}px;animation:prRock {ROCK}s ease-in-out infinite;will-change:transform}}'
           '.prw .prW>*{position:absolute;display:block}'
           f'.prw .prSky{{left:0;top:0;width:{WW}px;height:{WH}px}}'
           f'.prw .prCl{{left:0;top:{OY - 2}px;width:{2 * WW}px;height:60px;background-size:{WW}px 60px;background-repeat:repeat-x;animation:prFlow 90s linear infinite}}'
           f'.prw .prWv{{left:0;width:{2 * WW}px;background-repeat:repeat-x}}'
           f'.prw .prWv.a{{top:{OY + HZ + 2}px;height:24px;width:{WW + 120}px;background-size:120px 24px;animation:prWa 7s linear infinite}}'
           f'.prw .prWv.b{{top:{OY + HZ + 22}px;height:30px;width:{WW + 150}px;background-size:150px 30px;animation:prWb 5s linear infinite}}'
           '.prw .prGl{width:22px;height:10px;left:0;top:0}'
           # 海賊船：8秒に 1回（16秒で 右から 左・左から 右）。船は 波で ゆれる（.prSi）
           f'.prw .prSp{{left:0;top:0;width:56px;height:47px;opacity:0;will-change:transform}}'
           f'.prw .prSp.a{{animation:prShA {f(SHIP_T)}s linear infinite}}'
           f'.prw .prSp.b{{width:46px;height:39px;animation:prShB {f(SHIP_T)}s linear infinite}}'
           '.prw .prSp>i{position:absolute;inset:0;transform-origin:50% 88%;animation:prBob 2.6s ease-in-out infinite alternate}'
           '.prw .prSp.b>i{animation-delay:-1.1s}'
           '.prw .prSi{position:absolute;left:0;top:0;width:100%;height:100%}'
           '.prw .prGl.g1{animation:prG1 16s linear infinite}'
           '.prw .prGl.g2{width:15px;height:7px;animation:prG2 16s linear -6s infinite}'
           # 船（そのまま）
           '.prw .prRl,.prw .prFp,.prw .prDk{left:0;top:0;width:390px;height:160px}'
           '.prw .prFg{left:278px;top:6px;width:74px;height:46px}'
           f'.prw .prFg>b{{position:absolute;top:0;width:{f(74 / 32 + 0.7)}px;height:46px;background:url("{fl_uri}") 0 0/74px 46px no-repeat;animation:prFlag 1.6s ease-in-out infinite;will-change:transform}}'
           # 布の しわの かげ（波の かたむきに 合わせて 帯ごとに 明るさが かわる：旗の 形で 切りぬく）
           f'.prw .prFg>b::after{{content:"";position:absolute;inset:0;background:#000;opacity:0;-webkit-mask:url("{fl_uri}") var(--mx) 0/74px 46px no-repeat;mask:url("{fl_uri}") var(--mx) 0/74px 46px no-repeat;'
           'animation:prFlagS 1.6s ease-in-out infinite;animation-delay:inherit}'
           '.prw .prSt{left:316px;top:94px;width:20px;height:60px}'
           f'.prw .prWh{{left:290px;top:58px;width:72px;height:72px;animation:prWheel {ROCK}s ease-in-out infinite;will-change:transform}}'
           '.prw .prCh{left:2px;top:4px;width:124px;height:152px}'
           '.prw .prGt{width:17px;height:17px;opacity:0;animation:prGlint 4.2s ease-in-out infinite;will-change:transform,opacity}')
    if wk and sd:
        T, pos, flip, walking, frame = walk_keys(wk['speed'], wk['cx'])
        pc = lambda t: 100 * t / T
        n, (cw, ch), (ax, ay) = wk['frames'], wk['cell'], wk['at']
        sn, (sw, sh), (sx, sy) = sd['frames'], sd['cell'], sd['at']
        css += ('.prw .prHm,.prw .prHf,.prw .prHw,.prw .prHs{position:absolute;display:block}'
                '.prw .prHm,.prw .prHf{left:0;top:0;width:390px;height:160px}'
                f'.prw .prHm{{animation:prHm {f(T)}s linear infinite;will-change:transform}}'
                f'.prw .prHf{{transform-origin:{f(wk["cx"])}px 140px;animation:prHf {f(T)}s linear infinite}}'
                f'.prw .prHw{{left:{f(ax / 2)}px;top:{f(ay / 2)}px;width:{f(cw / 2)}px;height:{f(ch / 2)}px;overflow:hidden;animation:prHw {f(T)}s step-end infinite}}'
                f'.prw .prHw>i{{display:block;width:{f(n * cw / 2)}px;height:{f(ch / 2)}px;background:url({wk["url"]}) 0 0/{f(n * cw / 2)}px {f(ch / 2)}px no-repeat;'
                f'animation:prWalk {WALK_C}s steps({n}) infinite}}'
                f'.prw .prHs{{left:{f(sx / 2)}px;top:{f(sy / 2)}px;width:{f(sw / 2)}px;height:{f(sh / 2)}px;overflow:hidden;animation:prHs {f(T)}s step-end infinite}}'
                f'.prw .prHs>i{{display:block;width:{f(sn * sw / 2)}px;height:{f(sh / 2)}px;background:url({sd["url"]}) 0 0/{f(sn * sw / 2)}px {f(sh / 2)}px no-repeat;'
                f'animation:prLook {f(T)}s step-end infinite}}'
                + kf('prWalk', [(100, f'transform:translateX({f(-n * cw / 2)}px)')])
                + kf('prHm', [(pc(t), f'transform:translateX({f(x)}px)') for t, x in pos])
                + kf('prHf', [(pc(t), f'transform:scaleX({f(sc, 3)})') for t, sc in flip] + [(100, f'transform:scaleX({f(flip[0][1])})')]))
        vis = [(pc(t), f'opacity:{w}') for t, w in walking]
        css += kf('prHw', vis) + kf('prHs', [(p_, 'opacity:' + str(1 - int(v_[-1]))) for p_, v_ in vis])
        look, last = [], 0
        for t, k in frame:
            k = last if k is None else k
            last = k
            look.append((pc(t), f'transform:translateX({f(-k * sw / 2)}px)'))
        css += kf('prLook', look + [(100, look[0][1])])
    for k, (x, y, d) in enumerate(((36, 95, 0.0), (64, 88, 0.7), (86, 98, 1.4), (50, 104, 2.1), (74, 104, 2.8), (111, 145, 3.5))):
        css += f'.prw .prGt.t{k}{{left:{x - 8.5}px;top:{y - 8.5}px;animation-delay:{f(d, 2)}s}}'
    up, dn = BOB
    css += (kf('prRock', [(0, f'transform:rotate({-ROT}deg) translateY({-up}px)'), (25, f'transform:rotate(0deg) translateY({dn}px)'), (50, f'transform:rotate({ROT}deg) translateY({-up}px)'),
                          (75, f'transform:rotate(0deg) translateY({dn}px)'), (100, f'transform:rotate({-ROT}deg) translateY({-up}px)')])
            + kf('prWheel', [(0, f'transform:rotate({-WHEEL[0]}deg)'), (50, f'transform:rotate({WHEEL[1]}deg)'), (100, f'transform:rotate({-WHEEL[0]}deg)')])
            + kf('prFlow', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-WW}px)')])
            + kf('prWa', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-120px)')])
            + kf('prWb', [(0, 'transform:translateX(0)'), (100, 'transform:translateX(-150px)')])
            + kf('prFlag', [(0, 'transform:translateY(calc(var(--a) * -1))'), (50, 'transform:translateY(var(--a))'), (100, 'transform:translateY(calc(var(--a) * -1))')])
            + kf('prFlagS', [(0, 'opacity:0'), (25, 'opacity:.24'), (50, 'opacity:0'), (100, 'opacity:0')])
            + kf('prGlint', [(0, 'opacity:0;transform:scale(.2) rotate(0)'), (8, 'opacity:1;transform:scale(1) rotate(25deg)'), (16, 'opacity:0;transform:scale(.3) rotate(45deg)'), (100, 'opacity:0;transform:scale(.2)')]))
    # 海賊船：a＝右から 左（0〜7.2秒・へさきは 左）・b＝左から 右（8〜15.2秒・少し 小さく 遠く・へさきは 右）
    wa, wb = OY + HZ + 6 - 41.8, OY + HZ + 3 - 34.7        # 水の 線（ship_svg の 48 を 大きさに 合わせて）を 水平線の 少し 手前に
    T8 = SHIP_T
    css += kf('prShA', [(0, f'opacity:1;transform:translate({WW + 10}px,{wa}px)'), (100 * 7.2 / T8, f'opacity:1;transform:translate(-70px,{wa}px)'),
                        (100 * 7.21 / T8, f'opacity:0;transform:translate(-70px,{wa}px)'), (100, f'opacity:0;transform:translate({WW + 10}px,{wa}px)')])
    css += kf('prShB', [(0, f'opacity:0;transform:translate(-60px,{wb}px)'), (100 * 7.99 / T8, f'opacity:0;transform:translate(-60px,{wb}px)'),
                        (100 * 8.0 / T8, f'opacity:1;transform:translate(-60px,{wb}px)'), (100 * 15.2 / T8, f'opacity:1;transform:translate({WW + 8}px,{wb}px)'),
                        (100 * 15.21 / T8, f'opacity:0;transform:translate({WW + 8}px,{wb}px)'), (100, f'opacity:0;transform:translate(-60px,{wb}px)')])
    css += kf('prBob', [(0, 'transform:translateY(-.7px) rotate(-2.2deg)'), (100, 'transform:translateY(.7px) rotate(2deg)')])
    # かもめ：右から 左へ（ゆっくり 上下しながら）
    g1 = [(0, 470, 40), (25, 380, 30), (50, 270, 38), (75, 150, 28), (100, 20, 34)]
    g2 = [(0, 480, 58), (30, 360, 50), (60, 240, 56), (100, 70, 48)]
    css += kf('prG1', [(p, f'transform:translate({x}px,{y}px)') for p, x, y in g1])
    css += kf('prG2', [(p, f'transform:translate({x}px,{y}px)') for p, x, y in g2])
    css += reduced('.prw .prW,.prw .prRl,.prw .prFp,.prw .prFg,.prw .prDk,.prw .prSt,.prw .prWh,.prw .prHm,.prw .prCh,.prw .prGt') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_map():
    """背景の もよう：古い 宝の 地図（点線の 道・小さな 方位・波・×じるし）。うすく"""
    o = ("<path d='M8 104 C30 92 34 70 58 66 S96 52 112 30' fill='none' stroke='#A8865A' stroke-width='1.3' stroke-dasharray='3 4' stroke-linecap='round' opacity='.45'/>"
         "<path d='M106 24 l8 8 M114 24 l-8 8' stroke='#B0442E' stroke-width='2' stroke-linecap='round' opacity='.45'/>")
    cx, cy = 34, 30
    o += (f"<path d='{star_d(cx, cy, 11, 2.6, 4, -90)}' fill='#C2A06A' opacity='.35'/><path d='{star_d(cx, cy, 6.4, 1.6, 4, -45)}' fill='#C2A06A' opacity='.28'/>"
          f"<circle cx='{cx}' cy='{cy}' r='13.5' fill='none' stroke='#C2A06A' stroke-width='.8' opacity='.35'/>")
    for x, y in ((84, 92), (20, 128), (110, 120)):
        o += f"<path d='M{x} {y} q4 -4 8 0 t8 0' fill='none' stroke='#9CB8C4' stroke-width='1.2' stroke-linecap='round' opacity='.55'/>"
    return tile(140, 140, o)


def rope_strip():
    """上の 帯の 下の ふちの ロープ（より合わせた 綱）"""
    o = "<rect width='16' height='8' fill='none'/>"
    for k in range(2):
        x = k * 8
        o += (f"<path d='M{x - 2} 7.4 C{x + 1} 7.4 {x + 4} 0.6 {x + 7} 0.6 L{x + 10} 0.6 C{x + 7} 0.6 {x + 4} 7.4 {x + 1} 7.4 Z' fill='#C9A060'/>"
              f"<path d='M{x + 1} 6.2 C{x + 3} 5.2 {x + 5} 2.2 {x + 7} 1.6' fill='none' stroke='#F0D59A' stroke-width='.9' stroke-linecap='round'/>"
              f"<path d='M{x - 1} 7.4 C{x + 2} 7.4 {x + 4} 4 {x + 6} 2' fill='none' stroke='#7A5A2E' stroke-width='.8'/>")
    return tile(16, 8, o)


def orn():
    """すみの 飾り（44×44）：小さな 海賊旗（白い 蹄鉄）"""
    o = ("<path d='M9 4 V41' stroke='#6B4423' stroke-width='2.6' stroke-linecap='round'/>"
         "<path d='M10 6 H38 L35.6 13 L38 20 L35 26 H10 Z' fill='#16141A' stroke='#0A0A0C' stroke-width='.8'/>")
    o += f"<path d='{horseshoe_d(24, 15.5, 6.6, 3.9)}' fill='#F7F3EA'/>"
    o += "<circle cx='9' cy='4' r='2.4' fill='#F2C14E' stroke='#8A5A14' stroke-width='.8'/>"
    o += "<ellipse cx='30' cy='37' rx='9' ry='3.4' fill='#C8902A'/><ellipse cx='30' cy='35.8' rx='9' ry='3.2' fill='#F2C14E'/><ellipse cx='27' cy='35' rx='3' ry='1' fill='#FFE58A'/>"
    o += "<ellipse cx='22' cy='39.6' rx='6' ry='2.4' fill='#C8902A'/><ellipse cx='22' cy='38.8' rx='6' ry='2.2' fill='#F2C14E'/>"
    return o


THEME = dict(
    id=ID, cat=7, name='海賊', desc='宝箱と海賊旗', title='海賊（木×金×海）', banner=ID,
    alt='海賊船の甲板を、三角帽と赤いスカーフの芦毛の馬の船長が歩きまわる。左に金貨と宝石があふれる宝箱、右に舵輪と、白い蹄鉄の海賊旗。手すりのむこうに青い海と空と宝島、ときどき遠くを通る黒い帆の海賊船のイラスト',
    fonts=['Zen+Antique', 'Zen+Kaku+Gothic+New:wght@500;700'],
    v=dict(bg='#F2E6CC', ink='#2E2216', sub='#6A543A', card='#FFF9EC', cardB='1.5px solid #D8BF8A', cardO='0 solid transparent', cardS='0 3px 0 #E4D2A8',
           radius='12px', rs='9px', font='"Zen Kaku Gothic New"', dfont='"Zen Antique"', dw='400', logo='#F2C14E', logoS='0 2px 0 #241406',
           iii='#F2C14E', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#5C3B22,#3E2615)', hdInk='#F7E6C2', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.08)', mLine='rgba(242,193,78,.6)', mInk='#F7E6C2', pill='rgba(0,0,0,.22)', pillLine='rgba(242,193,78,.45)', pillInk='#F7E6C2',
           coin='#F2C14E', coinInk='#3E2615', badge='#FFF1D2', badgeInk='#8A3A12', badgeB='1.5px solid #D8BF8A', tagBg='#F8EDD4', tagInk='#5A4024',
           tagLine='#D8BF8A', warnBg='#F9DED2', warnInk='#9A2E1E', zBg='#FFFBF2', zB='1.5px solid #EADBB8', znBg='#1F4F6E', znInk='#FFFFFF',
           znB='0 solid transparent', znR='4px', znS='none', acc='#9A3A1E', nR='7px', w2B='0 solid transparent', sep='1.5px dashed #D8BF8A',
           btn='#A8322A', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='10px', btnS='0 3px 0 #6E1E16', btn2='#FFF9EC', btn2Ink='#7A3A16',
           btn2B='1.5px solid #C9A86A', tab='#3E2615', tabB='1px solid #2A180C', tabInk='#D8C29A', tabOn='rgba(242,193,78,.16)', tabOnInk='#F2C14E',
           tabR='10px', sel='#A8322A', selInk='#FFFFFF', h1='#8A3A12'),
    chk=dict(hd=['#5C3B22', '#3E2615']),
    css=[('', 'background-image:' + curi(tile_map()) + ';background-size:140px 140px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-7px;height:8px;background:' + curi(rope_strip()) + ' 0 0/16px 8px repeat-x'),
         ('.card', 'background-image:radial-gradient(circle at 100% 0,rgba(201,160,96,.14),transparent 42%),radial-gradient(circle at 0 100%,rgba(201,160,96,.1),transparent 38%)')],
    orn=orn(),
    guide=dict(colors=[('#3E2615', '木'), ('#F2C14E', '金'), ('#A8322A', 'ボタン'), ('#1F4F6E', '海'), ('#F2E6CC', '背景')],
               fonts='見出し：Zen Antique<br>本文：Zen Kaku Gothic New', shape='角丸12px・帯は 木の色で 下に ロープ・宝の地図の 背景・すみに 海賊旗と 金貨・的中ボタンは 宝箱のPUSH',
               pic='海賊船の 甲板・甲板を 歩きまわる 三角帽の 芦毛の 馬の 船長・ふたの あいた 宝箱（金貨・宝石・真珠）・舵輪・白い 蹄鉄の 海賊旗・海と 空と 宝島・ときどき 通る 海賊船'),
)


# ================================================================== 的中ボタン：宝箱の PUSH（pr）
def push_face(sfx=''):
    """ボタン（200×100）が 宝箱の 前の 面（木の 板・金の 帯と びょう・下に かぎ穴）。上に ひらいた ふた（赤い 布）と あふれる 金貨・宝石"""
    o = ''
    # ふた（うしろへ ひらく）
    o += ("<path d='M12 4 L4 -50 Q100 -78 196 -50 L188 4 Z' fill='#5E3A1E'/>"
          "<path d='M20 2 L13 -44 Q100 -68 187 -44 L180 2 Z' fill='#8E1E22'/>"
          "<path d='M20 2 L13 -44 Q100 -68 187 -44 L180 2 Z' fill='none' stroke='#5A1216' stroke-width='2'/>"
          "<path d='M34 2 L30 -46 L40 -48 L44 2 Z M156 2 L160 -48 L170 -46 L166 2 Z' fill='#C8902A'/>")
    # 金貨の 山
    R = rnd(41)
    o += ("<path d='M4 10 C14 -22 52 -34 100 -33 C148 -34 186 -22 196 10 Z' fill='#C8902A'/>"
          "<path d='M12 8 C22 -18 56 -28 100 -27 C144 -28 178 -18 188 8 Z' fill='#F2C14E'/>")
    coins = []
    for i in range(46):
        t = R.random()
        cx = 12 + t * 176
        top = -26 * math.sin(math.pi * (0.06 + 0.88 * t)) - 2
        coins.append((R.uniform(top, 8), cx, R.uniform(5.5, 7.6), R.uniform(-28, 28)))
    for cy, cx, r, a in sorted(coins):
        o += (f"<g transform='translate({f(cx)} {f(cy)}) rotate({f(a)})'><ellipse rx='{f(r)}' ry='{f(r * 0.6)}' fill='#C8902A'/>"
              f"<ellipse cy='-1.1' rx='{f(r)}' ry='{f(r * 0.58)}' fill='#F2C14E'/><ellipse cy='-1.3' rx='{f(r * 0.6)}' ry='{f(r * 0.32)}' fill='none' stroke='#C8902A' stroke-width='1'/>"
              f"<ellipse cx='{f(-r * 0.35)}' cy='-2.4' rx='{f(r * 0.3)}' ry='{f(r * 0.13)}' fill='#FFF0A8'/></g>")
    for gx, gy, c1, c2 in ((52, -16, '#E0284A', '#8E1028'), (104, -26, '#27B07A', '#12654A'), (146, -14, '#3E7BE0', '#1E3E8E')):
        o += (f"<path d='M{gx - 8} {gy} L{gx - 4.4} {gy - 6} H{gx + 4.4} L{gx + 8} {gy} L{gx} {gy + 9} Z' fill='{c1}' stroke='{c2}' stroke-width='1.2'/>"
              f"<path d='M{gx - 4.4} {gy - 6} L{gx - 1.4} {gy} L{gx} {gy - 6} M{gx - 8} {gy} H{gx + 8}' fill='none' stroke='{c2}' stroke-width='.8' opacity='.8'/>"
              f"<path d='M{gx - 3} {gy - 4.6} L{gx - 1.2} {gy - 1}' stroke='#FFFFFF' stroke-width='1.4' opacity='.9'/>")
    # 箱の 前の 面（ボタン）
    o += ("<rect x='0' y='0' width='200' height='100' rx='10' fill='#8E5E34'/>"
          "<rect x='0' y='0' width='200' height='7' rx='3' fill='#D9AD72' opacity='.8'/>")
    for y in (25, 50, 75):
        o += f"<path d='M3 {y} H197' stroke='#5E3A1E' stroke-width='1.6' opacity='.55'/>"
    R2 = rnd(7)
    for i in range(14):
        x, y = R2.uniform(8, 190), R2.uniform(8, 94)
        o += f"<path d='M{f(x)} {f(y)} q10 {f(R2.uniform(-1.4, 1.4))} 22 0' fill='none' stroke='#6E4626' stroke-width='1' opacity='.4'/>"
    for x in (16, 184):
        o += (f"<rect x='{x - 9}' y='0' width='18' height='100' fill='#C8902A'/><rect x='{x - 9}' y='0' width='5' height='100' fill='#F2C14E'/>"
              f"<rect x='{x + 5}' y='0' width='4' height='100' fill='#8A5A14' opacity='.7'/>")
        for y in (12, 50, 88):
            o += f"<circle cx='{x}' cy='{y}' r='2.6' fill='#8A5A14'/><circle cx='{x - 0.8}' cy='{y - 0.8}' r='1' fill='#FFE58A'/>"
    o += ("<rect x='-2' y='90' width='204' height='12' rx='4' fill='#5E3A1E'/>"
          "<path d='M88 74 H112 V92 Q100 100 88 92 Z' fill='#F2C14E' stroke='#8A5A14' stroke-width='1.6'/>"
          "<circle cx='100' cy='81' r='3' fill='#3A2410'/><path d='M98.6 82 L97.6 89 H102.4 L101.4 82 Z' fill='#3A2410'/>")
    return (f'<i class="prf" aria-hidden="true"><svg viewBox="-6 -80 212 186" width="212" height="186">{o}</svg></i>')


def push_decor(sfx=''):
    """まわりの キラッ（金・小さく ゆっくり）と うかぶ 金貨"""
    o = ''
    for j, (x, y, r) in enumerate(((22, -40, 7), (180, -50, 6), (-14, 20, 5), (214, 30, 6), (100, -76, 5.4), (58, -64, 4.6))):
        o += f'<path class="prtw" d="{sparkle_d(x, y, r, 0.18)}" fill="#FFF3B8" style="animation-delay:{-0.6 * j:.2f}s"/>'
    for j, (x, y, r) in enumerate(((-24, -24, 7.5), (226, -8, 7))):
        o += (f'<g transform="translate({x} {y})"><g class="prco" style="animation-delay:{-1.1 * j:.1f}s"><ellipse rx="{r}" ry="{r}" fill="#C8902A"/>'
              f'<ellipse cy="-.8" rx="{r}" ry="{r * 0.96:.1f}" fill="#F2C14E"/><ellipse cy="-.8" rx="{r * 0.64:.1f}" ry="{r * 0.62:.1f}" fill="none" stroke="#C8902A" stroke-width="1.2"/>'
              f'<path d="M{-r * 0.3:.1f} {-r * 0.5:.1f} q{r * 0.3:.1f} {-r * 0.1:.1f} {r * 0.5:.1f} 0" stroke="#FFF6C8" stroke-width="1.4" fill="none" stroke-linecap="round"/></g></g>')
    return f'<i class="prd" aria-hidden="true"><svg viewBox="-40 -100 280 230" width="280" height="230">{o}</svg></i>'


def _coin(c1='#F2C14E', c2='#C8902A'):
    return doc(24, 24, f"<ellipse cx='12' cy='12.6' rx='10.5' ry='10' fill='{c2}'/><ellipse cx='12' cy='11.6' rx='10.5' ry='9.8' fill='{c1}'/>"
                       f"<ellipse cx='12' cy='11.6' rx='6.6' ry='6.2' fill='none' stroke='{c2}' stroke-width='1.3'/><path d='M7.4 8.2 q3 -2 6 -.4' stroke='#FFF6C8' stroke-width='1.6' fill='none' stroke-linecap='round'/>")


def _gem(c1, c2):
    return doc(22, 20, f"<path d='M2 7 L6 1 H16 L20 7 L11 19 Z' fill='{c1}' stroke='{c2}' stroke-width='1.2'/><path d='M6 1 L9 7 L11 1 M2 7 H20' fill='none' stroke='{c2}' stroke-width='.8'/>"
                       f"<path d='M7 3 L8.6 6' stroke='#FFFFFF' stroke-width='1.4' opacity='.9'/>")


PIECES = dict(co=piece(_coin()), gr=piece(_gem('#E0284A', '#8E1028')), gg=piece(_gem('#27B07A', '#12654A')), gb=piece(_gem('#3E7BE0', '#1E3E8E')),
              pe='border-radius:50%;background:radial-gradient(circle at 35% 35%,#FFFFFF,#EDE6D8 55%,#B8AE9C)')


def push_burst():
    return fly_burst('pr', ['co', 'co', 'gr', 'co', 'gg', 'pe', 'co', 'gb'], 30, 31, sizes=dict(co=(15, 21), gr=(13, 17), gg=(13, 17), gb=(13, 17), pe=(7, 10)))


PUSH_CSS = r'''
/* ---------- 海賊の的中ボタン：宝箱のPUSH（壁紙パック） ----------
   ボタンが まるごと 宝箱：前の 面（木の 板・金の 帯と びょう・かぎ穴）に「PUSH」。上に ひらいた ふた（赤い 布）と あふれる 金貨・宝石。
   まわりに 金の キラッ（小さく ゆっくり）と うかぶ 金貨。上下の 動きは 的中と 同じ。押すと 箱が ちぢんで ふくらみ（強く 光らせない）、
   金貨・宝石・真珠が はじけて 落ち、金の 光の 輪が 広がる */
.pr{--pushA:#8E5E34;--pushB:#3E2615;--pushC:#C8902A;--rim:#F2C14E;--rimD:#5E3A1E}
.push.pr{--pr:10px;background:none;border-radius:10px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(40,20,6,.55)) drop-shadow(0 18px 24px rgba(0,0,0,.4))}
.push.pr span{top:-4px;font:400 40px/1 "Zen Antique",serif;letter-spacing:.06em;color:#FFE58A;text-shadow:0 3px 0 #5A3410,0 -1px 0 #FFF6C8,0 0 12px rgba(255,214,110,.5)}
.push.pr::after{inset:-20px -18px -14px;top:-90px;border-radius:30px;border-color:rgba(242,193,78,.9)}
.pr .prf{position:absolute;left:-6px;top:-80px;width:212px;height:186px;pointer-events:none;font-style:normal}
.pr .prf svg{display:block;width:212px;height:186px;overflow:visible}
.pr .prd{position:absolute;left:-40px;top:-100px;width:280px;height:230px;pointer-events:none;z-index:3;font-style:normal}
.pr .prd svg{display:block;width:280px;height:230px;overflow:visible}
.pr .prtw{transform-box:fill-box;transform-origin:50% 50%;animation:prTw 2.6s ease-in-out infinite}
@keyframes prTw{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1.05) rotate(20deg)}}
.pr .prco{animation:prCo 2.8s ease-in-out infinite alternate}
@keyframes prCo{from{transform:translate(0,-4px) rotate(-10deg)}to{transform:translate(0,4px) rotate(10deg)}}
.pshadow.pr{width:220px}
.tap.pr{font-family:"Zen Antique",serif;font-weight:400;color:#FFE58A;letter-spacing:.12em;text-shadow:0 2px 0 #3E2615,0 0 10px rgba(242,193,78,.6)}
.pressed.pr{border-radius:10px;background:#8E5E34;box-shadow:0 0 0 4px #F2C14E,0 7px 0 4px #3E2615;animation-name:prPress,fxH}
@keyframes prPress{0%{transform:scale(1)}22%{transform:scale(.9,.86)}45%{transform:scale(1.08)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.pr .prtw,.pr .prco{animation:none}.clips.pr{display:none}}
''' + fly_css('pr', 'rgba(242,193,78,.9)', PIECES)

PUSH = dict(code='pr', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
