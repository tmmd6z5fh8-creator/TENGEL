"""紫電（sd）の 顔と 蹄を まさちゃんの Meshy の 3D（GLB）で 描く（第4.118版の 候補・まさちゃん 03:18「極ど的中の演出の一枚目の写真の馬、ファイルの馬に変えて！
   演出的には暗闇から目が光ってなど演出は同じ！」・08:27「カットインの蹄もファイルの蹄使ってみて！」）
   ・顔：Violet_Nightmare（黒い つやの ある 馬の 胸像・むらさきの 長い たてがみ・ひたいの 白い 星・むらさきの 目）を
         前の 顔と 同じ 画面の 場所・大きさ・向き（右向きの 横顔）で。カメラの 動き（よこから 少し 前へ まわる・寄る）も 前と 同じ 数で：
         前の 顔の「目」と「鼻先」の 画面の 場所（face_marks）に この 馬の 目と 鼻先が 重なる ように、きょり・頭の 上げ下げ（胸像ごと 目の まわりで 回す）・ねらいを コマごとに 合わせる
         光は 前と 同じ（暗い むらさき・うしろから むらさきと 青の 強い ふちの 光・目の 火が まわりを 照らす）。たてがみは この 馬の もの（2D の たてがみは 使わない）
   ・蹄：Violet_Hoof_Flame（むらさき黒の 前足 1本・蹄）を 前の 蹄（shiden_hoof.py）と 同じ 置き方（足は 左・裏は 右・つま先は 上）・同じ カメラ・同じ 大きさに。
         焼けた 蹄鉄の だいだいの 光（裏の ふちの 輪）・うしろからの むらさきと 青の ふちの 光は 前と 同じ
   GLB は 外から もらう もの（リポジトリに 入れない）。場所：SD_HORSE_GLB・SD_HOOF_GLB（ない とき 下の DEF_*）
   描き方：kisekae/r3d/glb（glb.py・raster.py・raster.c：ソフトの ラスタライザ・libraster.so は はじめて 使う とき 作る）で
   G バッファ（色・向き・場所）を 作り、ここで 光を つける（コマごとに 1回 描く）"""
import os, sys, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
import glb as GL                                                               # noqa: E402
from raster import Camera, Light, render                                       # noqa: E402

