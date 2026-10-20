"""行事の4テーマ（クリスマス・ハロウィン・バレンタイン・ホワイトデー）の上の絵の部品（SVG の文字列・780×320 の1倍の座標）。
   ぺたっとした色の絵（線なし・明るい面と暗い面の2段・白い光）。人と物の形は すべて一から作ったオリジナル。
   flat/<テーマ>_banner.py が cute_horse.svg_layer で3倍に描いて重ねる"""
import math
import itertools

_GID = itertools.count(1)


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def pts(P):
    return ' '.join(f'{f(x)},{f(y)}' for x, y in P)


def circ(cx, cy, r, fill, extra=''):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" {extra}/>'


def ell(cx, cy, rx, ry, fill, rot=0, extra=''):
    t = f' transform="rotate({f(rot)} {f(cx)} {f(cy)})"' if rot else ''
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{t} {extra}/>'


def rect(x, y, w, h, fill, rx=0, extra=''):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}" {extra}/>'


def path(d, fill, extra=''):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def line(d, col, w, extra=''):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def g(inner, x=0.0, y=0.0, s=1.0, flip=False, rot=0.0):
    sx = -s if flip else s
    r = f' rotate({f(rot)})' if rot else ''
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sx)} {f(s)}){r}">{inner}</g>'


def star_d(cx, cy, r, r2=None, n=5, rot=-90.0):
    r2 = r * 0.45 if r2 is None else r2
    P = []
    for k in range(n * 2):
        a = math.radians(rot + k * 180 / n)
        rr = r if k % 2 == 0 else r2
        P.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in P) + ' Z'


def heart_d(cx, cy, s):
    """ハート（まん中 cx, cy・はば 約 2s）"""
    return (f'M{f(cx)},{f(cy + s * 0.95)} C{f(cx - s * 0.2)},{f(cy + s * 0.75)} {f(cx - s * 1.05)},{f(cy + s * 0.25)} {f(cx - s * 1.0)},{f(cy - s * 0.25)} '
            f'C{f(cx - s * 0.95)},{f(cy - s * 0.85)} {f(cx - s * 0.2)},{f(cy - s * 0.95)} {f(cx)},{f(cy - s * 0.42)} '
            f'C{f(cx + s * 0.2)},{f(cy - s * 0.95)} {f(cx + s * 0.95)},{f(cy - s * 0.85)} {f(cx + s * 1.0)},{f(cy - s * 0.25)} '
            f'C{f(cx + s * 1.05)},{f(cy + s * 0.25)} {f(cx + s * 0.2)},{f(cy + s * 0.75)} {f(cx)},{f(cy + s * 0.95)} Z')


def sparkle_d(cx, cy, r):
    """4つの とがりの キラッ"""
    q = r * 0.22
    return (f'M{f(cx)},{f(cy - r)} Q{f(cx + q)},{f(cy - q)} {f(cx + r)},{f(cy)} Q{f(cx + q)},{f(cy + q)} {f(cx)},{f(cy + r)} '
            f'Q{f(cx - q)},{f(cy + q)} {f(cx - r)},{f(cy)} Q{f(cx - q)},{f(cy - q)} {f(cx)},{f(cy - r)} Z')


def shadow(cx, cy, rx, ry, col, op):
    return ell(cx, cy, rx, ry, col, extra=f'opacity="{op}"')


# ------------------------------------------------------------------ 人（ちびキャラ：足もとが 0,0・前向き）
def face_parts(skin, eye='#3A2A22', blush='#F59AA0', happy=True, y=0.0, mouth=True, look=0.0):
    """顔の中（頭のまん中が 0,y）の 部品：(目, ほお, 口)。face() は この3つを つないだもの"""
    eyes = ''
    if happy:
        for sx in (-1, 1):
            x = sx * 9.5 + look
            eyes += line(f'M{f(x - 4.6)},{f(y + 1.4)} Q{f(x)},{f(y - 4.4)} {f(x + 4.6)},{f(y + 1.4)}', eye, 2.6)
    else:
        for sx in (-1, 1):
            x = sx * 9.5 + look
            eyes += ell(x, y, 3.4, 4.4, eye) + circ(x + 1.2, y - 1.6, 1.3, '#FFFFFF')
    cheeks = ell(-16 + look, y + 7.5, 4.8, 3.2, blush, extra='opacity=".75"') + ell(16 + look, y + 7.5, 4.8, 3.2, blush, extra='opacity=".75"')
    m = line(f'M{f(-3.6 + look)},{f(y + 9)} Q{f(look)},{f(y + 12.6)} {f(3.6 + look)},{f(y + 9)}', '#B24A4A', 2.0) if mouth else ''
    return eyes, cheeks, m


def face(skin, eye='#3A2A22', blush='#F59AA0', happy=True, y=0.0, mouth=True, look=0.0):
    """顔の中（頭のまん中が 0,y）：目・ほお・口"""
    return ''.join(face_parts(skin, eye, blush, happy, y, mouth, look))


SANTA_ORDER = ('pantsL', 'pantsR', 'bootL', 'bootR', 'shine', 'sleeveW', 'sleeveG', 'coat', 'handW',
               'skin', 'eyes', 'cheeks', 'nose', 'beard', 'stache', 'mouth', 'brows', 'hat', 'gift', 'handG')


