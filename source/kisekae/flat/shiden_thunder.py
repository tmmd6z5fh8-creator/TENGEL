"""極ど的中（紫電）の 顔の 場面（54〜113コマ・2.0秒）を まさちゃんの 3D「Violet Thunder」で 描く（第4.195版）

まさちゃん（2026/11/18 12:02）「極ど的中の演出、このファイルの3Dと入れ替えて！ かなり顔をアップにして作成して！
  顔は、ゆっくり上下小さく、左右大きく顔を揺らすように、とまってる画像ではなく、生きてる馬のように演出して！」
  ・顔の 場面の 長さは 今の 2.0秒の まま（まさちゃんが えらんだ）。顔が 見えて くる → 鼻息 2回 → 体を はう 雷 → 目の 光に つつまれる、の 時刻は 前と 同じ
    （shiden.py の FILM：LIT・PUFFS・RUSH ＝ 音 sfx_sd と そろう）
  ・馬：Violet Thunder（黒い 馬の 胸像・むらさきの 長い たてがみ・こわい 眉・むらさきの 目：三角 528万・骨なし）。+z が 前・+y が 上。
    顔の まん中の 線は x＝0.175（たてがみが 馬の 右がわ −x へ 大きく 出て いる ので 胸像の まん中は ずれて いる）
  ・右前から かなり アップ（目 2つが 画面に 入る・馬が 画面の 6〜7割）。頭は 首の 付け根（環椎）の まわりに：左右へ 大きく ゆっくり（±8°・1.6秒で 1往復・目が 光りはじめて から 大きく）・
    上下に 小さく（±1.8°・鼻息で 少し 上げる）・回る 向きへ 少し かたむく。カメラは ゆれを 5割 追う（手持ちの ような 小さな ゆれ）
  ・角度（12:22「スタートは一枚目くらいの顔の角度からスタートして、カメラが移動して顔を上げると二枚目くらいの顔の角度にして！」・
    13:29「スタートの顔の角度もっと下向いてて！光るのは左目で、目が光り始めてから今の角度になる。」）：
    はじめは 頭を 26° 下げて、カメラは 右前（16°）の 上（24°）から 見おろす → 目が 光りだして から 顔を 上げ（0.2〜0.95秒）、カメラも おりて
    （〜1.3秒）右前（22°）の ほぼ 横（6°）→ 近い 目へ 寄って 光に つつまれる
  ・目（13:29「目は徐々に光りが強くなり、顔が見える頃には両目が光るようにして！あと目の光りは紫で、もっとリアルに！」）：
    画面の 左の 目（カメラに 近い 目）が 0.10秒から だんだん 光る → もう 一つも 0.36秒から ともって 0.8秒には 両目（FIRST_EYE・EYE_KEYS・EYE_BOTH）。
    光は 紫：3D の 瞳の 形 そのものが 光って 形の まま にじむ（eye_masks・comp）・まぶたや 眉を 紫に 照らす（shade の EYE_LIGHT）・十字の 筋は なし
  ・首（12:30「首から下ないからそこが映らないようにね！」）：胸像の 首の 切れ目は 写さない（NECK：首の 下を 闇に とかす）
  ・生きて いる ように：たてがみが 頭の 動きに おくれて ついて くる・ゆらぐ／耳が ぴくっと 動く（左耳が うしろへ → 前へ）／鼻息の とき 鼻の 穴が ふくらむ
  ・3D：kisekae/r3d/glb（C の ラスタライザ）で G バッファ（色・向き・場所）を 2倍の 細かさ・たて 4つに 分けて（メモリ）描き、ここで 光を つける。
    雷（shiden_face2.Arcs3）・息（鼻の 穴 2つ）・背景・仕上げ は 前の 顔の 場面と 同じ しくみ（shiden_film の 道具）
  使い方：
    python3 kisekae/flat/shiden_thunder.py --buf  <buf>  [i0 i1]          … 3D（G バッファと 光を つけた 色）を buf/b%03d.npz に
    python3 kisekae/flat/shiden_thunder.py --comp <buf> <作業フォルダ> [i0 i1] … 雷・息・目・仕上げ → コマ f%03d.png（shiden_film と 同じ 名前）
    python3 kisekae/flat/shiden_thunder.py --splice <前の 動画> <作業フォルダ> <新しい 動画>
                                                                          … 顔 いがいの コマは 前の 動画から（54〜113 だけ 新しい コマ）→ CRF 20
    SCALE＝shiden_film と 同じ（1.5 で 1170×2532）。3D の 場所：SD_THUNDER_GLB（リポジトリに 入れない）
"""
import os, sys, math, json, time
import numpy as np
import cv2

cv2.setNumThreads(0)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import glb as GL                                                               # noqa: E402
from raster import Camera, Light, Scene, render                                # noqa: E402

GLB_PATH = os.environ.get('SD_THUNDER_GLB', '/home/claude/work/v195/glb/thunder.glb')
NOLIGHT = [Light((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), 0.0, shadow=False)]
SS = int(os.environ.get('SD_THUNDER_SS', '2'))                                   # 2倍の 細かさ（4倍の 点）
BANDS = int(os.environ.get('SD_THUNDER_BANDS', '4'))                             # たてに 分けて 描く（メモリ）

# ---------------------------------------------------------------- 馬の だいじな 点（モデルの 座標：前と 横から 描いて はかった）
XM = 0.175                                                                       # 顔の まん中の 線
LM = dict(eye_r=np.array([-0.052, 0.274, 0.486]),                                # 馬の 右の 目（正面の 画面で 左）
          eye_l=np.array([0.402, 0.243, 0.490]),                                 # 馬の 左の 目（正面の 画面で 右）
          nost_r=np.array([0.018, -0.113, 0.851]), nost_l=np.array([0.319, -0.103, 0.850]),   # 鼻の 穴
          muzzle=np.array([0.170, -0.114, 0.942]), chin=np.array([0.174, -0.370, 0.798]),
          forehead=np.array([0.178, 0.444, 0.485]),
          ear_l_tip=np.array([0.675, 0.713, 0.131]), ear_l_base=np.array([0.559, 0.485, 0.168]),
          ear_r_tip=np.array([-0.314, 0.730, 0.102]), ear_r_base=np.array([-0.209, 0.485, 0.168]))
PIVOT = np.array([XM, 0.30, 0.08])                                               # 環椎（耳の 付け根の 下・うしろ）：頭は ここの まわりに 動く
FACE_C = np.array([XM, 0.07, 0.70])                                              # 顔の まん中（目と 鼻の 穴の あいだ）：カメラが ねらう


