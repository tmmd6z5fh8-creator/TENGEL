# 結果ボードカスタム（絵の ボード）：絵の ボードの 字・行・飾りを 消す。設定（cfg.json）の 所だけ。
#   python3 bcp_clean.py <デザインの フォルダ>   → clean.png・clean_dbg.png
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
src = cv2.cvtColor(cv2.imread(os.path.join(D, cfg.get('src', 'src.png'))), cv2.COLOR_BGR2RGB).astype(np.float32)
H, W = src.shape[:2]
R, G, B = src[..., 0], src[..., 1], src[..., 2]
V = src.max(-1)
C = cfg['clean']
def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
def shape_mask(s):
    m = np.zeros((H, W), np.uint8)
    if 'bpoly' in s:
        # ボードの 面（350 × HP の 座標）の 四角 [x0,y0,x1,y1] を 絵の 板（cfg の quad）へ うつした 四すみ
        Qd = np.array(cfg['quad'], np.float32)
        wq_ = (np.linalg.norm(Qd[1] - Qd[0]) + np.linalg.norm(Qd[2] - Qd[3])) / 2; hq_ = (np.linalg.norm(Qd[3] - Qd[0]) + np.linalg.norm(Qd[2] - Qd[1])) / 2
        hp_ = float(cfg.get('hp') or round(350 * hq_ / wq_, 1))
        Mb = cv2.getPerspectiveTransform(np.array([(0, 0), (350, 0), (350, hp_), (0, hp_)], np.float32), Qd)
        bx0, by0, bx1, by1 = s['bpoly']
        pts = cv2.perspectiveTransform(np.array([[(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]], np.float32), Mb)[0]
        cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 1)
    elif 'poly' in s:
        cv2.fillPoly(m, [np.round(np.array(s['poly'])).astype(np.int32)], 1)
    elif 'rect' in s:
        x0, y0, x1, y1 = s['rect']; m[y0:y1, x0:x1] = 1
    elif 'brrect' in s:
        Qd = np.array(cfg['quad'], np.float32)
        wq_ = (np.linalg.norm(Qd[1] - Qd[0]) + np.linalg.norm(Qd[2] - Qd[3])) / 2; hq_ = (np.linalg.norm(Qd[3] - Qd[0]) + np.linalg.norm(Qd[2] - Qd[1])) / 2
        hp_ = float(cfg.get('hp') or round(350 * hq_ / wq_, 1))
        Kb = 4
        bx0, by0, bx1, by1, br_ = s['brrect']
        bm = np.zeros((int(hp_ * Kb) + 1, 350 * Kb + 1), np.uint8)
        bm[int(by0 * Kb):int(by1 * Kb), int(bx0 * Kb):int(bx1 * Kb)] = 1
        bm = cv2.morphologyEx(bm, cv2.MORPH_OPEN, disk(int(br_ * Kb)))
        Mb = cv2.getPerspectiveTransform(np.array([(0, 0), (350 * Kb, 0), (350 * Kb, hp_ * Kb), (0, hp_ * Kb)], np.float32), Qd)
        m = cv2.warpPerspective(bm, Mb, (W, H), flags=cv2.INTER_NEAREST)
    elif 'rrect' in s:
        x0, y0, x1, y1, r = s['rrect']; m[y0:y1, x0:x1] = 1
        r = int(min(r, (x1 - x0 - 1) // 2, (y1 - y0 - 1) // 2))          # 角の 丸みは 四角に おさまる 大きさまで
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(r))
    elif 'ellipse' in s:
        cx, cy, rx, ry = s['ellipse']; cv2.ellipse(m, (cx, cy), (rx, ry), 0, 0, 360, 1, -1)
    elif 'navy' in s:
        # 紺の かたまり（その 点を ふくむ もの）の 穴を うめた 形
        navy = (B > R + 12) & (B > G - 5) & (V < 140)
        lab, n = ndi.label(navy)
        x, y = s['navy']; k = lab[y, x]
        assert k, ('紺で ない 点', s['navy'])
        m = ndi.binary_fill_holes(lab == k).astype(np.uint8)
    if 'sat' in s:
        # その 中の あざやかな 所だけ（鎖の 輪 など：まわりの 地は のこさない）
        hsv_ = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        sm = ((hsv_[..., 1] > s['sat'][0]) & (hsv_[..., 2] > s['sat'][1])).astype(np.uint8)
        sm = cv2.dilate(sm, disk(s.get('dil', 2)))
        m = m & sm
    if s.get('shrink'):
        m = cv2.erode(m, disk(s['shrink']))
    if s.get('round'):
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(s['round']))
    if 'clip' in s:
        x0, y0, x1, y1 = s['clip']; c = np.zeros_like(m); c[y0:y1, x0:x1] = 1; m = m & c
    return m.astype(bool)
