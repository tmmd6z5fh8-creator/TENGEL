"""神様極的中 第16稿：はじめの 顔の 場面（0〜112コマ・0〜3.75秒）を まさちゃんの 3D から 描き直す（第4.216版）

まさちゃん（2026/11/24 11:01）「神様極的中の、最初の神様塗り直してくれたけど、塗った感がきになる… 3Dのデータから入れ直すことできる？」
  ・3D：神様馬の 胸像（Meshy：Solar_Sovereign 5254ac・三角 758万・色／金属と ざらつき／法線の 地図）。もとの 第13稿の 道具（W/…）は 11/09 に なくなった ので、
    ここで 新しく 描く。色の 地図・金属の 地図は きれい（ほおの まだらは 地図には ない）＝ まだらは 前の 描き方（影の 地図）で 出て いた
  ・流れと 時刻は 第14稿の まま（音と そろう）：0〜0.5秒 真っ暗 → 顔が じわじわ（うしろ横の 光で ふちから）→ 1.3秒 両目が 金色に → 顔を 上げる
    （前からの 光が だんだん・目と たてがみに 金の 雷）→ 3.75秒 大爆発（113コマ目から 第14稿：113〜115 は 顔の 所 だけ 新しい 顔に 入れかえ：assemble16.py）
  ・カメラ：第14稿の 45・90・110コマ目に 目じるし 9つを 合わせた（path.json）
  使い方：
    python3 kisekae/gk16/face3d.py --buf  <作業>  [f0 f1]   … G バッファ（色・金属・ざらつき・向き・場所・すけ・AO）を <作業>/gb/g%04d.npz に（float16）
    python3 kisekae/gk16/face3d.py --comp <作業>  [f0 f1]   … 光・目・雷・火の粉・仕上げ → <作業>/out/%04d.png（780×1688）
"""
import os, sys, json, math, time
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
from raster import Camera                                                      # noqa: E402

W, H, FPS = 780, 1688, 30
PJ = json.load(open(os.path.join(HERE, 'path.json'), encoding='utf8'))
FOV = PJ['fov']
LM = {k: np.array(v, np.float64) for k, v in PJ['landmarks'].items()}
LAST = 112                                                                       # 顔の 場面の さいごの コマ（113 から 大爆発）


def smootherstep(x):
    x = min(1.0, max(0.0, x)); return x * x * x * (x * (x * 6 - 15) + 10)


def progress(f):
    a, w = PJ['prog']
    return smootherstep((f - a) / float(w))


def _rc(k):
    p = PJ['poses'][str(k)]
    R = cv2.Rodrigues(np.array(p['rv'], float).reshape(3, 1))[0]; t = np.array(p['tv'], float)
    return R, -R.T @ t


def pose(f):
    """コマ f → (R, C)：モデル → カメラの 回転・カメラの 場所（45→90→110 を 進み s で）"""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    s = progress(f); s90 = progress(90)
    a, b, u = (45, 90, s / s90) if s <= s90 else (90, 110, (s - s90) / (1 - s90))
    Ra, Ca = _rc(a); Rb, Cb = _rc(b)
    R = Slerp([0, 1], Rot.from_matrix([Ra, Rb]))([u]).as_matrix()[0]
    return R, Ca + (Cb - Ca) * u


# 第4.216版（まさちゃん 2026/11/24 12:23「神様馬の顔をスタートもっと下向きで、光りが強くなるにつれて上を向くようにして！」）：
#   顔の 向き（度・＋＝下向き）を はじめは 大きく 下に → 目の 光が 強く なるに つれて 上へ（110コマ目で 第14稿と 同じ 向き＝つぎの 爆発の コマと つながる）。
#   回す 中心は 耳の あいだの 少し うしろ。光（RIG）は 世界に 止まった まま（顔が 動くと 光の 当たりかたが かわる）
PIVOT = np.array([0.0, 0.2, 0.1])
NOD = [(0, 30.0), (36, 30.0), (50, 28.5), (62, 25.5), (74, 20.5), (84, 15.0), (92, 10.0), (100, 5.0), (106, 1.8), (110, 0.0), (200, 0.0)]


def nod_mat(f):
    """コマ f の 顔の うなずき（モデル → 世界・4×4）"""
    a = math.radians(curve(NOD, f)); c, s_ = math.cos(a), math.sin(a)
    R = np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = PIVOT - R @ PIVOT
    return T


