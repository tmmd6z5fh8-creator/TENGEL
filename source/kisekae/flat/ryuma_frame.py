"""龍馬テーマの「金の双龍の額縁」（アニメ調・780×320）：一から作った創作の絵。
   まさちゃんが送った金の双龍の額縁の写真の「構図」（左右の上すみに向かい合う龍の頭・体は左右のふちを下へうねり・
   前足の爪が下の横木をつかむ・上下のまん中に飾り）に寄せて作る。写真そのものは使わない。
   - 龍は3Dで組み立てて（r3d/h3d.py：体はたまのつらなり・龍の頭・角・前足と爪）、法線と奥行きから
     アニメ調に塗る（金を3段階＋ハイライト・ふちは濃い線）。うろこ・はらの板・背びれ・たてがみ・ひげは2D
   - 右の龍を1体だけ描いて、左は法線を左右に返して同じ光で塗る（左右対称の額縁）
   - 横木（上下）と飾り（上下のまん中）は2D
   frame(bg_srgb, rng) → 額縁をのせた絵（sRGB 0〜1）"""
import os, sys, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
from h3d import Scene, nrm, basis
from paint import smoothstep

W, Hh = 780, 320
SS = 2                                   # 龍は2倍の大きさで塗ってから縮める（線がなめらかに）
CX, CY = W / 2.0, Hh / 2.0
CAM_D = 20.0                             # カメラの距離（遠いほど平行投影に近い。sdfr の最大距離 60 より手前）
FOV = math.degrees(2 * math.atan((Hh / 2.0 / 100.0) / CAM_D))

# 素材番号
BODY, HEAD, HORN, EYE, TEETH, MOUTH, FIN, LEG, CLAW, TONGUE = 1, 2, 3, 5, 6, 7, 8, 10, 11, 12
HEAD_MATS = (HEAD, HORN, EYE, TEETH, MOUTH, FIN, TONGUE)

# アニメ調の金（sRGB）
G_LINE = np.array([0.24, 0.12, 0.015])
G_DARK = np.array([0.52, 0.30, 0.05])
G_MID = np.array([0.86, 0.60, 0.15])
G_LIGHT = np.array([0.99, 0.84, 0.40])
G_HI = np.array([1.00, 0.97, 0.80])


def Wp(px, py, z=0.0):
    """画像の座標（画素）→ 世界（1単位＝100画素。カメラは -z にあり、画像の右は世界の -x）"""
    return np.array([-(px - CX) / 100.0, (CY - py) / 100.0, z])


def Wd(dx, dy, dz=0.0):
    return nrm(np.array([-dx, -dy, dz]))


def catmull(P, n_per=8):
    """点の列（x, y, ...）を なめらかな線に（各区間 n_per 分割）。列ごとに補間する"""
    P = np.asarray(P, float)
    Q = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for t in np.linspace(0, 1, n_per, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Q[-2])
    return np.array(out)


# ---------------------------------------------------------------- 龍の形（右の龍・画像の座標）
# 背骨：(x, y, 半径[画素], z[世界]) 頭のうしろ → 首 → 右のふちを下へ → 右下のすみ → 下の横木にそって → しっぽは下へ消える
SPINE = [(686, 126, 20, 0.0), (730, 156, 25, 0.0), (750, 200, 30, 0.0), (740, 244, 30, 0.0), (702, 272, 28, 0.0),
         (644, 282, 26, 0.0), (584, 272, 22, 0.05), (540, 286, 16, 0.25), (510, 316, 10, 0.4), (488, 345, 5, 0.5)]
HEAD_POLL = (684, 90)                    # 頭の座標の原点（うなじ）
HEAD_ANG = -8.0                         # 鼻先の向き（世界の角度：-x が画像の左）
HS = 2.25                                # 頭の大きさ（頭の長さ ≈ 0.63×HS 単位）
LEGP = dict(shoulder=(616, 270), elbow=(588, 302), wrist=(540, 296), foot=(512, 290), z=-0.26)


def head_frame():
    u = np.array([math.cos(math.radians(HEAD_ANG)), math.sin(math.radians(HEAD_ANG))])
    U3 = np.array([u[0], u[1], 0.0])
    V3 = np.array([-u[1], u[0], 0.0])
    poll = Wp(*HEAD_POLL)
    hp = lambda s_, w_, z=0.0: poll + (U3 * s_ + V3 * w_) * HS + np.array([0, 0, z * HS])
    return U3, V3, hp


def bez3(P, t):
    P = np.asarray(P, float)
    t = np.asarray(t, float)[..., None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]


def chain(sc, pts, rad, mat, k=0.0, kg=0.012):
    sc.begin('U', kg, mat)
    for i in range(len(pts) - 1):
        sc.rcone(pts[i], pts[i + 1], rad[i], rad[i + 1], k=k, mat=mat)
    sc.end()


