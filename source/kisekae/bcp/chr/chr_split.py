# キャラだけ 動かす（実験）：絵から キャラを 切りぬいて（うしろは 光の すじで 描きたす）、キャラごとの すき通しの 絵に する
#   python3 chr_split.py <cfg.json>   → <out>/bgx.png（キャラなしの 背景）・<out>/<id>.png（キャラの RGBA）・<out>/dbg_*.png
#   切りぬき：isnet-anime の マスク（seg.py）＋ 印（キャラの 中・背景）から watershed（キャラ どうしの さかいは 絵の ふち線で 分ける）
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
from skimage.segmentation import watershed
from skimage.filters import sobel
C = json.load(open(sys.argv[1], encoding='utf8')); OUT = C['out']; os.makedirs(OUT, exist_ok=True)
img = np.asarray(Image.open(C['clean']).convert('RGB')).astype(np.float32); H, W = img.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def poly(p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.round(np.array(p, np.float64) * 8).astype(np.int32)], 1, shift=3); return m.astype(bool)
def ell(c, rx, ry): return ((xx - c[0]) / rx) ** 2 + ((yy - c[1]) / ry) ** 2 <= 1
def shape(s):
    if 'poly' in s: return poly(s['poly'])
    if 'ell' in s: return ell(s['ell'][0], s['ell'][1], s['ell'][2])
    if 'rect' in s: x0, y0, x1, y1 = s['rect']; m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True; return m
    if 'mask' in s:          # 絵の マスク（白い 所）：{mask: png の パス}（大きさが ちがう ときは 左上を あわせて 切る・たす）
        mm = np.asarray(Image.open(s['mask']).convert('L')) > 127; out_ = np.zeros((H, W), bool)
        h_, w_ = min(H, mm.shape[0]), min(W, mm.shape[1]); out_[:h_, :w_] = mm[:h_, :w_]; return out_
    if 'line' in s:          # 太さの ある 線（しっぽ・足・耳の 先に そって 印を おく）：{line: [[x,y],…], r: 半はば}
        m = np.zeros((H, W), np.uint8); pts = np.round(np.array(s['line'], np.float64)).astype(np.int32)
        cv2.polylines(m, [pts], False, 1, thickness=max(1, int(round(s.get('r', 3) * 2))), lineType=cv2.LINE_8); return m.astype(bool)
    raise ValueError(s)
def shapes(lst):
    m = np.zeros((H, W), bool)
    for s in lst: m |= shape(s)
    return m
# 1) マスク（isnet-anime の 切りぬき：いくつかの 四角で 出した ものの 大きい ほう）
M = np.zeros((H, W), np.float32)
for f in C['masks']:
    M = np.maximum(M, np.asarray(Image.open(f).convert('L')).astype(np.float32) / 255)
# 2) 印
parts = C['parts']; lab0 = np.zeros((H, W), np.int32)
outer = {}
for i, p in enumerate(parts):
    outer[p['id']] = shapes(p.get('outer', [])) if p.get('outer') else None
out_all = np.zeros((H, W), bool)
for v in outer.values():
    if v is not None: out_all |= v
if C.get('bg_add_strict', True):        # bg_add は いつも 背景（outer の 中でも：キャラの 前の 本・紙 など）
    bgm = ((M < C.get('bg_thr', 0.12)) & ~ndi.binary_dilation(out_all, iterations=6)) | shapes(C.get('bg_add', []))
else:                                   # 前の やり方（スタンプ）：outer の 中は bg_add も 背景に しない
    bgm = (((M < C.get('bg_thr', 0.12)) & ~ndi.binary_dilation(out_all, iterations=6)) | shapes(C.get('bg_add', []))) & ~ndi.binary_dilation(out_all, iterations=2)
