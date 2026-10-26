"""紫電（第4.71版・第4.72版）：押した 瞬間から 1コマずつ 3D で 描いた 動画（sd_film.mp4・30コマ/秒・音なし）
   第4.70版・まさちゃん「…馬の顔のシーンもっと長くていい！ 動き方は任せる！ … 求めているのは、全部二枚目の写真のようなリアルなエフェクトにしてほしい！」
   第4.71版・まさちゃん「ど！的中演出のプチュン演出をボタンタップした瞬間に入るようにして！ プチュンして0.8秒で、一枚目の馬の顔が暗闇から目だけを光らせて、
   徐々に顔がみえる、暗闇から目が光り顔が全部見えて(今の馬の顔の演出と繋げて)、蹄カットインに入るまでを2秒くらいにして！ 二枚目の蹄カットインの入りの映像を1.3秒にして、
   奥の光りから、的中(縦文字で)が画面近くまで飛んできて、0.8秒停止、すぐに蹄カットインで的中の文字を的と中の真ん中から切り裂いて、画面が光りに包まれてど！！！的中が出てくる。
   ど！！！的中表示2.5秒にして！」
   第4.72版・まさちゃん「…目が光ってから1秒ほど、少し光りが揺らいで！ …的中は出てきた時に！もっと派手なエフェクト追加して！ デーーーん！…
   蹄カットインは、もっと画面を切り裂いてるような演出に…的中(縦の文字)も切り裂かれてる演出で… ど！！！的中、の時よりも遥かに激しい演出にして！
   文字を大きく振動させたり、色と大きさが違う、ど！！！的中を細切れで入れてド派手な演出にしたり！」「…切り裂いた箇所に細かく砕けるガラスの演出と、
   …蹄が通った箇所を黒と紫の細かい雷が不定期に切り裂かれた切り口に纏ってる演出も… 蹄にも同様に黒と紫の細かい雷を纏わせて！」（ほかの ことばは shiden.py）
   → どの 場面も 3D で 光と つやまで 計算した 絵：
     はじめの 黒（0〜BLACK 秒）：押した 瞬間の プチュン（CSS：shiden.py）の 下・プチュンの あと 真っ暗 0.8秒
     A 馬の 顔（BLACK〜FACE 秒）：暗闇に 目だけが 光る（約1秒 光が ゆらぐ）→ だんだん 青むらさきの 光で 顔が 見えて くる → 頭が 上がって こちらを 向き・耳が 立ち・鼻から 白い 息・
       たてがみが なびく → 目の 火が 強く なって あふれる → カメラが 目へ 寄って 目の 光が 画面を つつむ
     B 蹄の カットイン（FACE〜HOOF 秒）：むらさきの 雷雲の 中を 前へ 突き進む（雲の 層・雷・火の粉・とんでくる かけら）・奥の 光から 縦書きの 3D の「的中」
       （flat/shiden_logo.py）が 画面の 近くまで とんでくる → デーン（白い 光・後光・衝撃の 輪・火花・字に 雷）→ 0.8秒 止まる → 焼けた 蹄鉄の 蹄
       （黒と 紫の 雷を まとう）が 左から 画面を 右上がりに 斜めに 切り裂いて 右へ（「的」と「中」の あいだの まん中を 通って 字も 切る・まん中で ゆっくり）
       → 通った 所から 画面の ガラスが 細かく 割れて（光る 割れ目・かけらごとに ずれる）細かい かけらが とぶ・切り口の ふちに 黒と 紫の 細かい 雷が 不定期に まとう
       → 切り口が 光って 開き（上と 下が 切り口に そって ずれる）光が あふれ 画面が 光に つつまれる
     D ど！！！的中（HOOF〜FILM 秒）：光の 中から 白熱の 3D の ロゴ（flat/shiden_logo.py）が 手前へ とんでくる → ドンッ（大きく 振動・金の かけら・衝撃の 輪）
       → 金と 虹に 冷める → 色と 大きさの ちがう ど！！！的中の 細切れ 6つ（赤・青・緑・銀・紫・金の 寄り：背景も カットごとに ちがう）
       → 本物が もう一度 ドドーン（白熱で たたきつけて 振動）→ 雷を まとう・大きな 雷 →（ボードは CSS）
   python3 flat/shiden_film.py <作業フォルダ> [はじめの コマ] [おわりの コマ]   （コマ f%03d.png。SCALE=0.5 で ためしの 小さい 絵）
   python3 flat/shiden_film.py --encode <作業フォルダ> <出力.mp4>
   python3 flat/shiden_film.py --last <作業フォルダ> <出力.webp>          （さいごの 1まい＝sd_last.webp）"""
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

import shiden as SDM                             # 時刻の きまり（shiden.py の FILM：音・CSS と そろえる）
F = SDM.FILM
FPS = F['FPS']                                   # 30コマ/秒
BLACK, FACE, HOOF, FILM = F['BLACK'], F['FACE'], F['HOOF'], F['END']   # 区切りの 秒（黒 1.8・A 顔 3.8・B 蹄 7.4・D ど！！！的中 10.5）
NF = int(round(FILM * FPS))                      # 315コマ
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
FACE_LEN = FACE - BLACK                          # 顔の 場面の 長さ（2.0秒）。この 場面の 秒は BLACK からの 秒
FACE_KEYS = [  # 秒: 頭の 角度・耳・カメラ（横から まわる u・上下 v・距離）・目の 画面の 場所（第4.70版の 4秒の 動きを 2秒に）
    (0.0, dict(ha=-45, ear=-16, u=.08, v=.07, dist=2.8, ex=.53, ey=.36)),
    (0.55, dict(ha=-41, ear=-6, u=.15, v=.06, dist=2.45, ex=.52, ey=.36)),
    (1.1, dict(ha=-32, ear=12, u=.31, v=.03, dist=2.0, ex=.49, ey=.36)),
    (1.5, dict(ha=-27, ear=22, u=.42, v=.0, dist=1.62, ex=.47, ey=.36)),
    (1.78, dict(ha=-25, ear=24, u=.46, v=-.01, dist=1.12, ex=.47, ey=.38)),
    (2.0, dict(ha=-24, ear=25, u=.48, v=-.02, dist=0.72, ex=.48, ey=.41)),
]
PUFFS = F['PUFFS']                               # 鼻から 白い 息（秒）


def face_state(t):
    d = {k: float(spline(t, [(a, b[k]) for a, b in FACE_KEYS])) for k in FACE_KEYS[0][1]}
    e0, (e1, e2) = F['EYE_ON'], F['EYE']
    d['g'] = max(0.0, float(spline(t, [(0, 0.0), (e0 * .6, .9), (e0 + .1, .62), (e1, .8), (e2, 1.15), (1.78, 1.7), (FACE_LEN, 3.0)])))   # 目の 光：暗闇で まず 目だけ ともる（1 を こえると あふれる）
    d['L'] = ss(F['LIT'][0], F['LIT'][1], t)                                                               # 顔を 照らす 光が だんだん ともる（暗闇から 浮かぶ）
    # 第4.72版：目が 光って から 約1秒 光が ゆらぐ（炎の ように 明るさと 大きさが ゆれる：まさちゃん「目が光ってから1秒ほど、少し光りが揺らいで！」）
    a = t - e0
    wv = 0.0
    if 0 <= a < F['EYE_WAVER'] + .3:
        amp = .24 * ss(0, .1, a) * (1 - ss(F['EYE_WAVER'] - .2, F['EYE_WAVER'] + .3, a))
        wv = amp * (.55 * math.sin(2 * math.pi * 6.3 * t + 1.1) + .3 * math.sin(2 * math.pi * 10.9 * t + 2.4) + .25 * math.sin(2 * math.pi * 3.7 * t + .3))
    d['g'] *= 1 + wv
    d['wv'] = wv
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
    k = 0.03 + 0.97 * L                                                          # はじめは 暗闇（目の 光だけ）
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
    hs = hl / (817 * S)                                                          # 頭の 大きさ（寄ると 大きく：1.5秒で 1）
    hd = (mz - np.array([ex, ey])) / (hl + 1e-6)
    # ---------- 背景（ゆっくり 流れる もや・頭の うしろの 光・右上の 桃色・左下の 青） ----------
    ty = (yy / H)[..., None]
    bg = (np.array([0.004, 0.0015, 0.009]) * (1 - ty) + np.array([0.0015, 0.0008, 0.004]) * ty) * (0.1 + 0.9 * L)    # はじめは まっ暗（目の 光だけ）
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
    wv = st.get('wv', 0.0)                                                      # 第4.72版：光の ゆらぎ（大きさと 位置も 少し ゆれる）
    exw, eyw = ex + 1.6 * S * hs * math.sin(t * 23.0) * abs(wv) * 4, ey - 1.2 * S * hs * math.cos(t * 17.0) * abs(wv) * 4
    rr = np.sqrt((xx - exw) ** 2 + (yy - eyw) ** 2) / (S * hs * (1 + .45 * wv))
    orb = smoothstep(0, .3, alm)
    gg = min(g, 1.0)
    glow = (np.array([6.0, 5.2, 4.0]) * np.exp(-(rr / 9) ** 2)[..., None] + np.array([4.0, 2.2, 0.5]) * np.exp(-(rr / 17) ** 2)[..., None]
            + np.array([2.2, 0.6, 0.08]) * np.exp(-((rr - 22) / 6) ** 2)[..., None]) * orb[..., None]
    halo = np.array([1.0, 0.25, 0.04]) * np.exp(-(rr / 34) ** 1.4)[..., None] + np.array([0.12, 0.02, 0.05]) * np.exp(-(rr / 110) ** 1.2)[..., None]
    flare = np.exp(-(((yy - ey) / (3.0 * S * max(hs, .6))) ** 2)) * np.exp(-(np.abs(xx - ex) / (90 * S * hs * (1 + 1.5 * max(0, g - 1)))) ** 1.3)
    img = img + (glow + halo) * (0.15 * min(1.0, gg / .3) + 0.85 * gg) + flare[..., None] * np.array([1.6, 0.8, 0.35]) * gg * 0.6
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
    fl = ss(F['RUSH'], FACE_LEN, t)
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
T_B = HOOF - FACE                                             # 場面の 長さ（3.6秒）
T_FLY0, T_FLY1 = F['T_FLY']                                   # 縦書きの 的中が 奥の 光から とんでくる・止まる（〜蹄）
H_SHIFT = F['H_SHIFT'] / FPS                                  # 蹄の 3D（第4.70版と 同じ 動き）を おそく した 秒（とっておいた 3D の 名前に 使う）
Y0 = 0.47                                                     # 切り口の 高さ（H の 割合）＝つま先の 高さ（画面の まん中で）
ANG = math.radians(F['SLASH'])                                # 第4.72版：切り口は 右上がりに 斜め（的と 中の あいだの まん中を 通って 字も 切る）
TANG = math.tan(ANG)


def line_y(x):
    """切り口の 線の 高さ（px）：画面の まん中（的と 中の あいだ）を 通って 右上がり"""
    return Y0 * H - TANG * (np.asarray(x, np.float64) - W * .5)


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