def dragon_head(sc):
    """龍の頭（アニメ調向けに、鼻先を太く・まゆを大きく・口を大きく開ける）。目印（画像の座標）を返す"""
    U3, V3, hp = head_frame()
    out3 = np.array([0, 0, 1.0])

    def hdir(rot):
        a = math.radians(rot)
        return U3 * math.cos(a) + V3 * math.sin(a), -U3 * math.sin(a) + V3 * math.cos(a)

    def E(s_, w, z, r, k, op='U', rot=0.0, mat=HEAD):
        dx, dy = hdir(rot)
        sc.ell(hp(s_, w, z), tuple(x * HS for x in r), basis(dx, dy), op=op, k=k, mat=mat)

    def RB(s_, w, z, half, rnd, k, rot=0.0, op='U', mat=HEAD):
        dx, dy = hdir(rot)
        sc.rbox(hp(s_, w, z), tuple(x * HS for x in half), rnd * HS, basis(dx, dy), op=op, k=k, mat=mat)

    def RC(a, b, ra, rb, k, mat=HEAD):
        sc.rcone(hp(*a), hp(*b), ra * HS, rb * HS, k=k, mat=mat)

    # ---------- 上あご・頭蓋 ----------
    sc.begin('U', 0.03, HEAD)
    E(0.10, 0.01, 0, (0.165, 0.135, 0.150), k=0.05)                        # 頭蓋
    E(0.03, 0.085, 0, (0.11, 0.06, 0.11), k=0.04)                          # ひたい
    RB(0.35, 0.005, 0, (0.21, 0.098, 0.090), 0.06, k=0.04, rot=-2)         # 鼻先（箱のように深く）
    E(0.57, 0.030, 0, (0.095, 0.085, 0.095), k=0.03)                       # 鼻先の丸み（上を向いた鼻）
    RC((0.24, -0.100, 0.0), (0.58, -0.108, 0.0), 0.036, 0.036, k=0.03)     # 上くちびる（厚い）
    for z in (1, -1):
        E(0.19, 0.110, 0.084 * z, (0.13, 0.050, 0.055), k=0.02, rot=-12)   # まゆ（大きく張り出す）
        E(0.05, 0.130, 0.090 * z, (0.085, 0.032, 0.040), k=0.02, rot=-35)  # まゆのうしろの流れ
        E(0.24, -0.045, 0.090 * z, (0.14, 0.10, 0.045), k=0.03)            # ほお
        E(0.50, -0.062, 0.086 * z, (0.065, 0.045, 0.030), k=0.02, rot=6)   # 牙の上のふくらみ
        E(0.59, 0.080, 0.066 * z, (0.045, 0.030, 0.036), k=0.02, rot=10)   # 鼻の穴のふくらみ
        sc.sph(hp(0.630, 0.085, 0.070 * z), 0.020 * HS, op='S', k=0.006, mat=HEAD)    # 鼻の穴
    RB(0.40, -0.118, 0, (0.20, 0.010, 0.09), 0.006, k=0.004, op='S', rot=-1)         # 歯ぐきの線
    sc.end()
    # ---------- 下あご（大きく開く） ----------
    OPEN = 42.0
    hinge = hp(0.19, -0.095)
    dj, nj = hdir(-OPEN)
    JL = 0.44
    jaw_end = hinge + dj * JL * HS
    sc.begin('U', 0.02, HEAD)
    sc.rcone(hinge, jaw_end, 0.076 * HS, 0.048 * HS, k=0.02, mat=HEAD)
    sc.ell(jaw_end + nj * 0.014 * HS, (0.058 * HS, 0.042 * HS, 0.054 * HS), basis(dj, nj), k=0.02, mat=HEAD)       # あご先
    sc.ell(jaw_end - dj * 0.02 * HS + nj * 0.048 * HS, (0.052 * HS, 0.024 * HS, 0.052 * HS), basis(dj, nj), k=0.02, mat=HEAD)   # 下くちびる
    for z in (1, -1):
        sc.rcone(hinge + out3 * 0.060 * z * HS, jaw_end + out3 * 0.040 * z * HS, 0.042 * HS, 0.028 * HS, k=0.02, mat=HEAD)
    sc.end()
    # 口の中・舌
    mc = (hp(0.40, -0.11) + (hinge + dj * 0.24 * HS)) / 2
    sc.ell(mc, (0.20 * HS, 0.050 * HS, 0.062 * HS), basis(dj * 0.5 + U3 * 0.5, nj), k=0.0, mat=MOUTH)
    sc.ell(hinge + dj * 0.23 * HS + nj * 0.032 * HS, (0.14 * HS, 0.018 * HS, 0.036 * HS), basis(dj * 0.9 + nj * 0.1, nj), k=0.0, mat=TONGUE)
    # ---------- 歯 ----------
    for z in (1, -1):
        for s_ in np.arange(0.27, 0.58, 0.05):
            a = hp(s_, -0.108, 0.068 * z)
            fang = s_ >= 0.50
            L = 0.036 if not fang else 0.095
            r0 = 0.014 if not fang else 0.019
            sc.ccone(a + V3 * 0.012 * HS, a - V3 * L * HS - U3 * 0.006 * HS, r0 * HS, 0.0025 * HS, rnd=0.002, side=U3, k=0.0, mat=TEETH)
        for u in np.arange(0.22, 0.98, 0.12):
            a = hinge + dj * u * (JL - 0.02) * HS + out3 * 0.050 * z * HS + nj * 0.042 * HS
            fang = u >= 0.85
            L = 0.032 if not fang else 0.072
            r0 = 0.013 if not fang else 0.017
            sc.ccone(a - nj * 0.01 * HS, a + nj * L * HS - dj * (0.01 if fang else 0) * HS, r0 * HS, 0.0025 * HS, rnd=0.002, side=U3, k=0.0, mat=TEETH)
    # ---------- 目・まぶた ----------
    eyes = []
    for z in (1, -1):
        c = hp(0.21, 0.050, 0.098 * z)
        sc.sph(c, 0.060 * HS, k=0.0, mat=EYE)
        E(0.21, 0.098, 0.104 * z, (0.080, 0.026, 0.036), k=0.01, rot=-12)   # 上まぶた（するどく）
        eyes.append(c)
    # ---------- 角（うしろへ流れる・枝つき） ----------
    tips = []
    for z in (1, -1):
        b = hp(0.02, 0.105, 0.060 * z)
        d0 = nrm(-U3 * 0.74 + V3 * 0.50 + out3 * 0.28 * z)
        d1 = nrm(-U3 * 0.96 + V3 * 0.16 + out3 * 0.08 * z)
        d2 = nrm(-U3 * 0.85 + V3 * 0.42 + out3 * 0.02 * z)
        L = 0.40 * HS
        P = [b, b + d0 * L * 0.30, b + d0 * L * 0.40 + d1 * L * 0.32, b + d0 * L * 0.32 + d1 * L * 0.42 + d2 * L * 0.26]
        us = np.linspace(0, 1, 17)
        pts = [bez3(P, u) for u in us]
        rad = [0.064 * HS * (1 - 0.80 * u ** 1.1) for u in us]
        chain(sc, pts, rad, HORN, kg=0.014)
        for (u0, dt_, Lt, r0) in ((0.30, nrm(V3 * 0.80 + U3 * 0.50 + out3 * 0.25 * z), 0.18, 0.028),
                                  (0.62, nrm(V3 * 0.90 - U3 * 0.10 + out3 * 0.40 * z), 0.14, 0.022)):
            q = bez3(P, u0)
            Q = [q, q + dt_ * Lt * HS * 0.45, q + dt_ * Lt * HS * 0.8 - U3 * Lt * HS * 0.08, q + dt_ * Lt * HS - U3 * Lt * HS * 0.22]
            p2 = [bez3(Q, v) for v in np.linspace(0, 1, 8)]
            chain(sc, p2, [r0 * HS * (1 - 0.82 * v) for v in np.linspace(0, 1, 8)], HORN, kg=0.012)
            tips.append(p2[-1])
        tips.append(pts[-1])
    # 耳
    for z in (1, -1):
        sc.rcone(hp(0.02, 0.040, 0.098 * z), hp(-0.13, 0.085, 0.145 * z), 0.028 * HS, 0.005 * HS, k=0.01, mat=HEAD)
    # ほおのひれ（うしろへ広がる うすい板：3枚）
    for z in (1, -1):
        for i, rot in enumerate((165, 190, 215)):
            dx, dy = hdir(rot)
            c = hp(0.14, -0.050 - 0.025 * i, 0.108 * z)
            sc.ell(c + dx * 0.12 * HS, (0.14 * HS, 0.048 * HS * (1 - 0.15 * i), 0.008 * HS), basis(dx, dy), k=0.004, mat=FIN)
    return dict(eyes=eyes, tips=tips, hinge=hinge, jaw_end=jaw_end, hp=hp, U3=U3, V3=V3,
                nose=hp(0.66, 0.02), skull_back=hp(-0.05, 0.0), jaw_mid=hinge + dj * 0.5 * JL * HS)