def camera(f, w=W, h=H, near=0.05, far=50.0):
    R, C = pose(f)
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = -R @ C
    V = np.diag([1, -1, -1, 1.0]) @ M @ nod_mat(f)                                # OpenCV → OpenGL の 向き（顔の うなずき つき）
    t = 1 / math.tan(math.radians(FOV) / 2)
    P = np.array([[t * h / w, 0, 0, 0], [0, t, 0, 0], [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)], [0, 0, -1, 0]])
    c = Camera(V, P, w, h); c.near, c.far, c.fov_y = near, far, FOV
    return c


def project(cam, X):
    X = np.atleast_2d(np.asarray(X, float))
    c = np.c_[X, np.ones(len(X))] @ (cam.proj @ cam.view).T
    nd = c[:, :3] / c[:, 3:4]
    return np.c_[(nd[:, 0] + 1) / 2 * cam.W, (1 - nd[:, 1]) / 2 * cam.H]


# ---------------------------------------------------------------- G バッファ
GB_KEYS = ('alpha', 'alb', 'mr', 'nrm', 'pos', 'ao')


def buf(work, f0, f1):
    import gbuf
    os.makedirs(os.path.join(work, 'gb'), exist_ok=True)
    for f in range(f0, f1 + 1):
        out = os.path.join(work, 'gb', 'g%04d.npz' % f)
        if os.path.exists(out):
            continue
        t0 = time.time()
        G = gbuf.gbuffer(camera(f), ss=int(os.environ.get('GK16_SS', '2')), bands=int(os.environ.get('GK16_BANDS', '2')))
        np.savez_compressed(out + '.tmp.npz', **{k: G[k].astype(np.float16) for k in GB_KEYS})
        os.replace(out + '.tmp.npz', out)
        print('buf', f, round(time.time() - t0, 1), 's', flush=True)


def load_gb(work, f):
    d = np.load(os.path.join(work, 'gb', 'g%04d.npz' % f))
    return {k: d[k].astype(np.float32) for k in GB_KEYS}



