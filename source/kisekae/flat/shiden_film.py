"""紫電（第4.70版）：② を 1コマずつ 3D で 描いた 動画に（sd_film.mp4・30コマ/秒・音なし）
   まさちゃん「一枚目の画像から、二枚目の画像までの映像まで消して！ 三枚目のシーンからヒズメカットインまでのシーン消して、雑すぎる！
   もっと二枚目の馬みたいに蹄カットインをリアルな映像で作成して！ あと蹄カットインのあとから四枚目までのシーン消して！
   四枚目の光はもっと立体的に、リアルもっと強く発光した映像にして！ 蹄カットインの背景は、もっとリアルに立体的で、激しい映像にして！
   あと蹄カットインは、蹄が画面を切り裂いてるイメージね！ めちゃくちゃリアルで立体感のある表現にして！ 馬の顔のシーンもっと長くていい！ 動き方は任せる！
   あくまで参考にするのは、おくってるファイルの画像と動きをもとにしてね！ 求めているのは、全部二枚目の写真のようなリアルなエフェクトにしてほしい！」
   → ② は 3つの 場面だけ（どれも 3D で 光と つやまで 計算した 絵）：
     A 馬の 顔（0〜FACE 秒）：闇から 青むらさきの 光の 中に 黒い 馬の 横顔が 浮かぶ → 頭が 上がって こちらを 向き・耳が 立ち・鼻から 白い 息・
       たてがみが なびく → 目に 火が ともって 強く 光る → カメラが 目へ 寄って 目の 光が 画面を つつむ
     B 蹄の カットイン（FACE〜HOOF 秒）：むらさきの 雷雲の 中を 前へ 突き進む（雲の 層・雷・火の粉・とんでくる かけら）→ 焼けた 蹄鉄の 蹄が 左から
       画面を 切り裂いて 右へ（まん中で ゆっくり）→ 切り口が 光って 画面の ガラスが 割れて とぶ → 切り口が 開いて 光が あふれる
     C 光（HOOF〜FILM 秒）：深い 緑の 空間に 白熱の 光の 玉・まわる 金の 輪・光の 筋・集まる 金の 粒 → 光が ふくらんで 画面が 光で うまる（→ ③ ど！！！的中）
   python3 flat/shiden_film.py <作業フォルダ> [はじめの コマ] [おわりの コマ]   （コマ f%03d.png。SCALE=0.5 で ためしの 小さい 絵）
   python3 flat/shiden_film.py --encode <作業フォルダ> <出力.mp4>"""
import os, sys, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from h3d import Scene, nrm
import horse3d as Hm
from hair2d import HairBuf, guide
from fire2d import aces, to_srgb
from paint import fbm, blur, smoothstep

import shiden as SDM                             # 時刻の きまり（shiden.py の FILM：音・③ と そろえる）
F = SDM.FILM
FPS = F['FPS']                                   # 30コマ/秒
FACE, HOOF, FILM = F['FACE'], F['HOOF'], F['END']   # 場面の おわりの 秒（A 顔 4.0・B 蹄 6.4・C 光 7.6）
NF = int(round(FILM * FPS))                      # 228コマ
W0, H0 = F['W'], F['H']                          # 動画の 大きさ（画面 390×844 の 2倍）
SC = float(os.environ.get('SCALE', '1'))         # ためす とき 0.5
W, H = int(W0 * SC), int(H0 * SC)
S = W / 780.0                                    # 長さの 倍率（780 の 時 1）


# ================================================================ 道具
def spline(t, keys):
    """(秒, 値) の 列を なめらかに つなぐ（Catmull-Rom・はしは 止まる）"""
    ts = [k[0] for k in keys]
    vs = [np.asarray(k[1], float) for k in keys]
    if t <= ts[0]:
        return vs[0]
    if t >= ts[-1]:
        return vs[-1]
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    t0, t1 = ts[i], ts[i + 1]
    u = (t - t0) / (t1 - t0)
    p0 = vs[i - 1] if i > 0 else vs[i]
    p1, p2 = vs[i], vs[i + 1]
    p3 = vs[i + 2] if i + 2 < len(vs) else vs[i + 1]
    d0 = t1 - (ts[i - 1] if i > 0 else t0)
    d1 = (ts[i + 2] if i + 2 < len(ts) else t1) - t0
    m1 = (p2 - p0) / max(d0, 1e-6) * (t1 - t0) if i > 0 else np.zeros_like(p1)
    m2 = (p3 - p1) / max(d1, 1e-6) * (t1 - t0) if i + 2 < len(vs) else np.zeros_like(p1)
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * m2


def ss(a, b, x):
    return float(smoothstep(a, b, np.float32(x)))


GRID = None


def grid():
    global GRID
    if GRID is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        GRID = (yy, xx)
    return GRID


def bloom(img, k=1.0):
    """明るい 所の にじみ（3段）"""
    lm = img.max(2)
    br = img * smoothstep(0.55, 2.2, lm)[..., None]
    return img + (blur(br, 4 * S) * 0.35 + blur(br, 16 * S) * 0.25 + blur(br, 48 * S) * 0.18) * k


