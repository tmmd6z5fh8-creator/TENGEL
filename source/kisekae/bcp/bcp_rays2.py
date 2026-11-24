# 結果ボードカスタム（絵の ボード）：わくの 外の 光の すじを きれいに 描き直す（第4.216版）
#   まさちゃん 2026/11/24 11:39「赤丸のところ、枠がガタガタしてたり書き直しが甘かったりするところあるから、確認して描き直して！」
#   （花束 4つの 上と 下・自撮りの 右上：すじが ぼやけて まだらに なり、とちゅうで 暗い かたまりや にじみが あった）
#   作り方（すじの 中心 c の まわりの 極座標 θ・r で 考える）：
#     1. 物（花びら・紙ふぶき・星）を 色で さがし、もとの 絵から ぬいた 地（B）と すき通し（α）を 作る（差の 大きさ → α）
#     2. もとの 絵を θ・r の 絵に（すじは r の 向きに まっすぐ）。物と わくを のぞいて r の 向きに 長い まん中の 値 → θ にも 細い まん中の 値（1〜2行の とびはね＝細い 明るい線・暗い線を 消す）
#     3. θ ごとに、測れた 所より 外は さいごの 120px の まん中の 値から 地の 色へ τ で 弱く。r の 向きに ならす（まだら・にじみ・切れ目を 消す）→ きれいな すじ CF
#     4. わくの そば（near）は もとの 絵 → はなれる ほど CF。物は 上に のせなおす：出す 色 ＝ S ＋ (1−α)・w・(CF − B)（物の まわりに もとの 地が のこらない）
import sys, os, math, numpy as np, cv2
from scipy import ndimage
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def polar_maps(c, thetas, r0, r1):
    """θ（行）× r（列）→ 絵の x・y"""
    rr = np.arange(r0, r1, 1.0, np.float32)
    th = np.asarray(thetas, np.float32)[:, None]
    return (c[0] + rr[None] * np.cos(th)).astype(np.float32), (c[1] + rr[None] * np.sin(th)).astype(np.float32), rr


def nanmedian_filter_r(A, valid, win):
    """θ ごとに r の 向きの まん中の 値（valid の 所 だけ）"""
    out = np.full(A.shape, np.nan, np.float32)
    h = win // 2
    Ap = np.where(valid[..., None], A, np.nan)
    # 1/4 の 細かさで まん中の 値 → もどす（速さ）
    step = 4
    idx = np.arange(0, A.shape[1], step)
    for j0 in idx:
        a, b = max(0, j0 - h), min(A.shape[1], j0 + h + 1)
        out[:, j0] = np.nanmedian(Ap[:, a:b], axis=1)
    for k in range(1, step):
        j = idx + k; j = j[j < A.shape[1]]
        lo = out[:, j - k]; hi = out[:, np.minimum(j - k + step, idx[-1])]
        f = k / step; out[:, j] = lo * (1 - f) + hi * f
    return out


def nanmedian_theta(A, k):
    """θ の 向きに k 行の まん中の 値（NaN は 使わない）"""
    h = k // 2; n = A.shape[0]; out = np.empty_like(A)
    for ch in range(A.shape[2]):
        st = np.stack([A[np.clip(np.arange(n) + d, 0, n - 1), :, ch] for d in range(-h, h + 1)], 0)
        out[..., ch] = np.nanmedian(st, axis=0)
    return out


