"""ノーマルど的中（第4.77版）：白い 馬の 走り（地面を しっかり 走る・ひづめが すべらない）。
   まさちゃん「走ってる演出が地面から滑ってるように見えるから、しっかり地面を走ってる演出にして！」「馬もっと小さくていい！」「馬もう一回り小さくていいよ！」
   - 世界（m）：地面は y＝0。光の 玉は (0, 1.2, 0)（地面から 1.2m 浮いて いる）。
   - はじめ（RUN0〜T_LAND）：玉の まん中から 小さな 馬が とびだし、大きく なりながら うずまきの 道に そって 地面へ とびおりる（後ろ足から 着地）。
   - そのあと（〜RUN1）：地面の うずまき（玉の 真下が まん中・画面で 右まわり・さいごは 上を 右へ）を ギャロップで 走る。
   - ギャロップ（右手前：左後 → 右後 → 左前 → 右前 → 宙）：ひづめが 地面に ついて いる あいだは、ひづめの 場所が 地面から 動かない
     （足の 角度を ひづめの 場所から 逆に 計算する＝IK）。体は 1歩で V（馬の 中の m）進む → 世界で S_H×V。
     足の 回る 速さは 進む 速さから 決める（空回りも すべりも しない）。宙の 足は 前の ギャロップの 形（かぎ）を 通って なめらかに。
   - カーブの 内がわ（玉の 方）へ かたむく（地面の ひづめの 線を 軸に：ひづめは 地面から はなれない）。
   normal_film.py（絵）と gen_sfx.py（ひづめの 音の 時刻）が 使う。numpy と horse3d の 骨の 計算だけ（絵は 描かない）。"""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
import horse3d as Hm
import normal_do as ND

F = ND.FILM
adir = Hm.adir
RUN0, RUN1 = F['RUN']

# ================================================================ 世界
O = np.array([0.0, 1.2, 0.0])                     # 光の 玉の まん中
S_H = 0.6                                         # 馬の 大きさ（本物の 0.6倍：まさちゃん「馬もっと小さくていい」「もう一回り小さく」）
R_MAX = 3.95                                      # うずまきの いちばん 外（m）
R_LAND = 1.4                                      # 玉から とびおりて 地面に 着く 半径（m）
LEAP = 0.38                                       # とびおりる 長さ（秒）
T_LAND = RUN0 + LEAP
LREF = np.array([0.10, 1.25, 0.0])                # 体の まん中（馬の 中の 座標）
GAL = dict(Hm.GALLOP)

# ================================================================ ギャロップ（馬の 中の 座標：前＋x・上＋y・左＋z・地面は だいたい y≈0）
# まさちゃんが 送ってくれた 動画（競走馬の ハイスピードカメラ）を 見本に：前足は 肩の ずっと 前に 着き、後ろ足は おなかの 下に 着いて
# しりの ずっと うしろまで けりだす（体が 長く のびる）・宙では 4本を おなかの 下に あつめる・宙の 前足は ひざを 深く まげる・
# 後ろ足は 飛節を まげて たたむ・1歩は だいたい 2.2回/秒（動画は 見本だけ：絵は なぞらない）
TD = dict(HL=0.00, HR=0.11, FL=0.31, FR=0.44)     # ひづめが 着く 位相（右手前の ギャロップ：右まわりの カーブ）
DUTY = 0.22                                       # ひづめが 着いて いる 長さ（1歩の うち：本物の ギャロップと 同じ くらい）
SWEEP = 1.25                                      # 着いて いる あいだに ひづめ（つま先）が 体の 下を うしろへ 動く 長さ（馬の 中の m）
V = SWEEP / DUTY                                  # 1歩で 体が 進む 長さ（馬の 中の m）
XC = dict(F=0.655, H=-0.505)                      # 着いて いる あいだの まん中での つま先の 前後（前足：肩の 前 1.28 → 0.03・後ろ足：おなかの 下 0.12 → しりの うしろ −1.13）
SOLE, TOE = 0.029, 0.065                          # ひづめの 底（hf から 下へ：sdfr で はかった）・つま先（hf から 前へ）
BREAK = 45.0                                      # けりだす とき かかとが 上がる（つま先を 軸に ひづめが まわる・度）
Y0, BOB, G_LOW = 0.13, 0.025, 0.38                # 地面の 高さ（馬の 中）＝ Y0 + BOB·cos(2π(g − G_LOW))：体は 着地の まん中で 低く・宙で 高い
PITCH_A, PITCH_G = 2.4, 0.10                      # 体の 前後の ゆれ（度）：後ろ足で ける とき 頭が 上・前足で 着く とき 下
ZLEG = dict(FL=0.155 * 0.9, FR=-0.155 * 0.9, HL=0.165 * 0.88, HR=-0.165 * 0.88)   # 足の 左右（horse3d と 同じ）
LEGS = ('HL', 'HR', 'FL', 'FR')