def build(sc):
    """右の龍ぜんたい。目印（世界の点）を返す"""
    dense = catmull(SPINE, 6)                                             # (x, y, r, z)
    pts = [Wp(p[0], p[1], p[3]) for p in dense]
    rad = [p[2] / 100.0 for p in dense]
    chain(sc, pts, rad, BODY, k=0.02, kg=0.02)
    H = dragon_head(sc)
    # 首と頭のつなぎ（頭蓋のうしろ・下に たまを足す）
    sc.sph(H['hp'](0.02, -0.06), 0.14 * HS, k=0.05, mat=BODY)
    # 前足（手前）：肩 → ひじ → 手首 → 足 → 爪4本
    z = LEGP['z']
    sh, el, wr, ft = (Wp(*LEGP[k], z) for k in ('shoulder', 'elbow', 'wrist', 'foot'))
    sc.begin('U', 0.03, LEG)
    sc.sph(sh + np.array([0, 0, 0.16]), 0.15, k=0.03, mat=LEG)
    sc.rcone(sh, el, 0.150, 0.115, k=0.03, mat=LEG)
    sc.ell(el, (0.13, 0.12, 0.11), None, k=0.03, mat=LEG)
    sc.rcone(el, wr, 0.115, 0.095, k=0.03, mat=LEG)
    sc.ell(ft + np.array([0, 0.02, 0]), (0.14, 0.10, 0.11), None, k=0.03, mat=LEG)
    sc.end()
    claws = []
    for i, ang in enumerate((155, 178, 200, 125)):                        # 画像の角度（0=右・90=下）：左へ広げ、下へ曲がって横木をつかむ
        a = math.radians(ang)
        d = Wd(math.cos(a), math.sin(a), 0)
        dn = Wd(0, 1, 0)                                                  # 下へ曲がる
        L = (0.36, 0.34, 0.30, 0.26)[i]
        b = ft + d * 0.06 + np.array([0, 0, (-0.02 if i < 3 else 0.06)])
        P = [b, b + d * L * 0.45, b + d * L * 0.78 + dn * L * 0.12, b + d * L * 0.86 + dn * L * 0.50]
        vs = np.linspace(0, 1, 9)
        cp = [bez3(P, v) for v in vs]
        chain(sc, cp, [0.068 * (1 - 0.86 * v) + 0.006 for v in vs], CLAW, kg=0.01)
        claws.append(cp[-1])
    marks = dict(head=H, spine=dense, claws=claws, leg=dict(sh=sh, el=el, wr=wr, ft=ft))
    return marks


