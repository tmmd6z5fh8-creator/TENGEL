# 結果ボードカスタム：まわりの 光と 雲を 動かす（実験・まさちゃん 11/05 21:46「周り光や雲が動くようにして！」）
#   python3 amb_stage.py <デザインの 設定 json> [段の 名前,…]
#   トロフィー・ボード・紙ふぶきは 動かさない。光の すじ（上）は 光の もとの まわりで ゆっくり ゆれる＋明るさが ゆっくり 流れる・雲（横と 下）は ゆっくり うねる。
#   アプリの 舞台の 絵（bcp_<名前>.webp：1170×2532）の 上に WebGL の 絵（bcp_chr_exp2.js の amb）を かさねる：
#     m1（半分の 大きさ）：R,G＝雲の 動く 向き・B＝雲の 動く 強さ（トロフィーの そばは 0 へ）
#     m2：R＝光の すじの ゆれる 強さ・G＝位相の ゆらぎ 1・B＝かさねる こさ（トロフィー・紙ふぶきの 所は 0）
#     m3：R＝動かない 所（そこを 取った ときは うめた 色 f を つかう）・G＝0・B＝位相の ゆらぎ 2
#     f（4分の1）：動かない 所を まわりの 色で うめた 絵（動いた とき トロフィーの ふちの 色が 雲に 入らない）
#   止まって いる とき（t=0・動きの 強さ 0）は 元の 絵と 同じ（かさねる 所は 動かない 所から はなれて いる）。
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
D = json.load(open(sys.argv[1], encoding='utf8')); only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
ASSET = D.get('assets', '/home/claude/tengel/source/ios/bcp_assets'); SRV = D['srv']; os.makedirs(SRV, exist_ok=True)
DBG = D.get('dbg', SRV); os.makedirs(DBG, exist_ok=True)
H, W = 2532, 1170
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def shape(s):
    m = np.zeros((H, W), np.uint8)
    if 'poly' in s: cv2.fillPoly(m, [np.round(np.array(s['poly'])).astype(np.int32)], 1)
    elif 'ell' in s:
        (cx, cy), rx, ry = s['ell']; return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    elif 'rect' in s: x0, y0, x1, y1 = s['rect']; m[max(0, y0):y1, max(0, x0):x1] = 1
    elif 'line' in s: cv2.polylines(m, [np.round(np.array(s['line'])).astype(np.int32)], False, 1, thickness=int(round(2 * s['r'])))
    return m.astype(bool)
def shapes(l):
    m = np.zeros((H, W), bool)
    for s in l: m |= shape(s)
    return m
