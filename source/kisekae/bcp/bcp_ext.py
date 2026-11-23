# 結果ボードカスタム（絵の ボード）：絵の 上・下に 足す 所（もとの 絵より 外）を 作り直す（第4.215版）
#   まさちゃん 2026/11/24 01:31「②四枚目の上赤丸のところ、iPadのスクリーンショットで写ってたバッテリーわ時間などがぼやけて入ってるから消して！
#     ③十枚目の赤丸の絵と合わせて描いてる光の線がずれていたり、ぼやけすぎていたり、汚い線になっている壁紙がないか確認して、全て改良して！」
#   前の 作り方（bcp_bg.py：はしの 行を 横に 大きく ならして まん中から のばす radial／鏡 mirror／ぼかし glow）は、
#     ・光の すじの ふちが ぼやける・まん中が 合わないと すじの 向きが ずれる（つなぎ目で「く」の字）・はしで 切れた 紙ふぶきが すじに なる
#     ・鏡は すじが 折れる・物（キャラの 耳・観客・自撮り棒）が さかさまに うつる・つなぎ目に 線が 出る
#   もとの 作業フォルダは もう ない ので、**できあがった 絵（bcp_<デザイン>.webp：1170×2532）から** 足した 所 だけを 作り直す（もとの 絵の 所は かえない）。
#   前の 絵は 消さない・上書きしない（できた 絵は bcp_blank.py が 板を ぬり直して bcp_<デザイン>_b2.webp に する）
#
#   python3 kisekae/bcp/bcp_ext.py <絵の フォルダ（ios/bcp_assets）> <出す フォルダ> [デザイン…]     … bcp_<デザイン>.png（上下を 作り直した 絵・板は まだ もとの まま）
#
#   光の すじ（extend）：
#     1. すじは まん中 c を 通る 線：はしの 帯（もとの 絵の はしの 160行）を c から 見た 向きで まっすぐに 直す（straighten）
#     2. はしの 行に 合わせた 色 A（はしの 4行の 平均）。紙ふぶき・花びら（帯の まん中の 値から はなれた 所）は 帯の まん中の 値の 形に かえて、明るさは 両がわの はしの 行に 合わせる
#     3. 光の 強さ：すじ ＝ 地の 色 F ＋ 強さ a ×（A − F）。もとの 絵で はしへ 行く ほど 弱く なる 速さ（fade_len）の まま 外へ つづける（はしっこで ちょうど 0）
#     4. 足す 所：はしの 行の 場所から c の 向きへ まっすぐ（はしでは もとの 絵と 同じ 色・同じ 場所＝ずれない・ぼやけない）
#     5. はしで 切れて いる 小さな 物は もとの 絵の 方も すじの 色に もどす。消さない 物（ライト など）は 足す 所へ 少し にじませて 消す（ぷつっと 切れない）
#   まん中 c：はしの 行を ものさしに して、帯の 中の もようが いちばん そろう 点（fit_center）。デザインごとに 測った 値を FAM に 書いて ある
#   すじで ない 所：reflect（やわらかい 床の うつりこみ：はなれる ほど ぼかして 暗く）・fade（はしの 色を のばして ぼかして 暗く）
import sys, os, numpy as np, cv2
from scipy import ndimage
from PIL import Image

def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def band_rows(H, side, seam, band):
    """帯の 行（はしから 中へ）と はしの 行"""
    return (np.arange(seam, min(H, seam + band)), seam) if side == 'top' else (np.arange(seam - 1, max(0, seam - band) - 1, -1), seam - 1)


def straighten(P, side, seam, m, band):
    """帯を「すじが たてに まっすぐ」な 形に：T[j, xs] = 絵[はしから j 行 中, xs − m(xs)·j]。→ T・ok"""
    H, W = P.shape[:2]; rows, e0 = band_rows(H, side, seam, band); B = len(rows)
    xs = np.arange(W, dtype=np.float64); T = np.zeros((B, W, 3), np.float32); ok = np.zeros((B, W), bool)
    for j, y in enumerate(rows):
        x = xs - m * j; v = (x >= 0) & (x <= W - 1); ok[j] = v; xc = np.clip(x, 0, W - 1)
        for ch in range(3): T[j, :, ch] = np.interp(xc, xs, P[y, :, ch])
    return T, ok, rows


