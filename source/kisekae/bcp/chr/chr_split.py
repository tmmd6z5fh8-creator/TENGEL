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
    if 'rect' in s: x0, y0, x1, y1 = s['rect']; m = np.zeros((H, W), bool); m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True; return m   # 負の 数は 0 に（-5 は 空に なって いた）
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
# 動かない 前の 絵（static_front：キャラの 前に 描いて あるが キャラと いっしょに 動かない 物＝二人でしょんぼりの 残念の 青い 線 など。まさちゃん 11/05 17:06）
#   絵から その 物を 消して（まわりの 色で うめる）から 切りぬく → キャラは その 下も つづいて いる（動いても すき間が ない）・背景にも その 物は 入らない。
#   その 物は 元の 絵の まま キャラの 上に 動かない 絵として 重ねる（occl.png：物＋ふちの にじみ static_front_pad px は 1・そこから static_front_ring px で 0）
SFA = np.zeros((H, W), np.float32)
if C.get('static_front'):
    SFC = shapes(C['static_front'])
    SFL = ndi.binary_dilation(SFC, iterations=C.get('static_front_pad', 2))
    img = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), SFL.astype(np.uint8), 5, cv2.INPAINT_TELEA).astype(np.float32)
    M = cv2.inpaint(np.clip(M * 255, 0, 255).astype(np.uint8), SFL.astype(np.uint8), 5, cv2.INPAINT_TELEA).astype(np.float32) / 255
    RGf = C.get('static_front_ring', 2)
    SFA = np.clip(1 - ndi.distance_transform_edt(~SFL) / (RGf + 1), 0, 1).astype(np.float32); SFA[SFL] = 1
    print('static front px', int(SFL.sum()))
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
HZ = np.zeros((H, W), bool)             # 毛の 所（hair_zone）
if out_all.any() and all(p.get('outer') for p in parts):
    bgm |= ~ndi.binary_dilation(out_all, iterations=4)                    # キャラ ぜんぶに outer が ある とき：outer の 外は 背景
    notrust = np.zeros((H, W), bool)                                      # モデルが 弱い キャラ（trust_mask: false）の outer の 中は 線だけで 分ける
    HZR = np.zeros((H, W), bool)
    for p in parts:
        if p.get('trust_mask') is False: notrust |= outer[p['id']]
        # 毛の 所（hair_zone：長い たてがみ・しっぽ）：モデルが 毛を 見のがす（暗い 背景の 前）→ この 中は モデルを 見ないで、印と 絵の ふち線で 分ける。
        #   まわり 3px は 背景の 印（体の 上は のぞく）。中の 青っぽい 所（さく・雨の 光：hair_bg）も 背景の 印
        if p.get('hair_zone'):
            hz = shapes(p['hair_zone']); notrust |= hz; HZ |= hz
            HZR |= ndi.binary_dilation(hz, iterations=3) & ~hz & (M < C.get('hair_ring_m', 0.5))
    HZR &= ~HZ
    HZR &= ~ndi.binary_dilation(M > 0.6, iterations=C.get('hair_ring_gap', 14))   # 体の すぐ そば（体と 毛の あいだ）には 背景の 印を おかない（体と しっぽの あいだが 切れる）
    bgm |= (M < C.get('bg_thr_in', 0.04)) & ~notrust                      # outer の 中でも モデルが はっきり 背景と 見る 所は 背景
    bgm |= HZR
    if C.get('hair_bg') and HZ.any():
        hb = C['hair_bg']; V_ = img.max(-1); br_ = img[..., 2] - img[..., 0]
        hbm = HZ & (br_ >= hb.get('b_minus_r', 40)) & (V_ >= hb.get('vmin', 60)) & (V_ <= hb.get('vmax', 235))
        hbm = ndi.binary_opening(hbm, iterations=hb.get('open', 1))
        bgm |= hbm & ~shapes(C.get('hair_keep', []))