def santa_bits(gift=True):
    """サンタさんの 部品（名前 → SVG）。santa() は SANTA_ORDER の順に つないだもの（いまの絵と1バイトも ちがわない）。
       クリスマスの 動く壁紙（xmas_wall.py）は 部品ごとに <g> で包んで 動かす"""
    red, redD, fur, furD, skin, skinD = '#D7323A', '#A9232B', '#FFFFFF', '#E4E9F0', '#FFDCC4', '#F2BFA4'
    b = dict.fromkeys(SANTA_ORDER, '')
    # 足（ブーツ）・ズボン
    b['pantsL'], b['pantsR'] = rect(-24, -38, 20, 26, redD, 4), rect(4, -38, 20, 26, redD, 4)
    b['bootL'], b['bootR'] = rect(-27, -17, 25, 17, '#2A2224', 7), rect(2, -17, 25, 17, '#2A2224', 7)
    b['shine'] = rect(-24, -15, 8, 4, '#FFFFFF', 2, 'opacity=".25"')
    # うで（プレゼントの手は 体の前）・上着
    b['sleeveW'] = line('M30,-104 Q48,-120 54,-146', redD, 19)               # ふる手（右）：そで
    if gift:                                                                # プレゼントの手（左）：そでは 上着の 横（胸の高さ）から 外へ（つけねは 上着の下）
        b['sleeveG'] = line('M-24,-96 Q-46,-97 -60,-88', redD, 19)
    b['coat'] = (path('M-36,-34 Q-46,-78 -30,-112 Q0,-122 30,-112 Q46,-78 36,-34 Z', red)
                 + path('M2,-118 Q30,-114 36,-34 L2,-34 Z', redD, 'opacity=".35"')
                 + rect(-40, -44, 80, 15, fur, 7.5) + rect(-40, -36, 80, 7, furD, 3.5, 'opacity=".7"')
                 + rect(-6, -112, 12, 72, fur, 6)
                 + rect(-37, -74, 74, 11, '#2B2224', 3) + rect(-10, -77, 20, 17, 'none', 3, 'stroke="#F2C14E" stroke-width="3.4"'))
    b['handW'] = (circ(56, -150, 11, fur) + circ(56, -150, 11, furD, 'opacity=".25"') + ell(57, -161, 9.5, 8, '#FFFFFF')     # そでの白・手ぶくろ
                  + ell(63, -165, 3.5, 6, '#FFFFFF', rot=30))
    # あたま
    b['skin'] = circ(0, -140, 28, skin) + path('M14,-160 Q30,-148 26,-126 Q20,-140 14,-160 Z', skinD, 'opacity=".6"')
    b['eyes'], b['cheeks'], _ = face_parts(skin, y=-147, mouth=False)
    b['nose'] = circ(0, -138, 5.4, '#F49C88') + circ(-1.6, -140, 1.6, '#FFFFFF', 'opacity=".8"')
    # ひげ（ふわふわ）・口ひげ・まゆ
    beard = 'M-27,-140 Q-34,-112 -20,-100 Q-12,-88 0,-90 Q12,-88 20,-100 Q34,-112 27,-140 Q16,-126 0,-128 Q-16,-126 -27,-140 Z'
    b['beard'] = path(beard, fur) + path('M0,-90 Q12,-88 20,-100 Q34,-112 27,-140 Q22,-118 0,-104 Z', furD, 'opacity=".6"')
    for x, y, r in ((-24, -114, 7), (-17, -100, 7.5), (-6, -93, 7.5), (6, -93, 7.5), (17, -100, 7.5), (24, -114, 7)):
        b['beard'] += circ(x, y, r, fur)
    b['stache'] = ell(-8.5, -131, 10, 5.6, fur, rot=-14) + ell(8.5, -131, 10, 5.6, fur, rot=14)
    b['mouth'] = path('M-2,-130 Q0,-126 2,-130', 'none', 'stroke="#C9D2DC" stroke-width="1.4"')
    b['brows'] = line('M-14,-155 Q-9.5,-158.5 -5,-155', '#FFFFFF', 3.2) + line('M5,-155 Q9.5,-158.5 14,-155', '#FFFFFF', 3.2)
    # ぼうし（先が 右へ たれる・白い玉）
    b['hat'] = (path('M-29,-160 Q-22,-206 12,-212 Q40,-214 52,-190 L44,-186 Q34,-200 16,-196 Q20,-178 29,-160 Z', red)
                + path('M16,-196 Q34,-200 44,-186 L52,-190 Q42,-208 20,-210 Z', redD, 'opacity=".5"')
                + rect(-33, -170, 66, 16, fur, 8) + rect(-33, -160, 66, 6, furD, 3, 'opacity=".6"')
                + circ(51, -186, 10, fur) + circ(48, -189, 3.5, '#FFFFFF'))
    if gift:                                                                # プレゼント（左手に のせて 前に さしだす）
        gx, gy = -82, -124                                                  # 箱（はば38・高さ32）：手の上に のせる
        b['gift'] = (rect(gx - 19, gy, 38, 32, '#2E8C5A', 4) + rect(gx + 4, gy, 15, 32, '#246F47', 3, 'opacity=".6"')
                     + rect(gx - 4, gy, 8, 32, '#F2C14E') + rect(gx - 21, gy - 7, 42, 11, '#3BA66C', 3) + rect(gx - 4, gy - 7, 8, 11, '#F2C14E')
                     + path(f'M{gx},{gy - 7} Q{gx - 16},{gy - 22} {gx - 14},{gy - 8} Z', '#F2C14E')
                     + path(f'M{gx},{gy - 7} Q{gx + 16},{gy - 22} {gx + 14},{gy - 8} Z', '#F2C14E'))
        b['handG'] = (circ(-61, -88, 10.5, fur) + circ(-61, -88, 10.5, furD, 'opacity=".25"')   # そでの 白い ふち
                      + ell(-73, -91, 10.5, 7.5, '#FFFFFF') + ell(-73, -88.5, 9, 4, furD, extra='opacity=".5"'))   # 手ぶくろ（箱の 底を 下から ささえる）
    return b


def santa(gift=True):
    """サンタさん（前向き・右手を ふる・左手に プレゼントを のせて さしだす）。足もと 0,0・高さ 約200"""
    b = santa_bits(gift)
    return ''.join(b[k] for k in SANTA_ORDER)


def drop_d(s=1.0):
    """汗の しずく（先が上・まん中が 0,0・高さ 約 12s）"""
    return (f'M0,{f(-7 * s)} C{f(2.6 * s)},{f(-3.2 * s)} {f(4.6 * s)},{f(-0.4 * s)} {f(4.6 * s)},{f(2.2 * s)} '
            f'A{f(4.6 * s)},{f(4.6 * s)} 0 0 1 {f(-4.6 * s)},{f(2.2 * s)} C{f(-4.6 * s)},{f(-0.4 * s)} {f(-2.6 * s)},{f(-3.2 * s)} 0,{f(-7 * s)} Z')


def drop(x, y, s=1.0):
    return g(path(drop_d(), '#86CDF7') + ell(-1.6, 0.6, 1.3, 2.2, '#FFFFFF', rot=20, extra='opacity=".85"'), x, y, s)