def seam_colors(T, ok, mrows=4, thr=30.0, tall=(70, 150), F=None):
    """はしの 行に 合わせた 色 A(xs)・地の 色 F・行ごとの 光の 強さ a（はしで 1）・物の しるし（はしの 行）。
       光の すじは「地の 色 F ＋ 強さ a_j ×（A − F）」：はしへ 行く ほど 光が 弱く なって 地の 色に 近づく（行 ぜんぶを 同じ 倍に する 形では 合わない）"""
    B, W = T.shape[:2]; L = np.where(ok, lum(T), np.nan)
    if F is None:
        lv = L[np.isfinite(L)]; cut = np.percentile(lv, 6); F = np.median(T[ok & (lum(T) <= cut)], axis=0)
    F = np.asarray(F, np.float32); lF = float(lum(F))
    wv = ok[:mrows].astype(np.float32)[..., None]; A_s = (T[:mrows] * wv).sum(0) / np.maximum(wv.sum(0), 1e-3); have = ok[:mrows].any(0)
    # 光の 強さ a_j：帯の まん中の 値（物に 強い）で 光の すじの 向きを えらんで、行ごとに「地からの 明るさ」の 比の まん中の 値
    with np.errstate(invalid='ignore', divide='ignore'):
        dT = np.nanmedian(L[:min(B, tall[1])], axis=0) - lF
        beam = have & np.isfinite(dT) & (dT > max(6.0, 0.35 * np.nanpercentile(dT[np.isfinite(dT)], 90)))
        a = np.nanmedian(np.where(beam[None], (L - lF) / np.maximum(dT[None], 1e-3), np.nan), axis=1)
    a = np.where(np.isfinite(a), a, 1.0); a = ndimage.gaussian_filter1d(a, 3, mode='nearest'); a = np.maximum(a / max(float(a[:mrows].mean()), 1e-3), 0.15).astype(np.float32)
    Tn = F + (T - F) / a[:, None, None]
    def med(k):
        k = min(k, B); mm = np.ma.array(Tn[:k], mask=~np.repeat(ok[:k][..., None], 3, 2)); At = np.ma.median(mm, axis=0).filled(np.nan).astype(np.float32)
        dv = np.abs(Tn[:k] - At[None]).max(2); inl = (ok[:k] & (np.nan_to_num(dv, nan=1e9) < thr)).sum(0) / np.maximum(ok[:k].sum(0), 1)
        return At, (inl >= 0.5) & np.isfinite(At).all(1)
    A1, r1 = med(tall[0]); A2, r2 = med(tall[1])
    dev = np.nan_to_num(np.abs(A_s - A1).max(1), nan=1e9); strong = ndimage.binary_opening(dev > thr, iterations=1)
    # 物の ふちの にじみ まで：強い ずれ（thr）に つながる 弱い ずれ（thr の 0.4倍）も 物
    lw, _ = ndimage.label(dev > thr * 0.4); ids = np.unique(lw[strong]); flag = np.isin(lw, ids[ids > 0]) | ~have
    flag = ndimage.binary_dilation(flag, iterations=9)
    # 物の 所（flag の つづき）：形は 帯の まん中の 値（A2：すじの ふちの 場所が のこる）・明るさは 両がわの はしの 行に 合わせる（両がわの 比を 線で つなぐ）
    A = A_s.copy(); idx = np.arange(W); lab, nrun = ndimage.label(flag); lA2 = lum(A2) - lF; lAs = lum(A_s) - lF
    for k in range(1, nrun + 1):
        cols = np.nonzero(lab == k)[0]; s0, e0 = int(cols[0]), int(cols[-1]) + 1
        def side_ratio(lo, hi):
            lo, hi = max(lo, 0), min(hi, W)
            if hi - lo < 3: return None
            sel = ~flag[lo:hi] & r2[lo:hi] & (np.abs(lA2[lo:hi]) > 6)
            return float(np.median(lAs[lo:hi][sel] / lA2[lo:hi][sel])) if sel.sum() >= 3 else None
        rl, rr = side_ratio(s0 - 26, s0 - 2), side_ratio(e0 + 2, e0 + 26)
        if rl is None and rr is None: rl = rr = 1.0
        rl = rr if rl is None else rl; rr = rl if rr is None else rr
        rho = np.clip(np.linspace(rl, rr, e0 - s0), 0.2, 5.0)[:, None]
        okc = r2[s0:e0] & np.isfinite(A2[s0:e0]).all(1)
        if okc.mean() >= 0.6:
            g = F + (np.nan_to_num(A2[s0:e0]) - F) * rho
            if not okc.all():                                               # 信じられない 向きは となりから
                ii = np.arange(e0 - s0)
                for ch in range(3): g[:, ch] = np.interp(ii, ii[okc], g[okc, ch])
            A[s0:e0] = g
        else:                                                               # 帯の おくまで 物：両がわの はしの 行を 線で つなぐ
            l_ = A_s[max(s0 - 3, 0):max(s0, 1)].mean(0) if s0 > 0 else A_s[min(e0, W - 1)]
            r_ = A_s[min(e0, W - 1):min(e0 + 3, W)].mean(0) if e0 < W else l_
            A[s0:e0] = l_[None] + (r_ - l_)[None] * np.linspace(0, 1, e0 - s0)[:, None]
    wf = ndimage.gaussian_filter1d(flag.astype(np.float32), 2.0); mix = np.clip(wf * (1 - wf) * 4, 0, 1)[:, None]
    Asm = np.stack([ndimage.gaussian_filter1d(A[:, ch], 1.5) for ch in range(3)], 1); A = A * (1 - mix) + Asm * mix
    return A.astype(np.float32), F, a, flag