def finish(img, seed, vig=0.55, grain=0.008, ca=0.0):
    """仕上げ：周辺を 暗く → トーン（ACES）→ sRGB → 色の にじみ（ふち）→ 粒"""
    yy, xx = grid()
    v = np.clip(1.12 - np.sqrt(((xx - W * .5) / (W * .95)) ** 2 + ((yy - H * .45) / (H * .75)) ** 2) * vig, .3, 1)[..., None]
    out = to_srgb(aces(img * v))
    if ca > 0:
        r = cv2.warpAffine(out[..., 0], np.float32([[1 + ca, 0, -W * ca / 2], [0, 1 + ca, -H * ca / 2]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        b = cv2.warpAffine(out[..., 2], np.float32([[1 - ca, 0, W * ca / 2], [0, 1 - ca, H * ca / 2]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        out = np.dstack([r, out[..., 1], b])
    rng = np.random.default_rng(seed)
    out = out + rng.normal(0, grain, (H, W)).astype(np.float32)[..., None]
    return np.clip(out, 0, 1)


def screen(base, col, a):
    """スクリーン 合成（sRGB の 0〜1）：base + a・col・(1 − base)"""
    return base + (a[..., None] * col) * (1 - base)


def save_png(img, path):
    tmp = path[:-4] + '_tmp.png'                                                   # 書きおわってから 名前を かえる（とちゅうで 止まっても こわれた コマを のこさない）
    if not cv2.imwrite(tmp, (np.clip(img[..., ::-1], 0, 1) * 255 + .5).astype(np.uint8)):
        raise IOError('書けない: ' + path)
    os.replace(tmp, path)


# ================================================================ A 馬の 顔
FOV = 34.0
FACE_KEYS = [  # 秒: 頭の 角度・耳・カメラ（横から まわる u・上下 v・距離）・目の 画面の 場所
    (0.0, dict(ha=-45, ear=-16, u=.08, v=.07, dist=2.8, ex=.53, ey=.36)),
    (1.0, dict(ha=-41, ear=-8, u=.14, v=.06, dist=2.5, ex=.52, ey=.36)),
    (2.2, dict(ha=-32, ear=12, u=.31, v=.03, dist=2.0, ex=.49, ey=.36)),
    (3.0, dict(ha=-27, ear=22, u=.42, v=.0, dist=1.62, ex=.47, ey=.36)),
    (3.55, dict(ha=-25, ear=24, u=.46, v=-.01, dist=1.12, ex=.47, ey=.38)),
    (4.0, dict(ha=-24, ear=25, u=.48, v=-.02, dist=0.72, ex=.48, ey=.41)),
]
PUFFS = F['PUFFS']                               # 鼻から 白い 息（秒）


def face_state(t):
    d = {k: float(spline(t, [(a, b[k]) for a, b in FACE_KEYS])) for k in FACE_KEYS[0][1]}
    d['g'] = float(spline(t, [(0, 0.0), (0.9, 0.0), (2.0, .4), (2.9, 1.0), (3.55, 1.7), (4.0, 3.0)]))    # 目の 光（1 を こえると あふれる）
    d['L'] = ss(0.0, 1.1, t)                                                                               # 光が ともる（闇から 浮かぶ）
    return d


def face_aim(cam, eye, W_, H_, sx, sy):
    tgt = eye.copy()
    th = math.tan(math.radians(FOV) / 2); asp = W_ / H_
    for _ in range(30):
        fw = nrm(tgt - cam); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
        dd = eye - cam
        nx = (dd @ rt) / (dd @ fw) / (th * asp); ny = (dd @ up) / (dd @ fw) / th
        px, py = (nx + 1) / 2, (1 - ny) / 2
        D = np.linalg.norm(dd)
        tgt = tgt - rt * ((sx - px) * 2 * th * asp * D * .8) + up * ((sy - py) * 2 * th * D * .8)
    return tgt


def face_setup(st):
    pose = dict(Hm.REAR)
    pose['head_ang'] = st['ha']
    pose['ear_rot'] = st['ear']
    tmp = Scene()
    Sx = Hm.build(tmp, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    eye = np.array(Sx['eye'], float)
    U3, V3 = np.array(Sx['head_u'], float), np.array(Sx['head_v'], float)
    d = nrm(np.array([0, 0, 1.0]) + U3 * st['u'] + V3 * st['v'])
    cam = eye + d * st['dist']
    tgt = face_aim(cam, eye, W, H, st['ex'], st['ey'])
    return pose, Sx, cam, tgt


def face_marks(st):
    """3D を 描かずに 目・鼻・首すじの 画面の 場所だけ"""
    pose, Sx, cam, tgt = face_setup(st)
    sc = Scene(); sc.image(W, H, 1); sc.camera(cam, tgt, FOV)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    ts = np.linspace(0, 1, 40)
    crest = Hm.bez(Sx['crest'], ts)
    return dict(crest=P(np.c_[crest, np.full(len(ts), 0.02)]).tolist(), poll=P([Hm.v3(Sx['poll'], 0.0)])[0].tolist(),
                eye=P([Sx['eye']])[0].tolist(), muzzle=P([Hm.head_pt(Sx, 0.56, -0.03)])[0].tolist(),
                nose=P([Hm.head_pt(Sx, 0.545, 0.02, 0.05)])[0].tolist(), chin=P([Hm.head_pt(Sx, 0.50, -0.11)])[0].tolist())


def face_render(st, prefix):
    pose, S0, cam, tgt = face_setup(st)
    L, g = st['L'], min(st['g'], 1.0)
    sc = Scene()
    sc.image(W, H, 1)
    sc.camera(cam, tgt, FOV)
    sc.bounce(1)
    cd = nrm(cam - tgt)
    k = 0.15 + 0.85 * L
    sc.env(tuple(np.array((0.006, 0.002, 0.012)) * k), tuple(np.array((0.010, 0.004, 0.018)) * k), (0.002, 0.001, 0.004), (0.0008, 0.0003, 0.0014))
    sc.lobe(nrm(-cd + np.array([0.35, 0.55, 0.0])), tuple(np.array((1.1, 0.28, 0.95)) * k), 6.0)
    sc.lobe(nrm(np.array([-0.2, 1.0, -0.3])), tuple(np.array((0.18, 0.16, 0.26)) * k), 8.0)
    sc.light(nrm(cd * 0.55 + np.array([-0.55, 0.75, 0.15])), tuple(np.array((0.32, 0.28, 0.42)) * k), 10, 1)
    sc.light(nrm(-cd + np.array([0.45, 0.45, 0.0])), tuple(np.array((6.5, 1.5, 4.8)) * L), 8, 0)
    sc.light(nrm(-cd + np.array([-0.6, -0.15, 0.0])), tuple(np.array((1.3, 1.9, 5.2)) * L), 8, 0)
    sc.light(nrm(-cd * 0.6 + np.array([0.0, 1.0, 0.0])), tuple(np.array((1.8, 1.6, 2.4)) * L), 8, 0)
    eye = np.array(S0['eye'], float)
    sc.plight(eye + cd * 0.05 + np.array([0, 0.01, 0]), (0.05 * g + 0.004, 0.022 * g + 0.001, 0.004 * g), 8, 0)
    sc.mat(1, 1, (0.012, 0.009, 0.014), 0.42, 0.9, 0.35, 3.5)
    sc.mat(5, 1, (0.006, 0.003, 0.002), 0.06, 0.0, 0.3)
    sc.mat(6, 1, (0.02, 0.017, 0.015), 0.45, 0.3, 0.4)
    Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    return sc.render(prefix)


FACE_TEX = {}


def face_tex(seed=7):
    """顔の 場面で ずっと 使う もよう（もや・けむり・毛なみ・星・息）"""
    if not FACE_TEX:
        big = int(math.hypot(W, H)) + 8
        rs = np.random.RandomState(seed + 3)
        FACE_TEX['fur'] = cv2.resize(rs.rand(big // 2, big // 22).astype(np.float32), (big, big), interpolation=cv2.INTER_CUBIC)
        FACE_TEX['haze'] = fbm(H * 2, W * 2, 260 * S, 5, seed=seed + 1)
        FACE_TEX['smoke'] = fbm(H * 2, W * 2, 220 * S, 5, seed=seed + 9)
        FACE_TEX['fs'] = fbm(H, W, 140 * S, 3, seed=seed + 5)
        FACE_TEX['vap'] = fbm(512, 512, 60, 5, seed=seed + 21)
        rng = np.random.default_rng(seed + 31)
        FACE_TEX['stars'] = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(.3, 1.0), rng.uniform(0, 6.28), rng.uniform(.4, 1.6)) for _ in range(160)]
        FACE_TEX['emb'] = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(.4, 1.8), rng.uniform(.2, 1.0)) for _ in range(120)]
    return FACE_TEX


def vapor(img, M, t, hs, seed=7):
    """鼻から 白い 息（2回）：鼻の 穴から 下前へ 出て ふくらみ・うすれる。うしろの 光で ふちが ひかる"""
    yy, xx = grid()
    tx = face_tex()
    nx, ny = M['nose']
    mx, my = M['muzzle']
    ex, ey = M['eye']
    hd = np.array([mx - ex, my - ey]); hd /= np.linalg.norm(hd) + 1e-6
    dirv = nrm(np.array([-0.78, .62]))                                          # 下へ 出て 風で 左へ（たてがみと 同じ 風）
    out = np.zeros((H, W), np.float32)
    for k, t0 in enumerate(PUFFS):
        a = (t - t0) / 1.1
        if not 0 < a < 1:
            continue
        L_ = (60 + 480 * (1 - (1 - a) ** 2)) * hs * S
        cx, cy = nx + dirv[0] * L_ * .55, ny + dirv[1] * L_ * .55
        rx, ry = (26 + 170 * a) * hs * S, (18 + 95 * a) * hs * S
        ang = math.atan2(dirv[1], dirv[0])
        du = ((xx - cx) * math.cos(ang) + (yy - cy) * math.sin(ang)) / (rx * 1.7)
        dv = (-(xx - cx) * math.sin(ang) + (yy - cy) * math.cos(ang)) / ry
        blob = np.exp(-(du ** 2 + dv ** 2) * 1.6)
        vt = tx['vap']
        M2 = np.float32([[512 / (W * 1.1), 0, (k * 97 + a * 60) % 200], [0, 512 / (H * .55), (k * 53 - a * 40) % 200]])
        n_ = cv2.warpAffine(vt, M2, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
        dens = blob * smoothstep(.35, .75, n_ + .25 * (1 - a)) * (1 - a) ** 1.3 * ss(0, .08, a)
        out = np.maximum(out, dens)
    if out.max() <= 0:
        return img
    out = blur(out, 2 * S)
    col = np.array([0.55, 0.5, 0.75])
    return img * (1 - out[..., None] * .55) + col * out[..., None] * .55 * 0.9


def face_frame(t, R, M, seed=7):
    """3D の 顔に 背景・たてがみ・息・光る 目・火の粉・星を 重ねる（2まい目の ような 青むらさきの 光）→ 0〜1 の sRGB"""
    st = face_state(t)
    g, L = st['g'], st['L']
    rgb, A = R['rgb'], R['a']
    yy, xx = grid()
    tx = face_tex(seed)
    ex, ey = M['eye']
    mz = np.array(M['muzzle']); pl = np.array(M['poll'])
    hl = np.linalg.norm(mz - np.array([ex, ey]))
    hs = hl / (817 * S)                                                          # 頭の 大きさ（寄ると 大きく：3.0秒で 1）
    hd = (mz - np.array([ex, ey])) / (hl + 1e-6)
    # ---------- 背景（ゆっくり 流れる もや・頭の うしろの 光・右上の 桃色・左下の 青） ----------
    ty = (yy / H)[..., None]
    bg = np.array([0.004, 0.0015, 0.009]) * (1 - ty) + np.array([0.0015, 0.0008, 0.004]) * ty
    ox, oy = int((t * 30 * S) % W), int((t * 12 * S) % H)
    haze = tx['haze'][oy:oy + H, ox:ox + W]
    back = np.exp(-(((xx - ex - 120 * S * hs) / (W * .55)) ** 2 + ((yy - ey + 40 * S) / (H * .32)) ** 2)) * (0.55 + 0.7 * haze)
    pink = np.exp(-(((xx - W * 1.0) / (W * .7)) ** 2 + ((yy - H * .15) / (H * .4)) ** 2)) * (0.4 + 0.8 * haze)
    blue = np.exp(-(((xx - W * 0.05) / (W * .6)) ** 2 + ((yy - H * .85) / (H * .35)) ** 2)) * (0.4 + 0.7 * haze)
    bg = bg + (back[..., None] * np.array([0.050, 0.012, 0.060]) + pink[..., None] * np.array([0.06, 0.010, 0.045]) + blue[..., None] * np.array([0.008, 0.012, 0.045])) * L
    # 星（ゆっくり 流れて またたく）
    star = np.zeros((H, W), np.float32)
    for (sx_, sy_, b_, ph, sz) in tx['stars']:
        x = (sx_ * W - t * 9 * S * (0.5 + b_)) % W
        y = (sy_ * H + t * 4 * S) % H
        tw = 0.55 + 0.45 * math.sin(t * 3.1 + ph)
        cv2.circle(star, (int(x * 4), int(y * 4)), max(1, int(sz * S * 4)), float(b_ * tw), -1, cv2.LINE_AA, shift=2)
    star = blur(star, .7 * S)
    bg = bg + star[..., None] * np.array([0.06, 0.055, 0.09]) * L
    # 首と 胸は 闇へ（頭だけ 光る）
    nv = np.array([hd[1], -hd[0]])
    if nv[1] > 0:
        nv = -nv
    cxh, cyh = ex + hd[0] * hl * .42 + nv[0] * hl * .06, ey + hd[1] * hl * .42 + nv[1] * hl * .06
    pu = ((xx - cxh) * hd[0] + (yy - cyh) * hd[1]) / (hl * .9)
    pv = ((xx - cxh) * nv[0] + (yy - cyh) * nv[1])
    pv = np.where(pv > 0, pv / (hl * .5), -pv / (hl * .26))
    headm = 1 - smoothstep(.7, 1.15, np.sqrt(pu ** 2 + pv ** 2))
    rgb = rgb * (0.04 + 0.96 * headm ** 1.5)[..., None]
    img = bg * (1 - A[..., None]) + rgb
    smoke = smoothstep(.25, .7, tx['smoke'][(oy * 2) % H:(oy * 2) % H + H, ox:ox + W]) * smoothstep(H * .5, H * .82, yy + 60 * S * np.sin(xx / W * 3 + t * .9))     # 下は けむりに しずむ
    img = img * (1 - smoke[..., None] * .85) + smoke[..., None] * .85 * np.array([0.012, 0.005, 0.020]) * (0.3 + 0.7 * L)
    # 毛なみ
    ang = math.atan2(hd[1], hd[0])
    big = tx['fur'].shape[0]
    Mr = cv2.getRotationMatrix2D((big / 2, big / 2), -math.degrees(ang), 1.0)
    fur = cv2.warpAffine(tx['fur'], Mr, (big, big), borderMode=cv2.BORDER_REFLECT)[(big - H) // 2:(big - H) // 2 + H, (big - W) // 2:(big - W) // 2 + W]
    lum = img.mean(-1)
    img = img * (1 + (fur - .5)[..., None] * 0.22 * smoothstep(0.004, 0.05, lum)[..., None] * A[..., None])
    # ---------- たてがみ（風で なびく） ----------
    rng = np.random.default_rng(seed)
    hb = HairBuf(H, W, ss=2)
    crest = np.array(M['crest'])
    nC = len(crest)
    fs = tx['fs']
    wind = math.radians(-104) + 0.22 * math.sin(t * 1.9) + 0.08 * math.sin(t * 4.3)

    def flow_m(x, y, a, tt):
        d = math.atan2(math.sin(wind - a), math.cos(wind - a))
        return d * 0.07 + (fs[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))] - .5) * 0.25
    for i in range(110):
        tt = (i + rng.random()) / 110
        k0 = 0.04 + tt * 0.9
        q = k0 * (nC - 1); a0 = int(q); a1 = min(a0 + 1, nC - 1)
        p = crest[a0] + (crest[a1] - crest[a0]) * (q - a0)
        tg = crest[a1] - crest[max(a0 - 1, 0)]
        out_ang = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.sin(out_ang) > 0.3:
            out_ang += math.pi
        Ln = rng.uniform(300, 620) * S * hs * (0.7 + 0.5 * math.sin(tt * math.pi))
        gpts = guide(p + rng.normal(0, 4 * S * hs, 2), out_ang + rng.normal(0, 0.35), Ln, 34, rng, flow_m, wave=rng.uniform(1.2, 2.4), phase=rng.uniform(0, 6) + t * 2.6)
        hb.lock(gpts, 46, rng, spread=rng.uniform(6, 13) * S * hs, clump=0.55, wmin=0.45 * S * hs, wmax=1.2 * S * hs, rimk=1.0)
        hb.lock(gpts[:10], 26, rng, spread=7 * S * hs, clump=0.3, wmin=0.7 * S * hs, wmax=1.5 * S * hs, rimk=0.05)
    for i in range(14):
        gpts = guide(pl + rng.normal(0, 6 * S * hs, 2), wind + rng.normal(0.3, 0.3), rng.uniform(140, 260) * S * hs, 18, rng, flow_m, wave=1.2, phase=rng.uniform(0, 6) + t * 3.4)
        keep = np.hypot(gpts[:, 0] - ex, gpts[:, 1] - ey) > 85 * S * hs
        cut = int(np.argmin(keep)) if not keep.all() else len(gpts)
        if cut > 4:
            hb.lock(gpts[:cut], 20, rng, spread=4 * S * hs, clump=0.65, wmin=0.4 * S * hs, wmax=1.0 * S * hs, rimk=0.6)
    cov, rimw, cnt = hb.result(k=0.5)
    dens = blur(cov, 4 * S)
    rimI = np.clip(rimw * np.clip(1 - dens, 0, 1) ** 1.3 * 1.6, 0, 1.2) * L
    behind = np.clip(1 - A, 0, 1)
    outer = smoothstep(.2, .9, rimw) * behind
    hair_col = np.stack([0.003 + rimI * (0.30 * outer + 0.05), 0.0015 + rimI * (0.07 * outer + 0.02), 0.004 + rimI * (0.30 * outer + 0.06)], -1)
    img = img * (1 - cov[..., None]) + hair_col * cov[..., None]
    # ---------- 鼻から 白い 息 ----------
    img = vapor(img, M, t, hs, seed)
    # ---------- 光る 目（寄ると 大きく・1 を こえると 光が あふれる） ----------
    a_ = math.atan2(hd[1], hd[0]) * 0.5 - 0.2
    du = ((xx - ex) * math.cos(a_) + (yy - ey) * math.sin(a_)) / (34 * S * hs)
    dv = (-(xx - ex) * math.sin(a_) + (yy - ey) * math.cos(a_)) / (21 * S * hs)
    alm = np.clip(1 - (np.abs(du) ** 1.7 + np.abs(dv) ** 2.1), 0, 1)
    sock = smoothstep(0, .12, alm)
    img = img * (1 - sock[..., None] * 0.85) + np.array([0.012, 0.001, 0.001]) * sock[..., None] * 0.85
    rr = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) / (S * hs)
    orb = smoothstep(0, .3, alm)
    gg = min(g, 1.0)
    glow = (np.array([6.0, 5.2, 4.0]) * np.exp(-(rr / 9) ** 2)[..., None] + np.array([4.0, 2.2, 0.5]) * np.exp(-(rr / 17) ** 2)[..., None]
            + np.array([2.2, 0.6, 0.08]) * np.exp(-((rr - 22) / 6) ** 2)[..., None]) * orb[..., None]
    halo = np.array([1.0, 0.25, 0.04]) * np.exp(-(rr / 34) ** 1.4)[..., None] + np.array([0.12, 0.02, 0.05]) * np.exp(-(rr / 110) ** 1.2)[..., None]
    flare = np.exp(-(((yy - ey) / (3.0 * S * max(hs, .6))) ** 2)) * np.exp(-(np.abs(xx - ex) / (90 * S * hs * (1 + 1.5 * max(0, g - 1)))) ** 1.3)
    img = img + (glow + halo) * (0.15 + 0.85 * gg) + flare[..., None] * np.array([1.6, 0.8, 0.35]) * gg * 0.6
    if g > 1:                                                                    # あふれる 光（十字の 筋・広い にじみ）
        over = g - 1
        rr2 = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2)
        star = (np.exp(-(np.abs(yy - ey) / (2.5 * S)) ** 1.2) * np.exp(-(np.abs(xx - ex) / (W * .45)) ** 1.1)
                + np.exp(-(np.abs(xx - ex) / (2.5 * S)) ** 1.2) * np.exp(-(np.abs(yy - ey) / (H * .25)) ** 1.1) * .6)
        img = img + star[..., None] * np.array([2.2, 1.0, 0.4]) * over * .8 + np.exp(-(rr2 / (W * (.08 + .25 * over))) ** 1.5)[..., None] * np.array([2.0, .7, .2]) * over
    # ---------- 火の粉（下から 上へ） ----------
    em = np.zeros((H, W), np.float32)
    for (sx_, sy_, sz, b_) in tx['emb']:
        x = (sx_ * W + 40 * S * math.sin(t * 1.3 + sy_ * 9)) % W
        y = (sy_ * H - t * 110 * S * (0.6 + b_)) % H
        cv2.circle(em, (int(x * 4), int(y * 4)), max(1, int(sz * S * 4)), float(b_), -1, cv2.LINE_AA, shift=2)
    em = blur(em, .8 * S) + blur(em, 4 * S) * .6
    img = img + em[..., None] * np.array([1.0, 0.35, 0.6]) * 0.35 * L * (1 - 0.8 * headm)[..., None]
    img = bloom(img, .9)
    out = finish(img * 2.2, seed + int(t * 100), vig=.55)
    # ---------- 2まい目の ような 青むらさきの 光（スクリーンで 重ねる・闇から ともる） ----------
    rx = (xx - W * .45) / (W * .62); ry = (yy - H * .38) / (H * .62)
    r_ = np.sqrt(rx ** 2 + ry ** 2)
    c0, c1, c2 = np.array([120, 170, 255]) / 255, np.array([30, 70, 255]) / 255, np.array([10, 30, 200]) / 255
    w1 = np.clip(r_ / .45, 0, 1)[..., None]
    w2 = np.clip((r_ - .45) / .55, 0, 1)[..., None]
    col = c0 * (1 - w1) + c1 * w1
    col = col * (1 - w2) + c2 * w2
    alp = (0.7 * (1 - w1[..., 0]) + 0.5 * w1[..., 0]) * (1 - w2[..., 0]) + 0.45 * w2[..., 0]
    out = out + (alp[..., None] * col) * (1 - out) * (0.72 * L)
    # ---------- おわり：目の 光が 画面を つつむ ----------
    fl = ss(F['RUSH'], FACE, t)
    if fl > 0:
        rr2 = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) / (W * (.15 + 1.4 * fl ** 1.5))
        wash = np.clip(np.exp(-rr2 ** 2) * fl ** .8 * 1.6, 0, 1)[..., None]
        wcol = np.array([1.0, .72, .45]) * (1 - fl) + np.array([1.0, .95, .88]) * fl
        out = out * (1 - wash) + wcol * wash
    return np.clip(out, 0, 1)


# ================================================================ B 蹄の カットイン
import shiden_hoof as SH

T_IN, (T_SLOW0, T_SLOW1), T_OUT = F['H_IN'], F['H_SLOW'], F['H_OUT']   # 蹄（場面の 中の 秒）：入る・まん中で ゆっくり・抜ける
T_OPEN = F['H_OPEN']                                          # 切り口が 開く
T_ZOOM = F['H_ZOOM']                                          # 切り口の 光へ 寄る
T_B = HOOF - FACE                                             # 場面の 長さ（2.4秒）
Y0 = 0.47                                                     # 切り口の 高さ（H の 割合）＝つま先の 高さ


def herm(u, p0, p1, m0, m1):
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * m1


def toe_x(tau):
    """つま先の 画面の x（W の 割合）：速く 入る → まん中で ゆっくり → 速く 抜ける"""
    segs = ((T_IN, T_SLOW0, -0.12, 0.36, 3.4, 0.55), (T_SLOW0, T_SLOW1, 0.36, 0.58, 0.55, 0.55), (T_SLOW1, T_OUT, 0.58, 1.75, 0.55, 9.0))
    if tau <= T_IN:
        return -0.12 - (T_IN - tau) * 3.4
    for a, b, p0, p1, v0, v1 in segs:
        if tau <= b:
            d = b - a
            return float(herm((tau - a) / d, p0, p1, v0 * d, v1 * d))
    return 1.75 + (tau - T_OUT) * 9.0


def toe_v(tau):
    return (toe_x(tau + 1e-3) - toe_x(tau - 1e-3)) / 2e-3


_TCUT = None


def cut_time(xs):
    """画面の x（px）を つま先が 通る 秒（通らない 所は 大きな 値）"""
    global _TCUT
    if _TCUT is None:
        ts = np.linspace(T_IN - .1, T_OUT + .1, 4000)
        _TCUT = (ts, np.array([toe_x(t) for t in ts]) * W)
    ts, xp = _TCUT
    return np.interp(xs, xp, ts, left=-1.0, right=99.0)


def world_time(tau):
    """まわりの 時間（蹄が まん中で ゆっくりの 間は まわりも ゆっくり＝スローモーション）"""
    k = np.linspace(0, tau, 120)
    sp = 1 - 0.72 * np.array([ss(T_SLOW0 - .08, T_SLOW0 + .05, x) * (1 - ss(T_SLOW1 - .05, T_SLOW1 + .1, x)) for x in k])
    return float(np.trapezoid(sp, k))


STORM = {}


def storm_tex(seed=211):
    """雷雲の もよう（つながる 512 の ノイズ・明るさの 立体の 陰も 先に 計算）"""
    if not STORM:
        rng = np.random.default_rng(seed)
        texs = []
        for k in range(4):
            wa = fbm(512, 512, 220, 4, seed=seed + 40 + k)
            wb = fbm(512, 512, 220, 4, seed=seed + 60 + k)
            base = fbm(1024, 1024, 300, 6, seed=seed + k)                # もくもくした 大きな 形（ゆがめて 使う）
            yy_, xx_ = np.mgrid[0:512, 0:512].astype(np.float32)
            mx = (xx_ * 2 + (wa - .5) * 260) % 1024
            my = (yy_ * 2 + (wb - .5) * 260) % 1024
            n = cv2.remap(base, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            n = 1 - np.abs(2 * ((n - n.min()) / (n.max() - n.min() + 1e-6)) - 1) ** 0.8   # ふくらんだ 雲（billow）
            n = (n - n.min()) / (n.max() - n.min() + 1e-6)
            det = fbm(512, 512, 110, 4, seed=seed + 80 + k)
            n = np.clip(n * .9 + (det - .5) * .18 + .05, 0, 1)
            n = cv2.GaussianBlur(n.astype(np.float32), (0, 0), 2.0)
            gx = cv2.Sobel(n, cv2.CV_32F, 1, 0, ksize=5) / 40
            gy = cv2.Sobel(n, cv2.CV_32F, 0, 1, ksize=5) / 40
            lit = np.clip(0.55 - gx * 0.9 - gy * 1.3, 0, 1.4)              # 左上からの 光の 陰（立体に 見える）
            texs.append((n.astype(np.float32), lit.astype(np.float32)))
        STORM['tex'] = texs
        spr = []
        for k in range(5):                                                     # もくもくの 雲の かたまり（右から 光が 当たる 絵：まわして 使う）
            N_ = 256
            yy_, xx_ = np.mgrid[0:N_, 0:N_].astype(np.float32)
            u_, v_ = (xx_ - N_ / 2) / (N_ / 2), (yy_ - N_ / 2) / (N_ / 2)
            det = fbm(N_, N_, 46, 5, seed=seed + 300 + k)
            det2 = fbm(N_, N_, 18, 3, seed=seed + 320 + k)
            r_ = np.sqrt(u_ ** 2 + v_ ** 2) * (1.0 + (det - .5) * .9 + (det2 - .5) * .25)
            dens = np.clip(1 - smoothstep(.45, 1.0, r_), 0, 1)
            dens = dens * (0.65 + 0.5 * det)
            gx = cv2.Sobel(cv2.GaussianBlur(dens, (0, 0), 3), cv2.CV_32F, 1, 0, ksize=5) / 60
            shade = np.clip(0.18 + 0.9 * smoothstep(-0.7, 0.9, u_ + (det - .5) * .8) - gx * 2.0, 0, 1.4)      # 右（光の 方）ほど 明るい
            rim = np.clip((1 - smoothstep(.15, .55, dens)) * smoothstep(-.1, .8, u_) * (dens > .02), 0, 1)     # 光の 方の うすい ふちが 光る
            spr.append(np.dstack([dens, shade, rim]).astype(np.float32))
        STORM['spr'] = spr
        PF = []
        for i in range(240):
            a_ = rng.uniform(0, 6.28); r2 = rng.uniform(.75, 2.6)
            PF.append(dict(x=math.cos(a_) * r2, y=math.sin(a_) * r2 * 1.15, z=rng.uniform(.3, 12), R=rng.uniform(.35, .95), k=int(rng.integers(0, 5)), sp=rng.uniform(-.4, .4)))
        STORM['puff'] = PF
        STORM['layers'] = [dict(z0=z, tex=k % 4, ox=rng.uniform(0, 512), oy=rng.uniform(0, 512), rot=rng.uniform(0, 6.28)) for k, z in enumerate(np.linspace(1.0, 9.0, 9))]
        P = []
        for i in range(520):                                                  # 雨と 光の 粒（3D：カメラの まわりの 筒）
            a = rng.uniform(0, 6.28); r = rng.uniform(.25, 2.6)
            P.append((math.cos(a) * r, math.sin(a) * r * 1.15, rng.uniform(.3, 12), rng.uniform(.4, 1.0), rng.random()))
        STORM['rain'] = P
        D = []
        for i in range(16):                                                   # とんでくる 岩の かけら
            a = rng.uniform(0, 6.28); r = rng.uniform(.55, 2.2)
            nv = rng.integers(5, 8)
            ang = np.sort(rng.uniform(0, 6.28, nv))
            rad = rng.uniform(.55, 1.0, nv)
            D.append(dict(x=math.cos(a) * r, y=math.sin(a) * r * 1.1, z=rng.uniform(1.5, 12), s=rng.uniform(.08, .22), poly=np.c_[np.cos(ang) * rad, np.sin(ang) * rad],
                          w=rng.uniform(-6, 6), ph=rng.uniform(0, 6.28)))
        STORM['deb'] = D
    return STORM


BOLTS = ((F['H_BOLTS'][0], (.18, .22), (.44, .05)), (F['H_BOLTS'][1], (.84, .12), (.6, .3)))   # 雷：秒・はじまりと おわり（画面の 割合）


def bolt_mask(rng, p0, p1, thick):
    """ジグザグの 雷（枝つき）→ 0〜1"""
    m = np.zeros((H, W), np.float32)

    def zig(a, b, depth, w):
        pts = [np.array(a, float), np.array(b, float)]
        for _ in range(6):
            nw = [pts[0]]
            for q0, q1 in zip(pts, pts[1:]):
                d = q1 - q0; L = np.linalg.norm(d) + 1e-6
                nrm2 = np.array([-d[1], d[0]]) / L
                nw += [(q0 + q1) / 2 + nrm2 * rng.normal(0, L * .18), q1]
            pts = nw
        P = np.round(np.array(pts) * 16).astype(np.int32)
        cv2.polylines(m, [P], False, 1.0, max(1, int(w)), cv2.LINE_AA, shift=4)
        if depth > 0:
            for _ in range(2):
                k = rng.integers(len(pts) // 4, len(pts) * 3 // 4)
                q = pts[k]; d = np.array(b) - np.array(a)
                ang = math.atan2(d[1], d[0]) + rng.choice((-1, 1)) * rng.uniform(.4, .9)
                L = np.linalg.norm(d) * rng.uniform(.25, .45)
                zig(q, q + np.array([math.cos(ang), math.sin(ang)]) * L, depth - 1, w * .6)
    zig((p0[0] * W, p0[1] * H), (p1[0] * W, p1[1] * H), 2, thick)
    return m


def zoom_blur(img, cx, cy, k, n=10):
    """まん中から 外への ぶれ（速さ）：(cx, cy) を 中心に 1 → 1+k 倍の 平均"""
    if k <= 1e-3:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        z = 1 + k * i / (n - 1)
        M = np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return acc / n


def storm(tau, seed=211):
    """雷雲の トンネルを 前へ 突き進む（暗い 雲の かべ・ふちが 光る・まん中の 遠い 光・雷・雨と 光の 粒・岩の かけら・外への ぶれ）→ 線形の 色"""
    st = storm_tex(seed)
    yy, xx = grid()
    wt = world_time(tau)
    cx, cy = W * .5, H * .44
    F = W * .9
    rr = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / W) ** 2)
    img = np.zeros((H, W, 3), np.float32) + np.array([0.0015, 0.001, 0.005])
    core = np.exp(-(rr / .05) ** 2)[..., None] * np.array([2.2, 1.6, 2.8]) + np.exp(-(rr / .16) ** 2)[..., None] * np.array([0.55, 0.16, 0.85]) + np.exp(-(rr / .45) ** 2)[..., None] * np.array([0.05, 0.012, 0.09])
    img = img + core
    # 雷（その 間だけ 雲を 照らす）
    lights = []
    bolts = np.zeros((H, W), np.float32)
    for (tb, p0, p1) in BOLTS:
        a = tau - tb
        if -0.001 < a < .22:
            inten = math.exp(-a / .06) * (1 if a < .05 else .7)
            bm = bolt_mask(np.random.default_rng(seed + int(tb * 100)), p0, p1, 3.2 * S)
            bolts = np.maximum(bolts, bm * inten)
            lights.append(((p0[0] + p1[0]) / 2 * W, (p0[1] + p1[1]) / 2 * H, inten))
    lightf = np.zeros((H, W), np.float32)
    for (lx, ly, li) in lights:
        lightf += np.exp(-(((xx - lx) / (W * .4)) ** 2 + ((yy - ly) / (W * .4)) ** 2)) * li
    # 雲の かたまり（3D の 筒の 中に ちらばる もくもく・遠く → 近く・まん中の 光の 方の 側が 明るく ふちが 光る）
    speed = 3.2
    puffs = []
    for P_ in st['puff']:
        z = (P_['z'] - wt * speed) % 12.0 + .3
        puffs.append((z, P_))
    for z, P_ in sorted(puffs, key=lambda q: -q[0]):
        pxc, pyc = cx + F * P_['x'] / z, cy + F * P_['y'] / z
        R_ = F * P_['R'] / z
        if R_ < 3 or not (-R_ < pxc < W + R_ and -R_ < pyc < H + R_):
            continue
        fade = smoothstep(.3, .9, z) * (1 - smoothstep(9.0, 12.0, z))
        if fade <= .01:
            continue
        sp_ = st['spr'][P_['k']]
        ang = math.atan2(cy - pyc, cx - pxc) + P_['sp']                     # 光（まん中）の 方へ 明るい 側を 向ける
        x0, x1 = int(max(0, pxc - R_)), int(min(W, pxc + R_ + 1))
        y0, y1 = int(max(0, pyc - R_)), int(min(H, pyc + R_ + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        sc2 = 256 / (2 * R_)
        cs, sn = math.cos(-ang), math.sin(-ang)
        # 画面 → 絵：p_spr = 128 + sc2 * Rot(-ang) * (p − c)
        Mi = np.float32([[sc2 * cs, -sc2 * sn, 128 - sc2 * (cs * (pxc - x0) - sn * (pyc - y0))],
                         [sc2 * sn, sc2 * cs, 128 - sc2 * (sn * (pxc - x0) + cs * (pyc - y0))]])
        reg = cv2.warpAffine(sp_, Mi, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT)
        dens, shade, rim = reg[..., 0], reg[..., 1], reg[..., 2]
        al = np.clip(dens * 1.4, 0, 1) * fade
        rrr = rr[y0:y1, x0:x1]
        cl = np.exp(-(rrr / (.30 + .06 * z)) ** 2) * 1.2 + .08
        haze = ss(2.5, 9.0, z)
        lf = lightf[y0:y1, x0:x1]
        col = (np.array([0.006, 0.0035, 0.015]) * (1 - haze) + np.array([0.05, 0.02, 0.09]) * haze)[None, None, :] \
            + (shade * cl)[..., None] * np.array([0.30, 0.09, 0.48]) * (1 - .4 * haze) \
            + (rim * cl)[..., None] * np.array([1.1, 0.35, 1.6]) \
            + ((shade + rim) * lf)[..., None] * np.array([1.4, 1.1, 2.0])
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - al[..., None]) + col * al[..., None]
    img = img + bolts[..., None] * np.array([3.0, 2.6, 4.0]) + blur(bolts, 6 * S)[..., None] * np.array([1.2, .5, 1.8])
    # 岩の かけら（回りながら 手前へ・まん中の 光の 方の ふちが 光る）
    for D in st['deb']:
        z = (D['z'] - wt * speed * 1.3) % 12.0 + .3
        if z < .35:
            continue
        cxp, cyp = cx + F * D['x'] / z, cy + F * D['y'] / z
        R_ = D['s'] * F / z * 1.6
        if not (-R_ < cxp < W + R_ and -R_ < cyp < H + R_) or R_ < 2:
            continue
        ang = D['ph'] + wt * D['w']
        cs, sn = math.cos(ang), math.sin(ang)
        pts = np.c_[D['poly'][:, 0] * cs - D['poly'][:, 1] * sn, (D['poly'][:, 0] * sn + D['poly'][:, 1] * cs) * (.6 + .4 * math.sin(ang * .7))] * R_ + (cxp, cyp)
        x0, x1 = int(max(0, cxp - R_ - 4)), int(min(W, cxp + R_ + 5))
        y0, y1 = int(max(0, cyp - R_ - 4)), int(min(H, cyp + R_ + 5))
        if x1 <= x0 or y1 <= y0:
            continue
        m = np.zeros((y1 - y0, x1 - x0), np.float32)
        P = np.round((pts - (x0, y0)) * 16).astype(np.int32)
        cv2.fillPoly(m, [P], 1.0, cv2.LINE_AA, shift=4)
        m = cv2.GaussianBlur(m, (0, 0), max(.6, R_ * .04))
        fog = 1 - smoothstep(5, 12, z)
        dirc = nrm(np.array([cx - cxp, cy - cyp]))
        side = np.clip(((xx[y0:y1, x0:x1] - cxp) * dirc[0] + (yy[y0:y1, x0:x1] - cyp) * dirc[1]) / (R_ + 1e-3) * 1.3, 0, 1)
        er = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8), iterations=max(1, int(R_ * .08))), 0, 1)
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - (m * fog)[..., None]) + (np.array([0.005, 0.0035, 0.011]) + side[..., None] * np.array([0.03, 0.012, 0.05]))[None] * (m * fog)[..., None] \
            + (er * side * fog)[..., None] * np.array([1.0, 0.4, 1.3])
    # 外への ぶれ（前へ 突き進む 速さ：スローモーションの 間は 弱く）
    spd = 1 - 0.72 * ss(T_SLOW0 - .08, T_SLOW0 + .05, tau) * (1 - ss(T_SLOW1 - .05, T_SLOW1 + .1, tau))
    img = zoom_blur(img, cx, cy, 0.10 * spd, 9)
    # 雨と 光の 粒（手前へ とぶ 長い 筋）
    ln = np.zeros((H, W), np.float32)
    lc = np.zeros((H, W), np.float32)
    for (x, y, z0, b, c) in st['rain']:
        z = (z0 - wt * speed * 1.6) % 12.0 + .2
        z1 = z + speed * 1.6 * spd / 20
        if z < .25:
            continue
        p = (cx + F * x / z, cy + F * y / z)
        q = (cx + F * x / z1, cy + F * y / z1)
        if not (-80 < p[0] < W + 80 and -80 < p[1] < H + 80):
            continue
        w = max(1, int(1.3 * S / z * 2))
        cv2.line(ln if c < .8 else lc, (int(q[0] * 16), int(q[1] * 16)), (int(p[0] * 16), int(p[1] * 16)), float(b * min(1, 2.0 / z)), w, cv2.LINE_AA, shift=4)
    img = img + ln[..., None] * np.array([0.5, 0.4, 0.95]) * .55 + lc[..., None] * np.array([2.4, 1.0, .35]) * .8
    return img


