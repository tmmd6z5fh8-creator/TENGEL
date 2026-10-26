"""ノーマルど的中（第4.77版）：動画（30コマ/秒・780×1688・8.2秒・時刻は normal_do.py の FILM）。まさちゃんの 言葉は normal_do.py。
   - 送ってくれた 画像・動画は 色と 雰囲気・動きの 見本だけ。絵・形は すべて 一から 作る。
   - 上からの 場面（〜5.45秒）：世界（m）：地面は y＝0（芝：刈った すじ・黄みの ある 所）。光の 玉は (0, 1.2, 0)。カメラは 斜め 上から。
     馬（シルバーの 競走馬）と 騎手（金の 勝負服・白い そで）は 3D（horse3d・nd_horse の 騎手）を「馬から 見た カメラ」で 描く（かたむきの ぶんは 画面で もどす）。
     走りは nd_horse（玉の まん中から とびおりて 芝の うずまきを ギャロップ・ひづめは すべらない）。光は 玉の 点光源（影つき）＋ 照らされた 芝からの 照りかえし。
     たてがみ・しっぽは 銀の 毛。芝に 馬と 騎手の 影（玉の 光の 大きさで ぼける）・ひづめの あと（芝が けずれて 土）・金に 光る ひづめの あと・はねる 芝と 土。
   - 低い 目線の 場面（5.45秒〜）：芝から 45cm の カメラ。うしろに 大きな 光の 玉と 金の 輪・夜空・遠くの 木の かげ・芝の 葉（1本ずつ・玉の 光が すける）。
     3D の「ど！的中」（shiden_logo・！は 1つ）が 上から 落ちて 芝に ドーン → 足もとに 手前の 芝が かかる・芝に 字の 影・ふちに 玉の 光・まわりの 光・不定期な キラッ。
   python3 flat/normal_film.py <作業フォルダ> [はじめの コマ] [おわりの コマ]   （SCALE=0.5 で ためしの 小さい 絵）
   python3 flat/normal_film.py --encode <作業フォルダ> <出力.mp4>  /  --last <作業フォルダ> <出力.webp>"""
import os, sys, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
sys.path.insert(0, HERE)
from h3d import Scene, nrm
import horse3d as Hm
from hair2d import HairBuf
from paint import fbm, blur, smoothstep
import shiden_film as SF                          # 仕上げの 道具（bloom・finish・zoom_blur・save_png）
import shiden_logo as SL
import normal_do as ND
import nd_horse as NH

F = ND.FILM
FPS = F['FPS']
W0, H0 = F['W'], F['H']
W, H, S = SF.W, SF.H, SF.S
NF = int(round(F['END'] * FPS))
ss, grid, bloom, finish, zoom_blur = SF.ss, SF.grid, SF.bloom, SF.finish, SF.zoom_blur
TMP = os.environ.get('ND_TMP', '/tmp/nd_r')
os.makedirs(TMP, exist_ok=True)
f32 = np.float32

# ================================================================ 世界と カメラ
FOV = 50.0
O = NH.O                                          # 光の 玉の まん中（地面から 1.2m）
EYE = O + 20.0 * np.array([0.0, math.sin(math.radians(30)), math.cos(math.radians(30))])
TGT = np.array([0.0, 0.62, 0.0])
ORB_R = 0.42                                      # 玉の 半径（m）


def cam_axes(eye=EYE, tgt=TGT):
    fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
    return fw, rt, up


FW, RT, UP = cam_axes()
TH = math.tan(math.radians(FOV) * .5)


def project(P):
    """世界の 点 → 画面の px と 奥行き（カメラの 前向きの m）"""
    P = np.atleast_2d(np.asarray(P, float))
    d = P - EYE
    xc, yc, zc = d @ RT, d @ UP, d @ FW
    return np.stack([(xc / zc / (TH * W / H) + 1) * .5 * W, (1 - yc / zc / TH) * .5 * H], -1), zc


OC, OZ = project(O)
OC = OC[0]; OZ = float(OZ[0])
PX_M = H / (2 * OZ * TH)                          # 玉の 奥行きで 1m は 何 px


def px_per_m(z):
    return H / (2 * np.asarray(z, float) * TH)


def orb_px():
    return ORB_R * PX_M


# ================================================================ 時刻
T_BLACK = F['BLACK']
ORB0, ORB1 = F['ORB_IN']
RING0, RING1 = F['RINGS']
RUN0, RUN1 = F['RUN']
SW0, SW1 = F['SWELL']
T_BURST = F['BURST']
WH0, WH1 = F['WHITE']
LG0, LG1 = F['LOGO']
HOT0, HOT1 = F['HOT']
SWP0, SWP1 = F['SWEEP']
T_RES, T_END = F['RES'], F['END']
T_LAND = NH.T_LAND
H_END = WH0 + .12                                 # 馬は 光に つつまれて 見えなく なる


def orb_level(t):
    """玉の 明るさ・大きさ（0 → 1：光の 点 → 玉）"""
    return ss(ORB0, ORB1, t)


def swell(t):
    return ss(SW0, SW1, t)


ORB_COL = np.array([.80, 1.0, .70], f32)          # 玉の 光の 色（若草色の 白）
GOLD = np.array([2.4, 1.85, .75], f32)


def orb_I(t):
    """玉の 光の 強さ（地面・馬・砂けむり）"""
    return orb_level(t) * (1 + 1.8 * swell(t)) * (1 + .35 * math.exp(-max(t - RUN0, 0) / .12) * (t >= RUN0))


def irr(P, t):
    """玉の 光（向きを 問わない 受け手：砂けむり・とぶ 砂）"""
    d = np.linalg.norm(np.atleast_2d(P) - O, axis=-1)
    return orb_I(t) * 3.2 / (d ** 1.5 + .3)


# ================================================================ 地面（砂）：画面の 画素ごとの 地面の 場所（カメラは 動かない）
GEO = {}


def ground_geo():
    if not GEO:
        yy, xx = grid()
        nx = ((xx + .5) / W * 2 - 1) * TH * W / H
        ny = (1 - (yy + .5) / H * 2) * TH
        dxyz = [FW[i] + nx * RT[i] + ny * UP[i] for i in range(3)]
        tt = -EYE[1] / dxyz[1]                                                  # 画面は ぜんぶ 地平より 下
        GEO['X'] = (EYE[0] + dxyz[0] * tt).astype(f32)
        GEO['Z'] = (EYE[2] + dxyz[2] * tt).astype(f32)
        GEO['zc'] = tt.astype(f32)                                              # カメラの 前向きの 奥行き
        rl = np.sqrt(1 + nx * nx + ny * ny)
        GEO['cosf'] = (1 / rl).astype(f32)                                      # 光の 道の 長さ → 前向きの 奥行き
        GEO['foot'] = (tt * rl * 2 * TH / H / np.maximum(-dxyz[1] / rl, .05)).astype(f32)   # 1画素の 地面の 大きさ（m）
    return GEO


def _h2(i, j, sd):
    h = np.sin(i * 127.1 + j * 311.7 + sd * 74.7) * 43758.5453
    return h - np.floor(h)


def vnoise(X, Z, cell, sd):
    """世界に 固定の なめらかな ノイズ（0〜1）"""
    x = X / cell; z = Z / cell
    i = np.floor(x); j = np.floor(z)
    fx = x - i; fz = z - j
    ux = fx * fx * fx * (fx * (fx * 6 - 15) + 10); uz = fz * fz * fz * (fz * (fz * 6 - 15) + 10)
    a = _h2(i, j, sd); b = _h2(i + 1, j, sd); c = _h2(i, j + 1, sd); d = _h2(i + 1, j + 1, sd)
    return a + (b - a) * ux + (c - a) * uz + (a - b - c + d) * ux * uz


def turf(X, Z, foot):
    """芝（第4.77版：まさちゃん「芝の上に」）：世界に 固定の 色（albedo）と 凸凹の 向き（法線）。刈った すじ・黄みの ある 所・細かい 葉の もよう"""
    X = X.astype(np.float64); Z = Z.astype(np.float64); foot = foot.astype(np.float64)
    ow = lambda cell: np.clip((cell / np.maximum(foot, 1e-4) - 1.5) / 2.5, 0, 1)   # 画素より 細かい もようは 消す（ちらつかない）
    OCT = ((1.9, .012, 1), (.5, .006, 2), (.12, .003, 3), (.035, .0018, 4), (.012, .0009, 5))
    def hgt(x, z):
        return sum((vnoise(x, z, c, sd) - .5) * a * ow(c) for c, a, sd in OCT)
    e = .003
    h0 = hgt(X, Z)
    gx = (hgt(X + e, Z) - h0) / e
    gz = (hgt(X, Z + e) - h0) / e
    N = np.dstack([-gx, np.ones_like(gx), -gz])
    N /= np.linalg.norm(N, axis=2, keepdims=True)
    v1 = vnoise(X, Z, 3.0, 11); v2 = vnoise(X, Z, .6, 12); v3 = vnoise(X, Z, .11, 13); v4 = vnoise(X, Z, .028, 14); v5 = vnoise(X, Z, .009, 16)
    stripe = .5 + .5 * np.tanh(np.sin(np.pi * (X * .45 + Z) / 1.5) * 5)          # 刈った すじ（明るい 帯・暗い 帯）
    tone = (.84 + .3 * (v1 - .5) + .2 * (v2 - .5) * ow(.6) + .26 * (v3 - .5) * ow(.11) + .34 * (v4 - .5) * ow(.028) + .4 * (v5 - .5) * ow(.009)) * (.84 + .24 * stripe)
    yel = np.clip((vnoise(X, Z, 1.3, 15) - .45) * 2.2, 0, 1)                      # 黄みの ある 所
    g0, g1 = np.array([.040, .098, .024]), np.array([.072, .108, .030])
    alb = (g0[None, None] * (1 - yel[..., None]) + g1[None, None] * yel[..., None]) * tone[..., None]
    return alb.astype(f32), N.astype(f32)