def santa_fx():
    """クリスマスの 動く壁紙（xmas_wall.py）で サンタさんに たす 絵（santa() と同じ 足もと 0,0 の座標）：
       あせった目（まるく あける）・あけた口・こめかみの汗・とびちる汗・びくっの線・走る線・💨 の けむり（まん中 0,0）"""
    eye = '#3A2A22'
    o = {}
    o['eyesOpen'] = ''.join(ell(sx * 9.5, -147, 3.8, 5.0, eye) + circ(sx * 9.5 + 1.3, -148.9, 1.45, '#FFFFFF') for sx in (-1, 1))
    o['mouthOpen'] = ell(0, -122.5, 4.8, 5.8, '#8A2E35') + ell(0, -119.8, 3.0, 2.4, '#E58A8A')
    o['sweat'] = drop(30, -150, 0.9)
    o['burst'] = ''.join(line(f'M{f(math.cos(math.radians(a)) * 50)},{f(-150 + math.sin(math.radians(a)) * 50)} '
                              f'L{f(math.cos(math.radians(a)) * 63)},{f(-150 + math.sin(math.radians(a)) * 63)}', '#FFFFFF', 3.4)
                         for a in (196, 214, 232))
    o['speed'] = ''.join(line(f'M{f(x0)},{f(y)} L{f(x0 + w)},{f(y)}', '#FFFFFF', 3, 'opacity=".85"')
                         for x0, y, w in ((-104, -146, 28), (-112, -100, 36), (-100, -54, 24)))
    puff = [(-12, 0, 9), (0, -4.5, 11), (12, 0, 8), (2, 4, 8.5)]
    o['puff'] = (''.join(circ(x, y, r + 1.6, '#94ABC8') for x, y, r in puff) + ''.join(circ(x, y, r, '#FFFFFF') for x, y, r in puff)
                 + ''.join(ell(x, y + r * 0.45, r * 0.62, r * 0.3, '#E4ECF6') for x, y, r in puff)
                 + line('M20,-6 L31,-6', '#94ABC8', 2.4) + line('M18,5 L27,5', '#94ABC8', 2.4))
    return o


def xmas_tree(h=262.0):
    """クリスマスツリー（根もとの まん中が 0,0）：4だん・雪・金の星・玉・金のかざり・あかり"""
    G, GD, GL, SNOW = '#2F8A55', '#1E6A40', '#4CA86C', '#FFFFFF'
    o = rect(-11, -30, 22, 30, '#6B4428', 3) + rect(2, -30, 9, 30, '#53321C', 2)
    tiers = [(-262, -198, 44), (-236, -150, 64), (-200, -96, 86), (-158, -34, 110)]
    for k, (top, bot, hw) in enumerate(tiers):
        n = 4 + k
        d = f'M0,{f(top)} C{f(hw * 0.3)},{f(top + (bot - top) * 0.35)} {f(hw * 0.75)},{f(bot - 14)} {f(hw)},{f(bot - 2)}'
        for i in range(n):                                     # 下のふちの まるい ふくらみ（右から左）
            x0 = hw - 2 * hw * i / n
            x1 = hw - 2 * hw * (i + 1) / n
            d += f' Q{f((x0 + x1) / 2)},{f(bot + 9)} {f(x1)},{f(bot - 2)}'
        d += f' C{f(-hw * 0.75)},{f(bot - 14)} {f(-hw * 0.3)},{f(top + (bot - top) * 0.35)} 0,{f(top)} Z'
        o += path(d, G)
        o += path(f'M0,{f(top)} C{f(hw * 0.3)},{f(top + (bot - top) * 0.35)} {f(hw * 0.75)},{f(bot - 14)} {f(hw)},{f(bot - 2)} '
                  f'Q{f(hw * 0.6)},{f(bot + 6)} {f(hw * 0.25)},{f(bot - 1)} C{f(hw * 0.2)},{f(top + (bot - top) * 0.5)} {f(hw * 0.08)},{f(top + 20)} 0,{f(top)} Z', GD, 'opacity=".55"')
        o += path(f'M{f(-hw * 0.18)},{f(top + 26)} C{f(-hw * 0.32)},{f(top + (bot - top) * 0.5)} {f(-hw * 0.55)},{f(bot - 18)} {f(-hw * 0.7)},{f(bot - 10)}', 'none',
                  f'stroke="{GL}" stroke-width="5" stroke-linecap="round" opacity=".7"')
        # ふちの雪（左がわ）
        o += path(f'M{f(-hw)},{f(bot - 2)} Q{f(-hw * 0.82)},{f(bot + 7)} {f(-hw * 0.6)},{f(bot - 1)} Q{f(-hw * 0.45)},{f(bot + 6)} {f(-hw * 0.3)},{f(bot - 2)} '
                  f'Q{f(-hw * 0.5)},{f(bot - 9)} {f(-hw * 0.8)},{f(bot - 8)} Z', SNOW, 'opacity=".95"')
    # 金の かざり（ゆるい なみ）
    for y0, x0, x1, sag in ((-180, -50, 54, 12), (-128, -72, 76, 14), (-72, -94, 98, 16)):
        P = []
        for i in range(15):
            t = i / 14
            x = x0 + (x1 - x0) * t
            y = y0 + (x1 - x0) * 0.12 * (t - 0.5) + sag * math.sin(math.pi * t)
            P.append((x, y))
        for x, y in P:
            o += circ(x, y, 2.6, '#F6CE5A')
    # 玉（赤・金・青・銀）と あかり
    for x, y, r, c in ((-18, -214, 6.5, '#E23B3B'), (16, -196, 6, '#4A8FE0'), (-30, -170, 7, '#F2C14E'), (28, -160, 7, '#E23B3B'),
                       (-6, -150, 6, '#C9D6E6'), (-52, -114, 7.5, '#4A8FE0'), (46, -106, 7.5, '#F2C14E'), (8, -118, 6.5, '#E23B3B'),
                       (-70, -60, 8, '#E23B3B'), (-22, -78, 7, '#F2C14E'), (30, -60, 8, '#4A8FE0'), (72, -56, 7.5, '#E23B3B'), (-40, -50, 6, '#C9D6E6')):
        o += circ(x, y, r, c) + circ(x - r * 0.35, y - r * 0.35, r * 0.32, '#FFFFFF', 'opacity=".75"') + rect(x - 2.4, y - r - 3, 4.8, 3.6, '#C9A13E', 1)
    for x, y in ((-4, -232, ), (24, -214), (-40, -186), (40, -178), (-14, -168), (-62, -136), (18, -138), (62, -128), (-34, -96), (52, -88), (-86, -70), (0, -64), (88, -78), (-60, -40), (52, -40)):
        o += circ(x, y, 6, '#FFE9A0', 'opacity=".35"') + circ(x, y, 2.6, '#FFF6CC')
    # 星
    o += path(star_d(0, -264, 19), '#F6C445')
    o += path(star_d(-1.5, -266, 9, 4), '#FFF3C2')
    return o


