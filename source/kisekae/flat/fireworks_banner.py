"""花火の絵（780×320）：夜空・星・4つの花火・ちょうちんは前の r3d/banners/fireworks.py のまま（同じ乱数の順）、
   馬だけ描き直す → 光の線でえがいた、夜空をかける馬（flat/fireworks_horse.py）
   python3 flat/fireworks_banner.py <出力.webp>
   python3 flat/fireworks_banner.py --layers <出力フォルダ>   → 壁紙の動き（まさちゃんの指定・fireworks_wall.py）のための 絵の分け方：
     fireworks_base.webp（夜空・星・ちょうちん＝花火なし）・fireworks_layers.webp（花火4つと 馬の光を、それぞれ「足す光」にして
     たてに並べた1まい）・fireworks_layers.json（置く場所・花火のまん中・きらっとさせる点）
     足す光は「その花火を描いた絵 − 描く前の絵」（描く順は いつもの絵と同じ：花火1 → 2 → 3 → 4 → 馬 → ちょうちん）なので、
     下の絵に ぜんぶ足すと いつもの絵と同じになる（ページでは mix-blend-mode:plus-lighter で足す）
   （いつもの絵は前と1バイトもちがわない。夜空・花火・ちょうちんを関数に分けただけ）"""
import sys, os, math, json
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fireworks_horse import *

W, Hh = 780, 320
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
BURSTS = [(110, 92, 80, '#FF6FA8'), (300, 60, 60, '#FFD45E'), (690, 84, 86, '#6FE3FF'), (560, 40, 44, '#FF9F5A')]   # (x, y, 半径, 色)
N_RAY = 64