def sstep(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def diffuse(field, w, m):
    acc = None
    for sg in (64, 32, 16, 8, 4, 2):
        num = cv2.GaussianBlur(field * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
        f = num / np.maximum(den, 1e-6)[..., None]; conf = np.clip(den / 0.3, 0, 1)[..., None]
        acc = f if acc is None else acc * (1 - conf) + f * conf
    return acc
def smooth_noise(seed, sig):
    r = np.random.default_rng(seed).normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    r = cv2.GaussianBlur(r, (0, 0), sig / 4); r = (r - r.min()) / max(float(r.max() - r.min()), 1e-6)
    return cv2.resize(r, (W, H), interpolation=cv2.INTER_CUBIC)
names = [s['name'] for s in D['stages'] if not only or s['name'] in only]
IMG = {n: np.asarray(Image.open(os.path.join(ASSET, f'bcp_{n}.webp')).convert('RGB')).astype(np.float32) for n in names}
# 1) 動かない 所：トロフィー（形）と 紙ふぶき（四角の 中で まわりの 色と ちがう 所：段 ぜんぶの 合わせ）
T = shapes(D['static'])
OBJ = np.zeros((H, W), bool)
for ob in D.get('objects', []):
    x0, y0, x1, y1 = ob['box']; sub_all = np.zeros((y1 - y0, x1 - x0), bool)
    for n in names:
        a = IMG[n][y0:y1, x0:x1]; h, w = a.shape[:2]
        ring = np.zeros((h, w), bool); ring[:2] = ring[-2:] = True; ring[:, :2] = ring[:, -2:] = True
        Y, X = np.mgrid[0:h, 0:w].astype(np.float32); Ab = np.stack([X[ring], Y[ring], np.ones(ring.sum(), np.float32)], 1)
        bg = np.zeros_like(a)
        for c in range(3):
            co, *_ = np.linalg.lstsq(Ab, a[..., c][ring], rcond=None); bg[..., c] = co[0] * X + co[1] * Y + co[2]
        d = np.abs(a - bg).max(-1); thr = max(ob.get('thr', 28), 0.35 * float(np.percentile(d, 99)))
        m = d > thr; m &= ~ring
        m = ndi.binary_opening(m, iterations=1)
        l_, n_ = ndi.label(m)
        if n_:
            sz = ndi.sum(m, l_, range(1, n_ + 1)); m = l_ == (int(np.argmax(sz)) + 1)
            sub_all |= m
    if sub_all.sum() >= 12:
        pts = np.argwhere(sub_all)[:, ::-1].astype(np.int32); hull = cv2.convexHull(pts)
        hm = np.zeros(sub_all.shape, np.uint8); cv2.fillPoly(hm, [hull], 1); sub_all = hm.astype(bool)
    else:
        sub_all[:] = True
    OBJ[y0:y1, x0:x1] |= ndi.binary_dilation(sub_all, iterations=ob.get('dil', 3))
OBJ &= ~T
STAT = T | OBJ
dT = ndi.distance_transform_edt(~T).astype(np.float32); dO = ndi.distance_transform_edt(~OBJ).astype(np.float32)
dS = np.minimum(dT, dO)
tap = sstep(*D.get('taper_T', [4, 30]), dT) * sstep(*D.get('taper_O', [2, 10]), dO)        # 動く 強さ（トロフィーの そばで 0 へ）
WD = sstep(8, 16, dS)                                                                       # かさねる こさ（動かない 所から 8px は 0）
FS = 1 - sstep(2, 4, dS)                                                                    # 動かない 所（取った ときは うめた 色・4px より 外は 0）
R_ = D['rays']; SM = D['smoke']
rw = (1 - sstep(R_['y0'], R_['y1'], yy)) * tap
cw = sstep(SM['y0'], SM['y1'], yy) * (1 - sstep(SM['yb0'], SM['yb1'], yy)) * tap
WD = WD * sstep(0.0, 0.02, ndi.maximum_filter(np.maximum(rw, cw), size=9))               # 動かない 所（床・うつり）は かさねない
# 雲の 向き：トロフィーの まん中から 外へ（上むきを 少し）＋ゆらぎ（±25度）
bx = (xx - SM['cx']) / SM['cx']; by = np.full_like(bx, -SM.get('up', 0.45))
ang = np.arctan2(by, bx) + (smooth_noise(11, 220) - 0.5) * np.radians(2 * SM.get('curl_deg', 25))
dx, dy = np.cos(ang), np.sin(ang)
n1 = smooth_noise(21, 160); n2 = smooth_noise(31, 200)
def enc(*ch, half=True):
    a = np.dstack([np.clip(c * 255 + 0.5, 0, 255).astype(np.uint8) for c in ch])
    if half: a = cv2.resize(a, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    return Image.fromarray(a, 'RGB')
# かさねる こさが 0 でない 所で 動かない 所を 取らない（半分の 大きさの 線形 補間でも）：たしかめ
assert float(FS[WD > 0].max()) < 1e-6, 'overlap'
allj = json.load(open(D['stage_json'], encoding='utf8')) if os.path.exists(D['stage_json']) else {}
for n in names:
    a = IMG[n]
    # うめた 色（動かない 所 → まわりの 動く 所の 色）
    hole = ndi.binary_dilation(STAT, iterations=6)
    fill = diffuse(a, (~hole).astype(np.float32), hole)
    f4 = cv2.resize(np.clip(fill, 0, 255).astype(np.uint8), (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    p = f'bcp_{n}a'
    enc((dx + 1) / 2, (dy + 1) / 2, cw).save(os.path.join(SRV, p + '_m1.webp'), lossless=True)
    enc(rw, n1, WD).save(os.path.join(SRV, p + '_m2.webp'), lossless=True)
    enc(FS, np.zeros_like(FS), n2).save(os.path.join(SRV, p + '_m3.webp'), lossless=True)
    Image.fromarray(f4).save(os.path.join(SRV, p + '_f.webp'), quality=92)
    u = {'src': R_['src'], 'deg': R_['deg'], 'pr': R_['period'], 'sh': R_['shimmer'], 'ps': R_['sh_period'], 'bands': R_['bands'],
         'a1': SM['a1'], 'a2': SM['a2'], 'p1': SM['p1'], 'p2': SM['p2'], 'wl': SM['wl'], 'c': [SM['cx'], SM['cy']], 'ramp': D.get('ramp', 1.5)}
    fg = f'bcp_{n}_fg.webp' if os.path.exists(os.path.join(ASSET, f'bcp_{n}_fg.webp')) else None
    allj[n] = {'bgx': f'bcp_{n}.webp', 'fgx': fg, 'layers': [], 'amb': {'m1': p + '_m1.webp', 'm2': p + '_m2.webp', 'm3': p + '_m3.webp', 'f': p + '_f.webp', 'u': u}}
    # しらべる 絵（動かない 所＝青・紙ふぶき＝桃）
    v = a * 0.6; v[T] = v[T] * 0.5 + np.array([0, 80, 255]) * 0.5; v[OBJ] = v[OBJ] * 0.4 + np.array([255, 0, 200]) * 0.6
    Image.fromarray(v.astype(np.uint8)).resize((585, 1266)).save(os.path.join(DBG, f'dbg_{n}_static.png'))
    print(n, 'static px', int(STAT.sum()), 'obj px', int(OBJ.sum()), 'files', [os.path.getsize(os.path.join(SRV, p + s)) // 1024 for s in ('_m1.webp', '_m2.webp', '_m3.webp', '_f.webp')], 'KB')
np.save(os.path.join(DBG, 'amb_maps.npy'), np.stack([rw, cw, WD, FS, dx, dy, n1, n2]).astype(np.float16))
json.dump(allj, open(D['stage_json'], 'w', encoding='utf8'), ensure_ascii=False, indent=1)
