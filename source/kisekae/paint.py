"""絵を描く道具（OpenCV＋numpy）：なめらかな形・手足・ノイズ（雲・煙・炎）・光（ふちの光・つや）・ぼかし・合成"""
import math
import numpy as np
import cv2


# ---------- 形 ----------
def cr(pts, closed=True, n=14):
    """Catmull-Rom で点を通るなめらかな線（点の列）を返す"""
    P = [np.array(p, np.float64) for p in pts]
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[i + 1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append(q)
    if not closed:
        out.append(P[-1])
    return np.array(out)


def limb(pts, widths, n=10, cap=True):
    """骨（点の列）に太さをつけた形（輪郭の点の列）"""
    c = cr(pts, closed=False, n=n)
    # 太さを骨の長さに沿って補間
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.array(pts, float), axis=0), axis=1))]
    cl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    w = np.interp(cl / cl[-1] * seg[-1], seg, widths)
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    L = c + nrm * (w[:, None] / 2)
    R = c - nrm * (w[:, None] / 2)
    ring = [L]
    if cap:
        a0 = math.atan2(d[-1, 1], d[-1, 0])
        arc = [c[-1] + np.array([math.cos(a0 + math.pi / 2 - t), math.sin(a0 + math.pi / 2 - t)]) * w[-1] / 2 for t in np.linspace(0, math.pi, 9)]
        ring.append(np.array(arc))
    ring.append(R[::-1])
    if cap:
        a0 = math.atan2(-d[0, 1], -d[0, 0])
        arc = [c[0] + np.array([math.cos(a0 + math.pi / 2 - t), math.sin(a0 + math.pi / 2 - t)]) * w[0] / 2 for t in np.linspace(0, math.pi, 9)]
        ring.append(np.array(arc))
    return np.concatenate(ring)


def ellipse(cx, cy, rx, ry, rot=0, n=48):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x, y = rx * np.cos(t), ry * np.sin(t)
    r = math.radians(rot)
    return np.stack([cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)], 1)


def xform(poly, s=1.0, tx=0.0, ty=0.0, flip_w=None):
    p = np.array(poly, np.float64) * s
    if flip_w is not None:
        p[:, 0] = flip_w - p[:, 0]
    p[:, 0] += tx
    p[:, 1] += ty
    return p


def fill(mask, polys, val=1.0):
    """形を塗る（なめらかなふち）。mask は float32 0〜1"""
    h, w = mask.shape
    tmp = np.zeros((h, w), np.uint8)
    for p in polys:
        q = np.round(np.asarray(p) * 16).astype(np.int32)
        cv2.fillPoly(tmp, [q], 255, lineType=cv2.LINE_AA, shift=4)
    m = tmp.astype(np.float32) / 255.0
    np.maximum(mask, m * val, out=mask)
    return mask


def strokes(mask, lines, width, val=1.0, taper=True):
    """細い線（毛）をたくさん描く。lines は点の列のリスト"""
    h, w = mask.shape
    tmp = np.zeros((h, w), np.uint8)
    for ln in lines:
        ln = np.asarray(ln)
        k = len(ln)
        for i in range(k - 1):
            t = i / max(1, k - 2)
            wd = max(1, int(round(width * ((1 - t) if taper else 1) + 0.6)))
            a = tuple(np.round(ln[i] * 16).astype(int))
            b = tuple(np.round(ln[i + 1] * 16).astype(int))
            cv2.line(tmp, a, b, 255, wd, lineType=cv2.LINE_AA, shift=4)
    m = tmp.astype(np.float32) / 255.0
    np.maximum(mask, m * val, out=mask)
    return mask


# ---------- ノイズ ----------
def fbm(h, w, scale=200, octaves=6, seed=0, persistence=0.55):
    """なめらかなノイズ（雲・煙・炎のもと）0〜1"""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    s = scale
    for o in range(octaves):
        gh, gw = max(2, int(h / s) + 3), max(2, int(w / s) + 3)
        g = rng.random((gh, gw)).astype(np.float32)
        up = cv2.resize(g, (int(gw * s), int(gh * s)), interpolation=cv2.INTER_CUBIC)
        ox, oy = rng.integers(0, max(1, up.shape[1] - w)), rng.integers(0, max(1, up.shape[0] - h))
        acc += up[oy:oy + h, ox:ox + w] * amp
        tot += amp
        amp *= persistence
        s /= 2.0
        if s < 1.5:
            break
    acc /= tot
    acc -= acc.min()
    acc /= acc.max() + 1e-9
    return acc


def warp(img, dx, dy):
    h, w = img.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx + dx.astype(np.float32), gy + dy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------- 光・色 ----------
def blur(img, sigma):
    if sigma <= 0:
        return img
    k = int(sigma * 3) * 2 + 1
    return cv2.GaussianBlur(img, (k, k), sigma)


def ramp(x, stops):
    """0〜1 の値を色の段で色にする。stops=[(位置, (r,g,b)), …]（0〜255）"""
    xs = np.array([s[0] for s in stops], np.float32)
    out = np.zeros(x.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(x, xs, np.array([s[1][c] for s in stops], np.float32)) / 255.0
    return out


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def height_from_mask(mask, r1=6, r2=26):
    """形のふくらみ（ふちが低く、内側が高い）"""
    m = (mask > 0.5).astype(np.uint8)
    d = cv2.distanceTransform(m, cv2.DIST_L2, 5).astype(np.float32)
    h = 1 - np.exp(-d / r2)
    h = blur(h, r1)
    return h * mask


def normals(height, strength=40.0):
    gx = cv2.Sobel(height, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(height, cv2.CV_32F, 0, 1, ksize=3)
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(height)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / ln, ny / ln, nz / ln


def screen(a, b):
    return 1 - (1 - a) * (1 - b)


def over(dst, src, alpha):
    a = alpha[..., None] if alpha.ndim == 2 else alpha
    return dst * (1 - a) + src * a


def bloom(img, thr=0.7, sigma=18, k=0.6):
    lum = img.max(axis=2)
    b = img * smoothstep(thr, 1.0, lum)[..., None]
    return screen(img, blur(b, sigma) * k)


def grain(img, amt=0.03, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, img.shape[:2]).astype(np.float32)[..., None]
    return np.clip(img + n, 0, 1)


def save(img, path, q=88):
    u8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, q] if path.endswith('.jpg') else [])