# 色で えらぶ 背景（ボードの ふちの 光の 線 など）：within の 中の 明るくて 色の うすい 所（キャラの 印の 近くは のぞく）
PICK = np.zeros((H, W), bool)
for bp in C.get('bg_pick', []):
    mx_, mn_ = img.max(-1), img.min(-1); sat_ = (mx_ - mn_) / np.maximum(mx_, 1)
    pk = shapes(bp['within']) & (mx_ >= bp.get('vmin', 215)) & (mx_ <= bp.get('vmax', 256)) & (sat_ <= bp.get('smax', 0.55)) & (sat_ >= bp.get('smin', 0))
    if 'b_minus_r' in bp: pk &= (img[..., 2] - img[..., 0]) >= bp['b_minus_r']     # 青い 物（あせの しずく など）
    if bp.get('erode'): pk = ndi.binary_erosion(pk, iterations=bp['erode'])
    # 大きな かたまり だけ（紙：細い 毛の 光の すじは open で 消えて のこらない）・中の 字は 穴うめ・ふちを 少し のばす
    if bp.get('open'): pk = ndi.binary_opening(pk, iterations=bp['open'])
    if bp.get('blob_min'):
        l_, n_ = ndi.label(pk)
        if n_:
            sz_ = ndi.sum(pk, l_, range(1, n_ + 1)); pk = np.isin(l_, [i + 1 for i in range(n_) if sz_[i] >= bp['blob_min']])
    if bp.get('fill'): pk = ndi.binary_fill_holes(pk)
    if bp.get('grow'): pk = ndi.binary_dilation(pk, iterations=bp['grow']) & shapes(bp['within'])
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
    # キャラの 絵は アプリの ボードの 下（前の 絵の 所 だけ ボードの 上）に 重ねる（bcp_chr_exp2.js）→ 板に かかる キャラも ぜんぶ キャラに 入れる
    #   （前は 板の 中を キャラから のぞいて いた：動くと 板の ところで キャラが 切れて 見えた・まさちゃん 11/05 08:31）
    #   板の 中で のぞくのは 光の ふち（halo）だけ（キャラの すぐ そば 3px は のぞかない）。vis_hard: true で 前の やり方
    if C.get('vis_hard'):
        for k in hards: hards[k] &= ~VIS
# ボードの うしろに いる キャラ（behind: true・ボードの ふちが キャラの 前に ある）：ボード（board_mask）の 所は キャラに 入れない。
#   ボードは キャラの 上に 重ねる（occl.png）→ キャラが 動くと ボードの ふちの うしろに まわりこむ（切れて 見えない）
BM = shapes(C.get('board_mask', [])) if C.get('board_mask') else np.zeros((H, W), bool)
BEH = [p['id'] for p in parts if p.get('behind')]
for k in BEH: hards[k] &= ~BM
res = {k: (v, None) for k, v in hards.items()}
# 5) うしろ（キャラなし）：光の すじ（まん中 c から 見た 角度ごとの 色）＋ まわりとの ちがいを なめらかに。ボードの 中（plate_y より 下）は inpaint
#    1回目：キャラの まわり GZ px まで 消して うめる → 元の 絵と うめた 色が ちがう 所（光の ふち・ふち線・きらきら）は キャラと いっしょに 動かす（halo）
#    2回目：うしろは 元の 絵の まま、キャラ＋halo の 所 だけ 1回目の うめた 色に（止まって いる ときは 元の 絵と 同じ）
F = C['fill']; cx, cy = F.get('c', [W / 2, H / 2]); GZ = F.get('glow_px', 12); GT = F.get('glow_thr', 22)
SRC_EX = np.zeros((H, W), bool)        # うめる 色の もとに しない 所（前に 重ねる 物と その 光：あとで きめる）
def make_fill(hole, vmax=None):
    if F.get('mode') == 'smooth':
        ring_ = ndi.binary_dilation(hole, iterations=F.get('ring', 10)) & ~ndi.binary_dilation(hole, iterations=1) & ~SRC_EX
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
    band = ~ndi.binary_dilation(hole, iterations=4) & (yy < PY) & (V <= VM) & ~shapes(F.get('band_ex', [])) & ~SRC_EX
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
    ring = ndi.binary_dilation(hole, iterations=F.get('ring', 10)) & ~ndi.binary_dilation(hole, iterations=1) & (V <= VM) & ~SRC_EX
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
    vis_p = VIS & ~ndi.binary_dilation(hard, iterations=3)
    if p['id'] in BEH: vis_p |= BM
    allow = ~others & (yy < PY) & ndi.binary_dilation(hard, iterations=GZ - 2) & ~NOH & ~vis_p & ~STILL
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
    z = ndi.binary_closing(z, iterations=1) & (allow | hard) & ~vis_p
    zones[p['id']] = z
