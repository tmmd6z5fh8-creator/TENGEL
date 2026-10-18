"""牧場：青空・芝・木の柵・栗毛の馬（左向き・立ち姿）
   壁紙の動き（まさちゃんの指定）：馬が右から左へ1〜8秒で移動して、左に着いたらふり向いて、1〜8秒で右へ。これをくり返す。
   ＋8〜22秒ごとに1回立ち止まって、芝生を食べる（首を下げて もぐもぐ）か、ユーザーの方を見て（正面の顔）しっぽを3回ふる。
   片道の秒は WALK_TRIPS（1〜8秒をばらばらに並べた20本）・立ち止まる所とすることは WALK_STOPS（7回・止まる間は 9.5〜21秒）。1周約2分でくり返す。
   ゆっくりは歩く・速いと脚を大きく・2秒以下はギャロップ。脚の動きは進んだ道のりに合わせる（すべらない）。ふり向くときは小さくぴょんと跳ねる。
   SVG の中の CSS アニメーション（<style>）なので、アプリの中のファイルなら <img> で出しても動く。
   視差効果を減らす（prefers-reduced-motion）なら止まる（今までの絵のまま。動かないときの絵は前と同じ）。
   claude.ai のキャンバスは、アップロードした SVG の <style> を消してしまうので、キャンバスの判定画面には絵をじかに入れる（inline・動きの CSS はページの <style>）：
     python3 ranch.py <出力フォルダ>                                  → ranch.svg（ファイルの形・<style>つき）・ranch_horse.svg
     python3 ranch.py <出力フォルダ> --judge <Judge_Ranch.dc.html>    → ＋判定画面の上の絵を inline の形に書きかえる
     python3 ranch.py --gaps                                          → 立ち止まる間の秒（8〜22秒か確かめる）"""
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *

CH = '#B8642C'      # 栗毛
CH_D = '#97501F'    # 向こう側の脚
MANE = '#5A2D12'
HOOF = '#3A2A1E'
LINE = '#4A2410'

# ---------- 動き（歩く・走る）の決まり ----------
WALK_X = (84, -176)       # 右はし・左はし（今の絵の位置からのずれ・壁紙の座標。片道 260）
TURN = .45                # ふり向く秒（小さく跳ねる）
FLIP_X = 239.8            # ふり向く中心（馬のまん中・壁紙の座標）
LEG_O = dict(ff=(54, 60), fh=(92, 54), nf=(42, 62), nh=(104, 52))   # 脚の付け根（回す中心・馬の座標）。f＝前・h＝後ろ・n＝手前・f＝向こう
TAIL_O = (113, 42)        # しっぽの付け根
BODY_O = (76, 54)         # 体の上下・かたむきの中心
NECK_O = (50, 46)         # 首の付け根（芝を食べるとき首を下げる中心）
HEAD_O = (29, 14)         # 頭の付け根（首に対して頭を回す中心）
HEAD_CX = 19              # 横向きの頭のまん中（こっちを見るとき、ここを中心に細くなって正面の顔に入れかわる）
FACE_O = (26, 18)         # 正面の顔のまん中
LEG_L = 48                # 脚の長さ（付け根 → ひづめ。体の上下の大きさに使う）
ALT = '青空と芝生、木の柵、草原を右へ左へ行ったり来たりする栗毛の馬のイラスト（ときどき立ち止まって芝を食べたり、こっちを見たりする）'
INLINE_IDS = ('sky', 'sun')


def pivot(inner, o, cls, on=True):
    """CSS で動かす <g class="cls">。中心 o を原点にしておくので、動きは rotate() などだけで書ける（止まっているときは元の絵と同じ）"""
    if not on:
        return inner
    x, y = o
    return f'<g transform="translate({f(x)} {f(y)})"><g class="{cls}"><g transform="translate({f(-x)} {f(-y)})">{inner}</g></g></g>'