# 絵の 左右の はしに アプリの 画面が 写って いる（絵の まん中の 縦長の 舞台の 外）：舞台の はしの 光の すじを 外へ のばして うめる。
#   花の わく・きらきら・紙ふぶき（明るい 所・あたたかい 色の 暗い 所）は のこす。
#   side_rays = { c:[x,y]（光の まん中）, x:[左の はし, 右の はし]（舞台の 中の いちばん 外の 列）, med:25, fade:0.25 }
if 'side_rays' in C:
    sr = C['side_rays']; scx, scy = sr['c']; xl, xr = sr['x']
    Vs = src.max(-1)
    prot = (Vs > sr.get('v', 75)) | (((src[..., 0] - src[..., 2]) > 15) & (Vs > 35))
    prot = ndi.binary_closing(prot, iterations=sr.get('close', 4))
    prot = ndi.binary_fill_holes(prot)
    def edge_col(x0, x1):
        col = src[:, x0:x1].mean(1)                                 # H×3
        okc = ~prot[:, x0:x1].any(1)                                # 花で ない 行だけ
        ys_ok = np.nonzero(okc)[0]
        full = np.stack([np.interp(np.arange(H), ys_ok, col[ys_ok, c]) for c in range(3)], -1)
        return ndi.median_filter(full, size=(sr.get('med', 25), 1))
    colL = edge_col(xl, xl + 3); colR = edge_col(xr - 2, xr + 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ext = src.copy()
    for side, xe, colE in (('L', xl, colL), ('R', xr, colR)):
        m = (xx < xl) if side == 'L' else (xx > xr)
        t = (xe - scx) / np.where(np.abs(xx - scx) < 1e-3, 1e-3, xx - scx)
        ye = np.clip(scy + (yy - scy) * t, 0, H - 1)
        smp = np.stack([np.interp(ye[m], np.arange(H), colE[:, c]) for c in range(3)], -1)
        dist = np.abs(xx[m] - xe)
        k = 1 - sr.get('fade', 0.25) * np.clip(dist / 80.0, 0, 1)
        ext[m] = smp * k[:, None]
    side = (xx < xl) | (xx > xr)
    pm = cv2.GaussianBlur((prot & side).astype(np.float32), (0, 0), 1.2)
    pm = np.where(prot & side, np.maximum(pm, 0.7), pm)
    wv = side.astype(np.float32) * (1 - pm)
    src = src * (1 - wv[..., None]) + ext * wv[..., None]
    R, G, B = src[..., 0], src[..., 1], src[..., 2]; V = src.max(-1)
# 光の すじを 作り直す 所（resynth）：四角の 中を、はしの 行（edge）から 光の まん中 c へ むかう 線に そって のばした すじで おきかえる
#   （うすい アプリの 画面が 光の すじに かさなって いる 所。黒板 など のこす 物は 四角の 外に）。紙ふぶきは paste で もどす
#   resynth = [{ rect:[x0,y0,x1,y1], c:[cx,cy], edge:y, med:151, raw:40, raw_thr:95, len:1.0, blend:[左, 右, 上]（なじませる はば）, paste:[[x0,y0,x1,y1],…] }]
#   edge_line:[[xa,ya],[xb,yb]]（ななめの はし：黒板の 上の ふち など に そって）・dir:'down'（はしの 下を 作り直す：ボードの 下の 光の すじ）
def _paste_piece(dst, srcimg, pr):
    x0, y0, x1, y1 = pr
    p_ = srcimg[y0:y1, x0:x1]
    edge = np.concatenate([p_[:2].reshape(-1, 3), p_[-2:].reshape(-1, 3), p_[:, :2].reshape(-1, 3), p_[:, -2:].reshape(-1, 3)])
    bgc = np.median(edge, 0)
    d_ = np.linalg.norm(p_ - bgc, axis=-1)
    fc = np.median(p_[d_ >= np.percentile(d_, 97)], 0); dv = fc - bgc
    al = np.clip(((p_ - bgc) @ dv) / max(float(dv @ dv), 1.0), 0, 1)
    al = np.clip((al - 0.12) / 0.88, 0, 1)
    core_ = d_ >= 0.5 * d_.max()
    lab_, n_ = ndi.label(core_)
    if n_:
        sz_ = ndi.sum(core_, lab_, range(1, n_ + 1)); core_ = lab_ == (np.argmax(sz_) + 1)
    keep_ = cv2.GaussianBlur(ndi.binary_dilation(core_, iterations=2).astype(np.float32), (0, 0), 0.8)
    al = al * np.clip(keep_ * 1.5, 0, 1)
    al = np.maximum(al, cv2.GaussianBlur(ndi.binary_erosion(core_, iterations=1).astype(np.float32), (0, 0), 0.6))
    col = np.clip((p_ - (1 - al[..., None]) * bgc) / np.maximum(al[..., None], 1e-3), 0, 255)
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - al[..., None]) + col * al[..., None]
orig_src = src.copy()
for rs in C.get('resynth', []):
    x0, y0, x1, y1 = rs['rect']; cx_, cy_ = rs['c']
    if 'edge_line' in rs:
        (ax, ay), (bx, by) = rs['edge_line']
    else:
        ax, ay, bx, by = 0.0, float(rs['edge']), float(W - 1), float(rs['edge'])
    down = rs.get('dir', 'up') == 'down'
    # はしの 線に そった 色（1px ごと）：raw（3行 平均）・med（5行 × 横 med の なめらかな もの）
    Ln = int(np.ceil(np.hypot(bx - ax, by - ay))) + 1
    us = np.linspace(0, 1, Ln, dtype=np.float32)
    lx = (ax + (bx - ax) * us).astype(np.float32); ly = (ay + (by - ay) * us).astype(np.float32)
    strip = np.stack([cv2.remap(src.astype(np.float32), lx[None], (ly + o)[None], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)[0] for o in (-2, -1, 0, 1, 2)])
    raw = cv2.GaussianBlur(strip[1:4].mean(0)[None], (0, 0), 1.2)[0]
    med = ndi.median_filter(strip, size=(5, rs.get('med', 151), 1)).mean(0)
    med = cv2.GaussianBlur(med[None], (0, 0), 1.2)[0]
    dif = np.abs(raw - med).max(-1)
    out_ = ndi.binary_dilation(dif > rs.get('raw_thr', 95), iterations=6)
    wq = cv2.GaussianBlur(out_.astype(np.float32)[None], (0, 0), 3)[0][:, None]
    raw = raw * (1 - wq) + med * wq
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    # 光の まん中 c から この 点への 線と、はしの 線の 交わる 所 q
    dxl, dyl = bx - ax, by - ay
    rx, ry = xx - cx_, yy - cy_
    den = rx * dyl - ry * dxl
    den = np.where(np.abs(den) < 1e-6, 1e-6, den)
    sq = ((ax - cx_) * dyl - (ay - cy_) * dxl) / den
    qx = cx_ + sq * rx; qy = cy_ + sq * ry
    uu = np.clip(((qx - ax) * dxl + (qy - ay) * dyl) / max(dxl * dxl + dyl * dyl, 1e-6), 0, 1) * (Ln - 1)
    ii = np.arange(Ln, dtype=np.float32)
    at = lambda st: np.stack([np.interp(uu.ravel(), ii, st[:, c]).reshape(uu.shape) for c in range(3)], -1)
    dist = (yy - qy) if down else (qy - yy)
    Le = np.maximum((H - qy) if down else qy, 1)
    a_raw = np.clip(1 - np.clip(dist, 0, None) / float(rs.get('raw', 40)), 0, 1)[..., None]
    E = at(raw) * a_raw + at(med) * (1 - a_raw)
    sub = src[y0:y1, x0:x1]
    floor = np.median(sub.reshape(-1, 3)[sub.reshape(-1, 3).max(1) <= np.percentile(sub.max(-1), 8)], 0)
    k = (np.clip(1 - np.clip(dist, 0, None) / (rs.get('len', 1.0) * Le), 0, 1) ** 1.3)[..., None]
    E = E * k + floor * (1 - k)
    bl, br, bt = rs.get('blend', [0, 24, 0])
    wx = np.ones_like(xx)
    if br: wx *= np.clip((x1 - xx) / br, 0, 1)
    if bl: wx *= np.clip((xx - x0) / bl, 0, 1)
    if bt: wx *= np.clip(((y1 - yy) if down else (yy - y0)) / bt, 0, 1)
    wy = np.clip(dist / 3.0, 0, 1)          # はしの 線の すぐ 外から
    w_ = (wx * wy)[..., None]
    src[y0:y1, x0:x1] = sub * (1 - w_) + E * w_
    for pr in rs.get('paste', []):
        _paste_piece(src, orig_src, pr)
    print('resynth', rs['rect'], 'floor', floor.astype(int).tolist())