# 物の まとまり（絵を 色の まとまりで 区切る：felzenszwalb）：キャラの 外の 物（びっくりマーク・紙ふぶき・しずく など）を 一部だけ キャラに 入れない
#   区切りの 大部分（frac より 多く）が キャラの 外・あまり 大きく ない・まわりの キャラと 色が はっきり ちがう → その 区切りは キャラから のぞく（動くと ちぎれて 見える）
from skimage.segmentation import felzenszwalb
OI = C.get('obj_integrity', {})
SEG = felzenszwalb(img / 255, scale=(OI or {}).get('scale', 300), sigma=0.8, min_size=40)
NSEG = int(SEG.max()) + 1; AREA = np.bincount(SEG.ravel(), minlength=NSEG)
FOBJ = np.zeros((H, W), bool)          # キャラの すぐ そばの 小さな 色の 物（びっくりマーク・しずく・紙ふぶき・きらきら）：キャラの 上に 動かない 絵として 重ねる（occl.png）
if OI is not False:
    seedz = ndi.binary_dilation((lab0 >= 1) & (lab0 <= len(parts)), iterations=OI.get('seed_gap', 6))
    mx3, mn3 = img.max(-1), img.min(-1)
    SAT = [np.bincount(SEG.ravel(), weights=((mx3 - mn3) / np.maximum(mx3, 1)).ravel(), minlength=NSEG) / np.maximum(AREA, 1)][0]
    VAL = np.bincount(SEG.ravel(), weights=mx3.ravel(), minlength=NSEG) / np.maximum(AREA, 1)
    CM = [np.bincount(SEG.ravel(), weights=img[..., k].ravel(), minlength=NSEG) / np.maximum(AREA, 1) for k in range(3)]
    ZALL = np.zeros((H, W), bool); HALL = np.zeros((H, W), bool)       # キャラ ぜんぶ（ほかの キャラの 体を 前の 物に しない）
    for k_ in zones: ZALL |= zones[k_]
    for k_ in hards: HALL |= hards[k_]
    INALL = np.bincount(SEG[ZALL], minlength=NSEG); INHARD = np.bincount(SEG[HALL], minlength=NSEG)
    doutA = ndi.distance_transform_edt(ZALL)
    BOARDB = np.zeros((H, W), bool)                                   # ボードの ふちの まわり（ふちの 光・飾りは 前の 物に しない）
    if C.get('board'):
        qm2 = poly(C['board']['quad']); BOARDB = ndi.binary_dilation(qm2, iterations=40) & ~ndi.binary_erosion(qm2, iterations=40)
    for p in parts:
        z = zones[p['id']]
        inside = np.bincount(SEG[z], minlength=NSEG)
        frac = inside / np.maximum(AREA, 1)
        cands = np.where((inside > 0) & (frac < OI.get('frac', 0.35)) & (AREA < OI.get('max_area', 15000)))[0]
        drop = []
        for L in cands:
            R = SEG == L
            ys_, xs_ = np.where(R); y0_, y1_, x0_, x1_ = max(0, ys_.min() - 6), min(H, ys_.max() + 7), max(0, xs_.min() - 6), min(W, xs_.max() + 7)
            Rs = R[y0_:y1_, x0_:x1_]; zs = z[y0_:y1_, x0_:x1_]
            band = ndi.binary_dilation(Rs, iterations=4) & ~Rs & zs
            if band.sum() < 6: continue
            cz = img[y0_:y1_, x0_:x1_][band].mean(0); cr = np.array([CM[0][L], CM[1][L], CM[2][L]])
            if np.abs(cz - cr).max() > OI.get('dcol', 60): drop.append(L)
        if drop:
            rm = np.isin(SEG, drop) & z & ~seedz
            if OI.get('keep_hard'):             # 線で 分けた キャラの 体（hard）の 中は のぞかない（暗い ひづめ・毛が 暗い 背景と 同じ 区切りに なる 絵）
                rm &= ~ndi.binary_erosion(hards[p['id']], iterations=OI.get('keep_hard_erode', 2))
            zones[p['id']] = z & ~rm
            print(p['id'], 'object integrity: drop', len(drop), 'regions', int(rm.sum()), 'px')
        # キャラに ふれる（3px）小さな 色の 物 → 上に 重ねる 物（キャラが 動くと その うしろに まわる＝物が よごれない）
        z2 = zones[p['id']]
        near_ = np.unique(SEG[ndi.binary_dilation(z2, iterations=3) & ~z2]) if OI.get('front', False) else []   # 前の 物：デザインごとに えらぶ（front: true）
        fo = [L for L in near_ if AREA[L] < OI.get('fobj_max', 2000) and (SAT[L] > OI.get('fobj_sat', 0.45) or (VAL[L] > 235 and AREA[L] < 400))
              and INALL[L] / max(AREA[L], 1) < OI.get('frac', 0.35) and INHARD[L] / max(AREA[L], 1) < 0.5 and not (SEG == L)[BOARDB].any()]
        Vv = img.max(-1)
        for L in (np.unique(SEG[z2]) if OI.get('float', False) else []):     # 小さな 明るい 物（紙ふぶき）：髪の 光の すじを まちがえる ので ふだんは 使わない（float: true で 使う）
            if AREA[L] >= OI.get('float_max', 700) or L in fo: continue
            R = SEG == L
            if (R & seedz).any() or doutA[R].min() > OI.get('float_edge', 8): continue      # キャラ ぜんぶの 外の すぐ そば だけ（目の 光 など 体の 中の 物は とおい）
            ys_, xs_ = np.where(R); y0_, y1_, x0_, x1_ = max(0, ys_.min() - 5), min(H, ys_.max() + 6), max(0, xs_.min() - 5), min(W, xs_.max() + 6)
            Rs = R[y0_:y1_, x0_:x1_]; ring3 = ndi.binary_dilation(Rs, iterations=3) & ~Rs
            if ring3.sum() < 6: continue
            dark = ~HALL[y0_:y1_, x0_:x1_] | (Vv[y0_:y1_, x0_:x1_] < OI.get('float_dark', 125))   # まわりが キャラの 体で ない（光の ふち・背景）か 暗い
            if dark[ring3].mean() >= OI.get('float_bg', 0.6) and VAL[L] > 150: fo.append(L)
        if fo:
            # 色の ちがい（キャラの ふちの 色と ちがう 物 だけ）
            fo2 = []
            for L in fo:
                R = SEG == L
                ys_, xs_ = np.where(R); y0_, y1_, x0_, x1_ = max(0, ys_.min() - 6), min(H, ys_.max() + 7), max(0, xs_.min() - 6), min(W, xs_.max() + 7)
                Rs = R[y0_:y1_, x0_:x1_]; band = ndi.binary_dilation(Rs, iterations=4) & ~Rs & z2[y0_:y1_, x0_:x1_]
                if band.sum() < 4: fo2.append(L); continue            # キャラの 絵に ほとんど ふれて いない 物（びっくりマークの 体 など）：そのまま 前の 物
                cz = img[y0_:y1_, x0_:x1_][band].mean(0); cr = np.array([CM[0][L], CM[1][L], CM[2][L]])
                if np.abs(cz - cr).max() > OI.get('dcol', 60): fo2.append(L)
            if fo2:
                FOBJ |= np.isin(SEG, fo2)
                print(p['id'], 'front objects', len(fo2))
