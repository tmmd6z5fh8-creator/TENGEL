# 結果ボードカスタム（絵の ボード）：板の ふち（わくの 内がわの さかい）の ガタガタを 直す（第4.216版）
#   まさちゃん 2026/11/24 11:39「赤丸のところ、枠がガタガタしてたり書き直しが甘かったりするところあるから、確認して描き直して！」
#   （乾杯の ボード：わくの 内がわの ふち（板との さかいの 少し 暗い 段）が、ところどころ 四角く 出っぱったり へこんだり して いた＝もとの 絵の まま）
#   作り方（bcp_blank.clean が 作った 板の 形 geo を 使う）：
#     1. 板を まっすぐな 四角に 直して（射影）、角の まるい 四角の ふちに そって「ほどいた 帯」を 作る（よこ＝ふちに そった 場所 s・たて＝ふちからの きょり d：＋＝板の 中）
#     2. s ごとに 板の 紺が はじまる 所 b(s)（板の 中から 外へ 見て、はじめて 紺で なくなる 所）。長い まん中の 値で なめらかな さかい b_fit(s)
#     3. 帯の s の 向きに 長い まん中の 値 → その 場所の「ふつうの ふち」の 断面（わくの 段 → 暗い すじ → 板）。
#        段（d＝dlo〜さかい）が ふつうと ちがう 所（四角い 出っぱり・へこみ・明るさの ちがう 段）は、ふつうの 断面で ぬり直す
#        （わくの 外がわの 光る 線・前の 絵・紙ふぶきは さわらない）
import os, sys, math, numpy as np, cv2
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def coords(geo):
    """まっすぐに 直した 板の 絵（WR×HR）の 各点の d（ふちからの きょり・＋＝板の 中）・s（ふちに そった 場所 px）・Lp（ふちの 長さ）"""
    WR, HR, r, cx, cy, hx, hy = geo['WR'], geo['HR'], geo['r'], geo['cxr'], geo['cyr'], geo['hx'], geo['hy']
    yy, xx = np.mgrid[0:HR, 0:WR].astype(np.float32)
    qx = np.abs(xx - cx) - (hx - r); qy = np.abs(yy - cy) - (hy - r)
    d = -(np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r)
    wi, hi = 2 * (hx - r), 2 * (hy - r); arc = np.pi * r / 2; Lp = int(round(2 * (wi + hi) + 4 * arc))
    px, py = xx - cx, yy - cy; ax_, ay_ = qx, qy
    corner = (ax_ > 0) & (ay_ > 0); ang = np.arctan2(np.maximum(ay_, 1e-6), np.maximum(ax_, 1e-6))
    top = (~corner) & (ay_ >= ax_) & (py < 0); bot = (~corner) & (ay_ >= ax_) & (py >= 0); rgt = (~corner) & (ay_ < ax_) & (px >= 0); lft = (~corner) & (ay_ < ax_) & (px < 0)
    sp = np.zeros((HR, WR), np.float32)
    sp[top] = px[top] + (hx - r); sp[rgt] = wi + arc + (py[rgt] + (hy - r)); sp[bot] = wi + arc + hi + arc + ((hx - r) - px[bot]); sp[lft] = 2 * wi + hi + 3 * arc + ((hy - r) - py[lft])
    c_tr = corner & (px >= 0) & (py < 0); c_br = corner & (px >= 0) & (py >= 0); c_bl = corner & (px < 0) & (py >= 0); c_tl = corner & (px < 0) & (py < 0)
    sp[c_tr] = wi + (np.pi / 2 - ang[c_tr]) * r; sp[c_br] = wi + arc + hi + ang[c_br] * r; sp[c_bl] = 2 * wi + hi + 2 * arc + (np.pi / 2 - ang[c_bl]) * r; sp[c_tl] = 2 * wi + 2 * hi + 3 * arc + ang[c_tl] * r
    return d, sp, Lp