PIV = np.array([-0.60, 1.25])
LEN = dict(F=(0.30, 0.41, 0.28, 0.13), H=(0.43, 0.47, 0.29, 0.13))
FLAT = dict(F=-60.0, H=-62.0)                     # ひづめが 平らな ときの つなぎの 角度
HOOF = dict(F=(30.0, 0.085), H=(28.0, 0.09))
BEND = dict(F=-1, H=1)                            # 前足：ひじは うしろ・後ろ足：ひざは 前

# 宙の 足の かぎ（前の ギャロップ：sea_run・pixel_run と 同じ 形）：宙の あいだの 位置（0＝はなれる・1＝着く）と 角度
SWING_KEYS = dict(F=[(0.26, [-122, -22, -145, -172]), (0.60, [-66, -28, -38, -22]), (0.82, [-92, -50, -58, -40])],
                  H=[(0.22, [-116, -154, -128, -148]), (0.58, [-80, -150, -60, -30]), (0.84, [-58, -112, -70, -50])])


def _ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def theta(g):
    return GAL['theta'] + PITCH_A * math.cos(2 * math.pi * (g - PITCH_G))


def yground(g):
    return Y0 + BOB * math.cos(2 * math.pi * (g - G_LOW))


def _T(p, th):
    return Hm.rot2(np.asarray(p, float), PIV, th)


def root_of(f, th):
    return (_T((0.34, 1.52), th) + adir(th - 58) * 0.42) if f == 'F' else _T((-0.60, 1.25), th)


def ik2(root, tgt, L1, L2, bend):
    """2本の 骨の IK（のばしきる 少し 手前から やわらかく：ひざが ポンと はねない）"""
    d = np.asarray(tgt, float) - root
    D = float(math.hypot(*d))
    Lm = L1 + L2
    sft = 0.06 * Lm
    Ds = D if D <= Lm - sft else Lm - sft * math.exp(-(D - (Lm - sft)) / sft)
    Dc = min(max(Ds, abs(L1 - L2) + 1e-4), Lm - 1e-4)
    a = math.degrees(math.acos(max(-1.0, min(1.0, (L1 * L1 + Dc * Dc - L2 * L2) / (2 * L1 * Dc)))))
    a0 = _ang(d) + bend * a
    j = root + adir(a0) * L1
    a1 = _ang(root + d / max(D, 1e-9) * Dc - j)
    return a0, a1, max(0.0, D - Dc)


def toe_off(f, a3):
    """hf から つま先（ひづめの 底の 前の はし）へ"""
    ax = a3 - HOOF[f][0]
    return adir(ax + 90) * TOE + adir(ax) * SOLE


def lower(f, a2, a3):
    """ひざ（後ろ足は 飛節）から つま先までの ずれ"""
    L0, L1, L2, L3 = LEN[f]
    ho, hl = HOOF[f]
    return adir(a2) * L2 + adir(a3) * L3 + adir(a3 - ho) * hl + toe_off(f, a3)


def solve(leg, C, th, a2, a3):
    """つま先を C（馬の 中の x, y）に：下の 2本（a2・a3）は きめて、上の 2本を IK"""
    f = leg[0]
    L0, L1 = LEN[f][:2]
    kn = np.asarray(C, float) - lower(f, a2, a3)
    a0, a1, short = ik2(root_of(f, th), kn, L0, L1, BEND[f])
    return [a0, a1, a2, a3], short