def fade_len(a, n=45):
    """はしの 近くで 光が 弱く なる 速さ：a ≈ exp(j/τ) の τ（行）"""
    j = np.arange(min(n, len(a))); la = np.log(np.maximum(a[:len(j)], 1e-3)); s = np.polyfit(j, la, 1)[0]
    return float(1.0 / s) if s > 1e-4 else 1e4


def extend(P, side, seam, m, band=160, tau=None, stretch=1.8, tau_rng=(70.0, 260.0), end=None, floor=(10, 8, 16), thr=30.0, erase=True, soft=0.0, F=None, max_obj=None,
           protect=None, res_len=28.0, dbg=None):
    """足す 所（top：seam より 上／bottom：seam から 下）を、はしの 行から かたむき m(x) で まっすぐ のばして 作る。→ 新しい 絵・物を 消した 所
       光：地の 色 ＋ exp(−はなれた 行/τ)×（すじの 色 − 地の 色）。地の 色は はなれる ほど floor へ。end（0〜1）：足す 所の どこで 光を 0 に するか（なければ はしっこ）
       はしで 切れて いる 物：小さな 物（紙ふぶき・花びら）は もとの 絵の 方も すじの 色に もどす。消さない 物（protect・帯の おくまで つづく 大きな 物：ライト・キャラ）は、
       足す 所へ 少し だけ にじませて 消す（res_len 行で 1/e：はしで ぷつっと 切れない）"""
    H, W = P.shape[:2]; out = P.copy(); T, ok, rows = straighten(P, side, seam, m, band); B = len(rows)
    A, F, a, flag = seam_colors(T, ok, thr=thr, F=F)
    ext = np.arange(0, seam) if side == 'top' else np.arange(seam, H); dist = (seam - ext if side == 'top' else ext - seam + 1).astype(np.float64); n = len(ext)
    xs = np.arange(W, dtype=np.float64); model = F + (A[None] - F) * a[:, None, None]
    # ── はしで 切れて いる 物を さがす（まっすぐに 直した 帯の 中）
    sel = np.zeros((B, W), bool)
    if erase:
        b2 = min(B, 130) if max_obj is None else min(B, max_obj)
        dev = np.where(ok, np.abs(T - model).max(2), 0)[:b2]; jj = np.arange(b2, dtype=np.float32)[:, None]
        strong = ndimage.binary_opening(dev > thr * (1.2 + jj / 35.0), iterations=1)          # おくへ 行く ほど 形の 当てはまりが あまい：しきい値を 上げる
        lab, nl = ndimage.label(strong); touch = np.unique(lab[0:3][lab[0:3] > 0]); core = np.zeros_like(strong)
        for t_ in touch:
            comp = lab == t_; hgt = np.nonzero(comp.any(1))[0]
            if len(hgt) and hgt.max() < b2 - 8: core |= comp           # 帯の おくまで つづく 物（キャラ・大きな 飾り）は 消さない
        if protect is not None:                                        # 消さない 所（絵の 場所）→ まっすぐに 直した 帯の 場所
            pT = np.zeros((b2, W), bool)
            for j in range(b2):
                x = np.clip(np.round(xs - m * j).astype(int), 0, W - 1); pT[j] = protect[rows[j], x]
            lab2, _ = ndimage.label(core); bad = np.unique(lab2[pT & core]); core &= ~np.isin(lab2, bad[bad > 0])
        weak = dev > thr * 0.45 * (1 + jj / 60.0); lw2, _ = ndimage.label(weak | core); ids = np.unique(lw2[core])
        grow = np.isin(lw2, ids[ids > 0]) & ndimage.binary_dilation(core, iterations=12)
        sel[:b2] = ndimage.binary_dilation(ndimage.binary_closing(core | grow, iterations=3), iterations=6)      # ふちの にじみ・かげ まで（広めに）
    # ── はしの 行に のこる「すじで ない もの」（消さない 物）：足す 所へ 少し にじませる
    T2 = np.where(sel[..., None], model, T); mr = 4; wv = ok[:mr].astype(np.float32)[..., None]
    res = (T2[:mr] * wv).sum(0) / np.maximum(wv.sum(0), 1e-3) - (F + (A - F) * float(a[:mr].mean())); res[~ok[:mr].any(0)] = 0
    res = np.where(np.abs(res).max(1, keepdims=True) > 6, res, 0); res = np.stack([ndimage.gaussian_filter1d(res[:, ch], 1.0) for ch in range(3)], 1)
    tf = fade_len(a); tau = float(np.clip(tf * stretch, *tau_rng)) if tau is None else float(tau)
    t = dist / max(float(n), 1.0); e = 1.0 if end is None else float(end)
    amp = np.exp(-dist / tau) * np.clip(1 - (t / e) ** 3, 0, 1)                    # はしっこ（end）で ちょうど 0
    sm = np.clip(t, 0, 1); sm = sm * sm * (3 - 2 * sm); fl = np.array(floor, np.float32); has_res = bool(np.abs(res).max() > 0)
    for i, y in enumerate(ext):
        X = xs + m * dist[i]; src = np.interp(xs, X, xs)
        col = np.stack([np.interp(src, xs, A[:, ch]) for ch in range(3)], 1)
        if soft:
            sg = soft * dist[i] / 100.0
            if sg > 0.3: col = cv2.GaussianBlur(col[None].astype(np.float32), (0, 0), sg)[0]
        Fi = F * (1 - sm[i]) + fl * sm[i]
        row = Fi + (col - F) * amp[i]
        if has_res and dist[i] < res_len * 5:
            rr = np.stack([np.interp(src, xs, res[:, ch]) for ch in range(3)], 1)
            sg = 0.6 + dist[i] * 0.12; rr = cv2.GaussianBlur(rr[None].astype(np.float32), (0, 0), sg)[0]      # はなれる ほど ぼかす
            row = row + rr * np.exp(-dist[i] / res_len)
        out[y] = row
    erased = np.zeros((H, W), bool)
    if sel.any():
        selI = np.zeros((B, W), np.float32); modI = np.zeros((B, W, 3), np.float32)
        for j in range(B):
            X = xs - m * j; src = np.interp(xs, X, xs)
            selI[j] = np.interp(src, xs, sel[j].astype(np.float32)); modI[j] = np.stack([np.interp(src, xs, model[j, :, ch]) for ch in range(3)], 1)
        sub = P[rows]; am = cv2.GaussianBlur((selI > 0.5).astype(np.float32), (0, 0), 2.2)[..., None]
        om = ndimage.binary_dilation(selI > 0.3, iterations=4); resid = sub - modI; wgt = (~om).astype(np.float32)[..., None]
        num = cv2.GaussianBlur(resid * wgt, (0, 0), 10); den = cv2.GaussianBlur(wgt, (0, 0), 10)
        if den.ndim == 2: den = den[..., None]
        fill = modI + num / np.maximum(den, 1e-3)
        out[rows] = sub * (1 - am) + fill * am; erased[rows] = selI > 0.5
    if dbg is not None: dbg.update(A=A, a=a, F=F, flag=flag, rows=rows, T=T, tau=tau, tau_fit=tf, res=res)
    return np.clip(out, 0, 255), erased