FA = np.zeros((H, W), np.float32)
if FOBJ.any():
    HARD_ALL = np.zeros((H, W), bool)
    for k_, v_ in hards.items(): HARD_ALL |= v_
    core2 = ndi.binary_dilation(HARD_ALL, iterations=2) | seedz
    FB = FOBJ & ~seedz                                    # 前の 物（色が まわりの キャラと はっきり ちがう 物）は キャラの 区切りに 入って いても 前に
    # となりの 区切りで 物に くっついて いる 物の 一部（びっくりマークの 下の はしの ふち・光 など）：キャラの 中に 入って いても
    #   ・小さい（fm_area px 未満）・説明の 印（seedz）に ふれない・まわりの 25% 以上が 物・物の 色に にて いる（60）・まわりの キャラの 色とは ちがう（50）
    FM = np.zeros((H, W), bool)
    for _ in range(2):
        cur = FB | FM
        adj = np.unique(SEG[ndi.binary_dilation(cur, iterations=2) & ~cur])
        add = []
        for L2 in adj:
            if AREA[L2] > OI.get('fm_area', 800): continue
            R2 = SEG == L2
            ys_, xs_ = np.where(R2); y0_, y1_, x0_, x1_ = max(0, ys_.min() - 5), min(H, ys_.max() + 6), max(0, xs_.min() - 5), min(W, xs_.max() + 6)
            R2s = R2[y0_:y1_, x0_:x1_]; curs = cur[y0_:y1_, x0_:x1_]; hs = HARD_ALL[y0_:y1_, x0_:x1_]; im_ = img[y0_:y1_, x0_:x1_]
            if (R2s & seedz[y0_:y1_, x0_:x1_]).any(): continue
            bd2 = ndi.binary_dilation(R2s, iterations=2) & ~R2s
            if bd2.sum() < 4 or (bd2 & curs).sum() / bd2.sum() < 0.25: continue
            if np.abs(im_[R2s].mean(0) - im_[bd2 & curs].mean(0)).max() >= OI.get('fm_col', 60): continue
            around = bd2 & hs & ~curs
            if around.sum() >= 5 and np.abs(im_[R2s].mean(0) - im_[around].mean(0)).max() < OI.get('fm_char', 50): continue
            add.append(L2)
        if not add: break
        FM |= np.isin(SEG, add) & ~seedz
    FX = FB | FM
    core2 = (ndi.binary_dilation(HARD_ALL & ~ndi.binary_dilation(FM, iterations=1), iterations=2) | seedz) & ~FX
    RG = OI.get('fobj_ring', 3)
    dF = ndi.distance_transform_edt(~FX)
    dC = ndi.distance_transform_edt(~core2)
    FA = (np.clip((RG + 1 - dF) / 3.0, 0, 1) * np.clip(dC / 2.0, 0, 1)).astype(np.float32)   # 物の まわりの 光：RG-2 px は 1・そこから 3px で 0（キャラの そばも なめらかに 0）
    FA[FX] = 1.0                                                                               # 物 そのものは いつも 1（キャラの 絵が すけて 見えない）
    for k_ in zones: zones[k_] = zones[k_] & ~(FA > 0.5)           # 物の 所は キャラの 絵に 入れない（まわりの 光は キャラと いっしょ）
    SRC_EX = ndi.binary_dilation(FX, iterations=3)                 # うめる 色の もとに しない のは 物と その すぐ そば だけ（まわりの 暗い 所は もとに する）
    print('front objects ext px', int(FX.sum()), 'ring px', int((FA > 0.02).sum()))