def stance_angles(leg, C, th, tau=0.0):
    """つま先を C に 着いた 足の 角度・届かない 長さ（さいごの 半分で かかとが 上がる）"""
    f = leg[0]
    a2 = min(max(_ang(np.asarray(C, float) - root_of(f, th)), -128.0), -52.0)
    u = min(max((tau / DUTY - .5) / .5, 0.0), 1.0)
    return solve(leg, C, th, a2, FLAT[f] - BREAK * u * u * (3 - 2 * u))


def foot_fk(leg, ang, th):
    """足の 角度 → つま先（馬の 中の x, y）"""
    f = leg[0]
    L0, L1 = LEN[f][:2]
    kn = root_of(f, th) + adir(ang[0]) * L0 + adir(ang[1]) * L1
    return kn + lower(f, ang[2], ang[3])


def nominal_contact(leg, G, slope=0.0, tau=None):
    """着いて いる つま先（馬の 中・すべらない ための 予定の 場所）：tau＝着いてからの 位相"""
    f = leg[0]
    if tau is None:
        tau = (G - TD[leg]) % 1.0
    return np.array([XC[f] + V * (DUTY / 2 - tau), yground(G % 1.0) - slope * ZLEG[leg]])


def _unwrap(a, ref):
    return float(a + 360 * round((ref - a) / 360))


def _cr(ss_, vals, m0, m1, s):
    """Catmull-Rom（はしの 速さ m0・m1）"""
    n = len(ss_)
    ms = [m0] + [(vals[i + 1] - vals[i - 1]) / (ss_[i + 1] - ss_[i - 1]) for i in range(1, n - 1)] + [m1]
    for i in range(n - 1):
        if ss_[i] <= s <= ss_[i + 1]:
            h = ss_[i + 1] - ss_[i]
            u = (s - ss_[i]) / h
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
            return h00 * vals[i] + h10 * h * ms[i] + h01 * vals[i + 1] + h11 * h * ms[i + 1]
    return vals[-1]


def swing_angles(leg, s, G, slope, lo, td, dz=0.0):
    """宙の 足：はなれた 所（lo＝(ひづめの 底, 角度, 位相)）→ かぎの ひづめの 場所 → 着く 所（td）。
       ひづめの 道を なめらかに（地面より 下へは 行かない）・下の 2本の 角度も なめらかに → 上の 2本は IK"""
    f = leg[0]
    (C0, A0, G0), (C1, A1, G1) = lo, td
    th = theta(G % 1.0)
    keys = SWING_KEYS[f]
    sk = [0.0] + [k[0] for k in keys] + [1.0]
    Ck = [np.asarray(C0, float)] + [foot_fk(leg, a, theta((G0 + (G1 - G0) * sk_) % 1.0)) for sk_, a in keys] + [np.asarray(C1, float)]   # はしは 着いて いた ときの IK の 目あて（つながる）
    sw = (1 - DUTY)
    mx0, mx1 = -V * sw * .55, -V * sw * .65
    x = _cr(sk, [c[0] for c in Ck], mx0, mx1, s)
    y = _cr(sk, [c[1] for c in Ck], 0.9, -1.1, s)
    gy = yground(G % 1.0) - slope * (ZLEG[leg] + dz)                           # 地面（いまの 横の ずれの 所）
    y = max(y, gy + 0.03 * math.sin(math.pi * s) ** .5)
    a2s = [A0[2]] + [_unwrap(k[1][2], A0[2]) for k in keys] + [_unwrap(A1[2], A0[2])]
    a3s = [A0[3]] + [_unwrap(k[1][3], A0[3]) for k in keys] + [_unwrap(A1[3], A0[3])]
    a2 = _cr(sk, a2s, 0.0, 0.0, s)
    a3 = _cr(sk, a3s, 0.0, 0.0, s)
    return solve(leg, (x, y), th, a2, a3)[0]


