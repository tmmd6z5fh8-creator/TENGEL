"""神様的中 ② 金の 立体の 字（第4.48版）：1コマずつ 描く 絵。1170×2532（iPhone の 画面の 画素）・1秒 30コマ
   まさちゃん「じゃあ次のシーン！この感じの金ピカ、文字に立体感を持たせて、動きもこの感じ！ ファイルは画像46枚入ってるよ！
   このシーンは神様的中の三個めの動画で送ったシーン！」
   → 送ってくれた コマは 見るだけ（描き写さない・字・形・構図・動きの 組み立ては 姫の オリジナル）。
     字は Dela Gothic One（アプリに 入れて いる フォント）を 本当の 立体（前の 面・ふちの 面取り・うしろへの 厚い 厚み）に して、
     カメラから 見た 形（遠近）で 描く。金は まわりの 光の 映りこみ（金の 空：上は まぶしい 金・地平の こい 線・下は だいだいの 金・たての 光の 帯）
   流れ（0秒＝② の はじめ＝押して から 1.6秒）：
     0〜0.24秒 白が ひく → 0〜0.48秒「万馬券（きせき）」ななめから 大きく（ゆっくり 回りこむ）
     0.48〜1.22秒「天眼（テンゲル）」反対の ななめから（ゆっくり 寄る）→ 1.06〜1.52秒 白
     1.22秒〜 4行の 文「万馬券（きせき）は／偶然にあらず／天眼（テンゲル）が導く／必然なり」が 手前で ふわっと おちつく → 光が 2回 すべる → 3.24〜3.44秒 白（③ へ）
   python3 flat/kami_film2.py <出力フォルダ> [コマ番号（1〜）…]  → f001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami_art as KA
import kami_film as KF

S = 3.0
W, H = KF.W, KF.H
FPS = 30
N = 104                               # 3.44秒（③ の はじめの まっ白まで）
SSA = 2                               # 立体の 字は 2倍で 描いて もどす（ふちを なめらかに）
FOCAL = 1500.0                        # カメラ（絵の 画素：広い 角度で 遠近を 強く）
ENV_R = 2600.0                        # 映りこみの 空までの きょり（1000 単位：字の 場所で 映りこみが かわる）
SIDE_TINT = np.float32([1.0, .74, .38])   # 側面の 色み（こい 金・茶色）
CXS, CYS = W / 2, H / 2

# ---------------------------------------------------------------- 時刻（② の はじめが 0）
TT = dict(WIN=(0.0, .06, .24),                 # 白（まっ白 → 消える）
          CU1=(0.0, .5), CU2=(.48, 1.24),
          WB=(1.06, 1.2, 1.28, 1.52),          # 白（寄り → 4行の 文）
          TXT=1.22, SHINE=(1.95, 2.85),        # 4行の 文・光が すべる
          WC=(3.24, 3.38, 3.44))               # 白（③ へ）


def smoothstep(e0, e1, x):
    return KF.smoothstep(e0, e1, x)


def sstep(e0, e1, x):
    return KF.sstep(e0, e1, x)


def ease_out(u):
    return KF.ease_out(u)


# ---------------------------------------------------------------- 金の 映りこみ（まわりの 光：正距円筒の 絵）
ENV_H, ENV_W = 256, 512


def env_map():
    """まわりの 光（金）：たて＝上（+90°）→ 下（-90°）・よこ＝向き（-180°〜180°：0＝カメラの 前・±180＝カメラの うしろ）→ RGB（1 より 明るい 所 あり）"""
    def f():
        el = np.linspace(90, -90, ENV_H, dtype=np.float32)[:, None] * np.ones((1, ENV_W), np.float32)
        az = np.linspace(-180, 180, ENV_W, endpoint=False, dtype=np.float32)[None, :] * np.ones((ENV_H, 1), np.float32)
        stops = ((-90, (40, 18, 2)), (-60, (96, 46, 4)), (-30, (200, 120, 22)), (-12, (255, 196, 70)), (-4, (226, 150, 34)),
                 (0, (70, 34, 4)), (5, (120, 66, 8)), (12, (255, 206, 90)), (30, (255, 232, 140)), (55, (255, 246, 208)), (90, (255, 250, 232)))
        xs = np.array([s for s, _ in stops], np.float32)
        cs = np.array([c for _, c in stops], np.float32) / 255
        col = np.stack([np.interp(el, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)
        nz = KA.fbm(ENV_H, ENV_W, 8, 901, 4, .55)
        col *= (.82 + .36 * nz)[..., None]

        def spot(a0, e0, sa, se, g):
            d = np.degrees(np.angle(np.exp(1j * np.radians(az - a0))))
            return np.exp(-(d / sa) ** 2 - ((el - e0) / se) ** 2) * g
        hi = spot(150, 38, 26, 18, 1.4) + spot(-150, 52, 18, 12, 1.0)
        for a0, wd, g in ((118, 4.0, 1.5), (172, 2.5, 1.3), (-134, 5.0, 1.2), (-100, 3.0, 1.1), (60, 6.0, .8), (-40, 5.0, .7)):
            d = np.degrees(np.angle(np.exp(1j * np.radians(az - a0))))
            hi = hi + np.exp(-(d / wd) ** 2) * smoothstep(-6, 14, el) * (1 - smoothstep(60, 85, el)) * g
        col = col + np.float32([1.0, .95, .78])[None, None, :] * hi[..., None]
        return col.astype(np.float32)
    return KF.cache('env2', f)


def env_lookup(rv, rot=0.0):
    """映りこみの 向き rv（…×3：カメラ：x 右・y 下・z 前）→ 色"""
    env = env_map()
    x, y, z = rv[..., 0], rv[..., 1], rv[..., 2]
    el = np.degrees(np.arcsin(np.clip(-y, -1, 1)))
    az = np.degrees(np.arctan2(x, z)) + rot
    u = ((az + 180) % 360) / 360 * ENV_W
    v = np.clip((90 - el) / 180 * (ENV_H - 1), 0, ENV_H - 1.001)
    u0 = np.floor(u).astype(np.int32)
    v0 = np.floor(v).astype(np.int32)
    fu = (u - u0).astype(np.float32)[..., None]
    fv = (v - v0).astype(np.float32)[..., None]
    u0 %= ENV_W
    u1 = (u0 + 1) % ENV_W
    v1 = np.minimum(v0 + 1, ENV_H - 1)
    a = env[v0, u0] * (1 - fu) + env[v0, u1] * fu
    b = env[v1, u0] * (1 - fu) + env[v1, u1] * fu
    return a * (1 - fv) + b * fv


# ---------------------------------------------------------------- 立体の 字（前の 面・面取り・側面）
def build_obj(lines, box, k, depth, bevel_em=.05, pad_em=.12):
    """lines＝[(字の items, ふりがなの items)]（kami_art の 1000 単位）・box：箱（1000 単位）・k：1 単位あたりの 画素・depth：厚み（1000 単位）→ 立体の 字：
       前の 面（字の 形・面取りの 向き）と 側面（ふちの 線の きれはし・外向き・厚み）。座標は 1000 単位・字の まん中が 0"""
    pad = int(pad_em * 1000 * k)
    main = KA.mask([it for items, _ in lines for it in items], box, k, pad)
    has_ruby = any(r for _, r in lines)
    ruby = KA.mask([it for _, ritems in lines for it in ritems], box, k, pad) if has_ruby else np.zeros_like(main)
    Ht, Wt = main.shape
    cx_px = (box[2] - box[0]) / 2 * k + pad
    cy_px = (box[3] - box[1]) / 2 * k + pad
    alpha = np.maximum(main, ruby).astype(np.float32)

    def height(m, em_px):
        if m.max() < .5:
            return np.zeros_like(m, dtype=np.float32)
        d = KA.dist_in(m)
        w = bevel_em * em_px
        h = w * .75 * KA.bevel(d, w)
        g = np.exp(-((d - w * 1.25) / (w * .18)) ** 2) * w * .05          # みぞ（面取りと 面の さかい）
        return (h - g).astype(np.float32)
    em_px = 1000 * k
    h = height(main, em_px) + height(ruby, em_px * KA.RUBY)
    h = cv2.GaussianBlur(h, (0, 0), max(.6, .0025 * em_px))
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, -np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    segs = []
    for m, dep in ((main, depth), (ruby, depth * .55)):
        if m.max() < .5:
            continue
        b = (m > .5).astype(np.uint8)
        cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            if len(c) < 6:
                continue
            c = cv2.approxPolyDP(c, .7, True)[:, 0, :].astype(np.float64)
            if len(c) < 3:
                continue
            p0 = c
            p1 = np.roll(c, -1, axis=0)
            dv = p1 - p0
            L = np.hypot(dv[:, 0], dv[:, 1]) + 1e-9
            nx, ny = dv[:, 1] / L, -dv[:, 0] / L
            mid = (p0 + p1) / 2
            tx = np.clip(np.round(mid[:, 0] + nx * 2.0).astype(int), 0, Wt - 1)
            ty = np.clip(np.round(mid[:, 1] + ny * 2.0).astype(int), 0, Ht - 1)
            ins = b[ty, tx] > 0
            nx = np.where(ins, -nx, nx)
            ny = np.where(ins, -ny, ny)
            segs.append(np.stack([p0[:, 0], p0[:, 1], p1[:, 0], p1[:, 1], nx, ny, np.full(len(c), dep)], 1))
    segs = np.concatenate(segs, 0)
    # キラッの 場所の 候補（面取りの 上：ばらばらに）
    d_all = KA.dist_in(alpha)
    cand = np.argwhere((d_all > 1.5) & (d_all < bevel_em * em_px * .9))
    rng = np.random.default_rng(int(k * 1000) + len(segs))
    pick = []
    if len(cand):
        for i in rng.permutation(len(cand)):
            y_, x_ = cand[i]
            if all((x_ - a) ** 2 + (y_ - b) ** 2 > (.5 * em_px) ** 2 for a, b in pick):
                pick.append((x_, y_))
            if len(pick) >= 14:
                break
    segs[:, 0:4:2] = (segs[:, 0:4:2] - cx_px) / k
    segs[:, 1:4:2] = (segs[:, 1:4:2] - cy_px) / k
    return dict(alpha=alpha, n=n.astype(np.float32), k=k, c=(cx_px, cy_px), segs=segs, shape=(Ht, Wt),
                size=(box[2] - box[0], box[3] - box[1]), glints=np.array(pick, np.float64))


def rot(yaw, pitch, roll):
    """回転（度）：yaw＝たての 軸（＋で 右が おく）・pitch＝横の 軸（＋で 上が おく）・roll＝前の 軸"""
    a, b, c = math.radians(yaw), math.radians(pitch), math.radians(roll)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def project(P):
    """カメラの 点（…×3）→ 画面の 画素（…×2）"""
    z = np.maximum(P[..., 2], 1e-3)
    return np.stack([FOCAL * P[..., 0] / z + CXS, FOCAL * P[..., 1] / z + CYS], -1)


def draw_obj(obj, R, Tv, env_rot=0.0, side_gain=1.0, face_gain=1.0, shine=None):
    """立体の 字を 1コマ 描く → (premultiplied RGBA（画面の 画素 × SSA）の 箱の 絵, 箱の 左上（画面×SSA）) か None。
       側面（うしろ → 前の 順）→ 前の 面（面取りの 映りこみ）"""
    k = obj['k']
    segs = obj['segs']
    Wc, Hc = W * SSA, H * SSA
    # ---- 側面（3つの 厚みの 段：前ほど 明るい）
    p0 = np.stack([segs[:, 0], segs[:, 1], np.zeros(len(segs))], 1)
    p1 = np.stack([segs[:, 2], segs[:, 3], np.zeros(len(segs))], 1)
    nl = np.stack([segs[:, 4], segs[:, 5], np.zeros(len(segs))], 1)
    dep = segs[:, 6]
    Nc = nl @ R.T
    polys, cols, zs = [], [], []
    edges = [0.0, .04, .09, .15, .23, .33, .45, .58, .72, .86, 1.0]
    for j in range(len(edges) - 1):
        f0, f1 = edges[j], edges[j + 1]
        gk = 1.28 * (1 - (f0 + f1) / 2) ** 1.25 + .3
        a = p0 + np.stack([np.zeros(len(segs)), np.zeros(len(segs)), dep * f0], 1)
        b = p1 + np.stack([np.zeros(len(segs)), np.zeros(len(segs)), dep * f0], 1)
        c = p1 + np.stack([np.zeros(len(segs)), np.zeros(len(segs)), dep * f1], 1)
        d = p0 + np.stack([np.zeros(len(segs)), np.zeros(len(segs)), dep * f1], 1)
        quad = np.stack([a, b, c, d], 1) @ R.T + Tv                     # n×4×3
        cen = quad.mean(1)
        vis = np.einsum('ij,ij->i', Nc, -cen) > 0
        if not vis.any():
            continue
        V = cen / np.linalg.norm(cen, axis=1, keepdims=True)
        rv = V - 2 * np.einsum('ij,ij->i', V, Nc)[:, None] * Nc
        rv = rv + (cen - Tv) / ENV_R
        rv /= np.linalg.norm(rv, axis=1, keepdims=True)
        col = env_lookup(rv, env_rot) * (.5 * gk * side_gain) * SIDE_TINT
        pr = project(quad) * SSA
        polys.append(pr[vis])
        cols.append(col[vis])
        zs.append(cen[vis, 2])
    out = np.zeros((Hc, Wc, 3), np.float32)
    cov = np.zeros((Hc, Wc), np.float32)
    if polys:
        P = np.concatenate(polys, 0)
        C = np.concatenate(cols, 0)
        Z = np.concatenate(zs, 0)
        order = np.argsort(-Z)
        for i in order:
            q = np.round(P[i] * 4).astype(np.int32)
            if q[:, 0].max() < 0 or q[:, 1].max() < 0 or q[:, 0].min() > Wc * 4 or q[:, 1].min() > Hc * 4:
                continue
            cv2.fillConvexPoly(out, q, C[i].tolist(), cv2.LINE_8, shift=2)
            cv2.fillConvexPoly(cov, q, 1.0, cv2.LINE_8, shift=2)
    if polys:
        out = cv2.GaussianBlur(out, (0, 0), .9)
        cov = cv2.GaussianBlur(cov, (0, 0), .6)
    # ---- 前の 面（面取り：向きごとの 映りこみ）
    Ht, Wt = obj['shape']
    cx, cy = obj['c']
    # 面の 絵の 画素 (x, y) → 字の 座標 (u, v) → カメラ → 画面
    Hm = np.array([[1 / k, 0, -cx / k], [0, 1 / k, -cy / k], [0, 0, 1]])
    Mcam = np.column_stack([R[:, 0], R[:, 1], Tv])
    Kc = np.array([[FOCAL * SSA, 0, CXS * SSA], [0, FOCAL * SSA, CYS * SSA], [0, 0, 1]])
    Hs = Kc @ Mcam @ Hm
    yy, xx = np.mgrid[0:Ht, 0:Wt].astype(np.float32)
    u = (xx - cx) / k
    v = (yy - cy) / k
    Pc = u[..., None] * R[:, 0] + v[..., None] * R[:, 1] + Tv
    Vv = Pc / np.linalg.norm(Pc, axis=-1, keepdims=True)
    Nn = obj['n'] @ R.T
    rv = Vv - 2 * np.sum(Vv * Nn, -1, keepdims=True) * Nn
    rv = rv + (Pc - Tv) / ENV_R                                     # 映りこみは 字の 場所でも かわる（近い 空）
    rv /= np.linalg.norm(rv, axis=-1, keepdims=True)
    fc = env_lookup(rv, env_rot) * face_gain
    if shine is not None:                                          # 光が すべる（ななめの 光の 帯）
        s_pos, s_w = shine
        band = np.exp(-(((u + v * .6) / 1000 - s_pos) / s_w) ** 2)
        fc = fc + band[..., None] * np.float32([1.0, .96, .82]) * .9
    al = obj['alpha']
    face = np.dstack([fc * al[..., None], al]).astype(np.float32)
    fw = cv2.warpPerspective(face, Hs, (Wc, Hc), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = fw[..., 3:4]
    rgb = out * cov[..., None]
    rgb = fw[..., :3] + rgb * (1 - a)
    alpha = np.clip(a[..., 0] + cov * (1 - a[..., 0]), 0, 1)
    # 外の こい 茶色の ふち（金の 空から 字を うかせる）
    ring = np.clip(KA.grow(alpha, 2.2 * S * SSA / 2) - alpha, 0, 1)
    rgb = rgb + np.float32([.12, .055, .008]) * ring[..., None]
    alpha = np.clip(alpha + ring, 0, 1)
    return np.dstack([rgb, alpha]), Hs


def glints(img, obj, Hs, t, seed):
    """キラッ（面取りの 上の 小さな 光の 星：1つずつ ふわっと 出て 消える）"""
    g = obj['glints']
    if len(g) == 0:
        return
    pts = np.column_stack([g, np.ones(len(g))]) @ Hs.T
    xy = pts[:, :2] / pts[:, 2:3] / SSA
    rng = random.Random(seed)
    m = np.zeros((H, W), np.float32)
    for (x, y) in xy:
        t0 = rng.uniform(-.2, 3.4)
        dur = rng.uniform(.28, .45)
        if not (t0 <= t <= t0 + dur) or not (0 <= x < W and 0 <= y < H):
            continue
        e = math.sin(math.pi * (t - t0) / dur)
        L = rng.uniform(26, 44) * S * (.6 + .4 * e)
        star = np.zeros((H, W), np.float32)
        for ang in (0.0, math.pi / 2, math.pi / 4, -math.pi / 4):
            l = L if ang in (0.0, math.pi / 2) else L * .45
            cv2.line(m, (int((x - l * math.cos(ang)) * 4), int((y - l * math.sin(ang)) * 4)),
                     (int((x + l * math.cos(ang)) * 4), int((y + l * math.sin(ang)) * 4)), float(e * (1.0 if l == L else .6)), 2, cv2.LINE_AA, shift=2)
        cv2.circle(m, (int(x * 4), int(y * 4)), int(5 * S * 4 * e) + 1, float(e), -1, cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, 1, 1), 1.2), (1.5, (1, .92, .7), 1.0), (6, (1, .75, .3), .5)))


def downsample(img):
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)


# ---------------------------------------------------------------- 字・カメラの 動き
def objects():
    """立体の 字（1回だけ 作る）：万馬券（きせき）・天眼（テンゲル）・4行の 文"""
    def f():
        it, ri, box = KA.line_layout('万馬券', 0.0, ('きせき', 0, 3))
        o1 = build_obj([(it, ri)], box, .62, 300.0)
        it, ri, box = KA.line_layout('天眼', 0.0, ('テンゲル', 0, 2))
        o2 = build_obj([(it, ri)], box, .72, 300.0)
        lines, box = KA.layout_text()
        o3 = build_obj(lines, box, .42, 230.0, bevel_em=.055)
        return o1, o2, o3
    return KF.cache('objs2', f)


# カメラ（字の 向きと 場所）：(秒, yaw, pitch, roll, x, y, z)（x, y, z は 1000 単位・z は カメラからの きょり）
POSE1 = ((0.0, -40.0, 17.0, -13.0, 230.0, 140.0, 3350.0), (.5, -29.0, 12.0, -8.0, 90.0, 60.0, 2850.0))
POSE2 = ((.48, 36.0, 11.0, 10.0, -200.0, 120.0, 2900.0), (1.24, 23.0, 7.0, 5.0, -70.0, 40.0, 2450.0))


def txt_z():
    """4行の 文が 画面の はばの 9割に なる きょり"""
    o3 = objects()[2]
    return FOCAL * o3['size'][0] / (.9 * W)


def pose_txt(t):
    """4行の 文：白の 中から 手前で ふわっと おちつく → ゆっくり 少しだけ"""
    z0 = txt_z()
    u = ease_out((t - TT['TXT']) / .55)
    v = sstep(TT['TXT'] + .4, TT['WC'][2], t)
    yaw = -6.0 * (1 - u) + (-1.5 + 3.0 * v)
    pitch = 20.0 * (1 - u) + 7.0 - 2.0 * v
    z = z0 * (.78 + .22 * u) * (1 - .04 * v)
    cy = (436 - 422) * S * z / FOCAL
    return yaw, pitch, 0.0, 0.0, cy, z


def lerp_pose(P, t):
    (t0, *a), (t1, *b) = P
    u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    u = u * u * (3 - 2 * u) * .35 + u * .65              # ほぼ 一定の 速さ（はじめと おわりを 少し やわらかく）
    return [x + (y - x) * u for x, y in zip(a, b)]


def white_amt(t):
    w0, w1, w2 = TT['WIN']
    a = 1.0 - sstep(w1, w2, t) if t <= w2 else 0.0
    b0, b1, b2, b3 = TT['WB']
    if b0 <= t <= b3:
        a = max(a, sstep(b0, b1, t) if t < b2 else 1 - sstep(b2, b3, t))
    c0, c1, c2 = TT['WC']
    if t >= c0:
        a = max(a, sstep(c0, c1, t))
    return a


def sky_bg():
    return KF.cache('sky2', lambda: (KA.sky(W, H).astype(np.float32) * .86))


def dust(img, t):
    """金の ちり（ゆっくり ただよう・ときどき きらっ）"""
    m = np.zeros((H, W), np.float32)
    rng = random.Random(77)
    for _ in range(70):
        x0, y0 = rng.uniform(0, 390), rng.uniform(0, 844)
        vx, vy = rng.uniform(-14, 14), rng.uniform(-40, -10)
        r = rng.uniform(.6, 1.8)
        ph = rng.uniform(0, 6.3)
        fq = rng.uniform(.8, 1.6)
        x, y = (x0 + vx * t) % 390, (y0 + vy * t) % 844
        a = .35 + .65 * (.5 + .5 * math.sin(ph + 2 * math.pi * fq * t))
        cv2.circle(m, (int(x * S * 4), int(y * S * 4)), max(1, int(r * S * 4)), float(a), -1, cv2.LINE_AA, shift=2)
    KF.glow_add(img, m, ((0, (1, .95, .8), .9), (2, (1, .8, .35), .6), (7, (1, .6, .15), .35)))


def frame(fi):
    t = fi / FPS
    o1, o2, o3 = objects()
    img = sky_bg().copy()
    lay, gl = None, None
    if t < TT['CU1'][1] and t < TT['CU2'][0]:
        yaw, pitch, roll, x, y, z = lerp_pose(POSE1, t)
        lay, Hs = draw_obj(o1, rot(yaw, pitch, roll), np.array([x, y, z]), env_rot=-20 + 40 * t)
        gl = (o1, Hs, 11)
    elif t < TT['TXT'] + .02:
        yaw, pitch, roll, x, y, z = lerp_pose(POSE2, t)
        lay, Hs = draw_obj(o2, rot(yaw, pitch, roll), np.array([x, y, z]), env_rot=10 - 30 * (t - TT['CU2'][0]))
        gl = (o2, Hs, 12)
    if t >= TT['TXT']:
        yaw, pitch, roll, x, y, z = pose_txt(t)
        sh = None
        for s0 in TT['SHINE']:
            if s0 - .05 <= t <= s0 + .7:
                q = (t - s0) / .65
                sh = (-3.6 + 7.2 * ease_out(q) * 1.0, .45)
        lay, Hs = draw_obj(o3, rot(yaw, pitch, roll), np.array([x, y, z]), env_rot=-8 + 6 * (t - TT['TXT']), shine=sh)
        gl = (o3, Hs, 13)
    if lay is not None:
        lay = downsample(lay)
        img = lay[..., :3] + img * (1 - lay[..., 3:4])
        glints(img, gl[0], gl[1], t, gl[2])
    dust(img, t)
    img = KF.bloom(img)
    w = white_amt(t)
    if w > 0:
        img = img * (1 - w) + np.float32([1.0, 1.0, 1.0]) * w * 1.15 + img * w * .15
    out = KF.tonemap(img)
    return (out * 255 + .5).astype(np.uint8)


def main(out, which=None):
    os.makedirs(out, exist_ok=True)
    for fi in (which or range(N)):
        im = frame(fi)
        cv2.imwrite(os.path.join(out, f'f{fi + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('f', fi + 1, flush=True)


# ---------------------------------------------------------------- ためし
def _test(out):
    os.makedirs(out, exist_ok=True)
    it, ri, box = KA.line_layout('万馬券', 0.0, ('きせき', 0, 3))
    obj = build_obj([(it, ri)], box, .6, 260.0)
    bg = KF.cache('sky2', lambda: KA.sky(W, H).astype(np.float32))
    R = rot(-32, 14, -10)
    Tv = np.array([120.0, -60.0, 3900.0])
    lay, Hs = draw_obj(obj, R, Tv)
    lay = downsample(lay)
    img = bg * .8 * (1 - lay[..., 3:4]) + lay[..., :3]
    img = KF.bloom(img)
    o = KF.tonemap(img)
    cv2.imwrite(os.path.join(out, 'test.png'), cv2.cvtColor((o * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    if sys.argv[2:3] == ['test']:
        _test(sys.argv[1])
    else:
        main(sys.argv[1], [int(v) - 1 for v in sys.argv[2:]] or None)