# 毛の 所の 中の 穴（毛の すじの あいだ・毛の 前の しずく）：かこまれて いて ほとんど 毛の 所に ある 穴は キャラに 入れる（動いた とき 毛の 中に 止まった 所が 見えない）
if HZ.any():
    for k_ in zones:
        z_ = zones[k_]; hl_ = ndi.binary_fill_holes(z_) & ~z_
        l_, n_ = ndi.label(hl_)
        if n_:
            inz = ndi.sum(HZ, l_, range(1, n_ + 1)); sz_ = ndi.sum(hl_, l_, range(1, n_ + 1))
            fill_ = [i + 1 for i in range(n_) if inz[i] >= 0.9 * sz_[i] and sz_[i] <= C.get('hair_hole_max', 5000)]
            if fill_:
                oth_ = np.zeros((H, W), bool)
                for k2_ in zones:
                    if k2_ != k_: oth_ |= zones[k2_]
                zones[k_] = z_ | (np.isin(l_, fill_) & ~oth_ & ~(FA > 0.5))
                print(k_, 'hair holes filled', len(fill_), int(np.isin(l_, fill_).sum()), 'px')
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
# ボードの 前に 重ねる 所（occl.png・すき通し 0〜255）：うしろに いる キャラ（behind）の そばの ボード（ふち線まで＝1）と ふちの 光（behind_glow px で 1 → 0）
#   キャラの 絵は ふちの 光の 下も ふくむ（光の ふちで かたく 切れない）・前に いる キャラの 所は 入れない
for f_ in ('occl.png', 'board.png'):
    if os.path.exists(os.path.join(OUT, f_)): os.remove(os.path.join(OUT, f_))