def pose_base(g):
    w = 2 * math.pi
    return dict(theta=theta(g), neck_rot=GAL['neck_rot'] + 8 * math.cos(w * (g - 0.95)),
                head_ang=GAL['head_ang'] + 5 * math.sin(w * (g - .2)), tail=GAL['tail'], fore={}, hind={}, leg_dz={})


def hoof_local(S, leg, dz=0.0):
    """骨（skeleton）の つま先（馬の 中の 3D）"""
    p = S[leg]['hf'] + toe_off(leg[0], S[leg]['ang'][3])
    return np.array([p[0], p[1], ZLEG[leg] + dz])


# ================================================================ 道（地面の うずまき）
def spiral(u):
    """うずまき（地面）の 点 xz：u＝0 玉の 真下 → 1 外（上を 右へ）"""
    phi = -math.pi / 2 - 2 * math.pi * F['TURNS'] * (1 - u)
    r = R_MAX * (.03 + .97 * u)
    return np.array([r * math.cos(phi), r * math.sin(phi)])


U_LAND = (R_LAND / R_MAX - .03) / .97
_US = np.linspace(U_LAND, 1.0, 4001)
_PTS = np.array([spiral(u) for u in _US])
_ARC = np.concatenate([[0.0], np.cumsum(np.hypot(*(np.diff(_PTS, axis=0).T)))])
L_RUN = float(_ARC[-1])
T_RUN = RUN1 - T_LAND
V_RATIO = 1.3                                     # 走りの はじめ → おわりの 速さ（だんだん 速く）
V0 = 2 * L_RUN / ((1 + V_RATIO) * T_RUN)
V1 = V0 * V_RATIO


def arc_at(t):
    """着地からの 道の 長さ（m）"""
    tau = t - T_LAND
    if tau <= T_RUN:
        return V0 * tau + (V1 - V0) * tau * tau / (2 * T_RUN)
    return L_RUN + V1 * (tau - T_RUN)


def speed_at(t):
    tau = min(max(t - T_LAND, 0.0), T_RUN)
    return V0 + (V1 - V0) * tau / T_RUN


def path_xz(a):
    """道の 長さ a の 点と 向き（xz）。さいごより 先は まっすぐ"""
    if a <= L_RUN:
        i = int(np.searchsorted(_ARC, a))
        i = min(max(i, 1), len(_ARC) - 1)
        w = (a - _ARC[i - 1]) / max(_ARC[i] - _ARC[i - 1], 1e-12)
        p = _PTS[i - 1] * (1 - w) + _PTS[i] * w
        d = _PTS[i] - _PTS[i - 1]
        return p, d / (np.linalg.norm(d) + 1e-12)
    d = _PTS[-1] - _PTS[-2]
    d = d / np.linalg.norm(d)
    return _PTS[-1] + d * (a - L_RUN), d


def phase_at(t):
    """ギャロップの 位相（のばした まま：着地＝1.0）。とびおりる あいだは 0.68 → 1.0（宙の 形）"""
    if t < T_LAND:
        x = max(t - RUN0, 0.0) / LEAP
        return 0.68 + 0.32 * x
    return 1.0 + arc_at(t) / (S_H * V)


def scale_at(t):
    x = min(max((t - RUN0) / LEAP, 0.0), 1.0)
    return S_H * (0.1 + 0.9 * (1 - (1 - min(x / 0.85, 1.0)) ** 2))


LEAN_K = math.tan(math.radians(13.0)) * R_LAND / (V0 * V0)    # かたむき：tan ρ ＝ K·v²/r（着地の あたりで 13°）


def lean_at(t, r):
    k = min(max((t - T_LAND) / .3, 0.0), 1.0)
    k = k * k * (3 - 2 * k)
    v = speed_at(t)
    return math.degrees(math.atan(LEAN_K * v * v / max(r, .6))) * k


