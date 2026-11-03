# 結果ボードカスタム（絵の ボード）：ボードの 前に ある もの（馬・手・前の 紙ふぶき）を すき通しの 絵に 切り出す
#   python3 bcp_fg.py <デザインの フォルダ>   → fg.png（RGBA・絵と 同じ 大きさ）・fgmask.png（bcp_clean の keep に 使う）
#   cfg['fg'] = { roi:[x0,y0,x1,y1], seeds:[[x,y],…]（馬の 中の 点）, navy:{br,bg,v}（ボードの 紺の きまり）,
#                 conf:[[x0,y0,x1,y1],…]（前の 紙ふぶき：四角の 中の あざやかな 所）, close:2, feather:0.8 }
#   アプリの ボード（字・行）は 背景と この 絵の あいだに 入る（bcp_inj）
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
F = cfg['fg']
src = np.asarray(Image.open(os.path.join(D, cfg.get('src', 'src.png'))).convert('RGB')).astype(np.float32)
H, W = src.shape[:2]
R, G, B = src[..., 0], src[..., 1], src[..., 2]
V = src.max(-1)
nv = F.get('navy', {'br': 12, 'bg': -5, 'v': 170})
board = (B > R + nv['br']) & (B > G + nv['bg']) & (V < nv['v'])        # ボードの 紺（地・行）
x0, y0, x1, y1 = F['roi']
roi = np.zeros((H, W), bool); roi[y0:y1, x0:x1] = True
if F.get('quad_margin') is not None:
    # ボードの 四すみの 中（＋少し）だけ：ボードの 外は 背景と 同じ 絵なので いらない
    qm = np.zeros((H, W), np.uint8)
    cv2.fillPoly(qm, [np.round(np.array(cfg['quad'])).astype(np.int32)], 1)
    k = int(F['quad_margin'])
    if k: qm = cv2.dilate(qm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    roi &= qm.astype(bool)
cand = ~board & roi
if F.get('mode') == 'region':
    # 所で きめる：rects（足す 四角）− minus（ひく 四角）の 中の 紺で ない 所 ぜんぶ（馬・ふきだし・びっくりマーク など）。
    #   小さな かけら（min_part px より 小さい もの）は すてる
    reg = np.zeros((H, W), bool)
    for r_ in F['rects']:
        x0_, y0_, x1_, y1_ = r_; reg[y0_:y1_, x0_:x1_] = True
    for r_ in F.get('minus', []):
        x0_, y0_, x1_, y1_ = r_; reg[y0_:y1_, x0_:x1_] = False
    horse = cand & reg
    lab, n = ndi.label(horse, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(horse, lab, range(1, n + 1))
        horse = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= F.get('min_part', 30)])
    ids = ['region']
else:
    lab, n = ndi.label(cand, structure=np.ones((3, 3)))
    ids = sorted({int(lab[y, x]) for x, y in F['seeds']} - {0})
    horse = np.isin(lab, ids)
if F.get('close'):
    horse = ndi.binary_closing(horse, iterations=F['close']) & roi
def fill_small_holes(m, hmax):
    # 穴を うめる（hmax より 大きな 穴は うめない：布や 馬が ボードを かこむ と、ボードの 中 ぜんぶが 穴に なる ため）
    if hmax is None:
        return ndi.binary_fill_holes(m)
    holes = ndi.binary_fill_holes(m) & ~m
    lab_h, nh = ndi.label(holes)
    if nh == 0:
        return m
    sz = ndi.sum(holes, lab_h, range(1, nh + 1))
    return m | np.isin(lab_h, [i + 1 for i in range(nh) if sz[i] <= hmax])
