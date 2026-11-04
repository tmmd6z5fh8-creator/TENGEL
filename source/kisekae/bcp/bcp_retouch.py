# 結果ボードカスタム（絵の ボード）：まさちゃんの 絵の 一部を 消して 描き足す（まさちゃんの 指定の 直し）
#   python3 bcp_retouch.py <デザインの フォルダ>   → cfg['retouch'] の ops を 順に かけて out（ふつう src.png）。元の 絵は src（ふつう orig.png）
#   cfg['retouch'] = { src:'orig.png', out:'src.png', ops:[ … ] }
#   ops（形は 絵の px の 点の ならび。poly に minus:[形,…]（ひく）・clip:形（かさなる 所だけ）を つけられる。diffuse の src は 形 か 形の ならび）：
#     { op:'bg_radial', poly, c:[cx,cy], hole?, len:40, skip:3, vmax:250, exclude:[形,…], blur:1.2 }
#         光の すじの 背景で うめる：穴の 点から 光の まん中 c と 反対へ 進み、穴（hole：ない ときは poly）の 外に 出た 所から
#         len px の 色の 中央値（vmax より 明るい 所・exclude の 形の 中は のぞく）
#     { op:'bg_angular', poly, c:[cx,cy], band:[形,…], src?:[形,…] または ring:8, hole?, step:0.25, vmax:235, exclude:[形,…], src_exclude:[形,…] }
#         光の すじの 背景：band の 中の 色を まん中 c から 見た 角度ごとに 中央値（すじの もよう）→ 穴の まわりとの ちがいを なめらかに たす
#     { op:'diffuse', poly, src?:形, ring:25, gap:1, rule:{vmax, vmin, rmin, gmin, gmax, bmax, rb_min, br_min}, exclude:[形,…], noise:1.0 }
#         まわりの 色（src の 形の 中、または poly の まわり ring px の 中で rule に 合う 所）を 大きい ぼかし → 小さい ぼかしで かさねて うめる
#     { op:'clone', poly, dx, dy, flipx?:軸の x, feather:1.5 }  … poly の 中に (x-dx, y-dy) の 色を はる（flipx：軸で 左右を 入れかえた 色）
#     { op:'shade', poly, along:[点…], width:8, color:[r,g,b], alpha:0.35 }  … along の 線の 近く（poly の 中）を その 色へ
#     { op:'stroke', pts:[点…], width:3, color:[r,g,b], smooth:true }  … ふち線を 描く（なめらかな 線・AA）
#     { op:'glow', along:[点…], side:形, width:6, color:[r,g,b], alpha:0.4 }  … 線の 外がわ（side の 中）に ふちの 光
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
RT = cfg['retouch']
img = np.asarray(Image.open(os.path.join(D, RT.get('src', 'orig.png'))).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]


def poly_mask(pts):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts, np.float64) * 8).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=3)
    return m.astype(bool)


def smooth_pts(pts, n=24):
    """Catmull-Rom で 点の あいだを なめらかに"""
    P = np.array(pts, np.float64)
    if len(P) < 3:
        return P
    P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.array(out)


def line_alpha(pts, width, smooth=True):
    q = smooth_pts(pts) if smooth else np.array(pts, np.float64)
    c = np.zeros((H, W), np.uint8)
    cv2.polylines(c, [np.round(q * 16).astype(np.int32)], False, 255, thickness=max(1, int(round(width))), lineType=cv2.LINE_AA, shift=4)
    return c.astype(np.float32) / 255.0


def area(o):
    """poly − minus の 形 ∩ clip"""
    m = poly_mask(o['poly'])
    for q in o.get('minus', []):
        m &= ~poly_mask(q)
    if 'clip' in o:
        m &= poly_mask(o['clip'])
    return m