def world_speed(x):
    """まわりの 速さ：的中が 止まって いる 間は ゆっくり（0.4）・蹄が まん中の 間は もっと ゆっくり（0.28＝スローモーション）"""
    hold = ss(T_FLY1 - .1, T_FLY1 + .12, x) * (1 - ss(T_SLOW1 - .05, T_SLOW1 + .15, x))
    slow = ss(T_SLOW0 - .08, T_SLOW0 + .05, x) * (1 - ss(T_SLOW1 - .05, T_SLOW1 + .1, x))
    return 1 - .6 * hold - .12 * slow


def world_time(tau):
    """まわりの 時間（速さ world_speed を 足した もの）"""
    k = np.linspace(0, tau, 160)
    return float(np.trapezoid(np.array([world_speed(x) for x in k]), k))


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
            dens = dens * (0.65 + 0.5 * det) * (1 - smoothstep(.72, .97, np.sqrt(u_ ** 2 + v_ ** 2)))   # 絵の 四角の ふちでは 0（第4.71版：ゆっくりの 間に 雲の 切れめの たての 線が 見えないように）
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


# ---------------- 縦書きの 3D の 的中（flat/shiden_logo.py の 字の しくみ）
import shiden_logo as SL

_CDIR = nrm(np.array(SL.CAM_DIR, float))
TITLE = {}
S0T = .045                                                     # とびはじめの 大きさ（とまった 時を 1）
ROT0T = (10.0, -34.0, 7.0)                                     # とびはじめの 向き（度）


def title_setup():
    """縦書きの 的中の 置き場所・虹の 上下・とびはじめの 場所（奥の 光の まん中に 見える 所）"""
    if 'lay' not in TITLE:
        TITLE['lay'] = lay = SL.title_layout(TITLE['cache'])
        ys = [b[1] for _, b in lay] + [b[3] for _, b in lay]
        TITLE['hy'] = ((SL.ORIGIN[1] - min(ys)) / 100, (SL.ORIGIN[1] - max(ys)) / 100)
        cl = np.array([0.0, (SL.ORIGIN[1] - SL.TITLE_Y) / 100, 0.0])                        # 的と 中の あいだ（ロゴの 中）
        D0 = SL.CAM_DIST * (1 / S0T - 1)
        cam = SL.camera()
        eye, tgt, fov = cam
        fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
        th = math.tan(math.radians(fov) / 2); asp = W / H
        px, py = W * .5, H * .44                                                             # 雷雲の トンネルの 奥の 光（storm の まん中）
        rd = nrm(fw + rt * ((2 * px / W - 1) * th * asp) + up * ((1 - 2 * py / H) * th))
        R0 = SL.rot_xyz(*ROT0T)
        z = (-_CDIR * D0 + R0 @ cl - eye) @ fw                                               # その 奥行きで 光の まん中を 通る 点
        Pc = eye + rd * (z / (rd @ fw))
        TITLE['pos0'] = Pc - R0 @ cl
        TITLE['D0'] = D0
    return TITLE


def title_pose(tau):
    """場面の 秒 τ → 的中の 向き（度）・場所。まだ 出ない → None
       第4.72版：奥の 光から だんだん 速く とんできて 画面の 近くで「デーーン!!」と たたきつけて 止まる（少し 手前へ 出て もどる・うなずく）"""
    if tau < T_FLY0:
        return None
    T = title_setup()
    u = min(1.0, (tau - T_FLY0) / (T_FLY1 - T_FLY0))
    e = u ** 1.5
    s = S0T ** (1 - e)
    rr = (1 - u) ** 1.5
    rot = tuple(r * rr for r in ROT0T)
    a = tau - T_FLY1
    if a >= 0:
        s = 1 + .09 * math.sin(math.pi * a / .1) * math.exp(-a / .08)
        rot = (3.0 * math.sin(math.pi * a / .12) * math.exp(-a / .1), 0.0, 0.0)
    D = SL.CAM_DIST * (1 / s - 1)
    pos = -_CDIR * D + (T['pos0'] + _CDIR * T['D0']) * (D / T['D0'])
    return rot, pos, u


def title_light(tau):
    """的中に 映る 光：雷雲の むらさき（左右）・うしろの 光・雷（その 間だけ）・止まって いる 間に 光の 筋が 走る"""
    fl = [(nrm(np.array([-.92, .2, .3])), np.array([1.0, .35, 1.9]) * .55), (nrm(np.array([.9, .3, .3])), np.array([.8, .35, 1.8]) * .5),
          (nrm(np.array([0, -.95, .3])), np.array([.5, .2, 1.2]) * .4)]
    for (tb, p0, p1) in BOLTS:
        a = tau - tb
        if -0.001 < a < .22:
            d2 = np.array([(p0[0] + p1[0]) / 2 - .5, (p0[1] + p1[1]) / 2 - .44])
            fl.append((nrm(np.array([d2[0], -d2[1], .35])), np.array([1.6, 1.3, 2.6]) * 2.2 * math.exp(-a / .06)))
    sw = None
    if T_FLY1 + .12 <= tau <= T_FLY1 + .7:
        sw = -46 + 72 * ss(0, 1, (tau - T_FLY1 - .12) / .58)
    return fl, sw


def title_layer(tau, work):
    """縦書きの 的中の 1まい（色・すき通し・箱）。止まって からは 形を 1回だけ 描いて 光だけ 計算し直す"""
    TITLE.setdefault('cache', os.path.join(work, '_logo'))
    os.makedirs(TITLE['cache'], exist_ok=True)
    pz = title_pose(tau)
    if pz is None:
        return None
    rot, pos, u = pz
    T = title_setup()
    rd_ = os.path.join(work, '_r'); os.makedirs(rd_, exist_ok=True)
    heat = 1 - ss(T_FLY0 + .1, T_FLY0 + .8, tau)                                             # 光の 中から 出る ときは 白熱
    a = tau - T_FLY1
    if a >= 0:
        heat = max(heat, .85 * math.exp(-a / .09))                                           # デーン：たたきつけた 瞬間 字が 白く 光って すぐ 冷める
    fl, sw = title_light(tau)
    if a >= .45:                                                                             # 止まって 動かない 間は 形を 1回だけ 描く
        if 'rest' not in T:
            T['rest'] = SL.render(os.path.join(rd_, 'title_rest'), W, H, (0.0, 0.0, 0.0), np.zeros(3), T['cache'], layout=T['lay'])
        g = T['rest']
        rot, pos = (0.0, 0.0, 0.0), np.zeros(3)
    else:
        g = SL.render(os.path.join(rd_, f'title_{int(round(tau * FPS)):03d}'), W, H, rot, pos, T['cache'], layout=T['lay'])
    if g[0] is None:
        return None
    return SL.layer(None, W, H, rot, pos, sweep=sw, flash=fl, heat=heat, hit_y=T['hy'], gbuf=g)


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
    # 外への ぶれ（前へ 突き進む 速さ：止まって いる 間・スローモーションの 間は 弱く）
    spd = world_speed(tau)
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
        TEAR['y'] = (line_y(xs) + y * .2).astype(np.float32)                  # 第4.72版：右上がりの まっすぐな 刃の 切り口（ギザギザは 小さく）
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


TFX = {}


def title_rays(tau):
    """デーン（第4.72版）：たたきつけた 瞬間から 的中の うしろに 金と 白の 光の 筋（後光）と まん中の 光 → 蹄が 来る ころに ひく（線形の 色・なし → None）"""
    a = tau - T_FLY1
    fade = 1 - ss(T_IN - .15, T_IN + .15, tau)
    if a < 0 or fade <= 0:
        return None
    if 'th' not in TFX:
        yy, xx = grid()
        dx, dy = xx - W * .5, yy - Y0 * H
        TFX['th'] = np.arctan2(dy, dx).astype(np.float32)
        TFX['r'] = (np.sqrt(dx ** 2 + dy ** 2) / W).astype(np.float32)
    th, r = TFX['th'], TFX['r']
    k = (2.4 * math.exp(-a / .12) + .55) * fade
    rays = (.5 + .5 * np.cos(14 * th + .5 * a)) ** 10 + .7 * (.5 + .5 * np.cos(9 * th - .35 * a + 1.3)) ** 14
    img = (rays * np.exp(-r / .6) * smoothstep(.06, .3, r) * k)[..., None] * np.array([1.6, 1.15, .6], np.float32)
    img = img + (np.exp(-(r / .22) ** 2) * (2.0 * math.exp(-a / .15) + .35) * fade)[..., None] * np.array([1.5, 1.2, 1.0], np.float32)
    return img