# ---------------------------------------------------------------- 光（第14稿の コマに 合わせた：45〜106コマ目で 光の 強さを 合わせ、時刻の 強さは 第14稿の 明るさから）
def nz(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


def sstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


G_ = np.array([0.295, 0.309, 0.312]); WC = np.array([1.0, 0.82, 0.55]) * G_         # 光の 色（あたたかい 白）
RIG = dict(
    rims=[dict(d=(-0.85, 0.15, -0.5), c=WC * 0.834, rim=0.8), dict(d=(0.85, 0.15, -0.5), c=WC * 0.542, rim=0.8),          # うしろ横（ふちの 光）
          dict(d=(-0.75, 0.25, 0.6), c=WC * 0.30, side=1), dict(d=(0.75, 0.25, 0.6), c=WC * 0.30, side=1)],                 # 横まえ（ほおの 稜線の つや）
    rim_gold=np.array([1.0, 0.68, 0.30]), rim_k=2.3, rim_pow=5.0, envr_k=1.2, rim_dif=0.03, rim_rough=0.6, side_k=1.6, side_dif=0.02, skin_spec=0.10,
    front=[dict(d=(0.0, 0.8, -0.6), c=WC * 0.313, rim=0.4), dict(d=(0.0, -0.6, 0.8), c=WC * 0.145),                        # 上うしろ・下まえ
           dict(d=(-0.4, 0.45, 0.8), c=WC * 0.8)],                                                                     # 左まえ（第14稿の 白い 顔の 明るさ）
    sky=np.array([0.05, 0.041, 0.0275]) * 9.97 * G_,                                                                     # 空の 光（顔を ひらたく 明るく）
    env_rim=[dict(d=(-1.0, 0.2, 0.3), w=0.08, c=WC / G_ * G_ * 0.171), dict(d=(1.0, 0.2, 0.3), w=0.08, c=WC * 0.270)],      # 金の 映りこみ（横）
    env_front=[dict(d=(0.0, 1.0, 0.25), w=0.18, c=WC * 0.233), dict(d=(0.0, 0.4, 1.0), w=0.25, c=WC * 0.352)],           # 金の 映りこみ（上・前）
    fy=(-0.62, -0.40))                                                                                                   # あごの 下は 闇へ（モデルの 高さ）
# 時刻の 強さ（第14稿の 顔の 明るさ：ふち＝いちばん 明るい 所の 育ち・前＝まん中の 明るさの 育ち）
K_RIM = [(27, 0.0), (28, 0.005), (30, 0.023), (32, 0.11), (34, 0.24), (36, 0.44), (38, 0.68), (40, 0.72), (42, 0.78), (44, 0.84), (46, 0.91), (48, 1.0), (200, 1.0)]
K_FRONT = [(27, 0.0), (36, 0.001), (40, 0.004), (44, 0.008), (48, 0.012), (52, 0.03), (56, 0.06), (60, 0.10), (66, 0.20), (72, 0.36), (80, 0.55), (90, 0.75),
           (100, 0.92), (106, 1.0), (200, 1.0)]                                     # はじめは 顔の 前を 暗く（ふちと 金の 飾りが 先に 光る）


def curve(keys, f):
    xs, ys = zip(*keys)
    return float(np.interp(f, xs, ys))


def spec_ggx(N, V, L, rough, F0):
    Hh = nz(L + V)
    ndl = np.clip((N * L).sum(-1), 0, 1); ndv = np.clip((N * V).sum(-1), 1e-3, 1); ndh = np.clip((N * Hh).sum(-1), 0, 1); vdh = np.clip((V * Hh).sum(-1), 0, 1)
    a2 = (rough * rough) ** 2
    D = a2 / (np.pi * (ndh * ndh * (a2 - 1) + 1) ** 2 + 1e-7)
    k = (rough + 1) ** 2 / 8
    G = ndl / (ndl * (1 - k) + k) * ndv / (ndv * (1 - k) + k)
    F = F0 + (1 - F0) * ((1 - vdh) ** 5)[..., None]
    return (D * G / (4 * ndv + 1e-4))[..., None] * F, ndl


def shade(G, eye, kr, kf, eye_glow=0.0, eye_col=(0.25, 0.14, 0.03), eye_r=0.10, Tm=None):
    """G バッファ → 線形の 色（すけ を かけた もの）。kr：ふちの 光・kf：前の 光の 強さ（0〜）・eye_glow：目の 光が まわりを 照らす 強さ
       eye：カメラの 場所（モデルの 座標）・Tm：モデル → 世界（顔の うなずき。光は 世界に 止まった まま）"""
    A = G['alpha']; alb = G['alb']; m = np.clip(G['mr'][..., 0], 0, 1)[..., None]; rough = np.clip(G['mr'][..., 1], 0.05, 1)
    N = nz(G['nrm']); P0 = G['pos']; ao = np.clip(G['ao'], 0, 1)
    Rm, tm = (np.eye(3), np.zeros(3)) if Tm is None else (np.asarray(Tm, float)[:3, :3], np.asarray(Tm, float)[:3, 3])
    Rm32 = Rm.astype(np.float32)
    N = nz(N @ Rm32.T); P = P0 @ Rm32.T + tm.astype(np.float32)
    eye = Rm @ np.asarray(eye, float) + tm
    V = nz(np.asarray(eye, np.float32)[None, None, :] - P)
    ndv = np.clip((N * V).sum(-1), 1e-3, 1)
    F0 = 0.04 * (1 - m) + alb * m
    dif = alb * (1 - m)
    col = np.zeros_like(alb)
    for group, k in (('rims', kr), ('front', kf)):
        if k <= 0:
            continue
        for L in RIG[group]:
            Ld = nz(np.array(L['d'], np.float32)); c = np.array(L['c'], np.float32) * k
            kd, rr_ = 1.0, rough
            if group == 'rims':
                c = c * RIG['rim_k'] * RIG['rim_gold'] / WC * G_; kd = RIG['rim_dif']; rr_ = np.clip(rough * RIG['rim_rough'], 0.05, 1)
                if L.get('side'):
                    c = c * RIG['side_k']; kd = RIG['side_dif']
            sp, ndl = spec_ggx(N, V, Ld[None, None, :], rr_, F0)
            if group == 'rims':
                sp = sp * (RIG['skin_spec'] + (1 - RIG['skin_spec']) * m)          # ふちの 光の つやは 金の 飾りに（肌は 少し）
            col += (dif / np.pi * ndl[..., None] * kd + sp) * c
            if L.get('rim'):
                col += ((1 - ndv) ** RIG['rim_pow'] * np.clip((N * Ld).sum(-1) + 0.3, 0, 1) * L['rim'])[..., None] * c * (0.3 + 0.7 * ao[..., None])
    if kf > 0:
        hemi = (0.5 + 0.5 * N[..., 1:2]) * RIG['sky'] * kf
        col += dif * hemi * ao[..., None]
    R = nz(2 * ndv[..., None] * N - V)
    Fe = F0 + (np.maximum(1 - rough[..., None], F0) - F0) * ((1 - ndv) ** 5)[..., None]
    for group, k in (('env_rim', kr), ('env_front', kf)):
        if k <= 0:
            continue
        for lob in RIG[group]:
            d = nz(np.array(lob['d'], np.float32)); w = lob['w'] + (rough ** 2) * 0.6
            kk_ = k * (RIG['envr_k'] if group == 'env_rim' else 1.0)
            col += Fe * (np.exp(((R * d).sum(-1) - 1) / w)[..., None] * np.array(lob['c'], np.float32) * kk_) * (ao[..., None] ** 0.5)
    if eye_glow > 0:                                                             # 目の 光が まわり（まぶた・ほお・飾り）を 照らす
        for kk in ('eyeL', 'eyeR'):
            pe = Rm @ (LM[kk] + np.array([0, 0.005, 0.04])) + tm
            dv = pe[None, None, :] - P; dd = np.linalg.norm(dv, axis=-1) + 1e-6; Ld = dv / dd[..., None]
            ndl = np.clip((N * Ld).sum(-1), 0, 1); att = 1.0 / (1 + (dd / eye_r) ** 2)
            sp, _ = spec_ggx(N, V, Ld, rough, F0)
            col += (dif / np.pi * ndl[..., None] + sp * 0.5) * (att[..., None] * np.array(eye_col, np.float32) * eye_glow)
    col *= sstep(RIG['fy'][0], RIG['fy'][1], P0[..., 1])[..., None]                # あごの 下の 闇は 顔に ついた まま
    return col * A[..., None]


def tonemap(x):
    a_, b_, c_, d_, e_ = 2.51, 0.03, 2.43, 0.59, 0.14
    x = np.clip(x, 0, None); x = np.clip((x * (a_ * x + b_)) / (x * (c_ * x + d_) + e_), 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 1e-9), 1 / 2.4) - 0.055)


