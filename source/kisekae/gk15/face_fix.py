# 神様極的中：はじめの 神様馬の 顔の ほおの「かげの ような まだら」を けす（第4.215版・まさちゃん 2026/11/24 01:35 ①）
#   「演出スタート時の 神様馬の 顔が、赤丸の 箇所に 変な 影みたいなのが 入って いるから、無くして 綺麗に 直して！」
#   もとの 3D（顔）は もう ない ので、できた 動画（第14稿）の コマを 直す（コマ 30〜112：顔が 見えて いる 間）。
#   ・ほおの 形（左の ほお L1・左の あご L2・右の ほお R1：コマ 90 で 決めた）を、顔の 動きに 合わせて コマごとに うつす（face_track.json：face_track.py が ほお 1つずつ 追った 平面の 変形）
#   ・はじめ（〜コマ 62：ほおが 細い 光の 帯）：帯の 長い 向きに そって 見た「明るい 面の 明るさ」で、暗い まだら だけ うめる（ふちの 光の 線・帯の ふちは そのまま ＝ ぼやけない）
#   ・あと（コマ 78〜：ほおが 広い 面）：まわりを 広く ならした 明るさ（平均）と ちがう 所 だけ 入れかえる（62〜78 は 2つを 少しずつ まぜる）
#   ・金の かざり・目の 光・雷は さわらない
#   使い方（GK15_WORK＝作業フォルダ：src/0000.png… に 第14稿の コマ。何も 決めないと /home/claude/work/v215/gk）：
#     python3 face_fix.py --run [はじめ おわり]      … face_out/<コマ>.png を 作る（level.json＝コマごとの ほおの 明るさ も）
#     python3 face_fix.py <コマ,コマ…> <出す png> [倍率]  … 直す 前（形の 線つき）と 後を ならべた 点検の 絵
import numpy as np, cv2, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('GK15_WORK', '/home/claude/work/v215/gk')
REF = 90
# ほおの 形（コマ 90 の 画素：780×1688）
POLY = dict(
    L1=[(192, 760), (215, 742), (252, 733), (292, 748), (314, 800), (320, 880), (314, 944), (301, 966), (278, 984), (254, 984), (232, 955), (216, 915), (201, 872), (194, 825), (187, 790)],
    L2=[(118, 905), (150, 880), (182, 882), (202, 925), (214, 970), (224, 1015), (230, 1060), (224, 1110), (198, 1135), (150, 1135), (118, 1100), (108, 1000), (110, 940)],
    R1=[(466, 765), (515, 746), (556, 760), (588, 800), (606, 800), (614, 806), (607, 852), (588, 892), (562, 932), (544, 960), (524, 965), (498, 992), (482, 1000), (460, 988), (456, 960), (450, 890), (450, 815)],
)
TRACK = {n: {int(f): np.array(H) for f, H in d.items()} for n, d in json.load(open(os.path.join(HERE, 'face_track.json'))).items()}
LO, HI = min(TRACK['L1']), 112                                                    # 113 は ばくはつの かけらが 顔の 前を とぶ コマ（目の 光で ほおも 白く とぶ）＝ さわらない
L2_FROM = 64                                                                     # 左の あご（L2）は はじめは 見えない（まっ暗）＝ ここから 少しずつ（L2_FULL で ぜんぶ）
L2_FULL = 74


def warp_pts(H, p):
    q = np.hstack([p, np.ones((len(p), 1))]) @ H.T; return q[:, :2] / q[:, 2:3]


def masks(f, shape, names=None):
    """コマ f の ほおの 形（0/1）。ほお 1つずつ、その コマの 変形（ホモグラフィ：track2.py）で うつす"""
    m = np.zeros(shape[:2], np.uint8)
    if not LO <= f <= HI: return m
    for name, pts in POLY.items():
        if names and name not in names: continue
        if name == 'L2' and f <= L2_FROM: continue
        q = warp_pts(TRACK[name][f], np.array(pts, np.float64)); cv2.fillPoly(m, [np.round(q).astype(np.int32)], 1)
    return m