cores, ccen = {}, {}
for i, p in enumerate(parts):
    for cb in p.get('core', []):
        x0, y0, x1, y1 = cb; sx, sy = (x1 - x0) * C.get('core_shrink', 0.22), (y1 - y0) * C.get('core_shrink', 0.22)
        m_ = np.zeros((H, W), bool); m_[int(y0 + sy):int(y1 - sy), int(x0 + sx):int(x1 - sx)] = True
        cores.setdefault(p['id'], np.zeros((H, W), bool)); cores[p['id']] |= m_
        # 四角の まん中の だ円は モデルが 弱くても 印に（四角は キャラの 顔・体の まん中に おく）
        cr = C.get('core_center', 0.28)
        e_ = ell(((x0 + x1) / 2, (y0 + y1) / 2), max(2, (x1 - x0) * cr), max(2, (y1 - y0) * cr))
        ccen.setdefault(p['id'], np.zeros((H, W), bool)); ccen[p['id']] |= e_
for i, p in enumerate(parts):
    mk = shapes(p.get('inner', []))
    if p['id'] in cores:
        oth = np.zeros((H, W), bool)
        for k_, v_ in cores.items():
            if k_ != p['id']: oth |= v_
        mk |= (cores[p['id']] & (M > C.get('core_thr', 0.8)) | ccen[p['id']]) & ~oth
    if 'from_mask' in p:
        fm = p['from_mask']; x0, y0, x1, y1 = fm['box']; bx = np.zeros((H, W), bool); bx[y0:y1, x0:x1] = True
        mm = (M > fm.get('thr', 0.85)) & bx
        for oid in fm.get('minus', []):
            mm &= ~ndi.binary_dilation(outer[oid], iterations=fm.get('dil', 16))
        mm &= ~shapes(fm.get('minus_shapes', []))
        mk |= ndi.binary_erosion(mm, iterations=fm.get('erode', 2))
    if 'color_seed' in p:                       # 色で きめる 印（布：白っぽい 所の まん中・within の 中だけ）
        cs_ = p['color_seed']; mn_, mx_ = img.min(-1), img.max(-1)
        cm_ = (mn_ > cs_.get('min', 175)) & ((mx_ - mn_) < cs_.get('chroma', 55)) & shapes(cs_['within'])
        mk |= ndi.binary_erosion(cm_, iterations=cs_.get('erode', 4))
    mk &= ~shapes(C.get('bg_add', []))          # 印は モデルの マスクより つよい（モデルが キャラを 見のがす 絵：はしの 小さい キャラ など）
    lab0[mk & (lab0 == 0)] = i + 1
if out_all.any() and all(p.get('outer') for p in parts):
    bgm |= ~ndi.binary_dilation(out_all, iterations=4)                    # キャラ ぜんぶに outer が ある とき：outer の 外は 背景
    notrust = np.zeros((H, W), bool)                                      # モデルが 弱い キャラ（trust_mask: false）の outer の 中は 線だけで 分ける
    for p in parts:
        if p.get('trust_mask') is False: notrust |= outer[p['id']]
    bgm |= (M < C.get('bg_thr_in', 0.04)) & ~notrust                      # outer の 中でも モデルが はっきり 背景と 見る 所は 背景
# 色で えらぶ 背景（ボードの ふちの 光の 線 など）：within の 中の 明るくて 色の うすい 所（キャラの 印の 近くは のぞく）
PICK = np.zeros((H, W), bool)
for bp in C.get('bg_pick', []):
    mx_, mn_ = img.max(-1), img.min(-1); sat_ = (mx_ - mn_) / np.maximum(mx_, 1)
    pk = shapes(bp['within']) & (mx_ >= bp.get('vmin', 215)) & (mx_ <= bp.get('vmax', 256)) & (sat_ <= bp.get('smax', 0.55)) & (sat_ >= bp.get('smin', 0))
    if 'b_minus_r' in bp: pk &= (img[..., 2] - img[..., 0]) >= bp['b_minus_r']     # 青い 物（あせの しずく など）
    if bp.get('erode'): pk = ndi.binary_erosion(pk, iterations=bp['erode'])
    bgm |= pk; PICK |= pk
