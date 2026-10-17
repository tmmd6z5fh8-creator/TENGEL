"""水墨画の競走馬と騎手（墨の線＋灰色のぼかし）
   3Dの馬（horse3d）と騎手の形を3倍の大きさで描き（flat/anime_rider.render_anime）、墨絵にする：
   - ぼかし（にじみ）：光の当たり具合から、うすい墨・中の墨・こい墨を重ねる。境目は水のにじみでゆらぎ、乾いたふちが少し濃くなる。
     骨にそった「筆の向き」の筋で塗りをむらにし、光の当たる所は筆のかすれで白く抜く（飛白）
   - 線：外のふちは、影の側ほど太く・光の側ほど細く（ところどころ消える）。重なりと部分のさかい目は細い線。
     肩・ひじ・もも・すねに、筋肉をあらわす短い筆の線
   - たてがみ・前髪・しっぽ：穂先の毛を1本ずつ線にした筆の線（flat/ink_horse.bristle_stroke）
   - 目・鼻の穴・口・頭のベルト・手綱、騎手のヘルメット・ゴーグル・ブーツ
   戻り値は1倍の (墨の濃さ k, おおう量 A)。形はすべて一から作ったオリジナル"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from anime_rider import *                      # render_anime・_dist_line・_thick・_gsmooth・world_pos・素材の番号・Hm
from anime_rider import _dist_line, _thick, _gsmooth
from ink_horse import bones, direction_field, lic, resample, bristle_stroke, flow_path

# 部分ごとの墨（うすい地・影で足す・深い影で足す）
TONES_DARK = {0: (0.46, 0.26, 0.16), 2: (0.80, 0.10, 0.05), 3: (0.74, 0.12, 0.06), 4: (0.06, 0.16, 0.08), 5: (0.02, 0.16, 0.06),
              6: (0.70, 0.12, 0.05), 7: (0.66, 0.16, 0.06), 10: (0.06, 0.22, 0.10), 11: (0.06, 0.22, 0.10), 12: (0.70, 0.18, 0.06),
              13: (0.02, 0.15, 0.06), 14: (0.80, 0.12, 0.04), 15: (0.02, 0.10, 0.04), 16: (0.86, 0.06, 0.0), 17: (0.30, 0.16, 0.05), 1: (0.9, 0, 0)}
TONES_LIGHT = {0: (0.07, 0.20, 0.12), 2: (0.40, 0.14, 0.06), 3: (0.30, 0.14, 0.06), 4: (0.03, 0.12, 0.06), 5: (0.02, 0.12, 0.05),
               6: (0.36, 0.12, 0.05), 7: (0.34, 0.14, 0.05), 10: (0.04, 0.16, 0.08), 11: (0.04, 0.16, 0.08), 12: (0.42, 0.16, 0.06),
               13: (0.02, 0.12, 0.05), 14: (0.46, 0.14, 0.05), 15: (0.02, 0.08, 0.03), 16: (0.55, 0.06, 0.0), 17: (0.18, 0.12, 0.04), 1: (0.6, 0, 0)}


def _noise(shape, sig, rng):
    n = cv2.GaussianBlur(rng.random(shape).astype(np.float32), (0, 0), sig)
    return np.clip((n - n.mean()) / (n.std() + 1e-6) * 0.18 + 0.5, 0, 1)


def _lowf(shape, cell, rng):
    h, w = shape
    n = cv2.GaussianBlur(rng.random((h // cell + 2, w // cell + 2)).astype(np.float32), (0, 0), 1.2)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return np.clip((n - n.mean()) / (n.std() + 1e-6) * 0.25 + 0.5, 0, 1)


def make_parts(R, look):
    """部分の番号（anime_rider と同じ分け方）"""
    a = np.clip(R['a'], 0, 1)
    inside = a > 0.5
    m = np.round(R['m']).astype(int) * inside
    P = world_pos(R)
    Pn = np.nan_to_num(P, nan=99.0)
    S, J = R['S'], R['J']
    js = J['js']
    side = R['side']
    part = np.full(m.shape, -1, int)
    part[m == M_COAT] = 0; part[m == M_EYE] = 1; part[m == M_HOOF] = 2
    for k, v in ((M_SILK, 10), (M_SLEEVE, 11), (M_HELMET, 12), (M_PANTS, 13), (M_BOOT, 14)):
        part[m == k] = v
    legd = np.full(m.shape, 9.0, np.float32)
    for k, top in (('FL', 'kn'), ('FR', 'kn'), ('HL', 'hk'), ('HR', 'hk')):
        F = S[k]
        zl = 0.155 * F['z'] * 0.92
        q0 = np.array([*(np.asarray(F[top]) + (np.asarray(F['ft']) - np.asarray(F[top])) * 0.25), zl])
        q1 = np.array([*np.asarray(F['hf']), zl])
        dd = q1 - q0
        tt = np.clip(np.sum((Pn - q0) * dd, -1) / np.dot(dd, dd), 0, 1)
        legd = np.minimum(legd, np.linalg.norm(Pn - (q0 + tt[..., None] * dd), axis=-1))
    if look.get('legs', 'black') == 'black':
        part[(part == 0) & (legd < 0.11)] = 3
    w = np.asarray(S['withers'], float)
    zs = Pn[..., 2] * side
    cloth = (part == 0) & (Pn[..., 0] > w[0] - 0.56) & (Pn[..., 0] < w[0] - 0.08) & (Pn[..., 1] > w[1] - 0.50) & (zs > -0.05)
    part[cloth] = 5
    saddle = (part == 5) & (Pn[..., 0] > w[0] - 0.47) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] > w[1] - 0.115)
    part[saddle] = 7
    girth = np.isin(part, (0, 5)) & (Pn[..., 0] > w[0] - 0.21) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] < w[1] - 0.20) & (Pn[..., 1] > w[1] - 0.80)
    part[girth] = 6
    hc = J['head']
    q = Pn - hc
    front = (part == 12) & (q[..., 0] > -0.01 * js) & (q[..., 1] < -0.042 * js)
    part[front & (q[..., 1] > -0.074 * js)] = 16
    part[front & (q[..., 1] <= -0.074 * js)] = 15
    for z in (1, -1):
        part[(part == 14) & (np.linalg.norm(Pn - J[f'knee{z}'], axis=-1) < 0.075 * js)] = 17
    return part, Pn


def _bristles(canvas, P, w, rng, nb=20, lw=2, dry=0.55, split=0.5, gap=0.5, wander=0.5, ink=1.0, start=0.0):
    """穂先の毛を1本ずつ線に（w は道の点ごとの太さ）"""
    n = len(P)
    tg = np.gradient(P, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    offs = (np.arange(nb) + rng.uniform(0.2, 0.8, nb)) / nb - 0.5
    for b in range(nb):
        o = offs[b]
        Lb = 1.0 - split * (abs(o) * 2) ** 1.4 * rng.uniform(0.4, 1.0) - rng.uniform(0, 0.08)
        nn = max(3, int(n * Lb))
        jit = np.cumsum(rng.normal(0, 0.12, n))[:nn] * wander
        q = P[:nn] + nr[:nn] * (o * w[:nn] + jit)[:, None]
        td = dry + rng.uniform(-0.15, 0.20) - abs(o) * 0.25
        on = np.ones(nn, bool)
        i = int(td * n)
        while i < nn:
            run = int(rng.integers(3, 12))
            if rng.random() < gap * min(1.0, (i / n - td) * 3 + 0.3):
                on[i:i + run] = False
            i += run
        if start > 0:
            on[:int(rng.uniform(0, start) * n)] = False
        idx = np.nonzero(np.diff(np.r_[0, on.astype(int), 0]))[0]
        for s0, s1 in zip(idx[::2], idx[1::2]):
            if s1 - s0 >= 2:
                cv2.polylines(canvas, [np.round(q[s0:s1] * 16).astype(np.int32)], False, ink, lw, cv2.LINE_AA, shift=4)
    return canvas


def sweep(canvas, path, wmax, rng, root=0.22, w_end=0.06, **kw):
    """ふくらむ筆の線：根元は細く入り、root のあたりでいちばん太く、先へ細く払う（たてがみ・しっぽ）"""
    P = resample(path, 1.0)
    t = np.linspace(0, 1, len(P))
    w = np.where(t < root, 0.25 + 0.75 * (t / root) ** 0.6, w_end + (1 - w_end) * (1 - (t - root) / (1 - root)) ** 0.9) * wmax
    return _bristles(canvas, P, w, rng, **kw)


def trace(F, mask, p, L, h, rng):
    """筆の向き F にそって、点 p から前後へ L/2 ずつ進む道（形の外へ少し出たら止まる）"""
    H3, W3 = mask.shape
    out = []
    for sgn in (1, -1):
        q = np.array(p, float)
        dprev = None
        pts = []
        steps = int(L / 2 / h)
        miss = 0
        for _ in range(steps):
            xi, yi = int(q[0]), int(q[1])
            if not (0 <= xi < W3 and 0 <= yi < H3):
                break
            dv = F[yi, xi].astype(float)
            if np.allclose(dv, 0):
                break
            dv = dv * sgn if dprev is None else (dv if np.dot(dv, dprev) >= 0 else -dv)
            dv = dv + rng.normal(0, 0.04, 2)
            dv /= np.linalg.norm(dv) + 1e-9
            q = q + dv * h
            dprev = dv
            pts.append(q.copy())
            if mask[min(H3 - 1, max(0, int(q[1]))), min(W3 - 1, max(0, int(q[0])))] < 0.5:
                miss += 1
                if miss > 1:
                    break
        out.append(pts)
    path = out[1][::-1] + [np.array(p, float)] + out[0]
    return np.array(path) if len(path) >= 4 else None


def wash_layer(shape, F, mask, sel, ink, sp, L, wd, rng, nb=12, lw=2, dry=0.62, gap=0.45, keep=None):
    """形 mask の中で sel のある所に、筆の向きにそった太い筆を何本も置く（墨の濃さ ink の1枚）"""
    H3, W3 = shape
    cv_ = np.zeros(shape, np.float32)
    ys, xs = np.nonzero(sel)
    if len(ys) == 0:
        return cv_
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    for gy in np.arange(y0, y1 + 1, sp):
        for gx in np.arange(x0, x1 + 1, sp):
            px, py = gx + rng.uniform(-sp / 2, sp / 2), gy + rng.uniform(-sp / 2, sp / 2)
            xi, yi = int(px), int(py)
            if not (0 <= xi < W3 and 0 <= yi < H3) or not sel[yi, xi]:
                continue
            if keep is not None and rng.random() > keep[yi, xi]:
                continue
            path = trace(F, mask, (px, py), L * rng.uniform(0.7, 1.25), 1.5, rng)
            if path is None:
                continue
            P = resample(path, 1.0)
            t = np.linspace(0, 1, len(P))
            w = wd * rng.uniform(0.8, 1.2) * (0.55 + 0.45 * np.sin(np.pi * t))
            _bristles(cv_, P, w, rng, nb=nb, lw=lw, dry=dry, split=0.35, gap=gap, wander=0.6, ink=ink, start=0.15)
    return cv_


def contour_strokes(canvas, mask, press, low, rng, u1, s, lw=1.0, wmin=1.9, wk=2.2, seg=(26, 60), lost=0.5, nb=10, ink=1.0):
    """形のふちを、何本もの筆の線で描く（線ごとに入りと抜きがあり、影の側ほど太い・光の側はときどき消える）"""
    H3, W3 = mask.shape
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    blw = max(1, int(round(0.75 * s)))
    for c in cs:
        P = c[:, 0, :].astype(float)
        if len(P) < 12 * s:
            continue
        k_ = int(1.5 * s)                                               # 少しなめらかに
        P = np.stack([np.convolve(np.r_[P[-k_:, i], P[:, i], P[:k_, i]], np.ones(2 * k_ + 1) / (2 * k_ + 1), 'valid') for i in (0, 1)], 1)
        n = len(P)
        i = int(rng.integers(0, n))
        done = 0
        while done < n:
            L = int(rng.uniform(*seg) * u1)
            idx = (i + np.arange(L)) % n
            Q = P[idx]
            qx = np.clip(Q[:, 0].astype(int), 0, W3 - 1); qy = np.clip(Q[:, 1].astype(int), 0, H3 - 1)
            pr = np.clip(press[qy, qx] / 0.8, 0, 1)
            lo = low[qy, qx]
            if not (pr.mean() < 0.12 and lo.mean() > 0.56 and rng.random() < lost):
                t = np.linspace(0, 1, L)
                env = np.clip(np.sin(np.pi * t) * 2.2, 0, 1) ** 0.6              # 入りと抜き
                w = lw * s * (wmin + wk * pr) * (0.75 + 0.5 * lo) * (0.35 + 0.65 * env)
                tg = np.gradient(Q, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
                nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
                mid = Q[len(Q) // 2]
                probe = mid + nr[len(Q) // 2] * 2.0
                if mask[int(np.clip(probe[1], 0, H3 - 1)), int(np.clip(probe[0], 0, W3 - 1))] == 0:
                    nr = -nr                                            # 内がわへ
                C = Q + nr * (w * 0.42)[:, None]
                _bristles(canvas, C, w, rng, nb=nb, lw=blw, dry=0.78, split=0.25, gap=0.35, wander=0.35, ink=ink, start=0.0)
            step = L - int(rng.uniform(-3, 6) * s)                       # 少し重ねたり、すき間をあけたり
            i = (i + max(4, step)) % n
            done += max(4, step)
    return canvas


def paint_sumi(R, look, debug=None):
    """look: tones（'dark'／'light'）・seed・lw（線の太さの倍率）・line_ink（線の墨）・hair_ink・mane・tail_len・tail_ang
       silk・sleeve・helmet（騎手の墨：部分の (地・影・深い影) を上書き）・hi（白く抜く強さ）・hi_t（白く抜きはじめる明るさ）"""
    s = R['s']
    a = np.clip(R['a'], 0, 1)
    inside = a > 0.5
    H3, W3 = a.shape
    m = np.round(R['m']).astype(int) * inside
    n = R['n']
    d = R['d']
    side = R['side']
    Lk = R['Lk']
    rng = np.random.default_rng(look.get('seed', 1))
    horse = np.isin(m, HORSE) & inside
    jock = np.isin(m, JOCKEY) & inside
    groups = (horse, jock)
    lt = np.clip(R['rgb'].mean(-1) / 0.318, 0, 1.3)
    S, J = R['S'], R['J']
    lw = look.get('lw', 1.0)
    hl_ = np.linalg.norm(np.asarray(R['muzzle']) - np.asarray(R['poll']))
    u1 = hl_ / HEAD_REF
    Pj = lambda p3: R['scene'].project(np.asarray([p3], float))[0][0][:2]
    R['P'] = lambda pts: R['scene'].project(np.asarray(pts, float))[0]
    part, Pn = make_parts(R, look)

    def segd(p0, p1):
        dd = p1 - p0
        tt = np.clip(np.sum((Pn - p0) * dd, -1) / np.dot(dd, dd), 0, 1)
        return np.linalg.norm(Pn - (p0 + tt[..., None] * dd), axis=-1)
    head = (segd(Hm.v3(S['poll']), Hm.head_pt(S, 0.56, -0.03)) < 0.20 * Hm.HEAD_SCALE) & horse
    lts = np.where(head, _gsmooth(lt, groups, 2.6 * s), _gsmooth(lt, groups, 2.2 * s))
    ns = _gsmooth(n, groups, 1.6 * s)
    ns = ns / (np.linalg.norm(ns, axis=-1, keepdims=True) + 1e-6)
    nl = np.sum(ns * Lk, -1)
    ao = _gsmooth(R['ao'], groups, 1.5 * s)

    # ---------- 筆の向きと筋 ----------
    ys, xs = np.nonzero(a > 0.05)
    pad = 60 * s
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(W3, xs.max() + pad), min(H3, ys.max() + pad))
    F = direction_field((H3, W3), bones(R), box, sig=6.0 * s)
    noise = cv2.GaussianBlur(rng.random((H3, W3)).astype(np.float32), (0, 0), 1.3 * s)
    Sx = lic(noise, F, box, steps=40, h=1.2 * s)
    sub = Sx[box[1]:box[3], box[0]:box[2]]
    Sx = np.clip(0.5 + (Sx - sub.mean()) / (sub.std() + 1e-6) * 0.18, 0, 1)
    low = _lowf((H3, W3), 10 * s, rng)                                  # 大きなむら（にじみのゆらぎ）
    gran = _noise((H3, W3), 0.7 * s, rng)                               # 紙の上のつぶつぶ

    # ---------- ぼかし：小さな部分は平らな墨、体と足は筆の塗り重ね ----------
    tones = dict(TONES_DARK if look.get('tones', 'dark') == 'dark' else TONES_LIGHT)
    for key, pid in (('silk', 10), ('sleeve', 11), ('helmet', 12)):
        if key in look:
            tones[pid] = look[key]
    nlw = _gsmooth(nl, groups, 2.0 * s) + (low - 0.5) * 0.22             # 面の向き（落ち影なし）・境目を水でゆらす
    shade = ss_(look.get('sh_t', 0.30), look.get('sh_t', 0.30) - 0.10, nlw)      # 影の段
    deep = np.maximum(ss_(-0.05, -0.25, nlw), ss_(0.58, 0.48, ao)) * shade
    k = np.zeros((H3, W3), np.float32)
    for pid, (b0, b1, b2) in tones.items():
        reg = part == pid
        if reg.any() and pid not in (0, 3):
            k = np.where(reg, b0 + b1 * shade + b2 * deep, k)
    k = k * (0.90 + 0.20 * Sx) * (0.94 + 0.12 * gran)
    coat = np.isin(part, (0, 3))
    cm = coat.astype(np.float32)
    wl = look.get('wash', dict(base=0.42, shadow=0.34, deep=0.26, legs=0.55))
    hi_t = look.get('hi_t', 0.55)
    keep = 1.0 - ss_(hi_t, hi_t + 0.16, lts) * look.get('hi', 0.95)    # 光の当たる所は筆を少なく → 紙の白がすじで残る
    blw = max(1, int(round(0.8 * s)))
    LA = wash_layer((H3, W3), F, cm, coat, wl['base'], 6.5 * u1, 40 * u1, 10.0 * u1, rng, nb=14, lw=blw, dry=0.45, gap=0.50, keep=keep)
    LB = wash_layer((H3, W3), F, cm, coat & (shade > 0.5), wl['shadow'], 5.5 * u1, 26 * u1, 8.0 * u1, rng, nb=12, lw=blw, dry=0.60, gap=0.45)
    LC = wash_layer((H3, W3), F, cm, coat & (deep > 0.5), wl['deep'], 6.0 * u1, 22 * u1, 7.0 * u1, rng, nb=10, lw=blw, dry=0.55, gap=0.5)
    LD = wash_layer((H3, W3), F, cm, part == 3, wl['legs'], 4.0 * u1, 16 * u1, 5.0 * u1, rng, nb=10, lw=blw, dry=0.70, gap=0.3)
    kc = 1 - (1 - LA) * (1 - LB) * (1 - LC) * (1 - LD)
    kc = cv2.GaussianBlur(kc, (0, 0), 0.30 * s)                         # 墨が紙にしみる
    k = np.where(coat, kc * (0.94 + 0.12 * gran), k)
    k = np.clip(k * inside, 0, 1)

    # ---------- 線 ----------
    li = look.get('line_ink', 0.95)
    ins_l = a > 0.08                                                    # ふちのなめらかな画素まで線にする
    din = cv2.distanceTransform(ins_l.astype(np.uint8), cv2.DIST_L2, 5)
    Mb = cv2.GaussianBlur(ins_l.astype(np.float32), (0, 0), 1.5 * s)
    gx = cv2.Sobel(Mb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Mb, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx * gx + gy * gy) + 1e-6
    Fc = np.stack([-gy / gn, gx / gn], -1)                              # ふちにそう向き
    n2 = cv2.GaussianBlur(rng.random((H3, W3)).astype(np.float32), (0, 0), 0.9 * s)
    Sxc = lic(n2, Fc, box, steps=16, h=1.0 * s)
    sub = Sxc[box[1]:box[3], box[0]:box[2]]
    Sxc = np.clip(0.5 + (Sxc - sub.mean()) / (sub.std() + 1e-6) * 0.18, 0, 1)
    press = np.clip(0.50 - nl, 0, 1.2) * 0.75 + np.clip(-ns[..., 1], 0, 1) * 0.65   # 影の側・下向きほど筆をおす
    press = _gsmooth(press, groups, 2.2 * s)
    press = np.where(ins_l & ~inside, cv2.dilate(press, np.ones((3, 3), np.uint8)), press)
    wv = (0.72 + 0.56 * low)                                            # 筆の入り・抜きのゆらぎ
    wsil = lw * s * (2.20 + 2.10 * np.clip(press / 0.8, 0, 1)) * wv
    lost = ss_(0.16, 0.04, press) * ss_(0.50, 0.64, low)                # 光の側は ところどころ細く消えかける
    wsil = wsil * (1 - 0.50 * lost)
    sil = np.zeros((H3, W3), np.float32)
    contour_strokes(sil, ins_l, press, low, rng, u1, s, lw=lw, wmin=look.get('wmin', 1.9), wk=look.get('wk', 2.3))
    sil = np.clip(sil, 0, 1) * ins_l
    pl = np.zeros((H3, W3), np.float32)
    for pids in ((5,), (7,), (10, 11), (12, 15, 16), (13,), (14, 17)):
        pm = np.isin(part, pids)
        if pm.sum() > 30 * s:
            contour_strokes(pl, pm, press, low, rng, u1, s, lw=lw, wmin=1.05, wk=0.9, seg=(18, 40), lost=0.2, nb=7)
    pl = np.clip(pl, 0, 1) * inside
    big = np.where(inside, d, 1e3)
    near = np.zeros(m.shape, bool)
    bound = np.zeros(m.shape, bool)
    soft = (0, 3)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(np.roll(big, dy, 0), dx, 1)
        pnb = np.roll(np.roll(part, dy, 0), dx, 1)
        near |= inside & (nb - big > 0.06) & (nb < 1e3)
        diffp = (pnb != part) & inside & (nb < 1e3) & ~(np.isin(part, soft) & np.isin(pnb, soft))
        bound |= diffp & (big <= nb + 0.01)
    w_in = lw * s * (1.30 + 1.6 * np.clip(press / 0.8, 0, 1)) * wv
    inner = ss_(w_in + 0.7, w_in - 0.7, cv2.distanceTransform((~near).astype(np.uint8), cv2.DIST_L2, 5))
    line = np.clip(np.maximum(np.maximum(sil, pl), inner * inside), 0, 1)
    dryl = ss_(0.60, 0.70, Sxc) * ss_(1.2 * s, 3.2 * s, np.maximum(wsil, w_in * near)) * (0.35 + 0.65 * low)
    line = line * (1 - 0.70 * dryl)                                     # 太い線の中に、筆のかすれ
    # 体の中の折れ目（あご・肩・もも など、面の向きが急に変わる所）：細い線（小さな点は消す）
    nx = np.sum(n * np.roll(n, -1, 1), -1); ny = np.sum(n * np.roll(n, -1, 0), -1)
    crease = (((nx < 0.80) | (ny < 0.80)) & horse).astype(np.uint8)
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(crease, 8)
    big_c = np.isin(lab, np.nonzero(st[:, cv2.CC_STAT_AREA] >= 12 * s)[0][1:])
    cl = _thick(big_c.astype(np.float32), lw * s * look.get('crease_w', 0.55)) * horse
    line = np.maximum(line, cl * (1 - 0.6 * ss_(0.58, 0.70, Sxc)))

    # ---------- 目・鼻の穴・口 ----------
    ex, ey = R['eye']
    u = (np.asarray(R['muzzle']) - np.asarray(R['poll'])) / (hl_ + 1e-9)
    ang = math.degrees(math.atan2(u[1], u[0]))
    r = max(2.0, hl_ * 0.075)
    def ell(cx, cy, ax, ay, rot, a0=0, a1=360, th=-1):
        mm = np.zeros((H3, W3), np.uint8)
        cv2.ellipse(mm, (int(cx * 16), int(cy * 16)), (int(ax * 16), int(ay * 16)), rot, a0, a1, 255, th, cv2.LINE_AA, shift=4)
        return mm.astype(np.float32) / 255
    face = np.zeros((H3, W3), np.float32)
    face = np.maximum(face, ell(ex, ey, r, r * 0.62, ang - 14))
    face = np.maximum(face, ell(ex, ey + 0.15 * r, r * 1.35, r * 0.95, ang - 14, 200, 320, max(1, int(round(1.1 * s)))))
    nx_, ny_ = R['nostril']
    face = np.maximum(face, ell(nx_, ny_, r * 0.85, r * 0.38, ang - 60, 150, 340, max(1, int(round(1.2 * s)))))
    mo = np.asarray(R['mouth'], float)[:2]
    fd = u[:2] / (np.linalg.norm(u[:2]) + 1e-9)
    perp = np.array([-fd[1], fd[0]])
    mz = np.asarray(R['muzzle'], float)[:2]
    pp = np.asarray(R['poll'], float)[:2]
    def L3(img_, pts, wd):
        cv2.polylines(img_, [np.round(np.asarray(pts) * 16).astype(np.int32)], False, 1.0, max(1, int(round(wd))), cv2.LINE_AA, shift=4)
    L3(face, [mo - fd * 3.5 * u1, mo + fd * 1.0 * u1 + perp * 0.6 * u1], 1.2 * u1)
    face = face * horse
    tack = np.zeros((H3, W3), np.float32)                              # 頭のベルト・手綱（細い線）
    ey_ = np.asarray(R['eye'], float)[:2]
    nose = mz + (ey_ - mz) * 0.30
    L3(tack, [nose + perp * 5.5 * u1, nose - perp * 5.0 * u1], 1.5 * u1)
    top = pp + fd * 1.0 * u1 + perp * 1.0 * u1
    L3(tack, [top, (mo + top) / 2 + perp * 2.0 * u1, mo], 1.3 * u1)
    L3(tack, [pp + fd * 3.2 * u1 + perp * 0.5 * u1, pp + fd * 4.5 * u1 - perp * 4.5 * u1], 1.3 * u1)
    hand = np.asarray(R['hand_near'], float)[:2]
    mid = (mo + hand) / 2 + np.array([0.0, 4.0 * u1])
    L3(tack, [(1 - v_) ** 2 * mo + 2 * (1 - v_) * v_ * mid + v_ ** 2 * hand for v_ in np.linspace(0, 1, 18)], 1.2 * u1)
    line = np.maximum(line, np.maximum(face, tack))

    # ---------- たてがみ・前髪・しっぽ（ふくらむ筆の線） ----------
    hair = np.zeros((H3, W3), np.float32)
    hlw = max(1, int(round(0.7 * s)))
    crest = np.asarray(R['crest'], float)[:, :2]
    nC = len(crest)
    for j, i in enumerate(range(nC - 4, 7, -3)):
        p = crest[i]
        tgv = crest[min(i + 1, nC - 1)] - crest[i - 1]
        upa = math.atan2(tgv[1], tgv[0]) - math.pi / 2
        if math.cos(upa) > 0.3:
            upa += math.pi
        root = p - np.array([math.cos(upa), math.sin(upa)]) * 2.5 * u1
        frac = i / nC
        L = (24 + 20 * math.sin(frac * math.pi) + rng.uniform(-5, 7)) * u1 * look.get('mane', 1.0)
        ang_ = upa - 1.15 + rng.uniform(-0.15, 0.12)
        path = flow_path(root, ang_, L, 24, bend=-0.016 + rng.uniform(-0.006, 0.004), wave=1.0, phase=j * 0.8, rng=rng)
        sweep(hair, path, (6.8 + rng.uniform(-1.2, 1.6)) * u1, rng, root=0.22, nb=13, lw=hlw, dry=0.50, split=0.55, gap=0.5)
    for kk in range(2):
        path = flow_path(pp + fd * (4 + 3 * kk) * u1, math.atan2(-fd[1], -fd[0]) - 0.75 - 0.2 * kk, (16 - 3 * kk) * u1, 12, bend=-0.01, rng=rng)
        sweep(hair, path, (5.0 - kk) * u1, rng, root=0.3, nb=9, lw=hlw, dry=0.5, split=0.5)
    cr2, bt2 = Pj(Hm.v3(S['croup'])), Pj(Hm.v3(S['buttock']))
    ys_, xs_ = np.nonzero(horse)
    sel = (ys_ > cr2[1] - 12 * u1) & (ys_ < bt2[1] + 12 * u1) & (xs_ < cr2[0])
    k_ = np.argmin(xs_[sel] * 0.9 + ys_[sel] * 0.44)
    troot = np.array([xs_[sel][k_], ys_[sel][k_]], float) + np.array([3.0, 1.0]) * u1
    R['tail_root'] = troot / s
    t_ang = math.radians(look.get('tail_ang', 176))
    nt = look.get('tail_n', 6)
    for kk in range(nt):
        f = (kk - (nt - 1) / 2)
        L = (look.get('tail_len', 125) - abs(f) * 12 + rng.uniform(-12, 10)) * u1
        path = flow_path(troot + np.array([rng.uniform(-1.5, 1.5), f * 1.6]) * u1, t_ang + f * look.get('tail_spread', 0.075) + rng.uniform(-0.04, 0.04), L, 30,
                         bend=look.get('tail_bend', 0.004) + rng.uniform(-0.005, 0.005), wave=2.4, phase=kk * 1.7, rng=rng)
        sweep(hair, path, (7.2 - abs(f) * 0.9 + rng.uniform(-1, 1.2)) * u1, rng, root=0.15, w_end=0.04, nb=16, lw=hlw, dry=0.46,
              split=0.6, gap=0.55)
    hair = np.clip(hair, 0, 1) * look.get('hair_ink', 1.0)
    jm = np.clip(np.maximum(jock.astype(np.float32), _dist_line(jock.astype(np.float32), 0, 2.0 * s)) * 1.5, 0, 1)
    hair_front = hair * (1 - jm)

    # ---------- 合わせる ----------
    kk_ = np.maximum(k, line * li)
    kk_ = np.maximum(kk_, hair_front)
    A = np.clip(np.maximum(np.maximum(a, sil), np.maximum(hair_front, tack)), 0, 1)
    kk_ = np.where(A > 0, kk_, 0)
    if debug is not None:
        debug.update(part=part, k=k, line=line, Sx=Sx, lts=lts, u1=u1, press=press)
    W1, H1 = W3 // s, H3 // s
    kA = cv2.resize(kk_ * A, (W1, H1), interpolation=cv2.INTER_AREA)
    A1 = cv2.resize(A, (W1, H1), interpolation=cv2.INTER_AREA)
    return np.clip(kA / np.maximum(A1, 1e-4), 0, 1), np.clip(A1, 0, 1)