def object_matte(P, y0, y1, seed=70.0, weak=20.0, ksize=201, drop_last=True, min_px=120, keep_first=True):
    """行 y0〜y1 の 中の 物（紙ふぶき・花びら）の すき通し α（H×W・ほかは 0）。地は 大きな まん中の 値の ぼかし。下の はしで 切れて いる 物は はぶく（drop_last）"""
    H, W = P.shape[:2]; sub = np.clip(P[y0:y1], 0, 255).astype(np.uint8)
    pad = ksize // 2; sp = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_REFLECT)
    bg = np.dstack([cv2.medianBlur(np.ascontiguousarray(sp[..., c]), ksize) for c in range(3)])[pad:-pad, pad:-pad].astype(np.float32)
    d = np.abs(sub.astype(np.float32) - bg).max(2)
    st = ndimage.binary_opening(d > seed, iterations=1); wk = d > weak
    lab, n = ndimage.label(wk); ids = np.unique(lab[st]); ids = ids[ids > 0]
    if drop_last: ids = np.setdiff1d(ids, np.unique(lab[-2:]))
    if not keep_first: ids = np.setdiff1d(ids, np.unique(lab[:2]))
    cnt = np.bincount(lab.ravel(), minlength=n + 1); ids = np.array([i for i in ids if cnt[i] >= min_px], int)
    m = np.isin(lab, ids); m = ndimage.binary_fill_holes(m)
    a = cv2.GaussianBlur(ndimage.binary_dilation(m, iterations=2).astype(np.float32), (0, 0), 1.3)
    a = np.clip(a * 1.25 - 0.1, 0, 1)
    out = np.zeros((H, W), np.float32); out[y0:y1] = a
    return out, bg