def op_bg_radial(o):
    global img
    m = area(o)
    hole = (poly_mask(o['hole']) if 'hole' in o else m) | m
    ex = np.zeros((H, W), bool)
    for e in o.get('exclude', []):
        ex |= poly_mask(e)
    cx, cy = o['c']
    ys, xs = np.nonzero(m)
    d = np.stack([xs - cx, ys - cy], 1).astype(np.float32)
    u = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
    t_exit = np.zeros(len(xs), np.float32); done = np.zeros(len(xs), bool)
    for t in range(1, 800):
        px = np.round(xs + u[:, 0] * t).astype(int); py = np.round(ys + u[:, 1] * t).astype(int)
        inb = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        out = ~done & (~inb | ~hole[np.clip(py, 0, H - 1), np.clip(px, 0, W - 1)])
        t_exit[out] = t; done |= out
        if done.all():
            break
    skip, ln = o.get('skip', 3), o.get('len', 40)
    S = []; OK = []
    for k in range(ln):
        t = t_exit + skip + k
        px = np.round(xs + u[:, 0] * t).astype(int); py = np.round(ys + u[:, 1] * t).astype(int)
        inb = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        px = np.clip(px, 0, W - 1); py = np.clip(py, 0, H - 1)
        c = img[py, px]
        S.append(c); OK.append(inb & (c.max(-1) <= o.get('vmax', 250)) & ~ex[py, px] & ~hole[py, px])
    S = np.stack(S, 1); OK = np.stack(OK, 1)
    Sm = np.where(OK[..., None], S, np.nan)
    with np.errstate(all='ignore'):
        col = np.nanmedian(Sm, axis=1)
    bad = np.isnan(col).any(1)
    if bad.any():
        col[bad] = np.median(S[bad], 1)
    out = img.copy(); out[ys, xs] = col
    sm = cv2.GaussianBlur(out, (0, 0), o.get('blur', 1.2))
    out[ys, xs] = sm[ys, xs]
    img = out