def title_ring(img, tau):
    """デーン：衝撃の 輪（うしろの 景色を ゆがめる・ふちが 光る）"""
    a = tau - T_FLY1
    if not 0 <= a < .6:
        return img
    yy, xx = grid()
    cx, cy = W * .5, Y0 * H
    r_px = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    rs = W * (.15 + 1.5 * (1 - math.exp(-a / .2)))
    st_ = math.exp(-a / .17)
    bump = np.exp(-((r_px - rs) / (36 * S)) ** 2) * st_
    sc_ = 1 - 28 * S * bump / np.maximum(r_px, 1)
    img = cv2.remap(img, (cx + (xx - cx) * sc_).astype(np.float32), (cy + (yy - cy) * sc_).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    ring = np.exp(-((r_px - rs) / (9 * S)) ** 2) * st_
    return img + ring[..., None] * np.array([2.6, 2.0, 1.3]) + bump[..., None] * np.array([.6, .35, .9]) * .6


def title_sparks(tau, seed=903):
    """デーン：字の まわりから 外へ とびちる 金と 白の 火花（線形の 色）"""
    a = tau - T_FLY1
    out = np.zeros((H, W), np.float32)
    if not 0 <= a < 1.0:
        return out
    if 'sp' not in TFX:
        rng = np.random.default_rng(seed)
        P = []
        for i in range(130):
            ang = rng.uniform(0, 6.28)
            P.append(dict(x=math.cos(ang) * rng.uniform(.18, .42) * W, y=math.sin(ang) * rng.uniform(.25, .48) * W, vx=math.cos(ang) * rng.uniform(500, 1600) * S,
                          vy=math.sin(ang) * rng.uniform(500, 1600) * S - rng.uniform(0, 300) * S, life=rng.uniform(.35, .9), b=rng.uniform(.5, 1.0)))
        TFX['sp'] = P
    cx, cy = W * .5, Y0 * H
    for P_ in TFX['sp']:
        if a > P_['life']:
            continue
        def at(t):
            dr = (1 - math.exp(-t / .25)) * .25
            return cx + P_['x'] + P_['vx'] * dr, cy + P_['y'] + P_['vy'] * dr + 500 * S * t * t
        x1, y1 = at(a); x0, y0 = at(max(0.0, a - .035))
        cv2.line(out, (int(x0 * 16), int(y0 * 16)), (int(x1 * 16), int(y1 * 16)), float(P_['b'] * (1 - a / P_['life'])), max(1, int(2 * S)), cv2.LINE_AA, shift=4)
    return out


GLASS = {}


def glass_setup(seed=313):
    """第4.72版：切り口の まわりの 細かく 割れる 画面の ガラス（切り口に 近いほど 細かい かけら）。
       ボロノイの 割れ目（F2−F1）・かけらごとの ずれ（屈折）と 明るさの むら・割れが とどく 時刻（つま先が 通った 時刻 ＋ 切り口からの きょり／速さ）・
       細かい かけら（つま先が 通った 時と 切り口が 開く 時に 切り口から とぶ）"""
    if GLASS:
        return GLASS
    from scipy.spatial import cKDTree
    T = tear_line()
    rng = np.random.default_rng(seed)
    nv = np.array([math.sin(ANG), math.cos(ANG)])                              # 切り口に 直角（右下 向き）
    N = 700
    sx = rng.uniform(-40 * S, W + 40 * S, N)
    off = np.minimum(rng.exponential(52 * S, N), 250 * S) * rng.choice((-1, 1), N)
    pts = np.c_[sx + off * nv[0], line_y(sx) + off * nv[1]]
    yy, xx = grid()
    dperp = (yy - line_y(xx)) * math.cos(ANG)                                  # 切り口からの きょり（直角・下が +）
    band = np.abs(dperp) < 262 * S
    iy, ix = np.nonzero(band)
    tree = cKDTree(pts)
    dist, idx = tree.query(np.c_[ix, iy].astype(np.float64), k=2)
    f21 = (dist[:, 1] - dist[:, 0]).astype(np.float32)
    cid = idx[:, 0]
    # かけらごと：ずれ（切り口に 近い ほど 大きい）・明るさ・おくれ
    co = np.abs(off)
    amp = (1.2 + 3.2 * np.exp(-co / (70 * S))) * S
    ang = rng.uniform(0, 6.28, N)
    ox, oy = np.cos(ang) * amp, np.sin(ang) * amp
    gain = np.clip(1 + rng.normal(0, .13, N), .75, 1.3)
    dly = rng.uniform(0, .05, N)
    tx = T['tx']
    xf = np.clip(ix - dperp[iy, ix] * math.sin(ANG), 0, W - 1).astype(np.int32)    # 切り口の 上の 足の x
    tc = tx[xf] + np.abs(dperp[iy, ix]) / (1700 * S) + dly[cid]
    G = GLASS
    G['tc'] = np.full((H, W), np.inf, np.float32); G['tc'][iy, ix] = tc
    G['ox'] = np.zeros((H, W), np.float32); G['ox'][iy, ix] = ox[cid]
    G['oy'] = np.zeros((H, W), np.float32); G['oy'][iy, ix] = oy[cid]
    G['gain'] = np.ones((H, W), np.float32); G['gain'][iy, ix] = gain[cid]
    cr = 1 - smoothstep(.15 * S, 1.5 * S, f21)
    near = np.exp(-np.abs(dperp[iy, ix]) / (90 * S)) * (1 - smoothstep(200 * S, 262 * S, np.abs(dperp[iy, ix])))
    G['crack'] = np.zeros((H, W), np.float32); G['crack'][iy, ix] = cr * (.18 + .82 * near)
    # 細かい かけら（つま先が 通った 時：6わり・切り口が 開く 時：4わり）
    fs = []
    for i in range(1300):
        x = rng.uniform(0, W); sg = rng.choice((-1, 1))
        wave = 0 if i % 5 < 3 else 1
        nvx = 3 if rng.random() < .55 else 4
        a_ = np.sort(rng.uniform(0, 6.28, nvx)); r_ = rng.uniform(.45, 1.0, nvx)
        fs.append(dict(x=x, sg=sg, wave=wave, s=rng.uniform(1.8, 7.0) * S, vx=rng.uniform(-160, 560) * S, vy=sg * rng.uniform(70, 640) * S,
                       w=rng.uniform(-34, 34), ph=rng.uniform(0, 6.28), poly=np.c_[np.cos(a_) * r_, np.sin(a_) * r_], life=rng.uniform(.3, .95),
                       delay=rng.uniform(0, .1), b=rng.uniform(.5, 1.0)))
    G['fine'] = fs
    return G


def glass_crack(bg, tau):
    """割れが とどいた 所の 画面の ガラス：かけらごとに 少し ずれて（屈折）明るさが ちがう・割れ目が 光る（切り口の 光が もれる）"""
    G = glass_setup()
    vis = (G['tc'] <= tau).astype(np.float32)
    if vis.max() <= 0:
        return bg
    yy, xx = grid()
    out = cv2.remap(bg, xx + G['ox'] * vis, yy + G['oy'] * vis, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    out = out * (1 + (G['gain'] - 1) * vis)[..., None]
    cr = G['crack'] * vis
    return out + cr[..., None] * np.array([2.0, 1.75, 2.4]) + blur(cr, 1.6 * S)[..., None] * np.array([.7, .45, 1.1])


def glass_fine(img, tau, yt, d):
    """細かく 砕けた ガラスの かけら（つま先が 通った 所・開く 切り口から 上下と 前へ とぶ：回って きらり）"""
    G = glass_setup()
    T = tear_line()
    fa = np.zeros((H, W), np.float32); fb = np.zeros((H, W), np.float32)
    for D in G['fine']:
        xi = int(np.clip(D['x'], 0, W - 1))
        t0 = (T['tx'][xi] if D['wave'] == 0 else max(T_OPEN, T['tx'][xi])) + D['delay']
        a = tau - t0
        if not 0 < a < D['life']:
            continue
        k = a / D['life']
        y0 = yt[xi] + D['sg'] * ((d[xi] if D['wave'] else 0.0) + 2 * S)
        cxp = D['x'] + D['vx'] * a
        cyp = y0 + D['vy'] * a + 420 * S * a * a
        ang = D['ph'] + D['w'] * a
        cs, sn = math.cos(ang), math.sin(ang)
        sq = .35 + .65 * abs(math.cos(ang * .7))                               # 回る 薄い 板（つぶれて 見える）
        pts = np.c_[D['poly'][:, 0] * cs - D['poly'][:, 1] * sn * sq, D['poly'][:, 0] * sn + D['poly'][:, 1] * cs * sq] * D['s'] + (cxp, cyp)
        P = np.round(pts * 16).astype(np.int32)
        al = (1 - ss(.6, 1, k)) * .85
        gl = abs(math.cos(ang)) ** 8
        cv2.fillPoly(fa, [P], float(al), cv2.LINE_AA, shift=4)
        cv2.fillPoly(fb, [P], float(al * D['b'] * (.35 + 2.4 * gl)), cv2.LINE_AA, shift=4)
    if fa.max() <= 0:
        return img
    return img * (1 - fa * .5)[..., None] + fb[..., None] * np.array([1.5, 1.4, 1.9]) + blur(fb, 2.5 * S)[..., None] * np.array([.5, .35, .8])


def dark_bolts(img, md, mb):
    """黒と 紫の 細かい 雷（第4.72版）：md＝芯が 黒い 雷（下を 暗く して まわりが 紫に 光る）・mb＝白っぽい 紫に 光る 雷"""
    if md.max() > 0:
        core = np.clip(blur(md, .9 * S) * 2.2, 0, 1)
        g1, g2, g3 = blur(md, 2.6 * S), blur(md, 7 * S), blur(md, 18 * S)
        img = img * (1 - .95 * core)[..., None]
        img = img + (g1[..., None] * np.array([2.4, .4, 4.6]) + g2[..., None] * np.array([1.0, .12, 2.4]) + g3[..., None] * np.array([.22, .02, .55])) * (1 - core)[..., None]
    if mb.max() > 0:
        img = img + mb[..., None] * np.array([2.2, 1.3, 3.4]) + blur(mb, 2.5 * S)[..., None] * np.array([1.0, .2, 2.2]) + blur(mb, 10 * S)[..., None] * np.array([.3, .03, .7])
    return img


def cut_bolts(tau, fi, d, seed=941):
    """第4.72版：蹄が 通った 切り口の ふち（上と 下）に 不定期に まとわる 黒と 紫の 細かい 雷 →（黒い 雷, 光る 雷）。
       2〜4コマで 消えて 別の 所に 出る・出ない 回も ある・いま 切った 所（蹄の 近く）ほど 多い・ときどき 外へ はねる・切り口を こえる"""
    T = tear_line()
    md = np.zeros((H, W), np.float32); mb = np.zeros((H, W), np.float32)
    dt = tau - T['tx']
    ok = np.nonzero(dt > .015)[0]
    if len(ok) < 8:
        return md, mb
    yt = T['y']
    jt = T['jt'] * np.minimum(d * .9, 26 * S); jb = T['jb'] * np.minimum(d * .9, 26 * S)
    wgt = .3 + np.exp(-dt[ok] / .3)
    wgt = wgt / wgt.sum()
    nv = np.array([math.sin(ANG), math.cos(ANG)])
    for j in range(44):
        life = 2 + (j % 3)
        gen, age = (fi + 5 * j) // life, (fi + 5 * j) % life
        rb = np.random.default_rng(seed * 1000 + j * 131 + gen * 7919)
        if rb.random() < .3:                                                   # 不定期（出ない 回も ある）
            continue
        rj = np.random.default_rng(seed + fi * 977 + j)                         # 光る たびに 形が 少し かわる
        x0 = int(ok[rb.choice(len(ok), p=wgt)])
        L = rb.uniform(22, 150) * S
        xs_ = x0 + rb.choice((-1, 1)) * np.linspace(0, L, max(3, int(L / (5 * S))))
        xs_ = xs_[(xs_ >= 0) & (xs_ <= W - 1)]
        if len(xs_) < 3:
            continue
        xi = xs_.astype(np.int32)
        xs_, xi = xs_[dt[xi] > .015], xi[dt[xi] > .015]
        if len(xs_) < 3:
            continue
        side = int(rb.choice((-1, 1)))                                          # −1＝上の ふち・+1＝下の ふち
        lim = d[xi] + (jt[xi] if side < 0 else jb[xi])
        ys_ = yt[xi] + side * (lim + rb.uniform(.5, 3.5) * S)
        P = zig(rj, np.c_[xs_, ys_], .2, 2)
        env_ = (1.0, .72, .45, .22)[age] * rb.uniform(.65, 1.0)
        dark = rb.random() < .62
        poly(md if dark else mb, P, env_, (2.0 if dark else 1.2) * S)
        if rb.random() < .6:                                                   # 枝
            q = P[int(rj.integers(len(P)))]
            qx = int(np.clip(q[0], 0, W - 1))
            if rb.random() < .3:                                               # 切り口を こえて 反対の ふちへ
                lim2 = d[qx] + (jb[qx] if side < 0 else jt[qx])
                q2 = np.array([q[0] + rj.uniform(-14, 14) * S, yt[qx] - side * (lim2 + 1.5 * S)])
                P2 = zig(rj, [q, q2], .22, 3)
            else:                                                              # 外へ はねる
                ang = math.atan2(side * nv[1], side * nv[0]) + rj.uniform(-.9, .9)
                Lb = rj.uniform(14, 70) * S
                P2 = zig(rj, [q, q + np.array([math.cos(ang), math.sin(ang)]) * Lb], .22, 3)
            poly(md if dark else mb, P2, env_ * .8, (1.5 if dark else .9) * S)
    return md, mb


def hoof_frame(tau, work, seed=5):
    """蹄の カットインの 1コマ（場面の 秒 τ）→ 0〜1 の sRGB"""
    yy, xx = grid()
    T = tear_line()
    bg = storm(tau)
    # ---------- デーン（第4.72版）：うしろの 後光・衝撃の 輪 ----------
    ry = title_rays(tau)
    if ry is not None:
        bg = bg + ry
    bg = title_ring(bg, tau)
    # ---------- 縦書きの 3D の 的中（奥の 光から とんできて デーンと 止まる：切り口と いっしょに 切れて 分かれる） ----------
    tl = title_layer(tau, work)
    if tl is not None:
        col, A, (x0, y0, x1, y1) = tl
        bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - A[..., None]) + col
        a_ = tau - T_FLY1
        if a_ >= 0 and tau < T_IN + .3:                                                        # 止まって いる 間 字に 雷を まとう・火花
            Af = np.zeros((H, W), np.float32); Af[y0:y1, x0:x1] = A
            kk = ss(0, .08, a_) * (1 - ss(T_IN, T_IN + .3, tau)) * (1.3 if a_ < .25 else 1.0)
            ac = arcs(0.0, contours(Af), int(round(tau * FPS)), seed=921, k=kk)
            bg = bg + ac[..., None] * np.array([2.6, 2.3, 3.4]) + blur(ac, 2.5 * S)[..., None] * np.array([1.1, .45, 2.2]) + blur(ac, 9 * S)[..., None] * np.array([.35, .1, .8])
            aura = blur(Af, 12 * S) * (1 - Af)
            bg = bg + np.clip(aura, 0, 1)[..., None] * np.array([.5, .3, .9]) * kk
        sp = title_sparks(tau)
        if sp.max() > 0:
            bg = bg + sp[..., None] * np.array([3.0, 2.2, 1.0]) + blur(sp, 3 * S)[..., None] * np.array([1.2, .7, .2])
    # ---------- 第4.72版：つま先が 通った 所から 画面の ガラスが 細かく 割れる（割れ目が 光る・かけらごとに ずれる） ----------
    bg = glass_crack(bg, tau)
    # ---------- 画面が 切れる（上は 上へ・下は 下へ ずれて、あいだから 光） ----------
    d = opening(tau)
    yt = T['y']
    above = yy < yt[None, :]
    sl = 26 * S * ss(T_OUT - .12, T_OUT + .3, tau)                                          # 第4.72版：切られた 上と 下が 切り口に そって 反対へ ずれる（上は 右上へ・下は 左下へ）
    sgn = np.where(above, 1.0, -1.0)
    mapy = (np.where(above, yy + d[None, :], yy - d[None, :]) + sgn * sl * math.sin(ANG)).astype(np.float32)
    mapx = xx + np.where(above, -1, 1) * (d[None, :] * .08) - sgn * sl * math.cos(ANG)
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
    # 刃の 光（第4.72版）：つま先が 通った すぐ あとに 切り口の 線が 白く 光る（うしろへ のびる 光の 筋）・抜けた 瞬間 線 全体が ひかる
    dtc = tau - T['tx']
    trl = np.where((dtc >= 0) & (dtc < .22), np.exp(-np.clip(dtc, 0, None) / .055), 0.0).astype(np.float32)
    if T_OUT <= tau < T_OUT + .25:
        trl = np.maximum(trl, .8 * math.exp(-(tau - T_OUT) / .06) * (dtc >= 0))
    if trl.max() > 0:
        pr = np.exp(-((yy - yt[None, :]) / (24 * S)) ** 2) * trl[None, :]
        pc = np.exp(-((yy - yt[None, :]) / (2.6 * S)) ** 2) * trl[None, :]
        img = img + pr[..., None] * np.array([1.6, 1.3, 2.2]) + pc[..., None] * np.array([3.4, 3.2, 3.6])
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
    fi = int(round(tau * FPS))
    img = glass_fine(img, tau, yt, d)                                                         # 第4.72版：細かく 砕けた ガラス
    md, mb = cut_bolts(tau, fi, d)                                                           # 第4.72版：切り口の ふちに まとう 黒と 紫の 細かい 雷（光の にじみの あとで かさねる：黒い 芯が 光に とけない）
    # ---------- 3D の 蹄 ----------
    if T_IN - .05 <= tau <= T_OUT + .06:
        rd = os.path.join(work, '_r'); os.makedirs(rd, exist_ok=True)
        hl, ha, hg, Mk = hoof_layer(tau, os.path.join(rd, f'hoof2_{int(round((tau - H_SHIFT) * FPS)):03d}'), seed)
        tx_, ty_ = Mk['toe'][0]
        L_ = abs(toe_v(tau)) * W / 60.0
        L2 = L_ * 1.0
        hl, ha, hg = hblur(hl, L2), hblur(ha, L2), hblur(hg, L2)
        pad = int(330 * S)                                                                    # 第4.72版：切り口の 角度に あわせて 蹄を かたむける（つま先を 中心に）
        hl, hg = (cv2.copyMakeBorder(x, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=0) for x in (hl, hg))
        ha = cv2.copyMakeBorder(ha, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=0)
        ty_ += pad
        Mr = cv2.getRotationMatrix2D((tx_, ty_), F['SLASH'], 1.0)
        hh_, ww_ = ha.shape
        hl, hg = (cv2.warpAffine(x, Mr, (ww_, hh_), flags=cv2.INTER_LINEAR) for x in (hl, hg))
        ha = cv2.warpAffine(ha, Mr, (ww_, hh_), flags=cv2.INTER_LINEAR)
        tw = toe_x(tau) * W
        ox, oy = tw - tx_, float(line_y(tw)) - ty_ + 4 * S
        pl_, pa = place(hl, ha, ox, oy)
        pg, _ = place(hg, ha, ox, oy)
        img = img * (1 - pa[..., None]) + pl_ + pg
        hcons = contours(pa)                                                                  # 第4.72版：蹄に まとう 黒と 紫の 細かい 雷
        md = md + arcs(0.0, hcons, fi, seed=951, k=1.0)
        mb = mb + arcs(0.0, hcons, fi, seed=957, k=.75)
        # 火花（つま先から うしろへ）
        if T_IN <= tau <= T_OUT:
            spk = np.zeros((H, W), np.float32)
            rngs = np.random.default_rng(seed + int(tau * 600))
            tx0 = toe_x(tau) * W
            for k in range(60):
                age = rngs.uniform(0, .28)
                tx_past = toe_x(max(T_IN, tau - age)) * W
                x0, y0 = tx_past, float(line_y(tx_past)) + 2 * S
                vx = -rngs.uniform(100, 900) * S; vy = rngs.uniform(-700, 400) * S
                x1 = x0 + vx * age; y1 = y0 + vy * age + 900 * S * age * age
                x2 = x1 - vx * .02; y2 = y1 - (vy + 1800 * S * age) * .02
                cv2.line(spk, (int(x2 * 16), int(y2 * 16)), (int(x1 * 16), int(y1 * 16)), float(1 - age / .28), max(1, int(1.6 * S)), cv2.LINE_AA, shift=4)
            img = img + spk[..., None] * np.array([3.0, 1.5, .5]) + blur(spk, 4 * S)[..., None] * np.array([1.2, .4, .1])
    # ---------- 寄る（切り口の 光へ）・ゆれ ----------
    zm = 1 + 4.0 * ss(T_ZOOM, T_B, tau) ** 2.2
    sx = sy = 0.0
    for ti, ax, ay in ((T_FLY1, 0, 14), (T_IN + .02, 6, 0), (T_OPEN, 12 * math.sin(ANG), 12 * math.cos(ANG))):   # ゆれ：1回 ぐっと ずれて もどる（ふるえない＝ふちが 点めつ しない）
        a = tau - ti
        if 0 < a < .45:
            k_ = math.sin(math.pi * min(a / .2, 1.0)) * math.exp(-a / .14)
            sx += ax * S * k_; sy += ay * S * k_
    shake = abs(sx) + abs(sy)
    if zm > 1.001 or shake > .3:
        cxz, cyz = W * .5, Y0 * H
        M = np.float32([[zm, 0, cxz - zm * cxz + sx], [0, zm, cyz - zm * cyz + sy]])
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        md, mb = (cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LINEAR) for x in (md, mb))
    wash = ss(F['H_WASH'], T_B, tau)
    img = bloom(img, 1.0)
    img = dark_bolts(img, md, mb)
    a_ = tau - T_FLY1
    expo = 1.0 + (.6 * math.exp(-a_ / .07) if a_ >= 0 else 0.0)                              # デーン：たたきつけた 瞬間 ぱっと 明るく（1回）
    ca = .004 + (.012 * math.exp(-a_ / .1) if a_ >= 0 else 0.0) + (.012 * math.exp(-(tau - T_OUT) / .1) if tau >= T_OUT else 0.0)
    out = finish(img * 1.6 * expo, seed + int(tau * 100), vig=.5, ca=ca)
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