def _sample_rows(P, rows, cx, cy, us):
    H, W = P.shape[:2]; xs = np.arange(W, dtype=np.float64); S = np.zeros((len(rows), len(us), 3), np.float32); ok = np.zeros((len(rows), len(us)), bool)
    for j, y in enumerate(rows):
        x = cx + us * (cy - y); v = (x >= 0) & (x <= W - 1); ok[j] = v; xc = np.clip(x, 0, W - 1)
        for ch in range(3): S[j, :, ch] = np.interp(xc, xs, P[y, :, ch])
    return S, ok


def seam_cost(P, side, seam, band, cx, cy):
    """c の 当てはまり（小さい ほど よい）：c を 通る 線に そって 帯を 読むと、はしの 行の もようが 帯の 中でも 同じ 場所に あるか"""
    H, W = P.shape[:2]; rows = np.arange(seam, min(H, seam + band), 2) if side == 'top' else np.arange(seam - 1, max(0, seam - band) - 1, -2); e0 = rows[0]
    xs = np.arange(0, W, 2.0); S, ok = _sample_rows(P, list(rows), cx, cy, (xs - cx) / (cy - e0)); L = np.where(ok, lum(S), np.nan)
    with np.errstate(invalid='ignore'):
        rg = np.nanmedian(L, axis=1, keepdims=True); L = L / np.maximum(rg, 1.0) * np.nanmedian(rg); cost = np.nanmedian(np.abs(L[3:] - np.nanmean(L[:3], axis=0, keepdims=True)), axis=1)
    return float(np.nanmean(cost))


