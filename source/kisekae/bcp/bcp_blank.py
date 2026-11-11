# 結果ボードカスタム（絵の ボード）：アプリに 入る 絵（bcp_<デザイン>.webp）の「ボードの 中」を、何も 書いて いない きれいな 板に ぬり直す
#   （第4.153版・まさちゃん 2026/11/11 15:39「他の結果ボードカスタムのボードも、綺麗に何も書いていないようにして！
#     的中スタンプボードの結果ボードカスタムだけは、絵と繋がっている的中スタンプは消さなくていいよ！」）
#   前の やり方（bcp_clean.py：もとの 絵から 字・行・飾りを 消す）では、パネルの さかい（見出しの 所と 行の 所の 段）・ふちの へこみ・消した 字の うすい あと・すじ・板の 中の 細い 線が のこって いた。
#   もとの 作業フォルダは もう ない ので、**できあがった 絵（bcp_<デザイン>.webp）から** 作る。前の 絵は 消さない・上書きしない（新しい 名前 bcp_<デザイン>_bl.webp で 足す）
#
#   python3 kisekae/bcp/bcp_blank.py <絵の フォルダ（ios/bcp_assets）> <出す フォルダ> [デザイン…]     … bcp_<デザイン>_bl.webp（1170×2532・WebP quality 90）。デザインを 書かなければ 出世馬 以外の 52こ
#   DBG=<フォルダ> を つけると 見くらべの 絵（もと｜できた／消す 所の ふち｜ちがい）も 出す
#
#   作り方：
#     1. 板の 色の なめらかな 面（x・y の 2次式）を、板の まん中の 紺の 点に 当てはめる（はずれた 点は はぶく）
#     2. 物（わく・キャラ・紙ふぶき・ハンコ）＝明るい／面の 色から 遠い 点。板の 内がわ（ふちから はなれた 所）では あたたかい 色も 物
#        （ふちの 近くの あたたかい 色は わくの 光の にじみ＝板の 一部）。物の まわり 6px と 前の 絵（_fg.webp）は まもる（ふち取り・にじみ）
#        小さな 点（380px より 小さい かけら）は 物に しない＝消す
#     3. ぬり直す 所＝板の まん中から つながる、物で ない 所（うすい あと・パネルの 段・すじ・クモの巣・ひび も 入る）
#     4. 色＝1 の 面。ふちの 帯（40px）だけは、板を まっすぐな 四角に 直して（射影）角の まるい 四角の ふちに そって「面からの ずれ」の まん中の 値を とる
#        → へこみ・パネルの さかい・角の すき間は 消えて、ふちの 暗い すき間と わくの 光の にじみは 同じ はばで のこる。わくの きらきらは そのまま 上に のこる
#   デザインごとの きまり（CFGS）：スタンプ＝鎖は 消す・絵と つながる 的中の ハンコ（と しぶき）は のこす／馬が運ぶ＝板の 中の 細い 金の 線と 飾りは 消す／花束＝板の まん中に うかぶ 小さな 花びらは 消す
import sys, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import bcp_app
cv2.setNumThreads(1)
SUF = '_bl'                                           # できた 絵の 名前の しっぽ（bcp_app.pics と 同じ）

# デザインごとの きまり（名前の はじめで えらぶ）。四角は 板の 中の 割合（u0, v0, u1, v1）
#   force：かならず 消す 四角／keep：この 四角の 中の 物は 小さくても 消さない／thin：この 半径より 細い 線と 飾りは 消す／speck：これより 小さい 物は 消す（px）
CFGS = {
    'stamp': dict(force=[(0.0, 0.378, 1.0, 0.44)], keep=[(0.0, 0.0, 0.42, 0.376)]),      # スタンプ：鎖は 消す・絵と つながる 的中の ハンコは のこす
    'carry': dict(thin=7),                                                             # 馬が運ぶ：板の 中の 細い 金の 線と 飾りは 消す
    'bouquet': dict(speck=900),                                                        # 花束：板の まん中に うかぶ 小さな 花びらは 消す
}


def cfg_of(name):
    for k, v in CFGS.items():
        if name.startswith(k): return v
    return {}


def names():
    """ぬり直す デザイン（出世馬＝3D の 絵は shusse3d.py が 板を ぬる）"""
    return [n for iid, _k, st in bcp_app.ITEMS if iid != 'climb' for _d, n in st]


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)


