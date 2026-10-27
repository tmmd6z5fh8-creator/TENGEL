"""お正月の 羊の 着ぐるみ（第4.90版・まさちゃん「来年は羊年だから、この馬に羊の着ぐるみを被せてほしい！」）
   馬（flat/horse_flat.py の draw_horse）の 目印から：
   - もこもこの 体（首・胴・ももの 上まで）：馬の 体の 形から 足と 顔を のぞいた 所。ふちは 丸い もこもこが 体の 外へ はみ出す
   - フード：頭の うしろ（目の うしろ・ひたいの 上・あごの うしろ）と、耳を つつむ 頭の上の もこもこ。顔（目・ほお・鼻先）は 出す
   - 羊の 耳（よこに たれる・中は ピンク）と、くるっと 巻いた 角（金茶）。体の 下がわは 馬と 同じ 1段の かげ
   - 中に たてがみと 前髪を しまう（no_mane）。頭の 赤い ベルト・鈴の 綱・布・鞍は 着ぐるみの 上
   形は すべて 一から 作った オリジナル。乱数は いつも 同じ（同じ 絵に なる）"""
import math
import numpy as np
import cv2
from cute_horse import smooth, V, unit, f2, path, stroke, circ, svg_rgba

WOOL = '#FFF7EA'          # 毛（クリーム）
WOOL_D = '#E9D8BE'        # 毛の かげ（下の もこもこ）
WOOL_S = '#F2E4CF'        # 光の 当たらない 面
CURL = '#E4D0B0'          # 毛の 中の くるくる
HORN = '#E3BF7F'          # 角
HORN_D = '#B98B4B'        # 角の すじ・かげ
EAR_IN = '#F5B1A6'        # 耳の 中
CURL_SP, CURL_R, CURL_W = 0.20, 0.042, 0.016     # くるくるの 間・大きさ・太さ（m）
BUMP = 0.045              # ふちの もこもこの 半径（m）

# 足の どこから 下を 出すか（上の 骨の 長さの 割合）・太さ（m）・胴の 太さ（m）
LEG_FROM = dict(F=0.30, H=0.42)
LEG_R = 0.075
CORE_R = 0.33
# フードの ふち：頭の 目印（s＝うなじ 0 → 鼻先 0.6・w＝あご −／ひたい ＋）で、w ごとの s（この s より うしろが フード）。
#   ひたいの 上 → 目の うしろ → ほおの うしろ → あごの 下 を 通る（顔の まわりを まるく 出す）
HOOD_EDGE = ((-0.60, 3.0), (-0.21, 3.0), (-0.205, 0.33), (-0.12, 0.20), (-0.06, 0.11), (0.0, 0.075), (0.06, 0.095),
             (0.12, 0.19), (0.40, 0.25))       # w が −0.21 より 下（のど・首）は ぜんぶ フード
TUFT = ((0.07, 0.115), (0.13, 0.10), (0.01, 0.10))      # 頭の上の もこもこ（耳の 根もとから 先へ m, 半径 m）
# 角：頭の 目印（s, w）で まん中・はじめと おわりの 半径・はじめの 向き・巻く 回数・はば（m）
HORN_C = (-0.015, -0.03)
HORN_R = (0.10, 0.02)
HORN_A0 = 62.0                   # はじめの 向き（度：s の 向き 0 → w の 向き 90）＝耳の 前・頭の 上
HORN_TURN = 1.2
HORN_W = (0.062, 0.018)
EAR_ROOT = (-0.03, -0.06)        # 耳の 根もと（s, w）・向き（s, w）・長さ・はば（m）
EAR_DIR = (-0.55, -1.0)
EAR_L, EAR_W = 0.17, 0.08


def _segd(q, a, b):
    a, b = np.asarray(a, float)[:2], np.asarray(b, float)[:2]
    d = b - a
    t = np.clip(((q - a) @ d) / max(float(d @ d), 1e-9), 0, 1)
    return np.linalg.norm(q - (a + t[..., None] * d), axis=-1)


def _hp2(m, s_, w_, zz):
    return np.asarray(m['P1'](m['hp'](s_, w_, zz)), float)