def sky(rng):
    """夜空と星"""
    img = grad_v(Hh, W, [(0, '#0A0F2C'), (0.7, '#1B2457'), (1, '#2A2F63')])
    st = np.zeros((Hh, W), np.float32)
    for i in range(120):
        cv2.circle(st, (int(rng.uniform(0, W) * 4), int(rng.uniform(0, 200) * 4)), int(rng.uniform(0.4, 1.0) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    return over(img, hexc('#FFFFFF'), np.clip(st, 0, 1) * 0.6)


def ray_angles(rng, n=N_RAY):
    return [k / n * 2 * math.pi + rng.normal(0, 0.03) for k in range(n)]


def dot_xy(cx, cy, r, a, j):
    """花火の j 番目（0〜6）の点の場所"""
    r0 = r * 0.18
    rr = r0 + (r - r0) * j / 6
    return cx + math.cos(a) * rr, cy + math.sin(a) * rr + (rr / r) ** 2 * 6


def burst(angles, cx, cy, r, col):
    """花火1つ：(光のしん, まわりの光)"""
    lines = np.zeros((Hh, W), np.float32)
    dots = np.zeros((Hh, W), np.float32)
    for a in angles:
        r0 = r * 0.18
        for j in range(7):
            x, y = dot_xy(cx, cy, r, a, j)
            cv2.circle(dots, (int(x * 4), int(y * 4)), int((1.0 + j * 0.25) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        x1, y1 = cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95 + 5
        cv2.line(lines, (int((cx + math.cos(a) * r0) * 16), int((cy + math.sin(a) * r0) * 16)), (int(x1 * 16), int(y1 * 16)), 0.5, 1, cv2.LINE_AA, shift=4)
    m = np.clip(dots + lines, 0, 1)
    c = hexc(col)
    return m[..., None] * c, blur(m, 6)[..., None] * c


def add_burst(img, core, g):
    img = img + g * 0.9
    return np.where(core.max(-1, keepdims=True) > 0, np.maximum(img, core), img)


def lanterns(img):
    """提灯のひも・提灯（いちばん手前）"""
    yl = 268
    cv2.line(img, (0, int(yl - 8)), (W, int(yl - 8)), (0.15, 0.12, 0.1), 2, cv2.LINE_AA)
    for k, x in enumerate(np.arange(30, W, 62)):
        y = yl + 6 * math.sin(k)
        lm = np.zeros((Hh, W), np.float32)
        cv2.ellipse(lm, (int(x * 4), int(y * 4)), (int(19 * 4), int(25 * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=2)
        col = hexc('#E8352E') if k % 2 == 0 else hexc('#F2A23A')
        img = img + blur(lm, 14)[..., None] * col * 0.6
        img = over(img, col, lm)
        img = over(img, hexc('#FFE3A0'), lm * np.clip(1 - np.abs(xx - x) / 9, 0, 1) * 0.55)
        for dy in (-15, -5, 5, 15):
            rib = np.exp(-((yy - y - dy) / 1.0) ** 2) * lm
            img = over(img, hexc('#6E1410'), rib * 0.6)
        cap = np.zeros((Hh, W), np.float32)
        cv2.rectangle(cap, (int((x - 9) * 4), int((y - 29) * 4)), (int((x + 9) * 4), int((y - 23) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
        cv2.rectangle(cap, (int((x - 9) * 4), int((y + 23) * 4)), (int((x + 9) * 4), int((y + 29) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
        img = over(img, hexc('#1E1410'), cap)
    return img


def compose(on=(True, True, True, True), horse=True, parts=None):
    """いつもの絵（on：どの花火を描くか・horse：馬を描くか）。parts に (夜空, [(光のしん, まわりの光, 角度)…]) を入れて返す"""
    rng = np.random.default_rng(91)
    img = sky(rng)
    bs = []
    for (cx, cy, r, col), o in zip(BURSTS, on):
        ang = ray_angles(rng)                     # 描かない花火も 乱数は同じ順に使う
        core, g = burst(ang, cx, cy, r, col)
        bs.append((core, g, ang))
        if o:
            img = add_burst(img, core, g)
    if horse:
        img = light_horse(img, W, Hh)
    img = lanterns(img)
    if parts is not None:
        parts['bursts'] = bs
    return np.clip(img, 0, 1)


def bbox(m, pad=4):
    ys, xs = np.nonzero(m)
    x0, y0 = max(0, (xs.min() - pad) // 2 * 2), max(0, (ys.min() - pad) // 2 * 2)
    x1, y1 = min(W, -(-(xs.max() + 1 + pad) // 2) * 2), min(Hh, -(-(ys.max() + 1 + pad) // 2) * 2)
    return int(x0), int(y0), int(x1 - x0), int(y1 - y0)


def spread_points(pts, n, seed):
    """たくさんの点から、なるべく はなれた n 点（遠い点から順に えらぶ）"""
    rng = np.random.default_rng(seed)
    pts = np.asarray(pts, float)
    out = [pts[rng.integers(len(pts))]]
    d = np.linalg.norm(pts - out[0], axis=1)
    for _ in range(n - 1):
        i = int(np.argmax(d))
        out.append(pts[i])
        d = np.minimum(d, np.linalg.norm(pts - pts[i], axis=1))
    return [[round(float(x), 1), round(float(y), 1)] for x, y in out]


def layers(out):
    """壁紙の動きのための絵（下の絵・足す光・置く場所）"""
    os.makedirs(out, exist_ok=True)
    parts = {}
    off = (False,) * 4
    F = [compose(off, horse=False, parts=parts)]
    for k in range(4):
        F.append(compose(tuple(i <= k for i in range(4)), horse=False))
    F_all = compose()
    save_webp(F[0], f'{out}/fireworks_base.webp')
    D = [np.clip(F[k + 1] - F[k], 0, 1) for k in range(4)] + [np.clip(F_all - F[4], 0, 1)]
    rects, tiles, y_at = [], [], 0
    info = dict(size=[W, Hh], layers=[])
    for k, d in enumerate(D):
        m = d.max(-1) > 1.5 / 255
        x0, y0, w, h = bbox(m)
        tiles.append(d[y0:y0 + h, x0:x0 + w])
        e = dict(kind='burst' if k < 4 else 'horse', rect=[x0, y0, w, h], sheet_y=y_at)
        if k < 4:
            cx, cy, r, col = BURSTS[k]
            ang = parts['bursts'][k][2]
            rng = np.random.default_rng(300 + k)
            pts = [dot_xy(cx, cy, r, ang[i], j) for i in rng.choice(N_RAY, 9, replace=False) for j in [int(rng.integers(3, 7))]]
            e.update(center=[cx, cy], r=r, color=col, glints=[[round(x, 1), round(y, 1)] for x, y in pts])
        else:
            lum = d.max(-1)
            ys, xs = np.nonzero((lum > 0.80) & (yy < 236))
            e.update(center=[441, 146], glints=spread_points(np.stack([xs, ys], 1), 12, 77))
        info['layers'].append(e)
        y_at += h
    wmax = max(t.shape[1] for t in tiles)
    sheet = np.zeros((y_at, wmax, 3), np.float32)
    for t, e in zip(tiles, info['layers']):
        sheet[e['sheet_y']:e['sheet_y'] + t.shape[0], :t.shape[1]] = t
    save_webp(sheet, f'{out}/fireworks_layers.webp', q=92)
    info['sheet'] = [int(wmax), int(y_at)]
    json.dump(info, open(f'{out}/fireworks_layers.json', 'w'), ensure_ascii=False)
    print(json.dumps(info, ensure_ascii=False)[:400])
    # たしかめ：下の絵に ぜんぶ足すと いつもの絵
    back = F[0] + sum(D)
    print('max diff (float)', float(np.abs(np.clip(back, 0, 1) - F_all).max()))


if __name__ == '__main__':
    if sys.argv[1] == '--layers':
        layers(sys.argv[2])
    else:
        out = sys.argv[1]
        img = compose(horse=os.environ.get('FW_NO_HORSE') != '1')
        save_webp(img, out)
        print(out)