def gift(w, h, box, boxD, rib, bow=True):
    """プレゼント（底の まん中が 0,0）"""
    o = rect(-w / 2, -h, w, h, box, 3) + rect(w * 0.12, -h, w * 0.38, h, boxD, 2, 'opacity=".55"')
    o += rect(-w / 2 - 2, -h - 7, w + 4, 11, box, 3) + rect(-w / 2 - 2, -h + 1, w + 4, 3, boxD, 1, 'opacity=".5"')
    o += rect(-4, -h - 7, 8, h + 7, rib)
    if bow:
        o += path(f'M0,{f(-h - 7)} Q-17,{f(-h - 24)} -14,{f(-h - 8)} Z', rib) + path(f'M0,{f(-h - 7)} Q17,{f(-h - 24)} 14,{f(-h - 8)} Z', rib)
        o += circ(0, -h - 7, 3.6, rib)
    return o


def snowflake(cx, cy, r, col='#FFFFFF', op=1.0):
    o = ''
    for k in range(3):
        a = math.radians(k * 60)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        o += line(f'M{f(cx - dx)},{f(cy - dy)} L{f(cx + dx)},{f(cy + dy)}', col, max(0.8, r * 0.22), f'opacity="{op}"')
    return o


# ------------------------------------------------------------------ ハロウィン
VAMP_ORDER = ('cape', 'lining', 'shadeL', 'shadeR', 'legL', 'legR', 'bootL', 'bootR', 'body', 'armL', 'armR', 'handL', 'handR',
              'collar', 'ears', 'face', 'hair', 'eyeL', 'browL', 'eyeR', 'browR', 'cheeks', 'mouth')
VAMP_COL = dict(skin='#F1E6F2', skinD='#D9C6DE', hair='#231A2E', cape='#2A1E3A', capeD='#1A1226', lining='#C4243A', mouth='#7A1A2E')


def vampire_bits():
    """ドラキュラの 部品（名前 → SVG）。vampire() は VAMP_ORDER の順に つないだもの（いまの絵と1バイトも ちがわない）。
       capeL・capeR・liningL・liningR は マントの 左右の 半分（まん中で 6 ずつ かさねる：ハロウィンの 動く壁紙で 羽のように はばたかせる。halloween_wall.py）"""
    C = VAMP_COL
    skin, skinD, hair, cape, capeD, lining = C['skin'], C['skinD'], C['hair'], C['cape'], C['capeD'], C['lining']
    b = {}
    # マント（うしろ・ひろげた形）：外がわ・内がわの赤
    b['cape'] = path('M-12,-150 Q-70,-140 -92,-96 Q-98,-60 -84,-18 Q-60,-30 -46,-8 Q-30,-28 -14,-6 L14,-6 Q30,-28 46,-8 Q60,-30 84,-18 Q98,-60 92,-96 Q70,-140 12,-150 Z', cape)
    b['lining'] = path('M-12,-146 Q-62,-134 -80,-96 Q-86,-62 -76,-26 Q-58,-34 -46,-16 Q-30,-34 -14,-14 L14,-14 Q30,-34 46,-16 Q58,-34 76,-26 Q86,-62 80,-96 Q62,-134 12,-146 Z', lining)
    b['capeL'] = path('M6,-150 L-12,-150 Q-70,-140 -92,-96 Q-98,-60 -84,-18 Q-60,-30 -46,-8 Q-30,-28 -14,-6 L6,-6 Z', cape)
    b['capeR'] = path('M-6,-150 L12,-150 Q70,-140 92,-96 Q98,-60 84,-18 Q60,-30 46,-8 Q30,-28 14,-6 L-6,-6 Z', cape)
    b['liningL'] = path('M6,-146 L-12,-146 Q-62,-134 -80,-96 Q-86,-62 -76,-26 Q-58,-34 -46,-16 Q-30,-34 -14,-14 L6,-14 Z', lining)
    b['liningR'] = path('M-6,-146 L12,-146 Q62,-134 80,-96 Q86,-62 76,-26 Q58,-34 46,-16 Q30,-34 14,-14 L-6,-14 Z', lining)
    b['shadeL'] = path('M-12,-146 Q-62,-134 -80,-96 Q-70,-120 -12,-128 Z', '#9E1A2E', 'opacity=".6"')
    b['shadeR'] = path('M12,-146 Q62,-134 80,-96 Q70,-120 12,-128 Z', '#9E1A2E', 'opacity=".6"')
    # 足・ズボン
    b['legL'], b['legR'] = rect(-20, -40, 17, 30, '#2B2234', 4), rect(3, -40, 17, 30, '#2B2234', 4)
    b['bootL'], b['bootR'] = rect(-23, -14, 22, 14, '#141018', 7), rect(1, -14, 22, 14, '#141018', 7)
    # 体（白いシャツ・黒い上着・赤い ちょうネクタイ）
    o = path('M-28,-40 Q-32,-84 -22,-112 L22,-112 Q32,-84 28,-40 Z', '#2E2440')
    o += path('M-12,-112 L12,-112 L8,-58 L0,-48 L-8,-58 Z', '#FFFFFF')
    o += path('M-12,-112 L-2,-92 L-10,-60 Q-22,-80 -22,-112 Z', '#3A2E52') + path('M12,-112 L2,-92 L10,-60 Q22,-80 22,-112 Z', '#3A2E52')
    o += path('M0,-104 L-11,-110 L-11,-98 Z', lining) + path('M0,-104 L11,-110 L11,-98 Z', lining) + circ(0, -104, 3.2, '#E8364E')
    o += circ(0, -74, 4.5, '#F2C14E') + circ(-1.2, -75.5, 1.4, '#FFF4C2')
    b['body'] = o
    # うで（マントの はしを もつ）
    b['armL'], b['armR'] = line('M-24,-104 Q-50,-112 -74,-100', '#2E2440', 15), line('M24,-104 Q50,-112 74,-100', '#2E2440', 15)
    b['handL'], b['handR'] = circ(-78, -98, 8, skin), circ(78, -98, 8, skin)
    # えり（高く 立った マントの えり）
    b['collar'] = (path('M-14,-118 Q-40,-142 -34,-170 Q-20,-150 -4,-130 Z', capeD) + path('M14,-118 Q40,-142 34,-170 Q20,-150 4,-130 Z', capeD)
                   + path('M-12,-120 Q-34,-140 -31,-162 Q-20,-146 -5,-130 Z', lining) + path('M12,-120 Q34,-140 31,-162 Q20,-146 5,-130 Z', lining))
    # あたま（とがった耳・オールバックの髪・まん中が とがった 前髪）
    b['ears'] = path('M-26,-142 L-40,-160 L-25,-152 Z', skin) + path('M26,-142 L40,-160 L25,-152 Z', skin)
    b['face'] = circ(0, -146, 27, skin) + path('M14,-166 Q30,-152 25,-130 Q19,-144 14,-166 Z', skinD, 'opacity=".55"')
    b['hair'] = (path('M-28,-148 Q-30,-178 0,-180 Q30,-178 28,-148 Q22,-162 8,-164 L0,-152 L-8,-164 Q-22,-162 -28,-148 Z', hair)
                 + path('M-18,-170 Q-4,-176 10,-172', 'none', 'stroke="#4A3A60" stroke-width="2.4" stroke-linecap="round"'))
    for sx, k in ((-1, 'L'), (1, 'R')):                                    # 目（赤い ひとみ）・まゆ
        x = sx * 10
        b['eye' + k] = ell(x, -144, 4, 4.8, '#FFFFFF') + ell(x, -143.5, 2.8, 3.6, '#B3122E') + circ(x + 1, -145.5, 1.1, '#FFFFFF')
        b['brow' + k] = line(f'M{x - 5 * sx},{-153} L{x + 5 * sx},{-151}', hair, 2.4)
    b['cheeks'] = ell(-17, -136, 4.6, 3, '#E99AB8', extra='opacity=".7"') + ell(17, -136, 4.6, 3, '#E99AB8', extra='opacity=".7"')
    b['mouth'] = (path('M-8,-134 Q0,-128 8,-134 Q0,-131 -8,-134 Z', C['mouth'])          # にっこり＋きば
                  + path('M-5.5,-133.4 L-4,-128.6 L-2.5,-132.9 Z', '#FFFFFF') + path('M5.5,-133.4 L4,-128.6 L2.5,-132.9 Z', '#FFFFFF'))
    return b


