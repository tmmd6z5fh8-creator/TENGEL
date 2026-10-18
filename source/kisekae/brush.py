"""ど的中の演出の筆の字（パチンコのロゴのような極太の筆文字）を、筆の動き（線の通り道・太さ・入り・はらい・かすれ）から描いて、SVG の形にする。
   フォントは使わない（字の形は、ここに書いた線の通り道だけで決まる。まさちゃんの送ってくれた写真の字は、雰囲気の参考だけで、形は使っていない）。
   python3 brush.py <書き出す json（brush_glyphs.json）> [見本の png]
   字：ど・て・き・！・的・中（「どてき！！」「ど！」「ど的中！！！！」）。同じ入力なら毎回同じ形になる

   1文字 = 1000×1000（y は下向き）。線ごとに：
     p  通り道の点（なめらかにつなぐ）
     w  その点での太さ（0 で とがって終わる＝はらい・はね）
     dry  終わりのかすれ（0〜1）
     head 入りの打ち込み（左上から筆を置く。0 で なし）
   描き方：筆の先（だ円）を通り道にそって押していく → まとめて1つの形 → ふちをなぞって折れ線にする"""
import json
import math
import sys

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import approximate_polygon, find_contours

PX = 2.0        # 1単位 = 2px で描く
PAD = 200       # 1文字の外にはみ出してもいい幅
SIZE = int((1000 + 2 * PAD) * PX)
POINT = 1.3     # 筆の先の両はしのとがり方（2 でだ円・小さいほどとがる）
TIP = (.5, math.radians(45))   # 筆の先のだ円（短い方／長い方・傾き。左上から右下へ長い＝筆の先が左上）


