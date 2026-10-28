"""パドックの 馬の 常歩（壁紙パック・第4.94版：まさちゃんの 指定「パドックの馬地面から脚が浮いたり地面についたりしてるから安定して同じ場所で歩かせて！あと脚の動きもう少しスムーズにして！」）
   1回り 24コマ。ひづめの 道すじを 先に 決めて、足の 角度を 逆に 解く（IK）：
   - 地面に ついて いる 間（1回りの 62%）：ひづめは 地面（体から 見て 一定の 高さ）に ついたまま、まっすぐ うしろへ 同じ はやさで 動く
     （＝ページで 体を 同じ はやさで 前へ 動かすと、ひづめは 地面に 止まって 見える）
   - 持ち上げて いる 間：なめらかな 山なりで 前へ（前足は ひざを まげて 高く・うしろ足は 飛節を まげて 少し）
   - 足の 形：前足は 地面に ついて いる 間 まっすぐ（前腕と 管が 一直線）・うしろ足は 飛節と ひざが いっしょに まがる。管は 少しだけ のび ちぢみ できる（cannon_ext）
   - 体は 1回りに 2回 ほんの 少し 上下（BOB）して、首と 頭が うなずく。地面の 高さは 体の 上下を さし引いて いつも 同じ
   pose_at(g) → horse_flat の POSES と 同じ 形の dict（4本の 足の 角度・cannon_ext・しっぽ）・bob(g)（体の 上がり m）"""
import math

import numpy as np
from scipy.optimize import least_squares

import horse3d as Hm
from horse_flat import TAILS, make_pose

N = 24             # 1回りの コマ
ST = 0.62          # 足が 地面に ついて いる 長さ（1回りの 割合）
OFF = dict(HL=0.00, FL=0.25, HR=0.50, FR=0.75)      # 左うしろ → 左前 → 右うしろ → 右前（手前＝L）
FORE = dict(front=0.62, back=0.18, lift=0.13)       # 前足の ひづめの 道（体の 中の x：前 → うしろ・持ち上げる 高さ m）
HIND = dict(front=-0.38, back=-0.82, lift=0.085)
Y_G = -0.030       # 地面（体の 中の 高さ m：体が 上下 しない とき）
BOB = 0.010        # 体の 上下（m・1回りに 2回）


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def bob(g):
    """体の 上がり（m）：前足・うしろ足が 地面に つく ころ 低く、そのあいだ 高い"""
    return BOB * math.cos(4 * math.pi * (g - 0.06))


def hoof_target(leg, g):
    """足 leg（FL・FR・HL・HR：手前＝L）の 位相 g の ひづめの 場所（体の 中の x, y）と 地面に ついて いるか・持ち上げの 進み u"""
    P = FORE if leg[0] == 'F' else HIND
    ph = (g - OFF[leg]) % 1.0
    yg = Y_G - bob(g)
    if ph < ST:
        q = ph / ST
        return P['front'] - (P['front'] - P['back']) * q, yg, True, 0.0, q
    u = (ph - ST) / (1 - ST)
    x = P['back'] + (P['front'] - P['back']) * ease(u)
    h = P['lift'] * math.sin(math.pi * min(1.0, u / 0.9)) ** 0.85
    return x, yg + h, False, u, 0.0


def _shape(leg, a0, a1, stance, u, q):
    """足の 4つの 角度（世界の 角度°）：a0（上腕／大腿）・a1（前腕／すね）から 管と つなぎを 決める"""
    if leg[0] == 'F':
        if stance:
            a2 = a1
            a3 = a2 + 24 + 10 * q
        else:
            f = math.sin(math.pi * u) ** 1.1
            a2 = a1 - 82 * f
            a3 = a2 + 34 - 30 * f
    else:
        if stance:
            a2 = a1 + 28
            a3 = a2 + 26 + 6 * q
        else:
            f = math.sin(math.pi * u) ** 1.1
            a2 = a1 + 28 + 40 * f
            a3 = a2 + 32 - 8 * f
    return [a0, a1, a2, a3]