def front_face():
    """こっちを向いた顔（正面）：ユーザーの方を見るときに出す（.rq・ふだんは見えない）。横向きの顔と同じ栗毛・流星・前髪・ほっぺ"""
    out = path(smooth([(15, 6), (12, -8), (21, 1)]), fill=CH)                                # 耳（左）
    out += path(smooth([(31, 1), (40, -8), (37, 6)]), fill=CH)                               # 耳（右）
    out += path(smooth([(15.5, 3), (14, -4), (19, 1.5)]), fill='#7A3A16')
    out += path(smooth([(33, 1.5), (38, -4), (36.5, 3)]), fill='#7A3A16')
    out += path(smooth([(26, -1), (36, 2), (40, 11), (38, 22), (35.5, 31), (31.5, 38.5), (26, 40.5), (20.5, 38.5), (16.5, 31), (14, 22), (12, 11), (16, 2)]), fill=CH)
    out += path(smooth([(17.5, 30), (26, 27.5), (34.5, 30), (33.5, 37.5), (26, 41), (18.5, 37.5)]), fill='#C97B47')    # 鼻のまわり（少し明るく）
    out += path(limb([(26, 7), (26, 19), (26, 29)], [5, 4.4, 6]), fill='#FFF6E8')          # 流星
    out += path(smooth([(19, 3), (26, -3), (33, 3), (31, 8), (27.5, 5.5), (26, 9), (24.5, 5.5), (21, 8)]), fill=MANE)   # 前髪
    eyes = ''.join(f'<circle cx="{x}" cy="15.5" r="2.6" fill="#22140C"/><circle cx="{x + .9}" cy="14.6" r=".9" fill="#fff"/>' for x in (19, 33))
    out += pivot(eyes, (26, 15.5), 'rk')                                                  # 目（.rk でまばたき）
    out += '<ellipse cx="22.3" cy="35" rx="1.7" ry="1.2" fill="#4A2410"/><ellipse cx="29.7" cy="35" rx="1.7" ry="1.2" fill="#4A2410"/>'   # 鼻の穴
    out += path('M23.5 38.6 q2.5 1.5 5 0', fill='none', stroke=LINE, stroke_width='1.1', stroke_linecap='round', opacity='.7')
    out += f'<ellipse cx="15.8" cy="24" rx="3" ry="2.2" fill="{CH_D}" opacity=".35"/><ellipse cx="36.2" cy="24" rx="3" ry="2.2" fill="{CH_D}" opacity=".35"/>'
    return out