def region(m):
    """着ぐるみの 所（3倍の 画素の 0/1）"""
    s, S, Pn, inside = m['s'], m['S'], m['Pn'], m['inside']
    q = Pn[..., :2]
    big = np.full(inside.shape, 9.0, np.float32)
    # 足（ひじ・ももの 少し 下から）と 胴・首の 軸
    d_leg = big.copy()
    for k in ('FL', 'FR', 'HL', 'HR'):
        J = S[k]
        keys = ('el', 'kn', 'ft', 'co', 'hf') if k[0] == 'F' else ('st', 'hk', 'ft', 'co', 'hf')
        P = [np.asarray(J[c], float) for c in keys]
        P[0] = P[0] + (P[1] - P[0]) * LEG_FROM[k[0]]
        for a, b in zip(P[:-1], P[1:]):
            d_leg = np.minimum(d_leg, _segd(q, a, b))
    c0 = (np.asarray(S['chest']) + np.asarray(S['scap'])) / 2
    c1 = (np.asarray(S['hip']) + np.asarray(S['croup'])) / 2
    d_core = _segd(q, c0, c1)
    nm = m['neck_mid']
    for a, b in zip(nm[:-1:5], nm[5::5]):
        d_core = np.minimum(d_core, _segd(q, a, b) * 1.6)
    leg = (d_leg / LEG_R) < (d_core / CORE_R)
    # 頭（あごまで）と フード
    u2 = np.asarray(m['u2'], float)
    v2 = np.array([-u2[1], u2[0]])
    rel = q - np.asarray(S['poll'], float)
    hs, ws = (rel @ u2) / m['head_sc'], (rel @ v2) / m['head_sc']
    ew, es = zip(*HOOD_EDGE)
    face = inside & (hs >= np.interp(ws, ew, es))                  # 顔（フードの 前）：首の 方は HOOD_EDGE の s が 大きいので 入らない
    reg = (inside & ~face & ~leg).astype(np.uint8)
    # 頭の上の もこもこ（耳を つつむ）
    for f, r in TUFT:
        c = m['ear_base'] + (m['ear_tip'] - m['ear_base']) * (f / 0.17)
        cv2.circle(reg, (int(round(c[0] * s)), int(round(c[1] * s))), int(round(r * m['p1u'] * s)), 1, -1, cv2.LINE_8)
    # なめらかに
    g = cv2.GaussianBlur(reg.astype(np.float32), (0, 0), s * 0.9)
    return (g > 0.5).astype(np.uint8)


def contour_pts(reg, s, step):
    """いちばん外の ふち（1倍の 点）を step ごとに"""
    cs, _ = cv2.findContours(reg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if len(c) < 30:
            continue
        P = c[:, 0, :].astype(np.float64) / s
        Pc = np.vstack([P, P[:1]])
        L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Pc, axis=0), axis=1))])
        n = max(8, int(L[-1] / step))
        t = np.linspace(0, L[-1], n, endpoint=False)
        out.append(np.stack([np.interp(t, L, Pc[:, 0]), np.interp(t, L, Pc[:, 1])], 1))
    return out


def suit_parts(m, reg):
    """もこもこの 体と フード（SVG・1倍）"""
    p, s = m['p1u'], m['s']
    r = BUMP * p
    sh, top = [], []
    for P in contour_pts(reg, s, r * 1.3):
        d = 'M' + ' L'.join(f'{f2(x)},{f2(y)}' for x, y in P) + ' Z'
        sh.append(path(d, WOOL_D, f'transform="translate(0 {f2(r * 0.42)})"'))
        top.append(path(d, WOOL))
        for k, c in enumerate(P):
            rr = r * (1.0 + 0.12 * math.sin(k * 2.39))
            sh.append(circ(c + V(0, r * 0.42), rr, WOOL_D))
            top.append(circ(c, rr, WOOL))
    # 毛の 中の くるくる（内がわ だけ・まばらに）
    rng = np.random.default_rng(2027)
    er = cv2.erode(reg, np.ones((int(r * s * 2.4), int(r * s * 2.4)), np.uint8))
    curls = []
    sp = CURL_SP * p
    H, W = reg.shape
    for row, yy in enumerate(np.arange(0, H / s, sp * 0.87)):
        for xx in np.arange((row % 2) * sp / 2, W / s, sp):
            c = V(xx + rng.uniform(-0.2, 0.2) * sp, yy + rng.uniform(-0.2, 0.2) * sp)
            a0 = rng.uniform(0, 2 * math.pi)
            xi, yi = int(c[0] * s), int(c[1] * s)
            if not (0 <= xi < W and 0 <= yi < H) or not er[yi, xi]:
                continue
            rc = CURL_R * p
            P = [c + V(math.cos(a0 + t * 2 * math.pi * 1.25), math.sin(a0 + t * 2 * math.pi * 1.25)) * rc * (1 - 0.62 * t) for t in np.linspace(0, 1, 14)]
            curls.append(stroke(smooth(P, closed=False), CURL, CURL_W * p))
    return sh + top, curls, top