HMAX = F.get('hole_max')
horse = fill_small_holes(horse, HMAX)
if F.get('grabcut'):
    # GrabCut：色の かたまりで 出した 馬（ふちの 光も 入る）を、絵の ふち線で 切り直す（ボードの 字は 背景・馬の 中は 前）
    gcf = F['grabcut']
    m0 = horse.copy()
    gc = np.full((H, W), cv2.GC_BGD, np.uint8)
    gc[ndi.binary_dilation(m0, iterations=gcf.get('grow', 12))] = cv2.GC_PR_BGD
    gc[m0] = cv2.GC_PR_FGD
    core = ndi.binary_erosion(m0, iterations=gcf.get('erode', 10))
    gc[core] = cv2.GC_FGD
    gc[board & ~m0] = cv2.GC_BGD
    txt = (B - R > 15) & (V > 120)                      # 青っぽい 白（ボードの 字）は 背景
    gc[ndi.binary_dilation(txt, iterations=1) & ~core] = cv2.GC_BGD
    bx0, by0, bx1, by1 = gcf['box']
    sub = np.ascontiguousarray(src[by0:by1, bx0:bx1, ::-1].astype(np.uint8)); g = np.ascontiguousarray(gc[by0:by1, bx0:bx1])
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(sub, g, None, bgd, fgd, gcf.get('iters', 6), cv2.GC_INIT_WITH_MASK)
    res = np.zeros((H, W), bool); res[by0:by1, bx0:bx1] = (g == cv2.GC_FGD) | (g == cv2.GC_PR_FGD)
    horse = fill_small_holes(res, HMAX) & m0
    # 小さな かけら（1000px より 小さい もの）は すてる
    lab3, n3 = ndi.label(horse)
    if n3:
        sz = ndi.sum(horse, lab3, range(1, n3 + 1))
        horse = np.isin(lab3, [i + 1 for i in range(n3) if sz[i] >= gcf.get('min_px', 1000)])
for ex in F.get('exclude', []):                       # 馬に つながって しまった ボードの 字 など
    ex0, ey0, ex1, ey1 = ex; horse[ey0:ey1, ex0:ex1] = False
alpha = horse.astype(np.float32)
fe = F.get('feather', 0.8)
if fe:
    alpha = cv2.GaussianBlur(alpha, (0, 0), fe)
    alpha = np.where(horse, np.maximum(alpha, 0.5), alpha)
rgb = src.copy()
# 前の 紙ふぶき：四角の まわりの 紺を 地に して、色の ちがいから すき通しを 出す（ぼけた はしも なめらかに）
for c in F.get('conf', []):
    cx0, cy0, cx1, cy1 = c
    p = src[cy0:cy1, cx0:cx1]
    edge = np.concatenate([p[:2].reshape(-1, 3), p[-2:].reshape(-1, 3), p[:, :2].reshape(-1, 3), p[:, -2:].reshape(-1, 3)])
    eb = board[cy0:cy1, cx0:cx1]
    ebe = np.concatenate([eb[:2].ravel(), eb[-2:].ravel(), eb[:, :2].ravel(), eb[:, -2:].ravel()])
    bg = np.median(edge[ebe], 0) if ebe.sum() > 8 else np.median(edge, 0)
    d = np.linalg.norm(p - bg, axis=-1)
    # 紙ふぶきの 色（いちばん 地から 遠い 2%）と 地の 色の まぜ具合を すき通しに（紺っぽい 線 など は 入れない）
    top = p[d >= np.percentile(d, 98)]
    fc = np.median(top, 0)
    dv = fc - bg
    a = ((p - bg) @ dv) / max(float(dv @ dv), 1.0)
    lo = F.get('conf_lo', 0.15)
    a = np.clip((a - lo) / (1 - lo), 0, 1)
    # 四角の はしは 0 に（となりの もの を 入れない）
    m = np.ones_like(a); k = 3
    m[:k] *= np.linspace(0, 1, k)[:, None]; m[-k:] *= np.linspace(1, 0, k)[:, None]
    m[:, :k] *= np.linspace(0, 1, k)[None]; m[:, -k:] *= np.linspace(1, 0, k)[None]
    a = a * m
    col = (p - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 1e-3)
    col = np.clip(col, 0, 255)
    sub_a = alpha[cy0:cy1, cx0:cx1]
    take = a > sub_a
    rgb[cy0:cy1, cx0:cx1][take] = col[take]
    alpha[cy0:cy1, cx0:cx1] = np.maximum(sub_a, a)
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(os.path.join(D, 'fg.png'))
Image.fromarray((alpha * 255).astype(np.uint8)).save(os.path.join(D, 'fgmask.png'))
chk = src.copy(); chk[alpha > 0.5] = chk[alpha > 0.5] * 0.35 + np.array([0, 255, 0]) * 0.65
Image.fromarray(chk.astype(np.uint8)).save(os.path.join(D, 'fg_dbg.png'))
print('fg', D, 'horse px', int(horse.sum()), 'comps', ids)