def ground_tex():
    """芝の 色と 凸凹（上からの 場面）：一度 作って TMP に のこす"""
    g = ground_geo()
    if 'alb' in g:
        return g
    fn = os.path.join(TMP, f'ndturf_{W}x{H}_v1.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        g['alb'], g['N'] = z['alb'], z['N']
        return g
    g['alb'], g['N'] = turf(g['X'], g['Z'], g['foot'])
    tmp = fn[:-4] + f'_{os.getpid()}.npz'
    np.savez(tmp, alb=g['alb'], N=g['N'])
    os.replace(tmp, fn)
    return g


SOIL = np.array([.055, .040, .028], f32)          # 芝の 下の 土


KG = 6.0                                          # 地面の 光の 強さ
AMB = np.array([.018, .023, .028], f32)           # 夜空の うすい 光（月）


def ground_E(t, X, Z, N):
    """玉の 光（地面）：やわらかく 弱く なる（遠くも 少し 見える）"""
    lx, ly, lz = O[0] - X, O[1] - 0.0, O[2] - Z
    d = np.sqrt(lx * lx + ly * ly + lz * lz)
    ndl = (N[..., 0] * lx + N[..., 1] * ly + N[..., 2] * lz) / d
    return orb_I(t) * KG * np.maximum(ndl, 0) ** .7 / (d ** 1.3 + .3)


# ---------------------------------------------------------------- 影（玉の 光：馬と 騎手を 線分の かたまりで）
SH_MAX = 2.4                                      # 影を 描く 長さ（馬から m：遠くは うすく）


def _seg_dist(P0, P1, Q0, Q1):
    """線分 P（N 本）と 線分 Q（M 本）の いちばん 近い きょり と P の 上の 位置（0〜1）"""
    d1 = P1 - P0; d2 = Q1 - Q0
    r = P0[:, None] - Q0[None]
    a = (d1 * d1).sum(-1)[:, None]
    e = (d2 * d2).sum(-1)[None] + 1e-12
    f = (d2[None] * r).sum(-1)
    c = (d1[:, None] * r).sum(-1)
    b = (d1[:, None] * d2[None]).sum(-1)
    den = a * e - b * b
    s = np.where(den > 1e-12, np.clip((b * f - c * e) / np.maximum(den, 1e-12), 0, 1), 0.0)
    tq = (b * s + f) / e
    s = np.where(tq < 0, np.clip(-c / a, 0, 1), np.where(tq > 1, np.clip((b - c) / a, 0, 1), s))
    tq = np.clip((b * s + f) / e, 0, 1)
    p = P0[:, None] + d1[:, None] * s[..., None]
    q = Q0[None] + d2[None] * tq[..., None]
    return np.linalg.norm(p - q, axis=-1), s


def shadow_region(caps, P):
    """影が 落ちる 画面の 箱"""
    pts = []
    for a, b, r in caps:
        for q in (a, b):
            pts.append([q[0], 0.0, q[2]])
            if q[1] < O[1] - .05:
                sp = O + (q - O) * (O[1] / (O[1] - q[1]))
            else:
                dv = np.array([q[0] - O[0], 0.0, q[2] - O[2]])
                sp = P + dv / (np.linalg.norm(dv) + 1e-9) * SH_MAX
            dv = sp - P
            L_ = np.linalg.norm(dv)
            if L_ > SH_MAX:
                sp = P + dv / L_ * SH_MAX
            pts.append([sp[0], 0.0, sp[2]])
    q, z = project(np.array(pts))
    pad = 6
    x0, y0 = int(max(0, q[:, 0].min() - pad)), int(max(0, q[:, 1].min() - pad))
    x1, y1 = int(min(W, q[:, 0].max() + pad)), int(min(H, q[:, 1].max() + pad))
    return x0, y0, x1, y1


def horse_shadow(caps, P, box):
    """箱の 中の 地面の 光の 通り（1＝影なし）：玉は 半径 ORB_R の 光（影の ふちが ぼける）"""
    x0, y0, x1, y1 = box
    g = ground_geo()
    X, Z = g['X'][y0:y1, x0:x1].ravel(), g['Z'][y0:y1, x0:x1].ravel()
    G = np.stack([X, np.zeros_like(X), Z], 1).astype(np.float64)
    A = np.array([c[0] for c in caps]); B = np.array([c[1] for c in caps]); R_ = np.array([c[2] for c in caps])
    vis = np.ones(len(G))
    for k in range(0, len(G), 16000):
        Gk = G[k:k + 16000]
        dd, sk = _seg_dist(Gk, np.broadcast_to(O, Gk.shape), A, B)
        cl = np.maximum(ORB_R * sk, 1e-3)                                              # その 所での 光の 広がり
        occ = np.clip((R_[None] + cl - dd) / (2 * cl), 0, 1) * np.minimum(1.0, 1.6 * R_[None] / cl)
        vis[k:k + 16000] = np.prod(1 - occ * .92, axis=1)
    dist = np.hypot(X - P[0], Z - P[2])
    vis = 1 - (1 - vis) * np.clip((SH_MAX - dist) / (SH_MAX * .4), 0, 1)
    return vis.reshape(y1 - y0, x1 - x0).astype(f32)


# ---------------------------------------------------------------- ひづめの あと・金の あと・砂けむり・とぶ 砂（時刻は nd_horse の events）
EV = []


def events():
    if not EV:
        for e in NH.events(H_END + .2):
            fr = NH.frame_at(e[0])
            EV.append(dict(t=e[0], leg=e[1], kind=e[2], p=np.asarray(e[3], float), h=fr['Rm'][:, 0].copy(), side=np.cross(fr['Rm'][:, 0], (0, 1, 0))))
    return EV


def prints_apply(t, N, alb, box_all):
    """ひづめの あと（芝が けずれた くぼみ＋ うしろへ けった 土）：法線と 色を その 場所だけ かえる。box_all＝(x0, y0) の ずれ"""
    g = ground_geo()
    sc = NH.S_H / 0.5
    for e in events():
        if e['kind'] != 'td' or e['t'] > t:
            continue
        hv = e['h']; c = e['p'] - hv * .06 * sc
        rr = .12 * sc
        q, z = project(np.array([[c[0] - rr, 0, c[2] - rr], [c[0] + rr, 0, c[2] + rr], [c[0] - rr, 0, c[2] + rr], [c[0] + rr, 0, c[2] - rr]]))
        x0, y0 = int(max(0, q[:, 0].min() - 2)), int(max(0, q[:, 1].min() - 2))
        x1, y1 = int(min(W, q[:, 0].max() + 3)), int(min(H, q[:, 1].max() + 3))
        if x1 <= x0 or y1 <= y0:
            continue
        X, Z = g['X'][y0:y1, x0:x1], g['Z'][y0:y1, x0:x1]
        age = min((t - e['t']) / .06, 1.0)
        dx, dz = X - c[0], Z - c[2]
        sg = .034 * sc
        dent = -.011 * sc * age * np.exp(-(dx * dx + dz * dz) / (sg * sg))
        mx, mz = dx + hv[0] * .07 * sc, dz + hv[2] * .07 * sc
        sm = .05 * sc
        mound = .005 * sc * age * np.exp(-(mx * mx + mz * mz) / (sm * sm))
        hx = dent * (-2 * dx / (sg * sg)) + mound * (-2 * mx / (sm * sm))
        hz = dent * (-2 * dz / (sg * sg)) + mound * (-2 * mz / (sm * sm))
        n = N[y0:y1, x0:x1]
        nn = np.dstack([n[..., 0] - hx, n[..., 1], n[..., 2] - hz])
        N[y0:y1, x0:x1] = nn / np.linalg.norm(nn, axis=2, keepdims=True)
        k = np.clip(-dent / (.011 * sc) * 1.3, 0, 1)[..., None]                    # 芝が けずれて 土が 見える
        alb[y0:y1, x0:x1] = alb[y0:y1, x0:x1] * (1 - k) + SOIL * k


def gold_marks(t):
    """金に 光る ひづめの あと・広がる 光の 輪（着く とき）・着地の 大きな 光の 輪 → 地面の 光（線形）"""
    g = ground_geo()
    out = np.zeros((H, W), f32)
    sc = NH.S_H / 0.5
    items = [(e['t'], e['p'] - e['h'] * .06 * sc, 1.0) for e in events() if e['kind'] == 'td' and 0 <= t - e['t'] < .7]
    if 0 <= t - T_LAND < 1.2:
        items.append((T_LAND, NH.frame_at(T_LAND)['P'], 3.0))
    for t0, c, big in items:
        a = t - t0
        if big > 1:
            R_ = 1.9 * (1 - math.exp(-a / .25)); wd = .04 + .12 * a; I = 1.3 * math.exp(-a / .22)
            core = 1.2 * math.exp(-a / .18); cr = .45
        else:
            R_ = .03 + .35 * a ** .8; wd = .01 + .02 * a; I = .28 * math.exp(-a / .12)
            core = .8 * math.exp(-a / .25); cr = .04 * sc
        rr = R_ + 3 * wd + cr
        q, z = project(np.array([[c[0] - rr, 0, c[2] - rr], [c[0] + rr, 0, c[2] + rr], [c[0] - rr, 0, c[2] + rr], [c[0] + rr, 0, c[2] - rr]]))
        x0, y0 = int(max(0, q[:, 0].min() - 2)), int(max(0, q[:, 1].min() - 2))
        x1, y1 = int(min(W, q[:, 0].max() + 3)), int(min(H, q[:, 1].max() + 3))
        if x1 <= x0 or y1 <= y0:
            continue
        X, Z = g['X'][y0:y1, x0:x1], g['Z'][y0:y1, x0:x1]
        d = np.hypot(X - c[0], Z - c[2])
        out[y0:y1, x0:x1] += I * np.exp(-((d - R_) / wd) ** 2) + core * np.exp(-(d / cr) ** 2)
    return out


def trail_marks(t):
    """馬の 通った あと（地面）：金の 光の すじ（うしろ 1秒ぶん・だんだん 消える）"""
    if t < T_LAND:
        return None
    m = np.zeros((H, W), f32)
    ts = np.linspace(max(T_LAND, t - 1.0), t, 70)
    P = np.array([NH.frame_at(x)['P'] for x in ts])
    q, z = project(P)
    for i in range(len(P) - 1):
        k = ((i + 1) / (len(P) - 1)) ** 1.8
        w = max(1, int(round((1.0 + 3.0 * k) * S * (OZ / z[i]))))
        cv2.line(m, (int(q[i][0] * 16), int(q[i][1] * 16)), (int(q[i + 1][0] * 16), int(q[i + 1][1] * 16)), float(k), w, cv2.LINE_AA, shift=4)
    m *= 1 - ss(T_BURST - .05, T_BURST + .1, t)
    return m


def ground_layer(t, st=None, caps=None):
    """地面の 色（線形）と 奥行き"""
    g = ground_tex()
    N, alb = g['N'], g['alb']
    if any(e['kind'] == 'td' and e['t'] <= t for e in events()):
        N = N.copy(); alb = alb.copy()
        prints_apply(t, N, alb, (0, 0))
    E = ground_E(t, g['X'], g['Z'], N)
    if caps is not None:
        box = shadow_region(caps, st['P'] if st is not None else np.zeros(3))
        x0, y0, x1, y1 = box
        if x1 > x0 and y1 > y0:
            E[y0:y1, x0:x1] *= horse_shadow(caps, st['P'], box)
    col = alb * (E[..., None] * ORB_COL + AMB)
    gm = gold_marks(t)
    tr = trail_marks(t)
    em = gm if tr is None else gm + tr * .55
    col = col + em[..., None] * GOLD * .55 + blur(em, 3 * S)[..., None] * GOLD * .25
    return col.astype(f32)


# ---------------------------------------------------------------- 砂けむり（やわらかい もこもこ）・とぶ 砂（小さな 粒）
PUFFS, CLODS = [], []


def dust_lists():
    if PUFFS:
        return
    rng = np.random.default_rng(5)
    sc = NH.S_H / 0.5
    up = np.array([0.0, 1.0, 0.0])
    for e in events():
        hv, sd = e['h'], e['side']
        if e['kind'] == 'lo':                                                      # ける ときの 砂けむり・とぶ 砂
            PUFFS.append(dict(t0=e['t'], p=e['p'] - hv * .03, v=-hv * .55 + up * .28 + rng.normal(0, .06, 3), r0=.03 * sc, r1=.17 * sc, a=.14, life=.6))
            for k in range(9):                                                     # けられた 芝と 土の かたまり
                v = -hv * rng.uniform(.9, 2.6) + up * rng.uniform(.8, 2.0) + sd * rng.normal(0, .45)
                CLODS.append(dict(t0=e['t'], p=e['p'] + up * .01, v=v * sc ** .5, r=rng.uniform(.004, .011) * sc, b=rng.uniform(.6, 1.2), g=rng.random() < .5))
        else:                                                                      # 着く ときの 小さな ほこり
            PUFFS.append(dict(t0=e['t'], p=e['p'].copy(), v=up * .15 + rng.normal(0, .05, 3), r0=.02 * sc, r1=.09 * sc, a=.08, life=.45))
    P0 = NH.frame_at(T_LAND)['P']
    for k in range(12):                                                            # 着地：まわりへ 大きな 砂けむり・砂の 粒
        ang = 2 * math.pi * k / 12 + rng.uniform(-.2, .2)
        dv = np.array([math.cos(ang), 0.0, math.sin(ang)])
        PUFFS.append(dict(t0=T_LAND, p=P0 + dv * .12, v=dv * rng.uniform(.8, 1.4) + up * .3, r0=.08, r1=.38, a=.2, life=1.0))
    for k in range(46):
        ang = rng.uniform(0, 2 * math.pi)
        dv = np.array([math.cos(ang), 0.0, math.sin(ang)])
        CLODS.append(dict(t0=T_LAND, p=P0 + dv * .1 + up * .01, v=dv * rng.uniform(.8, 2.6) + up * rng.uniform(1.0, 2.6), r=rng.uniform(.005, .014), b=rng.uniform(.6, 1.2), g=rng.random() < .5))


def puff_state(p_, t):
    a = t - p_['t0']
    if a < 0 or a > p_['life']:
        return None
    pos = p_['p'] + p_['v'] * .45 * (1 - math.exp(-a / .45))
    r = p_['r0'] + (p_['r1'] - p_['r0']) * (1 - math.exp(-a / .28))
    al = p_['a'] * ss(0, .05, a) * (1 - ss(p_['life'] * .35, p_['life'], a))
    return pos, r, al


def dust_layer(t, img, zref, front):
    """砂けむりと とぶ 砂を img に 重ねる（front＝馬より 手前の もの・うしろの もの）。zref＝馬の 奥行き（なし＝全部 うしろ）"""
    dust_lists()
    T_ = tex()
    yy, xx = grid()
    lvl = orb_I(t)
    if lvl <= 0:
        return img
    for p_ in PUFFS:
        r_ = puff_state(p_, t)
        if r_ is None:
            continue
        pos, rad, al = r_
        q, z = project(pos)
        z = float(z[0])
        if (zref is not None and (z < zref) != front) or (zref is None and front):
            continue
        rp = rad * float(px_per_m(z))
        if rp < .6:
            continue
        cx, cy = q[0]
        x0, y0 = int(max(0, cx - 2.6 * rp)), int(max(0, cy - 2.6 * rp))
        x1, y1 = int(min(W, cx + 2.6 * rp + 1)), int(min(H, cy + 2.6 * rp + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        dx, dy = (xx[y0:y1, x0:x1] - cx) / rp, (yy[y0:y1, x0:x1] - cy) / rp
        n = sample(T_['n2'], dx * .35 + p_['t0'] * 3.1, dy * .35 + (t - p_['t0']) * .4)
        m = np.exp(-(dx * dx + dy * dy) * .55) * (.55 + .9 * n) * al
        vdir = nrm(pos - EYE); ldir = nrm(O - pos)
        fwd = 1 + 2.2 * max(0.0, float(vdir @ ldir)) ** 4                         # 玉の 光を うしろから 受けると 明るく ひかる
        c = np.array([.22, .25, .15], f32) * float(irr(pos, t)[0]) * fwd * ORB_COL + AMB * 2
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - m[..., None]) + c * m[..., None]
    for c_ in CLODS:
        a = t - c_['t0']
        if a < 0:
            continue
        v = c_['v']
        th_ = (v[1] + math.sqrt(v[1] ** 2 + 2 * 9.8 * max(c_['p'][1], 0))) / 9.8     # 地面に 落ちる まで
        def at(x):
            x = min(max(x, 0.0), th_)
            return c_['p'] + v * x + np.array([0.0, -4.9 * x * x, 0.0])
        if a > th_ + .35:
            continue
        al = 1.0 if a <= th_ else 1 - (a - th_) / .35
        p1, p0 = at(a), at(a - 1 / 60)
        q, z = project(np.array([p1, p0]))
        z0 = float(z[0])
        if (zref is not None and (z0 < zref) != front) or (zref is None and front):
            continue
        rp = max(.5, c_['r'] * float(px_per_m(z0)))
        c = (np.array([.06, .14, .04], f32) if c_['g'] else np.array([.20, .15, .10], f32)) * float(irr(p1, t)[0]) * c_['b'] * ORB_COL * 1.6 + AMB
        lay = np.zeros((H, W), f32)
        cv2.line(lay, (int(q[1][0] * 16), int(q[1][1] * 16)), (int(q[0][0] * 16), int(q[0][1] * 16)), 1.0, max(1, int(round(rp * 1.6))), cv2.LINE_AA, shift=4)
        x0, y0 = int(max(0, min(q[:, 0]) - rp - 3)), int(max(0, min(q[:, 1]) - rp - 3))
        x1, y1 = int(min(W, max(q[:, 0]) + rp + 4)), int(min(H, max(q[:, 1]) + rp + 4))
        if x1 > x0 and y1 > y0:
            m = lay[y0:y1, x0:x1] * al
            img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - m[..., None]) + c * m[..., None]
    return img


# ================================================================ 馬と 騎手（3D）：馬から 見た カメラで 描く
def _lin(hx):
    hx = hx.lstrip('#')
    return tuple((int(hx[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4))


COAT = _lin('#C3C7CE')                            # シルバー（銀色の 毛：つやで 光る）
SILK, SLEEVE, HELMET = _lin('#E7B03A'), _lin('#F3F3EF'), _lin('#E7B03A')
HAIR = np.array([.50, .52, .56], f32)             # 銀の たてがみ・しっぽ


def _mats(sc):
    sc.mat(NH.M_COAT, 1, COAT, 0.27, 0.55, 0.16, 4.0)
    sc.mat(NH.M_EYE, 1, (0.004, 0.003, 0.003), 0.06, 0.0, 0.0, 0.0)
    sc.mat(NH.M_HOOF, 1, (0.035, 0.033, 0.032), 0.4, 0.2, 0.0, 0.0)
    sc.mat(NH.M_SILK, 1, SILK, 0.30, 0.35, 0.35, 3.0)
    sc.mat(NH.M_SLEEVE, 1, SLEEVE, 0.32, 0.35, 0.30, 3.0)
    sc.mat(NH.M_HELMET, 1, HELMET, 0.16, 0.35, 0.10, 3.0)
    sc.mat(NH.M_PANTS, 1, (0.66, 0.66, 0.68), 0.6, 0.25, 0.10, 3.0)
    sc.mat(NH.M_BOOT, 1, (0.012, 0.012, 0.014), 0.3, 0.30, 0.05, 3.0)
    sc.mat(NH.M_CLOTH, 1, (0.72, 0.72, 0.74), 0.75, 0.2, 0.0, 3.0)
    sc.mat(NH.M_SADDLE, 1, (0.02, 0.016, 0.014), 0.4, 0.3, 0.05, 3.0)
    sc.mat(NH.M_GOGGLE, 1, (0.02, 0.02, 0.03), 0.08, 0.5, 0.0, 3.0)


def _tail_strands(st, S, sc3, t, rng):
    """しっぽ（3D の 毛の 束を 写す）：根元から うしろ・少し 下へ 流れ、走りに 合わせて 上下・左右に 波うつ。もとの 点は 毛の 束ごと"""
    s_ = st['s']
    Rm = st['Rm']
    hv = Rm[:, 0]; upv = Rm[:, 1]; sdv = Rm[:, 2]
    ta = S['tail_pts']
    root = NH.to_world(st, [ta[2][0], ta[2][1], 0.0])
    g = st['g']
    locks = []
    L_tail = 1.15 * s_                                                             # しっぽの 長さ（m）
    for k in range(18):
        a0 = rng.uniform(-1, 1); b0 = rng.uniform(-1, 1)
        L_ = L_tail * rng.uniform(.7, 1.08)
        n = 16
        pts = []
        for i in range(n + 1):
            u = i / n
            wave = math.sin(2 * math.pi * (g * 1.0 - u * .9) + k * .4)
            wav2 = math.sin(2 * math.pi * (g * 1.0 - u * .7) + 1.3 + k * .25)
            back = u * L_
            drop = (.10 + .30 * u * u) * L_ * u - .12 * L_ * math.sin(2 * math.pi * (g - .15)) * u * u
            lat = (.05 * a0 * u + .07 * wave * u * u) * L_
            vrt = (.04 * b0 * u + .05 * wav2 * u * u) * L_
            spread = (.06 + .28 * u) * L_tail
            p = root - hv * back - upv * (drop - vrt) + sdv * (lat + a0 * spread * .35 * u) + upv * b0 * spread * .25 * u
            pts.append(p)
        locks.append(np.array(pts))
    return locks


def horse_sample(t, seed=41):
    """1つの 時刻の 馬と 騎手：色（線形・すき通しを かけた もの）・すき通し・奥行き（カメラの 前向きの m）・その ほか"""
    st = NH.state(t)
    B, Rm, s_ = st['B'], st['Rm'], st['s']
    Lref = NH.LREF
    to_l = lambda q: Lref + Rm.T @ (np.asarray(q, float) - B) / s_
    eye_l, tgt_l = to_l(EYE), to_l(TGT)
    c2, cz = project(B)
    rad = 1.9 * s_ * H / (2 * float(cz[0]) * TH)
    wx0, wy0 = c2[0][0] - rad, c2[0][1] - rad * 1.1
    wx1, wy1 = c2[0][0] + rad, c2[0][1] + rad * .9
    if wx1 < 0 or wy1 < 0 or wx0 > W or wy0 > H:
        return None
    # 馬が かたむく（ロール）と、馬から 見た カメラの 絵は 画面の まん中を 軸に まわる（sdfr の カメラは 上を y に とる）→ 描いた あと もどす（Mw）
    fw_l = nrm(tgt_l - eye_l); rt_l = nrm(np.cross(fw_l, (0, 1, 0))); up_l = np.cross(rt_l, fw_l)
    def proj_l(Q):
        d = np.atleast_2d(np.asarray(Q, float)) - eye_l
        xc, yc, zc_ = d @ rt_l, d @ up_l, d @ fw_l
        return np.stack([(xc / zc_ / (TH * W / H) + 1) * .5 * W, (1 - yc / zc_ / TH) * .5 * H], -1)
    lq = [Lref + np.array(v) for v in ((0, 0, 0), (.8, 0, 0), (0, .8, 0), (0, 0, .8), (.6, .6, .6))]
    Mw = cv2.estimateAffinePartial2D(proj_l(lq).astype(f32), project(np.array([NH.to_world(st, q) for q in lq]))[0].astype(f32))[0]
    Mi = cv2.invertAffineTransform(Mw)
    cs = np.array([[wx0, wy0], [wx1, wy0], [wx0, wy1], [wx1, wy1]], f32)
    lc = cs @ Mi[:, :2].T + Mi[:, 2]
    x0, y0 = int(max(0, lc[:, 0].min())), int(max(0, lc[:, 1].min()))
    x1, y1 = int(min(W, lc[:, 0].max())), int(min(H, lc[:, 1].max()))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    sc = Scene()
    sc.image(W, H, 2, (x0, y0, x1, y1))
    sc.camera(eye_l, tgt_l, FOV)
    sc.bounce(0)
    sc.env((0.010, 0.014, 0.012), (0.008, 0.011, 0.008), (0.012, 0.012, 0.009), (0.004, 0.005, 0.004))
    lv = orb_I(t)
    ol = to_l(O)
    dO = max(np.linalg.norm(B - O), .5)
    sc.plight(ol, tuple(np.array([9.0, 10.5, 7.5]) * lv * dO ** .6 / (s_ * s_)), 6, 1)    # 玉（影つき：玉の 大きさで ぼける）
    gE = float(ground_E(t, np.array([st['P'][0]]), np.array([st['P'][2]]), np.array([[0.0, 1.0, 0.0]]))[0])
    sc.light(nrm(Rm.T @ np.array([0.0, -1.0, 0.0])), tuple(np.array([.20, .17, .12]) * ORB_COL * gE * 1.1), 10, 0)   # 照らされた 砂からの 照りかえし（下から）
    sc.light(nrm(Rm.T @ (-FW + np.array([0.0, .9, 0.0]))), (0.11, 0.13, 0.16), 10, 0)                              # 夜空の うすい 光
    kr = ss(RING0, RING0 + .35, t) * (1 - ss(T_BURST, T_BURST + .12, t))
    sc.light(nrm(Rm.T @ (-FW * .5 + np.array([0.0, 1.0, 0.0]))), tuple(np.array([.40, .32, .13]) * kr), 10, 0)      # 金の 輪の 光（上・手前から）
    _mats(sc)
    S3, J = NH.build_racer(sc, st)
    R = sc.render(os.path.join(TMP, f'h{os.getpid()}'))
    P = lambda pts: project(np.array([NH.to_world(st, q) for q in np.atleast_2d(np.asarray(pts, float))]))[0]   # 馬の 中の 点 → 画面
    rgb, A, D = R['rgb'], np.clip(R['a'], 0, 1), R['d']
    if R['a'].shape[0] == H:
        rgb, A, D = rgb[y0:y1, x0:x1], A[y0:y1, x0:x1], D[y0:y1, x0:x1]
        M = np.round(R['m'][y0:y1, x0:x1]).astype(int)
    else:
        M = np.round(R['m']).astype(int)
    # 足先を 少し こい 灰色に（銀の 馬：ひざ・飛節の 下 → ひづめ）：馬から 見た カメラの 画素の 3D の 場所で
    yy_, xx_ = np.mgrid[y0:y1, x0:x1].astype(f32)
    nx = ((xx_ + .5) / W * 2 - 1) * TH * W / H; ny = (1 - (yy_ + .5) / H * 2) * TH
    rd = fw_l[None, None] + rt_l[None, None] * nx[..., None] + up_l[None, None] * ny[..., None]
    rl = np.linalg.norm(rd, axis=2)
    rd /= rl[..., None]
    Pl = eye_l[None, None] + rd * D[..., None]
    near = np.zeros(A.shape, f32)
    dzs = st['pose'].get('leg_dz', {})
    for k, top in (('FL', 'kn'), ('FR', 'kn'), ('HL', 'hk'), ('HR', 'hk')):
        Fk = S3[k]
        dz = dzs.get(k, 0.0)
        zz = (0.1395 if k[0] == 'F' else 0.145) * Fk['z']
        q0 = np.array([*(np.asarray(Fk[top]) + (np.asarray(Fk['ft']) - np.asarray(Fk[top])) * .1), zz + dz * .5])
        q1 = np.array([*np.asarray(Fk['hf']), zz + dz])
        dv = q1 - q0
        tt = np.clip(((Pl - q0) * dv).sum(-1) / (dv @ dv), 0, 1)
        dist = np.linalg.norm(Pl - (q0 + tt[..., None] * dv), axis=-1)
        near = np.maximum(near, np.clip((.11 - dist) / .03, 0, 1) * (.35 + .65 * tt))
    coat = (M == NH.M_COAT).astype(f32) * near * .55
    rgb = rgb * (1 - coat[..., None] * .7)
    zl = np.where(A > .01, D * s_ / rl, 1e9).astype(f32)                         # カメラの 前向きの 奥行き（世界 m）
    colL = np.zeros((H, W, 3), f32); AL = np.zeros((H, W), f32); DL = np.full((H, W), 1e9, f32)
    colL[y0:y1, x0:x1] = rgb * A[..., None]
    AL[y0:y1, x0:x1] = A
    DL[y0:y1, x0:x1] = zl
    col = cv2.warpAffine(colL, Mw, (W, H), flags=cv2.INTER_LINEAR)
    Af = cv2.warpAffine(AL, Mw, (W, H), flags=cv2.INTER_LINEAR)
    Df = cv2.warpAffine(DL, Mw, (W, H), flags=cv2.INTER_NEAREST, borderValue=1e9)
    x0, y0, x1, y1 = int(max(0, wx0)), int(max(0, wy0)), int(min(W, wx1)), int(min(H, wy1))
    # ---- たてがみ・前髪（銀の 毛：走る 向きと 反対へ なびく）・しっぽ（3D の 毛の 束）
    rng = np.random.default_rng(seed)
    hb = HairBuf(H, W, ss=2)
    sz = rad / 120.0
    sv = project(B + Rm[:, 0] * .3)[0][0] - c2[0]
    back = -sv / (np.linalg.norm(sv) + 1e-6)
    ba = math.atan2(back[1], back[0])
    ts = np.linspace(0, 1, 40)
    crest = P(np.c_[Hm.bez(S3['crest'], ts), np.zeros(len(ts))])
    throat = P(np.c_[Hm.bez(S3['throat'], ts), np.zeros(len(ts))])
    nC = len(crest)
    from hair2d import guide
    for i in range(4, nC - 4, 2):                                                     # たてがみ：首に そって うしろへ 寝る 短い 毛（風で 少し 立つ）
        q = crest[i]
        tg = crest[i - 2] - crest[min(i + 2, nC - 1)]
        tg = tg / (np.linalg.norm(tg) + 1e-6)
        upn = np.array([-tg[1], tg[0]])
        if upn @ (q - throat[i]) < 0:
            upn = -upn
        dv = tg * math.cos(.45) + upn * math.sin(.45)
        ang = math.atan2(dv[1], dv[0]) + .12 * math.sin(i * .9 + st['g'] * 6.28)
        L_ = (5.5 + 3.5 * math.sin(i / nC * math.pi)) * sz
        gg = guide(q, ang, L_, 6, rng, lambda x, y, aa, tt_: 0.0, wave=.6, phase=i + st['g'] * 6)
        hb.lock(gg, 6, rng, spread=.8 * sz, clump=0.7, wmin=0.3, wmax=0.6, rimk=1.0)
    locks = _tail_strands(st, S3, sc, t, rng)
    for Lk in locks:                                                                  # しっぽ：細い 毛の 束（根元は まとまり・先は 広がる）
        q2 = project(Lk)[0]
        hb.lock(q2, 7, rng, spread=1.0 * sz, clump=0.5, wmin=0.25, wmax=0.6, rimk=1.4, tip_frac=(0.7, 1.0))
    cov, rimw, cnt = hb.result(k=0.5)
    # 毛の 色：銀（玉の 光の 強さ・ふちの 光）・こい 所ほど 少し 暗い
    lvh = float(irr(B, t)[0])
    hair = HAIR * (.05 + .38 * lvh) * ORB_COL + np.clip(rimw, 0, 1.6)[..., None] * ORB_COL * (.2 + .7 * lvh) * .45
    hair = hair * (1.0 - .35 * np.clip(cnt / (cnt.max() + 1e-6) * 2, 0, 1))[..., None]
    col = col * (1 - cov[..., None]) + hair * cov[..., None]
    Af = np.clip(Af + cov * (1 - Af), 0, 1)
    zt = float(project(locks[0][0])[1][0])
    Df = np.where((cov > .05) & (Df > 1e8), zt, Df)
    # ---- 頭の ベルト・手綱（こげ茶の 革）
    tack = np.zeros((H, W), f32)
    mz = P([Hm.head_pt(S3, 0.56, -0.03)])[0]
    mo = P([Hm.head_pt(S3, 0.50, -0.10, 0.05)])[0]
    po = P([Hm.v3(S3['poll'])])[0]
    hnd = P([J['hand1']])[0]
    mid = (mo + hnd) / 2 + np.array([0.0, 3.0 * sz])
    pts = [(1 - u) ** 2 * mo + 2 * (1 - u) * u * mid + u ** 2 * hnd for u in np.linspace(0, 1, 12)]
    cv2.polylines(tack, [(np.asarray(pts) * 16).astype(np.int32)], False, 1.0, max(1, int(round(1.2 * sz))), cv2.LINE_AA, shift=4)
    cv2.polylines(tack, [(np.asarray([mo, (mo + po) / 2, po]) * 16).astype(np.int32)], False, 1.0, max(1, int(round(1.0 * sz))), cv2.LINE_AA, shift=4)
    tack *= .85
    col = col * (1 - tack[..., None]) + np.array([.03, .02, .015], f32) * lvh * tack[..., None]
    Af = np.clip(Af + tack * (1 - Af), 0, 1)
    return dict(col=col, A=Af, D=Df, st=st, S=S3, J=J, box=(x0, y0, x1, y1))


def horse_layer(t):
    """馬と 騎手（3つの 時刻を 重ねて 動きの ぶれ：ひづめが 地面に 着いて いる 所は ぶれない）"""
    if not RUN0 <= t <= H_END:
        return None
    k = 1 / (3 * FPS)
    sm = [horse_sample(min(max(t + o, RUN0), H_END)) for o in (-k, 0.0, k)]
    sm = [x for x in sm if x is not None]
    if not sm:
        return None
    c = sum(x['col'] for x in sm) / len(sm)
    a = sum(x['A'] for x in sm) / len(sm)
    mid = sm[len(sm) // 2]
    D = np.minimum.reduce([x['D'] for x in sm])
    return dict(col=c, A=a, D=D, st=mid['st'], S=mid['S'], J=mid['J'])


# ================================================================ 光の 玉・輪・粒・光の 筋
TEX = {}


def tex():
    if not TEX:
        rng = np.random.default_rng(7)
        for k, (sc_, oc) in (('n1', (40, 5)), ('n2', (14, 4))):
            n = fbm(256, 256, sc_, oc, seed=31 + len(TEX))
            TEX[k] = ((n - n.min()) / (n.max() - n.min() + 1e-6)).astype(f32)
        TEX['bokeh'] = [dict(x=rng.uniform(-.1, 1.1), y=rng.uniform(-.05, 1.05), r=rng.uniform(14, 52), a=rng.uniform(.05, .16),
                             vx=rng.uniform(-6, 6), vy=rng.uniform(-10, -2), ph=rng.uniform(0, 6.28)) for i in range(18)]
        TEX['pt'] = [dict(r=rng.uniform(.6, 4.4), ph=rng.uniform(0, 6.28), w=rng.uniform(.5, 1.6) * rng.choice((1, 1, 1, -1)), y=rng.normal(0, .5),
                          life=rng.uniform(.7, 1.6), t0=rng.uniform(0, 1.6), out=rng.uniform(.2, 1.4), b=rng.uniform(.4, 1.0)) for i in range(150)]
        n = fbm(512, 512, 22, 4, seed=77)
        TEX['ray'] = ((n - n.min()) / (n.max() - n.min() + 1e-6)).astype(f32)
    return TEX


def sample(t_, u, v):
    u, v = np.broadcast_arrays(np.asarray(u, f32), np.asarray(v, f32))
    return cv2.remap(t_, (u % 1.0 * (t_.shape[1] - 1)).astype(f32), (v % 1.0 * (t_.shape[0] - 1)).astype(f32), cv2.INTER_LINEAR)


RINGS = (dict(r=3.7, tilt=6.0, yaw=12.0, w=1.0, sp=.55, beads=3),              # 大きな 輪（ほぼ 水平）
         dict(r=1.85, tilt=-38.0, yaw=58.0, w=1.15, sp=-.8, beads=2),             # ななめの 輪（地面に とどかない）
         dict(r=1.2, tilt=74.0, yaw=-32.0, w=1.25, sp=1.2, beads=2))              # 立った 輪


def ring_grow(t):
    return .05 + .95 * (1 - (1 - ss(RING0, RING1, t)) ** 2) + .25 * swell(t)


def ring_pts(R_, t, n=360):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ty, tw = math.radians(R_['tilt']), math.radians(R_['yaw'])
    rad = R_['r'] * ring_grow(t)
    P = np.stack([np.cos(a) * rad, np.zeros_like(a), np.sin(a) * rad], 1)
    Rx = np.array([[1, 0, 0], [0, math.cos(ty), -math.sin(ty)], [0, math.sin(ty), math.cos(ty)]])
    Ry = np.array([[math.cos(tw), 0, math.sin(tw)], [0, 1, 0], [-math.sin(tw), 0, math.cos(tw)]])
    return P @ (Ry @ Rx).T + O, a


def draw_rings(t, front, hD=None):
    """金の 輪（front＝玉より 手前の 半分 か うしろの 半分）→ 線形の 色。hD＝馬の 奥行き（馬より うしろの 所は 描かない）"""
    m = np.zeros((H, W), f32)
    k = ss(RING0, RING0 + .35, t) * (1 - ss(T_BURST, T_BURST + .12, t))
    if k <= 0:
        return np.zeros((H, W, 3), f32)
    for j, R_ in enumerate(RINGS):
        P, a = ring_pts(R_, t)
        q, z = project(P)
        nearer = z < OZ
        for i in range(len(P)):
            i2 = (i + 1) % len(P)
            if nearer[i] != front or P[i][1] < 0.02:
                continue
            x0, y0 = q[i]; x1, y1 = q[i2]
            if hD is not None:
                xi, yi = int(min(max(x0, 0), W - 1)), int(min(max(y0, 0), H - 1))
                if hD[yi, xi] < z[i]:
                    continue
            br = (.55 + .45 * (z[i] < OZ)) * R_['w']
            cv2.line(m, (int(x0 * 16), int(y0 * 16)), (int(x1 * 16), int(y1 * 16)), float(br), max(1, int(round(2.2 * S))), cv2.LINE_AA, shift=4)
        for b in range(R_['beads']):
            ang = (b / R_['beads']) * 2 * math.pi + t * R_['sp'] * 2.2
            i = int((ang % (2 * math.pi)) / (2 * math.pi) * len(P)) % len(P)
            if nearer[i] != front:
                continue
            if hD is not None:
                xi, yi = int(min(max(q[i][0], 0), W - 1)), int(min(max(q[i][1], 0), H - 1))
                if hD[yi, xi] < z[i]:
                    continue
            cv2.circle(m, (int(q[i][0] * 16), int(q[i][1] * 16)), int(5.5 * S * 16), 2.2, -1, cv2.LINE_AA, shift=4)
    m *= k
    return m[..., None] * np.array([2.4, 1.9, 0.9], f32) + blur(m, 3 * S)[..., None] * np.array([1.3, 1.0, .35], f32) + blur(m, 14 * S)[..., None] * np.array([.5, .45, .15], f32)


def orb_layer(t):
    """光の 玉（白 → 若草色・もやもや 動く 表面・ふちの とげ）と 大きな 光（線形の 色）・玉の 形（すき通し）"""
    T = tex()
    yy, xx = grid()
    lv = orb_level(t)
    if lv <= 0:
        return np.zeros((H, W, 3), f32), np.zeros((H, W), f32)
    sw = swell(t)
    R = orb_px() * (.15 + .85 * ss(ORB0 + .2, ORB1, t)) * (1 + .7 * sw)
    dx, dy = xx - OC[0], yy - OC[1]
    rr = np.sqrt(dx * dx + dy * dy)
    r = rr / R
    ang = np.arctan2(dy, dx)
    n = sample(T['n1'], dx / (R * 3.2) + t * .07, dy / (R * 3.2) - t * .05) * .6 + sample(T['n2'], dx / (R * 1.6) - t * .11, dy / (R * 1.6) + t * .09) * .4
    body = np.clip(1 - r ** 2, 0, 1) ** .5 * (.75 + .5 * n)
    spikes = np.clip(1 - np.abs(r - 1.02) / .35, 0, 1) * (sample(T['ray'], ang / 6.283 * 3 + t * .05, r * .2) ** 3) * 2.2
    core = np.exp(-(r / .55) ** 2) * 3.0
    glow = np.exp(-(rr / (R * 2.6)) ** 2) * .8 + np.exp(-(rr / (R * 7.0)) ** 1.2) * .07
    birth = 1 + .6 * math.exp(-max(t - RUN0, 0) / .1) * (t >= RUN0)                  # 馬が 生まれる 瞬間 少し 強く
    out = ((body * 2.2 + core + spikes)[..., None] * np.array([1.0, 1.0, .85], f32) + glow[..., None] * np.array([.55, .85, .35], f32)) * lv * (1 + 1.6 * sw) * birth
    alpha = np.clip((1 - r) * 3, 0, 1) * lv
    return out, alpha.astype(f32)


def god_rays(t, base):
    T = tex()
    lv = orb_level(t)
    if lv <= .02:
        return np.zeros((H, W, 3), f32)
    yy, xx = grid()
    dx, dy = xx - OC[0], yy - OC[1]
    ang = np.arctan2(dy, dx)
    rr = np.sqrt(dx * dx + dy * dy)
    msk = sample(T['ray'], ang / 6.283 * 2 + t * .012, rr * .0004) ** 3.0
    src = base * (msk * np.exp(-rr / (W * .45)))[..., None]
    return zoom_blur(np.minimum(src, 2.5), OC[0], OC[1], 2.2, 14) * (.28 * lv)


def lens_streak(t):
    lv = orb_level(t) * (1 + 1.4 * swell(t))
    if lv <= 0:
        return np.zeros((H, W, 3), f32)
    yy, xx = grid()
    v = np.exp(-((yy - OC[1]) / (2.2 * S)) ** 2) * np.exp(-np.abs(xx - OC[0]) / (W * .55))
    v2 = np.exp(-((yy - OC[1]) / (9 * S)) ** 2) * np.exp(-np.abs(xx - OC[0]) / (W * .3))
    return (v * 1.6 + v2 * .35)[..., None] * np.array([.75, 1.0, .7], f32) * lv


def particles(t, hD=None):
    """光の 粒（玉の まわりを まわりながら 外へ・短い 金の すじ）"""
    T = tex()
    m = np.zeros((H, W), f32)
    lv = ss(ORB0 + .3, ORB1 + .3, t) * (1 - ss(T_BURST, T_BURST + .2, t))
    if lv <= 0:
        return np.zeros((H, W, 3), f32)
    for Pp in T['pt']:
        a_ = ((t - Pp['t0']) % Pp['life']) / Pp['life']
        def at(tt):
            rad = Pp['r'] * (1 + Pp['out'] * tt) * ring_grow(t)
            ph = Pp['ph'] + Pp['w'] * tt * 1.6
            return O + np.array([rad * math.cos(ph), Pp['y'] * (1 + tt), rad * math.sin(ph)])
        p1 = at(a_)
        if p1[1] < .03:
            continue
        q, z = project([p1, at(max(0.0, a_ - .025))])
        if hD is not None:
            xi, yi = int(min(max(q[0][0], 0), W - 1)), int(min(max(q[0][1], 0), H - 1))
            if hD[yi, xi] < z[0]:
                continue
        f = Pp['b'] * math.sin(math.pi * a_)
        cv2.line(m, (int(q[1][0] * 16), int(q[1][1] * 16)), (int(q[0][0] * 16), int(q[0][1] * 16)), float(f), max(1, int(round(1.6 * S))), cv2.LINE_AA, shift=4)
    m *= lv
    return m[..., None] * np.array([2.6, 2.1, 1.0], f32) + blur(m, 2 * S)[..., None] * np.array([.9, .7, .25], f32)


def bokeh(t):
    T = tex()
    yy, xx = grid()
    out = np.zeros((H, W), f32)
    lv = orb_level(t)
    for B in T['bokeh']:
        x = (B['x'] * W + B['vx'] * t * S * 4)
        y = (B['y'] * H + B['vy'] * t * S * 4)
        r = B['r'] * S
        x0, x1 = int(max(0, x - r - 2)), int(min(W, x + r + 2)); y0, y1 = int(max(0, y - r - 2)), int(min(H, y + r + 2))
        if x1 <= x0 or y1 <= y0:
            continue
        d = np.sqrt((xx[y0:y1, x0:x1] - x) ** 2 + (yy[y0:y1, x0:x1] - y) ** 2)
        out[y0:y1, x0:x1] += np.clip((r - d) / (2.5 * S), 0, 1) * (.6 + .4 * np.clip(d / r, 0, 1)) * B['a'] * (.8 + .2 * math.sin(t * 1.3 + B['ph']))
    return out[..., None] * np.array([.35, .6, .25], f32) * lv * .45


def haze(t):
    """玉の まわりの 空気の 光（うすい もや）"""
    yy, xx = grid()
    lv = orb_level(t)
    d = np.sqrt(((xx - OC[0]) / W) ** 2 + ((yy - OC[1]) / W) ** 2)
    g = np.exp(-d / .45) * .03 + np.exp(-d / 1.2) * .008
    return g[..., None] * np.array([.35, .7, .3], f32) * lv * (1 + 1.5 * swell(t))


def leap_trail(t, hD=None):
    """玉から とびだす 馬の うしろの 光の すじ（とびおりる あいだ → 消える）"""
    if not RUN0 < t < T_LAND + .6:
        return None
    m = np.zeros((H, W), f32)
    ts = np.linspace(RUN0, min(t, T_LAND), 40)
    P = np.array([NH.frame_at(x)['B'] for x in ts])
    q, z = project(P)
    fade = 1 - ss(T_LAND, T_LAND + .6, t)
    for i in range(len(P) - 1):
        k = ((i + 1) / (len(P) - 1)) ** 1.4 * fade
        w = max(1, int(round((1.5 + 3.5 * k) * S)))
        cv2.line(m, (int(q[i][0] * 16), int(q[i][1] * 16)), (int(q[i + 1][0] * 16), int(q[i + 1][1] * 16)), float(k), w, cv2.LINE_AA, shift=4)
    return m[..., None] * GOLD * .9 + blur(m, 5 * S)[..., None] * GOLD * .45


# ================================================================ はじける・光に つつまれる
def burst_layer(t):
    a = t - T_BURST
    if a < -.02:
        return None
    yy, xx = grid()
    rr = np.sqrt((xx - OC[0]) ** 2 + (yy - OC[1]) ** 2)
    R = W * (.05 + 1.6 * (1 - math.exp(-max(a, 0) / .12)))
    core = np.exp(-(rr / max(R, 1)) ** 2) * (4.0 * math.exp(-max(a, 0) / .35))
    ring = np.exp(-((rr - R * 1.05) / (14 * S)) ** 2) * (1.6 * math.exp(-max(a, 0) / .18))
    white = ss(WH0, WH0 + .08, t) * (1 - ss(WH1 - .2, WH1, t))
    return (core + ring)[..., None] * np.array([1.0, 1.0, .85], f32) + white * np.array([2.2, 2.4, 2.0], f32)


# ================================================================ 低い 目線の 場面（第4.77版）：芝の 上・うしろに 大きな 光の 玉・上から ど！的中 が 落ちて くる
# まさちゃん「ノーマル的中演出、最後は芝の上に、上から、ど！的中、の文字が落ちてくる演出にして！ 背景は、一枚目の画像の玉(かなり大きい)の前に
# ど！的中の文字が落ちてきて、芝や地面、周りの明るさ、雰囲気は一枚目の画像の玉の映像の雰囲気で作成して！ 最後のど！的中の文字は背景や地面、
# 芝に負けない立体的でリアルに作成して！ あと、常に不定期に輝きを放っているようにして！」
T_SHOT2 = F['SHOT2']
SWP20, SWP21 = F['SWEEP2']
EYE2 = np.array([0.0, 0.45, 3.2])                 # 芝から 45cm・玉から 3.2m
TGT2 = np.array([0.0, 0.69, 0.0])                 # 少し 見上げる（玉が 画面の 上 1/3 に 大きく）
FW2, RT2, UP2 = cam_axes(EYE2, TGT2)


def project2(P):
    P = np.atleast_2d(np.asarray(P, float))
    d = P - EYE2
    xc, yc, zc = d @ RT2, d @ UP2, d @ FW2
    return np.stack([(xc / zc / (TH * W / H) + 1) * .5 * W, (1 - yc / zc / TH) * .5 * H], -1), zc


OC2, OZ2 = project2(O)
OC2 = OC2[0]; OZ2 = float(OZ2[0])
ORB2 = ORB_R * H / (2 * OZ2 * TH)                 # 玉の 半径（画面 px）
LOGO_DY = .125 * H                                # ど！的中 を 下へ（足もとが 芝の 上）
LOGO_BASE = 624 / 844 * H + LOGO_DY               # 「的中」の 下の はし（画面）
RINGS2 = (dict(r=1.3, tilt=9.0, yaw=12.0, w=1.0, sp=.55, beads=3),
          dict(r=.98, tilt=-40.0, yaw=58.0, w=1.1, sp=-.8, beads=2),
          dict(r=.74, tilt=70.0, yaw=-32.0, w=1.2, sp=1.2, beads=2))
GEO2 = {}


def geo2():
    """低い 目線の カメラの 画素ごとの 地面（芝）と 空"""
    if not GEO2:
        yy, xx = grid()
        nx = ((xx + .5) / W * 2 - 1) * TH * W / H
        ny = (1 - (yy + .5) / H * 2) * TH
        d = [FW2[i] + nx * RT2[i] + ny * UP2[i] for i in range(3)]
        rl = np.sqrt(1 + nx * nx + ny * ny)
        gnd = d[1] < -1e-4
        tt = np.where(gnd, -EYE2[1] / np.minimum(d[1], -1e-4), 1e4)
        GEO2['X'] = (EYE2[0] + d[0] * tt).astype(f32)
        GEO2['Z'] = (EYE2[2] + d[2] * tt).astype(f32)
        GEO2['gnd'] = gnd
        GEO2['el'] = (d[1] / rl).astype(f32)                                     # 光の 道の 上下の かたむき（地平で 0）
        GEO2['foot'] = (tt * rl * 2 * TH / H / np.maximum(-d[1] / rl, .02)).astype(f32)
        fn = os.path.join(TMP, f'ndturf2_{W}x{H}_v1.npz')
        if os.path.exists(fn):
            z = np.load(fn)
            GEO2['alb'], GEO2['N'] = z['alb'], z['N']
        else:
            GEO2['alb'], GEO2['N'] = turf(np.where(gnd, GEO2['X'], 0), np.where(gnd, GEO2['Z'], 0), np.where(gnd, GEO2['foot'], 1.0))
            tmp = fn[:-4] + f'_{os.getpid()}.npz'
            np.savez(tmp, alb=GEO2['alb'], N=GEO2['N'])
            os.replace(tmp, fn)
        # 「的中」の 足もとの 芝（画面の まん中の 線）の 奥行き
        nyb = (1 - (LOGO_BASE + .5) / H * 2) * TH
        db = FW2 + nyb * UP2
        GEO2['zlet'] = float(-EYE2[1] / db[1])                                   # 前向きの 奥行き
        GEO2['Zlet'] = float(EYE2[2] + db[2] * GEO2['zlet'])                     # 世界の z
    return GEO2


def orb2_I(t):
    """低い 目線の 場面の 玉の 光（おちついた 光・字が 落ちた とき 少し ふくらむ）"""
    a = t - LG1
    return 1.0 + (.22 * math.exp(-max(a, 0) / .25) if a >= 0 else 0.0)


def irr2(P, t):
    d = np.linalg.norm(np.atleast_2d(P) - O, axis=-1)
    return orb2_I(t) * 3.2 / (d ** 1.5 + .3)


def sky2(t):
    """空（地平の 上）：夜空・玉の まわりの もや・遠くの 木の かげ"""
    g = geo2()
    yy, xx = grid()
    el = np.clip(g['el'], 0, 1)
    base = np.array([.003, .005, .004], f32)[None, None] * (1 - el[..., None] * 1.5).clip(.2, 1) + np.array([.010, .016, .008], f32) * np.exp(-el / .05)[..., None]
    d = np.sqrt(((xx - OC2[0]) / W) ** 2 + ((yy - OC2[1]) / W) ** 2)
    hz = (np.exp(-d / .3) * .035 + np.exp(-d / 1.0) * .006)[..., None] * np.array([.35, .7, .3], f32) * orb2_I(t)
    return (base + hz).astype(f32)


def treeline(img):
    """地平の 少し 上の 木の かげ（黒い ぎざぎざ）"""
    g = geo2()
    yy, xx = grid()
    T = tex()
    # 地平の 画面の 高さ（まん中の 線で）
    row = np.argmax(g['gnd'][:, W // 2])
    nh = sample(T['n2'], (xx[0] / W) * 2.3, np.full(W, .41, f32))[0]
    top = row - (10 + 26 * nh + 8 * sample(T['n1'], (xx[0] / W) * 7.0, np.full(W, .2, f32))[0]) * S
    m = ((yy >= top[None, :]) & (~g['gnd'])).astype(f32)
    m = blur(m, 1.0 * S)
    rim = np.clip(m - blur(np.roll(m, -int(2 * S), 0), 1.5 * S), 0, 1)
    col = np.array([.004, .006, .004], f32)
    return img * (1 - m[..., None]) + col * m[..., None] + rim[..., None] * np.array([.05, .09, .04], f32) * .6


GRASS = {}


def grass2():
    """手前の 芝の 葉（1本ずつ：玉の 光を うしろから 受けて 先が 光る）→ 字より 奥の 葉・字より 手前の 葉（線形の 色・すき通し）。一度 作る"""
    if GRASS:
        return GRASS
    g = geo2()
    fn = os.path.join(TMP, f'ndgrass2_{W}x{H}_v1.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        for k in z.files:
            GRASS[k] = z[k]
        return GRASS
    rng = np.random.default_rng(812)
    k2 = 2                                                                       # 2倍で 描いて 縮める
    zl = g['Zlet']
    roots = []
    for (x0, x1, z0, z1, dens) in ((-1.7, 1.7, EYE2[2] - 2.75, EYE2[2] - .45, 15000), (-3.8, 3.8, -3.4, EYE2[2] - 2.75, 2600)):
        n = int((x1 - x0) * (z1 - z0) * dens * (S if S < 1 else 1) ** 1.0)
        roots.append(np.stack([rng.uniform(x0, x1, n), np.zeros(n), rng.uniform(z0, z1, n)], 1))
    R = np.concatenate(roots)
    q, z = project2(R)
    ok = (q[:, 0] > -20) & (q[:, 0] < W + 20) & (q[:, 1] > -20) & (q[:, 1] < H + 40) & (z > .3)
    R, q, z = R[ok], q[ok], z[ok]
    n = len(R)
    patch = vnoise(R[:, 0], R[:, 2], .35, 31)
    h = rng.uniform(.045, .095, n) * (.75 + .5 * patch)
    ang = rng.uniform(0, 2 * math.pi, n)
    lean = rng.uniform(.08, .5, n)
    tip = R + np.stack([np.cos(ang) * lean * h + .25 * h, h * np.sqrt(1 - lean ** 2), np.sin(ang) * lean * h], 1)
    bow = np.stack([-np.sin(ang), np.zeros(n), np.cos(ang)], 1) * (rng.normal(0, .12, n) * h)[:, None]
    mid = R + (tip - R) * .5 + bow + np.array([0.0, 0.0, 0.0])
    alb = np.array([.045, .105, .028])[None] * rng.uniform(.7, 1.3, n)[:, None]
    yl = rng.random(n) < .12
    alb[yl] = np.array([.09, .11, .03]) * rng.uniform(.8, 1.2, yl.sum())[:, None]
    V = EYE2[None] - R; V /= np.linalg.norm(V, axis=1, keepdims=True)
    L = O[None] - R; dl = np.linalg.norm(L, axis=1); L /= dl[:, None]
    E = 3.2 / (dl ** 1.5 + .3)
    tr = np.clip(-(V * L).sum(1), 0, 1) ** 2                                      # うしろから の 光（すける）
    c_root = alb * (E * .12)[:, None] * ORB_COL[None] * .5 + AMB[None] * .3
    c_mid = alb * (E * (.25 + 1.1 * tr))[:, None] * ORB_COL[None] + AMB[None] * .6
    c_tip = alb * (E * (.3 + 2.6 * tr))[:, None] * ORB_COL[None] * 1.15 + (np.array([.10, .14, .06]) * (E * tr * .5)[:, None])
    qr = project2(R)[0] * k2; qm = project2(mid)[0] * k2; qt = project2(tip)[0] * k2
    pxm = H / (2 * z * TH) * k2                                                  # 1m は 何 px（2倍）
    wr = np.maximum(.0032 * pxm, .7); wm = np.maximum(.0022 * pxm, .5)
    order = np.argsort(-z)
    Hk, Wk = H * k2, W * k2
    layers = {}
    for nm in ('back', 'front'):
        layers[nm] = (np.zeros((Hk, Wk, 3), f32), np.zeros((Hk, Wk), f32))
    zwl = g['zlet']
    for i in order:
        col, A = layers['front' if z[i] < zwl else 'back']
        r_, m_, t_ = qr[i], qm[i], qt[i]
        for (a, b, wa, wb, ca, cb) in ((r_, m_, wr[i], wm[i], c_root[i], c_mid[i]), (m_, t_, wm[i], .3, c_mid[i], c_tip[i])):
            dv = b - a
            ln = math.hypot(dv[0], dv[1])
            if ln < 1e-3:
                continue
            pn = np.array([-dv[1], dv[0]]) / ln
            poly = np.array([a + pn * wa * .5, b + pn * wb * .5, b - pn * wb * .5, a - pn * wa * .5])
            cc = tuple(float(v) for v in (ca + cb) * .5)
            cv2.fillConvexPoly(col, np.round(poly * 4).astype(np.int32), cc, lineType=cv2.LINE_8, shift=2)
            cv2.fillConvexPoly(A, np.round(poly * 4).astype(np.int32), 1.0, lineType=cv2.LINE_8, shift=2)
    for nm, (col, A) in layers.items():
        GRASS[nm + '_c'] = cv2.resize(col, (W, H), interpolation=cv2.INTER_AREA)
        GRASS[nm + '_a'] = cv2.resize(A, (W, H), interpolation=cv2.INTER_AREA)
    tmp = fn[:-4] + f'_{os.getpid()}.npz'
    np.savez(tmp, **GRASS)
    os.replace(tmp, fn)
    return GRASS


def letter_shadow(t, Afull):
    """字の 影（玉の 光が 字の うしろから → 手前の 芝へ のびる）：画面の 地面の 画素ごとの 光の 通り（1＝影なし）"""
    g = geo2()
    gnd = g['gnd']
    if Afull is None or Afull.max() < .01:
        return np.ones((H, W), f32)
    zl = g['Zlet']
    X, Z = g['X'], g['Z']
    front = gnd & (Z > zl + .01)
    vis = np.ones((H, W), f32)
    if not front.any():
        return vis
    Xf, Zf = X[front].astype(np.float64), Z[front].astype(np.float64)
    lam = (zl - Zf) / (O[2] - Zf)
    Q = np.stack([Xf + lam * (O[0] - Xf), lam * O[1], Zf + lam * (O[2] - Zf)], 1)
    q, _ = project2(Q)
    Ab = blur(Afull, 3 * S)
    n_ = len(q); c_ = 1024; r_ = (n_ + c_ - 1) // c_
    mx_ = np.zeros(r_ * c_, f32); my_ = np.full(r_ * c_, -10, f32)
    mx_[:n_] = q[:, 0]; my_[:n_] = q[:, 1]
    a = cv2.remap(Ab, mx_.reshape(r_, c_), my_.reshape(r_, c_), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0).ravel()[:n_]
    fade = np.exp(-(Zf - zl) / .9)                                                # 字の 足もとが いちばん こい・手前ほど うすい
    soft = np.clip(1 - .55 * a * fade, 0, 1)
    vis[front] = soft
    return blur(vis, 2 * S)


def ground2(t, vis):
    """芝の 地面（遠くは もようの 芝・玉の 光だまり・字の 影）"""
    g = geo2()
    E = ground_E(t, g['X'], g['Z'], g['N']) * (orb2_I(t) / max(orb_I(t), 1e-6)) if False else None
    lx, ly, lz = O[0] - g['X'], O[1], O[2] - g['Z']
    d = np.sqrt(lx * lx + ly * ly + lz * lz)
    N = g['N']
    ndl = (N[..., 0] * lx + N[..., 1] * ly + N[..., 2] * lz) / d
    E = orb2_I(t) * KG * np.maximum(ndl, 0) ** .7 / (d ** 1.3 + .3)
    col = g['alb'] * (E * vis)[..., None] * ORB_COL + g['alb'] * AMB * 6
    return np.where(g['gnd'][..., None], col, 0).astype(f32)


def rings2(t, front):
    m = np.zeros((H, W), f32)
    for R_ in RINGS2:
        n = 360
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        ty, tw = math.radians(R_['tilt']), math.radians(R_['yaw'] + t * R_['sp'] * 8)
        P = np.stack([np.cos(a) * R_['r'], np.zeros_like(a), np.sin(a) * R_['r']], 1)
        Rx = np.array([[1, 0, 0], [0, math.cos(ty), -math.sin(ty)], [0, math.sin(ty), math.cos(ty)]])
        Ry = np.array([[math.cos(tw), 0, math.sin(tw)], [0, 1, 0], [-math.sin(tw), 0, math.cos(tw)]])
        P = P @ (Ry @ Rx).T + O
        q, z = project2(P)
        nearer = z < OZ2
        for i in range(n):
            if nearer[i] != front:
                continue
            i2 = (i + 1) % n
            br = (.55 + .45 * nearer[i]) * R_['w']
            cv2.line(m, (int(q[i][0] * 16), int(q[i][1] * 16)), (int(q[i2][0] * 16), int(q[i2][1] * 16)), float(br), max(1, int(round(3.4 * S))), cv2.LINE_AA, shift=4)
        for b in range(R_['beads']):
            ang = (b / R_['beads']) * 2 * math.pi + t * R_['sp'] * 2.2
            i = int((ang % (2 * math.pi)) / (2 * math.pi) * n) % n
            if nearer[i] != front:
                continue
            cv2.circle(m, (int(q[i][0] * 16), int(q[i][1] * 16)), int(8 * S * 16), 2.2, -1, cv2.LINE_AA, shift=4)
    return m[..., None] * np.array([2.4, 1.9, 0.9], f32) + blur(m, 4 * S)[..., None] * np.array([.9, .7, .25], f32) + blur(m, 18 * S)[..., None] * np.array([.14, .12, .04], f32)


def orb2(t):
    """大きな 光の 玉（低い 目線）・光の 筋・横に 走る 光"""
    T = tex()
    yy, xx = grid()
    R = ORB2 * (1 + .04 * math.sin(t * 2.3))
    dx, dy = xx - OC2[0], yy - OC2[1]
    rr = np.sqrt(dx * dx + dy * dy)
    r = rr / R
    ang = np.arctan2(dy, dx)
    n = sample(T['n1'], dx / (R * 3.2) + t * .07, dy / (R * 3.2) - t * .05) * .6 + sample(T['n2'], dx / (R * 1.6) - t * .11, dy / (R * 1.6) + t * .09) * .4
    body = np.clip(1 - r ** 2, 0, 1) ** .6 * (.55 + .7 * n)                       # 玉の 中の もやもや
    rim = np.exp(-((r - .97) / .05) ** 2) * .9                                  # ふちの 光
    spikes = np.clip(1 - np.abs(r - 1.0) / .12, 0, 1) * (sample(T['ray'], ang / 6.283 * 9 + t * .05, r * .2) ** 4) * .9
    core = np.exp(-(r / .45) ** 2) * 2.4
    glow = np.exp(-(rr / (R * 1.35)) ** 2) * .13 + np.exp(-(rr / (R * 3.0)) ** 1.2) * .014   # まわりは 暗い まま（玉の 場面の 雰囲気）
    k = orb2_I(t)
    tint = np.clip(r, 0, 1)[..., None] ** 1.2                                   # まん中は 白・ふちは 若草色
    bc = np.array([1.0, 1.0, .9], f32) * (1 - tint) + np.array([.42, 1.0, .32], f32) * tint
    out = ((body * .95 + spikes + rim)[..., None] * bc + core[..., None] * np.array([1.0, 1.0, .9], f32) + glow[..., None] * np.array([.36, .9, .24], f32)) * k
    src = out * (sample(T['ray'], ang / 6.283 * 2 + t * .012, rr * .0004) ** 3.0 * np.exp(-rr / (W * .6)))[..., None]
    rays = zoom_blur(np.minimum(src, 2.5), OC2[0], OC2[1], 2.0, 14) * .12
    v = np.exp(-((yy - OC2[1]) / (2.6 * S)) ** 2) * np.exp(-np.abs(xx - OC2[0]) / (W * .6))
    streak = (v * 1.3)[..., None] * np.array([.75, 1.0, .7], f32) * k
    return out, rays + streak, np.clip((1 - r) * 3, 0, 1).astype(f32)


def particles2(t):
    T = tex()
    m = np.zeros((H, W), f32)
    for Pp in T['pt']:
        a_ = ((t - Pp['t0']) % Pp['life']) / Pp['life']
        def at(tt):
            rad = (Pp['r'] * .3 + .3) * (1 + Pp['out'] * tt)
            ph = Pp['ph'] + Pp['w'] * tt * 1.6
            return O + np.array([rad * math.cos(ph), Pp['y'] * .5 * (1 + tt), rad * math.sin(ph)])
        p1 = at(a_)
        if p1[1] < .03 or p1[2] > EYE2[2] - .3:
            continue
        q, z = project2([p1, at(max(0.0, a_ - .025))])
        f = Pp['b'] * math.sin(math.pi * a_)
        cv2.line(m, (int(q[1][0] * 16), int(q[1][1] * 16)), (int(q[0][0] * 16), int(q[0][1] * 16)), float(f), max(1, int(round(2.0 * S))), cv2.LINE_AA, shift=4)
    return m[..., None] * np.array([2.6, 2.1, 1.0], f32) + blur(m, 2 * S)[..., None] * np.array([.9, .7, .25], f32)


# ---------------------------------------------------------------- ど！的中（3D：shiden_logo の 形・！は 1つ）が 上から 落ちて 芝に ドーン
ND_LAYOUT = [('do', (30, 226, 260, 452)), ('e1', (276, 224, 372, 452)), ('hit', (12, 466, 378, 624))]
ND_HIT_Y = ((SL.ORIGIN[1] - 466) / 100, (SL.ORIGIN[1] - 624) / 100)
_CDIR = nrm(np.array(SL.CAM_DIR))


def logo_pose(t):
    """落ちる あいだは 少し 前へ たおれて → 着いたら ゆれて おちつく（大きさは そのまま）"""
    if t < LG0:
        return None
    if t < LG1:
        u = (t - LG0) / (LG1 - LG0)
        rot = (9 * (1 - u), -4 * (1 - u), 0.0)
    else:
        a = t - LG1
        k = ss(.25, .9, a)
        rot = (-2.2 * math.sin(math.pi * a / .13) * math.exp(-a / .1) - 1.0 * math.sin(2 * math.pi * a / 2.3 + .4) * k,
               1.8 * math.sin(2 * math.pi * a / 2.8) * k, 0.0)
    return rot, np.zeros(3), 1.0


def logo_drop(t):
    """画面の 上下の ずれ（px：落ちる → ドーン → 小さく はねる）と たての つぶれ"""
    if t < LG1:
        u = (t - LG0) / (LG1 - LG0)
        return -(LOGO_BASE + 40 * S) * (1 - u * u), 1.0, 2 * (LOGO_BASE + 40 * S) * u / (LG1 - LG0)
    a = t - LG1
    dy = -.022 * H * math.sin(math.pi * min(a / .16, 1.0)) * math.exp(-a / .12) if a < .4 else 0.0
    sq = 1 - .06 * math.exp(-a / .05) * math.cos(2 * math.pi * a / .2)
    return dy, sq, 0.0


def logo_layer(t, work, fi):
    pose = logo_pose(t)
    if pose is None:
        return None
    rot, pos, s = pose
    rd_ = os.path.join(work, '_r'); os.makedirs(rd_, exist_ok=True)
    cache = os.path.join(work, '_logo'); os.makedirs(cache, exist_ok=True)
    heat = .55 * math.exp(-(t - LG1) / .14) if t >= LG1 else 0.0               # 着いた 瞬間 少し 白く 光る
    sweep = None
    for a0, a1 in ((SWP0, SWP1), (SWP20, SWP21)):
        if a0 <= t <= a1:
            sweep = -48 + 78 * ss(0, 1, (t - a0) / (a1 - a0))
    flash = [(nrm(np.array([0.0, .2, 1.0])), np.array([.7, 1.0, .6]) * .5)]
    g = SL.render(os.path.join(rd_, f'ndlogo_{fi:03d}'), W, H, rot, pos, cache, layout=ND_LAYOUT)
    if g[0] is None:
        return None
    lay = SL.layer(None, W, H, rot, pos, sweep=sweep, flash=flash, heat=heat, layout=ND_LAYOUT, hit_y=ND_HIT_Y, gbuf=g)
    if lay is None:
        return None
    col, A, (x0, y0, x1, y1) = lay
    Cf = np.zeros((H, W, 3), f32); Af = np.zeros((H, W), f32)
    Cf[y0:y1, x0:x1] = col; Af[y0:y1, x0:x1] = A
    dy, sq, vel = logo_drop(t)
    M = np.float32([[1, 0, 0], [0, sq, LOGO_BASE * (1 - sq) + LOGO_DY + dy]])     # 足もとを 軸に たてに つぶれる
    Cf = cv2.warpAffine(Cf, M, (W, H), flags=cv2.INTER_LINEAR)
    Af = cv2.warpAffine(Af, M, (W, H), flags=cv2.INTER_LINEAR)
    if vel > 1:                                                                  # 落ちる 速さの ぶれ（1/60秒・上に 尾）
        k_ = int(round(vel / 60.0))
        if k_ >= 2:
            Cf = cv2.blur(Cf, (1, k_), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
            Af = cv2.blur(Af, (1, k_), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
    return Cf, Af


def letter_light(t, Cf, Af):
    """字に 玉の 光（うしろ 上から：上の ふちが 光る）・字の まわりの 光（ゆらぐ）"""
    k = ss(LG0, LG0 + .15, t)
    if k <= 0:
        return Cf
    dv = np.array([OC2[0] - W * .5, OC2[1] - LOGO_C2[1]]); dv = dv / (np.linalg.norm(dv) + 1e-6)
    sh = np.float32([[1, 0, -dv[0] * 4 * S], [0, 1, -dv[1] * 4 * S]])
    inner = cv2.warpAffine(Af, sh, (W, H))
    rim = np.clip(Af - inner, 0, 1)
    rim = blur(rim, .8 * S)
    return Cf + rim[..., None] * np.array([1.0, 1.25, .85], f32) * 1.3 * k * orb2_I(t)


LOGO_C2 = (195.0 * W / 390, 425.0 * H / 844 + LOGO_DY)


def aura2(t, Af):
    """字の まわりの 光（不定期に ゆらぐ）"""
    k = ss(LG1 - .05, LG1 + .4, t)
    if k <= 0:
        return np.zeros((H, W, 3), f32)
    w = .75 + .2 * math.sin(t * 3.1) + .15 * math.sin(t * 7.3 + 1.1) + .1 * math.sin(t * 13.1 + 2.3)
    a1 = blur(Af, 4 * S); a2 = blur(Af, 14 * S); a3 = blur(Af, 36 * S)
    out = a1[..., None] * np.array([1.2, 1.05, .7], f32) * .7 + a2[..., None] * np.array([1.1, .9, .35], f32) * .55 + a3[..., None] * np.array([.6, .8, .35], f32) * .55
    return out * k * w * .6 * (1 - Af[..., None] * .7)


GL = {}


def glint_points(Af, Cf):
    """キラッと 光る 所の 候補（字の 明るい ふち）"""
    if 'pts' not in GL:
        lum = Cf.mean(2)
        er = cv2.erode((Af > .5).astype(np.uint8), np.ones((3, 3), np.uint8))
        edge = (Af > .5) & (er == 0)
        cand = np.argwhere((Af > .9) & (lum > np.percentile(lum[Af > .9], 85)) | edge)
        GL['pts'] = cand[:, ::-1].astype(f32)
    return GL['pts']


def glints(t, Af, Cf):
    """不定期な キラッ（normal_do.GLINT_T の 時刻・字の 明るい 所に 十字の 光）"""
    m = np.zeros((H, W), f32)
    if t < ND.GLINT_T[0] - .01:
        return np.zeros((H, W, 3), f32)
    pts = glint_points(Af, Cf)
    if len(pts) == 0:
        return np.zeros((H, W, 3), f32)
    for i, t0 in enumerate(ND.GLINT_T):
        a = t - t0
        dur = .34
        if not 0 <= a <= dur:
            continue
        r = np.random.default_rng(900 + i)
        x, y = pts[r.integers(len(pts))]
        sz = r.uniform(45, 95) * S
        rot = r.uniform(-.3, .3) + a * .8
        e = math.sin(math.pi * a / dur) ** 1.5
        cv2.circle(m, (int(x * 16), int(y * 16)), int(sz * .09 * 16), 3.2 * e, -1, cv2.LINE_AA, shift=4)
        for k_, (ang, L_) in enumerate(((rot, sz), (rot + math.pi / 2, sz * .85), (rot + math.pi / 4, sz * .38), (rot - math.pi / 4, sz * .38))):
            for sgn in (1, -1):
                for j in range(6):
                    f0, f1 = j / 6, (j + 1) / 6
                    p0 = (x + math.cos(ang) * L_ * f0 * sgn, y + math.sin(ang) * L_ * f0 * sgn)
                    p1 = (x + math.cos(ang) * L_ * f1 * sgn, y + math.sin(ang) * L_ * f1 * sgn)
                    cv2.line(m, (int(p0[0] * 16), int(p0[1] * 16)), (int(p1[0] * 16), int(p1[1] * 16)), float(1.6 * e * (1 - f0) ** 1.5),
                             max(1, int(round((2.4 if k_ < 2 else 1.6) * S * (1 - f0 * .7)))), cv2.LINE_AA, shift=4)
    return m[..., None] * np.array([2.2, 2.0, 1.5], f32) + blur(m, 3 * S)[..., None] * np.array([1.2, 1.0, .5], f32) + blur(m, 10 * S)[..., None] * np.array([.5, .42, .15], f32)


IMP = []


def impact_bits(t, front):
    """着地で はねる 芝と 土（画面の 2D：字の 足もとから 上と 横へ）"""
    a = t - LG1
    if a < 0 or a > 1.2:
        return None
    if not IMP:
        r = np.random.default_rng(66)
        for i in range(160):
            x = W * .5 + r.uniform(-.46, .46) * W
            IMP.append(dict(x=x, vx=(x - W * .5) / W * r.uniform(300, 900) * S + r.normal(0, 120) * S, vy=-r.uniform(350, 1100) * S,
                            s=r.uniform(1.2, 3.6) * S, g=r.random() < .55, f=r.random() < .4, b=r.uniform(.6, 1.2)))
    m = np.zeros((H, W, 3), f32); al = np.zeros((H, W), f32)
    for P in IMP:
        if P['f'] != front:
            continue
        x = P['x'] + P['vx'] * a
        y = LOGO_BASE - 4 * S + P['vy'] * a + .5 * 2600 * S * a * a
        if y > LOGO_BASE + 30 * S and a > .15:
            continue
        x0, y0 = x - P['vx'] / 60, y - (P['vy'] + 2600 * S * a) / 60
        c = (np.array([.06, .15, .04]) if P['g'] else np.array([.16, .12, .08])) * P['b'] * 1.4 + np.array([.10, .14, .06]) * .5
        cv2.line(m, (int(x0 * 16), int(y0 * 16)), (int(x * 16), int(y * 16)), tuple(float(v) for v in c), max(1, int(round(P['s']))), cv2.LINE_AA, shift=4)
        cv2.line(al, (int(x0 * 16), int(y0 * 16)), (int(x * 16), int(y * 16)), 1.0, max(1, int(round(P['s']))), cv2.LINE_AA, shift=4)
    al *= 1 - ss(.7, 1.2, a)
    return m, al


def land_ring(t):
    """着地の 光の 輪（芝の 上に ひろがる）"""
    a = t - LG1
    if a < 0 or a > .9:
        return None
    g = geo2()
    R_ = 2.6 * (1 - math.exp(-a / .22)); wd = .05 + .25 * a; I = 1.5 * math.exp(-a / .28)
    d = np.hypot(g['X'] - 0.0, g['Z'] - g['Zlet'])
    v = (I * np.exp(-((d - R_) / wd) ** 2) + 1.0 * math.exp(-a / .15) * np.exp(-(d / .5) ** 2)) * g['gnd']
    return v.astype(f32)


def shot2(t, work, fi):
    """低い 目線の 場面の 1コマ（線形の 色）"""
    g = geo2()
    G = grass2()
    lay = logo_layer(t, work, fi) if t >= LG0 else None
    Cf, Af = lay if lay is not None else (None, None)
    vis = letter_shadow(t, Af) if Af is not None else np.ones((H, W), f32)
    img = ground2(t, vis)
    img = np.where(g['gnd'][..., None], img, sky2(t))
    img = treeline(img)
    lr = land_ring(t)
    if lr is not None:
        img = img + lr[..., None] * GOLD * .5 + blur(lr, 4 * S)[..., None] * GOLD * .3
    sc_ = orb2_I(t)
    img = img * (1 - G['back_a'][..., None]) + G['back_c'] * (.25 + .75 * vis * sc_)[..., None]
    base, rays, oa = orb2(t)
    img = img + rings2(t, False)
    img = img + base + rays
    img = img + rings2(t, True) + particles2(t) + bokeh(t) * .35
    if Cf is not None:
        bits = impact_bits(t, False)
        if bits is not None:
            img = img * (1 - bits[1][..., None]) + bits[0] * bits[1][..., None]
        Cl = letter_light(t, Cf, Af)
        img = img + aura2(t, Af)
        img = img * (1 - Af[..., None]) + Cl
        bits = impact_bits(t, True)
        if bits is not None:
            img = img * (1 - bits[1][..., None]) + bits[0] * bits[1][..., None]
    img = img * (1 - G['front_a'][..., None]) + G['front_c'] * (.25 + .75 * vis * sc_)[..., None]
    if Cf is not None:
        img = img + glints(t, Af, Cf)
    # 着地の ゆれ・ゆっくり 近づく
    a = t - LG1
    sx = sy = 0.0
    if 0 <= a < .5:                                                              # ドスン（ゆっくり 1回半：細い 輪が こまかく ふるえて 点めつ しない ように）
        e = math.exp(-a / .09)
        sx, sy = 5 * S * e * math.sin(2 * math.pi * a / .2), 14 * S * e * math.cos(2 * math.pi * a / .16)
    z = 1 + .035 * ss(T_SHOT2, T_END, t)
    M = np.float32([[z, 0, W * .5 * (1 - z) + sx], [0, z, H * .45 * (1 - z) + sy]])
    img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # 光に つつまれた ところから
    wf = 1 - ss(T_SHOT2, WH1 + .02, t)
    if wf > 0:
        img = img * (1 - wf * .6) + wf * np.array([2.2, 2.4, 2.0], f32)
    return img


# ================================================================ 1コマ
def frame(t, work, fi):
    if t >= T_SHOT2:
        img = shot2(t, work, fi)
        img = bloom(img, .35)
        return np.clip(finish(img, 811 + fi, vig=.6, ca=.003), 0, 1)
    hl = horse_layer(t)
    hD = hl['D'] if hl is not None else None
    caps = NH.capsules(hl['st'], hl['S'], hl['J']) if hl is not None and t >= T_LAND - .05 else None
    img = ground_layer(t, hl['st'] if hl is not None else None, caps)
    img = img + haze(t) + bokeh(t)
    base, oa = orb_layer(t)
    img = img + god_rays(t, base)
    img = img + draw_rings(t, False, hD)
    zh = float(project(hl['st']['B'])[1][0]) if hl is not None else None
    img = dust_layer(t, img, zh, False)
    lt = leap_trail(t, hD)
    if lt is not None:
        img = img + lt
    behind = hl is not None and t >= RUN0 + .25 and zh > OZ + .1                 # 馬が 玉の うしろ
    if hl is not None and behind:
        img = img * (1 - hl['A'][..., None]) + hl['col']
        img = img * (1 - oa[..., None] * .85) + base
    else:
        img = img + base
        if hl is not None:
            x = min(max((t - RUN0) / NH.LEAP, 0.0), 1.0)
            em = (1 - x) ** 1.5                                                        # 玉から 生まれる ときは 光って いる
            img = img * (1 - hl['A'][..., None]) + hl['col'] + (hl['A'] * em)[..., None] * np.array([1.4, 1.6, 1.1], f32)
    img = dust_layer(t, img, zh, True)
    img = img + draw_rings(t, True, hD) + particles(t, hD) + lens_streak(t)
    bl = burst_layer(t)
    if bl is not None:
        img = img + bl
    img = bloom(img, 1.0)
    out = finish(img, 811 + fi, vig=.55, ca=.003)
    if t < T_BLACK + .05:
        out = out * ss(T_BLACK - .05, T_BLACK + .05, t)                                   # はじめの 1秒は 真っ暗（タップ → 暗く → 光の 点）
    return np.clip(out, 0, 1)


def frame_path(work, i):
    return os.path.join(work, f'f{i:03d}.png')


def render(work, i0, i1):
    for i in range(max(i0, 0), min(i1, NF)):
        if os.path.exists(frame_path(work, i)):
            continue
        t = round(i / FPS, 6)
        if t < T_BLACK - .05:
            img = np.zeros((H, W, 3), f32)
        else:
            img = frame(t, work, i)
        SF.save_png(img, frame_path(work, i))
        print('nd', i, flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--last':
        work, out = sys.argv[2], sys.argv[3]
        im = cv2.imread(frame_path(work, NF - 1))
        assert im is not None and im.shape[:2] == (H0, W0), 'さいごの コマが 読めない'
        cv2.imwrite(out, im, [cv2.IMWRITE_WEBP_QUALITY, 90])
        print(out, os.path.getsize(out))
    elif sys.argv[1] == '--encode':
        work, out = sys.argv[2], sys.argv[3]
        import subprocess
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(work, 'f%03d.png'),
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an', out], check=True)
        print(out, os.path.getsize(out))
    else:
        work = sys.argv[1]; os.makedirs(work, exist_ok=True)
        i0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        i1 = int(sys.argv[3]) if len(sys.argv) > 3 else NF
        render(work, i0, i1)