def frame_at(t):
    """馬の いまの 場所・向き：B（体の まん中・世界）・Rm（馬 → 世界：列＝前・上・左）・s・位相 g・地面の かたむき slope（馬の 中）・道の 進み"""
    s = scale_at(t)
    up = np.array([0.0, 1.0, 0.0])
    if t < T_LAND:
        x = max(t - RUN0, 0.0) / LEAP
        # 道の 進み：玉の まん中 → 着地の 点（着地の 速さ ≒ 走りの はじめの 速さ）
        ue = x * x * (3 - 2 * x) * .35 + x * .65
        u = U_LAND * ue
        pxz = spiral(u)
        d = spiral(min(u + 1e-3, 1.0)) - spiral(max(u - 1e-3, 0.0))
        hxz = d / (np.linalg.norm(d) + 1e-12)
        g = phase_at(t)
        y_land = S_H * (LREF[1] - yground(1.0))
        y = O[1] + (y_land - O[1]) * x ** 1.7 + 0.10 * math.sin(math.pi * x) * (1 - x)
        h = np.array([hxz[0], 0.0, hxz[1]])
        Rm = np.stack([h, up, np.cross(h, up)], 1)
        return dict(B=np.array([pxz[0], y, pxz[1]]), Rm=Rm, s=s, g=g, slope=0.0, a=-1.0, lean=0.0, P=np.array([pxz[0], 0.0, pxz[1]]))
    a = arc_at(t)
    pxz, hxz = path_xz(a)
    g = phase_at(t)
    h = np.array([hxz[0], 0.0, hxz[1]])
    r = float(np.hypot(*pxz))
    lean = lean_at(t, r)
    inward = -np.array([pxz[0], 0.0, pxz[1]]) / max(r, 1e-6)
    inward = inward - h * float(inward @ h)
    inward = inward / (np.linalg.norm(inward) + 1e-12)
    lr = math.radians(lean)
    upl = up * math.cos(lr) + inward * math.sin(lr)
    Rm = np.stack([h, upl, np.cross(h, upl)], 1)
    nl = Rm.T @ up                                    # 地面の 向き（馬の 中）
    slope = float(nl[2] / nl[1])                      # 地面：y ＝ yg − slope·z
    gl = g % 1.0
    piv = np.array([LREF[0], yground(gl), 0.0])
    P = np.array([pxz[0], 0.0, pxz[1]])
    B = P + s * (Rm @ (LREF - piv))
    return dict(B=B, Rm=Rm, s=s, g=g, slope=slope, a=a, lean=lean, P=P)


def to_world(fr, q):
    return fr['B'] + fr['s'] * (fr['Rm'] @ (np.asarray(q, float) - LREF))


def to_local(fr, w):
    return LREF + fr['Rm'].T @ (np.asarray(w, float) - fr['B']) / fr['s']


def _t_of_phase(G):
    if G <= 1.0:
        return T_LAND
    lo, hi = T_LAND, RUN1 + 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if phase_at(mid) < G:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


_PLANT = {}


def planted(leg, Gtd):
    """着いた（位相 Gtd）ひづめの 世界の 場所（着地より 前は なし）"""
    if Gtd < 1.0 - 1e-9:
        return None
    key = (leg, round(Gtd, 6))
    if key not in _PLANT:
        t = _t_of_phase(Gtd)
        fr = frame_at(t)
        C = nominal_contact(leg, Gtd, fr['slope'], 0.0)
        _PLANT[key] = to_world(fr, [C[0], C[1], ZLEG[leg]])
    return _PLANT[key]


def stance_at(leg, G, fr):
    """着いて いる 足：ひづめの 底の 場所（馬の 中）・横の ずれ dz・角度"""
    tau = (G - TD[leg]) % 1.0
    W_ = planted(leg, G - tau)
    if W_ is None:
        C = nominal_contact(leg, G, fr['slope'], tau)
        dz = 0.0
    else:
        q = to_local(fr, W_)
        C, dz = q[:2], float(q[2] - ZLEG[leg])
    a, short = stance_angles(leg, C, theta(G % 1.0), tau)
    return C, dz, a