def _hoof(leg, ang, theta, ext):
    """角度 → ひづめの 場所（horse3d.skeleton と 同じ 形）"""
    base = dict(theta=theta, neck_rot=-6.0, head_ang=-54.0, tail=[-118, -100],
                fore=dict(L=[-125, -90, -90, -60], R=[-125, -90, -90, -60]), hind=dict(L=[-62, -118, -92, -62], R=[-62, -118, -92, -62]))
    side = leg[1]
    if leg[0] == 'F':
        base['fore'] = dict(base['fore'], **{side: ang})
    else:
        base['hind'] = dict(base['hind'], **{side: ang})
    base['cannon_ext'] = {leg: ext}
    S = Hm.skeleton(base)
    return S[leg]['hf']


_PREV = {}
_BOUND = {}
FLEX_F = 64.0      # 前足の ひざの まがり（持ち上げの まん中）
FLEX_H = 30.0      # うしろ足の 飛節の まがり
SWING_F = 10.0     # 前足を 持ち上げる とき 上腕を 前へ ふる°
SWING_H = 6.0


def _stance_solve(leg, ph, theta, g):
    """地面に ついて いる 足：ひづめが ぴったり 地面の 道に くる 角度（a0・a1・管の のび）"""
    P = FORE if leg[0] == 'F' else HIND
    q = ph / ST
    tx, ty = P['front'] - (P['front'] - P['back']) * q, Y_G - bob(g)
    if leg[0] == 'F':
        x0 = _PREV.get((leg, 's'), [-112.0, -86.0, 0.0])
        lb, ub = [-160.0, -125.0, -0.04], [-70.0, -55.0, 0.07]
    else:
        x0 = _PREV.get((leg, 's'), [-60.0, -118.0, 0.0])
        lb, ub = [-100.0, -165.0, -0.04], [-10.0, -80.0, 0.07]
    x0 = [min(max(v, l + 1e-6), h - 1e-6) for v, l, h in zip(x0, lb, ub)]

    def res(v):
        hf = _hoof(leg, _shape(leg, v[0], v[1], True, 0.0, q), theta, v[2])
        return [(hf[0] - tx) * 10, (hf[1] - ty) * 10, v[2] * 2.0]
    r = least_squares(res, x0, bounds=(lb, ub), xtol=1e-12, ftol=1e-12)
    _PREV[(leg, 's')] = list(r.x)
    ang = _shape(leg, r.x[0], r.x[1], True, 0.0, q)
    hf = _hoof(leg, ang, theta, r.x[2])
    return ang, float(r.x[2]), (float(hf[0] - tx), float(hf[1] - ty))


def _boundary(leg):
    """地面を はなれる とき（位相 ST）と つく とき（位相 0）の 角度（持ち上げて いる 間は この 2つを つなぐ）"""
    if leg not in _BOUND:
        g_lo = (OFF[leg] + ST - 1e-9) % 1.0
        g_td = OFF[leg] % 1.0
        th = lambda g: 0.35 * math.sin(2 * math.pi * 2 * (g - 0.06))
        lo = _stance_solve(leg, ST - 1e-9, th(g_lo), g_lo)
        td = _stance_solve(leg, 0.0, th(g_td), g_td)
        _BOUND[leg] = (lo, td)
    return _BOUND[leg]


