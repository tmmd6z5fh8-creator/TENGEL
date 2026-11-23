"""海賊の 壁紙（壁紙パック）の 馬の 船長：いままでの 壁紙と 同じ 馬（horse_flat）に、三角帽（金の ふち・金の 蹄鉄の しるし・赤い 羽）・
   赤い スカーフ・布の すみに 金の 蹄鉄。
   第4.93版（まさちゃん「馬は、ランダムに船を歩き回るようにして！」）：甲板を 歩きまわる コマ（常歩＝4拍子・12コマ・右向き。左向きは ページで 反転）と、
   止まって まわりを 見る コマ（前を 見る・見上げる 2つ・のぞきこむ 2つ＝5コマ）。どちらも 同じ カメラ・同じ 地面の 高さ（甲板の 奥：宝箱と 舵輪の うしろを 歩く）。
   足の 動きは 常歩（左うしろ → 左前 → 右うしろ → 右前・1本の 足は 1回りの 62% 地面に つく：パドックと 同じ 考え方を ここに 写した）。
   歩く はやさ（ページの px／秒）は 地面に ついた ひづめが すべらない はやさ（コマの ひづめの 動きから 出す）。
   第4.166版（まさちゃん 2026/11/13 15:21「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：
     歩く コマは 1回り 12コマ・1.25秒（＝1秒に 9.6コマ）だった → **36コマ・1.2秒（1秒に ちょうど 30コマ）**。シートは 12コマ × 3行の ます目（sheets.make_sheet の cols。止まった 形は 13コマ × 2行）。
     止まった 形は 5コマ（前・見上げる 2つ・のぞきこむ 2つ：あいだが 1コマ だけで カクッと 動いた）→ **25コマ**：前 1 ＋ 見上げて いく 8（u1〜u8）＋ のぞきこんで いく 8（d1〜d8）＋
     歩く 形（1回りの はじめ）から 止まった 形へ 足を そろえる つなぎ 8（t1〜t8：歩きだす ときは 逆に めくる）。あいだの 形は 首・頭・足の 角度を なめらかに つなぐ（ease）。
     歩く 足は パドックの 壁紙と 同じ 解き方（make/paddock_gait.py：ひづめの 道を 先に 決めて 足の 角度を 逆に 解く）に した：前の 足（キーを つないだ 角度）は
     地面に ついた ひづめの 高さが 足ごとに 少し ちがい、いちばん 低い ひづめを 地面に 合わせて いた ので、足が つく たびに 体が 1px ほど とんだ（12コマでは 目立たない・
     36コマに すると カクッと 見える）。新しい 足は 地面に ついて いる 間 ひづめが 同じ 地面の 線の 上を まっすぐ うしろへ 動く ＝ 体の 上下は ほんの 少しの ゆれ だけ（walk_dy）。
     前の 絵（12コマ・5コマ）は 消さない（手元の フォルダに 残る・アプリには 入らない：台帳が 新しい 絵を さす）
   python3 kisekae/pack/make/pirate_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の pirate.walk・pirate.stand（前の pirate.captain は 消す）"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import still_sheet, save_webp, record, preview_png, FLAT, render, make_sheet, HOOF_ORDER, PACK  # noqa: E402
import numpy as np  # noqa: E402
from cute_horse import smooth, path, stroke, circ, ell, unit, V, f2  # noqa: E402

PAL = dict(body='#E6E1DA', shade='#B8B0A6', muzzle='#F4F0EA', mane='#3A3434', maneD='#211D1D', hoof='#4A4440', eye='#1A1414',
           blush='#E8A898', tack='#2A1A12', ring='#E8B84A', cloth='#8E1E1E', clothTrim='#E8B84A', num='#F6E2B0', saddle='#2A1C14',
           bodyShade='#D3CCC3')
SPOT = dict(pose='stand', facing='left', box=(232, 84, 446, 300), azim=-6, shadow=('#2A1A0E', 0.30), ext=(0.067, 0.0765))
GOLD, GOLD_D, HAT, HAT_D = '#F0C24E', '#A8781C', '#1E1A1C', '#0C0A0B'


def horseshoe(c, r, rot, col, hole):
    """蹄鉄（U が 上に ひらく）：中心 c・大きさ r・回す rot°"""
    pts_o, pts_i = [], []
    for k in range(25):
        a = math.radians(-200 + 220 * k / 24)          # 下を まわる U
        pts_o.append((math.cos(a) * r, -math.sin(a) * r * 1.08))
        pts_i.append((math.cos(a) * r * 0.58, -math.sin(a) * r * 0.64))
    pts = pts_o + pts_i[::-1]
    cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    tr = lambda q: V(c[0] + q[0] * cs - q[1] * sn, c[1] + q[0] * sn + q[1] * cs)
    d = 'M' + ' L'.join(f'{f2(tr(q)[0])},{f2(tr(q)[1])}' for q in pts) + ' Z'
    out = [path(d, col, 'stroke="#5A3A0A" stroke-width="0.6" stroke-linejoin="round"')]
    for k in (3, 8, 16, 21):
        a = math.radians(-200 + 220 * k / 24)
        out.append(circ(tr((math.cos(a) * r * 0.79, -math.sin(a) * r * 0.86)), r * 0.075, hole))
    return out


def acc(m):
    p, fx = m['p1u'], m['fx']
    hd = unit(m['head_dir'])
    # ---- 三角帽：頭の 上（耳の うしろ → 前髪の あいだ）に、ふねの 形の つば（前と うしろが 上へ 反る）と まるい 山
    tilt = -6.0
    up = V(-math.sin(math.radians(tilt)) * fx, -math.cos(math.radians(tilt)))
    br = unit(V(-up[1], up[0]))
    if br[0] * fx < 0:
        br = -br
    base = m['poll'] + (m['forelock'] - m['poll']) * 0.38 + up * 0.035 * p
    Z = 1.12
    L = lambda x, y: base + br * x * Z * p + up * y * Z * p
    crown = [L(-0.17, 0.02), L(-0.19, 0.12), L(-0.12, 0.22), L(0.0, 0.25), L(0.12, 0.22), L(0.18, 0.12), L(0.16, 0.02)]
    brim = [L(-0.36, 0.16), L(-0.30, 0.07), L(-0.16, 0.00), L(0.0, -0.025), L(0.16, 0.0), L(0.30, 0.08), L(0.37, 0.18),
            L(0.30, 0.15), L(0.16, 0.085), L(0.0, 0.065), L(-0.16, 0.085), L(-0.30, 0.13)]
    hat = [path(smooth(crown, sharp=(0, 6)), HAT),
           path(smooth([L(-0.16, 0.03), L(-0.17, 0.12), L(-0.10, 0.20), L(-0.02, 0.215), L(-0.06, 0.12), L(-0.08, 0.03)], sharp=(0, 5)), '#3A3236', 'fill-opacity=".55"'),
           path(smooth(brim, sharp=(0, 6)), HAT_D),
           stroke(smooth([L(-0.36, 0.16), L(-0.30, 0.13), L(-0.16, 0.085), L(0.0, 0.065), L(0.16, 0.085), L(0.30, 0.15), L(0.37, 0.18)], closed=False), GOLD, 0.028 * p),
           stroke(smooth([L(-0.33, 0.13), L(-0.28, 0.065), L(-0.15, 0.012), L(0.0, -0.012), L(0.15, 0.012), L(0.28, 0.07), L(0.34, 0.15)], closed=False), '#3A3236', 0.012 * p)]
    hat += horseshoe(L(0.02, 0.12), 0.055 * p, -math.degrees(math.atan2(br[1], br[0])) * 0 + (0 if fx > 0 else 0), GOLD, HAT_D)
    # 赤い 羽（うしろへ）
    fb = L(-0.14, 0.17)
    hat.insert(0, path(smooth([fb, L(-0.30, 0.34), L(-0.46, 0.36), L(-0.34, 0.27), L(-0.20, 0.18)], sharp=(0, 2)), '#C8322A'))
    hat.insert(1, stroke(smooth([fb, L(-0.28, 0.30), L(-0.44, 0.35)], closed=False), '#7A1414', 0.012 * p))
    # ---- 眼帯（目の 上・ひもは ひたい と 耳の うしろへ）
    e = m['eye']
    ang = math.degrees(math.atan2(hd[1], hd[0]))
    patch = [stroke(smooth([e + hd * 0.05 * p + up * 0.03 * p, (e + m['forelock']) / 2 + hd * 0.02 * p, m['forelock'] + up * 0.01 * p], closed=False), '#141010', 0.02 * p),
             stroke(smooth([e - hd * 0.05 * p + up * 0.01 * p, (e + m['poll']) / 2 - up * 0.01 * p, m['poll']], closed=False), '#141010', 0.02 * p),
             ell(e + up * 0.004 * p, 0.062 * p, 0.048 * p, ang, '#141010'),
             ell(e + up * 0.014 * p - hd * 0.01 * p, 0.03 * p, 0.012 * p, ang, '#3A3236')]
    # ---- 赤い スカーフ（首の 根もと・のどの 下で むすんで 三角が たれる）
    top, bot, ax = m['collar'](0.74)
    dv = unit(bot - top)
    a, b = top - dv * 0.02 * p, bot + dv * 0.015 * p
    mid = (a + b) / 2 - ax * 0.03 * p
    hh = 0.05 * p
    band = [a + ax * hh, mid + ax * hh, b + ax * hh, b - ax * hh, mid - ax * hh, a - ax * hh]
    k = b - dv * 0.01 * p
    nv = V(-dv[1], dv[0])
    tri = [k - ax * 0.07 * p, k + ax * 0.07 * p, k + dv * 0.2 * p + ax * 0.02 * p]
    neck = [path(smooth(band), '#C8322A'), path(smooth(tri, sharp=(0, 1, 2)), '#B02A22')]
    for t in (0.2, 0.45, 0.75):
        q = a + (b - a) * t
        neck.append(circ(q + ax * 0.012 * p, 0.012 * p, '#FFF1D8'))
    neck.append(circ(k + dv * 0.09 * p, 0.012 * p, '#FFF1D8'))
    neck.append(circ(k, 0.032 * p, '#8E1E1A'))
    # ---- 布の まん中に 金の 蹄鉄
    x0, x1, yt, yb, trim = m['cloth']
    cloth = horseshoe(V((x0 + x1) / 2, (yt + trim) / 2 + 0.01 * p), 0.085 * p, 0, GOLD, '#8E1E1E')
    return dict(head=hat, neck=neck, cloth=cloth)


# ---------------------------------------------------------------- 歩く（常歩）：パドックの 壁紙と 同じ 考え方（キー・位相・すべらない はやさ）
N = 36             # 1回りの コマ（第4.166版：12 → 36）
CYCLE = 1.2        # 1回りの 秒（ページと 同じ。第4.166版：1.25 → 1.2 ＝ 1コマ 1/30秒 ちょうど）
COLS = 12          # 歩く シートの 1行の コマ（36コマ ＝ 3行）
COLS_S = 13        # 止まった 形の シートの 1行の コマ（25コマ ＝ 2行）
KU = 8             # 見上げて いく コマ（u1〜u8：u8 が 見上げきった 形）
KD = 8             # のぞきこんで いく コマ（d1〜d8：d8 が のぞきこんだ 形）
KT = 8             # 歩く 形（1回りの はじめ）→ 止まった 形 の つなぎの コマ（t1〜t8：t1 が 歩く 形に 近い）
ST = 0.62          # 足が 地面に ついて いる 長さ（1回りの 割合）
F_KEYS = [(0.00, [-114, -80, -80, -56]), (0.31, [-126, -92, -92, -62]), (0.60, [-136, -106, -106, -78]),
          (0.74, [-128, -78, -150, -150]), (0.88, [-110, -62, -92, -82])]
H_KEYS = [(0.00, [-52, -110, -82, -56]), (0.31, [-62, -118, -94, -64]), (0.60, [-73, -127, -109, -81]),
          (0.74, [-58, -128, -66, -40]), (0.88, [-50, -114, -72, -50])]
OFF = dict(HL=0.00, FL=0.25, HR=0.50, FR=0.75)
BOX = (232, 78, 438, 280)       # 2倍の 画素：甲板の 奥（ひづめ＝280 → 画面の 140px）。宝箱（下の はし 146px）・舵輪の 台（154px）より 奥
SPOT_W = dict(pose='stand', facing='right', box=BOX, azim=6, shadow=('#2A1A0E', 0.0), ext=(0.06, 0.06))
SPOT_P = {k: v for k, v in SPOT_W.items() if k != 'ext'}       # 第4.166版：コマを 描く 置き場（管の のびは ポーズの cannon_ext に 入れる。カメラは SPOT_W で 決める＝前と 同じ）
EXT0 = dict(FL=0.06, FR=0.06, HL=0.0, HR=0.0)                   # 止まった 形の 管の のび（SPOT_W の ext と 同じ：前足を 地面に つける）
GROUND = BOX[3] - 4
XV = -0.10         # 地面の 線を 決める 点（体の 中の x：前足と うしろ足の まん中。paddock_moves.XV と 同じ）
ZN = 0.15          # 手前の ひづめの 目印の z（右向き：horse_flat の hooves と 同じ）


def ease(t):
    return t * t * (3 - 2 * t)


def leg_at(keys, p):
    p %= 1.0
    ks = keys + [(keys[0][0] + 1.0, keys[0][1])]
    for (p0, a0), (p1, a1) in zip(ks, ks[1:]):
        if p0 <= p <= p1:
            t = (p - p0) / (p1 - p0)
            if p1 > ST:
                t = ease(t)
            return [round(x0 + (x1 - x0) * t, 2) for x0, x1 in zip(a0, a1)]
    return keys[0][1]


def walk_cycle(n=None):
    """常歩 1回り n コマ（右向き）：パドックの 壁紙と 同じ 足（paddock_gait.cycle：ひづめの 道 → 足の 角度）。首・頭・しっぽの ゆれも 同じ"""
    import paddock_gait as G
    return [G.with_facing(q, 'right') for q in G.cycle(n or N)]


def walk_dy(m0, n=None):
    """コマごとの 上下の ずらし（2倍の 画素）：地面に ついて いる 手前の ひづめが いつも 地面の 線（GROUND）に くる。
       ひづめは 体から 見て Y_G − bob(g) の 高さ（paddock_gait）＝ ずらしは 体の ほんの 少しの 上下 だけ（とばない）。m0：カメラを 決めた ときの 目印（sheets.camera）"""
    import paddock_gait as G
    import horse3d as Hm
    n = n or N
    return [GROUND - float(m0['P1'](Hm.v3((XV, G.Y_G - G.bob(i / n)), ZN))[1]) for i in range(n)]


def walk_pose_old(g):
    """第4.165版までの 歩く 形（キーを つないだ 足）。いまは 使わない（walk_cycle）"""
    from horse_flat import TAILS
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - OFF[k])
    w = 2 * math.pi
    wave = math.sin(w * g)
    tufts = [((a[0], a[1] + .015 * wave * (i + 1) / 3), (b[0] + .02 * wave * (i + 1) / 3, b[1]), (c[0] + .05 * math.sin(w * g - .9) * (i + 1) / 3, c[1]), wm)
             for i, (a, b, c, wm) in enumerate(TAILS['sway'])]
    return dict(theta=round(0.6 * math.sin(w * 2 * g), 2), neck_rot=round(-6 + 2.4 * math.cos(w * 2 * (g - 0.1)), 2), head_ang=round(-55 + 1.6 * math.sin(w * 2 * g), 2),
                tail=[-118, -100], tail_kind='sway', tail_tufts=tufts,
                fore_near=leg('FL'), fore_far=leg('FR'), hind_near=leg('HL'), hind_far=leg('HR'))


def stance(g):
    return [k for k in HOOF_ORDER if ((g - OFF[k]) % 1.0) < ST]


_W0 = {}


def walk0():
    """歩く 1回りの はじめの 形（つなぎの コマの 出発点）"""
    if 'p' not in _W0:
        _W0['p'] = walk_cycle()[0]
    return _W0['p']


UP = dict(neck_rot=8.0, head_ang=-38.0)                          # 見上げきった 形（首を 上げて 鼻を 上へ）
DOWN = dict(neck_bend=-46.0, neck_len=1.08, head_ang=-80.0)      # のぞきこんだ 形（首を 下げて 下を 見る）
BASE = dict(neck_rot=-4.0, head_ang=-56.0, neck_bend=0.0, neck_len=1.0)   # 前を 見る 形（horse_flat の POSES['stand'] と 同じ・neck_bend／neck_len は なし＝0／1）


def _lerp(a, b, t):
    if isinstance(a, (list, tuple)):
        return type(a)(_lerp(x, y, t) for x, y in zip(a, b))
    return a + (b - a) * t


def stand_pose(kind):
    """止まった 形：front（前を 見る）・u1〜u8（見上げて いく：u8 が 見上げきった 形）・d1〜d8（のぞきこんで いく：d8 が のぞきこんだ 形）・
       t1〜t8（歩く 形〈1回りの はじめ＝walk_pose(0)〉から 前を 見る 形へ：足を そろえて 止まる。t1 が 歩く 形に 近い）"""
    from horse_flat import POSES, TAILS
    P = {k: (list(v) if isinstance(v, list) else v) for k, v in POSES['stand'].items()}
    P['tail_kind'] = 'hang'
    P['cannon_ext'] = dict(EXT0)                                 # 管の のび（前は 置き場の ext で 入れて いた：同じ 形）
    if kind == 'front':
        return P
    k = int(kind[1:])
    if kind[0] == 'u':
        t = ease(k / KU)
        P.update(neck_rot=round(_lerp(BASE['neck_rot'], UP['neck_rot'], t), 2), head_ang=round(_lerp(BASE['head_ang'], UP['head_ang'], t), 2))
    elif kind[0] == 'd':
        t = ease(k / KD)
        P.update(neck_bend=round(_lerp(0.0, DOWN['neck_bend'], t), 2), neck_len=round(_lerp(1.0, DOWN['neck_len'], t), 4), head_ang=round(_lerp(BASE['head_ang'], DOWN['head_ang'], t), 2))
    elif kind[0] == 't':
        t = ease(k / (KT + 1))                                   # 0＝歩く 形・1＝止まった 形
        Wk = walk0()
        for key in ('theta', 'neck_rot', 'head_ang'):
            P[key] = round(_lerp(Wk[key], P[key], t), 2)
        for key in ('fore_near', 'fore_far', 'hind_near', 'hind_far', 'tail'):
            P[key] = [round(v, 2) for v in _lerp(list(Wk[key]), list(P[key]), t)]
        P['cannon_ext'] = {k: round(_lerp(float(Wk.get('cannon_ext', {}).get(k, 0.0)), EXT0[k], t), 4) for k in EXT0}      # 管の のびも つなぐ
        P['tail_tufts'] = _lerp([tuple(q) for q in Wk['tail_tufts']], [tuple(q) for q in TAILS['hang']], t)      # しっぽの 房も ゆれた 形 → たれた 形へ
        P['tail_kind'] = 'sway' if t < 0.5 else 'hang'
    else:
        raise ValueError(kind)
    return P


STANDS = ('front',) + tuple(f'u{k}' for k in range(1, KU + 1)) + tuple(f'd{k}' for k in range(1, KD + 1)) + tuple(f't{k}' for k in range(1, KT + 1))


def walk_speed(frames, legs):
    """地面に ついて いる ひづめが すべらない 横の はやさ（2倍の 画素／コマ）"""
    n = len(frames)
    vals = []
    for i in range(n):
        j = (i + 1) % n
        for k in legs[i]:
            if k in legs[j]:
                vals.append(frames[i][2][HOOF_ORDER.index(k)][0] - frames[j][2][HOOF_ORDER.index(k)][0])
    return sum(vals) / len(vals) if vals else 0.0


def drop(theme, name):
    """blobs.json から 使わなく なった 絵の 名前を 消す（record と 同じ ロック）"""
    import fcntl
    import json
    p = os.path.join(PACK, 'blobs.json')
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        d = json.load(open(p, encoding='utf-8'))
        if name in d.get(theme, {}):
            del d[theme][name]
            tmp = p + '.tmp'
            json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
            os.replace(tmp, p)
        fcntl.flock(lk, fcntl.LOCK_UN)


def acc_i(i):
    return acc


# ---------------------------------------------------------------- 向きを かえる コマ（第4.215版）
#   まさちゃん 2026/11/24 01:22「海賊の馬が向きを変える時が、2Dで不自然だから向きを変える時も立体的に見えるように改良して」
#   前は 止まった 絵を 横に つぶして 裏がえす（scaleX 1 → 0.06 → −1：紙が 回る ように 見えた）。
#   → 馬を 立体の まま 回した コマ（カメラを 馬の まわりに 回して 描く：体の 奥行き・胸・4本の 足の 重なりが 見える）を 5コマ。向きを かえる 11コマ（1/30秒ごと）：
#       前を 見る 形 → r1…r5（こちらへ 回る）→ 〔ここで 左右を 入れかえる〕→ r5…r1（うら返し：むこうへ 回りきる）→ 前を 見る 形（うら返し）
#     角度は はじめと おわりが ゆっくり（smoothstep）：4.2°・15.5°・31.6°・50.1°・69.7° ｜ 110.3°・129.9°・148.4°・164.5°・175.8°（＝うら返した 69.7°…4.2°）。
#     まん正面（70°〜110°）は 1コマで 通りすぎる（この 馬の 絵は 横から 見た 形で 帽子・顔を 描く ので、まん正面の コマは 作らない）
#   回す 軸：画面の 左右を 入れかえる 線（meta の cx＝箱の まん中）に うつる たての 線（＝うら返しても 場所が ずれない）。ひづめは 地面の 線に（いちばん 手前の ひづめ）
#   シートは 止まった 形の シートとは 別（pirate.turn）：前の 絵（walk・stand）は かえない
TURN_N = 11                                                    # 向きを かえる コマの 数（1/30秒が いくつ：前を 見る 形から うら返した 前を 見る 形 まで）
TURN_ANG = [round(180 * (3 * (k / TURN_N) ** 2 - 2 * (k / TURN_N) ** 3), 1) for k in range(1, (TURN_N + 1) // 2)]      # r1〜r5 の 角度


def front_deco(rgb, a):
    """まん正面に 近い コマ（r5）：この 馬の 絵は 横から 見た 形で 帽子・頭絡を 描く ので、正面では 帽子が 消えて 線の かけらが のこる。
       → かけらを 消して、正面から 見た 三角帽（黒い つば・金の ふち・まるい 山・金の 蹄鉄・赤い 羽）と 赤い ほおの 帯・金の 輪・鼻の 帯を 描き足す（rgb・a＝0〜1 の コマ。同じ 形で 返す）"""
    import cv2
    from PIL import Image, ImageDraw
    from scipy import ndimage
    H_, W_ = a.shape; op = a > 0.5
    rows = np.nonzero(op.any(1))[0]; y0 = int(rows.min())
    yM = None
    for y in range(y0 + 4, y0 + 80):
        xs = np.nonzero(op[y])[0]
        if len(xs) and (xs.max() - xs.min() + 1) == len(xs) and len(xs) > 18:
            yM = y; break
    xs = np.nonzero(op[yM + 10])[0]; hx = (xs.min() + xs.max()) / 2
    xs = np.nonzero(op[yM + 20])[0]; u = (xs.max() - xs.min() + 1) / 2
    edge = lambda y: (lambda q: (float(q.min()), float(q.max())))(np.nonzero(op[int(round(y))])[0])
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    # 1. 線の かけらを 消す：頭〜足の つけねの 細い 暗い 線（まわりより 暗い 細い 所：体の かげの 面は のこる）。目は あとで 描き直す
    lum = img.mean(2).astype(np.float32); yb = int(rows.max() - 3.2 * u)                      # ひづめ（下）は さわらない
    med = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 21).astype(np.float32)
    thin = op & ((med - lum) > 10); thin[yb:] = False; thin[:yM - 2] = False
    inner = ndimage.binary_erosion(op, iterations=3)                                          # ふちの ぼかしは さわらない
    kill = ndimage.binary_dilation(thin & inner, iterations=2) & op
    if kill.any(): img = cv2.inpaint(img, kill.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
    # 2. 帽子と 帯（4倍で 描いて ちぢめる）
    SS = 4; x_off, y_off = int(hx - 4 * u), int(y0 - 3.2 * u); bw, bh = int(8 * u), int(12 * u)
    y_off = max(0, y_off); ov = Image.new('RGBA', (bw * SS, bh * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    P = lambda x, y: ((x - x_off) * SS, (y - y_off) * SS)
    poly = lambda pts, col: d.polygon([P(*q) for q in pts], fill=col)
    line = lambda pts, col, w: d.line([P(*q) for q in pts], fill=col, width=max(1, int(round(w * SS))), joint='curve')
    yc = yM + 0.1 * u; hw = 1.62 * u
    # ほおの 赤い 帯（頭の 両はしに そって：つばの 下 → 口の よこ）・鼻の 帯・金の 輪
    y1, y2 = yM + 0.5 * u, yM + 3.1 * u
    for sgn in (-1, 1):
        pts = []
        for y in np.linspace(y1, y2, 9):
            l_, r_ = edge(y); pts.append(((l_ + 0.13 * u) if sgn < 0 else (r_ - 0.13 * u), y))
        line(pts, '#C8322A', 0.17 * u)
        for y in np.linspace(y1 + 0.5 * u, y2 - 0.4 * u, 3):
            l_, r_ = edge(y); cx_ = (l_ + 0.13 * u) if sgn < 0 else (r_ - 0.13 * u); r0 = 0.035 * u
            d.ellipse([P(cx_ - r0, y - r0), P(cx_ + r0, y + r0)], fill='#FFF1D8')
        # 目（頭の はしの 近く・たてに 長い）
        ye = yM + 1.05 * u; l_, r_ = edge(ye); ex = (l_ + 0.42 * u) if sgn < 0 else (r_ - 0.42 * u)
        d.ellipse([P(ex - 0.10 * u, ye - 0.15 * u), P(ex + 0.10 * u, ye + 0.15 * u)], fill='#1A1414')
        d.ellipse([P(ex - 0.035 * u + sgn * 0.02 * u, ye - 0.10 * u), P(ex + 0.025 * u + sgn * 0.02 * u, ye - 0.04 * u)], fill='#FFFFFF')
    l_, r_ = edge(y2 - 0.25 * u); line([(l_ + 0.1 * u, y2 - 0.25 * u), (hx, y2 - 0.12 * u), (r_ - 0.1 * u, y2 - 0.25 * u)], '#2A1A12', 0.1 * u)
    for sgn in (-1, 1):
        l_, r_ = edge(y2); cx_ = (l_ + 0.15 * u) if sgn < 0 else (r_ - 0.15 * u); r0 = 0.17 * u
        d.ellipse([P(cx_ - r0, y2 - r0), P(cx_ + r0, y2 + r0)], outline=GOLD, width=max(1, int(0.07 * u * SS)))
    # 赤い 羽（山の うしろ・左上へ）
    poly([(hx - 0.22 * u, yc - 0.85 * u), (hx - 0.48 * u, yc - 1.5 * u), (hx - 0.8 * u, yc - 1.95 * u), (hx - 0.62 * u, yc - 1.35 * u), (hx - 0.5 * u, yc - 0.85 * u)], '#C8322A')
    line([(hx - 0.36 * u, yc - 0.9 * u), (hx - 0.55 * u, yc - 1.42 * u), (hx - 0.77 * u, yc - 1.9 * u)], '#7A1414', 0.04 * u)
    # 山（まるい）
    cr, ch_ = 0.80 * u, 1.02 * u
    d.pieslice([P(hx - cr, yc - 0.1 * u - ch_), P(hx + cr, yc - 0.1 * u + ch_)], 180, 360, fill=HAT)
    d.pieslice([P(hx - cr * 0.9, yc - 0.1 * u - ch_ * 0.9), P(hx - cr * 0.1, yc - 0.1 * u + ch_ * 0.9)], 180, 300, fill=(58, 50, 54, 140))
    # つば（両はしが 上へ 反る）
    xsb = np.linspace(-hw, hw, 41); rise = lambda x: 0.5 * u * (abs(x) / hw) ** 2.2; th = lambda x: 0.2 * u * (1 - (abs(x) / hw) ** 2) ** 0.6 + 0.5
    top = [(hx + x, yc - rise(x) - th(x)) for x in xsb]; bot = [(hx + x, yc - rise(x) + th(x)) for x in xsb]
    poly(top + bot[::-1], HAT_D)
    line([(q[0], q[1] + 0.03 * u) for q in top], GOLD, 0.09 * u)
    line([(q[0], q[1] + 0.17 * u) for q in top[4:-4]], '#3A3236', 0.045 * u)
    # 金の 蹄鉄（山の まん中）
    r0 = 0.23 * u; d.arc([P(hx - r0, yc - 0.56 * u - r0), P(hx + r0, yc - 0.56 * u + r0)], 15, 165, fill=GOLD, width=max(2, int(0.09 * u * SS)))
    ov = ov.resize((bw, bh), Image.LANCZOS); o = np.asarray(ov).astype(np.float32) / 255
    x1_, y1_ = min(W_, x_off + bw), min(H_, y_off + bh); o = o[:y1_ - y_off, :x1_ - x_off]
    oa = o[..., 3]; A0 = a[y_off:y1_, x_off:x1_]; C0 = img[y_off:y1_, x_off:x1_].astype(np.float32) / 255
    pre = o[..., :3] * oa[..., None] + C0 * (A0 * (1 - oa))[..., None]; An = oa + A0 * (1 - oa)
    out_rgb = img.astype(np.float32) / 255; out_a = a.copy()
    out_rgb[y_off:y1_, x_off:x1_] = np.where(An[..., None] > 1e-4, pre / np.maximum(An, 1e-4)[..., None], C0); out_a[y_off:y1_, x_off:x1_] = An
    return out_rgb.astype(rgb.dtype), out_a.astype(a.dtype)


def build_turn(out=None):
    import horse3d as Hm
    from sheets import camera, shadow_layer, _hexc, W2
    cam, m0 = camera(PAL, SPOT_W, '', 'pkpitref')
    e, t = np.asarray(cam[0], float), np.asarray(cam[1], float)
    # 回す 軸：地面の 上で、画面の x が 箱の まん中（2倍の 画素）に なる 点（馬の まん中の 面 z=0 の 上）
    P1 = m0['P1']; xa, xb = 0.0, 1.0
    pa, pb = float(P1(Hm.v3((xa, 0.0), 0.0))[0]), float(P1(Hm.v3((xb, 0.0), 0.0))[0])
    xc = xa + ((BOX[0] + BOX[2]) / 2 - pa) * (xb - xa) / (pb - pa)
    C = np.asarray(Hm.v3((xc, 0.0), 0.0), float)
    print('回す 軸（世界の x）', round(xc, 3), '画面の x', round(float(P1(Hm.v3((xc, 0.0), 0.0))[0]), 2), '角度', TURN_ANG, flush=True)
    pose = stand_pose('front'); frames = []
    cache = os.environ.get('TURN_CACHE')                                           # 描いた コマを のこす ファイル（.npz）：描き足し（front_deco）を 直す とき 3D から 描き直さない
    raw = dict(np.load(cache, allow_pickle=True)) if cache and os.path.exists(cache) else {}
    for k, th in enumerate(TURN_ANG):
        key = f'r{k}_{th}'
        if key + '_rgb' in raw:
            f0 = (raw[key + '_rgb'].astype(np.float32), raw[key + '_a'].astype(np.float32), [tuple(map(float, h)) for h in raw[key + '_h']])
        else:
            r = math.radians(th); c_, s_ = math.cos(r), math.sin(r)
            rot = lambda v: np.array([v[0] * c_ + v[2] * s_, v[1], -v[0] * s_ + v[2] * c_])
            ck = [list(C + rot(e - C)), list(C + rot(t - C))]
            fr, _ = render(PAL, SPOT_P, [pose], acc=acc_i, number='', tag=f'pkpit{k}', workers=1, cam=ck)
            f0 = fr[0]; raw[key + '_rgb'], raw[key + '_a'], raw[key + '_h'] = f0[0], f0[1], np.array(f0[2])
        if th > 70: f0 = front_deco(f0[0], f0[1]) + (f0[2],)                       # まん正面に 近い コマ：帽子と 帯を 描き足す
        frames.append(f0); print('  r%d' % (k + 1), th, '°', flush=True)
    if cache: np.savez_compressed(cache, **raw)
    # 上下：止まった 形（前を 見る）と 同じ ずらし ＝ 回す 軸の 足もとが 動かない（こちらへ 来る ひづめは 遠近で 少し 下に 見える：体は 上下しない）
    dy0 = json.load(open(os.path.join(PACK, 'blobs.json'), encoding='utf-8'))['pirate']['stand']['dy'][0]
    dys = [dy0] * len(frames)
    # 影：止まった 形と 同じ 色・濃さ。はばは 馬の 見える 長さに 合わせて せまく（まん中は 4本の ひづめの まん中）
    Hp, Wp = frames[0][1].shape[:2]; z = Wp / W2; sc = _hexc('#2A1A0E')

    def shadow(i, pre, A):
        xs = [h[0] for h in frames[i][2]]; cx = (min(xs) + max(xs)) / 2; rx = max((max(xs) - min(xs)) * 0.5 + 30 * abs(math.sin(math.radians(TURN_ANG[i]))), 34)
        sm = shadow_layer(Wp, Hp, cx * z, (GROUND + 2.5) * z, rx * z, 5.0 * z, blur=3.4 * z, alpha=0.26)
        return pre + sc[None, None, :] * (sm * (1 - A))[..., None], A + sm * (1 - A)
    u8, meta = make_sheet(frames, dys, extra=shadow)
    meta['dy'] = [round(float(d), 2) for d in dys]; meta['ang'] = TURN_ANG; meta['n'] = TURN_N
    if out:
        preview_png(u8, os.path.join(out, 'pirate_turn.png'), bg=(170, 120, 70))
    bid = save_webp(u8, quality=90)
    record('pirate', 'turn', bid, meta)
    print('turn', bid, meta, flush=True)
    return bid, meta


def build(out=None):
    import horse_flat as HF
    from sheets import camera
    import paddock_gait as G
    poses = walk_cycle(N) + [stand_pose(k) for k in STANDS]
    cam, m0 = camera(PAL, SPOT_W, '', 'pkpiwref')                # カメラは 前と 同じ 置き場（ext つき）で 決める
    frames, cam = render(PAL, SPOT_P, poses, acc=acc_i, number='', tag='pkpiw', workers=2, cam=cam)
    wf, sf = frames[:N], frames[N:]
    legs = [G.stance(i / N) for i in range(N)]
    dys = walk_dy(m0, N)
    near = ('FL', 'HL')                                          # 手前の 足（地面の 線は 手前の ひづめ）
    dev = [abs(wf[i][2][HOOF_ORDER.index(k)][1] + dys[i] - GROUND) for i in range(N) for k in near if k in legs[i]]
    print('地面に ついた 手前の ひづめの 上下の ずれ（2倍の 画素）：いちばん 大きい', round(max(dev), 3), '・平均', round(sum(dev) / len(dev), 3), flush=True)
    v = walk_speed(wf, [[k for k in lg if k in near] for lg in legs])
    slide = []
    for i in range(N):
        j = (i + 1) % N
        for k in near:
            if k in legs[i] and k in legs[j]:
                slide.append(abs((wf[i][2][HOOF_ORDER.index(k)][0] - wf[j][2][HOOF_ORDER.index(k)][0]) - v))
    print('地面に ついた 手前の ひづめの すべり（2倍の 画素／コマ・平均の はやさ', round(v, 3), 'との ちがい）：いちばん 大きい', round(max(slide), 3), flush=True)
    xs = [h[0] for fr in wf for h in fr[2]]
    sh = ('#2A1A0E', (min(xs) + max(xs)) / 2, GROUND + 2.5, (max(xs) - min(xs)) * 0.5, 5.0, 0.26)
    u8, meta = make_sheet(wf, dys, shadow=sh, cols=COLS)
    meta['dy'] = [round(float(d), 2) for d in dys]
    meta['cycle'] = CYCLE                                         # 1回りの 秒（ページの WALK_C と 同じ）
    meta['speed'] = round(abs(v) / 2 * N / CYCLE, 2)            # ページの px／秒（右向きに 進む）
    meta['cx'] = round((BOX[0] + BOX[2]) / 4, 2)                # 馬の まん中（ページの px）：左向きは ここを 中心に 反転
    sdy = [GROUND - max(h[1] for h in fr[2]) for fr in sf]      # 止まった 形：4本の ひづめが 地面に
    u8s, meta_s = make_sheet(sf, sdy, shadow=sh, cols=COLS_S)
    meta_s['dy'] = [round(float(d), 2) for d in sdy]
    meta_s['names'] = list(STANDS)
    meta_s['ku'], meta_s['kd'], meta_s['kt'] = KU, KD, KT
    if out:
        preview_png(u8, os.path.join(out, 'pirate_walk.png'), bg=(170, 120, 70))
        preview_png(u8s, os.path.join(out, 'pirate_stand.png'), bg=(170, 120, 70))
    bid = save_webp(u8, quality=90)
    record('pirate', 'walk', bid, meta)
    bids = save_webp(u8s, quality=90)
    record('pirate', 'stand', bids, meta_s)
    drop('pirate', 'captain')
    print('walk', bid, meta)
    print('stand', bids, meta_s)


if __name__ == '__main__':
    if '--turn' in sys.argv:          # 第4.215版：向きを かえる コマ だけ 作る（歩く コマ・止まった 形の シートは かえない）
        build_turn(os.environ.get('OUT'))
    else:
        build(os.environ.get('OUT'))