def horse(anim=False):
    """左向きの馬（だいたい 0〜128 × -6〜108）。anim：脚・しっぽ・首・頭を動かせる形
       （.rlff・.rlfh・.rlnf・.rlnh＝脚・.rt＝しっぽ・.rn＝首（芝を食べる）・.rh＝横向きの頭（3つに分かれていて同じ動き）・.rq＝正面の顔（ふだんは見えない））"""
    far_f = limb([(54, 60), (58, 80), (60, 94), (60, 102)], [13, 9, 6.5, 7])        # 前の向こう脚（少し前に）
    far_h = limb([(92, 54), (87, 72), (96, 86), (94, 98), (94, 103)], [20, 13, 8, 6.5, 7])  # 後ろの向こう脚
    body = smooth([(34, 50), (40, 38), (52, 32), (68, 36), (84, 34), (100, 32), (112, 40), (116, 54),
                   (110, 66), (96, 70), (70, 72), (48, 70), (38, 64)])
    neck = smooth([(56, 36), (48, 22), (38, 11), (29, 7), (21, 14), (19, 25), (25, 38), (32, 50), (44, 54)])
    head = smooth([(31, 4), (22, 5), (14, 13), (7, 23), (3, 31), (6, 37), (13, 38), (20, 34), (27, 26), (32, 15)])
    near_f = limb([(42, 62), (42, 82), (43, 95), (43, 102)], [14, 9, 6.5, 7])        # 前の手前脚
    near_h = limb([(104, 52), (98, 72), (108, 86), (106, 98), (106, 103)], [24, 15, 8.5, 6.5, 7])  # 後ろの手前脚（飛節はうしろへ）
    ears = [smooth([(26, 7), (28, -6), (33, 4)]), smooth([(31, 8), (35, -4), (37, 7)])]
    # しっぽ（体のうしろ）
    tail = path(limb([(113, 42), (123, 50), (127, 66), (122, 86)], [8, 11, 10, 5]), fill=MANE)
    tail += path(smooth([(116, 46), (126, 58), (128, 76), (124, 92), (120, 80), (121, 62)]), fill=MANE)
    out = pivot(tail, TAIL_O, 'rt', anim)
    # 向こう側の脚（ひづめごと）
    out += pivot(path(far_f, fill=CH_D) + path('M56 101 L64 101 L65 106 L55 106 Z', fill=HOOF), LEG_O['ff'], 'rlff', anim)
    out += pivot(path(far_h, fill=CH_D) + path('M90 101 L98 101 L99 106 L89 106 Z', fill=HOOF), LEG_O['fh'], 'rlfh', anim)
    # 手前：体 → 手前の脚（白い靴下・ひづめごと）→ おなかの影（重ならないので、首・頭の前に描いても絵は同じ）
    out += path(body, fill=CH)
    out += pivot(path(near_f, fill=CH) + path('M39.6 95 L46.4 95 L46.6 101.5 L39.4 101.5 Z', fill='#FFF6E8')
                 + path('M39 101 L47 101 L48 106 L38 106 Z', fill=HOOF), LEG_O['nf'], 'rlnf', anim)
    out += pivot(path(near_h, fill=CH) + path('M102 101 L110 101 L111 106 L101 106 Z', fill=HOOF), LEG_O['nh'], 'rlnh', anim)
    out += path(smooth([(48, 66), (70, 68), (96, 66), (90, 72), (70, 73), (50, 71)]), fill=CH_D, opacity='.55')
    # 首と頭（.rn の中）：向こうの耳 → 首 → 頭・手前の耳・耳の中 → たてがみ → 前髪・流星・目・鼻・口・ほっぺ → 正面の顔
    nk = pivot(path(ears[1], fill=CH_D), HEAD_O, 'rh', anim)
    nk += path(neck, fill=CH)
    nk += pivot(path(head, fill=CH) + path(ears[0], fill=CH) + path(smooth([(28, 5), (29, -2), (31, 4)]), fill='#7A3A16'), HEAD_O, 'rh', anim)
    nk += path(smooth([(29, 4), (37, 6), (45, 12), (52, 21), (58, 31), (60, 37), (55, 35), (51, 29), (48, 31), (45, 24), (41, 25), (39, 18), (34, 17), (31, 10)]), fill=MANE)   # たてがみ（ふさが3つ）
    face = path(smooth([(28, 5), (22, 7), (18, 12), (22, 12), (25, 10)]), fill=MANE)           # 前髪
    face += path(limb([(23, 11), (16, 19), (9, 29)], [4.5, 4, 3.2]), fill='#FFF6E8')          # 鼻すじの白（流星）
    face += '<circle cx="19.5" cy="18.5" r="2.4" fill="#22140C"/><circle cx="20.3" cy="17.7" r=".8" fill="#fff"/>'
    face += path('M7.5 29.5 q2 -2 3.5 .5', fill='none', stroke=LINE, stroke_width='1.4', stroke_linecap='round')
    face += path('M8 35 q3 1 6 -.5', fill='none', stroke=LINE, stroke_width='1.1', stroke_linecap='round', opacity='.7')
    face += path(smooth([(22, 25), (26, 22), (27, 27), (24, 31)]), fill=CH_D, opacity='.35')  # ほっぺの丸み
    nk += pivot(face, HEAD_O, 'rh', anim)
    if anim:
        nk += f'<g transform="translate({f(FACE_O[0])} {f(FACE_O[1])})"><g class="rq" opacity="0"><g transform="translate({f(-FACE_O[0])} {f(-FACE_O[1])})">{front_face()}</g></g></g>'
    out += pivot(nk, NECK_O, 'rn', anim)
    return out


def tuft(x, y, s=1, c='#5C9A23'):
    return path(f'M{f(x)} {f(y)} l{f(2*s)} {f(-8*s)} l{f(1.6*s)} {f(8*s)} l{f(2.4*s)} {f(-6*s)} l{f(1.4*s)} {f(6*s)} l{f(2.2*s)} {f(-9*s)} l{f(1.6*s)} {f(9*s)} Z', fill=c)