def solve_leg(leg, g, theta):
    ph = (g - OFF[leg]) % 1.0
    if ph < ST:
        ang, e, d = _stance_solve(leg, ph, theta, g)
        return [round(v, 3) for v in ang], round(e, 4), True, d
    u = (ph - ST) / (1 - ST)
    (lo, e_lo, _), (td, e_td, _) = _boundary(leg)
    k = ease(u)
    ang = [a + (b - a) * k for a, b in zip(lo, td)]
    f = math.sin(math.pi * u) ** 1.2
    if leg[0] == 'F':                                     # ひざを まげて 前へ：管を うしろへ・つなぎも まげる・上腕を 少し 前へ
        ang[0] += SWING_F * f
        ang[1] += SWING_F * 0.6 * f
        ang[2] -= FLEX_F * f
        ang[3] -= (FLEX_F + 18) * f
    else:                                                 # 飛節を まげて 前へ
        ang[0] += SWING_H * f
        ang[2] += FLEX_H * f
        ang[3] += (FLEX_H * 0.6) * f
    e = e_lo + (e_td - e_lo) * k
    hf = _hoof(leg, ang, theta, e)
    yg = Y_G - bob(g)
    return [round(v, 3) for v in ang], round(e, 4), False, (0.0, float(hf[1] - yg))


def pose_at(g, solve=True):
    """位相 g の 常歩の ポーズ（near＝手前の 足：L）"""
    w = 2 * math.pi
    theta = round(0.35 * math.sin(w * 2 * (g - 0.06)), 3)
    wave = math.sin(w * g)
    tufts = [((a[0], a[1] + .015 * wave * (i + 1) / 3), (b[0] + .02 * wave * (i + 1) / 3, b[1]), (c[0] + .05 * math.sin(w * g - .9) * (i + 1) / 3, c[1]), wm)
             for i, (a, b, c, wm) in enumerate(TAILS['sway'])]
    p = dict(theta=theta, neck_rot=round(-7 + 2.4 * math.cos(w * 2 * (g - 0.1)), 3), head_ang=round(-55 + 1.6 * math.sin(w * 2 * g), 3),
             tail=[-118, -100], tail_kind='sway', tail_tufts=tufts)
    ext, lift = {}, {}
    err = 0.0
    for leg, key in (('FL', 'fore_near'), ('FR', 'fore_far'), ('HL', 'hind_near'), ('HR', 'hind_far')):
        ang, e, st, d = solve_leg(leg, g, theta)
        p[key] = ang
        ext[leg] = e
        if st:
            err = max(err, abs(d[0]), abs(d[1]))
        else:
            lift[leg] = d[1]
    p['_ext'] = ext                     # 手前／おく の 名前（FL＝手前の 前足）。向きで L／R に なおして cannon_ext に（with_facing）
    p['_err'] = err                     # 地面に ついて いる ひづめの ずれ（m）
    p['_lift'] = lift                   # 持ち上げて いる ひづめの 地面からの 高さ（m）
    return p


def with_facing(p, facing):
    """pose_at の _ext（手前＝L の 名前）を 向きに 合わせた cannon_ext に（左向きは 手前が R）"""
    q = {k: v for k, v in p.items() if not k.startswith('_')}
    if facing == 'right':
        q['cannon_ext'] = dict(p['_ext'])
    else:
        sw = {'FL': 'FR', 'FR': 'FL', 'HL': 'HR', 'HR': 'HL'}
        q['cannon_ext'] = {sw[k]: v for k, v in p['_ext'].items()}
    return q


def stance(g):
    """地面に ついて いる 足（手前＝L の 名前）"""
    return [k for k in ('FL', 'FR', 'HL', 'HR') if ((g - OFF[k]) % 1.0) < ST]


def cycle(n=N):
    """1回り n コマの ポーズ（前の コマから 解く＝なめらか）。2回 まわして 1回り目の はじめも つなぐ"""
    _PREV.clear()
    _BOUND.clear()
    for i in range(n):
        pose_at(i / n)
    return [pose_at(i / n) for i in range(n)]


def check(n=N):
    ps = cycle(n)
    for i, p in enumerate(ps):
        print(i, round(p['_err'] * 1000, 2), 'mm', {k: round(v, 3) for k, v in p['_ext'].items()}, [round(x) for x in p['fore_near']], [round(x) for x in p['hind_near']],
              'lift', {k: round(v * 100, 1) for k, v in p['_lift'].items()})


if __name__ == '__main__':
    check()