def sd_to_xy(geo, s, d):
    """ふちに そった 場所 s・きょり d（配列）→ まっすぐに 直した 板の 絵の x・y"""
    r, cx, cy, hx, hy = geo['r'], geo['cxr'], geo['cyr'], geo['hx'], geo['hy']
    wi, hi = 2 * (hx - r), 2 * (hy - r); arc = np.pi * r / 2
    s = np.asarray(s, np.float64); d = np.asarray(d, np.float64); s, d = np.broadcast_arrays(s, d)
    x = np.zeros(s.shape); y = np.zeros(s.shape); rad = np.maximum(r - d, 0.5)
    b = [0, wi, wi + arc, wi + arc + hi, wi + 2 * arc + hi, 2 * wi + 2 * arc + hi, 2 * wi + 3 * arc + hi, 2 * wi + 3 * arc + 2 * hi, 2 * wi + 4 * arc + 2 * hi]
    seg = np.clip(np.searchsorted(b, s, side='right') - 1, 0, 7); u = s - np.take(b, seg)
    m = seg == 0; x[m] = cx - (hx - r) + u[m]; y[m] = cy - hy + d[m]
    m = seg == 1; t = np.pi / 2 - u[m] / r; x[m] = cx + hx - r + rad[m] * np.cos(t); y[m] = cy - hy + r - rad[m] * np.sin(t)
    m = seg == 2; x[m] = cx + hx - d[m]; y[m] = cy - (hy - r) + u[m]
    m = seg == 3; t = u[m] / r; x[m] = cx + hx - r + rad[m] * np.cos(t); y[m] = cy + hy - r + rad[m] * np.sin(t)
    m = seg == 4; x[m] = cx + (hx - r) - u[m]; y[m] = cy + hy - d[m]
    m = seg == 5; t = np.pi / 2 - u[m] / r; x[m] = cx - hx + r - rad[m] * np.cos(t); y[m] = cy + hy - r + rad[m] * np.sin(t)
    m = seg == 6; x[m] = cx - hx + d[m]; y[m] = cy + (hy - r) - u[m]
    m = seg == 7; t = u[m] / r; x[m] = cx - hx + r - rad[m] * np.cos(t); y[m] = cy - hy + r - rad[m] * np.sin(t)
    return x.astype(np.float32), y.astype(np.float32)