def level(img, f):
    """ほお（L1・R1）の 明るさ（まん中の 値）：はじめの 暗い コマも コマ 90 と 同じ 明るさに そろえて から 直す ため"""
    M = masks(f, img.shape, ('L1', 'R1')) > 0
    if not M.any(): return 0.0
    return float(np.median(img.astype(np.float32).mean(2)[M]))


LEVEL = {}
REF_LEVEL = 93.0; BIG = 1e5


def frame(f):
    return cv2.imread(os.path.join(WORK, 'src', f'{f:04d}.png'))


def levels():
    """コマごとの ほおの 明るさ（level.json に とって おく：ない ときは 第14稿の コマから はかる）"""
    if not LEVEL:
        p = os.path.join(WORK, 'level.json')
        if os.path.exists(p): LEVEL.update({int(k): v for k, v in json.load(open(p)).items()})
        else:
            LEVEL.update({f: level(frame(f), f) for f in range(LO, max(TRACK['L1']) + 1)}); json.dump(LEVEL, open(p, 'w'))
    return LEVEL


def gain(f):
    """コマ f を 何倍に して 直すか（暗い はじめの コマ ほど 大きい・上は 10倍 まで）。前後 2コマ ならして から"""
    L = levels(); v = [L[k] for k in range(f - 2, f + 3) if k in L]
    if not v: return 1.0
    return float(np.clip(REF_LEVEL / max(np.mean(v), 1e-3), 1.0, 10.0))


def _disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)


def scale_of(name, f):
    """その コマで ほおが コマ 90 の 何倍の 大きさで 写って いるか（よこ・たて）：ならす 広さを ほおの 上で 同じに する ため"""
    H = TRACK[name][f]; c = np.array(POLY[name], np.float64).mean(0, keepdims=True); e = 4.0
    p = warp_pts(H, np.vstack([c, c + [e, 0], c + [0, e]]))
    return float(np.linalg.norm(p[1] - p[0]) / e), float(np.linalg.norm(p[2] - p[0]) / e)


def _mblur(X, w, sx, sy=None):
    sy = sx if sy is None else sy
    if X.ndim == 3: return cv2.GaussianBlur(X * w[..., None], (0, 0), sigmaX=sx, sigmaY=sy) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigmaX=sx, sigmaY=sy), 1e-3)[..., None]
    return cv2.GaussianBlur(X * w, (0, 0), sigmaX=sx, sigmaY=sy) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigmaX=sx, sigmaY=sy), 1e-3)


def _chains(pts):
    """形の 点を、いちばん 上の 点と いちばん 下の 点で 左の 辺・右の 辺に 分ける（上 → 下）"""
    p = np.array(pts, np.float64); n = len(p); t = int(np.argmin(p[:, 1])); b = int(np.argmax(p[:, 1]))
    c1 = [p[(t + k) % n] for k in range(((b - t) % n) + 1)]; c2 = [p[(t - k) % n] for k in range(((t - b) % n) + 1)]
    c1, c2 = np.array(c1), np.array(c2)
    return (c1, c2) if c1[:, 0].mean() < c2[:, 0].mean() else (c2, c1)


def _resample(c, n):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]; t = np.linspace(0.004, 0.996, n) * d[-1]
    return np.stack([np.interp(t, d, c[:, 0]), np.interp(t, d, c[:, 1])], 1)


_GRID = {}


def strip_grid(name):
    """ほおの 面の 上の ます目（もとの コマ 90 の 画素）：たて（v）＝ ほおの 長い 向き（左右の 辺に そう）・よこ（u）＝ 左の 辺 → 右の 辺"""
    if name not in _GRID:
        L, R = _chains(POLY[name]); nv = int(round(max(np.linalg.norm(np.diff(L, axis=0), axis=1).sum(), np.linalg.norm(np.diff(R, axis=0), axis=1).sum())))
        Lr, Rr = _resample(L, nv), _resample(R, nv); nu = int(round(np.linalg.norm(Rr - Lr, axis=1).max()))
        u = np.linspace(0, 1, nu)[None, :, None]; _GRID[name] = Lr[:, None, :] * (1 - u) + Rr[:, None, :] * u                # (nv, nu, 2)
    return _GRID[name]