def fit_center(P, side, seam, band=140, cxr=(430, 740), dyr=(250, 3000), n=(9, 14), rounds=3):
    """まん中 c を 広く さがす（たては 対数の きざみ）。→ (cost, cx, cy)。python3 bcp_ext.py --fit <絵の フォルダ> <デザイン> <top|bottom> <はしの 行> で 測る"""
    lo, hi = cxr; a, b = np.log(dyr[0]), np.log(dyr[1]); best = None; sgn = 1 if side == 'top' else -1
    for _ in range(rounds):
        cand = [(seam_cost(P, side, seam, band, cx, (seam if side == 'top' else seam - 1) + sgn * np.exp(ld)), cx, (seam if side == 'top' else seam - 1) + sgn * np.exp(ld), ld) for cx in np.linspace(lo, hi, n[0]) for ld in np.linspace(a, b, n[1])]
        best = min(cand); wx = (hi - lo) / (n[0] - 1) * 1.2; wl = (b - a) / (n[1] - 1) * 1.2; lo, hi, a, b = best[1] - wx, best[1] + wx, best[3] - wl, best[3] + wl
    return best[:3]


# ───────── すじで ない 所（やわらかい うつりこみ・のばして 暗く）─────────
def _blur_rows(img, sig):
    """行ごとに ちがう ぼかし（sig[i]）：いくつかの 強さで ぼかした 絵を 行ごとに まぜる"""
    levels = [0.0, 1.5, 3.0, 6.0, 12.0, 24.0, 48.0, 96.0]; stack = [img] + [cv2.GaussianBlur(img, (0, 0), s) for s in levels[1:]]
    out = np.zeros_like(img); lv = np.array(levels)
    for i in range(img.shape[0]):
        s = float(np.clip(sig[i], 0, levels[-1])); k = int(np.searchsorted(lv, s, side='right') - 1); k = min(k, len(levels) - 2)
        f = (s - lv[k]) / (lv[k + 1] - lv[k]); out[i] = stack[k][i] * (1 - f) + stack[k + 1][i] * f
    return out


def undim(P, seam, nb=90, amount=0.42, power=1.3):
    """前の 作り方（bcp_bg.py の 鏡）が もとの 絵の 下の 90行を 暗く した 分を もどした 絵（もとの 明るさ）と、行ごとの 倍"""
    f = np.ones(P.shape[0], np.float32); i = np.arange(nb); f[seam - nb + i] = 1.0 - amount * ((i + 1) / nb) ** power
    return P / f[:, None, None], f