bgm &= ~(ndi.binary_dilation(lab0 > 0, iterations=C.get('mark_gap', 8)) & ~shapes(C.get('bg_add', [])))
if 'bg_color' in C:                     # 色で きめる 背景（布・雲・紙 など 白っぽい 物）：キャラの core の 四角の 中は のぞく
    bc = C['bg_color']; mn_, mx_ = img.min(-1), img.max(-1)
    cm = (mn_ > bc.get('min', 175)) & ((mx_ - mn_) < bc.get('chroma', 55))
    cb_all = np.zeros((H, W), bool)
    for p in parts:
        for cb in p.get('core', []):
            x0, y0, x1, y1 = cb; cb_all[max(0, y0):y1, max(0, x0):x1] = True
    CM_FULL = cm.copy()
    cm = ndi.binary_erosion(cm, iterations=bc.get('erode', 6))          # 白い 所の まん中 だけ（キャラの ふちの 近くは 線で 分ける：ひづめ・腕の 先が 布に のこらない）
    cm &= ~ndi.binary_dilation(cb_all, iterations=bc.get('gap', 4))
    lab0[cm & (lab0 == 0)] = len(parts) + 1
else:
    CM_FULL = np.zeros((H, W), bool)
lab0[bgm & (lab0 == 0)] = len(parts) + 1
# 3) watershed（絵の ふち線で 分ける）
g = np.max(np.stack([sobel(cv2.GaussianBlur(img[..., c] / 255, (0, 0), 0.8)) for c in range(3)]), 0)
lab = watershed(g, lab0)
# まいご（モデルは キャラと 見て いるのに 背景に なった 所：しっぽ・耳の 先・毛の たば）は いちばん 近い キャラへ（orphan_dist px まで）
OT, OD = C.get('orphan_thr', 0.5), C.get('orphan_dist', 40)
if OD:
    bgl = len(parts) + 1
    orph = (M > OT) & (lab == bgl) & ~shapes(C.get('bg_add', []))
    if out_all.any() and all(p.get('outer') for p in parts): orph &= out_all
    orph &= ~CM_FULL                    # 白い 布・雲は まいごに しない（キャラと いっしょに 動かない）
    orph &= ~ndi.binary_dilation(PICK, iterations=4)   # 色で えらんだ 背景（あせの しずく・ボードの ふち）と その ふちも まいごに しない
    orph &= ~shapes(C.get('no_orphan', []))            # まいごに しない 所（ボードの ふちの 帯 など：モデルが キャラと 見ても 背景）
    if orph.any():
        charm = (lab >= 1) & (lab <= len(parts))
        dist, (iy, ix) = ndi.distance_transform_edt(~charm, return_indices=True)
        sel = orph & (dist <= OD)
        lab[sel] = lab[iy, ix][sel]
        print('orphan px', int(orph.sum()), 'given', int(sel.sum()))
# 4) すき通し（外の ふちは マスクの やわらかさ・キャラ どうしの さかいは 1px ぼかし）
soft = np.clip((M - 0.04) / 0.86, 0, 1)
res = {}
for i, p in enumerate(parts):
    hard = lab == i + 1
    if 'clip' in p:          # この 線より 下は 切る（ボードの うしろに かくれて いる 所）・keep の 形は のこす（ボードの 前の ひづめ など）
        cy = p['clip']['y']; keep = shapes(p['clip'].get('keep', []))
        hard &= (yy < cy) | keep
    hard = ndi.binary_opening(hard, iterations=1)
    fh = p.get('fill_holes', 3000)                 # 中の 小さな 穴（体の 色が 背景と にて いる 所）は うめる
    if fh:
        holes_ = ndi.binary_fill_holes(hard) & ~hard
        lh_, nh_ = ndi.label(holes_)
        if nh_:
            szh = ndi.sum(holes_, lh_, range(1, nh_ + 1))
            others_ = np.zeros((H, W), bool)
            for q in parts:
                if q['id'] != p['id']: others_ |= (lab == parts.index(q) + 1)
            hard |= np.isin(lh_, [k + 1 for k in range(nh_) if szh[k] <= fh]) & ~others_
    l_, n_ = ndi.label(hard)
    if n_ > 1:
        sz = ndi.sum(hard, l_, range(1, n_ + 1)); hard = np.isin(l_, [k + 1 for k in range(n_) if sz[k] >= p.get('min_part', 400)])
    res[p['id']] = hard