def strip_base(F, prot, name, f, sig_v=45.0, sig_u=2.5, r_dark=5, light=True):
    """ほおの 長い 向き（辺に そう 向き）へ だけ 広く ならした 明るさ。
       ふちの 光の 線・ほおの ふち・面の 外の 闇は 長い 向きに そって いる ＝ ならしても そのまま のこる（ぼやけない）。
       まだら（ぎざぎざの 島）は 長い 向きに ならすと 消えて、つやの すじ（なめらかな たての 明るさ）に なる"""
    G = strip_grid(name); H = TRACK[name][f]; nv, nu = G.shape[:2]
    P = warp_pts(H, G.reshape(-1, 2)).reshape(nv, nu, 2).astype(np.float32)
    S = cv2.remap(F, P[..., 0], P[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    ps = cv2.remap(prot.astype(np.float32), P[..., 0], P[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) > 0.01
    ok = ~ps
    if r_dark:                                                                       # 細い 暗い すじ・点は 先に うめる
        o3 = ok[..., None]; a = np.where(o3, S, 0.0).astype(np.float32); a = cv2.dilate(a, _disk(r_dark)); a = np.where(o3, a, BIG).astype(np.float32); S = np.where(o3, cv2.erode(a, _disk(r_dark)), S)
    # ほおの 光の 帯の ふち（左・右）を 行ごとに 見つけて まっすぐに のばして から ならす（ふちが ぴったり 長い 向きに そう ＝ ふちが ぼやけない）
    w = ok.astype(np.float32); lum = S.mean(2)
    Pv = _mblur(lum, w, 1.5, 12.0); mx = np.maximum(Pv.max(1, keepdims=True), 1e-3); on = Pv > 0.3 * mx
    uL = np.argmax(on, 1).astype(np.float32); uR = (nu - 1 - np.argmax(on[:, ::-1], 1)).astype(np.float32)
    thin = (uR - uL) < 0.25 * (nu - 1)                                                # 帯が 見つからない 行（暗い・細すぎる）は 形の はば ぜんぶ
    uL[thin] = 0; uR[thin] = nu - 1
    uL = cv2.GaussianBlur(uL[:, None], (0, 0), sigmaX=0.1, sigmaY=10.0)[:, 0]; uR = cv2.GaussianBlur(uR[:, None], (0, 0), sigmaX=0.1, sigmaY=10.0)[:, 0]
    wd = np.maximum(uR - uL, 8.0); mid_w = float(np.median(wd)); pad = int(np.ceil(max(uL.max(), (nu - 1 - uR).max()) / max(wd.min(), 8.0) * mid_w)) + 4
    nk = int(round(mid_w)) + 2 * pad + 1; k = np.arange(nk, dtype=np.float32)[None, :]
    mapx = (uL[:, None] + (k - pad) / mid_w * wd[:, None]).astype(np.float32); mapy = np.repeat(np.arange(nv, dtype=np.float32)[:, None], nk, 1)
    St = cv2.remap(S, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); wt = cv2.remap(w, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wt = wt * ((mapx >= 0) & (mapx <= nu - 1))
    if light:
        # 明るい 面の 明るさ（長い 向きに そって 見た 上から 2わりの 所）→ それより 暗い まだらを うめる ための 明るさ
        from scipy.ndimage import percentile_filter
        lt = St.mean(2); lt_ok = np.where(wt > 0.5, lt, 0.0)
        p80 = percentile_filter(lt_ok, 80, size=(2 * 90 + 1, 1), mode='nearest'); p80 = cv2.GaussianBlur(p80, (0, 0), sigmaX=1.2, sigmaY=6.0)
        wl = ((lt >= 0.80 * p80) & (wt > 0.5)).astype(np.float32)
        n1 = cv2.GaussianBlur(wl, (0, 0), sigmaX=1.5, sigmaY=14.0); L1 = cv2.GaussianBlur(St * wl[..., None], (0, 0), sigmaX=1.5, sigmaY=14.0) / np.maximum(n1, 1e-3)[..., None]
        n2 = cv2.GaussianBlur(wl, (0, 0), sigmaX=2.5, sigmaY=50.0); L2 = cv2.GaussianBlur(St * wl[..., None], (0, 0), sigmaX=2.5, sigmaY=50.0) / np.maximum(n2, 1e-4)[..., None]
        a = np.clip((n1 - 0.04) / 0.10, 0, 1)[..., None]; Bt = L1 * a + L2 * (1 - a)
        Bt = np.where((n2 > 1e-3)[..., None], Bt, St)
        Bt = cv2.GaussianBlur(Bt, (0, 0), sigmaX=2.0, sigmaY=3.0)
    else:
        Bt = _mblur(St, wt, sig_u, sig_v)
    j = np.arange(nu, dtype=np.float32)[None, :]; kx = ((j - uL[:, None]) / wd[:, None] * mid_w + pad).astype(np.float32)
    Bs = cv2.remap(Bt, kx, np.repeat(np.arange(nv, dtype=np.float32)[:, None], nu, 1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # コマの 画素 → ます目の 位置（あらい 点で 三角に 分けて うめる）
    from scipy.interpolate import LinearNDInterpolator
    ii, jj = np.meshgrid(np.r_[np.arange(0, nv - 1, 4), nv - 1], np.r_[np.arange(0, nu - 1, 4), nu - 1], indexing='ij')
    pts = P[ii, jj].reshape(-1, 2).astype(np.float64); val = np.stack([ii.ravel(), jj.ravel()], 1).astype(np.float64)
    _, keep = np.unique(np.round(pts, 3), axis=0, return_index=True)
    it = LinearNDInterpolator(pts[keep], val[keep])
    x0, y0 = np.floor(P.reshape(-1, 2).min(0)).astype(int) - 2; x1, y1 = np.ceil(P.reshape(-1, 2).max(0)).astype(int) + 3
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, F.shape[1]), min(y1, F.shape[0])
    X, Y = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1)); q = it(np.stack([X.ravel(), Y.ravel()], 1)).reshape(Y.shape + (2,))
    bad = np.isnan(q[..., 0]); q = np.nan_to_num(q).astype(np.float32)
    part = cv2.remap(Bs, q[..., 1], q[..., 0], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    base = F.copy(); valid = np.zeros(F.shape[:2], bool)
    base[y0:y1, x0:x1][~bad] = part[~bad]; valid[y0:y1, x0:x1] = ~bad
    return base, valid


def _replace(F, base, M, inside, t_light, t_dark, feather, strength, rel=None):
    """base と ちがう 所 だけ 入れかえる（まだらで ない 所は そのまま）。t_light＝None：base より 暗い 所 だけ（rel＝base の 何わり 暗ければ）"""
    d = F.mean(2) - base.mean(2)
    if t_light is None: patch = (d < -np.maximum(t_dark, rel * base.mean(2))) & inside
    else: patch = ((d > t_light) | (d < -t_dark)) & inside
    patch = cv2.dilate(patch.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    m = cv2.GaussianBlur(patch, (0, 0), 1.6)
    edge = np.clip(cv2.GaussianBlur(M.astype(np.float32), (0, 0), feather) * 2 - 1, 0, 1)      # 形の はしでは 0（外へ にじませない・内がわへ ふわっと）
    m = np.clip(m * 1.3, 0, 1) * edge * inside * strength
    return F + (base - F) * m[..., None], m


def _speck_pass(F, M, prot, r_open, r_close, sig, t_light, t_dark, feather, strength):
    """M の 中の 小さな 明るい 点・暗い 点 だけ（形で けずる：半径 r_open より 小さい 明るい 点・r_close より 小さい 暗い 点）"""
    Mb = M > 0; inside = Mb & ~prot; lum = F.mean(2)
    def opening(X, r):
        a = np.where(inside[..., None], X, BIG).astype(np.float32); a = cv2.erode(a, _disk(r))
        b = np.where(inside[..., None], a, 0.0).astype(np.float32); return cv2.dilate(b, _disk(r))
    def closing(X, r):
        a = np.where(inside[..., None], X, 0.0).astype(np.float32); a = cv2.dilate(a, _disk(r))
        b = np.where(inside[..., None], a, BIG).astype(np.float32); return cv2.erode(b, _disk(r))
    B0 = closing(opening(F, r_open), r_close)
    w = inside.astype(np.float32); num = cv2.GaussianBlur(B0 * w[..., None], (0, 0), sig); den = cv2.GaussianBlur(w, (0, 0), sig)[..., None]
    base = num / np.maximum(den, 1e-3)
    d = lum - base.mean(2)
    patch = ((d > t_light) | (d < -t_dark)) & inside
    patch = cv2.dilate(patch.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    m = cv2.GaussianBlur(patch, (0, 0), 1.6)
    edge = np.clip(cv2.GaussianBlur(M.astype(np.float32), (0, 0), feather) * 2 - 1, 0, 1)
    m = np.clip(m * 1.3, 0, 1) * edge * (~prot) * strength
    return F + (base - F) * m[..., None], m


SIG = 18.0                                                                           # まるく ならす 広さ（コマ 90 の ほおの 上で・px）
ISO = (62, 78)                                                                       # 長い 向き だけ（はじめ：ほおが 細い 光の 帯）→ まるく（あと：ほおが 広い 面）へ うつる コマ


def iso_w(f):
    t = float(np.clip((f - ISO[0]) / (ISO[1] - ISO[0]), 0, 1)); return t * t * (3 - 2 * t)


def fix(img, f, strength=1.0, dbg=None):
    """img＝BGR uint8（コマ f）。→ 直した コマ（uint8）。コマ LO〜HI の 外は そのまま。
       まだら＝ほおの「明るい 面と 暗い 面が ぎざぎざに 分かれた もよう（かげの ような もの）」と「細い 暗い すじ・点」。
       1回目（ほお 1つずつ・形の 中）：
         はじめ（ISO[0] まで）：strip_base（帯の 長い 向きの 明るい 面の 明るさ）より 7% より 暗い 所 だけ うめる
         あと（ISO[1] から）・左の あご（L2）：まるく 広く ならした 明るさ（平均）と ちがう 所 だけ 入れかえる（まだらで ない 所は そのまま ＝ のっぺり しない）
       2回目（ほおの まわり 12px：帯の ふち・鼻の 帯の はし）：小さな 明るい 点・暗い 点 だけ（半径 5・3）
       暗い はじめの コマは、ほおの 明るさを コマ 90 と そろえて から 直して、もとの 明るさへ もどす（gain）"""
    F0 = img.astype(np.float32); M = masks(f, F0.shape)
    if M.max() == 0: return img
    g = gain(f); F = F0 * g
    Z = cv2.dilate(M, _disk(12))
    # さわらない もの：雷・金の つや ＝ 明るくて（もとの 赤が 218 より 上）細い もの（半径 5 より 細い：まわりより 25 より 明るい）と、まっ白に とんだ 所。
    #   目の 光が 大きく ふくらむ さいごの コマ（111〜）は ほおの 上まで 明るく なる：広く 明るい だけの 所は まもらない（まだらが のこって しまう）
    R = F0[..., 2]; th = R - cv2.morphologyEx(R, cv2.MORPH_OPEN, _disk(5))
    Rs = cv2.GaussianBlur(R, (0, 0), 14.0)                                             # まわりが 広く 明るい 所（目の 光の ふくらみの 中）ほど、細い 明るい もの と 見る めやすを 上げる
    br = ((R > 218) & (th > 25 + 0.6 * np.maximum(Rs - 180, 0))) | (F0.min(2) > 245)
    #   （雷の あわい 所まで つづけて まもる 形も ためした：まだらの 明るい 細い かけらまで まもって しまい 白い すじが のこる ＝ やめた）
    # 小さな まるい 明るい 点（はがれた 点の いちばん 明るい もの）は まもらない：雷・金の つやは 細長い（長さ 16px より 上）か、形の 外へ つづく
    n, lab = cv2.connectedComponents(br.astype(np.uint8), connectivity=8)
    if n > 1:
        ys, xs = np.nonzero(br & (Z > 0)); ids = np.unique(lab[ys, xs]); keep = np.ones(n, bool)
        outside = np.unique(lab[br & (Z == 0)])
        for k in ids:
            if k == 0 or k in outside: continue
            yy, xx = np.nonzero(lab == k)
            if max(np.ptp(yy), np.ptp(xx)) < 16: keep[k] = False
        br = keep[lab] & br
    prot = cv2.dilate(br.astype(np.uint8), _disk(2)) > 0
    o = F; mt = np.zeros(F.shape[:2], np.float32); t = iso_w(f)
    for name in POLY:
        Mn = masks(f, F0.shape, (name,))
        if Mn.max() == 0: continue
        inside = (Mn > 0) & ~prot; sx, sy = scale_of(name, f)
        k = strength * (float(np.clip((f - L2_FROM) / (L2_FULL - L2_FROM), 0, 1)) if name == 'L2' else 1.0)
        late = None
        if name == 'L2' or t > 0:                                                    # あと：ほおが 広い 面 ＝ まるく ならした 明るさ（平均）と ちがう 所を 入れかえる
            base = _mblur(o, inside.astype(np.float32), max(SIG * sx, 5.0), max(SIG * sy, 5.0))
            late, m1 = _replace(o, base, Mn, inside, 7.0, 9.0, 3.0, k); mt = np.maximum(mt, m1)
        if name != 'L2' and t < 1:                                                   # はじめ：ほおが 細い 光の 帯 ＝ 長い 向きに そった 明るい 面の 明るさで、暗い まだら だけ うめる（ふちの 光の 線は そのまま）
            base, valid = strip_base(o, prot, name, f)
            early, m1 = _replace(o, base, Mn, inside & valid, None, 6.0, 3.0, k, rel=0.07); mt = np.maximum(mt, m1)
            o = early if late is None else early * (1 - t) + late * t
        else:
            o = late
    o, m2 = _speck_pass(o, Z, prot, 5, 3, 3.0, 14.0, 18.0, 3.0, strength); mt = np.maximum(mt, m2)
    o = o / g
    rng = np.random.default_rng(1000 + f); o = o + (rng.random(o.shape[:2], np.float32)[..., None] - 0.5) * 1.0 * (mt[..., None] > 0.02)    # 入れかえた 所は ごく 細かい つぶを 足す（なめらかな 面の しま ＝ 段を 出さない）
    if dbg is not None: dbg.update(M=M, prot=prot, m=mt, Z=Z, g=g)
    return np.clip(o + 0.5, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == '--run':
        out = os.path.join(WORK, 'face_out'); os.makedirs(out, exist_ok=True)
        lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (LO, HI)
        for f in range(lo, hi + 1):
            cv2.imwrite(os.path.join(out, f'{f:04d}.png'), fix(frame(f), f))
            if f % 10 == 0: print(f, flush=True)
        print('ok', out); sys.exit(0)
    fs = [int(x) for x in sys.argv[1].split(',')]; rows = []
    for f in fs:
        img = frame(f); d = {}
        o = fix(img, f, dbg=d)
        x0, y0, x1, y1 = 100, 640, 680, 1160
        v = img.copy(); cnt, _ = cv2.findContours(d['M'].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(v, cnt, -1, (255, 0, 255), 1)
        gg = min(d.get('g', 1.0), 6.0); up = lambda a: np.clip(a.astype(np.float32) * gg, 0, 255).astype(np.uint8)
        t = np.hstack([up(v[y0:y1, x0:x1]), up(o[y0:y1, x0:x1])]); cv2.putText(t, f'{f} x{gg:.1f}', (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2); rows.append(t)
    z = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    sh = np.vstack(rows) if len(rows) <= 2 else np.vstack([np.hstack(rows[i:i + 2]) for i in range(0, len(rows) - len(rows) % 2, 2)])
    cv2.imwrite(sys.argv[2], cv2.resize(sh, None, fx=z, fy=z, interpolation=cv2.INTER_AREA if z < 1 else cv2.INTER_LANCZOS4))