def fit_surface(P, good, roi):
    """板の 色の なめらかな 面（x・y の 2次式）：はずれた 点を はぶいて 3回 当てはめる"""
    ys, xs = np.nonzero(good); sel = np.random.RandomState(1).choice(len(ys), min(len(ys), 150000), replace=False); ys, xs = ys[sel], xs[sel]
    yi, xi = np.nonzero(roi); cx, cy, sx, sy = xi.mean(), yi.mean(), max(1.0, np.ptp(xi) / 2), max(1.0, np.ptp(yi) / 2)
    def basis(x, y):
        u, v = (x - cx) / sx, (y - cy) / sy; return np.stack([np.ones_like(u), u, v, u * u, v * v, u * v], 1)
    Bm = basis(xs.astype(np.float64), ys.astype(np.float64)); col = P[ys, xs].astype(np.float64); keep = np.ones(len(ys), bool)
    for _ in range(3):
        coef = np.linalg.lstsq(Bm[keep], col[keep], rcond=None)[0]; res = np.abs(Bm @ coef - col).max(1); keep = res < max(5.0, np.percentile(res, 80))
    S = np.zeros(P.shape, np.float32); S[yi, xi] = (basis(xi.astype(np.float64), yi.astype(np.float64)) @ coef).astype(np.float32)
    return np.clip(S, 0, 255)