# 動かさない 所（still：キャラの うしろを 通る リボン・ボードの 帯 など）：ふちの のばし・光の ふち（halo）でも キャラに 入れない
STILL = shapes(C.get('still', []))
# ふち線も キャラに（watershed の さかいが ふち線の 内がわに なる ことが ある）・まわりの 光の ふち（halo）も キャラと いっしょに 動かす
HALO, PY = C.get('halo', 5), C['fill'].get('plate_y', H)
hards = {}
for i, p in enumerate(parts):
    hard = res[p['id']]
    others = np.zeros((H, W), bool)
    for q in parts:
        if q['id'] != p['id']: others |= res[q['id']]
    grow = ndi.binary_dilation(hard, iterations=3) & (M > 0.5) & ~others & ~STILL & ~shapes(C.get('no_orphan', []))
    if 'clip' in p: grow &= (yy < p['clip']['y']) | shapes(p['clip'].get('keep', []))
    hards[p['id']] = hard | grow
# 見えて いる ボード（板の 中で 元の 前の 絵に 入って いない 所：アプリの 字・行が 出る 所）は キャラに 入れない（止まって いる とき アプリの 字を かくさない）
VIS = np.zeros((H, W), bool)
if C.get('board'):
    bq = C['board']; qm_ = poly(bq['quad'])
    fm_ = np.asarray(Image.open(bq['fgmask']).convert('L')) > 127 if bq.get('fgmask') and os.path.exists(bq['fgmask']) else np.zeros((H, W), bool)
    VIS = ndi.binary_erosion(qm_, iterations=C.get('vis_erode', 2)) & ~fm_
    VIS &= ~shapes(C.get('vis_keep', []))      # 板の ふちに かかる キャラの 光の ふち（旗の 玉 など）は キャラに 入れて よい（動いた とき 光の 線が のこらない）
    for k in hards: hards[k] &= ~VIS