def catmull(pts, n=40):
    """点をなめらかにつなぐ（centripetal Catmull-Rom）。戻り値：細かい点の列と、もとの点の位置（何番目か）"""
    P = [np.array(p, float) for p in pts]
    if len(P) == 2:
        t = np.linspace(0, 1, n * 2)[:, None]
        return P[0] * (1 - t) + P[1] * t, [0, n * 2 - 1]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out, idx = [], [0]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0
        t1 = t0 + max(np.linalg.norm(p1 - p0), 1e-6) ** .5
        t2 = t1 + max(np.linalg.norm(p2 - p1), 1e-6) ** .5
        t3 = t2 + max(np.linalg.norm(p3 - p2), 1e-6) ** .5
        for t in np.linspace(t1, t2, n, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
        idx.append(len(out))
    out.append(P[-2])
    idx[-1] = len(out) - 1
    return np.array(out), idx


def resample(path, idx, ws, step):
    """長さにそって等間隔に。太さは点のあいだをなめらかに（smoothstep）"""
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    L = s[-1]
    sk = s[idx]
    m = max(2, int(L / step) + 1)
    u = np.linspace(0, L, m)
    x = np.interp(u, s, path[:, 0])
    y = np.interp(u, s, path[:, 1])
    w = np.empty(m)
    for j, uu in enumerate(u):
        k = min(np.searchsorted(sk, uu, side='right') - 1, len(sk) - 2)
        a = (uu - sk[k]) / max(sk[k + 1] - sk[k], 1e-9)
        a = a * a * (3 - 2 * a)
        w[j] = ws[k] * (1 - a) + ws[k + 1] * a
    return x, y, w, u / max(L, 1e-9), L


class Canvas:
    def __init__(self):
        self.m = np.zeros((SIZE, SIZE), bool)

    def stamp(self, x, y, r, ratio=TIP[0], ang=TIP[1], val=True):
        """だ円を1つ押す（x, y, r は1文字の単位）"""
        if r <= .3:
            return
        cx, cy = (x + PAD) * PX, (y + PAD) * PX
        R = r * PX
        x0, x1 = max(0, int(cx - R - 2)), min(SIZE, int(cx + R + 3))
        y0, y1 = max(0, int(cy - R - 2)), min(SIZE, int(cy + R + 3))
        if x0 >= x1 or y0 >= y1:
            return
        dx = np.arange(x0, x1, dtype=np.float32)[None, :] - cx
        dy = np.arange(y0, y1, dtype=np.float32)[:, None] - cy
        c, s = math.cos(ang), math.sin(ang)
        u = (dx * c + dy * s) / R
        v = (-dx * s + dy * c) / (R * ratio)
        hit = np.abs(u) ** POINT + v * v <= 1
        if val:
            self.m[y0:y1, x0:x1] |= hit
        else:
            self.m[y0:y1, x0:x1] &= ~hit

    def stroke(self, p, w, dry=0.0, head=1.0, seed=0, wob=.05, ratio=None, gap=1.0):
        """w は見える太さ（線の向きに直角の幅）。筆の先のだ円の大きさは、線の向きから逆算する（はしの形だけだ円の向きで決まる）"""
        rnd = np.random.default_rng(seed)
        path, idx = catmull(p)
        x, y, ww, t, L = resample(path, idx, w, 1.0)
        # ふちのゆらぎ（ゆっくり変わる太さ）
        ph = rnd.uniform(0, 2 * np.pi, 3)
        ww = ww * (1 + wob * (np.sin(t * 7.3 + ph[0]) * .5 + np.sin(t * 13.1 + ph[1]) * .3 + np.sin(t * 29 + ph[2]) * .2))
        rt = TIP[0] if ratio is None else ratio
        tx, ty = np.gradient(x), np.gradient(y)
        nang = np.arctan2(ty, tx) + np.pi / 2
        psi = nang - TIP[1]
        fac = np.maximum(np.sqrt(np.cos(psi) ** 2 + (rt * np.sin(psi)) ** 2), .62)
        R = ww / 2 / fac
        k = 0
        while k < len(x):
            self.stamp(x[k], y[k], R[k], rt)
            k += max(1, int(max(R[k], 2) * .05))
        self.stamp(x[-1], y[-1], R[-1], rt)
        # 入りの打ち込み：左上から筆を置いた形（とがった角）
        if head and ww[0] > 20:
            w0 = R[0] * 2 * head
            back = np.array([-.7, -.7]) * w0 * .26
            for a in np.linspace(0, 1, 20):
                self.stamp(x[0] + back[0] * (1 - a), y[0] + back[1] * (1 - a), w0 / 2 * (.3 + .72 * a), rt)
        # かすれ：終わりのほうに、線にそった細いすき間（筆の毛の割れ目）
        if dry > 0:
            n = int(3 + dry * 8)
            nx, ny = -ty, tx
            nn = np.hypot(nx, ny) + 1e-9
            nx, ny = nx / nn, ny / nn
            for _ in range(n):
                o = rnd.uniform(-.8, .8)
                s0 = rnd.uniform(1 - .6 * dry, .96)
                gw = rnd.uniform(.016, .045) * gap
                for j in range(int(s0 * len(x)), len(x), 2):
                    hw = ww[j] / 2
                    self.stamp(x[j] + nx[j] * o * hw, y[j] + ny[j] * o * hw, max(1.2, gw * ww[j] + 1.0), 1.0, 0, val=False)

    def dot(self, x, y, r):
        self.stamp(x, y, r, 1.0, 0)

    def splat(self, x, y, r, seed):
        """墨のしぶき：小さな点をいくつか"""
        rnd = np.random.default_rng(seed)
        for _ in range(3):
            a, d = rnd.uniform(0, 2 * np.pi), rnd.uniform(.4, 1) * r * 3
            self.stamp(x + math.cos(a) * d, y + math.sin(a) * d, rnd.uniform(.25, .6) * r, 1.0, 0)
        self.stamp(x, y, r, 1.0, 0)

    def outline(self, shear=0.0, tol=.6, min_area=60.0):
        f = gaussian_filter(self.m.astype(np.float32), 1.1)
        cs = find_contours(f, .5)
        polys = []
        for c in cs:
            c = approximate_polygon(c, tol * PX)
            pts = np.stack([c[:, 1] / PX - PAD, c[:, 0] / PX - PAD], 1)
            if len(pts) < 4:
                continue
            a = .5 * np.sum(pts[:-1, 0] * pts[1:, 1] - pts[1:, 0] * pts[:-1, 1])
            if abs(a) < min_area:
                continue
            pts[:, 0] = pts[:, 0] - shear * (pts[:, 1] - 500)
            polys.append(pts)
        return polys


def path_d(polys):
    out = []
    for pts in polys:
        q = np.round(pts).astype(int)
        keep = [0] + [i for i in range(1, len(q)) if (q[i] != q[i - 1]).any()]
        q = q[keep]
        if (q[0] == q[-1]).all():
            q = q[:-1]
        out.append('M' + ' '.join(f'{a} {b}' for a, b in q) + 'Z')
    return ''.join(out)


def bbox(polys):
    a = np.concatenate(polys)
    return [int(a[:, 0].min()), int(a[:, 1].min()), int(math.ceil(a[:, 0].max())), int(math.ceil(a[:, 1].max()))]


# ---------- 字の形（筆の動き）：まさちゃんの字体の指定（パチンコのロゴのような極太の筆文字）から、こちらで描いたもの ----------
SHEAR = .14     # 少し右に傾ける（勢い）

GLYPHS = {
    'ど': dict(id='do', adv=1000, strokes=[
        dict(p=[(236, 110), (278, 270), (334, 438)], w=[172, 160, 118], head=.4, seed=1),
        dict(p=[(680, 300), (530, 410), (370, 540), (255, 690), (285, 825), (450, 885), (670, 880), (900, 845)],
             w=[120, 196, 206, 202, 196, 180, 140, 0], dry=.8, seed=2),
        dict(p=[(735, 60), (770, 150), (790, 245)], w=[140, 130, 40], head=.6, seed=3),
        dict(p=[(865, 25), (900, 110), (925, 200)], w=[140, 128, 40], head=.6, seed=4),
    ]),
    'て': dict(id='te', adv=1000, strokes=[
        dict(p=[(70, 330), (330, 272), (600, 232), (855, 200)], w=[165, 140, 135, 175], seed=11),
        dict(p=[(850, 210), (640, 340), (470, 505), (440, 690), (545, 835), (790, 895)], w=[170, 200, 205, 195, 165, 0], dry=.8, seed=12),
    ]),
    'き': dict(id='ki', adv=1000, strokes=[
        dict(p=[(160, 205), (450, 170), (780, 122)], w=[150, 128, 150], seed=21),
        dict(p=[(115, 420), (480, 380), (870, 322)], w=[155, 130, 160], seed=22),
        dict(p=[(420, 45), (515, 245), (618, 448), (690, 578)], w=[160, 175, 180, 172], seed=23),
        dict(p=[(430, 596), (285, 705), (318, 840), (520, 886), (830, 858)], w=[96, 176, 182, 166, 0], dry=.75, head=0, seed=25),
    ]),
    '！': dict(id='ex', adv=520, strokes=[
        dict(p=[(255, 40), (258, 330), (262, 610)], w=[220, 175, 30], head=.8, seed=31),
        dict(p=[(250, 800), (262, 842)], w=[182, 182], head=0, seed=32),
    ]),
    '的': dict(id='teki', adv=1000, strokes=[
        dict(p=[(334, 18), (304, 92), (272, 148)], w=[116, 86, 18], head=.6, seed=41),
        dict(p=[(118, 214), (124, 560), (132, 912)], w=[130, 118, 126], seed=42),
        dict(p=[(128, 224), (290, 214), (452, 200)], w=[92, 84, 112], head=0, seed=43),
        dict(p=[(448, 204), (444, 560), (436, 872)], w=[126, 116, 122], head=0, seed=44),
        dict(p=[(156, 532), (300, 528), (420, 522)], w=[84, 80, 84], head=0, seed=45),
        dict(p=[(156, 858), (300, 852), (424, 846)], w=[92, 86, 94], head=0, seed=46),
        dict(p=[(700, 20), (660, 160), (586, 302)], w=[132, 110, 16], seed=47),
        dict(p=[(612, 234), (770, 212), (928, 186)], w=[100, 90, 126], head=0, seed=48),
        dict(p=[(924, 192), (930, 470), (914, 760), (886, 886), (810, 878), (736, 836)], w=[136, 132, 124, 116, 70, 0], head=0, seed=49),
        dict(p=[(606, 450), (644, 522), (680, 592)], w=[92, 146, 126], head=.7, seed=51),
    ]),
    '中': dict(id='chu', adv=1000, strokes=[
        dict(p=[(124, 255), (134, 480), (146, 705)], w=[144, 138, 134], seed=61),
        dict(p=[(124, 258), (500, 236), (880, 212)], w=[120, 108, 140], seed=62),
        dict(p=[(874, 220), (864, 452), (854, 692)], w=[146, 140, 136], head=0, seed=63),
        dict(p=[(150, 690), (500, 678), (850, 664)], w=[112, 104, 112], head=0, seed=64),
        dict(p=[(500, 10), (500, 400), (503, 760), (506, 995)], w=[166, 162, 150, 0], dry=.7, seed=65),
    ]),
}


def build(name):
    g = GLYPHS[name]
    cv = Canvas()
    for s in g['strokes']:
        cv.stroke(s['p'], s['w'], dry=s.get('dry', 0), head=s.get('head', 1.0), seed=s.get('seed', 0))
    for d in g.get('dots', []):
        cv.dot(*d)
    for i, d in enumerate(g.get('splats', [])):
        cv.splat(*d, seed=i + 7)
    polys = cv.outline(shear=SHEAR)
    return dict(id=g['id'], d=path_d(polys), bbox=bbox(polys), adv=g['adv']), cv


if __name__ == '__main__':
    out = {}
    cvs = {}
    names = sys.argv[3] if len(sys.argv) > 3 else ''.join(GLYPHS)
    for k in names:
        out[k], cvs[k] = build(k)
        print(k, len(out[k]['d']), out[k]['bbox'])
    json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    if len(sys.argv) > 2 and sys.argv[2] != '-':
        from PIL import Image
        n = len(names)
        W = SIZE // 3
        img = Image.new('L', (n * W, W), 255)
        for i, k in enumerate(names):
            m = cvs[k].m[::3, ::3]
            a = np.where(m, 0, 255).astype(np.uint8)
            o = PAD * PX / 3
            for g in range(0, 1001, 100):
                a[int(o + g * PX / 3), ::4] = 128 if g % 500 else 60
                a[::4, int(o + g * PX / 3)] = 128 if g % 500 else 60
            img.paste(Image.fromarray(a), (i * W, 0))
        img.save(sys.argv[2])