def reflect(P, seam, tau=70.0, sig0=1.2, sig_k=0.14, floor=(10, 8, 16), dimmed=True, k0=None, end=1.0):
    """下の 足す 所（seam から 下）を やわらかい 床の うつりこみに。dimmed：もとの 絵の 下の 90行が 暗く して ある（前の 作り方）
       k0：つなぎ目での うつりこみの 明るさ（なければ もとの 絵の さいごの 行と 同じ ＝ 線が 出ない）"""
    H, W = P.shape[:2]; n = H - seam; out = P.copy()
    src, f = undim(P, seam) if dimmed else (P, np.ones(H, np.float32))
    k0 = float(f[seam - 1]) if k0 is None else k0
    m = min(n, seam); mir = src[seam - m:seam][::-1].copy()                      # mir[i] ＝ もとの 絵の seam−1−i 行
    i = np.arange(m, dtype=np.float32); mir = _blur_rows(mir, sig0 + sig_k * i)
    t = i / max(float(n), 1.0); amp = k0 * np.exp(-i / tau) * np.clip(1 - (t / end) ** 3, 0, 1)
    fl = np.array(floor, np.float32)
    out[seam:seam + m] = mir * amp[:, None, None] + fl * (1 - amp[:, None, None])
    if m < n: out[seam + m:] = fl
    return out


def fade(P, seam, side='bottom', tau=60.0, sig0=2.0, sig_k=0.45, floor=(10, 8, 16), end=1.0, avg=3):
    """足す 所を、はしの 行の 色を のばして 暗く（はなれる ほど 横に ぼかす）"""
    H, W = P.shape[:2]; out = P.copy()
    if side == 'bottom':
        ext = np.arange(seam, H); edge = P[seam - avg:seam].mean(0)
    else:
        ext = np.arange(seam - 1, -1, -1); edge = P[seam:seam + avg].mean(0)
    n = len(ext); i = np.arange(n, dtype=np.float32)
    rows = np.repeat(edge[None], n, 0).astype(np.float32); rows = _blur_rows(rows, sig0 + sig_k * i)
    t = i / max(float(n), 1.0); amp = np.exp(-i / tau) * np.clip(1 - (t / end) ** 3, 0, 1); fl = np.array(floor, np.float32)
    out[ext] = rows * amp[:, None, None] + fl * (1 - amp[:, None, None])
    return out


# ───────── デザインごとの きまり ─────────
XS = np.arange(1170.0)


def field(c, e0):
    """まん中 c から 広がる すじの かたむき（はしの 行 e0 で）：外へ 1行 進むと x が どれだけ ずれるか"""
    return (XS - c[0]) / (c[1] - e0)


def keep_objects(P, out, y0, y1, **kw):
    """行 y0〜y1 の 物（紙ふぶき・花びら）を もとの 絵から もどす"""
    al, _ = object_matte(P, y0, y1, **kw); return out * (1 - al[..., None]) + P * al[..., None]


def inpaint_boxes(P, boxes, radius=9):
    """四角の 中を まわりの 色で うめる（ぼやけた 字の あと など：まわりも なめらかな 所）"""
    m = np.zeros(P.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes: m[y0:y1, x0:x1] = 255
    m = cv2.GaussianBlur(m, (0, 0), 3) > 40
    out = cv2.inpaint(np.clip(P, 0, 255).astype(np.uint8), m.astype(np.uint8) * 255, radius, cv2.INPAINT_TELEA).astype(np.float32)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0)[..., None]; sm = cv2.GaussianBlur(out, (0, 0), 4.0); out = out * (1 - a) + sm * a
    return P * (1 - a) + out * a


def toast(P, n):
    # 馬達の祝杯：上の 105行は 鏡（馬の 耳が さかさまに うつって いた）→ はしの 色を のばして ぼかして 暗く（ライトは 上から 当たる ので すじは のばさない）
    return fade(P, 105 + INSET, side='top', tau=50.0)


def race(P, n):
    # 馬レース：もとの 絵の 上の はしに のこって いた iPad の 画面の 時刻（左）と 録画の しるし（右）の ぼやけた あとを まわりの 色で うめる（②）→ 光の すじを 上へ（上の 両すみの ライトは 消さない）
    #   下：観客の かげが 鏡で さかさまに うつって いた → はしの 色を のばして 暗く
    P1 = inpaint_boxes(P, [(36, 246, 172, 290), (1018, 244, 1126, 290)])
    prot = np.zeros(P.shape[:2], bool); prot[239:330, 0:130] = True; prot[239:330, 1040:1170] = True
    o, _ = extend(P1, 'top', 239, field((590, 1000), 239), band=150, protect=prot)
    return fade(o, 2171 - INSET, tau=60.0)