res = {k: (v, None) for k, v in hards.items()}
# 5) うしろ（キャラなし）：光の すじ（まん中 c から 見た 角度ごとの 色）＋ まわりとの ちがいを なめらかに。ボードの 中（plate_y より 下）は inpaint
#    1回目：キャラの まわり GZ px まで 消して うめる → 元の 絵と うめた 色が ちがう 所（光の ふち・ふち線・きらきら）は キャラと いっしょに 動かす（halo）
#    2回目：うしろは 元の 絵の まま、キャラ＋halo の 所 だけ 1回目の うめた 色に（止まって いる ときは 元の 絵と 同じ）
F = C['fill']; cx, cy = F.get('c', [W / 2, H / 2]); GZ = F.get('glow_px', 12); GT = F.get('glow_thr', 22)
def make_fill(hole, vmax=None):
    if F.get('mode') == 'smooth':
        ring_ = ndi.binary_dilation(hole, iterations=F.get('ring', 10)) & ~ndi.binary_dilation(hole, iterations=1)
        acc = diffuse(img, ring_.astype(np.float32), hole)
        acc += cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1.2, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
        return np.where(hole[..., None], acc, img)
    if F.get('mode') == 'inpaint':
        # まわりの 色で うめる（Telea）→ 穴の おくは 少し ぼかす（すじに ならない）。見えるのは キャラが 動いた ときの ふちの 数 px だけ
        u8 = np.clip(img, 0, 255).astype(np.uint8)
        out = cv2.inpaint(u8, ndi.binary_dilation(hole, iterations=1).astype(np.uint8), F.get('inpaint_r', 7), cv2.INPAINT_TELEA).astype(np.float32)
        blur = cv2.GaussianBlur(out, (0, 0), 2.0)
        k = np.clip((ndi.distance_transform_edt(hole) - 2) / 6.0, 0, 1)[..., None]
        out = out * (1 - k) + blur * k
        return np.where(hole[..., None], out, img)
    phi = np.degrees(np.arctan2(yy - cy, xx - cx))
    V = img.max(-1)
    VM = F.get('vmax', 250) if vmax is None else vmax
    band = ~ndi.binary_dilation(hole, iterations=4) & (yy < PY) & (V <= VM) & ~shapes(F.get('band_ex', []))
    step = F.get('step', 0.25); ph = phi[band]; cols = img[band]; lo, hi = ph.min(), ph.max(); nb = int(np.ceil((hi - lo) / step)) + 1
    idx = np.clip(((ph - lo) / step).astype(int), 0, nb - 1); prof = np.full((nb, 3), np.nan, np.float32)
    order = np.argsort(idx); idx_s = idx[order]; cols_s = cols[order]; starts = np.searchsorted(idx_s, np.arange(nb)); ends = np.searchsorted(idx_s, np.arange(nb), 'right')
    for b in range(nb):
        if ends[b] - starts[b] >= 3: prof[b] = np.median(cols_s[starts[b]:ends[b]], 0)
    ok = ~np.isnan(prof[:, 0]); xs_ = np.arange(nb)
    for c in range(3): prof[:, c] = np.interp(xs_, xs_[ok], prof[ok, c])
    prof = ndi.gaussian_filter1d(prof, F.get('psmooth', 2.0), axis=0)
    pidx = np.clip((phi - lo) / step, 0, nb - 1)
    P = np.stack([np.interp(pidx.ravel(), xs_, prof[:, c]).reshape(H, W) for c in range(3)], -1)
    ring = ndi.binary_dilation(hole, iterations=F.get('ring', 10)) & ~ndi.binary_dilation(hole, iterations=1) & (V <= VM)
    corr = diffuse(img - P, ring.astype(np.float32), hole)
    fill = P + corr
    fill += cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1.2, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
    out = np.where(hole[..., None], fill, img)
    inb = hole & (yy >= PY)
    if inb.any():
        u8 = np.clip(out, 0, 255).astype(np.uint8)
        out = cv2.inpaint(u8, ndi.binary_dilation(inb, iterations=1).astype(np.uint8), 5, cv2.INPAINT_TELEA).astype(np.float32)
    return out