def hoof_layer(tau, prefix, seed=5):
    """3D の 蹄（場面の 秒 τ の 向き）→（線形の 色・前もって かけた, すき通し, 蹄鉄の 光, しるし）
       黒い 馬の 蹄：黒っぽい 角質（縦の すじ・つや）・焼けた 蹄鉄の 光で 下が だいだいに 照る・かんむりの 毛・うしろからの むらさきと 青の ふちの 光"""
    az = 34 - 18 * ss(T_IN, T_OUT, tau)
    el = 7 - 4 * ss(T_IN, T_OUT, tau)
    Wc, Hc = int(1300 * S), int(640 * S)
    tmp = Scene()
    K = SH.build(tmp)
    tgt = K['sole'] + np.array([-0.20, -0.035, 0.0])
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])
    cam = tgt + d * 1.24
    sc = Scene()
    sc.image(Wc, Hc, 1)
    sc.camera(cam, tgt, 12.6)
    sc.bounce(1)
    cd = nrm(cam - tgt)
    sc.env((0.010, 0.004, 0.018), (0.012, 0.005, 0.020), (0.004, 0.001, 0.006), (0.001, 0.0005, 0.002))
    sc.lobe(nrm(np.array([-0.2, 0.9, -0.4])), (0.6, 0.25, 0.7), 6.0)
    sc.lobe(nrm(np.array([0.2, -0.8, -0.3])), (0.15, 0.25, 0.8), 6.0)
    sc.lobe(nrm(cd + np.array([0.0, 0.5, 0.0])), (0.25, 0.22, 0.3), 10.0)
    sc.light(nrm(cd * 0.7 + np.array([-0.3, 0.9, 0.0])), (0.7, 0.65, 0.9), 10, 0)        # 前からは 弱く（黒い 蹄の まま）
    sc.light(nrm(-cd + np.array([0.0, 0.9, 0.0])), (2.6, 1.1, 3.0), 8, 0)                 # うしろ上から むらさき
    sc.light(nrm(-cd + np.array([0.3, -0.8, 0.0])), (0.9, 1.4, 3.4), 8, 0)                # うしろ下から 青
    sc.light(nrm(-cd + np.array([0.9, 0.2, 0.0])), (2.4, 1.8, 3.2), 8, 0)                 # 雷雲の 光（右うしろ）
    sc.plight(K['sole'] + np.array([0.06, 0.0, 0.02]), (0.06, 0.015, 0.003), 8, 0)       # 焼けた 蹄鉄の 光
    sc.mat(SH.M_COAT, 1, (0.010, 0.009, 0.011), 0.5, 0.8, 0.3, 4.0)
    sc.bump(SH.M_COAT, 4, 900.0, 0.00006, o=(0, 0, 0), ax=K['ax'], rx=(0, 0, 1), rad=0.2)
    sc.mat(SH.M_HOOF, 1, (0.035, 0.032, 0.034), 0.26, 0.6, 0.3, 3.0)
    sc.bump(SH.M_HOOF, 4, 300.0, 0.00011, o=(0, 0, 0), ax=K['e1'], rx=(0, 0, 1), rad=0.2)
    sc.mat(SH.M_BAND, 1, (0.17, 0.16, 0.155), 0.8, 0.3, 0.2, 3.0)
    sc.mat(SH.M_SHOE, 0, (0.62, 0.56, 0.56), 0.28)
    sc.mat(SH.M_SOLE, 1, (0.07, 0.062, 0.058), 0.6, 0.2, 0.1, 3.0)
    SH.build(sc)
    R = load_r(prefix, Wc, Hc, ('rgb', 'a', 'm'))                                          # 描いた 3D は とっておく（2D だけ 直す とき）
    if R is None:
        R = sc.render(prefix)
        drop_r(prefix, ('d', 'n', 'ao'))
    P = lambda pts: sc.project(np.atleast_2d(np.asarray(pts, float)))[0]
    Mk = {k: P(v).tolist() for k, v in K.items() if k not in ('ax', 'e1')}
    rgb, A, mid = R['rgb'], R['a'], R['m']
    yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
    s2 = Wc / 960.0
    shoe = cv2.GaussianBlur((np.abs(mid - SH.M_SHOE) < .5).astype(np.float32) * A, (0, 0), .6)
    rs = np.random.RandomState(seed)
    tex = cv2.resize(rs.rand(Hc // 18 + 2, Wc // 2).astype(np.float32), (Wc, Hc), interpolation=cv2.INTER_CUBIC)
    coat = (np.abs(mid - SH.M_COAT) < .5).astype(np.float32)
    lum = rgb.mean(-1)
    rgb = rgb * (1 + (tex - .5)[..., None] * 0.8 * (coat * smoothstep(0.004, 0.06, lum))[..., None])
    hoofm = (np.abs(mid - SH.M_HOOF) < .5).astype(np.float32)
    ax = np.array(Mk['crown'][0]) - np.array(Mk['toe'][0])
    big = int(math.hypot(Wc, Hc)) + 8
    t2 = cv2.resize(rs.rand(big // 7, big // 60 + 2).astype(np.float32), (big, big), interpolation=cv2.INTER_CUBIC)
    t2 = cv2.warpAffine(t2, cv2.getRotationMatrix2D((big / 2, big / 2), math.degrees(math.atan2(ax[1], ax[0])) - 90, 1.0), (big, big), borderMode=cv2.BORDER_REFLECT)
    t2 = t2[(big - Hc) // 2:(big - Hc) // 2 + Hc, (big - Wc) // 2:(big - Wc) // 2 + Wc]
    rgb = rgb * (1 + (t2 - .5)[..., None] * 0.45 * hoofm[..., None])
    hot = np.array([2.2, 0.45, 0.07])
    rgb = rgb * (1 - shoe[..., None] * .6) + shoe[..., None] * hot
    rng = np.random.default_rng(seed)
    hb = HairBuf(Hc, Wc, ss=2)
    ex, ey = Mk['ergot'][0]
    fx, fy = Mk['fet'][0]

    def flow(x, y, a_, t):
        return math.atan2(math.sin(math.pi - a_), math.cos(math.pi - a_)) * 0.10
    for i in range(26):                                                                   # 球節の うしろの 毛（なびく）
        p0 = np.array([ex + rng.normal(0, 8 * s2), ey + rng.normal(0, 10 * s2)])
        gp = guide(p0, math.pi + rng.normal(0.15, 0.25), rng.uniform(70, 150) * s2, 16, rng, flow, wave=rng.uniform(1, 2), phase=rng.uniform(0, 6) + tau * 8)
        hb.lock(gp, 18, rng, spread=4 * s2, clump=0.6, wmin=0.5 * s2, wmax=1.2 * s2, rimk=0.8)
    cov, rimw, cnt = hb.result(k=0.5)
    hair = np.stack([0.004 + rimw * 0.07, 0.004 + rimw * 0.06, 0.007 + rimw * 0.12], -1)
    img = rgb * (1 - cov[..., None]) + hair * cov[..., None]
    a_ = np.clip(A + cov, 0, 1)
    # かんむり（蹄の 上の ふち）の 短い 毛：蹄の かべに かかって 地面の 方へ（こちらを 向いた 側だけ）
    rng2 = np.random.default_rng(seed + 3)
    hc = HairBuf(Hc, Wc, ss=2)
    rc = SH.R0 - SH.HT * SH.TANA + 0.004
    e1, ax3, e2 = np.asarray(K['e1'], float), np.asarray(K['ax'], float), np.array([0, 0, 1.0])
    crown = np.asarray(K['crown'], float)

    def flat_flow(x, y, a__, t):
        return 0.0
    for i in range(600):
        ph = rng2.uniform(-math.pi, math.pi)
        nv = math.cos(ph) * e1 + math.sin(ph) * e2
        p0 = crown + rc * nv + ax3 * rng2.uniform(0.0, 0.012)
        L = rng2.uniform(0.006, 0.016)
        if np.dot(nv, cam - p0) < 0:
            continue
        q = P(np.array([p0, p0 - ax3 * L + nv * 0.004]))
        Ln = math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1])
        if Ln < 2:
            continue
        gp = guide(np.array(q[0], float), math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]) + rng2.normal(0, .12), Ln, 10, rng2, flat_flow, wave=rng2.uniform(.5, 1.2), phase=rng2.uniform(0, 6) + tau * 6)
        hc.lock(gp, 6, rng2, spread=2.2 * s2, clump=0.5, wmin=0.35 * s2, wmax=0.8 * s2, rimk=0.9)
    cov2, rim2, _ = hc.result(k=0.5)
    hair2 = np.stack([0.004 + rim2 * .06, 0.003 + rim2 * .03, 0.006 + rim2 * .078], -1)
    img = img * (1 - cov2[..., None]) + hair2 * cov2[..., None]
    a_ = np.clip(a_ + cov2, 0, 1)
    fade = smoothstep(fx - 470 * s2, fx - 120 * s2, xx)                    # 足の 左の はしは 闇へ
    img = img * fade[..., None]; a_ = a_ * fade
    glow = cv2.GaussianBlur(shoe, (0, 0), 3 * s2)[..., None] * np.array([1.0, 0.22, 0.05]) + cv2.GaussianBlur(shoe, (0, 0), 14 * s2)[..., None] * np.array([0.6, 0.08, 0.12])
    return img * a_[..., None], a_, glow, Mk


def place(layer, a, ox, oy):
    """キャンバスの 絵を 画面の (ox, oy) に 置く（はみ出しは 切る）"""
    hc, wc = a.shape
    out = np.zeros((H, W, layer.shape[2]), np.float32) if layer.ndim == 3 else np.zeros((H, W), np.float32)
    oa = np.zeros((H, W), np.float32)
    x0, y0 = int(round(ox)), int(round(oy))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    w = min(wc - sx0, W - dx0); h = min(hc - sy0, H - dy0)
    if w > 0 and h > 0:
        out[dy0:dy0 + h, dx0:dx0 + w] = layer[sy0:sy0 + h, sx0:sx0 + w]
        oa[dy0:dy0 + h, dx0:dx0 + w] = a[sy0:sy0 + h, sx0:sx0 + w]
    return out, oa


def hblur(img, L):
    """横の ぶれ（速さ）：長さ L px の 平均"""
    L = int(L)
    if L < 2:
        return img
    k = np.ones((1, L), np.float32) / L
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_CONSTANT)