def leg_state(leg, G, fr):
    """位相 G（のばした まま）・いまの 場所 fr の 足：角度・横の ずれ・着いて いるか"""
    tau = (G - TD[leg]) % 1.0
    if tau < DUTY:
        C, dz, a = stance_at(leg, G, fr)
        return a, dz, True
    s = (tau - DUTY) / (1 - DUTY)
    G0 = G - (tau - DUTY)                     # はなれた 位相
    G1 = G + (1 - tau)                        # 次に 着く 位相
    if G0 >= 1.0:
        fr0 = frame_at(_t_of_phase(G0))
        C0, dz0, A0 = stance_at(leg, G0 - 1e-7, fr0)
    else:
        C0 = nominal_contact(leg, G0, 0.0, DUTY); dz0 = 0.0
        A0 = stance_angles(leg, C0, theta(G0 % 1.0), DUTY)[0]
    C1 = nominal_contact(leg, G1, fr['slope'], 0.0)
    A1 = stance_angles(leg, C1, theta(G1 % 1.0), 0.0)[0]
    k = min(s / .6, 1.0)
    dz = dz0 * (1 - k * k * (3 - 2 * k))
    a = swing_angles(leg, s, G, fr['slope'], (C0, A0, G0), (C1, A1, G1), dz)
    return a, dz, False


def state(t):
    """絵の ための すべて：frame_at ＋ 形（pose）・骨（S）・着いて いる 足・横の ずれ"""
    fr = frame_at(t)
    G = fr['g']
    pose = pose_base(G % 1.0)
    down = {}
    for leg in LEGS:
        a, dz, on = leg_state(leg, G, fr)
        (pose['fore'] if leg[0] == 'F' else pose['hind'])[leg[1]] = a
        if abs(dz) > 1e-6:
            pose['leg_dz'][leg] = dz
        down[leg] = on
    if not pose['leg_dz']:
        del pose['leg_dz']
    fr['pose'], fr['down'] = pose, down
    fr['S'] = Hm.skeleton(pose)
    return fr


# ================================================================ ひづめの 音・あと・土の ための 時刻（着く・はなれる）
def events(t_end=None):
    """[(時刻, 足, 'td'／'lo', 世界の ひづめの 点)]：着地（1.0）から t_end まで"""
    t_end = t_end if t_end is not None else F['BURST'] + .1
    out = []
    G_end = phase_at(t_end)
    for leg in LEGS:
        n = 1
        while n + TD[leg] <= G_end:
            Gt = n + TD[leg]
            W_ = planted(leg, Gt)
            out.append((_t_of_phase(Gt), leg, 'td', W_))
            if Gt + DUTY <= G_end:
                out.append((_t_of_phase(Gt + DUTY), leg, 'lo', W_))
            n += 1
    out.sort(key=lambda e: e[0])
    return out


def steps():
    """ひづめの 音の 時刻（着く とき）・足・画面の 左右（−1〜1）"""
    return [(t, leg, float(p[0] / R_MAX)) for t, leg, kind, p in events() if kind == 'td']


# ================================================================ 馬と 騎手の 形（3D：馬の 中の 座標）
# まさちゃん「馬の形もジョッキー乗せた状態で、この動画の馬を参考に作成して！」：競走馬（鹿毛：赤みの 茶・足先と たてがみ・しっぽは 黒）＋
# 前かがみの 騎手（勝負服・ヘルメット・白い ズボン・黒い ブーツ）＋ 鞍・ゼッケン。形と 色は 一から（勝負服の 色も オリジナル：金と 白）
M_COAT, M_EYE, M_HOOF = 1, 5, 6
M_SILK, M_PANTS, M_HELMET, M_BOOT, M_CLOTH, M_SLEEVE, M_SADDLE, M_GOGGLE = 7, 8, 9, 10, 11, 12, 13, 14
JOCKEY_MATS = (M_SILK, M_PANTS, M_HELMET, M_BOOT, M_SLEEVE, M_GOGGLE)
JS = 0.95                                          # 騎手の 大きさ（馬に 対して：動画の 騎手のように 小がらで 低く）