def cloud(x, y, s, o='1'):
    return g(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(10*s)}"/><circle cx="{f(x+12*s)}" cy="{f(y-6*s)}" r="{f(13*s)}"/>'
             f'<circle cx="{f(x+27*s)}" cy="{f(y-1*s)}" r="{f(10*s)}"/><rect x="{f(x)}" y="{f(y-2*s)}" width="{f(27*s)}" height="{f(12*s)}" rx="{f(6*s)}"/>',
             fill='#FFFFFF', opacity=o)


def fence(x0, x1, ytop, ybot, n):
    out = ''
    step = (x1 - x0) / (n - 1)
    rails = ''
    for yy in (ytop + 7, ytop + 18):
        rails += f'<rect x="{f(x0 - 3)}" y="{f(yy)}" width="{f(x1 - x0 + 6)}" height="5" rx="1.5" fill="#D29A5E" stroke="#8A5A2B" stroke-width="1.2"/>'
    posts = ''
    for i in range(n):
        x = x0 + i * step
        posts += f'<path d="M{f(x - 3.5)} {f(ybot)} L{f(x - 3.5)} {f(ytop + 3)} L{f(x)} {f(ytop - 1)} L{f(x + 3.5)} {f(ytop + 3)} L{f(x + 3.5)} {f(ybot)} Z" fill="#C88B4E" stroke="#8A5A2B" stroke-width="1.2" stroke-linejoin="round"/>'
    return posts + rails


# ---------- 歩く・走る（CSS のキーフレームを作る） ----------
def ramp_of(d):
    """動き出し・止まるまでの割合（片道の秒 d のうち）。ゆっくりでも速くても 0.3〜0.9秒くらい"""
    return min(.3, (.2 + .09 * d) / d)


def s_of(u, r):
    """時間の割合 u → 進んだ道のりの割合（はじめと終わり r だけ、だんだん速く・だんだん遅く）"""
    v = 1 / (1 - r)
    if u <= r:
        return v * u * u / (2 * r)
    if u >= 1 - r:
        return 1 - v * (1 - u) ** 2 / (2 * r)
    return v * (u - r / 2)


def u_of(s, r):
    """s_of の逆（道のりの割合 → 時間の割合）"""
    v, sr = 1 / (1 - r), r / (2 * (1 - r))
    if s <= sr:
        return math.sqrt(2 * r * s / v)
    if s >= 1 - sr:
        return 1 - math.sqrt(2 * r * (1 - s) / v)
    return s / v + r / 2


def gait(d, D=None):
    """片道 d 秒の走り方：(種類, 脚の振れ（度）, 半歩の数, 速さ 0〜1)。D：動く道のり（立ち止まるときは片道の一部）。
       半歩の数は整数（止まったとき・着いたとき脚がまっすぐ）"""
    k = (8 - d) / 7
    D = WALK_X[0] - WALK_X[1] if D is None else D
    if d <= 2:
        A, S, kind = 30, 100, 'gallop'
    else:
        A, S, kind = 12 + 12 * k, 30 + 40 * k, 'trot'
    return kind, A, max(2, round(2 * D / S)), k


# 脚ごとの (向き, 遅れ)：角度 ＝ 向き × 振れ × sin(2π(歩の位相 − 遅れ))。正の角度＝脚が前（左向きの馬で左）へ
LEG_PHASE = dict(trot=dict(nf=(1, 0), fh=(1, 0), ff=(-1, 0), nh=(-1, 0)),          # 速足：ななめの2本ずつ
                 gallop=dict(nf=(1, 0), ff=(1, .08), nh=(-1, 0), fh=(-1, .08)))     # ギャロップ：前の2本と後ろの2本（向こう側は少し遅れる）


