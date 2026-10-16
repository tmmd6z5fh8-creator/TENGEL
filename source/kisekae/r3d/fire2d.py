"""炎・火の粉・ぼけた光の粒を描く道具（線形の明るさで返す）"""
import math, os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from paint import fbm, warp, blur, smoothstep

# 炎の色（線形・明るいほど白く）
FIRE_STOPS = [(0.0, (0, 0, 0)), (0.12, (0.10, 0.012, 0.002)), (0.3, (0.55, 0.09, 0.01)), (0.5, (1.4, 0.38, 0.05)),
              (0.7, (2.6, 1.15, 0.22)), (0.86, (4.0, 2.6, 0.9)), (1.0, (6.0, 5.0, 3.2))]


def fire_color(h, stops=FIRE_STOPS):
    xs = np.array([s[0] for s in stops], np.float32)
    out = np.zeros(h.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(h, xs, np.array([s[1][c] for s in stops], np.float32))
    return out


def flow_path(p, ang, L, n, rng, wave=1.0, phase=0.0, turn=0.0, curl=0.0, rise=0.0, jitter=0.05):
    """炎のすじの道すじ（画像の座標・yは下向き・上は -90°）"""
    pts = [np.array(p, float)]
    a = ang
    for k in range(n):
        t = k / n
        a += turn + curl * t + wave * math.sin(k * 0.55 + phase) * 0.12 + rng.normal(0, jitter)
        a += rise * math.sin(-math.pi / 2 - a) * 0.10
        pts.append(pts[-1] + np.array([math.cos(a), math.sin(a)]) * (L / n))
    return np.array(pts)


class Heat:
    def __init__(self, H, W, ss=2):
        self.H, self.W, self.ss = H, W, ss
        self.buf = np.zeros((H * ss, W * ss), np.float32)

    def lock(self, c, w0, peak=1.0, tip=1.0, root_taper=0.12, power=1.15):
        """先が細くなる炎のすじを1本描く（最大値で重ねる）"""
        s = self.ss
        c = np.asarray(c, float) * s
        w0 = w0 * s
        x0, y0 = np.floor(c.min(0) - w0 - 2).astype(int)
        x1, y1 = np.ceil(c.max(0) + w0 + 2).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.W * s), min(y1, self.H * s)
        if x1 <= x0 or y1 <= y0:
            return
        sub = np.zeros((y1 - y0, x1 - x0), np.float32)
        n = len(c)
        for k in range(n - 2, -1, -1):
            t = k / (n - 1)
            w = w0 * ((1 - t) ** 0.85) * (0.55 + 0.45 * smoothstep(0, root_taper, t)) * (1 - (1 - tip) * t)
            v = peak * (1 - t) ** power
            q = np.round((np.array([c[k], c[k + 1]]) - (x0, y0)) * 16).astype(np.int32)
            cv2.line(sub, tuple(q[0]), tuple(q[1]), float(v), int(max(1, round(w))), cv2.LINE_AA, shift=4)
        np.maximum(self.buf[y0:y1, x0:x1], sub, out=self.buf[y0:y1, x0:x1])

    def result(self, turb=26, fine=10, seed=0, breakup=0.55, up=6):
        """ゆらぎ・ちぎれを加えて、元の大きさの熱（0〜1）を返す"""
        h = cv2.resize(self.buf, (self.W, self.H), interpolation=cv2.INTER_AREA)
        H, W = self.H, self.W
        h = blur(h, 1.0)
        dx = (fbm(H, W, 60, 4, seed=seed + 1) - .5) * turb + (fbm(H, W, 16, 3, seed=seed + 2) - .5) * fine
        dy = (fbm(H, W, 60, 4, seed=seed + 3) - .5) * turb + (fbm(H, W, 16, 3, seed=seed + 4) - .5) * fine + up
        h = warp(h, dx, dy)
        nz = fbm(H, W, 22, 4, seed=seed + 5)
        h = h * (1 - breakup + breakup * 2 * nz)
        return np.clip(h, 0, 1.2)


def bokeh(H, W, n, rng, rmin=3, rmax=18, cols=((1.0, 0.6, 0.18), (1.0, 0.75, 0.3), (0.9, 0.4, 0.08)), ymax=1.0, inten=(0.08, 0.5), avoid=None):
    """ぼけた光の丸（線形）"""
    out = np.zeros((H, W, 3), np.float32)
    for i in range(n):
        x = rng.uniform(0, W); y = rng.uniform(0, H * ymax)
        r = rng.uniform(rmin, rmax) * (rng.random() ** 1.5 * 0.7 + 0.3)
        c = np.array(cols[rng.integers(0, len(cols))]) * rng.uniform(*inten)
        x0, y0, x1, y1 = int(max(x - r - 3, 0)), int(max(y - r - 3, 0)), int(min(x + r + 4, W)), int(min(y + r + 4, H))
        if x1 <= x0 or y1 <= y0: continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        disc = np.clip((r - d) / 1.5 + .5, 0, 1) * (0.75 + 0.25 * np.clip(d / r, 0, 1) ** 2)
        out[y0:y1, x0:x1] += disc[..., None] * c
    return out


def sparks(H, W, n, rng, region=None, streak=(0, -1), slen=(2, 10), inten=(1.0, 4.0)):
    """火の粉（小さな明るい点と、上へ流れる尾）"""
    acc = np.zeros((H * 2, W * 2), np.float32)
    for i in range(n):
        if region is not None:
            x, y = region(rng)
        else:
            x, y = rng.uniform(0, W), rng.uniform(0, H)
        L = rng.uniform(*slen)
        dx = streak[0] + rng.normal(0, .35); dy = streak[1]
        nn = math.hypot(dx, dy)
        x2, y2 = x + dx / nn * L, y + dy / nn * L
        v = rng.uniform(*inten)
        cv2.line(acc, (int(x * 32), int(y * 32)), (int(x2 * 32), int(y2 * 32)), float(v), 1, cv2.LINE_AA, shift=4)
        cv2.circle(acc, (int(x * 32), int(y * 32)), int(rng.uniform(.6, 1.4) * 32), float(v * 1.2), -1, cv2.LINE_AA, shift=4)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_AREA)
    return acc


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    x = np.maximum(x, 0)
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


GOLD_STOPS = [(0.0, (0, 0, 0)), (0.2, (0.06, 0.025, 0.004)), (0.45, (0.45, 0.20, 0.03)), (0.7, (1.4, 0.80, 0.18)),
              (0.88, (2.6, 1.8, 0.6)), (1.0, (4.0, 3.2, 1.6))]


def dust(H, W, n, rng, pos, size=(0.5, 2.2), inten=(0.3, 2.0)):
    """丸い光の粒（金の粉・火の粉）。pos(rng) → (x, y)"""
    acc = np.zeros((H * 2, W * 2), np.float32)
    big = np.zeros((H, W), np.float32)
    for i in range(n):
        x, y = pos(rng)
        if not (0 <= x < W and 0 <= y < H):
            continue
        r = rng.uniform(*size) * (rng.random() ** 2 * 0.8 + 0.2) * 1.4
        v = rng.uniform(*inten)
        cv2.circle(acc, (int(x * 32), int(y * 32)), max(1, int(r * 32)), float(v), -1, cv2.LINE_AA, shift=4)
        if rng.random() < 0.18:
            cv2.circle(big, (int(x * 16), int(y * 16)), int(r * 2.2 * 16), float(v * 0.25), -1, cv2.LINE_AA, shift=4)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_AREA)
    return acc + blur(acc, 1.6) * 0.8 + blur(big, 3.0) + blur(acc, 6.0) * 0.5