def diffuse(field, w, m):
    acc = None
    for sg in (64, 32, 16, 8, 4, 2):
        num = cv2.GaussianBlur(field * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
        f = num / np.maximum(den, 1e-6)[..., None]; conf = np.clip(den / 0.3, 0, 1)[..., None]
        acc = f if acc is None else acc * (1 - conf) + f * conf
    return acc
allh = np.zeros((H, W), bool)
for v in hards.values(): allh |= v
NOH = shapes(F.get('no_halo', []))          # 光の ふちを キャラに 入れない 所（ボードの ふち など：キャラが 動いても ボードが ゆれない）
hole1 = (ndi.binary_dilation(allh, iterations=GZ) & (yy < PY)) | ndi.binary_dilation(allh, iterations=F.get('grow_plate', 3))
hole1 &= ~shapes(F.get('keep', []))
fill1 = make_fill(hole1)
dif = np.abs(img - fill1).max(-1)
zones = {}
for i, p in enumerate(parts):
    hard = hards[p['id']]
    others = np.zeros((H, W), bool)
    for q in parts:
        if q['id'] != p['id']: others |= hards[q['id']]
    allow = ~others & (yy < PY) & ndi.binary_dilation(hard, iterations=GZ - 2) & ~NOH & ~VIS & ~STILL
    if 'clip' in p: allow &= (yy < p['clip']['y'])
    g = (dif > GT) & allow
    l_, n_ = ndi.label(g | hard)
    touch = set(np.unique(l_[hard])) - {0}
    # キャラに つながって いない 小さな かけら（毛先の ふち線・きらきら）も キャラと いっしょに（背景に のこると 動いた とき 線が のこる）
    lg, ng = ndi.label(g)
    if ng:
        szg = ndi.sum(g, lg, range(1, ng + 1))
        small = np.isin(lg, [i + 1 for i in range(ng) if szg[i] < F.get('frag_max', 400)])
    else:
        small = np.zeros((H, W), bool)
    z = np.isin(l_, list(touch)) | small | (ndi.binary_dilation(hard, iterations=2) & allow) | hard
    z = ndi.binary_closing(z, iterations=1) & (allow | hard) & ~VIS
    zones[p['id']] = z
res = {}
for i, p in enumerate(parts):
    z = zones[p['id']]
    a = np.maximum(z.astype(np.float32), cv2.GaussianBlur(z.astype(np.float32), (0, 0), 0.8))
    res[p['id']] = (z, np.clip(a, 0, 1))
hole = np.zeros((H, W), bool)
for k, (z, a) in res.items():
    hole |= z                       # キャラ＋halo の 所 だけ（その まわりは 元の 絵：止まって いる ときは 元の 絵と 同じ）
hole &= hole1
# 2回目：うめる 所（キャラ＋halo）の すぐ 外の 元の 絵に 合わせて うめ直す（キャラが 動いた とき、うめた 所と 元の 絵の さかいが 線に 見えない）
fill2 = make_fill(hole, F.get('vmax2', 256)) if F.get('refill', True) else fill1
#    さかいの すぐ 内がわ（edge_px）は 元の 絵へ なめらかに（光の 強い 所でも 線に ならない）
#    （元の 絵が うめた 色と 大きく ちがう 所＝キャラの ふち線 などは 元の 絵を つかわない：動いた とき 線が 背景に のこらない）
din = ndi.distance_transform_edt(hole)
t = np.clip((din - 0.5) / F.get('edge_px', 4.0), 0, 1)
d2 = np.abs(img - fill2).max(-1)
w_o = ((1 - t) * np.clip(1 - (d2 - 12) / 20.0, 0, 1))[..., None]
bgx = np.where(hole[..., None], img * w_o + fill2 * (1 - w_o), img)
Image.fromarray(np.clip(bgx, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'bgx.png'))
# 6) キャラの 絵（RGBA）：色は 元の 絵・ext（ほかの キャラの うしろに かくれた 所）は まわりの 色で のばす
for i, p in enumerate(parts):
    hard, a = res[p['id']]; rgb = img.copy()
    if p.get('ext_under'):
        # ほかの キャラ（上に 重なる もの）の うしろに かくれた 所を、まわりの 色で のばす（動いた とき すき間に うしろが 見えない ように）
        over = np.zeros((H, W), bool)
        for oid in p['ext_under']: over |= res[oid][0]
        ex = over & ndi.binary_dilation(hard, iterations=p.get('ext_px', 20)) & ~hard
        src_w = (hard & ~ndi.binary_dilation(over, iterations=1)).astype(np.float32)
        ext_rgb = diffuse(img, src_w, ex)
        rgb = np.where(ex[..., None], ext_rgb, rgb); a = np.maximum(a, ex.astype(np.float32))
    Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUT, p['id'] + '.png'))
    print(p['id'], 'px', int(hard.sum()), 'alpha>0.5', int((a > 0.5).sum()))
# しらべる 絵
dbg = img.copy()
cols_ = [(255, 80, 80), (80, 255, 120), (80, 160, 255), (255, 220, 60)]
for i, p in enumerate(parts):
    hard, a = res[p['id']]; edge = hard & ~ndi.binary_erosion(hard, iterations=1)
    dbg[edge] = cols_[i % 4]
Image.fromarray(np.clip(dbg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'dbg_edges.png'))
mk = img * 0.45; 
for i in range(len(parts) + 1): mk[lab0 == i + 1] = mk[lab0 == i + 1] * 0.4 + np.array(cols_[i % 4]) * 0.6
Image.fromarray(np.clip(mk, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'dbg_markers.png'))
print('hole px', int(hole.sum()), 'out', OUT)