OCCA = np.zeros((H, W), np.float32)
if BEH and BM.any():
    GW = C.get('behind_glow', 12)
    ramp_ = np.clip(1 - ndi.distance_transform_edt(~BM) / max(GW, 1), 0, 1)
    near_b = np.zeros((H, W), bool)
    for k in BEH: near_b |= ndi.binary_dilation(res[k][0], iterations=C.get('occl_dist', 40))
    front = np.zeros((H, W), np.float32)
    for k, (z_, a_) in res.items():
        if k not in BEH: front = np.maximum(front, a_)
    OCCA = (ramp_ * near_b * (1 - np.clip(front / 0.02, 0, 1))).astype(np.float32)
    Image.fromarray((BM * 255).astype(np.uint8)).save(os.path.join(OUT, 'board.png'))
if FA.any():
    OCCA = np.maximum(OCCA, FA)          # 前の 物と その 光の ふち（元の 絵）：キャラの 上に 動かない 絵として
    print('front objects px', int((FA > 0.5).sum()))
if SFA.any():
    OCCA = np.maximum(OCCA, SFA)         # 動かない 前の 絵（static_front）
if OCCA.any():
    Image.fromarray(np.clip(OCCA * 255 + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'occl.png'))
    print('occl px', int((OCCA > 0.5).sum()))