def jockey(sc, S, pose, g):
    """前かがみの 騎手（右向きの 馬の 上・き甲を 目安）。上体は 馬の 上下を ひざで 吸収して あまり 動かない。手は たてがみの 上（首と いっしょに 動く）"""
    w = np.asarray(S['withers'], float)
    dy = 0.65 * (yground(g) - Y0)                    # 体が 下がる とき（馬の 中の 地面が 上がる）上体は 少し 上へ もどす
    def P(y, x, z=0.0, k=1.0):
        return np.array([w[0] + x * JS, w[1] + y * JS + dy * k, z * JS], float)
    J = {}
    J['pelvis'], J['chest'], J['neck'], J['head'] = P(0.25, -0.30), P(0.34, 0.07), P(0.38, 0.16), P(0.46, 0.25)
    a, b = J['pelvis'], J['chest']
    sc.ell_ax((a + b) / 2, b - a, (np.linalg.norm(b - a) / 2 + 0.07 * JS, 0.12 * JS, 0.15 * JS), up=(0, 1, 0), k=0.04, mat=M_SILK)
    sc.ell(a + np.array([0.02, -0.02, 0]) * JS, (0.13 * JS, 0.10 * JS, 0.15 * JS), k=0.05, mat=M_PANTS)
    sc.rcone(J['chest'], J['neck'], 0.07 * JS, 0.05 * JS, k=0.03, mat=M_SILK)
    sc.sph(J['head'], 0.095 * JS, k=0.02, mat=M_HELMET)
    sc.ell(J['head'] + np.array([0.085, -0.03, 0]) * JS, (0.05 * JS, 0.012 * JS, 0.07 * JS), k=0.01, mat=M_HELMET)          # ひさし
    sc.ell(J['head'] + np.array([0.07, -0.055, 0]) * JS, (0.035 * JS, 0.02 * JS, 0.075 * JS), k=0.01, mat=M_GOGGLE)       # ゴーグル
    crest = np.asarray(S['crest'], float)
    hp = Hm.bez(crest, 0.32) + np.array([0.02, -0.035])                              # 手：たてがみの 上（首と いっしょに）
    for z in (1, -1):
        sh = P(0.35, 0.05, 0.13 * z)
        hd = np.array([hp[0], hp[1], 0.085 * z * JS])
        el = (sh + hd) / 2 + np.array([-0.02, 0.07, 0.07 * z]) * JS
        sc.rcone(sh, el, 0.05 * JS, 0.042 * JS, k=0.02, mat=M_SLEEVE)
        sc.rcone(el, hd, 0.04 * JS, 0.032 * JS, k=0.02, mat=M_SLEEVE)
        sc.sph(hd, 0.035 * JS, k=0.01, mat=M_PANTS)
        hip = P(0.22, -0.26, 0.12 * z)
        kn = P(0.14, 0.02, 0.30 * z, k=0.5)
        an = P(-0.18, -0.18, 0.36 * z, k=0.0)                                           # あぶみ（馬と いっしょに 動く）
        toe = P(-0.22, -0.06, 0.37 * z, k=0.0)
        sc.rcone(hip, kn, 0.075 * JS, 0.055 * JS, k=0.03, mat=M_PANTS)
        sc.rcone(kn, an, 0.052 * JS, 0.04 * JS, k=0.02, mat=M_BOOT)
        sc.rcone(an, toe, 0.04 * JS, 0.03 * JS, k=0.01, mat=M_BOOT)
        J[f'hand{z}'], J[f'sh{z}'], J[f'el{z}'], J[f'hip{z}'], J[f'kn{z}'], J[f'an{z}'] = hd, sh, el, hip, kn, an
    return J


def tack(sc, S):
    """鞍・ゼッケン（白）・腹帯"""
    w = np.asarray(S['withers'], float)
    th = math.radians(S.get('theta', 0.0)) if isinstance(S, dict) else 0.0
    for z in (1, -1):
        sc.rbox(np.array([w[0] - 0.30, w[1] - 0.40, 0.295 * z]), (0.20, 0.14, 0.018), 0.03, k=0.02, mat=M_CLOTH)
    sc.ell(np.array([w[0] - 0.30, w[1] + 0.02, 0.0]), (0.20, 0.05, 0.19), k=0.03, mat=M_SADDLE)          # 鞍
    gb = np.array([w[0] - 0.12, w[1] - 0.05])
    gt = np.array([w[0] - 0.06, w[1] - 0.66])
    for z in (1, -1):
        sc.rcone(np.array([gb[0], gb[1], 0.25 * z]), np.array([gt[0], gt[1], 0.20 * z]), 0.03, 0.03, k=0.02, mat=M_SADDLE)   # 腹帯