R, G, B = src[..., 0], src[..., 1], src[..., 2]; V = src.max(-1)
# うすく 写りこんだ アプリの 画面（時刻・字・タブ など：絵を 作った ときの 下じき）を 消す：暗い 所の 細かい もようを なめらかに（紙ふぶき・光・馬は のこす）
if 'deghost' in C:
    dg = C['deghost']
    band = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1 in dg['bands']:
        band[y0:y1, x0:x1] = 1
    band = cv2.GaussianBlur(band, (0, 0), 6)
    Vl = cv2.GaussianBlur(src.max(-1), (0, 0), 8)
    if dg.get('flat'):
        # 暗い 所だけで 大きく なめらかに（うすい カードの 形も 消える）
        dk = (Vl < dg.get('v', 110) - 30).astype(np.float32)
        sg = dg['flat']
        base = np.stack([cv2.GaussianBlur(src[..., c] * dk, (0, 0), sg) / np.maximum(cv2.GaussianBlur(dk, (0, 0), sg), 1e-4) for c in range(3)], -1)
    else:
        base = cv2.GaussianBlur(src, (0, 0), dg.get('sigma', 10))
    hsv0 = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    prot = ((hsv0[..., 1] > 100) & (hsv0[..., 2] > 150)) | (src.max(-1) > 200) | (((src[..., 0] - src[..., 2]) > dg.get('warm_rb', 45)) & (src.max(-1) > dg.get('warm_v', 0)))
    prot = cv2.GaussianBlur(ndi.binary_dilation(prot, iterations=4).astype(np.float32), (0, 0), 2)
    v = dg.get('v', 110)
    if dg.get('dark_max'):
        dm = dg['dark_max']
        Vp = src.max(-1)
        dk2 = (Vp < dg.get('dark_base', dm)).astype(np.float32)       # 地の 色は もっと 暗い 所から（写りこみを 入れない）
        sg2 = dg.get('dark_sigma', 25)
        base = np.stack([cv2.GaussianBlur(src[..., c] * dk2, (0, 0), sg2) / np.maximum(cv2.GaussianBlur(dk2, (0, 0), sg2), 1e-4) for c in range(3)], -1)
        wgt = band * np.clip((dm - Vp) / 10.0, 0, 1) * (1 - prot)
    else:
        wgt = band * np.clip((v - Vl) / 40, 0, 1) * (1 - prot)
    src = src * (1 - wgt[..., None]) + base * wgt[..., None]