# ================================================================ D ど！！！的中（3D の ロゴ：flat/shiden_logo.py）
T_D = FILM - HOOF                                              # 場面の 長さ（3.1秒）
L_IN, L_LAND, L_ARCS = F['L_IN'], F['L_LAND'], F['L_ARCS']
L_HOT, L_WASH, L_SWEEP = F['L_HOT'], F['L_WASH'], F['L_SWEEP']
L_BOLTS = tuple((round(L_LAND + t, 3), n) for t, n in F['L_BOLTS'])   # 大きな 雷（場面の 秒・本数）
WASH_COL = np.array([1.0, .93, .78])                           # 蹄の 場面の さいごの 光の 色（つなぎめ）
S0, KIN = .06, 1.5                                              # ロゴが 出る ときの 大きさ（遠く）・近づき方（だんだん 速く）
ROT0 = (-16.0, 26.0, -9.0)                                      # 出る ときの 向き（度：x・y・z）
LOGO = {}
# 第4.72版：ドンッで 大きく 振動 → 色と 大きさの ちがう ど！！！的中の 細切れ → 本物が もう一度 ドドーン ＋ 振動
L_VIB, L_VIB2, L_SLAM = F['L_VIB'], F['L_VIB2'], F['L_SLAM']
C0, C1, NCUT = F['L_CUTS']                                      # 細切れ（場面の 秒）：はじまり・おわり・数
CUT_LEN = (C1 - C0) / NCUT                                      # 1つ 0.2秒
SLAM_D = 2 / FPS                                                # ドドーン：大きな 白熱の ロゴが 2コマで たたきつく
SLAM_HIT = round(L_SLAM + SLAM_D, 6)                            # たたきつく 瞬間（音の ドドーン）
HITS = (L_LAND, SLAM_HIT)                                       # ドンッ・ドドーン（光・衝撃の 輪・かけら）


def logo_pose(lam):
    """場面の 秒 λ → ロゴの 向き（度）・場所（世界）・大きさ（とまった 時を 1）。まだ 出ない → None
       光の 中から 遠くの 小さい 白熱の ロゴが まわりながら だんだん 速く 手前へ → L_LAND で ドンッ（少し 手前へ 出て もどる・うなずく）
       → あとは ゆっくり ゆれて 寄る（映り込みが 動いて 立体に 見える）"""
    if lam < L_IN:
        return None
    if lam < L_LAND:
        u = (lam - L_IN) / (L_LAND - L_IN)
        s = S0 ** (1 - u ** KIN)
        e = (1 - u) ** 1.8
        rot = tuple(r * e for r in ROT0)
    elif lam < L_SLAM:                                                          # ドンッ（このあと 細切れ）
        a = lam - L_LAND
        s = 1 + .11 * math.sin(math.pi * a / .11) * math.exp(-a / .085)
        rot = (3.0 * math.sin(math.pi * a / .13) * math.exp(-a / .09), 0.0, 0.0)
    elif lam < SLAM_HIT:                                                        # 第4.72版：本物が 大きく 白熱で 2コマで たたきつく
        u = (lam - L_SLAM) / SLAM_D
        s = 1.4 ** (1 - u ** 1.4)
        e = 1 - u
        rot = (6.0 * e, -10.0 * e, 4.0 * e)
    else:                                                                       # ドドーン → 少し 沈んで もどる → ゆっくり ゆれて 寄る
        a = lam - SLAM_HIT
        s = 1 - .07 * math.sin(math.pi * a / .1) * math.exp(-a / .08) + .03 * ss(.3, T_D - SLAM_HIT, a)
        k = ss(.15, .8, a)
        rot = (-1.6 * math.sin(2 * math.pi * a / 2.1 + .4) * k + 3.5 * math.sin(math.pi * a / .12) * math.exp(-a / .09),
               3.2 * math.sin(2 * math.pi * a / 2.6) * k,
               -.8 * math.sin(2 * math.pi * a / 3.1 + 1.0) * k)
    pos = -_CDIR * SL.CAM_DIST * (1 / s - 1)
    return rot, pos, s