def add_move(ch, ts, dm, xa, xb, d):
    """ts 秒から dm 秒で xa → xb へ動く（走り方は片道 d 秒のもの）：位置・脚・体・しっぽのキーフレームを足す。終わりは脚まっすぐ"""
    r = ramp_of(dm)
    sr = s_of(r, r)
    kind, A, N, k = gait(d, abs(xb - xa))
    tm = lambda phi: ts + dm * u_of(phi / (N / 2), r)     # 歩の位相 → 秒
    # 位置：だんだん速く → 同じ速さ → だんだん遅く（2次の曲線）
    ch['walk'] += [(ts, xa, 'cubic-bezier(.333,0,.667,.333)'), (ts + r * dm, xa + sr * (xb - xa), 'linear'),
                   (ts + (1 - r) * dm, xb - sr * (xb - xa), 'cubic-bezier(.333,.667,.667,1)'), (ts + dm, xb, None)]
    # 脚：振れのいちばん大きいところだけキーフレーム（あいだは ease-in-out ＝ ほぼ sin）
    for leg, (sg, lag) in LEG_PHASE[kind].items():
        ev, m = [(ts, 0, None)], 0
        while True:
            phi = lag + .25 + m * .5
            if phi >= N / 2 - 1e-6:
                break
            ev.append((tm(phi), round(sg * A * (1 if m % 2 == 0 else -1), 1), None))
            m += 1
        ch[leg] += ev + [(ts + dm, 0, None)]
    # 体の上下（とギャロップのかたむき）・しっぽ
    if kind == 'trot':
        B = LEG_L * (1 - math.cos(math.radians(A))) * 1.1           # 脚が開くと、ひづめが地面から浮かないように体が下がる
        T1 = 3 + 5 * k
        ev_b, ev_t = [(ts, (0, 0), None)], [(ts, 0, None)]
        for m in range(1, 2 * N):
            odd = m % 2 == 1
            ev_b.append((tm(m / 4), (round(B, 2) if odd else 0, 0), None))
            ev_t.append((tm(m / 4), round(-T1, 1) if odd else 0, None))
    else:
        ev_b, ev_t, m = [(ts, (0, 0), None)], [(ts, 0, None)], 0
        while .25 + m * .5 < N / 2 - 1e-6:
            ext = m % 2 == 0                                            # 脚がいちばん開く（体がのびて浮く）
            ev_b.append((tm(.25 + m * .5), (-5, 4) if ext else (6, -4), None))
            ev_t.append((tm(.25 + m * .5), -24 if ext else -12, None))
            m += 1
    ch['bob'] += ev_b + [(ts + dm, (0, 0), None)]
    ch['tail'] += ev_t + [(ts + dm, 0, None)]


# ---------- 立ち止まる（まさちゃんの指定：8〜22秒ごとに1回立ち止まって、芝生を食べる か ユーザーの方を見てしっぽを3回ふる） ----------
GRAZE_T = 3.6     # 芝を食べる秒：首を下げる（0.55秒）→ もぐもぐ3回 → 首を上げる
LOOK_T = 3.0      # こっちを見る秒：横向きの頭が細くなって正面の顔に（0.32秒）→ しっぽを3回ふる・まばたき → 横向きにもどる
GRAZE_POSE = (-100, 1.2, 70)   # 首を下げたとき：首の角度・首ののび（首のすじに沿って）・頭の角度（首に対して）
NECK_AXIS = -120               # 首のすじの向き（度。首の付け根 → 頭の付け根）


def add_stop(ch, t, what):
    """t 秒に止まって what（'graze'＝芝を食べる・'look'＝こっちを見てしっぽ3回）をする。かかった秒を返す"""
    if what == 'graze':
        an, k, ah = GRAZE_POSE
        ki = round(1 / k, 4)
        ch['neck'] += [(t, (0, 1), None), (t + .55, (an, k), None), (t + 2.95, (an, k), None), (t + 3.5, (0, 1), None)]
        hd = [(t, (0, 1, 1), None), (t + .55, (ah, ki, 1), None)]
        for j, a in enumerate((62, 72, 62, 72, 62, 72, 64)):          # もぐもぐ（頭を小さく上下）
            hd.append((t + .85 + .3 * j, (a, ki, 1), None))
        hd += [(t + 2.95, (ah, ki, 1), None), (t + 3.5, (0, 1, 1), None)]
        ch['head'] += hd
        ch['tail'] += [(t + 1.0, 0, None), (t + 1.5, -16, None), (t + 2.1, 6, None), (t + 2.6, 0, None)]   # しっぽを1回ゆっくり
        return GRAZE_T
    # こっちを見る：横向きの頭（.rh）が細くなる → 正面の顔（.rq）が広がる。しっぽを3回ふる・まばたき1回 → もどる
    # 頭がなくなる一瞬がないように、細くなるのと広がるのを少し重ねる
    ch['head'] += [(t, (0, 1, 1), None), (t + .2, (0, 1, 0), None), (t + 2.8, (0, 1, 0), None), (t + 3.0, (0, 1, 1), None)]
    ch['face'] += [(t, (0, 0), None), (t + .1, (0, 1), None), (t + .32, (1, 1), None), (t + 2.68, (1, 1), None), (t + 2.9, (0, 1), None), (t + 3.0, (0, 0), None)]
    ch['blink'] += [(t + 1.5, 1, None), (t + 1.57, .1, None), (t + 1.66, 1, None)]
    wag = [(t + .45, 0, None)]
    for j in range(3):                                                # しっぽを3回（上へ → 下へ）
        wag += [(t + .65 + .5 * j, -22, None), (t + .9 + .5 * j, 10, None)]
    ch['tail'] += wag + [(t + 2.1, 0, None)]
    return LOOK_T