# 先に 写す 所（となりの 絵を ずらして はる：旗の 下の 鎖など）
for p in C.get('patch', []):
    x0, y0, x1, y1 = p['dst']; dx, dy = p.get('dx', 0), p.get('dy', 0)
    if dx == 'auto':
        lo, hi = p.get('dx_range', [-220, -40]); bw = 4; best = None
        dlo, dhi = p.get('dy_range', [dy, dy])
        for e_ in range(dlo, dhi + 1):
            if y0 + e_ < 0 or y1 + e_ > H: continue
            for d_ in range(lo, hi + 1):
                if x0 + d_ - bw < 0 or x1 + d_ + bw > W: continue
                e = ((src[y0:y1, x0 - bw:x0] - src[y0 + e_:y1 + e_, x0 + d_ - bw:x0 + d_]) ** 2).sum() + ((src[y0:y1, x1:x1 + bw] - src[y0 + e_:y1 + e_, x1 + d_:x1 + d_ + bw]) ** 2).sum()
                if best is None or e < best[0]: best = (e, d_, e_)
        dx, dy = best[1], best[2]
        print('patch', p['dst'], 'auto dx', dx, 'dy', dy)
    cp = src[y0 + dy:y1 + dy, x0 + dx:x1 + dx].copy()
    fe = min(p.get('feather', 0), (x1 - x0) // 2)
    if fe:
        # 左右の はしは もとの 絵と まぜる（つなぎ目を 見えなく）
        wv = np.ones(x1 - x0, np.float32); wv[:fe] = np.linspace(0, 1, fe + 2)[1:-1]; wv[-fe:] = np.linspace(1, 0, fe + 2)[1:-1]
        cp = cp * wv[None, :, None] + src[y0:y1, x0:x1] * (1 - wv[None, :, None])
    src[y0:y1, x0:x1] = cp
R, G, B = src[..., 0], src[..., 1], src[..., 2]; V = src.max(-1)
region = np.zeros((H, W), bool)          # 中を ぜんぶ 消す 所
tregion = np.zeros((H, W), bool)         # 字（金・白・光）だけ 消す 所
for s in C['regions']:
    if s.get('only') == 'text':
        tregion |= shape_mask(s)
    else:
        region |= shape_mask(s)
if tregion.any():
    tx = C.get('text', {'rb': -30, 'v': 150, 'dil': 5})
    white = ((V > tx['v']) & ((B - R) < tx['white_br'])) if 'white_br' in tx else (V > tx['v'])
    tmask = ((R - B) > tx['rb']) | white
    tmask = ndi.binary_dilation(tmask, iterations=tx['dil']) & tregion
else:
    tmask = tregion
keep = np.zeros((H, W), bool)
for s in C.get('keep', []):
    keep |= shape_mask(s)
if C.get('keep_fg') and os.path.exists(os.path.join(D, 'fgmask.png')):
    fgm = np.asarray(Image.open(os.path.join(D, 'fgmask.png'))) > 100
    keep |= ndi.binary_dilation(fgm, iterations=C['keep_fg'] if isinstance(C['keep_fg'], int) else 2)
if C.get('keep_red'):
    kr = C['keep_red'] if isinstance(C['keep_red'], dict) else {'dil': C['keep_red']}
    red = (R > 140) & (R - B > 70) & (G < 130)
    if 'clip' in kr:
        x0, y0, x1, y1 = kr['clip']; cm = np.zeros((H, W), bool); cm[y0:y1, x0:x1] = True; red &= cm
    keep |= ndi.binary_dilation(red, iterations=kr['dil'])
if 'crowd' in C:
    cw = C['crowd']
    warm = (R - B > 35) | (V > 165)
    wb = warm.copy(); wb[:cw['y0']] = False
    lab, n = ndi.label(wb); touch = set(np.unique(lab[cw['ybot']:, :])) - {0}
    keep |= ndi.binary_dilation(np.isin(lab, list(touch)), iterations=2)
keep_hard = keep.copy()          # 形・前の 絵・ハンコ・馬の むれ（紙ふぶきの のこしは ふくまない：鎖の 輪も 紙ふぶきに 見えて しまう ため）
if C.get('keep_conf', True):
    # 紙ふぶき（あざやかな 色の かけら）で ボードの 外まで はみ出して いる ものは 丸ごと のこす
    hsv = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    sat = (hsv[..., 1] > 120) & (hsv[..., 2] > 170)          # 明るい あざやかな 色（紺の 線は 入れない）
    lab, n = ndi.label(sat)
    outside = ndi.binary_dilation(~(region | tregion), iterations=2)      # 字だけ 消す 所も「中」
    hit = set(np.unique(lab[outside & sat])) - {0}
    big = ndi.sum(sat, lab, range(1, n + 1))
    keepc = np.isin(lab, [k for k in hit if 60 < big[k - 1] < 8000])
    keep |= ndi.binary_dilation(keepc, iterations=3)
force = np.zeros((H, W), bool)
for s2 in C.get('force', []):
    force |= shape_mask(s2)
remove = (region & ~keep) | (region & force) | (tmask & ~keep)
keep &= ~force
# 地の 色（字・線・チップ・行の 帯を のぞいた 紺）から なめらかな 板の 色
pr = C.get('pill', {'g': 37, 'br': 38})
txt = ndi.binary_dilation((V > 100) | (R - B > 20), iterations=5)
pill = ndi.binary_dilation((G >= pr['g']) & (B - R >= pr['br']), iterations=4)
bg = ndi.binary_erosion((region | tregion) & ~keep & ~txt & ~pill & ~tmask, iterations=1)
def smooth_from(w, s1=18, s2=60):
    # 地の 点（w）から なめらかな 色。近くに 地の 点が ない 所は 地の 点 ぜんぶの 平均の 色（黒く ならない ように）
    f = np.zeros_like(src)
    tot = max(float(w.sum()), 1.0)
    for c in range(3):
        n1 = cv2.GaussianBlur(src[..., c] * w, (0, 0), s1); d1 = cv2.GaussianBlur(w, (0, 0), s1)
        n2 = cv2.GaussianBlur(src[..., c] * w, (0, 0), s2); d2 = cv2.GaussianBlur(w, (0, 0), s2)
        f1 = n1 / np.maximum(d1, 1e-6); f2 = n2 / np.maximum(d2, 1e-6)
        a = np.clip(d1 / 0.25, 0, 1)
        b = np.clip(d2 / 0.05, 0, 1)
        fb = float((src[..., c] * w).sum()) / tot
        f[..., c] = (f1 * a + f2 * (1 - a)) * b + fb * (1 - b)
    return f
if any('bg' in r for r in C['regions']):
    # 所ごとに：その 所の 地（きまり bg：vmax・br）だけから 色を 作る（明るい 地と 暗い 地を まぜない）
    fill = np.zeros_like(src)
    for r in C['regions']:
        rm = shape_mask(r); rule = r.get('bg', {})
        sel = rm & ~keep & ~ndi.binary_dilation(tmask, iterations=2)
        if rule.get('all'):
            # 地も 行も 光（トロフィーの 光 など）も ぜんぶ 使って なめらかに（行の ふちは ぼけて 消え、光の むらは のこる）。
            #   字と チップの 所（exclude の 四角）だけ 使わない
            for ex in rule.get('exclude', []):
                ex0, ey0, ex1, ey1 = ex; sel[ey0:ey1, ex0:ex1] = False
        else:
            if 'vmax' in rule: sel &= V <= rule['vmax']
            if 'gmax' in rule: sel &= G <= rule['gmax']
            if 'br' in rule: sel &= (B - R) >= rule['br']
            if rule.get('nopill'): sel &= ~pill
            if r.get('only') != 'text': sel &= ~txt
        sel = ndi.binary_erosion(sel, iterations=1)
        if sel.sum() < 400:
            # 地の 点が すくない（小さな 所）：まわり 30px まで 広げて とる
            big = ndi.binary_dilation(rm, iterations=30) & ~keep & ~ndi.binary_dilation(tmask, iterations=2) & ~txt
            if 'vmax' in rule: big &= V <= rule['vmax']
            if 'br' in rule: big &= (B - R) >= rule['br']
            sel = ndi.binary_erosion(big, iterations=1)
        if rule.get('poly'):
            # なめらかな 地（見出しの 所 など）：まわり（grow px まで）の 地の 点に 2次の 面を あてはめて うめる（光の むらも なめらかに つづく）
            grow = rule.get('grow', 40)
            area = ndi.binary_dilation(rm, iterations=grow)
            smp = area & ~keep & ~ndi.binary_dilation(tmask, iterations=3) & ~((R - B) > rule.get('rb_ex', 18)) & ~(V > rule.get('v_ex', 90))
            ys_, xs_ = np.nonzero(smp)
            if len(xs_) > 20000:
                pick = np.random.default_rng(5).choice(len(xs_), 20000, replace=False); ys_, xs_ = ys_[pick], xs_[pick]
            nx = lambda x: (x - W / 2) / (W / 2); ny = lambda y: (y - H / 2) / (H / 2)
            def feats(x, y):
                x, y = nx(np.asarray(x, np.float64)), ny(np.asarray(y, np.float64))
                cols = [np.ones_like(x), x, y, x * x, x * y, y * y]
                if rule['poly'] >= 3: cols += [x ** 3, x * x * y, x * y * y, y ** 3]
                return np.stack(cols, -1)
            A = feats(xs_, ys_)
            near_ = ndi.binary_dilation(rm, iterations=8)
            yy_, xx_ = np.nonzero(near_)
            F_ = feats(xx_, yy_)
            f = src.copy()
            for c in range(3):
                coef, *_ = np.linalg.lstsq(A, src[ys_, xs_, c].astype(np.float64), rcond=None)
                f[yy_, xx_, c] = (F_ @ coef).astype(np.float32)
            fill[near_] = f[near_]
            continue
        if rule.get('rows') and 'rect' in r:
            # 行ごとに 左と 右の となりの 地の 色を つなぐ（上下の 明るさの ちがいを その まま のこす）
            x0, y0, x1, y1 = r['rect']; bw = rule['rows']
            okn = ~keep & ~ndi.binary_dilation(tmask, iterations=2) & ~txt
            f = smooth_from(sel.astype(np.float32), rule.get('s1', 18), rule.get('s2', 60))
            for y in range(max(0, y0 - 8), min(H, y1 + 8)):
                Lm = okn[y, max(0, x0 - bw):x0]; Rm = okn[y, x1:min(W, x1 + bw)]
                if Lm.sum() < 3 or Rm.sum() < 3:
                    continue
                lc = np.median(src[y, max(0, x0 - bw):x0][Lm], 0); rc = np.median(src[y, x1:min(W, x1 + bw)][Rm], 0)
                t = np.linspace(0, 1, x1 - x0)[:, None]
                f[y, x0:x1] = lc * (1 - t) + rc * t
            f[max(0, y0 - 8):y1 + 8, x0:x1] = cv2.GaussianBlur(f[max(0, y0 - 8):y1 + 8, x0:x1], (0, 0), rule.get('vblur', 4))
        else:
            f = smooth_from(sel.astype(np.float32), rule.get('s1', 18), rule.get('s2', 60))
        near = ndi.binary_dilation(rm, iterations=8)
        fill[near] = f[near]
else:
    fill = smooth_from(bg.astype(np.float32))
rng = np.random.default_rng(3)
noise = cv2.GaussianBlur(rng.normal(0, 1.6, (H, W)).astype(np.float32), (0, 0), 0.7)
fill += noise[..., None] * np.array([0.6, 0.8, 1.2], np.float32)
soft = cv2.GaussianBlur(remove.astype(np.float32), (0, 0), 2.0)
ts = C.get('text', {}).get('soft')
if ts and tregion.any():
    # 字だけ 消す 所：さかいめを 大きく ぼかす（光の あとの 段が 見えない ように）
    tpart = (tmask & ~keep).astype(np.float32)
    soft = np.maximum(soft, cv2.GaussianBlur(tpart, (0, 0), ts) * np.clip(cv2.GaussianBlur(tregion.astype(np.float32), (0, 0), ts), 0, 1))
soft = soft * (~keep)
# 光（トロフィーの 光 など）が ボードに かかって いる 所は、あたたかい 色ほど もとの 絵を のこす（境目が 出ない ように なめらかに）
#   keep_soft = [{ box:[x0,y0,x1,y1], rb:[lo,hi]（R−B が lo → hi で のこす 割合 0 → 1）, sigma:3, xramp:[x0,x1]（x0 より 左は のこさない → x1 で ぜんぶ）}]
for ks in C.get('keep_soft', []):
    bx0, by0, bx1, by1 = ks['box']
    lo, hi = ks.get('rb', [-30, 40])
    wv = np.clip(((R - B) - lo) / max(hi - lo, 1), 0, 1)
    if 'v' in ks:
        # とても 明るい 所（光の しん：白に 近い）も のこす
        v0, v1 = ks['v']
        wv = np.maximum(wv, np.clip((V - v0) / max(v1 - v0, 1), 0, 1))
    bm = np.zeros((H, W), np.float32); bm[by0:by1, bx0:bx1] = 1
    bm = cv2.GaussianBlur(bm, (0, 0), ks.get('edge', 6))
    if 'xramp' in ks:
        xa, xb = ks['xramp']
        bm *= np.clip((np.arange(W, dtype=np.float32) - xa) / max(xb - xa, 1), 0, 1)[None, :]
    wv = cv2.GaussianBlur(wv.astype(np.float32), (0, 0), ks.get('sigma', 3)) * bm
    for ex in ks.get('exclude', []):
        em = np.zeros((H, W), np.float32); ex0, ey0, ex1, ey1 = ex; em[ey0:ey1, ex0:ex1] = 1
        wv = wv * (1 - cv2.GaussianBlur(em, (0, 0), ks.get('edge', 6)))
    if 'vmed' in ks:
        # のこす 所の 細い 横線（行の ふち など）は 縦の メディアンで 消す（光の むらは なめらかなので のこる）。y1 より 上だけ
        k_, y1_ = ks['vmed']
        sub = src[by0:min(by1, y1_), bx0:bx1]
        src[by0:min(by1, y1_), bx0:bx1] = ndi.median_filter(sub, size=(k_, 1, 1))
    if ks.get('no_white', True):
        # 白っぽい 字（光と ちがって 色が うすい）は のこさない
        wh = (V > 110) & ((src.max(-1) - src.min(-1)) < 70) & (B >= R - 5)     # 青みの ある 白（字）だけ：光（あたたかい 白）は ふくめない
        wh = cv2.GaussianBlur(ndi.binary_dilation(wh, iterations=3).astype(np.float32), (0, 0), 2)
        wv = wv * (1 - wh)
    soft = soft * (1 - wv)
out = np.clip(src * (1 - soft[..., None]) + fill * soft[..., None], 0, 255).astype(np.uint8)
# 鎖 など ボードの 中の 横に 長い 飾りを 消す（vfill）：帯の 中を、すぐ 上の 行と すぐ 下の 行の 色の あいだを 縦に つないで うめる
#   （上は 見出しの 箱の 下・下は 行の 箱の 上。前の 絵（keep の 形・keep_fg・keep_red）は 消さない・紙ふぶきの のこしは 見ない）。
#   vfill = [{ rect:[x0,y0,x1,y1], hmed:9 }] または ななめの 帯 { line:[[xa,ya],[xb,yb]]（鎖の まん中の 線）, half:10（帯の はばの 半分）, hmed:9 }
#   protect:[{ box:[x0,y0,x1,y1], seed:[x,y], tol:45 }]：帯に かかる 紙ふぶき・葉っぱ（seed の 色に 近く つながった 所）は のこす
#           または { poly:[[x,y],…], color:[r,g,b], tol:60 }（なぞった 形の 中の その 色の 所）
def _vf_strip(img, top, bot, hmed):
    """img[0]：上の はし、img[-1]：下の はし。あいだの 行を 縦に つなぐ（横に hmed の med で はしの 色の むらを ならす）"""
    if hmed > 1:
        top = ndi.median_filter(top, size=(hmed, 1)); bot = ndi.median_filter(bot, size=(hmed, 1))
    n = img.shape[0]
    t = np.linspace(0, 1, n + 2)[1:-1][:, None, None]
    fv = top[None] * (1 - t) + bot[None] * t
    fv += cv2.GaussianBlur(np.random.default_rng(7).normal(0, 1.2, fv.shape[:2]).astype(np.float32), (0, 0), 0.7)[..., None]
    return fv
for vf in C.get('vfill', []):
    o = out.astype(np.float32)
    prot = np.zeros((H, W), bool)
    for pr in vf.get('protect', []):
        if 'poly' in pr:
            # 手で なぞった 形（色 color が あれば その 色に 近い 所だけ：同じ 形の 中の 鎖の 輪は のこさない）
            mm = shape_mask({'poly': pr['poly']})
            if 'color' in pr:
                mm &= np.linalg.norm(orig_src - np.array(pr['color'], np.float32), axis=-1) < pr.get('tol', 60)
            dl = int(pr.get('dil', 1))
            prot |= (ndi.binary_dilation(mm, iterations=dl) if dl > 0 else mm) & shape_mask({'poly': pr['poly']})
            continue
        bx0, by0, bx1, by1 = pr['box']; sx, sy = pr['seed']
        sub = orig_src[by0:by1, bx0:bx1]
        c0 = np.median(orig_src[sy - 2:sy + 3, sx - 2:sx + 3].reshape(-1, 3), 0)
        near = np.linalg.norm(sub - c0, axis=-1) < pr.get('tol', 45)
        lab_, _ = ndi.label(near)
        li = lab_[sy - by0, sx - bx0]
        if li:
            mm = ndi.binary_dilation(lab_ == li, iterations=pr.get('dil', 1))
            prot[by0:by1, bx0:bx1] |= mm
    if 'line' in vf:
        (xa, ya), (xb, yb) = vf['line']; hf = float(vf.get('half', 10))
        L_ = float(np.hypot(xb - xa, yb - ya)); ux, uy = (xb - xa) / L_, (yb - ya) / L_; nx, ny = -uy, ux
        if ny < 0: nx, ny = -nx, -ny                      # 法線は 下 むき
        ns = int(np.ceil(L_)) + 1; nt = int(np.ceil(2 * hf)) + 7
        ss = np.arange(ns, dtype=np.float32); tt = np.linspace(-hf - 3, hf + 3, nt).astype(np.float32)
        S_, T_ = np.meshgrid(ss, tt)
        mx = (xa + S_ * ux + T_ * nx).astype(np.float32); my = (ya + S_ * uy + T_ * ny).astype(np.float32)
        st = cv2.remap(o, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)     # 帯を まっすぐに した もの（nt × ns）
        inner = np.abs(tt) <= hf
        i0 = np.nonzero(inner)[0][0]; i1 = np.nonzero(inner)[0][-1]
        top = st[max(0, i0 - 3):i0].mean(0); bot = st[i1 + 1:i1 + 4].mean(0)
        st2 = st.copy(); st2[i0:i1 + 1] = _vf_strip(st[i0:i1 + 1], top, bot, int(vf.get('hmed', 9)))
        x0 = int(max(0, np.floor(min(xa, xb) - hf - 4))); x1 = int(min(W, np.ceil(max(xa, xb) + hf + 4)))
        y0 = int(max(0, np.floor(min(ya, yb) - hf - 4))); y1 = int(min(H, np.ceil(max(ya, yb) + hf + 4)))
        yy_, xx_ = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        sp = (xx_ - xa) * ux + (yy_ - ya) * uy; tp = (xx_ - xa) * nx + (yy_ - ya) * ny
        inb = (np.abs(tp) <= hf) & (sp >= 0) & (sp <= L_)
        ti = ((tp + hf + 3) / (2 * hf + 6) * (nt - 1)).astype(np.float32)
        fill = cv2.remap(st2, sp.astype(np.float32), ti, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        sel = inb & ~keep_hard[y0:y1, x0:x1] & ~prot[y0:y1, x0:x1]
        o[y0:y1, x0:x1][sel] = fill[sel]
    else:
        x0, y0, x1, y1 = vf['rect']
        top = np.median(o[max(0, y0 - 3):y0, x0:x1], axis=0)
        bot = np.median(o[y1:min(H, y1 + 3), x0:x1], axis=0)
        # 上・下の 行が のこす 物（紙ふぶき・馬）に かかる 列は、となりの 列の 色で（のこす 物の 色が 帯に のびない ように）
        hold = keep_hard | prot
        for edge_, rows_ in ((top, slice(max(0, y0 - 3), y0)), (bot, slice(y1, min(H, y1 + 3)))):
            bad = hold[rows_, x0:x1].any(0)
            if bad.any() and (~bad).sum() > 2:
                xs_ = np.arange(x1 - x0); ok_ = ~bad
                for c in range(3):
                    edge_[bad, c] = np.interp(xs_[bad], xs_[ok_], edge_[ok_, c])
        fv = _vf_strip(o[y0:y1, x0:x1], top, bot, int(vf.get('hmed', 9)))
        kp = (keep_hard[y0:y1, x0:x1] | prot[y0:y1, x0:x1])[..., None]
        o[y0:y1, x0:x1] = np.where(kp, o[y0:y1, x0:x1], fv)
    out = np.clip(o, 0, 255).astype(np.uint8)
# 字・ボタン・ハンコ・月桂樹 など を うめる（inpaint）：形ごとに mode（なし＝Telea・rows・radial・diffuse）を えらべる
#   diffuse：まわりの 色を 大きい ぼかしから 小さい ぼかしへ かさねて うめる（光の むらの ある 見出しの 大きな ハンコ・月桂樹 など）
#     C['diffuse'] = { vmax:70（これより 明るい 所は 色の もとに しない）, within:{rrect:…}（この 形の 中だけ もとに する）}
def _inpaint(out, m, mode_):
    im8 = np.ascontiguousarray(out)
    if mode_ == 'diffuse':
        dcf = C.get('diffuse', {})
        img = im8.astype(np.float32); w = ~ndi.binary_dilation(m, iterations=int(dcf.get('gap', 2)))   # gap：穴の まわりの にじみは 色の もとに しない
        if 'vmax' in dcf: w &= img.max(-1) <= dcf['vmax']                 # 光る ふち・光の むらは 色の もとに しない
        if 'within' in dcf: w &= shape_mask(dcf['within'])               # ボードの 中だけ
        w = w.astype(np.float32)
        acc = None
        for sg in (64, 32, 16, 8, 4, 2):
            num = cv2.GaussianBlur(img * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
            f = num / np.maximum(den, 1e-6)[..., None]
            conf = np.clip(den / 0.35, 0, 1)[..., None]
            acc = f if acc is None else acc * (1 - conf) + f * conf
        acc += cv2.GaussianBlur(np.random.default_rng(11).normal(0, 1.1, (H, W)).astype(np.float32), (0, 0), 0.8)[..., None]
        wm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[..., None]
        wm = np.where(m[..., None], 1.0, wm)
        return np.clip(out * (1 - wm) + acc * wm, 0, 255).astype(np.uint8)
    if mode_ == 'radial':
        filled = im8.astype(np.float32).copy()
        icx, icy = C['inpaint_c']
        ys, xs = np.nonzero(m)
        dx, dy = xs - icx, ys - icy; L = np.maximum(np.hypot(dx, dy), 1e-3); ux, uy = dx / L, dy / L
        def first_out(sign):
            # まん中から 見て 内（-1）・外（+1）へ すすんで、絵の ボタンの 外に 出る 所
            d = np.zeros(len(xs), np.float32); done = np.zeros(len(xs), bool)
            for step in range(1, 400):
                px_ = np.clip(np.round(xs + sign * ux * step).astype(int), 0, W - 1); py_ = np.clip(np.round(ys + sign * uy * step).astype(int), 0, H - 1)
                out = ~m[py_, px_] & ~done
                d[out] = step; done |= out
                if done.all(): break
            return d
        di, do = first_out(-1), first_out(+1)
        def at(sign, d):
            px_ = np.clip(np.round(xs + sign * ux * (d + 2)).astype(int), 0, W - 1); py_ = np.clip(np.round(ys + sign * uy * (d + 2)).astype(int), 0, H - 1)
            return im8[py_, px_].astype(np.float32)
        ci, co = at(-1, di), at(+1, do)
        t = (di / np.maximum(di + do, 1e-3))[:, None]
        filled[ys, xs] = ci * (1 - t) + co * t
        filled = cv2.GaussianBlur(filled, (0, 0), 1.5)
    elif mode_ == 'rows':
        filled = im8.astype(np.float32).copy()
        ys, xs = np.nonzero(m)
        for y in range(ys.min(), ys.max() + 1):
            row = np.nonzero(m[y])[0]
            if not len(row): continue
            # 同じ 行に はなれた 形が ある とき（左右の 星 など）は 形ごとに
            for run in np.split(row, np.nonzero(np.diff(row) > 1)[0] + 1):
                x0, x1 = run.min(), run.max()
                a0 = im8[y, max(0, x0 - 6):max(1, x0 - 1)].astype(np.float32).mean(0); a1 = im8[y, min(W - 1, x1 + 2):min(W, x1 + 7)].astype(np.float32).mean(0)
                t = np.linspace(0, 1, x1 - x0 + 1)[:, None]
                filled[y, x0:x1 + 1] = a0 * (1 - t) + a1 * t
        filled = cv2.GaussianBlur(filled, (0, 0), 2.0)
    else:
        bgr = cv2.cvtColor(im8, cv2.COLOR_RGB2BGR)
        bgr = cv2.inpaint(bgr, m.astype(np.uint8) * 255, C.get('inpaint_r', 12), cv2.INPAINT_TELEA)
        filled = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    if mode_ not in ('rows', 'radial'):
        filled = cv2.GaussianBlur(filled, (0, 0), 3.0)
    wm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3.0)[..., None]
    return np.clip(out * (1 - wm) + filled * wm, 0, 255).astype(np.uint8)
if C.get('inpaint'):
    groups = {}
    for s3 in C['inpaint']:
        groups.setdefault(s3.get('mode', C.get('inpaint_mode')), []).append(s3)
    for mode_, shapes in groups.items():
        m = np.zeros((H, W), bool)
        for s3 in shapes:
            ms = shape_mask(s3)
            if s3.get('not_fg') and os.path.exists(os.path.join(D, 'fgmask.png')):
                # 前の 絵（布・馬）の 所は うめない（ボードの 見えて いる 所だけ）
                ms &= ~ndi.binary_dilation(np.asarray(Image.open(os.path.join(D, 'fgmask.png'))) > 60, iterations=2)
            m |= ms
        out = _inpaint(out, m, mode_)
Image.fromarray(out).save(os.path.join(D, 'clean.png'))
dbg = src.copy(); dbg[remove] = dbg[remove] * 0.4 + np.array([255, 0, 0]) * 0.6; dbg[keep & region] = dbg[keep & region] * 0.4 + np.array([0, 255, 0]) * 0.6
Image.fromarray(np.clip(dbg, 0, 255).astype(np.uint8)).save(os.path.join(D, 'clean_dbg.png'))
print('clean', D, int(remove.sum()))