def logo_center():
    if 'c' not in LOGO:
        LOGO['c'] = SL.project(np.zeros(3), SL.camera(), W, H)[0][0]
    return LOGO['c']


def heat_of(lam):
    if lam >= L_SLAM:                                                           # ドドーン：白熱で たたきつけて すぐ 冷める（ボードの 前に 金と 虹を 見せる）
        return 1 - ss(.05, .27, lam - L_SLAM)
    return 1 - ss(L_HOT[0], L_HOT[1], lam)


VIB_A = ((L_VIB, 30.0, 1.0), ((SLAM_HIT, L_VIB2[1]), 34.0, .6))   # 振動（場面の 秒・大きさ px・はじめの ガッの 大きさ）


def vib(lam):
    """第4.72版：大きな 振動（ドンッ・ドドーン）→（いまの ずれ x, y（px）, まわり（度）, ふるえの はば（px））。
       はじめの 2コマで 右へ ガッ → 左へ ガッ（ぶれ つき）→ あとは 速く ふるえる 二重の 像（左右 対称・はばが だんだん 小さく）。
       コマごとに 行ったり 来たり させない＝ふちが 1秒に 何回も 明るく 暗く ならない（点めつの きまり 16.6）"""
    for (t0, t1), A, jk in VIB_A:
        a = lam - t0
        if -1e-6 <= a < t1 - t0:
            j = int(round(a * FPS))
            A_ = A * S
            jx, jy, jr = (jk * v for v in {0: (1.0, .22, 1.2), 1: (-.55, -.12, -.7)}.get(j, (0.0, 0.0, 0.0)))
            amp = A_ * .5 * math.exp(-(a - 2 / FPS) / .12) * (1 - ss(t1 - t0 - .1, t1 - t0, a)) if j >= 2 else 0.0
            return jx * A_, jy * A_, jr, amp
    return 0.0, 0.0, 0.0, 0.0


def sweep_of(lam):
    """走る 光の 筋（映り込む 向き：度）。ない 時は None"""
    for a, b in L_SWEEP:
        if a <= lam <= b:
            return -48 + 78 * ss(0, 1, (lam - a) / (b - a))
    return None


ARC_L = (((-.95, .25, .2), (1.0, .45, 2.2), .9, 0.0), ((.95, .1, .25), (.9, .4, 2.0), 1.1, 1.3), ((-.4, -.9, .2), (.8, .3, 1.8), .7, 2.1),
         ((.5, -.85, .2), (1.0, .4, 2.1), 1.3, .4), ((.1, .98, .2), (.9, .5, 2.0), .8, 2.7))   # まとう 電気の 光（向き・色・ゆらぎの 速さ・位相）：面取りと 横に 映る


def d_tex(seed=611):
    """背景の 雲（つなぎめの ない 大きな もよう 2まい）・金の かけら・火の粉"""
    if 'c1' not in LOGO:
        rng = np.random.default_rng(seed)
        h2, w2 = int(H * .75) + 8, int(W * .75) + 8                                  # 画面の 1.5倍 を 半分の 細かさで（ゆっくり 寄っても はしが 出ない）
        for k, (sc_, oc) in enumerate(((150, 6), (70, 5))):
            n = fbm(h2, w2, sc_ * S, oc, seed=seed + 11 * k)
            n = (n - n.min()) / (n.max() - n.min() + 1e-6)
            n = 1 - np.abs(2 * n - 1) ** .85                                         # もくもく（billow）
            n = (n - n.min()) / (n.max() - n.min() + 1e-6)
            g = cv2.GaussianBlur(n.astype(np.float32), (0, 0), 1.2)
            gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=5) / 30
            gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=5) / 30
            LOGO[f'c{k + 1}'] = (g, gx, gy)
        for key, nfl, spk in (('fl', 170, 1.0), ('fl2', 240, 1.35)):           # ドンッ・ドドーンで とびちる 金の かけら（3D の 回る 薄い 板）
            FL = []
            for i in range(nfl):
                a = rng.uniform(0, 6.28); r0 = rng.uniform(.02, .3)
                sp = rng.uniform(.55, 1.9) * (1.25 if i % 3 else .8) * spk
                FL.append(dict(x=math.cos(a) * r0, y=math.sin(a) * r0 * .8, vx=math.cos(a) * sp, vy=math.sin(a) * sp * .85 - rng.uniform(.1, .5),
                               s=rng.uniform(2.2, 6.5), w=rng.uniform(8, 22) * rng.choice((-1, 1)), ph=rng.uniform(0, 6.28), life=rng.uniform(1.0, 1.9),
                               back=(i % 3 == 0), tint=rng.uniform(0, 1)))
            LOGO[key] = FL
        EM = []
        for i in range(110):                                                  # 下から 立ちのぼる 火の粉
            EM.append(dict(t0=rng.uniform(L_LAND - .2, T_D), x=rng.uniform(-.05, 1.05), vy=rng.uniform(.10, .26), life=rng.uniform(1.4, 2.6),
                           sw=rng.uniform(.01, .04), f=rng.uniform(.6, 1.6), ph=rng.uniform(0, 6.28), s=rng.uniform(1.0, 2.6), b=rng.uniform(.5, 1.0)))
        LOGO['em'] = EM
    return LOGO


def cloud(key, cx, cy, zoom, rot, drift):
    """雲の もよう（画面の まん中を 中心に ゆっくり 寄る・まわる・流れる）→ こさ・明るさの 向き（x, y）"""
    yy, xx = grid()
    n, gx, gy = d_tex()[key]
    h2, w2 = n.shape
    cs, sn = math.cos(rot), math.sin(rot)
    dx, dy = (xx - cx) / zoom, (yy - cy) / zoom
    u = (cs * dx - sn * dy) * .5 + w2 / 2 + drift[0]
    v = (sn * dx + cs * dy) * .5 + h2 / 2 + drift[1]
    u, v = u.astype(np.float32), v.astype(np.float32)
    return [cv2.remap(a, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) for a in (n, gx, gy)]


def d_bg(lam, bolt_glow):
    """背景：ロゴの うしろの 強い 光（白 → むらさき）を 暗い 雷雲が さえぎる（光に 近い 雲の ふちが 銀に 光る）・雲の すきまから 外へ 光の 筋・
       ドンッで 光が ふくらみ 衝撃の 輪"""
    yy, xx = grid()
    cx, cy = logo_center()
    rr = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / W) ** 2)
    op = 1 - ss(0.0, .55, lam)                                                  # はじめは 画面を つつむ 光 → ちぢむ
    hit = SLAM_HIT if lam >= L_SLAM else L_LAND                                  # ドンッ・ドドーン
    a = lam - hit
    land = math.exp(-a / .25) if a >= 0 else 0.0
    if L_SLAM <= lam < SLAM_HIT:                                                 # ドドーン：たたきつく 前の 2コマ も 光が ふくらむ
        land = .6 + .4 * (lam - L_SLAM) / SLAM_D
    puls = 1 + .05 * math.sin(2 * math.pi * .8 * lam) * ss(L_LAND, L_LAND + .5, lam)
    k = (1 + 1.2 * land + 1.8 * op) * puls
    core = np.exp(-(rr / (.13 + .5 * op + .06 * land)) ** 2)
    mid = np.exp(-rr / (.22 + .3 * op))
    far = np.exp(-rr / .7)
    light = (core[..., None] * np.array([1.5, 1.3, 1.75]) * 2.6 + mid[..., None] * np.array([.55, .2, 1.0]) * .75
             + far[..., None] * np.array([.1, .025, .2]) * .3) * k
    # 雲（2まい：ゆっくり 寄って まわる＝奥行き）
    n1, g1x, g1y = cloud('c1', cx, cy, 1 + .06 * lam, .03 * lam, (12 * lam, -18 * lam))
    n2, g2x, g2y = cloud('c2', cx, cy, 1 + .1 * lam, -.05 * lam, (-20 * lam, -10 * lam))
    d1 = smoothstep(.38, .78, n1)
    d2 = smoothstep(.45, .85, n2)
    dens = np.clip(d1 * .9 + d2 * .55, 0, 1)
    T = np.clip(1 - .94 * dens, 0, 1)                                           # 雲を ぬける 光
    # 光に 向いた 側（ロゴの 方）が 明るい：雲の こさの かたむきと 光の 向き
    lx, ly = (cx - xx) / (rr * W + 1e-3), (cy - yy) / (rr * W + 1e-3)
    facing = np.clip(.5 - (g1x * lx + g1y * ly) * 1.6 - (g2x * lx + g2y * ly) * .8, 0, 1.4)
    edge = np.clip(dens * (1 - dens) * 4, 0, 1)
    lit = (core * 1.2 + mid * .9 + far * .15)
    body = dens * (.012 + .05 * lit * facing)
    img = light * T[..., None]
    img = img + (edge * facing * lit * .9)[..., None] * np.array([1.0, .78, 1.15])          # 銀の ふち
    img = img + body[..., None] * np.array([.9, .45, 1.6])
    img = img + (dens * bolt_glow)[..., None] * np.array([1.1, .75, 2.2])                   # 雷が 雲を 照らす
    # 光の 筋（雲の すきまから 外へ）
    src = light * T[..., None] * smoothstep(.05, .3, rr)[..., None]
    img = img + zoom_blur(np.minimum(src, 2.5), cx, cy, 1.0, 14) * .42
    # 衝撃の 輪（ドンッ：背景を ゆがめる・ふちが 光る）
    if 0 <= a < .65:
        rs = W * (.12 + 1.55 * (1 - math.exp(-a / .22)))
        st_ = math.exp(-a / .18)
        r_px = rr * W
        bump = np.exp(-((r_px - rs) / (34 * S)) ** 2) * st_
        sc_ = 1 - 26 * S * bump / np.maximum(r_px, 1)
        mx = (cx + (xx - cx) * sc_).astype(np.float32)
        my = (cy + (yy - cy) * sc_).astype(np.float32)
        img = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ring = np.exp(-((r_px - rs) / (8 * S)) ** 2) * st_
        img = img + ring[..., None] * np.array([2.4, 1.9, 1.2]) + bump[..., None] * np.array([.5, .3, .8]) * .6
    img = img * (.55 + .45 * (1 - smoothstep(.3, 1.0, rr)))[..., None] + np.array([0.003, 0.0015, 0.007])   # まわりは 暗く
    return img