def render(tmp):
    sc = Scene()
    sc.image(W * SS, Hh * SS, 2)
    sc.camera((0, 0, -CAM_D), (0, 0, 0), FOV)
    sc.bounce(0)
    sc.env((1, 1, 1), (1, 1, 1), (1, 1, 1), (0, 0, 0))
    for mid in (BODY, HEAD, HORN, EYE, TEETH, MOUTH, FIN, LEG, CLAW, TONGUE):
        sc.mat(mid, 1, (1, 1, 1), 1.0, 0, 0, 0)
    M = build(sc)
    R = sc.render(os.path.join(tmp, 'frame'))
    P = lambda pts: sc.project(np.asarray(pts, float))[0][:, :2] / SS
    H = M['head']
    marks = dict(eyes=P(H['eyes']), tips=P(H['tips']), nose=P([H['nose']])[0], skull_back=P([H['skull_back']])[0],
                 hinge=P([H['hinge']])[0], jaw_end=P([H['jaw_end']])[0], jaw_mid=P([H['jaw_mid']])[0],
                 claws=P(M['claws']), spine=M['spine'], hp=lambda s_, w_, z=0.0: P([H['hp'](s_, w_, z)])[0])
    return R, marks


# ---------------------------------------------------------------- アニメ調の塗り
def toon(G, flip=False):
    """G：描画の結果（n・d・a・m・ao）。アニメ調の色（sRGB・2倍の大きさ）と、ふちの線・素材の番号を返す"""
    n = G['n'].copy(); d = G['d'].copy(); a = np.clip(G['a'], 0, 1).copy(); m = G['m'].copy(); ao = G['ao'].copy()
    if flip:
        n = n[:, ::-1].copy(); n[..., 0] *= -1
        d = d[:, ::-1].copy(); a = a[:, ::-1].copy(); m = m[:, ::-1].copy(); ao = ao[:, ::-1].copy()
    hit = d > 0
    mid = np.rint(m).astype(int)
    L = nrm(np.array([0.45, 0.80, -0.42]))                                # 画像の左上・手前から
    V = np.array([0, 0, -1.0])
    Hv = nrm(L + V)
    lam = n @ L
    spec = np.clip(n @ Hv, 0, 1)
    k1 = smoothstep(0.04, 0.12, lam)                                       # かげ → 中
    k2 = smoothstep(0.40, 0.48, lam)                                       # 中 → 明るい
    k3 = smoothstep(0.86, 0.90, spec) * (lam > 0.3)                        # ハイライト
    occl = smoothstep(0.30, 0.55, ao)                                      # くぼみはかげに
    k1 = k1 * occl; k2 = k2 * occl; k3 = k3 * occl
    col = np.zeros(n.shape, np.float32)

    def paint(mask, dark, mid_, light, hi):
        c = dark + (mid_ - dark) * k1[..., None] + (light - mid_) * k2[..., None] + (hi - light) * k3[..., None]
        col[mask] = c[mask]

    gold = np.isin(mid, (BODY, HEAD, HORN, FIN, LEG, CLAW)) & hit
    paint(gold, G_DARK, G_MID, G_LIGHT, G_HI)
    paint((mid == MOUTH) & hit, np.array([0.30, 0.04, 0.04]), np.array([0.58, 0.09, 0.07]), np.array([0.74, 0.16, 0.12]), np.array([0.85, 0.30, 0.25]))
    paint((mid == TONGUE) & hit, np.array([0.55, 0.12, 0.12]), np.array([0.82, 0.26, 0.26]), np.array([0.93, 0.42, 0.42]), np.array([1.0, 0.70, 0.70]))
    paint((mid == TEETH) & hit, np.array([0.70, 0.62, 0.45]), np.array([0.93, 0.89, 0.76]), np.array([1.0, 0.98, 0.90]), np.array([1, 1, 1]))
    paint((mid == EYE) & hit, np.array([0.80, 0.55, 0.10]), np.array([1.0, 0.80, 0.20]), np.array([1.0, 0.92, 0.45]), np.array([1, 1, 0.9]))
    # ふちの線：奥行きの段差・法線の折れ・輪郭
    dd = np.where(hit, d, CAM_D + 2.0)
    gx = cv2.Sobel(dd, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(dd, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    dep_edge = np.sqrt(gx * gx + gy * gy) > 0.018
    nn = n * hit[..., None]
    nd = 0
    for (dx, dy) in ((1, 0), (0, 1)):
        sh = np.roll(nn, (dy, dx), (0, 1))
        nd = np.maximum(nd, 1 - np.sum(nn * sh, -1))
    nor_edge = (nd > 0.45) & hit
    sil = (a > 0.08) & (a < 0.92)
    edge = (dep_edge | nor_edge | sil) & (a > 0.05)
    edge = cv2.dilate(edge.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)
    return col, a, edge, mid, hit


# ---------------------------------------------------------------- 2Dの飾り（うろこ・はらの板・背びれ・たてがみ・ひげ）
def spine_uv(dense, shape, mask, ss=SS):
    """各画素の、背骨にいちばん近い点の（u：頭からの長さ・v：横の符号つき距離・R：半径・tx,ty：向き）。画素の単位（ss倍）"""
    pts = dense[:, :2] * ss
    rad = dense[:, 2] * ss
    seg = np.diff(pts, axis=0)
    seglen = np.linalg.norm(seg, axis=1) + 1e-9
    u0 = np.concatenate([[0], np.cumsum(seglen)])
    ys, xs = np.nonzero(mask)
    P = np.stack([xs, ys], 1).astype(np.float32)
    best_d = np.full(len(P), 1e9, np.float32); best_u = np.zeros(len(P), np.float32); best_v = np.zeros(len(P), np.float32)
    best_R = np.zeros(len(P), np.float32); best_t = np.zeros((len(P), 2), np.float32)
    for i in range(len(seg)):
        A = pts[i]; T = seg[i] / seglen[i]
        rel = P - A
        t = np.clip(rel @ T, 0, seglen[i])
        q = A + np.outer(t, T)
        dv = P - q
        dist = np.linalg.norm(dv, axis=1)
        v = rel[:, 0] * T[1] - rel[:, 1] * T[0]                          # 符号つき横距離（進む向きの右が +）
        better = dist < best_d
        best_d[better] = dist[better]; best_u[better] = u0[i] + t[better]; best_v[better] = v[better]
        f = t[better] / seglen[i]
        best_R[better] = rad[i] + (rad[i + 1] - rad[i]) * f
        best_t[better] = T
    return xs, ys, best_u, best_v, best_R, best_t


def body_detail(col, edge, mid, hit, dense, ss=SS):
    """うろこ（瓦のように重なる弧）と はらの板（横のすじ）を、体の塗りに重ねる"""
    body = (mid == BODY) & hit
    xs, ys, u, v, R, T = spine_uv(dense, col.shape[:2], body, ss)
    # はらの側：進む向きの「画像の中心」がわ
    cxs, cys = CX * ss, CY * ss
    side = np.sign((cxs - xs) * T[:, 1] - (cys - ys) * T[:, 0])          # 中心が右（+）か左（-）か
    side[side == 0] = 1
    vb = v * side                                                         # はら側が +
    rel = vb / np.maximum(R, 1)
    s = np.maximum(7.0 * ss, 0.36 * R)                                   # うろこの大きさ
    row = np.floor(u / (0.78 * s))
    off = (row % 2) * 0.5 * s
    colm = np.floor((v + off) / s)
    cu = row * 0.78 * s + 0.25 * s
    cv_ = (colm + 0.5) * s - off
    dist = np.sqrt((u - cu) ** 2 + (v - cv_) ** 2)
    arc = (np.abs(dist - 0.5 * s) < 0.75 * ss) & (u >= cu)
    hi = (dist < 0.5 * s - 1.2 * ss) & (dist > 0.5 * s - 2.6 * ss) & (u >= cu) & ((v - cv_) * side < -0.15 * s)
    scaly = (rel < 0.30) & (np.abs(rel) < 0.94)
    belly = (rel >= 0.30) & (rel < 0.96)
    plate = (np.abs(((u + 4 * ss) % (10.0 * ss)) - 5.0 * ss) < 0.8 * ss)
    plate_hi = (np.abs(((u + 4 * ss) % (10.0 * ss)) - 7.4 * ss) < 0.9 * ss)
    dark = np.zeros(col.shape[:2], np.float32); light = np.zeros(col.shape[:2], np.float32)
    dark[ys[scaly & arc], xs[scaly & arc]] = 0.55
    light[ys[scaly & hi], xs[scaly & hi]] = 0.35
    dark[ys[belly & plate], xs[belly & plate]] = 0.5
    light[ys[belly & plate_hi], xs[belly & plate_hi]] = 0.25
    # はらの板は少し明るい金に
    bl = np.zeros(col.shape[:2], np.float32); bl[ys[belly], xs[belly]] = 1.0
    bl = cv2.GaussianBlur(bl, (0, 0), 1.0 * ss)
    col = col + bl[..., None] * (G_LIGHT - col) * 0.25
    col = col * (1 - dark[..., None]) + G_LINE * dark[..., None] * 0.9 + dark[..., None] * col * 0.1
    col = col + light[..., None] * (G_HI - col) * 0.6
    return col


def dorsal_spikes(dense, ss=SS):
    """背びれ：背骨の「外」がわ（はらの反対）に、しっぽの方へ少しねた とがった三角を並べる。塗り（色・alpha・線）を返す"""
    pts = dense[:, :2] * ss
    rad = dense[:, 2] * ss
    seg = np.diff(pts, axis=0); seglen = np.linalg.norm(seg, axis=1) + 1e-9
    u0 = np.concatenate([[0], np.cumsum(seglen)])
    cxs, cys = CX * ss, CY * ss
    fill = np.zeros((Hh * ss, W * ss), np.float32); line = np.zeros_like(fill); shade = np.zeros_like(fill)

    def at(uq):
        i = int(np.clip(np.searchsorted(u0, uq) - 1, 0, len(seg) - 1))
        f = (uq - u0[i]) / seglen[i]
        p = pts[i] + seg[i] * f
        T = seg[i] / seglen[i]
        R = rad[i] + (rad[i + 1] - rad[i]) * f
        side = np.sign((cxs - p[0]) * T[1] - (cys - p[1]) * T[0])          # 画像の中心が、v>0 の側（+）か（-）か
        back = np.array([-T[1], T[0]]) * (1 if side >= 0 else -1)          # 背は中心の反対がわ（v>0 の単位法線は (T[1], -T[0])）
        return p, T, R, back

    uq = 16.0 * ss
    k = 0
    while uq < u0[-1] - 30 * ss:
        p, T, R, back = at(uq)
        if R < 7 * ss:
            break
        h = R * (0.55 if k % 2 == 0 else 0.38) + 4 * ss
        wdt = R * 0.42
        b0 = p + back * R * 0.92 - T * wdt * 0.55
        b1 = p + back * R * 0.92 + T * wdt * 0.55
        apex = p + back * (R + h) + T * wdt * 0.75
        poly = np.round(np.array([b0, apex, b1]) * 16).astype(np.int32)
        cv2.fillPoly(fill, [poly], 1.0, cv2.LINE_AA, shift=4)
        half = np.round(np.array([b0, apex, (apex + b1) / 2 * 0.0 + (b0 + b1) / 2]) * 16).astype(np.int32)
        cv2.fillPoly(shade, [half], 1.0, cv2.LINE_AA, shift=4)
        cv2.polylines(line, [poly], True, 1.0, int(1.4 * ss), cv2.LINE_AA, shift=4)
        uq += max(13.0 * ss, 0.95 * R)
        k += 1
    col = G_MID[None, None] * (1 - shade[..., None] * 0.5) + G_LIGHT[None, None] * shade[..., None] * 0.5
    return col, fill, line


def tuft(acc_fill, acc_shade, acc_line, p0, ang, L, wd, curve, ss=SS):
    """炎のような とがった房（たてがみ・あごひげ）：根元 p0（画素）・向き ang（度）・長さ・幅・曲がり"""
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)]); n = np.array([-d[1], d[0]])
    us = np.linspace(0, 1, 14)
    spine = [p0 + d * L * u + n * curve * L * u * u for u in us]
    wid = [wd * (1 - u) ** 0.7 * (0.35 + 0.65 * smoothstep(0, 0.25, u)) for u in us]
    left = [spine[i] + n * wid[i] for i in range(len(us))]
    right = [spine[i] - n * wid[i] for i in range(len(us))]
    poly = np.array(left + right[::-1]) * ss
    q = np.round(poly * 16).astype(np.int32)
    cv2.fillPoly(acc_fill, [q], 1.0, cv2.LINE_AA, shift=4)
    half = np.array([spine[i] for i in range(len(us))] + right[::-1]) * ss
    cv2.fillPoly(acc_shade, [np.round(half * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
    cv2.polylines(acc_line, [q], True, 1.0, int(1.4 * ss), cv2.LINE_AA, shift=4)


def mane(M, rng, ss=SS, flip=False):
    """たてがみ（頭のうしろから外へ広がる炎のような房）・あごひげ・ひげ。塗り（色・alpha・線）と、ひげの線を返す。
       flip：左の龍（向きを左右に返す）"""
    fill = np.zeros((Hh * ss, W * ss), np.float32); shade = np.zeros_like(fill); line = np.zeros_like(fill)
    hp = M['hp']
    A = (lambda ang: 180 - ang) if flip else (lambda ang: ang)
    C = (lambda c: -c) if flip else (lambda c: c)
    X = (lambda dx: -dx) if flip else (lambda dx: dx)
    # たてがみ：頭蓋のうしろのふち（上から下へ）から、うしろ（右の龍では画像の右）へ
    base = [(hp(-0.02, 0.08), -62, 58, 15, 0.30), (hp(-0.06, 0.03), -38, 66, 17, 0.25), (hp(-0.08, -0.03), -16, 70, 18, 0.15),
            (hp(-0.07, -0.09), 4, 66, 17, 0.0), (hp(-0.03, -0.14), 24, 60, 16, -0.15), (hp(0.03, -0.17), 44, 50, 14, -0.25),
            (hp(0.10, -0.19), 66, 42, 12, -0.30)]
    for (p, ang, L, wd, cv_) in base:
        tuft(fill, shade, line, np.asarray(p), A(ang + rng.uniform(-4, 4)), L * rng.uniform(.92, 1.08), wd, C(cv_))
        tuft(fill, shade, line, np.asarray(p) + np.array([X(6), 0]), A(ang + rng.uniform(-6, 6) + 10), L * 0.6, wd * 0.6, C(cv_ * 0.5))
    # まゆの上の小さな房（ひたい）
    for (p, ang, L, wd, cv_) in ((hp(0.10, 0.17), -100, 26, 7, 0.2), (hp(0.16, 0.19), -92, 22, 6, 0.1)):
        tuft(fill, shade, line, np.asarray(p), A(ang), L, wd, C(cv_))
    # あごひげ：あご先から下・うしろへ
    je = M['jaw_end']
    for (dx, ang, L, wd, cv_) in ((0, 112, 34, 7, -0.2), (6, 96, 30, 6, -0.1), (-5, 128, 26, 5, -0.2)):
        tuft(fill, shade, line, je + np.array([X(dx), -4]), A(ang), L, wd, C(cv_))
    col = G_MID[None, None] * (1 - shade[..., None] * 0.5) + G_LIGHT[None, None] * shade[..., None] * 0.5
    # ひげ：鼻の横から 上・外へ出て、うしろへ曲がる 細い線（2本）
    wl = np.zeros_like(fill)
    nose = M['nose']
    for (sgn, L_, ang0, bend) in ((1, 48, 150, -1.9), (-1, 38, 125, -1.7)):
        a0 = math.radians(A(ang0))
        d = np.array([math.cos(a0), math.sin(a0)]); n = np.array([-d[1], d[0]])
        pts = [nose + np.array([X(-4), 4 + 4 * sgn]) + d * L_ * u + n * C(bend) * L_ * (u ** 2) * 0.55 + n * 2 * math.sin(6 * u) * u for u in np.linspace(0, 1, 30)]
        q = np.round(np.array(pts) * ss * 16).astype(np.int32)
        for i in range(len(q) - 1):
            wd = (4.6 - 3.6 * i / len(q)) * ss
            cv2.line(wl, tuple(q[i]), tuple(q[i + 1]), 1.0, max(1, int(round(wd))), cv2.LINE_AA, shift=4)
    return col, fill, line, wl


def rails_and_cartouche(ss=SS):
    """横木（上下）と、上下のまん中の飾り。塗り（色・alpha・線）"""
    Wd_, Hd_ = W * ss, Hh * ss
    col = np.zeros((Hd_, Wd_, 3), np.float32); fill = np.zeros((Hd_, Wd_), np.float32); line = np.zeros_like(fill)

    def bar(y0, y1, flip):
        """横木：外がわの太いふち（明るい）・内がわの段（中）・間の細い溝（かげ）"""
        bands = [(0.00, 0.30, G_LIGHT), (0.30, 0.42, G_DARK), (0.42, 0.72, G_MID), (0.72, 0.82, G_DARK), (0.82, 1.00, G_LIGHT)]
        if flip:
            bands = [(1 - b, 1 - a, c) for (a, b, c) in bands][::-1]
        for (a, b, c) in bands:
            ya, yb = int(round(y0 + (y1 - y0) * a)), int(round(y0 + (y1 - y0) * b))
            col[ya:yb, :] = c
            fill[ya:yb, :] = 1.0
        cv2.rectangle(line, (0, int(y0)), (Wd_ - 1, int(y1)), 1.0, int(1.4 * ss))

    bar(22 * ss, 46 * ss, False)
    bar(274 * ss, 298 * ss, True)

    def cartouche(cx, cy, up):
        """まん中の飾り：中心の玉・左右のうずまき（2段）・外へ広がる葉"""
        s = 1 if up else -1
        cx, cy = cx * ss, cy * ss
        # 葉（扇）
        for i, (ang, L, wd) in enumerate(((-90, 40, 12), (-118, 34, 10), (-62, 34, 10), (-146, 26, 9), (-34, 26, 9))):
            a = math.radians(ang)
            d = np.array([math.cos(a), math.sin(a) * s]); n = np.array([-d[1], d[0]])
            us = np.linspace(0, 1, 10)
            sp = [np.array([cx, cy]) + d * L * ss * u for u in us]
            wid = [wd * ss * (1 - u) ** 0.6 * (0.3 + 0.7 * smoothstep(0, 0.3, u)) for u in us]
            poly = np.array([sp[j] + n * wid[j] for j in range(10)] + [sp[j] - n * wid[j] for j in range(10)][::-1])
            q = np.round(poly * 16).astype(np.int32)
            cv2.fillPoly(fill, [q], 1.0, cv2.LINE_AA, shift=4)
            c3 = np.zeros((Hd_, Wd_), np.float32); cv2.fillPoly(c3, [q], 1.0, cv2.LINE_AA, shift=4)
            col[c3 > 0.5] = G_MID if i % 2 else G_LIGHT
            cv2.polylines(line, [q], True, 1.0, int(1.3 * ss), cv2.LINE_AA, shift=4)
        # うずまき（左右）
        for sx in (-1, 1):
            for (r, dxs, dys, thick) in ((12, 30, 2, 3.0), (8, 50, 9, 2.4)):
                c = (int(round(cx + sx * dxs * ss)), int(round(cy + dys * ss * s)))
                cv2.circle(fill, c, int(r * ss), 1.0, -1, cv2.LINE_AA)
                c3 = np.zeros((Hd_, Wd_), np.float32); cv2.circle(c3, c, int(r * ss), 1.0, -1, cv2.LINE_AA)
                col[c3 > 0.5] = G_MID
                cv2.circle(line, c, int(r * ss), 1.0, int(thick * ss * 0.5), cv2.LINE_AA)
                cv2.circle(line, c, int(r * ss * 0.45), 1.0, int(1.2 * ss), cv2.LINE_AA)
                c3 = np.zeros((Hd_, Wd_), np.float32); cv2.circle(c3, (c[0] - int(2 * ss * sx), c[1] - int(2 * ss * s)), int(r * ss * 0.55), 1.0, -1, cv2.LINE_AA)
                col[c3 > 0.5] = G_LIGHT
        # 中心の玉（赤）と金のふち
        c = (int(round(cx)), int(round(cy)))
        cv2.circle(fill, c, int(17 * ss), 1.0, -1, cv2.LINE_AA)
        c3 = np.zeros((Hd_, Wd_), np.float32); cv2.circle(c3, c, int(17 * ss), 1.0, -1, cv2.LINE_AA)
        col[c3 > 0.5] = G_LIGHT
        c3 = np.zeros((Hd_, Wd_), np.float32); cv2.circle(c3, c, int(12 * ss), 1.0, -1, cv2.LINE_AA)
        col[c3 > 0.5] = np.array([0.80, 0.12, 0.08])
        c3 = np.zeros((Hd_, Wd_), np.float32); cv2.circle(c3, (c[0] - int(4 * ss), c[1] - int(4 * ss)), int(4 * ss), 1.0, -1, cv2.LINE_AA)
        col[c3 > 0.5] = np.array([1.0, 0.75, 0.70])
        cv2.circle(line, c, int(17 * ss), 1.0, int(1.4 * ss), cv2.LINE_AA)
        cv2.circle(line, c, int(12 * ss), 1.0, int(1.2 * ss), cv2.LINE_AA)

    cartouche(W / 2, 34, True)
    cartouche(W / 2, 286, False)
    return col, fill, line


def frame(bg, rng, tmp):
    """bg：背景（sRGB 0〜1・780×320）。金の双龍の額縁をのせて返す"""
    R, M = render(tmp)
    ss = SS
    Hd_, Wd_ = Hh * ss, W * ss
    out = cv2.resize(bg.astype(np.float32), (Wd_, Hd_), interpolation=cv2.INTER_CUBIC)

    def over(dst, col, alpha):
        al = np.clip(alpha, 0, 1)[..., None]
        return dst * (1 - al) + col * al

    def lines(dst, line, strength=0.92):
        l = np.clip(line, 0, 1)[..., None] * strength
        return dst * (1 - l) + G_LINE * l

    # 横木と飾り（いちばん下）
    rc, rf, rl = rails_and_cartouche(ss)
    out = over(out, rc, rf)
    out = lines(out, rl)
    # 龍（右：そのまま／左：左右に返す）
    dense = M['spine']
    for flip in (False, True):
        col, a, edge, mid, hit = toon(R, flip)
        dn = dense.copy()
        if flip:
            dn[:, 0] = W - dn[:, 0]
        col = body_detail(col, edge, mid, hit, dn, ss)
        # 背びれ（体の下に）
        sc_col, sc_fill, sc_line = dorsal_spikes(dn, ss)
        out = over(out, sc_col, sc_fill)
        out = lines(out, sc_line)
        # 体
        out = over(out, col, a)
        out = lines(out, edge.astype(np.float32) * a)
        # たてがみ・あごひげ・ひげ（頭の上には出さない）
        Mm = dict(M)
        if flip:
            Mm = dict(M, hp=lambda s_, w_, z=0.0: np.array([W - M['hp'](s_, w_, z)[0], M['hp'](s_, w_, z)[1]]),
                      jaw_end=np.array([W - M['jaw_end'][0], M['jaw_end'][1]]), nose=np.array([W - M['nose'][0], M['nose'][1]]))
        mc, mf, ml, wl = mane(Mm, np.random.default_rng(7), ss, flip)
        headmask = np.isin(mid, HEAD_MATS) & hit
        headmask = cv2.dilate(headmask.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        keep = (~headmask).astype(np.float32)
        out = over(out, mc, mf * keep)
        out = lines(out, ml * keep)
        out = over(out, G_LIGHT[None, None] * np.ones_like(mc), wl * keep * 0.95)
        out = lines(out, cv2.dilate(wl, np.ones((3, 3), np.uint8)) * (1 - wl) * keep, 0.8)
        # 目：ひとみ
        for (ex, ey) in (M['eyes'] if not flip else [(W - e[0], e[1]) for e in M['eyes']]):
            if not hit[int(ey * ss), int(ex * ss)]:
                continue
            fwd = -1 if not flip else 1                                    # 鼻先の方（右の龍は左）
            c = (int(round((ex + 2.5 * fwd) * ss)), int(round((ey + 1.0) * ss)))
            cv2.ellipse(out, c, (int(2.4 * ss), int(5.0 * ss)), 0, 0, 360, (0.08, 0.03, 0.02), -1, cv2.LINE_AA)
            cv2.circle(out, (c[0] - int(1.4 * ss), c[1] - int(2.2 * ss)), int(1.2 * ss), (1.0, 1.0, 1.0), -1, cv2.LINE_AA)
    out = cv2.resize(out, (W, Hh), interpolation=cv2.INTER_AREA)
    return np.clip(out, 0, 1), M