def objects_matte(S, allow, edge_row, dbg=None):
    """S の 中の 物（花びら・紙ふぶき・星）→ α（0〜1）・物を ぬいて うめた 地 B・物の 所 Md（B を うめた 所）
       allow：さがす 所・edge_row：もとの 絵の はし（ここで 切れて いる 物は のせない）"""
    u8 = np.clip(S + 0.5, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    loc = v - cv2.GaussianBlur(v, (0, 0), 10)
    pink = ((h > 300) | (h < 12)) & (s > 0.15) & (v > 0.35)                      # 花びら
    sat = (s > 0.45) & (v > 0.3)
    red = sat & ((h >= 335) | (h < 12)); mag = sat & (h >= 270) & (h < 335)          # 紙ふぶき（色ごと：すじの 色と つながって 大きく ならない ように）
    blu = sat & (h >= 180) & (h < 270); grn = sat & (h >= 70) & (h < 180)
    org = (s > 0.5) & (v > 0.85) & (h >= 12) & (h < 35) & (loc > 0.10)            # だいだい・黄色の 紙ふぶき（すじより あざやかで 明るい）
    yel = (s > 0.5) & (v > 0.85) & (h >= 35) & (h < 70) & (loc > 0.10)
    wht = (v > 0.82) & (s < 0.32) & (loc > 0.12)                                 # 星・白い 紙ふぶき
    gry = (v > 0.55) & (s < 0.25) & (loc > 0.06)                                 # 灰色の 紙ふぶき（あざやかな すじの 中の 色の ない もの）
    M0 = np.zeros(S.shape[:2], bool)
    for mk in (pink, red, mag, blu, grn, org, yel, wht, gry):                           # 大きな かたまり（すじ そのもの）は 物に しない
        mk = mk & allow; lab0, n0 = ndimage.label(mk)
        if n0:
            sz0 = ndimage.sum(mk, lab0, range(1, n0 + 1)); M0 |= np.isin(lab0, np.nonzero(sz0 < 15000)[0] + 1)
    pale = (v > 0.8) & (s < 0.6) & (loc > 0.08)                                  # 紙ふぶき・花びらの 明るい まん中（うすい 黄色・うすい ピンク）
    M = M0 | (pale & allow & (cv2.dilate(M0.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))) > 0))
    M = cv2.morphologyEx(M.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
    M = ndimage.binary_fill_holes(cv2.morphologyEx(M.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0) & allow
    lab, n = ndimage.label(M)
    if n:                                                                          # 物は ふくらんだ 形（紙ふぶき・花びら）：かけた 所（C の 形）は 外の 形で うめる
        hull = np.zeros(M.shape, np.uint8)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if sl is None: continue
            sub = (lab[sl] == i + 1)
            if sub.sum() < 12 or sub.sum() > 12000: continue
            ys_, xs_ = np.nonzero(sub); pts = np.stack([xs_ + sl[1].start, ys_ + sl[0].start], 1).astype(np.int32)
            cv2.fillPoly(hull, [cv2.convexHull(pts)], 1)
        M = (M | (hull > 0)) & allow
        lab, n = ndimage.label(M)
    if n:
        sizes = ndimage.sum(M, lab, range(1, n + 1)); small = np.nonzero(sizes < 6)[0] + 1
        cut = np.unique(lab[max(0, edge_row - 2):edge_row + 3]); cut = cut[cut > 0]
        Mall = M & ~np.isin(lab, small)                                            # はしで 切れた 物も ふくむ（すじを 測る ときは 使わない）
        M &= ~np.isin(lab, np.concatenate([small, cut]))
    Md = cv2.dilate(M.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0
    B = cv2.inpaint(u8, Md.astype(np.uint8), 6, cv2.INPAINT_TELEA).astype(np.float32)
    B = np.where(Md[..., None], B, S)
    dev = np.abs(S - B).max(2)
    a = np.clip((dev - 8.0) / 30.0, 0, 1); a = a * a * (3 - 2 * a) * Md
    core = cv2.erode(M.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    a = np.maximum(a, core.astype(np.float32))
    a = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 0.7) * Md
    if dbg is not None: dbg.update(M=M, alpha=a)
    Mx = cv2.dilate(((Mall & ~M) if n else np.zeros_like(M)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0      # はしで 切れて のせない 物
    return np.clip(a, 0, 1), B, Md, Mx


def redraw(E, S, c, side, keep, seam, art_end=None, win=201, sig_r=30.0, edge_skip=60, tau=240.0, near=(20, 90), floor=(10, 8, 16), th_med=7, tail_n=120, dbg=None):
    """E＝今の 絵（float32・RGB・足した 所も ある）・S＝もとの 絵（同じ 大きさ）・c＝すじの 中心・side＝'top'／'bottom'
       keep＝わく（花・板：さわらない・r_ref の もと）・seam＝すじを 測る もとの 絵の はし（top：これより 上・bottom：これより 下 は 使わない）
       art_end＝もとの 絵の 物が のこって いる はし（bottom：ここまでの 物を のせる。既定は seam）→ 新しい 絵"""
    H, W = E.shape[:2]
    ae = seam if art_end is None else art_end
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    half = (ys < c[1]) if side == 'top' else (ys > c[1])
    obj_rows = ((ys >= ae) if side == 'top' else (ys <= ae)) & half
    Sx = np.where(obj_rows[..., None], S, E)
    a, B, Md, Mcut = objects_matte(Sx, obj_rows & ~keep, int(ae), dbg)
    n_th = 2600
    th = np.linspace(-math.pi + 0.01, -0.01, n_th) if side == 'top' else np.linspace(0.01, math.pi - 0.01, n_th)
    rmax = float(np.hypot(max(c[0], W - c[0]), max(c[1], H - c[1]))) + 10
    mx, my, rr = polar_maps(c, th, 0, rmax)
    inside = (mx >= 0) & (mx <= W - 1) & (my >= 0) & (my <= H - 1)
    PI = np.stack([cv2.remap(Sx[..., k], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) for k in range(3)], -1)
    KI = cv2.remap(keep.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderValue=0) > 0.5
    MI = cv2.remap((Md | Mcut).astype(np.float32), mx, my, cv2.INTER_LINEAR, borderValue=0) > 0.3
    orig = (my >= seam + edge_skip) if side == 'top' else (my <= seam - edge_skip)
    kk = KI & inside
    r_ref = np.where(kk.any(1), kk.shape[1] - 1 - np.argmax(kk[:, ::-1], axis=1), 0).astype(np.float32)
    rel = rr[None, :] - r_ref[:, None]
    valid = inside & orig & ~KI & ~MI & (rel > 3)
    RM = nanmedian_filter_r(PI, valid, win)
    RM = nanmedian_theta(np.where(valid[..., None], RM, np.nan), th_med)
    fl = np.array(floor, np.float32)
    good = np.isfinite(RM[..., 0])
    CF = np.zeros_like(PI); jj = np.arange(PI.shape[1])
    for i in range(n_th):
        g = np.nonzero(good[i])[0]
        if len(g) < 8:
            CF[i] = fl; continue
        row = np.stack([np.interp(jj, g, RM[i, g, k]) for k in range(3)], -1)
        j0, j1 = g.min(), g.max()
        tailv = np.median(RM[i, g[g >= j1 - tail_n]], axis=0)
        d = np.maximum(jj - j1, 0)[:, None]
        row = np.where(d > 0, fl + (tailv - fl) * np.exp(-d / tau), row)
        row[:j0] = row[j0]
        CF[i] = row
    CF = ndimage.gaussian_filter1d(CF, sig_r, axis=1, mode='nearest')
    CF = ndimage.gaussian_filter1d(CF, 0.7, axis=0, mode='nearest')
    dx, dy = xs - c[0], ys - c[1]
    T = np.arctan2(dy, dx); R = np.hypot(dx, dy)
    ti = ((T - th[0]) / (th[-1] - th[0]) * (n_th - 1)).astype(np.float32); ri = (R - rr[0]).astype(np.float32)
    region = (ti >= 0) & (ti <= n_th - 1) & half
    CFc = np.stack([cv2.remap(CF[..., k], ri, ti, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) for k in range(3)], -1)
    relc = cv2.remap(rel.astype(np.float32), ri, ti, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    w = np.clip((relc - near[0]) / (near[1] - near[0]), 0, 1); w = w * w * (3 - 2 * w)
    in_art = (ys >= seam) if side == 'top' else (ys <= seam)
    w = np.maximum(np.where(in_art, w, 1.0), cv2.GaussianBlur(Mcut.astype(np.float32), (0, 0), 2.0)) * region * (~keep)      # 切れて のせない 物は わくの そばでも すじに
    out = Sx + ((1 - a) * w)[..., None] * (CFc - B)
    out = np.where(region[..., None], out, E)
    if dbg is not None: dbg.update(w=w, CF=CFc, obj=Md)
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- デザインごとの きまり（すじの 中心・測る はし・物が のこる はし）
#   花束：上は もとの 絵の 上 251／280 行から 上が 足した 所・下は 1836／1864 行から 下（2093／2121 行までは もとの 絵の 物が ある）
#   自撮り：上の 343 行（338 ＋ 5）から 上が 足した 所（右上の すじが ぼやけて、黄色い 紙ふぶきの すじが のこって いた）
RAYS = {'bouquet1': [('top', 251, (585, 1332), None), ('bottom', 1836, (504, 1126), 2093)]}
for _k in ('bouquet2', 'bouquet3', 'bouquet4'):
    RAYS[_k] = [('top', 280, (585, 1360), None), ('bottom', 1864, (495, 1154), 2121)]
for _k in ('selfie1', 'selfie2', 'selfie3', 'selfie4'):
    RAYS[_k] = [('top', 343, (714, 955), None)]


def keep_mask(E, name, q, fga=None):
    """さわらない 所（板・わく・花・キャラ）。花束：板の まわりの 花・葉・リボン・白い 花（板から 250px まで）／自撮り：板の まわり 45px と 前の 絵（キャラ・自撮り棒）"""
    H, W = E.shape[:2]
    quad = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(quad, np.round(np.asarray(q)).astype(np.int32), 1)
    if name.startswith('selfie'):
        k = cv2.dilate(quad, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (91, 91))) > 0
        if fga is not None: k |= cv2.dilate(np.asarray(fga).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))) > 0
        return k
    hsv = cv2.cvtColor(np.clip(E, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    flower = (s > 0.42) & ~((h > 36) & (h < 62) & (s < 0.75)) & (v > 0.25)        # 花・葉・リボン（すじの 黄色 では ない あざやかな 色）
    white = (v > 0.85) & (s < 0.25)
    cand = (flower | white) & (quad == 0)
    near = cv2.dilate(quad, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (501, 501))) > 0
    seed = cv2.dilate(quad, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))) > 0
    cl = cv2.morphologyEx((cand & near).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))) > 0
    lab, n = ndimage.label(cl | seed); ids = np.unique(lab[seed]); keep = np.isin(lab, ids[ids > 0])
    keep = ndimage.binary_fill_holes(keep)
    return cv2.dilate(keep.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0


def fix(E, S, name, q, fga=None):
    """E（上下を 足した 絵）の すじを 描き直す（RAYS に ある デザイン だけ）→ 新しい 絵（float32）"""
    if name not in RAYS:
        return E
    keep = keep_mask(E, name, q, fga); out = np.asarray(E, np.float32)
    for side, seam, c, ae in RAYS[name]:
        out = redraw(out, np.asarray(S, np.float32), c, side, keep, seam, art_end=ae)
    return out