def nrm(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def ss(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def rot_axis(ax, a):
    ax = nrm(ax); x, y, z = ax; c, s = math.cos(a), math.sin(a); C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def xf(M, p):
    p = np.asarray(p, float)
    return p @ M[:3, :3].T + M[:3, 3]


def project(cam, P):
    P = np.atleast_2d(np.asarray(P, float))
    c = np.c_[P, np.ones(len(P))] @ (cam.proj @ cam.view).T
    nd = c[:, :3] / c[:, 3:4]
    return np.c_[(nd[:, 0] + 1) / 2 * cam.W, (1 - nd[:, 1]) / 2 * cam.H]


# ---------------------------------------------------------------- 時刻（顔の 場面の 秒 τ：0〜2.0）
import shiden as SDM                                                             # noqa: E402
F = SDM.FILM
FPS = F['FPS']
BLACK, FACE = F['BLACK'], F['FACE']
FACE_LEN = FACE - BLACK                                                          # 2.0秒
PUFFS = F['PUFFS']                                                               # 鼻息（0.62・1.22秒：音と 同じ）
RUSH = F['RUSH']                                                                 # 1.5秒から 目へ 寄る


def smoother(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * t * (t * (t * 6 - 15) + 10)


# まさちゃん（12:22・Meshy の 画面 2まい）「スタートは一枚目くらいの顔の角度からスタートして、カメラが移動して顔を上げると二枚目くらいの顔の角度にして！
#   カメラのより具合は任せる！」→ はじめ＝右前の 上から 見おろす（顔は 下向き）・おわり＝右前の ほぼ 横の 高さ（顔を 上げた）
#   カメラ（頭の もとの 向きから 見た 方角）：右へ 16° → 22°・上から 24° → 6°（0.2〜1.3秒）・頭は 26° 下げた 所から 上げて 0°（0.2〜0.95秒：13:29 の 直し。
#   前は 10° → 0°）＝ 頭から 見た カメラの 高さ 約48° → 約5°。その 上に 生きて いる ゆれ（左右 ±8°〈目が 光りはじめて から 大きく〉・上下 ±1.8°・鼻息の フンッ）
UP = (0.2, float(os.environ.get('SD_THUNDER_CUP1', '1.3')))                        # カメラが おりる（秒）
# まさちゃん（13:29）「スタートの顔の角度もっと下向いてて！光るのは左目で、目が光り始めてから今の角度になる。」
#   → はじめは 頭を HEAD0 まで 下げて おく（暗闇で 左の 目が 光りはじめる）→ 光りだして から 顔を 上げて いく（HEAD_UP）
HEAD0 = float(os.environ.get('SD_THUNDER_HEAD0', '-26'))                          # はじめの 頭の 上下（度：− が 下向き。前は −10）
HEAD_UP = (0.20, float(os.environ.get('SD_THUNDER_UP1', '0.95')))                 # 顔を 上げる（秒：目が 光りはじめる 0.10秒の あと → 顔が 見える ころ〈0.8秒〉には 上げて 両目が 見える）


def base_pitch(t):
    return HEAD0 * (1.0 - smoother(HEAD_UP[0], HEAD_UP[1], t))


YAW_IN = (float(os.environ.get('SD_THUNDER_YAW0', '0.12')), float(os.environ.get('SD_THUNDER_YAW1', '0.75')))


def head_pose(t):
    """τ → (左右 yaw・上下 pitch・かたむき roll)（度・pitch＋ で 鼻が 上がる）。左右は 大きく・上下は 小さく"""
    yaw = 8.0 * float(ss(YAW_IN[0], YAW_IN[1], t)) * math.sin(2 * math.pi * t / 1.6)   # 右 → 左 → もどる（1.6秒で 1往復）：目が 光りはじめて から 大きく なる
    pitch = base_pitch(t) + 1.8 * math.sin(2 * math.pi * t / 1.1 + 0.4)
    for tp in PUFFS:                                                             # 鼻息で 少し 頭を 上げて もどす（フンッ）
        a = t - (tp - 0.06)
        if 0 <= a < 0.9:
            pitch += 2.5 * math.sin(math.pi * min(1.0, a / 0.22) * 0.5) * math.exp(-max(0.0, a - 0.22) / 0.25)
    roll = -0.25 * yaw                                                           # 回る 向きへ 少し かたむく
    return yaw, pitch, roll


def pose_of(yaw, pitch, roll, bob=0.0):
    """pitch＋ で 鼻が 上がる（＋x の まわりに ＋ 回すと 前〈＋z〉が 下〈−y〉へ 向く ので −pitch で 回す）"""
    fwd = nrm(LM['muzzle'] - PIVOT)
    R = rot_axis((0, 1, 0), math.radians(yaw)) @ rot_axis((1, 0, 0), math.radians(-pitch)) @ rot_axis(fwd, math.radians(roll))
    M = np.eye(4); M[:3, :3] = R
    M[:3, 3] = PIVOT - R @ PIVOT + np.array([0.0, bob, 0.0])
    return M


def pose_matrix(t):
    """頭の 向き（環椎の まわり）＋ 呼吸の ごく 小さな 上下"""
    return pose_of(*head_pose(t), bob=0.004 * math.sin(2 * math.pi * t / 1.9))


def pose_base(t):
    """ゆれ なしの 頭（カメラの 方角の もと）"""
    return pose_of(0.0, base_pitch(t), 0.0)


# ---------------------------------------------------------------- カメラ（右前から かなり アップ：上から おりて 寄る → おわりは 近い 目へ）
FOV = 30.0
CAM_AZ = (float(os.environ.get('SD_THUNDER_AZ0', '-16')), float(os.environ.get('SD_THUNDER_AZ1', '-22')))      # 方角（度：− が 馬の 右がわ。13:29 の 直しで 少し 前へ：顔を 上げた とき 両目が 見える）
CAM_EL = (float(os.environ.get('SD_THUNDER_EL0', '24')), 6.0)                    # 高さ（度：上から → ほぼ 横）
CAM_D = (float(os.environ.get('SD_THUNDER_D0', '3.1')), float(os.environ.get('SD_THUNDER_D1', '2.4')))     # 顔の まん中からの きょり（寄る：顔が 画面の はば いっぱい → もっと 近く）
FOLLOW = 0.55                                                                    # ゆれを 追う 割合
AIM_M = np.array([-0.09, 0.05, 0.0])                                             # ねらい：顔の まん中から 近い 目の がわへ・少し 上へ（目が 2つとも 画面に 入る・耳と たてがみの 上も）


def cam_params(t):
    u = smoother(UP[0], UP[1], t)
    return CAM_AZ[0] + (CAM_AZ[1] - CAM_AZ[0]) * u, CAM_EL[0] + (CAM_EL[1] - CAM_EL[0]) * u, CAM_D[0] + (CAM_D[1] - CAM_D[0]) * smoother(0.0, FACE_LEN, t)


def camera(t, W, H, M=None):
    M = pose_matrix(t) if M is None else M
    c_now = xf(M, FACE_C)
    c_base = xf(pose_base(t), FACE_C + AIM_M)
    c_lag = xf(pose_matrix(t - 0.12), FACE_C + AIM_M)                            # 少し おくれて 追う（手持ちの カメラ）
    tgt = c_base + (c_lag - c_base) * FOLLOW
    tgt = tgt + np.array([0.004 * math.sin(t * 2.3 + 0.4), 0.003 * math.sin(t * 3.1 + 1.3), 0.0])
    az, el, d = cam_params(t)
    a, e = math.radians(az), math.radians(el)
    dirv = np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])
    eye = tgt + dirv * d
    # おわり（RUSH〜）：目の 光へ 寄る（近い ほうの 目）
    fr = float(ss(RUSH, FACE_LEN, t))
    if fr > 0:
        E = near_eye(M, eye)
        tgt = tgt * (1 - fr) + E * fr
        eye = tgt + dirv * d * (1 - 0.72 * fr ** 1.6)
    return Camera.look_at(eye, tgt, up=(0, 1, 0), fov_y=FOV, W=W, H=H), c_now


def near_eye(M, campos):
    El, Er = xf(M, LM['eye_l']), xf(M, LM['eye_r'])
    return El if np.linalg.norm(El - campos) <= np.linalg.norm(Er - campos) else Er


# ---------------------------------------------------------------- 3D（1回だけ 読む）・生きて いる 動き（たてがみ・耳・鼻の 穴）
_MD = {}


def horse():
    if 'p' not in _MD:
        t0 = time.time()
        p = GL.load(GLB_PATH).flatten()[0]
        uv = p.uv
        tx = p.mat.base_tex.tex.img                                             # 線形の 色（0〜1）
        th, tw = tx.shape[:2]
        u = np.clip((uv[:, 0] % 1.0) * (tw - 1), 0, tw - 1).astype(np.int32)
        v = np.clip((uv[:, 1] % 1.0) * (th - 1), 0, th - 1).astype(np.int32)
        c = np.clip(tx[v, u, :3], 0, 1) ** (1 / 2.2)                             # sRGB で 見る（肌：あざやかさ 0.1〜0.25・たてがみ：0.5〜0.7）
        hsv = cv2.cvtColor(c.astype(np.float32)[None], cv2.COLOR_RGB2HSV)[0]
        mane = ((hsv[:, 0] > 250) & (hsv[:, 0] < 335) & (hsv[:, 1] > 0.38) & (hsv[:, 2] > 0.35)).astype(np.float32)
        P = p.pos.astype(np.float64)
        # たてがみの 動く 重み：肌から はなれた 毛ほど 大きく（根もとは 肌に ついた まま）・顔の まん中から はなれて たれる 毛ほど 大きく
        from scipy.spatial import cKDTree
        skin = np.nonzero(mane < .5)[0]; hair = np.nonzero(mane > .5)[0]
        dskin = np.zeros(len(P))
        dskin[hair] = cKDTree(P[skin]).query(P[hair], k=1, workers=2)[0]
        root = ss(0.012, 0.16, dskin)
        side = ss(0.05, 0.5, np.abs(P[:, 0] - XM))
        low = ss(0.6, -0.1, P[:, 1])
        wm = mane * root * np.clip(0.35 + 0.65 * side * (0.5 + 0.5 * low), 0, 1)
        # 耳（付け根から 先へ 0 → 1・たてがみ でない 所）
        we = {}
        for k in ('l', 'r'):
            b, tp = LM['ear_%s_base' % k], LM['ear_%s_tip' % k]
            ax = tp - b; L = np.linalg.norm(ax); ax = ax / L
            q = P - b; s_ = q @ ax; r = np.linalg.norm(q - np.outer(s_, ax), axis=1)
            w = ss(-0.02, 0.35, s_ / L) * (s_ < L * 1.15) * (1 - ss(0.07, 0.13, r)) * (1 - mane)
            we[k] = w.astype(np.float32)
        # 鼻の 穴の まわり（ふくらむ）
        wn = {}
        for k in ('l', 'r'):
            c0 = LM['nost_%s' % k]
            dd = np.linalg.norm(P - c0, axis=1)
            wn[k] = ((1 - ss(0.02, 0.085, dd)) * ss(0.0, 0.03, dd) * (1 - mane)).astype(np.float32)
        idx = {k: np.nonzero(w > 1e-4)[0] for k, w in (('mane', wm), ('ear_l', we['l']), ('ear_r', we['r']), ('nos_l', wn['l']), ('nos_r', wn['r']))}
        _MD.update(p=p, mane=mane, wm=wm.astype(np.float32), we=we, wn=wn, idx=idx)
        print('thunder:', len(P), 'verts・たてがみ', int(mane.sum()), '・動く たてがみ', len(idx['mane']), '・耳', len(idx['ear_l']), len(idx['ear_r']),
              '・鼻', len(idx['nos_l']), len(idx['nos_r']), round(time.time() - t0, 1), 's', flush=True)
    return _MD


def ear_angle(t, k):
    """耳の 前後（度：＋ で うしろへ）。左耳が 0.85秒に ぴくっと うしろへ → もどる・右耳は ゆっくり 少し"""
    if k == 'l':
        a = t - 0.85
        return (16.0 * math.sin(math.pi * min(1, a / 0.16) * 0.5) * math.exp(-max(0.0, a - 0.16) / 0.30) if a >= 0 else 0.0) + 2.0 * math.sin(t * 2.1)
    return 4.0 * math.sin(2 * math.pi * t / 1.6 + 1.0)


def flare(t):
    """鼻の 穴の ふくらみ（0〜1）：鼻息の すこし 前から"""
    f = 0.0
    for tp in PUFFS:
        a = t - (tp - 0.12)
        if 0 <= a < 0.7:
            f = max(f, math.sin(math.pi * min(1, a / 0.14) * 0.5) * math.exp(-max(0.0, a - 0.14) / 0.22))
    return f


def posed_prim(t):
    """τ の ときの 馬（モデルの 座標・頭の 向きは 入れない）：たてがみの おくれと ゆらぎ・耳・鼻の 穴"""
    D = horse(); p = D['p']
    pos = p.pos.copy(); nrm_ = p.nrm.copy(); tan = p.tangent.copy() if p.tangent is not None else None

    def rot_part(ii, R_each, origin):
        """ii の 点を origin の まわりに 回す（R_each：(n,3,3)）"""
        q = pos[ii] - origin
        pos[ii] = origin + np.einsum('nij,nj->ni', R_each, q)
        nrm_[ii] = np.einsum('nij,nj->ni', R_each, nrm_[ii])
        if tan is not None:
            tan[ii, :3] = np.einsum('nij,nj->ni', R_each, tan[ii, :3])

    def rot_w(axis, ang_each):
        """角度（点ごと）と 軸 → 回す 行列（ロドリゲス）"""
        ax = nrm(np.asarray(axis, float)); x, y, z = ax
        c, s = np.cos(ang_each), np.sin(ang_each); C = 1 - c
        R = np.empty((len(ang_each), 3, 3), np.float32)
        R[:, 0, 0] = c + x * x * C; R[:, 0, 1] = x * y * C - z * s; R[:, 0, 2] = x * z * C + y * s
        R[:, 1, 0] = y * x * C + z * s; R[:, 1, 1] = c + y * y * C; R[:, 1, 2] = y * z * C - x * s
        R[:, 2, 0] = z * x * C - y * s; R[:, 2, 1] = z * y * C + x * s; R[:, 2, 2] = c + z * z * C
        return R
    # たてがみ：頭の 左右の 動きに おくれる（0.16秒）＋ 風で ゆらぐ
    ii = D['idx']['mane']; w = D['wm'][ii]
    y_now, y_lag = head_pose(t)[0], head_pose(t - 0.16)[0]
    lag = math.radians(y_lag - y_now) * 1.15
    P = pos[ii]
    wave = 0.9 * np.sin(P[:, 1] * 9.0 + P[:, 2] * 5.0 - t * 4.2) + 0.5 * np.sin(P[:, 0] * 7.0 - t * 2.7 + 1.3)
    rot_part(ii, rot_w((0, 1, 0), (lag + math.radians(2.2) * wave) * w), PIVOT)
    sway = (0.012 * np.sin(P[:, 1] * 6.0 - t * 3.3 + P[:, 0] * 4.0) * w)[:, None] * np.array([1.0, 0.0, 0.35])
    pos[ii] = pos[ii] + sway
    # 耳：付け根の まわりに 前後（横の 軸）
    for k in ('l', 'r'):
        ii = D['idx']['ear_' + k]
        if not len(ii):
            continue
        b, tp = LM['ear_%s_base' % k], LM['ear_%s_tip' % k]
        axis = nrm(np.cross(tp - b, np.array([0, 0, 1.0])))
        if axis[0] * (1 if k == 'l' else -1) < 0:
            axis = -axis
        ang = math.radians(ear_angle(t, k)) * D['we'][k][ii] * (1 if k == 'l' else -1)
        rot_part(ii, rot_w(axis, ang), b)
    # 鼻の 穴：ふくらむ（穴の まん中から 外へ）
    fl = flare(t)
    if fl > 0:
        for k in ('l', 'r'):
            ii = D['idx']['nos_' + k]
            c0 = LM['nost_%s' % k]
            d = pos[ii] - c0
            ax = nrm(np.array([0.0, -0.35, 1.0]))
            d = d - np.outer(d @ ax, ax)
            pos[ii] = pos[ii] + nrm(d) * (0.012 * fl * D['wn'][k][ii])[:, None]
    q = GL.Prim(pos.astype(np.float32), nrm_.astype(np.float32), p.uv, p.idx, p.mat, p.name, p.uv1, tan, p.color)
    return q


# ---------------------------------------------------------------- G バッファ（たて BANDS に 分けて）
def band_cam(cam, r0, r1):
    """画面の 行 r0〜r1 だけを 写す カメラ（同じ 目・同じ 向き）"""
    H = cam.H
    c = 1 - (r0 + r1) / H; h = (r1 - r0) / H
    T = np.eye(4); T[1, 1] = 1 / h; T[1, 3] = -c / h
    bc = Camera(cam.view, T @ cam.proj, cam.W, r1 - r0)
    bc.near, bc.far, bc.fov_y = cam.near, cam.far, cam.fov_y
    return bc


def gbuffer(prim, cam, Mm):
    sc = Scene([prim], Mm)
    out = {k: np.zeros((cam.H, cam.W) + ((3,) if k != 'alpha' else ()), np.float32) for k in ('alpha', 'albedo', 'normal', 'pos')}
    edges = np.linspace(0, cam.H, BANDS + 1).round().astype(int)
    for r0, r1 in zip(edges[:-1], edges[1:]):
        fr = render([prim], band_cam(cam, r0, r1), NOLIGHT, ss=SS, scene=sc, ao_strength=0.0, rim=None, want=('alpha', 'albedo', 'normal', 'pos'))
        for k in out:
            out[k][r0:r1] = fr[k]
        del fr
    del sc
    return out


# ---------------------------------------------------------------- 光（前の 顔の 場面と 同じ 色の 考え方：暗い むらさき・うしろから むらさきと 青の 強い ふちの 光・目の 紫の 光）
def ggx(N, Hh, Ld, V, rough):
    a2 = rough ** 4
    ndh = np.clip((N * Hh).sum(-1), 0, 1)
    D = a2 / (np.pi * (ndh * ndh * (a2 - 1) + 1) ** 2 + 1e-7)
    ndl = np.clip((N * Ld).sum(-1), 0, 1)
    ndv = np.clip((N * V).sum(-1), 1e-3, 1)
    k = (rough + 1) ** 2 / 8
    G = ndl / (ndl * (1 - k) + k) * ndv / (ndv * (1 - k) + k)
    return D * G / (4 * ndv + 1e-4)


def classify(alb):
    """たてがみ（あざやかな むらさき）と 肌"""
    hsv = cv2.cvtColor(np.clip(alb, 0, 1).astype(np.float32) ** (1 / 2.2), cv2.COLOR_RGB2HSV)
    h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    mane = ss(0.30, 0.45, s_) * ((h > 245) & (h < 340)) * ss(0.25, 0.4, v)
    return mane.astype(np.float32), v


def shade(G, cam, Mm, st):
    A = G['alpha']; alb = G['albedo']; N = G['normal']; P = G['pos']
    L, g = st['L'], min(st['g'], 1.0)
    V = cam.eye[None, None, :] - P
    V = V / (np.linalg.norm(V, axis=-1, keepdims=True) + 1e-9)
    fwd = nrm(cam.view[2, :3])                                                     # カメラの うしろ向き（＝顔から カメラへ）
    rt = nrm(cam.view[0, :3]); up = nrm(cam.view[1, :3])
    mane, val = classify(alb)
    k_alb = (0.22 * (1 - mane) + 0.34 * mane)[..., None]
    base = alb * k_alb
    k = 0.03 + 0.97 * L
    lights = [(nrm(fwd * 0.55 + up * 0.75 - rt * 0.15), np.array([0.30, 0.26, 0.42]) * k, 'front'),
              (nrm(-fwd + rt * 0.95 + up * 0.45), np.array([3.6, 0.85, 2.8]) * L, 'back'),         # 右うしろ上：むらさきの ふち（顔の 右の ほお・たてがみ）
              (nrm(-fwd - rt * 0.95 + up * 0.15), np.array([0.8, 1.15, 3.3]) * L, 'back'),         # 左うしろ：青の ふち
              (nrm(-fwd * 0.6 + up * 1.0), np.array([1.0, 0.9, 1.45]) * L, 'back')]                 # 上うしろ：耳・たてがみの 上
    ndv = np.clip((N * V).sum(-1), 0, 1)
    fres = 1 - ndv
    col = np.zeros_like(alb)
    rough = np.where(mane > .5, .5, .38)
    eyes = [xf(Mm, LM['eye_l']), xf(Mm, LM['eye_r'])]
    de = np.minimum(np.linalg.norm(P - eyes[0][None, None, :], axis=-1), np.linalg.norm(P - eyes[1][None, None, :], axis=-1))
    near_eye = np.clip((de - 0.05) / 0.10, 0.1, 1.0)
    for Ld, lc, kind in lights:
        ndl = (N * Ld[None, None, :]).sum(-1)
        dif = np.clip(ndl, 0, 1)
        Hh = Ld[None, None, :] + V; Hh /= np.linalg.norm(Hh, axis=-1, keepdims=True) + 1e-9
        sp = ggx(N, Hh, Ld[None, None, :], V, rough) * (0.04 + 0.96 * fres ** 5)
        col = col + base * dif[..., None] * lc + (sp * 0.25 * near_eye)[..., None] * lc
        if kind == 'back':
            rim = fres ** 4.0 * np.clip(ndl + 0.3, 0, 1) * near_eye
            col = col + (rim * (0.5 + 0.9 * mane))[..., None] * lc
    lob = nrm(-fwd + up * 0.6 + rt * 0.3)
    Rv = 2 * ndv[..., None] * N - V
    env = np.clip((Rv * lob[None, None, :]).sum(-1), 0, 1) ** 6.0
    col = col + (env * fres ** 2 * 0.22)[..., None] * np.array([1.1, 0.28, 0.95]) * k
    col = col + (np.clip(N[..., 1], 0, 1) * 0.02 + 0.01)[..., None] * np.array([0.18, 0.16, 0.26]) * k * base * 10
    # 目の 紫の 光が まわり（まぶた・眉・ほお）を 照らす（目ごとの 強さ：13:29「目の光りは紫で、もっとリアルに！」）
    ge = st.get('ge', {'eye_l': st['g'], 'eye_r': st['g']})
    for k, E in (('eye_l', eyes[0]), ('eye_r', eyes[1])):
        gk = min(ge[k], 1.0)
        if gk <= 0:
            continue
        pe = E + fwd * 0.05 + up * 0.01
        dv = pe[None, None, :] - P
        dd = np.linalg.norm(dv, axis=-1) + 1e-6
        ndl = np.clip((N * (dv / dd[..., None])).sum(-1), 0, 1)
        pl = EYE_LIGHT * gk * 0.25
        col = col + (base * 6 + 0.02) * (ndl / (dd ** 2 * 300 + 1))[..., None] * pl * 40
    return col, A, mane


# ---------------------------------------------------------------- 1コマの 3D（G バッファ・光を つけた 色・しるし）
# まさちゃん（13:29）「光るのは左目で、目が光り始めてから今の角度になる。目は徐々に光りが強くなり、顔が見える頃には両目が光るようにして！
#   あと目の光りは紫で、もっとリアルに！」→ 画面の 左の 目（カメラに 近い 目＝馬の 右目）が 0.10秒から だんだん 光る・
#   もう 一つの 目は 0.36秒から ともって 0.8秒（顔が 見える ころ）には 両目。光は 紫（目の 形の まま 光って にじむ：comp）
FIRST_EYE = 'eye_r'                                                              # 画面の 左の 目（カメラに 近い）
EYE_KEYS = [(0.0, 0.0), (0.10, 0.0), (0.30, 0.16), (0.55, 0.42), (0.80, 0.68), (1.0, 0.80), (1.5, 1.15), (1.78, 1.7), (FACE_LEN, 3.0)]
EYE_BOTH = (0.36, 0.80)                                                          # もう 一つの 目が ともる（秒）
EYE_LIGHT = np.array([0.024, 0.006, 0.066])                                      # 目の 光が まわりを 照らす 色（紫）
#   光の 色は 仕上げ（×2.2 → ACES → sRGB）の あとで 紫に 見える ように 決める：ACES は 明るい 色を 白へ よせる ので、赤・緑を ひかえめに
#   （目の 形の 所：sRGB で 約 (0.69, 0.25, 1.0)＝#B040FF・まん中：約 (0.88, 0.69, 1.0) の ラベンダー・にじみ：紫）
EYE_COL = np.array([0.09, 0.012, 1.00])                                          # 目の 光（紫：仕上げ前の 明るさ）
EYE_HOT = np.array([0.28, 0.13, 0.40])                                           # まん中に たす 光（ラベンダー）
OVER_COL = np.array([0.45, 0.16, 1.00])                                          # あふれる 光（明るい 紫）


def eye_masks(B, alb):
    """3D の 目（あざやかな 紫の 瞳）の 形：色 × 目の しるしからの きょり（たてがみの 紫は 入れない）→ {目: (形 0〜1, きょり)}"""
    Mi = np.linalg.inv(B['Mm'])
    Pm = B['P'] @ Mi[:3, :3].T + Mi[:3, 3]
    hsv = cv2.cvtColor(np.clip(alb, 0, 1).astype(np.float32) ** (1 / 2.2), cv2.COLOR_RGB2HSV)
    h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    col = (ss(0.42, 0.6, s_) * ss(0.40, 0.6, v) * ((h > 262) & (h < 318))).astype(np.float32)
    out = {}
    for k in ('eye_l', 'eye_r'):
        d = np.linalg.norm(Pm - LM[k], axis=-1).astype(np.float32)
        out[k] = ((col * (1 - ss(0.075, 0.11, d)) * np.clip(B['A'], 0, 1)).astype(np.float32), d)
    return out


def face_state(t):
    """前の 顔の 場面の 時刻（L：顔を 照らす 光・wv：目の 光の ゆらぎ）＋ 目ごとの 光（ge：1 を こえると あふれる）"""
    import shiden_film as SFm
    d = SFm.face_state(t)
    base = max(0.0, float(SFm.spline(t, EYE_KEYS))) * (1 + 0.35 * d['wv'])          # 光りはじめて 1秒ほどの ゆらぎ（第4.72版）は 小さく（本物っぽく）
    other = 'eye_l' if FIRST_EYE == 'eye_r' else 'eye_r'
    d['ge'] = {FIRST_EYE: base, other: base * float(ss(EYE_BOTH[0], EYE_BOTH[1], t))}
    d['g'] = base
    return d


def marks(cam, Mm):
    pts = np.array([xf(Mm, LM[k]) for k in ('eye_l', 'eye_r', 'nost_l', 'nost_r', 'muzzle', 'chin', 'forehead')])
    pe = project(cam, pts)
    D = dict(eye_l=pe[0].tolist(), eye_r=pe[1].tolist(), nost_l=pe[2].tolist(), nost_r=pe[3].tolist(), muzzle=pe[4].tolist(), chin=pe[5].tolist(), poll=pe[6].tolist())
    En = near_eye(Mm, cam.eye)
    D['eye'] = D['eye_l'] if np.allclose(En, pts[0]) else D['eye_r']             # 雷の しくみ（Arcs3）が 見る 目＝カメラに 近い ほう
    D['crest'] = [D['poll']] * 2
    return D


def buffers(f, W, H):
    t = f / FPS - BLACK
    st = face_state(t)
    Mm = pose_matrix(t)
    cam, _ = camera(t, W, H, Mm)
    prim = posed_prim(t)
    G = gbuffer(prim, cam, Mm)
    del prim
    col, A, mane = shade(G, cam, Mm, st)
    M = marks(cam, Mm)
    ed = math.hypot(M['eye_l'][0] - M['eye_r'][0], M['eye_l'][1] - M['eye_r'][1])
    hs = ed / (0.62 * W)                                                          # 頭の 大きさ（目と 目の あいだが 画面の はばの 6割 ＝ 1）
    return dict(col=col * A[..., None], A=A, mane=mane * A, P=G['pos'], N=G['normal'], cam=cam, Mm=Mm, phi=0.0, M=M, hs=hs, E=xf(Mm, LM['eye_l']), alb=G['albedo'])


def _oct_enc(n):
    n = n / (np.abs(n).sum(-1, keepdims=True) + 1e-9)
    x, y, z = n[..., 0], n[..., 1], n[..., 2]
    ox = np.where(z >= 0, x, (1 - np.abs(y)) * np.sign(x + 1e-12))
    oy = np.where(z >= 0, y, (1 - np.abs(x)) * np.sign(y + 1e-12))
    return np.round((np.stack([ox, oy], -1) * 0.5 + 0.5) * 65535).astype(np.uint16)


def save_buf(path, B):
    cam = B['cam']
    dep = np.linalg.norm(B['P'] - cam.eye[None, None, :], axis=-1)
    dep = np.where(B['A'] > 0.002, dep, 0.0)
    tmp = path[:-4] + '_tmp.npz'
    np.savez_compressed(tmp, col=B['col'].astype(np.float16), A=np.round(np.clip(B['A'], 0, 1) * 255).astype(np.uint8),
                        mane=np.round(np.clip(B['mane'], 0, 1) * 255).astype(np.uint8), dep=dep.astype(np.float32), N=_oct_enc(B['N']),
                        view=cam.view, proj=cam.proj, WH=np.array([cam.W, cam.H]), fov=np.array([cam.fov_y]), Mm=B['Mm'], phi=np.array([B['phi']]),
                        hs=np.array([B['hs']]), E=B['E'], M=np.array(json.dumps(B['M'])), alb=B['alb'].astype(np.float16))
    os.replace(tmp, path)


def load_buf(path):
    """shiden_glb.load_buf と 同じ ＋ alb（色）"""
    import shiden_glb as SG
    B = SG.load_buf(path)
    z = np.load(path)
    if 'alb' in z.files:
        B['alb'] = z['alb'].astype(np.float32)
    return B


BUF = {}
NECK = (-0.40, -0.60)                                                            # 第4.195版（まさちゃん 12:30「首から下ないからそこが映らないようにね！」）：
#   胸像の 首は y −0.81 で 切れて いる → モデルの 高さ −0.40 から −0.60 で 首と たてがみを 闇に とかす（すき通す）。雷も そこには 出ない


def neck_fade(B):
    """首の 下を 消す（モデルの 座標の 高さで）：A・色・たてがみを へらす"""
    Mi = np.linalg.inv(B['Mm'])
    y = (B['P'] @ Mi[:3, :3].T + Mi[:3, 3])[..., 1]
    k = (1 - ss(NECK[0], NECK[1], y)).astype(np.float32)
    k = np.where(B['A'] > 0.002, k, 1.0).astype(np.float32)
    B['A'] = B['A'] * k; B['col'] = B['col'] * k[..., None]; B['mane'] = B['mane'] * k
    return B


def buf_at(f):
    """コマ f の G バッファ（雷の しくみが 前の コマも 読む）・首の 下は 消して おく"""
    import shiden_glb as SG                                                      # 読む ところだけ 前の 顔と 同じ（SD_HORSE_MODEL は 決めない まま）
    if f not in BUF:
        while len(BUF) > 4:
            BUF.pop(next(iter(BUF)))
        B = load_buf(os.path.join(BUF_DIR[0], 'b%03d.npz' % f))
        if 'alb' in B:                                                           # 光を ここで つけ直す（shade の 直しが すぐ 効く）
            col, _, mane = shade(dict(alpha=B['A'], albedo=B['alb'], normal=B['N'], pos=B['P']), B['cam'], B['Mm'], face_state(f / FPS - BLACK))
            B['col'] = col * B['A'][..., None]; B['mane'] = mane * B['A']
            B['eyem'] = eye_masks(B, B['alb'])                                   # 光る 目の 形（3D の 紫の 瞳）
            del B['alb']
        BUF[f] = neck_fade(B)
    return BUF[f]


BUF_DIR = ['']


# ---------------------------------------------------------------- 鼻息（鼻の 穴 2つ・前の 息と 同じ つぶ：風は 画面の 左へ 少し）
WIND = np.array([-0.07, 0.02, 0.0])
NOSE_D = dict(l=nrm(np.array([0.30, -0.55, 1.0])), r=nrm(np.array([-0.30, -0.55, 1.0])))   # 穴の 軸（前・下・少し 外）


def make_breath(k, seed):
    import shiden_face2 as F2

    class Breath2(F2.Breath):
        def state(self, t):
            out = []
            for B in self.P:
                a = t - B['te']
                ok = (a > 0) & (a < B['life'])
                if not ok.any():
                    continue
                a = a[ok]
                kd = 2.7
                disp = B['v0'][ok] * ((1 - np.exp(-kd * a)) / kd)[:, None]
                disp += np.array([0, 1.0, 0]) * (0.5 * 0.07 * a * a)[:, None]
                disp += WIND * a[:, None]
                md = B['modes'][ok]; om = B['om'][ok]; ph = B['ph'][ok]
                tur = (np.sin(om * a[:, None] + ph) - np.sin(ph))[:, :, None] * md * (0.02 * (a ** 1.1))[:, None, None]
                disp += tur.sum(1)
                r = 0.004 + (B['r1'][ok] - 0.004) * (1 - np.exp(-a / 0.5))
                life = B['life'][ok]
                o = ss(0, 0.05, a) * (1 - ss(0.25 * life, life, a)) * (0.006 / r) ** 0.95 * B['k']
                out.append(dict(x=B['x0'][ok] + disp, r=r, o=o, tex=B['tex'][ok], rot=B['rot'][ok] + B['spin'][ok] * a, kind=B['kind'][ok], age=a / life))
            return out

    def nose_at(te):
        te = np.asarray(te, float)
        c = np.zeros((len(te), 3)); d = np.zeros((len(te), 3))
        for j, tt in enumerate(te):
            Mt = pose_matrix(tt)
            c[j] = xf(Mt, LM['nost_' + k] + NOSE_D[k] * 0.03)
            d[j] = Mt[:3, :3] @ NOSE_D[k]
        return c, d
    return Breath2(nose_at, seed=seed)


# ---------------------------------------------------------------- 雷・息（2D：G バッファから）
FX = {}


def layers(f, t, st, B, W, H):
    import shiden_face2 as F2
    R = dict(rgb=B['col'], a=B['A'], mane=B['mane'])
    L = st['L']
    s2 = W / 780.0
    Mm = B['Mm']
    to_w = lambda X: xf(Mm, X)
    inv_skin = lambda Xd, ph: Xd
    if os.environ.get('SD_ARCS', '1') != '0':
        if 'arcs' not in FX:
            FX['arcs'] = F2.Arcs3(int(round((BLACK + F['EYE_ON']) * FPS)) + 1, int(round(FACE * FPS)))
        C, Hot, AG, lit, n_on = FX['arcs'].frame(f, B, buf_at, project, to_w, inv_skin, s2, 0.085)
        R['bolt'] = F2.arcs3_glow(C, Hot, AG, s2 * (0.75 + 0.35 * B['hs']))
        R['blit'] = lit
        R['blit_k'] = 0.55 + 0.45 * L
        R['n_arcs'] = n_on
    if os.environ.get('SD_BREATH', '1') != '0':
        if 'br' not in FX:
            FX['br'] = [make_breath('l', 4242), make_breath('r', 5151)]
        al_t = np.zeros((H, W), np.float32); col_t = np.zeros((H, W, 3), np.float32)
        for br in FX['br']:
            v = br.layer(t, B['cam'], project, B['P'], B['A'], W, H, L, (lambda X: X), nrm(np.array([0.55, -0.8])))
            if v is not None:
                al, vcol = v
                col_t = col_t * (1 - al[..., None]) + vcol * al[..., None]
                al_t = 1 - (1 - al_t) * (1 - al)
        R['vap'] = (al_t, col_t) if al_t.max() > 0 else None
    return R


def soft_blur(img, sigma):
    """広い ぼかし（大きい ときは 小さく して から ぼかして もどす：速い）"""
    if sigma <= 6:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    f = int(2 ** math.floor(math.log2(sigma / 4)))
    h, w = img.shape[:2]
    sm = cv2.resize(img, (max(1, w // f), max(1, h // f)), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), sigma / f)
    return cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR)


# ---------------------------------------------------------------- 1コマを 仕上げる（背景・雷・息・光る 目 2つ〈紫〉・火の粉・仕上げ・おわりの 光）
def comp(f, B, W, H):
    import shiden_film as SF
    from paint import blur, smoothstep
    t = f / FPS - BLACK
    st = face_state(t)
    g, L = st['g'], st['L']
    R = layers(f, t, st, B, W, H)
    rgb, A = R['rgb'], R['a']
    yy, xx = SF.grid()
    tx = SF.face_tex(7)
    S = SF.S
    M = B['M']
    el, er = np.array(M['eye_l']), np.array(M['eye_r'])
    ec = (el + er) / 2
    hs = B['hs']
    chin = np.array(M['chin'])
    # ---------- 背景（前の 顔の 場面と 同じ：もや・頭の うしろの 光・右上の 桃色・左下の 青・星） ----------
    ty = (yy / H)[..., None]
    bg = (np.array([0.004, 0.0015, 0.009]) * (1 - ty) + np.array([0.0015, 0.0008, 0.004]) * ty) * (0.1 + 0.9 * L)
    ox, oy = int((t * 30 * S) % W), int((t * 12 * S) % H)
    haze = tx['haze'][oy:oy + H, ox:ox + W]
    back = np.exp(-(((xx - ec[0]) / (W * .62)) ** 2 + ((yy - ec[1] + 160 * S) / (H * .30)) ** 2)) * (0.55 + 0.7 * haze)
    pink = np.exp(-(((xx - W * 1.0) / (W * .7)) ** 2 + ((yy - H * .15) / (H * .4)) ** 2)) * (0.4 + 0.8 * haze)
    blue = np.exp(-(((xx - W * 0.05) / (W * .6)) ** 2 + ((yy - H * .85) / (H * .35)) ** 2)) * (0.4 + 0.7 * haze)
    bg = bg + (back[..., None] * np.array([0.050, 0.012, 0.060]) + pink[..., None] * np.array([0.06, 0.010, 0.045]) + blue[..., None] * np.array([0.008, 0.012, 0.045])) * L
    star = np.zeros((H, W), np.float32)
    for (sx_, sy_, b_, ph, sz) in tx['stars']:
        x = (sx_ * W - t * 9 * S * (0.5 + b_)) % W
        y = (sy_ * H + t * 4 * S) % H
        tw = 0.55 + 0.45 * math.sin(t * 3.1 + ph)
        cv2.circle(star, (int(x * 4), int(y * 4)), max(1, int(sz * S * 4)), float(b_ * tw), -1, cv2.LINE_AA, shift=2)
    star = blur(star, .7 * S)
    bg = bg + star[..., None] * np.array([0.06, 0.055, 0.09]) * L
    # ---------- 顔だけ 光る（首と 胸は 闇へ・たてがみは 光る） ----------
    cy_ = ec[1] * 0.45 + chin[1] * 0.55
    rx_ = max(1.0, np.linalg.norm(er - el)) * 1.05
    ry_ = max(1.0, chin[1] - ec[1]) * 1.15
    pu = (xx - ec[0]) / rx_; pv = np.where(yy < cy_, (yy - cy_) / (ry_ * 1.6), (yy - cy_) / ry_)
    headm = 1 - smoothstep(.75, 1.2, np.sqrt(pu ** 2 + pv ** 2))
    hm = np.maximum(headm, R['mane'] * .85)
    rgb = rgb * (0.04 + 0.96 * hm ** 1.5)[..., None]
    img = bg * (1 - A[..., None]) + rgb
    if R.get('blit') is not None:
        img = img + R['blit'] * R.get('blit_k', 0.35 + 0.65 * L)
    if R.get('bolt') is not None:
        img = img + R['bolt']
    smoke = smoothstep(.25, .7, tx['smoke'][(oy * 2) % H:(oy * 2) % H + H, ox:ox + W]) * smoothstep(H * .62, H * .92, yy + 60 * S * np.sin(xx / W * 3 + t * .9))
    img = img * (1 - smoke[..., None] * .85) + smoke[..., None] * .85 * np.array([0.012, 0.005, 0.020]) * (0.3 + 0.7 * L)
    # ---------- 鼻息 ----------
    if R.get('vap') is not None:
        al, vcol = R['vap']
        img = img * (1 - al[..., None] * .8) + vcol * al[..., None]
    # ---------- 光る 目（13:29「目の光りは紫で、もっとリアルに！」）：3D の 瞳の 形 そのものが 紫に 光り（まん中ほど 白っぽく）、
    #   形の まま まわりへ にじむ（細い・中くらい・広い・空気に 散る ぼかし）。まぶた・眉・ほおを 照らす 光は shade()。十字の 筋は なし。
    #   かくれた 目は 光らない（3D の 形で きまる）。あふれる 光（1 を こえる：さいごの 0.5秒）は 近い 目から 大きく にじむ ----------
    camp = B['cam'].eye
    Ew = {k: xf(B['Mm'], LM[k]) for k in ('eye_l', 'eye_r')}
    dist = {k: np.linalg.norm(Ew[k] - camp) for k in Ew}
    near = min(dist, key=dist.get)
    ge = st['ge']
    em = np.zeros((H, W, 3), np.float32); em_near = None
    for k in ('eye_l', 'eye_r'):
        gk = ge[k]
        if gk <= 0 or k not in B.get('eyem', {}):
            continue
        m, d = B['eyem'][k]
        lvl = min(gk, 1.0)
        core = np.exp(-(d / 0.030) ** 2) * lvl ** 1.5
        e = m[..., None] * (EYE_COL * (1.36 * lvl) + EYE_HOT * core[..., None])
        em += e
        if k == near:
            em_near = e
    if em.max() > 0:
        img = img + em + soft_blur(em, 1.6 * S) * 0.9 + soft_blur(em, 6 * S) * 0.75 + soft_blur(em, 22 * S) * 0.6 + soft_blur(em, 75 * S) * 0.45 \
            + soft_blur(em, 220 * S) * 0.35 * np.array([0.75, 0.35, 1.0])
    over = max(0.0, ge[near] - 1.0)
    if over > 0 and em_near is not None and em_near.max() > 0:                       # あふれる 光：近い 目から 大きく にじむ・まわりが 紫に つつまれて いく
        exn, eyn = M[near]
        rr2 = np.sqrt((xx - exn) ** 2 + (yy - eyn) ** 2)
        img = img + soft_blur(em_near, (30 + 140 * over) * S) * (1.2 * over) + np.exp(-(rr2 / (W * (.08 + .25 * over))) ** 1.5)[..., None] * OVER_COL * (1.4 * over)
    # ---------- 火の粉（下から 上へ） ----------
    em = np.zeros((H, W), np.float32)
    for (sx_, sy_, sz, b_) in tx['emb']:
        x = (sx_ * W + 40 * S * math.sin(t * 1.3 + sy_ * 9)) % W
        y = (sy_ * H - t * 110 * S * (0.6 + b_)) % H
        cv2.circle(em, (int(x * 4), int(y * 4)), max(1, int(sz * S * 4)), float(b_), -1, cv2.LINE_AA, shift=2)
    em = blur(em, .8 * S) + blur(em, 4 * S) * .6
    img = img + em[..., None] * np.array([1.0, 0.35, 0.6]) * 0.35 * L * (1 - 0.8 * headm)[..., None]
    img = SF.bloom(img, .9)
    out = SF.finish(img * 2.2, 7 + int(t * 100), vig=.55)
    # ---------- 青むらさきの 光（スクリーン・闇から ともる） ----------
    rx = (xx - W * .45) / (W * .62); ry = (yy - H * .38) / (H * .62)
    r_ = np.sqrt(rx ** 2 + ry ** 2)
    c0, c1, c2 = np.array([120, 170, 255]) / 255, np.array([30, 70, 255]) / 255, np.array([10, 30, 200]) / 255
    w1 = np.clip(r_ / .45, 0, 1)[..., None]
    w2 = np.clip((r_ - .45) / .55, 0, 1)[..., None]
    colb = c0 * (1 - w1) + c1 * w1
    colb = colb * (1 - w2) + c2 * w2
    alp = (0.7 * (1 - w1[..., 0]) + 0.5 * w1[..., 0]) * (1 - w2[..., 0]) + 0.45 * w2[..., 0]
    out = out + (alp[..., None] * colb) * (1 - out) * (0.72 * L)
    # ---------- おわり：近い 目の 光が 画面を つつむ ----------
    fl = float(ss(RUSH, FACE_LEN, t))
    if fl > 0:
        ex, ey = (el if near == 'eye_l' else er)
        rr2 = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) / (W * (.15 + 1.4 * fl ** 1.5))
        wash = np.clip(np.exp(-rr2 ** 2) * fl ** .8 * 1.6, 0, 1)[..., None]
        wcol = np.array([0.80, 0.55, 1.0]) * (1 - fl) + np.array([1.0, .95, .88]) * fl          # 紫の 光 → さいごは 前と 同じ 白（つぎの 蹄の 場面と つながる）
        out = out * (1 - wash) + wcol * wash
    return np.clip(out, 0, 1), R.get('n_arcs')


# ---------------------------------------------------------------- つなぐ（顔 いがいは 前の 動画の コマ）・書き出し
def splice(old_mp4, work, out_mp4, W, H, a0, a1, n_all, crf=20):
    import subprocess
    have = lambda i: os.path.exists(os.path.join(work, 'f%03d.png' % i))
    need = [i for i in range(n_all) if not (a0 <= i < a1) and not have(i)]
    if need:
        tmpd = os.path.join(work, '_old'); os.makedirs(tmpd, exist_ok=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', old_mp4, '-vf', f'scale={W}:{H}:flags=lanczos', '-start_number', '0', os.path.join(tmpd, 'o%03d.png')], check=True)
        for i in need:
            os.replace(os.path.join(tmpd, 'o%03d.png' % i), os.path.join(work, 'f%03d.png' % i))
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)
    miss = [i for i in range(n_all) if not have(i)]
    assert not miss, f'コマが たりない：{miss[:8]}'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(work, 'f%03d.png'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an', out_mp4], check=True)
    print(out_mp4, os.path.getsize(out_mp4), flush=True)


def key_frames(mp4):
    import subprocess
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'frame=key_frame', '-of', 'csv=p=0', mp4], capture_output=True, text=True, check=True)
    return [i for i, ln in enumerate(r.stdout.split()) if ln.strip().startswith('1')]


def splice_keyed(old_mp4, work, out_mp4, W, H, a0, a1, n_all):
    """前の 動画と 同じ 大きさの とき：顔の あとの 最初の キーフレーム K から うしろは 圧縮し直さずに そのまま つなぐ（1画素も 同じ）。
       0〜K−1 コマ（はじめの 黒・新しい 顔・蹄の はじめ）だけ 前と 同じ 決めごと（CRF 20・slow）で 圧縮。できなければ False"""
    import subprocess
    cap = cv2.VideoCapture(old_mp4)
    ow, oh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); cap.release()
    if (ow, oh) != (W, H) or os.environ.get('SD_SPLICE', '1') == '0':
        return False
    ks = [k for k in key_frames(old_mp4) if k >= a1]
    if not ks:
        return False
    K = ks[0]
    have = lambda i: os.path.exists(os.path.join(work, 'f%03d.png' % i))
    need = [i for i in range(K) if not (a0 <= i < a1) and not have(i)]
    if need:                                                                     # 前の 動画の コマ（劣化なしの PNG に）
        cap = cv2.VideoCapture(old_mp4)
        for i in range(K):
            ok, fr = cap.read()
            assert ok, f'前の 動画の {i} コマ目が 読めない'
            if i in need:
                cv2.imwrite(os.path.join(work, 'f%03d.png' % i), fr)
        cap.release()
    assert all(have(i) for i in range(K)), 'コマが たりない'
    a, b, lst = (os.path.join(work, x) for x in ('_sd_a.mp4', '_sd_b.mp4', '_sd_ab.txt'))
    FFm = ['ffmpeg', '-y', '-loglevel', 'error']
    with open(os.path.join(work, '_sd_a.txt'), 'w') as fl:
        for i in range(K):
            fl.write(f"file 'f{i:03d}.png'\nduration {1 / FPS:.6f}\n")
    subprocess.run(FFm + ['-framerate', str(FPS), '-i', os.path.join(work, 'f%03d.png'), '-frames:v', str(K),
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-tag:v', 'avc1', '-an', a], check=True)
    subprocess.run(FFm + ['-ss', f'{K / FPS:.6f}', '-i', old_mp4, '-c', 'copy', '-an', b], check=True)
    open(lst, 'w').write(f"file '{a}'\nfile '{b}'\n")
    subprocess.run(FFm + ['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', '-tag:v', 'avc1', out_mp4], check=True)
    co, cn = cv2.VideoCapture(old_mp4), cv2.VideoCapture(out_mp4)
    n = 0; same = 0
    while True:
        ok2, y = cn.read()
        if not ok2:
            break
        ok1, x = co.read()
        if n >= K:
            assert ok1 and np.array_equal(x, y), f'つないだ 動画の {n} コマ目が 前の 動画と ちがう'
            same += 1
        n += 1
    assert n == n_all, f'つないだ 動画の コマ数 {n}（{n_all} の はず）'
    for x in (a, b, lst, os.path.join(work, '_sd_a.txt')):
        os.remove(x)
    print(f'つないだ：{K}コマ目（キーフレーム）から うしろの {same}コマは 前の 動画と 1画素も 同じ（圧縮し直して いない）・はじめの {K}コマは 新しく 圧縮',
          out_mp4, os.path.getsize(out_mp4), flush=True)
    return True


if __name__ == '__main__':
    import shiden_film as SF
    W, H = SF.W, SF.H
    a0, a1 = int(round(BLACK * FPS)), int(round(FACE * FPS))                     # 54〜113
    if sys.argv[1] == '--buf':
        buf = sys.argv[2]; os.makedirs(buf, exist_ok=True)
        i0 = max(a0, int(sys.argv[3]) if len(sys.argv) > 3 else a0); i1 = min(a1, int(sys.argv[4]) if len(sys.argv) > 4 else a1)
        for i in range(i0, i1):
            p = os.path.join(buf, 'b%03d.npz' % i)
            if os.path.exists(p):
                continue
            t0 = time.time()
            save_buf(p, buffers(i, W, H))
            print('buf', i, round(time.time() - t0, 1), 's', os.path.getsize(p) // 1024, 'KB', flush=True)
    elif sys.argv[1] == '--comp':
        BUF_DIR[0] = sys.argv[2]; work = sys.argv[3]; os.makedirs(work, exist_ok=True)
        i0 = max(a0, int(sys.argv[4]) if len(sys.argv) > 4 else a0); i1 = min(a1, int(sys.argv[5]) if len(sys.argv) > 5 else a1)
        skip = os.environ.get('SD_COMP_SKIP', '0') == '1'                     # とちゅうから つづける（できた コマは とばす：雷・息は コマごとに きまる）
        for i in range(i0, i1):
            if skip and os.path.exists(os.path.join(work, 'f%03d.png' % i)):
                continue
            t0 = time.time()
            img, n_arcs = comp(i, buf_at(i), W, H)
            SF.save_png(img, os.path.join(work, 'f%03d.png' % i))
            print('comp', i, round(time.time() - t0, 1), 's', 'arcs', n_arcs, flush=True)
    elif sys.argv[1] == '--splice':
        if not splice_keyed(sys.argv[2], sys.argv[3], sys.argv[4], W, H, a0, a1, SF.NF):
            splice(sys.argv[2], sys.argv[3], sys.argv[4], W, H, a0, a1, SF.NF, int(os.environ.get('SD_CRF', '20')))