def vampire():
    """ドラキュラ（前向き・マントを 両手で ひろげる・きばの見える にっこり）。足もと 0,0・高さ 約190"""
    b = vampire_bits()
    return ''.join(b[k] for k in VAMP_ORDER)


def vampire_fx():
    """ハロウィンの 動く壁紙（halloween_wall.py）で ドラキュラに たす 顔（vampire() と同じ 足もと 0,0 の座標）：
       ぎゅっと つぶった目（＞＜）・にこっと 細めた目（＾＾）・あけた口（きばつき）・こめかみの汗・まっかな ほお"""
    C = VAMP_COL
    o = {}
    o['eyesShut'] = line('M-14.5,-148 L-6.5,-144 L-14.5,-140', C['hair'], 2.6) + line('M14.5,-148 L6.5,-144 L14.5,-140', C['hair'], 2.6)
    o['eyesHappy'] = line('M-14.5,-142.5 Q-10,-150 -5.5,-142.5', C['hair'], 2.6) + line('M5.5,-142.5 Q10,-150 14.5,-142.5', C['hair'], 2.6)
    o['mouthOpen'] = (path('M-6.5,-134.5 Q0,-136 6.5,-134.5 Q6,-124.5 0,-124 Q-6,-124.5 -6.5,-134.5 Z', C['mouth'])
                      + ell(0, -126.6, 3.2, 1.7, '#E58AA0')
                      + path('M-5,-134.6 L-3.8,-130.4 L-2.6,-134.9 Z', '#FFFFFF') + path('M5,-134.6 L3.8,-130.4 L2.6,-134.9 Z', '#FFFFFF'))
    o['sweat'] = drop(27, -160, 0.85)
    o['blush'] = ell(-17, -136, 5.6, 3.6, '#F07AA6', extra='opacity=".85"') + ell(17, -136, 5.6, 3.6, '#F07AA6', extra='opacity=".85"')
    return o


SKULL_ORDER = ('bone', 'shade', 'eyes', 'shine', 'nose', 'teeth')
SKULL_COL = dict(bone='#F3EEE2', boneD='#D8D0BE', hole='#2A1A3A')


def skull_bits():
    """ドクロの 部品（名前 → SVG・下の まん中が 0,0）。skull() は SKULL_ORDER の順に つないで 大きさ s に したもの（いまの絵と1バイトも ちがわない）"""
    bone, boneD, hole = SKULL_COL['bone'], SKULL_COL['boneD'], SKULL_COL['hole']
    b = {}
    b['bone'] = path('M-22,-26 Q-24,-50 0,-52 Q24,-50 22,-26 Q22,-16 14,-12 L14,0 L-14,0 L-14,-12 Q-22,-16 -22,-26 Z', bone)
    b['shade'] = path('M10,-50 Q24,-46 22,-26 Q22,-16 14,-12 L14,0 L8,0 L8,-14 Q16,-20 16,-32 Q16,-44 10,-50 Z', boneD, 'opacity=".7"')
    b['eyes'] = ell(-9, -30, 7, 8, hole) + ell(9, -30, 7, 8, hole)
    b['shine'] = circ(-7, -32, 2, '#FFFFFF', 'opacity=".8"') + circ(11, -32, 2, '#FFFFFF', 'opacity=".8"')
    b['nose'] = path('M0,-22 L-3.5,-15 L3.5,-15 Z', hole)
    b['teeth'] = ''.join(rect(x - 1.2, -10, 2.4, 7, hole, 1.2, 'opacity=".75"') for x in (-8, -3, 2, 7))
    return b


def skull(s=1.0):
    """かわいい ドクロ（下の まん中が 0,0・はば 約 46s）"""
    b = skull_bits()
    return g(''.join(b[k] for k in SKULL_ORDER), s=s)


JAW_Y = -6.5                          # ドクロの 口が ひらく 線（歯の まん中：まさちゃんの スクショの 黄色い線。上の歯は あたま・下の歯は あご）