def selfie(P, n):
    # 自撮り：上は すじが ぼやけて 黄色い 紙ふぶきが 上まで のびて いた → 光の すじ。下は 自撮り棒・紙ふぶきが くっきり さかさまに うつって いた → やわらかい うつりこみ
    o, _ = extend(P, 'top', 338 + INSET, field((714, 955), 338 + INSET), band=150)
    return reflect(o, 2012, tau=80.0)


def carry(P, n):
    # 馬が運ぶ：上の 620行（すじが ずれて 四角い 段に なって いた）→ 光の すじ
    o, _ = extend(P, 'top', 620 + INSET, field((570, 1370), 620 + INSET), band=150)
    return o


def bouquet(P, n):
    # 花束：上は すじが つなぎ目で ずれて いた → 光の すじ。下は もとの 絵の 下の 260行ほどが 四角い ぼかしの 重なり（すじが とちゅうで 切れる）→ その 上から すじを 作り直して、花びら・紙ふぶきは もどす
    one = n == 'bouquet1'; top, ct = (251, (585, 1332)) if one else (280, (585, 1360)); sb, cb, end = (1836, (504, 1126), 2093) if one else (1864, (495, 1154), 2121)
    o, _ = extend(P, 'top', top + INSET, field(ct, top + INSET), band=150)
    o, _ = extend(o, 'bottom', sb, -field(cb, sb - 1), band=160)
    return keep_objects(P, o, sb - 160, end)


def miss2(P, n):
    # ハズレ② 次…！：上の 525行（空）は 横に 大きく ぼかした 色の 帯（たての 白い むら）だった → 空の 光の すじを そのまま 上へ（地の 色＝空の 青・上へ 行く ほど 少し 濃い 青）
    #   下（芝）：ぼかしの たての むら → はしの 色を のばして、はなれる ほど 横に ならして 少し 暗く
    o, _ = extend(P, 'top', 525 + INSET + 1, field((536, 1356), 525 + INSET + 1), band=150, floor=(28, 84, 170))
    g = P[2168:2188].reshape(-1, 3).mean(0) * 0.72
    return fade(o, 2188, tau=300.0, floor=tuple(float(v) for v in g), sig0=3.0, sig_k=0.5)


INSET = 5                                # 前の つなぎ目の すぐ 内がわ（もとの 絵の はしの 数行）は 圧縮の にじみが ある：その ぶん 内がわから のばす
FAM = {'toast': toast, 'race': race, 'selfie': selfie, 'carry': carry, 'bouquet': bouquet, 'miss2': miss2}


def fam_of(n):
    for k in FAM:
        if n.startswith(k): return k
    return None


def make(src, name):
    """→ 上下を 作り直した 絵（float32）。きまりの ない デザインは もとの まま"""
    P = np.asarray(Image.open(os.path.join(src, f'bcp_{name}.webp')).convert('RGB')).astype(np.float32); f = fam_of(name)
    return FAM[f](P, name) if f else P


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--fit':
        P = np.asarray(Image.open(os.path.join(sys.argv[2], f'bcp_{sys.argv[3]}.webp')).convert('RGB')).astype(np.float32); print(fit_center(P, sys.argv[4], int(sys.argv[5]))); sys.exit(0)
    if len(sys.argv) < 3:
        print('使い方：bcp_ext.py <絵の フォルダ> <出す フォルダ> [デザイン…]'); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import bcp_app
    for n in (sys.argv[3:] or [n for _i, _k, st in bcp_app.ITEMS for _d, n in st]):
        o = make(src, n); Image.fromarray(np.clip(o + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(out, f'bcp_{n}.png')); print(n, fam_of(n) or '（そのまま）', flush=True)
