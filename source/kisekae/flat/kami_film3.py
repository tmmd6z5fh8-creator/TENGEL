"""神様的中 ③ 神様的中・おめでとう御座います！（第4.48版）：1コマずつ 描く 絵。1170×2532（iPhone の 画面の 画素）・1秒 30コマ
   まさちゃん「じゃあ最後のシーンいくね！ここは、GODの文字のところを、神様的中、GAMEの文字のところを、おめでとう御座います！にして！
   ファイルは全部で78枚あるよ！」
   → 送ってくれた コマは 見るだけ（描き写さない・字・形・構図・動きの 組み立ては 姫の オリジナル）。
     字は Dela Gothic One（アプリに 入れて いる フォント）を 本当の 立体（前の 面・まるい 金の ふち・うしろへの 厚い 厚み）に して、カメラから 見た 形（遠近）で 描く。
     字の 面は 夕やけの 金（上は まぶしい 金 → だいだい → 波の ような こい 赤の 線 → 赤 → 下は 明るい だいだい）・ふちは まわりの 光の 映りこみ（金）。
     金の 粒は 本当の 立体（ごつごつ した 金の かたまり：面ごとに 映りこみ）が 回りながら 手前へ とんで くる（近い 粒は ぼける・速い 粒は ぶれる）。
   流れ（0秒＝③ の はじめ＝② の おわりの まっ白）：
     白が ひく → 金の 粒が はじけて「神」の 寄り → 大きな 粒が 手前を 横切って「様」→ 金の 粒が はじけて「的」→ 大きな 粒が 横切って「中」
     → 金の 粒の 大爆発の 中に「神様／的中／おめでとう／御座います！」（ななめ）→ 正面へ 回りながら ひく（うしろに 金の 鳥居）→ 光が すべる → キラキラ
   画面 全体は 回さない・ゆらさない（動くのは 字と 金の 粒だけ・寄りは 横に ゆっくり）。点めつ：どの 1秒にも 3回 以下
   python3 flat/kami_film3.py <出力フォルダ> [コマ番号（1〜）…]  → f001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami_art as KA
import kami_film as KF
from cute_horse import svg_rgba

S = 3.0
W, H = KF.W, KF.H
FPS = 30
N = 126                               # 4.2秒
SSA = 2                               # 側面は 2倍で 描いて もどす
FOCAL = 1500.0                        # カメラ（絵の 画素）
ENV_R = 2600.0                        # 映りこみの 空までの きょり（1000 単位）
CXS, CYS = W / 2, H / 2

# ---------------------------------------------------------------- 時刻（③ の はじめが 0）
TT = dict(WIN=(0.0, .05, .3),                                          # 白（まっ白 → 消える）
          CU=((0.0, .55), (.55, 1.08), (1.08, 1.62), (1.62, 2.15)),    # 神・様・的・中 の 寄り
          BU=((0.0, 1, .55), (.5, 0, None), (1.05, 1, 1.62), (1.57, 0, None), (2.1, 2, None)),
          # 金の 粒（時刻・強さ 0＝大きな 粒が 手前を 横切る（光らない）・1＝はじける・2＝いちばん 大きい・寄りが かわる 時に 消す 時刻）
          LOGO=2.15, TURN=(2.15, 3.0),                                 # 神様／的中／おめでとう／御座います！（ななめ → 正面へ 回りながら ひく）
          SHINE=(3.1, 3.75))                                           # 光が すべる


def smoothstep(e0, e1, x):
    return KF.smoothstep(e0, e1, x)


def sstep(e0, e1, x):
    return KF.sstep(e0, e1, x)


def ease_out(u):
    return KF.ease_out(u)


# ---------------------------------------------------------------- 金の 映りこみ（夕やけの 金：正距円筒の 絵）
ENV_H, ENV_W = 256, 512


def env_map():
    """まわりの 光：たて＝上（+90°）→ 下（-90°）・よこ＝向き（0＝カメラの 前・±180＝カメラの うしろ）→ RGB（1 より 明るい 所 あり）"""
    def f():
        el = np.linspace(90, -90, ENV_H, dtype=np.float32)[:, None] * np.ones((1, ENV_W), np.float32)
        az = np.linspace(-180, 180, ENV_W, endpoint=False, dtype=np.float32)[None, :] * np.ones((ENV_H, 1), np.float32)
        stops = ((-90, (16, 5, 1)), (-55, (56, 18, 3)), (-28, (150, 52, 8)), (-10, (232, 108, 18)), (-3, (255, 178, 64)),
                 (0, (255, 236, 170)), (3, (255, 176, 46)), (10, (220, 104, 16)), (22, (255, 164, 48)), (42, (255, 212, 118)),
                 (68, (255, 236, 184)), (90, (255, 246, 214)))
        xs = np.array([s for s, _ in stops], np.float32)
        cs = np.array([c for _, c in stops], np.float32) / 255
        col = np.stack([np.interp(el, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)
        nz = KA.fbm(ENV_H, ENV_W, 8, 903, 4, .55)
        col *= (.8 + .4 * nz)[..., None]

        def dang(a0):
            return np.degrees(np.angle(np.exp(1j * np.radians(az - a0))))
        hi = np.zeros_like(el)
        for a0, e0, sa, se, g in ((150, 34, 24, 16, 1.5), (-150, 50, 18, 12, 1.1), (35, 22, 14, 10, .7), (-60, 28, 16, 10, .6)):
            hi += np.exp(-(dang(a0) / sa) ** 2 - ((el - e0) / se) ** 2) * g
        for a0, wd, g in ((122, 4.0, 1.4), (168, 2.5, 1.2), (-132, 5.0, 1.1), (-98, 3.0, 1.0), (64, 6.0, .7), (-36, 5.0, .6)):
            hi += np.exp(-(dang(a0) / wd) ** 2) * smoothstep(-4, 16, el) * (1 - smoothstep(58, 84, el)) * g
        col = col + np.float32([1.0, .94, .76])[None, None, :] * hi[..., None]
        return col.astype(np.float32)
    return KF.cache('env3', f)


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


# 字の 面（夕やけの 金：上から まぶしい 金 → 金 → だいだい → 波の ような こい 赤の 線 → 赤 → 下は 明るい だいだい）
FACE = ((0.0, (255, 232, 140)), (.08, (255, 206, 64)), (.2, (255, 170, 30)), (.31, (255, 196, 70)), (.4, (248, 132, 18)),
        (.455, (212, 74, 8)), (.48, (112, 20, 3)), (.505, (200, 56, 8)), (.64, (184, 38, 6)), (.8, (214, 70, 10)), (.93, (250, 136, 34)),
        (1.0, (255, 186, 76)))
GOLD_TINT = np.float32([1.0, .86, .55])       # ふちの 金
SIDE_TINT = np.float32([1.0, .62, .26])       # 側面（こい 金 → こげ茶）


# ---------------------------------------------------------------- 立体の 字（前の 面の 地図・側面の 線）
def _normals(h):
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, -np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n.astype(np.float32)


def _segments(m, dep, Wt, Ht):
    """形の ふちの 線の きれはし：[x0, y0, x1, y1, 外向き nx, ny, 厚み]（絵の 画素）"""
    b = (m > .5).astype(np.uint8)
    cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
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
        out.append(np.stack([p0[:, 0], p0[:, 1], p1[:, 0], p1[:, 1], nx, ny, np.full(len(c), dep)], 1))
    return out


def make_obj(parts, k, cx, cy, Wt, Ht, glint_n=14, seed=1, style='stripe', extra=None):
    """parts＝[(形 0〜1, 面取りの はば（画素）, 厚み（1000 単位）, しまの 座標 0〜1 か None)]（どれも 同じ 大きさの 絵）。
       k：1 単位あたりの 画素・(cx, cy)：字の まん中（画素）。→ 立体（地図は 3段：細かい → あらい）"""
    alpha = np.zeros((Ht, Wt), np.float32)
    hgt = np.zeros((Ht, Wt), np.float32)
    rim = np.zeros((Ht, Wt), np.float32)
    sv = np.zeros((Ht, Wt), np.float32)
    segs = []
    for j, (m, w, dep, svm) in enumerate(parts):
        if m.max() < .5:
            continue
        d = KA.dist_in(m)
        h = w * .75 * KA.bevel(d, w)
        h -= np.exp(-((d - w * 1.2) / (w * .16)) ** 2) * w * .06          # みぞ（ふちと 面の さかい）
        sel = (m > .5) | (m > alpha)
        hgt = np.where(sel, hgt + h if j else h, hgt)                         # 2つめ からは 上に のせる（額の 字）
        rim = np.where(sel, 1 - smoothstep(w * .92, w * 1.3, d), rim)
        if svm is not None:
            sv = np.where(sel, svm, sv)
        alpha = np.maximum(alpha, m)
        segs += _segments(m, dep, Wt, Ht)
    hgt = cv2.GaussianBlur(hgt, (0, 0), max(.6, .0025 * 1000 * k))
    n = _normals(hgt)
    segs = np.concatenate(segs, 0)
    segs[:, 0:4:2] = (segs[:, 0:4:2] - cx) / k
    segs[:, 1:4:2] = (segs[:, 1:4:2] - cy) / k
    # キラッの 場所の 候補（ふちの 上：ばらばらに）
    cand = np.argwhere((rim > .6) & (alpha > .9))
    rng = np.random.default_rng(seed)
    pick = []
    em_px = 1000 * k
    if len(cand):
        for i in rng.permutation(len(cand))[:4000]:
            y_, x_ = cand[i]
            if all((x_ - a) ** 2 + (y_ - b) ** 2 > (.42 * em_px) ** 2 for a, b in pick):
                pick.append((x_, y_))
            if len(pick) >= glint_n:
                break
    lv = []
    m4 = np.dstack([alpha, alpha * n[..., 0], alpha * n[..., 1], alpha * sv]).astype(np.float32)     # alpha を かけて おく（ふちで まざっても くずれない）
    r2 = (alpha * rim).astype(np.float32)
    ex = (alpha * extra).astype(np.float32) if extra is not None else None
    kk, ccx, ccy = k, cx, cy
    for j in range(3):
        lv.append(dict(m4=m4, rim=r2, extra=ex, k=kk, c=(ccx, ccy)))
        h_, w_ = m4.shape[:2]
        m4 = cv2.resize(m4, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        r2 = cv2.resize(r2, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        if ex is not None:
            ex = cv2.resize(ex, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        kk *= (w_ // 2) / w_
        ccx, ccy = ccx * (w_ // 2) / w_, ccy * (h_ // 2) / h_
    gl = (np.array(pick, np.float64) - np.array([cx, cy])) / k if pick else np.zeros((0, 2))
    return dict(lv=lv, segs=segs, glints=gl, style=style)


def text_obj(lines, k, bevel_em=.06, depth=280.0, pad_em=.14, seed=1):
    """lines＝[(文字列, 大きさ, 下の 線（1000 単位・y 下向き）, 面取り（字の 大きさの 何倍）, 厚み（1000 単位）)]（まん中 そろえ）→ 立体"""
    rows = []
    for txt, s, base, bev, dep in lines:
        its, box, w = KA.run([(c, s) for c in txt], 0.0, base, -40.0)
        its = KA.shift_items(its, -w / 2, 0)
        box = (box[0] - w / 2, box[1], box[2] - w / 2, box[3])
        rows.append((its, box, s, bev, dep))
    box = KA.union_box(*[r[1] for r in rows])
    pad = int(pad_em * 1000 * k)
    Wt = int(np.ceil((box[2] - box[0]) * k + 2 * pad))
    Ht = int(np.ceil((box[3] - box[1]) * k + 2 * pad))
    yy = np.arange(Ht, dtype=np.float32)[:, None] * np.ones((1, Wt), np.float32)
    parts = []
    for its, b, s, bev, dep in rows:
        m = KA.mask(its, box, k, pad)
        m = m[:Ht, :Wt] if m.shape[0] >= Ht and m.shape[1] >= Wt else cv2.copyMakeBorder(m, 0, max(0, Ht - m.shape[0]), 0, max(0, Wt - m.shape[1]), cv2.BORDER_CONSTANT, value=0)[:Ht, :Wt]
        y0 = (b[1] - box[1]) * k + pad
        y1 = (b[3] - box[1]) * k + pad
        svm = (yy - y0) / max(1.0, y1 - y0)
        parts.append((m, bev * 1000 * s * k, dep, svm))
    cx = (0 - box[0]) * k + pad
    cy = ((box[1] + box[3]) / 2 - box[1]) * k + pad
    o = make_obj(parts, k, cx, cy, Wt, Ht, seed=seed)
    o['size'] = (box[2] - box[0], box[3] - box[1])
    o['ymid'] = (box[1] + box[3]) / 2
    return o


# ---------------------------------------------------------------- 立体を 1コマ 描く
def rot(yaw, pitch, roll):
    """回転（度）：yaw＝たての 軸（＋で 右が おく）・pitch＝横の 軸（＋で 上が おく）・roll＝前の 軸"""
    a, b, c = math.radians(yaw), math.radians(pitch), math.radians(roll)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def project(P):
    z = np.maximum(P[..., 2], 1e-3)
    return np.stack([FOCAL * P[..., 0] / z + CXS, FOCAL * P[..., 1] / z + CYS], -1)


def sides(obj, R, Tv, gain=1.0, env_rot=0.0):
    """側面（うしろ → 前の 順：前ほど 明るい 金・うしろは こげ茶）→ (色, おおい)（画面の 画素）"""
    segs = obj['segs']
    Wc, Hc = W * SSA, H * SSA
    p0 = np.stack([segs[:, 0], segs[:, 1], np.zeros(len(segs))], 1)
    p1 = np.stack([segs[:, 2], segs[:, 3], np.zeros(len(segs))], 1)
    nl = np.stack([segs[:, 4], segs[:, 5], np.zeros(len(segs))], 1)
    dep = segs[:, 6]
    Nc = nl @ R.T
    polys, cols, zs = [], [], []
    edges = [0.0, .015, .035, .06, .09, .125, .165, .21, .26, .32, .39, .47, .56, .66, .77, .88, 1.0]
    zero = np.zeros(len(segs))
    for j in range(len(edges) - 1):
        f0, f1 = edges[j], edges[j + 1]
        fm = (f0 + f1) / 2
        gk = 1.45 * (1 - fm) ** 2.2 + .16
        a = p0 + np.stack([zero, zero, dep * f0], 1)
        b = p1 + np.stack([zero, zero, dep * f0], 1)
        c = p1 + np.stack([zero, zero, dep * f1], 1)
        d = p0 + np.stack([zero, zero, dep * f1], 1)
        quad = np.stack([a, b, c, d], 1) @ R.T + Tv
        cen = quad.mean(1)
        vis = np.einsum('ij,ij->i', Nc, -cen) > 0
        if not vis.any():
            continue
        V = cen / np.linalg.norm(cen, axis=1, keepdims=True)
        rv = V - 2 * np.einsum('ij,ij->i', V, Nc)[:, None] * Nc
        rv = rv + (cen - Tv) / ENV_R
        rv /= np.linalg.norm(rv, axis=1, keepdims=True)
        col = env_lookup(rv, env_rot) * (.5 * gk * gain) * SIDE_TINT
        if j == len(edges) - 2:                        # うしろの はしの 金の 線
            col = col * .6 + np.float32([.5, .32, .08]) * gain
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
        for i in np.argsort(-Z):
            q = np.round(P[i] * 4).astype(np.int32)
            if q[:, 0].max() < 0 or q[:, 1].max() < 0 or q[:, 0].min() > Wc * 4 or q[:, 1].min() > Hc * 4:
                continue
            cv2.fillConvexPoly(out, q, C[i].tolist(), cv2.LINE_8, shift=2)
            cv2.fillConvexPoly(cov, q, 1.0, cv2.LINE_8, shift=2)
        out = cv2.GaussianBlur(out, (0, 0), 1.3)
        cov = cv2.GaussianBlur(cov, (0, 0), .6)
    out = cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)
    cov = cv2.resize(cov, (W, H), interpolation=cv2.INTER_AREA)
    return out * cov[..., None], cov


def homography(L, R, Tv):
    k = L['k']
    cx, cy = L['c']
    Hm = np.array([[1 / k, 0, -cx / k], [0, 1 / k, -cy / k], [0, 0, 1]])
    Mcam = np.column_stack([R[:, 0], R[:, 1], Tv])
    Kc = np.array([[FOCAL, 0, CXS], [0, FOCAL, CYS], [0, 0, 1]])
    return Kc @ Mcam @ Hm


def pick_level(obj, Tv):
    """画面の 1画素 あたり 1〜2 の 細かさの 地図を えらぶ"""
    scr = FOCAL / max(Tv[2], 1.0)                     # 1 単位 あたりの 画面の 画素（まん中）
    for j, L in enumerate(obj['lv']):
        if L['k'] <= scr * 1.6 or j == len(obj['lv']) - 1:
            return j
    return 0


def face(obj, R, Tv, env_rot=0.0, gain=1.0, shine=None, tilt=0.0):
    """前の 面（ふち：映りこみの 金・面：夕やけの しま＋つや）→ (premultiplied 色, alpha, 字 → 画面 の 行列)"""
    L = obj['lv'][pick_level(obj, Tv)]
    Hs = homography(L, R, Tv)
    m4 = cv2.warpPerspective(L['m4'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    rw = cv2.warpPerspective(L['rim'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    ex = None
    if L['extra'] is not None:
        ex = cv2.warpPerspective(L['extra'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = m4[..., 0]
    idx = np.flatnonzero(a > .002)
    rgb = np.zeros((H * W, 3), np.float32)
    if len(idx):
        ys, xs = np.divmod(idx, W)
        al = a.ravel()[idx]
        nx = m4[..., 1].ravel()[idx] / np.maximum(al, 1e-3)
        ny = m4[..., 2].ravel()[idx] / np.maximum(al, 1e-3)
        sv = m4[..., 3].ravel()[idx] / np.maximum(al, 1e-3)
        rr = np.clip(rw.ravel()[idx] / np.maximum(al, 1e-3), 0, 1)
        nz = -np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        n = np.stack([nx, ny, nz], 1) @ R.T
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        d = np.stack([(xs - CXS) / FOCAL, (ys - CYS) / FOCAL, np.ones(len(idx))], 1)
        nP = R[:, 2]
        t = (nP @ Tv) / (d @ nP)
        P = d * t[:, None]
        V = d / np.linalg.norm(d, axis=1, keepdims=True)
        rv = V - 2 * np.sum(V * n, 1, keepdims=True) * n
        rv = rv + (P - Tv) / ENV_R
        rv /= np.linalg.norm(rv, axis=1, keepdims=True)
        envc = env_lookup(rv, env_rot).astype(np.float32)
        gold = envc * GOLD_TINT * 1.05
        u = (P - Tv) @ R[:, 0]                               # 字の 横の 位置（1000 単位）
        if obj['style'] == 'stripe':
            w = sv + .016 * np.sin(u / 1000 * 2 * math.pi * 2.3 + 1.1 + tilt) + .008 * np.sin(u / 1000 * 2 * math.pi * 5.9 + .4)
            fc = KA.ramp(w, FACE)
            lum = envc @ np.float32([.3, .55, .15])
            fc = fc * (.58 + .36 * np.clip(lum, 0, 1.6))[:, None]
            fc = fc + (np.clip(lum - 1.0, 0, None) * .4)[:, None] * np.float32([1.0, .9, .7])
        else:                                                # 金（鳥居）：みがいた 金の 面
            fc = envc * GOLD_TINT * .82
            if ex is not None:                               # 額：こい 赤（金の 字は ふちの 金）
                pm = np.clip(ex.ravel()[idx] / np.maximum(al, 1e-3), 0, 1)
                lac = np.float32([.36, .04, .02]) * (.7 + .5 * np.clip(envc @ np.float32([.3, .55, .15]), 0, 1.5))[:, None]
                fc = fc * (1 - pm[:, None]) + lac * pm[:, None]
        col = gold * rr[:, None] + fc * (1 - rr[:, None])
        if shine is not None:                                # 光が すべる（ななめの 光の 帯）
            s_pos, s_w = shine
            v_ = (P - Tv) @ R[:, 1]
            band = np.exp(-(((u + v_ * .55) / 1000 - s_pos) / s_w) ** 2)
            col = col + band[:, None] * np.float32([1.0, .86, .55]) * .5
        rgb[idx] = col * gain * al[:, None]
    return rgb.reshape(H, W, 3), a, Hs


def draw(img, obj, R, Tv, env_rot=0.0, gain=1.0, side_gain=1.0, shine=None, tilt=0.0, mv=None):
    """側面 → 前の 面 を img に 重ねる（mv：動きの ぶれ（画面の 画素））→ 字 → 画面 の 行列"""
    sc, scov = sides(obj, R, Tv, side_gain * gain, env_rot)
    fr, fa, Hs = face(obj, R, Tv, env_rot, gain, shine, tilt)
    rgb = fr + sc * (1 - fa[..., None])
    al = np.clip(fa + scov * (1 - fa), 0, 1)
    if mv is not None and math.hypot(*mv) > 1.5:
        lay = KF.motion_blur(np.dstack([rgb, al]).astype(np.float32), mv[0], mv[1])
        p_ = (lay.shape[0] - H) // 2
        lay = lay[p_:p_ + H, p_:p_ + W]
        rgb, al = lay[..., :3], np.clip(lay[..., 3], 0, 1)
    img *= (1 - al[..., None])
    img += rgb
    return Hs, al


# ---------------------------------------------------------------- 字（1回だけ 作る）
CU_CHARS = '神様的中'
CU_K = 1.6                            # 寄りの 字の 地図の 細かさ（1 単位 あたりの 画素）
LOGO_K = .8
LOGO_LINES = (('神様', 1.0, 0.0, .058, 280.0), ('的中', 1.0, 860.0, .058, 280.0),
              ('おめでとう', .36, 1272.0, .075, 170.0), ('御座います！', .36, 1620.0, .075, 170.0))


def cu_obj(j):
    return KF.cache(f'cu{j}', lambda: text_obj([(CU_CHARS[j], 1.0, 0.0, .048, 300.0)], CU_K, seed=11 + j))


def logo_obj():
    return KF.cache('logo3', lambda: text_obj(list(LOGO_LINES), LOGO_K, seed=21))


# ---------------------------------------------------------------- 金の 鳥居（うしろ）
TORII_U = 6.8                          # 鳥居の 絵の 1px（画面の px）＝ 6.8 単位
TORII_K = .45


def torii_obj():
    def f():
        d, (px0, py0, px1, py1) = KA.torii_d()
        k = TORII_K * TORII_U                         # 鳥居の 絵の 1px あたりの 画素
        Wt, Ht = int(KA.FRAME_W * k) + 40, int(KA.FRAME_H * k) + 40
        s = 3
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wt * s}" height="{Ht * s}" viewBox="{-20 / k} {-20 / k} {Wt / k} {Ht / k}">'
               f'<path d="{d}" fill="#fff"/></svg>')
        a = cv2.resize(svg_rgba(svg, Wt * s, Ht * s)[..., 3], (Wt, Ht), interpolation=cv2.INTER_AREA)
        pm = np.zeros((Ht, Wt), np.float32)
        cv2.rectangle(pm, (int(px0 * k + 20), int(py0 * k + 20)), (int(px1 * k + 20), int(py1 * k + 20)), 1.0, -1)
        pm = cv2.GaussianBlur(pm, (0, 0), .8)
        # 額の 中の 金の「天眼」（たて）
        its, boxes = [], []
        for j, c in enumerate('天眼'):
            it, bx, w = KA.run([(c, 1.0)], 0.0, 880.0 + j * 1000)
            its += it
            boxes.append(bx)
        box = KA.union_box(*boxes)
        kk = (py1 - py0 - 14) / (box[3] - box[1]) * k
        tm = KA.mask(its, box, kk, 0)
        th, tw = tm.shape
        tx, ty = int(((px0 + px1) / 2) * k + 20 - tw / 2), int(((py0 + py1) / 2) * k + 20 - th / 2)
        full = np.zeros((Ht, Wt), np.float32)
        full[ty:ty + th, tx:tx + tw] = tm[:max(0, min(th, Ht - ty)), :max(0, min(tw, Wt - tx))]
        panel = pm * (1 - full)
        cx, cy = (KA.FRAME_W / 2) * k + 20, (KA.FRAME_H / 2) * k + 20
        kk_u = k / TORII_U                             # 1 単位 あたりの 画素
        parts = [(a, 7.0 * k, 190.0, None), (full, 2.2 * k, 30.0, None)]
        o = make_obj(parts, kk_u, cx, cy, Wt, Ht, glint_n=8, seed=31, style='gold', extra=panel)
        o['size'] = (KA.FRAME_W * TORII_U, KA.FRAME_H * TORII_U)
        return o
    return KF.cache('torii3', f)


# ---------------------------------------------------------------- 背景（暗い 金の 部屋：動かない）
def background():
    def f():
        X = np.arange(W, dtype=np.float32)[None, :] / S
        Y = np.arange(H, dtype=np.float32)[:, None] / S
        r = np.sqrt(((X - 195) / 1.0) ** 2 + ((Y - 430) / 1.25) ** 2)
        base = np.float32([.035, .012, .004])
        img = np.ones((H, W, 3), np.float32) * base
        img += np.exp(-(r / 330) ** 2)[..., None] * np.float32([.3, .11, .025])
        img += np.exp(-(r / 150) ** 2)[..., None] * np.float32([.26, .12, .03])
        nz = KA.fbm(H // 4, W // 4, 10, 991, 4, .55)
        nz = cv2.resize(nz, (W, H), interpolation=cv2.INTER_CUBIC)
        img *= (.75 + .5 * nz)[..., None]
        # ぼけた 金の 光の 玉（遠くの 光：動かない）
        rng = np.random.default_rng(57)
        bok = np.zeros((H, W), np.float32)
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            rr = rng.uniform(14, 46) * S
            cv2.circle(bok, (int(x * 4), int(y * 4)), int(rr * 4), float(rng.uniform(.25, .7)), -1, cv2.LINE_AA, shift=2)
        bok = cv2.GaussianBlur(bok, (0, 0), 3 * S)
        img += bok[..., None] * np.float32([.24, .12, .035])
        return img.astype(np.float32)
    return KF.cache('bg3', f)


# ---------------------------------------------------------------- 金の 粒（ごつごつ した 金の かたまり：本当の 立体）
def icosphere(sub):
    t = (1 + 5 ** .5) / 2
    V = [np.array(v, np.float64) for v in ((-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
                                           (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1))]
    V = [v / np.linalg.norm(v) for v in V]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(sub):
        cache = {}

        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key not in cache:
                p = V[a] + V[b]
                V.append(p / np.linalg.norm(p))
                cache[key] = len(V) - 1
            return cache[key]
        F2 = []
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    V = np.array(V)
    F = np.array(F, np.int32)
    tri = V[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    if np.mean(np.einsum('ij,ij->i', n, tri.mean(1))) < 0:          # 外向きに そろえる
        F = F[:, ::-1].copy()
    return V, F


def nug_shape(V, seed):
    """球を ごつごつに：大きな こぶ・くぼみ・平らな 割れ面・細かい しわ・つぶれ"""
    rng = np.random.default_rng(seed)
    r = np.ones(len(V))

    def rdir():
        d = rng.normal(size=3)
        return d / np.linalg.norm(d)
    for _ in range(int(rng.integers(4, 7))):
        r += rng.uniform(.12, .3) * np.clip(V @ rdir(), 0, 1) ** rng.uniform(2.0, 4.5)
    for _ in range(int(rng.integers(5, 9))):
        r -= rng.uniform(.05, .14) * np.clip(V @ rdir(), 0, 1) ** rng.uniform(6, 14)
    for _ in range(int(rng.integers(2, 4))):
        d, c = rdir(), rng.uniform(.78, .95)
        pr = V @ d
        r = np.where(pr > .05, np.minimum(r, c / np.maximum(pr, .05)), r)
    for _ in range(70):
        d, s, a = rdir(), rng.uniform(.1, .28), rng.uniform(-.045, .055)
        r += a * np.exp(-(np.arccos(np.clip(V @ d, -1, 1)) / s) ** 2)
    for _ in range(170):                                             # 細かい しわ（くしゃっと した 金）
        d, s, a = rdir(), rng.uniform(.045, .11), rng.uniform(-.04, .035)
        r += a * np.exp(-(np.arccos(np.clip(V @ d, -1, 1)) / s) ** 2)
    for _ in range(5):                                               # おれ目の すじ
        d, fq, ph = rdir(), rng.uniform(9, 17), rng.uniform(0, 6.3)
        r += .022 * np.abs(np.sin(V @ d * fq + ph)) - .011
    P = V * r[:, None] * rng.uniform(.72, 1.12, 3)
    return (P / np.abs(P).max()).astype(np.float64), r


NUG_TYPES = 10
NUG_N = dict(burst=22, big=56, cover=3, drift=4, linger=4)      # 粒の 数（点めつ：1つの 所を 何回も 横切らない ように 少なめ）


def nug_meshes():
    """金の 粒の 形（10しゅ・細かさ 3段）"""
    def f():
        out = []
        for sub in (1, 2, 3, 4):
            V, F = icosphere(sub)
            # となりの 点（くぼみを 暗く する ため）
            nb = [set() for _ in range(len(V))]
            for a, b, c in F:
                nb[a] |= {b, c}
                nb[b] |= {a, c}
                nb[c] |= {a, b}
            lst = []
            for j in range(NUG_TYPES):
                P, r = nug_shape(V, 700 + j * 13)
                rs = r.copy()
                for _ in range(3):
                    rs = np.array([(rs[i] + np.mean(rs[list(nb[i])])) / 2 for i in range(len(V))])
                cav = np.clip((rs - r) / .06, 0, 1)                      # くぼみ（0〜1）
                lst.append((P, F, cav[F].mean(1)))
            out.append(lst)
        return out
    return KF.cache('nugm', f)


NUG_L = np.array([-.42, -.7, -.58])
NUG_L = NUG_L / np.linalg.norm(NUG_L)
NUG_TINT = np.float32([1.0, .8, .46])


def axis_rot(ax, ang):
    ax = np.asarray(ax, np.float64)
    ax = ax / np.linalg.norm(ax)
    x, y, z = ax
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def draw_nugget(img, mesh, Rn, pos, size, boost=1.0, blur=0.0, mv=(0.0, 0.0), fade=1.0):
    """金の 粒 1つを img に（面ごとに 映りこみ・近い ほど ぼける・速い ほど ぶれる）"""
    P, F, cav = mesh
    Q = P @ Rn.T * size + pos
    if Q[:, 2].min() < 30:
        return
    tri = Q[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    cen = tri.mean(1)
    vis = np.einsum('ij,ij->i', n, cen) < 0
    if not vis.any():
        return
    tri, n, cen, cav = tri[vis], n[vis], cen[vis], cav[vis]
    pts = project(tri)
    pad = blur * 2.6 + 4
    X0, Y0 = int(math.floor(pts[..., 0].min() - pad)), int(math.floor(pts[..., 1].min() - pad))
    X1, Y1 = int(math.ceil(pts[..., 0].max() + pad)), int(math.ceil(pts[..., 1].max() + pad))
    mvl = math.hypot(*mv)
    if X1 + mvl < 0 or Y1 + mvl < 0 or X0 - mvl > W or Y0 - mvl > H:
        return
    w, h = X1 - X0, Y1 - Y0
    if w * h > 9e6:
        return
    ss = 2.0 if max(w, h) < 260 else (1.0 if blur < 5 else .5)
    cw, ch = max(2, int(w * ss) + 1), max(2, int(h * ss) + 1)
    canvas = np.zeros((ch, cw, 3), np.float32)
    cov = np.zeros((ch, cw), np.float32)
    V = cen / np.linalg.norm(cen, axis=1, keepdims=True)
    vn = np.einsum('ij,ij->i', V, n)
    rv = V - 2 * vn[:, None] * n
    rv[:, 1] = rv[:, 1] * .55 - .2                                  # 下（暗い 床）を 映しすぎない
    rv /= np.linalg.norm(rv, axis=1, keepdims=True)
    envc = env_lookup(rv).astype(np.float32)
    envc = np.clip(envc - .16, 0, None) * 1.3                       # 映りこみの 明暗を 強く（みがいた 金）
    dif = np.clip(n @ NUG_L, 0, 1)
    hv = NUG_L[None, :] - V
    hv /= np.linalg.norm(hv, axis=1, keepdims=True)
    spec = np.clip(np.einsum('ij,ij->i', n, hv), 0, 1) ** 44
    col = envc * NUG_TINT * (.22 + .9 * dif)[:, None] + spec[:, None] * np.float32([1.0, .95, .8]) * 1.5
    col += ((1 - np.abs(vn)) ** 3 * .2)[:, None] * np.float32([1.0, .72, .3])
    col += np.float32([.1, .05, .015])                               # まわりの 金の 光（暗く なりすぎない）
    col *= (1 - .5 * cav)[:, None] * boost
    q = np.round((pts - np.array([X0, Y0])) * ss * 4).astype(np.int32)
    for i in np.argsort(-cen[:, 2]):
        cv2.fillConvexPoly(canvas, q[i], col[i].tolist(), cv2.LINE_8, shift=2)
        cv2.fillConvexPoly(cov, q[i], 1.0, cv2.LINE_8, shift=2)
    rgba = np.dstack([canvas, cov])
    if ss != 1.0:
        rgba = cv2.resize(rgba, (max(1, w), max(1, h)), interpolation=cv2.INTER_AREA if ss > 1 else cv2.INTER_LINEAR)
    if ss > 1:
        rgba = cv2.GaussianBlur(rgba, (0, 0), .55)
    if blur > .6:
        rgba = cv2.GaussianBlur(rgba, (0, 0), blur)
    ox, oy = X0, Y0
    if mvl > 1.5:
        b = KF.motion_blur(rgba, mv[0], mv[1])
        p_ = (b.shape[0] - rgba.shape[0]) // 2
        rgba, ox, oy = b, X0 - p_, Y0 - p_
    if fade < 1.0:
        rgba = rgba * fade
    KF.place(img, rgba, ox, oy)


def nug_events():
    """金の 粒の 一つ一つ：(はじめの 時刻, 種, 形, はじめの 場所, 速さ, ブレーキ, 回る 軸, 回る 速さ, 向き, 大きさ, 命)"""
    def f():
        ev = []
        for bi, (t0, kind, t_end) in enumerate(TT['BU']):
            rng = random.Random(500 + bi * 37)
            if kind == 0:                                           # 大きな 粒が 手前を 横切る（字の かわり目を かくす）
                dirn = -1 if bi % 4 == 1 else 1
                for k in range(NUG_N['cover']):
                    z = rng.uniform(300, 640)
                    half = (W / 2) * z / FOCAL * 1.45
                    y = rng.uniform(-.85, .85) * (H / 2) * z / FOCAL
                    tc = t0 + .05 + k * .04 + rng.uniform(-.02, .02)
                    dur = rng.uniform(.26, .36)
                    vx = 2 * half / dur * dirn
                    ev.append(dict(t0=tc - dur / 2, kind=0, typ=rng.randrange(NUG_TYPES), p0=np.array([-dirn * half, y, z]),
                                   v0=np.array([vx, rng.uniform(-150, 150), rng.uniform(-60, 60)]), tau=99.0, g=0.0,
                                   ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(3, 7) * rng.choice((-1, 1)),
                                   ph=rng.uniform(0, 6.3), size=rng.uniform(120, 175), life=dur + .02, end=None, soft=True))
                # 次の 寄りの 間：手前を ゆっくり ただよう 粒（光らない・ぼけて いる）
                j = 1 if bi == 1 else 3
                s0, s1 = TT['CU'][j]
                r2 = random.Random(800 + bi)
                for k in range(NUG_N['drift']):
                    z = r2.uniform(320, 850)
                    tt = s0 + r2.uniform(.04, .14)
                    ev.append(dict(t0=tt, kind=3, typ=r2.randrange(NUG_TYPES),
                                   p0=np.array([r2.uniform(-.8, .8) * (W / 2) * z / FOCAL, r2.uniform(-.85, .85) * (H / 2) * z / FOCAL, z]),
                                   v0=np.array([r2.uniform(-140, 140), r2.uniform(-120, 40), r2.uniform(-200, -60)]), tau=99.0, g=60.0,
                                   ax=np.array([r2.gauss(0, 1), r2.gauss(0, 1), r2.gauss(0, 1)]), w=r2.uniform(1.0, 2.5) * r2.choice((-1, 1)),
                                   ph=r2.uniform(0, 6.3), size=r2.uniform(18, 55), life=s1 - tt + .02, end=s1, fin=.15))
                continue
            big = kind == 2
            n = NUG_N['big'] if big else NUG_N['burst']
            cz, cx, cy = (2050.0, 0.0, 380.0) if big else (960.0, 0.0, 60.0)
            for k in range(n):
                th = rng.uniform(0, 2 * math.pi)
                lat = rng.uniform(400, 1800) * (1.35 if big else 1.0)
                vz = -rng.uniform(1400, 3400) * (1.25 if big else 1.0)
                vx, vy = lat * math.cos(th), lat * math.sin(th) * .85
                if big:
                    vy -= rng.uniform(300, 1100)                    # 下から 上へ ぶわっと
                sz = 9 + 70 * rng.random() ** 2.6
                if rng.random() < (.12 if big else .06):
                    sz = rng.uniform(70, 125)
                ev.append(dict(t0=t0 + rng.uniform(0, .07 if big else .05), kind=kind, typ=rng.randrange(NUG_TYPES),
                               p0=np.array([cx + rng.gauss(0, 380 if big else 230), cy + rng.gauss(0, 300 if big else 190), cz - rng.uniform(0, 420)]),
                               v0=np.array([vx, vy, vz]), tau=rng.uniform(.8, 1.2) if big else rng.uniform(.7, 1.0), g=rng.uniform(200, 500),
                               ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(3, 9) * rng.choice((-1, 1)),
                               ph=rng.uniform(0, 6.3), size=sz, life=rng.uniform(.55, .9) if big else rng.uniform(.45, .75), end=t_end))
            if big:                                                 # ゆっくり ただよう 粒（おちつく まで 少し のこる）
                for k in range(NUG_N['linger']):
                    th = rng.uniform(0, 2 * math.pi)
                    lat = rng.uniform(150, 480)
                    ev.append(dict(t0=t0 + rng.uniform(.02, .12), kind=kind, typ=rng.randrange(NUG_TYPES),
                                   p0=np.array([rng.choice((-1, 1)) * rng.uniform(320, 700), 380 + rng.gauss(0, 420), rng.uniform(1100, 1700)]),
                                   v0=np.array([lat * math.cos(th), lat * math.sin(th) - 200, -rng.uniform(150, 500)]), tau=1.2, g=rng.uniform(150, 300),
                                   ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(1.5, 4) * rng.choice((-1, 1)),
                                   ph=rng.uniform(0, 6.3), size=rng.uniform(20, 60), life=rng.uniform(1.0, 1.4), end=None))
        return ev
    return KF.cache('nugev', f)


def nug_state(e, t):
    s = t - e['t0']
    tau = e['tau']
    p = e['p0'] + e['v0'] * tau * (1 - math.exp(-s / tau)) + np.array([0.0, e['g'] * s * s * .5, 0.0])
    return p


def focus_z(t):
    """ピントの きょり（今 写って いる 字）"""
    return 970.0 if t < TT['LOGO'] else logo_pose(t)[5]


def nuggets(img, t):
    """金の 粒（遠い 順に）"""
    meshes = nug_meshes()
    zf = focus_z(t)
    items = []
    for e in nug_events():
        s = t - e['t0']
        if not (0 <= s <= e['life']) or (e['end'] is not None and t >= e['end']):
            continue
        p = nug_state(e, t)
        if p[2] < 60:
            continue
        items.append((p[2], e, p, s))
    items.sort(key=lambda a: -a[0])
    for z, e, p, s in items:
        pp = nug_state(e, t - .5 / FPS)
        c1 = project(p)
        c0 = project(pp)
        r_px = e['size'] * FOCAL / z
        blur = min(22.0, 3.2 * abs(zf / z - 1.0)) if z < zf else min(4.0, 3.0 * (1 - zf / z))
        if e.get('soft'):
            blur = max(blur, 30.0)                                  # 手前を 横切る 大きな 粒は 大きく ぼかす（中の 明暗で ちらつかない）
        lvl = 0 if r_px < 14 else (1 if r_px < 40 else (2 if (r_px < 130 or blur > 5) else 3))
        mesh = meshes[lvl][e['typ']]
        Rn = axis_rot(e['ax'], e['ph'] + e['w'] * s)
        boost = (1.15, 1.0 + 1.6 * math.exp(-s / .1), 1.0 + 1.6 * math.exp(-s / .1), 1.0)[e['kind']]
        fin = e.get('fin', .03)
        fade = min(1.0, (e['life'] - s) / .2) * min(1.0, s / fin + .2)
        draw_nugget(img, mesh, Rn, p, e['size'], boost, blur, (c1[0] - c0[0], c1[1] - c0[1]), fade)


# ---------------------------------------------------------------- はじける 光・金の ちり・キラッ
def burst_light(img, t):
    """金の 粒が はじける 時の 光（すぐ 消える：1回の はじけで 1回）"""
    X = np.arange(W, dtype=np.float32)[None, :]
    Y = np.arange(H, dtype=np.float32)[:, None]
    for t0, kind, _ in TT['BU']:
        s = t - t0
        if kind == 0 or not (-.01 <= s <= .5):
            continue
        A = 1.25 if kind == 1 else 1.7
        g = A * math.exp(-max(0.0, s) / .12) * smoothstep(-.01, .03, s)
        if g < .01:
            continue
        cx, cy = CXS, CYS + (60 if kind == 1 else 300) * S * .3
        d2 = (X - cx) ** 2 + ((Y - cy) * .8) ** 2
        r = (420 + 900 * s) * (1.3 if kind == 2 else 1.0)
        img += (np.exp(-d2 / (r * r)) * g)[..., None] * np.float32([1.0, .82, .45])
        img += (np.exp(-d2 / ((r * .3) ** 2)) * g * .8)[..., None] * np.float32([1.0, .96, .86])


def debris(img, t):
    """はじけた 時の 細かい 金の ちり（光の つぶ）"""
    m = np.zeros((H, W), np.float32)
    for bi, (t0, kind, t_end) in enumerate(TT['BU']):
        s = t - t0
        if kind == 0 or not (0 <= s <= 1.0) or (t_end is not None and t >= t_end):
            continue
        rng = random.Random(900 + bi)
        cx, cy = CXS, CYS + (60 if kind == 1 else 300) * S * .3
        for _ in range(120 if kind == 2 else 70):
            a = rng.uniform(0, 2 * math.pi)
            v = rng.uniform(300, 2200) * (1.3 if kind == 2 else 1.0)
            life = rng.uniform(.35, 1.0)
            if s > life:
                continue
            tau = .22
            dist = v * tau * (1 - math.exp(-s / tau))
            x = cx + rng.gauss(0, 60) + dist * math.cos(a)
            y = cy + rng.gauss(0, 60) + dist * math.sin(a) + 260 * s * s
            e = (1 - s / life) ** .7 * (.55 + .45 * math.sin(rng.uniform(0, 6.3) + 30 * s))
            tail = v * math.exp(-s / tau) * .012
            cv2.line(m, (int((x - tail * math.cos(a)) * 4), int((y - tail * math.sin(a)) * 4)), (int(x * 4), int(y * 4)),
                     float(max(0.0, e)), max(1, int(rng.uniform(2, 5))), cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, .97, .85), 1.1), (1.2, (1, .82, .4), .8), (5, (1, .6, .15), .35)))


def sparkle_events():
    def f():
        rng = random.Random(4242)
        ev = []
        t = 0.0
        while t < N / FPS:
            ev.append((t, rng.uniform(.04, .96), rng.uniform(.06, .94), rng.uniform(.6, 1.3), rng.uniform(.25, .42)))
            t += rng.uniform(.02, .07)
        return ev
    return KF.cache('spk', f)


def sparkles(img, t, amt=1.0):
    """白い 星の きらめき（ふわっと 出て 消える）"""
    m = np.zeros((H, W), np.float32)
    for t0, u, v, sc, dur in sparkle_events():
        if not (t0 <= t <= t0 + dur):
            continue
        e = math.sin(math.pi * (t - t0) / dur) * amt
        x, y = u * W, v * H
        L = 30 * S * sc * (.55 + .45 * e)
        for ang, l, g in ((0.0, L, 1.0), (math.pi / 2, L, 1.0), (math.pi / 4, L * .4, .55), (-math.pi / 4, L * .4, .55)):
            cv2.line(m, (int((x - l * math.cos(ang)) * 4), int((y - l * math.sin(ang)) * 4)),
                     (int((x + l * math.cos(ang)) * 4), int((y + l * math.sin(ang)) * 4)), float(e * g), 2, cv2.LINE_AA, shift=2)
        cv2.circle(m, (int(x * 4), int(y * 4)), int(3 * S * 4 * e) + 1, float(e), -1, cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, 1, 1), 1.0), (1.4, (1, .93, .75), .8), (5, (1, .75, .35), .35)))


def glints(img, obj, Hs, t, seed):
    """キラッ（ふちの 上の 小さな 光の 星：1つずつ ふわっと 出て 消える）"""
    g = obj['glints']
    if len(g) == 0:
        return
    m = np.zeros((H, W), np.float32)
    rng = random.Random(seed)
    for (gx, gy) in g:
        t0 = rng.uniform(-.2, N / FPS)
        dur = rng.uniform(.26, .42)
        if not (t0 <= t <= t0 + dur):
            continue
        p = Hs @ np.array([gx, gy, 1.0])
        x, y = p[0] / p[2], p[1] / p[2]
        if not (0 <= x < W and 0 <= y < H):
            continue
        e = math.sin(math.pi * (t - t0) / dur)
        Lg = rng.uniform(26, 44) * S * (.6 + .4 * e)
        for ang in (0.0, math.pi / 2, math.pi / 4, -math.pi / 4):
            l = Lg if ang in (0.0, math.pi / 2) else Lg * .45
            cv2.line(m, (int((x - l * math.cos(ang)) * 4), int((y - l * math.sin(ang)) * 4)),
                     (int((x + l * math.cos(ang)) * 4), int((y + l * math.sin(ang)) * 4)), float(e * (1.0 if l == Lg else .6)), 2, cv2.LINE_AA, shift=2)
        cv2.circle(m, (int(x * 4), int(y * 4)), int(5 * S * 4 * e) + 1, float(e), -1, cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, 1, 1), 1.2), (1.5, (1, .92, .7), 1.0), (6, (1, .75, .3), .5)))


def unit_h(R, Tv):
    """字の 単位 (u, v) → 画面 の 行列"""
    Kc = np.array([[FOCAL, 0, CXS], [0, FOCAL, CYS], [0, 0, 1]])
    return Kc @ np.column_stack([R[:, 0], R[:, 1], Tv])


# ---------------------------------------------------------------- 字の 動き
# 神・様・的・中 の 寄り：(yaw はじめ, おわり, pitch, roll, x はじめ, おわり, y, z)。横に ゆっくり（しまは 横 なので たてには 動かさない）
CU_POSE = ((-21.0, -16.0, 20.0, -3.0, -50.0, 45.0, 60.0, 960.0),
           (19.0, 14.0, 19.0, 3.0, 50.0, -45.0, 60.0, 970.0),
           (-15.0, -10.0, 21.0, -2.5, -45.0, 40.0, 60.0, 950.0),
           (22.0, 17.0, 18.0, 3.0, 45.0, -45.0, 60.0, 980.0))


CU_DRIFT = .35                       # 寄りの 横の 動きの 大きさ（点めつ：字の 細かい 明暗が 画素を 何度も 通らない）


def cu_pose(j, t):
    t0, t1 = TT['CU'][j]
    u = (t - t0) / (t1 - t0) - .5
    y0, y1, pitch, roll, x0, x1, y, z = CU_POSE[j]
    return (y0 + y1) / 2 + (y1 - y0) * u * CU_DRIFT, pitch, roll, (x0 + x1) / 2 + (x1 - x0) * u * CU_DRIFT, y, z


def logo_final():
    lo = logo_obj()
    zf = FOCAL * lo['size'][0] / (.92 * W)
    return zf, (470 * S - CYS) * zf / FOCAL


def logo_pose(t):
    """ななめ（大きい）→ 正面へ 回りながら ひく → ゆっくり"""
    zf, yf = logo_final()
    t0, t1 = TT['TURN']
    p = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    u = 1 - (1 - p) ** 2.6
    a = (-13.0, 10.0, -2.5, 170.0, yf + 140.0, zf * .82)
    b = (0.0, 3.0, 0.0, 0.0, yf, zf)
    pose = [x + (y - x) * u for x, y in zip(a, b)]
    s = max(0.0, t - t1)
    pose[0] += .9 * s
    pose[5] *= 1 + .012 * s
    return pose


def torii_place(R, Tv):
    """鳥居（字の うしろ 500）"""
    zf, yf = logo_final()
    zt = zf + 500.0
    yt = (426 * S - CYS) * zt / FOCAL
    off = np.array([0.0, yt - yf, 500.0])
    return R, Tv + R @ off


def white_amt(t):
    w0, w1, w2 = TT['WIN']
    return 1.0 if t <= w1 else max(0.0, 1.0 - sstep(w1, w2, t))


def frame(fi):
    t = fi / FPS
    img = background().copy()
    if t < TT['LOGO']:
        j = min(3, sum(1 for a, b in TT['CU'] if t >= b))
        yaw, pitch, roll, x, y, z = cu_pose(j, t)
        R = rot(yaw, pitch, roll)
        Tv = np.array([x, y, z])
        u = (t - TT['CU'][j][0]) / (TT['CU'][j][1] - TT['CU'][j][0])
        o = cu_obj(j)
        draw(img, o, R, Tv, env_rot=-10 + 14 * u + j * 25, tilt=j * 1.7)
        glints(img, o, unit_h(R, Tv), t, 60 + j)
    else:
        yaw, pitch, roll, x, y, z = logo_pose(t)
        R = rot(yaw, pitch, roll)
        Tv = np.array([x, y, z])
        Rt, Tt = torii_place(R, Tv)
        pv = logo_pose(max(TT['LOGO'], t - .5 / FPS))                # 動きの ぶれ（半コマぶん）
        c1, c0 = project(Tv), project(np.array(pv[3:]))
        mv = (float(c1[0] - c0[0]) * 1.4, float(c1[1] - c0[1]) * 1.4)
        draw(img, torii_obj(), Rt, Tt, env_rot=8 - 6 * (t - TT['LOGO']), mv=mv)
        sh = None
        s0, s1 = TT['SHINE']
        if s0 - .05 <= t <= s1 + .05:
            q = (t - s0) / (s1 - s0)
            sh = (-2.6 + 5.2 * ease_out(q), .5)
        o = logo_obj()
        draw(img, o, R, Tv, env_rot=-14 + 10 * (t - TT['LOGO']), shine=sh, mv=mv)
        glints(img, o, unit_h(R, Tv), t, 70)
    burst_light(img, t)
    nuggets(img, t)
    debris(img, t)
    sparkles(img, t, .8 if t < TT['LOGO'] else .55)
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
    for j in range(4):
        o = cu_obj(j)
        img = background().copy()
        yaw = (-20, 18, -14, 22)[j]
        R = rot(yaw, 16.0, (-3, 3, -2, 3)[j])
        Tv = np.array([0.0, 60.0, 1050.0])
        draw(img, o, R, Tv)
        img = KF.bloom(img)
        cv2.imwrite(os.path.join(out, f'cu{j}.png'), cv2.cvtColor((KF.tonemap(img) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))
        print('cu', j, flush=True)
    lo = logo_obj()
    to = torii_obj()
    z = FOCAL * lo['size'][0] / (.92 * W)
    img = background().copy()
    zt = z + 500
    Tt = np.array([0.0, (436 - 422) * S * zt / FOCAL, zt])
    draw(img, to, rot(0, 2, 0), Tt)
    Tl = np.array([0.0, (470 - 422) * S * z / FOCAL, z])
    draw(img, lo, rot(0, 4, 0), Tl)
    img = KF.bloom(img)
    cv2.imwrite(os.path.join(out, 'logo.png'), cv2.cvtColor((KF.tonemap(img) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))
    img = background().copy()
    draw(img, lo, rot(-20, 14, -3), np.array([150.0, 200.0, z * .78]))
    img = KF.bloom(img)
    cv2.imwrite(os.path.join(out, 'logo_tilt.png'), cv2.cvtColor((KF.tonemap(img) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    if sys.argv[2:3] == ['test']:
        _test(sys.argv[1])
    else:
        main(sys.argv[1], [int(v) - 1 for v in sys.argv[2:]] or None)