def skull_laugh(cid):
    """笑う ドクロ（ハロウィンの 動く壁紙：halloween_wall.py）の 部品：jaw（あご：下の歯と、あごが さがると 見える 口の中）・
       head（あたま：上の歯まで。目は そのまま＝まさちゃん「笑う時目は笑わないで！」）。どちらも いまの形を JAW_Y（歯の まん中）で 上下に 切ったもの
       （cid：切りぬきの id の 頭）。あごは 上へ 1 のばして あたまの 下に かくす（切れ目に すきまが 見えないように）。
       口の中は あごの 上の はしの 上に つけて、あごと いっしょに 動く（とじている時は あたまに かくれる）"""
    b = skull_bits()
    still = ''.join(b[k] for k in SKULL_ORDER)
    up, dn = f'{cid}U', f'{cid}D'
    top = JAW_Y - 1                                             # あごの 上の はし（あたまの 下に 1 かくれる）
    defs = (f'<defs><clipPath id="{up}"><rect x="-30" y="-60" width="60" height="{f(60 + JAW_Y)}"/></clipPath>'
            f'<clipPath id="{dn}"><rect x="-30" y="{f(top)}" width="60" height="{f(4 - top)}"/></clipPath></defs>')
    inside = rect(-13.5, top - 6, 27, 6.2, SKULL_COL['hole'], 1.5)  # 口の中（あごが 6 まで さがっても すきまを うめる）
    return dict(jaw=defs + inside + f'<g clip-path="url(#{dn})">{still}</g>', head=f'<g clip-path="url(#{up})">{still}</g>')


PUMPKIN_ORDER = ('glow', 'body', 'stem', 'eyes', 'nose', 'mouth')
PUMPKIN_FACE = '#FFE36A'


def pumpkin_bits(w=60.0, h=46.0, face=True, glow=True, look=0.0):
    """ジャック・オー・ランタンの 部品（名前 → SVG・下の まん中が 0,0）。pumpkin() は PUMPKIN_ORDER の順に つないだもの（いまの絵と1バイトも ちがわない）"""
    O, OD, OL = '#F28A1E', '#C9631A', '#FFB04A'
    b = dict.fromkeys(PUMPKIN_ORDER, '')
    if glow:                                                   # まわりの あたたかい光（まん中ほど こい）
        gid = f'pkg{next(_GID)}'
        b['glow'] = (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="#FFB347" stop-opacity=".55"/><stop offset=".5" stop-color="#FF9A2E" stop-opacity=".18"/>'
                     f'<stop offset="1" stop-color="#FF9A2E" stop-opacity="0"/></radialGradient></defs>') + ell(0, -h * 0.45, w * 1.05, h * 0.95, f'url(#{gid})')
    for k, (dx, ww) in enumerate(((-w * 0.28, w * 0.36), (w * 0.28, w * 0.36), (0, w * 0.34))):
        b['body'] += ell(dx, -h / 2, ww, h / 2, O if k < 2 else OL)
    b['body'] += ell(-w * 0.28, -h / 2, w * 0.36, h / 2, OD, extra='opacity=".35"') + ell(w * 0.1, -h * 0.5, w * 0.16, h * 0.46, OD, extra='opacity=".22"')
    b['stem'] = path(f'M{f(-w * 0.04)},{f(-h + 2)} Q{f(-w * 0.06)},{f(-h - 10)} {f(w * 0.06)},{f(-h - 14)} L{f(w * 0.1)},{f(-h - 10)} Q{f(w * 0.04)},{f(-h - 6)} {f(w * 0.06)},{f(-h + 2)} Z', '#4E7A2A')
    if face:
        c = PUMPKIN_FACE
        cy = -h * 0.55
        b['eyes'] = (path(f'M{f(look - w * 0.26)},{f(cy)} L{f(look - w * 0.16)},{f(cy - h * 0.2)} L{f(look - w * 0.06)},{f(cy)} Z', c)
                     + path(f'M{f(look + w * 0.06)},{f(cy)} L{f(look + w * 0.16)},{f(cy - h * 0.2)} L{f(look + w * 0.26)},{f(cy)} Z', c))
        b['nose'] = path(f'M{f(look - w * 0.03)},{f(cy + h * 0.06)} L{f(look)},{f(cy + h * 0.0)} L{f(look + w * 0.03)},{f(cy + h * 0.06)} Z', c)
        my = -h * 0.24
        d = f'M{f(look - w * 0.3)},{f(my - h * 0.08)}'
        for i in range(7):
            x = look - w * 0.3 + w * 0.6 * (i + 1) / 7
            d += f' L{f(x - w * 0.6 / 14)},{f(my + (h * 0.07 if i % 2 == 0 else -h * 0.02))} L{f(x)},{f(my - h * 0.08 + (0 if i % 2 else h * 0.03))}'
        d += f' Q{f(look)},{f(my + h * 0.2)} {f(look - w * 0.3)},{f(my - h * 0.08)} Z'
        b['mouth'] = path(d, c)
    return b


def pumpkin(w=60.0, h=46.0, face=True, glow=True, look=0.0):
    """ジャック・オー・ランタン（下の まん中が 0,0）：オレンジの みぞ・緑のへた・光る 三角の目と ぎざぎざの口"""
    b = pumpkin_bits(w, h, face, glow, look)
    return ''.join(b[k] for k in PUMPKIN_ORDER)


def pumpkin_laugh(w=60.0, h=46.0, look=0.0):
    """笑う ジャック・オー・ランタンの 口（ハロウィンの 動く壁紙：halloween_wall.py）：mouth（大きく あけた 口：上の歯 2本）。
       目と 鼻は いまの まま（まさちゃん「笑う時目は笑わないで！」）。mouth_top：口の 上の線の 高さ（口を ぱくぱく させる 中心）"""
    c, O = PUMPKIN_FACE, '#F28A1E'
    top = -h * 0.33
    o = {}
    o['mouth'] = (path(f'M{f(look - w * 0.3)},{f(top)} Q{f(look)},{f(top + h * 0.05)} {f(look + w * 0.3)},{f(top)} '
                       f'Q{f(look + w * 0.27)},{f(top + h * 0.3)} {f(look)},{f(top + h * 0.31)} Q{f(look - w * 0.27)},{f(top + h * 0.3)} {f(look - w * 0.3)},{f(top)} Z', c)
                  + rect(look - w * 0.14, top - 0.5, w * 0.08, h * 0.09, O, 1) + rect(look + w * 0.06, top - 0.5, w * 0.08, h * 0.09, O, 1))
    o['mouth_top'] = top
    return o