def fix(img, geo, fg=None, band=(-40, 24), dlo=-9, win=451, pwin=301, tol=1.5, lum_t=22.0, skip_top=True, corner_pad=70, dbg=None):
    """img＝板を ぬった 絵（H×W×3）・geo＝bcp_blank.clean の model['geo']・fg＝前の 絵の ある 所（さわらない）。→ 直した 絵（uint8）・直した 所（bool）
       dlo：ぬり直す 段の 外がわの はし（わくの 光る 線の すぐ 内）・skip_top：上の 辺（角の そば corner_pad px は のぞく）は さわらない（かざり・キャラ）"""
    P = np.asarray(img, np.float32); H, W = P.shape[:2]
    Hm, WR, HR = geo['Hm'], geo['WR'], geo['HR']
    R = cv2.warpPerspective(P, Hm, (WR, HR), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    FG = np.zeros((HR, WR), np.uint8) if fg is None else cv2.warpPerspective(fg.astype(np.uint8), Hm, (WR, HR), flags=cv2.INTER_NEAREST)
    d_map, s_map, Lp = coords(geo)
    D0, D1 = band; ds = np.arange(D0, D1 + 1, dtype=np.float64); ss = np.arange(Lp, dtype=np.float64); idx = np.arange(Lp)
    X, Y = sd_to_xy(geo, ss[None, :], ds[:, None])                             # 帯（たて d・よこ s）
    ST = np.stack([cv2.remap(R[..., k], X, Y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) for k in range(3)], -1)
    SF = cv2.remap(FG, X, Y, cv2.INTER_NEAREST, borderValue=0) > 0
    SF = ndimage.binary_dilation(SF, np.ones((3, 9), bool))
    L = lum(ST)
    navy = (ST[..., 2] - ST[..., 0] > 8) & (L < 110)
    # 2. 紺が はじまる 所 b(s)：板の 中（d の 大きい 方）から 外へ 見て、はじめて 紺で ない 所
    order = np.argsort(-ds); nv = navy[order]
    first = np.where((~nv).any(0), (~nv).argmax(0), len(ds) - 1)
    b = ds[order][first] + 0.5
    b[~nv[0]] = np.nan                                                            # いちばん 中が 紺で ない（物・キャラ）
    # 物（紙ふぶき など）・前の 絵が ふちに かかって いる 所 は 直さない
    hsv = cv2.cvtColor(np.clip(ST, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    hh, sv_, vv = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    fr = (ds[:, None] >= -30) & (ds[:, None] <= -4) & (sv_ > 0.3)
    hf = float(np.degrees(np.angle(np.exp(1j * np.radians(hh[fr])).mean()))) % 360 if fr.sum() > 100 else None
    objp = (sv_ > 0.45) & (vv > 0.35) & ((np.abs((hh - hf + 180) % 360 - 180) > 22) if hf is not None else True)
    near = (ds[:, None] >= dlo - 4) & (ds[:, None] <= 20)
    ok = ((objp & near).sum(0) < 6) & ~(SF & near).any(0) & np.isfinite(b)
    ok = ~ndimage.binary_dilation(~ok, np.ones(7, bool))
    if ok.sum() < 200:
        return (P + 0.5).astype(np.uint8), np.zeros((H, W), bool)
    g = ok
    bfi = np.interp(idx, idx[g], b[g], period=Lp)
    b_fit = ndimage.median_filter(bfi, size=win, mode='wrap'); b_fit = ndimage.uniform_filter1d(b_fit, 61, mode='wrap')
    # 3. ふつうの 断面（d ごとに s の 向きの まん中の 値・さかいが ふつうの 所 だけ）
    good = ok & (np.abs(b - b_fit) <= tol + 0.5)
    STg = np.where(good[None, :, None], ST, np.nan)
    pad = pwin // 2; jj = np.arange(0, Lp, 4); PRO = np.zeros_like(ST)
    for k in range(3):
        A = np.concatenate([STg[:, -pad:, k], STg[:, :, k], STg[:, :pad, k]], 1)
        cs = np.full((len(ds), len(jj)), np.nan, np.float32)
        for n_, j in enumerate(jj):
            blk = A[:, j:j + pwin]
            if np.isfinite(blk[0]).sum() >= 9: cs[:, n_] = np.nanmedian(blk, axis=1)
        fin = np.isfinite(cs[0])
        PRO[..., k] = np.array([np.interp(idx, jj[fin], cs[t, fin], period=Lp) for t in range(len(ds))])
    # ぬり直す 列：さかいが ずれて いる（出っぱり・へこみ）／段の 明るさが ふつうと ちがう
    seg = (ds[:, None] >= dlo) & (ds[:, None] <= b_fit[None, :] - 0.5)
    dl = np.abs(np.where(seg, L - lum(PRO), 0)).sum(0) / np.maximum(seg.sum(0), 1)
    badc = ok & ((np.abs(b - b_fit) > tol) | (dl > lum_t))
    if skip_top:
        wi = 2 * (geo['hx'] - geo['r'])
        badc &= ~((ss > corner_pad) & (ss < wi - corner_pad))
    if badc.any():
        badc = ndimage.binary_closing(badc, np.ones(9, bool)) & ok
        badc = ndimage.binary_dilation(badc, np.ones(5, bool)) & ok
    wd = np.zeros((len(ds), Lp), np.float32)
    for j in np.nonzero(badc)[0]:
        top_ = max(b[j], b_fit[j]) + 3
        wd[:, j] = np.clip(np.minimum(ds - (dlo - 2), top_ + 2 - ds) / 2.0, 0, 1)
    wd = ndimage.uniform_filter1d(wd, 5, axis=1, mode='wrap')
    NEWb = ST * (1 - wd[..., None]) + PRO * wd[..., None]
    delta_strip = (NEWb - ST) * (~SF)[..., None]
    # 帯 → まっすぐな 板の 絵（s・d の 地図で 引く）
    inband = (d_map >= D0) & (d_map <= D1)
    mx = s_map.astype(np.float32); my = (d_map - D0).astype(np.float32)
    dR = np.stack([cv2.remap(delta_strip[..., k].astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT) for k in range(3)], -1) * inband[..., None]
    wR = cv2.remap(wd.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT) * inband
    dI = cv2.warpPerspective(dR, Hm, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT)
    wI = cv2.warpPerspective(wR, Hm, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT)
    out = np.clip(P + dI, 0, 255)
    if fg is not None: out[fg] = P[fg]
    if dbg is not None: dbg.update(b=b, b_fit=b_fit, badc=badc, ok=ok, ST=ST, NEW=NEWb, ds=ds)
    return (out + 0.5).astype(np.uint8), wI > 0.02


# 花束①・④：板の 右上の すみに、四角く ぬりつぶした 紺の かたまり
#   まさちゃん 2026/11/24 11:39 の 赤丸（花束の 板の 右上）→ はじめは 四角を 板の 色で ぬり直し、上の 花の 切れた 花びらを、花の 形（花びら 5まい）を まわして 足した（下の TABS・fix_tab）
#   まさちゃん 13:24「花束ボードの元のデータある？」→ まさちゃんの もとの 絵（1048×1501）を さがしたら あった。四角は もとの 絵には 無く、
#   11/03 に 紙ふぶきを 消す とき（cfg の clean.regions の conf_rm）に 四角く ぬって しまった あと だった
#   → いまは ORIG・paste_orig（もとの 絵から その 所だけ くりぬいて かぶせる：まさちゃん 12:47「元のデータからここだけくり抜いて上から被せちゃえば？」）。TABS は 使わない（記録）
ORIG = {'bouquet1': dict(win=(860, 640, 1060, 860)), 'bouquet4': dict(win=(860, 640, 1060, 860))}
BCPIC = os.environ.get('BCPIC', '/home/claude/work/bcpic')                    # まさちゃんの 絵の 作業フォルダ（<デザイン>/src.png：リポジトリに 入れない）


def orig_canvas(name, cfg):
    """まさちゃんの もとの 絵（<BCPIC>/<デザイン>/src.png）を bcp_bg.py と 同じ 置き方で 1170×2532（RGB・float）に"""
    p = os.path.join(BCPIC, name, cfg.get('src', 'src.png'))
    assert os.path.exists(p), f'もとの 絵が ない：{p}（まさちゃんの 絵を この 名前で 置く）'
    pic = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32)
    Q = np.array(cfg['quad'], np.float64); fx0, fx1 = cfg['frame_lr']; K = 3
    S = cfg.get('S') or (380.0 / (fx1 - fx0))
    OX = 195 - S * cfg.get('cx', (fx0 + fx1) / 2); OY = cfg['top_pt'] - S * (Q[0, 1] + Q[1, 1]) / 2
    M = np.array([[S * K, 0, OX * K], [0, S * K, OY * K]], np.float32)
    return cv2.warpAffine(pic, M, (390 * K, 844 * K), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))


def paste_orig(bg, fg, cfg, name, thr=20.0, dbg=None):
    """bg＝板を ぬった 絵（H×W×3 RGB）・fg＝前の 絵（RGBA・なければ None）・cfg＝デザインの 設定（designs/<デザイン>.json）
       → (直した bg, 直した fg（または None）, 直した 所)
       ORIG の win の 中で、いまの 絵（bg と 前の 絵を 重ねた もの）と もとの 絵が ちがう 所（四角・その ふちの 線）を、もとの 絵で かぶせる。
       板の 紺は ぬり直した 板と 少し 色が ちがう ので、まわりの 紺の ちがいを なめらかに のばして 合わせる（花・星は そのまま）。
       かぶせた 所の 前の 絵は すき通しに して、その 分は bg に 焼きこむ（見た目は かわらない）"""
    t = ORIG.get(name)
    B0 = np.asarray(bg, np.float32); H, W = B0.shape[:2]
    if not t:
        return (B0 + 0.5).astype(np.uint8), fg, np.zeros((H, W), bool)
    F = None if fg is None else np.asarray(fg, np.float32).copy()
    O = orig_canvas(name, cfg)
    alF = np.zeros((H, W), np.float32) if F is None else F[..., 3] / 255.0
    C = B0 * (1 - alF[..., None]) + (0 if F is None else F[..., :3]) * alF[..., None]
    x0, y0, x1, y1 = t['win']
    win = np.zeros((H, W), bool); win[y0:y1, x0:x1] = True
    D = np.abs(C - O).max(-1)
    m = (D > thr) & win
    m = ndimage.binary_opening(m, np.ones((3, 3), bool))
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, np.ones((7, 7), bool)))
    m = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ww = np.clip(np.minimum(yy - y0, y1 - 1 - yy) / 12.0, 0, 1) * np.clip(np.minimum(xx - x0, x1 - 1 - xx) / 12.0, 0, 1)
    z = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0) * ww, 0, 1)
    # 板の 紺：まわりで 両方 紺の 所の ちがい（いま − もと）を なめらかに 中へ のばす
    navy = lambda a: (a @ np.array([0.299, 0.587, 0.114], np.float32) < 60) & (a[..., 2] > a[..., 0] + 15)
    nO = navy(O)
    big = np.zeros((H, W), bool); big[max(0, y0 - 30):y1 + 30, max(0, x0 - 30):x1 + 30] = True
    ring = nO & navy(C) & big & ~(cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))) > 0)
    den = cv2.GaussianBlur(ring.astype(np.float32), (0, 0), 18.0)
    Dcs = cv2.GaussianBlur((C - O) * ring[..., None], (0, 0), 18.0) / np.maximum(den, 1e-4)[..., None] * (den > 0.01)[..., None]
    dn = cv2.GaussianBlur(nO.astype(np.float32), (0, 0), 6.0)
    Nref = cv2.GaussianBlur(O * nO[..., None], (0, 0), 6.0) / np.maximum(dn, 1e-4)[..., None]
    aobj = np.where(dn > 0.05, np.clip((np.abs(O - Nref).max(-1) - 12.0) / 30.0, 0, 1), 1.0)       # 花・星（紺から はなれた 色）は 1
    T = O + Dcs * (1 - aobj)[..., None]
    R = cv2.dilate((z > 0.004).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) > 0
    Bn = np.where(R[..., None], C, B0)
    Bn = Bn * (1 - z[..., None]) + T * z[..., None]
    if F is not None:
        F[..., 3] = np.where(R, 0, F[..., 3])
    if dbg is not None:
        dbg.update(m=m, z=z, ring=ring, aobj=aobj, Dcs=Dcs, O=O, C=C)
    return (np.clip(Bn, 0, 255) + 0.5).astype(np.uint8), (None if F is None else (np.clip(F, 0, 255) + 0.5).astype(np.uint8)), z > 0.02