# ---------------------------------------------------------------- 目の 光（第14稿：39コマ目で 両目が ともる → だんだん 強く → 108〜112 で ふくらんで 大爆発へ）
IGN = 39
EYE_EMIT = np.array([1.5, 0.78, 0.18])                                             # 目の 形の 光（線形）
EYE_HALO = np.array([1.0, 0.66, 0.22])                                           # にじみの 色


def eye_level(f):
    if f < IGN:
        return 0.0
    flash = {39: 1.7, 40: 1.4, 41: 1.18, 42: 1.06}.get(f, 1.0)                    # ともった 瞬間（キィィン＋ドォン）
    swell = {108: 1.25, 109: 1.6, 110: 2.3, 111: 3.4, 112: 5.5}.get(f, 1.0)        # 大爆発の まえ
    flick = 1 + 0.05 * math.sin(f * 2.7) + 0.03 * math.sin(f * 5.3 + 1)
    base = float(np.interp(f, [39, 60, 90, 106], [0.6, 0.75, 1.0, 1.15]))
    return base * flash * swell * flick


def eye_mask(G):
    """3D の 目（黄色い 瞳・金属で ない）の 形"""
    alb = G['alb']; A = G['alpha']
    srgb = np.clip(alb, 0, 1) ** (1 / 2.2)
    hsv = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2HSV)
    h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    col = sstep(0.45, 0.6, s_) * sstep(0.45, 0.6, v) * ((h > 38) & (h < 64)) * (G['mr'][..., 0] < 0.25)
    out = np.zeros_like(A)
    for k in ('eyeL', 'eyeR'):
        d = np.linalg.norm(G['pos'] - LM[k][None, None, :], axis=-1)
        out = np.maximum(out, col * (1 - sstep(0.06, 0.09, d)))
    return (out * A).astype(np.float32)


def gauss_sprite(cx, cy, sx, sy):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    return np.exp(-(((xs - cx) / sx) ** 2 + ((ys - cy) / sy) ** 2) / 2)


# ---------------------------------------------------------------- 金の 雷（目の まわり → たてがみ → 下の 闇）
def _rng(*k):
    return np.random.default_rng([int(abs(x)) for x in k])


