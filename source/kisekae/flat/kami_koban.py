"""金の 小判（第4.50版：まさちゃん「小石のようなエフェクトは全てリアルな小判に変えて！」）
   本物の 慶長小判の つくり：たて長の だ円・表と 裏 いっぱいの 茣蓙目（横の すじ：たがねで 打った 少し ゆれた 線）・
   表：上と 下に 扇の わくの 桐の 紋・まん中の 上に「壹两」・下に「光次」と 花押（どれも 打ちこんだ 極印＝くぼんだ 枠の 中に もり上がった 形）・
   裏：まん中に 花押・下の 左右に 小さな 丸い 極印。
   桐の 紋と 花押の 形は 姫の 絵（本物の 写しでは ない）。字は Noto Sans CJK（太い ゴシックを 打ちこみの 形に して やわらかく）
   → 高さの 絵 → 法線（nx, ny）と くぼみ（cav）を 細かさ 5段で（小さく 写る 時は あらい 段：すじが ちらつかない）
   koban(i) → dict(front=[段…], back=[段…], TW, TH)。段＝(H, W, 4)：(alpha, alpha·nx, alpha·ny, alpha·cav)"""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

TW, TH = 384, 720                  # 絵の 大きさ（はば / 高さ ≈ .53：慶長小判の 形）
SHAPE_P = 2.15                     # だ円の 形（2＝だ円・大きい ほど 四角に 近い）
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
LINES = 44                         # 茣蓙目の すじの 数（たて 1枚で）


def _rng(seed):
    return np.random.default_rng(seed)


def _coords():
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    u = (xx + .5 - TW / 2) / (TW / 2 * .985)
    v = (yy + .5 - TH / 2) / (TH / 2 * .985)
    r = (np.abs(u) ** SHAPE_P + np.abs(v) ** SHAPE_P) ** (1 / SHAPE_P)
    return xx, yy, u, v, r


def _ss_mask(draw_fn, w, h, ss=4):
    """細かく 描いて 小さく（なめらかな ふち）"""
    im = Image.new('L', (w * ss, h * ss), 0)
    draw_fn(ImageDraw.Draw(im), ss)
    a = np.asarray(im, np.float32) / 255
    return cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)


def _glyph_col(chars, px, gap=.94):
    """字を たてに ならべた 形（0〜1）"""
    font = ImageFont.truetype(FONT, int(px * 4), index=0)
    w = int(px * 1.1)
    h = int(px * (gap * (len(chars) - 1) + 1.1))

    def f(d, ss):
        for i, c in enumerate(chars):
            bb = d.textbbox((0, 0), c, font=font)
            cw, ch = bb[2] - bb[0], bb[3] - bb[1]
            x = (w * ss - cw) / 2 - bb[0]
            y = (i * gap * px + .55 * px) * ss - ch / 2 - bb[1]
            d.text((x, y), c, font=font, fill=255)
    return _ss_mask(f, w, h)


def _kiri(w, h):
    """桐の 紋（姫の 形）：下に 3まいの 葉・上に 3本の 花の 穂（まん中 5つ・左右 3つの つぼみ）"""
    def f(d, ss):
        def P(x, y):
            return (x * w * ss, y * h * ss)

        def leaf(cx, cy, L, Wd, ang):
            a = math.radians(ang)
            pts = []
            for t in np.linspace(0, 2 * math.pi, 40):
                x0, y0 = Wd / 2 * math.sin(t) * (1 - .25 * math.cos(t)), -L / 2 * math.cos(t)
                pts.append(P(cx + x0 * math.cos(a) - y0 * math.sin(a), cy + x0 * math.sin(a) + y0 * math.cos(a)))
            d.polygon(pts, fill=255)
        leaf(.5, .79, .34, .22, 0)
        leaf(.27, .73, .3, .19, 38)
        leaf(.73, .73, .3, .19, -38)
        for (x0, y0, x1, y1, nb, rb) in ((.5, .6, .5, .1, 5, .052), (.29, .6, .2, .22, 3, .048), (.71, .6, .8, .22, 3, .048)):
            d.line([P(x0, y0), P(x1, y1)], fill=255, width=int(.035 * w * ss))
            for k in range(nb):
                t = (k + .5) / nb
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                off = (.045 if k % 2 else -.045) * (1 if nb == 5 else .8)
                d.ellipse([P(x + off - rb * .75, y - rb), P(x + off + rb * .75, y + rb)], fill=255)
    a = _ss_mask(f, w, h)
    # 葉の すじ（細い みぞ）
    def g(d, ss):
        for (x0, y0, x1, y1) in ((.5, .64, .5, .93), (.33, .64, .2, .82), (.67, .64, .8, .82)):
            d.line([(x0 * w * ss, y0 * h * ss), (x1 * w * ss, y1 * h * ss)], fill=255, width=max(1, int(.018 * w * ss)))
    vein = _ss_mask(g, w, h)
    return np.clip(a - .7 * vein, 0, 1)