TABS = {'bouquet1': dict(box=(900, 700, 1000, 795), star=(926, 766),
                         petals=[dict(c=(955, 681), R=66, kind='blossom', fill=[(18, 90, -72), (90, 165, 72)])],          # 大きな 桜：下の 2まいを となりの 花びらから
                         # まさちゃん 13:09 の 赤線：左下の 花びらの 下の ふちを この 線に（線より 下の とがった 先＝× は けす）
                         edits=[dict(kind='arc', flower='blossom', pts=[(910, 737), (918, 739), (925, 740), (932, 740), (937, 739), (941, 737), (945, 733), (949, 728), (951, 724), (953, 720), (955, 716)])]),
        'bouquet4': dict(box=(900, 700, 1000, 795),
                         # まさちゃん 12:55・13:09 の 赤線：ひまわりの 下 まん中に U の 形の 花びらの 先・その 左下と 右（×）の 切れはしは けす
                         edits=[dict(kind='U', flower='sun', pts=[(920, 704), (920, 712), (921, 718), (923, 724), (926, 729), (929, 732.5), (932, 733.5), (935, 731), (937, 726), (938, 720), (939, 713), (941, 704)],
                                     rm=[[(939, 709), (947, 712), (956, 715), (967, 716), (968, 724), (962, 732), (938, 732)], [(916, 721), (921, 719), (924, 727), (929, 734), (927, 741), (916, 741)]]),
                                # 右の 桜の 左の 花びら：まさちゃんの 赤線の 形（先に 切れこみ）に、同じ 桜の 花びらを まわして 大きさを 合わせて 入れる
                                dict(kind='petal', c=(1011.3, 765.5), src=108, flower='blossom',
                                     poly=[(1002, 759), (995, 754), (988, 751.5), (980, 750.5), (972, 751), (965, 753), (959, 756), (957, 758), (960, 760.5), (963, 762), (960, 764.5), (957, 767),
                                           (956, 770), (958, 773), (962, 776.5), (968, 779), (976, 780.5), (985, 780.5), (993, 778.5), (1000, 775), (1004, 770), (1005, 764)])])}