# 動くと「切れて」見える ふち（絵の ふち線で ない なめらかな 所＝布・雲・光の 中を 通る さかい）：キャラの 絵を 外へ のばして なめらかに すき通す
#   のばす 所の 色も 背景も 元の 絵（止まって いる ときは 元と 同じ）。動くと 少し ずれて とけこむ（かたい 切れ目に ならない）
#   のばす はば：その 所が 動く いちばん 大きい きょり（ぷるん＋3Dの 向き：bcp_chr_exp2.js と 同じ 計算）＋2px は すき通さない・そこから ramp px で 0 へ
GJ = os.path.join(os.path.dirname(C['clean']), 'geom.json')
SG = json.load(open(GJ))['S'] if os.path.exists(GJ) else 0.4
MO = C.get('motion', {}); GRP = C.get('groups', {})
def disp_bound(zm, spec):
    ys, xs = np.where(zm)
    if not len(xs): return np.zeros((H, W), np.float32)
    o = spec.get('o')
    if isinstance(o, list): ox, oy = o
    elif o == 'top': yt = ys.min(); ox, oy = float(xs[ys <= yt + 6].mean()), float(yt)
    elif o == 'bottom_center': ox, oy = float((xs.min() + xs.max()) / 2), float(ys.max())
    elif o == 'contact' and BM.any() and (zm & ndi.binary_dilation(BM, iterations=4)).any():
        cy_, cx_ = np.where(zm & ndi.binary_dilation(BM, iterations=4)); ox, oy = float(cx_.mean()), float(cy_.mean())
    else: yb = ys.max(); ox, oy = float(xs[ys >= yb - 6].mean()), float(yb)
    h_pt = (ys.max() - ys.min()) * SG; w_pt = (xs.max() - xs.min()) * SG
    amp = spec.get('amp', min(1.0, 205.0 / max(h_pt, 1))); deg = spec.get('deg', 4.0 * min(1.0, 300.0 / max(w_pt, 1))); axx = spec.get('ax', amp)
    X = (xx - ox) * SG; Y = (yy - oy) * SG
    jel = np.hypot(0.024 * axx * X, 0.038 * amp * Y)
    th = np.radians(deg); rot = np.zeros((H, W), np.float32)
    for sg_ in (1, -1):
        f_ = 600.0 / (600.0 - sg_ * X * np.sin(th))
        rot = np.maximum(rot, np.hypot(X * np.cos(th) * f_ - X, Y * f_ - Y))
    return ((jel + rot) / SG).astype(np.float32)