def zig(rng, pts, rough, iters):
    """折れ線を ジグザグに（まん中に 点を 足して 横へ ずらす を くりかえす）"""
    P = np.asarray(pts, float)
    for _ in range(iters):
        d = P[1:] - P[:-1]
        L = np.linalg.norm(d, axis=1, keepdims=True) + 1e-6
        nv = np.c_[-d[:, 1], d[:, 0]] / L
        mids = (P[:-1] + P[1:]) / 2 + nv * rng.normal(0, 1, (len(d), 1)) * L * rough
        Q = np.empty((len(P) + len(mids), 2))
        Q[0::2], Q[1::2] = P, mids
        P = Q
    return P


def poly(m, P, val, w):
    cv2.polylines(m, [np.round(P * 16).astype(np.int32)], False, float(val), max(1, int(round(w))), cv2.LINE_AA, shift=4)


def contours(Afull):
    """ロゴの ふち（外の 線ごと：点・外向き）"""
    cs, _ = cv2.findContours((Afull > .5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        c = c[:, 0, :].astype(np.float32)
        if len(c) < 40:
            continue
        c = c[::2]
        t = np.roll(c, -3, 0) - np.roll(c, 3, 0)
        nv = np.c_[t[:, 1], -t[:, 0]]
        nv /= np.linalg.norm(nv, axis=1, keepdims=True) + 1e-6
        q = np.round(c + nv * 4).astype(int)
        q[:, 0] = np.clip(q[:, 0], 0, W - 1); q[:, 1] = np.clip(q[:, 1], 0, H - 1)
        inside = Afull[q[:, 1], q[:, 0]] > .5
        nv[inside] *= -1
        out.append((c, nv))
    return out


def arcs(lam, cons, fi, seed=733, k=None):
    """ロゴに まとう 電気（ふちを はう・外へ はねる・字と 字の あいだを とぶ）→ 芯の 明るさ（0〜）。k＝強さ（なし → ロゴの 時刻で）"""
    m = np.zeros((H, W), np.float32)
    if not cons:
        return m
    if k is None:
        k = ss(L_ARCS, L_ARCS + .25, lam)
    lens = np.array([len(c) for c, _ in cons], float)
    pr = lens / lens.sum()
    allp = np.concatenate([c for c, _ in cons]); alln = np.concatenate([n for _, n in cons])
    owner = np.concatenate([np.full(len(c), j) for j, (c, _) in enumerate(cons)])
    NA = 16
    for j in range(NA):
        life = 3
        age = (fi + j) % life
        gen = (fi + j) // life
        rb = np.random.default_rng(seed * 1000 + j * 97 + gen * 7919)
        rj = np.random.default_rng(seed + fi * 131 + j)
        env_ = (1.0, .78, .5)[age] * k * rb.uniform(.6, 1.0)
        typ = rb.random()
        ci = rb.choice(len(cons), p=pr)
        c, nv = cons[ci]
        i = int(rb.integers(len(c)))
        if typ < .55:                                                          # ふちを はう
            L = int(rb.integers(10, 32))
            idx = (i + np.arange(0, L * 3, 3)) % len(c)
            h = (rb.uniform(2, 7) + 3 * np.sin(np.linspace(0, 3.14, len(idx)))) * S
            base = c[idx] + nv[idx] * h[:, None]
            P = zig(rj, base, .22, 2)
            poly(m, P, env_, 1.3 * S)
        elif typ < .85:                                                        # 外へ はねる（枝つき）
            ang = math.atan2(nv[i][1], nv[i][0]) + rb.uniform(-.6, .6)
            Ln = rb.uniform(28, 90) * S
            p1 = c[i] + np.array([math.cos(ang), math.sin(ang)]) * Ln
            P = zig(rj, [c[i], p1], .2, 5)
            poly(m, P, env_, 1.4 * S)
            q = P[len(P) // 2]
            a2 = ang + rb.choice((-1, 1)) * rb.uniform(.5, 1.0)
            P2 = zig(rj, [q, q + np.array([math.cos(a2), math.sin(a2)]) * Ln * .45], .22, 4)
            poly(m, P2, env_ * .7, 1.0 * S)
        else:                                                                  # 字と 字の あいだを とぶ
            d = np.linalg.norm(allp - c[i], axis=1)
            ok = np.nonzero((d > 24 * S) & (d < 150 * S) & (owner != ci))[0]
            if len(ok) == 0:
                continue
            q = allp[ok[int(rb.integers(len(ok)))]]
            mid = (c[i] + q) / 2 + (nv[i] - 0) * rb.uniform(5, 18) * S
            P = zig(rj, [c[i], mid, q], .18, 4)
            poly(m, P, env_ * 1.1, 1.5 * S)
    return m


def bolt_dir_end(p0, d):
    """p0 から 向き d に 画面の ふちの 少し 外まで"""
    ts = []
    for k_, lim in ((0, -.04 * W), (0, 1.04 * W), (1, -.04 * H), (1, 1.04 * H)):
        if abs(d[k_]) > 1e-6:
            t = (lim - p0[k_]) / d[k_]
            if t > 0:
                ts.append(t)
    return p0 + d * min(ts)


BOLT_I = (1.0, .85, .5, .25, .08)                                             # 大きな 雷の 明るさ（30コマ/秒の コマごと：1回 光って 消える＝点めつを ふやさない）


def big_bolts(lam, cons, seed=757):
    """不定期の 大きな 雷（ロゴの ふちから 画面の 全方位の ふちへ・枝つき）→（芯, 雲を 照らす 光, ロゴに 映る 光 [(画面の 向き, 強さ)]）"""
    core = np.zeros((H, W), np.float32)
    lights = []
    if not cons:
        return core, core, lights
    allp = np.concatenate([c for c, _ in cons]); alln = np.concatenate([n for _, n in cons])
    for (tb, nb) in L_BOLTS:
        fi = int(math.floor((lam - tb) * FPS + 1e-6))
        if not 0 <= fi < len(BOLT_I):
            continue
        inten = BOLT_I[fi]
        rng = np.random.default_rng(seed + int(tb * 1000))
        a0 = rng.uniform(0, 6.28)
        for j in range(nb):
            tgt = a0 + j * 6.28 / nb + rng.uniform(-.5, .5)
            want = np.array([math.cos(tgt), math.sin(tgt)])
            sc_ = alln @ want
            cand = np.nonzero(sc_ > .8)[0]
            i = int(cand[rng.integers(len(cand))]) if len(cand) else int(np.argmax(sc_))
            p0 = allp[i]
            d = nrm(alln[i] * .5 + want * .5)
            p1 = bolt_dir_end(p0, d)
            rj = np.random.default_rng(seed + int(tb * 1000) + j * 31 + fi * 7)     # 光る たびに 形が 少し かわる
            rs = np.random.default_rng(seed + int(tb * 1000) + j * 31)
            P = zig(rs, [p0, p1], .2, 6)
            P = P + rj.normal(0, 1.2 * S, P.shape) * np.linspace(0, 1, len(P))[:, None]
            poly(core, P, inten, 3.0 * S)
            for b in range(3):                                                 # 枝
                k0 = int(rs.integers(len(P) // 5, len(P) * 3 // 4))
                q = P[k0]
                dd = P[min(len(P) - 1, k0 + 8)] - q
                ang = math.atan2(dd[1], dd[0]) + rs.choice((-1, 1)) * rs.uniform(.35, .9)
                Lb = np.linalg.norm(p1 - p0) * rs.uniform(.15, .35)
                P2 = zig(rs, [q, q + np.array([math.cos(ang), math.sin(ang)]) * Lb], .22, 5)
                poly(core, P2, inten * .65, 1.6 * S)
            lights.append((d, inten))
    glow = blur(core, 30 * S) * 3.0
    return core, glow, lights


def flakes(lam, front):
    """ドンッ（細切れの 前）・ドドーン（第4.72版）で とびちる 金の かけら（回る 薄い 板：こちらを 向いた 時に きらり）→ 線形の 色"""
    out = np.zeros((H, W, 3), np.float32)
    key, t0 = ('fl2', SLAM_HIT) if lam >= L_SLAM else ('fl', L_LAND)
    a = lam - t0
    if a <= 0:
        return out
    cx, cy = logo_center()
    for P_ in d_tex()[key]:
        if P_['back'] == front or a > P_['life']:
            continue
        def at(t):
            dr = (1 - math.exp(-t / .35)) * .35                                   # 空気で おそく なる
            return (cx + (P_['x'] + P_['vx'] * dr * 2.4) * W, cy + (P_['y'] + P_['vy'] * dr * 2.4) * W + 420 * S * t * t)
        x, y = at(a)
        x2, y2 = at(max(0, a - 1 / 60))
        ang = P_['ph'] + P_['w'] * a
        face = abs(math.cos(ang))
        gl = face ** 10
        fade = 1 - ss(.7, 1.0, a / P_['life'])
        sz = P_['s'] * S * (1.15 if front else .8)
        col = (np.array([2.0, 1.35, .42]) * (1 - P_['tint']) + np.array([2.2, 1.7, .9]) * P_['tint']) * (.25 + .9 * face + 4.0 * gl) * fade
        m = np.zeros((H, W), np.float32)
        cv2.ellipse(m, (int(x * 16), int(y * 16)), (int(sz * 16), int(max(1, sz * (.25 + .75 * face)) * 16)), math.degrees(ang * .7) % 360, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
        cv2.line(m, (int(x2 * 16), int(y2 * 16)), (int(x * 16), int(y * 16)), .35, max(1, int(sz * .5)), cv2.LINE_AA, shift=4)
        out += m[..., None] * col
    return out


def embers(lam):
    """下から 立ちのぼる 火の粉（ゆれながら・ちらちら）→ 線形の 色"""
    m = np.zeros((H, W), np.float32)
    for E in d_tex()['em']:
        a = lam - E['t0']
        if not 0 < a < E['life']:
            continue
        u = a / E['life']
        x = (E['x'] + E['sw'] * math.sin(E['f'] * a * 6.28 + E['ph'])) * W
        y = (1.06 - E['vy'] * a * 1.6) * H
        x2 = (E['x'] + E['sw'] * math.sin(E['f'] * (a - .04) * 6.28 + E['ph'])) * W
        y2 = (1.06 - E['vy'] * (a - .04) * 1.6) * H
        b = E['b'] * ss(0, .12, u) * (1 - ss(.65, 1, u)) * (.75 + .25 * math.sin(a * 17 + E['ph']))
        cv2.line(m, (int(x2 * 16), int(y2 * 16)), (int(x * 16), int(y * 16)), float(b), max(1, int(E['s'] * S)), cv2.LINE_AA, shift=4)
    return m[..., None] * np.array([3.0, 1.25, .28]) + blur(m, 3 * S)[..., None] * np.array([1.2, .4, .08])


def star_glints(col, A):
    """ロゴの いちばん 明るい つや → 十字の 光（レンズの きらり）"""
    lum = col.max(2)
    hi = np.clip(lum - 2.6, 0, 3.0) * A
    if hi.max() <= 0:
        return np.zeros_like(col)
    hi = blur(hi, 1.0 * S)
    L = int(46 * S) | 1
    k1 = np.exp(-np.abs(np.linspace(-1, 1, L)) * 5).astype(np.float32)
    k1 /= k1.sum()
    st = cv2.filter2D(hi, -1, k1[None, :]) + cv2.filter2D(hi, -1, k1[:, None])
    return st[..., None] * np.array([1.0, .92, .8]) * 2.2


def logo_frame(lam, work, fi, seed=811):
    """ど！！！的中 の 1コマ（場面の 秒 λ）→ 0〜1 の sRGB。細切れ（第4.72版：C0〜L_SLAM）の あいだは cut_frame"""
    if C0 <= lam < L_SLAM:
        return cut_frame(lam, work, fi, seed)
    yy, xx = grid()
    cx, cy = logo_center()
    # ---------- 振動（第4.72版：ドンッ・ドドーン）：いまの ずれと 前の コマの ずれ（ぶれ） ----------
    vx, vy, vr, vamp = vib(lam)
    pvx, pvy, pvr, _ = vib(lam - 1 / FPS)
    jolt = abs(vx) + abs(vy) + abs(pvx) + abs(pvy) > .3 and vamp <= .3
    shaking = jolt or vamp > .3

    def Mv(ox, oy, r):
        M = cv2.getRotationMatrix2D((float(cx), float(cy)), float(r), 1.0)
        M[0, 2] += ox; M[1, 2] += oy
        return M
    # ---------- 3D の ロゴ（光は 2D で：映り込み・白熱・走る 光の 筋・まとう 電気と 大きな 雷の 光） ----------
    pose = logo_pose(lam)
    lay = None
    g = (None, None)
    Afull = np.zeros((H, W), np.float32)
    if pose is not None:
        rot, pos, s = pose
        rd_ = os.path.join(work, '_r'); os.makedirs(rd_, exist_ok=True)
        cache = os.path.join(work, '_logo'); os.makedirs(cache, exist_ok=True)
        g = SL.render(os.path.join(rd_, f'logo_{fi:03d}'), W, H, rot, pos, cache)              # 形（光は あとで：雷の 光の 前に ふちを 知る）
    if g[0] is not None:
        K = SL.K_SS
        x0, y0, x1, y1 = g[1]
        w_, h_ = (x1 - x0) // K, (y1 - y0) // K
        Afull[y0 // K:y0 // K + h_, x0 // K:x0 // K + w_] = cv2.resize(g[0]['a'], (w_, h_), interpolation=cv2.INTER_AREA)
        if jolt:
            Afull = cv2.warpAffine(Afull, Mv(vx, vy, vr), (W, H), flags=cv2.INTER_LINEAR)
    cons = contours(Afull) if g[0] is not None else []
    bc, bglow, blights = big_bolts(lam, cons)
    if g[0] is not None:
        flash = []
        k = ss(L_ARCS, L_ARCS + .3, lam)
        for d, c_, f_, ph in ARC_L:
            flash.append((nrm(np.array(d)), np.array(c_) * .6 * k * (.55 + .45 * math.sin(2 * math.pi * f_ * lam + ph))))
        for d2, it in blights:
            flash.append((nrm(np.array([d2[0], -d2[1], .45])), np.array([1.6, 1.2, 2.6]) * it))
        lay = SL.layer(None, W, H, rot, pos, sweep=sweep_of(lam), flash=flash, heat=heat_of(lam), gbuf=g)
    # ---------- 背景・うしろの かけら ----------
    img = d_bg(lam, bglow)
    img = img + flakes(lam, front=False)
    # ---------- ロゴ（振動は ぶれ つき：前の コマの 場所から いまの 場所へ） ----------
    if lay is not None:
        col, A, (x0, y0, x1, y1) = lay
        colF = np.zeros((H, W, 3), np.float32); AF = np.zeros((H, W), np.float32)
        colF[y0:y1, x0:x1] = col; AF[y0:y1, x0:x1] = A
        if shaking:
            NSB = 8
            acc_c = np.zeros_like(colF); acc_a = np.zeros_like(AF)
            for j in range(NSB):
                if jolt:                                                                        # ガッ：前の コマの 場所から いまの 場所へ ぶれ
                    f = j / (NSB - 1) * .7
                    M = Mv(vx + (pvx - vx) * f, vy + (pvy - vy) * f, vr + (pvr - vr) * f)
                else:                                                                           # ふるえる 二重の 像（左右 対称：コマが かわっても 同じ 形）
                    ph = 2 * math.pi * (j + .5) / NSB
                    M = Mv(vamp * math.sin(ph), .25 * vamp * math.sin(2 * ph), .6 * math.sin(ph) * vamp / (30 * S))
                acc_c += cv2.warpAffine(colF, M, (W, H), flags=cv2.INTER_LINEAR)
                acc_a += cv2.warpAffine(AF, M, (W, H), flags=cv2.INTER_LINEAR)
            colF, AF = acc_c / NSB, acc_a / NSB
        if L_SLAM <= lam < SLAM_HIT:                                                         # たたきつく 2コマ：手前へ 向かう ぶれ
            colF = zoom_blur(colF, cx, cy, .1, 8)
            AF = zoom_blur(AF, cx, cy, .1, 8)
        img = img * (1 - np.clip(AF, 0, 1)[..., None]) + colF
        gk = 1 - ss(0, .3, heat_of(lam))
        if gk > 0:
            img = img + star_glints(colF, AF) * gk
        # まとう 電気の うすい 光（ふちの まわり）
        aura = blur(Afull, 10 * S) * (1 - Afull)                                              # 字の 外だけ
        k = ss(L_ARCS, L_ARCS + .4, lam) * (.8 + .2 * math.sin(lam * 2 * math.pi * .9))
        img = img + np.clip(aura, 0, 1)[..., None] * np.array([.3, .1, .65]) * k
    # ---------- 電気・雷・手前の かけら・火の粉 ----------
    ac = arcs(lam, cons, fi)
    img = img + ac[..., None] * np.array([2.6, 2.3, 3.4]) + blur(ac, 2.5 * S)[..., None] * np.array([1.1, .45, 2.2]) + blur(ac, 9 * S)[..., None] * np.array([.35, .1, .8])
    img = img + bc[..., None] * np.array([3.2, 2.9, 4.0]) + blur(bc, 4 * S)[..., None] * np.array([1.4, .6, 2.6]) + bglow[..., None] * np.array([.12, .05, .28])
    img = img + flakes(lam, front=True)
    img = img + embers(lam)
    # ---------- ドンッ・ドドーン（光・画面の ゆれ） ----------
    hit = SLAM_HIT if lam >= L_SLAM else L_LAND
    a = lam - hit
    img = bloom(img, 1.0)
    ca = .003 + (.012 * math.exp(-a / .1) if a >= 0 else 0.0) + (.004 if shaking else 0.0)
    out = finish(img, seed + fi, vig=.55, ca=ca)                                  # 第4.72版：ぱっと 明るく する のは やめた（細切れと 振動の 点めつを ふやさない）
    w = 1 - ss(L_WASH[0], L_WASH[1], lam)                                       # はじめ：蹄の 場面の 光の 白から
    if w > 0:
        out = out * (1 - w) + WASH_COL * w
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- 第4.72版：色と 大きさの ちがう ど！！！的中 の 細切れ（0.2秒ずつ）
CUTS = (   # pal＝色（shiden_logo の PALETTES）・s＝大きさ（とまった 本物を 1）・rot＝向き（度）・q＝ロゴの 中の 点（原点からの px・下が +）を 画面の at（割合）へ・
           # bg＝背景の もよう・c1＝奥の 光・c2＝まわり・ln＝線（線形の 色：明るさは 0.1 未満＝点めつに ならない）。カットの 中では ロゴも 背景も 動かさない
    dict(pal='red', s=1.12, rot=(-8.0, 16.0, -8.0), q=(0, 0), at=(.5, .45), bg='burst', c1=(2.4, .3, .1), c2=(.42, .018, .01), ln=(.36, .016, .008)),
    dict(pal='blue', s=.7, rot=(14.0, -30.0, 6.0), q=(0, 0), at=(.47, .4), bg='streak', c1=(.45, 1.0, 2.8), c2=(.02, .045, .34), ln=(.03, .08, .6)),
    dict(pal='green', s=.98, rot=(-12.0, 24.0, 2.0), q=(0, 0), at=(.52, .55), bg='rings', c1=(.35, 2.2, .7), c2=(.01, .16, .04), ln=(.012, .1, .03)),
    dict(pal='silver', s=.9, rot=(6.0, 38.0, -4.0), q=(0, 0), at=(.5, .47), bg='slash', c1=(1.5, 1.6, 1.9), c2=(.06, .065, .09), ln=(.085, .09, .12)),
    dict(pal='purple', s=1.1, rot=(10.0, -16.0, 9.0), q=(0, 0), at=(.5, .44), bg='storm', c1=(1.5, .55, 2.9), c2=(.16, .025, .38), ln=(.12, .02, .36)),
    dict(pal='gold', s=1.45, rot=(-5.0, 12.0, -4.0), q=(-27, -62), at=(.53, .42), bg='gold', c1=(2.8, 1.5, .3), c2=(.36, .13, .02), ln=(.36, .15, .03)),
)


def place_logo(s, q, at, rot):
    """ロゴの 中の 点 q（原点からの px・下が +）が 画面の at（割合）に 大きさ s で 見える ロゴの 場所（世界）"""
    eye, tgt, fov = SL.camera()
    fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
    th = math.tan(math.radians(fov) / 2); asp = W / H
    z = float((np.zeros(3) - eye) @ fw) / s                                    # とまった 本物の 奥行きの 1/s
    p = eye + (fw + rt * ((2 * at[0] - 1) * th * asp) + up * ((1 - 2 * at[1]) * th)) * z
    return p - SL.rot_xyz(*rot) @ np.array([q[0] / 100.0, -q[1] / 100.0, 0.0])


def cut_layer(k, work):
    """細切れ k の ロゴ（3D の 形も 光も 1回だけ：カットの あいだは 2D で うごかす）→（色, すき通し, 箱）"""
    key = f'cut{k}'
    if key in LOGO:
        return LOGO[key]
    C = CUTS[k]
    rd_ = os.path.join(work, '_r'); os.makedirs(rd_, exist_ok=True)
    fn = os.path.join(rd_, f'cut{k}_{W}.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        LOGO[key] = (z['col'], z['a'], tuple(int(v) for v in z['box']))
        return LOGO[key]
    cache = os.path.join(work, '_logo'); os.makedirs(cache, exist_ok=True)
    c1 = np.array(C['c1'], float)
    tint = c1 / c1.max()
    flash = [(nrm(np.array([-.9, .3, .25])), tint * 1.3), (nrm(np.array([.85, -.25, .3])), tint * .9), (nrm(np.array([.1, .95, .25])), np.array([.9, .85, .8]) * .6)]
    pos = place_logo(C['s'], C['q'], C['at'], C['rot'])
    col, A, box = SL.layer(os.path.join(rd_, f'cut{k}'), W, H, C['rot'], pos, sweep=None, flash=flash, heat=0.0, cache=cache, pal=C['pal'])
    np.savez(fn, col=col.astype(np.float32), a=A.astype(np.float32), box=np.array(box))
    LOGO[key] = (col, A, box)
    return LOGO[key]


def focus_lines(k, cx, cy, u, n=160, r0=(.22, .5), wid=(.004, .016)):
    """集中線（外から まん中へ：カットの あいだ 少しずつ まん中へ のびる）→ こさ（0〜1.5）"""
    key = f'foc{k}'
    if key not in LOGO:
        rng = np.random.default_rng(300 + k)
        M = 4096
        tg = np.linspace(-math.pi, math.pi, M, endpoint=False)
        groups = []
        for gi in range(4):
            P = np.zeros(M, np.float32)
            for i in range(n // 4):
                t0 = rng.uniform(-math.pi, math.pi); w = rng.uniform(*wid); b = rng.uniform(.35, 1.0)
                d = (tg - t0 + math.pi) % (2 * math.pi) - math.pi
                P += (b * np.exp(-(d / w) ** 2)).astype(np.float32)
            groups.append((P, r0[0] + (r0[1] - r0[0]) * gi / 3))
        LOGO[key] = groups
    yy, xx = grid()
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / W
    th = np.arctan2(yy - cy, xx - cx)
    idx = (((th + math.pi) / (2 * math.pi)) * 4096).astype(np.int32) % 4096
    out = np.zeros((H, W), np.float32)
    for P, rr in LOGO[key]:
        out += P[idx] * smoothstep(rr, rr + .12, r)
    return np.minimum(out, 1.5)


def cut_bg(k, u, cx, cy):
    """細切れ k の 背景（線形の 色）：奥の 光（ロゴの うしろ）＋ もよう（集中線・横の 速さの 線・広がる 輪・斜めの 切りあと・雷雲・金の 集中線と きらめき）"""
    C = CUTS[k]
    yy, xx = grid()
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / W
    c1, c2, ln = (np.array(C[n], np.float32) for n in ('c1', 'c2', 'ln'))
    core = np.exp(-(r / .22) ** 2)
    mid = np.exp(-r / .32)
    img = core[..., None] * c1 + mid[..., None] * c2 + c2 * .1
    rng = np.random.default_rng(500 + k)
    kind = C['bg']
    m = np.zeros((H, W), np.float32)
    if kind in ('burst', 'gold'):
        m = focus_lines(k, cx, cy, u)
    elif kind == 'streak':                                                       # 横の 速さの 線（左へ とぶ）
        for i in range(120):
            y = rng.uniform(0, H); L = rng.uniform(.25, .9) * W; v = rng.uniform(1800, 3600) * S
            x = rng.uniform(-.2 * W, 1.2 * W) - v * u
            b = rng.uniform(.3, 1.0); th_ = max(1, int(round(rng.uniform(1.0, 4.5) * S)))
            cv2.line(m, (int(x * 16), int(y * 16)), (int((x + L) * 16), int(y * 16)), float(b), th_, cv2.LINE_AA, shift=4)
        m = cv2.blur(m, (int(31 * S) | 1, 1)) * 1.6
    elif kind == 'rings':                                                        # 広がる 輪
        for j in range(7):
            Rj = .14 + .16 * j + .7 * u
            m += np.exp(-((r - Rj) / (.006 + .002 * j)) ** 2) * (1 - .1 * j)
        m += focus_lines(k, cx, cy, u, n=90, r0=(.3, .6)) * .5
    elif kind == 'slash':                                                        # 斜めの 切りあと（銀）
        for i in range(9):
            ang = math.radians(rng.uniform(-38, -22)); off = rng.uniform(-.5, .5) * H
            x0, y0 = -W * .2, H * .5 + off; x1, y1 = W * 1.2, H * .5 + off + math.tan(ang) * W * 1.4
            th_ = max(1, int(round(rng.uniform(2.0, 7.0) * S)))
            cv2.line(m, (int(x0 * 16), int(y0 * 16)), (int(x1 * 16), int(y1 * 16)), float(rng.uniform(.5, 1.0)), th_, cv2.LINE_AA, shift=4)
        m = m + blur(m, 6 * S) * .8
        m += focus_lines(k, cx, cy, u, n=80, r0=(.35, .6)) * .4
    elif kind == 'storm':                                                        # 雷雲（雲の ふちが 光る）＋ 雷（2コマ目から 1回）
        n1, g1x, g1y = cloud('c1', cx, cy, 1.3, .4, (40, 10))
        dens = smoothstep(.36, .8, n1)
        img = img * (1 - .85 * dens)[..., None] + (dens * (1 - dens) * 4 * (core * 1.2 + mid))[..., None] * np.array([.8, .45, 1.3]) * .6
        f = int(round(u * FPS))
        if 1 <= f <= 3:
            inten = (1.0, .6, .25)[f - 1]
            core_ = np.zeros((H, W), np.float32)
            rs = np.random.default_rng(900 + k)
            for j in range(3):
                a0 = rs.uniform(0, 6.28)
                p0 = np.array([cx, cy]) + np.array([math.cos(a0), math.sin(a0)]) * W * .3
                p1 = bolt_dir_end(p0, np.array([math.cos(a0), math.sin(a0)]))
                P = zig(rs, [p0, p1], .2, 6)
                poly(core_, P, inten, 2.4 * S)
            img = img + core_[..., None] * np.array([3.0, 2.6, 4.0]) + blur(core_, 5 * S)[..., None] * np.array([1.0, .4, 2.2])
    if kind == 'gold':                                                           # きらめき（小さい 十字：2コマずつ）
        f = int(round(u * FPS))
        st = np.zeros((H, W), np.float32)
        for i in range(40):
            if rng.integers(0, 6) not in (f, f + 1):
                continue
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            Ls = rng.uniform(10, 26) * S
            cv2.line(st, (int((x - Ls) * 16), int(y * 16)), (int((x + Ls) * 16), int(y * 16)), 1.0, max(1, int(S)), cv2.LINE_AA, shift=4)
            cv2.line(st, (int(x * 16), int((y - Ls) * 16)), (int(x * 16), int((y + Ls) * 16)), 1.0, max(1, int(S)), cv2.LINE_AA, shift=4)
        img = img + (st + blur(st, 2 * S) * 2)[..., None] * np.array([2.2, 1.6, .7])
    img = img + m[..., None] * ln
    img = img * (.6 + .4 * (1 - smoothstep(.35, 1.1, r)))[..., None]            # まわりは 暗く
    return img


def cut_sparks(k, u, cx, cy):
    """細切れ k の 火花（ロゴの まわりから 外へ とぶ 筋）→ 線形の 色"""
    C = CUTS[k]
    rng = np.random.default_rng(700 + k)
    m = np.zeros((H, W), np.float32)
    for i in range(36):                                                         # 少なめ・細め（火花が 通る 点の 明るさの 上げ下げを ふやさない：16.6）
        a = rng.uniform(0, 6.28); v = rng.uniform(1000, 3400) * S; r0 = rng.uniform(.12, .3) * W
        b = rng.uniform(.4, .8); th_ = max(1, int(round(rng.uniform(1.0, 1.8) * S)))
        p1 = r0 + v * (u + .5 / FPS); p0 = max(r0, p1 - v * .035)
        ca_, sa_ = math.cos(a), math.sin(a)
        cv2.line(m, (int((cx + ca_ * p0) * 16), int((cy + sa_ * p0) * 16)), (int((cx + ca_ * p1) * 16), int((cy + sa_ * p1) * 16)), float(b), th_, cv2.LINE_AA, shift=4)
    c1 = np.array(C['c1'], np.float32)
    tint = c1 / c1.max()
    return m[..., None] * (tint * 1.6 + .5) + blur(m, 3 * S)[..., None] * tint * .8


def cut_frame(lam, work, fi, seed=811):
    """細切れの 1コマ：カットごとに 色・大きさ・向き・背景が ちがう ど！！！的中（はじめの コマで たたきつけ → ゆっくり ずれる）"""
    k = min(NCUT - 1, int((lam - C0) / CUT_LEN + 1e-6))
    C = CUTS[k]
    u = lam - (C0 + k * CUT_LEN)
    cx, cy = C['at'][0] * W, C['at'][1] * H
    col, A, (x0, y0, x1, y1) = cut_layer(k, work)
    colF = np.zeros((H, W, 3), np.float32); AF = np.zeros((H, W), np.float32)
    colF[y0:y1, x0:x1] = col; AF[y0:y1, x0:x1] = A
    img = cut_bg(k, u, cx, cy)                                                   # カットの 中で ロゴは 動かさない（ふちが 1秒に 何回も 明るく 暗く ならない：16.6）
    img = img * (1 - np.clip(AF, 0, 1)[..., None]) + colF
    img = img + star_glints(colF, AF) * .7
    img = img + cut_sparks(k, u, cx, cy)
    first = u < .5 / FPS
    img = bloom(img, 1.0)
    out = finish(img, seed + fi, vig=.5, ca=.004 + (.01 if first else 0.0))
    return np.clip(out, 0, 1)


def render_logo(work, i0, i1):
    a, b = int(round(HOOF * FPS)), NF
    for i in range(max(i0, a), min(i1, b)):
        if os.path.exists(frame_path(work, i)):
            continue
        lam = round(i / FPS - HOOF, 6)                                          # 2.0999… → 2.1（区切りの 秒と そろえる）
        save_png(logo_frame(lam, work, i), frame_path(work, i))
        print('logo', i, flush=True)


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


def render_black(work, i0, i1):
    """はじめの 黒（押した 瞬間の プチュン（CSS）の 下・真っ暗 0.8秒）"""
    for i in range(max(i0, 0), min(i1, int(round(BLACK * FPS)))):
        if not os.path.exists(frame_path(work, i)):
            save_png(np.zeros((H, W, 3), np.float32), frame_path(work, i))


def render_face(work, i0, i1):
    """顔の コマ（3D は はじめ 2コマに 1回・あいだの コマは となりの 2つを まぜる。動きが 速い 1.4秒 から は 毎コマ）"""
    rd = os.path.join(work, '_r'); os.makedirs(rd, exist_ok=True)
    cache = {}
    a0 = int(round(BLACK * FPS))

    def R_of(j):
        if j in cache:
            return cache[j]
        tj = j / FPS - BLACK
        pre = os.path.join(rd, f'face4_{j:03d}')
        R = load_r(pre, W, H, ('rgb', 'a'))
        if R is None:
            R = face_render(face_state(tj), pre)
            drop_r(pre, ('d', 'n', 'm', 'ao'))                                         # 使わない ものは 消す（場所を とる）
        cache[j] = R
        for k in list(cache):
            if k < j - 4:
                del cache[k]
                drop_r(os.path.join(rd, f'face4_{k:03d}'), ('rgb', 'a'))
        return R
    nface = int(round(FACE * FPS))
    for i in range(max(i0, a0), min(i1, nface)):
        if os.path.exists(frame_path(work, i)):
            continue
        t = i / FPS - BLACK
        if (i - a0) % 2 == 0 or t >= 1.4 or i + 1 >= nface:
            R = R_of(i)
        else:
            Ra, Rb = R_of(i - 1), R_of(i + 1)
            R = dict(rgb=(Ra['rgb'] + Rb['rgb']) * .5, a=(Ra['a'] + Rb['a']) * .5)
        M = face_marks(face_state(t))
        img = face_frame(t, R, M)
        save_png(img, frame_path(work, i))
        print('face', i, flush=True)


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
        render_black(work, i0, i1)
        render_face(work, i0, i1)
        render_hoof(work, i0, i1)
        render_logo(work, i0, i1)
