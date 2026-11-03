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
    if 'poly' in s:
        cv2.fillPoly(m, [np.round(np.array(s['poly'])).astype(np.int32)], 1)
    elif 'rect' in s:
        x0, y0, x1, y1 = s['rect']; m[y0:y1, x0:x1] = 1
    elif 'rrect' in s:
        x0, y0, x1, y1, r = s['rrect']; m[y0:y1, x0:x1] = 1
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
    if s.get('shrink'):
        m = cv2.erode(m, disk(s['shrink']))
    if s.get('round'):
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(s['round']))
    if 'clip' in s:
        x0, y0, x1, y1 = s['clip']; c = np.zeros_like(m); c[y0:y1, x0:x1] = 1; m = m & c
    return m.astype(bool)
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
    prot = ((hsv0[..., 1] > 100) & (hsv0[..., 2] > 150)) | (src.max(-1) > 200) | (((src[..., 0] - src[..., 2]) > 45) & (src.max(-1) > dg.get('warm_v', 0)))
    prot = cv2.GaussianBlur(ndi.binary_dilation(prot, iterations=4).astype(np.float32), (0, 0), 2)
    v = dg.get('v', 110)
    wgt = band * np.clip((v - Vl) / 40, 0, 1) * (1 - prot)
    src = src * (1 - wgt[..., None]) + base * wgt[..., None]
# 先に 写す 所（となりの 絵を ずらして はる：旗の 下の 鎖など）
for p in C.get('patch', []):
    x0, y0, x1, y1 = p['dst']; dx, dy = p.get('dx', 0), p.get('dy', 0)
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
    f = np.zeros_like(src)
    for c in range(3):
        n1 = cv2.GaussianBlur(src[..., c] * w, (0, 0), s1); d1 = cv2.GaussianBlur(w, (0, 0), s1)
        n2 = cv2.GaussianBlur(src[..., c] * w, (0, 0), s2); d2 = cv2.GaussianBlur(w, (0, 0), s2)
        f1 = n1 / np.maximum(d1, 1e-6); f2 = n2 / np.maximum(d2, 1e-6)
        a = np.clip(d1 / 0.25, 0, 1)
        f[..., c] = f1 * a + f2 * (1 - a)
    return f
if any('bg' in r for r in C['regions']):
    # 所ごとに：その 所の 地（きまり bg：vmax・br）だけから 色を 作る（明るい 地と 暗い 地を まぜない）
    fill = np.zeros_like(src)
    for r in C['regions']:
        rm = shape_mask(r); rule = r.get('bg', {})
        sel = rm & ~keep & ~ndi.binary_dilation(tmask, iterations=2)
        if 'vmax' in rule: sel &= V <= rule['vmax']
        if 'br' in rule: sel &= (B - R) >= rule['br']
        if rule.get('nopill'): sel &= ~pill
        if r.get('only') != 'text': sel &= ~txt
        sel = ndi.binary_erosion(sel, iterations=1)
        f = smooth_from(sel.astype(np.float32), rule.get('s1', 18), rule.get('s2', 60))
        near = ndi.binary_dilation(rm, iterations=8)
        fill[near] = f[near]
else:
    fill = smooth_from(bg.astype(np.float32))
rng = np.random.default_rng(3)
noise = cv2.GaussianBlur(rng.normal(0, 1.6, (H, W)).astype(np.float32), (0, 0), 0.7)
fill += noise[..., None] * np.array([0.6, 0.8, 1.2], np.float32)
soft = cv2.GaussianBlur(remove.astype(np.float32), (0, 0), 2.0) * (~keep)
out = np.clip(src * (1 - soft[..., None]) + fill * soft[..., None], 0, 255).astype(np.uint8)
if C.get('inpaint'):
    im8 = np.ascontiguousarray(out)
    m = np.zeros((H, W), bool)
    for s3 in C['inpaint']:
        m |= shape_mask(s3)
    if C.get('inpaint_mode') == 'rows':
        filled = im8.astype(np.float32).copy()
        ys, xs = np.nonzero(m)
        for y in range(ys.min(), ys.max() + 1):
            row = np.nonzero(m[y])[0]
            if not len(row): continue
            x0, x1 = row.min(), row.max()
            a0 = im8[y, max(0, x0 - 6):x0 - 1].astype(np.float32).mean(0); a1 = im8[y, x1 + 2:min(W, x1 + 7)].astype(np.float32).mean(0)
            t = np.linspace(0, 1, x1 - x0 + 1)[:, None]
            filled[y, x0:x1 + 1] = a0 * (1 - t) + a1 * t
        filled = cv2.GaussianBlur(filled, (0, 0), 2.0)
    else:
        bgr = cv2.cvtColor(im8, cv2.COLOR_RGB2BGR)
        bgr = cv2.inpaint(bgr, m.astype(np.uint8) * 255, C.get('inpaint_r', 12), cv2.INPAINT_TELEA)
        filled = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    if C.get('inpaint_mode') != 'rows':
        filled = cv2.GaussianBlur(filled, (0, 0), 3.0)
    wm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3.0)[..., None]
    out = np.clip(out * (1 - wm) + filled * wm, 0, 255).astype(np.uint8)
Image.fromarray(out).save(os.path.join(D, 'clean.png'))
dbg = src.copy(); dbg[remove] = dbg[remove] * 0.4 + np.array([255, 0, 0]) * 0.6; dbg[keep & region] = dbg[keep & region] * 0.4 + np.array([0, 255, 0]) * 0.6
Image.fromarray(np.clip(dbg, 0, 255).astype(np.uint8)).save(os.path.join(D, 'clean_dbg.png'))
print('clean', D, int(remove.sum()))