STf = C.get('soft_tear', {})
EXT = {}
if STf is not False:
    gimg = np.max(np.stack([sobel(cv2.GaussianBlur(img[..., k] / 255, (0, 0), 0.8)) for k in range(3)]), 0)
    gmx = ndi.maximum_filter(gimg, size=5)
    dif_ = np.abs(img - bgx).max(-1)
    border_ = np.zeros((H, W), bool); border_[:3, :] = border_[-3:, :] = True; border_[:, :3] = border_[:, -3:] = True
    claimed = np.zeros((H, W), bool)
    allz = np.zeros((H, W), bool); alla = np.zeros((H, W), np.float32)
    for k, (z_, a_) in res.items(): allz |= z_; alla = np.maximum(alla, a_)
    for i, p in enumerate(parts):
        pid = p['id']; z = res[pid][0]
        others = np.zeros((H, W), bool)
        for k, (z_, a_) in res.items():
            if k != pid: others |= a_ > 0.02
        gid = next((g_ for g_, mem in GRP.items() if pid in mem), None)
        if gid:
            zg = np.zeros((H, W), bool)
            for m_ in GRP[gid]:
                if m_ in res: zg |= res[m_][0]
            dmap = disp_bound(zg, MO.get(gid, {}))
        else:
            dmap = disp_bound(z, MO.get(pid, {}))
        er = cv2.erode(z.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        bd = z & ~er
        nogo = others | STILL | (OCCA > 0.02) | border_ | (BM if pid in BEH else np.zeros((H, W), bool)) | VIS   # 見えて いる ボード（アプリの ボードの 下で 見えない）には のばさない
        outside = cv2.dilate(z.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~z & ~nogo
        bd &= cv2.dilate(outside.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        inner = cv2.erode(z.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~cv2.erode(z.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
        difn = ndi.maximum_filter(np.where(inner, dif_, 0), size=9)
        weak = bd & (gmx < STf.get('g', 0.05)) & (difn > STf.get('dif', 14))
        lab_, n_ = ndi.label(weak, structure=np.ones((3, 3)))
        ext = np.zeros((H, W), np.float32)
        nt = 0
        for k in range(n_):
            comp = lab_ == k + 1
            if comp.sum() < STf.get('min', 8): continue
            dm = float(dmap[comp].max())
            m_ = int(np.clip(np.ceil(dm) + 2, 3, STf.get('margin_max', 18))); r_ = int(np.clip(np.ceil(1.5 * dm) + 4, 8, STf.get('ramp_max', 30)))
            y0_, x0_ = np.maximum(np.min(np.where(comp), 1) - (m_ + r_ + 2), 0); y1_, x1_ = np.minimum(np.max(np.where(comp), 1) + (m_ + r_ + 3), [H, W])
            sub = comp[y0_:y1_, x0_:x1_]
            dC = ndi.distance_transform_edt(~sub)
            al_ = np.clip((m_ + r_ - dC) / r_, 0, 1)
            # のばすのは 切れて いる 区切り（その 物：雲・布 など）の 中 だけ（ほかの 物に かかると 二重に 見える）
            outn = cv2.dilate(sub.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~z[y0_:y1_, x0_:x1_]
            labs = np.unique(SEG[y0_:y1_, x0_:x1_][outn])
            region = (dC <= m_ + r_) & ~z[y0_:y1_, x0_:x1_] & ~nogo[y0_:y1_, x0_:x1_] & ~claimed[y0_:y1_, x0_:x1_] & np.isin(SEG[y0_:y1_, x0_:x1_], labs)
            ext[y0_:y1_, x0_:x1_] = np.maximum(ext[y0_:y1_, x0_:x1_], np.where(region, al_, 0))
            nt += 1
        if nt:
            ext = cv2.GaussianBlur(ext, (0, 0), 1.0) * (ext > 0)
            claimed |= ext > 0.02
            EXT[pid] = ext
            print(pid, 'soft tear', nt, 'places ext px', int((ext > 0.5).sum()))
# 6) キャラの 絵（RGBA）：色は 元の 絵・ext（ほかの キャラの うしろに かくれた 所）は まわりの 色で のばす
for i, p in enumerate(parts):
    hard, a = res[p['id']]; rgb = img.copy()
    if p['id'] in EXT: a = np.maximum(a, EXT[p['id']])      # なめらかに のばした 所（色は 元の 絵）
    if p.get('ext_under'):
        # ほかの キャラ（上に 重なる もの）の うしろに かくれた 所を、まわりの 色で のばす（動いた とき すき間に うしろが 見えない ように）
        over = np.zeros((H, W), bool)
        for oid in p['ext_under']: over |= res[oid][0]
        ex = over & ndi.binary_dilation(hard, iterations=p.get('ext_px', 20)) & ~hard
        src_w = (hard & ~ndi.binary_dilation(over, iterations=1)).astype(np.float32)
        ext_rgb = diffuse(img, src_w, ex)
        rgb = np.where(ex[..., None], ext_rgb, rgb); a = np.maximum(a, ex.astype(np.float32))
    if p['id'] in BEH and BM.any():
        # ボードの うしろに かくれた 所を まわりの 色で のばす（動いて ボードの ふちから 出ても すき間に ならない・止まって いる ときは ボードの 下）
        others_ = np.zeros((H, W), bool)
        for q in parts:
            if q['id'] != p['id']: others_ |= res[q['id']][0]
        anyc_ = np.zeros((H, W), bool)
        for k_, (z_, a_) in res.items(): anyc_ |= a_ > 0.02
        ex = BM & ndi.binary_dilation(hard, iterations=p.get('behind_px', 10)) & ~hard & ~others_ & ~anyc_ & (OCCA > 0.98)    # occl.png の こい 所 だけ（止まって いる ときは かくれる）
        if ex.any():
            src_w = (hard & ~ndi.binary_dilation(BM, iterations=1)).astype(np.float32)
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