def bolt_path(rng, p0, p1, rough=0.36, depth=6):
    pts = [np.asarray(p0, float), np.asarray(p1, float)]
    for _ in range(depth):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            L = np.linalg.norm(b - a); n = np.array([-(b - a)[1], (b - a)[0]]) / (L + 1e-9)
            new += [(a + b) / 2 + n * rng.normal(0, rough * L * 0.5), b]
        pts = new
    return np.array(pts)


def bolts(f, eyes2d):
    """コマ f の 雷：[(点の 列, 太さ px, 強さ)]。1本は 2〜3コマ 生きる（同じ 形）"""
    out = []

    def add(rng, p0, ang, L, w, k, branches=3):
        p1 = p0 + L * np.array([math.cos(ang), math.sin(ang)])
        P = bolt_path(rng, p0, p1)
        out.append((P, w, k))
        for _ in range(rng.integers(0, branches + 1)):
            j = rng.integers(len(P) // 5, len(P) * 4 // 5)
            a2 = ang + rng.choice([-1, 1]) * rng.uniform(0.35, 0.95); L2 = L * rng.uniform(0.25, 0.5)
            q1 = P[j] + L2 * np.array([math.cos(a2), math.sin(a2)])
            out.append((bolt_path(rng, P[j], q1, depth=5), w * 0.6, k * 0.6))
    if f >= IGN:                                                                 # 目の まわり（目の 外がわ・ほおへ）
        n_eye = 2 if f <= 41 else int(round(float(np.interp(f, [42, 60, 90, 112], [1.2, 2.0, 2.8, 3.8]))))
        for side, E in enumerate(eyes2d):
            for i in range(n_eye):
                life = 2 + (i + side) % 2; ep = (f + i * 7 + side * 3) // life
                rng = _rng(16, 1, side, i, ep)
                if rng.random() > 0.82:
                    continue
                base = math.pi if side == 0 else 0.0                              # 画面の 左の 目は 左へ・右の 目は 右へ
                ang = base + (1 if side == 0 else -1) * rng.uniform(-0.9, 1.1) * (-1 if side == 0 else 1)
                ang += rng.normal(0, 0.35)
                L = rng.uniform(60, 170) * (1 + 0.5 * float(sstep(60, 112, f)))
                add(rng, np.asarray(E) + rng.normal(0, 7, 2), ang, L, rng.uniform(0.7, 1.2), rng.uniform(1.8, 2.8))
    if f >= 50:                                                                  # たてがみ（左・右・上）
        n_m = int(round(float(np.interp(f, [50, 80, 112], [1.0, 3.0, 5.5]))))
        ey = float(np.mean([e[1] for e in eyes2d]))
        zones = [((15, 190), (ey - 330, ey + 260)), ((590, 765), (ey - 330, ey + 260)), ((170, 610), (ey - 560, ey - 360))]
        for i in range(n_m):
            life = 2 + i % 2; ep = (f + i * 5) // life
            rng = _rng(16, 2, i, ep)
            if rng.random() > 0.8:
                continue
            (x0, x1), (y0, y1) = zones[rng.integers(0, 3)]
            p0 = np.array([rng.uniform(x0, x1), rng.uniform(y0, y1)])
            add(rng, p0, rng.uniform(0, 2 * math.pi), rng.uniform(70, 200), rng.uniform(0.6, 1.0), rng.uniform(1.3, 2.0))
    if f >= 70:                                                                  # 下の 闇（小さな 雷）
        n_b = 1 if f < 95 else 2
        for i in range(n_b):
            life = 3; ep = (f + i * 11) // life
            rng = _rng(16, 3, i, ep)
            if rng.random() > 0.65:
                continue
            x = rng.uniform(20, 200) if rng.random() < 0.5 else rng.uniform(580, 760)
            add(rng, np.array([x, rng.uniform(1120, 1500)]), rng.uniform(0, 2 * math.pi), rng.uniform(50, 120), 1.0, rng.uniform(1.4, 2.2), branches=1)
    return out


def bolt_layer(lst):
    """雷の 線（2倍で 描いて 平均）→ 芯（白っぽい 金）・にじみ（金）の 線形の 色"""
    S = 2; can = np.zeros((H * S, W * S), np.float32)
    for P, w, k in lst:
        pts = np.round(P * S * 8).astype(np.int32).reshape(-1, 1, 2)
        lay = np.zeros_like(can)
        cv2.polylines(lay, [pts], False, 1.0, thickness=max(1, int(round(w * S))), lineType=cv2.LINE_AA, shift=3)
        can = np.maximum(can, lay * k)
    core = can.reshape(H, S, W, S).mean((1, 3))
    g1 = cv2.GaussianBlur(core, (0, 0), 1.6); g2 = cv2.GaussianBlur(core, (0, 0), 5.0)
    return core[..., None] * np.array([1.0, 0.88, 0.50]) + g1[..., None] * np.array([1.0, 0.72, 0.22]) * 1.0 + g2[..., None] * np.array([1.0, 0.58, 0.12]) * 0.7


# ---------------------------------------------------------------- 火の粉（金の 小さな 点が ゆっくり 上へ）
def embers(f, n=70):
    rng = np.random.default_rng(1234)
    x0 = rng.uniform(0, W, n); y0 = rng.uniform(0, H, n); vy = rng.uniform(0.4, 1.4, n); ph = rng.uniform(0, 6.28, n)
    sz = rng.uniform(0.7, 1.7, n); br = rng.uniform(0.25, 1.0, n)
    y = (y0 - vy * f) % H; x = x0 + 6 * np.sin(f * 0.05 + ph)
    tw = 0.55 + 0.45 * np.sin(f * 0.4 + ph * 3)
    vis = float(sstep(28, 52, f))
    out = np.zeros((H, W), np.float32)
    for xi, yi, s_, b, t in zip(x, y, sz, br, tw):
        x0_, x1_ = int(max(0, xi - 6)), int(min(W, xi + 7)); y0_, y1_ = int(max(0, yi - 6)), int(min(H, yi + 7))
        if x1_ <= x0_ or y1_ <= y0_:
            continue
        yy, xx = np.mgrid[y0_:y1_, x0_:x1_]
        out[y0_:y1_, x0_:x1_] += np.exp(-((xx - xi) ** 2 + (yy - yi) ** 2) / (2 * s_ * s_)) * b * t * vis
    return out[..., None] * np.array([1.4, 0.9, 0.35])


def bloom(rgb, thr=0.9, k=0.35):
    lum = rgb.max(-1)
    hi = rgb * np.clip((lum - thr) / thr, 0, 6)[..., None]
    g = cv2.GaussianBlur(hi, (0, 0), 4) * 0.5 + cv2.GaussianBlur(hi, (0, 0), 12) * 0.3 + cv2.GaussianBlur(hi, (0, 0), 32) * 0.2
    return rgb + g * k


def comp_frame(work, f):
    """コマ f（0〜112）→ sRGB の 絵（H×W×3・uint8）"""
    if f < 28:
        return np.zeros((H, W, 3), np.uint8)
    cam = camera(f)
    G = load_gb(work, f)
    E = eye_level(f)
    col = shade(G, cam.eye, curve(K_RIM, f), curve(K_FRONT, f), eye_glow=E * 0.8, Tm=nod_mat(f))
    eyes2d = project(cam, [LM['eyeL'], LM['eyeR']])
    if E > 0:
        col += eye_mask(G)[..., None] * EYE_EMIT * E
        grow = 1 + max(0.0, E - 1.3) * 0.55
        hot = float(sstep(1.0, 4.0, E))                                          # 強く なる ほど 白く
        for (ex, ey) in eyes2d:
            col += gauss_sprite(ex, ey, 10 * grow, 7 * grow)[..., None] * (EYE_HALO * (1 - hot) + np.array([1.0, 0.92, 0.7]) * hot) * 0.55 * E
            col += gauss_sprite(ex, ey, 34 * grow, 24 * grow)[..., None] * EYE_HALO * 0.16 * E
    col += bolt_layer(bolts(f, eyes2d))
    col += embers(f)
    col = bloom(col)
    out = tonemap(col)
    out = out + (np.random.default_rng(f).random(out.shape) - 0.5) / 255.0        # 帯の 縞を ふせぐ
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def comp(work, f0, f1):
    os.makedirs(os.path.join(work, 'out'), exist_ok=True)
    for f in range(f0, f1 + 1):
        t0 = time.time()
        im = comp_frame(work, f)
        cv2.imwrite(os.path.join(work, 'out', '%04d.png' % f), im[..., ::-1])
        print('comp', f, round(time.time() - t0, 1), 's', flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--buf':
        buf(a[1], int(a[2]) if len(a) > 2 else 15, int(a[3]) if len(a) > 3 else LAST)
    elif a and a[0] == '--comp':
        comp(a[1], int(a[2]) if len(a) > 2 else 0, int(a[3]) if len(a) > 3 else LAST)
    else:
        print(__doc__)