def bat(s=1.0, col='#1A1028'):
    """こうもり（まん中が 0,0・はば 約 60s）"""
    d = ('M0,-4 Q-6,-10 -10,-6 Q-18,-16 -30,-14 Q-26,-8 -28,-2 Q-22,-4 -18,2 Q-14,-2 -10,4 Q-6,0 0,6 '
         'Q6,0 10,4 Q14,-2 18,2 Q22,-4 28,-2 Q26,-8 30,-14 Q18,-16 10,-6 Q6,-10 0,-4 Z')
    o = path(d, col) + path('M-5,-6 L-3,-12 L-1,-6 Z M5,-6 L3,-12 L1,-6 Z', col)
    o += circ(-2.4, -3, 1.2, '#FFD34A') + circ(2.4, -3, 1.2, '#FFD34A')
    return g(o, s=s)


def castle(col='#2A1840', win='#FFC94A'):
    """遠くの お城（下の まん中が 0,0・はば 約 120）"""
    o = rect(-46, -54, 92, 54, col) + rect(-60, -86, 24, 86, col) + rect(36, -96, 26, 96, col) + rect(-14, -110, 28, 110, col)
    o += path('M-64,-86 L-48,-118 L-32,-86 Z', col) + path('M32,-96 L49,-132 L66,-96 Z', col) + path('M-18,-110 L0,-148 L18,-110 Z', col)
    for x in range(-44, 46, 12):
        o += rect(x, -60, 7, 7, col)
    o += rect(-4, -94, 8, 11, win, 4) + rect(43, -78, 7, 9, win, 3.5) + rect(-53, -66, 7, 9, win, 3.5) + rect(-24, -36, 7, 9, win, 3.5)
    o += path('M-7,0 L-7,-14 Q0,-22 7,-14 L7,0 Z', '#140A22')
    return o


def bare_tree(col='#1E1230'):
    """はだかの木（根もとが 0,0・右へ のびる 枝）"""
    o = path('M-14,0 Q-8,-50 -12,-100 Q-14,-130 -30,-150 L-24,-154 Q-6,-134 -2,-110 Q4,-150 26,-176 L32,-172 Q12,-140 8,-100 Q24,-118 52,-124 L54,-118 Q22,-108 8,-80 Q6,-40 14,0 Z', col)
    o += path('M-12,-112 Q-36,-118 -52,-104 L-48,-100 Q-34,-110 -14,-104 Z', col)
    return o


# ------------------------------------------------------------------ バレンタイン・ホワイトデー
def girl(dress='#F58AA8', dressD='#D9668A', hair='#7A4A2E', hairD='#5A3420', ribbon='#E23B5A', hold=None, hand_out=1, skin='#FFE0CC'):
    """女の子（前向き・長い髪・リボン）。足もと 0,0・高さ 約170。hand_out：さしだす手（1＝右・-1＝左）。hold：手に もつ物の SVG（手の所が 0,0）"""
    o = ''
    o += path('M-30,-138 Q-38,-100 -30,-70 L30,-70 Q38,-100 30,-138 Z', hairD)                 # うしろ髪
    o += rect(-13, -36, 9, 26, skin, 4) + rect(4, -36, 9, 26, skin, 4)                        # 足
    o += path('M-16,-12 L-2,-12 L-2,-2 Q-9,1 -17,-2 Z', ribbon) + path('M2,-12 L16,-12 L17,-2 Q9,1 2,-2 Z', ribbon)
    o += path('M-20,-96 Q-12,-104 0,-104 Q12,-104 20,-96 L36,-34 Q0,-26 -36,-34 Z', dress)      # ワンピース
    o += path('M2,-104 Q12,-104 20,-96 L36,-34 Q20,-31 4,-30 Z', dressD, 'opacity=".45"')
    o += path('M-12,-102 Q0,-90 12,-102 Q6,-96 0,-95 Q-6,-96 -12,-102 Z', '#FFFFFF')
    # うで
    hx = 46 * hand_out
    o += line(f'M{-16 * hand_out},-96 Q{-24 * hand_out},-76 {-22 * hand_out},-62', skin, 9)
    o += line(f'M{16 * hand_out},-96 Q{32 * hand_out},-88 {hx},-84', skin, 9)
    # あたま・前髪・ほお・リボン
    o += circ(0, -128, 27, skin)
    o += face(skin, y=-126, happy=False)
    o += path('M-28,-128 Q-30,-160 0,-160 Q30,-160 28,-128 Q20,-146 6,-142 Q4,-150 -2,-142 Q-16,-148 -28,-128 Z', hair)
    o += path('M-28,-128 Q-34,-104 -30,-86 Q-24,-100 -22,-118 Z', hair) + path('M28,-128 Q34,-104 30,-86 Q24,-100 22,-118 Z', hair)
    o += path('M-16,-156 Q-4,-160 8,-158', 'none', 'stroke="#9A6A48" stroke-width="2.4" stroke-linecap="round" opacity=".7"')
    o += path('M16,-154 Q26,-166 32,-152 Q24,-150 16,-154 Z', ribbon) + path('M16,-154 Q10,-168 2,-156 Q10,-152 16,-154 Z', ribbon) + circ(16, -154, 3.2, ribbon)
    if hold is not None:
        o += g(hold, hx, -84)
    o += circ(hx, -84, 5.5, skin)
    return o