def _diffuse_field(field, w, m):
    """w（色の もと）の 値を 大きい ぼかし → 小さい ぼかしで m の 中へ"""
    acc = None
    for sg in (48, 24, 12, 6, 3, 1.5):
        num = cv2.GaussianBlur(field * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
        f = num / np.maximum(den, 1e-6)[..., None]
        conf = np.clip(den / 0.3, 0, 1)[..., None]
        acc = f if acc is None else acc * (1 - conf) + f * conf
    return acc


def op_bg_angular(o):
    """光の すじ（まん中 c から 広がる）の 背景で うめる：band の 中の 色を 角度ごとの 中央値に して（すじの もよう）、
    穴の まわりとの ちがいは なめらかに なじませる（さかい目が 出ない）"""
    global img
    m = area(o)
    cx, cy = o['c']
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    phi = np.degrees(np.arctan2(yy - cy, xx - cx))
    band = np.zeros((H, W), bool)
    for q in o['band']:
        band |= poly_mask(q)
    V = img.max(-1)
    band &= ~m & (V <= o.get('vmax', 235)) & (V >= o.get('vmin', 0))
    for e in o.get('exclude', []):
        band &= ~poly_mask(e)
    step = o.get('step', 0.25)
    ph = phi[band]; cols = img[band]
    lo, hi = ph.min(), ph.max()
    nb = int(np.ceil((hi - lo) / step)) + 1
    idx = np.clip(((ph - lo) / step).astype(int), 0, nb - 1)
    prof = np.full((nb, 3), np.nan, np.float32)
    for b in range(nb):
        sel = idx == b
        if sel.sum() >= 3:
            prof[b] = np.median(cols[sel], 0)
    ok = ~np.isnan(prof[:, 0]); xs_ = np.arange(nb)
    for c in range(3):
        prof[:, c] = np.interp(xs_, xs_[ok], prof[ok, c])
    prof = ndi.gaussian_filter1d(prof, o.get('psmooth', 2.0), axis=0)
    pidx = np.clip((phi - lo) / step, 0, nb - 1)
    P = np.stack([np.interp(pidx.ravel(), xs_, prof[:, c]).reshape(H, W) for c in range(3)], -1)
    # 穴の まわり（ring・src）との ちがいを なめらかに
    if 'src' in o:
        w = np.zeros((H, W), bool)
        for q in o['src']:
            w |= poly_mask(q)
    else:
        w = ndi.binary_dilation(m, iterations=o.get('ring', 8))
    w &= ~ndi.binary_dilation(m, iterations=1) & (V <= o.get('vmax', 235))
    if 'hole' in o:
        w &= ~poly_mask(o['hole'])                  # 穴の 中（まだ 消す 前の 絵）は 色の もとに しない
    for e in o.get('exclude', []) + o.get('src_exclude', []):
        w &= ~poly_mask(e)
    corr = _diffuse_field(img - P, w.astype(np.float32), m)
    fill = P + corr * o.get('corr', 1.0)
    nz = o.get('noise', 1.0)
    if nz:
        fill += cv2.GaussianBlur(np.random.default_rng(5).normal(0, nz, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
    img = np.where(m[..., None], fill, img)


def op_diffuse(o):
    global img
    m = area(o)
    if 'src' in o:
        srcm = np.zeros((H, W), bool)
        for q in (o['src'] if isinstance(o['src'][0][0], (list, tuple)) else [o['src']]):
            srcm |= poly_mask(q)
    else:
        srcm = ndi.binary_dilation(m, iterations=o.get('ring', 25))
    srcm &= ~ndi.binary_dilation(m, iterations=o.get('gap', 1))
    for e in o.get('exclude', []):
        srcm &= ~poly_mask(e)
    r = o.get('rule', {}); R, G, B = img[..., 0], img[..., 1], img[..., 2]; V = img.max(-1)
    if 'vmax' in r: srcm &= V <= r['vmax']
    if 'vmin' in r: srcm &= V >= r['vmin']
    if 'rmin' in r: srcm &= R >= r['rmin']
    if 'gmin' in r: srcm &= G >= r['gmin']
    if 'gmax' in r: srcm &= G <= r['gmax']
    if 'bmax' in r: srcm &= B <= r['bmax']
    if 'rb_min' in r: srcm &= (R - B) >= r['rb_min']
    if 'br_min' in r: srcm &= (B - R) >= r['br_min']        # 紺（青が 赤より 強い）だけ：馬の ふち線の 黒・布の かげは 入れない
    w = srcm.astype(np.float32)
    acc = None
    for sg in (48, 24, 12, 6, 3, 1.5):
        num = cv2.GaussianBlur(img * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
        f = num / np.maximum(den, 1e-6)[..., None]
        conf = np.clip(den / 0.3, 0, 1)[..., None]
        acc = f if acc is None else acc * (1 - conf) + f * conf
    nz = o.get('noise', 1.0)
    if nz:
        acc += cv2.GaussianBlur(np.random.default_rng(3).normal(0, nz, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
    img = np.where(m[..., None], acc, img)


def op_clone(o):
    global img
    m = area(o)
    if 'flipx' in o:
        ax = float(o['flipx'])
        xs = (2 * ax - np.arange(W, dtype=np.float32))
        mx = np.tile(xs - o.get('dx', 0), (H, 1)).astype(np.float32)
    else:
        mx = np.tile(np.arange(W, dtype=np.float32) - o['dx'], (H, 1))
    my = np.tile((np.arange(H, dtype=np.float32) - o.get('dy', 0))[:, None], (1, W))
    src = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), o.get('feather', 1.5)) if o.get('feather', 1.5) else m.astype(np.float32)
    if o.get('inside', True):
        a = a * ndi.binary_dilation(m, iterations=2)
    img = img * (1 - a[..., None]) + src * a[..., None]


def op_shade(o):
    global img
    m = area(o)
    ln = line_alpha(o['along'], 1, o.get('smooth', True)) > 0.3
    dist = ndi.distance_transform_edt(~ln)
    a = o.get('alpha', 0.35) * np.clip(1 - dist / o.get('width', 8), 0, 1) * m
    a = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 1.0)
    img = img * (1 - a[..., None]) + np.array(o['color'], np.float32) * a[..., None]


def op_stroke(o):
    global img
    a = line_alpha(o['pts'], o.get('width', 3), o.get('smooth', True)) * o.get('alpha', 1.0)
    img = img * (1 - a[..., None]) + np.array(o['color'], np.float32) * a[..., None]


def op_glow(o):
    global img
    side = poly_mask(o['side'])
    ln = line_alpha(o['along'], 1, o.get('smooth', True)) > 0.3
    dist = ndi.distance_transform_edt(~ln)
    a = o.get('alpha', 0.4) * np.clip(1 - dist / o.get('width', 6), 0, 1) ** 1.5 * side
    a = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 1.2)
    img = img * (1 - a[..., None]) + np.array(o['color'], np.float32) * a[..., None]


OPS = {'bg_radial': op_bg_radial, 'bg_angular': op_bg_angular, 'diffuse': op_diffuse, 'clone': op_clone, 'shade': op_shade, 'stroke': op_stroke, 'glow': op_glow}
for i, o in enumerate(RT['ops']):
    OPS[o['op']](o)
    print('retouch', i, o['op'], o.get('note', ''))
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(D, RT.get('out', 'src.png')))