# 1周（20本の片道・約2分）と、立ち止まる所：片道の番号 → (止まる所（その片道の道のりの割合）, すること)。
# 歩いている秒（ふり向く秒も入れる）で、止まってから次に止まるまで 8〜22秒（walk_timeline の gaps）
WALK_TRIPS = (5.5, 2.5, 7.0, 1.0, 4.0, 8.0, 3.0, 6.0, 1.5, 4.5, 3.5, 6.5, 2.0, 7.5, 5.0, 1.0, 4.5, 8.0, 2.5, 5.5)
WALK_STOPS = {2: (.25, 'look'), 4: (.59, 'graze'), 7: (.8, 'graze'), 10: (.3, 'look'), 14: (.15, 'graze'), 17: (.3, 'look'), 19: (.7, 'graze')}


def walk_timeline():
    """キーフレームのもと：チャンネルごとに [(秒, 値, つぎまでの動き方 or None)]。
       1周の秒 T・今の絵の位置になる秒 t0・立ち止まり [(はじめ, 終わり, すること)] も返す"""
    ch = dict(walk=[], flip=[], bob=[], tail=[], nf=[], ff=[], nh=[], fh=[],
              neck=[(0, (0, 1), None)], head=[(0, (0, 1, 1), None)], face=[(0, (0, 0), None)], blink=[(0, 1, None)])
    ts, stops = 0.0, []
    for i, d in enumerate(WALK_TRIPS):
        x0, x1 = (WALK_X[0], WALK_X[1]) if i % 2 == 0 else (WALK_X[1], WALK_X[0])
        sx = 1 if i % 2 == 0 else -1               # 右 → 左は左向き（元の絵）・左 → 右は右向き
        t_trip = ts
        if i in WALK_STOPS:
            fr, what = WALK_STOPS[i]
            xs = x0 + fr * (x1 - x0)
            add_move(ch, ts, d * fr, x0, xs, d)
            ts += d * fr
            dur = add_stop(ch, ts, what)
            stops.append((ts, ts + dur, what))
            ts += dur
            add_move(ch, ts, d * (1 - fr), xs, x1, d)
            ts += d * (1 - fr)
        else:
            add_move(ch, ts, d, x0, x1, d)
            ts += d
        ch['flip'] += [(t_trip, sx, None), (ts, sx, 'cubic-bezier(.8,0,.2,1)')]       # ふり向く：まん中（細くなる所）はさっと
        ch['bob'].append((ts + TURN / 2, (-4, 0), None))                                # ふり向くとき、ぴょん
        ts += TURN
    T = ts
    for c in ch.values():                                                      # 1周の終わり＝はじめと同じ
        c.append((T, c[0][1], None))
    # 今の絵の位置（ずれ 0）になる時刻：0番（右 → 左・止まらない）のとちゅう
    assert 0 not in WALK_STOPS
    d0, r0 = WALK_TRIPS[0], ramp_of(WALK_TRIPS[0])
    t0 = d0 * u_of(WALK_X[0] / (WALK_X[0] - WALK_X[1]), r0)
    return ch, T, t0, stops


def walk_gaps():
    """立ち止まってから次に立ち止まるまでの、歩いている秒（1周をまたぐ所も）と、ページを開いてから1回目まで"""
    _, T, t0, stops = walk_timeline()
    gaps = [round((stops[(i + 1) % len(stops)][0] - stops[i][1]) % T, 2) for i in range(len(stops))]
    return gaps, round(stops[0][0] - t0, 2), round(T, 2)