TEAR = {}


def tear_line():
    """切り口の 形（x ごとの y・ギザギザ）と 開く 大きさの むら"""
    if not TEAR:
        rng = np.random.default_rng(77)
        xs = np.arange(W, dtype=np.float32)
        y = np.zeros(W, np.float32)
        x = 0
        cur = 0.0
        while x < W:
            step = int(rng.integers(int(6 * S) + 1, int(26 * S) + 2))
            nxt = float(np.clip(cur + rng.normal(0, 7 * S), -16 * S, 16 * S))
            y[x:x + step] = np.linspace(cur, nxt, len(y[x:x + step]))
            cur = nxt; x += step
        TEAR['y'] = Y0 * H + y
        o1 = cv2.GaussianBlur(rng.random((1, W)).astype(np.float32), (0, 0), 60 * S)[0]
        TEAR['open'] = np.clip(0.75 + (o1 - o1.mean()) / (o1.std() + 1e-6) * .18, .4, 1.3)          # 上下の 画面は かたい 板の まま ずれる（ゆるい むら だけ）
        def jag(seed_):
            r_ = np.random.default_rng(seed_)
            j = np.zeros(W, np.float32); x_ = 0
            while x_ < W:
                st_ = int(r_.integers(int(3 * S) + 1, int(14 * S) + 2))
                pk = r_.uniform(0, 1) ** 2.2
                j[x_:x_ + st_] = np.interp(np.arange(len(j[x_:x_ + st_])), [0, len(j[x_:x_ + st_]) / 2, len(j[x_:x_ + st_])], [0, pk, 0])
                x_ += st_
            return j
        TEAR['jt'], TEAR['jb'] = jag(91), jag(92)                              # 光の ふちの ギザギザ（上・下）
        TEAR['tx'] = cut_time(xs)
        sh = []
        for x0 in np.arange(4 * S, W, 15 * S):                                  # 割れて とぶ ガラスの かけら
            for sgn in (-1, 1):
                if rng.random() < .25:
                    continue
                nv = 3 if rng.random() < .6 else 4
                ang = np.sort(rng.uniform(0, 6.28, nv)); rad = rng.uniform(.5, 1.0, nv)
                sh.append(dict(x=float(x0 + rng.uniform(-5, 5) * S), sg=sgn, s=rng.uniform(9, 30) * S, vx=rng.uniform(-60, 160) * S, vy=sgn * rng.uniform(120, 480) * S,
                               w=rng.uniform(-9, 9), ph=rng.uniform(0, 6.28), poly=np.c_[np.cos(ang) * rad, np.sin(ang) * rad], life=rng.uniform(.5, .9), gr=rng.uniform(.6, 1.6)))
        TEAR['shards'] = sh
    return TEAR