def shade(m, top):
    """光の 当たらない 面（馬と 同じ 1段の かげ）：着ぐるみの 所（はみ出した もこもこ も）の 3倍の こさ"""
    s, tsh, inside = m['s'], m['tsh'].astype(np.float32), m['inside']
    W, Hh = m['W'], m['Hh']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + ''.join(top) + '</svg>'
    cov = svg_rgba(svg, W * s, Hh * s)[..., 3]
    k = int(round(BUMP * m['p1u'] * s * 2.2)) | 1
    ext = cv2.dilate(tsh * inside, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    t = np.where(inside, tsh, ext)
    return (cov * t).astype(np.float32)


def horn(m):
    """くるっと 巻いた 角（手前）：頭の 横・耳の 前から うしろへ 回って 下から 前へ"""
    p = m['p1u']
    zz = 0.10 * m['side']
    N = 48
    pts, wid = [], []
    for i in range(N + 1):
        t = i / N
        a = math.radians(HORN_A0) + t * HORN_TURN * 2 * math.pi
        r = HORN_R[0] + (HORN_R[1] - HORN_R[0]) * t
        pts.append(_hp2(m, HORN_C[0] + r * math.cos(a), HORN_C[1] + r * math.sin(a), zz))
        wid.append((HORN_W[0] + (HORN_W[1] - HORN_W[0]) * t) * p)
    pts = np.array(pts)
    L, R = [], []
    for i in range(N + 1):
        d = pts[min(i + 1, N)] - pts[max(i - 1, 0)]
        nv = unit(V(-d[1], d[0]))
        L.append(pts[i] + nv * wid[i] / 2)
        R.append(pts[i] - nv * wid[i] / 2)
    shape = smooth(L + R[::-1], sharp=(N, N + 1))
    parts = [path(shape, HORN_D, f'transform="translate(0 {f2(0.012 * p)})"'), path(shape, HORN)]
    for i in range(4, N - 1, 4):                                   # すじ
        d = pts[i + 1] - pts[i - 1]
        nv = unit(V(-d[1], d[0]))
        w = wid[i] / 2 * 0.8
        a, b = pts[i] + nv * w, pts[i] - nv * w
        parts.append(stroke(f'M{f2(a[0])},{f2(a[1])} L{f2(b[0])},{f2(b[1])}', HORN_D, 0.011 * p))
    return parts


def ear(m):
    """よこに たれる 羊の 耳（手前・中は ピンク）：角の うしろ・下から（奥の 耳は 頭の上の もこもこに かくれる）"""
    p = m['p1u']
    zz = 0.10 * m['side']
    a = _hp2(m, EAR_ROOT[0], EAR_ROOT[1], zz)
    tipw = _hp2(m, EAR_ROOT[0] + EAR_DIR[0] * EAR_L, EAR_ROOT[1] + EAR_DIR[1] * EAR_L, zz)
    dv = unit(tipw - a)
    L, Wd = np.linalg.norm(tipw - a), EAR_W * p
    nv = V(-dv[1], dv[0])
    pts = [a + nv * Wd * 0.22, a + dv * L * 0.5 + nv * Wd * 0.5, a + dv * L, a + dv * L * 0.5 - nv * Wd * 0.5, a - nv * Wd * 0.22]
    inn = [a + dv * L * 0.22, a + dv * L * 0.52 + nv * Wd * 0.26, a + dv * L * 0.86, a + dv * L * 0.52 - nv * Wd * 0.26]
    return [path(smooth(pts, sharp=(0, 4)), WOOL_D, f'transform="translate(0 {f2(0.01 * p)})"'), path(smooth(pts, sharp=(0, 4)), WOOL),
            path(smooth(inn), EAR_IN)]


def sheep_acc(m):
    reg = region(m)
    suit, curls, top = suit_parts(m, reg)
    """draw_horse の 飾り：suit（もこもこ）・suit_shade（かげ）・suit_over（くるくる）・head（耳と 角：顔の 上）・no_mane（たてがみを しまう）"""
    return dict(suit=suit, suit_shade=(shade(m, top), WOOL_S), suit_over=curls, no_mane=True, head=ear(m) + horn(m))