def walk_css(sel='', kn='ranch', tag=True):
    """歩く・走る・立ち止まる CSS。sel：前につけるセレクタ（ページに入れるとき '.bnr'）・kn：キーフレームの名前の頭"""
    ch, T, t0, _ = walk_timeline()
    pct = lambda t: f'{100 * t / T:.4f}'.rstrip('0').rstrip('.') + '%'
    fx = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)
    ax = NECK_AXIS
    hx = HEAD_CX - HEAD_O[0]
    val = dict(walk=lambda v: f'transform:translate({fx(float(v))}px,0)', flip=lambda v: f'transform:scale({v},1)',
               bob=lambda v: f'transform:translate(0,{fx(float(v[0]))}px) rotate({fx(float(v[1]))}deg)',
               neck=lambda v: f'transform:rotate({v[0]}deg) rotate({ax}deg) scale({v[1]},1) rotate({-ax}deg)',
               head=lambda v: f'transform:rotate({ax}deg) scale({v[1]},1) rotate({-ax}deg) rotate({v[0]}deg) translate({hx}px,0) scale({v[2]},1) translate({-hx}px,0)',
               face=lambda v: f'transform:scale({v[0]},1);opacity:{v[1]}', blink=lambda v: f'transform:scale(1,{v})')
    names = dict(walk=('rw', 'Walk', 'linear'), flip=('rf', 'Flip', 'ease-in-out'), bob=('ry', 'Bob', 'ease-in-out'), tail=('rt', 'Tail', 'ease-in-out'),
                 nf=('rlnf', 'NF', 'ease-in-out'), ff=('rlff', 'FF', 'ease-in-out'), nh=('rlnh', 'NH', 'ease-in-out'), fh=('rlfh', 'FH', 'ease-in-out'),
                 neck=('rn', 'Neck', 'ease-in-out'), head=('rh', 'Head', 'ease-in-out'), face=('rq', 'Face', 'ease-in-out'), blink=('rk', 'Blink', 'ease-in-out'))
    pre = f'{sel} ' if sel else ''
    css = ''
    for key, (cls, nm, tf) in names.items():
        fn = val.get(key, lambda v: f'transform:rotate({fx(float(v))}deg)')
        kf, last = '', None
        for t, v, e in sorted(ch[key], key=lambda z: z[0]):
            p = pct(t)
            if p == last:                       # 同じ時刻は1つに（あとの値）
                kf = kf[:kf.rfind(last + '{')]
            kf += f'{p}{{{fn(v)}' + (f';animation-timing-function:{e}' if e and e != tf else '') + '}'
            last = p
        css += (f'{pre}.{cls}{{transform-box:view-box;transform-origin:0 0;animation:{kn}{nm} {T:.2f}s {tf} -{t0:.2f}s infinite}}'
                f'@keyframes {kn}{nm}{{{kf}}}')
    css += f'@media (prefers-reduced-motion:reduce){{' + ','.join(f'{pre}.{c[0]}' for c in names.values()) + '{animation:none}}'
    return f'<style>{css}</style>' if tag else css