def _fan(w, h):
    """扇の わく（上が ひろい 扇の 形）→ (わくの 中, わくの 線)"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h * 2.05
    R2, R1 = h * 2.0, h * 1.02
    rr = np.hypot(xx - cx, yy - cy)
    th = np.degrees(np.arctan2(xx - cx, cy - yy))
    half = math.degrees(math.asin(min(.99, (w / 2 * .96) / R2)))
    inside = (rr < R2) & (rr > R1) & (np.abs(th) < half)
    f = cv2.GaussianBlur(inside.astype(np.float32), (0, 0), .8)
    d = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 3)
    line = np.exp(-((d - 3.2) / 1.1) ** 2) * inside
    return f, line


def _kao(w, h, seed, thick=.075):
    """花押（姫の 形：横に のびる 線と 輪・たての 線）"""
    rng = _rng(seed)
    base = [(.08, .58), (.3, .38), (.52, .3), (.64, .5), (.48, .72), (.3, .62), (.5, .5), (.8, .44), (.95, .5)]
    pts = [(x + rng.uniform(-.02, .02), y + rng.uniform(-.03, .03)) for x, y in base]

    def cr(p, n=16):
        out = []
        p = [p[0]] + p + [p[-1]]
        for i in range(1, len(p) - 2):
            p0, p1, p2, p3 = map(np.array, (p[i - 1], p[i], p[i + 1], p[i + 2]))
            for t in np.linspace(0, 1, n, endpoint=False):
                out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        out.append(np.array(p[-2]))
        return out

    def f(d, ss):
        cur = cr(pts)
        for i in range(len(cur) - 1):
            u = i / (len(cur) - 1)
            wd = thick * w * ss * (.55 + .7 * math.sin(math.pi * min(1.0, u * 1.2)))
            d.line([(cur[i][0] * w * ss, cur[i][1] * h * ss), (cur[i + 1][0] * w * ss, cur[i + 1][1] * h * ss)], fill=255, width=max(1, int(wd)))
            r = wd / 2
            d.ellipse([cur[i][0] * w * ss - r, cur[i][1] * h * ss - r, cur[i][0] * w * ss + r, cur[i][1] * h * ss + r], fill=255)
        d.line([(.6 * w * ss, .12 * h * ss), (.56 * w * ss, .9 * h * ss)], fill=255, width=int(thick * .9 * w * ss))
    return _ss_mask(f, w, h)


def _place(dst, src, cx, cy):
    """src を dst の (cx, cy) を まん中に 置く（大きい 方を とる）"""
    h, w = src.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    dst[ys0:ys1, xs0:xs1] = np.maximum(dst[ys0:ys1, xs0:xs1], src[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0])


def _rrect(w, h, rad):
    def f(d, ss):
        d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=rad * ss, fill=255)
    return _ss_mask(f, w, h)


def _stamp(field, motif, frame_w=0.0):
    """極印：くぼんだ 枠（field）の 中に もり上がった 形（motif）・枠の 内に 細い 線（frame_w>0）"""
    f = cv2.GaussianBlur(field, (0, 0), 1.0)
    m = motif
    if frame_w > 0:
        d = cv2.distanceTransform((field > .5).astype(np.uint8), cv2.DIST_L2, 3)
        m = np.maximum(m, np.exp(-((d - 3.0) / frame_w) ** 2) * (field > .5))
    m = cv2.GaussianBlur(m, (0, 0), .7)
    return f, m


def _surface(seed, side):
    xx, yy, u, v, r = _coords()
    rng = _rng(seed)
    # 茣蓙目（少し ゆれた 横の すじ・深さは 1本ずつ ちがう）
    vv = (yy + .5) / TH
    uu = (xx + .5) / TW
    ph1, ph2 = rng.uniform(0, 6.3, 2)
    wav = .0024 * np.sin(2 * math.pi * uu * 1.3 + ph1) + .0012 * np.sin(2 * math.pi * (uu * 3.3 + vv * 2.1) + ph2)
    nz = cv2.resize(rng.normal(size=(12, 7)).astype(np.float32), (TW, TH), interpolation=cv2.INTER_CUBIC)
    phase = (vv + wav + .0014 * nz) * LINES
    k = np.floor(phase).astype(np.int32)
    fr = phase - k
    dep = (1.05 + .45 * rng.random(LINES + 4))[np.clip(k, 0, LINES + 3)]
    groove = np.exp(-((fr - .5) / .17) ** 2) * dep
    fade = 1 - np.clip((r - .9) / .075, 0, 1)
    h = -1.35 * groove * fade
    # 細かい 打ちあと
    h += .25 * cv2.GaussianBlur(rng.normal(size=(TH, TW)).astype(np.float32), (0, 0), 1.6)
    # ふくらみ と まるい ふち
    h += 14.0 * (1 - np.clip(r, 0, 1) ** 2)
    h -= 10.0 * np.clip((r - .95) / .05, 0, 1) ** 2
    # 極印
    stamps = []
    if side == 'front':
        fw_, fh_ = int(TW * .44), int(TH * .14)
        ff, fl = _fan(fw_, fh_)
        kr = _kiri(int(fw_ * .5), int(fh_ * .82))
        km = np.zeros((fh_, fw_), np.float32)
        _place(km, kr, fw_ / 2, fh_ * .52)
        for cy in (TH * .14, TH * .86):
            F = np.zeros((TH, TW), np.float32)
            M = np.zeros((TH, TW), np.float32)
            _place(F, ff, TW / 2, cy)
            _place(M, np.maximum(km * ff, fl), TW / 2, cy)
            stamps.append(_stamp(F, M))
        g1 = _glyph_col('壹两', TW * .18)
        F = np.zeros((TH, TW), np.float32)
        M = np.zeros((TH, TW), np.float32)
        _place(F, _rrect(g1.shape[1] + 22, g1.shape[0] + 18, 10), TW / 2, TH * .352)
        _place(M, g1, TW / 2, TH * .352)
        stamps.append(_stamp(F, M, 1.0))
        g2 = _glyph_col('光次', TW * .15)
        kao = _kao(int(TW * .3), int(TH * .075), seed + 5)
        col = np.zeros((g2.shape[0] + kao.shape[0] + 4, max(g2.shape[1], kao.shape[1])), np.float32)
        _place(col, g2, col.shape[1] / 2, g2.shape[0] / 2)
        _place(col, kao, col.shape[1] / 2, g2.shape[0] + 4 + kao.shape[0] / 2)
        F = np.zeros((TH, TW), np.float32)
        M = np.zeros((TH, TW), np.float32)
        _place(F, _rrect(col.shape[1] + 20, col.shape[0] + 16, 10), TW / 2, TH * .652)
        _place(M, col, TW / 2, TH * .652)
        stamps.append(_stamp(F, M, 1.0))
    else:
        kao = _kao(int(TW * .56), int(TH * .2), seed + 9, .085)
        F = np.zeros((TH, TW), np.float32)
        M = np.zeros((TH, TW), np.float32)
        fld = cv2.GaussianBlur(cv2.dilate((kao > .3).astype(np.float32), np.ones((15, 15), np.uint8)), (0, 0), 3.0)
        _place(F, np.clip(fld * 1.4, 0, 1), TW / 2, TH * .5)
        _place(M, kao, TW / 2, TH * .5)
        stamps.append(_stamp(F, M))
        for cx, c in ((TW * .36, '大'), (TW * .64, '吉')):
            rr_ = int(TW * .055)
            circ = _ss_mask(lambda d, ss: d.ellipse([0, 0, 2 * rr_ * ss - 1, 2 * rr_ * ss - 1], fill=255), 2 * rr_, 2 * rr_)
            g = _glyph_col(c, rr_ * 1.25)
            F = np.zeros((TH, TW), np.float32)
            M = np.zeros((TH, TW), np.float32)
            _place(F, circ, cx, TH * .8)
            _place(M, g, cx, TH * .8)
            stamps.append(_stamp(F, M, .9))
    for F, M in stamps:
        base = cv2.GaussianBlur(h, (0, 0), 6.0)                     # 枠の 中は すじを 消して 平らに
        h = h * (1 - F) + F * (base - 1.5 + 1.75 * M)
    alpha = 1 - np.clip((r - .996) / .008, 0, 1)
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), .6)
    hx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    hy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    cav = np.clip((cv2.GaussianBlur(h, (0, 0), 3.0) - h) / 1.6, 0, 1)
    wear = cv2.GaussianBlur(rng.normal(size=(TH // 8, TW // 8)).astype(np.float32), (0, 0), 1.2)
    cav = np.clip(cav + .12 * cv2.resize(wear, (TW, TH), interpolation=cv2.INTER_CUBIC), 0, 1)
    a = alpha.astype(np.float32)
    m4 = np.dstack([a, a * -hx, a * -hy, a * cav]).astype(np.float32)
    lv = [m4]
    for _ in range(4):
        hh, ww = lv[-1].shape[:2]
        lv.append(cv2.resize(lv[-1], (max(1, ww // 2), max(1, hh // 2)), interpolation=cv2.INTER_AREA))
    return lv


def koban(i=0):
    """小判 1しゅ（i で 打ちあとが 少し ちがう）"""
    return dict(front=_surface(1200 + i * 31, 'front'), back=_surface(1300 + i * 31, 'back'), TW=TW, TH=TH)


def outline(n=56):
    """ふちの 点（だ円：はば・高さ 1 に した 座標）と 外向き"""
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    x = np.sign(c) * np.abs(c) ** (2 / SHAPE_P)
    y = np.sign(s) * np.abs(s) ** (2 / SHAPE_P)
    nx = np.sign(c) * np.abs(c) ** (2 - 2 / SHAPE_P)
    ny = np.sign(s) * np.abs(s) ** (2 - 2 / SHAPE_P)
    nn = np.hypot(nx, ny) + 1e-9
    return np.stack([x, y], 1), np.stack([nx / nn, ny / nn], 1)