def build_racer(sc, st):
    """馬（horse3d）＋ 騎手 ＋ 鞍。st＝state(t)。戻り値 (S, J)"""
    Hm.HEAD_SCALE = 1.04
    S = Hm.build(sc, st['pose'], mats=dict(body=M_COAT, neck=M_COAT, hoof=M_HOOF, eye=M_EYE, head=M_COAT))
    J = jockey(sc, S, st['pose'], st['g'] % 1.0)
    tack(sc, S)
    return S, J


def capsules(st, S=None, J=None):
    """地面の 影の ための 形（世界の 線分と 半径のリスト）：胴・首・頭・足・騎手"""
    S = S if S is not None else st['S']
    pose = st['pose']
    dzs = pose.get('leg_dz', {})
    th = pose['theta']
    s = st['s']
    T = lambda p: Hm.rot2(np.asarray(p, float), PIV, th)
    out = []
    def C(a, za, b, zb, r):
        out.append((to_world(st, [a[0], a[1], za]), to_world(st, [b[0], b[1], zb]), r * s))
    C(T((-0.45, 1.24)), 0, T((0.42, 1.20)), 0, 0.30)
    C(T((-0.80, 1.30)), 0, T((-0.40, 1.40)), 0, 0.26)
    C(T((0.40, 1.10)), 0, T((0.55, 1.28)), 0, 0.24)
    cr, tr = np.asarray(S['crest'], float), np.asarray(S['throat'], float)
    nb, nm = (cr[0] + tr[0]) / 2, (cr[2] + tr[2]) / 2
    C(nb, 0, nm, 0, 0.17)
    C(nm, 0, S['poll'], 0, 0.11)
    C(S['poll'], 0, Hm.head_pt(S, 0.56, -0.03)[:2], 0, 0.085)
    ta = S.get('tail_pts')
    if ta:
        C(ta[0], 0, np.asarray(ta[0]) + np.array([-0.55, -0.12]), 0, 0.07)              # しっぽ（毛の かたまり）
    for leg in ('FL', 'FR'):
        L_ = S[leg]; z = L_['z']; dz = dzs.get(leg, 0.0)
        zl, zf = 0.155 * z, 0.1395 * z
        C(L_['ps'], zl, L_['el'], zl, 0.085)
        C(L_['el'], zl, L_['kn'], zf + dz * .45, 0.055)
        C(L_['kn'], zf + dz * .45, L_['ft'], zf + dz * .76, 0.04)
        C(L_['ft'], zf + dz * .76, L_['hf'], zf + dz, 0.045)
    for leg in ('HL', 'HR'):
        L_ = S[leg]; z = L_['z']; dz = dzs.get(leg, 0.0)
        zl = 0.165 * z
        C(L_['hj'], 0.17 * z, L_['st'], zl, 0.12)
        C(L_['st'], zl, L_['hk'], zl * .92 + dz * .48, 0.065)
        C(L_['hk'], zl * .92 + dz * .48, L_['ft'], zl * .88 + dz * .78, 0.04)
        C(L_['ft'], zl * .88 + dz * .78, L_['hf'], zl * .88 + dz, 0.045)
    if J is not None:
        def CJ(a, b, r):
            out.append((to_world(st, a), to_world(st, b), r * s))
        CJ(J['pelvis'], J['chest'], 0.14)
        CJ(J['chest'], J['head'], 0.09)
        for z in (1, -1):
            CJ(J[f'hip{z}'], J[f'kn{z}'], 0.07)
            CJ(J[f'kn{z}'], J[f'an{z}'], 0.05)
            CJ(J[f'sh{z}'], J[f'hand{z}'], 0.045)
    return out
