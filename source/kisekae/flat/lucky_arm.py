"""開運の招き馬の あげた右前足を 立体の形で描く（壁紙の lucky_wall.py：招く時に ひじから 前へ たおれて、ひづめが おれる）
   - 前足は 体から ひじを まがって 上へのびる 太さの変わる管（中心の線 ARM_C・半径 ARM_R＝いまの絵の 線のまん中まで）。
     ひじ（P_Q）を中心に 前へ たおれる（φ）。まがる所（BEND）は だんだん たおれる。少し 内がわへ まわる（ρ）
   - ひづめは 厚みのある だ円の板（いまの絵の ひづめと 桃色の裏に 合わせた だ円）：表＝金のふちと 桃色の裏・ふち（厚み）＝金の かべ・
     裏＝金の かべと 白い毛のふち。手首（管の先）を中心に さらに 前へ おれる（ψ）。θ＝φ＋ψ（ひづめ全体の おれ）
   - 少しだけ 遠近（近づくと 大きく：PERSP）。前足は 小さな面に分けて 遠い順に ぬり（画家の方法）、光（LIGHT）の 当たらない面を かげに
   - 前足の形と かげは 8倍の ラスターで ぬってから ふちを たどって 線に（cv2）。線は いまの絵と同じ（線を先に太く → 白を上に・体との つなぎ目は 線なし）
   frame_svg(θ, n) → 招き馬の座標（viewBox 0 0 240 270）の SVG（右前足とひづめ）。n：id のうしろにつける字
   python3 flat/lucky_arm.py <出力フォルダ>   → 確かめ用（θ ごとの絵）"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lucky_maneki import OUT, LW, LW2, SHADE, GOLD, GOLD_SH, GOLD_HI, RED, BY

# 前足の中心の線（いまの絵の座標 G0：translate(0 BY) の中）と 半径（線のまん中まで）。体の中 → ひじ → 手首
ARM_C = [(82, 182), (75, 182.2), (68, 182), (60, 180.5), (53, 177), (47.5, 171.5), (44.5, 164), (43.2, 155), (42.8, 146)]
ARM_R = [6.6, 8.2, 9.8, 11.3, 12.3, 12.8, 13.0, 13.0, 12.8]
N_SEC = 56                       # 管の 輪切りの数
N_AROUND = 44                    # 輪切りの まわりの点の数
BEND = (0.32, 0.62)              # まがる所（管の長さの わりあい：ここで だんだん たおれる）
P_Q = (49.0, 176.0 + BY)         # ひじ（前へ たおれる 中心）
PERSP = 480.0                    # 遠近（近づくと 大きく）：カメラまでの きょり
P_CAM = (120.0, 140.0)           # 遠近の まん中
LIGHT = np.array([0.55, -0.45, 0.70]) / np.linalg.norm([0.55, -0.45, 0.70])   # 光（右上の前から）
DARK = 0.28                      # これより 光が当たらない面は かげ
SC = 8                           # ラスターの 倍率
BOX = (-20.0, 70.0, 120.0, 260.0)    # ラスターにする所（x0, y0, x1, y1・招き馬の座標）
EPS = 1.8                        # ふちを 線にする時の まとめ（ラスターの 点）
DOT_AT = (44.0, 174.0 + BY)      # 赤い玉（いまの絵の 前足の かざり）
JUNC_X = 79.0                    # これより右（体との つなぎ目）は 前足の線を描かない
# ひづめ（招き馬の座標）：いまの絵の ひづめ・桃色の裏（だ円に合わせた）・つや
HOOF_C = (43.22, 133.17 + BY)
HOOF_AB = (20.62, 18.24)
HOOF_ROT = -2.34
SOLE_C = (42.93, 132.52 + BY)
SOLE_AB = (13.54, 11.68)
SOLE_ROT = -3.57
HOOF_Z = 6.0                     # ひづめの まん中の 前後（管の じくより 前）
HOOF_D = 8.0                     # ひづめの 厚み
SHINE = [(33, 137), (37, 133.2), (45, 132.2), (50, 134)]          # つや（G0 の 'M33 123 C37 119 45 118 50 120' ＋ BY）
RIM = '#E0A436'                  # ひづめの ふち（厚み）


def f1(v):
    s = f'{v:.1f}'
    if s.endswith('.0'):
        s = s[:-2]
    return '0' if s in ('-0', '') else s


def q1(v):
    """0.1 に まるめた数の 短い字（0.5 → .5・-0.5 → -.5）"""
    s = f'{round(v * 10) / 10:.1f}'
    if s.endswith('.0'):
        s = s[:-2]
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '') else s


def join_nums(nums):
    """数を つなぐ（- や 2つめの . の前は あけない）"""
    out = ''
    for t in nums:
        if out and not (t.startswith('-') or (t.startswith('.') and '.' in out.split(' ')[-1].split('-')[-1] and not out[-1].isalpha())):
            if not out[-1].isalpha():
                out += ' '
        out += t
    return out


def enc_poly(P2, close=True):
    """折れ線の道（はじめは M・あとは まるめた点どうしの ずれ l で短く）"""
    R = [(round(x * 10), round(y * 10)) for x, y in P2]
    d = 'M' + join_nums([q1(R[0][0] / 10), q1(R[0][1] / 10)])
    nums = []
    for (x0, y0), (x1, y1) in zip(R, R[1:]):
        if (x0, y0) == (x1, y1):
            continue
        nums += [q1((x1 - x0) / 10), q1((y1 - y0) / 10)]
    if nums:
        d += 'l' + join_nums(nums)
    return d + ('z' if close else '')


def enc_bez(Q):
    """3次ベジエの 道（Q：はじめの点 ＋ 3点ずつ。まるめた点どうしの ずれ c で）"""
    R = [(round(x * 10), round(y * 10)) for x, y in Q]
    d = 'M' + join_nums([q1(R[0][0] / 10), q1(R[0][1] / 10)]) + 'c'
    nums = []
    for i in range(0, len(R) - 1, 3):
        x0, y0 = R[i]
        for x, y in R[i + 1:i + 4]:
            nums += [q1((x - x0) / 10), q1((y - y0) / 10)]
    return d + join_nums(nums) + 'z'


def catmull(pts, n):
    """点の列を なめらかにつないで 長さで等分した n 点に（Catmull-Rom）。→ (点, 長さの わりあい)"""
    P = np.array(pts, float)
    dense = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for k in range(24):
            u = k / 24
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    dense.append(P[-1])
    D = np.array(dense)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(D, axis=0), axis=1))]
    s = np.linspace(0, seg[-1], n)
    return np.stack([np.interp(s, seg, D[:, 0]), np.interp(s, seg, D[:, 1])], 1), s / seg[-1]


CEN2, SPAR = catmull([(x, y + BY) for x, y in ARM_C], N_SEC)
CEN = np.c_[CEN2, np.zeros(N_SEC)]
RAD = np.interp(SPAR, np.linspace(0, 1, len(ARM_R)), ARM_R) - LW / 2      # ぬる半径（線のまん中から 半分 内がわ）
_tg = np.gradient(CEN2, axis=0)
_tg /= np.linalg.norm(_tg, axis=1, keepdims=True)
TAN = np.c_[_tg, np.zeros(N_SEC)]
NRM1 = np.c_[-_tg[:, 1], _tg[:, 0], np.zeros(N_SEC)]                    # 輪切りの 画面の中の 向き
NRM2 = np.tile([0.0, 0.0, 1.0], (N_SEC, 1))                               # 手前
WGT = np.array([((s - BEND[0]) / (BEND[1] - BEND[0])) for s in SPAR])
WGT = np.clip(WGT, 0, 1)
WGT = WGT * WGT * (3 - 2 * WGT)
J_REST = CEN[-1].copy()                                                   # 手首（ひづめが おれる中心）
Q3 = np.array([P_Q[0], P_Q[1], 0.0])


def pose(th):
    """ひづめ全体の おれ θ（度）→ (前足の たおれ φ, 手首の おれ ψ, 内がわへ まわる ρ)。前足が 4割・手首が 6割 おれて、少し 内がわへ"""
    phi = 0.4 * th
    return phi, th - phi, 0.06 * th


def rx(v, a):
    """x の じくの まわりに a 度（上が 手前へ）。v：(…, 3)"""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.stack([v[..., 0], v[..., 1] * c + v[..., 2] * s, -v[..., 1] * s + v[..., 2] * c], -1)


def rz(v, a):
    """画面の中で a 度（時計まわり＝内がわ）"""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.stack([v[..., 0] * c - v[..., 1] * s, v[..., 0] * s + v[..., 1] * c, v[..., 2]], -1)


def project(P):
    """遠近：カメラの まん中 P_CAM から 近いほど 大きく → 画面の (x, y)"""
    s = PERSP / (PERSP - P[..., 2])
    return np.stack([P_CAM[0] + (P[..., 0] - P_CAM[0]) * s, P_CAM[1] + (P[..., 1] - P_CAM[1]) * s], -1)


def tube(th):
    """管の 輪切りごとの (まん中, 向き1, 向き2, じく) を たおした形で"""
    phi, psi, rho = pose(th)
    C, N1, N2, T = [], [], [], []
    for k in range(N_SEC):
        a, r = phi * WGT[k], rho * WGT[k]
        C.append(Q3 + rz(rx(CEN[k] - Q3, a), r))
        N1.append(rz(rx(NRM1[k], a), r))
        N2.append(rz(rx(NRM2[k], a), r))
        T.append(rz(rx(TAN[k], a), r))
    return np.array(C), np.array(N1), np.array(N2), np.array(T)


def to_px(P2):
    return np.round((P2 - np.array([BOX[0], BOX[1]])) * SC * 16).astype(np.int32)     # cv2 の shift=4


def from_px(p):
    return p / SC + np.array([BOX[0], BOX[1]])


def poly_path(cnt):
    return enc_poly(from_px(cnt.reshape(-1, 2).astype(float)))


def contours(mask, min_area=40, eps=EPS):
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        out.append(cv2.approxPolyDP(c, eps, True))
    return out


def render_tube(th):
    """管を ぬる：(形の マスク, かげの マスク, 面の番号, 輪切りたち)"""
    C, N1, N2, T = tube(th)
    al = np.linspace(0, 2 * math.pi, N_AROUND, endpoint=False)
    ca, sa = np.cos(al), np.sin(al)
    NR = ca[None, :, None] * N1[:, None, :] + sa[None, :, None] * N2[:, None, :]      # (sec, around, 3)
    S = C[:, None, :] + RAD[:, None, None] * NR
    S2 = project(S)
    W, H = int((BOX[2] - BOX[0]) * SC), int((BOX[3] - BOX[1]) * SC)
    quads = []
    for k in range(N_SEC - 1):
        for j in range(N_AROUND):
            j2 = (j + 1) % N_AROUND
            n = NR[k, j] + NR[k, j2] + NR[k + 1, j] + NR[k + 1, j2]
            n /= np.linalg.norm(n)
            if n[2] < -0.02:
                continue
            z = (S[k, j, 2] + S[k, j2, 2] + S[k + 1, j, 2] + S[k + 1, j2, 2]) / 4
            quads.append((z, k, j, np.array([S2[k, j], S2[k, j2], S2[k + 1, j2], S2[k + 1, j]]), float(n @ LIGHT) < DARK))
    # 先の ふた（手首がわ）：手前を向いていれば
    cap = None
    if T[-1][2] > 0.02:
        cap = (C[-1][2] + 0.01, C[-1][None, :] + RAD[-1] * (ca[:, None] * N1[-1][None, :] + sa[:, None] * N2[-1][None, :]))
    shape = np.zeros((H, W), np.uint8)
    dark = np.zeros((H, W), np.uint8)
    qid = np.full((H, W), -1, np.int32)
    order = sorted(range(len(quads)), key=lambda i: quads[i][0])
    items = [(quads[i][0], 'q', i) for i in order]
    if cap is not None:
        items.append((cap[0], 'c', -1))
        items.sort(key=lambda x: x[0])
    for z, kind, i in items:
        if kind == 'q':
            _, k, j, P2, dk = quads[i]
            pts = to_px(P2)
            cv2.fillConvexPoly(shape, pts, 255, cv2.LINE_8, 4)
            cv2.fillConvexPoly(dark, pts, 255 if dk else 0, cv2.LINE_8, 4)
            cv2.fillConvexPoly(qid, pts, int(k * N_AROUND + j), cv2.LINE_8, 4)
        else:
            pts = cv2.convexHull(to_px(project(cap[1])))
            cv2.fillConvexPoly(shape, pts, 255, cv2.LINE_8, 4)
            cv2.fillConvexPoly(dark, pts, 0, cv2.LINE_8, 4)
            cv2.fillConvexPoly(qid, pts, -2, cv2.LINE_8, 4)
    return shape, dark, qid, (C, N1, N2, T)


# 赤い玉：いまの絵で (DOT_AT) にある 管の面（手前がわ）
def _dot_anchor():
    C, N1, N2, T = tube(0.0)
    best = None
    for k in range(N_SEC):
        for j in range(N_AROUND):
            a = 2 * math.pi * j / N_AROUND
            n = math.cos(a) * N1[k] + math.sin(a) * N2[k]
            if n[2] < 0.2:
                continue
            p = C[k] + RAD[k] * n
            d = math.hypot(p[0] - DOT_AT[0], p[1] - DOT_AT[1])
            if best is None or d < best[0]:
                best = (d, k, j, p[2])
    return best[1], best[2], best[3]


DOT_K, DOT_J, DOT_Z = _dot_anchor()


KAPPA = 0.5522847498                 # だ円を 4つの 3次ベジエで


def bez_ellipse(c, U, V, xf):
    """3D の だ円（まん中 c・半径の向き U・V）を xf で動かして 遠近で うつした 道（4つの ベジエ）"""
    P = [c + U, c + V, c - U, c - V]
    T = [V, -U, -V, U]                                   # 進む向き
    pts = [P[0]]
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        pts += [a + KAPPA * T[i], b - KAPPA * T[(i + 1) % 4], b]
    return enc_bez(project(xf(np.array(pts))))


def dot_xf(th):
    phi, psi, rho = pose(th)
    a, r = phi * WGT[DOT_K], rho * WGT[DOT_K]
    return lambda P: Q3 + rz(rx(P - Q3, a), r)


def dot_svg(th, qid):
    """前足の 赤い玉（いまの絵と同じ 赤い丸に 金のまん中）。前足と いっしょに 動く・向こうを向いたら・かくれたら 描かない"""
    xf = dot_xf(th)
    c0 = np.array([DOT_AT[0], DOT_AT[1], DOT_Z])
    nz = (xf(np.array([[0, 0, 1.0]]) + Q3) - xf(Q3[None, :]))[0][2]
    if nz < 0.15:
        return ''
    cp = to_px(project(xf(c0[None, :])))[0] // 16
    h, w = qid.shape
    if 0 <= cp[1] < h and 0 <= cp[0] < w:
        q = qid[cp[1], cp[0]]
        if q >= 0 and abs(q // N_AROUND - DOT_K) > 3:              # ほかの所に かくれている
            return ''
    ex, ey = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    return (f"<path d='{bez_ellipse(c0, 6 * ex, 6 * ey, xf)}' fill='{RED}' stroke='{OUT}' stroke-width='1.8'/>"
            f"<path d='{bez_ellipse(c0, 3.2 * ex, 3.2 * ey, xf)}' fill='{GOLD}'/>")


def hoof_xf(P, th):
    """ひづめの点（…,3）：手首で おれて（ψ）→ 前足と いっしょに たおれる（φ・ρ）"""
    phi, psi, rho = pose(th)
    P = J_REST + rx(P - J_REST, psi)
    return Q3 + rz(rx(P - Q3, phi), rho)


def ellipse3(c, ab, rot, z, n=96):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    x = ab[0] * np.cos(t); y = ab[1] * np.sin(t)
    return np.stack([c[0] + x * cr - y * sr, c[1] + x * sr + y * cr, np.full(n, z)], 1)


def ell_axes(c, ab, rot, z):
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return np.array([c[0], c[1], z]), np.array([ab[0] * cr, ab[0] * sr, 0.0]), np.array([-ab[1] * sr, ab[1] * cr, 0.0])


def pts_path(P2, close=True):
    return enc_poly(P2, close)


def hoof_svg(th, n=0):
    """ひづめ：まわりの形（厚みの ふち）→ 見えている面（表：金と桃色の裏・つや／裏：金の かべ・白い毛のふち）→ 外の線"""
    zf, zb = HOOF_Z + HOOF_D / 2, HOOF_Z - HOOF_D / 2
    xf = lambda P: hoof_xf(P, th)
    F2 = project(xf(ellipse3(HOOF_C, HOOF_AB, HOOF_ROT, zf)))
    B2 = project(xf(ellipse3(HOOF_C, HOOF_AB, HOOF_ROT, zb)))
    nrm = xf(np.array([[0, 0, 1.0]]) + J_REST)[0] - xf(J_REST[None, :])[0]
    hull = cv2.convexHull(np.round(np.r_[F2, B2] * 64).astype(np.int32))
    hull = cv2.approxPolyDP(hull, 0.16 * 64, True).reshape(-1, 2) / 64.0
    lw = LW2 + 0.6
    front = nrm[2] >= 0
    rim = abs(nrm[2]) < 0.995                             # ふち（厚み）が 見えるか
    hid = f'mkAh{n}'
    if rim:
        out = (f"<defs><path id='{hid}' d='{pts_path(hull)}'/></defs>"
               f"<use href='#{hid}' fill='{RIM}' stroke='{OUT}' stroke-width='{f1(lw)}' stroke-linejoin='round'/>")
    else:
        out = ''
    face = ell_axes(HOOF_C, HOOF_AB, HOOF_ROT, zf if front else zb)
    fd = bez_ellipse(*face, xf)
    if front:                                             # 表（桃色の裏が 手前）
        out += f"<path d='{fd}' fill='{GOLD}' stroke='{OUT}' stroke-width='{2 if rim else f1(lw)}' stroke-linejoin='round'/>"
        out += f"<path d='{bez_ellipse(*ell_axes(SOLE_C, SOLE_AB, SOLE_ROT, zf), xf)}' fill='#F9C6C4'/>"
        sh = project(xf(np.array([[x, y, zf] for x, y in catmull(SHINE, 6)[0]])))
        out += f"<path d='{pts_path(sh, False)}' fill='none' stroke='{GOLD_HI}' stroke-width='2.2' stroke-linecap='round'/>"
    else:                                                 # 裏（金の かべ・手首がわに 白い毛のふち）
        out += f"<path d='{fd}' fill='{GOLD}' stroke='{OUT}' stroke-width='2' stroke-linejoin='round'/>"
        cr, sr = math.cos(math.radians(HOOF_ROT)), math.sin(math.radians(HOOF_ROT))
        a, b = HOOF_AB

        def local(u, v):                                  # だ円の中の 位置（u：よこ −1〜1・v：たて −1＝つま先 〜 1＝手首がわ）
            x, y = a * u, b * v
            return [HOOF_C[0] + x * cr - y * sr, HOOF_C[1] + x * sr + y * cr, zb]
        t = np.linspace(-1, 1, 9)
        v0 = 0.5                                          # 白い毛のふちの さかい
        cuff = [local(u * math.sqrt(1 - v0 * v0), v0 + 0.1 * (1 - u * u)) for u in t]
        arc = [local(math.cos(g), math.sin(g)) for g in np.linspace(math.asin(v0), math.pi - math.asin(v0), 9)]
        toe = [local(u * math.sqrt(1 - 0.62 ** 2), -0.62 + 0.08 * (1 - u * u)) for u in t]
        tarc = [local(math.cos(g), -math.sin(g)) for g in np.linspace(math.asin(0.62), math.pi - math.asin(0.62), 9)]
        P = lambda L: project(xf(np.array(L)))
        ring = [local(u * 0.78, -0.1 + 0.06 * (1 - u * u)) for u in t]
        hi = [local(u, v0 - 0.16 - 0.05 * (1 - (u + 0.45) ** 2 / 0.09)) for u in np.linspace(-0.72, -0.2, 5)]
        out += (f"<path d='{pts_path(P(toe + tarc[::-1]))}' fill='{GOLD_SH}' opacity='.7'/>"
                f"<path d='{pts_path(P(ring), False)}' fill='none' stroke='{GOLD_SH}' stroke-width='2' stroke-linecap='round'/>"
                f"<path d='{pts_path(P(cuff + arc[::-1]))}' fill='#FFFFFF'/>"
                f"<path d='{pts_path(P(cuff), False)}' fill='none' stroke='{OUT}' stroke-width='2.2' stroke-linecap='round'/>"
                f"<path d='{pts_path(P(hi), False)}' fill='none' stroke='{GOLD_HI}' stroke-width='2.2' stroke-linecap='round'/>")
    if rim:
        out += f"<use href='#{hid}' fill='none' stroke='{OUT}' stroke-width='{f1(lw)}' stroke-linejoin='round'/>"
    return out


def frame_svg(th, n, junc='mkAj'):
    """θ の時の 右前足とひづめ（招き馬の座標）。前足の形は 1つの道（defs）を 2回使う：線（太く・体との つなぎ目は junc で切る）→ 白。
       その上に かげ・赤い玉・ひづめ"""
    shape, dark, qid, _ = render_tube(th)
    cs = contours(shape, 400)
    assert len(cs) == 1, ('tube parts', th, len(cs))
    tid = f'mkAt{n}'
    out = (f"<defs><path id='{tid}' d='{poly_path(cs[0])}'/></defs>"
           f"<use href='#{tid}' fill='{OUT}' stroke='{OUT}' stroke-width='{f1(LW * 2)}' stroke-linejoin='round' clip-path='url(#{junc})'/>"
           f"<use href='#{tid}' fill='#FFFFFF'/>")
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dk = cv2.morphologyEx(cv2.bitwise_and(dark, shape), cv2.MORPH_OPEN, k)
    sh = contours(dk, 60, 2.4)
    if sh:
        out += f"<path d='{''.join(poly_path(c) for c in sh)}' fill='{SHADE}'/>"
    out += dot_svg(th, qid)
    out += hoof_svg(th, n)
    return out


def bbox(th):
    shape, _, _, _ = render_tube(th)
    ys, xs = np.nonzero(shape)
    zf, zb = HOOF_Z + HOOF_D / 2, HOOF_Z - HOOF_D / 2
    H2 = np.r_[project(hoof_xf(ellipse3(HOOF_C, HOOF_AB, HOOF_ROT, zf), th)), project(hoof_xf(ellipse3(HOOF_C, HOOF_AB, HOOF_ROT, zb), th))]
    x0 = min(xs.min() / SC + BOX[0] - LW, H2[:, 0].min() - 2)
    x1 = max(xs.max() / SC + BOX[0] + LW, H2[:, 0].max() + 2)
    y0 = min(ys.min() / SC + BOX[1] - LW, H2[:, 1].min() - 2)
    y1 = max(ys.max() / SC + BOX[1] + LW, H2[:, 1].max() + 2)
    return x0, y0, x1, y1


THETAS = [0, -24, -16, -8, 8, 16, 24, 32, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]   # コマの θ（0 が いつもの形・帯の いちばん左）


def strip(junc='mkAj'):
    """コマを よこに ならべた帯：(SVG, θ の列, 窓 (x0, y0, x1, y1), コマの はば)。窓の外は 見えない（となりのコマが 入らない はば）"""
    boxes = [bbox(t) for t in THETAS]
    x0 = math.floor(min(b[0] for b in boxes)) - 1
    y0 = math.floor(min(b[1] for b in boxes)) - 1
    x1 = math.ceil(max(b[2] for b in boxes)) + 1
    y1 = math.ceil(max(b[3] for b in boxes)) + 1
    slot = int(x1 - x0 + 8)
    svg = ''.join(f"<g transform='translate({k * slot} 0)'>{frame_svg(t, k, junc)}</g>" if k else frame_svg(t, k, junc)
                  for k, t in enumerate(THETAS))
    return svg, THETAS, (x0, y0, x1, y1), slot


def nearest(th):
    """θ に いちばん近い コマの番号"""
    return min(range(len(THETAS)), key=lambda k: (abs(THETAS[k] - th), k))


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    import lucky_maneki as M
    from flat_horse import to_png
    ths = [0, -24, -12, 12, 24, 38, 60, 80, 90, 100, 120, 140, 160]
    cells = []
    for th in ths:
        arm = frame_svg(th, 0)

        def rig_arm(a, h, arm=arm):
            return arm
        svg = M.maneki_svg(rig=dict(arm=rig_arm, defs=lambda: "<clipPath id='mkAj'><rect x='-50' y='0' width='129' height='300'/></clipPath>"))
        svg = svg.replace('<defs>', "<rect x='-50' y='-50' width='400' height='400' fill='#FFF8EC'/><defs>", 1)
        fn = os.path.join(out, f'arm_{th:+04d}.png')
        to_png(svg.replace("width='240' height='270'", "width='480' height='540'"), 480, 540, fn, scale=1)
        cells.append(cv2.imread(fn))
        print(th, bbox(th))
    orig = os.path.join(out, 'orig.png')
    to_png(M.maneki_svg().replace('<defs>', "<rect x='-50' y='-50' width='400' height='400' fill='#FFF8EC'/><defs>", 1).replace("width='240' height='270'", "width='480' height='540'"), 480, 540, orig, scale=1)
    cells.insert(0, cv2.imread(orig))
    while len(cells) % 7:
        cells.append(np.full_like(cells[0], 255))
    rows = [np.concatenate(cells[i:i + 7], 1) for i in range(0, len(cells), 7)]
    cv2.imwrite(os.path.join(out, 'sheet.png'), np.concatenate(rows, 0))