def clean(src, name, cfg=None, dbg=None):
    """src＝絵の フォルダ。→ ぬり直した 絵（uint8）・ぬり直した 所（bool）"""
    cfg = cfg or {}
    P = np.asarray(Image.open(os.path.join(src, f'bcp_{name}.webp')).convert('RGB')).astype(np.float32); H, W = P.shape[:2]
    q = np.array(bcp_app.design(name)['q'], np.float64) * 3
    quad = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(quad, np.round(q).astype(np.int32), 1)
    roi = cv2.dilate(quad, disk(34)) > 0; core = cv2.erode(quad, disk(46)) > 0
    fgf = os.path.join(src, f'bcp_{name}_fg.webp'); fg = (np.asarray(Image.open(fgf).convert('RGBA'))[..., 3] > 8) if bcp_app.cfg(name).get('fg') and os.path.exists(fgf) else np.zeros((H, W), bool)
    R_, G_, B_ = P[..., 0], P[..., 1], P[..., 2]; mx = P.max(2)
    navy = roi & (B_ > R_ + 10) & (B_ >= G_ + 2) & (mx < 150)                                         # 紺（板の 色・うすい あと・明るい すじ）
    dark = roi & (mx < 46)                                                                           # 黒い かげ・へこみ
    S = fit_surface(P, navy & core & ~fg, roi)
    # 物（わく・キャラ・紙ふぶき・ハンコ）：明るい／面の 色から 遠い。板の 内がわ（ふちから はなれた 所）では あたたかい 色も 物（ふちの 近くの あたたかい 色は わくの 光の にじみ＝板の 一部）
    dmax = np.abs(P - S).max(2); inner = cv2.erode(quad, disk(30)) > 0
    strong = roi & ~(navy | dark) & ((mx > 135) | (dmax > 100) | (inner & (R_ > B_ + 15)))
    def box(b):                                                   # 板の 中の 割合の 四角 → 絵の 形
        u0, v0, u1, v1 = b; m_ = np.zeros((H, W), np.uint8); f = lambda u, v: (q[0] * (1 - u) + q[1] * u) * (1 - v) + (q[3] * (1 - u) + q[2] * u) * v
        cv2.fillConvexPoly(m_, np.round(np.array([f(u0, v0), f(u1, v0), f(u1, v1), f(u0, v1)])).astype(np.int32), 1); return m_ > 0
    keepm = np.zeros((H, W), bool)
    for b in cfg.get('keep', []): keepm |= box(b)                    # この 四角の 中の 物（ハンコと その しぶき）は 小さくても 消さない
    if cfg.get('thin'):                                           # 細い 線と 小さな 飾り（板の 中の 金の 線）は 物に しない＝消す
        tin = cv2.erode(quad, disk(10)) > 0; si_ = strong & tin; strong = (strong & ~tin) | (cv2.morphologyEx(si_.astype(np.uint8), cv2.MORPH_OPEN, disk(cfg['thin'])) > 0)
    sl, sn = ndimage.label(strong); ssz = np.bincount(sl.ravel(), minlength=sn + 1); strong &= ~(np.isin(sl, [i for i in range(1, sn + 1) if ssz[i] < cfg.get('speck', 380)]) & ~keepm)      # 小さな 点（あとの かけら）は 消す
    for b in cfg.get('force', []): strong &= ~box(b)                 # かならず 消す 四角（鎖 など）
    guard = (cv2.dilate((strong & inner).astype(np.uint8), disk(6)) > 0) | (cv2.dilate(strong.astype(np.uint8), disk(1)) > 0) | (cv2.dilate(fg.astype(np.uint8), disk(3)) > 0)
    free = roi & ~guard & (cv2.dilate(quad, disk(12)) > 0)
    lab, n = ndimage.label(free); ids = np.unique(lab[core & free]); ids = ids[ids > 0]; cnt = np.bincount(lab.ravel(), minlength=n + 1); M = np.isin(lab, [i for i in ids if cnt[i] > 3000])
    M = cv2.morphologyEx(cv2.morphologyEx(M.astype(np.uint8), cv2.MORPH_CLOSE, disk(8)), cv2.MORPH_OPEN, disk(5)) > 0; M &= ~guard            # ふちを なめらかに
    M |= ndimage.binary_fill_holes(M) & ~guard & roi                                                        # 物で ない 小さな 穴は うめる
    # ── ふちの 帯：板を まっすぐな 四角に 直して（射影）、角の まるい 四角の ふちに そって「面からの ずれ」の まん中の 値を とる
    #    （へこみ・パネルの さかい・あとが 消えて、ふちの 暗い すき間と 光の にじみは 同じ はばで のこる。わくの きらきらは そのまま 上に のこる）
    D = 40; PADc = 40; Wc = int(round((np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2)); Hc = int(round((np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2))
    dstq = np.float32([[PADc, PADc], [PADc + Wc, PADc], [PADc + Wc, PADc + Hc], [PADc, PADc + Hc]]); Hm = cv2.getPerspectiveTransform(q.astype(np.float32), dstq); WR, HR = Wc + 2 * PADc, Hc + 2 * PADc
    devR = cv2.warpPerspective(P - S, Hm, (WR, HR), flags=cv2.INTER_LINEAR); MR = cv2.warpPerspective(M.astype(np.uint8), Hm, (WR, HR), flags=cv2.INTER_NEAREST) > 0
    def side(vals, default):                                       # その 辺の ふちの 場所（まん中の 値）。物に かくれて いる 列が 多ければ 四すみの 四角の 辺
        vals = vals[np.isfinite(vals)]; return float(np.median(vals)) if len(vals) > 30 and np.abs(np.median(vals) - default) < 30 else float(default)
    ys_ = slice(PADc + int(Hc * 0.25), PADc + int(Hc * 0.75)); xs_ = slice(PADc + int(Wc * 0.25), PADc + int(Wc * 0.75))
    first = lambda m, ax: np.where(m.any(ax), m.argmax(ax).astype(np.float64), np.nan); last = lambda m, ax: np.where(m.any(ax), (m.shape[ax] - 1 - np.flip(m, ax).argmax(ax)).astype(np.float64), np.nan)
    xL = side(first(MR[ys_], 1), PADc); xR = side(last(MR[ys_], 1), PADc + Wc - 1); yT = side(first(MR[:, xs_], 0), PADc); yB = side(last(MR[:, xs_], 0), PADc + Hc - 1)
    yy, xx = np.mgrid[0:HR, 0:WR].astype(np.float32); cxr, cyr, hx, hy = (xL + xR) / 2, (yT + yB) / 2, (xR - xL) / 2, (yB - yT) / 2
    def sdf(r):
        qx = np.abs(xx - cxr) - (hx - r); qy = np.abs(yy - cyr) - (hy - r); return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    best = (-1, 30); cm = (np.abs(xx - cxr) > hx - 100) & (np.abs(yy - cyr) > hy - 100) & (np.abs(xx - cxr) < hx + 10) & (np.abs(yy - cyr) < hy + 10)
    for r in range(8, 96, 4):                                      # 角の まるみ：板の 形と いちばん 合う もの（角の 所 だけ くらべる）
        best = max(best, (((sdf(r) < 0) == MR)[cm].sum() / max(1, cm.sum()), r))
    r = best[1]; d = -sdf(r)
    # ふちに そった 場所（s）：上の 辺の 左から 時計回り
    wi, hi = 2 * (hx - r), 2 * (hy - r); arc = np.pi * r / 2; Lp = int(round(2 * (wi + hi) + 4 * arc)); px = xx - cxr; py = yy - cyr; ax_ = np.abs(px) - (hx - r); ay_ = np.abs(py) - (hy - r)
    corner = (ax_ > 0) & (ay_ > 0); ang = np.arctan2(np.maximum(ay_, 1e-6), np.maximum(ax_, 1e-6))             # 0＝横の 辺の 方 … π/2＝たての 辺の 方（角の 中）
    top = (~corner) & (ay_ >= ax_) & (py < 0); bot = (~corner) & (ay_ >= ax_) & (py >= 0); rgt = (~corner) & (ay_ < ax_) & (px >= 0); lft = (~corner) & (ay_ < ax_) & (px < 0)
    sp = np.zeros((HR, WR), np.float32)
    sp[top] = (px[top] + (hx - r)); sp[rgt] = wi + arc + (py[rgt] + (hy - r)); sp[bot] = wi + arc + hi + arc + ((hx - r) - px[bot]); sp[lft] = 2 * wi + hi + 3 * arc + ((hy - r) - py[lft])
    c_tr = corner & (px >= 0) & (py < 0); c_br = corner & (px >= 0) & (py >= 0); c_bl = corner & (px < 0) & (py >= 0); c_tl = corner & (px < 0) & (py < 0)
    sp[c_tr] = wi + (np.pi / 2 - ang[c_tr]) * r; sp[c_br] = wi + arc + hi + ang[c_br] * r; sp[c_bl] = 2 * wi + hi + 2 * arc + (np.pi / 2 - ang[c_bl]) * r; sp[c_tl] = 2 * wi + 2 * hi + 3 * arc + ang[c_tl] * r
    si = np.clip(sp.astype(np.int32), 0, Lp - 1); db = np.clip(np.floor(d).astype(np.int32), 0, D - 1)
    sel = MR & (d > -8) & (d <= D); U = np.zeros((D, Lp, 3), np.float64); Wt = np.zeros((D, Lp), np.float64)
    np.add.at(U, (db[sel], si[sel]), devR[sel]); np.add.at(Wt, (db[sel], si[sel]), 1)
    for k in range(D):                                             # あいた ます（物に かくれた 所）は となりの 値
        have = Wt[k] > 0
        if have.any():
            U[k, have] /= Wt[k, have][:, None]
            if not have.all(): nn = ndimage.distance_transform_edt(~np.r_[have, have, have], return_indices=True)[1][0][Lp:2 * Lp] % Lp; U[k] = U[k, nn]
    Um = ndimage.median_filter(U, size=(1, 301, 1), mode='wrap'); Um = ndimage.uniform_filter1d(Um, size=41, axis=1, mode='wrap'); Um = ndimage.uniform_filter1d(Um, size=3, axis=0, mode='nearest')
    fade = np.clip((D - d) / 16.0, 0, 1)[..., None]; synR = (Um[db, si] * fade).astype(np.float32); synR[d > D] = 0      # ふちから はなれると 面の 色へ
    syn = cv2.warpPerspective(synR, Hm, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    a = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 0.8)[..., None]; out = np.clip(P * (1 - a) + (S + syn) * a, 0, 255)      # ふちを なじませる（1px）
    if dbg:
        x0, y0, x1, y1 = [int(t) for t in (max(0, q[:, 0].min() - 50), max(0, q[:, 1].min() - 50), min(W, q[:, 0].max() + 50), min(H, q[:, 1].max() + 50))]
        v = P.copy(); edge = cv2.morphologyEx(M.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0; v[edge] = (255, 0, 255); gm = guard & roi & ~M; v[gm] = v[gm] * 0.6 + np.array([0, 255, 0]) * 0.4
        cv2.polylines(v, [np.round(q).astype(np.int32)], True, (255, 255, 0), 1)
        sh = np.vstack([np.hstack([P[y0:y1, x0:x1], out[y0:y1, x0:x1]]), np.hstack([v[y0:y1, x0:x1], np.clip(128 + (out[y0:y1, x0:x1] - P[y0:y1, x0:x1]) * 3, 0, 255)])]).astype(np.uint8)
        Image.fromarray(sh).resize((int(sh.shape[1] * 0.62), int(sh.shape[0] * 0.62)), Image.LANCZOS).save(dbg, quality=90)
    return (out + 0.5).astype(np.uint8), M


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('使い方：bcp_blank.py <絵の フォルダ> <出す フォルダ> [デザイン…]'); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); dbgd = os.environ.get('DBG')
    if dbgd: os.makedirs(dbgd, exist_ok=True)
    for n in (sys.argv[3:] or names()):
        o, M = clean(src, n, cfg_of(n), os.path.join(dbgd, f'{n}.jpg') if dbgd else None); f = os.path.join(out, f'bcp_{n}{SUF}.webp'); Image.fromarray(o).save(f, 'WEBP', quality=90, method=6)
        print(n, 'ぬり直した 点', int(M.sum()), '→', f, os.path.getsize(f), flush=True)