NOLIGHT = [Light((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 0.0, shadow=False)]           # G バッファだけ（光・影・AO は ここで 計算）

# 第4.163版（まさちゃん 2026/11/13 00:15「極ど的中の演出の馬、文字をこのファイルと入れ替えて！」）：顔の 馬は Violet_Nightmane（むらさき黒の 胸像・
#   うしろへ 大きく なびく むらさきの たてがみ・白むらさきに 光る 目・首は はじめから ななめ）。SD_HORSE_MODEL=nightmare で 前の 馬（Violet_Nightmare：第4.118版〜第4.162版）
GLB_DIR = os.environ.get('SD_GLB_DIR', '/home/claude/work/sd163/orig')
HORSE_KIND = os.environ.get('SD_HORSE_MODEL', 'nightmane')
assert HORSE_KIND in ('nightmane', 'nightmare'), HORSE_KIND
DEF_HORSE = os.path.join(GLB_DIR, 'nightmane.glb' if HORSE_KIND == 'nightmane' else 'nightmare_old.glb')
DEF_HOOF = os.path.join(GLB_DIR, 'hoof.glb')
HORSE_GLB = os.environ.get('SD_HORSE_GLB', DEF_HORSE)
HOOF_GLB = os.environ.get('SD_HOOF_GLB', DEF_HOOF)
SS_FACE = int(os.environ.get('SD_GLB_SS', '2'))                                # 顔の 3D の なめらかさ（2 で 4倍の 点）

# 馬の だいじな 点（モデルの 座標・+z が 前・+y が 上）。横と 前から 描いて 目の 光る 所・いちばん 前の 点などを はかった
LM_ALL = dict(
    nightmare=dict(eye=np.array([-0.1657, 0.4243, 0.5059]),                   # 左の 目（カメラは この 馬の 左がわ −x に いて 右向きの 横顔）
                   eye_r=np.array([0.1651, 0.4241, 0.5060]),
                   muzzle=np.array([0.0012, 0.0344, 0.7325]),                  # 鼻先（いちばん 前）
                   nose=np.array([-0.055, 0.075, 0.690]),                      # 鼻の 穴（白い 息が 出る 所）
                   chin=np.array([-0.0054, -0.1200, 0.5959]),
                   poll=np.array([-0.02, 0.80, 0.22])),                        # 耳の あいだ（頭の てっぺん）
    nightmane=dict(eye=np.array([-0.0959, 0.2898, 0.6539]),                   # 左の 目（白むらさきに 光る 所の まん中）。頭の まん中の 面は x≈+0.055（胸像の 中で 少し 右）
                   eye_r=np.array([0.2076, 0.2714, 0.6706]),
                   muzzle=np.array([0.045, -0.015, 0.948]),                    # 鼻先（いちばん 前・頭の まん中の 面）
                   nose=np.array([-0.060, 0.000, 0.905]),                      # 左の 鼻の 穴（輪の まん中）
                   chin=np.array([0.048, -0.190, 0.780]),
                   poll=np.array([0.05, 0.45, 0.47])))                         # 耳の 付け根の あいだ
LM = LM_ALL[HORSE_KIND]


def nrm(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-12)


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def m44(R, t=(0, 0, 0), s=1.0):
    M = np.eye(4)
    M[:3, :3] = np.asarray(R) * s
    M[:3, 3] = t
    return M


def xf(M, p):
    p = np.asarray(p, float)
    return (M[:3, :3] @ p.T).T + M[:3, 3] if p.ndim == 2 else M[:3, :3] @ p + M[:3, 3]


def project(cam, P):
    """世界の 点 → 画面の px（x, y）"""
    P = np.atleast_2d(np.asarray(P, float))
    hp = np.c_[P, np.ones(len(P))]
    c = hp @ (cam.proj @ cam.view).T
    nd = c[:, :3] / c[:, 3:4]
    return np.c_[(nd[:, 0] + 1) / 2 * cam.W, (1 - nd[:, 1]) / 2 * cam.H]


_MD = {}


def model(key):
    if key not in _MD:
        path = HORSE_GLB if key == 'horse' else HOOF_GLB
        assert os.path.exists(path), f'GLB が ない（{key}）: {path}（SD_HORSE_GLB・SD_HOOF_GLB で 場所を 指定）'
        _MD[key] = GL.load(path).flatten()
    return _MD[key]


def ggx(N, H_, L, V, rough):
    a2 = rough ** 4
    ndh = np.clip((N * H_).sum(-1), 0, 1)
    D = a2 / (np.pi * (ndh * ndh * (a2 - 1) + 1) ** 2 + 1e-7)
    ndl = np.clip((N * L).sum(-1), 0, 1)
    ndv = np.clip((N * V).sum(-1), 1e-3, 1)
    k = (rough + 1) ** 2 / 8
    G = ndl / (ndl * (1 - k) + k) * ndv / (ndv * (1 - k) + k)
    return D * G / (4 * ndv + 1e-4)


# ================================================================ 顔（Violet_Nightmare）
FOV = 34.0


def face_cam(Mo, u, v, W, H):
    """前の 顔の しるし Mo（目・鼻先の 画面の 場所）に この 馬の 目と 鼻先を 合わせる カメラ。
       カメラの 向きは 前と 同じ 作り方（目から：よこ Z ＋ 頭の 向き U × u ＋ 上 V × v）。
       頭の 上げ下げ（前の 馬は 首を 上げる）は 胸像ごと 目の まわりで x 軸に 回して 合わせる → (カメラ, モデルの 行列)"""
    ex, ey = Mo['eye']; mx, my = Mo['muzzle']
    L_t = math.hypot(mx - ex, my - ey); A_t = math.atan2(my - ey, mx - ex)
    E = LM['eye']
    Z = np.array([-1.0, 0.0, 0.0])
    th, dist = 0.0, 1.2
    for it in range(40):
        R = rot_x(th)
        Mm = m44(np.eye(3))
        Mm[:3, :3] = R; Mm[:3, 3] = E - R @ E                                     # 目の まわりで 回す
        Mz = xf(Mm, LM['muzzle'])
        U = nrm(Mz - E); U = nrm(U - Z * (U @ Z))
        V3 = nrm(np.cross(Z, U))
        if V3[1] < 0:
            V3 = -V3
        d = nrm(Z + U * u + V3 * v)
        cam_p = E + d * dist
        tgt = E.copy()
        for _ in range(12):                                                       # 目を 画面の (ex, ey) に
            cam = Camera.look_at(cam_p, tgt, up=(0, 1, 0), fov_y=FOV, W=W, H=H)
            pe = project(cam, E)[0]
            fw = nrm(tgt - cam_p); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
            th_ = math.tan(math.radians(FOV) / 2); asp = W / H
            D = np.linalg.norm(E - cam_p)
            tgt = tgt - rt * ((ex - pe[0]) / W * 2 * th_ * asp * D * .9) + up * ((ey - pe[1]) / H * 2 * th_ * D * .9)
        cam = Camera.look_at(cam_p, tgt, up=(0, 1, 0), fov_y=FOV, W=W, H=H)
        pe, pm = project(cam, np.array([E, Mz]))
        L_c = math.hypot(*(pm - pe)); A_c = math.atan2(pm[1] - pe[1], pm[0] - pe[0])
        dist *= (L_c / L_t) ** .9                                                  # 大きさ
        th -= (A_c - A_t) * .8                                                     # 頭の 上げ下げ（θ が 大きい ほど 鼻が 下がる）
        if abs(L_c - L_t) < .5 and abs(A_c - A_t) < 2e-4:
            break
    return cam, Mm


def classify(alb):
    """色で 分ける：たてがみ（あざやかな むらさき）・白い 星・目（明るい むらさき白）・毛（黒）"""
    hsv = cv2.cvtColor(np.clip(alb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
    h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    mane = ((h > 250) & (h < 320) & (s_ > .55) & (v > .25)).astype(np.float32)
    star = ((s_ < .25) & (v > .55)).astype(np.float32)
    return mane, star, v


def face_glb(t, st, Mo, W, H):
    """顔の 場面の 秒 t・その 時の 前の 顔の 数（st：L＝顔の 光・g＝目の 火）・前の 顔の しるし Mo
       → R（rgb：光を つけた 線形の 色（すき通しを かけた もの）・a・mane：たてがみ）・M（この 馬の しるし：画面の 場所）"""
    if FACE_V != 'v1':
        return face_glb2(t, st, Mo, W, H)
    prims = model('horse')
    cam, Mm = face_cam(Mo, st['u'], st['v'], W, H)
    fr = render(prims, cam, NOLIGHT, ss=SS_FACE, model_matrix=Mm, ao_strength=0.0, rim=None, want=('alpha', 'albedo', 'normal', 'pos'))
    E = LM['eye']
    col, A, mane = shade_face(fr, cam, E, st)
    R = dict(rgb=col * A[..., None], a=A, mane=mane * A)
    pts = np.array([E, xf(Mm, LM['muzzle']), xf(Mm, LM['nose']), xf(Mm, LM['chin']), xf(Mm, LM['poll'])])
    pe2 = project(cam, pts)
    M = dict(eye=pe2[0].tolist(), muzzle=pe2[1].tolist(), nose=pe2[2].tolist(), chin=pe2[3].tolist(), poll=pe2[4].tolist(), crest=[pe2[4].tolist()] * 2)
    return R, M


def shade_face(fr, cam, E, st):
    """G バッファ → 線形の 色（前の 馬と 同じ 光）。E＝目（世界）"""
    A = fr['alpha']; alb = fr['albedo']; N = fr['normal']; P = fr['pos']
    L, g = st['L'], min(st['g'], 1.0)
    eyeW = cam.eye
    V = P - eyeW[None, None, :]
    V = -V / (np.linalg.norm(V, axis=-1, keepdims=True) + 1e-9)
    tgt = E                                                                       # 前の 光の 向き（cd：ねらいから カメラへ）
    cd = nrm(eyeW - tgt)
    mane, star, val = classify(alb)
    # 色：毛は ほとんど 黒（前の 馬と 同じ くらい）・たてがみは むらさき（ふちの 光で 光る）・星は 少し
    k_alb = (0.32 * (1 - mane) * (1 - star) + 0.42 * mane + 0.12 * star)[..., None]
    base = alb * k_alb
    k = 0.03 + 0.97 * L
    # 前の 馬の 光と 同じ（前の 馬は +x が 前・+z が カメラの がわ → この 馬は +z が 前・−x が カメラの がわ：(a, b, c) → (−c, b, a)）
    o2n = lambda a: np.array([-a[2], a[1], a[0]])
    lights = [(nrm(cd * 0.55 + o2n((-0.55, 0.75, 0.15))), np.array([0.32, 0.28, 0.42]) * k, 'front'),
              (nrm(-cd + o2n((0.45, 0.45, 0.0))), np.array([6.5, 1.5, 4.8]) * L, 'back'),           # うしろ上から 鼻の 方へ：ひたい・鼻すじの ふち
              (nrm(-cd + o2n((-0.6, -0.15, 0.0))), np.array([1.3, 1.9, 5.2]) * L, 'back'),
              (nrm(-cd * 0.6 + o2n((0.0, 1.0, 0.0))), np.array([1.8, 1.6, 2.4]) * L, 'back')]
    ndv = np.clip((N * V).sum(-1), 0, 1)
    fres = 1 - ndv
    col = np.zeros_like(alb)
    rough = np.where(mane > .5, .5, .38)
    de = np.linalg.norm(P - E[None, None, :], axis=-1)
    near_eye = np.clip((de - 0.04) / 0.08, 0.1, 1.0)                              # 目の すぐ まわりは ふちの 光・つやを 弱く（目の 火が 主役）
    for Ld, lc, kind in lights:
        ndl = (N * Ld[None, None, :]).sum(-1)
        dif = np.clip(ndl, 0, 1)
        Hh = Ld[None, None, :] + V; Hh /= np.linalg.norm(Hh, axis=-1, keepdims=True) + 1e-9
        sp = ggx(N, Hh, Ld[None, None, :], V, rough) * (0.04 + 0.96 * fres ** 5)
        col = col + base * dif[..., None] * lc + (sp * 0.25 * near_eye)[..., None] * lc
        if kind == 'back':                                                        # うしろからの 光：横顔の ふち（ひたい・鼻すじ）が 強く 光る（前の 馬と 同じ）
            rim = fres ** 3.0 * np.clip(ndl + 0.35, 0, 1) * near_eye
            col = col + (rim * (0.55 + 0.9 * mane))[..., None] * lc
    # 背景の 光（前と 同じ うすい むらさき）
    lob = nrm(-cd + o2n((0.35, 0.55, 0.0)))
    Rv = 2 * ndv[..., None] * N - V
    env = np.clip((Rv * lob[None, None, :]).sum(-1), 0, 1) ** 6.0
    col = col + (env * fres ** 2 * 0.35)[..., None] * np.array([1.1, 0.28, 0.95]) * k
    col = col + (np.clip(N[..., 1], 0, 1) * 0.02 + 0.01)[..., None] * np.array([0.18, 0.16, 0.26]) * k * base * 10
    # 目の 火が まわりを 照らす（前の plight と 同じ 色）
    pe = E + cd * 0.04 + np.array([0, 0.008, 0])
    dv = pe[None, None, :] - P
    dd = np.linalg.norm(dv, axis=-1) + 1e-6
    ndl = np.clip((N * (dv / dd[..., None])).sum(-1), 0, 1)
    pl = np.array([0.05 * g + 0.004, 0.022 * g + 0.001, 0.004 * g]) * 0.25
    col = col + (base * 6 + 0.02)[..., :] * (ndl / (dd ** 2 * 400 + 1))[..., None] * pl * 40
    # この 馬の 目（むらさき）：火の 下に 少し 見える
    em = np.clip(1 - de / 0.045, 0, 1) ** 1.5 * np.clip(val - .3, 0, 1)
    col = col + em[..., None] * np.array([0.5, 0.12, 0.9]) * (0.15 + 0.85 * g) * 0.12
    return col, A, mane


# ---------------------------------------------------------------- 第2稿（まさちゃん 09:54・10:13：まつ毛なし・ひたいの こぶを 平らに・首を 動かさず 頭だけ 上げる・
#                                                                 鼻の 穴から 3D の 息・体を はう むらさきと 白の 雷）。SD_FACE=v1 で 第1稿に もどせる
FACE_V = os.environ.get('SD_FACE', 'v2')
TH0_DEG = dict(nightmare=-5.37, nightmane=float(os.environ.get('SD_TH0', '8.28')))[HORSE_KIND]
TH0 = math.radians(TH0_DEG)                   # 第1稿の はじめの コマの 胸像の 上げ下げ（目の まわり）。第2稿は ずっと これ（首は 動かさない）
FV2 = {}
HOOKS = {}                                    # shiden_film が わたす：state（秒 → 顔の 数）・marks（顔の 数 → 前の 顔の しるし）・t_of（コマ → 秒）・W・H


def horse_v2():
    """まつ毛を 消し ひたいの こぶを 平らに した 馬（1回だけ 作る）・頭の 重み・たてがみの しるし"""
    if 'p' not in FV2:
        import shiden_face2 as F2
        import time
        t0 = time.time()
        p0 = model('horse')[0]
        eyes = (LM['eye'], LM['eye_r'])
        if HORSE_KIND == 'nightmare':
            p1, lg1 = F2.lashless(p0, eyes)
            p2, lg2 = F2.brow_flat(p1, eyes)
            del p1
        else:                                                                    # Violet_Nightmane：まつ毛も ひたいの こぶも ない → そのまま
            p2, lg1, lg2 = p0, [], []
        del p0
        _MD.pop('horse', None)
        hair = F2.hair_of(F2.vert_albedo(p2, np.arange(len(p2.pos))))
        FV2.update(p=p2, w=F2.head_w(p2.pos), wb=F2.body_w(p2.pos), hair=hair, F2=F2)
        print('horse v2: まつ毛', lg1, 'ひたい', [(n, round(a, 4), round(b, 4)) for n, a, b in lg2], round(time.time() - t0, 1), 's', flush=True)
    return FV2


def face_cam2(Mo, u, v, W, H, Ed, Mzd):
    """第2稿の カメラ：胸像（首）は TH0 で 止めた まま。カメラの 向きの 作り方は 前と 同じ（頭の 向き U・V は 動かない 胸像の もの）。
       頭を 上げて 動いた 目を 前の 目の 画面の 場所に、目〜鼻先の 長さを 前と 同じに（きょり）"""
    ex, ey = Mo['eye']; mx, my = Mo['muzzle']
    L_t = math.hypot(mx - ex, my - ey)
    E0 = LM['eye']
    R = rot_x(TH0)
    Mm = m44(R); Mm[:3, 3] = E0 - R @ E0
    Ew, Mw = xf(Mm, Ed), xf(Mm, Mzd)
    Z = np.array([-1.0, 0.0, 0.0])
    U = nrm(xf(Mm, LM['muzzle']) - E0); U = nrm(U - Z * (U @ Z))
    V3 = nrm(np.cross(Z, U))
    if V3[1] < 0:
        V3 = -V3
    d = nrm(Z + U * u + V3 * v)
    dist = 1.2
    th_ = math.tan(math.radians(FOV) / 2); asp = W / H
    for it in range(40):
        cam_p = Ew + d * dist
        tgt = Ew.copy()
        for _ in range(12):
            cam = Camera.look_at(cam_p, tgt, up=(0, 1, 0), fov_y=FOV, W=W, H=H)
            pe = project(cam, Ew)[0]
            fw = nrm(tgt - cam_p); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
            D = np.linalg.norm(Ew - cam_p)
            tgt = tgt - rt * ((ex - pe[0]) / W * 2 * th_ * asp * D * .9) + up * ((ey - pe[1]) / H * 2 * th_ * D * .9)
        cam = Camera.look_at(cam_p, tgt, up=(0, 1, 0), fov_y=FOV, W=W, H=H)
        pe, pm = project(cam, np.array([Ew, Mw]))
        L_c = math.hypot(*(pm - pe))
        dist *= (L_c / L_t) ** .9
        if abs(L_c - L_t) < .3:
            break
    return cam, Mm


def head_phi_t(t):
    fv = horse_v2()
    return fv['F2'].head_phi(t) if os.environ.get('SD_HEADUP', '1') != '0' else 0.0


def deformer(phi):
    F2 = horse_v2()['F2']
    to_m = lambda P: F2.deform_pts(np.atleast_2d(P), phi)
    to_mn = lambda P, Nn: F2.deform_vec(np.atleast_2d(P), np.atleast_2d(Nn), phi)
    return to_m, to_mn


CAMS = {}


def cam_v2(f):
    """コマ f の カメラ（第2稿）：(cam, Mm, φ)"""
    if f not in CAMS:
        t = HOOKS['t_of'](f)
        st = HOOKS['state'](t)
        Mo = HOOKS['marks'](st)
        phi = head_phi_t(t)
        to_m, _ = deformer(phi)
        Ed, Mzd = to_m(np.array([LM['eye'], LM['muzzle']]))
        cam, Mm = face_cam2(Mo, st['u'], st['v'], HOOKS['W'], HOOKS['H'], Ed, Mzd)
        CAMS[f] = (cam, Mm, phi)
    return CAMS[f]


# ---------------------------------------------------------------- 第3稿（まさちゃん 12:24「雷もっと自然にして！」）：
#   3D（G バッファと 光を つけた 色）と 2D（雷・息・仕上げ）を わける。3D は 1回だけ 描いて buf/ に のこし、雷などは buf から 何回でも 作り直せる
def face_buffers(t, st, Mo, W, H):
    """3D だけ：頭を 上げた 馬を 描いて 光を つける → B（col：すき通しを かけた 線形の 色・A・mane・P：世界の 場所・N：向き・cam・Mm・φ・M・hs）"""
    fv = horse_v2(); F2 = fv['F2']
    phi = head_phi_t(t)
    prim = F2.skin2(fv['p'], fv['w'], fv['wb'], phi)
    to_m, to_mn = deformer(phi)
    Ed, Mzd, Nzd, Chd, Pld = to_m(np.array([LM['eye'], LM['muzzle'], F2.NOSE_C, LM['chin'], LM['poll']]))
    cam, Mm = face_cam2(Mo, st['u'], st['v'], W, H, Ed, Mzd)
    fr = render([prim], cam, NOLIGHT, ss=SS_FACE, model_matrix=Mm, ao_strength=0.0, rim=None, want=('alpha', 'albedo', 'normal', 'pos'))
    del prim
    E = xf(Mm, Ed)
    col, A, mane = shade_face(fr, cam, E, st)
    pts = np.array([E, xf(Mm, Mzd), xf(Mm, Nzd), xf(Mm, Chd), xf(Mm, Pld)])
    pe2 = project(cam, pts)
    M = dict(eye=pe2[0].tolist(), muzzle=pe2[1].tolist(), nose=pe2[2].tolist(), chin=pe2[3].tolist(), poll=pe2[4].tolist(), crest=[pe2[4].tolist()] * 2)
    hs = math.hypot(*(pe2[1] - pe2[0])) / (817 * W / 780.0)
    return dict(col=col * A[..., None], A=A, mane=mane * A, P=fr['pos'], N=fr['normal'], cam=cam, Mm=Mm, phi=phi, M=M, hs=hs, E=E)


def _oct_enc(n):
    n = n / (np.abs(n).sum(-1, keepdims=True) + 1e-9)
    x, y, z = n[..., 0], n[..., 1], n[..., 2]
    ox = np.where(z >= 0, x, (1 - np.abs(y)) * np.sign(x + 1e-12))
    oy = np.where(z >= 0, y, (1 - np.abs(x)) * np.sign(y + 1e-12))
    return np.round((np.stack([ox, oy], -1) * 0.5 + 0.5) * 65535).astype(np.uint16)


def _oct_dec(e):
    f = e.astype(np.float32) / 65535 * 2 - 1
    x, y = f[..., 0], f[..., 1]
    z = 1 - np.abs(x) - np.abs(y)
    t_ = np.clip(-z, 0, None)
    x = x - np.sign(x + 1e-12) * t_ * (z < 0)
    y = y - np.sign(y + 1e-12) * t_ * (z < 0)
    n = np.stack([x, y, z], -1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def save_buf(path, B):
    cam = B['cam']
    dep = np.linalg.norm(B['P'] - cam.eye[None, None, :], axis=-1)
    dep = np.where(B['A'] > 0.002, dep, 0.0)
    tmp = path[:-4] + '_tmp.npz'
    np.savez_compressed(tmp, col=B['col'].astype(np.float16), A=np.round(np.clip(B['A'], 0, 1) * 255).astype(np.uint8),
                        mane=np.round(np.clip(B['mane'], 0, 1) * 255).astype(np.uint8), dep=dep.astype(np.float32), N=_oct_enc(B['N']),
                        view=cam.view, proj=cam.proj, WH=np.array([cam.W, cam.H]), fov=np.array([cam.fov_y]), Mm=B['Mm'], phi=np.array([B['phi']]),
                        hs=np.array([B['hs']]), E=B['E'], M=np.array(json.dumps(B['M'])))
    os.replace(tmp, path)


def load_buf(path):
    z = np.load(path)
    W_, H_ = int(z['WH'][0]), int(z['WH'][1])
    cam = Camera(z['view'], z['proj'], W_, H_)
    cam.fov_y = float(z['fov'][0])
    A = z['A'].astype(np.float32) / 255
    dep = z['dep'].astype(np.float32)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    nx = (xx + 0.5) / W_ * 2 - 1; ny = 1 - (yy + 0.5) / H_ * 2
    iv = np.linalg.inv(cam.proj)
    d = np.stack([nx * iv[0, 0], ny * iv[1, 1], -np.ones_like(nx)], -1)        # 目の 前の 向き（カメラの 座標）
    d = d @ cam.inv_view[:3, :3].T
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    P = cam.eye[None, None, :] + d * dep[..., None]
    return dict(col=z['col'].astype(np.float32), A=A, mane=z['mane'].astype(np.float32) / 255, dep=dep, P=P, N=_oct_dec(z['N']), cam=cam, Mm=z['Mm'],
                phi=float(z['phi'][0]), hs=float(z['hs'][0]), E=z['E'], M=json.loads(str(z['M'])))


_BUFC = {}


def buf_at(f):
    """コマ f の G バッファ（HOOKS['buf'] から・少し とっておく）"""
    if f not in _BUFC:
        while len(_BUFC) > 4:
            _BUFC.pop(next(iter(_BUFC)))
        _BUFC[f] = load_buf(os.path.join(HOOKS['buf'], 'b%03d.npz' % f))
    return _BUFC[f]


def face_layers(f, t, st, B, W, H):
    """2D だけ（G バッファ B から）：第3稿の 雷（Arcs3）・息（Breath）→ R（face_frame に わたす）。3D の 馬の 網は 使わない"""
    import shiden_face2 as F2
    R = dict(rgb=B['col'], a=B['A'], mane=B['mane'])
    L = st['L']
    s2 = W / 780.0
    Mm, phi = B['Mm'], B['phi']
    to_w = lambda X: xf(Mm, F2.deform_pts(X, phi))
    inv_skin = lambda Xd, ph: F2.undeform_pts(Xd, ph)
    if os.environ.get('SD_ARCS', '1') != '0':
        if 'arcs3' not in FV2:
            FV2['arcs3'] = F2.Arcs3(HOOKS['f_on'], HOOKS['f_end'])
        C, Hot, AG, lit, n_on = FV2['arcs3'].frame(f, B, buf_at, project, to_w, inv_skin, s2, 0.085)
        R['bolt'] = F2.arcs3_glow(C, Hot, AG, s2 * (0.75 + 0.35 * B['hs']))
        R['blit'] = lit
        R['blit_k'] = 0.55 + 0.45 * L
        R['n_arcs'] = n_on
    if os.environ.get('SD_BREATH', '1') != '0':
        if 'breath2' not in FV2:
            hp = (lambda tt: F2.head_phi(tt)) if os.environ.get('SD_HEADUP', '1') != '0' else (lambda tt: 0.0)

            def nose_at(te):
                te = np.asarray(te, float)
                c = np.zeros((len(te), 3)); d = np.zeros((len(te), 3))
                for j, tt in enumerate(te):
                    ph = hp(tt)
                    c[j] = F2.deform_pts(F2.NOSE_C[None], ph)[0]; d[j] = F2.deform_vec(F2.NOSE_C[None], F2.NOSE_D[None], ph)[0]
                return c, d
            FV2['breath2'] = F2.Breath(nose_at)
        R['vap'] = FV2['breath2'].layer(t, B['cam'], project, B['P'], B['A'], W, H, L, (lambda X: xf(Mm, X)), nrm(np.array([0.55, -0.8])))
    return R


def face_glb2(t, st, Mo, W, H):
    fv = horse_v2(); F2 = fv['F2']
    f = HOOKS['f_of'](t)
    phi = head_phi_t(t)
    prim = F2.skin2(fv['p'], fv['w'], fv['wb'], phi)
    to_m, to_mn = deformer(phi)
    Ed, Mzd, Nzd, Chd, Pld = to_m(np.array([LM['eye'], LM['muzzle'], F2.NOSE_C, LM['chin'], LM['poll']]))
    cam, Mm = face_cam2(Mo, st['u'], st['v'], W, H, Ed, Mzd)
    fr = render([prim], cam, NOLIGHT, ss=SS_FACE, model_matrix=Mm, ao_strength=0.0, rim=None, want=('alpha', 'albedo', 'normal', 'pos'))
    del prim
    E = xf(Mm, Ed)
    col, A, mane = shade_face(fr, cam, E, st)
    R = dict(rgb=col * A[..., None], a=A, mane=mane * A)
    pts = np.array([E, xf(Mm, Mzd), xf(Mm, Nzd), xf(Mm, Chd), xf(Mm, Pld)])
    pe2 = project(cam, pts)
    M = dict(eye=pe2[0].tolist(), muzzle=pe2[1].tolist(), nose=pe2[2].tolist(), chin=pe2[3].tolist(), poll=pe2[4].tolist(), crest=[pe2[4].tolist()] * 2)
    hs = math.hypot(*(pe2[1] - pe2[0])) / (817 * W / 780.0)
    L = st['L']; k_l = 0.03 + 0.97 * L
    P, N = fr['pos'], fr['normal']
    s2 = W / 780.0
    # ---------- 体を はう 雷 ----------
    if os.environ.get('SD_ARCS', '1') != '0':
        if 'arcs' not in FV2:
            f_on = HOOKS['f_on']; f_end = HOOKS['f_end']
            FV2['arcs'] = F2.Arcs(fv['p'], fv['hair'], f_on, f_end)

        def cam_at(f0):
            c0, M0, ph0 = cam_v2(f0)
            tm, tmn = deformer(ph0)
            return c0, (lambda X: xf(M0, tm(X))), (lambda X, Nn: (M0[:3, :3] @ tmn(X, Nn).T).T)

        def eye_at(f0):
            c0, M0, ph0 = cam_v2(f0)
            tm, _ = deformer(ph0)
            return project(c0, xf(M0, tm(LM['eye'][None])))[0]
        to_w = lambda X: xf(Mm, to_m(X))
        cW, cP, spk, lit, n_on = FV2['arcs'].frame(f, cam, to_w, cam_at, project, eye_at, P, A, N, W, H, hs, 0.10 + 0.05 * (1 - L))
        R['bolt'] = F2.arcs_glow(cW, cP, spk, s2 * (0.75 + 0.4 * hs))
        R['blit'] = lit
        R['n_arcs'] = n_on
    # ---------- 鼻息 ----------
    if os.environ.get('SD_BREATH', '1') != '0':
        if 'breath' not in FV2:
            def nose_at(te):
                te = np.asarray(te, float)
                c = np.zeros((len(te), 3)); d = np.zeros((len(te), 3))
                for j, tt in enumerate(te):
                    tm, tmn = deformer(head_phi_t(tt))
                    c[j] = tm(F2.NOSE_C[None])[0]; d[j] = tmn(F2.NOSE_C[None], F2.NOSE_D[None])[0]
                return c, d
            FV2['breath'] = F2.Breath(nose_at)
        R['vap'] = FV2['breath'].layer(t, cam, project, P, A, W, H, L, (lambda X: xf(Mm, X)), nrm(np.array([0.55, -0.8])))
    return R, M


# ================================================================ 蹄（Violet_Hoof_Flame）
HF = {}


def hoof_model():
    """足を 立った 向き（前の shiden_hoof.py の 立った 座標：x 前・y 上・z 横・地面 y=0）へ：
       この GLB は 前が +z・上が +y（足は ななめ）。裏を 地面に、つま先を +x に、裏の まん中を 前の 蹄の 裏の まん中に、大きさを 前の 蹄に 合わせる"""
    if 'M' not in HF:
        import shiden_hoof as SH
        pr = model('hoof')
        Vt = np.concatenate([p.pos for p in pr])
        ymin = Vt[:, 1].min()
        bot = Vt[Vt[:, 1] < ymin + .03]
        Sc = bot.mean(0)
        r = np.hypot(bot[:, 0] - Sc[0], bot[:, 2] - Sc[2])
        toe = bot[np.argmax(bot[:, 2])]
        a = math.atan2(toe[0] - Sc[0], toe[2] - Sc[2])                         # つま先の 向き（+z から）
        R = rot_y(math.pi / 2) @ rot_y(-a)                                       # つま先 → +z → +x（立った 座標の 前）
        sc = (SH.R0 + 0.008) / float(np.percentile(r, 75))                        # 裏の ふとさを 前の 蹄に（蹄鉄の ぶん 少し 大きく）
        out, u, e1 = SH.sole_outline(96)
        cx = float(out[:, 0].mean())
        Ms = m44(R, s=sc)
        Ms[:3, 3] = np.array([cx, 0.0, 0.0]) - xf(Ms, np.array([Sc[0], ymin, Sc[2]]))
        Rw = np.array([[0, -1.0, 0], [1.0, 0, 0], [0, 0, 1.0]])                  # 立った 座標 → 絵の 世界（足の 下 → 右・つま先 → 上）
        # この 足は ななめに 立って いる（蹄は 地面に 平ら・すねが 後ろへ たおれる）ので、絵の 中で 前の 足と 同じ 向き（すねが ほぼ よこ）に なる よう
        # 蹄の 裏の まん中の まわりに 少し 回す（絵で 時計まわり）
        ph = math.radians(float(os.environ.get('SD_HOOF_TILT', '-15')))
        c_, s_ = math.cos(ph), math.sin(ph)
        sw = Rw @ np.array([cx, 0.0, 0.0])
        Rz = np.array([[c_, -s_, 0], [s_, c_, 0], [0, 0, 1.0]])
        Mt = m44(Rz, sw - Rz @ sw) @ m44(Rw)                                      # 立った 座標 → 絵の 世界（回した あと）
        Mw = Mt @ Ms
        HF.update(M=Mw, Ms=Ms, Mt=Mt, sc=sc, R0=SH.R0, prims=pr)
        st = xf(Ms, Vt)
        HF['toe_st'] = st[np.argmax(np.where(st[:, 1] < .004, st[:, 0], -9))]       # 立った 座標の つま先（地面の 上で いちばん 前）
        fet_h = np.abs(st[:, 1] - 0.17) < .01                                    # 球節の 高さ（前の 蹄の HT + 0.105 くらい）
        HF['fet_st'] = st[fet_h].mean(0) if fet_h.any() else np.array([0.0, .17, 0.0])
    return HF


def hoof_layer_glb(tau, az, el, Wc, Hc, K, s2, seed=5):
    """前の hoof_layer と 同じ もどり値：（線形の 色・すき通しを かけた もの, すき通し, 蹄鉄の 光, しるし）"""
    hf = hoof_model()
    tgt = K['sole'] + np.array([-0.20, -0.035, 0.0])
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])
    camp = tgt + d * 1.24
    cam = Camera.look_at(camp, tgt, up=(0, 1, 0), fov_y=12.6, W=Wc, H=Hc)
    fr = render(hf['prims'], cam, NOLIGHT, ss=2, model_matrix=hf['M'], ao_strength=0.0, rim=None, want=('alpha', 'albedo', 'normal', 'pos'))
    A = fr['alpha']; alb = fr['albedo']; N = fr['normal']; P = fr['pos']
    V = camp[None, None, :] - P
    V = V / (np.linalg.norm(V, axis=-1, keepdims=True) + 1e-9)
    cd = nrm(camp - tgt)
    # 立った 座標（地面からの 高さ・裏の まん中からの きょり）
    Mi = np.linalg.inv(hf['Mt'])
    stp = P @ Mi[:3, :3].T + Mi[:3, 3]
    hgt = stp[..., 1]
    import shiden_hoof as SH
    out, u, e1 = SH.sole_outline(96)
    cx = float(out[:, 0].mean())
    rad = np.hypot(stp[..., 0] - cx, stp[..., 2])
    sole = (hgt < 0.006).astype(np.float32) * A                                 # 裏（地面に つく 面）
    ring = sole * np.clip((rad - hf['R0'] * .55) / (hf['R0'] * .25), 0, 1)        # 裏の ふちの 輪（焼けた 蹄鉄）
    wall = np.clip(1 - hgt / 0.03, 0, 1) * (1 - sole) * A                         # 蹄の かべの 下（蹄鉄の 光で だいだいに 照る）
    base = alb * 0.75
    lights = [(nrm(cd * 0.7 + np.array([-0.3, 0.9, 0.0])), np.array([0.7, 0.65, 0.9]) * .5, 0),
              (nrm(-cd + np.array([0.0, 0.9, 0.0])), np.array([2.6, 1.1, 3.0]), 1),
              (nrm(-cd + np.array([0.3, -0.8, 0.0])), np.array([0.9, 1.4, 3.4]), 1),
              (nrm(-cd + np.array([0.9, 0.2, 0.0])), np.array([2.4, 1.8, 3.2]), 1)]
    ndv = np.clip((N * V).sum(-1), 0, 1)
    fres = 1 - ndv
    col = np.zeros_like(alb)
    for Ld, lc, back in lights:
        ndl = (N * Ld[None, None, :]).sum(-1)
        dif = np.clip(ndl, 0, 1)
        Hh = Ld[None, None, :] + V; Hh /= np.linalg.norm(Hh, axis=-1, keepdims=True) + 1e-9
        sp = ggx(N, Hh, Ld[None, None, :], V, .36) * (0.04 + 0.96 * fres ** 5)
        rim = 0.8 * fres ** 3.0 * np.clip(ndl + 0.3, 0, 1) if back else 0.0
        col = col + base * dif[..., None] * lc * .5 + (sp * 0.3)[..., None] * lc + (rim * 0.35 if back else 0 * dif)[..., None] * lc
    lob = nrm(np.array([-0.2, 0.9, -0.4]))
    Rv = 2 * ndv[..., None] * N - V
    col = col + (np.clip((Rv * lob).sum(-1), 0, 1) ** 6 * fres ** 2 * .3)[..., None] * np.array([0.6, 0.25, 0.7])
    hot = np.array([2.2, 0.45, 0.07])
    col = col + wall[..., None] * np.array([0.5, 0.1, 0.02]) * (base.mean(-1, keepdims=True) * 4 + .15)
    col = col * (1 - sole[..., None] * .7) + sole[..., None] * np.array([0.05, 0.012, 0.004])
    col = col * (1 - ring[..., None] * .6) + ring[..., None] * hot
    shoe = cv2.GaussianBlur(ring, (0, 0), .6)
    Mw = hf['M']
    Pj = lambda p: project(cam, xf(hf['Mt'], p))
    toe = Pj(hf['toe_st'])[0]; fet = Pj(hf['fet_st'])[0]
    Mk = dict(toe=[toe.tolist()], fet=[fet.tolist()], sole=Pj(np.array([cx, 0, 0])).tolist(), crown=Pj(np.array([cx, .06, 0])).tolist(),
              ergot=[(fet + np.array([-40 * s2, 20 * s2])).tolist()])
    yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
    fade = np.clip((xx - (fet[0] - 470 * s2)) / (350 * s2), 0, 1)
    fade = fade * fade * (3 - 2 * fade)                                           # 足の 左の はしは 闇へ（前と 同じ）
    col = col * fade[..., None]; a_ = A * fade
    glow = cv2.GaussianBlur(shoe, (0, 0), 3 * s2)[..., None] * np.array([1.0, 0.22, 0.05]) + cv2.GaussianBlur(shoe, (0, 0), 14 * s2)[..., None] * np.array([0.6, 0.08, 0.12])
    return col * a_[..., None], a_, glow, Mk
