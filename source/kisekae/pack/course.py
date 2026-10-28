"""壁紙パック ②競馬場（上から見た）（まさちゃんの 指定「真上から見たコース。馬群が周回して、ゴール前で1頭が抜け出す」
   第4.93版の 直し「赤丸の雲の影はもう少し雲っぽくして！青丸の馬達をもっとリアルな🐎にして！12秒に一回ランダムにゴールするようにして！」）
   上の絵：真上から 見た 競馬場。外がわの 芝コース（白い 内ラチ・外ラチ・ハロン棒）・内がわの ダートコース・まん中の 芝生（刈った すじ）と 池（噴水）と 蹄鉄の 形の 花だん・
     下に スタンドの 屋根と お客さん・まわりに 木。ゴールは 下の 直線の 右（赤と白の ゴール板・白い 線）。
   馬（第4.93版）：真上から 見た サラブレッドと 騎手（こし・胴・肩・首・頭・耳・前髪・たてがみ・顔の 白い すじ・ギャロップで 前後に のびる 4本の 足・なびく しっぽ・
     前かがみの 騎手＝ヘルメット・勝負服の せなか（もよう）・うで・白い ズボンの ひざ・ブーツ・手綱・鞍の 下の 布・影）を 6コマで めくる（make/course_art.py → 1まいの 絵）。
   動き：8頭の 馬群が 芝コースを 左回りに 周回する（1周 12秒＝12秒に 1回 ゴール）。馬群は 3つの 進路に ずれて ならぶ。周ごとに ちがう 馬
     （6周＝72秒で ばらばらの 順）が 外へ 出て 加速し、ゴール前で 抜け出して 先頭で ゴール（うしろの 馬ほど 早く 動きだす）→ ゴールの あと 外を ゆっくり もとの 場所へ もどる。
     雲の かげ（まるい もこもこが かこむ 雲の 形・ふちは やわらかい）が 3つ ゆっくり 流れる・池の 噴水の 波紋が ひろがる"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, kf, img, rnd, reduced, fly_burst, fly_css, piece, mix, smooth

ID = 'course'

# ---------------------------------------------------------------- コースの 形（芝コースの まん中の 線：下の 直線 → 右の カーブ → 上の 直線 → 左の カーブ）
XA, XB, YC, R = 98, 292, 78, 56      # 直線の 左右の はし・まん中の 高さ・カーブの 半径
YT, YB = YC - R, YC + R              # 上の 直線（22）・下の 直線（134）
TURF_W = 22                          # 芝コースの はば（まん中 ±11）
DIRT_W = 13                          # ダートコースの はば
FIN_X = 270                          # ゴール（下の 直線）
LAP = 12.0                           # 1周の 秒（第4.93版：12秒に 1回 ゴール）
SEG = [('s', FIN_X, XB), ('c', XB, 90, -90), ('s', XB, XA), ('c', XA, 270, 90), ('s', XA, FIN_X)]


def _segs():
    out = []
    for sg in SEG:
        if sg[0] == 's':
            out.append(('s', sg[1], sg[2], abs(sg[2] - sg[1])))
        else:
            out.append(('c', sg[1], sg[2], sg[3], math.radians(abs(sg[2] - sg[3])) * R))
    return out


SEGS = _segs()
L = sum(s[-1] for s in SEGS)          # 1周の 長さ（約 740）


def at(s, d=0.0):
    """芝コースの まん中の 線で ゴールから s（左回り）・外へ d の 点と 向き°（0＝右・90＝下）"""
    s %= L
    for sg in SEGS:
        n = sg[-1]
        if s <= n:
            if sg[0] == 's':
                x0, x1 = sg[1], sg[2]
                if x1 > x0:                       # 下の 直線（右へ）
                    return x0 + s, YB + d, 0.0
                return x0 - s, YT - d, 180.0      # 上の 直線（左へ）
            cx, a0, a1 = sg[1], sg[2], sg[3]
            ph = math.radians(a0 - (s / n) * (a0 - a1))      # φ は へっていく（左回り）
            rr = R + d
            x, y = cx + rr * math.cos(ph), YC + rr * math.sin(ph)
            hd = math.degrees(math.atan2(-math.cos(ph), math.sin(ph)))
            return x, y, hd
        s -= n
    return at(0, d)


# ---------------------------------------------------------------- 絵
def stadium_d(r, x0=XA, x1=XB, yc=YC):
    """競馬場の 形（直線と 半円）：まん中の 線から 半径 r"""
    return (f'M{f(x0)} {f(yc - r)} H{f(x1)} A{f(r)} {f(r)} 0 0 1 {f(x1)} {f(yc + r)} H{f(x0)} A{f(r)} {f(r)} 0 0 1 {f(x0)} {f(yc - r)} Z')


def ground_svg():
    """止まった 下の 絵：まわりの 芝・木・スタンド・コース・まん中の 芝生・池・花だん・ゴール板"""
    R0 = rnd(4)
    ro, ri = R + TURF_W / 2, R - TURF_W / 2            # 芝コースの 外・内
    rd = ri - DIRT_W                                    # ダートの 内
    defs = ("<pattern id='mw' width='16' height='16' patternUnits='userSpaceOnUse' patternTransform='rotate(28)'>"
            "<rect width='16' height='16' fill='#5DAF54'/><rect width='8' height='16' fill='#67B95C'/></pattern>"
            "<pattern id='tf' width='12' height='12' patternUnits='userSpaceOnUse' patternTransform='rotate(90)'>"
            "<rect width='12' height='12' fill='#7FC66C'/><rect width='6' height='12' fill='#86CC72'/></pattern>"
            "<pattern id='og' width='18' height='18' patternUnits='userSpaceOnUse' patternTransform='rotate(-20)'>"
            "<rect width='18' height='18' fill='#4E9A4A'/><rect width='9' height='18' fill='#549F4F'/></pattern>"
            "<radialGradient id='pd' cx='.4' cy='.35' r='.7'><stop offset='0' stop-color='#8ED4F2'/><stop offset='1' stop-color='#3E96CC'/></radialGradient>")
    o = f"<rect width='{W}' height='{H}' fill='url(#og)'/>"
    # 外の 道（コースの まわりの うすい 通路）
    o += f"<path d='{stadium_d(ro + 6)}' fill='#C9D8B8'/>"
    o += f"<path d='{stadium_d(ro + 3)}' fill='#9CC58A'/>"
    # 芝コース・ダート・まん中の 芝生
    o += f"<path d='{stadium_d(ro)}' fill='url(#tf)'/>"
    o += f"<path d='{stadium_d(ri)}' fill='#C8A272'/>"
    for k in range(5):                                                            # ダートの 砂の すじ（ハローの あと）
        o += f"<path d='{stadium_d(ri - 2.2 - k * 2.2)}' fill='none' stroke='#B8925F' stroke-width='.5' opacity='.6'/>"
    o += f"<path d='{stadium_d(rd)}' fill='url(#mw)'/>"
    # ラチ（白い 柵：外ラチ・芝の 内ラチ・ダートの 内ラチ）と 影
    for rr, w in ((ro, 1.6), (ri, 1.4), (rd, 1.2)):
        o += f"<path d='{stadium_d(rr)}' fill='none' stroke='#2E5A2A' stroke-width='{w + 1}' opacity='.25' transform='translate(.8 1.2)'/>"
        o += f"<path d='{stadium_d(rr)}' fill='none' stroke='#FFFFFF' stroke-width='{w}'/>"
    # ハロン棒（内ラチに そって 小さな 色の 印）
    for k in range(12):
        x, y, hd = at(k * L / 12, -TURF_W / 2 - 1.5)
        c = '#E23B3B' if k % 3 == 0 else '#2B6FD0' if k % 3 == 1 else '#F2C14E'
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='1.5' fill='{c}' stroke='#FFFFFF' stroke-width='.6'/>"
    # まん中の 芝生：池（噴水）・蹄鉄の 形の 花だん・小道
    o += "<path d='M122 90 C140 102 170 104 196 96 C220 88 240 90 262 98' fill='none' stroke='#E8DFC8' stroke-width='3' stroke-linecap='round' opacity='.85'/>"
    px, py = 150, 72
    o += (f"<ellipse cx='{px + 1.5}' cy='{py + 2}' rx='34' ry='15' fill='#2E6A3A' opacity='.35'/>"
          f"<path d='M{px - 34} {py} C{px - 34} {py - 12} {px - 14} {py - 17} {px + 4} {py - 15} C{px + 24} {py - 14} {px + 36} {py - 8} {px + 34} {py + 2} "
          f"C{px + 32} {py + 12} {px + 12} {py + 16} {px - 8} {py + 15} C{px - 26} {py + 14} {px - 34} {py + 9} {px - 34} {py} Z' fill='url(#pd)' stroke='#D9CBA8' stroke-width='1.6'/>"
          f"<path d='M{px - 26} {py - 6} q10 -6 22 -6' fill='none' stroke='#FFFFFF' stroke-width='1.4' stroke-linecap='round' opacity='.6'/>"
          f"<circle cx='{px + 4}' cy='{py}' r='3.4' fill='#E8F6FC' stroke='#B8D8E8' stroke-width='.8'/><circle cx='{px + 4}' cy='{py}' r='1.4' fill='#FFFFFF'/>")
    hx, hy = 236, 72                                                              # 蹄鉄の 花だん（U が 上に ひらく）
    so, si = [], []
    for k in range(29):
        a = math.radians(-205 + 230 * k / 28)
        so.append((hx + math.cos(a) * 20, hy - math.sin(a) * 18))
        si.append((hx + math.cos(a) * 11, hy - math.sin(a) * 9.5))
    o += f"<path d='{P(so + si[::-1])}' fill='#8B6A3E' transform='translate(1 1.4)' opacity='.35'/>"
    o += f"<path d='{P(so + si[::-1])}' fill='#7A5A32'/>"
    for k in range(40):
        t = R0.random()
        a = math.radians(-200 + 220 * t)
        rr = R0.uniform(12.6, 18.6)
        x, y = hx + math.cos(a) * rr, hy - math.sin(a) * rr * 0.9
        c = R0.choice(('#F25C7A', '#FFD23F', '#FFFFFF', '#F28A3B', '#C86BE0'))
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='{f(R0.uniform(1.1, 1.8))}' fill='{c}'/>"
    # まわりの 木（上と 左右）
    trees = [(8, 6, 9), (30, 3, 7), (52, 2, 6), (330, 3, 8), (354, 6, 9), (380, 4, 7), (6, 40, 8), (12, 70, 7), (5, 104, 9), (14, 132, 7),
             (382, 38, 8), (376, 72, 7), (384, 104, 8), (378, 132, 7), (200, 1, 5), (232, 1, 6), (164, 1, 5), (118, 2, 6), (270, 2, 6)]
    for x, y, r in trees:
        o += (f"<circle cx='{x + 2}' cy='{y + 3}' r='{r}' fill='#24502A' opacity='.35'/><circle cx='{x}' cy='{y}' r='{r}' fill='#3E8E45'/>"
              f"<circle cx='{f(x - r * 0.3)}' cy='{f(y - r * 0.3)}' r='{f(r * 0.55)}' fill='#55A85A'/><circle cx='{f(x - r * 0.4)}' cy='{f(y - r * 0.45)}' r='{f(r * 0.22)}' fill='#7CC47A'/>")
    # スタンド（下）：屋根・前の お客さん（外ラチと スタンドの あいだ）
    o += ("<rect x='56' y='152' width='270' height='12' rx='1.5' fill='#5A6670' opacity='.35'/>"
          "<rect x='54' y='151' width='270' height='12' rx='1.5' fill='#EEF0F2'/>"
          "<rect x='54' y='151' width='270' height='1.6' fill='#FFFFFF'/>")
    for i in range(54):
        x = 58 + i * 4.95
        o += f"<path d='M{f(x)} 153.4 v7' stroke='#C9CED4' stroke-width='.8'/>"
    for i in range(150):
        x = R0.uniform(56, 322)
        o += f"<circle cx='{f(x)}' cy='{f(R0.uniform(147.2, 149.8))}' r='.95' fill='{R0.choice(('#E85A5A', '#4A7BD0', '#F2C14E', '#FFFFFF', '#3A3A44', '#F28A3B', '#2FA35A'))}'/>"
    for i in range(16):
        x = R0.uniform(10, 50) if i < 8 else R0.uniform(332, 386)
        o += f"<circle cx='{f(x)}' cy='{f(R0.uniform(150, 158))}' r='1.1' fill='{R0.choice(('#E85A5A', '#4A7BD0', '#F2C14E', '#FFFFFF', '#3A3A44'))}'/>"
    # ゴール（下の 直線）：白い 線・ゴール板（赤と 白の 丸い 札：内ラチの 内がわ）・決勝審判の 小さな 塔（外ラチの 外）
    gy0, gy1 = YB - TURF_W / 2, YB + TURF_W / 2
    o += f"<path d='M{FIN_X} {gy0} V{gy1}' stroke='#FFFFFF' stroke-width='1.6' opacity='.95'/>"
    o += (f"<circle cx='{FIN_X + 1.2}' cy='{gy0 - 5}' r='4.8' fill='#1E3A1E' opacity='.3'/>"
          f"<circle cx='{FIN_X}' cy='{gy0 - 6}' r='4.8' fill='#FFFFFF'/><circle cx='{FIN_X}' cy='{gy0 - 6}' r='3.6' fill='#E23B3B'/><circle cx='{FIN_X}' cy='{gy0 - 6}' r='1.6' fill='#FFFFFF'/>")
    o += f"<rect x='{FIN_X - 4}' y='{gy1 + 1.2}' width='8' height='5' rx='1' fill='#D9DEE4' stroke='#8A949E' stroke-width='.6'/>"
    return doc(W, H, o, defs=defs)


SILKS = [  # (勝負服, 袖, 帽子, 毛色)
    ('#FFFFFF', '#2B6FD0', '#FFFFFF', '#8A5230'),
    ('#2A2A30', '#E23B3B', '#2A2A30', '#5A3A28'),
    ('#E23B3B', '#FFFFFF', '#E23B3B', '#A0612F'),
    ('#2B6FD0', '#F2C14E', '#2B6FD0', '#3A2A24'),
    ('#FFD23F', '#1E1E24', '#FFD23F', '#C27A3E'),     # 抜け出す 馬（黄色）
    ('#2FA35A', '#FFFFFF', '#2FA35A', '#7A4A2A'),
    ('#F28A3B', '#2A2A30', '#F28A3B', '#D9D2C8'),
    ('#F37BB2', '#2B6FD0', '#F37BB2', '#6A4232'),
]


def horse_sheet(silk, sleeve, cap, coat):
    """真上から 見た 馬と 騎手（右向き）の 2コマ：足を のばす／あつめる（よこ 2コマ・1コマ 26×14）"""
    mane = mix(coat, '#000000', 0.45)
    lg = mix(coat, '#000000', 0.3)
    out = ''
    for k in range(2):
        ox = k * 26
        o = f"<ellipse cx='{ox + 12.5}' cy='8' rx='10.5' ry='4.2' fill='#1C3A18' opacity='.28'/>"
        if k == 0:            # のばした 足：前足は 首の 下から 前へ・うしろ足は しっぽの よこから うしろへ（よこには 出さない）
            for (x0, y0, x1, y1) in ((16.4, 5.6, 21.4, 5.0), (16.4, 8.4, 20.6, 9.0), (5.6, 5.8, 1.6, 5.0), (5.6, 8.2, 1.8, 9.0)):
                o += f"<path d='M{ox + x0} {y0} L{ox + x1} {y1}' stroke='{lg}' stroke-width='1.3' stroke-linecap='round'/>"
        else:                 # あつめた 足：体の 下（少しだけ 見える）
            for (x0, y0, x1, y1) in ((14.2, 5.0, 15.6, 4.2), (14.2, 9.0, 15.6, 9.8), (7.8, 5.0, 6.6, 4.2), (7.8, 9.0, 6.6, 9.8)):
                o += f"<path d='M{ox + x0} {y0} L{ox + x1} {y1}' stroke='{lg}' stroke-width='1.2' stroke-linecap='round'/>"
        o += (f"<path d='M{ox + 3.6} 7 L{ox + 0.4} {6.2 if k == 0 else 5.6} L{ox + 0.6} {7.8 if k == 0 else 8.6} Z' fill='{mane}'/>"       # しっぽ
              f"<ellipse cx='{ox + 10.8}' cy='7' rx='7.8' ry='3.2' fill='{coat}'/>"
              f"<path d='M{ox + 16} 5.4 Q{ox + 19.6} 5.6 {ox + 21.8} 6.2 Q{ox + 23.6} 7 {ox + 21.8} 7.8 Q{ox + 19.6} 8.4 {ox + 16} 8.6 Z' fill='{coat}'/>"   # 首と 頭
              f"<path d='M{ox + 15.6} 6.4 Q{ox + 18.6} 6.6 {ox + 20.6} 7 Q{ox + 18.6} 7.4 {ox + 15.6} 7.6 Z' fill='{mane}'/>"
              f"<circle cx='{ox + 20.4}' cy='6.1' r='.55' fill='{mane}'/><circle cx='{ox + 20.4}' cy='7.9' r='.55' fill='{mane}'/>"
              f"<rect x='{ox + 8.4}' y='3.9' width='4.4' height='6.2' rx='1' fill='#FFFFFF'/>"                                               # ゼッケン
              f"<path d='M{ox + 12.6} 4.6 L{ox + 16.4} 5.8 M{ox + 12.6} 9.4 L{ox + 16.4} 8.2' stroke='{sleeve}' stroke-width='1.5' stroke-linecap='round'/>"   # 腕（手綱へ）
              f"<ellipse cx='{ox + 11.6}' cy='7' rx='2.6' ry='3' fill='{silk}' stroke='{mix(silk, '#000000', .3)}' stroke-width='.4'/>"
              f"<circle cx='{ox + 13.3}' cy='7' r='1.55' fill='{cap}' stroke='{mix(cap, '#000000', .35)}' stroke-width='.4'/>")
        out += o
    return doc(52, 14, out)


# ---------------------------------------------------------------- 真上から 見た サラブレッドと 騎手（第4.93版：上の絵の 馬。的中ボタンの まわりの 小さな 馬は 上の horse_sheet の まま）
NF = 6                      # ギャロップ 1回の コマ
GAL = 0.42                  # ギャロップ 1回の 秒
CW, CH = 42, 18             # 1コマの 大きさ（絵の 単位・右向き・鼻先が 右）
HS2 = 0.95                  # 絵の 単位 → 画面の px（1頭 約 40×17px）
PATS = ['hoop', 'plain', 'sash', 'halves', 'plain', 'dots', 'hoop', 'sash']          # 勝負服の もよう（せなか）
MANES = ['#1C1410', '#140E0C', '#6A3416', '#120E0C', '#7E4218', '#1C1410', '#8C867E', '#1A1210']   # たてがみと しっぽ
LEGS = ['#2A1E18', '#1E1612', '#7A4422', '#1A1412', '#8E5226', '#2A1E18', '#A8A29A', '#241A14']    # 足の 下の ほう
# 胴の 形：(せなかの 線の x, 半分の はば)。しっぽの 根もと → 鼻先（1単位 ≒ 9.4cm）。NECK0 より 前（首と 頭）は のびる（reach）
BODY = [(7.2, 0.0), (7.5, 1.6), (8.4, 2.6), (10.0, 3.1), (12.2, 3.3), (14.6, 3.38), (17.0, 3.3), (19.2, 3.15), (21.0, 2.9), (22.6, 2.5),
        (24.0, 2.22), (26.0, 1.98), (28.0, 1.74), (29.6, 1.52), (30.5, 1.45), (31.5, 1.66), (33.0, 1.5), (34.6, 1.22), (35.8, 0.98), (36.7, 0.72),
        (37.2, 0.34), (37.35, 0.0)]
NECK0 = 23.0
BLAZE = [True, False, False, True, False, True, False, False]           # 顔の 白い すじ


def _sp(pts, close=True):
    return smooth([(round(x, 2), round(y, 2)) for x, y in pts], close)


def _leg(o, x0, y0, x1, y1, x2, y2, col, low, w0, w1):
    """足（つけ根 → ひざ／飛節 → ひづめ）：上は 毛色・下は 濃い 色・ひづめ"""
    o += f"<path d='M{f(x0)} {f(y0)} L{f(x1)} {f(y1)}' stroke='{col}' stroke-width='{f(w0)}' stroke-linecap='round'/>"
    o += f"<path d='M{f(x1)} {f(y1)} L{f(x2)} {f(y2)}' stroke='{low}' stroke-width='{f(w1)}' stroke-linecap='round'/>"
    o += f"<ellipse cx='{f(x2)}' cy='{f(y2)}' rx='.48' ry='.42' fill='#141010'/>"
    return o


def top_frame(k, fi, ox):
    """馬 k の ギャロップの コマ fi（0〜NF-1）。ox：シートの 中の 左はし。右向き・まん中の 線 y=9（光は 左上から：下がわに かげ）"""
    silk, sleeve, cap, coat = SILKS[k]
    mane, low, pat = MANES[k], LEGS[k], PATS[k]
    th = fi / NF
    c2 = math.cos(2 * math.pi * th)
    reach = 0.5 + 0.5 * c2                            # 首を のばす（前足を のばす とき）
    yc = 9.0
    nx = lambda x: x if x < NECK0 else x + 0.9 * reach * (x - NECK0) / (37.5 - NECK0)
    X = lambda x: ox + nx(x)
    shade = mix(coat, '#000000', 0.30)
    light = mix(coat, '#FFFFFF', 0.28)
    o = f"<ellipse cx='{f(ox + 20.5)}' cy='{f(yc + 0.8)}' rx='15.5' ry='4.0' fill='#14300F' opacity='.28' filter='url(#sb)'/>"   # 影
    # 足：ギャロップ（左右で ずれる）。前足は 首の 下から 前へ、うしろ足は こしの うしろへ のびる
    for s_, lag in ((1, 0.0), (-1, 0.16)):
        e = 0.5 + 0.5 * math.cos(2 * math.pi * (th - lag))
        fx_ = 20.5 + 11.5 * e                         # 前の ひづめ
        o = _leg(o, ox + 21.0, yc + s_ * 1.4, ox + nx(21.0 + (fx_ - 21.0) * 0.52), yc + s_ * (1.75 + 0.6 * e), ox + nx(fx_), yc + s_ * (1.55 + 0.45 * e), coat, low, 1.3, 0.78)
        e2 = 0.5 + 0.5 * math.cos(2 * math.pi * (th - lag - 0.07))
        hx_ = 15.0 - 10.6 * e2                        # うしろの ひづめ
        o = _leg(o, ox + 11.8, yc + s_ * 1.7, ox + 11.8 + (hx_ - 11.8) * 0.48 - 0.5 * (1 - e2), yc + s_ * (2.15 + 0.55 * e2), ox + hx_, yc + s_ * (1.8 + 0.4 * e2), coat, low, 1.4, 0.8)
    # しっぽ（根もとは 太く、うしろへ なびく）
    cl = []
    for i in range(10):
        t = i / 9
        x = 8.0 - 7.2 * t
        y = yc + 0.85 * math.sin(2 * math.pi * (0.75 * t - th)) * t
        hw = 1.0 * (1 - t) ** 0.6 + 0.18
        cl.append((x, y, hw))
    o += f"<path d='{_sp([(ox + x, y - w) for x, y, w in cl] + [(ox + x, y + w) for x, y, w in cl][::-1])}' fill='{mane}'/>"
    # 胴・首・頭：毛色 → 下がわの かげ（体の 形で 切る）→ つや
    pu = [(X(x), yc - w) for x, w in BODY]
    pl = [(X(x), yc + w) for x, w in BODY[::-1][1:-1]]
    body = _sp(pu + pl)
    o += f"<path d='{body}' fill='{coat}'/>"
    o += f"<g clip-path='url(#bc{fi})'><path d='{_sp([(X(x), yc + w * 0.30) for x, w in BODY] + [(X(x), yc + w + 1) for x, w in BODY[::-1]])}' fill='{shade}'/></g>"
    o += f"<path d='{_sp([(ox + 8.6, yc - 1.2), (ox + 11.2, yc - 2.2), (ox + 13.6, yc - 1.4), (ox + 11.0, yc - 0.6)])}' fill='{light}' opacity='.55'/>"      # こしの つや
    o += f"<path d='{_sp([(ox + 18.6, yc - 1.8), (ox + 21.0, yc - 2.2), (ox + 22.4, yc - 1.2), (ox + 20.2, yc - 0.9)])}' fill='{light}' opacity='.45'/>"   # 肩の つや
    o += f"<path d='M{f(ox + 7.9)} {f(yc)} L{f(ox + 11.4)} {f(yc)}' stroke='{shade}' stroke-width='.32' opacity='.7' stroke-linecap='round'/>"           # こしの みぞ
    # 頭：白い すじ・耳・前髪・目・鼻の あな
    if BLAZE[k]:
        o += f"<path d='{_sp([(X(32.0), yc - 0.3), (X(33.0), yc - 0.24), (X(35.4), yc - 0.28), (X(36.6), yc - 0.38), (X(36.9), yc), (X(36.6), yc + 0.38), (X(35.4), yc + 0.28), (X(33.0), yc + 0.24), (X(32.0), yc + 0.3)])}' fill='#F2EEE6'/>"
    for s_ in (-1, 1):
        o += f"<ellipse cx='{f(X(32.6))}' cy='{f(yc + s_ * 1.25)}' rx='.36' ry='.2' fill='#120C0A'/>"
        o += f"<ellipse cx='{f(X(36.9))}' cy='{f(yc + s_ * 0.36)}' rx='.2' ry='.13' fill='{shade}'/>"
    xp = X(30.3)
    for s_ in (-1, 1):                                                                                              # 耳（前向き 外へ）
        o += f"<path d='M{f(xp - 0.7)} {f(yc + s_ * 0.6)} Q{f(xp + 0.3)} {f(yc + s_ * 2.05)} {f(xp + 1.35)} {f(yc + s_ * 1.85)} Q{f(xp + 0.65)} {f(yc + s_ * 0.95)} {f(xp - 0.7)} {f(yc + s_ * 0.6)} Z' fill='{coat}' stroke='{shade}' stroke-width='.22'/>"
        o += f"<path d='M{f(xp - 0.2)} {f(yc + s_ * 0.85)} Q{f(xp + 0.45)} {f(yc + s_ * 1.6)} {f(xp + 1.0)} {f(yc + s_ * 1.6)}' fill='none' stroke='{shade}' stroke-width='.3' opacity='.7'/>"
    # たてがみ（首の 上の まん中から 少し 下がわへ）と 前髪
    mp = [(X(22.4), yc - 0.4), (X(24.4), yc + 0.05), (X(26.4), yc + 0.55), (X(28.4), yc + 0.62), (X(30.0), yc + 0.4), (X(30.6), yc + 0.05),
          (X(30.2), yc - 0.35), (X(28.2), yc - 0.3), (X(26.0), yc - 0.4), (X(24.0), yc - 0.7)]
    o += f"<path d='{_sp(mp)}' fill='{mane}'/>"
    o += f"<path d='M{f(xp - 0.2)} {f(yc - 0.32)} Q{f(xp + 1.5)} {f(yc + 0.05)} {f(xp - 0.2)} {f(yc + 0.36)} Z' fill='{mane}'/>"
    bx = X(35.6)
    # 騎手（前かがみ）：鞍の 下の 布・ひざ・ブーツ・せなか（勝負服）・うで・手袋・手綱・ヘルメット
    jx = -0.16 * c2
    for s_ in (-1, 1):
        o += f"<path d='M{f(ox + 16.4)} {f(yc + s_ * 3.22)} L{f(ox + 19.4)} {f(yc + s_ * 3.08)}' stroke='#FFFFFF' stroke-width='.55' stroke-linecap='round'/>"
        kx, ky = ox + 22.0 + jx, yc + s_ * 2.9
        o += f"<path d='M{f(ox + 19.6 + jx)} {f(yc + s_ * 1.1)} L{f(kx)} {f(ky)}' stroke='#F4F1EA' stroke-width='1.2' stroke-linecap='round'/>"
        o += f"<path d='M{f(kx)} {f(ky)} L{f(kx - 1.6)} {f(ky + s_ * 0.3)}' stroke='#151112' stroke-width='1.0' stroke-linecap='round'/>"
    tx = ox + 21.0 + jx
    torso = (f"M{f(tx - 1.9)} {f(yc - 1.4)} Q{f(tx + 0.4)} {f(yc - 2.35)} {f(tx + 1.9)} {f(yc - 1.8)} Q{f(tx + 2.65)} {f(yc)} {f(tx + 1.9)} {f(yc + 1.8)} "
             f"Q{f(tx + 0.4)} {f(yc + 2.35)} {f(tx - 1.9)} {f(yc + 1.4)} Q{f(tx - 2.6)} {f(yc)} {f(tx - 1.9)} {f(yc - 1.4)} Z")
    o += f"<path d='{torso}' fill='{silk}'/>"
    if pat == 'hoop':
        o += f"<g clip-path='url(#jt{fi})'><path d='M{f(tx - 0.75)} {f(yc - 3)} V{f(yc + 3)} M{f(tx + 0.75)} {f(yc - 3)} V{f(yc + 3)}' stroke='{sleeve}' stroke-width='.62'/></g>"
    elif pat == 'sash':
        o += f"<g clip-path='url(#jt{fi})'><path d='M{f(tx - 2.2)} {f(yc - 2.4)} L{f(tx + 2.2)} {f(yc + 2.4)}' stroke='{sleeve}' stroke-width='.92'/></g>"
    elif pat == 'halves':
        o += f"<g clip-path='url(#jt{fi})'><rect x='{f(tx - 3)}' y='{f(yc)}' width='6' height='3' fill='{sleeve}'/></g>"
    elif pat == 'dots':
        for dx_, dy_ in ((-1.0, -0.9), (0.5, -1.15), (-0.5, 0.75), (0.9, 0.85)):
            o += f"<circle cx='{f(tx + dx_)}' cy='{f(yc + dy_)}' r='.42' fill='{sleeve}'/>"
    o += f"<g clip-path='url(#jt{fi})'><rect x='{f(tx - 3)}' y='{f(yc + 0.9)}' width='6' height='2' fill='#000000' opacity='.16'/></g>"
    o += f"<path d='{torso}' fill='none' stroke='{mix(silk, '#000000', .35)}' stroke-width='.2'/>"
    hx = X(25.6)
    for s_ in (-1, 1):
        o += f"<path d='M{f(tx + 1.4)} {f(yc + s_ * 1.6)} Q{f(tx + 2.8)} {f(yc + s_ * 1.75)} {f(hx)} {f(yc + s_ * 1.1)}' fill='none' stroke='{sleeve}' stroke-width='.85' stroke-linecap='round'/>"
        o += f"<path d='M{f(hx)} {f(yc + s_ * 1.1)} Q{f(X(30.5))} {f(yc + s_ * 1.3)} {f(bx)} {f(yc + s_ * 0.9)}' fill='none' stroke='{mix(coat, '#000000', .55)}' stroke-width='.16' opacity='.8'/>"
        o += f"<circle cx='{f(hx)}' cy='{f(yc + s_ * 1.0)}' r='.36' fill='#F4F1EA'/>"
    hcx = ox + 23.0 + jx
    o += f"<circle cx='{f(hcx + 0.2)}' cy='{f(yc + 0.3)}' r='1.5' fill='#000000' opacity='.18'/>"
    o += f"<circle cx='{f(hcx)}' cy='{f(yc)}' r='1.45' fill='{cap}' stroke='{mix(cap, '#000000', .35)}' stroke-width='.18'/>"
    o += f"<path d='M{f(hcx + 1.15)} {f(yc - 0.95)} Q{f(hcx + 2.05)} {f(yc)} {f(hcx + 1.15)} {f(yc + 0.95)}' fill='none' stroke='{mix(cap, '#000000', .45)}' stroke-width='.42' stroke-linecap='round'/>"
    o += f"<circle cx='{f(hcx - 0.35)}' cy='{f(yc - 0.42)}' r='.42' fill='#FFFFFF' opacity='.5'/>"
    defs = f"<clipPath id='jt{fi}'><path d='{torso}'/></clipPath><clipPath id='bc{fi}'><path d='{body}'/></clipPath>"
    return o, defs


def top_sheet(k):
    """馬 k の ギャロップの シート（右向き・NF コマ・横に ならべる）"""
    silk, sleeve, cap, coat = SILKS[k]
    shade = mix(coat, '#000000', 0.30)
    light = mix(coat, '#FFFFFF', 0.20)
    defs = (f"<linearGradient id='cg' x1='0' y1='{f(9 - 3.8)}' x2='0' y2='{f(9 + 3.8)}' gradientUnits='userSpaceOnUse'>"
            f"<stop offset='0' stop-color='{shade}'/><stop offset='.3' stop-color='{coat}'/><stop offset='.5' stop-color='{light}'/>"
            f"<stop offset='.7' stop-color='{coat}'/><stop offset='1' stop-color='{shade}'/></linearGradient>"
            "<filter id='sb' x='-20%' y='-60%' width='140%' height='220%'><feGaussianBlur stdDeviation='.9'/></filter>")
    body = ''
    for fi in range(NF):
        o, d = top_frame(k, fi, fi * CW)
        body += o
        defs += d
    return doc(CW * NF, CH, body, defs=defs)


# ---------------------------------------------------------------- レース（第4.93版：1周 12秒・周ごとに ちがう 馬が 抜け出して 勝つ）
NL = 6                                                # 1回り（72秒）の 周回数
WINNERS = [4, 1, 6, 2, 7, 3]                          # 周ごとの 勝ち馬（ランダムに 見える ように ばらばらの 順）
SLOTS = [(0, -6.2), (-15, 0), (-30, 6.2), (-44, -6.2), (-59, 0), (-74, 6.2), (-88, -6.2), (-103, 0)]   # 馬群の 中の 場所（前うしろ・内外：3つの 進路を ずらして）
AHEAD = 22                                            # ゴールで 先頭より 前へ
OUT_LANE = 9.6                                        # 抜け出す・もどる ときの 外の 進路
GAIN = 0.30                                           # 抜け出す 馬の はやさ（馬群より 3割 はやい）
U_BACK = 300                                          # ゴールの あと 馬群に もどりおわる


def _ease(q):
    q = min(1.0, max(0.0, q))
    return q * q * (3 - 2 * q)


def surge_from(k):
    """馬 k が 勝つ 周の 抜け出し はじめ（ゴールから の 道のり）：うしろの 馬ほど 早く 動く"""
    return L - max(285.0, (AHEAD - SLOTS[k][0]) / GAIN)


def curve_amt(s, soft=24.0):
    """コースの 道のり s が カーブの 中か（0〜1・さかいは なめらかに）"""
    s %= L
    a, out = 0.0, 0.0
    for sg in SEGS:
        n = sg[-1]
        if sg[0] == 'c':
            lo_, hi_ = a, a + n
            for off in (-L, 0.0, L):
                x0, x1 = lo_ + off, hi_ + off
                v_ = min(1.0, max(0.0, (s - x0 + soft / 2) / soft)) * min(1.0, max(0.0, (x1 - s + soft / 2) / soft))
                out = max(out, v_)
        a += n
    return out


def race_at(k, t):
    """馬 k の 時刻 t（0〜NL×LAP）の (コースの 上の 道のり s, 外へ d, 上に 重ねるか)"""
    v = L / LAP
    j = int(t // LAP) % NL
    u = v * (t % LAP)                                                     # 先頭の いる 所（ゴールから）
    ds, dl = SLOTS[k]
    wob = 1.6 * math.sin(2 * math.pi * t / LAP * 2 + k * 1.7) + 0.8 * math.sin(2 * math.pi * t / (LAP * 3) + k)
    lane = dl + 0.45 * math.sin(2 * math.pi * t / LAP + k * 2.1)
    top = False
    us = surge_from(k)
    if WINNERS[j] == k and u >= us:                                       # この 周の 勝ち馬：外へ 出て 加速 → ゴールで 先頭
        q = (u - us) / (L - us)
        e = _ease(q)
        ds = ds + (AHEAD - ds) * e
        lane = lane + (OUT_LANE - lane) * _ease(q * 3.0)
        wob *= 1 - e
        top = True
    elif WINNERS[(j - 1) % NL] == k and u <= U_BACK:                      # 前の 周の 勝ち馬：ゴールの あと 外を ゆっくり もとの 場所へ
        q = u / U_BACK
        e = _ease(q)
        ds = AHEAD + (ds - AHEAD) * e
        lane = OUT_LANE + (lane - OUT_LANE) * _ease((q - 0.7) / 0.3)
        wob *= e
        top = True
    sp = u + ds + wob
    if lane > 6.6:                                                        # カーブでは 外の 進路を 少し 内へ（外ラチに かからない）
        lane = lane - (lane - 6.6) * 0.75 * curve_amt(sp)
    return sp, lane, top


def keys_for(k, dt=0.05, tol=0.45, tol_a=2.0):
    """馬 k の 1回り（NL 周）の 場所と 向き（@keyframes）。こまかく 計算して、まっすぐ つないで よい 所は まびく"""
    T = NL * LAP
    n = int(round(T / dt))
    pts, prev = [], None
    for i in range(n + 1):
        t = i * dt
        s, d, _ = race_at(k, t)
        x, y, hd = at(s, d)
        if prev is not None:
            while hd - prev > 180:
                hd -= 360
            while hd - prev < -180:
                hd += 360
        prev = hd
        pts.append((t, x, y, hd))
    keep = [0]
    a = 0
    b = a + 2
    while b <= n:
        ta, xa, ya, ha = pts[a]
        tb, xb, yb, hb = pts[b]
        bad = False
        for i in range(a + 1, b):
            ti, xi, yi, hi = pts[i]
            q = (ti - ta) / (tb - ta)
            if (abs(xa + (xb - xa) * q - xi) > tol or abs(ya + (yb - ya) * q - yi) > tol or abs(ha + (hb - ha) * q - hi) > tol_a):
                bad = True
                break
        if bad:
            a = b - 1
            keep.append(a)
            b = a + 2
        else:
            b += 1
    if keep[-1] != n:
        keep.append(n)
    hw, hh = CW * HS2, CH * HS2
    return [(pts[i][0] / T * 100, f'transform:translate({f(pts[i][1] - hw / 2, 1)}px,{f(pts[i][2] - hh / 2, 1)}px) rotate({f(pts[i][3], 1)}deg)') for i in keep]


def z_keys(k):
    """抜け出す 馬は ほかの 馬の 上に（z-index）"""
    T = NL * LAP
    rows, cur = [], None
    for i in range(int(T / 0.1) + 1):
        t = i * 0.1
        z = 3 if race_at(k, t)[2] else 1
        if z != cur:
            rows.append((t / T * 100, f'z-index:{z}'))
            cur = z
    return rows


def ripple_svg():
    return doc(30, 14, "<ellipse cx='15' cy='7' rx='13' ry='6' fill='none' stroke='#FFFFFF' stroke-width='1.2'/>")


def cloud_svg(w, h, seed):
    """雲の かげ：まるい もこもこが まわりを かこむ 雲の 形（ふちは 少し ぼかす・まん中は 少し こい）"""
    R0 = rnd(seed)
    cx, cy = w / 2, h / 2
    rx, ry = w * 0.31, h * 0.25
    n = 10
    puffs = [(cx, cy, None)]
    for i in range(n):
        a = 2 * math.pi * (i + R0.uniform(-0.18, 0.18)) / n
        r = h * (0.17 + 0.07 * R0.random()) * (1.12 if math.sin(a) < 0 else 0.92)          # 上がわの もこもこを 大きく
        puffs.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry, r))
    o = f"<defs><filter id='b' x='-20%' y='-20%' width='140%' height='140%'><feGaussianBlur stdDeviation='{f(w * 0.014 + 0.6, 1)}'/></filter>"
    o += f"<filter id='c' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='{f(w * 0.05, 1)}'/></filter></defs>"
    body = f"<ellipse cx='{f(cx, 1)}' cy='{f(cy, 1)}' rx='{f(rx * 1.02, 1)}' ry='{f(ry * 1.05, 1)}'/>" + ''.join(f"<circle cx='{f(x, 1)}' cy='{f(y, 1)}' r='{f(r, 1)}'/>" for x, y, r in puffs[1:])
    o += f"<g filter='url(#b)' fill='#0E2A10' opacity='.15'>{body}</g>"
    o += f"<ellipse cx='{f(cx, 1)}' cy='{f(cy, 1)}' rx='{f(rx * 0.8, 1)}' ry='{f(ry * 0.75, 1)}' fill='#0E2A10' opacity='.07' filter='url(#c)'/>"
    return doc(w, h, o)


CLOUDS = [  # (はば, 高さ, 種, 秒, はじめ, おわり, おくれ)
    (176, 104, 3, 64.0, (-190, -20), (400, 70), 0.0),
    (136, 82, 8, 78.0, (-150, 60), (400, -30), -30.0),
    (110, 66, 13, 92.0, (-120, 100), (400, 30), -62.0),
]


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    still = B.get('still')
    hs = B.get('horses')
    alt = ('真上から見た競馬場のイラスト。白い柵の芝コースと内がわのダートコース、まん中の芝生に池と蹄鉄の形の花だん、下にスタンド、まわりに木。'
           'いろいろな勝負服の騎手を乗せた8頭のサラブレッドが芝コースを周回して、12秒ごとにゴール前で1頭が外から抜け出して先頭でゴールする（勝つ馬は毎回ちがう）。雲のかげがゆっくり流れる')
    hw, hh = CW * HS2, CH * HS2
    html = f'<div class="csw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('csG', ground_svg())
    html += img('csRp a', ripple_svg()) + img('csRp b', ripple_svg())
    if hs:
        for k in range(len(SILKS)):
            html += f'<i class="csH h{k}"><b></b></i>'
    for c, (w, h, seed, *_r) in enumerate(CLOUDS):
        html += img(f'csCl c{c}', cloud_svg(w, h, seed))
    html += '</div>'
    css = ('.csw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#4E9A4A}'
           '.csw>*{position:absolute;display:block}'
           '.csw .bnr,.csw .csG{left:0;top:0;width:390px;height:160px}'
           '.csw .csRp{left:139px;top:65px;width:30px;height:14px;opacity:0;animation:csRip 3.2s ease-out infinite}'
           '.csw .csRp.b{animation-delay:-1.6s}'
           '.csw .csCl{top:0;left:0;z-index:5;will-change:transform}')
    if hs:
        n, rows = hs['frames'], hs['rows']
        css += (f'.csw .csH{{left:0;top:0;width:{f(hw)}px;height:{f(hh)}px;overflow:hidden;will-change:transform}}'
                f'.csw .csH>b{{display:block;width:{f(n * hw)}px;height:{f(hh)}px;background:url({hs["url"]}) 0 0/{f(n * hw)}px {f(rows * hh)}px no-repeat;'
                f'animation:csGal {f(GAL)}s steps({n}) infinite}}')
        css += kf('csGal', [(100, f'transform:translateX({f(-n * hw)}px)')])
        T = NL * LAP
        for k in range(len(SILKS)):
            css += (f'.csw .csH.h{k}{{animation:csR{k} {f(T)}s linear infinite,csZ{k} {f(T)}s step-end infinite}}'
                    f'.csw .csH.h{k}>b{{background-position:0 {f(-k * hh)}px;animation-delay:{f(-0.053 * k * 7 % GAL, 3)}s}}')
            css += kf(f'csR{k}', keys_for(k)) + kf(f'csZ{k}', z_keys(k))
    for c, (w, h, seed, sec, p0, p1, dl) in enumerate(CLOUDS):
        css += f'.csw .csCl.c{c}{{width:{w}px;height:{h}px;animation:csC{c} {f(sec)}s linear {f(dl)}s infinite}}'
        css += kf(f'csC{c}', [(0, f'transform:translate({p0[0]}px,{p0[1]}px)'), (100, f'transform:translate({p1[0]}px,{p1[1]}px)')])
    css += kf('csRip', [(0, 'opacity:.85;transform:scale(.25)'), (100, 'opacity:0;transform:scale(1.25)')])
    css += reduced('.csw .csG,.csw .csRp,.csw .csH,.csw .csCl') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_turf():
    """背景の もよう：芝の 刈った すじ（ななめ）と 小さな 蹄の あと（うすく）"""
    o = ("<rect width='60' height='60' fill='none'/>"
         "<path d='M-10 30 L30 -10 M0 60 L60 0 M30 70 L70 30' stroke='#DDEBD6' stroke-width='14' opacity='.55'/>")
    for x, y, a in ((14, 44, -20), (44, 18, 25)):
        o += (f"<g transform='translate({x} {y}) rotate({a})' opacity='.28'><path d='M-3.4 2.6 C-4.4 -1 -2.6 -4 0 -4 C2.6 -4 4.4 -1 3.4 2.6 L2.2 2 C2.8 -.6 1.8 -2.6 0 -2.6 "
              "C-1.8 -2.6 -2.8 -.6 -2.2 2 Z' fill='#6E8F62'/></g>")
    return tile(60, 60, o)


def rail_strip():
    """上の 帯の 下の ふちの 白い ラチ（柵：横木と 柱）"""
    o = ("<rect y='1' width='14' height='2.6' fill='#FFFFFF'/><rect y='3.4' width='14' height='.8' fill='#9FB79A'/>"
         "<rect x='5.5' y='1' width='2.4' height='7' fill='#FFFFFF'/><rect x='5.5' y='7' width='2.4' height='1' fill='#9FB79A'/>")
    return tile(14, 8, o)


def orn():
    """すみの 飾り（44×44）：ゴール板（赤と 白の 丸い 札）と 白い 柵"""
    return ("<path d='M22 14 V41' stroke='#8A949E' stroke-width='2.4' stroke-linecap='round'/>"
            "<circle cx='22.8' cy='15.4' r='12.6' fill='#1E3A1E' opacity='.25'/>"
            "<circle cx='22' cy='14' r='12.6' fill='#FFFFFF' stroke='#C9CED4' stroke-width='1'/><circle cx='22' cy='14' r='9.6' fill='#E23B3B'/>"
            "<circle cx='22' cy='14' r='4.6' fill='#FFFFFF'/><circle cx='22' cy='14' r='1.8' fill='#E23B3B'/>"
            "<path d='M2 34 H42 M2 39 H42' stroke='#FFFFFF' stroke-width='2.4' stroke-linecap='round'/>"
            "<path d='M8 32 V42 M36 32 V42' stroke='#FFFFFF' stroke-width='2.4' stroke-linecap='round'/>")


THEME = dict(
    id=ID, cat=7, name='競馬場', desc='上から見たコース', title='競馬場（芝の緑×白いラチ×ゴール板の赤）', banner=ID,
    alt='真上から見た競馬場のイラスト。白い柵の芝コースと内がわのダートコース、まん中の芝生に池と蹄鉄の形の花だん、下にスタンド。いろいろな勝負服の騎手を乗せたサラブレッドの馬群が周回して、12秒ごとにゴール前で1頭が抜け出す（勝つ馬は毎回ちがう）',
    fonts=['Train+One', 'M+PLUS+1:wght@500;700'],
    v=dict(bg='#EEF5EA', ink='#17301C', sub='#4D6A50', card='#FFFFFF', cardB='1.5px solid #CFE3C8', cardO='0 solid transparent', cardS='0 3px 0 #DCEBD5',
           radius='14px', rs='10px', font='"M PLUS 1"', dfont='"Train One"', dw='400', logo='#FFFFFF', logoS='0 2px 0 #14401E',
           iii='#FFFFFF', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#2F8A44,#23733A)', hdInk='#FFFFFF', hdB='0 solid transparent',
           mBg='rgba(0,0,0,.14)', mLine='rgba(255,255,255,.55)', mInk='#FFFFFF', pill='rgba(0,0,0,.16)', pillLine='rgba(255,255,255,.35)', pillInk='#FFFFFF',
           coin='#E23B3B', coinInk='#FFFFFF', badge='#EAF5E6', badgeInk='#1E6A34', badgeB='1.5px solid #CFE3C8', tagBg='#F1F8EE', tagInk='#25552E',
           tagLine='#CFE3C8', warnBg='#FCE6E4', warnInk='#A8231B', zBg='#F8FCF6', zB='1.5px solid #E2EFDC', znBg='#D33A30', znInk='#FFFFFF',
           znB='0 solid transparent', znR='999px', znS='none', acc='#1E6A34', nR='7px', w2B='0 solid transparent', sep='1.5px dashed #CFE3C8',
           btn='#23733A', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='999px', btnS='0 3px 0 #164D26', btn2='#FFFFFF', btn2Ink='#1E6A34',
           btn2B='1.5px solid #A9CF9E', tab='#FFFFFF', tabB='1px solid #CFE3C8', tabInk='#4D6A50', tabOn='#E3F2DE', tabOnInk='#1E6A34', tabR='14px',
           sel='#23733A', selInk='#FFFFFF', h1='#1E6A34'),
    chk=dict(hd=['#2F8A44', '#23733A']),
    css=[('', 'background-image:' + curi(tile_turf()) + ';background-size:60px 60px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-8px;height:8px;background:' + curi(rail_strip()) + ' 0 0/14px 8px repeat-x'),
         ('.card::before', 'content:"";position:absolute;left:14px;right:14px;top:0;height:3px;border-radius:0 0 3px 3px;background:repeating-linear-gradient(90deg,#E23B3B 0 10px,#FFFFFF 10px 20px);opacity:.85')],
    orn=orn(),
    guide=dict(colors=[('#23733A', '芝'), ('#FFFFFF', 'ラチ'), ('#D33A30', 'ゴール板'), ('#C8A272', 'ダート'), ('#EEF5EA', '背景')],
               fonts='見出し：Train One<br>本文：M PLUS 1', shape='角丸14px・丸いボタン・帯の下に 白い ラチ・芝の すじの 背景・カードの 上に 赤白の しま・すみに ゴール板・的中ボタンは 上から 見た コースの PUSH',
               pic='真上から 見た 競馬場：芝コース・ダートコース・池と 蹄鉄の 花だん・スタンド・木・真上から 見た サラブレッドと 騎手 8頭の 馬群（12秒ごとに ゴール・毎回 ちがう 馬が 抜け出す）・雲の かげ'),
)


# ================================================================== 的中ボタン：上から 見た コースの PUSH（cs）
def _st(r):
    x0, x1, yc = 50, 150, 50
    return f'M{x0} {yc - r} H{x1} A{r} {r} 0 0 1 {x1} {yc + r} H{x0} A{r} {r} 0 0 1 {x0} {yc - r} Z'


def push_face(sfx=''):
    """ボタン（200×100）が 上から 見た コース：外の 芝の 帯（白い ラチ）・内の ダート・まん中の 芝生（すじ）・ゴール板"""
    o = f'<path d="{_st(50)}" fill="#4E9A4A"/><path d="{_st(48)}" fill="#86CC72"/><path d="{_st(36)}" fill="#C8A272"/><path d="{_st(28)}" fill="#5DAF54"/>'
    for k in range(9):
        x = 26 + k * 18
        o += f'<path d="M{x} 22 L{x + 10} 78" stroke="#67B95C" stroke-width="8" opacity=".9"/>'
    for r, w in ((48, 2.4), (36, 2), (28, 1.8)):
        o += f'<path d="{_st(r)}" fill="none" stroke="#FFFFFF" stroke-width="{w}"/>'
    o += ('<path d="M138 86 V98" stroke="#FFFFFF" stroke-width="2.4"/>'
          '<circle cx="138" cy="80" r="5.6" fill="#FFFFFF"/><circle cx="138" cy="80" r="4.2" fill="#E23B3B"/><circle cx="138" cy="80" r="1.8" fill="#FFFFFF"/>')
    clip = f'<clipPath id="csC{sfx}"><path d="{_st(50)}"/></clipPath>'
    return (f'<i class="csf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100"><defs>{clip}</defs>'
            f'<g clip-path="url(#csC{sfx})">{o}</g></svg></i>')


def push_decor(sfx=''):
    """コースの まわりを 小さな 馬（真上から）が 3頭 ぐるぐる 回る（.csrun）"""
    return '<i class="csd" aria-hidden="true">' + ''.join(f'<b class="csrun r{k}"><i style="background-image:url(&quot;{durl(horse_sheet(*SILKS[j]))}&quot;)"></i></b>' for k, j in enumerate((4, 2, 3))) + '</i>'


def _push_keys(n=48):
    """PUSH の まわりの 道（ボタンの 外の だ円）を 左回りに 1周"""
    rows, prev = [], None
    for i in range(n + 1):
        a = -2 * math.pi * i / n
        x, y = 100 + 116 * math.cos(a), 50 + 64 * math.sin(a)
        hd = math.degrees(math.atan2(-64 * math.cos(a), 116 * math.sin(a)))
        if prev is not None:
            while hd - prev > 180:
                hd -= 360
            while hd - prev < -180:
                hd += 360
        prev = hd
        rows.append((i / n * 100, f'transform:translate({f(x - 19.5, 1)}px,{f(y - 10.5, 1)}px) rotate({f(hd, 1)}deg)'))
    return rows


def _shoe(c1='#F2C14E', c2='#8A5A14'):
    so, si = [], []
    for k in range(25):
        a = math.radians(-205 + 230 * k / 24)
        so.append((12 + math.cos(a) * 10, 12 - math.sin(a) * 10.6))
        si.append((12 + math.cos(a) * 6, 12 - math.sin(a) * 6.6))
    return doc(24, 24, f"<path d='{P(so + si[::-1])}' fill='{c1}' stroke='{c2}' stroke-width='1.2'/>")


def _clod():
    return doc(20, 16, "<path d='M2 10 C2 4 8 2 12 3 C17 4 19 8 18 11 C17 14 12 15 8 14 C4 14 2 13 2 10 Z' fill='#7A5A32'/><path d='M4 6 L3 1 M8 4 L8 0 M12 4 L14 0 M16 6 L18 2' stroke='#4E9A4A' stroke-width='2' stroke-linecap='round'/>")


def _flag():
    o = "<path d='M3 1 V22' stroke='#8A949E' stroke-width='1.6' stroke-linecap='round'/>"
    for i in range(4):
        for j in range(3):
            o += f"<rect x='{4 + i * 4}' y='{2 + j * 4}' width='4' height='4' fill='{'#1E1E24' if (i + j) % 2 == 0 else '#FFFFFF'}'/>"
    return doc(22, 24, o)


PIECES = dict(sh=piece(_shoe()), cl=piece(_clod()), fl=piece(_flag()), rs='border-radius:50% 0 50% 50%;background:radial-gradient(circle at 40% 40%,#FF8FA8,#E23B5A 70%)')


def push_burst():
    return fly_burst('cs', ['sh', 'cl', 'fl', 'sh', 'rs', 'cl'], 28, 52, sizes=dict(sh=(15, 20), cl=(13, 17), fl=(16, 21), rs=(8, 11)))


PUSH_CSS = r'''
/* ---------- 競馬場の的中ボタン：上から見たコースのPUSH（壁紙パック） ----------
   ボタンが まるごと 上から 見た コース（外の 芝の 帯と 白い ラチ・ダート・まん中の 芝生の すじ・ゴール板）。まわりを 小さな 馬 3頭が ぐるぐる 回る。
   上下の 動きは 的中と 同じ。押すと コースが ちぢんで ふくらみ（強く 光らせない）、蹄鉄・芝の かたまり・チェッカーの 旗・バラが はじけて 落ち、白い 光の 輪が 広がる */
.cs{--pushA:#4E9A4A;--pushB:#164D26;--pushC:#86CC72;--rim:#FFFFFF;--rimD:#164D26}
.push.cs{--pr:50px;border-radius:50px;background:#4E9A4A;box-shadow:0 0 0 3px #FFFFFF,0 7px 0 3px #164D26,0 20px 28px rgba(0,30,0,.4)}
.push.cs span{font:400 42px/1 "Train One",sans-serif;letter-spacing:.06em;color:#FFFFFF;text-shadow:0 2px 0 #164D26,0 0 10px rgba(255,255,255,.4)}
.push.cs::after{border-radius:70px;border-color:rgba(255,255,255,.9)}
.cs .csf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:50px;overflow:hidden;pointer-events:none;font-style:normal}
.cs .csf svg{display:block;width:200px;height:100px}
.cs .csd{position:absolute;left:0;top:0;width:200px;height:100px;pointer-events:none;z-index:3;font-style:normal}
.cs .csrun{position:absolute;left:0;top:0;width:39px;height:21px;animation:csRun 5.4s linear infinite}
.cs .csrun>i{display:block;width:39px;height:21px;background-size:78px 21px;background-repeat:no-repeat;animation:csPg .26s steps(1) infinite}
.cs .csrun.r1{animation-delay:-1.8s}.cs .csrun.r2{animation-delay:-3.6s}
@keyframes csPg{0%{background-position:0 0}50%{background-position:-39px 0}100%{background-position:0 0}}
.pshadow.cs{width:210px}
.tap.cs{font-family:"Train One",sans-serif;font-weight:400;color:#E9F8E2;letter-spacing:.12em;text-shadow:0 2px 0 #164D26,0 0 10px rgba(255,255,255,.5)}
.pressed.cs{border-radius:50px;background:#4E9A4A;box-shadow:0 0 0 3px #FFFFFF,0 7px 0 3px #164D26;animation-name:csPress,fxH}
@keyframes csPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.cs .csrun,.cs .csrun>i{animation:none}.cs .csd,.clips.cs{display:none}}
''' + kf('csRun', _push_keys()) + '\n' + fly_css('cs', 'rgba(255,255,255,.9)', PIECES)

PUSH = dict(code='cs', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