def banner(anim=True):
    W, H = 390, 160
    defs = ('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9DDF6"/><stop offset="1" stop-color="#E6F6FC"/></linearGradient>'
            '<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6C2"/><stop offset=".55" stop-color="#FFE57A" stop-opacity=".9"/><stop offset="1" stop-color="#FFE57A" stop-opacity="0"/></radialGradient>')
    if anim:
        defs = walk_css() + defs
    b = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    b += '<circle cx="342" cy="34" r="30" fill="url(#sun)"/><circle cx="342" cy="34" r="15" fill="#FFD84A"/>'
    b += cloud(52, 34, 1.0) + cloud(196, 22, .75, '.95') + cloud(282, 50, .55, '.9')
    # 遠くの丘・小屋
    b += path('M0 92 C 50 70, 110 66, 170 82 S 300 60, 390 80 L390 160 L0 160 Z', fill='#B9DE7E')
    bx, by = 300, 64
    b += f'<rect x="{bx}" y="{by}" width="30" height="20" fill="#C8553D"/><path d="M{bx - 4} {by + 1} L{bx + 15} {by - 13} L{bx + 34} {by + 1} Z" fill="#9C3A2A"/>'
    b += f'<rect x="{bx + 10}" y="{by + 7}" width="10" height="13" fill="#F3E3C8"/><path d="M{bx + 10} {by + 7} L{bx + 20} {by + 20} M{bx + 20} {by + 7} L{bx + 10} {by + 20}" stroke="#C8553D" stroke-width="1.4"/>'
    b += path('M0 108 C 70 94, 150 98, 230 108 S 340 98, 390 104 L390 160 L0 160 Z', fill='#92CB45')
    b += fence(14, 150, 92, 128, 5)
    b += path('M0 128 C 110 118, 250 120, 390 126 L390 160 L0 160 Z', fill='#7DBA34')
    # 草・花
    for x, y, s in [(8, 146, 1), (40, 152, .8), (70, 141, 1.1), (122, 150, .9), (160, 140, 1), (260, 148, 1.1), (300, 139, .8), (338, 151, 1), (372, 142, .9), (226, 156, .7)]:
        b += tuft(x, y, s)
    for x, y, c in [(30, 136, '#FFFFFF'), (96, 146, '#FFE14D'), (142, 134, '#FFFFFF'), (284, 132, '#FFE14D'), (318, 146, '#FFFFFF'), (356, 132, '#FFFFFF'), (250, 138, '#FFE14D')]:
        b += f'<g fill="{c}"><circle cx="{x - 2.2}" cy="{y}" r="2"/><circle cx="{x + 2.2}" cy="{y}" r="2"/><circle cx="{x}" cy="{y - 2.2}" r="2"/><circle cx="{x}" cy="{y + 2.2}" r="2"/></g><circle cx="{x}" cy="{y}" r="1.3" fill="#F2A33A"/>'
    # 馬（影＋本体）。anim：.rw（右 ↔ 左）の中に 影（ふり向いても そのまま）と .rf（ふり向く）→ .ry（体の上下）の馬
    shadow = '<ellipse cx="236" cy="139" rx="50" ry="5" fill="#4E8A1C" opacity=".35"/>'
    hz = g(pivot(horse(anim), BODY_O, 'ry', anim), transform='translate(186 52) scale(.84)')
    b += f'<g class="rw">{shadow}{pivot(hz, (FLIP_X, 0), "rf")}</g>' if anim else shadow + hz
    return svg(W, H, b, defs)


def inline(alt=ALT, p='rb'):
    """ページの中にじかに入れる形（<svg class="bnr">）と、そのページの <style> に入れる動きの CSS。
       id に p をつけて、ページのほかの SVG とぶつからないようにする。戻り値 (svg, css)"""
    s = re.sub(r'<style>.*?</style>', '', banner(), flags=re.S)
    for i in INLINE_IDS:
        s = s.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'url(#{i})', f'url(#{p}{i})')
    s = s.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '').replace('<svg ', f'<svg class="bnr" role="img" aria-label="{alt}" ', 1)
    return s, walk_css('.bnr', f'{p}Ranch', tag=False)


def judge_inline(fn):
    """判定画面（Judge_Ranch.dc.html）の上の絵を inline の形に書きかえる（<img class="bnr"> か、前に入れた <svg class="bnr">）。動きの CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    svg_html, css = inline()
    page, n = re.subn(r'<img class="bnr" [^>]*>|<svg class="bnr" .*?</svg>', lambda m: svg_html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 牧場の壁紙：馬が右へ左へ（ranch.py） */\n{css}\n/* /牧場の壁紙 */\n'
    if '/* 牧場の壁紙：' in page:
        page = re.sub(r'/\* 牧場の壁紙：.*?/\* /牧場の壁紙 \*/\n', lambda m: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    if sys.argv[1] == '--gaps':
        gaps, first, T = walk_gaps()
        print('止まる間の秒', gaps, '・開いてから1回目', first, '・1周', T)
        assert all(8 <= x <= 22 for x in gaps + [first])
        sys.exit()
    out = sys.argv[1]
    open(f'{out}/ranch.svg', 'w').write(banner())
    open(f'{out}/ranch_horse.svg', 'w').write(svg(140, 120, g(horse(), transform='translate(4 10)')))
    if '--judge' in sys.argv:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