def boy(top='#5B8FD6', topD='#4473B8', pants='#3A4A6A', hair='#3A2A22', skin='#FFE0CC', hand_out=-1, shy=True, hold=None):
    """男の子（前向き・短い髪）。足もと 0,0・高さ 約176。shy：もう一方の手を 頭のうしろへ（てれる）"""
    o = ''
    o += rect(-16, -42, 14, 30, pants, 4) + rect(2, -42, 14, 30, pants, 4)
    o += path('M-19,-14 L-1,-14 L-1,-2 Q-10,1 -20,-2 Z', '#FFFFFF') + path('M1,-14 L19,-14 L20,-2 Q10,1 1,-2 Z', '#FFFFFF')
    o += rect(-19, -5, 19, 4, '#C9D4E2', 2) + rect(1, -5, 19, 4, '#C9D4E2', 2)
    o += path('M-24,-102 Q0,-112 24,-102 L28,-38 Q0,-32 -28,-38 Z', top)
    o += path('M2,-108 Q14,-106 24,-102 L28,-38 Q16,-35 4,-34 Z', topD, 'opacity=".45"')
    o += path('M-9,-106 L0,-96 L9,-106 Z', '#FFFFFF')
    hx = 46 * hand_out
    o += line(f'M{20 * hand_out},-98 Q{34 * hand_out},-90 {hx},-86', top, 11) + circ(hx, -86, 6, skin)
    if shy:
        o += line(f'M{-22 * hand_out},-98 Q{-40 * hand_out},-118 {-22 * hand_out},-146', top, 11) + circ(-20 * hand_out, -148, 6, skin)
    else:
        o += line(f'M{-22 * hand_out},-98 Q{-28 * hand_out},-76 {-26 * hand_out},-62', top, 11) + circ(-26 * hand_out, -60, 6, skin)
    o += circ(0, -134, 28, skin)
    o += face(skin, y=-132, happy=True, blush='#F27F8A')
    o += path('M-29,-134 Q-32,-168 0,-168 Q32,-168 29,-134 Q24,-150 12,-152 L16,-144 Q4,-150 -6,-152 L-4,-144 Q-18,-150 -29,-134 Z', hair)
    if hold is not None:
        o += g(hold, hx, -86)
    return o


def heart_box(s=1.0, col='#D7264A', colD='#A81A38', rib='#F7C9D6'):
    """ハートの チョコの箱（リボン）。まん中が 0,0・はば 約 40s"""
    o = path(heart_d(0, 0, 20), colD) + path(heart_d(-1.5, -2, 18), col)
    o += path('M-14,-8 Q-8,-14 -2,-10', 'none', 'stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" opacity=".55"')
    o += rect(-2.5, -12, 5, 30, rib) + rect(-19, -2, 38, 5, rib)
    o += path('M0,-12 Q-12,-24 -10,-12 Z', rib) + path('M0,-12 Q12,-24 10,-12 Z', rib) + circ(0, -12, 2.8, '#FFFFFF')
    return g(o, s=s)


def choco_bar(w=70.0, h=34.0, wrap='#E8547C', wrapD='#C33A62', foil='#F2C14E'):
    """板チョコ（下の まん中が 0,0）：右半分は 包み紙・左は 割れ目の 四角"""
    ch, chD, chL = '#6B3A22', '#4E2816', '#8A5232'
    o = rect(-w / 2, -h, w, h, chD, 3)
    n, m = 4, 2
    cw, chh = (w * 0.55) / 2, h / m
    for i in range(2):
        for j in range(m):
            x, y = -w / 2 + i * cw, -h + j * chh
            o += rect(x + 1.5, y + 1.5, cw - 3, chh - 3, ch, 2) + rect(x + 2.5, y + 2.5, cw - 6, 3, chL, 1.5, 'opacity=".7"')
    o += rect(-w / 2 + w * 0.5, -h - 2, w * 0.08, h + 4, foil, 1)
    o += rect(-w / 2 + w * 0.56, -h - 3, w * 0.44 + 2, h + 6, wrap, 3) + rect(-w / 2 + w * 0.56, -h - 3, w * 0.44 + 2, 7, wrapD, 3, 'opacity=".5"')
    o += path(heart_d(w * 0.28, -h / 2, 7), '#FFFFFF', 'opacity=".9"')
    return o


def truffle(r=11.0, col='#5A3020', top='#F6E6CF', drizzle=True):
    """トリュフ（下の まん中が 0,0）"""
    o = ell(0, -r * 0.95, r, r * 0.95, col) + ell(r * 0.3, -r * 0.8, r * 0.55, r * 0.6, '#3E1F12', extra='opacity=".4"')
    if drizzle:
        o += line(f'M{f(-r * 0.75)},{f(-r * 1.3)} Q{f(-r * 0.4)},{f(-r * 1.65)} {f(0)},{f(-r * 1.3)} Q{f(r * 0.4)},{f(-r * 0.95)} {f(r * 0.75)},{f(-r * 1.35)}', top, r * 0.22)
    o += circ(-r * 0.35, -r * 1.35, r * 0.18, '#FFFFFF', 'opacity=".6"')
    return o


def marshmallow(w=26.0, h=20.0, col='#FFFFFF', colD='#E3EAF2'):
    """マシュマロ（ころんとした つつ形・下の まん中が 0,0）"""
    o = rect(-w / 2, -h, w, h, colD, h * 0.45) + rect(-w / 2, -h - 2, w, h * 0.7, col, h * 0.4)
    o += ell(-w * 0.18, -h + 2, w * 0.16, h * 0.12, '#FFFFFF', extra='opacity=".9"')
    return o


def jar(w=58.0, h=70.0, fill=(('#FFFFFF', '#E3EAF2'), ('#FFD6E2', '#F2B5C8'), ('#D6ECFB', '#B5D6EF')), rib='#6FAEDB', seed=3):
    """マシュマロの入った びん（リボン）。下の まん中が 0,0"""
    import random
    rnd = random.Random(seed)
    o = rect(-w / 2, -h, w, h, '#DDEFFA', 10, 'opacity=".55"')
    for row in range(4):
        for k in range(3):
            x = -w / 2 + 6 + k * (w - 12) / 3 + (6 if row % 2 else 0)
            y = -8 - row * 14
            c, cd = fill[(row * 3 + k + seed) % len(fill)]
            o += g(marshmallow(14, 11, c, cd), x + 5, y, rot=rnd.uniform(-20, 20))
    o += rect(-w / 2, -h, w, h, 'none', 10, 'stroke="#BFDDF2" stroke-width="2.4"')
    o += rect(-w / 2 + 5, -h + 6, 5, h - 14, '#FFFFFF', 2.5, 'opacity=".7"')
    o += rect(-w / 2 - 3, -h - 10, w + 6, 12, '#F3F7FB', 4) + rect(-w / 2 - 3, -h - 2, w + 6, 4, '#C9D7E6', 2)
    o += rect(-w / 2 - 1, -h + 6, w + 2, 6, rib, 2)
    o += path(f'M0,{-h + 9} Q-16,{-h - 4} -14,{-h + 10} Z', rib) + path(f'M0,{-h + 9} Q16,{-h - 4} 14,{-h + 10} Z', rib) + circ(0, -h + 9, 3, rib)
    return o


def gift_box(w, h, box, boxD, rib, ribD='#FFFFFF'):
    """リボンの ついた 箱（下の まん中が 0,0）"""
    return gift(w, h, box, boxD, rib)