def opening(tau):
    """x ごとの 切り口の 半分の 開き（px）"""
    T = tear_line()
    dt = tau - T['tx']
    crack = np.where(dt > 0, 1.2 * S + 2.6 * S * (1 - np.exp(-np.clip(dt, 0, None) / .07)), 0.0)
    big = (90 * S) * ss(T_OPEN, T_OPEN + .38, tau) ** 1.3 * T['open']
    return np.where(dt > 0, crack + big, 0.0).astype(np.float32)


def hoof_frame(tau, work, seed=5):
    """蹄の カットインの 1コマ（場面の 秒 τ）→ 0〜1 の sRGB"""
    yy, xx = grid()
    T = tear_line()
    bg = storm(tau)
    # ---------- 画面が 切れる（上は 上へ・下は 下へ ずれて、あいだから 光） ----------
    d = opening(tau)
    yt = T['y']
    above = yy < yt[None, :]
    mapy = np.where(above, yy + d[None, :], yy - d[None, :]).astype(np.float32)
    mapx = xx + np.where(above, -1, 1) * (d[None, :] * .08)
    torn = cv2.remap(bg, mapx.astype(np.float32), mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    jg = np.where(above, T['jt'][None, :], T['jb'][None, :]) * np.minimum(d[None, :] * .9, 26 * S)
    lim = d[None, :] + jg
    gap = np.abs(yy - yt[None, :]) / np.maximum(lim, 1e-3)
    inside = (gap < 1).astype(np.float32) * (d[None, :] > 0)
    inside = cv2.GaussianBlur(inside, (0, 0), .7)
    if 'flow' not in T:                                                         # 切り口の 中の 光の むら：蹄の 方へ 流れる（コマごとに ちらつかない）
        T['flow'] = fbm(64, 1400, 12, 4, seed=seed + 331)
    Mf = np.float32([[256.0 / W, 0, 900 - tau * 260], [0, 64.0 / H, 0]])
    fl = cv2.warpAffine(T['flow'], Mf, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    core = np.exp(-(np.clip(gap, 0, 3) * 1.6) ** 2)
    lc = (np.array([3.2, 2.8, 2.0]) * core[..., None] + np.array([2.4, 1.0, 0.25]) * (1 - core)[..., None]) * (0.85 + 0.3 * fl[..., None])
    img = torn * (1 - inside[..., None]) + lc * inside[..., None]
    glowm = blur(inside * (0.6 + 0.4 * fl), 5 * S)
    img = img + glowm[..., None] * np.array([2.0, 0.8, 0.25]) + blur(inside, 22 * S)[..., None] * np.array([0.9, 0.3, 0.35])
    # 光の 筋（開いた あと：切り口の 光が 上下へ あふれる＝切り口を 中心に 外へ ぶらす）
    op = ss(T_OPEN, T_OPEN + .4, tau)
    if op > 0:
        src = (inside * (0.6 + 0.6 * fl))[..., None] * np.array([1.8, 1.3, .7])
        rays = zoom_blur(src, W * .5, Y0 * H, 1.8 * op, 14)
        img = img + rays * 1.4 * op
    # ガラスの かけら（つま先が 通った 所から 割れて 上下へ・手前へ とぶ）
    for D in T['shards']:
        t0 = float(np.interp(D['x'], np.arange(W), T['tx']))
        a = tau - t0
        if not 0 < a < D['life']:
            continue
        k = a / D['life']
        sc_ = D['s'] * (1 + D['gr'] * k)
        cxp = D['x'] + D['vx'] * a
        y0 = float(np.interp(D['x'], np.arange(W), yt))
        cyp = y0 + D['vy'] * a + D['sg'] * 6 * S + 300 * S * a * a
        ang = D['ph'] + D['w'] * a
        cs, sn = math.cos(ang), math.sin(ang)
        pts = np.c_[D['poly'][:, 0] * cs - D['poly'][:, 1] * sn, D['poly'][:, 0] * sn + D['poly'][:, 1] * cs] * sc_ + (cxp, cyp)
        m = np.zeros((H, W), np.float32)
        P = np.round(pts * 16).astype(np.int32)
        cv2.fillPoly(m, [P], 1.0, cv2.LINE_AA, shift=4)
        al = (1 - ss(.65, 1, k)) * .95
        sx_, sy_ = int(np.clip(D['x'], 0, W - 1)), int(np.clip(y0 - D['sg'] * 20 * S, 0, H - 1))
        col = bg[sy_, sx_] * 1.6 + np.array([0.10, 0.06, 0.16])
        img = img * (1 - (m * al)[..., None]) + col * (m * al)[..., None]
        e = np.zeros((H, W), np.float32)
        cv2.polylines(e, [P], True, 1.0, max(1, int(1.2 * S)), cv2.LINE_AA, shift=4)
        gl = .5 + .5 * math.sin(ang * 2 + 1)
        img = img + (e * al)[..., None] * np.array([1.4, 1.1, 1.6]) * (0.4 + 1.2 * gl)
    # ---------- 3D の 蹄 ----------
    if T_IN - .05 <= tau <= T_OUT + .06:
        rd = os.path.join(work, '_r'); os.makedirs(rd, exist_ok=True)
        hl, ha, hg, Mk = hoof_layer(tau, os.path.join(rd, f'hoof2_{int(round(tau * FPS)):03d}'), seed)
        tx_, ty_ = Mk['toe'][0]
        ox, oy = toe_x(tau) * W - tx_, Y0 * H - ty_ + 4 * S
        L_ = abs(toe_v(tau)) * W / 60.0
        L2 = L_ * 1.0
        hl, ha, hg = hblur(hl, L2), hblur(ha, L2), hblur(hg, L2)
        pl_, pa = place(hl, ha, ox, oy)
        pg, _ = place(hg, ha, ox, oy)
        img = img * (1 - pa[..., None]) + pl_ + pg
        # 火花（つま先から うしろへ）
        if T_IN <= tau <= T_OUT:
            spk = np.zeros((H, W), np.float32)
            rngs = np.random.default_rng(seed + int(tau * 600))
            tx0 = toe_x(tau) * W
            for k in range(60):
                age = rngs.uniform(0, .28)
                tx_past = toe_x(max(T_IN, tau - age)) * W
                x0, y0 = tx_past, Y0 * H + 2 * S
                vx = -rngs.uniform(100, 900) * S; vy = rngs.uniform(-700, 400) * S
                x1 = x0 + vx * age; y1 = y0 + vy * age + 900 * S * age * age
                x2 = x1 - vx * .02; y2 = y1 - (vy + 1800 * S * age) * .02
                cv2.line(spk, (int(x2 * 16), int(y2 * 16)), (int(x1 * 16), int(y1 * 16)), float(1 - age / .28), max(1, int(1.6 * S)), cv2.LINE_AA, shift=4)
            img = img + spk[..., None] * np.array([3.0, 1.5, .5]) + blur(spk, 4 * S)[..., None] * np.array([1.2, .4, .1])
    # ---------- 寄る（切り口の 光へ）・ゆれ ----------
    zm = 1 + 4.0 * ss(T_ZOOM, T_B, tau) ** 2.2
    shake = 0.0
    for ti, amp in ((T_IN + .02, 7), (T_OPEN, 16)):
        a = tau - ti
        if a > 0:
            shake += amp * S * math.exp(-a / .14)
    sx = shake * math.sin(tau * 97); sy = shake * math.cos(tau * 83)
    if zm > 1.001 or shake > .3:
        cxz, cyz = W * .5, Y0 * H
        M = np.float32([[zm, 0, cxz - zm * cxz + sx], [0, zm, cyz - zm * cyz + sy]])
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    wash = ss(F['H_WASH'], T_B, tau)
    img = bloom(img, 1.0)
    out = finish(img * 1.6, seed + int(tau * 100), vig=.5, ca=.004)
    w0 = 1 - ss(0.0, 0.3, tau)                                                   # はじめ：目の 光の 白から（前の 場面と つながる）
    if w0 > 0:
        out = out * (1 - w0) + np.array([1.0, .95, .88]) * w0
    if wash > 0:
        out = out * (1 - wash) + np.array([1.0, .93, .78]) * wash
    return out


def render_hoof(work, i0, i1):
    a, b = int(round(FACE * FPS)), int(round(HOOF * FPS))
    for i in range(max(i0, a), min(i1, b)):
        if os.path.exists(frame_path(work, i)):
            continue
        tau = i / FPS - FACE
        save_png(hoof_frame(tau, work), frame_path(work, i))
        print('hoof', i, flush=True)


# ================================================================ C 光（深い 緑の 空間の 光の 玉と 金の 輪）
LIGHT = {}


def light_tex(seed=401):
    if not LIGHT:
        rng = np.random.default_rng(seed)
        LIGHT['fog'] = fbm(H, W * 2, 200 * S, 5, seed=seed)
        LIGHT['occ'] = fbm(256, 256, 18, 4, seed=seed + 1)
        LIGHT['plasma'] = fbm(512, 1024, 26, 6, seed=seed + 2)                       # 玉の 表面（経度 × 緯度）
        LIGHT['plasma2'] = fbm(512, 1024, 9, 4, seed=seed + 5)                      # 細かい つぶつぶ
        P = []
        for i in range(240):                                                  # 光の 玉へ 集まる 金の 粒（らせん）
            P.append(dict(a=rng.uniform(0, 6.28), r=rng.uniform(.35, 1.4), z=rng.uniform(-.6, .6), w=rng.uniform(.6, 1.6) * rng.choice((-1, 1)),
                          ph=rng.uniform(0, 1), b=rng.uniform(.4, 1.0), sz=rng.uniform(.6, 1.8)))
        LIGHT['pts'] = P
        LIGHT['bok'] = [(rng.uniform(-.1, 1.1), rng.uniform(-.1, 1.1), rng.uniform(18, 46), rng.uniform(.3, 1.0), rng.uniform(0, 6.28)) for _ in range(14)]   # 手前の ぼけた 光の 粒
        LIGHT['prom'] = [(rng.uniform(0, 6.28), rng.uniform(.25, .6), rng.uniform(.25, .7), rng.uniform(.5, 1.0), rng.uniform(0, 6.28)) for _ in range(9)]   # 玉の ふちから 立ちのぼる 光の アーチ
    return LIGHT


RINGS = ((1.65, 0.38, 70, .9, 0.0), (2.15, 0.62, -55, -.7, 1.3), (2.75, 0.22, 20, .5, 2.4), (5.6, 0.30, 8, .12, 0.0))   # 金の 輪：大きさ（玉の 何倍）・かたむき・向き（°）・回る 速さ・位相


def ring_pts(rad, tilt, rot, ph, cx, cy, n=360):
    """3D の 輪（玉の まわり）→ 画面の 点・奥（+）か 手前（−）か"""
    th = np.linspace(0, 2 * math.pi, n) + ph
    x, y, z = np.cos(th) * rad, np.zeros(n), np.sin(th) * rad
    ct, st_ = math.cos(tilt), math.sin(tilt)
    y, z = y * ct - z * st_, y * st_ + z * ct                       # 横の 軸で かたむける
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    x, y = x * cr - y * sr, x * sr + y * cr                         # 画面の 中で まわす
    return np.c_[cx + x, cy + y], z, th


def light_frame(lam, seed=401):
    """光の 場面（場面の 秒 λ：0〜1.2）→ 0〜1 の sRGB
       白熱の 光の 玉（まわる 表面の もよう・ふちの 光の アーチ）・3D の 金の 輪（奥は 玉の うしろ・手前は 前）・らせんで 集まる 金の 粒・緑の 光の 筋・手前の ぼけた 粒"""
    LT = light_tex(seed)
    yy, xx = grid()
    T_C = FILM - HOOF
    cx, cy = W * .5, H * .45
    zoom = 1 + .18 * lam + .25 * ss(.8, T_C, lam) ** 2
    ch = 1 + 2.6 * ss(F['L_CHARGE'], T_C, lam) ** 1.6                           # 光が 強く なる（ため）
    R0 = W * .085 * zoom * (1 + .25 * ss(.85, T_C, lam))
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    # ---------- 背景：深い 緑の 闇・光に 照らされた もや ----------
    img = np.zeros((H, W, 3), np.float32) + np.array([0.0012, 0.005, 0.0025])
    ox = int((lam * 60 * S) % W)
    fog = LT['fog'][:, ox:ox + W]
    lit = np.exp(-(rr / (W * .55 * zoom)) ** 1.3)
    img = img + (lit * (.3 + 1.0 * fog ** 1.5))[..., None] * np.array([0.018, 0.055, 0.02]) * ch ** .5
    # ---------- 光の 筋（もやの すきまから 外へ） ----------
    occ = cv2.resize(LT['occ'], (W, H))
    src = (np.exp(-(rr / (R0 * 1.7)) ** 2) * smoothstep(.5, .72, occ))[..., None] * np.array([1.0, 1.4, .5]) * ch
    rays = zoom_blur(src, cx, cy, 3.2, 18)
    img = img + rays * .42
    # ---------- 輪の 奥の 半分（玉の うしろ） ----------
    front = []

    def ring_draw(segs):
        rl = np.zeros((H, W), np.float32); rh = np.zeros((H, W), np.float32); rk = np.zeros((H, W), np.float32)
        for seg, gl, wid, dep in segs:
            cv2.polylines(rl, [seg], False, float((.35 + .65 * gl) * dep), wid, cv2.LINE_AA, shift=4)
            cv2.polylines(rh, [seg], False, float(gl ** 6 * dep), max(1, wid // 2), cv2.LINE_AA, shift=4)
            if gl > .985:                                                           # つやの いちばん 明るい 所：きらり
                cv2.circle(rk, (int(seg[1][0]), int(seg[1][1])), int(wid * 16 * .5), float(dep), -1, cv2.LINE_AA, shift=4)
        return rl, rh, rk

    def ring_add(img, rl, rh, rk):
        spk = blur(rk, 1.5 * S)
        star = zoom_blur(spk[..., None] * np.array([1.0, .9, .6]), cx, cy, .06, 6)
        return (img + rl[..., None] * np.array([1.9, 1.25, .38]) + rh[..., None] * np.array([3.4, 3.0, 2.0]) + blur(rl, 5 * S)[..., None] * np.array([.9, .7, .18])
                + blur(rl, 18 * S)[..., None] * np.array([.25, .2, .05]) + star * 6.0 + blur(rk, 6 * S)[..., None] * np.array([2.0, 1.6, .6]))
    back = []
    for (k, (rad, tilt, rot, spd, ph)) in enumerate(RINGS):
        pts, z, th = ring_pts(rad * R0, tilt + .15 * math.sin(lam * 1.3 + k), rot + lam * 12 * spd, ph + lam * spd * 2.2, cx, cy)
        wid = max(1, int((6.0 if k < 3 else 2.4) * S * zoom))
        for i in range(len(pts) - 1):
            seg = np.round(pts[i:i + 2] * 16).astype(np.int32)
            gl = .5 + .5 * math.cos(th[i] * 3 - lam * 5 + k)              # 金の つやが 輪を 走る
            dep = .55 + .45 * (1 - z[i] / (rad * R0 + 1e-6)) / 2             # 奥ほど 少し 暗い（3D）
            (back if z[i] > 0 else front).append((seg, gl, wid, dep))
    img = ring_add(img, *ring_draw(back))
    # ---------- 光の 玉（まわる 表面・ふちの 光・白熱の しん） ----------
    d = rr / R0
    inside = d < 1.0
    zz = np.sqrt(np.clip(1 - d ** 2, 0, 1))
    ux, uy = (xx - cx) / R0, (yy - cy) / R0
    rot_ = lam * .9                                                              # 玉が まわる（たての 軸）
    tl_ = .35                                                                    # 軸の かたむき
    x3 = ux * math.cos(rot_) + zz * math.sin(rot_)
    z3 = -ux * math.sin(rot_) + zz * math.cos(rot_)
    y3 = uy * math.cos(tl_) - z3 * math.sin(tl_)
    z3 = uy * math.sin(tl_) + z3 * math.cos(tl_)
    lon = (np.arctan2(x3, z3) / (2 * math.pi) + .5) * 1024
    lat = (np.arccos(np.clip(y3, -1, 1)) / math.pi) * 511
    pl = cv2.remap(LT['plasma'], lon.astype(np.float32), lat.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    pl2 = cv2.remap(LT['plasma2'], (lon * 1.0).astype(np.float32), lat.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    gran = smoothstep(.3, .78, pl * .7 + pl2 * .45)
    limb = zz ** .45                                                             # ふちほど 暗い（球に 見える）
    surf = inside[..., None] * (np.array([1.05, 1.15, .5]) * (.1 + 1.7 * gran ** 1.3)[..., None] * limb[..., None]
                                + np.array([.9, .9, .7]) * np.exp(-(d / .38) ** 2)[..., None] * .5)
    rim = np.exp(-((d - 1.0) / .05) ** 2)[..., None] * np.array([1.3, 1.7, .7])  # ふちの 光の 輪（大気）
    corona = np.exp(-np.clip(d - 1, 0, None) * 4.0)[..., None] * np.array([1.0, 1.5, .45]) * (d > .98)[..., None] + np.exp(-(d / 3.0) ** 1.3)[..., None] * np.array([.24, .38, .1])
    # ふちから 立ちのぼる 光の アーチ（ゆっくり 動く）
    pr = np.zeros((H, W), np.float32)
    for (a0, h_, w_, b_, ph_) in LT['prom']:
        a1 = a0 + lam * .4
        span = w_ * .6
        ts = np.linspace(0, 1, 40)
        hgt = 1 + h_ * np.sin(np.pi * ts) * (.8 + .2 * math.sin(lam * 3 + ph_))
        ang = a1 - span / 2 + span * ts
        P_ = np.c_[cx + np.cos(ang) * hgt * R0, cy + np.sin(ang) * hgt * R0]
        cv2.polylines(pr, [np.round(P_ * 16).astype(np.int32)], False, float(b_), max(1, int(2.2 * S * zoom)), cv2.LINE_AA, shift=4)
    pr = blur(pr, 1.2 * S) * (d > .96)
    disc = np.clip((1.0 - d) / (1.5 / R0) + .5, 0, 1)[..., None]                 # 玉は うしろ（光の 筋・奥の 輪）を かくす
    img = img * (1 - disc * .85) + surf * ch + (rim + corona) * ch + pr[..., None] * np.array([1.4, 1.8, .7]) * ch + blur(pr, 6 * S)[..., None] * np.array([.6, .9, .3]) * ch
    # ---------- 輪の 手前の 半分（玉の 前を 通る） ----------
    img = ring_add(img, *ring_draw(front))
    # ---------- 集まる 金の 粒（らせんを えがいて 玉へ） ----------
    pk = np.zeros((H, W), np.float32)
    for P_ in LT['pts']:
        u = (P_['ph'] + lam * .55) % 1.0
        r_ = P_['r'] * (1 - u) ** 1.4 + .05
        a = P_['a'] + P_['w'] * u * 4
        x = cx + math.cos(a) * r_ * W * .55 * zoom
        y = cy + math.sin(a) * r_ * W * .55 * zoom * .55 + P_['z'] * r_ * W * .3
        r2 = P_['r'] * (1 - max(0, u - .012)) ** 1.4 + .05
        a2 = P_['a'] + P_['w'] * max(0, u - .012) * 4
        x2 = cx + math.cos(a2) * r2 * W * .55 * zoom
        y2 = cy + math.sin(a2) * r2 * W * .55 * zoom * .55 + P_['z'] * r2 * W * .3
        cv2.line(pk, (int(x2 * 16), int(y2 * 16)), (int(x * 16), int(y * 16)), float(P_['b'] * (.3 + .7 * u) * .7), max(1, int(P_['sz'] * S * 1.2)), cv2.LINE_AA, shift=4)
        cv2.circle(pk, (int(x * 16), int(y * 16)), max(1, int(P_['sz'] * S * 1.3 * 16)), float(P_['b'] * (.4 + .6 * u)), -1, cv2.LINE_AA, shift=4)
    img = img + pk[..., None] * np.array([2.2, 1.9, .7]) + blur(pk, 3 * S)[..., None] * np.array([1.0, .85, .25])
    # ---------- 横の 光の 筋（レンズ）・十字 ----------
    streak = np.exp(-(np.abs(yy - cy) / (2.6 * S * zoom)) ** 1.2) * np.exp(-(np.abs(xx - cx) / (W * .6)) ** 1.4)
    streak2 = np.exp(-(np.abs(yy - cy) / (14 * S * zoom)) ** 1.5) * np.exp(-(np.abs(xx - cx) / (W * .45)) ** 1.6)
    lens = 1 - .75 * disc * (1 - ss(F['L_CHARGE'], T_C, lam))                  # 玉の 上の レンズの 筋は うすく（玉の もようが 見える）
    img = img + (streak[..., None] * np.array([1.4, 1.7, 1.0]) + streak2[..., None] * np.array([.25, .45, .15])) * ch * lens
    vstreak = np.exp(-(np.abs(xx - cx) / (2.0 * S * zoom)) ** 1.2) * np.exp(-(np.abs(yy - cy) / (H * .07)) ** 1.4)
    img = img + vstreak[..., None] * np.array([1.0, 1.2, .6]) * ch * .35 * lens
    # ---------- 手前の ぼけた 光の 粒（奥行き） ----------
    bk = np.zeros((H, W), np.float32)
    for (bx, by, br, bb, ph_) in LT['bok']:
        x = (bx * W + lam * 40 * S * math.cos(ph_)) ; y = (by * H - lam * 70 * S)
        cv2.circle(bk, (int(x * 4), int(y * 4)), int(br * S * zoom * 4), float(bb * (.6 + .4 * math.sin(lam * 4 + ph_))), -1, cv2.LINE_AA, shift=2)
    bk = blur(bk, 3 * S)
    img = img + bk[..., None] * np.array([.06, .10, .03]) * (.6 + .4 * ch)
    img = bloom(img, 1.0)
    out = finish(img * .85, seed + int(lam * 100), vig=.6, ca=.003)
    # はじめ：白い 光から（前の 場面の おわりと つながる）・おわり：光が 画面を うめる
    w0 = 1 - ss(0.0, 0.28, lam)
    if w0 > 0:
        out = out * (1 - w0) + np.array([1.0, .93, .78]) * w0
    w1 = ss(F['L_WASH'], T_C, lam) ** 1.5
    if w1 > 0:
        rr2 = rr / (W * (.2 + 1.4 * w1))
        wash = np.clip(np.exp(-rr2 ** 2) * 1.5 * w1 + w1 * .5, 0, 1)[..., None]
        out = out * (1 - wash) + np.array([1.0, .97, .82]) * wash
    return np.clip(out, 0, 1)


def render_light(work, i0, i1):
    a, b = int(round(HOOF * FPS)), NF
    for i in range(max(i0, a), min(i1, b)):
        if os.path.exists(frame_path(work, i)):
            continue
        lam = i / FPS - HOOF
        save_png(light_frame(lam), frame_path(work, i))
        print('light', i, flush=True)


# ================================================================ 書く
def load_r(prefix, W_, H_, keys):
    """とっておいた 3D の 絵（keys だけ）。ない・こわれて いる → None"""
    ch = dict(rgb=3, n=3)
    out = {}
    for k in keys:
        f = f'{prefix}_{k}.f32'
        c = ch.get(k, 1)
        if not os.path.exists(f) or os.path.getsize(f) != W_ * H_ * c * 4:
            return None
        a = np.fromfile(f, np.float32)
        out[k] = a.reshape(H_, W_, c) if c > 1 else a.reshape(H_, W_)
    return out


def drop_r(prefix, keys):
    for k in keys:
        try:
            os.remove(f'{prefix}_{k}.f32')
        except OSError:
            pass


def frame_path(work, i):
    return os.path.join(work, f'f{i:03d}.png')


def render_face(work, i0, i1):
    """顔の コマ（3D は 2コマに 1回：あいだの コマは となりの 2つを まぜる）"""
    rd = os.path.join(work, '_r'); os.makedirs(rd, exist_ok=True)
    cache = {}

    def R_of(j):
        if j in cache:
            return cache[j]
        tj = j / FPS
        pre = os.path.join(rd, f'face{j:03d}')
        R = load_r(pre, W, H, ('rgb', 'a'))
        if R is None:
            R = face_render(face_state(tj), pre)
            drop_r(pre, ('d', 'n', 'm', 'ao'))                                         # 使わない ものは 消す（場所を とる）
        cache[j] = R
        for k in list(cache):
            if k < j - 4:
                del cache[k]
                drop_r(os.path.join(rd, f'face{k:03d}'), ('rgb', 'a'))
        return R
    nface = int(round(FACE * FPS))
    for i in range(i0, min(i1, nface)):
        if os.path.exists(frame_path(work, i)):
            continue
        t = i / FPS
        if i % 2 == 0 or i + 1 >= nface:
            R = R_of(i)
        else:
            Ra, Rb = R_of(i - 1), R_of(i + 1)
            R = dict(rgb=(Ra['rgb'] + Rb['rgb']) * .5, a=(Ra['a'] + Rb['a']) * .5)
        M = face_marks(face_state(t))
        img = face_frame(t, R, M)
        save_png(img, frame_path(work, i))
        print('face', i, flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--encode':
        work, out = sys.argv[2], sys.argv[3]
        import subprocess
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(work, 'f%03d.png'),
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an', out], check=True)
        print(out, os.path.getsize(out))
    else:
        work = sys.argv[1]; os.makedirs(work, exist_ok=True)
        i0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        i1 = int(sys.argv[3]) if len(sys.argv) > 3 else NF
        render_face(work, i0, i1)
        render_hoof(work, i0, i1)
        render_light(work, i0, i1)