def tab_mask(S, box, tol=4):
    """box の 中の、まったく 同じ 色で ぬった 四角（いちばん 多い 色 ±tol）"""
    x0, y0, x1, y1 = box; sub = S[y0:y1, x0:x1].astype(np.int32)
    keys, cnt = np.unique(sub.reshape(-1, 3), axis=0, return_counts=True); c0 = keys[cnt.argmax()]
    m = (np.abs(sub - c0).max(2) <= tol)
    lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); m = lab == (sz.argmax() + 1)
    out = np.zeros(S.shape[:2], bool); out[y0:y1, x0:x1] = ndimage.binary_fill_holes(m)
    return out


def fix_tab(bg, fg, S, board, name, dbg=None):
    """bg＝板を ぬった 絵（H×W×3）・fg＝前の 絵（H×W×4・RGBA・なければ None）・S＝もとの 絵・board＝板の 色（bcp_blank.clean の model['board']）
       → (直した bg（uint8）, 直した fg（uint8 RGBA または None）, 直した 所)
       1. 四角と その ふちの 線（前の ぬりの あと）を 板の 色に（前の 絵の 下と 明るい 星は のこす）
       2. 上の 花の 切れた 花びら：前の 絵の 切れ目の 暗い 線を 消し、花びら 5まいの 形を まわして 下に 足す（bg）
       3. 右の わくの 光の たての 切れ目（前の 絵）を なめらかに うすく  4. 四角に 切られた 星：のこった 左を 右へ うつす"""
    t = TABS.get(name)
    B0 = np.asarray(bg, np.float32); H, W = B0.shape[:2]
    if not t:
        return (B0 + 0.5).astype(np.uint8), fg, np.zeros((H, W), bool)
    F = None if fg is None else np.asarray(fg, np.float32).copy()
    al = np.zeros((H, W), np.float32) if F is None else F[..., 3] / 255.0
    Q = tab_mask(S, t['box']); qy, qx = np.nonzero(Q); qx0, qx1, qy0, qy1 = qx.min(), qx.max(), qy.min(), qy.max()
    x0b, y0b, x1b, y1b = t['box']; inb = np.zeros((H, W), bool); inb[y0b - 6:y1b + 6, x0b - 6:x1b + 6] = True
    R_ = (cv2.dilate(Q.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23))) > 0) & inb
    vB = B0.max(2) / 255.0
    Cm = B0 * (1 - al[..., None]) + (0 if F is None else F[..., :3]) * al[..., None]          # アプリで 見える 絵
    Lm = lum(Cm); k3 = np.ones((3, 3), np.uint8)
    ring = R_ & (Lm < 125) & (cv2.dilate(Q.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) > 0)    # 四角の ふちの 暗い 線（bg・fg）
    for _ in range(2):                                                             # その となりの うすく 暗い ふち（にじみ）
        ring |= (cv2.dilate((ring | Q).astype(np.uint8), k3) > 0) & (Lm < 175) & R_
    topb = np.zeros((H, W), bool); topb[qy0 - 6:qy0 + 2, qx0 - 4:qx1 + 5] = True
    for _ in range(2):                                                             # 上の 花びらの 切れ目の 1〜2行（少し 暗い）
        ring |= (cv2.dilate((ring | Q).astype(np.uint8), k3) > 0) & (Lm < 215) & topb & R_
    if F is not None:                                                              # 2. 前の 絵の 切れ目の 暗い 線 → すき通し
        F[..., 3] = np.where(ring | Q, 0, F[..., 3]); al = F[..., 3] / 255.0
        # 3. 右の わくの 光の たての 切れ目 → 16px で うすく
        ys_, xs_ = np.mgrid[0:H, 0:W]
        zone = (ys_ >= qy0) & (ys_ <= qy1) & (xs_ >= qx1 - 2) & (xs_ <= qx1 + 16) & inb
        ramp = np.clip((xs_ - (qx1 - 2)) / 18.0, 0, 1)
        F[..., 3] = np.where(zone, F[..., 3] * ramp, F[..., 3])
    fill = R_ & (al < 0.8) & ((vB < 0.5) | Q | ring)
    if t.get('star'):                                                              # 四角に 切られた 星は いったん 消す（あとで 同じ 絵の 星を のせる）
        sx0, sy0 = t['star']; yy0, xx0 = np.mgrid[0:H, 0:W]; sdisk = ((xx0 - sx0) ** 2 + (yy0 - sy0) ** 2 < 26 ** 2)
        if F is not None: F[..., 3] = np.where(sdisk, 0, F[..., 3]); al = F[..., 3] / 255.0      # 前の 絵に のこった 星の 半分も
        fill |= sdisk
    out = B0.copy(); out[fill] = board[fill]                                        # 1. 板の 色
    hsv = cv2.cvtColor(np.clip(S, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    hh, sv_, vv = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    yy, xx = np.mgrid[0:H, 0:W]
    # 2. 花びら：同じ 花の 切れて いない 花びらを、花の まん中で まわして、四角で 切れた 所・紺の 所に 足す（まさちゃん 12:47「元のデータからくり抜いて上から被せちゃえば？」・12:55 の 赤線）
    Cm2 = out * (1 - al[..., None]) + (0 if F is None else F[..., :3]) * al[..., None]
    vO = Cm2.max(2) / 255.0; navyO = (Cm2[..., 2] > Cm2[..., 0] + 6) & (vO < 0.45)
    bad = cv2.dilate((Q | ring).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0            # 花びらの もとに しない 所
    for pd in t.get('petals', []):
        cx, cy = pd['c']; Rr = pd['R']
        near = (xx - cx) ** 2 + (yy - cy) ** 2 < 26 ** 2
        if pd['kind'] == 'blossom':
            cen = near & (hh > 25) & (hh < 62) & (sv_ > 0.45) & (vv > 0.55)
            pm = (vv > 0.55) & ~((hh > 70) & (hh < 170)) & ~((hh > 180) & (hh < 290))
        else:
            cen = near & (hh > 10) & (hh < 40) & (sv_ > 0.5) & (vv > 0.2) & (vv < 0.6)
            pm = (hh >= 22) & (hh <= 64) & (sv_ > 0.42) & (vv > 0.5)
        if cen.sum() > 30 and not pd.get('fixc'): cy, cx = [float(v) for v in ndimage.center_of_mass(cen)]
        th_ = np.degrees(np.arctan2(yy - cy, xx - cx)); rr_ = np.hypot(xx - cx, yy - cy)
        pmk = pm & ~bad & (rr_ < Rr + 4)
        lab_p, _n = ndimage.label(pmk); idc = lab_p[int(round(cy)), int(round(cx))]           # 花の まん中と つながる 所 だけ（ほかの 花の 白い 所は 使わない）
        if idc == 0:
            cc = np.bincount(lab_p[(rr_ < 30) & pmk].ravel()); cc[0] = 0; idc = int(cc.argmax()) if cc.size > 1 else 0
        if idc: pmk = lab_p == idc
        pmf = pmk.astype(np.float32)
        canvas = (fill | navyO) & (rr_ < Rr) & ~(al > 0.5)
        if 'fill' in pd:
            jobs = [(lo, hi, a_) for lo, hi, a_ in pd['fill']]
        else:
            d_, s0, hw = pd['single']
            prof = [(float(rr_[pmf > 0.5][np.abs(((th_[pmf > 0.5] - a0 + 180) % 360) - 180) < 2].max()) if (np.abs(((th_[pmf > 0.5] - a0 + 180) % 360) - 180) < 2).any() else 0, a0) for a0 in np.arange(s0 - 15, s0 + 15.1, 1.0)]
            s_best = max(prof)[1]
            jobs = [(d_ - hw, d_ + hw, s_best - d_)]
        for lo, hi, a_ in jobs:
            M_ = cv2.getRotationMatrix2D((cx, cy), float(a_), 1.0)
            rI = cv2.warpAffine(Cm.astype(np.float32), M_, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            rM = cv2.warpAffine(pmf, M_, (W, H), flags=cv2.INTER_LINEAR)
            dth = ((th_ - (lo + hi) / 2 + 180) % 360) - 180; half = (hi - lo) / 2
            sec = np.clip((half - np.abs(dth)) / 3.0, 0, 1)
            a2 = cv2.GaussianBlur(rM, (0, 0), 0.7) * sec * cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), 0.8)
            core_ = a2 > 0.3; labn, nn_ = ndimage.label(core_)                          # 今の 花びらと つながらない かけら（白い 点 など）は 足さない
            if nn_:
                exist = pm & (rr_ < Rr + 4) & ~Q & (al > 0.3) | pmk                     # 今 見えて いる 花びら（前の 絵）
                touch = np.unique(labn[(cv2.dilate(exist.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0) & core_]); touch = touch[touch > 0]
                keepc = cv2.dilate(np.isin(labn, touch).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
                a2 = a2 * keepc
            out = out * (1 - a2[..., None]) + rI * a2[..., None]
            fill |= a2 > 0.02
        if dbg is not None: dbg.setdefault('petal', []).append((round(cx, 1), round(cy, 1), jobs))
    # 3. まさちゃんの 赤線（edits）：花びらの ふちを 線に 合わせる・切れた かどを けす・花びらを 形に 入れる
    def petalish(kind, img):
        hsv2 = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32); h2, s2, v2 = hsv2[..., 0] * 2, hsv2[..., 1] / 255, hsv2[..., 2] / 255
        if kind == 'sun': return (h2 >= 18) & (h2 <= 64) & (s2 > 0.42) & (v2 > 0.5)
        return (v2 > 0.6) & ~((h2 > 70) & (h2 < 170)) & ~((h2 > 180) & (h2 < 290))
    def poly_mask(pts, ss=4):
        m = np.zeros((H * 1, W * 1), np.uint8)
        big = np.zeros((int(H), int(W)), np.float32)
        x0e, y0e = int(min(p[0] for p in pts)) - 4, int(min(p[1] for p in pts)) - 4; x1e, y1e = int(max(p[0] for p in pts)) + 5, int(max(p[1] for p in pts)) + 5
        sub = np.zeros(((y1e - y0e) * ss, (x1e - x0e) * ss), np.uint8)
        cv2.fillPoly(sub, [np.round((np.array(pts) - [x0e, y0e]) * ss).astype(np.int32)], 1)
        big[y0e:y1e, x0e:x1e] = cv2.resize(sub.astype(np.float32), (x1e - x0e, y1e - y0e), interpolation=cv2.INTER_AREA)
        return big
    def col_fill(add, kind, img, up=30):
        """add の 中を、同じ 列の すぐ 上の 花びらの 色で うめる（下の ふちは 少し こく）"""
        res = img.copy(); pm2 = petalish(kind, img) & ~(add > 0.02)
        ys2, xs2 = np.nonzero(add > 0.02)
        for x_ in np.unique(xs2):
            col = ys2[xs2 == x_]; top = col.min()
            cand = [y_ for y_ in range(top - 1, max(0, top - up), -1) if pm2[y_, x_]]
            if not cand: continue
            src_ = np.median(img[cand[:5], x_], axis=0)
            for y_ in col: res[y_, x_] = src_
        return res
    for ed in t.get('edits', []):
        Cn0 = out * (1 - al[..., None]) + (0 if F is None else F[..., :3]) * al[..., None]
        if ed['kind'] in ('arc', 'U'):
            pts = ed['pts']
            if ed['kind'] == 'arc':                                                 # 線より 下（花の 外）＝ けす
                below = pts + [(pts[-1][0] + 2, pts[-1][1] + 45), (pts[0][0], pts[0][1] + 45)]
                rm_ = poly_mask(below); ad_ = np.zeros_like(rm_)
            else:                                                                   # U の 中 ＝ 花びらで うめる・× の 所 ＝ けす
                ad_ = poly_mask(pts); rm_ = np.zeros_like(ad_)
                for rp in ed['rm']: rm_ = np.maximum(rm_, poly_mask(rp))
                rm_ = np.clip(rm_ - ad_, 0, 1)
            fl_ = petalish(ed['flower'], Cn0) | (np.abs(Cn0 - board).max(2) > 28)        # 花びら と その ふちの 暗い 線（板の 色で ない 所）
            rm_ = rm_ * fl_ * (rm_ > 0.02)
            ad_ = ad_ * (~petalish(ed['flower'], Cn0))
            filled = col_fill(ad_, ed['flower'], Cn0)
            newc = Cn0 * (1 - ad_[..., None]) + filled * ad_[..., None]
            newc = newc * (1 - rm_[..., None]) + board * rm_[..., None]
            chg = (ad_ > 0.02) | (rm_ > 0.02)
        else:                                                                       # 花びらを 形（poly）に：同じ 花の 花びらを まわして のばして 入れる
            cx2, cy2 = ed['c']; P2 = np.array(ed['poly'], np.float64)
            dd2 = np.hypot(P2[:, 0] - cx2, P2[:, 1] - cy2); tip = P2[dd2.argmax()]; dst_a = np.degrees(np.arctan2(tip[1] - cy2, tip[0] - cx2)); dst_l = dd2.max()
            th2 = np.degrees(np.arctan2(yy - cy2, xx - cx2)); rr2 = np.hypot(xx - cx2, yy - cy2)
            pmS = petalish(ed['flower'], Cm) & ~(cv2.dilate((Q | ring).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & (rr2 < 80)
            lab2, _n2 = ndimage.label(pmS); i2 = lab2[int(round(cy2)), int(round(cx2))]
            if i2: pmS = lab2 == i2
            sel = pmS & (np.abs(((th2 - ed['src'] + 180) % 360) - 180) < 4)
            src_l = float(rr2[sel].max()) if sel.any() else dst_l
            M2 = cv2.getRotationMatrix2D((cx2, cy2), float(ed['src'] - dst_a), float(dst_l / max(src_l, 1)))
            Wi = cv2.warpAffine(Cm.astype(np.float32), M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            Wm = cv2.warpAffine(pmS.astype(np.float32), M2, (W, H), flags=cv2.INTER_LINEAR)
            pg2 = poly_mask(ed['poly'])
            hole = (pg2 > 0.02) & (Wm < 0.5)
            if hole.any():
                Wu8 = np.clip(Wi, 0, 255).astype(np.uint8); Wi = cv2.inpaint(Wu8, (hole & ~(pg2 < 0.02)).astype(np.uint8), 4, cv2.INPAINT_TELEA).astype(np.float32) * hole[..., None] + Wi * (~hole)[..., None]
            newc = Cn0 * (1 - pg2[..., None]) + Wi * pg2[..., None]
            chg = pg2 > 0.02
            if dbg is not None: dbg.setdefault('poly', []).append((round(dst_a, 1), round(dst_l, 1), round(src_l, 1)))
        out = np.where(chg[..., None], newc, out)
        if F is not None: F[..., 3] = np.where(chg, 0, F[..., 3]); al = F[..., 3] / 255.0
        fill |= chg
    if t.get('star'):                                                              # 4. 星：消した 星の 所に 小さな 4本の 光の 星を 描く（まわりの 星と 同じ 白〜金）
        sx, sy = t['star']; k = 26
        yy1, xx1 = np.mgrid[-k:k + 1, -k:k + 1].astype(np.float32)
        rays = np.exp(-(xx1 / 1.5) ** 2) * np.exp(-np.abs(yy1) / 8.0) + np.exp(-(yy1 / 1.5) ** 2) * np.exp(-np.abs(xx1) / 8.0)
        rr2 = xx1 ** 2 + yy1 ** 2; core = np.exp(-rr2 / (2 * 2.4 ** 2)); glow = np.exp(-rr2 / (2 * 7.5 ** 2))
        add = (core * 1.0 + rays * 0.85)[..., None] * np.array([255, 250, 232], np.float32) + glow[..., None] * np.array([170, 125, 40], np.float32) * 0.75
        add *= np.clip((k - np.sqrt(rr2)) / 6.0, 0, 1)[..., None]
        sl2 = (slice(sy - k, sy + k + 1), slice(sx - k, sx + k + 1))
        out[sl2] = 255 - (255 - out[sl2]) * (1 - np.clip(add / 255.0, 0, 1))                   # スクリーン 合成
    # 重ねた 絵で しあげる：四角の まわり（R_）は、前の 絵（花・光）を bg に 焼きこみ、ふちの 細い 線を まん中の 値で 消す。fg は R_ で すき通し
    alF = np.zeros((H, W), np.float32) if F is None else F[..., 3] / 255.0
    Cn = out * (1 - alF[..., None]) + (0 if F is None else F[..., :3]) * alF[..., None]
    edge = (cv2.dilate(Q.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))) > 0) & ~(cv2.erode(Q.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & R_
    med = cv2.medianBlur(np.clip(Cn, 0, 255).astype(np.uint8), 5).astype(np.float32)
    Cn = np.where(edge[..., None], med, Cn)
    a = np.clip(cv2.GaussianBlur((R_ | fill).astype(np.float32), (0, 0), 1.2) * 1.3, 0, 1)
    Bn = B0 * (1 - a[..., None]) + Cn * a[..., None]
    if F is not None:
        F[..., 3] = F[..., 3] * (1 - a)
    return (np.clip(Bn, 0, 255) + 0.5).astype(np.uint8), (None if F is None else (np.clip(F, 0, 255) + 0.5).astype(np.uint8)), a > 0.02
