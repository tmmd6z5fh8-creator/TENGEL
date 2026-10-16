"""2Dの毛（たてがみ・しっぽ）：房ごとに毛先が集まる・本数が多いほど濃い・毛先ほど光を通す"""
import math
import numpy as np
import cv2


def guide(p, ang, L, n, rng, flow, wave=1.0, phase=0.0):
    """房のガイドの線。flow(x, y, a, t) → 角度の変化"""
    pts = [np.array(p, float)]
    a = ang
    for k in range(n):
        t = k / n
        a += flow(pts[-1][0], pts[-1][1], a, t) + wave * math.sin(k * 0.45 + phase) * 0.06 + rng.normal(0, 0.03)
        pts.append(pts[-1] + np.array([math.cos(a), math.sin(a)]) * (L / n))
    return np.array(pts)


class HairBuf:
    """毛の本数（重なり）と、毛先の明るさの重みを ss 倍の細かさで描く"""

    def __init__(self, H, W, ss=2):
        self.H, self.W, self.ss = H, W, ss
        self.cnt = np.zeros((H * ss, W * ss), np.float32)
        self.rw = np.zeros((H * ss, W * ss), np.float32)

    def strand(self, c, width, rk):
        s = self.ss
        c = np.asarray(c, float) * s
        w = max(1, int(round(width * s)))
        x0, y0 = np.floor(c.min(0) - w - 2).astype(int)
        x1, y1 = np.ceil(c.max(0) + w + 2).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.W * s), min(y1, self.H * s)
        if x1 <= x0 or y1 <= y0:
            return
        a = np.zeros((y1 - y0, x1 - x0), np.float32)
        b = np.zeros_like(a)
        q = np.round((c - (x0, y0)) * 16).astype(np.int32)
        cv2.polylines(a, [q], False, 1.0, w, cv2.LINE_AA, shift=4)
        n = len(q)
        for j in range(n - 1):
            tt = j / max(1, n - 2)
            cv2.line(b, tuple(q[j]), tuple(q[j + 1]), float(rk * (0.3 + 0.7 * tt ** 0.8)), w, cv2.LINE_AA, shift=4)
        self.cnt[y0:y1, x0:x1] += a
        self.rw[y0:y1, x0:x1] += b

    def lock(self, g, n_strands, rng, spread, clump=0.75, wmin=0.6, wmax=1.5, rimk=1.0, tip_frac=(0.7, 1.0)):
        n = len(g)
        tang = np.gradient(g, axis=0)
        nr = np.stack([-tang[:, 1], tang[:, 0]], 1)
        nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-9
        t = np.linspace(0, 1, n)
        for k in range(n_strands):
            off = rng.normal(0, 1) * spread
            stray = rng.random() < 0.08
            prof = off * (1 - clump * t ** 1.4) + (rng.normal(0, 1) * spread * 1.8 * t ** 2 if stray else 0)
            wob = np.sin(t * rng.uniform(3, 9) + rng.uniform(0, 6)) * rng.uniform(0, 2.5) * t
            c = g + nr * (prof + wob)[:, None] + rng.normal(0, 0.35, g.shape)
            cut = max(3, int(n * rng.uniform(*tip_frac)))
            self.strand(c[:cut], rng.uniform(wmin, wmax), rng.uniform(0.4, 1.6) * rimk)

    def result(self, k=0.55):
        cnt = cv2.resize(self.cnt, (self.W, self.H), interpolation=cv2.INTER_AREA)
        rw = cv2.resize(self.rw, (self.W, self.H), interpolation=cv2.INTER_AREA)
        cov = 1 - np.exp(-cnt * k)
        rimw = rw / (cnt + 1e-4)
        return cov, rimw, cnt
